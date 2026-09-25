# Yêu cầu nghiệp vụ - Cảnh báo sớm sinh viên có nguy cơ không hoàn thành môn học

## 1. Mục đích tài liệu

Tài liệu này xác định bài toán nghiệp vụ mà nhóm sẽ giải quyết bằng Open University Learning Analytics Dataset (OULAD). Nội dung tập trung vào nhu cầu ra quyết định, phạm vi, quy tắc nghiệp vụ, chỉ số, dữ liệu đầu vào và tiêu chí nghiệm thu. Thiết kế kho dữ liệu, ETL, dashboard hoặc mô hình dự đoán phải được xây dựng từ các yêu cầu này.

## 2. Bài toán nghiệp vụ được chọn

> Xây dựng hệ thống phân tích cảnh báo sớm giúp đội ngũ học vụ và giảng viên nhận diện, giải thích và ưu tiên hỗ trợ những sinh viên đang học có nguy cơ nhận kết quả `Fail` hoặc `Withdrawn`, dựa trên tiến độ đánh giá và mức độ tham gia VLE quan sát được đến từng mốc thời gian.

Hệ thống không tự động kết luận một sinh viên chắc chắn sẽ thất bại. Kết quả là một danh sách ưu tiên hỗ trợ kèm các tín hiệu giải thích được để con người xem xét trước khi can thiệp.

## 3. Vì sao chọn bài toán này?

OULAD phù hợp trực tiếp với bài toán cảnh báo sớm vì dữ liệu mô tả đầy đủ quá trình học theo thời gian:

- 32.593 lượt sinh viên tham gia 22 module-presentation thuộc 7 module.
- 173.912 kết quả bài đánh giá.
- 10.655.280 dòng tương tác VLE được tổng hợp theo ngày.
- Kết quả cuối cùng gồm `Pass`, `Distinction`, `Fail` và `Withdrawn`.
- Có thời điểm đăng ký, hủy đăng ký, hạn bài, ngày nộp bài và ngày tương tác VLE theo cùng một trục ngày tương đối.

Bài toán này tạo ra một quyết định nghiệp vụ cụ thể: tại mỗi mốc theo dõi, đội ngũ học vụ cần biết nên xem xét hỗ trợ sinh viên nào trước và vì sao.

## 4. Mục tiêu nghiệp vụ

### 4.1. Mục tiêu chính

- Phát hiện sớm dấu hiệu giảm tham gia, chậm tiến độ hoặc kết quả đánh giá yếu khi sinh viên vẫn còn đang học.
- Xếp hạng mức độ ưu tiên để đội ngũ học vụ sử dụng nguồn lực hỗ trợ hiệu quả hơn.
- Cung cấp bằng chứng giải thích cho mỗi cảnh báo, thay vì chỉ đưa ra một điểm rủi ro khó diễn giải.
- Theo dõi tỷ lệ `Fail` và `Withdrawn` theo module, presentation, tuần học và nhóm sinh viên.
- Tạo nền tảng dữ liệu nhất quán để đánh giá chất lượng cảnh báo bằng kết quả lịch sử.

### 4.2. Mục tiêu không thuộc phạm vi

- Không tự động gửi cảnh báo hoặc áp dụng biện pháp bất lợi cho sinh viên.
- Không chẩn đoán nguyên nhân tâm lý, tài chính, sức khỏe hoặc hoàn cảnh cá nhân.
- Không đánh giá hiệu quả thực tế của một chương trình can thiệp, vì OULAD không có dữ liệu về hoạt động can thiệp và phản hồi sau can thiệp.
- Không suy luận tên thật của module, sinh viên hoặc thời gian lịch tuyệt đối đã bị ẩn danh.
- Không dùng dữ liệu 2013-2014 để khẳng định mô hình sẽ hoạt động tương đương trên một trường hoặc giai đoạn khác nếu chưa kiểm định lại.

## 5. Đối tượng sử dụng và quyết định cần hỗ trợ

