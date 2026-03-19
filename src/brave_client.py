"""Brave Search API client for atl-context-scout.

Provides three focused query functions that return structured result
lists for news, weather, and local events in a given city.
"""

from __future__ import annotations

import requests
from typing import Any

BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"
_HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip",
}


def _search(api_key: str, query: str, count: int = 5) -> list[dict[str, Any]]:
    """Run a raw Brave web search and return a list of result dicts."""
    headers = {**_HEADERS, "X-Subscription-Token": api_key}
    resp = requests.get(
        BRAVE_SEARCH_URL,
        headers=headers,
        params={"q": query, "count": count, "result_filter": "web"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("web", {}).get("results", [])


def _extract(results: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Normalize raw Brave results to {title, url, description}."""
    out = []
    for r in results:
        out.append(
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "description": r.get("description", "")[:280],
            }
        )
    return out


def search_news(api_key: str, location: str, count: int = 5) -> list[dict[str, str]]:
    """Return top news headlines for *location*."""
    query = f"{location} news today"
    return _extract(_search(api_key, query, count))


def search_weather(api_key: str, location: str) -> list[dict[str, str]]:
    """Return current weather and forecast results for *location*."""
    query = f"{location} weather forecast today"
    return _extract(_search(api_key, query, 3))


def search_events(api_key: str, location: str, count: int = 5) -> list[dict[str, str]]:
    """Return upcoming events and things-to-do for *location*."""
    query = f"{location} events this week things to do"
    return _extract(_search(api_key, query, count))
