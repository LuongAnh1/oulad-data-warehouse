"""Analyze correlations and relationships for OULAD EDA."""

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
EDA_DIR = ROOT_DIR / "EDA"
TABLE_DIR = EDA_DIR / "outputs" / "tables" / "05_correlation"
FIGURE_DIR = EDA_DIR / "outputs" / "figures" / "05_correlation"
DOC_DIR = EDA_DIR / "docs" / "05-correlation"

STUDENT_SUMMARY = EDA_DATA_DIR / "eda_student_summary.csv"
WEEKLY_ACTIVITY = EDA_DATA_DIR / "eda_weekly_activity.csv"
ASSESSMENT_PROGRESS = EDA_DATA_DIR / "eda_assessment_progress.csv"

FINAL_RESULT_ORDER = ["Distinction", "Pass", "Fail", "Withdrawn"]
SUCCESS_RESULTS = {"Distinction", "Pass"}
STUDENT_KEYS = ["code_module", "code_presentation", "id_student"]

NUMERIC_METRICS = [
    "log_total_click",
    "active_days",
    "active_weeks",
    "interacted_sites",
    "resource_types_used",
    "submitted_assessments",
    "submitted_weight_sum",
    "late_submissions",
    "late_submission_rate",
    "avg_score",
    "weighted_score",
    "studied_credits",
    "num_of_prev_attempts",
    "success_flag",
]

METRIC_LABELS = {
    "total_click": "Total click",
    "log_total_click": "Log1p total click",
    "active_days": "Active days",
    "active_weeks": "Active weeks",
    "interacted_sites": "Interacted sites",
    "resource_types_used": "Resource types",
    "submitted_assessments": "Submitted assessments",
    "submitted_weight_sum": "Submitted weight",
    "late_submissions": "Late submissions",
    "late_submission_rate": "Late submission rate",
    "avg_score": "Average score",
    "weighted_score": "Weighted score",
    "studied_credits": "Studied credits",
    "num_of_prev_attempts": "Previous attempts",
    "success_flag": "Pass/Distinction flag",
}

KEY_PAIR_DEFINITIONS = [
    ("total_click", "avg_score", "total click vs average score"),
    ("log_total_click", "avg_score", "log total click vs average score"),
    ("total_click", "weighted_score", "total click vs weighted score"),
    ("log_total_click", "weighted_score", "log total click vs weighted score"),
    ("active_days", "weighted_score", "active days vs weighted score"),
    ("active_weeks", "weighted_score", "active weeks vs weighted score"),
    ("interacted_sites", "weighted_score", "interacted sites vs weighted score"),
    ("resource_types_used", "weighted_score", "resource types vs weighted score"),
    ("submitted_assessments", "weighted_score", "submitted assessments vs weighted score"),
    ("submitted_weight_sum", "weighted_score", "submitted weight vs weighted score"),
    ("late_submissions", "weighted_score", "late submissions vs weighted score"),
    ("late_submission_rate", "weighted_score", "late submission rate vs weighted score"),
    ("log_total_click", "success_flag", "log total click vs pass/distinction flag"),
    ("active_days", "success_flag", "active days vs pass/distinction flag"),
    ("late_submission_rate", "success_flag", "late submission rate vs pass/distinction flag"),
]


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


def fmt_float(value: float, digits: int = 3) -> str:
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


def prepare_student_metrics(student_summary: pd.DataFrame) -> pd.DataFrame:
    df = student_summary.copy()
    numeric_cols = [
        "num_of_prev_attempts",
        "studied_credits",
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
        "banked_assessments",
        "score_weight_product_sum",
        "submitted_weight_sum",
        "weighted_score",
    ]
    for column in numeric_cols:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    df["log_total_click"] = np.log1p(df["total_click"].clip(lower=0))
    df["late_submission_rate"] = np.where(
        df["submitted_records"] > 0,
        df["late_submissions"] / df["submitted_records"],
        np.nan,
    )
    df["success_flag"] = df["final_result"].isin(SUCCESS_RESULTS).astype(int)
    return df


def correlation_matrix(df: pd.DataFrame, method: str) -> pd.DataFrame:
    numeric = df[NUMERIC_METRICS].apply(pd.to_numeric, errors="coerce")
    if method == "spearman":
        corr = numeric.rank(method="average").corr(method="pearson", min_periods=30)
    else:
        corr = numeric.corr(method="pearson", min_periods=30)
    return (
        corr.rename(index=METRIC_LABELS, columns=METRIC_LABELS)
        .reset_index()
        .rename(columns={"index": "metric"})
    )


def series_correlation(
    x: pd.Series, y: pd.Series, method: str, min_n: int = 30
) -> float:
    pair = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(pair) < min_n:
        return np.nan
    if pair["x"].nunique() < 2 or pair["y"].nunique() < 2:
        return np.nan
    if method == "spearman":
        pair = pair.rank(method="average")
    return pair["x"].corr(pair["y"], method="pearson")


