# OULAD Data Warehouse

Repo này lưu trữ dữ liệu thô, tài liệu mô tả và yêu cầu nghiệp vụ cho dự án phân tích/kho dữ liệu dựa trên Open University Learning Analytics Dataset (OULAD).

## Cấu trúc

    raw_data/        Dữ liệu CSV gốc của OULAD
    docs/            Tài liệu mô tả dữ liệu, schema và yêu cầu nghiệp vụ
    docs/paper/      Bài báo OULAD gốc và bản diễn giải tiếng Việt

## Tài liệu chính

- docs/requirements.md: bản nháp/ứng viên bài toán nghiệp vụ để nhóm tham khảo trước khi chốt phạm vi.
- docs/oulad_raw_data.md: tổng quan bộ dữ liệu, danh sách file và lưu ý khi đọc dữ liệu.
- docs/oulad_schema_relationships.md: ý nghĩa 7 bảng, từng cột và quan hệ khóa chính - khóa ngoại.
- docs/paper/sdata2017171_mo_ta_vi.md: bản diễn giải tiếng Việt của bài báo OULAD.

## Dữ liệu

OULAD gồm 7 bảng chính: courses, assessments, vle, studentInfo, studentRegistration, studentAssessment và studentVle.

Trong repo này, studentVle được chia thành studentVle_0.csv đến studentVle_7.csv. Các file này có thêm một cột index không tên ở đầu file; khi đọc bằng pandas có thể dùng index_col=0 hoặc bỏ cột này trước khi phân tích.

## Thiết lập môi trường Python

Nên dùng môi trường riêng cho các bước ETL/ELT để tránh lệch phiên bản thư viện giữa các máy.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Nếu chạy notebook trong VS Code/Jupyter, chọn kernel từ môi trường `.venv` vừa tạo.

## Lưu ý khi pull dữ liệu lớn bằng Git LFS

Repo có một số file dữ liệu staging lớn được quản lý bằng Git LFS, đặc biệt là `ETL/staging_data/studentVle.csv`. Để tránh `git pull` tự tải file lớn và bị chậm/kẹt, mỗi thành viên nên cấu hình Git LFS theo chế độ chỉ tải dữ liệu khi cần:

```powershell
git lfs install --skip-smudge
```

Sau đó có thể pull code và tài liệu như bình thường:

```powershell
git pull
```

Khi cần tải dữ liệu thật từ Git LFS, chạy:

```powershell
git lfs pull
```

Hoặc chỉ tải riêng một file lớn:

```powershell
git lfs pull --include="ETL/staging_data/studentVle.csv"
```

Nếu chưa chạy `git lfs pull`, các file trong `ETL/staging_data/*.csv` có thể chỉ là file pointer rất nhỏ của Git LFS, chưa phải dữ liệu CSV thật. Xem hướng dẫn chi tiết tại `GUILINE-GIT-LFS.md`.

## Nguồn tham khảo

- Kaggle: https://www.kaggle.com/datasets/rocki37/open-university-learning-analytics-dataset/
- OULAD official page: https://research.stem.open.ac.uk/ouanalyse/open-dataset-more/
- Paper: Kuzilek, J., Hlosta, M., & Zdrahal, Z. (2017). Open University Learning Analytics dataset. Scientific Data, 4, 170171. https://doi.org/10.1038/sdata.2017.171
