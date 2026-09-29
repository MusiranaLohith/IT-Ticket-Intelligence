from pathlib import Path
import csv
import json
import sys
csv.field_size_limit(sys.maxsize)

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

DATASET_ROOT = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE"
)

CANONICAL = DATASET_ROOT / (
    "DTM-002_T5_DUPLICATE_DETECTION_derived_canonical.csv"
)

TRAIN = DATASET_ROOT / "DTM-002_T5_TRAIN_GROUP_AWARE.csv"

EVAL = DATASET_ROOT / "DTM-002_T5_EVAL_GROUP_AWARE.csv"

AUDIT = DATASET_ROOT / "DTM-002_T5_FINAL_SPLIT_AUDIT.json"


FEATURE_COLUMNS = [
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
]

TARGET_COLUMN = "T5 target"

PROVENANCE_COLUMNS = [
    "Target event index",
    "Target change index",
    "Target time",
    "Target actor",
]

IDENTITY_COLUMNS = [
    "ID",
    "Creation time",
]


EXPECTED_COLUMNS = (
    IDENTITY_COLUMNS
    + FEATURE_COLUMNS
    + [TARGET_COLUMN]
    + PROVENANCE_COLUMNS
)


EXPECTED_CANONICAL_ROWS = 513_816
EXPECTED_CANONICAL_POSITIVE = 4_691
EXPECTED_CANONICAL_NEGATIVE = 509_125

EXPECTED_TRAIN_ROWS = 492_989
EXPECTED_TRAIN_POSITIVE = 3_373
EXPECTED_TRAIN_NEGATIVE = 489_616

EXPECTED_EVAL_ROWS = 20_827
EXPECTED_EVAL_POSITIVE = 1_318
EXPECTED_EVAL_NEGATIVE = 19_509


def fail(message):
    print(f"FAIL: {message}")
    sys.exit(1)


def read_header(path):
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        reader = csv.reader(f)
        return next(reader)


def validate_schema(path):
    header = read_header(path)

    if header != EXPECTED_COLUMNS:
        print(f"Actual columns: {header}")
        print(f"Expected columns: {EXPECTED_COLUMNS}")

        missing = [
            column
            for column in EXPECTED_COLUMNS
            if column not in header
        ]

        unexpected = [
            column
            for column in header
            if column not in EXPECTED_COLUMNS
        ]

        if missing:
            print(f"Missing columns: {missing}")

        if unexpected:
            print(f"Unexpected columns: {unexpected}")

        fail(f"{path.name}: schema mismatch.")

    return header


def count_rows_and_target(path):
    rows = 0
    positives = 0
    negatives = 0

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        reader = csv.DictReader(f)

        if reader.fieldnames != EXPECTED_COLUMNS:
            fail(
                f"{path.name}: schema changed during reading."
            )

        for row_number, row in enumerate(reader, start=2):
            rows += 1

            value = row[TARGET_COLUMN].strip()

            if value == "1":
                positives += 1
            elif value == "0":
                negatives += 1
            else:
                fail(
                    f"{path.name}: invalid target value "
                    f"{value!r} at row {row_number}."
                )

    return rows, positives, negatives


def inspect_id_uniqueness(path):
    seen = set()

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        reader = csv.DictReader(f)

        if "ID" not in reader.fieldnames:
            fail(f"{path.name}: missing ID column.")

        for row_number, row in enumerate(reader, start=2):
            ticket_id = row["ID"]

            if ticket_id in seen:
                fail(
                    f"{path.name}: duplicate ID "
                    f"{ticket_id!r} at row {row_number}."
                )

            seen.add(ticket_id)

    return len(seen)


def inspect_split_id_uniqueness(path):
    seen = set()

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        reader = csv.DictReader(f)

        for row_number, row in enumerate(reader, start=2):
            ticket_id = row["ID"]

            if ticket_id in seen:
                fail(
                    f"{path.name}: duplicate ID "
                    f"{ticket_id!r} at row {row_number}."
                )

            seen.add(ticket_id)

    return len(seen)


