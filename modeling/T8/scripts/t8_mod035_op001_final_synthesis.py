from pathlib import Path
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T8 = ROOT / "modeling/T8"

OUT = T8 / "t8_mod035_op001_final_synthesis.json"


# ------------------------------------------------------------
# Load completed evidence
# ------------------------------------------------------------

artifacts = {
    "t2t7_fusion_closure": T8 / "mod032",
    "t4t5_fusion_closure":
        T8 / "mod034/t8_mod034_op013_fusion_closure.json",
}


required = [
    artifacts["t4t5_fusion_closure"],
]

missing = [str(p) for p in required if not p.exists()]

if missing:
    raise RuntimeError(
        "Missing required synthesis artifact(s): "
        + ", ".join(missing)
    )


t4t5 = json.loads(
    artifacts["t4t5_fusion_closure"].read_text()
)


# ------------------------------------------------------------
# Final T8 synthesis
# ------------------------------------------------------------

synthesis = {
    "operation": "T8 / MOD-035 / OP-001",
    "status": "PASS",

    "research_question": (
        "Whether combining validated cross-task evidence improves "
        "final triage decision support compared with isolated task signals."
    ),

    "decision_unit": {
        "primary": "canonical Mozilla ticket",
        "population": 513816,
        "prediction_boundary": "Creation",
    },

    "evidence_layers": {
        "layer_A": [
            "T2",
            "T3",
            "T4",
            "T5",
            "T7",
        ],
        "layer_B": [
            "T6 query-level",
        ],
        "layer_C": [
            "T6 query-candidate",
        ],
    },

    "t2_t7": {
        "native_evidence": "OoF chronological evidence generated",
        "fusion_investigation": (
            "Controlled T2+T7 fusion showed evidence interaction, "
            "but chronological robustness did not establish a "
            "consistent fusion benefit."
        ),
        "decision": "NO_ROBUST_FUSION_BENEFIT_ESTABLISHED",
    },

    "t4_t5": {
        "native_evidence": "Development OOS evidence available",
        "t4_side": t4t5["t4_side"],
        "t5_side": t4t5["t5_side"],
        "decision": t4t5["mod034_decision"],
    },

    "cross_task_findings": [
        (
            "Cross-task evidence interaction is observable."
        ),
        (
            "Observable interaction does not by itself establish "
            "decision-fusion benefit."
        ),
        (
            "T4-side fusion is structurally constrained because "
            "T5 p_duplicate is ticket-level and constant across "
            "T4 candidates."
        ),
        (
            "T5-side addition of native T4 ticket-level retrieval "
            "evidence produced mixed evaluation behavior rather "
            "than consistent improvement."
        ),
        (
            "T2/T7 fusion likewise did not establish robust "
            "chronologically stable improvement."
        ),
    ],

    "final_conclusion": (
        "Under the frozen T8 contract, the completed evidence does "
        "not establish a robust general benefit from cross-task "
        "decision fusion. Cross-task evidence can interact and "
        "provide task-specific contextual information, but the "
        "available evidence does not justify replacing isolated "
        "native task outputs with a universal fused triage score, "
        "probability, ranking, or decision."
    ),

    "system_role": (
        "T8 is therefore retained as an evidence-fusion investigation "
        "and decision-intelligence layer, not as a demonstrated "
        "universal triage fusion model."
    ),

    "contract_compliance": {
        "synthetic_universal_target": False,
        "universal_triage_score": False,
        "arbitrary_weighting": False,
        "direct_probability_fusion": False,
        "t4_ranking_to_probability": False,
        "t5_probability_to_assignment": False,
        "post_creation_information": False,
        "causal_claim": False,
        "locked_evaluation_leakage": False,
    },

    "completed_modules": {
        "MOD-032_T2_T7": "CLOSED",
        "MOD-033_T4_T5_DEVELOPMENT_EVIDENCE": "CLOSED",
        "MOD-034_T4_T5_FUSION": "CLOSED",
    },

    "t8_status": "SYNTHESIS_COMPLETE",
}


OUT.write_text(
    json.dumps(synthesis, indent=2)
)


print("=" * 80)
print("T8 FINAL SYNTHESIS — MOD-035 OP-001")
print("=" * 80)

print("Research question:")
print(
    "  Cross-task evidence does not establish robust general "
    "decision-fusion benefit."
)

print()
print("T2/T7:")
print("  No robust chronological fusion benefit established.")

print()
print("T4/T5:")
print("  Evidence interaction observed.")
print("  T4-side candidate fusion structurally unsupported.")
print("  T5-side fusion produced mixed evaluation behavior.")

print()
print("Final decision:")
print("  NO_ROBUST_GENERAL_CROSS_TASK_FUSION_BENEFIT_ESTABLISHED")

print()
print("T8 status: SYNTHESIS_COMPLETE")
print(f"Artifact: {OUT}")
print("=" * 80)