| Đối tượng | Nhu cầu | Quyết định được hỗ trợ |
|---|---|---|
| Nhân viên hỗ trợ học tập | Có danh sách sinh viên cần xem xét theo mức ưu tiên | Liên hệ hoặc chuyển sinh viên đến hình thức hỗ trợ phù hợp |
| Giảng viên/tutor | Hiểu tín hiệu dẫn đến cảnh báo | Kiểm tra tình trạng nộp bài, mức tham gia và bối cảnh học tập trước khi hỗ trợ |
| Quản lý module | Theo dõi xu hướng theo tuần và presentation | Điều chỉnh kế hoạch hỗ trợ hoặc xem lại các giai đoạn có nhiều sinh viên mất tương tác |
| Nhóm phân tích dữ liệu | Đo chất lượng dữ liệu và cảnh báo | Hiệu chỉnh quy tắc, ngưỡng hoặc mô hình cho từng module-presentation |

Sinh viên là đối tượng chịu tác động nhưng không phải người sử dụng trực tiếp trong phạm vi MVP. Mọi hành động liên quan đến sinh viên phải có con người xem xét.

## 6. Đơn vị phân tích và trục thời gian

### 6.1. Đơn vị theo dõi

Một đối tượng được theo dõi là:

```text
student - module - presentation - checkpoint_date
```

Khóa nghiệp vụ tương ứng:

```text
(code_module, code_presentation, id_student, checkpoint_date)
```

Không được dùng riêng `id_student` làm đơn vị phân tích vì một sinh viên có thể tham gia nhiều module-presentation.

### 6.2. Mốc theo dõi

- `checkpoint_date` là số ngày tương đối so với ngày bắt đầu module-presentation.
- MVP tạo snapshot vào cuối mỗi tuần học.
- Các mốc báo cáo chính là ngày 14, 28, 42 và 56.
- Chỉ dữ liệu phát sinh vào hoặc trước `checkpoint_date` mới được dùng để tạo chỉ số và cảnh báo tại mốc đó.
- Presentation `B` và `J` phải được giữ riêng khi so sánh vì lịch học và cấu trúc đánh giá có thể khác nhau.

### 6.3. Sinh viên đang hoạt động tại một checkpoint

Một sinh viên được xem là đang hoạt động tại ngày `t` khi:

```text
date_registration <= t
AND (date_unregistration IS NULL OR date_unregistration > t)
```

Sinh viên đã hủy đăng ký vào hoặc trước ngày `t` không xuất hiện trong danh sách cần can thiệp tại `t`, nhưng vẫn được tính trong báo cáo lịch sử về rút học.

## 7. Định nghĩa kết quả mục tiêu

### 7.1. Kết quả bất lợi

```text
adverse_outcome = 1 nếu final_result thuộc {Fail, Withdrawn}
adverse_outcome = 0 nếu final_result thuộc {Pass, Distinction}
```

Trong phân tích chi tiết, `Fail` và `Withdrawn` phải được giữ thành hai nhóm riêng vì chúng biểu thị hai loại vấn đề khác nhau.

### 7.2. Nhãn dùng để đánh giá cảnh báo tại ngày t

- `Fail`: được xem là trường hợp rủi ro tại mọi checkpoint trước khi kết thúc môn.
- `Withdrawn` với `date_unregistration > t`: là trường hợp rút học trong tương lai và được xem là rủi ro tại `t`.
- `Withdrawn` với `date_unregistration <= t`: đã xảy ra, không còn là trường hợp cần dự báo tại `t`.
- `Pass` và `Distinction`: là nhóm không có kết quả bất lợi.

`final_result` và thông tin rút học trong tương lai chỉ được dùng để đánh giá lịch sử, tuyệt đối không được dùng làm tín hiệu đầu vào của cảnh báo.

## 8. Quy trình nghiệp vụ mục tiêu

1. Hệ thống tạo snapshot cho từng sinh viên đang hoạt động tại checkpoint.
2. Hệ thống tổng hợp tín hiệu VLE, tiến độ nộp bài và kết quả đã biết đến checkpoint.
3. Hệ thống gắn các cờ rủi ro có thể giải thích và tính mức ưu tiên.
4. Người dùng lọc danh sách theo module, presentation, checkpoint và mức ưu tiên.
5. Người dùng xem lý do cảnh báo trước khi quyết định hỗ trợ.
6. Sau khi có kết quả cuối cùng, nhóm phân tích đối chiếu cảnh báo với `Fail`/`Withdrawn` để đánh giá và hiệu chỉnh.

