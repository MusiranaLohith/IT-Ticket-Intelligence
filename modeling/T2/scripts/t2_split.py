from pathlib import Path
import json
import sys

import pandas as pd


# ============================================================
# T2-MOD-005
# Leakage-Safe Temporal Split
# ============================================================

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T2_ROOT = PROJECT_ROOT / "modeling" / "T2"

FEATURE_FILE = T2_ROOT / "derived" / "t2_features.csv"

SPLIT_ROOT = T2_ROOT / "splits"
TRAIN_FILE = SPLIT_ROOT / "train.csv"
VALIDATION_FILE = SPLIT_ROOT / "validation.csv"
TEST_FILE = SPLIT_ROOT / "test.csv"

REPORT_FILE = T2_ROOT / "splits" / "t2_split_report.json"

EXPECTED_ROWS = 29_498

TRAIN_FRACTION = 0.70
VALIDATION_FRACTION = 0.15
TEST_FRACTION = 0.15

EXPECTED_CLASSES = [
    "P1",
    "P2",
    "P3",
    "P4",
    "P5",
]


def fail(message):
    print(f"SPLIT_ERROR={message}")
    sys.exit(1)


def class_counts(df):
    counts = (
        df["target_priority"]
        .value_counts()
        .reindex(EXPECTED_CLASSES, fill_value=0)
    )

    return {
        class_name: int(counts[class_name])
        for class_name in EXPECTED_CLASSES
    }


def timestamp_summary(df):
    return {
        "rows": int(len(df)),
        "min_creation_time": (
            df["Creation time"].min().isoformat()
            if len(df) > 0
            else None
        ),
        "max_creation_time": (
            df["Creation time"].max().isoformat()
            if len(df) > 0
            else None
        ),
    }


