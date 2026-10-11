# Bản cũ

Vui lòng dùng bản đã gom theo chương tại `docs/muc_luc_luong_cong_viec_oulab_theo_chuong.md`.

---

# Mục Lục Và Luồng Thực Hiện Báo Cáo Data Warehouse Với Dữ Liệu OULAB

## Phần 1. Mục Lục / Luồng Công Việc

### 1. Bối cảnh và động cơ thực hiện đề tài

1.1. Bối cảnh đào tạo từ xa và nhu cầu quản trị chất lượng đào tạo  
1.2. Các vấn đề tổng quan trong đào tạo từ xa  
1.3. Vai trò của dữ liệu trong việc theo dõi và cải thiện quá trình học tập  
1.4. Nhu cầu về một bộ dữ liệu phục vụ phân tích đào tạo  
1.5. Giới thiệu tổng quan về nguồn dữ liệu OULAB  
1.6. Định hướng tiếp cận: từ dữ liệu đào tạo đến hệ thống hỗ trợ ra quyết định

### 2. Cơ sở về BI và Data Warehouse trong bài toán đào tạo

2.1. Khái niệm Business Intelligence  
2.2. BI hỗ trợ cải thiện chất lượng đào tạo như thế nào  
2.3. Khái niệm Data Warehouse và sự khác biệt với cơ sở dữ liệu tác nghiệp  
2.4. Mô hình dữ liệu đa chiều, OLAP và các chỉ số phân tích  
2.5. Kiến trúc tổng thể đề xuất cho bài toán OULAB  
2.6. Quy trình phân tích dữ liệu áp dụng trong đề tài

### 3. Xác định yêu cầu nghiệp vụ

3.1. Xác định các đối tượng sử dụng kết quả phân tích  
3.2. Xác định vấn đề nghiệp vụ cần giải quyết  
3.3. Xác định mục tiêu phân tích của hệ thống BI  
3.4. Xác định câu hỏi nghiệp vụ chính  
3.5. Xác định chỉ số đánh giá chất lượng đào tạo  
3.6. Xác định phạm vi, giả định và giới hạn của bài toán

### 4. Xác định yêu cầu phân tích

4.1. Chuyển hóa câu hỏi nghiệp vụ thành câu hỏi phân tích dữ liệu  
4.2. Xác định mức hạt phân tích  
4.3. Xác định các chiều phân tích  
4.4. Xác định các bảng sự kiện và nhóm chỉ số cần tính  
4.5. Xác định yêu cầu báo cáo, dashboard và truy vấn OLAP  
4.6. Xác định tiêu chí chấp nhận kết quả phân tích

### 5. Thu thập và hiểu nguồn dữ liệu

5.1. Liệt kê các bảng dữ liệu trong OULAB  
5.2. Mô tả ý nghĩa các bảng, cột và khóa liên kết  
5.3. Lập từ điển dữ liệu ban đầu  
5.4. Xác định cách nạp và lưu trữ dữ liệu gốc  
5.5. Đánh giá mức độ phù hợp của dữ liệu với mục tiêu phân tích  
5.6. Ghi nhận các vấn đề về quyền riêng tư, đạo đức và an toàn dữ liệu

### 6. Khám phá dữ liệu

6.1. Thống kê tổng quan về kích thước và cấu trúc dữ liệu  
6.2. Phân tích chất lượng dữ liệu: thiếu, trùng lặp, sai kiểu, bất thường  
6.3. Khám phá phân bố của người học, môn học, bài đánh giá và hoạt động học tập  
6.4. Khám phá sự thay đổi theo thời gian của hành vi học tập  
6.5. Khám phá mối quan hệ giữa tương tác, điểm số, đăng ký và kết quả học tập  
6.6. Tổng hợp nhận xét EDA và các giả thuyết phân tích

### 7. Tiền xử lý dữ liệu

7.1. Làm sạch dữ liệu thiếu, trùng lặp và không nhất quán  
7.2. Chuẩn hóa kiểu dữ liệu, định dạng thời gian và khóa liên kết  
7.3. Xử lý các giá trị bất thường theo quy tắc đã thống nhất  
7.4. Tổng hợp và biến đổi dữ liệu phục vụ phân tích  
7.5. Tạo biến dẫn xuất và nhãn phân tích nếu cần  
7.6. Lập tài liệu quy tắc tiền xử lý để đảm bảo khả năng lặp lại

### 8. Thiết kế kho dữ liệu

8.1. Xác định kiến trúc kho dữ liệu và vùng dữ liệu  
8.2. Xác định mức hạt cho từng bảng sự kiện  
8.3. Thiết kế các bảng dimension  
8.4. Thiết kế các bảng fact  
8.5. Thiết kế mô hình sao hoặc mô hình bông tuyết  
8.6. Thiết kế luồng ETL/ELT từ dữ liệu gốc vào kho dữ liệu  
8.7. Xác định data mart phục vụ từng nhóm báo cáo

