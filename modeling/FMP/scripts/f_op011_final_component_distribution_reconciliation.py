from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OP026_PATH = (
    PROJECT_ROOT
    / "modeling/T8/mod036/op026/"
      "t8_mod036_op026_decision_engine_validation.json"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "modeling/FMP/metrics/"
      "f_op011_final_component_distribution_reconciliation.json"
)

EXPECTED_ROWS = 119_895

EXPECTED_COUNTS = {
    1: 109_649,
    2: 9_727,
    3: 519,
    4: 0,
}


def normalize_distribution(
    raw_distribution,
):
    normalized = {}

    for key, value in raw_distribution.items():

        try:
            numeric_key = int(str(key))
        except ValueError:
            continue

        normalized[numeric_key] = int(value)

    return normalized


def main():

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 72)
    print(
        "F-OP-011 — FINAL COMPONENT "
        "DISTRIBUTION RECONCILIATION"
    )
    print("=" * 72)

    if not OP026_PATH.exists():

        print(
            "OP-026 exists            : False"
        )

        print(
            "RESULT: BLOCKED — "
            "OP-026 validation artifact "
            "not found"
        )

        return

    with OP026_PATH.open(
        "r",
        encoding="utf-8",
    ) as f:

        data = json.load(f)

    raw_distribution = data.get(
        "evidence_count_distribution",
        {},
    )

    observed = normalize_distribution(
        raw_distribution
    )

    # Missing categories are interpreted as
    # zero observed instances. This does not
    # invent observations; it records the
    # absence of that category from the
    # authoritative distribution.
    reconciled = {
        component_count: observed.get(
            component_count,
            0,
        )
        for component_count in (
            1,
            2,
            3,
            4,
        )
    }

    observed_total = sum(
        reconciled.values()
    )

    per_category_checks = {
        str(component_count): (
            reconciled[component_count]
            == expected_count
        )
        for component_count,
        expected_count
        in EXPECTED_COUNTS.items()
    }

    total_check = (
        observed_total == EXPECTED_ROWS
    )

    exact_reconciliation = (
        all(per_category_checks.values())
        and total_check
    )

    result = {
        "operation": "F-OP-011",
        "title": (
            "Final Component Distribution "
            "Reconciliation"
        ),
        "status": (
            "PASS"
            if exact_reconciliation
            else "REQUIRES_REVIEW"
        ),
        "read_only": True,
        "models_executed": False,
        "model_modified": False,
        "retraining_performed": False,
        "threshold_selection_performed": False,
        "locked_test_reused_for_policy_selection": (
            False
        ),
        "source": str(OP026_PATH),
        "raw_distribution": raw_distribution,
        "normalized_distribution": observed,
        "reconciled_distribution": reconciled,
        "expected_distribution": {
            str(key): value
            for key, value
            in EXPECTED_COUNTS.items()
        },
        "per_category_checks": (
            per_category_checks
        ),
        "observed_total": observed_total,
        "expected_total": EXPECTED_ROWS,
        "total_check": total_check,
        "exact_reconciliation": (
            exact_reconciliation
        ),
        "semantic_interpretation": {
            "absent_component_category_means_zero_"
            "observed_instances": True,
            "synthetic_rows_created": False,
            "population_modified": False,
            "native_evidence_semantics_preserved": (
                True
            ),
        },
    }

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(
        "OP-026 exists            : True"
    )

    print(
        "Raw distribution         : "
        f"{raw_distribution}"
    )

    print()
    print(
        "RECONCILED DISTRIBUTION"
    )
    print("-" * 72)

    for component_count in (
        1,
        2,
        3,
        4,
    ):

        print(
            f"{component_count} component(s)"
            f"       : "
            f"{reconciled[component_count]}"
        )

    print(
        f"Total                    : "
        f"{observed_total}"
    )

    print()
    print(
        "CATEGORY CHECKS"
    )
    print("-" * 72)

    for key, value in (
        per_category_checks.items()
    ):

        print(
            f"{key} component(s): "
            f"{value}"
        )

    print()
    print(
        f"Total check              : "
        f"{total_check}"
    )

    print(
        f"Exact reconciliation     : "
        f"{exact_reconciliation}"
    )

    print(
        "Absent category 4       : "
        "interpreted as 0 observed "
        "instances"
    )

    print()
    print(
        f"Output                   : "
        f"{OUTPUT_PATH}"
    )

    print("=" * 72)
    print(
        f"RESULT: {result['status']} — "
        "F-OP-011 complete"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()