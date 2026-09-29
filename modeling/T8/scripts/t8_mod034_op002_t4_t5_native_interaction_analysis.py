from pathlib import Path
import json

import numpy as np
import pandas as pd


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

EVIDENCE = (
    ROOT
    / "modeling/T8/mod033/"
    / "t8_mod033_op007_t4_t5_development_evidence.csv"
)

OUT_DIR = ROOT / "modeling/T8/mod034"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = OUT_DIR / "t8_mod034_op002_native_interaction_analysis.json"


df = pd.read_csv(EVIDENCE)

print("=" * 80)
print("T8 MOD-034 — OP-002: T4/T5 NATIVE EVIDENCE INTERACTION ANALYSIS")
print("=" * 80)


# ------------------------------------------------------------------
# 1. Basic population validation
# ------------------------------------------------------------------

if len(df) != 4716:
    raise RuntimeError(f"Unexpected population size: {len(df)}")

if df["ID"].nunique() != len(df):
    raise RuntimeError("Duplicate ticket IDs detected.")

p = df["t5_p_duplicate"]

if not (
    np.isfinite(p).all()
    and (p >= 0).all()
    and (p <= 1).all()
):
    raise RuntimeError("Invalid T5 probability values detected.")


# ------------------------------------------------------------------
# 2. Native T4 evidence characterization
# ------------------------------------------------------------------

rank1_score = df["t4_rank_1_score"]

top1_assignee_count = df["t4_rank_1_assignee"].nunique()

rank_score_summary = {
    "min": float(rank1_score.min()),
    "median": float(rank1_score.median()),
    "mean": float(rank1_score.mean()),
    "max": float(rank1_score.max()),
}


# ------------------------------------------------------------------
# 3. Native T5 evidence characterization
# ------------------------------------------------------------------

p_summary = {
    "min": float(p.min()),
    "q25": float(p.quantile(0.25)),
    "median": float(p.median()),
    "q75": float(p.quantile(0.75)),
    "mean": float(p.mean()),
    "max": float(p.max()),
}


# ------------------------------------------------------------------
# 4. T5 probability bands
# ------------------------------------------------------------------

p_band = pd.cut(
    p,
    bins=[-np.inf, 0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 1.0],
    labels=[
        "<=0.01",
        "0.01-0.05",
        "0.05-0.10",
        "0.10-0.25",
        "0.25-0.50",
        "0.50-0.75",
        "0.75-1.00",
    ],
    include_lowest=True,
)

t5_bands = (
    df.assign(t5_probability_band=p_band)
    .groupby("t5_probability_band", observed=False)
    .agg(
        n=("ID", "size"),
        t4_rank1_score_median=("t4_rank_1_score", "median"),
        t4_rank1_score_mean=("t4_rank_1_score", "mean"),
    )
    .reset_index()
)

t5_bands["n"] = t5_bands["n"].astype(int)


# ------------------------------------------------------------------
# 5. T4 ranking-score bands
# ------------------------------------------------------------------

t4_score_band = pd.qcut(
    rank1_score.rank(method="first"),
    q=4,
    labels=["Q1", "Q2", "Q3", "Q4"],
)

t4_bands = (
    df.assign(t4_rank1_score_band=t4_score_band)
    .groupby("t4_rank1_score_band", observed=False)
    .agg(
        n=("ID", "size"),
        t5_p_duplicate_median=("t5_p_duplicate", "median"),
        t5_p_duplicate_mean=("t5_p_duplicate", "mean"),
    )
    .reset_index()
)

t4_bands["n"] = t4_bands["n"].astype(int)


# ------------------------------------------------------------------
# 6. Rank position concentration
# ------------------------------------------------------------------

rank_positions = []

for k in range(1, 21):
    col = f"t4_rank_{k}_assignee"
    rank_positions.append(
        {
            "rank": k,
            "unique_assignees": int(df[col].nunique()),
            "non_null": int(df[col].notna().sum()),
        }
    )


