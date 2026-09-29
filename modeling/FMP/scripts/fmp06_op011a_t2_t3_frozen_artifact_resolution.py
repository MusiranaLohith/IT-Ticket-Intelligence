#!/usr/bin/env python3

"""
FMP-06 OP-011A
T2/T3 Frozen Artifact Resolution

Read-only investigation.

Purpose:
    Resolve the authoritative frozen runtime artifacts for T2 and T3
    after FMP-06 OP-010 found implementation candidates but could not
    establish the frozen closure/artifact contract.

This operation:
    - inventories files
    - reads JSON metadata
    - identifies model/prediction/metric/closure artifacts
    - inspects Python source text for authoritative/final artifact
      references
    - performs no inference
    - performs no training
    - modifies no project artifact
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

MODELING_ROOT = PROJECT_ROOT / "modeling"

OUTPUT_PATH = (
    MODELING_ROOT
    / "FMP"
    / "metrics"
    / "fmp06_op011a_t2_t3_frozen_artifact_resolution.json"
)


def read_text(path: Path) -> str:
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def load_json(path: Path) -> Any:
    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as handle:
            return json.load(handle)

    except Exception as exc:
        return {
            "__read_error__": (
                f"{type(exc).__name__}: {exc}"
            )
        }


def json_summary(obj: Any) -> dict[str, Any]:

    result = {
        "type": type(obj).__name__,
        "top_level_keys": [],
        "interesting_values": {},
    }

    if not isinstance(obj, dict):
        return result

    result["top_level_keys"] = sorted(
        str(key)
        for key in obj.keys()
    )

    interesting_keys = {
        "status",
        "closure_status",
        "final_status",
        "modeling_status",
        "supported_as",
        "not_supported_as",
        "selected_model",
        "final_model",
        "model_name",
        "model",
        "artifact",
        "artifact_path",
        "model_path",
        "prediction_path",
        "predictions_path",
        "metrics_path",
        "final_artifact",
        "selected_artifact",
    }

    for key in sorted(obj.keys(), key=str):

        if str(key) in interesting_keys:

            value = obj[key]

            if isinstance(
                value,
                (str, int, float, bool),
            ):
                result["interesting_values"][
                    str(key)
                ] = value

            elif value is None:
                result["interesting_values"][
                    str(key)
                ] = None

            else:
                result["interesting_values"][
                    str(key)
                ] = str(value)

    return result


def syntax_summary(path: Path) -> dict[str, Any]:

    result = {
        "syntax_valid": False,
        "functions": [],
        "classes": [],
        "error": None,
    }

    try:

        tree = ast.parse(
            read_text(path),
            filename=str(path),
        )

        result["syntax_valid"] = True

        result["functions"] = sorted(
            {
                node.name
                for node in ast.walk(tree)
                if isinstance(
                    node,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                    ),
                )
            }
        )

        result["classes"] = sorted(
            {
                node.name
                for node in ast.walk(tree)
                if isinstance(
                    node,
                    ast.ClassDef,
                )
            }
        )

    except Exception as exc:

        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

    return result


def source_hits(
    path: Path,
    patterns: list[str],
) -> dict[str, Any]:

    source = read_text(path)

    hits = {}

    for pattern in patterns:

        matching_lines = []

        for number, line in enumerate(
            source.splitlines(),
            start=1,
        ):

            if pattern.lower() in line.lower():

                matching_lines.append(
                    {
                        "line": number,
                        "text": line.strip(),
                    }
                )

        if matching_lines:
            hits[pattern] = matching_lines[:20]

    return hits


def classify_file(path: Path) -> str:

    name = path.name.lower()

    if name.endswith(".joblib"):
        return "MODEL_ARTIFACT"

    if name.endswith(".csv"):
        if "prediction" in name:
            return "PREDICTION_ARTIFACT"

        if "metric" in name:
            return "METRIC_ARTIFACT"

        return "CSV_ARTIFACT"

    if name.endswith(".json"):

        if "closure" in name:
            return "CLOSURE_ARTIFACT"

        if "metric" in name:
            return "METRIC_ARTIFACT"

        if "comparison" in name:
            return "COMPARISON_ARTIFACT"

        if "model" in name:
            return "MODEL_METADATA"

        return "JSON_ARTIFACT"

    if name.endswith(".py"):
        return "PYTHON_IMPLEMENTATION"

    return "OTHER"


def inspect_task(task: str) -> dict[str, Any]:

    task_root = MODELING_ROOT / task

    result = {
        "task": task,
        "task_root": str(task_root),
        "exists": task_root.exists(),
        "files": [],
        "closure_candidates": [],
        "model_candidates": [],
        "prediction_candidates": [],
        "metric_candidates": [],
        "implementation_candidates": [],
        "authoritative_reference_hits": [],
    }

    if not task_root.exists():
        return result

    patterns = [
        "final",
        "closure",
        "selected",
        "frozen",
        "artifact",
        "model_path",
        "joblib",
        "predict",
        "predict_proba",
        "decision_function",
        "locked",
    ]

    for path in sorted(
        task_root.rglob("*")
    ):

        if not path.is_file():
            continue

        relative = path.relative_to(
            PROJECT_ROOT
        )

        category = classify_file(path)

        record = {
            "path": str(path),
            "relative_path": str(relative),
            "name": path.name,
            "suffix": path.suffix,
            "category": category,
            "size_bytes": path.stat().st_size,
        }

        if path.suffix.lower() == ".json":

            obj = load_json(path)

            record["json_summary"] = (
                json_summary(obj)
            )

        elif path.suffix.lower() == ".py":

            syntax = syntax_summary(path)

            record["syntax"] = syntax

            hits = source_hits(
                path,
                patterns,
            )

            record["reference_hits"] = hits

            if hits:
                result[
                    "authoritative_reference_hits"
                ].append(
                    {
                        "path": str(relative),
                        "hits": hits,
                    }
                )

            if syntax["syntax_valid"]:
                result[
                    "implementation_candidates"
                ].append(
                    str(relative)
                )

        result["files"].append(record)

        if category == "CLOSURE_ARTIFACT":
            result["closure_candidates"].append(
                str(relative)
            )

        elif category == "MODEL_ARTIFACT":
            result["model_candidates"].append(
                str(relative)
            )

        elif category == "PREDICTION_ARTIFACT":
            result["prediction_candidates"].append(
                str(relative)
            )

        elif category in {
            "METRIC_ARTIFACT",
            "COMPARISON_ARTIFACT",
        }:
            result["metric_candidates"].append(
                str(relative)
            )

    return result


def determine_resolution(
    task_result: dict[str, Any]
) -> dict[str, Any]:

    closure = task_result[
        "closure_candidates"
    ]

    models = task_result[
        "model_candidates"
    ]

    implementations = task_result[
        "implementation_candidates"
    ]

    references = task_result[
        "authoritative_reference_hits"
    ]

    if (
        closure
        and models
        and implementations
        and references
    ):
        status = "RESOLVED_CANDIDATE"

    elif (
        closure
        and implementations
    ):
        status = "PARTIAL"

    else:
        status = "UNRESOLVED"

    return {
        "status": status,
        "reason": {
            "closure_candidates": len(closure),
            "model_candidates": len(models),
            "implementation_candidates": len(
                implementations
            ),
            "authoritative_reference_files": len(
                references
            ),
        },
        "important_constraint": (
            "This operation does not select a model merely "
            "because a file exists. Final selection requires "
            "explicit evidence connecting the artifact to the "
            "closed task."
        ),
    }


def main() -> None:

    print("=" * 70)
    print("FMP-06 OP-011A")
    print("T2/T3 FROZEN ARTIFACT RESOLUTION")
    print("=" * 70)

    results = {}

    for task in ["T2", "T3"]:

        print()
        print("-" * 70)
        print(task)
        print("-" * 70)

        result = inspect_task(task)

        resolution = determine_resolution(
            result
        )

        result["resolution"] = resolution

        results[task] = result

        print(
            f"task_exists             = "
            f"{result['exists']}"
        )

        print(
            f"total_files             = "
            f"{len(result['files'])}"
        )

        print(
            f"closure_candidates      = "
            f"{len(result['closure_candidates'])}"
        )

        print(
            f"model_candidates        = "
            f"{len(result['model_candidates'])}"
        )

        print(
            f"prediction_candidates   = "
            f"{len(result['prediction_candidates'])}"
        )

        print(
            f"metric_candidates       = "
            f"{len(result['metric_candidates'])}"
        )

        print(
            f"implementation_candidates = "
            f"{len(result['implementation_candidates'])}"
        )

        print(
            f"authoritative_reference_files = "
            f"{len(result['authoritative_reference_hits'])}"
        )

        print(
            f"resolution_status       = "
            f"{resolution['status']}"
        )

        print()
        print("CLOSURE CANDIDATES:")

        for item in result[
            "closure_candidates"
        ]:
            print(f"  {item}")

        print()
        print("MODEL CANDIDATES:")

        for item in result[
            "model_candidates"
        ]:
            print(f"  {item}")

    output = {
        "operation": "FMP-06 OP-011A",
        "operation_title": (
            "T2/T3 Frozen Artifact Resolution"
        ),
        "status": "PASS",
        "purpose": (
            "Resolve the authoritative frozen artifact "
            "evidence for T2 and T3 before raw-ticket inference."
        ),
        "inference_performed": False,
        "retraining_performed": False,
        "artifacts_modified": False,
        "tasks": results,
        "safeguards": {
            "prediction_generated": False,
            "model_fitted": False,
            "locked_test_used_for_selection": False,
            "threshold_selected": False,
            "universal_confidence_created": False,
            "universal_risk_created": False,
        },
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as handle:

        json.dump(
            output,
            handle,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(
        f"Output = {OUTPUT_PATH}"
    )

    print(
        "Inference performed = False"
    )

    print(
        "Retraining performed = False"
    )

    print(
        "Artifacts modified = False"
    )

    print("=" * 70)
    print("FMP-06 OP-011A COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()