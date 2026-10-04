# Báo cáo trực quan hóa dữ liệu (Module 08)

## 1. Mục tiêu
- Xây dựng hệ thống các biểu đồ cốt lõi từ bảng dữ liệu đã được chuẩn hóa kiểu `dtype` (từ module 07).
- Hỗ trợ công cụ phân tích khám phá (EDA) qua hình ảnh trực quan sinh động: phân bố kết quả, điểm số, độ tương tác, và tỷ lệ thiếu hụt dữ liệu.

## 2. Dữ liệu Đầu vào
- `eda_student_summary.csv`
- `eda_weekly_activity.csv`
- `eda_assessment_progress.csv`
- `studentInfo.csv` (dùng để khảo sát Missing Values).

## 3. Quá trình thực hiện
Chạy script `src/08_data_visualization.py` sử dụng thư viện `seaborn` và `matplotlib`. Các biểu đồ được sinh ra bao gồm:
1. `1_final_result_distribution.png`: Bar chart tần suất 4 nhóm kết quả cuối khóa.
2. `2_avg_score_distribution.png`: Histogram phân bố điểm trung bình của toàn bộ sinh viên.
3. `3_total_click_distribution.png`: Histogram cho tổng số lượt click (đã áp dụng log1p).
4. `4_weekly_interaction_by_result.png`: Line chart tiến trình click theo từng tuần cho mỗi nhóm kết quả (mẫu môn học lớn nhất).
5. `5_total_click_by_final_result.png`: Boxplot đối chiếu độ lệch click giữa 4 nhóm final_result.
6. `6_missing_value_chart.png`: Bar chart biểu diễn % missing values.
7. `7_correlation_heatmap.png`: Heatmap đo lường ma trận tương quan giữa tất cả các chỉ số đo lường.
8. `8_dashboard_module_presentation.png`: 1 trang dashboard chia 4 góc lưới (grid subplots) tổng kết cho môn học mẫu.

## 4. Đầu ra
Tất cả 8 ảnh đồ thị chất lượng cao được lưu trữ tại `EDA/outputs/figures/08_visualization/`.
