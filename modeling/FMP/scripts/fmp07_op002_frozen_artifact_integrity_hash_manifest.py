from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
MODEL = ROOT / "modeling"
METRICS = MODEL / "FMP" / "metrics"


FROZEN_ARTIFACTS = {
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
        MODEL / "T5" / "models"
        / "t5_mod005_tfidf.joblib",

        MODEL / "T5" / "models"
        / "t5_mod005_logreg.joblib",

        MODEL / "T5" / "models"
        / "t5_mod007_calibrated_tfidf.joblib",

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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def inspect_file(path: Path):
    if not path.exists():
        return {
            "exists": False,
            "readable": False,
            "size_bytes": None,
            "sha256": None,
            "modified_utc": None,
        }

    try:
        stat = path.stat()

        return {
            "exists": True,
            "readable": True,
            "size_bytes": stat.st_size,
            "sha256": sha256_file(path),
            "modified_utc": datetime.fromtimestamp(
                stat.st_mtime,
                tz=timezone.utc,
            ).isoformat(),
        }

    except (OSError, PermissionError):
        return {
            "exists": True,
            "readable": False,
            "size_bytes": None,
            "sha256": None,
            "modified_utc": None,
        }


def main():
    print("=" * 72)
    print("FMP-07 OP-002 — FROZEN ARTIFACT INTEGRITY & HASH MANIFEST")
    print("=" * 72)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    print("\n[1] Computing SHA-256 integrity manifest...")

    manifest = {}
    missing = []
    unreadable = []
    total_artifacts = 0

    for task, paths in FROZEN_ARTIFACTS.items():
        print(f"\n  {task}")

        manifest[task] = []

        for path in paths:
            total_artifacts += 1

            info = inspect_file(path)

            record = {
                "path": str(path),
                "filename": path.name,
                **info,
            }

            manifest[task].append(record)

            if not info["exists"]:
                state = "MISSING"
                missing.append(str(path))

            elif not info["readable"]:
                state = "UNREADABLE"
                unreadable.append(str(path))

            else:
                state = "PASS"

            print(f"    {path.name}: {state}")

            if info["exists"] and info["readable"]:
                print(f"      size_bytes: {info['size_bytes']}")
                print(f"      sha256: {info['sha256']}")

    print("\n[2] Integrity summary...")

    present_count = sum(
        1
        for records in manifest.values()
        for record in records
        if record["exists"] and record["readable"]
    )

    print(f"  Total frozen artifacts: {total_artifacts}")
    print(f"  Present/readable: {present_count}")
    print(f"  Missing: {len(missing)}")
    print(f"  Unreadable: {len(unreadable)}")

    final_status = (
        "PASS"
        if (
            present_count == total_artifacts
            and not missing
            and not unreadable
        )
        else "REQUIRES_REVIEW"
    )

    print(f"  Integrity manifest status: {final_status}")

    print("\n[3] Freeze interpretation...")

    interpretation = (
        "All inventoried T1–T7 frozen artifacts are present and "
        "readable. SHA-256 hashes have been recorded as the "
        "integrity reference for subsequent freeze/package "
        "operations."
        if final_status == "PASS"
        else
        "One or more frozen artifacts are missing or unreadable. "
        "Final freeze/package integrity cannot yet be established."
    )

    print(f"  {interpretation}")

    output = (
        METRICS
        / "fmp07_op002_frozen_artifact_integrity_hash_manifest.json"
    )

    result = {
        "operation": "FMP-07 OP-002",
        "operation_name":
            "FROZEN_ARTIFACT_INTEGRITY_HASH_MANIFEST",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": final_status,
        "read_only": True,
        "training_performed": False,
        "fitting_performed": False,
        "prediction_performed": False,
        "evaluation_performed": False,
        "locked_test_used": False,
        "artifact_modified": False,
        "total_frozen_artifacts": total_artifacts,
        "present_readable": present_count,
        "missing_count": len(missing),
        "unreadable_count": len(unreadable),
        "missing_artifacts": missing,
        "unreadable_artifacts": unreadable,
        "artifacts": manifest,
        "interpretation": interpretation,
    }

    with output.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("\n" + "=" * 72)
    print("OP-002 INTEGRITY MANIFEST COMPLETE")
    print("=" * 72)
    print(f"STATUS: {final_status}")
    print(f"Output: {output}")
    print("No training performed.")
    print("No fitting performed.")
    print("No prediction performed.")
    print("No evaluation performed.")
    print("No locked test used.")
    print("No artifact modification performed.")


if __name__ == "__main__":
    main()