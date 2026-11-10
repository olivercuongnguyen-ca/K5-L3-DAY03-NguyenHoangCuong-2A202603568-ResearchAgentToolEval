# Thành viên nhóm · Day 04

Tên nhóm: 
Lớp (L3A hoặc L3B): 
Link repo nhóm: https://github.com/olivercuongnguyen-ca/K5-L3-DAY03-NguyenHoangCuong-2A202603568-ResearchAgentToolEval

| STT | Họ và tên | MSSV | Phân công |
|---:|---|---|---|
| 1 | Nguyễn Hoàng Cương | 2A202603568 | Trưởng nhóm · Tổng hợp bài nộp, thử nghiệm provider TokenHarbor, UI HTML (`ui_server.py`), eval nhóm |
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

- Việc đã làm:
- Commit hoặc file thể hiện phần việc đó:
- Điều đã học:

## PhanBaAn-2A202603375

- Việc đã làm:
- Commit hoặc file thể hiện phần việc đó:
- Điều đã học:

## DoMinhHieu-2A202603402

- Việc đã làm:
- Commit hoặc file thể hiện phần việc đó:
- Điều đã học:
