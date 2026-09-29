from pathlib import Path
import json
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    log_loss,
)


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

SRC = ROOT / "modeling/T8/mod033/t8_mod033_op007_t4_t5_development_evidence.csv"
T5 = ROOT / "modeling/T5/splits/t5_model_val.csv"
OUT = ROOT / "modeling/T8/mod034/t8_mod034_op012_t5_controlled_ablation.json"


# ------------------------------------------------------------
# Load native T5 outcome
# ------------------------------------------------------------

df = pd.read_csv(SRC)
t5 = pd.read_csv(T5)

t5_outcome = t5[["ID", "T5 target"]].drop_duplicates("ID")

df = df.merge(
    t5_outcome,
    on="ID",
    how="inner",
    validate="one_to_one",
)

if len(df) != 4716:
    raise RuntimeError(f"Expected 4716 rows, got {len(df)}")


# ------------------------------------------------------------
# Reproduce OP-008 deterministic split
# ------------------------------------------------------------

df = df.sort_values("ID", kind="mergesort").reset_index(drop=True)

cut = int(len(df) * 0.75)

dev = df.iloc[:cut].copy()
eval_df = df.iloc[cut:].copy()


# ------------------------------------------------------------
# Native T5 baseline
# ------------------------------------------------------------

y_dev = dev["T5 target"].to_numpy(dtype=int)
y_eval = eval_df["T5 target"].to_numpy(dtype=int)

p_eval_native = eval_df["t5_p_duplicate"].to_numpy(dtype=float)

native_auc = roc_auc_score(y_eval, p_eval_native)
native_ap = average_precision_score(y_eval, p_eval_native)
native_logloss = log_loss(
    y_eval,
    np.clip(p_eval_native, 1e-7, 1 - 1e-7),
)


# ------------------------------------------------------------
# Native T4 ticket-level evidence descriptors
# ------------------------------------------------------------

score_cols = [
    f"t4_rank_{i}_score"
    for i in range(1, 21)
]

def make_features(frame):
    scores = frame[score_cols]

    return pd.DataFrame({
        "t4_top1_score": frame["t4_rank_1_score"],
        "t4_top5_mean": scores.iloc[:, :5].mean(axis=1),
        "t4_top20_mean": scores.mean(axis=1),
        "t4_top20_max": scores.max(axis=1),
        "t4_top20_min": scores.min(axis=1),
        "t4_top20_score_std": scores.std(axis=1),
    })


X_dev_t4 = make_features(dev)
X_eval_t4 = make_features(eval_df)


# ------------------------------------------------------------
# Scale T4 evidence using development statistics only.
# This is feature normalization, not arbitrary evidence weighting.
# ------------------------------------------------------------

means = X_dev_t4.mean()
stds = X_dev_t4.std().replace(0, 1)

X_dev_t4 = (X_dev_t4 - means) / stds
X_eval_t4 = (X_eval_t4 - means) / stds


# ------------------------------------------------------------
# T5-only learned control
# ------------------------------------------------------------

X_dev_t5 = dev[["t5_p_duplicate"]].to_numpy(dtype=float)
X_eval_t5 = eval_df[["t5_p_duplicate"]].to_numpy(dtype=float)

model_t5 = LogisticRegression(
    max_iter=1000,
    solver="lbfgs",
    class_weight="balanced",
    random_state=42,
)

model_t5.fit(X_dev_t5, y_dev)

p_eval_t5 = model_t5.predict_proba(X_eval_t5)[:, 1]


# ------------------------------------------------------------
# T5 + native T4 evidence
# ------------------------------------------------------------

X_dev_fused = np.column_stack([
    X_dev_t5,
    X_dev_t4.to_numpy(dtype=float),
])

X_eval_fused = np.column_stack([
    X_eval_t5,
    X_eval_t4.to_numpy(dtype=float),
])

model_fused = LogisticRegression(
    max_iter=1000,
    solver="lbfgs",
    class_weight="balanced",
    random_state=42,
)

