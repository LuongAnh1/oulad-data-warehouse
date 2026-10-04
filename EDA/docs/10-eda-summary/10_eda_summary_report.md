# Báo cáo Tổng hợp kết quả EDA (Executive Summary - Module 10)

## 1. Tổng quan chiến dịch phân tích
Giai đoạn Phân tích dữ liệu khám phá (EDA) của bộ dữ liệu OULAD đã hoàn tất thông qua một quy trình chặt chẽ (từ Module 02 đến Module 10). Toàn bộ dữ liệu đã được **chuẩn hóa kiểu**, **làm sạch**, **kiểm định toàn vẹn**, và **trực quan hóa** thành hệ thống báo cáo hoàn chỉnh.

## 2. Các nhận xét cốt lõi (Key Findings)

### 2.1. Phân bố kết quả học tập (Final Result)
- Nhóm sinh viên đạt `Pass` chiếm tỷ trọng lớn nhất, tuy nhiên nhóm sinh viên rút lui (`Withdrawn`) và trượt (`Fail`) cũng chiếm một phần không nhỏ.
- Mức điểm trung bình (`avg_score`) thường tụ lại ở dải 60 - 80 điểm. Số lượng sinh viên bị điểm 0 tương đối ít nhưng không thể bỏ qua (đặc trưng của việc bỏ thi hoặc bị hủy bài).

### 2.2. Mối liên hệ giữa VLE, Assessment và Kết quả cuối
- **Tương tác VLE (Virtual Learning Environment) là kim chỉ nam**: Có sự tương quan tuyến tính rất rõ giữa tần suất nhấp chuột (click) vào tài nguyên học tập và khả năng qua môn. Nhóm sinh viên đạt `Distinction` (Xuất sắc) luôn duy trì mức độ truy cập VLE trung bình cao nhất, vượt trội hoàn toàn so với nhóm `Fail` và `Withdrawn`.
- **Nhịp độ học tập qua từng tuần**: 
  - Sinh viên `Pass` & `Distinction`: Tương tác đều đặn, có các đỉnh bùng nổ rõ rệt trước ngày đáo hạn bài tập (Assessment Deadlines).
  - Sinh viên `Withdrawn`: Tương tác lao dốc tự do chỉ sau 1-2 tuần đầu tiên, cho thấy dấu hiệu mất động lực hoặc khó khăn sớm.
- **Nộp bài (Assessment)**: Việc nộp đủ bài tập là điều kiện kiên quyết. Bất kỳ sinh viên nào bắt đầu trễ nộp hoặc bỏ nộp bài đầu tiên có rủi ro cực cao sẽ lọt vào nhóm `Fail` hoặc `Withdrawn`.

## 3. Đề xuất các bài toán nghiệp vụ tiếp theo
Dựa trên những Insight đã thu được, đây là 3 hướng bài toán khả thi và mang lại giá trị cao nhất cho giai đoạn Data Modeling (Mô hình hóa) và Data Application (Ứng dụng dữ liệu):

1. **Mô hình học máy dự báo sớm sinh viên bỏ học (Early Dropout Prediction)**:
   - **Mục tiêu**: Dự báo những sinh viên có nguy cơ rơi vào nhóm `Fail` hoặc `Withdrawn`.
   - **Đặc trưng (Features) chính**: Số lượt click trong 4 tuần đầu tiên, biến động tương tác (tăng/giảm), kết quả bài Assessment số 1, các đặc điểm nhân khẩu học (`imd_band`, `highest_education`).
   - **Giá trị**: Giúp nhà trường có các biện pháp can thiệp sớm ngay từ tháng đầu tiên.

2. **Hệ thống phân nhóm hành vi sinh viên (Student Segmentation / Clustering)**:
   - **Mục tiêu**: Phân cụm sinh viên thành các nhóm tính cách học tập (VD: Học nhồi nhét trước lúc thi, Học đều đặn, Ít tương tác, Mất phương hướng).
   - **Đặc trưng (Features) chính**: Chuỗi thời gian click (time-series activity), thói quen làm bài (nộp sớm/nộp trễ).
   - **Giá trị**: Hỗ trợ cố vấn học tập thiết kế lộ trình kèm cặp riêng biệt.

3. **Thiết kế Data Warehouse & BI Dashboard chuẩn hóa**:
   - **Mục tiêu**: Load các dữ liệu Staging (đã đảm bảo toàn vẹn) vào mô hình Star Schema. Tạo các báo cáo Dashboard tương tác trên PowerBI / Tableau để quản lý theo dõi Real-time.
   - **Giá trị**: Giúp Ban Giám hiệu, Trưởng khoa có cái nhìn tổng quát về KPI khóa học (Course Health).
