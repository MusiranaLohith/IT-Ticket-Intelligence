from pathlib import Path
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# T9 MOD-037 FINAL VISUALIZATION PASS
# READ-ONLY PRESENTATION LAYER
#
# No model fitting
# No prediction generation
# No probability generation
# No calibration fitting
# No target modification
# No threshold selection
# No model selection
# No cross-task aggregation
# ============================================================


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T9_ROOT = PROJECT_ROOT / "modeling" / "T9" / "mod037"
T7_ROOT = PROJECT_ROOT / "modeling" / "T7"
T8_ROOT = PROJECT_ROOT / "modeling" / "T8"

PLOTS_ROOT = T9_ROOT / "plots"
PLOTS_ROOT.mkdir(parents=True, exist_ok=True)


def require_file(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Required artifact missing:\n{path}"
        )
    return path


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def savefig(fig, filename):
    path = PLOTS_ROOT / filename
    fig.tight_layout()
    fig.savefig(
        path,
        dpi=180,
        bbox_inches="tight",
    )
    plt.close(fig)
    print(f"CREATED: {path}")


def print_columns(label, df):
    print(f"{label} columns:")
    for column in df.columns:
        print(f"  - {column}")


print("=" * 72)
print("T9 MOD-037 FINAL VISUALIZATION PASS")
print("=" * 72)
print()
print("Read-only presentation layer.")
print(
    "No model fitting, probability generation, calibration fitting,"
)
print(
    "target modification, threshold selection, or cross-task aggregation."
)
print()


# ============================================================
# 1. T5 RELIABILITY DIAGRAM
# ============================================================

print("[1/6] T5 reliability diagram")

t5_rel_path = require_file(
    T9_ROOT / "t9_mod037_op008_t5_reliability_bins.csv"
)

t5_rel = pd.read_csv(t5_rel_path)

print_columns("T5 reliability", t5_rel)

required_t5_columns = {
    "probability_field",
    "bin_index",
    "count",
    "mean_predicted",
    "observed_event_rate",
    "absolute_gap",
    "weighted_gap",
}

missing = required_t5_columns - set(t5_rel.columns)

if missing:
    raise RuntimeError(
        "T5 reliability artifact is missing expected columns: "
        f"{sorted(missing)}"
    )


fig, ax = plt.subplots(figsize=(8, 6))

for probability_field in [
    "p_base",
    "p_sigmoid",
    "p_isotonic",
]:
    subset = t5_rel[
        t5_rel["probability_field"].astype(str)
        == probability_field
    ].copy()

    subset = subset.dropna(
        subset=[
            "mean_predicted",
            "observed_event_rate",
        ]
    )

    subset = subset.sort_values("mean_predicted")

    if subset.empty:
        print(
            f"WARNING: no reliability rows for "
            f"{probability_field}"
        )
        continue

    ax.plot(
        subset["mean_predicted"],
        subset["observed_event_rate"],
        marker="o",
        linewidth=1.8,
        label=probability_field,
    )


ax.plot(
    [0, 1],
    [0, 1],
    linestyle="--",
    linewidth=1.2,
    label="Perfect calibration",
)

ax.set_xlabel("Mean predicted probability")
ax.set_ylabel("Observed event rate")
ax.set_title(
    "T5 Native Probability Reliability"
)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.legend()
ax.grid(alpha=0.25)

savefig(
    fig,
    "t9_t5_reliability_diagram.png",
)


# ============================================================
# 2. T5 CALIBRATION METRICS
# ============================================================

print("[2/6] T5 calibration metrics")

t5_synthesis_path = require_file(
    T9_ROOT
    / "t9_mod037_op010_t5_calibration_evidence_synthesis.json"
)

t5_synthesis = load_json(t5_synthesis_path)

if not isinstance(t5_synthesis, dict):
    raise RuntimeError(
        "T5 OP-010 synthesis artifact is not a JSON object."
    )


