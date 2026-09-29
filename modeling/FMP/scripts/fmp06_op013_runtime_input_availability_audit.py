from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OUTPUT = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "fmp06_op013_runtime_input_availability_audit.json"
)


TASK_DIRS = {
    "T1": PROJECT_ROOT / "modeling" / "T1",
    "T2": PROJECT_ROOT / "modeling" / "T2",
    "T3": PROJECT_ROOT / "modeling" / "T3",
    "T4": PROJECT_ROOT / "modeling" / "T4",
    "T5": PROJECT_ROOT / "modeling" / "T5",
    "T6": PROJECT_ROOT / "modeling" / "T6",
    "T7": PROJECT_ROOT / "modeling" / "T7",
}


INTERESTING_TERMS = {
    "ticket_id": [
        "ticket_id",
        "bug_id",
        "issue_id",
        "id",
    ],
    "text": [
        "description",
        "summary",
        "title",
        "text",
        "body",
        "comment",
    ],
    "assignee": [
        "assignee",
        "assigned_to",
        "owner",
    ],
    "resolution": [
        "resolution",
        "resolved",
        "resolution_time",
        "time_to_resolution",
    ],
    "event": [
        "event",
        "resolved_event",
        "event_observed",
        "status",
    ],
    "time": [
        "time",
        "duration",
        "age",
        "resolution_time",
        "time_to_resolution",
    ],
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def inspect_csv(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "file": rel(path),
        "readable": False,
        "rows_sampled": 0,
        "column_count": 0,
        "columns": [],
        "matched_semantics": {},
        "sample_unique_values": {},
    }

    try:
        with path.open(
            "r",
            encoding="utf-8",
            errors="replace",
            newline="",
        ) as handle:
            reader = csv.reader(handle)

            header = next(reader, [])
            result["readable"] = True
            result["columns"] = header
            result["column_count"] = len(header)

            lowered = {
                str(col).strip().lower(): col
                for col in header
            }

            for semantic, terms in INTERESTING_TERMS.items():
                matches = []

                for lowered_name, original_name in lowered.items():
                    if any(term in lowered_name for term in terms):
                        matches.append(original_name)

                result["matched_semantics"][semantic] = sorted(
                    set(matches)
                )

            for row in reader:
                if result["rows_sampled"] >= 3:
                    break

                result["rows_sampled"] += 1

                for semantic, columns in result[
                    "matched_semantics"
                ].items():
                    for column in columns:
                        try:
                            index = header.index(column)
                            value = row[index]
                        except (ValueError, IndexError):
                            continue

                        if value not in ("", None):
                            result["sample_unique_values"].setdefault(
                                semantic,
                                []
                            )

                            values = result[
                                "sample_unique_values"
                            ][semantic]

                            if value not in values and len(values) < 3:
                                values.append(value)

    except Exception as exc:
        result["error"] = str(exc)

    return result


def inspect_json(path: Path) -> dict[str, Any]:
    result = {
        "file": rel(path),
        "readable": False,
        "top_level_type": None,
        "keys": [],
        "semantic_matches": {},
    }

    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        )

        result["readable"] = True
        result["top_level_type"] = type(data).__name__

        if isinstance(data, dict):
            keys = list(data.keys())
            result["keys"] = keys[:100]

            lowered = {
                str(key).lower(): key
                for key in keys
            }

            for semantic, terms in INTERESTING_TERMS.items():
                matches = []

                for lowered_name, original_name in lowered.items():
                    if any(term in lowered_name for term in terms):
                        matches.append(original_name)

                result["semantic_matches"][semantic] = sorted(
                    set(matches)
                )

    except Exception as exc:
        result["error"] = str(exc)

    return result


def collect_files(task_dir: Path) -> tuple[list[Path], list[Path]]:
    csv_files = sorted(task_dir.rglob("*.csv"))
    json_files = sorted(task_dir.rglob("*.json"))

    return csv_files, json_files


