from pathlib import Path
import json
import sys


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T5_ROOT = PROJECT_ROOT / "modeling" / "T5"

METRIC_FILE = (
    T5_ROOT
    / "metrics"
    / "t5_mod007_calibration_comparison.json"
)

OUTPUT_FILE = (
    T5_ROOT
    / "contracts"
    / "t5_mod008_model_selection_lock.json"
)


def fail(message):
    print(f"FAIL: {message}")
    sys.exit(1)


def require_close(
    left,
    right,
    tolerance=1e-12,
):
    return abs(left - right) <= tolerance


def main():
    print("=" * 80)
    print("T5-MOD-008 — MODEL SELECTION & EVALUATION LOCK")
    print("=" * 80)

    # ------------------------------------------------------------------
    # 1. Load controlled MOD-007 evidence
    # ------------------------------------------------------------------

    print("\n[1] Load MOD-007 calibration comparison")

    if not METRIC_FILE.exists():
        fail(
            f"Missing MOD-007 metrics: {METRIC_FILE}"
        )

    with METRIC_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        metrics = json.load(file)

    if metrics.get("operation") != "T5-MOD-007":
        fail(
            "Input metrics do not identify T5-MOD-007."
        )

    if metrics.get(
        "official_evaluation_used"
    ):
        fail(
            "MOD-007 indicates official evaluation was used."
        )

    if metrics.get(
        "threshold_optimization"
    ):
        fail(
            "MOD-007 indicates threshold optimization occurred."
        )

    print("MOD-007 evidence loaded.")
    print("Official evaluation used: False")
    print("Threshold optimization: False")
    print("PASS")

    # ------------------------------------------------------------------
    # 2. Extract comparison metrics
    # ------------------------------------------------------------------

    print("\n[2] Extract controlled comparison metrics")

    base = metrics["base_model"]
    sigmoid = metrics["sigmoid_calibrated"]
    isotonic = metrics["isotonic_calibrated"]

    base_ap = float(
        base["average_precision"]
    )

    sigmoid_ap = float(
        sigmoid["average_precision"]
    )

    isotonic_ap = float(
        isotonic["average_precision"]
    )

    base_roc = float(
        base["roc_auc"]
    )

    sigmoid_roc = float(
        sigmoid["roc_auc"]
    )

    isotonic_roc = float(
        isotonic["roc_auc"]
    )

    base_log_loss = float(
        base["log_loss"]
    )

    sigmoid_log_loss = float(
        sigmoid["log_loss"]
    )

    isotonic_log_loss = float(
        isotonic["log_loss"]
    )

    base_brier = float(
        base["brier_score"]
    )

    sigmoid_brier = float(
        sigmoid["brier_score"]
    )

    isotonic_brier = float(
        isotonic["brier_score"]
    )

    print(
        f"Baseline AP: {base_ap:.12f}"
    )

    print(
        f"Sigmoid AP: {sigmoid_ap:.12f}"
    )

    print(
        f"Isotonic AP: {isotonic_ap:.12f}"
    )

    print(
        f"Baseline ROC-AUC: {base_roc:.12f}"
    )

    print(
        f"Sigmoid ROC-AUC: {sigmoid_roc:.12f}"
    )

    print(
        f"Isotonic ROC-AUC: {isotonic_roc:.12f}"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 3. Apply frozen selection criteria
    # ------------------------------------------------------------------

    print("\n[3] Apply frozen selection criteria")

    sigmoid_ap_preserved = require_close(
        base_ap,
        sigmoid_ap,
    )

    sigmoid_roc_preserved = require_close(
        base_roc,
        sigmoid_roc,
    )

    sigmoid_brier_improved = (
        sigmoid_brier < base_brier
    )

    sigmoid_log_loss_improved = (
        sigmoid_log_loss < base_log_loss
    )

    isotonic_ap_loss = (
        isotonic_ap < base_ap
    )

    isotonic_roc_loss = (
        isotonic_roc < base_roc
    )

    print(
        "Sigmoid AP preserved: "
        f"{sigmoid_ap_preserved}"
    )

    print(
        "Sigmoid ROC-AUC preserved: "
        f"{sigmoid_roc_preserved}"
    )

    print(
        "Sigmoid Brier improved: "
        f"{sigmoid_brier_improved}"
    )

    print(
        "Sigmoid Log Loss improved: "
        f"{sigmoid_log_loss_improved}"
    )

    print(
        "Isotonic AP lower than baseline: "
        f"{isotonic_ap_loss}"
    )

    print(
        "Isotonic ROC-AUC lower than baseline: "
        f"{isotonic_roc_loss}"
    )

    if not sigmoid_ap_preserved:
        fail(
            "Sigmoid calibration does not preserve "
            "the primary AP result."
        )

    if not sigmoid_roc_preserved:
        fail(
            "Sigmoid calibration does not preserve "
            "ROC-AUC."
        )

    if not sigmoid_brier_improved:
        fail(
            "Sigmoid calibration does not improve Brier score."
        )

    if not sigmoid_log_loss_improved:
        fail(
            "Sigmoid calibration does not improve Log Loss."
        )

    if not isotonic_ap_loss:
        fail(
            "Isotonic did not show the expected AP distinction."
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 4. Lock selected pipeline
    # ------------------------------------------------------------------

    print("\n[4] Lock selected T5 pipeline")

    selected_pipeline = {
        "task": "T5 — Binary Duplicate Detection",

        "target": {
            "column": "T5 target",
            "definition": (
                "1 = first observed post-Creation "
                "Dupe of addition; "
                "0 = no observed post-Creation "
                "Dupe of addition through the "
                "administrative observation endpoint"
            ),
        },

        "prediction_boundary": "Creation time",

        "features": [
            "Creator",
            "Creator Detail",
            "Summary",
            "Description",
        ],

        "representation": {
            "type": "word-level TF-IDF",
            "ngram_range": [
                1,
                2,
            ],
            "min_df": 2,
            "max_features": 100000,
            "sublinear_tf": True,
            "lowercase": True,
        },

        "classifier": {
            "type": "LogisticRegression",
            "solver": "liblinear",
            "class_weight": "balanced",
            "max_iter": 1000,
            "random_state": 42,
        },

        "calibration": {
            "selected_method": "sigmoid",
            "fit_on": (
                "separate group-aware calibration partition"
            ),
            "validation_used_for_calibration": False,
        },

        "probability_output": "p_duplicate",

        "primary_metric": (
            "Average Precision / PR-AUC"
        ),

        "secondary_metrics": [
            "ROC-AUC",
            "Log Loss",
            "Brier Score",
        ],

        "threshold": {
            "value": 0.5,
            "purpose": "descriptive reporting only",
            "operational_selection": False,
        },

        "evaluation_protocol": {
            "official_evaluation_locked": True,
            "official_evaluation_used_for_selection": False,
            "group_aware_evaluation_boundary": True,
            "threshold_optimization": False,
        },
    }

    # ------------------------------------------------------------------
    # 5. Record evidence
    # ------------------------------------------------------------------

    print("\n[5] Record selection evidence")

    selection_evidence = {
        "baseline": {
            "average_precision": base_ap,
            "roc_auc": base_roc,
            "log_loss": base_log_loss,
            "brier_score": base_brier,
        },

        "sigmoid": {
            "average_precision": sigmoid_ap,
            "roc_auc": sigmoid_roc,
            "log_loss": sigmoid_log_loss,
            "brier_score": sigmoid_brier,
        },

        "isotonic": {
            "average_precision": isotonic_ap,
            "roc_auc": isotonic_roc,
            "log_loss": isotonic_log_loss,
            "brier_score": isotonic_brier,
        },

        "selection_basis": [
            (
                "Sigmoid preserves Average Precision "
                "to numerical precision."
            ),
            (
                "Sigmoid preserves ROC-AUC "
                "to numerical precision."
            ),
            (
                "Sigmoid substantially reduces "
                "Log Loss relative to baseline."
            ),
            (
                "Sigmoid substantially reduces "
                "Brier score relative to baseline."
            ),
            (
                "Isotonic produces lower AP and ROC-AUC "
                "than the baseline in the controlled "
                "validation comparison."
            ),
        ],
    }

    # ------------------------------------------------------------------
    # 6. Final lock artifact
    # ------------------------------------------------------------------

    print("\n[6] Write model-selection lock")

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact = {
        "operation": "T5-MOD-008",
        "operation_name": (
            "Model Selection & Evaluation Lock"
        ),

        "status": "MODEL_SELECTION_LOCKED",

        "selected_pipeline": selected_pipeline,

        "selection_evidence": selection_evidence,

        "data_controls": {
            "official_evaluation_rows": 20827,
            "official_evaluation_used": False,
            "training_validation_group_boundary_preserved": True,
            "calibration_partition_group_boundary_preserved": True,
            "synthetic_data": False,
            "raw_archive_scanned": False,
        },

        "explicit_non_decisions": [
            (
                "No operational duplicate-confirmation threshold "
                "was selected."
            ),
            (
                "No automatic duplicate confirmation is authorized "
                "by this model-selection operation."
            ),
            (
                "No target-ticket identification/pairing is implied."
            ),
            (
                "No claim of production calibration performance "
                "is made before locked evaluation."
            ),
        ],
    }

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            artifact,
            file,
            indent=2,
        )

        file.write("\n")

    print(
        f"Lock artifact: {OUTPUT_FILE}"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # Final
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print(
        "T5-MOD-008 RESULT: "
        "MODEL_SELECTION_LOCKED"
    )
    print("=" * 80)

    print(
        "\nSelected calibration method: SIGMOID"
    )

    print(
        "Official evaluation set: LOCKED / UNUSED"
    )

    print(
        "Operational threshold selection: NONE"
    )

    print(
        "Next stage: LOCKED EVALUATION"
    )


if __name__ == "__main__":
    main()