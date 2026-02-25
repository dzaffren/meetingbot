"""Unit tests for TaskAgent — updated for AI Foundry agent stubs."""
from __future__ import annotations

from datetime import date

import pytest

from app.models.minutes import ActionItem, MeetingMinutes


@pytest.fixture
def minutes():
    return MeetingMinutes(
        meeting_id="m1",
        title="Test Meeting",
        attendees=["Alice", "Bob"],
        summary="Summary.",
        action_items=[
            ActionItem(title="Write spec", pic="Alice", due_date=date(2026, 3, 1)),
            ActionItem(title="Review PR", pic="Bob", due_date=None),
        ],
    )


@pytest.mark.asyncio
async def test_assign_tasks_raises_not_implemented(minutes):
    # TODO: Replace with proper mock of AI Foundry agent once implemented.
    from app.agents.task_agent import assign_tasks

    with pytest.raises(NotImplementedError):
        await assign_tasks(minutes)


@pytest.mark.asyncio
async def test_assign_tasks_no_items_raises_not_implemented():
    # TODO: Once assign_tasks() is implemented, empty action_items should return early.
    m = MeetingMinutes(
        meeting_id="m2",
        title="Empty",
        summary="No tasks.",
    )
    from app.agents.task_agent import assign_tasks

    with pytest.raises(NotImplementedError):
        await assign_tasks(m)

