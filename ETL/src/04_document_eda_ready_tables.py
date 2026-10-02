from __future__ import annotations

import csv
import time
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
STAGING_DIR = ROOT_DIR / "ETL" / "staging_data"
EDA_DIR = ROOT_DIR / "ETL" / "eda_data"
DOC_DIR = ROOT_DIR / "ETL" / "docs" / "04-eda-ready-tables"
REPORT_PATH = DOC_DIR / "04_eda_ready_tables_report.md"
CHECKLIST_PATH = DOC_DIR / "04_eda_ready_tables_checklist.md"


@dataclass(frozen=True)
class TableSpec:
    logical_name: str
    path: Path
    purpose: str
    owner: str


TABLES = [
    TableSpec(
        "stg_courses",
        STAGING_DIR / "courses.csv",
        "Danh mục module và presentation.",
        "Người 1",
    ),
    TableSpec(
        "stg_assessments",
        STAGING_DIR / "assessments.csv",
        "Danh mục bài đánh giá, hạn nộp và trọng số.",
        "Người 1",
    ),
    TableSpec(
        "stg_vle",
        STAGING_DIR / "vle.csv",
        "Danh mục tài nguyên VLE và loại hoạt động.",
        "Người 1",
    ),
    TableSpec(
        "stg_student_info",
        STAGING_DIR / "studentInfo.csv",
        "Thông tin nền và kết quả cuối của sinh viên.",
        "Người 1",
    ),
    TableSpec(
        "stg_student_registration",
        STAGING_DIR / "studentRegistration.csv",
        "Thông tin đăng ký và hủy đăng ký.",
        "Người 2",
    ),
    TableSpec(
        "stg_student_assessment",
        STAGING_DIR / "studentAssessment.csv",
        "Log bài đánh giá sinh viên đã nộp.",
        "Người 2",
    ),
    TableSpec(
        "stg_student_vle",
        STAGING_DIR / "studentVle.csv",
        "Log tương tác VLE đã gộp và loại duplicate dòng.",
        "Người 2",
    ),
    TableSpec(
        "eda_student_summary",
        EDA_DIR / "eda_student_summary.csv",
        "Bảng tổng hợp một dòng cho mỗi sinh viên trong từng module-presentation.",
        "Người 2",
    ),
    TableSpec(
        "eda_weekly_activity",
        EDA_DIR / "eda_weekly_activity.csv",
        "Bảng hoạt động VLE theo sinh viên và tuần học.",
        "Người 2",
    ),
    TableSpec(
        "eda_assessment_progress",
        EDA_DIR / "eda_assessment_progress.csv",
        "Bảng tiến độ nộp bài và điểm ở mức assessment.",
        "Người 2",
    ),
]


def relative_path(path: Path) -> str:
    return path.relative_to(ROOT_DIR).as_posix()


def csv_profile(path: Path) -> dict[str, object]:
    if not path.exists():
        return {
            "exists": False,
            "rows": None,
            "columns": None,
            "size": None,
            "headers": [],
        }

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        headers = next(reader, [])

    with path.open("rb") as f:
        newline_count = sum(block.count(b"\n") for block in iter(lambda: f.read(1024 * 1024), b""))

    rows = max(newline_count - 1, 0)
    return {
        "exists": True,
        "rows": rows,
        "columns": len(headers),
        "size": path.stat().st_size,
        "headers": headers,
    }


def format_number(value: object) -> str:
    if value is None:
        return "-"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def main() -> None:
    DOC_DIR.mkdir(parents=True, exist_ok=True)

    profiled = [(spec, csv_profile(spec.path)) for spec in TABLES]
    all_present = all(profile["exists"] for _, profile in profiled)

    report_lines = [
        "# Báo Cáo Tạo Bảng EDA-ready",
        f"Thời gian chạy: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 1. Cách hiểu bảng EDA-ready trong repo",
        "Các bảng `stg_*` được xem là tên logic của các file đã có trong `ETL/staging_data/`. Script này không copy/rename thêm để tránh nhân đôi dữ liệu lớn.",
        "",
        "Các bảng `eda_*` là output tổng hợp đã sinh ở `ETL/eda_data/` từ bước tạo biến phục vụ EDA.",
        "",
        "## 2. Danh sách bảng",
        "| Bảng logic | File vật lý | Owner | Số dòng | Số cột | Kích thước bytes | Mục đích |",
        "|---|---|---|---:|---:|---:|---|",
    ]

    for spec, profile in profiled:
        report_lines.append(
            "| "
            + " | ".join(
                [
                    f"`{spec.logical_name}`",
                    f"`{relative_path(spec.path)}`",
                    spec.owner,
                    format_number(profile["rows"]),
                    format_number(profile["columns"]),
                    format_number(profile["size"]),
                    spec.purpose,
                ]
            )
            + " |"
        )

    report_lines.extend(
        [
            "",
            "## 3. Quy ước sử dụng",
            "- Dùng `stg_*` khi cần dữ liệu đã staging nhưng vẫn gần với dữ liệu gốc.",
            "- Dùng `eda_student_summary` cho EDA theo sinh viên/module-presentation.",
            "- Dùng `eda_weekly_activity` cho EDA theo thời gian/tuần học.",
            "- Dùng `eda_assessment_progress` cho EDA về bài đánh giá, hạn nộp và điểm.",
            "- Các file trong `ETL/eda_data/*.csv` là output sinh ra local và đã được ignore để tránh commit dữ liệu dẫn xuất.",
            "",
            "## 4. Kết luận",
            f"- Số bảng logic cần có: {len(TABLES)}.",
            f"- Số bảng đang tồn tại: {sum(1 for _, profile in profiled if profile['exists'])}.",
            f"- Trạng thái: {'Hoàn tất' if all_present else 'Cần bổ sung file còn thiếu'}.",
            "",
        ]
    )

    checklist_lines = [
        "# Checklist 04 - Tạo Bảng EDA-ready",
        "",
        "Dựa trên danh sách công việc trong `ETL/elt_tasks.csv`, dưới đây là trạng thái các bảng EDA-ready.",
        "",
        "## Bảng staging logic",
    ]

    for spec, profile in profiled[:7]:
        mark = "x" if profile["exists"] else " "
        checklist_lines.append(
            f"- [{mark}] **Tạo {spec.logical_name}:** `{relative_path(spec.path)}`."
        )

    checklist_lines.extend(["", "## Bảng tổng hợp phục vụ EDA"])
    for spec, profile in profiled[7:]:
        mark = "x" if profile["exists"] else " "
        checklist_lines.append(
            f"- [{mark}] **Tạo {spec.logical_name}:** `{relative_path(spec.path)}`."
        )

    checklist_lines.extend(
        [
            "",
            f"**Trạng thái chung:** {'Hoàn tất' if all_present else 'Cần bổ sung'}",
            "",
        ]
    )

    REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")
    CHECKLIST_PATH.write_text("\n".join(checklist_lines), encoding="utf-8")

    print("Wrote ETL/docs/04-eda-ready-tables/04_eda_ready_tables_report.md")
    print("Wrote ETL/docs/04-eda-ready-tables/04_eda_ready_tables_checklist.md")


if __name__ == "__main__":
    main()
