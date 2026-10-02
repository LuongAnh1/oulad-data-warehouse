# EDA Insights - Phát Hiện Dữ Liệu Khuyết

## Cách đọc nhanh

File report chính cho biết missing nằm ở đâu. File này giải thích missing đó có ý nghĩa gì trong OULAD và nên xử lý thế nào khi phân tích tiếp.

## 1. Missing không phải lúc nào cũng là lỗi

Quan sát:

- Bảng có tỷ lệ missing cao nhất là `stg_vle` với 27.5%.
- Nhiều missing tập trung ở các cột có ý nghĩa nghiệp vụ hoặc metadata, ví dụ `date_unregistration`, `week_from`, `week_to`.

Diễn giải:

- Missing trong OULAD không nên được xử lý máy móc bằng cách xóa dòng hoặc điền 0.
- Một số cột thiếu vì sự kiện không xảy ra. Ví dụ sinh viên không rút môn thì không có `date_unregistration`.
- Một số cột thiếu vì metadata của tài nguyên hoặc assessment không đầy đủ. Các cột này chỉ cần xử lý mạnh nếu dùng trực tiếp trong phân tích thời gian.

Ý nghĩa với phân tích sau:

- Cần phân loại missing trước khi xử lý.
- Missing có ý nghĩa nghiệp vụ nên được giữ lại và chuyển thành flag hoặc nhóm riêng.

## 2. `date_unregistration`

Quan sát:

- Với nhóm `Withdrawn`, có 93 dòng thiếu `date_unregistration`, chiếm 0.9%.

Diễn giải:

- `date_unregistration` thiếu ở nhóm `Pass`, `Distinction`, `Fail` phần lớn là hợp lý vì sinh viên không hủy đăng ký.
- Riêng nhóm `Withdrawn` mà thiếu `date_unregistration` mới cần chú ý, vì nhóm này đáng lẽ thường có ngày hủy.

Ý nghĩa với phân tích sau:

- Có thể tạo biến `is_unregistered` từ việc `date_unregistration` có giá trị hay không.
- Khi phân tích thời điểm rút môn, cần loại riêng hoặc kiểm tra 93 dòng `Withdrawn` thiếu ngày hủy.

## 3. `score`

Quan sát:

- Missing score tập trung nhiều nhất ở assessment type `TMA`, với 173 dòng.

Diễn giải:

- Score bị thiếu không nên hiểu là điểm 0.
- Missing score có thể đến từ bài chưa có điểm, bài không nộp được biểu diễn gián tiếp, hoặc bản ghi có trạng thái đặc biệt như banked.

Ý nghĩa với phân tích sau:

- Nên tạo flag `is_missing_score`.
- Khi tính điểm trung bình hoặc weighted score, cần dùng thêm số bài đã nộp và tổng trọng số đã nộp.
- Không thay score missing bằng 0 nếu mục tiêu là mô tả kết quả học thật.

## 4. `date_submitted`

Quan sát:

- `date_submitted` thiếu 0 dòng trong các submission quan sát được.

Diễn giải:

- Không có missing `date_submitted` không có nghĩa là mọi sinh viên đều nộp đủ bài.
- Trong dữ liệu dạng submission, sinh viên không nộp một assessment thường có thể không xuất hiện dòng tương ứng trong `studentAssessment`, thay vì xuất hiện một dòng có ngày nộp rỗng.

Ý nghĩa với phân tích sau:

- Muốn phát hiện không nộp bài, cần so danh sách assessment bắt buộc với từng student-module-presentation.
- Đây là phần nên làm tiếp ở phân tích chất lượng dữ liệu hoặc phân tích hành vi assessment.

## 5. Biến nền sinh viên

Quan sát:

- `imd_band` thiếu 1,111 dòng, chiếm 3.4%.

Diễn giải:

- `imd_band` là biến nền liên quan tới điều kiện kinh tế-xã hội, nên missing ở biến này cần được ghi rõ thay vì xóa dòng.
- Nếu xóa các dòng thiếu `imd_band`, phân tích có thể lệch mẫu vì nhóm thiếu thông tin nền có thể không ngẫu nhiên.

Ý nghĩa với phân tích sau:

- Nên tạo nhóm `Unknown` hoặc flag `is_missing_imd_band`.
- Khi so sánh kết quả theo `imd_band`, cần hiển thị cả nhóm missing.

## 6. Các trường cần ưu tiên theo dõi

- `stg_vle.week_from`: 5,243 missing. Missing metadata cần ghi chú.
- `stg_vle.week_to`: 5,243 missing. Missing metadata cần ghi chú.
- `stg_student_registration.date_unregistration`: 22,521 missing. Missing hợp lệ theo nghiệp vụ ở phần lớn trường hợp.
- `eda_student_summary.weighted_score`: 9,087 missing. Missing phát sinh khi không có trọng số điểm đã nộp.
- `eda_student_summary.avg_score`: 6,773 missing. Missing phát sinh từ việc không có điểm assessment để tính trung bình.
- `stg_assessments.date`: 11 missing. Missing metadata cần ghi chú.
- `stg_student_info.imd_band`: 1,111 missing. Missing biến nền cần xử lý rõ ràng.
- `eda_assessment_progress.score`: 173 missing. Missing cần ghi chú khi phân tích điểm.
