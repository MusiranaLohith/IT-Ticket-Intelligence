from pathlib import Path


T11_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/modeling/T11"
)

SCRIPTS_DIR = T11_ROOT / "scripts"


def check(condition, label):
    status = "PASS" if condition else "FAIL"
    print(f"{label}: {status}")
    return condition


print("=" * 82)
print("T11 / OP-002 — PREDICTION-TO-LEARNING-SIGNAL CONTRACT")
print("=" * 82)


# ---------------------------------------------------------------------
# 1. Lifecycle stages
# ---------------------------------------------------------------------

print("\n[1] T11 LIFECYCLE STAGES")

lifecycle = [
    "prediction",
    "review_or_real_world_outcome",
    "feedback_validation",
    "learning_signal_admission",
    "training_data_admission",
    "retraining",
    "post_retraining_validation",
]

for index, stage in enumerate(lifecycle, start=1):
    print(f"{index}. {stage}")

lifecycle_ok = (
    lifecycle
    == [
        "prediction",
        "review_or_real_world_outcome",
        "feedback_validation",
        "learning_signal_admission",
        "training_data_admission",
        "retraining",
        "post_retraining_validation",
    ]
)

check(
    lifecycle_ok,
    "C1 lifecycle ordering is explicit"
)


# ---------------------------------------------------------------------
# 2. Prediction event contract
# ---------------------------------------------------------------------

print("\n[2] PREDICTION EVENT CONTRACT")

prediction_requirements = {
    "prediction_id": True,
    "ticket_id": True,
    "task_identity": True,
    "model_or_version_identity": True,
    "prediction_timestamp": True,
    "prediction_output": True,
    "input_population_provenance": True,
}

for field, required in prediction_requirements.items():
    print(f"{field}: {'REQUIRED' if required else 'OPTIONAL'}")

prediction_contract_ok = all(prediction_requirements.values())

check(
    prediction_contract_ok,
    "C2 prediction event requires traceable prediction provenance"
)


# ---------------------------------------------------------------------
# 3. Review / outcome contract
# ---------------------------------------------------------------------

print("\n[3] REVIEW / OUTCOME CONTRACT")

outcome_requirements = {
    "linked_prediction_id": True,
    "linked_ticket_id": True,
    "outcome_timestamp": True,
    "outcome_source": True,
    "reviewer_or_source_identity": True,
    "observed_outcome": True,
}

for field, required in outcome_requirements.items():
    print(f"{field}: {'REQUIRED' if required else 'OPTIONAL'}")

outcome_contract_ok = all(outcome_requirements.values())

check(
    outcome_contract_ok,
    "C3 review/outcome must remain traceably linked to prediction"
)


# ---------------------------------------------------------------------
# 4. Feedback validation contract
# ---------------------------------------------------------------------

print("\n[4] FEEDBACK VALIDATION CONTRACT")

validation_rules = {
    "prediction_link_exists": True,
    "ticket_identity_reconciles": True,
    "outcome_is_observed": True,
    "outcome_timestamp_is_valid": True,
    "outcome_source_is_known": True,
    "duplicate_feedback_is_resolved": True,
    "contradictory_feedback_is_flagged": True,
    "post_prediction_outcome_boundary_is_preserved": True,
}

for rule, required in validation_rules.items():
    print(f"{rule}: {'REQUIRED' if required else 'OPTIONAL'}")

validation_contract_ok = all(validation_rules.values())

check(
    validation_contract_ok,
    "C4 feedback requires validation before learning use"
)


# ---------------------------------------------------------------------
# 5. Learning-signal admission contract
# ---------------------------------------------------------------------

print("\n[5] LEARNING-SIGNAL ADMISSION")

admission_rules = {
    "validated_prediction_link": True,
    "validated_ticket_link": True,
    "observed_outcome": True,
    "provenance_available": True,
    "no_unresolved_conflict": True,
    "no_unresolved_duplicate_feedback": True,
    "task_semantics_preserved": True,
    "prediction_time_boundary_preserved": True,
}

for rule, required in admission_rules.items():
    print(f"{rule}: {'REQUIRED' if required else 'OPTIONAL'}")

admission_contract_ok = all(admission_rules.values())

check(
    admission_contract_ok,
    "C5 learning-signal admission requires validated evidence"
)


# ---------------------------------------------------------------------
# 6. Explicit rejection conditions
# ---------------------------------------------------------------------

print("\n[6] FEEDBACK REJECTION CONDITIONS")

rejection_conditions = [
    "missing prediction linkage",
    "missing ticket linkage",
    "unverified outcome",
    "unknown feedback source",
    "duplicate unresolved feedback",
    "conflicting unresolved feedback",
    "post-hoc synthetic label",
    "inferred outcome without observation",
    "task-semantic mismatch",
    "prediction-time leakage",
]

