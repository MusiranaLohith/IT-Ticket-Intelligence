from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


RUNTIME_DIR = Path(__file__).resolve().parent


def find_project_root() -> Path:
    for candidate in [RUNTIME_DIR, *RUNTIME_DIR.parents]:
        if (
            (candidate / "modeling").is_dir()
            and (candidate / "modeling" / "T1").is_dir()
            and (candidate / "modeling" / "FMP").is_dir()
        ):
            return candidate

    raise RuntimeError(
        "Could not locate IT-Ticket-Triage-System project root."
    )


PROJECT_ROOT = find_project_root()

if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from ticket_pipeline import TicketPipeline


OUTPUT_JSON = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "h_run023r2_final_runtime_freeze_manifest.json"
)


FROZEN_ARTIFACTS = {
    "T1": (
        PROJECT_ROOT
        / "modeling/T1/baselines/t1_it_support_char_svm.joblib"
    ),

    "T2": (
        PROJECT_ROOT
        / "modeling/T2/models/t2_class_weighted_tfidf_logreg.joblib"
    ),

    "T3": (
        PROJECT_ROOT
        / "modeling/T3/models/t3_class_weighted_tfidf_logreg.joblib"
    ),

    "T4_tfidf": (
        PROJECT_ROOT
        / "modeling/T4/results/mod007_checkpoints/t4_mod007_tfidf.joblib"
    ),

    "T4_neighbors": (
        PROJECT_ROOT
        / "modeling/T4/results/mod007_checkpoints/t4_mod007_neighbors.joblib"
    ),

    "T4_retrieval": (
        PROJECT_ROOT
        / "modeling/T4/results/mod007_checkpoints/t4_mod007_full_retrieval.npz"
    ),

    "T5_tfidf": (
        PROJECT_ROOT
        / "modeling/T5/models/t5_mod005_tfidf.joblib"
    ),

    "T5_logreg": (
        PROJECT_ROOT
        / "modeling/T5/models/t5_mod005_logreg.joblib"
    ),

    "T5_calibrated_vectorizer": (
        PROJECT_ROOT
        / "modeling/T5/models/t5_mod007_calibrated_tfidf.joblib"
    ),

    "T5_calibration_models": (
        PROJECT_ROOT
        / "modeling/T5/models/t5_mod007_calibration_models.joblib"
    ),

    "T6": (
        PROJECT_ROOT
        / "modeling/T6/metrics/t6_mod010_corrected_hybrid_results.json"
    ),

    "T7": (
        PROJECT_ROOT
        / "modeling/T7/metrics/t7_mod010_log_normal_aft_model.json"
    ),
}


REQUIRED_EVIDENCE = {
    "FMP-06 closure": (
        PROJECT_ROOT
        / "modeling/FMP/metrics/fmp06_final_phase_closure.json"
    ),

    "FMP-07 freeze": (
        PROJECT_ROOT
        / "modeling/FMP/metrics/fmp07_op006_final_modeling_freeze_release_manifest.json"
    ),

    "H-RUN-021R3": (
        PROJECT_ROOT
        / "modeling/FMP/metrics/h_run021r3_frozen_runtime_equivalence.json"
    ),
}


