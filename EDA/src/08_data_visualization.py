import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os
import io

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
STAGING_DIR = PROJECT_ROOT / 'ETL' / 'staging_data'
EDA_DATA_DIR = PROJECT_ROOT / 'ETL' / 'eda_data'
OUTPUT_FIGURES = PROJECT_ROOT / 'EDA' / 'outputs' / 'figures' / '08_visualization'
OUTPUT_FIGURES.mkdir(parents=True, exist_ok=True)

# Visual settings
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 150

categorical_cols = ['code_module', 'code_presentation', 'assessment_type', 'final_result', 'activity_type',
                   'gender', 'region', 'highest_education', 'imd_band', 'age_band', 'disability']
id_cols = ['id_student', 'id_site', 'id_assessment']

def load_data_with_types(filepath):
    df = pd.read_csv(filepath)
    for col in df.columns:
        if col in categorical_cols:
            df[col] = df[col].astype('category')
        elif col in id_cols:
            df[col] = df[col].astype('string')
    return df

print("Loading data...")
try:
    df_summary = load_data_with_types(EDA_DATA_DIR / 'eda_student_summary.csv')
    df_weekly = load_data_with_types(EDA_DATA_DIR / 'eda_weekly_activity.csv')
    df_assessment = load_data_with_types(EDA_DATA_DIR / 'eda_assessment_progress.csv')
except Exception as e:
    print(f"Error loading data: {e}")
    exit(1)

# 1. Phân bố final_result
plt.figure()
ax = sns.countplot(data=df_summary, x='final_result', order=['Distinction', 'Pass', 'Fail', 'Withdrawn'], palette="Set2")
plt.title("Phân bố kết quả học tập (final_result)", fontsize=14, pad=15)
plt.xlabel("Kết quả cuối")
plt.ylabel("Số lượng sinh viên")
for p in ax.patches:
    ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', xytext=(0, 5), textcoords='offset points')
plt.savefig(OUTPUT_FIGURES / '1_final_result_distribution.png', bbox_inches='tight')
plt.close()

# 2. Phân bố điểm assessment (Trung bình điểm của sinh viên)
plt.figure()
sns.histplot(data=df_summary, x='avg_score', bins=20, kde=True, color='skyblue')
plt.title("Phân bố điểm đánh giá trung bình (avg_score)", fontsize=14, pad=15)
plt.xlabel("Điểm trung bình")
plt.ylabel("Tần suất")
plt.savefig(OUTPUT_FIGURES / '2_avg_score_distribution.png', bbox_inches='tight')
plt.close()

# 3. Tổng click VLE (Sử dụng log1p để giảm lệch phải)
plt.figure()
df_summary['log_total_click'] = np.log1p(df_summary['total_click'])
sns.histplot(data=df_summary, x='log_total_click', bins=30, kde=True, color='coral')
plt.title("Phân bố tổng click VLE (Log1p transformed)", fontsize=14, pad=15)
plt.xlabel("Log1p(Total Click)")
plt.ylabel("Tần suất")
plt.savefig(OUTPUT_FIGURES / '3_total_click_distribution.png', bbox_inches='tight')
plt.close()

# 4. Tương tác theo tuần học và kết quả cuối
# Lấy sample một module_presentation lớn để dễ nhìn (VD: FFF_2014J)
top_mp = df_weekly.groupby(['code_module', 'code_presentation']).size().idxmax()
df_weekly_sample = df_weekly[(df_weekly['code_module'] == top_mp[0]) & (df_weekly['code_presentation'] == top_mp[1])]
df_weekly_sample = df_weekly_sample.merge(df_summary[['id_student', 'final_result']], on='id_student', how='inner')

plt.figure(figsize=(12, 7))
sns.lineplot(data=df_weekly_sample, x='study_week', y='weekly_click', hue='final_result',
             hue_order=['Distinction', 'Pass', 'Fail', 'Withdrawn'], errorbar=None, marker='o')
plt.title(f"Trung bình lượt tương tác theo tuần học - {top_mp[0]} {top_mp[1]}", fontsize=14, pad=15)
plt.xlabel("Tuần học")
plt.ylabel("Trung bình lượt click")
plt.legend(title='Kết quả cuối')
plt.savefig(OUTPUT_FIGURES / '4_weekly_interaction_by_result.png', bbox_inches='tight')
plt.close()

