# SUNNY FLEX 3D V88 — KẾT QUẢ KIỂM TRA

Đây là mã nguồn đang phát triển, **KHÔNG ĐỦ CƠ SỞ XÁC NHẬN CHỈ CÒN THIẾU ĐIỀU KIỆN THỰC TẾ**.

## Sửa trong V88
- Thay FastAPI `on_event(startup)` đã lỗi thời bằng lifespan.
- Khắc phục lỗi tạo bảng `marketing_leads` không khớp schema chính.
- Giữ nguyên giao diện V86 gốc và API hiện có.
- Thêm kiểm thử tạo lead marketing với cơ sở dữ liệu thực trong môi trường kiểm thử.

## Chưa hoàn thành / chưa nghiệm thu
- Giao diện V86 di sản chưa chuyển toàn bộ sang API xác thực, chưa kiểm thử luồng đầu cuối.
- AI ngôn ngữ `/api/ask` chưa triển khai thực, AI Agent quy tắc chưa có tự chủ đa tác vụ đầy đủ.
- Hạch toán kế toán kép, lương, đối soát, giá thành theo lô chưa được chứng minh.
- Camera, cân điện tử, QR, PDF OCR và tự động hóa từ thiết bị chưa tích hợp thực.
- Cần kiểm thử bảo mật, hiệu năng, sao lưu/khôi phục, quyền theo từng bản ghi trước triển khai.

**Không dùng cho dữ liệu tài chính hoặc vận hành nhà máy chính thức.**
