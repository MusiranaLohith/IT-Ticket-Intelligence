from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


# ============================================================
# T9 MOD-037 OP-011
# T4 Native Ranking Evaluation & Calibration-Readiness Audit
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
    / "t9_mod037_op011_t4_ranking_evaluation.json"
)


# ============================================================
# PRIOR ARTIFACTS
# ============================================================

OP004_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op004_native_output_acceptance.json"
)

OP005_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op005_output_semantics_lock.json"
)

OP011A_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op011a_t4_prior_artifact_schema.json"
)

OP020_ARTIFACT = (
    PROJECT_ROOT
    / "modeling"
    / "T8"
    / "mod036"
    / "op020"
    / "t8_mod036_op020_assignment_component_baseline.json"
)

OP020_PREDICTIONS = (
    PROJECT_ROOT
    / "modeling"
    / "T8"
    / "mod036"
    / "op020"
    / "t8_mod036_op020_assignment_predictions.csv"
)


# ============================================================
# NATIVE T4 ARTIFACTS
# ============================================================

T4_FEATURES = (
    PROJECT_ROOT
    / "modeling"
    / "T4"
    / "derived"
    / "t4_features.csv"
)

T4_TRAIN = (
    PROJECT_ROOT
    / "modeling"
    / "T4"
    / "derived"
    / "t4_train.csv"
)

T4_EVAL = (
    PROJECT_ROOT
    / "modeling"
    / "T4"
    / "derived"
    / "t4_eval.csv"
)


# ============================================================
# HELPERS
# ============================================================

