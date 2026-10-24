# Backend API — chạy thử

## Khởi động
```bash
python -m pip install -r requirements.txt
export SUNNY_ADMIN_PASSWORD='mat-khau-dai-va-duy-nhat'
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8765
```
Windows: đặt biến môi trường `SUNNY_ADMIN_PASSWORD`, chạy `CHAY_WINDOWS.bat`.

- Swagger API: `http://127.0.0.1:8765/api/docs`
- Giao diện V86 hiện trạng: `http://127.0.0.1:8765/`
- Đăng nhập API: `POST /api/auth/login`, lấy `access_token`, gửi `Authorization: Bearer TOKEN`.

## Các API đã lập trình
| Method | Endpoint | Mục đích |
|---|---|---|
| GET | `/api/health` | Tình trạng dịch vụ |
| POST | `/api/auth/login` | Đăng nhập và lấy Bearer token |
| GET | `/api/auth/me` | Người đăng nhập và vai trò |
| GET/POST | `/api/v1/customers` | Khách hàng |
| GET/POST | `/api/v1/sales_orders` | Đơn hàng (phần đầu đơn) |
| GET/POST | `/api/v1/employees` | Hồ sơ nhân sự cơ bản |
| GET/POST | `/api/v1/assets` | Sổ tài sản cơ bản |
| GET/POST | `/api/v1/marketing_campaigns` | Chiến dịch |
| GET/POST | `/api/v1/inventory_items` | Danh mục vật tư |
| GET/POST | `/api/v1/production_batches` | Lô sản xuất |
| GET/POST | `/api/v1/incidents` | Sự cố |
| GET/POST | `/api/v1/duty_catalog` | Danh mục nhiệm vụ |
| GET | `/api/stock/summary` | Tồn kho theo sổ biến động, cảnh báo 40% |
| POST | `/api/stock/movements` | Nhập/xuất, chống trùng, chặn âm kho |
| POST | `/api/purchases/commit` | Khoản mua, chống ghi trùng, chờ đối soát |
| GET | `/api/costs/3-percent` | Tổng hợp chi phí từ sổ chuẩn |
| GET | `/api/dashboard` | Số liệu theo quyền |
| POST | `/api/documents/intake` | Tiếp nhận ảnh/PDF, đưa vào hàng chờ xử lý |
| POST | `/api/agents/run` | Chạy 10 bộ phân tích quy tắc trên SQLite |
| GET | `/api/agents/history` | Lịch sử phân tích |
| GET | `/api/audit` | Nhật ký giám đốc |

## Ví dụ đăng nhập và tạo khách
```bash
curl -X POST http://127.0.0.1:8765/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"YOUR_PASSWORD"}'
# Dùng token trả về:
curl http://127.0.0.1:8765/api/v1/customers -H 'Authorization: Bearer YOUR_TOKEN'
```

## Quan trọng
- HTML V86 hiện trạng vẫn còn `localStorage`; chưa chuyển toàn bộ lời gọi sang API mới. Đội kỹ thuật phải thay nguồn đọc/ghi của từng màn hình bằng endpoint có xác thực.
- Bộ 10 Agent ở đây **là quy tắc truy vấn SQLite**, không phải 10 LLM độc lập; chưa có khóa mô hình và chưa có bộ lập lịch tự chạy trong bản API mới.
- Chưa có xử lý OCR ảnh thật. Upload chỉ đưa tài liệu vào hàng chờ.
- Chưa có HTTPS, khóa tài khoản theo lần đăng nhập sai, CSRF/cookie nếu chuyển sang session, quota AI bền vững, hay cơ chế triển khai Internet an toàn.
- Cần triển khai xác thực người dùng và quyền tới từng trường nhạy cảm; các API CRUD tổng quát hiện là bản nền kỹ thuật.
