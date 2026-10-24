# Quy tắc bảo toàn giao diện SUNNY V86
- `public/index.html` và `public/v86.html`: bản giao diện V86 nguyên gốc, giữ nguyên byte từ tệp được giao.
- `public/app.html`: giao diện kết nối API đang phát triển, không thay thế V86.
- Các API thực thi ở `backend/`. Xem `docs/API_KIEM_KE_THUC_TE.json`.
- CẢNH BÁO: V86 gốc có thể chứa thao tác giả lập/chưa kết nối Backend. Việc giữ nguyên giao diện không chứng minh tích hợp hoàn chỉnh.
