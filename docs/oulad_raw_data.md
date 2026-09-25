# Open University Learning Analytics Dataset (OULAD) - Raw Data

Thư mục này chứa dữ liệu thô của **Open University Learning Analytics Dataset (OULAD)**, được tải từ Kaggle và dựa trên bộ dữ liệu OULAD chính thức của The Open University.

## Nguồn dữ liệu

- Kaggle: <https://www.kaggle.com/datasets/rocki37/open-university-learning-analytics-dataset/>
- OULAD official description: <https://research.stem.open.ac.uk/ouanalyse/open-dataset-more/>
- Bài báo gốc cần trích dẫn khi sử dụng dữ liệu: Kuzilek, J., Hlosta, M., & Zdrahal, Z. (2017). *Open University Learning Analytics dataset*. Scientific Data, 4, 170171. <https://doi.org/10.1038/sdata.2017.171>
- License: CC-BY 4.0.

## Mô tả tổng quan

OULAD là bộ dữ liệu ẩn danh về học tập trực tuyến tại The Open University. Dữ liệu mô tả các khóa học, sinh viên, bài đánh giá, kết quả học tập và tương tác của sinh viên với hệ thống học trực tuyến Virtual Learning Environment (VLE).

Bộ dữ liệu gồm các bảng CSV được liên kết bằng các khóa định danh như `code_module`, `code_presentation`, `id_student`, `id_assessment` và `id_site`.

Một số đặc điểm chính:

- Gồm 7 module/khóa học được chọn.
- Có 22 module-presentation trong `courses.csv`.
- Presentation bắt đầu vào tháng 2 được ký hiệu bằng `B`; presentation bắt đầu vào tháng 10 được ký hiệu bằng `J`.
- Các mốc thời gian trong dữ liệu thường được đo theo số ngày so với ngày bắt đầu module-presentation, trong đó ngày bắt đầu là `0`.
- Dữ liệu VLE rất lớn, gồm 10,655,280 dòng tương tác của sinh viên.

## Các file trong thư mục này

| File | Số dòng dữ liệu | Số cột | Mô tả |
|---|---:|---:|---|
| `courses.csv` | 22 | 3 | Danh sách module và các lần mở lớp/presentation. |
| `assessments.csv` | 206 | 6 | Thông tin về các bài đánh giá trong từng module-presentation. |
| `vle.csv` | 6,364 | 6 | Danh mục tài nguyên học tập trên VLE. |
| `studentInfo.csv` | 32,593 | 12 | Thông tin nhân khẩu học và kết quả cuối cùng của sinh viên. |
| `studentRegistration.csv` | 32,593 | 5 | Thời điểm đăng ký và hủy đăng ký module-presentation của sinh viên. |
| `studentAssessment.csv` | 173,912 | 5 | Kết quả nộp bài và điểm đánh giá của sinh viên. |
| `studentVle_0.csv` - `studentVle_7.csv` | 10,655,280 tổng cộng | 7 trong file hiện tại | Log tương tác hằng ngày của sinh viên với tài nguyên VLE. |

Lưu ý: trong bộ dữ liệu gốc, bảng VLE của sinh viên thường là một file `studentVle.csv`. Ở thư mục này, file đó đã được chia thành 8 phần: `studentVle_0.csv` đến `studentVle_7.csv`. Các file này có thêm một cột index ở đầu file; khi đọc bằng pandas, cột này thường hiện là `Unnamed: 0`.

## Dictionary ngắn gọn theo bảng

### `courses.csv`

Thông tin các module-presentation.

- `code_module`: mã module.
- `code_presentation`: mã presentation, gồm năm và ký hiệu `B` hoặc `J`.
- `module_presentation_length`: độ dài presentation theo ngày.

### `assessments.csv`

Thông tin các bài đánh giá.

- `code_module`: mã module.
- `code_presentation`: mã presentation.
- `id_assessment`: mã bài đánh giá.
- `assessment_type`: loại bài đánh giá, gồm `TMA`, `CMA` hoặc `Exam`.
- `date`: hạn nộp, tính theo số ngày từ lúc bắt đầu module-presentation.
- `weight`: trọng số điểm của bài đánh giá.

### `vle.csv`

Thông tin tài nguyên học tập trên VLE.

