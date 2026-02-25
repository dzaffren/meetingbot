from __future__ import annotations

import logging

from app.agents.base import (
    MULTILINGUAL_SYSTEM_PREAMBLE,
    create_or_get_agent,
    run_agent_thread,
)
from app.agents.tools.search_tools import SEARCH_MEETING_DOCS_TOOL, SEARCH_ORG_KB_TOOL
from app.agents.tools.sharepoint_tool import UPLOAD_MINUTES_TO_SHAREPOINT_TOOL
from app.models.minutes import ActionItem, MeetingMinutes
from app.models.session import MeetingSession
from app.transcription.transcript_buffer import TranscriptBuffer

logger = logging.getLogger(__name__)

_AGENT_NAME = "meetingbot-minutes-agent"

_INSTRUCTIONS = f"""{MULTILINGUAL_SYSTEM_PREAMBLE}

Your task: generate structured meeting minutes from the provided meeting transcript.

You have access to tools to search meeting documents and upload the final minutes
to SharePoint. Use them when appropriate.

Output a JSON object with the following fields:
  title, attendees, summary, key_decisions, action_items
  (action_items: list of {{title, description, pic, due_date}})

Always output formal English for minutes regardless of transcript language.
"""


async def generate_minutes(
    session: MeetingSession,
    buffer: TranscriptBuffer | None = None,
    entries: list | None = None,
) -> MeetingMinutes:
    """
    Generate structured meeting minutes from a TranscriptBuffer using an AI Foundry agent.

    Args:
        session: The active MeetingSession (provides meeting_id, participants, etc.).
        buffer: TranscriptBuffer to snapshot. Mutually exclusive with `entries`.
        entries: Explicit list of TranscriptEntry. Used if buffer is None.

    Returns:
        A populated MeetingMinutes Pydantic model.
    """
    # TODO: Implement minutes generation using the AI Foundry agent.
    #
    # Pattern:
    #   1. Build transcript text from buffer or entries
    #   2. Get or create the minutes agent via create_or_get_agent()
    #   3. Call run_agent_thread() with a user message containing the transcript
    #   4. Handle tool calls (search_meeting_docs, upload_minutes_to_sharepoint) in the loop
    #   5. Parse the final JSON response into a MeetingMinutes object
    #
    # Example user message:
    #   f"Meeting participants: {', '.join(session.participants)}\n\n"
    #   f"--- TRANSCRIPT ---\n{transcript_text}\n--- END TRANSCRIPT ---\n\n"
    #   "Generate the meeting minutes JSON now."
    #
    # Tool call handler (in run_agent_thread — see base.py TODO):
    #   from app.agents.tools.search_tools import execute_search_tool
    #   from app.agents.tools.sharepoint_tool import execute_upload_minutes_tool
    raise NotImplementedError("TODO: implement generate_minutes()")

