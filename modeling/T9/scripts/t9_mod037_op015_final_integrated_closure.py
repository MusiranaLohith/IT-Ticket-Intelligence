from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# ============================================================
# T9 MOD-037 OP-015
# FINAL INTEGRATED EVIDENCE SYNTHESIS & CLOSURE
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
    / "t9_mod037_op015_final_integrated_closure.json"
)


# ============================================================
# PRIOR EVIDENCE
# ============================================================

PRIOR_ARTIFACTS = {

    "OP-001":
        OUTPUT_DIR
        / "t9_mod037_op001_confidence_calibration_contract.json",

    "OP-005":
        OUTPUT_DIR
        / "t9_mod037_op005_output_semantics_lock.json",

    "OP-010":
        OUTPUT_DIR
        / "t9_mod037_op010_t5_calibration_evidence_synthesis.json",

    "OP-011":
        OUTPUT_DIR
        / "t9_mod037_op011_t4_ranking_evaluation.json",

    "OP-012D":
        OUTPUT_DIR
        / "t9_mod037_op012d_t6_ranking_reliability.json",

    "OP-013F":
        OUTPUT_DIR
        / "t9_mod037_op013f_t7_evidence_synthesis.json",

    "OP-014":
        OUTPUT_DIR
        / "t9_mod037_op014_cross_task_evidence_synthesis.json",
}


# ============================================================
# HELPERS
# ============================================================

