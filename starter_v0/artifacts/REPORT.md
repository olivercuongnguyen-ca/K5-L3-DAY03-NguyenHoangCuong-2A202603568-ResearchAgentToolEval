# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: Nguyen Hoang Cuong
- Members: Nguyen Hoang Cuong – 2A202603568, 
- Provider/model: tokenharbor / deepseek-v4.1-flash:free
- Phiên bản cuối: **v4** = prompt v3 (`system_prompt.md`) + tools v4 (`tools.yaml`)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent: tìm tin web/mạng xã hội, đọc URL, tìm & đọc paper arXiv, tra cứu chính sách nội bộ, tổng hợp digest; hỏi lại khi thiếu thông tin và chỉ gửi Telegram sau khi người dùng xác nhận.

**Link dùng thử (deploy):** không deploy.

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin / xác nhận trước khi gửi | không |
| timeline | bài đăng gần đây của MỘT tài khoản X (tên → handle) | không |
| social_search | tìm bài đăng X theo từ khoá (Latest/Top) | không |
| lookup | tìm web/tin tức (topic + timeframe) | không |
| fetch | đọc nội dung một URL | không |
| format | dựng digest (brief/sections/bullets/thread/daily_ai_vn) | không |
| papers / paper_text | tìm / đọc paper arXiv | không |
| policy | tra chính sách nội bộ | không |
| send | gửi Telegram, chỉ sau khi xác nhận | không |

## A3. Câu hỏi mẫu để thử

1. Tweet mới nhất của Sam Altman là gì?
2. Tin AI tháng này
3. Tìm paper mới nhất về RAG evaluation
4. Quy định nội bộ về trích dẫn nguồn là gì?
5. Đăng bản tin này lên Telegram (agent phải hỏi lại, không tự gửi)

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Metric = case_accuracy trên `eval_base.json` (20 case).

| Version | Changed Artifact | Hypothesis | Before | After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline (đoán, gửi ngay) | — | — | 0.60 | runs/v0_B_base_tokenharbor_20261110T104104108616.json |
| v1 | system_prompt: cấu trúc XML | cấu trúc rõ hơn → routing/args tốt hơn | 0.60 | 0.65 | runs/v1_B_base_tokenharbor_20261110T111927199515.json |
| v2 | system_prompt: liệt kê tool + routing rules | mô tả tool rõ → routing đúng | 0.65 | 0.60 | runs/v2_B_base_tokenharbor_20261110T112657187106.json |
| v3 | system_prompt: guardrail clarify/send + error handling | sửa missing_info, wrong_boundary | 0.60 | 0.65 | runs/v3_B_base_tokenharbor_20261110T113242700325.json |
| v4 | **tools.yaml**: description (khi nào dùng/không), quy ước arg | sửa extra_tool_call + wrong_arg_value | 0.65 | **1.00** (lần chạy cuối; 0.95 ở 2 lần trước) | runs/v4_B_base_tokenharbor_20261110T164534306864.json |

Kết luận: chỉ sửa prompt gần như không đổi metric (0.60–0.65); sửa mô tả/tham số trong `tools.yaml` mới tạo bước nhảy lớn (routing 0.8 → 1.0). v5 (thử đổi prompt, `runs/v5_...160903690025.json`) chỉ đạt 0.95 nên **bỏ**, giữ v4. Kết quả có nhiễu giữa các lần chạy (v4: 0.95/0.95/1.0).

## B2. Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R10_missing_handle | missing_info | timeline (đoán) | không hỏi lại khi thiếu handle | v3 prompt `<missing_information>` + mô tả timeline "chưa biết tài khoản → clarify" |
| R12_confirm_before_send | wrong_boundary | lookup/policy, send | gửi/tra thay vì xác nhận | v3 `<send_safety>` + mô tả send; còn lệch `response_type` (text vs yes_no) ở 2 lần chạy v4 |
| R03_web_news_routing | wrong_arg_value | lookup + social_search thừa | query chứa "news/tin tức", gọi thừa tool | v4: "query chỉ từ khoá, KHÔNG thêm news/hôm nay", "gọi MỘT lần" |
| R06_timeframe_arg | wrong_tool | lookup lặp | gọi thừa tool | v4 mô tả timeframe + không lặp |
| M02_carryover_timeframe | wrong_arg_value | lookup `robotics news` | query lẫn "news"; mất timeframe | v4 quy ước query + "giữ timeframe lượt trước" |
| M05_correction_limit | wrong_arg_value | timeline `Elon Musk` | dùng tên đầy đủ thay handle | v4: "KHÔNG @, KHÔNG tên đầy đủ, Elon Musk → elonmusk" |

