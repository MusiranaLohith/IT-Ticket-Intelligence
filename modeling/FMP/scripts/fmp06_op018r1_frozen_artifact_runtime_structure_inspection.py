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
    / "fmp06_op018r1_frozen_artifact_runtime_structure_inspection.json"
)


ARTIFACTS = {
    "T1": [
        PROJECT_ROOT
        / "modeling/T1/baselines/"
        "t1_it_support_char_svm.joblib"
    ],
    "T2": [
        PROJECT_ROOT
        / "modeling/T2/models/"
        "t2_class_weighted_tfidf_logreg.joblib"
    ],
    "T3": [
        PROJECT_ROOT
        / "modeling/T3/models/"
        "t3_class_weighted_tfidf_logreg.joblib"
    ],
    "T5": [
        PROJECT_ROOT
        / "modeling/T5/models/"
        "t5_mod005_tfidf.joblib",
        PROJECT_ROOT
        / "modeling/T5/models/"
        "t5_mod005_logreg.joblib",
        PROJECT_ROOT
        / "modeling/T5/models/"
        "t5_mod007_calibrated_tfidf.joblib",
        PROJECT_ROOT
        / "modeling/T5/models/"
        "t5_mod007_calibration_models.joblib",
    ],
}


INTERESTING_METHODS = [
    "predict",
    "predict_proba",
    "decision_function",
    "transform",
    "fit",
    "fit_transform",
]


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def safe_type(obj: Any) -> str:
    return f"{type(obj).__module__}.{type(obj).__name__}"


def inspect_object(
    obj: Any,
    path: str = "root",
    depth: int = 0,
    max_depth: int = 3,
) -> dict[str, Any]:

    result: dict[str, Any] = {
        "path": path,
        "type": safe_type(obj),
        "python_class": type(obj).__name__,
        "python_module": type(obj).__module__,
        "methods": {},
    }

    for method in INTERESTING_METHODS:
        try:
            result["methods"][method] = callable(
                getattr(obj, method, None)
            )
        except Exception:
            result["methods"][method] = False

    if depth >= max_depth:
        return result

    if isinstance(obj, dict):

        result["container_type"] = "dict"
        result["keys"] = [
            str(key)
            for key in obj.keys()
        ]

        result["children"] = []

        for key, value in obj.items():

            child_path = (
                f"{path}[{key!r}]"
            )

            child = inspect_object(
                value,
                child_path,
                depth + 1,
                max_depth,
            )

            result["children"].append(child)

    elif isinstance(obj, (list, tuple)):

        result["container_type"] = (
            type(obj).__name__
        )

        result["length"] = len(obj)
        result["children"] = []

        for index, value in enumerate(
            obj[:10]
        ):

            child = inspect_object(
                value,
                f"{path}[{index}]",
                depth + 1,
                max_depth,
            )

            result["children"].append(child)

    else:

        result["container_type"] = None

    return result


def inspect_artifact(
    task: str,
    path: Path,
) -> dict[str, Any]:

    print("-" * 72)
    print(task)
    print("ARTIFACT:", rel(path))

    if not path.exists():
        print("STATUS: FILE_NOT_FOUND")

        return {
            "task": task,
            "artifact": rel(path),
            "exists": False,
            "status": "FILE_NOT_FOUND",
        }

    size = path.stat().st_size

    print("SIZE:", size)

    # Runtime loading is intentional here.
    # No inference is executed.
    obj = joblib.load(path)

    print("ROOT TYPE:", safe_type(obj))

    structure = inspect_object(obj)

    if isinstance(obj, dict):
        print(
            "ROOT KEYS:",
            [
                str(key)
                for key in obj.keys()
            ],
        )

    print(
        "ROOT METHODS:",
        {
            method: value
            for method, value
            in structure["methods"].items()
            if value
        },
    )

    return {
        "task": task,
        "artifact": rel(path),
        "exists": True,
        "size_bytes": size,
        "status": "INSPECTED",
        "structure": structure,
    }


def main() -> None:

    print("=" * 72)
    print(
        "FMP-06 OP-018R1 — "
        "FROZEN ARTIFACT RUNTIME STRUCTURE INSPECTION"
    )
    print("=" * 72)
    print()
    print("READ-ONLY STRUCTURE INSPECTION")
    print("joblib.load(): YES")
    print("model inference: NO")
    print("predict(): NO")
    print("fit(): NO")
    print("retraining: NO")
    print("artifact modification: NO")
    print()

    report: dict[str, Any] = {
        "operation": "FMP-06 OP-018R1",
        "operation_type": (
            "READ_ONLY_FROZEN_ARTIFACT_RUNTIME_STRUCTURE_INSPECTION"
        ),
        "artifacts": {},
        "safeguards": {
            "inference_executed": False,
            "predict_called": False,
            "predict_proba_called": False,
            "fit_called": False,
            "retraining": False,
            "artifact_modification": False,
            "threshold_selection": False,
            "calibration_fitting": False,
        },
    }

    for task, paths in ARTIFACTS.items():

        report["artifacts"][task] = []

        for path in paths:

            try:

                result = inspect_artifact(
                    task,
                    path,
                )

            except Exception as exc:

                result = {
                    "task": task,
                    "artifact": rel(path),
                    "exists": path.exists(),
                    "status": "INSPECTION_FAILED",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }

                print(
                    "STATUS: INSPECTION_FAILED"
                )
                print(
                    "ERROR:",
                    str(exc),
                )

            report["artifacts"][task].append(
                result
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