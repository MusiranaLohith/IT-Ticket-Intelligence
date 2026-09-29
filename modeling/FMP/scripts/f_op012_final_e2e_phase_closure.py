from pathlib import Path
import csv
import json


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

METRICS_DIR = PROJECT_ROOT / "modeling" / "FMP" / "metrics"

INPUTS = {
    "f_op001": METRICS_DIR / "f_op001_final_e2e_contract_reconciliation.json",
    "f_op007": METRICS_DIR / "f_op007_op025_op026_contract_reconciliation.json",
    "f_op009": METRICS_DIR / "f_op009_op026_evidence_structure_inspection.json",
    "f_op010": METRICS_DIR / "f_op010_corrected_final_e2e_evidence_reconciliation.json",
    "f_op011": METRICS_DIR / "f_op011_final_component_distribution_reconciliation.json",
}

OP025_CSV = (
    PROJECT_ROOT
    / "modeling"
    / "T8"
    / "mod036"
    / "op025"
    / "t8_mod036_op025_decision_engine_predictions.csv"
)

OP026_JSON = (
    PROJECT_ROOT
    / "modeling"
    / "T8"
    / "mod036"
    / "op026"
    / "t8_mod036_op026_decision_engine_validation.json"
)

OUTPUT = METRICS_DIR / "f_final_e2e_phase_closure.json"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_path(root, path_parts, default=None):
    value = root

    for part in path_parts:
        if not isinstance(value, dict):
            return default

        if part not in value:
            return default

        value = value[part]

    return value


def first_present(root, paths, default=None):
    for path_parts in paths:
        value = get_path(root, path_parts, None)

        if value is not None:
            return value

    return default


