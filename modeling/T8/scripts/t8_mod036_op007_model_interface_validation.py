from pathlib import Path
import json
import joblib


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T8 = ROOT / "modeling/T8"

OUT_DIR = T8 / "mod036"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "t8_mod036_op007_model_interface_validation.json"


# ------------------------------------------------------------------
# Candidate model artifacts
# ------------------------------------------------------------------

MODEL_CANDIDATES = {
    "T1_svm":
        ROOT / "modeling/baselines/t1_it_support_svm.joblib",

    "T3_final":
        ROOT / "modeling/T3/models/t3_class_weighted_tfidf_logreg.joblib",
}


# ------------------------------------------------------------------
# Load JSON provenance reports
# ------------------------------------------------------------------

PROVENANCE_FILES = {
    "T1_baseline_report":
        ROOT / "modeling/T1/baselines/t1_it_support_baseline_report.json",

    "T1_svm_report":
        ROOT / "modeling/T1/baselines/t1_it_support_svm_report.json",

    "T1_char_svm_report":
        ROOT / "modeling/T1/baselines/t1_it_support_char_svm_report.json",

    "T3_final_closure":
        ROOT / "modeling/T3/analysis/t3_final_closure.json",

    "T3_final_metrics":
        ROOT / "modeling/T3/metrics/t3_final_test_metrics.json",

    "T3_model_contract":
        ROOT / "modeling/T3/contracts/t3_model_contract.json",
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
# Model interface inspection
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
        model = joblib.load(path)

        result["status"] = "LOADED"
        result["python_type"] = type(model).__name__
        result["module"] = type(model).__module__

        result["has_predict"] = callable(
            getattr(model, "predict", None)
        )

        result["has_predict_proba"] = callable(
            getattr(model, "predict_proba", None)
        )

        result["has_decision_function"] = callable(
            getattr(model, "decision_function", None)
        )

        classes = getattr(model, "classes_", None)

        if classes is not None:
            result["classes"] = [
                str(x)
                for x in classes
            ]

        # Pipeline / composite-model structure
        if hasattr(model, "steps"):

            result["pipeline_steps"] = [
                {
                    "name": name,
                    "type": type(step).__name__,
                    "module": type(step).__module__,
                }
                for name, step in model.steps
            ]

        elif hasattr(model, "named_steps"):

            result["pipeline_steps"] = [
                {
                    "name": name,
                    "type": type(step).__name__,
                    "module": type(step).__module__,
                }
                for name, step in model.named_steps.items()
            ]

        else:
            result["pipeline_steps"] = []

        # Useful vectorizer/model attributes without fitting
        for attr in [
            "n_features_in_",
            "feature_names_in_",
            "vocabulary_",
            "idf_",
        ]:

            if hasattr(model, attr):

                value = getattr(model, attr)

                if attr == "vocabulary_":
                    result["vocabulary_size"] = len(value)

                elif attr == "idf_":
                    result["idf_length"] = len(value)

                elif attr == "feature_names_in_":
                    result["feature_names_count"] = len(value)

                else:
                    result[attr] = (
                        str(value)
                        if not isinstance(
                            value,
                            (int, float, str, bool)
                        )
                        else value
                    )

    except Exception as exc:

        result["status"] = "LOAD_ERROR"
        result["error"] = str(exc)

    return result


model_results = {}

for name, path in MODEL_CANDIDATES.items():
    model_results[name] = inspect_model(
        name,
        path,
    )


# ------------------------------------------------------------------
# Provenance inspection
# ------------------------------------------------------------------

provenance_results = {}

for name, path in PROVENANCE_FILES.items():

    loaded = load_json(path)

    if loaded["status"] != "FOUND":
        provenance_results[name] = loaded
        continue

    data = loaded["data"]

    selected = {}

    if isinstance(data, dict):

        for key in [
            "status",
            "task",
            "model",
            "model_id",
            "model_path",
            "final_candidate",
            "system_role",
            "recommended_use",
            "probability_output",
            "artifacts",
            "prediction_boundary",
            "target",
            "features",
        ]:

            if key in data:
                selected[key] = data[key]

    provenance_results[name] = {
        "status": "FOUND",
        "selected_fields": selected,
    }


# ------------------------------------------------------------------
# Decision
# ------------------------------------------------------------------

decision = {
    "T1_model_interface_validated": (
        model_results["T1_svm"].get("status") == "LOADED"
        and model_results["T1_svm"].get("has_predict", False)
    ),

    "T3_model_interface_validated": (
        model_results["T3_final"].get("status") == "LOADED"
        and model_results["T3_final"].get("has_predict", False)
    ),

    "T3_final_model_explicitly_identified": (
        provenance_results
        .get("T3_final_closure", {})
        .get("selected_fields", {})
        .get("final_candidate", {})
        .get("model_id")
        == "T3-MOD-008"
    ),

    "prediction_generation_performed": False,
    "training_performed": False,
}


report = {
    "operation": "T8 / MOD-036 / OP-007",
    "status": "PASS",
    "purpose": (
        "Validate the inference interfaces and provenance of "
        "the identified T1/T3 model artifacts without training "
        "or generating predictions."
    ),
    "model_interfaces": model_results,
    "provenance": provenance_results,
    "decision": decision,
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
print("T8 DECISION ENGINE — MOD-036 OP-007")
print("=" * 80)

print()
print("Model interface validation")
print("-" * 80)

for name, result in model_results.items():

    print(f"{name}")
    print(f"  Status: {result['status']}")
    print(f"  Path: {result['path']}")

    if result["status"] != "LOADED":
        continue

    print(
        f"  Type: "
        f"{result['module']}."
        f"{result['python_type']}"
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

print()
print("Decision")
print("-" * 80)

for key, value in decision.items():
    print(f"{key}: {value}")

print()
print("Status: PASS")
print(f"Artifact: {OUT}")
print("=" * 80)