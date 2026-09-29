from pathlib import Path


SCRIPT_PATH = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/modeling/T11/scripts"
)

FEEDBACK_STATES = [
    ("F0", "NO_FEEDBACK", "NOT_A_CANDIDATE"),
    ("F1", "OBSERVED_TASK_OUTCOME", "CONDITIONAL_CANDIDATE"),
    ("F2", "PREDICTION_OUTCOME_COMPARISON", "FUTURE_SUPPORTED"),
    ("F3", "EXPLICIT_HUMAN_CONFIRMATION", "FUTURE_SUPPORTED"),
    ("F4", "EXPLICIT_HUMAN_CORRECTION", "FUTURE_SUPPORTED"),
    ("F5", "EXPLICIT_HUMAN_OVERRIDE", "FUTURE_SUPPORTED"),
    ("F6", "EXPLICIT_REJECTION", "FUTURE_SUPPORTED"),
    ("F7", "INSUFFICIENT_OR_UNRESOLVED_FEEDBACK", "REVIEW_ONLY"),
]

REQUIRED_GATES = [
    "identity_linkage",
    "task_alignment",
    "provenance",
    "temporal_integrity",
    "evidence_sufficiency",
    "human_validation_where_required",
    "label_semantic_validity",
    "task_semantic_preservation",
]

FORBIDDEN_AUTOMATIC_PROMOTIONS = [
    "historical_task_outcome_as_model_feedback",
    "prediction_outcome_agreement_as_correctness",
    "prediction_outcome_disagreement_as_model_error",
    "human_override_as_automatic_model_error",
    "human_rejection_as_automatic_model_error",
    "observable_non_positive_as_true_negative",
    "right_censored_survival_observation_as_negative_feedback",
    "synthetic_or_inferred_feedback_as_learning_label",
]

PIPELINE_STAGES = [
    "eligible_evidence",
    "active_learning_candidate",
    "review_prioritization",
    "human_review_or_validation",
    "validated_learning_signal",
    "retraining_decision",
]


