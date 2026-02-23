from __future__ import annotations

import logging

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


async def web_search(query: str, top_n: int | None = None) -> list[dict[str, str]]:
    """
    Search the web using Bing Search API and return top-N result snippets.

    Returns a list of dicts with keys: title, snippet, url.
    """
    settings = get_settings()
    n = top_n or settings.search_top_k

    headers = {"Ocp-Apim-Subscription-Key": settings.bing_search_api_key}
    params = {"q": query, "count": n, "mkt": "en-MY", "safeSearch": "Moderate"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            settings.bing_search_endpoint,
            headers=headers,
            params=params,
        )
        response.raise_for_status()
        data = response.json()

    results = []
    for item in data.get("webPages", {}).get("value", [])[:n]:
        results.append(
            {
                "title": item.get("name", ""),
                "snippet": item.get("snippet", ""),
                "url": item.get("url", ""),
            }
        )

    logger.info("Bing search '%s' → %d results", query, len(results))
    return results
