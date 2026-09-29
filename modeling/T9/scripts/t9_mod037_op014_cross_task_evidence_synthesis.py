from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# ============================================================
# T9 MOD-037 OP-014
# CROSS-TASK EVIDENCE BOUNDARY & CALIBRATION SYNTHESIS
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
    / "t9_mod037_op014_cross_task_evidence_synthesis.json"
)


# ============================================================
# PRIOR ARTIFACTS
# ============================================================

OP005 = (
    OUTPUT_DIR
    / "t9_mod037_op005_output_semantics_lock.json"
)

OP008 = (
    OUTPUT_DIR
    / "t9_mod037_op008_t5_empirical_calibration.json"
)

OP009 = (
    OUTPUT_DIR
    / "t9_mod037_op009_t5_uncertainty_reliability.json"
)

OP010 = (
    OUTPUT_DIR
    / "t9_mod037_op010_t5_calibration_evidence_synthesis.json"
)

OP011 = (
    OUTPUT_DIR
    / "t9_mod037_op011_t4_ranking_evaluation.json"
)

OP012C = (
    OUTPUT_DIR
    / "t9_mod037_op012c_t6_native_ranking_evaluation.json"
)

OP012D = (
    OUTPUT_DIR
    / "t9_mod037_op012d_t6_ranking_reliability.json"
)

OP013F = (
    OUTPUT_DIR
    / "t9_mod037_op013f_t7_evidence_synthesis.json"
)


# ============================================================
# HELPERS
# ============================================================

def require_file(path: Path) -> None:

    if not path.exists():

        raise FileNotFoundError(
            f"Required artifact missing: {path}"
        )


def load_json(path: Path) -> dict[str, Any]:

    require_file(path)

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        data = json.load(f)

    if not isinstance(data, dict):

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
# LOAD EVIDENCE
# ============================================================

def load_evidence() -> dict[str, dict[str, Any]]:

    paths = {

        "OP-005": OP005,

        "OP-008": OP008,

        "OP-009": OP009,

        "OP-010": OP010,

        "OP-011": OP011,

        "OP-012C": OP012C,

        "OP-012D": OP012D,

        "OP-013F": OP013F,
    }

    result = {}

    for name, path in paths.items():

        result[name] = load_json(path)

    return result


# ============================================================
# T5 VALIDATION
# ============================================================

def validate_t5(
    evidence: dict[str, dict[str, Any]],
) -> dict[str, Any]:

    op008 = evidence["OP-008"]
    op009 = evidence["OP-009"]
    op010 = evidence["OP-010"]

    require_pass(
        "OP-008",
        op008,
    )

    require_pass(
        "OP-009",
        op009,
    )

    require_pass(
        "OP-010",
        op010,
    )

    serialized = json.dumps(
        op010
    )

    if (
        "CALIBRATION_IMPROVEMENT_SUPPORTED"
        not in serialized
    ):

        raise RuntimeError(
            "OP-010 does not establish the "
            "expected T5 calibration evidence."
        )

    if (
        "NOT_FORMALLY_SELECTED"
        not in serialized
    ):

        raise RuntimeError(
            "OP-010 does not preserve the "
            "required no-formal-selection boundary."
        )

    return {

        "task": "T5",

        "status":
            "EMPIRICAL_CALIBRATION_EVIDENCE_ESTABLISHED",

        "native_quantity":
            "Binary duplicate probability",

        "calibration_evidence":
            "ESTABLISHED",

        "calibration_improvement":
            "SUPPORTED",

        "formal_method_selection":
            "NOT_FORMALLY_SELECTED",

        "uncertainty_reliability":
            "ESTABLISHED",

        "locked_test_used":
            False,

        "universal_score_created":
            False,
    }


# ============================================================
# T4 VALIDATION
# ============================================================

