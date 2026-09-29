from pathlib import Path
import json
from datetime import datetime, timezone


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
MODEL = ROOT / "modeling"
METRICS = MODEL / "FMP" / "metrics"


INPUTS = {
    "op001":
        METRICS / "fmp07_op001_final_modeling_freeze_inventory.json",

    "op002":
        METRICS / "fmp07_op002_frozen_artifact_integrity_hash_manifest.json",

    "op003r1":
        METRICS /
        "fmp07_op003r1_frozen_artifact_closure_identity_reconciliation.json",

    "op004":
        METRICS /
        "fmp07_op004_frozen_runtime_reproducibility_manifest.json",

    "fmp06":
        METRICS / "fmp06_final_phase_closure.json",

    "t8":
        MODEL /
        "T8/mod036/op026/"
        "t8_mod036_op026_decision_engine_validation.json",

    "t9":
        MODEL /
        "T9/mod037/"
        "t9_mod037_op015_final_integrated_closure.json",

    "t10":
        METRICS /
        "fmp05_op008_empirical_policy_boundary_audit.json",
}


OUTPUT = (
    METRICS /
    "fmp07_op005r1_final_frozen_modeling_package_completeness_audit.json"
)


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize(path):
    return str(Path(path).resolve())


def check_file(path):
    if not path.exists():
        return {
            "exists": False,
            "readable": False,
            "size_bytes": None,
        }

    try:
        size = path.stat().st_size

        with path.open("rb") as f:
            f.read(1)

        return {
            "exists": True,
            "readable": True,
            "size_bytes": size,
        }

    except Exception:
        return {
            "exists": True,
            "readable": False,
            "size_bytes": None,
        }


