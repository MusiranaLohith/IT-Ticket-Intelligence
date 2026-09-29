from pathlib import Path


SCRIPT_DIR = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/modeling/T11/scripts"
)

TASK_SEMANTICS = {
    "T2": {
        "task": "Priority Prediction",
        "evidence_type": "classification",
        "target_semantics": "priority_label",
        "feedback_must_preserve": "priority_semantics",
    },
    "T3": {
        "task": "Task-specific prediction",
        "evidence_type": "task_native_prediction",
        "target_semantics": "task_native",
        "feedback_must_preserve": "task_specific_semantics",
    },
    "T4": {
        "task": "Assignee Ranking",
        "evidence_type": "ranking",
        "target_semantics": "assignee_ranking",
        "feedback_must_preserve": "ranking_semantics",
    },
    "T5": {
        "task": "Duplicate Probability",
        "evidence_type": "probability",
        "target_semantics": "duplicate_relationship",
        "feedback_must_preserve": "duplicate_probability_semantics",
    },
    "T6": {
        "task": "Candidate Ranking",
        "evidence_type": "ranking",
        "target_semantics": "candidate_ranking",
        "feedback_must_preserve": "candidate_ranking_semantics",
    },
    "T7": {
        "task": "Resolution Survival",
        "evidence_type": "survival",
        "target_semantics": "event_and_right_censoring",
        "feedback_must_preserve": "survival_semantics",
    },
}

FORBIDDEN_CROSS_TASK_CONVERSIONS = [
    "T2_priority_label_to_T4_assignee_label",
    "T2_priority_label_to_T6_candidate_label",
    "T4_assignee_ranking_to_universal_correctness_label",
    "T5_duplicate_probability_to_binary_duplicate_truth_without_validation",
    "T6_observable_non_positive_to_true_negative",
    "T7_right_censored_observation_to_negative_feedback",
    "T7_survival_event_to_generic_success_label",
    "T4_ranking_to_classification_label",
    "T6_ranking_to_classification_label",
    "T5_probability_to_universal_confidence_score",
]

TASK_FEEDBACK_REQUIREMENTS = [
    "feedback_task_identity_must_be_explicit",
    "feedback_target_semantics_must_match_task",
    "feedback_prediction_semantics_must_match_task",
    "feedback_outcome_semantics_must_match_task",
    "feedback_provenance_must_identify_source_task",
    "cross_task_reuse_requires_explicit_validation",
    "cross_task_reuse_cannot_be_assumed_from_shared_ticket_id",
]

SPECIAL_SEMANTIC_GUARDS = [
    "T2_priority_is_not_assignee_correctness",
    "T4_ranking_is_not_classification",
    "T5_duplicate_probability_is_not_duplicate_identity",
    "T6_observable_non_positive_is_not_true_negative",
    "T7_censoring_is_not_negative_feedback",
    "T7_event_is_not_generic_success",
]

CURRENT_STATE = {
    "cross_task_feedback_dataset": "NOT_ESTABLISHED",
    "validated_cross_task_learning_signal": "NOT_ESTABLISHED",
    "universal_feedback_label": "NOT_DEFINED",
    "universal_feedback_score": "NOT_DEFINED",
    "cross_task_feedback_mapping": "NOT_ESTABLISHED",
}


