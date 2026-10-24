# SUNNY FLEX 3D — BỘ BÀN GIAO HỢP NHẤT

Đây là MỘT gói mã nguồn hiện có để đội kỹ thuật tiếp nhận, KHÔNG phải chứng nhận ERP hoàn chỉnh.

- Giao diện gốc: `public/v86.html`; trang hiện tại có Tổng kết ngày: `public/index.html`. Không thay giao diện gốc khi chưa duyệt.
- Giao diện tích hợp API riêng: `public/app.html`.
- Backend: `backend/`; cơ sở dữ liệu: `database/`; kiểm thử: `tests/`; hướng dẫn: `HUONG_DAN_BAN_GIAO.md`.
- Danh mục API: `docs/API_KIEM_KE_THUC_TE.json`, `DANH_SACH_API.json`; số kiểm kê hiện tại 121 cặp phương thức/đường dẫn, KHÔNG phải 121 quy trình đã nghiệm thu.
- AI Agent: 10 báo cáo quy tắc, chưa phải hệ AI Agent tự chủ đầy đủ.
- Kiểm thử gần nhất: 47 đạt, 1 lỗi bảo toàn giao diện (xem `KET_QUA_KIEM_THU_HIEN_TAI.txt`).
- Kiểm toán kỹ thuật và những phần chưa hoàn thành: `BAO_CAO_KIEM_TOAN_AI_AGENT_API.md`.

## Chạy thử
`pip install -r requirements.txt`
`export SUNNY_ADMIN_PASSWORD='your-long-secret-password'`
`python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`
`python -m pytest -q`

Không đưa lên internet hoặc dùng dữ liệu tài chính thật khi chưa hoàn thành kiểm thử bảo mật và nghiệm thu nghiệp vụ.
