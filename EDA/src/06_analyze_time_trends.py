"""Analyze time patterns and trends for OULAD EDA."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


ROOT_DIR = Path(__file__).resolve().parents[2]
EDA_DATA_DIR = ROOT_DIR / "ETL" / "eda_data"
STAGING_DATA_DIR = ROOT_DIR / "ETL" / "staging_data"
EDA_DIR = ROOT_DIR / "EDA"
TABLE_DIR = EDA_DIR / "outputs" / "tables" / "06_time_trends"
FIGURE_DIR = EDA_DIR / "outputs" / "figures" / "06_time_trends"
DOC_DIR = EDA_DIR / "docs" / "06-time-trends"

STUDENT_SUMMARY = EDA_DATA_DIR / "eda_student_summary.csv"
WEEKLY_ACTIVITY = EDA_DATA_DIR / "eda_weekly_activity.csv"
ASSESSMENT_PROGRESS = EDA_DATA_DIR / "eda_assessment_progress.csv"
STUDENT_REGISTRATION = STAGING_DATA_DIR / "studentRegistration.csv"

FINAL_RESULT_ORDER = ["Distinction", "Pass", "Fail", "Withdrawn"]
STUDENT_KEYS = ["code_module", "code_presentation", "id_student"]
CHECKPOINT_DAYS = [14, 28, 42, 56]
ASSESSMENT_WINDOW_WEEKS = [-2, -1, 0, 1]


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


def table_link(path: Path) -> str:
    return path.relative_to(ROOT_DIR).as_posix()


def fmt_int(value: float | int) -> str:
    if pd.isna(value):
        return "n.a."
    return f"{int(round(value)):,}"


def fmt_float(value: float, digits: int = 1) -> str:
    if pd.isna(value):
        return "n.a."
    return f"{value:.{digits}f}"


def fmt_pct(value: float, digits: int = 1) -> str:
    if pd.isna(value):
        return "n.a."
    return f"{value * 100:.{digits}f}%"


def save_current_figure(filename: str) -> Path:
    path = FIGURE_DIR / filename
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()
    return path


def week_from_relative_day(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    return np.floor(numeric / 7).astype("Int64")


def prepare_inputs(
    student_summary: pd.DataFrame,
    weekly_activity: pd.DataFrame,
    assessment_progress: pd.DataFrame,
    student_registration: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    students = student_summary.copy()
    numeric_student_cols = [
        "total_click",
        "first_activity_date",
        "last_activity_date",
        "active_days",
        "active_weeks",
        "interacted_sites",
        "resource_types_used",
        "submitted_assessments",
        "submitted_records",
        "late_submissions",
        "avg_score",
        "submitted_weight_sum",
        "weighted_score",
    ]
    for column in numeric_student_cols:
        if column in students.columns:
            students[column] = pd.to_numeric(students[column], errors="coerce")
    students["final_result"] = pd.Categorical(
        students["final_result"], categories=FINAL_RESULT_ORDER, ordered=True
    )

    weekly = weekly_activity.copy()
    for column in ["study_week", "weekly_click", "active_days", "interacted_sites"]:
        weekly[column] = pd.to_numeric(weekly[column], errors="coerce")
    weekly = weekly.merge(
        students[STUDENT_KEYS + ["final_result"]],
        on=STUDENT_KEYS,
        how="left",
    )
    weekly["final_result"] = pd.Categorical(
        weekly["final_result"], categories=FINAL_RESULT_ORDER, ordered=True
    )
    weekly["study_day_start"] = weekly["study_week"] * 7

    assessments = assessment_progress.copy()
    for column in ["date", "date_submitted", "score", "weight"]:
        assessments[column] = pd.to_numeric(assessments[column], errors="coerce")
    assessments["assessment_week"] = week_from_relative_day(assessments["date"])
    assessments["submission_week"] = week_from_relative_day(assessments["date_submitted"])
    assessments = assessments.merge(
        students[STUDENT_KEYS + ["final_result"]],
        on=STUDENT_KEYS,
        how="left",
    )
    assessments["final_result"] = pd.Categorical(
        assessments["final_result"], categories=FINAL_RESULT_ORDER, ordered=True
    )

    registration = student_registration.copy()
    registration["date_registration"] = pd.to_numeric(
        registration["date_registration"], errors="coerce"
    )
    registration["date_unregistration"] = pd.to_numeric(
        registration["date_unregistration"], errors="coerce"
    )
    registration["registration_week"] = week_from_relative_day(registration["date_registration"])
    registration["unregistration_week"] = week_from_relative_day(
        registration["date_unregistration"]
    )
    registration = registration.merge(
        students[STUDENT_KEYS + ["final_result"]],
        on=STUDENT_KEYS,
        how="left",
    )
    registration["final_result"] = pd.Categorical(
        registration["final_result"], categories=FINAL_RESULT_ORDER, ordered=True
    )

    return students, weekly, assessments, registration


def summarize_weekly_overall(weekly: pd.DataFrame, student_count: int) -> pd.DataFrame:
    summary = (
        weekly.groupby("study_week")
        .agg(
            active_student_count=("id_student", "nunique"),
            weekly_click_sum=("weekly_click", "sum"),
            weekly_click_median=("weekly_click", "median"),
            weekly_click_mean=("weekly_click", "mean"),
            active_days_sum=("active_days", "sum"),
            active_days_median=("active_days", "median"),
            interacted_sites_median=("interacted_sites", "median"),
        )
        .reset_index()
        .sort_values("study_week")
    )
    summary["click_per_active_student"] = (
        summary["weekly_click_sum"] / summary["active_student_count"]
    )
    summary["active_student_pct"] = summary["active_student_count"] / student_count

    all_weeks = pd.DataFrame(
        {
            "study_week": range(
                int(summary["study_week"].min()), int(summary["study_week"].max()) + 1
            )
        }
    )
    summary = all_weeks.merge(summary, on="study_week", how="left")
    zero_cols = ["active_student_count", "weekly_click_sum", "active_days_sum"]
    summary[zero_cols] = summary[zero_cols].fillna(0)
    summary["click_per_active_student"] = np.where(
        summary["active_student_count"] > 0,
        summary["weekly_click_sum"] / summary["active_student_count"],
        np.nan,
    )
    summary["active_student_pct"] = summary["active_student_count"] / student_count
    return summary


def summarize_weekly_by_final_result(
    weekly: pd.DataFrame, students: pd.DataFrame
) -> pd.DataFrame:
    counts_by_result = students["final_result"].value_counts().reindex(FINAL_RESULT_ORDER)
    grouped = (
        weekly.groupby(["study_week", "final_result"], observed=False)
        .agg(
            active_student_count=("id_student", "nunique"),
            weekly_click_sum=("weekly_click", "sum"),
            weekly_click_median=("weekly_click", "median"),
            weekly_click_mean=("weekly_click", "mean"),
            active_days_sum=("active_days", "sum"),
            active_days_median=("active_days", "median"),
            interacted_sites_median=("interacted_sites", "median"),
        )
        .reset_index()
    )

    all_weeks = range(int(weekly["study_week"].min()), int(weekly["study_week"].max()) + 1)
    full_index = pd.MultiIndex.from_product(
        [all_weeks, FINAL_RESULT_ORDER], names=["study_week", "final_result"]
    )
    grouped = (
        grouped.set_index(["study_week", "final_result"])
        .reindex(full_index)
        .reset_index()
    )
    grouped["final_result"] = pd.Categorical(
        grouped["final_result"], categories=FINAL_RESULT_ORDER, ordered=True
    )
    zero_cols = ["active_student_count", "weekly_click_sum", "active_days_sum"]
    grouped[zero_cols] = grouped[zero_cols].fillna(0)
    grouped["total_students_in_result"] = (
        grouped["final_result"].astype(str).map(counts_by_result).astype(float)
    )
    grouped["active_student_pct"] = (
        grouped["active_student_count"] / grouped["total_students_in_result"]
    )
    grouped["click_per_active_student"] = np.where(
        grouped["active_student_count"] > 0,
        grouped["weekly_click_sum"] / grouped["active_student_count"],
        np.nan,
    )
    return grouped.sort_values(["study_week", "final_result"])


def summarize_weekly_by_module_presentation(weekly: pd.DataFrame) -> pd.DataFrame:
    summary = (
        weekly.groupby(["code_module", "code_presentation", "study_week"])
        .agg(
            active_student_count=("id_student", "nunique"),
            weekly_click_sum=("weekly_click", "sum"),
            weekly_click_median=("weekly_click", "median"),
            active_days_median=("active_days", "median"),
        )
        .reset_index()
        .sort_values(["code_module", "code_presentation", "study_week"])
    )
    summary["module_presentation"] = (
        summary["code_module"] + "-" + summary["code_presentation"]
    )
    summary["click_per_active_student"] = (
        summary["weekly_click_sum"] / summary["active_student_count"]
    )
    return summary


def summarize_assessment_schedule(assessments: pd.DataFrame) -> pd.DataFrame:
    schedule = (
        assessments[
            [
                "code_module",
                "code_presentation",
                "id_assessment",
                "assessment_type",
                "date",
                "assessment_week",
                "weight",
            ]
        ]
        .drop_duplicates()
        .dropna(subset=["date", "assessment_week"])
        .sort_values(["code_module", "code_presentation", "date", "id_assessment"])
    )
    schedule["assessment_week"] = schedule["assessment_week"].astype(int)
    return schedule


def build_assessment_window_activity(
    weekly: pd.DataFrame, assessment_schedule: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    weekly_mp_result = (
        weekly.groupby(["code_module", "code_presentation", "study_week", "final_result"])
        .agg(
            active_student_count=("id_student", "nunique"),
            weekly_click_sum=("weekly_click", "sum"),
            weekly_click_median=("weekly_click", "median"),
            active_days_median=("active_days", "median"),
        )
        .reset_index()
    )
    weekly_mp_result["click_per_active_student"] = np.where(
        weekly_mp_result["active_student_count"] > 0,
        weekly_mp_result["weekly_click_sum"] / weekly_mp_result["active_student_count"],
        np.nan,
    )

    rows: list[pd.DataFrame] = []
    for assessment in assessment_schedule.itertuples(index=False):
        for relative_week in ASSESSMENT_WINDOW_WEEKS:
            target_week = int(assessment.assessment_week) + relative_week
            mask = (
                (weekly_mp_result["code_module"] == assessment.code_module)
                & (weekly_mp_result["code_presentation"] == assessment.code_presentation)
                & (weekly_mp_result["study_week"] == target_week)
            )
            selected = weekly_mp_result.loc[mask].copy()
            if selected.empty:
                continue
            selected["id_assessment"] = assessment.id_assessment
            selected["assessment_type"] = assessment.assessment_type
            selected["assessment_date"] = assessment.date
            selected["assessment_week"] = assessment.assessment_week
            selected["assessment_weight"] = assessment.weight
            selected["relative_week_to_assessment"] = relative_week
            rows.append(selected)

    if rows:
        window = pd.concat(rows, ignore_index=True)
    else:
        window = pd.DataFrame(
            columns=[
                "code_module",
                "code_presentation",
                "study_week",
                "final_result",
                "active_student_count",
                "weekly_click_sum",
                "weekly_click_median",
                "active_days_median",
                "click_per_active_student",
                "id_assessment",
                "assessment_type",
                "assessment_date",
                "assessment_week",
                "assessment_weight",
                "relative_week_to_assessment",
            ]
        )

    summary = (
        window.groupby(["relative_week_to_assessment", "final_result"], observed=False)
        .agg(
            assessment_window_count=("id_assessment", "count"),
            active_student_count_mean=("active_student_count", "mean"),
            click_per_active_student_median=("click_per_active_student", "median"),
            weekly_click_sum_median=("weekly_click_sum", "median"),
            active_days_median=("active_days_median", "median"),
        )
        .reset_index()
        .sort_values(["relative_week_to_assessment", "final_result"])
    )
    return window, summary


def detect_trend_change_points(weekly_by_result: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for result in FINAL_RESULT_ORDER:
        group = weekly_by_result[
            (weekly_by_result["final_result"] == result)
            & (weekly_by_result["study_week"] >= 0)
            & (weekly_by_result["active_student_count"] > 0)
        ].copy()
        group = group.sort_values("study_week")
        if group.empty:
            continue

        group["click_per_active_smooth"] = (
            group["click_per_active_student"].rolling(3, min_periods=1).mean()
        )
        peak_idx = group["click_per_active_smooth"].idxmax()
        peak = group.loc[peak_idx]
        threshold = peak["click_per_active_smooth"] * 0.8
        after_peak = group[group["study_week"] > peak["study_week"]].copy()
        decline_candidates = after_peak[
            after_peak["click_per_active_smooth"] <= threshold
        ]
        if decline_candidates.empty:
            decline_week = np.nan
            decline_value = np.nan
        else:
            decline = decline_candidates.iloc[0]
            decline_week = decline["study_week"]
            decline_value = decline["click_per_active_smooth"]

        end = group.iloc[-1]
        first = group.iloc[0]
        rows.append(
            {
                "final_result": result,
                "start_week": int(first["study_week"]),
                "peak_week": int(peak["study_week"]),
                "peak_click_per_active_student_smooth": peak["click_per_active_smooth"],
                "first_week_below_80pct_of_peak_after_peak": decline_week,
                "click_per_active_student_at_decline_week": decline_value,
                "end_week": int(end["study_week"]),
                "end_click_per_active_student": end["click_per_active_student"],
                "start_active_student_count": first["active_student_count"],
                "peak_active_student_count": peak["active_student_count"],
                "end_active_student_count": end["active_student_count"],
                "end_active_student_pct_of_peak": (
                    end["active_student_count"] / peak["active_student_count"]
                    if peak["active_student_count"]
                    else np.nan
                ),
            }
        )
    return pd.DataFrame(rows)


def build_unregistration_timeline(
    registration: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    total_registrations = len(registration)
    unregistered = registration.dropna(subset=["unregistration_week"]).copy()
    unregistered["unregistration_week"] = unregistered["unregistration_week"].astype(int)
    timeline = (
        unregistered.groupby("unregistration_week")
        .agg(
            unregistration_count=("id_student", "size"),
            distinct_students=("id_student", "nunique"),
        )
        .reset_index()
        .sort_values("unregistration_week")
    )
    timeline["cumulative_unregistration_count"] = timeline[
        "unregistration_count"
    ].cumsum()
    timeline["cumulative_unregistration_pct"] = (
        timeline["cumulative_unregistration_count"] / total_registrations
    )

    by_module = (
        registration.groupby(["code_module", "code_presentation"])
        .agg(
            registration_count=("id_student", "size"),
            unregistration_count=("date_unregistration", lambda s: int(s.notna().sum())),
            median_unregistration_date=("date_unregistration", "median"),
        )
        .reset_index()
        .sort_values(["code_module", "code_presentation"])
    )
    by_module["unregistration_pct"] = (
        by_module["unregistration_count"] / by_module["registration_count"]
    )
    return timeline, by_module


def build_checkpoint_metrics(
    weekly: pd.DataFrame, students: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = students[STUDENT_KEYS + ["final_result"]].copy()
    rows_by_result: list[dict[str, object]] = []
    rows_overall: list[dict[str, object]] = []

    for checkpoint_day in CHECKPOINT_DAYS:
        checkpoint_week = checkpoint_day // 7
        observed = weekly[weekly["study_week"] <= checkpoint_week]
        cumulative = (
            observed.groupby(STUDENT_KEYS)
            .agg(
                cumulative_click=("weekly_click", "sum"),
                cumulative_active_weeks=("study_week", "nunique"),
                cumulative_active_days=("active_days", "sum"),
                cumulative_weekly_site_touches=("interacted_sites", "sum"),
            )
            .reset_index()
        )
        checkpoint = base.merge(cumulative, on=STUDENT_KEYS, how="left")
        fill_cols = [
            "cumulative_click",
            "cumulative_active_weeks",
            "cumulative_active_days",
            "cumulative_weekly_site_touches",
        ]
        checkpoint[fill_cols] = checkpoint[fill_cols].fillna(0)
        checkpoint["is_active_by_checkpoint"] = checkpoint["cumulative_click"] > 0

        rows_overall.append(
            {
                "checkpoint_day": checkpoint_day,
                "checkpoint_week": checkpoint_week,
                "student_count": len(checkpoint),
                "active_student_count": int(checkpoint["is_active_by_checkpoint"].sum()),
                "active_student_pct": checkpoint["is_active_by_checkpoint"].mean(),
                "median_cumulative_click": checkpoint["cumulative_click"].median(),
                "p75_cumulative_click": checkpoint["cumulative_click"].quantile(0.75),
                "median_cumulative_active_weeks": checkpoint[
                    "cumulative_active_weeks"
                ].median(),
                "median_cumulative_active_days": checkpoint[
                    "cumulative_active_days"
                ].median(),
            }
        )

        for result in FINAL_RESULT_ORDER:
            group = checkpoint[checkpoint["final_result"] == result]
            rows_by_result.append(
                {
                    "checkpoint_day": checkpoint_day,
                    "checkpoint_week": checkpoint_week,
                    "final_result": result,
                    "student_count": len(group),
                    "active_student_count": int(group["is_active_by_checkpoint"].sum()),
                    "active_student_pct": (
                        group["is_active_by_checkpoint"].mean() if len(group) else np.nan
                    ),
                    "median_cumulative_click": group["cumulative_click"].median(),
                    "p75_cumulative_click": group["cumulative_click"].quantile(0.75),
                    "median_cumulative_active_weeks": group[
                        "cumulative_active_weeks"
                    ].median(),
                    "median_cumulative_active_days": group[
                        "cumulative_active_days"
                    ].median(),
                }
            )

    return pd.DataFrame(rows_by_result), pd.DataFrame(rows_overall)


def plot_weekly_total_click(weekly_overall: pd.DataFrame) -> Path:
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=weekly_overall, x="study_week", y="weekly_click_sum", marker="o")
    plt.title("Tổng click VLE theo tuần học")
    plt.xlabel("study_week")
    plt.ylabel("Tổng weekly_click")
    return save_current_figure("weekly_total_click_line.png")


def plot_weekly_active_students(weekly_overall: pd.DataFrame) -> Path:
    plt.figure(figsize=(10, 5))
    sns.lineplot(
        data=weekly_overall, x="study_week", y="active_student_count", marker="o"
    )
    plt.title("Số sinh viên active VLE theo tuần học")
    plt.xlabel("study_week")
    plt.ylabel("Số sinh viên active")
    return save_current_figure("weekly_active_students_line.png")


def plot_weekly_click_by_result(weekly_by_result: pd.DataFrame) -> Path:
    plot_data = weekly_by_result[weekly_by_result["active_student_count"] >= 30].copy()
    plt.figure(figsize=(11, 6))
    sns.lineplot(
        data=plot_data,
        x="study_week",
        y="click_per_active_student",
        hue="final_result",
        hue_order=FINAL_RESULT_ORDER,
        marker="o",
    )
    plt.title("Click trung bình trên sinh viên active theo final_result")
    plt.xlabel("study_week")
    plt.ylabel("Click / sinh viên active (tuần có >= 30 sinh viên active)")
    plt.legend(title="final_result")
    return save_current_figure("weekly_click_per_active_by_final_result_line.png")


def plot_weekly_active_rate_by_result(weekly_by_result: pd.DataFrame) -> Path:
    plt.figure(figsize=(11, 6))
    sns.lineplot(
        data=weekly_by_result,
        x="study_week",
        y="active_student_pct",
        hue="final_result",
        hue_order=FINAL_RESULT_ORDER,
        marker="o",
    )
    plt.title("Tỷ lệ sinh viên active theo tuần và final_result")
    plt.xlabel("study_week")
    plt.ylabel("Tỷ lệ active trong nhóm")
    plt.legend(title="final_result")
    return save_current_figure("weekly_active_rate_by_final_result_line.png")


def plot_weekly_click_share_area(weekly_by_result: pd.DataFrame) -> Path:
    pivot = (
        weekly_by_result.pivot_table(
            index="study_week",
            columns="final_result",
            values="weekly_click_sum",
            aggfunc="sum",
            observed=False,
        )
        .reindex(columns=FINAL_RESULT_ORDER)
        .fillna(0)
    )
    share = pivot.div(pivot.sum(axis=1), axis=0).fillna(0)
    ax = share.plot.area(
        figsize=(11, 6),
        color=["#4C78A8", "#54A24B", "#F58518", "#E45756"],
        linewidth=0,
    )
    ax.set_title("Tỷ trọng weekly_click theo final_result")
    ax.set_xlabel("study_week")
    ax.set_ylabel("Tỷ trọng click")
    ax.legend(title="final_result", bbox_to_anchor=(1.02, 1), loc="upper left")
    return save_current_figure("weekly_click_share_by_final_result_area.png")


def plot_module_week_heatmap(weekly_by_module: pd.DataFrame) -> Path:
    pivot = weekly_by_module.pivot_table(
        index="module_presentation",
        columns="study_week",
        values="click_per_active_student",
        aggfunc="mean",
    ).fillna(0)
    plt.figure(figsize=(14, 7))
    sns.heatmap(
        np.log1p(pivot),
        cmap="viridis",
        linewidths=0.1,
        cbar_kws={"label": "log1p(click / active student)"},
    )
    plt.title("Cường độ click theo tuần và module-presentation")
    plt.xlabel("study_week")
    plt.ylabel("module-presentation")
    return save_current_figure("module_presentation_weekly_click_heatmap.png")


def plot_assessment_window(assessment_window_summary: pd.DataFrame) -> Path:
    plt.figure(figsize=(9, 5))
    sns.lineplot(
        data=assessment_window_summary,
        x="relative_week_to_assessment",
        y="click_per_active_student_median",
        hue="final_result",
        hue_order=FINAL_RESULT_ORDER,
        marker="o",
    )
    plt.axvline(0, color="#444444", linestyle="--", linewidth=1)
    plt.title("Click quanh tuần có assessment deadline")
    plt.xlabel("Tuần tương đối so với deadline assessment")
    plt.ylabel("Median click / sinh viên active")
    plt.legend(title="final_result")
    return save_current_figure("assessment_window_click_by_final_result_line.png")


def plot_unregistration_timeline(unregistration_timeline: pd.DataFrame) -> Path:
    plt.figure(figsize=(10, 5))
    sns.lineplot(
        data=unregistration_timeline,
        x="unregistration_week",
        y="cumulative_unregistration_pct",
        marker="o",
    )
    plt.axvline(0, color="#444444", linestyle="--", linewidth=1)
    plt.title("Tỷ lệ hủy đăng ký tích lũy theo tuần tương đối")
    plt.xlabel("unregistration_week")
    plt.ylabel("Tỷ lệ hủy đăng ký tích lũy")
    return save_current_figure("cumulative_unregistration_timeline.png")


def plot_checkpoint_active_rate(checkpoint_by_result: pd.DataFrame) -> Path:
    plt.figure(figsize=(9, 5))
    sns.lineplot(
        data=checkpoint_by_result,
        x="checkpoint_day",
        y="active_student_pct",
        hue="final_result",
        hue_order=FINAL_RESULT_ORDER,
        marker="o",
    )
    plt.title("Tỷ lệ đã active VLE tại các checkpoint")
    plt.xlabel("Checkpoint day")
    plt.ylabel("Tỷ lệ active lũy kế")
    plt.legend(title="final_result")
    return save_current_figure("checkpoint_active_rate_by_final_result_line.png")


def plot_figures(
    weekly_overall: pd.DataFrame,
    weekly_by_result: pd.DataFrame,
    weekly_by_module: pd.DataFrame,
    assessment_window_summary: pd.DataFrame,
    unregistration_timeline: pd.DataFrame,
    checkpoint_by_result: pd.DataFrame,
) -> list[Path]:
    return [
        plot_weekly_total_click(weekly_overall),
        plot_weekly_active_students(weekly_overall),
        plot_weekly_click_by_result(weekly_by_result),
        plot_weekly_active_rate_by_result(weekly_by_result),
        plot_weekly_click_share_area(weekly_by_result),
        plot_module_week_heatmap(weekly_by_module),
        plot_assessment_window(assessment_window_summary),
        plot_unregistration_timeline(unregistration_timeline),
        plot_checkpoint_active_rate(checkpoint_by_result),
    ]


def write_report(
    table_paths: dict[str, Path],
    figure_paths: list[Path],
    weekly_overall: pd.DataFrame,
    weekly_by_result: pd.DataFrame,
    trend_change_points: pd.DataFrame,
    unregistration_timeline: pd.DataFrame,
    checkpoint_by_result: pd.DataFrame,
    assessment_window_summary: pd.DataFrame,
) -> Path:
    table_lines = "\n".join(
        f"- `{table_link(path)}`" for path in sorted(table_paths.values(), key=lambda p: p.name)
    )
    figure_lines = "\n".join(
        f"- `{table_link(path)}`" for path in sorted(figure_paths, key=lambda p: p.name)
    )

    peak_click = weekly_overall.sort_values("weekly_click_sum", ascending=False).iloc[0]
    peak_active = weekly_overall.sort_values(
        "active_student_count", ascending=False
    ).iloc[0]
    week_min = int(weekly_overall["study_week"].min())
    week_max = int(weekly_overall["study_week"].max())

    withdrawn_decline = trend_change_points[
        trend_change_points["final_result"] == "Withdrawn"
    ].iloc[0]
    pass_decline = trend_change_points[trend_change_points["final_result"] == "Pass"].iloc[0]

    total_unregistration = int(unregistration_timeline["unregistration_count"].sum())
    by_week0 = unregistration_timeline[
        unregistration_timeline["unregistration_week"] <= 0
    ]
    cumulative_by_week0 = (
        by_week0["cumulative_unregistration_count"].iloc[-1] if len(by_week0) else 0
    )
    cumulative_pct_by_week0 = (
        by_week0["cumulative_unregistration_pct"].iloc[-1] if len(by_week0) else 0
    )

    checkpoint_14 = checkpoint_by_result[
        (checkpoint_by_result["checkpoint_day"] == 14)
        & (checkpoint_by_result["final_result"] == "Withdrawn")
    ].iloc[0]
    checkpoint_56_pass = checkpoint_by_result[
        (checkpoint_by_result["checkpoint_day"] == 56)
        & (checkpoint_by_result["final_result"] == "Pass")
    ].iloc[0]

    assessment_before = assessment_window_summary[
        assessment_window_summary["relative_week_to_assessment"] == -1
    ]
    assessment_week = assessment_window_summary[
        assessment_window_summary["relative_week_to_assessment"] == 0
    ]
    before_pass = assessment_before[assessment_before["final_result"] == "Pass"].iloc[0]
    week_pass = assessment_week[assessment_week["final_result"] == "Pass"].iloc[0]

    report = f"""# Báo Cáo EDA - Phân Tích Mẫu Và Xu Hướng Theo Thời Gian