### 9. Xử lý dữ liệu và xây dựng lớp phân tích

9.1. Nạp dữ liệu vào các vùng staging, warehouse và data mart  
9.2. Tính toán các chỉ số đào tạo và chỉ số hành vi học tập  
9.3. Xây dựng các truy vấn tổng hợp và cube phân tích  
9.4. Phân tích mô tả kết quả học tập và mức độ tương tác  
9.5. Phân tích chẩn đoán các yếu tố liên quan đến kết quả học tập  
9.6. Xây dựng mô hình dự báo hoặc cảnh báo sớm nếu phạm vi đề tài yêu cầu

### 10. Kiểm tra hợp lệ và tinh chỉnh

10.1. Kiểm tra tính đúng đắn của dữ liệu sau ETL/ELT  
10.2. Kiểm tra toàn vẹn khóa và quan hệ giữa các bảng  
10.3. Đối chiếu chỉ số với định nghĩa nghiệp vụ  
10.4. Đánh giá kết quả phân tích hoặc mô hình dự báo  
10.5. Tinh chỉnh tham số, quy tắc tiền xử lý và mô hình nếu chưa đạt yêu cầu  
10.6. Chốt bộ dữ liệu, mô hình và chỉ số dùng cho báo cáo

### 11. Trực quan hóa và báo cáo BI

11.1. Xác định cấu trúc dashboard và đối tượng người xem  
11.2. Thiết kế dashboard tổng quan chất lượng đào tạo  
11.3. Thiết kế dashboard về hành vi học tập và tương tác trên hệ thống  
11.4. Thiết kế dashboard về điểm số, bài đánh giá và kết quả học tập  
11.5. Trình bày insight chính và khuyến nghị hành động  
11.6. Đánh giá mức độ đáp ứng của dashboard với câu hỏi nghiệp vụ

### 12. Triển khai, giám sát và kết luận

12.1. Đề xuất cách triển khai hệ thống BI trong bối cảnh thực tế  
12.2. Đề xuất lịch cập nhật dữ liệu và cơ chế giám sát chất lượng dữ liệu  
12.3. Nêu các rủi ro, hạn chế và điều kiện áp dụng kết quả  
12.4. Tổng kết kết quả đạt được so với mục tiêu ban đầu  
12.5. Đề xuất hướng phát triển tiếp theo  
12.6. Phân công công việc và kế hoạch thực hiện nhóm

## Phần 2. Bảng Thống Kê Mục Đích, Input Và Output

