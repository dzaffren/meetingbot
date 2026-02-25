from __future__ import annotations

import logging

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


async def web_search(query: str, top_n: int | None = None) -> list[dict[str, str]]:
    """
    Search the web using Bing Search API and return top-N result snippets.

    Args:
        query: The search query string.
        top_n: Number of results to return. Defaults to settings.search_top_k.

    Returns:
        List of dicts with keys: title, snippet, url.
    """
    # TODO: Implement Bing web search.
    #
    # Pattern:
    #   settings = get_settings()
    #   n = top_n or settings.search_top_k
    #   headers = {"Ocp-Apim-Subscription-Key": settings.bing_search_api_key}
    #   params = {"q": query, "count": n, "mkt": "en-MY", "safeSearch": "Moderate"}
    #   async with httpx.AsyncClient(timeout=10.0) as client:
    #       response = await client.get(settings.bing_search_endpoint, headers=headers, params=params)
    #       response.raise_for_status()
    #       data = response.json()
    #   return [
    #       {"title": item["name"], "snippet": item["snippet"], "url": item["url"]}
    #       for item in data.get("webPages", {}).get("value", [])[:n]
    #   ]
    raise NotImplementedError("TODO: implement web_search()")
