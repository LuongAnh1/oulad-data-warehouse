# EDA - Exploratory Data Analysis

## 1. Mục đích

EDA là bước khám phá dữ liệu sau khi đã load và chuẩn bị dữ liệu ở mức tối thiểu. Với OULAD, mục tiêu của EDA là hiểu cấu trúc dữ liệu, phân bố kết quả học tập, mức độ tương tác VLE, tình trạng nộp bài và các hướng phân tích tiềm năng trước khi nhóm chốt bài toán nghiệp vụ.

EDA không nhằm kết luận quan hệ nhân quả. Kết quả của EDA dùng để:

- Hiểu đặc điểm chính của bộ dữ liệu.
- Phát hiện vấn đề chất lượng dữ liệu.
- Tìm các mẫu, xu hướng và mối liên hệ đáng chú ý.
- Đề xuất biến phân tích hoặc feature cho các bước sau.
- Hỗ trợ nhóm lựa chọn bài toán nghiệp vụ, thiết kế dashboard hoặc mô hình dữ liệu ở các bước sau.

## 2. Nguyên tắc khi EDA OULAD

- Giữ dữ liệu gốc trong `raw_data`, không chỉnh sửa trực tiếp file CSV gốc.
- Phân tích theo đúng đơn vị `student - module - presentation`.
- Không dùng riêng `id_student` để kết luận vì một sinh viên có thể học nhiều module-presentation.
- Phân biệt rõ dữ liệu dùng để mô tả lịch sử với dữ liệu có thể dùng cho dự báo hoặc cảnh báo sau này.
- Khi phân tích theo thời gian, chỉ dùng dữ liệu phát sinh đến mốc thời gian đang xét.
- Không dùng `final_result` như biến đầu vào nếu sau này chọn bài toán dự báo hoặc cảnh báo.
- Luôn ghi lại giả định, cách xử lý missing value và các vấn đề dữ liệu phát hiện được.

## 3. Các đầu mục công việc EDA

### 3.1. Tổng quan dữ liệu

Mục tiêu là nắm được bộ dữ liệu có những bảng nào, quy mô ra sao và mỗi bảng đang mô tả điều gì.

Công việc cần làm:

- Liệt kê 7 bảng chính: `courses`, `assessments`, `vle`, `studentInfo`, `studentRegistration`, `studentAssessment`, `studentVle`.
- Thống kê số dòng, số cột của từng bảng.
- Kiểm tra tên cột và kiểu dữ liệu ban đầu.
- Xác định khóa logic và các cặp bảng có thể join.
- Kiểm tra số lượng `code_module`, `code_presentation`, `id_student`, `id_assessment`, `id_site`.
- Tóm tắt vai trò từng bảng trong bài toán phân tích.

Kết quả mong muốn:

- Bảng tổng hợp quy mô dữ liệu.
- Ghi chú ngắn về ý nghĩa từng bảng.
- Danh sách các khóa join chính.

### 3.2. Phân bố dữ liệu

Mục tiêu là hiểu dữ liệu đang phân bố như thế nào, có bị lệch nhóm hay mất cân bằng không.

Công việc cần làm:

- Phân bố `final_result`: `Pass`, `Distinction`, `Fail`, `Withdrawn`.
- Phân bố sinh viên theo `code_module` và `code_presentation`.
- Phân bố điểm `score` trong `studentAssessment`.
- Phân bố trọng số bài đánh giá `weight`.
- Phân bố số lần tương tác `sum_click`.
- Phân bố loại tài nguyên VLE qua `activity_type`.
- Phân bố thông tin nền của sinh viên như `gender`, `region`, `highest_education`, `imd_band`, `age_band`, `disability`.
- So sánh phân bố giữa các module-presentation.

Biểu đồ gợi ý:

- Bar chart cho biến phân loại.
- Histogram cho điểm và số click.
- Boxplot cho `score` và `sum_click`.
- Stacked bar chart cho `final_result` theo module hoặc presentation.

### 3.3. Phát hiện dữ liệu khuyết và xử lý

Mục tiêu là biết dữ liệu thiếu ở đâu, thiếu có hợp lý không và cần xử lý như thế nào.

Công việc cần làm:

- Thống kê số lượng và tỷ lệ missing value theo từng cột.
- Kiểm tra `date_unregistration`: giá trị thiếu thường có nghĩa là sinh viên không hủy đăng ký.
- Kiểm tra `score`: missing có thể xuất hiện khi bài đánh giá chưa có điểm hoặc không nộp.
- Kiểm tra `date_submitted`: missing có thể liên quan đến việc chưa nộp assessment.
- Kiểm tra các biến nền như `imd_band` có missing hay không.
- Phân loại missing value thành missing hợp lệ, missing cần xử lý và missing cần ghi chú.

