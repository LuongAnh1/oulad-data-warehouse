"""Detect and classify missing values for OULAD EDA."""

from __future__ import annotations

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
TABLE_DIR = EDA_DIR / "outputs" / "tables" / "03_missing_values"
FIGURE_DIR = EDA_DIR / "outputs" / "figures" / "03_missing_values"
DOC_DIR = EDA_DIR / "docs" / "03-missing-values"

STAGING_TABLES = {
    "stg_courses": STAGING_DATA_DIR / "courses.csv",
    "stg_assessments": STAGING_DATA_DIR / "assessments.csv",
    "stg_vle": STAGING_DATA_DIR / "vle.csv",
    "stg_student_info": STAGING_DATA_DIR / "studentInfo.csv",
    "stg_student_registration": STAGING_DATA_DIR / "studentRegistration.csv",
    "stg_student_assessment": STAGING_DATA_DIR / "studentAssessment.csv",
    "stg_student_vle": STAGING_DATA_DIR / "studentVle.csv",
}

EDA_TABLES = {
    "eda_student_summary": EDA_DATA_DIR / "eda_student_summary.csv",
    "eda_weekly_activity": EDA_DATA_DIR / "eda_weekly_activity.csv",
    "eda_assessment_progress": EDA_DATA_DIR / "eda_assessment_progress.csv",
}

