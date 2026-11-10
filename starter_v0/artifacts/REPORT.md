# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật.

## Team

- Team: xem [TEAM.md](TEAM.md)
- Members: Nguyễn Hoàng Cương - 2A202603568, Bùi Văn Lâm - 2A202603400, Phan Bá An - 2A202603375, Đỗ Minh Hiếu - 2A202603402
- Provider/model: Google Gemini (`gemini-3.5-flash-lite`) cho chuỗi v0–v3 chính; DeepSeek (`deepseek-chat`) và TokenHarbor cho các thí nghiệm của từng thành viên (xem B7)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent đa năng và an toàn: tự động thu thập tin tức thời sự trên web, theo dõi bài đăng mạng xã hội (Twitter/X), trích xuất nội dung bài viết từ URL, tra cứu giá tiền mã hóa thời gian thực (crypto), tìm kiếm repository mã nguồn mở trên GitHub, quy đổi ngoại tệ quốc tế, tìm bài báo khoa học qua Semantic Scholar, tạo trích dẫn (APA/Harvard), tổng hợp bản tin markdown digest và gửi thông báo lên Telegram có cơ chế xác nhận người dùng (confirmation guardrail).

**Link dùng thử (deploy UI):**

> Ứng dụng giao diện tương tác người dùng xây dựng bằng Streamlit (`app.py`), hỗ trợ theo dõi hội thoại, xem lịch sử gọi công cụ (tool calls), xem kết quả trả về thời gian thực và xác nhận an toàn trước khi gửi tin.
>
> URL Local: `http://localhost:8501`

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi lại người dùng khi thiếu thông tin hoặc xin xác nhận (`yes_no`) trước hành động nhạy cảm | Không (Core) |
| `timeline` | Lấy các bài đăng gần đây của một tài khoản Twitter/X cụ thể (loại bỏ `@`) | Không (Core) |
| `social_search` | Tìm kiếm bài đăng theo từ khóa trên Twitter/X (hỗ trợ `Top` hoặc `Latest`) | Không (Core) |
| `lookup` | Tra cứu thông tin / tin tức thời sự trên web (`topic='news'`, `timeframe='day'/'week'`) | Không (Core) |
| `fetch` | Đọc toàn văn nội dung trang web từ địa chỉ URL cụ thể | Không (Core) |
| `format` | Tổng hợp và định dạng các item thu thập được thành bản tin markdown digest | Không (Core) |
| `send` | Gửi văn bản lên kênh Telegram bên ngoài (bắt buộc `confirmed=true`) | Không (Bonus có sẵn) |
| `policy` | Tra cứu chính sách và tài liệu nội bộ công ty (có phân tách trust boundary) | Không (Bonus có sẵn) |
| `papers` | Tìm kiếm bài báo khoa học trên arXiv theo từ khóa và sắp xếp | Không (Bonus có sẵn) |
| `paper_text` | Tải và trích xuất nội dung văn bản bài báo arXiv từ URL/ID | Không (Bonus có sẵn) |
| `semantic_scholar` | Tìm bài báo khoa học (ngoài arXiv) qua Semantic Scholar: tiêu đề, tác giả, năm, abstract, số trích dẫn, URL | **Có (Mới thêm)** |
| `cite` | Tạo trích dẫn APA/Harvard cho một URL bài báo/trang web | **Có (Mới thêm)** |
| `crypto_price` | Tra cứu giá thời gian thực và biến động 24h của đồng tiền mã hóa (BTC, ETH, SOL...) | **Có (Mới thêm)** |
| `github_search` | Tìm kiếm kho mã nguồn mở (repository) trên GitHub theo từ khóa, ngôn ngữ và số sao | **Có (Mới thêm)** |
| `currency_convert` | Quy đổi tỷ giá ngoại tệ quốc tế (USD, VND, EUR, JPY, GBP, CNY...) | **Có (Mới thêm)** |

