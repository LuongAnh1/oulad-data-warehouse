# Checklist EDA - Phát Hiện Dữ Liệu Ngoại Lệ

- [x] Kiểm tra `score` ngoài khoảng hợp lý.
- [x] Kiểm tra `sum_click` bằng 0 quá cao hoặc âm.
- [x] Kiểm tra `date_submitted` quá sớm hoặc quá muộn so với hạn `date`.
- [x] Kiểm tra sinh viên có tương tác VLE rất cao hoặc rất thấp.
- [x] Kiểm tra assessment có `weight` bất thường.
- [x] So sánh outlier theo từng module-presentation.

Minh chứng:

- Script: `EDA/src/04_detect_outliers.py`
- Report: `EDA/docs/04-outliers/04_outliers_report.md`
- Insights: `EDA/docs/04-outliers/04_outliers_insights.md`
- Tables: `EDA/outputs/tables/04_outliers/`
- Figures: `EDA/outputs/figures/04_outliers/`
