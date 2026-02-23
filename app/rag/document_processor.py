from __future__ import annotations

import logging
from dataclasses import dataclass

from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

from app.config import get_settings

logger = logging.getLogger(__name__)

# Characters per chunk (overlap handled by stride)
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


@dataclass
class DocumentChunk:
    """A single text chunk extracted from a document."""

    text: str
    source: str        # original filename
    page: int          # 1-based page number
    chunk_index: int
    meeting_id: str
    doc_type: str = "meeting"  # "meeting" | "org"


def _split_text(text: str, source: str, meeting_id: str, page: int = 1) -> list[DocumentChunk]:
    """Split text into overlapping chunks."""
    chunks: list[DocumentChunk] = []
    start = 0
    idx = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append(
                DocumentChunk(
                    text=chunk_text,
                    source=source,
                    page=page,
                    chunk_index=idx,
                    meeting_id=meeting_id,
                )
            )
            idx += 1
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


async def process_document(
    file_bytes: bytes,
    filename: str,
    meeting_id: str,
    doc_type: str = "meeting",
) -> list[DocumentChunk]:
    """
    Analyze a document using Azure Document Intelligence and return text chunks.
    Supports PDF, DOCX, PPTX, XLSX, images (PNG/JPEG/TIFF).
    """
    settings = get_settings()
    client = DocumentIntelligenceClient(
        endpoint=settings.azure_document_intelligence_endpoint,
        credential=AzureKeyCredential(settings.azure_document_intelligence_key),
    )

    async with client:
        poller = await client.begin_analyze_document(
            model_id="prebuilt-layout",
            analyze_request={"base64Source": None},
            body=file_bytes,
            content_type="application/octet-stream",
        )
        result = await poller.result()

    all_chunks: list[DocumentChunk] = []

    if result.pages:
        for page in result.pages:
            page_num = page.page_number or 1
            # Collect all line texts on the page
            lines = [line.content for line in (page.lines or []) if line.content]
            page_text = " ".join(lines)
            chunks = _split_text(page_text, filename, meeting_id, page=page_num)
            for c in chunks:
                c.doc_type = doc_type
            all_chunks.extend(chunks)

    logger.info(
        "Processed '%s': %d pages → %d chunks", filename, len(result.pages or []), len(all_chunks)
    )
    return all_chunks
