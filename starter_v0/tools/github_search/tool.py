from __future__ import annotations

from typing import Any
import requests

from tools._shared import TIMEOUT, err


def search_github_repos(
    query: str = "",
    language: str = "",
    sort: str = "stars",
    limit: int = 5,
) -> dict[str, Any]:
    """Search repositories on GitHub."""
    try:
        clean_query = (query or "").strip()
        if not clean_query:
            return {"tool": "github_search", "error": "ValueError", "message": "Query cannot be empty"}

        q = clean_query
        if language and language.strip():
            q += f" language:{language.strip()}"

        clean_limit = max(1, min(int(limit) if str(limit).isdigit() else 5, 20))
        url = "https://api.github.com/search/repositories"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ResearchAgent-Lab/1.0",
        }
        params = {
            "q": q,
            "sort": sort or "stars",
            "order": "desc",
            "per_page": clean_limit,
        }

        response = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()

        items = []
        for repo in (data.get("items") or [])[:clean_limit]:
            items.append({
                "name": repo.get("full_name", ""),
                "url": repo.get("html_url", ""),
                "description": repo.get("description") or "",
                "stars": repo.get("stargazers_count", 0),
                "language": repo.get("language") or "",
            })

        return {
            "tool": "github_search",
            "query": clean_query,
            "total_count": data.get("total_count", 0),
            "items": items,
        }
    except Exception as exc:
        return err("github_search", exc)

