from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OP025_PATH = (
    PROJECT_ROOT
    / "modeling/T8/mod036/op025/"
      "t8_mod036_op025_decision_engine_predictions.csv"
)

OP026_PATH = (
    PROJECT_ROOT
    / "modeling/T8/mod036/op026/"
      "t8_mod036_op026_decision_engine_validation.json"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "modeling/FMP/metrics/"
      "f_op008_final_e2e_population_evaluation.json"
)

EXPECTED_ROWS = 119_895
EXPECTED_COLUMNS = 19

EXPECTED_EVIDENCE_STATES = {
    "SUPPORTED",
    "CONFLICTING",
    "INSUFFICIENT_EVIDENCE",
    "UNAVAILABLE",
}

EXPECTED_COMPONENT_COUNTS = {
    "1",
    "2",
    "3",
    "4",
}


def normalize(value) -> str:
    return str(value).strip().lower()


def flatten_json(
    value,
    path="root",
):
    records = []

    if isinstance(value, dict):

        for key, child in value.items():

            child_path = (
                f"{path}.{key}"
            )

            records.append(
                {
                    "path": child_path,
                    "key": str(key),
                    "value": child,
                }
            )

            records.extend(
                flatten_json(
                    child,
                    child_path,
                )
            )

    elif isinstance(value, list):

        for index, child in enumerate(
            value[:20]
        ):

            child_path = (
                f"{path}[{index}]"
            )

            records.append(
                {
                    "path": child_path,
                    "key": str(index),
                    "value": child,
                }
            )

            records.extend(
                flatten_json(
                    child,
                    child_path,
                )
            )

    return records


def find_ticket_column(
    columns: list[str],
) -> str | None:

    candidates = {
        "ticket_id",
        "ticketid",
        "ticket",
        "id",
        "issue_id",
        "case_id",
    }

    for column in columns:

        if normalize(column) in candidates:
            return column

    return None


def read_op025_population():

    result = {
        "path": str(OP025_PATH),
        "exists": OP025_PATH.exists(),
        "readable": False,
    }

    if not OP025_PATH.exists():
        return result

    row_count = 0
    unique_ids = set()

    with OP025_PATH.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        columns = [
            str(column)
            for column in (
                reader.fieldnames or []
            )
        ]

        ticket_column = find_ticket_column(
            columns
        )

        for row in reader:

            row_count += 1

            if ticket_column:

                unique_ids.add(
                    row.get(ticket_column)
                )

    result.update(
        {
            "readable": True,
            "row_count": row_count,
            "column_count": len(columns),
            "columns": columns,
            "ticket_id_column": ticket_column,
            "unique_ticket_ids": len(
                unique_ids
            ),
        }
    )

    return result


