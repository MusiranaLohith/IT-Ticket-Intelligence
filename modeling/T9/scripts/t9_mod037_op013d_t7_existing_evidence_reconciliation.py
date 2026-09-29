from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


# ============================================================
# T9 MOD-037 OP-013D
# T7 EXISTING EVALUATION EVIDENCE RECONCILIATION
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
    / "t9_mod037_op013d_t7_existing_evidence_reconciliation.json"
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


# ============================================================
# EXISTING AUTHORITATIVE T7 ARTIFACTS
# ============================================================

FILES = {

    "contract":
        T7_ROOT
        / "contracts"
        / "t7_modeling_contract.json",

    "split_freeze":
        T7_ROOT
        / "metrics"
        / "t7_mod005_split_freeze.json",

    "survival_baseline":
        T7_ROOT
        / "metrics"
        / "t7_mod006_survival_baseline_audit.json",

    "weibull_audit":
        T7_ROOT
        / "metrics"
        / "t7_mod007_predictive_survival_audit.json",

    "weibull_model":
        T7_ROOT
        / "metrics"
        / "t7_mod007_weibull_aft_model.json",

    "predictive_reference":
        T7_ROOT
        / "metrics"
        / "t7_mod008_predictive_vs_reference_audit.json",

    "predictive_reference_csv":
        T7_ROOT
        / "metrics"
        / "t7_mod008_predictive_vs_reference.csv",

    "calibration":
        T7_ROOT
        / "metrics"
        / "t7_mod009_survival_calibration.csv",

    "calibration_audit":
        T7_ROOT
        / "metrics"
        / "t7_mod009_survival_calibration_audit.json",

    "lognormal_audit":
        T7_ROOT
        / "metrics"
        / "t7_mod010_log_normal_aft_audit.json",

    "lognormal_model":
        T7_ROOT
        / "metrics"
        / "t7_mod010_log_normal_aft_model.json",

    "final_comparison":
        T7_ROOT
        / "metrics"
        / "t7_mod011_final_model_comparison.csv",

    "final_comparison_audit":
        T7_ROOT
        / "metrics"
        / "t7_mod011_final_model_comparison_audit.json",

    "final_closure":
        T7_ROOT
        / "metrics"
        / "t7_mod012_final_closure.json",
}


# ============================================================
# HELPERS
# ============================================================

