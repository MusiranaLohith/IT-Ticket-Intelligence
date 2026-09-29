from pathlib import Path
import json
from datetime import datetime, timezone


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
MODEL = ROOT / "modeling"
METRICS = MODEL / "FMP" / "metrics"


OUTPUT = (
    METRICS
    / "fmp07_op005_final_frozen_modeling_package_completeness_audit.json"
)


REQUIRED_FILES = {
    "T1_closure":
        MODEL / "T1/analysis/t1_final_closure.json",

    "T2_frozen_model":
        MODEL / "T2/models/t2_class_weighted_tfidf_logreg.joblib",

    "T3_frozen_model":
        MODEL / "T3/models/t3_class_weighted_tfidf_logreg.joblib",

    "T4_closure":
        MODEL / "T4/results/t4_mod013_closure.json",

    "T5_closure":
        MODEL / "T5/metrics/t5_mod011_final_closure.json",

    "T6_closure":
        MODEL / "T6/metrics/t6_final_closure.json",

    "T7_closure":
        MODEL / "T7/metrics/t7_mod012_final_closure.json",

    "T8_closure":
        MODEL
        / "T8/mod036/op026/"
        "t8_mod036_op026_decision_engine_validation.json",

    "T9_closure":
        MODEL
        / "T9/mod037/"
        "t9_mod037_op015_final_integrated_closure.json",

    "T10_policy":
        METRICS
        / "fmp05_op008_empirical_policy_boundary_audit.json",

    "FMP06_closure":
        METRICS
        / "fmp06_final_phase_closure.json",

    "FMP07_OP001":
        METRICS
        / "fmp07_op001_final_modeling_freeze_inventory.json",

    "FMP07_OP002":
        METRICS
        / "fmp07_op002_frozen_artifact_integrity_hash_manifest.json",

    "FMP07_OP003R1":
        METRICS
        / "fmp07_op003r1_frozen_artifact_closure_identity_reconciliation.json",

    "FMP07_OP004":
        METRICS
        / "fmp07_op004_frozen_runtime_reproducibility_manifest.json",
}


