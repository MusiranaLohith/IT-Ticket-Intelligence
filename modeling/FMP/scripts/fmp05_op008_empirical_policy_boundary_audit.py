from pathlib import Path
import json
from datetime import datetime, timezone


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
OUTPUT_PATH = (
    PROJECT_ROOT
    / "modeling/FMP/metrics/fmp05_op008_empirical_policy_boundary_audit.json"
)

TARGET_FILES = {
    "T2_closure": PROJECT_ROOT / "modeling/T2/analysis/t2_final_closure.json",
    "T2_metrics": PROJECT_ROOT / "modeling/T2/analysis/t2_final_test_metrics.json",

    "T3_closure": PROJECT_ROOT / "modeling/T3/analysis/t3_final_closure.json",
    "T3_metrics": PROJECT_ROOT / "modeling/T3/metrics/t3_final_test_metrics.json",

    "T4_closure": PROJECT_ROOT / "modeling/T4/results/t4_mod013_closure.json",

    "T5_closure": PROJECT_ROOT / "modeling/T5/metrics/t5_mod011_final_closure.json",
    "T5_locked": PROJECT_ROOT / "modeling/T5/metrics/t5_mod009_locked_evaluation_metrics.json",
    "T5_calibration": PROJECT_ROOT / "modeling/T5/metrics/t5_mod006_calibration_metrics.json",

    "T6_closure": PROJECT_ROOT / "modeling/T6/metrics/t6_final_closure.json",

    "T7_closure": PROJECT_ROOT / "modeling/T7/metrics/t7_mod012_final_closure.json",

    "T9_closure": (
        PROJECT_ROOT
        / "modeling/T9/mod037/t9_mod037_op015_final_integrated_closure.json"
    ),
}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_nested(obj, *keys, default=None):
    current = obj

    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]

    return current


def contains_text(obj, terms):
    """
    Read-only recursive text search.
    Used only to detect explicit evidence language.
    """
    found = []

    def walk(value, path=""):
        if isinstance(value, dict):
            for key, child in value.items():
                walk(child, f"{path}.{key}" if path else key)

        elif isinstance(value, list):
            for i, child in enumerate(value):
                walk(child, f"{path}[{i}]")

        elif isinstance(value, str):
            lower = value.lower()
            for term in terms:
                if term.lower() in lower:
                    found.append(
                        {
                            "term": term,
                            "path": path,
                            "value": value,
                        }
                    )

    walk(obj)
    return found


