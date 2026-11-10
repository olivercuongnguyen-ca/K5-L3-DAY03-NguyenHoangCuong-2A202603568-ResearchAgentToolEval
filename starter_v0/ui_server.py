"""Local web UI for the Research Agent chat (stdlib only).

Usage: python ui_server.py --provider tokenharbor --version v0 [--port 8000]
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from chat import (ARTIFACTS_DIR, ROOT, now_iso, run_model_tool_loop, safe_slug,
                  trim_history, write_transcript)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

UI_DIR = ROOT / "ui"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini", "ollama", "tokenharbor"], required=True)
    p.add_argument("--model", default=None)
    p.add_argument("--version", default="ui")
    p.add_argument("--system-prompt", type=Path, default=ARTIFACTS_DIR / "system_prompt.md")
    p.add_argument("--tools", type=Path, default=ARTIFACTS_DIR / "tools.yaml")
    p.add_argument("--transcripts-dir", type=Path, default=ROOT / "transcripts")
    p.add_argument("--history-window", type=int, default=5)
    p.add_argument("--max-tool-rounds", type=int, default=4)
    p.add_argument("--port", type=int, default=8000)
    args = p.parse_args()

    system_prompt = args.system_prompt.read_text(encoding="utf-8")
    tools = to_openai_tools(load_tool_declarations(args.tools))
    provider = make_provider(args.provider)
    model = args.model or getattr(provider, "default_model", None)
    av = build_artifact_version(args.version, args.system_prompt, args.tools)

    state: dict = {"history": [], "transcript": None, "path": None}

    def new_session() -> None:
        tid = "_".join([safe_slug(args.version), safe_slug(args.provider),
                        datetime.now().strftime("%Y%m%dT%H%M%S%f")])
        state["history"] = []
        state["path"] = args.transcripts_dir / f"{tid}.transcript.json"
        state["transcript"] = {
            "transcript_id": tid, **artifact_version_dict(av), "provider": args.provider,
            "model": model, "created_at": now_iso(), "updated_at": now_iso(), "turns": [],
        }

    new_session()

    class Handler(BaseHTTPRequestHandler):
        def _json(self, code: int, obj: dict) -> None:
            body = json.dumps(obj, ensure_ascii=False, default=str).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/api/info":
                return self._json(200, {"provider": args.provider, "model": model,
                                        "version": av.artifact_version})
            if self.path in ("/", "/index.html"):
                body = (UI_DIR / "index.html").read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_error(404)

        def do_POST(self):
            try:
                self._post()
            except Exception as exc:
                import traceback; traceback.print_exc()
                try:
                    self._json(500, {"status": "error", "text": f"{type(exc).__name__}: {exc}", "tools": []})
                except Exception:
                    pass

        def do_OPTIONS(self):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.end_headers()

        def _post(self):
            n = int(self.headers.get("Content-Length") or 0)
            data = json.loads(self.rfile.read(n) or b"{}")
            if self.path == "/api/reset":
                new_session()
                return self._json(200, {"ok": True})
            if self.path != "/api/chat":
                return self.send_error(404)
            text = (data.get("message") or "").strip()
            if not text:
                return self._json(400, {"error": "empty message"})
            messages = [{"role": "system", "content": system_prompt},
                        *trim_history(state["history"], args.history_window),
                        {"role": "user", "content": text}]
            turn = {"turn_index": len(state["transcript"]["turns"]) + 1,
                    "started_at": now_iso(), "user": text}
            try:
                result = run_model_tool_loop(provider=provider, messages=messages, tools=tools,
                                             model=args.model, max_tool_rounds=args.max_tool_rounds)
                turn.update(result)
                state["history"] += [{"role": "user", "content": text},
                                     {"role": "assistant", "content": result["assistant_text"]}]
                out = {"status": result["status"], "text": result["assistant_text"],
                       "tools": [{"name": e["tool"], "args": e["args"], "result": e["result"]}
                                 for e in result["tool_events"]]}
            except Exception as exc:
                turn.update(status="provider_error", error=f"{type(exc).__name__}: {exc}")
                out = {"status": "error", "text": turn["error"], "tools": []}
            turn["ended_at"] = now_iso()
            state["transcript"]["turns"].append(turn)
            write_transcript(state["path"], state["transcript"])
            self._json(200, out)

        def log_message(self, *a):
            pass

    print(f"Research Agent UI: http://127.0.0.1:{args.port}  (provider={args.provider}, model={model})")
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
