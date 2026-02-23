from __future__ import annotations

import logging
from typing import Sequence

from app.agents.base import chat_completion, system_message
from app.config import get_settings
from app.models.session import ConversationTurn, TranscriptEntry
from app.rag.retriever import hybrid_search
from app.rag.web_search import web_search
from app.storage.cosmos_client import CONTAINER_HISTORY, get_cosmos_store
from app.transcription.transcript_buffer import TranscriptBuffer

logger = logging.getLogger(__name__)

_EXTRA_INSTRUCTIONS = """
Your task: answer the user's question accurately and concisely.

You will be given:
1. TRANSCRIPT CONTEXT — the most recent portion of the live meeting transcript.
2. DOCUMENT CONTEXT — relevant excerpts from pre-uploaded meeting documents and the 
   organisation's knowledge base, each with a [Source: ...] label.
3. WEB CONTEXT — web search snippets (if internal sources are insufficient).
4. CONVERSATION HISTORY — previous Q&A turns in this session.

Guidelines:
- Prioritise information from Transcript and Documents over Web.
- Always cite your sources: e.g. "(Source: Q3 Report.pdf, p.3)" or "(Web: <url>)".
- If the answer is not in any context, say so honestly — do not fabricate.
- Keep responses clear and concise. Use bullet points for lists.
- You understand English, Bahasa Malaysia, and Manglish — respond in the same language 
  the user used, except for formal outputs which are always in English.
"""


def _format_search_results(results: list[dict]) -> str:
    if not results:
        return "No relevant documents found."
    lines = []
    for r in results:
        source_label = f"{r['source']} (p.{r['page']})" if r.get("page") else r.get("source", "")
        lines.append(f"[Source: {source_label}]\n{r['content']}")
    return "\n\n".join(lines)


def _format_web_results(results: list[dict]) -> str:
    if not results:
        return "No web results."
    lines = [f"[Web: {r['url']}]\n{r['title']}: {r['snippet']}" for r in results]
    return "\n\n".join(lines)


async def answer(
    question: str,
    meeting_id: str,
    conversation_id: str,
    buffer: TranscriptBuffer | None = None,
) -> str:
    """
    Answer a question using multi-source RAG:
      1. Current live transcript context
      2. Pre-uploaded meeting documents (AI Search, meeting-scoped)
      3. Permanent org KB (AI Search, org-scoped)
      4. Bing web search

    Conversation history is loaded from Cosmos DB and appended.

    Args:
        question: The user's question (EN / Malay / Manglish).
        meeting_id: Used to scope document retrieval to the current session.
        conversation_id: Unique ID for this conversation thread (for history).
        buffer: The live TranscriptBuffer; if None, no transcript context is used.

    Returns:
        The assistant's answer as a string.
    """
    settings = get_settings()
    store = get_cosmos_store()

    # ── 1. Transcript context ────────────────────────────────────────────────
    if buffer:
        transcript_ctx = buffer.to_text(buffer.last_n(settings.qa_transcript_context_limit))
    else:
        transcript_ctx = "(No live transcript available)"

    # ── 2. Meeting document search ────────────────────────────────────────────
    meeting_docs = await hybrid_search(question, meeting_id=meeting_id, doc_type="meeting")

    # ── 3. Org KB search ─────────────────────────────────────────────────────
    org_docs = await hybrid_search(question, doc_type="org")

    # ── 4. Web search (if internal results are sparse) ────────────────────────
    total_internal = len(meeting_docs) + len(org_docs)
    web_results = []
    if total_internal < 2:
        web_results = await web_search(question)

    # ── 5. Conversation history ───────────────────────────────────────────────
    history_records = await store.query(
        CONTAINER_HISTORY,
        "SELECT * FROM c WHERE c.conversation_id = @cid ORDER BY c._ts DESC OFFSET 0 LIMIT @n",
        [
            {"name": "@cid", "value": conversation_id},
            {"name": "@n", "value": settings.conversation_history_limit},
        ],
    )
    # Reverse to chronological order
    history_turns: list[ConversationTurn] = [
        ConversationTurn(role=r["role"], content=r["content"])
        for r in reversed(history_records)
    ]

    # ── 6. Build messages ─────────────────────────────────────────────────────
    context_block = (
        f"## TRANSCRIPT CONTEXT (last {settings.qa_transcript_context_limit} utterances)\n"
        f"{transcript_ctx}\n\n"
        f"## DOCUMENT CONTEXT (meeting docs)\n"
        f"{_format_search_results(meeting_docs)}\n\n"
        f"## DOCUMENT CONTEXT (org knowledge base)\n"
        f"{_format_search_results(org_docs)}\n\n"
        f"## WEB CONTEXT\n"
        f"{_format_web_results(web_results)}"
    )

    messages = [system_message(_EXTRA_INSTRUCTIONS)]
    messages.append({"role": "user", "content": context_block})

    for turn in history_turns:
        messages.append({"role": turn.role, "content": turn.content})

    messages.append({"role": "user", "content": question})

    # ── 7. Generate answer ────────────────────────────────────────────────────
    answer_text = await chat_completion(messages)

    # ── 8. Persist this turn to history ──────────────────────────────────────
    import uuid
    from datetime import datetime, timezone

    for role, content in [("user", question), ("assistant", answer_text)]:
        await store.upsert(
            CONTAINER_HISTORY,
            {
                "id": str(uuid.uuid4()),
                "conversation_id": conversation_id,
                "meeting_id": meeting_id,
                "role": role,
                "content": content,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    return answer_text
