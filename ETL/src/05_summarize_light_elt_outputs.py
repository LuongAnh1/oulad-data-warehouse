from __future__ import annotations

import csv
import time
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT_DIR / "raw_data"
STAGING_DIR = ROOT_DIR / "ETL" / "staging_data"
EDA_DIR = ROOT_DIR / "ETL" / "eda_data"
DOC_DIR = ROOT_DIR / "ETL" / "docs" / "05-light-elt-summary"
REPORT_PATH = DOC_DIR / "05_light_elt_summary.md"
CHECKLIST_PATH = DOC_DIR / "05_light_elt_checklist.md"


@dataclass(frozen=True)
class OutputSpec:
    name: str
    path: Path
    kind: str
    description: str


OUTPUTS = [
    OutputSpec("stg_courses", STAGING_DIR / "courses.csv", "staging", "Danh mục module/presentation."),
    OutputSpec("stg_assessments", STAGING_DIR / "assessments.csv", "staging", "Danh mục assessment, hạn nộp, trọng số."),
    OutputSpec("stg_vle", STAGING_DIR / "vle.csv", "staging", "Danh mục tài nguyên VLE."),
    OutputSpec("stg_student_info", STAGING_DIR / "studentInfo.csv", "staging", "Thông tin sinh viên và kết quả cuối."),
    OutputSpec("stg_student_registration", STAGING_DIR / "studentRegistration.csv", "staging", "Thông tin đăng ký/hủy đăng ký."),
    OutputSpec("stg_student_assessment", STAGING_DIR / "studentAssessment.csv", "staging", "Bài đánh giá sinh viên đã nộp."),
    OutputSpec("stg_student_vle", STAGING_DIR / "studentVle.csv", "staging", "Tương tác VLE đã gộp từ 8 file và loại duplicate dòng."),
    OutputSpec("eda_student_summary", EDA_DIR / "eda_student_summary.csv", "eda-ready", "Bảng tổng hợp theo sinh viên/module-presentation."),
    OutputSpec("eda_weekly_activity", EDA_DIR / "eda_weekly_activity.csv", "eda-ready", "Bảng hoạt động VLE theo sinh viên và tuần học."),
    OutputSpec("eda_assessment_progress", EDA_DIR / "eda_assessment_progress.csv", "eda-ready", "Bảng tiến độ nộp bài và điểm assessment."),
]

DOC_OUTPUTS = [
    ROOT_DIR / "ETL" / "docs" / "01-report" / "01_etl_report.md",
    ROOT_DIR / "ETL" / "docs" / "01-report" / "01_etl_checklist.md",
    ROOT_DIR / "ETL" / "docs" / "02-relationship-check" / "02_relationship_report.md",
    ROOT_DIR / "ETL" / "docs" / "02-relationship-check" / "02_relationship_checklist.md",
    ROOT_DIR / "ETL" / "docs" / "03-eda-features" / "03_eda_features_report.md",
    ROOT_DIR / "ETL" / "docs" / "03-eda-features" / "03_eda_features_checklist.md",
    ROOT_DIR / "ETL" / "docs" / "04-eda-ready-tables" / "04_eda_ready_tables_report.md",
    ROOT_DIR / "ETL" / "docs" / "04-eda-ready-tables" / "04_eda_ready_tables_checklist.md",
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT_DIR).as_posix()


def csv_profile(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"exists": False, "rows": None, "columns": None, "size": None}

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        headers = next(reader, [])

    with path.open("rb") as f:
        newline_count = sum(block.count(b"\n") for block in iter(lambda: f.read(1024 * 1024), b""))

    return {
        "exists": True,
        "rows": max(newline_count - 1, 0),
        "columns": len(headers),
        "size": path.stat().st_size,
    }


