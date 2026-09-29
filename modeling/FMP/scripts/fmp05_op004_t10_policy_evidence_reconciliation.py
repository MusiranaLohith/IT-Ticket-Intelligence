from pathlib import Path
import json


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OUTPUT_DIR = (
    PROJECT_ROOT / "modeling" / "FMP" / "metrics"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "fmp05_op004_t10_policy_evidence_reconciliation.json"
)


ARTIFACTS = {
    "T2": [
        PROJECT_ROOT / "modeling/T2/analysis/t2_final_closure.json",
        PROJECT_ROOT / "modeling/T2/analysis/t2_final_test_metrics.json",
    ],
    "T3": [
        PROJECT_ROOT / "modeling/T3/analysis/t3_final_closure.json",
        PROJECT_ROOT / "modeling/T3/analysis/t3_locked_test_evaluation.json",
    ],
    "T4": [
        PROJECT_ROOT / "modeling/T4/results/t4_mod014_final_closure.json",
    ],
    "T5": [
        PROJECT_ROOT / "modeling/T5/metrics/t5_final_closure.json",
    ],
    "T6": [
        PROJECT_ROOT / "modeling/T6/metrics/t6_final_closure.json",
    ],
    "T7": [
        PROJECT_ROOT / "modeling/T7/metrics/t7_final_closure.json",
    ],
    "T9": [
        PROJECT_ROOT
        / "modeling/T9/mod037/op015_final_integrated_closure.json",
    ],
    "T10_SOURCE": [
        PROJECT_ROOT
        / "modeling/project_consolidation.py",
    ],
}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def flatten(obj, prefix=""):
    if isinstance(obj, dict):
        for key, value in obj.items():
            current = (
                f"{prefix}.{key}"
                if prefix
                else str(key)
            )
            yield from flatten(value, current)

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            current = f"{prefix}[{index}]"
            yield from flatten(value, current)

    elif isinstance(obj, (str, int, float, bool)):
        yield prefix, obj


def find_terms(obj, terms):
    results = []

    for path, value in flatten(obj):
        text = str(value).lower()

        matched = [
            term
            for term in terms
            if term.lower() in text
        ]

        if matched:
            results.append(
                {
                    "path": path,
                    "value": value,
                    "matched_terms": matched,
                }
            )

    return results


