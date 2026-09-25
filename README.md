# OULAD Data Warehouse

Repo này lưu trữ dữ liệu thô, tài liệu mô tả và yêu cầu nghiệp vụ cho dự án phân tích/kho dữ liệu dựa trên Open University Learning Analytics Dataset (OULAD).

## Cấu trúc

    raw_data/        Dữ liệu CSV gốc của OULAD
    docs/            Tài liệu mô tả dữ liệu, schema và yêu cầu nghiệp vụ
    docs/paper/      Bài báo OULAD gốc và bản diễn giải tiếng Việt

## Tài liệu chính

- docs/requirements.md: bài toán nghiệp vụ nhóm chọn - cảnh báo sớm sinh viên có nguy cơ Fail hoặc Withdrawn.
- docs/oulad_raw_data.md: tổng quan bộ dữ liệu, danh sách file và lưu ý khi đọc dữ liệu.
- docs/oulad_schema_relationships.md: ý nghĩa 7 bảng, từng cột và quan hệ khóa chính - khóa ngoại.
- docs/paper/sdata2017171_mo_ta_vi.md: bản diễn giải tiếng Việt của bài báo OULAD.

## Dữ liệu

OULAD gồm 7 bảng chính: courses, assessments, vle, studentInfo, studentRegistration, studentAssessment và studentVle.

Trong repo này, studentVle được chia thành studentVle_0.csv đến studentVle_7.csv. Các file này có thêm một cột index không tên ở đầu file; khi đọc bằng pandas có thể dùng index_col=0 hoặc bỏ cột này trước khi phân tích.

## Nguồn tham khảo

- Kaggle: https://www.kaggle.com/datasets/rocki37/open-university-learning-analytics-dataset/
- OULAD official page: https://research.stem.open.ac.uk/ouanalyse/open-dataset-more/
- Paper: Kuzilek, J., Hlosta, M., & Zdrahal, Z. (2017). Open University Learning Analytics dataset. Scientific Data, 4, 170171. https://doi.org/10.1038/sdata.2017.171