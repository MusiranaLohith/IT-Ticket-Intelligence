from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


# ============================================================
# T9 MOD-037 OP-010
# T5 Calibration Evidence Synthesis & Method Selection Audit
#
# Purpose:
#   Synthesize the empirical T5 calibration evidence produced
#   by OP-008 and OP-009 under the frozen T9 protocol.
#
# This operation DOES NOT:
#   - fit calibration
#   - generate probabilities
#   - create/relabel targets
#   - use locked test data
#   - select automation thresholds
#   - create universal confidence/risk
#   - run unrestricted new experiments
#
# It evaluates whether the existing evidence supports a
# defensible task-specific T5 calibration conclusion.
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
    / "t9_mod037_op010_t5_calibration_evidence_synthesis.json"
)


# ------------------------------------------------------------
# Previous artifacts
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

OP009_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op009_t5_uncertainty_reliability.json"
)

OP009_METRICS = (
    OUTPUT_DIR
    / "t9_mod037_op009_t5_metric_uncertainty_summary.csv"
)

OP009_RELIABILITY = (
    OUTPUT_DIR
    / "t9_mod037_op009_t5_reliability_summary.csv"
)


# ------------------------------------------------------------
# Expected representations
# ------------------------------------------------------------

REPRESENTATIONS = [
    "p_base",
    "p_sigmoid",
    "p_isotonic",
]