model_fused.fit(X_dev_fused, y_dev)

p_eval_fused = model_fused.predict_proba(X_eval_fused)[:, 1]


# ------------------------------------------------------------
# Metrics
# ------------------------------------------------------------

t5_auc = roc_auc_score(y_eval, p_eval_t5)
t5_ap = average_precision_score(y_eval, p_eval_t5)
t5_logloss = log_loss(
    y_eval,
    np.clip(p_eval_t5, 1e-7, 1 - 1e-7),
)

fused_auc = roc_auc_score(y_eval, p_eval_fused)
fused_ap = average_precision_score(y_eval, p_eval_fused)
fused_logloss = log_loss(
    y_eval,
    np.clip(p_eval_fused, 1e-7, 1 - 1e-7),
)


# ------------------------------------------------------------
# Result
# ------------------------------------------------------------

result = {
    "operation": "MOD-034 / OP-012",
    "status": "PASS",

    "population": {
        "development": len(dev),
        "held_out_evaluation": len(eval_df),
        "development_positive": int(y_dev.sum()),
        "evaluation_positive": int(y_eval.sum()),
    },

    "native_t5": {
        "roc_auc": native_auc,
        "average_precision": native_ap,
        "log_loss": native_logloss,
    },

    "t5_only_learned": {
        "roc_auc": t5_auc,
        "average_precision": t5_ap,
        "log_loss": t5_logloss,
    },

    "t5_plus_t4_evidence": {
        "roc_auc": fused_auc,
        "average_precision": fused_ap,
        "log_loss": fused_logloss,
    },

    "delta_fused_vs_t5_only": {
        "roc_auc": fused_auc - t5_auc,
        "average_precision": fused_ap - t5_ap,
        "log_loss": fused_logloss - t5_logloss,
    },

    "added_t4_evidence": [
        "t4_top1_score",
        "t4_top5_mean",
        "t4_top20_mean",
        "t4_top20_max",
        "t4_top20_min",
        "t4_top20_score_std",
    ],

    "controls": {
        "synthetic_target": False,
        "arbitrary_manual_weighting": False,
        "t4_probability_conversion": False,
        "locked_evaluation_used_for_training": False,
        "development_statistics_used_for_scaling": True,
    },

    "interpretation_rule": (
        "Results concern native T5 duplicate prediction only. "
        "They do not establish a universal triage fusion benefit."
    ),
}


OUT.write_text(json.dumps(result, indent=2))


print("=" * 80)
print("MOD-034 OP-012 — T5-SIDE CONTROLLED ABLATION")
print("=" * 80)

print(f"Development rows:       {len(dev)}")
print(f"Held-out evaluation:    {len(eval_df)}")
print(f"Development positives:  {int(y_dev.sum())}")
print(f"Evaluation positives:   {int(y_eval.sum())}")

print()

print("Native T5:")
print(f"  ROC-AUC:       {native_auc:.6f}")
print(f"  AP:            {native_ap:.6f}")
print(f"  Log Loss:      {native_logloss:.6f}")

print()

print("T5-only learned:")
print(f"  ROC-AUC:       {t5_auc:.6f}")
print(f"  AP:            {t5_ap:.6f}")
print(f"  Log Loss:      {t5_logloss:.6f}")

print()

print("T5 + T4 evidence:")
print(f"  ROC-AUC:       {fused_auc:.6f}")
print(f"  AP:            {fused_ap:.6f}")
print(f"  Log Loss:      {fused_logloss:.6f}")

print()

print("Delta (T5 + T4) - (T5-only):")
print(f"  ROC-AUC:       {fused_auc - t5_auc:+.6f}")
print(f"  AP:            {fused_ap - t5_ap:+.6f}")
print(f"  Log Loss:      {fused_logloss - t5_logloss:+.6f}")

print()
print("STATUS: PASS")
print(f"Artifact: {OUT}")
print("=" * 80)