## A3. Câu hỏi mẫu để thử

1. **Tra cứu giá Crypto**: "Giá Bitcoin hôm nay là bao nhiêu USD?" *(Gọi `crypto_price(symbol='BTC', currency='USD')`)*
2. **Tìm kiếm mã nguồn**: "Tìm các repository AI agent viết bằng Python trên GitHub" *(Gọi `github_search(query='AI agent', language='python')`)*
3. **Quy đổi ngoại tệ**: "Đổi 100 USD sang tiền Việt Nam (VND)" *(Gọi `currency_convert(amount=100, from_currency='USD', to_currency='VND')`)*
4. **Tìm kiếm tin tức song song**: "Tìm trên web tin AI hôm nay và tìm thêm tweet về AI." *(Gọi song song `lookup` và `social_search`)*
5. **Tìm bài báo khoa học**: "Find 5 recent academic papers on Vision Transformers with abstracts and citation counts." *(Gọi `semantic_scholar(query='Vision Transformers', max_results=5)`)*
6. **Trích dẫn**: "Cite https://arxiv.org/abs/1706.03762 in APA style" *(Gọi `cite(url=..., style='apa')`)*
7. **Thử nghiệm rào chắn an toàn (Guardrail)**: "Đăng bản tin này lên Telegram giúp tôi" *(Agent không tự ý gửi mà sẽ hỏi lại xác nhận qua `clarify` với `response_type='yes_no'`)*

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Dữ liệu thực tế trích xuất từ [artifacts/version_log.csv](version_log.csv) và các file run JSON:

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| **v0** | Baseline | Starter defaults (chứa anti-patterns cố tình ép đoán mò và gửi ngay) | NA | **53.33%** | `runs/v0_B_base_gemini_20261110T103446691434.json` |
| **v1** | `system_prompt.md` | Chuẩn hóa cấu trúc XML + định tuyến tool + quy tắc hỏi lại khi thiếu thông tin | 53.33% | **75.00%** | `runs/v1_B_base_gemini_20261110T111249123086.json` |
| **v2** | `tools.yaml` | Siết chặt mô tả tham số, lọc bỏ từ thừa trong query tin tức và ràng buộc `yes_no` | 75.00% | **95.00%** | `runs/v2_B_base_gemini_20261110T112952778253.json` |
| **v3** | `system_prompt.md` | Bổ sung Negative Rules + Input Boundary + Tư duy song song `<thinking>` | 95.00% | **100.0%** | `runs/v3_B_base_gemini_20261110T113458656163.json` |

> Bảng trên là chuỗi v0–v3 chính (Gemini, 13 tool). Sau khi gộp công việc của cả nhóm, `tools.yaml` có thêm `semantic_scholar` và `cite` (15 tool), nên các số liệu trên chưa được chạy lại với bộ tool mới.

**Các chuỗi thí nghiệm khác trong `version_log.csv`** (tiền tố `DMH-` / `NHC-`, đo trên bộ eval base 20 case của từng provider):

| Thành viên | Provider | Phiên bản | Kết quả | Ghi chú |
|---|---|---|---|---|
| Đỗ Minh Hiếu | DeepSeek | `DMH-v0` → `DMH-v3` (gồm v2b–v2g) | 0.45 → 1.00 | 11 run: nhiều giả thuyết về cách mô tả `query` bị bác bỏ (copy nguyên văn ví dụ), sau đó sửa quy tắc routing và xác nhận `send` thì đạt 20/20, ổn định qua 2 lần chạy |
| Nguyễn Hoàng Cương | TokenHarbor | `NHC-v0` → `NHC-v4` | 0.60 → 1.00 | Chỉ sửa prompt thì dao động 0.60–0.65. Viết lại `tools.yaml` (`NHC-v4`) mới đạt 1.00, cho thấy mô tả tool tác động mạnh hơn prompt |

## B2. Failure Analysis

