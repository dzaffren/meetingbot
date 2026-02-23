"""
Integration test fixtures.

Tests in this package require real Azure credentials in .env (or environment).
They are automatically skipped when required env vars are absent.

Run with:
    pytest tests/integration/ -m integration -v
"""
from __future__ import annotations

import os
import uuid
from pathlib import Path

import pytest
import pytest_asyncio

# ── Load .env if present ───────────────────────────────────────────────────────
_env_file = Path(__file__).parent.parent.parent / ".env"
if _env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file)
    except ImportError:
        pass

# ── Required env vars for all integration tests ───────────────────────────────
_REQUIRED_VARS = [
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_KEY",
    "AZURE_SPEECH_KEY",
    "AZURE_SPEECH_REGION",
    "AZURE_SEARCH_ENDPOINT",
    "AZURE_SEARCH_KEY",
    "AZURE_SEARCH_INDEX",
]

_missing = [v for v in _REQUIRED_VARS if not os.getenv(v)]


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: marks tests as requiring real Azure credentials (skipped by default)",
    )


# ── Auto-skip if credentials are absent ───────────────────────────────────────
@pytest.fixture(autouse=True)
def require_azure_env(request):
    if request.node.get_closest_marker("integration") and _missing:
        pytest.skip(f"Missing Azure env vars: {', '.join(_missing)}")


# ── Settings fixture ───────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def settings():
    from app.config import get_settings
    get_settings.cache_clear()
    return get_settings()


# ── Unique test meeting ID (session-scoped) ────────────────────────────────────
@pytest.fixture(scope="session")
def test_meeting_id() -> str:
    """
    Unique meeting ID for this test run.  Uses doc_type='meeting' so test
    data never touches the permanent org KB.
    """
    return f"test-{uuid.uuid4().hex[:8]}"


# ── Azure AI Search client ─────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def search_client(settings):
    from azure.search.documents.aio import SearchClient
    from azure.core.credentials import AzureKeyCredential
    return SearchClient(
        endpoint=settings.azure_search_endpoint,
        index_name=settings.azure_search_index,
        credential=AzureKeyCredential(settings.azure_search_key),
    )


# ── Azure Blob Storage client ──────────────────────────────────────────────────
@pytest.fixture(scope="session")
def blob_client(settings):
    from app.storage.blob_client import BlobStorageClient
    return BlobStorageClient(settings)


# ── Cosmos DB client ───────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def cosmos_client(settings):
    from app.storage.cosmos_client import CosmosDBClient
    return CosmosDBClient(settings)
