| STT | Họ và tên | MSSV | Phân công |
|---:|---|---|---|
| 2 | Bùi Văn Lâm | 2A202603400 | 3 tool mới (`crypto_price`, `github_search`, `currency_convert`), UI Streamlit (`app.py`), tune prompt v0–v3, `REPORT.md` |

# Cá nhân

## BuiVanLam-2A202603400

- Việc đã làm: Chạy baseline và tối ưu v0–v3 trên Gemini (0.53 → 1.00); viết 3 tool mới `crypto_price`, `github_search`, `currency_convert` kèm test; dựng UI Streamlit (`app.py`), poster và báo cáo đầu tiên.
- Commit hoặc file thể hiện phần việc đó: commit `f9c9759`, `4e9916e`, `1c88ba0`, `2d8fb46`, `2a793f1`, `39c4ed9` trên nhánh `buivanlam`; `tools/crypto_price/`, `tools/github_search/`, `tools/currency_convert/`, `app.py`, `artifacts/poster.html`, `runs/v*_gemini_*`.
- Điều đã học: Mỗi version chỉ nên đổi một thứ (prompt hoặc tool declaration) để biết giả thuyết nào làm metric tăng. Rule routing, rule xin xác nhận trước khi gửi và quy ước tham số (`topic=news`, handle không có `@`) là phần tác động nhiều nhất tới eval.
