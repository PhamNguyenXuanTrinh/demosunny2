# API dữ liệu mở rộng V96

Các đường dẫn `/api/resources/{resource}` (GET, POST), `/api/resources/{resource}/{id}` (GET, PATCH) dùng bảng dữ liệu SQLite thật, xác thực Bearer, phân quyền từng phân hệ, kiểm tra trường hợp lệ, nhật ký ghi/sửa.

Các bảng hỗ trợ: `suppliers`, `products`, `order_lines`, `receipts`, `customer_interactions`, `qc_inspections`, `attendance`, `payroll_drafts`, `kpi_definitions`, `kpi_measurements`, `meters`, `meter_readings`, `asset_events`, `cost_opportunities`, `incidents`, `stock_lots`.

**Giới hạn an toàn:** chứng từ cần quy trình riêng chỉ đọc; không cho sửa trạng thái xác minh, bằng chứng hoặc quyền qua API chung. API chung **không thay thế** quy trình nghiệp vụ kế toán, lương, KPI tự động. Một số bảng có thể yêu cầu cột hoặc khóa ngoại khi tạo.
