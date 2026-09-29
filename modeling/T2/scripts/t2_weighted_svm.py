from pathlib import Path
import json
import sys

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.svm import LinearSVC


# ============================================================
# T2-MOD-010
# Class-Weighted Linear SVM
#
# Controlled comparison against:
# T2-MOD-008: TF-IDF + Linear SVM
#
# Only intentional model change:
#     class_weight="balanced"
#
# Test data is NOT loaded.
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_ROOT = PROJECT_ROOT / "modeling" / "T2"

TRAIN_FILE = T2_ROOT / "splits" / "train.csv"
VALIDATION_FILE = T2_ROOT / "splits" / "validation.csv"

MODEL_FILE = (
    T2_ROOT
    / "models"
    / "t2_weighted_tfidf_linear_svm.joblib"
)

METRICS_FILE = (
    T2_ROOT
    / "metrics"
    / "t2_weighted_svm_metrics.json"
)

CONFUSION_FILE = (
    T2_ROOT
    / "metrics"
    / "t2_weighted_svm_confusion_matrix.csv"
)

LOG_FILE = (
    T2_ROOT
    / "logs"
    / "t2_weighted_svm_run.json"
)

CLASSES = [
    "P1",
    "P2",
    "P3",
    "P4",
    "P5",
]


def fail(message):
    print(f"MODEL_ERROR={message}")
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
    print("T2_MOD_010_START")

    # --------------------------------------------------------
    # Create output directories before writing artifacts.
    # --------------------------------------------------------
    (T2_ROOT / "models").mkdir(
        parents=True,
        exist_ok=True,
    )

    (T2_ROOT / "metrics").mkdir(
        parents=True,
        exist_ok=True,
    )

    (T2_ROOT / "logs").mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Verify inputs.
    # --------------------------------------------------------
    if not TRAIN_FILE.exists():
        fail(
            f"TRAIN_FILE_NOT_FOUND={TRAIN_FILE}"
        )

    if not VALIDATION_FILE.exists():
        fail(
            f"VALIDATION_FILE_NOT_FOUND="
            f"{VALIDATION_FILE}"
        )

    # --------------------------------------------------------
    # Load train and validation only.
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
    # Verify train/validation ID separation.
    # --------------------------------------------------------
    overlap = set(
        train["ID"]
    ).intersection(
        set(validation["ID"])
    )

    if overlap:
        fail(
            f"TRAIN_VALIDATION_ID_OVERLAP="
            f"{len(overlap)}"
        )

    # --------------------------------------------------------
    # Build Creation-time text representation.
    # --------------------------------------------------------
    X_train_text = build_text(train)
    X_validation_text = build_text(validation)

    y_train = train[
        "target_priority"
    ]

    y_validation = validation[
        "target_priority"
    ]

    # --------------------------------------------------------
    # TF-IDF
    #
    # Same configuration as T2-MOD-006/007/008.
    # Fit ONLY on training text.
    # --------------------------------------------------------
    vectorizer = TfidfVectorizer(
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
        "TFIDF_TRAIN_SHAPE="
        f"{X_train.shape[0]}x{X_train.shape[1]}"
    )

    print(
        "TFIDF_VALIDATION_SHAPE="
        f"{X_validation.shape[0]}x{X_validation.shape[1]}"
    )

    # --------------------------------------------------------
    # Class-weighted Linear SVM
    #
    # ONLY intentional model change:
    # class_weight="balanced"
    # --------------------------------------------------------
    model = LinearSVC(
        C=1.0,
        class_weight="balanced",
        random_state=42,
    )

    model.fit(
        X_train,
        y_train,
    )

    # --------------------------------------------------------
    # Validation prediction.
    # --------------------------------------------------------
    y_pred = model.predict(
        X_validation
    )

    accuracy = accuracy_score(
        y_validation,
        y_pred,
    )

    macro_f1 = f1_score(
        y_validation,
        y_pred,
        average="macro",
        zero_division=0,
    )

    weighted_f1 = f1_score(
        y_validation,
        y_pred,
        average="weighted",
        zero_division=0,
    )

    report = classification_report(
        y_validation,
        y_pred,
        labels=CLASSES,
        output_dict=True,
        zero_division=0,
    )

    cm = confusion_matrix(
        y_validation,
        y_pred,
        labels=CLASSES,
    )

    # --------------------------------------------------------
    # Save model artifact.
    # --------------------------------------------------------
    model_artifact = {
        "task": "T2",
        "task_name": "Priority Prediction",
        "dataset": "Mozilla CORE",
        "operation": "T2-MOD-010",
        "model_type": "LinearSVC",
        "class_weight": "balanced",
        "C": 1.0,
        "random_state": 42,
        "features": [
            "Summary",
            "Description",
        ],
        "prediction_boundary": "Creation",
        "target": "target_priority",
        "classes": CLASSES,
        "vectorizer": vectorizer,
        "model": model,
        "test_used": False,
    }

    joblib.dump(
        model_artifact,
        MODEL_FILE,
    )

    # --------------------------------------------------------
    # Save metrics.
    # --------------------------------------------------------
    metrics = {
        "operation": "T2-MOD-010",
        "operation_name": (
            "Class-Weighted Linear SVM"
        ),
        "task": "T2",
        "dataset": "Mozilla CORE",
        "model": "TF-IDF + LinearSVC",
        "class_weight": "balanced",
        "C": 1.0,
        "random_state": 42,
        "train_rows": int(len(train)),
        "validation_rows": int(len(validation)),
        "test_used": False,
        "accuracy": float(accuracy),
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "per_class": {
            class_name: {
                "precision": float(
                    report[class_name][
                        "precision"
                    ]
                ),
                "recall": float(
                    report[class_name][
                        "recall"
                    ]
                ),
                "f1": float(
                    report[class_name][
                        "f1-score"
                    ]
                ),
                "support": int(
                    report[class_name][
                        "support"
                    ]
                ),
            }
            for class_name in CLASSES
        },
        "tfidf": {
            "ngram_range": [1, 2],
            "min_df": 2,
            "max_df": 0.98,
            "sublinear_tf": True,
            "train_features": int(
                X_train.shape[1]
            ),
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
    # Save confusion matrix.
    # --------------------------------------------------------
    confusion_df = pd.DataFrame(
        cm,
        index=CLASSES,
        columns=CLASSES,
    )

    confusion_df.index.name = "actual"

    confusion_df.to_csv(
        CONFUSION_FILE
    )

    # --------------------------------------------------------
    # Save execution log.
    # --------------------------------------------------------
    log = {
        "operation": "T2-MOD-010",
        "status": "COMPLETE",
        "train_rows": int(len(train)),
        "validation_rows": int(
            len(validation)
        ),
        "test_used": False,
        "model_retrained": True,
        "class_weight": "balanced",
        "raw_source_modified": False,
        "split_artifacts_modified": False,
        "previous_model_artifacts_modified": False,
        "outputs": {
            "model": str(MODEL_FILE),
            "metrics": str(METRICS_FILE),
            "confusion_matrix": str(
                CONFUSION_FILE
            ),
        },
    }

    with LOG_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            log,
            f,
            indent=2,
        )

    # --------------------------------------------------------
    # Console output.
    # --------------------------------------------------------
    print("T2_MOD_010_COMPLETE")

    print(
        f"ACCURACY={accuracy:.6f}"
    )

    print(
        f"MACRO_F1={macro_f1:.6f}"
    )

    print(
        f"WEIGHTED_F1={weighted_f1:.6f}"
    )

    print("\nPER_CLASS_METRICS")

    for class_name in CLASSES:
        values = metrics[
            "per_class"
        ][class_name]

        print(
            f"{class_name} "
            f"PRECISION={values['precision']:.6f} "
            f"RECALL={values['recall']:.6f} "
            f"F1={values['f1']:.6f} "
            f"SUPPORT={values['support']}"
        )

    print(
        f"MODEL={MODEL_FILE}"
    )

    print(
        f"METRICS={METRICS_FILE}"
    )

    print(
        f"CONFUSION_MATRIX={CONFUSION_FILE}"
    )

    print(
        f"LOG={LOG_FILE}"
    )

    print("TEST_USED=False")
    print("STATUS=COMPLETE")


if __name__ == "__main__":
    main()