from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# ============================================================
# T9 MOD-037 OP-005
# Accepted Native Output Population & Semantics Lock
#
# Purpose:
#   Formally freeze the empirical T9 output boundary established
#   by OP-003, OP-004 and OP-004A.
#
# This operation DOES NOT:
#   - fit a model
#   - fit calibration
#   - generate probabilities
#   - create targets
#   - select models
#   - select thresholds
#   - create a universal confidence/risk score
#
# It only records what T9 is empirically permitted to evaluate
# and the native semantics that must be preserved.
# ============================================================


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

MODELING_ROOT = PROJECT_ROOT / "modeling"

T9_ROOT = MODELING_ROOT / "T9"
OUTPUT_DIR = T9_ROOT / "mod037"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_JSON = (
    OUTPUT_DIR
    / "t9_mod037_op005_output_semantics_lock.json"
)


# ------------------------------------------------------------
# Existing evidence artifacts
# ------------------------------------------------------------

OP003_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op003_calibration_feasibility.json"
)

OP004_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op004_native_output_acceptance.json"
)

OP004A_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op004a_t2_probability_resolution.json"
)


# ------------------------------------------------------------
# Frozen native output boundary
# ------------------------------------------------------------

TASK_BOUNDARY: dict[str, dict[str, Any]] = {

    "T2": {
        "status": "UNAVAILABLE_FOR_PROBABILITY_CALIBRATION",

        "native_quantity": (
            "Hard-label categorical Priority prediction"
        ),

        "native_probability_output": False,

        "accepted_for_calibration": False,

        "reason": (
            "Existing T2 prediction artifacts contain hard "
            "predictions but no native T2_probability_P1 through "
            "T2_probability_P5 probability artifact was found "
            "within the T2 evidence boundary."
        ),

        "allowed_use": [
            "Document native hard predictions",
            "Retain as task evidence",
        ],

        "prohibited_use": [
            "Invent probability values",
            "Generate probability values under this operation",
            "Perform probability calibration without a native "
            "probability output",
        ],
    },


    "T3": {
        "status": "UNAVAILABLE",

        "native_quantity": (
            "Operational Severity prediction"
        ),

        "native_probability_output": False,

        "accepted_for_calibration": False,

        "reason": (
            "OP-003 identified no native prediction/probability "
            "artifact suitable for the T9 acceptance boundary."
        ),

        "allowed_use": [
            "Document the absence of an accepted native output",
        ],

        "prohibited_use": [
            "Create synthetic predictions",
            "Create synthetic probabilities",
            "Infer confidence from evaluation metrics alone",
        ],
    },


    "T4": {
        "status": "ACCEPTED_NATIVE_RANKING",

        "native_quantity": (
            "Candidate-space assignee retrieval/ranking"
        ),

        "native_probability_output": False,

        "accepted_for_calibration": False,

        "accepted_for_native_evaluation": True,

        "artifact": (
            "modeling/T4/results/mod011_checkpoints/"
            "t4_mod011_retrieval.npz"
        ),

        "native_outputs": [
            "neighbor_indices",
            "neighbor_scores",
        ],

        "population": (
            "T4 native retrieval evaluation population"
        ),

        "semantic_restrictions": [
            (
                "Scores remain native candidate-space ranking "
                "quantities."
            ),
            (
                "Scores must not be interpreted as universally "
                "calibrated ticket-level probabilities."
            ),
            (
                "Candidate-space restriction must be preserved."
            ),
            (
                "Unseen assignee targets remain unavailable "
                "rather than being treated as ordinary negatives."
            ),
        ],

        "calibration_boundary": (
            "Any later confidence/calibration formulation must "
            "be defined specifically for the T4 ranking/candidate "
            "space and must not invent a universal probability."
        ),
    },


    "T5": {
        "status": "ACCEPTED_NATIVE_PROBABILITY",

        "native_quantity": (
            "Duplicate probability"
        ),

        "native_probability_output": True,

        "accepted_for_calibration": True,

        "artifact": (
            "modeling/T5/metrics/"
            "t5_mod007_calibrated_validation_predictions.npz"
        ),

        "native_outputs": [
            "y_true",
            "p_base",
            "p_sigmoid",
            "p_isotonic",
        ],

        "target": (
            "T5 target"
        ),

        "population": (
            "T5 model validation population"
        ),

        "semantic_restrictions": [
            (
                "Native binary duplicate target must remain "
                "unchanged."
            ),
            (
                "Group-aware structure must be preserved."
            ),
            (
                "Probability output must remain a duplicate "
                "probability, not a universal ticket-risk score."
            ),
            (
                "Locked evaluation data must not be used for "
                "calibration fitting or model selection."
            ),
        ],

        "calibration_boundary": (
            "Task-specific duplicate-probability calibration "
            "may proceed using the accepted native development/"
            "validation output under the established T5 structure."
        ),
    },


    "T6": {
        "status": "ACCEPTED_NATIVE_RANKING",

        "native_quantity": (
            "Query-level candidate retrieval/ranking"
        ),

        "native_probability_output": False,

        "accepted_for_calibration": False,

        "accepted_for_native_evaluation": True,

        "artifact": (
            "modeling/T6/metrics/"
            "t6_mod010_corrected_hybrid_query_rankings.csv"
        ),

        "native_outputs": [
            "query-level ranking",
            "candidate-level score/ranking information",
        ],

        "semantic_restrictions": [
            (
                "T6 remains a query-level retrieval/ranking task."
            ),
            (
                "observable_non_positive is not a true negative."
            ),
            (
                "T6 must not be flattened into an ordinary "
                "binary classifier."
            ),
            (
                "Any confidence/relevance formulation must retain "
                "native retrieval semantics."
            ),
        ],

        "calibration_boundary": (
            "Any later T6 confidence formulation must be "
            "defined around native query-level retrieval/ranking "
            "semantics rather than ordinary binary probability "
            "calibration."
        ),
    },


    "T7": {
        "status": "ACCEPTED_NATIVE_SURVIVAL",

        "native_quantity": (
            "Survival / time-to-event prediction"
        ),

        "native_probability_output": True,

        "accepted_for_calibration": True,

        "artifact": (
            "modeling/T7/derived/"
            "t7_mod007_evaluation_predictions.csv"
        ),

        "native_outputs": [
            "predicted_median_survival_seconds",
            "survival_probability_at_211583_seconds",
            "survival_probability_at_1780179_seconds",
            "survival_probability_at_14608619_seconds",
        ],

        "outcomes": [
            "duration_seconds",
            "event",
        ],

        "semantic_restrictions": [
            (
                "T7 remains a survival/time-to-event task."
            ),
            (
                "Right-censoring must be preserved."
            ),
            (
                "event=0 must not be relabelled as a negative "
                "resolution outcome."
            ),
            (
                "T7 must not be converted into ordinary binary "
                "resolved/not-resolved confidence."
            ),
            (
                "Calibration must be defined for an appropriate "
                "survival/time-to-event predictive quantity."
            ),
        ],

        "calibration_boundary": (
            "Later T7 calibration must retain survival semantics "
            "and right censoring."
        ),
    },
}


