from pathlib import Path
import json
from datetime import datetime, timezone


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
MODEL = ROOT / "modeling"
FMP = MODEL / "FMP"
METRICS = FMP / "metrics"


AUTHORITATIVE_FILES = {
    # T1–T7 / FMP closure evidence
    "T1_closure": MODEL / "T1" / "analysis" / "t1_final_closure.json",
    "T2_final_model": MODEL / "T2" / "models"
        / "t2_class_weighted_tfidf_logreg.joblib",
    "T3_final_model": MODEL / "T3" / "models"
        / "t3_class_weighted_tfidf_logreg.joblib",
    "T4_closure": MODEL / "T4" / "results" / "t4_mod013_closure.json",
    "T5_closure": MODEL / "T5" / "metrics"
        / "t5_mod011_final_closure.json",
    "T6_closure": MODEL / "T6" / "metrics"
        / "t6_final_closure.json",
    "T7_closure": MODEL / "T7" / "metrics"
        / "t7_mod012_final_closure.json",

    # T8 / T9 / T10
    "T8_closure": MODEL / "T8" / "mod036" / "op026"
        / "t8_mod036_op026_decision_engine_validation.json",
    "T9_closure": MODEL / "T9" / "mod037"
        / "t9_mod037_op015_final_integrated_closure.json",
    "T10_policy_evidence": METRICS
        / "fmp05_op008_empirical_policy_boundary_audit.json",

    # FMP phase closures
    "FMP06_closure": METRICS / "fmp06_final_phase_closure.json",
}


FROZEN_MODEL_ARTIFACTS = {
    "T1": [
        MODEL / "T1" / "baselines"
        / "t1_it_support_char_svm.joblib",
    ],
    "T2": [
        MODEL / "T2" / "models"
        / "t2_class_weighted_tfidf_logreg.joblib",
    ],
    "T3": [
        MODEL / "T3" / "models"
        / "t3_class_weighted_tfidf_logreg.joblib",
    ],
    "T4": [
        MODEL / "T4" / "results" / "mod007_checkpoints"
        / "t4_mod007_tfidf.joblib",
        MODEL / "T4" / "results" / "mod007_checkpoints"
        / "t4_mod007_neighbors.joblib",
        MODEL / "T4" / "results" / "mod007_checkpoints"
        / "t4_mod007_full_retrieval.npz",
    ],
    "T5": [
        MODEL / "T5" / "models" / "t5_mod005_tfidf.joblib",
        MODEL / "T5" / "models" / "t5_mod005_logreg.joblib",
        MODEL / "T5" / "models" / "t5_mod007_calibrated_tfidf.joblib",
        MODEL / "T5" / "models"
        / "t5_mod007_calibration_models.joblib",
    ],
    "T6": [
        MODEL / "T6" / "metrics"
        / "t6_mod010_corrected_hybrid_results.json",
    ],
    "T7": [
        MODEL / "T7" / "metrics"
        / "t7_mod010_log_normal_aft_model.json",
    ],
}


def file_info(path):
    if not path.exists():
        return {
            "exists": False,
            "readable": False,
            "size_bytes": None,
            "modified_utc": None,
        }

    try:
        size = path.stat().st_size
        modified = datetime.fromtimestamp(
            path.stat().st_mtime,
            tz=timezone.utc,
        ).isoformat()

        readable = path.is_file() and path.stat().st_size >= 0

        return {
            "exists": True,
            "readable": readable,
            "size_bytes": size,
            "modified_utc": modified,
        }

    except OSError:
        return {
            "exists": True,
            "readable": False,
            "size_bytes": None,
            "modified_utc": None,
        }


