#!/usr/bin/env python3

"""
FMP-02 / Operation 7R
Corrected Native Manifest-to-Artifact Interface Validation

Read-only validation of the retained T2-T7 inference components.

No predictions.
No fitting.
No retraining.
No evaluation selection.
No artifact modification.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

MANIFEST = (
    ROOT
    / "modeling/FMP/metrics/fmp02_t2_t7_inference_manifest.json"
)

OUT = (
    ROOT
    / "modeling/FMP/metrics/"
    "fmp02_manifest_artifact_interface_validation.json"
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def has_method(obj: Any, name: str) -> bool:
    return callable(getattr(obj, name, None))


def type_name(obj: Any) -> str:
    return f"{type(obj).__module__}.{type(obj).__name__}"


def validate_t2_t3(
    task: str,
    artifact_path: Path,
) -> dict[str, Any]:

    obj = joblib.load(artifact_path)

    result = {
        "task": task,
        "artifact": str(artifact_path),
        "loaded": True,
        "artifact_type": type_name(obj),
        "checks": {},
    }

    vectorizer = obj.get("vectorizer")
    model = obj.get("model")

    result["vectorizer_type"] = (
        type_name(vectorizer)
        if vectorizer is not None
        else None
    )

    result["model_type"] = (
        type_name(model)
        if model is not None
        else None
    )

    result["metadata_keys"] = list(obj.keys())

    result["checks"]["vectorizer_present"] = (
        vectorizer is not None
    )

    result["checks"]["vectorizer_transform"] = (
        has_method(vectorizer, "transform")
        if vectorizer is not None
        else False
    )

    result["checks"]["model_present"] = (
        model is not None
    )

    result["checks"]["model_predict"] = (
        has_method(model, "predict")
        if model is not None
        else False
    )

    result["checks"]["model_predict_proba"] = (
        has_method(model, "predict_proba")
        if model is not None
        else False
    )

    # T3's "features" field is metadata, not an executable transformer.
    if task == "T3":
        features = obj.get("features")

        result["features_metadata"] = {
            "present": features is not None,
            "type": (
                type_name(features)
                if features is not None
                else None
            ),
            "value": features,
            "treated_as_executable_transformer": False,
        }

    return result


def validate_t4() -> dict[str, Any]:

    paths = {
        "mod007_tfidf": (
            ROOT
            / "modeling/T4/results/mod007_checkpoints/"
            "t4_mod007_tfidf.joblib"
        ),
        "mod007_neighbors": (
            ROOT
            / "modeling/T4/results/mod007_checkpoints/"
            "t4_mod007_neighbors.joblib"
        ),
        "r1_tfidf": (
            ROOT
            / "modeling/T4/results/r1_checkpoints/"
            "t4_r1_tfidf.joblib"
        ),
        "r1_linear_svc": (
            ROOT
            / "modeling/T4/results/r1_checkpoints/"
            "t4_r1_linear_svc.joblib"
        ),
    }

    objects = {
        label: joblib.load(path)
        for label, path in paths.items()
    }

    checks = {
        "mod007_tfidf_transform": has_method(
            objects["mod007_tfidf"],
            "transform",
        ),
        "mod007_neighbors_kneighbors": has_method(
            objects["mod007_neighbors"],
            "kneighbors",
        ),
        "r1_tfidf_transform": has_method(
            objects["r1_tfidf"],
            "transform",
        ),
        "r1_svc_predict": has_method(
            objects["r1_linear_svc"],
            "predict",
        ),
        "r1_svc_decision_function": has_method(
            objects["r1_linear_svc"],
            "decision_function",
        ),
    }

    return {
        "task": "T4",
        "objects": {
            label: {
                "path": str(paths[label]),
                "type": type_name(objects[label]),
            }
            for label in paths
        },
        "checks": checks,
    }


def validate_t5() -> dict[str, Any]:

    paths = {
        "tfidf": (
            ROOT
            / "modeling/T5/models/"
            "t5_mod005_tfidf.joblib"
        ),
        "logreg": (
            ROOT
            / "modeling/T5/models/"
            "t5_mod005_logreg.joblib"
        ),
        "calibration_models": (
            ROOT
            / "modeling/T5/models/"
            "t5_mod007_calibration_models.joblib"
        ),
    }

    tfidf = joblib.load(paths["tfidf"])
    logreg = joblib.load(paths["logreg"])
    calibration = joblib.load(paths["calibration_models"])

    sigmoid = calibration.get("sigmoid_calibrator")
    isotonic = calibration.get("isotonic_calibrator")
    base_model = calibration.get("base_model")

    checks = {
        "tfidf_transform": has_method(
            tfidf,
            "transform",
        ),
        "standalone_logreg_predict": has_method(
            logreg,
            "predict",
        ),
        "base_model_present": base_model is not None,
        "base_model_predict": (
            has_method(base_model, "predict")
            if base_model is not None
            else False
        ),
        "base_model_predict_proba": (
            has_method(base_model, "predict_proba")
            if base_model is not None
            else False
        ),
        "sigmoid_calibrator_present": sigmoid is not None,
        "sigmoid_calibrator_predict": (
            has_method(sigmoid, "predict")
            if sigmoid is not None
            else False
        ),
        "isotonic_calibrator_present": isotonic is not None,
        "isotonic_calibrator_predict": (
            has_method(isotonic, "predict")
            if isotonic is not None
            else False
        ),
    }

    return {
        "task": "T5",
        "objects": {
            "tfidf": {
                "path": str(paths["tfidf"]),
                "type": type_name(tfidf),
            },
            "logreg": {
                "path": str(paths["logreg"]),
                "type": type_name(logreg),
            },
            "calibration_models": {
                "path": str(paths["calibration_models"]),
                "type": type_name(calibration),
                "keys": list(calibration.keys()),
            },
            "base_model": {
                "type": (
                    type_name(base_model)
                    if base_model is not None
                    else None
                ),
            },
            "sigmoid_calibrator": {
                "type": (
                    type_name(sigmoid)
                    if sigmoid is not None
                    else None
                ),
            },
            "isotonic_calibrator": {
                "type": (
                    type_name(isotonic)
                    if isotonic is not None
                    else None
                ),
            },
        },
        "checks": checks,
    }


def validate_t6() -> dict[str, Any]:

    tfidf_path = (
        ROOT
        / "modeling/T6/models/"
        "t6_mod004_tfidf_vectorizer.joblib"
    )

    semantic_script = (
        ROOT
        / "modeling/T6/scripts/"
        "t6_mod008_semantic_failure_retrieval.py"
    )

    hybrid_script = (
        ROOT
        / "modeling/T6/scripts/"
        "t6_mod009_hybrid_lexical_semantic_retrieval.py"
    )

    tfidf = joblib.load(tfidf_path)

    checks = {
        "lexical_transform": has_method(
            tfidf,
            "transform",
        ),
        "semantic_implementation_present": (
            semantic_script.exists()
        ),
        "hybrid_implementation_present": (
            hybrid_script.exists()
        ),
    }

    return {
        "task": "T6",
        "lexical_component": {
            "path": str(tfidf_path),
            "type": type_name(tfidf),
        },
        "implementation_components": {
            "semantic_retrieval_script": str(semantic_script),
            "hybrid_retrieval_script": str(hybrid_script),
        },
        "checks": checks,
    }


def validate_t7() -> dict[str, Any]:

    lognormal_path = (
        ROOT
        / "modeling/T7/metrics/"
        "t7_mod010_log_normal_aft_model.json"
    )

    weibull_path = (
        ROOT
        / "modeling/T7/metrics/"
        "t7_mod007_weibull_aft_model.json"
    )

    script_path = (
        ROOT
        / "modeling/T7/scripts/"
        "t7_mod010_log_normal_aft_baseline.py"
    )

    lognormal = load_json(lognormal_path)
    weibull = load_json(weibull_path)

    required_lognormal = {
        "model_type",
        "sigma",
        "beta",
        "feature_names",
        "standardization_mean",
        "standardization_std",
    }

    required_weibull = {
        "model_type",
        "shape",
        "beta",
        "feature_names",
        "standardization_mean",
        "standardization_std",
    }

    checks = {
        "lognormal_spec_readable": True,
        "weibull_spec_readable": True,
        "lognormal_required_parameters": (
            required_lognormal.issubset(
                lognormal.keys()
            )
        ),
        "weibull_required_parameters": (
            required_weibull.issubset(
                weibull.keys()
            )
        ),
        "reconstruction_script_present": (
            script_path.exists()
        ),
    }

    return {
        "task": "T7",
        "lognormal_keys": list(lognormal.keys()),
        "weibull_keys": list(weibull.keys()),
        "reconstruction_script": str(script_path),
        "checks": checks,
    }


def task_passes(task_report: dict[str, Any]) -> bool:

    return all(
        value is True
        for value in task_report["checks"].values()
    )


def main() -> None:

    manifest = load_json(MANIFEST)

    report = {
        "operation": "FMP-02-OP-007R",
        "title": (
            "Corrected Native Manifest-to-Artifact "
            "Interface Validation"
        ),
        "manifest": str(MANIFEST),
        "read_only": True,
        "prediction_generated": False,
        "retraining_performed": False,
        "evaluation_selection_performed": False,
        "artifact_modified": False,
        "tasks": {},
    }

    print("=" * 80)
    print("FMP-02 / OPERATION 7R")
    print("CORRECTED NATIVE INTERFACE VALIDATION")
    print("=" * 80)

    print()
    print("T2")
    print("-" * 80)

    report["tasks"]["T2"] = validate_t2_t3(
        "T2",
        Path(
            manifest["tasks"]["T2"]["artifact"]
        ),
    )

    print(
        "Native T2 artifact structure validated."
    )

    print()
    print("T3")
    print("-" * 80)

    report["tasks"]["T3"] = validate_t2_t3(
        "T3",
        Path(
            manifest["tasks"]["T3"]["artifact"]
        ),
    )

    print(
        "Native T3 artifact structure validated."
    )

    print()
    print("T4")
    print("-" * 80)

    report["tasks"]["T4"] = validate_t4()

    print(
        "Native T4 retrieval interfaces validated."
    )

    print()
    print("T5")
    print("-" * 80)

    report["tasks"]["T5"] = validate_t5()

    print(
        "Native T5 calibration interfaces validated."
    )

    print()
    print("T6")
    print("-" * 80)

    report["tasks"]["T6"] = validate_t6()

    print(
        "Native T6 hybrid components validated."
    )

    print()
    print("T7")
    print("-" * 80)

    report["tasks"]["T7"] = validate_t7()

    print(
        "Native T7 model-specification interfaces validated."
    )

    all_pass = all(
        task_passes(task_report)
        for task_report in report["tasks"].values()
    )

    report["status"] = (
        "PASS"
        if all_pass
        else "FAIL"
    )

    OUT.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 80)
    print("REPORT WRITTEN")
    print("=" * 80)
    print(OUT)

    print()
    print("Read-only controls:")
    print("  prediction generated: NO")
    print("  model retrained: NO")
    print("  evaluation used for selection: NO")
    print("  artifact modified: NO")

    print()
    print("STATUS:", report["status"])
    print("=" * 80)


if __name__ == "__main__":
    main()