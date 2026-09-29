from pathlib import Path
import json
import math

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# T7 MOD-013
# Post-Closure Visualization Generation
#
# Visualization only.
# No model fitting.
# No raw archive access.
# No target reconstruction.
# No modification of existing T7 result artifacts.
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T7_ROOT = PROJECT_ROOT / "modeling" / "T7"
DERIVED = T7_ROOT / "derived"
METRICS = T7_ROOT / "metrics"
PLOTS = T7_ROOT / "plots"

PLOTS.mkdir(parents=True, exist_ok=True)


def require_column(df, column, description):
    if column not in df.columns:
        raise KeyError(
            f"Required {description} column '{column}' not found.\n"
            f"Available columns: {list(df.columns)}"
        )


def seconds_to_days(series):
    return pd.to_numeric(
        series,
        errors="coerce"
    ) / 86400.0


def save_figure(fig, filename):
    path = PLOTS / filename

    fig.tight_layout()
    fig.savefig(
        path,
        dpi=220,
        bbox_inches="tight"
    )

    plt.close(fig)

    print(f"  CREATED: {path}")


def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


# ============================================================
# Required artifacts
# ============================================================

KM_CSV = (
    DERIVED /
    "t7_mod006_kaplan_meier_curve.csv"
)

NA_CSV = (
    DERIVED /
    "t7_mod006_nelson_aalen_curve.csv"
)

BRIER_CSV = (
    METRICS /
    "t7_mod008_predictive_vs_reference.csv"
)

CALIBRATION_CSV = (
    METRICS /
    "t7_mod009_survival_calibration.csv"
)

# IMPORTANT:
# C-index is an evaluation result, not a model-parameter
# field. Therefore use the predictive-survival audit files.
WEIBULL_AUDIT_JSON = (
    METRICS /
    "t7_mod007_predictive_survival_audit.json"
)

LOGNORMAL_AUDIT_JSON = (
    METRICS /
    "t7_mod010_log_normal_aft_audit.json"
)


required = [
    KM_CSV,
    NA_CSV,
    BRIER_CSV,
    CALIBRATION_CSV,
    WEIBULL_AUDIT_JSON,
    LOGNORMAL_AUDIT_JSON,
]


print("=" * 80)
print("T7 MOD-013 — POST-CLOSURE VISUALIZATION GENERATION")
print("=" * 80)

print()
print("Checking required artifacts...")

for path in required:

    if not path.is_file():
        raise FileNotFoundError(
            f"Required T7 artifact not found:\n{path}"
        )

    print(f"  PASS: {path}")


# ============================================================
# Load evaluation audit artifacts
# ============================================================

weibull_audit = load_json(
    WEIBULL_AUDIT_JSON
)

lognormal_audit = load_json(
    LOGNORMAL_AUDIT_JSON
)


# ============================================================
# 1. Kaplan–Meier Survival Curve
# ============================================================

print()
print("[1/5] Kaplan–Meier survival curve")

km = pd.read_csv(KM_CSV)

print(
    f"  Kaplan–Meier columns: "
    f"{list(km.columns)}"
)

require_column(
    km,
    "duration_seconds",
    "Kaplan–Meier time"
)

require_column(
    km,
    "kaplan_meier_survival",
    "Kaplan–Meier survival"
)

km_time_days = seconds_to_days(
    km["duration_seconds"]
)

km_survival = pd.to_numeric(
    km["kaplan_meier_survival"],
    errors="coerce"
)

valid = (
    km_time_days.notna()
    & km_survival.notna()
)

fig, ax = plt.subplots(
    figsize=(9, 6)
)

ax.step(
    km_time_days[valid],
    km_survival[valid],
    where="post"
)

ax.set_xlabel(
    "Time since ticket creation (days)"
)

ax.set_ylabel(
    "Estimated survival probability"
)

ax.set_title(
    "T7 — Kaplan–Meier Survival Curve\n"
    "Time to First Observed RESOLVED"
)

ax.set_ylim(
    0,
    1.02
)

ax.grid(
    True,
    alpha=0.25
)

save_figure(
    fig,
    "t7_mod013_kaplan_meier_survival_curve.png"
)


# ============================================================
# 2. Nelson–Aalen Cumulative Hazard
# ============================================================

print()
print("[2/5] Nelson–Aalen cumulative hazard curve")

na = pd.read_csv(NA_CSV)

print(
    f"  Nelson–Aalen columns: "
    f"{list(na.columns)}"
)

require_column(
    na,
    "duration_seconds",
    "Nelson–Aalen time"
)

require_column(
    na,
    "nelson_aalen_cumulative_hazard",
    "Nelson–Aalen cumulative hazard"
)

