# Checklist EDA - Phát Hiện Dữ Liệu Khuyết

- [x] Thống kê số lượng missing value theo từng cột.
- [x] Tính tỷ lệ missing value theo từng bảng.
- [x] Kiểm tra `date_unregistration` bị thiếu.
- [x] Kiểm tra `score` bị thiếu.
- [x] Kiểm tra `date_submitted` bị thiếu.
- [x] Kiểm tra missing value trong các biến nền như `imd_band`.
- [x] Phân loại missing value hợp lệ và missing cần xử lý.

Minh chứng:

- Script: `EDA/src/03_detect_missing_values.py`
- Report: `EDA/docs/03-missing-values/03_missing_values_report.md`
- Insights: `EDA/docs/03-missing-values/03_missing_values_insights.md`
- Tables: `EDA/outputs/tables/03_missing_values/`
- Figures: `EDA/outputs/figures/03_missing_values/`
