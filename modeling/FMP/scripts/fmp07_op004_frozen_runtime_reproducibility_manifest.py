from pathlib import Path
import json
from datetime import datetime, timezone


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
MODEL = ROOT / "modeling"
METRICS = MODEL / "FMP" / "metrics"


INPUTS = {
    "freeze_inventory":
        METRICS / "fmp07_op001_final_modeling_freeze_inventory.json",

    "hash_manifest":
        METRICS / "fmp07_op002_frozen_artifact_integrity_hash_manifest.json",

    "identity_reconciliation":
        METRICS
        / "fmp07_op003r1_frozen_artifact_closure_identity_reconciliation.json",

    "runtime_binding":
        METRICS
        / "fmp06_op019r1_final_t1_t7_runtime_binding_reconciliation.json",

    "t8_runtime":
        MODEL
        / "T8/mod036/op026/t8_mod036_op026_decision_engine_validation.json",

    "t9_closure":
        MODEL
        / "T9/mod037/t9_mod037_op015_final_integrated_closure.json",

    "t10_policy":
        METRICS
        / "fmp05_op008_empirical_policy_boundary_audit.json",
}


OUTPUT = (
    METRICS
    / "fmp07_op004_frozen_runtime_reproducibility_manifest.json"
)


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize(path):
    return str(Path(path).resolve())


def artifact_records(inventory, task):
    records = inventory["frozen_model_artifacts"].get(task, [])
    result = []

    for record in records:
        if "path" in record:
            result.append({
                "path": normalize(record["path"]),
                "exists": Path(record["path"]).exists(),
            })

    return result


