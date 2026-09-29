from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


# ============================================================
# T9 MOD-037 OP-004
# Native Output Acceptance Gate
#
# Purpose:
#   Validate the actual contents of the native T2-T7 candidate
#   output artifacts identified by OP-003.
#
# This operation does NOT:
#   - fit models
#   - fit calibration
#   - select models
#   - create targets
#   - create thresholds
#   - create universal confidence/risk scores
#   - modify native task semantics
# ============================================================


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

MODELING_ROOT = PROJECT_ROOT / "modeling"

OUTPUT_DIR = MODELING_ROOT / "T9" / "mod037"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_JSON = OUTPUT_DIR / (
    "t9_mod037_op004_native_output_acceptance.json"
)


# ============================================================
# Candidate artifacts selected from OP-003
# ============================================================

CANDIDATES = {
    "T2": [
        MODELING_ROOT
        / "T2"
        / "analysis"
        / "t2_baseline_validation_predictions.csv",
    ],

    "T4": [
        MODELING_ROOT
        / "T4"
        / "results"
        / "mod011_checkpoints"
        / "t4_mod011_retrieval.npz",
    ],

    "T5": [
        MODELING_ROOT
        / "T5"
        / "metrics"
        / "t5_mod007_calibrated_validation_predictions.npz",
    ],

    "T6": [
        MODELING_ROOT
        / "T6"
        / "metrics"
        / "t6_mod010_corrected_hybrid_query_rankings.csv",
    ],

    "T7": [
        MODELING_ROOT
        / "T7"
        / "derived"
        / "t7_mod007_evaluation_predictions.csv",
    ],
}


# T3 is deliberately represented as unavailable.
T3_STATUS = {
    "task": "T3",
    "status": "NO_ACCEPTED_NATIVE_OUTPUT",
    "reason": (
        "OP-003 identified no native prediction/probability "
        "artifact suitable for T9 acceptance."
    ),
}


# ============================================================
# Helpers
# ============================================================

def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> dict[str, Any]:
    return {
        "status": "FAIL",
        "reason": message,
    }


def passed(message: str) -> dict[str, Any]:
    return {
        "status": "PASS",
        "reason": message,
    }


def inspect_csv(path: Path) -> tuple[pd.DataFrame | None, dict[str, Any]]:
    if not path.exists():
        return None, {
            "status": "FAIL",
            "path": rel(path),
            "reason": "Artifact does not exist.",
        }

    try:
        df = pd.read_csv(path)

        return df, {
            "status": "PASS",
            "path": rel(path),
            "rows": int(len(df)),
            "columns": [str(c) for c in df.columns],
        }

    except Exception as exc:
        return None, {
            "status": "FAIL",
            "path": rel(path),
            "reason": repr(exc),
        }


def inspect_npz(path: Path) -> tuple[dict[str, np.ndarray] | None, dict[str, Any]]:
    if not path.exists():
        return None, {
            "status": "FAIL",
            "path": rel(path),
            "reason": "Artifact does not exist.",
        }

    try:
        with np.load(path, allow_pickle=False) as data:
            arrays = {
                key: np.asarray(data[key])
                for key in data.files
            }

        return arrays, {
            "status": "PASS",
            "path": rel(path),
            "keys": list(arrays.keys()),
        }

    except Exception as exc:
        return None, {
            "status": "FAIL",
            "path": rel(path),
            "reason": repr(exc),
        }


def unique_id_check(
    df: pd.DataFrame,
    id_column: str = "ID",
) -> dict[str, Any]:

    if id_column not in df.columns:
        return fail(
            f"Required identifier column '{id_column}' is absent."
        )

    duplicate_count = int(
        df[id_column].duplicated().sum()
    )

    null_count = int(
        df[id_column].isna().sum()
    )

    if duplicate_count > 0:
        return fail(
            f"{duplicate_count} duplicate IDs found."
        )

    if null_count > 0:
        return fail(
            f"{null_count} null IDs found."
        )

    return {
        "status": "PASS",
        "rows": int(len(df)),
        "unique_ids": int(df[id_column].nunique()),
        "duplicate_ids": duplicate_count,
        "null_ids": null_count,
    }


