from pathlib import Path
import json
import joblib


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T8 = ROOT / "modeling/T8"

OUT_DIR = T8 / "mod036"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "t8_mod036_op009_t1_model_resolution.json"


# ------------------------------------------------------------------
# Authoritative T1 contract / reconciliation artifacts
# ------------------------------------------------------------------

SOURCE_FILES = {
    "t1_contract":
        ROOT / "modeling/T1/contracts/t1_contract.json",

    "t1_reconcile_status_script":
        ROOT / "modeling/T1/splits/t1_reconcile_status.py",

    "t1_baseline_report":
        ROOT / "modeling/T1/baselines/t1_it_support_baseline_report.json",

    "t1_svm_report":
        ROOT / "modeling/T1/baselines/t1_it_support_svm_report.json",

    "t1_char_svm_report":
        ROOT / "modeling/T1/baselines/t1_it_support_char_svm_report.json",

    "t1_three_model_compare":
        ROOT / "modeling/T1/analysis/t1_it_support_3model_compare.json",
}


MODEL_FILES = {
    "t1_baseline":
        ROOT / "modeling/T1/baselines/t1_it_support_baseline.joblib",

    "t1_svm":
        ROOT / "modeling/T1/baselines/t1_it_support_svm.joblib",

    "t1_char_svm":
        ROOT / "modeling/T1/baselines/t1_it_support_char_svm.joblib",
}


def load_json(path):

    if not path.exists():
        return {
            "status": "MISSING",
            "path": str(path),
        }

    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        )

        return {
            "status": "FOUND",
            "path": str(path),
            "data": data,
        }

    except Exception as exc:

        return {
            "status": "ERROR",
            "path": str(path),
            "error": str(exc),
        }


# ------------------------------------------------------------------
# Inspect T1 reports/contracts
# ------------------------------------------------------------------

source_results = {}

for name, path in SOURCE_FILES.items():

    result = load_json(path)

    if result["status"] != "FOUND":
        source_results[name] = result
        continue

    data = result["data"]

    selected = {}

    if isinstance(data, dict):

        for key in [
            "status",
            "operation",
            "task",
            "task_id",
            "target",
            "prediction_boundary",
            "model",
            "models",
            "results",
            "rankings",
            "selected_model",
            "selection",
            "final_model",
            "model_path",
            "probability_output",
            "metrics",
            "overall",
            "integrity",
            "controls",
            "raw_source_modified",
            "model_retrained",
            "evaluation_used_for_fit",
            "frozen_split_modified",
            "labels_modified",
        ]:

            if key in data:
                selected[key] = data[key]

    source_results[name] = {
        "status": "FOUND",
        "path": str(path),
        "selected_fields": selected,
        "top_level_keys": (
            list(data.keys())
            if isinstance(data, dict)
            else []
        ),
    }


# ------------------------------------------------------------------
# Inspect actual T1 model objects
# ------------------------------------------------------------------

def inspect_model(name, path):

    result = {
        "name": name,
        "path": str(path),
        "exists": path.exists(),
    }

    if not path.exists():
        result["status"] = "MISSING"
        return result

    try:

        obj = joblib.load(path)

        result["status"] = "LOADED"
        result["outer_type"] = type(obj).__name__
        result["outer_module"] = type(obj).__module__

        result["has_predict"] = callable(
            getattr(obj, "predict", None)
        )

        result["has_predict_proba"] = callable(
            getattr(obj, "predict_proba", None)
        )

        result["has_decision_function"] = callable(
            getattr(obj, "decision_function", None)
        )

        if hasattr(obj, "classes_"):

            result["classes"] = [
                str(x)
                for x in obj.classes_
            ]

        if hasattr(obj, "steps"):

            result["pipeline_steps"] = [
                {
                    "name": step_name,
                    "type": type(step).__name__,
                    "module": type(step).__module__,
                }
                for step_name, step in obj.steps
            ]

        else:

            result["pipeline_steps"] = []

        if isinstance(obj, dict):

            result["dictionary_keys"] = list(
                obj.keys()
            )

            result["dictionary_components"] = {
                str(key): {
                    "type": type(value).__name__,
                    "module": type(value).__module__,
                    "has_predict": callable(
                        getattr(value, "predict", None)
                    ),
                    "has_predict_proba": callable(
                        getattr(value, "predict_proba", None)
                    ),
                }
                for key, value in obj.items()
            }

    except Exception as exc:

        result["status"] = "LOAD_ERROR"
        result["error"] = str(exc)

    return result


model_results = {}

for name, path in MODEL_FILES.items():

    model_results[name] = inspect_model(
        name,
        path,
    )


# ------------------------------------------------------------------
# Report
# ------------------------------------------------------------------

report = {
    "operation": "T8 / MOD-036 / OP-009",
    "status": "PASS",
    "purpose": (
        "Resolve the native T1 IT Support model from the "
        "existing frozen contract, reports, comparison evidence, "
        "and actual model artifacts."
    ),
    "source_evidence": source_results,
    "model_interfaces": model_results,
    "controls": {
        "training_performed": False,
        "prediction_generation_performed": False,
        "model_modified": False,
        "dataset_modified": False,
        "new_model_selected": False,
    },
}


OUT.write_text(
    json.dumps(
        report,
        indent=2,
    )
)


# ------------------------------------------------------------------
# Terminal output
# ------------------------------------------------------------------

print("=" * 80)
print("T8 DECISION ENGINE — MOD-036 OP-009")
print("=" * 80)

print()
print("T1 contract / report evidence")
print("-" * 80)

for name, result in source_results.items():

    print(f"{name}: {result['status']}")

    if result["status"] != "FOUND":
        continue

    fields = result.get(
        "selected_fields",
        {},
    )

    for key, value in fields.items():

        print(
            f"  {key}: "
            f"{str(value)[:1000]}"
        )

print()
print("Actual T1 model interfaces")
print("-" * 80)

for name, result in model_results.items():

    print(f"{name}")
    print(f"  Status: {result['status']}")
    print(f"  Path: {result['path']}")

    if result["status"] != "LOADED":
        continue

    print(
        f"  Type: "
        f"{result['outer_module']}."
        f"{result['outer_type']}"
    )

    print(
        f"  predict(): "
        f"{result['has_predict']}"
    )

    print(
        f"  predict_proba(): "
        f"{result['has_predict_proba']}"
    )

    print(
        f"  decision_function(): "
        f"{result['has_decision_function']}"
    )

    if "classes" in result:
        print(
            f"  Classes: "
            f"{result['classes']}"
        )

    if result.get("pipeline_steps"):
        print("  Pipeline steps:")

        for step in result["pipeline_steps"]:
            print(
                f"    {step['name']}: "
                f"{step['module']}."
                f"{step['type']}"
            )

    if result.get("dictionary_components"):
        print("  Dictionary components:")

        for key, component in result[
            "dictionary_components"
        ].items():

            print(
                f"    {key}: "
                f"{component['module']}."
                f"{component['type']} "
                f"(predict={component['has_predict']}, "
                f"predict_proba={component['has_predict_proba']})"
            )

print()
print("Controls")
print("-" * 80)

for key, value in report["controls"].items():
    print(f"{key}: {value}")

print()
print("Status: PASS")
print(f"Artifact: {OUT}")
print("=" * 80)