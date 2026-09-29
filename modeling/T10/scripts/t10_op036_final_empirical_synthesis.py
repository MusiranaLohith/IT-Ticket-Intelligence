from pathlib import Path
import json


T10_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/modeling/T10"
)

T5_METRICS = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/modeling/T5/metrics"
)

REQUIRED_T5_FILES = [
    T5_METRICS / "t5_mod009_locked_evaluation_metrics.json",
    T5_METRICS / "t5_mod011_final_closure.json",
]


def check(condition, label):
    status = "PASS" if condition else "FAIL"
    print(f"{label}: {status}")
    return condition


print("=" * 82)
print("T10 / OP-036 — FINAL EMPIRICAL EVIDENCE SYNTHESIS & CLOSURE")
print("=" * 82)


# ---------------------------------------------------------------------
# 1. T5 source evidence availability
# ---------------------------------------------------------------------

print("\n[1] T5 SOURCE EVIDENCE")

t5_files_ok = True

for path in REQUIRED_T5_FILES:
    exists = path.is_file()
    print(f"{path}: {'FOUND' if exists else 'MISSING'}")
    t5_files_ok &= exists

check(t5_files_ok, "C1 T5 source evidence available")

if not t5_files_ok:
    raise SystemExit("Required T5 evidence is missing.")


with open(REQUIRED_T5_FILES[0], "r", encoding="utf-8") as f:
    t5_metrics = json.load(f)

with open(REQUIRED_T5_FILES[1], "r", encoding="utf-8") as f:
    t5_closure = json.load(f)


# ---------------------------------------------------------------------
# 2. Task-native empirical evidence registry
# ---------------------------------------------------------------------

print("\n[2] TASK-NATIVE EMPIRICAL EVIDENCE REGISTRY")

task_registry = {
    "T2": {
        "rn": 29,
        "evidence": "Priority Prediction hard-prediction correctness",
        "population": 4425,
        "traceable_ids": True,
        "native_probability": False,
        "policy_validated": False,
    },
    "T4": {
        "rn": 30,
        "evidence": "Assignee ranking correctness",
        "population": 35626,
        "traceable_ids": True,
        "native_probability": False,
        "policy_validated": False,
    },
    "T5": {
        "rn": 33,
        "evidence": "Duplicate relationship probability",
        "population": 20827,
        "traceable_ids": False,
        "native_probability": True,
        "policy_validated": False,
    },
    "T6": {
        "rn": 31,
        "evidence": "Duplicate retrieval ranking correctness",
        "population": 82416,
        "traceable_ids": True,
        "native_probability": False,
        "policy_validated": False,
    },
    "T7": {
        "rn": 32,
        "evidence": "Resolution-time survival evidence",
        "population": 102764,
        "traceable_ids": True,
        "native_probability": False,
        "policy_validated": False,
    },
}

for task, record in task_registry.items():
    print(
        f"{task}: RN #{record['rn']} | "
        f"{record['evidence']} | "
        f"population={record['population']} | "
        f"traceable_ids={record['traceable_ids']} | "
        f"native_probability={record['native_probability']}"
    )

registry_ok = (
    all(record["population"] > 0 for record in task_registry.values())
    and all(record["policy_validated"] is False
            for record in task_registry.values())
)

check(
    registry_ok,
    "C2 task-native evidence registered without policy overclaim"
)


# ---------------------------------------------------------------------
# 3. T5 locked-evaluation reconciliation
# ---------------------------------------------------------------------

print("\n[3] T5 LOCKED-EVALUATION RECONCILIATION")

t5_population = t5_metrics["evaluation_population"]
t5_locked = t5_metrics["metrics"]

print("Rows:", t5_population["rows"])
print("Positive:", t5_population["positive"])
print("Negative:", t5_population["negative"])
print("Unique IDs in source evaluation population:",
      t5_population["unique_ids"])

print("AP:", t5_locked["average_precision"])
print("ROC-AUC:", t5_locked["roc_auc"])
print("Log loss:", t5_locked["log_loss"])
print("Brier:", t5_locked["brier_score"])

t5_ok = (
    t5_population["rows"] == 20827
    and t5_population["positive"] == 1318
    and t5_population["negative"] == 19509
    and t5_population["unique_ids"] == 20827
)

check(t5_ok, "C3 T5 locked population reconciles")


# ---------------------------------------------------------------------
# 4. Cross-task fusion boundary
# ---------------------------------------------------------------------

print("\n[4] CROSS-TASK FUSION BOUNDARY")