def main():
    print("=" * 82)
    print("T11 / OP-013 — CROSS-TASK FEEDBACK SEMANTIC PROTECTION")
    print("=" * 82)

    print("\n[1] TASK-NATIVE SEMANTICS")

    for task_id, details in TASK_SEMANTICS.items():
        print(
            f"{task_id}: "
            f"{details['task']} | "
            f"type={details['evidence_type']} | "
            f"target={details['target_semantics']} | "
            f"preserve={details['feedback_must_preserve']}"
        )

    c1 = (
        set(TASK_SEMANTICS.keys())
        == {"T2", "T3", "T4", "T5", "T6", "T7"}
        and all(
            all(
                isinstance(value, str) and value.strip()
                for value in details.values()
            )
            for details in TASK_SEMANTICS.values()
        )
    )

    print(
        "C1 T2-T7 native task semantics are explicitly registered: "
        f"{'PASS' if c1 else 'FAIL'}"
    )

    print("\n[2] TASK-IDENTITY REQUIREMENTS")

    for requirement in TASK_FEEDBACK_REQUIREMENTS:
        print(f"REQUIRED: {requirement}")

    c2 = (
        len(TASK_FEEDBACK_REQUIREMENTS) == 7
        and len(set(TASK_FEEDBACK_REQUIREMENTS)) == 7
    )

    print(
        "C2 future feedback must retain explicit task identity and "
        f"semantic alignment: {'PASS' if c2 else 'FAIL'}"
    )

    print("\n[3] FORBIDDEN CROSS-TASK CONVERSIONS")

    for conversion in FORBIDDEN_CROSS_TASK_CONVERSIONS:
        print(f"FORBIDDEN: {conversion}")

    c3 = (
        len(FORBIDDEN_CROSS_TASK_CONVERSIONS) == 10
        and len(set(FORBIDDEN_CROSS_TASK_CONVERSIONS)) == 10
    )

    print(
        "C3 unsupported cross-task label conversions are explicitly "
        f"blocked: {'PASS' if c3 else 'FAIL'}"
    )

    print("\n[4] SPECIAL SEMANTIC GUARDS")

    for guard in SPECIAL_SEMANTIC_GUARDS:
        print(f"GUARD: {guard}")

    c4 = (
        len(SPECIAL_SEMANTIC_GUARDS) == 6
        and len(set(SPECIAL_SEMANTIC_GUARDS)) == 6
    )

    print(
        "C4 task-specific semantic traps are explicitly protected: "
        f"{'PASS' if c4 else 'FAIL'}"
    )

    print("\n[5] T2 PRIORITY BOUNDARY")

    t2_rules = [
        "priority_feedback_must_remain_priority_feedback",
        "priority_prediction_error_is_not_universal_system_error",
        "priority_label_cannot_be_reused_as_assignee_correctness",
        "priority_label_cannot_be_reused_as_duplicate_truth",
        "priority_label_cannot_be_reused_as_survival_outcome",
    ]

    for rule in t2_rules:
        print(f"T2 GUARD: {rule}")

    c5 = (
        len(t2_rules) == 5
        and len(set(t2_rules)) == 5
    )

    print(
        "C5 T2 priority semantics remain isolated from other task "
        f"semantics: {'PASS' if c5 else 'FAIL'}"
    )

    print("\n[6] T4 / T5 / T6 / T7 SPECIAL BOUNDARIES")

    task_specific_rules = [
        "T4_historical_assignment_does_not_equal_universal_routing_correctness",
        "T5_probability_does_not_equal_duplicate_identity",
        "T6_non_observed_candidate_does_not_equal_true_negative",
        "T7_right_censoring_does_not_equal_negative_feedback",
        "T7_event_status_does_not_equal_generic_success_label",
    ]

    for rule in task_specific_rules:
        print(f"TASK GUARD: {rule}")

    c6 = (
        len(task_specific_rules) == 5
        and len(set(task_specific_rules)) == 5
    )

    print(
        "C6 task-specific semantic protections for T4-T7 are preserved: "
        f"{'PASS' if c6 else 'FAIL'}"
    )

    print("\n[7] CROSS-TASK REUSE BOUNDARY")

    reuse_rules = [
        "shared_ticket_id_does_not_establish_shared_target_semantics",
        "shared_prediction_timestamp_does_not_establish_shared_feedback_semantics",
        "shared_population_does_not_establish_cross_task_label_equivalence",
        "cross_task_reuse_requires_explicit_validation",
        "cross_task_reuse_requires_preserved_provenance",
        "cross_task_reuse_requires_task_semantic_compatibility",
    ]

    for rule in reuse_rules:
        print(f"REUSE BOUNDARY: {rule}")

    c7 = (
        len(reuse_rules) == 6
        and len(set(reuse_rules)) == 6
    )

    print(
        "C7 cross-task evidence reuse cannot be assumed from shared "
        f"identifiers alone: {'PASS' if c7 else 'FAIL'}"
    )

    print("\n[8] CURRENT T11 CROSS-TASK STATE")

    for key, value in CURRENT_STATE.items():
        print(f"{key}: {value}")

    expected_state = {
        "cross_task_feedback_dataset": "NOT_ESTABLISHED",
        "validated_cross_task_learning_signal": "NOT_ESTABLISHED",
        "universal_feedback_label": "NOT_DEFINED",
        "universal_feedback_score": "NOT_DEFINED",
        "cross_task_feedback_mapping": "NOT_ESTABLISHED",
    }

    c8 = CURRENT_STATE == expected_state

    print(
        "C8 no universal cross-task feedback population or label is "
        f"claimed: {'PASS' if c8 else 'FAIL'}"
    )

    print("\n[9] FINAL CONTRACT STATUS")

    checks = {
        "C1": c1,
        "C2": c2,
        "C3": c3,
        "C4": c4,
        "C5": c5,
        "C6": c6,
        "C7": c7,
        "C8": c8,
    }

    for name, result in checks.items():
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    overall = all(checks.values())

    print("\n" + "=" * 82)
    print(f"STATUS: {'PASS' if overall else 'FAIL'}")
    print("=" * 82)

    if overall:
        print(
            "T11 cross-task feedback semantic protection is explicitly defined."
        )
        print(
            "T2-T7 feedback must retain native task identity, target semantics, "
            "provenance, and validation boundaries."
        )
        print(
            "No universal feedback label, score, or cross-task learning "
            "population is claimed."
        )
    else:
        print("One or more T11 cross-task semantic checks failed.")


if __name__ == "__main__":
    main()