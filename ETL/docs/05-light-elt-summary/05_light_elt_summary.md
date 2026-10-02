# Tổng Hợp Đầu Ra ELT Nhẹ
Thời gian chạy: 2026-10-02 22:58:05

## 1. Mục tiêu
Tổng hợp lại các đầu ra đã sẵn sàng cho EDA, các quy tắc xử lý chính, chất lượng dữ liệu đã kiểm tra và trạng thái dữ liệu gốc.

## 2. Đầu ra dữ liệu sẵn sàng cho EDA
| Tên logic | File | Loại | Số dòng | Số cột | Kích thước bytes | Ghi chú |
|---|---|---|---:|---:|---:|---|
| `stg_courses` | `ETL/staging_data/courses.csv` | staging | 22 | 3 | 388 | Danh mục module/presentation. |
| `stg_assessments` | `ETL/staging_data/assessments.csv` | staging | 206 | 6 | 6,490 | Danh mục assessment, hạn nộp, trọng số. |
| `stg_vle` | `ETL/staging_data/vle.csv` | staging | 6,364 | 6 | 188,230 | Danh mục tài nguyên VLE. |
| `stg_student_info` | `ETL/staging_data/studentInfo.csv` | staging | 32,593 | 12 | 2,679,396 | Thông tin sinh viên và kết quả cuối. |
| `stg_student_registration` | `ETL/staging_data/studentRegistration.csv` | staging | 32,593 | 5 | 869,284 | Thông tin đăng ký/hủy đăng ký. |
| `stg_student_assessment` | `ETL/staging_data/studentAssessment.csv` | staging | 173,912 | 5 | 4,298,658 | Bài đánh giá sinh viên đã nộp. |
| `stg_student_vle` | `ETL/staging_data/studentVle.csv` | staging | 9,868,110 | 6 | 301,922,152 | Tương tác VLE đã gộp từ 8 file và loại duplicate dòng. |
| `eda_student_summary` | `ETL/eda_data/eda_student_summary.csv` | eda-ready | 32,593 | 27 | 5,092,120 | Bảng tổng hợp theo sinh viên/module-presentation. |
| `eda_weekly_activity` | `ETL/eda_data/eda_weekly_activity.csv` | eda-ready | 627,031 | 7 | 17,560,277 | Bảng hoạt động VLE theo sinh viên và tuần học. |
| `eda_assessment_progress` | `ETL/eda_data/eda_assessment_progress.csv` | eda-ready | 173,912 | 12 | 10,485,012 | Bảng tiến độ nộp bài và điểm assessment. |

## 3. Tài liệu và checklist đã hoàn tất
| Tài liệu | Trạng thái |
|---|---|
| `ETL/docs/01-report/01_etl_report.md` | Có |
| `ETL/docs/01-report/01_etl_checklist.md` | Có |
| `ETL/docs/02-relationship-check/02_relationship_report.md` | Có |
| `ETL/docs/02-relationship-check/02_relationship_checklist.md` | Có |
| `ETL/docs/03-eda-features/03_eda_features_report.md` | Có |
| `ETL/docs/03-eda-features/03_eda_features_checklist.md` | Có |
| `ETL/docs/04-eda-ready-tables/04_eda_ready_tables_report.md` | Có |
| `ETL/docs/04-eda-ready-tables/04_eda_ready_tables_checklist.md` | Có |

## 4. Quy tắc xử lý dữ liệu chính
- Không ghi đè hoặc chỉnh sửa trực tiếp file trong `raw_data/`.
- Cột index kỹ thuật không tên/`Unnamed` được loại khỏi dữ liệu staging vì không mang ý nghĩa nghiệp vụ.
- `studentVle_0.csv` đến `studentVle_7.csv` được gộp thành bảng logic `studentVle`.
- Duplicate dòng trong `studentVle` được loại theo toàn bộ cột nghiệp vụ sau khi bỏ cột index kỹ thuật.
- Ngày trong OULAD được giữ là ngày tương đối, không chuyển sang ngày lịch.
- `study_week` phục vụ EDA được tính bằng `date // 7`; các hoạt động trước khai giảng có thể có tuần âm.
- `late_submissions` được tính khi có hạn nộp assessment và `date_submitted > date`.
- `weighted_score` được tính bằng `sum(score * weight) / sum(weight)` theo sinh viên/module-presentation.

## 5. Tóm tắt kiểm tra chất lượng và quan hệ
- Đã thống kê row/column, missing %, min/max/unique trong báo cáo staging.
- `studentVle` sau gộp có 10,655,280 dòng trước loại duplicate và 9,868,110 dòng sau loại duplicate.
- Không phát hiện dòng không khớp trong các quan hệ chính: studentInfo/studentRegistration, studentAssessment/assessments, studentVle/vle.
- Các bảng EDA-ready đã được sinh từ staging data và sẵn sàng dùng trong notebook EDA.

## 6. Xác nhận dữ liệu gốc
- Số file CSV trong `raw_data/`: 14.
- Quy trình ELT nhẹ chỉ đọc `raw_data/` và ghi đầu ra vào `ETL/staging_data/`, `ETL/eda_data/`, `ETL/docs/`.
- `ETL/eda_data/*.csv` là dữ liệu dẫn xuất local và đã được ignore để tránh commit nhầm.

### Danh sách file raw_data
| File | Kích thước bytes | Last modified |
|---|---:|---|
| `assessments.csv` | 8,200 | 2019-10-07 11:43:22 |
| `courses.csv` | 526 | 2019-10-07 11:43:22 |
| `studentAssessment.csv` | 5,690,310 | 2019-10-07 11:43:22 |
| `studentInfo.csv` | 3,461,652 | 2019-10-07 11:43:24 |
| `studentRegistration.csv` | 1,109,984 | 2019-10-07 11:43:24 |
| `studentVle_0.csv` | 56,748,485 | 2019-10-07 11:43:24 |
| `studentVle_1.csv` | 57,839,973 | 2019-10-07 11:43:30 |
| `studentVle_2.csv` | 57,867,236 | 2019-10-07 11:43:34 |
| `studentVle_3.csv` | 57,878,754 | 2019-10-07 11:43:40 |
| `studentVle_4.csv` | 57,814,714 | 2019-10-07 11:43:46 |
| `studentVle_5.csv` | 57,981,039 | 2019-10-07 11:43:52 |
| `studentVle_6.csv` | 58,455,771 | 2019-10-07 11:43:58 |
| `studentVle_7.csv` | 6,173,860 | 2019-10-07 11:44:04 |
| `vle.csv` | 260,126 | 2019-10-07 11:44:04 |

## 7. Kết luận
- Đầu ra dữ liệu: Đủ.
- Tài liệu kiểm chứng: Đủ.
- Trạng thái tổng hợp ELT nhẹ: Hoàn tất.
