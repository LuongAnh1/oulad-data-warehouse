# ELT nhẹ cho giai đoạn chuẩn bị dữ liệu

## 1. Mục đích

Tài liệu này mô tả vì sao dự án không cần một quy trình ETL đầy đủ trước khi phân tích Open University Learning Analytics Dataset (OULAD), nhưng vẫn cần một bước ELT nhẹ để đưa dữ liệu về trạng thái sẵn sàng cho EDA và các phân tích tiếp theo.

Trong phạm vi hiện tại, ELT nhẹ được hiểu là:

- Giữ nguyên dữ liệu gốc trong `raw_data`.
- Load dữ liệu CSV vào môi trường phân tích.
- Chuẩn hóa tối thiểu sau khi load.
- Tạo các bảng trung gian hoặc biến phân tích cơ bản để phục vụ EDA.

ELT nhẹ không phải là bước xây dựng data warehouse hoàn chỉnh, cũng chưa phải là mô hình hóa fact/dimension chính thức.

## 2. Vì sao cần ELT nhẹ?

OULAD là bộ dữ liệu nghiên cứu đã được công bố sẵn dưới dạng CSV, có schema rõ ràng và đã được ẩn danh. Vì vậy nhóm có thể bắt đầu EDA sớm mà không cần trích xuất dữ liệu từ các hệ thống nguồn như trong dự án thực tế.

Tuy nhiên, nếu dùng trực tiếp dữ liệu thô mà không chuẩn bị trước, quá trình EDA dễ gặp các vấn đề sau:

- Một bảng logic có thể bị chia thành nhiều file, ví dụ `studentVle_0.csv` đến `studentVle_7.csv`.
- Một số file có cột index không tên phát sinh trong quá trình xuất dữ liệu.
- Kiểu dữ liệu khi đọc từ CSV có thể chưa đúng với ý nghĩa nghiệp vụ.
- Các cột ngày trong OULAD là ngày tương đối, không phải ngày lịch thật.
- Các bảng cần được kiểm tra khóa join trước khi phân tích chéo.
- Một số chỉ số EDA cần được tổng hợp từ dữ liệu giao dịch chi tiết, ví dụ tổng click theo tuần hoặc số bài nộp muộn.
- Nếu sau này chọn bài toán dự báo hoặc cảnh báo sớm, cần tránh dùng dữ liệu tương lai hoặc dùng `final_result` sai mục đích.

Vì vậy, ELT nhẹ giúp tạo một lớp dữ liệu đáng tin cậy hơn cho EDA, nhưng vẫn giữ phạm vi gọn và phù hợp với đặc thù của bộ dữ liệu.

## 3. ELT nhẹ hỗ trợ EDA như thế nào?

Trong dự án này, ELT nhẹ không tách rời EDA mà đóng vai trò chuẩn bị dữ liệu để EDA trả lời được các câu hỏi cơ bản một cách đáng tin cậy.

| Mục tiêu EDA | ELT nhẹ cần chuẩn bị |
|---|---|
| Phân bố dữ liệu | Chuẩn hóa kiểu dữ liệu và tạo các biến như tổng click, điểm, số bài nộp |
| Dữ liệu khuyết | Thống kê missing value và phân biệt missing hợp lệ với lỗi dữ liệu |
| Dữ liệu lạ hoặc ngoại lệ | Kiểm tra giá trị bất thường như `score`, `sum_click`, ngày nộp bài |
| Tương quan | Tạo bảng tổng hợp theo sinh viên để so sánh tương tác VLE, điểm và kết quả cuối |
| Mẫu theo thời gian | Gom dữ liệu theo tuần học hoặc checkpoint để quan sát xu hướng |
| Chuẩn hóa kiểu dữ liệu | Ép kiểu ID, nhóm phân loại, cột ngày tương đối và cột số |
| Trực quan hóa dữ liệu | Tạo bảng EDA-ready để vẽ biểu đồ nhanh và nhất quán |
| Nâng chất lượng dữ liệu | Ghi nhận vấn đề dữ liệu, duplicate, khóa join lỗi và quy tắc xử lý |

Nhờ bước này, EDA không chỉ là vẽ biểu đồ từ file CSV gốc, mà là phân tích trên một lớp dữ liệu đã được kiểm tra tối thiểu.

## 4. Khác nhau giữa ETL đầy đủ và ELT nhẹ trong dự án này

| Nội dung | ETL đầy đủ | ELT nhẹ trong dự án |
|---|---|---|
| Nguồn dữ liệu | Nhiều hệ thống vận hành | CSV OULAD đã có sẵn |
| Extract | Cần kết nối và trích xuất dữ liệu | Không cần, dữ liệu đã nằm trong `raw_data` |
| Transform | Làm sạch, chuẩn hóa, tích hợp sâu | Chỉ chuẩn hóa tối thiểu và tạo biến EDA |
| Load | Đưa vào kho dữ liệu chính thức | Đọc vào notebook/database tạm hoặc staging |
| Mục tiêu | Xây data warehouse vận hành lâu dài | Chuẩn bị dữ liệu cho EDA và phân tích ban đầu |

Với cách làm này, dự án đi theo hướng gần với ELT hơn: load dữ liệu thô trước, sau đó xử lý nhẹ trong môi trường phân tích.

## 5. Đầu mục công việc cần làm

### 5.1. Kiểm kê dữ liệu

- Liệt kê toàn bộ file CSV trong `raw_data`.
- Xác nhận đủ 7 bảng chính: `courses`, `assessments`, `vle`, `studentInfo`, `studentRegistration`, `studentAssessment`, `studentVle`.
- Ghi nhận các file bị chia nhỏ, đặc biệt là nhóm `studentVle`.
- Kiểm tra số dòng, số cột và tên cột của từng bảng.

