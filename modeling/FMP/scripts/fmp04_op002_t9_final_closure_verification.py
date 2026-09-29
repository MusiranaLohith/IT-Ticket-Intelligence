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
    print("FMP-04 OP-002 — T9 FINAL INTEGRATED CLOSURE VERIFICATION")
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
    print(f"Top-level keys: {list(data.keys())}")

    print("\n[2] Closure state")
    print("-" * 80)

    status = data.get("status")
    title = data.get("title")
    purpose = data.get("purpose")

    print(f"title: {title}")
    print(f"status: {status}")
    print(f"purpose: {purpose}")

    print("\n[3] Contract validation")
    print("-" * 80)

    contract = data.get("contract_validation")

    if isinstance(contract, dict):
        for key, value in contract.items():
            print(f"{key}: {value}")
    else:
        print("contract_validation: NOT PRESENT")

    print("\n[4] Semantic lock validation")
    print("-" * 80)

    semantic = data.get("semantic_lock_validation")

    if isinstance(semantic, dict):
        for key, value in semantic.items():
            print(f"{key}: {value}")
    else:
        print("semantic_lock_validation: NOT PRESENT")

    print("\n[5] Task evidence status")
    print("-" * 80)

    task_evidence = data.get("task_evidence")

    if isinstance(task_evidence, dict):
        for task, evidence in task_evidence.items():
            print(f"\n{task}:")
            if isinstance(evidence, dict):
                for key, value in evidence.items():
                    print(f"  {key}: {value}")
            else:
                print(f"  {evidence}")
    else:
        print("task_evidence: NOT PRESENT")

    print("\n[6] Final evidence statement")
    print("-" * 80)

    final_statement = data.get("final_evidence_statement")

    if isinstance(final_statement, dict):
        for task, statement in final_statement.items():
            print(f"{task}: {statement}")
    else:
        print("final_evidence_statement: NOT PRESENT")

    print("\n[7] Closure checks")
    print("-" * 80)

    checks = {
        "artifact_exists": T9_CLOSURE.exists(),
        "status_present": status is not None,
        "contract_validation_present": isinstance(contract, dict),
        "semantic_lock_validation_present": isinstance(semantic, dict),
        "task_evidence_present": isinstance(task_evidence, dict),
        "final_evidence_statement_present":
            isinstance(final_statement, dict),

        "universal_score_not_created":
            contract.get("universal_score") is False
            if isinstance(contract, dict)
            else False,

        "cross_task_probability_comparability_disabled":
            semantic.get("cross_task_probability_comparability") is False
            if isinstance(semantic, dict)
            else False,

        "universal_confidence_disabled":
            semantic.get("universal_confidence") is False
            if isinstance(semantic, dict)
            else False,

        "universal_risk_disabled":
            semantic.get("universal_risk") is False
            if isinstance(semantic, dict)
            else False,

        "T6_binary_reinterpretation_disabled":
            semantic.get("T6_binary_reinterpretation") is False
            if isinstance(semantic, dict)
            else False,

        "T7_binary_conversion_disabled":
            semantic.get("T7_binary_conversion") is False
            if isinstance(semantic, dict)
            else False,

        "T7_censoring_relabelling_disabled":
            semantic.get("T7_censoring_relabelling") is False
            if isinstance(semantic, dict)
            else False,
    }

    for key, value in checks.items():
        print(f"{key}: {value}")

    print("\n[8] Operation safeguards")
    print("-" * 80)

    print("Predictions generated: False")
    print("Models loaded: False")
    print("Retraining performed: False")
    print("New calibration fitted: False")
    print("Evaluation performed: False")
    print("Threshold selected: False")
    print("Universal confidence score created: False")
    print("Universal risk score created: False")
    print("Artifacts modified: False")

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
        print("T9 is ready to close at the FMP level.")
    else:
        failed = [
            key for key, value in checks.items()
            if not value
        ]

        print(f"Failed checks: {failed}")
        print("\nSTATUS: BLOCKED")


if __name__ == "__main__":
    main()