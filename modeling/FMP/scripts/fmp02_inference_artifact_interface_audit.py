#!/usr/bin/env python3

"""
FMP-02 / Operation 4
Deterministic Inference-Artifact Interface Audit

Purpose
-------
Read-only audit of retained T2-T7 final artifacts.

This operation:
- loads retained serialized artifacts where applicable
- inspects object types and inference interfaces
- inspects JSON model specifications
- records artifact metadata
- does NOT generate predictions
- does NOT retrain
- does NOT modify artifacts
- does NOT use evaluation data for selection

Output
------
modeling/FMP/metrics/fmp02_inference_artifact_interface_audit.json
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Any

import joblib


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
OUT = ROOT / "modeling/FMP/metrics/fmp02_inference_artifact_interface_audit.json"

TASKS = {
    "T2": {
        "artifacts": {
            "model": ROOT / "modeling/T2/models/t2_class_weighted_tfidf_logreg.joblib",
            "closure": ROOT / "modeling/T2/analysis/t2_final_closure.json",
            "metrics": ROOT / "modeling/T2/analysis/t2_final_test_metrics.json",
        }
    },
    "T3": {
        "artifacts": {
            "model": ROOT / "modeling/T3/models/t3_class_weighted_tfidf_logreg.joblib",
            "closure": ROOT / "modeling/T3/analysis/t3_final_closure.json",
            "metrics": ROOT / "modeling/T3/metrics/t3_final_test_metrics.json",
        }
    },
    "T4": {
        "artifacts": {
            "tfidf": ROOT / "modeling/T4/results/mod007_checkpoints/t4_mod007_tfidf.joblib",
            "neighbors": ROOT / "modeling/T4/results/mod007_checkpoints/t4_mod007_neighbors.joblib",
            "r1_tfidf": ROOT / "modeling/T4/results/r1_checkpoints/t4_r1_tfidf.joblib",
            "r1_svc": ROOT / "modeling/T4/results/r1_checkpoints/t4_r1_linear_svc.joblib",
            "closure": ROOT / "modeling/T4/results/t4_mod013_closure.json",
        }
    },
    "T5": {
        "artifacts": {
            "tfidf": ROOT / "modeling/T5/models/t5_mod005_tfidf.joblib",
            "logreg": ROOT / "modeling/T5/models/t5_mod005_logreg.joblib",
            "calibrated_pipeline": ROOT / "modeling/T5/models/t5_mod007_calibrated_tfidf.joblib",
            "calibration_models": ROOT / "modeling/T5/models/t5_mod007_calibration_models.joblib",
            "closure": ROOT / "modeling/T5/metrics/t5_mod011_final_closure.json",
        }
    },
    "T6": {
        "artifacts": {
            "tfidf": ROOT / "modeling/T6/models/t6_mod004_tfidf_vectorizer.joblib",
            "hybrid_results": ROOT / "modeling/T6/metrics/t6_mod010_corrected_hybrid_results.json",
            "hybrid_rankings": ROOT / "modeling/T6/metrics/t6_mod010_corrected_hybrid_query_rankings.csv",
            "direct_reconciliation": ROOT / "modeling/T6/metrics/t6_mod010_direct_score_reconciliation.json",
            "closure": ROOT / "modeling/T6/metrics/t6_final_closure.json",
        }
    },
    "T7": {
        "artifacts": {
            "lognormal_spec": ROOT / "modeling/T7/metrics/t7_mod010_log_normal_aft_model.json",
            "weibull_spec": ROOT / "modeling/T7/metrics/t7_mod007_weibull_aft_model.json",
            "comparison": ROOT / "modeling/T7/metrics/t7_mod011_final_model_comparison_audit.json",
            "evaluation_predictions": ROOT / "modeling/T7/derived/t7_mod010_evaluation_predictions.csv",
            "closure": ROOT / "modeling/T7/metrics/t7_mod012_final_closure.json",
        }
    },
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def json_summary(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text())

        if isinstance(data, dict):
            keys = list(data.keys())
            return {
                "json_type": "dict",
                "top_level_keys": keys[:100],
                "top_level_key_count": len(keys),
            }

        if isinstance(data, list):
            return {
                "json_type": "list",
                "length": len(data),
            }

        return {
            "json_type": type(data).__name__,
        }

    except Exception as exc:
        return {
            "json_type": "ERROR",
            "error": f"{type(exc).__name__}: {exc}",
        }


def object_interface(obj: Any) -> dict[str, Any]:
    methods = [
        "predict",
        "predict_proba",
        "decision_function",
        "transform",
        "fit",
        "fit_transform",
        "kneighbors",
    ]

    return {
        "python_type": f"{type(obj).__module__}.{type(obj).__name__}",
        "interfaces": {
            method: callable(getattr(obj, method, None))
            for method in methods
        },
    }


def inspect_joblib(path: Path) -> dict[str, Any]:
    result = {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
        "sha256": sha256_file(path) if path.exists() else None,
    }

    if not path.exists():
        result["status"] = "MISSING"
        return result

    try:
        obj = joblib.load(path)

        result["status"] = "LOADED"
        result["object_interface"] = object_interface(obj)

        if isinstance(obj, dict):
            result["dict_keys"] = list(obj.keys())

            component_types = {}

            for key, value in obj.items():
                try:
                    component_types[key] = (
                        f"{type(value).__module__}.{type(value).__name__}"
                    )
                except Exception:
                    component_types[key] = "UNKNOWN"

            result["dict_component_types"] = component_types

            component_interfaces = {}

            for key, value in obj.items():
                component_interfaces[key] = object_interface(value)

            result["dict_component_interfaces"] = component_interfaces

    except Exception as exc:
        result["status"] = "LOAD_ERROR"
        result["error"] = f"{type(exc).__name__}: {exc}"

    return result


def inspect_json(path: Path) -> dict[str, Any]:
    result = {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
        "sha256": sha256_file(path) if path.exists() else None,
    }

    if not path.exists():
        result["status"] = "MISSING"
        return result

    summary = json_summary(path)

    if summary.get("json_type") == "ERROR":
        result["status"] = "LOAD_ERROR"
        result["summary"] = summary
    else:
        result["status"] = "READABLE"
        result["summary"] = summary

    return result


def inspect_csv(path: Path) -> dict[str, Any]:
    result = {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
        "sha256": sha256_file(path) if path.exists() else None,
    }

    if not path.exists():
        result["status"] = "MISSING"
        return result

    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            header = f.readline().rstrip("\n")
            second = f.readline().rstrip("\n")

        result["status"] = "READABLE"
        result["header"] = header
        result["sample_second_line_present"] = bool(second)

    except Exception as exc:
        result["status"] = "READ_ERROR"
        result["error"] = f"{type(exc).__name__}: {exc}"

    return result


def inspect_artifact(label: str, path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()

    if suffix == ".joblib":
        result = inspect_joblib(path)
    elif suffix == ".json":
        result = inspect_json(path)
    elif suffix == ".csv":
        result = inspect_csv(path)
    else:
        result = {
            "path": str(path),
            "exists": path.exists(),
            "status": "UNSUPPORTED_EXTENSION",
        }

    result["label"] = label
    return result


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    report: dict[str, Any] = {
        "operation": "FMP-02-OP-004",
        "title": "Deterministic Inference-Artifact Interface Audit",
        "read_only": True,
        "prediction_generated": False,
        "retraining_performed": False,
        "evaluation_selection_performed": False,
        "artifact_modification_performed": False,
        "tasks": {},
    }

    print("=" * 80)
    print("FMP-02 / OPERATION 4 — INFERENCE-ARTIFACT INTERFACE AUDIT")
    print("=" * 80)

    for task, config in TASKS.items():
        print()
        print("-" * 80)
        print(task)
        print("-" * 80)

        task_report = {}

        for label, path in config["artifacts"].items():
            print(f"{label}: ", end="", flush=True)

            result = inspect_artifact(label, path)

            if result.get("status") in {"LOADED", "READABLE"}:
                print(result["status"])
            else:
                print(result.get("status", "UNKNOWN"))

            task_report[label] = result

        report["tasks"][task] = task_report

    OUT.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print()
    print("=" * 80)
    print("REPORT WRITTEN")
    print("=" * 80)
    print(OUT)

    print()
    print("Read-only controls:")
    print("  model loaded for inspection only: YES")
    print("  prediction generated: NO")
    print("  model retrained: NO")
    print("  evaluation used for selection: NO")
    print("  artifact modified: NO")

    print()
    print("STATUS: COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()