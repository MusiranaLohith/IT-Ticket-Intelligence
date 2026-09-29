from pathlib import Path
import json
import pandas as pd
import numpy as np


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

EVIDENCE = (
    ROOT
    / "modeling/T8/mod033/"
    / "t8_mod033_op007_t4_t5_development_evidence.csv"
)

OUT_DIR = ROOT / "modeling/T8/mod034"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = OUT_DIR / "t8_mod034_op001_fusion_contract_audit.json"


df = pd.read_csv(EVIDENCE)

print("=" * 80)
print("T8 MOD-034 — OP-001: T4/T5 FUSION DECISION-CONTRACT AUDIT")
print("=" * 80)


# ------------------------------------------------------------------
# 1. Evidence population
# ------------------------------------------------------------------

required = {
    "ID",
    "t5_p_duplicate",
    "t4_source_population",
    "t5_source_population",
    "t4_prediction_boundary",
    "t5_prediction_boundary",
    "t4_implementation",
    "t5_implementation",
    "t4_rank_1_assignee",
    "t4_rank_1_score",
}

missing = sorted(required - set(df.columns))

if missing:
    raise RuntimeError(f"Missing required evidence columns: {missing}")


# ------------------------------------------------------------------
# 2. Native task semantics
# ------------------------------------------------------------------

t4_semantics = {
    "task": "assignee ranking / retrieval",
    "output_type": "ranked candidate assignees with native retrieval scores",
    "target_semantics": "observed target assignee",
    "boundary": "Creation",
}

t5_semantics = {
    "task": "duplicate detection",
    "output_type": "calibrated duplicate probability",
    "target_semantics": "frozen duplicate target",
    "probability_field": "p_duplicate",
    "boundary": "Creation",
}


# ------------------------------------------------------------------
# 3. Check whether a universal T8 target exists
# ------------------------------------------------------------------

synthetic_universal_target = False

# No universal triage label is present in the evidence artifact.
universal_triage_target_present = False


# ------------------------------------------------------------------
# 4. Check whether native evidence can be directly combined
# ------------------------------------------------------------------

direct_probability_fusion_supported = False
t4_to_probability_conversion_allowed = False
t5_to_assignment_conversion_allowed = False
arbitrary_weighting_allowed = False


# ------------------------------------------------------------------
# 5. Identify defensible investigation types
# ------------------------------------------------------------------

defensible_analyses = {
    "conditional_error_analysis": True,
    "evidence_stratification": True,
    "cross_task_association": True,
    "native_task_specific_evaluation": True,

    # These require transformations that are not part of the contract.
    "single_fused_probability": False,
    "synthetic_triage_score": False,
    "arbitrary_weighted_combination": False,
    "t4_ranking_to_probability": False,
    "t5_probability_to_assignment": False,
}


# ------------------------------------------------------------------
# 6. Population integrity
# ------------------------------------------------------------------

population_checks = {
    "rows": int(len(df)),
    "unique_ids": int(df["ID"].nunique()),
    "duplicate_ids": int(df["ID"].duplicated().sum()),
    "t5_probability_min": float(df["t5_p_duplicate"].min()),
    "t5_probability_max": float(df["t5_p_duplicate"].max()),
    "t5_probability_valid": bool(
        np.isfinite(df["t5_p_duplicate"]).all()
        and (df["t5_p_duplicate"] >= 0).all()
        and (df["t5_p_duplicate"] <= 1).all()
    ),
}


# ------------------------------------------------------------------
# 7. Decision
# ------------------------------------------------------------------

decision = (
    "PROCEED_WITH_NATIVE_EVIDENCE_INTERACTION_ANALYSIS"
    if (
        population_checks["duplicate_ids"] == 0
        and population_checks["t5_probability_valid"]
        and not synthetic_universal_target
        and not universal_triage_target_present
    )
    else "BLOCK"
)


result = {
    "operation": "MOD-034 / OP-001",
    "status": "PASS" if decision != "BLOCK" else "FAIL",

    "population": population_checks,

    "native_task_semantics": {
        "t4": t4_semantics,
        "t5": t5_semantics,
    },

    "fusion_constraints": {
        "synthetic_universal_target": synthetic_universal_target,
        "universal_triage_target_present": universal_triage_target_present,
        "direct_probability_fusion_supported": direct_probability_fusion_supported,
        "t4_to_probability_conversion_allowed": t4_to_probability_conversion_allowed,
        "t5_to_assignment_conversion_allowed": t5_to_assignment_conversion_allowed,
        "arbitrary_weighting_allowed": arbitrary_weighting_allowed,
    },

    "defensible_analyses": defensible_analyses,

    "decision": decision,
}


with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)


print(f"Evidence rows: {len(df)}")
print(f"Unique IDs: {df['ID'].nunique()}")
print(f"T5 probability valid: {population_checks['t5_probability_valid']}")
print()
print("T4 native semantics: ASSIGNEE RANKING")
print("T5 native semantics: DUPLICATE PROBABILITY")
print("Universal synthetic triage target: NO")
print("Arbitrary probability fusion: NO")
print("T4 ranking → probability: NO")
print("T5 probability → assignment: NO")
print()
print(f"DECISION: {decision}")
print(f"Artifact: {OUTPUT}")
print("=" * 80)