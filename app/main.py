from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.agents import minutes_agent, qa_agent, task_agent
from app.integrations.sharepoint import upload_minutes
from app.models.session import MeetingSession
from app.rag.document_processor import process_document
from app.rag.retriever import ensure_index, upsert_chunks
from app.storage.blob_client import get_blob_store
from app.storage.cosmos_client import (
    CONTAINER_MINUTES,
    CONTAINER_SESSIONS,
    get_cosmos_store,
)
from app.transcription.transcript_buffer import TranscriptBuffer

# In-memory map of meeting_id → TranscriptBuffer (lives for the duration of the server process)
_active_buffers: dict[str, TranscriptBuffer] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise Azure resources on startup."""
    cosmos = get_cosmos_store()
    await cosmos.initialize()

    blob = get_blob_store()
    await blob.initialize()

    await ensure_index()

    yield

    await cosmos.close()
    await blob.close()


app = FastAPI(title="MeetingBot API", version="0.1.0", lifespan=lifespan)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok"}


# ── Meeting session ───────────────────────────────────────────────────────────

class StartMeetingRequest(BaseModel):
    title: str = "Untitled Meeting"
    participants: list[str] = []


@app.post("/meetings", status_code=201)
async def start_meeting(body: StartMeetingRequest):
    """Start a new meeting session."""
    session = MeetingSession(
        id=str(uuid.uuid4()),
        title=body.title,
        participants=body.participants,
    )
    store = get_cosmos_store()
    await store.upsert(CONTAINER_SESSIONS, session.model_dump(mode="json"))
    _active_buffers[session.id] = TranscriptBuffer()
    return {"meeting_id": session.id, "status": "active"}


@app.post("/meetings/{meeting_id}/end")
async def end_meeting(meeting_id: str):
    """
    End a meeting session:
    1. Generate meeting minutes from the transcript buffer.
    2. Upload minutes to SharePoint.
    3. Create Planner tasks for all action items.
    4. Persist minutes to Cosmos DB.
    """
    store = get_cosmos_store()
    session_doc = await store.get(CONTAINER_SESSIONS, meeting_id)
    if not session_doc:
        raise HTTPException(status_code=404, detail="Meeting not found")

    session = MeetingSession(**session_doc)
    buffer = _active_buffers.get(meeting_id)

    # Generate minutes
    minutes = await minutes_agent.generate_minutes(session=session, buffer=buffer)

    # Upload to SharePoint
    try:
        sp_url = await upload_minutes(minutes)
        minutes.sharepoint_url = sp_url
    except Exception as exc:
        # Non-fatal: log and continue
        minutes.sharepoint_url = None

    # Assign tasks in Planner
    minutes = await task_agent.assign_tasks(minutes)

    # Persist minutes
    await store.upsert(CONTAINER_MINUTES, minutes.model_dump(mode="json"))

    # Mark session ended
    session.status = "ended"
    session.ended_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await store.upsert(CONTAINER_SESSIONS, session.model_dump(mode="json"))

    # Clean up buffer
    _active_buffers.pop(meeting_id, None)

    return minutes.model_dump(mode="json")


@app.get("/meetings/{meeting_id}/minutes")
async def get_minutes(meeting_id: str):
    """Retrieve stored meeting minutes."""
    store = get_cosmos_store()
    doc = await store.get(CONTAINER_MINUTES, meeting_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Minutes not found")
    return doc


# ── Transcript ingestion (for PoC / testing without live audio) ───────────────

class TranscriptLine(BaseModel):
    speaker: str
    text: str
    language: str = "en-US"


@app.post("/meetings/{meeting_id}/transcript")
async def add_transcript(meeting_id: str, lines: list[TranscriptLine]):
    """Push transcript lines into the live buffer (for PoC/testing)."""
    from app.models.session import TranscriptEntry

    buf = _active_buffers.get(meeting_id)
    if buf is None:
        raise HTTPException(status_code=404, detail="No active meeting buffer")

    for line in lines:
        buf.append(TranscriptEntry(speaker=line.speaker, text=line.text, language=line.language))

    return {"buffered": len(lines), "total": len(buf)}


@app.get("/meetings/{meeting_id}/transcript")
async def get_transcript(meeting_id: str):
    """Return the current transcript for the active meeting."""
    buf = _active_buffers.get(meeting_id)
    if buf is None:
        raise HTTPException(status_code=404, detail="No active meeting buffer")
    return {"entries": [e.model_dump(mode="json") for e in buf.snapshot()]}


# ── Document upload ───────────────────────────────────────────────────────────

@app.post("/meetings/{meeting_id}/documents", status_code=201)
async def upload_document(
    meeting_id: str,
    file: UploadFile = File(...),
):
    """
    Pre-upload a document for a meeting session.
    The document is processed by Document Intelligence and indexed in AI Search.
    """
    store = get_cosmos_store()
    session_doc = await store.get(CONTAINER_SESSIONS, meeting_id)
    if not session_doc:
        raise HTTPException(status_code=404, detail="Meeting not found")

    blob_store = get_blob_store()
    file_bytes = await file.read()

    # Store in Blob
    blob_name = await blob_store.upload(
        data=file_bytes,
        filename=file.filename or "upload",
        meeting_id=meeting_id,
        content_type=file.content_type or "application/octet-stream",
    )

    # Process with Document Intelligence
    chunks = await process_document(
        file_bytes=file_bytes,
        filename=file.filename or "upload",
        meeting_id=meeting_id,
        doc_type="meeting",
    )

    # Index chunks in Azure AI Search
    await upsert_chunks(chunks)

    # Track document in session
    session = MeetingSession(**session_doc)
    session.document_ids.append(blob_name)
    await store.upsert(CONTAINER_SESSIONS, session.model_dump(mode="json"))

    return {"blob_name": blob_name, "chunks_indexed": len(chunks)}


# ── Q&A ───────────────────────────────────────────────────────────────────────

class QARequest(BaseModel):
    question: str
    conversation_id: str | None = None


@app.post("/meetings/{meeting_id}/qa")
async def ask_question(meeting_id: str, body: QARequest):
    """Answer a question in the context of the active meeting."""
    conversation_id = body.conversation_id or meeting_id
    buffer = _active_buffers.get(meeting_id)

    answer = await qa_agent.answer(
        question=body.question,
        meeting_id=meeting_id,
        conversation_id=conversation_id,
        buffer=buffer,
    )
    return {"answer": answer, "conversation_id": conversation_id}
