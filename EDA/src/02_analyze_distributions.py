"""Analyze distribution patterns for OULAD EDA.

This script reads the EDA-ready outputs from ETL plus the staging VLE mapping
needed for activity_type, then writes summary tables, figures, and a Markdown
report for the "Phan bo du lieu" EDA task.
"""

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
EDA_DATA_DIR = ROOT_DIR / "ETL" / "eda_data"
STAGING_DATA_DIR = ROOT_DIR / "ETL" / "staging_data"
EDA_DIR = ROOT_DIR / "EDA"
TABLE_DIR = EDA_DIR / "outputs" / "tables" / "02_distribution"
FIGURE_DIR = EDA_DIR / "outputs" / "figures" / "02_distribution"
DOC_DIR = EDA_DIR / "docs" / "02-distribution"

STUDENT_SUMMARY = EDA_DATA_DIR / "eda_student_summary.csv"
WEEKLY_ACTIVITY = EDA_DATA_DIR / "eda_weekly_activity.csv"
ASSESSMENT_PROGRESS = EDA_DATA_DIR / "eda_assessment_progress.csv"
STAGING_ASSESSMENTS = STAGING_DATA_DIR / "assessments.csv"
STAGING_VLE = STAGING_DATA_DIR / "vle.csv"
STAGING_STUDENT_VLE = STAGING_DATA_DIR / "studentVle.csv"

FINAL_RESULT_ORDER = ["Distinction", "Pass", "Fail", "Withdrawn"]
DEMOGRAPHIC_COLUMNS = [
    "gender",
    "region",
    "highest_education",
    "imd_band",
    "age_band",
    "disability",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create EDA distribution tables, figures, and report."
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1_000_000,
        help="Rows per chunk when reading staging studentVle for activity_type.",
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


def value_distribution(series: pd.Series, value_name: str) -> pd.DataFrame:
    prepared = series.astype("object").where(series.notna(), "(missing)").astype(str)
    counts = prepared.value_counts(dropna=False).rename_axis(value_name).reset_index(name="count")
    counts["pct"] = counts["count"] / counts["count"].sum()
    return counts


def numeric_summary(series: pd.Series, metric: str) -> pd.DataFrame:
    numeric = pd.to_numeric(series, errors="coerce")
    non_missing = numeric.dropna()
    quantiles = non_missing.quantile([0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99])
    return pd.DataFrame(
        [
            {
                "metric": metric,
                "count": int(non_missing.count()),
                "missing": int(numeric.isna().sum()),
                "zero_count": int((non_missing == 0).sum()),
                "negative_count": int((non_missing < 0).sum()),
                "min": non_missing.min(),
                "p01": quantiles.loc[0.01],
                "p05": quantiles.loc[0.05],
                "p25": quantiles.loc[0.25],
                "median": quantiles.loc[0.5],
                "mean": non_missing.mean(),
                "p75": quantiles.loc[0.75],
                "p95": quantiles.loc[0.95],
                "p99": quantiles.loc[0.99],
                "max": non_missing.max(),
                "std": non_missing.std(),
            }
        ]
    )


def add_pct(df: pd.DataFrame, count_col: str, pct_col: str = "pct") -> pd.DataFrame:
    df = df.copy()
    total = df[count_col].sum()
    df[pct_col] = df[count_col] / total if total else 0
    return df


def save_current_figure(filename: str) -> Path:
    path = FIGURE_DIR / filename
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()
    return path


def plot_bar(
    df: pd.DataFrame,
    x: str,
    y: str,
    filename: str,
    title: str,
    xlabel: str,
    ylabel: str,
    order: list[str] | None = None,
    rotation: int = 0,
) -> Path:
    plt.figure(figsize=(9, 5))
    sns.barplot(data=df, x=x, y=y, order=order, color="#4C78A8")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=rotation, ha="right" if rotation else "center")
    return save_current_figure(filename)


def plot_hist(
    series: pd.Series,
    filename: str,
    title: str,
    xlabel: str,
    bins: int = 40,
    log1p: bool = False,
) -> Path:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if log1p:
        numeric = numeric.clip(lower=0).map(math.log1p)
    plt.figure(figsize=(9, 5))
    sns.histplot(numeric, bins=bins, color="#72B7B2")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Số quan sát")
    return save_current_figure(filename)


def plot_final_result_by_module_presentation(df: pd.DataFrame) -> Path:
    pivot = (
        df.pivot_table(
            index=["code_module", "code_presentation"],
            columns="final_result",
            values="id_student",
            aggfunc="count",
            fill_value=0,
        )
        .reindex(columns=FINAL_RESULT_ORDER, fill_value=0)
        .sort_index()
    )
    pct = pivot.div(pivot.sum(axis=1), axis=0).fillna(0)
    labels = [f"{module}-{presentation}" for module, presentation in pct.index]

    plt.figure(figsize=(14, 6))
    bottom = pd.Series([0.0] * len(pct), index=pct.index)
    colors = {
        "Distinction": "#54A24B",
        "Pass": "#4C78A8",
        "Fail": "#E45756",
        "Withdrawn": "#F58518",
    }
    for result in FINAL_RESULT_ORDER:
        values = pct[result]
        plt.bar(labels, values, bottom=bottom, label=result, color=colors[result])
        bottom += values
    plt.title("Tỷ lệ final_result theo module-presentation")
    plt.xlabel("Module-presentation")
    plt.ylabel("Tỷ lệ")
    plt.xticks(rotation=60, ha="right")
    plt.ylim(0, 1)
    plt.legend(title="final_result", loc="upper left", bbox_to_anchor=(1.01, 1.0))
    return save_current_figure("final_result_by_module_presentation.png")


