# Git & Git LFS Guide

Hướng dẫn quản lý source code và dữ liệu lớn trong project **OULAD Data Warehouse / ETL**.

---

## 1. Tại sao cần Git LFS?

GitHub giới hạn kích thước file thông thường ở mức **100 MB/file**.

Trong project OULAD có file:

```text
ETL/staging_data/studentVle.csv
```

kích thước khoảng **278 MB**, nên không thể push trực tiếp bằng Git thông thường.

Git LFS (Large File Storage) cho phép:

```text
Git
├── Source code
├── SQL
├── Documentation
└── Metadata / pointer của file lớn

Git LFS
└── File dữ liệu lớn
    └── studentVle.csv
```

Nhờ đó vẫn có thể sử dụng GitHub để quản lý project mà không đưa trực tiếp file 278 MB vào Git repository.

---

# 2. Cài đặt Git LFS

Kiểm tra Git LFS:

```powershell
git lfs --version
```

Nếu đã cài, kết quả sẽ tương tự:

```text
git-lfs/3.7.1
```

Nếu chưa cài, tải Git LFS từ:

[Git LFS](https://git-lfs.com/?utm_source=chatgpt.com)

---

# 3. Khởi tạo Git LFS

Trong thư mục project:

```powershell
git lfs install
```

Lệnh này kích hoạt Git LFS cho môi trường Git hiện tại.

Kiểm tra thành công:

```text
Git LFS initialized.
```

---

# 4. Cấu hình file nào sử dụng Git LFS

Ví dụ project có cấu trúc:

```text
ETL/
├── src/
├── docs/
└── staging_data/
    ├── studentVle.csv
    ├── studentInfo.csv
    └── studentAssessment.csv
```

Muốn tất cả CSV trong `staging_data` sử dụng Git LFS:

```powershell
git lfs track "ETL/staging_data/*.csv"
```

Kết quả:

```text
Tracking "ETL/staging_data/*.csv"
```

Git sẽ tạo hoặc cập nhật:

```text
.gitattributes
```

Nội dung có dạng:

```text
ETL/staging_data/*.csv filter=lfs diff=lfs merge=lfs -text
```

`.gitattributes` là file chứa **quy tắc để Git biết những file nào phải được quản lý bằng LFS**.

---

# 5. Add `.gitattributes`

Đưa file cấu hình vào staging:

```powershell
git add .gitattributes
```

Sau đó add toàn bộ project:

```powershell
git add .
```

---

# 6. Kiểm tra file đã được Git LFS nhận chưa

Chạy:

```powershell
git lfs ls-files
```

Nếu thấy:

```text
xxxxxxxx ETL/staging_data/studentVle.csv
```

thì `studentVle.csv` đã được Git LFS quản lý.

Nếu có nhiều CSV được track:

```text
xxxxxxxx ETL/staging_data/studentInfo.csv
xxxxxxxx ETL/staging_data/studentVle.csv
xxxxxxxx ETL/staging_data/studentAssessment.csv
```

---

# 7. Kiểm tra Git Status

Trước khi commit:

```powershell
git status
```

Kiểm tra các file đang được chuẩn bị commit.

Đảm bảo:

* Code cần thiết đã được add.
* `.gitattributes` đã được add.
* Dataset lớn nằm trong danh sách Git LFS.
* Không add nhầm file không cần thiết.

---

# 8. Tạo commit

Sau khi kiểm tra:

```powershell
git commit -m "Add ETL project with Git LFS"
```

Commit này lưu:

```text
Source code
Documentation
SQL
.gitattributes
Git LFS pointer
```

File lớn thực tế sẽ được Git LFS quản lý.

---

# 9. Push lên GitHub

Sau khi commit thành công:

```powershell
git push -u origin main
```

Git sẽ:

```text
GitHub
  │
  ├── Git repository
  │     ├── Source code
  │     ├── SQL
  │     ├── Documentation
  │     └── LFS pointer
  │
  └── Git LFS
        └── studentVle.csv
```

Nếu push thành công, project trên GitHub sẽ có cả source code và khả năng tải dataset thông qua Git LFS.

---

# 10. Người khác clone project

Người khác cần cài Git LFS trước.

Kiểm tra:

```powershell
git lfs --version
```

Sau đó clone:

```powershell
git clone https://github.com/LuongAnh1/oulad-data-warehouse.git
```

Di chuyển vào project:

```powershell
cd oulad-data-warehouse
```

Sau đó tải các file LFS:

```powershell
git lfs pull
```

Kết quả mong muốn:

```text
ETL/
├── src/
├── docs/
└── staging_data/
    ├── studentVle.csv
    ├── studentInfo.csv
    └── studentAssessment.csv
```

---

# 11. Quy trình làm việc hằng ngày

Sau khi project đã được thiết lập Git LFS, quy trình thông thường là:

### Lấy code mới nhất

```powershell
git pull
```

Nếu cần đảm bảo các file LFS được tải:

```powershell
git lfs pull
```

### Sau khi sửa code

```powershell
git status
```

Sau đó:

```powershell
git add .
```

Commit:

```powershell
git commit -m "Update ETL pipeline"
```

Push:

```powershell
git push
```

---

# 12. Thêm dataset mới

Nếu thêm một file:

```text
ETL/staging_data/new_data.csv
```

và file nằm trong pattern:

```text
ETL/staging_data/*.csv
```

thì Git LFS sẽ tự động quản lý file đó.

Kiểm tra:

```powershell
git lfs ls-files
```

---

# 13. Không nên làm gì?

### Không push file lớn trực tiếp bằng Git

Không nên:

```powershell
git add studentVle.csv
```

trước khi cấu hình LFS.

Phải cấu hình:

```powershell
git lfs track "ETL/staging_data/*.csv"
```

trước.

---

### Không commit dataset lớn nếu không cần thiết

Nếu dataset chỉ dùng để chạy ETL và có thể tải lại từ nguồn công khai, có thể cân nhắc:

```text
GitHub
└── Code + documentation

Dataset
└── Download riêng
```

Git LFS phù hợp khi muốn người khác có thể clone project và lấy luôn dataset.

---

# 14. `.gitignore` và `.gitattributes` khác nhau thế nào?

Hai file này có mục đích khác nhau.

### `.gitignore`

Nói với Git:

> "Đừng theo dõi file này."

Ví dụ:

```gitignore
__pycache__/
.env
*.log
```

### `.gitattributes`

Nói với Git:

> "File này được xử lý như thế nào?"

Ví dụ:

```text
ETL/staging_data/*.csv filter=lfs diff=lfs merge=lfs -text
```

Nói cách khác:

```text
.gitignore
    ↓
Không đưa file vào Git

.gitattributes
    ↓
File vẫn thuộc Git
nhưng được quản lý bằng Git LFS
```

---

# 15. `.gitkeep` là gì?

Git không theo dõi thư mục rỗng.

Nếu muốn giữ:

```text
ETL/staging_data/
```

trên GitHub khi thư mục chưa có dataset, có thể tạo:

```text
ETL/staging_data/.gitkeep
```

`.gitkeep` chỉ là một file giữ chỗ.

Nó không chứa dữ liệu và không thực hiện chương trình nào.

---

# 16. Cấu trúc project đề xuất

Project cuối cùng có thể tổ chức:

```text
oulad-data-warehouse/
│
├── ETL/
│   ├── src/
│   │   └── 01_run_etl.py
│   │
│   ├── docs/
│   │   └── 01-report/
│   │
│   └── staging_data/
│       ├── .gitkeep
│       ├── studentInfo.csv
│       ├── studentVle.csv
│       └── ...
│
├── .gitignore
├── .gitattributes
├── README.md
└── ...
```

Trong đó:

```text
Source code       → Git
Documentation     → Git
SQL               → Git
Configuration     → Git
Large CSV         → Git LFS
Temporary files   → .gitignore
```

---

# 17. Cheat Sheet

## Người tạo project

```powershell
git lfs install

git lfs track "ETL/staging_data/*.csv"

git add .gitattributes

git add .

git lfs ls-files

git status

git commit -m "Add ETL project with Git LFS"

git push -u origin main
```

## Người clone project

```powershell
git lfs install

git clone <repository-url>

cd <repository-folder>

git lfs pull
```

## Làm việc hằng ngày

```powershell
git pull

git lfs pull

git add .

git commit -m "Update project"

git push
```

---

# 18. Mô hình tổng quát

```text
                    GitHub
                      │
             ┌────────┴────────┐
             │                 │
          Git Repo           Git LFS
             │                 │
       ┌─────┴─────┐           │
       │            │           │
      Code        Docs      Large Dataset
       │            │           │
       │            │      studentVle.csv
       │            │          278 MB
       └─────┬──────┘           │
             │                  │
             └────────┬─────────┘
                      │
                   Project
                      │
               ETL / Data Warehouse
```

**Nguyên tắc chính:**

> **Git quản lý code và lịch sử project; Git LFS quản lý các file dữ liệu lớn.**
