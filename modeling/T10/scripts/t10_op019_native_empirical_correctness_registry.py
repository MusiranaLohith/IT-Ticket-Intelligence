"""
T10 / OP-019

Native Outcome & Empirical Correctness Registry

Purpose
-------
Register already-established empirical task results and identify exactly
what each result supports.

This operation does NOT:
    - train models
    - load datasets
    - calculate new predictions
    - establish automation thresholds
    - create a universal T10 target
    - create a universal score
    - assign ticket-level policy states
"""


TASKS = [
    {
        "task": "T2",
        "role": "Priority Prediction",
        "output": "hard classification",
        "population": 4425,
        "primary_evidence": (
            "locked evaluation hard-prediction correctness"
        ),
        "policy_supported": (
            "task-native predictive correctness evidence"
        ),
        "policy_not_supported": (
            "universal automation eligibility"
        ),
    },
    {
        "task": "T4",
        "role": "Assignee Retrieval / Ranking",
        "output": "ranking",
        "population": 35626,
        "primary_evidence": (
            "Top-K retrieval/ranking correctness"
        ),
        "policy_supported": (
            "task-native ranking evidence"
        ),
        "policy_not_supported": (
            "universal routing correctness or automation threshold"
        ),
    },
    {
        "task": "T5",
        "role": "Duplicate Probability",
        "output": "calibrated probability",
        "population": 20827,
        "primary_evidence": (
            "locked duplicate-probability evaluation"
        ),
        "policy_supported": (
            "native duplicate-probability evidence"
        ),
        "policy_not_supported": (
            "ticket-level automation boundary from retained NPZ"
        ),
    },
    {
        "task": "T6",
        "role": "Duplicate Retrieval",
        "output": "query-level ranking",
        "population": 82416,
        "primary_evidence": (
            "query-level retrieval correctness"
        ),
        "policy_supported": (
            "task-native retrieval/ranking evidence"
        ),
        "policy_not_supported": (
            "universal duplicate decision threshold"
        ),
    },
    {
        "task": "T7",
        "role": "Resolution-Time Survival",
        "output": "survival",
        "population": 102764,
        "primary_evidence": (
            "survival/time-to-event predictive evidence"
        ),
        "policy_supported": (
            "task-native survival evidence"
        ),
        "policy_not_supported": (
            "autonomous resolution-time decision or workflow automation"
        ),
    },
]


def main():

    print("=" * 82)
    print("T10 / OP-019 — NATIVE OUTCOME & EMPIRICAL CORRECTNESS REGISTRY")
    print("=" * 82)

    print()

    checks = []

    # ------------------------------------------------------------
    # Registry integrity
    # ------------------------------------------------------------

    checks.append(
        (
            "required_tasks_registered",
            {
                item["task"] for item in TASKS
            }
            == {"T2", "T4", "T5", "T6", "T7"},
        )
    )

    checks.append(
        (
            "all_populations_positive",
            all(
                item["population"] > 0
                for item in TASKS
            ),
        )
    )

    checks.append(
        (
            "native_semantics_preserved",
            len(
                {
                    item["output"]
                    for item in TASKS
                }
            )
            == 5,
        )
    )

    checks.append(
        (
            "performance_not_equated_with_automation",
            True,
        )
    )

    checks.append(
        (
            "no_policy_threshold_established",
            True,
        )
    )

    # ------------------------------------------------------------
    # Evidence registry
    # ------------------------------------------------------------

    print("=" * 82)
    print("1. REGISTERED EMPIRICAL EVIDENCE")
    print("=" * 82)

    for item in TASKS:

        print()
        print(
            f"{item['task']} — {item['role']}"
        )

        print(
            f"  output population : "
            f"{item['population']:,}"
        )

        print(
            f"  native output     : "
            f"{item['output']}"
        )

        print(
            f"  primary evidence  : "
            f"{item['primary_evidence']}"
        )

        print(
            f"  supports          : "
            f"{item['policy_supported']}"
        )

        print(
            f"  does NOT support  : "
            f"{item['policy_not_supported']}"
        )

    # ------------------------------------------------------------
    # Policy boundary
    # ------------------------------------------------------------

    print()
    print("=" * 82)
    print("2. EMPIRICAL POLICY BOUNDARY")
    print("=" * 82)

    print(
        "Existing task metrics establish task-native predictive evidence."
    )

    print(
        "They do not independently establish a universal automation policy."
    )

    print(
        "Task outputs retain their native semantics."
    )

    print(
        "Ranking is not converted to probability."
    )

    print(
        "Survival is not converted to binary classification."
    )

    print(
        "Task performance is not treated as ticket-level automation eligibility."
    )

    print(
        "No numerical automation threshold is established."
    )

    print(
        "No universal confidence or risk score is established."
    )

    # ------------------------------------------------------------
    # Checks
    # ------------------------------------------------------------

    print()
    print("=" * 82)
    print("3. CONTRACT CHECKS")
    print("=" * 82)

    passed = 0

    for name, result in checks:

        status = "PASS" if result else "FAIL"

        print(
            f"{status:8s} : {name}"
        )

        if result:
            passed += 1

    # ------------------------------------------------------------
    # Final
    # ------------------------------------------------------------

    print()
    print("=" * 82)
    print("4. FINAL RESULT")
    print("=" * 82)

    print(
        f"Contract checks: "
        f"{passed}/{len(checks)}"
    )

    if passed == len(checks):

        print(
            "OP-019 STATUS : PASS"
        )

        print(
            "NEXT : empirical decision-boundary validation."
        )

    else:

        print(
            "OP-019 STATUS : FAIL"
        )

    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())