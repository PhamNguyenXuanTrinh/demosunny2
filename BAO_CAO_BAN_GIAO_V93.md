# SUNNY FLEX 3D V93 – Bàn giao mã nguồn

## Thay đổi được kiểm chứng
1. Giữ nguyên bản HTML V86 trong archive; chuyển /legacy.html sang giao diện có xác thực để chặn dữ liệu thử từ localStorage được hiểu nhầm là dữ liệu vận hành. **Chưa chuyển đổi 100% chức năng V86.**
2. Thêm khóa đăng nhập sau 5 lần sai trong 15 phút, trạng thái lưu DB, có kiểm thử.
3. Cập nhật thông báo PDF và thêm kiểm thử bảo vệ dữ liệu giả.
4. Chạy lại toàn bộ bộ kiểm thử hiện có và kiểm thử bổ sung: **28/28 đạt**.
5. Cung cấp API list, frontend, backend, schema, hướng dẫn, các bản giao diện lịch sử, báo cáo giới hạn.

## Cần kỹ thuật triển khai và nghiệm thu
- Hoàn thiện từng màn hình nghiệp vụ V86 còn thiếu trên giao diện mới, test end-to-end với dữ liệu kiểm thử có chứng từ.
- Driver thiết bị theo model, firmware, giao thức và địa chỉ kết nối thực tế; hiện có gateway HTTP nhận dữ liệu, **không có driver PLC/RS485/Modbus/camera hãng được nghiệm thu**.
- Nghiệp vụ kế toán đầy đủ theo quy định hiện hành; hiện mới có phần sổ bút toán và bảng cân đối.
- OCR ảnh/PDF cần khóa AI và thử bộ chứng từ thực tế; không được tự động hạch toán nếu thiếu xác minh.
- Agent hiện có quy tắc phân tích và worker tùy chọn, chưa đạt yêu cầu tự động toàn diện.
- Kiểm thử thâm nhập độc lập, tải cao, sao lưu/khôi phục và nghiệm thu vận hành trên hạ tầng thật.

**Không được công bố V93 là sản phẩm hoàn thiện hay không còn lỗi.**
