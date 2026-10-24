# SUNNY FLEX 3D V91 – Báo cáo thực hiện và kiểm thử

## Đã sửa trực tiếp trên mã nguồn
- Backend nhận diện PDF: chuyển tối đa 10 trang PDF thành ảnh bằng PyMuPDF, gửi cùng một yêu cầu trích xuất AI; kết quả vẫn phải đối chiếu chứng từ, không tự xác nhận.
- Bổ sung sổ nhật ký kế toán hai bên Nợ/Có (`POST /api/accounting/journal`) với kiểm tra cân đối, chống ghi trùng request_id, nhật ký truy cập; và bảng cân đối phát sinh (`GET /api/accounting/trial-balance`). Đây là nền tảng kế toán, chưa phải phần mềm kế toán hoàn chỉnh đáp ứng chế độ kế toán Việt Nam.
- Bổ sung `POST /api/evidence/verify-production/{batch_id}` kiểm tra tính nhất quán số liệu và trả trạng thái chưa xác minh nếu thiếu ảnh, cân và biên bản QC; không tự đánh dấu hoàn thành.
- Sửa lỗi thứ tự đăng ký route: API mới phải được đăng ký trước StaticFiles gắn tại `/` (trước khi sửa bị HTTP 405).
- Thêm 3 bài kiểm thử kế toán, bằng chứng và chuyển PDF; tổng 22/22 đạt trong môi trường kiểm thử cục bộ.

## Chưa hoàn tất / không được phép tuyên bố đã xong
- Đồng bộ mọi thao tác của giao diện V86 cũ với Backend: chưa có kiểm thử toàn diện và còn phụ thuộc luồng cũ.
- Hạch toán thuế, công nợ, lương, giá thành, kết chuyển và báo cáo theo quy định: chưa hoàn chỉnh.
- AI Agent tự trị cho tất cả phòng ban và xử lý ngoại lệ đa bước: chưa hoàn chỉnh. Worker cần cấu hình `SUNNY_ENABLE_WORKER=1`; việc đánh giá theo quy tắc hiện có không phải AI tự trị toàn diện.
- Nhận diện PDF mới được kiểm thử với phản hồi AI giả lập (mock), chưa có kiểm thử API OpenAI thật.
- Camera, đồng hồ mét, cân, QR, thiết bị nhà máy: chưa có giao thức/thiết bị thật để thử; phải tích hợp adapter theo từng thiết bị.
- Kiểm thử xâm nhập, tải đồng thời, bảo mật toàn diện và kiểm thử đầu cuối toàn bộ giao diện: chưa thực hiện.

## Kiểm thử
Lệnh: `python -m pytest -q` trong thư mục gốc; kết quả: **22 passed**. Các kiểm thử dùng cơ sở dữ liệu SQLite tạm và mô phỏng API AI; không xác nhận sản xuất thực tế.

## Cài đặt
`python -m pip install -r requirements.txt`
`export SUNNY_ADMIN_PASSWORD='mật khẩu riêng tối thiểu 12 ký tự'`
`python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`
Mở `/` cho frontend và `/api/docs` cho OpenAPI. Không đưa mật khẩu/khóa thật vào ZIP.

## Nguyên tắc nghiệm thu
Không gắn nhãn 'hoàn tất' cho một nghiệp vụ nếu không có bằng chứng kiểm thử và dữ liệu được đối chiếu. V91 là mã nguồn phát triển được cải tiến, **chưa đạt nghiệm thu triển khai chính thức**.
