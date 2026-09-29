#!/usr/bin/env python3

import json
from pathlib import Path

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T7_ROOT = PROJECT_ROOT / "modeling/T7"

FILES = {
    "closure":
        T7_ROOT / "metrics/t7_mod012_final_closure.json",

    "comparison":
        T7_ROOT / "metrics/t7_mod011_final_model_comparison_audit.json",

    "comparison_csv":
        T7_ROOT / "metrics/t7_mod011_final_model_comparison.csv",

    "weibull_audit":
        T7_ROOT / "metrics/t7_mod007_predictive_survival_audit.json",

    "weibull_model":
        T7_ROOT / "metrics/t7_mod007_weibull_aft_model.json",

    "lognormal_audit":
        T7_ROOT / "metrics/t7_mod010_log_normal_aft_audit.json",

    "lognormal_model":
        T7_ROOT / "metrics/t7_mod010_log_normal_aft_model.json",

    "weibull_script":
        T7_ROOT / "scripts/t7_mod007_predictive_survival_baseline.py",

    "lognormal_script":
        T7_ROOT / "scripts/t7_mod010_log_normal_aft_baseline.py",

    "comparison_script":
        T7_ROOT / "scripts/t7_mod011_final_model_comparison.py",

    "contract":
        T7_ROOT / "contracts/t7_modeling_contract.json",

    "split":
        T7_ROOT / "metrics/t7_mod005_split_freeze.json",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path):
    with path.open(
        "r",
        encoding="utf-8",
        errors="replace"
    ) as f:
        return json.load(f)


def print_header(title):
    print("\n" + "=" * 96)
    print(title)
    print("=" * 96)


def relative(path):
    try:
        return path.relative_to(PROJECT_ROOT)
    except ValueError:
        return path


def recursive_find_keys(obj, wanted, prefix=""):
    found = {}

    if isinstance(obj, dict):

        for key, value in obj.items():

            current = (
                f"{prefix}.{key}"
                if prefix
                else key
            )

            if key in wanted:
                found[current] = value

            found.update(
                recursive_find_keys(
                    value,
                    wanted,
                    current
                )
            )

    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            current = f"{prefix}[{index}]"

            found.update(
                recursive_find_keys(
                    value,
                    wanted,
                    current
                )
            )

    return found


def show_selected_keys(label, path, wanted):
    print(
        f"\n--- {label} ---"
    )

    print(
        f"FILE: {relative(path)}"
    )

    if not path.exists():

        print(
            "NOT FOUND"
        )

        return None

    data = load_json(path)

    found = recursive_find_keys(
        data,
        wanted
    )

    for key_path in sorted(found):

        print(
            f"\n{key_path}:"
        )

        print(
            json.dumps(
                found[key_path],
                indent=2,
                ensure_ascii=False
            )
        )

    return data


def search_script(path, terms):
    print(
        f"\n--- {relative(path)} ---"
    )

    if not path.exists():

        print(
            "NOT FOUND"
        )

        return

    text = path.read_text(
        encoding="utf-8",
        errors="replace"
    )

    lines = text.splitlines()

    hits = []

    for number, line in enumerate(
        lines,
        start=1
    ):

        lower = line.lower()

        if any(
            term.lower() in lower
            for term in terms
        ):

            hits.append(
                (
                    number,
                    line
                )
            )

    if not hits:

        print(
            "No semantic markers found."
        )

        return

    for number, line in hits:

        print(
            f"{number:04d}: {line}"
        )


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

print("=" * 96)
print(
    "MOD-026 — T7 FINAL MODEL SELECTION AND "
    "FEATURE CONTRACT EXTRACTION"
)
print("=" * 96)

print(
    "Purpose: establish the exact frozen T7 model, Creation-time "
    "feature contract, survival formulation, and native prediction "
    "representation before controlled OoF generation."
)

print(
    "\nREAD-ONLY AUDIT."
    "\nNo model loading."
    "\nNo model fitting."
    "\nNo prediction generation."
    "\nNo artifact modification."
)


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------

print_header(
    "MOD-026 — AUTHORITATIVE T7 ARTIFACT AVAILABILITY"
)

for label, path in FILES.items():

    print(
        f"{label:20s} "
        f"{'FOUND' if path.exists() else 'MISSING'} "
        f"{relative(path)}"
    )


# ---------------------------------------------------------------------------
# T7 contract
# ---------------------------------------------------------------------------