# Existing OP-010 evidence values.
# No new calibration or fitting is performed.
t5_metrics = pd.DataFrame(
    {
        "probability_field": [
            "p_base",
            "p_sigmoid",
            "p_isotonic",
        ],
        "Brier": [
            0.031010,
            0.005862,
            0.005845,
        ],
        "Log Loss": [
            0.119526,
            0.028366,
            0.029754,
        ],
        "ECE": [
            0.075796,
            0.001051,
            0.001321,
        ],
    }
)


x = np.arange(len(t5_metrics))
width = 0.25

fig, ax = plt.subplots(figsize=(9, 6))

for offset, metric in enumerate(
    ["Brier", "Log Loss", "ECE"]
):
    ax.bar(
        x + (offset - 1) * width,
        t5_metrics[metric].to_numpy(),
        width,
        label=metric,
    )

ax.set_xticks(x)
ax.set_xticklabels(
    t5_metrics["probability_field"]
)
ax.set_ylabel("Metric value")
ax.set_title(
    "T5 Calibration Evidence — Descriptive Comparison"
)
ax.legend()
ax.grid(
    axis="y",
    alpha=0.25,
)

savefig(
    fig,
    "t9_t5_calibration_metrics.png",
)


# ============================================================
# 3. T4 NATIVE RANKING
# ============================================================

print("[3/6] T4 native ranking")

t4_path = require_file(
    T8_ROOT
    / "mod036"
    / "op020"
    / "t8_mod036_op020_assignment_predictions.csv"
)

t4 = pd.read_csv(t4_path)

print_columns("T4 predictions", t4)

required_t4_columns = {
    "true_assignee",
    "recommended_assignee",
    "recommended_score",
    "target_rank",
    "target_present",
}

missing = required_t4_columns - set(t4.columns)

if missing:
    raise RuntimeError(
        "T4 prediction artifact is missing columns: "
        f"{sorted(missing)}"
    )


t4_present = t4[
    t4["target_present"].astype(bool)
    & t4["target_rank"].notna()
].copy()

t4_present["target_rank"] = pd.to_numeric(
    t4_present["target_rank"],
    errors="coerce",
)

t4_present = t4_present.dropna(
    subset=["target_rank"]
)

k_values = np.array(
    [1, 3, 5, 10, 20]
)

hit_values = np.array(
    [
        (t4_present["target_rank"] <= k).mean()
        for k in k_values
    ]
)

fig, axes = plt.subplots(
    1,
    2,
    figsize=(13, 5),
)

rank_counts = (
    t4_present["target_rank"]
    .value_counts()
    .sort_index()
)

rank_display = rank_counts[
    rank_counts.index <= 20
]

axes[0].bar(
    rank_display.index.astype(int),
    rank_display.values,
)

axes[0].set_xlabel(
    "Native target rank"
)
axes[0].set_ylabel(
    "Evaluation rows"
)
axes[0].set_title(
    "T4 Target-Rank Distribution (Ranks 1–20)"
)
axes[0].grid(
    axis="y",
    alpha=0.25,
)


axes[1].plot(
    k_values,
    hit_values,
    marker="o",
    linewidth=1.8,
)

axes[1].set_xlabel("K")
axes[1].set_ylabel("Hit@K")
axes[1].set_title(
    "T4 Native Candidate-Ranking Hit@K"
)
axes[1].set_xticks(k_values)
axes[1].set_ylim(0, 1)
axes[1].grid(alpha=0.25)


savefig(
    fig,
    "t9_t4_native_ranking.png",
)


# ============================================================
# 4. T6 NATIVE RETRIEVAL + BOOTSTRAP CI
# ============================================================

print("[4/6] T6 native retrieval")

t6_results_path = require_file(
    T9_ROOT
    / "t9_mod037_op012c_t6_query_level_results.csv"
)

t6_bootstrap_path = require_file(
    T9_ROOT
    / "t9_mod037_op012d_t6_bootstrap_summary.csv"
)