## 1. Phạm vi

Phần này phân tích hành vi học tập theo tiến trình thời gian tương đối của OULAD. Các cột ngày trong OULAD là ngày tương đối, không phải ngày lịch thật. Đơn vị thời gian chính là `study_week` trong `eda_weekly_activity`.

Nguồn dữ liệu:

- `ETL/eda_data/eda_student_summary.csv`
- `ETL/eda_data/eda_weekly_activity.csv`
- `ETL/eda_data/eda_assessment_progress.csv`
- `ETL/staging_data/studentRegistration.csv`

## 2. Lưu ý phương pháp

- `study_week` chạy từ tuần {week_min} đến tuần {week_max}. Tuần âm là hoạt động trước mốc bắt đầu khóa học.
- Sinh viên active trong một tuần là sinh viên có bản ghi VLE ở tuần đó.
- Các checkpoint 14, 28, 42 và 56 ngày chỉ dùng dữ liệu có `study_week <= checkpoint_day / 7`.
- Biểu đồ click / sinh viên active theo `final_result` chỉ hiển thị các điểm có ít nhất 30 sinh viên active để tránh nhiễu ở cuối kỳ khi mẫu quá nhỏ. Bảng CSV vẫn giữ đầy đủ các tuần.
- Nếu sau này chọn bài toán dự báo sớm, không được dùng dữ liệu phát sinh sau checkpoint.

