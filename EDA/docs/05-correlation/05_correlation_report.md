# Báo Cáo EDA - Phân Tích Tương Quan

## 1. Phạm vi

Phần này phân tích các mối liên hệ ban đầu giữa hoạt động VLE, kết quả assessment và `final_result` trên dữ liệu OULAD EDA-ready. Đơn vị chính là một bản ghi `student - module - presentation` trong `eda_student_summary`.

Nguồn dữ liệu:

- `ETL/eda_data/eda_student_summary.csv`
- `ETL/eda_data/eda_weekly_activity.csv`
- `ETL/eda_data/eda_assessment_progress.csv`

## 2. Lưu ý phương pháp

- Tương quan không có nghĩa là quan hệ nhân quả.
- `final_result` là biến phân loại, nên phần này dùng bảng nhóm, boxplot và stacked bar thay vì ép toàn bộ vào correlation matrix.
- `success_flag` chỉ là biến phụ trợ để sàng lọc nhanh, với `1` là `Distinction` hoặc `Pass`, `0` là `Fail` hoặc `Withdrawn`.
- Các tương quan với `score` hoặc `weighted_score` chỉ tính trên bản ghi có điểm quan sát được.
- Nếu sau này chọn bài toán dự báo sớm, cần giới hạn dữ liệu theo checkpoint thời gian để tránh leakage.

## 3. Nhận xét chính

- Spearman giữa `log1p(total_click)` và `weighted_score`: 0.388.
- Spearman giữa `active_days` và `weighted_score`: 0.378.
- Spearman giữa `late_submission_rate` và `weighted_score`: -0.240.
- Spearman giữa `log1p(total_click)` và `success_flag`: 0.646.
- Median `total_click` của `Distinction`: 1,819, trong khi `Withdrawn`: 85.
- Median `weighted_score` của `Distinction`: 89.2, trong khi `Withdrawn`: 65.5.
- Median `active_days` của `Distinction`: 103.0, trong khi `Withdrawn`: 7.0.
- Trong nhóm `High click`, tỷ lệ `Distinction` + `Pass` là 87.2%.
- Trong nhóm `0 click`, tỷ lệ `Withdrawn` là 88.8%.
- Spearman `log1p(total_click)` và `weighted_score` cao nhất ở `CCC-2014B`: 0.531.
- Spearman `log1p(total_click)` và `weighted_score` thấp nhất ở `DDD-2014J`: 0.301.

Đọc diễn giải chi tiết tại [05_correlation_insights.md](05_correlation_insights.md).

## 4. Các phân tích đã hoàn thành

- Tính Pearson và Spearman correlation matrix cho các biến số chính.
- Tính tương quan giữa `total_click`, `log1p(total_click)`, `active_days`, nộp assessment và `weighted_score`.
- So sánh mức độ tương tác VLE giữa các nhóm `final_result`.
- So sánh điểm assessment và weighted score giữa các nhóm `final_result`.
- Phân tích quan hệ giữa active days, late submissions và kết quả cuối.
- Kiểm tra tương quan `log1p(total_click)` và `weighted_score` riêng theo từng module-presentation.
- Tạo nhóm mức độ tương tác VLE và so sánh tỷ lệ `final_result` theo từng nhóm.

## 5. Bảng đầu ra

- `EDA/outputs/tables/05_correlation/assessment_score_by_final_result.csv`
- `EDA/outputs/tables/05_correlation/assessment_score_by_type_final_result.csv`
- `EDA/outputs/tables/05_correlation/final_result_by_engagement_band.csv`
- `EDA/outputs/tables/05_correlation/key_correlations.csv`
- `EDA/outputs/tables/05_correlation/metrics_by_final_result.csv`
- `EDA/outputs/tables/05_correlation/module_presentation_correlations.csv`
- `EDA/outputs/tables/05_correlation/numeric_pearson_correlation_matrix.csv`
- `EDA/outputs/tables/05_correlation/numeric_spearman_correlation_matrix.csv`
- `EDA/outputs/tables/05_correlation/weekly_activity_by_final_result.csv`

## 6. Biểu đồ đầu ra

- `EDA/outputs/figures/05_correlation/active_days_by_final_result_boxplot.png`
- `EDA/outputs/figures/05_correlation/assessment_score_by_final_result_boxplot.png`
- `EDA/outputs/figures/05_correlation/final_result_by_engagement_band_stacked.png`
- `EDA/outputs/figures/05_correlation/late_submission_rate_by_final_result.png`
- `EDA/outputs/figures/05_correlation/log_total_click_by_final_result_boxplot.png`
- `EDA/outputs/figures/05_correlation/log_total_click_vs_weighted_score_scatter.png`
- `EDA/outputs/figures/05_correlation/module_presentation_click_score_spearman_heatmap.png`
- `EDA/outputs/figures/05_correlation/numeric_spearman_correlation_heatmap.png`
- `EDA/outputs/figures/05_correlation/weighted_score_by_final_result_boxplot.png`

## 7. Khuyến nghị dùng kết quả

- Dùng `log1p(total_click)`, `active_days`, `active_weeks`, `submitted_weight_sum`, `late_submission_rate` làm biến ứng viên cho phân tích sâu hơn.
- Khi so sánh giữa module-presentation, không dùng một hệ số tương quan toàn cục để kết luận cho tất cả môn học.
- Với `final_result`, ưu tiên bảng chéo, boxplot và phân tích theo nhóm hơn là mã hóa thứ bậc tùy tiện.
- Nếu làm dự báo sớm, tạo lại các biến tương tác VLE và assessment theo checkpoint trước khi đưa vào mô hình.