# 5. So sánh các nhóm kết quả cuối (Boxplot tổng click vs final result)
plt.figure()
sns.boxplot(data=df_summary, x='final_result', y='log_total_click',
            order=['Distinction', 'Pass', 'Fail', 'Withdrawn'], palette="Set2")
plt.title("So sánh tương tác VLE theo kết quả học tập", fontsize=14, pad=15)
plt.xlabel("Kết quả cuối")
plt.ylabel("Log1p(Total Click)")
plt.savefig(OUTPUT_FIGURES / '5_total_click_by_final_result.png', bbox_inches='tight')
plt.close()

# 6. Biểu đồ Missing Value (Dựa trên dataframe gốc như studentInfo)
studentInfo = pd.read_csv(STAGING_DIR / 'studentInfo.csv')
missing_pct = (studentInfo.isnull().sum() / len(studentInfo)) * 100
missing_pct = missing_pct[missing_pct > 0].sort_values(ascending=False)
if len(missing_pct) > 0:
    plt.figure()
    ax = sns.barplot(x=missing_pct.values, y=missing_pct.index, color='salmon')
    plt.title("Tỷ lệ giá trị khuyết (Missing Values) trong studentInfo (%)", fontsize=14, pad=15)
    plt.xlabel("Tỷ lệ (%)")
    plt.ylabel("Cột")
    for p in ax.patches:
        ax.annotate(f'{p.get_width():.1f}%', (p.get_width(), p.get_y() + p.get_height() / 2.),
                    ha='left', va='center', xytext=(5, 0), textcoords='offset points')
    plt.savefig(OUTPUT_FIGURES / '6_missing_value_chart.png', bbox_inches='tight')
    plt.close()

# 7. Heatmap Tương quan (Correlation)
numeric_df = df_summary[['total_click', 'active_days', 'interacted_sites',
                         'submitted_assessments', 'late_submissions', 'avg_score', 'studied_credits']].dropna()
plt.figure(figsize=(10, 8))
corr = numeric_df.corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap='coolwarm', vmin=-1, vmax=1, square=True)
plt.title("Ma trận tương quan các biến số", fontsize=14, pad=15)
plt.savefig(OUTPUT_FIGURES / '7_correlation_heatmap.png', bbox_inches='tight')
plt.close()

# 8. Nhóm biểu đồ tổng hợp (Dashboard grid)
fig, axs = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle(f'Dashboard Tổng Hợp - Môn học: {top_mp[0]} {top_mp[1]}', fontsize=18, fontweight='bold', y=0.95)

# Top Left: Result
sns.countplot(data=df_summary[(df_summary['code_module'] == top_mp[0]) & (df_summary['code_presentation'] == top_mp[1])],
              x='final_result', order=['Distinction', 'Pass', 'Fail', 'Withdrawn'], ax=axs[0,0], palette="Set2")
axs[0,0].set_title('Phân bố Kết quả')

# Top Right: Avg Score
sns.histplot(data=df_summary[(df_summary['code_module'] == top_mp[0]) & (df_summary['code_presentation'] == top_mp[1])],
             x='avg_score', bins=20, ax=axs[0,1], color='skyblue')
axs[0,1].set_title('Phân bố Điểm trung bình')

# Bottom Left: Weekly Activity by Result
sns.lineplot(data=df_weekly_sample, x='study_week', y='weekly_click', hue='final_result',
             hue_order=['Distinction', 'Pass', 'Fail', 'Withdrawn'], errorbar=None, ax=axs[1,0])
axs[1,0].set_title('Tương tác VLE theo tuần')

# Bottom Right: Score vs Total Click Scatter
sample_scatter = df_summary[(df_summary['code_module'] == top_mp[0]) & (df_summary['code_presentation'] == top_mp[1])].dropna(subset=['avg_score', 'log_total_click'])
sns.scatterplot(data=sample_scatter, x='log_total_click', y='avg_score', hue='final_result', alpha=0.6, ax=axs[1,1])
axs[1,1].set_title('Điểm trung bình vs Tương tác (Log)')

plt.tight_layout(rect=[0, 0.03, 1, 0.93])
plt.savefig(OUTPUT_FIGURES / '8_dashboard_module_presentation.png', bbox_inches='tight')
plt.close()

print(f"Hoan thanh truc quan hoa! Anh duoc luu tai: {OUTPUT_FIGURES}")
