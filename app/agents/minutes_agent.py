from __future__ import annotations

import json
import logging
from datetime import date as date_type

from app.agents.base import chat_completion, system_message
from app.models.minutes import ActionItem, MeetingMinutes
from app.models.session import MeetingSession, TranscriptEntry
from app.transcription.transcript_buffer import TranscriptBuffer

logger = logging.getLogger(__name__)

_EXTRA_INSTRUCTIONS = """
Your task: generate structured meeting minutes from the provided transcript.

Output a single JSON object matching this schema exactly:
{
  "title": "<descriptive meeting title>",
  "attendees": ["<name>", ...],
  "summary": "<2-4 paragraph executive summary in formal English>",
  "key_decisions": ["<decision 1>", ...],
  "action_items": [
    {
      "title": "<short task title>",
      "description": "<detailed description of what needs to be done>",
      "pic": "<full name of Person In Charge, exactly as mentioned in transcript>",
      "due_date": "<YYYY-MM-DD or null>"
    }
  ]
}

Rules:
- Output ONLY the JSON object, no markdown fences, no extra text.
- Infer the meeting title from the discussion topics.
- Extract every commitment, task, or follow-up mentioned — even casual ones ("I'll check on that").
- If a due date is not stated, set due_date to null.
- Normalize all names to their full form if possible.
- Minutes must be in formal English regardless of the spoken language in the transcript.
"""


async def generate_minutes(
    session: MeetingSession,
    buffer: TranscriptBuffer | None = None,
    entries: list[TranscriptEntry] | None = None,
) -> MeetingMinutes:
    """
    Generate structured meeting minutes from a TranscriptBuffer or a list of entries.

    Args:
        session: The active MeetingSession (provides meeting_id, participants, etc.).
        buffer: TranscriptBuffer to snapshot. Mutually exclusive with `entries`.
        entries: Explicit list of TranscriptEntry. Used if buffer is None.

    Returns:
        A populated MeetingMinutes Pydantic model.
    """
    if buffer is not None:
        transcript_entries = buffer.snapshot()
    elif entries is not None:
        transcript_entries = entries
    else:
        raise ValueError("Either buffer or entries must be provided")

    if not transcript_entries:
        logger.warning("No transcript entries to summarise for meeting %s", session.id)
        return MeetingMinutes(
            meeting_id=session.id,
            title=session.title,
            attendees=session.participants,
            summary="No transcript was recorded for this meeting.",
        )

    # Format transcript as readable text
    transcript_text = TranscriptBuffer().to_text(transcript_entries)
    participants_str = ", ".join(session.participants) if session.participants else "Unknown"

    user_content = (
        f"Meeting participants: {participants_str}\n\n"
        f"--- TRANSCRIPT ---\n{transcript_text}\n--- END TRANSCRIPT ---\n\n"
        "Generate the meeting minutes JSON now."
    )

    messages = [
        system_message(_EXTRA_INSTRUCTIONS),
        {"role": "user", "content": user_content},
    ]

    raw = await chat_completion(messages, response_format={"type": "json_object"})

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("MinutesAgent returned invalid JSON: %s", exc)
        raise

    action_items = [
        ActionItem(
            title=a["title"],
            description=a.get("description", ""),
            pic=a["pic"],
            due_date=date_type.fromisoformat(a["due_date"]) if a.get("due_date") else None,
        )
        for a in data.get("action_items", [])
    ]

    return MeetingMinutes(
        meeting_id=session.id,
        title=data.get("title", session.title),
        attendees=data.get("attendees", session.participants),
        summary=data.get("summary", ""),
        key_decisions=data.get("key_decisions", []),
        action_items=action_items,
    )
