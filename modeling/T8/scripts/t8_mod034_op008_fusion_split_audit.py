from pathlib import Path
import json
import pandas as pd

ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

SRC = ROOT / "modeling/T8/mod033/t8_mod033_op007_t4_t5_development_evidence.csv"
T4 = ROOT / "modeling/T4/derived/t4_eval.csv"
T5 = ROOT / "modeling/T5/splits/t5_model_val.csv"
OUT = ROOT / "modeling/T8/mod034/t8_mod034_op008_fusion_split_audit.json"

df = pd.read_csv(SRC)
t4 = pd.read_csv(T4)
t5 = pd.read_csv(T5)

required_evidence = [
    "ID",
    "t4_rank_1_assignee",
    "t4_rank_1_score",
    "t5_p_duplicate",
]

for c in required_evidence:
    if c not in df.columns:
        raise RuntimeError(f"Missing evidence column: {c}")

for c in ["ID", "target_assignee"]:
    if c not in t4.columns:
        raise RuntimeError(f"Missing T4 column: {c}")

for c in ["ID", "T5 target"]:
    if c not in t5.columns:
        raise RuntimeError(f"Missing T5 column: {c}")

if len(df) != 4716:
    raise RuntimeError(f"Unexpected evidence population: {len(df)}")

if df["ID"].duplicated().any():
    raise RuntimeError("Duplicate IDs in evidence artifact")

# Recover native outcomes using the same ID key.
t4_outcome = t4[["ID", "target_assignee"]].drop_duplicates("ID")
t5_outcome = t5[["ID", "T5 target"]].drop_duplicates("ID")

merged = (
    df.merge(t4_outcome, on="ID", how="inner", validate="one_to_one")
      .merge(t5_outcome, on="ID", how="inner", validate="one_to_one")
)

if len(merged) != len(df):
    raise RuntimeError(
        f"Outcome join changed population: evidence={len(df)}, joined={len(merged)}"
    )

# Deterministic ticket-level split.
ordered = merged.sort_values("ID", kind="mergesort").reset_index(drop=True)

cut = int(len(ordered) * 0.75)

dev = ordered.iloc[:cut].copy()
eval_df = ordered.iloc[cut:].copy()

dev_ids = set(dev["ID"])
eval_ids = set(eval_df["ID"])

overlap = dev_ids & eval_ids

checks = {
    "population_4716": len(merged) == 4716,
    "unique_ticket_ids": not merged["ID"].duplicated().any(),
    "zero_id_overlap": len(overlap) == 0,
    "t5_positive_in_development": int((dev["T5 target"] == 1).sum()) > 0,
    "t5_positive_in_evaluation": int((eval_df["T5 target"] == 1).sum()) > 0,
    "t4_classes_in_development": dev["target_assignee"].nunique() > 1,
    "t4_classes_in_evaluation": eval_df["target_assignee"].nunique() > 1,
    "native_outcomes_joined": True,
}

result = {
    "operation": "MOD-034 / OP-008",
    "status": "PASS" if all(checks.values()) else "FAIL",
    "source_evidence_rows": len(df),
    "joined_rows": len(merged),
    "development_rows": len(dev),
    "evaluation_rows": len(eval_df),
    "id_overlap": len(overlap),
    "development_t5_positive": int((dev["T5 target"] == 1).sum()),
    "development_t5_negative": int((dev["T5 target"] == 0).sum()),
    "evaluation_t5_positive": int((eval_df["T5 target"] == 1).sum()),
    "evaluation_t5_negative": int((eval_df["T5 target"] == 0).sum()),
    "development_t4_unique_assignees": int(dev["target_assignee"].nunique()),
    "evaluation_t4_unique_assignees": int(eval_df["target_assignee"].nunique()),
    "checks": checks,
    "design": {
        "development": "first 75% after deterministic ID ordering",
        "evaluation": "remaining 25%",
        "native_outcomes": [
            "T4 target_assignee",
            "T5 target",
        ],
        "locked_evaluation_used": False,
        "synthetic_target_created": False,
    },
}

OUT.write_text(json.dumps(result, indent=2))

print("=" * 80)
print("MOD-034 OP-008 — CONTROLLED FUSION SPLIT AUDIT")
print("=" * 80)
print(f"Evidence population: {len(df)}")
print(f"Joined population:   {len(merged)}")
print(f"Development:         {len(dev)}")
print(f"Evaluation:          {len(eval_df)}")
print(f"ID overlap:          {len(overlap)}")
print(f"T5 dev positives:    {result['development_t5_positive']}")
print(f"T5 eval positives:   {result['evaluation_t5_positive']}")
print(f"T4 dev classes:      {result['development_t4_unique_assignees']}")
print(f"T4 eval classes:     {result['evaluation_t4_unique_assignees']}")
print()
print(f"STATUS: {result['status']}")
print(f"Artifact: {OUT}")
print("=" * 80)