print_header(
    "MOD-026 — T7 FROZEN MODELING CONTRACT"
)

contract_wanted = {
    "task",
    "task_name",
    "prediction_boundary",
    "target",
    "censoring",
    "leakage_controls",
    "evaluation",
    "features",
    "admitted_features",
    "excluded_features",
    "missingness_policy",
    "modeling_policy",
}

contract = show_selected_keys(
    "T7 modeling contract",
    FILES["contract"],
    contract_wanted
)


# ---------------------------------------------------------------------------
# T7 final closure
# ---------------------------------------------------------------------------

print_header(
    "MOD-026 — T7 FINAL CLOSURE"
)

closure_wanted = {
    "task",
    "task_name",
    "task_definition",
    "prediction_boundary",
    "target",
    "data_boundary",
    "final_model",
    "selected_model",
    "model_selection",
    "selection_basis",
    "selection_reason",
    "comparison",
    "closure_status",
    "limitations",
    "supported_claims",
    "unsupported_claims",
}

closure = show_selected_keys(
    "T7 final closure",
    FILES["closure"],
    closure_wanted
)


# ---------------------------------------------------------------------------
# Final model comparison audit
# ---------------------------------------------------------------------------

print_header(
    "MOD-026 — T7 FINAL MODEL COMPARISON AUDIT"
)

comparison_wanted = {
    "task",
    "task_name",
    "models",
    "weibull",
    "lognormal",
    "log_normal",
    "selection",
    "selected_model",
    "winner",
    "recommendation",
    "comparison",
    "evaluation",
    "metrics",
    "c_index",
    "integrated_brier_score",
    "calibration",
}

comparison = show_selected_keys(
    "T7 final model comparison audit",
    FILES["comparison"],
    comparison_wanted
)


# ---------------------------------------------------------------------------
# Model-specific audit artifacts
# ---------------------------------------------------------------------------

print_header(
    "MOD-026 — WEIBULL AFT AUDIT"
)

weibull_wanted = {
    "task",
    "objective",
    "model",
    "features",
    "feature_columns",
    "prediction",
    "outputs",
    "evaluation",
    "metrics",
    "c_index",
    "integrated_brier_score",
    "calibration",
    "training",
}

show_selected_keys(
    "Weibull AFT predictive audit",
    FILES["weibull_audit"],
    weibull_wanted
)

show_selected_keys(
    "Weibull AFT model artifact",
    FILES["weibull_model"],
    weibull_wanted
)


# ---------------------------------------------------------------------------
# Log-normal audit artifacts
# ---------------------------------------------------------------------------

print_header(
    "MOD-026 — LOG-NORMAL AFT AUDIT"
)

lognormal_wanted = {
    "task",
    "objective",
    "model",
    "features",
    "feature_columns",
    "prediction",
    "outputs",
    "evaluation",
    "metrics",
    "c_index",
    "integrated_brier_score",
    "calibration",
    "training",
}

show_selected_keys(
    "Log-Normal AFT predictive audit",
    FILES["lognormal_audit"],
    lognormal_wanted
)

show_selected_keys(
    "Log-Normal AFT model artifact",
    FILES["lognormal_model"],
    lognormal_wanted
)


# ---------------------------------------------------------------------------
# Chronological split
# ---------------------------------------------------------------------------

print_header(
    "MOD-026 — T7 FROZEN SPLIT CONTRACT"
)

split_wanted = {
    "task",
    "task_name",
    "split_method",
    "ordering",
    "shuffle",
    "fractions",
    "sizes",
    "temporal_boundaries",
    "train",
    "evaluation",
    "event_accounting",
    "artifacts",
}

show_selected_keys(
    "T7 split freeze",
    FILES["split"],
    split_wanted
)


# ---------------------------------------------------------------------------
# Script-level feature and model extraction
# ---------------------------------------------------------------------------

print_header(
    "MOD-026 — WEIBULL IMPLEMENTATION CONTRACT EXTRACTION"
)

implementation_terms = [
    "WeibullAFTFitter",
    "duration_col",
    "event_col",
    "feature_cols",
    "features",
    "Creation time",
    "creation_year_scaled",
    "creation_month_sin",
    "creation_month_cos",
    "weekday_sin",
    "weekday_cos",
    "hour_sin",
    "hour_cos",
    "predict_median",
    "predict_survival_function",
    "211583",
    "1780179",
    "14608619",
    "TRAIN_PATH",
    "EVAL_PATH",
    "fit(",
]

