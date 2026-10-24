# SUNNY FLEX 3D – Bàn giao mã nguồn V94

## Mục đích
Bộ mã nguồn để kỹ thuật viên tiếp tục triển khai và kiểm thử độc lập. **Không khẳng định đã hoàn thiện toàn bộ ERP hoặc không còn lỗi.** Không cần dữ liệu sản xuất thật để chạy các bài kiểm thử tự động; kiểm thử với thiết bị thật cần giao thức của nhà sản xuất.

## Thành phần
- `public/`: giao diện kết nối API, bản lưu giao diện V86 và trang cũ được chuyển hướng.
- `backend/`: FastAPI, xác thực, cơ sở dữ liệu, nghiệp vụ, AI Agent dựa trên quy tắc, cổng dữ liệu thiết bị, xử lý chứng từ, kế toán bút toán, kiểm tra bằng chứng.
- `database/schema_target.sql`: cấu trúc dữ liệu gốc; các bảng mở rộng khởi tạo qua `backend/db.py`, `backend/devices.py`, `backend/operations.py`, `backend/compat.py`.
- `tests/`: bộ kiểm thử tự động.
- `docs/`: mô tả API, database, tích hợp và bảo mật.
- `DANH_SACH_API_V94.json`: toàn bộ đường dẫn OpenAPI từ ứng dụng hiện tại.
- `KET_QUA_KIEM_THU_V94.txt`: kết quả chạy pytest thực tế.

## Khởi chạy trên máy mới
1. Python 3.11+; `python -m venv .venv`; kích hoạt môi trường.
2. `pip install -r requirements.txt`.
3. Đặt `SUNNY_ADMIN_PASSWORD` tối thiểu 12 ký tự, không dùng giá trị ví dụ trong môi trường thật.
4. `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`.
5. Truy cập `http://127.0.0.1:8000` và `/api/docs`.
6. Chạy `python -m pytest -q` với mật khẩu môi trường đã cấu hình.
7. Khi triển khai công khai: HTTPS qua reverse proxy, tách database và sao lưu, quản lý secrets, log tập trung, đánh giá bảo mật độc lập.

## Các vấn đề chưa thể xác nhận hoàn thành
- Giao diện V86 gốc có nhiều chức năng chỉ được lưu để đối chiếu; giao diện mới **không tương đương 100%** V86. Cần bản đồ từng chức năng và kiểm thử thao tác trên trình duyệt.
- Chưa có trình điều khiển cho từng PLC/cân/camera cụ thể; đã có API tiếp nhận dữ liệu thiết bị và bảng ánh xạ, nhưng phải tích hợp giao thức thực tế.
- Agent dựa trên quy tắc và lịch chạy; chưa phải AI Agent tự chủ có thể kiểm tra và kết luận mọi nghiệp vụ. Phải cấu hình worker và nhà cung cấp mô hình AI nếu dùng nhận diện.
- Kế toán chỉ có bút toán cân đối, sổ cái, bảng cân đối; chưa có đầy đủ nghiệp vụ thuế, công nợ, lương, báo cáo tài chính theo chế độ kế toán Việt Nam.
- Chứng từ tải lên chưa tự chứng minh tính xác thực; bằng chứng được gắn không đồng nghĩa QC đạt.
- Kiểm thử hiện tại là tự động ở mức API và một số quy tắc; chưa có pentest độc lập, kiểm thử tải, khôi phục thảm họa, kiểm thử trình duyệt thực, nghiệm thu dây chuyền.

## Nguyên tắc bàn giao
Không lưu mật khẩu hoặc khóa API thật trong ZIP. Không được coi dữ liệu mô phỏng là dữ liệu thực. Không đánh dấu hoàn thành thủ công thay cho chứng cứ. Không kết luận 'chỉ cần cài đặt là vận hành' khi chưa hoàn thành các mục trên.
