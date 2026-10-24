# Ma trận nghiệm thu ERP SUNNY FLEX 3D

**Quy tắc:** chỉ được ký nghiệm thu khi tất cả tiêu chí P0 đạt, có bằng chứng kiểm thử và người chịu trách nhiệm ký. Không được đánh đồng API trả 200 với nghiệp vụ hoạt động đúng.

| Mã | Tiêu chí bắt buộc | Bằng chứng cần nộp | Trạng thái hiện tại |
|---|---|---|---|
| P0-01 | Đăng nhập, đổi mật khẩu, khóa tài khoản, phân quyền mọi vai trò | Bảng quyền + thử truy cập trái phép | Chưa nghiệm thu toàn diện |
| P0-02 | Frontend mọi màn hình V86 được nối API thật, không mock | Bảng đối chiếu màn hình → API → DB và video chạy thử | Chưa đạt |
| P0-03 | Quy trình mua hàng → nhập kho → công nợ → thanh toán | Dữ liệu đầu vào, nhật ký, chứng từ, bút toán đối ứng | Chưa đạt |
| P0-04 | Bán hàng → xuất kho → công nợ → thu tiền → đối soát | Kịch bản đầu-cuối và báo cáo đối chiếu | Chưa đạt |
| P0-05 | Lệnh sản xuất → cấp phát → sản lượng → KCS → tồn kho | Nhật ký ca, QR cuộn, định mức, chênh lệch và bằng chứng | Chưa đạt |
| P0-06 | Ca 6 người: 1 tổ trưởng kiêm KCS + 5 công nhân | Phân ca, phân quyền, dữ liệu thực nghiệm | Chưa đạt |
| P0-07 | KPI 5 kỳ, chỉ xác nhận khi có bằng chứng | Thử KPI đạt giả, không đạt, cảnh báo đỏ/vàng/xanh | Chưa đạt |
| P0-08 | Kế toán: cân đối Nợ/Có, sổ cái, công nợ, lương, thuế, khóa kỳ, đảo bút toán | Bộ dữ liệu kế toán chuẩn và chuyên gia kế toán ký | Chưa đạt |
| P0-09 | AI Agent chạy định kỳ, có giám sát, ghi lý do, không tự ý duyệt giao dịch rủi ro | Nhật ký lịch chạy, kiểm thử sai lệch, cơ chế dừng | Chưa đạt |
| P0-10 | Nhận diện ảnh/PDF và hàng chờ người duyệt khi độ tin cậy thấp | Tệp mẫu, độ chính xác, sai lệch và kết quả kiểm tra | Chưa đạt |
| P0-11 | Thiết bị: cân, camera, bộ đếm, QR, mất kết nối và chống trùng | Bộ giả lập giao thức + thử thiết bị theo hãng | Chưa đạt |
| P0-12 | Bảo mật: OWASP API, kiểm tra phân quyền từng đối tượng, giới hạn tốc độ, bí mật, nhật ký | Báo cáo pentest độc lập và kết quả sửa lỗi | Chưa đạt |
| P0-13 | Sao lưu, khôi phục, nâng cấp DB, kiểm thử tải và phục hồi sự cố | Bản sao lưu + biên bản khôi phục thành công | Chưa đạt |
| P0-14 | Đối chiếu số liệu liên phân hệ và giảm 3% chi phí quản trị/tháng | Báo cáo sai lệch, phương pháp tính và nguồn dữ liệu | Chưa đạt |
| P0-15 | API có tài liệu, phân quyền, lỗi chuẩn, kiểm thử âm và dữ liệu thật | OpenAPI, ma trận API và kết quả tự động | Chưa nghiệm thu toàn diện |

## Quy trình nghiệm thu
1. Đội kỹ thuật chạy `python nghiem_thu/kiem_tra_nghiem_thu.py` trong môi trường thử nghiệm độc lập.
2. Dựng môi trường tách biệt, tạo dữ liệu thử theo các kịch bản nghiệp vụ, không dùng dữ liệu sản xuất thật.
3. Kiểm thử từng P0 theo trình tự, lưu request/response đã che thông tin nhạy cảm, ảnh, video, số liệu đối soát và log.
4. Mọi P0 lỗi hoặc chưa có bằng chứng đều là **KHÔNG ĐẠT**. Không được ký nghiệm thu tổng thể.
5. Đội phát triển sửa, chạy lại kiểm thử hồi quy, kiểm thử an ninh và kiểm thử khôi phục.
6. Giám đốc, trưởng kỹ thuật, kế toán phụ trách và đại diện vận hành ký biên bản sau khi toàn bộ P0 đạt.

**Giới hạn:** 46 bài kiểm thử trước đây chỉ chứng minh phạm vi kiểm thử đã viết; không phải bằng chứng hoàn tất ERP.
