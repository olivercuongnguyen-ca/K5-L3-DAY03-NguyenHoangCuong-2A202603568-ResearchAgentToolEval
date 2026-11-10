| STT | Họ và tên | MSSV | Phân công |
|---:|---|---|---|
| 2 | Bùi Văn Lâm | 2A202603400 | 3 tool mới (`crypto_price`, `github_search`, `currency_convert`), UI Streamlit (`app.py`), tune prompt v0–v3, `REPORT.md` |
| 3 | Phan Bá An | 2A202603375 | Tool `semantic_scholar`, unit test, eval case, viết lại `tools.yaml` và prompt |

# Cá nhân

## BuiVanLam-2A202603400

- Việc đã làm: Chạy baseline và tối ưu v0–v3 trên Gemini (0.53 → 1.00); viết 3 tool mới `crypto_price`, `github_search`, `currency_convert` kèm test; dựng UI Streamlit (`app.py`), poster và báo cáo đầu tiên.
- Commit hoặc file thể hiện phần việc đó: commit `f9c9759`, `4e9916e`, `1c88ba0`, `2d8fb46`, `2a793f1`, `39c4ed9` trên nhánh `buivanlam`; `tools/crypto_price/`, `tools/github_search/`, `tools/currency_convert/`, `app.py`, `artifacts/poster.html`, `runs/v*_gemini_*`.
- Điều đã học: Mỗi version chỉ nên đổi một thứ (prompt hoặc tool declaration) để biết giả thuyết nào làm metric tăng. Rule routing, rule xin xác nhận trước khi gửi và quy ước tham số (`topic=news`, handle không có `@`) là phần tác động nhiều nhất tới eval.

## PhanBaAn-2A202603375

- Việc đã làm: Viết tool `semantic_scholar` (tìm bài báo ngoài arXiv, trả abstract và số trích dẫn), khai báo trong `tools.yaml`, viết unit test và 3 eval case `B_SEMANTIC_001–003`.
- Commit hoặc file thể hiện phần việc đó: commit `9afe1e0` trên nhánh `phanbaan`; `tools/semantic_scholar/` (`tool.py`, `TOOL.md`), các test `test_semantic_scholar_*` trong `tests/test_tools_todo.py`.
- Điều đã học: Một tool mới cần đủ 4 phần: code, `TOOL.md`, đăng ký trong `tools/__init__.py` và khai báo trong `tools.yaml`; contract test sẽ báo lỗi nếu các nơi này lệch nhau. Unit test với `fake_http` kiểm tra được xử lý lỗi HTTP mà eval routing không thấy được.
