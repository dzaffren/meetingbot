"""Unit tests for QAAgent — updated for AI Foundry agent stubs."""
from __future__ import annotations

import pytest

from app.transcription.transcript_buffer import TranscriptBuffer
from app.models.session import TranscriptEntry


@pytest.fixture
def buffer():
    buf = TranscriptBuffer()
    buf.append(TranscriptEntry(speaker="Alice", text="We are targeting Q3 for the launch."))
    return buf


@pytest.mark.asyncio
async def test_qa_answer_raises_not_implemented(buffer):
    # TODO: Replace with proper mock of AI Foundry agent once implemented.
    from app.agents.qa_agent import answer

    with pytest.raises(NotImplementedError):
        await answer(
            question="When is the launch?",
            meeting_id="m1",
            conversation_id="c1",
            buffer=buffer,
        )


@pytest.mark.asyncio
async def test_qa_answer_without_buffer_raises_not_implemented():
    # TODO: QA agent should handle None buffer gracefully (no transcript context).
    from app.agents.qa_agent import answer

    with pytest.raises(NotImplementedError):
        await answer(
            question="What is the company leave policy?",
            meeting_id="m1",
            conversation_id="c1",
            buffer=None,
        )

