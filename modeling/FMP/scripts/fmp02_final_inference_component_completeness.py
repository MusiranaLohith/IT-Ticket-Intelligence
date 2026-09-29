#!/usr/bin/env python3

"""
FMP-02 / Operation 5
Final Inference-Component Completeness Audit

Read-only targeted audit.

Purpose:
    Determine whether the components required for deterministic final
    inference are present for T2-T7.

No predictions.
No retraining.
No evaluation selection.
No artifact modification.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
OUT = ROOT / "modeling/FMP/metrics/fmp02_final_inference_component_completeness.json"


REQUIRED = {
    "T2": [
        (
            "final_model",
            ROOT / "modeling/T2/models/t2_class_weighted_tfidf_logreg.joblib",
        ),
        (
            "closure",
            ROOT / "modeling/T2/analysis/t2_final_closure.json",
        ),
        (
            "test_metrics",
            ROOT / "modeling/T2/analysis/t2_final_test_metrics.json",
        ),
    ],

    "T3": [
        (
            "final_model",
            ROOT / "modeling/T3/models/t3_class_weighted_tfidf_logreg.joblib",
        ),
        (
            "closure",
            ROOT / "modeling/T3/analysis/t3_final_closure.json",
        ),
        (
            "test_metrics",
            ROOT / "modeling/T3/metrics/t3_final_test_metrics.json",
        ),
    ],

    "T4": [
        (
            "mod007_tfidf",
            ROOT / "modeling/T4/results/mod007_checkpoints/t4_mod007_tfidf.joblib",
        ),
        (
            "mod007_neighbors",
            ROOT / "modeling/T4/results/mod007_checkpoints/t4_mod007_neighbors.joblib",
        ),
        (
            "r1_tfidf",
            ROOT / "modeling/T4/results/r1_checkpoints/t4_r1_tfidf.joblib",
        ),
        (
            "r1_linear_svc",
            ROOT / "modeling/T4/results/r1_checkpoints/t4_r1_linear_svc.joblib",
        ),
        (
            "closure",
            ROOT / "modeling/T4/results/t4_mod013_closure.json",
        ),
    ],

    "T5": [
        (
            "tfidf",
            ROOT / "modeling/T5/models/t5_mod005_tfidf.joblib",
        ),
        (
            "logreg",
            ROOT / "modeling/T5/models/t5_mod005_logreg.joblib",
        ),
        (
            "calibrated_pipeline",
            ROOT / "modeling/T5/models/t5_mod007_calibrated_tfidf.joblib",
        ),
        (
            "calibration_models",
            ROOT / "modeling/T5/models/t5_mod007_calibration_models.joblib",
        ),
        (
            "closure",
            ROOT / "modeling/T5/metrics/t5_mod011_final_closure.json",
        ),
    ],

    "T6": [
        (
            "lexical_tfidf",
            ROOT / "modeling/T6/models/t6_mod004_tfidf_vectorizer.joblib",
        ),
        (
            "corrected_hybrid_results",
            ROOT / "modeling/T6/metrics/t6_mod010_corrected_hybrid_results.json",
        ),
        (
            "corrected_hybrid_rankings",
            ROOT / "modeling/T6/metrics/t6_mod010_corrected_hybrid_query_rankings.csv",
        ),
        (
            "direct_score_reconciliation",
            ROOT / "modeling/T6/metrics/t6_mod010_direct_score_reconciliation.json",
        ),
        (
            "closure",
            ROOT / "modeling/T6/metrics/t6_final_closure.json",
        ),
    ],

    "T7": [
        (
            "lognormal_model_spec",
            ROOT / "modeling/T7/metrics/t7_mod010_log_normal_aft_model.json",
        ),
        (
            "weibull_model_spec",
            ROOT / "modeling/T7/metrics/t7_mod007_weibull_aft_model.json",
        ),
        (
            "final_model_comparison",
            ROOT / "modeling/T7/metrics/t7_mod011_final_model_comparison_audit.json",
        ),
        (
            "evaluation_predictions",
            ROOT / "modeling/T7/derived/t7_mod010_evaluation_predictions.csv",
        ),
        (
            "closure",
            ROOT / "modeling/T7/metrics/t7_mod012_final_closure.json",
        ),
    ],
}


# Targeted filename search terms only.
# This intentionally avoids broad recursive filesystem scanning.
TARGET_TERMS = {
    "T6": [
        "minilm",
        "sentence",
        "semantic",
        "embedding",
        "transformer",
        "encoder",
    ],
    "T7": [
        "aft",
        "log_normal",
        "lognormal",
        "weibull",
        "model",
        "lifelines",
    ],
}


def targeted_candidates(task: str) -> list[str]:
    task_root = ROOT / f"modeling/{task}"

    if not task_root.exists():
        return []

    terms = TARGET_TERMS.get(task, [])

    matches = []

    # Limited depth traversal.
    # We inspect only task-local files and ignore huge CSV contents.
    for path in task_root.rglob("*"):
        if not path.is_file():
            continue

        if "__pycache__" in path.parts:
            continue

        name = path.name.lower()

        if any(term in name for term in terms):
            matches.append(str(path))

    return sorted(matches)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "operation": "FMP-02-OP-005",
        "title": "Final Inference-Component Completeness Audit",
        "read_only": True,
        "prediction_generated": False,
        "retraining_performed": False,
        "evaluation_selection_performed": False,
        "artifact_modified": False,
        "tasks": {},
    }

    print("=" * 80)
    print("FMP-02 / OPERATION 5")
    print("FINAL INFERENCE-COMPONENT COMPLETENESS AUDIT")
    print("=" * 80)

    for task, requirements in REQUIRED.items():

        print()
        print("-" * 80)
        print(task)
        print("-" * 80)

        task_report = {
            "required_components": [],
            "missing_required_components": [],
            "targeted_candidate_files": [],
        }

        for label, path in requirements:

            exists = path.exists()

            record = {
                "label": label,
                "path": str(path),
                "exists": exists,
                "size_bytes": path.stat().st_size if exists else None,
            }

            task_report["required_components"].append(record)

            if exists:
                print(f"{label}: FOUND")
            else:
                print(f"{label}: MISSING")
                task_report["missing_required_components"].append(record)

        if task in TARGET_TERMS:
            candidates = targeted_candidates(task)

            task_report["targeted_candidate_files"] = candidates

            print()
            print("Targeted candidate files:")

            if candidates:
                for candidate in candidates:
                    print(f"  {candidate}")
            else:
                print("  NONE FOUND")

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
    print("  prediction generated: NO")
    print("  model retrained: NO")
    print("  evaluation used for selection: NO")
    print("  artifact modified: NO")

    print()
    print("STATUS: COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()