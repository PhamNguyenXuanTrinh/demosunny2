# KIỂM TOÁN KỸ THUẬT SUNNY FLEX 3D ERP — 25/10/2026

## Kết luận kiểm thử thực tế
- Mã nguồn kiểm tra: `SUNNY_FLEX3D_ERP_V101_GIAO_DIEN_V86_GOC_API`.
- Chạy `SUNNY_ADMIN_PASSWORD=... python -m pytest tests -q`: **47 đạt, 1 thất bại**.
- Thất bại: `tests/test_v86_preservation.py`, `public/index.html` khác byte so với `public/v86.html`. Nguyên nhân cần xác định: sửa trang chính để thêm Tổng kết ngày đã vi phạm hợp đồng bảo toàn V86. Không được sửa bài kiểm thử để che lỗi; cần đặt Tổng kết ngày vào cấu trúc UI V86 với kiểm thử hồi quy thiết kế hoặc giữ nguyên V86 và triển khai bản mở rộng có quản lý thay đổi.
- `docs/API_KIEM_KE_THUC_TE.json`: **121 cặp phương thức/đường dẫn**. `DANH_SACH_API_V100.json` ghi **123**: cần đối soát danh mục, không được quảng cáo 123 API đã nghiệm thu.

## Kiểm tra AI Agent
- `backend/agents.py`: 10 Agent được khai báo: Kho, Sản xuất, Kế toán, Tài chính, Marketing, Kinh doanh, Nhân sự, Chất lượng, Tài sản, Kiểm toán.
- `evaluate()` đọc SQLite, tạo báo cáo quy tắc và lưu `agent_evaluations`; trả `mode=sqlite_rules_not_llm`. Chưa có hệ tác nhân LLM lập kế hoạch/thực thi đa bước.
- Kho: cảnh báo tồn kho dưới 40% định mức (đã có quy tắc). Kinh doanh: đếm đơn. Kế toán: đếm phiếu mua, ghi chưa đối soát ngân hàng. Tài chính: cộng chi phí và tính 3% *chi phí*, **không chứng minh đã tiết kiệm 3%**. Tài sản: đếm tài sản.
- Sản xuất, Marketing, Nhân sự, Chất lượng, Kiểm toán: nhiều kết quả chỉ là ghi chú cần dữ liệu; chưa có bằng chứng đánh giá hiệu quả đầu cuối.
- `backend/automation.py`: có xử lý hàng đợi OCR/ảnh gọi OpenAI khi cấu hình `OPENAI_API_KEY`; kết quả yêu cầu người duyệt. Không thể xác nhận kết nối OpenAI chạy thật khi chưa có khóa và kiểm thử tích hợp. Vòng nền chỉ bật khi `SUNNY_ENABLE_WORKER=1`; mặc định tắt; chu kỳ tối thiểu 60 giây.

## Yêu cầu kỹ thuật bắt buộc để nghiệm thu
1. **Đóng băng hợp đồng giao diện V86**: lưu ảnh chuẩn từng màn hình, kiểm tra tự động các menu/nút và báo cáo Tổng kết ngày; không xóa chức năng cũ.
2. **Hợp đồng API OpenAPI 3.x**: định nghĩa đầu vào/đầu ra, mã lỗi, phân quyền, phân trang, lọc, khóa idempotency, ví dụ dữ liệu, webhook, versioning; kiểm tra tự động từng endpoint với cơ sở dữ liệu kiểm thử.
3. **Dữ liệu**: dùng PostgreSQL triển khai thật, migration, khóa ngoại, giao dịch, nhật ký thay đổi, backup/restore; SQLite chỉ dùng phát triển nếu được đánh giá phù hợp.
4. **Nghiệp vụ liên thông**: khách hàng → báo giá → đơn hàng → kiểm tra tồn → kế hoạch sản xuất → cấp nguyên liệu → ghi nhận ca/KCS → nhập kho → giao hàng → hóa đơn → thu tiền → đối soát → lãi lỗ. Bài kiểm thử bắt buộc có lỗi, hoàn tiền, trả hàng, thiếu hàng, hủy chứng từ.
5. **Kế toán**: bút toán kép, công nợ, đối chiếu ngân hàng, kho–giá vốn, khóa kỳ, hóa đơn/thuế theo quy định hiện hành, báo cáo tài chính; không cho AI tự ghi sổ/phê duyệt thanh toán thiếu kiểm soát.
6. **AI Agent có kiểm soát**: lịch chạy và hàng đợi bền vững, phân vai từng Agent, công cụ API có quyền tối thiểu, xác thực dữ liệu nguồn, mức tin cậy, giải thích cảnh báo, dấu vết hành động, chống chạy lặp, retry, dead-letter, giới hạn chi phí; phê duyệt con người cho nghiệp vụ rủi ro.
7. **KPI năm kỳ**: ngày/tuần/tháng/quý/năm, gắn dữ liệu gốc và kết quả thực, đánh dấu người đạt hoạt động nhưng không đạt doanh thu/sản lượng/chất lượng; 6 người/ca gồm 1 tổ trưởng kiêm KCS và 5 công nhân.
8. **Thiết bị**: giao thức tích hợp QR, cân, camera, bộ đếm mét; bộ mô phỏng và hợp đồng thiết bị, kiểm tra sai số/đứt kết nối; không nhận ảnh làm số liệu xác nhận tự động nếu thiếu đối soát.
9. **Vận hành**: Docker Compose cho môi trường thử; production cần TLS, secret manager, RBAC, rate limit, giám sát, cảnh báo, CI/CD, khôi phục sự cố, quy trình rollback và tài liệu triển khai.
10. **Nghiệm thu**: kiểm thử đơn vị + API + tích hợp + UI + nghiệp vụ đầu cuối + tải + an ninh + phục hồi. Mọi tính năng phải có bằng chứng; trạng thái chưa kiểm thử = chưa nghiệm thu.

## Bảng phân loại hiện trạng
- Có mã: FastAPI, SQLite, 10 báo cáo Agent quy tắc, xử lý OCR có điều kiện, danh mục API, frontend V86 và frontend API riêng.
- Chưa xác minh: kết nối AI API thực tế, 121 endpoint hoạt động đầy đủ nghiệp vụ, đồng bộ camera/cân/QR, báo cáo kế toán pháp lý, UI toàn bộ nút với dữ liệu thật.
- Lỗi tái hiện: 1 bài kiểm thử bảo toàn V86 thất bại; 121/123 API không nhất quán.

**Không được coi đây là xác nhận ERP đã hoàn thiện.** Đây là danh sách nghiệm thu và việc cần làm để kỹ thuật tiếp nhận mà không phải đoán kiến trúc.