## 3. Nhận xét chính

- Tổng `weekly_click` cao nhất ở tuần {fmt_int(peak_click["study_week"])} với {fmt_int(peak_click["weekly_click_sum"])} click.
- Số sinh viên active cao nhất ở tuần {fmt_int(peak_active["study_week"])} với {fmt_int(peak_active["active_student_count"])} sinh viên.
- Nhóm `Withdrawn` có tuần đầu tiên sau peak rơi dưới 80% cường độ click peak ở tuần {fmt_int(withdrawn_decline["first_week_below_80pct_of_peak_after_peak"])}.
- Nhóm `Pass` có tuần đầu tiên sau peak rơi dưới 80% cường độ click peak ở tuần {fmt_int(pass_decline["first_week_below_80pct_of_peak_after_peak"])}.
- Tổng số bản ghi có `date_unregistration`: {fmt_int(total_unregistration)}.
- Đến hết tuần 0, đã có {fmt_int(cumulative_by_week0)} lượt hủy đăng ký, chiếm {fmt_pct(cumulative_pct_by_week0)} tổng đăng ký.
- Ở checkpoint ngày 14, tỷ lệ sinh viên nhóm `Withdrawn` đã active VLE là {fmt_pct(checkpoint_14["active_student_pct"])}.
- Ở checkpoint ngày 56, tỷ lệ sinh viên nhóm `Pass` đã active VLE là {fmt_pct(checkpoint_56_pass["active_student_pct"])}.
- Với nhóm `Pass`, median click / sinh viên active quanh assessment tăng từ {fmt_float(before_pass["click_per_active_student_median"])} ở tuần -1 lên {fmt_float(week_pass["click_per_active_student_median"])} ở tuần deadline.

