#!/usr/bin/env python3

"""
FMP-06 OP-011D
Frozen T2/T3 Artifact Binding

Read-only targeted audit.

Binds:
    model operation
        ->
    exact artifact
        ->
    preprocessing
        ->
    inference method

No model loading.
No inference.
No training.
No artifact modification.
"""

from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

MODELING_ROOT = PROJECT_ROOT / "modeling"

OUTPUT_PATH = (
    MODELING_ROOT
    / "FMP"
    / "metrics"
    / "fmp06_op011d_frozen_t2_t3_artifact_binding.json"
)


TARGETS = {
    "T2": {
        "operation": "T2-MOD-007",
        "task_root": MODELING_ROOT / "T2",
        "known_candidates": [
            MODELING_ROOT
            / "T2"
            / "models"
            / "t2_class_weighted_tfidf_logreg.joblib",
        ],
        "evidence_files": [
            MODELING_ROOT
            / "T2"
            / "analysis"
            / "t2_final_model_selection.json",
            MODELING_ROOT
            / "T2"
            / "analysis"
            / "t2_final_closure.json",
            MODELING_ROOT
            / "T2"
            / "logs"
            / "t2_class_weighted_run.json",
            MODELING_ROOT
            / "T2"
            / "metrics"
            / "t2_class_weighted_metrics.json",
        ],
        "search_terms": [
            "T2-MOD-007",
            "t2_class_weighted_tfidf_logreg",
            "joblib",
            "TfidfVectorizer",
            "LogisticRegression",
            "predict(",
            "predict_proba",
            "fit(",
        ],
    },
    "T3": {
        "operation": "T3-MOD-008",
        "task_root": MODELING_ROOT / "T3",
        "known_candidates": [
            MODELING_ROOT
            / "T3"
            / "models"
            / "t3_baseline_tfidf_logreg.joblib",
            MODELING_ROOT
            / "T3"
            / "models"
            / "t3_class_weighted_tfidf_logreg.joblib",
            MODELING_ROOT
            / "T3"
            / "models"
            / "t3_linear_svm.joblib",
            MODELING_ROOT
            / "T3"
            / "models"
            / "t3_svm_class_weighted.joblib",
            MODELING_ROOT
            / "T3"
            / "models"
            / "t3_word_char_tfidf_logreg.joblib",
        ],
        "evidence_files": [
            MODELING_ROOT
            / "T3"
            / "analysis"
            / "t3_classical_model_comparison.json",
            MODELING_ROOT
            / "T3"
            / "analysis"
            / "t3_final_closure.json",
            MODELING_ROOT
            / "T3"
            / "analysis"
            / "t3_final_generalization_analysis.json",
            MODELING_ROOT
            / "T3"
            / "metrics"
            / "t3_final_test_metrics.json",
        ],
        "search_terms": [
            "T3-MOD-008",
            "joblib",
            "TfidfVectorizer",
            "LogisticRegression",
            "LinearSVC",
            "predict(",
            "predict_proba",
            "word",
            "char",
        ],
    },
}


def load_json(path: Path):
    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


def flatten_strings(
    obj,
    path="",
):
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
                        "path": current,
                        "value": value,
                    }
                )

            else:

                results.extend(
                    flatten_strings(
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
                        "path": current,
                        "value": value,
                    }
                )

            else:

                results.extend(
                    flatten_strings(
                        value,
                        current,
                    )
                )

    return results


def inspect_evidence_file(
    path: Path,
    terms: list[str],
):
    result = {
        "path": str(
            path.relative_to(PROJECT_ROOT)
        ),
        "exists": path.exists(),
        "matches": [],
    }

    if not path.exists():
        return result

    try:
        obj = load_json(path)

    except Exception as exc:
        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )
        return result

    for item in flatten_strings(obj):

        value = item["value"]

        matches = [
            term
            for term in terms
            if term.lower() in value.lower()
        ]

        if matches:

            result["matches"].append(
                {
                    "json_path": item["path"],
                    "value": value,
                    "terms": matches,
                }
            )

    return result