Hướng xử lý:

- Không xóa dòng chỉ vì có missing nếu missing đó có ý nghĩa nghiệp vụ.
- Tạo cờ như `is_unregistered`, `is_missing_score`, `is_missing_imd_band` nếu cần phân tích.
- Ghi rõ quy tắc xử lý trong notebook hoặc báo cáo EDA.

### 3.4. Phát hiện dữ liệu ngoại lệ

Mục tiêu là phát hiện giá trị bất thường có thể ảnh hưởng đến thống kê và biểu đồ.

Công việc cần làm:

- Kiểm tra `score` ngoài khoảng hợp lý.
- Kiểm tra `sum_click` bằng 0, quá cao hoặc âm.
- Kiểm tra ngày nộp bài `date_submitted` quá sớm hoặc quá muộn so với hạn `date`.
- Kiểm tra sinh viên có tương tác VLE rất cao hoặc rất thấp.
- Kiểm tra assessment có trọng số `weight` bất thường.
- So sánh outlier theo từng module-presentation thay vì chỉ nhìn toàn bộ dữ liệu.

Biểu đồ gợi ý:

- Boxplot theo module.
- Histogram có giới hạn trục.
- Scatter plot giữa `sum_click` và `score`.

Lưu ý:

- Không tự động xóa outlier.
- Với OULAD, outlier có thể là hành vi học tập thật, ví dụ một sinh viên truy cập VLE rất nhiều trước kỳ đánh giá.

### 3.5. Phân tích tương quan

Mục tiêu là tìm các mối liên hệ ban đầu giữa hoạt động học tập, kết quả đánh giá và kết quả cuối cùng.

Công việc cần làm:

- Tính tương quan giữa tổng `sum_click` và `score`.
- So sánh mức độ tương tác VLE giữa các nhóm `final_result`.
- So sánh điểm assessment giữa nhóm `Pass`, `Distinction`, `Fail`, `Withdrawn`.
- Phân tích quan hệ giữa số ngày có hoạt động VLE và kết quả cuối.
- Phân tích quan hệ giữa nộp muộn assessment và kết quả cuối.
- Kiểm tra tương quan riêng theo từng module-presentation.

Biểu đồ gợi ý:

- Heatmap tương quan cho biến số.
- Boxplot `sum_click` theo `final_result`.
- Scatter plot `sum_click` và `score`.
- Grouped bar chart cho tỷ lệ kết quả cuối theo nhóm mức độ tương tác.

Lưu ý:

- Tương quan không có nghĩa là nguyên nhân.
- Với biến phân loại, nên dùng bảng chéo, tỷ lệ phần trăm hoặc biểu đồ nhóm thay vì chỉ dùng correlation matrix.

### 3.6. Phân tích mẫu và xu hướng theo thời gian

Mục tiêu là hiểu hành vi học tập thay đổi như thế nào theo tiến trình môn học.

Công việc cần làm:

- Tổng hợp `sum_click` theo tuần học.
- Theo dõi số sinh viên còn hoạt động qua từng tuần.
- Phân tích xu hướng tương tác trước các mốc assessment.
- So sánh xu hướng VLE giữa nhóm `Pass`, `Fail` và `Withdrawn`.
- Phát hiện giai đoạn sinh viên bắt đầu giảm tương tác.
- Phân tích tỷ lệ hủy đăng ký theo thời gian.
- Tạo các checkpoint như ngày 14, 28, 42 và 56 nếu sau này nhóm chọn bài toán dự báo hoặc cảnh báo sớm.

Biểu đồ gợi ý:

- Line chart tổng click theo tuần.
- Line chart số sinh viên active theo tuần.
- Area chart hoặc stacked chart theo nhóm kết quả cuối.
- Heatmap tuần học và module-presentation.

Lưu ý:

- Các cột ngày trong OULAD là ngày tương đối, không phải ngày lịch thật.
- Nếu phân tích theo hướng dự báo hoặc cảnh báo sớm, không dùng dữ liệu sau checkpoint.

### 3.7. Chuẩn hóa kiểu dữ liệu

Mục tiêu là đảm bảo dữ liệu được đọc đúng kiểu để thống kê và trực quan hóa không bị sai.

Công việc cần làm:

