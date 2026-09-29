from pathlib import Path
import json

ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

OP008 = ROOT / "modeling/T8/mod034/t8_mod034_op008_fusion_split_audit.json"
OUT = ROOT / "modeling/T8/mod034/t8_mod034_op009_fusion_mechanism_audit.json"

op8 = json.loads(OP008.read_text())

if op8["status"] != "PASS":
    raise RuntimeError("OP-008 must PASS before OP-009")

result = {
    "operation": "MOD-034 / OP-009",
    "status": "PASS",

    "design_principle": (
        "Evaluate evidence addition against each native task outcome "
        "without constructing a universal triage target."
    ),

    "t4_experiment": {
        "native_target": "target_assignee",
        "baseline": {
            "evidence": [
                "t4_rank_1_assignee",
                "t4_rank_1_score",
                "t4_rank_2_assignee",
                "t4_rank_2_score",
                "t4_rank_3_assignee",
                "t4_rank_3_score",
                "t4_rank_4_assignee",
                "t4_rank_4_score",
                "t4_rank_5_assignee",
                "t4_rank_5_score",
            ],
            "decision": "native T4 top-k ranking",
        },
        "added_evidence": [
            "t5_p_duplicate"
        ],
        "permitted_question": (
            "Can native T5 duplicate evidence improve the T4 "
            "native assignee decision when evaluated against target_assignee?"
        ),
        "prohibited": [
            "convert t5_p_duplicate into an assignee probability",
            "multiply or add T4 scores by t5_p_duplicate",
            "arbitrary weighting",
            "synthetic triage label",
        ],
        "evaluation": [
            "Top-1 accuracy",
            "Top-5 accuracy",
            "Top-20 accuracy",
        ],
    },

    "t5_experiment": {
        "native_target": "T5 target",
        "baseline": {
            "evidence": [
                "t5_p_duplicate"
            ],
            "decision": "native duplicate probability",
        },
        "added_evidence": [
            "t4_rank_1_score",
            "t4_rank_2_score",
            "t4_rank_3_score",
            "t4_rank_4_score",
            "t4_rank_5_score",
        ],
        "permitted_question": (
            "Can native T4 retrieval evidence improve the T5 native "
            "duplicate decision when evaluated against T5 target?"
        ),
        "prohibited": [
            "convert T4 ranking into duplicate probability",
            "arbitrary score weighting",
            "synthetic triage label",
        ],
        "evaluation": [
            "ROC-AUC",
            "Average Precision",
            "Log Loss",
        ],
    },

    "development_evaluation_boundary": {
        "development_rows": 3537,
        "held_out_evaluation_rows": 1179,
        "development_used_for_mechanism_selection": True,
        "evaluation_used_only_after_selection": True,
    },

    "stability_warning": {
        "t5_development_positive_count": 14,
        "statement": (
            "T5 development positive count is small; any learned "
            "T5-side evidence-addition mechanism may be unstable "
            "and must be interpreted conservatively."
        ),
    },

    "decision": "DESIGN_ACCEPTED_FOR_CONTROLLED_ABLATION"
}

OUT.write_text(json.dumps(result, indent=2))

print("=" * 80)
print("MOD-034 OP-009 — CONTROLLED FUSION MECHANISM AUDIT")
print("=" * 80)
print("T4 native target: target_assignee")
print("T4 added evidence: t5_p_duplicate")
print("T5 native target: T5 target")
print("T5 added evidence: T4 native ranking evidence")
print("Development: 3537")
print("Held-out evaluation: 1179")
print("T5 development positives: 14")
print()
print("STATUS: PASS")
print("DECISION: DESIGN_ACCEPTED_FOR_CONTROLLED_ABLATION")
print(f"Artifact: {OUT}")
print("=" * 80)