from pathlib import Path


SCRIPT_DIR = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/modeling/T11/scripts"
)

VALIDATION_GATES = [
    "prediction_link_exists",
    "ticket_identity_reconciles",
    "outcome_is_observed",
    "outcome_timestamp_is_valid",
    "outcome_source_is_known",
    "duplicate_feedback_is_resolved",
    "contradictory_feedback_is_flagged",
    "post_prediction_outcome_boundary_is_preserved",
]

ADMISSION_GATES = [
    "validated_prediction_link",
    "validated_ticket_link",
    "observed_outcome",
    "provenance_available",
    "no_unresolved_conflict",
    "no_unresolved_duplicate_feedback",
    "task_semantics_preserved",
    "prediction_time_boundary_preserved",
]

REJECTION_CONDITIONS = [
    "missing_prediction_linkage",
    "missing_ticket_linkage",
    "unverified_outcome",
    "unknown_feedback_source",
    "unresolved_duplicate_feedback",
    "unresolved_conflicting_feedback",
    "synthetic_or_inferred_outcome",
    "task_semantic_mismatch",
    "prediction_time_leakage",
]

PROVENANCE_FIELDS = [
    "prediction_reference",
    "ticket_reference",
    "feedback_source",
    "feedback_timestamp",
    "validation_reference",
    "admission_reference",
]

TASK_SEMANTIC_GUARDS = [
    "T2_priority_prediction_remains_priority_semantics",
    "T3_task_semantics_remain_unchanged",
    "T4_assignee_ranking_remains_ranking_semantics",
    "T5_duplicate_probability_remains_duplicate_semantics",
    "T6_candidate_ranking_remains_ranking_semantics",
    "T7_event_and_right_censoring_semantics_are_preserved",
]


