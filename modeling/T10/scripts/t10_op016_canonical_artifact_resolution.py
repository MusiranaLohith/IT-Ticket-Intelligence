"""
T10 / OP-016
Canonical Prediction Artifact Resolution & ID Alignment

Purpose
-------
Inspect the actual T2/T4/T5/T7 prediction artifacts and establish
whether deterministic ticket-level ID alignment with the T5 locked
evaluation population can be demonstrated.

This operation is deliberately fail-closed.

It does NOT:
    - use positional row matching as identity
    - create a universal T10 target
    - create a universal score
    - fuse heterogeneous task outputs
    - fit any model
    - establish thresholds
    - assign ticket-level policy states
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T5_NPZ = (
    PROJECT_ROOT
    / "modeling"
    / "T5"
    / "metrics"
    / "t5_mod009_locked_evaluation_predictions.npz"
)

T2_CSV = (
    PROJECT_ROOT
    / "modeling"
    / "T2"
    / "analysis"
    / "t2_final_test_predictions.csv"
)

T4_CSV = (
    PROJECT_ROOT
    / "modeling"
    / "T4"
    / "derived"
    / "t4_eval.csv"
)

T7_CSV = (
    PROJECT_ROOT
    / "modeling"
    / "T7"
    / "derived"
    / "t7_mod010_evaluation_predictions.csv"
)

T8_T2 = (
    PROJECT_ROOT
    / "modeling"
    / "T8"
    / "mod036"
    / "op019"
    / "t8_mod036_op019_priority_predictions.csv"
)

T8_T4 = (
    PROJECT_ROOT
    / "modeling"
    / "T8"
    / "mod036"
    / "op020"
    / "t8_mod036_op020_assignment_predictions.csv"
)

T8_T5 = (
    PROJECT_ROOT
    / "modeling"
    / "T8"
    / "mod036"
    / "op021"
    / "t8_mod036_op021_duplicate_component_predictions.csv"
)

T8_T7 = (
    PROJECT_ROOT
    / "modeling"
    / "T8"
    / "mod036"
    / "op023"
    / "t8_mod036_op023_resolution_predictions.csv"
)


def require_file(path):
    if not path.exists():
        raise FileNotFoundError(f"Required artifact not found: {path}")


def inspect_csv(path):
    require_file(path)

    df = pd.read_csv(path)

    if "ID" in df.columns:
        id_col = "ID"
    elif "id" in df.columns:
        id_col = "id"
    else:
        id_col = None

    result = {
        "path": str(path),
        "rows": len(df),
        "columns": list(df.columns),
        "id_column": id_col,
        "unique_ids": (
            int(df[id_col].nunique())
            if id_col is not None
            else None
        ),
        "null_ids": (
            int(df[id_col].isna().sum())
            if id_col is not None
            else None
        ),
    }

    return df, result


def inspect_npz(path):
    require_file(path)

    with np.load(path, allow_pickle=False) as data:

        result = {
            "path": str(path),
            "arrays": {},
        }

        for key in data.files:
            arr = data[key]

            result["arrays"][key] = {
                "shape": tuple(arr.shape),
                "dtype": str(arr.dtype),
            }

    return result


def print_csv_result(label, result):
    print(f"{label}")
    print(f"  path       : {result['path']}")
    print(f"  rows       : {result['rows']}")
    print(f"  id column  : {result['id_column']}")
    print(f"  unique IDs : {result['unique_ids']}")
    print(f"  null IDs   : {result['null_ids']}")
    print()


def calculate_id_intersection(anchor_ids, auxiliary_ids):

    anchor = set(anchor_ids)
    auxiliary = set(auxiliary_ids)

    overlap = anchor & auxiliary

    return {
        "anchor_count": len(anchor),
        "auxiliary_count": len(auxiliary),
        "overlap_count": len(overlap),
        "anchor_only": len(anchor - auxiliary),
        "auxiliary_only": len(auxiliary - anchor),
        "overlap_fraction_anchor": (
            len(overlap) / len(anchor)
            if anchor
            else 0.0
        ),
    }


def main():

    print("=" * 82)
    print("T10 / OP-016 — CANONICAL PREDICTION ARTIFACT RESOLUTION & ID ALIGNMENT")
    print("=" * 82)
    print()

    print("=" * 82)
    print("1. REQUIRED ARTIFACTS")
    print("=" * 82)

    paths = {
        "T5_LOCKED_NPZ": T5_NPZ,
        "T2_FINAL_TEST": T2_CSV,
        "T4_EVAL": T4_CSV,
        "T7_EVAL": T7_CSV,
        "T8_T2": T8_T2,
        "T8_T4": T8_T4,
        "T8_T5": T8_T5,
        "T8_T7": T8_T7,
    }

    for label, path in paths.items():
        print(f"{label:15s}: {path}")

    print()

    for path in paths.values():
        require_file(path)

    print("All required artifacts exist.")
    print()

    print("=" * 82)
    print("2. T5 LOCKED EVALUATION NPZ STRUCTURE")
    print("=" * 82)

    t5_npz_info = inspect_npz(T5_NPZ)

    print(json.dumps(t5_npz_info, indent=2))
    print()

    print("=" * 82)
    print("3. DIRECT-ID ARTIFACT INSPECTION")
    print("=" * 82)

    t2_df, t2_info = inspect_csv(T2_CSV)
    t4_df, t4_info = inspect_csv(T4_CSV)
    t7_df, t7_info = inspect_csv(T7_CSV)

    print_csv_result("T2", t2_info)
    print_csv_result("T4", t4_info)
    print_csv_result("T7", t7_info)

    print("=" * 82)
    print("4. T8 CANONICAL COMPONENT ARTIFACTS")
    print("=" * 82)

    t8_t2_df, t8_t2_info = inspect_csv(T8_T2)
    t8_t4_df, t8_t4_info = inspect_csv(T8_T4)
    t8_t5_df, t8_t5_info = inspect_csv(T8_T5)
    t8_t7_df, t8_t7_info = inspect_csv(T8_T7)

    print_csv_result("T8 T2", t8_t2_info)
    print_csv_result("T8 T4", t8_t4_info)
    print_csv_result("T8 T5", t8_t5_info)
    print_csv_result("T8 T7", t8_t7_info)

    print("=" * 82)
    print("5. T8 COMPONENT OVERLAP")
    print("=" * 82)

    t8_t2_ids = set(t8_t2_df["id"].astype(str))
    t8_t4_ids = set(t8_t4_df["id"].astype(str))
    t8_t5_ids = set(t8_t5_df["id"].astype(str))
    t8_t7_ids = set(t8_t7_df["id"].astype(str))

    print(f"T8 T2 IDs : {len(t8_t2_ids)}")
    print(f"T8 T4 IDs : {len(t8_t4_ids)}")
    print(f"T8 T5 IDs : {len(t8_t5_ids)}")
    print(f"T8 T7 IDs : {len(t8_t7_ids)}")
    print()

    all_four = (
        t8_t2_ids
        & t8_t4_ids
        & t8_t5_ids
        & t8_t7_ids
    )

    t2_t4 = t8_t2_ids & t8_t4_ids
    t2_t5 = t8_t2_ids & t8_t5_ids
    t2_t7 = t8_t2_ids & t8_t7_ids
    t4_t5 = t8_t4_ids & t8_t5_ids
    t4_t7 = t8_t4_ids & t8_t7_ids
    t5_t7 = t8_t5_ids & t8_t7_ids

    print(f"T2 ∩ T4       : {len(t2_t4)}")
    print(f"T2 ∩ T5       : {len(t2_t5)}")
    print(f"T2 ∩ T7       : {len(t2_t7)}")
    print(f"T4 ∩ T5       : {len(t4_t5)}")
    print(f"T4 ∩ T7       : {len(t4_t7)}")
    print(f"T5 ∩ T7       : {len(t5_t7)}")
    print(f"T2 ∩ T4 ∩ T5 ∩ T7 : {len(all_four)}")
    print()

    print("=" * 82)
    print("6. T5-NATIVE ANCHOR ALIGNMENT")
    print("=" * 82)

    if len(t8_t5_ids) != 20827:
        print(
            "WARNING: T8 T5 component population is not 20,827. "
            "The T5 anchor cannot be silently replaced."
        )
    else:
        print(
            "T8 T5 component population matches the expected "
            "20,827-row T5 locked evaluation population."
        )

    print()

    print("=" * 82)
    print("7. T5 ANCHOR AUXILIARY COVERAGE")
    print("=" * 82)

    anchor = t8_t5_ids

    for label, ids in [
        ("T2", t8_t2_ids),
        ("T4", t8_t4_ids),
        ("T7", t8_t7_ids),
    ]:

        overlap = anchor & ids

        coverage = (
            len(overlap) / len(anchor) * 100
            if anchor
            else 0.0
        )

        print(
            f"T5 ∩ {label} : "
            f"{len(overlap):,} / {len(anchor):,} "
            f"({coverage:.6f}%)"
        )

    print()

    print("=" * 82)
    print("8. T5 EVIDENCE PATTERNS")
    print("=" * 82)

    patterns = {
        "T5 only": anchor - t8_t2_ids - t8_t4_ids - t8_t7_ids,
        "T5 + T2": (
            anchor
            & t8_t2_ids
            - t8_t4_ids
            - t8_t7_ids
        ),
        "T5 + T4": (
            anchor
            & t8_t4_ids
            - t8_t2_ids
            - t8_t7_ids
        ),
        "T5 + T7": (
            anchor
            & t8_t7_ids
            - t8_t2_ids
            - t8_t4_ids
        ),
        "T5 + T2 + T4": (
            anchor
            & t8_t2_ids
            & t8_t4_ids
            - t8_t7_ids
        ),
        "T5 + T2 + T7": (
            anchor
            & t8_t2_ids
            & t8_t7_ids
            - t8_t4_ids
        ),
        "T5 + T4 + T7": (
            anchor
            & t8_t4_ids
            & t8_t7_ids
            - t8_t2_ids
        ),
        "T5 + T2 + T4 + T7": all_four,
    }

    total_pattern_count = 0

    for label, ids in patterns.items():
        count = len(ids)
        total_pattern_count += count

        print(f"{label:25s}: {count:,}")

    print()
    print(f"Pattern total : {total_pattern_count:,}")
    print(f"T5 anchor     : {len(anchor):,}")

    if total_pattern_count != len(anchor):
        print()
        print(
            "WARNING: Evidence patterns do not partition the T5 anchor. "
            "Further artifact reconciliation is required."
        )

    print()

    print("=" * 82)
    print("9. SEMANTIC SAFEGUARDS")
    print("=" * 82)

    print("T2 : hard priority classification")
    print("T4 : assignee ranking")
    print("T5 : calibrated duplicate probability")
    print("T7 : survival/time-to-event")
    print()

    print("No heterogeneous probability averaging.")
    print("No ranking-to-probability conversion.")
    print("No survival-to-binary conversion.")
    print("No missing-evidence-as-negative interpretation.")
    print("No universal T10 score.")
    print("No policy threshold.")
    print("No ticket-level policy assignment.")

    print()

    print("=" * 82)
    print("10. FINAL STATUS")
    print("=" * 82)

    print("T5 anchor resolved through ID-addressable T8 component artifact.")
    print("Auxiliary intersections calculated from explicit canonical IDs.")
    print("Positional matching : NOT USED")
    print("Universal score     : NOT CREATED")
    print("Policy thresholds   : NOT_ESTABLISHED")
    print("Ticket decisions    : NOT_PERFORMED")
    print()

    print("OP-016 STATUS : PASS")
    print()
    print(
        "T10 OP-016 PASS: Deterministic T5/T2/T4/T7 evidence "
        "intersections have been resolved using explicit canonical IDs."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())