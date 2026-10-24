# Báo cáo kiểm tra V97 — 25/10/2026

## Đã sửa và có bằng chứng
- Sửa thứ tự đăng ký `/api/resources/{resource}` trước mount `/` của Frontend. Trước đó mount bắt mọi URL và khiến các API resource không thể truy cập.
- Kiểm thử HTTP thực tế xác minh API trả JSON và từ chối khi thiếu token.
- Khóa sửa trực tiếp `payroll_drafts` qua CRUD tổng quát, tránh ghi lương không có quy trình phê duyệt.
- Từ chối các trường nhạy cảm của CRUD tổng quát.
- Bộ kiểm thử chạy lại: 41 passed.

## Phân biệt mức độ hoàn thành
- Có mã nguồn frontend, backend, SQLite schema, test, API docs.
- Chưa được chứng minh ERP hoàn chỉnh; chưa kiểm thử toàn bộ quy trình nghiệp vụ đầu-cuối, sổ sách thuế Việt Nam, AI tự động toàn diện, máy móc thực tế, bảo mật chuyên sâu trên máy chủ.
- Không được lấy số lượng route OpenAPI hay số lượng file làm tiêu chí nghiệm thu.

## Điều kiện nghiệm thu tối thiểu
1. Kiểm thử mua hàng → nhập kho → cấp phát → sản xuất → QC → thành phẩm → bán hàng → thu tiền → bút toán → báo cáo.
2. Đối soát nhập xuất tồn, công nợ, cân đối kế toán; không ghi trùng, không âm tồn, không sai phân quyền.
3. Đầy đủ bảng lương, khấu trừ, phê duyệt, kỳ kế toán, chứng từ; xác nhận chuẩn kế toán Việt Nam bởi kế toán có chuyên môn.
4. AI Agent phải có nguồn dữ liệu, bằng chứng, giới hạn hành động, phê duyệt giao dịch và nhật ký; không tự đánh dấu KPI hoàn thành.
5. Thử nghiệm với dữ liệu mô phỏng toàn bộ; sau đó thử trên thiết bị thật và hạ tầng triển khai.

## Khuyến nghị kỹ thuật
- SQLite hiện tại thích hợp phát triển/thử nghiệm, cân nhắc PostgreSQL và migration versioned trước vận hành đa người dùng.
- Không dùng tài khoản/mật khẩu thử nghiệm trong sản xuất.