def main():
    print("=" * 72)
    print("FMP-07 OP-001 — REPRODUCIBILITY / FINAL MODELING FREEZE INVENTORY")
    print("=" * 72)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    print("\n[1] Authoritative closure/evidence inventory...")

    authoritative_results = {}
    authoritative_missing = []

    for name, path in AUTHORITATIVE_FILES.items():
        info = file_info(path)
        authoritative_results[name] = {
            "path": str(path),
            **info,
        }

        state = (
            "PRESENT"
            if info["exists"] and info["readable"]
            else "MISSING_OR_UNREADABLE"
        )

        print(f"  {name}: {state}")

        if state != "PRESENT":
            authoritative_missing.append(name)

    print("\n[2] Frozen model artifact inventory...")

    artifact_results = {}
    artifact_missing = []

    for task, paths in FROZEN_MODEL_ARTIFACTS.items():
        print(f"  {task}:")

        artifact_results[task] = []

        for path in paths:
            info = file_info(path)

            artifact_results[task].append({
                "path": str(path),
                **info,
            })

            state = (
                "PRESENT"
                if info["exists"] and info["readable"]
                else "MISSING_OR_UNREADABLE"
            )

            print(f"    {path.name}: {state}")

            if state != "PRESENT":
                artifact_missing.append(str(path))

    print("\n[3] T1–T7 closure/modeling freeze coverage...")

    task_coverage = {}

    for task in ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]:
        closure_present = False

        closure_keys = {
            "T1": "T1_closure",
            "T2": "T2_final_model",
            "T3": "T3_final_model",
            "T4": "T4_closure",
            "T5": "T5_closure",
            "T6": "T6_closure",
            "T7": "T7_closure",
        }

        key = closure_keys[task]

        closure_present = (
            authoritative_results[key]["exists"]
            and authoritative_results[key]["readable"]
        )

        artifacts_present = all(
            item["exists"] and item["readable"]
            for item in artifact_results[task]
        )

        task_coverage[task] = {
            "closure_or_final_binding_present": closure_present,
            "frozen_artifacts_present": artifacts_present,
            "freeze_inventory_pass": (
                closure_present and artifacts_present
            ),
        }

        print(
            f"  {task}: "
            f"{'PASS' if task_coverage[task]['freeze_inventory_pass'] else 'REQUIRES_REVIEW'}"
        )

    print("\n[4] T8–T10 final evidence coverage...")

    t8_present = (
        authoritative_results["T8_closure"]["exists"]
        and authoritative_results["T8_closure"]["readable"]
    )

    t9_present = (
        authoritative_results["T9_closure"]["exists"]
        and authoritative_results["T9_closure"]["readable"]
    )

    t10_present = (
        authoritative_results["T10_policy_evidence"]["exists"]
        and authoritative_results["T10_policy_evidence"]["readable"]
    )

    print(f"  T8 closure: {'PASS' if t8_present else 'REQUIRES_REVIEW'}")
    print(f"  T9 closure: {'PASS' if t9_present else 'REQUIRES_REVIEW'}")
    print(
        f"  T10 policy evidence: "
        f"{'PASS' if t10_present else 'REQUIRES_REVIEW'}"
    )

    print("\n[5] FMP-06 closure coverage...")

    fmp06_present = (
        authoritative_results["FMP06_closure"]["exists"]
        and authoritative_results["FMP06_closure"]["readable"]
    )

    print(
        f"  FMP-06 closure: "
        f"{'PASS' if fmp06_present else 'REQUIRES_REVIEW'}"
    )

    print("\n[6] Final inventory determination...")

    all_tasks_pass = all(
        item["freeze_inventory_pass"]
        for item in task_coverage.values()
    )

    final_pass = (
        not authoritative_missing
        and not artifact_missing
        and all_tasks_pass
        and t8_present
        and t9_present
        and t10_present
        and fmp06_present
    )

    status = "PASS" if final_pass else "REQUIRES_REVIEW"

    print(f"  Authoritative files missing: {len(authoritative_missing)}")
    print(f"  Frozen artifacts missing: {len(artifact_missing)}")
    print(
        f"  T1–T7 freeze coverage: "
        f"{'PASS' if all_tasks_pass else 'REQUIRES_REVIEW'}"
    )
    print(f"  Final inventory status: {status}")

    output = METRICS / "fmp07_op001_final_modeling_freeze_inventory.json"

    result = {
        "operation": "FMP-07 OP-001",
        "operation_name":
            "REPRODUCIBILITY_FINAL_MODELING_FREEZE_INVENTORY",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "read_only": True,
        "training_performed": False,
        "fitting_performed": False,
        "prediction_performed": False,
        "evaluation_performed": False,
        "locked_test_used": False,
        "artifact_modified": False,
        "authoritative_files": authoritative_results,
        "frozen_model_artifacts": artifact_results,
        "task_coverage": task_coverage,
        "final_evidence_coverage": {
            "T8": t8_present,
            "T9": t9_present,
            "T10": t10_present,
            "FMP06": fmp06_present,
        },
        "missing_authoritative_files": authoritative_missing,
        "missing_frozen_artifacts": artifact_missing,
        "interpretation": (
            "This operation inventories the final modeling and "
            "phase-closure evidence before reproducibility/final "
            "model freezing. It does not modify, retrain, evaluate, "
            "or replace any artifact."
        ),
    }

    with output.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("\n" + "=" * 72)
    print("OP-001 INVENTORY COMPLETE")
    print("=" * 72)
    print(f"STATUS: {status}")
    print(f"Output: {output}")
    print("No training performed.")
    print("No fitting performed.")
    print("No prediction performed.")
    print("No evaluation performed.")
    print("No locked test used.")
    print("No artifact modification performed.")


if __name__ == "__main__":
    main()