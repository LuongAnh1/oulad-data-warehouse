"""Detect outliers and unusual values for OULAD EDA."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT_DIR = Path(__file__).resolve().parents[2]
STAGING_DATA_DIR = ROOT_DIR / "ETL" / "staging_data"
EDA_DATA_DIR = ROOT_DIR / "ETL" / "eda_data"
EDA_DIR = ROOT_DIR / "EDA"
TABLE_DIR = EDA_DIR / "outputs" / "tables" / "04_outliers"
FIGURE_DIR = EDA_DIR / "outputs" / "figures" / "04_outliers"
DOC_DIR = EDA_DIR / "docs" / "04-outliers"

STUDENT_SUMMARY = EDA_DATA_DIR / "eda_student_summary.csv"
WEEKLY_ACTIVITY = EDA_DATA_DIR / "eda_weekly_activity.csv"
ASSESSMENT_PROGRESS = EDA_DATA_DIR / "eda_assessment_progress.csv"
STAGING_ASSESSMENTS = STAGING_DATA_DIR / "assessments.csv"
STAGING_STUDENT_VLE = STAGING_DATA_DIR / "studentVle.csv"

KEYS = ["code_module", "code_presentation"]
STUDENT_KEYS = ["code_module", "code_presentation", "id_student"]

VERY_EARLY_DAYS = -60
VERY_LATE_DAYS = 30
WEIGHT_TOTAL_TOLERANCE = 0.01


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create EDA outlier tables, figures, and report."
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1_000_000,
        help="Rows per chunk when scanning staging studentVle.",
    )
    return parser.parse_args()


def ensure_output_dirs() -> None:
    for path in [TABLE_DIR, FIGURE_DIR, DOC_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def read_csv(path: Path, **kwargs) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required input not found: {path}")
    return pd.read_csv(path, **kwargs)


def write_table(df: pd.DataFrame, filename: str) -> Path:
    path = TABLE_DIR / filename
    df.to_csv(path, index=False, encoding="utf-8")
    return path


def fmt_int(value: float | int) -> str:
    return f"{int(round(value)):,}"


def fmt_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def table_link(path: Path) -> str:
    return path.relative_to(ROOT_DIR).as_posix()


def iqr_bounds(df: pd.DataFrame, group_cols: list[str], value_col: str) -> pd.DataFrame:
    quantiles = (
        df.groupby(group_cols)[value_col]
        .quantile([0.25, 0.75])
        .unstack()
        .reset_index()
        .rename(columns={0.25: "q1", 0.75: "q3"})
    )
    quantiles["iqr"] = quantiles["q3"] - quantiles["q1"]
    quantiles["lower_bound"] = (quantiles["q1"] - 1.5 * quantiles["iqr"]).clip(lower=0)
    quantiles["upper_bound"] = quantiles["q3"] + 1.5 * quantiles["iqr"]
    return quantiles


def analyze_score_range(assessment_progress: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    data = assessment_progress.copy()
    data["score_below_0"] = data["score"] < 0
    data["score_above_100"] = data["score"] > 100
    data["score_out_of_range"] = data["score_below_0"] | data["score_above_100"]

    outliers = data[data["score_out_of_range"]].copy()
    summary = pd.DataFrame(
        [
            {
                "rule": "score_outside_0_100",
                "row_count": len(data),
                "outlier_count": int(data["score_out_of_range"].sum()),
                "outlier_pct": data["score_out_of_range"].mean(),
                "below_0_count": int(data["score_below_0"].sum()),
                "above_100_count": int(data["score_above_100"].sum()),
                "min_score": data["score"].min(),
                "max_score": data["score"].max(),
            }
        ]
    )
    return summary, outliers


def analyze_raw_sum_click(chunk_size: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    aggregate_rows: list[pd.DataFrame] = []
    total_rows = 0
    zero_count = 0
    negative_count = 0
    max_sum_click = 0
    total_sum_click = 0

    chunks = pd.read_csv(
        STAGING_STUDENT_VLE,
        usecols=["code_module", "code_presentation", "sum_click"],
        chunksize=chunk_size,
    )
    for chunk in chunks:
        total_rows += len(chunk)
        zero_count += int((chunk["sum_click"] == 0).sum())
        negative_count += int((chunk["sum_click"] < 0).sum())
        max_sum_click = max(max_sum_click, int(chunk["sum_click"].max()))
        total_sum_click += int(chunk["sum_click"].sum())

        grouped = (
            chunk.assign(
                zero_count=chunk["sum_click"].eq(0).astype(int),
                negative_count=chunk["sum_click"].lt(0).astype(int),
            )
            .groupby(KEYS)
            .agg(
                row_count=("sum_click", "size"),
                zero_count=("zero_count", "sum"),
                negative_count=("negative_count", "sum"),
                total_sum_click=("sum_click", "sum"),
                max_sum_click=("sum_click", "max"),
            )
            .reset_index()
        )
        aggregate_rows.append(grouped)

    by_module = (
        pd.concat(aggregate_rows, ignore_index=True)
        .groupby(KEYS)
        .agg(
            row_count=("row_count", "sum"),
            zero_count=("zero_count", "sum"),
            negative_count=("negative_count", "sum"),
            total_sum_click=("total_sum_click", "sum"),
            max_sum_click=("max_sum_click", "max"),
        )
        .reset_index()
        .sort_values(KEYS)
    )
    by_module["zero_pct"] = by_module["zero_count"] / by_module["row_count"]
    by_module["negative_pct"] = by_module["negative_count"] / by_module["row_count"]

    summary = pd.DataFrame(
        [
            {
                "rule": "raw_student_vle_sum_click",
                "row_count": total_rows,
                "zero_count": zero_count,
                "zero_pct": zero_count / total_rows if total_rows else 0,
                "negative_count": negative_count,
                "negative_pct": negative_count / total_rows if total_rows else 0,
                "total_sum_click": total_sum_click,
                "max_sum_click": max_sum_click,
            }
        ]
    )
    return summary, by_module


def analyze_student_click_outliers(student_summary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    bounds = iqr_bounds(student_summary, KEYS, "total_click")
    data = student_summary.merge(bounds, on=KEYS, how="left")
    data["zero_total_click"] = data["total_click"].fillna(0).eq(0)
    data["high_total_click_iqr"] = data["total_click"] > data["upper_bound"]
    data["low_total_click_iqr"] = (
        (data["total_click"] < data["lower_bound"]) & ~data["zero_total_click"]
    )
    data["student_click_outlier"] = (
        data["zero_total_click"] | data["high_total_click_iqr"] | data["low_total_click_iqr"]
    )

    outliers = data[data["student_click_outlier"]].copy()
    columns = STUDENT_KEYS + [
        "final_result",
        "total_click",
        "active_days",
        "active_weeks",
        "q1",
        "q3",
        "lower_bound",
        "upper_bound",
        "zero_total_click",
        "low_total_click_iqr",
        "high_total_click_iqr",
    ]
    outliers = outliers[columns].sort_values(
        ["high_total_click_iqr", "zero_total_click", "total_click"],
        ascending=[False, False, False],
    )

    summary = (
        data.groupby(KEYS)
        .agg(
            student_records=("id_student", "size"),
            zero_total_click_count=("zero_total_click", "sum"),
            high_total_click_iqr_count=("high_total_click_iqr", "sum"),
            low_total_click_iqr_count=("low_total_click_iqr", "sum"),
            median_total_click=("total_click", "median"),
            max_total_click=("total_click", "max"),
            iqr_upper_bound=("upper_bound", "first"),
        )
        .reset_index()
    )
    summary["zero_total_click_pct"] = summary["zero_total_click_count"] / summary["student_records"]
    summary["high_total_click_iqr_pct"] = (
        summary["high_total_click_iqr_count"] / summary["student_records"]
    )
    summary["low_total_click_iqr_pct"] = (
        summary["low_total_click_iqr_count"] / summary["student_records"]
    )
    return summary.sort_values(KEYS), outliers


def analyze_weekly_click_outliers(weekly_activity: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    bounds = iqr_bounds(weekly_activity, KEYS, "weekly_click")
    data = weekly_activity.merge(bounds, on=KEYS, how="left")
    data["zero_weekly_click"] = data["weekly_click"].eq(0)
    data["negative_weekly_click"] = data["weekly_click"].lt(0)
    data["high_weekly_click_iqr"] = data["weekly_click"] > data["upper_bound"]
    data["weekly_click_outlier"] = data["negative_weekly_click"] | data["high_weekly_click_iqr"]

    outliers = data[data["weekly_click_outlier"]].copy()
    outliers = outliers[
        STUDENT_KEYS
        + [
            "study_week",
            "weekly_click",
            "active_days",
            "q1",
            "q3",
            "upper_bound",
            "negative_weekly_click",
            "high_weekly_click_iqr",
        ]
    ].sort_values("weekly_click", ascending=False)

    summary = (
        data.groupby(KEYS)
        .agg(
            weekly_records=("weekly_click", "size"),
            zero_weekly_click_count=("zero_weekly_click", "sum"),
            negative_weekly_click_count=("negative_weekly_click", "sum"),
            high_weekly_click_iqr_count=("high_weekly_click_iqr", "sum"),
            median_weekly_click=("weekly_click", "median"),
            max_weekly_click=("weekly_click", "max"),
            iqr_upper_bound=("upper_bound", "first"),
        )
        .reset_index()
    )
    summary["zero_weekly_click_pct"] = summary["zero_weekly_click_count"] / summary["weekly_records"]
    summary["negative_weekly_click_pct"] = (
        summary["negative_weekly_click_count"] / summary["weekly_records"]
    )
    summary["high_weekly_click_iqr_pct"] = (
        summary["high_weekly_click_iqr_count"] / summary["weekly_records"]
    )
    return summary.sort_values(KEYS), outliers


def analyze_submission_timing(
    assessment_progress: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    data = assessment_progress.copy()
    data["days_from_due"] = data["date_submitted"] - data["date"]
    data["missing_due_date"] = data["date"].isna()
    data["very_early_submission"] = (
        data["days_from_due"].notna() & (data["days_from_due"] < VERY_EARLY_DAYS)
    )
    data["very_late_submission"] = (
        data["days_from_due"].notna() & (data["days_from_due"] > VERY_LATE_DAYS)
    )
    data["submission_timing_outlier"] = (
        data["very_early_submission"] | data["very_late_submission"]
    )

    outliers = data[data["submission_timing_outlier"]].copy()
    outliers = outliers[
        STUDENT_KEYS
        + [
            "id_assessment",
            "assessment_type",
            "date",
            "date_submitted",
            "days_from_due",
            "very_early_submission",
            "very_late_submission",
            "score",
            "weight",
        ]
    ].sort_values("days_from_due")

    summary = pd.DataFrame(
        [
            {
                "rule": "submission_timing",
                "row_count": len(data),
                "missing_due_date_count": int(data["missing_due_date"].sum()),
                "very_early_threshold_days": VERY_EARLY_DAYS,
                "very_early_count": int(data["very_early_submission"].sum()),
                "very_early_pct": data["very_early_submission"].mean(),
                "very_late_threshold_days": VERY_LATE_DAYS,
                "very_late_count": int(data["very_late_submission"].sum()),
                "very_late_pct": data["very_late_submission"].mean(),
                "min_days_from_due": data["days_from_due"].min(),
                "median_days_from_due": data["days_from_due"].median(),
                "max_days_from_due": data["days_from_due"].max(),
            }
        ]
    )
    by_module = (
        data.groupby(KEYS)
        .agg(
            submission_records=("id_student", "size"),
            missing_due_date_count=("missing_due_date", "sum"),
            very_early_count=("very_early_submission", "sum"),
            very_late_count=("very_late_submission", "sum"),
            median_days_from_due=("days_from_due", "median"),
            min_days_from_due=("days_from_due", "min"),
            max_days_from_due=("days_from_due", "max"),
        )
        .reset_index()
    )
    by_module["very_early_pct"] = by_module["very_early_count"] / by_module["submission_records"]
    by_module["very_late_pct"] = by_module["very_late_count"] / by_module["submission_records"]
    return summary, by_module.sort_values(KEYS), outliers


def analyze_assessment_weight(
    assessments: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    data = assessments.copy()
    data["is_exam"] = data["assessment_type"].eq("Exam")
    data["weight_missing"] = data["weight"].isna()
    data["weight_below_0"] = data["weight"] < 0
    data["weight_above_100"] = data["weight"] > 100
    data["zero_weight"] = data["weight"].fillna(-1).eq(0)
    data["weight_range_outlier"] = data["weight_below_0"] | data["weight_above_100"]

    by_module = (
        data.groupby(KEYS)
        .agg(
            assessment_count=("id_assessment", "nunique"),
            total_weight=("weight", "sum"),
            exam_weight=("weight", lambda s: s[data.loc[s.index, "is_exam"]].sum()),
            non_exam_weight=("weight", lambda s: s[~data.loc[s.index, "is_exam"]].sum()),
            zero_weight_count=("zero_weight", "sum"),
            missing_weight_count=("weight_missing", "sum"),
            min_weight=("weight", "min"),
            max_weight=("weight", "max"),
            mean_weight=("weight", "mean"),
            assessment_types=("assessment_type", lambda s: ",".join(sorted(s.unique()))),
        )
        .reset_index()
    )
    by_module["non_exam_weight_not_100"] = (
        by_module["non_exam_weight"].sub(100).abs() > WEIGHT_TOTAL_TOLERANCE
    )
    by_module["exam_weight_not_100"] = (
        by_module["exam_weight"].gt(0)
        & by_module["exam_weight"].sub(100).abs().gt(WEIGHT_TOTAL_TOLERANCE)
    )

    outliers = data[
        data["weight_range_outlier"] | data["zero_weight"] | data["weight_missing"]
    ].copy()
    outliers = outliers[
        KEYS
        + [
            "id_assessment",
            "assessment_type",
            "date",
            "weight",
            "weight_missing",
            "zero_weight",
            "weight_below_0",
            "weight_above_100",
        ]
    ].sort_values(KEYS + ["id_assessment"])

    summary = pd.DataFrame(
        [
            {
                "rule": "assessment_weight",
                "assessment_count": len(data),
                "missing_weight_count": int(data["weight_missing"].sum()),
                "zero_weight_count": int(data["zero_weight"].sum()),
                "below_0_count": int(data["weight_below_0"].sum()),
                "above_100_count": int(data["weight_above_100"].sum()),
                "non_exam_weight_not_100_count": int(
                    by_module["non_exam_weight_not_100"].sum()
                ),
                "exam_weight_not_100_count": int(
                    by_module["exam_weight_not_100"].sum()
                ),
                "min_weight": data["weight"].min(),
                "median_weight": data["weight"].median(),
                "max_weight": data["weight"].max(),
            }
        ]
    )
    return summary, by_module.sort_values(KEYS), outliers


def build_outlier_summary_by_module_presentation(
    student_click_summary: pd.DataFrame,
    weekly_click_summary: pd.DataFrame,
    submission_by_module: pd.DataFrame,
    assessment_weight_by_module: pd.DataFrame,
    score_outliers: pd.DataFrame,
) -> pd.DataFrame:
    summary = student_click_summary.merge(
        weekly_click_summary[
            KEYS
            + [
                "weekly_records",
                "negative_weekly_click_count",
                "high_weekly_click_iqr_count",
                "negative_weekly_click_pct",
                "high_weekly_click_iqr_pct",
            ]
        ],
        on=KEYS,
        how="outer",
    ).merge(
        submission_by_module[
            KEYS
            + [
                "submission_records",
                "very_early_count",
                "very_late_count",
                "very_early_pct",
                "very_late_pct",
            ]
        ],
        on=KEYS,
        how="outer",
    ).merge(
        assessment_weight_by_module[
            KEYS
            + [
                "total_weight",
                "exam_weight",
                "non_exam_weight",
                "zero_weight_count",
                "non_exam_weight_not_100",
                "exam_weight_not_100",
            ]
        ],
        on=KEYS,
        how="outer",
    )

    if len(score_outliers):
        score_summary = (
            score_outliers.groupby(KEYS).size().reset_index(name="score_range_outlier_count")
        )
        summary = summary.merge(score_summary, on=KEYS, how="left")
    else:
        summary["score_range_outlier_count"] = 0

    count_cols = [
        "zero_total_click_count",
        "high_total_click_iqr_count",
        "low_total_click_iqr_count",
        "negative_weekly_click_count",
        "high_weekly_click_iqr_count",
        "very_early_count",
        "very_late_count",
        "zero_weight_count",
        "score_range_outlier_count",
    ]
    for column in count_cols:
        if column in summary.columns:
            summary[column] = summary[column].fillna(0).astype(int)

    summary["has_any_outlier_signal"] = (
        summary[count_cols].sum(axis=1).gt(0)
        | summary["non_exam_weight_not_100"].fillna(False).astype(bool)
        | summary["exam_weight_not_100"].fillna(False).astype(bool)
    )
    return summary.sort_values(KEYS)


def save_current_figure(filename: str) -> Path:
    path = FIGURE_DIR / filename
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()
    return path


def create_figures(
    student_summary: pd.DataFrame,
    student_click_summary: pd.DataFrame,
    submission_timing_outliers: pd.DataFrame,
    assessment_weight_by_module: pd.DataFrame,
    outlier_summary: pd.DataFrame,
    raw_sum_click_by_module: pd.DataFrame,
    assessment_progress: pd.DataFrame,
) -> list[Path]:
    figure_paths: list[Path] = []

    plot_data = student_summary.copy()
    plot_data["log_total_click"] = pd.to_numeric(
        plot_data["total_click"], errors="coerce"
    ).fillna(0).clip(lower=0).map(math.log1p)
    plot_data["module_presentation"] = (
        plot_data["code_module"] + "-" + plot_data["code_presentation"]
    )
    plt.figure(figsize=(14, 6))
    sns.boxplot(data=plot_data, x="module_presentation", y="log_total_click", color="#4C78A8")
    plt.title("Boxplot log1p(total_click) theo module-presentation")
    plt.xlabel("Module-presentation")
    plt.ylabel("log1p(total_click)")
    plt.xticks(rotation=60, ha="right")
    figure_paths.append(save_current_figure("student_total_click_boxplot_by_module_presentation.png"))

    click_rate = student_click_summary.copy()
    click_rate["module_presentation"] = (
        click_rate["code_module"] + "-" + click_rate["code_presentation"]
    )
    plt.figure(figsize=(14, 6))
    sns.barplot(
        data=click_rate,
        x="module_presentation",
        y="high_total_click_iqr_pct",
        color="#F58518",
    )
    plt.title("Tỷ lệ sinh viên có total_click cao theo IQR")
    plt.xlabel("Module-presentation")
    plt.ylabel("Tỷ lệ")
    plt.xticks(rotation=60, ha="right")
    figure_paths.append(save_current_figure("high_total_click_rate_by_module_presentation.png"))

    heatmap_data = outlier_summary.copy()
    heatmap_data["module_presentation"] = (
        heatmap_data["code_module"] + "-" + heatmap_data["code_presentation"]
    )
    heatmap_cols = [
        "zero_total_click_pct",
        "high_total_click_iqr_pct",
        "high_weekly_click_iqr_pct",
        "very_early_pct",
        "very_late_pct",
    ]
    heatmap_matrix = heatmap_data.set_index("module_presentation")[heatmap_cols].fillna(0)
    plt.figure(figsize=(9, max(6, len(heatmap_matrix) * 0.34)))
    sns.heatmap(
        heatmap_matrix,
        cmap="YlOrRd",
        annot=True,
        fmt=".1%",
        linewidths=0.5,
        cbar_kws={"label": "Tỷ lệ"},
    )
    plt.title("Heatmap tỷ lệ tín hiệu ngoại lệ theo module-presentation")
    plt.xlabel("Tín hiệu ngoại lệ")
    plt.ylabel("Module-presentation")
    figure_paths.append(save_current_figure("outlier_rate_heatmap_by_module_presentation.png"))

    delay_data = assessment_progress.copy()
    delay_data["days_from_due"] = delay_data["date_submitted"] - delay_data["date"]
    delay_data = delay_data[delay_data["days_from_due"].notna()].copy()
    clipped = delay_data["days_from_due"].clip(lower=-100, upper=100)
    plt.figure(figsize=(10, 5))
    sns.histplot(clipped, bins=60, color="#72B7B2")
    plt.axvline(VERY_EARLY_DAYS, color="#E45756", linestyle="--", label="very early")
    plt.axvline(VERY_LATE_DAYS, color="#F58518", linestyle="--", label="very late")
    plt.title("Phân bố số ngày nộp so với hạn")
    plt.xlabel("date_submitted - date, clipped [-100, 100]")
    plt.ylabel("Số submission")
    plt.legend()
    figure_paths.append(save_current_figure("submission_delay_distribution.png"))

    if len(submission_timing_outliers):
        timing_counts = (
            submission_timing_outliers.assign(
                module_presentation=lambda df: df["code_module"] + "-" + df["code_presentation"],
                outlier_type=lambda df: df["very_late_submission"].map(
                    {True: "very_late", False: "very_early"}
                ),
            )
            .groupby(["module_presentation", "outlier_type"])
            .size()
            .reset_index(name="count")
        )
        plt.figure(figsize=(14, 6))
        sns.barplot(
            data=timing_counts,
            x="module_presentation",
            y="count",
            hue="outlier_type",
        )
        plt.title("Submission quá sớm/quá muộn theo module-presentation")
        plt.xlabel("Module-presentation")
        plt.ylabel("Số submission")
        plt.xticks(rotation=60, ha="right")
        figure_paths.append(save_current_figure("submission_timing_outliers_by_module_presentation.png"))

    timing_scatter = outlier_summary.copy()
    timing_scatter["module_presentation"] = (
        timing_scatter["code_module"] + "-" + timing_scatter["code_presentation"]
    )
    plt.figure(figsize=(9, 6))
    sizes = (
        timing_scatter["submission_records"].fillna(0)
        / timing_scatter["submission_records"].fillna(0).max()
        * 900
        + 80
    )
    plt.scatter(
        timing_scatter["very_early_pct"].fillna(0),
        timing_scatter["very_late_pct"].fillna(0),
        s=sizes,
        alpha=0.65,
        color="#4C78A8",
        edgecolor="white",
        linewidth=1,
    )
    for row in timing_scatter.itertuples(index=False):
        plt.annotate(
            row.module_presentation,
            (row.very_early_pct if pd.notna(row.very_early_pct) else 0, row.very_late_pct if pd.notna(row.very_late_pct) else 0),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=8,
        )
    plt.title("Submission quá sớm và quá muộn theo module-presentation")
    plt.xlabel("Tỷ lệ submission quá sớm")
    plt.ylabel("Tỷ lệ submission quá muộn")
    figure_paths.append(save_current_figure("submission_timing_scatter_by_module_presentation.png"))

    weight_plot = assessment_weight_by_module.copy()
    weight_plot["module_presentation"] = (
        weight_plot["code_module"] + "-" + weight_plot["code_presentation"]
    )
    weight_plot = weight_plot.set_index("module_presentation")[["non_exam_weight", "exam_weight"]]
    weight_plot.plot(kind="bar", stacked=True, figsize=(14, 5), color=["#B279A2", "#4C78A8"])
    plt.title("Tổng weight non-Exam và Exam theo module-presentation")
    plt.xlabel("Module-presentation")
    plt.ylabel("Tổng weight")
    plt.xticks(rotation=60, ha="right")
    figure_paths.append(save_current_figure("assessment_total_weight_by_module_presentation.png"))

    weight_scatter = assessment_weight_by_module.copy()
    weight_scatter["module_presentation"] = (
        weight_scatter["code_module"] + "-" + weight_scatter["code_presentation"]
    )
    plt.figure(figsize=(8, 6))
    plt.scatter(
        weight_scatter["non_exam_weight"],
        weight_scatter["exam_weight"],
        s=weight_scatter["assessment_count"] * 18,
        alpha=0.7,
        color="#B279A2",
        edgecolor="white",
        linewidth=1,
    )
    plt.axvline(100, color="#E45756", linestyle="--", linewidth=1)
    plt.axhline(100, color="#E45756", linestyle="--", linewidth=1)
    for row in weight_scatter.itertuples(index=False):
        plt.annotate(
            row.module_presentation,
            (row.non_exam_weight, row.exam_weight),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=8,
        )
    plt.title("Exam weight và non-Exam weight")
    plt.xlabel("Tổng non-Exam weight")
    plt.ylabel("Tổng Exam weight")
    figure_paths.append(save_current_figure("assessment_weight_exam_non_exam_scatter.png"))

    return figure_paths


def write_report(
    table_paths: dict[str, Path],
    figure_paths: list[Path],
    score_range_summary: pd.DataFrame,
    raw_sum_click_summary: pd.DataFrame,
    student_click_summary: pd.DataFrame,
    weekly_click_summary: pd.DataFrame,
    submission_timing_summary: pd.DataFrame,
    assessment_weight_summary: pd.DataFrame,
) -> Path:
    table_lines = "\n".join(
        f"- `{table_link(path)}`" for path in sorted(table_paths.values(), key=lambda p: p.name)
    )
    figure_lines = "\n".join(
        f"- `{table_link(path)}`" for path in sorted(figure_paths, key=lambda p: p.name)
    )

    score = score_range_summary.iloc[0]
    raw_click = raw_sum_click_summary.iloc[0]
    student_zero = int(student_click_summary["zero_total_click_count"].sum())
    student_high = int(student_click_summary["high_total_click_iqr_count"].sum())
    weekly_negative = int(weekly_click_summary["negative_weekly_click_count"].sum())
    weekly_high = int(weekly_click_summary["high_weekly_click_iqr_count"].sum())
    timing = submission_timing_summary.iloc[0]
    weight = assessment_weight_summary.iloc[0]

    report = f"""# Báo Cáo EDA - Phát Hiện Dữ Liệu Ngoại Lệ