def pair_correlation(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    segment: str,
    min_n: int = 30,
) -> dict[str, object]:
    pair = df[[x_col, y_col]].dropna()
    n = len(pair)
    pearson = series_correlation(pair[x_col], pair[y_col], "pearson", min_n=min_n)
    spearman = series_correlation(pair[x_col], pair[y_col], "spearman", min_n=min_n)
    return {
        "segment": segment,
        "x_metric": x_col,
        "x_label": METRIC_LABELS.get(x_col, x_col),
        "y_metric": y_col,
        "y_label": METRIC_LABELS.get(y_col, y_col),
        "n": n,
        "pearson_corr": pearson,
        "spearman_corr": spearman,
    }


def build_key_correlations(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for x_col, y_col, description in KEY_PAIR_DEFINITIONS:
        row = pair_correlation(df, x_col, y_col, "overall")
        row["relationship"] = description
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_metric_by_final_result(df: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "total_click",
        "log_total_click",
        "active_days",
        "active_weeks",
        "interacted_sites",
        "resource_types_used",
        "submitted_assessments",
        "submitted_weight_sum",
        "late_submissions",
        "late_submission_rate",
        "avg_score",
        "weighted_score",
    ]
    rows: list[dict[str, object]] = []
    for result in FINAL_RESULT_ORDER:
        group = df[df["final_result"] == result]
        for metric in metrics:
            values = pd.to_numeric(group[metric], errors="coerce").dropna()
            quantiles = values.quantile([0.25, 0.5, 0.75, 0.9]) if len(values) else pd.Series()
            rows.append(
                {
                    "final_result": result,
                    "metric": metric,
                    "metric_label": METRIC_LABELS.get(metric, metric),
                    "row_count": len(group),
                    "non_missing_count": len(values),
                    "mean": values.mean() if len(values) else np.nan,
                    "p25": quantiles.loc[0.25] if len(values) else np.nan,
                    "median": quantiles.loc[0.5] if len(values) else np.nan,
                    "p75": quantiles.loc[0.75] if len(values) else np.nan,
                    "p90": quantiles.loc[0.9] if len(values) else np.nan,
                    "max": values.max() if len(values) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def build_engagement_band_distribution(df: pd.DataFrame) -> pd.DataFrame:
    data = df[["final_result", "total_click"]].copy()
    data["engagement_band"] = "0 click"
    positive = data["total_click"] > 0
    labels = ["Low click", "Medium-low click", "Medium-high click", "High click"]
    data.loc[positive, "engagement_band"] = pd.qcut(
        data.loc[positive, "total_click"],
        q=4,
        labels=labels,
        duplicates="drop",
    ).astype(str)
    band_order = ["0 click", *labels]
    grouped = (
        data.groupby(["engagement_band", "final_result"], observed=False)
        .size()
        .rename("count")
        .reset_index()
    )
    all_index = pd.MultiIndex.from_product(
        [band_order, FINAL_RESULT_ORDER], names=["engagement_band", "final_result"]
    )
    grouped = (
        grouped.set_index(["engagement_band", "final_result"])
        .reindex(all_index, fill_value=0)
        .reset_index()
    )
    grouped["band_total"] = grouped.groupby("engagement_band")["count"].transform("sum")
    grouped["pct_within_band"] = np.where(
        grouped["band_total"] > 0,
        grouped["count"] / grouped["band_total"],
        0,
    )
    grouped["engagement_band"] = pd.Categorical(
        grouped["engagement_band"], categories=band_order, ordered=True
    )
    grouped["final_result"] = pd.Categorical(
        grouped["final_result"], categories=FINAL_RESULT_ORDER, ordered=True
    )
    return grouped.sort_values(["engagement_band", "final_result"])


def summarize_assessment_scores(
    assessment_progress: pd.DataFrame, student_metrics: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    keys = STUDENT_KEYS
    student_results = student_metrics[keys + ["final_result"]]
    data = assessment_progress.merge(student_results, on=keys, how="left")
    data["score"] = pd.to_numeric(data["score"], errors="coerce")
    data["days_from_due"] = data["date_submitted"] - data["date"]

    rows: list[dict[str, object]] = []
    for result in FINAL_RESULT_ORDER:
        group = data[data["final_result"] == result]
        values = group["score"].dropna()
        quantiles = values.quantile([0.25, 0.5, 0.75]) if len(values) else pd.Series()
        rows.append(
            {
                "final_result": result,
                "row_count": len(group),
                "score_count": len(values),
                "score_missing_count": int(group["score"].isna().sum()),
                "score_mean": values.mean() if len(values) else np.nan,
                "score_p25": quantiles.loc[0.25] if len(values) else np.nan,
                "score_median": quantiles.loc[0.5] if len(values) else np.nan,
                "score_p75": quantiles.loc[0.75] if len(values) else np.nan,
                "late_count": int(group["is_late"].fillna(False).sum()),
                "late_pct": group["is_late"].fillna(False).mean() if len(group) else np.nan,
                "median_days_from_due": group["days_from_due"].median(),
            }
        )
    by_result = pd.DataFrame(rows)

    by_type = (
        data.groupby(["assessment_type", "final_result"], dropna=False)
        .agg(
            row_count=("id_assessment", "size"),
            score_count=("score", "count"),
            score_mean=("score", "mean"),
            score_median=("score", "median"),
            late_pct=("is_late", "mean"),
            median_days_from_due=("days_from_due", "median"),
        )
        .reset_index()
        .sort_values(["assessment_type", "final_result"])
    )

    plot_sample = data[
        ["final_result", "assessment_type", "score", "days_from_due", "is_late"]
    ].copy()
    return by_result, by_type, plot_sample


def build_module_correlations(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (module, presentation), group in df.groupby(["code_module", "code_presentation"]):
        row = {
            "code_module": module,
            "code_presentation": presentation,
            "student_module_presentation_count": len(group),
            "success_rate": group["success_flag"].mean(),
        }
        for x_col, y_col, description in KEY_PAIR_DEFINITIONS:
            stats = pair_correlation(group, x_col, y_col, f"{module}-{presentation}")
            prefix = description.replace(" ", "_").replace("/", "_")
            row[f"{prefix}_n"] = stats["n"]
            row[f"{prefix}_pearson_corr"] = stats["pearson_corr"]
            row[f"{prefix}_spearman_corr"] = stats["spearman_corr"]
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["code_module", "code_presentation"])


def build_weekly_relationship_summary(
    weekly_activity: pd.DataFrame, student_metrics: pd.DataFrame
) -> pd.DataFrame:
    keys = STUDENT_KEYS
    weekly = weekly_activity.merge(
        student_metrics[keys + ["final_result"]],
        on=keys,
        how="left",
    )
    weekly["weekly_click"] = pd.to_numeric(weekly["weekly_click"], errors="coerce")
    weekly["active_days"] = pd.to_numeric(weekly["active_days"], errors="coerce")
    summary = (
        weekly.groupby(["study_week", "final_result"], dropna=False)
        .agg(
            active_student_count=("id_student", "nunique"),
            weekly_click_sum=("weekly_click", "sum"),
            weekly_click_median=("weekly_click", "median"),
            active_days_median=("active_days", "median"),
        )
        .reset_index()
        .sort_values(["study_week", "final_result"])
    )
    return summary


def plot_correlation_heatmap(spearman_matrix: pd.DataFrame) -> Path:
    corr = spearman_matrix.set_index("metric")
    plt.figure(figsize=(12, 9))
    sns.heatmap(
        corr,
        cmap="vlag",
        center=0,
        vmin=-1,
        vmax=1,
        annot=True,
        fmt=".2f",
        linewidths=0.4,
        cbar_kws={"label": "Spearman correlation"},
    )
    plt.title("Spearman correlation giữa các biến số chính")
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    return save_current_figure("numeric_spearman_correlation_heatmap.png")


def plot_click_score_scatter(df: pd.DataFrame) -> Path:
    plot_data = df.dropna(subset=["log_total_click", "weighted_score", "final_result"])
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=plot_data,
        x="log_total_click",
        y="weighted_score",
        hue="final_result",
        hue_order=FINAL_RESULT_ORDER,
        alpha=0.28,
        s=18,
        edgecolor=None,
    )
    plt.title("Log total click và weighted score theo final_result")
    plt.xlabel("Log1p(total_click)")
    plt.ylabel("Weighted score")
    plt.legend(title="final_result", bbox_to_anchor=(1.02, 1), loc="upper left")
    return save_current_figure("log_total_click_vs_weighted_score_scatter.png")


def plot_boxplot(
    df: pd.DataFrame,
    y_col: str,
    filename: str,
    title: str,
    ylabel: str,
) -> Path:
    plt.figure(figsize=(9, 5))
    sns.boxplot(
        data=df,
        x="final_result",
        y=y_col,
        order=FINAL_RESULT_ORDER,
        color="#72B7B2",
        showfliers=False,
    )
    plt.title(title)
    plt.xlabel("final_result")
    plt.ylabel(ylabel)
    return save_current_figure(filename)


def plot_late_submission_rate(metric_summary: pd.DataFrame) -> Path:
    data = metric_summary[metric_summary["metric"] == "late_submission_rate"].copy()
    plt.figure(figsize=(9, 5))
    sns.pointplot(
        data=data,
        x="final_result",
        y="mean",
        order=FINAL_RESULT_ORDER,
        color="#E45756",
    )
    plt.title("Tỷ lệ nộp muộn trung bình theo final_result")
    plt.xlabel("final_result")
    plt.ylabel("Late submission rate")
    return save_current_figure("late_submission_rate_by_final_result.png")


def plot_engagement_band_outcome(engagement_band: pd.DataFrame) -> Path:
    pivot = (
        engagement_band.pivot_table(
            index="engagement_band",
            columns="final_result",
            values="pct_within_band",
            aggfunc="sum",
            observed=False,
        )
        .reindex(columns=FINAL_RESULT_ORDER)
        .fillna(0)
    )
    ax = pivot.plot(
        kind="bar",
        stacked=True,
        figsize=(10, 6),
        color=["#4C78A8", "#54A24B", "#F58518", "#E45756"],
    )
    ax.set_title("Tỷ lệ final_result theo nhóm mức độ tương tác VLE")
    ax.set_xlabel("Nhóm total_click")
    ax.set_ylabel("Tỷ lệ trong nhóm")
    ax.legend(title="final_result", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=25, ha="right")
    return save_current_figure("final_result_by_engagement_band_stacked.png")


def plot_module_correlation_heatmap(module_correlations: pd.DataFrame) -> Path:
    value_col = "log_total_click_vs_weighted_score_spearman_corr"
    pivot = module_correlations.pivot(
        index="code_module",
        columns="code_presentation",
        values=value_col,
    )
    plt.figure(figsize=(8, 5))
    sns.heatmap(
        pivot,
        cmap="vlag",
        center=0,
        vmin=-1,
        vmax=1,
        annot=True,
        fmt=".2f",
        linewidths=0.4,
        cbar_kws={"label": "Spearman correlation"},
    )
    plt.title("Spearman log total click và weighted score theo module-presentation")
    plt.xlabel("code_presentation")
    plt.ylabel("code_module")
    return save_current_figure("module_presentation_click_score_spearman_heatmap.png")


def plot_assessment_score_boxplot(assessment_plot_sample: pd.DataFrame) -> Path:
    plot_data = assessment_plot_sample.dropna(subset=["score", "final_result"])
    plt.figure(figsize=(9, 5))
    sns.boxplot(
        data=plot_data,
        x="final_result",
        y="score",
        order=FINAL_RESULT_ORDER,
        color="#B279A2",
        showfliers=False,
    )
    plt.title("Điểm assessment theo final_result")
    plt.xlabel("final_result")
    plt.ylabel("Score")
    return save_current_figure("assessment_score_by_final_result_boxplot.png")


def plot_figures(
    student_metrics: pd.DataFrame,
    spearman_matrix: pd.DataFrame,
    metric_summary: pd.DataFrame,
    engagement_band: pd.DataFrame,
    module_correlations: pd.DataFrame,
    assessment_plot_sample: pd.DataFrame,
) -> list[Path]:
    figure_paths = [
        plot_correlation_heatmap(spearman_matrix),
        plot_click_score_scatter(student_metrics),
        plot_boxplot(
            student_metrics,
            "log_total_click",
            "log_total_click_by_final_result_boxplot.png",
            "Log total click theo final_result",
            "Log1p(total_click)",
        ),
        plot_boxplot(
            student_metrics,
            "weighted_score",
            "weighted_score_by_final_result_boxplot.png",
            "Weighted score theo final_result",
            "Weighted score",
        ),
        plot_boxplot(
            student_metrics,
            "active_days",
            "active_days_by_final_result_boxplot.png",
            "Số ngày active VLE theo final_result",
            "Active days",
        ),
        plot_late_submission_rate(metric_summary),
        plot_engagement_band_outcome(engagement_band),
        plot_module_correlation_heatmap(module_correlations),
        plot_assessment_score_boxplot(assessment_plot_sample),
    ]
    return figure_paths


def write_report(
    table_paths: dict[str, Path],
    figure_paths: list[Path],
    student_metrics: pd.DataFrame,
    key_correlations: pd.DataFrame,
    metric_summary: pd.DataFrame,
    engagement_band: pd.DataFrame,
    assessment_score_by_result: pd.DataFrame,
    module_correlations: pd.DataFrame,
) -> Path:
    table_lines = "\n".join(
        f"- `{table_link(path)}`" for path in sorted(table_paths.values(), key=lambda p: p.name)
    )
    figure_lines = "\n".join(
        f"- `{table_link(path)}`" for path in sorted(figure_paths, key=lambda p: p.name)
    )

    def corr_value(x_metric: str, y_metric: str, method: str = "spearman_corr") -> float:
        row = key_correlations[
            (key_correlations["x_metric"] == x_metric)
            & (key_correlations["y_metric"] == y_metric)
        ]
        return row[method].iloc[0] if len(row) else np.nan

    click_score_corr = corr_value("log_total_click", "weighted_score")
    active_score_corr = corr_value("active_days", "weighted_score")
    late_score_corr = corr_value("late_submission_rate", "weighted_score")
    click_success_corr = corr_value("log_total_click", "success_flag")

    summary_pivot = metric_summary.pivot_table(
        index="final_result", columns="metric", values="median", aggfunc="first"
    )
    distinction_click = summary_pivot.loc["Distinction", "total_click"]
    withdrawn_click = summary_pivot.loc["Withdrawn", "total_click"]
    distinction_score = summary_pivot.loc["Distinction", "weighted_score"]
    withdrawn_score = summary_pivot.loc["Withdrawn", "weighted_score"]
    distinction_active_days = summary_pivot.loc["Distinction", "active_days"]
    withdrawn_active_days = summary_pivot.loc["Withdrawn", "active_days"]

    high_band = engagement_band[engagement_band["engagement_band"].astype(str) == "High click"]
    high_success_pct = high_band[high_band["final_result"].isin(["Distinction", "Pass"])][
        "pct_within_band"
    ].sum()
    zero_band = engagement_band[engagement_band["engagement_band"].astype(str) == "0 click"]
    zero_withdrawn_pct = zero_band[zero_band["final_result"] == "Withdrawn"][
        "pct_within_band"
    ].sum()

    assessment_distinction = assessment_score_by_result[
        assessment_score_by_result["final_result"] == "Distinction"
    ].iloc[0]
    assessment_withdrawn = assessment_score_by_result[
        assessment_score_by_result["final_result"] == "Withdrawn"
    ].iloc[0]

    module_value_col = "log_total_click_vs_weighted_score_spearman_corr"
    strongest_module = module_correlations.sort_values(module_value_col, ascending=False).iloc[0]
    weakest_module = module_correlations.sort_values(module_value_col, ascending=True).iloc[0]

    report = f"""# Báo Cáo EDA - Phân Tích Tương Quan

## 1. Phạm vi

Phần này phân tích các mối liên hệ ban đầu giữa hoạt động VLE, kết quả assessment và `final_result` trên dữ liệu OULAD EDA-ready. Đơn vị chính là một bản ghi `student - module - presentation` trong `eda_student_summary`.

Nguồn dữ liệu:

- `ETL/eda_data/eda_student_summary.csv`
- `ETL/eda_data/eda_weekly_activity.csv`
- `ETL/eda_data/eda_assessment_progress.csv`

## 2. Lưu ý phương pháp

- Tương quan không có nghĩa là quan hệ nhân quả.
- `final_result` là biến phân loại, nên phần này dùng bảng nhóm, boxplot và stacked bar thay vì ép toàn bộ vào correlation matrix.
- `success_flag` chỉ là biến phụ trợ để sàng lọc nhanh, với `1` là `Distinction` hoặc `Pass`, `0` là `Fail` hoặc `Withdrawn`.
- Các tương quan với `score` hoặc `weighted_score` chỉ tính trên bản ghi có điểm quan sát được.
- Nếu sau này chọn bài toán dự báo sớm, cần giới hạn dữ liệu theo checkpoint thời gian để tránh leakage.

## 3. Nhận xét chính

- Spearman giữa `log1p(total_click)` và `weighted_score`: {fmt_float(click_score_corr)}.
- Spearman giữa `active_days` và `weighted_score`: {fmt_float(active_score_corr)}.
- Spearman giữa `late_submission_rate` và `weighted_score`: {fmt_float(late_score_corr)}.
- Spearman giữa `log1p(total_click)` và `success_flag`: {fmt_float(click_success_corr)}.
- Median `total_click` của `Distinction`: {fmt_int(distinction_click)}, trong khi `Withdrawn`: {fmt_int(withdrawn_click)}.
- Median `weighted_score` của `Distinction`: {fmt_float(distinction_score, 1)}, trong khi `Withdrawn`: {fmt_float(withdrawn_score, 1)}.
- Median `active_days` của `Distinction`: {fmt_float(distinction_active_days, 1)}, trong khi `Withdrawn`: {fmt_float(withdrawn_active_days, 1)}.
- Trong nhóm `High click`, tỷ lệ `Distinction` + `Pass` là {fmt_pct(high_success_pct)}.
- Trong nhóm `0 click`, tỷ lệ `Withdrawn` là {fmt_pct(zero_withdrawn_pct)}.
- Spearman `log1p(total_click)` và `weighted_score` cao nhất ở `{strongest_module["code_module"]}-{strongest_module["code_presentation"]}`: {fmt_float(strongest_module[module_value_col])}.
- Spearman `log1p(total_click)` và `weighted_score` thấp nhất ở `{weakest_module["code_module"]}-{weakest_module["code_presentation"]}`: {fmt_float(weakest_module[module_value_col])}.

Đọc diễn giải chi tiết tại [05_correlation_insights.md](05_correlation_insights.md).

## 4. Các phân tích đã hoàn thành

- Tính Pearson và Spearman correlation matrix cho các biến số chính.
- Tính tương quan giữa `total_click`, `log1p(total_click)`, `active_days`, nộp assessment và `weighted_score`.
- So sánh mức độ tương tác VLE giữa các nhóm `final_result`.
- So sánh điểm assessment và weighted score giữa các nhóm `final_result`.
- Phân tích quan hệ giữa active days, late submissions và kết quả cuối.
- Kiểm tra tương quan `log1p(total_click)` và `weighted_score` riêng theo từng module-presentation.
- Tạo nhóm mức độ tương tác VLE và so sánh tỷ lệ `final_result` theo từng nhóm.

## 5. Bảng đầu ra

{table_lines}

## 6. Biểu đồ đầu ra

{figure_lines}

## 7. Khuyến nghị dùng kết quả

- Dùng `log1p(total_click)`, `active_days`, `active_weeks`, `submitted_weight_sum`, `late_submission_rate` làm biến ứng viên cho phân tích sâu hơn.
- Khi so sánh giữa module-presentation, không dùng một hệ số tương quan toàn cục để kết luận cho tất cả môn học.
- Với `final_result`, ưu tiên bảng chéo, boxplot và phân tích theo nhóm hơn là mã hóa thứ bậc tùy tiện.
- Nếu làm dự báo sớm, tạo lại các biến tương tác VLE và assessment theo checkpoint trước khi đưa vào mô hình.
"""
    path = DOC_DIR / "05_correlation_report.md"
    path.write_text(report, encoding="utf-8")
    return path


def write_insights(
    key_correlations: pd.DataFrame,
    metric_summary: pd.DataFrame,
    engagement_band: pd.DataFrame,
    assessment_score_by_result: pd.DataFrame,
    module_correlations: pd.DataFrame,
) -> Path:
    def corr_value(x_metric: str, y_metric: str, method: str = "spearman_corr") -> float:
        row = key_correlations[
            (key_correlations["x_metric"] == x_metric)
            & (key_correlations["y_metric"] == y_metric)
        ]
        return row[method].iloc[0] if len(row) else np.nan

    click_score_corr = corr_value("log_total_click", "weighted_score")
    active_score_corr = corr_value("active_days", "weighted_score")
    submitted_weight_corr = corr_value("submitted_weight_sum", "weighted_score")
    late_score_corr = corr_value("late_submission_rate", "weighted_score")
    click_success_corr = corr_value("log_total_click", "success_flag")

    summary_pivot = metric_summary.pivot_table(
        index="final_result", columns="metric", values="median", aggfunc="first"
    )
    click_distinction = summary_pivot.loc["Distinction", "total_click"]
    click_withdrawn = summary_pivot.loc["Withdrawn", "total_click"]
    active_pass = summary_pivot.loc["Pass", "active_days"]
    active_fail = summary_pivot.loc["Fail", "active_days"]
    late_withdrawn = metric_summary[
        (metric_summary["final_result"] == "Withdrawn")
        & (metric_summary["metric"] == "late_submission_rate")
    ]["mean"].iloc[0]

    high_band = engagement_band[engagement_band["engagement_band"].astype(str) == "High click"]
    high_success_pct = high_band[high_band["final_result"].isin(["Distinction", "Pass"])][
        "pct_within_band"
    ].sum()
    zero_band = engagement_band[engagement_band["engagement_band"].astype(str) == "0 click"]
    zero_withdrawn_pct = zero_band[zero_band["final_result"] == "Withdrawn"][
        "pct_within_band"
    ].sum()

    score_distinction = assessment_score_by_result[
        assessment_score_by_result["final_result"] == "Distinction"
    ].iloc[0]
    score_fail = assessment_score_by_result[
        assessment_score_by_result["final_result"] == "Fail"
    ].iloc[0]
    score_withdrawn = assessment_score_by_result[
        assessment_score_by_result["final_result"] == "Withdrawn"
    ].iloc[0]

    module_value_col = "log_total_click_vs_weighted_score_spearman_corr"
    strongest_module = module_correlations.sort_values(module_value_col, ascending=False).iloc[0]
    weakest_module = module_correlations.sort_values(module_value_col, ascending=True).iloc[0]

    insights = f"""# EDA Insights - Phân Tích Tương Quan

## Cách đọc nhanh

File report chính cho biết đã tính những bảng và biểu đồ nào. File này diễn giải các mối liên hệ đáng chú ý, mức độ tin cậy khi đọc chúng, và cách dùng kết quả cho các bước EDA hoặc mô hình sau này.

## 1. Click VLE và điểm có quan hệ cùng chiều nhưng không tuyệt đối

Quan sát:

- Spearman giữa `log1p(total_click)` và `weighted_score` là {fmt_float(click_score_corr)}.
- Spearman giữa `active_days` và `weighted_score` là {fmt_float(active_score_corr)}.
- Median `total_click` của `Distinction` là {fmt_int(click_distinction)}, còn `Withdrawn` là {fmt_int(click_withdrawn)}.

Diễn giải:

- Quan hệ cùng chiều xuất hiện khá rõ: sinh viên tương tác VLE nhiều hơn và đều hơn thường có điểm weighted cao hơn.
- Tuy vậy, hệ số tương quan không đủ để nói click gây ra điểm cao. Sinh viên học tốt có thể chủ động học nhiều hơn, môn học có thiết kế khác nhau, hoặc assessment có trọng số khác nhau.
- Dùng `log1p(total_click)` hợp lý hơn `total_click` thô vì click lệch phải mạnh.

Ý nghĩa với phân tích sau:

- `log1p(total_click)`, `active_days`, `active_weeks` là feature ứng viên tốt.
- Khi trực quan hóa, nên dùng scatter với log click hoặc boxplot theo nhóm kết quả thay vì chỉ dùng histogram tổng thể.

## 2. Active days giúp nhìn hành vi đều đặn hơn tổng click

Quan sát:

- Spearman giữa `active_days` và `weighted_score` là {fmt_float(active_score_corr)}.
- Median `active_days` của `Pass` là {fmt_float(active_pass, 1)}, còn `Fail` là {fmt_float(active_fail, 1)}.

Diễn giải:

- Tổng click có thể tăng do vài phiên học rất dày. `active_days` cho biết sinh viên có duy trì hoạt động qua nhiều ngày hay không.
- Nếu một sinh viên có tổng click vừa phải nhưng active days cao, hành vi đó có thể khác với sinh viên click rất nhiều trong ít ngày.

Ý nghĩa với phân tích sau:

- Nên giữ cả intensity (`total_click`) và consistency (`active_days`, `active_weeks`).
- Phần phân tích xu hướng theo thời gian nên kiểm tra tuần nào nhóm `Fail` hoặc `Withdrawn` bắt đầu giảm active days.

## 3. Nộp bài và trọng số đã nộp cần được đọc cẩn thận

Quan sát:

- Spearman giữa `submitted_weight_sum` và `weighted_score` là {fmt_float(submitted_weight_corr)}.
- Spearman giữa `late_submission_rate` và `weighted_score` là {fmt_float(late_score_corr)}.
- Late submission rate trung bình của `Withdrawn` là {fmt_pct(late_withdrawn)}.

Diễn giải:

- `submitted_weight_sum` có quan hệ cùng chiều nhưng không quá mạnh với `weighted_score`. Biến này vẫn cần đọc cẩn thận vì weighted score được tính từ assessment đã nộp, nên có phần quan hệ cấu trúc.
- `late_submission_rate` có xu hướng ngược chiều với điểm, nhưng cũng chịu ảnh hưởng bởi việc sinh viên có nộp đủ bài hay không.

Ý nghĩa với phân tích sau:

- Khi dùng biến assessment, cần phân biệt feature hành vi thật với biến gần như cấu thành điểm.
- Với bài toán dự báo sớm, không dùng assessment sau checkpoint.

## 4. Nhóm mức độ tương tác cho thấy khác biệt rõ về final_result

Quan sát:

- Trong nhóm `High click`, tỷ lệ `Distinction` + `Pass` là {fmt_pct(high_success_pct)}.
- Trong nhóm `0 click`, tỷ lệ `Withdrawn` là {fmt_pct(zero_withdrawn_pct)}.
- Spearman giữa `log1p(total_click)` và `success_flag` là {fmt_float(click_success_corr)}.

Diễn giải:

- Nhóm không có click là tín hiệu mạnh của rủi ro rút môn hoặc kết quả xấu.
- Nhóm click cao có tỷ lệ kết quả tốt cao hơn, nhưng vẫn có sinh viên `Fail` hoặc `Withdrawn`. Vì vậy không nên dùng ngưỡng click đơn giản để kết luận một sinh viên chắc chắn thành công.

Ý nghĩa với phân tích sau:

- Nên tạo nhóm engagement band để dashboard dễ đọc.
- Với mô hình, engagement band có thể là biến giải thích dễ diễn giải hơn tổng click thô.

## 5. Điểm assessment khác biệt theo final_result

Quan sát:

- Median score assessment của `Distinction` là {fmt_float(score_distinction["score_median"], 1)}.
- Median score assessment của `Fail` là {fmt_float(score_fail["score_median"], 1)}.
- Median score assessment của `Withdrawn` là {fmt_float(score_withdrawn["score_median"], 1)}.

Diễn giải:

- Điểm assessment phân tách nhóm kết quả cuối khá rõ. Tuy nhiên, với `Withdrawn`, điểm chỉ quan sát được ở những bài sinh viên đã nộp trước khi rút hoặc dừng học.
- Vì vậy, thiếu điểm và số bài đã nộp quan trọng không kém bản thân điểm số.

Ý nghĩa với phân tích sau:

- Khi phân tích kết quả cuối, nên dùng kết hợp `avg_score`, `weighted_score`, `submitted_assessments`, `submitted_weight_sum`.
- Không nên so sánh điểm trung bình giữa nhóm nếu bỏ qua tỷ lệ missing score và số bài đã nộp.

## 6. Tương quan thay đổi theo module-presentation

Quan sát:

- Spearman `log1p(total_click)` và `weighted_score` cao nhất ở `{strongest_module["code_module"]}-{strongest_module["code_presentation"]}`: {fmt_float(strongest_module[module_value_col])}.
- Spearman `log1p(total_click)` và `weighted_score` thấp nhất ở `{weakest_module["code_module"]}-{weakest_module["code_presentation"]}`: {fmt_float(weakest_module[module_value_col])}.

Diễn giải:

- Không nên dùng một hệ số toàn cục để đại diện cho mọi môn học. Thiết kế môn học, loại assessment, mức độ dùng VLE và hành vi sinh viên khác nhau theo module-presentation.
- Nếu một module có tương quan thấp, điều đó không nhất thiết nghĩa là VLE không quan trọng. Có thể VLE không phản ánh toàn bộ hoạt động học, hoặc assessment đo năng lực khác.

Ý nghĩa với phân tích sau:

- Dashboard nên có filter theo module-presentation.
- Nếu xây mô hình, nên kiểm tra hiệu năng theo module-presentation thay vì chỉ nhìn metric toàn cục.

## 7. Kết luận cho bước tiếp theo

- Click, active days và assessment progress có tín hiệu liên quan đến kết quả học tập.
- Tín hiệu mạnh nhất có nguy cơ leakage thường nằm ở các biến assessment gần điểm cuối. Cần kiểm soát thời gian nếu dùng cho dự báo.
- Phần tiếp theo nên đi vào xu hướng theo thời gian để xem khác biệt xuất hiện từ tuần nào, thay vì chỉ nhìn tương quan tổng kỳ.
"""
    path = DOC_DIR / "05_correlation_insights.md"
    path.write_text(insights, encoding="utf-8")
    return path


def write_checklist() -> Path:
    checklist = """# Checklist EDA - Phân Tích Tương Quan

- [x] Tính tương quan giữa tổng `sum_click` và `score`.
- [x] So sánh mức độ tương tác VLE giữa các nhóm `final_result`.
- [x] So sánh điểm assessment giữa nhóm `Pass`, `Distinction`, `Fail`, `Withdrawn`.
- [x] Phân tích quan hệ giữa số ngày hoạt động VLE và kết quả cuối.
- [x] Phân tích quan hệ giữa nộp muộn assessment và kết quả cuối.
- [x] Kiểm tra tương quan riêng theo từng module-presentation.
- [x] Bổ sung bảng insight và diễn giải để tránh hiểu tương quan là nhân quả.

Minh chứng:

- Script: `EDA/src/05_analyze_correlations.py`
- Report: `EDA/docs/05-correlation/05_correlation_report.md`
- Insights: `EDA/docs/05-correlation/05_correlation_insights.md`
- Tables: `EDA/outputs/tables/05_correlation/`
- Figures: `EDA/outputs/figures/05_correlation/`
"""
    path = DOC_DIR / "05_correlation_checklist.md"
    path.write_text(checklist, encoding="utf-8")
    return path


def main() -> None:
    ensure_output_dirs()
    sns.set_theme(style="whitegrid", context="notebook")

    student_summary = read_csv(STUDENT_SUMMARY)
    weekly_activity = read_csv(WEEKLY_ACTIVITY)
    assessment_progress = read_csv(ASSESSMENT_PROGRESS)

    student_metrics = prepare_student_metrics(student_summary)

    pearson_matrix = correlation_matrix(student_metrics, "pearson")
    spearman_matrix = correlation_matrix(student_metrics, "spearman")
    key_correlations = build_key_correlations(student_metrics)
    metric_summary = summarize_metric_by_final_result(student_metrics)
    engagement_band = build_engagement_band_distribution(student_metrics)
    assessment_score_by_result, assessment_score_by_type, assessment_plot_sample = (
        summarize_assessment_scores(assessment_progress, student_metrics)
    )
    module_correlations = build_module_correlations(student_metrics)
    weekly_relationship = build_weekly_relationship_summary(weekly_activity, student_metrics)

    table_paths = {
        "numeric_pearson_correlation_matrix": write_table(
            pearson_matrix, "numeric_pearson_correlation_matrix.csv"
        ),
        "numeric_spearman_correlation_matrix": write_table(
            spearman_matrix, "numeric_spearman_correlation_matrix.csv"
        ),
        "key_correlations": write_table(key_correlations, "key_correlations.csv"),
        "metrics_by_final_result": write_table(
            metric_summary, "metrics_by_final_result.csv"
        ),
        "final_result_by_engagement_band": write_table(
            engagement_band, "final_result_by_engagement_band.csv"
        ),
        "assessment_score_by_final_result": write_table(
            assessment_score_by_result, "assessment_score_by_final_result.csv"
        ),
        "assessment_score_by_type_final_result": write_table(
            assessment_score_by_type, "assessment_score_by_type_final_result.csv"
        ),
        "module_presentation_correlations": write_table(
            module_correlations, "module_presentation_correlations.csv"
        ),
        "weekly_activity_by_final_result": write_table(
            weekly_relationship, "weekly_activity_by_final_result.csv"
        ),
    }

    figure_paths = plot_figures(
        student_metrics,
        spearman_matrix,
        metric_summary,
        engagement_band,
        module_correlations,
        assessment_plot_sample,
    )

    report_path = write_report(
        table_paths,
        figure_paths,
        student_metrics,
        key_correlations,
        metric_summary,
        engagement_band,
        assessment_score_by_result,
        module_correlations,
    )
    insights_path = write_insights(
        key_correlations,
        metric_summary,
        engagement_band,
        assessment_score_by_result,
        module_correlations,
    )
    checklist_path = write_checklist()

    print(f"Wrote {len(table_paths)} tables to {TABLE_DIR.relative_to(ROOT_DIR)}")
    print(f"Wrote {len(figure_paths)} figures to {FIGURE_DIR.relative_to(ROOT_DIR)}")
    print(f"Wrote report: {report_path.relative_to(ROOT_DIR)}")
    print(f"Wrote insights: {insights_path.relative_to(ROOT_DIR)}")
    print(f"Wrote checklist: {checklist_path.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
