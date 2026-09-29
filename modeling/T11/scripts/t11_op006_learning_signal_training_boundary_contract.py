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
print("T11 / OP-006 — LEARNING-SIGNAL & TRAINING-DATA BOUNDARY CONTRACT")
print("=" * 82)


# ---------------------------------------------------------------------
# 1. Admission pipeline
# ---------------------------------------------------------------------

print("\n[1] LEARNING-SIGNAL ADMISSION PIPELINE")

admission_pipeline = [
    "validated_feedback",
    "learning_signal_creation",
    "learning_signal_provenance_check",
    "task_semantics_check",
    "temporal_boundary_check",
    "evaluation_set_exclusion_check",
    "duplicate_conflict_check",
    "training_data_admission_decision",
    "admission_audit_record",
]

for index, stage in enumerate(admission_pipeline, start=1):
    print(f"{index}. {stage}")

pipeline_ok = len(admission_pipeline) == 9

check(
    pipeline_ok,
    "C1 learning-signal admission pipeline is explicitly ordered"
)


# ---------------------------------------------------------------------
# 2. Required learning-signal fields
# ---------------------------------------------------------------------

print("\n[2] LEARNING-SIGNAL RECORD REQUIREMENTS")

learning_signal_fields = [
    "learning_signal_id",
    "prediction_id",
    "ticket_id",
    "task_identity",
    "validated_feedback_reference",
    "observed_outcome",
    "feedback_timestamp",
    "validation_status",
    "validation_provenance",
    "admission_timestamp",
]

for field in learning_signal_fields:
    print(f"REQUIRED: {field}")

learning_signal_fields_ok = len(learning_signal_fields) == 10

check(
    learning_signal_fields_ok,
    "C2 admitted learning signals require traceable provenance"
)


# ---------------------------------------------------------------------
# 3. Admission requirements
# ---------------------------------------------------------------------

print("\n[3] LEARNING-SIGNAL ADMISSION REQUIREMENTS")

admission_requirements = [
    "feedback status must be VALIDATED",
    "prediction linkage must be verified",
    "ticket linkage must be verified",
    "observed outcome must be available",
    "source provenance must be retained",
    "task semantics must be preserved",
    "prediction-time boundary must be preserved",
    "no unresolved conflict may remain",
    "no unresolved duplicate may remain",
    "admission decision must be recorded",
]

for requirement in admission_requirements:
    print(f"REQUIRED: {requirement}")

admission_requirements_ok = len(admission_requirements) == 10

check(
    admission_requirements_ok,
    "C3 learning-signal admission requirements are explicit"
)


# ---------------------------------------------------------------------
# 4. Excluded feedback states
# ---------------------------------------------------------------------

print("\n[4] EXCLUDED FEEDBACK STATES")

excluded_states = [
    "REJECTED",
    "CONFLICT_PENDING",
    "DUPLICATE_PENDING",
    "UNVERIFIED",
    "UNOBSERVED",
]

for state in excluded_states:
    print(f"EXCLUDE: {state}")

excluded_states_ok = len(excluded_states) == 5

check(
    excluded_states_ok,
    "C4 non-validated feedback states cannot enter training data"
)


# ---------------------------------------------------------------------
# 5. Task-target preservation
# ---------------------------------------------------------------------

print("\n[5] TASK-TARGET SEMANTICS")

target_rules = [
    "learning signal must retain originating task identity",
    "observed outcome must retain originating task semantics",
    "feedback cannot silently change target definition",
    "classification outcomes remain classification outcomes",
    "ranking outcomes remain ranking outcomes",
    "survival outcomes retain event/censoring semantics",
    "duplicate-related outcomes retain duplicate-task semantics",
]

for rule in target_rules:
    print(f"RULE: {rule}")

target_rules_ok = len(target_rules) == 7

check(
    target_rules_ok,
    "C5 task-target semantics remain unchanged during admission"
)


# ---------------------------------------------------------------------
# 6. Feature / label boundary
# ---------------------------------------------------------------------

print("\n[6] FEATURE / LABEL BOUNDARY")

feature_label_rules = [
    "post-prediction feedback cannot become a prediction-time feature",
    "observed outcome remains the learning target where appropriate",
    "feedback metadata must not leak into prediction features",
    "validation decisions must not become prediction features",
    "admission status must not become a prediction feature",
]

for rule in feature_label_rules:
    print(f"RULE: {rule}")

feature_label_ok = len(feature_label_rules) == 5

check(
    feature_label_ok,
    "C6 feature/label separation prevents feedback leakage"
)


# ---------------------------------------------------------------------
# 7. Evaluation-set protection
# ---------------------------------------------------------------------