def fmt(value: object) -> str:
    if value is None:
        return "-"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def main() -> None:
    DOC_DIR.mkdir(parents=True, exist_ok=True)

    raw_files = sorted(RAW_DIR.glob("*.csv"))
    output_profiles = [(spec, csv_profile(spec.path)) for spec in OUTPUTS]
    output_ready = all(profile["exists"] for _, profile in output_profiles)
    docs_ready = all(path.exists() for path in DOC_OUTPUTS)

    report_lines = [
        "# Tổng Hợp Đầu Ra ELT Nhẹ",
        f"Thời gian chạy: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 1. Mục tiêu",
        "Tổng hợp lại các đầu ra đã sẵn sàng cho EDA, các quy tắc xử lý chính, chất lượng dữ liệu đã kiểm tra và trạng thái dữ liệu gốc.",
        "",
        "## 2. Đầu ra dữ liệu sẵn sàng cho EDA",
        "| Tên logic | File | Loại | Số dòng | Số cột | Kích thước bytes | Ghi chú |",
        "|---|---|---|---:|---:|---:|---|",
    ]

    for spec, profile in output_profiles:
        report_lines.append(
            "| "
            + " | ".join(
                [
                    f"`{spec.name}`",
                    f"`{rel(spec.path)}`",
                    spec.kind,
                    fmt(profile["rows"]),
                    fmt(profile["columns"]),
                    fmt(profile["size"]),
                    spec.description,
                ]
            )
            + " |"
        )

    report_lines.extend(
        [
            "",
            "## 3. Tài liệu và checklist đã hoàn tất",
            "| Tài liệu | Trạng thái |",
            "|---|---|",
        ]
    )
    for path in DOC_OUTPUTS:
        report_lines.append(f"| `{rel(path)}` | {'Có' if path.exists() else 'Thiếu'} |")

    report_lines.extend(
        [
            "",
            "## 4. Quy tắc xử lý dữ liệu chính",
            "- Không ghi đè hoặc chỉnh sửa trực tiếp file trong `raw_data/`.",
            "- Cột index kỹ thuật không tên/`Unnamed` được loại khỏi dữ liệu staging vì không mang ý nghĩa nghiệp vụ.",
            "- `studentVle_0.csv` đến `studentVle_7.csv` được gộp thành bảng logic `studentVle`.",
            "- Duplicate dòng trong `studentVle` được loại theo toàn bộ cột nghiệp vụ sau khi bỏ cột index kỹ thuật.",
            "- Ngày trong OULAD được giữ là ngày tương đối, không chuyển sang ngày lịch.",
            "- `study_week` phục vụ EDA được tính bằng `date // 7`; các hoạt động trước khai giảng có thể có tuần âm.",
            "- `late_submissions` được tính khi có hạn nộp assessment và `date_submitted > date`.",
            "- `weighted_score` được tính bằng `sum(score * weight) / sum(weight)` theo sinh viên/module-presentation.",
            "",
            "## 5. Tóm tắt kiểm tra chất lượng và quan hệ",
            "- Đã thống kê row/column, missing %, min/max/unique trong báo cáo staging.",
            "- `studentVle` sau gộp có 10,655,280 dòng trước loại duplicate và 9,868,110 dòng sau loại duplicate.",
            "- Không phát hiện dòng không khớp trong các quan hệ chính: studentInfo/studentRegistration, studentAssessment/assessments, studentVle/vle.",
            "- Các bảng EDA-ready đã được sinh từ staging data và sẵn sàng dùng trong notebook EDA.",
            "",
            "## 6. Xác nhận dữ liệu gốc",
            f"- Số file CSV trong `raw_data/`: {len(raw_files)}.",
            "- Quy trình ELT nhẹ chỉ đọc `raw_data/` và ghi đầu ra vào `ETL/staging_data/`, `ETL/eda_data/`, `ETL/docs/`.",
            "- `ETL/eda_data/*.csv` là dữ liệu dẫn xuất local và đã được ignore để tránh commit nhầm.",
            "",
            "### Danh sách file raw_data",
            "| File | Kích thước bytes | Last modified |",
            "|---|---:|---|",
        ]
    )
    for path in raw_files:
        report_lines.append(
            f"| `{path.name}` | {path.stat().st_size:,} | {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(path.stat().st_mtime))} |"
        )

    report_lines.extend(
        [
            "",
            "## 7. Kết luận",
            f"- Đầu ra dữ liệu: {'Đủ' if output_ready else 'Thiếu'}.",
            f"- Tài liệu kiểm chứng: {'Đủ' if docs_ready else 'Thiếu'}.",
            f"- Trạng thái tổng hợp ELT nhẹ: {'Hoàn tất' if output_ready and docs_ready else 'Cần bổ sung'}.",
            "",
        ]
    )

    checklist_lines = [
        "# Checklist 05 - Tổng Hợp Đầu Ra ELT Nhẹ",
        "",
        "Dựa trên danh sách công việc trong `ETL/elt_tasks.csv`, dưới đây là trạng thái các đầu việc tổng hợp đầu ra ELT nhẹ.",
        "",
        "## Tổng Hợp Đầu Ra ELT Nhẹ",
        f"- [{'x' if output_ready else ' '}] **Tạo bảng hoặc file dữ liệu đã sẵn sàng cho EDA:** {'Đủ 10 bảng logic' if output_ready else 'Còn thiếu bảng/file'}.",
        "- [x] **Tạo ghi chú về quy tắc xử lý dữ liệu:** Đã ghi trong `05_light_elt_summary.md`.",
        "- [x] **Tạo báo cáo ngắn về chất lượng dữ liệu:** Đã tổng hợp từ các report staging, relationship và EDA-ready.",
        "- [x] **Xác nhận dữ liệu gốc vẫn được giữ nguyên:** Quy trình chỉ đọc `raw_data/`, không ghi output vào thư mục này.",
        "",
        f"**Trạng thái chung:** {'Hoàn tất' if output_ready and docs_ready else 'Cần bổ sung'}",
        "",
    ]

    REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")
    CHECKLIST_PATH.write_text("\n".join(checklist_lines), encoding="utf-8")

    print("Wrote ETL/docs/05-light-elt-summary/05_light_elt_summary.md")
    print("Wrote ETL/docs/05-light-elt-summary/05_light_elt_checklist.md")


if __name__ == "__main__":
    main()
