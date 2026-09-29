from __future__ import annotations

import hashlib
import json
import py_compile
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

FMP_ROOT = PROJECT_ROOT / "modeling" / "FMP"
METRICS_ROOT = FMP_ROOT / "metrics"
SCRIPTS_ROOT = FMP_ROOT / "scripts"


OUTPUT_PATH = (
    METRICS_ROOT
    / "h_run018_final_runtime_freeze.json"
)


REQUIRED_FILES = {
    "runtime_orchestrator": (
        SCRIPTS_ROOT
        / "h_run015_final_ticket_orchestrator.py"
    ),
    "multi_ticket_validation_script": (
        SCRIPTS_ROOT
        / "h_run017_multi_ticket_runtime_validation.py"
    ),
    "multi_ticket_validation_result": (
        METRICS_ROOT
        / "h_run017r3_multi_ticket_runtime_validation.json"
    ),
    "t1_runtime_probe": (
        SCRIPTS_ROOT
        / "fmp06_op018r5_t1_corrected_frozen_runtime_probe.py"
    ),
    "t2_t3_runtime_probe": (
        SCRIPTS_ROOT
        / "fmp06_op018r3_corrected_frozen_runtime_inference_probe.py"
    ),
    "t6_runtime_probe": (
        SCRIPTS_ROOT
        / "fmp06_op018r21_t6_mod010_frozen_runtime_composition_probe.py"
    ),
    "t7_runtime_probe": (
        SCRIPTS_ROOT
        / "fmp06_op018r22c_t7_compact_runtime_interface_resolution.py"
    ),
    "fmp06_final_closure": (
        SCRIPTS_ROOT
        / "fmp06_final_phase_closure.py"
    ),
    "fmp07_freeze_manifest": (
        METRICS_ROOT
        / "fmp07_op006_final_modeling_freeze_release_manifest.json"
    ),
    "fmp07_completeness": (
        METRICS_ROOT
        / "fmp07_op005r1_final_frozen_modeling_package_completeness_audit.json"
    ),
    "fmp07_integrity_manifest": (
        METRICS_ROOT
        / "fmp07_op002_frozen_artifact_integrity_hash_manifest.json"
    ),
    "fmp06_closure": (
        METRICS_ROOT
        / "fmp06_final_phase_closure.json"
    ),
    "t8_runtime_validation": (
        METRICS_ROOT
        / "t8_mod036_op026_decision_engine_validation.json"
    ),
    "t9_closure": (
        PROJECT_ROOT
        / "modeling"
        / "T9"
        / "mod037"
        / "t9_mod037_op015_final_integrated_closure.json"
    ),
    "t10_policy_evidence": (
        METRICS_ROOT
        / "fmp05_op008_empirical_policy_boundary_audit.json"
    ),
}


