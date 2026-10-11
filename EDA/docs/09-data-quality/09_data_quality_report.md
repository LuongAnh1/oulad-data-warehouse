# Báo cáo Chất lượng dữ liệu (Module 09)

## 1. Mục tiêu
- Đánh giá toàn diện chất lượng của bộ dữ liệu OULAD sau khi trải qua bước Staging.
- Phát hiện các lỗi logic dữ liệu như: trùng lặp dòng (duplicates), đứt gãy khóa ngoại (foreign key mismatches).
- Tài liệu hóa các quy tắc xử lý Missing Value và Outlier đã được thống nhất áp dụng xuyên suốt dự án.

## 2. Đầu vào
- 7 bảng dữ liệu cốt lõi từ `ETL/staging_data/`: `courses.csv`, `assessments.csv`, `vle.csv`, `studentInfo.csv`, `studentRegistration.csv`, `studentAssessment.csv`, `studentVle.csv`.

## 3. Quy trình đánh giá
- **Kiểm tra trùng lặp**: Quét toàn bộ các dòng trên cả 7 bảng dữ liệu. Bất kỳ dòng nào lặp lại 100% nội dung sẽ được đếm.
- **Kiểm tra khóa ngoại**: Thiết lập 10 quy tắc Map khóa (Ví dụ: `id_student` trong `studentAssessment` phải tồn tại trong `studentInfo`). Dùng kỹ thuật `Left Join` để tìm ra các bản ghi bị "mồ côi" (orphan records).

## 4. Đầu ra
- Kết quả rà soát chi tiết được lưu thành bảng tại: `EDA/outputs/tables/09_data_quality/data_quality_issues.csv`.
- Các quy tắc xử lý ngoại lệ được lưu vào file insights.
