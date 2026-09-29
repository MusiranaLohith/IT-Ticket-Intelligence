from pathlib import Path
import json
import csv
from datetime import datetime, timezone


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

OUTPUT_PATH = (
    PROJECT_ROOT
    / "modeling/FMP/metrics/fmp06_op001_e2e_runtime_interface_inventory.json"
)


# ---------------------------------------------------------------------
# Authoritative artifacts representing the frozen outputs/interfaces
# ---------------------------------------------------------------------

ARTIFACTS = {
    "T1": [
        PROJECT_ROOT / "modeling/T1/analysis/t1_final_closure.json",
        PROJECT_ROOT / "modeling/T1/analysis/t1_it_support_3model_compare.json",
    ],

    "T2": [
        PROJECT_ROOT / "modeling/T2/analysis/t2_final_test_predictions.csv",
        PROJECT_ROOT / "modeling/T2/analysis/t2_final_test_metrics.json",
        PROJECT_ROOT / "modeling/T2/analysis/t2_final_closure.json",
    ],

    "T3": [
        PROJECT_ROOT / "modeling/T3/analysis/t3_locked_test_evaluation.json",
        PROJECT_ROOT / "modeling/T3/metrics/t3_final_test_metrics.json",
        PROJECT_ROOT / "modeling/T3/analysis/t3_final_closure.json",
    ],

    "T4": [
        PROJECT_ROOT / "modeling/T4/results/t4_mod013_closure.json",
    ],

    "T5": [
        PROJECT_ROOT / "modeling/T5/metrics/t5_mod009_locked_evaluation_metrics.json",
        PROJECT_ROOT / "modeling/T5/metrics/t5_mod011_final_closure.json",
    ],

    "T6": [
        PROJECT_ROOT / "modeling/T6/metrics/t6_final_closure.json",
        PROJECT_ROOT / "modeling/T6/metrics/t6_mod010_corrected_hybrid_results.json",
    ],

    "T7": [
        PROJECT_ROOT / "modeling/T7/metrics/t7_mod012_final_closure.json",
    ],

    "T8": [
        PROJECT_ROOT
        / "modeling/T8/mod036/op026/t8_mod036_op026_decision_engine_validation.json",
    ],

    "T9": [
        PROJECT_ROOT
        / "modeling/T9/mod037/t9_mod037_op015_final_integrated_closure.json",
    ],

    "T10": [
        PROJECT_ROOT / "modeling/project_consolidation.py",
    ],
}


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def read_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_csv_header(path):
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        reader = csv.reader(f)
        return next(reader, [])


def inspect_artifact(path):
    result = {
        "path": str(path),
        "exists": path.exists(),
        "readable": False,
        "type": path.suffix.lower(),
        "size_bytes": None,
        "top_level_keys": None,
        "columns": None,
        "error": None,
    }

    if not path.exists():
        return result

    try:
        result["size_bytes"] = path.stat().st_size

        if path.suffix.lower() == ".json":
            data = read_json(path)
            result["readable"] = True

            if isinstance(data, dict):
                result["top_level_keys"] = list(data.keys())

            elif isinstance(data, list):
                result["top_level_keys"] = [
                    f"<list:{len(data)}>"
                ]

            else:
                result["top_level_keys"] = [
                    f"<{type(data).__name__}>"
                ]

        elif path.suffix.lower() == ".csv":
            columns = read_csv_header(path)
            result["readable"] = True
            result["columns"] = columns

        elif path.suffix.lower() == ".py":
            path.read_text(encoding="utf-8")
            result["readable"] = True

        else:
            result["readable"] = True

    except Exception as exc:
        result["error"] = str(exc)

    return result


def summarize_stage(stage, artifacts):
    readable = [
        item for item in artifacts
        if item["exists"] and item["readable"]
    ]

    missing = [
        item for item in artifacts
        if not item["exists"]
    ]

    unreadable = [
        item for item in artifacts
        if item["exists"] and not item["readable"]
    ]

    return {
        "stage": stage,
        "artifact_count": len(artifacts),
        "readable_count": len(readable),
        "missing_count": len(missing),
        "unreadable_count": len(unreadable),
        "stage_status": (
            "PASS"
            if readable and not missing and not unreadable
            else "REVIEW_REQUIRED"
        ),
        "artifacts": artifacts,
    }


# ---------------------------------------------------------------------
# Main operation
# ---------------------------------------------------------------------