t6_results = pd.read_csv(
    t6_results_path
)

t6_bootstrap = pd.read_csv(
    t6_bootstrap_path
)

print_columns(
    "T6 query-level results",
    t6_results,
)

print_columns(
    "T6 bootstrap summary",
    t6_bootstrap,
)


required_t6_results = {
    "query_id",
    "candidate_count",
    "target_observed_count",
    "target_present",
    "target_rank",
    "target_candidate_id",
    "target_hybrid_score",
}

missing = required_t6_results - set(
    t6_results.columns
)

if missing:
    raise RuntimeError(
        "T6 query-level artifact is missing columns: "
        f"{sorted(missing)}"
    )


required_t6_bootstrap = {
    "metric",
    "point_estimate",
    "bootstrap_mean",
    "bootstrap_std",
    "ci_lower_95",
    "ci_upper_95",
    "replicates",
}

missing = required_t6_bootstrap - set(
    t6_bootstrap.columns
)

if missing:
    raise RuntimeError(
        "T6 bootstrap artifact is missing columns: "
        f"{sorted(missing)}"
    )


# Actual metric names in the frozen artifact:
# hit_at_1, hit_at_3, ..., hit_at_100, mrr

t6_hit_rows = t6_bootstrap[
    t6_bootstrap["metric"].astype(str).str.startswith(
        "hit_at_"
    )
].copy()

if t6_hit_rows.empty:
    raise RuntimeError(
        "No hit_at_* rows were found in the T6 "
        "bootstrap artifact."
    )


t6_hit_rows["k"] = pd.to_numeric(
    t6_hit_rows["metric"]
    .astype(str)
    .str.replace("hit_at_", "", regex=False),
    errors="coerce",
)

t6_hit_rows = t6_hit_rows.dropna(
    subset=["k"]
)

t6_hit_rows["k"] = (
    t6_hit_rows["k"].astype(int)
)

t6_hit_rows = t6_hit_rows.sort_values(
    "k"
)

t6_k = t6_hit_rows["k"].to_numpy()

t6_hit = t6_hit_rows[
    "point_estimate"
].to_numpy(dtype=float)

t6_ci_lower = t6_hit_rows[
    "ci_lower_95"
].to_numpy(dtype=float)

t6_ci_upper = t6_hit_rows[
    "ci_upper_95"
].to_numpy(dtype=float)


fig, ax = plt.subplots(figsize=(9, 6))

ax.errorbar(
    t6_k,
    t6_hit,
    yerr=[
        t6_hit - t6_ci_lower,
        t6_ci_upper - t6_hit,
    ],
    fmt="o-",
    capsize=4,
    linewidth=1.5,
)

ax.set_xlabel("K")
ax.set_ylabel("Hit@K")
ax.set_title(
    "T6 Native Retrieval Performance "
    "with 95% Bootstrap CIs"
)
ax.set_xticks(t6_k)
ax.set_ylim(
    max(0, float(t6_ci_lower.min()) - 0.05),
    1.02,
)
ax.grid(alpha=0.25)

savefig(
    fig,
    "t9_t6_native_retrieval_bootstrap.png",
)


# ============================================================
# 5. T7 SURVIVAL IPCW BRIER
# ============================================================

print("[5/6] T7 survival Brier evidence")

t7_compare_path = require_file(
    T7_ROOT
    / "metrics"
    / "t7_mod011_final_model_comparison.csv"
)

t7_compare = pd.read_csv(
    t7_compare_path
)

print_columns(
    "T7 final model comparison",
    t7_compare,
)

required_t7_columns = {
    "horizon_seconds",
    "kaplan_meier_ipcw_brier",
    "weibull_aft_ipcw_brier",
    "lognormal_aft_ipcw_brier",
    "weibull_minus_km",
    "lognormal_minus_km",
    "lognormal_minus_weibull",
}

missing = required_t7_columns - set(
    t7_compare.columns
)

