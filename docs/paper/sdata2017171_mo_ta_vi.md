# Diễn giải bài báo: Open University Learning Analytics Dataset

> Đây là bản diễn giải và mô tả có cấu trúc bằng tiếng Việt, không phải bản dịch từng câu. Nội dung dựa trên bài báo `sdata2017171.pdf`:  
> Kuzilek, J., Hlosta, M., & Zdrahal, Z. (2017). *Open University Learning Analytics dataset*. Scientific Data, 4, 170171. https://doi.org/10.1038/sdata.2017.171

## 1. Thông tin chung

Bài báo giới thiệu **Open University Learning Analytics Dataset (OULAD)**, một bộ dữ liệu mở phục vụ nghiên cứu trong lĩnh vực **Learning Analytics** - phân tích dữ liệu người học để hiểu hành vi học tập, dự đoán kết quả và hỗ trợ cải thiện trải nghiệm học.

Bộ dữ liệu được xây dựng từ dữ liệu của **The Open University (OU)**, một đại học đào tạo từ xa lớn tại Vương quốc Anh. Sinh viên học thông qua hệ thống trực tuyến **Virtual Learning Environment (VLE)**, nơi chứa tài liệu học, trang HTML, file PDF, bài tập, diễn đàn và các tài nguyên học tập khác. Những lần sinh viên tương tác với các tài nguyên này được ghi lại thành log.

Điểm nổi bật của OULAD là nó không chỉ có điểm số hay thông tin khóa học, mà kết hợp nhiều loại dữ liệu trong cùng một bộ:

- Thông tin nhân khẩu học của sinh viên.
- Thông tin đăng ký và hủy đăng ký module.
- Kết quả các bài đánh giá.
- Log tương tác hằng ngày với VLE.
- Thông tin về module, presentation và tài nguyên học tập.

Nhờ vậy, OULAD phù hợp cho các bài toán như dự đoán kết quả học tập, phát hiện sinh viên có nguy cơ rớt hoặc rút khỏi khóa học, phân tích hành vi học trực tuyến và đánh giá vai trò của VLE trong quá trình học.

## 2. Vì sao bộ dữ liệu này quan trọng?

Trong giáo dục đại học và học trực tuyến, các hệ thống quản lý học tập ngày càng thu thập nhiều dữ liệu về sinh viên. Tuy nhiên, nghiên cứu Learning Analytics cần các bộ dữ liệu mở, có cấu trúc rõ ràng và đủ chuẩn để những nghiên cứu khác nhau có thể so sánh kết quả.

Trước OULAD, một số bộ dữ liệu mở đã tồn tại, ví dụ:

- **KDD Cup 2010**: tập trung vào tương tác của sinh viên với hệ thống tutoring.
- **KDD Cup 2015**: dữ liệu từ nền tảng MOOC XuetangX, có cấu trúc khóa học và tương tác VLE, nhưng không có nhiều thông tin nhân khẩu học hay dữ liệu lịch sử từ các khóa học trước.

So với các bộ dữ liệu này, OULAD có điểm mạnh là kết hợp **dữ liệu nhân khẩu học**, **dữ liệu thành tích** và **dữ liệu hành vi học tập trên VLE**. Điều này giúp nhà nghiên cứu không chỉ nhìn thấy kết quả cuối cùng, mà còn quan sát được quá trình học của sinh viên theo thời gian.

## 3. Bối cảnh của The Open University

Tại OU, khóa học được gọi là **module**. Mỗi module có thể được mở nhiều lần trong các đợt học khác nhau; mỗi lần mở được gọi là **presentation**.

Mã presentation thường gồm năm và ký hiệu tháng bắt đầu. Ví dụ:

- `2013J`: presentation bắt đầu vào tháng 10 năm 2013.
- Trong OULAD, presentation bắt đầu vào tháng 2 thường được ký hiệu bằng `B`, còn presentation bắt đầu vào tháng 10 được ký hiệu bằng `J`.

Một module-presentation thường kéo dài khoảng 9 tháng. Tài nguyên học tập có thể được mở trên VLE trước ngày bắt đầu chính thức vài tuần. Sinh viên có thể đăng ký từ vài tháng trước khi module bắt đầu và thường vẫn có thể đăng ký trong một khoảng thời gian ngắn sau ngày bắt đầu.

Trong quá trình học, sinh viên làm nhiều bài đánh giá. Cuối module thường có bài thi cuối kỳ.

## 4. Phạm vi dữ liệu

OULAD gồm dữ liệu từ các năm **2013 và 2014**.

Theo bài báo, bộ dữ liệu chứa:

- 22 module-presentations.
- 32,593 sinh viên đã đăng ký.
- 173,912 bản ghi kết quả bài đánh giá.
- 10,655,280 bản ghi tương tác VLE được tổng hợp theo ngày.
- 7 module được chọn, gồm 4 module STEM và 3 module Social Sciences.

Bảng tóm tắt module trong bài báo:

| Module | Lĩnh vực | Số presentation | Số sinh viên |
|---|---|---:|---:|
| AAA | Social Sciences | 2 | 748 |
| BBB | Social Sciences | 4 | 7,909 |
| CCC | STEM | 2 | 4,434 |
| DDD | STEM | 4 | 6,272 |
| EEE | STEM | 3 | 2,934 |
| FFF | STEM | 4 | 7,762 |
| GGG | Social Sciences | 3 | 2,534 |

## 5. Cách chọn dữ liệu

Dữ liệu gốc được lấy từ data warehouse của OU, nơi tổng hợp dữ liệu từ nhiều hệ thống khác nhau của trường. Nhóm tác giả chia dữ liệu thành 3 nhóm lớn:

- **Demographic data**: thông tin cá nhân hoặc nhân khẩu học của sinh viên, như tuổi, giới tính, vùng địa lý, trình độ học vấn và tình trạng khuyết tật.
- **Performance data**: kết quả học tập, điểm bài đánh giá và kết quả cuối cùng.
- **Learning behaviour data**: hành vi học tập, cụ thể là log tương tác với VLE.

Không phải tất cả module của OU đều được đưa vào OULAD. Các module được chọn cần thỏa một số điều kiện:

- Mỗi module-presentation có hơn 500 sinh viên.
- Module có ít nhất 2 presentation.
- Có dữ liệu VLE cho module-presentation đó.
- Có số lượng sinh viên trượt hoặc học không đạt đủ đáng kể, phù hợp với bài toán dự đoán rủi ro.

Ban đầu có 38,239 sinh viên trong các module được chọn. Sau bước ẩn danh hóa, còn lại 32,593 sinh viên trong bộ dữ liệu công khai.

## 6. Ẩn danh hóa và bảo vệ riêng tư

Một phần quan trọng của bài báo là cách OU ẩn danh hóa dữ liệu trước khi công bố.

Nhóm tác giả loại bỏ các thông tin có thể nhận diện trực tiếp, chẳng hạn:

- Số an sinh xã hội.
- Ngày sinh.
- Mã định danh nội bộ của sinh viên tại OU.
- Tên module thật.
- Mốc thời gian tuyệt đối.

Thay vào đó:

- Tên module được thay bằng các mã không mang ý nghĩa như `AAA`, `BBB`, `CCC`.
- Thời gian được biểu diễn tương đối so với ngày bắt đầu module-presentation.
- Các mã định danh số được gán lại và xáo trộn ngẫu nhiên.

Ngoài các thông tin nhận diện trực tiếp, bài báo cũng chú ý đến **quasi-identifiers** - những thuộc tính riêng lẻ không đủ để nhận diện ai, nhưng khi kết hợp với nguồn dữ liệu khác có thể làm lộ danh tính.

Nhóm quasi-identifiers gồm:

- Giới tính.
- IMD band.
- Trình độ học vấn cao nhất.
- Nhóm tuổi.
- Vùng địa lý.
- Tình trạng khuyết tật.

Để xử lý các thuộc tính này, nhóm tác giả dùng **ARX anonymisation tool** và áp dụng **k-anonymity** với `k = 5`. Nói đơn giản, mỗi bản ghi sau ẩn danh hóa sẽ khó bị phân biệt với ít nhất một nhóm bản ghi tương tự, nhờ đó giảm rủi ro tái định danh cá nhân.

## 7. Cấu trúc bộ dữ liệu

OULAD được phát hành dưới dạng các file CSV riêng biệt. Mỗi file tương ứng với một bảng trong mô hình quan hệ. Các bảng liên kết với nhau bằng các khóa định danh.

Quan hệ chính:

- `studentInfo` là bảng trung tâm về sinh viên.
- `studentInfo`, `studentRegistration`, `studentAssessment` và `studentVle` có thể liên kết qua `id_student`.
- `courses` liên kết với các bảng khác qua `code_module` và `code_presentation`.
- `assessments` liên kết với `studentAssessment` qua `id_assessment`.
- `vle` liên kết với `studentVle` qua `id_site`.

Có thể hình dung bộ dữ liệu xoay quanh một bộ ba:

```text
student - module - presentation
```

Từ bộ ba này, ta có thể nối tiếp sang thông tin đăng ký, kết quả bài đánh giá, kết quả cuối cùng và hành vi click trên VLE.