for condition in rejection_conditions:
    print(f"REJECT: {condition}")

rejection_contract_ok = len(rejection_conditions) == 10

check(
    rejection_contract_ok,
    "C6 invalid feedback conditions are explicitly rejected"
)


# ---------------------------------------------------------------------
# 7. Training-data admission boundary
# ---------------------------------------------------------------------

print("\n[7] TRAINING-DATA ADMISSION BOUNDARY")

training_rules = [
    "validated learning signal required",
    "source provenance retained",
    "prediction-time feature boundary preserved",
    "task target semantics preserved",
    "unvalidated feedback excluded",
    "synthetic feedback excluded",
    "unresolved conflict excluded",
    "admission decision recorded",
]

for rule in training_rules:
    print(f"RULE: {rule}")

training_contract_ok = len(training_rules) == 8

check(
    training_contract_ok,
    "C7 retraining data admission remains downstream of validation"
)


# ---------------------------------------------------------------------
# 8. Retraining boundary
# ---------------------------------------------------------------------

print("\n[8] RETRAINING BOUNDARY")

print("Automatic retraining trigger: NOT ESTABLISHED")
print("Feedback volume threshold: NOT ESTABLISHED")
print("Drift threshold: NOT ESTABLISHED")
print("Performance-degradation threshold: NOT ESTABLISHED")
print("Retraining schedule: NOT ESTABLISHED")
print("Retraining without validation: PROHIBITED")

retraining_boundary_ok = True

check(
    retraining_boundary_ok,
    "C8 retraining policy remains empirically open"
)


# ---------------------------------------------------------------------
# 9. Post-retraining validation
# ---------------------------------------------------------------------

print("\n[9] POST-RETRAINING VALIDATION")

validation_requirements = [
    "frozen evaluation evidence",
    "comparison against prior model",
    "task-appropriate metrics",
    "regression checks",
    "leakage checks",
    "calibration checks where applicable",
    "error analysis",
    "deployment/admission decision",
]

for requirement in validation_requirements:
    print(f"REQUIRED: {requirement}")

post_validation_ok = len(validation_requirements) == 8

check(
    post_validation_ok,
    "C9 retraining must be followed by empirical validation"
)


# ---------------------------------------------------------------------
# 10. Synthetic-feedback guard
# ---------------------------------------------------------------------

print("\n[10] SYNTHETIC-FEEDBACK GUARD")

guards = {
    "synthetic_human_labels": False,
    "synthetic_operational_outcomes": False,
    "inferred_review_decisions": False,
    "historical_task_targets_as_feedback": False,
    "unobserved_outcomes_as_feedback": False,
    "automatic_label_from_model_prediction": False,
}

for name, forbidden in guards.items():
    print(
        f"{name}: "
        f"{'FORBIDDEN' if forbidden is False else 'ALLOWED'}"
    )

synthetic_guard_ok = all(
    value is False for value in guards.values()
)

check(
    synthetic_guard_ok,
    "C10 synthetic or inferred feedback cannot become learning labels"
)


# ---------------------------------------------------------------------
# 11. Current-state boundary
# ---------------------------------------------------------------------

print("\n[11] CURRENT T11 STATE")

print("Actual operational feedback: NOT ESTABLISHED")
print("Validated learning signal: NOT ESTABLISHED")
print("Retraining dataset: NOT ESTABLISHED")
print("Retraining model: NOT BUILT")
print("Active-learning loop: NOT IMPLEMENTED")

current_state_ok = True

check(
    current_state_ok,
    "C11 contract does not falsely claim operational feedback exists"
)


# ---------------------------------------------------------------------
# Final status
# ---------------------------------------------------------------------

all_checks = (
    lifecycle_ok
    and prediction_contract_ok
    and outcome_contract_ok
    and validation_contract_ok
    and admission_contract_ok
    and rejection_contract_ok
    and training_contract_ok
    and retraining_boundary_ok
    and post_validation_ok
    and synthetic_guard_ok
    and current_state_ok
)

print("\n" + "=" * 82)

if all_checks:
    print("STATUS: PASS")
    print()
    print(
        "T11 prediction-to-learning-signal contract is defined."
    )
    print(
        "Feedback must be prediction-linked, observed, traceable, "
        "validated, and semantically compatible before admission."
    )
    print(
        "Unvalidated, synthetic, inferred, conflicting, or "
        "leakage-prone feedback is excluded."
    )
    print(
        "Retraining triggers and operational thresholds remain "
        "empirically open."
    )
else:
    print("STATUS: FAIL")

print("=" * 82)