def plot_final_result_heatmap_by_module_presentation(df: pd.DataFrame) -> Path:
    pivot = (
        df.pivot_table(
            index=["code_module", "code_presentation"],
            columns="final_result",
            values="id_student",
            aggfunc="count",
            fill_value=0,
        )
        .reindex(columns=FINAL_RESULT_ORDER, fill_value=0)
        .sort_index()
    )
    pct = pivot.div(pivot.sum(axis=1), axis=0).fillna(0)
    pct.index = [f"{module}-{presentation}" for module, presentation in pct.index]

    plt.figure(figsize=(8, max(6, len(pct) * 0.34)))
    sns.heatmap(
        pct,
        cmap="YlGnBu",
        annot=True,
        fmt=".0%",
        linewidths=0.5,
        cbar_kws={"label": "Tỷ lệ"},
    )
    plt.title("Heatmap tỷ lệ final_result theo module-presentation")
    plt.xlabel("final_result")
    plt.ylabel("Module-presentation")
    return save_current_figure("final_result_heatmap_by_module_presentation.png")


def plot_demographics(student_summary: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(3, 2, figsize=(15, 13))
    axes = axes.flatten()
    for axis, column in zip(axes, DEMOGRAPHIC_COLUMNS):
        counts = value_distribution(student_summary[column], column).head(15)
        sns.barplot(data=counts, y=column, x="count", ax=axis, color="#B279A2")
        axis.set_title(column)
        axis.set_xlabel("Số bản ghi student-module-presentation")
        axis.set_ylabel("")
    fig.suptitle("Phân bố thông tin nền của sinh viên", y=1.01)
    return save_current_figure("student_background_distributions.png")


def plot_box(
    series: pd.Series,
    filename: str,
    title: str,
    ylabel: str,
    log1p: bool = False,
) -> Path:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if log1p:
        numeric = numeric.clip(lower=0).map(math.log1p)
    plt.figure(figsize=(7, 5))
    sns.boxplot(y=numeric, color="#72B7B2")
    plt.title(title)
    plt.ylabel(ylabel)
    return save_current_figure(filename)


def plot_score_by_final_result(assessment_progress: pd.DataFrame, student_summary: pd.DataFrame) -> Path:
    score_with_result = assessment_progress.merge(
        student_summary[["code_module", "code_presentation", "id_student", "final_result"]],
        on=["code_module", "code_presentation", "id_student"],
        how="left",
    )
    plt.figure(figsize=(9, 5))
    sns.boxplot(
        data=score_with_result,
        x="final_result",
        y="score",
        order=[item for item in FINAL_RESULT_ORDER if item in set(score_with_result["final_result"])],
        color="#4C78A8",
    )
    plt.title("Phân bố score theo final_result")
    plt.xlabel("final_result")
    plt.ylabel("Score")
    return save_current_figure("score_by_final_result_boxplot.png")


def plot_total_click_by_final_result(student_summary: pd.DataFrame) -> Path:
    plot_data = student_summary[["final_result", "total_click"]].copy()
    plot_data["log_total_click"] = pd.to_numeric(
        plot_data["total_click"], errors="coerce"
    ).fillna(0).clip(lower=0).map(math.log1p)
    plt.figure(figsize=(9, 5))
    sns.boxplot(
        data=plot_data,
        x="final_result",
        y="log_total_click",
        order=[item for item in FINAL_RESULT_ORDER if item in set(plot_data["final_result"])],
        color="#F58518",
    )
    plt.title("Phân bố tổng click theo final_result")
    plt.xlabel("final_result")
    plt.ylabel("log1p(total_click)")
    return save_current_figure("student_total_click_by_final_result_boxplot.png")


def plot_weekly_click_by_final_result(
    weekly_activity: pd.DataFrame, student_summary: pd.DataFrame
) -> Path:
    weekly_with_result = weekly_activity.merge(
        student_summary[["code_module", "code_presentation", "id_student", "final_result"]],
        on=["code_module", "code_presentation", "id_student"],
        how="left",
    )
    weekly_with_result["log_weekly_click"] = pd.to_numeric(
        weekly_with_result["weekly_click"], errors="coerce"
    ).fillna(0).clip(lower=0).map(math.log1p)
    plt.figure(figsize=(9, 5))
    sns.boxplot(
        data=weekly_with_result,
        x="final_result",
        y="log_weekly_click",
        order=[item for item in FINAL_RESULT_ORDER if item in set(weekly_with_result["final_result"])],
        color="#B279A2",
    )
    plt.title("Phân bố weekly_click theo final_result")
    plt.xlabel("final_result")
    plt.ylabel("log1p(weekly_click)")
    return save_current_figure("weekly_click_by_final_result_boxplot.png")


def plot_demographics_by_final_result(student_summary: pd.DataFrame) -> Path:
    colors = {
        "Distinction": "#54A24B",
        "Pass": "#4C78A8",
        "Fail": "#E45756",
        "Withdrawn": "#F58518",
    }
    fig, axes = plt.subplots(3, 2, figsize=(16, 15))
    axes = axes.flatten()

    for axis, column in zip(axes, DEMOGRAPHIC_COLUMNS):
        prepared = student_summary[[column, "final_result"]].copy()
        prepared[column] = prepared[column].astype("object").where(
            prepared[column].notna(), "(missing)"
        )
        counts = (
            prepared.groupby([column, "final_result"])
            .size()
            .reset_index(name="count")
        )
        category_totals = counts.groupby(column)["count"].sum().sort_values(ascending=True)
        category_order = category_totals.tail(15).index
        pivot = (
            counts[counts[column].isin(category_order)]
            .pivot_table(index=column, columns="final_result", values="count", fill_value=0)
            .reindex(index=category_order)
            .reindex(columns=FINAL_RESULT_ORDER, fill_value=0)
        )
        pct = pivot.div(pivot.sum(axis=1), axis=0).fillna(0)
        left = pd.Series([0.0] * len(pct), index=pct.index)
        for result in FINAL_RESULT_ORDER:
            axis.barh(
                pct.index.astype(str),
                pct[result],
                left=left,
                color=colors[result],
                label=result,
            )
            left += pct[result]
        axis.set_title(column)
        axis.set_xlabel("Tỷ lệ trong nhóm")
        axis.set_ylabel("")
        axis.set_xlim(0, 1)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        title="final_result",
        ncol=4,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.01),
    )
    return save_current_figure("student_background_by_final_result.png")


