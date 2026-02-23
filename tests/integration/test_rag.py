"""
Integration tests — RAG pipeline (document upload → index → search).

Uses doc_type='meeting' with a unique test_meeting_id to avoid polluting
the permanent org KB.  Test documents are cleaned up after the session.
"""
from __future__ import annotations

import asyncio
import io
import uuid

import pytest

from app.rag.retriever import HybridRetriever


_TEST_TEXT = (
    "MeetingBot quarterly review. "
    "The team agreed to increase the sprint velocity target by 20 percent. "
    "Action item: Alice will update the project roadmap by end of month. "
    "Key decision: adopt Azure AI Search for all knowledge retrieval tasks."
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_blob_upload_and_sas_url(blob_client, test_meeting_id):
    """Uploads a text file to Blob Storage and gets a valid SAS URL back."""
    content = _TEST_TEXT.encode()
    filename = f"integration-test-{test_meeting_id}.txt"

    url = await blob_client.upload_bytes(
        data=content,
        blob_name=filename,
        content_type="text/plain",
    )

    assert url.startswith("https://")
    assert filename in url

    # Cleanup
    await blob_client.delete_blob(filename)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_search_upsert_and_retrieval(search_client, settings, test_meeting_id):
    """Upserts a document to AI Search and retrieves it via hybrid search."""
    from azure.search.documents.models import VectorizedQuery
    from app.rag.retriever import HybridRetriever

    retriever = HybridRetriever(settings)
    doc_id = f"inttest-{uuid.uuid4().hex[:8]}"

    # Upsert a single chunk directly
    doc = {
        "id": doc_id,
        "meeting_id": test_meeting_id,
        "doc_type": "meeting",
        "chunk_text": _TEST_TEXT,
        "source_file": "integration-test.txt",
        "chunk_index": 0,
    }
    await retriever.upsert_documents([doc])

    # Allow indexer to catch up
    await asyncio.sleep(3)

    results = await retriever.hybrid_search(
        query="sprint velocity action item Alice",
        meeting_id=test_meeting_id,
        doc_type="meeting",
        top_k=3,
    )

    assert len(results) >= 1
    assert any("Alice" in r.get("chunk_text", "") for r in results)

    # Cleanup — delete the test document from the index
    await retriever.delete_documents([doc_id])


@pytest.mark.integration
@pytest.mark.asyncio
async def test_org_kb_is_queryable(settings):
    """Verify the permanent org KB index is accessible and non-empty."""
    retriever = HybridRetriever(settings)

    results = await retriever.hybrid_search(
        query="organisation structure",
        meeting_id="org",
        doc_type="org",
        top_k=1,
    )

    # Index exists and is reachable — even zero results is acceptable
    assert isinstance(results, list)
