from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


# ============================================================
# T9 MOD-037 OP-013E
# T7 NATIVE SURVIVAL UNCERTAINTY & RELIABILITY ANALYSIS
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T7_ROOT = PROJECT_ROOT / "modeling" / "T7"
T9_ROOT = PROJECT_ROOT / "modeling" / "T9"
OUTPUT_DIR = T9_ROOT / "mod037"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_JSON = (
    OUTPUT_DIR
    / "t9_mod037_op013e_t7_survival_uncertainty_reliability.json"
)

OUTPUT_CSV = (
    OUTPUT_DIR
    / "t9_mod037_op013e_t7_bootstrap_summary.csv"
)

OUTPUT_RELIABILITY_CSV = (
    OUTPUT_DIR
    / "t9_mod037_op013e_t7_reliability_summary.csv"
)


# ============================================================
# PRIOR T9 ARTIFACTS
# ============================================================

OP004 = (
    OUTPUT_DIR
    / "t9_mod037_op004_native_output_acceptance.json"
)

OP005 = (
    OUTPUT_DIR
    / "t9_mod037_op005_output_semantics_lock.json"
)

OP013A = (
    OUTPUT_DIR
    / "t9_mod037_op013a_t7_prior_artifact_schema.json"
)

OP013B = (
    OUTPUT_DIR
    / "t9_mod037_op013b_t7_survival_semantics_audit.json"
)

OP013C = (
    OUTPUT_DIR
    / "t9_mod037_op013c_t7_full_evidence_scan.json"
)

OP013D = (
    OUTPUT_DIR
    / "t9_mod037_op013d_t7_existing_evidence_reconciliation.json"
)


# ============================================================
# T7 EXISTING NATIVE PREDICTIONS
# ============================================================

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
# FIXED NATIVE HORIZONS
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
# BOOTSTRAP CONFIGURATION
# ============================================================

BOOTSTRAP_REPS = 1000
RANDOM_SEED = 37013
RELIABILITY_BINS = 10


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

    checks = {}

    # OP-004: T7 task-level acceptance.
    op004 = load_json(
        OP004
    )

    checks[
        "OP-004_T7_acceptance"
    ] = (
        "PASS"
        if "T7"
        in op004.get(
            "accepted_tasks",
            [],
        )
        else "FAIL"
    )

    # All subsequent T7 operations must be PASS.
    for name, path in [
        ("OP-005", OP005),
        ("OP-013A", OP013A),
        ("OP-013B", OP013B),
        ("OP-013C", OP013C),
        ("OP-013D", OP013D),
    ]:

        data = load_json(
            path
        )

        checks[
            name
        ] = (
            "PASS"
            if data.get(
                "status"
            ) == "PASS"
            else "FAIL"
        )

    failed = [
        key
        for key, value
        in checks.items()
        if value != "PASS"
    ]

    return {

        "status": (
            "PASS"
            if not failed
            else "FAIL"
        ),

        "checks": checks,

        "failed": failed,
    }


# ============================================================
# LOAD EVALUATION POPULATION
# ============================================================

