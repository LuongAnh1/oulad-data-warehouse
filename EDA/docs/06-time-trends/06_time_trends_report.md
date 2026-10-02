# Báo Cáo EDA - Phân Tích Mẫu Và Xu Hướng Theo Thời Gian

## 1. Phạm vi

Phần này phân tích hành vi học tập theo tiến trình thời gian tương đối của OULAD. Các cột ngày trong OULAD là ngày tương đối, không phải ngày lịch thật. Đơn vị thời gian chính là `study_week` trong `eda_weekly_activity`.

Nguồn dữ liệu:

- `ETL/eda_data/eda_student_summary.csv`
- `ETL/eda_data/eda_weekly_activity.csv`
- `ETL/eda_data/eda_assessment_progress.csv`
- `ETL/staging_data/studentRegistration.csv`

## 2. Lưu ý phương pháp

- `study_week` chạy từ tuần -4 đến tuần 38. Tuần âm là hoạt động trước mốc bắt đầu khóa học.
- Sinh viên active trong một tuần là sinh viên có bản ghi VLE ở tuần đó.
- Các checkpoint 14, 28, 42 và 56 ngày chỉ dùng dữ liệu có `study_week <= checkpoint_day / 7`.
- Biểu đồ click / sinh viên active theo `final_result` chỉ hiển thị các điểm có ít nhất 30 sinh viên active để tránh nhiễu ở cuối kỳ khi mẫu quá nhỏ. Bảng CSV vẫn giữ đầy đủ các tuần.
- Nếu sau này chọn bài toán dự báo sớm, không được dùng dữ liệu phát sinh sau checkpoint.

## 3. Nhận xét chính

- Tổng `weekly_click` cao nhất ở tuần 2 với 2,236,153 click.
- Số sinh viên active cao nhất ở tuần 2 với 21,553 sinh viên.
- Nhóm `Withdrawn` có tuần đầu tiên sau peak rơi dưới 80% cường độ click peak ở tuần 5.
- Nhóm `Pass` có tuần đầu tiên sau peak rơi dưới 80% cường độ click peak ở tuần 5.
- Tổng số bản ghi có `date_unregistration`: 10,072.
- Đến hết tuần 0, đã có 3,397 lượt hủy đăng ký, chiếm 10.4% tổng đăng ký.
- Ở checkpoint ngày 14, tỷ lệ sinh viên nhóm `Withdrawn` đã active VLE là 69.0%.
- Ở checkpoint ngày 56, tỷ lệ sinh viên nhóm `Pass` đã active VLE là 99.7%.
- Với nhóm `Pass`, median click / sinh viên active quanh assessment tăng từ 51.4 ở tuần -1 lên 59.4 ở tuần deadline.

Đọc diễn giải chi tiết tại [06_time_trends_insights.md](06_time_trends_insights.md).

## 4. Các phân tích đã hoàn thành

- Tổng hợp `sum_click` theo tuần học.
- Theo dõi số sinh viên active qua từng tuần.
- Phân tích xu hướng tương tác trước và quanh các mốc assessment.
- So sánh xu hướng VLE giữa các nhóm `Distinction`, `Pass`, `Fail`, `Withdrawn`.
- Phát hiện giai đoạn cường độ tương tác bắt đầu giảm sau peak.
- Phân tích tỷ lệ hủy đăng ký theo thời gian tương đối.
- Tạo checkpoint ngày 14, 28, 42 và 56 ở mức thống kê EDA.

## 5. Bảng đầu ra

- `EDA/outputs/tables/06_time_trends/assessment_schedule_by_week.csv`
- `EDA/outputs/tables/06_time_trends/assessment_window_activity_by_result.csv`
- `EDA/outputs/tables/06_time_trends/assessment_window_summary.csv`
- `EDA/outputs/tables/06_time_trends/checkpoint_metrics_by_final_result.csv`
- `EDA/outputs/tables/06_time_trends/checkpoint_overall_metrics.csv`
- `EDA/outputs/tables/06_time_trends/trend_change_points_by_final_result.csv`
- `EDA/outputs/tables/06_time_trends/unregistration_by_module_presentation.csv`
- `EDA/outputs/tables/06_time_trends/unregistration_timeline.csv`
- `EDA/outputs/tables/06_time_trends/weekly_overall_trends.csv`
- `EDA/outputs/tables/06_time_trends/weekly_trends_by_final_result.csv`
- `EDA/outputs/tables/06_time_trends/weekly_trends_by_module_presentation.csv`

## 6. Biểu đồ đầu ra

- `EDA/outputs/figures/06_time_trends/assessment_window_click_by_final_result_line.png`
- `EDA/outputs/figures/06_time_trends/checkpoint_active_rate_by_final_result_line.png`
- `EDA/outputs/figures/06_time_trends/cumulative_unregistration_timeline.png`
- `EDA/outputs/figures/06_time_trends/module_presentation_weekly_click_heatmap.png`
- `EDA/outputs/figures/06_time_trends/weekly_active_rate_by_final_result_line.png`
- `EDA/outputs/figures/06_time_trends/weekly_active_students_line.png`
- `EDA/outputs/figures/06_time_trends/weekly_click_per_active_by_final_result_line.png`
- `EDA/outputs/figures/06_time_trends/weekly_click_share_by_final_result_area.png`
- `EDA/outputs/figures/06_time_trends/weekly_total_click_line.png`

## 7. Khuyến nghị dùng kết quả

- Dùng phần này để chọn checkpoint hợp lý nếu nhóm chuyển sang bài toán cảnh báo sớm.
- Khi làm dashboard, nên có filter theo `final_result`, `code_module`, `code_presentation` và `study_week`.
- Không dùng toàn bộ thời gian của môn học cho bài toán dự báo sớm.
- Nên nối phần này với phân tích tương quan: biến nào tương quan mạnh cần kiểm tra thêm thời điểm tín hiệu bắt đầu xuất hiện.
