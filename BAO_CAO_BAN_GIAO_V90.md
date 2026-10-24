# SUNNY FLEX 3D V90 — Bàn giao kỹ thuật và giới hạn xác minh

## Đã sửa và kiểm tra
- Frontend chính: xác thực Bearer; giao diện V86 lịch sử thêm đăng nhập Bearer cho các API đang gọi, sửa đường dẫn xuất/nhập kho từ API không tương thích sang `/api/stock/movements` với UUID vật tư và kho được chọn.
- Backend: thêm `GET /api/warehouses`, kiểm tra kho tồn tại trước khi ghi phiếu kho.
- AI hỏi đáp: gọi mô hình ngôn ngữ thật nếu cấu hình `OPENAI_API_KEY`; khi chưa cấu hình báo rõ chưa có, không dựng câu trả lời giả; câu trả lời AI luôn ghi chưa xác minh độc lập.
- Marketing: kiểm tra giá trị ngân sách/chi phí không âm và hữu hạn; thêm nhật ký tạo bản ghi và duyệt chi.
- Bảo toàn giao diện V86 gốc trong `archive`; cảnh báo rõ dữ liệu localStorage V86 là dữ liệu thử, không được coi là dữ liệu thật.
- Bộ kiểm thử: 19/19 đạt trong môi trường thử nghiệm; kiểm tra cú pháp Python thành công.

## Các phần chưa thể nghiệm thu và giao kỹ thuật tiếp tục
1. Các màn hình V86 dùng localStorage chưa chuyển hết sang DB thật; không sử dụng làm nghiệp vụ chính thức. Giao diện vận hành chính là `/index.html`.
2. Hệ thống tự động AI Agent hiện chủ yếu dựa trên quy tắc; không thể tuyên bố tự quyết toán kế toán, tự xác minh mọi bằng chứng, hoặc vận hành 24/7 khi chưa có hạ tầng/khóa/dữ liệu thực và kiểm thử tích hợp.
3. Nhận diện PDF chưa hỗ trợ; nhận diện ảnh cần khóa API và dữ liệu kiểm chứng. Chưa kết nối cân, QR, camera, thiết bị thực.
4. Chưa có kiểm thử trình duyệt thực, tải cao, xâm nhập, phục hồi dữ liệu, phân quyền toàn bộ ma trận và đối chiếu số liệu thực địa.
5. Kế toán đầy đủ (bút toán kép, công nợ, thu tiền, đối chiếu ngân hàng, báo cáo tài chính) chưa được triển khai hoàn chỉnh; không được dùng thay hệ thống kế toán được phê duyệt.
6. Tác vụ nền mặc định tắt, cần cấu hình `SUNNY_ENABLE_WORKER=1`, kiểm tra khóa AI, cấu hình môi trường triển khai và theo dõi hàng đợi lỗi.
7. Giao diện V86 lịch sử vẫn có dữ liệu mẫu và các chức năng giả lập; tuyệt đối không xem như chứng từ vận hành.
8. Cần kiểm tra bảo mật thực tế, giới hạn đăng nhập, sao lưu, HTTPS, nhật ký tập trung, quy trình khôi phục và cơ chế phê duyệt trước khi mở mạng công cộng.

## Kiểm thử
`SUNNY_ADMIN_PASSWORD='mật khẩu kiểm thử >=12 ký tự' python -m pytest -q`
Kết quả phiên chạy: **19 passed**. Đây là kiểm thử tự động hiện có, không phải xác nhận toàn hệ thống không lỗi.

## Chạy thử
`pip install -r requirements.txt`
Tạo `.env` từ `.env.example`, đặt `SUNNY_ADMIN_PASSWORD` bằng mật khẩu riêng mạnh; cấu hình biến môi trường theo hệ điều hành; khởi chạy `uvicorn backend.main:app --host 127.0.0.1 --port 8000`; mở `http://127.0.0.1:8000/index.html`.

## Quy tắc nghiệm thu
Chỉ nghiệm thu khi chức năng nghiệp vụ đã được kiểm thử đầu cuối bằng dữ liệu thật, có bằng chứng, có kiểm thử phân quyền, có phương án sao lưu/phục hồi và chữ ký người chịu trách nhiệm. Không suy ra từ số lượng API hay số bài kiểm thử đạt.
