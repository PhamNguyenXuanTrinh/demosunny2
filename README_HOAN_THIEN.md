# SUNNY V86 – Bản tích hợp backend có thể chạy

## Chạy thử
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows; Linux: source .venv/bin/activate
pip install -r requirements.txt
# Cấu hình SUNNY_ADMIN_PASSWORD tối thiểu 12 ký tự trong môi trường
uvicorn backend.main:app --host 127.0.0.1 --port 8765
```
Truy cập `http://127.0.0.1:8765/` (giao diện kết nối API thật), `/legacy.html` (V86 cũ), `/api/docs` (Swagger).

Bật xử lý nền: `SUNNY_ENABLE_WORKER=1`; muốn nhận diện ảnh thật phải có `OPENAI_API_KEY`. Worker hiện không xử lý PDF. Không dùng tài khoản mặc định yếu.

## Mức độ hoàn thành
Có: API xác thực, CRUD một số phân hệ, kho có kiểm tra tồn, hàng chờ chứng từ, nhận diện JPEG/PNG nếu cấu hình, phân tích quy tắc định kỳ, dashboard API mới.
Chưa có: di trú toàn bộ 1MB giao diện cũ sang API, tự động phân loại và ghi sổ kế toán, 10 agent LLM tự chủ, camera/cân tích hợp, phân quyền đầy đủ ở mức bản ghi/ca, backup production, thử nghiệm vận hành thực. Không tuyên bố nghiệm thu toàn bộ.
