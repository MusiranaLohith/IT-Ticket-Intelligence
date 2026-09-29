from pathlib import Path
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
METRICS = ROOT / "modeling/FMP/metrics"

T5_EVIDENCE = (
    METRICS /
    "fmp06_op018r3_corrected_frozen_runtime_inference_probe.json"
)

T10_EVIDENCE = (
    METRICS /
    "fmp05_op008_empirical_policy_boundary_audit.json"
)

OUT = (
    METRICS /
    "fmp06_op022r2_t5_t10_authoritative_boundary_reconciliation.json"
)


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_values(obj, wanted_keys, path=""):
    found = {}

    if isinstance(obj, dict):
        for key, value in obj.items():
            current = f"{path}.{key}" if path else key

            if key in wanted_keys:
                found[current] = value

            found.update(
                find_values(
                    value,
                    wanted_keys,
                    current
                )
            )

    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            current = f"{path}[{i}]"
            found.update(
                find_values(
                    value,
                    wanted_keys,
                    current
                )
            )

    return found


def main():
    print("=" * 72)
    print(
        "FMP-06 OP-022R2 — T5/T10 AUTHORITATIVE "
        "BOUNDARY RECONCILIATION"
    )
    print("=" * 72)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    print("\n[1] Loading T5 runtime evidence...")

    if not T5_EVIDENCE.exists():
        raise RuntimeError(
            f"T5 evidence missing: {T5_EVIDENCE}"
        )

    t5 = load_json(T5_EVIDENCE)

    print("  T5 evidence: PRESENT")

    print("\n[2] Extracting T5 task-specific runtime statuses...")

    t5_status_values = find_values(
        t5,
        {
            "status",
            "runtime_status",
            "task_status",
            "T5",
            "t5",
        }
    )

    print(
        f"  Structured status fields found: "
        f"{len(t5_status_values)}"
    )

    t5_text = json.dumps(
        t5,
        sort_keys=True
    ).lower()

    # OP-018R3 is known to contain a task-specific T5 PASS
    # result even though its aggregate operation status was FAIL
    # because the earlier T1 wrapper failed.
    t5_pass_evidence = (
        (
            "t5" in path.lower()
            and str(value).upper() == "PASS"
        )
        for path, value in t5_status_values.items()
    )

    t5_pass_evidence = any(t5_pass_evidence)

    print(
        f"  T5 task-specific PASS evidence: "
        f"{t5_pass_evidence}"
    )

    # Preserve the already-established T5 artifact binding as
    # additional evidence.
    t5_artifacts = [
        ROOT / "modeling/T5/models/t5_mod005_tfidf.joblib",
        ROOT / "modeling/T5/models/t5_mod005_logreg.joblib",
        ROOT / "modeling/T5/models/t5_mod007_calibrated_tfidf.joblib",
        ROOT / "modeling/T5/models/t5_mod007_calibration_models.joblib",
    ]

    t5_artifacts_present = all(
        path.exists() and path.stat().st_size > 0
        for path in t5_artifacts
    )

    print(
        f"  T5 frozen artifact set present: "
        f"{t5_artifacts_present}"
    )

    t5_pass = (
        t5_pass_evidence
        and t5_artifacts_present
    )

    print(
        f"  T5 authoritative boundary: "
        f"{'PASS' if t5_pass else 'REQUIRES_REVIEW'}"
    )

    print("\n[3] Loading T10 policy-boundary evidence...")

    if not T10_EVIDENCE.exists():
        raise RuntimeError(
            f"T10 evidence missing: {T10_EVIDENCE}"
        )

    t10 = load_json(T10_EVIDENCE)

    print("  T10 evidence: PRESENT")

    print("\n[4] Extracting structured T10 boundary fields...")

    t10_values = find_values(
        t10,
        {
            "empirical_automation_threshold_is_currently_established",
            "empirical_automation_correctness_is_currently_measurable",
            "human_review_outcome_ground_truth_is_currently_established",
            "automation_threshold_created",
            "synthetic_automation_target_created",
            "universal_confidence_threshold",
            "universal_risk_score",
            "no_universal_confidence_threshold",
            "no_universal_risk_score",
        }
    )

    for path, value in t10_values.items():
        print(f"  {path} = {value}")

    threshold_not_established = any(
        str(value).upper() == "NOT ESTABLISHED"
        for path, value in t10_values.items()
        if "threshold" in path.lower()
    )

    threshold_not_created = any(
        str(value).upper() in {
            "NO",
            "FALSE",
            "NOT CREATED",
        }
        for path, value in t10_values.items()
        if "threshold" in path.lower()
        or "automation_threshold" in path.lower()
    )

    synthetic_target_not_created = any(
        str(value).upper() in {
            "NO",
            "FALSE",
            "NOT CREATED",
        }
        for path, value in t10_values.items()
        if "synthetic_automation_target" in path.lower()
    )

    t10_pass = (
        threshold_not_established
        and threshold_not_created
        and synthetic_target_not_created
    )

    print(
        f"  Automation threshold not empirically established: "
        f"{threshold_not_established}"
    )

    print(
        f"  Automation threshold not created: "
        f"{threshold_not_created}"
    )

    print(
        f"  Synthetic automation target not created: "
        f"{synthetic_target_not_created}"
    )

    print(
        f"  T10 authoritative policy boundary: "
        f"{'PASS' if t10_pass else 'REQUIRES_REVIEW'}"
    )

    final_status = (
        "PASS"
        if t5_pass and t10_pass
        else "REQUIRES_REVIEW"
    )

    print("\n[5] Final reconciliation...")

    print(f"  T5: {'PASS' if t5_pass else 'REQUIRES_REVIEW'}")
    print(f"  T10: {'PASS' if t10_pass else 'REQUIRES_REVIEW'}")

    print("=" * 72)
    print(f"FINAL STATUS: {final_status}")
    print("=" * 72)

    result = {
        "operation":
            "FMP-06 OP-022R2",

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

        "T5": {
            "task_specific_pass_evidence":
                t5_pass_evidence,
            "frozen_artifacts_present":
                t5_artifacts_present,
            "status":
                "PASS" if t5_pass else "REQUIRES_REVIEW",
        },

        "T10": {
            "structured_fields":
                t10_values,
            "threshold_not_empirically_established":
                threshold_not_established,
            "threshold_not_created":
                threshold_not_created,
            "synthetic_target_not_created":
                synthetic_target_not_created,
            "status":
                "PASS" if t10_pass else "REQUIRES_REVIEW",
        },

        "interpretation":
            (
                "T5 is reconciled using task-specific runtime "
                "evidence rather than the aggregate OP-018R3 "
                "status. T10 is reconciled using its structured "
                "policy-boundary fields rather than generic "
                "textual threshold detection."
            ),
    }

    OUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUT.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"\nOutput: {OUT}")
    print("No training performed.")
    print("No fitting performed.")
    print("No prediction performed.")
    print("No evaluation performed.")
    print("No locked test used.")
    print("No artifact modification performed.")


if __name__ == "__main__":
    main()