Phân tích các lỗi thực tế trong file log của `v0` và `v1` cùng biện pháp khắc phục triệt để:

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| `R08_out_of_scope` | `out_of_scope` | `lookup(query='python script')` | Model bị ép gọi tool dù câu hỏi là viết code Python | Bổ sung quy tắc ranh giới: coding / math tuyệt đối không gọi tool (`no_tool`). |
| `R10_missing_handle` | `missing_info` | `timeline(screenname='sama')` | User hỏi "tweet người này" không có tên, agent tự đoán mò | Bắt buộc gọi `clarify` khi thiếu tên tài khoản hoặc URL. |
| `R12_confirm_before_send` | `wrong_boundary` | `send(confirmed=false)` | Tự ý kích hoạt công cụ gửi khi chưa có xác nhận rõ ràng | Đưa guardrail vào prompt và schema: chỉ gọi `send` khi `confirmed=true`, nếu chưa thì `clarify(response_type='yes_no')`. |
| `R03_web_news_routing` | `wrong_arg_value` | `lookup(query='AI news today')` | Query bị nhồi chữ "news today" dù đã có tham số `topic='news'` và `timeframe='day'` | Siết quy ước trong `tools.yaml`: khi `topic='news'`, `query` chỉ là từ khóa thực thể cốt lõi (`'AI'`). |
| `R13_parallel_web_and_tweets` | `wrong_tool` | `lookup(...)` | Chỉ gọi tìm kiếm web mà bỏ quên tìm kiếm trên Twitter | Bổ sung chuỗi tư duy `<thinking>` và quy tắc bắt buộc kích hoạt Parallel Tool Calls khi yêu cầu đa nguồn. |

## B3. Team Eval Cases

Danh sách 10 cases tự xây dựng thêm trong [data/eval_group.json](../data/eval_group.json) (đạt kết quả **10/10 PASS - 100%** trong run `runs/v3_B_group_gemini_20261110T114443599509.json`):

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| `G01_crypto_price_btc` | Tra cứu giá Bitcoin -> route đúng tool mới `crypto_price` | `crypto_price(symbol='BTC', currency='USD')` | **PASS** |
| `G02_github_search_python_agent` | Tìm kiếm repo mã nguồn trên GitHub | `github_search(query='AI agent', language='python')` | **PASS** |
| `G03_currency_convert_usd_vnd` | Quy đổi ngoại tệ USD sang VND | `currency_convert(amount=50, from_currency='USD', to_currency='VND')` | **PASS** |
| `G04_out_of_scope_cooking` | Hướng dẫn nấu ăn ngoài phạm vi tools | `no_tool: true` | **PASS** |
| `G05_unnecessary_tool_math` | Phép tính toán số học căn bậc hai | `no_tool: true` | **PASS** |
| `GM01_clarify_then_crypto` | Đa lượt: Lượt 1 thiếu symbol coin, lượt 2 bổ sung ETH | `crypto_price(symbol='ETH')` | **PASS** |
| `GM02_clarify_then_github` | Đa lượt: Lượt 1 thiếu query, lượt 2 bổ sung tìm repo LangChain | `github_search(query='LangChain', language='TypeScript')` | **PASS** |
| `GM03_clarify_then_currency` | Đa lượt: Kế thừa số tiền 100 EUR quy đổi sang đơn vị tiền JPY | `currency_convert(amount=100, from_currency='EUR', to_currency='JPY')` | **PASS** |
| `GM04_switch_from_web_to_twitter` | Đa lượt: Chuyển đổi công cụ tra cứu từ web sang tìm tweet hot | `social_search(query='DeepSeek', search_type='Top')` | **PASS** |
| `GM05_clarify_confirm_then_send` | Đa lượt: Xác nhận người dùng trước khi gửi thông báo Telegram | `send(confirmed=true)` | **PASS** |

