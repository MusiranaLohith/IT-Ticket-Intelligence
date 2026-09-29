from pathlib import Path
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
METRICS = ROOT / "modeling/FMP/metrics"

OUT = METRICS / (
    "fmp06_op021_end_to_end_runtime_chain_interface_audit.json"
)


REQUIRED_EVIDENCE = {
    "T1_T7_RUNTIME_BINDING":
        "fmp06_op019r1_final_t1_t7_runtime_binding_reconciliation.json",

    "T8_RUNTIME_VALIDATION":
        "t8_mod036_op026_decision_engine_validation.json",

    "T9_FINAL_CLOSURE":
        "t9_mod037_op015_final_integrated_closure.json",

    "T10_POLICY_EVIDENCE":
        "fmp05_op008_empirical_policy_boundary_audit.json",
}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def recursive_text(obj):
    return json.dumps(obj, sort_keys=True).lower()


def main():
    print("=" * 72)
    print("FMP-06 OP-021 — END-TO-END RUNTIME CHAIN INTERFACE AUDIT")
    print("=" * 72)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation metrics: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    results = {}
    overall_pass = True

    print("\n[1] Checking authoritative chain evidence...")

    loaded = {}

    for name, filename in REQUIRED_EVIDENCE.items():
        path = METRICS / filename
        exists = path.exists()

        print(
            f"  {name}: "
            f"{'PRESENT' if exists else 'MISSING'}"
        )

        if not exists:
            overall_pass = False
            results[name] = {
                "path": str(path),
                "exists": False,
            }
            continue

        try:
            data = load_json(path)
            loaded[name] = data

            results[name] = {
                "path": str(path),
                "exists": True,
                "readable": True,
            }
        except Exception as exc:
            overall_pass = False
            results[name] = {
                "path": str(path),
                "exists": True,
                "readable": False,
                "error": str(exc),
            }

    print("\n[2] T1–T7 → T8 interface audit...")

    t17 = loaded.get("T1_T7_RUNTIME_BINDING")
    t8 = loaded.get("T8_RUNTIME_VALIDATION")

    t17_ok = (
        isinstance(t17, dict)
        and t17.get("status") == "PASS"
    )

    t8_text = recursive_text(t8) if t8 else ""

    t8_native_semantics = (
        "native" in t8_text
        and (
            "semantic" in t8_text
            or "evidence" in t8_text
        )
    )

    t8_no_universal_target = (
        "synthetic" in t8_text
        or "universal" in t8_text
    )

    t17_t8_pass = (
        t17_ok
        and t8 is not None
        and t8_native_semantics
    )

    print(
        f"  T1–T7 binding PASS: {t17_ok}"
    )
    print(
        f"  T8 native/evidence semantics present: "
        f"{t8_native_semantics}"
    )
    print(
        f"  T1–T7 → T8 interface: "
        f"{'PASS' if t17_t8_pass else 'REQUIRES_REVIEW'}"
    )

    if not t17_t8_pass:
        overall_pass = False

    results["T1_T7_TO_T8"] = {
        "t1_t7_binding_pass": t17_ok,
        "t8_native_evidence_semantics_present":
            t8_native_semantics,
        "textual_universal_or_synthetic_terms_present":
            t8_no_universal_target,
        "status":
            "PASS" if t17_t8_pass else "REQUIRES_REVIEW",
    }

    print("\n[3] T8 → T9 interface audit...")

    t9 = loaded.get("T9_FINAL_CLOSURE")

    t9_text = recursive_text(t9) if t9 else ""

    t9_loaded = t9 is not None

    t9_evidence_language = (
        "evidence" in t9_text
        and (
            "t8" in t9_text
            or "cross-task" in t9_text
            or "fusion" in t9_text
        )
    )

    t9_universal_guard = (
        "universal_confidence" in t9_text
        or "universal_risk" in t9_text
    )

    t8_t9_pass = (
        t9_loaded
        and t9_evidence_language
    )

    print(
        f"  T9 closure readable: {t9_loaded}"
    )
    print(
        f"  T9 evidence integration terms present: "
        f"{t9_evidence_language}"
    )
    print(
        f"  Universal confidence/risk fields present: "
        f"{t9_universal_guard}"
    )
    print(
        f"  T8 → T9 interface: "
        f"{'PASS' if t8_t9_pass else 'REQUIRES_REVIEW'}"
    )

    if not t8_t9_pass:
        overall_pass = False

    results["T8_TO_T9"] = {
        "t9_closure_readable": t9_loaded,
        "t9_evidence_integration_present":
            t9_evidence_language,
        "universal_confidence_or_risk_fields_present":
            t9_universal_guard,
        "status":
            "PASS" if t8_t9_pass else "REQUIRES_REVIEW",
    }

    print("\n[4] T9 → T10 policy interface audit...")

    t10 = loaded.get("T10_POLICY_EVIDENCE")

    t10_text = recursive_text(t10) if t10 else ""

    t10_loaded = t10 is not None

    policy_terms = [
        "policy",
        "human_review",
        "defer",
        "automation",
    ]

    policy_term_count = sum(
        term in t10_text
        for term in policy_terms
    )

    t10_policy_interface = (
        t10_loaded
        and policy_term_count >= 2
    )

    unsupported_threshold_terms = (
        "validated threshold" in t10_text
        or "empirically validated threshold" in t10_text
    )

    t9_t10_pass = t10_policy_interface

    print(
        f"  T10 policy evidence readable: {t10_loaded}"
    )
    print(
        f"  Policy interface terms detected: "
        f"{policy_term_count}/4"
    )
    print(
        f"  Empirically validated threshold claim detected: "
        f"{unsupported_threshold_terms}"
    )
    print(
        f"  T9 → T10 interface: "
        f"{'PASS' if t9_t10_pass else 'REQUIRES_REVIEW'}"
    )

    if not t9_t10_pass:
        overall_pass = False

    results["T9_TO_T10"] = {
        "t10_policy_evidence_readable":
            t10_loaded,
        "policy_interface_term_count":
            policy_term_count,
        "empirically_validated_threshold_claim_detected":
            unsupported_threshold_terms,
        "status":
            "PASS" if t9_t10_pass else "REQUIRES_REVIEW",
    }

    print("\n[5] Final chain interpretation...")

    if overall_pass:
        final_status = "PASS"
    else:
        final_status = "REQUIRES_REVIEW"

    print(
        f"  T1–T7 → T8: "
        f"{results['T1_T7_TO_T8']['status']}"
    )

    print(
        f"  T8 → T9: "
        f"{results['T8_TO_T9']['status']}"
    )

    print(
        f"  T9 → T10: "
        f"{results['T9_TO_T10']['status']}"
    )

    print("=" * 72)
    print(f"FINAL STATUS: {final_status}")
    print("=" * 72)

    output = {
        "operation":
            "FMP-06 OP-021",

        "status":
            final_status,

        "read_only":
            True,

        "training_performed":
            False,

        "fitting_performed":
            False,

        "prediction_performed":
            False,

        "evaluation_performed":
            False,

        "locked_test_used":
            False,

        "artifact_modified":
            False,

        "interfaces":
            results,

        "interpretation":
            (
                "This operation audits compatibility of the "
                "already-established T1-T7, T8, T9, and T10 "
                "evidence interfaces. It does not execute a "
                "new end-to-end prediction chain and does not "
                "create unsupported universal confidence, risk, "
                "or automation thresholds."
            ),
    }

    OUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUT.open(
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            output,
            f,
            indent=2
        )

    print(f"\nOutput: {OUT}")
    print("No training performed.")
    print("No fitting performed.")
    print("No prediction performed.")
    print("No evaluation performed.")
    print("No locked test used.")
    print("No artifact modification performed.")


if __name__ == "__main__":
    main()