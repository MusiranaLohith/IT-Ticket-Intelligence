from pathlib import Path
import json
import sys

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)


# ============================================================
# T2-MOD-007
# Class-Weighted Baseline
#
# TF-IDF + class-weighted Logistic Regression
# Features: Summary + Description
# Target: target_priority
# ============================================================

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T2_ROOT = PROJECT_ROOT / "modeling" / "T2"

TRAIN_FILE = T2_ROOT / "splits" / "train.csv"
VALIDATION_FILE = T2_ROOT / "splits" / "validation.csv"

MODEL_ROOT = T2_ROOT / "models"
METRICS_ROOT = T2_ROOT / "metrics"
LOG_ROOT = T2_ROOT / "logs"

MODEL_FILE = MODEL_ROOT / "t2_class_weighted_tfidf_logreg.joblib"
METRICS_FILE = METRICS_ROOT / "t2_class_weighted_metrics.json"
CONFUSION_FILE = METRICS_ROOT / "t2_class_weighted_confusion_matrix.csv"
LOG_FILE = LOG_ROOT / "t2_class_weighted_run.json"

EXPECTED_CLASSES = [
    "P1",
    "P2",
    "P3",
    "P4",
    "P5",
]


def fail(message):
    print(f"CLASS_WEIGHTED_ERROR={message}")
    sys.exit(1)


