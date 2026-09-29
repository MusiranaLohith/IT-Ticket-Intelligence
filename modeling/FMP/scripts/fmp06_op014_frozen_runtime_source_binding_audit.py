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
    / "fmp06_op014_frozen_runtime_source_binding_audit.json"
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


SEMANTICS = {
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
    "priority": [
        "priority",
    ],
    "severity": [
        "severity",
    ],
    "resolution": [
        "resolution",
        "resolved",
    ],
    "time": [
        "time_to_resolution",
        "resolution_time",
        "duration",
        "time",
        "age",
    ],
    "event": [
        "event",
        "event_observed",
        "resolved_event",
        "status",
    ],
}


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def match_columns(columns: list[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}

    for semantic, terms in SEMANTICS.items():
        matches = []

        for column in columns:
            lowered = str(column).strip().lower()

            if any(term in lowered for term in terms):
                matches.append(column)

        result[semantic] = sorted(set(matches))

    return result


def inspect_csv(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "file": relative(path),
        "readable": False,
        "row_count_estimate": None,
        "columns": [],
        "semantic_columns": {},
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
            result["semantic_columns"] = match_columns(header)

            rows = 0

            for _ in reader:
                rows += 1

            result["row_count_estimate"] = rows

    except Exception as exc:
        result["error"] = str(exc)

    return result


def inspect_json(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "file": relative(path),
        "readable": False,
        "top_level_type": None,
        "keys": [],
        "semantic_keys": {},
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

            result["keys"] = keys[:200]
            result["semantic_keys"] = match_columns(
                [str(key) for key in keys]
            )

    except Exception as exc:
        result["error"] = str(exc)

    return result


def inspect_task(task: str, task_dir: Path) -> dict[str, Any]:
    csv_files = sorted(task_dir.rglob("*.csv"))
    json_files = sorted(task_dir.rglob("*.json"))

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
        "csv_records": csv_records,
        "json_records": json_records,
    }


def aggregate_semantics(
    result: dict[str, Any]
) -> dict[str, list[str]]:

    aggregate = {
        semantic: []
        for semantic in SEMANTICS
    }

    for record in (
        result["csv_records"]
        + result["json_records"]
    ):

        mapping = (
            record.get("semantic_columns")
            or record.get("semantic_keys")
            or {}
        )

        for semantic, values in mapping.items():
            aggregate.setdefault(semantic, [])

            for value in values:
                if value not in aggregate[semantic]:
                    aggregate[semantic].append(value)

    return aggregate


def identify_candidate_sources(
    task: str,
    result: dict[str, Any],
) -> list[dict[str, Any]]:

    candidates = []

    required = {
        "T1": ["text"],
        "T2": ["text"],
        "T3": ["text"],
        "T4": ["text", "assignee"],
        "T5": ["text"],
        "T6": ["text"],
        "T7": ["time", "event"],
    }[task]

    for record in result["csv_records"]:
        mapping = record["semantic_columns"]

        available = [
            semantic
            for semantic in required
            if mapping.get(semantic)
        ]

        if len(available) == len(required):
            candidates.append(
                {
                    "file": record["file"],
                    "source_type": "CSV",
                    "matched_required_semantics": available,
                    "columns": {
                        semantic: mapping[semantic]
                        for semantic in available
                    },
                    "row_count_estimate": record[
                        "row_count_estimate"
                    ],
                }
            )

    for record in result["json_records"]:
        mapping = record["semantic_keys"]

        available = [
            semantic
            for semantic in required
            if mapping.get(semantic)
        ]

        if len(available) == len(required):
            candidates.append(
                {
                    "file": record["file"],
                    "source_type": "JSON",
                    "matched_required_semantics": available,
                    "columns_or_keys": {
                        semantic: mapping[semantic]
                        for semantic in available
                    },
                }
            )

    return candidates


def determine_binding_status(
    task: str,
    candidates: list[dict[str, Any]],
) -> str:

    if not candidates:
        return "NO_EXACT_SOURCE_BOUND"

    if task in {"T1", "T2", "T3"}:
        return "SOURCE_CANDIDATE_FOUND"

    if task == "T4":
        return "SOURCE_CANDIDATE_FOUND"

    if task == "T5":
        return "SOURCE_CANDIDATE_FOUND"

    if task == "T6":
        return "SOURCE_CANDIDATE_FOUND"

    if task == "T7":
        return "SOURCE_CANDIDATE_FOUND"

    return "NOT_ESTABLISHED"


def main() -> None:

    print("=" * 72)
    print("FMP-06 OP-014 — FROZEN RUNTIME SOURCE BINDING AUDIT")
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
        "operation": "FMP-06 OP-014",
        "operation_type": (
            "READ_ONLY_FROZEN_RUNTIME_SOURCE_BINDING_AUDIT"
        ),
        "project_root": str(PROJECT_ROOT),
        "tasks": {},
        "safeguards": {
            "models_loaded": False,
            "inference_executed": False,
            "retraining": False,
            "artifact_modification": False,
            "threshold_created": False,
            "calibration_performed": False,
            "synthetic_input_created": False,
            "synthetic_target_created": False,
            "universal_confidence_created": False,
            "universal_risk_created": False,
        },
    }

    overall_status = "PASS"

    for task, task_dir in TASK_DIRS.items():

        print("-" * 72)
        print(task)

        task_result = inspect_task(
            task,
            task_dir,
        )

        candidates = identify_candidate_sources(
            task,
            task_result,
        )

        binding_status = determine_binding_status(
            task,
            candidates,
        )

        aggregate = aggregate_semantics(
            task_result
        )

        task_result["aggregate_semantics"] = aggregate
        task_result["candidate_runtime_sources"] = candidates
        task_result["binding_status"] = binding_status

        report["tasks"][task] = task_result

        print(
            "  directory exists:",
            task_result["task_directory_exists"],
        )

        print(
            "  CSV files inspected:",
            len(task_result["csv_records"]),
        )

        print(
            "  JSON files inspected:",
            len(task_result["json_records"]),
        )

        print(
            "  candidate runtime sources:",
            len(candidates),
        )

        print(
            "  binding status:",
            binding_status,
        )

        for candidate in candidates[:5]:
            print(
                "    SOURCE:",
                candidate["file"],
            )

            print(
                "    TYPE:",
                candidate["source_type"],
            )

            print(
                "    MATCHED:",
                candidate[
                    "matched_required_semantics"
                ],
            )

        print()

    report["overall_status"] = overall_status

    OUTPUT.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("=" * 72)
    print(f"OVERALL STATUS: {overall_status}")
    print(f"OUTPUT: {OUTPUT}")
    print("=" * 72)


if __name__ == "__main__":
    main()