Đọc diễn giải chi tiết tại [06_time_trends_insights.md](06_time_trends_insights.md).

## 4. Các phân tích đã hoàn thành

- Tổng hợp `sum_click` theo tuần học.
- Theo dõi số sinh viên active qua từng tuần.
- Phân tích xu hướng tương tác trước và quanh các mốc assessment.
- So sánh xu hướng VLE giữa các nhóm `Distinction`, `Pass`, `Fail`, `Withdrawn`.
- Phát hiện giai đoạn cường độ tương tác bắt đầu giảm sau peak.
- Phân tích tỷ lệ hủy đăng ký theo thời gian tương đối.
- Tạo checkpoint ngày 14, 28, 42 và 56 ở mức thống kê EDA.

## 5. Bảng đầu ra

{table_lines}

## 6. Biểu đồ đầu ra

{figure_lines}

## 7. Khuyến nghị dùng kết quả

- Dùng phần này để chọn checkpoint hợp lý nếu nhóm chuyển sang bài toán cảnh báo sớm.
- Khi làm dashboard, nên có filter theo `final_result`, `code_module`, `code_presentation` và `study_week`.
- Không dùng toàn bộ thời gian của môn học cho bài toán dự báo sớm.
- Nên nối phần này với phân tích tương quan: biến nào tương quan mạnh cần kiểm tra thêm thời điểm tín hiệu bắt đầu xuất hiện.
"""
    path = DOC_DIR / "06_time_trends_report.md"
    path.write_text(report, encoding="utf-8")
    return path


def write_insights(
    weekly_overall: pd.DataFrame,
    weekly_by_result: pd.DataFrame,
    trend_change_points: pd.DataFrame,
    unregistration_timeline: pd.DataFrame,
    checkpoint_by_result: pd.DataFrame,
    assessment_window_summary: pd.DataFrame,
) -> Path:
    peak_click = weekly_overall.sort_values("weekly_click_sum", ascending=False).iloc[0]
    peak_active = weekly_overall.sort_values(
        "active_student_count", ascending=False
    ).iloc[0]
    withdrawn_trend = trend_change_points[
        trend_change_points["final_result"] == "Withdrawn"
    ].iloc[0]
    distinction_trend = trend_change_points[
        trend_change_points["final_result"] == "Distinction"
    ].iloc[0]

    week0 = unregistration_timeline[
        unregistration_timeline["unregistration_week"] <= 0
    ]
    week4 = unregistration_timeline[
        unregistration_timeline["unregistration_week"] <= 4
    ]
    cumulative_week0 = week0["cumulative_unregistration_pct"].iloc[-1] if len(week0) else 0
    cumulative_week4 = week4["cumulative_unregistration_pct"].iloc[-1] if len(week4) else 0

    cp14 = checkpoint_by_result[checkpoint_by_result["checkpoint_day"] == 14]
    cp56 = checkpoint_by_result[checkpoint_by_result["checkpoint_day"] == 56]
    cp14_distinction = cp14[cp14["final_result"] == "Distinction"].iloc[0]
    cp14_withdrawn = cp14[cp14["final_result"] == "Withdrawn"].iloc[0]
    cp56_pass = cp56[cp56["final_result"] == "Pass"].iloc[0]
    cp56_fail = cp56[cp56["final_result"] == "Fail"].iloc[0]

    assessment_week = assessment_window_summary[
        assessment_window_summary["relative_week_to_assessment"] == 0
    ]
    pass_deadline = assessment_week[assessment_week["final_result"] == "Pass"].iloc[0]
    withdrawn_deadline = assessment_week[
        assessment_week["final_result"] == "Withdrawn"
    ].iloc[0]

    insights = f"""# EDA Insights - Phân Tích Mẫu Và Xu Hướng Theo Thời Gian

