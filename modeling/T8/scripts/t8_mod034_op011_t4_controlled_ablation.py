from pathlib import Path
import json
import numpy as np
import pandas as pd

from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

SRC = ROOT / "modeling/T8/mod033/t8_mod033_op007_t4_t5_development_evidence.csv"
T4 = ROOT / "modeling/T4/derived/t4_eval.csv"
OUT = ROOT / "modeling/T8/mod034/t8_mod034_op011_t4_controlled_ablation.json"


# ------------------------------------------------------------
# Load common development evidence + native T4 outcome
# ------------------------------------------------------------

df = pd.read_csv(SRC)
t4 = pd.read_csv(T4)

t4_outcome = t4[["ID", "target_assignee"]].drop_duplicates("ID")

df = df.merge(
    t4_outcome,
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
# Baseline: native T4 rank-1
# ------------------------------------------------------------

baseline_top1 = (
    eval_df["t4_rank_1_assignee"].to_numpy()
    == eval_df["target_assignee"].to_numpy()
)

baseline_top1_acc = float(baseline_top1.mean())


# ------------------------------------------------------------
# Native T4 candidate space
# ------------------------------------------------------------

candidate_assignees = sorted(
    dev["t4_rank_1_assignee"].dropna().unique()
)

candidate_set = set(candidate_assignees)

train = dev[
    dev["target_assignee"].isin(candidate_set)
].copy()

test = eval_df[
    eval_df["target_assignee"].isin(candidate_set)
].copy()

if len(train) == 0 or len(test) == 0:
    raise RuntimeError("Empty controlled candidate population")


# ------------------------------------------------------------
# Encode native T4 target
# ------------------------------------------------------------

encoder = LabelEncoder()
encoder.fit(candidate_assignees)

y_train = encoder.transform(train["target_assignee"])
y_test = encoder.transform(test["target_assignee"])


# ------------------------------------------------------------
# Native T4 evidence
# ------------------------------------------------------------

t4_score_cols = [
    "t4_rank_1_score",
    "t4_rank_2_score",
    "t4_rank_3_score",
    "t4_rank_4_score",
    "t4_rank_5_score",
]

rank1_codes = {
    value: i
    for i, value in enumerate(candidate_assignees)
}


# ------------------------------------------------------------
# T4-only features
# ------------------------------------------------------------

X_train_t4 = np.column_stack([
    train[t4_score_cols].to_numpy(dtype=float),
    train["t4_rank_1_assignee"]
        .map(rank1_codes)
        .to_numpy(dtype=float),
])

X_test_t4 = np.column_stack([
    test[t4_score_cols].to_numpy(dtype=float),
    test["t4_rank_1_assignee"]
        .map(rank1_codes)
        .to_numpy(dtype=float),
])


# ------------------------------------------------------------
# T4-only learned control
# ------------------------------------------------------------

model_t4 = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
    solver="lbfgs",
    random_state=42,
)

model_t4.fit(X_train_t4, y_train)

pred_t4 = model_t4.predict(X_test_t4)

t4_only_acc = float(
    accuracy_score(y_test, pred_t4)
)


# ------------------------------------------------------------
# T4 + native T5 evidence
# ------------------------------------------------------------

X_train_fused = np.column_stack([
    train[t4_score_cols].to_numpy(dtype=float),
    train["t4_rank_1_assignee"]
        .map(rank1_codes)
        .to_numpy(dtype=float),
    train["t5_p_duplicate"].to_numpy(dtype=float),
])

X_test_fused = np.column_stack([
    test[t4_score_cols].to_numpy(dtype=float),
    test["t4_rank_1_assignee"]
        .map(rank1_codes)
        .to_numpy(dtype=float),
    test["t5_p_duplicate"].to_numpy(dtype=float),
])


# ------------------------------------------------------------
# T4 + T5 learned ablation
# ------------------------------------------------------------

model_fused = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
    solver="lbfgs",
    random_state=42,
)

model_fused.fit(X_train_fused, y_train)

pred_fused = model_fused.predict(X_test_fused)

fused_acc = float(
    accuracy_score(y_test, pred_fused)
)


# ------------------------------------------------------------
# Result
# ------------------------------------------------------------

result = {
    "operation": "MOD-034 / OP-011",
    "status": "PASS",

    "population": {
        "development": len(dev),
        "held_out_evaluation": len(eval_df),
        "candidate_development_rows": len(train),
        "candidate_evaluation_rows": len(test),
        "candidate_assignees": len(candidate_assignees),
    },

    "baseline": {
        "native_t4_rank1_accuracy": baseline_top1_acc,
    },

    "controlled_ablation": {
        "t4_only_learned_accuracy": t4_only_acc,
        "t4_plus_t5_learned_accuracy": fused_acc,
        "delta_t4_plus_t5_vs_t4_only": (
            fused_acc - t4_only_acc
        ),
    },

    "features": {
        "native_t4_scores": t4_score_cols,
        "native_t4_rank1_assignee": True,
        "native_t5_evidence": "t5_p_duplicate",
    },

    "controls": {
        "synthetic_target": False,
        "arbitrary_weighting": False,
        "t4_probability_conversion": False,
        "t5_assignment_conversion": False,
        "locked_evaluation_used": False,
        "held_out_evaluation_used_for_training": False,
    },

    "interpretation_rule": (
        "Any improvement is interpreted only as evidence concerning "
        "T5 evidence addition to the native T4 target. It is not a "
        "universal triage improvement claim."
    ),
}


OUT.write_text(
    json.dumps(result, indent=2)
)


# ------------------------------------------------------------
# Small terminal output
# ------------------------------------------------------------

print("=" * 80)
print("MOD-034 OP-011 — T4-SIDE CONTROLLED ABLATION")
print("=" * 80)

print(f"Development rows:       {len(dev)}")
print(f"Held-out evaluation:    {len(eval_df)}")
print(f"Candidate assignees:    {len(candidate_assignees)}")
print(f"Candidate eval rows:    {len(test)}")

print()

print(f"Native T4 rank-1:       {baseline_top1_acc:.6f}")
print(f"T4-only learned:        {t4_only_acc:.6f}")
print(f"T4 + T5 learned:        {fused_acc:.6f}")
print(
    f"T5 evidence delta:      "
    f"{fused_acc - t4_only_acc:+.6f}"
)

print()

print("STATUS: PASS")
print(f"Artifact: {OUT}")
print("=" * 80)