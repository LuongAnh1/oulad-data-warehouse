import pandas as pd
import numpy as np
import os
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / 'raw_data'
STAGING_DIR = PROJECT_ROOT / 'ETL' / 'staging_data'
EDA_DATA_DIR = PROJECT_ROOT / 'ETL' / 'eda_data'
OUTPUT_TABLES = PROJECT_ROOT / 'EDA' / 'outputs' / 'tables' / '07_standardize_dtypes'
OUTPUT_FIGURES = PROJECT_ROOT / 'EDA' / 'outputs' / 'figures' / '07_standardize_dtypes'

OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
OUTPUT_FIGURES.mkdir(parents=True, exist_ok=True)

# Tables to process
tables = ['courses', 'assessments', 'vle', 'studentInfo', 'studentRegistration', 'studentAssessment', 'studentVle']
eda_tables = ['eda_student_summary', 'eda_weekly_activity', 'eda_assessment_progress']

# Define target dtypes based on ETL report and EDA requirements
categorical_cols = ['code_module', 'code_presentation', 'assessment_type', 'final_result', 'activity_type', 
                   'gender', 'region', 'highest_education', 'imd_band', 'age_band', 'disability']
id_cols = ['id_student', 'id_site', 'id_assessment']

def get_target_dtype(col, current_type):
    if col in categorical_cols: return 'category'
    if col in id_cols: return 'string'
    # Default to current type (int64/float64/object) if not specifically cast
    return current_type

results = []

# Process core OULAD tables
for tbl in tables:
    raw_path = RAW_DIR / f"{tbl}.csv"
    staging_path = STAGING_DIR / f"{tbl}.csv"
    
    if raw_path.exists() and staging_path.exists():
        raw_df = pd.read_csv(raw_path, nrows=100) # Only need dtypes
        staging_df = pd.read_csv(staging_path, nrows=100)
        
        for col in raw_df.columns:
            raw_type = str(raw_df[col].dtype)
            staging_type = str(staging_df[col].dtype)
            
            # The ETL intended type as per 01_etl_report.md
            etl_intended = get_target_dtype(col, staging_type)
            
            # EDA will strictly enforce this 
            eda_enforced = etl_intended
            
            results.append({
                'Table': tbl,
                'Column': col,
                'Raw_CSV_Dtype': raw_type,
                'ETL_Staging_CSV_Dtype': staging_type,
                'ETL_Intended_Dtype': etl_intended,
                'EDA_Enforced_Dtype': eda_enforced
            })

# Process EDA-generated tables
for tbl in eda_tables:
    eda_path = EDA_DATA_DIR / f"{tbl}.csv"
    if eda_path.exists():
        df = pd.read_csv(eda_path, nrows=100)
        for col in df.columns:
            current_type = str(df[col].dtype)
            raw_type = "N/A (Generated in EDA)"
            staging_type = "N/A"
            etl_intended = "N/A"
            eda_enforced = get_target_dtype(col, current_type)
            
            results.append({
                'Table': tbl,
                'Column': col,
                'Raw_CSV_Dtype': raw_type,
                'ETL_Staging_CSV_Dtype': staging_type,
                'ETL_Intended_Dtype': etl_intended,
                'EDA_Enforced_Dtype': eda_enforced
            })

report_df = pd.DataFrame(results)
report_path = OUTPUT_TABLES / 'dtype_mapping_raw_etl_eda.csv'
report_df.to_csv(report_path, index=False)
print(f"✅ Data type mapping generated successfully at: {report_path}")

# Function to actually load data with correct types for EDA tasks
def load_eda_data_with_types(filepath):
    # This utility function will be used by subsequent EDA scripts
    df = pd.read_csv(filepath)
    for col in df.columns:
        if col in categorical_cols:
            df[col] = df[col].astype('category')
        elif col in id_cols:
            df[col] = df[col].astype('string')
    return df

print("✅ Standardize dtypes script completed.")
