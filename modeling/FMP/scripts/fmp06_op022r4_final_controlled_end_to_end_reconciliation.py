from pathlib import Path
import json
from datetime import datetime, timezone


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

METRICS = ROOT / "modeling" / "FMP" / "metrics"


SOURCES = {
    "t1_t7_runtime_binding": (
        METRICS / "fmp06_op019r1_final_t1_t7_runtime_binding_reconciliation.json"
    ),
    "end_to_end_interface": (
        METRICS / "fmp06_op021r1_corrected_end_to_end_runtime_chain_interface_audit.json"
    ),
    "t5_boundary": (
        METRICS / "fmp06_op022r2_t5_t10_authoritative_boundary_reconciliation.json"
    ),
    "t10_boundary": (
        METRICS / "fmp06_op022r3_t10_direct_policy_boundary_extraction.json"
    ),
    "t8_closure": (
        ROOT
        / "modeling"
        / "T8"
        / "mod036"
        / "op026"
        / "t8_mod036_op026_decision_engine_validation.json"
    ),
    "t9_closure": (
        ROOT
        / "modeling"
        / "T9"
        / "mod037"
        / "t9_mod037_op015_final_integrated_closure.json"
    ),
}


def load_json(path: Path):
    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def status_from_t1_t7(data):
    if not isinstance(data, dict):
        return "UNAVAILABLE"

    statuses = []

    for task in ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]:
        value = data.get(task)

        if isinstance(value, dict):
            status = value.get("runtime_status") or value.get("status")
            if status:
                statuses.append(str(status).upper())

    if statuses and all(
        s in {"PASS", "COMPLETE", "CLOSED", "SUPPORTED_WITH_LIMITATIONS"}
        for s in statuses
    ):
        return "PASS"

    return "REQUIRES_REVIEW"


