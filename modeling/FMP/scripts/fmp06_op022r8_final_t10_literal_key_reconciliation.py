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
    print("FMP-06 OP-022R8 — FINAL T10 LITERAL-KEY RECONCILIATION")
    print("=" * 72)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    print("\n[1] Loading authoritative evidence...")

    data = {}

    for name, path in FILES.items():
        if not path.exists():
            raise FileNotFoundError(path)

        data[name] = load(path)
        print(f"  {name}: PRESENT")

    print("\n[2] T1–T7 reconciliation...")

    t1_t7 = data["t1_t7"]

    t1_t7_pass = (
        t1_t7["status"] == "PASS"
        and all(
            t1_t7["tasks"][task]["runtime_evidence_status"] == "PASS"
            for task in ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]
        )
    )

    for task in ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]:
        print(
            f"  {task}: "
            f"{t1_t7['tasks'][task]['runtime_evidence_status']}"
        )

    print(
        f"  T1–T7 reconciliation: "
        f"{'PASS' if t1_t7_pass else 'FAIL'}"
    )

    print("\n[3] End-to-end interface reconciliation...")

    e2e_status = data["e2e"]["status"]
    e2e_pass = e2e_status == "PASS"

    print(f"  T1–T7 → T8 → T9 → T10: {e2e_status}")

    print(
        f"  Interface reconciliation: "
        f"{'PASS' if e2e_pass else 'FAIL'}"
    )

    print("\n[4] T5 authoritative reconciliation...")

    t5 = data["t5_t10"]["T5"]

    t5_pass = (
        t5["status"] == "PASS"
        and t5["task_specific_pass_evidence"] is True
        and t5["frozen_artifacts_present"] is True
    )

    print(f"  T5 status: {t5['status']}")
    print(
        f"  Task-specific PASS evidence: "
        f"{t5['task_specific_pass_evidence']}"
    )
    print(
        f"  Frozen artifacts present: "
        f"{t5['frozen_artifacts_present']}"
    )
    print(
        f"  T5 reconciliation: "
        f"{'PASS' if t5_pass else 'FAIL'}"
    )

    print("\n[5] T10 literal-key extraction...")

    t10 = data["t10"]
    fields = t10["relevant_structured_fields"]

    # OP-022R5 established that these are literal keys
    # inside relevant_structured_fields.

    required_keys = [
        "$.determination.automation",
        "$.determination.human_review",
        "$.determination.universal_threshold",
        "$.determination.universal_confidence",
        "$.determination.universal_risk",
        "$.safeguards.new_threshold_selected",
        "$.safeguards.threshold_reoptimized",
        "$.safeguards.universal_confidence_created",
        "$.safeguards.universal_risk_created",
        "$.safeguards.synthetic_fusion_target_created",
    ]

    missing = [
        key for key in required_keys
        if key not in fields
    ]

    if missing:
        print("  REQUIRED T10 KEYS MISSING:")
        for key in missing:
            print(f"    {key}")

        raise KeyError(
            "Expected literal T10 keys were not found."
        )

    automation = fields["$.determination.automation"]
    human_review = fields["$.determination.human_review"]
    universal_threshold = fields["$.determination.universal_threshold"]
    universal_confidence = fields["$.determination.universal_confidence"]
    universal_risk = fields["$.determination.universal_risk"]

    new_threshold_selected = fields[
        "$.safeguards.new_threshold_selected"
    ]

    threshold_reoptimized = fields[
        "$.safeguards.threshold_reoptimized"
    ]

    universal_confidence_created = fields[
        "$.safeguards.universal_confidence_created"
    ]

    universal_risk_created = fields[
        "$.safeguards.universal_risk_created"
    ]

    synthetic_fusion_target_created = fields[
        "$.safeguards.synthetic_fusion_target_created"
    ]

    print(f"  AUTOMATION: {automation}")
    print(f"  HUMAN_REVIEW: {human_review}")
    print(f"  UNIVERSAL_THRESHOLD: {universal_threshold}")
    print(f"  UNIVERSAL_CONFIDENCE: {universal_confidence}")
    print(f"  UNIVERSAL_RISK: {universal_risk}")

    print(
        f"  New threshold selected: "
        f"{new_threshold_selected}"
    )

    print(
        f"  Threshold reoptimized: "
        f"{threshold_reoptimized}"
    )

    print(
        f"  Universal confidence created: "
        f"{universal_confidence_created}"
    )

    print(
        f"  Universal risk created: "
        f"{universal_risk_created}"
    )

    print(
        f"  Synthetic fusion target created: "
        f"{synthetic_fusion_target_created}"
    )

    t10_pass = (
        t10["status"] == "PASS"
        and automation == "NOT_ESTABLISHED"
        and human_review == "NOT_ESTABLISHED"
        and universal_threshold == "NOT_ESTABLISHED"
        and universal_confidence == "NOT_CREATED"
        and universal_risk == "NOT_CREATED"
        and new_threshold_selected is False
        and threshold_reoptimized is False
        and universal_confidence_created is False
        and universal_risk_created is False
        and synthetic_fusion_target_created is False
    )

    print(
        f"  T10 policy-boundary reconciliation: "
        f"{'PASS' if t10_pass else 'FAIL'}"
    )

    print("\n[6] T8 closure...")

    t8_status = data["t8"]["status"]
    t8_pass = t8_status in {"PASS", "COMPLETE", "CLOSED"}

    print(f"  T8 status: {t8_status}")

    print(
        f"  T8 reconciliation: "
        f"{'PASS' if t8_pass else 'FAIL'}"
    )

    print("\n[7] T9 closure...")

    t9_status = data["t9"]["status"]
    t9_pass = t9_status in {"PASS", "COMPLETE", "CLOSED"}

    print(f"  T9 status: {t9_status}")

    print(
        f"  T9 reconciliation: "
        f"{'PASS' if t9_pass else 'FAIL'}"
    )

    print("\n[8] Final reconciliation...")

    final_status = (
        "PASS"
        if (
            t1_t7_pass
            and e2e_pass
            and t5_pass
            and t10_pass
            and t8_pass
            and t9_pass
        )
        else "REQUIRES_REVIEW"
    )

    print(f"  T1–T7 runtime chain: {'PASS' if t1_t7_pass else 'FAIL'}")
    print(f"  E2E interface: {'PASS' if e2e_pass else 'FAIL'}")
    print(f"  T5: {'PASS' if t5_pass else 'FAIL'}")
    print(f"  T8: {'PASS' if t8_pass else 'FAIL'}")
    print(f"  T9: {'PASS' if t9_pass else 'FAIL'}")
    print(f"  T10 policy boundary: {'PASS' if t10_pass else 'FAIL'}")

    output = (
        METRICS
        / "fmp06_op022r8_final_t10_literal_key_reconciliation.json"
    )

    result = {
        "operation": "FMP-06 OP-022R8",
        "operation_name": "FINAL_T10_LITERAL_KEY_RECONCILIATION",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": final_status,
        "read_only": True,
        "training_performed": False,
        "fitting_performed": False,
        "prediction_performed": False,
        "evaluation_performed": False,
        "locked_test_used": False,
        "artifact_modified": False,
        "reconciliation": {
            "t1_t7_pass": t1_t7_pass,
            "e2e_pass": e2e_pass,
            "t5_pass": t5_pass,
            "t8_pass": t8_pass,
            "t9_pass": t9_pass,
            "t10_pass": t10_pass,
        },
        "t10_policy_boundary": {
            "automation": automation,
            "human_review": human_review,
            "universal_threshold": universal_threshold,
            "universal_confidence": universal_confidence,
            "universal_risk": universal_risk,
            "new_threshold_selected": new_threshold_selected,
            "threshold_reoptimized": threshold_reoptimized,
            "universal_confidence_created":
                universal_confidence_created,
            "universal_risk_created":
                universal_risk_created,
            "synthetic_fusion_target_created":
                synthetic_fusion_target_created,
        },
        "interpretation": (
            "Final reconciliation uses the exact literal T10 "
            "keys established by OP-022R5. No threshold is "
            "selected or optimized. AUTOMATION and HUMAN_REVIEW "
            "remain NOT_ESTABLISHED. Universal confidence and "
            "universal risk remain NOT_CREATED."
        ),
    }

    with output.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("\n" + "=" * 72)
    print("OP-022R8 RECONCILIATION COMPLETE")
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