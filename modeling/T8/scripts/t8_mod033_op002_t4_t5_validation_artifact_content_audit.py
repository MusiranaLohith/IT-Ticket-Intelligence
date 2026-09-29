from pathlib import Path
import json


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OUTPUT = (
    ROOT
    / "modeling/T8/mod033"
    / "t8_mod033_op002_t4_t5_validation_artifact_content.json"
)

FILES = [
    ROOT / "modeling/T4/derived/t4_validation_report.json",
    ROOT / "modeling/T4/results/t4_mod007_full_results.json",
    ROOT / "modeling/T4/results/t4_mod007_retrieval_analysis.json",
    ROOT / "modeling/T4/results/t4_mod007_similarity_analysis.json",
    ROOT / "modeling/T4/results/t4_mod008_analysis.json",
    ROOT / "modeling/T4/results/t4_mod008_full.json",
    ROOT / "modeling/T4/results/t4_mod010_comparison.json",
    ROOT / "modeling/T4/results/t4_mod011_full.json",
    ROOT / "modeling/T4/results/t4_mod012_analysis.json",
    ROOT / "modeling/T4/results/t4_mod013_closure.json",
    ROOT / "modeling/T4/results/t4_r1_analysis.json",
    ROOT / "modeling/T4/results/t4_r1_metrics.json",
    ROOT / "modeling/T4/results/t4_r1_vs_mod007_analysis.json",

    ROOT / "modeling/T5/metrics/t5_mod005_validation_metrics.json",
    ROOT / "modeling/T5/metrics/t5_mod006_calibration_bins.json",
    ROOT / "modeling/T5/metrics/t5_mod006_calibration_metrics.json",
    ROOT / "modeling/T5/metrics/t5_mod007_calibration_comparison.json",
    ROOT / "modeling/T5/metrics/t5_mod009_locked_evaluation_metrics.json",
    ROOT / "modeling/T5/metrics/t5_mod010_generalization_analysis.json",
    ROOT / "modeling/T5/metrics/t5_mod011_final_closure.json",
]


PREDICTION_TERMS = {
    "prediction",
    "predictions",
    "predicted",
    "probability",
    "probabilities",
    "score",
    "scores",
    "ranking",
    "rankings",
    "candidate",
    "candidates",
    "id",
    "ids",
    "ticket",
    "tickets",
    "oof",
    "out_of_fold",
    "validation",
    "eval",
    "evaluation",
}


def inspect_structure(obj, path="root", depth=0, results=None):
    if results is None:
        results = []

    if depth > 8:
        return results

    if isinstance(obj, dict):
        for key, value in obj.items():

            key_text = str(key).lower()

            if any(
                term in key_text
                for term in PREDICTION_TERMS
            ):
                results.append(
                    {
                        "path": f"{path}.{key}",
                        "kind": "key",
                        "type": type(value).__name__,
                        "summary": summarize(value),
                    }
                )

            inspect_structure(
                value,
                f"{path}.{key}",
                depth + 1,
                results,
            )

    elif isinstance(obj, list):

        if obj:
            first = obj[0]

            if isinstance(first, dict):
                inspect_structure(
                    first,
                    f"{path}[0]",
                    depth + 1,
                    results,
                )

    return results


def summarize(value):

    if isinstance(value, dict):
        return {
            "kind": "dict",
            "keys": [
                str(k)
                for k in list(value.keys())[:30]
            ],
        }

    if isinstance(value, list):
        summary = {
            "kind": "list",
            "length": len(value),
        }

        if value:
            summary["first_type"] = (
                type(value[0]).__name__
            )

            if isinstance(value[0], dict):
                summary["first_keys"] = [
                    str(k)
                    for k in list(
                        value[0].keys()
                    )[:30]
                ]

        return summary

    return {
        "kind": type(value).__name__,
        "value": str(value)[:300],
    }


print("=" * 100)
print(
    "T8 MOD-033 — OP-002: "
    "T4/T5 VALIDATION ARTIFACT CONTENT AUDIT"
)
print("=" * 100)


results = []

for path in FILES:

    print("\n" + "-" * 100)
    print(path.relative_to(ROOT))

    record = {
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "readable": False,
        "top_level_type": None,
        "prediction_like_content": [],
        "error": None,
    }

    if not path.exists():

        print("EXISTS: NO")
        results.append(record)
        continue

    print("EXISTS: YES")

    try:

        with path.open(
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        record["readable"] = True
        record["top_level_type"] = (
            type(data).__name__
        )

        matches = inspect_structure(data)

        record[
            "prediction_like_content"
        ] = matches

        print(
            "Top-level type:",
            type(data).__name__,
        )

        print(
            "Prediction/prediction-related "
            "structural matches:",
            len(matches),
        )

        for match in matches[:40]:

            print(
                "  ",
                match["path"],
                "=>",
                match["summary"],
            )

        if len(matches) > 40:

            print(
                "  ...",
                len(matches) - 40,
                "additional matches",
            )

    except Exception as exc:

        record["error"] = repr(exc)

        print(
            "READ ERROR:",
            repr(exc),
        )

    results.append(record)


print("\n" + "=" * 100)
print("[SUMMARY]")
print("=" * 100)

for task in ["T4", "T5"]:

    task_records = [
        record
        for record in results
        if (
            f"/{task}/"
            in record["path"]
        )
    ]

    readable = sum(
        record["readable"]
        for record in task_records
    )

    structural_matches = sum(
        len(
            record[
                "prediction_like_content"
            ]
        )
        for record in task_records
    )

    print(
        f"{task}: "
        f"files={len(task_records)}, "
        f"readable={readable}, "
        f"structural_matches={structural_matches}"
    )


print(
    "\nThis operation only inspects existing JSON content."
)

print(
    "It does not treat a metric, ranking summary, "
    "or model artifact as a prediction table."
)

print(
    "No fusion eligibility is established by this audit alone."
)


with OUTPUT.open(
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        {
            "module": "T8-MOD-033",
            "operation": "OP-002",
            "files": results,
            "locked_evaluation_used": False,
            "fusion_model_trained": False,
        },
        f,
        indent=2,
    )

print(
    "\nAudit written:",
    OUTPUT,
)

print("\n" + "=" * 100)
print("MOD-033 OP-002 COMPLETE")
print("=" * 100)