def main():
    print("=" * 72)
    print("FMP-06 OP-022R4 — FINAL CONTROLLED END-TO-END RECONCILIATION")
    print("=" * 72)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    loaded = {}
    missing = []

    print("\n[1] Loading authoritative evidence...")

    for name, path in SOURCES.items():
        data = load_json(path)
        loaded[name] = data

        state = "PRESENT" if data is not None else "MISSING"
        print(f"  {name}: {state}")

        if data is None:
            missing.append(str(path))

    if missing:
        result = {
            "operation": "FMP-06 OP-022R4",
            "operation_name": "FINAL_CONTROLLED_END_TO_END_RECONCILIATION",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "status": "BLOCKED",
            "reason": "Required authoritative evidence file(s) missing.",
            "missing_files": missing,
        }

        output = METRICS / "fmp06_op022r4_final_controlled_end_to_end_reconciliation.json"
        output.parent.mkdir(parents=True, exist_ok=True)

        with output.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        print("\nSTATUS: BLOCKED")
        print(f"Output: {output}")
        return

    print("\n[2] T1–T7 runtime binding reconciliation...")

    t1_t7_status = status_from_t1_t7(loaded["t1_t7_runtime_binding"])

    print(f"  T1–T7 runtime binding: {t1_t7_status}")

    print("\n[3] End-to-end interface reconciliation...")

    e2e = loaded["end_to_end_interface"]

    e2e_status = str(
        e2e.get("status", e2e.get("overall_status", "UNKNOWN"))
    ).upper()

    print(f"  T1–T7 → T8 → T9 → T10 interface evidence: {e2e_status}")

    print("\n[4] T5 authoritative boundary reconciliation...")

    t5 = loaded["t5_boundary"]

    t5_status = str(
        t5.get("status", t5.get("overall_status", "UNKNOWN"))
    ).upper()

    print(f"  T5 boundary evidence: {t5_status}")

    print("\n[5] T10 authoritative policy-boundary reconciliation...")

    t10 = loaded["t10_boundary"]

    t10_policy_states = {
        "automation": None,
        "human_review": None,
        "universal_threshold": None,
        "universal_confidence": None,
        "universal_risk": None,
    }

    determination = t10.get("determination", {})

    if isinstance(determination, dict):
        for key in t10_policy_states:
            t10_policy_states[key] = determination.get(key)

    print(
        f"  AUTOMATION: "
        f"{t10_policy_states['automation']}"
    )
    print(
        f"  HUMAN_REVIEW: "
        f"{t10_policy_states['human_review']}"
    )
    print(
        f"  UNIVERSAL_THRESHOLD: "
        f"{t10_policy_states['universal_threshold']}"
    )
    print(
        f"  UNIVERSAL_CONFIDENCE: "
        f"{t10_policy_states['universal_confidence']}"
    )
    print(
        f"  UNIVERSAL_RISK: "
        f"{t10_policy_states['universal_risk']}"
    )

    print("\n[6] T8 closure reconciliation...")

    t8 = loaded["t8_closure"]

    t8_status = str(
        t8.get("status", t8.get("overall_status", "UNKNOWN"))
    ).upper()

    print(f"  T8 closure: {t8_status}")

    print("\n[7] T9 closure reconciliation...")

    t9 = loaded["t9_closure"]

    t9_status = str(
        t9.get("status", t9.get("overall_status", "UNKNOWN"))
    ).upper()

    print(f"  T9 closure: {t9_status}")

    print("\n[8] Final controlled interpretation...")

    runtime_chain_pass = (
        t1_t7_status == "PASS"
        and e2e_status == "PASS"
        and t5_status == "PASS"
        and t8_status in {"PASS", "COMPLETE", "CLOSED"}
        and t9_status in {"PASS", "COMPLETE", "CLOSED"}
    )

    policy_not_operationalized = (
        t10_policy_states["automation"] == "NOT_ESTABLISHED"
        and t10_policy_states["human_review"] == "NOT_ESTABLISHED"
        and t10_policy_states["universal_threshold"] == "NOT_ESTABLISHED"
        and t10_policy_states["universal_confidence"] == "NOT_CREATED"
        and t10_policy_states["universal_risk"] == "NOT_CREATED"
    )

    final_status = "PASS" if runtime_chain_pass and policy_not_operationalized else "REQUIRES_REVIEW"

    interpretation = {
        "runtime_evidence_chain": (
            "RECONCILED"
            if runtime_chain_pass
            else "NOT_FULLY_RECONCILED"
        ),
        "autonomous_policy_validation": (
            "NOT_ESTABLISHED"
            if policy_not_operationalized
            else "REQUIRES_REVIEW"
        ),
        "universal_confidence": "NOT_CREATED",
        "universal_risk": "NOT_CREATED",
        "synthetic_fusion_target": "NOT_CREATED",
        "threshold_selection_or_reoptimization": "NOT_PERFORMED",
        "final_meaning": (
            "The available evidence supports the reconciled "
            "T1–T10 evidence/integration chain while preserving "
            "the authoritative T10 boundary that empirically "
            "validated AUTOMATION and HUMAN_REVIEW policy boundaries "
            "are not established."
        ),
    }

    print(f"  Runtime evidence chain: {interpretation['runtime_evidence_chain']}")
    print(
        "  Autonomous policy validation: "
        f"{interpretation['autonomous_policy_validation']}"
    )
    print("  Universal confidence: NOT_CREATED")
    print("  Universal risk: NOT_CREATED")
    print("  Synthetic fusion target: NOT_CREATED")
    print("  Threshold selection/reoptimization: NOT_PERFORMED")

    result = {
        "operation": "FMP-06 OP-022R4",
        "operation_name": "FINAL_CONTROLLED_END_TO_END_RECONCILIATION",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": final_status,
        "read_only": True,
        "training_performed": False,
        "fitting_performed": False,
        "prediction_performed": False,
        "evaluation_performed": False,
        "locked_test_used": False,
        "artifact_modification": False,
        "authoritative_sources": {
            name: str(path)
            for name, path in SOURCES.items()
        },
        "reconciled_components": {
            "t1_t7_runtime_binding": t1_t7_status,
            "end_to_end_interface": e2e_status,
            "t5_boundary": t5_status,
            "t8_closure": t8_status,
            "t9_closure": t9_status,
        },
        "t10_authoritative_policy_state": t10_policy_states,
        "interpretation": interpretation,
    }

    output = METRICS / "fmp06_op022r4_final_controlled_end_to_end_reconciliation.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("\n" + "=" * 72)
    print("OP-022R4 RECONCILIATION COMPLETE")
    print("=" * 72)
    print(f"STATUS: {final_status}")
    print(f"Output: {output}")
    print("No training performed.")
    print("No fitting performed.")
    print("No prediction performed.")
    print("No evaluation performed.")
    print("No locked test used.")
    print("No artifact modification performed.")


if __name__ == "__main__":
    main()