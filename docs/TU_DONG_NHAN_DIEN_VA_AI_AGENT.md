# V86 – Luồng tự động ảnh và 10 Agent

## Vận hành thực tế
1. Điện thoại tải ảnh JPEG/PNG qua `POST /api/documents/intake` (Bearer token). PDF được lưu nhưng OCR PDF **chưa hỗ trợ**.
2. Máy chủ tạo hàng chờ `api_jobs`, nhận diện bằng Vision API khi có `OPENAI_API_KEY` và `SUNNY_ENABLE_WORKER=1`.
3. Trích xuất loại chứng từ, trường dữ liệu, độ tin cậy, cảnh báo; lưu `extraction_results` và trạng thái `review_required`.
4. Người có quyền kiểm tra bằng `GET /api/documents/{id}/extraction`, xác minh qua `POST /api/documents/{id}/review`.
5. Chưa tự động hạch toán, tạo phiếu nhập/xuất, ghi nhận doanh thu hoặc chi tiền từ ảnh; các giao dịch phải qua API nghiệp vụ, kiểm tra khóa ngoại, quyền và chống trùng.
6. Bộ phân tích 10 Agent theo luật SQL chạy mỗi 300 giây (cấu hình được); kết quả lưu `agent_evaluations`. **Chưa phải 10 LLM Agent độc lập.**

## Cấu hình
`pip install -r requirements.txt`, đặt `SUNNY_ADMIN_PASSWORD` >= 12 ký tự; đặt `OPENAI_API_KEY`; `SUNNY_ENABLE_WORKER=1`; chạy `uvicorn backend.main:app --host 127.0.0.1 --port 8765 --workers 1`. Cần kết nối Internet cho Vision API, chi phí theo nhà cung cấp.

## Luồng dữ liệu và quyền
`documents` (tệp gốc, SHA-256) → `api_jobs` → `extraction_results` (JSON trích xuất) → xác minh → API nghiệp vụ → bảng đích → `audit_log` → `agent_evaluations` → dashboard. Trạng thái thất bại phải kiểm tra thủ công, không tự nhận là đã nhập sổ.

## Cần kỹ thuật triển khai trước nghiệm thu
- Hàng chờ bền vững với retry, lease, dead-letter và đa tiến trình; hiện worker một tiến trình, job lỗi được đánh dấu failed.
- Phân quyền duyệt theo loại chứng từ và phạm vi phòng ban, chống truy cập chéo; chính sách dữ liệu nhạy cảm và lưu trữ mã hóa.
- Bộ chuyển PDF nhiều trang, đọc QR/camera/cân qua adapter thiết bị, đối chiếu nhà cung cấp, số hóa đơn và tổng tiền.
- Giao diện V86 gọi API thật thay cho localStorage; ánh xạ chứng từ đã duyệt vào giao dịch chuẩn theo cơ chế idempotency.
- 10 Agent chuyên trách có lịch, công cụ, điều kiện kích hoạt, giám sát, xử lý lỗi và kiểm định kết quả; hiện chỉ có phân tích SQL định kỳ.
- KPI 5 kỳ và giảm 3% chi phí dựa trên số liệu đã đối soát, không giả định dữ liệu thiếu là 0.
- Backup, phục hồi, TLS, giám sát, nhật ký bảo mật và kiểm thử end-to-end trên Android.
