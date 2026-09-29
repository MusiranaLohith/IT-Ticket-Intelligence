#!/usr/bin/env python3

"""
T7 MOD-005 — Freeze Chronological Train/Evaluation Split

T7 RN:
    #006

Purpose:
    Freeze the chronological train/evaluation split established
    diagnostically in MOD-004.

Frozen ordering:
    (Creation time, ID)

Frozen population:
    513,816 rows

Frozen split:
    Train      = 411,052 rows
    Evaluation = 102,764 rows

No raw Mozilla CORE archive is accessed.
No model is trained.
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path


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

SPLIT_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "T7"
    / "splits"
)

TRAIN_OUTPUT = (
    SPLIT_DIR
    / "t7_train.csv"
)

EVAL_OUTPUT = (
    SPLIT_DIR
    / "t7_evaluation.csv"
)

AUDIT_OUTPUT = (
    PROJECT_ROOT
    / "modeling"
    / "T7"
    / "metrics"
    / "t7_mod005_split_freeze.json"
)


EXPECTED_TOTAL = 513_816
EXPECTED_TRAIN = 411_052
EXPECTED_EVAL = 102_764


def fail(message: str) -> None:
    print(
        f"\nERROR: {message}",
        file=sys.stderr,
    )
    raise SystemExit(1)


def parse_creation(value: str) -> datetime:
    value = value.strip()

    if not value:
        raise ValueError(
            "empty Creation time"
        )

    return datetime.fromisoformat(
        value.replace("Z", "")
    )


def event_summary(rows: list[dict]) -> dict:
    event_1 = sum(
        1
        for row in rows
        if row["event"] == "1"
    )

    event_0 = sum(
        1
        for row in rows
        if row["event"] == "0"
    )

    total = len(rows)

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


def main() -> None:
    print("=" * 78)
    print(
        "T7 MOD-005 — FREEZE CHRONOLOGICAL TRAIN/EVALUATION SPLIT"
    )
    print("=" * 78)
    print()

    print("Input:")
    print(INPUT_DATASET)
    print()

    print("Frozen split:")
    print(
        f"  Train:      {EXPECTED_TRAIN:,}"
    )
    print(
        f"  Evaluation: {EXPECTED_EVAL:,}"
    )
    print(
        f"  Total:      {EXPECTED_TOTAL:,}"
    )
    print()

    print("Ordering key:")
    print("  (Creation time, ID)")
    print()

    print("Controls:")
    print("  Raw archive accessed: NO")
    print("  Model trained:        NO")
    print()

    if not INPUT_DATASET.exists():
        fail(
            "Input dataset does not exist:\n"
            f"{INPUT_DATASET}"
        )

    SPLIT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    AUDIT_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    print(
        "[1/6] Loading finalized T7 modeling dataset..."
    )

    rows = []

    with INPUT_DATASET.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:

        reader = csv.DictReader(handle)

        if reader.fieldnames is None:
            fail("Input CSV has no header.")

        fieldnames = list(
            reader.fieldnames
        )

        for row in reader:
            row["_creation_dt"] = parse_creation(
                row["Creation time"]
            )

            rows.append(row)

    print(
        f"Rows loaded: {len(rows):,}"
    )

    if len(rows) != EXPECTED_TOTAL:
        fail(
            f"Expected {EXPECTED_TOTAL:,} rows, "
            f"found {len(rows):,}."
        )

    # ------------------------------------------------------------------
    # Deterministic chronological ordering
    # ------------------------------------------------------------------

    print()
    print(
        "[2/6] Applying deterministic chronological ordering..."
    )

    rows.sort(
        key=lambda row: (
            row["_creation_dt"],
            row["ID"],
        )
    )

    # ------------------------------------------------------------------
    # Freeze boundary
    # ------------------------------------------------------------------

    print()
    print(
        "[3/6] Freezing 80/20 chronological boundary..."
    )

    train_rows = rows[
        :EXPECTED_TRAIN
    ]

    evaluation_rows = rows[
        EXPECTED_TRAIN:
    ]

    if len(train_rows) != EXPECTED_TRAIN:
        fail(
            "Train population mismatch."
        )

    if len(evaluation_rows) != EXPECTED_EVAL:
        fail(
            "Evaluation population mismatch."
        )

    train_last = train_rows[-1]
    eval_first = evaluation_rows[0]

    train_last_creation = (
        train_last["_creation_dt"]
    )

    eval_first_creation = (
        eval_first["_creation_dt"]
    )

    if train_last_creation > eval_first_creation:
        fail(
            "Chronological ordering violation: "
            "latest train Creation occurs after "
            "earliest evaluation Creation."
        )

    boundary_gap_seconds = (
        eval_first_creation
        - train_last_creation
    ).total_seconds()

    print(
        "Frozen boundary:"
    )

    print(
        "  Train last:"
        f" {train_last['Creation time']}"
        f"  (ID={train_last['ID']})"
    )

    print(
        "  Evaluation first:"
        f" {eval_first['Creation time']}"
        f"  (ID={eval_first['ID']})"
    )

    print(
        f"  Temporal gap: "
        f"{boundary_gap_seconds} seconds"
    )

    # ------------------------------------------------------------------
    # Validate IDs and populations
    # ------------------------------------------------------------------

    print()
    print(
        "[4/6] Validating split integrity..."
    )

    all_ids = {
        row["ID"]
        for row in rows
    }

    train_ids = {
        row["ID"]
        for row in train_rows
    }

    evaluation_ids = {
        row["ID"]
        for row in evaluation_rows
    }

    overlap = (
        train_ids
        & evaluation_ids
    )

    if overlap:
        fail(
            f"Train/evaluation ID overlap detected: "
            f"{len(overlap)} IDs."
        )

    if (
        len(train_ids)
        + len(evaluation_ids)
        != len(all_ids)
    ):
        fail(
            "Split ID population does not "
            "equal full unique population."
        )

    if (
        len(train_rows)
        + len(evaluation_rows)
        != EXPECTED_TOTAL
    ):
        fail(
            "Train + evaluation rows do not "
            "equal total population."
        )

    print(
        "ID overlap: 0"
    )

    print(
        f"Unique IDs preserved: {len(all_ids):,}"
    )

    print(
        "Population coverage: PASS"
    )

    # ------------------------------------------------------------------
    # Event/censoring accounting
    # ------------------------------------------------------------------

    print()
    print(
        "[5/6] Validating event/censoring accounting..."
    )

    full_summary = event_summary(
        rows
    )

    train_summary = event_summary(
        train_rows
    )

    evaluation_summary = event_summary(
        evaluation_rows
    )

    print(
        f"Full event=1: "
        f"{full_summary['event_1']:,}"
    )

    print(
        f"Full event=0: "
        f"{full_summary['event_0']:,}"
    )

    print(
        f"Train event=1: "
        f"{train_summary['event_1']:,}"
    )

    print(
        f"Train event=0: "
        f"{train_summary['event_0']:,}"
    )

    print(
        f"Evaluation event=1: "
        f"{evaluation_summary['event_1']:,}"
    )

    print(
        f"Evaluation event=0: "
        f"{evaluation_summary['event_0']:,}"
    )

    if (
        train_summary["event_1"]
        + evaluation_summary["event_1"]
        != full_summary["event_1"]
    ):
        fail(
            "Event=1 accounting mismatch."
        )

    if (
        train_summary["event_0"]
        + evaluation_summary["event_0"]
        != full_summary["event_0"]
    ):
        fail(
            "Event=0 accounting mismatch."
        )

    # ------------------------------------------------------------------
    # Materialize
    # ------------------------------------------------------------------

    print()
    print(
        "[6/6] Writing frozen split artifacts..."
    )

    def write_split(
        path: Path,
        split_rows: list[dict],
    ) -> None:

        with path.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as handle:

            writer = csv.DictWriter(
                handle,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            for row in split_rows:
                clean_row = {
                    column: row[column]
                    for column in fieldnames
                }

                writer.writerow(
                    clean_row
                )

    write_split(
        TRAIN_OUTPUT,
        train_rows,
    )

    write_split(
        EVAL_OUTPUT,
        evaluation_rows,
    )

    audit = {
        "operation": "T7_MOD-005",
        "rn": "T7 RN #006",
        "status": "COMPLETE",
        "input_dataset": str(
            INPUT_DATASET
        ),
        "raw_archive_accessed": False,
        "model_trained": False,
        "split_frozen": True,
        "ordering": {
            "primary": "Creation time",
            "secondary": "ID",
            "tie_policy": (
                "Creation timestamp ties are "
                "ordered deterministically by ID."
            ),
        },
        "split_rule": {
            "type": "chronological",
            "train_rows": EXPECTED_TRAIN,
            "evaluation_rows": EXPECTED_EVAL,
            "train_fraction": (
                EXPECTED_TRAIN
                / EXPECTED_TOTAL
            ),
            "evaluation_fraction": (
                EXPECTED_EVAL
                / EXPECTED_TOTAL
            ),
        },
        "boundary": {
            "train_last_creation": (
                train_last["Creation time"]
            ),
            "train_last_id": train_last["ID"],
            "evaluation_first_creation": (
                eval_first["Creation time"]
            ),
            "evaluation_first_id": (
                eval_first["ID"]
            ),
            "gap_seconds": boundary_gap_seconds,
        },
        "population": {
            "total_rows": len(rows),
            "total_unique_ids": len(all_ids),
            "train_rows": len(train_rows),
            "evaluation_rows": len(
                evaluation_rows
            ),
            "id_overlap": len(overlap),
        },
        "event_accounting": {
            "full": full_summary,
            "train": train_summary,
            "evaluation": evaluation_summary,
        },
        "artifacts": {
            "train": str(
                TRAIN_OUTPUT
            ),
            "evaluation": str(
                EVAL_OUTPUT
            ),
            "audit": str(
                AUDIT_OUTPUT
            ),
        },
    }

    with AUDIT_OUTPUT.open(
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
        "T7 MOD-005 COMPLETE"
    )
    print("=" * 78)
    print()

    print("Frozen train:")
    print(TRAIN_OUTPUT)
    print()

    print("Frozen evaluation:")
    print(EVAL_OUTPUT)
    print()

    print("Split audit:")
    print(AUDIT_OUTPUT)
    print()

    print(
        "Split status: FROZEN"
    )


if __name__ == "__main__":
    main()