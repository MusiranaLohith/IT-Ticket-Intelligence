#!/usr/bin/env python3

"""
FMP-06 OP-011B
T2/T3 Final Model Selection Resolution

Read-only audit.

Purpose:
    Resolve the authoritative frozen model artifact for T2 and T3
    from their final closure records.

No:
    - model loading
    - inference
    - training
    - calibration
    - threshold selection
    - artifact modification
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
    / "fmp06_op011b_t2_t3_final_model_selection_resolution.json"
)


TASKS = {
    "T2": {
        "closure": (
            MODELING_ROOT
            / "T2"
            / "analysis"
            / "t2_final_closure.json"
        ),
        "task_root": MODELING_ROOT / "T2",
    },
    "T3": {
        "closure": (
            MODELING_ROOT
            / "T3"
            / "analysis"
            / "t3_final_closure.json"
        ),
        "task_root": MODELING_ROOT / "T3",
    },
}


REFERENCE_KEYS = {
    "selected_model",
    "final_model",
    "model_name",
    "model",
    "artifact",
    "artifact_path",
    "model_path",
    "selected_artifact",
    "final_artifact",
    "model_artifact",
    "frozen_artifact",
    "joblib",
}


def load_json(path: Path) -> Any:
    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


def flatten_values(
    obj: Any,
    path: str = "",
) -> list[dict[str, Any]]:

    results = []

    if isinstance(obj, dict):

        for key, value in obj.items():

            current = (
                f"{path}.{key}"
                if path
                else str(key)
            )

            if str(key).lower() in {
                key.lower()
                for key in REFERENCE_KEYS
            }:

                results.append(
                    {
                        "json_path": current,
                        "key": str(key),
                        "value": value,
                    }
                )

            results.extend(
                flatten_values(
                    value,
                    current,
                )
            )

    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            current = f"{path}[{index}]"

            results.extend(
                flatten_values(
                    value,
                    current,
                )
            )

    return results


def collect_strings(
    obj: Any,
    path: str = "",
) -> list[dict[str, str]]:

    results = []

    if isinstance(obj, dict):

        for key, value in obj.items():

            current = (
                f"{path}.{key}"
                if path
                else str(key)
            )

            if isinstance(value, str):

                results.append(
                    {
                        "json_path": current,
                        "value": value,
                    }
                )

            else:

                results.extend(
                    collect_strings(
                        value,
                        current,
                    )
                )

    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            current = f"{path}[{index}]"

            if isinstance(value, str):

                results.append(
                    {
                        "json_path": current,
                        "value": value,
                    }
                )

            else:

                results.extend(
                    collect_strings(
                        value,
                        current,
                    )
                )

    return results


def source_file_candidates(
    task_root: Path,
) -> list[Path]:

    return sorted(
        task_root.rglob("*.py")
    )


def inspect_source(
    path: Path,
) -> dict[str, Any]:

    result = {
        "path": str(path),
        "relative_path": str(
            path.relative_to(PROJECT_ROOT)
        ),
        "syntax_valid": False,
        "functions": [],
        "reference_hits": [],
        "error": None,
    }

    try:

        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        tree = ast.parse(
            source,
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

        patterns = [
            "joblib",
            "load(",
            "predict(",
            "predict_proba",
            "decision_function",
            "t2_class_weighted_tfidf_logreg",
            "t3_",
        ]

        for number, line in enumerate(
            source.splitlines(),
            start=1,
        ):

            lower = line.lower()

            matching = [
                pattern
                for pattern in patterns
                if pattern.lower() in lower
            ]

            if matching:

                result["reference_hits"].append(
                    {
                        "line": number,
                        "patterns": matching,
                        "text": line.strip(),
                    }
                )

    except Exception as exc:

        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

    return result


def resolve_artifact_paths(
    task: str,
    closure: Any,
    task_root: Path,
) -> list[dict[str, Any]]:

    candidates = []

    strings = collect_strings(closure)

    for item in strings:

        value = item["value"]

        if (
            ".joblib" not in value.lower()
            and "model" not in value.lower()
            and "artifact" not in value.lower()
        ):
            continue

        candidate = Path(value)

        possibilities = []

        if candidate.is_absolute():
            possibilities.append(candidate)
        else:
            possibilities.append(
                PROJECT_ROOT / candidate
            )
            possibilities.append(
                task_root / candidate
            )

        for possible in possibilities:

            if possible.exists():

                candidates.append(
                    {
                        "source_json_path": item[
                            "json_path"
                        ],
                        "raw_value": value,
                        "resolved_path": str(
                            possible
                        ),
                        "relative_path": str(
                            possible.relative_to(
                                PROJECT_ROOT
                            )
                        ),
                        "exists": True,
                        "size_bytes": possible.stat().st_size,
                    }
                )

    # Deduplicate
    unique = {}
    for item in candidates:
        unique[
            (
                item["source_json_path"],
                item["resolved_path"],
            )
        ] = item

    return list(unique.values())


def inspect_task(
    task: str,
    config: dict[str, Path],
) -> dict[str, Any]:

    closure_path = config["closure"]
    task_root = config["task_root"]

    result = {
        "task": task,
        "closure_path": str(closure_path),
        "closure_exists": closure_path.exists(),
        "closure_readable": False,
        "closure_summary": {},
        "reference_fields": [],
        "resolved_artifact_references": [],
        "joblib_files": [],
        "source_candidates": [],
        "resolution_status": "UNRESOLVED",
    }

    if not closure_path.exists():
        return result

    try:
        closure = load_json(closure_path)
        result["closure_readable"] = True

    except Exception as exc:

        result["closure_summary"] = {
            "read_error": (
                f"{type(exc).__name__}: {exc}"
            )
        }

        return result

    if isinstance(closure, dict):

        summary_keys = [
            "status",
            "closure_status",
            "final_status",
            "modeling_status",
            "supported_as",
            "not_supported_as",
            "decision",
            "selected_model",
            "final_model",
            "model_name",
            "artifact",
            "artifact_path",
            "model_path",
            "selected_artifact",
            "final_artifact",
            "frozen_artifact",
        ]

        for key in summary_keys:

            if key in closure:

                result["closure_summary"][
                    key
                ] = closure[key]

    result["reference_fields"] = (
        flatten_values(closure)
    )

    result["resolved_artifact_references"] = (
        resolve_artifact_paths(
            task,
            closure,
            task_root,
        )
    )

    for path in sorted(
        task_root.rglob("*.joblib")
    ):

        result["joblib_files"].append(
            {
                "path": str(path),
                "relative_path": str(
                    path.relative_to(
                        PROJECT_ROOT
                    )
                ),
                "size_bytes": path.stat().st_size,
            }
        )

    for path in source_file_candidates(
        task_root
    ):

        source = inspect_source(path)

        if (
            source["reference_hits"]
        ):

            result["source_candidates"].append(
                source
            )

    resolved = result[
        "resolved_artifact_references"
    ]

    if resolved:

        result[
            "resolution_status"
        ] = "RESOLVED"

    elif result[
        "closure_readable"
    ]:

        result[
            "resolution_status"
        ] = "CLOSURE_READABLE_BUT_ARTIFACT_REFERENCE_NOT_RESOLVED"

    return result


def main() -> None:

    print("=" * 70)
    print("FMP-06 OP-011B")
    print("T2/T3 FINAL MODEL SELECTION RESOLUTION")
    print("=" * 70)

    results = {}

    for task, config in TASKS.items():

        print()
        print("-" * 70)
        print(task)
        print("-" * 70)

        result = inspect_task(
            task,
            config,
        )

        results[task] = result

        print(
            f"closure_exists       = "
            f"{result['closure_exists']}"
        )

        print(
            f"closure_readable     = "
            f"{result['closure_readable']}"
        )

        print(
            f"joblib_files         = "
            f"{len(result['joblib_files'])}"
        )

        print(
            f"reference_fields     = "
            f"{len(result['reference_fields'])}"
        )

        print(
            f"resolved_references  = "
            f"{len(result['resolved_artifact_references'])}"
        )

        print(
            f"resolution_status    = "
            f"{result['resolution_status']}"
        )

        print()
        print("CLOSURE SUMMARY:")

        for key, value in result[
            "closure_summary"
        ].items():

            print(
                f"  {key} = {value}"
            )

        print()
        print("RESOLVED ARTIFACT REFERENCES:")

        for item in result[
            "resolved_artifact_references"
        ]:

            print(
                f"  {item['relative_path']}"
            )

            print(
                f"    source = "
                f"{item['source_json_path']}"
            )

            print(
                f"    value  = "
                f"{item['raw_value']}"
            )

        print()
        print("JOBLIB FILES:")

        for item in result[
            "joblib_files"
        ]:

            print(
                f"  {item['relative_path']}"
            )

    overall_status = (
        "PASS"
        if all(
            result["resolution_status"]
            == "RESOLVED"
            for result in results.values()
        )
        else "PARTIAL"
    )

    output = {
        "operation": "FMP-06 OP-011B",
        "operation_title": (
            "T2/T3 Final Model Selection Resolution"
        ),
        "status": overall_status,
        "purpose": (
            "Resolve authoritative frozen model artifacts "
            "from T2/T3 final closure records."
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
            "threshold_optimized": False,
            "universal_confidence_created": False,
            "universal_risk_created": False,
            "synthetic_target_created": False,
        },
        "next_gate": (
            "Proceed to FMP-06 OP-011 controlled "
            "single-ticket inference after frozen "
            "T1-T7 runtime interfaces are resolved."
        ),
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
        f"Overall status = {overall_status}"
    )

    for task, result in results.items():

        print(
            f"{task} = "
            f"{result['resolution_status']}"
        )

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
    print("FMP-06 OP-011B COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()