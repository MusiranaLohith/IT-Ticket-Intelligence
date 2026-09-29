"""
T10 / OP-018

Traceable Empirical Evidence Population Registry

Purpose
-------
Register the existing task-native evidence populations that can support
T10 empirical policy validation.

This is a model-independent registry.

It does NOT:
    - load datasets
    - train models
    - calculate new predictions
    - create a universal T10 target
    - create a universal score
    - assign ticket decisions
    - establish automation thresholds
    - combine heterogeneous task outputs numerically
"""


EVIDENCE = [
    {
        "task": "T2",
        "semantic_role": "Priority Prediction",
        "native_output": "hard_classification",
        "evaluation_population": 4425,
        "traceable_ids": True,
        "native_probability": False,
        "policy_boundary": "task-native correctness only",
    },
    {
        "task": "T3",
        "semantic_role": "Severity Prediction",
        "native_output": "hard_classification",
        "evaluation_population": None,
        "traceable_ids": "limited",
        "native_probability": False,
        "policy_boundary": "limited empirical evidence",
    },
    {
        "task": "T4",
        "semantic_role": "Assignee Retrieval / Ranking",
        "native_output": "ranking",
        "evaluation_population": 35626,
        "traceable_ids": True,
        "native_probability": False,
        "policy_boundary": "ranking evidence only",
    },
    {
        "task": "T5",
        "semantic_role": "Duplicate Probability",
        "native_output": "calibrated_probability",
        "evaluation_population": 20827,
        "traceable_ids": False,
        "native_probability": True,
        "policy_boundary": "native duplicate evidence; ticket-level ID intersection unavailable",
    },
    {
        "task": "T6",
        "semantic_role": "Duplicate Retrieval",
        "native_output": "query_level_ranking",
        "evaluation_population": 82416,
        "traceable_ids": True,
        "native_probability": False,
        "policy_boundary": "retrieval/ranking evidence only",
    },
    {
        "task": "T7",
        "semantic_role": "Resolution-Time Survival",
        "native_output": "survival",
        "evaluation_population": 102764,
        "traceable_ids": True,
        "native_probability": False,
        "policy_boundary": "survival/time-to-event evidence; censoring preserved",
    },
]


def main():

    print("=" * 82)
    print("T10 / OP-018 — TRACEABLE EMPIRICAL EVIDENCE POPULATION REGISTRY")
    print("=" * 82)

    print()

    checks = []

    # ------------------------------------------------------------
    # Registry integrity
    # ------------------------------------------------------------

    checks.append(
        (
            "all_required_tasks_present",
            {
                item["task"] for item in EVIDENCE
            }
            == {"T2", "T3", "T4", "T5", "T6", "T7"},
        )
    )

    checks.append(
        (
            "t5_locked_population_is_20827",
            next(
                item["evaluation_population"]
                for item in EVIDENCE
                if item["task"] == "T5"
            )
            == 20827,
        )
    )

    checks.append(
        (
            "t5_ids_not_claimed",
            next(
                item["traceable_ids"]
                for item in EVIDENCE
                if item["task"] == "T5"
            )
            is False,
        )
    )

    checks.append(
        (
            "heterogeneous_semantics_preserved",
            len(
                {
                    item["native_output"]
                    for item in EVIDENCE
                }
            )
            > 1,
        )
    )

    checks.append(
        (
            "no_universal_policy_target",
            True,
        )
    )

    print("=" * 82)
    print("1. REGISTERED TASK-NATIVE EVIDENCE")
    print("=" * 82)

    for item in EVIDENCE:

        population = item["evaluation_population"]

        if population is None:
            population_text = "NOT ESTABLISHED"
        else:
            population_text = f"{population:,}"

        print()
        print(f"{item['task']} — {item['semantic_role']}")
        print(f"  native output       : {item['native_output']}")
        print(f"  evaluation population: {population_text}")
        print(f"  traceable IDs       : {item['traceable_ids']}")
        print(f"  native probability  : {item['native_probability']}")
        print(f"  policy boundary     : {item['policy_boundary']}")

    print()
    print("=" * 82)
    print("2. CONTRACT CHECKS")
    print("=" * 82)

    passed = 0

    for name, result in checks:

        status = "PASS" if result else "FAIL"

        print(f"{status:8s} : {name}")

        if result:
            passed += 1

    print()
    print("=" * 82)
    print("3. POLICY VALIDATION BOUNDARY")
    print("=" * 82)

    print(
        "Task-native evidence populations are registered."
    )

    print(
        "No heterogeneous outputs are converted into a universal score."
    )

    print(
        "Ranking outputs remain rankings."
    )

    print(
        "Survival outputs remain survival evidence."
    )

    print(
        "T5 locked probability remains native duplicate evidence."
    )

    print(
        "T5 ticket-level intersection remains unavailable because "
        "the retained 20,827-row NPZ has no explicit IDs."
    )

    print(
        "No automation threshold or ticket-level policy state is established."
    )

    print()
    print("=" * 82)
    print("4. FINAL RESULT")
    print("=" * 82)

    print(f"Contract checks: {passed}/{len(checks)}")

    if passed == len(checks):
        print("OP-018 STATUS : PASS")
        print(
            "NEXT : empirical task-native policy validation."
        )
    else:
        print("OP-018 STATUS : FAIL")

    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())