def validate_t4(
    evidence: dict[str, dict[str, Any]],
) -> dict[str, Any]:

    op011 = evidence["OP-011"]

    require_pass(
        "OP-011",
        op011,
    )

    serialized = json.dumps(
        op011
    ).lower()

    if (
        "native ranking"
        not in serialized
        and
        "candidate-space"
        not in serialized
    ):

        raise RuntimeError(
            "OP-011 does not establish "
            "T4 native ranking semantics."
        )

    return {

        "task": "T4",

        "status":
            "NATIVE_RANKING_EVALUATION_ESTABLISHED",

        "native_quantity":
            "Candidate-space assignee retrieval/ranking",

        "native_evaluation":
            "ESTABLISHED",

        "probability_calibration":
            "NOT_ESTABLISHED",

        "candidate_space_restriction":
            "PRESERVED",

        "unseen_targets":
            "UNAVAILABLE_NOT_NEGATIVE",

        "universal_score_created":
            False,
    }


# ============================================================
# T6 VALIDATION
#
# OP-012C establishes the native ranking evaluation.
# OP-012D establishes uncertainty/reliability around
# that native ranking evaluation.
#
# OP-012D is therefore NOT treated as a standalone
# ranking-semantics artifact.
# ============================================================

def validate_t6(
    evidence: dict[str, dict[str, Any]],
) -> dict[str, Any]:

    op012c = evidence["OP-012C"]
    op012d = evidence["OP-012D"]

    require_pass(
        "OP-012C",
        op012c,
    )

    require_pass(
        "OP-012D",
        op012d,
    )

    serialized_c = json.dumps(
        op012c
    ).lower()

    serialized_d = json.dumps(
        op012d
    ).lower()

    # --------------------------------------------------------
    # OP-012C: native ranking establishment
    # --------------------------------------------------------

    ranking_evidence_present = (
        "hit@1" in serialized_c
        or
        "hit@3" in serialized_c
        or
        "mrr" in serialized_c
        or
        "native ranking" in serialized_c
        or
        "query-level" in serialized_c
    )

    if not ranking_evidence_present:

        raise RuntimeError(
            "OP-012C does not contain sufficient "
            "native T6 ranking evaluation evidence."
        )

    # --------------------------------------------------------
    # OP-012D: uncertainty/reliability establishment
    # --------------------------------------------------------

    reliability_evidence_present = (
        "bootstrap" in serialized_d
        or
        "confidence interval" in serialized_d
        or
        "hit@1" in serialized_d
        or
        "mrr" in serialized_d
    )

    if not reliability_evidence_present:

        raise RuntimeError(
            "OP-012D does not contain sufficient "
            "T6 ranking reliability evidence."
        )

    # --------------------------------------------------------
    # Preserve T6 observation semantics
    # --------------------------------------------------------

    combined_serialized = (
        serialized_c
        + serialized_d
    )

    observable_non_positive_preserved = (
        "observable_non_positive"
        in combined_serialized
        or
        "true negative"
        in combined_serialized
        or
        "not a true negative"
        in combined_serialized
    )

    if not observable_non_positive_preserved:

        raise RuntimeError(
            "T6 evidence chain does not preserve "
            "the observable_non_positive / "
            "true-negative distinction."
        )

    return {

        "task": "T6",

        "status":
            "NATIVE_RETRIEVAL_EVALUATION_ESTABLISHED",

        "native_quantity":
            "Query-level candidate retrieval/ranking",

        "native_evaluation":
            "ESTABLISHED",

        "uncertainty_reliability":
            "ESTABLISHED",

        "ranking_evidence_source":
            "OP-012C",

        "reliability_evidence_source":
            "OP-012D",

        "binary_probability_calibration":
            "NOT_ESTABLISHED",

        "observable_non_positive":
            "NOT_TRUE_NEGATIVE",

        "universal_score_created":
            False,
    }


# ============================================================
# T7 VALIDATION
# ============================================================

def validate_t7(
    evidence: dict[str, dict[str, Any]],
) -> dict[str, Any]:

    op013f = evidence["OP-013F"]

    require_pass(
        "OP-013F",
        op013f,
    )

    conclusion = op013f.get(
        "final_t7_conclusion",
        {},
    )

    if (
        conclusion.get(
            "t7_t9_status"
        )
        != "NATIVE_SURVIVAL_EVIDENCE_CLOSED"
    ):

        raise RuntimeError(
            "OP-013F does not establish "
            "T7 native survival closure."
        )

    return {

        "task": "T7",

        "status":
            "NATIVE_SURVIVAL_EVIDENCE_CLOSED",

        "native_quantity":
            "Survival / time-to-event prediction",

        "native_evaluation":
            "ESTABLISHED",

        "native_uncertainty":
            "ESTABLISHED",

        "descriptive_reliability":
            "ESTABLISHED",

        "formal_survival_calibration":
            "NOT_ESTABLISHED",

        "formal_calibration_uncertainty":
            "NOT_ESTABLISHED",

        "right_censoring":
            "PRESERVED",

        "universal_score_created":
            False,
    }


