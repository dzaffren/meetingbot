from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

CREATE_PLANNER_TASK_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "create_planner_task",
        "description": (
            "Create a Microsoft Planner task for a meeting action item. "
            "Assigns the task to the Person In Charge (PIC) by resolving their display name "
            "to an Azure AD user ID."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Short task title.",
                },
                "description": {
                    "type": "string",
                    "description": "Detailed description of what needs to be done.",
                },
                "pic": {
                    "type": "string",
                    "description": "Full display name of the Person In Charge.",
                },
                "due_date": {
                    "type": "string",
                    "description": "Due date in YYYY-MM-DD format, or null if not specified.",
                    "nullable": True,
                },
            },
            "required": ["title", "pic"],
        },
    },
}


async def execute_create_planner_task_tool(arguments: dict[str, Any]) -> str:
    """
    Execute the create_planner_task tool call.

    Args:
        arguments: Parsed JSON arguments from the model's tool call.

    Returns:
        A string confirming task creation with the Planner task ID.
    """
    # TODO: Implement by calling app.integrations.planner.create_planner_tasks().
    #
    # Example:
    #   from app.models.minutes import ActionItem
    #   from datetime import date
    #   from app.integrations.planner import create_planner_tasks
    #   item = ActionItem(
    #       title=arguments["title"],
    #       description=arguments.get("description", ""),
    #       pic=arguments["pic"],
    #       due_date=date.fromisoformat(arguments["due_date"]) if arguments.get("due_date") else None,
    #   )
    #   [updated] = await create_planner_tasks([item])
    #   return f"Created Planner task '{updated.title}' (ID: {updated.planner_task_id}) assigned to {updated.pic}"
    raise NotImplementedError("TODO: implement execute_create_planner_task_tool()")
