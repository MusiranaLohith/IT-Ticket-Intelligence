from pathlib import Path
import json


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

METRIC_DIR = PROJECT_ROOT / "modeling" / "T3" / "metrics"
ANALYSIS_DIR = PROJECT_ROOT / "modeling" / "T3" / "analysis"

BASELINE_PATH = (
    METRIC_DIR / "t3_baseline_validation_metrics.json"
)

CLASS_WEIGHTED_PATH = (
    METRIC_DIR / "t3_class_weighted_validation_metrics.json"
)

OUTPUT_PATH = (
    ANALYSIS_DIR / "t3_baseline_comparison.json"
)

LABELS = ["S1", "S2", "S3", "S4"]


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("T3_MOD_009_START")

    baseline = load_json(BASELINE_PATH)
    weighted = load_json(CLASS_WEIGHTED_PATH)

    print(f"BASELINE_MODEL={baseline['model']}")
    print(f"WEIGHTED_MODEL={weighted['model']}")

    if baseline["train_rows"] != weighted["train_rows"]:
        raise RuntimeError("TRAIN_ROW_MISMATCH")

    if baseline["validation_rows"] != weighted["validation_rows"]:
        raise RuntimeError("VALIDATION_ROW_MISMATCH")

    if baseline["feature_count"] != weighted["feature_count"]:
        raise RuntimeError("FEATURE_COUNT_MISMATCH")

    if baseline["labels"] != weighted["labels"]:
        raise RuntimeError("LABEL_ORDER_MISMATCH")

    if baseline["test_used"] or weighted["test_used"]:
        raise RuntimeError("TEST_WAS_USED")

    comparison = {
        "task": "T3_SEVERITY_PREDICTION",
        "baseline": {
            "model": baseline["model"],
            "class_weight": baseline["class_weight"],
        },
        "comparison_model": {
            "model": weighted["model"],
            "class_weight": weighted["class_weight"],
        },
        "controlled_conditions": {
            "train_rows": baseline["train_rows"],
            "validation_rows": baseline["validation_rows"],
            "feature_count": baseline["feature_count"],
            "features": [
                "Summary",
                "Description",
            ],
            "test_used": False,
        },
        "overall_metrics": {},
        "per_class_changes": {},
        "confusion_matrices": {
            "baseline": baseline["confusion_matrix"],
            "class_weighted": weighted["confusion_matrix"],
        },
    }

    for metric in [
        "accuracy",
        "macro_f1",
        "weighted_f1",
    ]:
        baseline_value = baseline[metric]
        weighted_value = weighted[metric]

        comparison["overall_metrics"][metric] = {
            "baseline": baseline_value,
            "class_weighted": weighted_value,
            "absolute_change": weighted_value - baseline_value,
        }

    for label in LABELS:
        comparison["per_class_changes"][label] = {}

        for metric in [
            "precision",
            "recall",
            "f1",
        ]:
            baseline_value = baseline["per_class"][label][metric]
            weighted_value = weighted["per_class"][label][metric]

            comparison["per_class_changes"][label][metric] = {
                "baseline": baseline_value,
                "class_weighted": weighted_value,
                "absolute_change": weighted_value - baseline_value,
            }

        comparison["per_class_changes"][label]["support"] = (
            baseline["per_class"][label]["support"]
        )

    ANALYSIS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            comparison,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("OVERALL_COMPARISON")

    for metric in [
        "accuracy",
        "macro_f1",
        "weighted_f1",
    ]:
        result = comparison["overall_metrics"][metric]

        print(
            f"{metric.upper()}_BASELINE="
            f"{result['baseline']:.6f}"
        )

        print(
            f"{metric.upper()}_CLASS_WEIGHTED="
            f"{result['class_weighted']:.6f}"
        )

        print(
            f"{metric.upper()}_CHANGE="
            f"{result['absolute_change']:+.6f}"
        )

    print("PER_CLASS_COMPARISON")

    for label in LABELS:
        print(f"{label}")

        for metric in [
            "precision",
            "recall",
            "f1",
        ]:
            result = comparison["per_class_changes"][label][metric]

            print(
                f"{label}_{metric.upper()}_CHANGE="
                f"{result['absolute_change']:+.6f}"
            )

        print(
            f"{label}_SUPPORT="
            f"{comparison['per_class_changes'][label]['support']}"
        )

    print(f"OUTPUT={OUTPUT_PATH}")
    print("TEST_USED=False")
    print("STATUS=BASELINE_COMPARISON_COMPLETE")
    print("T3_MOD_009_COMPLETE")


if __name__ == "__main__":
    main()