def plot_score_ecdf_by_final_result(
    assessment_progress: pd.DataFrame, student_summary: pd.DataFrame
) -> Path:
    score_with_result = assessment_progress.merge(
        student_summary[["code_module", "code_presentation", "id_student", "final_result"]],
        on=["code_module", "code_presentation", "id_student"],
        how="left",
    )
    plt.figure(figsize=(9, 5))
    sns.ecdfplot(
        data=score_with_result.dropna(subset=["score", "final_result"]),
        x="score",
        hue="final_result",
        hue_order=[item for item in FINAL_RESULT_ORDER if item in set(score_with_result["final_result"])],
    )
    plt.title("ECDF điểm assessment theo final_result")
    plt.xlabel("Score")
    plt.ylabel("Tỷ lệ tích lũy")
    return save_current_figure("score_ecdf_by_final_result.png")


def plot_total_click_ecdf_by_final_result(student_summary: pd.DataFrame) -> Path:
    plot_data = student_summary[["final_result", "total_click"]].copy()
    plot_data["log_total_click"] = pd.to_numeric(
        plot_data["total_click"], errors="coerce"
    ).fillna(0).clip(lower=0).map(math.log1p)
    plt.figure(figsize=(9, 5))
    sns.ecdfplot(
        data=plot_data.dropna(subset=["final_result"]),
        x="log_total_click",
        hue="final_result",
        hue_order=[item for item in FINAL_RESULT_ORDER if item in set(plot_data["final_result"])],
    )
    plt.title("ECDF log1p(total_click) theo final_result")
    plt.xlabel("log1p(total_click)")
    plt.ylabel("Tỷ lệ tích lũy")
    return save_current_figure("student_total_click_ecdf_by_final_result.png")


def plot_activity_type_bubble(activity_type_distribution: pd.DataFrame) -> Path:
    plot_data = activity_type_distribution.sort_values("total_click", ascending=False).head(15).copy()
    max_records = plot_data["interaction_records"].max()
    plot_data["bubble_size"] = (
        plot_data["interaction_records"] / max_records * 900 + 80 if max_records else 120
    )

    plt.figure(figsize=(10, 7))
    plt.scatter(
        plot_data["resource_count"],
        plot_data["total_click"],
        s=plot_data["bubble_size"],
        alpha=0.65,
        color="#4C78A8",
        edgecolor="white",
        linewidth=1,
    )
    for row in plot_data.itertuples(index=False):
        plt.annotate(
            row.activity_type,
            (row.resource_count, row.total_click),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=8,
        )
    plt.title("Activity_type theo số tài nguyên và tổng click")
    plt.xlabel("Số tài nguyên VLE")
    plt.ylabel("Tổng click")
    plt.xscale("log")
    plt.yscale("log")
    return save_current_figure("activity_type_resource_click_bubble.png")


def build_student_distributions(student_summary: pd.DataFrame) -> dict[str, pd.DataFrame]:
    outputs: dict[str, pd.DataFrame] = {}

    outputs["final_result_distribution.csv"] = value_distribution(
        student_summary["final_result"], "final_result"
    )

    by_module = (
        student_summary.groupby("code_module")
        .agg(
            enrolment_count=("id_student", "size"),
            unique_students=("id_student", "nunique"),
        )
        .reset_index()
        .sort_values("enrolment_count", ascending=False)
    )
    outputs["students_by_module.csv"] = add_pct(by_module, "enrolment_count")

    by_presentation = (
        student_summary.groupby("code_presentation")
        .agg(
            enrolment_count=("id_student", "size"),
            unique_students=("id_student", "nunique"),
        )
        .reset_index()
        .sort_values("code_presentation")
    )
    outputs["students_by_presentation.csv"] = add_pct(by_presentation, "enrolment_count")

    by_module_presentation = (
        student_summary.groupby(["code_module", "code_presentation"])
        .agg(
            enrolment_count=("id_student", "size"),
            unique_students=("id_student", "nunique"),
            median_total_click=("total_click", "median"),
            mean_total_click=("total_click", "mean"),
            median_weighted_score=("weighted_score", "median"),
            mean_weighted_score=("weighted_score", "mean"),
        )
        .reset_index()
        .sort_values(["code_module", "code_presentation"])
    )
    outputs["students_by_module_presentation.csv"] = by_module_presentation

    final_result_mp = (
        student_summary.groupby(["code_module", "code_presentation", "final_result"])
        .size()
        .reset_index(name="count")
    )
    final_result_mp["pct_within_module_presentation"] = final_result_mp["count"] / final_result_mp.groupby(
        ["code_module", "code_presentation"]
    )["count"].transform("sum")
    outputs["final_result_by_module_presentation.csv"] = final_result_mp

    for column in DEMOGRAPHIC_COLUMNS:
        outputs[f"{column}_distribution.csv"] = value_distribution(student_summary[column], column)
        prepared = student_summary[[column, "final_result"]].copy()
        prepared[column] = prepared[column].astype("object").where(
            prepared[column].notna(), "(missing)"
        )
        by_result = (
            prepared.groupby([column, "final_result"])
            .size()
            .reset_index(name="count")
            .sort_values([column, "final_result"])
        )
        by_result["pct_within_group"] = by_result["count"] / by_result.groupby(column)[
            "count"
        ].transform("sum")
        outputs[f"{column}_by_final_result.csv"] = by_result

    outputs["total_click_summary.csv"] = numeric_summary(
        student_summary["total_click"], "student_total_click"
    )
    bins = [-1, 0, 50, 100, 250, 500, 1000, 2000, 5000, 10_000, float("inf")]
    labels = ["0", "1-50", "51-100", "101-250", "251-500", "501-1000", "1001-2000", "2001-5000", "5001-10000", ">10000"]
    click_bins = pd.cut(student_summary["total_click"].fillna(0), bins=bins, labels=labels)
    outputs["total_click_distribution_bins.csv"] = value_distribution(click_bins, "total_click_bin")

    return outputs