# ------------------------------------------------------------
# Global restrictions
# ------------------------------------------------------------

GLOBAL_RESTRICTIONS = {

    "task_specific_calibration_only": True,

    "universal_confidence_score": False,

    "universal_risk_score": False,

    "cross_task_probability_comparability": False,

    "synthetic_target_creation": False,

    "synthetic_probability_creation": False,

    "blind_probability_averaging": False,

    "arbitrary_cross_task_weights": False,

    "post_creation_features_allowed": False,

    "t6_observable_non_positive_as_true_negative": False,

    "t7_binary_resolution_conversion": False,

    "t7_censoring_relabelling": False,

    "locked_test_for_calibration_selection": False,

}


# ------------------------------------------------------------
# Load previous operation records
# ------------------------------------------------------------

def load_json(
    path: Path,
) -> dict[str, Any]:

    if not path.exists():
        raise FileNotFoundError(
            f"Required evidence artifact missing: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


# ------------------------------------------------------------
# Evidence consistency checks
# ------------------------------------------------------------

def validate_previous_operations() -> dict[str, Any]:

    op003 = load_json(
        OP003_ARTIFACT
    )

    op004 = load_json(
        OP004_ARTIFACT
    )

    op004a = load_json(
        OP004A_ARTIFACT
    )

    checks: dict[str, Any] = {}

    # --------------------------------------------------------
    # OP-003
    # --------------------------------------------------------

    checks["op003_status"] = {
        "status": (
            "PASS"
            if op003.get("status") == "PASS"
            else "FAIL"
        ),
        "observed": op003.get("status"),
    }

    feasibility = op003.get(
        "task_feasibility",
        {},
    )

    expected_op003_statuses = {
        "T2": "FEASIBLE_CANDIDATE_PRESENT",
        "T3": "NO_FEASIBLE_CANDIDATE_IDENTIFIED",
        "T4": "FEASIBLE_NATIVE_RANKING_PRESENT",
        "T5": "FEASIBLE_NATIVE_PROBABILITY_PRESENT",
        "T6": "FEASIBLE_NATIVE_RANKING_PRESENT",
        "T7": "FEASIBLE_NATIVE_SURVIVAL_PRESENT",
    }

    checks["op003_task_feasibility"] = {}

    for task, expected in (
        expected_op003_statuses.items()
    ):

        observed = feasibility.get(
            task,
            {},
        ).get("status")

        checks["op003_task_feasibility"][task] = {
            "status": (
                "PASS"
                if observed == expected
                else "FAIL"
            ),
            "expected": expected,
            "observed": observed,
        }

    # --------------------------------------------------------
    # OP-004
    # --------------------------------------------------------

    checks["op004_status"] = {
        "status": (
            "PASS"
            if op004.get("status") == "FAIL"
            else "FAIL"
        ),
        "observed": op004.get("status"),
        "reason": (
            "OP-004 correctly rejected the initially selected "
            "T2 hard-label artifact."
        ),
    }

    op004_results = op004.get(
        "results",
        {},
    )

    expected_op004_statuses = {
        "T2": "FAIL",
        "T3": "NO_ACCEPTED_NATIVE_OUTPUT",
        "T4": "PASS",
        "T5": "PASS",
        "T6": "PASS",
        "T7": "PASS",
    }

    checks["op004_task_results"] = {}

    for task, expected in (
        expected_op004_statuses.items()
    ):

        observed = op004_results.get(
            task,
            {},
        ).get("status")

        checks["op004_task_results"][task] = {
            "status": (
                "PASS"
                if observed == expected
                else "FAIL"
            ),
            "expected": expected,
            "observed": observed,
        }

    # --------------------------------------------------------
    # OP-004A
    # --------------------------------------------------------

    checks["op004a_status"] = {
        "status": (
            "PASS"
            if op004a.get("status") == "PASS"
            else "FAIL"
        ),
        "observed": op004a.get("status"),
    }

    checks["op004a_exact_probability_candidates"] = {
        "status": (
            "PASS"
            if op004a.get(
                "exact_probability_candidate_count"
            ) == 0
            else "FAIL"
        ),
        "expected": 0,
        "observed": op004a.get(
            "exact_probability_candidate_count"
        ),
    }

    checks["op004a_accepted_probability_artifacts"] = {
        "status": (
            "PASS"
            if len(
                op004a.get(
                    "accepted_native_probability_artifacts",
                    [],
                )
            ) == 0
            else "FAIL"
        ),
        "expected": 0,
        "observed": len(
            op004a.get(
                "accepted_native_probability_artifacts",
                [],
            )
        ),
    }

    # --------------------------------------------------------
    # Overall previous-operation consistency
    # --------------------------------------------------------

    failed = []

    def collect_failures(
        value: Any,
        prefix: str = "",
    ) -> None:

        if isinstance(value, dict):

            if value.get("status") == "FAIL":
                failed.append(
                    prefix or "unknown"
                )

            for key, child in value.items():

                if key == "status":
                    continue

                collect_failures(
                    child,
                    (
                        f"{prefix}.{key}"
                        if prefix
                        else key
                    ),
                )

    collect_failures(
        checks
    )

    return {
        "checks": checks,
        "failed_check_paths": failed,
        "status": (
            "PASS"
            if not failed
            else "FAIL"
        ),
    }


# ------------------------------------------------------------
# Semantic boundary validation
# ------------------------------------------------------------

def validate_boundary() -> dict[str, Any]:

    required_tasks = {
        "T2",
        "T3",
        "T4",
        "T5",
        "T6",
        "T7",
    }

    observed_tasks = set(
        TASK_BOUNDARY.keys()
    )

    checks = {}

    checks["task_set"] = {
        "status": (
            "PASS"
            if observed_tasks == required_tasks
            else "FAIL"
        ),
        "expected": sorted(
            required_tasks
        ),
        "observed": sorted(
            observed_tasks
        ),
    }

    expected_statuses = {
        "T2": "UNAVAILABLE_FOR_PROBABILITY_CALIBRATION",
        "T3": "UNAVAILABLE",
        "T4": "ACCEPTED_NATIVE_RANKING",
        "T5": "ACCEPTED_NATIVE_PROBABILITY",
        "T6": "ACCEPTED_NATIVE_RANKING",
        "T7": "ACCEPTED_NATIVE_SURVIVAL",
    }

    checks["task_statuses"] = {}

    for task, expected in (
        expected_statuses.items()
    ):

        observed = TASK_BOUNDARY[
            task
        ]["status"]

        checks["task_statuses"][task] = {
            "status": (
                "PASS"
                if observed == expected
                else "FAIL"
            ),
            "expected": expected,
            "observed": observed,
        }

    # --------------------------------------------------------
    # Specific T2 restriction
    # --------------------------------------------------------

    checks["T2_probability_unavailable"] = {
        "status": (
            "PASS"
            if (
                TASK_BOUNDARY["T2"][
                    "native_probability_output"
                ]
                is False
                and
                TASK_BOUNDARY["T2"][
                    "accepted_for_calibration"
                ]
                is False
            )
            else "FAIL"
        ),
    }

    # --------------------------------------------------------
    # Specific T3 restriction
    # --------------------------------------------------------

    checks["T3_unavailable"] = {
        "status": (
            "PASS"
            if (
                TASK_BOUNDARY["T3"][
                    "accepted_for_calibration"
                ]
                is False
            )
            else "FAIL"
        ),
    }

    # --------------------------------------------------------
    # T4
    # --------------------------------------------------------

    checks["T4_ranking_semantics"] = {
        "status": (
            "PASS"
            if (
                TASK_BOUNDARY["T4"][
                    "native_quantity"
                ]
                == (
                    "Candidate-space assignee "
                    "retrieval/ranking"
                )
                and
                TASK_BOUNDARY["T4"][
                    "native_probability_output"
                ]
                is False
            )
            else "FAIL"
        ),
    }

    # --------------------------------------------------------
    # T5
    # --------------------------------------------------------

    checks["T5_probability_semantics"] = {
        "status": (
            "PASS"
            if (
                TASK_BOUNDARY["T5"][
                    "native_probability_output"
                ]
                is True
                and
                TASK_BOUNDARY["T5"][
                    "accepted_for_calibration"
                ]
                is True
            )
            else "FAIL"
        ),
    }

    # --------------------------------------------------------
    # T6
    # --------------------------------------------------------

    checks["T6_query_ranking_semantics"] = {
        "status": (
            "PASS"
            if (
                TASK_BOUNDARY["T6"][
                    "native_probability_output"
                ]
                is False
                and
                "observable_non_positive"
                in " ".join(
                    TASK_BOUNDARY["T6"][
                        "semantic_restrictions"
                    ]
                )
            )
            else "FAIL"
        ),
    }

    # --------------------------------------------------------
    # T7
    # --------------------------------------------------------

    checks["T7_survival_semantics"] = {
        "status": (
            "PASS"
            if (
                TASK_BOUNDARY["T7"][
                    "native_quantity"
                ]
                == (
                    "Survival / time-to-event prediction"
                )
                and
                "duration_seconds"
                in TASK_BOUNDARY["T7"][
                    "outcomes"
                ]
                and
                "event"
                in TASK_BOUNDARY["T7"][
                    "outcomes"
                ]
            )
            else "FAIL"
        ),
    }

    failed = []

    for key, value in checks.items():

        if value.get("status") == "FAIL":
            failed.append(key)

        nested = value.get(
            "task_statuses",
            {},
        )

        for task, task_check in nested.items():

            if (
                task_check.get("status")
                == "FAIL"
            ):
                failed.append(
                    f"{key}.{task}"
                )

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
# Global control validation
# ------------------------------------------------------------

def validate_controls() -> dict[str, Any]:

    expected_false = [
        "task_specific_calibration_only",
        "universal_confidence_score",
        "universal_risk_score",
        "cross_task_probability_comparability",
        "synthetic_target_creation",
        "synthetic_probability_creation",
        "blind_probability_averaging",
        "arbitrary_cross_task_weights",
        "post_creation_features_allowed",
        "t6_observable_non_positive_as_true_negative",
        "t7_binary_resolution_conversion",
        "t7_censoring_relabelling",
        "locked_test_for_calibration_selection",
    ]

    checks = {}

    # task-specific calibration must be TRUE
    checks[
        "task_specific_calibration_only"
    ] = {
        "status": (
            "PASS"
            if GLOBAL_RESTRICTIONS[
                "task_specific_calibration_only"
            ]
            is True
            else "FAIL"
        ),
        "value": GLOBAL_RESTRICTIONS[
            "task_specific_calibration_only"
        ],
    }

    for key in expected_false:

        if key == "task_specific_calibration_only":
            continue

        checks[key] = {
            "status": (
                "PASS"
                if GLOBAL_RESTRICTIONS[key]
                is False
                else "FAIL"
            ),
            "value": GLOBAL_RESTRICTIONS[key],
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
# Main
# ------------------------------------------------------------

def main() -> None:

    print("=" * 72)
    print("T9 MOD-037 OP-005")
    print("Accepted Native Output Population & Semantics Lock")
    print("=" * 72)
    print()

    print(
        "Loading previous T9 evidence..."
    )

    previous = (
        validate_previous_operations()
    )

    print(
        f"Previous-operation consistency: "
        f"{previous['status']}"
    )

    print()

    print(
        "Validating frozen task boundary..."
    )

    boundary = (
        validate_boundary()
    )

    print(
        f"Task-boundary validation: "
        f"{boundary['status']}"
    )

    print()

    print(
        "Validating global restrictions..."
    )

    controls = (
        validate_controls()
    )

    print(
        f"Global restrictions: "
        f"{controls['status']}"
    )

    # --------------------------------------------------------
    # Overall closure
    # --------------------------------------------------------

    overall_pass = (
        previous["status"] == "PASS"
        and boundary["status"] == "PASS"
        and controls["status"] == "PASS"
    )

    # --------------------------------------------------------
    # Population summary
    # --------------------------------------------------------

    empirical_calibration_tasks = [
        task
        for task, info
        in TASK_BOUNDARY.items()
        if info.get(
            "accepted_for_calibration"
        )
    ]

    native_evaluation_tasks = [
        task
        for task, info
        in TASK_BOUNDARY.items()
        if info.get(
            "accepted_for_native_evaluation"
        )
    ]

    unavailable_tasks = [
        task
        for task, info
        in TASK_BOUNDARY.items()
        if info.get(
            "status"
        )
        in {
            "UNAVAILABLE",
            "UNAVAILABLE_FOR_PROBABILITY_CALIBRATION",
        }
    ]

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    output = {
        "operation": "T9_MOD-037_OP-005",
        "title": (
            "Accepted Native Output Population & "
            "Semantics Lock"
        ),
        "status": (
            "PASS"
            if overall_pass
            else "FAIL"
        ),
        "purpose": (
            "Freeze the empirical T9 output boundary and "
            "task-specific semantics before calibration/"
            "evaluation procedures are selected or fitted."
        ),
        "previous_operation_artifacts": {
            "OP-003": str(OP003_ARTIFACT),
            "OP-004": str(OP004_ARTIFACT),
            "OP-004A": str(OP004A_ARTIFACT),
        },
        "previous_operation_validation": previous,
        "task_boundary": TASK_BOUNDARY,
        "empirical_calibration_tasks": (
            empirical_calibration_tasks
        ),
        "native_evaluation_tasks": (
            native_evaluation_tasks
        ),
        "unavailable_tasks": unavailable_tasks,
        "global_restrictions": GLOBAL_RESTRICTIONS,
        "global_control_validation": controls,
        "closure_statement": (
            "The T9 empirical boundary is frozen at the "
            "task-specific native-output level. T5 is the "
            "currently accepted native probability output. "
            "T4 and T6 remain native ranking quantities. "
            "T7 remains native survival/time-to-event output. "
            "T2 probability calibration is unavailable because "
            "no native probability artifact exists. T3 has no "
            "accepted native prediction artifact. No universal "
            "confidence or risk score is established."
        ),
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
    # Console output
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print("T9 MOD-037 OP-005 RESULT")
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
            f"{TASK_BOUNDARY[task]['status']}"
        )

    print()

    print(
        "Empirical calibration tasks:",
        ", ".join(
            empirical_calibration_tasks
        )
        if empirical_calibration_tasks
        else "NONE",
    )

    print(
        "Native evaluation tasks:",
        ", ".join(
            native_evaluation_tasks
        )
        if native_evaluation_tasks
        else "NONE",
    )

    print(
        "Unavailable tasks:",
        ", ".join(
            unavailable_tasks
        )
        if unavailable_tasks
        else "NONE",
    )

    print()

    print(
        "Previous-operation validation:",
        previous["status"],
    )

    print(
        "Boundary validation:",
        boundary["status"],
    )

    print(
        "Global restriction validation:",
        controls["status"],
    )

    print()

    print(
        f"Output: {OUTPUT_JSON}"
    )

    print()

    if overall_pass:

        print(
            "T9 MOD-037 OP-005 semantics lock: PASS"
        )

    else:

        print(
            "T9 MOD-037 OP-005 semantics lock: FAIL"
        )


if __name__ == "__main__":
    main()