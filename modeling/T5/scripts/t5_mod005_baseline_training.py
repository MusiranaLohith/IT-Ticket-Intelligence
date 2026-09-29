from pathlib import Path
import csv
import json
import time
import sys

import joblib
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
    log_loss,
    brier_score_loss,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)


csv.field_size_limit(sys.maxsize)


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T5_ROOT = PROJECT_ROOT / "modeling" / "T5"

TRAIN_FILE = T5_ROOT / "splits" / "t5_model_train.csv"

VAL_FILE = T5_ROOT / "splits" / "t5_model_val.csv"

MODEL_DIR = T5_ROOT / "models"

METRIC_DIR = T5_ROOT / "metrics"

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

METRIC_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


VECTORIZER_PATH = MODEL_DIR / "t5_mod005_tfidf.joblib"

MODEL_PATH = MODEL_DIR / "t5_mod005_logreg.joblib"

VAL_PREDICTIONS_PATH = (
    METRIC_DIR / "t5_mod005_validation_predictions.npz"
)

METRICS_PATH = (
    METRIC_DIR / "t5_mod005_validation_metrics.json"
)


TEXT_COLUMNS = [
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
]

TARGET_COLUMN = "T5 target"

EXPECTED_TRAIN_ROWS = 418_898
EXPECTED_VAL_ROWS = 74_091

RANDOM_STATE = 42


def fail(message):
    print(f"FAIL: {message}")
    sys.exit(1)


def combine_text(row):
    """
    Combine only the frozen Creation-time predictive features.

    Explicit field markers preserve the distinction between
    Creator, Creator Detail, Summary, and Description.
    """

    parts = []

    for column in TEXT_COLUMNS:
        value = row[column]

        if value is None:
            value = ""

        value = value.strip()

        parts.append(
            f"{column}: {value}"
        )

    return "\n".join(parts)


def load_dataset(path, expected_rows):
    texts = []
    targets = []

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        expected_columns = [
            "ID",
            "Creation time",
            *TEXT_COLUMNS,
            TARGET_COLUMN,
        ]

        if reader.fieldnames != expected_columns:
            fail(
                f"{path.name}: schema mismatch."
            )

        for row_number, row in enumerate(
            reader,
            start=2,
        ):

            target = row[TARGET_COLUMN].strip()

            if target not in {"0", "1"}:
                fail(
                    f"{path.name}: invalid target "
                    f"{target!r} at row {row_number}."
                )

            texts.append(
                combine_text(row)
            )

            targets.append(
                int(target)
            )

    if len(texts) != expected_rows:
        fail(
            f"{path.name}: expected {expected_rows} rows, "
            f"found {len(texts)}."
        )

    return texts, np.asarray(
        targets,
        dtype=np.int8,
    )


