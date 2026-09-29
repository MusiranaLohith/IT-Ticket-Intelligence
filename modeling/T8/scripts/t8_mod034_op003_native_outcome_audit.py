from pathlib import Path
import json

import pandas as pd
import numpy as np


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T4_EVAL = ROOT / "modeling/T4/derived/t4_eval.csv"
T5_VAL = ROOT / "modeling/T5/splits/t5_model_val.csv"

EVIDENCE = (
    ROOT
    / "modeling/T8/mod033/"
    / "t8_mod033_op007_t4_t5_development_evidence.csv"
)

OUT_DIR = ROOT / "modeling/T8/mod034"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = OUT_DIR / "t8_mod034_op003_native_outcome_audit.json"


t4 = pd.read_csv(T4_EVAL)
t5 = pd.read_csv(T5_VAL)
evidence = pd.read_csv(EVIDENCE)

print("=" * 80)
print("T8 MOD-034 — OP-003: NATIVE OUTCOME / EVALUATION TARGET AUDIT")
print("=" * 80)


# ------------------------------------------------------------------
# 1. Common population
# ------------------------------------------------------------------

common_ids = set(evidence["ID"])

t4_common = t4[t4["ID"].isin(common_ids)].copy()
t5_common = t5[t5["ID"].isin(common_ids)].copy()

if len(t4_common) != 4716:
    raise RuntimeError(f"Unexpected T4 common population: {len(t4_common)}")

if len(t5_common) != 4716:
    raise RuntimeError(f"Unexpected T5 common population: {len(t5_common)}")


# ------------------------------------------------------------------
# 2. Discover likely native outcome columns
# ------------------------------------------------------------------

def candidate_columns(df):
    keywords = [
        "target",
        "label",
        "duplicate",
        "assignee",
        "y_",
        "class",
    ]

    return [
        c for c in df.columns
        if any(k in c.lower() for k in keywords)
    ]


t4_candidates = candidate_columns(t4_common)
t5_candidates = candidate_columns(t5_common)

print(f"T4 candidate outcome columns: {t4_candidates}")
print(f"T5 candidate outcome columns: {t5_candidates}")


# ------------------------------------------------------------------
# 3. Native T4 outcome
# ------------------------------------------------------------------

if "target_assignee" not in t4_common.columns:
    raise RuntimeError("T4 native target_assignee not found.")

t4_target = t4_common["target_assignee"]

t4_outcome = {
    "column": "target_assignee",
    "non_null": int(t4_target.notna().sum()),
    "unique_values": int(t4_target.nunique()),
    "missing": int(t4_target.isna().sum()),
    "semantics": "observed target assignee",
    "evaluation_type": "native assignee-ranking outcome",
}


# ------------------------------------------------------------------
# 4. Discover T5 native target
# ------------------------------------------------------------------

t5_target_candidates = [
    c for c in t5_common.columns
    if c == "T5 target"
]

print(f"T5 target candidates: {t5_target_candidates}")

t5_target_summary = {}

for col in t5_target_candidates:
    s = t5_common[col]

    if pd.api.types.is_numeric_dtype(s):
        values = sorted(pd.Series(s.dropna().unique()).tolist())

        if len(values) <= 10:
            t5_target_summary[col] = {
                "non_null": int(s.notna().sum()),
                "missing": int(s.isna().sum()),
                "unique_values": int(s.nunique()),
                "values": values,
            }


# ------------------------------------------------------------------
# 5. Identify binary native duplicate target
# ------------------------------------------------------------------

native_duplicate_target = None

for col, info in t5_target_summary.items():
    if set(info["values"]).issubset({0, 1}):
        if col == "T5 target":
            native_duplicate_target = col
            break


if native_duplicate_target is None:
    raise RuntimeError(
        "Could not identify a native binary duplicate target in T5 validation."
    )


s = t5_common[native_duplicate_target]

t5_outcome = {
    "column": native_duplicate_target,
    "non_null": int(s.notna().sum()),
    "missing": int(s.isna().sum()),
    "unique_values": int(s.nunique()),
    "values": sorted(s.dropna().unique().tolist()),
    "positive_count": int((s == 1).sum()),
    "negative_count": int((s == 0).sum()),
    "semantics": "native frozen duplicate target",
    "evaluation_type": "native duplicate-probability outcome",
}


# ------------------------------------------------------------------
# 6. Check whether a joint universal target exists
# ------------------------------------------------------------------

joint_target_candidates = [
    c for c in evidence.columns
    if any(
        x in c.lower()
        for x in ["triage", "priority", "decision", "risk", "outcome"]
    )
]

# The evidence artifact itself should not contain a synthetic joint target.
synthetic_joint_target_present = len(joint_target_candidates) > 0


# ------------------------------------------------------------------
# 7. Verify native outcomes are independently defined
# ------------------------------------------------------------------

independent_native_outcomes = (
    t4_outcome["column"] == "target_assignee"
    and t5_outcome["column"] == native_duplicate_target
    and t4_outcome["semantics"] != t5_outcome["semantics"]
)


# ------------------------------------------------------------------
# 8. Determine defensible evaluation directions
# ------------------------------------------------------------------

evaluation_directions = {
    "evaluate_T4_against_native_assignee_target": True,
    "evaluate_T5_against_native_duplicate_target": True,

    # These would require an invented common target.
    "evaluate_single_joint_triage_target": False,
    "evaluate_universal_triage_accuracy": False,
    "evaluate_universal_triage_f1": False,
    "evaluate_joint_probability": False,
}


# ------------------------------------------------------------------
# 9. Final decision
# ------------------------------------------------------------------

decision = (
    "NATIVE_TASK_SPECIFIC_EVALUATION_TARGETS_AVAILABLE"
    if (
        independent_native_outcomes
        and not synthetic_joint_target_present
    )
    else "BLOCK"
)


result = {
    "operation": "MOD-034 / OP-003",
    "status": "PASS" if decision != "BLOCK" else "FAIL",

    "population": {
        "common_ids": int(len(common_ids)),
        "t4_rows": int(len(t4_common)),
        "t5_rows": int(len(t5_common)),
    },

    "t4_native_outcome": t4_outcome,
    "t5_native_outcome": t5_outcome,

    "t5_target_candidates": t5_target_summary,

    "joint_target_check": {
        "candidate_joint_columns": joint_target_candidates,
        "synthetic_joint_target_present": synthetic_joint_target_present,
    },

    "independent_native_outcomes": independent_native_outcomes,

    "evaluation_directions": evaluation_directions,

    "decision": decision,
}


with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)


print()
print("T4 native outcome:")
print(
    f"  {t4_outcome['column']} | "
    f"unique={t4_outcome['unique_values']} | "
    f"missing={t4_outcome['missing']}"
)

print("T5 native outcome:")
print(
    f"  {t5_outcome['column']} | "
    f"positive={t5_outcome['positive_count']} | "
    f"negative={t5_outcome['negative_count']}"
)

print()
print(f"Independent native outcomes: {independent_native_outcomes}")
print(f"Synthetic joint target present: {synthetic_joint_target_present}")
print()
print(f"DECISION: {decision}")
print(f"Artifact: {OUTPUT}")

print("=" * 80)