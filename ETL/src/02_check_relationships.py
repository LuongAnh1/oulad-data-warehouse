from __future__ import annotations

import time
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
STAGING_DIR = ROOT_DIR / "ETL" / "staging_data"
DOC_DIR = ROOT_DIR / "ETL" / "docs" / "02-relationship-check"
REPORT_PATH = DOC_DIR / "02_relationship_report.md"
CHECKLIST_PATH = DOC_DIR / "02_relationship_checklist.md"

STUDENT_KEY = ["code_module", "code_presentation", "id_student"]
VLE_KEY = ["id_site", "code_module", "code_presentation"]


def read_staging_csv(name: str, usecols: list[str]) -> pd.DataFrame:
    return pd.read_csv(
        STAGING_DIR / f"{name}.csv",
        usecols=usecols,
        dtype=str,
        low_memory=False,
    )


def key_set(df: pd.DataFrame, cols: list[str]) -> set[tuple[str, ...]]:
    return set(df[cols].itertuples(index=False, name=None))


def duplicate_count(df: pd.DataFrame, cols: list[str]) -> int:
    return int(df.duplicated(subset=cols).sum())


def count_unmatched(
    df: pd.DataFrame,
    cols: list[str],
    ref_keys: set[tuple[str, ...]],
    sample_limit: int = 10,
) -> tuple[int, list[dict[str, str]]]:
    unmatched = 0
    samples: list[dict[str, str]] = []
    seen_samples: set[tuple[str, ...]] = set()

    for values in df[cols].itertuples(index=False, name=None):
        if values not in ref_keys:
            unmatched += 1
            if len(samples) < sample_limit and values not in seen_samples:
                samples.append(dict(zip(cols, values)))
                seen_samples.add(values)

    return unmatched, samples


def count_student_vle_relationships(
    vle_keys: set[tuple[str, str, str]],
    student_info_keys: set[tuple[str, str, str]],
    registration_keys: set[tuple[str, str, str]],
    sample_limit: int = 10,
    chunksize: int = 500_000,
) -> dict[str, object]:
    result = {
        "rows": 0,
        "unmatched_vle": 0,
        "unmatched_student_info": 0,
        "unmatched_registration": 0,
        "samples_vle": [],
        "samples_student_info": [],
        "samples_registration": [],
    }
    sample_seen = {
        "samples_vle": set(),
        "samples_student_info": set(),
        "samples_registration": set(),
    }

    def add_sample(bucket: str, cols: list[str], values: tuple[str, ...]) -> None:
        samples = result[bucket]
        if len(samples) >= sample_limit or values in sample_seen[bucket]:
            return
        samples.append(dict(zip(cols, values)))
        sample_seen[bucket].add(values)

    for chunk in pd.read_csv(
        STAGING_DIR / "studentVle.csv",
        usecols=["code_module", "code_presentation", "id_student", "id_site"],
        dtype=str,
        chunksize=chunksize,
        low_memory=False,
    ):
        chunk = chunk[["code_module", "code_presentation", "id_student", "id_site"]]
        for code_module, code_presentation, id_student, id_site in chunk.itertuples(
            index=False, name=None
        ):
            result["rows"] += 1

            vle_key = (id_site, code_module, code_presentation)
            if vle_key not in vle_keys:
                result["unmatched_vle"] += 1
                add_sample("samples_vle", VLE_KEY, vle_key)

            student_key = (code_module, code_presentation, id_student)
            if student_key not in student_info_keys:
                result["unmatched_student_info"] += 1
                add_sample("samples_student_info", STUDENT_KEY, student_key)

            if student_key not in registration_keys:
                result["unmatched_registration"] += 1
                add_sample("samples_registration", STUDENT_KEY, student_key)

    return result


def sample_block(title: str, samples: list[dict[str, str]]) -> list[str]:
    lines = [f"#### {title}"]
    if not samples:
        lines.append("Không có dòng không khớp.")
        return lines

    cols = list(samples[0].keys())
    lines.append("| " + " | ".join(cols) + " |")
    lines.append("|" + "|".join(["---"] * len(cols)) + "|")
    for row in samples:
        lines.append("| " + " | ".join(str(row[col]) for col in cols) + " |")
    return lines


def yes_no(condition: bool) -> str:
    return "Đạt" if condition else "Cần kiểm tra"


