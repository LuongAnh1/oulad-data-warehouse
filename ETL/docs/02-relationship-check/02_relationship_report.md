# Báo Cáo Kiểm Tra Quan Hệ Giữa Các Bảng
Thời gian chạy: 2026-10-02 22:44:53

## 1. Phạm vi kiểm tra
- `studentInfo` nối với `studentRegistration` bằng khóa ghép `code_module, code_presentation, id_student`.
- `studentAssessment` nối với `assessments` bằng `id_assessment`.
- `studentVle` nối với `vle` bằng khóa ghép `id_site, code_module, code_presentation`.
- Các bảng hoạt động của sinh viên được kiểm tra lại với khóa ghép `code_module, code_presentation, id_student`.

## 2. Tổng quan dữ liệu dùng để kiểm tra
| Bảng | Số dòng | Khóa kiểm tra | Duplicate khóa |
|---|---:|---|---:|
| studentInfo | 32593 | `code_module, code_presentation, id_student` | 0 |
| studentRegistration | 32593 | `code_module, code_presentation, id_student` | 0 |
| assessments | 206 | `id_assessment` | 0 |
| vle | 6364 | `id_site, code_module, code_presentation` | 0 |
| studentAssessment | 173912 | `id_assessment`, student key suy ra từ assessments | - |
| studentVle | 9868110 | `id_site`, student key | - |

## 3. Kết quả kiểm tra quan hệ
| Kiểm tra | Dòng không khớp | Kết luận |
|---|---:|---|
| studentInfo không có studentRegistration tương ứng | 0 | Đạt |
| studentRegistration không có studentInfo tương ứng | 0 | Đạt |
| studentAssessment không tìm thấy id_assessment trong assessments | 0 | Đạt |
| studentAssessment không khớp studentInfo sau khi suy ra module-presentation | 0 | Đạt |
| studentAssessment không khớp studentRegistration sau khi suy ra module-presentation | 0 | Đạt |
| studentVle không tìm thấy id_site/module/presentation trong vle | 0 | Đạt |
| studentVle không khớp studentInfo theo student key | 0 | Đạt |
| studentVle không khớp studentRegistration theo student key | 0 | Đạt |

## 4. Dòng không khớp
#### studentInfo thiếu studentRegistration
Không có dòng không khớp.

#### studentRegistration thiếu studentInfo
Không có dòng không khớp.

#### studentAssessment thiếu assessments
Không có dòng không khớp.

#### studentAssessment không khớp studentInfo
Không có dòng không khớp.

#### studentAssessment không khớp studentRegistration
Không có dòng không khớp.

#### studentVle thiếu vle
Không có dòng không khớp.

#### studentVle không khớp studentInfo
Không có dòng không khớp.

#### studentVle không khớp studentRegistration
Không có dòng không khớp.

## 5. Kết luận
- Các quan hệ bắt buộc giữa bảng sinh viên, đăng ký, đánh giá và VLE đều được kiểm tra bằng khóa logic tương ứng.
- Không phát hiện dòng không khớp khóa nếu tất cả các chỉ số ở mục 3 bằng 0.
- Thời gian chạy: 69.03 giây.
