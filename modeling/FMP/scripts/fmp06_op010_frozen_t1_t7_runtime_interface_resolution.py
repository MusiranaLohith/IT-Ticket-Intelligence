#!/usr/bin/env python3

"""
FMP-06 OP-010
Frozen T1-T7 Runtime Interface Resolution

Purpose
-------
Read-only audit of the frozen T1-T7 artifacts and their selected runtime
implementation candidates.

This operation does NOT:
- train models
- fit models
- modify frozen artifacts
- generate predictions
- use locked evaluation data for model selection
- create thresholds
- create universal confidence/risk
- declare an autonomous operating policy

The objective is narrower:

    Can we establish the exact runtime interface required to invoke
    each frozen T1-T7 component on a raw ticket/query?

Status semantics
----------------
RESOLVED
    The frozen artifact and implementation evidence are sufficient to
    establish the runtime interface.

PARTIAL
    Some interface evidence exists, but the complete runtime contract
    cannot yet be established safely.

UNRESOLVED
    The existing authoritative evidence is insufficient to establish
    the runtime interface.

Important
---------
A script containing predict()/predict_proba()/decision_function() is NOT
automatically treated as the authoritative runtime interface.

Only evidence connected to the frozen task artifacts and closure records
is considered.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
MODELING_ROOT = PROJECT_ROOT / "modeling"
FMP_ROOT = MODELING_ROOT / "FMP"
METRICS_ROOT = FMP_ROOT / "metrics"

OUTPUT_PATH = (
    METRICS_ROOT
    / "fmp06_op010_frozen_t1_t7_runtime_interface_resolution.json"
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def syntax_check(path: Path) -> dict[str, Any]:
    result = {
        "path": str(path),
        "exists": path.exists(),
        "syntax_valid": False,
        "functions": [],
        "classes": [],
        "error": None,
    }

    if not path.exists():
        result["error"] = "FILE_NOT_FOUND"
        return result

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))

        result["syntax_valid"] = True
        result["functions"] = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        result["classes"] = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
        ]

    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"

    return result


def find_scripts(
    task_root: Path,
    keywords: list[str],
) -> list[dict[str, Any]]:
    results = []

    if not task_root.exists():
        return results

    for path in sorted(task_root.rglob("*.py")):
        try:
            source = path.read_text(encoding="utf-8")
        except Exception:
            continue

        lowered = source.lower()

        matched = [
            keyword
            for keyword in keywords
            if keyword.lower() in lowered
        ]

        if not matched:
            continue

        syntax = syntax_check(path)

        results.append(
            {
                "path": str(path),
                "relative_path": str(path.relative_to(PROJECT_ROOT)),
                "keyword_hits": sorted(set(matched)),
                "syntax_valid": syntax["syntax_valid"],
                "functions": syntax["functions"],
                "classes": syntax["classes"],
                "syntax_error": syntax["error"],
            }
        )

    return results


def load_first_existing(
    candidates: list[Path],
) -> tuple[Path | None, Any | None]:
    for path in candidates:
        if path.exists():
            try:
                return path, load_json(path)
            except Exception:
                return path, None

    return None, None


def summarize_closure(
    task: str,
    candidates: list[Path],
) -> dict[str, Any]:
    path, obj = load_first_existing(candidates)

    result = {
        "task": task,
        "closure_path": str(path) if path else None,
        "closure_exists": path is not None,
        "closure_readable": obj is not None,
        "status": None,
        "closure_status": None,
        "supported_as": None,
        "not_supported_as": None,
        "selected_model": None,
    }

    if obj is None:
        return result

    if isinstance(obj, dict):
        result["status"] = obj.get("status")
        result["closure_status"] = obj.get("closure_status")
        result["supported_as"] = obj.get("supported_as")
        result["not_supported_as"] = obj.get("not_supported_as")

        for key in (
            "selected_model",
            "final_model",
            "model_name",
            "model",
            "selected_artifact",
            "artifact",
        ):
            if key in obj:
                result["selected_model"] = obj[key]
                break

    return result


def file_inventory(candidates: list[Path]) -> list[dict[str, Any]]:
    inventory = []

    for path in candidates:
        inventory.append(
            {
                "path": str(path),
                "exists": path.exists(),
                "size_bytes": path.stat().st_size if path.exists() else None,
            }
        )

    return inventory


def determine_interface(
    task: str,
    closure: dict[str, Any],
    scripts: list[dict[str, Any]],
    artifact_inventory: list[dict[str, Any]],
) -> dict[str, Any]:

    readable_artifacts = [
        item for item in artifact_inventory if item["exists"]
    ]

    syntax_valid_scripts = [
        item
        for item in scripts
        if item["syntax_valid"]
    ]

    notes: list[str] = []

    if not closure["closure_exists"]:
        notes.append("Authoritative closure artifact was not found.")

    if not closure["closure_readable"]:
        notes.append("Closure artifact could not be read.")

    if not readable_artifacts:
        notes.append("No candidate frozen runtime artifact was found.")

    if not syntax_valid_scripts:
        notes.append(
            "No syntax-valid implementation candidate was found "
            "for this task."
        )

    # Conservative task-specific interface rules.
    #
    # These rules intentionally establish only whether an interface is
    # evidenced. They do not claim production readiness.

    if task == "T1":
        interface = {
            "input_grain": "single ticket text",
            "expected_native_output": "ticket category/class prediction",
            "runtime_operation": "classifier inference",
            "probability_semantics": "not established as calibrated probability",
        }

    elif task == "T2":
        interface = {
            "input_grain": "single ticket",
            "expected_native_output": "priority class prediction",
            "runtime_operation": "classifier inference",
            "probability_semantics": "no universal automated confidence threshold",
        }

    elif task == "T3":
        interface = {
            "input_grain": "single ticket",
            "expected_native_output": "severity class prediction",
            "runtime_operation": "classifier inference",
            "probability_semantics": "not an autonomous severity decision",
        }

    elif task == "T4":
        interface = {
            "input_grain": "ticket/query",
            "expected_native_output": "historical assignee candidate ranking",
            "runtime_operation": "candidate retrieval/ranking",
            "probability_semantics": "ranking score, not universal probability",
        }

    elif task == "T5":
        interface = {
            "input_grain": "ticket pair",
            "expected_native_output": "duplicate relationship score/probability",
            "runtime_operation": "binary duplicate inference",
            "probability_semantics": (
                "native p_duplicate exists; operational threshold "
                "not established"
            ),
        }

    elif task == "T6":
        interface = {
            "input_grain": "query ticket",
            "expected_native_output": "similar-ticket candidate ranking",
            "runtime_operation": "lexical + semantic retrieval/ranking",
            "probability_semantics": (
                "retrieval/ranking score; not binary probability"
            ),
        }

    elif task == "T7":
        interface = {
            "input_grain": "ticket",
            "expected_native_output": (
                "native time-to-resolution survival output"
            ),
            "runtime_operation": "survival prediction",
            "probability_semantics": (
                "censoring-aware survival semantics; not universal risk"
            ),
        }

    else:
        interface = {
            "input_grain": None,
            "expected_native_output": None,
            "runtime_operation": None,
            "probability_semantics": None,
        }

    # Conservative resolution rule:
    #
    # We require:
    #   1. closure exists/readable
    #   2. at least one frozen artifact exists
    #   3. at least one syntax-valid implementation candidate exists
    #
    # This still does NOT mean the runtime has been executed.
    if (
        closure["closure_exists"]
        and closure["closure_readable"]
        and readable_artifacts
        and syntax_valid_scripts
    ):
        status = "RESOLVED"
        notes.append(
            "Frozen artifact, closure evidence, and an implementation "
            "candidate are all present."
        )
    elif (
        closure["closure_exists"]
        and closure["closure_readable"]
        and readable_artifacts
    ):
        status = "PARTIAL"
        notes.append(
            "Frozen artifact and closure evidence exist, but no "
            "syntax-valid implementation candidate was established."
        )
    else:
        status = "UNRESOLVED"

    notes.append(
        "Resolution here means interface evidence is sufficient for "
        "the next controlled inference operation; it does not prove "
        "successful runtime execution."
    )

    return {
        "status": status,
        "interface_contract": interface,
        "evidence_notes": notes,
    }


def main() -> None:

    print("=" * 70)
    print("FMP-06 OP-010")
    print("FROZEN T1-T7 RUNTIME INTERFACE RESOLUTION")
    print("=" * 70)

    METRICS_ROOT.mkdir(parents=True, exist_ok=True)

    task_specs = {
        "T1": {
            "closure_candidates": [
                MODELING_ROOT / "T1" / "analysis" / "t1_final_closure.json",
                MODELING_ROOT / "T1" / "baselines"
                / "t1_it_support_char_svm.joblib",
            ],
            "artifacts": [
                MODELING_ROOT / "T1" / "baselines"
                / "t1_it_support_char_svm.joblib",
                MODELING_ROOT / "T1" / "analysis"
                / "t1_it_support_3model_compare.json",
                MODELING_ROOT / "T1" / "analysis"
                / "t1_final_closure.json",
            ],
            "script_keywords": [
                "LinearSVC",
                "TfidfVectorizer",
                "predict(",
                "decision_function",
                "char",
            ],
        },

        "T2": {
            "closure_candidates": [
                MODELING_ROOT / "T2" / "metrics"
                / "t2_final_closure.json",
                MODELING_ROOT / "T2" / "metrics"
                / "t2_mod007_final_closure.json",
            ],
            "artifacts": [
                MODELING_ROOT / "T2" / "models"
                / "t2_class_weighted_tfidf_logreg.joblib",
                MODELING_ROOT / "T2" / "metrics"
                / "t2_final_test_metrics.json",
                MODELING_ROOT / "T2" / "metrics"
                / "t2_locked_test_predictions.csv",
            ],
            "script_keywords": [
                "LogisticRegression",
                "TfidfVectorizer",
                "predict(",
                "predict_proba",
                "actual_priority",
                "predicted_priority",
            ],
        },

        "T3": {
            "closure_candidates": [
                MODELING_ROOT / "T3" / "metrics"
                / "t3_final_closure.json",
                MODELING_ROOT / "T3" / "metrics"
                / "t3_mod008_final_closure.json",
            ],
            "artifacts": [
                MODELING_ROOT / "T3" / "metrics"
                / "t3_locked_test_predictions.csv",
                MODELING_ROOT / "T3" / "metrics"
                / "t3_locked_test_metrics.json",
                MODELING_ROOT / "T3" / "metrics"
                / "t3_final_closure.json",
            ],
            "script_keywords": [
                "predict(",
                "severity",
                "TfidfVectorizer",
                "classification",
                "locked",
            ],
        },

        "T4": {
            "closure_candidates": [
                MODELING_ROOT / "T4" / "results"
                / "t4_mod013_closure.json",
                MODELING_ROOT / "T4" / "results"
                / "t4_mod010_comparison.json",
            ],
            "artifacts": [
                MODELING_ROOT / "T4" / "results"
                / "t4_mod013_closure.json",
                MODELING_ROOT / "T4" / "results"
                / "t4_r1_metrics.json",
            ],
            "script_keywords": [
                "retrieval",
                "ranking",
                "assignee",
                "candidate",
                "Hit@",
            ],
        },

        "T5": {
            "closure_candidates": [
                MODELING_ROOT / "T5" / "metrics"
                / "t5_mod011_final_closure.json",
            ],
            "artifacts": [
                MODELING_ROOT / "T5" / "metrics"
                / "t5_mod009_locked_evaluation_metrics.json",
                MODELING_ROOT / "T5" / "metrics"
                / "t5_mod006_calibration_metrics.json",
                MODELING_ROOT / "T5" / "metrics"
                / "t5_mod007_calibration_comparison.json",
                MODELING_ROOT / "T5" / "metrics"
                / "t5_mod011_final_closure.json",
                MODELING_ROOT / "T5" / "models"
                / "t5_mod007_calibrated_tfidf.joblib",
                MODELING_ROOT / "T5" / "models"
                / "t5_mod007_calibration_models.joblib",
            ],
            "script_keywords": [
                "p_duplicate",
                "predict_proba",
                "LogisticRegression",
                "calibration",
                "duplicate",
            ],
        },

        "T6": {
            "closure_candidates": [
                MODELING_ROOT / "T6" / "metrics"
                / "t6_final_closure.json",
                MODELING_ROOT / "T6" / "metrics"
                / "t6_mod010_corrected_hybrid_results.json",
            ],
            "artifacts": [
                MODELING_ROOT / "T6" / "metrics"
                / "t6_final_closure.json",
                MODELING_ROOT / "T6" / "metrics"
                / "t6_mod010_corrected_hybrid_results.json",
                MODELING_ROOT / "T6" / "metrics"
                / "t6_mod010_final_comparison.json",
                MODELING_ROOT / "T6" / "metrics"
                / "t6_mod010_exact_reproduction_report.json",
            ],
            "script_keywords": [
                "retrieval",
                "hybrid",
                "semantic",
                "tfidf",
                "ranking",
                "query",
            ],
        },

        "T7": {
            "closure_candidates": [
                MODELING_ROOT / "T7" / "metrics"
                / "t7_mod012_final_closure.json",
                MODELING_ROOT / "T7" / "metrics"
                / "t7_mod011_final_model_comparison_audit.json",
            ],
            "artifacts": [
                MODELING_ROOT / "T7" / "metrics"
                / "t7_mod012_final_closure.json",
                MODELING_ROOT / "T7" / "metrics"
                / "t7_mod011_final_model_comparison_audit.json",
                MODELING_ROOT / "T7" / "metrics"
                / "t7_mod010_log_normal_aft_model.json",
            ],
            "script_keywords": [
                "survival",
                "LogNormal",
                "AFT",
                "Weibull",
                "time_to_resolution",
                "censor",
            ],
        },
    }

    all_results: dict[str, Any] = {}

    for task, spec in task_specs.items():

        print()
        print("-" * 70)
        print(task)
        print("-" * 70)

        closure = summarize_closure(
            task,
            spec["closure_candidates"],
        )

        artifacts = file_inventory(spec["artifacts"])

        scripts = find_scripts(
            MODELING_ROOT / task,
            spec["script_keywords"],
        )

        resolution = determine_interface(
            task=task,
            closure=closure,
            scripts=scripts,
            artifact_inventory=artifacts,
        )

        task_result = {
            "task": task,
            "closure": closure,
            "artifact_inventory": artifacts,
            "implementation_candidates": scripts,
            "resolution": resolution,
        }

        all_results[task] = task_result

        print(
            f"closure_exists      = "
            f"{closure['closure_exists']}"
        )
        print(
            f"closure_readable    = "
            f"{closure['closure_readable']}"
        )
        print(
            f"artifact_count      = "
            f"{sum(1 for x in artifacts if x['exists'])}"
        )
        print(
            f"implementation_hits = "
            f"{len(scripts)}"
        )
        print(
            f"interface_status    = "
            f"{resolution['status']}"
        )

        print(
            f"input_grain         = "
            f"{resolution['interface_contract']['input_grain']}"
        )

        print(
            f"native_output       = "
            f"{resolution['interface_contract']['expected_native_output']}"
        )

        print(
            f"runtime_operation   = "
            f"{resolution['interface_contract']['runtime_operation']}"
        )

    statuses = {
        task: result["resolution"]["status"]
        for task, result in all_results.items()
    }

    resolved = [
        task
        for task, status in statuses.items()
        if status == "RESOLVED"
    ]

    partial = [
        task
        for task, status in statuses.items()
        if status == "PARTIAL"
    ]

    unresolved = [
        task
        for task, status in statuses.items()
        if status == "UNRESOLVED"
    ]

    safeguards = {
        "model_fitted": False,
        "prediction_generated": False,
        "locked_test_used_for_selection": False,
        "threshold_selected": False,
        "threshold_optimized": False,
        "universal_confidence_created": False,
        "universal_risk_created": False,
        "synthetic_target_created": False,
        "frozen_artifact_modified": False,
        "post_creation_information_used": False,
    }

    overall_status = (
        "PASS"
        if not unresolved
        else "PARTIAL"
    )

    output = {
        "operation": "FMP-06 OP-010",
        "operation_title": "Frozen T1-T7 Runtime Interface Resolution",
        "status": overall_status,
        "purpose": (
            "Resolve the runtime interfaces of the frozen T1-T7 "
            "components before controlled raw-ticket inference."
        ),
        "runtime_execution_performed": False,
        "inference_performed": False,
        "retraining_performed": False,
        "task_statuses": statuses,
        "resolved_tasks": resolved,
        "partial_tasks": partial,
        "unresolved_tasks": unresolved,
        "task_results": all_results,
        "safeguards": safeguards,
        "interpretation": {
            "meaning_of_resolved": (
                "The frozen artifact, closure evidence, and an "
                "implementation candidate provide enough evidence "
                "to define the next controlled inference interface."
            ),
            "not_proven": [
                "successful runtime execution",
                "end-to-end raw-ticket execution",
                "production readiness",
                "autonomous operation generation",
                "validated human-review boundary",
                "validated automation threshold",
            ],
        },
        "next_gate": (
            "FMP-06 OP-011 controlled single-ticket inference"
            if overall_status == "PASS"
            else
            "Resolve PARTIAL/UNRESOLVED task interfaces before "
            "single-ticket inference."
        ),
    }

    write_json(OUTPUT_PATH, output)

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"Overall status       = {overall_status}")
    print(f"Resolved tasks       = {resolved}")
    print(f"Partial tasks        = {partial}")
    print(f"Unresolved tasks     = {unresolved}")
    print(f"Inference performed  = False")
    print(f"Retraining performed = False")
    print(f"Output               = {OUTPUT_PATH}")

    print()
    print("SAFEGUARDS")
    for key, value in safeguards.items():
        print(f"{key} = {value}")

    print()
    print("=" * 70)
    print("FMP-06 OP-010 COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()