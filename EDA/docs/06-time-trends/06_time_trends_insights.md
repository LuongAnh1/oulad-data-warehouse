# EDA Insights - Phân Tích Mẫu Và Xu Hướng Theo Thời Gian

## Cách đọc nhanh

File report chính cho biết đã sinh bảng và biểu đồ nào. File này giải thích xu hướng theo thời gian đang nói gì, vì sao đáng chú ý và nên dùng thế nào nếu nhóm chuyển sang dashboard hoặc cảnh báo sớm.

## 1. Nhịp tương tác VLE không đều trong suốt môn học

Quan sát:

- Tổng click cao nhất ở tuần 2 với 2,236,153 click.
- Số sinh viên active cao nhất ở tuần 2 với 21,553 sinh viên.

Diễn giải:

- Hành vi VLE có nhịp rõ theo tuần, không phân bổ đều trong toàn khóa.
- Peak tổng click và peak số sinh viên active không nhất thiết là cùng một tuần. Một tuần có nhiều sinh viên active chưa chắc có cường độ click cao nhất trên mỗi sinh viên.

Ý nghĩa với phân tích sau:

- Không nên chỉ dùng tổng click toàn kỳ nếu muốn hiểu quá trình học.
- Dashboard nên có line chart theo tuần và filter module-presentation.

## 2. Nhóm kết quả cuối có nhịp học khác nhau

Quan sát:

- Nhóm `Withdrawn` rơi dưới 80% cường độ click peak sau peak ở tuần 5.
- Nhóm `Distinction` rơi dưới 80% cường độ click peak sau peak ở tuần 5.

Diễn giải:

- Nhóm `Withdrawn` thường mất tương tác sớm hơn và duy trì active rate thấp hơn. Đây là tín hiệu thời gian quan trọng hơn việc chỉ biết tổng click cả kỳ thấp.
- Nhóm kết quả tốt có xu hướng duy trì active dài hơn, nhưng vẫn cần đọc theo module-presentation vì cấu trúc môn học khác nhau.

Ý nghĩa với phân tích sau:

- Nếu chọn bài toán cảnh báo sớm, active rate và click theo tuần là biến nên ưu tiên.
- Cần kiểm tra từ tuần nào tín hiệu đủ rõ để cảnh báo mà không quá muộn.

## 3. Assessment tạo nhịp tương tác quanh deadline

Quan sát:

- Ở tuần deadline assessment, median click / sinh viên active của nhóm `Pass` là 59.4.
- Ở tuần deadline assessment, median click / sinh viên active của nhóm `Withdrawn` là 45.9.

Diễn giải:

- Tương tác quanh assessment phản ánh nhịp làm bài, ôn tập hoặc truy cập tài nguyên đúng hạn.
- Nhóm `Withdrawn` có thể không còn xuất hiện quanh nhiều deadline, nên số click thấp vừa phản ánh cường độ thấp vừa phản ánh việc đã rời khỏi môn.

Ý nghĩa với phân tích sau:

- Phân tích quanh assessment nên tách rõ số sinh viên còn active và click trên sinh viên active.
- Nếu dự báo sớm, chỉ dùng assessment đã xảy ra trước checkpoint.

## 4. Hủy đăng ký xuất hiện cả trước và sau mốc bắt đầu khóa học

Quan sát:

- Đến hết tuần 0, tỷ lệ hủy đăng ký tích lũy là 10.4%.
- Đến hết tuần 4, tỷ lệ hủy đăng ký tích lũy là 16.4%.

Diễn giải:

- Một phần sinh viên hủy đăng ký rất sớm, thậm chí trước hoặc ngay quanh mốc bắt đầu khóa học.
- `date_unregistration` bị thiếu không nên xem là lỗi. Với OULAD, thiếu thường nghĩa là sinh viên không hủy đăng ký.

Ý nghĩa với phân tích sau:

- Với dashboard vận hành, nên theo dõi cumulative unregistration theo tuần.
- Với mô hình dự báo `Withdrawn`, cần chú ý không dùng `date_unregistration` như feature nếu thời điểm dự báo chưa đến ngày đó.

## 5. Checkpoint cho thấy khả năng quan sát sớm

Quan sát:

- Ngày 14, tỷ lệ đã active của `Distinction` là 99.1%.
- Ngày 14, tỷ lệ đã active của `Withdrawn` là 69.0%.
- Ngày 56, tỷ lệ đã active của `Pass` là 99.7%.
- Ngày 56, tỷ lệ đã active của `Fail` là 94.0%.

Diễn giải:

- Checkpoint sớm đã có tín hiệu khác biệt giữa các nhóm, nhưng chưa đủ để kết luận cá nhân.
- Checkpoint càng muộn càng có nhiều thông tin hơn, nhưng cũng giảm giá trị cảnh báo sớm.

Ý nghĩa với phân tích sau:

- Nếu nhóm chọn cảnh báo sớm, nên thử nhiều checkpoint và so sánh trade-off giữa độ sớm và độ đầy đủ thông tin.
- Nếu chỉ làm dashboard mô tả, checkpoint vẫn hữu ích để tạo các mốc theo dõi cố định.

## 6. Kết luận cho bước tiếp theo

- Phần thời gian bổ sung điều mà phân tích tương quan chưa trả lời: tín hiệu xuất hiện ở tuần nào.
- Các biến `weekly_click`, `active_student_pct`, `click_per_active_student`, hoạt động quanh assessment và cumulative checkpoint nên được giữ lại cho phân tích sâu hơn.
- Chưa nên chốt bài toán dự báo chỉ từ EDA này. Kết quả hiện tại phù hợp để nhóm chọn hướng: dashboard tiến trình học, cảnh báo rút môn, hoặc phân tích hành vi quanh assessment.