OULAD không có dữ liệu can thiệp, vì vậy MVP kết thúc ở bước tạo danh sách và đánh giá cảnh báo lịch sử; không đo tác động sau hỗ trợ.

## 9. Câu hỏi nghiệp vụ cần trả lời

1. Tại mỗi checkpoint, sinh viên đang hoạt động nào cần được ưu tiên xem xét hỗ trợ?
2. Cảnh báo của từng sinh viên xuất phát từ mất tương tác VLE, bỏ lỡ đánh giá, điểm thấp hay sự kết hợp của nhiều tín hiệu?
3. Tỷ lệ `Fail` và `Withdrawn` thay đổi thế nào giữa các module-presentation?
4. Từ tuần nào nhóm có kết quả bất lợi bắt đầu khác biệt rõ so với nhóm `Pass`/`Distinction` về mức độ tham gia VLE?
5. Những loại tài nguyên VLE nào được các nhóm kết quả sử dụng khác nhau?
6. Tiến độ nộp bài, tỷ lệ nộp muộn và điểm tích lũy liên quan thế nào đến kết quả cuối cùng?
7. Cảnh báo có hoạt động ổn định giữa presentation `B` và `J`, giữa các module và giữa các nhóm sinh viên hay không?
8. Tại cùng một năng lực hỗ trợ giới hạn, danh sách ưu tiên bắt được bao nhiêu trường hợp `Fail`/`Withdrawn` trong tương lai?

## 10. Các tín hiệu cảnh báo trong MVP

Các tín hiệu dưới đây được tính tại checkpoint `t`; không sử dụng dữ liệu sau `t`.

### 10.1. Tương tác VLE

- `clicks_7d`, `clicks_14d`, `clicks_28d`: tổng `sum_click` trong các cửa sổ gần nhất.
- `active_days_14d`: số ngày có ít nhất một tương tác trong 14 ngày gần nhất.
- `days_since_last_activity`: số ngày từ lần tương tác gần nhất đến checkpoint.
- `click_change_7d`: mức thay đổi lượt click của 7 ngày gần nhất so với 7 ngày liền trước.
- `resource_type_count_14d`: số loại `activity_type` đã tương tác trong 14 ngày gần nhất.
- `inactive_14d`: cờ không có tương tác VLE trong 14 ngày gần nhất.

Không được xem `sum_click` là thời lượng học hay chất lượng học; đây chỉ là chỉ báo mức tương tác được hệ thống ghi nhận.

### 10.2. Tiến độ đánh giá

- `assessments_due`: số bài có hạn nộp vào hoặc trước checkpoint.
- `assessments_submitted`: số bài đến hạn đã có bản ghi nộp vào hoặc trước checkpoint.
- `missed_assessments`: số bài đã đến hạn nhưng không có bản ghi nộp.
- `late_submissions`: số bài được nộp sau hạn nhưng không sau checkpoint.
- `due_weight`: tổng trọng số của các bài đã đến hạn.
- `submitted_weight`: tổng trọng số của các bài đã nộp.
- `weighted_score_to_date`: điểm trung bình có trọng số của các bài đã có kết quả đến checkpoint.
- `failed_assessments`: số bài có `score < 40`.

Không được gắn cờ bỏ lỡ bài đánh giá trước hạn nộp. Bản ghi có `is_banked = 1` phải được giữ riêng để tránh xem điểm chuyển từ presentation trước như hành vi nộp bài hiện tại.

### 10.3. Bối cảnh đăng ký và học tập

- Ngày đăng ký so với ngày bắt đầu module.
- Số lần học module trước đó (`num_of_prev_attempts`).
- Tổng số tín chỉ đang học (`studied_credits`).
- Module, presentation và độ dài presentation.

Các biến nhân khẩu học được dùng để phân tích độ bao phủ và công bằng của cảnh báo. Trong MVP, `gender`, `region`, `imd_band`, `age_band` và `disability` không được dùng làm lý do duy nhất để tăng mức ưu tiên của một cá nhân.

