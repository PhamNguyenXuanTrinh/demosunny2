# SUNNY FLEX 3D V96 — mã nguồn bàn giao kiểm tra độc lập

Đây là bản mở rộng **trên toàn bộ mã nguồn V95**, không phải bản demo độc lập. Frontend nằm trong `public/`, Backend trong `backend/`, cấu trúc cơ sở dữ liệu trong `database/schema_target.sql`, triển khai tại `deploy/`, kiểm thử tại `tests/`.

## Cài đặt thử

1. Python 3.11+; `pip install -r requirements.txt`.
2. Thiết lập `SUNNY_ADMIN_PASSWORD` dài từ 12 ký tự, không ghi vào mã nguồn.
3. `uvicorn backend.main:app --host 127.0.0.1 --port 8000`.
4. Mở `/api/docs`, đăng nhập `/api/auth/login`, dùng Bearer token để thử API.
5. Chạy `python -m pytest -q`.

## Đánh giá thực tế

- Có mã nguồn và các API thực hiện CRUD/kiểm tra dữ liệu/nhật ký, không phải chỉ giao diện HTML.
- **Không được coi là 100 API nghiệp vụ độc lập** chỉ bằng cách nhân số phương thức và số bảng.
- **Chưa nghiệm thu:** kế toán pháp định Việt Nam, toàn bộ tương tác V86, AI tự chủ, thiết bị phần cứng thật, bảo mật chuyên sâu và kiểm thử đầu-cuối với nhiều vai trò.
- Đội kỹ thuật cần rà soát nghiệp vụ và chạy thử độc lập trước khi triển khai; không cam kết chỉ cần sửa vài dòng.
