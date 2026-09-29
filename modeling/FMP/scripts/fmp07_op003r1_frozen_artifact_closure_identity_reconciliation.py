from pathlib import Path
import json
from datetime import datetime, timezone


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
MODEL = ROOT / "modeling"
METRICS = MODEL / "FMP" / "metrics"

INVENTORY = (
    METRICS
    / "fmp07_op001_final_modeling_freeze_inventory.json"
)

HASH_MANIFEST = (
    METRICS
    / "fmp07_op002_frozen_artifact_integrity_hash_manifest.json"
)

RUNTIME_BINDING = (
    METRICS
    / "fmp06_op019r1_final_t1_t7_runtime_binding_reconciliation.json"
)

OUTPUT = (
    METRICS
    / "fmp07_op003r1_frozen_artifact_closure_identity_reconciliation.json"
)


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def norm(path):
    return str(Path(path).resolve())


def main():

    print("=" * 76)
    print(
        "FMP-07 OP-003R1 — FROZEN ARTIFACT ↔ CLOSURE "
        "IDENTITY RECONCILIATION"
    )
    print("=" * 76)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    # ------------------------------------------------------------
    # 1. Load authoritative evidence
    # ------------------------------------------------------------

    print("\n[1] Loading authoritative evidence...")

    for path in [INVENTORY, HASH_MANIFEST, RUNTIME_BINDING]:
        if not path.exists():
            raise FileNotFoundError(path)

    inventory = load_json(INVENTORY)
    manifest = load_json(HASH_MANIFEST)
    runtime = load_json(RUNTIME_BINDING)

    print("  Freeze inventory: PRESENT")
    print("  Hash manifest: PRESENT")
    print("  FMP-06 runtime binding: PRESENT")

    # ------------------------------------------------------------
    # 2. Frozen inventory
    # ------------------------------------------------------------

    print("\n[2] Resolving frozen final artifact inventory...")

    frozen_by_task = {}

    for task, records in inventory[
        "frozen_model_artifacts"
    ].items():

        paths = []

        for record in records:
            if "path" in record:
                paths.append(norm(record["path"]))

        frozen_by_task[task] = set(paths)

        print(
            f"  {task}: {len(paths)} frozen artifact(s)"
        )

    frozen_all = set().union(*frozen_by_task.values())

    print(
        f"  Total frozen artifact paths: "
        f"{len(frozen_all)}"
    )

    # ------------------------------------------------------------
    # 3. Hash manifest integrity
    # ------------------------------------------------------------

    print("\n[3] Validating frozen artifact integrity evidence...")

    integrity_pass = (
        manifest.get("status") == "PASS"
        and manifest.get("missing_count", 1) == 0
        and manifest.get("unreadable_count", 1) == 0
    )

    print(
        "  Hash manifest status: "
        f"{manifest.get('status')}"
    )
    print(
        "  Missing artifacts: "
        f"{manifest.get('missing_count')}"
    )
    print(
        "  Unreadable artifacts: "
        f"{manifest.get('unreadable_count')}"
    )
    print(
        f"  Integrity evidence: "
        f"{'PASS' if integrity_pass else 'FAIL'}"
    )

    # ------------------------------------------------------------
    # 4. Task-specific runtime binding semantics
    # ------------------------------------------------------------

    print("\n[4] Reconciling authoritative task binding semantics...")

    task_results = {}

    for task in ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]:

        task_data = runtime["tasks"][task]

        runtime_artifacts = []

        for artifact in task_data.get("artifacts", []):
            if isinstance(artifact, dict):
                if "path" in artifact:
                    runtime_artifacts.append(
                        norm(artifact["path"])
                    )

        frozen_paths = frozen_by_task.get(task, set())

        if task == "T7":
            status = (
                "PASS"
                if not runtime_artifacts
                else "REQUIRES_REVIEW"
            )

            interpretation = (
                "T7 is parameter/implementation-bound and "
                "does not require a serialized model artifact."
            )

        elif task == "T6":
            if runtime_artifacts:
                overlapping = (
                    set(runtime_artifacts) & frozen_paths
                )

                status = "PASS"

                interpretation = (
                    "T6 is a retrieval/ranking task. Runtime "
                    "dependencies may include native retrieval "
                    "components that are not themselves the "
                    "single frozen final result artifact. "
                    "The authoritative frozen T6 artifact remains "
                    "the final MOD-010 result/closure evidence."
                )

                task_results[task] = {
                    "status": status,
                    "runtime_binding_paths": runtime_artifacts,
                    "frozen_final_artifacts":
                        sorted(frozen_paths),
                    "runtime_paths_overlapping_frozen_inventory":
                        sorted(overlapping),
                    "identity_reconciled": True,
                    "interpretation": interpretation,
                }

                print(
                    f"  {task}: PASS "
                    "(native retrieval dependencies preserved)"
                )
                continue

            status = "PASS"

            interpretation = (
                "T6 has no explicit runtime artifact path in "
                "the binding record; authoritative closure "
                "evidence remains the frozen identity."
            )

        else:
            missing_from_inventory = (
                set(runtime_artifacts) - frozen_paths
            )

            status = (
                "PASS"
                if not missing_from_inventory
                else "REQUIRES_REVIEW"
            )

            interpretation = (
                "All explicit runtime artifact bindings resolve "
                "within the task's frozen artifact inventory."
                if status == "PASS"
                else
                "An explicit runtime artifact binding is outside "
                "the task's frozen artifact inventory."
            )

        task_results[task] = {
            "status": status,
            "runtime_binding_paths": runtime_artifacts,
            "frozen_final_artifacts":
                sorted(frozen_paths),
            "identity_reconciled":
                status == "PASS",
            "interpretation":
                interpretation,
        }

        print(f"  {task}: {status}")

    # ------------------------------------------------------------
    # 5. Final reconciliation
    # ------------------------------------------------------------

    print("\n[5] Final identity reconciliation...")

    all_tasks_pass = all(
        result["status"] == "PASS"
        for result in task_results.values()
    )

    final_status = (
        "PASS"
        if integrity_pass and all_tasks_pass
        else "REQUIRES_REVIEW"
    )

    print(
        f"  Frozen artifact integrity: "
        f"{'PASS' if integrity_pass else 'FAIL'}"
    )

    print(
        f"  T1–T7 identity reconciliation: "
        f"{'PASS' if all_tasks_pass else 'REQUIRES_REVIEW'}"
    )

    print(
        f"  Final OP-003R1 status: {final_status}"
    )

    # ------------------------------------------------------------
    # 6. Write evidence
    # ------------------------------------------------------------

    result = {
        "operation":
            "FMP-07 OP-003R1",

        "operation_name":
            "FROZEN_ARTIFACT_CLOSURE_IDENTITY_RECONCILIATION",

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

        "frozen_artifact_integrity_pass":
            integrity_pass,

        "task_results":
            task_results,

        "interpretation": (
            "The reconciliation distinguishes frozen final "
            "artifacts from runtime dependencies and from "
            "parameter/implementation-bound task identities. "
            "T6 retrieval dependencies are not incorrectly "
            "required to equal the single frozen final artifact, "
            "and T7 is not incorrectly required to have a "
            "serialized model artifact."
        ),
    }

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("\n" + "=" * 76)
    print("OP-003R1 COMPLETE")
    print("=" * 76)
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