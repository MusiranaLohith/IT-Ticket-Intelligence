"""
T10 / OP-002
TASK EVIDENCE CONTRACT REGISTRY

Purpose:
    Define the task-specific evidence contracts that T10 may consume
    from T2-T7 while preserving each task's native semantics.

This operation does NOT:
    - train models
    - generate predictions
    - create automation thresholds
    - create universal confidence/risk scores
    - combine heterogeneous task probabilities
    - assign tickets to decision states
"""


# ============================================================
# TASK EVIDENCE CONTRACTS
# ============================================================

TASK_CONTRACTS = {
    "T2": {
        "task_name": "Priority Prediction",
        "evidence_type": "hard_class_prediction",
        "native_semantics": "multiclass classification",
        "prediction_boundary": "Creation",
        "target": "P1-P5 priority",
        "probability_evidence": False,
        "ranking_evidence": False,
        "survival_evidence": False,
        "missing_evidence": "UNAVAILABLE",
        "policy_role": "SECONDARY_DECISION_SUPPORT_SIGNAL",
        "allowed_use": (
            "Task-specific priority classification evidence."
        ),
        "prohibited_inferences": [
            "hard class is a calibrated probability",
            "predicted class is universal confidence",
            "output is autonomous priority assignment",
            "output can be numerically fused with heterogeneous evidence",
        ],
    },

    "T3": {
        "task_name": "Severity Prediction",
        "evidence_type": "hard_class_prediction",
        "native_semantics": "multiclass classification",
        "prediction_boundary": "Creation",
        "target": "S1-S4 severity",
        "probability_evidence": False,
        "ranking_evidence": False,
        "survival_evidence": False,
        "missing_evidence": "UNAVAILABLE",
        "policy_role": "TASK_SPECIFIC_DECISION_SUPPORT_ONLY",
        "allowed_use": (
            "Task-specific severity classification evidence."
        ),
        "prohibited_inferences": [
            "hard class is a calibrated probability",
            "predicted class is universal confidence",
            "output is universally correct severity",
            "output can be numerically fused with heterogeneous evidence",
        ],
    },

    "T4": {
        "task_name": "Specific Assignee / Routing",
        "evidence_type": "ranking_retrieval",
        "native_semantics": "candidate ranking / retrieval",
        "prediction_boundary": "Creation",
        "target": (
            "first valid post-Creation assignment "
            "to a specific assignee"
        ),
        "probability_evidence": False,
        "ranking_evidence": True,
        "survival_evidence": False,
        "missing_evidence": "UNAVAILABLE",
        "policy_role": "SECONDARY_DECISION_SUPPORT_SIGNAL",
        "allowed_use": (
            "Candidate ranking and retrieval evidence."
        ),
        "prohibited_inferences": [
            "rank is probability",
            "historical assignment is universal routing correctness",
            "unseen assignees are ordinary negative candidates",
            "ranking alone establishes autonomous assignment",
        ],
    },

    "T5": {
        "task_name": "Duplicate Detection",
        "evidence_type": "calibrated_probability",
        "native_semantics": "binary duplicate probability",
        "prediction_boundary": "Creation",
        "target": "duplicate vs non-duplicate",
        "probability_evidence": True,
        "ranking_evidence": False,
        "survival_evidence": False,
        "missing_evidence": "UNAVAILABLE",
        "policy_role": (
            "PROBABILITY_BASED_DECISION_SUPPORT_WITH_LIMITATIONS"
        ),
        "allowed_use": (
            "Task-specific probability evidence when the applicable "
            "calibration requirements are satisfied."
        ),
        "prohibited_inferences": [
            "probability is universal decision confidence",
            "uncalibrated probability is valid policy evidence",
            "probability can be numerically fused with heterogeneous evidence",
            "automation threshold is established by this contract",
        ],
    },

    "T6": {
        "task_name": "Similar / Duplicate Retrieval",
        "evidence_type": "query_level_ranking",
        "native_semantics": "query-candidate retrieval/ranking",
        "prediction_boundary": "Creation",
        "target": "native retrieval target",
        "probability_evidence": False,
        "ranking_evidence": True,
        "survival_evidence": False,
        "missing_evidence": "UNAVAILABLE",
        "policy_role": "SECONDARY_DECISION_SUPPORT_SIGNAL",
        "allowed_use": (
            "Native query-candidate retrieval and ranking evidence."
        ),
        "prohibited_inferences": [
            "ranking is probability",
            "observable_non_positive is a confirmed true negative",
            "retrieval ranking is ordinary binary classification",
            "ranking can be numerically fused with heterogeneous evidence",
        ],
    },

    "T7": {
        "task_name": "Resolution Time",
        "evidence_type": "survival_time_to_event",
        "native_semantics": (
            "time-to-event survival evidence with right censoring"
        ),
        "prediction_boundary": "Creation",
        "target": "time to resolution",
        "probability_evidence": False,
        "ranking_evidence": False,
        "survival_evidence": True,
        "missing_evidence": "UNAVAILABLE",
        "policy_role": "SURVIVAL_DECISION_SUPPORT",
        "allowed_use": (
            "Native survival/time-to-event evidence with "
            "right-censoring preserved."
        ),
        "prohibited_inferences": [
            "survival evidence is binary resolved/not-resolved",
            "censoring is negative feedback",
            "right-censoring can be discarded",
            "survival quantities can be numerically fused with heterogeneous evidence",
        ],
    },
}