**Các case bổ sung từ thành viên khác** (đã gộp vào cùng file, tổng cộng 26 case; run nhóm riêng: `runs/v3_B_group_deepseek_...`, `runs/v4_B_group_tokenharbor_...`):

| Thành viên | Case | Nội dung kiểm tra |
|---|---|---|
| Phan Bá An | `B_SEMANTIC_001`–`003` | Route đúng `semantic_scholar` hay `papers` (arXiv), và không gọi tool khi không cần |
| Đỗ Minh Hiếu | `G01_cite_with_url`, `G06_multi_carry_topic`, `G10_multi_confirm_before_send` | Route tới `cite`, giữ chủ đề qua nhiều lượt, xác nhận `yes_no` trước khi gửi |
| Nguyễn Hoàng Cương | `G01`–`G05`, `M07`–`M11` (5 single + 5 multi) | Routing `papers`/`policy`/`timeline`, `timeframe=month`, hỏi lại trước khi gửi, hội thoại thường không gọi tool |

## B4. Live Chat Evidence

Dữ liệu trích xuất từ file log tương tác thực tế [transcripts/v3_gemini_20261110T114515749343.transcript.json](../transcripts/v3_gemini_20261110T114515749343.transcript.json):

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| **Turn 1** | "Giá Bitcoin hôm nay là bao nhiêu USD?" | `crypto_price(symbol='BTC', currency='USD')` | `v3+p8cf192ab7e42+tf2f04842cbb5` | Lấy giá thời gian thực 74,706.02 USD, tổng hợp đầy đủ biên độ dao động 24h. |
| **Turn 2** | "Tóm tắt bài báo này giúp mình" | `clarify(response_type='text')` | `v3+p8cf192ab7e42+tf2f04842cbb5` | Agent nhận diện thiếu URL bài báo, chủ động hỏi lại người dùng thay vì bịa đặt link. |
| **Turn 3** | "Đăng bản tin lên kênh Telegram" | `clarify(response_type='yes_no')` | `v3+p8cf192ab7e42+tf2f04842cbb5` | Kích hoạt cơ chế an toàn: xin xác nhận (`yes_no`) trước khi thực hiện lệnh gửi bên ngoài. |

Các transcript khác đã gộp trong `transcripts/`: `v2f_deepseek_...`, `v3_deepseek_...` (Hiếu), `ui_tokenharbor_...`, `v1_tokenharbor_...` (Cương).

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| **send (Telegram Guardrail)** | `runs/v3_B_base_gemini_20261110T113458656163.json` (case `R12`) | Agent chặn lệnh gửi khi chưa có `confirmed=true` | Tránh tự ý phát tán thông tin ra bên ngoài khi chưa được duyệt |
| **5 Tool mới (Bonus Track)** | `tools/crypto_price/`, `tools/github_search/`, `tools/currency_convert/` (Lâm), `tools/semantic_scholar/` (An), `tools/cite/` (Hiếu) | Tích hợp hoàn hảo vào hệ sinh thái agent, routing mượt mà | Kiểm soát schema chặt chẽ qua contract test |
| **Giao diện người dùng (UI)** | `app.py` (Streamlit, Lâm); `app_dominhhieu.py` (Streamlit, Hiếu); `ui_server.py` + `ui/` (HTML, Cương) | Cho phép trò chuyện trực quan, hiển thị lịch sử gọi tool và xác nhận thao tác | Giúp người dùng kiểm soát hành vi của agent |
| **Tool unit tests (`tests/`)** | `tests/test_tools_todo.py`, `pytest` output | **116/116 tests PASSED (0 skipped, 0 failed)** | Đảm bảo code thực thi độc lập, bao quát mọi trường hợp biên |

