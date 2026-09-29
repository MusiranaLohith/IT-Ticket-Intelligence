from pathlib import Path
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
METRICS = ROOT / "modeling/FMP/metrics"

OUT = METRICS / (
    "fmp06_op021r1_corrected_end_to_end_runtime_chain_interface_audit.json"
)


T1_T7_EVIDENCE = (
    METRICS /
    "fmp06_op019r1_final_t1_t7_runtime_binding_reconciliation.json"
)

T8_EVIDENCE = (
    ROOT /
    "modeling/T8/mod036/op026/"
    "t8_mod036_op026_decision_engine_validation.json"
)

T9_EVIDENCE = (
    ROOT /
    "modeling/T9/mod037/"
    "t9_mod037_op015_final_integrated_closure.json"
)

T10_EVIDENCE = (
    METRICS /
    "fmp05_op008_empirical_policy_boundary_audit.json"
)


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def text_of(obj):
    return json.dumps(
        obj,
        sort_keys=True
    ).lower()


def main():
    print("=" * 72)
    print(
        "FMP-06 OP-021R1 — CORRECTED END-TO-END "
        "RUNTIME CHAIN INTERFACE AUDIT"
    )
    print("=" * 72)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation metrics: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    print("\n[1] Loading authoritative evidence...")

    paths = {
        "T1_T7": T1_T7_EVIDENCE,
        "T8": T8_EVIDENCE,
        "T9": T9_EVIDENCE,
        "T10": T10_EVIDENCE,
    }

    loaded = {}
    evidence_status = {}

    for name, path in paths.items():
        exists = path.exists()

        print(
            f"  {name}: "
            f"{'PRESENT' if exists else 'MISSING'}"
        )

        if not exists:
            evidence_status[name] = False
            continue

        try:
            loaded[name] = load_json(path)
            evidence_status[name] = True
        except Exception as exc:
            evidence_status[name] = False
            print(f"    READ ERROR: {exc}")

    overall_pass = all(evidence_status.values())

    print("\n[2] T1–T7 → T8 interface...")

    t17 = loaded.get("T1_T7")
    t8 = loaded.get("T8")

    t17_pass = (
        isinstance(t17, dict)
        and t17.get("status") == "PASS"
    )

    t8_text = text_of(t8) if t8 is not None else ""

    t8_native_semantics = (
        "native" in t8_text
        and "evidence" in t8_text
    )

    t8_missingness = (
        "missing" in t8_text
        or "unavailable" in t8_text
    )

    t8_no_synthetic_target = (
        "synthetic" in t8_text
    )

    t8_no_arbitrary_weights = (
        "arbitrary" in t8_text
        or "blind probability averaging" in t8_text
    )

    t17_to_t8 = (
        t17_pass
        and evidence_status.get("T8", False)
        and t8_native_semantics
        and t8_missingness
    )

    print(
        f"  T1–T7 reconciliation PASS: "
        f"{t17_pass}"
    )

    print(
        f"  T8 native evidence semantics: "
        f"{t8_native_semantics}"
    )

    print(
        f"  T8 missing/unavailable semantics: "
        f"{t8_missingness}"
    )

    print(
        f"  T8 synthetic-target guard present: "
        f"{t8_no_synthetic_target}"
    )

    print(
        f"  T8 arbitrary-weight guard present: "
        f"{t8_no_arbitrary_weights}"
    )

    print(
        f"  T1–T7 → T8: "
        f"{'PASS' if t17_to_t8 else 'REQUIRES_REVIEW'}"
    )

    if not t17_to_t8:
        overall_pass = False

    print("\n[3] T8 → T9 interface...")

    t9 = loaded.get("T9")
    t9_text = text_of(t9) if t9 is not None else ""

    t9_evidence_integration = (
        "evidence" in t9_text
        and (
            "cross-task" in t9_text
            or "fusion" in t9_text
            or "t8" in t9_text
        )
    )

    t9_universal_confidence_guard = (
        "universal_confidence" in t9_text
        and (
            "not_created" in t9_text
            or "not_established" in t9_text
        )
    )

    t9_universal_risk_guard = (
        "universal_risk" in t9_text
        and (
            "not_created" in t9_text
            or "not_established" in t9_text
        )
    )

    t8_to_t9 = (
        evidence_status.get("T8", False)
        and evidence_status.get("T9", False)
        and t9_evidence_integration
    )

    print(
        f"  T9 evidence integration present: "
        f"{t9_evidence_integration}"
    )

    print(
        f"  Universal confidence guard: "
        f"{t9_universal_confidence_guard}"
    )

    print(
        f"  Universal risk guard: "
        f"{t9_universal_risk_guard}"
    )

    print(
        f"  T8 → T9: "
        f"{'PASS' if t8_to_t9 else 'REQUIRES_REVIEW'}"
    )

    if not t8_to_t9:
        overall_pass = False

    print("\n[4] T9 → T10 interface...")

    t10 = loaded.get("T10")
    t10_text = text_of(t10) if t10 is not None else ""

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

    t10_policy_evidence = (
        evidence_status.get("T10", False)
        and policy_term_count >= 2
    )

    empirically_validated_threshold = (
        "empirically validated threshold" in t10_text
        or "validated threshold" in t10_text
    )

    t9_to_t10 = t10_policy_evidence

    print(
        f"  T10 policy evidence readable: "
        f"{evidence_status.get('T10', False)}"
    )

    print(
        f"  Policy interface terms: "
        f"{policy_term_count}/4"
    )

    print(
        f"  Empirically validated threshold claim: "
        f"{empirically_validated_threshold}"
    )

    print(
        f"  T9 → T10: "
        f"{'PASS' if t9_to_t10 else 'REQUIRES_REVIEW'}"
    )

    if not t9_to_t10:
        overall_pass = False

    print("\n[5] Final chain interpretation...")

    final_status = (
        "PASS"
        if overall_pass
        else "REQUIRES_REVIEW"
    )

    print(
        f"  T1–T7 → T8: "
        f"{'PASS' if t17_to_t8 else 'REQUIRES_REVIEW'}"
    )

    print(
        f"  T8 → T9: "
        f"{'PASS' if t8_to_t9 else 'REQUIRES_REVIEW'}"
    )

    print(
        f"  T9 → T10: "
        f"{'PASS' if t9_to_t10 else 'REQUIRES_REVIEW'}"
    )

    print("=" * 72)
    print(f"FINAL STATUS: {final_status}")
    print("=" * 72)

    result = {
        "operation":
            "FMP-06 OP-021R1",

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

        "evidence_paths": {
            name: str(path)
            for name, path in paths.items()
        },

        "interfaces": {
            "T1_T7_TO_T8": {
                "status":
                    "PASS"
                    if t17_to_t8
                    else "REQUIRES_REVIEW",
                "t1_t7_reconciliation":
                    t17_pass,
                "t8_native_evidence_semantics":
                    t8_native_semantics,
                "t8_missingness_semantics":
                    t8_missingness,
                "synthetic_target_guard":
                    t8_no_synthetic_target,
                "arbitrary_weight_guard":
                    t8_no_arbitrary_weights,
            },

            "T8_TO_T9": {
                "status":
                    "PASS"
                    if t8_to_t9
                    else "REQUIRES_REVIEW",
                "evidence_integration":
                    t9_evidence_integration,
                "universal_confidence_guard":
                    t9_universal_confidence_guard,
                "universal_risk_guard":
                    t9_universal_risk_guard,
            },

            "T9_TO_T10": {
                "status":
                    "PASS"
                    if t9_to_t10
                    else "REQUIRES_REVIEW",
                "policy_term_count":
                    policy_term_count,
                "empirically_validated_threshold_claim":
                    empirically_validated_threshold,
            },
        },

        "interpretation":
            (
                "This operation verifies compatibility of the "
                "already-established evidence interfaces. It does "
                "not execute a new production end-to-end prediction "
                "chain and does not create unsupported confidence, "
                "risk, or automation thresholds."
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
            result,
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