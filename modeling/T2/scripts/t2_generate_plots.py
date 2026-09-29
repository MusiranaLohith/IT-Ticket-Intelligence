from pathlib import Path
import csv
import json

import matplotlib.pyplot as plt
import numpy as np


# ============================================================
# T2-VIZ-001
# Final T2 Visualization
#
# Visualization only.
# No training.
# No refitting.
# No test tuning.
# No dataset modification.
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_ROOT = PROJECT_ROOT / "modeling" / "T2"

ANALYSIS_DIR = T2_ROOT / "analysis"
PLOTS_DIR = T2_ROOT / "plots"

GENERALIZATION_FILE = (
    ANALYSIS_DIR
    / "t2_final_generalization_analysis.json"
)

TEST_PREDICTIONS_FILE = (
    ANALYSIS_DIR
    / "t2_final_test_predictions.csv"
)

OUTPUT_MANIFEST = (
    PLOTS_DIR
    / "t2_visualization_manifest.json"
)


CLASSES = [
    "P1",
    "P2",
    "P3",
    "P4",
    "P5",
]


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(
            f"REQUIRED_FILE_NOT_FOUND={path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def load_predictions(path):
    if not path.exists():
        raise FileNotFoundError(
            f"REQUIRED_FILE_NOT_FOUND={path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        required = {
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

        return list(reader)


def build_confusion_matrix(rows):
    index = {
        label: i
        for i, label in enumerate(CLASSES)
    }

    matrix = np.zeros(
        (len(CLASSES), len(CLASSES)),
        dtype=int,
    )

    for row in rows:

        actual = row[
            "actual_priority"
        ]

        predicted = row[
            "predicted_priority"
        ]

        if (
            actual in index
            and predicted in index
        ):
            matrix[
                index[actual],
                index[predicted],
            ] += 1

    return matrix


def create_performance_plot(generalization):
    validation = generalization[
        "validation"
    ]

    test = generalization[
        "test"
    ]

    labels = [
        "Accuracy",
        "Macro-F1",
        "Weighted-F1",
    ]

    validation_values = [
        validation["accuracy"] * 100,
        validation["macro_f1"] * 100,
        validation["weighted_f1"] * 100,
    ]

    test_values = [
        test["accuracy"] * 100,
        test["macro_f1"] * 100,
        test["weighted_f1"] * 100,
    ]

    x = np.arange(
        len(labels)
    )

    width = 0.36

    fig, ax = plt.subplots(
        figsize=(9, 5.5)
    )

    ax.bar(
        x - width / 2,
        validation_values,
        width,
        label="Validation",
    )

    ax.bar(
        x + width / 2,
        test_values,
        width,
        label="Locked test",
    )

    ax.set_title(
        "T2 Final Model: Validation vs Locked Test"
    )

    ax.set_ylabel(
        "Score (%)"
    )

    ax.set_xticks(x)

    ax.set_xticklabels(
        labels
    )

    ax.set_ylim(
        0,
        50,
    )

    ax.legend()

    fig.tight_layout()

    output = (
        PLOTS_DIR
        / "t2_validation_vs_test.png"
    )

    fig.savefig(
        output,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    return output


def create_per_class_f1_plot(generalization):
    per_class = generalization[
        "test_per_class"
    ]

    values = [
        per_class[label]["f1"] * 100
        for label in CLASSES
    ]

    fig, ax = plt.subplots(
        figsize=(9, 5.5)
    )

    bars = ax.bar(
        CLASSES,
        values,
    )

    ax.set_title(
        "T2 Final Model: Per-Class F1 on Locked Test"
    )

    ax.set_ylabel(
        "F1 score (%)"
    )

    ax.set_ylim(
        0,
        60,
    )

    for bar, value in zip(
        bars,
        values,
    ):
        ax.text(
            bar.get_x()
            + bar.get_width() / 2,
            value + 1,
            f"{value:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    fig.tight_layout()

    output = (
        PLOTS_DIR
        / "t2_test_per_class_f1.png"
    )

    fig.savefig(
        output,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    return output


def create_confusion_matrix_plot(rows):
    matrix = build_confusion_matrix(
        rows
    )

    fig, ax = plt.subplots(
        figsize=(8, 7)
    )

    image = ax.imshow(
        matrix
    )

    ax.set_title(
        "T2 Final Model: Locked-Test Confusion Matrix"
    )

    ax.set_xlabel(
        "Predicted priority"
    )

    ax.set_ylabel(
        "Actual priority"
    )

    ax.set_xticks(
        range(len(CLASSES))
    )

    ax.set_yticks(
        range(len(CLASSES))
    )

    ax.set_xticklabels(
        CLASSES
    )

    ax.set_yticklabels(
        CLASSES
    )

    for i in range(
        len(CLASSES)
    ):
        for j in range(
            len(CLASSES)
        ):
            ax.text(
                j,
                i,
                f"{matrix[i, j]:,}",
                ha="center",
                va="center",
                fontsize=9,
            )

    fig.colorbar(
        image,
        ax=ax,
        label="Ticket count",
    )

    fig.tight_layout()

    output = (
        PLOTS_DIR
        / "t2_test_confusion_matrix.png"
    )

    fig.savefig(
        output,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    return output


def main():

    print(
        "T2_VIZ_001_START"
    )

    PLOTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    generalization = load_json(
        GENERALIZATION_FILE
    )

    predictions = load_predictions(
        TEST_PREDICTIONS_FILE
    )

    performance_plot = (
        create_performance_plot(
            generalization
        )
    )

    f1_plot = (
        create_per_class_f1_plot(
            generalization
        )
    )

    confusion_plot = (
        create_confusion_matrix_plot(
            predictions
        )
    )

    manifest = {
        "operation": "T2-VIZ-001",
        "task": "T2 — Priority Prediction",
        "dataset": "Mozilla CORE",
        "visualizations": [
            {
                "name": (
                    "Validation vs Locked Test"
                ),
                "file": str(
                    performance_plot
                ),
                "purpose": (
                    "Show final-model "
                    "generalization change"
                ),
            },
            {
                "name": (
                    "Per-Class F1"
                ),
                "file": str(
                    f1_plot
                ),
                "purpose": (
                    "Show class-dependent "
                    "predictive performance"
                ),
            },
            {
                "name": (
                    "Locked-Test Confusion Matrix"
                ),
                "file": str(
                    confusion_plot
                ),
                "purpose": (
                    "Show dominant "
                    "misclassification patterns"
                ),
            },
        ],
        "integrity": {
            "training": False,
            "refitting": False,
            "test_tuning": False,
            "dataset_modified": False,
        },
        "status": "COMPLETE",
    }

    with OUTPUT_MANIFEST.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            manifest,
            f,
            indent=2,
        )

    print(
        "PERFORMANCE_GRAPH="
        f"{performance_plot}"
    )

    print(
        "PER_CLASS_F1_GRAPH="
        f"{f1_plot}"
    )

    print(
        "CONFUSION_MATRIX_GRAPH="
        f"{confusion_plot}"
    )

    print(
        "MANIFEST="
        f"{OUTPUT_MANIFEST}"
    )

    print(
        "TRAINING=False"
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
        "STATUS=COMPLETE"
    )

    print(
        "T2_VIZ_001_COMPLETE"
    )


if __name__ == "__main__":
    main()