# ------------------------------------------------------------------
# 7. Native evidence association
# ------------------------------------------------------------------

spearman = df[
    ["t4_rank_1_score", "t5_p_duplicate"]
].corr(method="spearman").iloc[0, 1]

pearson = df[
    ["t4_rank_1_score", "t5_p_duplicate"]
].corr(method="pearson").iloc[0, 1]


# ------------------------------------------------------------------
# 8. High/low evidence interaction table
# ------------------------------------------------------------------

t4_median = rank1_score.median()
t5_median = p.median()

interaction = (
    df.assign(
        t4_evidence_level=np.where(
            df["t4_rank_1_score"] >= t4_median,
            "higher_or_equal",
            "lower",
        ),
        t5_evidence_level=np.where(
            df["t5_p_duplicate"] >= t5_median,
            "higher_or_equal",
            "lower",
        ),
    )
    .groupby(
        ["t4_evidence_level", "t5_evidence_level"],
        observed=False,
    )
    .agg(
        n=("ID", "size"),
        mean_t4_score=("t4_rank_1_score", "mean"),
        mean_t5_probability=("t5_p_duplicate", "mean"),
    )
    .reset_index()
)

interaction["n"] = interaction["n"].astype(int)


# ------------------------------------------------------------------
# 9. Native top-k score spread
# ------------------------------------------------------------------

score_spread = {}

for k in [1, 3, 5, 10, 20]:
    score_col = f"t4_rank_{k}_score"

    score_spread[str(k)] = {
        "median": float(df[score_col].median()),
        "mean": float(df[score_col].mean()),
    }


# ------------------------------------------------------------------
# 10. Decision framing
# ------------------------------------------------------------------

result = {
    "operation": "MOD-034 / OP-002",
    "status": "PASS",

    "population": {
        "rows": int(len(df)),
        "unique_ids": int(df["ID"].nunique()),
    },

    "t4_native_characterization": {
        "top1_unique_assignees": top1_assignee_count,
        "rank1_score": rank_score_summary,
        "rank_score_spread": score_spread,
    },

    "t5_native_characterization": {
        "p_duplicate": p_summary,
    },

    "t5_probability_bands": t5_bands.to_dict(orient="records"),
    "t4_score_quartiles": t4_bands.to_dict(orient="records"),
    "rank_position_characterization": rank_positions,

    "native_association": {
        "spearman_t4_rank1_score_vs_t5_probability": float(spearman),
        "pearson_t4_rank1_score_vs_t5_probability": float(pearson),
    },

    "median_interaction_table": interaction.to_dict(orient="records"),

    "interpretation_constraints": {
        "causal_claim": False,
        "fusion_performance_claim": False,
        "synthetic_triage_target": False,
        "t4_ranking_to_probability": False,
        "t5_probability_to_assignment": False,
        "arbitrary_weighting": False,
    },

    "decision": (
        "NATIVE_EVIDENCE_INTERACTION_CHARACTERIZED; "
        "NO_FUSION_PERFORMANCE_CLAIM"
    ),
}


with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)


print(f"Population: {len(df)}")
print(f"T4 rank-1 unique assignees: {top1_assignee_count}")
print(
    "T4 rank-1 score: "
    f"median={rank_score_summary['median']:.6f}, "
    f"mean={rank_score_summary['mean']:.6f}"
)
print(
    "T5 p_duplicate: "
    f"median={p_summary['median']:.6f}, "
    f"mean={p_summary['mean']:.6f}"
)
print(
    "Spearman(T4 rank-1 score, T5 p_duplicate): "
    f"{spearman:.6f}"
)
print(
    "Pearson(T4 rank-1 score, T5 p_duplicate): "
    f"{pearson:.6f}"
)

print()
print("No causal claim: YES")
print("No fusion-performance claim: YES")
print("Synthetic T8 target: NO")
print()
print("DECISION: NATIVE_EVIDENCE_INTERACTION_CHARACTERIZED")
print(f"Artifact: {OUTPUT}")
print("=" * 80)