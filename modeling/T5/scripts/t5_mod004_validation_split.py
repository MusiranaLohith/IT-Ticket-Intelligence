from pathlib import Path
import csv
import hashlib
import json
import sys
import time


csv.field_size_limit(sys.maxsize)


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T5_ROOT = PROJECT_ROOT / "modeling" / "T5"

SOURCE = T5_ROOT / "derived" / "t5_train_features.csv"

SPLIT_DIR = T5_ROOT / "splits"

TRAIN_OUTPUT = SPLIT_DIR / "t5_model_train.csv"

VAL_OUTPUT = SPLIT_DIR / "t5_model_val.csv"

REPORT = SPLIT_DIR / "t5_mod004_split_report.json"


FEATURE_COLUMNS = [
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
]

TARGET_COLUMN = "T5 target"

OUTPUT_COLUMNS = [
    "ID",
    "Creation time",
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
    "T5 target",
]

EXPECTED_SOURCE_ROWS = 492_989

VALIDATION_FRACTION = 0.15

RANDOM_SEED = 42


def fail(message):
    print(f"FAIL: {message}")
    sys.exit(1)


def normalized_content_key(row):
    """
    Frozen T5 group definition:
    normalized Summary + normalized Description.
    """

    summary = (row["Summary"] or "").strip().lower()
    description = (row["Description"] or "").strip().lower()

    normalized = summary + "\n" + description

    return normalized


def deterministic_group_value(group_key):
    """
    Deterministic hash-based assignment.

    This avoids random row-level splitting and ensures that every
    normalized-content group is assigned wholly to one side.
    """

    payload = f"{RANDOM_SEED}|{group_key}".encode("utf-8")

    digest = hashlib.sha256(payload).hexdigest()

    value = int(digest[:16], 16) / float(16**16)

    return value