## 1. Phạm vi

Phần này phát hiện giá trị bất thường trong dữ liệu OULAD sau ELT. Kết quả chỉ gắn cờ và mô tả, không tự động xóa outlier. Với OULAD, một số outlier có thể là hành vi học tập thật, ví dụ sinh viên tương tác VLE rất nhiều trước assessment.

## 2. Quy tắc đã dùng

- `score` hợp lệ trong khoảng 0 đến 100.
- `sum_click` không được âm. Dòng `sum_click = 0` được thống kê như tín hiệu cần xem tỷ lệ, không mặc định là lỗi.
- Sinh viên có `total_click` rất cao được phát hiện bằng IQR trong từng module-presentation.
- Submission quá sớm nếu `date_submitted - date < {VERY_EARLY_DAYS}` ngày.
- Submission quá muộn nếu `date_submitted - date > {VERY_LATE_DAYS}` ngày.
- `weight` assessment hợp lệ trong khoảng 0 đến 100. Tổng weight được tách `Exam` và non-Exam vì OULAD có thể chấm exam riêng với coursework.

## 3. Nhận xét chính

- `score` ngoài khoảng 0-100: {fmt_int(score["outlier_count"])} dòng.
- Dòng raw `studentVle.sum_click = 0`: {fmt_int(raw_click["zero_count"])} trên {fmt_int(raw_click["row_count"])} dòng, chiếm {fmt_pct(raw_click["zero_pct"])}.
- Dòng raw `studentVle.sum_click < 0`: {fmt_int(raw_click["negative_count"])} dòng.
- Sinh viên có `total_click = 0`: {fmt_int(student_zero)} bản ghi student-module-presentation.
- Sinh viên có `total_click` cao theo IQR trong module-presentation: {fmt_int(student_high)} bản ghi.
- Weekly activity có `weekly_click < 0`: {fmt_int(weekly_negative)} dòng.
- Weekly activity có `weekly_click` cao theo IQR: {fmt_int(weekly_high)} dòng.
- Submission quá sớm hơn {abs(VERY_EARLY_DAYS)} ngày so với hạn: {fmt_int(timing["very_early_count"])} dòng.
- Submission quá muộn hơn {VERY_LATE_DAYS} ngày so với hạn: {fmt_int(timing["very_late_count"])} dòng.
- Assessment có `weight = 0`: {fmt_int(weight["zero_weight_count"])} dòng.
- Module-presentation có tổng non-Exam weight khác 100: {fmt_int(weight["non_exam_weight_not_100_count"])} nhóm.
- Module-presentation có tổng Exam weight khác 100: {fmt_int(weight["exam_weight_not_100_count"])} nhóm.

