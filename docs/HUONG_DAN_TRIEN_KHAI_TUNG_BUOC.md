# Hướng dẫn kỹ thuật nhận bàn giao

## 1. Cài đặt
- Python 3.12 hoặc 3.13; tạo môi trường ảo: `python -m venv .venv`; kích hoạt môi trường; `pip install -r requirements.txt`.
- Sao chép `.env.example` thành `.env`; tạo `SUNNY_ADMIN_PASSWORD` riêng tối thiểu 12 ký tự; không đưa mật khẩu vào Git.
- Cấu hình `SUNNY_DB_PATH` tới ổ lưu trữ có sao lưu. SQLite chỉ phù hợp triển khai nhỏ/đơn tiến trình; cân nhắc PostgreSQL trước khi chạy đa người dùng hoặc nhiều máy.
- Khởi động: `uvicorn backend.main:app --host 127.0.0.1 --port 8000 --workers 1`.
- Truy cập `/api/docs` để xem OpenAPI, `/api/health` để kiểm tra khởi động.
- Chạy thử `python -m pytest -q`.

## 2. Dữ liệu và AI
- Dùng dữ liệu mô phỏng trong cơ sở dữ liệu kiểm thử riêng; không trộn với dữ liệu sản xuất.
- Muốn xử lý ảnh/PDF: cấp `OPENAI_API_KEY` trong môi trường an toàn. Không cấu hình thì không được tự nhận đã nhận diện.
- Worker mặc định tắt. Chỉ bật `SUNNY_ENABLE_WORKER=1` với **một** tiến trình, sau khi kiểm tra quyền và giám sát lỗi.
- Kết nối thiết bị: thu thập model, giao thức, sơ đồ thanh ghi, đơn vị đo, tốc độ truyền, xác thực và dữ liệu mẫu; viết adapter tương ứng; không được khẳng định đã tương thích máy thật.

## 3. Nghiệm thu trước khi chạy nhà máy
- Đối chiếu tất cả màn hình V86 với nghiệp vụ thật, lập ma trận từng nút/luồng/API.
- Đối soát tồn kho, kế toán kép, chứng từ, khóa kỳ, công nợ, chi phí, lương và thuế với kế toán có chứng chỉ.
- Kiểm tra phân quyền theo từng vai trò, thử lỗi mất mạng, ghi trùng, khôi phục sao lưu, tải lớn, kiểm thử xâm nhập.
- Thử kết nối trực tiếp cân, camera, máy đếm mét, mã QR và hệ thống sản xuất.
- Chỉ nghiệm thu khi có biên bản và bằng chứng cho từng mục.
