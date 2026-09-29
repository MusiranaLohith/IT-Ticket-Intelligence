from __future__ import annotations

import json
from pathlib import Path


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

VALIDATION_ARTIFACT = (
    ROOT
    / "modeling"
    / "T8"
    / "mod036"
    / "op026"
    / "t8_mod036_op026_decision_engine_validation.json"
)


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    print("=" * 80)
    print("FMP-03 OP-004 — T8 FINAL INTERFACE CLOSURE CHECK")
    print("=" * 80)

    print("\n[1] Validation artifact")
    print("-" * 80)

    print(f"Path: {VALIDATION_ARTIFACT}")
    print(f"Exists: {VALIDATION_ARTIFACT.exists()}")

    if not VALIDATION_ARTIFACT.exists():
        print("\nSTATUS: BLOCKED")
        return

    data = read_json(VALIDATION_ARTIFACT)

    print("Readable JSON: True")

    print("\n[2] T8 closure state")
    print("-" * 80)

    status = data.get("status")
    closure_status = data.get("closure_status")

    print(f"status: {status}")
    print(f"closure_status: {closure_status}")

    print("\n[3] Closure criteria")
    print("-" * 80)

    closure_criteria = data.get("closure_criteria")

    if not isinstance(closure_criteria, dict):
        print("closure_criteria present: False")
        print("\nSTATUS: BLOCKED")
        return

    print("closure_criteria present: True")

    for key, value in closure_criteria.items():
        print(f"{key}: {value}")

    print("\n[4] Architecture safeguards")
    print("-" * 80)

    architecture = data.get("architecture")

    if not isinstance(architecture, dict):
        print("architecture present: False")
        print("\nSTATUS: BLOCKED")
        return

    print("architecture present: True")

    expected_safeguards = [
        "variable_evidence",
        "missing_evidence_is_unavailable",
        "native_task_semantics_preserved",
        "blind_probability_averaging",
        "arbitrary_cross_task_weights",
        "synthetic_universal_target",
        "post_creation_features_added",
    ]

    safeguard_results = {}

    for key in expected_safeguards:
        value = architecture.get(key)
        safeguard_results[key] = value
        print(f"{key}: {value}")

    print("\n[5] Limitations")
    print("-" * 80)

    limitations = data.get("limitations")

    print(f"limitations present: {isinstance(limitations, list)}")

    if isinstance(limitations, list):
        print(f"limitation count: {len(limitations)}")

        for item in limitations:
            print(f"- {item}")

    print("\n[6] Next phase")
    print("-" * 80)

    next_phase = data.get("next_phase")

    print(f"next_phase present: {isinstance(next_phase, dict)}")

    if isinstance(next_phase, dict):
        for key, value in next_phase.items():
            print(f"{key}: {value}")
    else:
        print(f"next_phase: {next_phase}")

    print("\n[7] Closure checks")
    print("-" * 80)

    checks = {
        "t8_status_pass": status == "PASS",
        "t8_decision_engine_closed": closure_status == "T8_DECISION_ENGINE_CLOSED",
        "closure_criteria_present": isinstance(closure_criteria, dict),
        "architecture_present": isinstance(architecture, dict),
        "variable_evidence_enabled":
            architecture.get("variable_evidence") is True,
        "missing_evidence_unavailable":
            architecture.get("missing_evidence_is_unavailable") is True,
        "native_semantics_preserved":
            architecture.get("native_task_semantics_preserved") is True,
        "blind_probability_averaging_disabled":
            architecture.get("blind_probability_averaging") is False,
        "arbitrary_cross_task_weights_disabled":
            architecture.get("arbitrary_cross_task_weights") is False,
        "synthetic_universal_target_disabled":
            architecture.get("synthetic_universal_target") is False,
        "post_creation_features_not_added":
            architecture.get("post_creation_features_added") is False,
        "limitations_present":
            isinstance(limitations, list),
        "next_phase_present":
            isinstance(next_phase, dict),
    }

    for key, value in checks.items():
        print(f"{key}: {value}")

    print("\n[8] Operation safeguards")
    print("-" * 80)

    print("Predictions generated: False")
    print("Models loaded: False")
    print("Retraining performed: False")
    print("Evaluation performed: False")
    print("Threshold selected: False")
    print("Artifacts modified: False")

    print("\n[9] Final summary")
    print("-" * 80)

    all_checks_pass = all(checks.values())

    print(f"All closure checks passed: {all_checks_pass}")

    if all_checks_pass:
        print("\nSTATUS: PASS")
        print("Operation type: READ_ONLY_T8_FINAL_INTERFACE_CLOSURE_CHECK")
        print("FMP-03 interface reconciliation is ready to close.")
    else:
        failed = [
            key
            for key, value in checks.items()
            if not value
        ]

        print(f"Failed checks: {failed}")
        print("\nSTATUS: BLOCKED")


if __name__ == "__main__":
    main()