Đọc diễn giải chi tiết tại [04_outliers_insights.md](04_outliers_insights.md).

## 4. Diễn giải

- Không phát hiện `score` âm hoặc lớn hơn 100, nên điểm assessment cơ bản nằm trong khoảng hợp lý.
- Không phát hiện `sum_click` âm, nên biến click không có lỗi âm rõ ràng.
- `sum_click = 0` và `total_click = 0` nên được giữ lại để phân tích nhóm ít hoặc không tương tác, không tự động xóa.
- Các submission quá sớm/quá muộn nên được kiểm tra trong bối cảnh deadline của từng assessment.
- Assessment có `weight = 0` hoặc tổng Exam/non-Exam khác 100 cần ghi chú vì có thể là đặc thù thiết kế đánh giá, không nhất thiết là lỗi.

## 5. Bảng đầu ra

{table_lines}

## 6. Biểu đồ đầu ra

{figure_lines}

## 7. Khuyến nghị xử lý

- Giữ outlier trong dữ liệu EDA ban đầu.
- Khi trực quan hóa click, dùng log scale hoặc winsorized view để tránh vài giá trị lớn che khuất phần còn lại.
- Nếu xây mô hình, tạo flag như `is_zero_click`, `is_high_click_iqr`, `is_very_late_submission`.
- So sánh outlier theo module-presentation thay vì chỉ nhìn toàn bộ dữ liệu.
"""
    path = DOC_DIR / "04_outliers_report.md"
    path.write_text(report, encoding="utf-8")
    return path


def write_insights(
    score_range_summary: pd.DataFrame,
    raw_sum_click_summary: pd.DataFrame,
    student_click_summary: pd.DataFrame,
    weekly_click_summary: pd.DataFrame,
    submission_timing_summary: pd.DataFrame,
    submission_timing_by_module: pd.DataFrame,
    assessment_weight_summary: pd.DataFrame,
    assessment_weight_by_module: pd.DataFrame,
) -> Path:
    score = score_range_summary.iloc[0]
    raw_click = raw_sum_click_summary.iloc[0]
    high_click_module = student_click_summary.sort_values(
        "high_total_click_iqr_pct", ascending=False
    ).iloc[0]
    zero_click_module = student_click_summary.sort_values(
        "zero_total_click_pct", ascending=False
    ).iloc[0]
    weekly_high_module = weekly_click_summary.sort_values(
        "high_weekly_click_iqr_pct", ascending=False
    ).iloc[0]
    timing = submission_timing_summary.iloc[0]
    early_module = submission_timing_by_module.sort_values(
        "very_early_pct", ascending=False
    ).iloc[0]
    late_module = submission_timing_by_module.sort_values(
        "very_late_pct", ascending=False
    ).iloc[0]
    weight = assessment_weight_summary.iloc[0]
    non_exam_issue = assessment_weight_by_module[
        assessment_weight_by_module["non_exam_weight_not_100"]
    ]
    exam_issue = assessment_weight_by_module[
        assessment_weight_by_module["exam_weight_not_100"]
    ]

    insights = f"""# EDA Insights - Phát Hiện Dữ Liệu Ngoại Lệ