def main():
    print("=" * 80)
    print("T5-MOD-001 — MODELING CONTRACT RECONCILIATION")
    print("=" * 80)

    # ------------------------------------------------------------------
    # 1. Project
    # ------------------------------------------------------------------

    print("\n[1] Project")
    print(f"Project root: {PROJECT_ROOT}")

    if not PROJECT_ROOT.exists():
        fail("Project root does not exist.")

    print("PASS")

    # ------------------------------------------------------------------
    # 2. Accepted artifacts
    # ------------------------------------------------------------------

    print("\n[2] Accepted artifact existence")

    artifacts = {
        "Canonical": CANONICAL,
        "Training": TRAIN,
        "Evaluation": EVAL,
        "Final audit": AUDIT,
    }

    for name, path in artifacts.items():
        print(f"{name}: {path}")

        if not path.exists():
            fail(f"{name} artifact does not exist.")

        print("  PASS")

    # ------------------------------------------------------------------
    # 3. Frozen contract
    # ------------------------------------------------------------------

    print("\n[3] Frozen T5 modeling boundary")

    print("Identity columns:")
    for column in IDENTITY_COLUMNS:
        print(f"  - {column}")

    print("\nCreation-time predictive features:")
    for column in FEATURE_COLUMNS:
        print(f"  - {column}")

    print(f"\nTarget:")
    print(f"  - {TARGET_COLUMN}")

    print("\nTarget/provenance columns:")
    for column in PROVENANCE_COLUMNS:
        print(f"  - {column}")

    print("\nPASS")

    # ------------------------------------------------------------------
    # 4. Canonical schema
    # ------------------------------------------------------------------

    print("\n[4] Canonical schema validation")

    canonical_header = validate_schema(CANONICAL)

    print(f"Canonical columns: {len(canonical_header)}")
    print("PASS")

    # ------------------------------------------------------------------
    # 5. Training schema
    # ------------------------------------------------------------------

    print("\n[5] Training schema validation")

    train_header = validate_schema(TRAIN)

    print(f"Training columns: {len(train_header)}")
    print("PASS")

    # ------------------------------------------------------------------
    # 6. Evaluation schema
    # ------------------------------------------------------------------

    print("\n[6] Evaluation schema validation")

    eval_header = validate_schema(EVAL)

    print(f"Evaluation columns: {len(eval_header)}")
    print("PASS")

    # ------------------------------------------------------------------
    # 7. Canonical target population
    # ------------------------------------------------------------------

    print("\n[7] Canonical target population")

    rows, positives, negatives = count_rows_and_target(
        CANONICAL
    )

    print(f"Rows: {rows}")
    print(f"Positive: {positives}")
    print(f"Negative: {negatives}")

    if rows != EXPECTED_CANONICAL_ROWS:
        fail(
            f"Expected {EXPECTED_CANONICAL_ROWS} canonical rows, "
            f"found {rows}."
        )

    if positives != EXPECTED_CANONICAL_POSITIVE:
        fail(
            f"Expected {EXPECTED_CANONICAL_POSITIVE} positives, "
            f"found {positives}."
        )

    if negatives != EXPECTED_CANONICAL_NEGATIVE:
        fail(
            f"Expected {EXPECTED_CANONICAL_NEGATIVE} negatives, "
            f"found {negatives}."
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 8. Training population
    # ------------------------------------------------------------------

    print("\n[8] Training population")

    rows, positives, negatives = count_rows_and_target(TRAIN)

    print(f"Rows: {rows}")
    print(f"Positive: {positives}")
    print(f"Negative: {negatives}")

    if rows != EXPECTED_TRAIN_ROWS:
        fail(
            f"Expected {EXPECTED_TRAIN_ROWS} training rows, "
            f"found {rows}."
        )

    if positives != EXPECTED_TRAIN_POSITIVE:
        fail(
            f"Expected {EXPECTED_TRAIN_POSITIVE} training positives, "
            f"found {positives}."
        )

    if negatives != EXPECTED_TRAIN_NEGATIVE:
        fail(
            f"Expected {EXPECTED_TRAIN_NEGATIVE} training negatives, "
            f"found {negatives}."
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 9. Evaluation population
    # ------------------------------------------------------------------

    print("\n[9] Evaluation population")

    rows, positives, negatives = count_rows_and_target(EVAL)

    print(f"Rows: {rows}")
    print(f"Positive: {positives}")
    print(f"Negative: {negatives}")

    if rows != EXPECTED_EVAL_ROWS:
        fail(
            f"Expected {EXPECTED_EVAL_ROWS} evaluation rows, "
            f"found {rows}."
        )

    if positives != EXPECTED_EVAL_POSITIVE:
        fail(
            f"Expected {EXPECTED_EVAL_POSITIVE} evaluation positives, "
            f"found {positives}."
        )

    if negatives != EXPECTED_EVAL_NEGATIVE:
        fail(
            f"Expected {EXPECTED_EVAL_NEGATIVE} evaluation negatives, "
            f"found {negatives}."
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 10. Canonical ID uniqueness
    # ------------------------------------------------------------------

    print("\n[10] Canonical ID uniqueness")

    unique_ids = inspect_id_uniqueness(CANONICAL)

    print(f"Unique IDs: {unique_ids}")

    if unique_ids != EXPECTED_CANONICAL_ROWS:
        fail(
            f"Expected {EXPECTED_CANONICAL_ROWS} unique IDs, "
            f"found {unique_ids}."
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 11. Split ID uniqueness
    # ------------------------------------------------------------------

    print("\n[11] Training ID uniqueness")

    train_unique_ids = inspect_split_id_uniqueness(TRAIN)

    print(f"Unique training IDs: {train_unique_ids}")

    if train_unique_ids != EXPECTED_TRAIN_ROWS:
        fail(
            f"Expected {EXPECTED_TRAIN_ROWS} unique training IDs, "
            f"found {train_unique_ids}."
        )

    print("PASS")

    print("\n[12] Evaluation ID uniqueness")

    eval_unique_ids = inspect_split_id_uniqueness(EVAL)

    print(f"Unique evaluation IDs: {eval_unique_ids}")

    if eval_unique_ids != EXPECTED_EVAL_ROWS:
        fail(
            f"Expected {EXPECTED_EVAL_ROWS} unique evaluation IDs, "
            f"found {eval_unique_ids}."
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 13. Final split audit
    # ------------------------------------------------------------------

    print("\n[13] Final split audit")

    with AUDIT.open("r", encoding="utf-8") as f:
        audit = json.load(f)

    print("Final audit JSON loaded successfully.")
    print(f"Top-level keys: {list(audit.keys())}")
    print("PASS")

    # ------------------------------------------------------------------
    # Final result
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("T5-MOD-001 RESULT: READY_FOR_CONTROLLED_MODELING")
    print("=" * 80)

    print("\nFrozen Creation-time features:")
    for feature in FEATURE_COLUMNS:
        print(f"  - {feature}")

    print(f"\nFrozen target: {TARGET_COLUMN}")

    print("\nTarget metadata retained:")
    for column in PROVENANCE_COLUMNS:
        print(f"  - {column}")

    print("\nNo model trained.")
    print("No artifact modified.")
    print("No raw archive scanned.")
    print("No dataset copied or extracted.")


if __name__ == "__main__":
    main()