def main():
    print("=" * 80)
    print("FMP-06 OP-001 — E2E RUNTIME INTERFACE INVENTORY")
    print("=" * 80)

    print("\n[1] Operation contract")
    print("-" * 80)

    print("Operation type: READ_ONLY_E2E_RUNTIME_INTERFACE_INVENTORY")
    print("Models loaded: False")
    print("Predictions generated: False")
    print("Retraining: False")
    print("Calibration fitting: False")
    print("Threshold selection: False")
    print("Policy modification: False")
    print("Artifact modification: False")

    print("\n[2] Inspecting frozen stage artifacts")
    print("-" * 80)

    stage_results = {}
    all_missing = []
    all_unreadable = []

    for stage, paths in ARTIFACTS.items():
        print(f"\n{stage}")

        inspected = []

        for path in paths:
            result = inspect_artifact(path)
            inspected.append(result)

            print(f"  path: {path}")
            print(f"    exists: {result['exists']}")
            print(f"    readable: {result['readable']}")
            print(f"    size_bytes: {result['size_bytes']}")

            if result["top_level_keys"] is not None:
                print(
                    "    top_level_keys:",
                    ", ".join(result["top_level_keys"])
                )

            if result["columns"] is not None:
                print(
                    "    columns:",
                    ", ".join(result["columns"])
                )

            if result["error"]:
                print(f"    error: {result['error']}")

            if not result["exists"]:
                all_missing.append(
                    {
                        "stage": stage,
                        "path": str(path),
                    }
                )

            elif not result["readable"]:
                all_unreadable.append(
                    {
                        "stage": stage,
                        "path": str(path),
                        "error": result["error"],
                    }
                )

        stage_results[stage] = summarize_stage(
            stage,
            inspected
        )

    print("\n[3] Stage availability summary")
    print("-" * 80)

    for stage in ARTIFACTS:
        summary = stage_results[stage]

        print(
            f"{stage}: "
            f"readable={summary['readable_count']}/"
            f"{summary['artifact_count']} "
            f"status={summary['stage_status']}"
        )

    print("\n[4] Frozen chain representation")
    print("-" * 80)

    chain = [
        "T1",
        "T2",
        "T3",
        "T4",
        "T5",
        "T6",
        "T7",
        "T8",
        "T9",
        "T10",
    ]

    for index, stage in enumerate(chain):
        if index < len(chain) - 1:
            print(f"{stage} -> {chain[index + 1]}")
        else:
            print(stage)

    print("\n[5] Runtime interface observations")
    print("-" * 80)

    interface_observations = {
        "T1_to_T2": (
            "Both task artifacts exist, but this operation does not infer "
            "an executable runtime adapter merely from artifact presence."
        ),
        "T2_to_T3": (
            "T2 and T3 native prediction/evaluation artifacts exist. "
            "Native task semantics remain separate."
        ),
        "T3_to_T4": (
            "T3 and T4 artifacts exist. This inventory does not assume "
            "that a direct prediction-to-retrieval runtime call exists."
        ),
        "T4_to_T5": (
            "T4 and T5 artifacts exist with distinct task semantics."
        ),
        "T5_to_T6": (
            "T5 duplicate-probability evidence and T6 retrieval evidence "
            "remain task-specific."
        ),
        "T6_to_T7": (
            "T6 retrieval and T7 survival evidence remain at their "
            "native task grains."
        ),
        "T7_to_T8": (
            "T8 has a validated evidence-engine artifact and consumes "
            "native task evidence according to its established architecture."
        ),
        "T8_to_T9": (
            "T9 has an integrated closure artifact and receives "
            "task-specific reliability/calibration evidence."
        ),
        "T9_to_T10": (
            "T10 policy architecture exists in project consolidation, "
            "while empirical operational policy boundaries remain "
            "not established."
        ),
    }

    for interface, observation in interface_observations.items():
        print(f"{interface}")
        print(f"  {observation}")

    print("\n[6] E2E execution distinction")
    print("-" * 80)

    print(
        "Artifact availability does NOT by itself prove that a complete "
        "runtime execution T1-T7 -> T8 -> T9 -> T10 has occurred."
    )

    print(
        "This operation therefore records interface/artifact availability "
        "without claiming full runtime execution."
    )

    print("\n[7] Read-only safeguards")
    print("-" * 80)

    safeguards = {
        "models_loaded": False,
        "predictions_generated": False,
        "retraining_performed": False,
        "calibration_fitted": False,
        "threshold_selected": False,
        "threshold_optimized": False,
        "policy_modified": False,
        "artifacts_modified": False,
        "universal_confidence_created": False,
        "universal_risk_created": False,
    }

    for key, value in safeguards.items():
        print(f"{key}: {value}")

    print("\n[8] Final status")
    print("-" * 80)

    if all_missing or all_unreadable:
        status = "BLOCKED"
    else:
        status = "PASS"

    print(f"STATUS: {status}")

    output = {
        "operation": "FMP-06-OP-001",
        "operation_name": "E2E Runtime Interface Inventory",
        "operation_type": "READ_ONLY_E2E_RUNTIME_INTERFACE_INVENTORY",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "stage_order": chain,
        "stage_results": stage_results,
        "missing_artifacts": all_missing,
        "unreadable_artifacts": all_unreadable,
        "interface_observations": interface_observations,
        "e2e_execution_claim": (
            "NOT_ESTABLISHED_BY_THIS_OPERATION"
        ),
        "safeguards": safeguards,
        "status": status,
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(
            output,
            f,
            indent=2
        )

    print("\n[9] Output")
    print("-" * 80)
    print(f"Saved: {OUTPUT_PATH}")

    print("\n" + "=" * 80)
    print("FMP-06 OP-001 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()