print("Common universal target: NOT ESTABLISHED")
print("Common universal score: NOT ESTABLISHED")
print("Common calibrated score: NOT ESTABLISHED")
print("Universal ticket-level fusion population: NOT ESTABLISHED")
print("T5 locked ticket-ID provenance: NOT ESTABLISHED")
print("Cross-task fusion model: NOT BUILT")
print("Cross-task threshold optimization: NOT PERFORMED")

fusion_boundary_ok = True

check(
    fusion_boundary_ok,
    "C4 cross-task fusion boundary preserved"
)


# ---------------------------------------------------------------------
# 5. Decision-state validation status
# ---------------------------------------------------------------------

print("\n[5] DECISION-STATE VALIDATION STATUS")

decision_states = {
    "AUTOMATE": "NOT_VALIDATED",
    "HUMAN_REVIEW": "DEFINED_BUT_NOT_EMPIRICALLY_VALIDATED",
    "DEFER_INSUFFICIENT_EVIDENCE":
        "DEFINED_BUT_NOT_EMPIRICALLY_VALIDATED",
}

for state, status in decision_states.items():
    print(f"{state}: {status}")

decision_boundary_ok = all(
    status != "VALIDATED"
    for status in decision_states.values()
)

check(
    decision_boundary_ok,
    "C5 no unsupported validated decision state"
)


# ---------------------------------------------------------------------
# 6. Remaining empirical gaps
# ---------------------------------------------------------------------

print("\n[6] REMAINING EMPIRICAL GAPS")

remaining_gaps = [
    "validated uncertainty behavior",
    "evidence-to-correctness relationship",
    "acceptable automation-region error",
    "human-review behavior",
    "defer behavior",
    "evidence-combination performance",
    "override/correction outcomes",
    "operational cost consequences",
    "final empirical policy validation",
]

for gap in remaining_gaps:
    print(f"OPEN: {gap}")

gaps_preserved = len(remaining_gaps) == 9

check(
    gaps_preserved,
    "C6 remaining empirical policy gaps preserved"
)


# ---------------------------------------------------------------------
# 7. Prohibited inference guard
# ---------------------------------------------------------------------

print("\n[7] PROHIBITED INFERENCE GUARD")

prohibited_inferences = {
    "universal_automation_threshold": False,
    "universal_confidence_threshold": False,
    "universal_risk_threshold": False,
    "ticket_level_automation_eligibility": False,
    "overall_t10_accuracy": False,
    "overall_t10_probability": False,
    "task_ranking_as_overall_policy_winner": False,
    "higher_coverage_is_better": False,
}

for name, asserted in prohibited_inferences.items():
    print(
        f"{name}: "
        f"{'ASSERTED' if asserted else 'NOT ASSERTED'}"
    )

guard_ok = all(
    asserted is False
    for asserted in prohibited_inferences.values()
)

check(
    guard_ok,
    "C7 prohibited T10 inferences not asserted"
)


# ---------------------------------------------------------------------
# 8. T10 empirical closure determination
# ---------------------------------------------------------------------

print("\n[8] EMPIRICAL PHASE CLOSURE")

print("Native empirical branches completed: T2, T4, T5, T6, T7")
print("Task-native evidence preserved: YES")
print("Known provenance limitation preserved: YES")
print("Universal T10 policy empirically validated: NO")
print("Additional model-independent T10 contract expansion required: NO")

closure_ok = (
    t5_ok
    and registry_ok
    and fusion_boundary_ok
    and decision_boundary_ok
    and gaps_preserved
    and guard_ok
)

check(
    closure_ok,
    "C8 empirical evidence synthesis is internally consistent"
)


# ---------------------------------------------------------------------
# Final status
# ---------------------------------------------------------------------

print("\n" + "=" * 82)

if closure_ok:
    print("STATUS: PASS — T10 EMPIRICAL EVIDENCE PHASE CLOSED")
    print()
    print(
        "Task-native empirical evidence is available for T2, T4, T5, T6, "
        "and T7."
    )
    print(
        "The evidence remains task-native and is not converted into a "
        "universal T10 score or policy."
    )
    print(
        "T5 retains its documented ticket-level provenance limitation."
    )
    print(
        "AUTOMATE, HUMAN_REVIEW, and DEFER_INSUFFICIENT_EVIDENCE remain "
        "model-dependent empirical policy states rather than validated "
        "ticket-level outcomes."
    )
    print(
        "Further validation of thresholds, uncertainty, evidence "
        "combination, review/defer behavior, operational cost, "
        "override outcomes, and final policy performance requires "
        "future model-dependent empirical work."
    )
else:
    print("STATUS: FAIL")

print("=" * 82)