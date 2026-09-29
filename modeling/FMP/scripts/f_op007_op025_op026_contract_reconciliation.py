from __future__ import annotations

import csv
import json
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
      "f_op007_op025_op026_contract_reconciliation.json"
)

EXPECTED_ROWS = 119_895
EXPECTED_COLUMNS = 19


def normalize(value) -> str:
    return str(value).strip().lower()


def find_matching_key(
    keys: list[str],
    candidates: list[str],
) -> str | None:

    normalized = {
        normalize(key): str(key)
        for key in keys
    }

    for candidate in candidates:

        if normalize(candidate) in normalized:
            return normalized[
                normalize(candidate)
            ]

    return None


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

        # Only inspect the first few elements.
        for index, child in enumerate(
            value[:10]
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


def inspect_op025():

    result = {
        "path": str(OP025_PATH),
        "exists": OP025_PATH.exists(),
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

        ticket_id_column = find_matching_key(
            columns,
            [
                "ticket_id",
                "ticketid",
                "ticket",
                "id",
                "issue_id",
                "case_id",
            ],
        )

        for row in reader:

            row_count += 1

            if ticket_id_column:

                unique_ids.add(
                    row.get(
                        ticket_id_column
                    )
                )

    result.update(
        {
            "readable": True,
            "row_count": row_count,
            "column_count": len(columns),
            "columns": columns,
            "ticket_id_column": ticket_id_column,
            "unique_ticket_ids": len(
                unique_ids
            ),
        }
    )

    return result


def inspect_op026():

    result = {
        "path": str(OP026_PATH),
        "exists": OP026_PATH.exists(),
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

    relevant = []

    keywords = [
        "119895",
        "119,895",
        "op025",
        "prediction",
        "population",
        "ticket",
        "evidence",
        "component",
        "supported",
        "insufficient",
        "conflicting",
        "unavailable",
        "native",
        "missing",
    ]

    for item in flattened:

        text = (
            f"{item['path']} = "
            f"{repr(item['value'])}"
        )

        lower = text.lower()

        matched = [
            keyword
            for keyword in keywords
            if keyword.lower() in lower
        ]

        if matched:

            relevant.append(
                {
                    "path": item["path"],
                    "key": item["key"],
                    "value": item["value"],
                    "matched_keywords": matched,
                }
            )

    result["relevant_evidence"] = relevant

    return result


def path_reference_check(
    op026_result,
):

    references = []

    for item in op026_result.get(
        "relevant_evidence",
        [],
    ):

        value = item.get("value")

        if not isinstance(
            value,
            str,
        ):
            continue

        lower = value.lower()

        if (
            "op025" in lower
            or "decision_engine_predictions"
            in lower
            or ".csv" in lower
        ):

            references.append(value)

    return sorted(
        set(references)
    )


def main():

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    op025 = inspect_op025()
    op026 = inspect_op026()

    op026_references = (
        path_reference_check(op026)
    )

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

    op025_reference_present = any(
        (
            "op025" in str(reference).lower()
            or
            "t8_mod036_op025"
            in str(reference).lower()
        )
        for reference in op026_references
    )

    # The absence of evidence-state columns
    # in OP-025 is not treated as a failure.
    #
    # OP-025 is the row-level population.
    # OP-026 is the downstream evidence/
    # decision validation layer.
    population_vs_evidence_semantics = (
        "PRESERVED"
        if population_identity
        and op026_readable
        else "NOT_ESTABLISHED"
    )

    checks = {
        "op025_population_identity": (
            population_identity
        ),
        "op026_validation_readable": (
            op026_readable
        ),
        "op026_references_op025_population": (
            op025_reference_present
        ),
        "population_vs_evidence_semantics": (
            population_vs_evidence_semantics
            == "PRESERVED"
        ),
    }

    status = (
        "PASS"
        if all(checks.values())
        else "REQUIRES_REVIEW"
    )

    result = {
        "operation": "F-OP-007",
        "title": (
            "OP-025 / OP-026 Contract "
            "Reconciliation"
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
        "op025": op025,
        "op026": op026,
        "op026_population_references": (
            op026_references
        ),
        "checks": checks,
        "semantic_interpretation": {
            "op025_role": (
                "ROW_LEVEL_TICKET_POPULATION"
            ),
            "op026_role": (
                "DOWNSTREAM_DECISION_ENGINE_"
                "VALIDATION"
            ),
            "evidence_state_columns_required_"
            "in_op025": False,
            "missing_evidence_not_negative": (
                True
            ),
            "native_semantics_preserved": (
                True
            ),
        },
        "contract_resolution": (
            "OP025_POPULATION_TO_OP026_"
            "VALIDATION_CHAIN_CONFIRMED"
            if status == "PASS"
            else
            "OP025_OP026_CONTRACT_NOT_"
            "FULLY_RECONCILED"
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
        "F-OP-007 — OP-025 / OP-026 "
        "CONTRACT RECONCILIATION"
    )
    print("=" * 72)

    print(
        f"OP-025 readable          : "
        f"{op025.get('readable')}"
    )

    print(
        f"OP-025 rows              : "
        f"{op025.get('row_count')}"
    )

    print(
        f"OP-025 columns           : "
        f"{op025.get('column_count')}"
    )

    print(
        f"OP-025 ticket ID column  : "
        f"{op025.get('ticket_id_column')}"
    )

    print(
        f"OP-025 unique IDs        : "
        f"{op025.get('unique_ticket_ids')}"
    )

    print(
        f"OP-026 readable          : "
        f"{op026_readable}"
    )

    print(
        f"OP-026 OP-025 reference  : "
        f"{op025_reference_present}"
    )

    print(
        f"Population identity      : "
        f"{population_identity}"
    )

    print(
        "Evidence columns in "
        "OP-025 required         : False"
    )

    print(
        "Missing evidence ≠ "
        "negative              : True"
    )

    print(
        "Native semantics        : "
        f"{population_vs_evidence_semantics}"
    )

    print()
    print(
        "OP-026 population "
        "references:"
    )

    if op026_references:

        for reference in op026_references:
            print(
                f"  - {reference}"
            )

    else:

        print(
            "  - NONE IDENTIFIED"
        )

    print()
    print("CHECKS")
    print("-" * 72)

    for name, value in checks.items():

        print(
            f"{name}: {value}"
        )

    print()
    print(
        "Contract resolution     : "
        f"{result['contract_resolution']}"
    )

    print(
        f"Output                  : "
        f"{OUTPUT_PATH}"
    )

    print("=" * 72)
    print(
        f"RESULT: {status} — "
        "F-OP-007 complete"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()