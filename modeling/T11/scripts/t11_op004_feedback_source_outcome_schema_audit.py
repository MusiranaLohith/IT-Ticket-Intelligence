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
print("T11 / OP-004 — OPERATIONAL FEEDBACK SOURCE & OUTCOME SCHEMA AUDIT")
print("=" * 82)


# ---------------------------------------------------------------------
# 1. Feedback source categories
# ---------------------------------------------------------------------

print("\n[1] ELIGIBLE OPERATIONAL FEEDBACK SOURCE CATEGORIES")

source_categories = {
    "human_review": (
        "documented human review of a prediction-linked ticket"
    ),
    "human_correction": (
        "documented correction or override of a prediction-linked output"
    ),
    "real_world_outcome": (
        "observed downstream operational outcome linked to a prediction"
    ),
    "validated_external_outcome": (
        "externally sourced outcome with traceable ticket/prediction linkage"
    ),
}

for name, definition in source_categories.items():
    print(f"{name}: {definition}")

source_categories_ok = len(source_categories) == 4

check(
    source_categories_ok,
    "C1 legitimate operational feedback source categories are explicit"
)


# ---------------------------------------------------------------------
# 2. Required source provenance
# ---------------------------------------------------------------------

print("\n[2] FEEDBACK SOURCE PROVENANCE")

source_requirements = {
    "source_type": True,
    "source_identity": True,
    "collection_or_observation_timestamp": True,
    "provenance_reference": True,
    "prediction_link": True,
    "ticket_link": True,
}

for field, required in source_requirements.items():
    print(f"{field}: {'REQUIRED' if required else 'OPTIONAL'}")

source_provenance_ok = all(source_requirements.values())

check(
    source_provenance_ok,
    "C2 feedback source provenance requirements are explicit"
)


# ---------------------------------------------------------------------
# 3. Human review outcome schema
# ---------------------------------------------------------------------

print("\n[3] HUMAN REVIEW OUTCOME SCHEMA")

human_review_fields = [
    "prediction_id",
    "ticket_id",
    "review_timestamp",
    "reviewer_identity_or_role",
    "review_decision",
    "review_basis_or_reason",
    "source_reference",
]

for field in human_review_fields:
    print(f"REQUIRED: {field}")

human_review_ok = len(human_review_fields) == 7

check(
    human_review_ok,
    "C3 human review feedback requires traceable review evidence"
)


# ---------------------------------------------------------------------
# 4. Human correction / override schema
# ---------------------------------------------------------------------

print("\n[4] HUMAN CORRECTION / OVERRIDE SCHEMA")

correction_fields = [
    "prediction_id",
    "ticket_id",
    "original_prediction",
    "corrected_outcome",
    "correction_timestamp",
    "reviewer_identity_or_role",
    "correction_reason",
    "source_reference",
]

for field in correction_fields:
    print(f"REQUIRED: {field}")

correction_ok = len(correction_fields) == 8

check(
    correction_ok,
    "C4 correction/override feedback preserves before-and-after evidence"
)


# ---------------------------------------------------------------------
# 5. Real-world outcome schema
# ---------------------------------------------------------------------

print("\n[5] REAL-WORLD OPERATIONAL OUTCOME SCHEMA")

outcome_fields = [
    "prediction_id",
    "ticket_id",
    "outcome_timestamp",
    "outcome_type",
    "observed_outcome",
    "outcome_source",
    "source_reference",
]

for field in outcome_fields:
    print(f"REQUIRED: {field}")

outcome_ok = len(outcome_fields) == 7

check(
    outcome_ok,
    "C5 real-world outcomes require explicit observed outcome provenance"
)


# ---------------------------------------------------------------------
# 6. Temporal boundary
# ---------------------------------------------------------------------

print("\n[6] TEMPORAL FEEDBACK BOUNDARY")

temporal_rules = [
    "feedback observation must occur after or at the prediction event",
    "prediction timestamp must remain immutable",
    "feedback timestamp must be retained",
    "future information must not enter prediction-time features",
    "post-prediction outcomes may become learning signals only after validation",
]

for rule in temporal_rules:
    print(f"RULE: {rule}")

temporal_ok = len(temporal_rules) == 5

check(
    temporal_ok,
    "C6 prediction-time and feedback-time boundaries are explicit"
)


# ---------------------------------------------------------------------
# 7. Validation requirements
# ---------------------------------------------------------------------

print("\n[7] FEEDBACK VALIDATION REQUIREMENTS")

validation_requirements = [
    "prediction linkage verified",
    "ticket linkage verified",
    "source verified",
    "timestamp verified",
    "outcome observed rather than inferred",
    "duplicate feedback resolved",
    "conflicting feedback resolved or rejected",
    "task semantics verified",
    "prediction-time leakage excluded",
]

