from pathlib import Path
import json
from datetime import datetime, timezone


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
MODEL = ROOT / "modeling"
METRICS = MODEL / "FMP" / "metrics"


INPUTS = {
    "freeze_inventory": (
        METRICS
        / "fmp07_op001_final_modeling_freeze_inventory.json"
    ),
    "hash_manifest": (
        METRICS
        / "fmp07_op002_frozen_artifact_integrity_hash_manifest.json"
    ),
    "runtime_binding": (
        METRICS
        / "fmp06_op019r1_final_t1_t7_runtime_binding_reconciliation.json"
    ),
}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize(path):
    return str(Path(path).resolve())


def main():
    print("=" * 72)
    print("FMP-07 OP-003 — FROZEN ARTIFACT ↔ CLOSURE IDENTITY RECONCILIATION")
    print("=" * 72)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    print("\n[1] Loading authoritative inputs...")

    data = {}

    for name, path in INPUTS.items():
        if not path.exists():
            raise FileNotFoundError(path)

        data[name] = load_json(path)
        print(f"  {name}: PRESENT")

    print("\n[2] Checking freeze inventory against hash manifest...")

    inventory = data["freeze_inventory"]
    manifest = data["hash_manifest"]

    inventory_artifacts = {
        normalize(record["path"])
        for task_records in inventory["frozen_model_artifacts"].values()
        for record in task_records
    }

    manifest_artifacts = {
        normalize(record["path"])
        for task_records in manifest["artifacts"].values()
        for record in task_records
    }

    inventory_manifest_match = (
        inventory_artifacts == manifest_artifacts
    )

    print(
        f"  Inventory artifact count: "
        f"{len(inventory_artifacts)}"
    )
    print(
        f"  Hash manifest artifact count: "
        f"{len(manifest_artifacts)}"
    )
    print(
        f"  Inventory ↔ hash manifest: "
        f"{'PASS' if inventory_manifest_match else 'FAIL'}"
    )

    print("\n[3] Checking authoritative T1–T7 runtime bindings...")

    runtime = data["runtime_binding"]

    runtime_bindings = {}

    for task in ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]:
        task_data = runtime["tasks"][task]

        artifact_paths = []

        for artifact in task_data.get("artifacts", []):
            if "path" in artifact:
                artifact_paths.append(
                    normalize(artifact["path"])
                )

        runtime_bindings[task] = artifact_paths

        print(
            f"  {task}: "
            f"{len(artifact_paths)} artifact binding path(s)"
        )

    print("\n[4] Comparing runtime bindings with frozen artifact inventory...")

    binding_results = {}

    for task, paths in runtime_bindings.items():
        frozen_task_paths = {
            normalize(record["path"])
            for record in inventory["frozen_model_artifacts"].get(
                task, []
            )
        }

        if paths:
            matched = set(paths).issubset(frozen_task_paths)
            binding_results[task] = {
                "runtime_binding_paths": paths,
                "frozen_paths": sorted(frozen_task_paths),
                "binding_resolved_within_frozen_inventory": matched,
            }

            print(
                f"  {task}: "
                f"{'PASS' if matched else 'REQUIRES_REVIEW'}"
            )
        else:
            binding_results[task] = {
                "runtime_binding_paths": [],
                "frozen_paths": sorted(frozen_task_paths),
                "binding_resolved_within_frozen_inventory":
                    "NOT_EXPRESSED_AS_EXPLICIT_ARTIFACT_PATH",
            }

            print(
                f"  {task}: "
                f"NO_EXPLICIT_ARTIFACT_PATH_IN_BINDING_RECORD"
            )

    print("\n[5] Checking frozen artifact existence/readability...")

    artifact_integrity_pass = (
        manifest["status"] == "PASS"
        and manifest["missing_count"] == 0
        and manifest["unreadable_count"] == 0
    )

    print(
        f"  Hash manifest integrity: "
        f"{'PASS' if artifact_integrity_pass else 'FAIL'}"
    )

    print("\n[6] Final identity reconciliation...")

    explicit_binding_tasks = [
        task
        for task, result in binding_results.items()
        if result["binding_resolved_within_frozen_inventory"] is not
        "NOT_EXPRESSED_AS_EXPLICIT_ARTIFACT_PATH"
    ]

    explicit_binding_pass = all(
        binding_results[task]["binding_resolved_within_frozen_inventory"]
        is True
        for task in explicit_binding_tasks
    )

    final_pass = (
        inventory_manifest_match
        and artifact_integrity_pass
        and explicit_binding_pass
    )

    status = "PASS" if final_pass else "REQUIRES_REVIEW"

    print(
        f"  Inventory ↔ hash manifest: "
        f"{'PASS' if inventory_manifest_match else 'FAIL'}"
    )

    print(
        f"  Frozen artifact integrity: "
        f"{'PASS' if artifact_integrity_pass else 'FAIL'}"
    )

    print(
        f"  Explicit runtime bindings: "
        f"{'PASS' if explicit_binding_pass else 'FAIL'}"
    )

    print(f"  Final identity reconciliation: {status}")

    output = (
        METRICS
        / "fmp07_op003_frozen_artifact_closure_identity_reconciliation.json"
    )

    result = {
        "operation": "FMP-07 OP-003",
        "operation_name":
            "FROZEN_ARTIFACT_CLOSURE_IDENTITY_RECONCILIATION",
        "timestamp_utc":
            datetime.now(timezone.utc).isoformat(),
        "status": status,
        "read_only": True,
        "training_performed": False,
        "fitting_performed": False,
        "prediction_performed": False,
        "evaluation_performed": False,
        "locked_test_used": False,
        "artifact_modified": False,
        "inventory_manifest_match":
            inventory_manifest_match,
        "artifact_integrity_pass":
            artifact_integrity_pass,
        "runtime_binding_results":
            binding_results,
        "explicit_binding_tasks":
            explicit_binding_tasks,
        "explicit_binding_pass":
            explicit_binding_pass,
        "interpretation": (
            "The operation reconciles the final frozen artifact "
            "inventory, SHA-256 manifest, and authoritative runtime "
            "binding evidence without executing or modifying any "
            "model artifact."
        ),
    }

    with output.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("\n" + "=" * 72)
    print("OP-003 IDENTITY RECONCILIATION COMPLETE")
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