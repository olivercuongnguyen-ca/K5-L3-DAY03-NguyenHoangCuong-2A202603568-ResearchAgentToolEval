# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: 
- Members: Đỗ Minh Hiếu - 2A202603402
- Provider/model: deepseek / deepseek-chat

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent: tìm tin trên web theo từ khóa và khung thời gian, lấy bài đăng của một tài khoản hoặc tìm bài đăng theo chủ đề trên mạng xã hội, đọc nội dung một URL, tạo trích dẫn (APA/Harvard) cho một bài báo, và hỏi lại khi thiếu thông tin hoặc trước khi gửi nội dung đi. Giao diện chat (Streamlit) hiển thị từng tool mà agent đã gọi.

**Link dùng thử (deploy):**

> Buổi demo đã kết thúc nên không dùng link công khai. Chạy local: `streamlit run app.py` rồi mở http://localhost:8501 (code UI: `app.py`).
>
> URL: http://localhost:8501 (chạy local)

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin hoặc cần xác nhận trước khi gửi | không |
| lookup | tìm tin/thông tin trên web (topic=news, timeframe day/week/month/year) | không |
| fetch | đọc nội dung một URL | không |
| timeline | lấy bài đăng gần đây của một tài khoản | không |
| social_search | tìm bài đăng theo chủ đề trên mạng xã hội (Latest/Top) | không |
| format | trình bày danh sách item thành digest markdown | không |
| cite | tạo trích dẫn APA/Harvard cho một URL | có |
| send, policy, papers, paper_text | gửi Telegram (cần xác nhận), tìm tài liệu nội bộ, tìm và đọc paper arXiv (bonus, chưa dùng trong demo) | không |

## A3. Câu hỏi mẫu để thử

1. Tin tức Bitcoin hôm nay có gì?
2. Lấy 3 tweet mới nhất của Bill Gates
3. Mọi người nói gì về VinFast trên Twitter?
4. Trích dẫn giúp mình bài này theo APA: https://arxiv.org/abs/1706.03762
5. Tóm tắt 5 tweet mới nhất giúp mình (thiếu tài khoản: agent phải hỏi lại)

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Measure starter behaviour before any change | – | 0.45 | runs/v0_B_base_deepseek_20261110T100153055845.json |
| v1 | system_prompt.md | Starter prompt told the model to guess and auto-send; removing that fixes missing_info / out_of_scope / wrong_boundary | 0.45 | 0.70 | runs/v1_B_base_deepseek_20261110T112025442181.json |
| v2 (v2 to v2g) | tools.yaml (+ prompt routing rules from v2f) | Query format in tools.yaml and routing rules fix verbose queries and extra tool calls. Examples are copied literally by the model (v2b and v2e failed) | 0.70 | 0.95 (v2g) | runs/v2g_B_base_deepseek_20261110T205858398543.json |
| v3 | system_prompt.md | Send rule "first and only action is clarify yes_no, no matter the content" beats the missing-info reading (R12) | 0.95 | 1.00 | runs/v3_B_base_deepseek_20261110T210937618790.json |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

v0 = 11 failed of 20. Final status (v3) = 20/20 pass. "Fixed in" = first version where the case passed and stayed passing.

| Case ID | Failure Type | Actual Tool Calls (v0) | What Failed | Fix that worked | Fixed in |
|---|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | send (answered the integral via Telegram) | should call no tool | prompt: off-topic -> refuse, no tool | v1 |
| R14_out_of_scope_coding | out_of_scope | unexpected tool call | should call no tool | prompt: off-topic -> refuse, no tool | v1 |
| R10_missing_handle | missing_info | timeline(sama) | guessed account instead of clarify | prompt: ask first, never guess | v1 |
| R11_missing_url | missing_info | fetch(theverge.com) | invented URL instead of clarify | prompt: ask first, never guess | v1 |
| M06_switch_tool | wrong_tool | lookup("OpenAI news", timeframe=week) | verbose query + unrequested timeframe | passed in v1; regressed in v2c; stable from v2d with bare-subject query examples | v1 (flaky until v2d) |
| R13_parallel_web_and_tweets | wrong_tool | lookup("tin tức AI hôm nay") + social_search | lookup query not a bare subject | tools.yaml: query examples are bare subjects (v2d); translated examples broke it in v2e | v2d |
| M02_carryover_timeframe | wrong_arg_value | lookup("robotics news") | query has filler word "news" | tools.yaml: bare-subject query examples | v2d |
| R02_search_tweets_routing | wrong_tool | social_search x2 (Top + Latest) | extra tool call | prompt: routing rules + one call per source | v2f |
| R06_timeframe_arg | wrong_arg_value | lookup x2 | extra tool call | prompt: routing rules + one call per source | v2f |
| R03_web_news_routing | wrong_tool | lookup(long VN phrase) + social_search | query not a bare subject; extra call | v2f removed the extra call; v2g query text "không dịch, không đổi từ ngữ của user" (the earlier "preserve input" kept "tin tức AI") | v2g |
| R12_confirm_before_send | wrong_boundary | send(confirmed=true) | sent without asking; after v1 asked clarify with response_type=text, not yes_no | prompt: "first and only action is clarify with response_type=yes_no, no matter the content" | v3 |