if missing:
    raise RuntimeError(
        "T7 final model comparison is missing columns: "
        f"{sorted(missing)}"
    )


horizon_days = (
    t7_compare["horizon_seconds"].to_numpy(
        dtype=float
    )
    / 86400.0
)

fig, ax = plt.subplots(figsize=(9, 6))

ax.plot(
    horizon_days,
    t7_compare[
        "kaplan_meier_ipcw_brier"
    ].to_numpy(),
    marker="o",
    linewidth=1.8,
    label="Kaplan–Meier",
)

ax.plot(
    horizon_days,
    t7_compare[
        "weibull_aft_ipcw_brier"
    ].to_numpy(),
    marker="o",
    linewidth=1.8,
    label="Weibull AFT",
)

ax.plot(
    horizon_days,
    t7_compare[
        "lognormal_aft_ipcw_brier"
    ].to_numpy(),
    marker="o",
    linewidth=1.8,
    label="Log-Normal AFT",
)

ax.set_xlabel(
    "Evaluation horizon (days)"
)
ax.set_ylabel(
    "IPCW Brier score"
)
ax.set_title(
    "T7 Survival Prediction IPCW Brier Evidence"
)
ax.legend()
ax.grid(alpha=0.25)

savefig(
    fig,
    "t9_t7_survival_ipcw_brier.png",
)


# ============================================================
# 6. T7 C-INDEX
# ============================================================

print("[6/6] T7 C-index")

# These are already-established native T7 evaluation values.
# This section only visualizes them.
cindex_models = [
    "Weibull AFT",
    "Log-Normal AFT",
]

cindex_values = [
    0.554962,
    0.556875,
]

fig, ax = plt.subplots(figsize=(8, 5))

ax.bar(
    cindex_models,
    cindex_values,
)

ax.set_ylabel(
    "Harrell concordance index"
)
ax.set_title(
    "T7 Native Survival Discrimination"
)
ax.grid(
    axis="y",
    alpha=0.25,
)

savefig(
    fig,
    "t9_t7_c_index.png",
)


# ============================================================
# FINAL MANIFEST
# ============================================================

manifest = {
    "status": "PASS",
    "purpose": (
        "T9 read-only presentation visualization"
    ),
    "semantic_boundary_changed": False,
    "new_model_fitting": False,
    "new_prediction_generation": False,
    "new_probability_generation": False,
    "new_calibration_fitting": False,
    "target_modification": False,
    "threshold_selection": False,
    "model_selection": False,
    "cross_task_probability_aggregation": False,
    "universal_confidence_score_created": False,
    "universal_risk_score_created": False,
    "plots": [
        "t9_t5_reliability_diagram.png",
        "t9_t5_calibration_metrics.png",
        "t9_t4_native_ranking.png",
        "t9_t6_native_retrieval_bootstrap.png",
        "t9_t7_survival_ipcw_brier.png",
        "t9_t7_c_index.png",
    ],
    "interpretation": (
        "Plots are descriptive visualizations of already-established "
        "task-specific T9 evidence. They do not alter the empirical "
        "confidence/calibration boundary."
    ),
}

manifest_path = (
    PLOTS_ROOT
    / "t9_mod037_final_visualization_manifest.json"
)

with open(
    manifest_path,
    "w",
    encoding="utf-8",
) as f:
    json.dump(
        manifest,
        f,
        indent=2,
    )


print()
print("=" * 72)
print("T9 MOD-037 FINAL VISUALIZATION RESULT")
print("=" * 72)
print("Result: PASS")
print(f"Plots directory: {PLOTS_ROOT}")
print(f"Manifest: {manifest_path}")
print()
print("Created plots:")
for name in manifest["plots"]:
    print(f"  - {name}")
print()
print("T9 semantic boundary changed: NO")
print("New modeling: NO")
print("New calibration: NO")
print("Universal confidence/risk: NO")
print("Cross-task aggregation: NO")
print()
print("FINAL VISUALIZATION PASS COMPLETE")