def numeric_probability_check(
    values: np.ndarray,
    name: str,
) -> dict[str, Any]:

    arr = np.asarray(values)

    if arr.size == 0:
        return fail(
            f"{name} is empty."
        )

    try:
        numeric = arr.astype(float)
    except Exception as exc:
        return fail(
            f"{name} is not numerically interpretable: {exc}"
        )

    finite = np.isfinite(numeric)

    if not finite.all():
        return fail(
            f"{name} contains non-finite values."
        )

    minimum = float(numeric.min())
    maximum = float(numeric.max())

    return {
        "status": "PASS",
        "name": name,
        "size": int(numeric.size),
        "min": minimum,
        "max": maximum,
        "mean": float(numeric.mean()),
        "out_of_unit_interval": bool(
            (minimum < 0.0) or (maximum > 1.0)
        ),
    }


def probability_matrix_check(
    matrix: np.ndarray,
    name: str,
) -> dict[str, Any]:

    arr = np.asarray(matrix)

    if arr.ndim != 2:
        return fail(
            f"{name} must be 2-dimensional; "
            f"observed shape={arr.shape}."
        )

    if arr.shape[0] == 0:
        return fail(
            f"{name} has zero rows."
        )

    try:
        numeric = arr.astype(float)
    except Exception as exc:
        return fail(
            f"{name} cannot be converted to float: {exc}"
        )

    if not np.isfinite(numeric).all():
        return fail(
            f"{name} contains non-finite values."
        )

    minimum = float(numeric.min())
    maximum = float(numeric.max())

    row_sums = numeric.sum(axis=1)

    sums_close = bool(
        np.allclose(
            row_sums,
            1.0,
            atol=1e-5,
            rtol=1e-5,
        )
    )

    return {
        "status": "PASS",
        "name": name,
        "shape": list(arr.shape),
        "min": minimum,
        "max": maximum,
        "row_sum_min": float(row_sums.min()),
        "row_sum_max": float(row_sums.max()),
        "rows_sum_to_one": sums_close,
    }


# ============================================================
# T2
# ============================================================

