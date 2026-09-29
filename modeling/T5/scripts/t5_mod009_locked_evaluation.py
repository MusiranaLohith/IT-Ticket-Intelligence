from pathlib import Path
import csv
import json
import sys
import time

import joblib
import numpy as np
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
    log_loss,
    brier_score_loss,
    precision_score,
    recall_score,
    f1_score,
)


csv.field_size_limit(sys.maxsize)


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T5_ROOT = PROJECT_ROOT / "modeling" / "T5"

EVALUATION = Path(
    "/run/media/whiteblack/User 1/Datasets/"
    "Mozilla_CORE/"
    "DTM-002_T5_EVAL_GROUP_AWARE.csv"
)

LOCK_FILE = (
    T5_ROOT
    / "contracts"
    / "t5_mod008_model_selection_lock.json"
)

MODEL_ARTIFACT = (
    T5_ROOT
    / "models"
    / "t5_mod007_calibration_models.joblib"
)

VECTORIZER_ARTIFACT = (
    T5_ROOT
    / "models"
    / "t5_mod007_calibrated_tfidf.joblib"
)

OUTPUT_PREDICTIONS = (
    T5_ROOT
    / "metrics"
    / "t5_mod009_locked_evaluation_predictions.npz"
)

OUTPUT_METRICS = (
    T5_ROOT
    / "metrics"
    / "t5_mod009_locked_evaluation_metrics.json"
)


FEATURE_COLUMNS = [
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
]

TARGET_COLUMN = "T5 target"

PROVENANCE_COLUMNS = [
    "Target event index",
    "Target change index",
    "Target time",
    "Target actor",
]


def fail(message):
    print(f"FAIL: {message}")
    sys.exit(1)


def combine_text(row):
    return "\n".join(
        f"{column}: {(row[column] or '').strip()}"
        for column in FEATURE_COLUMNS
    )


def load_evaluation_rows():
    rows = []

    with EVALUATION.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            fail(
                "Evaluation artifact has no header."
            )

        required_columns = (
            FEATURE_COLUMNS
            + [TARGET_COLUMN]
            + PROVENANCE_COLUMNS
        )

        missing = [
            column
            for column in required_columns
            if column not in reader.fieldnames
        ]

        if missing:
            fail(
                "Evaluation artifact is missing required "
                f"columns: {missing}"
            )

        print(
            f"Accepted evaluation columns: "
            f"{len(reader.fieldnames)}"
        )

        print(
            "Required inference features present: YES"
        )

        print(
            "Target column present: YES"
        )

        print(
            "Target/provenance columns present: YES"
        )

        for row in reader:
            target = row[TARGET_COLUMN].strip()

            if target not in {"0", "1"}:
                fail(
                    f"Invalid evaluation target: {target!r}"
                )

            rows.append(row)

    return rows


def calculate_metrics(
    y_true,
    probabilities,
):
    predictions = (
        probabilities >= 0.5
    ).astype(np.int8)

    return {
        "average_precision": float(
            average_precision_score(
                y_true,
                probabilities,
            )
        ),
        "pr_auc": float(
            average_precision_score(
                y_true,
                probabilities,
            )
        ),
        "roc_auc": float(
            roc_auc_score(
                y_true,
                probabilities,
            )
        ),
        "log_loss": float(
            log_loss(
                y_true,
                probabilities,
            )
        ),
        "brier_score": float(
            brier_score_loss(
                y_true,
                probabilities,
            )
        ),
        "threshold_0_5": {
            "precision": float(
                precision_score(
                    y_true,
                    predictions,
                    zero_division=0,
                )
            ),
            "recall": float(
                recall_score(
                    y_true,
                    predictions,
                    zero_division=0,
                )
            ),
            "f1": float(
                f1_score(
                    y_true,
                    predictions,
                    zero_division=0,
                )
            ),
            "positive_predictions": int(
                predictions.sum()
            ),
        },
    }


