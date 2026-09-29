from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T5_ROOT = PROJECT_ROOT / "modeling" / "T5"

METRICS_DIR = T5_ROOT / "metrics"
PLOTS_DIR = T5_ROOT / "plots"

CALIBRATION_FILE = (
    METRICS_DIR
    / "t5_mod007_calibration_comparison.json"
)

EVALUATION_METRICS_FILE = (
    METRICS_DIR
    / "t5_mod009_locked_evaluation_metrics.json"
)

EVALUATION_PREDICTIONS_FILE = (
    METRICS_DIR
    / "t5_mod009_locked_evaluation_predictions.npz"
)

GENERALIZATION_FILE = (
    METRICS_DIR
    / "t5_mod010_generalization_analysis.json"
)


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def save_plot(fig, path):
    fig.tight_layout()
    fig.savefig(
        path,
        dpi=180,
        bbox_inches="tight",
    )
    plt.close(fig)


def main():
    print("=" * 80)
    print("T5 — VISUALIZATION")
    print("=" * 80)

    PLOTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ------------------------------------------------------------------
    # 1. Load existing controlled artifacts
    # ------------------------------------------------------------------

    print("\n[1] Load existing controlled artifacts")

    calibration = load_json(
        CALIBRATION_FILE
    )

    evaluation_metrics = load_json(
        EVALUATION_METRICS_FILE
    )

    generalization = load_json(
        GENERALIZATION_FILE
    )

    predictions = np.load(
        EVALUATION_PREDICTIONS_FILE
    )

    print("Calibration comparison: PASS")
    print("Locked evaluation metrics: PASS")
    print("Generalization analysis: PASS")
    print("Locked evaluation predictions: PASS")

    # ------------------------------------------------------------------
    # 2. Extract validation/evaluation metrics
    # ------------------------------------------------------------------

    print("\n[2] Extract final metrics")

    validation = {
        "average_precision": float(
            calibration[
                "sigmoid_calibrated"
            ]["average_precision"]
        ),
        "roc_auc": float(
            calibration[
                "sigmoid_calibrated"
            ]["roc_auc"]
        ),
        "log_loss": float(
            calibration[
                "sigmoid_calibrated"
            ]["log_loss"]
        ),
        "brier_score": float(
            calibration[
                "sigmoid_calibrated"
            ]["brier_score"]
        ),
    }

    evaluation = {
        "average_precision": float(
            evaluation_metrics[
                "metrics"
            ]["average_precision"]
        ),
        "roc_auc": float(
            evaluation_metrics[
                "metrics"
            ]["roc_auc"]
        ),
        "log_loss": float(
            evaluation_metrics[
                "metrics"
            ]["log_loss"]
        ),
        "brier_score": float(
            evaluation_metrics[
                "metrics"
            ]["brier_score"]
        ),
    }

    print("Validation and evaluation metrics loaded.")
    print("PASS")

    # ------------------------------------------------------------------
    # 3. Extract prediction arrays
    # ------------------------------------------------------------------

    print("\n[3] Load locked prediction arrays")

    if "y_true" not in predictions:
        raise KeyError(
            "y_true missing from locked prediction artifact."
        )

    y_true = predictions["y_true"]

    probability_keys = [
        "p_sigmoid",
        "p_calibrated",
        "p_duplicate",
    ]

    probability_key = None

    for key in probability_keys:
        if key in predictions:
            probability_key = key
            break

    if probability_key is None:
        raise KeyError(
            "Calibrated probability array not found."
        )

    probabilities = predictions[
        probability_key
    ]

    if len(y_true) != len(probabilities):
        raise ValueError(
            "Prediction arrays have different lengths."
        )

    y_pred = (
        probabilities >= 0.5
    ).astype(int)

    print(
        f"Rows: {len(y_true):,}"
    )

    print(
        f"Probability source: {probability_key}"
    )

    print(
        f"Positive predictions @0.5: "
        f"{int(y_pred.sum()):,}"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 4. Plot metric comparison
    # ------------------------------------------------------------------

    print("\n[4] Generate validation/evaluation plots")

    metric_specs = [
        (
            "average_precision",
            "Average Precision / PR-AUC",
            "t5_validation_vs_evaluation_ap.png",
        ),
        (
            "roc_auc",
            "ROC-AUC",
            "t5_validation_vs_evaluation_roc_auc.png",
        ),
        (
            "log_loss",
            "Log Loss",
            "t5_validation_vs_evaluation_log_loss.png",
        ),
        (
            "brier_score",
            "Brier Score",
            "t5_validation_vs_evaluation_brier.png",
        ),
    ]

    for key, title, filename in metric_specs:

        fig, ax = plt.subplots(
            figsize=(7, 5)
        )

        values = [
            validation[key],
            evaluation[key],
        ]

        ax.bar(
            ["Validation", "Locked evaluation"],
            values,
        )

        ax.set_title(
            f"T5 — {title}"
        )

        ax.set_ylabel(title)

        for index, value in enumerate(values):
            ax.text(
                index,
                value,
                f"{value:.4f}",
                ha="center",
                va="bottom",
            )

        save_plot(
            fig,
            PLOTS_DIR / filename,
        )

    print(
        "Created 4 metric comparison plots."
    )

    # ------------------------------------------------------------------
    # 5. Confusion matrix at descriptive threshold
    # ------------------------------------------------------------------

    print(
        "\n[5] Generate locked evaluation confusion matrix"
    )

    tn = int(
        np.sum(
            (y_true == 0)
            & (y_pred == 0)
        )
    )

    fp = int(
        np.sum(
            (y_true == 0)
            & (y_pred == 1)
        )
    )

    fn = int(
        np.sum(
            (y_true == 1)
            & (y_pred == 0)
        )
    )

    tp = int(
        np.sum(
            (y_true == 1)
            & (y_pred == 1)
        )
    )

    confusion = np.array(
        [
            [tn, fp],
            [fn, tp],
        ]
    )

    fig, ax = plt.subplots(
        figsize=(6, 5)
    )

    image = ax.imshow(
        confusion
    )

    ax.set_title(
        "T5 — Locked Evaluation Confusion Matrix @ 0.5"
    )

    ax.set_xlabel(
        "Predicted label"
    )

    ax.set_ylabel(
        "True label"
    )

    ax.set_xticks(
        [0, 1],
        ["0", "1"],
    )

    ax.set_yticks(
        [0, 1],
        ["0", "1"],
    )

    for i in range(2):
        for j in range(2):
            ax.text(
                j,
                i,
                f"{confusion[i, j]:,}",
                ha="center",
                va="center",
            )

    fig.colorbar(
        image,
        ax=ax,
        label="Count",
    )

    save_plot(
        fig,
        PLOTS_DIR
        / "t5_locked_evaluation_confusion_matrix.png",
    )

    print(
        f"TN={tn:,}, FP={fp:,}, FN={fn:,}, TP={tp:,}"
    )

    # ------------------------------------------------------------------
    # 6. Probability distribution
    # ------------------------------------------------------------------

    print(
        "\n[6] Generate probability distribution"
    )

    fig, ax = plt.subplots(
        figsize=(8, 5)
    )

    ax.hist(
        probabilities[y_true == 0],
        bins=50,
        alpha=0.7,
        label="True negative",
    )

    ax.hist(
        probabilities[y_true == 1],
        bins=50,
        alpha=0.7,
        label="True positive",
    )

    ax.axvline(
        0.5,
        linestyle="--",
        label="Descriptive threshold = 0.5",
    )

    ax.set_title(
        "T5 — Locked Evaluation Calibrated Probability Distribution"
    )

    ax.set_xlabel(
        "p_duplicate"
    )

    ax.set_ylabel(
        "Number of tickets"
    )

    ax.legend()

    save_plot(
        fig,
        PLOTS_DIR
        / "t5_locked_evaluation_probability_distribution.png",
    )

    # ------------------------------------------------------------------
    # 7. Generalization change
    # ------------------------------------------------------------------

    print(
        "\n[7] Generate generalization summary"
    )

    generalization_data = (
        generalization[
            "generalization"
        ]
    )

    labels = [
        "AP / PR-AUC",
        "ROC-AUC",
        "Log Loss",
        "Brier",
    ]

    keys = [
        "average_precision",
        "roc_auc",
        "log_loss",
        "brier_score",
    ]

    changes = [
        generalization_data[key][
            "relative_change_percent"
        ]
        for key in keys
    ]

    fig, ax = plt.subplots(
        figsize=(8, 5)
    )

    bars = ax.bar(
        labels,
        changes,
    )

    ax.axhline(
        0,
        linewidth=1,
    )

    ax.set_title(
        "T5 — Validation → Locked Evaluation Relative Change"
    )

    ax.set_ylabel(
        "Relative change (%)"
    )

    for bar, value in zip(
        bars,
        changes,
    ):
        ax.text(
            bar.get_x()
            + bar.get_width() / 2,
            value,
            f"{value:+.1f}%",
            ha="center",
            va=(
                "bottom"
                if value >= 0
                else "top"
            ),
        )

    save_plot(
        fig,
        PLOTS_DIR
        / "t5_validation_to_evaluation_generalization.png",
    )

    # ------------------------------------------------------------------
    # 8. Manifest
    # ------------------------------------------------------------------

    print(
        "\n[8] Save visualization manifest"
    )

    plot_files = sorted(
        PLOTS_DIR.glob(
            "t5_*.png"
        )
    )

    manifest = {
        "task": (
            "T5 — Binary Duplicate Detection"
        ),

        "source_artifacts": [
            str(CALIBRATION_FILE),
            str(EVALUATION_METRICS_FILE),
            str(EVALUATION_PREDICTIONS_FILE),
            str(GENERALIZATION_FILE),
        ],

        "plots": [
            str(path)
            for path in plot_files
        ],

        "threshold": 0.5,

        "threshold_status": (
            "descriptive_only"
        ),

        "modeling_performed": False,

        "training_performed": False,

        "calibration_performed": False,

        "threshold_optimization": False,

        "raw_dataset_read": False,

        "raw_dataset_modified": False,
    }

    manifest_path = (
        PLOTS_DIR
        / "t5_visualization_manifest.json"
    )

    with manifest_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            manifest,
            file,
            indent=2,
        )

    print(
        f"Manifest: {manifest_path}"
    )

    # ------------------------------------------------------------------
    # Final
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print(
        "T5 VISUALIZATION RESULT: "
        "COMPLETE"
    )
    print("=" * 80)

    print(
        f"Plots created: {len(plot_files)}"
    )

    print(
        "Training performed: NO"
    )

    print(
        "Calibration performed: NO"
    )

    print(
        "Threshold optimization: NO"
    )

    print(
        "Raw dataset read: NO"
    )


if __name__ == "__main__":
    main()