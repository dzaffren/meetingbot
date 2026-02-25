from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

WEB_SEARCH_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": (
            "Search the web using Bing Search for current or external information not "
            "available in internal documents. Use when internal search yields insufficient results."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The web search query.",
                },
                "top_n": {
                    "type": "integer",
                    "description": "Number of results to return. Default 5.",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
}


async def execute_web_search_tool(arguments: dict[str, Any]) -> str:
    """
    Execute the web_search tool call.

    Args:
        arguments: Parsed JSON arguments from the model's tool call.

    Returns:
        A formatted string of web search results.
    """
    # TODO: Implement by calling app.rag.web_search.web_search().
    #
    # Example:
    #   from app.rag.web_search import web_search
    #   results = await web_search(query=arguments["query"], top_n=arguments.get("top_n", 5))
    #   return "\n\n".join(f"[Web: {r['url']}]\n{r['title']}: {r['snippet']}" for r in results)
    raise NotImplementedError("TODO: implement execute_web_search_tool()")