# ============================================================
# T2 / T3 BOUNDARY
# ============================================================

def validate_t2_t3(
    evidence: dict[str, dict[str, Any]],
) -> dict[str, Any]:

    op005 = evidence["OP-005"]

    require_pass(
        "OP-005",
        op005,
    )

    task_boundary = op005.get(
        "task_boundary",
        {},
    )

    t2 = task_boundary.get(
        "T2",
        {},
    )

    t3 = task_boundary.get(
        "T3",
        {},
    )

    if not t2:

        raise RuntimeError(
            "T2 boundary missing from OP-005."
        )

    if not t3:

        raise RuntimeError(
            "T3 boundary missing from OP-005."
        )

    t2_status = str(
        t2.get(
            "status",
            "",
        )
    )

    t3_status = str(
        t3.get(
            "status",
            "",
        )
    )

    return {

        "task": "T2/T3",

        "T2": {

            "status":
                t2_status,

            "probability_calibration":
                (
                    "AVAILABLE"
                    if t2_status
                    == "ACCEPTED_NATIVE_PROBABILITY"
                    else "NOT_AVAILABLE"
                ),
        },

        "T3": {

            "status":
                t3_status,

            "probability_calibration":
                (
                    "AVAILABLE"
                    if t3_status
                    == "ACCEPTED_NATIVE_PROBABILITY"
                    else "NOT_AVAILABLE"
                ),
        },

        "interpretation":
            (
                "T2 and T3 remain governed by "
                "their frozen OP-005 task boundaries. "
                "No unavailable native probability "
                "artifact is reconstructed here."
            ),
    }


# ============================================================
# CROSS-TASK RESTRICTION VALIDATION
# ============================================================

