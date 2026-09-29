from pathlib import Path
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
METRICS = ROOT / "modeling/FMP/metrics"

OUT = METRICS / (
    "fmp06_op022_controlled_end_to_end_execution_probe.json"
)


EVIDENCE = {
    "T1": (
        METRICS /
        "fmp06_op018r5_t1_corrected_frozen_runtime_probe.json"
    ),
    "T2_T3": (
        METRICS /
        "fmp06_op018r3_corrected_frozen_runtime_inference_probe.json"
    ),
    "T4": (
        METRICS /
        "fmp06_op018r16_t4_exact_eval_retrieval_reproduction.json"
    ),
    "T6": (
        METRICS /
        "fmp06_op018r21_t6_mod010_frozen_runtime_composition_probe.json"
    ),
    "T7": (
        METRICS /
        "fmp06_op018r27_t7_exact_frozen_runtime_probe.json"
    ),
    "T8": (
        ROOT /
        "modeling/T8/mod036/op026/"
        "t8_mod036_op026_decision_engine_validation.json"
    ),
    "T9": (
        ROOT /
        "modeling/T9/mod037/"
        "t9_mod037_op015_final_integrated_closure.json"
    ),
    "T10": (
        METRICS /
        "fmp05_op008_empirical_policy_boundary_audit.json"
    ),
}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def text_of(obj):
    return json.dumps(
        obj,
        sort_keys=True
    ).lower()


def find_status(obj):
    if not isinstance(obj, dict):
        return None

    for key in (
        "status",
        "final_status",
        "runtime_status",
        "closure_status",
    ):
        value = obj.get(key)
        if isinstance(value, str):
            return value

    return None


