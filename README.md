# OULAD Data Warehouse

Repo này lưu trữ dữ liệu thô và tài liệu mô tả cho Open University Learning Analytics Dataset (OULAD), phục vụ việc tìm hiểu dữ liệu và chuẩn bị cho phân tích/kho dữ liệu.

## Cấu trúc

    raw_data/        CSV gốc của OULAD
    docs/            Tài liệu mô tả dữ liệu và schema
    docs/paper/      Bài báo gốc và bản diễn giải tiếng Việt

## Tài liệu nên đọc

- docs/oulad_raw_data.md: tổng quan bộ dữ liệu, danh sách file, số dòng/số cột và lưu ý khi đọc dữ liệu.
- docs/oulad_schema_relationships.md: ý nghĩa 7 bảng, từng cột, khóa chính logic và khóa ngoại.
- docs/paper/sdata2017171_mo_ta_vi.md: bản diễn giải tiếng Việt của bài báo OULAD.

## Dữ liệu chính

OULAD gồm 7 bảng chính: courses, assessments, vle, studentInfo, studentRegistration, studentAssessment và studentVle.

Trong repo này, studentVle được chia thành studentVle_0.csv đến studentVle_7.csv. Các file này có thêm một cột index không tên ở đầu file; khi đọc bằng pandas nên dùng index_col=0 hoặc bỏ cột này trước khi phân tích.

## Nguồn tham khảo

- Kaggle: https://www.kaggle.com/datasets/rocki37/open-university-learning-analytics-dataset/
- OULAD official page: https://research.stem.open.ac.uk/ouanalyse/open-dataset-more/
- Paper: Kuzilek, J., Hlosta, M., & Zdrahal, Z. (2017). Open University Learning Analytics dataset. Scientific Data, 4, 170171. https://doi.org/10.1038/sdata.2017.171
