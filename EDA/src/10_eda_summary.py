import shutil
from pathlib import Path
import os

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
EDA_OUTPUTS = PROJECT_ROOT / 'EDA' / 'outputs'
SUMMARY_FIGURES = EDA_OUTPUTS / 'figures' / '10_eda_summary'
SUMMARY_TABLES = EDA_OUTPUTS / 'tables' / '10_eda_summary'

SUMMARY_FIGURES.mkdir(parents=True, exist_ok=True)
SUMMARY_TABLES.mkdir(parents=True, exist_ok=True)

print("Gathering Executive Summary artifacts...")

# Key figures to copy
key_figures = [
    EDA_OUTPUTS / 'figures' / '08_visualization' / '8_dashboard_module_presentation.png',
    EDA_OUTPUTS / 'figures' / '08_visualization' / '7_correlation_heatmap.png',
    EDA_OUTPUTS / 'figures' / '08_visualization' / '4_weekly_interaction_by_result.png'
]

for fig in key_figures:
    if fig.exists():
        shutil.copy(fig, SUMMARY_FIGURES / fig.name)
        print(f"Copied figure: {fig.name}")
    else:
        print(f"Warning: Missing figure {fig.name}")

# Key tables to copy
key_tables = [
    EDA_OUTPUTS / 'tables' / '07_standardize_dtypes' / 'dtype_mapping_raw_etl_eda.csv',
    EDA_OUTPUTS / 'tables' / '09_data_quality' / 'data_quality_issues.csv'
]

for tbl in key_tables:
    if tbl.exists():
        shutil.copy(tbl, SUMMARY_TABLES / tbl.name)
        print(f"Copied table: {tbl.name}")
    else:
        print(f"Warning: Missing table {tbl.name}")

print("Executive Summary artifacts successfully consolidated in outputs/10_eda_summary!")