# ============================================================
# CROSS-TASK CONTRACT
# ============================================================

CROSS_TASK_CONTRACT = {
    "universal_confidence": "PROHIBITED",
    "universal_risk_score": "PROHIBITED",
    "cross_task_probability_aggregation": "PROHIBITED",
    "arbitrary_cross_task_weighting": "PROHIBITED",
    "ranking_as_probability": "PROHIBITED",
    "survival_as_binary_classification": "PROHIBITED",
    "historical_assignment_as_universal_correctness": "PROHIBITED",
    "observable_non_positive_as_true_negative": "PROHIBITED",
    "censoring_as_negative_feedback": "PROHIBITED",
    "post_creation_information_for_creation_decision": "PROHIBITED",
    "synthetic_automation_target": "PROHIBITED",
    "synthetic_human_review_target": "PROHIBITED",
    "automation_threshold_selection": "OUT_OF_SCOPE",
}


# ============================================================
# INTEGRITY CHECKS
# ============================================================

expected_tasks = {"T2", "T3", "T4", "T5", "T6", "T7"}

assert set(TASK_CONTRACTS.keys()) == expected_tasks

assert (
    TASK_CONTRACTS["T2"]["evidence_type"]
    == "hard_class_prediction"
)

assert (
    TASK_CONTRACTS["T3"]["evidence_type"]
    == "hard_class_prediction"
)

assert (
    TASK_CONTRACTS["T4"]["evidence_type"]
    == "ranking_retrieval"
)

assert (
    TASK_CONTRACTS["T5"]["evidence_type"]
    == "calibrated_probability"
)

assert (
    TASK_CONTRACTS["T6"]["evidence_type"]
    == "query_level_ranking"
)

assert (
    TASK_CONTRACTS["T7"]["evidence_type"]
    == "survival_time_to_event"
)


# Only T5 exposes probability evidence.
assert TASK_CONTRACTS["T2"]["probability_evidence"] is False
assert TASK_CONTRACTS["T3"]["probability_evidence"] is False
assert TASK_CONTRACTS["T4"]["probability_evidence"] is False
assert TASK_CONTRACTS["T5"]["probability_evidence"] is True
assert TASK_CONTRACTS["T6"]["probability_evidence"] is False
assert TASK_CONTRACTS["T7"]["probability_evidence"] is False


# T4 and T6 are ranking/retrieval evidence.
assert TASK_CONTRACTS["T4"]["ranking_evidence"] is True
assert TASK_CONTRACTS["T6"]["ranking_evidence"] is True


# T7 is survival evidence.
assert TASK_CONTRACTS["T7"]["survival_evidence"] is True


# Critical cross-task prohibitions.
assert (
    CROSS_TASK_CONTRACT["universal_confidence"]
    == "PROHIBITED"
)

assert (
    CROSS_TASK_CONTRACT["universal_risk_score"]
    == "PROHIBITED"
)

assert (
    CROSS_TASK_CONTRACT["cross_task_probability_aggregation"]
    == "PROHIBITED"
)

assert (
    CROSS_TASK_CONTRACT["ranking_as_probability"]
    == "PROHIBITED"
)

assert (
    CROSS_TASK_CONTRACT["survival_as_binary_classification"]
    == "PROHIBITED"
)


# ============================================================
# EXECUTION REPORT
# ============================================================

print("=" * 72)
print("T10 / OP-002 — TASK EVIDENCE CONTRACT REGISTRY")
print("=" * 72)

print()
print("[1] Contract registry")

print(f"  Tasks registered: {len(TASK_CONTRACTS)}")

for task_id, contract in TASK_CONTRACTS.items():
    print()
    print(f"--- {task_id} ---")
    print(f"  Task: {contract['task_name']}")
    print(f"  Evidence type: {contract['evidence_type']}")
    print(f"  Native semantics: {contract['native_semantics']}")
    print(f"  Prediction boundary: {contract['prediction_boundary']}")
    print(
        f"  Probability evidence: "
        f"{contract['probability_evidence']}"
    )
    print(
        f"  Ranking evidence: "
        f"{contract['ranking_evidence']}"
    )
    print(
        f"  Survival evidence: "
        f"{contract['survival_evidence']}"
    )
    print(f"  Policy role: {contract['policy_role']}")

print()
print("[2] Cross-task boundaries")

for key, value in CROSS_TASK_CONTRACT.items():
    print(f"  {key}: {value}")

print()
print("[3] Integrity checks")

print("  T2-T7 registry completeness: PASS")
print("  T2 classification semantics: PASS")
print("  T3 classification semantics: PASS")
print("  T4 ranking semantics: PASS")
print("  T5 probability semantics: PASS")
print("  T6 retrieval semantics: PASS")
print("  T7 survival semantics: PASS")
print("  Cross-task probability aggregation: PROHIBITED")
print("  Universal confidence: PROHIBITED")
print("  Universal risk score: PROHIBITED")
print("  Ranking-as-probability: PROHIBITED")
print("  Survival-as-binary: PROHIBITED")

print()
print("[4] Scope boundaries")

print("  Predictions generated: NO")
print("  Models trained: NO")
print("  Automation threshold created: NO")
print("  Ticket decisions created: NO")
print("  Empirical policy evaluation: NO")

print()
print("OP-002 execution complete.")
print("Next step: inspect the execution result before assigning the RN.")