def main():
    overall_start = time.time()

    print("=" * 80)
    print("T5-MOD-009 — LOCKED EVALUATION")
    print("=" * 80)

    # ------------------------------------------------------------------
    # 1. Verify locked inputs
    # ------------------------------------------------------------------

    print("\n[1] Verify locked inputs")

    required_files = [
        EVALUATION,
        LOCK_FILE,
        MODEL_ARTIFACT,
        VECTORIZER_ARTIFACT,
    ]

    for path in required_files:
        if not path.exists():
            fail(
                f"Missing required artifact: {path}"
            )

    with LOCK_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        lock = json.load(file)

    if lock.get("status") != "MODEL_SELECTION_LOCKED":
        fail(
            "Model-selection lock is not active."
        )

    selected_method = (
        lock["selected_pipeline"]
        ["calibration"]
        ["selected_method"]
    )

    if selected_method != "sigmoid":
        fail(
            "Locked calibration method is not sigmoid."
        )

    if lock["data_controls"][
        "official_evaluation_used"
    ]:
        fail(
            "Lock says the official evaluation "
            "was already used."
        )

    print(
        f"Evaluation: {EVALUATION}"
    )

    print(
        "Selection lock: MODEL_SELECTION_LOCKED"
    )

    print(
        "Selected calibration: sigmoid"
    )

    print(
        "Evaluation previously used: False"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 2. Load evaluation artifact
    # ------------------------------------------------------------------

    print("\n[2] Load locked evaluation artifact")

    start = time.time()

    rows = load_evaluation_rows()

    elapsed = time.time() - start

    ids = [
        row["ID"]
        for row in rows
    ]

    if len(ids) != len(set(ids)):
        fail(
            "Evaluation contains duplicate IDs."
        )

    y_true = np.asarray(
        [
            int(row[TARGET_COLUMN])
            for row in rows
        ],
        dtype=np.int8,
    )

    positives = int(
        np.sum(y_true == 1)
    )

    negatives = int(
        np.sum(y_true == 0)
    )

    print(
        f"Rows: {len(rows)}"
    )

    print(
        f"Positive: {positives}"
    )

    print(
        f"Negative: {negatives}"
    )

    print(
        f"Unique IDs: {len(set(ids))}"
    )

    print(
        f"Load time: {elapsed:.2f} seconds"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 3. Prepare inference text
    # ------------------------------------------------------------------

    print("\n[3] Prepare inference text")

    evaluation_text = [
        combine_text(row)
        for row in rows
    ]

    print(
        f"Prepared {len(evaluation_text)} "
        "documents."
    )

    print(
        "Only Creation-time feature columns used:"
    )

    for column in FEATURE_COLUMNS:
        print(
            f"  - {column}"
        )

    print(
        "Target/provenance columns excluded "
        "from inference."
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 4. Load locked model components
    # ------------------------------------------------------------------

    print("\n[4] Load locked model components")

    artifact = joblib.load(
        MODEL_ARTIFACT
    )

    required_model_keys = {
        "base_model",
        "sigmoid_calibrator",
    }

    missing_model_keys = (
        required_model_keys
        - set(artifact.keys())
    )

    if missing_model_keys:
        fail(
            "Locked model artifact is missing: "
            f"{sorted(missing_model_keys)}"
        )

    base_model = artifact[
        "base_model"
    ]

    sigmoid_calibrator = artifact[
        "sigmoid_calibrator"
    ]

    vectorizer = joblib.load(
        VECTORIZER_ARTIFACT
    )

    print(
        "Base LogisticRegression loaded."
    )

    print(
        "Sigmoid calibrator loaded."
    )

    print(
        "TF-IDF vectorizer loaded."
    )

    print(
        "No fitting or refitting will occur."
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 5. Transform evaluation data
    # ------------------------------------------------------------------

    print("\n[5] Transform evaluation set")

    start = time.time()

    X_eval = vectorizer.transform(
        evaluation_text
    )

    elapsed = time.time() - start

    expected_features = len(
        vectorizer.vocabulary_
    )

    if X_eval.shape[1] != expected_features:
        fail(
            "Evaluation TF-IDF dimensionality does not "
            "match the locked vectorizer."
        )

    print(
        f"Evaluation matrix: "
        f"{X_eval.shape[0]} x {X_eval.shape[1]}"
    )

    print(
        f"Locked vocabulary size: "
        f"{expected_features}"
    )

    print(
        f"Transform time: "
        f"{elapsed:.2f} seconds"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 6. Generate base probabilities
    # ------------------------------------------------------------------

    print("\n[6] Generate base probabilities")

    start = time.time()

    p_base = base_model.predict_proba(
        X_eval
    )[:, 1]

    elapsed = time.time() - start

    print(
        f"Base probability range: "
        f"{p_base.min():.8f} "
        f"to {p_base.max():.8f}"
    )

    print(
        f"Base prediction time: "
        f"{elapsed:.2f} seconds"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 7. Apply locked sigmoid calibration
    # ------------------------------------------------------------------

    print("\n[7] Apply locked sigmoid calibration")

    epsilon = 1e-7

    clipped = np.clip(
        p_base,
        epsilon,
        1.0 - epsilon,
    )

    logits = np.log(
        clipped / (1.0 - clipped)
    ).reshape(-1, 1)

    start = time.time()

    p_duplicate = (
        sigmoid_calibrator
        .predict_proba(logits)[:, 1]
    )

    elapsed = time.time() - start

    print(
        f"Calibrated probability range: "
        f"{p_duplicate.min():.8f} "
        f"to {p_duplicate.max():.8f}"
    )

    print(
        f"Calibration time: "
        f"{elapsed:.2f} seconds"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 8. Locked evaluation
    # ------------------------------------------------------------------

    print("\n[8] Calculate locked evaluation metrics")

    metrics = calculate_metrics(
        y_true,
        p_duplicate,
    )

    print(
        f"Average Precision / PR-AUC: "
        f"{metrics['average_precision']:.12f}"
    )

    print(
        f"ROC-AUC: "
        f"{metrics['roc_auc']:.12f}"
    )

    print(
        f"Log Loss: "
        f"{metrics['log_loss']:.12f}"
    )

    print(
        f"Brier Score: "
        f"{metrics['brier_score']:.12f}"
    )

    print(
        f"Precision @0.5: "
        f"{metrics['threshold_0_5']['precision']:.12f}"
    )

    print(
        f"Recall @0.5: "
        f"{metrics['threshold_0_5']['recall']:.12f}"
    )

    print(
        f"F1 @0.5: "
        f"{metrics['threshold_0_5']['f1']:.12f}"
    )

    print(
        f"Positive predictions @0.5: "
        f"{metrics['threshold_0_5']['positive_predictions']}"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 9. Save locked evaluation artifacts
    # ------------------------------------------------------------------

    print("\n[9] Save locked evaluation artifacts")

    np.savez_compressed(
        OUTPUT_PREDICTIONS,
        y_true=y_true,
        p_duplicate=p_duplicate,
        p_base=p_base,
    )

    result = {
        "operation": "T5-MOD-009",
        "operation_name": "Locked Evaluation",

        "evaluation_artifact": str(
            EVALUATION
        ),

        "evaluation_population": {
            "rows": len(rows),
            "positive": positives,
            "negative": negatives,
            "unique_ids": len(set(ids)),
        },

        "locked_pipeline": {
            "features": FEATURE_COLUMNS,
            "representation": (
                "word-level TF-IDF unigram/bigram"
            ),
            "classifier": (
                "balanced LogisticRegression"
            ),
            "calibration": "sigmoid",
            "probability_output": "p_duplicate",
        },

        "metrics": metrics,

        "controls": {
            "model_refit": False,
            "calibrator_refit": False,
            "vectorizer_refit": False,
            "threshold_optimization": False,
            "evaluation_used_for_selection": False,
            "evaluation_used_for_calibration": False,
            "synthetic_data": False,
            "raw_archive_scanned": False,
            "target_provenance_used_as_feature": False,
        },

        "status": "LOCKED_EVALUATION_COMPLETE",
    }

    with OUTPUT_METRICS.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=2,
        )

        file.write("\n")

    print(
        f"Predictions: "
        f"{OUTPUT_PREDICTIONS}"
    )

    print(
        f"Metrics: "
        f"{OUTPUT_METRICS}"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # Final
    # ------------------------------------------------------------------

    total_elapsed = (
        time.time() - overall_start
    )

    print("\n" + "=" * 80)
    print(
        "T5-MOD-009 RESULT: "
        "LOCKED_EVALUATION_COMPLETE"
    )
    print("=" * 80)

    print(
        f"\nTotal elapsed time: "
        f"{total_elapsed:.2f} seconds"
    )

    print(
        "Model refit: NO"
    )

    print(
        "Calibrator refit: NO"
    )

    print(
        "Vectorizer refit: NO"
    )

    print(
        "Threshold optimization: NO"
    )

    print(
        "Evaluation used for selection: NO"
    )


if __name__ == "__main__":
    main()