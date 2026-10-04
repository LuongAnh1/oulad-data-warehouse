# Báo cáo chuẩn hóa kiểu dữ liệu (Module 07)

## 1. Mục tiêu
- Đối chiếu kiểu dữ liệu (Data Types) qua 3 giai đoạn: `Raw` (Dữ liệu gốc), `ETL` (Staging/Data Warehouse), và `EDA` (Sẵn sàng để phân tích).
- Xây dựng bảng quy chuẩn ép kiểu phục vụ cho các module trực quan hóa (08) và tổng hợp kết quả (10).

## 2. Đầu vào
- Các file `.csv` từ thư mục `raw_data/`.
- Các file `.csv` từ thư mục `ETL/staging_data/`.
- Các file tổng hợp `.csv` từ thư mục `ETL/eda_data/`.

## 3. Quá trình xử lý
- Đọc `100` dòng đầu tiên từ mỗi file để thu thập `dtype` cơ bản của Pandas.
- Khớp với luật nghiệp vụ được định nghĩa trong `ETL/docs/01-report/01_etl_report.md` (ép ID thành string, phân loại thành category).
- Xuất báo cáo mapping.

## 4. Đầu ra
- Bảng mapping: `EDA/outputs/tables/07_standardize_dtypes/dtype_mapping_raw_etl_eda.csv`
- Định dạng dữ liệu đã được chốt hạ cho toàn bộ các script sau này trong hàm `load_eda_data_with_types`.
