"""
CLI script to bulk-index organisational knowledge base documents into Azure AI Search.

Usage:
    python scripts/index_org_kb.py --folder ./org_docs
    python scripts/index_org_kb.py --folder ./org_docs --overwrite

Supported file types: .pdf, .docx, .txt, .md
Documents are indexed with doc_type="org" so the QA agent can search them
separately from meeting-specific documents.

Environment variables required (same as main app):
    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT, AZURE_DOCUMENT_INTELLIGENCE_KEY
    AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY, AZURE_SEARCH_INDEX_NAME
    AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_EMBEDDING_DEPLOYMENT
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Ensure app package is importable when run from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.logging import configure_logging

logger = logging.getLogger(__name__)


async def main(folder: str, overwrite: bool = False) -> None:
    """
    Entry point for the org KB indexing CLI.

    Args:
        folder: Path to the folder containing org KB documents.
        overwrite: If True, re-index files already present in the search index.
    """
    # TODO: Implement org KB indexing.
    #
    # Pattern:
    #   from app.rag.retriever import ensure_index
    #   from app.rag.org_kb_indexer import index_org_documents
    #
    #   logger.info("Ensuring search index exists...")
    #   await ensure_index()
    #
    #   logger.info("Indexing documents from: %s", folder)
    #   result = await index_org_documents(folder_path=folder, overwrite=overwrite)
    #
    #   logger.info(
    #       "Done. Files processed: %d, Chunks indexed: %d, Errors: %d",
    #       result["files_processed"], result["chunks_indexed"], len(result["errors"])
    #   )
    #   for err in result["errors"]:
    #       logger.error("  Error in %s: %s", err["file"], err["error"])
    raise NotImplementedError("TODO: implement main() in index_org_kb.py")


if __name__ == "__main__":
    configure_logging()

    parser = argparse.ArgumentParser(
        description="Bulk-index org knowledge base documents into Azure AI Search."
    )
    parser.add_argument(
        "--folder",
        required=True,
        help="Path to the folder containing org KB documents (.pdf, .docx, .txt, .md)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Re-index files even if they already exist in the search index.",
    )
    args = parser.parse_args()

    asyncio.run(main(folder=args.folder, overwrite=args.overwrite))