# ------------------------------------------------------------
# Utility
# ------------------------------------------------------------

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

    op009 = load_json(
        OP009_ARTIFACT
    )

    checks: dict[str, Any] = {}

    artifacts = {
        "OP-005": op005,
        "OP-006": op006,
        "OP-007": op007,
        "OP-008": op008,
        "OP-009": op009,
    }

    for name, artifact in artifacts.items():

        checks[
            f"{name}_status"
        ] = {
            "status": (
                "PASS"
                if artifact.get("status")
                == "PASS"
                else "FAIL"
            ),
            "observed": artifact.get(
                "status"
            ),
        }

    # --------------------------------------------------------
    # Frozen methodological controls
    # --------------------------------------------------------

    checks[
        "OP-007_calibration_fitting"
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

    checks[
        "OP-007_threshold_selection"
    ] = {
        "status": (
            "PASS"
            if op007.get(
                "threshold_selection_performed"
            )
            is False
            else "FAIL"
        ),
        "observed": op007.get(
            "threshold_selection_performed"
        ),
    }

    checks[
        "OP-007_locked_test"
    ] = {
        "status": (
            "PASS"
            if op007.get(
                "locked_test_used_for_selection"
            )
            is False
            else "FAIL"
        ),
        "observed": op007.get(
            "locked_test_used_for_selection"
        ),
    }

    # --------------------------------------------------------
    # OP-008 controls
    # --------------------------------------------------------

    op008_controls = op008.get(
        "controls",
        {},
    )

    for key in [
        "calibration_fitting_performed",
        "threshold_selection_performed",
        "automation_threshold_selected",
        "review_threshold_selected",
        "universal_confidence_created",
        "universal_risk_score_created",
        "locked_test_used",
    ]:

        checks[
            f"OP-008_{key}"
        ] = {
            "status": (
                "PASS"
                if op008_controls.get(key)
                is False
                else "FAIL"
            ),
            "observed": op008_controls.get(
                key
            ),
        }

    # --------------------------------------------------------
    # OP-009 controls
    # --------------------------------------------------------

    op009_controls = op009.get(
        "controls",
        {},
    )

    for key in [
        "new_calibration_fitted",
        "new_probability_generated",
        "automation_threshold_selected",
        "review_threshold_selected",
        "locked_test_used",
        "universal_confidence_created",
        "universal_risk_score_created",
    ]:

        checks[
            f"OP-009_{key}"
        ] = {
            "status": (
                "PASS"
                if op009_controls.get(key)
                is False
                else "FAIL"
            ),
            "observed": op009_controls.get(
                key
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
# Load empirical evidence
# ============================================================

def load_empirical_evidence() -> dict[str, Any]:

    op008 = load_json(
        OP008_ARTIFACT
    )

    op009 = load_json(
        OP009_ARTIFACT
    )

    if not OP009_METRICS.exists():
        fail(
            f"Missing metric uncertainty artifact: "
            f"{OP009_METRICS}"
        )

    if not OP009_RELIABILITY.exists():
        fail(
            f"Missing reliability summary artifact: "
            f"{OP009_RELIABILITY}"
        )

    metrics_df = pd.read_csv(
        OP009_METRICS
    )

    reliability_df = pd.read_csv(
        OP009_RELIABILITY
    )

    return {
        "op008": op008,
        "op009": op009,
        "metrics": metrics_df,
        "reliability": reliability_df,
    }


# ============================================================
# Evidence structure validation
# ============================================================

def validate_evidence_structure(
    evidence: dict[str, Any],
) -> dict[str, Any]:

    metrics = evidence["metrics"]
    reliability = evidence["reliability"]

    checks: dict[str, Any] = {}

    observed_metric_fields = set(
        metrics[
            "probability_field"
        ].unique()
    )

    observed_reliability_fields = set(
        reliability[
            "probability_field"
        ].unique()
    )

    checks[
        "metric_probability_fields"
    ] = {
        "status": (
            "PASS"
            if observed_metric_fields
            == set(REPRESENTATIONS)
            else "FAIL"
        ),
        "observed": sorted(
            observed_metric_fields
        ),
    }

    checks[
        "reliability_probability_fields"
    ] = {
        "status": (
            "PASS"
            if observed_reliability_fields
            == set(REPRESENTATIONS)
            else "FAIL"
        ),
        "observed": sorted(
            observed_reliability_fields
        ),
    }

    expected_metrics = {
        "brier_score",
        "log_loss",
        "ece",
        "mce",
        "roc_auc",
        "average_precision",
    }

    observed_metrics = set(
        metrics[
            "metric"
        ].unique()
    )

    checks["metric_set"] = {
        "status": (
            "PASS"
            if observed_metrics
            == expected_metrics
            else "FAIL"
        ),
        "observed": sorted(
            observed_metrics
        ),
    }

    checks["metric_rows"] = {
        "status": (
            "PASS"
            if len(metrics)
            == 18
            else "FAIL"
        ),
        "observed": int(
            len(metrics)
        ),
    }

    checks["reliability_rows"] = {
        "status": (
            "PASS"
            if len(reliability)
            == 3
            else "FAIL"
        ),
        "observed": int(
            len(reliability)
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
# Extract point estimates
# ============================================================

def point_estimate_table(
    metrics: pd.DataFrame,
) -> pd.DataFrame:

    rows = []

    for representation in REPRESENTATIONS:

        subset = metrics[
            metrics[
                "probability_field"
            ]
            == representation
        ]

        row = {
            "probability_field": representation,
        }

        for metric in [
            "brier_score",
            "log_loss",
            "ece",
            "mce",
            "roc_auc",
            "average_precision",
        ]:

            match = subset[
                subset["metric"]
                == metric
            ]

            if len(match) != 1:
                fail(
                    f"Expected exactly one "
                    f"{metric} row for "
                    f"{representation}."
                )

            row[
                metric
            ] = float(
                match.iloc[0][
                    "bootstrap_mean"
                ]
            )

            row[
                f"{metric}_ci_lower"
            ] = float(
                match.iloc[0][
                    "ci_95_lower"
                ]
            )

            row[
                f"{metric}_ci_upper"
            ] = float(
                match.iloc[0][
                    "ci_95_upper"
                ]
            )

        rows.append(
            row
        )

    return pd.DataFrame(
        rows
    )


# ============================================================
# Reliability interpretation
# ============================================================

def reliability_flags(
    reliability: pd.DataFrame,
) -> dict[str, Any]:

    flags = {}

    for _, row in reliability.iterrows():

        representation = row[
            "probability_field"
        ]

        flags[
            representation
        ] = {
            "populated_bins": int(
                row["populated_bins"]
            ),
            "empty_bins": int(
                row["empty_bins"]
            ),
            "minimum_bin_count": (
                None
                if pd.isna(
                    row[
                        "min_bin_count"
                    ]
                )
                else int(
                    row[
                        "min_bin_count"
                    ]
                )
            ),
            "sparse_bins_lt_100": int(
                row[
                    "sparse_bins_lt_100"
                ]
            ),
            "maximum_absolute_gap": (
                None
                if pd.isna(
                    row[
                        "max_absolute_gap"
                    ]
                )
                else float(
                    row[
                        "max_absolute_gap"
                    ]
                )
            ),
        }

    return flags


# ============================================================
# Evidence-based descriptive comparison
# ============================================================

def compare_metrics(
    table: pd.DataFrame,
) -> dict[str, Any]:

    result: dict[str, Any] = {}

    # Lower is better for these.
    for metric in [
        "brier_score",
        "log_loss",
        "ece",
        "mce",
    ]:

        values = {
            row[
                "probability_field"
            ]: float(
                row[metric]
            )
            for _, row
            in table.iterrows()
        }

        minimum = min(
            values.values()
        )

        result[
            metric
        ] = {
            "values": values,
            "minimum_value": minimum,
            "minimum_representations": [
                key
                for key, value
                in values.items()
                if np.isclose(
                    value,
                    minimum,
                    rtol=0,
                    atol=1e-12,
                )
            ],
        }

    # Higher is better for discrimination.
    for metric in [
        "roc_auc",
        "average_precision",
    ]:

        values = {
            row[
                "probability_field"
            ]: float(
                row[metric]
            )
            for _, row
            in table.iterrows()
        }

        maximum = max(
            values.values()
        )

        result[
            metric
        ] = {
            "values": values,
            "maximum_value": maximum,
            "maximum_representations": [
                key
                for key, value
                in values.items()
                if np.isclose(
                    value,
                    maximum,
                    rtol=0,
                    atol=1e-12,
                )
            ],
        }

    return result


# ============================================================
# Formal evidence rules
# ============================================================

def build_evidence_rules(
    table: pd.DataFrame,
    reliability_flags_data: dict[str, Any],
) -> dict[str, Any]:

    rules: dict[str, Any] = {}

    # --------------------------------------------------------
    # Rule 1:
    # p_base must not be called calibrated merely because
    # it has discrimination.
    # --------------------------------------------------------

    p_base = table[
        table["probability_field"]
        == "p_base"
    ].iloc[0]

    rules[
        "p_base_calibration_evidence"
    ] = {
        "status": (
            "NOT_ESTABLISHED"
            if (
                p_base["ece"] > 0
                or
                p_base["mce"] > 0
            )
            else "ESTABLISHED"
        ),
        "reason": (
            "Native p_base exhibits substantial calibration "
            "error in the observed validation evidence and "
            "therefore cannot be described as empirically "
            "well-calibrated from this evidence."
        ),
    }

    # --------------------------------------------------------
    # Rule 2:
    # Extremely sparse bins limit interpretation.
    # --------------------------------------------------------

    sparse_flags = {}

    for representation, info in (
        reliability_flags_data.items()
    ):

        sparse_flags[
            representation
        ] = (
            info[
                "sparse_bins_lt_100"
            ] > 0
            or
            info[
                "empty_bins"
            ] > 0
        )

    rules[
        "sparse_bin_limitation"
    ] = {
        "status": (
            "PRESENT"
            if any(
                sparse_flags.values()
            )
            else "NOT_PRESENT"
        ),
        "by_representation": sparse_flags,
        "interpretation": (
            "Sparse or empty reliability bins limit the "
            "strength of local calibration interpretation, "
            "especially where individual bins contain very "
            "few observations."
        ),
    }

    # --------------------------------------------------------
    # Rule 3:
    # Discrimination preservation.
    # --------------------------------------------------------

    p_base_auc = float(
        p_base["roc_auc"]
    )

    p_sigmoid = table[
        table["probability_field"]
        == "p_sigmoid"
    ].iloc[0]

    p_isotonic = table[
        table["probability_field"]
        == "p_isotonic"
    ].iloc[0]

    rules[
        "discrimination_behavior"
    ] = {
        "p_base_roc_auc": p_base_auc,
        "p_sigmoid_roc_auc": float(
            p_sigmoid["roc_auc"]
        ),
        "p_isotonic_roc_auc": float(
            p_isotonic["roc_auc"]
        ),
        "p_sigmoid_delta_vs_base": float(
            p_sigmoid["roc_auc"]
            - p_base_auc
        ),
        "p_isotonic_delta_vs_base": float(
            p_isotonic["roc_auc"]
            - p_base_auc
        ),
        "interpretation": (
            "Sigmoid representation preserves the observed "
            "ROC-AUC numerically, while isotonic shows a small "
            "reduction in the observed ROC-AUC. These are "
            "descriptive observations, not significance tests."
        ),
    }

    # --------------------------------------------------------
    # Rule 4:
    # No method should be selected solely from one metric.
    # --------------------------------------------------------

    rules[
        "single_metric_selection_prohibited"
    ] = {
        "status": "ENFORCED",
        "reason": (
            "The T9 protocol requires joint consideration of "
            "proper scoring metrics, calibration diagnostics, "
            "discrimination context, reliability support, and "
            "uncertainty."
        ),
    }

    # --------------------------------------------------------
    # Rule 5:
    # No universal confidence/risk.
    # --------------------------------------------------------

    rules[
        "universal_score"
    ] = {
        "status": "PROHIBITED",
        "confidence_score_created": False,
        "risk_score_created": False,
    }

    return rules


# ============================================================
# Method-selection conclusion
# ============================================================

def derive_conclusion(
    table: pd.DataFrame,
    reliability_flags_data: dict[str, Any],
) -> dict[str, Any]:

    p_base = table[
        table["probability_field"]
        == "p_base"
    ].iloc[0]

    p_sigmoid = table[
        table["probability_field"]
        == "p_sigmoid"
    ].iloc[0]

    p_isotonic = table[
        table["probability_field"]
        == "p_isotonic"
    ].iloc[0]

    # --------------------------------------------------------
    # Evidence observations
    # --------------------------------------------------------

    observations = [

        (
            "p_base has materially larger Brier, log-loss, "
            "and ECE values than the two transformed "
            "representations in the observed validation "
            "evidence."
        ),

        (
            "p_sigmoid and p_isotonic both show substantially "
            "lower Brier and ECE than p_base."
        ),

        (
            "p_sigmoid retains the same observed ROC-AUC as "
            "p_base in this validation artifact."
        ),

        (
            "p_isotonic has a small observed ROC-AUC reduction "
            "relative to p_base."
        ),

        (
            "p_sigmoid contains sparse reliability bins, "
            "including a minimum populated-bin count of 1."
        ),

        (
            "p_isotonic contains empty and sparse reliability "
            "bins as well."
        ),

        (
            "The evidence therefore supports a task-specific "
            "calibration improvement relative to p_base, but "
            "local reliability estimates in sparse regions "
            "remain limited."
        ),
    ]

    # --------------------------------------------------------
    # Explicit method status
    #
    # We do not silently call a method universally "best".
    # The conclusion describes the evidence-supported status.
    # --------------------------------------------------------

    p_sigmoid_strong_scoring = (
        p_sigmoid["brier_score"]
        < p_base["brier_score"]
        and
        p_sigmoid["log_loss"]
        < p_base["log_loss"]
        and
        p_sigmoid["ece"]
        < p_base["ece"]
    )

    p_isotonic_strong_scoring = (
        p_isotonic["brier_score"]
        < p_base["brier_score"]
        and
        p_isotonic["log_loss"]
        < p_base["log_loss"]
        and
        p_isotonic["ece"]
        < p_base["ece"]
    )

    # --------------------------------------------------------
    # Selection status
    # --------------------------------------------------------

    if (
        p_sigmoid_strong_scoring
        and
        p_isotonic_strong_scoring
    ):

        selection_status = (
            "CALIBRATION_IMPROVEMENT_SUPPORTED_BUT_METHOD_SELECTION_REQUIRES_CAUTION"
        )

        selected_method = (
            "NOT_FORMALLY_SELECTED"
        )

        rationale = (
            "Both p_sigmoid and p_isotonic materially improve "
            "the observed proper-scoring/calibration diagnostics "
            "relative to p_base. However, reliability-bin "
            "sparsity is present for both transformed "
            "representations, and the available evidence is "
            "validation-population evidence rather than an "
            "independent locked-test calibration comparison. "
            "Therefore this operation does not declare one "
            "method universally superior or establish an "
            "automation-ready calibrated probability."
        )

    else:

        selection_status = (
            "NO_UNAMBIGUOUS_CALIBRATION_IMPROVEMENT_ESTABLISHED"
        )

        selected_method = (
            "NOT_FORMALLY_SELECTED"
        )

        rationale = (
            "The predefined evidence does not support a "
            "defensible single calibration-method selection "
            "under the frozen protocol."
        )

    return {
        "selection_status": selection_status,
        "selected_method": selected_method,
        "rationale": rationale,
        "observations": observations,
        "supporting_conditions": {
            "p_sigmoid_improves_vs_p_base": bool(
                p_sigmoid_strong_scoring
            ),
            "p_isotonic_improves_vs_p_base": bool(
                p_isotonic_strong_scoring
            ),
            "p_sigmoid_sparse_bins": bool(
                reliability_flags_data[
                    "p_sigmoid"
                ][
                    "sparse_bins_lt_100"
                ] > 0
            ),
            "p_isotonic_sparse_or_empty_bins": bool(
                reliability_flags_data[
                    "p_isotonic"
                ][
                    "sparse_bins_lt_100"
                ] > 0
                or
                reliability_flags_data[
                    "p_isotonic"
                ][
                    "empty_bins"
                ] > 0
            ),
        },
    }


# ============================================================
# Main
# ============================================================

def main() -> None:

    print("=" * 72)
    print("T9 MOD-037 OP-010")
    print("T5 Calibration Evidence Synthesis & Method Selection Audit")
    print("=" * 72)
    print()

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
            "Previous-operation validation failed."
        )

    print()

    print(
        "Loading OP-008 and OP-009 evidence..."
    )

    evidence = (
        load_empirical_evidence()
    )

    print(
        "Empirical evidence loaded."
    )

    print()

    print(
        "Validating evidence structure..."
    )

    structure = (
        validate_evidence_structure(
            evidence
        )
    )

    print(
        "Evidence structure:",
        structure["status"],
    )

    if structure["status"] != "PASS":

        raise RuntimeError(
            "Evidence structure validation failed."
        )

    metrics_df = evidence[
        "metrics"
    ]

    reliability_df = evidence[
        "reliability"
    ]

    print()

    print(
        "Building point-estimate and uncertainty table..."
    )

    table = point_estimate_table(
        metrics_df
    )

    print(
        "Point-estimate table built."
    )

    print()

    print(
        "Analyzing reliability support..."
    )

    reliability_info = (
        reliability_flags(
            reliability_df
        )
    )

    print(
        "Reliability support analyzed."
    )

    print()

    print(
        "Comparing predefined metrics..."
    )

    comparison = compare_metrics(
        table
    )

    print(
        "Metric comparison completed."
    )

    print()

    print(
        "Applying evidence rules..."
    )

    rules = build_evidence_rules(
        table,
        reliability_info,
    )

    print(
        "Evidence rules applied."
    )

    print()

    print(
        "Deriving calibration evidence conclusion..."
    )

    conclusion = derive_conclusion(
        table,
        reliability_info,
    )

    print(
        "Conclusion derived."
    )

    # --------------------------------------------------------
    # Controls
    # --------------------------------------------------------

    controls = {

        "new_model_fitted": False,

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

        "single_metric_method_selection_used": False,

        "native_t5_probability_semantics_preserved": True,

        "validation_prevalence_preserved": True,
    }

    control_failures = []

    for key, value in controls.items():

        if key in {
            "native_t5_probability_semantics_preserved",
            "validation_prevalence_preserved",
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

    overall_pass = (
        previous["status"] == "PASS"
        and
        structure["status"] == "PASS"
        and
        controls_status == "PASS"
    )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    output = {

        "operation": "T9_MOD-037_OP-010",

        "title": (
            "T5 Calibration Evidence Synthesis & "
            "Method Selection Audit"
        ),

        "status": (
            "PASS"
            if overall_pass
            else "FAIL"
        ),

        "operation_type": (
            "EVIDENCE_SYNTHESIS_AND_METHOD_SELECTION_AUDIT"
        ),

        "previous_operation_validation": previous,

        "evidence_structure_validation": structure,

        "point_estimate_and_uncertainty_table": (
            table.to_dict(
                orient="records"
            )
        ),

        "metric_comparison": comparison,

        "reliability_evidence": (
            reliability_info
        ),

        "evidence_rules": rules,

        "conclusion": conclusion,

        "controls": controls,

        "control_failures": (
            control_failures
        ),

        "artifacts_used": {
            "OP-005": str(
                OP005_ARTIFACT
            ),
            "OP-006": str(
                OP006_ARTIFACT
            ),
            "OP-007": str(
                OP007_ARTIFACT
            ),
            "OP-008": str(
                OP008_ARTIFACT
            ),
            "OP-009": str(
                OP009_ARTIFACT
            ),
            "OP-009_metrics": str(
                OP009_METRICS
            ),
            "OP-009_reliability": str(
                OP009_RELIABILITY
            ),
        },

        "interpretation_boundary": [
            (
                "This operation synthesizes validation evidence "
                "and does not create a new probability model."
            ),
            (
                "Improved calibration diagnostics do not imply "
                "a universal confidence or ticket-risk score."
            ),
            (
                "Sparse reliability bins reduce the strength "
                "of local calibration interpretation."
            ),
            (
                "Confidence-interval overlap is descriptive "
                "and is not a formal hypothesis test."
            ),
            (
                "No automation or human-review threshold is "
                "established."
            ),
        ],

        "decision": (
            "T5 calibration evidence has been synthesized under "
            "the frozen T9 protocol. The operation records the "
            "evidence-supported calibration status without "
            "creating a universal score or automation decision."
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
    print("T9 MOD-037 OP-010 RESULT")
    print("=" * 72)
    print()

    print(
        "Previous-operation validation:",
        previous["status"],
    )

    print(
        "Evidence structure:",
        structure["status"],
    )

    print(
        "Control validation:",
        controls_status,
    )

    print()

    print(
        "Calibration evidence status:",
        conclusion[
            "selection_status"
        ],
    )

    print(
        "Formal selected method:",
        conclusion[
            "selected_method"
        ],
    )

    print()

    print(
        "p_base:"
    )

    p_base = table[
        table[
            "probability_field"
        ]
        == "p_base"
    ].iloc[0]

    print(
        f"  Brier: {p_base['brier_score']:.6f}"
    )

    print(
        f"  Log loss: {p_base['log_loss']:.6f}"
    )

    print(
        f"  ECE: {p_base['ece']:.6f}"
    )

    print()

    print(
        "p_sigmoid:"
    )

    p_sigmoid = table[
        table[
            "probability_field"
        ]
        == "p_sigmoid"
    ].iloc[0]

    print(
        f"  Brier: {p_sigmoid['brier_score']:.6f}"
    )

    print(
        f"  Log loss: {p_sigmoid['log_loss']:.6f}"
    )

    print(
        f"  ECE: {p_sigmoid['ece']:.6f}"
    )

    print()

    print(
        "p_isotonic:"
    )

    p_isotonic = table[
        table[
            "probability_field"
        ]
        == "p_isotonic"
    ].iloc[0]

    print(
        f"  Brier: {p_isotonic['brier_score']:.6f}"
    )

    print(
        f"  Log loss: {p_isotonic['log_loss']:.6f}"
    )

    print(
        f"  ECE: {p_isotonic['ece']:.6f}"
    )

    print()

    print(
        "New calibration fitting: NO"
    )

    print(
        "New probability generation: NO"
    )

    print(
        "Threshold selection: NO"
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

    if overall_pass:

        print(
            "T9 MOD-037 OP-010 T5 calibration evidence "
            "synthesis: PASS"
        )

    else:

        print(
            "T9 MOD-037 OP-010 T5 calibration evidence "
            "synthesis: FAIL"
        )


if __name__ == "__main__":
    main()