# EDA Insights - Phân Bố Dữ Liệu

## Cách đọc nhanh

File report chính cho biết đã vẽ gì và sinh bảng nào. File này trả lời câu hỏi: các biểu đồ đó đang nói gì, vì sao đáng chú ý, và nên dùng kết quả này thế nào ở các bước sau.

## 1. Phân bố kết quả học tập

Quan sát:

- Nhóm kết quả lớn nhất là `Pass` với 37.9% số bản ghi.
- Tỷ lệ `Withdrawn` cao nhất ở `CCC-2014B`, đạt 46.4%.
- Tỷ lệ `Distinction` cao nhất ở `GGG-2014J`, đạt 17.0%.

Diễn giải:

- Bộ dữ liệu không cân bằng hoàn toàn giữa các nhóm kết quả. `Pass` là nhóm lớn nhất, nhưng `Withdrawn` cũng đủ lớn để không thể xem là nhóm phụ.
- Khác biệt giữa module-presentation cho thấy không nên đánh giá kết quả học tập chỉ ở cấp toàn bộ dữ liệu. Mỗi module-presentation có thể có cấu trúc môn học, deadline, đánh giá và hành vi học khác nhau.

Ý nghĩa với phân tích sau:

- Nếu xây dashboard hoặc mô hình, nên luôn có lát cắt `code_module` và `code_presentation`.
- Nếu chọn bài toán dự báo `final_result`, cần chú ý mất cân bằng nhãn, đặc biệt giữa `Distinction` và các nhóm còn lại.

## 2. Điểm assessment

Quan sát:

- Điểm assessment trung vị của nhóm `Pass` là 79.0.
- Điểm assessment trung vị của nhóm `Withdrawn` là 70.0.

Diễn giải:

- Điểm assessment phân biệt khá rõ các nhóm kết quả cuối, nhưng `Withdrawn` không đơn giản là nhóm điểm thấp. Một phần sinh viên rút môn có thể đã nộp một số bài với điểm quan sát được.
- Vì vậy, khi dùng điểm assessment để phân tích, cần đi kèm số bài đã nộp và thời điểm nộp. Chỉ nhìn điểm trung bình có thể bỏ sót bối cảnh sinh viên rút môn.

Ý nghĩa với phân tích sau:

- Nên dùng thêm `submitted_assessments`, `submitted_weight_sum`, `late_submissions` thay vì chỉ dùng `avg_score` hoặc `weighted_score`.
- Nếu làm cảnh báo sớm, không dùng điểm của assessment diễn ra sau checkpoint.

## 3. Tương tác VLE

Quan sát:

- Nhóm `Distinction` có median `total_click` là 1819.0.
- Nhóm `Withdrawn` có median `total_click` là 85.0.
- Tỷ lệ `total_click = 0` trong nhóm `Withdrawn` là 29.4%.

Diễn giải:

- Click VLE lệch phải mạnh. Một số sinh viên tương tác rất nhiều, làm trung bình cao hơn trung vị.
- ECDF theo `final_result` cho thấy nhóm kết quả tốt thường dịch sang phải, nghĩa là cần nhiều click hơn mới đạt cùng tỷ lệ tích lũy. Đây là tín hiệu có ích, nhưng không phải bằng chứng nhân quả.

Ý nghĩa với phân tích sau:

- Khi vẽ hoặc mô hình hóa click, nên dùng `log1p(total_click)` hoặc phân nhóm mức tương tác.
- Cần phân biệt sinh viên không tương tác với sinh viên tương tác ít. `total_click = 0` nên được giữ như một tín hiệu riêng.

## 4. Activity type

Quan sát:

- `activity_type` có tổng click cao nhất là `oucontent`.
- `activity_type` có số bản ghi tương tác cao nhất là `forumng`.

Diễn giải:

- Một loại tài nguyên có nhiều click không nhất thiết có nhiều bản ghi tương tác nhất. Bubble chart giúp tách ba chiều: số tài nguyên, số bản ghi tương tác, và tổng click.
- Những loại như nội dung học, diễn đàn, quiz và homepage có vai trò khác nhau. Cần tránh gom tất cả thành một biến click duy nhất nếu câu hỏi phân tích cần hiểu hành vi học.

Ý nghĩa với phân tích sau:

- Nên tạo feature theo nhóm activity_type, ví dụ click vào nội dung học, forum, quiz.
- Nếu xây dashboard, nên hiển thị activity_type theo cả tổng click và số tài nguyên để tránh hiểu sai mức độ phổ biến.

## 5. Biến nền sinh viên

Quan sát:

- Phân bố theo `gender`, `region`, `highest_education`, `imd_band`, `age_band`, `disability` đã được so sánh với `final_result`.

Diễn giải:

- Biến nền có thể cho thấy khác biệt nhóm, nhưng cần cẩn thận khi diễn giải. Đây là quan sát mô tả, không phải kết luận nguyên nhân.
- Một số biến nền có thể phản ánh điều kiện học tập, nền tảng học vấn hoặc khả năng tiếp cận tài nguyên, nhưng cần kiểm tra thêm bằng phân tích tương quan hoặc mô hình kiểm soát module-presentation.

Ý nghĩa với phân tích sau:

- Với biến nhạy cảm như `disability`, nên dùng để hiểu chất lượng hỗ trợ và công bằng dữ liệu, không dùng để đưa ra kết luận đơn giản về năng lực cá nhân.
- `imd_band` có missing, nên khi phân tích biến này cần kết hợp insight từ phần missing data.
