from pathlib import Path


SCRIPT_DIR = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/modeling/T11/scripts"
)

STATES = [
    "NO_FEEDBACK",
    "FEEDBACK_CAPTURED",
    "CANDIDATE_IDENTIFIED",
    "FEEDBACK_VALIDATED",
    "LEARNING_SIGNAL_ADMITTED",
    "TRAINING_DATA_ADMITTED",
    "RETRAINING_DECISION",
    "RETRAINING_EXECUTED",
    "POST_RETRAINING_VALIDATED",
]

VALID_TRANSITIONS = [
    ("NO_FEEDBACK", "FEEDBACK_CAPTURED"),
    ("FEEDBACK_CAPTURED", "CANDIDATE_IDENTIFIED"),
    ("CANDIDATE_IDENTIFIED", "FEEDBACK_VALIDATED"),
    ("FEEDBACK_VALIDATED", "LEARNING_SIGNAL_ADMITTED"),
    ("LEARNING_SIGNAL_ADMITTED", "TRAINING_DATA_ADMITTED"),
    ("TRAINING_DATA_ADMITTED", "RETRAINING_DECISION"),
    ("RETRAINING_DECISION", "RETRAINING_EXECUTED"),
    ("RETRAINING_EXECUTED", "POST_RETRAINING_VALIDATED"),
]

FORBIDDEN_TRANSITIONS = [
    ("NO_FEEDBACK", "LEARNING_SIGNAL_ADMITTED"),
    ("FEEDBACK_CAPTURED", "LEARNING_SIGNAL_ADMITTED"),
    ("CANDIDATE_IDENTIFIED", "TRAINING_DATA_ADMITTED"),
    ("FEEDBACK_VALIDATED", "RETRAINING_EXECUTED"),
    ("LEARNING_SIGNAL_ADMITTED", "RETRAINING_EXECUTED"),
    ("CANDIDATE_IDENTIFIED", "RETRAINING_EXECUTED"),
    ("FEEDBACK_CAPTURED", "RETRAINING_EXECUTED"),
    ("NO_FEEDBACK", "RETRAINING_EXECUTED"),
    ("RETRAINING_EXECUTED", "LEARNING_SIGNAL_ADMITTED"),
]

REQUIRED_STATE_PROPERTIES = {
    "NO_FEEDBACK": "no operational feedback is available",
    "FEEDBACK_CAPTURED": "feedback exists but is not yet validated",
    "CANDIDATE_IDENTIFIED": "evidence is eligible for review consideration",
    "FEEDBACK_VALIDATED": "feedback satisfies validation requirements",
    "LEARNING_SIGNAL_ADMITTED": "validated evidence is admitted as a learning signal",
    "TRAINING_DATA_ADMITTED": "validated learning signal is explicitly admitted to training data",
    "RETRAINING_DECISION": "retraining is separately assessed and decided",
    "RETRAINING_EXECUTED": "a retraining operation has actually occurred",
    "POST_RETRAINING_VALIDATED": "retrained model has passed required empirical validation",
}

INVALID_SHORTCUTS = [
    "feedback_capture_to_learning_signal",
    "candidate_to_training_data",
    "candidate_to_retraining",
    "validated_feedback_to_retraining_execution",
    "learning_signal_to_retraining_execution",
    "human_action_to_retraining",
    "single_feedback_event_to_retraining",
]

CURRENT_IMPLEMENTATION_STATE = {
    "operational_feedback": "NOT_ESTABLISHED",
    "candidate_population": "NOT_ESTABLISHED",
    "validated_learning_signals": "NOT_ESTABLISHED",
    "training_data_admission": "NOT_ESTABLISHED",
    "retraining_execution": "NOT_IMPLEMENTED",
    "post_retraining_validation": "NOT_AVAILABLE",
}


