from __future__ import annotations

import json
from pathlib import Path


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T9_CLOSURE = (
    ROOT
    / "modeling"
    / "T9"
    / "mod037"
    / "t9_mod037_op015_final_integrated_closure.json"
)


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    print("=" * 80)
    print("FMP-04 OP-003 — T9 → T10 HANDOFF VERIFICATION")
    print("=" * 80)

    print("\n[1] Loading T9 closure artifact")
    print("-" * 80)

    print(f"Path: {T9_CLOSURE}")
    print(f"Exists: {T9_CLOSURE.exists()}")

    if not T9_CLOSURE.exists():
        print("\nSTATUS: BLOCKED")
        return

    data = read_json(T9_CLOSURE)

    print("Readable JSON: True")
    print(f"Artifact status: {data.get('status')}")

    contract = data.get("contract_validation", {})
    semantic = data.get("semantic_lock_validation", {})
    task_evidence = data.get("task_evidence", {})
    final_statement = data.get("final_evidence_statement", {})

    print("\n[2] T9 → T10 contract boundary")
    print("-" * 80)

    print(f"T9 status: {data.get('status')}")
    print(f"Contract status: {contract.get('status')}")
    print(f"Model fitting: {contract.get('model_fitting')}")
    print(f"Universal score: {contract.get('universal_score')}")

    print("\n[3] Semantic restrictions handed forward")
    print("-" * 80)

    restrictions = {
        "cross_task_probability_comparability":
            semantic.get("cross_task_probability_comparability"),

        "universal_confidence":
            semantic.get("universal_confidence"),

        "universal_risk":
            semantic.get("universal_risk"),

        "synthetic_target":
            semantic.get("synthetic_target"),

        "T6_binary_reinterpretation":
            semantic.get("T6_binary_reinterpretation"),

        "T7_binary_conversion":
            semantic.get("T7_binary_conversion"),

        "T7_censoring_relabelling":
            semantic.get("T7_censoring_relabelling"),
    }

    for key, value in restrictions.items():
        print(f"{key}: {value}")

    print("\n[4] Native task evidence handoff")
    print("-" * 80)

    expected_task_semantics = {
        "T2": {
            "status": "UNAVAILABLE_FOR_PROBABILITY_CALIBRATION",
        },
        "T3": {
            "status": "UNAVAILABLE",
        },
        "T4": {
            "status": "NATIVE_RANKING_EVALUATION_ESTABLISHED",
            "probability_calibration": "NOT_ESTABLISHED",
        },
        "T5": {
            "status": "EMPIRICAL_CALIBRATION_EVIDENCE_ESTABLISHED",
            "formal_method_selection": "NOT_FORMALLY_SELECTED",
        },
        "T6": {
            "status": "NATIVE_RETRIEVAL_EVALUATION_ESTABLISHED",
            "binary_probability_calibration": "NOT_ESTABLISHED",
        },
        "T7": {
            "status": "NATIVE_SURVIVAL_EVIDENCE_CLOSED",
            "formal_survival_calibration": "NOT_ESTABLISHED",
            "formal_calibration_uncertainty": "NOT_ESTABLISHED",
        },
    }

    for task, expected in expected_task_semantics.items():
        actual = task_evidence.get(task, {})

        print(f"\n{task}:")

        for key, expected_value in expected.items():
            actual_value = actual.get(key)
            print(
                f"  {key}: "
                f"actual={actual_value!r} "
                f"expected={expected_value!r}"
            )

    print("\n[5] T10 boundary implications")
    print("-" * 80)

    print(
        "T10 receives native task evidence rather than a universal confidence score."
    )
    print(
        "T10 may evaluate task-specific automation/review/defer conditions "
        "only where empirical evidence supports them."
    )
    print(
        "T10 must not convert ranking, retrieval, or survival quantities "
        "into ordinary binary probabilities."
    )
    print(
        "T10 must not claim a universal confidence/risk threshold."
    )

    print("\n[6] Handoff checks")
    print("-" * 80)

    checks = {
        "t9_closure_pass":
            data.get("status") == "PASS",

        "contract_pass":
            contract.get("status") == "PASS",

        "model_fitting_not_performed":
            contract.get("model_fitting") == "NOT_PERFORMED",

        "universal_score_not_created":
            contract.get("universal_score") == "NOT_CREATED",

        "cross_task_probability_comparability_prohibited":
            semantic.get("cross_task_probability_comparability")
            == "PROHIBITED",

        "universal_confidence_prohibited":
            semantic.get("universal_confidence") == "PROHIBITED",

        "universal_risk_prohibited":
            semantic.get("universal_risk") == "PROHIBITED",

        "synthetic_target_prohibited":
            semantic.get("synthetic_target") == "PROHIBITED",

        "T6_binary_reinterpretation_prohibited":
            semantic.get("T6_binary_reinterpretation")
            == "PROHIBITED",

        "T7_binary_conversion_prohibited":
            semantic.get("T7_binary_conversion")
            == "PROHIBITED",

        "T7_censoring_relabelling_prohibited":
            semantic.get("T7_censoring_relabelling")
            == "PROHIBITED",

        "T2_native_boundary_preserved":
            task_evidence.get("T2", {}).get("status")
            == "UNAVAILABLE_FOR_PROBABILITY_CALIBRATION",

        "T3_native_boundary_preserved":
            task_evidence.get("T3", {}).get("status")
            == "UNAVAILABLE",

        "T4_ranking_boundary_preserved":
            task_evidence.get("T4", {}).get("status")
            == "NATIVE_RANKING_EVALUATION_ESTABLISHED",

        "T5_calibration_boundary_preserved":
            task_evidence.get("T5", {}).get("status")
            == "EMPIRICAL_CALIBRATION_EVIDENCE_ESTABLISHED",

        "T6_retrieval_boundary_preserved":
            task_evidence.get("T6", {}).get("status")
            == "NATIVE_RETRIEVAL_EVALUATION_ESTABLISHED",

        "T7_survival_boundary_preserved":
            task_evidence.get("T7", {}).get("status")
            == "NATIVE_SURVIVAL_EVIDENCE_CLOSED",

        "final_cross_task_statement_present":
            isinstance(final_statement, dict)
            and "cross_task" in final_statement,
    }

    for key, value in checks.items():
        print(f"{key}: {value}")

    print("\n[7] Read-only safeguards")
    print("-" * 80)

    safeguards = {
        "Predictions generated": False,
        "Models loaded": False,
        "Retraining performed": False,
        "New calibration fitted": False,
        "Evaluation performed": False,
        "Threshold selected": False,
        "Universal confidence score created": False,
        "Universal risk score created": False,
        "Artifacts modified": False,
    }

    for key, value in safeguards.items():
        print(f"{key}: {value}")

    print("\n[8] Final summary")
    print("-" * 80)

    all_pass = all(checks.values())

    print(f"All T9 → T10 handoff checks passed: {all_pass}")

    if all_pass:
        print("\nSTATUS: PASS")
        print(
            "Operation type: "
            "READ_ONLY_T9_T10_HANDOFF_VERIFICATION"
        )
        print(
            "T9 evidence boundary is valid for handoff to T10."
        )
    else:
        failed = [
            key for key, value in checks.items()
            if not value
        ]

        print(f"Failed checks: {failed}")
        print("\nSTATUS: BLOCKED")


if __name__ == "__main__":
    main()