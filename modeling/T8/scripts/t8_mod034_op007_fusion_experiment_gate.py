from pathlib import Path
import json

ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

OP001 = ROOT / "modeling/T8/mod034/t8_mod034_op001_fusion_contract_audit.json"
OP003 = ROOT / "modeling/T8/mod034/t8_mod034_op003_native_outcome_audit.json"
OP006 = ROOT / "modeling/T8/mod034/t8_mod034_op006_robust_stratification.json"

OUT = ROOT / "modeling/T8/mod034/t8_mod034_op007_fusion_experiment_gate.json"

op1 = json.loads(OP001.read_text())
op3 = json.loads(OP003.read_text())
op6 = json.loads(OP006.read_text())

checks = {
    "fusion_contract_pass": op1["status"] == "PASS",
    "native_outcomes_available": op3["status"] == "PASS",
    "robust_interaction_pass": op6["status"] == "PASS",
    "synthetic_joint_target": False,
    "arbitrary_weighting": False,
    "t4_probability_conversion": False,
    "t5_assignment_conversion": False,
}

# A controlled experiment is justified only as an
# evidence-addition/ablation analysis against each native task outcome.
positive_checks = [
    checks["fusion_contract_pass"],
    checks["native_outcomes_available"],
    checks["robust_interaction_pass"],
]

prohibition_checks = [
    not checks["synthetic_joint_target"],
    not checks["arbitrary_weighting"],
    not checks["t4_probability_conversion"],
    not checks["t5_assignment_conversion"],
]

decision = (
    "PROCEED_WITH_CONTROLLED_NATIVE_EVIDENCE_ADDITION_EXPERIMENT"
    if all(positive_checks) and all(prohibition_checks)
    else "BLOCK"
)

result = {
    "operation": "MOD-034 / OP-007",
    "status": "PASS" if decision != "BLOCK" else "FAIL",
    "checks": checks,
    "allowed_experiment": {
        "t4_task": {
            "target": "target_assignee",
            "baseline": "native T4 ranking",
            "addition": "T5 native p_duplicate evidence",
            "evaluation": "native T4 ranking metrics",
        },
        "t5_task": {
            "target": "T5 target",
            "baseline": "native T5 p_duplicate",
            "addition": "T4 native ranking evidence",
            "evaluation": "native T5 discrimination metrics",
        },
    },
    "prohibited": [
        "synthetic universal triage target",
        "single fused probability",
        "arbitrary weighted score",
        "T4 ranking to probability conversion",
        "T5 probability to assignment conversion",
        "causal interpretation",
    ],
    "decision": decision,
}

OUT.write_text(json.dumps(result, indent=2))

print("=" * 80)
print("MOD-034 OP-007 — FUSION EXPERIMENT GATE")
print("=" * 80)

for name, value in checks.items():
    print(f"{name}: {value}")

print()
print(f"DECISION: {decision}")
print(f"Artifact: {OUT}")
print("=" * 80)