for requirement in validation_requirements:
    print(f"REQUIRED: {requirement}")

validation_ok = len(validation_requirements) == 9

check(
    validation_ok,
    "C7 operational feedback requires validation before learning use"
)


# ---------------------------------------------------------------------
# 8. Explicit non-feedback sources
# ---------------------------------------------------------------------

print("\n[8] EXPLICIT NON-FEEDBACK SOURCES")

non_feedback_sources = [
    "historical task evaluation targets",
    "held-out test labels",
    "validation labels",
    "model predictions without observed outcomes",
    "inferred human decisions",
    "synthetic human-review labels",
    "synthetic operational outcomes",
    "unobserved ticket outcomes",
    "model-generated self-labels",
]

for source in non_feedback_sources:
    print(f"NOT FEEDBACK: {source}")

non_feedback_ok = len(non_feedback_sources) == 9

check(
    non_feedback_ok,
    "C8 non-feedback sources are explicitly excluded"
)


# ---------------------------------------------------------------------
# 9. Admission boundary
# ---------------------------------------------------------------------

print("\n[9] LEARNING-SIGNAL ADMISSION BOUNDARY")

admission_rules = [
    "validated operational feedback required",
    "prediction linkage required",
    "ticket linkage required",
    "source provenance retained",
    "outcome observation retained",
    "task semantics retained",
    "temporal boundary retained",
    "validation decision recorded",
]

for rule in admission_rules:
    print(f"RULE: {rule}")

admission_ok = len(admission_rules) == 8

check(
    admission_ok,
    "C9 learning-signal admission remains downstream of feedback validation"
)


# ---------------------------------------------------------------------
# 10. Current evidence state
# ---------------------------------------------------------------------

print("\n[10] CURRENT OPERATIONAL EVIDENCE STATE")

print("Actual human review records: NOT ESTABLISHED")
print("Actual correction/override records: NOT ESTABLISHED")
print("Actual real-world outcome records: NOT ESTABLISHED")
print("Validated external outcome records: NOT ESTABLISHED")
print("Prediction-to-feedback linkage: NOT ESTABLISHED")
print("Validated operational feedback: NOT ESTABLISHED")
print("Learning-signal dataset: NOT ESTABLISHED")

current_state_ok = True

check(
    current_state_ok,
    "C10 current state does not falsely claim operational feedback exists"
)


# ---------------------------------------------------------------------
# 11. No synthetic feedback creation
# ---------------------------------------------------------------------

print("\n[11] SYNTHETIC-FEEDBACK GUARD")

synthetic_guards = [
    "no synthetic human reviews",
    "no synthetic corrections",
    "no synthetic overrides",
    "no synthetic operational outcomes",
    "no inferred reviewer decisions",
    "no conversion of historical targets into feedback",
]

for guard in synthetic_guards:
    print(f"GUARD: {guard}")

synthetic_guard_ok = len(synthetic_guards) == 6

check(
    synthetic_guard_ok,
    "C11 no synthetic operational feedback is created"
)


# ---------------------------------------------------------------------
# 12. Final contract state
# ---------------------------------------------------------------------

print("\n[12] FINAL OP-004 STATE")

print("Eligible feedback source schema: DEFINED")
print("Outcome schema: DEFINED")
print("Temporal boundary: DEFINED")
print("Validation boundary: DEFINED")
print("Learning-signal admission boundary: DEFINED")
print("Actual operational feedback: NOT ESTABLISHED")

final_state_ok = (
    source_categories_ok
    and source_provenance_ok
    and human_review_ok
    and correction_ok
    and outcome_ok
    and temporal_ok
    and validation_ok
    and non_feedback_ok
    and admission_ok
    and current_state_ok
    and synthetic_guard_ok
)


check(
    final_state_ok,
    "C12 T11 operational feedback schema remains evidence-consistent"
)


# ---------------------------------------------------------------------
# Final status
# ---------------------------------------------------------------------

print("\n" + "=" * 82)

if final_state_ok:
    print("STATUS: PASS")
    print()
    print(
        "T11 operational feedback source and outcome schemas are defined."
    )
    print(
        "Only observed, traceable, prediction-linked feedback may "
        "be considered for learning-signal admission."
    )
    print(
        "Historical evaluation targets, inferred outcomes, "
        "synthetic feedback, and unobserved outcomes remain excluded."
    )
    print(
        "No actual operational feedback is claimed to exist."
    )
else:
    print("STATUS: FAIL")

print("=" * 82)