na_time_days = seconds_to_days(
    na["duration_seconds"]
)

na_hazard = pd.to_numeric(
    na["nelson_aalen_cumulative_hazard"],
    errors="coerce"
)

valid = (
    na_time_days.notna()
    & na_hazard.notna()
)

fig, ax = plt.subplots(
    figsize=(9, 6)
)

ax.step(
    na_time_days[valid],
    na_hazard[valid],
    where="post"
)

ax.set_xlabel(
    "Time since ticket creation (days)"
)

ax.set_ylabel(
    "Cumulative hazard"
)

ax.set_title(
    "T7 — Nelson–Aalen Cumulative Hazard\n"
    "Time to First Observed RESOLVED"
)

ax.grid(
    True,
    alpha=0.25
)

save_figure(
    fig,
    "t7_mod013_nelson_aalen_cumulative_hazard.png"
)


# ============================================================
# 3. IPCW Brier Comparison
# ============================================================

print()
print("[3/5] IPCW Brier comparison")

brier = pd.read_csv(BRIER_CSV)

print(
    f"  Brier columns: "
    f"{list(brier.columns)}"
)

require_column(
    brier,
    "horizon_seconds",
    "Brier horizon"
)

require_column(
    brier,
    "km_reference_ipcw_brier",
    "KM IPCW Brier"
)

require_column(
    brier,
    "predictive_ipcw_brier",
    "predictive IPCW Brier"
)

horizons = pd.to_numeric(
    brier["horizon_seconds"],
    errors="coerce"
)

km_brier = pd.to_numeric(
    brier["km_reference_ipcw_brier"],
    errors="coerce"
)

weibull_brier = pd.to_numeric(
    brier["predictive_ipcw_brier"],
    errors="coerce"
)


# The MOD-010 audit contains the Log-Normal IPCW Brier
# values. Extract only the documented evaluation structure.
lognormal_metrics = lognormal_audit.get(
    "evaluation_metrics",
    {}
)

lognormal_brier_records = lognormal_metrics.get(
    "ipcw_brier",
    []
)

lognormal_brier = {}

for record in lognormal_brier_records:

    horizon = float(
        record["horizon_seconds"]
    )

    score = float(
        record["ipcw_brier_score"]
    )

    lognormal_brier[horizon] = score


lognormal_values = [
    lognormal_brier.get(
        float(h),
        math.nan
    )
    for h in horizons
]

horizon_days = (
    horizons / 86400.0
)


fig, ax = plt.subplots(
    figsize=(9, 6)
)

ax.plot(
    horizon_days,
    km_brier,
    marker="o",
    label="Kaplan–Meier reference"
)

ax.plot(
    horizon_days,
    weibull_brier,
    marker="o",
    label="Weibull AFT"
)

ax.plot(
    horizon_days,
    lognormal_values,
    marker="o",
    label="Log-Normal AFT"
)

ax.set_xlabel(
    "Evaluation horizon (days)"
)

ax.set_ylabel(
    "IPCW Brier score"
)

ax.set_title(
    "T7 — IPCW Brier Score Comparison"
)

ax.legend()

ax.grid(
    True,
    alpha=0.25
)

save_figure(
    fig,
    "t7_mod013_ipcw_brier_comparison.png"
)


# ============================================================
# 4. Survival Calibration-Style Diagnostic
# ============================================================

print()
print(
    "[4/5] Survival calibration-style diagnostic"
)

cal = pd.read_csv(CALIBRATION_CSV)

print(
    f"  Calibration columns: "
    f"{list(cal.columns)}"
)

required_calibration_columns = [
    "horizon_seconds",
    "bin",
    "n",
    "predicted_survival_mean",
    "observed_survival_mean",
    "absolute_calibration_gap",
]

for column in required_calibration_columns:

    require_column(
        cal,
        column,
        "calibration"
    )


cal["horizon_days"] = (
    pd.to_numeric(
        cal["horizon_seconds"],
        errors="coerce"
    ) / 86400.0
)

cal["predicted_survival_mean"] = pd.to_numeric(
    cal["predicted_survival_mean"],
    errors="coerce"
)

cal["observed_survival_mean"] = pd.to_numeric(
    cal["observed_survival_mean"],
    errors="coerce"
)

cal["bin"] = pd.to_numeric(
    cal["bin"],
    errors="coerce"
)

valid = (
    cal["horizon_days"].notna()
    & cal["predicted_survival_mean"].notna()
    & cal["observed_survival_mean"].notna()
    & cal["bin"].notna()
)

cal_valid = cal.loc[
    valid
].copy()


