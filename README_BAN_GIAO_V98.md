# SUNNY FLEX 3D – ERP V98: mã nguồn bàn giao và phạm vi xác minh

## Cài đặt
Python 3.11+; `pip install -r requirements.txt`; đặt `SUNNY_ADMIN_PASSWORD` dài ít nhất 12 ký tự (không lưu mật khẩu vào mã nguồn); `uvicorn backend.main:app --host 127.0.0.1 --port 8000`. Xem `deploy/` để cấu hình triển khai. Dữ liệu SQLite phục vụ phát triển/kiểm thử; đánh giá chuyển PostgreSQL trước khi vận hành nhiều người dùng.

## Thành phần
`public/`: Frontend và giao diện V86 lưu trữ; `backend/`: API, xác thực, nghiệp vụ, AI theo quy tắc, kế toán, kho, thiết bị, phê duyệt; `database/`: cấu trúc SQL; `tests/`: kiểm thử; `docs/`: hợp đồng API và hướng dẫn; `archive/`: mã nguồn gốc V86.

## Bổ sung V98
`backend/erp_workflows.py`: quy trình yêu cầu phê duyệt chi phí/mua hàng, lịch sử sự kiện, kiểm tra tách người đề nghị/người phê duyệt, báo cáo sản xuất theo ngày/tuần/tháng/quý/năm từ bảng dữ liệu. Phê duyệt không tự tạo bút toán kế toán hoặc xác nhận đã thanh toán. Không tự đánh dấu hoàn thành nếu chưa đủ chứng cứ.

## Kết quả kiểm thử
Xem `KET_QUA_KIEM_THU_V98.txt`. Các kiểm thử tự động **không thay thế** kiểm thử tải, bảo mật độc lập, thiết bị thực tế và nghiệm thu quy trình end-to-end.

## Những phần CHƯA HOÀN THÀNH – phải giao kỹ thuật
1. Chuyển đổi toàn bộ màn hình/tác vụ V86 thành giao diện vận hành đồng bộ với API.
2. Luồng nghiệp vụ khép kín đơn hàng→giao hàng→thu tiền→hạch toán→đối soát ngân hàng; mua hàng→nhập kho→phải trả→thanh toán; sản xuất→định mức→giá thành→thành phẩm; chấm công→lương→thuế/BHXH.
3. Kế toán pháp định Việt Nam: hệ thống tài khoản, hóa đơn điện tử, thuế, báo cáo, quy tắc khóa/đảo sổ và kiểm tra bởi kế toán có chứng chỉ.
4. AI Agent có lịch chạy, bộ công cụ được giới hạn quyền, hàng chờ phê duyệt, đối chiếu bằng chứng ảnh/PDF, theo dõi độ tin cậy và nhật ký quyết định; cấu hình mô hình và đánh giá đầu ra.
5. Trình điều khiển hãng/model cụ thể cho cân, camera, bộ đếm mét, PLC; thông số giao tiếp và kiểm thử tại xưởng.
6. Đánh giá bảo mật độc lập (OWASP ASVS, phân quyền từng bản ghi, kiểm thử tải, sao lưu/khôi phục, xử lý sự cố, mã hóa, bí mật triển khai).

**Trạng thái:** mã nguồn phát triển có thể bàn giao để kỹ thuật tiếp tục, KHÔNG phải ERP hoàn chỉnh và KHÔNG được tuyên bố đủ điều kiện vận hành chính thức.