## Cách đọc nhanh

File report chính cho biết đã sinh bảng và biểu đồ nào. File này giải thích xu hướng theo thời gian đang nói gì, vì sao đáng chú ý và nên dùng thế nào nếu nhóm chuyển sang dashboard hoặc cảnh báo sớm.

## 1. Nhịp tương tác VLE không đều trong suốt môn học

Quan sát:

- Tổng click cao nhất ở tuần {fmt_int(peak_click["study_week"])} với {fmt_int(peak_click["weekly_click_sum"])} click.
- Số sinh viên active cao nhất ở tuần {fmt_int(peak_active["study_week"])} với {fmt_int(peak_active["active_student_count"])} sinh viên.

Diễn giải:

- Hành vi VLE có nhịp rõ theo tuần, không phân bổ đều trong toàn khóa.
- Peak tổng click và peak số sinh viên active không nhất thiết là cùng một tuần. Một tuần có nhiều sinh viên active chưa chắc có cường độ click cao nhất trên mỗi sinh viên.

Ý nghĩa với phân tích sau:

- Không nên chỉ dùng tổng click toàn kỳ nếu muốn hiểu quá trình học.
- Dashboard nên có line chart theo tuần và filter module-presentation.

## 2. Nhóm kết quả cuối có nhịp học khác nhau

