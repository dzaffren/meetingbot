from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

GET_MEETING_INFO_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "get_meeting_info",
        "description": (
            "Retrieve Microsoft Teams online meeting metadata (subject, organiser, "
            "scheduled time, join URL) via Microsoft Graph API."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "meeting_id": {
                    "type": "string",
                    "description": "The Teams online meeting ID (Graph API format).",
                },
            },
            "required": ["meeting_id"],
        },
    },
}

LIST_MEETING_MEMBERS_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "list_meeting_members",
        "description": (
            "List the members (attendees) of a Teams channel or chat associated with "
            "the meeting, including their display names and AAD user IDs."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "chat_id": {
                    "type": "string",
                    "description": "The Teams chat or channel ID.",
                },
            },
            "required": ["chat_id"],
        },
    },
}


async def execute_graph_tool(tool_name: str, arguments: dict[str, Any]) -> str:
    """
    Execute a Graph API tool call dispatched by the AI Foundry agent runner.

    Args:
        tool_name: "get_meeting_info" or "list_meeting_members"
        arguments: Parsed JSON arguments from the model's tool call.

    Returns:
        A formatted string with the retrieved data.
    """
    # TODO: Implement using app.integrations.graph_client.get_graph_client().
    #
    # get_meeting_info example:
    #   from app.integrations.graph_client import get_graph_client
    #   graph = get_graph_client()
    #   meeting = await graph.communications.online_meetings.by_online_meeting_id(meeting_id).get()
    #   return f"Subject: {meeting.subject}, Organiser: {meeting.participants.organizer.upn}"
    #
    # list_meeting_members example:
    #   members = await graph.chats.by_chat_id(chat_id).members.get()
    #   return "\n".join(f"- {m.display_name} ({m.id})" for m in members.value)
    raise NotImplementedError(f"TODO: implement execute_graph_tool for '{tool_name}'")