## B3. Team Eval Cases

`data/eval_group.json` – 10 case (5 single + 5 multi). Run v4: **8/10** (case_acc 0.80, routing 1.0) – `runs/v4_B_group_tokenharbor_20261110T192516920466.json`.

| Case ID | What It Tests | Expected | Result |
|---|---|---|---|
| G01_papers_routing | tìm paper → papers | papers(RAG evaluation) | pass |
| G02_papers_latest_sort | "mới nhất" → sort_by=submittedDate | papers(agents, submittedDate) | fail: query "LLM agents" (đúng nghĩa, grader chặt) |
| G03_policy_routing | quy định nội bộ → policy | policy | pass |
| G04_timeline_name_map | Sam Altman → sama, limit 3 | timeline(sama,3) | pass |
| G05_month_news | "tháng này" → timeframe=month | lookup(AI,news,month) | pass |
| M07_paper_then_sort | đổi sang "mới nhất", giữ chủ đề | papers(RAG, submittedDate) | fail: query "retrieval-augmented generation RAG" (đúng nghĩa) |
| M08_send_clarify | gửi khi chưa có nội dung → clarify | clarify | pass |
| M09_policy_then_area | hỏi tiếp quy định → policy | policy | pass |
| M10_topic_to_user | chuyển từ chủ đề sang tài khoản | timeline(elonmusk) | pass |
| M11_chit_chat_no_tool | chào/cảm ơn → không tool | no tool | pass |

2 fail đều là agent mở rộng query hợp lý; cần review thủ công, không phải lỗi routing.

## B4. Live Chat Evidence

Từ `transcripts/`:

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | "post a tweet saying hello" | không (hỏi xác nhận) | v1 | không có tool đăng → chặn/hỏi, sau "khong" thì huỷ đúng |
| 2 | "Tweet mới nhất của Sam Altman" | timeline | v1 | tool lỗi → báo ngắn gọn, không bịa |
| 3 | "musk" → "bài viết mới nhất của elon musk" | hỏi lại → timeline(elonmusk) | v1 | clarify rồi trả bài đăng kèm nguồn |
| 4 | "tweet" / "này" | clarify | v1 | hỏi lại khi thiếu thông tin |
| 5 | "tweet về spacex tuần này" | social_search | v1 | trả kết quả Latest |
| 6 | "giải phương trình 2x+5=4" | không | v1 | ngoài phạm vi, trả lời trực tiếp |
| 7 | "Search the web for latest news about OpenAI" | lookup | ui (v0) | trả tin có nguồn |

(Transcript chỉ ghi phiên v0/v1; v4 được kiểm bằng eval.)

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | tools/send, prompt `<send_safety>` | không gọi send khi chưa duyệt (R12, M08) | confirmed=true chỉ sau xác nhận rõ |
| arXiv/company policy | papers, paper_text, policy; G01–G03, M07, M09 | routing đúng 5/5 | query paper có thể bị mở rộng |
| UI | `ui/`, `ui_server.py` | chạy local | không deploy |
| Tool unit tests (`tests/`) | `pytest`: 79 passed, 0 skipped | 17 stub đã viết xong (clarify, format, send, lookup, fetch, timeline, social_search, policy) + 3 test cho `papers` (nhóm không thêm tool mới) | Không tìm thấy bug trong tool có sẵn; test chặn mạng thật nên chạy offline, miễn phí |

## B6. Reflection

- **Prompt**: guardrail (clarify khi thiếu info, xác nhận trước khi send, ngoài phạm vi, không lộ lỗi).
- **tools.yaml**: routing (khi nào dùng/không), quy ước arg (handle viết thường, query chỉ từ khoá, timeframe, search_type), "gọi một lần". Đây là phần hiệu quả nhất (0.65 → 0.95–1.0).
- **Cần review thủ công**: query paper được mở rộng (G02, M07) và `response_type` text vs yes_no ở R12.
- **Cải thiện tiếp**: nới grader cho query tương đương; chạy lại nhiều lần để đo nhiễu; thêm tool mới.

## B7. Small Local Model Challenge (bonus)