## Cách đọc nhanh

File report chính liệt kê các rule và số lượng outlier. File này giải thích outlier nào là lỗi dữ liệu rõ ràng, outlier nào có thể là hành vi học thật, và nên xử lý thế nào ở bước sau.

## 1. Score và sum_click không có lỗi range rõ ràng

Quan sát:

- `score` ngoài khoảng 0-100: {fmt_int(score["outlier_count"])} dòng.
- Raw `studentVle.sum_click < 0`: {fmt_int(raw_click["negative_count"])} dòng.
- Raw `studentVle.sum_click = 0`: {fmt_int(raw_click["zero_count"])} dòng.

Diễn giải:

- Các biến số lõi không có lỗi range thô. Đây là tín hiệu tốt cho chất lượng staging.
- Không có dòng raw `sum_click = 0`, nhưng vẫn có sinh viên có `total_click = 0` ở bảng tổng hợp. Điều này thường nghĩa là sinh viên có đăng ký/thông tin học tập nhưng không có hoạt động VLE quan sát được.

Ý nghĩa với phân tích sau:

- Không cần rule loại bỏ score ngoài khoảng.
- Nên giữ nhóm `total_click = 0` như một nhóm hành vi riêng.

## 2. Tương tác VLE rất thấp hoặc rất cao

