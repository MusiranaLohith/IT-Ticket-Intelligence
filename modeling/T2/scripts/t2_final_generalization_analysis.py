from pathlib import Path
import csv
import json


# ============================================================
# T2-MOD-021
# Final Test Error & Generalization Analysis
#
# Analysis only.
# No training.
# No refitting.
# No dataset modification.
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_ROOT = PROJECT_ROOT / "modeling" / "T2"

ANALYSIS_DIR = T2_ROOT / "analysis"

TEST_METRICS_FILE = (
    ANALYSIS_DIR
    / "t2_final_test_metrics.json"
)

VALIDATION_ERROR_FILE = (
    ANALYSIS_DIR
    / "t2_baseline_error_analysis.json"
)

TEST_PREDICTIONS_FILE = (
    ANALYSIS_DIR
    / "t2_final_test_predictions.csv"
)

OUTPUT_FILE = (
    ANALYSIS_DIR
    / "t2_final_generalization_analysis.json"
)

CLASSES = [
    "P1",
    "P2",
    "P3",
    "P4",
    "P5",
]


def load_json(path):
    with path.open(
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def load_predictions(path):
    rows = []

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        required = {
            "ID",
            "actual_priority",
            "predicted_priority",
        }

        fields = set(
            reader.fieldnames or []
        )

        missing = required - fields

        if missing:
            raise RuntimeError(
                "PREDICTION_SCHEMA_MISSING="
                + ",".join(sorted(missing))
            )

        for row in reader:
            rows.append(row)

    return rows


def build_confusion_counts(rows):
    matrix = {
        actual: {
            predicted: 0
            for predicted in CLASSES
        }
        for actual in CLASSES
    }

    for row in rows:
        actual = row[
            "actual_priority"
        ]

        predicted = row[
            "predicted_priority"
        ]

        if (
            actual in CLASSES
            and predicted in CLASSES
        ):
            matrix[
                actual
            ][
                predicted
            ] += 1

    return matrix


def build_distributions(rows):
    actual = {
        label: 0
        for label in CLASSES
    }

    predicted = {
        label: 0
        for label in CLASSES
    }

    for row in rows:

        actual_label = row[
            "actual_priority"
        ]

        predicted_label = row[
            "predicted_priority"
        ]

        if actual_label in actual:
            actual[
                actual_label
            ] += 1

        if predicted_label in predicted:
            predicted[
                predicted_label
            ] += 1

    return actual, predicted


def top_errors(matrix):
    errors = []

    for actual in CLASSES:
        for predicted in CLASSES:

            if actual == predicted:
                continue

            count = matrix[
                actual
            ][
                predicted
            ]

            errors.append(
                {
                    "actual": actual,
                    "predicted": predicted,
                    "count": count,
                }
            )

    errors.sort(
        key=lambda item: item["count"],
        reverse=True,
    )

    return errors


def class_error_summary(matrix):
    result = {}

    for label in CLASSES:

        support = sum(
            matrix[label].values()
        )

        correct = matrix[
            label
        ][
            label
        ]

        errors = (
            support - correct
        )

        error_rate = (
            errors / support
            if support > 0
            else 0.0
        )

        result[label] = {
            "support": support,
            "correct": correct,
            "errors": errors,
            "error_rate": error_rate,
        }

    return result


def main():

    print("T2_MOD_021_START")

    ANALYSIS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Verify required artifacts.
    # --------------------------------------------------------

    required_files = [
        TEST_METRICS_FILE,
        VALIDATION_ERROR_FILE,
        TEST_PREDICTIONS_FILE,
    ]

    for path in required_files:

        if not path.exists():
            raise FileNotFoundError(
                f"REQUIRED_ARTIFACT_NOT_FOUND={path}"
            )

    # --------------------------------------------------------
    # Load completed evaluation artifacts.
    # --------------------------------------------------------

    test_metrics = load_json(
        TEST_METRICS_FILE
    )

    validation_analysis = load_json(
        VALIDATION_ERROR_FILE
    )

    test_rows = load_predictions(
        TEST_PREDICTIONS_FILE
    )

    # --------------------------------------------------------
    # Validation metrics.
    #
    # These were produced by T2-MOD-019 selection evidence.
    # --------------------------------------------------------

    validation_accuracy = 0.446102
    validation_macro_f1 = 0.310450
    validation_weighted_f1 = 0.443565

    # --------------------------------------------------------
    # Test metrics.
    # --------------------------------------------------------

    test_metric_block = test_metrics[
        "metrics"
    ]

    test_accuracy = float(
        test_metric_block[
            "accuracy"
        ]
    )

    test_macro_f1 = float(
        test_metric_block[
            "macro_f1"
        ]
    )

    test_weighted_f1 = float(
        test_metric_block[
            "weighted_f1"
        ]
    )

    # --------------------------------------------------------
    # Generalization gaps.
    # --------------------------------------------------------

    accuracy_change = (
        test_accuracy
        - validation_accuracy
    )

    macro_f1_change = (
        test_macro_f1
        - validation_macro_f1
    )

    weighted_f1_change = (
        test_weighted_f1
        - validation_weighted_f1
    )

    # --------------------------------------------------------
    # Test confusion/error analysis.
    # --------------------------------------------------------

    matrix = build_confusion_counts(
        test_rows
    )

    actual_distribution, predicted_distribution = (
        build_distributions(
            test_rows
        )
    )

    errors = top_errors(
        matrix
    )

    class_errors = class_error_summary(
        matrix
    )

    # --------------------------------------------------------
    # Largest distribution differences.
    # --------------------------------------------------------

    distribution_shift = {}

    total = len(test_rows)

    for label in CLASSES:

        actual_rate = (
            actual_distribution[label]
            / total
        )

        predicted_rate = (
            predicted_distribution[label]
            / total
        )

        distribution_shift[label] = {
            "actual_count": (
                actual_distribution[label]
            ),
            "predicted_count": (
                predicted_distribution[label]
            ),
            "actual_percentage": (
                actual_rate * 100
            ),
            "predicted_percentage": (
                predicted_rate * 100
            ),
            "difference_percentage_points": (
                (predicted_rate - actual_rate)
                * 100
            ),
        }

    # --------------------------------------------------------
    # Per-class test metrics.
    # --------------------------------------------------------

    per_class = {}

    for label in CLASSES:

        block = test_metric_block[
            "per_class"
        ][label]

        per_class[label] = {
            "precision": float(
                block["precision"]
            ),
            "recall": float(
                block["recall"]
            ),
            "f1": float(
                block["f1"]
            ),
            "support": int(
                block["support"]
            ),
        }

    # --------------------------------------------------------
    # Generalization interpretation.
    # --------------------------------------------------------

    observations = [
        (
            "Test accuracy is lower than validation "
            "accuracy, indicating reduced performance "
            "on the later held-out period."
        ),
        (
            "Test macro-F1 decreases more strongly "
            "than accuracy, indicating that the "
            "generalization loss is particularly "
            "important for class-balanced performance."
        ),
        (
            "P4 and P5 remain difficult on the final "
            "test period, with substantially lower "
            "F1 than P1-P3."
        ),
        (
            "The model continues to concentrate "
            "predictions toward the more represented "
            "priority classes."
        ),
        (
            "The results do not support treating "
            "the T2 model as a uniformly reliable "
            "five-class priority predictor."
        ),
        (
            "The evidence supports using T2 as a "
            "confidence-aware decision-support signal "
            "rather than an unquestioned automated "
            "priority assignment."
        ),
    ]

    # --------------------------------------------------------
    # Strongest test errors.
    # --------------------------------------------------------

    top_nonzero_errors = [
        item
        for item in errors
        if item["count"] > 0
    ][:10]

    report = {
        "operation": "T2-MOD-021",
        "operation_name": (
            "Final Test Error & "
            "Generalization Analysis"
        ),

        "task": "T2",
        "dataset": "Mozilla CORE",

        "model": {
            "operation": "T2-MOD-007",
            "name": (
                "TF-IDF + Class-Weighted "
                "Logistic Regression"
            ),
        },

        "validation": {
            "accuracy": validation_accuracy,
            "macro_f1": validation_macro_f1,
            "weighted_f1": validation_weighted_f1,
            "source": "T2-MOD-019",
        },

        "test": {
            "rows": len(test_rows),
            "accuracy": test_accuracy,
            "macro_f1": test_macro_f1,
            "weighted_f1": test_weighted_f1,
            "source": "T2-MOD-020",
        },

        "generalization_change": {
            "accuracy_change": accuracy_change,
            "macro_f1_change": macro_f1_change,
            "weighted_f1_change": weighted_f1_change,
            "accuracy_change_percentage_points": (
                accuracy_change * 100
            ),
            "macro_f1_change_percentage_points": (
                macro_f1_change * 100
            ),
            "weighted_f1_change_percentage_points": (
                weighted_f1_change * 100
            ),
        },

        "test_per_class": per_class,

        "test_actual_distribution": (
            actual_distribution
        ),

        "test_predicted_distribution": (
            predicted_distribution
        ),

        "test_prediction_distribution_difference": (
            distribution_shift
        ),

        "test_confusion_matrix": matrix,

        "top_test_errors": (
            top_nonzero_errors
        ),

        "test_class_error_summary": (
            class_errors
        ),

        "interpretation": {
            "observations": observations,
            "model_reliability": (
                "limited and class-dependent"
            ),
            "minority_class_reliability": (
                "weak for P4 and P5"
            ),
            "recommended_system_role": (
                "decision-support signal requiring "
                "confidence-aware handling and "
                "human-review consideration"
            ),
        },

        "integrity": {
            "retraining_performed": False,
            "refitting_performed": False,
            "test_tuning_performed": False,
            "dataset_modified": False,
        },

        "status": (
            "GENERALIZATION_ANALYSIS_COMPLETE"
        ),
    }

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            report,
            f,
            indent=2,
        )

    # --------------------------------------------------------
    # Console output.
    # --------------------------------------------------------

    print(
        "MODEL=T2-MOD-007"
    )

    print(
        "TEST_ROWS="
        f"{len(test_rows)}"
    )

    print(
        "VALIDATION_ACCURACY="
        f"{validation_accuracy:.6f}"
    )

    print(
        "TEST_ACCURACY="
        f"{test_accuracy:.6f}"
    )

    print(
        "ACCURACY_CHANGE_PP="
        f"{accuracy_change * 100:.4f}"
    )

    print(
        "VALIDATION_MACRO_F1="
        f"{validation_macro_f1:.6f}"
    )

    print(
        "TEST_MACRO_F1="
        f"{test_macro_f1:.6f}"
    )

    print(
        "MACRO_F1_CHANGE_PP="
        f"{macro_f1_change * 100:.4f}"
    )

    print(
        "VALIDATION_WEIGHTED_F1="
        f"{validation_weighted_f1:.6f}"
    )

    print(
        "TEST_WEIGHTED_F1="
        f"{test_weighted_f1:.6f}"
    )

    print(
        "WEIGHTED_F1_CHANGE_PP="
        f"{weighted_f1_change * 100:.4f}"
    )

    for label in CLASSES:

        print(
            f"{label}_TEST_F1="
            f"{per_class[label]['f1']:.6f}"
        )

        print(
            f"{label}_TEST_SUPPORT="
            f"{per_class[label]['support']}"
        )

    print()

    print(
        "TOP_TEST_ERRORS"
    )

    for item in top_nonzero_errors:

        print(
            f"{item['actual']}->"
            f"{item['predicted']}="
            f"{item['count']}"
        )

    print()

    print(
        "RETRAINING=False"
    )

    print(
        "REFITTING=False"
    )

    print(
        "TEST_TUNING=False"
    )

    print(
        "DATASET_MODIFIED=False"
    )

    print(
        "OUTPUT="
        f"{OUTPUT_FILE}"
    )

    print(
        "STATUS="
        "GENERALIZATION_ANALYSIS_COMPLETE"
    )

    print(
        "T2_MOD_021_COMPLETE"
    )


if __name__ == "__main__":
    main()