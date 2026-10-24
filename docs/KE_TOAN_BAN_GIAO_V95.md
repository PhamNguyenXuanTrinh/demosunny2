# SUNNY FLEX 3D – Bàn giao kế toán mở rộng V95

## Phần đã lập trình và kiểm thử
- Sổ nhật ký Nợ/Có cân đối, sổ cái, bảng cân đối phát sinh.
- Danh mục tài khoản (có kiểm tra trùng mã), đối tượng khách hàng/nhà cung cấp.
- Công nợ phải thu/phải trả; theo dõi hạn thanh toán, quá hạn, thanh toán từng phần; từ chối thanh toán vượt dư.
- Sổ theo dõi VAT đầu vào/đầu ra; kiểm tra số tiền thuế so với thuế suất; tổng hợp theo kỳ.
- Khóa kỳ kế toán bởi giám đốc; ngăn tạo mới công nợ, VAT và bút toán nhật ký vào kỳ đã khóa.
- Báo cáo quản trị doanh thu, chi phí, kết quả theo khoảng ngày; xác thực và phân quyền.
- Nhật ký thao tác tạo tài khoản, đối tượng, công nợ, thanh toán, VAT, khóa kỳ.

## Các thành phần KHÔNG được tuyên bố đã hoàn chỉnh
- Tự động định khoản từ tất cả nghiệp vụ bán hàng, mua hàng, kho, ngân hàng, tài sản, lương; hiện công nợ và thanh toán KHÔNG tự ghi bút toán, để tránh hạch toán sai.
- Hệ thống chứng từ, hóa đơn điện tử, ngân hàng, đối chiếu sao kê, quản lý tiền mặt đầy đủ.
- Lương, bảo hiểm, thuế thu nhập cá nhân, khấu hao, phân bổ trả trước, giá thành sản xuất và tính giá vốn tự động.
- Kết chuyển cuối kỳ, báo cáo tài chính và tờ khai thuế đúng chế độ kế toán Việt Nam; cần chọn chế độ và rà soát bởi kế toán có chuyên môn.
- Phân quyền theo từng nghiệp vụ kế toán (hiện tái sử dụng quyền mua hàng), duyệt bút toán nhiều cấp, bất biến sổ đã ghi, cơ chế đảo bút toán và chỉnh sửa kiểm soát.
- Chạy trên PostgreSQL, xử lý đồng thời quy mô lớn, sao lưu/khôi phục kiểm chứng, kiểm thử xâm nhập độc lập.

## Quy trình kỹ thuật phải làm trước triển khai
1. Chốt chế độ kế toán, hệ thống tài khoản và quy tắc hạch toán áp dụng.
2. Thiết kế trạng thái chứng từ (nháp, duyệt, ghi sổ, đảo bút toán), phê duyệt hai người.
3. Liên kết phiếu nhập/xuất, bán hàng, mua hàng, sản xuất, lương, tài sản và ngân hàng vào sổ kép.
4. Thử nghiệm đóng kỳ, đối chiếu tồn kho – giá vốn – công nợ – ngân hàng – thuế – sổ cái.
5. Chạy kiểm thử đầu cuối, kiểm thử bảo mật và nghiệm thu bởi kế toán trưởng/đơn vị độc lập.

## API mới
GET/POST `/api/accounting/accounts`; GET/POST `/api/accounting/parties`;
GET/POST `/api/accounting/open-items`; POST `/api/accounting/settlements`;
POST `/api/accounting/vat-lines`; GET `/api/accounting/vat-summary?period=YYYY-MM`;
GET `/api/accounting/periods`; POST `/api/accounting/periods/close`;
GET `/api/accounting/financial-summary?start=YYYY-MM-DD&end=YYYY-MM-DD`.

Các API mới dùng SQLite, giao dịch nguyên tử, xác thực Bearer. Tiền lưu dưới dạng số nguyên VND. Không dùng mật khẩu/khóa API thật trong gói.
