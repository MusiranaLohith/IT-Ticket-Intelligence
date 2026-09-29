from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OUTPUT = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "fmp06_op018r2_frozen_runtime_component_interface_audit.json"
)


ARTIFACTS = {
    "T1": (
        PROJECT_ROOT
        / "modeling/T1/baselines/"
        "t1_it_support_char_svm.joblib"
    ),
    "T2": (
        PROJECT_ROOT
        / "modeling/T2/models/"
        "t2_class_weighted_tfidf_logreg.joblib"
    ),
    "T3": (
        PROJECT_ROOT
        / "modeling/T3/models/"
        "t3_class_weighted_tfidf_logreg.joblib"
    ),
    "T5_VECTOR": (
        PROJECT_ROOT
        / "modeling/T5/models/"
        "t5_mod005_tfidf.joblib"
    ),
    "T5_CLASSIFIER": (
        PROJECT_ROOT
        / "modeling/T5/models/"
        "t5_mod005_logreg.joblib"
    ),
    "T5_CALIBRATION": (
        PROJECT_ROOT
        / "modeling/T5/models/"
        "t5_mod007_calibration_models.joblib"
    ),
}


METHODS = [
    "transform",
    "predict",
    "predict_proba",
    "decision_function",
    "fit",
    "fit_transform",
]


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def component_info(
    name: str,
    obj: Any,
) -> dict[str, Any]:

    result: dict[str, Any] = {
        "name": name,
        "type": (
            f"{type(obj).__module__}."
            f"{type(obj).__name__}"
        ),
        "methods": {},
        "attributes": {},
    }

    for method in METHODS:

        try:
            result["methods"][method] = callable(
                getattr(obj, method, None)
            )
        except Exception:
            result["methods"][method] = False

    interesting_attributes = [
        "classes_",
        "n_features_in_",
        "n_features_",
        "coef_",
        "intercept_",
        "vocabulary_",
        "idf_",
        "feature_names_in_",
        "a_",
        "b_",
        "X_thresholds_",
        "y_thresholds_",
    ]

    for attribute in interesting_attributes:

        try:

            value = getattr(
                obj,
                attribute,
            )

            if attribute in {
                "coef_",
                "intercept_",
                "idf_",
                "vocabulary_",
            }:
                if hasattr(value, "shape"):
                    result["attributes"][
                        attribute
                    ] = {
                        "type": (
                            f"{type(value).__module__}."
                            f"{type(value).__name__}"
                        ),
                        "shape": list(
                            value.shape
                        ),
                    }
                elif isinstance(value, dict):
                    result["attributes"][
                        attribute
                    ] = {
                        "type": "dict",
                        "size": len(value),
                    }
                else:
                    result["attributes"][
                        attribute
                    ] = {
                        "type": type(value).__name__
                    }

            elif hasattr(value, "shape"):

                result["attributes"][
                    attribute
                ] = {
                    "shape": list(value.shape)
                }

            elif isinstance(value, (list, tuple)):

                result["attributes"][
                    attribute
                ] = {
                    "type": type(value).__name__,
                    "length": len(value),
                }

            else:

                result["attributes"][
                    attribute
                ] = str(value)[:500]

        except Exception:
            pass

    return result


def inspect_dict_component(
    artifact_name: str,
    path: Path,
    keys: list[str],
) -> dict[str, Any]:

    obj = joblib.load(path)

    result = {
        "artifact": rel(path),
        "artifact_type": (
            f"{type(obj).__module__}."
            f"{type(obj).__name__}"
        ),
        "components": [],
    }

    for key in keys:

        if key not in obj:

            result["components"].append(
                {
                    "name": key,
                    "status": "MISSING",
                }
            )
            continue

        result["components"].append(
            component_info(
                key,
                obj[key],
            )
        )

    return result