def load_evaluation() -> pd.DataFrame:

    require_file(
        T7_EVAL
    )

    frame = normalize_columns(
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
            "T7 evaluation is missing required "
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

    if (
        frame[
            "duration_seconds"
        ]
        .isna()
        .any()
    ):

        raise RuntimeError(
            "Invalid duration values in T7 evaluation."
        )

    if (
        ~frame[
            "event"
        ].isin(
            [0, 1]
        )
    ).any():

        raise RuntimeError(
            "T7 event column contains values outside {0,1}."
        )

    return frame.reset_index(
        drop=True
    )


# ============================================================
# LOAD NATIVE PREDICTIONS
# ============================================================

def load_prediction(
    path: Path,
    label: str,
) -> pd.DataFrame:

    require_file(
        path
    )

    frame = normalize_columns(
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
            f"{label} is missing required native "
            f"survival fields: {missing}"
        )

    for column in required:

        frame[
            column
        ] = pd.to_numeric(
            frame[
                column
            ],
            errors="coerce",
        )

    return frame.reset_index(
        drop=True
    )


# ============================================================
# ALIGN PREDICTIONS
# ============================================================

def align_prediction(
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

        "evaluation_rows": len(
            evaluation
        ),

        "prediction_rows": len(
            prediction
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

        if set(
            eval_ids
        ) != set(
            pred_ids
        ):

            raise RuntimeError(
                f"{label} ID populations do not match."
            )

        indexed = (
            prediction
            .assign(
                __alignment_id=pred_ids
            )
            .set_index(
                "__alignment_id"
            )
        )

        aligned = (
            indexed
            .loc[
                eval_ids
            ]
            .reset_index(
                drop=True
            )
        )

        if not np.array_equal(
            aligned[
                pred_id
            ]
            .astype(str)
            .to_numpy(),
            eval_ids.to_numpy(),
        ):

            raise RuntimeError(
                f"{label} deterministic ID alignment failed."
            )

        result[
            "alignment_basis"
        ] = "exact_id_alignment"

    else:

        if len(
            evaluation
        ) != len(
            prediction
        ):

            raise RuntimeError(
                f"{label} cannot be aligned by ID or row count."
            )

        aligned = prediction.reset_index(
            drop=True
        )

        result[
            "alignment_basis"
        ] = "row_count_alignment"

    result[
        "status"
    ] = "PASS"

    return aligned, result


# ============================================================
# KAPLAN-MEIER CENSORING SURVIVAL
# ============================================================

def censoring_km(
    durations: np.ndarray,
    events: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:

    """
    Estimate G(t), the survival function of the censoring
    process.

    Original event=1 becomes censoring-event=0.
    Original event=0 becomes censoring-event=1.
    """

    censor_events = (
        1
        -
        events
    )

    order = np.argsort(
        durations
    )

    durations_sorted = durations[
        order
    ]

    censor_sorted = censor_events[
        order
    ]

    unique_times = np.unique(
        durations_sorted
    )

    at_risk = len(
        durations_sorted
    )

    survival = 1.0

    times = []
    values = []

    for time in unique_times:

        mask = (
            durations_sorted
            == time
        )

        censor_count = int(
            np.sum(
                censor_sorted[
                    mask
                ]
                == 1
            )
        )

        total_count = int(
            np.sum(
                mask
            )
        )

        if at_risk > 0:

            survival *= (
                1.0
                -
                censor_count
                /
                at_risk
            )

        times.append(
            float(time)
        )

        values.append(
            float(survival)
        )

        at_risk -= total_count

    return (
        np.asarray(
            times,
            dtype=float,
        ),
        np.asarray(
            values,
            dtype=float,
        ),
    )


def censoring_survival_before(
    time: float,
    km_times: np.ndarray,
    km_values: np.ndarray,
) -> float:

    index = np.searchsorted(
        km_times,
        time,
        side="left",
    )

    if index == 0:
        return 1.0

    return float(
        km_values[
            index - 1
        ]
    )


def censoring_survival_at(
    time: float,
    km_times: np.ndarray,
    km_values: np.ndarray,
) -> float:

    index = np.searchsorted(
        km_times,
        time,
        side="right",
    )

    if index == 0:
        return 1.0

    return float(
        km_values[
            index - 1
        ]
    )


# ============================================================
# FIXED-CENSORING IPCW COMPONENTS
# ============================================================

def build_horizon_components(
    durations: np.ndarray,
    events: np.ndarray,
    predictions: np.ndarray,
    horizon: float,
) -> dict[str, np.ndarray]:

    km_times, km_values = (
        censoring_km(
            durations,
            events,
        )
    )

    n = len(
        durations
    )

    squared_error = np.full(
        n,
        np.nan,
        dtype=float,
    )

    weight = np.zeros(
        n,
        dtype=float,
    )

    observed_outcome = np.full(
        n,
        np.nan,
        dtype=float,
    )

    prediction_used = np.full(
        n,
        np.nan,
        dtype=float,
    )

    for i in range(n):

        time_i = float(
            durations[i]
        )

        event_i = int(
            events[i]
        )

        prediction_i = float(
            predictions[i]
        )

        if not np.isfinite(
            prediction_i
        ):

            continue

        # Event observed before or at horizon.
        if (
            event_i == 1
            and
            time_i <= horizon
        ):

            g = censoring_survival_before(
                time_i,
                km_times,
                km_values,
            )

            if g <= 0:
                continue

            observed_outcome[i] = 0.0
            weight[i] = 1.0 / g

        # No event observed by horizon.
        elif time_i > horizon:

            g = censoring_survival_at(
                horizon,
                km_times,
                km_values,
            )

            if g <= 0:
                continue

            observed_outcome[i] = 1.0
            weight[i] = 1.0 / g

        # Censored before horizon:
        # no observable fixed-horizon outcome.
        else:

            continue

        prediction_used[i] = prediction_i

        squared_error[i] = (
            weight[i]
            *
            (
                observed_outcome[i]
                -
                prediction_i
            )
            ** 2
        )

    valid = np.isfinite(
        squared_error
    )

    return {

        "squared_error": squared_error,

        "weight": weight,

        "observed_outcome": observed_outcome,

        "prediction": prediction_used,

        "valid": valid,
    }


# ============================================================
# POINT ESTIMATE
# ============================================================

def weighted_brier(
    components: dict[str, np.ndarray],
) -> float:

    values = components[
        "squared_error"
    ]

    valid = components[
        "valid"
    ]

    if not valid.any():

        return float(
            "nan"
        )

    return float(
        np.mean(
            values[
                valid
            ]
        )
    )


# ============================================================
# FIXED-WEIGHT BOOTSTRAP
# ============================================================

def bootstrap_mean(
    values: np.ndarray,
    reps: int,
    rng: np.random.Generator,
) -> dict[str, Any]:

    values = values[
        np.isfinite(values)
    ]

    n = len(
        values
    )

    if n == 0:

        return {

            "point_estimate": None,

            "bootstrap_replicates": 0,

            "ci_lower": None,

            "ci_upper": None,

            "status": "NO_VALID_ROWS",
        }

    point = float(
        np.mean(
            values
        )
    )

    replicate_values = np.empty(
        reps,
        dtype=float,
    )

    chunk_size = 100

    for start in range(
        0,
        reps,
        chunk_size,
    ):

        end = min(
            start + chunk_size,
            reps,
        )

        size = end - start

        indices = rng.integers(
            0,
            n,
            size=(
                size,
                n,
            ),
        )

        replicate_values[
            start:end
        ] = np.mean(
            values[
                indices
            ],
            axis=1,
        )

    lower, upper = np.quantile(
        replicate_values,
        [
            0.025,
            0.975,
        ],
    )

    return {

        "point_estimate": point,

        "bootstrap_replicates": reps,

        "ci_lower_95": float(
            lower
        ),

        "ci_upper_95": float(
            upper
        ),

        "bootstrap_mean": float(
            np.mean(
                replicate_values
            )
        ),

        "bootstrap_std": float(
            np.std(
                replicate_values,
                ddof=1,
            )
        ),

        "status": "PASS",
    }


# ============================================================
# RELIABILITY BINS
# ============================================================

def reliability_summary(
    prediction: np.ndarray,
    components: dict[str, np.ndarray],
    bins: int,
) -> pd.DataFrame:

    valid = components[
        "valid"
    ]

    pred = prediction[
        valid
    ]

    outcome = components[
        "observed_outcome"
    ][
        valid
    ]

    weights = components[
        "weight"
    ][
        valid
    ]

    if len(pred) == 0:

        return pd.DataFrame()

    # Quantile bins based only on native predicted survival.
    edges = np.quantile(
        pred,
        np.linspace(
            0,
            1,
            bins + 1,
        ),
    )

    edges = np.unique(
        edges
    )

    if len(edges) < 2:

        return pd.DataFrame(
            [
                {
                    "bin": 1,
                    "rows": len(pred),
                    "predicted_mean": float(
                        np.mean(pred)
                    ),
                    "weighted_observed_mean": float(
                        np.average(
                            outcome,
                            weights=weights,
                        )
                    ),
                    "absolute_gap": abs(
                        float(
                            np.mean(pred)
                        )
                        -
                        float(
                            np.average(
                                outcome,
                                weights=weights,
                            )
                        )
                    ),
                }
            ]
        )

    bin_ids = np.digitize(
        pred,
        edges[
            1:-1
        ],
        right=True,
    )

    rows = []

    for bin_id in sorted(
        np.unique(
            bin_ids
        )
    ):

        mask = (
            bin_ids
            ==
            bin_id
        )

        pred_mean = float(
            np.mean(
                pred[
                    mask
                ]
            )
        )

        observed_mean = float(
            np.average(
                outcome[
                    mask
                ],
                weights=weights[
                    mask
                ],
            )
        )

        rows.append(
            {

                "bin": int(
                    bin_id + 1
                ),

                "rows": int(
                    np.sum(
                        mask
                    )
                ),

                "predicted_mean": pred_mean,

                "weighted_observed_mean": (
                    observed_mean
                ),

                "absolute_gap": abs(
                    pred_mean
                    -
                    observed_mean
                ),
            }
        )

    return pd.DataFrame(
        rows
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 72)
    print(
        "T9 MOD-037 OP-013E"
    )
    print(
        "T7 NATIVE SURVIVAL UNCERTAINTY "
        "& RELIABILITY ANALYSIS"
    )
    print("=" * 72)
    print()

    # --------------------------------------------------------
    # PRIOR VALIDATION
    # --------------------------------------------------------

    print(
        "Validating prior T9 operations..."
    )

    prior = validate_prior_operations()

    print(
        "Prior-operation validation:",
        prior[
            "status"
        ],
    )

    if prior[
        "status"
    ] != "PASS":

        print(
            "Failed:",
            prior[
                "failed"
            ],
        )

        raise RuntimeError(
            "Prior-operation validation failed."
        )

    print()

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    print(
        "Loading T7 evaluation population..."
    )

    evaluation = load_evaluation()

    print(
        "T7 evaluation rows:",
        len(
            evaluation
        ),
    )

    print()

    print(
        "Loading MOD-007 native predictions..."
    )

    mod007 = load_prediction(
        T7_MOD007,
        "MOD-007",
    )

    print(
        "MOD-007 rows:",
        len(
            mod007
        ),
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
        len(
            mod010
        ),
    )

    print()

    # --------------------------------------------------------
    # ALIGNMENT
    # --------------------------------------------------------

    mod007, alignment007 = align_prediction(
        evaluation,
        mod007,
        "MOD-007",
    )

    mod010, alignment010 = align_prediction(
        evaluation,
        mod010,
        "MOD-010",
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

    print()

    # --------------------------------------------------------
    # NATIVE ARRAYS
    # --------------------------------------------------------

    durations = (
        evaluation[
            "duration_seconds"
        ]
        .to_numpy(
            dtype=float
        )
    )

    events = (
        evaluation[
            "event"
        ]
        .to_numpy(
            dtype=int
        )
    )

    rng = np.random.default_rng(
        RANDOM_SEED
    )

    bootstrap_rows = []
    reliability_frames = []

    # --------------------------------------------------------
    # HORIZON ANALYSIS
    # --------------------------------------------------------

    for label, prediction_frame in [
        (
            "MOD-007",
            mod007,
        ),
        (
            "MOD-010",
            mod010,
        ),
    ]:

        print(
            f"Analyzing {label}..."
        )

        for horizon, column in HORIZONS.items():

            print(
                f"  Horizon {horizon} seconds..."
            )

            predicted = (
                prediction_frame[
                    column
                ]
                .to_numpy(
                    dtype=float
                )
            )

            components = build_horizon_components(
                durations,
                events,
                predicted,
                horizon,
            )

            valid = components[
                "valid"
            ]

            if not valid.any():

                raise RuntimeError(
                    f"No evaluable observations for "
                    f"{label} at horizon {horizon}."
                )

            point = weighted_brier(
                components
            )

            bootstrap = bootstrap_mean(
                components[
                    "squared_error"
                ][
                    valid
                ],
                BOOTSTRAP_REPS,
                rng,
            )

            reliability = reliability_summary(
                predicted,
                components,
                RELIABILITY_BINS,
            )

            if reliability.empty:

                raise RuntimeError(
                    f"Reliability analysis produced "
                    f"no bins for {label} at "
                    f"horizon {horizon}."
                )

            reliability.insert(
                0,
                "artifact",
                label,
            )

            reliability.insert(
                1,
                "horizon_seconds",
                horizon,
            )

            reliability_frames.append(
                reliability
            )

            bootstrap_rows.append(
                {

                    "artifact": label,

                    "horizon_seconds": horizon,

                    "metric": "IPCW_Brier_fixed_weight_bootstrap",

                    "point_estimate": point,

                    "ci_lower_95": bootstrap[
                        "ci_lower_95"
                    ],

                    "ci_upper_95": bootstrap[
                        "ci_upper_95"
                    ],

                    "bootstrap_std": bootstrap[
                        "bootstrap_std"
                    ],

                    "bootstrap_replicates": (
                        BOOTSTRAP_REPS
                    ),

                    "evaluated_rows": int(
                        np.sum(
                            valid
                        )
                    ),

                    "evaluation_fraction": float(
                        np.mean(
                            valid
                        )
                    ),
                }
            )

            print(
                "    point Brier:",
                f"{point:.6f}",
            )

            print(
                "    95% CI:",
                (
                    f"["
                    f"{bootstrap['ci_lower_95']:.6f}, "
                    f"{bootstrap['ci_upper_95']:.6f}"
                    f"]"
                ),
            )

    # --------------------------------------------------------
    # RELIABILITY AGGREGATION
    # --------------------------------------------------------

    reliability_frame = pd.concat(
        reliability_frames,
        ignore_index=True,
    )

    reliability_frame.to_csv(
        OUTPUT_RELIABILITY_CSV,
        index=False,
    )

    bootstrap_frame = pd.DataFrame(
        bootstrap_rows
    )

    bootstrap_frame.to_csv(
        OUTPUT_CSV,
        index=False,
    )

    print()

    print(
        "Bootstrap summary saved:",
        OUTPUT_CSV,
    )

    print(
        "Reliability summary saved:",
        OUTPUT_RELIABILITY_CSV,
    )

    print()

    # --------------------------------------------------------
    # GLOBAL RELIABILITY SUMMARY
    # --------------------------------------------------------

    reliability_global = []

    for (
        artifact,
        horizon,
    ), group in reliability_frame.groupby(
        [
            "artifact",
            "horizon_seconds",
        ]
    ):

        weighted_gap = np.average(
            group[
                "absolute_gap"
            ],
            weights=group[
                "rows"
            ],
        )

        max_gap = float(
            group[
                "absolute_gap"
            ].max()
        )

        reliability_global.append(
            {

                "artifact": artifact,

                "horizon_seconds": int(
                    horizon
                ),

                "bins": int(
                    len(group)
                ),

                "weighted_mean_absolute_gap": float(
                    weighted_gap
                ),

                "maximum_bin_absolute_gap": max_gap,

                "smallest_bin_rows": int(
                    group[
                        "rows"
                    ].min()
                ),

                "largest_bin_rows": int(
                    group[
                        "rows"
                    ].max()
                ),
            }
        )

    reliability_global_frame = pd.DataFrame(
        reliability_global
    )

    # --------------------------------------------------------
    # CONTROLS
    # --------------------------------------------------------

    controls = {

        "artifact_read_only": True,

        "model_fitted": False,

        "prediction_generated": False,

        "probability_generated": False,

        "calibration_fitted": False,

        "target_created": False,

        "target_relabelled": False,

        "censoring_relabelled": False,

        "survival_to_binary_conversion": False,

        "threshold_selected": False,

        "model_selected": False,

        "locked_test_used": False,

        "universal_confidence_created": False,

        "universal_risk_score_created": False,

        "existing_t7_artifacts_modified": False,

        "post_creation_information_used": False,

        "native_survival_semantics_preserved": True,

        "censoring_aware_evaluation_preserved": True,

        "fixed_censoring_weights_used_for_bootstrap": True,
    }

    allowed_true = {
        "artifact_read_only",
        "native_survival_semantics_preserved",
        "censoring_aware_evaluation_preserved",
        "fixed_censoring_weights_used_for_bootstrap",
    }

    control_failures = []

    for key, value in controls.items():

        if key in allowed_true:

            if value is not True:

                control_failures.append(
                    key
                )

        elif value is not False:

            control_failures.append(
                key
            )

    control_status = (
        "PASS"
        if not control_failures
        else "FAIL"
    )

    print(
        "Control validation:",
        control_status,
    )

    if control_status != "PASS":

        raise RuntimeError(
            "Control validation failed."
        )

    # --------------------------------------------------------
    # INTERPRETATION
    # --------------------------------------------------------

    interpretation = {

        "uncertainty_type": (
            "Fixed-censoring-weight bootstrap "
            "uncertainty around existing native "
            "fixed-horizon IPCW Brier contributions."
        ),

        "formal_calibration": (
            "NOT_ESTABLISHED"
        ),

        "reliability_status": (
            "DESCRIPTIVE_NATIVE_SURVIVAL_RELIABILITY"
        ),

        "binary_conversion": (
            "NO"
        ),

        "censoring_relabelling": (
            "NO"
        ),

        "model_selection": (
            "NO"
        ),

        "method_selection": (
            "NO"
        ),

        "locked_test_use": (
            "NO"
        ),

        "universal_confidence": (
            "NOT_CREATED"
        ),

        "universal_risk_score": (
            "NOT_CREATED"
        ),

        "bootstrap_limitation": (
            "Bootstrap uncertainty conditions on the "
            "full-sample censoring-weight structure. "
            "It does not re-estimate the censoring "
            "survival function inside every replicate."
        ),

        "reliability_limitation": (
            "Bin-level weighted observed survival "
            "comparisons are descriptive reliability "
            "evidence, not a fitted formal survival "
            "calibration model."
        ),

        "mod007_mod010_selection": (
            "No model is selected."
        ),
    }

    # --------------------------------------------------------
    # OVERALL STATUS
    # --------------------------------------------------------

    overall_status = (
        "PASS"
        if (
            prior[
                "status"
            ] == "PASS"
            and
            alignment007[
                "status"
            ] == "PASS"
            and
            alignment010[
                "status"
            ] == "PASS"
            and
            control_status
            == "PASS"
            and
            len(
                bootstrap_rows
            )
            == (
                2
                *
                len(
                    HORIZONS
                )
            )
        )
        else "FAIL"
    )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    output = {

        "operation": (
            "T9_MOD-037_OP-013E"
        ),

        "title": (
            "T7 Native Survival Uncertainty "
            "& Reliability Analysis"
        ),

        "status": overall_status,

        "purpose": (
            "Quantify uncertainty and descriptive "
            "reliability around already-established "
            "native T7 fixed-horizon survival outputs "
            "without fitting a new model or converting "
            "the survival task into binary classification."
        ),

        "previous_operation_validation": prior,

        "evaluation_population": {

            "rows": int(
                len(evaluation)
            ),

            "events": int(
                np.sum(
                    events == 1
                )
            ),

            "censored": int(
                np.sum(
                    events == 0
                )
            ),

            "event_rate": float(
                np.mean(
                    events == 1
                ),
            ),

            "censor_rate": float(
                np.mean(
                    events == 0
                ),
            ),
        },

        "alignment": {

            "MOD-007": alignment007,

            "MOD-010": alignment010,
        },

        "bootstrap_configuration": {

            "replicates": BOOTSTRAP_REPS,

            "seed": RANDOM_SEED,

            "confidence_interval": "95%",

            "reliability_bins": RELIABILITY_BINS,

            "weight_structure": (
                "fixed full-sample censoring "
                "survival weights"
            ),
        },

        "bootstrap_results": bootstrap_rows,

        "reliability_global": (
            reliability_global_frame.to_dict(
                orient="records"
            )
        ),

        "bootstrap_summary_csv": str(
            OUTPUT_CSV
        ),

        "reliability_summary_csv": str(
            OUTPUT_RELIABILITY_CSV
        ),

        "interpretation": interpretation,

        "controls": controls,

        "control_validation": {

            "status": control_status,

            "failed_controls": control_failures,
        },

        "methodological_restrictions": [

            "Existing native T7 survival outputs "
            "are evaluated as-is.",

            "Right censoring is preserved.",

            "No censored observation is relabelled "
            "as an observed event.",

            "No survival quantity is converted "
            "into a binary classifier.",

            "No calibration model is fitted.",

            "No model is selected.",

            "No threshold is selected.",

            "No locked test is used.",

            "No universal confidence score is created.",

            "No universal risk score is created.",

            "Bootstrap uncertainty is explicitly "
            "conditional on the fixed full-sample "
            "censoring-weight structure.",
        ],

        "artifacts_generated": [

            str(
                OUTPUT_JSON
            ),

            str(
                OUTPUT_CSV
            ),

            str(
                OUTPUT_RELIABILITY_CSV
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

    print()
    print("=" * 72)
    print(
        "T9 MOD-037 OP-013E RESULT"
    )
    print("=" * 72)
    print()

    print(
        "Prior-operation validation:",
        prior[
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
        "Bootstrap replicates:",
        BOOTSTRAP_REPS,
    )

    print(
        "Bootstrap seed:",
        RANDOM_SEED,
    )

    print(
        "Formal calibration fitting:",
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

    print(
        "Control validation:",
        control_status,
    )

    print()

    print(
        "Output:",
        OUTPUT_JSON,
    )

    print(
        "Bootstrap summary:",
        OUTPUT_CSV,
    )

    print(
        "Reliability summary:",
        OUTPUT_RELIABILITY_CSV,
    )

    print()

    print(
        "T9 MOD-037 OP-013E:",
        overall_status,
    )


if __name__ == "__main__":
    main()