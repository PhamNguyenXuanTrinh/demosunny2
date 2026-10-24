# Báo cáo V95
- Mã nguồn kế thừa nguyên bản V94; bổ sung `backend/accounting.py`, `tests/test_accounting_extended.py`, tài liệu kế toán và OpenAPI V95.
- Kết quả pytest thực chạy: xem `KET_QUA_KIEM_THU_V95.txt`.
- Đã kiểm tra các đường API kế toán mới và luồng công nợ, thanh toán vượt dư, VAT, khóa kỳ, quyền truy cập.
- Chưa kiểm thử tất cả luồng giao diện đầu-cuối và chưa kiểm thử xâm nhập thực tế.
- Không có căn cứ nói kế toán đã đầy đủ theo chế độ pháp lý Việt Nam; đọc `docs/KE_TOAN_BAN_GIAO_V95.md`.