Lessons from the logs:
- The model copies the shape of examples in a tool description (v2b copied a sentence template; v2e copied translated words such as "trí tuệ nhân tạo").
- A broad rule ("preserve user input") can conflict with a filler-removal rule; the fix was to scope it to "do not translate or change words".
- v2f and v2g changed both system_prompt.md and tools.yaml in one run, so those gains cannot be split between the two files.

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

Status: 3 of 10 cases written so far (1 single + 2 multi). Still needed: 4 single + 3 multi (ideas in `data/eval_group_example.json`).
Runs (v3 config, `--suite group`): `runs/v3_B_group_deepseek_20261110T214122889423.json` and `runs/v3_B_group_deepseek_20261110T214650772004.json`, both 3/3 pass.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_cite_with_url (single) | New tool routing: citation request with a URL goes to `cite` with the right url and style | `cite(url="https://arxiv.org/abs/1706.03762", style="apa")` | PASS (2 runs) |
| G06_multi_carry_topic (multi, 3 turns) | Switch the subject Bitcoin to Tesla and carry over topic=news and timeframe=day | `lookup(query="Tesla", topic="news", timeframe="day")` | PASS (2 runs) |
| G10_multi_confirm_before_send (multi, 3 turns) | Telegram post request needs a yes/no confirmation first, no `send` | `clarify(response_type="yes_no")` | PASS (2 runs) |

Note: the first version of G01 had no URL in the question but expected a specific URL, so the agent correctly asked with `clarify` and the case failed (0/1). Rewritten so every expected arg appears in the user's message. These cases all pass on v3, so they do not expose new weaknesses yet; harder cases are still to add.

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | "bitcoin news today?" | lookup(query="bitcoin", topic="news", timeframe="day", max_results=8), then round 2 wrote the answer from results | v2f, transcripts/v2f_deepseek_20261110T174012102361.transcript.json (chat.py) | Bare-subject query on a topic not in the eval; answer cited sources |
| 2 | "Tin tức Bitcoin hôm nay có gì?" (Streamlit UI) | lookup(query="Bitcoin", topic="news", timeframe="day", max_results=8) | v3, transcripts/v3_deepseek_20261110T215812239514.transcript.json (app.py) | Answer with 6+ cited sources; UI shows the tool trace |
| 3 | "Tóm tắt 5 tweet mới nhất giúp mình" (no account named) | no tool call; the agent asked in plain text which account | v3, same transcript, turn 2 | Asked instead of guessing. Note: in live chat the model replied in text, not via the clarify tool (the eval forces a tool call, chat does not). Follow-up answer not yet tested |
| 4 | TODO: follow-up with the account name | | | |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) |  |  |  |
| arXiv/company policy |  |  |  |
| UI | `app.py` (Streamlit), `.streamlit/config.toml`, transcript `transcripts/v3_deepseek_20261110T215812239514.transcript.json` | Chat UI with sample prompts, per-message tool trace, quick yes/no replies for clarify, auto-saved transcripts, download button | Public link still needs `cloudflared`; light theme only; UI sends the same tool loop as chat.py (max 4 tool rounds) |
| Tool unit tests (`tests/`) | `pytest` output: 70 passed, 14 skipped | 3 tests for the new cite tool (happy path, bad input, failure returns error dict) | 14 starter TODO stub tests still skipped; no bug found in existing tools yet |

Tool unit tests: số test đã viết, số bug tìm được trong tool có sẵn (nếu có), và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?

## B7. Small Local Model Challenge (bonus)

Only fill if your team did the local model challenge.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?