Quan sát:

- Nhóm `Withdrawn` rơi dưới 80% cường độ click peak sau peak ở tuần {fmt_int(withdrawn_trend["first_week_below_80pct_of_peak_after_peak"])}.
- Nhóm `Distinction` rơi dưới 80% cường độ click peak sau peak ở tuần {fmt_int(distinction_trend["first_week_below_80pct_of_peak_after_peak"])}.

Diễn giải:

- Nhóm `Withdrawn` thường mất tương tác sớm hơn và duy trì active rate thấp hơn. Đây là tín hiệu thời gian quan trọng hơn việc chỉ biết tổng click cả kỳ thấp.
- Nhóm kết quả tốt có xu hướng duy trì active dài hơn, nhưng vẫn cần đọc theo module-presentation vì cấu trúc môn học khác nhau.

Ý nghĩa với phân tích sau:

- Nếu chọn bài toán cảnh báo sớm, active rate và click theo tuần là biến nên ưu tiên.
- Cần kiểm tra từ tuần nào tín hiệu đủ rõ để cảnh báo mà không quá muộn.

## 3. Assessment tạo nhịp tương tác quanh deadline

Quan sát:

- Ở tuần deadline assessment, median click / sinh viên active của nhóm `Pass` là {fmt_float(pass_deadline["click_per_active_student_median"])}.
- Ở tuần deadline assessment, median click / sinh viên active của nhóm `Withdrawn` là {fmt_float(withdrawn_deadline["click_per_active_student_median"])}.