## 11. Quy tắc xếp mức ưu tiên ban đầu

MVP sử dụng các cờ minh bạch trước khi cân nhắc mô hình học máy:

- `flag_inactive`: không có tương tác VLE trong 14 ngày gần nhất.
- `flag_missed_assessment`: có ít nhất một bài đã đến hạn nhưng chưa nộp.
- `flag_low_score`: điểm trung bình có trọng số đến hiện tại dưới 40, khi đã có điểm.
- `flag_engagement_drop`: lượt click 7 ngày gần nhất giảm ít nhất 50% so với 7 ngày liền trước và cửa sổ trước có hoạt động.

Mức ưu tiên mặc định:

| Mức | Quy tắc ban đầu | Ý nghĩa sử dụng |
|---|---|---|
| Cao | Có `flag_missed_assessment`, hoặc có từ 2 cờ rủi ro trở lên | Xem xét trước trong danh sách hỗ trợ |
| Trung bình | Có đúng 1 cờ rủi ro khác `flag_missed_assessment` | Theo dõi và xem thêm bối cảnh |
| Thấp | Không có cờ rủi ro | Chưa cần ưu tiên, vẫn tiếp tục theo dõi |

Các ngưỡng phải có thể cấu hình theo module-presentation. Nhóm phải đánh giá quy tắc trên dữ liệu lịch sử trước khi trình bày nó như một cơ chế cảnh báo hữu ích; không mặc định rằng một ngưỡng phù hợp với mọi module.

## 12. Yêu cầu chức năng

| Mã | Yêu cầu |
|---|---|
| FR-01 | Tạo snapshot hằng tuần cho mỗi sinh viên đang hoạt động trong từng module-presentation. |
| FR-02 | Tổng hợp tương tác VLE theo checkpoint, cửa sổ thời gian và loại tài nguyên. |
| FR-03 | Xác định bài đã đến hạn, đã nộp, nộp muộn, chưa nộp và điểm đã biết tại checkpoint. |
| FR-04 | Sinh các cờ rủi ro và mức ưu tiên kèm lý do cụ thể. |
| FR-05 | Cho phép lọc theo module, presentation, checkpoint, mức ưu tiên và loại kết quả lịch sử. |
| FR-06 | Hiển thị một sinh viên duy nhất một lần tại mỗi module-presentation-checkpoint. |
| FR-07 | Hiển thị xu hướng VLE và tiến độ đánh giá của sinh viên đến checkpoint. |
| FR-08 | Báo cáo tỷ lệ cảnh báo, `Fail`, `Withdrawn`, `Pass` và `Distinction` theo cohort. |
| FR-09 | Đánh giá cảnh báo trên dữ liệu lịch sử theo từng checkpoint và module-presentation. |
| FR-10 | Cho phép truy vết mỗi chỉ số tổng hợp về bảng nguồn và quy tắc tính. |

## 13. Chỉ số báo cáo

### 13.1. Chỉ số vận hành

- Số sinh viên đang hoạt động tại checkpoint.
- Số và tỷ lệ sinh viên theo mức ưu tiên.
- Số sinh viên có từng loại cờ rủi ro.
- Tỷ lệ nộp bài đến hạn và tỷ lệ nộp muộn.
- Tỷ lệ sinh viên không hoạt động VLE trong 7 hoặc 14 ngày.

### 13.2. Chỉ số kết quả

- `fail_rate = Fail / tổng cohort hợp lệ`.
- `withdrawal_rate = Withdrawn / tổng cohort hợp lệ`.
- `adverse_outcome_rate = (Fail + Withdrawn) / tổng cohort hợp lệ`.
- Tỷ lệ `Pass` và `Distinction` được báo cáo riêng.

### 13.3. Chỉ số chất lượng cảnh báo

