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
    / "fmp06_op015_runtime_source_semantic_validation.json"
)


# Candidate sources deliberately restricted to the most plausible
# runtime populations discovered by OP-014.
CANDIDATES = {
    "T1": [
        PROJECT_ROOT / "modeling/T1/derived/t1_dataset.csv",
        PROJECT_ROOT / "modeling/T1/derived/t1_vscode_dataset.csv",
    ],
    "T2": [
        PROJECT_ROOT / "modeling/T2/derived/t2_features.csv",
    ],
    "T3": [
        PROJECT_ROOT / "modeling/T3/derived/t3_features.csv",
    ],
    "T4": [
        PROJECT_ROOT / "modeling/T4/derived/t4_features.csv",
        PROJECT_ROOT / "modeling/T4/derived/t4_train.csv",
        PROJECT_ROOT / "modeling/T4/derived/t4_eval.csv",
    ],
    "T5": [
        PROJECT_ROOT / "modeling/T5/derived/t5_train_features.csv",
    ],
    "T6": [
        PROJECT_ROOT / "modeling/T6/splits/t6_train_group_aware.csv",
        PROJECT_ROOT / "modeling/T6/splits/t6_eval_group_aware.csv",
    ],
    "T7": [
        PROJECT_ROOT / "modeling/T7/derived/t7_creation_time_modeling_dataset.csv",
    ],
}


