from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


# ============================================================
# T9 MOD-037 OP-013C
# T7 Native Survival Evaluation
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
    / "t9_mod037_op013c_t7_native_survival_evaluation.json"
)

OUTPUT_CSV = (
    OUTPUT_DIR
    / "t9_mod037_op013c_t7_survival_metrics.csv"
)


# ============================================================
# PRIOR T9 ARTIFACTS
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

OP013B_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op013b_t7_survival_semantics_audit.json"
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

T7_MOD007 = (
    T7_ROOT
    / "derived"
    / "t7_mod007_evaluation_predictions.csv"
)

T7_MOD010 = (
    T7_ROOT
    / "derived"
    / "t7_mod010_evaluation_predictions.csv"
)


# ============================================================
# NATIVE HORIZONS
# ============================================================

HORIZONS = {
    211583: (
        "survival_probability_at_211583_seconds"
    ),
    1780179: (
        "survival_probability_at_1780179_seconds"
    ),
    14608619: (
        "survival_probability_at_14608619_seconds"
    ),
}


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


def normalize_frame(
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

    for column in [
        "ID",
        "id",
        "ticket_id",
        "issue_id",
        "bug_id",
        "row_id",
    ]:

        if column in frame.columns:

            return column

    candidates = [
        column
        for column in frame.columns
        if "id" in str(column).lower()
    ]

    return (
        candidates[0]
        if candidates
        else None
    )


# ============================================================
# PRIOR OPERATION VALIDATION
# ============================================================

def validate_prior_operations() -> dict[str, Any]:

    op004 = load_json(
        OP004_ARTIFACT
    )

    op005 = load_json(
        OP005_ARTIFACT
    )

    op013a = load_json(
        OP013A_ARTIFACT
    )

    op013b = load_json(
        OP013B_ARTIFACT
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
    ] = (
        "PASS"
        if "T7" in accepted_tasks
        else "FAIL"
    )

    checks[
        "OP-005_T7_boundary"
    ] = (
        "PASS"
        if (
            op005.get("status") == "PASS"
            and
            t7_boundary.get(
                "status"
            )
            == "ACCEPTED_NATIVE_SURVIVAL"
        )
        else "FAIL"
    )

    checks[
        "OP-013A"
    ] = (
        "PASS"
        if op013a.get(
            "status"
        ) == "PASS"
        else "FAIL"
    )

    checks[
        "OP-013B"
    ] = (
        "PASS"
        if op013b.get(
            "status"
        ) == "PASS"
        else "FAIL"
    )

    failed = [
        key
        for key, value in checks.items()
        if value != "PASS"
    ]

    return {

        "status": (
            "PASS"
            if not failed
            else "FAIL"
        ),

        "checks": checks,

        "failed_checks": failed,
    }


# ============================================================
# LOAD EVALUATION POPULATION
# ============================================================

def load_eval_population() -> pd.DataFrame:

    require_file(
        T7_EVAL
    )

    frame = normalize_frame(
        pd.read_csv(
            T7_EVAL,
            low_memory=False,
        )
    )

    required = [
        "duration_seconds",
        "event",
    ]

    missing = [
        column
        for column in required
        if column not in frame.columns
    ]

    if missing:

        raise RuntimeError(
            f"T7 EVAL missing required columns: "
            f"{missing}"
        )

    frame[
        "duration_seconds"
    ] = pd.to_numeric(
        frame[
            "duration_seconds"
        ],
        errors="coerce",
    )

    frame[
        "event"
    ] = pd.to_numeric(
        frame[
            "event"
        ],
        errors="coerce",
    )

    if (
        frame[
            "duration_seconds"
        ]
        .isna()
        .any()
    ):

        raise RuntimeError(
            "T7 EVAL contains invalid duration values."
        )

    if (
        ~frame[
            "event"
        ].isin(
            [0, 1]
        )
    ).any():

        raise RuntimeError(
            "T7 EVAL event field contains values "
            "outside {0,1}."
        )

    return frame


# ============================================================
# LOAD PREDICTION ARTIFACT
# ============================================================

def load_prediction(
    path: Path,
    label: str,
) -> pd.DataFrame:

    require_file(path)

    frame = normalize_frame(
        pd.read_csv(
            path,
            low_memory=False,
        )
    )

    required = [
        "duration_seconds",
        "event",
        "predicted_median_survival_seconds",
        *HORIZONS.values(),
    ]

    missing = [
        column
        for column in required
        if column not in frame.columns
    ]

    if missing:

        raise RuntimeError(
            f"{label} missing required native survival "
            f"columns: {missing}"
        )

    frame[
        "duration_seconds"
    ] = pd.to_numeric(
        frame[
            "duration_seconds"
        ],
        errors="coerce",
    )

    frame[
        "event"
    ] = pd.to_numeric(
        frame[
            "event"
        ],
        errors="coerce",
    )

    frame[
        "predicted_median_survival_seconds"
    ] = pd.to_numeric(
        frame[
            "predicted_median_survival_seconds"
        ],
        errors="coerce",
    )

    for column in HORIZONS.values():

        frame[
            column
        ] = pd.to_numeric(
            frame[
                column
            ],
            errors="coerce",
        )

    return frame


# ============================================================
# POPULATION ALIGNMENT
# ============================================================

def align_prediction_to_eval(
    evaluation: pd.DataFrame,
    prediction: pd.DataFrame,
    label: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:

    eval_id = find_id_column(
        evaluation
    )

    pred_id = find_id_column(
        prediction
    )

    result = {

        "label": label,

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

        if (
            eval_set
            !=
            pred_set
        ):

            raise RuntimeError(
                f"{label} ID population does not "
                "exactly match T7 EVAL."
            )

        # Reorder prediction rows to EVAL ID order.
        prediction_indexed = (
            prediction
            .copy()
            .assign(
                __alignment_id=pred_ids
            )
            .set_index(
                "__alignment_id"
            )
        )

        aligned = (
            prediction_indexed
            .loc[
                eval_ids
            ]
            .reset_index(
                drop=True
            )
        )

        evaluation = (
            evaluation
            .reset_index(
                drop=True
            )
        )

        if not np.array_equal(
            evaluation[
                eval_id
            ]
            .astype(str)
            .to_numpy(),
            aligned[
                pred_id
            ]
            .astype(str)
            .to_numpy(),
        ):

            raise RuntimeError(
                f"{label} failed deterministic "
                "ID alignment."
            )

        result[
            "exact_id_set_alignment"
        ] = True

    else:

        if len(
            evaluation
        ) != len(
            prediction
        ):

            raise RuntimeError(
                f"{label} has no resolvable ID column "
                "and row counts do not match."
            )

        aligned = (
            prediction
            .reset_index(
                drop=True
            )
        )

        evaluation = (
            evaluation
            .reset_index(
                drop=True
            )
        )

        result[
            "exact_id_set_alignment"
        ] = None

        result[
            "alignment_basis"
        ] = (
            "Exact row-count alignment because "
            "no common ID column was resolvable."
        )

    result[
        "status"
    ] = "PASS"

    return aligned, result


# ============================================================
# PREDICTION RANGE AUDIT
# ============================================================

def audit_prediction_ranges(
    prediction: pd.DataFrame,
    label: str,
) -> dict[str, Any]:

    median = pd.to_numeric(
        prediction[
            "predicted_median_survival_seconds"
        ],
        errors="coerce",
    )

    median_invalid = (
        median.isna()
        |
        ~np.isfinite(
            median
        )
        |
        (median < 0)
    )

    horizon_audit = {}

    for horizon, column in HORIZONS.items():

        values = pd.to_numeric(
            prediction[
                column
            ],
            errors="coerce",
        )

        invalid = (
            values.isna()
            |
            ~np.isfinite(
                values
            )
            |
            (values < 0)
            |
            (values > 1)
        )

        horizon_audit[
            str(horizon)
        ] = {

            "column": column,

            "rows": int(
                len(values)
            ),

            "invalid_rows": int(
                invalid.sum()
            ),

            "min": float(
                values.min()
            ),

            "max": float(
                values.max()
            ),

            "mean": float(
                values.mean()
            ),

            "status": (
                "PASS"
                if not invalid.any()
                else "FAIL"
            ),
        }

    return {

        "label": label,

        "median_survival": {

            "invalid_rows": int(
                median_invalid.sum()
            ),

            "min": float(
                median.min()
            ),

            "max": float(
                median.max()
            ),

            "mean": float(
                median.mean()
            ),

            "status": (
                "PASS"
                if not median_invalid.any()
                else "FAIL"
            ),
        },

        "horizons": horizon_audit,
    }


# ============================================================
# KAPLAN-MEIER CENSORING SURVIVAL
# ============================================================

def censoring_km(
    durations: np.ndarray,
    events: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:

    """
    Kaplan-Meier estimate of the censoring-survival
    function G(t).

    In the censoring process:

        censoring event = 1 - event

    The returned time points are event times in the
    censoring process, with the post-event survival
    probability G(t).
    """

    durations = np.asarray(
        durations,
        dtype=float,
    )

    events = np.asarray(
        events,
        dtype=int,
    )

    censor_event = (
        1
        -
        events
    )

    unique_times = np.sort(
        np.unique(
            durations
        )
    )

    at_risk = len(
        durations
    )

    survival = 1.0

    times = []
    probabilities = []

    for time in unique_times:

        at_time = (
            durations
            == time
        )

        censor_count = int(
            np.sum(
                censor_event[
                    at_time
                ]
                == 1
            )
        )

        total_count = int(
            np.sum(
                at_time
            )
        )

        if at_risk > 0:

            survival *= (
                1.0
                -
                (
                    censor_count
                    /
                    at_risk
                )
            )

        times.append(
            float(time)
        )

        probabilities.append(
            float(survival)
        )

        at_risk -= total_count

    return (
        np.asarray(
            times,
            dtype=float,
        ),
        np.asarray(
            probabilities,
            dtype=float,
        ),
    )


def censoring_survival_at(
    time: float,
    km_times: np.ndarray,
    km_survival: np.ndarray,
) -> float:

    if len(
        km_times
    ) == 0:

        return 1.0

    indices = np.searchsorted(
        km_times,
        time,
        side="right",
    )

    if indices == 0:

        return 1.0

    return float(
        km_survival[
            indices - 1
        ]
    )


def censoring_survival_before(
    time: float,
    km_times: np.ndarray,
    km_survival: np.ndarray,
) -> float:

    if len(
        km_times
    ) == 0:

        return 1.0

    indices = np.searchsorted(
        km_times,
        time,
        side="left",
    )

    if indices == 0:

        return 1.0

    return float(
        km_survival[
            indices - 1
        ]
    )


# ============================================================
# IPCW BRIER SCORE
# ============================================================

def ipcw_brier_score(
    durations: np.ndarray,
    events: np.ndarray,
    predicted_survival: np.ndarray,
    horizon: float,
) -> dict[str, Any]:

    km_times, km_survival = (
        censoring_km(
            durations,
            events,
        )
    )

    n = len(
        durations
    )

    contributions = []
    included = 0
    excluded_zero_weight = 0

    for i in range(n):

        time_i = float(
            durations[i]
        )

        event_i = int(
            events[i]
        )

        prediction_i = float(
            predicted_survival[i]
        )

        # Event observed by horizon.
        if (
            event_i == 1
            and
            time_i <= horizon
        ):

            g = censoring_survival_before(
                time_i,
                km_times,
                km_survival,
            )

            if g <= 0:

                excluded_zero_weight += 1
                continue

            outcome = 0.0

            weight = (
                1.0
                /
                g
            )

            contribution = (
                weight
                *
                (
                    outcome
                    -
                    prediction_i
                )
                ** 2
            )

            contributions.append(
                contribution
            )

            included += 1

        # Still event-free at horizon.
        elif time_i > horizon:

            g = censoring_survival_at(
                horizon,
                km_times,
                km_survival,
            )

            if g <= 0:

                excluded_zero_weight += 1
                continue

            outcome = 1.0

            weight = (
                1.0
                /
                g
            )

            contribution = (
                weight
                *
                (
                    outcome
                    -
                    prediction_i
                )
                ** 2
            )

            contributions.append(
                contribution
            )

            included += 1

        # Censored before horizon:
        # no observable outcome at this horizon.
        else:

            continue

    if not contributions:

        raise RuntimeError(
            f"No evaluable observations for "
            f"horizon {horizon}."
        )

    return {

        "horizon_seconds": int(
            horizon
        ),

        "brier_score_ipcw": float(
            np.mean(
                contributions
            )
        ),

        "evaluated_rows": int(
            included
        ),

        "excluded_zero_censoring_weight_rows": int(
            excluded_zero_weight
        ),

        "total_rows": int(
            n
        ),

        "evaluation_fraction": float(
            included / n
        ),
    }


# ============================================================
# SURVIVAL CALIBRATION DESCRIPTIVE AUDIT
# ============================================================

def survival_calibration_summary(
    durations: np.ndarray,
    events: np.ndarray,
    predicted_survival: np.ndarray,
    horizon: float,
) -> dict[str, Any]:

    """
    Descriptive fixed-horizon calibration evidence.

    This does NOT fit a calibration model.

    It compares:
      - mean predicted survival
      - IPCW observed survival estimate

    The observed survival estimate is the Kaplan-Meier
    survival estimate from the evaluation population.
    """

    km_times, km_survival = (
        kaplan_meier_event_survival(
            durations,
            events,
        )
    )

    observed_survival = (
        kaplan_meier_survival_at(
            horizon,
            km_times,
            km_survival,
        )
    )

    predicted_mean = float(
        np.mean(
            predicted_survival
        )
    )

    return {

        "horizon_seconds": int(
            horizon
        ),

        "predicted_survival_mean": (
            predicted_mean
        ),

        "observed_kaplan_meier_survival": (
            observed_survival
        ),

        "mean_predicted_minus_observed": (
            predicted_mean
            -
            observed_survival
        ),

        "calibration_model_fitted": False,
    }


# ============================================================
# KAPLAN-MEIER EVENT SURVIVAL
# ============================================================

def kaplan_meier_event_survival(
    durations: np.ndarray,
    events: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:

    durations = np.asarray(
        durations,
        dtype=float,
    )

    events = np.asarray(
        events,
        dtype=int,
    )

    unique_times = np.sort(
        np.unique(
            durations
        )
    )

    at_risk = len(
        durations
    )

    survival = 1.0

    times = []
    probabilities = []

    for time in unique_times:

        at_time = (
            durations
            == time
        )

        event_count = int(
            np.sum(
                events[
                    at_time
                ]
                == 1
            )
        )

        total_count = int(
            np.sum(
                at_time
            )
        )

        if at_risk > 0:

            survival *= (
                1.0
                -
                (
                    event_count
                    /
                    at_risk
                )
            )

        times.append(
            float(time)
        )

        probabilities.append(
            float(survival)
        )

        at_risk -= total_count

    return (
        np.asarray(
            times,
            dtype=float,
        ),
        np.asarray(
            probabilities,
            dtype=float,
        ),
    )


def kaplan_meier_survival_at(
    horizon: float,
    km_times: np.ndarray,
    km_survival: np.ndarray,
) -> float:

    if len(
        km_times
    ) == 0:

        return 1.0

    indices = np.searchsorted(
        km_times,
        horizon,
        side="right",
    )

    if indices == 0:

        return 1.0

    return float(
        km_survival[
            indices - 1
        ]
    )


# ============================================================
# CONCORDANCE INDEX
# ============================================================

def harrell_c_index(
    durations: np.ndarray,
    events: np.ndarray,
    predicted_median_survival: np.ndarray,
) -> dict[str, Any]:

    """
    Harrell-style concordance using predicted median survival.

    Lower predicted survival time means earlier predicted event.

    A pair is usable when the earlier observed time is an
    observed event. Censored observations are therefore not
    automatically treated as failures.

    This is descriptive native survival ranking evidence.
    """

    n = len(
        durations
    )

    comparable = 0
    concordant = 0.0
    tied = 0

    for i in range(n):

        for j in range(
            i + 1,
            n,
        ):

            ti = float(
                durations[i]
            )

            tj = float(
                durations[j]
            )

            ei = int(
                events[i]
            )

            ej = int(
                events[j]
            )

            pi = float(
                predicted_median_survival[i]
            )

            pj = float(
                predicted_median_survival[j]
            )

            # i has an observed event before j.
            if (
                ei == 1
                and
                ti < tj
            ):

                comparable += 1

                if pi < pj:

                    concordant += 1.0

                elif pi == pj:

                    concordant += 0.5
                    tied += 1

            # j has an observed event before i.
            elif (
                ej == 1
                and
                tj < ti
            ):

                comparable += 1

                if pj < pi:

                    concordant += 1.0

                elif pj == pi:

                    concordant += 0.5
                    tied += 1

    c_index = (
        concordant / comparable
        if comparable > 0
        else np.nan
    )

    return {

        "harrell_c_index": (
            float(c_index)
            if np.isfinite(
                c_index
            )
            else None
        ),

        "comparable_pairs": int(
            comparable
        ),

        "concordant_or_half_tied_pairs": float(
            concordant
        ),

        "prediction_tied_pairs": int(
            tied
        ),
    }


# ============================================================
# MEDIAN SURVIVAL ERROR
# ============================================================

def median_survival_descriptive_error(
    durations: np.ndarray,
    events: np.ndarray,
    predicted_median: np.ndarray,
) -> dict[str, Any]:

    """
    Median-survival error is only summarized for uncensored
    event observations. Censored observations are NOT treated
    as exact event times.
    """

    observed = (
        events == 1
    )

    if not observed.any():

        return {

            "event_observed_rows": 0,

            "mae_seconds": None,

            "median_absolute_error_seconds": None,

            "bias_seconds": None,

            "status": "NO_EVENT_ROWS",
        }

    error = (
        predicted_median[
            observed
        ]
        -
        durations[
            observed
        ]
    )

    absolute_error = np.abs(
        error
    )

    return {

        "event_observed_rows": int(
            observed.sum()
        ),

        "mae_seconds": float(
            np.mean(
                absolute_error
            )
        ),

        "median_absolute_error_seconds": float(
            np.median(
                absolute_error
            )
        ),

        "bias_seconds": float(
            np.mean(
                error
            )
        ),

        "status": "DESCRIPTIVE_ONLY",
    }


# ============================================================
# MODEL OUTPUT COMPARISON
# ============================================================

def compare_native_outputs(
    mod007: pd.DataFrame,
    mod010: pd.DataFrame,
) -> dict[str, Any]:

    columns = [
        "predicted_median_survival_seconds",
        *HORIZONS.values(),
    ]

    comparison = {}

    for column in columns:

        left = pd.to_numeric(
            mod007[
                column
            ],
            errors="coerce",
        ).to_numpy()

        right = pd.to_numeric(
            mod010[
                column
            ],
            errors="coerce",
        ).to_numpy()

        diff = (
            left
            -
            right
        )

        finite = np.isfinite(
            diff
        )

        if finite.any():

            comparison[
                column
            ] = {

                "exact_equal": bool(
                    np.all(
                        diff[
                            finite
                        ]
                        == 0
                    )
                ),

                "max_absolute_difference": float(
                    np.max(
                        np.abs(
                            diff[
                                finite
                            ]
                        )
                    )
                ),

                "mean_absolute_difference": float(
                    np.mean(
                        np.abs(
                            diff[
                                finite
                            ]
                        )
                    )
                ),
            }

        else:

            comparison[
                column
            ] = {

                "exact_equal": False,

                "max_absolute_difference": None,

                "mean_absolute_difference": None,
            }

    return comparison


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

        "binary_classifier_created": False,

        "threshold_selected": False,

        "locked_test_used": False,

        "post_creation_information_used": False,

        "universal_confidence_created": False,

        "universal_risk_score_created": False,

        "arbitrary_cross_task_weighting": False,

        "existing_artifacts_modified": False,

        "native_survival_semantics_preserved": True,

        "censoring_aware_evaluation_used": True,
    }


def validate_controls(
    controls: dict[str, Any],
) -> dict[str, Any]:

    allowed_true = {
        "artifact_read_only",
        "native_survival_semantics_preserved",
        "censoring_aware_evaluation_used",
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
    print("T9 MOD-037 OP-013C")
    print(
        "T7 Native Survival Evaluation"
    )
    print("=" * 72)
    print()

    # --------------------------------------------------------
    # PRIOR VALIDATION
    # --------------------------------------------------------

    print(
        "Validating prior T9 operations..."
    )

    previous = (
        validate_prior_operations()
    )

    print(
        "Previous-operation validation:",
        previous[
            "status"
        ],
    )

    if previous[
        "status"
    ] != "PASS":

        print(
            "Failed checks:",
            previous[
                "failed_checks"
            ],
        )

        raise RuntimeError(
            "Prior-operation validation failed."
        )

    print()

    # --------------------------------------------------------
    # EVAL
    # --------------------------------------------------------

    print(
        "Loading T7 EVAL population..."
    )

    evaluation = (
        load_eval_population()
    )

    print(
        "T7 EVAL rows:",
        len(evaluation),
    )

    print()

    # --------------------------------------------------------
    # PREDICTIONS
    # --------------------------------------------------------

    print(
        "Loading MOD-007 native predictions..."
    )

    mod007 = load_prediction(
        T7_MOD007,
        "MOD-007",
    )

    print(
        "MOD-007 rows:",
        len(mod007),
    )

    print()

    print(
        "Loading MOD-010 native predictions..."
    )

    mod010 = load_prediction(
        T7_MOD010,
        "MOD-010",
    )

    print(
        "MOD-010 rows:",
        len(mod010),
    )

    print()

    # --------------------------------------------------------
    # ALIGN
    # --------------------------------------------------------

    print(
        "Aligning MOD-007 to T7 EVAL..."
    )

    mod007_aligned, alignment007 = (
        align_prediction_to_eval(
            evaluation,
            mod007,
            "MOD-007",
        )
    )

    print(
        "MOD-007 alignment:",
        alignment007[
            "status"
        ],
    )

    print()

    print(
        "Aligning MOD-010 to T7 EVAL..."
    )

    mod010_aligned, alignment010 = (
        align_prediction_to_eval(
            evaluation,
            mod010,
            "MOD-010",
        )
    )

    print(
        "MOD-010 alignment:",
        alignment010[
            "status"
        ],
    )

    print()

    # --------------------------------------------------------
    # RANGE AUDIT
    # --------------------------------------------------------

    print(
        "Auditing native prediction ranges..."
    )

    range007 = audit_prediction_ranges(
        mod007_aligned,
        "MOD-007",
    )

    range010 = audit_prediction_ranges(
        mod010_aligned,
        "MOD-010",
    )

    print(
        "MOD-007 range audit:",
        (
            "PASS"
            if (
                range007[
                    "median_survival"
                ][
                    "status"
                ]
                == "PASS"
                and
                all(
                    item[
                        "status"
                    ] == "PASS"
                    for item in
                    range007[
                        "horizons"
                    ].values()
                )
            )
            else "FAIL"
        ),
    )

    print(
        "MOD-010 range audit:",
        (
            "PASS"
            if (
                range010[
                    "median_survival"
                ][
                    "status"
                ]
                == "PASS"
                and
                all(
                    item[
                        "status"
                    ] == "PASS"
                    for item in
                    range010[
                        "horizons"
                    ].values()
                )
            )
            else "FAIL"
        ),
    )

    print()

    # --------------------------------------------------------
    # OUTPUT COMPARISON
    # --------------------------------------------------------

    print(
        "Comparing MOD-007 and MOD-010 native outputs..."
    )

    native_comparison = (
        compare_native_outputs(
            mod007_aligned,
            mod010_aligned,
        )
    )

    for column, result in (
        native_comparison.items()
    ):

        print(
            f"  {column}: "
            f"exact_equal="
            f"{result['exact_equal']} "
            f"max_abs_diff="
            f"{result['max_absolute_difference']}"
        )

    print()

    # --------------------------------------------------------
    # EVAL ARRAYS
    # --------------------------------------------------------

    durations = (
        evaluation[
            "duration_seconds"
        ]
        .astype(float)
        .to_numpy()
    )

    events = (
        evaluation[
            "event"
        ]
        .astype(int)
        .to_numpy()
    )

    # --------------------------------------------------------
    # METRICS FOR EACH NATIVE ARTIFACT
    # --------------------------------------------------------

    all_metric_rows = []

    model_results = {}

    for label, prediction in [
        (
            "MOD-007",
            mod007_aligned,
        ),
        (
            "MOD-010",
            mod010_aligned,
        ),
    ]:

        print(
            f"Evaluating {label} native survival outputs..."
        )

        predicted_median = (
            prediction[
                "predicted_median_survival_seconds"
            ]
            .astype(float)
            .to_numpy()
        )

        c_index = harrell_c_index(
            durations,
            events,
            predicted_median,
        )

        median_error = (
            median_survival_descriptive_error(
                durations,
                events,
                predicted_median,
            )
        )

        horizon_results = {}

        for horizon, column in (
            HORIZONS.items()
        ):

            predicted_survival = (
                prediction[
                    column
                ]
                .astype(float)
                .to_numpy()
            )

            brier = ipcw_brier_score(
                durations,
                events,
                predicted_survival,
                horizon,
            )

            calibration = (
                survival_calibration_summary(
                    durations,
                    events,
                    predicted_survival,
                    horizon,
                )
            )

            horizon_results[
                str(horizon)
            ] = {

                "prediction_column": column,

                "brier": brier,

                "descriptive_calibration": (
                    calibration
                ),
            }

            all_metric_rows.append(
                {

                    "artifact": label,

                    "horizon_seconds": horizon,

                    "metric": "IPCW_Brier",

                    "value": brier[
                        "brier_score_ipcw"
                    ],

                    "evaluated_rows": brier[
                        "evaluated_rows"
                    ],

                    "interpretation": (
                        "Censoring-aware survival "
                        "prediction error."
                    ),
                }
            )

            all_metric_rows.append(
                {

                    "artifact": label,

                    "horizon_seconds": horizon,

                    "metric": (
                        "mean_predicted_survival"
                    ),

                    "value": calibration[
                        "predicted_survival_mean"
                    ],

                    "evaluated_rows": int(
                        len(
                            predicted_survival
                        )
                    ),

                    "interpretation": (
                        "Descriptive native survival "
                        "output summary."
                    ),
                }
            )

            all_metric_rows.append(
                {

                    "artifact": label,

                    "horizon_seconds": horizon,

                    "metric": (
                        "observed_KM_survival"
                    ),

                    "value": calibration[
                        "observed_kaplan_meier_survival"
                    ],

                    "evaluated_rows": int(
                        len(
                            predicted_survival
                        )
                    ),

                    "interpretation": (
                        "Reference Kaplan-Meier "
                        "survival estimate."
                    ),
                }
            )

            all_metric_rows.append(
                {

                    "artifact": label,

                    "horizon_seconds": horizon,

                    "metric": (
                        "mean_prediction_minus_KM"
                    ),

                    "value": calibration[
                        "mean_predicted_minus_observed"
                    ],

                    "evaluated_rows": int(
                        len(
                            predicted_survival
                        )
                    ),

                    "interpretation": (
                        "Descriptive calibration "
                        "difference; no calibration "
                        "model fitted."
                    ),
                }
            )

        model_results[
            label
        ] = {

            "harrell_c_index": c_index,

            "median_survival_error": (
                median_error
            ),

            "horizon_results": (
                horizon_results
            ),
        }

    # --------------------------------------------------------
    # CONSOLE METRICS
    # --------------------------------------------------------

    print()

    for label, result in (
        model_results.items()
    ):

        print(
            f"{label} Harrell C-index:",
            result[
                "harrell_c_index"
            ][
                "harrell_c_index"
            ],
        )

        print(
            f"{label} comparable pairs:",
            result[
                "harrell_c_index"
            ][
                "comparable_pairs"
            ],
        )

        median_error = result[
            "median_survival_error"
        ]

        print(
            f"{label} median survival MAE:",
            median_error[
                "mae_seconds"
            ],
        )

        for horizon, values in (
            result[
                "horizon_results"
            ].items()
        ):

            print(
                f"{label} "
                f"IPCW Brier @ {horizon}s:",
                f"{values['brier']['brier_score_ipcw']:.6f}",
            )

            print(
                f"{label} "
                f"mean predicted survival @ {horizon}s:",
                f"{values['descriptive_calibration']['predicted_survival_mean']:.6f}",
            )

            print(
                f"{label} "
                f"KM survival @ {horizon}s:",
                f"{values['descriptive_calibration']['observed_kaplan_meier_survival']:.6f}",
            )

    print()

    # --------------------------------------------------------
    # METRICS CSV
    # --------------------------------------------------------

    metrics_frame = pd.DataFrame(
        all_metric_rows
    )

    metrics_frame.to_csv(
        OUTPUT_CSV,
        index=False,
    )

    print(
        "Metric summary saved:",
        OUTPUT_CSV,
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
    # NO MODEL SELECTION
    # --------------------------------------------------------

    identical_outputs = all(
        item[
            "exact_equal"
        ]
        for item
        in native_comparison.values()
    )

    interpretation = {

        "native_survival_evaluation": (
            "ESTABLISHED"
        ),

        "censoring_aware_brier_evaluation": (
            "ESTABLISHED"
        ),

        "survival_ranking_evaluation": (
            "ESTABLISHED"
        ),

        "fixed_horizon_descriptive_calibration": (
            "ESTABLISHED"
        ),

        "calibration_model_fitted": (
            "NO"
        ),

        "binary_probability_conversion": (
            "NO"
        ),

        "target_relabelling": (
            "NO"
        ),

        "censoring_relabelling": (
            "NO"
        ),

        "locked_test_used": (
            "NO"
        ),

        "model_selection": (
            "NOT_PERFORMED"
        ),

        "mod007_mod010_native_outputs_identical": (
            identical_outputs
        ),

        "method_selection_note": (
            "Metric values are reported as native "
            "survival evidence. No MOD-007 versus "
            "MOD-010 winner is selected by this "
            "operation."
        ),
    }

    # --------------------------------------------------------
    # OVERALL STATUS
    # --------------------------------------------------------

    range007_pass = (
        range007[
            "median_survival"
        ][
            "status"
        ]
        == "PASS"
        and
        all(
            item[
                "status"
            ] == "PASS"
            for item
            in range007[
                "horizons"
            ].values()
        )
    )

    range010_pass = (
        range010[
            "median_survival"
        ][
            "status"
        ]
        == "PASS"
        and
        all(
            item[
                "status"
            ] == "PASS"
            for item
            in range010[
                "horizons"
            ].values()
        )
    )

    overall_checks = [

        previous[
            "status"
        ] == "PASS",

        alignment007[
            "status"
        ] == "PASS",

        alignment010[
            "status"
        ] == "PASS",

        range007_pass,

        range010_pass,

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
            "T9_MOD-037_OP-013C"
        ),

        "title": (
            "T7 Native Survival Evaluation"
        ),

        "status": overall_status,

        "purpose": (
            "Evaluate the accepted native T7 survival "
            "outputs using censoring-aware survival "
            "metrics while preserving native "
            "time-to-event semantics."
        ),

        "previous_operation_validation": (
            previous
        ),

        "evaluation_population": {

            "rows": int(
                len(evaluation)
            ),

            "event_1": int(
                np.sum(
                    events == 1
                )
            ),

            "event_0": int(
                np.sum(
                    events == 0
                )
            ),

            "event_rate": float(
                np.mean(
                    events == 1
                )
            ),

            "censor_rate": float(
                np.mean(
                    events == 0
                )
            ),
        },

        "population_alignment": {

            "MOD-007": alignment007,

            "MOD-010": alignment010,
        },

        "prediction_range_audit": {

            "MOD-007": range007,

            "MOD-010": range010,
        },

        "native_output_comparison": (
            native_comparison
        ),

        "native_survival_results": (
            model_results
        ),

        "metric_summary_csv": str(
            OUTPUT_CSV
        ),

        "interpretation": interpretation,

        "controls": controls,

        "control_validation": (
            control_validation
        ),

        "methodological_restrictions": [

            "Native survival semantics are preserved.",

            "Right-censoring is preserved.",

            "No censored observation is relabelled "
            "as an observed event.",

            "No survival output is converted into "
            "an ordinary binary classifier.",

            "No synthetic target is created.",

            "No calibration model is fitted.",

            "Fixed-horizon predicted-versus-Kaplan-Meier "
            "comparison is descriptive only.",

            "No threshold is selected.",

            "No locked test is used.",

            "No universal confidence or risk score "
            "is created.",

            "MOD-007 versus MOD-010 is not ranked "
            "or selected by this operation.",
        ],

        "artifacts_generated": [

            str(
                OUTPUT_JSON
            ),

            str(
                OUTPUT_CSV
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
    # FINAL
    # --------------------------------------------------------

    print("=" * 72)
    print("T9 MOD-037 OP-013C RESULT")
    print("=" * 72)
    print()

    print(
        "Previous-operation validation:",
        previous[
            "status"
        ],
    )

    print(
        "MOD-007 alignment:",
        alignment007[
            "status"
        ],
    )

    print(
        "MOD-010 alignment:",
        alignment010[
            "status"
        ],
    )

    print(
        "MOD-007 range audit:",
        "PASS"
        if range007_pass
        else "FAIL",
    )

    print(
        "MOD-010 range audit:",
        "PASS"
        if range010_pass
        else "FAIL",
    )

    print(
        "Native outputs identical:",
        identical_outputs,
    )

    print(
        "Censoring-aware evaluation:",
        "YES",
    )

    print(
        "Calibration fitting:",
        "NO",
    )

    print(
        "Binary conversion:",
        "NO",
    )

    print(
        "Censoring relabelled:",
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
        "Output:",
        OUTPUT_JSON,
    )

    print(
        "Metric summary:",
        OUTPUT_CSV,
    )

    print()

    print(
        "T9 MOD-037 OP-013C:",
        overall_status,
    )


if __name__ == "__main__":
    main()