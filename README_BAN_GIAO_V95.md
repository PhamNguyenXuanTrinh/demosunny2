# SUNNY FLEX 3D V95 – Bộ mã nguồn bàn giao kỹ thuật

Đây là bản phát triển dựa trên toàn bộ V94, không phải bản HTML riêng lẻ. Bao gồm frontend, backend, schema SQL, tài liệu, kiểm thử, API OpenAPI được xuất và báo cáo kiểm thử V95.

## Chạy thử
`python -m pip install -r requirements.txt`
`export SUNNY_ADMIN_PASSWORD='MAT_KHAU_MOI_TOI_THIEU_12_KY_TU'`
`python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`

Trên Windows dùng lệnh đặt biến môi trường tương ứng. API docs: `/api/docs`. Giao diện: `/`.

## Chạy kiểm thử
`python -m pytest -q`

## Trạng thái
Đã chạy kiểm thử tự động với SQLite độc lập. Đây là mã nguồn bàn giao để tiếp tục phát triển/đánh giá; chưa đủ bằng chứng đạt tiêu chuẩn kế toán Việt Nam hoặc nghiệm thu sản xuất.
Đọc `docs/KE_TOAN_BAN_GIAO_V95.md` và `BAO_CAO_V95.md` trước khi triển khai.
