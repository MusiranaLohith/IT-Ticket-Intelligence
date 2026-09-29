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
    / "fmp05_op007r_native_operating_evidence.json"
)


TARGET_FILES = {
    "T2_test_predictions": (
        PROJECT_ROOT
        / "modeling/T2/analysis/t2_final_test_predictions.csv"
    ),
    "T2_test_metrics": (
        PROJECT_ROOT
        / "modeling/T2/analysis/t2_final_test_metrics.json"
    ),
    "T2_closure": (
        PROJECT_ROOT
        / "modeling/T2/analysis/t2_final_closure.json"
    ),
    "T3_locked_evaluation": (
        PROJECT_ROOT
        / "modeling/T3/analysis/t3_locked_test_evaluation.json"
    ),
    "T3_test_metrics": (
        PROJECT_ROOT
        / "modeling/T3/metrics/t3_final_test_metrics.json"
    ),
    "T3_closure": (
        PROJECT_ROOT
        / "modeling/T3/analysis/t3_final_closure.json"
    ),
    "T5_locked_evaluation": (
        PROJECT_ROOT
        / "modeling/T5/metrics/t5_mod009_locked_evaluation_metrics.json"
    ),
    "T5_calibration_metrics": (
        PROJECT_ROOT
        / "modeling/T5/metrics/t5_mod006_calibration_metrics.json"
    ),
    "T5_calibration_bins": (
        PROJECT_ROOT
        / "modeling/T5/metrics/t5_mod006_calibration_bins.json"
    ),
    "T5_calibration_comparison": (
        PROJECT_ROOT
        / "modeling/T5/metrics/t5_mod007_calibration_comparison.json"
    ),
    "T5_validation_metrics": (
        PROJECT_ROOT
        / "modeling/T5/metrics/t5_mod005_validation_metrics.json"
    ),
    "T5_closure": (
        PROJECT_ROOT
        / "modeling/T5/metrics/t5_mod011_final_closure.json"
    ),
}


