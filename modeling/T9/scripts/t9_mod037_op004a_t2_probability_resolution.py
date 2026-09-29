from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


# ============================================================
# T9 MOD-037 OP-004A
# T2 Native Probability Artifact Resolution
#
# Purpose:
#   Search existing T2 artifacts for a native class-probability
#   output suitable for later T9 calibration.
#
# This operation DOES NOT:
#   - fit a model
#   - generate probabilities
#   - fit calibration
#   - create targets
#   - select a model
#   - select thresholds
#   - modify the locked test set
# ============================================================


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_ROOT = PROJECT_ROOT / "modeling" / "T2"

OUTPUT_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "T9"
    / "mod037"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_JSON = (
    OUTPUT_DIR
    / "t9_mod037_op004a_t2_probability_resolution.json"
)


EXPECTED_PROBABILITY_COLUMNS = [
    "T2_probability_P1",
    "T2_probability_P2",
    "T2_probability_P3",
    "T2_probability_P4",
    "T2_probability_P5",
]


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def rel(path: Path) -> str:
    try:
        return str(
            path.relative_to(PROJECT_ROOT)
        )
    except ValueError:
        return str(path)


def inspect_csv(path: Path) -> dict[str, Any]:

    result: dict[str, Any] = {
        "path": rel(path),
        "format": "csv",
        "status": "UNKNOWN",
    }

    try:
        header = pd.read_csv(
            path,
            nrows=0,
        )

        result["columns"] = [
            str(c)
            for c in header.columns
        ]

        result["column_count"] = len(
            header.columns
        )

        result["has_expected_probability_columns"] = (
            all(
                column in header.columns
                for column
                in EXPECTED_PROBABILITY_COLUMNS
            )
        )

        result["probability_columns_found"] = [
            column
            for column in EXPECTED_PROBABILITY_COLUMNS
            if column in header.columns
        ]

        result["status"] = "PASS"

    except Exception as exc:

        result["status"] = "ERROR"
        result["error"] = repr(exc)

    return result


def inspect_npz(path: Path) -> dict[str, Any]:

    result: dict[str, Any] = {
        "path": rel(path),
        "format": "npz",
        "status": "UNKNOWN",
    }

    try:

        with np.load(
            path,
            allow_pickle=False,
        ) as data:

            keys = list(data.files)

            result["keys"] = keys

            result["probability_keys_found"] = [
                key
                for key in keys
                if (
                    "probability" in key.lower()
                    or "prob_" in key.lower()
                    or key.startswith("p_")
                )
            ]

        result["status"] = "PASS"

    except Exception as exc:

        result["status"] = "ERROR"
        result["error"] = repr(exc)

    return result


def inspect_file(path: Path) -> dict[str, Any]:

    suffix = path.suffix.lower()

    if suffix == ".csv":
        return inspect_csv(path)

    if suffix == ".npz":
        return inspect_npz(path)

    return {
        "path": rel(path),
        "format": suffix,
        "status": "SKIPPED",
    }


# ------------------------------------------------------------
# Candidate discovery
# ------------------------------------------------------------

def discover_candidates() -> list[Path]:

    candidates = []

    if not T2_ROOT.exists():
        return candidates

    for path in T2_ROOT.rglob("*"):

        if not path.is_file():
            continue

        if path.suffix.lower() not in {
            ".csv",
            ".npz",
        }:
            continue

        candidates.append(path)

    return sorted(
        candidates,
        key=lambda p: str(p),
    )


# ------------------------------------------------------------
# Detailed T2 CSV validation
# ------------------------------------------------------------

