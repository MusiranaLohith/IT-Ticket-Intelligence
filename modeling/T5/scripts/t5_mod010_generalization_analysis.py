from pathlib import Path
import json
import sys
from datetime import datetime, timezone


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T5_ROOT = PROJECT_ROOT / "modeling" / "T5"

CALIBRATION_COMPARISON = (
    T5_ROOT
    / "metrics"
    / "t5_mod007_calibration_comparison.json"
)

LOCKED_EVALUATION = (
    T5_ROOT
    / "metrics"
    / "t5_mod009_locked_evaluation_metrics.json"
)

OUTPUT = (
    T5_ROOT
    / "metrics"
    / "t5_mod010_generalization_analysis.json"
)


EXPECTED_VALIDATION = {
    "average_precision": 0.16377630768463408,
    "roc_auc": 0.8969287312131792,
    "log_loss": 0.028358865729,
    "brier_score": 0.005860260618,
}

EXPECTED_EVALUATION = {
    "average_precision": 0.12583280543036882,
    "roc_auc": 0.6781415853279965,
    "log_loss": 0.27250018754800265,
    "brier_score": 0.059906950851585296,
}


def fail(message):
    print(f"FAIL: {message}")
    sys.exit(1)


def load_json(path):
    if not path.exists():
        fail(f"Missing required artifact: {path}")

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def extract_validation_metrics(data):
    if "sigmoid_calibrated" not in data:
        fail(
            "MOD-007 calibration comparison does not contain "
            "'sigmoid_calibrated'."
        )

    section = data["sigmoid_calibrated"]

    required = [
        "average_precision",
        "roc_auc",
        "log_loss",
        "brier_score",
    ]

    for key in required:
        if key not in section:
            fail(
                f"MOD-007 validation metrics missing: {key}"
            )

    return {
        key: float(section[key])
        for key in required
    }


def extract_evaluation_metrics(data):
    if "metrics" not in data:
        fail(
            "MOD-009 evaluation artifact does not contain "
            "'metrics'."
        )

    section = data["metrics"]

    required = [
        "average_precision",
        "roc_auc",
        "log_loss",
        "brier_score",
    ]

    for key in required:
        if key not in section:
            fail(
                f"MOD-009 evaluation metrics missing: {key}"
            )

    return {
        key: float(section[key])
        for key in required
    }


def relative_change(old, new):
    if old == 0:
        return None

    return (
        (new - old)
        / old
        * 100.0
    )


