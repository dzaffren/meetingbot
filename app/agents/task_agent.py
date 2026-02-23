from __future__ import annotations

import logging

from app.integrations.planner import create_planner_tasks
from app.models.minutes import ActionItem, MeetingMinutes
from app.storage.cosmos_client import CONTAINER_TASKS, get_cosmos_store

logger = logging.getLogger(__name__)


async def assign_tasks(minutes: MeetingMinutes) -> MeetingMinutes:
    """
    For each ActionItem in MeetingMinutes:
      1. Create a Microsoft Planner task (with PIC assignment).
      2. Persist the task record to Cosmos DB.

    The minutes object is updated in-place with planner_task_id values.
    Returns the updated MeetingMinutes.
    """
    if not minutes.action_items:
        logger.info("No action items to assign for meeting %s", minutes.meeting_id)
        return minutes

    # Create Planner tasks and populate planner_task_id
    updated_items = await create_planner_tasks(minutes.action_items)
    minutes.action_items = updated_items

    # Persist each task to Cosmos DB
    store = get_cosmos_store()
    for item in minutes.action_items:
        doc = {
            "id": item.planner_task_id or f"{minutes.meeting_id}-{item.title[:40]}",
            "meeting_id": minutes.meeting_id,
            "title": item.title,
            "description": item.description,
            "pic": item.pic,
            "due_date": item.due_date.isoformat() if item.due_date else None,
            "planner_task_id": item.planner_task_id,
        }
        await store.upsert(CONTAINER_TASKS, doc)

    logger.info(
        "Assigned %d tasks for meeting %s", len(minutes.action_items), minutes.meeting_id
    )
    return minutes
