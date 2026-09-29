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
    print("FMP-04 OP-002R — CORRECTED T9 FINAL INTEGRATED CLOSURE VERIFICATION")
    print("=" * 80)

    print("\n[1] Closure artifact")
    print("-" * 80)

    print(f"Path: {T9_CLOSURE}")
    print(f"Exists: {T9_CLOSURE.exists()}")

    if not T9_CLOSURE.exists():
        print("\nSTATUS: BLOCKED")
        return

    data = read_json(T9_CLOSURE)

    print("Readable JSON: True")
    print(f"Top-level type: {type(data).__name__}")

    print("\n[2] Closure state")
    print("-" * 80)

    print(f"title: {data.get('title')}")
    print(f"status: {data.get('status')}")
    print(f"purpose: {data.get('purpose')}")

    print("\n[3] Contract validation")
    print("-" * 80)

    contract = data.get("contract_validation", {})

    print(f"status: {contract.get('status')}")
    print(f"role: {contract.get('role')}")
    print(f"model_fitting: {contract.get('model_fitting')}")
    print(f"universal_score: {contract.get('universal_score')}")

    print("\n[4] Semantic lock validation")
    print("-" * 80)

    semantic = data.get("semantic_lock_validation", {})

    semantic_fields = [
        "status",
        "semantic_boundary",
        "cross_task_probability_comparability",
        "universal_confidence",
        "universal_risk",
        "synthetic_target",
        "T6_binary_reinterpretation",
        "T7_binary_conversion",
        "T7_censoring_relabelling",
    ]

    for field in semantic_fields:
        print(f"{field}: {semantic.get(field)}")

    print("\n[5] Task evidence status")
    print("-" * 80)

    task_evidence = data.get("task_evidence", {})

    for task, evidence in task_evidence.items():
        print(f"{task}:")
        if isinstance(evidence, dict):
            for key, value in evidence.items():
                print(f"  {key}: {value}")
        else:
            print(f"  {evidence}")

    print("\n[6] Final evidence statement")
    print("-" * 80)

    final_statement = data.get("final_evidence_statement", {})

    for task, statement in final_statement.items():
        print(f"{task}: {statement}")

    print("\n[7] Corrected closure checks")
    print("-" * 80)

    checks = {
        "artifact_exists":
            T9_CLOSURE.exists(),

        "status_present":
            data.get("status") == "PASS",

        "contract_validation_pass":
            contract.get("status") == "PASS",

        "model_fitting_not_performed":
            contract.get("model_fitting") == "NOT_PERFORMED",

        "universal_score_not_created":
            contract.get("universal_score") == "NOT_CREATED",

        "semantic_lock_pass":
            semantic.get("status") == "PASS",

        "semantic_boundary_frozen":
            semantic.get("semantic_boundary") == "FROZEN",

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

        "task_evidence_present":
            isinstance(task_evidence, dict)
            and all(
                task in task_evidence
                for task in ["T2", "T3", "T4", "T5", "T6", "T7"]
            ),

        "final_evidence_statement_present":
            isinstance(final_statement, dict)
            and all(
                task in final_statement
                for task in ["T2", "T3", "T4", "T5", "T6", "T7", "cross_task"]
            ),
    }

    for key, value in checks.items():
        print(f"{key}: {value}")

    print("\n[8] Operation safeguards")
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

    print("\n[9] Final summary")
    print("-" * 80)

    all_pass = all(checks.values())

    print(f"All closure checks passed: {all_pass}")

    if all_pass:
        print("\nSTATUS: PASS")
        print(
            "Operation type: "
            "READ_ONLY_T9_FINAL_INTEGRATED_CLOSURE_VERIFICATION"
        )
        print("T9 final integrated closure is verified.")
    else:
        failed = [
            key for key, value in checks.items()
            if not value
        ]

        print(f"Failed checks: {failed}")
        print("\nSTATUS: BLOCKED")


if __name__ == "__main__":
    main()