### 5.2. Load dữ liệu thô

- Đọc từng file CSV bằng cấu hình thống nhất.
- Giữ nguyên bản dữ liệu gốc trong `raw_data`.
- Không sửa trực tiếp file thô.
- Nếu tạo dữ liệu trung gian, lưu ở một khu vực riêng như `staging` hoặc sinh ra trong notebook/script.

### 5.3. Gộp bảng bị chia nhỏ

- Gộp `studentVle_0.csv` đến `studentVle_7.csv` thành một bảng logic `studentVle`.
- Đảm bảo các file thành phần có cùng cấu trúc cột.
- Kiểm tra tổng số dòng sau khi gộp.

### 5.4. Loại bỏ cột kỹ thuật dư thừa

- Kiểm tra các cột như `Unnamed: 0` hoặc cột index không tên.
- Loại bỏ các cột này khỏi bảng dùng cho phân tích.
- Không xem các cột index phát sinh này là dữ liệu nghiệp vụ.

### 5.5. Chuẩn hóa kiểu dữ liệu

- Chuyển các cột định danh như `id_student`, `id_site`, `id_assessment` về kiểu số nguyên nếu phù hợp.
- Xem các cột như `code_module`, `code_presentation`, `assessment_type`, `final_result` là dữ liệu phân loại.
- Xử lý các cột ngày tương đối như `date`, `date_submitted`, `date_registration`, `date_unregistration`.
- Đảm bảo các cột số như `score`, `weight`, `sum_click` được đọc đúng kiểu.

### 5.6. Kiểm tra chất lượng dữ liệu

- Kiểm tra giá trị thiếu theo từng bảng và từng cột.
- Kiểm tra duplicate theo khóa logic.
- Kiểm tra giá trị bất thường, ví dụ `score` ngoài khoảng hợp lý hoặc `sum_click` âm.
- Phân biệt missing value hợp lệ với lỗi dữ liệu, ví dụ `date_unregistration` trống có thể hiểu là sinh viên không hủy đăng ký.

### 5.7. Kiểm tra quan hệ giữa các bảng

- Kiểm tra `studentInfo` nối được với `studentRegistration`.
- Kiểm tra `studentAssessment` nối được với `assessments`.
- Kiểm tra `studentVle` nối được với `vle`.
- Kiểm tra các khóa ghép gồm `code_module`, `code_presentation`, `id_student` khi phân tích theo sinh viên trong từng module-presentation.
- Ghi nhận các dòng không khớp khóa nếu có.

### 5.8. Tạo biến phục vụ EDA

- Tổng số click VLE theo sinh viên.
- Tổng số click theo tuần học hoặc mốc thời gian.
- Số ngày sinh viên có hoạt động VLE.
- Số loại tài nguyên VLE mà sinh viên đã tương tác.
- Số bài đánh giá đã nộp.
- Số bài nộp muộn.
- Điểm trung bình hoặc điểm có trọng số theo assessment.
- Nhóm kết quả cuối cùng từ `final_result`, ví dụ `Pass`, `Distinction`, `Fail`, `Withdrawn`.

### 5.9. Tạo bảng EDA-ready

Một số bảng trung gian có thể tạo để phục vụ EDA:

- `stg_courses`
- `stg_assessments`
- `stg_vle`
- `stg_student_info`
- `stg_student_registration`
- `stg_student_assessment`
- `stg_student_vle`
- `eda_student_summary`
- `eda_weekly_activity`
- `eda_assessment_progress`

Các bảng này không thay thế dữ liệu gốc. Chúng chỉ là lớp dữ liệu thuận tiện hơn cho phân tích.

## 6. Lưu ý nếu chọn bài toán dự báo hoặc cảnh báo sớm

Hiện tại nhóm chưa chốt bài toán nghiệp vụ cuối cùng. Tuy nhiên, nếu sau EDA nhóm chọn hướng dự báo kết quả học tập, rút học hoặc cảnh báo sớm sinh viên có nguy cơ `Fail`/`Withdrawn`, bước ELT nhẹ cần đặc biệt chú ý đến yếu tố thời gian:

- Không dùng dữ liệu phát sinh sau mốc phân tích để tạo chỉ số tại mốc đó.
- Không dùng `final_result` làm biến đầu vào cho mô hình dự báo hoặc cảnh báo.
- Khi tạo chỉ số theo tuần hoặc checkpoint, chỉ tổng hợp dữ liệu có `date` nhỏ hơn hoặc bằng mốc đó.
- Sinh viên đã `Withdrawn` trước một checkpoint không nên được đưa vào danh sách cần can thiệp tại checkpoint đó.
- Cần giữ riêng từng `code_module` và `code_presentation` khi so sánh.

## 7. Kết quả đầu ra mong muốn

Sau bước ELT nhẹ, nhóm nên có:

- Bộ dữ liệu đã load và kiểm tra được cấu trúc.
- Bảng `studentVle` đã gộp từ các file thành phần.
- Các bảng staging sạch hơn nhưng vẫn bám sát dữ liệu gốc.
- Báo cáo ngắn về chất lượng dữ liệu.
- Một số bảng hoặc biến tổng hợp sẵn sàng cho EDA.

Các kết quả này là nền tảng để thực hiện EDA, lựa chọn bài toán nghiệp vụ, thiết kế dashboard, tạo feature hoặc phát triển mô hình dữ liệu ở các bước sau.