search_script(
    FILES["weibull_script"],
    implementation_terms
)


print_header(
    "MOD-026 — LOG-NORMAL IMPLEMENTATION CONTRACT EXTRACTION"
)

implementation_terms = [
    "LogNormalAFTFitter",
    "duration_col",
    "event_col",
    "feature_cols",
    "features",
    "Creation time",
    "creation_year_scaled",
    "creation_month_sin",
    "creation_month_cos",
    "weekday_sin",
    "weekday_cos",
    "hour_sin",
    "hour_cos",
    "predict_median",
    "predict_survival_function",
    "211583",
    "1780179",
    "14608619",
    "TRAIN_PATH",
    "EVAL_PATH",
    "fit(",
]

search_script(
    FILES["lognormal_script"],
    implementation_terms
)


# ---------------------------------------------------------------------------
# Final comparison implementation
# ---------------------------------------------------------------------------

print_header(
    "MOD-026 — FINAL MODEL COMPARISON IMPLEMENTATION"
)

comparison_terms = [
    "Weibull",
    "LogNormal",
    "Log-Normal",
    "concordance",
    "c_index",
    "integrated_brier",
    "selection",
    "selected",
    "better",
    "winner",
    "t7_mod007",
    "t7_mod010",
]

search_script(
    FILES["comparison_script"],
    comparison_terms
)


# ---------------------------------------------------------------------------
# Native output contract
# ---------------------------------------------------------------------------

print_header(
    "MOD-026 — NATIVE T7 PREDICTION OUTPUT CONTRACT"
)

print(
    """
The existing T7 prediction artifacts establish the following
native predictive representation:

  1. ID
  2. predicted_median_survival_seconds
  3. survival_probability_at_211583_seconds
  4. survival_probability_at_1780179_seconds
  5. survival_probability_at_14608619_seconds

The development OoF generation must preserve survival semantics.

It must NOT:

  - convert survival output into ordinary regression,
  - replace censoring with binary labels,
  - invent a universal T8 score,
  - treat survival probabilities at different horizons as
    independent task labels,
  - use duration_seconds or event as fusion features when
    evaluating predictive evidence,
  - use post-Creation information.
"""
)


# ---------------------------------------------------------------------------
# Contract extraction summary
# ---------------------------------------------------------------------------

print_header(
    "MOD-026 — CONTRACT EXTRACTION SUMMARY"
)

print(
    """
T7 task:
  Resolution-Time Estimation

Prediction boundary:
  Creation

Target:
  Time from Creation to first qualifying post-Creation
  RESOLVED status transition

Censoring:
  Right censoring preserved

Primary survival candidates:
  Weibull AFT
  Log-Normal AFT

Final selected model:
  MUST be determined from the authoritative MOD-011/MOD-012
  comparison/closure evidence above.

Creation-time feature family:
  Expected to be extracted from the implementation scripts
  above; no feature should be added by T8.

Native predictive evidence:
  Survival-native outputs, including predicted median
  survival time and horizon-specific survival probabilities.
"""
)


# ---------------------------------------------------------------------------
# Safety gate
# ---------------------------------------------------------------------------

print_header(
    "MOD-026 — GENERATION SAFETY GATE"
)

print(
    "T2 frozen contract available from MOD-024: YES"
)

print(
    "T7 modeling contract available: "
    f"{'YES' if FILES['contract'].exists() else 'NO'}"
)

print(
    "T7 final closure available: "
    f"{'YES' if FILES['closure'].exists() else 'NO'}"
)

print(
    "T7 final comparison audit available: "
    f"{'YES' if FILES['comparison'].exists() else 'NO'}"
)

print(
    "T7 chronological split freeze available: "
    f"{'YES' if FILES['split'].exists() else 'NO'}"
)

print(
    """
OoF generation remains BLOCKED until the final-model selection
and exact feature/output contract are unambiguously established
from the extracted evidence.
"""
)

print(
    "\nNo model loaded."
)

print(
    "No model trained."
)

print(
    "No prediction generated."
)

print(
    "No artifact modified."
)

print(
    "\nMOD-026 T7 FINAL MODEL SELECTION AND "
    "FEATURE CONTRACT EXTRACTION COMPLETE"
)

print(
    "STATUS: COMPLETE / REVIEW REQUIRED"
)