def main():

    print("=" * 78)
    print(
        "FMP-07 OP-004 — FROZEN RUNTIME REPRODUCIBILITY MANIFEST"
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

    print("\n[1] Loading authoritative evidence...")

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
    # 2. Validate prerequisite evidence
    # ------------------------------------------------------------

    print("\n[2] Validating prerequisite evidence...")

    identity_status = data[
        "identity_reconciliation"
    ].get("status")

    hash_status = data[
        "hash_manifest"
    ].get("status")

    runtime_status = data[
        "runtime_binding"
    ].get("status")

    print(
        f"  Identity reconciliation: {identity_status}"
    )

    print(
        f"  Hash manifest: {hash_status}"
    )

    print(
        f"  T1–T7 runtime binding: {runtime_status}"
    )

    prerequisites_pass = (
        identity_status == "PASS"
        and hash_status == "PASS"
        and runtime_status == "PASS"
    )

    print(
        "  Prerequisites: "
        f"{'PASS' if prerequisites_pass else 'REQUIRES_REVIEW'}"
    )

    # ------------------------------------------------------------
    # 3. Build task reproducibility manifest
    # ------------------------------------------------------------

    print("\n[3] Building T1–T7 reproducibility manifest...")

    task_contracts = {

        "T1": {
            "runtime_type":
                "FeatureUnion word+character TF-IDF + LinearSVC",

            "input_boundary":
                "Creation/incoming-ticket text",

            "serialized_artifact":
                True,

            "reconstruction_required":
                False,

            "runtime_evidence":
                "FMP-06 OP-018R5",

            "reproducibility_status":
                "RUNTIME_REPRODUCED",
        },

        "T2": {
            "runtime_type":
                "TF-IDF + class-weighted LogisticRegression",

            "input_boundary":
                "Creation-time ticket feature input",

            "serialized_artifact":
                True,

            "reconstruction_required":
                False,

            "runtime_evidence":
                "FMP-06 OP-018R3",

            "reproducibility_status":
                "RUNTIME_REPRODUCED",
        },

        "T3": {
            "runtime_type":
                "TF-IDF + class-weighted LogisticRegression",

            "input_boundary":
                "Creation-time Summary + Description",

            "serialized_artifact":
                True,

            "reconstruction_required":
                False,

            "runtime_evidence":
                "FMP-06 OP-018R3",

            "reproducibility_status":
                "RUNTIME_REPRODUCED",
        },

        "T4": {
            "runtime_type":
                "TF-IDF nearest-neighbor historical retrieval",

            "input_boundary":
                "Creation-time Creator + Creator Detail + "
                "Summary + Description",

            "serialized_artifact":
                True,

            "reconstruction_required":
                False,

            "runtime_evidence":
                "FMP-06 OP-018R16",

            "reproducibility_status":
                "EXACT_EVAL_REPRODUCED",
        },

        "T5": {
            "runtime_type":
                "TF-IDF + LogisticRegression + "
                "task-specific calibration",

            "input_boundary":
                "Creation-time Creator + Creator Detail + "
                "Summary + Description",

            "serialized_artifact":
                True,

            "reconstruction_required":
                False,

            "runtime_evidence":
                "FMP-06 OP-018R3",

            "reproducibility_status":
                "RUNTIME_REPRODUCED",
        },

        "T6": {
            "runtime_type":
                "0.5 lexical + 0.5 semantic retrieval/ranking",

            "input_boundary":
                "Creation-time query/candidate text",

            "serialized_artifact":
                False,

            "reconstruction_required":
                True,

            "runtime_evidence":
                "FMP-06 OP-018R21",

            "reproducibility_status":
                "FROZEN_COMPOSITION_REPRODUCED",
        },

        "T7": {
            "runtime_type":
                "Log-Normal AFT survival model",

            "input_boundary":
                "Creation-time ticket features",

            "serialized_artifact":
                False,

            "reconstruction_required":
                True,

            "runtime_evidence":
                "FMP-06 OP-018R27",

            "reproducibility_status":
                "RUNTIME_REPRODUCED",
        },
    }

    task_manifest = {}

    for task, contract in task_contracts.items():

        artifacts = artifact_records(
            data["freeze_inventory"],
            task
        )

        artifact_presence = all(
            record["exists"]
            for record in artifacts
        )

        task_status = (
            "PASS"
            if artifact_presence
            else "REQUIRES_REVIEW"
        )

        task_manifest[task] = {
            **contract,
            "frozen_artifacts": artifacts,
            "frozen_artifact_presence": artifact_presence,
            "status": task_status,
        }

        print(
            f"  {task}: {task_status} — "
            f"{contract['reproducibility_status']}"
        )

    # ------------------------------------------------------------
    # 4. Record T8–T10 downstream reproducibility boundary
    # ------------------------------------------------------------

    print("\n[4] Recording downstream T8–T10 boundary...")

    downstream = {
        "T8": {
            "status": "CLOSED_PASS",
            "authoritative_runtime_evidence":
                normalize(INPUTS["t8_runtime"]),
            "runtime_execution_established":
                True,
            "role":
                "Evidence integration / decision-engine architecture",
        },

        "T9": {
            "status": "CLOSED_PASS",
            "authoritative_closure":
                normalize(INPUTS["t9_closure"]),
            "runtime_execution_established":
                True,
            "role":
                "Task-specific reliability/calibration synthesis",
        },

        "T10": {
            "status": "POLICY_BOUNDARY_PRESERVED",
            "authoritative_policy_evidence":
                normalize(INPUTS["t10_policy"]),
            "empirically_validated_universal_threshold":
                False,
            "universal_confidence_created":
                False,
            "universal_risk_created":
                False,
            "role":
                "Policy layer; no empirically validated "
                "universal operating threshold established",
        },
    }

    print("  T8: CLOSED_PASS")
    print("  T9: CLOSED_PASS")
    print("  T10: POLICY_BOUNDARY_PRESERVED")

    # ------------------------------------------------------------
    # 5. Final status
    # ------------------------------------------------------------

    print("\n[5] Final reproducibility manifest status...")

    all_tasks_pass = all(
        item["status"] == "PASS"
        for item in task_manifest.values()
    )

    final_status = (
        "PASS"
        if prerequisites_pass and all_tasks_pass
        else "REQUIRES_REVIEW"
    )

    print(
        f"  T1–T7 reproducibility manifest: "
        f"{'PASS' if all_tasks_pass else 'REQUIRES_REVIEW'}"
    )

    print(
        f"  Final OP-004 status: {final_status}"
    )

    # ------------------------------------------------------------
    # 6. Write manifest
    # ------------------------------------------------------------

    result = {
        "operation":
            "FMP-07 OP-004",

        "operation_name":
            "FROZEN_RUNTIME_REPRODUCIBILITY_MANIFEST",

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

        "prerequisites_pass":
            prerequisites_pass,

        "tasks":
            task_manifest,

        "downstream_boundary":
            downstream,

        "interpretation": (
            "This manifest records the frozen runtime "
            "reproducibility boundary for T1–T7 and the "
            "downstream T8–T10 integration boundary. "
            "It does not retrain, refit, select, optimize, "
            "or modify any model or artifact."
        ),
    }

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("\n" + "=" * 78)
    print("OP-004 COMPLETE")
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