def load_json(path):
    with path.open(
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def read_csv_schema(path):
    result = {
        "columns": [],
        "sample_rows": [],
        "row_count_sampled": 0,
    }

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        result["columns"] = (
            reader.fieldnames or []
        )

        for _ in range(5):

            row = next(
                reader,
                None,
            )

            if row is None:
                break

            result["sample_rows"].append(row)
            result["row_count_sampled"] += 1

    return result


def flatten(obj, prefix=""):
    """
    Recursively yield JSON scalar values as:
        (json_path, value)
    """

    if isinstance(obj, dict):

        for key, child_value in obj.items():

            current = (
                f"{prefix}.{key}"
                if prefix
                else str(key)
            )

            yield from flatten(
                child_value,
                current,
            )

    elif isinstance(obj, list):

        for index, child_value in enumerate(obj):

            current = (
                f"{prefix}[{index}]"
            )

            yield from flatten(
                child_value,
                current,
            )

    elif isinstance(
        obj,
        (str, int, float, bool),
    ):

        yield prefix, obj


def collect_matching_fields(data, terms):

    matches = []

    for path, value in flatten(data):

        path_lower = path.lower()
        value_lower = str(value).lower()

        matched_terms = []

        for term in terms:

            term_lower = term.lower()

            if (
                term_lower in path_lower
                or term_lower in value_lower
            ):
                matched_terms.append(term)

        if matched_terms:

            matches.append(
                {
                    "path": path,
                    "value": value,
                    "matched_terms": matched_terms,
                }
            )

    return matches


def print_matches(
    matches,
    limit,
):

    for match in matches[:limit]:

        print(
            f"  {match['path']} = "
            f"{match['value']}"
        )

    if len(matches) > limit:

        print(
            f"  ... "
            f"{len(matches) - limit} "
            f"additional matches stored in JSON"
        )


def main():

    print("=" * 80)
    print(
        "FMP-05 OP-007R — CORRECTED NATIVE OPERATING EVIDENCE EXTRACTION"
    )
    print("=" * 80)

    print()
    print("[1] Loading authoritative native evidence")
    print("-" * 80)

    loaded = {}

    for name, path in TARGET_FILES.items():

        print()
        print(name)
        print(f"  path: {path}")
        print(f"  exists: {path.exists()}")

        if not path.exists():

            raise RuntimeError(
                f"Required artifact missing: {path}"
            )

        if path.suffix.lower() == ".json":

            data = load_json(path)

            loaded[name] = {
                "type": "json",
                "data": data,
            }

            print("  readable: True")

            if isinstance(data, dict):

                print(
                    "  top-level keys: "
                    + ", ".join(
                        str(k)
                        for k in data.keys()
                    )
                )

        elif path.suffix.lower() == ".csv":

            schema = read_csv_schema(path)

            loaded[name] = {
                "type": "csv",
                "data": schema,
            }

            print("  readable: True")

            print(
                "  columns: "
                + ", ".join(
                    schema["columns"]
                )
            )

    print()
    print("[2] T2 native operating evidence")
    print("-" * 80)

    t2_terms = [
        "probability",
        "probabilities",
        "score",
        "decision",
        "threshold",
        "confidence",
        "predicted",
        "actual",
        "accuracy",
        "macro_f1",
        "weighted_f1",
    ]

    t2_evidence = {}

    for name in [
        "T2_test_metrics",
        "T2_closure",
    ]:

        matches = collect_matching_fields(
            loaded[name]["data"],
            t2_terms,
        )

        t2_evidence[name] = matches

        print(
            f"{name}: "
            f"{len(matches)} relevant fields"
        )

        print_matches(
            matches,
            50,
        )

    t2_prediction_schema = loaded[
        "T2_test_predictions"
    ]["data"]

    print()
    print(
        "T2 prediction columns: "
        + ", ".join(
            t2_prediction_schema["columns"]
        )
    )

    print()
    print("[3] T3 native operating evidence")
    print("-" * 80)

    t3_terms = [
        "probability",
        "probabilities",
        "score",
        "decision",
        "threshold",
        "confidence",
        "prediction",
        "actual",
        "accuracy",
        "macro_f1",
        "weighted_f1",
    ]

    t3_evidence = {}

    for name in [
        "T3_locked_evaluation",
        "T3_test_metrics",
        "T3_closure",
    ]:

        matches = collect_matching_fields(
            loaded[name]["data"],
            t3_terms,
        )

        t3_evidence[name] = matches

        print()
        print(
            f"{name}: "
            f"{len(matches)} relevant fields"
        )

        print_matches(
            matches,
            60,
        )

    print()
    print("[4] T5 native operating evidence")
    print("-" * 80)

    t5_terms = [
        "probability",
        "probabilities",
        "threshold",
        "threshold_optimization",
        "threshold_diagnostics",
        "calibration",
        "brier",
        "expected_calibration_error",
        "precision",
        "recall",
        "f1",
        "average_precision",
        "roc_auc",
        "log_loss",
        "operational",
        "selected",
        "optimized",
    ]

    t5_evidence = {}

    for name in [
        "T5_locked_evaluation",
        "T5_calibration_metrics",
        "T5_calibration_bins",
        "T5_calibration_comparison",
        "T5_validation_metrics",
        "T5_closure",
    ]:

        matches = collect_matching_fields(
            loaded[name]["data"],
            t5_terms,
        )

        t5_evidence[name] = matches

        print()
        print(
            f"{name}: "
            f"{len(matches)} relevant fields"
        )

        print_matches(
            matches,
            100,
        )

    print()
    print("[5] Native semantics check")
    print("-" * 80)

    semantics = {
        "T2": (
            "classification / "
            "task-specific priority evidence"
        ),
        "T3": (
            "classification / "
            "task-specific severity evidence"
        ),
        "T5": (
            "task-specific duplicate probability "
            "with existing calibration evidence"
        ),
    }

    for task, description in semantics.items():

        print(
            f"{task}: {description}"
        )

    print()
    print("[6] Existing threshold-policy controls")
    print("-" * 80)

    controls = {
        "new_threshold_selected": False,
        "threshold_reoptimized": False,
        "model_loaded": False,
        "predictions_generated": False,
        "new_calibration_fitted": False,
        "policy_modified": False,
        "universal_confidence_created": False,
        "universal_risk_created": False,
    }

    for key, value in controls.items():

        print(
            f"{key}: {value}"
        )

    print()
    print("[7] Read-only safeguards")
    print("-" * 80)

    safeguards = {
        "models_loaded": False,
        "predictions_generated": False,
        "retraining_performed": False,
        "calibration_fitted": False,
        "threshold_selected": False,
        "threshold_optimized": False,
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
    print("[8] Output")
    print("-" * 80)

    result = {
        "operation": "FMP-05-OP-007R",
        "operation_type": (
            "READ_ONLY_NATIVE_OPERATING_EVIDENCE_EXTRACTION"
        ),
        "status": "PASS",
        "authoritative_files": {
            name: str(path)
            for name, path
            in TARGET_FILES.items()
        },
        "t2_evidence": t2_evidence,
        "t2_prediction_schema": (
            loaded[
                "T2_test_predictions"
            ]["data"]
        ),
        "t3_evidence": t3_evidence,
        "t5_evidence": t5_evidence,
        "native_semantics": semantics,
        "controls": controls,
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
    print("[9] Final summary")
    print("-" * 80)

    print(
        "Operation type: "
        "READ_ONLY_NATIVE_OPERATING_EVIDENCE_EXTRACTION"
    )

    print("STATUS: PASS")

    print("=" * 80)


if __name__ == "__main__":
    main()