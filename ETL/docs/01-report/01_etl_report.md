# Báo Cáo Kết Quả Xử Lý ETL - Staging
Thời gian chạy: 2026-10-02 09:21:15

## 1. Kiểm kê dữ liệu và Load dữ liệu thô
**Tổng số file CSV trong raw_data:** 14

### Tóm tắt các bảng đơn lẻ (Sau khi loại bỏ cột kỹ thuật dư thừa):
- **courses**: 22 dòng, 3 cột. Cột: `code_module, code_presentation, module_presentation_length`
- **assessments**: 206 dòng, 6 cột. Cột: `code_module, code_presentation, id_assessment, assessment_type, date, weight`
- **vle**: 6364 dòng, 6 cột. Cột: `id_site, code_module, code_presentation, activity_type, week_from, week_to`
- **studentInfo**: 32593 dòng, 12 cột. Cột: `code_module, code_presentation, id_student, gender, region, highest_education, imd_band, age_band, num_of_prev_attempts, studied_credits, disability, final_result`
- **studentRegistration**: 32593 dòng, 5 cột. Cột: `code_module, code_presentation, id_student, date_registration, date_unregistration`
- **studentAssessment**: 173912 dòng, 5 cột. Cột: `id_assessment, id_student, date_submitted, is_banked, score`

## 2. Gộp bảng studentVle
- Tổng số file `studentVle_*.csv`: 8
- Tổng số dòng trước khi gộp: 10655280
- Tổng số dòng sau khi gộp: 10655280
- Số dòng trùng lặp (duplicate) sau khi gộp: 787170
- Đã loại bỏ duplicate. Số dòng còn lại: 9868110

## 3. Chuẩn hóa kiểu dữ liệu
- Đã ép kiểu các cột ID (`id_student`, `id_site`, `id_assessment`) sang `string`.
- Đã ép kiểu các cột phân loại (`code_module`, `code_presentation`, `assessment_type`, `final_result`) sang `category`.
- Đã đảm bảo các cột định lượng (`score`, `weight`, `sum_click`) là kiểu số.
- Các cột ngày (`date`, `date_submitted`...) được giữ nguyên kiểu số do đặc thù ngày tương đối của OULAD.

## 4. Xuất dữ liệu ra Staging
- Đã lưu bảng **courses** vào `staging_data/courses.csv`
- Đã lưu bảng **assessments** vào `staging_data/assessments.csv`
- Đã lưu bảng **vle** vào `staging_data/vle.csv`
- Đã lưu bảng **studentInfo** vào `staging_data/studentInfo.csv`
- Đã lưu bảng **studentRegistration** vào `staging_data/studentRegistration.csv`
- Đã lưu bảng **studentAssessment** vào `staging_data/studentAssessment.csv`
- Đã lưu bảng **studentVle** vào `staging_data/studentVle.csv`
## 5. Đánh giá chất lượng dữ liệu (Data Type & Value Range)

### Bảng: courses
| Cột | Kiểu dữ liệu | Số lượng Non-Null | Missing (%) | Min / Max / Unique |
|---|---|---|---|---|
| code_module | object | 22 | 0.0% | 7 unique |
| code_presentation | object | 22 | 0.0% | 4 unique |
| module_presentation_length | int64 | 22 | 0.0% | 234 -> 269 |

### Bảng: assessments
| Cột | Kiểu dữ liệu | Số lượng Non-Null | Missing (%) | Min / Max / Unique |
|---|---|---|---|---|
| code_module | object | 206 | 0.0% | 7 unique |
| code_presentation | object | 206 | 0.0% | 4 unique |
| id_assessment | int64 | 206 | 0.0% | 1752 -> 40088 |
| assessment_type | object | 206 | 0.0% | 3 unique |
| date | float64 | 195 | 5.34% | 12.0 -> 261.0 |
| weight | float64 | 206 | 0.0% | 0.0 -> 100.0 |

### Bảng: vle
| Cột | Kiểu dữ liệu | Số lượng Non-Null | Missing (%) | Min / Max / Unique |
|---|---|---|---|---|
| id_site | int64 | 6364 | 0.0% | 526721 -> 1077905 |
| code_module | object | 6364 | 0.0% | 7 unique |
| code_presentation | object | 6364 | 0.0% | 4 unique |
| activity_type | object | 6364 | 0.0% | 20 unique |
| week_from | float64 | 1121 | 82.39% | 0.0 -> 29.0 |
| week_to | float64 | 1121 | 82.39% | 0.0 -> 29.0 |

### Bảng: studentInfo
| Cột | Kiểu dữ liệu | Số lượng Non-Null | Missing (%) | Min / Max / Unique |
|---|---|---|---|---|
| code_module | object | 32593 | 0.0% | 7 unique |
| code_presentation | object | 32593 | 0.0% | 4 unique |
| id_student | int64 | 32593 | 0.0% | 3733 -> 2716795 |
| gender | object | 32593 | 0.0% | 2 unique |
| region | object | 32593 | 0.0% | 13 unique |
| highest_education | object | 32593 | 0.0% | 5 unique |
| imd_band | object | 31482 | 3.41% | 10 unique |
| age_band | object | 32593 | 0.0% | 3 unique |
| num_of_prev_attempts | int64 | 32593 | 0.0% | 0 -> 6 |
| studied_credits | int64 | 32593 | 0.0% | 30 -> 655 |
| disability | object | 32593 | 0.0% | 2 unique |
| final_result | object | 32593 | 0.0% | 4 unique |

### Bảng: studentRegistration
| Cột | Kiểu dữ liệu | Số lượng Non-Null | Missing (%) | Min / Max / Unique |
|---|---|---|---|---|
| code_module | object | 32593 | 0.0% | 7 unique |
| code_presentation | object | 32593 | 0.0% | 4 unique |
| id_student | int64 | 32593 | 0.0% | 3733 -> 2716795 |
| date_registration | float64 | 32548 | 0.14% | -322.0 -> 167.0 |
| date_unregistration | float64 | 10072 | 69.1% | -365.0 -> 444.0 |

### Bảng: studentAssessment
| Cột | Kiểu dữ liệu | Số lượng Non-Null | Missing (%) | Min / Max / Unique |
|---|---|---|---|---|
| id_assessment | int64 | 173912 | 0.0% | 1752 -> 37443 |
| id_student | int64 | 173912 | 0.0% | 6516 -> 2698588 |
| date_submitted | int64 | 173912 | 0.0% | -11 -> 608 |
| is_banked | int64 | 173912 | 0.0% | 0 -> 1 |
| score | float64 | 173739 | 0.1% | 0.0 -> 100.0 |

### Bảng: studentVle
| Cột | Kiểu dữ liệu | Số lượng Non-Null | Missing (%) | Min / Max / Unique |
|---|---|---|---|---|
| code_module | object | 9868110 | 0.0% | 7 unique |
| code_presentation | object | 9868110 | 0.0% | 4 unique |
| id_student | int64 | 9868110 | 0.0% | 6516 -> 2698588 |
| id_site | int64 | 9868110 | 0.0% | 526721 -> 1049562 |
| date | int64 | 9868110 | 0.0% | -25 -> 269 |
| sum_click | int64 | 9868110 | 0.0% | 1 -> 6977 |