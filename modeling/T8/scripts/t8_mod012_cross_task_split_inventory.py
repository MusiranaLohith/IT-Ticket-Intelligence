#!/usr/bin/env python3

import csv
from pathlib import Path


csv.field_size_limit(2**31 - 1)

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

MODELING_ROOT = PROJECT_ROOT / "modeling"


TASKS = {
    "T2": MODELING_ROOT / "T2",
    "T4": MODELING_ROOT / "T4",
    "T5": MODELING_ROOT / "T5",
    "T7": MODELING_ROOT / "T7",
}


PREDICTION_ARTIFACTS = {
    "T2": [
        MODELING_ROOT /
        "T2/analysis/t2_final_test_predictions.csv",
    ],

    "T4": [
        MODELING_ROOT /
        "T4/results/r1_checkpoints/t4_r1_topk_predictions.npz",
    ],

    "T5": [
        MODELING_ROOT /
        "T5/metrics/t5_mod009_locked_evaluation_predictions.npz",
    ],

    "T7": [
        MODELING_ROOT /
        "T7/derived/t7_mod010_evaluation_predictions.csv",
    ],
}


def print_header(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def discover_files(root):
    if not root.exists():
        return []

    return sorted(
        path for path in root.rglob("*")
        if path.is_file()
    )


def csv_header(path):
    try:
        with path.open(
            "r",
            encoding="utf-8",
            errors="replace",
            newline=""
        ) as f:

            reader = csv.reader(f)
            return next(reader)

    except Exception:
        return []


print_header(
    "MOD-012 — CROSS-TASK SPLIT / PROVENANCE INVENTORY"
)

print(
    "Purpose: discover existing task split artifacts before "
    "performing any cross-task ID-overlap calculation."
)

print(
    "Read-only: no models, no training, no raw archive access, "
    "no artifact modification."
)


# ------------------------------------------------------------
# 1. Task directory inventory
# ------------------------------------------------------------

print_header(
    "TASK DIRECTORY INVENTORY"
)

for task, root in TASKS.items():

    files = discover_files(root)

    print()
    print(f"{task}")
    print(f"Root: {root}")
    print(f"Exists: {root.exists()}")
    print(f"Files: {len(files)}")

    for path in files:

        name = path.name.lower()

        if any(
            token in name
            for token in (
                "train",
                "test",
                "eval",
                "split",
                "prediction",
                "closure",
            )
        ):

            print(
                f"  {path.relative_to(MODELING_ROOT)}"
            )


# ------------------------------------------------------------
# 2. Candidate split artifacts
# ------------------------------------------------------------

print_header(
    "CANDIDATE SPLIT / EVALUATION ARTIFACTS"
)

for task, root in TASKS.items():

    print()
    print(f"--- {task} ---")

    files = discover_files(root)

    candidates = []

    for path in files:

        name = path.name.lower()

        if any(
            token in name
            for token in (
                "train",
                "test",
                "eval",
                "split",
            )
        ):

            candidates.append(path)

    for path in candidates:

        print(
            path.relative_to(MODELING_ROOT)
        )


# ------------------------------------------------------------
# 3. CSV schemas
# ------------------------------------------------------------

print_header(
    "CSV SPLIT / EVALUATION SCHEMA INVENTORY"
)

for task, root in TASKS.items():

    print()
    print(f"--- {task} ---")

    files = discover_files(root)

    for path in files:

        if path.suffix.lower() != ".csv":
            continue

        name = path.name.lower()

        if not any(
            token in name
            for token in (
                "train",
                "test",
                "eval",
                "split",
            )
        ):
            continue

        header = csv_header(path)

        print()
        print(
            path.relative_to(MODELING_ROOT)
        )
        print(
            f"  columns: {len(header)}"
        )
        print(
            f"  header: {header}"
        )


# ------------------------------------------------------------
# 4. Prediction artifact confirmation
# ------------------------------------------------------------

print_header(
    "PREDICTION ARTIFACT CONFIRMATION"
)

for task, paths in PREDICTION_ARTIFACTS.items():

    print()
    print(f"--- {task} ---")

    for path in paths:

        print(
            f"Exists: {path.exists()}"
        )
        print(
            f"Path: {path}"
        )


# ------------------------------------------------------------
# 5. Explicit next-step gate
# ------------------------------------------------------------

print_header(
    "MOD-012 NEXT-STEP GATE"
)

print(
    "This operation only inventories candidate split artifacts."
)

print(
    "No cross-task overlap has been calculated yet."
)

print(
    "No evaluation population has been selected."
)

print(
    "No fusion model has been created."
)

print(
    "MOD-012 SPLIT INVENTORY COMPLETE"
)