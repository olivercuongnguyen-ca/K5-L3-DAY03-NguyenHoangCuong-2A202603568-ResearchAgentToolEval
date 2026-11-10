"""Streamlit chat UI for the research agent.

Run:  streamlit run app.py
Reuses the same agent loop as chat.py (run_model_tool_loop), so behaviour matches the eval.
Every conversation is saved to transcripts/ in the same format as chat.py (evidence for REPORT B4).
"""
from __future__ import annotations

import contextlib
import io
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)

PROVIDERS = ["deepseek", "openrouter", "openai", "anthropic", "gemini", "ollama"]
SAMPLES = [
    ("Bitcoin news today", "Tin tức Bitcoin hôm nay có gì?"),
    ("3 latest posts by Bill Gates", "Lấy 3 tweet mới nhất của Bill Gates"),
    ("What people say about VinFast", "Mọi người nói gì về VinFast trên Twitter?"),
    ("Cite a paper in APA", "Trích dẫn giúp mình bài này theo APA: https://arxiv.org/abs/1706.03762"),
]

st.set_page_config(page_title="Research Agent", page_icon=":material/travel_explore:", layout="centered")

# ---- Design tokens: AI-Native UI (purple primary, cyan accent, Inter), from ui-ux-pro-max ----
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
:root {
  --primary: #7C3AED; --on-primary: #FFFFFF; --accent: #0E7490;
  --bg: #FAF5FF; --card: #FFFFFF; --fg: #1E1B4B; --muted: #ECEEF9; --muted-fg: #475569; --border: #DDD6FE;
}
html, body, [class*="css"], .stApp { font-family: 'Inter', system-ui, sans-serif; color: var(--fg); }
.stApp { background: var(--bg); }
.block-container { padding-top: 2rem; max-width: 760px; }
h1 { font-weight: 700; letter-spacing: -0.02em; margin-bottom: 0.25rem; }
.subtitle { color: var(--muted-fg); font-size: 1rem; line-height: 1.5; margin-bottom: 1.25rem; }
[data-testid="stChatMessage"] {
  background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 0.9rem 1rem;
}
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li { line-height: 1.6; }
.stButton > button, .stDownloadButton > button {
  border-radius: 10px; border: 1px solid var(--border); background: var(--card); color: var(--fg);
  min-height: 44px; cursor: pointer; transition: background 160ms ease, border-color 160ms ease;
}
.stButton > button:hover, .stDownloadButton > button:hover { border-color: var(--primary); background: #F5F3FF; }
button:focus-visible, textarea:focus-visible, input:focus-visible { outline: 3px solid var(--primary) !important; outline-offset: 2px; }
.chip { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 0.8rem; font-weight: 600;
        background: #EDE9FE; color: #5B21B6; margin-right: 6px; }
.chip.wait { background: #CFFAFE; color: #155E75; }
.meta { color: var(--muted-fg); font-size: 0.85rem; }
[data-testid="stSidebar"] { background: var(--card); border-right: 1px solid var(--border); }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }
</style>
""",
    unsafe_allow_html=True,
)


# ---- Helpers ----
def summarize_result(result: Any) -> str:
    if not isinstance(result, dict):
        return str(result)[:200]
    if "error" in result:
        return f"error: {result.get('error')} {result.get('message', '')}".strip()
    if result.get("awaiting_user"):
        return f"asked user ({result.get('response_type')}): {result.get('question')}"
    if isinstance(result.get("items"), list):
        titles = [str(i.get("title", ""))[:70] for i in result["items"][:3] if isinstance(i, dict)]
        return f"{len(result['items'])} items" + (": " + " | ".join(titles) if titles else "")
    if "markdown" in result:
        return f"markdown digest, {result.get('item_count', '?')} items"
    return ", ".join(result.keys())


def render_trace(tool_events: list[dict[str, Any]]) -> None:
    if not tool_events:
        return
    with st.expander(f"Tool trace ({len(tool_events)})", icon=":material/construction:"):
        for event in tool_events:
            st.markdown(f"**{event.get('tool')}**")
            st.code(json.dumps(event.get("args", {}), ensure_ascii=False, indent=2), language="json")
            st.caption(summarize_result(event.get("result")))


def init_state() -> None:
    ss = st.session_state
    ss.setdefault("view", [])  # what the page shows
    ss.setdefault("history", [])  # what the model sees (user/assistant text only)
    ss.setdefault("turn_index", 0)
    ss.setdefault("transcript", None)
    ss.setdefault("transcript_path", None)


def new_transcript(provider_name: str, model: str | None, version: str, system_path: Path, tools_path: Path) -> None:
    artifact = build_artifact_version(version, system_path, tools_path)
    transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), datetime.now().strftime("%Y%m%dT%H%M%S%f")])
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(system_path),
        "tools": str(tools_path),
        "history_window": 5,
        "max_tool_rounds": 4,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
        "source": "app.py (Streamlit UI)",
    }


init_state()
system_path = ARTIFACTS_DIR / "system_prompt.md"
tools_path = ARTIFACTS_DIR / "tools.yaml"
declarations = load_tool_declarations(tools_path)

# ---- Sidebar ----
with st.sidebar:
    st.header("Settings")
    provider_name = st.selectbox("Model provider", PROVIDERS, index=0)
    version = st.text_input("Version label", value="v3", help="Stored in the transcript, e.g. v3")
    st.markdown("**Tools the agent can use**")
    st.markdown(" ".join(f"<span class='chip'>{d['name']}</span>" for d in declarations), unsafe_allow_html=True)
    st.divider()
    if st.button("New chat", icon=":material/add_comment:", use_container_width=True):
        for key in ("view", "history", "turn_index", "transcript", "transcript_path"):
            st.session_state.pop(key, None)
        st.rerun()
    if st.session_state.transcript:
        st.download_button(
            "Download transcript",
            data=json.dumps(st.session_state.transcript, ensure_ascii=False, indent=2, default=str),
            file_name=Path(st.session_state.transcript_path).name,
            mime="application/json",
            icon=":material/download:",
            use_container_width=True,
        )
        st.caption(f"Saved to transcripts/{Path(st.session_state.transcript_path).name}")

# ---- Header ----
st.title("Research Agent")
st.markdown(
    "<p class='subtitle'>Ask for web news, posts from a person, what people say about a topic, "
    "or a citation. The agent picks a tool, runs it, and shows you exactly what it did.</p>",
    unsafe_allow_html=True,
)

# ---- Empty state: sample prompts ----
if not st.session_state.view:
    st.markdown("**Try one of these**")
    cols = st.columns(2)
    for i, (label, text) in enumerate(SAMPLES):
        if cols[i % 2].button(label, key=f"sample_{i}", help=text, use_container_width=True):
            st.session_state.queued = text
            st.rerun()

# ---- Conversation ----
for message in st.session_state.view:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            if message.get("waiting"):
                st.markdown("<span class='chip wait'>Waiting for your answer</span>", unsafe_allow_html=True)
            render_trace(message.get("tool_events", []))

# Quick replies when the agent asked a clarifying question
last = st.session_state.view[-1] if st.session_state.view else None
if last and last.get("waiting"):
    reply_type = last.get("response_type")
    quick: list[str] = []
    if reply_type == "yes_no":
        quick = ["Yes", "No"]
    elif reply_type == "choice":
        quick = last.get("options", [])
    if quick:
        cols = st.columns(len(quick))
        for i, option in enumerate(quick):
            if cols[i].button(option, key=f"quick_{len(st.session_state.view)}_{i}", use_container_width=True):
                st.session_state.queued = option
                st.rerun()

# ---- Input ----
queued = st.session_state.pop("queued", None)
user_text = st.chat_input("Ask the research agent...") or queued

if user_text:
    if st.session_state.transcript is None:
        provider_for_name = make_provider(provider_name)
        new_transcript(provider_name, getattr(provider_for_name, "default_model", None), version, system_path, tools_path)

    with st.chat_message("user"):
        st.markdown(user_text)

    system_prompt = system_path.read_text(encoding="utf-8")
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, 5),
        {"role": "user", "content": user_text},
    ]
    st.session_state.turn_index += 1
    turn: dict[str, Any] = {
        "turn_index": st.session_state.turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    assistant_view: dict[str, Any] = {"role": "assistant", "content": "", "tool_events": []}
    with st.chat_message("assistant"):
        with st.spinner("Thinking and calling tools..."):
            try:
                # chat.py prints tool calls with an emoji; swallow stdout so Windows consoles cannot crash on it.
                with contextlib.redirect_stdout(io.StringIO()):
                    result = run_model_tool_loop(
                        provider=make_provider(provider_name),
                        messages=messages,
                        tools=to_openai_tools(declarations),
                        model=None,
                        max_tool_rounds=4,
                    )
                turn.update(result)
                assistant_view["content"] = result["assistant_text"]
                assistant_view["tool_events"] = result["tool_events"]
                if result["status"] == "waiting_for_user":
                    assistant_view["waiting"] = True
                    for event in reversed(result["tool_events"]):
                        res = event.get("result", {})
                        if isinstance(res, dict) and res.get("awaiting_user"):
                            assistant_view["response_type"] = res.get("response_type")
                            assistant_view["options"] = res.get("options", [])
                            break
                st.session_state.history.append({"role": "user", "content": user_text})
                st.session_state.history.append({"role": "assistant", "content": result["assistant_text"]})
            except Exception as exc:  # show a recoverable error instead of a stack trace
                turn.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})
                assistant_view["content"] = (
                    f"Something went wrong: `{type(exc).__name__}: {exc}`. "
                    "Check your API key in `.env`, then send the message again."
                )

    turn["ended_at"] = now_iso()
    st.session_state.transcript["turns"].append(turn)
    write_transcript(Path(st.session_state.transcript_path), st.session_state.transcript)
    st.session_state.view.append({"role": "user", "content": user_text})
    st.session_state.view.append(assistant_view)
    st.rerun()
