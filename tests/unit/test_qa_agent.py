"""Unit tests for QAAgent (mocked retrieval and LLM)."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.transcription.transcript_buffer import TranscriptBuffer
from app.models.session import TranscriptEntry


@pytest.fixture
def buffer():
    buf = TranscriptBuffer()
    buf.append(TranscriptEntry(speaker="Alice", text="We are targeting Q3 for the launch."))
    return buf


def _mock_settings():
    s = MagicMock()
    s.qa_transcript_context_limit = 50
    s.conversation_history_limit = 10
    s.search_top_k = 5
    return s


@pytest.mark.asyncio
async def test_qa_returns_answer(buffer):
    with (
        patch("app.agents.qa_agent.hybrid_search", new=AsyncMock(return_value=[])),
        patch("app.agents.qa_agent.web_search", new=AsyncMock(return_value=[])),
        patch("app.agents.qa_agent.get_settings", return_value=_mock_settings()),
        patch(
            "app.agents.qa_agent.get_cosmos_store",
            return_value=MagicMock(
                query=AsyncMock(return_value=[]),
                upsert=AsyncMock(),
            ),
        ),
        patch(
            "app.agents.qa_agent.chat_completion",
            new=AsyncMock(return_value="The launch is targeted for Q3."),
        ),
    ):
        from app.agents.qa_agent import answer

        result = await answer(
            question="When is the launch?",
            meeting_id="m1",
            conversation_id="c1",
            buffer=buffer,
        )

    assert "Q3" in result


@pytest.mark.asyncio
async def test_qa_calls_web_search_when_no_docs(buffer):
    """Web search should be triggered when internal results are sparse."""
    web_mock = AsyncMock(
        return_value=[{"title": "News", "snippet": "Q3 launch", "url": "http://x.com"}]
    )

    with (
        patch("app.agents.qa_agent.hybrid_search", new=AsyncMock(return_value=[])),
        patch("app.agents.qa_agent.web_search", web_mock),
        patch("app.agents.qa_agent.get_settings", return_value=_mock_settings()),
        patch(
            "app.agents.qa_agent.get_cosmos_store",
            return_value=MagicMock(
                query=AsyncMock(return_value=[]),
                upsert=AsyncMock(),
            ),
        ),
        patch("app.agents.qa_agent.chat_completion", new=AsyncMock(return_value="answer")),
    ):
        from app.agents.qa_agent import answer

        await answer("When is the launch?", "m1", "c1", buffer)

    web_mock.assert_called_once()
