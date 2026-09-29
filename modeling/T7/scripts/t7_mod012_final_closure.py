import json
from pathlib import Path


# ============================================================================
# PATHS
# ============================================================================

ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T7 = ROOT / "modeling/T7"

METRICS = T7 / "metrics"
DERIVED = T7 / "derived"
SPLITS = T7 / "splits"
CONTRACTS = T7 / "contracts"

OUTPUT = (
    METRICS /
    "t7_mod012_final_closure.json"
)


# ============================================================================
# REQUIRED ARTIFACTS
# ============================================================================

REQUIRED = [
    CONTRACTS / "t7_modeling_contract.json",

    METRICS / "t7_mod002_feature_source_audit.json",
    METRICS / "t7_mod003_feature_construction_audit.json",
    METRICS / "t7_mod004_feature_temporal_split_audit.json",
    METRICS / "t7_mod005_split_freeze.json",

    METRICS / "t7_mod006_survival_baseline_audit.json",

    METRICS / "t7_mod007_weibull_aft_model.json",
    METRICS / "t7_mod007_predictive_survival_audit.json",

    METRICS / "t7_mod008_predictive_vs_reference.csv",
    METRICS / "t7_mod008_predictive_vs_reference_audit.json",

    METRICS / "t7_mod009_survival_calibration.csv",
    METRICS / "t7_mod009_survival_calibration_audit.json",

    METRICS / "t7_mod010_log_normal_aft_model.json",
    METRICS / "t7_mod010_log_normal_aft_audit.json",

    METRICS / "t7_mod011_final_model_comparison.csv",
    METRICS / "t7_mod011_final_model_comparison_audit.json",

    SPLITS / "t7_train.csv",
    SPLITS / "t7_evaluation.csv",

    DERIVED / "t7_creation_time_modeling_dataset.csv",
]


# ============================================================================
# HELPERS
# ============================================================================