def main():
    print("=" * 80)
    print("T5-MOD-010 — GENERALIZATION ANALYSIS")
    print("=" * 80)

    # ------------------------------------------------------------------
    # 1. Verify controlled metric artifacts
    # ------------------------------------------------------------------

    print("\n[1] Verify controlled metric artifacts")

    validation_data = load_json(
        CALIBRATION_COMPARISON
    )

    evaluation_data = load_json(
        LOCKED_EVALUATION
    )

    print(
        f"Validation metrics: "
        f"{CALIBRATION_COMPARISON}"
    )

    print(
        f"Locked evaluation metrics: "
        f"{LOCKED_EVALUATION}"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 2. Extract MOD-007 frozen sigmoid validation metrics
    # ------------------------------------------------------------------

    print(
        "\n[2] Extract frozen sigmoid validation metrics"
    )

    validation = extract_validation_metrics(
        validation_data
    )

    for metric, value in validation.items():
        print(
            f"{metric}: {value:.12f}"
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 3. Extract MOD-009 locked evaluation metrics
    # ------------------------------------------------------------------

    print(
        "\n[3] Extract locked evaluation metrics"
    )

    evaluation = extract_evaluation_metrics(
        evaluation_data
    )

    for metric, value in evaluation.items():
        print(
            f"{metric}: {value:.12f}"
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 4. Cross-check recorded values
    # ------------------------------------------------------------------

    print(
        "\n[4] Cross-check recorded metric values"
    )

    for metric, expected in EXPECTED_VALIDATION.items():

        actual = validation[metric]

        if abs(actual - expected) > 1e-12:
            fail(
                f"Validation {metric} does not match "
                f"the recorded MOD-007 value."
            )

    for metric, expected in EXPECTED_EVALUATION.items():

        actual = evaluation[metric]

        if abs(actual - expected) > 1e-12:
            fail(
                f"Evaluation {metric} does not match "
                f"the recorded MOD-009 value."
            )

    print(
        "Validation metrics match MOD-007."
    )

    print(
        "Evaluation metrics match MOD-009."
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 5. Calculate generalization changes
    # ------------------------------------------------------------------

    print(
        "\n[5] Calculate validation-to-evaluation changes"
    )

    generalization = {}

    for metric in validation:

        val = validation[metric]
        evaluation_value = evaluation[metric]

        absolute_change = (
            evaluation_value - val
        )

        relative = relative_change(
            val,
            evaluation_value,
        )

        generalization[metric] = {
            "validation": val,
            "locked_evaluation": evaluation_value,
            "absolute_change": absolute_change,
            "relative_change_percent": relative,
        }

        print(f"\n{metric}")

        print(
            f"  Validation: "
            f"{val:.12f}"
        )

        print(
            f"  Locked evaluation: "
            f"{evaluation_value:.12f}"
        )

        print(
            f"  Absolute change: "
            f"{absolute_change:.12f}"
        )

        if relative is not None:
            print(
                f"  Relative change: "
                f"{relative:.2f}%"
            )

    # ------------------------------------------------------------------
    # 6. Determine observed directions
    # ------------------------------------------------------------------

    print(
        "\n[6] Determine observed generalization directions"
    )

    discrimination_metrics = [
        "average_precision",
        "roc_auc",
    ]

    probability_loss_metrics = [
        "log_loss",
        "brier_score",
    ]

    discrimination_decreased = all(
        generalization[metric]["absolute_change"] < 0
        for metric in discrimination_metrics
    )

    loss_increased = all(
        generalization[metric]["absolute_change"] > 0
        for metric in probability_loss_metrics
    )

    print(
        "Discrimination metrics decreased: "
        f"{discrimination_decreased}"
    )

    print(
        "Log-loss/Brier increased: "
        f"{loss_increased}"
    )

    # ------------------------------------------------------------------
    # 7. Build controlled analysis record
    # ------------------------------------------------------------------

    print(
        "\n[7] Build generalization analysis record"
    )

    result = {
        "operation": "T5-MOD-010",
        "operation_name": "Generalization Analysis",
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),

        "inputs": {
            "validation_source": str(
                CALIBRATION_COMPARISON
            ),
            "locked_evaluation_source": str(
                LOCKED_EVALUATION
            ),
        },

        "selected_model": {
            "classifier": "balanced LogisticRegression",
            "calibration": "sigmoid",
            "threshold": None,
        },

        "validation_metrics": validation,

        "locked_evaluation_metrics": evaluation,

        "generalization": generalization,

        "observed_direction": {
            "discrimination_decreased": (
                discrimination_decreased
            ),
            "log_loss_increased": (
                generalization["log_loss"][
                    "absolute_change"
                ] > 0
            ),
            "brier_score_increased": (
                generalization["brier_score"][
                    "absolute_change"
                ] > 0
            ),
        },

        "interpretation": (
            "The locked evaluation shows lower discrimination "
            "and higher probabilistic loss than the "
            "training-derived validation results. This is an "
            "observed validation-to-temporal-evaluation "
            "difference. No model, calibrator, threshold, or "
            "evaluation data was changed."
        ),

        "controls": {
            "model_refit": False,
            "calibrator_refit": False,
            "vectorizer_refit": False,
            "threshold_optimization": False,
            "evaluation_used_for_selection": False,
            "evaluation_modified": False,
            "raw_dataset_read": False,
        },

        "status": (
            "GENERALIZATION_ANALYSIS_COMPLETE"
        ),
    }

    # ------------------------------------------------------------------
    # 8. Save result
    # ------------------------------------------------------------------

    print(
        "\n[8] Save generalization analysis"
    )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=2,
        )

    print(
        f"Saved: {OUTPUT}"
    )

    print(
        f"File size: "
        f"{OUTPUT.stat().st_size:,} bytes"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # Final
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print(
        "T5-MOD-010 RESULT: "
        "GENERALIZATION_ANALYSIS_COMPLETE"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()