from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TranscriptEntry(BaseModel):
    """A single recognized speech utterance."""

    speaker: str
    text: str
    language: str = "en-US"  # e.g. "en-US" or "ms-MY"
    timestamp: datetime = Field(default_factory=_utcnow)


class MeetingSession(BaseModel):
    """Tracks an active or completed meeting session."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str = "Untitled Meeting"
    participants: list[str] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=_utcnow)
    ended_at: datetime | None = None
    status: Literal["active", "ended"] = "active"
    # IDs of documents pre-uploaded for this session
    document_ids: list[str] = Field(default_factory=list)


class ConversationTurn(BaseModel):
    """A single Q&A turn in a meeting chat."""

    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime = Field(default_factory=_utcnow)
