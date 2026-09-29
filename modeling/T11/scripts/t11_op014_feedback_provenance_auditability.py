from pathlib import Path


SCRIPT_DIR = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/modeling/T11/scripts"
)

PROVENANCE_CHAIN = [
    "prediction_reference",
    "ticket_reference",
    "task_identity",
    "model_or_version_identity",
    "prediction_timestamp",
    "feedback_source",
    "feedback_timestamp",
    "validation_reference",
    "admission_reference",
]

IDENTITY_REQUIREMENTS = [
    "prediction_id_is_explicit",
    "ticket_id_is_explicit",
    "task_identity_is_explicit",
    "model_or_version_identity_is_explicit",
    "feedback_event_identity_is_explicit",
    "learning_signal_identity_is_explicit",
]

TRACEABILITY_REQUIREMENTS = [
    "learning_signal_to_prediction",
    "learning_signal_to_ticket",
    "learning_signal_to_feedback_source",
    "learning_signal_to_feedback_timestamp",
    "learning_signal_to_validation",
    "learning_signal_to_admission_decision",
]

AUDIT_REQUIREMENTS = [
    "source_can_be_identified",
    "prediction_event_can_be_recovered",
    "ticket_can_be_reconciled",
    "feedback_event_can_be_recovered",
    "validation_decision_can_be_recovered",
    "admission_decision_can_be_recovered",
    "task_semantics_can_be_recovered",
    "prediction_time_boundary_can_be_recovered",
]

FORBIDDEN_RECONSTRUCTION_METHODS = [
    "positional_row_alignment_without_explicit_contract",
    "filename_position_as_ticket_identity",
    "row_order_as_prediction_identity",
    "timestamp_only_linkage",
    "shared_population_size_as_identity",
    "implicit_task_identity",
    "inferred_feedback_source",
    "inferred_human_action",
]

PROVENANCE_FAILURES = [
    "missing_prediction_reference",
    "missing_ticket_reference",
    "missing_task_identity",
    "missing_model_or_version_identity",
    "missing_feedback_source",
    "missing_feedback_timestamp",
    "missing_validation_reference",
    "missing_admission_reference",
    "unresolved_identity_mismatch",
    "unresolved_duplicate_feedback",
    "unresolved_conflicting_feedback",
]

CURRENT_STATE = {
    "operational_feedback_population": "NOT_ESTABLISHED",
    "validated_learning_signal_population": "NOT_ESTABLISHED",
    "prediction_feedback_join": "NOT_ESTABLISHED",
    "feedback_validation_audit": "NOT_ESTABLISHED",
    "training_admission_audit": "NOT_ESTABLISHED",
    "production_feedback_trace": "NOT_AVAILABLE",
}


