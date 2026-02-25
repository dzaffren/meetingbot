"""Unit tests for MinutesAgent — updated for AI Foundry agent stubs."""
from __future__ import annotations

import pytest

from app.models.session import MeetingSession, TranscriptEntry
from app.transcription.transcript_buffer import TranscriptBuffer


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
async def test_generate_minutes_raises_not_implemented(session, buffer_with_entries):
    # TODO: Replace with proper mock of AI Foundry agent once implemented.
    # For now, assert that the stub raises NotImplementedError.
    from app.agents.minutes_agent import generate_minutes

    with pytest.raises(NotImplementedError):
        await generate_minutes(session=session, buffer=buffer_with_entries)


@pytest.mark.asyncio
async def test_generate_minutes_empty_transcript_raises_not_implemented(session):
    # TODO: Once generate_minutes() is implemented, empty transcript should return
    # a MeetingMinutes with summary="No transcript was recorded for this meeting."
    buf = TranscriptBuffer()  # empty

    from app.agents.minutes_agent import generate_minutes

    with pytest.raises(NotImplementedError):
        await generate_minutes(session=session, buffer=buf)


@pytest.mark.asyncio
async def test_generate_minutes_requires_buffer_or_entries(session):
    from app.agents.minutes_agent import generate_minutes

    with pytest.raises((NotImplementedError, ValueError)):
        await generate_minutes(session=session)

