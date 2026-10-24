# Bàn giao kiểm thử V93 - ranh giới kỹ thuật

- Giao diện V86 gốc không còn được dùng để nhập số liệu vận hành; /legacy.html chuyển hướng về /index.html. Bản gốc giữ trong archive. Đây là biện pháp ngăn dữ liệu trình duyệt giả, **không phải chuyển đổi 100% chức năng V86**.
- Gateway /api/devices/readings nhận dữ liệu HTTP từ thiết bị có token, chống trùng và kiểm tra giới hạn. Driver giao thức hãng/PLC/Modbus/RS485/camera cần tài liệu và kiểm thử thực tế; chưa có driver hãng được chứng minh.
- Nhận diện ảnh/PDF phụ thuộc khóa AI và worker. Có hàng chờ, kết quả cần duyệt; chưa xác nhận độ chính xác OCR trên dữ liệu nhà máy.
- Agent có luật kiểm tra cơ sở dữ liệu, chưa có quyền tự động kết chuyển kế toán hay phê duyệt nghiệp vụ không có chứng cứ.
- Kế toán có sổ bút toán cân bằng, không phải hệ thống kế toán Việt Nam hoàn chỉnh (VAT, công nợ, ngân hàng, báo cáo thuế, khóa sổ...).
- Kiểm thử bảo mật tự động không thay thế đánh giá thâm nhập độc lập; không khẳng định hết lỗ hổng.
- Cần kỹ thuật: bổ sung chức năng V86 còn thiếu vào giao diện dữ liệu thật, tích hợp driver theo tài liệu thiết bị, đánh giá bảo mật triển khai, xác nhận nghiệp vụ kế toán và kiểm thử đầu cuối.
