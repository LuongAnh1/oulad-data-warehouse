# Insights - Trực quan hóa dữ liệu (Module 08)

## Những đúc kết quan trọng từ hệ thống Biểu đồ

1. **Về phân bố kết quả (`1_final_result` & `2_avg_score`)**:
   - Tỷ lệ sinh viên `Pass` là cao nhất, nhưng lượng sinh viên bỏ ngang (`Withdrawn`) hoặc thi rớt (`Fail`) cũng chiếm một phần không nhỏ.
   - Điểm số (avg_score) thường tập trung thành cụm xoay quanh 60-80 điểm, một số lượng ít bị điểm 0.

2. **Về phân bố tương tác (`3_total_click` & `5_total_click_by_final_result`)**:
   - Dữ liệu `total_click` bị lệch phải nghiêm trọng (right-skewed), phần lớn sinh viên tương tác trung bình nhưng có một số lượng nhỏ tương tác cực kỳ dày đặc. Việc sử dụng hàm logarit `log1p` giúp kéo đồ thị trở về dáng dấp gần chuẩn hơn, trực quan dễ nhìn hơn.
   - Nhìn vào biểu đồ Boxplot, nhóm `Distinction` có trung vị tương tác cao nhất, sau đó là `Pass`, `Fail`, và thấp nhất là `Withdrawn`. Điểu này chứng tỏ VLE là một chỉ báo (predictor) rất mạnh.

3. **Tiến trình tương tác theo tuần (`4_weekly_interaction`)**:
   - Sinh viên `Distinction` và `Pass` duy trì nhịp độ đều đặn suốt học kỳ, với các đỉnh tương tác cao trước các cột mốc làm bài kiểm tra (assessment deadlines).
   - Sinh viên `Withdrawn` thể hiện rõ sự tuột dốc sau tuần đầu tiên, tương tác giảm tiệm cận 0 trước khi họ chính thức rút lui.

4. **Biến tương quan (`7_correlation_heatmap`)**:
   - Có sự tương quan dương nhẹ/trung bình giữa `total_click` và `avg_score`.
   - `interacted_sites` và `total_click` có tương quan rất mạnh vì chúng bổ trợ cho nhau (số lượng trang truy cập vs số lượt nhấn).

5. **Lợi ích của Dashboard (Biểu đồ số 8)**:
   - Gom 4 biểu đồ quan trọng nhất (Phân bố kết quả, Phân bố điểm, Tương tác theo tuần, Mối liên hệ điểm-click) vào 1 khung hình chung theo cấp độ môn học (`code_module - code_presentation`). Việc này giúp người ra quyết định xem nhanh 1 trang giấy duy nhất (one-pager) cho 1 kỳ học cụ thể.