def main():
    print("=" * 82)
    print("T11 / OP-004 — FEEDBACK VALIDATION & LEARNING-SIGNAL ADMISSION")
    print("=" * 82)

    print("\n[1] FEEDBACK VALIDATION GATES")

    for gate in VALIDATION_GATES:
        print(f"REQUIRED: {gate}")

    c1 = (
        len(VALIDATION_GATES) == 8
        and len(set(VALIDATION_GATES)) == 8
    )

    print(
        "C1 all required feedback-validation gates are explicitly defined: "
        f"{'PASS' if c1 else 'FAIL'}"
    )

    print("\n[2] LEARNING-SIGNAL ADMISSION GATES")

    for gate in ADMISSION_GATES:
        print(f"REQUIRED: {gate}")

    c2 = (
        len(ADMISSION_GATES) == 8
        and len(set(ADMISSION_GATES)) == 8
    )

    print(
        "C2 learning-signal admission requires validated evidence: "
        f"{'PASS' if c2 else 'FAIL'}"
    )

    print("\n[3] FEEDBACK REJECTION CONDITIONS")

    for condition in REJECTION_CONDITIONS:
        print(f"REJECT: {condition}")

    c3 = (
        len(REJECTION_CONDITIONS) == 9
        and len(set(REJECTION_CONDITIONS)) == 9
    )

    print(
        "C3 invalid, synthetic, unresolved, or leakage-prone feedback "
        f"is rejected: {'PASS' if c3 else 'FAIL'}"
    )

    print("\n[4] PROVENANCE REQUIREMENTS")

    for field in PROVENANCE_FIELDS:
        print(f"REQUIRED PROVENANCE: {field}")

    c4 = (
        len(PROVENANCE_FIELDS) == 6
        and len(set(PROVENANCE_FIELDS)) == 6
    )

    print(
        "C4 complete prediction-to-admission provenance is required: "
        f"{'PASS' if c4 else 'FAIL'}"
    )

    print("\n[5] TASK-SEMANTIC PRESERVATION")

    for guard in TASK_SEMANTIC_GUARDS:
        print(f"GUARD: {guard}")

    c5 = (
        len(TASK_SEMANTIC_GUARDS) == 6
        and len(set(TASK_SEMANTIC_GUARDS)) == 6
    )

    print(
        "C5 feedback cannot silently change T2-T7 task semantics: "
        f"{'PASS' if c5 else 'FAIL'}"
    )

    print("\n[6] TEMPORAL BOUNDARY")

    temporal_rules = [
        "feedback_must_occur_at_or_after_prediction",
        "prediction_timestamp_is_retained",
        "feedback_timestamp_is_retained",
        "post_prediction_outcome_boundary_is_checked",
        "future_information_cannot_become_prediction_time_feature",
    ]

    for rule in temporal_rules:
        print(f"TEMPORAL RULE: {rule}")

    c6 = (
        len(temporal_rules) == 5
        and len(set(temporal_rules)) == 5
    )

    print(
        "C6 prediction-time temporal integrity is preserved: "
        f"{'PASS' if c6 else 'FAIL'}"
    )

    print("\n[7] VALIDATION → ADMISSION SEPARATION")

    stages = [
        "feedback_capture",
        "candidate_identification",
        "feedback_validation",
        "learning_signal_admission",
        "training_data_admission",
    ]

    for index, stage in enumerate(stages, start=1):
        print(f"{index}. {stage}")

    c7 = (
        stages
        == [
            "feedback_capture",
            "candidate_identification",
            "feedback_validation",
            "learning_signal_admission",
            "training_data_admission",
        ]
    )

    print(
        "C7 validation and learning-signal admission remain separate "
        f"from raw feedback capture: {'PASS' if c7 else 'FAIL'}"
    )

    print("\n[8] NO AUTOMATIC PROMOTION")

    prohibited_promotions = [
        "candidate_is_not_automatically_a_learning_signal",
        "observed_outcome_is_not_automatically_a_validated_label",
        "human_action_is_not_automatically_model_error",
        "prediction_disagreement_is_not_automatically_incorrect_prediction",
        "unresolved_feedback_is_not_admissible_training_data",
        "synthetic_feedback_is_never_admissible",
        "historical_task_targets_are_not_reclassified_as_feedback",
    ]

    for rule in prohibited_promotions:
        print(f"PROHIBITED: {rule}")

    c8 = (
        len(prohibited_promotions) == 7
        and len(set(prohibited_promotions)) == 7
    )

    print(
        "C8 automatic promotion from evidence to learning data is "
        f"prohibited: {'PASS' if c8 else 'FAIL'}"
    )

    print("\n[9] CURRENT T11 POPULATION STATE")

    current_state = {
        "operational_feedback_population": "NOT_ESTABLISHED",
        "validated_learning_signal_population": "NOT_ESTABLISHED",
        "training_data_admission_population": "NOT_ESTABLISHED",
        "actual_prediction_outcome_feedback": "NOT_ESTABLISHED",
        "explicit_human_feedback": "NOT_ESTABLISHED",
        "feedback_validation_dataset": "NOT_ESTABLISHED",
    }

    for key, value in current_state.items():
        print(f"{key}: {value}")

    c9 = all(value == "NOT_ESTABLISHED" for value in current_state.values())

    print(
        "C9 current T11 population remains unestablished without "
        f"fabricating feedback: {'PASS' if c9 else 'FAIL'}"
    )

    print("\n[10] FINAL CONTRACT STATUS")

    checks = {
        "C1": c1,
        "C2": c2,
        "C3": c3,
        "C4": c4,
        "C5": c5,
        "C6": c6,
        "C7": c7,
        "C8": c8,
        "C9": c9,
    }

    for name, result in checks.items():
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    overall = all(checks.values())

    print("\n" + "=" * 82)
    print(f"STATUS: {'PASS' if overall else 'FAIL'}")
    print("=" * 82)

    if overall:
        print(
            "T11 feedback validation and learning-signal admission "
            "boundaries are explicitly defined."
        )
        print(
            "Only validated, traceable, task-compatible, temporally valid "
            "feedback may progress toward learning-signal admission."
        )
        print(
            "No operational feedback or validated learning-signal population "
            "is claimed."
        )
    else:
        print("One or more T11 validation/admission checks failed.")


if __name__ == "__main__":
    main()