fig, ax = plt.subplots(
    figsize=(8, 7)
)

ax.plot(
    [0, 1],
    [0, 1],
    linestyle="--",
    label="Ideal agreement"
)


for horizon, group in cal_valid.groupby(
    "horizon_days"
):

    group = group.sort_values(
        "predicted_survival_mean"
    )

    ax.plot(
        group["predicted_survival_mean"],
        group["observed_survival_mean"],
        marker="o",
        label=f"{horizon:.1f} days"
    )


ax.set_xlabel(
    "Predicted survival mean"
)

ax.set_ylabel(
    "Observed survival mean"
)

ax.set_title(
    "T7 — Survival Calibration-Style Diagnostic"
)

ax.set_xlim(
    0,
    1
)

ax.set_ylim(
    0,
    1
)

ax.legend()

ax.grid(
    True,
    alpha=0.25
)

save_figure(
    fig,
    "t7_mod013_survival_calibration_style.png"
)


# ============================================================
# 5. C-index Comparison
# ============================================================

print()
print("[5/5] C-index comparison")

print(
    "  Reading C-index from evaluation audit artifacts..."
)

print(
    f"  Weibull audit keys: "
    f"{list(weibull_audit.keys())}"
)

print(
    f"  Log-Normal audit keys: "
    f"{list(lognormal_audit.keys())}"
)


# Actual MOD-007 audit schema established earlier:
#
# top-level:
#   task
#   operation
#   status
#   model
#   feature_boundary
#   features
#   train_event_count
#   train_censor_count
#   evaluation_event_count
#   evaluation_censor_count
#   weibull
#   evaluation_metrics
#   artifacts
#
# The C-index is under evaluation_metrics.

weibull_evaluation = weibull_audit[
    "evaluation_metrics"
]

lognormal_evaluation = lognormal_audit[
    "evaluation_metrics"
]


weibull_cindex = float(
    weibull_evaluation[
        "harrell_concordance_index"
    ]
)

lognormal_cindex = float(
    lognormal_evaluation[
        "harrell_concordance_index"
    ]
)


print(
    f"  Weibull C-index: "
    f"{weibull_cindex:.9f}"
)

print(
    f"  Log-Normal C-index: "
    f"{lognormal_cindex:.9f}"
)


models = [
    "Weibull AFT",
    "Log-Normal AFT"
]

cindices = [
    weibull_cindex,
    lognormal_cindex
]


fig, ax = plt.subplots(
    figsize=(8, 6)
)

bars = ax.bar(
    models,
    cindices
)

ax.set_ylabel(
    "Harrell C-index"
)

ax.set_title(
    "T7 — Predictive Survival Model C-index"
)

lower = max(
    0,
    min(cindices) - 0.02
)

upper = min(
    1,
    max(cindices) + 0.02
)

ax.set_ylim(
    lower,
    upper
)

ax.grid(
    axis="y",
    alpha=0.25
)


for bar, value in zip(
    bars,
    cindices
):

    ax.text(
        bar.get_x()
        + bar.get_width() / 2,
        value,
        f"{value:.6f}",
        ha="center",
        va="bottom"
    )


save_figure(
    fig,
    "t7_mod013_cindex_comparison.png"
)


# ============================================================
# Final Visualization Manifest
# ============================================================

manifest = {

    "operation":
        "T7 MOD-013",

    "purpose":
        "Post-closure visualization generation",

    "model_refit":
        False,

    "raw_archive_access":
        False,

    "target_reconstruction":
        False,

    "source_artifacts": [
        str(KM_CSV),
        str(NA_CSV),
        str(BRIER_CSV),
        str(CALIBRATION_CSV),
        str(WEIBULL_AUDIT_JSON),
        str(LOGNORMAL_AUDIT_JSON),
    ],

    "plots": [

        "t7_mod013_kaplan_meier_survival_curve.png",

        "t7_mod013_nelson_aalen_cumulative_hazard.png",

        "t7_mod013_ipcw_brier_comparison.png",

        "t7_mod013_survival_calibration_style.png",

        "t7_mod013_cindex_comparison.png",
    ],

    "status":
        "COMPLETE"
}


manifest_path = (
    METRICS /
    "t7_mod013_visualization_manifest.json"
)


with open(
    manifest_path,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        manifest,
        f,
        indent=2
    )


print()
print("=" * 80)
print("T7 MOD-013 COMPLETE")
print("=" * 80)

print()
print("Generated plots:")

for filename in manifest["plots"]:

    print(
        f"  {PLOTS / filename}"
    )

print()
print(
    f"Manifest: {manifest_path}"
)