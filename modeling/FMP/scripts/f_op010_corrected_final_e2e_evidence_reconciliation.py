from __future__ import annotations

import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OP025_PATH = (
    PROJECT_ROOT
    / "modeling/T8/mod036/op025/"
      "t8_mod036_op025_decision_engine_predictions.csv"
)

OP026_PATH = (
    PROJECT_ROOT
    / "modeling/T8/mod036/op026/"
      "t8_mod036_op026_decision_engine_validation.json"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "modeling/FMP/metrics/"
      "f_op010_corrected_final_e2e_evidence_reconciliation.json"
)

EXPECTED_ROWS = 119_895
EXPECTED_COLUMNS = 19

EXPECTED_COMPONENT_COUNTS = {
    "1": 109_649,
    "2": 9_727,
    "3": 519,
    "4": 0,
}

EXPECTED_OBSERVED_STATES = {
    "INSUFFICIENT_EVIDENCE",
    "SUPPORTED",
}


def read_op025():

    result = {
        "exists": OP025_PATH.exists(),
        "readable": False,
    }

    if not OP025_PATH.exists():
        return result

    row_count = 0
    unique_ids = set()

    with OP025_PATH.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        columns = [
            str(column)
            for column in (
                reader.fieldnames or []
            )
        ]

        id_column = None

        for column in columns:

            if column.strip().lower() in {
                "id",
                "ticket_id",
                "ticketid",
                "issue_id",
                "case_id",
            }:
                id_column = column
                break

        for row in reader:

            row_count += 1

            if id_column:
                unique_ids.add(
                    row.get(id_column)
                )

    result.update(
        {
            "readable": True,
            "rows": row_count,
            "columns": len(columns),
            "column_names": columns,
            "id_column": id_column,
            "unique_ids": len(unique_ids),
        }
    )

    return result


def read_op026():

    result = {
        "exists": OP026_PATH.exists(),
        "readable": False,
    }

    if not OP026_PATH.exists():
        return result

    with OP026_PATH.open(
        "r",
        encoding="utf-8",
    ) as f:

        data = json.load(f)

    result["readable"] = True
    result["top_level_keys"] = list(
        data.keys()
    )

    population = data.get(
        "population",
        {},
    )

    architecture = data.get(
        "architecture",
        {},
    )

    result["population"] = population
    result["architecture"] = architecture

    result["observed_overall_states"] = (
        data.get(
            "observed_overall_states",
            [],
        )
    )

    result["observed_consistency_states"] = (
        data.get(
            "observed_consistency_states",
            [],
        )
    )

    result["evidence_count_distribution"] = (
        data.get(
            "evidence_count_distribution",
            {},
        )
    )

    result["closure_criteria"] = (
        data.get(
            "closure_criteria",
            {},
        )
    )

    result["limitations"] = (
        data.get(
            "limitations",
            {},
        )
    )

    return result


