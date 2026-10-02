# EDA Insights - Phát Hiện Dữ Liệu Ngoại Lệ

## Cách đọc nhanh

File report chính liệt kê các rule và số lượng outlier. File này giải thích outlier nào là lỗi dữ liệu rõ ràng, outlier nào có thể là hành vi học thật, và nên xử lý thế nào ở bước sau.

## 1. Score và sum_click không có lỗi range rõ ràng

Quan sát:

- `score` ngoài khoảng 0-100: 0 dòng.
- Raw `studentVle.sum_click < 0`: 0 dòng.
- Raw `studentVle.sum_click = 0`: 0 dòng.

Diễn giải:

- Các biến số lõi không có lỗi range thô. Đây là tín hiệu tốt cho chất lượng staging.
- Không có dòng raw `sum_click = 0`, nhưng vẫn có sinh viên có `total_click = 0` ở bảng tổng hợp. Điều này thường nghĩa là sinh viên có đăng ký/thông tin học tập nhưng không có hoạt động VLE quan sát được.

Ý nghĩa với phân tích sau:

- Không cần rule loại bỏ score ngoài khoảng.
- Nên giữ nhóm `total_click = 0` như một nhóm hành vi riêng.

## 2. Tương tác VLE rất thấp hoặc rất cao

Quan sát:

- Module-presentation có tỷ lệ `total_click = 0` cao nhất là `BBB-2014B`, chiếm 19.8%.
- Module-presentation có tỷ lệ sinh viên `total_click` cao theo IQR lớn nhất là `BBB-2013B`, chiếm 8.2%.
- Module-presentation có tỷ lệ weekly click cao theo IQR lớn nhất là `BBB-2013B`, chiếm 9.1%.

Diễn giải:

- Tương tác VLE có đuôi phải dài. Người học có click rất cao không nên bị xóa mặc định vì đó có thể là hành vi ôn tập thật.
- Nhóm `total_click = 0` lại là tín hiệu khác: sinh viên có thể không vào VLE, hoặc hoạt động không được ghi nhận ở bảng tương tác.

Ý nghĩa với phân tích sau:

- Nên tạo các flag `is_zero_click`, `is_high_click_iqr`.
- Khi dùng click làm feature, nên dùng `log1p` hoặc binning để giảm ảnh hưởng của vài giá trị rất lớn.

## 3. Submission quá sớm hoặc quá muộn

Quan sát:

- Submission quá sớm hơn 60 ngày: 18,037 dòng.
- Submission quá muộn hơn 30 ngày: 471 dòng.
- Tỷ lệ quá sớm cao nhất ở `FFF-2014J`, chiếm 27.6%.
- Tỷ lệ quá muộn cao nhất ở `GGG-2014J`, chiếm 0.6%.

Diễn giải:

- Nộp rất sớm không nhất thiết là lỗi. Một số assessment có thể mở sớm hoặc có cách tính ngày tương đối khác nhau.
- Nộp rất muộn đáng chú ý hơn cho phân tích hành vi học, đặc biệt nếu gắn với `final_result` hoặc score thấp.

Ý nghĩa với phân tích sau:

- Nên tạo biến `days_from_due`, `is_very_early_submission`, `is_very_late_submission`.
- Nếu nhóm chọn bài toán cảnh báo sớm, cần kiểm soát checkpoint thời gian để tránh dùng thông tin tương lai.

## 4. Weight assessment

Quan sát:

- Assessment có `weight = 0`: 56 dòng.
- Module-presentation có non-Exam weight khác 100: 3 nhóm.
- Module-presentation có Exam weight khác 100: 2 nhóm.

Diễn giải:

- `weight = 0` thường không phải lỗi range vì vẫn nằm trong khoảng 0-100. Nó có thể là assessment không đóng góp trực tiếp vào điểm cuối.
- Cần tách Exam và non-Exam. Nếu cộng tất cả assessment lại, nhiều module-presentation có tổng 200 hoặc 300 vì exam và coursework có thể là hai thành phần riêng.

Module-presentation cần ghi chú:

- Non-Exam khác 100: `GGG-2013J` có non_exam_weight = 0.0.
- Non-Exam khác 100: `GGG-2014B` có non_exam_weight = 0.0.
- Non-Exam khác 100: `GGG-2014J` có non_exam_weight = 0.0.
- Exam khác 100: `CCC-2014B` có exam_weight = 200.0.
- Exam khác 100: `CCC-2014J` có exam_weight = 200.0.

Ý nghĩa với phân tích sau:

- Khi tính weighted score, nên dùng tổng trọng số đã nộp thay vì giả định mọi module có cùng cấu trúc assessment.
- Các assessment weight 0 nên được giữ lại cho phân tích hành vi nộp bài, nhưng không nên làm sai điểm weighted score.

## 5. Kết luận xử lý outlier

- Không xóa outlier tự động.
- Gắn cờ outlier để phân tích sâu hơn.
- Luôn so sánh theo module-presentation.
- Với click và submission timing, outlier có thể là tín hiệu hành vi học quan trọng thay vì lỗi dữ liệu.
