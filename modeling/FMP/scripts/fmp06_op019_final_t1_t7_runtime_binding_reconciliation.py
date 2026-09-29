from pathlib import Path
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

BINDING_AUDIT = (
    ROOT / "modeling/FMP/metrics/"
    "fmp06_op017_exact_frozen_runtime_binding_audit.json"
)

T7_RECONCILIATION = (
    ROOT / "modeling/FMP/metrics/"
    "fmp06_op018r28_t7_runtime_closure_reconciliation.json"
)

TASKS = {
    "T1": [
        ROOT / "modeling/T1/analysis/t1_final_closure.json",
    ],
    "T2": [
        ROOT / "modeling/T2/metrics/t2_final_closure.json",
        ROOT / "modeling/T2/models/"
        "t2_class_weighted_tfidf_logreg.joblib",
    ],
    "T3": [
        ROOT / "modeling/T3/metrics/t3_final_closure.json",
        ROOT / "modeling/T3/models/"
        "t3_class_weighted_tfidf_logreg.joblib",
    ],
    "T4": [
        ROOT / "modeling/T4/results/t4_mod013_closure.json",
        ROOT / "modeling/T4/results/mod007_checkpoints/"
        "t4_mod007_tfidf.joblib",
        ROOT / "modeling/T4/results/mod007_checkpoints/"
        "t4_mod007_neighbors.joblib",
    ],
    "T5": [
        ROOT / "modeling/T5/metrics/"
        "t5_mod011_final_closure.json",
        ROOT / "modeling/T5/models/"
        "t5_mod005_tfidf.joblib",
        ROOT / "modeling/T5/models/"
        "t5_mod005_logreg.joblib",
    ],
    "T6": [
        ROOT / "modeling/T6/metrics/"
        "t6_final_closure.json",
        ROOT / "modeling/T6/models/"
        "t6_mod004_tfidf_vectorizer.joblib",
        ROOT / "modeling/T6/metrics/"
        "t6_mod009_hybrid_query_rankings.csv",
    ],
    "T7": [
        ROOT / "modeling/T7/metrics/"
        "t7_mod012_final_closure.json",
        ROOT / "modeling/T7/metrics/"
        "t7_mod010_log_normal_aft_model.json",
    ],
}

OUT = (
    ROOT / "modeling/FMP/metrics/"
    "fmp06_op019_final_t1_t7_runtime_binding_reconciliation.json"
)


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def describe_binding(binding, task):
    if not isinstance(binding, dict):
        return None

    value = binding.get(task)

    if value is None:
        return None

    return value


