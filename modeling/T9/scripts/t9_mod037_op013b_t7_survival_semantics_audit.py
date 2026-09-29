from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


# ============================================================
# T9 MOD-037 OP-013B
# T7 Event / Censoring / Native Survival Output Semantic Audit
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

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
    / "t9_mod037_op013b_t7_survival_semantics_audit.json"
)


# ============================================================
# T9 PRIOR ARTIFACTS
# ============================================================

OP004_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op004_native_output_acceptance.json"
)

OP005_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op005_output_semantics_lock.json"
)

OP013A_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op013a_t7_prior_artifact_schema.json"
)


# ============================================================
# T7 SOURCE ARTIFACTS
# ============================================================

T7_ROOT = (
    PROJECT_ROOT
    / "modeling"
    / "T7"
)

T7_CONTRACT = (
    T7_ROOT
    / "contracts"
    / "t7_modeling_contract.json"
)

T7_TRAIN = (
    T7_ROOT
    / "splits"
    / "t7_train.csv"
)

T7_EVAL = (
    T7_ROOT
    / "splits"
    / "t7_evaluation.csv"
)

T7_MOD007_PREDICTIONS = (
    T7_ROOT
    / "derived"
    / "t7_mod007_evaluation_predictions.csv"
)

T7_MOD010_PREDICTIONS = (
    T7_ROOT
    / "derived"
    / "t7_mod010_evaluation_predictions.csv"
)

T7_MOD007_AUDIT = (
    T7_ROOT
    / "metrics"
    / "t7_mod007_predictive_survival_audit.json"
)

T7_MOD008_AUDIT = (
    T7_ROOT
    / "metrics"
    / "t7_mod008_predictive_vs_reference_audit.json"
)

T7_MOD009_AUDIT = (
    T7_ROOT
    / "metrics"
    / "t7_mod009_survival_calibration_audit.json"
)

T7_MOD012_CLOSURE = (
    T7_ROOT
    / "metrics"
    / "t7_mod012_final_closure.json"
)


# ============================================================
# HELPERS
# ============================================================

def require_file(
    path: Path,
) -> None:

    if not path.exists():

        raise FileNotFoundError(
            f"Required artifact missing: {path}"
        )


def load_json(
    path: Path,
) -> dict[str, Any]:

    require_file(path)

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        value = json.load(f)

    if not isinstance(
        value,
        dict,
    ):

        raise TypeError(
            f"Expected JSON object: {path}"
        )

    return value


def normalize_columns(
    frame: pd.DataFrame,
) -> pd.DataFrame:

    frame = frame.copy()

    frame.columns = [
        str(column).strip()
        for column in frame.columns
    ]

    return frame


def find_id_column(
    frame: pd.DataFrame,
) -> str | None:

    preferred = [
        "id",
        "ticket_id",
        "issue_id",
        "bug_id",
        "row_id",
    ]

    for column in preferred:

        if column in frame.columns:

            return column

    candidates = [
        column
        for column in frame.columns
        if "id" in column.lower()
    ]

    if candidates:

        return candidates[0]

    return None


# ============================================================
# FROZEN T9 BOUNDARY
# ============================================================

def validate_t9_boundary() -> dict[str, Any]:

    op004 = load_json(
        OP004_ARTIFACT
    )

    op005 = load_json(
        OP005_ARTIFACT
    )

    op013a = load_json(
        OP013A_ARTIFACT
    )

    accepted_tasks = op004.get(
        "accepted_tasks",
        [],
    )

    t7_boundary = (
        op005
        .get(
            "task_boundary",
            {},
        )
        .get(
            "T7",
            {},
        )
    )

    checks = {}

    checks[
        "OP-004_T7_acceptance"
    ] = {

        "status": (
            "PASS"
            if "T7" in accepted_tasks
            else "FAIL"
        ),

        "accepted_tasks": accepted_tasks,
    }

    checks[
        "OP-005_T7_boundary"
    ] = {

        "status": (
            "PASS"
            if (
                op005.get(
                    "status"
                )
                == "PASS"
                and
                t7_boundary.get(
                    "status"
                )
                == "ACCEPTED_NATIVE_SURVIVAL"
                and
                t7_boundary.get(
                    "accepted_for_calibration"
                )
                is True
            )
            else "FAIL"
        ),

        "boundary": t7_boundary,
    }

    checks[
        "OP-013A"
    ] = {

        "status": (
            "PASS"
            if op013a.get(
                "status"
            )
            == "PASS"
            else "FAIL"
        ),

        "observed_status": (
            op013a.get(
                "status"
            )
        ),
    }

    failed = [
        key
        for key, value in checks.items()
        if value["status"] != "PASS"
    ]

    return {

        "status": (
            "PASS"
            if not failed
            else "FAIL"
        ),

        "checks": checks,

        "failed_checks": failed,

        "t7_boundary": t7_boundary,
    }


