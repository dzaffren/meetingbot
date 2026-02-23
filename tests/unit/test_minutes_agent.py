"""Unit tests for MinutesAgent (mocked Azure OpenAI)."""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.models.session import MeetingSession, TranscriptEntry
from app.transcription.transcript_buffer import TranscriptBuffer


MOCK_MINUTES_JSON = {
    "title": "Q3 Planning Session",
    "attendees": ["Alice", "Bob"],
    "summary": "The team discussed Q3 roadmap priorities.",
    "key_decisions": ["Focus on mobile first", "Delay feature X to Q4"],
    "action_items": [
        {
            "title": "Prepare mobile spec",
            "description": "Write the spec document for mobile feature",
            "pic": "Alice",
            "due_date": "2026-03-01",
        },
        {
            "title": "Reschedule feature X",
            "description": "Move feature X to Q4 backlog",
            "pic": "Bob",
            "due_date": None,
        },
    ],
}


@pytest.fixture
def session():
    return MeetingSession(
        id="test-meeting-123",
        title="Q3 Planning",
        participants=["Alice", "Bob"],
    )


@pytest.fixture
def buffer_with_entries():
    buf = TranscriptBuffer()
    buf.append(TranscriptEntry(speaker="Alice", text="Let's focus on mobile this quarter lah."))
    buf.append(TranscriptEntry(speaker="Bob", text="Agreed. Feature X boleh defer to Q4."))
    return buf


@pytest.mark.asyncio
async def test_generate_minutes_returns_structured_output(session, buffer_with_entries):
    with patch(
        "app.agents.minutes_agent.chat_completion",
        new=AsyncMock(return_value=json.dumps(MOCK_MINUTES_JSON)),
    ):
        from app.agents.minutes_agent import generate_minutes

        minutes = await generate_minutes(session=session, buffer=buffer_with_entries)

    assert minutes.meeting_id == "test-meeting-123"
    assert minutes.title == "Q3 Planning Session"
    assert len(minutes.action_items) == 2
    assert minutes.action_items[0].pic == "Alice"
    assert minutes.action_items[0].due_date is not None
    assert minutes.action_items[1].due_date is None


@pytest.mark.asyncio
async def test_generate_minutes_empty_transcript(session):
    buf = TranscriptBuffer()  # empty

    from app.agents.minutes_agent import generate_minutes

    minutes = await generate_minutes(session=session, buffer=buf)
    assert "No transcript" in minutes.summary
    assert minutes.action_items == []


@pytest.mark.asyncio
async def test_generate_minutes_accepts_entries_list(session):
    entries = [TranscriptEntry(speaker="Alice", text="Let's do it lah.")]
    with patch(
        "app.agents.minutes_agent.chat_completion",
        new=AsyncMock(return_value=json.dumps(MOCK_MINUTES_JSON)),
    ):
        from app.agents.minutes_agent import generate_minutes

        minutes = await generate_minutes(session=session, entries=entries)

    assert minutes.title == "Q3 Planning Session"
