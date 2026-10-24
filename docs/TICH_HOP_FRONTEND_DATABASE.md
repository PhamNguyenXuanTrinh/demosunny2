# Luồng kết nối dữ liệu V86

1. Trình duyệt `/` tải giao diện API thực, không lấy dữ liệu localStorage.
2. Đăng nhập `POST /api/auth/login` nhận bearer token trong bộ nhớ phiên trang (không lưu mật khẩu).
3. `GET /api/meta/modules` trả quyền đọc/ghi; backend kiểm tra lại quyền cho từng yêu cầu.
4. `GET /api/v1/{table}` lấy dữ liệu trực tiếp SQLite; `POST` ghi dữ liệu và nhật ký.
5. Ảnh: `POST /api/documents/intake` → bảng documents → api_jobs → worker → extraction_results → người có thẩm quyền xác minh. Chưa tự hạch toán.
6. Agent: worker định kỳ đọc SQLite → agent_evaluations. Hiện là quy tắc, chưa phải 10 LLM độc lập.
7. `/legacy.html` giữ giao diện V86 nguyên trạng (chạy dữ liệu trình duyệt riêng, **không đồng bộ**).
8. Sơ đồ FK chi tiết: `docs/CAU_TRUC_DATABASE_VA_QUAN_HE.md`; SQL `database/schema_target.sql`.

**Chưa đủ điều kiện sản xuất:** cần migrate mọi tính năng giao diện V86 cũ, bảo mật tải tệp, giới hạn truy cập theo ca/đơn, xử lý PDF, webhook thiết bị, AI thực và kiểm thử đầu-cuối.