Quan sát:

- Module-presentation có tỷ lệ `total_click = 0` cao nhất là `{zero_click_module["code_module"]}-{zero_click_module["code_presentation"]}`, chiếm {fmt_pct(zero_click_module["zero_total_click_pct"])}.
- Module-presentation có tỷ lệ sinh viên `total_click` cao theo IQR lớn nhất là `{high_click_module["code_module"]}-{high_click_module["code_presentation"]}`, chiếm {fmt_pct(high_click_module["high_total_click_iqr_pct"])}.
- Module-presentation có tỷ lệ weekly click cao theo IQR lớn nhất là `{weekly_high_module["code_module"]}-{weekly_high_module["code_presentation"]}`, chiếm {fmt_pct(weekly_high_module["high_weekly_click_iqr_pct"])}.

Diễn giải:

- Tương tác VLE có đuôi phải dài. Người học có click rất cao không nên bị xóa mặc định vì đó có thể là hành vi ôn tập thật.
- Nhóm `total_click = 0` lại là tín hiệu khác: sinh viên có thể không vào VLE, hoặc hoạt động không được ghi nhận ở bảng tương tác.

Ý nghĩa với phân tích sau:

- Nên tạo các flag `is_zero_click`, `is_high_click_iqr`.
- Khi dùng click làm feature, nên dùng `log1p` hoặc binning để giảm ảnh hưởng của vài giá trị rất lớn.

