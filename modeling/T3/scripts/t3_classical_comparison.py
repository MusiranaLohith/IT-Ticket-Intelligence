from pathlib import Path
import json


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

METRICS_DIR = PROJECT_ROOT / "modeling" / "T3" / "metrics"
OUTPUT_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T3"
    / "analysis"
    / "t3_classical_model_comparison.json"
)

MODEL_FILES = {
    "T3-MOD-007": "t3_baseline_validation_metrics.json",
    "T3-MOD-008": "t3_class_weighted_validation_metrics.json",
    "T3-MOD-015": "t3_linear_svm_validation_metrics.json",
    "T3-MOD-016": "t3_svm_class_weighted_validation_metrics.json",
}

LABELS = ["S1", "S2", "S3", "S4"]


def load_metrics(filename):
    path = METRICS_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"METRICS_FILE_NOT_FOUND={path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("T3_MOD_017_START")

    results = {}

    for model_id, filename in MODEL_FILES.items():
        results[model_id] = load_metrics(filename)

    print("MODEL_SUMMARY")

    for model_id, metrics in results.items():
        print(model_id)
        print(f"ACCURACY={metrics['accuracy']:.6f}")
        print(f"MACRO_F1={metrics['macro_f1']:.6f}")
        print(f"WEIGHTED_F1={metrics['weighted_f1']:.6f}")

        for label in LABELS:
            print(
                f"{label}_F1="
                f"{metrics['per_class'][label]['f1']:.6f}"
            )

    # Frozen selection criterion:
    # Primary: macro F1
    # Secondary: accuracy, weighted F1
    ranked_by_macro_f1 = sorted(
        results.items(),
        key=lambda item: (
            item[1]["macro_f1"],
            item[1]["accuracy"],
            item[1]["weighted_f1"],
        ),
        reverse=True,
    )

    selected_model = ranked_by_macro_f1[0][0]

    comparison = {
        "task": "T3_SEVERITY_PREDICTION",
        "operation": "T3-MOD-017",
        "selection_criterion": {
            "primary_metric": "macro_f1",
            "secondary_metrics": [
                "accuracy",
                "weighted_f1",
            ],
            "per_class_metrics_required": True,
            "test_used": False,
        },
        "models": {},
        "ranking_by_frozen_criterion": [
            model_id
            for model_id, _ in ranked_by_macro_f1
        ],
        "selected_classical_candidate": selected_model,
        "selection_note": (
            "Selection is based only on validation macro F1, "
            "with accuracy and weighted F1 used as secondary "
            "tie-break criteria. Locked test data was not used."
        ),
        "status": "CLASSICAL_MODEL_COMPARISON_COMPLETE",
    }

    for model_id, metrics in results.items():
        comparison["models"][model_id] = {
            "accuracy": metrics["accuracy"],
            "macro_f1": metrics["macro_f1"],
            "weighted_f1": metrics["weighted_f1"],
            "per_class": metrics["per_class"],
            "test_used": metrics.get("test_used", False),
        }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_PATH.write_text(
        json.dumps(comparison, indent=2),
        encoding="utf-8",
    )

    print("RANKING_BY_MACRO_F1")

    for position, (model_id, metrics) in enumerate(
        ranked_by_macro_f1,
        start=1,
    ):
        print(
            f"{position}. {model_id} "
            f"MACRO_F1={metrics['macro_f1']:.6f} "
            f"ACCURACY={metrics['accuracy']:.6f} "
            f"WEIGHTED_F1={metrics['weighted_f1']:.6f}"
        )

    print(f"SELECTED_CLASSICAL_CANDIDATE={selected_model}")
    print(f"OUTPUT={OUTPUT_PATH}")
    print("TEST_USED=False")
    print("STATUS=CLASSICAL_MODEL_COMPARISON_COMPLETE")
    print("T3_MOD_017_COMPLETE")


if __name__ == "__main__":
    main()