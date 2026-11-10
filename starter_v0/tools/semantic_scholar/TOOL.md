
---
name: semantic_scholar
track: bonus
kind: live_api
provider: Semantic Scholar Academic Graph API
requires_env: []
---
# Semantic Scholar Search

## Purpose

Search academic papers using the Semantic Scholar Academic Graph API.

Use this tool when users request scientific papers, research publications,
or literature discovery beyond arXiv.

## Input

- `query`: Research topic, keywords, or scientific question.
- `max_results`: Maximum number of papers to return (1-10, default 5).

## Output

Returns a dictionary containing:

- `tool`: Tool identifier.
- `query`: Search query.
- `total_results`: Total matching papers reported by the API.
- `items`: List of academic papers.

Each paper contains:

- `paper_id`
- `title`
- `authors`
- `year`
- `abstract`
- `citation_count`
- `url`
- `arxiv_id`
- `source`

## Usage guidance

- Use concise, topic-focused research queries.
- Use `papers` when the user specifically needs arXiv search options.
- Use `paper_text` to retrieve the content of a specific arXiv paper.
- Use this tool to discover papers indexed by Semantic Scholar.
- Do not treat citation count as a direct measure of paper quality.

## Limitations

The API may enforce rate limits. HTTP errors and invalid responses are
returned as error dictionaries.