FROZEN_MODEL_ARTIFACTS = {
    "T1": [
        PROJECT_ROOT
        / "modeling"
        / "T1"
        / "baselines"
        / "t1_it_support_char_svm.joblib",
    ],
    "T2": [
        PROJECT_ROOT
        / "modeling"
        / "T2"
        / "models"
        / "t2_class_weighted_tfidf_logreg.joblib",
    ],
    "T3": [
        PROJECT_ROOT
        / "modeling"
        / "T3"
        / "models"
        / "t3_class_weighted_tfidf_logreg.joblib",
    ],
    "T4": [
        PROJECT_ROOT
        / "modeling"
        / "T4"
        / "results"
        / "mod007_checkpoints"
        / "t4_mod007_tfidf.joblib",
        PROJECT_ROOT
        / "modeling"
        / "T4"
        / "results"
        / "mod007_checkpoints"
        / "t4_mod007_neighbors.joblib",
        PROJECT_ROOT
        / "modeling"
        / "T4"
        / "results"
        / "mod007_checkpoints"
        / "t4_mod007_full_retrieval.npz",
    ],
    "T5": [
        PROJECT_ROOT
        / "modeling"
        / "T5"
        / "results"
        / "t5_mod005_tfidf.joblib",
        PROJECT_ROOT
        / "modeling"
        / "T5"
        / "results"
        / "t5_mod005_logreg.joblib",
        PROJECT_ROOT
        / "modeling"
        / "T5"
        / "results"
        / "t5_mod007_calibrated_tfidf.joblib",
        PROJECT_ROOT
        / "modeling"
        / "T5"
        / "results"
        / "t5_mod007_calibration_models.joblib",
    ],
    "T6": [
        PROJECT_ROOT
        / "modeling"
        / "T6"
        / "metrics"
        / "t6_mod010_corrected_hybrid_results.json",
    ],
    "T7": [
        PROJECT_ROOT
        / "modeling"
        / "T7"
        / "metrics"
        / "t7_mod010_log_normal_aft_model.json",
    ],
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def read_json(path: Path) -> dict:
    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


def syntax_check(path: Path) -> dict:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "py_compile",
            str(path),
        ],
        capture_output=True,
        text=True,
    )

    return {
        "path": str(path),
        "status": (
            "PASS"
            if result.returncode == 0
            else "FAIL"
        ),
        "return_code": result.returncode,
        "stderr": result.stderr.strip(),
    }


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:

    print("=" * 72)
    print(
        "H-RUN-018 — FINAL RUNTIME FREEZE "
        "& DELIVERY RECONCILIATION"
    )
    print("=" * 72)

    report = {
        "operation": "H-RUN-018",
        "operation_name": (
            "Final Runtime Freeze & Delivery Reconciliation"
        ),
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": "REQUIRES_REVIEW",
        "controls": {
            "retraining": False,
            "model_modification": False,
            "prediction_modification": False,
            "threshold_optimization": False,
            "locked_test_use": False,
            "new_model_selection": False,
            "universal_confidence_creation": False,
            "universal_risk_creation": False,
            "synthetic_fusion_target_creation": False,
        },
        "checks": {},
    }

    # ------------------------------------------------------------
    # 1. Required runtime/package files
    # ------------------------------------------------------------

    print("\n[1] Required runtime/package files")

    file_results = {}

    for name, path in REQUIRED_FILES.items():

        exists = path.exists()

        record = {
            "path": str(path),
            "exists": exists,
        }

        if exists:
            record["size_bytes"] = path.stat().st_size
            record["sha256"] = sha256_file(path)

        file_results[name] = record

        print(
            f"{name}:",
            "PASS" if exists else "MISSING",
        )

    report["checks"]["required_files"] = (
        file_results
    )

    # ------------------------------------------------------------
    # 2. H-RUN-017R3 result reconciliation
    # ------------------------------------------------------------

    print(
        "\n[2] H-RUN-017R3 multi-ticket validation"
    )

    validation_path = REQUIRED_FILES[
        "multi_ticket_validation_result"
    ]

    require(
        validation_path.exists(),
        "H-RUN-017R3 result is missing.",
    )

    validation = read_json(
        validation_path
    )

    validation_status = validation.get(
        "status"
    )

    tickets = validation.get(
        "tickets",
        [],
    )

    ticket_statuses = [
        ticket.get("status")
        for ticket in tickets
    ]

    validation_pass = (
        validation_status == "PASS"
        and len(tickets) == 3
        and all(
            status == "PASS"
            for status in ticket_statuses
        )
    )

    print(
        "Recorded status:",
        validation_status,
    )

    print(
        "Ticket count:",
        len(tickets),
    )

    print(
        "Ticket statuses:",
        ticket_statuses,
    )

    print(
        "Multi-ticket validation:",
        "PASS" if validation_pass else "FAIL",
    )

    report["checks"][
        "multi_ticket_runtime_validation"
    ] = {
        "status": (
            "PASS"
            if validation_pass
            else "FAIL"
        ),
        "recorded_status": validation_status,
        "ticket_count": len(tickets),
        "ticket_statuses": ticket_statuses,
    }

    # ------------------------------------------------------------
    # 3. Frozen model artifact inventory
    # ------------------------------------------------------------

    print(
        "\n[3] Frozen model artifact inventory"
    )

    frozen_results = {}
    total_expected = 0
    total_present = 0

    for task, paths in FROZEN_MODEL_ARTIFACTS.items():

        task_records = []

        for path in paths:

            total_expected += 1

            exists = path.exists()

            if exists:
                total_present += 1

            record = {
                "path": str(path),
                "exists": exists,
            }

            if exists:
                record["size_bytes"] = (
                    path.stat().st_size
                )
                record["sha256"] = (
                    sha256_file(path)
                )

            task_records.append(record)

        frozen_results[task] = task_records

        task_status = (
            "PASS"
            if all(
                record["exists"]
                for record in task_records
            )
            else "FAIL"
        )

        print(
            f"{task}:",
            task_status,
        )

    frozen_pass = (
        total_expected == total_present
    )

    print(
        "Frozen artifacts:",
        f"{total_present}/{total_expected}",
    )

    report["checks"][
        "frozen_model_artifacts"
    ] = {
        "status": (
            "PASS"
            if frozen_pass
            else "FAIL"
        ),
        "expected": total_expected,
        "present": total_present,
        "artifacts": frozen_results,
    }

    # ------------------------------------------------------------
    # 4. FMP freeze state
    # ------------------------------------------------------------

    print("\n[4] FMP freeze state")

    freeze_manifest_path = REQUIRED_FILES[
        "fmp07_freeze_manifest"
    ]

    require(
        freeze_manifest_path.exists(),
        "FMP-07 freeze manifest is missing.",
    )

    freeze_manifest = read_json(
        freeze_manifest_path
    )

    freeze_status = freeze_manifest.get(
        "status"
    )

    freeze_state = freeze_manifest.get(
        "release_state"
    )

    print(
        "FMP-07 status:",
        freeze_status,
    )

    print(
        "Release state:",
        freeze_state,
    )

    fmp_freeze_pass = (
        freeze_status == "FROZEN_PASS"
        and freeze_state == "FROZEN"
    )

    report["checks"]["fmp07_freeze"] = {
        "status": (
            "PASS"
            if fmp_freeze_pass
            else "FAIL"
        ),
        "recorded_status": freeze_status,
        "release_state": freeze_state,
    }

    # ------------------------------------------------------------
    # 5. FMP-06 closure
    # ------------------------------------------------------------

    print("\n[5] FMP-06 closure")

    fmp06_path = REQUIRED_FILES[
        "fmp06_closure"
    ]

    require(
        fmp06_path.exists(),
        "FMP-06 closure artifact is missing.",
    )

    fmp06 = read_json(
        fmp06_path
    )

    fmp06_status = fmp06.get(
        "status"
    )

    print(
        "FMP-06 status:",
        fmp06_status,
    )

    fmp06_pass = (
        fmp06_status == "CLOSED_PASS"
    )

    report["checks"]["fmp06_closure"] = {
        "status": (
            "PASS"
            if fmp06_pass
            else "FAIL"
        ),
        "recorded_status": fmp06_status,
    }

    # ------------------------------------------------------------
    # 6. T8/T9/T10 boundary preservation
    # ------------------------------------------------------------

    print(
        "\n[6] T8/T9/T10 boundary preservation"
    )

    t8_path = REQUIRED_FILES[
        "t8_runtime_validation"
    ]

    t9_path = REQUIRED_FILES[
        "t9_closure"
    ]

    t10_path = REQUIRED_FILES[
        "t10_policy_evidence"
    ]

    t8 = read_json(t8_path)
    t9 = read_json(t9_path)
    t10 = read_json(t10_path)

    t8_status = (
        t8.get("closure_status")
        or t8.get("status")
    )

    t9_status = t9.get(
        "status"
    )

    t10_automation = t10.get(
        "automation",
        t10.get(
            "automation_status",
            "NOT_ESTABLISHED",
        ),
    )

    print(
        "T8:",
        t8_status,
    )

    print(
        "T9:",
        t9_status,
    )

    print(
        "T10 automation:",
        t10_automation,
    )

    boundary_pass = (
        t8_status in {
            "T8_DECISION_ENGINE_CLOSED",
            "CLOSED",
            "PASS",
            "CLOSED_PASS",
        }
        and t9_status in {
            "PASS",
            "CLOSED_PASS",
            "CLOSED",
        }
    )

    report["checks"][
        "downstream_boundaries"
    ] = {
        "status": (
            "PASS"
            if boundary_pass
            else "REQUIRES_REVIEW"
        ),
        "t8_status": t8_status,
        "t9_status": t9_status,
        "t10_automation": t10_automation,
        "universal_confidence_created": False,
        "universal_risk_created": False,
        "autonomous_automation_established": False,
    }

    # ------------------------------------------------------------
    # 7. Runtime source syntax
    # ------------------------------------------------------------

    print(
        "\n[7] Runtime source syntax"
    )

    runtime_scripts = [
        REQUIRED_FILES[
            "runtime_orchestrator"
        ],
        REQUIRED_FILES[
            "multi_ticket_validation_script"
        ],
        REQUIRED_FILES[
            "t1_runtime_probe"
        ],
        REQUIRED_FILES[
            "t2_t3_runtime_probe"
        ],
        REQUIRED_FILES[
            "t6_runtime_probe"
        ],
        REQUIRED_FILES[
            "t7_runtime_probe"
        ],
        REQUIRED_FILES[
            "fmp06_final_closure"
        ],
    ]

    syntax_results = []

    for path in runtime_scripts:

        result = syntax_check(path)

        syntax_results.append(result)

        print(
            path.name + ":",
            result["status"],
        )

    syntax_pass = all(
        result["status"] == "PASS"
        for result in syntax_results
    )

    report["checks"][
        "runtime_source_syntax"
    ] = {
        "status": (
            "PASS"
            if syntax_pass
            else "FAIL"
        ),
        "results": syntax_results,
    }

    # ------------------------------------------------------------
    # 8. Final freeze decision
    # ------------------------------------------------------------

    print(
        "\n[8] Final runtime freeze decision"
    )

    all_required_files = all(
        record["exists"]
        for record in file_results.values()
    )

    final_pass = all(
        [
            all_required_files,
            validation_pass,
            frozen_pass,
            fmp_freeze_pass,
            fmp06_pass,
            boundary_pass,
            syntax_pass,
        ]
    )

    report["status"] = (
        "FROZEN_PASS"
        if final_pass
        else "REQUIRES_REVIEW"
    )

    report["release_state"] = (
        "RUNTIME_FROZEN"
        if final_pass
        else "NOT_FROZEN"
    )

    report["final_boundary"] = {
        "t1_t7_runtime": (
            "VALIDATED"
            if final_pass
            else "REQUIRES_REVIEW"
        ),
        "t8": "CLOSED",
        "t9": "CLOSED",
        "t10_automation": "NOT_ESTABLISHED",
        "t11": "SPECIFICATION_ONLY",
        "t6_new_ticket_mode": (
            "PARTIAL_NATIVE_RUNTIME"
        ),
        "t7_new_ticket_support": (
            "OUTSIDE_OBSERVED_TRAINING_RANGE "
            "FOR_2026_DEVELOPMENT_TICKETS"
        ),
    }

    report["delivery_statement"] = (
        "The frozen ticket-facing runtime is a "
        "development/runtime integration artifact. "
        "It does not establish autonomous routing, "
        "priority, severity, duplicate, assignment, "
        "or resolution decisions. T6 remains partial "
        "for genuinely new tickets because the full "
        "MOD-010 semantic evidence is not available "
        "at new-ticket inference time. T7 runtime "
        "outputs remain subject to the observed "
        "temporal training-support limitation."
    )

    METRICS_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        "Required files:",
        "PASS"
        if all_required_files
        else "FAIL",
    )

    print(
        "Multi-ticket runtime:",
        "PASS"
        if validation_pass
        else "FAIL",
    )

    print(
        "Frozen artifacts:",
        "PASS"
        if frozen_pass
        else "FAIL",
    )

    print(
        "FMP-07 freeze:",
        "PASS"
        if fmp_freeze_pass
        else "FAIL",
    )

    print(
        "FMP-06 closure:",
        "PASS"
        if fmp06_pass
        else "FAIL",
    )

    print(
        "T8/T9/T10 boundary:",
        "PASS"
        if boundary_pass
        else "REVIEW",
    )

    print(
        "Runtime syntax:",
        "PASS"
        if syntax_pass
        else "FAIL",
    )

    print(
        "\nOutput:",
        OUTPUT_PATH,
    )

    print("\n" + "=" * 72)
    print(
        "H-RUN-018 STATUS:",
        report["status"],
    )
    print(
        "RELEASE STATE:",
        report["release_state"],
    )
    print("=" * 72)


if __name__ == "__main__":
    main()