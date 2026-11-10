---
name: github_search
track: bonus
kind: live_api
provider: GitHub Search API
requires_env: []
inputs: [query, language, sort, limit]
outputs: [tool, query, total_count, items]
side_effect: false
---
# github_search

Tìm kiếm các kho lưu trữ (repository) mã nguồn mở trên GitHub theo từ khóa, ngôn ngữ và độ phổ biến.

