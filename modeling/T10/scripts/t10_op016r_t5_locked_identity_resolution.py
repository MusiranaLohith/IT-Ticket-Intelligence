"""
T10 / OP-016R
T5 Locked-Evaluation Identity Resolution

Purpose
-------
Resolve the canonical ticket IDs corresponding specifically to the
20,827-row T5 locked evaluation prediction artifact.

This operation exists because the previous OP-016 incorrectly used
the 74,091-row T8 T5 component population as the T5 anchor.

This operation MUST keep these populations distinct:

    T5 locked evaluation      = 20,827
    T5 calibration population = 74,091

No auxiliary intersection is calculated here.

This operation does NOT:
    - create a fusion model
    - calculate policy performance
    - create a universal score
    - establish thresholds
    - assign ticket-level states
    - use positional correspondence as ticket identity unless the
      underlying T5 split/evaluation contract explicitly establishes
      that ordering
"""

from pathlib import Path
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

T5_MODEL_TRAIN = (
    PROJECT_ROOT
    / "modeling"
    / "T5"
    / "splits"
    / "t5_model_train.csv"
)

T5_MODEL_VAL = (
    PROJECT_ROOT
    / "modeling"
    / "T5"
    / "splits"
    / "t5_model_val.csv"
)

T5_CALIBRATION_CAL = (
    PROJECT_ROOT
    / "modeling"
    / "T5"
    / "splits"
    / "t5_calibration_cal.csv"
)

T5_CALIBRATION_FIT = (
    PROJECT_ROOT
    / "modeling"
    / "T5"
    / "splits"
    / "t5_calibration_fit.csv"
)

T5_LOCKED_METRICS = (
    PROJECT_ROOT
    / "modeling"
    / "T5"
    / "metrics"
    / "t5_mod009_locked_evaluation_metrics.json"
)

T5_GENERALIZATION = (
    PROJECT_ROOT
    / "modeling"
    / "T5"
    / "metrics"
    / "t5_mod010_generalization_analysis.json"
)

T5_CLOSURE = (
    PROJECT_ROOT
    / "modeling"
    / "T5"
    / "metrics"
    / "t5_mod011_final_closure.json"
)


EXPECTED_LOCKED_ROWS = 20827
EXPECTED_CALIBRATION_ROWS = 74091


def require(path):
    if not path.exists():
        raise FileNotFoundError(f"Required artifact missing: {path}")


def inspect_csv(path):
    require(path)

    df = pd.read_csv(path)

    if "ID" not in df.columns:
        raise ValueError(
            f"Expected ID column not found in {path}. "
            f"Columns: {list(df.columns)}"
        )

    return df


def main():

    print("=" * 82)
    print("T10 / OP-016R — T5 LOCKED-EVALUATION IDENTITY RESOLUTION")
    print("=" * 82)
    print()

    print("=" * 82)
    print("1. T5 LOCKED NPZ")
    print("=" * 82)

    require(T5_NPZ)

    with np.load(T5_NPZ, allow_pickle=False) as data:
        arrays = list(data.files)

        print(f"Arrays : {arrays}")

        for name in arrays:
            print(
                f"{name:12s}: "
                f"shape={data[name].shape}, "
                f"dtype={data[name].dtype}"
            )

        y_true = data["y_true"]
        p_duplicate = data["p_duplicate"]

    print()
    print(f"Locked y_true rows       : {len(y_true):,}")
    print(f"Locked probability rows  : {len(p_duplicate):,}")
    print()

    if len(y_true) != EXPECTED_LOCKED_ROWS:
        raise ValueError(
            "T5 locked NPZ does not contain the expected 20,827 rows."
        )

    if len(p_duplicate) != EXPECTED_LOCKED_ROWS:
        raise ValueError(
            "T5 locked probability vector does not contain 20,827 rows."
        )

    print("T5 LOCKED POPULATION : 20,827 CONFIRMED")
    print()

    print("=" * 82)
    print("2. T5 SOURCE SPLIT POPULATIONS")
    print("=" * 82)

    train = inspect_csv(T5_MODEL_TRAIN)
    val = inspect_csv(T5_MODEL_VAL)
    cal = inspect_csv(T5_CALIBRATION_CAL)
    fit = inspect_csv(T5_CALIBRATION_FIT)

    print(f"t5_model_train.csv       : {len(train):,}")
    print(f"t5_model_val.csv         : {len(val):,}")
    print(f"t5_calibration_cal.csv   : {len(cal):,}")
    print(f"t5_calibration_fit.csv   : {len(fit):,}")
    print()

    print("=" * 82)
    print("3. POPULATION IDENTITY CHECK")
    print("=" * 82)

    print(
        "The 74,091-row calibration population is explicitly kept "
        "separate from the 20,827-row locked evaluation population."
    )

    print()

    if len(cal) == EXPECTED_CALIBRATION_ROWS:
        print(
            "T5 calibration population : 74,091 CONFIRMED"
        )
    else:
        print(
            f"T5 calibration population : {len(cal):,} "
            f"(expected 74,091)"
        )

    print()

    print("=" * 82)
    print("4. DUPLICATE / ID INTEGRITY")
    print("=" * 82)

    for name, df in [
        ("model_train", train),
        ("model_val", val),
        ("calibration_cal", cal),
        ("calibration_fit", fit),
    ]:

        null_count = int(df["ID"].isna().sum())
        unique_count = int(df["ID"].nunique())

        print(
            f"{name:18s} "
            f"rows={len(df):8,} "
            f"unique_IDs={unique_count:8,} "
            f"null_IDs={null_count:4,}"
        )

    print()

    print("=" * 82)
    print("5. LOCKED-EVALUATION IDENTITY STATUS")
    print("=" * 82)

    print(
        "The locked prediction NPZ contains only y_true and probability "
        "arrays; it contains no explicit ID array."
    )

    print()

    print(
        "Therefore, this operation does NOT silently infer ticket IDs "
        "from an arbitrary dataframe."
    )

    print()

    print(
        "A valid 20,827-ticket identity mapping requires an explicit "
        "T5 evaluation-source artifact or documented evaluation-order "
        "contract connecting those 20,827 predictions to canonical IDs."
    )

    print()

    print("=" * 82)
    print("6. CURRENT RESOLUTION")
    print("=" * 82)

    print("T5 locked population        : RESOLVED = 20,827")
    print("T5 locked ticket IDs        : NOT YET EXPLICITLY RESOLVED")
    print("T5 calibration population  : DISTINCT = 74,091")
    print("74,091 artifact as anchor   : REJECTED")
    print("Positional ID assumption    : NOT ACCEPTED")
    print()

    print("=" * 82)
    print("7. POLICY BOUNDARY")
    print("=" * 82)

    print("T5 native outcome           : RETAINED")
    print("Universal T10 target       : ABSENT")
    print("Universal T10 score        : ABSENT")
    print("Auxiliary fusion           : NOT PERFORMED")
    print("Policy thresholds          : NOT_ESTABLISHED")
    print("Ticket decisions           : NOT_PERFORMED")
    print()

    print("=" * 82)
    print("8. FINAL RESULT")
    print("=" * 82)

    print(
        "OP-016R STATUS : RESOLUTION INCOMPLETE"
    )

    print()

    print(
        "The 20,827-row T5 locked population is confirmed, but its "
        "canonical ticket IDs have not yet been explicitly resolved."
    )

    print(
        "No RN is assigned from this operation."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())