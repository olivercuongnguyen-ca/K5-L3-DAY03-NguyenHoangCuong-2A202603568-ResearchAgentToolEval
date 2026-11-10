from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err


SEMANTIC_SCHOLAR_API_URL = (
    "https://api.semanticscholar.org/graph/v1/paper/search"
)

PAPER_FIELDS = ",".join([
    "title",
    "authors",
    "year",
    "abstract",
    "citationCount",
    "url",
    "externalIds",
])


def semantic_scholar_search(
    query: str = "",
    max_results: int = 5,
) -> dict[str, Any]:
    """Search academic papers through Semantic Scholar."""
    try:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")

        max_results = max(1, min(int(max_results or 5), 10))

        params = {
            "query": query.strip(),
            "limit": max_results,
            "fields": PAPER_FIELDS,
        }

        response = requests.get(
            SEMANTIC_SCHOLAR_API_URL,
            params=params,
            timeout=TIMEOUT,
        )
        response.raise_for_status()

        payload = response.json()
        raw_items = payload.get("data", [])

        if not isinstance(raw_items, list):
            raise ValueError("Invalid Semantic Scholar response: data must be a list")

        items: list[dict[str, Any]] = []

        for paper in raw_items:
            if not isinstance(paper, dict):
                continue

            external_ids = paper.get("externalIds") or {}
            authors = paper.get("authors") or []

            arxiv_id = external_ids.get("ArXiv")

            items.append({
                "paper_id": paper.get("paperId"),
                "title": paper.get("title") or "",
                "authors": [
                    author.get("name", "")
                    for author in authors
                    if isinstance(author, dict)
                ],
                "year": paper.get("year"),
                "abstract": paper.get("abstract") or "",
                "citation_count": paper.get("citationCount") or 0,
                "url": paper.get("url") or "",
                "arxiv_id": arxiv_id,
                "source": "semanticscholar.org",
            })

        return {
            "tool": "semantic_scholar_search",
            "query": query.strip(),
            "total_results": payload.get("total"),
            "items": items,
        }

    except Exception as exc:
        return err("semantic_scholar_search", exc)