BACKGROUND_COLUMNS = [
    "gender",
    "region",
    "highest_education",
    "imd_band",
    "age_band",
    "disability",
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


def missing_mask(series: pd.Series) -> pd.Series:
    mask = series.isna()
    if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
        mask = mask | series.astype("string").str.strip().eq("")
    return mask.fillna(False)


def summarize_missing_by_column(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for table_name, df in tables.items():
        row_count = len(df)
        for column in df.columns:
            mask = missing_mask(df[column])
            missing_count = int(mask.sum())
            rows.append(
                {
                    "table_name": table_name,
                    "column_name": column,
                    "dtype": str(df[column].dtype),
                    "row_count": row_count,
                    "missing_count": missing_count,
                    "missing_pct": missing_count / row_count if row_count else 0,
                    "non_missing_count": row_count - missing_count,
                }
            )
    return pd.DataFrame(rows).sort_values(
        ["missing_pct", "missing_count", "table_name", "column_name"],
        ascending=[False, False, True, True],
    )


def summarize_missing_by_table(missing_by_column: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for table_name, group in missing_by_column.groupby("table_name", sort=False):
        row_count = int(group["row_count"].iloc[0])
        column_count = len(group)
        total_cells = row_count * column_count
        missing_cells = int(group["missing_count"].sum())
        rows.append(
            {
                "table_name": table_name,
                "row_count": row_count,
                "column_count": column_count,
                "total_cells": total_cells,
                "missing_cells": missing_cells,
                "missing_pct": missing_cells / total_cells if total_cells else 0,
                "columns_with_missing": int((group["missing_count"] > 0).sum()),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["missing_pct", "missing_cells"], ascending=[False, False]
    )


def analyze_date_unregistration(
    student_registration: pd.DataFrame, student_info: pd.DataFrame
) -> pd.DataFrame:
    keys = ["code_module", "code_presentation", "id_student"]
    reg = student_registration.merge(
        student_info[keys + ["final_result"]],
        on=keys,
        how="left",
    )
    reg["date_unregistration_missing"] = missing_mask(reg["date_unregistration"])
    summary = (
        reg.groupby("final_result", dropna=False)
        .agg(
            row_count=("id_student", "size"),
            missing_count=("date_unregistration_missing", "sum"),
        )
        .reset_index()
    )
    summary["missing_pct"] = summary["missing_count"] / summary["row_count"]
    summary["classification"] = summary["final_result"].map(
        {
            "Withdrawn": "Cần kiểm tra nếu thiếu vì sinh viên đã hủy đăng ký thường có ngày hủy.",
            "Pass": "Có thể hợp lệ vì sinh viên hoàn thành môn học.",
            "Distinction": "Có thể hợp lệ vì sinh viên hoàn thành môn học.",
            "Fail": "Có thể hợp lệ nếu sinh viên không hủy đăng ký.",
        }
    ).fillna("Cần kiểm tra do thiếu final_result.")
    return summary.sort_values("missing_pct", ascending=False)


def analyze_score_missing(assessment_progress: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    data = assessment_progress.copy()
    data["score_missing"] = missing_mask(data["score"])

    by_banked = (
        data.groupby("is_banked")
        .agg(
            row_count=("id_student", "size"),
            missing_count=("score_missing", "sum"),
        )
        .reset_index()
    )
    by_banked["missing_pct"] = by_banked["missing_count"] / by_banked["row_count"]

    by_type = (
        data.groupby("assessment_type")
        .agg(
            row_count=("id_student", "size"),
            missing_count=("score_missing", "sum"),
        )
        .reset_index()
    )
    by_type["missing_pct"] = by_type["missing_count"] / by_type["row_count"]
    return by_banked.sort_values("is_banked"), by_type.sort_values("missing_pct", ascending=False)


def analyze_date_submitted_missing(
    student_assessment: pd.DataFrame, assessment_progress: pd.DataFrame
) -> pd.DataFrame:
    rows = []
    for table_name, df in {
        "stg_student_assessment": student_assessment,
        "eda_assessment_progress": assessment_progress,
    }.items():
        missing_count = int(missing_mask(df["date_submitted"]).sum())
        rows.append(
            {
                "table_name": table_name,
                "row_count": len(df),
                "missing_count": missing_count,
                "missing_pct": missing_count / len(df) if len(df) else 0,
                "note": "Không có missing trong các dòng submission quan sát được."
                if missing_count == 0
                else "Cần kiểm tra dòng submission thiếu date_submitted.",
            }
        )
    return pd.DataFrame(rows)


def analyze_background_missing(student_info: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in BACKGROUND_COLUMNS:
        missing_count = int(missing_mask(student_info[column]).sum())
        rows.append(
            {
                "column_name": column,
                "row_count": len(student_info),
                "missing_count": missing_count,
                "missing_pct": missing_count / len(student_info) if len(student_info) else 0,
                "suggested_action": "Tạo nhóm Unknown/flag riêng nếu dùng làm biến phân tích."
                if missing_count
                else "Không cần xử lý missing.",
            }
        )
    return pd.DataFrame(rows).sort_values("missing_pct", ascending=False)


def build_missing_classification(
    missing_by_column: pd.DataFrame,
    date_unregistration: pd.DataFrame,
    score_by_banked: pd.DataFrame,
    date_submitted: pd.DataFrame,
    background_missing: pd.DataFrame,
    student_summary: pd.DataFrame,
) -> pd.DataFrame:
    lookup = missing_by_column.set_index(["table_name", "column_name"])

    def value(table_name: str, column_name: str, metric: str) -> float:
        if (table_name, column_name) not in lookup.index:
            return 0
        return float(lookup.loc[(table_name, column_name), metric])

    unregistration_missing = int(date_unregistration["missing_count"].sum())
    unregistration_rows = int(date_unregistration["row_count"].sum())
    withdrawn_missing = int(
        date_unregistration.loc[
            date_unregistration["final_result"].eq("Withdrawn"), "missing_count"
        ].sum()
    )

    score_missing = int(score_by_banked["missing_count"].sum())
    score_rows = int(score_by_banked["row_count"].sum())
    date_submitted_missing = int(date_submitted["missing_count"].sum())
    date_submitted_rows = int(date_submitted["row_count"].sum())
    imd_missing = int(
        background_missing.loc[
            background_missing["column_name"].eq("imd_band"), "missing_count"
        ].sum()
    )
    imd_rows = int(
        background_missing.loc[
            background_missing["column_name"].eq("imd_band"), "row_count"
        ].sum()
    )
    avg_score_missing = int(missing_mask(student_summary["avg_score"]).sum())
    weighted_score_missing = int(missing_mask(student_summary["weighted_score"]).sum())

    rows = [
        {
            "source_table": "stg_student_registration",
            "column_name": "date_unregistration",
            "missing_count": unregistration_missing,
            "missing_pct": unregistration_missing / unregistration_rows if unregistration_rows else 0,
            "classification": "Missing hợp lệ theo nghiệp vụ ở phần lớn trường hợp.",
            "suggested_action": "Diễn giải là không hủy đăng ký; kiểm tra riêng các dòng Withdrawn bị thiếu ngày hủy.",
            "attention_level": "medium" if withdrawn_missing else "low",
        },
        {
            "source_table": "eda_assessment_progress",
            "column_name": "score",
            "missing_count": score_missing,
            "missing_pct": score_missing / score_rows if score_rows else 0,
            "classification": "Missing cần ghi chú khi phân tích điểm.",
            "suggested_action": "Tạo flag is_missing_score; không xóa tự động vì có thể liên quan tới bài chưa chấm hoặc bản ghi banked.",
            "attention_level": "medium" if score_missing else "low",
        },
        {
            "source_table": "stg_student_assessment / eda_assessment_progress",
            "column_name": "date_submitted",
            "missing_count": date_submitted_missing,
            "missing_pct": date_submitted_missing / date_submitted_rows if date_submitted_rows else 0,
            "classification": "Không thấy missing trong các dòng submission quan sát được.",
            "suggested_action": "Không dùng missing date_submitted để suy ra chưa nộp; cần so với danh sách assessment bắt buộc nếu phân tích non-submission.",
            "attention_level": "low",
        },
        {
            "source_table": "stg_student_info",
            "column_name": "imd_band",
            "missing_count": imd_missing,
            "missing_pct": imd_missing / imd_rows if imd_rows else 0,
            "classification": "Missing biến nền cần xử lý rõ ràng.",
            "suggested_action": "Giữ nhóm Unknown hoặc tạo flag is_missing_imd_band khi dùng trong phân tích/model.",
            "attention_level": "medium" if imd_missing else "low",
        },
        {
            "source_table": "eda_student_summary",
            "column_name": "avg_score",
            "missing_count": avg_score_missing,
            "missing_pct": avg_score_missing / len(student_summary) if len(student_summary) else 0,
            "classification": "Missing phát sinh từ việc không có điểm assessment để tính trung bình.",
            "suggested_action": "Giữ NaN và dùng kèm submitted_assessments/submitted_records khi phân tích.",
            "attention_level": "medium" if avg_score_missing else "low",
        },
        {
            "source_table": "eda_student_summary",
            "column_name": "weighted_score",
            "missing_count": weighted_score_missing,
            "missing_pct": weighted_score_missing / len(student_summary) if len(student_summary) else 0,
            "classification": "Missing phát sinh khi không có trọng số điểm đã nộp.",
            "suggested_action": "Không thay bằng 0 nếu 0 có nghĩa điểm thật; dùng flag hoặc phân nhóm no_submission.",
            "attention_level": "medium" if weighted_score_missing else "low",
        },
    ]

    for table_name, column_name in [
        ("stg_assessments", "date"),
        ("stg_vle", "week_from"),
        ("stg_vle", "week_to"),
    ]:
        missing_count = int(value(table_name, column_name, "missing_count"))
        row_count = int(value(table_name, column_name, "row_count"))
        if missing_count:
            rows.append(
                {
                    "source_table": table_name,
                    "column_name": column_name,
                    "missing_count": missing_count,
                    "missing_pct": missing_count / row_count if row_count else 0,
                    "classification": "Missing metadata cần ghi chú.",
                    "suggested_action": "Giữ nguyên ở EDA; kiểm tra lại nếu dùng cột này làm mốc thời gian.",
                    "attention_level": "medium",
                }
            )

    return pd.DataFrame(rows).sort_values(["attention_level", "missing_pct"], ascending=[True, False])


def save_current_figure(filename: str) -> Path:
    path = FIGURE_DIR / filename
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()
    return path


def create_figures(
    missing_by_table: pd.DataFrame,
    missing_by_column: pd.DataFrame,
    date_unregistration: pd.DataFrame,
    score_by_type: pd.DataFrame,
    background_missing: pd.DataFrame,
) -> list[Path]:
    figure_paths: list[Path] = []

    plt.figure(figsize=(10, 5))
    sns.barplot(
        data=missing_by_table,
        y="table_name",
        x="missing_pct",
        color="#4C78A8",
    )
    plt.title("Tỷ lệ missing theo bảng")
    plt.xlabel("Tỷ lệ missing trên toàn bộ ô dữ liệu")
    plt.ylabel("Bảng")
    figure_paths.append(save_current_figure("missing_rate_by_table.png"))

    missing_columns = missing_by_column[missing_by_column["missing_count"] > 0].copy()
    if len(missing_columns):
        matrix = missing_columns.pivot_table(
            index="table_name",
            columns="column_name",
            values="missing_pct",
            fill_value=0,
        )
        matrix = matrix.loc[matrix.max(axis=1).sort_values(ascending=False).index]
        matrix = matrix[matrix.max(axis=0).sort_values(ascending=False).index]
        plt.figure(figsize=(max(10, len(matrix.columns) * 0.8), max(5, len(matrix) * 0.45)))
        sns.heatmap(
            matrix,
            cmap="YlOrRd",
            annot=True,
            fmt=".0%",
            linewidths=0.5,
            cbar_kws={"label": "Tỷ lệ missing"},
        )
        plt.title("Heatmap missing value theo bảng và cột")
        plt.xlabel("Cột")
        plt.ylabel("Bảng")
        figure_paths.append(save_current_figure("missing_matrix_heatmap.png"))

    top_columns = missing_by_column[missing_by_column["missing_count"] > 0].head(20)
    plt.figure(figsize=(11, 7))
    if len(top_columns):
        plot_data = top_columns.assign(
            field=top_columns["table_name"] + "." + top_columns["column_name"]
        )
        sns.barplot(data=plot_data, y="field", x="missing_pct", color="#F58518")
    plt.title("Top cột có tỷ lệ missing cao")
    plt.xlabel("Tỷ lệ missing")
    plt.ylabel("Cột")
    figure_paths.append(save_current_figure("top_missing_columns.png"))

    unreg_plot = date_unregistration.copy()
    unreg_plot["observed_pct"] = 1 - unreg_plot["missing_pct"]
    unreg_melted = unreg_plot.melt(
        id_vars=["final_result"],
        value_vars=["missing_pct", "observed_pct"],
        var_name="status",
        value_name="pct",
    )
    unreg_matrix = unreg_melted.pivot(index="final_result", columns="status", values="pct")
    plt.figure(figsize=(6, 4))
    sns.heatmap(
        unreg_matrix,
        cmap="Blues",
        annot=True,
        fmt=".1%",
        linewidths=0.5,
        cbar=False,
    )
    plt.title("date_unregistration thiếu/có theo final_result")
    plt.xlabel("")
    plt.ylabel("final_result")
    figure_paths.append(save_current_figure("date_unregistration_missing_heatmap.png"))

    plt.figure(figsize=(8, 5))
    sns.barplot(
        data=date_unregistration,
        x="final_result",
        y="missing_pct",
        color="#E45756",
    )
    plt.title("Tỷ lệ thiếu date_unregistration theo final_result")
    plt.xlabel("final_result")
    plt.ylabel("Tỷ lệ thiếu date_unregistration")
    figure_paths.append(save_current_figure("date_unregistration_missing_by_final_result.png"))

    plt.figure(figsize=(8, 5))
    sns.barplot(
        data=score_by_type,
        x="assessment_type",
        y="missing_pct",
        color="#72B7B2",
    )
    plt.title("Tỷ lệ thiếu score theo assessment_type")
    plt.xlabel("assessment_type")
    plt.ylabel("Tỷ lệ thiếu score")
    figure_paths.append(save_current_figure("score_missing_by_assessment_type.png"))

    plt.figure(figsize=(8, 5))
    sns.barplot(
        data=background_missing,
        y="column_name",
        x="missing_pct",
        color="#B279A2",
    )
    plt.title("Tỷ lệ missing trong biến nền sinh viên")
    plt.xlabel("Tỷ lệ missing")
    plt.ylabel("Biến nền")
    figure_paths.append(save_current_figure("background_missing_rates.png"))

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
    missing_by_table: pd.DataFrame,
    date_unregistration: pd.DataFrame,
    score_by_banked: pd.DataFrame,
    date_submitted: pd.DataFrame,
    background_missing: pd.DataFrame,
    missing_classification: pd.DataFrame,
) -> Path:
    table_lines = "\n".join(
        f"- `{table_link(path)}`" for path in sorted(table_paths.values(), key=lambda p: p.name)
    )
    figure_lines = "\n".join(
        f"- `{table_link(path)}`" for path in sorted(figure_paths, key=lambda p: p.name)
    )

    top_table = missing_by_table.iloc[0]
    unregistration_missing = int(date_unregistration["missing_count"].sum())
    unregistration_rows = int(date_unregistration["row_count"].sum())
    withdrawn_missing = int(
        date_unregistration.loc[
            date_unregistration["final_result"].eq("Withdrawn"), "missing_count"
        ].sum()
    )
    score_missing = int(score_by_banked["missing_count"].sum())
    score_rows = int(score_by_banked["row_count"].sum())
    date_submitted_missing = int(date_submitted["missing_count"].sum())
    imd_row = background_missing[background_missing["column_name"].eq("imd_band")].iloc[0]
    medium_attention = missing_classification[
        missing_classification["attention_level"].eq("medium")
    ]

    report = f"""# Báo Cáo EDA - Phát Hiện Dữ Liệu Khuyết

## 1. Phạm vi

Phần này kiểm tra missing value trong các bảng staging và các bảng EDA-ready. Kết quả không tự động xóa hay điền dữ liệu thiếu. Mục tiêu là xác định missing nào có ý nghĩa nghiệp vụ và missing nào cần xử lý rõ ở bước phân tích sau.

## 2. Nhận xét chính

- Bảng có tỷ lệ missing trên toàn bộ ô dữ liệu cao nhất là `{top_table["table_name"]}` với {fmt_pct(top_table["missing_pct"])}.
- `date_unregistration` thiếu {fmt_int(unregistration_missing)} trên {fmt_int(unregistration_rows)} dòng. Đây chủ yếu là missing hợp lệ, vì sinh viên không hủy đăng ký thường không có ngày hủy.
- Trong nhóm `Withdrawn`, có {fmt_int(withdrawn_missing)} dòng thiếu `date_unregistration`. Nhóm này cần kiểm tra riêng nếu dùng ngày hủy đăng ký.
- `score` thiếu {fmt_int(score_missing)} trên {fmt_int(score_rows)} dòng assessment đã quan sát, chiếm {fmt_pct(score_missing / score_rows if score_rows else 0)}.
- `date_submitted` thiếu {fmt_int(date_submitted_missing)} dòng trong các bảng submission đang có.
- `imd_band` thiếu {fmt_int(imd_row["missing_count"])} dòng, chiếm {fmt_pct(imd_row["missing_pct"])} trong `studentInfo`.

Đọc diễn giải chi tiết tại [03_missing_values_insights.md](03_missing_values_insights.md).

## 3. Phân loại missing value

Các trường cần chú ý mức trung bình:

{chr(10).join(f'- `{row.source_table}.{row.column_name}`: {fmt_int(row.missing_count)} missing. {row.suggested_action}' for row in medium_attention.itertuples(index=False))}

Diễn giải quan trọng:

- Không nên xóa dòng chỉ vì `date_unregistration` bị thiếu.
- Không nên thay `score`, `avg_score` hoặc `weighted_score` bị thiếu bằng 0 nếu 0 có thể là điểm thật.
- Với biến nền như `imd_band`, nên giữ nhóm `Unknown` hoặc tạo flag missing khi dùng cho phân tích/model.
- `date_submitted` không bị thiếu trong các submission quan sát được. Việc chưa nộp bài không được biểu diễn bằng một dòng có `date_submitted` rỗng, mà thường là không có bản ghi submission tương ứng.

## 4. Bảng đầu ra

{table_lines}

## 5. Biểu đồ đầu ra

{figure_lines}

## 6. Khuyến nghị xử lý

- Giữ nguyên missing có ý nghĩa nghiệp vụ và ghi rõ cách diễn giải.
- Tạo flag như `is_unregistered`, `is_missing_score`, `is_missing_imd_band` nếu các biến này được dùng trong phân tích sâu hơn.
- Khi phân tích điểm, luôn đi kèm số bài đã nộp hoặc số assessment có điểm để tránh hiểu nhầm sinh viên không có điểm với sinh viên điểm 0.
- Nếu nhóm chọn bài toán cảnh báo sớm, cần phân biệt dữ liệu vắng mặt do chưa phát sinh ở thời điểm checkpoint với dữ liệu thật sự thiếu.
"""
    path = DOC_DIR / "03_missing_values_report.md"
    path.write_text(report, encoding="utf-8")
    return path


def write_insights(
    missing_by_table: pd.DataFrame,
    date_unregistration: pd.DataFrame,
    score_by_type: pd.DataFrame,
    date_submitted: pd.DataFrame,
    background_missing: pd.DataFrame,
    missing_classification: pd.DataFrame,
) -> Path:
    top_table = missing_by_table.iloc[0]
    withdrawn_row = date_unregistration[
        date_unregistration["final_result"].eq("Withdrawn")
    ].iloc[0]
    score_top = score_by_type.sort_values("missing_pct", ascending=False).iloc[0]
    date_submitted_missing = int(date_submitted["missing_count"].sum())
    imd_row = background_missing[background_missing["column_name"].eq("imd_band")].iloc[0]
    medium_attention = missing_classification[
        missing_classification["attention_level"].eq("medium")
    ]

    insights = f"""# EDA Insights - Phát Hiện Dữ Liệu Khuyết

## Cách đọc nhanh

File report chính cho biết missing nằm ở đâu. File này giải thích missing đó có ý nghĩa gì trong OULAD và nên xử lý thế nào khi phân tích tiếp.

## 1. Missing không phải lúc nào cũng là lỗi

Quan sát:

- Bảng có tỷ lệ missing cao nhất là `{top_table["table_name"]}` với {fmt_pct(top_table["missing_pct"])}.
- Nhiều missing tập trung ở các cột có ý nghĩa nghiệp vụ hoặc metadata, ví dụ `date_unregistration`, `week_from`, `week_to`.

Diễn giải:

- Missing trong OULAD không nên được xử lý máy móc bằng cách xóa dòng hoặc điền 0.
- Một số cột thiếu vì sự kiện không xảy ra. Ví dụ sinh viên không rút môn thì không có `date_unregistration`.
- Một số cột thiếu vì metadata của tài nguyên hoặc assessment không đầy đủ. Các cột này chỉ cần xử lý mạnh nếu dùng trực tiếp trong phân tích thời gian.

Ý nghĩa với phân tích sau:

- Cần phân loại missing trước khi xử lý.
- Missing có ý nghĩa nghiệp vụ nên được giữ lại và chuyển thành flag hoặc nhóm riêng.

## 2. `date_unregistration`

Quan sát:

- Với nhóm `Withdrawn`, có {fmt_int(withdrawn_row["missing_count"])} dòng thiếu `date_unregistration`, chiếm {fmt_pct(withdrawn_row["missing_pct"])}.

Diễn giải:

- `date_unregistration` thiếu ở nhóm `Pass`, `Distinction`, `Fail` phần lớn là hợp lý vì sinh viên không hủy đăng ký.
- Riêng nhóm `Withdrawn` mà thiếu `date_unregistration` mới cần chú ý, vì nhóm này đáng lẽ thường có ngày hủy.

Ý nghĩa với phân tích sau:

- Có thể tạo biến `is_unregistered` từ việc `date_unregistration` có giá trị hay không.
- Khi phân tích thời điểm rút môn, cần loại riêng hoặc kiểm tra 93 dòng `Withdrawn` thiếu ngày hủy.

## 3. `score`

Quan sát:

- Missing score tập trung nhiều nhất ở assessment type `{score_top["assessment_type"]}`, với {fmt_int(score_top["missing_count"])} dòng.

Diễn giải:

- Score bị thiếu không nên hiểu là điểm 0.
- Missing score có thể đến từ bài chưa có điểm, bài không nộp được biểu diễn gián tiếp, hoặc bản ghi có trạng thái đặc biệt như banked.

Ý nghĩa với phân tích sau:

- Nên tạo flag `is_missing_score`.
- Khi tính điểm trung bình hoặc weighted score, cần dùng thêm số bài đã nộp và tổng trọng số đã nộp.
- Không thay score missing bằng 0 nếu mục tiêu là mô tả kết quả học thật.

## 4. `date_submitted`

Quan sát:

- `date_submitted` thiếu {fmt_int(date_submitted_missing)} dòng trong các submission quan sát được.

Diễn giải:

- Không có missing `date_submitted` không có nghĩa là mọi sinh viên đều nộp đủ bài.
- Trong dữ liệu dạng submission, sinh viên không nộp một assessment thường có thể không xuất hiện dòng tương ứng trong `studentAssessment`, thay vì xuất hiện một dòng có ngày nộp rỗng.

Ý nghĩa với phân tích sau:

- Muốn phát hiện không nộp bài, cần so danh sách assessment bắt buộc với từng student-module-presentation.
- Đây là phần nên làm tiếp ở phân tích chất lượng dữ liệu hoặc phân tích hành vi assessment.

## 5. Biến nền sinh viên

Quan sát:

- `imd_band` thiếu {fmt_int(imd_row["missing_count"])} dòng, chiếm {fmt_pct(imd_row["missing_pct"])}.

Diễn giải:

- `imd_band` là biến nền liên quan tới điều kiện kinh tế-xã hội, nên missing ở biến này cần được ghi rõ thay vì xóa dòng.
- Nếu xóa các dòng thiếu `imd_band`, phân tích có thể lệch mẫu vì nhóm thiếu thông tin nền có thể không ngẫu nhiên.

Ý nghĩa với phân tích sau:

- Nên tạo nhóm `Unknown` hoặc flag `is_missing_imd_band`.
- Khi so sánh kết quả theo `imd_band`, cần hiển thị cả nhóm missing.

## 6. Các trường cần ưu tiên theo dõi

{chr(10).join(f'- `{row.source_table}.{row.column_name}`: {fmt_int(row.missing_count)} missing. {row.classification}' for row in medium_attention.itertuples(index=False))}
"""
    path = DOC_DIR / "03_missing_values_insights.md"
    path.write_text(insights, encoding="utf-8")
    return path


def write_checklist() -> Path:
    checklist = """# Checklist EDA - Phát Hiện Dữ Liệu Khuyết

- [x] Thống kê số lượng missing value theo từng cột.
- [x] Tính tỷ lệ missing value theo từng bảng.
- [x] Kiểm tra `date_unregistration` bị thiếu.
- [x] Kiểm tra `score` bị thiếu.
- [x] Kiểm tra `date_submitted` bị thiếu.
- [x] Kiểm tra missing value trong các biến nền như `imd_band`.
- [x] Phân loại missing value hợp lệ và missing cần xử lý.

Minh chứng:

- Script: `EDA/src/03_detect_missing_values.py`
- Report: `EDA/docs/03-missing-values/03_missing_values_report.md`
- Insights: `EDA/docs/03-missing-values/03_missing_values_insights.md`
- Tables: `EDA/outputs/tables/03_missing_values/`
- Figures: `EDA/outputs/figures/03_missing_values/`
"""
    path = DOC_DIR / "03_missing_values_checklist.md"
    path.write_text(checklist, encoding="utf-8")
    return path


def main() -> None:
    ensure_output_dirs()
    sns.set_theme(style="whitegrid", context="notebook")

    staging_tables = {name: read_csv(path) for name, path in STAGING_TABLES.items()}
    eda_tables = {name: read_csv(path) for name, path in EDA_TABLES.items()}
    all_tables = {**staging_tables, **eda_tables}

    student_info = staging_tables["stg_student_info"]
    student_registration = staging_tables["stg_student_registration"]
    student_assessment = staging_tables["stg_student_assessment"]
    assessment_progress = eda_tables["eda_assessment_progress"]
    student_summary = eda_tables["eda_student_summary"]

    missing_by_column = summarize_missing_by_column(all_tables)
    missing_by_table = summarize_missing_by_table(missing_by_column)
    date_unregistration = analyze_date_unregistration(student_registration, student_info)
    score_by_banked, score_by_type = analyze_score_missing(assessment_progress)
    date_submitted = analyze_date_submitted_missing(student_assessment, assessment_progress)
    background_missing = analyze_background_missing(student_info)
    missing_classification = build_missing_classification(
        missing_by_column=missing_by_column,
        date_unregistration=date_unregistration,
        score_by_banked=score_by_banked,
        date_submitted=date_submitted,
        background_missing=background_missing,
        student_summary=student_summary,
    )

    output_tables = {
        "missing_by_column.csv": missing_by_column,
        "missing_by_table.csv": missing_by_table,
        "date_unregistration_missing_by_final_result.csv": date_unregistration,
        "score_missing_by_banked.csv": score_by_banked,
        "score_missing_by_assessment_type.csv": score_by_type,
        "date_submitted_missing_summary.csv": date_submitted,
        "background_missing_summary.csv": background_missing,
        "missing_classification.csv": missing_classification,
    }
    table_paths = {
        filename: write_table(dataframe, filename)
        for filename, dataframe in output_tables.items()
    }
    figure_paths = create_figures(
        missing_by_table=missing_by_table,
        missing_by_column=missing_by_column,
        date_unregistration=date_unregistration,
        score_by_type=score_by_type,
        background_missing=background_missing,
    )
    report_path = write_report(
        table_paths=table_paths,
        figure_paths=figure_paths,
        missing_by_table=missing_by_table,
        date_unregistration=date_unregistration,
        score_by_banked=score_by_banked,
        date_submitted=date_submitted,
        background_missing=background_missing,
        missing_classification=missing_classification,
    )
    insights_path = write_insights(
        missing_by_table=missing_by_table,
        date_unregistration=date_unregistration,
        score_by_type=score_by_type,
        date_submitted=date_submitted,
        background_missing=background_missing,
        missing_classification=missing_classification,
    )
    checklist_path = write_checklist()

    print(f"Wrote {len(table_paths)} tables to {TABLE_DIR.relative_to(ROOT_DIR)}")
    print(f"Wrote {len(figure_paths)} figures to {FIGURE_DIR.relative_to(ROOT_DIR)}")
    print(f"Wrote report: {report_path.relative_to(ROOT_DIR)}")
    print(f"Wrote insights: {insights_path.relative_to(ROOT_DIR)}")
    print(f"Wrote checklist: {checklist_path.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