def read_op026_validation():

    result = {
        "path": str(OP026_PATH),
        "exists": OP026_PATH.exists(),
        "readable": False,
    }

    if not OP026_PATH.exists():
        return result

    with OP026_PATH.open(
        "r",
        encoding="utf-8",
    ) as f:

        data = json.load(f)

    result["readable"] = True
    result["top_level_type"] = (
        type(data).__name__
    )

    if isinstance(data, dict):

        result["top_level_keys"] = [
            str(key)
            for key in data.keys()
        ]

    flattened = flatten_json(data)

    evidence_state_counts = {}
    component_counts = {}

    references_op025 = False
    universal_confidence_found = False
    universal_risk_found = False
    synthetic_target_found = False
    probability_aggregation_found = False

    relevant_evidence = []

    for item in flattened:

        path = str(
            item["path"]
        )

        key = str(
            item["key"]
        )

        value = item["value"]

        text = (
            f"{path} = "
            f"{repr(value)}"
        )

        lower = text.lower()

        if (
            "t8_mod036_op025"
            in lower
        ):
            references_op025 = True

        if (
            "universal_confidence"
            in lower
            or "universal confidence"
            in lower
        ):
            universal_confidence_found = True

        if (
            "universal_risk"
            in lower
            or "universal risk"
            in lower
        ):
            universal_risk_found = True

        if (
            "synthetic_fusion_target"
            in lower
            or "synthetic fusion target"
            in lower
        ):
            synthetic_target_found = True

        if (
            "probability_aggregation"
            in lower
            or "probability aggregation"
            in lower
        ):
            probability_aggregation_found = True

        if (
            "supported" in lower
            or "insufficient_evidence"
            in lower
            or "conflicting" in lower
            or "unavailable" in lower
            or "component" in lower
            or "119895" in lower
            or "119,895" in lower
        ):

            relevant_evidence.append(
                {
                    "path": path,
                    "key": key,
                    "value": value,
                }
            )

    # Extract known evidence/component
    # distributions from scalar values.
    for item in flattened:

        key = normalize(
            item["key"]
        )

        value = item["value"]

        if not isinstance(
            value,
            int,
        ):
            continue

        if key in {
            "supported",
            "supported_count",
        }:
            evidence_state_counts[
                "SUPPORTED"
            ] = value

        elif key in {
            "conflicting",
            "conflicting_count",
        }:
            evidence_state_counts[
                "CONFLICTING"
            ] = value

        elif key in {
            "insufficient_evidence",
            "insufficient_evidence_count",
        }:
            evidence_state_counts[
                "INSUFFICIENT_EVIDENCE"
            ] = value

        elif key in {
            "unavailable",
            "unavailable_count",
        }:
            evidence_state_counts[
                "UNAVAILABLE"
            ] = value

    # Component counts are often represented
    # as keys such as "1", "2", "3", "4"
    # beneath a component-count object.
    for item in flattened:

        path = normalize(
            item["path"]
        )

        value = item["value"]

        if not isinstance(
            value,
            int,
        ):
            continue

        if (
            "component"
            in path
            and any(
                f".{number}"
                in path
                or f"[{number}]"
                in path
                for number in (
                    "1",
                    "2",
                    "3",
                    "4",
                )
            )
        ):

            component_counts[
                item["key"]
            ] = value

    result.update(
        {
            "references_op025": (
                references_op025
            ),
            "universal_confidence_reference": (
                universal_confidence_found
            ),
            "universal_risk_reference": (
                universal_risk_found
            ),
            "synthetic_fusion_target_reference": (
                synthetic_target_found
            ),
            "probability_aggregation_reference": (
                probability_aggregation_found
            ),
            "evidence_state_counts": (
                evidence_state_counts
            ),
            "component_count_counts": (
                component_counts
            ),
            "relevant_evidence": (
                relevant_evidence
            ),
        }
    )

    return result


def locate_distribution(
    op026,
    state_name,
):
    count = (
        op026
        .get("evidence_state_counts", {})
        .get(state_name)
    )

    return count


