from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
)


# ============================================================
# T9 MOD-037 OP-008
# T5 Empirical Calibration Evaluation
#
# Purpose:
#   Execute the frozen T5 calibration/evaluation protocol
#   established in OP-007.
#
# This operation evaluates EXISTING native probability
# representations:
#
#   p_base
#   p_sigmoid
#   p_isotonic
#
# It does NOT fit a new calibration model.
#
# It does NOT:
#   - create targets
#   - alter target prevalence
#   - select automation thresholds
#   - use locked test data
#   - create universal confidence/risk
#   - compare T5 probabilities with other task quantities
#
# Primary metrics:
#   - Brier score
#   - Log loss
#
# Supporting:
#   - ECE
#   - MCE
#   - ROC-AUC
#   - Average Precision
#
# Uncertainty:
#   - Bootstrap 95% confidence intervals
#
# Reliability:
#   - Fixed probability bins
#   - Per-bin count, mean prediction,
#     observed event rate, absolute gap
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
    / "t9_mod037_op008_t5_empirical_calibration.json"
)

RELIABILITY_CSV = (
    OUTPUT_DIR
    / "t9_mod037_op008_t5_reliability_bins.csv"
)

BOOTSTRAP_CSV = (
    OUTPUT_DIR
    / "t9_mod037_op008_t5_bootstrap_summary.csv"
)

OP005_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op005_output_semantics_lock.json"
)

OP006_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op006_t5_calibration_population_audit.json"
)

OP007_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op007_t5_calibration_protocol.json"
)

T5_PROBABILITY_ARTIFACT = (
    PROJECT_ROOT
    / "modeling"
    / "T5"
    / "metrics"
    / "t5_mod007_calibrated_validation_predictions.npz"
)

T5_POPULATION_ARTIFACT = (
    PROJECT_ROOT
    / "modeling"
    / "T5"
    / "splits"
    / "t5_model_val.csv"
)


# ============================================================
# Frozen analysis settings
# ============================================================

RANDOM_STATE = 42

N_BOOTSTRAPS = 1000

# Fixed bins.
# These are defined before observing the empirical results.
BIN_EDGES = np.array(
    [
        0.0,
        0.01,
        0.05,
        0.10,
        0.20,
        0.30,
        0.40,
        0.50,
        0.60,
        0.70,
        0.80,
        0.90,
        0.95,
        0.99,
        1.00,
    ],
    dtype=float,
)


PROBABILITY_FIELDS = [
    "p_base",
    "p_sigmoid",
    "p_isotonic",
]


# ============================================================
# Utility
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

        return json.load(f)


def clip_probabilities(
    values: np.ndarray,
) -> np.ndarray:

    return np.clip(
        values.astype(float),
        1e-15,
        1.0 - 1e-15,
    )


# ============================================================
# Previous-operation validation
# ============================================================

