from pathlib import Path
import hashlib
import json
import shutil


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

RUNTIME_DIR = (
    PROJECT_ROOT / "modeling" / "FMP" / "runtime"
)

METRICS_DIR = (
    PROJECT_ROOT / "modeling" / "FMP" / "metrics"
)

DEPLOYMENT_DIR = (
    PROJECT_ROOT / "modeling" / "FMP" / "deployment"
)

DEPLOYMENT_RUNTIME_DIR = (
    DEPLOYMENT_DIR / "runtime"
)

OUTPUT = (
    METRICS_DIR
    / "h_run026_op001_deployment_package_manifest.json"
)


def sha256(path):
    digest = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def readable(path):
    return (
        path.exists()
        and path.is_file()
        and path.stat().st_size > 0
    )


def inspect_file(relative_path):
    path = PROJECT_ROOT / relative_path

    return {
        "declared_path": relative_path,
        "resolved_path": str(path),
        "exists": path.exists(),
        "readable": readable(path),
        "size_bytes": (
            path.stat().st_size
            if path.exists()
            else None
        ),
        "sha256": (
            sha256(path)
            if readable(path)
            else None
        ),
    }


def main():

    print("=" * 70)
    print(
        "H-RUN-026-OP-001 — "
        "DEPLOYMENT PACKAGE ASSEMBLY"
    )
    print("=" * 70)

    DEPLOYMENT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    DEPLOYMENT_RUNTIME_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    METRICS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ============================================================
    # 1. Runtime contract
    # ============================================================

    print("\n[1] Runtime contract")

    pipeline_path = (
        RUNTIME_DIR / "ticket_pipeline.py"
    )

    runtime = {
        "exists": pipeline_path.exists(),
        "readable": readable(pipeline_path),
        "class_present": False,
        "predict_present": False,
        "predict_batch_present": False,
        "importable": False,
        "error": None,
    }

    if runtime["readable"]:

        source = pipeline_path.read_text(
            encoding="utf-8"
        )

        runtime["class_present"] = (
            "class TicketPipeline" in source
        )

        runtime["predict_present"] = (
            "def predict(" in source
        )

        runtime["predict_batch_present"] = (
            "def predict_batch(" in source
        )

        try:

            import sys

            if str(RUNTIME_DIR) not in sys.path:
                sys.path.insert(
                    0,
                    str(RUNTIME_DIR),
                )

            from ticket_pipeline import (
                TicketPipeline
            )

            runtime["importable"] = callable(
                TicketPipeline
            )

        except Exception as exc:

            runtime["error"] = (
                f"{type(exc).__name__}: {exc}"
            )

    print(
        "    ticket_pipeline.py : "
        f"{runtime['readable']}"
    )

    print(
        "    TicketPipeline     : "
        f"{runtime['class_present']}"
    )

    print(
        "    predict()          : "
        f"{runtime['predict_present']}"
    )

    print(
        "    predict_batch()    : "
        f"{runtime['predict_batch_present']}"
    )

    print(
        "    importable         : "
        f"{runtime['importable']}"
    )

    # ============================================================
    # 2. Frozen T1–T7 artifacts
    # ============================================================

    print("\n[2] Frozen T1–T7 artifacts")

    frozen_artifacts = {

        "T1": [
            "modeling/T1/baselines/"
            "t1_it_support_char_svm.joblib"
        ],

        "T2": [
            "modeling/T2/models/"
            "t2_class_weighted_tfidf_logreg.joblib"
        ],

        "T3": [
            "modeling/T3/models/"
            "t3_class_weighted_tfidf_logreg.joblib"
        ],

        "T4": [
            "modeling/T4/results/mod007_checkpoints/"
            "t4_mod007_tfidf.joblib",

            "modeling/T4/results/mod007_checkpoints/"
            "t4_mod007_neighbors.joblib",

            "modeling/T4/results/mod007_checkpoints/"
            "t4_mod007_full_retrieval.npz",
        ],

        # CORRECT AUTHORITATIVE T5 LOCATION
        "T5": [
            "modeling/T5/models/"
            "t5_mod005_tfidf.joblib",

            "modeling/T5/models/"
            "t5_mod005_logreg.joblib",

            "modeling/T5/models/"
            "t5_mod007_calibrated_tfidf.joblib",

            "modeling/T5/models/"
            "t5_mod007_calibration_models.joblib",
        ],

        "T6": [
            "modeling/T6/metrics/"
            "t6_mod010_corrected_hybrid_results.json"
        ],

        "T7": [
            "modeling/T7/metrics/"
            "t7_mod010_log_normal_aft_model.json"
        ],
    }

    artifact_records = {}

    total_artifacts = 0
    valid_artifacts = 0

    for task, paths in frozen_artifacts.items():

        artifact_records[task] = []

        for relative_path in paths:

            record = inspect_file(
                relative_path
            )

            artifact_records[task].append(
                record
            )

            total_artifacts += 1

            if record["readable"]:
                valid_artifacts += 1

        task_valid = sum(
            record["readable"]
            for record in artifact_records[task]
        )

        task_total = len(
            artifact_records[task]
        )

        print(
            f"    {task}: "
            f"{task_valid}/{task_total}"
        )

    print(
        f"    TOTAL: "
        f"{valid_artifacts}/{total_artifacts}"
    )

    # ============================================================
    # 3. Required evidence
    # ============================================================

    print("\n[3] Required evidence")

    evidence_paths = {

        "FMP-06": (
            "modeling/FMP/metrics/"
            "fmp06_final_phase_closure.json"
        ),

        "FMP-07": (
            "modeling/FMP/metrics/"
            "fmp07_op006_final_modeling_freeze_release_manifest.json"
        ),

        "H-RUN-021R3": (
            "modeling/FMP/metrics/"
            "h_run021r3_frozen_runtime_equivalence.json"
        ),

        "H-RUN-023R2": (
            "modeling/FMP/metrics/"
            "h_run023r2_final_runtime_freeze_manifest.json"
        ),

        "H-RUN-024": (
            "modeling/FMP/metrics/"
            "h_run024_final_e2e_demonstration.json"
        ),
    }

    evidence_records = {}

    for name, relative_path in evidence_paths.items():

        record = inspect_file(
            relative_path
        )

        evidence_records[name] = record

        status = (
            "PASS"
            if record["readable"]
            else "MISSING"
        )

        print(
            f"    {name}: {status}"
        )

    # ============================================================
    # 4. Deployment runtime
    # ============================================================

    print("\n[4] Deployment runtime")

    runtime_destination = (
        DEPLOYMENT_RUNTIME_DIR
        / "ticket_pipeline.py"
    )

    shutil.copy2(
        pipeline_path,
        runtime_destination,
    )

    print(
        "    Runtime copied:"
    )

    print(
        f"    {runtime_destination}"
    )

    # ============================================================
    # 5. Requirements
    # ============================================================

    requirements_path = (
        DEPLOYMENT_DIR
        / "requirements.txt"
    )

    requirements_lines = [
        "joblib",
        "numpy",
        "pandas",
        "scikit-learn",
        "scipy",
    ]

    requirements_path.write_text(
        "\n".join(requirements_lines) + "\n",
        encoding="utf-8",
    )

    print(
        "    Requirements:"
    )

    print(
        f"    {requirements_path}"
    )

    # ============================================================
    # 6. README
    # ============================================================

    readme_path = (
        DEPLOYMENT_DIR / "README.md"
    )

    readme_lines = [
        "# IT Ticket Intelligence - Deployment Runtime",
        "",
        "## Runtime API",
        "",
        "The validated runtime provides:",
        "",
        "- TicketPipeline.predict(ticket)",
        "- TicketPipeline.predict_batch(tickets)",
        "",
        "## Pipeline",
        "",
        "T1 -> T2 -> T3 -> T4 -> T5 -> T6 -> T7 -> T8 -> T9 -> T10 -> T11",
        "",
        "## Important boundaries",
        "",
        "- T1-T7 use frozen modeling artifacts.",
        "- T8 preserves native evidence semantics.",
        "- Missing evidence is not treated as a negative outcome.",
        "- T9 does not create universal confidence or universal risk.",
        "- T10 does not establish an empirically validated autonomous threshold.",
        "- T11 represents lifecycle and feedback state.",
        "",
        "## T6 limitation",
        "",
        "The full frozen MOD-010 semantic branch depends on stored",
        "evaluation-population semantic evidence.",
        "",
        "A genuinely new ticket therefore reports the explicit",
        "PARTIAL_NATIVE_RUNTIME boundary rather than fabricating",
        "a semantic score.",
        "",
        "## T7 limitation",
        "",
        "The frozen survival model executes using the authoritative",
        "21-feature creation-time construction.",
        "",
        "Tickets outside the observed training temporal range receive",
        "an explicit temporal-support limitation.",
        "",
        "## Decision boundary",
        "",
        "The system provides decision support.",
        "",
        "It does not claim autonomous ticket disposition.",
        "",
        "Human decision remains required where the T10 policy boundary",
        "indicates incomplete or unsupported evidence.",
    ]

    readme_path.write_text(
        "\n".join(readme_lines) + "\n",
        encoding="utf-8",
    )

    print(
        "    README:"
    )

    print(
        f"    {readme_path}"
    )

    # ============================================================
    # 7. Final manifest
    # ============================================================

    print("\n[5] Final manifest")

    evidence_valid = all(
        record["readable"]
        for record in evidence_records.values()
    )

    package_pass = (
        runtime["readable"]
        and runtime["class_present"]
        and runtime["predict_present"]
        and runtime["predict_batch_present"]
        and runtime["importable"]
        and valid_artifacts == total_artifacts
        and evidence_valid
    )

    manifest = {
        "operation": "H-RUN-026-OP-001",
        "operation_name": (
            "deployment package assembly"
        ),
        "status": (
            "PASS"
            if package_pass
            else "REQUIRES_REVIEW"
        ),

        "runtime_contract": runtime,

        "frozen_artifacts": artifact_records,

        "evidence": evidence_records,

        "deployment_package": {
            "directory": str(
                DEPLOYMENT_DIR
            ),
            "runtime": str(
                runtime_destination
            ),
            "requirements": str(
                requirements_path
            ),
            "readme": str(
                readme_path
            ),
            "model_artifacts_copied": False,
            "source_models_modified": False,
        },

        "controls": {
            "model_retraining": False,
            "model_modification": False,
            "threshold_optimization": False,
            "locked_test_reuse": False,
            "prediction_modification": False,
            "synthetic_feedback": False,
            "dataset_modification": False,
            "mozilla_archive_access": False,
        },
    }

    OUTPUT.write_text(
        json.dumps(
            manifest,
            indent=2,
        ),
        encoding="utf-8",
    )

    # ============================================================
    # Final output
    # ============================================================

    print("\n" + "=" * 70)
    print(
        "H-RUN-026-OP-001 RESULT"
    )
    print("=" * 70)

    print(
        "Runtime contract : "
        f"{'PASS' if runtime['importable'] else 'FAIL'}"
    )

    print(
        "Frozen artifacts : "
        f"{valid_artifacts}/{total_artifacts}"
    )

    print(
        "Evidence files   : "
        f"{sum(r['readable'] for r in evidence_records.values())}/"
        f"{len(evidence_records)}"
    )

    print(
        "Model modified   : NO"
    )

    print(
        "Retraining       : NO"
    )

    print(
        "FINAL STATUS     : "
        f"{'PASS' if package_pass else 'REQUIRES_REVIEW'}"
    )

    print(
        f"Manifest         : {OUTPUT}"
    )


if __name__ == "__main__":
    main()