
from pathlib import Path
import json

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    log_loss,
    roc_auc_score,
)


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

EVIDENCE = (
    ROOT
    / "modeling/T8/mod033/"
    / "t8_mod033_op007_t4_t5_development_evidence.csv"
)

T4_EVAL = ROOT / "modeling/T4/derived/t4_eval.csv"
T5_VAL = ROOT / "modeling/T5/splits/t5_model_val.csv"

OUT_DIR = ROOT / "modeling/T8/mod034"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = OUT_DIR / "t8_mod034_op004_native_evidence_addition.json"


df = pd.read_csv(EVIDENCE)
t4 = pd.read_csv(T4_EVAL)
t5 = pd.read_csv(T5_VAL)

if len(df) != 4716 or df["ID"].nunique() != 4716:
    raise RuntimeError("Unexpected common development population.")

# ---------------------------------------------------------------
# Attach native outcomes
# ---------------------------------------------------------------

t4_targets = t4[["ID", "target_assignee"]].copy()
t5_targets = t5[["ID", "T5 target"]].copy()

if t4_targets["ID"].duplicated().any():
    raise RuntimeError("Duplicate T4 IDs.")

if t5_targets["ID"].duplicated().any():
    raise RuntimeError("Duplicate T5 IDs.")

df = df.merge(t4_targets, on="ID", how="left", validate="one_to_one")
df = df.merge(t5_targets, on="ID", how="left", validate="one_to_one")

if df["target_assignee"].isna().any():
    raise RuntimeError("Missing T4 native outcomes.")

if df["T5 target"].isna().any():
    raise RuntimeError("Missing T5 native outcomes.")


# ---------------------------------------------------------------
# T4 native baseline
#
# The native T4 artifact provides ranked candidate assignees.
# Evaluate whether the native top-k ranking contains the observed
# target assignee.
# ---------------------------------------------------------------

def topk_hit_rate(frame, k):
    col = f"t4_rank_{k}_assignee"
    return float(
        frame.apply(
            lambda r: str(r["target_assignee"]) == str(r[col]),
            axis=1,
        ).mean()
    )


t4_baseline = {
    "top1_hit_rate": topk_hit_rate(df, 1),
    "top3_hit_rate": float(
        np.mean([
            any(
                str(r["target_assignee"]) == str(
                    r[f"t4_rank_{k}_assignee"]
                )
                for k in range(1, 4)
            )
            for _, r in df.iterrows()
        ])
    ),
    "top5_hit_rate": float(
        np.mean([
            any(
                str(r["target_assignee"]) == str(
                    r[f"t4_rank_{k}_assignee"]
                )
                for k in range(1, 6)
            )
            for _, r in df.iterrows()
        ])
    ),
    "top10_hit_rate": float(
        np.mean([
            any(
                str(r["target_assignee"]) == str(
                    r[f"t4_rank_{k}_assignee"]
                )
                for k in range(1, 11)
            )
            for _, r in df.iterrows()
        ])
    ),
    "top20_hit_rate": float(
        np.mean([
            any(
                str(r["target_assignee"]) == str(
                    r[f"t4_rank_{k}_assignee"]
                )
                for k in range(1, 21)
            )
            for _, r in df.iterrows()
        ])
    ),
}


# ---------------------------------------------------------------
# T4 evidence conditioned on T5 evidence
#
# T5 is NOT used to alter the T4 ranking.
# We only characterize native T4 performance within T5 strata.
# ---------------------------------------------------------------

df["t5_band"] = pd.cut(
    df["t5_p_duplicate"],
    bins=[-np.inf, 0.01, 0.05, 0.10, 0.25, 0.50, np.inf],
    labels=[
        "<=0.01",
        "0.01-0.05",
        "0.05-0.10",
        "0.10-0.25",
        "0.25-0.50",
        ">0.50",
    ],
    include_lowest=True,
)

t4_by_t5 = []

for band, g in df.groupby("t5_band", observed=False):
    if len(g) == 0:
        continue

    t4_by_t5.append({
        "t5_band": str(band),
        "n": int(len(g)),
        "t4_top1_hit_rate": topk_hit_rate(g, 1),
        "t4_top5_hit_rate": float(
            np.mean([
                any(
                    str(r["target_assignee"]) == str(
                        r[f"t4_rank_{k}_assignee"]
                    )
                    for k in range(1, 6)
                )
                for _, r in g.iterrows()
            ])
        ),
        "t4_top20_hit_rate": float(
            np.mean([
                any(
                    str(r["target_assignee"]) == str(
                        r[f"t4_rank_{k}_assignee"]
                    )
                    for k in range(1, 21)
                )
                for _, r in g.iterrows()
            ])
        ),
    })


