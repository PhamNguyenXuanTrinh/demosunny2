# SUNNY FLEX 3D V92 – Báo cáo bàn giao mã nguồn và kết quả xác minh

## Phạm vi thực hiện
- Kế thừa **toàn bộ** tệp mã nguồn V91, bao gồm giao diện V86 gốc bất biến, giao diện vận hành kết nối cơ sở dữ liệu, Backend FastAPI, cấu trúc SQLite, API, AI Agent theo quy tắc, nhận diện ảnh/PDF qua dịch vụ AI khi cấu hình, kế toán bút toán Nợ/Có, kho, marketing, sản xuất, KPI.
- Bổ sung cổng dữ liệu thiết bị thực (API tiếp nhận), xác thực token theo thiết bị, ngăn gửi lặp và dữ liệu thay đổi, hạn chế giá trị bất thường, quyền đọc theo vai trò.
- Bổ sung HTTP security headers và kiểm thử bảo vệ đường dẫn mã nguồn/cơ sở dữ liệu, kiểm tra hợp đồng API giao diện chính.

## Giới hạn không được che giấu
1. **Giao diện V86 gốc vẫn là giao diện mô phỏng**, không được đồng bộ tất cả module với Backend. Giao diện vận hành `/index.html` sử dụng dữ liệu cơ sở dữ liệu; không lấy số liệu V86 mẫu làm kết quả thực.
2. **Thiết bị**: cổng nhận số đo đã có và kiểm thử, nhưng trình điều khiển PLC, camera, cân, công tơ theo hãng và chứng minh nguồn gốc dữ liệu thực địa chưa có. Không có thiết bị vật lý để thử.
3. **Bảo mật**: kiểm thử chức năng phân quyền, token và đường dẫn nhạy cảm; **chưa** có kiểm thử xâm nhập độc lập, đánh giá OWASP toàn diện, kiểm thử tải, triển khai HTTPS và hệ thống sao lưu/khôi phục thực địa.
4. **AI Agent**: quy tắc tự chạy khi bật worker, AI hỏi đáp/nhận diện cần khóa dịch vụ; chưa có cơ chế tác vụ tự động toàn diện đủ chứng cứ để nghiệm thu kế toán và QC.
5. **Kế toán**: bút toán cân đối cơ bản chưa thay thế hệ thống kế toán theo chuẩn và quy định Việt Nam.
6. Không tuyên bố phần mềm đã sẵn sàng vận hành sản xuất chỉ từ kết quả pytest.

## Cách thử
`python -m pip install -r requirements.txt`
`SUNNY_ADMIN_PASSWORD='mật_khẩu_thử_đủ_dài' python -m pytest -q`
`SUNNY_ADMIN_PASSWORD='mật_khẩu_mạnh_riêng' python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`
Truy cập http://127.0.0.1:8000/ và tài liệu http://127.0.0.1:8000/api/docs.

## Bàn giao kỹ thuật
- Không đưa mật khẩu thật hoặc khóa API thật vào ZIP.
- Tham khảo `docs/THIET_BI_VA_BAO_MAT_V92.md`, `docs/API_HUONG_DAN.md`, `docs/CAU_TRUC_DATABASE_VA_QUAN_HE.md`.
- Cần kiểm tra độc lập mọi API và giao diện theo vai trò, kiểm tra đối soát chứng từ, kiểm thử khôi phục dữ liệu, tải thực tế, an toàn bảo mật và thử thiết bị trước nghiệm thu.