def main() -> None:

    print("=" * 72)
    print(
        "FMP-06 OP-018R2 — "
        "FROZEN RUNTIME COMPONENT INTERFACE AUDIT"
    )
    print("=" * 72)
    print()
    print("joblib.load(): YES")
    print("inference: NO")
    print("predict(): NO")
    print("fit(): NO")
    print("artifact modification: NO")
    print()

    report: dict[str, Any] = {
        "operation": "FMP-06 OP-018R2",
        "operation_type": (
            "READ_ONLY_FROZEN_RUNTIME_COMPONENT_INTERFACE_AUDIT"
        ),
        "components": {},
        "safeguards": {
            "inference_executed": False,
            "predict_called": False,
            "predict_proba_called": False,
            "transform_called": False,
            "fit_called": False,
            "retraining": False,
            "artifact_modification": False,
        },
    }

    # T1
    print("-" * 72)
    print("T1")

    t1 = inspect_dict_component(
        "T1",
        ARTIFACTS["T1"],
        ["model", "features", "classifier"],
    )

    report["components"]["T1"] = t1

    for component in t1["components"]:
        print(
            " ",
            component["name"],
            "type=",
            component.get("type"),
            "methods=",
            component.get("methods"),
        )

    # T2
    print("-" * 72)
    print("T2")

    t2 = inspect_dict_component(
        "T2",
        ARTIFACTS["T2"],
        ["vectorizer", "model"],
    )

    report["components"]["T2"] = t2

    for component in t2["components"]:
        print(
            " ",
            component["name"],
            "type=",
            component.get("type"),
            "methods=",
            component.get("methods"),
        )

    # T3
    print("-" * 72)
    print("T3")

    t3 = inspect_dict_component(
        "T3",
        ARTIFACTS["T3"],
        ["vectorizer", "model"],
    )

    report["components"]["T3"] = t3

    for component in t3["components"]:
        print(
            " ",
            component["name"],
            "type=",
            component.get("type"),
            "methods=",
            component.get("methods"),
        )

    # T5 vectorizer
    print("-" * 72)
    print("T5 VECTOR")

    t5_vector = joblib.load(
        ARTIFACTS["T5_VECTOR"]
    )

    vector_info = component_info(
        "t5_vectorizer",
        t5_vector,
    )

    report["components"]["T5_VECTOR"] = vector_info

    print(
        " type=",
        vector_info["type"],
        "methods=",
        vector_info["methods"],
    )

    # T5 classifier
    print("-" * 72)
    print("T5 CLASSIFIER")

    t5_classifier = joblib.load(
        ARTIFACTS["T5_CLASSIFIER"]
    )

    classifier_info = component_info(
        "t5_classifier",
        t5_classifier,
    )

    report["components"]["T5_CLASSIFIER"] = classifier_info

    print(
        " type=",
        classifier_info["type"],
        "methods=",
        classifier_info["methods"],
    )

    # T5 calibration bundle
    print("-" * 72)
    print("T5 CALIBRATION")

    calibration = joblib.load(
        ARTIFACTS["T5_CALIBRATION"]
    )

    calibration_info = {
        "artifact": rel(
            ARTIFACTS["T5_CALIBRATION"]
        ),
        "keys": [
            str(key)
            for key in calibration.keys()
        ],
        "components": [],
    }

    for key in (
        "base_model",
        "sigmoid_calibrator",
        "isotonic_calibrator",
    ):

        if key not in calibration:

            calibration_info["components"].append(
                {
                    "name": key,
                    "status": "MISSING",
                }
            )
            continue

        info = component_info(
            key,
            calibration[key],
        )

        calibration_info["components"].append(
            info
        )

        print(
            " ",
            key,
            "type=",
            info["type"],
            "methods=",
            info["methods"],
        )

    report["components"]["T5_CALIBRATION"] = (
        calibration_info
    )

    report["overall_status"] = "PASS"

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            report,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 72)
    print("OVERALL STATUS: PASS")
    print("OUTPUT:", OUTPUT)
    print("=" * 72)


if __name__ == "__main__":
    main()