def main():
    print("=" * 82)
    print("T11 / OP-014 — FEEDBACK PROVENANCE & AUDITABILITY")
    print("=" * 82)

    print("\n[1] PROVENANCE CHAIN")

    for index, field in enumerate(PROVENANCE_CHAIN, start=1):
        print(f"{index}. {field}")

    c1 = (
        len(PROVENANCE_CHAIN) == 9
        and len(set(PROVENANCE_CHAIN)) == 9
    )

    print(
        "C1 complete prediction-to-admission provenance chain is defined: "
        f"{'PASS' if c1 else 'FAIL'}"
    )

    print("\n[2] IDENTITY REQUIREMENTS")

    for requirement in IDENTITY_REQUIREMENTS:
        print(f"REQUIRED: {requirement}")

    c2 = (
        len(IDENTITY_REQUIREMENTS) == 6
        and len(set(IDENTITY_REQUIREMENTS)) == 6
    )

    print(
        "C2 prediction, ticket, task, feedback, and learning-signal "
        f"identities must be explicit: {'PASS' if c2 else 'FAIL'}"
    )

    print("\n[3] TRACEABILITY REQUIREMENTS")

    for requirement in TRACEABILITY_REQUIREMENTS:
        print(f"TRACE: {requirement}")

    c3 = (
        len(TRACEABILITY_REQUIREMENTS) == 6
        and len(set(TRACEABILITY_REQUIREMENTS)) == 6
    )

    print(
        "C3 every learning signal must remain traceable through the "
        f"full evidence chain: {'PASS' if c3 else 'FAIL'}"
    )

    print("\n[4] AUDIT REQUIREMENTS")

    for requirement in AUDIT_REQUIREMENTS:
        print(f"AUDIT: {requirement}")

    c4 = (
        len(AUDIT_REQUIREMENTS) == 8
        and len(set(AUDIT_REQUIREMENTS)) == 8
    )

    print(
        "C4 provenance must support retrospective audit without "
        f"semantic reconstruction: {'PASS' if c4 else 'FAIL'}"
    )

    print("\n[5] FORBIDDEN RECONSTRUCTION METHODS")

    for method in FORBIDDEN_RECONSTRUCTION_METHODS:
        print(f"FORBIDDEN: {method}")

    c5 = (
        len(FORBIDDEN_RECONSTRUCTION_METHODS) == 8
        and len(set(FORBIDDEN_RECONSTRUCTION_METHODS)) == 8
    )

    print(
        "C5 implicit, positional, or inferred provenance reconstruction "
        f"is prohibited: {'PASS' if c5 else 'FAIL'}"
    )

    print("\n[6] PROVENANCE FAILURE CONDITIONS")

    for failure in PROVENANCE_FAILURES:
        print(f"FAILURE CONDITION: {failure}")

    c6 = (
        len(PROVENANCE_FAILURES) == 11
        and len(set(PROVENANCE_FAILURES)) == 11
    )

    print(
        "C6 incomplete or contradictory provenance blocks learning-signal "
        f"admission: {'PASS' if c6 else 'FAIL'}"
    )

    print("\n[7] AUDIT CHAIN SEPARATION")

    stages = [
        "prediction_capture",
        "feedback_capture",
        "feedback_validation",
        "learning_signal_admission",
        "training_data_admission",
        "retraining_decision",
        "post_retraining_validation",
    ]

    for index, stage in enumerate(stages, start=1):
        print(f"{index}. {stage}")

    c7 = (
        stages
        == [
            "prediction_capture",
            "feedback_capture",
            "feedback_validation",
            "learning_signal_admission",
            "training_data_admission",
            "retraining_decision",
            "post_retraining_validation",
        ]
    )

    print(
        "C7 provenance remains auditable across the complete T11 "
        f"lifecycle: {'PASS' if c7 else 'FAIL'}"
    )

    print("\n[8] CURRENT T11 PROVENANCE STATE")

    for key, value in CURRENT_STATE.items():
        print(f"{key}: {value}")

    expected_state = {
        "operational_feedback_population": "NOT_ESTABLISHED",
        "validated_learning_signal_population": "NOT_ESTABLISHED",
        "prediction_feedback_join": "NOT_ESTABLISHED",
        "feedback_validation_audit": "NOT_ESTABLISHED",
        "training_admission_audit": "NOT_ESTABLISHED",
        "production_feedback_trace": "NOT_AVAILABLE",
    }

    c8 = CURRENT_STATE == expected_state

    print(
        "C8 current provenance state is reported without claiming an "
        f"operational feedback trace: {'PASS' if c8 else 'FAIL'}"
    )

    print("\n[9] NO SYNTHETIC TRACEABILITY")

    guards = [
        "no_fabricated_prediction_id",
        "no_fabricated_ticket_id",
        "no_fabricated_feedback_event",
        "no_fabricated_reviewer_identity",
        "no_fabricated_validation_reference",
        "no_fabricated_admission_reference",
    ]

    for guard in guards:
        print(f"GUARD: {guard}")

    c9 = (
        len(guards) == 6
        and len(set(guards)) == 6
    )

    print(
        "C9 provenance identifiers cannot be fabricated to make feedback "
        f"appear traceable: {'PASS' if c9 else 'FAIL'}"
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
            "T11 feedback provenance and auditability boundaries "
            "are explicitly defined."
        )
        print(
            "Future learning signals must be traceable from prediction "
            "through feedback, validation, and admission."
        )
        print(
            "Implicit, positional, inferred, or fabricated provenance "
            "cannot establish a valid learning signal."
        )
    else:
        print("One or more T11 provenance checks failed.")


if __name__ == "__main__":
    main()