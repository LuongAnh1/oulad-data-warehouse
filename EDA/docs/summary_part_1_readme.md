# Tổng kết EDA Phần 1 (Đã hoàn thành)

Dựa trên cấu trúc và các tệp hiện có trong thư mục `EDA/`, dưới đây là tóm tắt về tiến độ và quy trình mà những người thực hiện trước đã thiết lập.

## 1. Các hạng mục đã hoàn thành
Hệ thống đã hoàn thiện 5 chủ đề phân tích chính (từ 02 đến 06):
- **02. Phân bố dữ liệu (Distribution)**: Phân tích phân bố của `final_result`, sinh viên theo môn học, điểm `score`, lượt click VLE (`sum_click`), thông tin nhân khẩu học.
- **03. Dữ liệu khuyết (Missing Values)**: Thống kê tỷ lệ missing, phân biệt missing hợp lệ (VD: `date_unregistration`) và missing cần xử lý (VD: `score`, `imd_band`).
- **04. Dữ liệu ngoại lệ (Outliers)**: Kiểm tra các giá trị bất thường về điểm số, số lượt click, thời gian nộp bài. Đã đánh cờ (flag) thay vì tự động xóa.
- **05. Phân tích tương quan (Correlation)**: Đánh giá mối quan hệ giữa tương tác VLE, điểm số assessment và kết quả cuối cùng (`final_result`).
- **06. Xu hướng thời gian (Time Trends)**: Đánh giá lượt tương tác theo tuần, mức độ active của sinh viên, xu hướng giảm tương tác và tỷ lệ hủy đăng ký qua các mốc thời gian.

## 2. Workflow và Cấu trúc thư mục hiện tại
Quy trình làm việc (workflow) hiện tại rất chuẩn mực và có tính module hóa cao. Bất kỳ task nào tiếp theo cũng cần tuân thủ kiến trúc này:

- **`src/`**: Chứa các script Python (`.py`) tự động hóa việc tính toán, sinh biểu đồ và bảng biểu.
- **`notebooks/`**: Chứa Jupyter Notebook (`.ipynb`) hỗ trợ chạy tương tác, debug và trình bày phân tích trực quan.
- **`docs/`**: Nơi chứa tài liệu chi tiết chia theo từng thư mục con (VD: `02-distribution`), bao gồm:
  - `*_report.md`: Báo cáo tóm tắt quá trình chạy dữ liệu và sinh file.
  - `*_insights.md`: Viết nhận xét chi tiết, giải thích ý nghĩa các biểu đồ, rút ra insight kinh doanh.
  - `*_checklist.md`: Danh sách các công việc nhỏ đã hoàn thành.
- **`outputs/`**: Nơi chứa kết quả chạy từ script.
  - `figures/`: Lưu ảnh biểu đồ.
  - `tables/`: Lưu các bảng dữ liệu thống kê (CSV).

Quy trình chuẩn cho một task mới:
1. Cập nhật trạng thái vào `eda_tasks.csv`.
2. Tạo script Python trong `src/`.
3. Tạo Notebook trong `notebooks/`.
4. Viết file report, insights, và checklist lưu vào `docs/<tên-task>/`.
5. Xuất các bảng tĩnh/biểu đồ vào `outputs/`.
