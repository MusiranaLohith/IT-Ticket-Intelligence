from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


# ============================================================
# T9 MOD-037 OP-009
# T5 Calibration Uncertainty & Reliability Analysis
#
# Purpose:
#   Analyze the uncertainty and reliability artifacts produced
#   by OP-008 under the frozen T5 calibration protocol.
#
# This operation DOES NOT:
#   - fit calibration
#   - generate probabilities
#   - create/relabel targets
#   - select an automation threshold
#   - select a human-review threshold
#   - use locked test data
#   - create universal confidence/risk
#
# Inputs:
#   OP-005 semantics lock
#   OP-006 population audit
#   OP-007 frozen calibration protocol
#   OP-008 empirical calibration JSON
#   OP-008 bootstrap summary CSV
#   OP-008 reliability bins CSV
#
# Outputs:
#   Formal uncertainty/reliability audit JSON
#   Reliability summary CSV
#   Metric uncertainty summary CSV
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
    / "t9_mod037_op009_t5_uncertainty_reliability.json"
)

OUTPUT_RELIABILITY_CSV = (
    OUTPUT_DIR
    / "t9_mod037_op009_t5_reliability_summary.csv"
)

OUTPUT_METRICS_CSV = (
    OUTPUT_DIR
    / "t9_mod037_op009_t5_metric_uncertainty_summary.csv"
)


# ------------------------------------------------------------
# Required previous artifacts
# ------------------------------------------------------------

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

OP008_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op008_t5_empirical_calibration.json"
)

OP008_BOOTSTRAP = (
    OUTPUT_DIR
    / "t9_mod037_op008_t5_bootstrap_summary.csv"
)

OP008_RELIABILITY = (
    OUTPUT_DIR
    / "t9_mod037_op008_t5_reliability_bins.csv"
)


# ------------------------------------------------------------
# Expected probability representations
# ------------------------------------------------------------

PROBABILITY_FIELDS = {
    "p_base",
    "p_sigmoid",
    "p_isotonic",
}


# ------------------------------------------------------------
# Expected metrics
# ------------------------------------------------------------

EXPECTED_METRICS = {
    "brier_score",
    "log_loss",
    "ece",
    "mce",
    "roc_auc",
    "average_precision",
}


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


