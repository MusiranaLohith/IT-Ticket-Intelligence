from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T8_OP026_DIR = (
    PROJECT_ROOT / "modeling/T8/mod036/op026"
)

METRICS_DIR = (
    PROJECT_ROOT / "modeling/FMP/metrics"
)

OUTPUT_PATH = (
    METRICS_DIR
    / "f_op002_final_e2e_integrated_population_evaluation.json"
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def flatten(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(
            f"{flatten(k)} {flatten(v)}"
            for k, v in value.items()
        )

    if isinstance(value, list):
        return " ".join(
            flatten(v)
            for v in value
        )

    return str(value)


def find_json_files(root: Path) -> list[Path]:
    if not root.exists():
        return []

    return sorted(
        root.rglob("*.json")
    )


def score_candidate(path: Path) -> int:
    name = path.name.lower()

    score = 0

    priority_terms = [
        "prediction",
        "predictions",
        "e2e",
        "integrated",
        "validation",
        "decision",
    ]

    for term in priority_terms:
        if term in name:
            score += 1

    return score


def choose_primary_artifact(
    files: list[Path],
) -> Path | None:

    candidates = []

    for path in files:
        try:
            data = load_json(path)
        except Exception:
            continue

        if not isinstance(data, dict):
            continue

        text = flatten(data).lower()

        signal_count = 0

        for term in [
            "prediction",
            "ticket",
            "evidence",
            "state",
            "provenance",
            "insufficient",
            "supported",
        ]:
            if term in text:
                signal_count += 1

        filename_score = score_candidate(path)

        candidates.append(
            (
                filename_score + signal_count,
                path.stat().st_size,
                path,
            )
        )

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: (
            -x[0],
            -x[1],
            str(x[2]),
        )
    )

    return candidates[0][2]


def extract_rows(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        if all(
            isinstance(item, dict)
            for item in data
        ):
            return data

        return []

    if not isinstance(data, dict):
        return []

    candidate_keys = [
        "predictions",
        "prediction_rows",
        "records",
        "rows",
        "results",
        "data",
    ]

    for key in candidate_keys:
        value = data.get(key)

        if isinstance(value, list):
            if all(
                isinstance(item, dict)
                for item in value
            ):
                return value

    return []


def find_key(
    row: dict[str, Any],
    candidates: list[str],
) -> str | None:

    normalized = {
        str(key).lower(): key
        for key in row.keys()
    }

    for candidate in candidates:
        if candidate.lower() in normalized:
            return normalized[candidate.lower()]

    return None


def count_values(
    rows: list[dict[str, Any]],
    candidates: list[str],
) -> dict[str, int]:

    key = None

    for row in rows:
        key = find_key(
            row,
            candidates,
        )

        if key is not None:
            break

    if key is None:
        return {}

    counts: dict[str, int] = {}

    for row in rows:
        value = row.get(key)

        if value is None:
            label = "NULL"
        else:
            label = str(value)

        counts[label] = (
            counts.get(label, 0) + 1
        )

    return dict(
        sorted(
            counts.items(),
            key=lambda item: (-item[1], item[0]),
        )
    )


def main() -> None:
    METRICS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_files = find_json_files(
        T8_OP026_DIR
    )

    if not json_files:
        print("=" * 72)
        print(
            "F-OP-002 — FINAL E2E INTEGRATED "
            "POPULATION EVALUATION"
        )
        print("=" * 72)
        print(
            "RESULT: BLOCKED — no T8 OP-026 JSON artifacts found"
        )
        print("=" * 72)
        return

    primary = choose_primary_artifact(
        json_files
    )

    if primary is None:
        print("=" * 72)
        print(
            "F-OP-002 — FINAL E2E INTEGRATED "
            "POPULATION EVALUATION"
        )
        print("=" * 72)
        print(
            "RESULT: BLOCKED — no readable integrated artifact found"
        )
        print("=" * 72)
        return

    data = load_json(primary)

    rows = extract_rows(data)

    # ------------------------------------------------------------
    # Population identity
    # ------------------------------------------------------------

    ticket_key = None

    if rows:
        for candidate in [
            "ticket_id",
            "ticketid",
            "id",
            "issue_id",
            "case_id",
        ]:
            ticket_key = find_key(
                rows[0],
                [candidate],
            )

            if ticket_key is not None:
                break

    ticket_values = []

    if ticket_key is not None:
        ticket_values = [
            row.get(ticket_key)
            for row in rows
        ]

    non_null_ticket_values = [
        value
        for value in ticket_values
        if value is not None
    ]

    unique_ticket_count = len(
        set(
            str(value)
            for value in non_null_ticket_values
        )
    )

    duplicate_ticket_rows = (
        len(non_null_ticket_values)
        - unique_ticket_count
    )

    null_ticket_count = (
        len(ticket_values)
        - len(non_null_ticket_values)
    )

    # ------------------------------------------------------------
    # Evidence state
    # ------------------------------------------------------------

    evidence_state_counts = count_values(
        rows,
        [
            "evidence_state",
            "decision_state",
            "t8_evidence_state",
        ],
    )

    # ------------------------------------------------------------
    # Component count
    # ------------------------------------------------------------

    component_count_counts = count_values(
        rows,
        [
            "evidence_component_count",
            "component_count",
            "t8_component_count",
        ],
    )

    # ------------------------------------------------------------
    # Availability / provenance
    # ------------------------------------------------------------

    provenance_counts = count_values(
        rows,
        [
            "provenance",
            "provenance_complete",
            "has_provenance",
        ],
    )

    availability_counts = count_values(
        rows,
        [
            "availability",
            "evidence_available",
            "available",
        ],
    )

    conflict_counts = count_values(
        rows,
        [
            "conflict",
            "conflicting_evidence",
            "evidence_conflict",
        ],
    )

    # ------------------------------------------------------------
    # Unsupported universal fields
    # ------------------------------------------------------------

    universal_confidence_fields = []
    universal_risk_fields = []

    if rows:
        for key in rows[0].keys():
            key_lower = str(key).lower()

            if (
                "universal" in key_lower
                and "confidence" in key_lower
            ):
                universal_confidence_fields.append(
                    str(key)
                )

            if (
                "universal" in key_lower
                and "risk" in key_lower
            ):
                universal_risk_fields.append(
                    str(key)
                )

    # ------------------------------------------------------------
    # Read-only integrity checks
    # ------------------------------------------------------------

    integrity_failures = []

    if not rows:
        integrity_failures.append(
            "PRIMARY_ARTIFACT_HAS_NO_ROW_RECORDS"
        )

    if ticket_key is None and rows:
        integrity_failures.append(
            "NO_TICKET_ID_FIELD_IDENTIFIED"
        )

    if duplicate_ticket_rows > 0:
        integrity_failures.append(
            "DUPLICATE_TICKET_ROWS_PRESENT"
        )

    if null_ticket_count > 0:
        integrity_failures.append(
            "NULL_TICKET_IDS_PRESENT"
        )

    if universal_confidence_fields:
        integrity_failures.append(
            "UNSUPPORTED_UNIVERSAL_CONFIDENCE_FIELD_PRESENT"
        )

    if universal_risk_fields:
        integrity_failures.append(
            "UNSUPPORTED_UNIVERSAL_RISK_FIELD_PRESENT"
        )

    status = (
        "PASS"
        if not integrity_failures
        else "REQUIRES_REVIEW"
    )

    result = {
        "operation": "F-OP-002",
        "title": (
            "Final E2E Integrated Population Evaluation"
        ),
        "status": status,
        "read_only": True,
        "models_executed": False,
        "model_modified": False,
        "retraining_performed": False,
        "threshold_selection_performed": False,
        "threshold_optimization_performed": False,
        "locked_test_reused_for_policy_selection": False,
        "primary_artifact": str(primary),
        "all_op026_json_files": [
            str(path)
            for path in json_files
        ],
        "population": {
            "row_count": len(rows),
            "ticket_id_field": ticket_key,
            "non_null_ticket_ids": len(
                non_null_ticket_values
            ),
            "unique_ticket_count": unique_ticket_count,
            "duplicate_ticket_rows": duplicate_ticket_rows,
            "null_ticket_count": null_ticket_count,
        },
        "evidence_state_counts": (
            evidence_state_counts
        ),
        "component_count_counts": (
            component_count_counts
        ),
        "provenance_counts": provenance_counts,
        "availability_counts": availability_counts,
        "conflict_counts": conflict_counts,
        "unsupported_universal_fields": {
            "confidence": universal_confidence_fields,
            "risk": universal_risk_fields,
        },
        "integrity_failures": integrity_failures,
        "interpretation": {
            "missing_evidence_is_not_negative": True,
            "native_task_semantics_preserved": True,
            "universal_confidence_not_created": (
                not universal_confidence_fields
            ),
            "universal_risk_not_created": (
                not universal_risk_fields
            ),
        },
    }

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("=" * 72)
    print(
        "F-OP-002 — FINAL E2E INTEGRATED "
        "POPULATION EVALUATION"
    )
    print("=" * 72)

    print(
        f"OP-026 JSON artifacts : {len(json_files)}"
    )
    print(
        f"Primary artifact      : {primary.name}"
    )

    print()
    print("POPULATION")
    print("-" * 72)
    print(
        f"Rows                  : {len(rows)}"
    )
    print(
        f"Ticket ID field       : {ticket_key}"
    )
    print(
        f"Unique tickets        : {unique_ticket_count}"
    )
    print(
        f"Duplicate ticket rows : {duplicate_ticket_rows}"
    )
    print(
        f"Null ticket IDs       : {null_ticket_count}"
    )

    print()
    print("EVIDENCE STATES")
    print("-" * 72)

    if evidence_state_counts:
        for key, value in evidence_state_counts.items():
            print(
                f"{key}: {value}"
            )
    else:
        print(
            "No explicit evidence-state field identified"
        )

    print()
    print("COMPONENT COUNTS")
    print("-" * 72)

    if component_count_counts:
        for key, value in component_count_counts.items():
            print(
                f"{key}: {value}"
            )
    else:
        print(
            "No explicit component-count field identified"
        )

    print()
    print("UNSUPPORTED UNIVERSAL FIELDS")
    print("-" * 72)
    print(
        "Universal confidence fields: "
        f"{len(universal_confidence_fields)}"
    )
    print(
        "Universal risk fields      : "
        f"{len(universal_risk_fields)}"
    )

    print()
    print(
        f"Integrity failures    : {len(integrity_failures)}"
    )
    print(
        f"Status                : {status}"
    )
    print(
        f"Output                : {OUTPUT_PATH}"
    )

    print("=" * 72)
    print(
        f"RESULT: {status} — F-OP-002 complete"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()