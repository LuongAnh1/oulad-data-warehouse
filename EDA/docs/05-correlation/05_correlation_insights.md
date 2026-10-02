# EDA Insights - Phân Tích Tương Quan

## Cách đọc nhanh

File report chính cho biết đã tính những bảng và biểu đồ nào. File này diễn giải các mối liên hệ đáng chú ý, mức độ tin cậy khi đọc chúng, và cách dùng kết quả cho các bước EDA hoặc mô hình sau này.

## 1. Click VLE và điểm có quan hệ cùng chiều nhưng không tuyệt đối

Quan sát:

- Spearman giữa `log1p(total_click)` và `weighted_score` là 0.388.
- Spearman giữa `active_days` và `weighted_score` là 0.378.
- Median `total_click` của `Distinction` là 1,819, còn `Withdrawn` là 85.

Diễn giải:

- Quan hệ cùng chiều xuất hiện khá rõ: sinh viên tương tác VLE nhiều hơn và đều hơn thường có điểm weighted cao hơn.
- Tuy vậy, hệ số tương quan không đủ để nói click gây ra điểm cao. Sinh viên học tốt có thể chủ động học nhiều hơn, môn học có thiết kế khác nhau, hoặc assessment có trọng số khác nhau.
- Dùng `log1p(total_click)` hợp lý hơn `total_click` thô vì click lệch phải mạnh.

Ý nghĩa với phân tích sau:

- `log1p(total_click)`, `active_days`, `active_weeks` là feature ứng viên tốt.
- Khi trực quan hóa, nên dùng scatter với log click hoặc boxplot theo nhóm kết quả thay vì chỉ dùng histogram tổng thể.

## 2. Active days giúp nhìn hành vi đều đặn hơn tổng click

Quan sát:

- Spearman giữa `active_days` và `weighted_score` là 0.378.
- Median `active_days` của `Pass` là 78.0, còn `Fail` là 22.0.

Diễn giải:

- Tổng click có thể tăng do vài phiên học rất dày. `active_days` cho biết sinh viên có duy trì hoạt động qua nhiều ngày hay không.
- Nếu một sinh viên có tổng click vừa phải nhưng active days cao, hành vi đó có thể khác với sinh viên click rất nhiều trong ít ngày.

Ý nghĩa với phân tích sau:

- Nên giữ cả intensity (`total_click`) và consistency (`active_days`, `active_weeks`).
- Phần phân tích xu hướng theo thời gian nên kiểm tra tuần nào nhóm `Fail` hoặc `Withdrawn` bắt đầu giảm active days.

## 3. Nộp bài và trọng số đã nộp cần được đọc cẩn thận

Quan sát:

- Spearman giữa `submitted_weight_sum` và `weighted_score` là 0.191.
- Spearman giữa `late_submission_rate` và `weighted_score` là -0.240.
- Late submission rate trung bình của `Withdrawn` là 41.3%.

Diễn giải:

- `submitted_weight_sum` có quan hệ cùng chiều nhưng không quá mạnh với `weighted_score`. Biến này vẫn cần đọc cẩn thận vì weighted score được tính từ assessment đã nộp, nên có phần quan hệ cấu trúc.
- `late_submission_rate` có xu hướng ngược chiều với điểm, nhưng cũng chịu ảnh hưởng bởi việc sinh viên có nộp đủ bài hay không.

Ý nghĩa với phân tích sau:

- Khi dùng biến assessment, cần phân biệt feature hành vi thật với biến gần như cấu thành điểm.
- Với bài toán dự báo sớm, không dùng assessment sau checkpoint.

## 4. Nhóm mức độ tương tác cho thấy khác biệt rõ về final_result

Quan sát:

- Trong nhóm `High click`, tỷ lệ `Distinction` + `Pass` là 87.2%.
- Trong nhóm `0 click`, tỷ lệ `Withdrawn` là 88.8%.
- Spearman giữa `log1p(total_click)` và `success_flag` là 0.646.

Diễn giải:

- Nhóm không có click là tín hiệu mạnh của rủi ro rút môn hoặc kết quả xấu.
- Nhóm click cao có tỷ lệ kết quả tốt cao hơn, nhưng vẫn có sinh viên `Fail` hoặc `Withdrawn`. Vì vậy không nên dùng ngưỡng click đơn giản để kết luận một sinh viên chắc chắn thành công.

Ý nghĩa với phân tích sau:

- Nên tạo nhóm engagement band để dashboard dễ đọc.
- Với mô hình, engagement band có thể là biến giải thích dễ diễn giải hơn tổng click thô.

## 5. Điểm assessment khác biệt theo final_result

Quan sát:

- Median score assessment của `Distinction` là 91.0.
- Median score assessment của `Fail` là 66.0.
- Median score assessment của `Withdrawn` là 70.0.

Diễn giải:

- Điểm assessment phân tách nhóm kết quả cuối khá rõ. Tuy nhiên, với `Withdrawn`, điểm chỉ quan sát được ở những bài sinh viên đã nộp trước khi rút hoặc dừng học.
- Vì vậy, thiếu điểm và số bài đã nộp quan trọng không kém bản thân điểm số.

Ý nghĩa với phân tích sau:

- Khi phân tích kết quả cuối, nên dùng kết hợp `avg_score`, `weighted_score`, `submitted_assessments`, `submitted_weight_sum`.
- Không nên so sánh điểm trung bình giữa nhóm nếu bỏ qua tỷ lệ missing score và số bài đã nộp.

## 6. Tương quan thay đổi theo module-presentation

Quan sát:

- Spearman `log1p(total_click)` và `weighted_score` cao nhất ở `CCC-2014B`: 0.531.
- Spearman `log1p(total_click)` và `weighted_score` thấp nhất ở `DDD-2014J`: 0.301.

Diễn giải:

- Không nên dùng một hệ số toàn cục để đại diện cho mọi môn học. Thiết kế môn học, loại assessment, mức độ dùng VLE và hành vi sinh viên khác nhau theo module-presentation.
- Nếu một module có tương quan thấp, điều đó không nhất thiết nghĩa là VLE không quan trọng. Có thể VLE không phản ánh toàn bộ hoạt động học, hoặc assessment đo năng lực khác.

Ý nghĩa với phân tích sau:

- Dashboard nên có filter theo module-presentation.
- Nếu xây mô hình, nên kiểm tra hiệu năng theo module-presentation thay vì chỉ nhìn metric toàn cục.

## 7. Kết luận cho bước tiếp theo

- Click, active days và assessment progress có tín hiệu liên quan đến kết quả học tập.
- Tín hiệu mạnh nhất có nguy cơ leakage thường nằm ở các biến assessment gần điểm cuối. Cần kiểm soát thời gian nếu dùng cho dự báo.
- Phần tiếp theo nên đi vào xu hướng theo thời gian để xem khác biệt xuất hiện từ tuần nào, thay vì chỉ nhìn tương quan tổng kỳ.
