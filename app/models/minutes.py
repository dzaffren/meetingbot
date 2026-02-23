from __future__ import annotations

from datetime import date as date_type, datetime, timezone
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ActionItem(BaseModel):
    """A single action item extracted from meeting minutes."""

    title: str
    description: str = ""
    pic: str  # Person In Charge (display name from meeting participants)
    due_date: date_type | None = None
    # Populated after Planner task creation
    planner_task_id: str | None = None


class MeetingMinutes(BaseModel):
    """Structured output of the MinutesAgent."""

    meeting_id: str
    title: str
    date: date_type = Field(default_factory=date_type.today)
    attendees: list[str] = Field(default_factory=list)
    summary: str
    key_decisions: list[str] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)
    # URL populated after SharePoint upload
    sharepoint_url: str | None = None
    created_at: datetime = Field(default_factory=_utcnow)
