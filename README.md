# MeetingBot

AI-powered meeting assistant with real-time transcription, multilingual support (English, Bahasa Malaysia, Manglish), and Microsoft 365 integration.

## Features

| Feature | Description |
|---|---|
| 🎙️ Real-time transcription | Azure Speech Services with auto language detection (EN / MS / Manglish) |
| 📝 Meeting minutes | Auto-generated structured minutes via GPT-4o at meeting end |
| ✅ Task assignment | Action items extracted and created as Microsoft Planner tasks with PIC assignment |
| 📄 SharePoint upload | Minutes automatically uploaded as `.docx` to a configured SharePoint site |
| 💬 In-meeting Q&A | Answer questions grounded in live transcript + uploaded docs + org KB + Bing web |
| 📎 Document context | Pre-upload meeting docs (PDF/DOCX/images) for the bot to reference |
| 🧠 Org knowledge base | Permanent Azure AI Search index for org-wide knowledge |

## Architecture

```
PRE-MEETING
  Document upload → Azure Document Intelligence → Azure AI Search (meeting-scoped)

LIVE MEETING
  Audio → Azure Speech Services (en-US + ms-MY) → TranscriptBuffer
  @mention → QA Agent → GPT-4o (transcript + docs + org KB + Bing)

POST-MEETING
  Transcript → MinutesAgent → MeetingMinutes
      ├── SharePoint upload (Graph API)
      └── TaskAgent → Planner tasks (Graph API)
```

## Tech Stack

- **Backend**: Python 3.13, FastAPI, uvicorn
- **Transcription**: Azure Speech Services
- **LLM**: Azure OpenAI (GPT-4o)
- **Document parsing**: Azure Document Intelligence
- **Knowledge retrieval**: Azure AI Search (hybrid vector + keyword)
- **Web search**: Bing Search API
- **M365 integration**: Microsoft Graph API (Planner + SharePoint)
- **Persistence**: Azure Cosmos DB, Azure Blob Storage
- **Auth**: Azure AD (app-only, client credentials)

---

## Prerequisites

1. Python 3.12+ (project uses `pyenv` — see setup below)
2. **All Azure resources already provisioned** in your subscription:
   - Azure OpenAI (GPT-4o + text-embedding-3-large deployments)
   - Azure Speech Services
   - Azure Document Intelligence
   - Azure AI Search (with an existing index)
   - Azure Blob Storage
   - Azure Cosmos DB (NoSQL)
   - Azure Container Registry + Container Apps (for deployment)
   - Bing Search (v7)
3. An Azure AD app registration with the Graph API permissions listed below
4. A Microsoft 365 tenant with Planner and SharePoint
5. **Linux**: `libportaudio2` installed (`sudo apt-get install libportaudio2`) for mic capture

### Required Azure AD App Permissions

| Permission | Type | Purpose |
|---|---|---|
| `Tasks.ReadWrite` | Application | Create/assign Planner tasks |
| `Group.Read.All` | Application | Read Planner plan group |
| `Sites.ReadWrite.All` | Application | Upload to SharePoint |
| `Files.ReadWrite.All` | Application | Write to SharePoint document libraries |
| `User.Read.All` | Application | Resolve PIC names → AAD user IDs |

Grant admin consent for all application permissions.

---

## Local Development Setup

### 1. Clone and set up Python environment

```bash
git clone <repo-url>
cd meetingbot

# Create pyenv virtualenv (uses Python 3.13 — already configured via .python-version)
pyenv install 3.13.5        # skip if already installed
pyenv virtualenv 3.13.5 meetingbot
pyenv local meetingbot      # auto-activated in this directory

# Install dependencies
pip install -e ".[dev]"
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your Azure credentials and resource details
```

Key variables to fill in:

| Variable | Description |
|---|---|
| `AZURE_OPENAI_ENDPOINT` | Your Azure OpenAI resource endpoint |
| `AZURE_OPENAI_API_KEY` | API key |
| `AZURE_OPENAI_DEPLOYMENT` | GPT-4o deployment name |
| `AZURE_SPEECH_KEY` | Azure Speech resource key |
| `AZURE_SPEECH_REGION` | e.g. `southeastasia` |
| `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` | Doc Intelligence endpoint |
| `AZURE_SEARCH_ENDPOINT` | AI Search endpoint |
| `AZURE_SEARCH_KEY` | AI Search admin key |
| `AZURE_SEARCH_INDEX` | Name of existing AI Search index |
| `AZURE_STORAGE_CONNECTION_STRING` | Blob Storage connection string |
| `AZURE_COSMOS_ENDPOINT` | Cosmos DB endpoint |
| `AZURE_COSMOS_KEY` | Cosmos DB primary key |
| `AZURE_TENANT_ID` | AAD tenant ID |
| `AZURE_CLIENT_ID` | App registration client ID |
| `AZURE_CLIENT_SECRET` | App registration client secret |
| `PLANNER_PLAN_ID` | Target Planner plan ID |
| `PLANNER_GROUP_ID` | M365 group owning the plan |
| `SHAREPOINT_SITE_ID` | SharePoint site ID |
| `SHAREPOINT_DRIVE_ID` | Document library drive ID |
| `BING_SEARCH_API_KEY` | Bing Search v7 API key |

### 3. Run the backend API

```bash
uvicorn app.main:app --reload
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 4. Run a live local meeting (laptop mic)

In a second terminal (with the API running):

```bash
python scripts/local_meeting.py \
    --title "Sprint Planning" \
    --participants "Alice,Bob,Charlie" \
    --speaker "Your Name"
```

**In-session commands:**

| Command | Action |
|---|---|
| `? <question>` | Ask the bot a question — answers using transcript + docs + org KB + web |
| `end` | End the meeting — generates minutes, uploads to SharePoint, creates Planner tasks |
| `Ctrl+C` | Same as `end` |

Example session:

```
════════════════════════════════════════════════════════════
  Meeting: Sprint Planning
  ID: 3f2e...
  Speaker: alice
════════════════════════════════════════════════════════════
  Listening... speak now.
  Commands:  ? <question>  |  end  |  Ctrl+C
════════════════════════════════════════════════════════════

  [10:04:22] alice: Let's review the backlog items.
  [10:04:35] alice: Bob will handle the auth module by Friday.

? Who owns the auth module?
[you] Who owns the auth module?
[bot] Based on the meeting so far, Bob is responsible for the auth module, with a deadline of Friday.

end

[bot] Generating meeting minutes…

════════════════════════════════════════════════════════════
  MEETING MINUTES: Sprint Planning
  Date: 2025-01-15  |  ID: 3f2e...
...
```

### 5. Run unit tests

```bash
pytest tests/unit/ -v
```

### 6. Run integration tests

Integration tests run against real Azure resources. Requires `.env` populated.

```bash
# All integration tests
pytest tests/integration/ -m integration -v

# Only a specific suite
pytest tests/integration/test_rag.py -m integration -v

# Include backend flow tests (requires uvicorn running separately)
MEETINGBOT_API_URL=http://localhost:8000 pytest tests/integration/test_meeting_flow.py -m integration -v
```

---

## Deployment (Azure Container Apps)

All Azure resources are assumed to be pre-provisioned. The deployment pipeline:
1. Builds the Docker image using ACR Tasks (no local Docker daemon required)
2. Pushes to your Container Registry
3. Updates the Container App to serve the new revision

### Required environment variables for deployment

```bash
export ACR_NAME=myregistry          # ACR name (without .azurecr.io)
export RESOURCE_GROUP=rg-meetingbot
export CONTAINER_APP_NAME=meetingbot
export CONTAINER_APP_ENV=meetingbot-env
```

### Deploy

```bash
# Login to Azure
az login

# Run the deployment script
./infra/deploy.sh

# Or specify an explicit tag
./infra/deploy.sh --tag v1.2.3
```

The script will:
1. Build & push the image: `az acr build ...`
2. Update the Container App: `az containerapp update ...`
3. Print the FQDN of the deployed app
