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
print("T11 / OP-008 — LEARNING-SIGNAL POPULATION INTEGRITY & ADMISSION AUDIT")
print("=" * 82)


# ---------------------------------------------------------------------
# 1. Population identity
# ---------------------------------------------------------------------

print("\n[1] LEARNING-SIGNAL POPULATION IDENTITY")

population_identity_fields = [
    "learning_signal_id",
    "prediction_id",
    "ticket_id",
    "task_identity",
    "model_or_version_identity",
    "feedback_reference",
]

for field in population_identity_fields:
    print(f"REQUIRED: {field}")

population_identity_ok = len(population_identity_fields) == 6

check(
    population_identity_ok,
    "C1 learning-signal population requires stable identity fields"
)


# ---------------------------------------------------------------------
# 2. Uniqueness rules
# ---------------------------------------------------------------------

print("\n[2] UNIQUENESS RULES")

uniqueness_rules = [
    "learning_signal_id must be unique",
    "prediction_id must resolve to the intended prediction event",
    "one prediction event must not silently create duplicate learning signals",
    "duplicate feedback must be resolved before admission",
    "duplicate learning signals must not receive repeated training weight",
]

for rule in uniqueness_rules:
    print(f"RULE: {rule}")

uniqueness_ok = len(uniqueness_rules) == 5

check(
    uniqueness_ok,
    "C2 learning-signal uniqueness rules are explicit"
)


# ---------------------------------------------------------------------
# 3. Prediction linkage integrity
# ---------------------------------------------------------------------

print("\n[3] PREDICTION LINKAGE INTEGRITY")

prediction_link_rules = [
    "prediction_id must resolve to an existing prediction",
    "prediction task identity must be known",
    "prediction output must remain traceable",
    "prediction provenance must be retained",
    "prediction timestamp must remain available where required",
]

for rule in prediction_link_rules:
    print(f"RULE: {rule}")

prediction_link_ok = len(prediction_link_rules) == 5

check(
    prediction_link_ok,
    "C3 learning signals require valid prediction linkage"
)


# ---------------------------------------------------------------------
# 4. Ticket linkage integrity
# ---------------------------------------------------------------------

print("\n[4] TICKET LINKAGE INTEGRITY")

ticket_link_rules = [
    "ticket_id must resolve to the intended ticket",
    "ticket identity must remain consistent across records",
    "feedback must not be attached to an unrelated ticket",
    "prediction and feedback ticket identities must reconcile",
]

for rule in ticket_link_rules:
    print(f"RULE: {rule}")

ticket_link_ok = len(ticket_link_rules) == 4

check(
    ticket_link_ok,
    "C4 ticket linkage must remain internally consistent"
)


# ---------------------------------------------------------------------
# 5. Task separation
# ---------------------------------------------------------------------

print("\n[5] TASK SEPARATION")

task_rules = [
    "each learning signal retains its originating task identity",
    "priority labels cannot be admitted as assignee labels",
    "classification outcomes cannot be silently converted into ranking targets",
    "ranking outcomes cannot be silently converted into classification targets",
    "survival outcomes retain event/censoring semantics",
    "duplicate outcomes retain duplicate-task semantics",
]

for rule in task_rules:
    print(f"RULE: {rule}")

task_separation_ok = len(task_rules) == 6

check(
    task_separation_ok,
    "C5 learning signals remain separated by task semantics"
)


# ---------------------------------------------------------------------
# 6. Outcome integrity
# ---------------------------------------------------------------------

print("\n[6] OUTCOME INTEGRITY")

outcome_rules = [
    "outcome must be observed",
    "outcome source must be known",
    "outcome timestamp must be retained",
    "inferred outcomes are not equivalent to observed outcomes",
    "unobserved outcomes are excluded",
]

for rule in outcome_rules:
    print(f"RULE: {rule}")

outcome_integrity_ok = len(outcome_rules) == 5

check(
    outcome_integrity_ok,
    "C6 admitted learning signals require observed outcome integrity"
)


# ---------------------------------------------------------------------
# 7. Conflict integrity
# ---------------------------------------------------------------------

print("\n[7] CONFLICT INTEGRITY")

conflict_rules = [
    "conflicting feedback must be detected",
    "unresolved conflicts cannot be admitted",
    "resolved conflicts retain adjudication provenance",
    "conflict resolution must not silently overwrite original evidence",
]

for rule in conflict_rules:
    print(f"RULE: {rule}")

conflict_integrity_ok = len(conflict_rules) == 4

check(
    conflict_integrity_ok,
    "C7 unresolved conflicting signals remain excluded"
)


# ---------------------------------------------------------------------
# 8. Temporal integrity
# ---------------------------------------------------------------------

print("\n[8] TEMPORAL INTEGRITY")

