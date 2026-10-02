from __future__ import annotations

import time
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
STAGING_DIR = ROOT_DIR / "ETL" / "staging_data"
EDA_DIR = ROOT_DIR / "ETL" / "eda_data"
DOC_DIR = ROOT_DIR / "ETL" / "docs" / "03-eda-features"
REPORT_PATH = DOC_DIR / "03_eda_features_report.md"
CHECKLIST_PATH = DOC_DIR / "03_eda_features_checklist.md"

STUDENT_KEY = ["code_module", "code_presentation", "id_student"]
VLE_JOIN_KEY = ["id_site", "code_module", "code_presentation"]


def read_csv(name: str, dtype: str | dict[str, str] = "string") -> pd.DataFrame:
    return pd.read_csv(STAGING_DIR / f"{name}.csv", dtype=dtype, low_memory=False)


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    result = numerator / denominator
    return result.where(denominator.ne(0))


def build_assessment_features() -> tuple[pd.DataFrame, pd.DataFrame]:
    assessments = read_csv("assessments")
    student_assessment = read_csv("studentAssessment")

    assessments["date"] = pd.to_numeric(assessments["date"], errors="coerce")
    assessments["weight"] = pd.to_numeric(assessments["weight"], errors="coerce")
    student_assessment["date_submitted"] = pd.to_numeric(
        student_assessment["date_submitted"], errors="coerce"
    )
    student_assessment["score"] = pd.to_numeric(
        student_assessment["score"], errors="coerce"
    )
    student_assessment["is_banked"] = pd.to_numeric(
        student_assessment["is_banked"], errors="coerce"
    ).fillna(0)

    progress = student_assessment.merge(
        assessments[
            [
                "id_assessment",
                "code_module",
                "code_presentation",
                "assessment_type",
                "date",
                "weight",
            ]
        ],
        on="id_assessment",
        how="left",
        validate="many_to_one",
    )
    progress["is_late"] = (
        progress["date"].notna()
        & progress["date_submitted"].notna()
        & progress["date_submitted"].gt(progress["date"])
    )
    progress["score_weight_product"] = progress["score"] * progress["weight"]

    assessment_summary = progress.groupby(STUDENT_KEY, dropna=False).agg(
        submitted_assessments=("id_assessment", "nunique"),
        submitted_records=("id_assessment", "size"),
        late_submissions=("is_late", "sum"),
        avg_score=("score", "mean"),
        banked_assessments=("is_banked", "sum"),
        score_weight_product_sum=("score_weight_product", "sum"),
        submitted_weight_sum=("weight", "sum"),
    )
    assessment_summary["weighted_score"] = safe_divide(
        assessment_summary["score_weight_product_sum"],
        assessment_summary["submitted_weight_sum"],
    )
    assessment_summary = assessment_summary.reset_index()

    progress = progress[
        [
            "code_module",
            "code_presentation",
            "id_student",
            "id_assessment",
            "assessment_type",
            "date",
            "date_submitted",
            "is_late",
            "is_banked",
            "score",
            "weight",
            "score_weight_product",
        ]
    ]

    return assessment_summary, progress