def build_text(df):
    summary = (
        df["Summary"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    description = (
        df["Description"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    return (
        "summary: "
        + summary
        + " description: "
        + description
    )


def main():
    print("T2_MOD_007_START")

    if not TRAIN_FILE.exists():
        fail(f"TRAIN_FILE_NOT_FOUND={TRAIN_FILE}")

    if not VALIDATION_FILE.exists():
        fail(
            f"VALIDATION_FILE_NOT_FOUND="
            f"{VALIDATION_FILE}"
        )

    # --------------------------------------------------------
    # Load train and validation only.
    # Test remains untouched.
    # --------------------------------------------------------
    train = pd.read_csv(
        TRAIN_FILE,
        dtype={
            "ID": "string",
            "Summary": "string",
            "Description": "string",
            "target_priority": "string",
        },
        keep_default_na=False,
    )

    validation = pd.read_csv(
        VALIDATION_FILE,
        dtype={
            "ID": "string",
            "Summary": "string",
            "Description": "string",
            "target_priority": "string",
        },
        keep_default_na=False,
    )

    print(f"TRAIN_ROWS={len(train)}")
    print(f"VALIDATION_ROWS={len(validation)}")
    print("TEST_LOADED=False")

    # --------------------------------------------------------
    # Input integrity
    # --------------------------------------------------------
    required_columns = [
        "ID",
        "Summary",
        "Description",
        "target_priority",
    ]

    for column in required_columns:
        if column not in train.columns:
            fail(f"TRAIN_MISSING_COLUMN={column}")

        if column not in validation.columns:
            fail(
                f"VALIDATION_MISSING_COLUMN={column}"
            )

    if train["ID"].duplicated().any():
        fail("TRAIN_DUPLICATE_IDS")

    if validation["ID"].duplicated().any():
        fail("VALIDATION_DUPLICATE_IDS")

    overlap = set(train["ID"]).intersection(
        set(validation["ID"])
    )

    if overlap:
        fail(
            f"TRAIN_VALIDATION_ID_OVERLAP={len(overlap)}"
        )

    # --------------------------------------------------------
    # Target integrity
    # --------------------------------------------------------
    train_classes = set(train["target_priority"])
    validation_classes = set(
        validation["target_priority"]
    )

    unknown_train = sorted(
        train_classes - set(EXPECTED_CLASSES)
    )

    unknown_validation = sorted(
        validation_classes - set(EXPECTED_CLASSES)
    )

    if unknown_train:
        fail(
            f"UNKNOWN_TRAIN_CLASSES={unknown_train}"
        )

    if unknown_validation:
        fail(
            f"UNKNOWN_VALIDATION_CLASSES="
            f"{unknown_validation}"
        )

    # --------------------------------------------------------
    # Build text
    # --------------------------------------------------------
    X_train_text = build_text(train)
    X_validation_text = build_text(validation)

    y_train = train["target_priority"]
    y_validation = validation["target_priority"]

    # --------------------------------------------------------
    # TF-IDF
    #
    # Identical settings to T2-MOD-006.
    # Fit exclusively on training data.
    # --------------------------------------------------------
    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.98,
        sublinear_tf=True,
    )

    X_train = vectorizer.fit_transform(
        X_train_text
    )

    X_validation = vectorizer.transform(
        X_validation_text
    )

    print(
        f"TFIDF_TRAIN_SHAPE="
        f"{X_train.shape[0]}x{X_train.shape[1]}"
    )

    print(
        f"TFIDF_VALIDATION_SHAPE="
        f"{X_validation.shape[0]}x{X_validation.shape[1]}"
    )

    # --------------------------------------------------------
    # Class-weighted Logistic Regression
    #
    # ONLY intentional change from T2-MOD-006:
    # class_weight="balanced"
    # --------------------------------------------------------
    model = LogisticRegression(
        max_iter=2000,
        solver="lbfgs",
        class_weight="balanced",
        random_state=42,
    )

    model.fit(
        X_train,
        y_train,
    )

    # --------------------------------------------------------
    # Validation prediction
    # --------------------------------------------------------
    y_pred = model.predict(
        X_validation
    )

    y_proba = model.predict_proba(
        X_validation
    )

    # Prevent unused-variable confusion while explicitly
    # preserving probability generation for later work.
    probability_shape = y_proba.shape

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------
    accuracy = accuracy_score(
        y_validation,
        y_pred,
    )

    macro_f1 = f1_score(
        y_validation,
        y_pred,
        labels=EXPECTED_CLASSES,
        average="macro",
        zero_division=0,
    )

    weighted_f1 = f1_score(
        y_validation,
        y_pred,
        labels=EXPECTED_CLASSES,
        average="weighted",
        zero_division=0,
    )

    report = classification_report(
        y_validation,
        y_pred,
        labels=EXPECTED_CLASSES,
        output_dict=True,
        zero_division=0,
    )

    confusion = confusion_matrix(
        y_validation,
        y_pred,
        labels=EXPECTED_CLASSES,
    )

    # --------------------------------------------------------
    # Per-class metrics
    # --------------------------------------------------------
    per_class = {}

    for class_name in EXPECTED_CLASSES:
        per_class[class_name] = {
            "precision": float(
                report[class_name]["precision"]
            ),
            "recall": float(
                report[class_name]["recall"]
            ),
            "f1": float(
                report[class_name]["f1-score"]
            ),
            "support": int(
                report[class_name]["support"]
            ),
        }

    # --------------------------------------------------------
    # Output directories
    # --------------------------------------------------------
    MODEL_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    METRICS_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    LOG_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Save model artifact
    # --------------------------------------------------------
    artifact = {
        "task": "T2",
        "task_name": "Priority Prediction",
        "dataset": "Mozilla CORE",
        "model_type": "LogisticRegression",
        "vectorizer_type": "TfidfVectorizer",
        "feature_sources": [
            "Summary",
            "Description",
        ],
        "target": "target_priority",
        "classes": EXPECTED_CLASSES,
        "class_weight": "balanced",
        "vectorizer": vectorizer,
        "model": model,
    }

    joblib.dump(
        artifact,
        MODEL_FILE,
    )

    # --------------------------------------------------------
    # Save metrics
    # --------------------------------------------------------
    metrics = {
        "operation": "T2-MOD-007",
        "operation_name": "Class-Weighted Baseline",
        "task": "T2",
        "task_name": "Priority Prediction",
        "dataset": "Mozilla CORE",
        "comparison_reference": "T2-MOD-006",
        "intentional_change": (
            'LogisticRegression class_weight="balanced"'
        ),
        "model": {
            "type": "TF-IDF + class-weighted "
                    "Logistic Regression",
            "solver": "lbfgs",
            "max_iter": 2000,
            "class_weight": "balanced",
            "random_state": 42,
        },
        "features": {
            "sources": [
                "Summary",
                "Description",
            ],
            "description_missingness": (
                "retained as empty text; no information "
                "was fabricated"
            ),
            "tfidf_ngram_range": [1, 2],
            "tfidf_min_df": 2,
            "tfidf_max_df": 0.98,
            "tfidf_sublinear_tf": True,
        },
        "evaluation": {
            "split": "validation",
            "test_used": False,
            "accuracy": float(accuracy),
            "macro_f1": float(macro_f1),
            "weighted_f1": float(weighted_f1),
            "probability_shape": [
                int(probability_shape[0]),
                int(probability_shape[1]),
            ],
            "per_class": per_class,
        },
        "train": {
            "rows": int(len(train)),
            "features": int(X_train.shape[1]),
        },
        "validation": {
            "rows": int(len(validation)),
            "features": int(X_validation.shape[1]),
        },
    }

    with METRICS_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            metrics,
            f,
            indent=2,
        )

    # --------------------------------------------------------
    # Save confusion matrix
    # --------------------------------------------------------
    confusion_df = pd.DataFrame(
        confusion,
        index=EXPECTED_CLASSES,
        columns=EXPECTED_CLASSES,
    )

    confusion_df.index.name = "actual"

    confusion_df.to_csv(
        CONFUSION_FILE
    )

    # --------------------------------------------------------
    # Save run log
    # --------------------------------------------------------
    run_log = {
        "operation": "T2-MOD-007",
        "status": "COMPLETE",
        "train_rows": int(len(train)),
        "validation_rows": int(len(validation)),
        "test_loaded": False,
        "train_validation_overlap": 0,
        "comparison_reference": "T2-MOD-006",
        "intentional_change": (
            'class_weight="balanced"'
        ),
        "model_file": str(MODEL_FILE),
        "metrics_file": str(METRICS_FILE),
        "confusion_matrix_file": str(CONFUSION_FILE),
    }

    with LOG_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            run_log,
            f,
            indent=2,
        )

    # --------------------------------------------------------
    # Console output
    # --------------------------------------------------------
    print("T2_MOD_007_COMPLETE")
    print(f"ACCURACY={accuracy:.6f}")
    print(f"MACRO_F1={macro_f1:.6f}")
    print(f"WEIGHTED_F1={weighted_f1:.6f}")

    print("\nPER_CLASS_METRICS")

    for class_name in EXPECTED_CLASSES:
        values = per_class[class_name]

        print(
            f"{class_name} "
            f"PRECISION={values['precision']:.6f} "
            f"RECALL={values['recall']:.6f} "
            f"F1={values['f1']:.6f} "
            f"SUPPORT={values['support']}"
        )

    print(f"\nMODEL={MODEL_FILE}")
    print(f"METRICS={METRICS_FILE}")
    print(f"CONFUSION_MATRIX={CONFUSION_FILE}")
    print(f"LOG={LOG_FILE}")
    print("TEST_USED=False")
    print("STATUS=COMPLETE")


if __name__ == "__main__":
    main()