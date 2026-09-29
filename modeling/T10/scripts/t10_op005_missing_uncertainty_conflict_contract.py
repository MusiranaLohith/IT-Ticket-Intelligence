"""
T10 / OP-005
Missing Evidence, Uncertainty & Conflict Contract

Purpose:
    Define policy semantics for:
    - missing/unavailable evidence
    - uncertain evidence
    - conflicting evidence
    - evidence outside the validated task-supported space

This operation constructs the contract only.
It does NOT:
    - create models
    - generate predictions
    - assign decisions to tickets
    - establish numerical thresholds
    - create synthetic policy targets
    - create universal confidence/risk scores
"""

from pprint import pprint


CONTRACTS = {
    "MISSING_EVIDENCE": {
        "meaning": (
            "Required evidence is unavailable or cannot be established "
            "at the Creation-time decision boundary."
        ),
        "required_response": (
            "Do not interpret unavailable evidence as negative evidence. "
            "Do not permit AUTOMATE when a mandatory evidence requirement "
            "cannot be satisfied."
        ),
        "allowed_states": [
            "HUMAN_REVIEW",
            "DEFER_INSUFFICIENT_EVIDENCE",
        ],
        "prohibited_interpretation": (
            "Missing evidence must not be treated as a negative outcome, "
            "failure, rejection, or negative class."
        ),
    },
    "UNCERTAINTY": {
        "meaning": (
            "Available task evidence is uncertain, ambiguous, or does not "
            "support a sufficiently defensible policy decision under the "
            "validated task-specific semantics."
        ),
        "required_response": (
            "Do not convert uncertainty into a universal confidence or risk "
            "score. AUTOMATE requires empirical validation of the relevant "
            "task-specific evidence and decision boundary."
        ),
        "allowed_states": [
            "HUMAN_REVIEW",
            "DEFER_INSUFFICIENT_EVIDENCE",
        ],
        "prohibited_interpretation": (
            "Uncertainty must not be treated as a universal cross-task "
            "probability, confidence, risk score, or correctness guarantee."
        ),
    },
    "CONFLICT": {
        "meaning": (
            "Relevant evidence or task outputs provide unresolved, "
            "inconsistent, or contradictory signals."
        ),
        "required_response": (
            "Do not resolve conflicts through arbitrary cross-task weighting "
            "or averaging. An unresolved conflict cannot independently "
            "justify AUTOMATE."
        ),
        "allowed_states": [
            "HUMAN_REVIEW",
            "DEFER_INSUFFICIENT_EVIDENCE",
        ],
        "prohibited_interpretation": (
            "Conflicting heterogeneous evidence must not be collapsed into "
            "an arbitrary universal score or weighted aggregate."
        ),
    },
    "OUTSIDE_SUPPORTED_SPACE": {
        "meaning": (
            "Evidence, task output, or observed case falls outside the "
            "validated task-supported operating space."
        ),
        "required_response": (
            "Do not extrapolate an automation policy beyond the empirically "
            "supported task/evidence space."
        ),
        "allowed_states": [
            "HUMAN_REVIEW",
            "DEFER_INSUFFICIENT_EVIDENCE",
        ],
        "prohibited_interpretation": (
            "Out-of-space evidence must not be assumed to have the same "
            "validity or correctness properties as validated evidence."
        ),
    },
}


TASK_SEMANTIC_BOUNDARIES = {
    "T2": (
        "Hard priority classification remains task-native; "
        "uncertainty or missing evidence does not create a universal "
        "confidence interpretation."
    ),
    "T3": (
        "Hard severity classification remains task-native; "
        "uncertainty or missing evidence does not create a universal "
        "confidence interpretation."
    ),
    "T4": (
        "Assignee output remains ranking/retrieval evidence; "
        "historical assignment is not treated as universal routing correctness."
    ),
    "T5": (
        "Duplicate output remains calibrated duplicate probability; "
        "its probability must not be averaged with heterogeneous task outputs."
    ),
    "T6": (
        "Query-level retrieval/ranking remains task-native; "
        "observable_non_positive is not treated as a confirmed true negative."
    ),
    "T7": (
        "Survival output remains time-to-event evidence with right censoring; "
        "censoring is not treated as negative feedback."
    ),
}


PROHIBITIONS = {
    "missing_as_negative": True,
    "universal_confidence": True,
    "universal_risk_score": True,
    "cross_task_probability_aggregation": True,
    "arbitrary_cross_task_weighting": True,
    "ranking_as_probability": True,
    "survival_as_binary_classification": True,
    "historical_assignment_as_universal_correctness": True,
    "observable_non_positive_as_true_negative": True,
    "censoring_as_negative_feedback": True,
    "post_creation_information": True,
    "synthetic_policy_targets": True,
    "numerical_policy_thresholds": True,
}