# H-RUN-022R2 was successfully executed, but its artifact was
# written outside the project root by the original validation script.
# We reference that existing evidence explicitly rather than
# regenerating or silently moving it.
H_RUN_022_SOURCE = Path(
    "/home/whiteblack/Documents/modeling/FMP/metrics/"
    "h_run022r2_realistic_multi_ticket_validation.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def inspect_pipeline():
    report = {
        "class_available": False,
        "predict_available": False,
        "predict_batch_available": False,
        "initialization_pass": False,
        "errors": [],
    }

    try:
        report["class_available"] = TicketPipeline is not None

        report["predict_available"] = hasattr(
            TicketPipeline,
            "predict",
        )

        report["predict_batch_available"] = hasattr(
            TicketPipeline,
            "predict_batch",
        )

        pipeline = TicketPipeline()

        report["initialization_pass"] = pipeline is not None

    except Exception as exc:
        report["errors"].append(
            f"{type(exc).__name__}: {exc}"
        )

    return report


def inspect_json(path: Path):
    if not path.exists():
        return {
            "exists": False,
            "readable": False,
            "status": None,
            "operation": None,
            "final_status": None,
            "data": None,
        }

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        return {
            "exists": True,
            "readable": True,
            "status": data.get("status"),
            "operation": data.get("operation"),
            "final_status": data.get("final_status"),
            "data": data,
        }

    except Exception as exc:
        return {
            "exists": True,
            "readable": False,
            "status": None,
            "operation": None,
            "final_status": None,
            "data": None,
            "error": (
                f"{type(exc).__name__}: {exc}"
            ),
        }


def main():

    print("=" * 78)
    print("H-RUN-023R2 — FINAL RUNTIME FREEZE")
    print("=" * 78)

    # ---------------------------------------------------------
    # 1. PROJECT ROOT
    # ---------------------------------------------------------

    print()
    print("[1] Project root:")
    print(f"  {PROJECT_ROOT}")

    # ---------------------------------------------------------
    # 2. PIPELINE CONTRACT
    # ---------------------------------------------------------

    print()
    print("[2] Inspecting reusable TicketPipeline...")

    pipeline_report = inspect_pipeline()

    print(
        "Class available       :",
        pipeline_report["class_available"],
    )

    print(
        "predict() available   :",
        pipeline_report["predict_available"],
    )

    print(
        "predict_batch()       :",
        pipeline_report["predict_batch_available"],
    )

    print(
        "Initialization        :",
        pipeline_report["initialization_pass"],
    )

    # ---------------------------------------------------------
    # 3. FROZEN MODEL ARTIFACTS
    # ---------------------------------------------------------

    print()
    print("[3] Checking frozen T1–T7 artifacts...")

    artifact_report = {}

    for name, path in FROZEN_ARTIFACTS.items():

        exists = path.exists()
        readable = False
        size = None
        digest = None

        if exists:
            try:
                size = path.stat().st_size
                digest = sha256_file(path)
                readable = True
            except Exception:
                readable = False

        artifact_report[name] = {
            "path": str(path),
            "exists": exists,
            "readable": readable,
            "size_bytes": size,
            "sha256": digest,
        }

        print(
            f"  {name:<24} "
            f"{'PASS' if exists and readable else 'FAIL'}"
        )

    # ---------------------------------------------------------
    # 4. REQUIRED EVIDENCE
    # ---------------------------------------------------------

    print()
    print("[4] Checking authoritative freeze evidence...")

    evidence_report = {}

    for name, path in REQUIRED_EVIDENCE.items():

        report = inspect_json(path)

        evidence_report[name] = {
            "path": str(path),
            "exists": report["exists"],
            "readable": report["readable"],
            "status": report["status"],
            "operation": report["operation"],
            "final_status": report["final_status"],
        }

        print(
            f"  {name:<24} "
            f"{'PASS' if report['exists'] and report['readable'] else 'FAIL'}"
        )

    # ---------------------------------------------------------
    # 5. H-RUN-021R3 ACTUAL EQUIVALENCE VALIDATION
    # ---------------------------------------------------------

    print()
    print("[5] Reading H-RUN-021R3 final status...")

    h021_path = Path(
        evidence_report["H-RUN-021R3"]["path"]
    )

    h021 = inspect_json(h021_path)
    h021_data = h021.get("data")

    if not isinstance(h021_data, dict):
        h021_pass = False
    else:
        h021_final_status = (
            h021_data.get("final_status")
        )

        h021_validation = (
            h021_data.get("validation", {})
        )

        # IMPORTANT:
        # This is the actual field produced by H-RUN-021R3.
        #
        # Do NOT use "equivalence_pass".
        #
        # H-RUN-021R3 records:
        #   all_equivalence_checks_pass: true
        h021_all_equivalence_checks_pass = (
            h021_validation.get(
                "all_equivalence_checks_pass",
                False,
            )
        )

        h021_pass = (
            h021_final_status == "PASS"
            and h021_all_equivalence_checks_pass is True
        )

    print(
        "  H-RUN-021R3:",
        "PASS" if h021_pass else "FAIL",
    )

    # ---------------------------------------------------------
    # 6. H-RUN-022R2 ACTUAL VALIDATION
    # ---------------------------------------------------------

    print()
    print("[6] Reading existing H-RUN-022R2 evidence...")

    h022 = inspect_json(H_RUN_022_SOURCE)
    h022_data = h022.get("data")

    h022_pass = (
        h022["readable"]
        and isinstance(h022_data, dict)
        and h022_data.get("status")
        == "PASS_WITH_LIMITATIONS"
        and h022_data.get("ticket_count")
        == 15
        and h022_data.get("results_returned")
        == 15
        and len(
            h022_data.get(
                "structural_failures",
                [],
            )
        ) == 0
        and all(
            value == 0
            for value in h022_data.get(
                "stage_failure_counts",
                {},
            ).values()
        )
        and len(
            h022_data.get(
                "integrity_failures",
                [],
            )
        ) == 0
    )

    print(
        "  H-RUN-022R2:",
        "PASS" if h022_pass else "FAIL",
    )

    print(
        "  Source:",
        H_RUN_022_SOURCE,
    )

    # ---------------------------------------------------------
    # 7. AGGREGATE FREEZE CRITERIA
    # ---------------------------------------------------------

    artifact_failures = [
        name
        for name, record in artifact_report.items()
        if not record["exists"]
        or not record["readable"]
    ]

    evidence_failures = [
        name
        for name, record in evidence_report.items()
        if not record["exists"]
        or not record["readable"]
    ]

    pipeline_pass = (
        pipeline_report["class_available"]
        and pipeline_report["predict_available"]
        and pipeline_report["predict_batch_available"]
        and pipeline_report["initialization_pass"]
        and not pipeline_report["errors"]
    )

    freeze_pass = (
        pipeline_pass
        and not artifact_failures
        and not evidence_failures
        and h021_pass
        and h022_pass
    )

    final_status = (
        "FROZEN_PASS"
        if freeze_pass
        else "REQUIRES_REVIEW"
    )

    # ---------------------------------------------------------
    # 8. MANIFEST
    # ---------------------------------------------------------

    manifest = {
        "operation": "H-RUN-023R2",

        "operation_name":
            "final_runtime_freeze",

        "timestamp_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "project_root":
            str(PROJECT_ROOT),

        "status":
            final_status,

        "runtime": {
            "module":
                str(
                    RUNTIME_DIR
                    / "ticket_pipeline.py"
                ),

            "pipeline":
                pipeline_report,
        },

        "frozen_artifacts":
            artifact_report,

        "required_evidence":
            evidence_report,

        "runtime_validation": {

            "H-RUN-021R3": {
                "status":
                    "PASS"
                    if h021_pass
                    else "FAIL",

                "final_status":
                    h021_data.get(
                        "final_status"
                    )
                    if isinstance(
                        h021_data,
                        dict,
                    )
                    else None,

                "all_equivalence_checks_pass":
                    h021_data.get(
                        "validation",
                        {},
                    ).get(
                        "all_equivalence_checks_pass"
                    )
                    if isinstance(
                        h021_data,
                        dict,
                    )
                    else None,
            },

            "H-RUN-022R2": {
                "status":
                    "PASS"
                    if h022_pass
                    else "FAIL",

                "source_path":
                    str(H_RUN_022_SOURCE),

                "source_is_outside_project_root":
                    True,

                "validated_ticket_count":
                    h022_data.get(
                        "ticket_count"
                    )
                    if isinstance(
                        h022_data,
                        dict,
                    )
                    else None,

                "results_returned":
                    h022_data.get(
                        "results_returned"
                    )
                    if isinstance(
                        h022_data,
                        dict,
                    )
                    else None,

                "original_validation_status":
                    h022_data.get(
                        "status"
                    )
                    if isinstance(
                        h022_data,
                        dict,
                    )
                    else None,
            },
        },

        "validation": {

            "pipeline_pass":
                pipeline_pass,

            "artifact_failures":
                artifact_failures,

            "evidence_failures":
                evidence_failures,

            "H-RUN-021R3_pass":
                h021_pass,

            "H-RUN-022R2_pass":
                h022_pass,
        },

        "freeze_controls": {

            "runtime_source_modification_authorized":
                False,

            "model_retraining":
                False,

            "model_modification":
                False,

            "threshold_optimization":
                False,

            "locked_test_reuse":
                False,

            "prediction_modification":
                False,

            "synthetic_feedback":
                False,
        },

        "known_runtime_boundaries": {

            "T6_full_MOD010_new_ticket_semantic_runtime":
                False,

            "T7_2026_temporal_support":
                False,

            "T8_missing_evidence_is_not_negative":
                True,

            "T9_universal_confidence":
                False,

            "T9_universal_risk":
                False,

            "T10_automatic_action_policy":
                False,

            "T11_operational_feedback_population":
                False,
        },

        "release_state":
            (
                "RUNTIME_FROZEN"
                if freeze_pass
                else "RUNTIME_NOT_FROZEN"
            ),
    }

    # ---------------------------------------------------------
    # 9. WRITE MANIFEST
    # ---------------------------------------------------------

    OUTPUT_JSON.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            manifest,
            f,
            indent=2,
            default=str,
        )

    # ---------------------------------------------------------
    # 10. TERMINAL SUMMARY
    # ---------------------------------------------------------

    print()
    print("=" * 78)
    print("H-RUN-023R2 SUMMARY")
    print("=" * 78)

    print(
        "Pipeline contract       :",
        "PASS" if pipeline_pass else "FAIL",
    )

    print(
        "Frozen artifacts        :",
        f"{len(FROZEN_ARTIFACTS) - len(artifact_failures)}/"
        f"{len(FROZEN_ARTIFACTS)}",
    )

    print(
        "H-RUN-021R3 equivalence :",
        "PASS" if h021_pass else "FAIL",
    )

    print(
        "H-RUN-022R2 validation  :",
        "PASS" if h022_pass else "FAIL",
    )

    print()
    print(
        "FINAL STATUS             :",
        final_status,
    )

    print()
    print("[FREEZE CONTROLS]")
    print("Model retraining         : NO")
    print("Model modification       : NO")
    print("Threshold optimization   : NO")
    print("Locked test reuse        : NO")
    print("Prediction modification  : NO")
    print("Synthetic feedback       : NO")

    print()
    print("[ARTIFACT]")
    print(f"JSON : {OUTPUT_JSON}")


if __name__ == "__main__":
    main()