# ---------------------------------------------------------------
# T5 native baseline
# ---------------------------------------------------------------

y = df["T5 target"].astype(int).to_numpy()
p = df["t5_p_duplicate"].astype(float).to_numpy()

t5_baseline = {
    "positive_count": int(y.sum()),
    "negative_count": int((y == 0).sum()),
    "positive_rate": float(y.mean()),
    "roc_auc": float(roc_auc_score(y, p)),
    "average_precision": float(average_precision_score(y, p)),
    "log_loss": float(log_loss(y, p, labels=[0, 1])),
}


# ---------------------------------------------------------------
# T5 evidence conditioned on T4 evidence
#
# T4 is NOT converted into probability.
# We only characterize native T5 discrimination within T4 strata.
# ---------------------------------------------------------------

df["t4_band"] = pd.qcut(
    df["t4_rank_1_score"].rank(method="first"),
    q=4,
    labels=["Q1", "Q2", "Q3", "Q4"],
)

t5_by_t4 = []

for band, g in df.groupby("t4_band", observed=False):
    if len(g) == 0:
        continue

    yg = g["T5 target"].astype(int).to_numpy()
    pg = g["t5_p_duplicate"].astype(float).to_numpy()

    # AUC/AP are undefined when a stratum contains one class.
    if len(np.unique(yg)) == 2:
        auc = float(roc_auc_score(yg, pg))
        ap = float(average_precision_score(yg, pg))
    else:
        auc = None
        ap = None

    t5_by_t4.append({
        "t4_score_quartile": str(band),
        "n": int(len(g)),
        "positive_count": int(yg.sum()),
        "roc_auc": auc,
        "average_precision": ap,
        "mean_p_duplicate": float(pg.mean()),
    })


# ---------------------------------------------------------------
# Native evidence interaction table
# ---------------------------------------------------------------

interaction = (
    df.groupby(
        ["t4_band", "t5_band"],
        observed=False,
    )
    .agg(
        n=("ID", "size"),
        t5_positive=("T5 target", "sum"),
        mean_t4_score=("t4_rank_1_score", "mean"),
        mean_t5_probability=("t5_p_duplicate", "mean"),
    )
    .reset_index()
)

interaction["n"] = interaction["n"].astype(int)
interaction["t5_positive"] = interaction["t5_positive"].astype(int)


# ---------------------------------------------------------------
# Interpretation
# ---------------------------------------------------------------

result = {
    "operation": "MOD-034 / OP-004",
    "status": "PASS",

    "population": {
        "rows": int(len(df)),
        "unique_ids": int(df["ID"].nunique()),
    },

    "t4_native_baseline": t4_baseline,
    "t4_native_performance_by_t5_evidence": t4_by_t5,

    "t5_native_baseline": t5_baseline,
    "t5_native_performance_by_t4_evidence": t5_by_t4,

    "native_interaction_table": interaction.to_dict(
        orient="records"
    ),

    "constraints": {
        "t4_ranking_preserved": True,
        "t4_ranking_to_probability": False,
        "t5_probability_preserved": True,
        "t5_probability_to_assignment": False,
        "synthetic_joint_target": False,
        "arbitrary_weighting": False,
        "causal_claim": False,
    },

    "decision": (
        "NATIVE_EVIDENCE_ADDITION_CHARACTERIZED; "
        "NO_SYNTHETIC_FUSION_SCORE_CREATED"
    ),
}


with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)


print("=" * 80)
print("MOD-034 OP-004 COMPLETE")
print("=" * 80)

print(f"Population: {len(df)}")

print("\nT4 NATIVE BASELINE")
for k, v in t4_baseline.items():
    print(f"{k}: {v:.6f}")

print("\nT5 NATIVE BASELINE")
print(f"positive_count: {t5_baseline['positive_count']}")
print(f"negative_count: {t5_baseline['negative_count']}")
print(f"positive_rate: {t5_baseline['positive_rate']:.6f}")
print(f"ROC-AUC: {t5_baseline['roc_auc']:.6f}")
print(f"Average precision: {t5_baseline['average_precision']:.6f}")
print(f"Log loss: {t5_baseline['log_loss']:.6f}")

print("\nConstraints preserved:")
print("T4 ranking preserved: YES")
print("T4 ranking -> probability: NO")
print("T5 probability preserved: YES")
print("T5 probability -> assignment: NO")
print("Synthetic joint target: NO")
print("Arbitrary weighting: NO")
print("Causal claim: NO")

print("\nDECISION:")
print("NATIVE_EVIDENCE_ADDITION_CHARACTERIZED")
print(f"Artifact: {OUTPUT}")

print("=" * 80)
