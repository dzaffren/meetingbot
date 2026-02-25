from __future__ import annotations

import logging

from app.agents.base import (
    MULTILINGUAL_SYSTEM_PREAMBLE,
    create_or_get_agent,
    run_agent_thread,
)
from app.agents.tools.planner_tool import CREATE_PLANNER_TASK_TOOL
from app.models.minutes import ActionItem, MeetingMinutes
from app.storage.cosmos_client import CONTAINER_TASKS, get_cosmos_store

logger = logging.getLogger(__name__)

_AGENT_NAME = "meetingbot-task-agent"

_INSTRUCTIONS = f"""{MULTILINGUAL_SYSTEM_PREAMBLE}

Your task: create Microsoft Planner tasks for every action item extracted from meeting minutes.

For each action item you receive:
1. Call create_planner_task with the title, description, PIC, and due_date.
2. Confirm each task was created successfully.

Always assign tasks to the Person In Charge (PIC) named in the action item.
If a due date is not specified, omit it from the tool call.
"""


async def assign_tasks(minutes: MeetingMinutes) -> MeetingMinutes:
    """
    Create Microsoft Planner tasks for each ActionItem in MeetingMinutes using an AI Foundry agent.

    The agent calls create_planner_task() for each item autonomously.
    The minutes object is updated in-place with planner_task_id values.

    Args:
        minutes: A MeetingMinutes instance with action_items populated.

    Returns:
        The updated MeetingMinutes with planner_task_id fields populated.
    """
    # TODO: Implement task assignment using the AI Foundry agent.
    #
    # Pattern:
    #   1. If no action items, return early
    #   2. Build a user message listing all action items as JSON
    #   3. Get or create the task agent via create_or_get_agent()
    #   4. Call run_agent_thread() — agent calls create_planner_task() for each item
    #   5. Parse tool call results to populate planner_task_id on each ActionItem
    #   6. Persist each task record to Cosmos DB (CONTAINER_TASKS)
    #   7. Return updated minutes
    #
    # Alternatively, bypass the agent and call create_planner_tasks() from integrations directly
    # for a simpler implementation before full agentic loop is ready.
    raise NotImplementedError("TODO: implement task_agent.assign_tasks()")