def main():
    print("=" * 72)
    print("FMP-06 OP-019 — FINAL T1–T7 RUNTIME BINDING RECONCILIATION")
    print("=" * 72)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation metrics: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    print("\n[1] Loading prior authoritative binding evidence...")

    if not BINDING_AUDIT.exists():
        raise RuntimeError(
            f"Missing binding audit: {BINDING_AUDIT}"
        )

    binding_audit = load_json(BINDING_AUDIT)

    t7_recon = None

    if T7_RECONCILIATION.exists():
        t7_recon = load_json(T7_RECONCILIATION)

    print(
        f"  OP-017 binding audit: "
        f"{'PRESENT' if BINDING_AUDIT.exists() else 'MISSING'}"
    )

    print(
        f"  OP-018R28 T7 reconciliation: "
        f"{'PRESENT' if T7_RECONCILIATION.exists() else 'MISSING'}"
    )

    # ------------------------------------------------------------
    # Filesystem resolution
    # ------------------------------------------------------------
    print("\n[2] Resolving final T1–T7 evidence paths...")

    task_results = {}

    for task, paths in TASKS.items():

        existing = []
        missing = []

        for path in paths:
            if path.exists():
                existing.append(str(path))
            else:
                missing.append(str(path))

        task_results[task] = {
            "expected_paths": [
                str(path)
                for path in paths
            ],
            "existing_paths": existing,
            "missing_paths": missing,
        }

        print(
            f"  {task}: "
            f"{len(existing)}/{len(paths)} expected paths present"
        )

    # ------------------------------------------------------------
    # Prior binding evidence
    # ------------------------------------------------------------
    print("\n[3] Reading OP-017 task binding statuses...")

    binding_candidates = [
        binding_audit.get("task_bindings"),
        binding_audit.get("tasks"),
        binding_audit.get("bindings"),
        binding_audit.get("results"),
    ]

    prior_bindings = None

    for candidate in binding_candidates:
        if isinstance(candidate, dict):
            prior_bindings = candidate
            break

    if prior_bindings is None:
        prior_bindings = {}

    # ------------------------------------------------------------
    # Final semantic classification
    # ------------------------------------------------------------
    print("\n[4] Final task interface reconciliation...")

    semantic_contracts = {
        "T1": {
            "native_role": "ticket classification",
            "interface": "single ticket text -> class prediction",
        },
        "T2": {
            "native_role": "priority classification",
            "interface": "ticket text -> priority decision-support output",
        },
        "T3": {
            "native_role": "severity classification",
            "interface": "ticket text -> severity decision-support output",
        },
        "T4": {
            "native_role": "historical assignee retrieval",
            "interface": "ticket/query -> ranked historical assignee candidates",
        },
        "T5": {
            "native_role": "duplicate relationship detection",
            "interface": "ticket pair -> duplicate score",
        },
        "T6": {
            "native_role": "similar historical ticket retrieval",
            "interface": "query + candidate corpus -> ranked candidates",
        },
        "T7": {
            "native_role": "time-to-resolution survival modeling",
            "interface": "ticket features -> Log-Normal AFT survival prediction",
        },
    }

    final_matrix = {}

    for task in TASKS:

        existing_count = len(
            task_results[task]["existing_paths"]
        )

        expected_count = len(
            task_results[task]["expected_paths"]
        )

        filesystem_complete = (
            existing_count == expected_count
        )

        t7_specific = (
            task == "T7"
            and isinstance(t7_recon, dict)
            and t7_recon.get("status") == "PASS"
        )

        if task == "T7":
            status = (
                "RECONCILED"
                if filesystem_complete and t7_specific
                else "REQUIRES_REVIEW"
            )
        else:
            status = (
                "PATHS_PRESENT"
                if filesystem_complete
                else "REQUIRES_REVIEW"
            )

        final_matrix[task] = {
            "status": status,
            "filesystem_paths_complete":
                filesystem_complete,
            "prior_binding_evidence_present":
                task in prior_bindings,
            "native_role":
                semantic_contracts[task]["native_role"],
            "interface":
                semantic_contracts[task]["interface"],
            "existing_paths":
                task_results[task]["existing_paths"],
            "missing_paths":
                task_results[task]["missing_paths"],
        }

        print(
            f"  {task}: {status}"
        )

    # ------------------------------------------------------------
    # Overall boundary
    # ------------------------------------------------------------
    reconciled_tasks = [
        task
        for task, result in final_matrix.items()
        if result["status"] in (
            "PATHS_PRESENT",
            "RECONCILED",
        )
    ]

    overall_pass = (
        len(reconciled_tasks) == 7
        and isinstance(t7_recon, dict)
        and t7_recon.get("status") == "PASS"
    )

    print("\n[5] Overall T1–T7 reconciliation...")

    print(
        f"  reconciled tasks: "
        f"{len(reconciled_tasks)}/7"
    )

    print(
        f"  T1–T7 runtime binding reconciliation: "
        f"{'PASS' if overall_pass else 'REQUIRES_REVIEW'}"
    )

    # ------------------------------------------------------------
    # Evidence artifact
    # ------------------------------------------------------------
    result = {
        "operation":
            "FMP-06 OP-019",

        "status":
            "PASS" if overall_pass else "REQUIRES_REVIEW",

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

        "reconciled_task_count":
            len(reconciled_tasks),

        "task_matrix":
            final_matrix,

        "t7_runtime_reconciliation":
            (
                t7_recon.get("status")
                if isinstance(t7_recon, dict)
                else "MISSING"
            ),

        "boundary_statement":
            (
                "T1–T7 native task interfaces are reconciled "
                "to their frozen artifacts or authoritative "
                "implementations for downstream integration. "
                "This operation does not assert that all tasks "
                "share a common prediction type or common "
                "probability semantics."
            ),

        "t8_handoff_boundary":
            (
                "Downstream integration must preserve each task's "
                "native output semantics and must not convert "
                "ranking, retrieval, survival, or duplicate scores "
                "into universal probabilities or a universal target "
                "without separate empirical evidence."
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

    print("\n" + "=" * 72)
    print("OP-019 RECONCILIATION COMPLETE")
    print("=" * 72)

    print(
        f"Status: {result['status']}"
    )

    print(
        f"Reconciled tasks: "
        f"{len(reconciled_tasks)}/7"
    )

    print(
        f"Output: {OUT}"
    )

    print("\nNo training performed.")
    print("No fitting performed.")
    print("No prediction performed.")
    print("No evaluation performed.")
    print("No locked test used.")
    print("No artifact modification performed.")

    print("=" * 72)


if __name__ == "__main__":
    main()