# SUNNY FLEX 3D V87 - BAO CAO BAN GIAO

**TRANG THAI: BAN PHAT TRIEN - CHUA DU DIEU KIEN NGHIEM THU ERP.**

## Da thuc hien
- Bao toan ma nguon V86 va giao dien legacy goc.
- Them backend/compat.py: API status, run, ask, realtime, stock, electric, marketing, marketing/create, marketing/review, marketing/seed va integration/coverage.
- Them kiem tra xac thuc va kiem thu realtime, dien nang, marketing, khong bao AI that khi chua co.
- Ket qua kiem thu: 11 passed, 2 warnings (FastAPI on_event deprecated).
- Canh bao ro giao dien legacy co du lieu mo phong.

## CHUA HOAN THANH
- Frontend legacy chua duoc chuyen hoan toan sang xac thuc Bearer; mot so loi goi co the nhan HTTP 401. Co API khong dong nghia da tich hop dau cuoi.
- /api/stock legacy tra HTTP 409 co chu dich de tranh ghi sai vat tu; su dung /api/stock/movements.
- /api/ask chua co AI ngon ngu thuc; /api/run chi la bo quy tac.
- Ke toan, luong, QR, camera, can dien tu, nhan dien anh, tu dong hoa Agent, quy trinh san xuat-QC-kho-giao hang chua nghiem thu.
- Khong su dung cho tien that hoac nha may khi chua kiem thu va nghiem thu thuc te.

## Cai dat
1. Python 3.11+, `pip install -r requirements.txt`
2. Dat bien `SUNNY_ADMIN_PASSWORD` it nhat 12 ky tu, khong dua mat khau that vao source.
3. `uvicorn backend.main:app --host 127.0.0.1 --port 8000`
4. Mo `http://127.0.0.1:8000/` va `/api/docs`.
5. `python -m pytest -q`.

## Yeu cau ky thuat tiep theo
Chuyen frontend sang API co xac thuc, xay dung ke toan but toan doi, kiem thu end-to-end SX-QC-QR-kho, cau hinh AI thuc co kiem soat, kiem thu bao mat va sao luu/khoi phuc.
