from __future__ import annotations

import logging
from dataclasses import dataclass

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


async def process_document(
    file_bytes: bytes,
    filename: str,
    meeting_id: str,
    doc_type: str = "meeting",
) -> list[DocumentChunk]:
    """
    Analyze a document using Azure Document Intelligence and return text chunks.
    Supports PDF, DOCX, PPTX, XLSX, images (PNG/JPEG/TIFF).

    Args:
        file_bytes: Raw bytes of the document.
        filename: Original filename (used as source label in search).
        meeting_id: Meeting session ID for search scoping.
        doc_type: "meeting" (session-scoped) or "org" (persistent org KB).

    Returns:
        List of DocumentChunk objects ready for embedding and indexing.
    """
    # TODO: Implement document analysis using Azure Document Intelligence.
    #
    # Pattern:
    #   from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
    #   from azure.core.credentials import AzureKeyCredential
    #   settings = get_settings()
    #   client = DocumentIntelligenceClient(
    #       endpoint=settings.azure_document_intelligence_endpoint,
    #       credential=AzureKeyCredential(settings.azure_document_intelligence_key),
    #   )
    #   async with client:
    #       poller = await client.begin_analyze_document(
    #           model_id="prebuilt-layout",
    #           body=file_bytes,
    #           content_type="application/octet-stream",
    #       )
    #       result = await poller.result()
    #   # Split each page's text into overlapping chunks using _split_text()
    #   # Set doc_type on each chunk
    raise NotImplementedError("TODO: implement process_document()")


def _split_text(text: str, source: str, meeting_id: str, page: int = 1) -> list[DocumentChunk]:
    """Split text into overlapping chunks of CHUNK_SIZE characters with CHUNK_OVERLAP overlap."""
    # TODO: Implement text chunking.
    #
    # Basic sliding window:
    #   chunks, start, idx = [], 0, 0
    #   while start < len(text):
    #       chunk_text = text[start : start + CHUNK_SIZE].strip()
    #       if chunk_text:
    #           chunks.append(DocumentChunk(text=chunk_text, source=source, page=page, chunk_index=idx, meeting_id=meeting_id))
    #           idx += 1
    #       start += CHUNK_SIZE - CHUNK_OVERLAP
    #   return chunks
    raise NotImplementedError("TODO: implement _split_text()")