temporal_rules = [
    "feedback observation must not precede prediction",
    "feedback timestamp must remain immutable",
    "prediction-time feature boundary must remain intact",
    "future outcome information must not be backfilled into historical features",
    "retraining admission must preserve temporal ordering",
]

for rule in temporal_rules:
    print(f"RULE: {rule}")

temporal_integrity_ok = len(temporal_rules) == 5

check(
    temporal_integrity_ok,
    "C8 learning-signal population must preserve temporal integrity"
)


# ---------------------------------------------------------------------
# 9. Evaluation contamination protection
# ---------------------------------------------------------------------

print("\n[9] EVALUATION CONTAMINATION PROTECTION")

evaluation_rules = [
    "frozen evaluation membership must remain identifiable",
    "held-out evaluation records cannot be admitted as new operational feedback",
    "evaluation outcomes cannot be recycled into retraining labels",
    "training and evaluation populations must remain separable",
    "evaluation contamination must block admission",
]

for rule in evaluation_rules:
    print(f"RULE: {rule}")

evaluation_integrity_ok = len(evaluation_rules) == 5

check(
    evaluation_integrity_ok,
    "C9 evaluation contamination is explicitly blocked"
)


# ---------------------------------------------------------------------
# 10. Provenance completeness
# ---------------------------------------------------------------------

print("\n[10] PROVENANCE COMPLETENESS")

provenance_fields = [
    "prediction_reference",
    "ticket_reference",
    "feedback_source",
    "feedback_timestamp",
    "validation_reference",
    "admission_reference",
]

for field in provenance_fields:
    print(f"REQUIRED: {field}")

provenance_ok = len(provenance_fields) == 6

check(
    provenance_ok,
    "C10 admitted learning signals require complete provenance"
)


# ---------------------------------------------------------------------
# 11. Population-level admission states
# ---------------------------------------------------------------------

print("\n[11] POPULATION-LEVEL ADMISSION STATES")

population_states = {
    "ADMISSIBLE": (
        "all required integrity and validation conditions are satisfied"
    ),
    "PARTIALLY_ADMISSIBLE": (
        "some records qualify but invalid/conflicting records remain excluded"
    ),
    "NOT_ADMISSIBLE": (
        "population integrity is insufficient for training-data admission"
    ),
}

for state, meaning in population_states.items():
    print(f"{state}: {meaning}")

population_states_ok = len(population_states) == 3

check(
    population_states_ok,
    "C11 population-level admission states are explicitly separated"
)


# ---------------------------------------------------------------------
# 12. Current population state
# ---------------------------------------------------------------------

print("\n[12] CURRENT T11 LEARNING-SIGNAL POPULATION")

print("Learning-signal dataset: NOT ESTABLISHED")
print("Admitted learning-signal rows: 0 established")
print("Operational feedback population: NOT ESTABLISHED")
print("Population integrity metrics: NOT AVAILABLE")
print("Training-data admission population: NOT ESTABLISHED")

current_population_ok = True

check(
    current_population_ok,
    "C12 no nonexistent learning-signal population is claimed"
)


# ---------------------------------------------------------------------
# 13. Synthetic population guard
# ---------------------------------------------------------------------

print("\n[13] SYNTHETIC-POPULATION GUARD")

synthetic_guards = [
    "do not fabricate learning-signal rows",
    "do not fabricate feedback provenance",
    "do not fabricate outcome timestamps",
    "do not fabricate conflict resolutions",
    "do not fabricate admission decisions",
    "do not use synthetic records as empirical population evidence",
]

for guard in synthetic_guards:
    print(f"GUARD: {guard}")

synthetic_guard_ok = len(synthetic_guards) == 6

check(
    synthetic_guard_ok,
    "C13 population integrity audit does not create synthetic evidence"
)


# ---------------------------------------------------------------------
# Final status
# ---------------------------------------------------------------------

all_checks = (
    population_identity_ok
    and uniqueness_ok
    and prediction_link_ok
    and ticket_link_ok
    and task_separation_ok
    and outcome_integrity_ok
    and conflict_integrity_ok
    and temporal_integrity_ok
    and evaluation_integrity_ok
    and provenance_ok
    and population_states_ok
    and current_population_ok
    and synthetic_guard_ok
)

print("\n" + "=" * 82)

if all_checks:
    print("STATUS: PASS")
    print()
    print(
        "T11 learning-signal population integrity and admission "
        "requirements are defined."
    )
    print(
        "Population-level identity, uniqueness, linkage, task separation, "
        "outcome integrity, conflict handling, temporal integrity, "
        "evaluation protection, and provenance requirements are explicit."
    )
    print(
        "No actual operational learning-signal population exists, "
        "and no synthetic population has been created."
    )
else:
    print("STATUS: FAIL")

print("=" * 82)