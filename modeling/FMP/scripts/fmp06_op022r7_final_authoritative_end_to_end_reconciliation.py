from pathlib import Path
import json
from datetime import datetime, timezone


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
METRICS = ROOT / "modeling" / "FMP" / "metrics"


FILES = {
    "t1_t7": METRICS / "fmp06_op019r1_final_t1_t7_runtime_binding_reconciliation.json",
    "e2e": METRICS / "fmp06_op021r1_corrected_end_to_end_runtime_chain_interface_audit.json",
    "t5_t10": METRICS / "fmp06_op022r2_t5_t10_authoritative_boundary_reconciliation.json",
    "t10": METRICS / "fmp06_op022r3_t10_direct_policy_boundary_extraction.json",
    "t8": ROOT / "modeling" / "T8" / "mod036" / "op026"
        / "t8_mod036_op026_decision_engine_validation.json",
    "t9": ROOT / "modeling" / "T9" / "mod037"
        / "t9_mod037_op015_final_integrated_closure.json",
}


def load(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("=" * 72)
    print("FMP-06 OP-022R7 — CORRECTED FINAL AUTHORITATIVE END-TO-END RECONCILIATION")
    print("=" * 72)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    print("\n[1] Loading exact authoritative evidence...")

    data = {}

    for name, path in FILES.items():
        if not path.exists():
            print(f"  {name}: MISSING")
            raise FileNotFoundError(path)

        data[name] = load(path)
        print(f"  {name}: PRESENT")

    print("\n[2] T1–T7 authoritative runtime reconciliation...")

    t1_t7 = data["t1_t7"]

    t1_t7_status = t1_t7["status"]

    task_statuses = {
        task: details["runtime_evidence_status"]
        for task, details in t1_t7["tasks"].items()
    }

    for task in ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]:
        print(f"  {task}: {task_statuses[task]}")

    t1_t7_pass = (
        t1_t7_status == "PASS"
        and all(
            task_statuses[task] == "PASS"
            for task in ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]
        )
    )

    print(f"  Overall: {t1_t7_status}")
    print(f"  T1–T7 reconciliation: {'PASS' if t1_t7_pass else 'FAIL'}")

    print("\n[3] End-to-end interface reconciliation...")

    e2e = data["e2e"]
    e2e_status = e2e["status"]

    print(f"  T1–T7 → T8 → T9 → T10: {e2e_status}")

    e2e_pass = e2e_status == "PASS"

    print(f"  Interface reconciliation: {'PASS' if e2e_pass else 'FAIL'}")

    print("\n[4] T5 authoritative boundary reconciliation...")

    t5_t10 = data["t5_t10"]

    t5_status = t5_t10["T5"]["status"]
    t5_task_specific = t5_t10["T5"]["task_specific_pass_evidence"]
    t5_artifacts = t5_t10["T5"]["frozen_artifacts_present"]

    print(f"  T5 status: {t5_status}")
    print(f"  Task-specific PASS evidence: {t5_task_specific}")
    print(f"  Frozen artifacts present: {t5_artifacts}")

    t5_pass = (
        t5_status == "PASS"
        and t5_task_specific is True
        and t5_artifacts is True
    )

    print(f"  T5 reconciliation: {'PASS' if t5_pass else 'FAIL'}")

    print("\n[5] T10 authoritative policy-boundary reconciliation...")

    t10 = data["t10"]

    # OP-022R5 established that:
    #
    # $.relevant_structured_fields.$.determination.*
    # $.relevant_structured_fields.$.safeguards.*
    #
    # are the authoritative extracted fields.

    relevant = t10["relevant_structured_fields"]["$"]

    determination = relevant["$.determination"]
    safeguards = relevant["$.safeguards"]

    automation = determination["automation"]
    human_review = determination["human_review"]
    universal_threshold = determination["universal_threshold"]
    universal_confidence = determination["universal_confidence"]
    universal_risk = determination["universal_risk"]

    print(f"  AUTOMATION: {automation}")
    print(f"  HUMAN_REVIEW: {human_review}")
    print(f"  UNIVERSAL_THRESHOLD: {universal_threshold}")
    print(f"  UNIVERSAL_CONFIDENCE: {universal_confidence}")
    print(f"  UNIVERSAL_RISK: {universal_risk}")

    print(
        f"  New threshold selected: "
        f"{safeguards['new_threshold_selected']}"
    )

    print(
        f"  Threshold reoptimized: "
        f"{safeguards['threshold_reoptimized']}"
    )

    print(
        f"  Universal confidence created: "
        f"{safeguards['universal_confidence_created']}"
    )

    print(
        f"  Universal risk created: "
        f"{safeguards['universal_risk_created']}"
    )

    print(
        f"  Synthetic fusion target created: "
        f"{safeguards['synthetic_fusion_target_created']}"
    )

    t10_policy_boundary_preserved = (
        automation == "NOT_ESTABLISHED"
        and human_review == "NOT_ESTABLISHED"
        and universal_threshold == "NOT_ESTABLISHED"
        and universal_confidence == "NOT_CREATED"
        and universal_risk == "NOT_CREATED"
        and safeguards["new_threshold_selected"] is False
        and safeguards["threshold_reoptimized"] is False
        and safeguards["universal_confidence_created"] is False
        and safeguards["universal_risk_created"] is False
        and safeguards["synthetic_fusion_target_created"] is False
    )

    print(
        "  T10 policy-boundary preservation: "
        f"{'PASS' if t10_policy_boundary_preserved else 'FAIL'}"
    )

    print("\n[6] T8 closure reconciliation...")

    t8_status = data["t8"]["status"]

    print(f"  T8 status: {t8_status}")

    t8_pass = t8_status in {"PASS", "COMPLETE", "CLOSED"}

    print(f"  T8 reconciliation: {'PASS' if t8_pass else 'FAIL'}")

    print("\n[7] T9 closure reconciliation...")

    t9_status = data["t9"]["status"]

    print(f"  T9 status: {t9_status}")

    t9_pass = t9_status in {"PASS", "COMPLETE", "CLOSED"}

    print(f"  T9 reconciliation: {'PASS' if t9_pass else 'FAIL'}")

    print("\n[8] Final authoritative interpretation...")

    runtime_chain_pass = (
        t1_t7_pass
        and e2e_pass
        and t5_pass
        and t8_pass
        and t9_pass
    )

    final_status = (
        "PASS"
        if runtime_chain_pass and t10_policy_boundary_preserved
        else "REQUIRES_REVIEW"
    )

    interpretation = {
        "runtime_evidence_chain": (
            "PASS" if runtime_chain_pass else "REQUIRES_REVIEW"
        ),
        "t10_policy_boundary": (
            "PRESERVED"
            if t10_policy_boundary_preserved
            else "REQUIRES_REVIEW"
        ),
        "automation": automation,
        "human_review": human_review,
        "universal_threshold": universal_threshold,
        "universal_confidence": universal_confidence,
        "universal_risk": universal_risk,
        "threshold_selection": "NOT_PERFORMED",
        "threshold_reoptimization": "NOT_PERFORMED",
        "synthetic_fusion_target": "NOT_CREATED",
        "overall_meaning": (
            "The authoritative evidence reconciles the T1–T7 "
            "runtime binding, the T1–T7 to T8 to T9 to T10 "
            "interface chain, T5 task-specific evidence, T8 "
            "closure, and T9 closure. The authoritative T10 "
            "policy boundary is preserved: AUTOMATION and "
            "HUMAN_REVIEW remain NOT_ESTABLISHED, while no "
            "universal threshold, confidence, or risk construct "
            "is created."
        ),
    }

    print(
        f"  Runtime evidence chain: "
        f"{interpretation['runtime_evidence_chain']}"
    )

    print(
        f"  T10 policy boundary: "
        f"{interpretation['t10_policy_boundary']}"
    )

    print(f"  Automation: {automation}")
    print(f"  Human review: {human_review}")
    print(f"  Universal threshold: {universal_threshold}")
    print(f"  Universal confidence: {universal_confidence}")
    print(f"  Universal risk: {universal_risk}")

    output = (
        METRICS
        / "fmp06_op022r7_final_authoritative_end_to_end_reconciliation.json"
    )

    result = {
        "operation": "FMP-06 OP-022R7",
        "operation_name": "CORRECTED_FINAL_AUTHORITATIVE_END_TO_END_RECONCILIATION",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": final_status,
        "read_only": True,
        "training_performed": False,
        "fitting_performed": False,
        "prediction_performed": False,
        "evaluation_performed": False,
        "locked_test_used": False,
        "artifact_modified": False,
        "authoritative_inputs": {
            name: str(path)
            for name, path in FILES.items()
        },
        "reconciliation": {
            "t1_t7": {
                "status": t1_t7_status,
                "task_statuses": task_statuses,
                "pass": t1_t7_pass,
            },
            "e2e_interface": {
                "status": e2e_status,
                "pass": e2e_pass,
            },
            "t5": {
                "status": t5_status,
                "task_specific_pass_evidence": t5_task_specific,
                "frozen_artifacts_present": t5_artifacts,
                "pass": t5_pass,
            },
            "t8": {
                "status": t8_status,
                "pass": t8_pass,
            },
            "t9": {
                "status": t9_status,
                "pass": t9_pass,
            },
            "t10": {
                "policy_boundary_preserved":
                    t10_policy_boundary_preserved,
                "automation": automation,
                "human_review": human_review,
                "universal_threshold": universal_threshold,
                "universal_confidence": universal_confidence,
                "universal_risk": universal_risk,
                "new_threshold_selected":
                    safeguards["new_threshold_selected"],
                "threshold_reoptimized":
                    safeguards["threshold_reoptimized"],
                "universal_confidence_created":
                    safeguards["universal_confidence_created"],
                "universal_risk_created":
                    safeguards["universal_risk_created"],
                "synthetic_fusion_target_created":
                    safeguards["synthetic_fusion_target_created"],
            },
        },
        "interpretation": interpretation,
    }

    with output.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("\n" + "=" * 72)
    print("OP-022R7 RECONCILIATION COMPLETE")
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