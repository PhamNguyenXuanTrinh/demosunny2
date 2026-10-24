# Hướng dẫn triển khai thử nghiệm

1. Python 3.11 trở lên. `pip install -r requirements.txt`
2. Đặt `SUNNY_ADMIN_PASSWORD` tối thiểu 12 ký tự; không gửi mật khẩu qua chat.
3. `uvicorn backend.main:app --host 127.0.0.1 --port 8000`
4. Mở `http://127.0.0.1:8000/api/docs` để kiểm tra danh sách API.
5. Chạy `python -m pytest -q`.
6. Dữ liệu vận hành phải được sao lưu và bảo vệ riêng. Không bật public internet trước kiểm thử bảo mật.

Đọc `BAO_CAO_V88.md` trước khi nghiệm thu.