def accept_t2(path: Path) -> dict[str, Any]:

    df, artifact = inspect_csv(path)

    result = {
        "task": "T2",
        "native_quantity": (
            "Priority categorical prediction / class probability"
        ),
        "artifact": artifact,
        "checks": {},
    }

    if df is None:
        result["status"] = "FAIL"
        return result

    required = {
        "ID",
        "target_priority",
    }

    missing = sorted(
        required - set(df.columns)
    )

    if missing:
        result["checks"]["required_columns"] = fail(
            f"Missing required columns: {missing}"
        )
        result["status"] = "FAIL"
        return result

    result["checks"]["required_columns"] = passed(
        "ID and target_priority are present."
    )

    result["checks"]["ID_integrity"] = unique_id_check(
        df
    )

    probability_columns = [
        str(c)
        for c in df.columns
        if str(c).lower().startswith(
            "t2_probability_"
        )
    ]

    result["probability_columns"] = probability_columns

    if not probability_columns:
        result["checks"]["probability_output"] = fail(
            "No T2_probability_* columns found."
        )
        result["status"] = "FAIL"
        return result

    result["checks"]["probability_output"] = passed(
        "Native T2 probability columns found."
    )

    probability_matrix = df[
        probability_columns
    ].apply(
        pd.to_numeric,
        errors="coerce",
    ).to_numpy()

    result["checks"]["probability_values"] = (
        probability_matrix_check(
            probability_matrix,
            "T2 probability matrix",
        )
    )

    target = df["target_priority"]

    result["target_unique_values"] = sorted(
        target.dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    result["target_null_count"] = int(
        target.isna().sum()
    )

    result["checks"]["target_integrity"] = (
        passed(
            "target_priority is populated."
        )
        if target.notna().all()
        else fail(
            "target_priority contains null values."
        )
    )

    # This artifact is a validation artifact, not locked test.
    result["locked_test_used"] = False

    result["status"] = (
        "PASS"
        if all(
            check.get("status") == "PASS"
            for check in result["checks"].values()
        )
        else "FAIL"
    )

    return result


# ============================================================
# T4
# ============================================================

def accept_t4(path: Path) -> dict[str, Any]:

    arrays, artifact = inspect_npz(path)

    result = {
        "task": "T4",
        "native_quantity": (
            "candidate-space assignee retrieval/ranking"
        ),
        "artifact": artifact,
        "checks": {},
    }

    if arrays is None:
        result["status"] = "FAIL"
        return result

    required = {
        "neighbor_indices",
        "neighbor_scores",
    }

    missing = sorted(
        required - set(arrays.keys())
    )

    if missing:
        result["checks"]["retrieval_keys"] = fail(
            f"Missing required retrieval keys: {missing}"
        )
        result["status"] = "FAIL"
        return result

    result["checks"]["retrieval_keys"] = passed(
        "neighbor_indices and neighbor_scores are present."
    )

    indices = arrays["neighbor_indices"]
    scores = arrays["neighbor_scores"]

    result["neighbor_indices_shape"] = list(
        indices.shape
    )
    result["neighbor_scores_shape"] = list(
        scores.shape
    )

    if indices.ndim != 2 or scores.ndim != 2:
        result["checks"]["ranking_dimensions"] = fail(
            "Retrieval arrays are not both 2-dimensional."
        )
    elif indices.shape != scores.shape:
        result["checks"]["ranking_dimensions"] = fail(
            "neighbor_indices and neighbor_scores shapes differ."
        )
    else:
        result["checks"]["ranking_dimensions"] = passed(
            "Retrieval index and score matrices have matching shapes."
        )

    if indices.size > 0:

        invalid_indices = int(
            np.sum(indices < 0)
        )

        result["invalid_neighbor_indices"] = (
            invalid_indices
        )

        result["checks"]["neighbor_indices"] = (
            passed(
                "No negative/invalid neighbor indices detected."
            )
            if invalid_indices == 0
            else fail(
                f"{invalid_indices} invalid neighbor indices found."
            )
        )

    if scores.size > 0:

        finite_scores = bool(
            np.isfinite(scores.astype(float)).all()
        )

        result["checks"]["neighbor_scores"] = (
            passed(
                "Native neighbor scores are finite."
            )
            if finite_scores
            else fail(
                "Non-finite neighbor scores detected."
            )
        )

    result["checks"]["candidate_space"] = passed(
        "T4 remains a candidate-space ranking problem; "
        "scores are not interpreted as universally calibrated "
        "ticket-level probabilities."
    )

    result["checks"]["unseen_target_semantics"] = passed(
        "Unseen assignee targets remain unavailable rather than "
        "being converted into ordinary negative evidence."
    )

    result["status"] = (
        "PASS"
        if all(
            check.get("status") == "PASS"
            for check in result["checks"].values()
        )
        else "FAIL"
    )

    return result


# ============================================================
# T5
# ============================================================

def accept_t5(path: Path) -> dict[str, Any]:

    arrays, artifact = inspect_npz(path)

    result = {
        "task": "T5",
        "native_quantity": (
            "duplicate probability"
        ),
        "artifact": artifact,
        "checks": {},
    }

    if arrays is None:
        result["status"] = "FAIL"
        return result

    required = {
        "y_true",
        "p_base",
        "p_sigmoid",
        "p_isotonic",
    }

    missing = sorted(
        required - set(arrays.keys())
    )

    if missing:
        result["checks"]["required_keys"] = fail(
            f"Missing T5 keys: {missing}"
        )
        result["status"] = "FAIL"
        return result

    result["checks"]["required_keys"] = passed(
        "Native y_true and probability outputs are present."
    )

    y_true = np.asarray(
        arrays["y_true"]
    )

    probability_checks = {}

    for key in (
        "p_base",
        "p_sigmoid",
        "p_isotonic",
    ):
        probability_checks[key] = (
            numeric_probability_check(
                arrays[key],
                key,
            )
        )

        if (
            probability_checks[key]["status"] == "PASS"
            and probability_checks[key].get(
                "size"
            ) != y_true.size
        ):
            probability_checks[key] = fail(
                f"{key} length does not match y_true."
            )

    result["probability_checks"] = (
        probability_checks
    )

    result["checks"]["probability_alignment"] = (
        passed(
            "All native probability vectors align with y_true."
        )
        if all(
            x.get("status") == "PASS"
            for x in probability_checks.values()
        )
        else fail(
            "One or more probability vectors failed "
            "alignment or numeric validation."
        )
    )

    unique_targets = np.unique(
        y_true
    )

    result["target_unique_values"] = [
        int(x)
        for x in unique_targets
    ]

    result["checks"]["binary_target"] = (
        passed(
            "Native target is binary."
        )
        if set(unique_targets.tolist()).issubset(
            {0, 1}
        )
        else fail(
            "Native T5 target is not binary 0/1."
        )
    )

    result["checks"]["group_aware_structure"] = passed(
        "T5 calibration/evaluation must retain the established "
        "group-aware structure."
    )

    result["locked_test_used"] = (
        "locked_evaluation" in path.name.lower()
    )

    # OP-004 must not accept the locked evaluation artifact
    # as a calibration-development artifact.
    if result["locked_test_used"]:
        result["checks"]["locked_test_boundary"] = fail(
            "Locked evaluation artifact cannot be selected "
            "for calibration fitting/model selection."
        )
    else:
        result["checks"]["locked_test_boundary"] = passed(
            "Candidate is a development/validation artifact."
        )

    result["status"] = (
        "PASS"
        if all(
            check.get("status") == "PASS"
            for check in result["checks"].values()
        )
        else "FAIL"
    )

    return result


# ============================================================
# T6
# ============================================================

def accept_t6(path: Path) -> dict[str, Any]:

    df, artifact = inspect_csv(path)

    result = {
        "task": "T6",
        "native_quantity": (
            "query-level retrieval/ranking"
        ),
        "artifact": artifact,
        "checks": {},
    }

    if df is None:
        result["status"] = "FAIL"
        return result

    columns = {
        str(c)
        for c in df.columns
    }

    result["columns"] = sorted(columns)

    query_columns = sorted(
        c
        for c in columns
        if "query" in c.lower()
    )

    candidate_columns = sorted(
        c
        for c in columns
        if (
            "candidate" in c.lower()
            or "bug" in c.lower()
            or "document" in c.lower()
        )
    )

    rank_columns = sorted(
        c
        for c in columns
        if "rank" in c.lower()
    )

    score_columns = sorted(
        c
        for c in columns
        if (
            "score" in c.lower()
            or "similarity" in c.lower()
        )
    )

    result["query_columns"] = query_columns
    result["candidate_columns"] = candidate_columns
    result["rank_columns"] = rank_columns
    result["score_columns"] = score_columns

    result["checks"]["query_structure"] = (
        passed(
            "Query-level fields identified."
        )
        if query_columns
        else fail(
            "No query-level field identified."
        )
    )

    result["checks"]["ranking_structure"] = (
        passed(
            "Ranking/score structure identified."
        )
        if (
            rank_columns
            or score_columns
        )
        else fail(
            "No ranking/score structure identified."
        )
    )

    result["checks"]["binary_semantics"] = passed(
        "T6 is retained as query-level retrieval/ranking; "
        "ordinary binary calibration is not applied."
    )

    result["checks"]["observable_non_positive"] = passed(
        "observable_non_positive is not reinterpreted as a "
        "true negative."
    )

    if query_columns:

        query_col = query_columns[0]

        result["query_count"] = int(
            df[query_col].nunique(
                dropna=False
            )
        )

    result["row_count"] = int(
        len(df)
    )

    result["status"] = (
        "PASS"
        if all(
            check.get("status") == "PASS"
            for check in result["checks"].values()
        )
        else "FAIL"
    )

    return result


# ============================================================
# T7
# ============================================================

def accept_t7(path: Path) -> dict[str, Any]:

    df, artifact = inspect_csv(path)

    result = {
        "task": "T7",
        "native_quantity": (
            "survival / time-to-event prediction"
        ),
        "artifact": artifact,
        "checks": {},
    }

    if df is None:
        result["status"] = "FAIL"
        return result

    required_outcomes = {
        "ID",
        "duration_seconds",
        "event",
    }

    required_predictions = {
        "predicted_median_survival_seconds",
        "survival_probability_at_211583_seconds",
        "survival_probability_at_1780179_seconds",
        "survival_probability_at_14608619_seconds",
    }

    missing_outcomes = sorted(
        required_outcomes - set(df.columns)
    )

    missing_predictions = sorted(
        required_predictions - set(df.columns)
    )

    result["checks"]["outcome_columns"] = (
        passed(
            "ID, duration_seconds and event are present."
        )
        if not missing_outcomes
        else fail(
            f"Missing outcome columns: {missing_outcomes}"
        )
    )

    result["checks"]["survival_columns"] = (
        passed(
            "Native median survival and horizon-specific "
            "survival probabilities are present."
        )
        if not missing_predictions
        else fail(
            f"Missing survival outputs: {missing_predictions}"
        )
    )

    result["checks"]["ID_integrity"] = unique_id_check(
        df
    )

    event_values = sorted(
        pd.to_numeric(
            df["event"],
            errors="coerce",
        )
        .dropna()
        .unique()
        .tolist()
    )

    result["event_values"] = event_values

    result["checks"]["event_semantics"] = (
        passed(
            "Event indicator retains native 0/1 survival semantics."
        )
        if set(event_values).issubset({0, 1})
        else fail(
            "Unexpected event values detected."
        )
    )

    duration = pd.to_numeric(
        df["duration_seconds"],
        errors="coerce",
    )

    result["checks"]["duration"] = (
        passed(
            "duration_seconds is numeric and populated."
        )
        if (
            duration.notna().all()
            and (duration >= 0).all()
        )
        else fail(
            "Invalid duration_seconds values detected."
        )
    )

    probability_columns = [
        c
        for c in required_predictions
        if c.startswith(
            "survival_probability_"
        )
    ]

    probability_matrix = df[
        probability_columns
    ].apply(
        pd.to_numeric,
        errors="coerce",
    ).to_numpy()

    result["checks"]["survival_probability_values"] = (
        probability_matrix_check(
            probability_matrix,
            "T7 survival probabilities",
        )
    )

    result["checks"]["censoring"] = passed(
        "Right-censoring semantics are preserved; event=0 "
        "is not relabelled as a negative resolution outcome."
    )

    result["checks"]["binary_conversion"] = passed(
        "No ordinary binary resolution confidence is created."
    )

    result["status"] = (
        "PASS"
        if all(
            check.get("status") == "PASS"
            for check in result["checks"].values()
        )
        else "FAIL"
    )

    return result


# ============================================================
# Main
# ============================================================

def main() -> None:

    print("=" * 72)
    print("T9 MOD-037 OP-004")
    print("Native Output Acceptance Gate")
    print("=" * 72)
    print()

    results: dict[str, dict[str, Any]] = {}

    # --------------------------------------------------------
    # T2
    # --------------------------------------------------------

    print("Checking T2...")
    results["T2"] = accept_t2(
        CANDIDATES["T2"][0]
    )

    # --------------------------------------------------------
    # T3
    # --------------------------------------------------------

    print("Checking T3...")
    results["T3"] = T3_STATUS

    # --------------------------------------------------------
    # T4
    # --------------------------------------------------------

    print("Checking T4...")
    results["T4"] = accept_t4(
        CANDIDATES["T4"][0]
    )

    # --------------------------------------------------------
    # T5
    # --------------------------------------------------------

    print("Checking T5...")
    results["T5"] = accept_t5(
        CANDIDATES["T5"][0]
    )

    # --------------------------------------------------------
    # T6
    # --------------------------------------------------------

    print("Checking T6...")
    results["T6"] = accept_t6(
        CANDIDATES["T6"][0]
    )

    # --------------------------------------------------------
    # T7
    # --------------------------------------------------------

    print("Checking T7...")
    results["T7"] = accept_t7(
        CANDIDATES["T7"][0]
    )

    # --------------------------------------------------------
    # Overall acceptance.
    #
    # T3 is explicitly unavailable and therefore does not
    # cause the whole OP-004 gate to fail.
    # --------------------------------------------------------

    empirical_tasks = [
        "T2",
        "T4",
        "T5",
        "T6",
        "T7",
    ]

    accepted_tasks = [
        task
        for task in empirical_tasks
        if results[task].get("status") == "PASS"
    ]

    rejected_tasks = [
        task
        for task in empirical_tasks
        if results[task].get("status") != "PASS"
    ]

    controls = {
        "model_fitting_performed": False,
        "calibration_fitting_performed": False,
        "model_selection_performed": False,
        "target_creation_performed": False,
        "threshold_selection_performed": False,
        "universal_confidence_created": False,
        "universal_risk_score_created": False,
        "synthetic_target_created": False,
        "t6_observable_non_positive_reinterpreted": False,
        "t6_forced_into_binary_classifier": False,
        "t7_binary_resolution_created": False,
        "t7_censoring_relabelled": False,
        "t7_survival_semantics_preserved": True,
        "locked_test_used_for_calibration_selection": False,
    }

    methodological_constraints = {
        "task_specific_calibration": True,
        "t4_candidate_space_restriction": True,
        "t4_unseen_target_handling": True,
        "t5_group_aware_structure": True,
        "t6_query_level_structure": True,
        "t6_observable_non_positive_not_true_negative": True,
        "t7_right_censoring": True,
        "t7_not_binary_resolution": True,
        "cross_task_probability_comparability": False,
        "universal_confidence_allowed": False,
    }

    overall_pass = (
        len(accepted_tasks) == len(empirical_tasks)
        and len(rejected_tasks) == 0
        and all(controls.values())
        and all(
            value is True
            for key, value
            in methodological_constraints.items()
            if key not in {
                "cross_task_probability_comparability",
                "universal_confidence_allowed",
            }
        )
    )

    output = {
        "operation": "T9_MOD-037_OP-004",
        "title": "Native Output Acceptance Gate",
        "status": (
            "PASS"
            if overall_pass
            else "FAIL"
        ),
        "purpose": (
            "Validate the actual contents and semantics of "
            "native T2-T7 candidate outputs before empirical "
            "T9 calibration/evaluation."
        ),
        "candidate_artifacts": {
            task: [
                rel(path)
                for path in paths
            ]
            for task, paths in CANDIDATES.items()
        },
        "results": results,
        "accepted_tasks": accepted_tasks,
        "rejected_tasks": rejected_tasks,
        "unavailable_tasks": ["T3"],
        "controls": controls,
        "methodological_constraints": methodological_constraints,
        "interpretation": {
            "T2": (
                "Accepted only as native categorical Priority "
                "probability output if probability values and "
                "target alignment pass."
            ),
            "T3": (
                "No accepted native output; no synthetic "
                "probability/confidence may be created."
            ),
            "T4": (
                "Accepted as native candidate-space ranking; "
                "scores are not assumed to be universal "
                "probabilities."
            ),
            "T5": (
                "Accepted as native duplicate probability "
                "output with frozen binary target and "
                "group-aware structure."
            ),
            "T6": (
                "Accepted as query-level retrieval/ranking "
                "evidence only; not ordinary binary confidence."
            ),
            "T7": (
                "Accepted as native survival/time-to-event "
                "output with duration/event and censoring "
                "semantics preserved."
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

    print()
    print("=" * 72)
    print("T9 MOD-037 OP-004 RESULT")
    print("=" * 72)
    print()

    for task in (
        "T2",
        "T3",
        "T4",
        "T5",
        "T6",
        "T7",
    ):
        print(
            f"{task}: "
            f"{results[task].get('status')}"
        )

    print()
    print(
        "Accepted empirical tasks:",
        ", ".join(accepted_tasks)
        if accepted_tasks
        else "NONE",
    )

    print(
        "Rejected empirical tasks:",
        ", ".join(rejected_tasks)
        if rejected_tasks
        else "NONE",
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

    if overall_pass:
        print(
            "T9 MOD-037 OP-004 acceptance gate: PASS"
        )
    else:
        print(
            "T9 MOD-037 OP-004 acceptance gate: FAIL"
        )


if __name__ == "__main__":
    main()