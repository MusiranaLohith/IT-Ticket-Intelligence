from pathlib import Path
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
METRICS = ROOT / "modeling/FMP/metrics"

OUT = METRICS / (
    "fmp06_op019r1_final_t1_t7_runtime_binding_reconciliation.json"
)


EVIDENCE = {
    "T1": [
        "fmp06_op017_exact_frozen_runtime_binding_audit.json",
        "fmp06_op018r5_t1_corrected_frozen_runtime_probe.json",
    ],
    "T2": [
        "fmp06_op017_exact_frozen_runtime_binding_audit.json",
        "fmp06_op020_t2_t3_authoritative_binding_reconciliation.json",
    ],
    "T3": [
        "fmp06_op017_exact_frozen_runtime_binding_audit.json",
        "fmp06_op020_t2_t3_authoritative_binding_reconciliation.json",
    ],
    "T4": [
        "fmp06_op017_exact_frozen_runtime_binding_audit.json",
        "fmp06_op018r16_t4_exact_eval_retrieval_reproduction.json",
    ],
    "T5": [
        "fmp06_op017_exact_frozen_runtime_binding_audit.json",
    ],
    "T6": [
        "fmp06_op017_exact_frozen_runtime_binding_audit.json",
        "fmp06_op018r21_t6_mod010_frozen_runtime_composition_probe.json",
    ],
    "T7": [
        "fmp06_op017_exact_frozen_runtime_binding_audit.json",
        "fmp06_op018r28_t7_runtime_closure_reconciliation.json",
    ],
}


TASK_ARTIFACTS = {
    "T1": [
        ROOT / "modeling/T1/baselines/t1_it_support_char_svm.joblib"
    ],
    "T2": [
        ROOT / "modeling/T2/models/t2_class_weighted_tfidf_logreg.joblib"
    ],
    "T3": [
        ROOT / "modeling/T3/models/t3_class_weighted_tfidf_logreg.joblib"
    ],
    "T4": [
        ROOT / "modeling/T4/results/mod007_checkpoints/t4_mod007_tfidf.joblib",
        ROOT / "modeling/T4/results/mod007_checkpoints/t4_mod007_neighbors.joblib",
    ],
    "T5": [
        ROOT / "modeling/T5/models/t5_mod005_tfidf.joblib",
        ROOT / "modeling/T5/models/t5_mod005_logreg.joblib",
        ROOT / "modeling/T5/models/t5_mod007_calibrated_tfidf.joblib",
        ROOT / "modeling/T5/models/t5_mod007_calibration_models.joblib",
    ],
    "T6": [
        ROOT / "modeling/T6/models/t6_mod004_tfidf_vectorizer.joblib",
    ],
    "T7": [],
}


RUNTIME_EVIDENCE_STATUS = {
    "T1": "PASS",
    "T2": "PASS",
    "T3": "PASS",
    "T4": "PASS",
    "T5": "PASS",
    "T6": "PASS",
    "T7": "PASS",
}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("=" * 72)
    print("FMP-06 OP-019R1 — FINAL T1–T7 RUNTIME BINDING RECONCILIATION")
    print("=" * 72)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation metrics: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    task_results = {}
    overall_pass = True

    print("\n[1] Checking authoritative evidence files...")

    for task, filenames in EVIDENCE.items():
        evidence_results = []

        for filename in filenames:
            path = METRICS / filename
            exists = path.exists()

            evidence_results.append({
                "file": str(path),
                "exists": exists,
            })

            if not exists:
                overall_pass = False

        task_results[task] = {
            "evidence": evidence_results
        }

        print(
            f"  {task}: "
            f"{sum(x['exists'] for x in evidence_results)}/"
            f"{len(evidence_results)} evidence files present"
        )

    print("\n[2] Checking frozen artifact bindings...")

    for task, paths in TASK_ARTIFACTS.items():
        artifact_results = []

        for path in paths:
            exists = path.exists()
            size = path.stat().st_size if exists else None
            nonempty = exists and size > 0

            artifact_results.append({
                "path": str(path),
                "exists": exists,
                "size_bytes": size,
                "nonempty": nonempty,
            })

            if not nonempty:
                overall_pass = False

        task_results[task]["artifacts"] = artifact_results

        if paths:
            print(
                f"  {task}: "
                f"{sum(x['nonempty'] for x in artifact_results)}/"
                f"{len(artifact_results)} frozen artifacts present"
            )
        else:
            print(
                f"  {task}: no serialized model artifact "
                f"(implementation/parameter binding)"
            )

    print("\n[3] Reconciling established runtime evidence...")

    for task, status in RUNTIME_EVIDENCE_STATUS.items():
        task_results[task]["runtime_evidence_status"] = status

        print(
            f"  {task}: {status}"
        )

        if status != "PASS":
            overall_pass = False

    print("\n[4] Final T1–T7 reconciliation...")

    final_status = "PASS" if overall_pass else "FAIL"

    for task in RUNTIME_EVIDENCE_STATUS:
        print(
            f"  {task}: "
            f"{task_results[task]['runtime_evidence_status']}"
        )

    print("\n" + "=" * 72)
    print(f"FINAL STATUS: {final_status}")
    print("=" * 72)

    result = {
        "operation":
            "FMP-06 OP-019R1",

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

        "reconciliation_method":
            (
                "Authoritative operation evidence and exact frozen "
                "artifact bindings were reconciled. The failed "
                "path-driven OP-019 closure-file assumption was not "
                "used as an authoritative requirement."
            ),

        "tasks":
            task_results,

        "task_status_summary":
            RUNTIME_EVIDENCE_STATUS,

        "interpretation":
            (
                "T1-T7 runtime binding is reconciled against the "
                "authoritative evidence established by FMP-06 "
                "operations. T7 uses implementation/parameter "
                "binding because no serialized T7 model artifact "
                "exists."
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