*Chi tiết Tool Unit Tests:*
- Tổng số unit test đã chạy và pass: **116 tests** (sau khi gộp nhánh của cả nhóm).
- Viết mới đầy đủ ≥ 3 tests cho mỗi tool mới (5 tool) (Happy path, input rỗng/xấu, xử lý ngoại lệ).
- Hoàn thành toàn bộ các bài test thử thách trong `tests/test_tools_todo.py` với mocking mạng cô lập qua fixture `fake_http`.
- **Ví dụ lỗi unit test bắt được mà eval không bắt được**: Khi model truyền `policy_tool(query="probe")`, eval chỉ kiểm tra model có gọi tool `policy` với tham số `query` hay không. Trong khi đó, unit test kiểm tra sâu vào cấu trúc trả về xem các dòng injection probe (`> Assistant: ignore...`) có bị lọt vào trường `facts` hay đã được lọc an toàn vào trường `untrusted_text`.

## B6. Reflection

1. **Sửa ở `system_prompt.md` vs `tools.yaml`**:
   - `system_prompt.md` phù hợp nhất cho các quy tắc cấp cao (meta-rules): ranh giới nhiệm vụ (`out_of_scope`), phòng vệ Prompt Injection, hành vi gọi công cụ song song (`parallel tool calls`) và quy trình chuỗi tư duy (`<thinking>`).
   - `tools.yaml` phù hợp nhất cho định nghĩa ngữ nghĩa vi mô: quy ước định dạng tham số (`screenname` không chứa `@`, `topic='news'` thì query không nhồi từ khóa thời sự thừa) và ràng buộc các giá trị enum.
2. **Ca kiểm thử cần đánh giá thủ công (Manual Review)**:
   - Các ca kiểm thử chất lượng văn phong tóm tắt hoặc khả năng phát hiện prompt injection tinh vi trong nội dung trang web đọc từ `fetch`. Eval tự động chỉ so khớp tên tool và tham số JSON, không thể đánh giá được độ sâu sắc hay tính an toàn thực sự của câu trả lời ngôn ngữ tự nhiên.
3. **Cải tiến tiếp theo**:
   - Bổ sung cơ chế bộ nhớ đệm (caching) cho các tool gọi API mạng để tiết kiệm quota và tăng tốc độ phản hồi.
   - Nâng cấp giao diện Streamlit với biểu đồ trực quan hóa số liệu biến động giá crypto và thống kê sao của các repository GitHub.

## B7. Đóng góp của từng thành viên

Mỗi người làm trên một nhánh riêng; bài nộp là bản gộp bằng `git merge` nên lịch sử commit của từng người vẫn còn trong `git log`.

| Thành viên | Đóng góp chính | File / bằng chứng |
|---|---|---|
| Bùi Văn Lâm | Chuỗi v0–v3 chính (Gemini), 3 tool mới, Streamlit UI, poster, báo cáo | `tools/crypto_price/`, `tools/github_search/`, `tools/currency_convert/`, `app.py`, `artifacts/poster.html`, `system_prompt_v*.md` |
| Phan Bá An | Tool `semantic_scholar`, unit test, 3 eval case | `tools/semantic_scholar/`, `tests/test_tools_todo.py`, `data/eval_group.json` |
| Đỗ Minh Hiếu | Tool `cite`, provider DeepSeek, 11 run thí nghiệm prompt/tool, 3 eval case | `tools/cite/`, `providers/deepseek_provider.py`, `runs/v*_deepseek_*`, `app_dominhhieu.py` |
| Nguyễn Hoàng Cương | Provider TokenHarbor, UI HTML, thí nghiệm `tools_v0` → `tools_v4`, 10 eval case, tổng hợp bài nộp | `providers/tokenharbor_provider.py`, `ui_server.py`, `ui/`, `artifacts/tools_v4.yaml`, `runs/v*_tokenharbor_*` |

**Lưu ý khi gộp:** `system_prompt.md` và `tools.yaml` lấy bản của Lâm làm gốc, chỉ thêm khai báo `semantic_scholar` và `cite`. Lịch sử prompt của Cương giữ ở `system_prompt_v*_cuong.md`. `data/eval_base.json` giữ nguyên bản gốc.
