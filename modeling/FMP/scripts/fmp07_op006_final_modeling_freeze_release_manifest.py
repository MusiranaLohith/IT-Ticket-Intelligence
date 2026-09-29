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

    "op005r1":
        METRICS /
        "fmp07_op005r1_final_frozen_modeling_package_completeness_audit.json",

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
    "fmp07_op006_final_modeling_freeze_release_manifest.json"
)


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize(path):
    return str(Path(path).resolve())


def main():

    print("=" * 80)
    print(
        "FMP-07 OP-006 — FINAL MODELING FREEZE / RELEASE MANIFEST"
    )
    print("=" * 80)

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
    # 2. Validate FMP-07 chain
    # ------------------------------------------------------------

    print("\n[2] Validating FMP-07 freeze chain...")

    chain_status = {
        "OP-001":
            data["op001"].get("status"),

        "OP-002":
            data["op002"].get("status"),

        "OP-003R1":
            data["op003r1"].get("status"),

        "OP-004":
            data["op004"].get("status"),

        "OP-005R1":
            data["op005r1"].get("status"),
    }

    for name, status in chain_status.items():
        print(f"  {name}: {status}")

    chain_pass = all(
        status == "PASS"
        for status in chain_status.values()
    )

    print(
        f"  FMP-07 freeze chain: "
        f"{'PASS' if chain_pass else 'FAIL'}"
    )

    # ------------------------------------------------------------
    # 3. Extract authoritative frozen artifact hashes
    # ------------------------------------------------------------

    print("\n[3] Recording frozen artifact identities and hashes...")

    manifest = data["op002"]

    frozen_artifacts = {}

    total_artifacts = 0

    for task, records in manifest["artifacts"].items():

        frozen_artifacts[task] = []

        for record in records:

            path = Path(record["path"])

            frozen_artifacts[task].append({
                "path":
                    normalize(path),

                "size_bytes":
                    record.get("size_bytes"),

                "sha256":
                    record.get("sha256"),
            })

            total_artifacts += 1

        print(
            f"  {task}: "
            f"{len(frozen_artifacts[task])} artifact(s)"
        )

    print(
        f"  Total frozen artifacts: {total_artifacts}"
    )

    hash_manifest_pass = (
        manifest.get("status") == "PASS"
        and manifest.get("missing_count", 1) == 0
        and manifest.get("unreadable_count", 1) == 0
        and total_artifacts == 12
    )

    print(
        f"  Frozen hash manifest: "
        f"{'PASS' if hash_manifest_pass else 'FAIL'}"
    )

    # ------------------------------------------------------------
    # 4. Validate final package completeness
    # ------------------------------------------------------------

    print("\n[4] Validating final package completeness...")

    package_status = data["op005r1"].get("status")

    print(
        f"  OP-005R1 package completeness: "
        f"{package_status}"
    )

    package_pass = package_status == "PASS"

    # ------------------------------------------------------------
    # 5. Validate runtime reproducibility boundary
    # ------------------------------------------------------------

    print("\n[5] Validating runtime reproducibility boundary...")

    reproducibility_status = data["op004"].get("status")

    print(
        f"  OP-004 reproducibility manifest: "
        f"{reproducibility_status}"
    )

    reproducibility_pass = (
        reproducibility_status == "PASS"
    )

    # ------------------------------------------------------------
    # 6. Validate FMP-06 E2E closure
    # ------------------------------------------------------------

    print("\n[6] Validating FMP-06 E2E closure...")

    fmp06_status = data["fmp06"].get("status")

    print(
        f"  FMP-06: {fmp06_status}"
    )

    fmp06_pass = (
        fmp06_status == "CLOSED_PASS"
    )

    # ------------------------------------------------------------
    # 7. Validate T8/T9/T10 downstream boundary
    # ------------------------------------------------------------

    print("\n[7] Validating T8–T10 downstream boundary...")

    t8_status = data["t8"].get("status")
    t9_status = data["t9"].get("status")
    t10_status = data["t10"].get("status")

    print(f"  T8: {t8_status}")
    print(f"  T9: {t9_status}")
    print(f"  T10: {t10_status}")

    t8_pass = t8_status in {
        "PASS",
        "CLOSED_PASS",
    }

    t9_pass = t9_status in {
        "PASS",
        "CLOSED_PASS",
    }

    t10_pass = t10_status == "PASS"

    downstream_pass = (
        t8_pass
        and t9_pass
        and t10_pass
    )

    print(
        f"  T8–T10 boundary: "
        f"{'PASS' if downstream_pass else 'FAIL'}"
    )

    # ------------------------------------------------------------
    # 8. Record explicit freeze controls
    # ------------------------------------------------------------

    print("\n[8] Recording final freeze controls...")

    freeze_controls = {
        "model_retraining_authorized":
            False,

        "model_refitting_authorized":
            False,

        "new_model_selection_authorized":
            False,

        "threshold_reoptimization_authorized":
            False,

        "universal_confidence_creation_authorized":
            False,

        "universal_risk_creation_authorized":
            False,

        "synthetic_fusion_target_creation_authorized":
            False,

        "frozen_artifact_modification_authorized":
            False,

        "locked_test_reuse_for_selection_authorized":
            False,
    }

    for key, value in freeze_controls.items():
        print(
            f"  {key}: {value}"
        )

    # ------------------------------------------------------------
    # 9. Final freeze determination
    # ------------------------------------------------------------

    print("\n[9] Final modeling freeze determination...")

    final_freeze_pass = all([
        chain_pass,
        hash_manifest_pass,
        package_pass,
        reproducibility_pass,
        fmp06_pass,
        downstream_pass,
    ])

    final_status = (
        "FROZEN_PASS"
        if final_freeze_pass
        else "REQUIRES_REVIEW"
    )

    print(
        f"  FMP-07 freeze chain: "
        f"{'PASS' if chain_pass else 'FAIL'}"
    )

    print(
        f"  Artifact hash manifest: "
        f"{'PASS' if hash_manifest_pass else 'FAIL'}"
    )

    print(
        f"  Package completeness: "
        f"{'PASS' if package_pass else 'FAIL'}"
    )

    print(
        f"  Runtime reproducibility: "
        f"{'PASS' if reproducibility_pass else 'FAIL'}"
    )

    print(
        f"  FMP-06 E2E closure: "
        f"{'PASS' if fmp06_pass else 'FAIL'}"
    )

    print(
        f"  T8–T10 boundary: "
        f"{'PASS' if downstream_pass else 'FAIL'}"
    )

    print(
        f"  FINAL MODELING FREEZE: {final_status}"
    )

    # ------------------------------------------------------------
    # 10. Write final release manifest
    # ------------------------------------------------------------

    result = {
        "operation":
            "FMP-07 OP-006",

        "operation_name":
            "FINAL_MODELING_FREEZE_RELEASE_MANIFEST",

        "timestamp_utc":
            datetime.now(timezone.utc).isoformat(),

        "status":
            final_status,

        "release_state":
            (
                "FROZEN"
                if final_freeze_pass
                else "NOT_FROZEN"
            ),

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

        "fmp07_chain":
            chain_status,

        "frozen_artifacts":
            frozen_artifacts,

        "total_frozen_artifacts":
            total_artifacts,

        "hash_manifest_status":
            manifest.get("status"),

        "package_completeness_status":
            package_status,

        "runtime_reproducibility_status":
            reproducibility_status,

        "fmp06_status":
            fmp06_status,

        "downstream_status": {
            "T8": t8_status,
            "T9": t9_status,
            "T10": t10_status,
        },

        "freeze_controls":
            freeze_controls,

        "interpretation": (
            "This manifest establishes the final frozen "
            "modeling-package release state using only "
            "previously established authoritative evidence. "
            "The operation does not train, refit, select, "
            "optimize, evaluate, or modify any model artifact."
        ),
    }

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("\n" + "=" * 80)
    print("OP-006 COMPLETE")
    print("=" * 80)
    print(f"STATUS: {final_status}")
    print(f"Release state: {result['release_state']}")
    print(f"Output: {OUTPUT}")
    print("No training performed.")
    print("No fitting performed.")
    print("No prediction performed.")
    print("No evaluation performed.")
    print("No locked test used.")
    print("No artifact modification performed.")


if __name__ == "__main__":
    main()