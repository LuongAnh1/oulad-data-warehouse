# Báo Cáo EDA - Phân Bố Dữ Liệu

## 1. Phạm vi

Phần này phân tích phân bố dữ liệu OULAD ở mức EDA-ready. Đơn vị chính của bảng `eda_student_summary` là một bản ghi `student - module - presentation`, không phải chỉ riêng `id_student`.

Nguồn dữ liệu:

- `ETL/eda_data/eda_student_summary.csv`
- `ETL/eda_data/eda_weekly_activity.csv`
- `ETL/eda_data/eda_assessment_progress.csv`
- `ETL/staging_data/assessments.csv`
- `ETL/staging_data/vle.csv`
- `ETL/staging_data/studentVle.csv`

## 2. Quy mô dữ liệu đã dùng

| Bảng | Số dòng | Ý nghĩa chính |
| --- | ---: | --- |
| `eda_student_summary` | 32,593 | Tổng hợp theo student-module-presentation |
| `eda_assessment_progress` | 173,912 | Bản ghi nộp assessment |
| `eda_weekly_activity` | 627,031 | Hoạt động VLE theo tuần học |

## 3. Nhận xét chính

- Nhóm `final_result` lớn nhất là `Pass` với 12,361 bản ghi, chiếm 37.9%.
- Module có nhiều bản ghi student-module-presentation nhất là `BBB` với 7,909 bản ghi.
- Điểm assessment có trung vị 80.0, trung bình 75.8, và thiếu 173 giá trị.
- Tổng click theo sinh viên lệch phải rõ rệt: trung vị 575.0, p95 4436.4, max 23513.0.
- `activity_type` có tổng click lớn nhất là `oucontent` với 11,078,195 click.

Đọc diễn giải chi tiết tại `EDA/docs/02-distribution/02_distribution_insights.md`.

## 4. Các phân bố đã hoàn thành

- Phân bố `final_result`.
- Phân bố sinh viên theo `code_module`.
- Phân bố sinh viên theo `code_presentation`.
- Phân bố `score` trong `studentAssessment`.
- Phân bố `weight` của assessment.
- Phân bố click theo sinh viên và theo tuần học.
- Phân bố `activity_type` theo số tài nguyên, số bản ghi tương tác và tổng click.
- Phân bố thông tin nền: `gender`, `region`, `highest_education`, `imd_band`, `age_band`, `disability`.
- So sánh phân bố `final_result` giữa các module-presentation.
- Boxplot cho `score`, tổng click theo sinh viên và click theo tuần học.
- So sánh phân bố thông tin nền theo `final_result`.

## 5. Bảng đầu ra

- `EDA/outputs/tables/02_distribution/activity_type_distribution.csv`
- `EDA/outputs/tables/02_distribution/age_band_by_final_result.csv`
- `EDA/outputs/tables/02_distribution/age_band_distribution.csv`
- `EDA/outputs/tables/02_distribution/assessment_weight_by_type.csv`
- `EDA/outputs/tables/02_distribution/assessment_weight_distribution_bins.csv`
- `EDA/outputs/tables/02_distribution/assessment_weight_summary.csv`
- `EDA/outputs/tables/02_distribution/disability_by_final_result.csv`
- `EDA/outputs/tables/02_distribution/disability_distribution.csv`
- `EDA/outputs/tables/02_distribution/final_result_by_module_presentation.csv`
- `EDA/outputs/tables/02_distribution/final_result_distribution.csv`
- `EDA/outputs/tables/02_distribution/gender_by_final_result.csv`
- `EDA/outputs/tables/02_distribution/gender_distribution.csv`
- `EDA/outputs/tables/02_distribution/highest_education_by_final_result.csv`
- `EDA/outputs/tables/02_distribution/highest_education_distribution.csv`
- `EDA/outputs/tables/02_distribution/imd_band_by_final_result.csv`
- `EDA/outputs/tables/02_distribution/imd_band_distribution.csv`
- `EDA/outputs/tables/02_distribution/region_by_final_result.csv`
- `EDA/outputs/tables/02_distribution/region_distribution.csv`
- `EDA/outputs/tables/02_distribution/score_by_assessment_type.csv`
- `EDA/outputs/tables/02_distribution/score_by_final_result.csv`
- `EDA/outputs/tables/02_distribution/score_distribution_bins.csv`
- `EDA/outputs/tables/02_distribution/score_summary.csv`
- `EDA/outputs/tables/02_distribution/students_by_module.csv`
- `EDA/outputs/tables/02_distribution/students_by_module_presentation.csv`
- `EDA/outputs/tables/02_distribution/students_by_presentation.csv`
- `EDA/outputs/tables/02_distribution/total_click_distribution_bins.csv`
- `EDA/outputs/tables/02_distribution/total_click_summary.csv`
- `EDA/outputs/tables/02_distribution/weekly_click_distribution_bins.csv`
- `EDA/outputs/tables/02_distribution/weekly_click_summary.csv`

## 6. Biểu đồ đầu ra

- `EDA/outputs/figures/02_distribution/activity_type_resource_click_bubble.png`
- `EDA/outputs/figures/02_distribution/activity_type_total_click.png`
- `EDA/outputs/figures/02_distribution/assessment_weight_distribution.png`
- `EDA/outputs/figures/02_distribution/final_result_by_module_presentation.png`
- `EDA/outputs/figures/02_distribution/final_result_distribution.png`
- `EDA/outputs/figures/02_distribution/final_result_heatmap_by_module_presentation.png`
- `EDA/outputs/figures/02_distribution/score_boxplot.png`
- `EDA/outputs/figures/02_distribution/score_by_final_result_boxplot.png`
- `EDA/outputs/figures/02_distribution/score_distribution.png`
- `EDA/outputs/figures/02_distribution/score_ecdf_by_final_result.png`
- `EDA/outputs/figures/02_distribution/student_background_by_final_result.png`
- `EDA/outputs/figures/02_distribution/student_background_distributions.png`
- `EDA/outputs/figures/02_distribution/student_total_click_by_final_result_boxplot.png`
- `EDA/outputs/figures/02_distribution/student_total_click_ecdf_by_final_result.png`
- `EDA/outputs/figures/02_distribution/student_total_click_log_boxplot.png`
- `EDA/outputs/figures/02_distribution/student_total_click_log_distribution.png`
- `EDA/outputs/figures/02_distribution/students_by_module.png`
- `EDA/outputs/figures/02_distribution/weekly_click_by_final_result_boxplot.png`
- `EDA/outputs/figures/02_distribution/weekly_click_log_boxplot.png`
- `EDA/outputs/figures/02_distribution/weekly_click_log_distribution.png`

## 7. Ghi chú diễn giải

- Không xóa hoặc thay đổi dữ liệu nguồn trong quá trình EDA.
- Các biểu đồ click dùng `log1p` để nhìn rõ phân bố vì biến click lệch phải mạnh.
- Boxplot click cũng dùng `log1p` để tránh một vài giá trị rất lớn làm nén toàn bộ phần còn lại.
- Phân bố `activity_type` dùng `vle.id_site` để map sang `studentVle.id_site`; nếu xuất hiện dòng không map được, số lượng sẽ được ghi trong bảng `activity_type_distribution.csv`.
- Kết quả này là EDA mô tả, chưa khẳng định quan hệ nhân quả giữa tương tác VLE, điểm assessment và kết quả cuối.