- `id_site`: mã tài nguyên VLE.
- `code_module`: mã module.
- `code_presentation`: mã presentation.
- `activity_type`: loại hoặc vai trò của tài nguyên.
- `week_from`: tuần bắt đầu tài nguyên được dự kiến sử dụng.
- `week_to`: tuần kết thúc tài nguyên được dự kiến sử dụng.

### `studentInfo.csv`

Thông tin sinh viên và kết quả cuối cùng.

- `code_module`, `code_presentation`: module-presentation mà sinh viên đăng ký.
- `id_student`: mã sinh viên đã được ẩn danh.
- `gender`, `region`, `highest_education`, `imd_band`, `age_band`, `disability`: thông tin nhân khẩu học.
- `num_of_prev_attempts`: số lần sinh viên từng học lại module này.
- `studied_credits`: tổng số tín chỉ sinh viên đang học.
- `final_result`: kết quả cuối cùng, ví dụ `Pass`, `Fail`, `Withdrawn`, `Distinction`.

### `studentRegistration.csv`

Thông tin đăng ký học.

- `code_module`, `code_presentation`: module-presentation.
- `id_student`: mã sinh viên.
- `date_registration`: ngày đăng ký, tính tương đối so với ngày bắt đầu module-presentation. Giá trị âm nghĩa là đăng ký trước ngày bắt đầu.
- `date_unregistration`: ngày hủy đăng ký. Sinh viên hoàn thành khóa học thường để trống trường này.

### `studentAssessment.csv`

Kết quả bài đánh giá của sinh viên.

- `id_assessment`: mã bài đánh giá.
- `id_student`: mã sinh viên.
- `date_submitted`: ngày nộp bài, tính theo số ngày từ lúc bắt đầu module-presentation.
- `is_banked`: cờ cho biết điểm được chuyển từ presentation trước.
- `score`: điểm số từ 0 đến 100. Theo mô tả OULAD, điểm dưới 40 được hiểu là không đạt.

### `studentVle_0.csv` - `studentVle_7.csv`

Log tương tác của sinh viên với tài nguyên VLE.

- Cột đầu tiên không có tên: index dư khi file lớn được tách thành nhiều phần.
- `code_module`: mã module.
- `code_presentation`: mã presentation.
- `id_student`: mã sinh viên.
- `id_site`: mã tài nguyên VLE.
- `date`: ngày tương tác, tính theo số ngày từ lúc bắt đầu module-presentation.
- `sum_click`: số lượt tương tác/click của sinh viên với tài nguyên đó trong ngày.

## Quan hệ giữa các bảng

- `courses.csv` liên kết với các bảng khác bằng `code_module` và `code_presentation`.
- `assessments.csv` liên kết với `studentAssessment.csv` bằng `id_assessment`.
- `vle.csv` liên kết với `studentVle_*.csv` bằng `id_site`, đồng thời có thể đối chiếu thêm `code_module` và `code_presentation`.
- `studentInfo.csv`, `studentRegistration.csv`, `studentAssessment.csv` và `studentVle_*.csv` liên kết với nhau qua `id_student`.

## Gợi ý đọc dữ liệu bằng pandas

```python
from pathlib import Path
import pandas as pd

data_dir = Path("raw_data")

courses = pd.read_csv(data_dir / "courses.csv")
assessments = pd.read_csv(data_dir / "assessments.csv")
vle = pd.read_csv(data_dir / "vle.csv")
student_info = pd.read_csv(data_dir / "studentInfo.csv")
student_registration = pd.read_csv(data_dir / "studentRegistration.csv")
student_assessment = pd.read_csv(data_dir / "studentAssessment.csv")

student_vle = pd.concat(
    (
        pd.read_csv(path, index_col=0)
        for path in sorted(data_dir.glob("studentVle_*.csv"))
    ),
    ignore_index=True,
)
```

## Lưu ý khi phân tích

- Nên xử lý riêng các presentation `B` và `J` vì cấu trúc và thời lượng khóa học có thể khác nhau.
- Các cột ngày là ngày tương đối, không phải ngày lịch thực tế.
- `studentVle_0.csv` đến `studentVle_6.csv` là file lớn, nên một số editor có thể tắt syntax highlighting khi mở trực tiếp.
- Một số trường có giá trị thiếu, ví dụ `date_unregistration`, `imd_band`, `week_from`, `week_to`.
- Khi dùng các mảnh `studentVle_*.csv`, nên bỏ cột index dư ở đầu file trước khi phân tích.