- Kiểm tra kiểu dữ liệu sau khi đọc CSV.
- Chuyển các cột ID như `id_student`, `id_site`, `id_assessment` về kiểu phù hợp.
- Xem `code_module`, `code_presentation`, `assessment_type`, `activity_type`, `final_result` là biến phân loại.
- Xử lý các cột ngày tương đối như số nguyên.
- Chuyển `score`, `weight`, `sum_click` về kiểu số.
- Kiểm tra lại kiểu dữ liệu sau khi gộp các file `studentVle`.

Kết quả mong muốn:

- Bảng dữ liệu có kiểu dữ liệu nhất quán.
- Danh sách cột cần ép kiểu và lý do ép kiểu.

### 3.8. Trực quan hóa dữ liệu

Mục tiêu là trình bày kết quả EDA rõ ràng, dễ hiểu và hỗ trợ ra quyết định.

Công việc cần làm:

- Vẽ biểu đồ phân bố kết quả cuối.
- Vẽ biểu đồ điểm assessment.
- Vẽ biểu đồ tổng click VLE.
- Vẽ biểu đồ tương tác theo tuần học.
- Vẽ biểu đồ so sánh các nhóm kết quả cuối.
- Vẽ biểu đồ missing value nếu cần.
- Vẽ dashboard hoặc nhóm biểu đồ tổng hợp cho module-presentation.

Nguyên tắc trình bày:

- Mỗi biểu đồ nên trả lời một câu hỏi rõ ràng.
- Ghi rõ đơn vị phân tích và bộ lọc đang dùng.
- Không đưa quá nhiều biến vào một biểu đồ.
- So sánh theo module-presentation khi khác biệt giữa các môn học có thể ảnh hưởng kết quả.

### 3.9. Nâng chất lượng dữ liệu

Mục tiêu là ghi nhận và xử lý tối thiểu các vấn đề làm EDA sai lệch.

Công việc cần làm:

- Ghi lại các vấn đề dữ liệu phát hiện được.
- Kiểm tra duplicate theo khóa logic.
- Kiểm tra khóa ngoại không khớp giữa các bảng.
- Ghi lại quy tắc xử lý missing value.
- Ghi lại quy tắc xử lý outlier.
- Tạo bảng dữ liệu EDA-ready nếu cần.
- Tách rõ dữ liệu gốc, dữ liệu staging và dữ liệu dùng cho biểu đồ.

Kết quả mong muốn:

- Danh sách data quality issues.
- Quy tắc xử lý dữ liệu đã thống nhất.
- Bộ dữ liệu sẵn sàng cho phân tích sâu hơn.

## 4. Kết quả đầu ra của EDA

Sau khi hoàn thành EDA, nhóm nên có:

- Notebook hoặc script EDA có thể chạy lại.
- Bảng thống kê mô tả các bảng dữ liệu chính.
- Các biểu đồ quan trọng.
- Báo cáo missing value và outlier.
- Nhận xét về phân bố kết quả học tập.
- Nhận xét về mối liên hệ giữa VLE, assessment và kết quả cuối.
- Danh sách biến tiềm năng cho bài toán nghiệp vụ sẽ được nhóm chọn sau EDA.
- Các vấn đề dữ liệu cần lưu ý ở bước sau.

## 5. Thứ tự thực hiện gợi ý

1. Kiểm kê dữ liệu và kiểm tra schema.
2. Chuẩn hóa kiểu dữ liệu tối thiểu.
3. Kiểm tra missing value và duplicate.
4. Phân tích phân bố dữ liệu.
5. Phân tích outlier.
6. Phân tích tương quan.
7. Phân tích xu hướng theo thời gian.
8. Trực quan hóa các phát hiện chính.
9. Tổng hợp insight và vấn đề dữ liệu.
10. Đề xuất biến hoặc hướng phân tích tiếp theo.

## 6. Phần đã thực hiện

### 6.0. Luồng đọc khuyến nghị

Nếu chỉ cần nắm kết quả chính:

1. Đọc `EDA/README.md` để hiểu phạm vi và nguyên tắc EDA.
2. Đọc file `*_report.md` của từng phần để nắm tóm tắt, dữ liệu đầu vào, bảng và biểu đồ đã sinh.
3. Đọc file `*_insights.md` của từng phần để hiểu biểu đồ nói gì, vì sao đáng chú ý và nên dùng kết quả đó thế nào.
4. Mở thư mục `EDA/outputs/figures/` khi cần xem hình minh chứng.
5. Mở thư mục `EDA/outputs/tables/` khi cần kiểm tra số liệu chi tiết.