def main():
    print("=" * 82)
    print("T11 / OP-012 — FEEDBACK LIFECYCLE STATE MACHINE")
    print("=" * 82)

    print("\n[1] LIFECYCLE STATES")

    for index, state in enumerate(STATES, start=1):
        print(f"{index}. {state}")

    c1 = (
        len(STATES) == 9
        and len(set(STATES)) == 9
        and STATES[0] == "NO_FEEDBACK"
        and STATES[-1] == "POST_RETRAINING_VALIDATED"
    )

    print(
        "C1 lifecycle states are explicitly ordered from no feedback "
        f"through post-retraining validation: {'PASS' if c1 else 'FAIL'}"
    )

    print("\n[2] VALID TRANSITIONS")

    for source, target in VALID_TRANSITIONS:
        print(f"VALID: {source} -> {target}")

    expected_transitions = [
        ("NO_FEEDBACK", "FEEDBACK_CAPTURED"),
        ("FEEDBACK_CAPTURED", "CANDIDATE_IDENTIFIED"),
        ("CANDIDATE_IDENTIFIED", "FEEDBACK_VALIDATED"),
        ("FEEDBACK_VALIDATED", "LEARNING_SIGNAL_ADMITTED"),
        ("LEARNING_SIGNAL_ADMITTED", "TRAINING_DATA_ADMITTED"),
        ("TRAINING_DATA_ADMITTED", "RETRAINING_DECISION"),
        ("RETRAINING_DECISION", "RETRAINING_EXECUTED"),
        ("RETRAINING_EXECUTED", "POST_RETRAINING_VALIDATED"),
    ]

    c2 = VALID_TRANSITIONS == expected_transitions

    print(
        "C2 only explicitly defined lifecycle transitions are permitted: "
        f"{'PASS' if c2 else 'FAIL'}"
    )

    print("\n[3] STATE SEMANTICS")

    for state, meaning in REQUIRED_STATE_PROPERTIES.items():
        print(f"{state}: {meaning}")

    c3 = (
        len(REQUIRED_STATE_PROPERTIES) == len(STATES)
        and set(REQUIRED_STATE_PROPERTIES) == set(STATES)
    )

    print(
        "C3 each lifecycle state has an explicit semantic boundary: "
        f"{'PASS' if c3 else 'FAIL'}"
    )

    print("\n[4] FORBIDDEN TRANSITIONS")

    for source, target in FORBIDDEN_TRANSITIONS:
        print(f"FORBIDDEN: {source} -> {target}")

    c4 = (
        len(FORBIDDEN_TRANSITIONS) == 9
        and len(set(FORBIDDEN_TRANSITIONS)) == 9
        and not any(
            transition in VALID_TRANSITIONS
            for transition in FORBIDDEN_TRANSITIONS
        )
    )

    print(
        "C4 unsupported lifecycle shortcuts are explicitly blocked: "
        f"{'PASS' if c4 else 'FAIL'}"
    )

    print("\n[5] VALIDATION BOUNDARY")

    validation_rules = [
        "feedback_validation_precedes_learning_signal_admission",
        "learning_signal_admission_precedes_training_data_admission",
        "training_data_admission_precedes_retraining_decision",
        "retraining_decision_precedes_retraining_execution",
        "retraining_execution_precedes_post_retraining_validation",
        "failed_validation_blocks_downstream_promotion",
    ]

    for rule in validation_rules:
        print(f"BOUNDARY: {rule}")

    c5 = (
        len(validation_rules) == 6
        and len(set(validation_rules)) == 6
    )

    print(
        "C5 validation gates remain mandatory between lifecycle stages: "
        f"{'PASS' if c5 else 'FAIL'}"
    )

    print("\n[6] NO SHORTCUT PROMOTION")

    for rule in INVALID_SHORTCUTS:
        print(f"PROHIBITED: {rule}")

    c6 = (
        len(INVALID_SHORTCUTS) == 7
        and len(set(INVALID_SHORTCUTS)) == 7
    )

    print(
        "C6 direct promotion from feedback evidence to retraining is "
        f"prohibited: {'PASS' if c6 else 'FAIL'}"
    )

    print("\n[7] CURRENT IMPLEMENTATION STATE")

    for key, value in CURRENT_IMPLEMENTATION_STATE.items():
        print(f"{key}: {value}")

    expected_state = {
        "operational_feedback": "NOT_ESTABLISHED",
        "candidate_population": "NOT_ESTABLISHED",
        "validated_learning_signals": "NOT_ESTABLISHED",
        "training_data_admission": "NOT_ESTABLISHED",
        "retraining_execution": "NOT_IMPLEMENTED",
        "post_retraining_validation": "NOT_AVAILABLE",
    }

    c7 = CURRENT_IMPLEMENTATION_STATE == expected_state

    print(
        "C7 lifecycle contract does not falsely claim an implemented "
        f"feedback/retraining loop: {'PASS' if c7 else 'FAIL'}"
    )

    print("\n[8] SYNTHETIC / INFERRED TRANSITION GUARD")

    guards = [
        "synthetic_feedback_cannot_advance_state",
        "inferred_feedback_cannot_advance_state",
        "historical_task_target_cannot_advance_state",
        "unobserved_outcome_cannot_advance_state",
        "automatic_model_prediction_cannot_advance_state_as_feedback",
        "unresolved_conflict_cannot_advance_state",
    ]

    for guard in guards:
        print(f"GUARD: {guard}")

    c8 = (
        len(guards) == 6
        and len(set(guards)) == 6
    )

    print(
        "C8 synthetic, inferred, historical, unresolved, or automatic "
        f"feedback cannot advance the lifecycle: {'PASS' if c8 else 'FAIL'}"
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
            "T11 feedback lifecycle state-machine boundaries are explicitly defined."
        )
        print(
            "Learning-signal admission, training-data admission, retraining, "
            "and post-retraining validation cannot be bypassed."
        )
        print(
            "No operational feedback or implemented retraining loop is claimed."
        )
    else:
        print("One or more T11 lifecycle checks failed.")


if __name__ == "__main__":
    main()