def build_vle_features(chunksize: int = 500_000) -> tuple[pd.DataFrame, pd.DataFrame]:
    vle_lookup = read_csv("vle")[
        ["id_site", "code_module", "code_presentation", "activity_type"]
    ]

    student_sum_parts: list[pd.DataFrame] = []
    student_day_parts: list[pd.DataFrame] = []
    student_week_parts: list[pd.DataFrame] = []
    student_site_parts: list[pd.DataFrame] = []
    student_resource_parts: list[pd.DataFrame] = []

    weekly_sum_parts: list[pd.DataFrame] = []
    weekly_day_parts: list[pd.DataFrame] = []
    weekly_site_parts: list[pd.DataFrame] = []

    for chunk in pd.read_csv(
        STAGING_DIR / "studentVle.csv",
        usecols=[
            "code_module",
            "code_presentation",
            "id_student",
            "id_site",
            "date",
            "sum_click",
        ],
        dtype={
            "code_module": "string",
            "code_presentation": "string",
            "id_student": "string",
            "id_site": "string",
        },
        chunksize=chunksize,
        low_memory=False,
    ):
        chunk["date"] = pd.to_numeric(chunk["date"], errors="coerce")
        chunk["sum_click"] = pd.to_numeric(chunk["sum_click"], errors="coerce").fillna(0)
        chunk["study_week"] = (chunk["date"] // 7).astype("Int64")

        enriched = chunk.merge(
            vle_lookup,
            on=VLE_JOIN_KEY,
            how="left",
            validate="many_to_one",
        )

        student_sum_parts.append(
            enriched.groupby(STUDENT_KEY, dropna=False).agg(
                total_click=("sum_click", "sum"),
                first_activity_date=("date", "min"),
                last_activity_date=("date", "max"),
            )
        )
        student_day_parts.append(
            enriched[STUDENT_KEY + ["date"]].drop_duplicates()
        )
        student_week_parts.append(
            enriched[STUDENT_KEY + ["study_week"]].drop_duplicates()
        )
        student_site_parts.append(
            enriched[STUDENT_KEY + ["id_site"]].drop_duplicates()
        )
        student_resource_parts.append(
            enriched[STUDENT_KEY + ["activity_type"]]
            .dropna(subset=["activity_type"])
            .drop_duplicates()
        )

        weekly_key = STUDENT_KEY + ["study_week"]
        weekly_sum_parts.append(
            enriched.groupby(weekly_key, dropna=False)["sum_click"]
            .sum()
            .rename("weekly_click")
            .reset_index()
        )
        weekly_day_parts.append(
            enriched[weekly_key + ["date"]].drop_duplicates()
        )
        weekly_site_parts.append(
            enriched[weekly_key + ["id_site"]].drop_duplicates()
        )

    student_clicks = (
        pd.concat(student_sum_parts)
        .groupby(level=STUDENT_KEY, dropna=False)
        .agg(
            total_click=("total_click", "sum"),
            first_activity_date=("first_activity_date", "min"),
            last_activity_date=("last_activity_date", "max"),
        )
        .reset_index()
    )
    active_days = (
        pd.concat(student_day_parts)
        .drop_duplicates()
        .groupby(STUDENT_KEY, dropna=False)
        .size()
        .rename("active_days")
        .reset_index()
    )
    active_weeks = (
        pd.concat(student_week_parts)
        .drop_duplicates()
        .groupby(STUDENT_KEY, dropna=False)
        .size()
        .rename("active_weeks")
        .reset_index()
    )
    interacted_sites = (
        pd.concat(student_site_parts)
        .drop_duplicates()
        .groupby(STUDENT_KEY, dropna=False)
        .size()
        .rename("interacted_sites")
        .reset_index()
    )
    resource_types = (
        pd.concat(student_resource_parts)
        .drop_duplicates()
        .groupby(STUDENT_KEY, dropna=False)
        .size()
        .rename("resource_types_used")
        .reset_index()
    )

    student_vle_summary = student_clicks
    for feature_df in [active_days, active_weeks, interacted_sites, resource_types]:
        student_vle_summary = student_vle_summary.merge(
            feature_df, on=STUDENT_KEY, how="left"
        )

    weekly_clicks = (
        pd.concat(weekly_sum_parts)
        .groupby(STUDENT_KEY + ["study_week"], dropna=False)["weekly_click"]
        .sum()
        .reset_index()
    )
    weekly_active_days = (
        pd.concat(weekly_day_parts)
        .drop_duplicates()
        .groupby(STUDENT_KEY + ["study_week"], dropna=False)
        .size()
        .rename("active_days")
        .reset_index()
    )
    weekly_sites = (
        pd.concat(weekly_site_parts)
        .drop_duplicates()
        .groupby(STUDENT_KEY + ["study_week"], dropna=False)
        .size()
        .rename("interacted_sites")
        .reset_index()
    )

    weekly_activity = weekly_clicks.merge(
        weekly_active_days, on=STUDENT_KEY + ["study_week"], how="left"
    ).merge(weekly_sites, on=STUDENT_KEY + ["study_week"], how="left")

    return student_vle_summary, weekly_activity


def build_student_summary(
    student_vle_summary: pd.DataFrame, assessment_summary: pd.DataFrame
) -> pd.DataFrame:
    student_info = read_csv("studentInfo")
    student_summary = student_info.merge(
        student_vle_summary, on=STUDENT_KEY, how="left"
    ).merge(assessment_summary, on=STUDENT_KEY, how="left")

    zero_columns = [
        "total_click",
        "active_days",
        "active_weeks",
        "interacted_sites",
        "resource_types_used",
        "submitted_assessments",
        "submitted_records",
        "late_submissions",
        "banked_assessments",
        "score_weight_product_sum",
        "submitted_weight_sum",
    ]
    for col in zero_columns:
        if col in student_summary.columns:
            student_summary[col] = student_summary[col].fillna(0)

    return student_summary


def write_report(
    student_summary: pd.DataFrame,
    weekly_activity: pd.DataFrame,
    assessment_progress: pd.DataFrame,
    elapsed_seconds: float,
) -> None:
    DOC_DIR.mkdir(parents=True, exist_ok=True)

    output_rows = [
        ("eda_student_summary.csv", len(student_summary), len(student_summary.columns)),
        ("eda_weekly_activity.csv", len(weekly_activity), len(weekly_activity.columns)),
        (
            "eda_assessment_progress.csv",
            len(assessment_progress),
            len(assessment_progress.columns),
        ),
    ]

    report_lines = [
        "# Báo Cáo Tạo Biến Phục Vụ EDA",
        f"Thời gian chạy: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 1. Mục tiêu",
        "Tạo các biến tổng hợp từ dữ liệu staging để phục vụ EDA nhất quán giữa các notebook/script.",
        "",
        "## 2. Biến đã tạo",
        "| Nhóm biến | Biến | Ý nghĩa |",
        "|---|---|---|",
        "| VLE theo sinh viên | `total_click` | Tổng số click VLE của sinh viên trong một module-presentation |",
        "| VLE theo sinh viên | `active_days` | Số ngày tương đối có hoạt động VLE |",
        "| VLE theo sinh viên | `active_weeks` | Số tuần học có hoạt động VLE, tính bằng `date // 7` |",
        "| VLE theo sinh viên | `interacted_sites` | Số tài nguyên/site VLE sinh viên đã tương tác |",
        "| VLE theo sinh viên | `resource_types_used` | Số loại tài nguyên VLE sinh viên đã tương tác |",
        "| VLE theo sinh viên | `first_activity_date`, `last_activity_date` | Mốc hoạt động VLE đầu/cuối |",
        "| Assessment theo sinh viên | `submitted_assessments` | Số bài đánh giá đã nộp |",
        "| Assessment theo sinh viên | `late_submissions` | Số bài nộp sau hạn `date` của assessment |",
        "| Assessment theo sinh viên | `avg_score` | Điểm trung bình các bài đã nộp |",
        "| Assessment theo sinh viên | `weighted_score` | Điểm trung bình có trọng số theo `weight` |",
        "",
        "## 3. File đầu ra",
        "| File | Số dòng | Số cột |",
        "|---|---:|---:|",
    ]
    for filename, rows, cols in output_rows:
        report_lines.append(f"| `ETL/eda_data/{filename}` | {rows} | {cols} |")

    report_lines.extend(
        [
            "",
            "## 4. Quy tắc xử lý",
            "- `study_week` được tính bằng phép chia nguyên `date // 7`; dữ liệu trước ngày khai giảng có thể có tuần âm.",
            "- `late_submissions` chỉ tính khi assessment có hạn nộp `date` và `date_submitted > date`.",
            "- `weighted_score = sum(score * weight) / sum(weight)` trên các bài có điểm và trọng số.",
            "- Các sinh viên không có hoạt động VLE hoặc assessment được giữ lại trong `eda_student_summary` và điền 0 cho biến đếm/tổng.",
            "",
            "## 5. Kiểm tra nhanh",
            f"- `eda_student_summary` giữ đủ {len(student_summary)} dòng từ `studentInfo`.",
            f"- `eda_weekly_activity` có {len(weekly_activity)} dòng theo sinh viên và tuần học.",
            f"- `eda_assessment_progress` có {len(assessment_progress)} dòng ở mức bài đánh giá đã nộp.",
            f"- Thời gian chạy: {round(elapsed_seconds, 2)} giây.",
            "",
        ]
    )

    checklist_lines = [
        "# Checklist 03 - Tạo Biến Phục Vụ EDA",
        "",
        "Dựa trên danh sách công việc trong `ETL/elt_tasks.csv`, dưới đây là trạng thái các đầu việc thuộc nhóm tạo biến phục vụ EDA.",
        "",
        "## Tạo Biến Phục Vụ EDA",
        "- [x] **Tính tổng số click VLE theo sinh viên:** `total_click` trong `eda_student_summary.csv`.",
        "- [x] **Tính tổng số click theo tuần học hoặc mốc thời gian:** `weekly_click` trong `eda_weekly_activity.csv`.",
        "- [x] **Tính số ngày sinh viên có hoạt động VLE:** `active_days`.",
        "- [x] **Tính số loại tài nguyên VLE mà sinh viên đã tương tác:** `resource_types_used`.",
        "- [x] **Tính số bài đánh giá đã nộp:** `submitted_assessments`.",
        "- [x] **Tính số bài nộp muộn nếu có đủ dữ liệu:** `late_submissions`.",
        "- [x] **Tính điểm trung bình hoặc điểm có trọng số theo assessment:** `avg_score`, `weighted_score`.",
        "",
        "**Trạng thái chung:** Hoàn tất",
        "",
    ]

    REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")
    CHECKLIST_PATH.write_text("\n".join(checklist_lines), encoding="utf-8")


def main() -> None:
    start = time.time()
    EDA_DIR.mkdir(parents=True, exist_ok=True)

    assessment_summary, assessment_progress = build_assessment_features()
    student_vle_summary, weekly_activity = build_vle_features()
    student_summary = build_student_summary(student_vle_summary, assessment_summary)

    student_summary.to_csv(EDA_DIR / "eda_student_summary.csv", index=False)
    weekly_activity.to_csv(EDA_DIR / "eda_weekly_activity.csv", index=False)
    assessment_progress.to_csv(EDA_DIR / "eda_assessment_progress.csv", index=False)

    write_report(
        student_summary=student_summary,
        weekly_activity=weekly_activity,
        assessment_progress=assessment_progress,
        elapsed_seconds=time.time() - start,
    )

    print("Wrote ETL/eda_data/eda_student_summary.csv")
    print("Wrote ETL/eda_data/eda_weekly_activity.csv")
    print("Wrote ETL/eda_data/eda_assessment_progress.csv")
    print("Wrote ETL/docs/03-eda-features/03_eda_features_report.md")
    print("Wrote ETL/docs/03-eda-features/03_eda_features_checklist.md")


if __name__ == "__main__":
    main()