## 3. Submission quá sớm hoặc quá muộn

Quan sát:

- Submission quá sớm hơn {abs(VERY_EARLY_DAYS)} ngày: {fmt_int(timing["very_early_count"])} dòng.
- Submission quá muộn hơn {VERY_LATE_DAYS} ngày: {fmt_int(timing["very_late_count"])} dòng.
- Tỷ lệ quá sớm cao nhất ở `{early_module["code_module"]}-{early_module["code_presentation"]}`, chiếm {fmt_pct(early_module["very_early_pct"])}.
- Tỷ lệ quá muộn cao nhất ở `{late_module["code_module"]}-{late_module["code_presentation"]}`, chiếm {fmt_pct(late_module["very_late_pct"])}.

Diễn giải:

- Nộp rất sớm không nhất thiết là lỗi. Một số assessment có thể mở sớm hoặc có cách tính ngày tương đối khác nhau.
- Nộp rất muộn đáng chú ý hơn cho phân tích hành vi học, đặc biệt nếu gắn với `final_result` hoặc score thấp.

Ý nghĩa với phân tích sau:

- Nên tạo biến `days_from_due`, `is_very_early_submission`, `is_very_late_submission`.
- Nếu nhóm chọn bài toán cảnh báo sớm, cần kiểm soát checkpoint thời gian để tránh dùng thông tin tương lai.