| Mục | Bước trong quy trình phân tích dữ liệu | Mục đích trình bày | Việc cần làm | Input | Output |
|---|---|---|---|---|---|
| 1. Bối cảnh và động cơ | Tiền đề trước Goal Definition | Giải thích vì sao bài toán đào tạo từ xa cần được phân tích bằng dữ liệu. | Mô tả bối cảnh, nêu vấn đề tổng quan, dẫn đến nhu cầu cần dữ liệu và hệ thống BI. | Kiến thức về đào tạo từ xa, yêu cầu đề tài, nguồn OULAB. | Bối cảnh rõ ràng, vấn đề được đặt ra nhưng chưa đi vào yêu cầu nghiệp vụ chi tiết. |
| 2. Cơ sở BI và Data Warehouse | Tiền đề phương pháp | Đặt nền tảng lý thuyết để người đọc hiểu vì sao dùng BI và kho dữ liệu. | Trình bày BI, Data Warehouse, OLAP, mô hình đa chiều và kiến trúc tổng thể. | Tài liệu lý thuyết, cấu trúc tham khảo từ báo cáo cũ, định hướng đề tài. | Cơ sở lý thuyết và kiến trúc định hướng cho các phần sau. |
| 3. Xác định yêu cầu nghiệp vụ | Goal Definition | Xác định bài toán cần giải quyết theo góc nhìn nghiệp vụ. | Xác định đối tượng sử dụng, vấn đề nghiệp vụ, mục tiêu, KPI, phạm vi và giới hạn. | Bối cảnh mục 1, khả năng của BI mục 2. | Danh sách mục tiêu nghiệp vụ, câu hỏi nghiệp vụ và KPI cần theo dõi. |
| 4. Xác định yêu cầu phân tích | Goal Definition chi tiết | Chuyển mục tiêu nghiệp vụ thành yêu cầu có thể xử lý bằng dữ liệu. | Xác định mức hạt, chiều phân tích, fact, metric, dashboard và tiêu chí chấp nhận. | Output mục 3, hiểu biết ban đầu về OULAB. | Bản đặc tả yêu cầu phân tích và tiêu chí đánh giá kết quả. |
| 5. Thu thập và hiểu nguồn dữ liệu | DAQ | Xác định dữ liệu nào được sử dụng và dữ liệu có đáp ứng bài toán không. | Liệt kê bảng, cột, khóa, quan hệ; lập từ điển dữ liệu; lưu trữ bản raw. | Bộ dữ liệu OULAB, đặc tả dữ liệu nếu có. | Data inventory, data dictionary, bản raw data và nhận xét về mức độ phù hợp. |
| 6. Khám phá dữ liệu | Data Exploration | Hiểu đặc điểm, chất lượng và các mẫu hình ban đầu trong dữ liệu. | Thống kê, vẽ biểu đồ EDA, kiểm tra missing, duplicate, outlier, phân bố và tương quan. | Raw data, data dictionary, yêu cầu phân tích mục 4. | Báo cáo EDA, danh sách vấn đề dữ liệu, insight ban đầu và giả thuyết phân tích. |
| 7. Tiền xử lý dữ liệu | Data Preprocessing | Biến dữ liệu thô thành dữ liệu sạch và sẵn sàng cho warehouse/phân tích. | Làm sạch, chuẩn hóa, biến đổi, tổng hợp, tạo biến dẫn xuất và ghi nhận quy tắc xử lý. | Raw data, kết quả EDA, quy tắc nghiệp vụ. | Dataset sạch, quy tắc tiền xử lý, mapping giữa dữ liệu gốc và dữ liệu sau xử lý. |
| 8. Thiết kế kho dữ liệu | Data Preprocessing và Data Processing | Tạo cấu trúc kho dữ liệu phù hợp với câu hỏi phân tích. | Chọn grain, thiết kế fact/dimension, mô hình sao/bông tuyết, staging, warehouse, data mart. | Dataset sạch, yêu cầu phân tích, KPI và chiều phân tích. | Lược đồ kho dữ liệu, mô hình logic/vật lý và thiết kế ETL/ELT. |
| 9. Xử lý dữ liệu và lớp phân tích | Data Processing / Modelling | Tạo các bảng, chỉ số, truy vấn và mô hình phân tích để trả lời câu hỏi nghiệp vụ. | Nạp dữ liệu, tính metric, viết query, xây cube, phân tích mô tả/chẩn đoán, dự báo nếu có. | Kho dữ liệu đã thiết kế, data mart, KPI. | Bảng tổng hợp, metric, truy vấn phân tích, kết quả phân tích và/hoặc mô hình dự báo. |
| 10. Kiểm tra hợp lệ và tinh chỉnh | Validation và vòng lặp tinh chỉnh | Đảm bảo dữ liệu, metric, dashboard và mô hình đúng với yêu cầu. | Kiểm tra row count, khóa, quan hệ, công thức KPI; đánh giá mô hình; lặp lại tiền xử lý/xử lý khi cần. | Kết quả ETL/ELT, metric, dashboard bản nháp, tiêu chí chấp nhận. | Kết quả validation, danh sách lỗi đã sửa, phiên bản dữ liệu và metric được chốt. |
| 11. Trực quan hóa và báo cáo BI | Reporting / Business Data Visualization | Truyền đạt kết quả phân tích thành dashboard, insight và khuyến nghị. | Thiết kế dashboard, chọn biểu đồ, viết insight, gắn insight với câu hỏi nghiệp vụ và KPI. | Metric đã validation, kết quả phân tích, mục tiêu nghiệp vụ. | Dashboard BI, báo cáo insight, khuyến nghị hành động. |
| 12. Triển khai, giám sát và kết luận | Deployment / Monitoring / Reporting | Đóng gói kết quả để có thể sử dụng, đánh giá và phát triển tiếp. | Đề xuất triển khai, cập nhật dữ liệu, giám sát chất lượng, nêu hạn chế và tổng kết. | Dashboard, warehouse, kết quả validation, phạm vi đề tài. | Kế hoạch triển khai/giám sát, kết luận báo cáo, hướng phát triển và phân công nhóm. |

## Ghi Chú Sử Dụng

- Nhóm nên thực hiện từ mục 3 đến mục 11 theo đúng thứ tự; nếu mục 10 phát hiện lỗi thì quay lại mục 7, 8 hoặc 9 để tinh chỉnh.
- Mục 1 và 2 nên viết sau khi đã hiểu rõ hướng tiếp cận, nhưng trong báo cáo vẫn đặt ở đầu để dẫn dắt người đọc.
- Mỗi dashboard, truy vấn hoặc bảng tổng hợp ở mục 11 phải truy ngược được về câu hỏi nghiệp vụ ở mục 3 và metric ở mục 4.
- Nếu một nội dung không tạo ra input cho bước sau hoặc không trả lời câu hỏi nghiệp vụ, nên đưa vào phụ lục hoặc loại bỏ để tránh báo cáo bị tràn lan.