- `precision`: trong số sinh viên được cảnh báo, tỷ lệ có kết quả bất lợi.
- `recall`: trong số sinh viên có kết quả bất lợi, tỷ lệ đã được cảnh báo tại checkpoint.
- `recall_at_capacity`: recall khi chỉ có thể xem xét một tỷ lệ cố định, ví dụ 20% sinh viên đang hoạt động.
- `lift_at_capacity`: mức tập trung trường hợp bất lợi trong danh sách ưu tiên so với chọn ngẫu nhiên.
- Tỷ lệ cảnh báo sai theo module-presentation và các nhóm dùng để kiểm tra công bằng.

Mục tiêu thử nghiệm của MVP là `lift_at_20_percent >= 1.5` trên tập kiểm tra theo presentation. Đây là mục tiêu đánh giá, không phải cam kết triển khai thực tế; nếu không đạt, nhóm phải báo cáo trung thực và hiệu chỉnh quy tắc.

## 14. Ánh xạ bảy bảng dữ liệu vào bài toán

| Bảng | Vai trò trong yêu cầu |
|---|---|
| `courses` | Xác định module-presentation, độ dài khóa học và phạm vi checkpoint hợp lệ. |
| `assessments` | Cung cấp lịch, loại và trọng số bài đánh giá. |
| `vle` | Diễn giải tài nguyên VLE theo `activity_type` và khoảng tuần dự kiến sử dụng. |
| `studentInfo` | Xác định cohort, bối cảnh sinh viên và kết quả cuối cùng để đánh giá lịch sử. |
| `studentRegistration` | Xác định sinh viên đã đăng ký, đang hoạt động hoặc đã hủy đăng ký tại checkpoint. |
| `studentAssessment` | Cung cấp ngày nộp, điểm và trạng thái điểm chuyển cho các bài đã quan sát được. |
| `studentVle` | Cung cấp chuỗi hành vi tương tác hằng ngày để đo mức tham gia và sự suy giảm hoạt động. |

Tất cả tám file `studentVle_0.csv` đến `studentVle_7.csv` phải được coi là các mảnh của cùng một bảng logic. Cột index không tên không phải dữ liệu nghiệp vụ và phải bị loại khỏi phép tính.

## 15. Quy tắc chất lượng dữ liệu

- Mỗi khóa `(code_module, code_presentation, id_student)` trong `studentInfo` phải là duy nhất.
- Mỗi sinh viên trong snapshot phải nối được với đúng một module-presentation và bản ghi đăng ký tương ứng.
- `studentAssessment` phải nối qua `assessments` để lấy đúng module-presentation trước khi nối với sinh viên.
- `studentVle.id_site` phải nối được với `vle.id_site`; đồng thời module-presentation phải nhất quán ở hai bảng.
- Các cột ngày phải được xử lý như số ngày tương đối, không chuyển thành ngày lịch giả định.
- Giá trị thiếu ở `imd_band`, `week_from`, `week_to` và `date_unregistration` phải được giữ và gắn trạng thái rõ ràng, không tự động thay bằng 0.
- Không có bản ghi trong `studentAssessment` sau khi bài đã đến hạn được hiểu là chưa thấy bản nộp trong dữ liệu; không được tự động gán điểm 0 nếu yêu cầu phân tích không quy định như vậy.
- Các phép tổng hợp `studentVle` phải tránh nhân bản dòng khi join với bảng khác.

## 16. Quy tắc chống rò rỉ dữ liệu

Tại checkpoint `t`, hệ thống không được sử dụng:

- `final_result` làm tín hiệu cảnh báo.
- `date_unregistration` trong tương lai làm đặc trưng dự báo.
- Tương tác VLE có `date > t`.
- Bài nộp có `date_submitted > t`.
- Trạng thái chưa nộp của bài có hạn sau `t`.
- Chỉ số được tổng hợp từ toàn bộ presentation rồi gắn ngược vào snapshot quá khứ.

Khi chia tập đánh giá, ưu tiên giữ nguyên cả presentation trong cùng một tập và kiểm tra trên presentation chưa dùng để hiệu chỉnh. Không chia ngẫu nhiên các snapshot của cùng một sinh viên hoặc cùng một lần học vào cả tập huấn luyện và tập kiểm tra.

## 17. Yêu cầu đạo đức và công bằng

