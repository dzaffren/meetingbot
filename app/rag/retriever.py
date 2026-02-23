from __future__ import annotations

import logging
import uuid
from typing import Any

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.indexes.aio import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery
from openai import AsyncAzureOpenAI

from app.config import get_settings
from app.rag.document_processor import DocumentChunk

logger = logging.getLogger(__name__)


async def ensure_index() -> None:
    """Create the Azure AI Search index if it doesn't exist."""
    settings = get_settings()
    credential = AzureKeyCredential(settings.azure_search_key)

    index = SearchIndex(
        name=settings.azure_search_index_name,
        fields=[
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SimpleField(name="source", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="doc_type", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="meeting_id", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="page", type=SearchFieldDataType.Int32, filterable=True),
            SearchField(
                name="embedding",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=3072,
                vector_search_profile_name="hnsw-profile",
            ),
        ],
        vector_search=VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(name="hnsw-algo")],
            profiles=[VectorSearchProfile(name="hnsw-profile", algorithm_configuration_name="hnsw-algo")],
        ),
    )

    async with SearchIndexClient(
        endpoint=settings.azure_search_endpoint, credential=credential
    ) as idx_client:
        await idx_client.create_or_update_index(index)
        logger.info("Search index '%s' ensured", settings.azure_search_index_name)


async def _embed(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using Azure OpenAI."""
    settings = get_settings()
    client = AsyncAzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
    )
    response = await client.embeddings.create(
        model=settings.azure_openai_embedding_deployment,
        input=texts,
    )
    return [item.embedding for item in response.data]


async def upsert_chunks(chunks: list[DocumentChunk]) -> None:
    """Embed and upsert document chunks into Azure AI Search."""
    if not chunks:
        return

    settings = get_settings()
    credential = AzureKeyCredential(settings.azure_search_key)

    texts = [c.text for c in chunks]
    embeddings = await _embed(texts)

    docs = [
        {
            "id": str(uuid.uuid4()),
            "content": c.text,
            "source": c.source,
            "doc_type": c.doc_type,
            "meeting_id": c.meeting_id,
            "page": c.page,
            "embedding": emb,
        }
        for c, emb in zip(chunks, embeddings)
    ]

    async with SearchClient(
        endpoint=settings.azure_search_endpoint,
        index_name=settings.azure_search_index_name,
        credential=credential,
    ) as client:
        await client.upload_documents(documents=docs)

    logger.info("Upserted %d chunks into search index", len(docs))


async def hybrid_search(
    query: str,
    meeting_id: str | None = None,
    doc_type: str | None = None,
    top_k: int | None = None,
) -> list[dict[str, Any]]:
    """
    Perform hybrid (keyword + vector) search against Azure AI Search.

    Args:
        query: The search query text.
        meeting_id: If set, restrict results to a specific meeting session.
        doc_type: If set, restrict to "meeting" or "org" documents.
        top_k: Number of results to return (defaults to settings.search_top_k).

    Returns:
        List of result dicts with keys: content, source, doc_type, meeting_id, page, score.
    """
    settings = get_settings()
    k = top_k or settings.search_top_k
    credential = AzureKeyCredential(settings.azure_search_key)

    # Build OData filter
    filters: list[str] = []
    if meeting_id:
        filters.append(f"meeting_id eq '{meeting_id}'")
    if doc_type:
        filters.append(f"doc_type eq '{doc_type}'")
    odata_filter = " and ".join(filters) if filters else None

    # Embed query for vector search
    [query_embedding] = await _embed([query])
    vector_query = VectorizedQuery(
        vector=query_embedding,
        k_nearest_neighbors=k,
        fields="embedding",
    )

    async with SearchClient(
        endpoint=settings.azure_search_endpoint,
        index_name=settings.azure_search_index_name,
        credential=credential,
    ) as client:
        results = await client.search(
            search_text=query,
            vector_queries=[vector_query],
            filter=odata_filter,
            top=k,
            select=["content", "source", "doc_type", "meeting_id", "page"],
        )
        return [
            {
                "content": r["content"],
                "source": r["source"],
                "doc_type": r["doc_type"],
                "meeting_id": r["meeting_id"],
                "page": r["page"],
                "score": r.get("@search.score", 0.0),
            }
            async for r in results
        ]
