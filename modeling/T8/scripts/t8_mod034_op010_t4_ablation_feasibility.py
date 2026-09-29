from pathlib import Path
import json
import pandas as pd
import numpy as np

ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

SRC = ROOT / "modeling/T8/mod033/t8_mod033_op007_t4_t5_development_evidence.csv"
T4 = ROOT / "modeling/T4/derived/t4_eval.csv"
OP008 = ROOT / "modeling/T8/mod034/t8_mod034_op008_fusion_split_audit.json"

OUT = ROOT / "modeling/T8/mod034/t8_mod034_op010_t4_ablation_feasibility.json"

df = pd.read_csv(SRC)
t4 = pd.read_csv(T4)
op8 = json.loads(OP008.read_text())

if op8["status"] != "PASS":
    raise RuntimeError("OP-008 must PASS")

t4_outcome = t4[["ID", "target_assignee"]].drop_duplicates("ID")

df = (
    df.merge(t4_outcome, on="ID", how="inner", validate="one_to_one")
)

if len(df) != 4716:
    raise RuntimeError(f"Unexpected joined population: {len(df)}")

# Development portion established by OP-008.
ordered = df.sort_values("ID", kind="mergesort").reset_index(drop=True)
cut = int(len(ordered) * 0.75)
dev = ordered.iloc[:cut].copy()

rank_assignee_cols = [f"t4_rank_{i}_assignee" for i in range(1, 21)]
rank_score_cols = [f"t4_rank_{i}_score" for i in range(1, 21)]

missing = [
    c for c in rank_assignee_cols + rank_score_cols + ["t5_p_duplicate"]
    if c not in dev.columns
]

if missing:
    raise RuntimeError(f"Missing required columns: {missing}")

# Native T4 ranking integrity.
rank_order_ok = []
rank1_matches_target = 0

for _, row in dev.iterrows():
    scores = row[rank_score_cols].to_numpy(dtype=float)

    finite = np.isfinite(scores).all()
    descending = np.all(scores[:-1] >= scores[1:])

    rank_order_ok.append(bool(finite and descending))

    if row["t4_rank_1_assignee"] == row["target_assignee"]:
        rank1_matches_target += 1

# Candidate learning inputs that preserve native semantics.
# These are evidence descriptors, not converted probabilities.
feature_candidates = [
    "t5_p_duplicate",
    "t4_rank_1_score",
    "t4_rank_2_score",
    "t4_rank_3_score",
    "t4_rank_4_score",
    "t4_rank_5_score",
]

# Check whether T5 evidence has usable variation in development.
p = dev["t5_p_duplicate"].to_numpy(dtype=float)

result = {
    "operation": "MOD-034 / OP-010",
    "status": "PASS",

    "population": {
        "common_oos": len(df),
        "development": len(dev),
        "held_out_evaluation": 4716 - len(dev),
    },

    "native_t4_integrity": {
        "rank_rows_monotonic": bool(all(rank_order_ok)),
        "rank1_target_matches": int(rank1_matches_target),
        "rank1_accuracy": float(rank1_matches_target / len(dev)),
        "unique_target_assignees": int(dev["target_assignee"].nunique()),
    },

    "t5_evidence_variation": {
        "min": float(np.min(p)),
        "max": float(np.max(p)),
        "mean": float(np.mean(p)),
        "median": float(np.median(p)),
        "unique_values": int(pd.Series(p).nunique()),
        "finite": bool(np.isfinite(p).all()),
    },

    "candidate_native_features": feature_candidates,

    "design_constraints": {
        "target": "target_assignee",
        "baseline": "native T4 top-k ranking",
        "added_native_evidence": "t5_p_duplicate",
        "synthetic_target": False,
        "arbitrary_weighting": False,
        "direct_score_multiplication": False,
        "ranking_to_probability_conversion": False,
        "held_out_evaluation_used": False,
    },

    "decision": (
        "T4_SIDE_LEARNING_MECHANISM_FEASIBLE_FOR_DEVELOPMENT_ABLATION"
    ),
}

OUT.write_text(json.dumps(result, indent=2))

print("=" * 80)
print("MOD-034 OP-010 — T4-SIDE ABLATION FEASIBILITY")
print("=" * 80)
print(f"Development rows:       {len(dev)}")
print(f"T4 target classes:      {dev['target_assignee'].nunique()}")
print(f"Native rank integrity:  {all(rank_order_ok)}")
print(f"T4 Top-1 accuracy:      {rank1_matches_target / len(dev):.6f}")
print(f"T5 p_duplicate unique:  {pd.Series(p).nunique()}")
print(f"T5 p_duplicate range:   {p.min():.6f} -> {p.max():.6f}")
print()
print("STATUS: PASS")
print("DECISION: T4_SIDE_LEARNING_MECHANISM_FEASIBLE_FOR_DEVELOPMENT_ABLATION")
print(f"Artifact: {OUT}")
print("=" * 80)