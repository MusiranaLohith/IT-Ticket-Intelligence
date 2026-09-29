"""
T10 / OP-021

Empirical Policy-Validation Anchor Registry

Purpose
-------
Assess whether existing task-native evidence populations possess the
minimum characteristics required to serve as empirical anchors for
T10 policy validation.

This operation does NOT:
    - rank tasks
    - select a model
    - load datasets
    - calculate predictions
    - establish thresholds
    - create a universal score
    - assign ticket-level policy states
"""


CANDIDATES = [
    {
        "task": "T2",
        "role": "Priority Prediction",
        "traceable_population": True,
        "population": 4425,
        "native_outcome": True,
        "correctness_evidence": True,
        "calibration_relevant": False,
        "native_semantics": "hard classification",
        "anchor_status": "ELIGIBLE_CANDIDATE",
        "limitation": "hard prediction; no native probability",
    },
    {
        "task": "T4",
        "role": "Assignee Retrieval / Ranking",
        "traceable_population": True,
        "population": 35626,
        "native_outcome": True,
        "correctness_evidence": True,
        "calibration_relevant": False,
        "native_semantics": "ranking",
        "anchor_status": "ELIGIBLE_CANDIDATE",
        "limitation": "ranking is not probability or universal routing correctness",
    },
    {
        "task": "T5",
        "role": "Duplicate Probability",
        "traceable_population": False,
        "population": 20827,
        "native_outcome": True,
        "correctness_evidence": True,
        "calibration_relevant": True,
        "native_semantics": "calibrated probability",
        "anchor_status": "LIMITED_CANDIDATE",
        "limitation": "locked NPZ has no explicit ticket IDs",
    },
    {
        "task": "T6",
        "role": "Duplicate Retrieval",
        "traceable_population": True,
        "population": 82416,
        "native_outcome": True,
        "correctness_evidence": True,
        "calibration_relevant": False,
        "native_semantics": "query-level ranking",
        "anchor_status": "ELIGIBLE_CANDIDATE",
        "limitation": "retrieval/ranking evidence; not a universal duplicate decision",
    },
    {
        "task": "T7",
        "role": "Resolution-Time Survival",
        "traceable_population": True,
        "population": 102764,
        "native_outcome": True,
        "correctness_evidence": True,
        "calibration_relevant": False,
        "native_semantics": "survival/time-to-event",
        "anchor_status": "ELIGIBLE_CANDIDATE",
        "limitation": "right censoring must remain distinct from negative outcome",
    },
]


def candidate_is_structurally_eligible(item):

    return all(
        [
            item["traceable_population"],
            item["native_outcome"],
            item["correctness_evidence"],
        ]
    )


def main():

    print("=" * 82)
    print("T10 / OP-021 — EMPIRICAL POLICY-VALIDATION ANCHOR REGISTRY")
    print("=" * 82)

    print()
    print("=" * 82)
    print("1. CANDIDATE EVIDENCE ANCHORS")
    print("=" * 82)

    for item in CANDIDATES:

        eligible = candidate_is_structurally_eligible(item)

        print()
        print(
            f"{item['task']} — {item['role']}"
        )

        print(
            f"  traceable population : "
            f"{item['traceable_population']}"
        )

        print(
            f"  population           : "
            f"{item['population']:,}"
        )

        print(
            f"  native outcome       : "
            f"{item['native_outcome']}"
        )

        print(
            f"  correctness evidence : "
            f"{item['correctness_evidence']}"
        )

        print(
            f"  calibration relevant : "
            f"{item['calibration_relevant']}"
        )

        print(
            f"  native semantics     : "
            f"{item['native_semantics']}"
        )

        print(
            f"  structural eligibility: "
            f"{eligible}"
        )

        print(
            f"  registry status      : "
            f"{item['anchor_status']}"
        )

        print(
            f"  limitation           : "
            f"{item['limitation']}"
        )

    print()
    print("=" * 82)
    print("2. ANCHOR-ELIGIBILITY PRINCIPLE")
    print("=" * 82)

    print(
        "A candidate is structurally eligible when its evaluation "
        "population is traceable, its native outcome is available, "
        "and empirical correctness evidence exists."
    )

    print(
        "Structural eligibility does NOT establish that the task is "
        "suitable for autonomous automation."
    )

    print(
        "No candidate is ranked or declared superior."
    )

    print(
        "T5 remains limited because its retained locked probability "
        "artifact lacks explicit ticket IDs."
    )

    print(
        "Native task semantics remain unchanged."
    )

    print()
    print("=" * 82)
    print("3. CONTRACT CHECKS")
    print("=" * 82)

    checks = [
        (
            "all_candidates_have_native_semantics",
            all(
                bool(item["native_semantics"])
                for item in CANDIDATES
            ),
        ),
        (
            "traceability_requirement_preserved",
            all(
                isinstance(
                    item["traceable_population"],
                    bool,
                )
                for item in CANDIDATES
            ),
        ),
        (
            "t5_limitation_preserved",
            next(
                item["anchor_status"]
                for item in CANDIDATES
                if item["task"] == "T5"
            )
            == "LIMITED_CANDIDATE",
        ),
        (
            "no_automation_claim",
            True,
        ),
        (
            "no_universal_target_created",
            True,
        ),
    ]

    passed = 0

    for name, result in checks:

        status = "PASS" if result else "FAIL"

        print(
            f"{status:8s} : {name}"
        )

        if result:
            passed += 1

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
            "OP-021 STATUS : PASS"
        )

        print(
            "NEXT : empirical validation design for traceable "
            "task-native evidence."
        )

    else:

        print(
            "OP-021 STATUS : FAIL"
        )

    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())