def main():

    print("=" * 78)
    print(
        "FMP-07 OP-005R1 — FINAL FROZEN MODELING PACKAGE "
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
    # 1. Load authoritative evidence
    # ------------------------------------------------------------

    print("\n[1] Loading authoritative freeze evidence...")

    for name, path in INPUTS.items():

        if not path.exists():
            raise FileNotFoundError(
                f"Missing authoritative input: {path}"
            )

        print(f"  {name}: PRESENT")

    data = {
        name: load_json(path)
        for name, path in INPUTS.items()
    }

    # ------------------------------------------------------------
    # 2. Validate FMP-07 prerequisite chain
    # ------------------------------------------------------------

    print("\n[2] Validating FMP-07 prerequisite chain...")

    prerequisite_status = {
        "OP-001":
            data["op001"].get("status"),

        "OP-002":
            data["op002"].get("status"),

        "OP-003R1":
            data["op003r1"].get("status"),

        "OP-004":
            data["op004"].get("status"),
    }

    for name, status in prerequisite_status.items():
        print(f"  {name}: {status}")

    prerequisite_pass = all(
        status == "PASS"
        for status in prerequisite_status.values()
    )

    print(
        f"  FMP-07 prerequisites: "
        f"{'PASS' if prerequisite_pass else 'FAIL'}"
    )

    # ------------------------------------------------------------
    # 3. Use OP-002 as authoritative frozen artifact manifest
    # ------------------------------------------------------------

    print(
        "\n[3] Rechecking frozen artifacts from the "
        "authoritative OP-002 manifest..."
    )

    manifest = data["op002"]

    manifest_artifacts = manifest.get("artifacts", {})

    artifact_results = {}
    total_artifacts = 0
    failed_artifacts = 0

    for task, records in manifest_artifacts.items():

        task_results = []

        for record in records:

            path = Path(record["path"])

            check = check_file(path)

            expected_sha256 = record.get("sha256")
            recorded_size = record.get("size_bytes")

            task_pass = (
                check["exists"]
                and check["readable"]
                and check["size_bytes"] == recorded_size
            )

            task_results.append({
                "path": normalize(path),
                "exists": check["exists"],
                "readable": check["readable"],
                "current_size_bytes": check["size_bytes"],
                "manifest_size_bytes": recorded_size,
                "sha256_from_manifest":
                    expected_sha256,
                "status":
                    "PASS" if task_pass else "FAIL",
            })

            total_artifacts += 1

            if not task_pass:
                failed_artifacts += 1

        task_pass = all(
            item["status"] == "PASS"
            for item in task_results
        )

        artifact_results[task] = {
            "artifact_count":
                len(task_results),
            "artifacts":
                task_results,
            "status":
                "PASS" if task_pass else "FAIL",
        }

        print(
            f"  {task}: "
            f"{'PASS' if task_pass else 'FAIL'} "
            f"({len(task_results)} artifact(s))"
        )

    artifact_pass = (
        failed_artifacts == 0
        and total_artifacts == 12
        and manifest.get("status") == "PASS"
        and manifest.get("missing_count", 1) == 0
        and manifest.get("unreadable_count", 1) == 0
    )

    print(
        f"  Frozen artifact package: "
        f"{'PASS' if artifact_pass else 'FAIL'}"
    )

    # ------------------------------------------------------------
    # 4. Required closure/evidence files
    # ------------------------------------------------------------

    print("\n[4] Checking required closure/evidence files...")

    evidence_results = {}

    for name, path in INPUTS.items():

        check = check_file(path)

        evidence_results[name] = {
            "path": normalize(path),
            **check,
            "status":
                "PASS"
                if check["exists"] and check["readable"]
                else "FAIL",
        }

        print(
            f"  {name}: "
            f"{evidence_results[name]['status']}"
        )

    evidence_pass = all(
        item["status"] == "PASS"
        for item in evidence_results.values()
    )

    print(
        f"  Required evidence files: "
        f"{'PASS' if evidence_pass else 'FAIL'}"
    )

    # ------------------------------------------------------------
    # 5. T8/T9/T10/FMP-06 actual authoritative statuses
    # ------------------------------------------------------------

    print("\n[5] Reconciling downstream authoritative statuses...")

    t8_status = data["t8"].get("status")
    t9_status = data["t9"].get("status")
    t10_status = data["t10"].get("status")
    fmp06_status = data["fmp06"].get("status")

    print(f"  T8: {t8_status}")
    print(f"  T9: {t9_status}")
    print(f"  T10 policy evidence: {t10_status}")
    print(f"  FMP-06: {fmp06_status}")

    t8_pass = t8_status in {
        "PASS",
        "CLOSED_PASS",
    }

    t9_pass = t9_status in {
        "PASS",
        "CLOSED_PASS",
    }

    t10_pass = t10_status == "PASS"

    fmp06_pass = fmp06_status == "CLOSED_PASS"

    downstream_pass = (
        t8_pass
        and t9_pass
        and t10_pass
        and fmp06_pass
    )

    print(
        f"  T8/T9/T10/FMP-06 boundary: "
        f"{'PASS' if downstream_pass else 'FAIL'}"
    )

    # ------------------------------------------------------------
    # 6. Final completeness
    # ------------------------------------------------------------

    print("\n[6] Final package completeness determination...")

    final_status = (
        "PASS"
        if (
            prerequisite_pass
            and artifact_pass
            and evidence_pass
            and downstream_pass
        )
        else "REQUIRES_REVIEW"
    )

    print(
        f"  FMP-07 prerequisites: "
        f"{'PASS' if prerequisite_pass else 'FAIL'}"
    )

    print(
        f"  Frozen artifacts: "
        f"{'PASS' if artifact_pass else 'FAIL'}"
    )

    print(
        f"  Required evidence: "
        f"{'PASS' if evidence_pass else 'FAIL'}"
    )

    print(
        f"  Downstream closure boundary: "
        f"{'PASS' if downstream_pass else 'FAIL'}"
    )

    print(
        f"  FINAL PACKAGE COMPLETENESS: {final_status}"
    )

    # ------------------------------------------------------------
    # 7. Write corrected evidence
    # ------------------------------------------------------------

    result = {
        "operation":
            "FMP-07 OP-005R1",

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

        "correction_basis": [
            "OP-002 is the authoritative frozen artifact manifest.",
            "T6 runtime dependencies are not required to equal "
            "the single frozen final-result artifact.",
            "T7 is parameter/implementation-bound.",
            "T8 and T9 accept their authoritative PASS closure status.",
            "FMP-06 CLOSED_PASS is retained as the final phase status."
        ],

        "prerequisite_status":
            prerequisite_status,

        "frozen_artifacts":
            artifact_results,

        "required_evidence":
            evidence_results,

        "downstream_status": {
            "T8": t8_status,
            "T9": t9_status,
            "T10": t10_status,
            "FMP06": fmp06_status,
        },

        "interpretation": (
            "This corrected audit reconciles package completeness "
            "against the authoritative freeze manifest and actual "
            "closure status values. It does not introduce new "
            "modeling evidence or modify any frozen artifact."
        ),
    }

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("\n" + "=" * 78)
    print("OP-005R1 COMPLETE")
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