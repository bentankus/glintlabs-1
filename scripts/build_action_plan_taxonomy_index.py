#!/usr/bin/env python
"""Build manager action-plan lookup artifacts from the taxonomy workbook."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd


MAIN_SHEET = "APTemplate_FocusAreas_Ext"
SCHEMA_VERSION = "2.0.0"
SOURCE_URL = (
    "https://microsoft.sharepoint-df.com/:x:/r/teams/EVE/_layouts/15/Doc.aspx"
    "?sourcedoc=%7B0F15DEAC-2FD9-4324-9CDC-DADF01AED66C%7D"
    "&file=Action%20Planning%20Taxonomy.xlsx&action=default&mobileredirect=true"
    "&share=cQqs3hUP2S8kQ5zc2t8BrtZsEgUC16tQCPV2ZNTnlKYSFg7kWQ"
    "&CID=D800A8D6-41EE-4F68-AB87-33B90E17CF69"
)
MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
SUSPICIOUS_ENCODING = re.compile(r"â|Â|�")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build MAT action-plan taxonomy artifacts.")
    parser.add_argument(
        "--workbook",
        default="plugins/eve-people-science/references/skills/manager-action-taking/Action Planning Taxonomy.xlsx",
        help="Path to Action Planning Taxonomy.xlsx.",
    )
    parser.add_argument(
        "--output-dir",
        default="plugins/eve-people-science/references/skills/manager-action-taking/gen",
        help="Directory for normalized runtime artifacts.",
    )
    parser.add_argument(
        "--output-csv",
        default=None,
        help="Optional output flattened CSV path for debugging.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify committed generated artifacts are current with the workbook.",
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_text(value: Any) -> str:
    text = "" if value is None else str(value)
    if text.lower() == "nan":
        return ""
    text = text.replace("_x000D_", "\n")
    replacements = {
        "â€™": "'",
        "â€œ": '"',
        "â€�": '"',
        "â€“": "-",
        "â€”": "-",
        "â€˜": "'",
        "â€¢": "-",
        "Â ": " ",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_question_ids(value: str) -> list[str]:
    text = clean_text(value)
    if not text:
        return []
    question_ids = []
    for part in text.split(","):
        question_id = part.strip().strip("[]{}").strip().upper()
        if question_id:
            question_ids.append(question_id)
    return question_ids


def display_question_id(question_id: str) -> str:
    return f"[{question_id}]"


def parse_sequence(value: Any) -> int:
    text = clean_text(value)
    try:
        return int(float(text))
    except ValueError as exc:
        raise ValueError(f"Invalid action-record sequence: {text!r}") from exc


def parse_excel_timestamp(value: Any) -> str:
    text = clean_text(value)
    if not text:
        return ""
    try:
        timestamp = pd.to_datetime(float(text), unit="D", origin="1899-12-30", utc=True)
    except (ValueError, TypeError, OverflowError):
        timestamp = pd.to_datetime(text, errors="coerce", utc=True)
    return "" if pd.isna(timestamp) else timestamp.round("s").isoformat()


def ext_links(row: pd.Series) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    seen: set[str] = set()
    for col in [c for c in row.index if re.match(r"^Ext Link \d+$", str(c))]:
        link = clean_text(row[col])
        if link and link not in seen:
            links.append((str(col), link))
            seen.add(link)
    return links


def body_links(body: str) -> list[dict[str, Any]]:
    links = []
    for label, target in MARKDOWN_LINK.findall(body):
        is_external = bool(re.match(r"^https?://", target, re.IGNORECASE))
        links.append(
            {
                "type": "inline_external" if is_external else "internal_reference",
                "title": clean_text(label),
                "url": target if is_external else "",
                "target": "" if is_external else clean_text(target),
                "sources": ["content_text_body"],
                "status": "unchecked" if is_external else "unresolved",
            }
        )
    return links


def record_resources(row: pd.Series, body: str) -> list[dict[str, Any]]:
    resources: list[dict[str, Any]] = []
    video_link = clean_text(row["Video Link"])
    if video_link:
        resources.append(
            {
                "type": "video",
                "title": clean_text(row["Video Title"]),
                "url": video_link,
                "target": "",
                "sources": ["Video Link"],
                "status": "unchecked",
            }
        )
    for column, link in ext_links(row):
        resources.append(
            {
                "type": "external_link",
                "title": "",
                "url": link,
                "target": "",
                "sources": [column],
                "status": "unchecked",
            }
        )
    resources.extend(body_links(body))

    unique: list[dict[str, Any]] = []
    positions: dict[tuple[str, str], int] = {}
    type_priority = {
        "video": 3,
        "external_link": 2,
        "inline_external": 1,
        "internal_reference": 0,
    }
    for resource in resources:
        key = (resource["url"], resource["target"])
        if key not in positions:
            positions[key] = len(unique)
            unique.append(resource)
            continue
        existing = unique[positions[key]]
        if not existing["title"] and resource["title"]:
            existing["title"] = resource["title"]
        existing["sources"] = list(dict.fromkeys([*existing["sources"], *resource["sources"]]))
        if type_priority[resource["type"]] > type_priority[existing["type"]]:
            existing["type"] = resource["type"]
    return unique


def content_type(description: str, body: str, resources: list[dict[str, Any]]) -> str:
    if body and re.fullmatch(r"https?://\S+", body, re.IGNORECASE):
        return "video" if any(item["type"] == "video" for item in resources) else "resource_only"
    if body:
        return "mixed" if resources else "guide"
    if description:
        return "discussion_prompt"
    return "resource_only"


ACTION_TYPE_RULES = [
    (
        "team_conversation",
        (
            "discuss",
            "conversation",
            "input",
            "ideas",
            "ask your team",
            "share with your team",
            "team meeting",
            "listen",
            "feedback",
        ),
    ),
    (
        "communication",
        (
            "communicat",
            "message",
            "informed",
            "share",
            "clarify",
            "explain",
            "story",
            "stories",
        ),
    ),
    (
        "resources_and_support",
        (
            "resource",
            "support",
            "barrier",
            "obstacle",
            "network",
            "help",
            "tools",
        ),
    ),
    (
        "trust_and_inclusion",
        (
            "trust",
            "inclusive",
            "inclusion",
            "belong",
            "diverse",
            "fair",
            "empathy",
            "care",
        ),
    ),
    (
        "growth_and_development",
        (
            "career",
            "growth",
            "development",
            "learn",
            "skill",
            "strength",
            "weakness",
            "coach",
        ),
    ),
    (
        "recognition_and_motivation",
        (
            "recognition",
            "recognize",
            "celebrat",
            "appreciat",
            "motivat",
            "energ",
        ),
    ),
    (
        "workload_and_prioritization",
        (
            "workload",
            "priority",
            "priorities",
            "priorit",
            "deadline",
            "capacity",
            "focus",
            "time",
        ),
    ),
    (
        "process_and_accountability",
        (
            "process",
            "accountab",
            "decision",
            "follow through",
            "commit",
            "plan",
            "milestone",
            "measure",
        ),
    ),
    (
        "reflection_and_self_assessment",
        (
            "self-assessment",
            "reflect",
            "think about",
            "assess yourself",
            "self assessment",
        ),
    ),
    (
        "resource_learning",
        (
            "watch",
            "read",
            "learning",
            "video",
            "article",
        ),
    ),
]


def action_type(title: str, description: str, body: str, resources: list[dict[str, Any]]) -> str:
    if resources and not (description or body and not re.fullmatch(r"https?://\S+", body, re.IGNORECASE)):
        return "resource_learning"
    title_text = title.lower()
    description_text = description.lower()
    body_text = body.lower()
    scores: list[tuple[int, int, str]] = []
    for priority, (label, needles) in enumerate(ACTION_TYPE_RULES):
        score = 0
        for needle in needles:
            if needle in title_text:
                score += 4
            if needle in description_text:
                score += 2
            if needle in body_text:
                score += 1
        if score:
            scores.append((score, priority, label))
    if not scores:
        return "general_action"
    return sorted(scores, key=lambda item: (-item[0], item[1]))[0][2]


def selection_signals(record_action_type: str, content_kind: str, resources: list[dict[str, Any]]) -> list[str]:
    signals = [record_action_type]
    if content_kind in {"guide", "mixed"}:
        signals.append("has_detailed_guidance")
    if content_kind == "discussion_prompt":
        signals.append("quick_start")
    if any(resource["type"] == "video" for resource in resources):
        signals.append("has_video")
    if any(resource["type"] in {"external_link", "inline_external"} for resource in resources):
        signals.append("has_external_resources")
    if any(resource["type"] == "internal_reference" for resource in resources):
        signals.append("has_unresolved_internal_references")
    return signals


def record_file_name(template_uuid: str, sequence: int) -> str:
    return f"{template_uuid}--{sequence:04d}.json"


def load_frame(workbook: Path) -> pd.DataFrame:
    frame = pd.read_excel(workbook, sheet_name=MAIN_SHEET, header=2, dtype=str)
    frame = frame.dropna(how="all")
    frame.columns = [str(col).strip() for col in frame.columns]
    for col in frame.columns:
        frame[col] = frame[col].fillna("").astype(str).map(clean_text)

    required = {
        "#",
        "question_uuid",
        "action_plan_template_uuid",
        "sequence",
        "content_resource_version_id",
        "AP Template",
        "Focus Areas Title",
        "Content Description",
        "Content Text Body",
        "template_version_last_modified_timestamp",
        "Video Title",
        "Video Link",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Missing expected columns: {', '.join(missing)}")
    return frame


def build_artifacts(
    workbook: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], pd.DataFrame]:
    frame = load_frame(workbook)
    workbook_hash = sha256(workbook)
    source = {
        "workbook": workbook.as_posix(),
        "source_url": SOURCE_URL,
        "sheet": MAIN_SHEET,
        "sha256": workbook_hash,
    }

    question_map: dict[str, Any] = {}
    candidate_sets: dict[str, Any] = {}
    action_records: dict[str, Any] = {}
    flat_rows: list[dict[str, Any]] = []
    unresolved_references: list[dict[str, Any]] = []
    encoding_warnings: list[dict[str, Any]] = []

    for frame_position, (_, row) in enumerate(frame.iterrows(), start=4):
        question_ids = split_question_ids(row["question_uuid"])
        if not question_ids:
            raise ValueError(f"Excel row {frame_position} has no question IDs.")

        template_uuid = clean_text(row["action_plan_template_uuid"])
        template_name = clean_text(row["AP Template"])
        sequence = parse_sequence(row["sequence"])
        record_id = f"{template_uuid}:{sequence}"
        if record_id in action_records:
            raise ValueError(f"Duplicate action-plan record ID: {record_id}")

        description = clean_text(row["Content Description"])
        body = clean_text(row["Content Text Body"])
        resources = record_resources(row, body)
        kind = content_type(description, body, resources)
        record_action_type = action_type(clean_text(row["Focus Areas Title"]), description, body, resources)
        record = {
            "schema_version": SCHEMA_VERSION,
            "action_plan_record_id": record_id,
            "id_strategy": "action_plan_template_uuid:sequence",
            "question_ids": question_ids,
            "source_question_id_cell": clean_text(row["question_uuid"]),
            "action_plan_template_uuid": template_uuid,
            "template_name": template_name,
            "sequence": sequence,
            "focus_area_title": clean_text(row["Focus Areas Title"]),
            "content_type": kind,
            "action_type": record_action_type,
            "selection_signals": selection_signals(record_action_type, kind, resources),
            "content_description": description,
            "content_text_body": body,
            "content_resource_version_id": clean_text(row["content_resource_version_id"]),
            "template_version_last_modified_at": parse_excel_timestamp(
                row["template_version_last_modified_timestamp"]
            ),
            "video_extract": clean_text(row.get("video_extract", "")),
            "resources": resources,
            "source": {
                "workbook_sha256": workbook_hash,
                "sheet": MAIN_SHEET,
                "excel_row": frame_position,
                "source_record_number": clean_text(row["#"]),
            },
        }
        if not description and not body and not resources:
            raise ValueError(f"Action-plan record {record_id} has no usable content.")
        action_records[record_id] = record

        if SUSPICIOUS_ENCODING.search(" ".join((description, body, record["focus_area_title"]))):
            encoding_warnings.append(
                {
                    "action_plan_record_id": record_id,
                    "excel_row": frame_position,
                }
            )
        for resource in resources:
            if resource["type"] == "internal_reference":
                unresolved_references.append(
                    {
                        "action_plan_record_id": record_id,
                        "title": resource["title"],
                        "target": resource["target"],
                    }
                )

        candidate_set = candidate_sets.setdefault(
            template_uuid,
            {
                "schema_version": SCHEMA_VERSION,
                "action_plan_template_uuid": template_uuid,
                "template_name": template_name,
                "action_plan_record_ids": [],
            },
        )
        if candidate_set["template_name"] != template_name:
            raise ValueError(f"Template {template_uuid} has inconsistent names.")
        candidate_set["action_plan_record_ids"].append(record_id)

        for question_id in question_ids:
            question_entry = question_map.setdefault(
                question_id,
                {
                    "question_id": question_id,
                    "display_question_id": display_question_id(question_id),
                    "candidate_sets": {},
                },
            )
            question_candidate_set = question_entry["candidate_sets"].setdefault(
                template_uuid,
                {
                    "action_plan_template_uuid": template_uuid,
                    "template_name": template_name,
                    "action_plan_record_ids": [],
                },
            )
            question_candidate_set["action_plan_record_ids"].append(record_id)

            flat = {
                "question_id": question_id,
                "display_question_id": display_question_id(question_id),
                "action_plan_record_id": record_id,
                "action_plan_template_uuid": template_uuid,
                "sequence": sequence,
                "template_name": template_name,
                "focus_area_title": record["focus_area_title"],
                "content_description": description,
                "content_text_body": body,
                "resources": json.dumps(resources, ensure_ascii=True),
            }
            flat_rows.append(flat)

    for question in question_map.values():
        question["candidate_sets"] = sorted(
            question["candidate_sets"].values(),
            key=lambda item: item["template_name"],
        )
        for candidate_set in question["candidate_sets"]:
            candidate_set["action_plan_record_ids"] = sorted(
                set(candidate_set["action_plan_record_ids"]),
                key=lambda item: action_records[item]["sequence"],
            )

    for candidate_set in candidate_sets.values():
        candidate_set["action_plan_record_ids"] = sorted(
            candidate_set["action_plan_record_ids"],
            key=lambda item: action_records[item]["sequence"],
        )

    summary = {
        "source_rows": int(len(frame)),
        "question_ids": int(len(question_map)),
        "candidate_sets": int(len(candidate_sets)),
        "action_plan_records": int(len(action_records)),
        "expanded_question_record_relationships": int(len(flat_rows)),
    }
    action_type_counts = dict(
        sorted(collections.Counter(record["action_type"] for record in action_records.values()).items())
    )
    content_type_counts = dict(
        sorted(collections.Counter(record["content_type"] for record in action_records.values()).items())
    )
    selection_signal_counts = dict(
        sorted(
            collections.Counter(
                signal
                for record in action_records.values()
                for signal in record["selection_signals"]
            ).items()
        )
    )
    generated: dict[str, dict[str, Any]] = {
        "catalog.json": {
            "schema_version": SCHEMA_VERSION,
            "source": source,
            "summary": summary,
            "action_type_counts": action_type_counts,
            "content_type_counts": content_type_counts,
            "selection_signal_counts": selection_signal_counts,
            "action_plan_record_id_strategy": "action_plan_template_uuid:sequence",
            "candidate_sets": [
                {
                    "action_plan_template_uuid": template_uuid,
                    "template_name": candidate_set["template_name"],
                    "action_plan_record_count": len(candidate_set["action_plan_record_ids"]),
                    "file": f"c/{template_uuid}.json",
                }
                for template_uuid, candidate_set in sorted(
                    candidate_sets.items(),
                    key=lambda item: item[1]["template_name"],
                )
            ],
        },
        "question-map.json": {
            "schema_version": SCHEMA_VERSION,
            "source": source,
            "summary": summary,
            "questions": dict(sorted(question_map.items())),
        },
        "validation-report.json": {
            "schema_version": SCHEMA_VERSION,
            "source": source,
            "status": "warnings" if encoding_warnings or unresolved_references else "passed",
            "summary": {
                **summary,
                "encoding_warning_records": len(encoding_warnings),
                "unresolved_internal_references": len(unresolved_references),
            },
            "action_type_counts": action_type_counts,
            "content_type_counts": content_type_counts,
            "selection_signal_counts": selection_signal_counts,
            "encoding_warnings": encoding_warnings,
            "unresolved_internal_references": unresolved_references,
        },
    }
    for template_uuid, candidate_set in candidate_sets.items():
        generated[f"c/{template_uuid}.json"] = candidate_set
    for record_id, record in action_records.items():
        generated[
            f"a/{record_file_name(record['action_plan_template_uuid'], record['sequence'])}"
        ] = record

    flat = pd.DataFrame(flat_rows).sort_values(
        ["question_id", "action_plan_template_uuid", "sequence"],
        na_position="last",
    )
    return generated, flat


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_generated(root: Path, artifacts: dict[str, dict[str, Any]]) -> None:
    expected_paths = {Path(relative_path) for relative_path in artifacts}
    if root.exists():
        for path in root.rglob("*"):
            if path.is_file() and path.relative_to(root) not in expected_paths:
                path.unlink()
    for relative_path, payload in artifacts.items():
        write_json(root / relative_path, payload)
    if root.exists():
        for path in sorted((p for p in root.rglob("*") if p.is_dir()), reverse=True):
            try:
                path.rmdir()
            except OSError:
                pass


def compare_file(path: Path, expected: Path) -> bool:
    return path.exists() and path.read_bytes() == expected.read_bytes()


def compare_directories(current: Path, expected: Path) -> bool:
    current_files = {
        path.relative_to(current)
        for path in current.rglob("*")
        if path.is_file()
    } if current.exists() else set()
    expected_files = {
        path.relative_to(expected)
        for path in expected.rglob("*")
        if path.is_file()
    }
    if current_files != expected_files:
        return False
    return all(compare_file(current / path, expected / path) for path in expected_files)


def main() -> int:
    args = parse_args()
    workbook = Path(args.workbook)
    output_dir = Path(args.output_dir)
    generated, flat = build_artifacts(workbook)

    if args.check:
        with tempfile.TemporaryDirectory() as tmp_dir:
            temporary = Path(tmp_dir)
            expected_dir = temporary / "gen"
            write_generated(expected_dir, generated)
            if not compare_directories(output_dir, expected_dir):
                print(
                    "Manager Action Taking taxonomy artifacts are out of date. Run "
                    "python plugins/eve-people-science/scripts/build_action_plan_taxonomy_index.py",
                    file=sys.stderr,
                )
                return 1
    else:
        write_generated(output_dir, generated)
        if args.output_csv:
            output_csv = Path(args.output_csv)
            output_csv.parent.mkdir(parents=True, exist_ok=True)
            flat.to_csv(output_csv, index=False)

    print(json.dumps(generated["catalog.json"]["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