## 4. Weight assessment

Quan sát:

- Assessment có `weight = 0`: {fmt_int(weight["zero_weight_count"])} dòng.
- Module-presentation có non-Exam weight khác 100: {fmt_int(weight["non_exam_weight_not_100_count"])} nhóm.
- Module-presentation có Exam weight khác 100: {fmt_int(weight["exam_weight_not_100_count"])} nhóm.

Diễn giải:

- `weight = 0` thường không phải lỗi range vì vẫn nằm trong khoảng 0-100. Nó có thể là assessment không đóng góp trực tiếp vào điểm cuối.
- Cần tách Exam và non-Exam. Nếu cộng tất cả assessment lại, nhiều module-presentation có tổng 200 hoặc 300 vì exam và coursework có thể là hai thành phần riêng.

Module-presentation cần ghi chú:

{chr(10).join(f'- Non-Exam khác 100: `{row.code_module}-{row.code_presentation}` có non_exam_weight = {row.non_exam_weight:.1f}.' for row in non_exam_issue.itertuples(index=False))}
{chr(10).join(f'- Exam khác 100: `{row.code_module}-{row.code_presentation}` có exam_weight = {row.exam_weight:.1f}.' for row in exam_issue.itertuples(index=False))}

Ý nghĩa với phân tích sau:

- Khi tính weighted score, nên dùng tổng trọng số đã nộp thay vì giả định mọi module có cùng cấu trúc assessment.
- Các assessment weight 0 nên được giữ lại cho phân tích hành vi nộp bài, nhưng không nên làm sai điểm weighted score.

## 5. Kết luận xử lý outlier

- Không xóa outlier tự động.
- Gắn cờ outlier để phân tích sâu hơn.
- Luôn so sánh theo module-presentation.
- Với click và submission timing, outlier có thể là tín hiệu hành vi học quan trọng thay vì lỗi dữ liệu.
"""
    path = DOC_DIR / "04_outliers_insights.md"
    path.write_text(insights, encoding="utf-8")
    return path


def write_checklist() -> Path:
    checklist = """# Checklist EDA - Phát Hiện Dữ Liệu Ngoại Lệ