def main():
    print("T2_MOD_005_START")

    if not FEATURE_FILE.exists():
        fail(f"FEATURE_FILE_NOT_FOUND={FEATURE_FILE}")

    # --------------------------------------------------------
    # Load validated modeling artifact.
    # --------------------------------------------------------
    df = pd.read_csv(
        FEATURE_FILE,
        dtype={
            "ID": "string",
            "Summary": "string",
            "Description": "string",
            "target_priority": "string",
        },
        keep_default_na=False,
    )

    if len(df) != EXPECTED_ROWS:
        fail(
            f"INPUT_ROW_COUNT_MISMATCH "
            f"expected={EXPECTED_ROWS} actual={len(df)}"
        )

    required_columns = [
        "ID",
        "Creation time",
        "Summary",
        "Description",
        "target_priority",
    ]

    if list(df.columns) != required_columns:
        fail(
            f"INPUT_COLUMNS_MISMATCH "
            f"expected={required_columns} "
            f"actual={list(df.columns)}"
        )

    # --------------------------------------------------------
    # Parse Creation time.
    # --------------------------------------------------------
    df["Creation time"] = pd.to_datetime(
        df["Creation time"],
        errors="coerce",
        utc=True,
    )

    invalid_creation = int(
        df["Creation time"].isna().sum()
    )

    if invalid_creation != 0:
        fail(
            f"INVALID_CREATION_TIME={invalid_creation}"
        )

    # --------------------------------------------------------
    # Check ID uniqueness before splitting.
    # --------------------------------------------------------
    duplicate_ids = int(
        df["ID"].duplicated().sum()
    )

    if duplicate_ids != 0:
        fail(
            f"INPUT_DUPLICATE_IDS={duplicate_ids}"
        )

    # --------------------------------------------------------
    # Stable chronological ordering.
    #
    # Creation time is the primary ordering key.
    # ID is a deterministic secondary key for equal timestamps.
    # --------------------------------------------------------
    df = df.sort_values(
        by=["Creation time", "ID"],
        ascending=[True, True],
        kind="mergesort",
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # Calculate deterministic boundaries.
    # --------------------------------------------------------
    train_end = int(
        EXPECTED_ROWS * TRAIN_FRACTION
    )

    validation_end = int(
        EXPECTED_ROWS
        * (TRAIN_FRACTION + VALIDATION_FRACTION)
    )

    train = df.iloc[:train_end].copy()
    validation = df.iloc[
        train_end:validation_end
    ].copy()
    test = df.iloc[
        validation_end:
    ].copy()

    # --------------------------------------------------------
    # Basic size validation.
    # --------------------------------------------------------
    expected_train = 20_648
    expected_validation = 4_425
    expected_test = 4_425

    if len(train) != expected_train:
        fail(
            f"TRAIN_SIZE_MISMATCH "
            f"expected={expected_train} actual={len(train)}"
        )

    if len(validation) != expected_validation:
        fail(
            f"VALIDATION_SIZE_MISMATCH "
            f"expected={expected_validation} "
            f"actual={len(validation)}"
        )

    if len(test) != expected_test:
        fail(
            f"TEST_SIZE_MISMATCH "
            f"expected={expected_test} actual={len(test)}"
        )

    # --------------------------------------------------------
    # Check complete partition coverage.
    # --------------------------------------------------------
    if (
        len(train)
        + len(validation)
        + len(test)
        != EXPECTED_ROWS
    ):
        fail("PARTITION_ROW_TOTAL_MISMATCH")

    train_ids = set(train["ID"])
    validation_ids = set(validation["ID"])
    test_ids = set(test["ID"])

    if train_ids.intersection(validation_ids):
        fail("TRAIN_VALIDATION_ID_OVERLAP")

    if train_ids.intersection(test_ids):
        fail("TRAIN_TEST_ID_OVERLAP")

    if validation_ids.intersection(test_ids):
        fail("VALIDATION_TEST_ID_OVERLAP")

    combined_ids = (
        train_ids
        | validation_ids
        | test_ids
    )

    if len(combined_ids) != EXPECTED_ROWS:
        fail(
            f"PARTITION_UNIQUE_ID_TOTAL_MISMATCH "
            f"expected={EXPECTED_ROWS} "
            f"actual={len(combined_ids)}"
        )

    # --------------------------------------------------------
    # Temporal ordering checks.
    # --------------------------------------------------------
    train_max = train["Creation time"].max()
    validation_min = validation["Creation time"].min()
    validation_max = validation["Creation time"].max()
    test_min = test["Creation time"].min()

    train_before_validation = train_max <= validation_min
    validation_before_test = validation_max <= test_min

    if not train_before_validation:
        fail("TRAIN_NOT_TEMPORALLY_BEFORE_VALIDATION")

    if not validation_before_test:
        fail("VALIDATION_NOT_TEMPORALLY_BEFORE_TEST")

    # --------------------------------------------------------
    # Check whether exact boundary timestamps overlap.
    #
    # Equal timestamps are allowed because Creation time may
    # contain multiple tickets at the same instant. We record
    # this explicitly rather than silently claiming a strict
    # timestamp gap.
    # --------------------------------------------------------
    boundary_timestamp_overlap_train_validation = (
        train_max == validation_min
    )

    boundary_timestamp_overlap_validation_test = (
        validation_max == test_min
    )

    # --------------------------------------------------------
    # Class distributions.
    # --------------------------------------------------------
    train_counts = class_counts(train)
    validation_counts = class_counts(validation)
    test_counts = class_counts(test)

    missing_train_classes = [
        cls
        for cls in EXPECTED_CLASSES
        if train_counts[cls] == 0
    ]

    missing_validation_classes = [
        cls
        for cls in EXPECTED_CLASSES
        if validation_counts[cls] == 0
    ]

    missing_test_classes = [
        cls
        for cls in EXPECTED_CLASSES
        if test_counts[cls] == 0
    ]

    # --------------------------------------------------------
    # Persist split artifacts.
    # --------------------------------------------------------
    SPLIT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    train.to_csv(
        TRAIN_FILE,
        index=False,
    )

    validation.to_csv(
        VALIDATION_FILE,
        index=False,
    )

    test.to_csv(
        TEST_FILE,
        index=False,
    )

    # --------------------------------------------------------
    # Final reproducibility report.
    # --------------------------------------------------------
    report = {
        "operation": "T2-MOD-005",
        "operation_name": "Leakage-Safe Temporal Split",
        "task": "T2",
        "task_name": "Priority Prediction",
        "dataset": "Mozilla CORE",
        "input_artifact": str(FEATURE_FILE),
        "split_method": "chronological",
        "shuffle": False,
        "stratification": False,
        "ordering": [
            "Creation time ascending",
            "ID ascending secondary key",
        ],
        "fractions": {
            "train": TRAIN_FRACTION,
            "validation": VALIDATION_FRACTION,
            "test": TEST_FRACTION,
        },
        "sizes": {
            "total": int(len(df)),
            "train": int(len(train)),
            "validation": int(len(validation)),
            "test": int(len(test)),
        },
        "temporal_boundaries": {
            "train_min": train["Creation time"].min().isoformat(),
            "train_max": train["Creation time"].max().isoformat(),
            "validation_min": validation["Creation time"].min().isoformat(),
            "validation_max": validation["Creation time"].max().isoformat(),
            "test_min": test["Creation time"].min().isoformat(),
            "test_max": test["Creation time"].max().isoformat(),
            "train_before_validation": bool(train_before_validation),
            "validation_before_test": bool(validation_before_test),
            "train_validation_equal_boundary_timestamp": bool(
                boundary_timestamp_overlap_train_validation
            ),
            "validation_test_equal_boundary_timestamp": bool(
                boundary_timestamp_overlap_validation_test
            ),
        },
        "class_counts": {
            "train": train_counts,
            "validation": validation_counts,
            "test": test_counts,
        },
        "missing_classes": {
            "train": missing_train_classes,
            "validation": missing_validation_classes,
            "test": missing_test_classes,
        },
        "integrity": {
            "train_validation_overlap": False,
            "train_test_overlap": False,
            "validation_test_overlap": False,
            "complete_id_coverage": True,
            "input_artifact_modified": False,
            "raw_source_modified": False,
            "frozen_target_artifact_modified": False,
        },
        "artifacts": {
            "train": str(TRAIN_FILE),
            "validation": str(VALIDATION_FILE),
            "test": str(TEST_FILE),
        },
        "status": "COMPLETE",
    }

    with REPORT_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            report,
            f,
            indent=2,
        )

    # --------------------------------------------------------
    # Console summary.
    # --------------------------------------------------------
    print("T2_MOD_005_COMPLETE")
    print(f"TOTAL={len(df)}")
    print(f"TRAIN={len(train)}")
    print(f"VALIDATION={len(validation)}")
    print(f"TEST={len(test)}")

    print(
        f"TRAIN_MIN={train['Creation time'].min().isoformat()}"
    )
    print(
        f"TRAIN_MAX={train['Creation time'].max().isoformat()}"
    )
    print(
        f"VALIDATION_MIN="
        f"{validation['Creation time'].min().isoformat()}"
    )
    print(
        f"VALIDATION_MAX="
        f"{validation['Creation time'].max().isoformat()}"
    )
    print(
        f"TEST_MIN={test['Creation time'].min().isoformat()}"
    )
    print(
        f"TEST_MAX={test['Creation time'].max().isoformat()}"
    )

    print(
        "TRAIN_CLASS_COUNTS="
        f"{train_counts}"
    )
    print(
        "VALIDATION_CLASS_COUNTS="
        f"{validation_counts}"
    )
    print(
        "TEST_CLASS_COUNTS="
        f"{test_counts}"
    )

    print(
        "MISSING_TRAIN_CLASSES="
        + (
            ",".join(missing_train_classes)
            if missing_train_classes
            else "NONE"
        )
    )
    print(
        "MISSING_VALIDATION_CLASSES="
        + (
            ",".join(missing_validation_classes)
            if missing_validation_classes
            else "NONE"
        )
    )
    print(
        "MISSING_TEST_CLASSES="
        + (
            ",".join(missing_test_classes)
            if missing_test_classes
            else "NONE"
        )
    )

    print(
        "TRAIN_VALIDATION_EQUAL_BOUNDARY_TIMESTAMP="
        f"{boundary_timestamp_overlap_train_validation}"
    )
    print(
        "VALIDATION_TEST_EQUAL_BOUNDARY_TIMESTAMP="
        f"{boundary_timestamp_overlap_validation_test}"
    )

    print(f"TRAIN_FILE={TRAIN_FILE}")
    print(f"VALIDATION_FILE={VALIDATION_FILE}")
    print(f"TEST_FILE={TEST_FILE}")
    print(f"REPORT={REPORT_FILE}")
    print("STATUS=COMPLETE")


if __name__ == "__main__":
    main()