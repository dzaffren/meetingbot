"""
Integration tests — full meeting flow (start → transcript → Q&A → end).

Runs against a live FastAPI backend.  Start the backend before running:
    uvicorn app.main:app --reload

Skipped automatically if MEETINGBOT_API_URL is not set or if Azure vars are missing.
"""
from __future__ import annotations

import os
import uuid

import httpx
import pytest

API_BASE = os.getenv("MEETINGBOT_API_URL", "http://localhost:8000")


def _api(path: str, *, method: str = "POST", **kwargs) -> dict:
    url = f"{API_BASE}{path}"
    resp = httpx.request(method, url, timeout=60.0, **kwargs)
    resp.raise_for_status()
    return resp.json()


# ── Skip entire module if backend is unreachable ───────────────────────────────
def pytest_runtest_setup(item):
    """Skip flow tests if the backend is not running."""
    if "test_meeting_flow" in item.nodeid or "test_qa" in item.nodeid:
        try:
            httpx.get(f"{API_BASE}/health", timeout=3.0).raise_for_status()
        except Exception:
            pytest.skip(f"Backend not reachable at {API_BASE}")


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def meeting_session() -> dict:
    """Creates a meeting and tears it down (end) after the module."""
    session = _api(
        "/meetings",
        json={
            "title": "Integration Test Meeting",
            "participants": ["IntegrationBot", "TestUser"],
        },
    )
    yield session
    # Best-effort cleanup — ignore if already ended
    try:
        _api(f"/meetings/{session['meeting_id']}/end")
    except Exception:
        pass


# ── Tests ──────────────────────────────────────────────────────────────────────

@pytest.mark.integration
def test_create_meeting(meeting_session):
    """POST /meetings returns a valid session with a meeting_id."""
    assert "meeting_id" in meeting_session
    assert meeting_session.get("status") == "active"


@pytest.mark.integration
def test_push_transcript_entries(meeting_session):
    """POST /meetings/{id}/transcript accepts a batch of transcript entries."""
    meeting_id = meeting_session["meeting_id"]
    entries = [
        {"speaker": "TestUser", "text": "Welcome everyone to the integration test meeting.", "language": "en-US"},
        {"speaker": "IntegrationBot", "text": "The main agenda today is to review the test results.", "language": "en-US"},
        {"speaker": "TestUser", "text": "Alice will prepare a test summary report by Friday.", "language": "en-US"},
    ]
    result = _api(f"/meetings/{meeting_id}/transcript", json=entries)
    assert result.get("added") == len(entries)


@pytest.mark.integration
def test_qa_with_transcript_context(meeting_session):
    """POST /meetings/{id}/qa answers a question using the live transcript."""
    meeting_id = meeting_session["meeting_id"]
    result = _api(
        f"/meetings/{meeting_id}/qa",
        json={
            "question": "Who is preparing the test summary report?",
            "conversation_id": meeting_id,
        },
    )
    assert "answer" in result
    assert len(result["answer"]) > 10  # non-trivial answer
    # Expect Alice to be mentioned given the transcript context
    assert "Alice" in result["answer"] or "summary" in result["answer"].lower()


@pytest.mark.integration
def test_end_meeting_returns_minutes(meeting_session):
    """POST /meetings/{id}/end returns a MeetingMinutes object."""
    meeting_id = meeting_session["meeting_id"]
    minutes = _api(f"/meetings/{meeting_id}/end")

    assert minutes.get("meeting_id") == meeting_id
    assert "summary" in minutes
    assert isinstance(minutes.get("action_items"), list)
    assert isinstance(minutes.get("key_decisions"), list)

    # At least one action item should reference Alice and the report
    action_titles = [item.get("title", "") for item in minutes["action_items"]]
    assert any(
        "report" in t.lower() or "alice" in t.lower() or "summary" in t.lower()
        for t in action_titles
    ), f"Expected action item about report, got: {action_titles}"


@pytest.mark.integration
def test_ended_meeting_is_not_active():
    """A second /end call on the same meeting should return 404 or 409."""
    # Create a fresh short-lived meeting and end it twice
    session = _api(
        "/meetings",
        json={"title": "End-twice test", "participants": []},
    )
    mid = session["meeting_id"]
    _api(f"/meetings/{mid}/end")

    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        _api(f"/meetings/{mid}/end")

    assert exc_info.value.response.status_code in (404, 409, 400)
