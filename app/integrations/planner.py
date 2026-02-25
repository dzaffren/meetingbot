from __future__ import annotations

import logging

from app.config import get_settings
from app.integrations.graph_client import get_graph_client
from app.models.minutes import ActionItem

logger = logging.getLogger(__name__)


async def _resolve_user_id(graph, display_name: str) -> str | None:
    """
    Resolve a participant display name to an Azure AD user ID via Microsoft Graph.

    Args:
        graph: An authenticated GraphServiceClient instance.
        display_name: The participant's display name as it appears in the meeting.

    Returns:
        AAD object ID string if found, None otherwise.
    """
    # TODO: Implement AAD user ID resolution.
    #
    # Pattern:
    #   from kiota_abstractions.base_request_configuration import RequestConfiguration
    #   result = await graph.users.get(
    #       request_configuration=RequestConfiguration(
    #           query_parameters={"$filter": f"displayName eq '{display_name}'", "$select": "id,displayName"}
    #       )
    #   )
    #   if result and result.value:
    #       return result.value[0].id
    #   return None
    raise NotImplementedError("TODO: implement _resolve_user_id()")


async def create_planner_tasks(action_items: list[ActionItem]) -> list[ActionItem]:
    """
    Create Microsoft Planner tasks for a list of ActionItems.

    For each item:
    1. Resolve the PIC display name to an AAD user ID.
    2. Create a Planner task in the configured plan with due date and assignment.
    3. Populate item.planner_task_id with the created task ID.

    Args:
        action_items: List of ActionItem objects with title, description, pic, due_date.

    Returns:
        The same list with planner_task_id populated where task creation succeeded.
    """
    # TODO: Implement Planner task creation via Microsoft Graph.
    #
    # Pattern:
    #   settings = get_settings()
    #   graph = get_graph_client()
    #   for item in action_items:
    #       user_id = await _resolve_user_id(graph, item.pic)
    #       task = PlannerTask()
    #       task.plan_id = settings.planner_plan_id
    #       task.title = item.title
    #       if item.due_date: task.due_date_time = f"{item.due_date.isoformat()}T23:59:00Z"
    #       if user_id:
    #           assignments = PlannerAssignments()
    #           assignments.additional_data = {user_id: {"@odata.type": "#microsoft.graph.plannerAssignment", "orderHint": " !"}}
    #           task.assignments = assignments
    #       created = await graph.planner.tasks.post(task)
    #       item.planner_task_id = created.id
    #   return action_items
    raise NotImplementedError("TODO: implement create_planner_tasks()")