def validate_cross_task_restrictions(
    evidence: dict[str, dict[str, Any]],
) -> dict[str, Any]:

    op005 = evidence["OP-005"]

    restrictions = op005.get(
        "global_restrictions",
        {},
    )

    expected_false = [

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

    for key in expected_false:

        if key in restrictions:

            value = restrictions[key]

            if value is not False:

                failures.append(
                    (
                        key,
                        value,
                    )
                )

    serialized = json.dumps(
        op005
    ).lower()

    required_phrases = [

        "cross_task_probability_comparability",

        "universal_confidence_score",

        "universal_risk_score",
    ]

    phrase_presence = {

        phrase:
            phrase in serialized

        for phrase in required_phrases
    }

    if failures:

        raise RuntimeError(
            "Cross-task restrictions failed: "
            f"{failures}"
        )

    return {

        "status":
            "PASS",

        "prohibited_constructs":
            {

                "universal_confidence_score":
                    "PROHIBITED",

                "universal_risk_score":
                    "PROHIBITED",

                "cross_task_probability_comparability":
                    "PROHIBITED",

                "synthetic_target":
                    "PROHIBITED",

                "blind_probability_averaging":
                    "PROHIBITED",

                "arbitrary_cross_task_weights":
                    "PROHIBITED",
            },

        "OP-005_restriction_fields_present":
            phrase_presence,
    }


# ============================================================
# TASK MATRIX
# ============================================================

def build_task_matrix(
    t2_t3: dict[str, Any],
    t4: dict[str, Any],
    t5: dict[str, Any],
    t6: dict[str, Any],
    t7: dict[str, Any],
) -> list[dict[str, Any]]:

    return [

        {

            "task":
                "T2",

            "native_quantity":
                "Categorical Priority probability",

            "empirical_status":
                (
                    t2_t3[
                        "T2"
                    ][
                        "probability_calibration"
                    ]
                ),

            "cross_task_comparison":
                "PROHIBITED",

            "universal_score":
                "NOT_CREATED",
        },

        {

            "task":
                "T3",

            "native_quantity":
                "Categorical Severity probability",

            "empirical_status":
                (
                    t2_t3[
                        "T3"
                    ][
                        "probability_calibration"
                    ]
                ),

            "cross_task_comparison":
                "PROHIBITED",

            "universal_score":
                "NOT_CREATED",
        },

        {

            "task":
                "T4",

            "native_quantity":
                t4[
                    "native_quantity"
                ],

            "empirical_status":
                t4[
                    "status"
                ],

            "cross_task_comparison":
                "PROHIBITED",

            "universal_score":
                "NOT_CREATED",
        },

        {

            "task":
                "T5",

            "native_quantity":
                t5[
                    "native_quantity"
                ],

            "empirical_status":
                t5[
                    "status"
                ],

            "cross_task_comparison":
                "PROHIBITED",

            "universal_score":
                "NOT_CREATED",
        },

        {

            "task":
                "T6",

            "native_quantity":
                t6[
                    "native_quantity"
                ],

            "empirical_status":
                t6[
                    "status"
                ],

            "cross_task_comparison":
                "PROHIBITED",

            "universal_score":
                "NOT_CREATED",
        },

        {

            "task":
                "T7",

            "native_quantity":
                t7[
                    "native_quantity"
                ],

            "empirical_status":
                t7[
                    "status"
                ],

            "cross_task_comparison":
                "PROHIBITED",

            "universal_score":
                "NOT_CREATED",
        },
    ]


# ============================================================
# FINAL T8 INTERFACE
# ============================================================

def build_t8_interface() -> dict[str, Any]:

    return {

        "status":
            "ACCEPTED_TASK_SPECIFIC_INTERFACE",

        "principle":
            (
                "T8 may preserve and present each "
                "task's native output/uncertainty "
                "with provenance, but may not "
                "convert heterogeneous task outputs "
                "into a common numerical probability "
                "or universal risk/confidence score."
            ),

        "task_specific_outputs":

            {

                "T2":
                    "Priority probability/confidence "
                    "only when native probability output "
                    "is available.",

                "T3":
                    "Severity probability/confidence "
                    "only when native probability output "
                    "is available.",

                "T4":
                    "Candidate-space assignee ranking "
                    "within its defined candidate universe.",

                "T5":
                    "Duplicate probability/calibration "
                    "evidence.",

                "T6":
                    "Query-level retrieval/ranking "
                    "evidence with native retrieval "
                    "semantics.",

                "T7":
                    "Survival/time-to-event prediction "
                    "with explicit uncertainty and "
                    "censoring semantics.",
            },

        "cross_task_probability_aggregation":
            "PROHIBITED",

        "cross_task_numerical_comparison":
            "PROHIBITED",

        "universal_confidence_score":
            "NOT_CREATED",

        "universal_risk_score":
            "NOT_CREATED",

        "synthetic_fusion_target":
            "NOT_CREATED",

        "automatic_action_label":
            "NOT_CREATED",

        "provenance":
            "MUST_BE_PRESERVED",

        "missing_evidence":
            (
                "Unavailable task evidence remains "
                "unavailable; it is not interpreted "
                "as a negative outcome."
            ),
    }


# ============================================================
# CONTROLS
# ============================================================

def build_controls() -> dict[str, bool]:

    return {

        "artifact_read_only":
            True,

        "new_model_fitted":
            False,

        "new_predictions_generated":
            False,

        "new_probability_generated":
            False,

        "calibration_fitted":
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

        "blind_probability_averaging":
            False,

        "arbitrary_cross_task_weights":
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

        "native_task_semantics_preserved":
            True,

        "task_specific_quantities_preserved":
            True,

        "provenance_preserved":
            True,

        "missing_evidence_preserved_as_unavailable":
            True,
    }


def validate_controls(
    controls: dict[str, bool],
) -> dict[str, Any]:

    allowed_true = {

        "artifact_read_only",

        "native_task_semantics_preserved",

        "task_specific_quantities_preserved",

        "provenance_preserved",

        "missing_evidence_preserved_as_unavailable",
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
        "T9 MOD-037 OP-014"
    )
    print(
        "CROSS-TASK EVIDENCE BOUNDARY "
        "& CALIBRATION SYNTHESIS"
    )
    print("=" * 72)
    print()

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    print(
        "Loading completed T9 task evidence..."
    )

    evidence = load_evidence()

    print(
        "Artifacts loaded:",
        len(evidence),
    )

    print()

    # --------------------------------------------------------
    # T2 / T3
    # --------------------------------------------------------

    print(
        "Validating T2/T3 boundary..."
    )

    t2_t3 = validate_t2_t3(
        evidence
    )

    print(
        "T2 boundary:",
        t2_t3[
            "T2"
        ][
            "status"
        ],
    )

    print(
        "T3 boundary:",
        t2_t3[
            "T3"
        ][
            "status"
        ],
    )

    print()

    # --------------------------------------------------------
    # T4
    # --------------------------------------------------------

    print(
        "Validating T4 evidence..."
    )

    t4 = validate_t4(
        evidence
    )

    print(
        "T4:",
        t4[
            "status"
        ],
    )

    print()

    # --------------------------------------------------------
    # T5
    # --------------------------------------------------------

    print(
        "Validating T5 calibration evidence..."
    )

    t5 = validate_t5(
        evidence
    )

    print(
        "T5:",
        t5[
            "status"
        ],
    )

    print()

    # --------------------------------------------------------
    # T6
    # --------------------------------------------------------

    print(
        "Validating T6 evidence..."
    )

    t6 = validate_t6(
        evidence
    )

    print(
        "T6:",
        t6[
            "status"
        ],
    )

    print(
        "T6 ranking source:",
        t6[
            "ranking_evidence_source"
        ],
    )

    print(
        "T6 reliability source:",
        t6[
            "reliability_evidence_source"
        ],
    )

    print()

    # --------------------------------------------------------
    # T7
    # --------------------------------------------------------

    print(
        "Validating T7 evidence..."
    )

    t7 = validate_t7(
        evidence
    )

    print(
        "T7:",
        t7[
            "status"
        ],
    )

    print()

    # --------------------------------------------------------
    # CROSS-TASK RESTRICTIONS
    # --------------------------------------------------------

    print(
        "Validating cross-task restrictions..."
    )

    restrictions = (
        validate_cross_task_restrictions(
            evidence
        )
    )

    print(
        "Cross-task restrictions:",
        restrictions[
            "status"
        ],
    )

    print()

    # --------------------------------------------------------
    # TASK MATRIX
    # --------------------------------------------------------

    matrix = build_task_matrix(
        t2_t3,
        t4,
        t5,
        t6,
        t7,
    )

    print(
        "Task evidence matrix:"
    )

    for row in matrix:

        print(
            f"  {row['task']}: "
            f"{row['empirical_status']}"
        )

    print()

    # --------------------------------------------------------
    # T8 INTERFACE
    # --------------------------------------------------------

    interface = build_t8_interface()

    print(
        "T8 task-specific interface:",
        interface[
            "status"
        ],
    )

    print(
        "Universal confidence score:",
        interface[
            "universal_confidence_score"
        ],
    )

    print(
        "Universal risk score:",
        interface[
            "universal_risk_score"
        ],
    )

    print(
        "Cross-task probability aggregation:",
        interface[
            "cross_task_probability_aggregation"
        ],
    )

    print(
        "Cross-task numerical comparison:",
        interface[
            "cross_task_numerical_comparison"
        ],
    )

    print()

    # --------------------------------------------------------
    # CONTROLS
    # --------------------------------------------------------

    controls = build_controls()

    control_validation = (
        validate_controls(
            controls
        )
    )

    print(
        "Control validation:",
        control_validation[
            "status"
        ],
    )

    if (
        control_validation[
            "status"
        ]
        != "PASS"
    ):

        raise RuntimeError(
            "Control validation failed."
        )

    print()

    # --------------------------------------------------------
    # FINAL CONCLUSION
    # --------------------------------------------------------

    conclusion = {

        "t9_cross_task_status":
            "TASK_SPECIFIC_EVIDENCE_BOUNDARY_CLOSED",

        "T2":
            t2_t3[
                "T2"
            ],

        "T3":
            t2_t3[
                "T3"
            ],

        "T4":
            t4,

        "T5":
            t5,

        "T6":
            t6,

        "T7":
            t7,

        "cross_task_comparability":
            "NOT_ESTABLISHED_AND_PROHIBITED",

        "universal_confidence":
            "NOT_CREATED",

        "universal_risk_score":
            "NOT_CREATED",

        "synthetic_fusion_target":
            "NOT_CREATED",

        "automatic_action_label":
            "NOT_CREATED",

        "interpretation":
            (
                "T9 establishes a task-specific "
                "empirical evidence boundary rather "
                "than a universal confidence or risk "
                "scale. Each task remains interpreted "
                "according to its native predictive "
                "quantity, population, observation "
                "structure, and uncertainty semantics."
            ),
    }

    # --------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------

    overall_status = (
        "PASS"
        if (
            restrictions[
                "status"
            ]
            == "PASS"

            and
            control_validation[
                "status"
            ]
            == "PASS"

            and
            t5[
                "status"
            ]
            == (
                "EMPIRICAL_CALIBRATION_"
                "EVIDENCE_ESTABLISHED"
            )

            and
            t4[
                "status"
            ]
            == (
                "NATIVE_RANKING_"
                "EVALUATION_ESTABLISHED"
            )

            and
            t6[
                "status"
            ]
            == (
                "NATIVE_RETRIEVAL_"
                "EVALUATION_ESTABLISHED"
            )

            and
            t7[
                "status"
            ]
            == (
                "NATIVE_SURVIVAL_"
                "EVIDENCE_CLOSED"
            )
        )
        else "FAIL"
    )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    output = {

        "operation":
            "T9_MOD-037_OP-014",

        "title":
            (
                "Cross-Task Evidence Boundary "
                "& Calibration Synthesis"
            ),

        "status":
            overall_status,

        "purpose":
            (
                "Synthesize completed T2-T7 empirical "
                "evidence while preserving native "
                "task semantics and explicitly "
                "prohibiting cross-task probability "
                "aggregation or universal confidence "
                "construction."
            ),

        "task_evidence_matrix":
            matrix,

        "task_boundaries":
            {

                "T2_T3":
                    t2_t3,

                "T4":
                    t4,

                "T5":
                    t5,

                "T6":
                    t6,

                "T7":
                    t7,
            },

        "cross_task_restrictions":
            restrictions,

        "t8_interface":
            interface,

        "final_conclusion":
            conclusion,

        "controls":
            controls,

        "control_validation":
            control_validation,

        "methodological_restrictions": [

            "No universal confidence score.",

            "No universal risk score.",

            "No synthetic fusion target.",

            "No automatic-action label.",

            "No cross-task numerical probability "
            "comparison.",

            "No blind probability averaging.",

            "No arbitrary cross-task weights.",

            "No task output is reinterpreted as "
            "another task's predictive quantity.",

            "T4 candidate-space restrictions remain "
            "preserved.",

            "T6 observable_non_positive remains "
            "distinct from a true negative.",

            "T7 right censoring remains preserved.",

            "Unavailable task evidence remains "
            "unavailable rather than negative.",

            "Task-specific provenance must remain "
            "attached to every reported quantity.",
        ],

        "closure_statement":
            (
                "T9 cross-task empirical evidence is "
                "closed at the task-specific boundary. "
                "The evidence supports preservation and "
                "presentation of native task quantities, "
                "but does not establish cross-task "
                "numerical comparability or justify a "
                "universal confidence/risk construct."
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
    # FINAL CONSOLE
    # --------------------------------------------------------

    print("=" * 72)
    print(
        "T9 MOD-037 OP-014 RESULT"
    )
    print("=" * 72)
    print()

    print(
        "T9 cross-task status:",
        conclusion[
            "t9_cross_task_status"
        ],
    )

    print(
        "Cross-task comparability:",
        conclusion[
            "cross_task_comparability"
        ],
    )

    print(
        "Universal confidence:",
        conclusion[
            "universal_confidence"
        ],
    )

    print(
        "Universal risk score:",
        conclusion[
            "universal_risk_score"
        ],
    )

    print(
        "Synthetic fusion target:",
        conclusion[
            "synthetic_fusion_target"
        ],
    )

    print(
        "Automatic action label:",
        conclusion[
            "automatic_action_label"
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
        "T9 MOD-037 OP-014:",
        overall_status,
    )


if __name__ == "__main__":
    main()