## 8. Diễn giải từng bảng dữ liệu

### 8.1. `studentInfo`

Bảng này chứa thông tin nhân khẩu học của sinh viên và kết quả cuối cùng trong từng module-presentation.

Một dòng trong bảng có thể hiểu là: **một sinh viên đăng ký học một module trong một presentation cụ thể**.

Một số cột quan trọng:

- `id_student`: mã sinh viên đã ẩn danh.
- `code_module`: mã module.
- `code_presentation`: mã presentation.
- `gender`: giới tính.
- `region`: khu vực sinh sống.
- `highest_education`: trình độ học vấn cao nhất khi vào module.
- `imd_band`: nhóm chỉ số Index of Multiple Deprivation, liên quan đến mức độ thiếu thốn của khu vực sinh viên sinh sống.
- `age_band`: nhóm tuổi.
- `num_of_prev_attempts`: số lần sinh viên đã học module này trước đó.
- `studied_credits`: tổng số tín chỉ sinh viên đang học.
- `disability`: sinh viên có khai báo khuyết tật hay không.
- `final_result`: kết quả cuối cùng, ví dụ `Pass`, `Fail`, `Withdrawn`, `Distinction`.

Đây là bảng rất quan trọng nếu làm bài toán dự đoán kết quả học tập.

### 8.2. `courses`

Bảng này liệt kê các module và presentation có trong dữ liệu.

Cột chính:

- `code_module`: mã module.
- `code_presentation`: mã presentation.
- `module_presentation_length`: độ dài module-presentation tính theo ngày.

Bài báo lưu ý nên phân tích riêng presentation `B` và `J`, vì cấu trúc học, thời lượng, lịch đánh giá hoặc cách tổ chức có thể khác nhau.

### 8.3. `studentRegistration`

Bảng này cho biết sinh viên đăng ký và hủy đăng ký khi nào.

Cột chính:

- `date_registration`: ngày đăng ký, tính tương đối so với ngày bắt đầu module.
- `date_unregistration`: ngày hủy đăng ký. Nếu sinh viên hoàn thành khóa học, trường này thường để trống.

Giá trị ngày có thể âm. Ví dụ `-30` nghĩa là sinh viên đăng ký trước ngày module bắt đầu 30 ngày.

Bảng này hữu ích khi phân tích hành vi rút lui hoặc hủy học, đặc biệt khi kết hợp với `final_result = Withdrawn`.

### 8.4. `assessments`

Bảng này mô tả các bài đánh giá trong mỗi module-presentation.

Cột chính:

- `id_assessment`: mã bài đánh giá.
- `assessment_type`: loại bài đánh giá.
- `date`: hạn nộp bài, tính theo ngày tương đối.
- `weight`: trọng số điểm.

Có 3 loại đánh giá:

- `TMA`: Tutor Marked Assessment.
- `CMA`: Computer Marked Assessment.
- `Exam`: bài thi cuối kỳ.

Theo bài báo, nếu thông tin hạn của bài thi cuối kỳ bị thiếu, bài thi thường diễn ra vào tuần cuối của module-presentation.

### 8.5. `studentAssessment`

Bảng này ghi lại kết quả bài đánh giá của sinh viên.

Cột chính:

- `id_assessment`: liên kết với bảng `assessments`.
- `id_student`: mã sinh viên.
- `date_submitted`: ngày nộp bài.
- `is_banked`: điểm có được chuyển từ presentation trước hay không.
- `score`: điểm từ 0 đến 100.

Nếu sinh viên không nộp bài, sẽ không có bản ghi kết quả cho bài đó. Bài báo cũng nói kết quả bài thi cuối kỳ thường không có trong bảng này, vì nó được xử lý ngay cuối module để tính điểm tổng kết.

Theo mô tả của bài báo, điểm dưới 40 được hiểu là không đạt.

### 8.6. `studentVle`

Bảng `studentVle` là phần lớn nhất của bộ dữ liệu. Nó ghi lại tương tác hằng ngày của sinh viên với tài nguyên VLE.

Một dòng trong bảng có thể hiểu là: **trong một ngày cụ thể, một sinh viên đã tương tác bao nhiêu lần với một tài nguyên VLE cụ thể**.

Cột chính:

- `id_student`: mã sinh viên.
- `id_site`: mã tài nguyên VLE.
- `date`: ngày tương tác, tính tương đối so với ngày bắt đầu module-presentation.
- `sum_click`: số lần click hoặc tương tác trong ngày.

Bảng này rất hữu ích khi muốn phân tích:

