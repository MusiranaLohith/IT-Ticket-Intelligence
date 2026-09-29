#!/usr/bin/env python3

"""
T7 MOD-004 — Feature Boundary + Temporal Split Audit

Purpose
-------
Audit the finalized T7 Creation-time modeling dataset before freezing
the chronological train/evaluation split.

This operation:
    1. validates the finalized dataset schema;
    2. validates the Creation-time feature whitelist;
    3. measures feature missingness and cardinality;
    4. audits target/event/censoring structure;
    5. establishes Creation-time temporal coverage;
    6. verifies temporal ordering is usable;
    7. evaluates a diagnostic chronological 80/20 boundary;
    8. reports event/censoring distributions around that boundary;
    9. checks for obvious target-derived feature leakage.

IMPORTANT
---------
The 80/20 chronological boundary is DIAGNOSTIC ONLY in MOD-004.
It is NOT frozen by this operation because the T7 modeling contract
requires the chronological split to be explicitly frozen later.

No raw Mozilla CORE archive is accessed.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


# Allow Mozilla CORE ticket descriptions/summaries larger than Python's
# default 131072-byte CSV field limit.
csv.field_size_limit(sys.maxsize)


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

INPUT_DATASET = (
    PROJECT_ROOT
    / "modeling"
    / "T7"
    / "derived"
    / "t7_creation_time_modeling_dataset.csv"
)

OUTPUT_AUDIT = (
    PROJECT_ROOT
    / "modeling"
    / "T7"
    / "metrics"
    / "t7_mod004_feature_temporal_split_audit.json"
)


# ---------------------------------------------------------------------------
# Frozen T7 predictive feature boundary
# ---------------------------------------------------------------------------

PREDICTIVE_FEATURES = [
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
]


# ---------------------------------------------------------------------------
# T7 target / evidence columns
# ---------------------------------------------------------------------------

TARGET_COLUMNS = {
    "ID",
    "Creation time",
    "first_resolved_time",
    "duration_seconds",
    "event",
    "endpoint_type",
    "observation_endpoint",
    "source_row_width",
}


# ---------------------------------------------------------------------------
# Explicitly forbidden post-Creation / outcome-derived terms
# ---------------------------------------------------------------------------

FORBIDDEN_FEATURE_TERMS = [
    "status",
    "resolution",
    "resolved",
    "duration",
    "event",
    "endpoint",
    "history",
    "created",
    "creation",
]


def fail(message: str) -> None:
    print(
        f"\nERROR: {message}",
        file=sys.stderr,
    )
    raise SystemExit(1)


def parse_creation(value: str) -> datetime:
    """
    Parse accepted target Creation time.

    The accepted T7 target stores Creation as timezone-naive wall-clock
    timestamps corresponding to UTC+05:30.

    For temporal ordering itself, wall-clock ordering is sufficient.
    """
    value = value.strip()

    if not value:
        raise ValueError(
            "empty Creation time"
        )

    return datetime.fromisoformat(
        value.replace("Z", "")
    )


def parse_int(
    value: str,
    field_name: str,
) -> int:
    value = value.strip()

    if value == "":
        raise ValueError(
            f"empty integer field: {field_name}"
        )

    return int(value)


def percentile(
    sorted_values: list[datetime],
    fraction: float,
) -> datetime:
    if not sorted_values:
        raise ValueError(
            "cannot calculate percentile of empty list"
        )

    if len(sorted_values) == 1:
        return sorted_values[0]

    position = fraction * (
        len(sorted_values) - 1
    )

    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return sorted_values[lower]

    lower_value = sorted_values[lower]
    upper_value = sorted_values[upper]

    return lower_value + (
        upper_value - lower_value
    ) * (position - lower)


def summarize_feature(
    name: str,
    values: list[str],
) -> dict:
    total = len(values)

    missing = sum(
        1
        for value in values
        if value.strip() == ""
    )

    non_missing_values = [
        value
        for value in values
        if value.strip() != ""
    ]

    counts = Counter(
        non_missing_values
    )

    return {
        "rows": total,
        "missing": missing,
        "missing_rate": (
            missing / total
            if total
            else None
        ),
        "non_missing": len(
            non_missing_values
        ),
        "unique_non_missing": len(
            counts
        ),
        "top_values": [
            {
                "value": value,
                "count": count,
            }
            for value, count
            in counts.most_common(10)
        ],
    }


def event_summary(
    rows: list[dict],
) -> dict:
    total = len(rows)

    event_1 = sum(
        1
        for row in rows
        if row["event"] == 1
    )

    event_0 = sum(
        1
        for row in rows
        if row["event"] == 0
    )

    return {
        "rows": total,
        "event_1": event_1,
        "event_0": event_0,
        "event_rate": (
            event_1 / total
            if total
            else None
        ),
        "censor_rate": (
            event_0 / total
            if total
            else None
        ),
    }


def temporal_summary(
    rows: list[dict],
) -> dict:
    creation_times = sorted(
        row["_creation_dt"]
        for row in rows
    )

    if not creation_times:
        fail(
            "No valid Creation timestamps found."
        )

    return {
        "min_creation": (
            creation_times[0].isoformat()
        ),
        "max_creation": (
            creation_times[-1].isoformat()
        ),
        "p01_creation": percentile(
            creation_times,
            0.01,
        ).isoformat(),
        "p05_creation": percentile(
            creation_times,
            0.05,
        ).isoformat(),
        "p25_creation": percentile(
            creation_times,
            0.25,
        ).isoformat(),
        "p50_creation": percentile(
            creation_times,
            0.50,
        ).isoformat(),
        "p75_creation": percentile(
            creation_times,
            0.75,
        ).isoformat(),
        "p95_creation": percentile(
            creation_times,
            0.95,
        ).isoformat(),
        "p99_creation": percentile(
            creation_times,
            0.99,
        ).isoformat(),
    }


def check_temporal_order(
    rows: list[dict],
) -> dict:
    """
    Verify that Creation times can be sorted into a valid chronological
    ordering and count exact timestamp ties.
    """
    creation_times = [
        row["_creation_dt"]
        for row in rows
    ]

    ordered = sorted(
        creation_times
    )

    backwards = 0

    for previous, current in zip(
        creation_times,
        creation_times[1:],
    ):
        if current < previous:
            backwards += 1

    ties = 0

    for previous, current in zip(
        ordered,
        ordered[1:],
    ):
        if current == previous:
            ties += 1

    return {
        "rows_checked": len(rows),
        "input_order_backwards_transitions": (
            backwards
        ),
        "exact_creation_timestamp_ties": ties,
        "chronological_sort_available": True,
    }


def diagnostic_chronological_split(
    rows: list[dict],
    fraction: float = 0.80,
) -> dict:
    """
    Evaluate an 80/20 chronological split for diagnostic purposes only.

    This does NOT freeze the split.
    """
    ordered = sorted(
        rows,
        key=lambda row: (
            row["_creation_dt"],
            row["ID"],
        ),
    )

    total = len(ordered)

    split_index = int(
        total * fraction
    )

    if (
        split_index <= 0
        or split_index >= total
    ):
        fail(
            "Diagnostic split produced "
            "an invalid boundary."
        )

    train_rows = ordered[
        :split_index
    ]

    eval_rows = ordered[
        split_index:
    ]

    train_last = (
        train_rows[-1]["_creation_dt"]
    )

    eval_first = (
        eval_rows[0]["_creation_dt"]
    )

    train_summary = event_summary(
        train_rows
    )

    eval_summary = event_summary(
        eval_rows
    )

    return {
        "status": (
            "DIAGNOSTIC_ONLY_NOT_FROZEN"
        ),
        "candidate_fraction": fraction,
        "candidate_train_rows": (
            len(train_rows)
        ),
        "candidate_eval_rows": (
            len(eval_rows)
        ),
        "candidate_train_first_creation": (
            train_rows[0][
                "_creation_dt"
            ].isoformat()
        ),
        "candidate_train_last_creation": (
            train_last.isoformat()
        ),
        "candidate_eval_first_creation": (
            eval_first.isoformat()
        ),
        "candidate_eval_last_creation": (
            eval_rows[-1][
                "_creation_dt"
            ].isoformat()
        ),
        "candidate_boundary_gap_seconds": (
            eval_first - train_last
        ).total_seconds(),
        "train": train_summary,
        "evaluation": eval_summary,
    }


def main() -> None:
    print("=" * 78)
    print(
        "T7 MOD-004 — FEATURE + TEMPORAL SPLIT AUDIT"
    )
    print("=" * 78)
    print()

    print("Input dataset:")
    print(INPUT_DATASET)
    print()

    print("IMPORTANT:")
    print(
        "  Raw Mozilla CORE archive will NOT be accessed."
    )
    print(
        "  No model will be trained."
    )
    print(
        "  Diagnostic 80/20 split will NOT be frozen."
    )
    print()

    if not INPUT_DATASET.exists():
        fail(
            "Final T7 modeling dataset does not exist:\n"
            f"{INPUT_DATASET}"
        )

    OUTPUT_AUDIT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ------------------------------------------------------------------
    # Load dataset
    # ------------------------------------------------------------------

    print(
        "[1/7] Loading finalized T7 modeling dataset..."
    )

    rows: list[dict] = []

    with INPUT_DATASET.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:

        reader = csv.DictReader(
            handle
        )

        if reader.fieldnames is None:
            fail(
                "CSV has no header."
            )

        fieldnames = list(
            reader.fieldnames
        )

        print(
            f"Columns: {len(fieldnames)}"
        )

        print("Schema:")

        for column in fieldnames:
            print(
                f"  - {column}"
            )

        required_columns = (
            set(PREDICTIVE_FEATURES)
            | TARGET_COLUMNS
        )

        missing_required = sorted(
            required_columns
            - set(fieldnames)
        )

        if missing_required:
            fail(
                "Required columns missing:\n"
                + "\n".join(
                    f"  - {column}"
                    for column in missing_required
                )
            )

        for row in reader:
            rows.append(row)

    print(
        f"Rows loaded: {len(rows):,}"
    )

    # ------------------------------------------------------------------
    # Validate exact feature boundary
    # ------------------------------------------------------------------

    print()
    print(
        "[2/7] Validating Creation-time feature boundary..."
    )

    actual_predictive_columns = [
        column
        for column in fieldnames
        if column not in TARGET_COLUMNS
    ]

    unexpected_predictive_columns = sorted(
        set(actual_predictive_columns)
        - set(PREDICTIVE_FEATURES)
    )

    missing_predictive_columns = sorted(
        set(PREDICTIVE_FEATURES)
        - set(actual_predictive_columns)
    )

    if unexpected_predictive_columns:
        fail(
            "Unexpected predictive columns detected:\n"
            + "\n".join(
                f"  - {column}"
                for column
                in unexpected_predictive_columns
            )
        )

    if missing_predictive_columns:
        fail(
            "Expected predictive columns missing:\n"
            + "\n".join(
                f"  - {column}"
                for column
                in missing_predictive_columns
            )
        )

    print(
        "Predictive feature boundary: PASS"
    )

    for feature in PREDICTIVE_FEATURES:
        print(
            f"  - {feature}"
        )

    suspicious_feature_names = []

    for feature in actual_predictive_columns:
        lowered = feature.lower()

        for term in FORBIDDEN_FEATURE_TERMS:
            if term in lowered:
                suspicious_feature_names.append(
                    {
                        "feature": feature,
                        "matched_term": term,
                    }
                )

    if suspicious_feature_names:
        fail(
            "Suspicious predictive feature names detected:\n"
            + "\n".join(
                f"  - {item['feature']} "
                f"(matched '{item['matched_term']}')"
                for item
                in suspicious_feature_names
            )
        )

    # ------------------------------------------------------------------
    # Parse / validate target structure
    # ------------------------------------------------------------------

    print()
    print(
        "[3/7] Validating target and censoring structure..."
    )

    seen_ids = set()
    invalid_events = []

    for row_number, row in enumerate(
        rows,
        start=2,
    ):
        ticket_id = row["ID"]

        if ticket_id in seen_ids:
            fail(
                "Duplicate ID detected at CSV row "
                f"{row_number}: {ticket_id}"
            )

        seen_ids.add(ticket_id)

        try:
            event = parse_int(
                row["event"],
                "event",
            )
        except ValueError as exc:
            fail(
                f"Invalid event at CSV row "
                f"{row_number}: {exc}"
            )

        if event not in (0, 1):
            invalid_events.append(
                {
                    "row": row_number,
                    "ID": ticket_id,
                    "event": event,
                }
            )

        try:
            creation_dt = parse_creation(
                row["Creation time"]
            )
        except ValueError as exc:
            fail(
                f"Invalid Creation time at CSV row "
                f"{row_number}: {exc}"
            )

        row["event"] = event
        row["_creation_dt"] = creation_dt

    if invalid_events:
        fail(
            "Invalid event values detected."
        )

    target_summary = event_summary(
        rows
    )

    print(
        f"Rows:       {target_summary['rows']:,}"
    )

    print(
        f"Event = 1:  {target_summary['event_1']:,}"
    )

    print(
        f"Event = 0:  {target_summary['event_0']:,}"
    )

    print(
        f"Event rate: {target_summary['event_rate']:.6f}"
    )

    print(
        f"Censor rate:{target_summary['censor_rate']:.6f}"
    )

    # ------------------------------------------------------------------
    # Feature statistics
    # ------------------------------------------------------------------

    print()
    print(
        "[4/7] Auditing feature missingness and cardinality..."
    )

    feature_audit = {}

    for feature in PREDICTIVE_FEATURES:
        values = [
            row[feature]
            for row in rows
        ]

        summary = summarize_feature(
            feature,
            values,
        )

        feature_audit[
            feature
        ] = summary

        print(
            f"{feature}: "
            f"missing={summary['missing']:,} "
            f"({summary['missing_rate']:.6f}), "
            f"unique={summary['unique_non_missing']:,}"
        )

    # ------------------------------------------------------------------
    # Temporal coverage
    # ------------------------------------------------------------------

    print()
    print(
        "[5/7] Auditing Creation-time coverage and ordering..."
    )

    temporal = temporal_summary(
        rows
    )

    ordering = check_temporal_order(
        rows
    )

    print(
        f"Minimum Creation: "
        f"{temporal['min_creation']}"
    )

    print(
        f"Maximum Creation: "
        f"{temporal['max_creation']}"
    )

    print(
        f"Median Creation:  "
        f"{temporal['p50_creation']}"
    )

    print(
        "Input-order backwards transitions: "
        f"{ordering['input_order_backwards_transitions']:,}"
    )

    print(
        "Exact Creation timestamp ties: "
        f"{ordering['exact_creation_timestamp_ties']:,}"
    )

    # ------------------------------------------------------------------
    # Diagnostic split
    # ------------------------------------------------------------------

    print()
    print(
        "[6/7] Evaluating diagnostic chronological 80/20 split..."
    )

    diagnostic_split = (
        diagnostic_chronological_split(
            rows,
            fraction=0.80,
        )
    )

    print(
        f"Candidate train rows: "
        f"{diagnostic_split['candidate_train_rows']:,}"
    )

    print(
        f"Candidate evaluation rows: "
        f"{diagnostic_split['candidate_eval_rows']:,}"
    )

    print(
        "Candidate boundary:"
    )

    print(
        f"  train last Creation: "
        f"{diagnostic_split['candidate_train_last_creation']}"
    )

    print(
        f"  eval first Creation: "
        f"{diagnostic_split['candidate_eval_first_creation']}"
    )

    print(
        "Candidate train event rate: "
        f"{diagnostic_split['train']['event_rate']:.6f}"
    )

    print(
        "Candidate train censor rate: "
        f"{diagnostic_split['train']['censor_rate']:.6f}"
    )

    print(
        "Candidate eval event rate: "
        f"{diagnostic_split['evaluation']['event_rate']:.6f}"
    )

    print(
        "Candidate eval censor rate: "
        f"{diagnostic_split['evaluation']['censor_rate']:.6f}"
    )

    print()
    print(
        "IMPORTANT: This 80/20 boundary is diagnostic only."
    )

    # ------------------------------------------------------------------
    # Write audit
    # ------------------------------------------------------------------

    print()
    print(
        "[7/7] Writing MOD-004 audit..."
    )

    audit = {
        "operation": "T7_MOD-004",
        "status": "COMPLETE",
        "input_dataset": str(
            INPUT_DATASET
        ),
        "raw_archive_accessed": False,
        "model_trained": False,
        "split_frozen": False,
        "rows": len(rows),
        "unique_ids": len(seen_ids),
        "schema": {
            "all_columns": fieldnames,
            "predictive_features": (
                PREDICTIVE_FEATURES
            ),
            "target_columns": sorted(
                TARGET_COLUMNS
            ),
            "unexpected_predictive_columns": (
                unexpected_predictive_columns
            ),
        },
        "target_summary": target_summary,
        "feature_audit": feature_audit,
        "temporal_summary": temporal,
        "temporal_ordering": ordering,
        "diagnostic_chronological_80_20": (
            diagnostic_split
        ),
        "leakage_name_audit": {
            "suspicious_predictive_feature_names": (
                suspicious_feature_names
            ),
            "status": (
                "PASS"
                if not suspicious_feature_names
                else "FAIL"
            ),
        },
        "next_decision": (
            "Freeze the chronological "
            "train/evaluation boundary "
            "after reviewing this audit. "
            "Do not treat the diagnostic "
            "80/20 boundary as frozen."
        ),
    }

    with OUTPUT_AUDIT.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            audit,
            handle,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("=" * 78)
    print(
        "T7 MOD-004 COMPLETE"
    )
    print("=" * 78)
    print()
    print("Audit:")
    print(OUTPUT_AUDIT)
    print()
    print("Split status:")
    print(
        "  DIAGNOSTIC ONLY — NOT FROZEN"
    )
    print()


if __name__ == "__main__":
    main()