def main():

    print("=" * 72)
    print("F-OP-012R3 — FINAL E2E PHASE CLOSURE")
    print("=" * 72)

    # ==============================================================
    # 1. Load prior F-phase evidence
    # ==============================================================

    loaded = {}

    for name, path in INPUTS.items():

        if not path.exists():
            raise FileNotFoundError(
                f"Missing required input: {path}"
            )

        loaded[name] = load_json(path)

    if not OP025_CSV.exists():
        raise FileNotFoundError(
            f"Missing OP-025 population artifact: {OP025_CSV}"
        )

    if not OP026_JSON.exists():
        raise FileNotFoundError(
            f"Missing OP-026 validation artifact: {OP026_JSON}"
        )

    # ==============================================================
    # 2. Load the ACTUAL OP-026 validation artifact.
    #
    # F-OP-009 is an inspection record. OP-026 itself is the
    # authoritative validation artifact.
    # ==============================================================

    op026 = load_json(OP026_JSON)

    # The known OP-026 structure from F-OP-009 is:
    #
    # population
    # observed_overall_states
    # observed_consistency_states
    # evidence_count_distribution
    # architecture
    #
    # Therefore use the actual OP-026 object directly.
    # ==============================================================

    population = op026.get("population", {})

    prediction_rows = population.get(
        "prediction_rows"
    )

    unique_prediction_ids = population.get(
        "unique_prediction_ids"
    )

    decision_engine_union = population.get(
        "decision_engine_union"
    )

    all_four_intersection = population.get(
        "all_four_intersection"
    )

    observed_states = op026.get(
        "observed_overall_states",
        []
    )

    consistency_states = op026.get(
        "observed_consistency_states",
        []
    )

    architecture = op026.get(
        "architecture",
        {}
    )

    architecture_variable_evidence = architecture.get(
        "variable_evidence"
    )

    architecture_missing_unavailable = architecture.get(
        "missing_evidence_is_unavailable"
    )

    # ==============================================================
    # 3. Validate OP-025 population directly
    # ==============================================================

    with OP025_CSV.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        reader = csv.reader(f)

        header = next(reader)

        if "id" not in header:
            raise RuntimeError(
                "OP-025 CSV does not contain required 'id' column."
            )

        id_index = header.index("id")

        op025_rows = 0
        unique_ids = set()

        for row in reader:

            op025_rows += 1

            if id_index < len(row):
                unique_ids.add(row[id_index])

    op025_unique_ids = len(unique_ids)

    # ==============================================================
    # 4. F-OP-011 authoritative component reconciliation
    # ==============================================================

    op011 = loaded["f_op011"]

    op011_status = op011.get(
        "status"
    )

    reconciled = (
        op011.get("reconciled_distribution")
        or op011.get("final_distribution")
        or {}
    )

    component_1 = reconciled.get(
        "1",
        reconciled.get(1, 0)
    )

    component_2 = reconciled.get(
        "2",
        reconciled.get(2, 0)
    )

    component_3 = reconciled.get(
        "3",
        reconciled.get(3, 0)
    )

    component_4 = reconciled.get(
        "4",
        reconciled.get(4, 0)
    )

    component_total = op011.get(
        "reconciled_total"
    )

    if component_total is None:
        component_total = (
            component_1
            + component_2
            + component_3
            + component_4
        )

    # ==============================================================
    # 5. Final checks
    # ==============================================================

    checks = {

        "f_op001_pass":
            loaded["f_op001"].get("status") == "PASS",

        "f_op007_pass":
            loaded["f_op007"].get("status") == "PASS",

        "f_op009_pass":
            loaded["f_op009"].get("status") == "PASS",

        "f_op011_pass":
            op011_status == "PASS",

        "op025_population_119895":
            op025_rows == 119895,

        "op025_unique_ids_119895":
            op025_unique_ids == 119895,

        "op026_prediction_rows_119895":
            prediction_rows == 119895,

        "op026_unique_prediction_ids_119895":
            unique_prediction_ids == 119895,

        "population_identity_reconciled":
            (
                op025_rows
                == prediction_rows
                == 119895
                and
                op025_unique_ids
                == unique_prediction_ids
                == 119895
            ),

        "decision_engine_union_119895":
            decision_engine_union == 119895,

        "all_four_intersection_zero":
            all_four_intersection == 0,

        "component_distribution_exact":
            (
                component_1 == 109649
                and
                component_2 == 9727
                and
                component_3 == 519
                and
                component_4 == 0
                and
                component_total == 119895
            ),

        "observed_overall_states_valid":
            set(observed_states)
            == {
                "INSUFFICIENT_EVIDENCE",
                "SUPPORTED",
            },

        "observed_consistency_states_valid":
            set(consistency_states)
            == {
                "INSUFFICIENT_EVIDENCE",
                "SUPPORTED",
            },

        "variable_evidence_preserved":
            architecture_variable_evidence is True,

        "missing_evidence_unavailable":
            architecture_missing_unavailable is True,

        "no_universal_confidence_created":
            loaded["f_op001"].get(
                "universal_confidence_created"
            ) is not True,

        "no_universal_risk_created":
            loaded["f_op001"].get(
                "universal_risk_created"
            ) is not True,

        "no_synthetic_fusion_target_created":
            loaded["f_op001"].get(
                "synthetic_fusion_target_created"
            ) is not True,

        "no_operational_policy_established":
            (
                loaded["f_op001"].get(
                    "automation_established"
                ) is not True
                and
                loaded["f_op001"].get(
                    "human_review_established"
                ) is not True
                and
                loaded["f_op001"].get(
                    "universal_threshold_established"
                ) is not True
            ),
    }

    # ==============================================================
    # 6. Historical F-OP-010 reconciliation
    # ==============================================================

    op010_status = loaded["f_op010"].get(
        "status"
    )

    op010_representation_issue_reconciled = (
        op010_status == "REQUIRES_REVIEW"
        and
        op011_status == "PASS"
        and
        checks["component_distribution_exact"]
    )

    checks[
        "f_op010_representation_issue_reconciled_by_f_op011"
    ] = op010_representation_issue_reconciled

    # ==============================================================
    # 7. Final status
    # ==============================================================

    all_checks_pass = all(
        checks.values()
    )

    closure_status = (
        "CLOSED_PASS"
        if all_checks_pass
        else
        "REQUIRES_REVIEW"
    )

    # ==============================================================
    # 8. Write closure record
    # ==============================================================

    result = {

        "operation":
            "F-OP-012R3",

        "operation_name":
            "Final E2E Phase Closure",

        "status":
            "PASS"
            if all_checks_pass
            else
            "REQUIRES_REVIEW",

        "closure_status":
            closure_status,

        "scope": (
            "Integrated population and evidence-chain validation "
            "at the frozen T1-T7 -> T8 -> T9 -> T10 architecture "
            "boundary."
        ),

        "population": {

            "op025_rows":
                op025_rows,

            "op025_unique_ids":
                op025_unique_ids,

            "op026_prediction_rows":
                prediction_rows,

            "op026_unique_prediction_ids":
                unique_prediction_ids,

            "decision_engine_union":
                decision_engine_union,

            "all_four_intersection":
                all_four_intersection,
        },

        "component_distribution": {

            "component_1":
                component_1,

            "component_2":
                component_2,

            "component_3":
                component_3,

            "component_4":
                component_4,

            "total":
                component_total,
        },

        "observed_evidence_states": {

            "overall":
                observed_states,

            "consistency":
                consistency_states,
        },

        "architecture": {

            "variable_evidence":
                architecture_variable_evidence,

            "missing_evidence_is_unavailable":
                architecture_missing_unavailable,
        },

        "historical_reconciliation": {

            "f_op010_status":
                op010_status,

            "f_op010_not_overwritten":
                True,

            "f_op011_resolution": (
                "F-OP-011 independently reconciled the "
                "component distribution and interpreted the "
                "absent component-4 category as zero observed "
                "instances."
            ),
        },

        "not_established": [

            "model-performance superiority across tasks",

            "universal confidence",

            "universal risk",

            "universal threshold",

            "autonomous action policy",

            "human-review threshold",

            "synthetic fusion target",
        ],

        "controls": {

            "model_retraining":
                False,

            "model_selection":
                False,

            "frozen_artifact_modification":
                False,

            "threshold_optimization":
                False,

            "locked_test_reuse":
                False,

            "universal_probability_aggregation":
                False,

            "synthetic_target_creation":
                False,
        },

        "checks":
            checks,

        "artifacts": {

            "f_op001":
                str(INPUTS["f_op001"]),

            "f_op007":
                str(INPUTS["f_op007"]),

            "f_op009":
                str(INPUTS["f_op009"]),

            "f_op010":
                str(INPUTS["f_op010"]),

            "f_op011":
                str(INPUTS["f_op011"]),

            "op025_population":
                str(OP025_CSV),

            "op026_validation":
                str(OP026_JSON),

            "output":
                str(OUTPUT),
        },

        "final_statement": (
            "F phase validates the integrated population and "
            "evidence chain at the frozen architecture boundary. "
            "This closure does not establish autonomous operational "
            "policy or a universal confidence/risk construct."
            if all_checks_pass
            else
            "F phase remains open because one or more final "
            "closure checks did not pass."
        ),
    }

    with OUTPUT.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            result,
            f,
            indent=2
        )

    # ==============================================================
    # 9. Compact output
    # ==============================================================

    passed = sum(
        value is True
        for value in checks.values()
    )

    total = len(checks)

    print(
        f"Input records loaded: "
        f"{len(loaded)}/{len(INPUTS)}"
    )

    print(
        f"OP-025 rows: {op025_rows}"
    )

    print(
        f"OP-025 unique IDs: {op025_unique_ids}"
    )

    print(
        f"OP-026 prediction rows: "
        f"{prediction_rows}"
    )

    print(
        f"OP-026 unique prediction IDs: "
        f"{unique_prediction_ids}"
    )

    print(
        f"Decision-engine union: "
        f"{decision_engine_union}"
    )

    print(
        f"All-four intersection: "
        f"{all_four_intersection}"
    )

    print(
        "Component distribution: "
        f"1={component_1}, "
        f"2={component_2}, "
        f"3={component_3}, "
        f"4={component_4}, "
        f"total={component_total}"
    )

    print(
        f"Observed overall states: "
        f"{observed_states}"
    )

    print(
        f"Observed consistency states: "
        f"{consistency_states}"
    )

    print(
        f"F-OP-010 historical status: "
        f"{op010_status}"
    )

    print(
        "F-OP-010 representation issue "
        "reconciled by F-OP-011: "
        f"{op010_representation_issue_reconciled}"
    )

    print(
        f"Closure checks: "
        f"{passed}/{total}"
    )

    print(
        f"OUTPUT: {OUTPUT}"
    )

    print(
        f"STATUS: {closure_status}"
    )


if __name__ == "__main__":
    main()