from __future__ import annotations

import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

INPUT_PATH = (
    PROJECT_ROOT
    / "modeling/T8/mod036/op025/"
      "t8_mod036_op025_decision_engine_predictions.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "modeling/FMP/metrics/"
      "f_op006_op025_row_population_verification.json"
)

EXPECTED_ROWS = 119_895
EXPECTED_COLUMNS = 19


def find_column(
    columns: list[str],
    candidates: list[str],
) -> str | None:

    normalized = {
        str(column).strip().lower(): str(column)
        for column in columns
    }

    for candidate in candidates:

        if candidate.lower() in normalized:
            return normalized[
                candidate.lower()
            ]

    return None


def main() -> None:

    print("=" * 72)
    print(
        "F-OP-006 — OP-025 ROW POPULATION "
        "VERIFICATION"
    )
    print("=" * 72)

    result = {
        "operation": "F-OP-006",
        "input_path": str(INPUT_PATH),
        "expected_rows": EXPECTED_ROWS,
        "expected_columns": EXPECTED_COLUMNS,
        "read_only": True,
        "model_modified": False,
        "retraining_performed": False,
        "threshold_selection_performed": False,
        "locked_test_reused_for_policy_selection": False,
    }

    if not INPUT_PATH.exists():

        result["status"] = "BLOCKED"
        result["error"] = "INPUT_FILE_NOT_FOUND"

        print(
            "Input file exists       : False"
        )

        print(
            "RESULT: BLOCKED — input file "
            "not found"
        )

        with OUTPUT_PATH.open(
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                result,
                f,
                indent=2,
            )

        return

    result["file_exists"] = True
    result["file_bytes"] = (
        INPUT_PATH.stat().st_size
    )

    row_count = 0
    columns = []
    first_row = None

    unique_ticket_ids = set()
    duplicate_ticket_ids = 0

    evidence_state_counts = {}
    component_count_counts = {}

    ticket_column = None
    evidence_state_column = None
    component_count_column = None

    with INPUT_PATH.open(
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

        ticket_column = find_column(
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

        evidence_state_column = find_column(
            columns,
            [
                "evidence_state",
                "decision_state",
                "evidence_status",
            ],
        )

        component_count_column = find_column(
            columns,
            [
                "evidence_component_count",
                "component_count",
                "n_evidence_components",
            ],
        )

        for row in reader:

            row_count += 1

            if first_row is None:
                first_row = row

            if ticket_column:

                ticket_id = row.get(
                    ticket_column
                )

                if ticket_id in unique_ticket_ids:

                    duplicate_ticket_ids += 1

                else:

                    unique_ticket_ids.add(
                        ticket_id
                    )

            if evidence_state_column:

                state = row.get(
                    evidence_state_column
                )

                evidence_state_counts[
                    state
                ] = (
                    evidence_state_counts.get(
                        state,
                        0,
                    )
                    + 1
                )

            if component_count_column:

                value = row.get(
                    component_count_column
                )

                component_count_counts[
                    value
                ] = (
                    component_count_counts.get(
                        value,
                        0,
                    )
                    + 1
                )

    result[
        "row_count"
    ] = row_count

    result[
        "column_count"
    ] = len(columns)

    result[
        "columns"
    ] = columns

    result[
        "ticket_id_column"
    ] = ticket_column

    result[
        "unique_ticket_ids"
    ] = len(unique_ticket_ids)

    result[
        "duplicate_ticket_ids"
    ] = duplicate_ticket_ids

    result[
        "evidence_state_column"
    ] = evidence_state_column

    result[
        "evidence_state_counts"
    ] = evidence_state_counts

    result[
        "component_count_column"
    ] = component_count_column

    result[
        "component_count_counts"
    ] = component_count_counts

    row_match = (
        row_count == EXPECTED_ROWS
    )

    column_match = (
        len(columns) == EXPECTED_COLUMNS
    )

    unique_match = (
        ticket_column is not None
        and len(unique_ticket_ids)
        == EXPECTED_ROWS
        and duplicate_ticket_ids == 0
    )

    expected_states = {
        "SUPPORTED",
        "CONFLICTING",
        "INSUFFICIENT_EVIDENCE",
        "UNAVAILABLE",
    }

    observed_states = set(
        evidence_state_counts.keys()
    )

    state_contract_present = (
        evidence_state_column is not None
        and observed_states.issubset(
            expected_states
        )
    )

    result[
        "row_count_match"
    ] = row_match

    result[
        "column_count_match"
    ] = column_match

    result[
        "unique_ticket_id_match"
    ] = unique_match

    result[
        "evidence_state_contract_present"
    ] = state_contract_present

    result[
        "population_identity"
    ] = (
        "119895_UNIQUE_TICKETS"
        if (
            row_match
            and unique_match
        )
        else "NOT_CONFIRMED"
    )

    all_required_checks = (
        row_match
        and column_match
        and unique_match
        and state_contract_present
    )

    result["status"] = (
        "PASS"
        if all_required_checks
        else "REQUIRES_REVIEW"
    )

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

    print(
        f"Input file exists       : "
        f"{INPUT_PATH.exists()}"
    )

    print(
        f"File size               : "
        f"{INPUT_PATH.stat().st_size} bytes"
    )

    print(
        f"Rows                    : "
        f"{row_count}"
    )

    print(
        f"Columns                 : "
        f"{len(columns)}"
    )

    print(
        f"Expected rows           : "
        f"{EXPECTED_ROWS}"
    )

    print(
        f"Expected columns        : "
        f"{EXPECTED_COLUMNS}"
    )

    print(
        f"Ticket ID column        : "
        f"{ticket_column}"
    )

    print(
        f"Unique ticket IDs       : "
        f"{len(unique_ticket_ids)}"
    )

    print(
        f"Duplicate ticket IDs    : "
        f"{duplicate_ticket_ids}"
    )

    print(
        f"Evidence-state column   : "
        f"{evidence_state_column}"
    )

    print(
        "Evidence-state counts   :"
    )

    for state, count in sorted(
        evidence_state_counts.items()
    ):
        print(
            f"  {state}: {count}"
        )

    print(
        f"Component-count column  : "
        f"{component_count_column}"
    )

    print(
        "Component-count counts  :"
    )

    for value, count in sorted(
        component_count_counts.items(),
        key=lambda item: str(item[0]),
    ):
        print(
            f"  {value}: {count}"
        )

    print()
    print(
        f"Row-count check         : "
        f"{row_match}"
    )

    print(
        f"Column-count check      : "
        f"{column_match}"
    )

    print(
        f"Unique-ID check         : "
        f"{unique_match}"
    )

    print(
        f"Evidence-state check    : "
        f"{state_contract_present}"
    )

    print(
        f"Population identity     : "
        f"{result['population_identity']}"
    )

    print(
        f"Output                  : "
        f"{OUTPUT_PATH}"
    )

    print("=" * 72)
    print(
        f"RESULT: {result['status']} — "
        "F-OP-006 complete"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()