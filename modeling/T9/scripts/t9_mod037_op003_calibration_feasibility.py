from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


# ============================================================
# T9 MOD-037 OP-003
# Calibration / Evaluation Population Feasibility
#
# Purpose:
#   Determine whether existing native T2-T7 model outputs have
#   an admissible evaluation population and outcome structure
#   for later task-specific T9 calibration/evaluation.
#
# This operation DOES NOT:
#   - fit calibration
#   - fit a model
#   - select a model
#   - create targets
#   - create thresholds
#   - create universal confidence/risk scores
#   - alter T6 observable_non_positive semantics
#   - convert T7 survival into binary classification
# ============================================================


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

MODELING_ROOT = PROJECT_ROOT / "modeling"

OUTPUT_DIR = MODELING_ROOT / "T9" / "mod037"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_JSON = OUTPUT_DIR / (
    "t9_mod037_op003_calibration_feasibility.json"
)


# ------------------------------------------------------------
# Candidate native artifacts
#
# These are evidence candidates only.
# OP-003 does not assume that any candidate is valid until
# schema and population checks pass.
# ------------------------------------------------------------

CANDIDATES = {
    "T2": [
        MODELING_ROOT
        / "T2"
        / "analysis"
        / "t2_baseline_validation_predictions.csv",

        MODELING_ROOT
        / "T2"
        / "analysis"
        / "t2_final_test_predictions.csv",
    ],

    "T3": [
        # T3 prediction artifacts are discovered dynamically
        # below because the authoritative directory does not
        # expose one single predetermined prediction filename.
    ],

    "T4": [
        MODELING_ROOT
        / "T4"
        / "results"
        / "mod011_checkpoints"
        / "t4_mod011_retrieval.npz",

        MODELING_ROOT
        / "T4"
        / "results"
        / "mod007_checkpoints"
        / "t4_mod007_full_retrieval.npz",

        MODELING_ROOT
        / "T4"
        / "results"
        / "r1_checkpoints"
        / "t4_r1_topk_predictions.npz",
    ],

    "T5": [
        MODELING_ROOT
        / "T5"
        / "metrics"
        / "t5_mod005_validation_predictions.npz",

        MODELING_ROOT
        / "T5"
        / "metrics"
        / "t5_mod007_calibrated_validation_predictions.npz",

        MODELING_ROOT
        / "T5"
        / "metrics"
        / "t5_mod009_locked_evaluation_predictions.npz",
    ],

    "T6": [
        MODELING_ROOT
        / "T6"
        / "metrics"
        / "t6_mod004_query_rankings.csv",

        MODELING_ROOT
        / "T6"
        / "metrics"
        / "t6_mod007_bm25_query_rankings.csv",

        MODELING_ROOT
        / "T6"
        / "metrics"
        / "t6_mod008_semantic_failure_rankings.csv",

        MODELING_ROOT
        / "T6"
        / "metrics"
        / "t6_mod009_hybrid_query_rankings.csv",

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

        MODELING_ROOT
        / "T7"
        / "derived"
        / "t7_mod010_evaluation_predictions.csv",
    ],
}


# ------------------------------------------------------------
# Known authoritative population sizes from the DTM.
#
# These are expected values. OP-003 verifies actual artifacts
# against them where the relevant population is directly
# observable.
# ------------------------------------------------------------

EXPECTED_POPULATIONS = {
    "T2": 29498,
    "T3": 30839,
    "T4": 178127,
    "T5": 513816,
    "T6": 274922,
    "T7": 513816,
}


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def exists(path: Path) -> bool:
    return path.exists() and path.is_file()


def inspect_csv(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": rel(path),
        "format": "csv",
        "exists": exists(path),
        "status": "NOT_FOUND",
    }

    if not exists(path):
        return result

    try:
        df = pd.read_csv(path)

        result["status"] = "PASS"
        result["rows"] = int(len(df))
        result["columns"] = [
            str(c) for c in df.columns
        ]
        result["column_count"] = len(df.columns)

        if "ID" in df.columns:
            result["unique_IDs"] = int(
                df["ID"].nunique(dropna=False)
            )
            result["duplicate_IDs"] = int(
                df["ID"].duplicated().sum()
            )

        return result

    except Exception as exc:
        result["status"] = "ERROR"
        result["error"] = repr(exc)
        return result


