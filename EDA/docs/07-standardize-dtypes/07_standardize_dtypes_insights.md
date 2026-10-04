# Insights - Chuẩn hóa kiểu dữ liệu (Module 07)

## Nhận xét từ bảng đối chiếu Raw - ETL - EDA

1. **Sự hao hụt kiểu dữ liệu khi lưu `.csv`**:
   - Khi luồng ETL ghi dữ liệu ra `staging_data/*.csv`, các kiểu dữ liệu nâng cao như `category` hoặc chuỗi `string` bị mất thông tin. Khi Pandas đọc lại, chúng mặc định trở về `object` (đối với text) hoặc `int64` (đối với ID dạng số).
   - Do đó, bước **EDA Enforced Dtype** là bắt buộc để khôi phục đúng tính chất của dữ liệu, giảm thiểu dung lượng RAM và tối ưu tốc độ trực quan hóa.

2. **Các biến Categorical cần lưu ý**:
   - Nhóm 1 (Định vị học tập): `code_module`, `code_presentation`, `assessment_type`, `activity_type`. Việc đưa nhóm này về `category` giúp các biểu đồ theo module-presentation dễ nhóm hơn.
   - Nhóm 2 (Thông tin nền): `gender`, `region`, `highest_education`, `imd_band`, `age_band`, `disability`. Nhóm này có nhiều text trùng lặp, ép về `category` tối ưu rất tốt.
   - Nhóm 3 (Kết quả): `final_result`.

3. **Biến ID (Định danh)**:
   - Các cột `id_student`, `id_site`, `id_assessment` không bao giờ được dùng để cộng trừ nhân chia hay tìm trung bình. 
   - Đưa về `string` để ngăn biểu đồ/phân tích thống kê nhầm lẫn chúng là biến liên tục.

4. **Biến tính toán (Numeric & Dates)**:
   - Các biến số như `score`, `weight`, `sum_click` cần là `float` hoặc `int`.
   - Đặc thù của OULAD: các ngày (`date`, `date_registration`...) là số ngày tương đối tính từ đầu kỳ, do đó chúng ta giữ nguyên kiểu số nguyên.