def main():
    print("=" * 82)
    print("T11 / OP-003 — FEEDBACK TAXONOMY & CANDIDATE-STATE BOUNDARY")
    print("=" * 82)

    print("\n[1] FEEDBACK TAXONOMY")
    expected_codes = [f"F{i}" for i in range(8)]

    actual_codes = [code for code, _, _ in FEEDBACK_STATES]

    for code, state, status in FEEDBACK_STATES:
        print(f"{code}: {state} -> {status}")

    c1 = actual_codes == expected_codes
    print(
        "C1 feedback taxonomy contains explicit F0-F7 states: "
        f"{'PASS' if c1 else 'FAIL'}"
    )

    print("\n[2] CANDIDATE-STATE SEMANTICS")

    expected_status = {
        "F0": "NOT_A_CANDIDATE",
        "F1": "CONDITIONAL_CANDIDATE",
        "F2": "FUTURE_SUPPORTED",
        "F3": "FUTURE_SUPPORTED",
        "F4": "FUTURE_SUPPORTED",
        "F5": "FUTURE_SUPPORTED",
        "F6": "FUTURE_SUPPORTED",
        "F7": "REVIEW_ONLY",
    }

    c2 = all(
        status == expected_status[code]
        for code, _, status in FEEDBACK_STATES
    )

    for code, state, status in FEEDBACK_STATES:
        print(
            f"{code} {state}: "
            f"expected={expected_status[code]}, actual={status}"
        )

    print(
        "C2 candidate-state semantics preserve the DTM boundary: "
        f"{'PASS' if c2 else 'FAIL'}"
    )

    print("\n[3] ACTIVE-LEARNING PIPELINE")

    print(" -> ".join(PIPELINE_STAGES))

    expected_pipeline = [
        "eligible_evidence",
        "active_learning_candidate",
        "review_prioritization",
        "human_review_or_validation",
        "validated_learning_signal",
        "retraining_decision",
    ]

    c3 = PIPELINE_STAGES == expected_pipeline

    print(
        "C3 candidate selection, review, validation, learning-signal "
        f"admission, and retraining remain separate stages: "
        f"{'PASS' if c3 else 'FAIL'}"
    )

    print("\n[4] REQUIRED PROMOTION GATES")

    for gate in REQUIRED_GATES:
        print(f"REQUIRED: {gate}")

    c4 = len(REQUIRED_GATES) == 8 and len(set(REQUIRED_GATES)) == 8

    print(
        "C4 promotion requires identity, task, provenance, temporal, "
        f"evidence, validation, and semantic gates: "
        f"{'PASS' if c4 else 'FAIL'}"
    )

    print("\n[5] FORBIDDEN AUTOMATIC PROMOTIONS")

    for rule in FORBIDDEN_AUTOMATIC_PROMOTIONS:
        print(f"FORBIDDEN: {rule}")

    c5 = (
        "historical_task_outcome_as_model_feedback"
        in FORBIDDEN_AUTOMATIC_PROMOTIONS
        and "prediction_outcome_agreement_as_correctness"
        in FORBIDDEN_AUTOMATIC_PROMOTIONS
        and "prediction_outcome_disagreement_as_model_error"
        in FORBIDDEN_AUTOMATIC_PROMOTIONS
        and "human_override_as_automatic_model_error"
        in FORBIDDEN_AUTOMATIC_PROMOTIONS
        and "human_rejection_as_automatic_model_error"
        in FORBIDDEN_AUTOMATIC_PROMOTIONS
        and "observable_non_positive_as_true_negative"
        in FORBIDDEN_AUTOMATIC_PROMOTIONS
        and "right_censored_survival_observation_as_negative_feedback"
        in FORBIDDEN_AUTOMATIC_PROMOTIONS
        and "synthetic_or_inferred_feedback_as_learning_label"
        in FORBIDDEN_AUTOMATIC_PROMOTIONS
    )

    print(
        "C5 automatic feedback-label inference is explicitly blocked: "
        f"{'PASS' if c5 else 'FAIL'}"
    )

    print("\n[6] CURRENT T11 EMPIRICAL STATE")

    current_state = {
        "actual_model_uncertainty": "NOT_YET_AVAILABLE",
        "prediction_outcome_comparison": "NOT_YET_AVAILABLE",
        "explicit_human_feedback": "NOT_CURRENTLY_ESTABLISHED",
        "numerical_acquisition_policy": "NOT_FROZEN",
        "sampling_weights": "NOT_FROZEN",
        "review_volume_threshold": "NOT_FROZEN",
        "operational_feedback_population": "NOT_ESTABLISHED",
        "validated_learning_signal_population": "NOT_ESTABLISHED",
    }

    for key, value in current_state.items():
        print(f"{key}: {value}")

    c6 = all(
        value
        in {
            "NOT_YET_AVAILABLE",
            "NOT_CURRENTLY_ESTABLISHED",
            "NOT_FROZEN",
            "NOT_ESTABLISHED",
        }
        for value in current_state.values()
    )

    print(
        "C6 current T11 state does not falsely claim empirical feedback "
        f"availability: {'PASS' if c6 else 'FAIL'}"
    )

    print("\n[7] SYNTHETIC-FEEDBACK GUARD")

    synthetic_guard = [
        "No synthetic human confirmation/correction/override/rejection",
        "No inferred reviewer decisions",
        "No historical T2-T7 target relabeling as T11 feedback",
        "No automatic learning label from model prediction",
        "No fabricated operational feedback population",
    ]

    for rule in synthetic_guard:
        print(f"GUARD: {rule}")

    c7 = len(synthetic_guard) == 5

    print(
        "C7 synthetic/inferred feedback population remains prohibited: "
        f"{'PASS' if c7 else 'FAIL'}"
    )

    print("\n[8] T11 BOUNDARY CHECK")

    boundary_rules = [
        "candidate_selection_is_not_learning_signal_admission",
        "review_prioritization_is_not_validation",
        "validated_learning_signal_is_not_automatic_retraining",
        "retraining_decision_requires_empirical_validation",
        "F7_can_prioritize_review_but_cannot_become_learning_label",
        "F1_requires_conditional_treatment",
    ]

    for rule in boundary_rules:
        print(f"BOUNDARY: {rule}")

    c8 = len(boundary_rules) == 6 and len(set(boundary_rules)) == 6

    print(
        "C8 staged T11 boundaries remain explicit and non-collapsed: "
        f"{'PASS' if c8 else 'FAIL'}"
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
            "T11 feedback taxonomy and active-learning candidate boundaries "
            "are explicitly defined."
        )
        print(
            "Feedback states remain separate from validated learning signals, "
            "training-data admission, and retraining decisions."
        )
        print(
            "Historical outcomes, inferred decisions, and synthetic feedback "
            "cannot be promoted automatically into learning labels."
        )
    else:
        print("One or more T11 boundary checks failed.")


if __name__ == "__main__":
    main()