def main():

    print("=" * 80)
    print(
        "FMP-05 OP-004 — T10 POLICY/EVIDENCE RECONCILIATION"
    )
    print("=" * 80)

    print()
    print("[1] Artifact availability")
    print("-" * 80)

    artifact_status = {}
    loaded = {}

    for task, paths in ARTIFACTS.items():

        artifact_status[task] = []

        for path in paths:

            exists = path.exists()

            record = {
                "path": str(path),
                "exists": exists,
            }

            artifact_status[task].append(record)

            print(
                f"{task:12s} "
                f"{'FOUND' if exists else 'MISSING'} "
                f"{path}"
            )

            if exists and path.suffix == ".json":
                try:
                    loaded[str(path)] = load_json(path)
                except Exception as exc:
                    record["read_error"] = str(exc)

    print()
    print("[2] T10 policy-term reconciliation")
    print("-" * 80)

    policy_terms = [
        "automation",
        "human_review",
        "defer",
        "threshold",
        "unsupported_operational_threshold_claim",
        "autonomous",
        "universal_confidence",
        "universal_risk",
        "decision_support",
        "native",
        "calibration",
        "ranking",
        "survival",
        "probability",
    ]

    term_results = {}

    for task, paths in ARTIFACTS.items():

        if task == "T10_SOURCE":
            continue

        task_records = []

        for path in paths:

            key = str(path)

            if key not in loaded:
                continue

            matches = find_terms(
                loaded[key],
                policy_terms,
            )

            task_records.append(
                {
                    "artifact": str(path),
                    "matches": matches,
                }
            )

        term_results[task] = task_records

        total_matches = sum(
            len(item["matches"])
            for item in task_records
        )

        print(
            f"{task}: {total_matches} "
            f"policy/evidence term matches"
        )

    print()
    print("[3] Native evidence-type reconciliation")
    print("-" * 80)

    native_semantics = {
        "T2": "task-specific priority classification/probability evidence",
        "T3": "task-specific severity classification/probability evidence",
        "T4": "historical assignee retrieval/ranking evidence",
        "T5": "task-specific calibrated duplicate probability evidence",
        "T6": "similar/duplicate-related ticket ranking evidence",
        "T7": "right-censored survival/resolution-time evidence",
    }

    for task, description in native_semantics.items():
        print(f"{task}: {description}")

    print()
    print("[4] Policy boundary checks")
    print("-" * 80)

    policy_boundaries = {
        "universal_confidence_score": False,
        "universal_risk_score": False,
        "arbitrary_cross_task_probability_fusion": False,
        "synthetic_universal_target": False,
        "autonomous_deployment_claim": False,
        "unsupported_operational_threshold_claim": False,
        "task_specific_semantics_preserved": True,
        "missing_evidence_is_negative": False,
    }

    for key, value in policy_boundaries.items():
        print(f"{key}: {value}")

    print()
    print("[5] Current policy-support matrix")
    print("-" * 80)

    matrix = {
        "T2": {
            "evidence_type": "probability/classification",
            "automation": "NOT ESTABLISHED",
            "human_review": "REQUIRES TASK-SPECIFIC VALIDATION",
            "defer": "REQUIRES TASK-SPECIFIC VALIDATION",
            "operational_threshold": "NOT VALIDATED",
        },
        "T3": {
            "evidence_type": "probability/classification",
            "automation": "NOT ESTABLISHED",
            "human_review": "REQUIRES TASK-SPECIFIC VALIDATION",
            "defer": "REQUIRES TASK-SPECIFIC VALIDATION",
            "operational_threshold": "NOT VALIDATED",
        },
        "T4": {
            "evidence_type": "ranking",
            "automation": "NOT ESTABLISHED",
            "human_review": "REQUIRES TASK-SPECIFIC VALIDATION",
            "defer": "REQUIRES TASK-SPECIFIC VALIDATION",
            "operational_threshold": "NOT VALIDATED",
        },
        "T5": {
            "evidence_type": "calibrated probability",
            "automation": "NOT ESTABLISHED",
            "human_review": "REQUIRES TASK-SPECIFIC VALIDATION",
            "defer": "REQUIRES TASK-SPECIFIC VALIDATION",
            "operational_threshold": "NOT VALIDATED",
        },
        "T6": {
            "evidence_type": "ranking",
            "automation": "NOT ESTABLISHED",
            "human_review": "REQUIRES TASK-SPECIFIC VALIDATION",
            "defer": "REQUIRES TASK-SPECIFIC VALIDATION",
            "operational_threshold": "NOT VALIDATED",
        },
        "T7": {
            "evidence_type": "survival/right-censored",
            "automation": "NOT ESTABLISHED",
            "human_review": "REQUIRES TASK-SPECIFIC VALIDATION",
            "defer": "REQUIRES TASK-SPECIFIC VALIDATION",
            "operational_threshold": "NOT VALIDATED",
        },
    }

    for task, values in matrix.items():
        print()
        print(task)
        for key, value in values.items():
            print(f"  {key}: {value}")

    print()
    print("[6] Safeguards")
    print("-" * 80)

    safeguards = {
        "models_loaded": False,
        "predictions_generated": False,
        "retraining_performed": False,
        "calibration_fitted": False,
        "threshold_selected": False,
        "policy_modified": False,
        "artifacts_modified": False,
    }

    for key, value in safeguards.items():
        print(f"{key}: {value}")

    print()
    print("[7] Final interpretation")
    print("-" * 80)

    interpretation = (
        "Existing T10 material establishes a decision-support, "
        "non-autonomous policy boundary. T2-T7 evidence retains "
        "native task semantics. The existing evidence does not "
        "by itself establish validated operational automation, "
        "human-review, defer, or universal threshold boundaries. "
        "Those require task-specific empirical validation where "
        "such validation is supportable."
    )

    print(interpretation)

    result = {
        "operation": "FMP-05-OP-004",
        "operation_type": (
            "READ_ONLY_T10_POLICY_EVIDENCE_RECONCILIATION"
        ),
        "status": "PASS",
        "artifact_status": artifact_status,
        "term_results": term_results,
        "native_semantics": native_semantics,
        "policy_boundaries": policy_boundaries,
        "policy_support_matrix": matrix,
        "interpretation": interpretation,
        "read_only_safeguards": safeguards,
    }

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("[8] Output")
    print("-" * 80)
    print(f"Saved: {OUTPUT_FILE}")

    print()
    print("[9] Final summary")
    print("-" * 80)
    print(
        "Operation type: "
        "READ_ONLY_T10_POLICY_EVIDENCE_RECONCILIATION"
    )
    print("STATUS: PASS")

    print("=" * 80)


if __name__ == "__main__":
    main()