Nếu thời gian ít, đọc trọng tâm theo thứ tự:

- [02_distribution_insights.md](docs/02-distribution/02_distribution_insights.md)
- [03_missing_values_insights.md](docs/03-missing-values/03_missing_values_insights.md)
- [04_outliers_insights.md](docs/04-outliers/04_outliers_insights.md)

Các notebook trong `EDA/notebooks/` dùng để chạy lại và xem kết quả tương tác. Các script trong `EDA/src/` là nguồn tạo lại bảng, biểu đồ, report và insight.

### 6.1. Phân bố dữ liệu

Script chính:

```powershell
python EDA\src\02_analyze_distributions.py
```

Notebook:

- `EDA/notebooks/02_distribution_eda.ipynb`

Đầu vào chính:

- `ETL/eda_data/eda_student_summary.csv`
- `ETL/eda_data/eda_weekly_activity.csv`
- `ETL/eda_data/eda_assessment_progress.csv`
- `ETL/staging_data/assessments.csv`
- `ETL/staging_data/vle.csv`
- `ETL/staging_data/studentVle.csv`

Đầu ra:

- Report: `EDA/docs/02-distribution/02_distribution_report.md`
- Insights: [02_distribution_insights.md](docs/02-distribution/02_distribution_insights.md)
- Checklist: `EDA/docs/02-distribution/02_distribution_checklist.md`
- Bảng thống kê: `EDA/outputs/tables/02_distribution/`
- Biểu đồ: `EDA/outputs/figures/02_distribution/`

Ghi chú: các biểu đồ click dùng `log1p` để giảm ảnh hưởng của phân bố lệch phải.
Phần này cũng đã bổ sung boxplot, ECDF, heatmap và bubble chart để tránh phụ thuộc quá nhiều vào bar chart.

### 6.2. Phát hiện dữ liệu khuyết

Script chính:

```powershell
python EDA\src\03_detect_missing_values.py
```

Notebook:

- `EDA/notebooks/03_missing_values_eda.ipynb`

Đầu vào chính:

- `ETL/staging_data/*.csv`
- `ETL/eda_data/eda_student_summary.csv`
- `ETL/eda_data/eda_weekly_activity.csv`
- `ETL/eda_data/eda_assessment_progress.csv`

Đầu ra:

- Report: `EDA/docs/03-missing-values/03_missing_values_report.md`
- Insights: [03_missing_values_insights.md](docs/03-missing-values/03_missing_values_insights.md)
- Checklist: `EDA/docs/03-missing-values/03_missing_values_checklist.md`
- Bảng thống kê: `EDA/outputs/tables/03_missing_values/`
- Biểu đồ: `EDA/outputs/figures/03_missing_values/`

Ghi chú: phần này phân biệt missing hợp lệ theo nghiệp vụ, ví dụ `date_unregistration`, với missing cần xử lý rõ khi phân tích, ví dụ `score`, `imd_band`, `avg_score`, `weighted_score`.
Heatmap missing matrix được dùng để nhìn nhanh cột nào thiếu ở bảng nào.

### 6.3. Phát hiện dữ liệu ngoại lệ

Script chính:

```powershell
python EDA\src\04_detect_outliers.py
```

Notebook:

- `EDA/notebooks/04_outliers_eda.ipynb`

Đầu vào chính:

- `ETL/eda_data/eda_student_summary.csv`
- `ETL/eda_data/eda_weekly_activity.csv`
- `ETL/eda_data/eda_assessment_progress.csv`
- `ETL/staging_data/assessments.csv`
- `ETL/staging_data/studentVle.csv`

Đầu ra:

- Report: `EDA/docs/04-outliers/04_outliers_report.md`
- Insights: [04_outliers_insights.md](docs/04-outliers/04_outliers_insights.md)
- Checklist: `EDA/docs/04-outliers/04_outliers_checklist.md`
- Bảng thống kê: `EDA/outputs/tables/04_outliers/`
- Biểu đồ: `EDA/outputs/figures/04_outliers/`

Ghi chú: phần này chỉ phát hiện và gắn cờ ngoại lệ. Không xóa outlier tự động vì với OULAD, tương tác VLE rất cao hoặc nộp bài rất sớm/muộn có thể là hành vi học tập thật.
Heatmap và scatter plot được dùng để so sánh tín hiệu ngoại lệ giữa các module-presentation rõ hơn so với chỉ dùng biểu đồ cột.
