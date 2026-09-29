from pathlib import Path
import json
import sys

import numpy as np
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve
from sklearn.metrics import brier_score_loss


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T5_ROOT = PROJECT_ROOT / "modeling" / "T5"

PREDICTIONS = (
    T5_ROOT
    / "metrics"
    / "t5_mod005_validation_predictions.npz"
)

METRICS_PATH = (
    T5_ROOT
    / "metrics"
    / "t5_mod006_calibration_metrics.json"
)

PLOT_PATH = (
    T5_ROOT
    / "plots"
    / "t5_mod006_reliability_curve.png"
)

BINS_PATH = (
    T5_ROOT
    / "metrics"
    / "t5_mod006_calibration_bins.json"
)


N_BINS = 10


def fail(message):
    print(f"FAIL: {message}")
    sys.exit(1)


def calculate_ece(y_true, probabilities, n_bins=10):
    """
    Expected Calibration Error using equal-width probability bins.
    """

    bin_edges = np.linspace(
        0.0,
        1.0,
        n_bins + 1,
    )

    total = len(y_true)
    ece = 0.0
    bins = []

    for index in range(n_bins):
        lower = bin_edges[index]
        upper = bin_edges[index + 1]

        if index == n_bins - 1:
            mask = (
                (probabilities >= lower)
                & (probabilities <= upper)
            )
        else:
            mask = (
                (probabilities >= lower)
                & (probabilities < upper)
            )

        count = int(mask.sum())

        if count == 0:
            bins.append(
                {
                    "bin": index,
                    "lower": float(lower),
                    "upper": float(upper),
                    "count": 0,
                    "mean_predicted_probability": None,
                    "observed_positive_rate": None,
                    "absolute_calibration_error": None,
                }
            )
            continue

        mean_probability = float(
            probabilities[mask].mean()
        )

        observed_rate = float(
            y_true[mask].mean()
        )

        absolute_error = abs(
            mean_probability - observed_rate
        )

        ece += (
            count / total
        ) * absolute_error

        bins.append(
            {
                "bin": index,
                "lower": float(lower),
                "upper": float(upper),
                "count": count,
                "mean_predicted_probability": (
                    mean_probability
                ),
                "observed_positive_rate": (
                    observed_rate
                ),
                "absolute_calibration_error": (
                    absolute_error
                ),
            }
        )

    return float(ece), bins


def probability_summary(probabilities):
    percentiles = [
        0,
        25,
        50,
        75,
        90,
        95,
        99,
        99.5,
        99.9,
        100,
    ]

    values = np.percentile(
        probabilities,
        percentiles,
    )

    return {
        str(percentile): float(value)
        for percentile, value
        in zip(percentiles, values)
    }


def threshold_analysis(y_true, probabilities):
    thresholds = [
        0.01,
        0.02,
        0.05,
        0.10,
        0.20,
        0.30,
        0.40,
        0.50,
        0.60,
        0.70,
        0.80,
        0.90,
    ]

    results = []

    for threshold in thresholds:
        predictions = (
            probabilities >= threshold
        )

        predicted_positive = int(
            predictions.sum()
        )

        if predicted_positive == 0:
            precision = 0.0
        else:
            precision = float(
                y_true[predictions].mean()
            )

        true_positive = int(
            (
                predictions
                & (y_true == 1)
            ).sum()
        )

        actual_positive = int(
            (y_true == 1).sum()
        )

        recall = (
            true_positive / actual_positive
            if actual_positive > 0
            else 0.0
        )

        results.append(
            {
                "threshold": threshold,
                "predicted_positive": (
                    predicted_positive
                ),
                "predicted_positive_rate": (
                    predicted_positive
                    / len(y_true)
                ),
                "precision": precision,
                "recall": float(recall),
            }
        )

    return results


