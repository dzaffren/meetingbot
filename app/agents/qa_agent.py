from __future__ import annotations

import logging

from app.agents.base import (
    MULTILINGUAL_SYSTEM_PREAMBLE,
    create_or_get_agent,
    run_agent_thread,
)
from app.agents.tools.search_tools import SEARCH_MEETING_DOCS_TOOL, SEARCH_ORG_KB_TOOL
from app.agents.tools.web_search_tool import WEB_SEARCH_TOOL
from app.agents.tools.graph_tool import GET_MEETING_INFO_TOOL
from app.transcription.transcript_buffer import TranscriptBuffer

logger = logging.getLogger(__name__)

_AGENT_NAME = "meetingbot-qa-agent"

_INSTRUCTIONS = f"""{MULTILINGUAL_SYSTEM_PREAMBLE}

Your task: answer questions accurately and concisely using the available tools.

You have access to:
- search_meeting_docs: search documents uploaded for the current meeting
- search_org_kb: search the organisation's general knowledge base
- web_search: search the web for external or current information
- get_meeting_info: retrieve Teams meeting metadata

Guidelines:
- Always search internal sources before the web.
- Cite your sources inline: (Source: <filename>) or (Web: <url>).
- If information is not found in any source, say so honestly.
- Keep responses concise. Use bullet points for lists.
- Respond in the same language the user used (English / Malay / Manglish).
"""


async def answer(
    question: str,
    meeting_id: str,
    conversation_id: str,
    buffer: TranscriptBuffer | None = None,
) -> str:
    """
    Answer a question using an AI Foundry agent with multi-source RAG tools.

    The agent autonomously decides which tools to call (meeting docs search,
    org KB search, web search) based on the question context.

    Args:
        question: The user's question (EN / Malay / Manglish).
        meeting_id: Used to scope meeting document search to the current session.
        conversation_id: Unique ID for this conversation thread (for multi-turn history).
        buffer: The live TranscriptBuffer; included as context in the user message.

    Returns:
        The assistant's answer as a string.
    """
    # TODO: Implement Q&A using the AI Foundry agent.
    #
    # Pattern:
    #   1. Build a user message that includes:
    #      - Current transcript snippet (last N entries from buffer)
    #      - The user's question
    #      - meeting_id as context (for tool calls)
    #   2. Get or create the QA agent via create_or_get_agent()
    #   3. Call run_agent_thread(agent_id, user_message, thread_id=conversation_id)
    #      → the agent calls search_meeting_docs, search_org_kb, web_search as needed
    #   4. Persist conversation turn to Cosmos DB (CONTAINER_HISTORY)
    #   5. Return the final answer string
    raise NotImplementedError("TODO: implement qa_agent.answer()")

