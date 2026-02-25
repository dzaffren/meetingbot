from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tool schema definitions for Azure AI Foundry Agent SDK.
# Pass these dicts to client.agents.create_agent(tools=[...]).
# Each entry follows the OpenAI function-calling tool schema.
# ---------------------------------------------------------------------------

SEARCH_MEETING_DOCS_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "search_meeting_docs",
        "description": (
            "Search documents uploaded for the current meeting session using hybrid "
            "keyword + vector search. Use this to answer questions grounded in pre-meeting "
            "materials such as agendas, reports, or presentations."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query.",
                },
                "meeting_id": {
                    "type": "string",
                    "description": "The meeting session ID to scope the search.",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of results to return. Default 5.",
                    "default": 5,
                },
            },
            "required": ["query", "meeting_id"],
        },
    },
}

SEARCH_ORG_KB_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "search_org_kb",
        "description": (
            "Search the organisation's general knowledge base using hybrid search. "
            "Use this for questions about company policies, org structure, HR information, "
            "or any persistent organisational knowledge."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query.",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of results to return. Default 5.",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
}


# ---------------------------------------------------------------------------
# Tool call executor — called by the agent runner when the model invokes a tool
# ---------------------------------------------------------------------------

async def execute_search_tool(tool_name: str, arguments: dict[str, Any]) -> str:
    """
    Execute a search tool call dispatched by the AI Foundry agent runner.

    Args:
        tool_name: "search_meeting_docs" or "search_org_kb"
        arguments: Parsed JSON arguments from the model's tool call.

    Returns:
        A formatted string of search results to feed back to the model.
    """
    # TODO: Implement tool execution by calling app.rag.retriever.hybrid_search().
    #
    # Example:
    #   from app.rag.retriever import hybrid_search
    #   if tool_name == "search_meeting_docs":
    #       results = await hybrid_search(
    #           query=arguments["query"],
    #           meeting_id=arguments["meeting_id"],
    #           doc_type="meeting",
    #           top_k=arguments.get("top_k", 5),
    #       )
    #   elif tool_name == "search_org_kb":
    #       results = await hybrid_search(
    #           query=arguments["query"],
    #           doc_type="org",
    #           top_k=arguments.get("top_k", 5),
    #       )
    #   return "\n\n".join(f"[Source: {r['source']}]\n{r['content']}" for r in results)
    raise NotImplementedError(f"TODO: implement execute_search_tool for '{tool_name}'")
