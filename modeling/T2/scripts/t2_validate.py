from pathlib import Path
import json
import sys

import pandas as pd


# ============================================================
# T2-MOD-004
# Feature Materialization Validation
# ============================================================

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T2_ROOT = PROJECT_ROOT / "modeling" / "T2"

FEATURE_FILE = T2_ROOT / "derived" / "t2_features.csv"

TARGET_FILE = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T2_FIRST_PRIORITY_24H_derived.csv"
)

REPORT_FILE = T2_ROOT / "derived" / "t2_validation_report.json"


EXPECTED_ROWS = 29_498

EXPECTED_COLUMNS = [
    "ID",
    "Creation time",
    "Summary",
    "Description",
    "target_priority",
]

EXPECTED_CLASSES = {
    "P1": 7325,
    "P2": 9156,
    "P3": 11015,
    "P4": 784,
    "P5": 1218,
}

FORBIDDEN_FEATURES = {
    "Product",
    "Component",
    "Priority",
    "Severity",
    "Status",
    "Keywords",
    "Version",
    "Platform",
    "Target Milestone",
    "Classification",
    "Blocks",
    "CC",
}


def fail(message):
    print(f"VALIDATION_ERROR={message}")
    sys.exit(1)


def main():
    print("T2_MOD_004_START")

    if not FEATURE_FILE.exists():
        fail(f"FEATURE_FILE_NOT_FOUND={FEATURE_FILE}")

    if not TARGET_FILE.exists():
        fail(f"TARGET_FILE_NOT_FOUND={TARGET_FILE}")

    # --------------------------------------------------------
    # Load materialized T2 modeling artifact.
    #
    # keep_default_na=False is intentional:
    # blank Description values must remain blank strings so
    # semantic missingness can be measured consistently.
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

    print(f"FEATURE_ROWS={len(df)}")
    print(f"FEATURE_COLUMNS={len(df.columns)}")

    # --------------------------------------------------------
    # 1. Row count
    # --------------------------------------------------------
    if len(df) != EXPECTED_ROWS:
        fail(
            f"ROW_COUNT_MISMATCH expected={EXPECTED_ROWS} "
            f"actual={len(df)}"
        )

    # --------------------------------------------------------
    # 2. Exact columns
    # --------------------------------------------------------
    actual_columns = list(df.columns)

    if actual_columns != EXPECTED_COLUMNS:
        fail(
            f"COLUMN_MISMATCH expected={EXPECTED_COLUMNS} "
            f"actual={actual_columns}"
        )

    # --------------------------------------------------------
    # 3. ID integrity
    # --------------------------------------------------------
    blank_id_count = int(
        df["ID"].fillna("").str.strip().eq("").sum()
    )

    duplicate_id_count = int(
        df["ID"].duplicated().sum()
    )

    unique_id_count = int(
        df["ID"].nunique(dropna=True)
    )

    if blank_id_count != 0:
        fail(f"BLANK_IDS={blank_id_count}")

    if duplicate_id_count != 0:
        fail(f"DUPLICATE_IDS={duplicate_id_count}")

    # --------------------------------------------------------
    # 4. Creation-time validity
    # --------------------------------------------------------
    creation = pd.to_datetime(
        df["Creation time"],
        errors="coerce",
        utc=True,
    )

    invalid_creation_count = int(
        creation.isna().sum()
    )

    if invalid_creation_count != 0:
        fail(
            f"INVALID_CREATION_TIME={invalid_creation_count}"
        )

    # --------------------------------------------------------
    # 5. Summary completeness
    # --------------------------------------------------------
    summary_unavailable = int(
        df["Summary"]
        .fillna("")
        .str.strip()
        .eq("")
        .sum()
    )

    summary_non_empty = int(
        df["Summary"]
        .fillna("")
        .str.strip()
        .ne("")
        .sum()
    )

    if summary_unavailable != 0:
        fail(
            f"SUMMARY_UNAVAILABLE={summary_unavailable}"
        )

    # --------------------------------------------------------
    # 6. Description completeness
    #
    # DTM semantic definition:
    # unavailable = blank or whitespace-only.
    #
    # This intentionally does NOT rely only on pandas NaN.
    # --------------------------------------------------------
    description_unavailable = int(
        df["Description"]
        .fillna("")
        .str.strip()
        .eq("")
        .sum()
    )

    description_non_empty = int(
        df["Description"]
        .fillna("")
        .str.strip()
        .ne("")
        .sum()
    )

    expected_description_unavailable = 1592
    expected_description_non_empty = 27906

    if description_unavailable != expected_description_unavailable:
        fail(
            f"DESCRIPTION_UNAVAILABLE_MISMATCH "
            f"expected={expected_description_unavailable} "
            f"actual={description_unavailable}"
        )

    if description_non_empty != expected_description_non_empty:
        fail(
            f"DESCRIPTION_NON_EMPTY_MISMATCH "
            f"expected={expected_description_non_empty} "
            f"actual={description_non_empty}"
        )

    # --------------------------------------------------------
    # 7. Target integrity
    # --------------------------------------------------------
    target_missing = int(
        df["target_priority"]
        .fillna("")
        .str.strip()
        .eq("")
        .sum()
    )

    if target_missing != 0:
        fail(f"TARGET_MISSING={target_missing}")

    actual_class_counts = (
        df["target_priority"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    actual_class_counts = {
        str(key): int(value)
        for key, value in actual_class_counts.items()
    }

    if actual_class_counts != EXPECTED_CLASSES:
        fail(
            f"TARGET_CLASS_COUNTS_MISMATCH "
            f"expected={EXPECTED_CLASSES} "
            f"actual={actual_class_counts}"
        )

    # --------------------------------------------------------
    # 8. Target alignment against frozen accepted artifact
    #
    # Read-only cross-check.
    # The frozen target artifact is never modified.
    # --------------------------------------------------------
    target_df = pd.read_csv(
        TARGET_FILE,
        dtype={
            "ID": "string",
            "target_priority": "string",
        },
        keep_default_na=False,
    )

    if "ID" not in target_df.columns:
        fail("TARGET_ARTIFACT_MISSING_ID_COLUMN")

    if "target_priority" not in target_df.columns:
        fail("TARGET_ARTIFACT_MISSING_TARGET_PRIORITY_COLUMN")

    target_subset = target_df[
        ["ID", "target_priority"]
    ].copy()

    target_duplicate_ids = int(
        target_subset["ID"].duplicated().sum()
    )

    if target_duplicate_ids != 0:
        fail(
            f"TARGET_ARTIFACT_DUPLICATE_IDS="
            f"{target_duplicate_ids}"
        )

    feature_target = df[
        ["ID", "target_priority"]
    ].copy()

    merged = feature_target.merge(
        target_subset,
        on="ID",
        how="left",
        suffixes=("_feature", "_frozen"),
        indicator=True,
    )

    unmatched_target_ids = int(
        (merged["_merge"] != "both").sum()
    )

    if unmatched_target_ids != 0:
        fail(
            f"TARGET_ALIGNMENT_UNMATCHED_IDS="
            f"{unmatched_target_ids}"
        )

    target_mismatch_count = int(
        (
            merged["target_priority_feature"]
            != merged["target_priority_frozen"]
        ).sum()
    )

    if target_mismatch_count != 0:
        fail(
            f"TARGET_ALIGNMENT_MISMATCHES="
            f"{target_mismatch_count}"
        )

    # --------------------------------------------------------
    # 9. Forbidden feature check
    # --------------------------------------------------------
    present_forbidden = sorted(
        set(df.columns).intersection(FORBIDDEN_FEATURES)
    )

    if present_forbidden:
        fail(
            f"FORBIDDEN_FEATURES_PRESENT="
            f"{present_forbidden}"
        )

    # --------------------------------------------------------
    # 10. Final report
    # --------------------------------------------------------
    report = {
        "operation": "T2-MOD-004",
        "operation_name": "Feature Materialization Validation",
        "task": "T2",
        "task_name": "Priority Prediction",
        "dataset": "Mozilla CORE",
        "status": "PASS",
        "feature_artifact": str(FEATURE_FILE),
        "frozen_target_artifact": str(TARGET_FILE),
        "checks": {
            "row_count": {
                "expected": EXPECTED_ROWS,
                "actual": int(len(df)),
                "pass": True,
            },
            "columns": {
                "expected": EXPECTED_COLUMNS,
                "actual": actual_columns,
                "pass": True,
            },
            "ids": {
                "blank": blank_id_count,
                "duplicates": duplicate_id_count,
                "unique": unique_id_count,
                "pass": True,
            },
            "creation_time": {
                "invalid": invalid_creation_count,
                "pass": True,
            },
            "summary": {
                "non_empty": summary_non_empty,
                "unavailable": summary_unavailable,
                "pass": True,
            },
            "description": {
                "non_empty": description_non_empty,
                "unavailable": description_unavailable,
                "pass": True,
            },
            "target": {
                "missing": target_missing,
                "class_counts": actual_class_counts,
                "pass": True,
            },
            "target_alignment": {
                "unmatched_ids": unmatched_target_ids,
                "label_mismatches": target_mismatch_count,
                "pass": True,
            },
            "forbidden_features": {
                "present": present_forbidden,
                "pass": True,
            },
        },
        "integrity": {
            "raw_source_modified": False,
            "frozen_target_artifact_modified": False,
            "feature_artifact_validated_separately": True,
            "post_creation_information_added": False,
            "target_labels_modified": False,
        },
    }

    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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
    # Final console output
    # --------------------------------------------------------
    print("T2_MOD_004_COMPLETE")
    print(f"ROWS={len(df)}")
    print(f"UNIQUE_IDS={unique_id_count}")
    print(f"SUMMARY_NON_EMPTY={summary_non_empty}")
    print(f"DESCRIPTION_NON_EMPTY={description_non_empty}")
    print(f"DESCRIPTION_UNAVAILABLE={description_unavailable}")
    print(f"TARGET_MISSING={target_missing}")

    print(
        f"P1={actual_class_counts.get('P1', 0)}"
    )
    print(
        f"P2={actual_class_counts.get('P2', 0)}"
    )
    print(
        f"P3={actual_class_counts.get('P3', 0)}"
    )
    print(
        f"P4={actual_class_counts.get('P4', 0)}"
    )
    print(
        f"P5={actual_class_counts.get('P5', 0)}"
    )

    print(
        f"TARGET_UNMATCHED={unmatched_target_ids}"
    )
    print(
        f"TARGET_MISMATCHES={target_mismatch_count}"
    )
    print(
        "FORBIDDEN_FEATURES="
        + (
            ",".join(present_forbidden)
            if present_forbidden
            else "NONE"
        )
    )

    print(f"REPORT={REPORT_FILE}")
    print("STATUS=PASS")


if __name__ == "__main__":
    main()