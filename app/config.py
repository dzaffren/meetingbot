from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ── Azure OpenAI ────────────────────────────────────────────────────────
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_deployment: str = "gpt-4o"
    azure_openai_embedding_deployment: str = "text-embedding-3-large"
    azure_openai_api_version: str = "2024-08-01-preview"

    # ── Azure Speech ────────────────────────────────────────────────────────
    azure_speech_key: str
    azure_speech_region: str = "southeastasia"

    # ── Azure Document Intelligence ─────────────────────────────────────────
    azure_document_intelligence_endpoint: str
    azure_document_intelligence_key: str

    # ── Azure AI Search ─────────────────────────────────────────────────────
    azure_search_endpoint: str
    azure_search_key: str
    azure_search_index_name: str = "meetingbot-index"

    # ── Azure Blob Storage ──────────────────────────────────────────────────
    azure_storage_connection_string: str
    azure_storage_container_meeting_docs: str = "meeting-docs"

    # ── Azure Cosmos DB ─────────────────────────────────────────────────────
    azure_cosmos_endpoint: str
    azure_cosmos_key: str
    azure_cosmos_database: str = "meetingbot"

    # ── Microsoft Graph / Azure AD ──────────────────────────────────────────
    azure_tenant_id: str
    azure_client_id: str
    azure_client_secret: str

    # ── Microsoft Planner ───────────────────────────────────────────────────
    planner_plan_id: str
    planner_group_id: str

    # ── SharePoint ──────────────────────────────────────────────────────────
    sharepoint_site_id: str
    sharepoint_drive_id: str
    sharepoint_folder_path: str = "Meeting Minutes"

    # ── Bing Search ─────────────────────────────────────────────────────────
    bing_search_api_key: str
    bing_search_endpoint: str = "https://api.bing.microsoft.com/v7.0/search"

    # ── App tuning ──────────────────────────────────────────────────────────
    # Max transcript entries to include as QA context
    qa_transcript_context_limit: int = 50
    # Max conversation history turns to include
    conversation_history_limit: int = 10
    # Number of search results to retrieve per source
    search_top_k: int = 5
    # Temp document TTL in days
    doc_ttl_days: int = 7


@lru_cache
def get_settings() -> Settings:
    return Settings()