Diễn giải:

- Tương tác quanh assessment phản ánh nhịp làm bài, ôn tập hoặc truy cập tài nguyên đúng hạn.
- Nhóm `Withdrawn` có thể không còn xuất hiện quanh nhiều deadline, nên số click thấp vừa phản ánh cường độ thấp vừa phản ánh việc đã rời khỏi môn.

Ý nghĩa với phân tích sau:

- Phân tích quanh assessment nên tách rõ số sinh viên còn active và click trên sinh viên active.
- Nếu dự báo sớm, chỉ dùng assessment đã xảy ra trước checkpoint.

## 4. Hủy đăng ký xuất hiện cả trước và sau mốc bắt đầu khóa học

Quan sát:

- Đến hết tuần 0, tỷ lệ hủy đăng ký tích lũy là {fmt_pct(cumulative_week0)}.
- Đến hết tuần 4, tỷ lệ hủy đăng ký tích lũy là {fmt_pct(cumulative_week4)}.

Diễn giải:

- Một phần sinh viên hủy đăng ký rất sớm, thậm chí trước hoặc ngay quanh mốc bắt đầu khóa học.
- `date_unregistration` bị thiếu không nên xem là lỗi. Với OULAD, thiếu thường nghĩa là sinh viên không hủy đăng ký.

Ý nghĩa với phân tích sau:

- Với dashboard vận hành, nên theo dõi cumulative unregistration theo tuần.
- Với mô hình dự báo `Withdrawn`, cần chú ý không dùng `date_unregistration` như feature nếu thời điểm dự báo chưa đến ngày đó.

## 5. Checkpoint cho thấy khả năng quan sát sớm

Quan sát:

- Ngày 14, tỷ lệ đã active của `Distinction` là {fmt_pct(cp14_distinction["active_student_pct"])}.
- Ngày 14, tỷ lệ đã active của `Withdrawn` là {fmt_pct(cp14_withdrawn["active_student_pct"])}.
- Ngày 56, tỷ lệ đã active của `Pass` là {fmt_pct(cp56_pass["active_student_pct"])}.
- Ngày 56, tỷ lệ đã active của `Fail` là {fmt_pct(cp56_fail["active_student_pct"])}.

Diễn giải:

- Checkpoint sớm đã có tín hiệu khác biệt giữa các nhóm, nhưng chưa đủ để kết luận cá nhân.
- Checkpoint càng muộn càng có nhiều thông tin hơn, nhưng cũng giảm giá trị cảnh báo sớm.

Ý nghĩa với phân tích sau:

- Nếu nhóm chọn cảnh báo sớm, nên thử nhiều checkpoint và so sánh trade-off giữa độ sớm và độ đầy đủ thông tin.
- Nếu chỉ làm dashboard mô tả, checkpoint vẫn hữu ích để tạo các mốc theo dõi cố định.

## 6. Kết luận cho bước tiếp theo