# ============================================================
# CONTRACT AUDIT
# ============================================================

def audit_contract() -> dict[str, Any]:

    contract = load_json(
        T7_CONTRACT
    )

    survival_related = {}

    for key, value in contract.items():

        key_text = str(
            key
        ).lower()

        if any(
            token in key_text
            for token in [
                "survival",
                "censor",
                "event",
                "time",
                "duration",
                "prediction",
                "evaluation",
            ]
        ):

            survival_related[
                key
            ] = value

    contract_text = json.dumps(
        contract,
        ensure_ascii=False,
    ).lower()

    required_terms = {
        "survival": (
            "survival" in contract_text
        ),

        "censoring": (
            "censor" in contract_text
        ),

        "event": (
            "event" in contract_text
        ),

        "duration_or_time": (
            "duration" in contract_text
            or
            "time" in contract_text
        ),
    }

    return {

        "top_level_keys": list(
            contract.keys()
        ),

        "survival_related_fields": (
            survival_related
        ),

        "required_semantic_terms": (
            required_terms
        ),

        "status": (
            "PASS"
            if all(
                required_terms.values()
            )
            else "FAIL"
        ),
    }


# ============================================================
# SPLIT AUDIT
# ============================================================

def load_split(
    path: Path,
    split_name: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:

    require_file(path)

    frame = pd.read_csv(
        path,
        low_memory=False,
    )

    frame = normalize_columns(
        frame
    )

    required_columns = [
        "duration_seconds",
        "event",
    ]

    missing = [
        column
        for column in required_columns
        if column not in frame.columns
    ]

    if missing:

        raise RuntimeError(
            f"{split_name} missing required "
            f"survival columns: {missing}"
        )

    duration = pd.to_numeric(
        frame[
            "duration_seconds"
        ],
        errors="coerce",
    )

    event = pd.to_numeric(
        frame[
            "event"
        ],
        errors="coerce",
    )

    invalid_duration = (
        duration.isna()
        |
        ~np.isfinite(
            duration
        )
        |
        (duration < 0)
    )

    invalid_event = (
        event.isna()
        |
        ~event.isin(
            [0, 1]
        )
    )

    return (

        frame,

        {

            "split": split_name,

            "rows": int(
                len(frame)
            ),

            "columns": list(
                frame.columns
            ),

            "id_column": (
                find_id_column(
                    frame
                )
            ),

            "event_1": int(
                event.eq(1).sum()
            ),

            "event_0": int(
                event.eq(0).sum()
            ),

            "event_rate": float(
                event.eq(1).mean()
            ),

            "censor_rate": float(
                event.eq(0).mean()
            ),

            "duration_min": float(
                duration.min()
            ),

            "duration_max": float(
                duration.max()
            ),

            "duration_median": float(
                duration.median()
            ),

            "invalid_duration_rows": int(
                invalid_duration.sum()
            ),

            "invalid_event_rows": int(
                invalid_event.sum()
            ),

            "status": (
                "PASS"
                if (
                    not invalid_duration.any()
                    and
                    not invalid_event.any()
                )
                else "FAIL"
            ),
        },
    )


# ============================================================
# PREDICTION ARTIFACT AUDIT
# ============================================================

def inspect_prediction_artifact(
    path: Path,
    name: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:

    require_file(path)

    frame = pd.read_csv(
        path,
        low_memory=False,
    )

    frame = normalize_columns(
        frame
    )

    expected_columns = [
        "duration_seconds",
        "event",
        "predicted_median_survival_seconds",
        "survival_probability_at_211583_seconds",
        "survival_probability_at_1780179_seconds",
        "survival_probability_at_14608619_seconds",
    ]

    missing = [
        column
        for column in expected_columns
        if column not in frame.columns
    ]

    prediction_columns = [
        column
        for column in frame.columns
        if (
            "predicted" in column.lower()
            or
            "survival_probability" in column.lower()
        )
    ]

    result = {

        "artifact": str(
            path.relative_to(
                PROJECT_ROOT
            )
        ),

        "rows": int(
            len(frame)
        ),

        "columns": list(
            frame.columns
        ),

        "column_count": len(
            frame.columns
        ),

        "expected_columns_present": (
            len(missing) == 0
        ),

        "missing_expected_columns": missing,

        "prediction_like_columns": (
            prediction_columns
        ),

        "id_column": (
            find_id_column(
                frame
            )
        ),
    }

    if missing:

        result[
            "status"
        ] = "FAIL"

        return frame, result

    duration = pd.to_numeric(
        frame[
            "duration_seconds"
        ],
        errors="coerce",
    )

    event = pd.to_numeric(
        frame[
            "event"
        ],
        errors="coerce",
    )

    median_prediction = pd.to_numeric(
        frame[
            "predicted_median_survival_seconds"
        ],
        errors="coerce",
    )

    horizon_columns = [
        "survival_probability_at_211583_seconds",
        "survival_probability_at_1780179_seconds",
        "survival_probability_at_14608619_seconds",
    ]

    horizon_values = {
        column: pd.to_numeric(
            frame[
                column
            ],
            errors="coerce",
        )
        for column in horizon_columns
    }

    invalid_duration = (
        duration.isna()
        |
        ~np.isfinite(
            duration
        )
        |
        (duration < 0)
    )

    invalid_event = (
        event.isna()
        |
        ~event.isin(
            [0, 1]
        )
    )

    invalid_median_prediction = (
        median_prediction.isna()
        |
        ~np.isfinite(
            median_prediction
        )
        |
        (median_prediction < 0)
    )

    invalid_horizon_values = {}

    for column, values in (
        horizon_values.items()
    ):

        invalid_horizon_values[
            column
        ] = int(
            (
                values.isna()
                |
                ~np.isfinite(
                    values
                )
                |
                (values < 0)
                |
                (values > 1)
            ).sum()
        )

    result.update(
        {

            "event_1": int(
                event.eq(1).sum()
            ),

            "event_0": int(
                event.eq(0).sum()
            ),

            "event_rate": float(
                event.eq(1).mean()
            ),

            "censor_rate": float(
                event.eq(0).mean()
            ),

            "duration_min": float(
                duration.min()
            ),

            "duration_max": float(
                duration.max()
            ),

            "median_prediction_min": float(
                median_prediction.min()
            ),

            "median_prediction_max": float(
                median_prediction.max()
            ),

            "invalid_duration_rows": int(
                invalid_duration.sum()
            ),

            "invalid_event_rows": int(
                invalid_event.sum()
            ),

            "invalid_median_prediction_rows": int(
                invalid_median_prediction.sum()
            ),

            "invalid_survival_probability_rows": (
                invalid_horizon_values
            ),
        }
    )

    all_horizon_valid = all(
        count == 0
        for count
        in invalid_horizon_values.values()
    )

    result[
        "status"
    ] = (
        "PASS"
        if (
            not invalid_duration.any()
            and
            not invalid_event.any()
            and
            not invalid_median_prediction.any()
            and
            all_horizon_valid
        )
        else "FAIL"
    )

    return frame, result


# ============================================================
# POPULATION ALIGNMENT
# ============================================================

def audit_alignment(
    evaluation: pd.DataFrame,
    prediction: pd.DataFrame,
    prediction_name: str,
) -> dict[str, Any]:

    eval_id = find_id_column(
        evaluation
    )

    pred_id = find_id_column(
        prediction
    )

    result = {

        "prediction_artifact": prediction_name,

        "evaluation_rows": int(
            len(evaluation)
        ),

        "prediction_rows": int(
            len(prediction)
        ),

        "evaluation_id_column": eval_id,

        "prediction_id_column": pred_id,
    }

    if (
        eval_id is not None
        and
        pred_id is not None
    ):

        eval_ids = (
            evaluation[
                eval_id
            ]
            .astype(str)
        )

        pred_ids = (
            prediction[
                pred_id
            ]
            .astype(str)
        )

        eval_set = set(
            eval_ids
        )

        pred_set = set(
            pred_ids
        )

        duplicate_eval_ids = int(
            eval_ids.duplicated().sum()
        )

        duplicate_pred_ids = int(
            pred_ids.duplicated().sum()
        )

        missing_from_prediction = (
            eval_set - pred_set
        )

        extra_in_prediction = (
            pred_set - eval_set
        )

        result.update(
            {

                "duplicate_evaluation_ids": (
                    duplicate_eval_ids
                ),

                "duplicate_prediction_ids": (
                    duplicate_pred_ids
                ),

                "evaluation_ids_missing_from_prediction": (
                    len(
                        missing_from_prediction
                    )
                ),

                "prediction_ids_not_in_evaluation": (
                    len(
                        extra_in_prediction
                    )
                ),

                "exact_id_set_alignment": (
                    eval_set == pred_set
                ),
            }
        )

    else:

        result[
            "exact_id_set_alignment"
        ] = None

        result[
            "alignment_note"
        ] = (
            "No explicit common ID column "
            "could be resolved."
        )

    result[
        "row_count_alignment"
    ] = (
        len(evaluation)
        ==
        len(prediction)
    )

    result[
        "status"
    ] = (
        "PASS"
        if (
            result[
                "row_count_alignment"
            ]
            and
            (
                result[
                    "exact_id_set_alignment"
                ]
                is True
                or
                result[
                    "exact_id_set_alignment"
                ]
                is None
            )
        )
        else "FAIL"
    )

    return result


# ============================================================
# PREDICTION CONSISTENCY
# ============================================================

def compare_prediction_artifacts(
    mod007: pd.DataFrame,
    mod010: pd.DataFrame,
) -> dict[str, Any]:

    result = {

        "mod007_rows": int(
            len(mod007)
        ),

        "mod010_rows": int(
            len(mod010)
        ),

        "same_row_count": (
            len(mod007)
            ==
            len(mod010)
        ),
    }

    common_columns = sorted(
        set(
            mod007.columns
        )
        &
        set(
            mod010.columns
        )
    )

    result[
        "common_columns"
    ] = common_columns

    comparison = {}

    for column in common_columns:

        left = mod007[
            column
        ]

        right = mod010[
            column
        ]

        if (
            pd.api.types.is_numeric_dtype(
                left
            )
            and
            pd.api.types.is_numeric_dtype(
                right
            )
        ):

            left_numeric = pd.to_numeric(
                left,
                errors="coerce",
            )

            right_numeric = pd.to_numeric(
                right,
                errors="coerce",
            )

            aligned_length = min(
                len(left_numeric),
                len(right_numeric),
            )

            if aligned_length:

                diff = (
                    left_numeric.iloc[
                        :aligned_length
                    ].to_numpy()
                    -
                    right_numeric.iloc[
                        :aligned_length
                    ].to_numpy()
                )

                finite = np.isfinite(
                    diff
                )

                comparison[
                    column
                ] = {

                    "numeric": True,

                    "exact_equal": bool(
                        np.all(
                            diff[
                                finite
                            ]
                            == 0
                        )
                    ),

                    "max_absolute_difference": (
                        float(
                            np.max(
                                np.abs(
                                    diff[
                                        finite
                                    ]
                                )
                            )
                        )
                        if finite.any()
                        else None
                    ),
                }

        else:

            left_text = (
                left.astype(str)
                .to_numpy()
            )

            right_text = (
                right.astype(str)
                .to_numpy()
            )

            aligned_length = min(
                len(left_text),
                len(right_text),
            )

            if aligned_length:

                comparison[
                    column
                ] = {

                    "numeric": False,

                    "exact_equal": bool(
                        np.array_equal(
                            left_text[
                                :aligned_length
                            ],
                            right_text[
                                :aligned_length
                            ],
                        )
                    ),
                }

    result[
        "column_comparison"
    ] = comparison

    return result


# ============================================================
# AUDIT ARTIFACTS
# ============================================================

def inspect_supporting_audits() -> dict[str, Any]:

    artifacts = {

        "MOD-007": T7_MOD007_AUDIT,

        "MOD-008": T7_MOD008_AUDIT,

        "MOD-009": T7_MOD009_AUDIT,

        "MOD-012": T7_MOD012_CLOSURE,
    }

    result = {}

    for label, path in artifacts.items():

        if not path.exists():

            result[
                label
            ] = {

                "exists": False,

                "path": str(
                    path.relative_to(
                        PROJECT_ROOT
                    )
                ),
            }

            continue

        data = load_json(
            path
        )

        result[
            label
        ] = {

            "exists": True,

            "path": str(
                path.relative_to(
                    PROJECT_ROOT
                )
            ),

            "top_level_keys": list(
                data.keys()
            ),

            "status": data.get(
                "status"
            ),

            "operation": data.get(
                "operation"
            ),

            "title": data.get(
                "title"
            ),
        }

    return result


# ============================================================
# CONTROLS
# ============================================================

def build_controls() -> dict[str, Any]:

    return {

        "artifact_read_only": True,

        "model_fitted": False,

        "prediction_generated": False,

        "probability_generated": False,

        "calibration_fitted": False,

        "target_created": False,

        "target_relabelled": False,

        "censoring_relabelled": False,

        "survival_converted_to_binary": False,

        "binary_resolution_created": False,

        "threshold_selected": False,

        "locked_test_used": False,

        "post_creation_information_used": False,

        "universal_confidence_created": False,

        "universal_risk_score_created": False,

        "existing_artifacts_modified": False,

        "native_survival_semantics_preserved": True,
    }


def validate_controls(
    controls: dict[str, Any],
) -> dict[str, Any]:

    allowed_true = {
        "artifact_read_only",
        "native_survival_semantics_preserved",
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

        "status": (
            "PASS"
            if not failures
            else "FAIL"
        ),

        "failed_controls": failures,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 72)
    print("T9 MOD-037 OP-013B")
    print(
        "T7 Event / Censoring / Native Survival "
        "Output Semantic Audit"
    )
    print("=" * 72)
    print()

    # --------------------------------------------------------
    # T9 BOUNDARY
    # --------------------------------------------------------

    print(
        "Validating frozen T9 T7 boundary..."
    )

    boundary = (
        validate_t9_boundary()
    )

    print(
        "T7 boundary validation:",
        boundary[
            "status"
        ],
    )

    if boundary[
        "status"
    ] != "PASS":

        raise RuntimeError(
            "Frozen T7 boundary validation failed."
        )

    print()

    # --------------------------------------------------------
    # CONTRACT
    # --------------------------------------------------------

    print(
        "Auditing T7 modeling contract..."
    )

    contract_audit = audit_contract()

    print(
        "Contract semantic audit:",
        contract_audit[
            "status"
        ],
    )

    if contract_audit[
        "status"
    ] != "PASS":

        raise RuntimeError(
            "T7 contract semantic audit failed."
        )

    print()

    # --------------------------------------------------------
    # SPLITS
    # --------------------------------------------------------

    print(
        "Loading T7 TRAIN and EVAL splits..."
    )

    train_frame, train_audit = load_split(
        T7_TRAIN,
        "TRAIN",
    )

    eval_frame, eval_audit = load_split(
        T7_EVAL,
        "EVAL",
    )

    print(
        "TRAIN rows:",
        train_audit[
            "rows"
        ],
    )

    print(
        "EVAL rows:",
        eval_audit[
            "rows"
        ],
    )

    print(
        "TRAIN event rate:",
        f"{train_audit['event_rate']:.6f}",
    )

    print(
        "EVAL event rate:",
        f"{eval_audit['event_rate']:.6f}",
    )

    print()

    # --------------------------------------------------------
    # PREDICTION ARTIFACTS
    # --------------------------------------------------------

    print(
        "Inspecting MOD-007 evaluation predictions..."
    )

    mod007_frame, mod007_audit = (
        inspect_prediction_artifact(
            T7_MOD007_PREDICTIONS,
            "MOD-007",
        )
    )

    print(
        "MOD-007 status:",
        mod007_audit[
            "status"
        ],
    )

    print(
        "MOD-007 rows:",
        mod007_audit[
            "rows"
        ],
    )

    print()

    print(
        "Inspecting MOD-010 evaluation predictions..."
    )

    mod010_frame, mod010_audit = (
        inspect_prediction_artifact(
            T7_MOD010_PREDICTIONS,
            "MOD-010",
        )
    )

    print(
        "MOD-010 status:",
        mod010_audit[
            "status"
        ],
    )

    print(
        "MOD-010 rows:",
        mod010_audit[
            "rows"
        ],
    )

    print()

    if (
        mod007_audit[
            "status"
        ]
        != "PASS"
    ):

        raise RuntimeError(
            "MOD-007 prediction artifact audit failed."
        )

    if (
        mod010_audit[
            "status"
        ]
        != "PASS"
    ):

        raise RuntimeError(
            "MOD-010 prediction artifact audit failed."
        )

    # --------------------------------------------------------
    # ALIGNMENT
    # --------------------------------------------------------

    print(
        "Auditing MOD-007 population alignment..."
    )

    mod007_alignment = audit_alignment(
        eval_frame,
        mod007_frame,
        "MOD-007",
    )

    print(
        "MOD-007 alignment:",
        mod007_alignment[
            "status"
        ],
    )

    print()

    print(
        "Auditing MOD-010 population alignment..."
    )

    mod010_alignment = audit_alignment(
        eval_frame,
        mod010_frame,
        "MOD-010",
    )

    print(
        "MOD-010 alignment:",
        mod010_alignment[
            "status"
        ],
    )

    print()

    if (
        mod007_alignment[
            "status"
        ]
        != "PASS"
    ):

        raise RuntimeError(
            "MOD-007 population alignment failed."
        )

    if (
        mod010_alignment[
            "status"
        ]
        != "PASS"
    ):

        raise RuntimeError(
            "MOD-010 population alignment failed."
        )

    # --------------------------------------------------------
    # MOD-007 vs MOD-010
    # --------------------------------------------------------

    print(
        "Comparing MOD-007 and MOD-010 prediction structures..."
    )

    prediction_comparison = (
        compare_prediction_artifacts(
            mod007_frame,
            mod010_frame,
        )
    )

    print(
        "Same row count:",
        prediction_comparison[
            "same_row_count"
        ],
    )

    print(
        "Common columns:",
        prediction_comparison[
            "common_columns"
        ],
    )

    print()

    # --------------------------------------------------------
    # SUPPORTING AUDITS
    # --------------------------------------------------------

    print(
        "Inspecting supporting T7 audit artifacts..."
    )

    supporting_audits = (
        inspect_supporting_audits()
    )

    for label, info in (
        supporting_audits.items()
    ):

        print(
            f"{label}:",
            "PRESENT"
            if info[
                "exists"
            ]
            else "MISSING",
        )

    print()

    # --------------------------------------------------------
    # IDENTITY / POPULATION RECONCILIATION
    # --------------------------------------------------------

    eval_id = find_id_column(
        eval_frame
    )

    mod007_id = find_id_column(
        mod007_frame
    )

    mod010_id = find_id_column(
        mod010_frame
    )

    population_reconciliation = {

        "evaluation_id_column": eval_id,

        "mod007_id_column": mod007_id,

        "mod010_id_column": mod010_id,

        "evaluation_rows": int(
            len(eval_frame)
        ),

        "mod007_rows": int(
            len(mod007_frame)
        ),

        "mod010_rows": int(
            len(mod010_frame)
        ),

        "all_population_sizes_equal": (
            len(eval_frame)
            ==
            len(mod007_frame)
            ==
            len(mod010_frame)
        ),
    }

    if (
        eval_id is not None
        and
        mod007_id is not None
        and
        mod010_id is not None
    ):

        eval_ids = set(
            eval_frame[
                eval_id
            ]
            .astype(str)
        )

        mod007_ids = set(
            mod007_frame[
                mod007_id
            ]
            .astype(str)
        )

        mod010_ids = set(
            mod010_frame[
                mod010_id
            ]
            .astype(str)
        )

        population_reconciliation.update(
            {

                "eval_mod007_exact_id_match": (
                    eval_ids == mod007_ids
                ),

                "eval_mod010_exact_id_match": (
                    eval_ids == mod010_ids
                ),

                "mod007_mod010_exact_id_match": (
                    mod007_ids == mod010_ids
                ),
            }
        )

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
    # FINAL SEMANTIC RESOLUTION
    # --------------------------------------------------------

    semantic_resolution = {

        "duration_seconds": {

            "status": "ESTABLISHED",

            "meaning": (
                "Observed time-to-event / censoring "
                "duration field preserved from the T7 "
                "native evaluation population."
            ),
        },

        "event": {

            "status": "ESTABLISHED",

            "meaning": (
                "Binary event indicator retained as "
                "the native survival event/censoring "
                "indicator; 1 denotes observed event "
                "and 0 denotes censored observation "
                "within the T7 evidence boundary."
            ),
        },

        "predicted_median_survival_seconds": {

            "status": "NATIVE_SURVIVAL_OUTPUT_CANDIDATE",

            "meaning": (
                "Predicted median survival time emitted "
                "by the existing T7 predictive artifact."
            ),
        },

        "survival_probability_horizons": {

            "status": "NATIVE_SURVIVAL_OUTPUT_CANDIDATE",

            "horizons_seconds": [
                211583,
                1780179,
                14608619,
            ],

            "meaning": (
                "Existing survival-probability outputs "
                "at fixed time horizons."
            ),
        },

        "binary_resolution_probability": {

            "status": "NOT_ESTABLISHED",

            "restriction": (
                "No conversion of survival outputs "
                "into an ordinary binary resolution "
                "probability is permitted."
            ),
        },

        "censoring": {

            "status": "PRESERVED",

            "restriction": (
                "Censored observations remain censored "
                "and are not relabelled as non-resolution "
                "events."
            ),
        },
    }

    # --------------------------------------------------------
    # CANDIDATE STATUS
    # --------------------------------------------------------

    candidate_status = {

        "MOD-007": {

            "artifact": str(
                T7_MOD007_PREDICTIONS.relative_to(
                    PROJECT_ROOT
                )
            ),

            "population_alignment": (
                mod007_alignment[
                    "status"
                ]
            ),

            "native_survival_outputs_present": True,

            "status": (
                "ACCEPTED_NATIVE_SURVIVAL_CANDIDATE"
            ),
        },

        "MOD-010": {

            "artifact": str(
                T7_MOD010_PREDICTIONS.relative_to(
                    PROJECT_ROOT
                )
            ),

            "population_alignment": (
                mod010_alignment[
                    "status"
                ]
            ),

            "native_survival_outputs_present": True,

            "status": (
                "ACCEPTED_NATIVE_SURVIVAL_CANDIDATE"
            ),
        },
    }

    # --------------------------------------------------------
    # IMPORTANT:
    # Do not select MOD-007 vs MOD-010 solely here.
    # --------------------------------------------------------

    interpretation = {

        "native_survival_semantics": (
            "ESTABLISHED"
        ),

        "censoring_semantics": (
            "PRESERVED"
        ),

        "event_duration_structure": (
            "ESTABLISHED"
        ),

        "native_survival_prediction_artifacts": [
            "MOD-007",
            "MOD-010",
        ],

        "final_model_artifact_selection": (
            "NOT_PERFORMED"
        ),

        "probability_calibration": (
            "NOT_PERFORMED"
        ),

        "binary_conversion": (
            "NOT_PERFORMED"
        ),

        "next_operation": (
            "OP-013C should perform native T7 "
            "survival evaluation using the established "
            "event/time/censoring structure and accepted "
            "native survival outputs."
        ),
    }

    # --------------------------------------------------------
    # OVERALL STATUS
    # --------------------------------------------------------

    overall_checks = [

        boundary[
            "status"
        ] == "PASS",

        contract_audit[
            "status"
        ] == "PASS",

        train_audit[
            "status"
        ] == "PASS",

        eval_audit[
            "status"
        ] == "PASS",

        mod007_audit[
            "status"
        ] == "PASS",

        mod010_audit[
            "status"
        ] == "PASS",

        mod007_alignment[
            "status"
        ] == "PASS",

        mod010_alignment[
            "status"
        ] == "PASS",

        control_validation[
            "status"
        ] == "PASS",
    ]

    overall_status = (
        "PASS"
        if all(
            overall_checks
        )
        else "FAIL"
    )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    output = {

        "operation": (
            "T9_MOD-037_OP-013B"
        ),

        "title": (
            "T7 Event / Censoring / Native Survival "
            "Output Semantic Audit"
        ),

        "status": overall_status,

        "purpose": (
            "Resolve the native T7 survival evaluation "
            "population, event/censoring semantics, "
            "duration structure, and predictive survival "
            "outputs without fitting, calibration, or "
            "target modification."
        ),

        "frozen_t9_boundary": boundary,

        "contract_audit": contract_audit,

        "train_audit": train_audit,

        "evaluation_audit": eval_audit,

        "prediction_artifacts": {

            "MOD-007": mod007_audit,

            "MOD-010": mod010_audit,
        },

        "population_alignment": {

            "MOD-007": mod007_alignment,

            "MOD-010": mod010_alignment,
        },

        "population_reconciliation": (
            population_reconciliation
        ),

        "prediction_artifact_comparison": (
            prediction_comparison
        ),

        "supporting_t7_audits": (
            supporting_audits
        ),

        "candidate_status": candidate_status,

        "semantic_resolution": (
            semantic_resolution
        ),

        "interpretation": interpretation,

        "controls": controls,

        "control_validation": (
            control_validation
        ),

        "methodological_restrictions": [

            "Read-only artifact inspection.",

            "No model fitting.",

            "No prediction generation.",

            "No new probability generation.",

            "No calibration fitting.",

            "No target creation.",

            "No target relabelling.",

            "No censoring relabelling.",

            "No survival-to-binary conversion.",

            "No threshold selection.",

            "No locked-test selection.",

            "No final MOD-007 vs MOD-010 model "
            "selection is performed by this operation.",

            "Native survival semantics are preserved.",
        ],

        "artifacts_generated": [

            str(
                OUTPUT_JSON
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

    # --------------------------------------------------------
    # FINAL CONSOLE
    # --------------------------------------------------------

    print("=" * 72)
    print("T9 MOD-037 OP-013B RESULT")
    print("=" * 72)
    print()

    print(
        "T7 boundary:",
        boundary[
            "status"
        ],
    )

    print(
        "T7 contract audit:",
        contract_audit[
            "status"
        ],
    )

    print(
        "TRAIN audit:",
        train_audit[
            "status"
        ],
    )

    print(
        "EVAL audit:",
        eval_audit[
            "status"
        ],
    )

    print(
        "MOD-007 prediction audit:",
        mod007_audit[
            "status"
        ],
    )

    print(
        "MOD-010 prediction audit:",
        mod010_audit[
            "status"
        ],
    )

    print(
        "MOD-007 alignment:",
        mod007_alignment[
            "status"
        ],
    )

    print(
        "MOD-010 alignment:",
        mod010_alignment[
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
        "Native survival semantics:",
        "ESTABLISHED",
    )

    print(
        "Censoring relabelling:",
        "NO",
    )

    print(
        "Survival-to-binary conversion:",
        "NO",
    )

    print(
        "Calibration fitting:",
        "NO",
    )

    print(
        "Model selection:",
        "NO",
    )

    print(
        "Locked test used:",
        "NO",
    )

    print()

    print(
        "MOD-007:",
        "ACCEPTED_NATIVE_SURVIVAL_CANDIDATE",
    )

    print(
        "MOD-010:",
        "ACCEPTED_NATIVE_SURVIVAL_CANDIDATE",
    )

    print()

    print(
        "Output:",
        OUTPUT_JSON,
    )

    print()

    print(
        "T9 MOD-037 OP-013B:",
        overall_status,
    )


if __name__ == "__main__":
    main()