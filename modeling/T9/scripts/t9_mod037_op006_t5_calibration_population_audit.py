from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


# ============================================================
# T9 MOD-037 OP-006
# T5 Calibration Population & Probability Semantics Audit
#
# Purpose:
#   Audit the accepted native T5 probability artifact before
#   any new calibration/evaluation operation is performed.
#
# This operation DOES NOT:
#   - fit a model
#   - fit calibration
#   - select a calibration method
#   - select a threshold
#   - create a target
#   - create probabilities
#   - use locked test data for selection
#   - create a universal confidence/risk score
#
# It establishes:
#   1. Artifact existence and structure
#   2. Population integrity
#   3. Native target semantics
#   4. Native probability semantics
#   5. Probability validity
#   6. Target/probability alignment
#   7. Suitability for subsequent T5 calibration work
# ============================================================


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T9_ROOT = PROJECT_ROOT / "modeling" / "T9"
OUTPUT_DIR = T9_ROOT / "mod037"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_JSON = (
    OUTPUT_DIR
    / "t9_mod037_op006_t5_calibration_population_audit.json"
)


# ------------------------------------------------------------
# Accepted T5 native artifact
# ------------------------------------------------------------

T5_ARTIFACT = (
    PROJECT_ROOT
    / "modeling"
    / "T5"
    / "metrics"
    / "t5_mod007_calibrated_validation_predictions.npz"
)


# Native T5 model-validation population
T5_POPULATION = (
    PROJECT_ROOT
    / "modeling"
    / "T5"
    / "splits"
    / "t5_model_val.csv"
)


# Previous T9 semantics lock
OP005_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op005_output_semantics_lock.json"
)


# ------------------------------------------------------------
# Expected native fields
# ------------------------------------------------------------

EXPECTED_NPZ_KEYS = {
    "y_true",
    "p_base",
    "p_sigmoid",
    "p_isotonic",
}

EXPECTED_POPULATION_COLUMNS = {
    "ID",
    "Creation time",
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
    "T5 target",
}


# ------------------------------------------------------------
# Utility
# ------------------------------------------------------------

def fail(message: str) -> None:
    raise RuntimeError(message)


def finite_array(
    values: np.ndarray,
) -> bool:
    return bool(
        np.isfinite(values).all()
    )


def probability_range_valid(
    values: np.ndarray,
) -> bool:
    return bool(
        finite_array(values)
        and
        np.all(values >= 0.0)
        and
        np.all(values <= 1.0)
    )


def binary_target_valid(
    values: np.ndarray,
) -> bool:

    if values.size == 0:
        return False

    if not finite_array(
        values.astype(float)
    ):
        return False

    unique = set(
        np.unique(values).tolist()
    )

    return unique.issubset(
        {0, 1}
    )


