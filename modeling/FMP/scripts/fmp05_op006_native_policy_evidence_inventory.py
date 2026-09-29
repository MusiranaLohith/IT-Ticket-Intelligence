from pathlib import Path
import json
import csv


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "fmp05_op006_native_policy_evidence_inventory.json"
)

TASKS = {
    "T2": PROJECT_ROOT / "modeling" / "T2",
    "T3": PROJECT_ROOT / "modeling" / "T3",
    "T5": PROJECT_ROOT / "modeling" / "T5",
}

# Names that strongly indicate empirical evaluation evidence.
NAME_TERMS = [
    "prediction",
    "predictions",
    "evaluation",
    "eval",
    "locked",
    "calibration",
    "metrics",
    "test",
    "validation",
]


def read_json(path):
    with path.open(
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def inspect_json(path):
    result = {
        "path": str(path),
        "relative_path": str(
            path.relative_to(PROJECT_ROOT)
        ),
        "readable": False,
        "top_level_type": None,
        "top_level_keys": [],
        "interesting_keys": [],
    }

    try:
        data = read_json(path)

        result["readable"] = True
        result["top_level_type"] = type(data).__name__

        if isinstance(data, dict):

            result["top_level_keys"] = sorted(
                str(key)
                for key in data.keys()
            )

            interesting_terms = [
                "prediction",
                "probability",
                "score",
                "label",
                "target",
                "y_true",
                "y_pred",
                "threshold",
                "precision",
                "recall",
                "f1",
                "roc",
                "auc",
                "average_precision",
                "brier",
                "log_loss",
                "calibration",
                "support",
            ]

            for key in data.keys():

                key_text = str(key).lower()

                if any(
                    term in key_text
                    for term in interesting_terms
                ):
                    result["interesting_keys"].append(
                        str(key)
                    )

        elif isinstance(data, list):

            result["top_level_keys"] = [
                "LIST",
                f"length={len(data)}",
            ]

    except Exception as exc:

        result["error"] = str(exc)

    return result


def inspect_csv(path):
    result = {
        "path": str(path),
        "relative_path": str(
            path.relative_to(PROJECT_ROOT)
        ),
        "readable": False,
        "columns": [],
        "row_count_sampled": 0,
        "interesting_columns": [],
    }

    try:

        with path.open(
            "r",
            encoding="utf-8",
            errors="replace",
            newline="",
        ) as f:

            reader = csv.reader(f)

            header = next(
                reader,
                [],
            )

            result["readable"] = True
            result["columns"] = header

            interesting_terms = [
                "prediction",
                "pred",
                "prob",
                "probability",
                "score",
                "label",
                "target",
                "truth",
                "y_true",
                "y_pred",
                "threshold",
                "precision",
                "recall",
                "f1",
                "calibration",
                "duplicate",
                "priority",
                "severity",
            ]

            for column in header:

                lowered = column.lower()

                if any(
                    term in lowered
                    for term in interesting_terms
                ):
                    result[
                        "interesting_columns"
                    ].append(column)

            # Only sample a small number of rows.
            for _ in range(5):

                row = next(
                    reader,
                    None,
                )

                if row is None:
                    break

                result[
                    "row_count_sampled"
                ] += 1

    except Exception as exc:

        result["error"] = str(exc)

    return result


def main():

    print("=" * 80)
    print(
        "FMP-05 OP-006 — NATIVE TASK-SPECIFIC POLICY EVIDENCE INVENTORY"
    )
    print("=" * 80)

    print()
    print("[1] Task directories")
    print("-" * 80)

    for task, root in TASKS.items():

        print(
            f"{task}: "
            f"{root} "
            f"exists={root.exists()}"
        )

    print()
    print("[2] Discovering candidate empirical artifacts")
    print("-" * 80)

    results = {}

    for task, root in TASKS.items():

        if not root.exists():

            results[task] = {
                "root_exists": False,
                "candidates": [],
            }

            continue

        candidates = []

        # Restrict discovery to the task directory.
        # No project-wide recursive scan.
        for path in sorted(
            root.rglob("*")
        ):

            if not path.is_file():
                continue

            suffix = path.suffix.lower()

            if suffix not in {
                ".json",
                ".csv",
            }:
                continue

            name = path.name.lower()

            if not any(
                term in name
                for term in NAME_TERMS
            ):
                continue

            if suffix == ".json":

                inspected = inspect_json(path)

            else:

                inspected = inspect_csv(path)

            candidates.append(
                inspected
            )

        results[task] = {
            "root_exists": True,
            "candidate_count": len(candidates),
            "candidates": candidates,
        }

        print(
            f"{task}: "
            f"{len(candidates)} candidate artifacts"
        )

    print()
    print("[3] Candidate empirical artifacts")
    print("-" * 80)

    for task, task_result in results.items():

        print()
        print(task)

        for candidate in task_result.get(
            "candidates",
            [],
        ):

            print(
                f"  {candidate['relative_path']}"
            )

            print(
                f"    readable: "
                f"{candidate.get('readable')}"
            )

            if candidate.get(
                "interesting_keys"
            ):
                print(
                    "    interesting JSON keys: "
                    + ", ".join(
                        candidate[
                            "interesting_keys"
                        ]
                    )
                )

            if candidate.get(
                "interesting_columns"
            ):
                print(
                    "    interesting CSV columns: "
                    + ", ".join(
                        candidate[
                            "interesting_columns"
                        ]
                    )
                )

    print()
    print("[4] Native evidence requirements")
    print("-" * 80)

    requirements = {
        "T2": [
            "locked evaluation predictions or equivalent",
            "native class labels / truth",
            "probability or decision-score evidence if available",
        ],
        "T3": [
            "locked evaluation predictions or equivalent",
            "native class labels / truth",
            "probability or decision-score evidence if available",
        ],
        "T5": [
            "locked evaluation predictions or equivalent",
            "duplicate truth",
            "native calibrated probability if available",
            "existing calibration/reliability evidence",
        ],
    }

    for task, items in requirements.items():

        print()
        print(task)

        for item in items:

            print(
                f"  - {item}"
            )

    print()
    print("[5] Read-only safeguards")
    print("-" * 80)

    safeguards = {
        "models_loaded": False,
        "predictions_generated": False,
        "retraining_performed": False,
        "calibration_fitted": False,
        "threshold_selected": False,
        "policy_modified": False,
        "artifacts_modified": False,
        "universal_confidence_created": False,
        "universal_risk_created": False,
    }

    for key, value in safeguards.items():

        print(
            f"{key}: {value}"
        )

    print()
    print("[6] Output")
    print("-" * 80)

    result = {
        "operation": "FMP-05-OP-006",
        "operation_type": (
            "READ_ONLY_NATIVE_TASK_SPECIFIC_POLICY_EVIDENCE_INVENTORY"
        ),
        "status": "PASS",
        "tasks": results,
        "native_evidence_requirements": requirements,
        "read_only_safeguards": safeguards,
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"Saved: {OUTPUT_FILE}"
    )

    print()
    print("[7] Final summary")
    print("-" * 80)

    print(
        "Operation type: "
        "READ_ONLY_NATIVE_TASK_SPECIFIC_POLICY_EVIDENCE_INVENTORY"
    )

    print("STATUS: PASS")

    print("=" * 80)


if __name__ == "__main__":
    main()