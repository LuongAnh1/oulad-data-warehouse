# Open University Learning Analytics Dataset - BTN

Repo này lưu trữ dữ liệu thô và tài liệu mô tả cho bộ **Open University Learning Analytics Dataset (OULAD)**, phục vụ việc tìm hiểu dữ liệu và chuẩn bị cho các bước phân tích hoặc xây dựng kho dữ liệu.

## Cấu trúc thư mục

```text
.
├── raw_data/
│   ├── assessments.csv
│   ├── courses.csv
│   ├── studentAssessment.csv
│   ├── studentInfo.csv
│   ├── studentRegistration.csv
│   ├── studentVle_0.csv
│   ├── studentVle_1.csv
│   ├── studentVle_2.csv
│   ├── studentVle_3.csv
│   ├── studentVle_4.csv
│   ├── studentVle_5.csv
│   ├── studentVle_6.csv
│   ├── studentVle_7.csv
│   └── vle.csv
└── docs/
    ├── oulad_raw_data.md
    ├── oulad_schema_relationships.md
    └── paper/
        ├── sdata2017171.pdf
        └── sdata2017171_mo_ta_vi.md
```

## Nội dung chính

### `raw_data/`

Chứa các file CSV gốc của OULAD. Bộ dữ liệu gồm 7 bảng chính:

- `courses`
- `assessments`
- `vle`
- `studentInfo`
- `studentRegistration`
- `studentAssessment`
- `studentVle`

Trong repo này, `studentVle` đang được tách thành 8 file `studentVle_0.csv` đến `studentVle_7.csv` vì bảng này rất lớn.

### `docs/oulad_raw_data.md`

Tài liệu tổng quan về bộ dữ liệu OULAD:

- nguồn dữ liệu,
- mô tả ngắn về OULAD,
- danh sách file CSV,
- số dòng/số cột,
- ý nghĩa tổng quan của từng bảng,
- lưu ý khi đọc dữ liệu bằng pandas.

### `docs/oulad_schema_relationships.md`

Tài liệu tập trung vào schema dữ liệu:

- ý nghĩa 7 bảng chính,
- ý nghĩa từng cột,
- khóa chính logic,
- khóa ngoại,
- quan hệ giữa các bảng,
- kiểm tra nhanh tính nhất quán khóa trên dữ liệu hiện tại.

### `docs/paper/`

Chứa bài báo gốc và bản diễn giải tiếng Việt:

- `sdata2017171.pdf`: bài báo *Open University Learning Analytics dataset*.
- `sdata2017171_mo_ta_vi.md`: bản mô tả/diễn giải tiếng Việt, không dịch từng câu.

## Lưu ý quan trọng về `studentVle`

Trong OULAD gốc, bảng `studentVle` thường là một file lớn. Ở repo này, file đó được chia thành:

```text
studentVle_0.csv
studentVle_1.csv
studentVle_2.csv
studentVle_3.csv
studentVle_4.csv
studentVle_5.csv
studentVle_6.csv
studentVle_7.csv
```

Các file này có thêm một cột index không tên ở đầu file. Khi đọc bằng pandas, nên dùng `index_col=0` hoặc bỏ cột index dư này trước khi phân tích.

Ví dụ:

```python
from pathlib import Path
import pandas as pd

data_dir = Path("raw_data")

student_vle = pd.concat(
    (
        pd.read_csv(path, index_col=0)
        for path in sorted(data_dir.glob("studentVle_*.csv"))
    ),
    ignore_index=True,
)
```

## Nguồn tham khảo

- Kaggle dataset: <https://www.kaggle.com/datasets/rocki37/open-university-learning-analytics-dataset/>
- OULAD official page: <https://research.stem.open.ac.uk/ouanalyse/open-dataset-more/>
- Paper: Kuzilek, J., Hlosta, M., & Zdrahal, Z. (2017). *Open University Learning Analytics dataset*. Scientific Data, 4, 170171. <https://doi.org/10.1038/sdata.2017.171>