def validate_probability_csv(
    path: Path,
) -> dict[str, Any]:

    result: dict[str, Any] = {
        "path": rel(path),
        "status": "UNKNOWN",
        "checks": {},
    }

    try:

        df = pd.read_csv(path)

    except Exception as exc:

        result["status"] = "FAIL"
        result["error"] = repr(exc)

        return result

    result["rows"] = int(
        len(df)
    )

    result["columns"] = [
        str(c)
        for c in df.columns
    ]

    # --------------------------------------------------------
    # Required structural columns
    # --------------------------------------------------------

    required = {
        "ID",
        "target_priority",
        *EXPECTED_PROBABILITY_COLUMNS,
    }

    missing = sorted(
        required - set(df.columns)
    )

    if missing:

        result["checks"][
            "required_columns"
        ] = {
            "status": "FAIL",
            "missing": missing,
        }

        result["status"] = "FAIL"

        return result

    result["checks"][
        "required_columns"
    ] = {
        "status": "PASS",
        "columns": sorted(required),
    }

    # --------------------------------------------------------
    # ID integrity
    # --------------------------------------------------------

    duplicate_ids = int(
        df["ID"].duplicated().sum()
    )

    null_ids = int(
        df["ID"].isna().sum()
    )

    result["checks"]["ID_integrity"] = {
        "status": (
            "PASS"
            if duplicate_ids == 0
            and null_ids == 0
            else "FAIL"
        ),
        "rows": int(len(df)),
        "unique_ids": int(
            df["ID"].nunique()
        ),
        "duplicate_ids": duplicate_ids,
        "null_ids": null_ids,
    }

    # --------------------------------------------------------
    # Target integrity
    # --------------------------------------------------------

    target_nulls = int(
        df["target_priority"].isna().sum()
    )

    target_values = sorted(
        df["target_priority"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    result["target_values"] = target_values

    result["checks"]["target_integrity"] = {
        "status": (
            "PASS"
            if target_nulls == 0
            else "FAIL"
        ),
        "null_targets": target_nulls,
        "unique_targets": target_values,
    }

    # --------------------------------------------------------
    # Probability conversion
    # --------------------------------------------------------

    probabilities = df[
        EXPECTED_PROBABILITY_COLUMNS
    ].apply(
        pd.to_numeric,
        errors="coerce",
    )

    non_numeric_counts = {
        column: int(
            probabilities[column].isna().sum()
        )
        for column
        in EXPECTED_PROBABILITY_COLUMNS
    }

    result["checks"][
        "probability_numeric"
    ] = {
        "status": (
            "PASS"
            if all(
                count == 0
                for count
                in non_numeric_counts.values()
            )
            else "FAIL"
        ),
        "non_numeric_or_null_counts": (
            non_numeric_counts
        ),
    }

    # --------------------------------------------------------
    # Probability bounds
    # --------------------------------------------------------

    values = probabilities.to_numpy(
        dtype=float
    )

    finite = np.isfinite(
        values
    )

    finite_all = bool(
        finite.all()
    )

    if finite_all:

        minimum = float(
            values.min()
        )

        maximum = float(
            values.max()
        )

        out_of_bounds = int(
            np.sum(
                (values < 0.0)
                | (values > 1.0)
            )
        )

    else:

        minimum = None
        maximum = None
        out_of_bounds = -1

    result["checks"][
        "probability_bounds"
    ] = {
        "status": (
            "PASS"
            if finite_all
            and out_of_bounds == 0
            else "FAIL"
        ),
        "min": minimum,
        "max": maximum,
        "out_of_bounds": out_of_bounds,
        "finite": finite_all,
    }

    # --------------------------------------------------------
    # Row-wise probability sums
    # --------------------------------------------------------

    if finite_all:

        row_sums = values.sum(
            axis=1
        )

        deviation = np.abs(
            row_sums - 1.0
        )

        max_deviation = float(
            deviation.max()
        )

        rows_not_summing_to_one = int(
            np.sum(
                deviation > 1e-5
            )
        )

        result["checks"][
            "probability_normalization"
        ] = {
            "status": (
                "PASS"
                if rows_not_summing_to_one == 0
                else "FAIL"
            ),
            "rows": int(
                len(row_sums)
            ),
            "row_sum_min": float(
                row_sums.min()
            ),
            "row_sum_max": float(
                row_sums.max()
            ),
            "max_absolute_deviation": (
                max_deviation
            ),
            "rows_not_summing_to_one": (
                rows_not_summing_to_one
            ),
        }

    else:

        result["checks"][
            "probability_normalization"
        ] = {
            "status": "FAIL",
            "reason": (
                "Normalization cannot be evaluated "
                "because probability values are not "
                "all finite."
            ),
        }

    # --------------------------------------------------------
    # Predicted class alignment
    # --------------------------------------------------------

    if "predicted_priority" in df.columns:

        predicted_from_probability = (
            probabilities
            .idxmax(axis=1)
            .str.replace(
                "T2_probability_",
                "",
                regex=False,
            )
        )

        predicted_column = (
            df["predicted_priority"]
            .astype(str)
        )

        alignment = (
            predicted_from_probability
            == predicted_column
        )

        mismatch_count = int(
            (~alignment).sum()
        )

        result["checks"][
            "prediction_probability_alignment"
        ] = {
            "status": (
                "PASS"
                if mismatch_count == 0
                else "FAIL"
            ),
            "rows": int(
                len(df)
            ),
            "mismatches": mismatch_count,
        }

    else:

        result["checks"][
            "prediction_probability_alignment"
        ] = {
            "status": "NOT_AVAILABLE",
            "reason": (
                "predicted_priority column is absent."
            ),
        }

    # --------------------------------------------------------
    # Population classification
    # --------------------------------------------------------

    filename_lower = (
        path.name.lower()
    )

    if "test" in filename_lower:

        population_role = (
            "LOCKED_TEST_CANDIDATE"
        )

    elif (
        "validation" in filename_lower
        or "val" in filename_lower
    ):

        population_role = (
            "DEVELOPMENT_VALIDATION_CANDIDATE"
        )

    elif "train" in filename_lower:

        population_role = (
            "DEVELOPMENT_TRAIN_CANDIDATE"
        )

    else:

        population_role = (
            "UNKNOWN_POPULATION_ROLE"
        )

    result["population_role"] = (
        population_role
    )

    result["checks"][
        "locked_test_boundary"
    ] = {
        "status": (
            "FAIL"
            if population_role
            == "LOCKED_TEST_CANDIDATE"
            else "PASS"
        ),
        "population_role": (
            population_role
        ),
    }

    # --------------------------------------------------------
    # Overall acceptance
    # --------------------------------------------------------

    required_pass_checks = [
        "required_columns",
        "ID_integrity",
        "target_integrity",
        "probability_numeric",
        "probability_bounds",
        "probability_normalization",
        "locked_test_boundary",
    ]

    # Prediction alignment is useful but is only evaluated
    # when predicted_priority exists.
    if (
        result["checks"][
            "prediction_probability_alignment"
        ]["status"]
        != "NOT_AVAILABLE"
    ):
        required_pass_checks.append(
            "prediction_probability_alignment"
        )

    result["status"] = (
        "PASS"
        if all(
            result["checks"][key]["status"]
            == "PASS"
            for key
            in required_pass_checks
        )
        else "FAIL"
    )

    return result


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main() -> None:

    print("=" * 72)
    print("T9 MOD-037 OP-004A")
    print("T2 Native Probability Artifact Resolution")
    print("=" * 72)
    print()

    print(
        f"T2 root: {T2_ROOT}"
    )

    print(
        f"Output:  {OUTPUT_JSON}"
    )

    print()

    candidates = discover_candidates()

    print(
        f"Candidate structured artifacts discovered: "
        f"{len(candidates)}"
    )

    print()

    # --------------------------------------------------------
    # Discovery inventory
    # --------------------------------------------------------

    inventory = []

    for path in candidates:

        result = inspect_file(path)

        # Only display files that contain probability-like
        # evidence or prediction-like filenames.
        lower_name = path.name.lower()

        probability_hint = any(
            token in lower_name
            for token in (
                "prob",
                "prediction",
                "predict",
                "oof",
            )
        )

        if (
            probability_hint
            or result.get(
                "has_expected_probability_columns",
                False,
            )
            or result.get(
                "probability_keys_found",
                [],
            )
        ):

            inventory.append(
                result
            )

    print(
        "Probability/prediction candidate artifacts:"
    )

    for item in inventory:

        print(
            f"  {item['path']}"
        )

    print()

    # --------------------------------------------------------
    # Exact probability candidates
    # --------------------------------------------------------

    exact_candidates = []

    for path in candidates:

        if path.suffix.lower() != ".csv":
            continue

        inspection = inspect_csv(
            path
        )

        if (
            inspection.get(
                "has_expected_probability_columns",
                False,
            )
        ):

            exact_candidates.append(
                path
            )

    print(
        "Exact T2 probability-column candidates:",
        len(exact_candidates),
    )

    print()

    # --------------------------------------------------------
    # Detailed validation
    # --------------------------------------------------------

    validations = []

    for path in exact_candidates:

        print(
            f"Validating: {rel(path)}"
        )

        validation = (
            validate_probability_csv(
                path
            )
        )

        validations.append(
            validation
        )

    print()

    accepted = [
        item
        for item in validations
        if item.get("status") == "PASS"
    ]

    rejected = [
        item
        for item in validations
        if item.get("status") != "PASS"
    ]

    # --------------------------------------------------------
    # Important distinction:
    #
    # No exact probability candidate is NOT an operation
    # failure. It means T2 has no accepted native probability
    # artifact under the current evidence boundary.
    #
    # The operation itself passes if the resolution search
    # completed successfully without creating anything.
    # --------------------------------------------------------

    controls = {
        "model_fitting_performed": False,
        "probability_generation_performed": False,
        "calibration_fitting_performed": False,
        "target_creation_performed": False,
        "model_selection_performed": False,
        "threshold_selection_performed": False,
        "locked_test_used_for_selection": False,
        "synthetic_probability_created": False,
    }

    output = {
        "operation": "T9_MOD-037_OP-004A",
        "title": (
            "T2 Native Probability Artifact Resolution"
        ),
        "status": "PASS",
        "purpose": (
            "Resolve whether an existing native T2 artifact "
            "contains valid class probabilities suitable for "
            "later task-specific T9 calibration."
        ),
        "expected_probability_columns": (
            EXPECTED_PROBABILITY_COLUMNS
        ),
        "candidate_count": len(candidates),
        "candidate_inventory": inventory,
        "exact_probability_candidate_count": (
            len(exact_candidates)
        ),
        "validations": validations,
        "accepted_native_probability_artifacts": [
            item["path"]
            for item in accepted
        ],
        "rejected_native_probability_artifacts": [
            item["path"]
            for item in rejected
        ],
        "controls": controls,
        "interpretation": {
            "no_candidate": (
                "If no accepted native probability artifact "
                "exists, T2 probability calibration is not "
                "empirically established and no probabilities "
                "may be generated by this operation."
            ),
            "accepted_candidate": (
                "An accepted artifact is evidence of an "
                "existing native T2 probability output only. "
                "Calibration remains a later operation."
            ),
            "locked_test": (
                "Locked test artifacts cannot be selected "
                "for calibration fitting or model selection."
            ),
        },
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

    # --------------------------------------------------------
    # Console summary
    # --------------------------------------------------------

    print("=" * 72)
    print("T9 MOD-037 OP-004A RESULT")
    print("=" * 72)
    print()

    print(
        "Exact probability candidates:",
        len(exact_candidates),
    )

    print(
        "Accepted native probability artifacts:",
        len(accepted),
    )

    print(
        "Rejected native probability artifacts:",
        len(rejected),
    )

    print()

    for item in accepted:

        print(
            "ACCEPTED:",
            item["path"],
        )

    for item in rejected:

        print(
            "REJECTED:",
            item["path"],
        )

    print()

    print("Controls:")

    for key, value in controls.items():

        print(
            f"  {key}: {value}"
        )

    print()

    print(
        f"Output: {OUTPUT_JSON}"
    )

    print()

    print(
        "T9 MOD-037 OP-004A resolution: PASS"
    )


if __name__ == "__main__":
    main()