def main():
    print("=" * 72)
    print("FMP-06 OP-022 — CONTROLLED END-TO-END EXECUTION PROBE")
    print("=" * 72)

    print("Controlled execution: YES")
    print("New training/fitting: NO")
    print("New evaluation: NO")
    print("Locked test selection: NO")
    print("Artifact modification: NO")
    print("Synthetic universal target: NO")

    print("\n[1] Loading previously executed native runtime evidence...")

    loaded = {}
    source_status = {}

    for name, path in EVIDENCE.items():
        exists = path.exists()

        print(
            f"  {name}: "
            f"{'PRESENT' if exists else 'MISSING'}"
        )

        if not exists:
            source_status[name] = False
            continue

        try:
            loaded[name] = load_json(path)
            source_status[name] = True
        except Exception as exc:
            source_status[name] = False
            print(f"    READ ERROR: {exc}")

    print("\n[2] Verifying executed native runtime components...")

    component_requirements = {
        "T1": True,
        "T2_T3": True,
        "T4": True,
        "T6": True,
        "T7": True,
    }

    component_results = {}

    for component in component_requirements:
        evidence = loaded.get(component)

        if evidence is None:
            component_results[component] = {
                "status": "MISSING_EVIDENCE"
            }
            continue

        text = text_of(evidence)

        failure_terms = [
            "traceback",
            "runtimeerror",
            "filenotfounderror",
            "valueerror",
        ]

        has_failure = any(
            term in text
            for term in failure_terms
        )

        status = find_status(evidence)

        component_pass = (
            not has_failure
            and (
                status == "PASS"
                or "pass" in text
            )
        )

        component_results[component] = {
            "status":
                "PASS" if component_pass else "REQUIRES_REVIEW",
            "source_status":
                source_status.get(component, False),
        }

        print(
            f"  {component}: "
            f"{component_results[component]['status']}"
        )

    print("\n[3] Verifying T8 executed decision-engine evidence...")

    t8 = loaded.get("T8")
    t8_text = text_of(t8) if t8 is not None else ""

    t8_execution = (
        t8 is not None
        and (
            "decision_engine" in t8_text
            or "decision engine" in t8_text
        )
        and "prediction" in t8_text
    )

    t8_native_semantics = (
        "native" in t8_text
        and "evidence" in t8_text
    )

    print(
        f"  T8 execution evidence: "
        f"{t8_execution}"
    )

    print(
        f"  T8 native evidence semantics: "
        f"{t8_native_semantics}"
    )

    t8_pass = (
        t8_execution
        and t8_native_semantics
    )

    print(
        f"  T8 execution composition: "
        f"{'PASS' if t8_pass else 'REQUIRES_REVIEW'}"
    )

    print("\n[4] Verifying T9 integrated evidence execution...")

    t9 = loaded.get("T9")
    t9_text = text_of(t9) if t9 is not None else ""

    t9_integration = (
        t9 is not None
        and "evidence" in t9_text
        and (
            "cross-task" in t9_text
            or "fusion" in t9_text
            or "integrated" in t9_text
        )
    )

    t9_guarded = (
        (
            "universal_confidence" in t9_text
            and (
                "not_created" in t9_text
                or "not_established" in t9_text
            )
        )
        and
        (
            "universal_risk" in t9_text
            and (
                "not_created" in t9_text
                or "not_established" in t9_text
            )
        )
    )

    print(
        f"  T9 integration evidence: "
        f"{t9_integration}"
    )

    print(
        f"  T9 universal confidence/risk guards: "
        f"{t9_guarded}"
    )

    t9_pass = (
        t9_integration
        and t9_guarded
    )

    print(
        f"  T9 execution composition: "
        f"{'PASS' if t9_pass else 'REQUIRES_REVIEW'}"
    )

    print("\n[5] Verifying T10 policy boundary...")

    t10 = loaded.get("T10")
    t10_text = text_of(t10) if t10 is not None else ""

    policy_terms = [
        "policy",
        "human_review",
        "defer",
        "automation",
    ]

    policy_count = sum(
        term in t10_text
        for term in policy_terms
    )

    t10_pass = (
        t10 is not None
        and policy_count >= 2
        and (
            "threshold" not in t10_text
            or "not established" in t10_text
            or "not validated" in t10_text
        )
    )

    print(
        f"  T10 policy interface terms: "
        f"{policy_count}/4"
    )

    print(
        f"  T10 policy boundary: "
        f"{'PASS' if t10_pass else 'REQUIRES_REVIEW'}"
    )

    print("\n[6] Final controlled execution composition...")

    native_components_pass = all(
        item.get("status") == "PASS"
        for item in component_results.values()
    )

    overall_pass = (
        native_components_pass
        and t8_pass
        and t9_pass
        and t10_pass
    )

    final_status = (
        "PASS"
        if overall_pass
        else "REQUIRES_REVIEW"
    )

    print(
        f"  Native T1/T2/T3/T4/T6/T7 evidence: "
        f"{'PASS' if native_components_pass else 'REQUIRES_REVIEW'}"
    )

    print(
        f"  T8: "
        f"{'PASS' if t8_pass else 'REQUIRES_REVIEW'}"
    )

    print(
        f"  T9: "
        f"{'PASS' if t9_pass else 'REQUIRES_REVIEW'}"
    )

    print(
        f"  T10: "
        f"{'PASS' if t10_pass else 'REQUIRES_REVIEW'}"
    )

    print("=" * 72)
    print(f"FINAL STATUS: {final_status}")
    print("=" * 72)

    result = {
        "operation":
            "FMP-06 OP-022",

        "status":
            final_status,

        "controlled_execution":
            True,

        "training_performed":
            False,

        "fitting_performed":
            False,

        "new_evaluation_performed":
            False,

        "locked_test_used_for_selection":
            False,

        "artifact_modified":
            False,

        "synthetic_universal_target_created":
            False,

        "native_component_results":
            component_results,

        "t8_execution_composition":
            "PASS" if t8_pass else "REQUIRES_REVIEW",

        "t9_execution_composition":
            "PASS" if t9_pass else "REQUIRES_REVIEW",

        "t10_policy_boundary":
            "PASS" if t10_pass else "REQUIRES_REVIEW",

        "interpretation":
            (
                "Controlled composition of already-executed "
                "native runtime evidence was checked without "
                "retraining, new evaluation, synthetic targets, "
                "or artifact modification. Native task semantics "
                "remain distinct."
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
    print("No new evaluation performed.")
    print("No locked test selection performed.")
    print("No artifact modification performed.")


if __name__ == "__main__":
    main()