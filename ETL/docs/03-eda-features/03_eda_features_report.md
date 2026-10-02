# Báo Cáo Tạo Biến Phục Vụ EDA
Thời gian chạy: 2026-10-02 22:51:21

## 1. Mục tiêu
Tạo các biến tổng hợp từ dữ liệu staging để phục vụ EDA nhất quán giữa các notebook/script.

## 2. Biến đã tạo
| Nhóm biến | Biến | Ý nghĩa |
|---|---|---|
| VLE theo sinh viên | `total_click` | Tổng số click VLE của sinh viên trong một module-presentation |
| VLE theo sinh viên | `active_days` | Số ngày tương đối có hoạt động VLE |
| VLE theo sinh viên | `active_weeks` | Số tuần học có hoạt động VLE, tính bằng `date // 7` |
| VLE theo sinh viên | `interacted_sites` | Số tài nguyên/site VLE sinh viên đã tương tác |
| VLE theo sinh viên | `resource_types_used` | Số loại tài nguyên VLE sinh viên đã tương tác |
| VLE theo sinh viên | `first_activity_date`, `last_activity_date` | Mốc hoạt động VLE đầu/cuối |
| Assessment theo sinh viên | `submitted_assessments` | Số bài đánh giá đã nộp |
| Assessment theo sinh viên | `late_submissions` | Số bài nộp sau hạn `date` của assessment |
| Assessment theo sinh viên | `avg_score` | Điểm trung bình các bài đã nộp |
| Assessment theo sinh viên | `weighted_score` | Điểm trung bình có trọng số theo `weight` |

## 3. File đầu ra
| File | Số dòng | Số cột |
|---|---:|---:|
| `ETL/eda_data/eda_student_summary.csv` | 32593 | 27 |
| `ETL/eda_data/eda_weekly_activity.csv` | 627031 | 7 |
| `ETL/eda_data/eda_assessment_progress.csv` | 173912 | 12 |

## 4. Quy tắc xử lý
- `study_week` được tính bằng phép chia nguyên `date // 7`; dữ liệu trước ngày khai giảng có thể có tuần âm.
- `late_submissions` chỉ tính khi assessment có hạn nộp `date` và `date_submitted > date`.
- `weighted_score = sum(score * weight) / sum(weight)` trên các bài có điểm và trọng số.
- Các sinh viên không có hoạt động VLE hoặc assessment được giữ lại trong `eda_student_summary` và điền 0 cho biến đếm/tổng.

## 5. Kiểm tra nhanh
- `eda_student_summary` giữ đủ 32593 dòng từ `studentInfo`.
- `eda_weekly_activity` có 627031 dòng theo sinh viên và tuần học.
- `eda_assessment_progress` có 173912 dòng ở mức bài đánh giá đã nộp.
- Thời gian chạy: 77.8 giây.
