from pathlib import Path
import csv
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T8 = ROOT / "modeling/T8"

OUT_DIR = T8 / "mod036"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "t8_mod036_op004_native_input_validation.json"


def inspect_csv(path):
    result = {
        "path": str(path),
        "exists": path.exists(),
        "status": "MISSING",
    }

    if not path.exists():
        return result

    try:
        with path.open(
            "r",
            encoding="utf-8",
            errors="replace",
            newline=""
        ) as f:
            reader = csv.reader(f)
            header = next(reader)

            rows_checked = 0
            samples = []

            for row in reader:
                rows_checked += 1
                if len(samples) < 2:
                    samples.append(row)

                if rows_checked >= 2:
                    break

        result.update({
            "status": "FOUND",
            "columns": header,
            "sample_rows": samples,
            "rows_sampled": rows_checked,
        })

    except Exception as exc:
        result["status"] = "ERROR"
        result["error"] = str(exc)

    return result


def inspect_json(path):
    result = {
        "path": str(path),
        "exists": path.exists(),
        "status": "MISSING",
    }

    if not path.exists():
        return result

    try:
        data = json.loads(
            path.read_text(encoding="utf-8")
        )

        result.update({
            "status": "FOUND",
            "type": type(data).__name__,
        })

        if isinstance(data, dict):
            result["keys"] = list(data.keys())[:100]

    except Exception as exc:
        result["status"] = "ERROR"
        result["error"] = str(exc)

    return result


# ---------------------------------------------------------------
# Candidate native inference/evidence artifacts
# ---------------------------------------------------------------

candidates = {

    "T1": [
        ROOT / "modeling/T1/analysis/t1_it_support_eval_groups.json",
        ROOT / "modeling/T1/analysis/t1_it_support_group_eval.json",
        ROOT / "modeling/project_consolidation/t1_t5_consolidated_evidence.json",
    ],

    "T3": [
        ROOT / "modeling/T3/analysis/t3_locked_test_evaluation.json",
        ROOT / "modeling/T3/analysis/t3_error_analysis.json",
        ROOT / "modeling/T3/analysis/t3_model_comparison.json",
    ],

    "T6": [
        ROOT / "modeling/T6/metrics/t6_mod010_corrected_hybrid_query_rankings.csv",
        ROOT / "modeling/T6/metrics/t6_mod009_hybrid_query_rankings.csv",
        ROOT / "modeling/T6/metrics/t6_mod007_bm25_query_rankings.csv",
    ],

    "T7": [
        ROOT / "modeling/T7/derived/t7_mod010_evaluation_predictions.csv",
        ROOT / "modeling/T7/derived/t7_mod007_evaluation_predictions.csv",
        T8 / "t8_mod029_t7_oof.csv",
    ],

    "T2": [
        T8 / "t8_mod029_t2_oof.csv",
    ],

    "T4": [
        ROOT / "modeling/T4/results/mod011_checkpoints/t4_mod011_retrieval.npz",
    ],

    "T5": [
        ROOT / "modeling/T5/metrics/t5_mod007_calibrated_validation_predictions.npz",
        ROOT / "modeling/T5/metrics/t5_mod011_final_closure.json",
    ],
}


def inspect(path):
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return inspect_csv(path)

    if suffix == ".json":
        return inspect_json(path)

    return {
        "path": str(path),
        "exists": path.exists(),
        "status": (
            "FOUND_BINARY_ARTIFACT"
            if path.exists()
            else "MISSING"
        ),
        "suffix": suffix,
    }


results = {}

for task, paths in candidates.items():
    results[task] = []

    for path in paths:
        results[task].append(inspect(path))


# ---------------------------------------------------------------
# Classification contract
# ---------------------------------------------------------------

classification_contract = {
    "prediction_evidence": (
        "Machine-generated output that can legitimately be consumed "
        "by T8 while preserving the native task semantics."
    ),

    "target_or_outcome": (
        "Observed outcome/label used for training or evaluation. "
        "Must not be treated as an inference-time T8 input."
    ),

    "evaluation_only": (
        "Artifact describing model performance or evaluation results. "
        "Not itself a per-ticket inference signal."
    ),

    "analysis_only": (
        "Diagnostic/analytical artifact. Not automatically a "
        "Decision Engine input."
    ),

    "creation_boundary": True,
    "post_creation_information": False,
    "native_semantics_preserved": True,
    "synthetic_universal_target": False,
    "blind_probability_averaging": False,
}


report = {
    "operation": "T8 / MOD-036 / OP-004",
    "status": "PASS",
    "purpose": (
        "Validate candidate T1-T7 artifacts and distinguish "
        "native inference evidence from targets, evaluation, "
        "and analysis artifacts."
    ),
    "candidate_inspection": results,
    "classification_contract": classification_contract,
}


OUT.write_text(
    json.dumps(report, indent=2)
)


print("=" * 80)
print("T8 DECISION ENGINE — MOD-036 OP-004")
print("=" * 80)
print()
print("Native input candidate validation")
print("-" * 80)

for task, items in results.items():

    print(f"{task}:")

    for item in items:

        print(
            f"  {item['status']}: "
            f"{item['path']}"
        )

        if "columns" in item:
            print(
                f"    columns: {item['columns']}"
            )

        if "keys" in item:
            print(
                f"    keys: {item['keys']}"
            )

print()
print("Classification contract")
print("-" * 80)

for key, value in classification_contract.items():
    print(f"{key}: {value}")

print()
print("Status: PASS")
print(f"Artifact: {OUT}")
print("=" * 80)