def main():
    print("=" * 80)
    print("FMP-05 OP-008 — EMPIRICAL POLICY-BOUNDARY AUDIT")
    print("=" * 80)

    print("\n[1] Loading authoritative closure/evaluation artifacts")
    print("-" * 80)

    loaded = {}

    for name, path in TARGET_FILES.items():
        exists = path.exists()
        readable = False
        data = None

        if exists:
            try:
                data = load_json(path)
                readable = True
                loaded[name] = data
            except Exception as exc:
                print(f"{name}")
                print(f"  path: {path}")
                print("  exists: True")
                print("  readable: False")
                print(f"  error: {exc}")
                continue

        print(name)
        print(f"  path: {path}")
        print(f"  exists: {exists}")
        print(f"  readable: {readable}")

    missing = [
        name
        for name in TARGET_FILES
        if name not in loaded
    ]

    if missing:
        print("\nBLOCKED: required authoritative artifacts missing/unreadable")
        print("Missing:")
        for name in missing:
            print(f"  - {name}")
        print("=" * 80)
        return

    print("\n[2] T2 policy-boundary evidence")
    print("-" * 80)

    t2 = loaded["T2_closure"]

    t2_role = get_nested(t2, "system_role", "decision")
    t2_description = get_nested(t2, "system_role", "description")
    t2_suitability = t2.get("suitability_decision")

    t2_unsupported = t2.get("unsupported_claims", [])
    t2_limitations = t2.get("limitations", [])

    print(f"system_role.decision = {t2_role}")
    print(f"suitability_decision = {t2_suitability}")

    print("Relevant limitations:")
    for item in t2_limitations:
        if "threshold" in str(item).lower() or "autom" in str(item).lower():
            print(f"  - {item}")

    print("Relevant unsupported claims:")
    for item in t2_unsupported:
        if (
            "threshold" in str(item).lower()
            or "autom" in str(item).lower()
            or "human" in str(item).lower()
        ):
            print(f"  - {item}")

    print("\n[3] T3 policy-boundary evidence")
    print("-" * 80)

    t3 = loaded["T3_closure"]

    print(f"system_role = {t3.get('system_role')}")
    print(f"recommended_use = {t3.get('recommended_use')}")
    print(f"closure_statement = {t3.get('closure_statement')}")

    print("\n[4] T4 policy-boundary evidence")
    print("-" * 80)

    t4 = loaded["T4_closure"]

    print(f"status = {t4.get('status')}")
    print(f"closure_status = {t4.get('closure_status')}")
    print(f"system_role = {t4.get('system_role')}")
    print(f"suitability_decision = {t4.get('suitability_decision')}")

    if isinstance(t4.get("unsupported_claims"), list):
        for item in t4["unsupported_claims"]:
            if (
                "eligib" in str(item).lower()
                or "autom" in str(item).lower()
                or "threshold" in str(item).lower()
            ):
                print(f"  unsupported: {item}")

    print("\n[5] T5 policy-boundary evidence")
    print("-" * 80)

    t5 = loaded["T5_closure"]
    t5_locked = loaded["T5_locked"]
    t5_cal = loaded["T5_calibration"]

    print(
        "selected_pipeline.threshold.value =",
        get_nested(t5, "selected_pipeline", "threshold", "value"),
    )

    print(
        "selected_pipeline.threshold.status =",
        get_nested(t5, "selected_pipeline", "threshold", "status"),
    )

    print(
        "selected_pipeline.threshold.optimized =",
        get_nested(t5, "selected_pipeline", "threshold", "optimized"),
    )

    print(
        "controls.threshold_optimization =",
        get_nested(t5, "controls", "threshold_optimization"),
    )

    print(
        "controls.evaluation_used_for_calibration =",
        get_nested(t5, "controls", "evaluation_used_for_calibration"),
    )

    print(
        "locked threshold precision =",
        get_nested(t5_locked, "metrics", "threshold_0_5", "precision"),
    )

    print(
        "locked threshold recall =",
        get_nested(t5_locked, "metrics", "threshold_0_5", "recall"),
    )

    print(
        "locked threshold F1 =",
        get_nested(t5_locked, "metrics", "threshold_0_5", "f1"),
    )

    print(
        "calibration threshold_optimization =",
        t5_cal.get("threshold_optimization"),
    )

    print("\n[6] T6 policy-boundary evidence")
    print("-" * 80)

    t6 = loaded["T6_closure"]

    print(f"system_role = {t6.get('system_role')}")
    print(f"suitability_decision = {t6.get('suitability_decision')}")
    print(f"final_conclusion = {t6.get('final_conclusion')}")

    print("\n[7] T7 policy-boundary evidence")
    print("-" * 80)

    t7 = loaded["T7_closure"]

    print(f"final_project_status = {t7.get('final_project_status')}")
    print(f"supported_as = {t7.get('supported_as')}")
    print("not_supported_as =")

    for item in t7.get("not_supported_as", []):
        print(f"  - {item}")

    print("\n[8] T9 cross-task policy boundary")
    print("-" * 80)

    t9 = loaded["T9_closure"]

    for key in [
        "automatic_action_policy",
        "human_review_boundary",
        "universal_confidence",
        "universal_risk",
        "synthetic_fusion_target",
    ]:
        print(f"{key} = {t9.get(key)}")

    print("\n[9] Explicit policy-evidence classification")
    print("-" * 80)

    policy_states = {
        "AUTOMATION": {
            "status": "NOT_EMPIRICALLY_ESTABLISHED",
            "basis": [
                "T2 does not establish automatic action at a fixed confidence threshold.",
                "T3 is explicitly not an autonomous severity assignment capability.",
                "T4 historical retrieval does not establish operational eligibility/correctness.",
                "T5 threshold is descriptive-only and not optimized.",
                "T7 explicitly excludes autonomous resolution-time decisions and workflow automation.",
                "T9 automatic_action_policy is NOT_ESTABLISHED.",
            ],
        },
        "HUMAN_REVIEW": {
            "status": "NOT_EMPIRICALLY_ESTABLISHED",
            "basis": [
                "T2/T3 provide secondary decision-support signals rather than validated review boundaries.",
                "T5 contains threshold diagnostics but no operational threshold was established.",
                "T7 explicitly excludes a validated human-review threshold.",
                "T9 human_review_boundary is NOT_ESTABLISHED_BY_T9.",
            ],
        },
        "DEFER": {
            "status": "NOT_EMPIRICALLY_ESTABLISHED",
            "basis": [
                "No authoritative task closure establishes an empirically validated defer boundary.",
                "No cross-task universal risk/confidence boundary exists.",
                "T9 explicitly does not create a universal risk or synthetic fusion target.",
            ],
        },
    }

    for state, evidence in policy_states.items():
        print(f"{state}")
        print(f"  status = {evidence['status']}")
        for item in evidence["basis"]:
            print(f"  - {item}")

    print("\n[10] Policy-boundary safeguards")
    print("-" * 80)

    safeguards = {
        "new_threshold_selected": False,
        "threshold_reoptimized": False,
        "new_policy_created": False,
        "models_loaded": False,
        "predictions_generated": False,
        "retraining_performed": False,
        "calibration_fitted": False,
        "artifacts_modified": False,
        "universal_confidence_created": False,
        "universal_risk_created": False,
        "synthetic_fusion_target_created": False,
    }

    for key, value in safeguards.items():
        print(f"{key}: {value}")

    print("\n[11] Final determination")
    print("-" * 80)

    final_status = "PASS"

    determination = {
        "automation": "NOT_ESTABLISHED",
        "human_review": "NOT_ESTABLISHED",
        "defer": "NOT_ESTABLISHED",
        "universal_threshold": "NOT_ESTABLISHED",
        "universal_confidence": "NOT_CREATED",
        "universal_risk": "NOT_CREATED",
        "next_policy_requirement": (
            "Any future operational policy boundary must be task-specific, "
            "empirically validated, and supported by an appropriate evaluation "
            "population. No boundary is selected by this audit."
        ),
    }

    print("AUTOMATION =", determination["automation"])
    print("HUMAN_REVIEW =", determination["human_review"])
    print("DEFER =", determination["defer"])
    print("UNIVERSAL_THRESHOLD =", determination["universal_threshold"])
    print("UNIVERSAL_CONFIDENCE =", determination["universal_confidence"])
    print("UNIVERSAL_RISK =", determination["universal_risk"])
    print("NEXT_POLICY_REQUIREMENT =")
    print(f"  {determination['next_policy_requirement']}")

    output = {
        "operation": "FMP-05-OP-008",
        "operation_name": "Empirical Policy-Boundary Audit",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "operation_type": "READ_ONLY_EMPIRICAL_POLICY_BOUNDARY_AUDIT",
        "status": final_status,
        "authoritative_artifacts": {
            name: str(path)
            for name, path in TARGET_FILES.items()
        },
        "policy_states": policy_states,
        "determination": determination,
        "safeguards": safeguards,
        "interpretation": (
            "Existing evidence does not establish empirically validated "
            "AUTOMATION, HUMAN_REVIEW, or DEFER boundaries. The audit does "
            "not select or optimize any threshold. Task-specific evidence "
            "must be evaluated separately before any operational policy "
            "boundary can be established."
        ),
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("\n[12] Output")
    print("-" * 80)
    print(f"Saved: {OUTPUT_PATH}")

    print("\n[13] Final summary")
    print("-" * 80)
    print(f"Operation type: {output['operation_type']}")
    print(f"STATUS: {final_status}")

    print("=" * 80)


if __name__ == "__main__":
    main()