- [x] Kiểm tra `score` ngoài khoảng hợp lý.
- [x] Kiểm tra `sum_click` bằng 0 quá cao hoặc âm.
- [x] Kiểm tra `date_submitted` quá sớm hoặc quá muộn so với hạn `date`.
- [x] Kiểm tra sinh viên có tương tác VLE rất cao hoặc rất thấp.
- [x] Kiểm tra assessment có `weight` bất thường.
- [x] So sánh outlier theo từng module-presentation.

Minh chứng:

- Script: `EDA/src/04_detect_outliers.py`
- Report: `EDA/docs/04-outliers/04_outliers_report.md`
- Insights: `EDA/docs/04-outliers/04_outliers_insights.md`
- Tables: `EDA/outputs/tables/04_outliers/`
- Figures: `EDA/outputs/figures/04_outliers/`
"""
    path = DOC_DIR / "04_outliers_checklist.md"
    path.write_text(checklist, encoding="utf-8")
    return path


def main() -> None:
    args = parse_args()
    ensure_output_dirs()
    sns.set_theme(style="whitegrid", context="notebook")

    student_summary = read_csv(STUDENT_SUMMARY)
    weekly_activity = read_csv(WEEKLY_ACTIVITY)
    assessment_progress = read_csv(ASSESSMENT_PROGRESS)
    assessments = read_csv(STAGING_ASSESSMENTS)

    score_range_summary, score_range_outliers = analyze_score_range(assessment_progress)
    raw_sum_click_summary, raw_sum_click_by_module = analyze_raw_sum_click(args.chunk_size)
    student_click_summary, student_click_outliers = analyze_student_click_outliers(
        student_summary
    )
    weekly_click_summary, weekly_click_outliers = analyze_weekly_click_outliers(
        weekly_activity
    )
    (
        submission_timing_summary,
        submission_timing_by_module,
        submission_timing_outliers,
    ) = analyze_submission_timing(assessment_progress)
    (
        assessment_weight_summary,
        assessment_weight_by_module,
        assessment_weight_outliers,
    ) = analyze_assessment_weight(assessments)
    outlier_summary = build_outlier_summary_by_module_presentation(
        student_click_summary=student_click_summary,
        weekly_click_summary=weekly_click_summary,
        submission_by_module=submission_timing_by_module,
        assessment_weight_by_module=assessment_weight_by_module,
        score_outliers=score_range_outliers,
    )

    output_tables = {
        "score_range_summary.csv": score_range_summary,
        "score_range_outliers.csv": score_range_outliers,
        "raw_sum_click_summary.csv": raw_sum_click_summary,
        "raw_sum_click_by_module_presentation.csv": raw_sum_click_by_module,
        "student_click_outlier_summary_by_module_presentation.csv": student_click_summary,
        "student_click_outliers.csv": student_click_outliers,
        "weekly_click_outlier_summary_by_module_presentation.csv": weekly_click_summary,
        "weekly_click_outliers.csv": weekly_click_outliers,
        "submission_timing_summary.csv": submission_timing_summary,
        "submission_timing_by_module_presentation.csv": submission_timing_by_module,
        "submission_timing_outliers.csv": submission_timing_outliers,
        "assessment_weight_summary.csv": assessment_weight_summary,
        "assessment_weight_by_module_presentation.csv": assessment_weight_by_module,
        "assessment_weight_outliers.csv": assessment_weight_outliers,
        "outlier_summary_by_module_presentation.csv": outlier_summary,
    }
    table_paths = {
        filename: write_table(dataframe, filename)
        for filename, dataframe in output_tables.items()
    }
    figure_paths = create_figures(
        student_summary=student_summary,
        student_click_summary=student_click_summary,
        submission_timing_outliers=submission_timing_outliers,
        assessment_weight_by_module=assessment_weight_by_module,
        outlier_summary=outlier_summary,
        raw_sum_click_by_module=raw_sum_click_by_module,
        assessment_progress=assessment_progress,
    )
    report_path = write_report(
        table_paths=table_paths,
        figure_paths=figure_paths,
        score_range_summary=score_range_summary,
        raw_sum_click_summary=raw_sum_click_summary,
        student_click_summary=student_click_summary,
        weekly_click_summary=weekly_click_summary,
        submission_timing_summary=submission_timing_summary,
        assessment_weight_summary=assessment_weight_summary,
    )
    insights_path = write_insights(
        score_range_summary=score_range_summary,
        raw_sum_click_summary=raw_sum_click_summary,
        student_click_summary=student_click_summary,
        weekly_click_summary=weekly_click_summary,
        submission_timing_summary=submission_timing_summary,
        submission_timing_by_module=submission_timing_by_module,
        assessment_weight_summary=assessment_weight_summary,
        assessment_weight_by_module=assessment_weight_by_module,
    )
    checklist_path = write_checklist()

    print(f"Wrote {len(table_paths)} tables to {TABLE_DIR.relative_to(ROOT_DIR)}")
    print(f"Wrote {len(figure_paths)} figures to {FIGURE_DIR.relative_to(ROOT_DIR)}")
    print(f"Wrote report: {report_path.relative_to(ROOT_DIR)}")
    print(f"Wrote insights: {insights_path.relative_to(ROOT_DIR)}")
    print(f"Wrote checklist: {checklist_path.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
