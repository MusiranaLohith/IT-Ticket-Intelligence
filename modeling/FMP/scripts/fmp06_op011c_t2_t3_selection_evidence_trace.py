#!/usr/bin/env python3

"""
FMP-06 OP-011C
T2/T3 Selection-Evidence Trace

Purpose
-------
Trace the existing T2/T3 model-selection evidence to establish the
authoritative frozen model artifact without relying on filenames alone.

Read-only:
    - JSON inspection only
    - source-text inspection only

No:
    - model loading
    - inference
    - training
    - calibration
    - threshold selection
    - artifact modification
"""

from __future__ import annotations

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
    / "fmp06_op011c_t2_t3_selection_evidence_trace.json"
)


SEARCH_TERMS = [
    "selected",
    "selection",
    "final_model",
    "final model",
    "winner",
    "chosen",
    "chosen_model",
    "selected_model",
    "T2-MOD-007",
    "T3-MOD-008",
    "T2-MOD",
    "T3-MOD",
    "class-weighted",
    "class weighted",
    "tf-idf",
    "word-char",
    "word char",
    "svm",
    "logistic",
]


def load_json(path: Path) -> Any:

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:

        return json.load(handle)


def flatten(
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

            if isinstance(value, (str, int, float, bool)):

                results.append(
                    {
                        "json_path": current,
                        "key": str(key),
                        "value": value,
                    }
                )

            results.extend(
                flatten(
                    value,
                    current,
                )
            )

    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            current = f"{path}[{index}]"

            if isinstance(value, (str, int, float, bool)):

                results.append(
                    {
                        "json_path": current,
                        "key": str(index),
                        "value": value,
                    }
                )

            results.extend(
                flatten(
                    value,
                    current,
                )
            )

    return results


def term_matches(
    value: Any,
) -> list[str]:

    if not isinstance(value, str):
        value = str(value)

    lowered = value.lower()

    return [
        term
        for term in SEARCH_TERMS
        if term.lower() in lowered
    ]


def inspect_json(
    path: Path,
) -> dict[str, Any]:

    result = {
        "path": str(path),
        "relative_path": str(
            path.relative_to(PROJECT_ROOT)
        ),
        "readable": False,
        "top_level_type": None,
        "matched_fields": [],
        "error": None,
    }

    try:

        obj = load_json(path)

        result["readable"] = True
        result["top_level_type"] = type(obj).__name__

        for item in flatten(obj):

            matches = term_matches(
                item["value"]
            )

            if matches:

                result["matched_fields"].append(
                    {
                        **item,
                        "matched_terms": matches,
                    }
                )

    except Exception as exc:

        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

    return result


def inspect_task(
    task: str,
) -> dict[str, Any]:

    task_root = MODELING_ROOT / task

    result = {
        "task": task,
        "task_root": str(task_root),
        "json_files": [],
        "matching_json_files": [],
        "text_matches": [],
    }

    if not task_root.exists():
        return result

    for path in sorted(
        task_root.rglob("*.json")
    ):

        inspection = inspect_json(path)

        result["json_files"].append(
            inspection
        )

        if inspection["matched_fields"]:
            result["matching_json_files"].append(
                inspection
            )

    # Also inspect source text, but only for selection references.
    for path in sorted(
        task_root.rglob("*.py")
    ):

        try:

            source = path.read_text(
                encoding="utf-8",
                errors="replace",
            )

        except Exception:
            continue

        for number, line in enumerate(
            source.splitlines(),
            start=1,
        ):

            matches = term_matches(line)

            if matches:

                result["text_matches"].append(
                    {
                        "relative_path": str(
                            path.relative_to(
                                PROJECT_ROOT
                            )
                        ),
                        "line": number,
                        "matched_terms": matches,
                        "text": line.strip(),
                    }
                )

    return result


def identify_strong_evidence(
    task_result: dict[str, Any],
) -> list[dict[str, Any]]:

    strong = []

    for file_result in task_result[
        "matching_json_files"
    ]:

        for field in file_result[
            "matched_fields"
        ]:

            value = str(
                field["value"]
            ).lower()

            matched = field[
                "matched_terms"
            ]

            # Strong selection evidence requires explicit selection
            # terminology rather than merely mentioning a model.
            explicit_selection_terms = {
                "selected",
                "selection",
                "final_model",
                "selected_model",
                "chosen",
                "chosen_model",
                "winner",
                "t2-mod-007",
                "t3-mod-008",
            }

            if any(
                term.lower()
                in explicit_selection_terms
                for term in matched
            ):

                strong.append(
                    {
                        "file": file_result[
                            "relative_path"
                        ],
                        "json_path": field[
                            "json_path"
                        ],
                        "key": field["key"],
                        "value": field["value"],
                        "matched_terms": matched,
                    }
                )

    return strong


def main() -> None:

    print("=" * 70)
    print("FMP-06 OP-011C")
    print("T2/T3 SELECTION-EVIDENCE TRACE")
    print("=" * 70)

    results = {}

    for task in ["T2", "T3"]:

        print()
        print("-" * 70)
        print(task)
        print("-" * 70)

        result = inspect_task(task)

        result["strong_selection_evidence"] = (
            identify_strong_evidence(result)
        )

        results[task] = result

        print(
            f"JSON files inspected = "
            f"{len(result['json_files'])}"
        )

        print(
            f"JSON files with matches = "
            f"{len(result['matching_json_files'])}"
        )

        print(
            f"Strong selection evidence = "
            f"{len(result['strong_selection_evidence'])}"
        )

        print()
        print("STRONG SELECTION EVIDENCE:")

        for item in result[
            "strong_selection_evidence"
        ]:

            print(
                f"  FILE: {item['file']}"
            )

            print(
                f"  PATH: {item['json_path']}"
            )

            print(
                f"  KEY:  {item['key']}"
            )

            print(
                f"  VALUE: {item['value']}"
            )

            print(
                f"  TERMS: "
                f"{item['matched_terms']}"
            )

            print()

    output = {
        "operation": "FMP-06 OP-011C",
        "operation_title": (
            "T2/T3 Selection-Evidence Trace"
        ),
        "status": "PASS",
        "purpose": (
            "Trace authoritative model-selection evidence "
            "before controlled runtime inference."
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

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for task, result in results.items():

        print(
            f"{task}: "
            f"{len(result['strong_selection_evidence'])} "
            f"strong selection evidence items"
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
    print("FMP-06 OP-011C COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()