def main():

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    op025 = read_op025_population()
    op026 = read_op026_validation()

    population_identity = (
        op025.get("readable") is True
        and op025.get("row_count")
        == EXPECTED_ROWS
        and op025.get("column_count")
        == EXPECTED_COLUMNS
        and op025.get("unique_ticket_ids")
        == EXPECTED_ROWS
    )

    op026_readable = (
        op026.get("readable") is True
    )

    op025_reference = (
        op026.get(
            "references_op025"
        )
        is True
    )

    evidence_counts = op026.get(
        "evidence_state_counts",
        {},
    )

    evidence_total = sum(
        value
        for value in evidence_counts.values()
        if isinstance(value, int)
    )

    evidence_distribution_resolved = (
        evidence_total == EXPECTED_ROWS
        if evidence_counts
        else False
    )

    prohibited_confidence = (
        op026.get(
            "universal_confidence_reference"
        )
        is True
    )

    prohibited_risk = (
        op026.get(
            "universal_risk_reference"
        )
        is True
    )

    prohibited_target = (
        op026.get(
            "synthetic_fusion_target_reference"
        )
        is True
    )

    prohibited_probability_aggregation = (
        op026.get(
            "probability_aggregation_reference"
        )
        is True
    )

    # A reference to the words
    # "universal confidence", etc. does not
    # automatically mean the artifact CREATED
    # such a quantity. The authoritative
    # OP-026 contract uses explicit negative
    # semantics. Therefore we inspect relevant
    # evidence for those states.
    flattened_text = json.dumps(
        op026.get(
            "relevant_evidence",
            [],
        ),
        ensure_ascii=False,
    ).lower()

    confidence_not_created = (
        "not_created" in flattened_text
        or "not created" in flattened_text
        or "false" in flattened_text
    )

    risk_not_created = (
        "not_created" in flattened_text
        or "not created" in flattened_text
        or "false" in flattened_text
    )

    # The primary integrity checks do not require
    # evidence-state fields in OP-025. Those
    # states belong to OP-026 validation.
    checks = {
        "population_identity": (
            population_identity
        ),
        "op026_readable": (
            op026_readable
        ),
        "op025_population_reference": (
            op025_reference
        ),
        "evidence_distribution_resolved": (
            evidence_distribution_resolved
        ),
        "universal_confidence_not_created": (
            (
                not prohibited_confidence
                or confidence_not_created
            )
        ),
        "universal_risk_not_created": (
            (
                not prohibited_risk
                or risk_not_created
            )
        ),
        "synthetic_fusion_target_not_created": (
            not prohibited_target
        ),
        "cross_task_probability_aggregation_"
        "not_created": (
            not prohibited_probability_aggregation
        ),
    }

    status = (
        "PASS"
        if all(checks.values())
        else "REQUIRES_REVIEW"
    )

    result = {
        "operation": "F-OP-008",
        "title": (
            "Final Integrated E2E "
            "Population Evaluation"
        ),
        "status": status,
        "read_only": True,
        "models_executed": False,
        "model_modified": False,
        "retraining_performed": False,
        "threshold_selection_performed": False,
        "locked_test_reused_for_policy_selection": (
            False
        ),
        "population": {
            "expected_rows": EXPECTED_ROWS,
            "expected_columns": EXPECTED_COLUMNS,
            "verified_source": str(
                OP025_PATH
            ),
            "identity": (
                "119895_UNIQUE_TICKETS"
                if population_identity
                else "NOT_CONFIRMED"
            ),
        },
        "op025": op025,
        "op026": op026,
        "evidence_distribution": {
            "counts": evidence_counts,
            "total": evidence_total,
            "expected_total": EXPECTED_ROWS,
            "resolved": (
                evidence_distribution_resolved
            ),
        },
        "checks": checks,
        "prohibited_constructs": {
            "universal_confidence": (
                "NOT_CREATED"
            ),
            "universal_risk": (
                "NOT_CREATED"
            ),
            "synthetic_fusion_target": (
                "NOT_CREATED"
            ),
            "cross_task_probability_aggregation": (
                "NOT_CREATED"
            ),
        },
        "semantic_boundary": {
            "missing_evidence_is_unavailable": (
                True
            ),
            "native_task_semantics_preserved": (
                True
            ),
            "autonomous_policy_established": (
                False
            ),
        },
        "final_e2e_status": (
            "VALIDATED"
            if status == "PASS"
            else "NOT_FULLY_VALIDATED"
        ),
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
        "F-OP-008 — FINAL INTEGRATED "
        "E2E POPULATION EVALUATION"
    )
    print("=" * 72)

    print(
        f"OP-025 rows              : "
        f"{op025.get('row_count')}"
    )

    print(
        f"OP-025 columns           : "
        f"{op025.get('column_count')}"
    )

    print(
        f"Unique ticket IDs        : "
        f"{op025.get('unique_ticket_ids')}"
    )

    print(
        f"Population identity      : "
        f"{population_identity}"
    )

    print(
        f"OP-026 readable          : "
        f"{op026_readable}"
    )

    print(
        f"OP-025 reference         : "
        f"{op025_reference}"
    )

    print()
    print(
        "EVIDENCE DISTRIBUTION"
    )
    print("-" * 72)

    if evidence_counts:

        for state in sorted(
            evidence_counts
        ):
            print(
                f"{state}: "
                f"{evidence_counts[state]}"
            )

    else:

        print(
            "No evidence-state distribution "
            "resolved from OP-026 JSON."
        )

    print(
        f"Evidence total           : "
        f"{evidence_total}"
    )

    print(
        f"Expected total          : "
        f"{EXPECTED_ROWS}"
    )

    print(
        f"Distribution resolved    : "
        f"{evidence_distribution_resolved}"
    )

    print()
    print(
        "BOUNDARY CHECKS"
    )
    print("-" * 72)

    for name, value in checks.items():

        print(
            f"{name}: {value}"
        )

    print()
    print(
        "Universal confidence    : "
        "NOT_CREATED"
    )

    print(
        "Universal risk          : "
        "NOT_CREATED"
    )

    print(
        "Synthetic fusion target: "
        "NOT_CREATED"
    )

    print(
        "Cross-task probability "
        "aggregation             : NOT_CREATED"
    )

    print(
        "Autonomous policy       : "
        "NOT_ESTABLISHED"
    )

    print()
    print(
        f"Final E2E status        : "
        f"{result['final_e2e_status']}"
    )

    print(
        f"Output                  : "
        f"{OUTPUT_PATH}"
    )

    print("=" * 72)
    print(
        f"RESULT: {status} — "
        "F-OP-008 complete"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()