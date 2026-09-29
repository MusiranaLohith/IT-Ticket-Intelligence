from pathlib import Path
import json


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "fmp05_op004r_t10_artifact_path_reconciliation.json"
)

TASK_ROOTS = {
    "T4": PROJECT_ROOT / "modeling" / "T4",
    "T5": PROJECT_ROOT / "modeling" / "T5",
    "T7": PROJECT_ROOT / "modeling" / "T7",
    "T9": PROJECT_ROOT / "modeling" / "T9",
}

NAME_TERMS = [
    "closure",
    "final",
    "integrated",
    "comparison",
    "evaluation",
    "metrics",
]


def inspect_json(path):
    result = {
        "path": str(path),
        "relative_path": str(
            path.relative_to(PROJECT_ROOT)
        ),
        "readable": False,
        "top_level_type": None,
        "top_level_keys": [],
        "status_values": [],
        "closure_values": [],
    }

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        result["readable"] = True
        result["top_level_type"] = type(data).__name__

        if isinstance(data, dict):
            result["top_level_keys"] = sorted(
                str(k) for k in data.keys()
            )

            for key, value in data.items():
                key_lower = str(key).lower()

                if (
                    "status" in key_lower
                    or "state" in key_lower
                ):
                    result["status_values"].append(
                        {
                            "key": str(key),
                            "value": value,
                        }
                    )

                if "closure" in key_lower:
                    result["closure_values"].append(
                        {
                            "key": str(key),
                            "value": value,
                        }
                    )

    except Exception as exc:
        result["error"] = str(exc)

    return result


def main():

    print("=" * 80)
    print(
        "FMP-05 OP-004R — T10 ARTIFACT PATH RECONCILIATION"
    )
    print("=" * 80)

    all_results = {}

    print()
    print("[1] Targeted task directories")
    print("-" * 80)

    for task, root in TASK_ROOTS.items():

        print(
            f"{task}: "
            f"{root} "
            f"exists={root.exists()}"
        )

        if not root.exists():
            all_results[task] = {
                "root_exists": False,
                "candidates": [],
            }
            continue

        candidates = []

        for path in sorted(
            root.rglob("*.json")
        ):
            filename = path.name.lower()

            if any(
                term in filename
                for term in NAME_TERMS
            ):
                candidates.append(
                    inspect_json(path)
                )

        all_results[task] = {
            "root_exists": True,
            "candidate_count": len(candidates),
            "candidates": candidates,
        }

        print(
            f"  candidate JSON artifacts: "
            f"{len(candidates)}"
        )

    print()
    print("[2] Candidate artifacts")
    print("-" * 80)

    for task, result in all_results.items():

        print()
        print(task)

        for candidate in result.get(
            "candidates",
            [],
        ):
            print(
                f"  "
                f"{candidate['relative_path']} "
                f"readable={candidate['readable']}"
            )

            if candidate["status_values"]:
                print(
                    "    status/state: "
                    + json.dumps(
                        candidate["status_values"],
                        ensure_ascii=False,
                    )
                )

            if candidate["closure_values"]:
                print(
                    "    closure fields: "
                    + json.dumps(
                        candidate["closure_values"],
                        ensure_ascii=False,
                    )
                )

    print()
    print("[3] Closure-artifact candidates")
    print("-" * 80)

    closure_candidates = {}

    for task, result in all_results.items():

        candidates = []

        for item in result.get(
            "candidates",
            [],
        ):

            name = Path(
                item["path"]
            ).name.lower()

            if (
                "closure" in name
                or "integrated" in name
            ):
                candidates.append(item)

        closure_candidates[task] = candidates

        print(
            f"{task}: "
            f"{len(candidates)} closure/integrated candidates"
        )

    print()
    print("[4] Read-only safeguards")
    print("-" * 80)

    safeguards = {
        "models_loaded": False,
        "predictions_generated": False,
        "retraining_performed": False,
        "calibration_fitted": False,
        "threshold_selected": False,
        "policy_modified": False,
        "artifacts_modified": False,
    }

    for key, value in safeguards.items():
        print(f"{key}: {value}")

    print()
    print("[5] Output")
    print("-" * 80)

    result = {
        "operation": "FMP-05-OP-004R",
        "operation_type": (
            "READ_ONLY_T10_ARTIFACT_PATH_RECONCILIATION"
        ),
        "status": "PASS",
        "task_roots": {
            task: str(root)
            for task, root in TASK_ROOTS.items()
        },
        "artifacts": all_results,
        "closure_candidates": closure_candidates,
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

    print(f"Saved: {OUTPUT_FILE}")

    print()
    print("[6] Final summary")
    print("-" * 80)
    print(
        "Operation type: "
        "READ_ONLY_T10_ARTIFACT_PATH_RECONCILIATION"
    )
    print("STATUS: PASS")

    print("=" * 80)


if __name__ == "__main__":
    main()