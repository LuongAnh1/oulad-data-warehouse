# Checklist 01 - Kết Quả Thực Hiện ETL (Staging)

Dựa trên danh sách các đầu việc, dưới đây là trạng thái hoàn thành của từng mục sau khi chạy quy trình ETL:

## 1. Kiểm kê dữ liệu
- [x] **Liệt kê toàn bộ file CSV trong raw_data:** Đã hoàn thành (Tìm thấy 14 file).
- [x] **Xác nhận đủ 7 bảng chính của OULAD:** Đã hoàn thành (courses, assessments, vle, studentInfo, studentRegistration, studentAssessment, studentVle).
- [x] **Ghi nhận các file bị chia nhỏ:** Đã hoàn thành (studentVle_0.csv đến studentVle_7.csv).
- [x] **Kiểm tra số dòng và số cột của từng bảng:** Đã hoàn thành (Có chi tiết trong báo cáo `01_etl_report.md`).
- [x] **Kiểm tra tên cột của từng bảng:** Đã hoàn thành.
- [x] **Tóm tắt vai trò của từng bảng trong dữ liệu:** Đã hoàn thành (Được ghi chú đầy đủ trong phần giải thích của file Markdown / Notebook).

## 2. Load dữ liệu thô
- [x] **Đọc từng file CSV bằng cấu hình thống nhất:** Đã hoàn thành (Dùng hàm đọc chuẩn của Pandas).
- [x] **Giữ nguyên dữ liệu gốc trong raw_data:** Đã hoàn thành (Quy trình chỉ đọc, không ghi đè lên thư mục raw_data).
- [x] **Không chỉnh sửa trực tiếp file CSV gốc:** Đã hoàn thành.
- [x] **Xác định nơi lưu dữ liệu staging hoặc dữ liệu trung gian:** Đã hoàn thành (Dữ liệu đầu ra được lưu riêng biệt tại `ETL/staging_data/`).
- [x] **Ghi nhận lỗi đọc file nếu có:** Đã hoàn thành (Tất cả file đều được đọc thành công, không phát hiện file hỏng hay lỗi format).

## 3. Gộp bảng bị chia nhỏ
- [x] **Gộp studentVle_0.csv đến studentVle_7.csv thành một bảng logic:** Đã hoàn thành.
- [x] **Kiểm tra các file studentVle có cùng cấu trúc cột:** Đã hoàn thành (Gộp bằng concat thành công).
- [x] **Kiểm tra tổng số dòng trước và sau khi gộp:** Đã hoàn thành (10,655,280 dòng trước và sau gộp).
- [x] **Kiểm tra duplicate sau khi gộp:** Đã hoàn thành (Phát hiện và xóa 787,170 dòng trùng lặp log, còn lại 9,868,110 dòng).
- [x] **Lưu hoặc sinh bảng studentVle đã gộp cho bước EDA:** Đã hoàn thành (Lưu tại `staging_data/studentVle.csv`).

## 4. Loại bỏ cột kỹ thuật dư thừa
- [x] **Kiểm tra các cột index không tên như Unnamed: 0:** Đã hoàn thành.
- [x] **Loại bỏ cột index dư khỏi bảng dùng để phân tích:** Đã hoàn thành (Đoạn code loại bỏ tất cả các cột tự sinh chứa `Unnamed`).
- [x] **Xác nhận cột bị loại bỏ không mang ý nghĩa nghiệp vụ:** Đã hoàn thành (Đó chỉ là cột index dòng của database xuất ra).
- [x] **Ghi lại quy tắc loại bỏ cột kỹ thuật:** Đã hoàn thành.

## 5. Chuẩn hóa kiểu dữ liệu
- [x] **Chuyển id_student, id_site, id_assessment về kiểu phù hợp:** Đã hoàn thành (Được ép về kiểu chuỗi String/Object).
- [x] **Xem code_module, code_presentation, assessment_type, final_result là biến phân loại:** Đã hoàn thành (Được ép về kiểu Category trong lúc xử lý).
- [x] **Xử lý các cột ngày tương đối:** Đã hoàn thành (Giữ nguyên định dạng số do OULAD dùng số ngày tương đối so với khai giảng).
- [x] **Chuyển score, weight, sum_click về kiểu số:** Đã hoàn thành (Đảm bảo định dạng toán học Float/Int64).
- [x] **Kiểm tra lại kiểu dữ liệu sau khi gộp dữ liệu:** Đã hoàn thành (Bảng "Đánh giá chất lượng dữ liệu" - Min/Max/Unique đã được đính kèm ở phần cuối báo cáo).

---
**Trạng thái chung:** Hoàn tất 100%
**Tiếp theo:** Dữ liệu hoàn toàn sạch sẽ, sẵn sàng chuyển sang giai đoạn EDA (Khám phá Dữ liệu).
