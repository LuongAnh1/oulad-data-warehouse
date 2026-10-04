# Insights & Rules - Nâng chất lượng dữ liệu (Module 09)

Dưới đây là tổng hợp các vấn đề dữ liệu được phát hiện từ Script `09_data_quality.py` cùng với các quy chuẩn giải quyết cho việc xử lý Missing Value và Outliers.

## 1. Vấn đề dữ liệu phát hiện được (Data Quality Issues)
(Dựa trên file `data_quality_issues.csv`)
- **Về Duplicates**: Bộ dữ liệu chuẩn mực OULAD nhìn chung đã được làm sạch trước khi phát hành nên không phát hiện dòng trùng lặp hoàn toàn nào.
- **Về Khóa ngoại (Foreign Keys)**: 
  - Đa số các bảng liên kết như `assessments` -> `courses` hay `studentVle` -> `studentInfo` đều hoàn toàn khớp 100% khóa.
  - Sự toàn vẹn dữ liệu được đảm bảo để có thể xây dựng Schema Ngôi sao (Star Schema) cho quá trình làm Data Warehouse ở phần sau.

## 2. Quy tắc xử lý Missing Value
Trong bộ OULAD, dữ liệu khuyết không phải lúc nào cũng là "lỗi" mà thường mang ý nghĩa nghiệp vụ. Quy tắc đã chốt:
1. **`date_unregistration` (Bảng `studentRegistration`)**: Bị khuyết >70%. **Quy tắc**: Không được xóa. Khuyết có nghĩa là sinh viên KHÔNG hủy môn. Có thể tạo thêm cờ `is_unregistered = False`.
2. **`score` (Bảng `studentAssessment`)**: Thiếu khi sinh viên nộp bài nhưng chưa có điểm hoặc hệ thống không chấm. **Quy tắc**: Xử lý bằng cách điền trung vị môn học, hoặc tạo flag `is_missing_score = True`. 
3. **`imd_band` (Bảng `studentInfo`)**: Thiếu khoảng 5%. **Quy tắc**: Cập nhật giá trị thành `Unknown` hoặc `Missing` thay vì bỏ dòng vì các sinh viên này vẫn có lịch sử học tập quan trọng.

## 3. Quy tắc xử lý Outliers
1. **Tổng lượt click (`sum_click`)**: Có một nhóm sinh viên có lượng click lên tới chục nghìn lượt, cao gấp nhiều lần trung bình. **Quy tắc**: TUYỆT ĐỐI KHÔNG XÓA. Sự chăm chỉ vượt mức này là một hành vi thực tế, báo hiệu xác suất đạt Distinction cực cao.
2. **Nộp bài quá sớm / Quá muộn**: Có bài nộp trước hạn 100 ngày hoặc trễ hạn hàng tháng. **Quy tắc**: Đánh cờ `is_late` hoặc tính `days_late = date_submitted - date` thay vì vứt bỏ dữ liệu.

## 4. Tách bạch Data Layers (Kiến trúc dữ liệu)
Để tránh nhầm lẫn, kiến trúc dữ liệu được quy hoạch rõ:
- **`raw_data/`**: Cấm sửa đổi.
- **`ETL/staging_data/`**: Dữ liệu đã định dạng đúng ID/Category, sẵn sàng để EDA.
- **`ETL/eda_data/`**: Dữ liệu phái sinh (derived) tổng hợp theo tuần, theo sinh viên, làm nền tảng trực tiếp vẽ biểu đồ và chạy ML.
