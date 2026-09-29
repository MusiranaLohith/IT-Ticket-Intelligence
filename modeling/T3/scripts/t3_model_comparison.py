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

WORD_CHAR_PATH = (
    METRIC_DIR / "t3_word_char_validation_metrics.json"
)

OUTPUT_PATH = (
    ANALYSIS_DIR / "t3_model_comparison.json"
)

LABELS = ["S1", "S2", "S3", "S4"]


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_common_conditions(models):
    reference = models[0]

    for model in models[1:]:
        if model["train_rows"] != reference["train_rows"]:
            raise RuntimeError("TRAIN_ROW_MISMATCH")

        if model["validation_rows"] != reference["validation_rows"]:
            raise RuntimeError("VALIDATION_ROW_MISMATCH")

        if model["labels"] != reference["labels"]:
            raise RuntimeError("LABEL_ORDER_MISMATCH")

        if model["test_used"]:
            raise RuntimeError("TEST_WAS_USED")

    if reference["test_used"]:
        raise RuntimeError("TEST_WAS_USED")


def main():
    print("T3_MOD_011_START")

    baseline = load_json(BASELINE_PATH)
    class_weighted = load_json(CLASS_WEIGHTED_PATH)
    word_char = load_json(WORD_CHAR_PATH)

    models = [
        baseline,
        class_weighted,
        word_char,
    ]

    validate_common_conditions(models)

    results = {
        "task": "T3_SEVERITY_PREDICTION",
        "evaluation_split": "VALIDATION_ONLY",
        "test_used": False,
        "models": {},
    }

    model_definitions = {
        "T3-MOD-007": baseline,
        "T3-MOD-008": class_weighted,
        "T3-MOD-010": word_char,
    }

    for model_id, data in model_definitions.items():
        results["models"][model_id] = {
            "model": data["model"],
            "class_weight": data["class_weight"],
            "train_rows": data["train_rows"],
            "validation_rows": data["validation_rows"],
            "feature_count": data.get(
                "feature_count",
                data.get("combined_feature_count"),
            ),
            "accuracy": data["accuracy"],
            "macro_f1": data["macro_f1"],
            "weighted_f1": data["weighted_f1"],
            "per_class": data["per_class"],
        }

    results["feature_details"] = {
        "T3-MOD-007": {
            "word_features": baseline["feature_count"],
            "character_features": 0,
            "combined_features": baseline["feature_count"],
        },
        "T3-MOD-008": {
            "word_features": class_weighted["feature_count"],
            "character_features": 0,
            "combined_features": class_weighted["feature_count"],
        },
        "T3-MOD-010": {
            "word_features": word_char[
                "word_feature_count"
            ],
            "character_features": word_char[
                "char_feature_count"
            ],
            "combined_features": word_char[
                "combined_feature_count"
            ],
        },
    }

    results["pairwise_changes"] = {}

    model_ids = list(model_definitions.keys())

    for i in range(len(model_ids)):
        for j in range(i + 1, len(model_ids)):
            first_id = model_ids[i]
            second_id = model_ids[j]

            first = model_definitions[first_id]
            second = model_definitions[second_id]

            pair_name = f"{first_id}_vs_{second_id}"

            results["pairwise_changes"][pair_name] = {
                "accuracy_change": (
                    second["accuracy"]
                    - first["accuracy"]
                ),
                "macro_f1_change": (
                    second["macro_f1"]
                    - first["macro_f1"]
                ),
                "weighted_f1_change": (
                    second["weighted_f1"]
                    - first["weighted_f1"]
                ),
                "per_class_f1_change": {},
            }

            for label in LABELS:
                results["pairwise_changes"][
                    pair_name
                ]["per_class_f1_change"][label] = (
                    second["per_class"][label]["f1"]
                    - first["per_class"][label]["f1"]
                )

    ANALYSIS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            results,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("MODEL_SUMMARY")

    for model_id, data in results["models"].items():
        print(f"{model_id}")
        print(
            f"ACCURACY={data['accuracy']:.6f}"
        )
        print(
            f"MACRO_F1={data['macro_f1']:.6f}"
        )
        print(
            f"WEIGHTED_F1={data['weighted_f1']:.6f}"
        )
        print(
            f"FEATURE_COUNT={data['feature_count']}"
        )

        for label in LABELS:
            print(
                f"{label}_F1="
                f"{data['per_class'][label]['f1']:.6f}"
            )

    print("PAIRWISE_CHANGES")

    for pair_name, changes in (
        results["pairwise_changes"].items()
    ):
        print(pair_name)
        print(
            f"ACCURACY_CHANGE="
            f"{changes['accuracy_change']:+.6f}"
        )
        print(
            f"MACRO_F1_CHANGE="
            f"{changes['macro_f1_change']:+.6f}"
        )
        print(
            f"WEIGHTED_F1_CHANGE="
            f"{changes['weighted_f1_change']:+.6f}"
        )

        for label in LABELS:
            print(
                f"{label}_F1_CHANGE="
                f"{changes['per_class_f1_change'][label]:+.6f}"
            )

    print(f"OUTPUT={OUTPUT_PATH}")
    print("TEST_USED=False")
    print("STATUS=MODEL_COMPARISON_COMPLETE")
    print("T3_MOD_011_COMPLETE")


if __name__ == "__main__":
    main()