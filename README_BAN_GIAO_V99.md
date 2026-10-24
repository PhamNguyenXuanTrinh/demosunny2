# SUNNY FLEX 3D – V99 bàn giao mã nguồn phát triển ERP

## Tình trạng được xác minh
- 115 cặp phương thức–đường dẫn API, tính từ FastAPI app.routes (không phải 115 quy trình ERP hoàn chỉnh).
- 44/44 bài kiểm thử tự động đạt trong môi trường kiểm thử tại thời điểm đóng gói.
- 12 phân hệ danh mục ERP bổ sung có SQL thật, phân quyền, kiểm tra dữ liệu, nhật ký thay đổi; 48 cặp API GET/POST/PATCH.
- Đã kiểm tra đăng nhập, tạo/đọc bản ghi, tài liệu OpenAPI và tình huống truy cập thiếu xác thực.

## Thành phần
- `backend/`: mã nguồn API và xử lý nghiệp vụ.
- `database/`: lược đồ SQL; bảng ERP mở rộng được khởi tạo trong `backend/erp_registry.py`.
- `public/`, `archive/`: giao diện hiện hành và giao diện V86 lưu trữ.
- `tests/`: kiểm thử; `DANH_SACH_API_V99.json`: danh sách đường dẫn thực tế.
- `deploy/`, `.env.example`, `requirements.txt`: cấu hình triển khai.

## Chạy thử
1. Tạo môi trường Python, cài `pip install -r requirements.txt`.
2. Đặt biến môi trường `SUNNY_ADMIN_PASSWORD` là mật khẩu riêng tối thiểu 12 ký tự (không dùng mật khẩu kiểm thử).
3. `python -m pytest -q`.
4. `uvicorn backend.main:app --host 127.0.0.1 --port 8000`.
5. Mở `/api/docs` để kiểm tra các API.

## Chưa thể xác nhận là ERP hoàn chỉnh
- 48 API mới là các thao tác quản lý hồ sơ theo phân hệ, chưa phải quy trình mua–nhập–xuất–sản xuất–bán–thu tiền–hạch toán khép kín.
- Chưa nghiệm thu nghiệp vụ kế toán pháp định Việt Nam, tính lương/thuế đầy đủ, AI Agent tự động đầu cuối, đồng bộ mọi nút giao diện V86, trình điều khiển thiết bị theo hãng, bảo mật chuyên sâu trên hạ tầng triển khai.
- SQLite là cơ sở dữ liệu đang dùng để thử nghiệm; cần đánh giá giao dịch đồng thời, sao lưu và phương án PostgreSQL khi triển khai thực tế.
- Kiểm thử hiện có chưa đủ để cam kết không còn lỗi.

**Không triển khai chính thức chỉ dựa vào số lượng API hoặc số bài kiểm thử.**