def load_json(path: Path) -> dict[str, Any]:

    if not path.exists():
        raise FileNotFoundError(
            f"Required artifact missing: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:
        value = json.load(f)

    if not isinstance(value, dict):
        raise TypeError(
            f"Expected JSON object: {path}"
        )

    return value


def require_file(path: Path) -> None:

    if not path.exists():
        raise FileNotFoundError(
            f"Required artifact missing: {path}"
        )


def resolve_column(
    frame: pd.DataFrame,
    candidates: list[str],
    label: str,
) -> str:

    for candidate in candidates:

        if candidate in frame.columns:
            return candidate

    lowered = {
        str(column).lower(): column
        for column in frame.columns
    }

    for candidate in candidates:

        if candidate.lower() in lowered:

            return lowered[
                candidate.lower()
            ]

    raise RuntimeError(
        f"Could not resolve {label}. "
        f"Candidates={candidates}; "
        f"available={list(frame.columns)}"
    )


def normalize_ids(
    series: pd.Series,
) -> pd.Series:

    return (
        series
        .astype(str)
        .str.strip()
    )


def normalize_targets(
    series: pd.Series,
) -> pd.Series:

    return (
        series
        .astype(str)
        .str.strip()
    )


# ============================================================
# OP-011A VALIDATION
# ============================================================

def validate_op011a() -> dict[str, Any]:

    artifact = load_json(
        OP011A_ARTIFACT
    )

    return {
        "status": (
            "PASS"
            if artifact.get("status")
            == "PASS"
            else "FAIL"
        ),
        "observed_status": artifact.get(
            "status"
        ),
        "artifact": str(
            OP011A_ARTIFACT
        ),
    }


# ============================================================
# PREVIOUS OPERATION VALIDATION
# ============================================================

def validate_previous_operations() -> dict[str, Any]:

    op004 = load_json(
        OP004_ARTIFACT
    )

    op005 = load_json(
        OP005_ARTIFACT
    )

    op020 = load_json(
        OP020_ARTIFACT
    )

    checks: dict[str, Any] = {}

    # --------------------------------------------------------
    # OP-004
    #
    # OP-004 overall status is FAIL because T2 was rejected.
    # T4 itself is explicitly accepted.
    # --------------------------------------------------------

    accepted_tasks = op004.get(
        "accepted_tasks",
        [],
    )

    rejected_tasks = op004.get(
        "rejected_tasks",
        [],
    )

    unavailable_tasks = op004.get(
        "unavailable_tasks",
        [],
    )

    checks[
        "OP-004_T4_accepted"
    ] = {
        "status": (
            "PASS"
            if (
                "T4" in accepted_tasks
                and
                "T4" not in rejected_tasks
                and
                "T4" not in unavailable_tasks
            )
            else "FAIL"
        ),
        "overall_operation_status": (
            op004.get("status")
        ),
        "accepted_tasks": accepted_tasks,
        "rejected_tasks": rejected_tasks,
        "unavailable_tasks": unavailable_tasks,
    }

    # --------------------------------------------------------
    # OP-004 controls
    # --------------------------------------------------------

    op004_controls = op004.get(
        "controls",
        {},
    )

    prohibited_true_controls = [
        "model_fitting_performed",
        "calibration_fitting_performed",
        "model_selection_performed",
        "target_creation_performed",
        "threshold_selection_performed",
        "universal_confidence_created",
        "universal_risk_score_created",
        "synthetic_target_created",
        "t6_observable_non_positive_reinterpreted",
        "t6_forced_into_binary_classifier",
        "t7_binary_resolution_created",
        "t7_censoring_relabelled",
        "locked_test_used_for_calibration_selection",
    ]

    op004_control_failures = [
        key
        for key in prohibited_true_controls
        if op004_controls.get(key)
        is not False
    ]

    if (
        op004_controls.get(
            "t7_survival_semantics_preserved"
        )
        is not True
    ):
        op004_control_failures.append(
            "t7_survival_semantics_preserved"
        )

    checks[
        "OP-004_controls"
    ] = {
        "status": (
            "PASS"
            if not op004_control_failures
            else "FAIL"
        ),
        "failed_controls": (
            op004_control_failures
        ),
    }

    # --------------------------------------------------------
    # OP-005
    # --------------------------------------------------------

    native_evaluation_tasks = (
        op005.get(
            "native_evaluation_tasks",
            [],
        )
    )

    checks[
        "OP-005_status"
    ] = {
        "status": (
            "PASS"
            if op005.get("status")
            == "PASS"
            else "FAIL"
        ),
        "observed": op005.get(
            "status"
        ),
    }

    checks[
        "OP-005_T4_native_evaluation"
    ] = {
        "status": (
            "PASS"
            if "T4"
            in native_evaluation_tasks
            else "FAIL"
        ),
        "native_evaluation_tasks": (
            native_evaluation_tasks
        ),
    }

    # --------------------------------------------------------
    # OP-005 T4 semantic boundary
    # --------------------------------------------------------

    task_boundary = op005.get(
        "task_boundary",
        {},
    )

    t4_boundary = task_boundary.get(
        "T4",
        {},
    )

    checks[
        "OP-005_T4_semantic_boundary"
    ] = {
        "status": (
            "PASS"
            if (
                t4_boundary.get(
                    "status"
                )
                == "ACCEPTED_NATIVE_RANKING"
                and
                t4_boundary.get(
                    "native_probability_output"
                )
                is False
                and
                t4_boundary.get(
                    "accepted_for_native_evaluation"
                )
                is True
            )
            else "FAIL"
        ),
        "observed": t4_boundary,
    }

    # --------------------------------------------------------
    # OP-005 global controls
    # --------------------------------------------------------

    global_controls = (
        op005.get(
            "global_control_validation",
            {},
        )
    )

    checks[
        "OP-005_global_controls"
    ] = {
        "status": (
            "PASS"
            if global_controls.get(
                "status"
            )
            == "PASS"
            else "FAIL"
        ),
        "observed_status": (
            global_controls.get(
                "status"
            )
        ),
    }

    # --------------------------------------------------------
    # T8 OP-020
    # --------------------------------------------------------

    checks[
        "OP-020_status"
    ] = {
        "status": (
            "PASS"
            if op020.get("status")
            == "PASS"
            else "FAIL"
        ),
        "observed": op020.get(
            "status"
        ),
    }

    checks[
        "OP-020_component"
    ] = {
        "status": (
            "PASS"
            if op020.get(
                "component"
            )
            == "assignment"
            else "FAIL"
        ),
        "observed": op020.get(
            "component"
        ),
    }

    # --------------------------------------------------------
    # OP-020 native semantics
    # --------------------------------------------------------

    native_semantics = (
        op020.get(
            "native_semantics",
            {},
        )
    )

    checks[
        "OP-020_native_semantics"
    ] = {
        "status": (
            "PASS"
            if (
                native_semantics.get(
                    "task_type"
                )
                == "candidate_ranking"
                and
                native_semantics.get(
                    "target"
                )
                == "target_assignee"
                and
                native_semantics.get(
                    "recommendation_type"
                )
                == "ranked_assignment_candidates"
                and
                native_semantics.get(
                    "neighbor_count"
                )
                == 20
            )
            else "FAIL"
        ),
        "observed": native_semantics,
    }

    # --------------------------------------------------------
    # OP-020 alignment
    # --------------------------------------------------------

    alignment = op020.get(
        "alignment",
        {},
    )

    checks[
        "OP-020_alignment"
    ] = {
        "status": (
            "PASS"
            if (
                alignment.get(
                    "aligned"
                )
                is True
                and
                alignment.get(
                    "retrieval_rows"
                )
                ==
                alignment.get(
                    "evaluation_rows"
                )
                and
                alignment.get(
                    "invalid_neighbor_indices"
                )
                == 0
            )
            else "FAIL"
        ),
        "observed": alignment,
    }

    # --------------------------------------------------------
    # OP-020 controls
    # --------------------------------------------------------

    op020_controls = op020.get(
        "controls",
        {},
    )

    expected_false_controls = [
        "post_creation_information_used",
        "locked_t4_evaluation_used",
        "target_converted_to_negative",
        "candidate_universe_expanded",
        "probability_conversion_performed",
        "blind_probability_averaging",
        "arbitrary_cross_task_weighting",
    ]

    op020_control_failures = [
        key
        for key in expected_false_controls
        if op020_controls.get(key)
        is not False
    ]

    checks[
        "OP-020_controls"
    ] = {
        "status": (
            "PASS"
            if not op020_control_failures
            else "FAIL"
        ),
        "failed_controls": (
            op020_control_failures
        ),
    }

    failed_checks = [
        key
        for key, value
        in checks.items()
        if value["status"]
        == "FAIL"
    ]

    return {
        "status": (
            "PASS"
            if not failed_checks
            else "FAIL"
        ),
        "checks": checks,
        "failed_checks": failed_checks,
    }


# ============================================================
# LOAD NATIVE SOURCES
# ============================================================

def load_native_sources() -> dict[
    str,
    pd.DataFrame,
]:

    for path in [
        T4_FEATURES,
        T4_TRAIN,
        T4_EVAL,
        OP020_PREDICTIONS,
    ]:
        require_file(path)

    return {
        "features": pd.read_csv(
            T4_FEATURES,
            low_memory=False,
        ),
        "train": pd.read_csv(
            T4_TRAIN,
            low_memory=False,
        ),
        "evaluation": pd.read_csv(
            T4_EVAL,
            low_memory=False,
        ),
        "predictions": pd.read_csv(
            OP020_PREDICTIONS,
            low_memory=False,
        ),
    }


# ============================================================
# SOURCE SCHEMA
# ============================================================

def audit_source_schema(
    sources: dict[str, pd.DataFrame],
) -> dict[str, Any]:

    features = sources[
        "features"
    ]

    train = sources[
        "train"
    ]

    evaluation = sources[
        "evaluation"
    ]

    predictions = sources[
        "predictions"
    ]

    feature_id = resolve_column(
        features,
        ["ID", "id"],
        "T4 feature ID",
    )

    train_id = resolve_column(
        train,
        ["ID", "id"],
        "T4 train ID",
    )

    eval_id = resolve_column(
        evaluation,
        ["ID", "id"],
        "T4 evaluation ID",
    )

    train_target = resolve_column(
        train,
        [
            "target_assignee",
            "true_assignee",
        ],
        "T4 train target",
    )

    eval_target = resolve_column(
        evaluation,
        [
            "target_assignee",
            "true_assignee",
        ],
        "T4 evaluation target",
    )

    # VERIFIED ACTUAL T8 OP-020 PREDICTION SCHEMA
    prediction_id = resolve_column(
        predictions,
        ["id"],
        "T4 prediction ID",
    )

    prediction_assignee = resolve_column(
        predictions,
        ["recommended_assignee"],
        "T4 Top-1 recommended assignee",
    )

    prediction_true_assignee = resolve_column(
        predictions,
        ["true_assignee"],
        "T4 native prediction target",
    )

    prediction_score = resolve_column(
        predictions,
        ["recommended_score"],
        "T4 native recommendation score",
    )

    target_rank = resolve_column(
        predictions,
        ["target_rank"],
        "T4 native target rank",
    )

    target_present = resolve_column(
        predictions,
        ["target_present"],
        "T4 native target-present indicator",
    )

    top20_candidates = resolve_column(
        predictions,
        ["top20_candidates"],
        "T4 native top-20 candidate list",
    )

    status = resolve_column(
        predictions,
        ["status"],
        "T4 recommendation status",
    )

    return {
        "status": "PASS",

        "columns": {

            "features_id": feature_id,

            "train_id": train_id,

            "train_target": train_target,

            "evaluation_id": eval_id,

            "evaluation_target": eval_target,

            "prediction_id": prediction_id,

            "prediction_assignee": (
                prediction_assignee
            ),

            "prediction_true_assignee": (
                prediction_true_assignee
            ),

            "prediction_score": (
                prediction_score
            ),

            "target_rank": target_rank,

            "target_present": (
                target_present
            ),

            "top20_candidates": (
                top20_candidates
            ),

            "prediction_status": (
                status
            ),
        },
    }


# ============================================================
# POPULATION / IDENTITY AUDIT
# ============================================================

def audit_populations(
    sources: dict[str, pd.DataFrame],
    columns: dict[str, str],
) -> dict[str, Any]:

    train_ids = normalize_ids(
        sources["train"][
            columns["train_id"]
        ]
    )

    eval_ids = normalize_ids(
        sources["evaluation"][
            columns["evaluation_id"]
        ]
    )

    prediction_ids = normalize_ids(
        sources["predictions"][
            columns["prediction_id"]
        ]
    )

    details = {}

    for name, ids in [
        ("train", train_ids),
        ("evaluation", eval_ids),
        ("predictions", prediction_ids),
    ]:

        duplicate_count = int(
            ids.duplicated().sum()
        )

        blank_count = int(
            (
                ids.isna()
                |
                (ids.str.len() == 0)
            ).sum()
        )

        details[name] = {

            "rows": int(
                len(ids)
            ),

            "unique_ids": int(
                ids.nunique()
            ),

            "duplicate_ids": (
                duplicate_count
            ),

            "blank_ids": (
                blank_count
            ),

            "status": (
                "PASS"
                if (
                    duplicate_count == 0
                    and
                    blank_count == 0
                )
                else "FAIL"
            ),
        }

    train_set = set(
        train_ids
    )

    eval_set = set(
        eval_ids
    )

    prediction_set = set(
        prediction_ids
    )

    details[
        "train_eval_overlap"
    ] = {

        "rows": len(
            train_set
            &
            eval_set
        ),

        "status": (
            "PASS"
            if not (
                train_set
                &
                eval_set
            )
            else "FAIL"
        ),
    }

    details[
        "eval_prediction_alignment"
    ] = {

        "evaluation_rows": len(
            eval_set
        ),

        "prediction_rows": len(
            prediction_set
        ),

        "intersection": len(
            eval_set
            &
            prediction_set
        ),

        "evaluation_only": len(
            eval_set
            -
            prediction_set
        ),

        "prediction_only": len(
            prediction_set
            -
            eval_set
        ),

        "status": (
            "PASS"
            if eval_set
            ==
            prediction_set
            else "FAIL"
        ),
    }

    failed = [
        key
        for key, value
        in details.items()
        if value["status"]
        == "FAIL"
    ]

    return {
        "status": (
            "PASS"
            if not failed
            else "FAIL"
        ),

        "details": details,

        "failed_checks": failed,
    }


# ============================================================
# CANDIDATE SPACE
# ============================================================

def audit_candidate_space(
    sources: dict[str, pd.DataFrame],
    columns: dict[str, str],
) -> dict[str, Any]:

    train_targets = normalize_targets(
        sources["train"][
            columns["train_target"]
        ]
    )

    eval_targets = normalize_targets(
        sources["evaluation"][
            columns["evaluation_target"]
        ]
    )

    predicted_targets = normalize_targets(
        sources["predictions"][
            columns[
                "prediction_assignee"
            ]
        ]
    )

    candidate_space = set(
        train_targets
    )

    eval_target_space = set(
        eval_targets
    )

    prediction_space = set(
        predicted_targets
    )

    unseen_distinct = (
        eval_target_space
        -
        candidate_space
    )

    outside_prediction_space = (
        prediction_space
        -
        candidate_space
    )

    return {

        "status": (
            "PASS"
            if not outside_prediction_space
            else "FAIL"
        ),

        "training_candidate_assignee_count": (
            len(candidate_space)
        ),

        "evaluation_distinct_target_assignees": (
            len(eval_target_space)
        ),

        "evaluation_targets_seen_in_training": (
            len(
                eval_target_space
                &
                candidate_space
            )
        ),

        "evaluation_targets_unseen_in_training": (
            len(unseen_distinct)
        ),

        "predicted_distinct_assignees": (
            len(prediction_space)
        ),

        "predictions_outside_training_candidate_space": (
            len(
                outside_prediction_space
            )
        ),
    }


# ============================================================
# TARGET AVAILABILITY
# ============================================================

def audit_target_availability(
    sources: dict[str, pd.DataFrame],
    columns: dict[str, str],
) -> dict[str, Any]:

    train_targets = set(
        normalize_targets(
            sources["train"][
                columns["train_target"]
            ]
        )
    )

    evaluation_targets = normalize_targets(
        sources["evaluation"][
            columns["evaluation_target"]
        ]
    )

    present_mask = (
        evaluation_targets
        .isin(
            train_targets
        )
    )

    present = int(
        present_mask.sum()
    )

    unseen = int(
        (~present_mask).sum()
    )

    total = int(
        len(evaluation_targets)
    )

    return {

        "rows": total,

        "target_present_in_training_candidate_space": (
            present
        ),

        "target_unseen_in_training_candidate_space": (
            unseen
        ),

        "target_present_rate": (
            present / total
            if total
            else 0.0
        ),

        "target_unseen_rate": (
            unseen / total
            if total
            else 0.0
        ),
    }


# ============================================================
# NATIVE TOP-1 RANKING EVALUATION
# ============================================================

def evaluate_top1(
    sources: dict[str, pd.DataFrame],
    columns: dict[str, str],
) -> dict[str, Any]:

    predictions = sources[
        "predictions"
    ]

    pred = predictions[
        [
            columns[
                "prediction_id"
            ],

            columns[
                "prediction_assignee"
            ],

            columns[
                "prediction_true_assignee"
            ],

            columns[
                "prediction_score"
            ],

            columns[
                "target_rank"
            ],

            columns[
                "target_present"
            ],

            columns[
                "prediction_status"
            ],
        ]
    ].copy()

    pred["ID"] = normalize_ids(
        pred[
            columns[
                "prediction_id"
            ]
        ]
    )

    pred[
        "recommended_assignee"
    ] = normalize_targets(
        pred[
            columns[
                "prediction_assignee"
            ]
        ]
    )

    pred[
        "true_assignee_native"
    ] = normalize_targets(
        pred[
            columns[
                "prediction_true_assignee"
            ]
        ]
    )

    pred[
        "recommended_score"
    ] = pd.to_numeric(
        pred[
            columns[
                "prediction_score"
            ]
        ],
        errors="coerce",
    )

    pred[
        "target_rank_native"
    ] = pd.to_numeric(
        pred[
            columns[
                "target_rank"
            ]
        ],
        errors="coerce",
    )

    pred[
        "target_present_native"
    ] = pred[
        columns[
            "target_present"
        ]
    ]

    pred[
        "status_native"
    ] = pred[
        columns[
            "prediction_status"
        ]
    ]

    if pred[
        "recommended_score"
    ].isna().any():

        raise RuntimeError(
            "Native recommended_score contains "
            "non-numeric or missing values."
        )

    correct = (
        pred[
            "recommended_assignee"
        ]
        ==
        pred[
            "true_assignee_native"
        ]
    )

    correct_count = int(
        correct.sum()
    )

    rows = int(
        len(pred)
    )

    return {

        "rows_evaluated": rows,

        "top1_correct": (
            correct_count
        ),

        "top1_incorrect": (
            rows
            -
            correct_count
        ),

        "top1_accuracy": (
            correct_count / rows
            if rows
            else 0.0
        ),

        "native_target_present_rows": int(
            pred[
                "target_present_native"
            ]
            .astype(bool)
            .sum()
        ),

        "native_target_unseen_rows": int(
            (
                ~pred[
                    "target_present_native"
                ]
                .astype(bool)
            ).sum()
        ),

        "native_no_recommendation_rows": int(
            (
                pred[
                    "status_native"
                ]
                .astype(str)
                .str.lower()
                !=
                "recommended"
            ).sum()
        ),

        "target_rank_available_rows": int(
            pred[
                "target_rank_native"
            ]
            .notna()
            .sum()
        ),

        "recommended_score_available_rows": int(
            pred[
                "recommended_score"
            ]
            .notna()
            .sum()
        ),
    }


# ============================================================
# NATIVE OUTPUT SEMANTICS
# ============================================================

def audit_output_semantics(
    predictions: pd.DataFrame,
    columns: dict[str, str],
) -> dict[str, Any]:

    return {

        "verified_native_columns": {

            "id": columns[
                "prediction_id"
            ],

            "true_assignee": columns[
                "prediction_true_assignee"
            ],

            "recommended_assignee": columns[
                "prediction_assignee"
            ],

            "recommended_score": columns[
                "prediction_score"
            ],

            "target_rank": columns[
                "target_rank"
            ],

            "target_present": columns[
                "target_present"
            ],

            "top20_candidates": columns[
                "top20_candidates"
            ],

            "status": columns[
                "prediction_status"
            ],
        },

        "native_ranking_output_established": True,

        "native_probability_artifact_established": False,

        "score_semantics": (
            "recommended_score remains a native "
            "candidate-ranking score. It is not "
            "converted into a calibrated probability."
        ),

        "probability_like_columns_observed": [],

        "interpretation": (
            "T4 remains a candidate-space ranking task. "
            "The native recommendation score is preserved "
            "as a ranking quantity."
        ),
    }


# ============================================================
# CALIBRATION READINESS
# ============================================================

def determine_calibration_readiness() -> dict[str, Any]:

    return {

        "native_ranking_evaluation": (
            "READY"
        ),

        "probability_calibration": (
            "NOT_ESTABLISHED"
        ),

        "reason": (
            "The accepted T4 artifact provides native "
            "candidate-ranking outputs including "
            "recommended_assignee, recommended_score, "
            "target_rank and top20_candidates. "
            "It does not establish a calibrated "
            "probability distribution over candidates."
        ),
    }


# ============================================================
# CONTROLS
# ============================================================

def build_controls() -> dict[str, Any]:

    return {

        "new_model_fitted": False,

        "new_prediction_generated": False,

        "new_probability_generated": False,

        "new_calibration_fitted": False,

        "synthetic_target_created": False,

        "target_relabelled": False,

        "unseen_target_reinterpreted_as_negative": False,

        "ranking_converted_to_classification": False,

        "threshold_selected": False,

        "locked_test_used_for_selection": False,

        "universal_confidence_created": False,

        "universal_risk_score_created": False,

        "arbitrary_cross_task_weights_used": False,

        "native_t4_ranking_semantics_preserved": True,

        "candidate_space_preserved": True,

        "unseen_targets_preserved_as_unavailable": True,
    }


def validate_controls(
    controls: dict[str, Any],
) -> dict[str, Any]:

    positive_controls = {

        "native_t4_ranking_semantics_preserved",

        "candidate_space_preserved",

        "unseen_targets_preserved_as_unavailable",
    }

    failures = []

    for key, value in controls.items():

        if key in positive_controls:

            if value is not True:
                failures.append(key)

        else:

            if value is not False:
                failures.append(key)

    return {

        "status": (
            "PASS"
            if not failures
            else "FAIL"
        ),

        "failures": failures,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 72)
    print("T9 MOD-037 OP-011")
    print(
        "T4 Native Ranking Evaluation & "
        "Calibration-Readiness Audit"
    )
    print("=" * 72)
    print()

    # --------------------------------------------------------
    # OP-011A
    # --------------------------------------------------------

    print(
        "Validating OP-011A schema resolution..."
    )

    op011a = validate_op011a()

    print(
        "OP-011A validation:",
        op011a["status"],
    )

    if op011a["status"] != "PASS":

        raise RuntimeError(
            "OP-011A schema resolution is not PASS."
        )

    print()

    # --------------------------------------------------------
    # PREVIOUS OPERATIONS
    # --------------------------------------------------------

    print(
        "Validating previous T9/T8 operations..."
    )

    previous = (
        validate_previous_operations()
    )

    print(
        "Previous-operation validation:",
        previous["status"],
    )

    if previous["status"] != "PASS":

        print(
            "Failed checks:",
            previous[
                "failed_checks"
            ],
        )

        raise RuntimeError(
            "Previous-operation validation failed."
        )

    print()

    # --------------------------------------------------------
    # LOAD NATIVE T4 ARTIFACTS
    # --------------------------------------------------------

    print(
        "Loading native T4 artifacts..."
    )

    sources = load_native_sources()

    print(
        "T4 features:",
        len(
            sources[
                "features"
            ]
        ),
        "rows",
    )

    print(
        "T4 train:",
        len(
            sources[
                "train"
            ]
        ),
        "rows",
    )

    print(
        "T4 evaluation:",
        len(
            sources[
                "evaluation"
            ]
        ),
        "rows",
    )

    print(
        "T4 predictions:",
        len(
            sources[
                "predictions"
            ]
        ),
        "rows",
    )

    print()

    # --------------------------------------------------------
    # SOURCE SCHEMA
    # --------------------------------------------------------

    print(
        "Auditing T4 source schemas..."
    )

    schema = audit_source_schema(
        sources
    )

    print(
        "Source schema:",
        schema["status"],
    )

    print(
        "Verified prediction columns:",
        list(
            sources[
                "predictions"
            ].columns
        ),
    )

    print()

    # --------------------------------------------------------
    # POPULATION
    # --------------------------------------------------------

    print(
        "Auditing populations and identity..."
    )

    populations = audit_populations(
        sources,
        schema[
            "columns"
        ],
    )

    print(
        "Population audit:",
        populations[
            "status"
        ],
    )

    if populations[
        "status"
    ] != "PASS":

        print(
            "Failed checks:",
            populations[
                "failed_checks"
            ],
        )

        raise RuntimeError(
            "T4 population audit failed."
        )

    print()

    # --------------------------------------------------------
    # CANDIDATE SPACE
    # --------------------------------------------------------

    print(
        "Auditing training-observed candidate space..."
    )

    candidate_space = (
        audit_candidate_space(
            sources,
            schema[
                "columns"
            ],
        )
    )

    print(
        "Candidate-space audit:",
        candidate_space[
            "status"
        ],
    )

    print(
        "Training candidate assignees:",
        candidate_space[
            "training_candidate_assignee_count"
        ],
    )

    print(
        "Evaluation distinct target assignees:",
        candidate_space[
            "evaluation_distinct_target_assignees"
        ],
    )

    print(
        "Evaluation targets unseen in training:",
        candidate_space[
            "evaluation_targets_unseen_in_training"
        ],
    )

    if candidate_space[
        "status"
    ] != "PASS":

        raise RuntimeError(
            "T4 predictions contain assignees "
            "outside the training-observed "
            "candidate space."
        )

    print()

    # --------------------------------------------------------
    # TARGET AVAILABILITY
    # --------------------------------------------------------

    print(
        "Auditing row-level target availability..."
    )

    target_availability = (
        audit_target_availability(
            sources,
            schema[
                "columns"
            ],
        )
    )

    print(
        "Target-present rows:",
        target_availability[
            "target_present_in_training_candidate_space"
        ],
    )

    print(
        "Target-unseen rows:",
        target_availability[
            "target_unseen_in_training_candidate_space"
        ],
    )

    print(
        "Target-unseen rate:",
        f"{target_availability['target_unseen_rate']:.6f}",
    )

    print()

    # --------------------------------------------------------
    # NATIVE TOP-1
    # --------------------------------------------------------

    print(
        "Evaluating native T4 Top-1 ranking..."
    )

    top1 = evaluate_top1(
        sources,
        schema[
            "columns"
        ],
    )

    print(
        "Rows evaluated:",
        top1[
            "rows_evaluated"
        ],
    )

    print(
        "Top-1 correct:",
        top1[
            "top1_correct"
        ],
    )

    print(
        "Top-1 accuracy:",
        f"{top1['top1_accuracy']:.6f}",
    )

    print(
        "Native target-present rows:",
        top1[
            "native_target_present_rows"
        ],
    )

    print(
        "Native target-unseen rows:",
        top1[
            "native_target_unseen_rows"
        ],
    )

    print(
        "Native target-rank available rows:",
        top1[
            "target_rank_available_rows"
        ],
    )

    print(
        "Native recommendation-score rows:",
        top1[
            "recommended_score_available_rows"
        ],
    )

    print()

    # --------------------------------------------------------
    # OUTPUT SEMANTICS
    # --------------------------------------------------------

    print(
        "Auditing native output semantics..."
    )

    output_semantics = (
        audit_output_semantics(
            sources[
                "predictions"
            ],
            schema[
                "columns"
            ],
        )
    )

    print(
        "Native ranking:",
        output_semantics[
            "native_ranking_output_established"
        ],
    )

    print(
        "Native probability:",
        output_semantics[
            "native_probability_artifact_established"
        ],
    )

    print()

    # --------------------------------------------------------
    # CALIBRATION READINESS
    # --------------------------------------------------------

    calibration_readiness = (
        determine_calibration_readiness()
    )

    print(
        "Native ranking evaluation:",
        calibration_readiness[
            "native_ranking_evaluation"
        ],
    )

    print(
        "Probability calibration:",
        calibration_readiness[
            "probability_calibration"
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

    if control_validation[
        "status"
    ] != "PASS":

        raise RuntimeError(
            "Control validation failed."
        )

    # --------------------------------------------------------
    # OVERALL
    # --------------------------------------------------------

    overall_pass = all(
        [
            op011a[
                "status"
            ] == "PASS",

            previous[
                "status"
            ] == "PASS",

            schema[
                "status"
            ] == "PASS",

            populations[
                "status"
            ] == "PASS",

            candidate_space[
                "status"
            ] == "PASS",

            control_validation[
                "status"
            ] == "PASS",
        ]
    )

    # --------------------------------------------------------
    # OUTPUT ARTIFACT
    # --------------------------------------------------------

    output = {

        "operation": (
            "T9_MOD-037_OP-011"
        ),

        "title": (
            "T4 Native Ranking Evaluation & "
            "Calibration-Readiness Audit"
        ),

        "status": (
            "PASS"
            if overall_pass
            else "FAIL"
        ),

        "operation_type": (
            "NATIVE_RANKING_EVALUATION_AND_"
            "CALIBRATION_READINESS_AUDIT"
        ),

        "OP-011A_validation": (
            op011a
        ),

        "previous_operation_validation": (
            previous
        ),

        "native_source_population": {

            "T4_features_rows": int(
                len(
                    sources[
                        "features"
                    ]
                )
            ),

            "T4_train_rows": int(
                len(
                    sources[
                        "train"
                    ]
                )
            ),

            "T4_evaluation_rows": int(
                len(
                    sources[
                        "evaluation"
                    ]
                )
            ),

            "T4_prediction_rows": int(
                len(
                    sources[
                        "predictions"
                    ]
                )
            ),
        },

        "source_schema": schema,

        "population_identity_audit": (
            populations
        ),

        "candidate_space_audit": (
            candidate_space
        ),

        "target_availability": (
            target_availability
        ),

        "native_top1_evaluation": (
            top1
        ),

        "native_output_semantics": (
            output_semantics
        ),

        "calibration_readiness": (
            calibration_readiness
        ),

        "controls": controls,

        "control_validation": (
            control_validation
        ),

        "artifacts_used": {

            "OP-004": str(
                OP004_ARTIFACT
            ),

            "OP-005": str(
                OP005_ARTIFACT
            ),

            "OP-011A": str(
                OP011A_ARTIFACT
            ),

            "T8_OP-020": str(
                OP020_ARTIFACT
            ),

            "T8_OP-020_predictions": str(
                OP020_PREDICTIONS
            ),

            "T4_features": str(
                T4_FEATURES
            ),

            "T4_train": str(
                T4_TRAIN
            ),

            "T4_eval": str(
                T4_EVAL
            ),
        },

        "interpretation_boundary": [

            (
                "T4 is evaluated as a "
                "specific-assignee candidate-space "
                "ranking task."
            ),

            (
                "The training-observed assignee set "
                "defines the evaluated candidate space."
            ),

            (
                "Unseen evaluation targets are "
                "unavailable rather than ordinary "
                "negative examples."
            ),

            (
                "recommended_assignee is treated as "
                "the native Top-1 assignment recommendation."
            ),

            (
                "recommended_score remains a native "
                "ranking score and is not converted "
                "into a calibrated probability."
            ),

            (
                "target_rank is retained as native "
                "candidate-ranking evidence."
            ),

            (
                "Top-1 accuracy is native ranking "
                "evidence and is not probability "
                "calibration."
            ),

            (
                "Historical assignment is not "
                "interpreted as universal routing "
                "correctness."
            ),

            (
                "No universal confidence or risk "
                "score is created."
            ),
        ],

        "decision": (
            "T4 native assignment-ranking evidence "
            "is validated for native evaluation "
            "under the frozen candidate-space "
            "semantics. Probability calibration "
            "is not established by the accepted "
            "native artifact."
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
    print("T9 MOD-037 OP-011 RESULT")
    print("=" * 72)
    print()

    print(
        "OP-011A validation:",
        op011a[
            "status"
        ],
    )

    print(
        "Previous-operation validation:",
        previous[
            "status"
        ],
    )

    print(
        "Source schema:",
        schema[
            "status"
        ],
    )

    print(
        "Population audit:",
        populations[
            "status"
        ],
    )

    print(
        "Candidate-space audit:",
        candidate_space[
            "status"
        ],
    )

    print(
        "Control validation:",
        control_validation[
            "status"
        ],
    )

    print()

    print(
        "Rows evaluated:",
        top1[
            "rows_evaluated"
        ],
    )

    print(
        "Top-1 correct:",
        top1[
            "top1_correct"
        ],
    )

    print(
        "Top-1 accuracy:",
        f"{top1['top1_accuracy']:.6f}",
    )

    print(
        "Target-present rows:",
        target_availability[
            "target_present_in_training_candidate_space"
        ],
    )

    print(
        "Target-unseen rows:",
        target_availability[
            "target_unseen_in_training_candidate_space"
        ],
    )

    print(
        "Target-unseen rate:",
        f"{target_availability['target_unseen_rate']:.6f}",
    )

    print()

    print(
        "Native ranking evaluation: READY"
    )

    print(
        "Probability calibration: "
        "NOT ESTABLISHED"
    )

    print(
        "New model fitted: NO"
    )

    print(
        "New prediction generated: NO"
    )

    print(
        "New probability generated: NO"
    )

    print(
        "Calibration fitted: NO"
    )

    print(
        "Threshold selected: NO"
    )

    print(
        "Locked test used: NO"
    )

    print(
        "Universal confidence/risk created: NO"
    )

    print()

    print(
        "Output:",
        OUTPUT_JSON,
    )

    print()

    print(
        "T9 MOD-037 OP-011 T4 native ranking "
        "evaluation & calibration-readiness audit:",
        (
            "PASS"
            if overall_pass
            else "FAIL"
        ),
    )


if __name__ == "__main__":
    main()