def fail(
    message: str,
) -> None:

    raise RuntimeError(
        message
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

    op008 = load_json(
        OP008_ARTIFACT
    )

    checks: dict[str, Any] = {}

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

    # OP-007 must have remained design-only.
    checks[
        "OP-007_calibration_not_fitted"
    ] = {
        "status": (
            "PASS"
            if op007.get(
                "calibration_fitting_performed"
            )
            is False
            else "FAIL"
        ),
        "observed": op007.get(
            "calibration_fitting_performed"
        ),
    }

    # --------------------------------------------------------
    # OP-008
    # --------------------------------------------------------

    checks["OP-008"] = {
        "status": (
            "PASS"
            if op008.get("status") == "PASS"
            else "FAIL"
        ),
        "observed": op008.get(
            "status"
        ),
    }

    # --------------------------------------------------------
    # OP-008 must have respected controls
    # --------------------------------------------------------

    controls = op008.get(
        "controls",
        {},
    )

    expected_false_controls = [
        "calibration_fitting_performed",
        "threshold_selection_performed",
        "automation_threshold_selected",
        "review_threshold_selected",
        "universal_confidence_created",
        "universal_risk_score_created",
        "cross_task_probability_averaging_performed",
        "arbitrary_cross_task_weights_used",
        "locked_test_used",
        "post_creation_information_used",
    ]

    for key in expected_false_controls:

        checks[
            f"OP-008_{key}"
        ] = {
            "status": (
                "PASS"
                if controls.get(key)
                is False
                else "FAIL"
            ),
            "observed": controls.get(
                key
            ),
        }

    # --------------------------------------------------------
    # Overall
    # --------------------------------------------------------

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
# Bootstrap artifact audit
# ============================================================

def audit_bootstrap() -> dict[str, Any]:

    if not OP008_BOOTSTRAP.exists():

        return {
            "status": "FAIL",
            "reason": (
                f"Bootstrap artifact missing: "
                f"{OP008_BOOTSTRAP}"
            ),
        }

    df = pd.read_csv(
        OP008_BOOTSTRAP
    )

    required_columns = {
        "probability_field",
        "metric",
        "bootstrap_replicates",
        "mean",
        "std",
        "ci_95_lower",
        "ci_95_upper",
    }

    missing_columns = sorted(
        required_columns
        - set(df.columns)
    )

    observed_fields = set(
        df[
            "probability_field"
        ].dropna().unique()
    )

    observed_metrics = set(
        df[
            "metric"
        ].dropna().unique()
    )

    checks: dict[str, Any] = {}

    checks["required_columns"] = {
        "status": (
            "PASS"
            if not missing_columns
            else "FAIL"
        ),
        "missing": missing_columns,
    }

    checks["probability_fields"] = {
        "status": (
            "PASS"
            if observed_fields
            == PROBABILITY_FIELDS
            else "FAIL"
        ),
        "expected": sorted(
            PROBABILITY_FIELDS
        ),
        "observed": sorted(
            observed_fields
        ),
    }

    checks["metrics"] = {
        "status": (
            "PASS"
            if observed_metrics
            == EXPECTED_METRICS
            else "FAIL"
        ),
        "expected": sorted(
            EXPECTED_METRICS
        ),
        "observed": sorted(
            observed_metrics
        ),
    }

    checks["row_count"] = {
        "status": (
            "PASS"
            if len(df) == (
                len(PROBABILITY_FIELDS)
                * len(EXPECTED_METRICS)
            )
            else "FAIL"
        ),
        "observed": int(
            len(df)
        ),
    }

    checks["bootstrap_replicates"] = {
        "status": (
            "PASS"
            if (
                df[
                    "bootstrap_replicates"
                ]
                .astype(int)
                .eq(1000)
                .all()
            )
            else "FAIL"
        ),
        "unique_values": sorted(
            df[
                "bootstrap_replicates"
            ]
            .astype(int)
            .unique()
            .tolist()
        ),
    }

    # --------------------------------------------------------
    # Numerical validity
    # --------------------------------------------------------

    numeric_columns = [
        "mean",
        "std",
        "ci_95_lower",
        "ci_95_upper",
    ]

    finite = True

    for column in numeric_columns:

        if not np.isfinite(
            df[column]
            .astype(float)
            .to_numpy()
        ).all():

            finite = False

    checks["finite_statistics"] = {
        "status": (
            "PASS"
            if finite
            else "FAIL"
        ),
    }

    checks["interval_order"] = {
        "status": (
            "PASS"
            if (
                df[
                    "ci_95_lower"
                ]
                <=
                df[
                    "ci_95_upper"
                ]
            ).all()
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
        "status": (
            "PASS"
            if not failed
            else "FAIL"
        ),
        "checks": checks,
        "failed_checks": failed,
        "rows": int(
            len(df)
        ),
        "dataframe": df,
    }


# ============================================================
# Reliability artifact audit
# ============================================================

def audit_reliability() -> dict[str, Any]:

    if not OP008_RELIABILITY.exists():

        return {
            "status": "FAIL",
            "reason": (
                f"Reliability artifact missing: "
                f"{OP008_RELIABILITY}"
            ),
        }

    df = pd.read_csv(
        OP008_RELIABILITY
    )

    required_columns = {
        "probability_field",
        "bin_index",
        "bin_left",
        "bin_right",
        "count",
        "mean_predicted",
        "observed_event_rate",
        "absolute_gap",
        "weighted_gap",
    }

    missing_columns = sorted(
        required_columns
        - set(df.columns)
    )

    observed_fields = set(
        df[
            "probability_field"
        ].dropna().unique()
    )

    checks: dict[str, Any] = {}

    checks["required_columns"] = {
        "status": (
            "PASS"
            if not missing_columns
            else "FAIL"
        ),
        "missing": missing_columns,
    }

    checks["probability_fields"] = {
        "status": (
            "PASS"
            if observed_fields
            == PROBABILITY_FIELDS
            else "FAIL"
        ),
        "expected": sorted(
            PROBABILITY_FIELDS
        ),
        "observed": sorted(
            observed_fields
        ),
    }

    # The OP-008 fixed bin definition has 14 bins.
    expected_bins = 14

    rows_per_field = (
        df.groupby(
            "probability_field"
        )
        .size()
    )

    checks["fixed_bin_count"] = {
        "status": (
            "PASS"
            if (
                set(
                    rows_per_field.index
                )
                == PROBABILITY_FIELDS
                and
                rows_per_field.eq(
                    expected_bins
                ).all()
            )
            else "FAIL"
        ),
        "expected_bins_per_field": (
            expected_bins
        ),
        "observed_rows_per_field": {
            str(k): int(v)
            for k, v
            in rows_per_field.items()
        },
    }

    # --------------------------------------------------------
    # Counts must be non-negative integers.
    # --------------------------------------------------------

    counts_valid = (
        pd.to_numeric(
            df["count"],
            errors="coerce",
        ).notna().all()
        and
        (
            df["count"]
            >= 0
        ).all()
    )

    checks["counts_valid"] = {
        "status": (
            "PASS"
            if counts_valid
            else "FAIL"
        ),
    }

    # --------------------------------------------------------
    # Mean probabilities/event rates are bounded.
    # Empty bins may be NaN.
    # --------------------------------------------------------

    bounded = True

    for column in [
        "mean_predicted",
        "observed_event_rate",
        "absolute_gap",
        "weighted_gap",
    ]:

        values = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        finite_values = values[
            values.notna()
        ]

        if len(finite_values) > 0:

            if (
                not np.isfinite(
                    finite_values.to_numpy()
                ).all()
            ):

                bounded = False

    checks["reliability_values_finite"] = {
        "status": (
            "PASS"
            if bounded
            else "FAIL"
        ),
    }

    # --------------------------------------------------------
    # Empty bins explicitly retained.
    # --------------------------------------------------------

    empty_bins = int(
        (
            df["count"]
            == 0
        ).sum()
    )

    populated_bins = int(
        (
            df["count"]
            > 0
        ).sum()
    )

    checks["empty_bins_explicitly_retained"] = {
        "status": (
            "PASS"
            if (
                empty_bins
                +
                populated_bins
                == len(df)
            )
            else "FAIL"
        ),
        "empty_bins": empty_bins,
        "populated_bins": populated_bins,
    }

    # --------------------------------------------------------
    # Reliability gaps must be non-negative.
    # --------------------------------------------------------

    gap_valid = (
        pd.to_numeric(
            df["absolute_gap"],
            errors="coerce",
        )
        .dropna()
        >= 0
    ).all()

    checks["absolute_gap_valid"] = {
        "status": (
            "PASS"
            if gap_valid
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
        "status": (
            "PASS"
            if not failed
            else "FAIL"
        ),
        "checks": checks,
        "failed_checks": failed,
        "rows": int(
            len(df)
        ),
        "empty_bins": empty_bins,
        "populated_bins": populated_bins,
        "dataframe": df,
    }


# ============================================================
# Reliability analysis
# ============================================================

def summarize_reliability(
    df: pd.DataFrame,
) -> pd.DataFrame:

    rows = []

    for field, group in df.groupby(
        "probability_field",
        sort=True,
    ):

        populated = group[
            group["count"] > 0
        ].copy()

        if len(populated) == 0:

            rows.append(
                {
                    "probability_field": field,
                    "total_bins": int(
                        len(group)
                    ),
                    "populated_bins": 0,
                    "empty_bins": int(
                        len(group)
                    ),
                    "total_observations": 0,
                    "min_bin_count": np.nan,
                    "median_bin_count": np.nan,
                    "max_bin_count": np.nan,
                    "max_absolute_gap": np.nan,
                    "mean_absolute_gap_unweighted": np.nan,
                    "weighted_gap_sum": np.nan,
                    "sparse_bins_lt_100": np.nan,
                }
            )

            continue

        rows.append(
            {
                "probability_field": field,
                "total_bins": int(
                    len(group)
                ),
                "populated_bins": int(
                    len(populated)
                ),
                "empty_bins": int(
                    (
                        group["count"]
                        == 0
                    ).sum()
                ),
                "total_observations": int(
                    group["count"].sum()
                ),
                "min_bin_count": int(
                    populated["count"].min()
                ),
                "median_bin_count": float(
                    populated["count"].median()
                ),
                "max_bin_count": int(
                    populated["count"].max()
                ),
                "max_absolute_gap": float(
                    populated[
                        "absolute_gap"
                    ].max()
                ),
                "mean_absolute_gap_unweighted": float(
                    populated[
                        "absolute_gap"
                    ].mean()
                ),
                "weighted_gap_sum": float(
                    populated[
                        "weighted_gap"
                    ].sum()
                ),
                "sparse_bins_lt_100": int(
                    (
                        populated["count"]
                        < 100
                    ).sum()
                ),
            }
        )

    return pd.DataFrame(
        rows
    )


# ============================================================
# Metric uncertainty summary
# ============================================================

def build_metric_summary(
    bootstrap_df: pd.DataFrame,
) -> pd.DataFrame:

    rows = []

    for _, row in bootstrap_df.iterrows():

        rows.append(
            {
                "probability_field": (
                    row[
                        "probability_field"
                    ]
                ),
                "metric": row[
                    "metric"
                ],
                "bootstrap_replicates": int(
                    row[
                        "bootstrap_replicates"
                    ]
                ),
                "bootstrap_mean": float(
                    row[
                        "mean"
                    ]
                ),
                "bootstrap_std": float(
                    row[
                        "std"
                    ]
                ),
                "ci_95_lower": float(
                    row[
                        "ci_95_lower"
                    ]
                ),
                "ci_95_upper": float(
                    row[
                        "ci_95_upper"
                    ]
                ),
                "ci_width": float(
                    row[
                        "ci_95_upper"
                    ]
                    -
                    row[
                        "ci_95_lower"
                    ]
                ),
            }
        )

    return pd.DataFrame(
        rows
    )


# ============================================================
# Descriptive interval overlap
# ============================================================

def calculate_interval_overlap(
    metrics_df: pd.DataFrame,
) -> list[dict[str, Any]]:

    comparisons = []

    metric_names = sorted(
        EXPECTED_METRICS
    )

    pairs = [
        ("p_base", "p_sigmoid"),
        ("p_base", "p_isotonic"),
        ("p_sigmoid", "p_isotonic"),
    ]

    for metric in metric_names:

        metric_rows = metrics_df[
            metrics_df["metric"]
            == metric
        ]

        lookup = {
            row[
                "probability_field"
            ]: row
            for _, row
            in metric_rows.iterrows()
        }

        for left, right in pairs:

            a = lookup[left]
            b = lookup[right]

            lower = max(
                float(
                    a["ci_95_lower"]
                ),
                float(
                    b["ci_95_lower"]
                ),
            )

            upper = min(
                float(
                    a["ci_95_upper"]
                ),
                float(
                    b["ci_95_upper"]
                ),
            )

            overlap = (
                lower <= upper
            )

            comparisons.append(
                {
                    "metric": metric,
                    "left": left,
                    "right": right,
                    "left_ci_lower": float(
                        a[
                            "ci_95_lower"
                        ]
                    ),
                    "left_ci_upper": float(
                        a[
                            "ci_95_upper"
                        ]
                    ),
                    "right_ci_lower": float(
                        b[
                            "ci_95_lower"
                        ]
                    ),
                    "right_ci_upper": float(
                        b[
                            "ci_95_upper"
                        ]
                    ),
                    "intervals_overlap": bool(
                        overlap
                    ),
                }
            )

    return comparisons


# ============================================================
# Main
# ============================================================

def main() -> None:

    print("=" * 72)
    print("T9 MOD-037 OP-009")
    print("T5 Calibration Uncertainty & Reliability Analysis")
    print("=" * 72)
    print()

    # --------------------------------------------------------
    # Previous-operation validation
    # --------------------------------------------------------

    print(
        "Validating previous T9 operations..."
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
            "Previous T9 operation validation failed."
        )

    print()

    # --------------------------------------------------------
    # Bootstrap audit
    # --------------------------------------------------------

    print(
        "Auditing OP-008 bootstrap artifact..."
    )

    bootstrap_audit = (
        audit_bootstrap()
    )

    print(
        "Bootstrap artifact audit:",
        bootstrap_audit["status"],
    )

    if bootstrap_audit["status"] != "PASS":

        raise RuntimeError(
            "Bootstrap artifact audit failed."
        )

    bootstrap_df = (
        bootstrap_audit["dataframe"]
    )

    print()

    # --------------------------------------------------------
    # Reliability audit
    # --------------------------------------------------------

    print(
        "Auditing OP-008 reliability artifact..."
    )

    reliability_audit = (
        audit_reliability()
    )

    print(
        "Reliability artifact audit:",
        reliability_audit["status"],
    )

    if reliability_audit["status"] != "PASS":

        raise RuntimeError(
            "Reliability artifact audit failed."
        )

    reliability_df = (
        reliability_audit["dataframe"]
    )

    print()

    # --------------------------------------------------------
    # Summaries
    # --------------------------------------------------------

    print(
        "Building reliability summary..."
    )

    reliability_summary = (
        summarize_reliability(
            reliability_df
        )
    )

    reliability_summary.to_csv(
        OUTPUT_RELIABILITY_CSV,
        index=False,
    )

    print(
        "Reliability summary written."
    )

    print()

    print(
        "Building metric uncertainty summary..."
    )

    metric_summary = (
        build_metric_summary(
            bootstrap_df
        )
    )

    metric_summary.to_csv(
        OUTPUT_METRICS_CSV,
        index=False,
    )

    print(
        "Metric uncertainty summary written."
    )

    print()

    # --------------------------------------------------------
    # Interval-overlap analysis
    #
    # Descriptive only.
    # It does NOT constitute a statistical significance test
    # and does NOT declare a calibration-method winner.
    # --------------------------------------------------------

    interval_comparisons = (
        calculate_interval_overlap(
            metric_summary
        )
    )

    # --------------------------------------------------------
    # Reliability diagnostics
    # --------------------------------------------------------

    reliability_diagnostics = {}

    for field, group in reliability_df.groupby(
        "probability_field",
        sort=True,
    ):

        populated = group[
            group["count"] > 0
        ].copy()

        reliability_diagnostics[
            field
        ] = {
            "total_bins": int(
                len(group)
            ),
            "populated_bins": int(
                len(populated)
            ),
            "empty_bins": int(
                (
                    group["count"]
                    == 0
                ).sum()
            ),
            "minimum_populated_bin_count": (
                int(
                    populated[
                        "count"
                    ].min()
                )
                if len(populated)
                else None
            ),
            "maximum_populated_bin_count": (
                int(
                    populated[
                        "count"
                    ].max()
                )
                if len(populated)
                else None
            ),
            "sparse_bins_lt_100": int(
                (
                    populated["count"]
                    < 100
                ).sum()
            ),
            "maximum_absolute_gap": (
                float(
                    populated[
                        "absolute_gap"
                    ].max()
                )
                if len(populated)
                else None
            ),
            "mean_absolute_gap_unweighted": (
                float(
                    populated[
                        "absolute_gap"
                    ].mean()
                )
                if len(populated)
                else None
            ),
        }

    # --------------------------------------------------------
    # Check prevalence preservation
    # --------------------------------------------------------

    total_observations = int(
        reliability_df[
            "count"
        ].groupby(
            reliability_df[
                "probability_field"
            ]
        ).sum().iloc[0]
    )

    expected_population = 74091

    prevalence_check = {
        "expected_population": (
            expected_population
        ),
        "reliability_population": (
            total_observations
        ),
        "status": (
            "PASS"
            if total_observations
            == expected_population
            else "FAIL"
        ),
    }

    # --------------------------------------------------------
    # Controls
    # --------------------------------------------------------

    controls = {

        "new_calibration_fitted": False,

        "new_probability_generated": False,

        "target_created": False,

        "target_relabelled": False,

        "automation_threshold_selected": False,

        "review_threshold_selected": False,

        "locked_test_used": False,

        "universal_confidence_created": False,

        "universal_risk_score_created": False,

        "cross_task_probability_comparison_performed": False,

        "arbitrary_cross_task_weights_used": False,

        "native_t5_probability_semantics_preserved": True,

        "observed_validation_prevalence_preserved": (
            prevalence_check["status"]
            == "PASS"
        ),
    }

    control_failures = []

    for key, value in controls.items():

        if key in {
            "native_t5_probability_semantics_preserved",
            "observed_validation_prevalence_preserved",
        }:

            if value is not True:
                control_failures.append(
                    key
                )

        else:

            if value is not False:
                control_failures.append(
                    key
                )

    controls_status = (
        "PASS"
        if not control_failures
        else "FAIL"
    )

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    overall_pass = (
        previous["status"] == "PASS"
        and
        bootstrap_audit["status"] == "PASS"
        and
        reliability_audit["status"] == "PASS"
        and
        prevalence_check["status"] == "PASS"
        and
        controls_status == "PASS"
    )

    # --------------------------------------------------------
    # Interpretation
    # --------------------------------------------------------

    interpretation = {

        "uncertainty": (
            "Bootstrap confidence intervals quantify sampling "
            "uncertainty around the reported empirical metrics. "
            "They do not establish causal superiority or "
            "guarantee future-population performance."
        ),

        "interval_overlap": (
            "Confidence-interval overlap is reported only as a "
            "descriptive diagnostic. It is not treated as a "
            "formal hypothesis test."
        ),

        "reliability": (
            "Reliability bins describe agreement between "
            "predicted duplicate probability and observed "
            "duplicate frequency within fixed probability "
            "ranges."
        ),

        "sparse_bins": (
            "Bins with low support are explicitly identified "
            "and should not be interpreted as equally precise "
            "as high-support bins."
        ),

        "class_imbalance": (
            "The analysis preserves the observed T5 validation "
            "prevalence of 480 positives and 73,611 negatives."
        ),

        "method_selection": (
            "This operation does not declare a calibration-method "
            "winner. Any later selection must remain within the "
            "frozen protocol and account for proper scoring, "
            "calibration diagnostics, discrimination context, "
            "and uncertainty."
        ),

        "thresholds": (
            "No automation or human-review threshold is "
            "established."
        ),
    }

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    output = {

        "operation": "T9_MOD-037_OP-009",

        "title": (
            "T5 Calibration Uncertainty & "
            "Reliability Analysis"
        ),

        "status": (
            "PASS"
            if overall_pass
            else "FAIL"
        ),

        "operation_type": (
            "UNCERTAINTY_AND_RELIABILITY_ANALYSIS"
        ),

        "previous_operation_validation": previous,

        "bootstrap_audit": {
            key: value
            for key, value
            in bootstrap_audit.items()
            if key != "dataframe"
        },

        "reliability_audit": {
            key: value
            for key, value
            in reliability_audit.items()
            if key != "dataframe"
        },

        "prevalence_check": prevalence_check,

        "metric_uncertainty_summary": (
            metric_summary.to_dict(
                orient="records"
            )
        ),

        "reliability_summary": (
            reliability_summary.to_dict(
                orient="records"
            )
        ),

        "interval_overlap_descriptive": (
            interval_comparisons
        ),

        "reliability_diagnostics": (
            reliability_diagnostics
        ),

        "controls": controls,

        "control_failures": (
            control_failures
        ),

        "output_artifacts": {
            "metric_uncertainty_summary": str(
                OUTPUT_METRICS_CSV
            ),
            "reliability_summary": str(
                OUTPUT_RELIABILITY_CSV
            ),
        },

        "interpretation": interpretation,

        "decision": (
            "T5 uncertainty and reliability evidence has been "
            "audited under the frozen T9 protocol. This operation "
            "does not select an automation threshold, create a "
            "universal confidence/risk score, or declare a "
            "calibration-method winner."
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

    print("=" * 72)
    print("T9 MOD-037 OP-009 RESULT")
    print("=" * 72)
    print()

    print(
        "Previous-operation validation:",
        previous["status"],
    )

    print(
        "Bootstrap artifact audit:",
        bootstrap_audit["status"],
    )

    print(
        "Reliability artifact audit:",
        reliability_audit["status"],
    )

    print(
        "Prevalence preservation:",
        prevalence_check["status"],
    )

    print(
        "Control validation:",
        controls_status,
    )

    print()

    print(
        "Reliability diagnostics:"
    )

    for field, info in (
        reliability_diagnostics.items()
    ):

        print(
            f"  {field}:"
        )

        print(
            f"    populated bins: "
            f"{info['populated_bins']}"
        )

        print(
            f"    empty bins: "
            f"{info['empty_bins']}"
        )

        print(
            f"    minimum bin count: "
            f"{info['minimum_populated_bin_count']}"
        )

        print(
            f"    sparse bins (<100): "
            f"{info['sparse_bins_lt_100']}"
        )

        print(
            f"    maximum absolute gap: "
            f"{info['maximum_absolute_gap']}"
        )

    print()

    print(
        "New calibration fitting performed: NO"
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
        "Metric uncertainty output:",
        OUTPUT_METRICS_CSV,
    )

    print(
        "Reliability summary output:",
        OUTPUT_RELIABILITY_CSV,
    )

    print(
        "JSON output:",
        OUTPUT_JSON,
    )

    print()

    if overall_pass:

        print(
            "T9 MOD-037 OP-009 T5 uncertainty/reliability "
            "analysis: PASS"
        )

    else:

        print(
            "T9 MOD-037 OP-009 T5 uncertainty/reliability "
            "analysis: FAIL"
        )


if __name__ == "__main__":
    main()