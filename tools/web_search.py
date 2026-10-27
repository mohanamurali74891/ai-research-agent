"""
tools/web_search.py
────────────────────────────────────────────────
Tool: Web Search via DuckDuckGo + Wikipedia Fallback
Part of: AI Research Agent - Module 5
"""

import warnings
import re
from typing import List, Dict

# Suppress ddgs rename warning
warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

try:
    import requests
except ImportError:
    requests = None


def web_search(query: str, max_results: int = 5) -> List[Dict]:
    """
    Search the web using DuckDuckGo, with Wikipedia search API as reliable fallback.

    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5)

    Returns:
        List of dicts with 'title', 'href', 'body' keys
    """
    results = []

    # 1. Try DuckDuckGo
    if DDGS:
        try:
            with DDGS() as ddgs:
                raw = list(ddgs.text(query, max_results=max_results))
                if raw:
                    for r in raw:
                        if r.get("title") and r.get("body"):
                            results.append({
                                "title": r.get("title", ""),
                                "href": r.get("href", ""),
                                "body": r.get("body", ""),
                            })
        except Exception:
            pass

    # 2. If DDGS returned nothing, fall back to Wikipedia search API
    if not results and requests:
        try:
            url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": max_results,
                "format": "json"
            }
            resp = requests.get(
                url,
                params=params,
                headers={"User-Agent": "AIResearchAgent/1.0 (educational-agent)"},
                timeout=5
            ).json()

            search_hits = resp.get("query", {}).get("search", [])
            for hit in search_hits:
                snippet = hit.get("snippet", "")
                # Clean html tags from snippet
                clean_snippet = re.sub(r"<[^>]+>", "", snippet)
                title = hit.get("title", "")
                page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                results.append({
                    "title": f"Wikipedia: {title}",
                    "href": page_url,
                    "body": clean_snippet,
                })
        except Exception:
            pass

    if not results:
        results.append({
            "title": f"Search Results for '{query}'",
            "href": "",
            "body": f"No direct search results found for '{query}'. Please use get_wikipedia_summary for specific topics.",
        })

    return results


def format_search_results(results: List[Dict]) -> str:
    """Format search results into readable text for the LLM."""
    if not results:
        return "No results found."

    formatted = []
    for i, r in enumerate(results, 1):
        formatted.append(
            f"[{i}] **{r.get('title', 'No title')}**\n"
            f"URL: {r.get('href', 'N/A')}\n"
            f"Summary: {r.get('body', 'No description')}\n"
        )
    return "\n".join(formatted)
