"""TODO(student): Tool Unit Test Challenge.

Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
One behaviour per test. Name the test after the behaviour, not the function.
Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS

format_tool = TOOL_FUNCTIONS["format"]
clarify_tool = TOOL_FUNCTIONS["clarify"]
send_tool = TOOL_FUNCTIONS["send"]
lookup_tool = TOOL_FUNCTIONS["lookup"]
fetch_tool = TOOL_FUNCTIONS["fetch"]
timeline_tool = TOOL_FUNCTIONS["timeline"]
social_search_tool = TOOL_FUNCTIONS["social_search"]
policy_tool = TOOL_FUNCTIONS["policy"]
crypto_price_tool = TOOL_FUNCTIONS["crypto_price"]
github_search_tool = TOOL_FUNCTIONS["github_search"]
currency_convert_tool = TOOL_FUNCTIONS["currency_convert"]
semantic_scholar_tool = TOOL_FUNCTIONS["semantic_scholar"]


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    res = clarify_tool(question="Chọn phương án?", response_type="choice", options=["Opt1", "Opt2"])
    assert res["options"] == ["Opt1", "Opt2"]
    assert res["response_type"] == "choice"
    assert res["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "Item 1", "section": "A"},
        {"title": "Item 2", "section": "B"},
        {"title": "Item 3", "section": "A"},
    ]
    result = format_tool(items=items, template="sections")
    assert result["markdown"].count("## A") == 1
    assert result["markdown"].count("## B") == 1


def test_format_thread_numbers_items() -> None:
    items = [{"title": "Bài 1"}, {"title": "Bài 2"}]
    result = format_tool(items=items, template="thread")
    assert "1/ " in result["markdown"]
    assert "2/ " in result["markdown"]


def test_format_empty_items_does_not_crash() -> None:
    res1 = format_tool(items=None)
    assert res1["item_count"] == 0
    res2 = format_tool(items=[])
    assert res2["item_count"] == 0


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake_bot_token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123456")
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Test message", confirmed=True)
    assert len(calls) == 1
    assert "fake_bot_token" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "123456"
    assert calls[0]["json"]["text"] == "Test message"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))
    result = send_tool(text="Test message", confirmed=True)
    assert calls == []
    assert result.get("error") == "RuntimeError"


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test_key")
    calls = fake_http(FakeResponse({"results": []}))

    lookup_tool(query="test query", timeframe=None)
    assert len(calls) == 1
    assert "time_range" not in calls[0]["json"]


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test_fc_key")
    fake_http(FakeResponse({
        "data": {
            "markdown": "Page content markdown",
            "metadata": {"title": "Test Title", "sourceURL": "https://openai.com/blog/test"}
        }
    }))
    result = fetch_tool(url="https://openai.com/blog/test")
    item = result["items"][0]
    assert item["title"] == "Test Title"
    assert item["url"] == "https://openai.com/blog/test"
    assert item["source"] == "openai.com"
    assert item["summary"] == "Page content markdown"


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test_fc_key")
    long_markdown = "A" * 5000
    fake_http(FakeResponse({"data": {"markdown": long_markdown, "metadata": {}}}))
    result = fetch_tool(url="https://example.com")
    assert len(result["items"][0]["summary"]) == 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test_rapid_key")
    timeline_data = {
        "timeline": [
            {"text": "no id item"},
            *[{"tweet_id": f"t_{i}", "screen_name": "sama", "text": f"Tweet {i}"} for i in range(6)]
        ]
    }
    fake_http(FakeResponse(timeline_data))
    result = timeline_tool(screenname="sama", limit=3)
    assert len(result["items"]) == 3
    for item in result["items"]:
        assert item["url"].startswith("https://x.com/sama/status/t_")


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test_rapid_key")
    calls = fake_http(FakeResponse({"tweets": []}))

    social_search_tool(query="AI", search_type="Top")
    assert len(calls) == 1
    assert calls[0]["params"]["query"] == "AI"
    assert calls[0]["params"]["search_type"] == "Top"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    result = policy_tool(query="")
    assert len(result["results"]) == 0


def test_policy_area_filter_only_returns_that_area() -> None:
    result = policy_tool(query="data", policy_area="data_privacy")
    assert len(result["results"]) > 0
    assert all(item["policy_area"] == "data_privacy" for item in result["results"])


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    result = policy_tool(query="probe", policy_area="source_citation", top_k=5)
    untrusted_items = [item for item in result["results"] if item.get("untrusted_text")]
    assert len(untrusted_items) > 0
    item = untrusted_items[0]
    assert any("ignore" in line.lower() for line in item["untrusted_text"])
    assert "ignore" not in item["facts"].lower()


# ---------------- STUDENT BONUS TOOLS (≥ 3 tests per tool) ----------------

# 1. crypto_price
def test_crypto_price_happy_path(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "lastPrice": "95500.5",
        "priceChangePercent": "3.5",
        "highPrice": "96000.0",
        "lowPrice": "94000.0"
    }))
    res = crypto_price_tool(symbol="BTC", currency="USD")
    assert res["status"] == "success"
    assert res["symbol"] == "BTC"
    assert res["price"] == 95500.5
    assert res["change_24h"] == 3.5
    assert "BTCUSDT" in calls[0]["url"]


def test_crypto_price_bad_input_empty_symbol() -> None:
    res = crypto_price_tool(symbol="")
    assert res.get("error") == "ValueError"
    assert "Symbol cannot be empty" in res.get("message", "")


def test_crypto_price_network_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse({}, status_code=500))
    res = crypto_price_tool(symbol="INVALID")
    assert "error" in res


# 2. github_search
def test_github_search_happy_path(fake_http) -> None:
    fake_http(FakeResponse({
        "total_count": 1,
        "items": [{
            "full_name": "google/gemini",
            "html_url": "https://github.com/google/gemini",
            "description": "Official Gemini repository",
            "stargazers_count": 8000,
            "language": "Python"
        }]
    }))
    res = github_search_tool(query="gemini", language="python", sort="stars", limit=5)
    assert res["tool"] == "github_search"
    assert res["total_count"] == 1
    assert len(res["items"]) == 1
    assert res["items"][0]["name"] == "google/gemini"
    assert res["items"][0]["stars"] == 8000


def test_github_search_bad_input_empty_query() -> None:
    res = github_search_tool(query="")
    assert res.get("error") == "ValueError"
    assert "Query cannot be empty" in res.get("message", "")


def test_github_search_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse({}, status_code=403))
    res = github_search_tool(query="agent")
    assert "error" in res


# 3. currency_convert
def test_currency_convert_happy_path() -> None:
    res = currency_convert_tool(amount=100, from_currency="USD", to_currency="VND")
    assert res["status"] == "success"
    assert res["amount"] == 100.0
    assert res["from_currency"] == "USD"
    assert res["to_currency"] == "VND"
    assert res["converted_amount"] > 0


def test_currency_convert_negative_or_unsupported_currency() -> None:
    res1 = currency_convert_tool(amount=-10)
    assert res1.get("error") == "ValueError"
    res2 = currency_convert_tool(amount=100, from_currency="UNKNOWN")
    assert res2.get("error") == "ValueError"


def test_currency_convert_invalid_amount_type() -> None:
    res = currency_convert_tool(amount="abc")
    assert res.get("error") == "ValueError"


# ---------------- SEMANTIC SCHOLAR ----------------

def test_semantic_scholar_happy_path(monkeypatch, fake_http) -> None:
    calls = fake_http(FakeResponse({
        "total": 125,
        "data": [
            {
                "paperId": "paper-123",
                "title": "Attention Is All You Need",
                "authors": [
                    {"name": "Ashish Vaswani"},
                    {"name": "Noam Shazeer"},
                ],
                "year": 2017,
                "abstract": "We propose a new architecture...",
                "citationCount": 100000,
                "url": "https://www.semanticscholar.org/paper/paper-123",
                "externalIds": {"ArXiv": "1706.03762"},
            }
        ],
    }))

    result = semantic_scholar_tool(
        query="transformer architecture",
        max_results=3,
    )

    assert calls[0]["url"] == (
        "https://api.semanticscholar.org/graph/v1/paper/search"
    )
    assert calls[0]["params"]["query"] == "transformer architecture"
    assert calls[0]["params"]["limit"] == 3
    assert "title" in calls[0]["params"]["fields"]
    assert "citationCount" in calls[0]["params"]["fields"]

    assert result["tool"] == "semantic_scholar_search"
    assert result["total_results"] == 125
    assert result["items"][0] == {
        "paper_id": "paper-123",
        "title": "Attention Is All You Need",
        "authors": ["Ashish Vaswani", "Noam Shazeer"],
        "year": 2017,
        "abstract": "We propose a new architecture...",
        "citation_count": 100000,
        "url": "https://www.semanticscholar.org/paper/paper-123",
        "arxiv_id": "1706.03762",
        "source": "semanticscholar.org",
    }


def test_semantic_scholar_rejects_bad_input() -> None:
    result = semantic_scholar_tool(query="   ")

    assert result["error"] == "ValueError"
    assert "query" in result["message"]


def test_semantic_scholar_http_error_returns_error_dict(
    fake_http,
) -> None:
    fake_http(FakeResponse(status_code=429))

    result = semantic_scholar_tool(query="large language models")

    assert result["tool"] == "semantic_scholar_search"
    assert result["error"] == "HTTPError"