- Cảnh báo là công cụ hỗ trợ quyết định, không phải bằng chứng về năng lực hay động cơ của sinh viên.
- Mọi cảnh báo cá nhân phải có ít nhất một lý do dựa trên hành vi hoặc tiến độ có thể kiểm tra.
- Các thuộc tính nhạy cảm hoặc gần nhạy cảm chỉ dùng để kiểm tra chênh lệch chất lượng cảnh báo trong MVP.
- Không đưa ra kết luận nhân quả từ mối tương quan giữa nhân khẩu học, tương tác VLE và kết quả.
- Báo cáo theo nhóm phải tránh hiển thị nhóm quá nhỏ có nguy cơ tái nhận diện.
- Kết quả phải được diễn giải trong bối cảnh dữ liệu đã ẩn danh và giới hạn ở OULAD.

## 18. Tiêu chí nghiệm thu MVP

MVP được xem là đạt yêu cầu khi:

1. Tạo được snapshot cho các ngày 14, 28, 42 và 56 mà không dùng dữ liệu tương lai.
2. Mỗi sinh viên đang hoạt động chỉ có một dòng tại mỗi module-presentation-checkpoint.
3. Tất cả bảy bảng logic được sử dụng đúng vai trò và truy vết được về nguồn.
4. Mỗi cảnh báo hiển thị mức ưu tiên và ít nhất một lý do cụ thể.
5. Sinh viên đã hủy đăng ký vào hoặc trước checkpoint không còn trong danh sách can thiệp.
6. Các chỉ số VLE và đánh giá được kiểm tra bằng mẫu đối chiếu trực tiếp với CSV nguồn.
7. Báo cáo chất lượng cảnh báo có precision, recall, recall@20% và lift@20% theo từng checkpoint.
8. Kết quả được tách ít nhất theo module-presentation; không chỉ báo cáo một con số gộp toàn bộ OULAD.
9. Có kiểm tra chênh lệch cảnh báo giữa các nhóm nhân khẩu học nhưng không dùng các nhóm đó để tự động đưa ra hành động bất lợi.
10. Tài liệu nêu rõ giới hạn, trường dữ liệu thiếu và các ngưỡng đã sử dụng.

## 19. Giả định và giới hạn

- OULAD là dữ liệu lịch sử năm 2013-2014 và chỉ gồm các module đã qua tiêu chí chọn mẫu của tác giả.
- `sum_click` không phản ánh đầy đủ thời gian học, mức độ tập trung hoặc chất lượng tiếp thu.
- Không có dữ liệu nội dung trao đổi, chất lượng bài làm, hoàn cảnh cá nhân hoặc can thiệp của tutor.
- Kết quả bài thi cuối kỳ có thể không xuất hiện trong `studentAssessment`.
- Các module đã được ẩn danh nên không thể diễn giải theo tên môn học thật.
- Cấu trúc đánh giá và cách dùng VLE khác nhau giữa module-presentation; mọi ngưỡng chung đều cần được kiểm tra lại theo cohort.
- Mối liên hệ quan sát được không chứng minh quan hệ nhân quả.

## 20. Sản phẩm bàn giao dự kiến

- Bộ dữ liệu snapshot hằng tuần ở grain sinh viên - module - presentation - checkpoint.
- Bộ chỉ số tương tác VLE, tiến độ đánh giá và cờ rủi ro có định nghĩa thống nhất.
- Dashboard hoặc báo cáo danh sách ưu tiên và xu hướng theo cohort.
- Báo cáo đánh giá lịch sử, bao gồm chất lượng cảnh báo, độ ổn định giữa các presentation và giới hạn sử dụng.
- Data dictionary cho các trường dẫn xuất và tài liệu quy tắc chống rò rỉ dữ liệu.

## 21. Tài liệu liên quan

- `docs/oulad_raw_data.md`: tổng quan bộ dữ liệu và các file nguồn.
- `docs/oulad_schema_relationships.md`: ý nghĩa cột và quan hệ khóa của bảy bảng.
- `docs/paper/sdata2017171_mo_ta_vi.md`: diễn giải tiếng Việt của bài báo OULAD.
- `docs/paper/sdata2017171.pdf`: bài báo gốc.