def inspect_source(
    task_root: Path,
    operation: str,
    terms: list[str],
):
    results = []

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

        matches = []

        for number, line in enumerate(
            source.splitlines(),
            start=1,
        ):

            found = [
                term
                for term in terms
                if term.lower() in line.lower()
            ]

            if found:

                matches.append(
                    {
                        "line": number,
                        "text": line.strip(),
                        "terms": found,
                    }
                )

        if matches:

            results.append(
                {
                    "path": str(
                        path.relative_to(
                            PROJECT_ROOT
                        )
                    ),
                    "matches": matches,
                }
            )

    return results


def inspect_task(
    task: str,
    config: dict,
):

    evidence = []

    for path in config["evidence_files"]:

        evidence.append(
            inspect_evidence_file(
                path,
                config["search_terms"],
            )
        )

    source = inspect_source(
        config["task_root"],
        config["operation"],
        config["search_terms"],
    )

    candidate_inventory = []

    for path in config["known_candidates"]:

        candidate_inventory.append(
            {
                "path": str(
                    path.relative_to(
                        PROJECT_ROOT
                    )
                ),
                "exists": path.exists(),
                "size_bytes": (
                    path.stat().st_size
                    if path.exists()
                    else None
                ),
            }
        )

    return {
        "task": task,
        "operation": config["operation"],
        "candidate_artifacts": candidate_inventory,
        "evidence_files": evidence,
        "implementation_source_matches": source,
    }


def main():

    print("=" * 70)
    print("FMP-06 OP-011D")
    print("FROZEN T2/T3 ARTIFACT BINDING")
    print("=" * 70)

    results = {}

    for task, config in TARGETS.items():

        print()
        print("-" * 70)
        print(task)
        print("-" * 70)

        result = inspect_task(
            task,
            config,
        )

        results[task] = result

        existing = [
            item
            for item in result[
                "candidate_artifacts"
            ]
            if item["exists"]
        ]

        print(
            f"operation = "
            f"{config['operation']}"
        )

        print(
            f"candidate_artifacts_existing = "
            f"{len(existing)}"
        )

        print(
            f"evidence_files = "
            f"{len(result['evidence_files'])}"
        )

        print(
            f"source_files_with_matches = "
            f"{len(result['implementation_source_matches'])}"
        )

        print()
        print("EXISTING CANDIDATE ARTIFACTS:")

        for item in existing:
            print(
                f"  {item['path']}"
            )

        print()
        print("EVIDENCE MATCHES:")

        for item in result[
            "evidence_files"
        ]:

            if not item.get("matches"):
                continue

            print(
                f"  {item['path']}"
            )

            for match in item["matches"]:

                print(
                    f"    {match['json_path']} "
                    f"= {match['value']}"
                )

        print()
        print("IMPLEMENTATION MATCHES:")

        for source in result[
            "implementation_source_matches"
        ]:

            print(
                f"  {source['path']}"
            )

            for match in source["matches"][:20]:

                print(
                    f"    L{match['line']}: "
                    f"{match['text']}"
                )

    output = {
        "operation": "FMP-06 OP-011D",
        "operation_title": (
            "Frozen T2/T3 Artifact Binding"
        ),
        "status": "PASS",
        "purpose": (
            "Establish exact frozen T2/T3 artifact and "
            "implementation binding before inference."
        ),
        "inference_performed": False,
        "retraining_performed": False,
        "artifacts_modified": False,
        "tasks": results,
        "safeguards": {
            "prediction_generated": False,
            "model_loaded": False,
            "model_fitted": False,
            "locked_test_used": False,
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
        "Model loaded = False"
    )

    print(
        "Retraining performed = False"
    )

    print(
        "Artifacts modified = False"
    )

    print("=" * 70)
    print("FMP-06 OP-011D COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()