def main():
    print("=" * 80)
    print("T5-MOD-006 — CALIBRATION ANALYSIS")
    print("=" * 80)

    # ------------------------------------------------------------------
    # 1. Verify prediction artifact
    # ------------------------------------------------------------------

    print("\n[1] Verify validation prediction artifact")

    if not PREDICTIONS.exists():
        fail(
            f"Prediction artifact does not exist:\n"
            f"{PREDICTIONS}"
        )

    print(f"Predictions: {PREDICTIONS}")
    print("PASS")

    # ------------------------------------------------------------------
    # 2. Load predictions
    # ------------------------------------------------------------------

    print("\n[2] Load validation probabilities")

    data = np.load(PREDICTIONS)

    required_keys = {
        "y_true",
        "p_duplicate",
        "y_pred_0_5",
    }

    missing = required_keys - set(data.files)

    if missing:
        fail(
            "Prediction artifact is missing: "
            + ", ".join(sorted(missing))
        )

    y_true = data["y_true"].astype(np.int8)
    probabilities = data["p_duplicate"].astype(
        np.float64
    )
    y_pred = data["y_pred_0_5"].astype(np.int8)

    print(f"Rows: {len(y_true)}")
    print(
        f"Positive labels: "
        f"{int(y_true.sum())}"
    )
    print(
        f"Negative labels: "
        f"{int((y_true == 0).sum())}"
    )

    if len(y_true) != len(probabilities):
        fail(
            "y_true and probability arrays have "
            "different lengths."
        )

    if len(y_true) != len(y_pred):
        fail(
            "y_true and prediction arrays have "
            "different lengths."
        )

    if np.any(
        (probabilities < 0)
        | (probabilities > 1)
    ):
        fail(
            "Probability values outside [0, 1] detected."
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 3. Calculate ECE
    # ------------------------------------------------------------------

    print("\n[3] Expected Calibration Error")

    ece, bins = calculate_ece(
        y_true,
        probabilities,
        N_BINS,
    )

    brier = brier_score_loss(
        y_true,
        probabilities,
    )

    print(f"ECE: {ece:.6f}")
    print(f"Brier Score: {brier:.6f}")

    print("PASS")

    # ------------------------------------------------------------------
    # 4. Print calibration bins
    # ------------------------------------------------------------------

    print("\n[4] Calibration bins")

    for item in bins:
        if item["count"] == 0:
            continue

        print(
            f"Bin {item['bin']:2d} "
            f"[{item['lower']:.1f}, "
            f"{item['upper']:.1f}) "
            f"n={item['count']:6d} "
            f"pred={item['mean_predicted_probability']:.6f} "
            f"obs={item['observed_positive_rate']:.6f}"
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 5. Probability distribution
    # ------------------------------------------------------------------

    print("\n[5] Probability distribution")

    summary = probability_summary(
        probabilities
    )

    for percentile, value in summary.items():
        print(
            f"P{percentile}: {value:.8f}"
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 6. Threshold diagnostics
    # ------------------------------------------------------------------

    print("\n[6] Threshold diagnostics")

    threshold_results = threshold_analysis(
        y_true,
        probabilities,
    )

    for result in threshold_results:
        print(
            f"Threshold={result['threshold']:.2f} "
            f"Predicted+={result['predicted_positive']:6d} "
            f"Precision={result['precision']:.6f} "
            f"Recall={result['recall']:.6f}"
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 7. Reliability curve
    # ------------------------------------------------------------------

    print("\n[7] Generate reliability curve")

    fraction_of_positives, mean_predicted_value = (
        calibration_curve(
            y_true,
            probabilities,
            n_bins=N_BINS,
            strategy="uniform",
        )
    )

    PLOT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.figure(
        figsize=(8, 7)
    )

    plt.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        label="Perfect calibration",
    )

    plt.plot(
        mean_predicted_value,
        fraction_of_positives,
        marker="o",
        label="T5 baseline",
    )

    plt.xlabel(
        "Mean predicted probability"
    )

    plt.ylabel(
        "Observed positive rate"
    )

    plt.title(
        "T5 Baseline Reliability Curve"
    )

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        PLOT_PATH,
        dpi=150,
    )

    plt.close()

    print(f"Plot: {PLOT_PATH}")
    print("PASS")

    # ------------------------------------------------------------------
    # 8. Save bin-level analysis
    # ------------------------------------------------------------------

    print("\n[8] Save calibration-bin analysis")

    with BINS_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            bins,
            file,
            indent=2,
        )

        file.write("\n")

    print(f"Bins: {BINS_PATH}")
    print("PASS")

    # ------------------------------------------------------------------
    # 9. Save metrics
    # ------------------------------------------------------------------

    print("\n[9] Save calibration metrics")

    metrics = {
        "operation": "T5-MOD-006",
        "operation_name": "Calibration Analysis",
        "source": str(PREDICTIONS),
        "rows": int(len(y_true)),
        "positive": int(y_true.sum()),
        "negative": int((y_true == 0).sum()),
        "brier_score": float(brier),
        "expected_calibration_error": float(ece),
        "probability_summary": summary,
        "threshold_diagnostics": threshold_results,
        "n_calibration_bins": N_BINS,
        "official_evaluation_used": False,
        "threshold_optimization": False,
        "status": "PASS",
    }

    with METRICS_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metrics,
            file,
            indent=2,
        )

        file.write("\n")

    print(f"Metrics: {METRICS_PATH}")
    print("PASS")

    # ------------------------------------------------------------------
    # Final
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("T5-MOD-006 RESULT: CALIBRATION_ANALYSIS_COMPLETE")
    print("=" * 80)

    print("\nOfficial evaluation set: NOT USED.")
    print("Model retraining: NOT PERFORMED.")
    print("Threshold optimization: NOT PERFORMED.")
    print("Validation predictions only.")


if __name__ == "__main__":
    main()