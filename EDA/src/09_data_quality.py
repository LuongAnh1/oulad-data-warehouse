import pandas as pd
import numpy as np
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
STAGING_DIR = PROJECT_ROOT / 'ETL' / 'staging_data'
OUTPUT_DIR = PROJECT_ROOT / 'EDA' / 'outputs' / 'tables' / '09_data_quality'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Define tables
table_names = ['courses', 'assessments', 'vle', 'studentInfo', 'studentRegistration', 'studentAssessment', 'studentVle']
data = {}

print("Loading data for quality check...")
for t in table_names:
    filepath = STAGING_DIR / f"{t}.csv"
    if filepath.exists():
        data[t] = pd.read_csv(filepath)
    else:
        print(f"Warning: File not found {filepath}")

issues = []

# 1. Check Duplicates
print("Checking for Duplicates...")
for t, df in data.items():
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        issues.append({
            'Loại kiểm tra': 'Duplicate',
            'Bảng': t,
            'Cột / Khóa liên quan': 'All columns',
            'Số lượng lỗi': dup_count,
            'Mô tả': f"Phát hiện {dup_count} dòng trùng lặp hoàn toàn."
        })
    else:
        issues.append({
            'Loại kiểm tra': 'Duplicate',
            'Bảng': t,
            'Cột / Khóa liên quan': 'All columns',
            'Số lượng lỗi': 0,
            'Mô tả': "Không có dòng trùng lặp."
        })

# 2. Check Foreign Keys mismatches
print("Checking Foreign Keys...")
fk_rules = [
    {'child': 'assessments', 'parent': 'courses', 'keys': ['code_module', 'code_presentation']},
    {'child': 'vle', 'parent': 'courses', 'keys': ['code_module', 'code_presentation']},
    {'child': 'studentInfo', 'parent': 'courses', 'keys': ['code_module', 'code_presentation']},
    {'child': 'studentRegistration', 'parent': 'courses', 'keys': ['code_module', 'code_presentation']},
    {'child': 'studentRegistration', 'parent': 'studentInfo', 'keys': ['id_student']},
    {'child': 'studentAssessment', 'parent': 'assessments', 'keys': ['id_assessment']},
    {'child': 'studentAssessment', 'parent': 'studentInfo', 'keys': ['id_student']},
    {'child': 'studentVle', 'parent': 'vle', 'keys': ['id_site']},
    {'child': 'studentVle', 'parent': 'studentInfo', 'keys': ['id_student']},
    {'child': 'studentVle', 'parent': 'courses', 'keys': ['code_module', 'code_presentation']}
]

for rule in fk_rules:
    child, parent, keys = rule['child'], rule['parent'], rule['keys']
    if child in data and parent in data:
        df_child = data[child][keys].drop_duplicates()
        df_parent = data[parent][keys].drop_duplicates()

        # Merge left to find orphans
        merged = df_child.merge(df_parent, on=keys, how='left', indicator=True)
        orphans = merged[merged['_merge'] == 'left_only']
        orphan_count = len(orphans)

        if orphan_count > 0:
            issues.append({
                'Loại kiểm tra': 'Foreign Key',
                'Bảng': child,
                'Cột / Khóa liên quan': f"-> {parent} via {', '.join(keys)}",
                'Số lượng lỗi': orphan_count,
                'Mô tả': f"Có {orphan_count} bản ghi không khớp khóa với bảng cha."
            })
        else:
            issues.append({
                'Loại kiểm tra': 'Foreign Key',
                'Bảng': child,
                'Cột / Khóa liên quan': f"-> {parent} via {', '.join(keys)}",
                'Số lượng lỗi': 0,
                'Mô tả': "Toàn vẹn khóa dữ liệu được đảm bảo."
            })

# 3. Export results
issues_df = pd.DataFrame(issues)
issues_path = OUTPUT_DIR / 'data_quality_issues.csv'
issues_df.to_csv(issues_path, index=False, encoding='utf-8-sig')
print(f"Data quality check complete. Report saved.")