def main():
    overall_start = time.time()

    print("=" * 80)
    print("T5-MOD-005 — BASELINE MODEL TRAINING")
    print("=" * 80)

    # ------------------------------------------------------------------
    # 1. Verify inputs
    # ------------------------------------------------------------------

    print("\n[1] Verify controlled inputs")

    if not TRAIN_FILE.exists():
        fail(
            f"Training file does not exist: {TRAIN_FILE}"
        )

    if not VAL_FILE.exists():
        fail(
            f"Validation file does not exist: {VAL_FILE}"
        )

    print(f"Training: {TRAIN_FILE}")
    print(f"Validation: {VAL_FILE}")
    print("PASS")

    # ------------------------------------------------------------------
    # 2. Load training data
    # ------------------------------------------------------------------

    print("\n[2] Load training data")

    start = time.time()

    X_train_text, y_train = load_dataset(
        TRAIN_FILE,
        EXPECTED_TRAIN_ROWS,
    )

    elapsed = time.time() - start

    print(f"Training rows: {len(X_train_text)}")
    print(
        f"Training positives: "
        f"{int(y_train.sum())}"
    )
    print(
        f"Training negatives: "
        f"{int((y_train == 0).sum())}"
    )
    print(f"Load time: {elapsed:.2f} seconds")
    print("PASS")

    # ------------------------------------------------------------------
    # 3. Load validation data
    # ------------------------------------------------------------------

    print("\n[3] Load validation data")

    start = time.time()

    X_val_text, y_val = load_dataset(
        VAL_FILE,
        EXPECTED_VAL_ROWS,
    )

    elapsed = time.time() - start

    print(f"Validation rows: {len(X_val_text)}")
    print(
        f"Validation positives: "
        f"{int(y_val.sum())}"
    )
    print(
        f"Validation negatives: "
        f"{int((y_val == 0).sum())}"
    )
    print(f"Load time: {elapsed:.2f} seconds")
    print("PASS")

    # ------------------------------------------------------------------
    # 4. Fit TF-IDF
    # ------------------------------------------------------------------

    print("\n[4] Fit word TF-IDF")

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_features=100_000,
        sublinear_tf=True,
        lowercase=True,
    )

    start = time.time()

    X_train = vectorizer.fit_transform(
        X_train_text
    )

    elapsed = time.time() - start

    print(f"Vocabulary size: {len(vectorizer.vocabulary_)}")
    print(
        f"Training matrix: "
        f"{X_train.shape[0]} x {X_train.shape[1]}"
    )
    print(
        f"Training matrix non-zero entries: "
        f"{X_train.nnz}"
    )
    print(f"TF-IDF fit time: {elapsed:.2f} seconds")
    print("PASS")

    # ------------------------------------------------------------------
    # 5. Transform validation
    # ------------------------------------------------------------------

    print("\n[5] Transform validation data")

    start = time.time()

    X_val = vectorizer.transform(
        X_val_text
    )

    elapsed = time.time() - start

    print(
        f"Validation matrix: "
        f"{X_val.shape[0]} x {X_val.shape[1]}"
    )
    print(
        f"Validation matrix non-zero entries: "
        f"{X_val.nnz}"
    )
    print(
        f"Validation transform time: "
        f"{elapsed:.2f} seconds"
    )
    print("PASS")

    # ------------------------------------------------------------------
    # 6. Train Logistic Regression
    # ------------------------------------------------------------------

    print("\n[6] Train Logistic Regression")

    model = LogisticRegression(
        solver="liblinear",
        class_weight="balanced",
        max_iter=1000,
        random_state=RANDOM_STATE,
    )

    start = time.time()

    model.fit(
        X_train,
        y_train,
    )

    elapsed = time.time() - start

    print("Model: LogisticRegression")
    print("Solver: liblinear")
    print("class_weight: balanced")
    print(f"Iterations: {model.n_iter_}")
    print(f"Training time: {elapsed:.2f} seconds")
    print("PASS")

    # ------------------------------------------------------------------
    # 7. Generate validation probabilities
    # ------------------------------------------------------------------

    print("\n[7] Generate validation probabilities")

    start = time.time()

    val_probability = model.predict_proba(
        X_val
    )[:, 1]

    val_prediction = (
        val_probability >= 0.5
    ).astype(np.int8)

    elapsed = time.time() - start

    print(
        f"Probability range: "
        f"{val_probability.min():.8f} "
        f"to {val_probability.max():.8f}"
    )
    print(
        f"Positive predictions @ 0.5: "
        f"{int(val_prediction.sum())}"
    )
    print(f"Scoring time: {elapsed:.2f} seconds")
    print("PASS")

    # ------------------------------------------------------------------
    # 8. Calculate validation metrics
    # ------------------------------------------------------------------

    print("\n[8] Calculate validation metrics")

    average_precision = average_precision_score(
        y_val,
        val_probability,
    )

    roc_auc = roc_auc_score(
        y_val,
        val_probability,
    )

    logloss = log_loss(
        y_val,
        val_probability,
    )

    brier = brier_score_loss(
        y_val,
        val_probability,
    )

    precision = precision_score(
        y_val,
        val_prediction,
        zero_division=0,
    )

    recall = recall_score(
        y_val,
        val_prediction,
        zero_division=0,
    )

    f1 = f1_score(
        y_val,
        val_prediction,
        zero_division=0,
    )

    cm = confusion_matrix(
        y_val,
        val_prediction,
        labels=[0, 1],
    )

    tn, fp, fn, tp = cm.ravel()

    metrics = {
        "operation": "T5-MOD-005",
        "operation_name": "Baseline Model Training",
        "task": "T5 Binary Duplicate Detection",
        "model": {
            "representation": "word_tfidf",
            "ngram_range": [1, 2],
            "min_df": 2,
            "max_features": 100_000,
            "sublinear_tf": True,
            "classifier": "LogisticRegression",
            "solver": "liblinear",
            "class_weight": "balanced",
            "max_iter": 1000,
            "random_state": RANDOM_STATE,
        },
        "training": {
            "rows": int(len(y_train)),
            "positive": int(y_train.sum()),
            "negative": int((y_train == 0).sum()),
        },
        "validation": {
            "rows": int(len(y_val)),
            "positive": int(y_val.sum()),
            "negative": int((y_val == 0).sum()),
        },
        "metrics": {
            "average_precision": float(
                average_precision
            ),
            "pr_auc": float(
                average_precision
            ),
            "roc_auc": float(
                roc_auc
            ),
            "log_loss": float(
                logloss
            ),
            "brier_score_loss": float(
                brier
            ),
            "precision_at_0_5": float(
                precision
            ),
            "recall_at_0_5": float(
                recall
            ),
            "f1_at_0_5": float(
                f1
            ),
        },
        "confusion_matrix_at_0_5": {
            "labels": [0, 1],
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "true_positive": int(tp),
        },
        "probability_output": {
            "column": "p_duplicate",
            "minimum": float(
                val_probability.min()
            ),
            "maximum": float(
                val_probability.max()
            ),
            "mean": float(
                val_probability.mean()
            ),
        },
        "evaluation_set_used": False,
        "threshold_optimization": False,
        "status": "BASELINE_VALIDATION_COMPLETE",
    }

    print(
        f"Average Precision: "
        f"{average_precision:.6f}"
    )

    print(
        f"PR-AUC: "
        f"{average_precision:.6f}"
    )

    print(
        f"ROC-AUC: "
        f"{roc_auc:.6f}"
    )

    print(
        f"Log Loss: "
        f"{logloss:.6f}"
    )

    print(
        f"Brier Score: "
        f"{brier:.6f}"
    )

    print(
        f"Precision @ 0.5: "
        f"{precision:.6f}"
    )

    print(
        f"Recall @ 0.5: "
        f"{recall:.6f}"
    )

    print(
        f"F1 @ 0.5: "
        f"{f1:.6f}"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 9. Save model artifacts
    # ------------------------------------------------------------------

    print("\n[9] Save model artifacts")

    joblib.dump(
        vectorizer,
        VECTORIZER_PATH,
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    np.savez_compressed(
        VAL_PREDICTIONS_PATH,
        y_true=y_val,
        p_duplicate=val_probability,
        y_pred_0_5=val_prediction,
    )

    with METRICS_PATH.open(
        "w",
        encoding="utf-8",
    ) as metrics_file:

        json.dump(
            metrics,
            metrics_file,
            indent=2,
        )

        metrics_file.write("\n")

    print(f"Vectorizer: {VECTORIZER_PATH}")
    print(f"Model: {MODEL_PATH}")
    print(
        f"Validation predictions: "
        f"{VAL_PREDICTIONS_PATH}"
    )
    print(f"Metrics: {METRICS_PATH}")
    print("PASS")

    # ------------------------------------------------------------------
    # Final
    # ------------------------------------------------------------------

    total_elapsed = time.time() - overall_start

    print("\n" + "=" * 80)
    print("T5-MOD-005 RESULT: BASELINE_VALIDATION_COMPLETE")
    print("=" * 80)

    print(
        f"\nTotal elapsed time: "
        f"{total_elapsed:.2f} seconds"
    )

    print("\nOfficial T5 evaluation set: NOT USED.")
    print("Threshold optimization: NOT PERFORMED.")
    print("Model selection: NOT PERFORMED.")
    print("Baseline model and validation outputs saved.")


if __name__ == "__main__":
    main()