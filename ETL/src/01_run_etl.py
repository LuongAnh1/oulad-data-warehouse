import os
import pandas as pd
import glob
import time

base_dir = r"d:\Học Tập\2026.1\Kho dữ liệu và kinh doanh thông minh\oulad-data-warehouse"
raw_dir = os.path.join(base_dir, "raw_data")
staging_dir = os.path.join(base_dir, "ETL", "staging_data")
report_path = os.path.join(base_dir, "ETL", "etl_report.md")

os.makedirs(staging_dir, exist_ok=True)

report_lines = []
report_lines.append("# Báo Cáo Kết Quả Xử Lý ETL - Staging")
report_lines.append(f"Thời gian chạy: {time.strftime('%Y-%m-%d %H:%M:%S')}")
report_lines.append("\n## 1. Kiểm kê dữ liệu và Load dữ liệu thô")

# 1. Liệt kê và Kiểm kê
all_files = glob.glob(os.path.join(raw_dir, "*.csv"))
report_lines.append(f"**Tổng số file CSV trong raw_data:** {len(all_files)}")

tables = {
    'courses': None,
    'assessments': None,
    'vle': None,
    'studentInfo': None,
    'studentRegistration': None,
    'studentAssessment': None,
    'studentVle': []
}

# 2. Load data and remove unnamed
dataframes = {}

for f in all_files:
    fname = os.path.basename(f)
    try:
        df = pd.read_csv(f)
        # 4. Loại bỏ cột Unnamed: 0 nếu có
        unnamed_cols = [c for c in df.columns if 'Unnamed' in c]
        if unnamed_cols:
            df = df.drop(columns=unnamed_cols)
        
        if fname.startswith('studentVle_'):
            tables['studentVle'].append(df)
        else:
            tname = fname.replace('.csv', '')
            if tname in tables:
                tables[tname] = df
    except Exception as e:
        report_lines.append(f"- Lỗi khi đọc file {fname}: {e}")

report_lines.append("\n### Tóm tắt các bảng đơn lẻ (Sau khi loại bỏ cột kỹ thuật dư thừa):")
for t, df in tables.items():
    if t != 'studentVle' and df is not None:
        report_lines.append(f"- **{t}**: {df.shape[0]} dòng, {df.shape[1]} cột. Cột: `{', '.join(df.columns)}`")

# 3. Gộp bảng bị chia nhỏ
report_lines.append("\n## 2. Gộp bảng studentVle")
total_rows_before = sum(df.shape[0] for df in tables['studentVle'])
studentVle_df = pd.concat(tables['studentVle'], ignore_index=True)
report_lines.append(f"- Tổng số file `studentVle_*.csv`: {len(tables['studentVle'])}")
report_lines.append(f"- Tổng số dòng trước khi gộp: {total_rows_before}")
report_lines.append(f"- Tổng số dòng sau khi gộp: {studentVle_df.shape[0]}")

dups = studentVle_df.duplicated().sum()
report_lines.append(f"- Số dòng trùng lặp (duplicate) sau khi gộp: {dups}")
if dups > 0:
    studentVle_df = studentVle_df.drop_duplicates()
    report_lines.append(f"- Đã loại bỏ duplicate. Số dòng còn lại: {studentVle_df.shape[0]}")
tables['studentVle'] = studentVle_df

# 5. Chuẩn hóa kiểu dữ liệu
report_lines.append("\n## 3. Chuẩn hóa kiểu dữ liệu")

def normalize_dtypes(name, df):
    # IDs -> string
    for col in ['id_student', 'id_site', 'id_assessment']:
        if col in df.columns:
            df[col] = df[col].astype(str)
            
    # Categorical -> category
    for col in ['code_module', 'code_presentation', 'assessment_type', 'final_result']:
        if col in df.columns:
            df[col] = df[col].astype('category')
            
    # Numeric -> float/int
    for col in ['score', 'weight', 'sum_click']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

for t, df in tables.items():
    if df is not None:
        tables[t] = normalize_dtypes(t, df)
        
report_lines.append("- Đã ép kiểu các cột ID (`id_student`, `id_site`, `id_assessment`) sang `string`.")
report_lines.append("- Đã ép kiểu các cột phân loại (`code_module`, `code_presentation`, `assessment_type`, `final_result`) sang `category`.")
report_lines.append("- Đã đảm bảo các cột định lượng (`score`, `weight`, `sum_click`) là kiểu số.")
report_lines.append("- Các cột ngày (`date`, `date_submitted`...) được giữ nguyên kiểu số do đặc thù ngày tương đối của OULAD.")

# Lưu kết quả
report_lines.append("\n## 4. Xuất dữ liệu ra Staging")
for t, df in tables.items():
    if df is not None:
        out_path = os.path.join(staging_dir, f"{t}.csv")
        df.to_csv(out_path, index=False)
        report_lines.append(f"- Đã lưu bảng **{t}** vào `staging_data/{t}.csv`")

with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print("ETL script completed successfully!")
