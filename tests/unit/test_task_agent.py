"""Unit tests for TaskAgent (mocked Planner and Cosmos)."""
from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

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
async def test_assign_tasks_creates_planner_tasks(minutes):
    async def _planner_mock(items):
        for idx, i in enumerate(items):
            i.planner_task_id = f"task-{idx}"
        return items

    cosmos_mock = MagicMock()
    cosmos_mock.upsert = AsyncMock()

    with (
        patch("app.agents.task_agent.create_planner_tasks", side_effect=_planner_mock),
        patch("app.agents.task_agent.get_cosmos_store", return_value=cosmos_mock),
    ):
        from app.agents.task_agent import assign_tasks

        result = await assign_tasks(minutes)

    assert len(result.action_items) == 2
    assert cosmos_mock.upsert.call_count == 2


@pytest.mark.asyncio
async def test_assign_tasks_no_items():
    m = MeetingMinutes(
        meeting_id="m2",
        title="Empty",
        summary="No tasks.",
    )
    with patch("app.agents.task_agent.create_planner_tasks") as mock_planner:
        from app.agents.task_agent import assign_tasks

        result = await assign_tasks(m)

    mock_planner.assert_not_called()
    assert result.action_items == []