def validate_previous_operations() -> dict[str, Any]:

    op005 = load_json(
        OP005_ARTIFACT
    )

    op006 = load_json(
        OP006_ARTIFACT
    )

    op007 = load_json(
        OP007_ARTIFACT
    )

    checks = {}

    # --------------------------------------------------------
    # OP-005
    # --------------------------------------------------------

    checks["OP-005"] = {
        "status": (
            "PASS"
            if op005.get("status") == "PASS"
            else "FAIL"
        ),
        "observed": op005.get(
            "status"
        ),
    }

    # --------------------------------------------------------
    # OP-006
    # --------------------------------------------------------

    checks["OP-006"] = {
        "status": (
            "PASS"
            if op006.get("status") == "PASS"
            else "FAIL"
        ),
        "observed": op006.get(
            "status"
        ),
    }

    # --------------------------------------------------------
    # OP-007
    # --------------------------------------------------------

    checks["OP-007"] = {
        "status": (
            "PASS"
            if op007.get("status") == "PASS"
            else "FAIL"
        ),
        "observed": op007.get(
            "status"
        ),
    }

    # --------------------------------------------------------
    # OP-007 must remain design-only
    # --------------------------------------------------------

    frozen_protocol = op007.get(
        "frozen_protocol",
        {},
    )

    checks[
        "OP-007_no_calibration_fitting"
    ] = {
        "status": (
            "PASS"
            if op007.get(
                "calibration_fitting_performed"
            )
            is False
            else "FAIL"
        ),
    }

    checks[
        "OP-007_no_threshold_selection"
    ] = {
        "status": (
            "PASS"
            if op007.get(
                "threshold_selection_performed"
            )
            is False
            else "FAIL"
        ),
    }

    checks[
        "OP-007_locked_test_isolated"
    ] = {
        "status": (
            "PASS"
            if op007.get(
                "locked_test_used_for_selection"
            )
            is False
            else "FAIL"
        ),
    }

    # --------------------------------------------------------
    # Protocol settings must match this operation
    # --------------------------------------------------------

    protocol_metrics = (
        frozen_protocol
        .get(
            "calibration_metrics",
            {},
        )
        .get(
            "primary",
            [],
        )
    )

    checks[
        "protocol_primary_metrics"
    ] = {
        "status": (
            "PASS"
            if set(protocol_metrics)
            == {
                "Brier score",
                "Log loss",
            }
            else "FAIL"
        ),
        "observed": protocol_metrics,
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


# ============================================================
# Load native T5 data
# ============================================================

def load_native_data() -> dict[str, Any]:

    if not T5_PROBABILITY_ARTIFACT.exists():
        raise FileNotFoundError(
            f"T5 probability artifact missing: "
            f"{T5_PROBABILITY_ARTIFACT}"
        )

    if not T5_POPULATION_ARTIFACT.exists():
        raise FileNotFoundError(
            f"T5 population artifact missing: "
            f"{T5_POPULATION_ARTIFACT}"
        )

    with np.load(
        T5_PROBABILITY_ARTIFACT,
        allow_pickle=False,
    ) as data:

        y_true = np.asarray(
            data["y_true"],
            dtype=float,
        )

        probabilities = {
            field: np.asarray(
                data[field],
                dtype=float,
            )
            for field
            in PROBABILITY_FIELDS
        }

    population = pd.read_csv(
        T5_POPULATION_ARTIFACT
    )

    return {
        "y_true": y_true,
        "probabilities": probabilities,
        "population": population,
    }


# ============================================================
# Native data validation
# ============================================================

def validate_native_data(
    data: dict[str, Any],
) -> dict[str, Any]:

    y_true = data["y_true"]
    probabilities = data["probabilities"]
    population = data["population"]

    checks = {}

    checks["population_rows"] = {
        "status": (
            "PASS"
            if len(population) == 74091
            else "FAIL"
        ),
        "observed": int(
            len(population)
        ),
    }

    checks["population_unique_ids"] = {
        "status": (
            "PASS"
            if (
                population["ID"]
                .nunique()
                == 74091
            )
            else "FAIL"
        ),
        "observed": int(
            population["ID"].nunique()
        ),
    }

    checks["population_duplicate_ids"] = {
        "status": (
            "PASS"
            if (
                population["ID"]
                .duplicated()
                .sum()
                == 0
            )
            else "FAIL"
        ),
        "observed": int(
            population["ID"]
            .duplicated()
            .sum()
        ),
    }

    checks["target_length"] = {
        "status": (
            "PASS"
            if len(y_true) == 74091
            else "FAIL"
        ),
        "observed": int(
            len(y_true)
        ),
    }

    target_values = set(
        np.unique(y_true).tolist()
    )

    checks["binary_target"] = {
        "status": (
            "PASS"
            if target_values.issubset(
                {0.0, 1.0}
            )
            else "FAIL"
        ),
        "observed": sorted(
            target_values
        ),
    }

    expected_counts = {
        0.0: 73611,
        1.0: 480,
    }

    observed_counts = {
        float(value): int(
            np.sum(
                y_true == value
            )
        )
        for value
        in [0.0, 1.0]
    }

    checks["target_distribution"] = {
        "status": (
            "PASS"
            if observed_counts
            == expected_counts
            else "FAIL"
        ),
        "expected": expected_counts,
        "observed": observed_counts,
    }

    for field in PROBABILITY_FIELDS:

        values = probabilities[field]

        checks[
            f"{field}_length"
        ] = {
            "status": (
                "PASS"
                if len(values)
                == len(y_true)
                else "FAIL"
            ),
            "observed": int(
                len(values)
            ),
        }

        checks[
            f"{field}_finite"
        ] = {
            "status": (
                "PASS"
                if np.isfinite(values).all()
                else "FAIL"
            ),
        }

        checks[
            f"{field}_range"
        ] = {
            "status": (
                "PASS"
                if (
                    np.all(values >= 0.0)
                    and
                    np.all(values <= 1.0)
                )
                else "FAIL"
            ),
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


# ============================================================
# Calibration metrics
# ============================================================

def expected_calibration_error(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    bin_edges: np.ndarray,
) -> tuple[float, float, list[dict[str, Any]]]:

    y_true = np.asarray(
        y_true,
        dtype=float,
    )

    probabilities = np.asarray(
        probabilities,
        dtype=float,
    )

    total = len(
        y_true
    )

    weighted_error = 0.0
    maximum_error = 0.0

    rows = []

    for index in range(
        len(bin_edges) - 1
    ):

        left = bin_edges[index]
        right = bin_edges[index + 1]

        if index == len(
            bin_edges
        ) - 2:

            mask = (
                (probabilities >= left)
                &
                (probabilities <= right)
            )

        else:

            mask = (
                (probabilities >= left)
                &
                (probabilities < right)
            )

        count = int(
            np.sum(mask)
        )

        if count == 0:

            rows.append(
                {
                    "bin_index": index,
                    "bin_left": float(left),
                    "bin_right": float(right),
                    "count": 0,
                    "mean_predicted": np.nan,
                    "observed_event_rate": np.nan,
                    "absolute_gap": np.nan,
                    "weighted_gap": np.nan,
                }
            )

            continue

        mean_predicted = float(
            np.mean(
                probabilities[mask]
            )
        )

        observed_rate = float(
            np.mean(
                y_true[mask]
            )
        )

        absolute_gap = abs(
            mean_predicted
            - observed_rate
        )

        weighted_gap = (
            count / total
        ) * absolute_gap

        weighted_error += (
            weighted_gap
        )

        maximum_error = max(
            maximum_error,
            absolute_gap,
        )

        rows.append(
            {
                "bin_index": index,
                "bin_left": float(left),
                "bin_right": float(right),
                "count": count,
                "mean_predicted": mean_predicted,
                "observed_event_rate": observed_rate,
                "absolute_gap": absolute_gap,
                "weighted_gap": weighted_gap,
            }
        )

    return (
        float(weighted_error),
        float(maximum_error),
        rows,
    )


def compute_metrics(
    y_true: np.ndarray,
    probabilities: np.ndarray,
) -> dict[str, float]:

    p = clip_probabilities(
        probabilities
    )

    brier = float(
        brier_score_loss(
            y_true,
            p,
        )
    )

    loss = float(
        log_loss(
            y_true,
            p,
            labels=[0, 1],
        )
    )

    roc_auc = float(
        roc_auc_score(
            y_true,
            p,
        )
    )

    average_precision = float(
        average_precision_score(
            y_true,
            p,
        )
    )

    ece, mce, _ = (
        expected_calibration_error(
            y_true,
            p,
            BIN_EDGES,
        )
    )

    return {
        "brier_score": brier,
        "log_loss": loss,
        "ece": ece,
        "mce": mce,
        "roc_auc": roc_auc,
        "average_precision": average_precision,
    }


# ============================================================
# Bootstrap uncertainty
# ============================================================

def bootstrap_metrics(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    n_bootstraps: int,
    random_state: int,
) -> dict[str, Any]:

    rng = np.random.default_rng(
        random_state
    )

    n = len(
        y_true
    )

    metric_names = [
        "brier_score",
        "log_loss",
        "ece",
        "mce",
        "roc_auc",
        "average_precision",
    ]

    values = {
        metric: []
        for metric
        in metric_names
    }

    # --------------------------------------------------------
    # Stratified bootstrap
    #
    # Preserve the observed binary class composition in each
    # bootstrap replicate so that the extremely rare positive
    # class is not randomly absent from a replicate.
    # --------------------------------------------------------

    negative_indices = np.flatnonzero(
        y_true == 0
    )

    positive_indices = np.flatnonzero(
        y_true == 1
    )

    for _ in range(
        n_bootstraps
    ):

        sampled_negative = rng.choice(
            negative_indices,
            size=len(
                negative_indices
            ),
            replace=True,
        )

        sampled_positive = rng.choice(
            positive_indices,
            size=len(
                positive_indices
            ),
            replace=True,
        )

        indices = np.concatenate(
            [
                sampled_negative,
                sampled_positive,
            ]
        )

        # Shuffle the resulting sample.
        rng.shuffle(
            indices
        )

        y_boot = y_true[
            indices
        ]

        p_boot = probabilities[
            indices
        ]

        metrics = compute_metrics(
            y_boot,
            p_boot,
        )

        for metric in metric_names:

            values[metric].append(
                metrics[metric]
            )

    summary = {}

    for metric in metric_names:

        array = np.asarray(
            values[metric],
            dtype=float,
        )

        summary[metric] = {
            "bootstrap_replicates": int(
                len(array)
            ),
            "mean": float(
                np.mean(array)
            ),
            "std": float(
                np.std(
                    array,
                    ddof=1,
                )
            ),
            "ci_95_lower": float(
                np.percentile(
                    array,
                    2.5,
                )
            ),
            "ci_95_upper": float(
                np.percentile(
                    array,
                    97.5,
                )
            ),
        }

    return summary


# ============================================================
# Reliability table
# ============================================================

def reliability_table(
    y_true: np.ndarray,
    probability_map: dict[str, np.ndarray],
) -> pd.DataFrame:

    rows = []

    for field, probabilities in (
        probability_map.items()
    ):

        _, _, bins = (
            expected_calibration_error(
                y_true,
                probabilities,
                BIN_EDGES,
            )
        )

        for row in bins:

            row_copy = dict(
                row
            )

            row_copy[
                "probability_field"
            ] = field

            rows.append(
                row_copy
            )

    columns = [
        "probability_field",
        "bin_index",
        "bin_left",
        "bin_right",
        "count",
        "mean_predicted",
        "observed_event_rate",
        "absolute_gap",
        "weighted_gap",
    ]

    return pd.DataFrame(
        rows,
        columns=columns,
    )


# ============================================================
# Main
# ============================================================

def main() -> None:

    print("=" * 72)
    print("T9 MOD-037 OP-008")
    print("T5 Empirical Calibration Evaluation")
    print("=" * 72)
    print()

    # --------------------------------------------------------
    # Previous operation validation
    # --------------------------------------------------------

    print(
        "Validating frozen T9 protocol..."
    )

    previous = (
        validate_previous_operations()
    )

    print(
        "Previous-operation validation:",
        previous["status"],
    )

    if previous["status"] != "PASS":

        raise RuntimeError(
            "Frozen T9 protocol validation failed. "
            "No empirical evaluation performed."
        )

    print()

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    print(
        "Loading native T5 probability artifact..."
    )

    data = load_native_data()

    y_true = data[
        "y_true"
    ]

    probabilities = data[
        "probabilities"
    ]

    population = data[
        "population"
    ]

    print(
        "Loaded T5 population:",
        len(population),
    )

    print(
        "Loaded probability representations:",
        ", ".join(
            PROBABILITY_FIELDS
        ),
    )

    print()

    # --------------------------------------------------------
    # Native data validation
    # --------------------------------------------------------

    print(
        "Validating native T5 evaluation population..."
    )

    native_validation = (
        validate_native_data(
            data
        )
    )

    print(
        "Native-data validation:",
        native_validation["status"],
    )

    if native_validation[
        "status"
    ] != "PASS":

        raise RuntimeError(
            "Native T5 validation failed. "
            "No empirical metrics generated."
        )

    print()

    # --------------------------------------------------------
    # Evaluate each native representation
    # --------------------------------------------------------

    metrics_by_probability = {}

    reliability_frames = []

    bootstrap_rows = []

    for field in PROBABILITY_FIELDS:

        print(
            f"Evaluating {field}..."
        )

        p = probabilities[
            field
        ]

        metrics = compute_metrics(
            y_true,
            p,
        )

        bootstrap = bootstrap_metrics(
            y_true,
            p,
            N_BOOTSTRAPS,
            RANDOM_STATE,
        )

        metrics_by_probability[
            field
        ] = {
            "point_estimates": metrics,
            "bootstrap_95_ci": bootstrap,
        }

        reliability_frames.append(
            reliability_table(
                y_true,
                {
                    field: p,
                },
            )
        )

        for metric_name, result in (
            bootstrap.items()
        ):

            bootstrap_rows.append(
                {
                    "probability_field": field,
                    "metric": metric_name,
                    "bootstrap_replicates": result[
                        "bootstrap_replicates"
                    ],
                    "mean": result[
                        "mean"
                    ],
                    "std": result[
                        "std"
                    ],
                    "ci_95_lower": result[
                        "ci_95_lower"
                    ],
                    "ci_95_upper": result[
                        "ci_95_upper"
                    ],
                }
            )

        print(
            f"  Brier: "
            f"{metrics['brier_score']:.6f}"
        )

        print(
            f"  Log loss: "
            f"{metrics['log_loss']:.6f}"
        )

        print(
            f"  ECE: "
            f"{metrics['ece']:.6f}"
        )

        print(
            f"  MCE: "
            f"{metrics['mce']:.6f}"
        )

        print(
            f"  ROC-AUC: "
            f"{metrics['roc_auc']:.6f}"
        )

        print(
            f"  Average Precision: "
            f"{metrics['average_precision']:.6f}"
        )

        print()

    # --------------------------------------------------------
    # Save reliability data
    # --------------------------------------------------------

    reliability_df = pd.concat(
        reliability_frames,
        ignore_index=True,
    )

    reliability_df.to_csv(
        RELIABILITY_CSV,
        index=False,
    )

    # --------------------------------------------------------
    # Save bootstrap summary
    # --------------------------------------------------------

    bootstrap_df = pd.DataFrame(
        bootstrap_rows
    )

    bootstrap_df.to_csv(
        BOOTSTRAP_CSV,
        index=False,
    )

    # --------------------------------------------------------
    # Probability distribution summaries
    # --------------------------------------------------------

    probability_distributions = {}

    for field in PROBABILITY_FIELDS:

        p = probabilities[
            field
        ]

        probability_distributions[
            field
        ] = {
            "min": float(
                np.min(p)
            ),
            "max": float(
                np.max(p)
            ),
            "mean": float(
                np.mean(p)
            ),
            "median": float(
                np.median(p)
            ),
            "std": float(
                np.std(
                    p,
                    ddof=1,
                )
            ),
            "quantiles": {
                "0.01": float(
                    np.quantile(
                        p,
                        0.01,
                    )
                ),
                "0.05": float(
                    np.quantile(
                        p,
                        0.05,
                    )
                ),
                "0.25": float(
                    np.quantile(
                        p,
                        0.25,
                    )
                ),
                "0.50": float(
                    np.quantile(
                        p,
                        0.50,
                    )
                ),
                "0.75": float(
                    np.quantile(
                        p,
                        0.75,
                    )
                ),
                "0.95": float(
                    np.quantile(
                        p,
                        0.95,
                    )
                ),
                "0.99": float(
                    np.quantile(
                        p,
                        0.99,
                    )
                ),
            },
        }

    # --------------------------------------------------------
    # Basic empirical comparison
    #
    # This is descriptive only.
    # No "winner" is declared by this operation.
    # --------------------------------------------------------

    metric_table = []

    for field in PROBABILITY_FIELDS:

        point = metrics_by_probability[
            field
        ]["point_estimates"]

        metric_table.append(
            {
                "probability_field": field,
                **point,
            }
        )

    # --------------------------------------------------------
    # Control assertions
    # --------------------------------------------------------

    controls = {

        "model_fitting_performed": False,

        "new_probability_generation_performed": False,

        "calibration_fitting_performed": False,

        "target_creation_performed": False,

        "target_relabelling_performed": False,

        "threshold_selection_performed": False,

        "automation_threshold_selected": False,

        "review_threshold_selected": False,

        "universal_confidence_created": False,

        "universal_risk_score_created": False,

        "cross_task_probability_averaging_performed": False,

        "arbitrary_cross_task_weights_used": False,

        "locked_test_used": False,

        "post_creation_information_used": False,

        "native_t5_target_preserved": True,

        "native_t5_probability_semantics_preserved": True,

        "observed_validation_prevalence_preserved": True,
    }

    control_failures = []

    false_required = [
        key
        for key, value
        in controls.items()
        if (
            key
            not in {
                "native_t5_target_preserved",
                "native_t5_probability_semantics_preserved",
                "observed_validation_prevalence_preserved",
            }
            and value is not False
        )
    ]

    true_required = [
        key
        for key in [
            "native_t5_target_preserved",
            "native_t5_probability_semantics_preserved",
            "observed_validation_prevalence_preserved",
        ]
        if controls[key] is not True
    ]

    control_failures.extend(
        false_required
    )

    control_failures.extend(
        true_required
    )

    controls_status = (
        "PASS"
        if not control_failures
        else "FAIL"
    )

    # --------------------------------------------------------
    # Final operation status
    # --------------------------------------------------------

    overall_pass = (
        previous["status"] == "PASS"
        and
        native_validation["status"] == "PASS"
        and
        controls_status == "PASS"
        and
        len(metrics_by_probability)
        == 3
    )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    output = {

        "operation": "T9_MOD-037_OP-008",

        "title": (
            "T5 Empirical Calibration Evaluation"
        ),

        "status": (
            "PASS"
            if overall_pass
            else "FAIL"
        ),

        "operation_type": (
            "EMPIRICAL_EVALUATION_OF_EXISTING_NATIVE_OUTPUTS"
        ),

        "previous_operation_validation": previous,

        "native_data_validation": native_validation,

        "population": {
            "rows": int(
                len(population)
            ),
            "unique_ids": int(
                population["ID"].nunique()
            ),
            "duplicate_ids": int(
                population["ID"]
                .duplicated()
                .sum()
            ),
            "positive_targets": int(
                np.sum(
                    y_true == 1
                )
            ),
            "negative_targets": int(
                np.sum(
                    y_true == 0
                )
            ),
            "positive_rate": float(
                np.mean(
                    y_true
                )
            ),
        },

        "fixed_probability_bins": (
            BIN_EDGES.tolist()
        ),

        "bootstrap": {
            "method": (
                "Stratified bootstrap preserving "
                "observed binary class counts."
            ),
            "replicates": N_BOOTSTRAPS,
            "random_state": RANDOM_STATE,
            "confidence_level": 0.95,
        },

        "metrics_by_probability": (
            metrics_by_probability
        ),

        "descriptive_metric_table": (
            metric_table
        ),

        "probability_distributions": (
            probability_distributions
        ),

        "reliability_output": str(
            RELIABILITY_CSV
        ),

        "bootstrap_output": str(
            BOOTSTRAP_CSV
        ),

        "controls": controls,

        "control_failures": (
            control_failures
        ),

        "interpretation_boundary": [
            (
                "Brier score and log loss are treated as "
                "proper probabilistic scoring metrics."
            ),
            (
                "ECE and MCE are calibration diagnostics, "
                "not standalone proof of calibration."
            ),
            (
                "ROC-AUC and Average Precision describe "
                "discrimination/ranking, not calibration."
            ),
            (
                "No automation threshold is established."
            ),
            (
                "No human-review threshold is established."
            ),
            (
                "T5 probabilities remain task-specific "
                "duplicate probabilities."
            ),
            (
                "No universal ticket confidence or risk "
                "quantity is created."
            ),
            (
                "No cross-task numerical comparison is "
                "performed."
            ),
        ],

        "decision": (
            "T5 native probability representations have been "
            "empirically evaluated under the frozen T9 protocol. "
            "Any subsequent model/calibration selection claim "
            "must be based on these predefined metrics and "
            "uncertainty estimates and must preserve the "
            "task-specific T5 probability semantics."
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
    # Console
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print("T9 MOD-037 OP-008 RESULT")
    print("=" * 72)
    print()

    print(
        "Previous-operation validation:",
        previous["status"],
    )

    print(
        "Native-data validation:",
        native_validation["status"],
    )

    print(
        "Control validation:",
        controls_status,
    )

    print()

    for row in metric_table:

        print(
            row["probability_field"]
        )

        print(
            f"  Brier score: "
            f"{row['brier_score']:.6f}"
        )

        print(
            f"  Log loss: "
            f"{row['log_loss']:.6f}"
        )

        print(
            f"  ECE: "
            f"{row['ece']:.6f}"
        )

        print(
            f"  MCE: "
            f"{row['mce']:.6f}"
        )

        print(
            f"  ROC-AUC: "
            f"{row['roc_auc']:.6f}"
        )

        print(
            f"  Average Precision: "
            f"{row['average_precision']:.6f}"
        )

        print()

    print(
        "Population rows:",
        len(population),
    )

    print(
        "Positive targets:",
        int(
            np.sum(
                y_true == 1
            )
        ),
    )

    print(
        "Negative targets:",
        int(
            np.sum(
                y_true == 0
            )
        ),
    )

    print(
        "Bootstrap replicates:",
        N_BOOTSTRAPS,
    )

    print(
        "Calibration fitting performed: NO"
    )

    print(
        "Threshold selection performed: NO"
    )

    print(
        "Locked test used: NO"
    )

    print(
        "Universal confidence/risk created: NO"
    )

    print()

    print(
        "Reliability output:",
        RELIABILITY_CSV,
    )

    print(
        "Bootstrap output:",
        BOOTSTRAP_CSV,
    )

    print(
        "JSON output:",
        OUTPUT_JSON,
    )

    print()

    if overall_pass:

        print(
            "T9 MOD-037 OP-008 T5 empirical calibration "
            "evaluation: PASS"
        )

    else:

        print(
            "T9 MOD-037 OP-008 T5 empirical calibration "
            "evaluation: FAIL"
        )


if __name__ == "__main__":
    main()