- Mức độ tham gia học tập theo thời gian.
- Sinh viên học sớm hay học muộn.
- Mối quan hệ giữa tần suất truy cập VLE và kết quả cuối cùng.
- Dấu hiệu cảnh báo sớm về nguy cơ trượt hoặc rút lui.

Trong folder dữ liệu của dự án này, `studentVle` đang được tách thành nhiều file `studentVle_0.csv` đến `studentVle_7.csv`. Khi đọc bằng pandas, nên ghép các file lại và bỏ cột index dư nếu có.

### 8.7. `vle`

Bảng này mô tả các tài nguyên có trong VLE.

Cột chính:

- `id_site`: mã tài nguyên.
- `code_module`: mã module.
- `code_presentation`: mã presentation.
- `activity_type`: loại hoạt động hoặc vai trò của tài nguyên.
- `week_from`: tuần bắt đầu dự kiến sử dụng tài nguyên.
- `week_to`: tuần kết thúc dự kiến sử dụng tài nguyên.

Bảng này giúp biến các log click trong `studentVle` thành thông tin có ý nghĩa hơn. Ví dụ, thay vì chỉ biết sinh viên click vào `id_site = 546652`, ta có thể nối với `vle` để biết đó là loại tài nguyên nào.

## 9. Kiểm định kỹ thuật của bộ dữ liệu

Nhóm tác giả muốn kiểm tra xem dữ liệu OULAD từ năm 2013-2014 có còn phản ánh tương đối tốt sinh viên hiện tại hay không. Để làm việc này, họ so sánh module `CCC` trong OULAD với dữ liệu từ năm 2015.

Các thuộc tính trong `studentInfo` được so sánh bằng:

- Chi-squared test với các biến phân loại.
- Wilcoxon rank sum test với biến phù hợp.

Giả thuyết kiểm định là phân phối dữ liệu năm 2013/2014 và năm 2015 giống nhau. Kết quả p-value nằm trong khoảng khoảng 0.15 đến 0.93, nên không có bằng chứng thống kê rõ ràng cho thấy hai phân phối khác nhau.

Nói đơn giản: nhóm tác giả kết luận OULAD vẫn phản ánh khá tốt đặc điểm sinh viên trong bộ dữ liệu đối chiếu năm 2015.

## 10. Các cách sử dụng phù hợp

Bài báo gợi ý OULAD có thể được dùng cho nhiều hướng nghiên cứu:

- Dự đoán kết quả cuối cùng của sinh viên.
- Dự đoán điểm bài đánh giá.
- Phát hiện sớm sinh viên có nguy cơ `Fail` hoặc `Withdrawn`.
- Phân tích hành vi học tập trên VLE.
- So sánh mô hình dự đoán giữa các nghiên cứu khác nhau.
- Nghiên cứu ảnh hưởng của cấu trúc tài nguyên VLE đến kết quả học tập.

Với đồ án kho dữ liệu/data warehouse, bộ dữ liệu này cũng phù hợp để thực hành:

- Thiết kế schema quan hệ.
- Xây dựng ETL pipeline.
- Làm sạch và chuẩn hóa dữ liệu.
- Tổng hợp log VLE theo ngày, tuần, module hoặc sinh viên.
- Xây dựng bảng fact/dimension cho bài toán learning analytics.

## 11. Lưu ý khi làm việc với OULAD

Một số điểm cần nhớ khi sử dụng bộ dữ liệu:

- Các ngày trong dữ liệu là ngày tương đối, không phải ngày lịch thật.
- Tên module đã được ẩn danh thành `AAA`, `BBB`, ..., nên không thể suy ra tên môn học thật.
- Một sinh viên có thể xuất hiện nhiều dòng nếu học nhiều module-presentation.
- `studentVle` rất lớn, nên cần cân nhắc đọc theo chunk hoặc tổng hợp trước khi join.
- Các presentation `B` và `J` có thể có cấu trúc khác nhau, nên không nên mặc định chúng hoàn toàn giống nhau.
- Các trường như `date_unregistration`, `imd_band`, `week_from`, `week_to` có thể có giá trị thiếu.
- Với bài toán dự đoán sớm, cần tránh dùng thông tin xảy ra sau mốc thời gian dự đoán, vì sẽ gây rò rỉ dữ liệu.

## 12. Tóm tắt một câu

OULAD là một bộ dữ liệu học tập trực tuyến đã ẩn danh, kết hợp thông tin sinh viên, đăng ký, điểm đánh giá và clickstream VLE, giúp nghiên cứu mối quan hệ giữa hành vi học tập và kết quả của sinh viên trong môi trường giáo dục trực tuyến.