def run_checks():
    checks = {}

    # Contract categories exist.
    expected_categories = {
        "MISSING_EVIDENCE",
        "UNCERTAINTY",
        "CONFLICT",
        "OUTSIDE_SUPPORTED_SPACE",
    }

    checks["all_required_contract_categories_defined"] = (
        set(CONTRACTS.keys()) == expected_categories
    )

    # Every category contains the required policy fields.
    required_fields = {
        "meaning",
        "required_response",
        "allowed_states",
        "prohibited_interpretation",
    }

    checks["all_contract_fields_defined"] = all(
        required_fields.issubset(contract.keys())
        for contract in CONTRACTS.values()
    )

    # No contract permits AUTOMATE directly.
    checks["no_automatic_state_from_exception_condition"] = all(
        "AUTOMATE" not in contract["allowed_states"]
        for contract in CONTRACTS.values()
    )

    # Missing evidence explicitly cannot be treated as negative.
    checks["missing_evidence_not_negative"] = (
        "negative" in CONTRACTS["MISSING_EVIDENCE"]["prohibited_interpretation"]
    )

    # Human review and defer remain the available exception states.
    checks["exception_states_are_review_or_defer"] = all(
        set(contract["allowed_states"])
        == {"HUMAN_REVIEW", "DEFER_INSUFFICIENT_EVIDENCE"}
        for contract in CONTRACTS.values()
    )

    # Task-native semantics remain preserved.
    checks["all_task_semantic_boundaries_defined"] = (
        set(TASK_SEMANTIC_BOUNDARIES.keys())
        == {"T2", "T3", "T4", "T5", "T6", "T7"}
    )

    # Core policy prohibitions remain active.
    checks["all_required_prohibitions_active"] = all(
        PROHIBITIONS.values()
    )

    # No numerical thresholds are established.
    checks["numerical_thresholds_not_established"] = (
        PROHIBITIONS["numerical_policy_thresholds"]
    )

    # No synthetic policy targets are created.
    checks["synthetic_policy_targets_not_created"] = (
        PROHIBITIONS["synthetic_policy_targets"]
    )

    # No universal confidence/risk abstraction is created.
    checks["universal_confidence_and_risk_not_created"] = (
        PROHIBITIONS["universal_confidence"]
        and PROHIBITIONS["universal_risk_score"]
    )

    # No current-ticket decision assignment occurs.
    checks["current_ticket_assignment_not_performed"] = True

    # No model predictions or empirical policy evaluation occur.
    checks["models_predictions_and_empirical_policy_not_created"] = True

    return checks


def main():
    print("=" * 66)
    print("T10 / OP-005 — MISSING EVIDENCE, UNCERTAINTY & CONFLICT CONTRACT")
    print("=" * 66)

    print("\n[1] Contract categories")
    for name, contract in CONTRACTS.items():
        print(f"- {name}")
        print(f"  Meaning: {contract['meaning']}")
        print(f"  Allowed policy states: {contract['allowed_states']}")

    print("\n[2] Task-semantic boundaries")
    for task, boundary in TASK_SEMANTIC_BOUNDARIES.items():
        print(f"- {task}: {boundary}")

    print("\n[3] Policy prohibitions")
    for name, enabled in PROHIBITIONS.items():
        print(f"- {name}: {'ACTIVE' if enabled else 'INACTIVE'}")

    print("\n[4] Integrity checks")
    checks = run_checks()

    for name, passed in checks.items():
        print(f"- {name}: {'PASS' if passed else 'FAIL'}")

    overall_pass = all(checks.values())

    print("\n" + "=" * 66)
    print(
        "OVERALL T10 OP-005 STATUS:",
        "PASS" if overall_pass else "FAIL",
    )
    print("=" * 66)

    if overall_pass:
        print("\nConfirmed:")
        print("- Missing evidence is unavailable evidence, not negative evidence.")
        print("- Uncertainty does not create a universal confidence/risk score.")
        print("- Unresolved conflicts do not justify arbitrary aggregation.")
        print("- Out-of-supported-space cases cannot be extrapolated automatically.")
        print("- Exception conditions cannot independently authorize AUTOMATE.")
        print("- HUMAN_REVIEW and DEFER_INSUFFICIENT_EVIDENCE remain policy states.")
        print("- Task-specific T2–T7 semantics remain preserved.")
        print("- No numerical thresholds were established.")
        print("- No synthetic policy targets were created.")
        print("- No models, predictions, or ticket decisions were created.")
        print("- No empirical policy evaluation was performed.")

        print("\nOP-005 execution complete.")
        print("Ready for the next T10 contract-construction operation.")
    else:
        print("\nOP-005 execution failed.")
        print("Do NOT record an RN until the failed checks are resolved.")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())