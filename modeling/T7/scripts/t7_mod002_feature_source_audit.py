from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


# =============================================================================
# T7 MOD-002 — CREATION-TIME FEATURE SOURCE AUDIT
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

T7_ARTIFACT = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T7_TIME_TO_FIRST_RESOLVED_derived.csv"
)

OUTPUT_JSON = (
    PROJECT_ROOT
    / "modeling"
    / "T7"
    / "metrics"
    / "t7_mod002_feature_source_audit.json"
)


# =============================================================================
# ACCEPTED PHYSICAL T7 ARTIFACT SCHEMA
# =============================================================================

EXPECTED_COLUMNS = [
    "ID",
    "Creation time",
    "first_resolved_time",
    "duration_seconds",
    "event",
    "endpoint_type",
    "observation_endpoint",
    "source_row_width",
]


# =============================================================================
# TARGET / EVIDENCE FIELDS
# =============================================================================

TARGET_EVIDENCE_FIELDS = {
    "first_resolved_time",
    "duration_seconds",
    "event",
    "endpoint_type",
    "observation_endpoint",
}


IDENTITY_TIME_FIELDS = {
    "ID",
    "Creation time",
}


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:

    print("=" * 80)
    print("T7 MOD-002 — CREATION-TIME FEATURE SOURCE AUDIT")
    print("=" * 80)
    print()

    # -------------------------------------------------------------------------
    # 1. Verify accepted artifact
    # -------------------------------------------------------------------------

    print("[1/7] Loading accepted T7 derived artifact...")

    if not T7_ARTIFACT.exists():
        raise FileNotFoundError(
            f"Accepted T7 artifact not found:\n{T7_ARTIFACT}"
        )

    df = pd.read_csv(T7_ARTIFACT)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")
    print()

    # -------------------------------------------------------------------------
    # 2. Exact schema verification
    # -------------------------------------------------------------------------

    print("[2/7] Verifying accepted artifact schema...")

    actual_columns = list(df.columns)

    print("Actual columns:")
    for index, column in enumerate(actual_columns, start=1):
        print(f"  {index:02d}. {column}")

    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in actual_columns
    ]

    unexpected_columns = [
        column
        for column in actual_columns
        if column not in EXPECTED_COLUMNS
    ]

    if missing_columns:
        raise ValueError(
            "Accepted T7 artifact is missing expected columns: "
            f"{missing_columns}"
        )

    if unexpected_columns:
        print()
        print("Unexpected columns:")
        for column in unexpected_columns:
            print(f"  - {column}")

    print()
    print("Expected T7 artifact schema: VALID")

    # -------------------------------------------------------------------------
    # 3. Ticket-level integrity
    # -------------------------------------------------------------------------

    print()
    print("[3/7] Validating ticket-level structure...")

    if df["ID"].isna().any():
        raise ValueError("T7 artifact contains missing ID values.")

    duplicate_rows = int(df["ID"].duplicated().sum())

    if duplicate_rows != 0:
        raise ValueError(
            f"T7 artifact contains {duplicate_rows} duplicate ID rows."
        )

    unique_ids = int(df["ID"].nunique())

    print(f"Unique IDs: {unique_ids:,}")
    print(f"Duplicate ID rows: {duplicate_rows}")

    # -------------------------------------------------------------------------
    # 4. Target semantics
    # -------------------------------------------------------------------------

    print()
    print("[4/7] Validating physical target/evidence fields...")

    event_counts = (
        df["event"]
        .value_counts(dropna=False)
        .sort_index()
        .to_dict()
    )

    print("Event value counts:")
    for value, count in event_counts.items():
        print(f"  {value!r}: {int(count):,}")

    duration_missing = int(df["duration_seconds"].isna().sum())
    first_resolved_missing = int(df["first_resolved_time"].isna().sum())

    print()
    print(f"Missing duration_seconds: {duration_missing:,}")
    print(
        f"Missing first_resolved_time: "
        f"{first_resolved_missing:,}"
    )

    print()
    print("Semantic target mapping:")
    print("  time_to_first_resolved -> duration_seconds")
    print("  event                  -> event")
    print("  first observed endpoint -> first_resolved_time")

    # -------------------------------------------------------------------------
    # 5. Determine feature availability in accepted artifact
    # -------------------------------------------------------------------------

    print()
    print("[5/7] Identifying Creation-time predictive fields...")

    candidate_creation_fields = [
        column
        for column in actual_columns
        if column not in TARGET_EVIDENCE_FIELDS
        and column not in IDENTITY_TIME_FIELDS
    ]

    print()
    print("Creation-time predictive fields physically present")
    print("in accepted T7 artifact:")

    if candidate_creation_fields:
        for column in candidate_creation_fields:
            print(f"  - {column}")
    else:
        print("  NONE")

    # -------------------------------------------------------------------------
    # 6. Boundary determination
    # -------------------------------------------------------------------------

    print()
    print("[6/7] Applying T7 Creation-time feature boundary...")

    print()
    print("Allowed predictive information:")
    print("  - Information legitimately available at Creation")
    print()

    print("Forbidden predictive information:")
    print("  - Post-Creation History")
    print("  - Current/final Status")
    print("  - Current/final Resolution")
    print("  - Post-Creation assignment")
    print("  - Post-Creation relationships")
    print("  - Post-Creation state changes")
    print("  - Target-derived information")
    print("  - Future information")

    feature_source_status = (
        "FEATURES_PRESENT_IN_ACCEPTED_ARTIFACT"
        if candidate_creation_fields
        else "CREATION_FEATURES_NOT_PRESENT_IN_ACCEPTED_ARTIFACT"
    )

    # -------------------------------------------------------------------------
    # 7. Save audit
    # -------------------------------------------------------------------------

    print()
    print("[7/7] Writing MOD-002 audit artifact...")

    audit = {
        "task_id": "T7",
        "operation_id": "MOD-002",
        "operation_name": (
            "Creation-Time Feature Source Audit"
        ),
        "status": "COMPLETED",

        "source": {
            "artifact": str(T7_ARTIFACT),
            "raw_dataset_read": False,
            "artifact_modified": False,
        },

        "population": {
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "unique_ids": unique_ids,
            "duplicate_id_rows": duplicate_rows,
        },

        "schema": {
            "expected_columns": EXPECTED_COLUMNS,
            "actual_columns": actual_columns,
            "schema_valid": len(missing_columns) == 0,
            "unexpected_columns": unexpected_columns,
        },

        "target_mapping": {
            "semantic_duration_field": "time_to_first_resolved",
            "physical_duration_field": "duration_seconds",
            "event_field": "event",
            "endpoint_timestamp_field": "first_resolved_time",
        },

        "target_evidence_fields": sorted(
            TARGET_EVIDENCE_FIELDS
        ),

        "identity_time_fields": sorted(
            IDENTITY_TIME_FIELDS
        ),

        "candidate_creation_fields_physically_present": (
            candidate_creation_fields
        ),

        "feature_boundary": {
            "prediction_boundary": "Creation time",
            "creation_time_only": True,
            "post_creation_information_allowed": False,
            "current_final_fields_allowed": False,
            "target_derived_fields_allowed": False,
            "status": feature_source_status,
        },

        "decision": {
            "raw_source_scanned": False,
            "target_modified": False,
            "model_trained": False,
            "next_action": (
                "Controlled extraction of Creation-time predictive "
                "fields from immutable Mozilla CORE source is required."
                if not candidate_creation_fields
                else
                "Review and freeze the Creation-time feature whitelist."
            ),
        },
    }

    OUTPUT_JSON.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_JSON.write_text(
        json.dumps(
            audit,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 80)
    print("T7 MOD-002: COMPLETED")
    print("=" * 80)
    print()
    print(f"Audit: {OUTPUT_JSON}")
    print()
    print("Raw Mozilla CORE dataset read: NO")
    print("Accepted T7 artifact modified: NO")
    print("Model trained: NO")


if __name__ == "__main__":
    main()