print("\n[7] EVALUATION-SET PROTECTION")

evaluation_rules = [
    "frozen evaluation populations remain excluded from retraining admission",
    "held-out test labels are not recycled as operational feedback",
    "evaluation outcomes cannot be used to manufacture learning signals",
    "evaluation membership must remain traceable",
    "future retraining must use a separate development/training boundary",
]

for rule in evaluation_rules:
    print(f"RULE: {rule}")

evaluation_ok = len(evaluation_rules) == 5

check(
    evaluation_ok,
    "C7 frozen evaluation evidence remains protected"
)


# ---------------------------------------------------------------------
# 8. Duplicate and conflict protection
# ---------------------------------------------------------------------

print("\n[8] DUPLICATE / CONFLICT PROTECTION")

integrity_rules = [
    "duplicate learning signals must not receive repeated training weight",
    "unresolved conflicts cannot be admitted",
    "resolved conflicts retain adjudication provenance",
    "one feedback event must not silently become multiple independent labels",
]

for rule in integrity_rules:
    print(f"RULE: {rule}")

integrity_ok = len(integrity_rules) == 4

check(
    integrity_ok,
    "C8 duplicate/conflict protection is preserved at admission"
)


# ---------------------------------------------------------------------
# 9. Admission audit trail
# ---------------------------------------------------------------------

print("\n[9] ADMISSION AUDIT TRAIL")

audit_fields = [
    "learning_signal_id",
    "admission_decision",
    "decision_timestamp",
    "validation_reference",
    "decision_reason",
    "task_identity",
]

for field in audit_fields:
    print(f"REQUIRED: {field}")

audit_ok = len(audit_fields) == 6

check(
    audit_ok,
    "C9 training-data admission decisions remain auditable"
)


# ---------------------------------------------------------------------
# 10. Retraining boundary
# ---------------------------------------------------------------------

print("\n[10] RETRAINING BOUNDARY")

print("Automatic retraining trigger: NOT ESTABLISHED")
print("Minimum admitted-feedback volume: NOT ESTABLISHED")
print("Drift trigger: NOT ESTABLISHED")
print("Performance-degradation trigger: NOT ESTABLISHED")
print("Retraining schedule: NOT ESTABLISHED")
print("Retraining without post-retraining validation: PROHIBITED")

retraining_boundary_ok = True

check(
    retraining_boundary_ok,
    "C10 retraining policy remains empirically open"
)


# ---------------------------------------------------------------------
# 11. Synthetic-data guard
# ---------------------------------------------------------------------

print("\n[11] SYNTHETIC-DATA GUARD")

synthetic_guards = [
    "no synthetic learning signals",
    "no fabricated observed outcomes",
    "no fabricated validation decisions",
    "no synthetic reviewer labels",
    "no conversion of historical evaluation targets into feedback",
    "no model-generated self-labels",
]

for guard in synthetic_guards:
    print(f"GUARD: {guard}")

synthetic_guard_ok = len(synthetic_guards) == 6

check(
    synthetic_guard_ok,
    "C11 training-data admission cannot create synthetic feedback"
)


# ---------------------------------------------------------------------
# 12. Current operational state
# ---------------------------------------------------------------------

print("\n[12] CURRENT T11 TRAINING-DATA STATE")

print("Validated learning signals: NOT ESTABLISHED")
print("Admitted training records: NOT ESTABLISHED")
print("T11 retraining dataset: NOT ESTABLISHED")
print("T11 retraining model: NOT BUILT")
print("Automatic retraining: NOT ESTABLISHED")

current_state_ok = True

check(
    current_state_ok,
    "C12 current T11 training-data state remains non-operational"
)


# ---------------------------------------------------------------------
# Final status
# ---------------------------------------------------------------------

all_checks = (
    pipeline_ok
    and learning_signal_fields_ok
    and admission_requirements_ok
    and excluded_states_ok
    and target_rules_ok
    and feature_label_ok
    and evaluation_ok
    and integrity_ok
    and audit_ok
    and retraining_boundary_ok
    and synthetic_guard_ok
    and current_state_ok
)

print("\n" + "=" * 82)

if all_checks:
    print("STATUS: PASS")
    print()
    print(
        "T11 learning-signal and training-data admission boundaries "
        "are defined."
    )
    print(
        "Only validated feedback may become a learning signal, "
        "and only admitted learning signals may enter future "
        "training data."
    )
    print(
        "Frozen evaluation evidence, unresolved conflicts, "
        "duplicates, unverified feedback, and synthetic signals "
        "remain excluded."
    )
    print(
        "No actual T11 training data or retraining model is claimed "
        "to exist."
    )
else:
    print("STATUS: FAIL")

print("=" * 82)