# Cổng nhận dữ liệu thiết bị V92

- `POST /api/devices/readings`: tiếp nhận số đo qua HTTPS, xác thực `X-Device-Token` riêng cho từng thiết bị, chống gửi lặp bằng `request_id`, từ chối thay đổi nội dung của yêu cầu đã ghi. Trạng thái `device_reported` **không** phải số liệu đã đối chiếu độc lập.
- `GET /api/devices/readings`: truy vấn dữ liệu theo vai trò. Chỉ giám đốc, kế toán, thủ kho, tổ trưởng và bảo trì có quyền xem.
- Các loại: `scale_kg`, `meter_m`, `power_kwh`, `camera_event`, `humidity_pct`, `temperature_c`. Kết nối camera RTSP, PLC, Modbus, đầu cân serial, đầu đếm mét **chưa có trình điều khiển**. Cần adapter riêng của từng hãng/thiết bị để chuyển dữ liệu về API trên.
- Cấu hình `SUNNY_DEVICE_TOKENS_JSON` chứa ánh xạ ID thiết bị -> token dài ít nhất 24 ký tự, ví dụ `{"SCALE01":"REPLACE_WITH_A_LONG_RANDOM_SECRET"}`. Không ghi token thật vào kho mã nguồn.
- Cần HTTPS qua proxy, tường lửa, quản lý và xoay vòng token, giám sát, sao lưu. Không đưa trực tiếp SQLite ra Internet.
- API có kiểm tra giới hạn số đo, thời gian +/-24 giờ, độ dài dữ liệu, phân quyền đọc, chống phát lại mã yêu cầu. Chưa có kiểm thử xâm nhập chuyên nghiệp, kiểm tra tải, quét phụ thuộc và quản lý bí mật tập trung.