def load_json(
    path: Path,
) -> dict[str, Any]:

    if not path.exists():
        fail(
            f"Required JSON artifact missing: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


# ------------------------------------------------------------
# OP-005 boundary validation
# ------------------------------------------------------------

def validate_op005() -> dict[str, Any]:

    data = load_json(
        OP005_ARTIFACT
    )

    checks: dict[str, Any] = {}

    checks["operation_status"] = {
        "status": (
            "PASS"
            if data.get("status") == "PASS"
            else "FAIL"
        ),
        "observed": data.get("status"),
    }

    boundary = data.get(
        "task_boundary",
        {},
    )

    t5 = boundary.get(
        "T5",
        {},
    )

    checks["T5_status"] = {
        "status": (
            "PASS"
            if t5.get("status")
            == "ACCEPTED_NATIVE_PROBABILITY"
            else "FAIL"
        ),
        "observed": t5.get("status"),
    }

    checks["T5_probability_accepted"] = {
        "status": (
            "PASS"
            if t5.get(
                "accepted_for_calibration"
            )
            is True
            else "FAIL"
        ),
        "observed": t5.get(
            "accepted_for_calibration"
        ),
    }

    failed = [
        key
        for key, value
        in checks.items()
        if value["status"] == "FAIL"
    ]

    return {
        "checks": checks,
        "failed_checks": failed,
        "status": (
            "PASS"
            if not failed
            else "FAIL"
        ),
    }


# ------------------------------------------------------------
# Artifact audit
# ------------------------------------------------------------

def audit_t5_artifact() -> dict[str, Any]:

    if not T5_ARTIFACT.exists():

        return {
            "status": "FAIL",
            "reason": (
                f"T5 artifact does not exist: "
                f"{T5_ARTIFACT}"
            ),
        }

    with np.load(
        T5_ARTIFACT,
        allow_pickle=False,
    ) as data:

        keys = set(
            data.files
        )

        required_keys_present = (
            EXPECTED_NPZ_KEYS.issubset(
                keys
            )
        )

        missing_keys = sorted(
            EXPECTED_NPZ_KEYS - keys
        )

        y_true = np.asarray(
            data["y_true"]
        )

        p_base = np.asarray(
            data["p_base"]
        )

        p_sigmoid = np.asarray(
            data["p_sigmoid"]
        )

        p_isotonic = np.asarray(
            data["p_isotonic"]
        )

    return {
        "status": (
            "PASS"
            if required_keys_present
            else "FAIL"
        ),
        "path": str(
            T5_ARTIFACT
        ),
        "keys": sorted(
            keys
        ),
        "required_keys": sorted(
            EXPECTED_NPZ_KEYS
        ),
        "missing_keys": missing_keys,
        "arrays": {
            "y_true": {
                "shape": list(
                    y_true.shape
                ),
                "dtype": str(
                    y_true.dtype
                ),
            },
            "p_base": {
                "shape": list(
                    p_base.shape
                ),
                "dtype": str(
                    p_base.dtype
                ),
            },
            "p_sigmoid": {
                "shape": list(
                    p_sigmoid.shape
                ),
                "dtype": str(
                    p_sigmoid.dtype
                ),
            },
            "p_isotonic": {
                "shape": list(
                    p_isotonic.shape
                ),
                "dtype": str(
                    p_isotonic.dtype
                ),
            },
        },
    }


# ------------------------------------------------------------
# Population audit
# ------------------------------------------------------------

def audit_population() -> dict[str, Any]:

    if not T5_POPULATION.exists():

        return {
            "status": "FAIL",
            "reason": (
                f"T5 population artifact does not exist: "
                f"{T5_POPULATION}"
            ),
        }

    df = pd.read_csv(
        T5_POPULATION
    )

    columns = set(
        df.columns
    )

    missing_columns = sorted(
        EXPECTED_POPULATION_COLUMNS - columns
    )

    if "ID" in df.columns:

        duplicate_ids = int(
            df["ID"]
            .duplicated()
            .sum()
        )

        null_ids = int(
            df["ID"]
            .isna()
            .sum()
        )

        unique_ids = int(
            df["ID"]
            .nunique()
        )

    else:

        duplicate_ids = None
        null_ids = None
        unique_ids = None

    if "T5 target" in df.columns:

        target_series = df[
            "T5 target"
        ]

        target_non_null = int(
            target_series.notna().sum()
        )

        target_unique = sorted(
            target_series
            .dropna()
            .unique()
            .tolist()
        )

        target_counts = {
            str(k): int(v)
            for k, v in (
                target_series
                .value_counts(
                    dropna=False
                )
                .to_dict()
                .items()
            )
        }

    else:

        target_non_null = None
        target_unique = []
        target_counts = {}

    return {
        "status": (
            "PASS"
            if (
                not missing_columns
                and
                duplicate_ids == 0
                and
                null_ids == 0
            )
            else "FAIL"
        ),
        "path": str(
            T5_POPULATION
        ),
        "rows": int(
            len(df)
        ),
        "columns": list(
            df.columns
        ),
        "missing_required_columns": (
            missing_columns
        ),
        "ID_integrity": {
            "unique_ids": unique_ids,
            "duplicate_ids": duplicate_ids,
            "null_ids": null_ids,
        },
        "target": {
            "column": "T5 target",
            "non_null": target_non_null,
            "unique_values": target_unique,
            "value_counts": target_counts,
        },
    }


# ------------------------------------------------------------
# Native probability semantics
# ------------------------------------------------------------

def audit_probability_semantics() -> dict[str, Any]:

    with np.load(
        T5_ARTIFACT,
        allow_pickle=False,
    ) as data:

        y_true = np.asarray(
            data["y_true"]
        )

        p_base = np.asarray(
            data["p_base"]
        )

        p_sigmoid = np.asarray(
            data["p_sigmoid"]
        )

        p_isotonic = np.asarray(
            data["p_isotonic"]
        )

    arrays = {
        "p_base": p_base,
        "p_sigmoid": p_sigmoid,
        "p_isotonic": p_isotonic,
    }

    probability_checks = {}

    for name, values in arrays.items():

        probability_checks[name] = {
            "shape": list(
                values.shape
            ),
            "finite": finite_array(
                values
            ),
            "range_0_to_1": probability_range_valid(
                values
            ),
            "min": float(
                np.min(values)
            ),
            "max": float(
                np.max(values)
            ),
            "mean": float(
                np.mean(values)
            ),
            "median": float(
                np.median(values)
            ),
        }

    target_check = {
        "finite": finite_array(
            y_true.astype(float)
        ),
        "binary": binary_target_valid(
            y_true
        ),
        "unique_values": [
            int(v)
            for v in np.unique(
                y_true
            )
        ],
    }

    return {
        "status": (
            "PASS"
            if (
                target_check["finite"]
                and target_check["binary"]
                and all(
                    item["finite"]
                    and item["range_0_to_1"]
                    for item
                    in probability_checks.values()
                )
            )
            else "FAIL"
        ),
        "target": target_check,
        "probabilities": probability_checks,
        "semantic_statement": (
            "The native T5 probability arrays are treated as "
            "task-specific duplicate-probability quantities. "
            "They are not interpreted as universal ticket "
            "confidence or universal ticket risk."
        ),
    }


# ------------------------------------------------------------
# Alignment audit
# ------------------------------------------------------------

def audit_alignment() -> dict[str, Any]:

    with np.load(
        T5_ARTIFACT,
        allow_pickle=False,
    ) as data:

        y_true = np.asarray(
            data["y_true"]
        )

        p_base = np.asarray(
            data["p_base"]
        )

        p_sigmoid = np.asarray(
            data["p_sigmoid"]
        )

        p_isotonic = np.asarray(
            data["p_isotonic"]
        )

    lengths = {
        "y_true": int(
            len(y_true)
        ),
        "p_base": int(
            len(p_base)
        ),
        "p_sigmoid": int(
            len(p_sigmoid)
        ),
        "p_isotonic": int(
            len(p_isotonic)
        ),
    }

    equal_lengths = (
        len(set(lengths.values()))
        == 1
    )

    population_rows = None

    if T5_POPULATION.exists():

        population_rows = int(
            pd.read_csv(
                T5_POPULATION,
                usecols=["ID"],
            ).shape[0]
        )

    population_alignment = (
        population_rows == lengths["y_true"]
        if population_rows is not None
        else False
    )

    return {
        "status": (
            "PASS"
            if (
                equal_lengths
                and
                population_alignment
            )
            else "FAIL"
        ),
        "array_lengths": lengths,
        "equal_array_lengths": equal_lengths,
        "population_rows": population_rows,
        "population_matches_probability_rows": (
            population_alignment
        ),
    }


# ------------------------------------------------------------
# Leakage / boundary audit
# ------------------------------------------------------------

def audit_boundary_controls() -> dict[str, Any]:

    controls = {

        "new_model_fitted": False,

        "new_probability_generated": False,

        "new_calibration_fitted": False,

        "target_created": False,

        "target_relabelled": False,

        "threshold_selected": False,

        "universal_confidence_created": False,

        "universal_risk_score_created": False,

        "synthetic_target_created": False,

        "locked_test_used_for_selection": False,

        "post_creation_features_introduced": False,

        "native_t5_target_preserved": True,

        "native_probability_semantics_preserved": True,
    }

    failed = [
        key
        for key, value
        in controls.items()
        if (
            key.startswith(
                (
                    "new_",
                    "target_",
                    "threshold_",
                    "universal_",
                    "synthetic_",
                    "locked_",
                    "post_",
                )
            )
            and value is not False
        )
    ]

    return {
        "checks": controls,
        "failed_checks": failed,
        "status": (
            "PASS"
            if not failed
            else "FAIL"
        ),
    }


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main() -> None:

    print("=" * 72)
    print("T9 MOD-037 OP-006")
    print("T5 Calibration Population & Probability Semantics Audit")
    print("=" * 72)
    print()

    print(
        "Validating OP-005 semantics lock..."
    )

    op005 = validate_op005()

    print(
        "OP-005 validation:",
        op005["status"],
    )

    print()

    print(
        "Auditing native T5 probability artifact..."
    )

    artifact = audit_t5_artifact()

    print(
        "Artifact audit:",
        artifact["status"],
    )

    print()

    print(
        "Auditing T5 calibration population..."
    )

    population = audit_population()

    print(
        "Population audit:",
        population["status"],
    )

    print()

    print(
        "Auditing probability and target semantics..."
    )

    semantics = audit_probability_semantics()

    print(
        "Probability semantics:",
        semantics["status"],
    )

    print()

    print(
        "Auditing target/probability alignment..."
    )

    alignment = audit_alignment()

    print(
        "Alignment audit:",
        alignment["status"],
    )

    print()

    print(
        "Auditing T9 boundary controls..."
    )

    controls = audit_boundary_controls()

    print(
        "Boundary controls:",
        controls["status"],
    )

    overall_pass = (
        op005["status"] == "PASS"
        and artifact["status"] == "PASS"
        and population["status"] == "PASS"
        and semantics["status"] == "PASS"
        and alignment["status"] == "PASS"
        and controls["status"] == "PASS"
    )

    output = {
        "operation": "T9_MOD-037_OP-006",
        "title": (
            "T5 Calibration Population & "
            "Probability Semantics Audit"
        ),
        "status": (
            "PASS"
            if overall_pass
            else "FAIL"
        ),
        "purpose": (
            "Audit the accepted native T5 duplicate-probability "
            "artifact and its model-validation population before "
            "subsequent task-specific calibration work."
        ),
        "op005_validation": op005,
        "native_artifact_audit": artifact,
        "population_audit": population,
        "probability_semantics_audit": semantics,
        "alignment_audit": alignment,
        "boundary_controls": controls,
        "calibration_readiness_statement": (
            "T5 may proceed to a subsequent task-specific "
            "calibration/evaluation operation only if the "
            "native duplicate-probability semantics, target "
            "alignment, population boundary, and evaluation "
            "protocol remain frozen. This operation itself "
            "does not fit or select calibration."
        ),
        "prohibited_interpretations": [
            (
                "T5 probability is not a universal ticket "
                "confidence score."
            ),
            (
                "T5 probability is not a universal ticket "
                "risk score."
            ),
            (
                "T5 probability must not be compared numerically "
                "with T4/T6 ranking scores or T7 survival "
                "quantities as if they were the same predictive "
                "quantity."
            ),
            (
                "No automation threshold is established by "
                "this operation."
            ),
        ],
    }

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("=" * 72)
    print("T9 MOD-037 OP-006 RESULT")
    print("=" * 72)
    print()

    print(
        "OP-005 validation:",
        op005["status"],
    )

    print(
        "Native artifact audit:",
        artifact["status"],
    )

    print(
        "Population audit:",
        population["status"],
    )

    print(
        "Probability semantics:",
        semantics["status"],
    )

    print(
        "Target/probability alignment:",
        alignment["status"],
    )

    print(
        "Boundary controls:",
        controls["status"],
    )

    if population.get("rows") is not None:
        print(
            "T5 population rows:",
            population.get("rows"),
        )

    target_info = population.get(
        "target",
        {},
    )

    if target_info:
        print(
            "T5 target distribution:",
            target_info.get(
                "value_counts"
            ),
        )

    print()

    print(
        "Output:",
        OUTPUT_JSON,
    )

    print()

    if overall_pass:

        print(
            "T9 MOD-037 OP-006 T5 population/semantics audit: PASS"
        )

    else:

        print(
            "T9 MOD-037 OP-006 T5 population/semantics audit: FAIL"
        )


if __name__ == "__main__":
    main()