def inspect_npz(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": rel(path),
        "format": "npz",
        "exists": exists(path),
        "status": "NOT_FOUND",
    }

    if not exists(path):
        return result

    try:
        with np.load(path, allow_pickle=False) as data:
            result["status"] = "PASS"
            result["keys"] = list(data.files)

            summaries = {}

            for key in data.files:
                arr = np.asarray(data[key])

                summaries[key] = {
                    "shape": list(arr.shape),
                    "dtype": str(arr.dtype),
                    "size": int(arr.size),
                }

            result["key_summaries"] = summaries

        return result

    except Exception as exc:
        result["status"] = "ERROR"
        result["error"] = repr(exc)
        return result


def inspect(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".csv":
        return inspect_csv(path)

    if path.suffix.lower() == ".npz":
        return inspect_npz(path)

    return {
        "path": rel(path),
        "status": "UNSUPPORTED",
    }


def discover_t3_candidates() -> list[Path]:
    root = MODELING_ROOT / "T3"

    if not root.exists():
        return []

    candidates = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in {
            ".csv",
            ".npz",
        }:
            continue

        lower = path.name.lower()

        if any(
            token in lower
            for token in (
                "prediction",
                "predictions",
                "prob",
                "output",
                "oof",
            )
        ):
            candidates.append(path)

    return sorted(
        candidates,
        key=lambda p: str(p),
    )


def csv_columns(path: Path) -> list[str]:
    try:
        return [
            str(c)
            for c in pd.read_csv(
                path,
                nrows=0,
            ).columns
        ]
    except Exception:
        return []


def load_csv_columns(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


# ------------------------------------------------------------
# T2 feasibility
# ------------------------------------------------------------

def evaluate_t2(
    artifacts: list[dict[str, Any]]
) -> dict[str, Any]:

    result = {
        "task": "T2",
        "target": "target_priority",
        "native_quantity": (
            "categorical Priority prediction / "
            "class probability where actually present"
        ),
        "candidates": artifacts,
        "feasible_candidate_count": 0,
        "locked_test_candidates": 0,
        "development_candidates": 0,
    }

    for artifact in artifacts:

        if artifact.get("status") != "PASS":
            continue

        path = PROJECT_ROOT / artifact["path"]

        if path.suffix.lower() != ".csv":
            continue

        df = pd.read_csv(path)

        columns = set(df.columns)

        has_target = "target_priority" in columns

        probability_columns = [
            c
            for c in df.columns
            if str(c).lower().startswith(
                "t2_probability_"
            )
            or "probability" in str(c).lower()
        ]

        prediction_columns = [
            c
            for c in df.columns
            if "prediction" in str(c).lower()
            or "predicted" in str(c).lower()
        ]

        artifact["has_target_priority"] = has_target
        artifact["probability_columns"] = [
            str(c)
            for c in probability_columns
        ]
        artifact["prediction_columns"] = [
            str(c)
            for c in prediction_columns
        ]

        is_test = "final_test_predictions" in path.name.lower()

        artifact["locked_test_candidate"] = is_test

        if (
            has_target
            and (
                probability_columns
                or prediction_columns
            )
        ):
            result["feasible_candidate_count"] += 1

            if is_test:
                result["locked_test_candidates"] += 1
            else:
                result["development_candidates"] += 1

    result["development_population_available"] = (
        result["development_candidates"] > 0
    )

    result["locked_test_present"] = (
        result["locked_test_candidates"] > 0
    )

    result["status"] = (
        "FEASIBLE_CANDIDATE_PRESENT"
        if result["feasible_candidate_count"] > 0
        else "NO_FEASIBLE_CANDIDATE_IDENTIFIED"
    )

    return result


# ------------------------------------------------------------
# T3 feasibility
# ------------------------------------------------------------

def evaluate_t3(
    artifacts: list[dict[str, Any]]
) -> dict[str, Any]:

    result = {
        "task": "T3",
        "target": "severity",
        "native_quantity": (
            "categorical operational Severity prediction "
            "and task-specific probability/confidence"
        ),
        "candidates": artifacts,
        "feasible_candidate_count": 0,
    }

    for artifact in artifacts:

        if artifact.get("status") != "PASS":
            continue

        path = PROJECT_ROOT / artifact["path"]

        if path.suffix.lower() == ".csv":
            columns = set(
                csv_columns(path)
            )

            target_candidates = [
                c
                for c in columns
                if (
                    "severity" in c.lower()
                    and (
                        "target" in c.lower()
                        or "label" in c.lower()
                    )
                )
            ]

            prediction_candidates = [
                c
                for c in columns
                if (
                    "prediction" in c.lower()
                    or "predicted" in c.lower()
                    or "probability" in c.lower()
                    or "prob_" in c.lower()
                )
            ]

            artifact[
                "severity_target_like_columns"
            ] = sorted(target_candidates)

            artifact[
                "prediction_probability_like_columns"
            ] = sorted(prediction_candidates)

            if (
                target_candidates
                and prediction_candidates
            ):
                result["feasible_candidate_count"] += 1

    result["status"] = (
        "FEASIBLE_CANDIDATE_PRESENT"
        if result["feasible_candidate_count"] > 0
        else "NO_FEASIBLE_CANDIDATE_IDENTIFIED"
    )

    return result


# ------------------------------------------------------------
# T4 feasibility
# ------------------------------------------------------------

def evaluate_t4(
    artifacts: list[dict[str, Any]]
) -> dict[str, Any]:

    result = {
        "task": "T4",
        "target": "target_assignee",
        "native_quantity": (
            "candidate-space assignee retrieval/ranking"
        ),
        "candidates": artifacts,
        "retrieval_candidates": 0,
        "score_keys": [],
        "target_population_verified": False,
    }

    for artifact in artifacts:

        if artifact.get("status") != "PASS":
            continue

        keys = set(
            artifact.get("keys", [])
        )

        if (
            "neighbor_indices" in keys
            and "neighbor_scores" in keys
        ):
            result["retrieval_candidates"] += 1
            result["score_keys"].append({
                "path": artifact["path"],
                "score_key": "neighbor_scores",
                "index_key": "neighbor_indices",
            })

    eval_path = (
        MODELING_ROOT
        / "T4"
        / "derived"
        / "t4_eval.csv"
    )

    if eval_path.exists():

        df = pd.read_csv(
            eval_path,
            usecols=lambda c: c in {
                "ID",
                "target_assignee",
            },
        )

        if "target_assignee" in df.columns:
            result["target_population_verified"] = True
            result["evaluation_rows"] = int(len(df))
            result["evaluation_unique_IDs"] = int(
                df["ID"].nunique()
            )

            result["target_assignee_non_null"] = int(
                df["target_assignee"].notna().sum()
            )

    result["candidate_space_restriction_required"] = True
    result["unseen_target_handling_required"] = True

    result["status"] = (
        "FEASIBLE_NATIVE_RANKING_PRESENT"
        if (
            result["retrieval_candidates"] > 0
            and result["target_population_verified"]
        )
        else "FEASIBILITY_INCOMPLETE"
    )

    return result


# ------------------------------------------------------------
# T5 feasibility
# ------------------------------------------------------------

def evaluate_t5(
    artifacts: list[dict[str, Any]]
) -> dict[str, Any]:

    result = {
        "task": "T5",
        "target": "T5 target",
        "native_quantity": (
            "duplicate probability / binary probability"
        ),
        "candidates": artifacts,
        "probability_candidates": [],
    }

    for artifact in artifacts:

        if artifact.get("status") != "PASS":
            continue

        keys = set(
            artifact.get("keys", [])
        )

        probability_keys = [
            key
            for key in (
                "p_base",
                "p_sigmoid",
                "p_isotonic",
            )
            if key in keys
        ]

        if probability_keys:

            result["probability_candidates"].append({
                "path": artifact["path"],
                "probability_keys": probability_keys,
                "keys": artifact.get(
                    "keys",
                    [],
                ),
            })

    result["native_probability_available"] = (
        len(result["probability_candidates"]) > 0
    )

    result["group_aware_evaluation_required"] = True

    result["status"] = (
        "FEASIBLE_NATIVE_PROBABILITY_PRESENT"
        if result["native_probability_available"]
        else "NO_FEASIBLE_NATIVE_PROBABILITY_IDENTIFIED"
    )

    return result


# ------------------------------------------------------------
# T6 feasibility
# ------------------------------------------------------------

def evaluate_t6(
    artifacts: list[dict[str, Any]]
) -> dict[str, Any]:

    result = {
        "task": "T6",
        "native_quantity": (
            "query-level candidate retrieval/ranking"
        ),
        "candidates": artifacts,
        "ranking_candidates": 0,
        "query_like_columns": [],
        "candidate_like_columns": [],
        "score_like_columns": [],
        "observable_non_positive_preserved": True,
        "ordinary_binary_calibration_allowed": False,
    }

    for artifact in artifacts:

        if artifact.get("status") != "PASS":
            continue

        path = PROJECT_ROOT / artifact["path"]

        if path.suffix.lower() != ".csv":
            continue

        columns = csv_columns(path)

        query_cols = [
            c
            for c in columns
            if "query" in c.lower()
        ]

        candidate_cols = [
            c
            for c in columns
            if (
                "candidate" in c.lower()
                or "bug" in c.lower()
                or "document" in c.lower()
            )
        ]

        score_cols = [
            c
            for c in columns
            if (
                "score" in c.lower()
                or "similarity" in c.lower()
                or "rank" in c.lower()
            )
        ]

        artifact["query_like_columns"] = query_cols
        artifact["candidate_like_columns"] = candidate_cols
        artifact["score_like_columns"] = score_cols

        if query_cols and score_cols:
            result["ranking_candidates"] += 1

        result["query_like_columns"].extend(
            query_cols
        )
        result["candidate_like_columns"].extend(
            candidate_cols
        )
        result["score_like_columns"].extend(
            score_cols
        )

    result["query_like_columns"] = sorted(
        set(result["query_like_columns"])
    )

    result["candidate_like_columns"] = sorted(
        set(result["candidate_like_columns"])
    )

    result["score_like_columns"] = sorted(
        set(result["score_like_columns"])
    )

    result["status"] = (
        "FEASIBLE_NATIVE_RANKING_PRESENT"
        if result["ranking_candidates"] > 0
        else "NO_FEASIBLE_RANKING_IDENTIFIED"
    )

    return result


# ------------------------------------------------------------
# T7 feasibility
# ------------------------------------------------------------

def evaluate_t7(
    artifacts: list[dict[str, Any]]
) -> dict[str, Any]:

    result = {
        "task": "T7",
        "outcomes": [
            "duration_seconds",
            "event",
        ],
        "native_quantity": (
            "survival / time-to-event prediction"
        ),
        "candidates": artifacts,
        "survival_candidates": 0,
        "censoring_preserved": True,
        "binary_resolution_conversion": False,
    }

    for artifact in artifacts:

        if artifact.get("status") != "PASS":
            continue

        path = PROJECT_ROOT / artifact["path"]

        if path.suffix.lower() != ".csv":
            continue

        columns = set(
            csv_columns(path)
        )

        required_outcomes = {
            "duration_seconds",
            "event",
        }

        survival_prediction_columns = {
            "predicted_median_survival_seconds",
            "survival_probability_at_211583_seconds",
            "survival_probability_at_1780179_seconds",
            "survival_probability_at_14608619_seconds",
        }

        has_outcomes = required_outcomes.issubset(
            columns
        )

        has_survival_outputs = bool(
            survival_prediction_columns.intersection(
                columns
            )
        )

        artifact["has_survival_outcomes"] = has_outcomes
        artifact["has_survival_prediction"] = (
            has_survival_outputs
        )

        if has_outcomes and has_survival_outputs:
            result["survival_candidates"] += 1

    result["status"] = (
        "FEASIBLE_NATIVE_SURVIVAL_PRESENT"
        if result["survival_candidates"] > 0
        else "NO_FEASIBLE_SURVIVAL_OUTPUT_IDENTIFIED"
    )

    return result


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main() -> None:

    print("=" * 72)
    print("T9 MOD-037 OP-003")
    print("Calibration / Evaluation Population Feasibility")
    print("=" * 72)

    print()
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Output:       {OUTPUT_JSON}")
    print()

    # --------------------------------------------------------
    # Discover T3 candidates.
    # --------------------------------------------------------

    candidates = {
        task: list(paths)
        for task, paths in CANDIDATES.items()
    }

    candidates["T3"] = discover_t3_candidates()

    # --------------------------------------------------------
    # Inspect candidate artifacts.
    # --------------------------------------------------------

    inspected = {}

    for task, paths in candidates.items():

        inspected[task] = []

        print(f"--- {task} ---")

        for path in paths:

            print(
                f"Inspecting: {rel(path)}"
            )

            result = inspect(path)

            inspected[task].append(result)

        if not paths:
            print("No candidate artifact paths discovered.")

        print()

    # --------------------------------------------------------
    # Task-specific feasibility.
    # --------------------------------------------------------

    feasibility = {}

    feasibility["T2"] = evaluate_t2(
        inspected["T2"]
    )

    feasibility["T3"] = evaluate_t3(
        inspected["T3"]
    )

    feasibility["T4"] = evaluate_t4(
        inspected["T4"]
    )

    feasibility["T5"] = evaluate_t5(
        inspected["T5"]
    )

    feasibility["T6"] = evaluate_t6(
        inspected["T6"]
    )

    feasibility["T7"] = evaluate_t7(
        inspected["T7"]
    )

    # --------------------------------------------------------
    # Expected population checks.
    #
    # These are informational and do not automatically make
    # a candidate calibration-ready.
    # --------------------------------------------------------

    population_checks = {}

    for task, expected in EXPECTED_POPULATIONS.items():

        task_checks = []

        for artifact in inspected.get(task, []):

            if artifact.get("status") != "PASS":
                continue

            rows = artifact.get("rows")

            if rows is None:
                continue

            task_checks.append({
                "path": artifact["path"],
                "rows": rows,
                "expected_authoritative_population": expected,
                "matches_expected_population": (
                    rows == expected
                ),
            })

        population_checks[task] = task_checks

    # --------------------------------------------------------
    # Global controls.
    # --------------------------------------------------------

    controls = {
        "model_fitting_performed": False,
        "calibration_fitting_performed": False,
        "target_creation_performed": False,
        "model_selection_performed": False,
        "threshold_selection_performed": False,
        "universal_confidence_created": False,
        "universal_risk_score_created": False,
        "synthetic_target_created": False,
        "t6_observable_non_positive_reinterpreted": False,
        "t6_forced_into_ordinary_binary_calibration": False,
        "t7_binary_resolution_created": False,
        "t7_censoring_relabelled": False,
        "t7_survival_semantics_preserved": True,
        "locked_test_selected_for_calibration": False,
    }

    # --------------------------------------------------------
    # DTM-required methodological constraints.
    # --------------------------------------------------------

    methodological_constraints = {
        "task_specific_calibration_required": True,
        "t4_candidate_space_restriction_required": True,
        "t4_unseen_target_handling_required": True,
        "t5_group_aware_structure_required": True,
        "t6_query_level_semantics_required": True,
        "t6_observable_non_positive_is_not_true_negative": True,
        "t7_right_censoring_preserved": True,
        "t7_not_ordinary_binary_classification": True,
        "cross_task_probability_comparability_assumed": False,
        "universal_confidence_score_allowed": False,
    }

    # --------------------------------------------------------
    # Overall status.
    #
    # OP-003 is an inventory/feasibility operation.
    # It PASSes if it successfully evaluates the task-specific
    # feasibility boundary. It does NOT require every task to
    # have a feasible calibration artifact.
    # --------------------------------------------------------

    task_statuses = {
        task: value.get("status")
        for task, value in feasibility.items()
    }

    output = {
        "operation": "T9_MOD-037_OP-003",
        "title": (
            "Calibration / Evaluation Population Feasibility"
        ),
        "status": "PASS",
        "purpose": (
            "Determine whether existing native T2-T7 outputs "
            "have admissible evaluation populations and "
            "outcome structures for later task-specific "
            "T9 calibration/evaluation."
        ),
        "project_root": str(PROJECT_ROOT),
        "expected_authoritative_populations": (
            EXPECTED_POPULATIONS
        ),
        "candidate_paths": {
            task: [
                rel(path)
                for path in paths
            ]
            for task, paths in candidates.items()
        },
        "inspected_artifacts": inspected,
        "population_checks": population_checks,
        "task_feasibility": feasibility,
        "task_statuses": task_statuses,
        "methodological_constraints": (
            methodological_constraints
        ),
        "controls": controls,
        "interpretation": {
            "t2": (
                "Priority probability/confidence can only be "
                "evaluated where a valid prediction-output and "
                "target linkage is established."
            ),
            "t3": (
                "Severity calibration requires an actual native "
                "prediction/probability artifact aligned to the "
                "frozen severity outcome."
            ),
            "t4": (
                "Assignment confidence must remain restricted "
                "to the explicitly observed candidate output "
                "space; unseen targets are not treated as "
                "ordinary negative predictions."
            ),
            "t5": (
                "Duplicate probability may be evaluated using "
                "the frozen binary target with the established "
                "group-aware structure."
            ),
            "t6": (
                "Retrieval confidence must retain query-level "
                "ranking semantics; observable_non_positive is "
                "not a true negative."
            ),
            "t7": (
                "Resolution confidence must retain survival/"
                "time-to-event semantics and right censoring."
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
    # Console summary.
    # --------------------------------------------------------

    print("=" * 72)
    print("T9 MOD-037 OP-003 RESULT")
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
            f"{task_statuses.get(task)}"
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
        "T9 MOD-037 OP-003 feasibility audit: PASS"
    )


if __name__ == "__main__":
    main()