
from pathlib import Path
import json
import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score

ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

EVIDENCE = (
    ROOT / "modeling/T8/mod033/"
    / "t8_mod033_op007_t4_t5_development_evidence.csv"
)

T4_EVAL = ROOT / "modeling/T4/derived/t4_eval.csv"
T5_VAL = ROOT / "modeling/T5/splits/t5_model_val.csv"

OUT = ROOT / "modeling/T8/mod034/"
OUT.mkdir(parents=True, exist_ok=True)

OUTPUT = OUT / "t8_mod034_op006_robust_stratification.json"

df = pd.read_csv(EVIDENCE)
t4 = pd.read_csv(T4_EVAL)[["ID", "target_assignee"]]
t5 = pd.read_csv(T5_VAL)[["ID", "T5 target"]]

df = df.merge(t4, on="ID", validate="one_to_one")
df = df.merge(t5, on="ID", validate="one_to_one")

if len(df) != 4716:
    raise RuntimeError("Unexpected population.")

# Conservative, sufficiently populated T5 bands.
df["t5_band"] = pd.cut(
    df["t5_p_duplicate"],
    bins=[-np.inf, 0.01, 0.05, 0.10, np.inf],
    labels=["<=0.01", "0.01-0.05", "0.05-0.10", ">0.10"],
    include_lowest=True,
)

t4_results = []

for band, g in df.groupby("t5_band", observed=False):
    t4_results.append({
        "t5_band": str(band),
        "n": int(len(g)),
        "t4_top1": float(np.mean([
            str(r["target_assignee"]) == str(r["t4_rank_1_assignee"])
            for _, r in g.iterrows()
        ])),
        "t4_top5": float(np.mean([
            any(
                str(r["target_assignee"]) ==
                str(r[f"t4_rank_{k}_assignee"])
                for k in range(1, 6)
            )
            for _, r in g.iterrows()
        ])),
        "t4_top20": float(np.mean([
            any(
                str(r["target_assignee"]) ==
                str(r[f"t4_rank_{k}_assignee"])
                for k in range(1, 21)
            )
            for _, r in g.iterrows()
        ])),
    })

# Conservative T4 quartiles, then T5 discrimination.
df["t4_quartile"] = pd.qcut(
    df["t4_rank_1_score"].rank(method="first"),
    q=4,
    labels=["Q1", "Q2", "Q3", "Q4"],
)

t5_results = []

for band, g in df.groupby("t4_quartile", observed=False):
    y = g["T5 target"].astype(int).to_numpy()
    p = g["t5_p_duplicate"].astype(float).to_numpy()

    t5_results.append({
        "t4_quartile": str(band),
        "n": int(len(g)),
        "positives": int(y.sum()),
        "positive_rate": float(y.mean()),
        "roc_auc": (
            float(roc_auc_score(y, p))
            if len(np.unique(y)) == 2 else None
        ),
        "average_precision": (
            float(average_precision_score(y, p))
            if y.sum() > 0 else None
        ),
    })

# Robustness comparison uses only the two largest T5 regions.
large_t5 = df[df["t5_p_duplicate"] <= 0.05].copy()

robust_low = large_t5[
    large_t5["t5_p_duplicate"] <= 0.01
]
robust_mid = large_t5[
    (large_t5["t5_p_duplicate"] > 0.01)
    & (large_t5["t5_p_duplicate"] <= 0.05)
]

result = {
    "operation": "MOD-034 / OP-006",
    "status": "PASS",
    "population": len(df),
    "t4_performance_by_conservative_t5_band": t4_results,
    "t5_performance_by_t4_quartile": t5_results,
    "robust_large_band_comparison": {
        "low_band_n": len(robust_low),
        "mid_band_n": len(robust_mid),
        "low_band_t4_top1": float(np.mean([
            str(r["target_assignee"]) ==
            str(r["t4_rank_1_assignee"])
            for _, r in robust_low.iterrows()
        ])),
        "mid_band_t4_top1": float(np.mean([
            str(r["target_assignee"]) ==
            str(r["t4_rank_1_assignee"])
            for _, r in robust_mid.iterrows()
        ])),
    },
    "constraints": {
        "sparse_upper_tail_used_for_primary_comparison": False,
        "synthetic_target": False,
        "fusion_score": False,
        "causal_claim": False,
    },
    "decision": "ROBUST_STRATIFICATION_CHECK_COMPLETE",
}

OUTPUT.write_text(json.dumps(result, indent=2))

print("=" * 80)
print("MOD-034 OP-006 — ROBUST STRATIFICATION CHECK")
print("=" * 80)

print("\nT4 PERFORMANCE BY CONSERVATIVE T5 BANDS")
for r in t4_results:
    print(
        f"{r['t5_band']:>10} | n={r['n']:4d} | "
        f"Top1={r['t4_top1']:.4f} | "
        f"Top5={r['t4_top5']:.4f} | "
        f"Top20={r['t4_top20']:.4f}"
    )

print("\nT5 PERFORMANCE BY T4 QUARTILE")
for r in t5_results:
    auc = "NA" if r["roc_auc"] is None else f"{r['roc_auc']:.4f}"
    print(
        f"{r['t4_quartile']} | n={r['n']:4d} | "
        f"positives={r['positives']:2d} | "
        f"AUC={auc}"
    )

print("\nLARGE-BAND T4 TOP-1 COMPARISON")
print(f"<=0.01:    n={len(robust_low):4d} | "
      f"{result['robust_large_band_comparison']['low_band_t4_top1']:.4f}")
print(f"0.01-0.05: n={len(robust_mid):4d} | "
      f"{result['robust_large_band_comparison']['mid_band_t4_top1']:.4f}")

print("\nDECISION: ROBUST_STRATIFICATION_CHECK_COMPLETE")
print(f"Artifact: {OUTPUT}")
print("=" * 80)