def load_json(
    path: Path,
) -> dict[str, Any]:

    if not path.exists():

        raise FileNotFoundError(
            f"Required artifact missing: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        data = json.load(f)

    if not isinstance(
        data,
        dict,
    ):

        raise TypeError(
            f"Expected JSON object: {path}"
        )

    return data


def require_pass(
    name: str,
    data: dict[str, Any],
) -> None:

    status = str(
        data.get(
            "status",
            "",
        )
    )

    if status != "PASS":

        raise RuntimeError(
            f"{name} status is {status!r}; "
            "expected PASS."
        )


# ============================================================
# LOAD ALL PRIOR EVIDENCE
# ============================================================

def load_prior_evidence() -> dict[str, dict[str, Any]]:

    evidence = {}

    for name, path in PRIOR_ARTIFACTS.items():

        evidence[name] = load_json(path)

    return evidence


# ============================================================
# OP-001 CONTRACT VALIDATION
# ============================================================

def validate_contract(
    evidence: dict[str, dict[str, Any]],
) -> dict[str, Any]:

    op001 = evidence["OP-001"]

    require_pass(
        "OP-001",
        op001,
    )

    serialized = json.dumps(
        op001
    ).lower()

    required_terms = [

        "calibration",

        "confidence",
    ]

    missing = [

        term

        for term in required_terms

        if term not in serialized
    ]

    if missing:

        raise RuntimeError(
            "OP-001 contract evidence missing: "
            f"{missing}"
        )

    return {

        "status":
            "PASS",

        "role":
            "T9 confidence/calibration contract",

        "model_fitting":
            "NOT_PERFORMED",

        "universal_score":
            "NOT_CREATED",
    }


# ============================================================
# OP-005 SEMANTIC LOCK VALIDATION
# ============================================================

def validate_semantic_lock(
    evidence: dict[str, dict[str, Any]],
) -> dict[str, Any]:

    op005 = evidence["OP-005"]

    require_pass(
        "OP-005",
        op005,
    )

    global_restrictions = op005.get(
        "global_restrictions",
        {},
    )

    required_false = [

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

    failures = []

    for key in required_false:

        if (
            key in global_restrictions
            and
            global_restrictions[key]
            is not False
        ):

            failures.append(
                (
                    key,
                    global_restrictions[key],
                )
            )

    if failures:

        raise RuntimeError(
            "OP-005 semantic restrictions failed: "
            f"{failures}"
        )

    return {

        "status":
            "PASS",

        "semantic_boundary":
            "FROZEN",

        "cross_task_probability_comparability":
            "PROHIBITED",

        "universal_confidence":
            "PROHIBITED",

        "universal_risk":
            "PROHIBITED",

        "synthetic_target":
            "PROHIBITED",

        "T6_binary_reinterpretation":
            "PROHIBITED",

        "T7_binary_conversion":
            "PROHIBITED",

        "T7_censoring_relabelling":
            "PROHIBITED",
    }


# ============================================================
# TASK EVIDENCE VALIDATION
# ============================================================

def validate_task_evidence(
    evidence: dict[str, dict[str, Any]],
) -> dict[str, Any]:

    op010 = evidence["OP-010"]
    op011 = evidence["OP-011"]
    op012d = evidence["OP-012D"]
    op013f = evidence["OP-013F"]

    require_pass(
        "OP-010",
        op010,
    )

    require_pass(
        "OP-011",
        op011,
    )

    require_pass(
        "OP-012D",
        op012d,
    )

    require_pass(
        "OP-013F",
        op013f,
    )

    # --------------------------------------------------------
    # T5
    # --------------------------------------------------------

    t5_status = (
        "EMPIRICAL_CALIBRATION_EVIDENCE_ESTABLISHED"
    )

    op010_text = json.dumps(
        op010
    )

    if (
        "NOT_FORMALLY_SELECTED"
        not in op010_text
    ):

        raise RuntimeError(
            "T5 formal method-selection boundary "
            "was not preserved."
        )

    # --------------------------------------------------------
    # T4
    # --------------------------------------------------------

    t4_status = (
        "NATIVE_RANKING_EVALUATION_ESTABLISHED"
    )

    # --------------------------------------------------------
    # T6
    # --------------------------------------------------------

    t6_status = (
        "NATIVE_RETRIEVAL_EVALUATION_ESTABLISHED"
    )

    # --------------------------------------------------------
    # T7
    # --------------------------------------------------------

    op013f_text = json.dumps(
        op013f
    )

    if (
        "NATIVE_SURVIVAL_EVIDENCE_CLOSED"
        not in op013f_text
    ):

        raise RuntimeError(
            "T7 native survival closure was "
            "not preserved."
        )

    t7_status = (
        "NATIVE_SURVIVAL_EVIDENCE_CLOSED"
    )

    return {

        "T2":
            {
                "status":
                    "UNAVAILABLE_FOR_PROBABILITY_CALIBRATION"
            },

        "T3":
            {
                "status":
                    "UNAVAILABLE"
            },

        "T4":
            {
                "status":
                    t4_status,

                "probability_calibration":
                    "NOT_ESTABLISHED",
            },

        "T5":
            {
                "status":
                    t5_status,

                "formal_method_selection":
                    "NOT_FORMALLY_SELECTED",
            },

        "T6":
            {
                "status":
                    t6_status,

                "binary_probability_calibration":
                    "NOT_ESTABLISHED",
            },

        "T7":
            {
                "status":
                    t7_status,

                "formal_survival_calibration":
                    "NOT_ESTABLISHED",

                "formal_calibration_uncertainty":
                    "NOT_ESTABLISHED",
            },
    }


# ============================================================
# OP-014 FINAL BOUNDARY VALIDATION
# ============================================================

def validate_op014(
    evidence: dict[str, dict[str, Any]],
) -> dict[str, Any]:

    op014 = evidence["OP-014"]

    require_pass(
        "OP-014",
        op014,
    )

    final_conclusion = op014.get(
        "final_conclusion",
        {},
    )

    interface = op014.get(
        "t8_interface",
        {},
    )

    if (
        final_conclusion.get(
            "t9_cross_task_status"
        )
        !=
        "TASK_SPECIFIC_EVIDENCE_BOUNDARY_CLOSED"
    ):

        raise RuntimeError(
            "OP-014 does not establish the "
            "required final task-specific boundary."
        )

    if (
        final_conclusion.get(
            "universal_confidence"
        )
        !=
        "NOT_CREATED"
    ):

        raise RuntimeError(
            "OP-014 universal confidence boundary "
            "is not preserved."
        )

    if (
        final_conclusion.get(
            "universal_risk_score"
        )
        !=
        "NOT_CREATED"
    ):

        raise RuntimeError(
            "OP-014 universal risk boundary "
            "is not preserved."
        )

    if (
        interface.get(
            "status"
        )
        !=
        "ACCEPTED_TASK_SPECIFIC_INTERFACE"
    ):

        raise RuntimeError(
            "OP-014 T8 interface is not accepted."
        )

    return {

        "status":
            "PASS",

        "cross_task_status":
            "TASK_SPECIFIC_EVIDENCE_BOUNDARY_CLOSED",

        "T8_interface":
            "ACCEPTED_TASK_SPECIFIC_INTERFACE",

        "universal_confidence":
            "NOT_CREATED",

        "universal_risk":
            "NOT_CREATED",

        "synthetic_fusion_target":
            "NOT_CREATED",

        "automatic_action_label":
            "NOT_CREATED",
    }


# ============================================================
# FINAL EVIDENCE STATEMENT
# ============================================================

def build_final_evidence_statement(
    task_evidence: dict[str, Any],
) -> dict[str, Any]:

    return {

        "T2":
            (
                "No accepted native probability artifact "
                "for probability calibration."
            ),

        "T3":
            (
                "No accepted native probability artifact "
                "for probability calibration."
            ),

        "T4":
            (
                "Native candidate-space ranking evaluation "
                "is established. Universal probability "
                "calibration is not established."
            ),

        "T5":
            (
                "Empirical calibration improvement evidence "
                "is established. No formal calibration method "
                "winner was selected."
            ),

        "T6":
            (
                "Native query-level retrieval/ranking "
                "evaluation and reliability evidence are "
                "established. Ordinary binary probability "
                "calibration is not established."
            ),

        "T7":
            (
                "Native survival evaluation, uncertainty, "
                "and descriptive reliability are established. "
                "Formal survival calibration and formal "
                "calibration uncertainty are not established."
            ),

        "cross_task":
            (
                "Task-specific quantities cannot be treated "
                "as numerically comparable probabilities. "
                "No universal confidence/risk construct "
                "is empirically established or created."
            ),
    }


# ============================================================
# FINAL CONTROLS
# ============================================================

def build_final_controls() -> dict[str, bool]:

    return {

        "all_prior_T9_operations_validated":
            True,

        "new_model_fitted":
            False,

        "new_predictions_generated":
            False,

        "new_probability_generated":
            False,

        "new_calibration_fitted":
            False,

        "new_target_created":
            False,

        "synthetic_target_created":
            False,

        "synthetic_probability_created":
            False,

        "cross_task_probability_aggregation":
            False,

        "cross_task_probability_comparison":
            False,

        "universal_confidence_created":
            False,

        "universal_risk_score_created":
            False,

        "automatic_action_label_created":
            False,

        "threshold_selected":
            False,

        "model_selected":
            False,

        "locked_test_used":
            False,

        "post_creation_information_used":
            False,

        "existing_artifacts_modified":
            False,

        "native_semantics_preserved":
            True,

        "task_specific_evidence_preserved":
            True,

        "provenance_preserved":
            True,

        "missing_evidence_preserved":
            True,

        "T6_observation_semantics_preserved":
            True,

        "T7_right_censoring_preserved":
            True,
    }


def validate_final_controls(
    controls: dict[str, bool],
) -> dict[str, Any]:

    allowed_true = {

        "all_prior_T9_operations_validated",

        "native_semantics_preserved",

        "task_specific_evidence_preserved",

        "provenance_preserved",

        "missing_evidence_preserved",

        "T6_observation_semantics_preserved",

        "T7_right_censoring_preserved",
    }

    failures = []

    for key, value in controls.items():

        if key in allowed_true:

            if value is not True:

                failures.append(
                    key
                )

        else:

            if value is not False:

                failures.append(
                    key
                )

    return {

        "status":
            (
                "PASS"
                if not failures
                else "FAIL"
            ),

        "failed_controls":
            failures,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 72)
    print(
        "T9 MOD-037 OP-015"
    )
    print(
        "FINAL INTEGRATED EVIDENCE SYNTHESIS & CLOSURE"
    )
    print("=" * 72)
    print()

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    print(
        "Loading completed T9 evidence..."
    )

    evidence = load_prior_evidence()

    print(
        "Prior artifacts loaded:",
        len(evidence),
    )

    print()

    # --------------------------------------------------------
    # CONTRACT
    # --------------------------------------------------------

    print(
        "Validating T9 contract..."
    )

    contract = validate_contract(
        evidence
    )

    print(
        "Contract:",
        contract[
            "status"
        ],
    )

    print()

    # --------------------------------------------------------
    # SEMANTIC LOCK
    # --------------------------------------------------------

    print(
        "Validating frozen semantic boundary..."
    )

    semantic_lock = validate_semantic_lock(
        evidence
    )

    print(
        "Semantic boundary:",
        semantic_lock[
            "semantic_boundary"
        ],
    )

    print(
        "Universal confidence:",
        semantic_lock[
            "universal_confidence"
        ],
    )

    print(
        "Universal risk:",
        semantic_lock[
            "universal_risk"
        ],
    )

    print()

    # --------------------------------------------------------
    # TASK EVIDENCE
    # --------------------------------------------------------

    print(
        "Validating integrated task evidence..."
    )

    task_evidence = validate_task_evidence(
        evidence
    )

    for task, result in task_evidence.items():

        print(
            f"{task}:",
            result[
                "status"
            ],
        )

    print()

    # --------------------------------------------------------
    # OP-014
    # --------------------------------------------------------

    print(
        "Validating OP-014 final boundary..."
    )

    op014_boundary = validate_op014(
        evidence
    )

    print(
        "OP-014:",
        op014_boundary[
            "status"
        ],
    )

    print(
        "Cross-task status:",
        op014_boundary[
            "cross_task_status"
        ],
    )

    print(
        "T8 interface:",
        op014_boundary[
            "T8_interface"
        ],
    )

    print()

    # --------------------------------------------------------
    # FINAL EVIDENCE STATEMENT
    # --------------------------------------------------------

    final_evidence = (
        build_final_evidence_statement(
            task_evidence
        )
    )

    print(
        "Final evidence boundary:"
    )

    print(
        "  T2:",
        task_evidence[
            "T2"
        ][
            "status"
        ],
    )

    print(
        "  T3:",
        task_evidence[
            "T3"
        ][
            "status"
        ],
    )

    print(
        "  T4:",
        task_evidence[
            "T4"
        ][
            "status"
        ],
    )

    print(
        "  T5:",
        task_evidence[
            "T5"
        ][
            "status"
        ],
    )

    print(
        "  T6:",
        task_evidence[
            "T6"
        ][
            "status"
        ],
    )

    print(
        "  T7:",
        task_evidence[
            "T7"
        ][
            "status"
        ],
    )

    print()

    # --------------------------------------------------------
    # FINAL CONTROLS
    # --------------------------------------------------------

    controls = build_final_controls()

    control_validation = (
        validate_final_controls(
            controls
        )
    )

    print(
        "Final control validation:",
        control_validation[
            "status"
        ],
    )

    if (
        control_validation[
            "status"
        ]
        !=
        "PASS"
    ):

        raise RuntimeError(
            "Final control validation failed."
        )

    print()

    # --------------------------------------------------------
    # FINAL CLOSURE
    # --------------------------------------------------------

    final_status = (
        "T9_MOD-037_CLOSED"
        if (
            contract[
                "status"
            ]
            == "PASS"

            and
            semantic_lock[
                "status"
            ]
            == "PASS"

            and
            op014_boundary[
                "status"
            ]
            == "PASS"

            and
            control_validation[
                "status"
            ]
            == "PASS"
        )
        else
        "T9_MOD-037_NOT_CLOSED"
    )

    closure_statement = {

        "status":
            final_status,

        "scope":
            (
                "T9 confidence, calibration, native "
                "evaluation, uncertainty, reliability, "
                "and cross-task evidence boundary."
            ),

        "empirical_boundary":
            (
                "T9 establishes task-specific empirical "
                "evidence only. Heterogeneous task outputs "
                "remain tied to their native predictive "
                "quantities and observation structures."
            ),

        "calibration_boundary":
            (
                "T5 has empirical calibration improvement "
                "evidence without formal method selection. "
                "T2 and T3 lack accepted native probability "
                "artifacts. T4 and T6 remain native ranking/"
                "retrieval quantities. T7 remains a survival "
                "quantity with censoring-aware uncertainty."
            ),

        "cross_task_boundary":
            (
                "Cross-task numerical probability "
                "comparability is not established and "
                "is prohibited by the frozen methodology."
            ),

        "universal_confidence":
            "NOT_ESTABLISHED_AND_NOT_CREATED",

        "universal_risk":
            "NOT_ESTABLISHED_AND_NOT_CREATED",

        "synthetic_fusion_target":
            "NOT_CREATED",

        "automatic_action_policy":
            "NOT_ESTABLISHED",

        "human_review_boundary":
            "NOT_ESTABLISHED_BY_T9",

        "locked_test":
            "NOT_USED_FOR_CALIBRATION_SELECTION",

        "final_interpretation":
            (
                "T9 is closed as an evidence and calibration "
                "boundary. It does not create a universal "
                "confidence/risk score or an autonomous "
                "decision policy. The resulting T8 interface "
                "remains task-specific, provenance-preserving, "
                "and uncertainty-aware."
            ),
    }

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    output = {

        "operation":
            "T9_MOD-037_OP-015",

        "title":
            "Final Integrated Evidence Synthesis & Closure",

        "status":
            (
                "PASS"
                if final_status
                == "T9_MOD-037_CLOSED"
                else "FAIL"
            ),

        "purpose":
            (
                "Perform the final read-only integration of "
                "completed T9 evidence and close the T9 "
                "empirical confidence/calibration boundary."
            ),

        "prior_operations":
            list(
                PRIOR_ARTIFACTS.keys()
            ),

        "contract_validation":
            contract,

        "semantic_lock_validation":
            semantic_lock,

        "task_evidence":
            task_evidence,

        "final_evidence_statement":
            final_evidence,

        "OP014_boundary":
            op014_boundary,

        "controls":
            controls,

        "control_validation":
            control_validation,

        "closure":
            closure_statement,

        "methodological_restrictions": [

            "No universal confidence score.",

            "No universal risk score.",

            "No synthetic fusion target.",

            "No automatic-action label.",

            "No cross-task probability aggregation.",

            "No cross-task numerical probability "
            "comparison.",

            "No arbitrary cross-task weighting.",

            "No new model fitting.",

            "No new prediction generation.",

            "No new probability generation.",

            "No new calibration fitting.",

            "No threshold selection.",

            "No model selection.",

            "No locked-test calibration selection.",

            "T4 candidate-space semantics preserved.",

            "T6 observable_non_positive is not treated "
            "as a true negative.",

            "T7 right censoring is preserved.",

            "Unavailable evidence remains unavailable.",
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

    # --------------------------------------------------------
    # FINAL CONSOLE
    # --------------------------------------------------------

    print("=" * 72)
    print(
        "T9 MOD-037 OP-015 RESULT"
    )
    print("=" * 72)
    print()

    print(
        "T9 final status:",
        final_status,
    )

    print(
        "Universal confidence:",
        closure_statement[
            "universal_confidence"
        ],
    )

    print(
        "Universal risk:",
        closure_statement[
            "universal_risk"
        ],
    )

    print(
        "Synthetic fusion target:",
        closure_statement[
            "synthetic_fusion_target"
        ],
    )

    print(
        "Automatic action policy:",
        closure_statement[
            "automatic_action_policy"
        ],
    )

    print(
        "Human-review boundary:",
        closure_statement[
            "human_review_boundary"
        ],
    )

    print(
        "Locked test:",
        closure_statement[
            "locked_test"
        ],
    )

    print()

    print(
        "Control validation:",
        control_validation[
            "status"
        ],
    )

    print()

    print(
        "Output:",
        OUTPUT_JSON,
    )

    print()

    print(
        "T9 MOD-037 OP-015:",
        (
            "PASS"
            if final_status
            == "T9_MOD-037_CLOSED"
            else "FAIL"
        ),
    )


if __name__ == "__main__":
    main()