def build_assessment_distributions(
    assessment_progress: pd.DataFrame,
    assessments: pd.DataFrame,
    student_summary: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    outputs: dict[str, pd.DataFrame] = {}

    outputs["score_summary.csv"] = numeric_summary(assessment_progress["score"], "assessment_score")
    score_bins = pd.cut(
        assessment_progress["score"],
        bins=[-0.01, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        labels=["0-10", "11-20", "21-30", "31-40", "41-50", "51-60", "61-70", "71-80", "81-90", "91-100"],
    )
    outputs["score_distribution_bins.csv"] = value_distribution(score_bins, "score_bin")

    score_by_type = (
        assessment_progress.groupby("assessment_type")
        .agg(
            submission_count=("score", "size"),
            scored_count=("score", "count"),
            mean_score=("score", "mean"),
            median_score=("score", "median"),
            p25_score=("score", lambda s: s.quantile(0.25)),
            p75_score=("score", lambda s: s.quantile(0.75)),
        )
        .reset_index()
        .sort_values("submission_count", ascending=False)
    )
    outputs["score_by_assessment_type.csv"] = score_by_type

    score_with_result = assessment_progress.merge(
        student_summary[
            ["code_module", "code_presentation", "id_student", "final_result"]
        ],
        on=["code_module", "code_presentation", "id_student"],
        how="left",
    )
    score_by_result = (
        score_with_result.groupby("final_result")
        .agg(
            submission_count=("score", "size"),
            scored_count=("score", "count"),
            mean_score=("score", "mean"),
            median_score=("score", "median"),
        )
        .reset_index()
    )
    outputs["score_by_final_result.csv"] = score_by_result

    unique_assessments = assessments.drop_duplicates("id_assessment").copy()
    outputs["assessment_weight_summary.csv"] = numeric_summary(
        unique_assessments["weight"], "assessment_weight"
    )
    weight_bins = pd.cut(
        unique_assessments["weight"],
        bins=[-0.01, 0, 5, 10, 20, 40, 60, 80, 100],
        labels=["0", "1-5", "6-10", "11-20", "21-40", "41-60", "61-80", "81-100"],
    )
    outputs["assessment_weight_distribution_bins.csv"] = value_distribution(
        weight_bins, "weight_bin"
    )
    weight_by_type = (
        unique_assessments.groupby("assessment_type")
        .agg(
            assessment_count=("id_assessment", "nunique"),
            mean_weight=("weight", "mean"),
            median_weight=("weight", "median"),
            min_weight=("weight", "min"),
            max_weight=("weight", "max"),
        )
        .reset_index()
        .sort_values("assessment_count", ascending=False)
    )
    outputs["assessment_weight_by_type.csv"] = weight_by_type

    return outputs


def build_weekly_click_distributions(weekly_activity: pd.DataFrame) -> dict[str, pd.DataFrame]:
    outputs: dict[str, pd.DataFrame] = {}
    outputs["weekly_click_summary.csv"] = numeric_summary(
        weekly_activity["weekly_click"], "weekly_click"
    )
    weekly_bins = pd.cut(
        weekly_activity["weekly_click"],
        bins=[-1, 0, 10, 25, 50, 100, 250, 500, 1000, float("inf")],
        labels=["0", "1-10", "11-25", "26-50", "51-100", "101-250", "251-500", "501-1000", ">1000"],
    )
    outputs["weekly_click_distribution_bins.csv"] = value_distribution(
        weekly_bins, "weekly_click_bin"
    )
    return outputs


def build_activity_type_distribution(chunk_size: int) -> pd.DataFrame:
    vle = read_csv(STAGING_VLE, usecols=["id_site", "activity_type"])
    resource_counts = (
        vle.groupby("activity_type")
        .size()
        .reset_index(name="resource_count")
        .sort_values("resource_count", ascending=False)
    )

    site_activity = vle.set_index("id_site")["activity_type"]
    chunks = pd.read_csv(
        STAGING_STUDENT_VLE,
        usecols=["id_site", "sum_click"],
        chunksize=chunk_size,
    )

    grouped_chunks: list[pd.DataFrame] = []
    missing_rows = 0
    for chunk in chunks:
        chunk["activity_type"] = chunk["id_site"].map(site_activity)
        missing_rows += int(chunk["activity_type"].isna().sum())
        grouped = (
            chunk.dropna(subset=["activity_type"])
            .groupby("activity_type")
            .agg(
                interaction_records=("sum_click", "size"),
                total_click=("sum_click", "sum"),
                mean_click_per_record=("sum_click", "mean"),
            )
            .reset_index()
        )
        grouped_chunks.append(grouped)

    if grouped_chunks:
        engagement = (
            pd.concat(grouped_chunks, ignore_index=True)
            .groupby("activity_type")
            .agg(
                interaction_records=("interaction_records", "sum"),
                total_click=("total_click", "sum"),
            )
            .reset_index()
        )
        engagement["mean_click_per_record"] = (
            engagement["total_click"] / engagement["interaction_records"]
        )
    else:
        engagement = pd.DataFrame(
            columns=["activity_type", "interaction_records", "total_click", "mean_click_per_record"]
        )

    distribution = resource_counts.merge(engagement, on="activity_type", how="outer").fillna(0)
    distribution["pct_interaction_records"] = distribution["interaction_records"] / distribution[
        "interaction_records"
    ].sum()
    distribution["pct_total_click"] = distribution["total_click"] / distribution["total_click"].sum()
    distribution["unmatched_student_vle_rows"] = missing_rows
    return distribution.sort_values("total_click", ascending=False)


def create_figures(
    student_summary: pd.DataFrame,
    assessment_progress: pd.DataFrame,
    assessments: pd.DataFrame,
    weekly_activity: pd.DataFrame,
    activity_type_distribution: pd.DataFrame,
    final_result_distribution: pd.DataFrame,
    students_by_module: pd.DataFrame,
) -> list[Path]:
    figure_paths: list[Path] = []

    figure_paths.append(
        plot_bar(
            final_result_distribution,
            "final_result",
            "count",
            "final_result_distribution.png",
            "Phân bố final_result",
            "Kết quả cuối",
            "Số bản ghi student-module-presentation",
            order=[item for item in FINAL_RESULT_ORDER if item in set(final_result_distribution["final_result"])],
        )
    )
    figure_paths.append(
        plot_bar(
            students_by_module,
            "code_module",
            "enrolment_count",
            "students_by_module.png",
            "Phân bố sinh viên theo module",
            "Module",
            "Số bản ghi student-module-presentation",
        )
    )
    figure_paths.append(plot_final_result_by_module_presentation(student_summary))
    figure_paths.append(plot_final_result_heatmap_by_module_presentation(student_summary))
    figure_paths.append(
        plot_hist(
            assessment_progress["score"],
            "score_distribution.png",
            "Phân bố điểm assessment",
            "Score",
        )
    )
    figure_paths.append(
        plot_hist(
            assessments.drop_duplicates("id_assessment")["weight"],
            "assessment_weight_distribution.png",
            "Phân bố weight của assessment",
            "Weight",
            bins=30,
        )
    )
    figure_paths.append(
        plot_hist(
            student_summary["total_click"],
            "student_total_click_log_distribution.png",
            "Phân bố tổng click theo sinh viên",
            "log1p(total_click)",
            bins=45,
            log1p=True,
        )
    )
    figure_paths.append(
        plot_hist(
            weekly_activity["weekly_click"],
            "weekly_click_log_distribution.png",
            "Phân bố click theo tuần học",
            "log1p(weekly_click)",
            bins=45,
            log1p=True,
        )
    )
    figure_paths.append(
        plot_box(
            assessment_progress["score"],
            "score_boxplot.png",
            "Boxplot điểm assessment",
            "Score",
        )
    )
    figure_paths.append(
        plot_box(
            student_summary["total_click"],
            "student_total_click_log_boxplot.png",
            "Boxplot tổng click theo sinh viên",
            "log1p(total_click)",
            log1p=True,
        )
    )
    figure_paths.append(
        plot_box(
            weekly_activity["weekly_click"],
            "weekly_click_log_boxplot.png",
            "Boxplot click theo tuần học",
            "log1p(weekly_click)",
            log1p=True,
        )
    )
    figure_paths.append(plot_score_by_final_result(assessment_progress, student_summary))
    figure_paths.append(plot_total_click_by_final_result(student_summary))
    figure_paths.append(plot_weekly_click_by_final_result(weekly_activity, student_summary))
    figure_paths.append(plot_score_ecdf_by_final_result(assessment_progress, student_summary))
    figure_paths.append(plot_total_click_ecdf_by_final_result(student_summary))

    top_activity = activity_type_distribution.sort_values("total_click", ascending=False).head(15)
    plt.figure(figsize=(10, 7))
    sns.barplot(data=top_activity, y="activity_type", x="total_click", color="#F58518")
    plt.title("Top activity_type theo tổng click")
    plt.xlabel("Tổng click")
    plt.ylabel("activity_type")
    figure_paths.append(save_current_figure("activity_type_total_click.png"))
    figure_paths.append(plot_activity_type_bubble(activity_type_distribution))

    figure_paths.append(plot_demographics(student_summary))
    figure_paths.append(plot_demographics_by_final_result(student_summary))
    return figure_paths


def fmt_int(value: float | int) -> str:
    return f"{int(round(value)):,}"


def fmt_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def table_link(path: Path) -> str:
    return path.relative_to(ROOT_DIR).as_posix()


def write_report(
    table_paths: dict[str, Path],
    figure_paths: list[Path],
    student_summary: pd.DataFrame,
    assessment_progress: pd.DataFrame,
    weekly_activity: pd.DataFrame,
    activity_type_distribution: pd.DataFrame,
) -> Path:
    final_result = pd.read_csv(table_paths["final_result_distribution.csv"])
    top_result = final_result.sort_values("count", ascending=False).iloc[0]
    module_counts = pd.read_csv(table_paths["students_by_module.csv"])
    top_module = module_counts.iloc[0]
    score_summary = pd.read_csv(table_paths["score_summary.csv"]).iloc[0]
    click_summary = pd.read_csv(table_paths["total_click_summary.csv"]).iloc[0]
    top_activity = activity_type_distribution.iloc[0]

    figure_lines = "\n".join(
        f"- `{table_link(path)}`" for path in sorted(figure_paths, key=lambda p: p.name)
    )
    table_lines = "\n".join(
        f"- `{table_link(path)}`" for path in sorted(table_paths.values(), key=lambda p: p.name)
    )

    report = f"""# Báo Cáo EDA - Phân Bố Dữ Liệu

## 1. Phạm vi

Phần này phân tích phân bố dữ liệu OULAD ở mức EDA-ready. Đơn vị chính của bảng `eda_student_summary` là một bản ghi `student - module - presentation`, không phải chỉ riêng `id_student`.

Nguồn dữ liệu:

- `ETL/eda_data/eda_student_summary.csv`
- `ETL/eda_data/eda_weekly_activity.csv`
- `ETL/eda_data/eda_assessment_progress.csv`
- `ETL/staging_data/assessments.csv`
- `ETL/staging_data/vle.csv`
- `ETL/staging_data/studentVle.csv`

## 2. Quy mô dữ liệu đã dùng

| Bảng | Số dòng | Ý nghĩa chính |
| --- | ---: | --- |
| `eda_student_summary` | {fmt_int(len(student_summary))} | Tổng hợp theo student-module-presentation |
| `eda_assessment_progress` | {fmt_int(len(assessment_progress))} | Bản ghi nộp assessment |
| `eda_weekly_activity` | {fmt_int(len(weekly_activity))} | Hoạt động VLE theo tuần học |

## 3. Nhận xét chính

- Nhóm `final_result` lớn nhất là `{top_result["final_result"]}` với {fmt_int(top_result["count"])} bản ghi, chiếm {fmt_pct(top_result["pct"])}.
- Module có nhiều bản ghi student-module-presentation nhất là `{top_module["code_module"]}` với {fmt_int(top_module["enrolment_count"])} bản ghi.
- Điểm assessment có trung vị {score_summary["median"]:.1f}, trung bình {score_summary["mean"]:.1f}, và thiếu {fmt_int(score_summary["missing"])} giá trị.
- Tổng click theo sinh viên lệch phải rõ rệt: trung vị {click_summary["median"]:.1f}, p95 {click_summary["p95"]:.1f}, max {click_summary["max"]:.1f}.
- `activity_type` có tổng click lớn nhất là `{top_activity["activity_type"]}` với {fmt_int(top_activity["total_click"])} click.

Đọc diễn giải chi tiết tại [02_distribution_insights.md](02_distribution_insights.md).

## 4. Các phân bố đã hoàn thành

- Phân bố `final_result`.
- Phân bố sinh viên theo `code_module`.
- Phân bố sinh viên theo `code_presentation`.
- Phân bố `score` trong `studentAssessment`.
- Phân bố `weight` của assessment.
- Phân bố click theo sinh viên và theo tuần học.
- Phân bố `activity_type` theo số tài nguyên, số bản ghi tương tác và tổng click.
- Phân bố thông tin nền: `gender`, `region`, `highest_education`, `imd_band`, `age_band`, `disability`.
- So sánh phân bố `final_result` giữa các module-presentation.
- Boxplot cho `score`, tổng click theo sinh viên và click theo tuần học.
- So sánh phân bố thông tin nền theo `final_result`.

## 5. Bảng đầu ra

{table_lines}

## 6. Biểu đồ đầu ra

{figure_lines}

## 7. Ghi chú diễn giải

- Không xóa hoặc thay đổi dữ liệu nguồn trong quá trình EDA.
- Các biểu đồ click dùng `log1p` để nhìn rõ phân bố vì biến click lệch phải mạnh.
- Boxplot click cũng dùng `log1p` để tránh một vài giá trị rất lớn làm nén toàn bộ phần còn lại.
- Phân bố `activity_type` dùng `vle.id_site` để map sang `studentVle.id_site`; nếu xuất hiện dòng không map được, số lượng sẽ được ghi trong bảng `activity_type_distribution.csv`.
- Kết quả này là EDA mô tả, chưa khẳng định quan hệ nhân quả giữa tương tác VLE, điểm assessment và kết quả cuối.
"""
    path = DOC_DIR / "02_distribution_report.md"
    path.write_text(report, encoding="utf-8")
    return path


def write_insights(
    table_paths: dict[str, Path],
    student_summary: pd.DataFrame,
    activity_type_distribution: pd.DataFrame,
) -> Path:
    final_result = pd.read_csv(table_paths["final_result_distribution.csv"])
    final_result_mp = pd.read_csv(table_paths["final_result_by_module_presentation.csv"])
    score_by_result = pd.read_csv(table_paths["score_by_final_result.csv"])

    top_result = final_result.sort_values("count", ascending=False).iloc[0]
    withdrawn_mp = final_result_mp[final_result_mp["final_result"].eq("Withdrawn")].sort_values(
        "pct_within_module_presentation", ascending=False
    ).iloc[0]
    distinction_mp = final_result_mp[
        final_result_mp["final_result"].eq("Distinction")
    ].sort_values("pct_within_module_presentation", ascending=False).iloc[0]

    click_by_result = (
        student_summary.groupby("final_result")
        .agg(
            student_records=("id_student", "size"),
            median_total_click=("total_click", "median"),
            mean_total_click=("total_click", "mean"),
            zero_click_count=("total_click", lambda s: int(s.fillna(0).eq(0).sum())),
            median_weighted_score=("weighted_score", "median"),
        )
        .reset_index()
    )
    click_by_result["zero_click_pct"] = (
        click_by_result["zero_click_count"] / click_by_result["student_records"]
    )
    withdrawn_click = click_by_result[click_by_result["final_result"].eq("Withdrawn")].iloc[0]
    distinction_click = click_by_result[
        click_by_result["final_result"].eq("Distinction")
    ].iloc[0]
    pass_score = score_by_result[score_by_result["final_result"].eq("Pass")].iloc[0]
    withdrawn_score = score_by_result[
        score_by_result["final_result"].eq("Withdrawn")
    ].iloc[0]
    top_activity = activity_type_distribution.sort_values("total_click", ascending=False).iloc[0]
    top_activity_by_records = activity_type_distribution.sort_values(
        "interaction_records", ascending=False
    ).iloc[0]

    insights = f"""# EDA Insights - Phân Bố Dữ Liệu

## Cách đọc nhanh

File report chính cho biết đã vẽ gì và sinh bảng nào. File này trả lời câu hỏi: các biểu đồ đó đang nói gì, vì sao đáng chú ý, và nên dùng kết quả này thế nào ở các bước sau.

## 1. Phân bố kết quả học tập

Quan sát:

- Nhóm kết quả lớn nhất là `{top_result["final_result"]}` với {fmt_pct(top_result["pct"])} số bản ghi.
- Tỷ lệ `Withdrawn` cao nhất ở `{withdrawn_mp["code_module"]}-{withdrawn_mp["code_presentation"]}`, đạt {fmt_pct(withdrawn_mp["pct_within_module_presentation"])}.
- Tỷ lệ `Distinction` cao nhất ở `{distinction_mp["code_module"]}-{distinction_mp["code_presentation"]}`, đạt {fmt_pct(distinction_mp["pct_within_module_presentation"])}.

Diễn giải:

- Bộ dữ liệu không cân bằng hoàn toàn giữa các nhóm kết quả. `Pass` là nhóm lớn nhất, nhưng `Withdrawn` cũng đủ lớn để không thể xem là nhóm phụ.
- Khác biệt giữa module-presentation cho thấy không nên đánh giá kết quả học tập chỉ ở cấp toàn bộ dữ liệu. Mỗi module-presentation có thể có cấu trúc môn học, deadline, đánh giá và hành vi học khác nhau.

Ý nghĩa với phân tích sau:

- Nếu xây dashboard hoặc mô hình, nên luôn có lát cắt `code_module` và `code_presentation`.
- Nếu chọn bài toán dự báo `final_result`, cần chú ý mất cân bằng nhãn, đặc biệt giữa `Distinction` và các nhóm còn lại.

## 2. Điểm assessment

Quan sát:

- Điểm assessment trung vị của nhóm `Pass` là {pass_score["median_score"]:.1f}.
- Điểm assessment trung vị của nhóm `Withdrawn` là {withdrawn_score["median_score"]:.1f}.

Diễn giải:

- Điểm assessment phân biệt khá rõ các nhóm kết quả cuối, nhưng `Withdrawn` không đơn giản là nhóm điểm thấp. Một phần sinh viên rút môn có thể đã nộp một số bài với điểm quan sát được.
- Vì vậy, khi dùng điểm assessment để phân tích, cần đi kèm số bài đã nộp và thời điểm nộp. Chỉ nhìn điểm trung bình có thể bỏ sót bối cảnh sinh viên rút môn.

Ý nghĩa với phân tích sau:

- Nên dùng thêm `submitted_assessments`, `submitted_weight_sum`, `late_submissions` thay vì chỉ dùng `avg_score` hoặc `weighted_score`.
- Nếu làm cảnh báo sớm, không dùng điểm của assessment diễn ra sau checkpoint.

## 3. Tương tác VLE

Quan sát:

- Nhóm `Distinction` có median `total_click` là {distinction_click["median_total_click"]:.1f}.
- Nhóm `Withdrawn` có median `total_click` là {withdrawn_click["median_total_click"]:.1f}.
- Tỷ lệ `total_click = 0` trong nhóm `Withdrawn` là {fmt_pct(withdrawn_click["zero_click_pct"])}.

Diễn giải:

- Click VLE lệch phải mạnh. Một số sinh viên tương tác rất nhiều, làm trung bình cao hơn trung vị.
- ECDF theo `final_result` cho thấy nhóm kết quả tốt thường dịch sang phải, nghĩa là cần nhiều click hơn mới đạt cùng tỷ lệ tích lũy. Đây là tín hiệu có ích, nhưng không phải bằng chứng nhân quả.

Ý nghĩa với phân tích sau:

- Khi vẽ hoặc mô hình hóa click, nên dùng `log1p(total_click)` hoặc phân nhóm mức tương tác.
- Cần phân biệt sinh viên không tương tác với sinh viên tương tác ít. `total_click = 0` nên được giữ như một tín hiệu riêng.

## 4. Activity type

Quan sát:

- `activity_type` có tổng click cao nhất là `{top_activity["activity_type"]}`.
- `activity_type` có số bản ghi tương tác cao nhất là `{top_activity_by_records["activity_type"]}`.

Diễn giải:

- Một loại tài nguyên có nhiều click không nhất thiết có nhiều bản ghi tương tác nhất. Bubble chart giúp tách ba chiều: số tài nguyên, số bản ghi tương tác, và tổng click.
- Những loại như nội dung học, diễn đàn, quiz và homepage có vai trò khác nhau. Cần tránh gom tất cả thành một biến click duy nhất nếu câu hỏi phân tích cần hiểu hành vi học.

Ý nghĩa với phân tích sau:

- Nên tạo feature theo nhóm activity_type, ví dụ click vào nội dung học, forum, quiz.
- Nếu xây dashboard, nên hiển thị activity_type theo cả tổng click và số tài nguyên để tránh hiểu sai mức độ phổ biến.

## 5. Biến nền sinh viên

Quan sát:

- Phân bố theo `gender`, `region`, `highest_education`, `imd_band`, `age_band`, `disability` đã được so sánh với `final_result`.

Diễn giải:

- Biến nền có thể cho thấy khác biệt nhóm, nhưng cần cẩn thận khi diễn giải. Đây là quan sát mô tả, không phải kết luận nguyên nhân.
- Một số biến nền có thể phản ánh điều kiện học tập, nền tảng học vấn hoặc khả năng tiếp cận tài nguyên, nhưng cần kiểm tra thêm bằng phân tích tương quan hoặc mô hình kiểm soát module-presentation.

Ý nghĩa với phân tích sau:

- Với biến nhạy cảm như `disability`, nên dùng để hiểu chất lượng hỗ trợ và công bằng dữ liệu, không dùng để đưa ra kết luận đơn giản về năng lực cá nhân.
- `imd_band` có missing, nên khi phân tích biến này cần kết hợp insight từ phần missing data.
"""
    path = DOC_DIR / "02_distribution_insights.md"
    path.write_text(insights, encoding="utf-8")
    return path


def write_checklist() -> Path:
    checklist = """# Checklist EDA - Phân Bố Dữ Liệu

- [x] Phân tích phân bố `final_result`.
- [x] Phân tích phân bố sinh viên theo `code_module`.
- [x] Phân tích phân bố sinh viên theo `code_presentation`.
- [x] Phân tích phân bố điểm `score`.
- [x] Phân tích phân bố `weight` của assessment.
- [x] Phân tích phân bố click từ dữ liệu VLE.
- [x] Phân tích phân bố `activity_type`.
- [x] Phân tích phân bố `gender`, `region`, `highest_education`, `imd_band`, `age_band`, `disability`.
- [x] So sánh phân bố giữa các module-presentation.
- [x] Bổ sung boxplot cho `score`, `total_click`, `weekly_click`.
- [x] Bổ sung so sánh biến nền theo `final_result`.

Minh chứng:

- Script: `EDA/src/02_analyze_distributions.py`
- Report: `EDA/docs/02-distribution/02_distribution_report.md`
- Insights: `EDA/docs/02-distribution/02_distribution_insights.md`
- Tables: `EDA/outputs/tables/02_distribution/`
- Figures: `EDA/outputs/figures/02_distribution/`
"""
    path = DOC_DIR / "02_distribution_checklist.md"
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

    distribution_tables: dict[str, pd.DataFrame] = {}
    distribution_tables.update(build_student_distributions(student_summary))
    distribution_tables.update(
        build_assessment_distributions(assessment_progress, assessments, student_summary)
    )
    distribution_tables.update(build_weekly_click_distributions(weekly_activity))
    distribution_tables["activity_type_distribution.csv"] = build_activity_type_distribution(
        args.chunk_size
    )

    table_paths = {
        filename: write_table(dataframe, filename)
        for filename, dataframe in distribution_tables.items()
    }

    figure_paths = create_figures(
        student_summary=student_summary,
        assessment_progress=assessment_progress,
        assessments=assessments,
        weekly_activity=weekly_activity,
        activity_type_distribution=distribution_tables["activity_type_distribution.csv"],
        final_result_distribution=distribution_tables["final_result_distribution.csv"],
        students_by_module=distribution_tables["students_by_module.csv"],
    )
    report_path = write_report(
        table_paths=table_paths,
        figure_paths=figure_paths,
        student_summary=student_summary,
        assessment_progress=assessment_progress,
        weekly_activity=weekly_activity,
        activity_type_distribution=distribution_tables["activity_type_distribution.csv"],
    )
    insights_path = write_insights(
        table_paths=table_paths,
        student_summary=student_summary,
        activity_type_distribution=distribution_tables["activity_type_distribution.csv"],
    )
    checklist_path = write_checklist()

    print(f"Wrote {len(table_paths)} tables to {TABLE_DIR.relative_to(ROOT_DIR)}")
    print(f"Wrote {len(figure_paths)} figures to {FIGURE_DIR.relative_to(ROOT_DIR)}")
    print(f"Wrote report: {report_path.relative_to(ROOT_DIR)}")
    print(f"Wrote insights: {insights_path.relative_to(ROOT_DIR)}")
    print(f"Wrote checklist: {checklist_path.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
