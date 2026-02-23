from __future__ import annotations

import logging

from kiota_abstractions.base_request_configuration import RequestConfiguration
from msgraph.generated.models.planner_assignments import PlannerAssignments
from msgraph.generated.models.planner_task import PlannerTask

from app.config import get_settings
from app.integrations.graph_client import get_graph_client
from app.models.minutes import ActionItem

logger = logging.getLogger(__name__)


async def _resolve_user_id(graph, display_name: str) -> str | None:
    """Resolve a participant display name to an AAD user ID."""
    try:
        result = await graph.users.get(
            request_configuration=RequestConfiguration(
                query_parameters={
                    "$filter": f"displayName eq '{display_name}'",
                    "$select": "id,displayName",
                }
            )
        )
        if result and result.value:
            return result.value[0].id
    except Exception as exc:
        logger.warning("Could not resolve user '%s': %s", display_name, exc)
    return None


async def create_planner_tasks(action_items: list[ActionItem]) -> list[ActionItem]:
    """
    Create Microsoft Planner tasks for each ActionItem.
    Resolves PIC display names to AAD user IDs and assigns tasks.
    Returns the same list with planner_task_id populated where successful.
    """
    settings = get_settings()
    graph = get_graph_client()

    for item in action_items:
        try:
            user_id = await _resolve_user_id(graph, item.pic)

            task = PlannerTask()
            task.plan_id = settings.planner_plan_id
            task.title = item.title
            if item.due_date:
                task.due_date_time = f"{item.due_date.isoformat()}T23:59:00Z"

            if user_id:
                assignments = PlannerAssignments()
                # Graph API: assignments is a dict keyed by AAD user ID
                assignments.additional_data = {
                    user_id: {
                        "@odata.type": "#microsoft.graph.plannerAssignment",
                        "orderHint": " !",
                    }
                }
                task.assignments = assignments

            created = await graph.planner.tasks.post(task)
            item.planner_task_id = created.id
            logger.info("Created Planner task '%s' (id=%s)", item.title, created.id)

        except Exception as exc:
            logger.error("Failed to create Planner task for '%s': %s", item.title, exc)

    return action_items