SEMANTIC_TERMS = {
    "id": [
        "ticket_id",
        "bug_id",
        "issue_id",
        "id",
    ],
    "text": [
        "text",
        "description",
        "summary",
        "title",
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
    "duplicate_label": [
        "duplicate",
        "is_duplicate",
        "duplicate_label",
        "label",
        "target",
        "y",
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
    "query": [
        "query",
    ],
    "candidate": [
        "candidate",
    ],
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def semantic_columns(columns: list[str]) -> dict[str, list[str]]:
    result = {}

    for semantic, terms in SEMANTIC_TERMS.items():
        matches = []

        for column in columns:
            lowered = str(column).strip().lower()

            if any(term in lowered for term in terms):
                matches.append(column)

        result[semantic] = sorted(set(matches))

    return result


def inspect_csv(path: Path) -> dict[str, Any]:
    result = {
        "file": rel(path),
        "exists": path.exists(),
        "readable": False,
        "columns": [],
        "row_count": None,
        "semantic_columns": {},
        "sample_rows": [],
    }

    if not path.exists():
        return result

    try:
        with path.open(
            "r",
            encoding="utf-8",
            errors="replace",
            newline="",
        ) as handle:

            reader = csv.DictReader(handle)

            columns = reader.fieldnames or []

            result["readable"] = True
            result["columns"] = columns
            result["semantic_columns"] = semantic_columns(
                columns
            )

            rows = 0

            for row in reader:
                rows += 1

                if len(result["sample_rows"]) < 3:
                    compact = {}

                    for semantic, names in result[
                        "semantic_columns"
                    ].items():

                        for name in names:
                            value = row.get(name)

                            if value not in ("", None):
                                compact[name] = str(value)[:160]

                    result["sample_rows"].append(compact)

            result["row_count"] = rows

    except Exception as exc:
        result["error"] = str(exc)

    return result


def classify_source(
    task: str,
    record: dict[str, Any],
) -> dict[str, Any]:

    columns = record.get(
        "semantic_columns",
        {}
    )

    reasons = []
    warnings = []

    has_text = bool(columns.get("text"))
    has_id = bool(columns.get("id"))
    has_assignee = bool(columns.get("assignee"))
    has_time = bool(columns.get("time"))
    has_event = bool(columns.get("event"))

    outcome_columns = (
        columns.get("priority", [])
        + columns.get("severity", [])
        + columns.get("duplicate_label", [])
        + columns.get("resolution", [])
        + columns.get("event", [])
    )

    if task in {"T1", "T2", "T3"}:

        if has_text:
            reasons.append("ticket text present")

        if outcome_columns:
            warnings.append(
                "source also contains outcome/label-like columns"
            )

        if has_id:
            reasons.append("ticket identifier present")

    elif task == "T4":

        if has_text:
            reasons.append("ticket/query text present")

        if has_assignee:
            reasons.append(
                "historical assignee field present"
            )

        if not has_assignee:
            warnings.append(
                "historical assignee candidate population "
                "not established"
            )

    elif task == "T5":

        if has_text:
            reasons.append("ticket text present")

        if has_id:
            reasons.append("ticket identifier present")

        if columns.get("duplicate_label"):
            warnings.append(
                "duplicate/outcome label present; "
                "must not be used as runtime input"
            )

    elif task == "T6":

        if has_text:
            reasons.append("ticket text present")

        if has_id:
            reasons.append("ticket identifier present")

        warnings.append(
            "retrieval-corpus suitability requires "
            "explicit population-level verification"
        )

    elif task == "T7":

        if has_time:
            reasons.append("time-related field present")

        if has_event:
            reasons.append("event/status field present")

        if has_time and has_event:
            reasons.append(
                "ticket-level survival semantics potentially present"
            )

    if task == "T5":
        source_role = (
            "TICKET_PAIR_SOURCE_CANDIDATE"
            if has_text and has_id
            else "NOT_ESTABLISHED"
        )

    elif task == "T6":
        source_role = (
            "RETRIEVAL_CORPUS_CANDIDATE"
            if has_text and has_id
            else "NOT_ESTABLISHED"
        )

    elif task == "T7":
        source_role = (
            "SURVIVAL_OBSERVATION_CANDIDATE"
            if has_time and has_event
            else "NOT_ESTABLISHED"
        )

    elif task == "T4":
        source_role = (
            "HISTORICAL_ASSIGNEE_SOURCE_CANDIDATE"
            if has_text and has_assignee
            else "NOT_ESTABLISHED"
        )

    else:
        source_role = (
            "TICKET_TEXT_SOURCE_CANDIDATE"
            if has_text
            else "NOT_ESTABLISHED"
        )

    return {
        "source_role": source_role,
        "positive_evidence": reasons,
        "warnings": warnings,
    }


def main() -> None:

    print("=" * 72)
    print("FMP-06 OP-015 — RUNTIME SOURCE SEMANTIC VALIDATION")
    print("=" * 72)
    print()
    print("Mode: READ-ONLY")
    print("No model loading")
    print("No inference")
    print("No retraining")
    print("No artifact modification")
    print()

    report = {
        "operation": "FMP-06 OP-015",
        "operation_type": (
            "READ_ONLY_RUNTIME_SOURCE_SEMANTIC_VALIDATION"
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

    for task, paths in CANDIDATES.items():

        print("-" * 72)
        print(task)

        task_records = []

        for path in paths:

            record = inspect_csv(path)

            if not record["exists"]:
                print(
                    "  MISSING:",
                    record["file"],
                )
                task_records.append(record)
                continue

            classification = classify_source(
                task,
                record,
            )

            record["classification"] = classification
            task_records.append(record)

            print(
                "  SOURCE:",
                record["file"],
            )
            print(
                "    rows:",
                record["row_count"],
            )
            print(
                "    columns:",
                record["columns"],
            )
            print(
                "    semantic columns:",
                record["semantic_columns"],
            )
            print(
                "    source role:",
                classification["source_role"],
            )

            for reason in classification[
                "positive_evidence"
            ]:
                print(
                    "    evidence:",
                    reason,
                )

            for warning in classification[
                "warnings"
            ]:
                print(
                    "    WARNING:",
                    warning,
                )

            print()

        report["tasks"][task] = {
            "candidate_count": len(task_records),
            "sources": task_records,
        }

    report["overall_status"] = "PASS"

    OUTPUT.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("=" * 72)
    print("OVERALL STATUS: PASS")
    print(f"OUTPUT: {OUTPUT}")
    print("=" * 72)


if __name__ == "__main__":
    main()