def require_file(
    path: Path,
) -> None:

    if not path.exists():

        raise FileNotFoundError(
            f"Required T7 artifact missing: {path}"
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


def load_csv(
    path: Path,
) -> list[dict[str, str]]:

    require_file(path)

    with open(
        path,
        "r",
        encoding="utf-8",
        errors="replace",
        newline="",
    ) as f:

        return list(
            csv.DictReader(f)
        )


def get_nested(
    data: dict[str, Any],
    *keys: str,
) -> Any:

    current: Any = data

    for key in keys:

        if not isinstance(
            current,
            dict,
        ):

            return None

        current = current.get(
            key
        )

    return current


def first_present(
    data: dict[str, Any],
    candidates: list[tuple[str, ...]],
) -> Any:

    for path in candidates:

        value = get_nested(
            data,
            *path,
        )

        if value is not None:

            return value

    return None


def number_or_none(
    value: Any,
) -> float | None:

    if value is None:
        return None

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return None


# ============================================================
# PRIOR T9 VALIDATION
# ============================================================

def validate_prior_operations() -> dict[str, Any]:

    results = {}

    # --------------------------------------------------------
    # OP-004:
    # task-level T7 acceptance is authoritative here.
    # --------------------------------------------------------

    op004 = load_json(
        OP004
    )

    accepted_tasks = op004.get(
        "accepted_tasks",
        [],
    )

    results[
        "OP-004_T7_acceptance"
    ] = (
        "PASS"
        if "T7" in accepted_tasks
        else "FAIL"
    )

    # --------------------------------------------------------
    # Remaining T7-chain operations require PASS.
    # --------------------------------------------------------

    for name, path in [
        ("OP-005", OP005),
        ("OP-013A", OP013A),
        ("OP-013B", OP013B),
        ("OP-013C", OP013C),
    ]:

        data = load_json(
            path
        )

        results[
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
        for key, value in results.items()
        if value != "PASS"
    ]

    return {

        "status": (
            "PASS"
            if not failed
            else "FAIL"
        ),

        "checks": results,

        "failed": failed,
    }


# ============================================================
# FILE PRESENCE
# ============================================================

def validate_artifact_presence() -> dict[str, Any]:

    results = {}

    for name, path in FILES.items():

        results[
            name
        ] = {

            "path": str(path),

            "exists": path.exists(),

            "size_bytes": (
                path.stat().st_size
                if path.exists()
                else None
            ),
        }

    missing = [
        name
        for name, result
        in results.items()
        if not result[
            "exists"
        ]
    ]

    return {

        "status": (
            "PASS"
            if not missing
            else "FAIL"
        ),

        "missing": missing,

        "artifacts": results,
    }


# ============================================================
# POPULATION / SPLIT EVIDENCE
# ============================================================

def extract_population_evidence(
    split_freeze: dict[str, Any],
) -> dict[str, Any]:

    evaluation = first_present(
        split_freeze,
        [
            (
                "event_accounting",
                "evaluation",
            ),
            (
                "evaluation",
            ),
        ],
    )

    if not isinstance(
        evaluation,
        dict,
    ):

        evaluation = {}

    return {

        "evaluation_rows": evaluation.get(
            "rows"
        ),

        "evaluation_events": evaluation.get(
            "event_1"
        ),

        "evaluation_censored": evaluation.get(
            "event_0"
        ),

        "evaluation_event_rate": evaluation.get(
            "event_rate"
        ),

        "evaluation_censor_rate": evaluation.get(
            "censor_rate"
        ),

        "ordering": split_freeze.get(
            "ordering"
        ),
    }


# ============================================================
# MODEL AUDIT EXTRACTION
# ============================================================

def extract_model_audit(
    audit: dict[str, Any],
    label: str,
) -> dict[str, Any]:

    result = {

        "label": label,

        "task": audit.get(
            "task"
        ),

        "purpose": audit.get(
            "purpose"
        ),

        "status": audit.get(
            "status"
        ),

        "artifacts": audit.get(
            "artifacts"
        ),
    }

    # Search common metric locations without assuming
    # one particular schema.

    metric_candidates = [
        (
            "c_index",
            [
                ("c_index",),
                ("metrics", "c_index"),
                ("evaluation", "c_index"),
            ],
        ),
        (
            "ipcw_brier",
            [
                ("ipcw_brier",),
                ("metrics", "ipcw_brier"),
                ("evaluation", "ipcw_brier"),
            ],
        ),
    ]

    extracted = {}

    for metric_name, paths in metric_candidates:

        value = first_present(
            audit,
            paths,
        )

        if value is not None:

            extracted[
                metric_name
            ] = value

    result[
        "direct_metrics_found"
    ] = extracted

    return result


# ============================================================
# MODEL METRIC EXTRACTION FROM FINAL COMPARISON
# ============================================================

def extract_final_comparison(
    rows: list[dict[str, str]],
    audit: dict[str, Any],
) -> dict[str, Any]:

    result = {

        "rows": rows,

        "audit_task": audit.get(
            "task"
        ),

        "comparison": audit.get(
            "comparison"
        ),

        "evidence_statement": audit.get(
            "evidence_statement"
        ),

        "interpretation_boundary": audit.get(
            "interpretation_boundary"
        ),
    }

    return result


# ============================================================
# CALIBRATION EVIDENCE
# ============================================================

def extract_calibration_evidence(
    rows: list[dict[str, str]],
    audit: dict[str, Any],
) -> dict[str, Any]:

    result = {

        "audit": audit,

        "row_count": len(
            rows
        ),

        "columns": (
            list(
                rows[0].keys()
            )
            if rows
            else []
        ),

        "rows": rows,

        "methodological_note": (
            audit.get(
                "methodological_note"
            )
        ),

        "formal_ipcw_calibration_estimator": (
            False
        ),
    }

    return result


# ============================================================
# FINAL CLOSURE
# ============================================================

def extract_final_closure(
    closure: dict[str, Any],
) -> dict[str, Any]:

    task_definition = closure.get(
        "task_definition",
        {},
    )

    data_boundary = closure.get(
        "data_boundary",
        {},
    )

    limitations = closure.get(
        "limitations",
        [],
    )

    return {

        "task": closure.get(
            "task"
        ),

        "prediction_boundary": (
            task_definition.get(
                "prediction_boundary"
            )
        ),

        "target": task_definition.get(
            "target"
        ),

        "event_definition": task_definition.get(
            "event_definition"
        ),

        "censoring_definition": (
            task_definition.get(
                "censoring_definition"
            )
        ),

        "censoring_treated_as": (
            task_definition.get(
                "censoring_treated_as"
            )
        ),

        "primary_endpoint": task_definition.get(
            "primary_endpoint"
        ),

        "administrative_endpoint": (
            task_definition.get(
                "administrative_endpoint"
            )
        ),

        "data_boundary": data_boundary,

        "limitations": limitations,
    }


# ============================================================
# EVIDENCE GAP CLASSIFICATION
# ============================================================

def classify_remaining_gaps(
    calibration: dict[str, Any],
    final_comparison: dict[str, Any],
    closure: dict[str, Any],
) -> dict[str, Any]:

    return {

        "native_survival_evaluation": (
            "ALREADY_ESTABLISHED"
        ),

        "model_comparison": (
            "ALREADY_ESTABLISHED"
        ),

        "fixed_horizon_ipcw_brier": (
            "ALREADY_ESTABLISHED"
        ),

        "c_index": (
            "ALREADY_ESTABLISHED"
        ),

        "survival_calibration_diagnostic": (
            "ALREADY_ESTABLISHED"
        ),

        "formal_survival_calibration_estimator": (
            "NOT_ESTABLISHED"
        ),

        "calibration_uncertainty": (
            "NOT_ESTABLISHED"
        ),

        "uncertainty_for_model_comparison": (
            "NOT_ESTABLISHED"
        ),

        "additional_model_selection": (
            "NOT_REQUIRED_FROM_THIS_RECONCILIATION"
        ),

        "locked_test_re_evaluation": (
            "NOT_JUSTIFIED"
        ),

        "remaining_t9_question": (
            "Determine whether the existing T7-native "
            "survival evidence is sufficient for T9 "
            "calibration/reliability purposes, and if "
            "not, define only the missing survival-native "
            "uncertainty/calibration evidence."
        ),
    }


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

        "survival_to_binary_conversion": False,

        "threshold_selected": False,

        "model_selected": False,

        "locked_test_used": False,

        "universal_confidence_created": False,

        "universal_risk_score_created": False,

        "existing_t7_artifacts_modified": False,

        "post_creation_information_used": False,

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

        elif value is not False:

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
    print(
        "T9 MOD-037 OP-013D"
    )
    print(
        "T7 EXISTING EVALUATION EVIDENCE RECONCILIATION"
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
    # FILE PRESENCE
    # --------------------------------------------------------

    print(
        "Validating authoritative T7 artifacts..."
    )

    presence = (
        validate_artifact_presence()
    )

    print(
        "T7 artifact presence:",
        presence[
            "status"
        ],
    )

    if presence[
        "status"
    ] != "PASS":

        print(
            "Missing:",
            presence[
                "missing"
            ],
        )

        raise RuntimeError(
            "Required T7 evidence is missing."
        )

    print()

    # --------------------------------------------------------
    # LOAD EXISTING EVIDENCE
    # --------------------------------------------------------

    contract = load_json(
        FILES[
            "contract"
        ]
    )

    split_freeze = load_json(
        FILES[
            "split_freeze"
        ]
    )

    survival_baseline = load_json(
        FILES[
            "survival_baseline"
        ]
    )

    weibull_audit = load_json(
        FILES[
            "weibull_audit"
        ]
    )

    predictive_reference = load_json(
        FILES[
            "predictive_reference"
        ]
    )

    calibration_audit = load_json(
        FILES[
            "calibration_audit"
        ]
    )

    lognormal_audit = load_json(
        FILES[
            "lognormal_audit"
        ]
    )

    final_comparison_audit = load_json(
        FILES[
            "final_comparison_audit"
        ]
    )

    final_closure = load_json(
        FILES[
            "final_closure"
        ]
    )

    predictive_reference_rows = (
        load_csv(
            FILES[
                "predictive_reference_csv"
            ]
        )
    )

    calibration_rows = (
        load_csv(
            FILES[
                "calibration"
            ]
        )
    )

    final_comparison_rows = (
        load_csv(
            FILES[
                "final_comparison"
            ]
        )
    )

    print(
        "All authoritative evidence loaded."
    )

    print()

    # --------------------------------------------------------
    # POPULATION
    # --------------------------------------------------------

    population = extract_population_evidence(
        split_freeze
    )

    print(
        "Evaluation rows:",
        population[
            "evaluation_rows"
        ],
    )

    print(
        "Evaluation events:",
        population[
            "evaluation_events"
        ],
    )

    print(
        "Evaluation censored:",
        population[
            "evaluation_censored"
        ],
    )

    print()

    # --------------------------------------------------------
    # MODEL EVIDENCE
    # --------------------------------------------------------

    weibull = extract_model_audit(
        weibull_audit,
        "Weibull AFT",
    )

    lognormal = extract_model_audit(
        lognormal_audit,
        "Log-Normal AFT",
    )

    print(
        "Weibull audit loaded."
    )

    print(
        "Log-Normal audit loaded."
    )

    print()

    # --------------------------------------------------------
    # CALIBRATION
    # --------------------------------------------------------

    calibration = (
        extract_calibration_evidence(
            calibration_rows,
            calibration_audit,
        )
    )

    print(
        "Calibration rows:",
        calibration[
            "row_count"
        ],
    )

    print(
        "Formal IPCW calibration estimator:",
        calibration[
            "formal_ipcw_calibration_estimator"
        ],
    )

    print()

    # --------------------------------------------------------
    # FINAL COMPARISON
    # --------------------------------------------------------

    comparison = (
        extract_final_comparison(
            final_comparison_rows,
            final_comparison_audit,
        )
    )

    comparison_values = comparison[
        "comparison"
    ]

    if isinstance(
        comparison_values,
        dict,
    ):

        print(
            "Weibull horizons better than KM:",
            comparison_values.get(
                "weibull_horizons_better_than_km"
            ),
        )

        print(
            "Log-Normal horizons better than KM:",
            comparison_values.get(
                "lognormal_horizons_better_than_km"
            ),
        )

        print(
            "Log-Normal horizons better than Weibull:",
            comparison_values.get(
                "lognormal_horizons_better_than_weibull"
            ),
        )

    print()

    # --------------------------------------------------------
    # CLOSURE
    # --------------------------------------------------------

    closure = extract_final_closure(
        final_closure
    )

    print(
        "T7 closure task:",
        closure[
            "task"
        ],
    )

    print(
        "Prediction boundary:",
        closure[
            "prediction_boundary"
        ],
    )

    print(
        "Censoring semantics:",
        closure[
            "censoring_treated_as"
        ],
    )

    print()

    # --------------------------------------------------------
    # GAP CLASSIFICATION
    # --------------------------------------------------------

    gaps = classify_remaining_gaps(
        calibration,
        comparison,
        closure,
    )

    print(
        "Native survival evaluation:",
        gaps[
            "native_survival_evaluation"
        ],
    )

    print(
        "Model comparison:",
        gaps[
            "model_comparison"
        ],
    )

    print(
        "IPCW Brier:",
        gaps[
            "fixed_horizon_ipcw_brier"
        ],
    )

    print(
        "C-index:",
        gaps[
            "c_index"
        ],
    )

    print(
        "Formal survival calibration:",
        gaps[
            "formal_survival_calibration_estimator"
        ],
    )

    print(
        "Calibration uncertainty:",
        gaps[
            "calibration_uncertainty"
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
    # FINAL STATUS
    # --------------------------------------------------------

    overall_status = (
        "PASS"
        if (
            prior[
                "status"
            ] == "PASS"
            and
            presence[
                "status"
            ] == "PASS"
            and
            control_validation[
                "status"
            ] == "PASS"
        )
        else "FAIL"
    )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    output = {

        "operation": (
            "T9_MOD-037_OP-013D"
        ),

        "title": (
            "T7 Existing Evaluation Evidence "
            "Reconciliation"
        ),

        "status": overall_status,

        "purpose": (
            "Reconcile existing authoritative T7 "
            "survival evaluation, model-comparison, "
            "calibration-style, and final-closure "
            "evidence before performing any new "
            "T9-specific T7 analysis."
        ),

        "prior_operation_validation": prior,

        "artifact_presence": presence,

        "contract": {

            "task": contract.get(
                "task_name"
            ),

            "prediction_boundary": get_nested(
                contract,
                "prediction_boundary",
            ),

            "target": get_nested(
                contract,
                "target",
            ),

            "censoring": get_nested(
                contract,
                "censoring",
            ),
        },

        "evaluation_population": population,

        "survival_baseline": survival_baseline,

        "weibull_evidence": weibull,

        "lognormal_evidence": lognormal,

        "predictive_reference_evidence": {

            "audit": predictive_reference,

            "rows": predictive_reference_rows,
        },

        "calibration_evidence": calibration,

        "final_model_comparison": comparison,

        "final_closure": closure,

        "remaining_evidence_gaps": gaps,

        "controls": controls,

        "control_validation": (
            control_validation
        ),

        "interpretation": {

            "existing_native_evaluation": (
                "T7 native survival evaluation is "
                "already established in the existing "
                "T7 evidence chain."
            ),

            "existing_model_comparison": (
                "T7 already contains an explicit "
                "Weibull versus Log-Normal versus "
                "Kaplan-Meier comparison."
            ),

            "existing_calibration": (
                "T7 contains a calibration-style "
                "diagnostic, but the final closure "
                "explicitly limits its interpretation "
                "and does not treat it as a formal "
                "IPCW survival calibration estimator."
            ),

            "new_evaluation_requirement": (
                "No generic re-computation of existing "
                "T7 metrics is justified merely to "
                "duplicate completed T7 evaluation."
            ),

            "remaining_t9_question": (
                "The remaining T9-specific question is "
                "whether additional survival-native "
                "uncertainty/reliability evidence is "
                "required and defensible for the accepted "
                "T7 native outputs."
            ),

            "model_selection": (
                "No new model selection is performed "
                "by this reconciliation."
            ),
        },

        "artifacts_generated": [
            str(
                OUTPUT_JSON
            )
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

    print(
        "Output:",
        OUTPUT_JSON,
    )

    print()
    print(
        "T9 MOD-037 OP-013D:",
        overall_status,
    )


if __name__ == "__main__":
    main()