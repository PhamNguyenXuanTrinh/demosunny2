# SUNNY FLEX 3D – Bàn giao mã nguồn V100 (25/10/2026)

## Phạm vi thực tế
Đây là **mã nguồn ERP đang phát triển**, không phải ERP đã nghiệm thu vận hành. Không có bằng chứng để khẳng định tất cả nghiệp vụ liên thông, kế toán pháp định, thiết bị theo từng hãng và AI Agent tự chủ đã hoàn thành.

## Thay đổi V100
- Thêm 6 API đối soát đọc dữ liệu thật từ SQLite: `/api/erp/integrity/dashboard`, `/production-balance`, `/journal-balance`, `/unverified-production`, `/pending-approvals`, `/missing-source-documents`.
- Các API kiểm tra phân quyền, giới hạn truy vấn và không tự xác nhận chứng cứ khi chưa có.
- Thêm kiểm thử HTTP yêu cầu xác thực và truy cập đã đăng nhập; toàn bộ 46 bài kiểm thử đạt trong môi trường thử nghiệm.
- Giữ mã nguồn giao diện V86 và toàn bộ Backend/Database/API hiện có trong V99.

## Việc kỹ thuật phải đánh giá trước khi triển khai
1. Kiểm thử quy trình liên thông đơn hàng → xuất kho → sản xuất → ghi nhận kế toán, kiểm soát giao dịch đồng thời.
2. Xây dựng/kiểm tra hệ thống sổ sách kế toán, báo cáo thuế và tiền lương đúng chế độ áp dụng ở Việt Nam.
3. Chuyển đổi từng chức năng giao diện V86 sang API và kiểm thử trên trình duyệt.
4. Hoàn thiện AI Agent với phân quyền công cụ, phê duyệt hành động rủi ro, cơ chế lặp và truy vết.
5. Đối chiếu giao thức thực của cân, camera, PLC, QR, kiểm thử phần cứng tại xưởng.
6. Rà soát bảo mật chuyên sâu (OWASP), sao lưu/phục hồi, phân tách quyền, kiểm thử tải và vận hành.

## Cách kiểm tra
`SUNNY_ADMIN_PASSWORD=<mật khẩu thử nghiệm tối thiểu 12 ký tự> python -m pytest -q`

Không gửi khóa thật. Kiểm tra `DANH_SACH_API_V100.json`, `MANIFEST_V100.json` và `KET_QUA_KIEM_THU_V100.txt`.