FROZEN_ARTIFACTS = {
    "T1":
        [
            MODEL / "T1/baselines/t1_it_support_char_svm.joblib"
        ],

    "T2":
        [
            MODEL / "T2/models/t2_class_weighted_tfidf_logreg.joblib"
        ],

    "T3":
        [
            MODEL / "T3/models/t3_class_weighted_tfidf_logreg.joblib"
        ],

    "T4":
        [
            MODEL / "T4/results/mod007_checkpoints/t4_mod007_tfidf.joblib",
            MODEL / "T4/results/mod007_checkpoints/t4_mod007_neighbors.joblib",
            MODEL / "T4/results/mod007_checkpoints/t4_mod007_full_retrieval.npz",
        ],

    "T5":
        [
            MODEL / "T5/metrics/t5_mod005_tfidf.joblib",
            MODEL / "T5/metrics/t5_mod005_logreg.joblib",
            MODEL / "T5/metrics/t5_mod007_calibrated_tfidf.joblib",
            MODEL / "T5/metrics/t5_mod007_calibration_models.joblib",
        ],

    "T6":
        [
            MODEL / "T6/metrics/t6_mod010_corrected_hybrid_results.json"
        ],

    "T7":
        [
            MODEL / "T7/metrics/t7_mod010_log_normal_aft_model.json"
        ],
}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():

    print("=" * 78)
    print(
        "FMP-07 OP-005 — FINAL FROZEN MODELING PACKAGE "
        "COMPLETENESS AUDIT"
    )
    print("=" * 78)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    # ------------------------------------------------------------
    # 1. Required evidence files
    # ------------------------------------------------------------

    print("\n[1] Checking required authoritative evidence files...")

    evidence_results = {}

    for name, path in REQUIRED_FILES.items():

        exists = path.exists()
        readable = False

        if exists:
            try:
                if path.suffix.lower() == ".json":
                    load_json(path)
                else:
                    with path.open("rb") as f:
                        f.read(1)

                readable = True

            except Exception:
                readable = False

        status = (
            "PASS"
            if exists and readable
            else "FAIL"
        )

        evidence_results[name] = {
            "path": str(path.resolve()),
            "exists": exists,
            "readable": readable,
            "status": status,
        }

        print(
            f"  {name}: {status}"
        )

    evidence_pass = all(
        item["status"] == "PASS"
        for item in evidence_results.values()
    )

    print(
        f"  Required evidence set: "
        f"{'PASS' if evidence_pass else 'FAIL'}"
    )

    # ------------------------------------------------------------
    # 2. Frozen artifact package
    # ------------------------------------------------------------

    print("\n[2] Checking frozen T1–T7 artifact package...")

    artifact_results = {}

    for task, paths in FROZEN_ARTIFACTS.items():

        task_items = []

        for path in paths:

            exists = path.exists()
            readable = False
            size_bytes = None

            if exists:
                try:
                    size_bytes = path.stat().st_size
                    with path.open("rb") as f:
                        f.read(1)
                    readable = True
                except Exception:
                    readable = False

            status = (
                "PASS"
                if exists and readable and size_bytes > 0
                else "FAIL"
            )

            task_items.append({
                "path": str(path.resolve()),
                "exists": exists,
                "readable": readable,
                "size_bytes": size_bytes,
                "status": status,
            })

        task_pass = all(
            item["status"] == "PASS"
            for item in task_items
        )

        artifact_results[task] = {
            "artifact_count": len(task_items),
            "artifacts": task_items,
            "status":
                "PASS" if task_pass else "FAIL",
        }

        print(
            f"  {task}: "
            f"{'PASS' if task_pass else 'FAIL'} "
            f"({len(task_items)} artifact(s))"
        )

    artifact_pass = all(
        item["status"] == "PASS"
        for item in artifact_results.values()
    )

    # ------------------------------------------------------------
    # 3. FMP-07 prerequisite chain
    # ------------------------------------------------------------

    print("\n[3] Checking FMP-07 freeze prerequisite chain...")

    prerequisite_names = [
        "FMP07_OP001",
        "FMP07_OP002",
        "FMP07_OP003R1",
        "FMP07_OP004",
    ]

    prerequisite_status = {}

    for name in prerequisite_names:

        data = load_json(
            REQUIRED_FILES[name]
        )

        status = data.get("status")

        prerequisite_status[name] = status

        print(
            f"  {name}: {status}"
        )

    prerequisite_pass = all(
        status == "PASS"
        for status in prerequisite_status.values()
    )

    print(
        f"  FMP-07 prerequisite chain: "
        f"{'PASS' if prerequisite_pass else 'FAIL'}"
    )

    # ------------------------------------------------------------
    # 4. Downstream T8–T10 closure boundary
    # ------------------------------------------------------------

    print("\n[4] Checking T8–T10 downstream closure boundary...")

    t8 = load_json(REQUIRED_FILES["T8_closure"])
    t9 = load_json(REQUIRED_FILES["T9_closure"])
    t10 = load_json(REQUIRED_FILES["T10_policy"])
    fmp06 = load_json(REQUIRED_FILES["FMP06_closure"])

    downstream = {
        "T8": {
            "status":
                t8.get("status"),
            "expected":
                "CLOSED_PASS",
        },

        "T9": {
            "status":
                t9.get("status"),
            "expected":
                "CLOSED_PASS",
        },

        "T10": {
            "status":
                t10.get("status"),
            "policy_boundary_preserved":
                True,
        },

        "FMP06": {
            "status":
                fmp06.get("status"),
            "expected":
                "CLOSED_PASS",
        },
    }

    print(
        f"  T8: {downstream['T8']['status']}"
    )
    print(
        f"  T9: {downstream['T9']['status']}"
    )
    print(
        f"  T10 policy evidence: {downstream['T10']['status']}"
    )
    print(
        f"  FMP-06: {downstream['FMP06']['status']}"
    )

    downstream_pass = (
        downstream["T8"]["status"] == "CLOSED_PASS"
        and downstream["T9"]["status"] == "CLOSED_PASS"
        and downstream["T10"]["status"] == "PASS"
        and downstream["FMP06"]["status"] == "CLOSED_PASS"
    )

    print(
        f"  Downstream closure boundary: "
        f"{'PASS' if downstream_pass else 'FAIL'}"
    )

    # ------------------------------------------------------------
    # 5. Final completeness
    # ------------------------------------------------------------

    print("\n[5] Final package completeness determination...")

    final_status = (
        "PASS"
        if (
            evidence_pass
            and artifact_pass
            and prerequisite_pass
            and downstream_pass
        )
        else "REQUIRES_REVIEW"
    )

    print(
        f"  Required evidence: "
        f"{'PASS' if evidence_pass else 'FAIL'}"
    )

    print(
        f"  Frozen artifacts: "
        f"{'PASS' if artifact_pass else 'FAIL'}"
    )

    print(
        f"  FMP-07 prerequisite chain: "
        f"{'PASS' if prerequisite_pass else 'FAIL'}"
    )

    print(
        f"  T8–T10/FMP-06 boundary: "
        f"{'PASS' if downstream_pass else 'FAIL'}"
    )

    print(
        f"  FINAL PACKAGE COMPLETENESS: {final_status}"
    )

    # ------------------------------------------------------------
    # 6. Write evidence
    # ------------------------------------------------------------

    result = {
        "operation":
            "FMP-07 OP-005",

        "operation_name":
            "FINAL_FROZEN_MODELING_PACKAGE_COMPLETENESS_AUDIT",

        "timestamp_utc":
            datetime.now(timezone.utc).isoformat(),

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

        "required_evidence":
            evidence_results,

        "frozen_artifacts":
            artifact_results,

        "fmp07_prerequisite_status":
            prerequisite_status,

        "downstream_closure":
            downstream,

        "interpretation": (
            "This operation verifies that the final frozen "
            "modeling package contains the required authoritative "
            "task closures, frozen T1–T7 artifacts, integrity "
            "evidence, reproducibility evidence, FMP-06 closure, "
            "and T8–T10 downstream evidence. It does not perform "
            "model training, fitting, prediction, evaluation, "
            "selection, optimization, or artifact modification."
        ),
    }

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("\n" + "=" * 78)
    print("OP-005 COMPLETE")
    print("=" * 78)
    print(f"STATUS: {final_status}")
    print(f"Output: {OUTPUT}")
    print("No training performed.")
    print("No fitting performed.")
    print("No prediction performed.")
    print("No evaluation performed.")
    print("No locked test used.")
    print("No artifact modification performed.")


if __name__ == "__main__":
    main()