def main() -> None:
    start = time.time()
    DOC_DIR.mkdir(parents=True, exist_ok=True)

    student_info = read_staging_csv("studentInfo", STUDENT_KEY)
    registration = read_staging_csv("studentRegistration", STUDENT_KEY)
    assessments = read_staging_csv(
        "assessments", ["id_assessment", "code_module", "code_presentation"]
    )
    student_assessment = read_staging_csv(
        "studentAssessment", ["id_assessment", "id_student"]
    )
    vle = read_staging_csv("vle", VLE_KEY)

    student_info_keys = key_set(student_info, STUDENT_KEY)
    registration_keys = key_set(registration, STUDENT_KEY)
    assessment_ids = set(assessments["id_assessment"])
    vle_keys = key_set(vle, VLE_KEY)

    student_info_dup = duplicate_count(student_info, STUDENT_KEY)
    registration_dup = duplicate_count(registration, STUDENT_KEY)
    assessments_dup = duplicate_count(assessments, ["id_assessment"])
    vle_dup = duplicate_count(vle, VLE_KEY)

    info_missing_registration, info_missing_registration_samples = count_unmatched(
        student_info, STUDENT_KEY, registration_keys
    )
    registration_missing_info, registration_missing_info_samples = count_unmatched(
        registration, STUDENT_KEY, student_info_keys
    )

    assessment_missing_assessment = int(
        (~student_assessment["id_assessment"].isin(assessment_ids)).sum()
    )
    assessment_missing_assessment_samples = (
        student_assessment.loc[
            ~student_assessment["id_assessment"].isin(assessment_ids),
            ["id_assessment", "id_student"],
        ]
        .drop_duplicates()
        .head(10)
        .to_dict("records")
    )

    assessment_enriched = student_assessment.merge(
        assessments,
        on="id_assessment",
        how="left",
        validate="many_to_one",
    )
    assessment_matched = assessment_enriched.dropna(
        subset=["code_module", "code_presentation"]
    )
    assessment_student_keys = assessment_matched[
        ["code_module", "code_presentation", "id_student"]
    ]
    assessment_missing_info, assessment_missing_info_samples = count_unmatched(
        assessment_student_keys, STUDENT_KEY, student_info_keys
    )
    assessment_missing_registration, assessment_missing_registration_samples = (
        count_unmatched(assessment_student_keys, STUDENT_KEY, registration_keys)
    )

    student_vle_result = count_student_vle_relationships(
        vle_keys=vle_keys,
        student_info_keys=student_info_keys,
        registration_keys=registration_keys,
    )

    all_checks = {
        "studentInfo_studentRegistration": info_missing_registration == 0
        and registration_missing_info == 0
        and student_info_dup == 0
        and registration_dup == 0,
        "studentAssessment_assessments": assessment_missing_assessment == 0
        and assessments_dup == 0,
        "studentVle_vle": student_vle_result["unmatched_vle"] == 0 and vle_dup == 0,
        "composite_student_key": assessment_missing_info == 0
        and assessment_missing_registration == 0
        and student_vle_result["unmatched_student_info"] == 0
        and student_vle_result["unmatched_registration"] == 0,
    }

    report_lines = [
        "# Báo Cáo Kiểm Tra Quan Hệ Giữa Các Bảng",
        f"Thời gian chạy: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 1. Phạm vi kiểm tra",
        "- `studentInfo` nối với `studentRegistration` bằng khóa ghép `code_module, code_presentation, id_student`.",
        "- `studentAssessment` nối với `assessments` bằng `id_assessment`.",
        "- `studentVle` nối với `vle` bằng khóa ghép `id_site, code_module, code_presentation`.",
        "- Các bảng hoạt động của sinh viên được kiểm tra lại với khóa ghép `code_module, code_presentation, id_student`.",
        "",
        "## 2. Tổng quan dữ liệu dùng để kiểm tra",
        "| Bảng | Số dòng | Khóa kiểm tra | Duplicate khóa |",
        "|---|---:|---|---:|",
        f"| studentInfo | {len(student_info)} | `{', '.join(STUDENT_KEY)}` | {student_info_dup} |",
        f"| studentRegistration | {len(registration)} | `{', '.join(STUDENT_KEY)}` | {registration_dup} |",
        f"| assessments | {len(assessments)} | `id_assessment` | {assessments_dup} |",
        f"| vle | {len(vle)} | `{', '.join(VLE_KEY)}` | {vle_dup} |",
        f"| studentAssessment | {len(student_assessment)} | `id_assessment`, student key suy ra từ assessments | - |",
        f"| studentVle | {student_vle_result['rows']} | `id_site`, student key | - |",
        "",
        "## 3. Kết quả kiểm tra quan hệ",
        "| Kiểm tra | Dòng không khớp | Kết luận |",
        "|---|---:|---|",
        f"| studentInfo không có studentRegistration tương ứng | {info_missing_registration} | {yes_no(info_missing_registration == 0)} |",
        f"| studentRegistration không có studentInfo tương ứng | {registration_missing_info} | {yes_no(registration_missing_info == 0)} |",
        f"| studentAssessment không tìm thấy id_assessment trong assessments | {assessment_missing_assessment} | {yes_no(assessment_missing_assessment == 0)} |",
        f"| studentAssessment không khớp studentInfo sau khi suy ra module-presentation | {assessment_missing_info} | {yes_no(assessment_missing_info == 0)} |",
        f"| studentAssessment không khớp studentRegistration sau khi suy ra module-presentation | {assessment_missing_registration} | {yes_no(assessment_missing_registration == 0)} |",
        f"| studentVle không tìm thấy id_site/module/presentation trong vle | {student_vle_result['unmatched_vle']} | {yes_no(student_vle_result['unmatched_vle'] == 0)} |",
        f"| studentVle không khớp studentInfo theo student key | {student_vle_result['unmatched_student_info']} | {yes_no(student_vle_result['unmatched_student_info'] == 0)} |",
        f"| studentVle không khớp studentRegistration theo student key | {student_vle_result['unmatched_registration']} | {yes_no(student_vle_result['unmatched_registration'] == 0)} |",
        "",
        "## 4. Dòng không khớp",
    ]

    report_lines.extend(
        sample_block(
            "studentInfo thiếu studentRegistration", info_missing_registration_samples
        )
    )
    report_lines.append("")
    report_lines.extend(
        sample_block(
            "studentRegistration thiếu studentInfo", registration_missing_info_samples
        )
    )
    report_lines.append("")
    report_lines.extend(
        sample_block(
            "studentAssessment thiếu assessments", assessment_missing_assessment_samples
        )
    )
    report_lines.append("")
    report_lines.extend(
        sample_block(
            "studentAssessment không khớp studentInfo",
            assessment_missing_info_samples,
        )
    )
    report_lines.append("")
    report_lines.extend(
        sample_block(
            "studentAssessment không khớp studentRegistration",
            assessment_missing_registration_samples,
        )
    )
    report_lines.append("")
    report_lines.extend(
        sample_block(
            "studentVle thiếu vle", student_vle_result["samples_vle"]
        )
    )
    report_lines.append("")
    report_lines.extend(
        sample_block(
            "studentVle không khớp studentInfo",
            student_vle_result["samples_student_info"],
        )
    )
    report_lines.append("")
    report_lines.extend(
        sample_block(
            "studentVle không khớp studentRegistration",
            student_vle_result["samples_registration"],
        )
    )

    report_lines.extend(
        [
            "",
            "## 5. Kết luận",
            "- Các quan hệ bắt buộc giữa bảng sinh viên, đăng ký, đánh giá và VLE đều được kiểm tra bằng khóa logic tương ứng.",
            "- Không phát hiện dòng không khớp khóa nếu tất cả các chỉ số ở mục 3 bằng 0.",
            f"- Thời gian chạy: {round(time.time() - start, 2)} giây.",
            "",
        ]
    )

    checklist_lines = [
        "# Checklist 02 - Kiểm Tra Quan Hệ Giữa Các Bảng",
        "",
        "Dựa trên danh sách công việc trong `ETL/elt_tasks.csv`, dưới đây là trạng thái các đầu việc thuộc nhóm kiểm tra quan hệ giữa các bảng.",
        "",
        "## Kiểm Tra Quan Hệ Giữa Các Bảng",
        f"- [{'x' if all_checks['studentInfo_studentRegistration'] else ' '}] **Kiểm tra studentInfo nối được với studentRegistration:** {yes_no(all_checks['studentInfo_studentRegistration'])}.",
        f"- [{'x' if all_checks['studentAssessment_assessments'] else ' '}] **Kiểm tra studentAssessment nối được với assessments:** {yes_no(all_checks['studentAssessment_assessments'])}.",
        f"- [{'x' if all_checks['studentVle_vle'] else ' '}] **Kiểm tra studentVle nối được với vle:** {yes_no(all_checks['studentVle_vle'])}.",
        f"- [{'x' if all_checks['composite_student_key'] else ' '}] **Kiểm tra khóa ghép code_module, code_presentation, id_student:** {yes_no(all_checks['composite_student_key'])}.",
        "- [x] **Ghi nhận các dòng không khớp khóa nếu có:** Đã ghi chi tiết trong `02_relationship_report.md`.",
        "",
        f"**Trạng thái chung:** {'Hoàn tất' if all(all_checks.values()) else 'Cần kiểm tra thêm'}",
        "",
    ]

    REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")
    CHECKLIST_PATH.write_text("\n".join(checklist_lines), encoding="utf-8")

    print(f"Wrote {REPORT_PATH.relative_to(ROOT_DIR).as_posix()}")
    print(f"Wrote {CHECKLIST_PATH.relative_to(ROOT_DIR).as_posix()}")


if __name__ == "__main__":
    main()
