# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- 

### Changed
- 

### Fixed
- 

---

## [0.2.0] — Phase 1 Backend Rebuild

### Added
- Azure AI Foundry Agent SDK (`azure-ai-projects`) as the primary agent runtime
- `app/agents/orchestrator.py` — top-level agent routing meeting tasks to sub-agents
- `app/agents/tools/` — AI Foundry function tool definitions: AI Search, Bing web search, Planner, SharePoint, Graph
- `app/utils/logging.py` — structured JSON logging helper (`configure_logging`)
- `app/utils/auth.py` — token helper stubs (ready for Bot Framework Phase 2)
- `app/utils/document_generator.py` — Word (`.docx`) and PDF generation stubs
- `app/rag/org_kb_indexer.py` — bulk org knowledge base indexing pipeline
- `scripts/index_org_kb.py` — CLI tool to index org KB documents into Azure AI Search
- `CHANGELOG.md` — this file

### Changed
- `app/agents/base.py` — migrated from raw `AsyncAzureOpenAI` to `AIProjectClient` factory
- `app/agents/minutes_agent.py`, `qa_agent.py`, `task_agent.py` — stubs updated for AI Foundry agent pattern
- `app/config.py` — added `AZURE_AI_FOUNDRY_PROJECT_CONNECTION_STRING`, `AZURE_AI_FOUNDRY_MODEL_DEPLOYMENT`
- `app/rag/retriever.py`, `web_search.py`, `document_processor.py` — preserved signatures, cleared implementation to `# TODO`
- `app/integrations/planner.py`, `sharepoint.py` — preserved signatures, cleared implementation to `# TODO`
- `pyproject.toml` — added `azure-ai-projects`, `reportlab`, `jinja2` dependencies

### Fixed
- 

---

## [0.1.0] — Initial Project

### Added
- FastAPI REST API with Azure OpenAI-based agents
- Real-time transcription via Azure Speech SDK
- RAG pipeline with Azure AI Search (hybrid search)
- Microsoft Planner task creation via Graph API
- SharePoint document upload
- Azure Cosmos DB session + minutes persistence
- Azure Blob Storage for meeting documents
