from pathlib import Path
import json

ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
MOD = ROOT / "modeling/T8/mod034"

artifacts = {
    "op001_contract": MOD / "t8_mod034_op001_fusion_contract_audit.json",
    "op002_interaction": MOD / "t8_mod034_op002_native_interaction_analysis.json",
    "op003_outcome": MOD / "t8_mod034_op003_native_outcome_audit.json",
    "op004_native_addition": MOD / "t8_mod034_op004_native_evidence_addition.json",
    "op006_robustness": MOD / "t8_mod034_op006_robust_stratification.json",
    "op007_gate": MOD / "t8_mod034_op007_fusion_experiment_gate.json",
    "op008_split": MOD / "t8_mod034_op008_fusion_split_audit.json",
    "op009_design": MOD / "t8_mod034_op009_fusion_mechanism_audit.json",
    "op010_t4_feasibility": MOD / "t8_mod034_op010_t4_ablation_feasibility.json",
    "op012_t5_ablation": MOD / "t8_mod034_op012_t5_controlled_ablation.json",
}

missing = [name for name, path in artifacts.items() if not path.exists()]

if missing:
    raise RuntimeError(f"Missing MOD-034 artifacts: {missing}")

loaded = {
    name: json.loads(path.read_text())
    for name, path in artifacts.items()
}

# Required completed operations.
required_pass = [
    "op001_contract",
    "op002_interaction",
    "op003_outcome",
    "op004_native_addition",
    "op006_robustness",
    "op007_gate",
    "op008_split",
    "op009_design",
    "op010_t4_feasibility",
    "op012_t5_ablation",
]

failed = [
    name
    for name in required_pass
    if loaded[name].get("status") != "PASS"
]

if failed:
    raise RuntimeError(f"Required artifacts not PASS: {failed}")

t5 = loaded["op012_t5_ablation"]

closure = {
    "operation": "MOD-034 / OP-013",
    "status": "PASS",

    "scope": "T4/T5 native evidence fusion investigation",

    "t4_side": {
        "finding": (
            "T5 p_duplicate is constant across all 20 T4 candidates "
            "within each ticket; therefore it cannot change native "
            "T4 candidate ordering."
        ),
        "candidate_recall_top20": 0.360475,
        "decision": "NO_VALID_T4_RERANKING_FUSION_ESTABLISHED",
    },

    "t5_side": {
        "native_roc_auc": t5["native_t5"]["roc_auc"],
        "native_average_precision": t5["native_t5"]["average_precision"],
        "native_log_loss": t5["native_t5"]["log_loss"],

        "fused_roc_auc": t5["t5_plus_t4_evidence"]["roc_auc"],
        "fused_average_precision": t5["t5_plus_t4_evidence"]["average_precision"],
        "fused_log_loss": t5["t5_plus_t4_evidence"]["log_loss"],

        "roc_auc_delta": t5["delta_fused_vs_t5_only"]["roc_auc"],
        "average_precision_delta": t5["delta_fused_vs_t5_only"]["average_precision"],
        "log_loss_delta": t5["delta_fused_vs_t5_only"]["log_loss"],

        "decision": (
            "MIXED_RESULT_NO_ROBUST_FUSION_BENEFIT_ESTABLISHED"
        ),
    },

    "overall_conclusion": (
        "T4/T5 evidence interaction is observable, but the investigation "
        "does not establish a robust native decision-fusion benefit. "
        "T4-side candidate reranking is structurally unsupported by the "
        "ticket-level T5 evidence representation. T5-side evidence "
        "addition produces mixed evaluation behavior and therefore does "
        "not justify claiming general fusion improvement."
    ),

    "contract_controls": {
        "synthetic_universal_target": False,
        "direct_probability_fusion": False,
        "arbitrary_weighting": False,
        "ranking_to_probability_conversion": False,
        "probability_to_assignment_conversion": False,
        "causal_interpretation": False,
        "locked_evaluation_used_for_training": False,
    },

    "mod034_decision": "CLOSED_NO_ROBUST_FUSION_BENEFIT",
}

OUT = MOD / "t8_mod034_op013_fusion_closure.json"
OUT.write_text(json.dumps(closure, indent=2))

print("=" * 80)
print("MOD-034 OP-013 — FUSION INVESTIGATION CLOSURE")
print("=" * 80)

print("T4-side:")
print("  Native T5 evidence can NOT rerank T4 candidates.")
print("  T4 Top-20 candidate recall:", closure["t4_side"]["candidate_recall_top20"])

print()
print("T5-side:")
print(f"  Native ROC-AUC: {closure['t5_side']['native_roc_auc']:.6f}")
print(f"  Fused ROC-AUC:  {closure['t5_side']['fused_roc_auc']:.6f}")
print(f"  ROC-AUC delta:  {closure['t5_side']['roc_auc_delta']:+.6f}")
print(f"  AP delta:       {closure['t5_side']['average_precision_delta']:+.6f}")
print(f"  Log-loss delta: {closure['t5_side']['log_loss_delta']:+.6f}")

print()
print("OVERALL:")
print("  Evidence interaction: OBSERVED")
print("  Robust fusion benefit: NOT ESTABLISHED")
print("  MOD-034: CLOSED")
print()
print("STATUS: PASS")
print(f"Artifact: {OUT}")
print("=" * 80)