def summarize_task(
    task: str,
    task_dir: Path,
) -> dict[str, Any]:

    csv_files, json_files = collect_files(task_dir)

    csv_records = [
        inspect_csv(path)
        for path in csv_files
    ]

    json_records = [
        inspect_json(path)
        for path in json_files
    ]

    return {
        "task": task,
        "task_directory_exists": task_dir.exists(),
        "csv_file_count": len(csv_files),
        "json_file_count": len(json_files),
        "csv_files": csv_records,
        "json_files": json_records,
    }


def determine_availability(
    task: str,
    task_result: dict[str, Any],
) -> dict[str, Any]:

    all_records = (
        task_result["csv_files"]
        + task_result["json_files"]
    )

    semantics = set()

    for record in all_records:
        for mapping_name in (
            "matched_semantics",
            "semantic_matches",
        ):
            for values in record.get(
                mapping_name,
                {}
            ).values():
                semantics.update(
                    str(value).lower()
                    for value in values
                )

    if task in {"T1", "T2", "T3"}:
        required = ["text"]

    elif task == "T4":
        required = ["text", "assignee"]

    elif task == "T5":
        required = ["text"]

    elif task == "T6":
        required = ["text"]

    elif task == "T7":
        required = ["time", "event"]

    else:
        required = []

    satisfied = []

    for requirement in required:
        terms = INTERESTING_TERMS[requirement]

        if any(
            any(term in item for term in terms)
            for item in semantics
        ):
            satisfied.append(requirement)

    missing = [
        requirement
        for requirement in required
        if requirement not in satisfied
    ]

    if not missing:
        status = "POTENTIALLY_AVAILABLE"
    else:
        status = "NOT_ESTABLISHED"

    return {
        "required_semantics": required,
        "observed_required_semantics": satisfied,
        "missing_required_semantics": missing,
        "availability_status": status,
    }


def main() -> None:
    print("=" * 72)
    print("FMP-06 OP-013 — RUNTIME INPUT AVAILABILITY AUDIT")
    print("=" * 72)
    print()
    print("Mode: READ-ONLY")
    print("No model loading")
    print("No inference")
    print("No retraining")
    print("No artifact modification")
    print()

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report: dict[str, Any] = {
        "operation": "FMP-06 OP-013",
        "operation_type": (
            "READ_ONLY_RUNTIME_INPUT_AVAILABILITY_AUDIT"
        ),
        "project_root": str(PROJECT_ROOT),
        "tasks": {},
        "safeguards": {
            "models_loaded": False,
            "inference_executed": False,
            "retraining": False,
            "artifact_modification": False,
            "threshold_created": False,
            "synthetic_input_created": False,
            "synthetic_target_created": False,
            "universal_confidence_created": False,
            "universal_risk_created": False,
        },
    }

    for task, task_dir in TASK_DIRS.items():

        print("-" * 72)
        print(task)

        result = summarize_task(
            task,
            task_dir,
        )

        availability = determine_availability(
            task,
            result,
        )

        result["runtime_input_availability"] = availability

        report["tasks"][task] = result

        print(
            "  task directory:",
            result["task_directory_exists"],
        )

        print(
            "  CSV files:",
            result["csv_file_count"],
        )

        print(
            "  JSON files:",
            result["json_file_count"],
        )

        print(
            "  required semantics:",
            availability["required_semantics"],
        )

        print(
            "  observed semantics:",
            availability[
                "observed_required_semantics"
            ],
        )

        print(
            "  missing semantics:",
            availability[
                "missing_required_semantics"
            ],
        )

        print(
            "  availability:",
            availability[
                "availability_status"
            ],
        )

    report["overall_status"] = "PASS"

    OUTPUT.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 72)
    print("OVERALL STATUS: PASS")
    print(f"OUTPUT: {OUTPUT}")
    print("=" * 72)


if __name__ == "__main__":
    main()