def main():
    start = time.time()

    print("=" * 80)
    print("T5-MOD-004 — TRAINING-ONLY GROUP-AWARE VALIDATION SPLIT")
    print("=" * 80)

    # ------------------------------------------------------------------
    # 1. Source
    # ------------------------------------------------------------------

    print("\n[1] Source artifact")

    print(f"Source: {SOURCE}")

    if not SOURCE.exists():
        fail("Controlled T5 training artifact does not exist.")

    print("PASS")

    # ------------------------------------------------------------------
    # 2. Output directory
    # ------------------------------------------------------------------

    print("\n[2] Split directory")

    SPLIT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(f"Split directory: {SPLIT_DIR}")
    print("PASS")

    # ------------------------------------------------------------------
    # 3. Read source and assign complete groups
    # ------------------------------------------------------------------

    print("\n[3] Group-aware assignment")

    groups = {}

    total_rows = 0
    positive_rows = 0
    negative_rows = 0

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as source_file:

        reader = csv.DictReader(source_file)

        if reader.fieldnames != OUTPUT_COLUMNS:
            fail(
                "Source schema does not match the controlled "
                "T5 modeling artifact."
            )

        for row in reader:
            total_rows += 1

            target = row[TARGET_COLUMN].strip()

            if target == "1":
                positive_rows += 1
            elif target == "0":
                negative_rows += 1
            else:
                fail(
                    f"Invalid target value {target!r} "
                    f"at source row {total_rows + 1}."
                )

            group_key = normalized_content_key(row)

            if group_key not in groups:
                groups[group_key] = []

            groups[group_key].append(row)

    print(f"Rows read: {total_rows}")
    print(f"Positive rows: {positive_rows}")
    print(f"Negative rows: {negative_rows}")
    print(f"Normalized-content groups: {len(groups)}")

    if total_rows != EXPECTED_SOURCE_ROWS:
        fail(
            f"Expected {EXPECTED_SOURCE_ROWS} source rows, "
            f"found {total_rows}."
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 4. Assign whole groups
    # ------------------------------------------------------------------

    print("\n[4] Deterministic whole-group split")

    train_groups = []
    val_groups = []

    for group_key in groups:
        value = deterministic_group_value(group_key)

        if value < VALIDATION_FRACTION:
            val_groups.append(group_key)
        else:
            train_groups.append(group_key)

    print(f"Training groups: {len(train_groups)}")
    print(f"Validation groups: {len(val_groups)}")

    if not train_groups:
        fail("Training group set is empty.")

    if not val_groups:
        fail("Validation group set is empty.")

    print("PASS")

    # ------------------------------------------------------------------
    # 5. Materialize split
    # ------------------------------------------------------------------

    print("\n[5] Materialize training/validation artifacts")

    train_rows = []
    val_rows = []

    for group_key in train_groups:
        train_rows.extend(groups[group_key])

    for group_key in val_groups:
        val_rows.extend(groups[group_key])

    # Deterministic ordering by original source order is preserved
    # because rows were appended in source traversal order.

    with TRAIN_OUTPUT.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as train_file:

        writer = csv.DictWriter(
            train_file,
            fieldnames=OUTPUT_COLUMNS,
        )

        writer.writeheader()
        writer.writerows(train_rows)

    with VAL_OUTPUT.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as val_file:

        writer = csv.DictWriter(
            val_file,
            fieldnames=OUTPUT_COLUMNS,
        )

        writer.writeheader()
        writer.writerows(val_rows)

    print(f"Training rows: {len(train_rows)}")
    print(f"Validation rows: {len(val_rows)}")

    if len(train_rows) + len(val_rows) != total_rows:
        fail(
            "Training + validation rows do not equal source rows."
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 6. Validate target distributions
    # ------------------------------------------------------------------

    print("\n[6] Target distribution")

    train_positive = sum(
        1
        for row in train_rows
        if row[TARGET_COLUMN].strip() == "1"
    )

    train_negative = len(train_rows) - train_positive

    val_positive = sum(
        1
        for row in val_rows
        if row[TARGET_COLUMN].strip() == "1"
    )

    val_negative = len(val_rows) - val_positive

    print(
        f"Training: {train_positive} positive / "
        f"{train_negative} negative"
    )

    print(
        f"Validation: {val_positive} positive / "
        f"{val_negative} negative"
    )

    if train_positive == 0:
        fail("Training split contains no positive examples.")

    if val_positive == 0:
        fail("Validation split contains no positive examples.")

    print("PASS")

    # ------------------------------------------------------------------
    # 7. Verify no group crosses the split
    # ------------------------------------------------------------------

    print("\n[7] Cross-split group validation")

    train_group_keys = {
        normalized_content_key(row)
        for row in train_rows
    }

    val_group_keys = {
        normalized_content_key(row)
        for row in val_rows
    }

    crossing_groups = train_group_keys & val_group_keys

    print(f"Training groups: {len(train_group_keys)}")
    print(f"Validation groups: {len(val_group_keys)}")
    print(f"Cross-split groups: {len(crossing_groups)}")

    if crossing_groups:
        fail(
            f"Found {len(crossing_groups)} normalized-content "
            f"groups crossing train/validation."
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 8. Verify ID disjointness
    # ------------------------------------------------------------------

    print("\n[8] ID disjointness")

    train_ids = {
        row["ID"]
        for row in train_rows
    }

    val_ids = {
        row["ID"]
        for row in val_rows
    }

    overlapping_ids = train_ids & val_ids

    print(f"Training unique IDs: {len(train_ids)}")
    print(f"Validation unique IDs: {len(val_ids)}")
    print(f"Overlapping IDs: {len(overlapping_ids)}")

    if overlapping_ids:
        fail(
            f"Found {len(overlapping_ids)} IDs crossing "
            "training/validation."
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 9. Write report
    # ------------------------------------------------------------------

    print("\n[9] Write split report")

    elapsed = time.time() - start

    report = {
        "operation": "T5-MOD-004",
        "operation_name": (
            "Training-Only Group-Aware Validation Split"
        ),
        "source": str(SOURCE),
        "train_output": str(TRAIN_OUTPUT),
        "validation_output": str(VAL_OUTPUT),
        "source_rows": total_rows,
        "train_rows": len(train_rows),
        "validation_rows": len(val_rows),
        "train_positive": train_positive,
        "train_negative": train_negative,
        "validation_positive": val_positive,
        "validation_negative": val_negative,
        "validation_fraction_target": VALIDATION_FRACTION,
        "random_seed": RANDOM_SEED,
        "group_definition": (
            "normalized Summary + normalized Description"
        ),
        "group_assignment": "deterministic SHA-256 hash",
        "cross_split_groups": len(crossing_groups),
        "cross_split_ids": len(overlapping_ids),
        "official_evaluation_used": False,
        "official_evaluation_modified": False,
        "raw_archive_accessed": False,
        "status": "PASS",
        "elapsed_seconds": round(elapsed, 3),
    }

    with REPORT.open(
        "w",
        encoding="utf-8",
    ) as report_file:

        json.dump(
            report,
            report_file,
            indent=2,
            ensure_ascii=False,
        )

        report_file.write("\n")

    print(f"Report: {REPORT}")
    print(f"Elapsed: {elapsed:.2f} seconds")
    print("PASS")

    # ------------------------------------------------------------------
    # Final
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("T5-MOD-004 RESULT: GROUP_AWARE_VALIDATION_SPLIT_PASS")
    print("=" * 80)

    print(f"\nTraining artifact:")
    print(TRAIN_OUTPUT)

    print(f"\nValidation artifact:")
    print(VAL_OUTPUT)

    print("\nOfficial T5 evaluation set: untouched.")
    print("No model trained.")
    print("No raw archive accessed.")
    print("Source training artifact not modified.")


if __name__ == "__main__":
    main()