# SUNNY AI FLEX 3D V86 — Backend API & Database (bản nền kỹ thuật)

Bộ này bổ sung **backend thực thi** cho bộ giao diện V86 đã bàn giao. Đây là nền tảng phát triển và kiểm thử, **không phải ERP đã hoàn thiện 100%**.

## Thư mục
- `backend/main.py`: FastAPI endpoints, xác thực, kiểm tra đầu vào, phân quyền, kho, mua hàng, chi phí, tài liệu.
- `backend/security.py`: PBKDF2, Bearer token, vai trò.
- `backend/db.py`: SQLite, transaction, khởi tạo schema.
- `backend/agents.py`: 10 bộ phân tích theo quy tắc đọc dữ liệu SQLite.
- `database/schema_target.sql`: cấu trúc cơ sở dữ liệu đích.
- `docs/CAU_TRUC_DATABASE_VA_QUAN_HE.md`: mô tả quan hệ bảng và SQL mẫu.
- `docs/API_HUONG_DAN.md`: danh mục API, hướng dẫn chạy.
- `tests/test_api.py`: kiểm thử API thực.
- `public/index.html`: giao diện V86 trước đó, chưa chuyển hoàn toàn sang API.
- `archive/V86_GOC_BAT_BIEN.html`: V86 nguyên bản để đối chiếu, không phục vụ qua web.

## Chạy
```bash
python -m pip install -r requirements.txt
export SUNNY_ADMIN_PASSWORD='a-unique-password-longer-than-12'
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8765
```
Mở `http://127.0.0.1:8765/api/docs` để kỹ thuật chạy thử API.

## Kiểm thử
`python -m pytest tests -q`

## Điều kiện nghiệm thu còn thiếu
Kết nối giao diện V86 với API, đồng bộ localStorage có đối soát, kiểm soát vai trò/phạm vi chi tiết, OCR ảnh thật, tự động hóa 10 AI có điều phối và giới hạn ngân sách, 12 nhóm chi phí lấy từ sổ kế toán chuẩn, lương/KPI 5 kỳ, QC theo lô, đồng hồ điện, kiểm thử bảo mật và sao lưu/khôi phục.
