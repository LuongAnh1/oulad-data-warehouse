# Báo Cáo Tạo Bảng EDA-ready
Thời gian chạy: 2026-10-02 22:55:35

## 1. Cách hiểu bảng EDA-ready trong repo
Các bảng `stg_*` được xem là tên logic của các file đã có trong `ETL/staging_data/`. Script này không copy/rename thêm để tránh nhân đôi dữ liệu lớn.

Các bảng `eda_*` là output tổng hợp đã sinh ở `ETL/eda_data/` từ bước tạo biến phục vụ EDA.

## 2. Danh sách bảng
| Bảng logic | File vật lý | Owner | Số dòng | Số cột | Kích thước bytes | Mục đích |
|---|---|---|---:|---:|---:|---|
| `stg_courses` | `ETL/staging_data/courses.csv` | Người 1 | 22 | 3 | 388 | Danh mục module và presentation. |
| `stg_assessments` | `ETL/staging_data/assessments.csv` | Người 1 | 206 | 6 | 6,490 | Danh mục bài đánh giá, hạn nộp và trọng số. |
| `stg_vle` | `ETL/staging_data/vle.csv` | Người 1 | 6,364 | 6 | 188,230 | Danh mục tài nguyên VLE và loại hoạt động. |
| `stg_student_info` | `ETL/staging_data/studentInfo.csv` | Người 1 | 32,593 | 12 | 2,679,396 | Thông tin nền và kết quả cuối của sinh viên. |
| `stg_student_registration` | `ETL/staging_data/studentRegistration.csv` | Người 2 | 32,593 | 5 | 869,284 | Thông tin đăng ký và hủy đăng ký. |
| `stg_student_assessment` | `ETL/staging_data/studentAssessment.csv` | Người 2 | 173,912 | 5 | 4,298,658 | Log bài đánh giá sinh viên đã nộp. |
| `stg_student_vle` | `ETL/staging_data/studentVle.csv` | Người 2 | 9,868,110 | 6 | 301,922,152 | Log tương tác VLE đã gộp và loại duplicate dòng. |
| `eda_student_summary` | `ETL/eda_data/eda_student_summary.csv` | Người 2 | 32,593 | 27 | 5,092,120 | Bảng tổng hợp một dòng cho mỗi sinh viên trong từng module-presentation. |
| `eda_weekly_activity` | `ETL/eda_data/eda_weekly_activity.csv` | Người 2 | 627,031 | 7 | 17,560,277 | Bảng hoạt động VLE theo sinh viên và tuần học. |
| `eda_assessment_progress` | `ETL/eda_data/eda_assessment_progress.csv` | Người 2 | 173,912 | 12 | 10,485,012 | Bảng tiến độ nộp bài và điểm ở mức assessment. |

## 3. Quy ước sử dụng
- Dùng `stg_*` khi cần dữ liệu đã staging nhưng vẫn gần với dữ liệu gốc.
- Dùng `eda_student_summary` cho EDA theo sinh viên/module-presentation.
- Dùng `eda_weekly_activity` cho EDA theo thời gian/tuần học.
- Dùng `eda_assessment_progress` cho EDA về bài đánh giá, hạn nộp và điểm.
- Các file trong `ETL/eda_data/*.csv` là output sinh ra local và đã được ignore để tránh commit dữ liệu dẫn xuất.

## 4. Kết luận
- Số bảng logic cần có: 10.
- Số bảng đang tồn tại: 10.
- Trạng thái: Hoàn tất.