- Phần thời gian bổ sung điều mà phân tích tương quan chưa trả lời: tín hiệu xuất hiện ở tuần nào.
- Các biến `weekly_click`, `active_student_pct`, `click_per_active_student`, hoạt động quanh assessment và cumulative checkpoint nên được giữ lại cho phân tích sâu hơn.
- Chưa nên chốt bài toán dự báo chỉ từ EDA này. Kết quả hiện tại phù hợp để nhóm chọn hướng: dashboard tiến trình học, cảnh báo rút môn, hoặc phân tích hành vi quanh assessment.
"""
    path = DOC_DIR / "06_time_trends_insights.md"
    path.write_text(insights, encoding="utf-8")
    return path


def write_checklist() -> Path:
    checklist = """# Checklist EDA - Phân Tích Mẫu Và Xu Hướng Theo Thời Gian

- [x] Tổng hợp `sum_click` theo tuần học.
- [x] Theo dõi số sinh viên còn hoạt động qua từng tuần.
- [x] Phân tích xu hướng tương tác trước các mốc assessment.
- [x] So sánh xu hướng VLE giữa các nhóm kết quả cuối.
- [x] Phát hiện giai đoạn sinh viên bắt đầu giảm tương tác.
- [x] Phân tích tỷ lệ hủy đăng ký theo thời gian.
- [x] Tạo checkpoint ngày 14, 28, 42 và 56 ở mức thống kê EDA.
- [x] Ghi chú rõ rủi ro leakage nếu dùng cho dự báo sớm.

Minh chứng:

- Script: `EDA/src/06_analyze_time_trends.py`
- Report: `EDA/docs/06-time-trends/06_time_trends_report.md`
- Insights: `EDA/docs/06-time-trends/06_time_trends_insights.md`
- Tables: `EDA/outputs/tables/06_time_trends/`
- Figures: `EDA/outputs/figures/06_time_trends/`
"""
    path = DOC_DIR / "06_time_trends_checklist.md"
    path.write_text(checklist, encoding="utf-8")
    return path


def main() -> None:
    ensure_output_dirs()
    sns.set_theme(style="whitegrid", context="notebook")

    student_summary = read_csv(STUDENT_SUMMARY)
    weekly_activity = read_csv(WEEKLY_ACTIVITY)
    assessment_progress = read_csv(ASSESSMENT_PROGRESS)
    student_registration = read_csv(STUDENT_REGISTRATION)

    students, weekly, assessments, registration = prepare_inputs(
        student_summary,
        weekly_activity,
        assessment_progress,
        student_registration,
    )

    weekly_overall = summarize_weekly_overall(weekly, len(students))
    weekly_by_result = summarize_weekly_by_final_result(weekly, students)
    weekly_by_module = summarize_weekly_by_module_presentation(weekly)
    assessment_schedule = summarize_assessment_schedule(assessments)
    assessment_window, assessment_window_summary = build_assessment_window_activity(
        weekly, assessment_schedule
    )
    trend_change_points = detect_trend_change_points(weekly_by_result)
    unregistration_timeline, unregistration_by_module = build_unregistration_timeline(
        registration
    )
    checkpoint_by_result, checkpoint_overall = build_checkpoint_metrics(weekly, students)

    table_paths = {
        "weekly_overall_trends": write_table(
            weekly_overall, "weekly_overall_trends.csv"
        ),
        "weekly_trends_by_final_result": write_table(
            weekly_by_result, "weekly_trends_by_final_result.csv"
        ),
        "weekly_trends_by_module_presentation": write_table(
            weekly_by_module, "weekly_trends_by_module_presentation.csv"
        ),
        "assessment_schedule_by_week": write_table(
            assessment_schedule, "assessment_schedule_by_week.csv"
        ),
        "assessment_window_activity_by_result": write_table(
            assessment_window, "assessment_window_activity_by_result.csv"
        ),
        "assessment_window_summary": write_table(
            assessment_window_summary, "assessment_window_summary.csv"
        ),
        "trend_change_points_by_final_result": write_table(
            trend_change_points, "trend_change_points_by_final_result.csv"
        ),
        "unregistration_timeline": write_table(
            unregistration_timeline, "unregistration_timeline.csv"
        ),
        "unregistration_by_module_presentation": write_table(
            unregistration_by_module, "unregistration_by_module_presentation.csv"
        ),
        "checkpoint_metrics_by_final_result": write_table(
            checkpoint_by_result, "checkpoint_metrics_by_final_result.csv"
        ),
        "checkpoint_overall_metrics": write_table(
            checkpoint_overall, "checkpoint_overall_metrics.csv"
        ),
    }

    figure_paths = plot_figures(
        weekly_overall,
        weekly_by_result,
        weekly_by_module,
        assessment_window_summary,
        unregistration_timeline,
        checkpoint_by_result,
    )

    report_path = write_report(
        table_paths,
        figure_paths,
        weekly_overall,
        weekly_by_result,
        trend_change_points,
        unregistration_timeline,
        checkpoint_by_result,
        assessment_window_summary,
    )
    insights_path = write_insights(
        weekly_overall,
        weekly_by_result,
        trend_change_points,
        unregistration_timeline,
        checkpoint_by_result,
        assessment_window_summary,
    )
    checklist_path = write_checklist()

    print(f"Wrote {len(table_paths)} tables to {TABLE_DIR.relative_to(ROOT_DIR)}")
    print(f"Wrote {len(figure_paths)} figures to {FIGURE_DIR.relative_to(ROOT_DIR)}")
    print(f"Wrote report: {report_path.relative_to(ROOT_DIR)}")
    print(f"Wrote insights: {insights_path.relative_to(ROOT_DIR)}")
    print(f"Wrote checklist: {checklist_path.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
