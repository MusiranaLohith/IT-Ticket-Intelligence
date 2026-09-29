from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OUTPUT = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "fmp06_op017_exact_frozen_runtime_binding_audit.json"
)


# Explicitly authoritative artifacts already established
# during previous FMP operations.
AUTHORITATIVE = {
    "T1": {
        "closure_candidates": [
            PROJECT_ROOT / "modeling/T1/analysis/t1_final_closure.json",
            PROJECT_ROOT / "modeling/T1/analysis/t1_it_support_3model_compare.json",
        ],
        "artifact_candidates": [
            PROJECT_ROOT / "modeling/T1/baselines/t1_it_support_char_svm.joblib",
        ],
        "model_operation_terms": [
            "t1",
            "char",
            "svm",
            "linear",
        ],
    },
    "T2": {
        "closure_candidates": [
            PROJECT_ROOT / "modeling/T2/analysis/t2_final_closure.json",
            PROJECT_ROOT / "modeling/T2/analysis/t2_final_model_selection.json",
        ],
        "artifact_candidates": [
            PROJECT_ROOT
            / "modeling/T2/models/t2_class_weighted_tfidf_logreg.joblib",
        ],
        "model_operation_terms": [
            "T2-MOD-007",
            "class_weighted",
            "logreg",
        ],
    },
    "T3": {
        "closure_candidates": [
            PROJECT_ROOT / "modeling/T3/analysis/t3_final_closure.json",
            PROJECT_ROOT / "modeling/T3/analysis/t3_locked_test_evaluation.json",
        ],
        "artifact_candidates": [
            PROJECT_ROOT
            / "modeling/T3/models/t3_class_weighted_tfidf_logreg.joblib",
        ],
        "model_operation_terms": [
            "T3-MOD-008",
            "class_weighted",
            "logreg",
        ],
    },
    "T4": {
        "closure_candidates": [
            PROJECT_ROOT / "modeling/T4/results/t4_mod013_closure.json",
            PROJECT_ROOT / "modeling/T4/results/t4_mod010_comparison.json",
        ],
        "artifact_candidates": [],
        "model_operation_terms": [
            "T4",
            "mod013",
            "mod010",
            "ranking",
            "retrieval",
            "assignee",
        ],
    },
    "T5": {
        "closure_candidates": [
            PROJECT_ROOT / "modeling/T5/metrics/t5_mod011_final_closure.json",
            PROJECT_ROOT / "modeling/T5/metrics/t5_mod009_locked_evaluation_metrics.json",
        ],
        "artifact_candidates": [
            PROJECT_ROOT / "modeling/T5/models/t5_mod005_tfidf.joblib",
            PROJECT_ROOT / "modeling/T5/models/t5_mod005_logreg.joblib",
            PROJECT_ROOT / "modeling/T5/models/t5_mod007_calibrated_tfidf.joblib",
            PROJECT_ROOT / "modeling/T5/models/t5_mod007_calibration_models.joblib",
        ],
        "model_operation_terms": [
            "T5",
            "mod011",
            "calibr",
            "duplicate",
            "sigmoid",
            "isotonic",
        ],
    },
    "T6": {
        "closure_candidates": [
            PROJECT_ROOT / "modeling/T6/metrics/t6_final_closure.json",
            PROJECT_ROOT / "modeling/T6/metrics/t6_mod010_corrected_hybrid_results.json",
            PROJECT_ROOT / "modeling/T6/metrics/t6_mod010_final_comparison.json",
        ],
        "artifact_candidates": [],
        "model_operation_terms": [
            "T6",
            "MOD-010",
            "mod010",
            "hybrid",
            "retrieval",
            "semantic",
            "lexical",
        ],
    },
    "T7": {
        "closure_candidates": [
            PROJECT_ROOT / "modeling/T7/metrics/t7_mod012_final_closure.json",
            PROJECT_ROOT / "modeling/T7/metrics/t7_mod011_final_model_comparison_audit.json",
        ],
        "artifact_candidates": [],
        "model_operation_terms": [
            "T7",
            "MOD-012",
            "mod012",
            "survival",
            "lognormal",
            "weibull",
            "aft",
        ],
    },
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> tuple[bool, Any, str]:
    if not path.exists():
        return False, None, "FILE_NOT_FOUND"

    try:
        return (
            True,
            json.loads(
                path.read_text(
                    encoding="utf-8",
                    errors="replace",
                )
            ),
            "",
        )
    except Exception as exc:
        return False, None, str(exc)


def json_strings(
    obj: Any,
    prefix: str = "",
) -> list[dict[str, str]]:
    """
    Recursively collect string-valued JSON leaves with their paths.
    """
    records: list[dict[str, str]] = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            child = (
                f"{prefix}.{key}"
                if prefix
                else str(key)
            )
            records.extend(
                json_strings(value, child)
            )

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            child = (
                f"{prefix}[{index}]"
                if prefix
                else f"[{index}]"
            )
            records.extend(
                json_strings(value, child)
            )

    elif isinstance(obj, str):
        records.append(
            {
                "path": prefix,
                "value": obj,
            }
        )

    return records


def inspect_closure(
    task: str,
    path: Path,
) -> dict[str, Any]:

    readable, data, error = read_json(path)

    result = {
        "file": rel(path),
        "exists": path.exists(),
        "readable": readable,
        "error": error,
        "status_fields": {},
        "artifact_like_strings": [],
        "model_like_strings": [],
        "selection_like_strings": [],
    }

    if not readable:
        return result

    strings = json_strings(data)

    for item in strings:
        value = item["value"]
        lowered = value.lower()
        field = item["path"].lower()

        if any(
            token in lowered
            for token in (
                ".joblib",
                ".pkl",
                ".pickle",
                "modeling/",
                "models/",
                "baselines/",
            )
        ):
            result["artifact_like_strings"].append(item)

        if any(
            token in lowered
            for token in (
                "t1-mod",
                "t2-mod",
                "t3-mod",
                "t4-mod",
                "t5-mod",
                "t6-mod",
                "t7-mod",
                "mod010",
                "mod011",
                "mod012",
                "class_weighted",
                "logreg",
                "svm",
                "hybrid",
                "survival",
            )
        ):
            result["model_like_strings"].append(item)

        if any(
            token in field
            for token in (
                "selection",
                "selected",
                "final_model",
                "final_candidate",
                "operation",
            )
        ):
            result["selection_like_strings"].append(item)

        if any(
            token in field
            for token in (
                "status",
                "closure",
            )
        ):
            result["status_fields"][item["path"]] = value

    return result


def inspect_joblib_metadata(
    path: Path,
) -> dict[str, Any]:

    result = {
        "file": rel(path),
        "exists": path.exists(),
        "size_bytes": (
            path.stat().st_size
            if path.exists()
            else None
        ),
        "loaded": False,
        "type": None,
        "metadata_only": True,
    }

    # Deliberately do NOT joblib.load().
    # Runtime loading is prohibited in this audit.
    return result


def python_files(task: str) -> list[Path]:

    task_dir = PROJECT_ROOT / "modeling" / task

    if not task_dir.exists():
        return []

    return sorted(
        path
        for path in task_dir.rglob("*.py")
        if "__pycache__" not in path.parts
    )


def source_evidence(
    task: str,
    terms: list[str],
) -> list[dict[str, Any]]:

    matches: list[dict[str, Any]] = []

    for path in python_files(task):

        try:
            source = path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        except Exception:
            continue

        lowered = source.lower()

        matched_terms = [
            term
            for term in terms
            if term.lower() in lowered
        ]

        if not matched_terms:
            continue

        try:
            tree = ast.parse(
                source,
                filename=str(path),
            )

            functions = sorted(
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

        except Exception:
            functions = []

        line_hits = []

        for number, line in enumerate(
            source.splitlines(),
            start=1,
        ):
            line_lower = line.lower()

            if any(
                term.lower() in line_lower
                for term in terms
            ):
                line_hits.append(
                    {
                        "line": number,
                        "text": line.strip()[:240],
                    }
                )

                if len(line_hits) >= 20:
                    break

        matches.append(
            {
                "file": rel(path),
                "matched_terms": matched_terms,
                "functions": functions,
                "line_evidence": line_hits,
            }
        )

    # Prefer files with more relevant terms.
    matches.sort(
        key=lambda item: (
            -len(item["matched_terms"]),
            str(item["file"]),
        )
    )

    return matches[:12]


def validate_explicit_artifacts(
    task: str,
    candidates: list[Path],
) -> list[dict[str, Any]]:

    return [
        inspect_joblib_metadata(path)
        for path in candidates
    ]


def task_summary(
    task: str,
    config: dict[str, Any],
) -> dict[str, Any]:

    closure_records = [
        inspect_closure(task, path)
        for path in config["closure_candidates"]
    ]

    artifact_records = validate_explicit_artifacts(
        task,
        config["artifact_candidates"],
    )

    implementation_records = source_evidence(
        task,
        config["model_operation_terms"],
    )

    existing_closures = [
        item
        for item in closure_records
        if item["readable"]
    ]

    existing_artifacts = [
        item
        for item in artifact_records
        if item["exists"]
    ]

    return {
        "closure_records": closure_records,
        "explicit_artifacts": artifact_records,
        "implementation_evidence": implementation_records,
        "binding_evidence": {
            "readable_closure_count": len(
                existing_closures
            ),
            "existing_explicit_artifact_count": len(
                existing_artifacts
            ),
            "implementation_evidence_count": len(
                implementation_records
            ),
        },
    }


def determine_status(
    task: str,
    result: dict[str, Any],
) -> str:

    evidence = result["binding_evidence"]

    closure_ok = (
        evidence["readable_closure_count"] > 0
    )

    implementation_ok = (
        evidence["implementation_evidence_count"] > 0
    )

    artifact_ok = (
        evidence["existing_explicit_artifact_count"] > 0
    )

    # T1-T3 have explicitly known frozen artifacts.
    if task in {"T1", "T2", "T3"}:
        if closure_ok and artifact_ok and implementation_ok:
            return "EXACT_BINDING_ESTABLISHED"

        return "BINDING_NOT_ESTABLISHED"

    # T5 has an explicit multi-artifact frozen pipeline.
    if task == "T5":
        if closure_ok and artifact_ok and implementation_ok:
            return "PIPELINE_ARTIFACT_BINDING_ESTABLISHED"

        return "BINDING_NOT_ESTABLISHED"

    # T4/T6/T7 need implementation + closure evidence.
    # Their authoritative closures may describe native
    # ranking/survival implementations rather than a single
    # joblib file.
    if closure_ok and implementation_ok:
        return "IMPLEMENTATION_BINDING_ESTABLISHED"

    return "BINDING_NOT_ESTABLISHED"


def main() -> None:

    print("=" * 72)
    print(
        "FMP-06 OP-017 — "
        "EXACT FROZEN RUNTIME BINDING AUDIT"
    )
    print("=" * 72)
    print()
    print("Mode: READ-ONLY")
    print("No joblib loading")
    print("No inference")
    print("No retraining")
    print("No artifact modification")
    print()

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = {
        "operation": "FMP-06 OP-017",
        "operation_type": (
            "READ_ONLY_EXACT_FROZEN_RUNTIME_BINDING_AUDIT"
        ),
        "project_root": str(PROJECT_ROOT),
        "tasks": {},
        "safeguards": {
            "joblib_loaded": False,
            "models_loaded": False,
            "inference_executed": False,
            "retraining": False,
            "artifact_modification": False,
            "threshold_created": False,
            "calibration_performed": False,
            "synthetic_input_created": False,
            "synthetic_target_created": False,
            "universal_confidence_created": False,
            "universal_risk_created": False,
        },
    }

    statuses = []

    for task, config in AUTHORITATIVE.items():

        print("-" * 72)
        print(task)

        result = task_summary(
            task,
            config,
        )

        status = determine_status(
            task,
            result,
        )

        result["binding_status"] = status

        report["tasks"][task] = result
        statuses.append(status)

        print(
            "  readable closures:",
            result["binding_evidence"][
                "readable_closure_count"
            ],
        )

        print(
            "  explicit artifacts:",
            result["binding_evidence"][
                "existing_explicit_artifact_count"
            ],
        )

        print(
            "  implementation evidence:",
            result["binding_evidence"][
                "implementation_evidence_count"
            ],
        )

        print(
            "  binding status:",
            status,
        )

        for artifact in result[
            "explicit_artifacts"
        ]:
            print(
                "    ARTIFACT:",
                artifact["file"],
                "exists=",
                artifact["exists"],
                "size=",
                artifact["size_bytes"],
            )

        for closure in result[
            "closure_records"
        ]:

            if not closure["readable"]:
                continue

            print(
                "    CLOSURE:",
                closure["file"],
            )

            for item in closure[
                "selection_like_strings"
            ][:5]:
                print(
                    "      SELECTION:",
                    item["path"],
                    "=",
                    item["value"][:180],
                )

            for item in closure[
                "artifact_like_strings"
            ][:5]:
                print(
                    "      ARTIFACT REF:",
                    item["path"],
                    "=",
                    item["value"][:180],
                )

        for implementation in result[
            "implementation_evidence"
        ][:5]:

            print(
                "    IMPLEMENTATION:",
                implementation["file"],
                "terms=",
                implementation["matched_terms"],
            )

            for line in implementation[
                "line_evidence"
            ][:3]:
                print(
                    "      LINE",
                    line["line"],
                    ":",
                    line["text"],
                )

        print()

    # This operation is considered PASS as an audit if it completed
    # without crashing. Individual binding states are reported
    # separately and are not silently upgraded.
    report["overall_status"] = "PASS"

    OUTPUT.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("=" * 72)
    print("OVERALL STATUS: PASS")
    print(f"OUTPUT: {OUTPUT}")
    print("=" * 72)


if __name__ == "__main__":
    main()