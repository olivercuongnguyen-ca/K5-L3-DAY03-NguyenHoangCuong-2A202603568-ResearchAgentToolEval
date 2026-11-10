# Thành viên nhóm · Day 04

Tên nhóm: 
Lớp (L3A hoặc L3B): L3A
Link repo nhóm: https://github.com/olivercuongnguyen-ca/K5-L3-DAY03-NguyenHoangCuong-2A202603568-ResearchAgentToolEval

| STT | Họ và tên | MSSV | Phân công |
|---:|---|---|---|
| 1 | Nguyễn Hoàng Cương | 2A202603568 | Trưởng nhóm - Tổng hợp bài nộp, thử nghiệm provider TokenHarbor, UI HTML (`ui_server.py`), eval nhóm |
| 2 | Bùi Văn Lâm | 2A202603400 | 3 tool mới (`crypto_price`, `github_search`, `currency_convert`), UI Streamlit (`app.py`), tune prompt v0–v3, `REPORT.md` |
| 3 | Phan Bá An | 2A202603375 | Tool `semantic_scholar`, unit test, eval case, viết lại `tools.yaml` và prompt |
| 4 | Đỗ Minh Hiếu | 2A202603402 | Tool `cite`, provider DeepSeek, thí nghiệm tune prompt/tool v1–v3 (v2b–v2g) |

Gợi ý chia việc: TODO 1 và 2, TODO 3, chạy eval và đọc trace, 2 thí nghiệm và `REFLECTION.md`.

# Cá nhân

Mỗi thành viên tự viết một mục theo mẫu dưới, đặt tiêu đề theo họ tên không dấu và MSSV của mình.

## NguyenHoangCuong-2A202603568

- Việc đã làm: Cài provider TokenHarbor và chạy chuỗi thí nghiệm v0–v4 trên bộ eval base; dựng UI HTML (`ui_server.py`, `ui/`); viết 10 eval case nhóm (5 single, 5 multi); tổng hợp bài nộp của cả nhóm bằng `git merge`, chạy lại eval `v4` trên 15 tool và cập nhật `REPORT.md`.
- Commit hoặc file thể hiện phần việc đó: commit `73a46f8`, `896c9b2`, `09f905f`, `8605dd5` trên nhánh `cuong`; `providers/tokenharbor_provider.py`, `ui_server.py`, `artifacts/tools_v4.yaml`, `runs/v*_tokenharbor_*`; các merge commit và `runs/v4_B_*_gemini_*` trên `main`.
- Điều đã học: Chỉ sửa prompt thì điểm dao động 0.60–0.65, còn viết lại mô tả tool trong `tools.yaml` (`NHC-v4`) mới đưa eval lên 1.00. Khi gộp công việc nhiều người, `system_prompt.md` và `tools.yaml` không merge cơ học được vì hash trong `version_log.csv` phải khớp artifact, nên phải chạy lại eval sau khi gộp.

## BuiVanLam-2A202603400

- Việc đã làm: Chạy baseline và tối ưu v0–v3 trên Gemini (0.53 → 1.00); viết 3 tool mới `crypto_price`, `github_search`, `currency_convert` kèm test; dựng UI Streamlit (`app.py`), poster và báo cáo đầu tiên.
- Commit hoặc file thể hiện phần việc đó: commit `f9c9759`, `4e9916e`, `1c88ba0`, `2d8fb46`, `2a793f1`, `39c4ed9` trên nhánh `buivanlam`; `tools/crypto_price/`, `tools/github_search/`, `tools/currency_convert/`, `app.py`, `artifacts/poster.html`, `runs/v*_gemini_*`.
- Điều đã học: Mỗi version chỉ nên đổi một thứ (prompt hoặc tool declaration) để biết giả thuyết nào làm metric tăng. Rule routing, rule xin xác nhận trước khi gửi và quy ước tham số (`topic=news`, handle không có `@`) là phần tác động nhiều nhất tới eval.

## PhanBaAn-2A202603375

- Việc đã làm: Viết tool `semantic_scholar` (tìm bài báo ngoài arXiv, trả abstract và số trích dẫn), khai báo trong `tools.yaml`, viết unit test và 3 eval case `B_SEMANTIC_001–003`.
- Commit hoặc file thể hiện phần việc đó: commit `9afe1e0` trên nhánh `phanbaan`; `tools/semantic_scholar/` (`tool.py`, `TOOL.md`), các test `test_semantic_scholar_*` trong `tests/test_tools_todo.py`.
- Điều đã học: Một tool mới cần đủ 4 phần: code, `TOOL.md`, đăng ký trong `tools/__init__.py` và khai báo trong `tools.yaml`; contract test sẽ báo lỗi nếu các nơi này lệch nhau. Unit test với `fake_http` kiểm tra được xử lý lỗi HTTP mà eval routing không thấy được.

## DoMinhHieu-2A202603402

- Việc đã làm:
  - Chạy baseline v0 và tối ưu prompt/tool qua v1 đến v3 trên DeepSeek. v2 có nhiều subedit, overall v0->v3 từ 0.45 -> 0.7 -> 0.95 -> 1.0
  - Phân tích 11 case lỗi của v0 và ghi version log (REPORT B1, B2).
  - Viết tool mới `cite` (TOOL.md, đăng ký, khai báo `tools.yaml`, 3 unit test) và thêm provider DeepSeek.
  - Xây UI Streamlit `app.py`, viết 3 eval case nhóm, điền REPORT Part A và B1 đến B5.
- Commit hoặc file thể hiện phần việc đó: nhánh `dominhhieu`, commit `0d1b414`: `artifacts/system_prompt.md`, `artifacts/tools.yaml`, `artifacts/version_log.csv`, `artifacts/REPORT.md`, `tools/cite/`, `tests/test_tools_todo.py`, `providers/deepseek_provider.py`, `app.py`, `runs/`, `transcripts/`.
- Điều đã học:
  - Model sao chép dạng của ví dụ trong mô tả của tool nên ví dụ Đúng/Sai phải khớp dạng mong muốn (keyword ngắn, preferable 1-2 từ, không thêm từ thừa).
  - Phải prompt rõ ưu tiên quy tắc xác nhận yes/no trước khi gửi file, priority phải cao hơn hỏi missing context/information.  
  - Mỗi version chỉ nên đổi một thứ để dễ tracking; v2f và v2g đổi cả prompt và tools nên không tách được tác động của từng thay đổi, dẫn đến kết quả tương tự nhau.
  - Eval case phải suy ra được hoàn toàn từ câu của người dùng, nếu không agent hỏi lại là đúng còn case thì sai.
- Còn thiếu: 14 test stub còn skip và mới có 3 trong 10 eval case nhóm.