def main():

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    op025 = read_op025()
    op026 = read_op026()

    population = op026.get(
        "population",
        {},
    )

    architecture = op026.get(
        "architecture",
        {},
    )

    observed_states = set(
        op026.get(
            "observed_overall_states",
            [],
        )
    )

    component_distribution = {
        str(key): int(value)
        for key, value in op026.get(
            "evidence_count_distribution",
            {},
        ).items()
    }

    component_total = sum(
        component_distribution.values()
    )

    population_prediction_rows = (
        population.get(
            "prediction_rows"
        )
    )

    population_unique_ids = (
        population.get(
            "unique_prediction_ids"
        )
    )

    population_union = (
        population.get(
            "decision_engine_union"
        )
    )

    all_four_intersection = (
        population.get(
            "all_four_intersection"
        )
    )

    variable_evidence = (
        architecture.get(
            "variable_evidence"
        )
    )

    missing_evidence_unavailable = (
        architecture.get(
            "missing_evidence_is_unavailable"
        )
    )

    # Read the authoritative policy boundary
    # only if explicitly represented.
    serialized_text = json.dumps(
        op026,
        ensure_ascii=False,
    ).lower()

    universal_confidence_created = (
        "universal_confidence" in serialized_text
        and "not_created" not in serialized_text
        and "not created" not in serialized_text
    )

    universal_risk_created = (
        "universal_risk" in serialized_text
        and "not_created" not in serialized_text
        and "not created" not in serialized_text
    )

    synthetic_target_created = (
        "synthetic_fusion_target" in serialized_text
        and "not_created" not in serialized_text
        and "not created" not in serialized_text
    )

    checks = {
        "op025_population_rows": (
            op025.get("rows")
            == EXPECTED_ROWS
        ),
        "op025_population_columns": (
            op025.get("columns")
            == EXPECTED_COLUMNS
        ),
        "op025_unique_ids": (
            op025.get("unique_ids")
            == EXPECTED_ROWS
        ),
        "op026_prediction_rows": (
            population_prediction_rows
            == EXPECTED_ROWS
        ),
        "op026_unique_prediction_ids": (
            population_unique_ids
            == EXPECTED_ROWS
        ),
        "decision_engine_union": (
            population_union
            == EXPECTED_ROWS
        ),
        "all_four_intersection_zero": (
            all_four_intersection
            == 0
        ),
        "component_distribution_total": (
            component_total
            == EXPECTED_ROWS
        ),
        "component_distribution_exact": (
            component_distribution
            == EXPECTED_COMPONENT_COUNTS
        ),
        "observed_states_exact": (
            observed_states
            == EXPECTED_OBSERVED_STATES
        ),
        "variable_evidence": (
            variable_evidence is True
        ),
        "missing_evidence_is_unavailable": (
            missing_evidence_unavailable
            is True
        ),
        "universal_confidence_not_created": (
            universal_confidence_created
            is False
        ),
        "universal_risk_not_created": (
            universal_risk_created
            is False
        ),
        "synthetic_fusion_target_not_created": (
            synthetic_target_created
            is False
        ),
    }

    status = (
        "PASS"
        if all(checks.values())
        else "REQUIRES_REVIEW"
    )

    result = {
        "operation": "F-OP-010",
        "title": (
            "Corrected Final E2E Evidence "
            "Reconciliation"
        ),
        "status": status,
        "read_only": True,
        "models_executed": False,
        "model_modified": False,
        "retraining_performed": False,
        "threshold_selection_performed": False,
        "locked_test_reused_for_policy_selection": (
            False
        ),
        "op025": op025,
        "op026": op026,
        "component_distribution_total": (
            component_total
        ),
        "expected_component_distribution": (
            EXPECTED_COMPONENT_COUNTS
        ),
        "expected_observed_states": sorted(
            EXPECTED_OBSERVED_STATES
        ),
        "checks": checks,
        "semantic_boundary": {
            "missing_evidence_is_unavailable": True,
            "native_task_semantics_preserved": True,
            "universal_confidence": (
                "NOT_CREATED"
            ),
            "universal_risk": (
                "NOT_CREATED"
            ),
            "synthetic_fusion_target": (
                "NOT_CREATED"
            ),
            "autonomous_policy": (
                "NOT_ESTABLISHED"
            ),
        },
        "final_e2e_status": (
            "VALIDATED"
            if status == "PASS"
            else "NOT_FULLY_VALIDATED"
        ),
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

    print("=" * 72)
    print(
        "F-OP-010 — CORRECTED FINAL E2E "
        "EVIDENCE RECONCILIATION"
    )
    print("=" * 72)

    print(
        f"OP-025 rows              : "
        f"{op025.get('rows')}"
    )

    print(
        f"OP-025 columns           : "
        f"{op025.get('columns')}"
    )

    print(
        f"OP-025 unique IDs        : "
        f"{op025.get('unique_ids')}"
    )

    print(
        f"OP-026 prediction rows   : "
        f"{population_prediction_rows}"
    )

    print(
        f"OP-026 unique IDs        : "
        f"{population_unique_ids}"
    )

    print(
        f"Decision-engine union    : "
        f"{population_union}"
    )

    print(
        f"All-four intersection    : "
        f"{all_four_intersection}"
    )

    print()
    print(
        "COMPONENT DISTRIBUTION"
    )
    print("-" * 72)

    for key in sorted(
        EXPECTED_COMPONENT_COUNTS,
        key=int,
    ):

        observed = component_distribution.get(
            key,
            0,
        )

        print(
            f"{key} component(s)       : "
            f"{observed}"
        )

    print(
        f"Total                    : "
        f"{component_total}"
    )

    print()
    print(
        "OBSERVED OVERALL STATES"
    )
    print("-" * 72)

    for state in sorted(
        observed_states
    ):
        print(
            f"  {state}"
        )

    print()
    print(
        "ARCHITECTURE BOUNDARY"
    )
    print("-" * 72)

    print(
        f"Variable evidence        : "
        f"{variable_evidence}"
    )

    print(
        "Missing evidence = "
        "unavailable              : "
        f"{missing_evidence_unavailable}"
    )

    print(
        "Universal confidence     : "
        "NOT_CREATED"
    )

    print(
        "Universal risk           : "
        "NOT_CREATED"
    )

    print(
        "Synthetic fusion target : "
        "NOT_CREATED"
    )

    print(
        "Autonomous policy        : "
        "NOT_ESTABLISHED"
    )

    print()
    print("CHECKS")
    print("-" * 72)

    for name, value in checks.items():

        print(
            f"{name}: {value}"
        )

    print()
    print(
        f"Final E2E status         : "
        f"{result['final_e2e_status']}"
    )

    print(
        f"Output                   : "
        f"{OUTPUT_PATH}"
    )

    print("=" * 72)
    print(
        f"RESULT: {status} — "
        "F-OP-010 complete"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()