def load_json(path):
    with path.open(
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


# ============================================================================
# MAIN
# ============================================================================

def main():

    print("=" * 80)
    print(
        "T7 MOD-012 — Final T7 Closure"
    )
    print("=" * 80)

    # ------------------------------------------------------------------------
    # STEP 1 — Artifact existence
    # ------------------------------------------------------------------------

    print(
        "\n[1/5] Checking required T7 artifacts..."
    )

    missing = []

    for path in REQUIRED:

        if path.exists():

            print(
                f"  PASS  {path.name}"
            )

        else:

            print(
                f"  FAIL  {path}"
            )

            missing.append(
                str(path)
            )

    if missing:

        print(
            "\nMissing artifacts:"
        )

        for path in missing:
            print(
                f"  - {path}"
            )

        raise RuntimeError(
            "T7 closure cannot proceed."
        )

    # ------------------------------------------------------------------------
    # STEP 2 — Load final evidence
    # ------------------------------------------------------------------------

    print(
        "\n[2/5] Loading final T7 evidence..."
    )

    mod007 = load_json(
        METRICS /
        "t7_mod007_predictive_survival_audit.json"
    )

    mod009 = load_json(
        METRICS /
        "t7_mod009_survival_calibration_audit.json"
    )

    mod010 = load_json(
        METRICS /
        "t7_mod010_log_normal_aft_audit.json"
    )

    mod011 = load_json(
        METRICS /
        "t7_mod011_final_model_comparison_audit.json"
    )

    print(
        "  PASS  MOD-007 evidence loaded"
    )

    print(
        "  PASS  MOD-009 evidence loaded"
    )

    print(
        "  PASS  MOD-010 evidence loaded"
    )

    print(
        "  PASS  MOD-011 evidence loaded"
    )

    # ------------------------------------------------------------------------
    # STEP 3 — Validate final comparison
    # ------------------------------------------------------------------------

    print(
        "\n[3/5] Validating final comparison evidence..."
    )

    if mod011.get("operation") != "MOD-011":
        raise RuntimeError(
            "MOD-011 audit identifies an unexpected operation."
        )

    if str(
        mod011.get("status", "")
    ).upper() != "COMPLETE":

        raise RuntimeError(
            "MOD-011 is not marked COMPLETE."
        )

    comparison = mod011.get(
        "comparison"
    )

    if not isinstance(
        comparison,
        dict,
    ):
        raise RuntimeError(
            "MOD-011 comparison block is missing."
        )

    required_comparison_fields = [
        "lognormal_minus_weibull_cindex",
        "weibull_horizons_better_than_km",
        "lognormal_horizons_better_than_km",
        "lognormal_horizons_better_than_weibull",
    ]

    for field in required_comparison_fields:

        if field not in comparison:
            raise RuntimeError(
                f"MOD-011 comparison field missing: {field}"
            )

    print(
        "  PASS  MOD-011 final comparison"
    )

    # ------------------------------------------------------------------------
    # STEP 4 — Extract final evidence
    # ------------------------------------------------------------------------

    print(
        "\n[4/5] Constructing final T7 closure..."
    )

    model_info = mod007[
        "model"
    ]

    evaluation_metrics = mod007[
        "evaluation_metrics"
    ]

    population = {
        "training_rows": int(
            model_info[
                "training_rows"
            ]
        ),

        "evaluation_rows": int(
            model_info[
                "evaluation_rows"
            ]
        ),

        "evaluation_event_count": int(
            mod007[
                "evaluation_event_count"
            ]
        ),

        "evaluation_censor_count": int(
            mod007[
                "evaluation_censor_count"
            ]
        ),
    }

    weibull_cindex = float(
        evaluation_metrics[
            "harrell_concordance_index"
        ]
    )

    lognormal_cindex = float(
        mod010[
            "evaluation_metrics"
        ][
            "harrell_concordance_index"
        ]
    )

    closure = {

        "task":
            "T7 Resolution-Time Estimation",

        "operation":
            "MOD-012",

        "status":
            "COMPLETE",

        "closure_type":
            "FINAL_T7_CLOSURE",

        "task_definition": {

            "prediction_boundary":
                "Ticket Creation",

            "target":
                "Time from Creation until first "
                "post-Creation operationally observed "
                "Status change to RESOLVED",

            "event_definition":
                "First qualifying post-Creation "
                "Status change adds RESOLVED",

            "censoring_definition":
                "No qualifying RESOLVED event observed "
                "through the administrative observation endpoint",

            "censoring_treated_as":
                "Right-censored observation",

            "primary_endpoint":
                "First post-Creation Status -> RESOLVED",

            "administrative_endpoint":
                "2024-11-24 07:26:14",
        },

        "population":
            population,

        "data_boundary": {

            "prediction_boundary":
                "Creation",

            "creation_only_features":
                True,

            "post_creation_history_used":
                False,

            "current_status_used":
                False,

            "current_resolution_used":
                False,

            "evaluation_fitting":
                False,

            "raw_archive_access":
                False,
        },

        "chronological_split": {

            "method":
                "Frozen chronological split",

            "training_rows":
                population[
                    "training_rows"
                ],

            "evaluation_rows":
                population[
                    "evaluation_rows"
                ],

            "id_overlap":
                0,

            "population_coverage":
                "PASS",
        },

        "survival_baselines": {

            "kaplan_meier":
                "Established non-parametric survival reference",

            "nelson_aalen":
                "Established cumulative-hazard reference",
        },

        "predictive_models": {

            "weibull_aft": {

                "harrell_concordance_index":
                    weibull_cindex,

                "role":
                    "First predictive survival baseline",
            },

            "lognormal_aft": {

                "harrell_concordance_index":
                    lognormal_cindex,

                "role":
                    "Controlled alternative survival baseline",
            },
        },

        "final_comparison": {

            "lognormal_minus_weibull_cindex":
                comparison[
                    "lognormal_minus_weibull_cindex"
                ],

            "weibull_horizons_better_than_km":
                comparison[
                    "weibull_horizons_better_than_km"
                ],

            "lognormal_horizons_better_than_km":
                comparison[
                    "lognormal_horizons_better_than_km"
                ],

            "lognormal_horizons_better_than_weibull":
                comparison[
                    "lognormal_horizons_better_than_weibull"
                ],

            "evidence_statement":
                mod011[
                    "evidence_statement"
                ],
        },

        "calibration": {

            "mod009_completed":
                True,

            "interpretation":
                "Calibration-style reliability diagnostic; "
                "not a formal IPCW survival calibration estimator.",

            "automation_threshold":
                "NOT_ESTABLISHED",
        },

        "supported_role": {

            "role":
                "SECONDARY_DECISION_SUPPORT_SIGNAL",

            "autonomous_resolution_time_decision":
                False,

            "autonomous_workflow_automation":
                False,

            "validated_human_review_threshold":
                False,
        },

        "limitations": [

            "Creation-time features provide limited discrimination.",

            "Predictive survival models do not uniformly outperform the Kaplan-Meier reference across evaluated horizons.",

            "The Log-Normal AFT model improves the reported comparative metrics over Weibull, but the improvement does not establish operational sufficiency.",

            "MOD-009 is a calibration-style diagnostic rather than a formal IPCW survival calibration estimator.",

            "No empirically validated automation threshold was established.",

            "Right-censoring is intrinsic to the target and must be preserved in interpretation.",

            "T7 evidence does not justify autonomous resolution-time workflow decisions.",
        ],

        "evidence_chain": {

            "MOD-001":
                "Modeling contract",

            "MOD-002":
                "Feature source audit",

            "MOD-003":
                "Feature construction",

            "MOD-004":
                "Feature temporal split audit",

            "MOD-005":
                "Frozen chronological split",

            "MOD-006":
                "Kaplan-Meier / Nelson-Aalen survival baselines",

            "MOD-007":
                "Weibull AFT predictive baseline",

            "MOD-008":
                "Predictive versus reference evaluation",

            "MOD-009":
                "Survival calibration / reliability diagnostic",

            "MOD-010":
                "Log-Normal AFT alternative",

            "MOD-011":
                "Final model comparison",
        },

        "final_project_status": {

            "T7_modeling":
                "COMPLETE",

            "T7_closure":
                "CLOSED",

            "supported_as":
                "SECONDARY_DECISION_SUPPORT_SIGNAL",

            "not_supported_as": [

                "Autonomous resolution-time decision",

                "Autonomous workflow automation",

                "Validated human-review threshold",

                "Production-grade calibrated survival service",
            ],
        },

        "source_evidence": {

            "MOD-009_status":
                mod009.get(
                    "status"
                ),

            "MOD-010_status":
                mod010.get(
                    "status"
                ),

            "MOD-011_status":
                mod011.get(
                    "status"
                ),
        },
    }

    # ------------------------------------------------------------------------
    # STEP 5 — Write closure
    # ------------------------------------------------------------------------

    print(
        "\n[5/5] Writing final closure artifact..."
    )

    with OUTPUT.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            closure,
            f,
            indent=2,
        )

    print(
        "\n" + "=" * 80
    )

    print(
        "MOD-012 COMPLETE — T7 CLOSED"
    )

    print(
        "=" * 80
    )

    print(
        "\nT7 Modeling: COMPLETE"
    )

    print(
        "T7 Closure: CLOSED"
    )

    print(
        "Supported role: SECONDARY_DECISION_SUPPORT_SIGNAL"
    )

    print(
        "\nFinal closure artifact:"
    )

    print(
        OUTPUT
    )


if __name__ == "__main__":
    main()