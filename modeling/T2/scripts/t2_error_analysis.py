from pathlib import Path
import json
import sys

import joblib
import pandas as pd
from sklearn.metrics import confusion_matrix


# ============================================================
# T2-MOD-009
# Baseline Error & Distribution Analysis
#
# Analysis of T2-MOD-006:
# TF-IDF + Logistic Regression
#
# No model training.
# No test-set access.
# ============================================================

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T2_ROOT = PROJECT_ROOT / "modeling" / "T2"

TRAIN_FILE = T2_ROOT / "splits" / "train.csv"
VALIDATION_FILE = T2_ROOT / "splits" / "validation.csv"

MODEL_FILE = (
    T2_ROOT
    / "models"
    / "t2_baseline_tfidf_logreg.joblib"
)

ANALYSIS_ROOT = T2_ROOT / "analysis"

REPORT_FILE = (
    ANALYSIS_ROOT
    / "t2_baseline_error_analysis.json"
)

PREDICTIONS_FILE = (
    ANALYSIS_ROOT
    / "t2_baseline_validation_predictions.csv"
)

CONFUSION_FILE = (
    ANALYSIS_ROOT
    / "t2_baseline_confusion_matrix.csv"
)

EXPECTED_CLASSES = [
    "P1",
    "P2",
    "P3",
    "P4",
    "P5",
]


def fail(message):
    print(f"ANALYSIS_ERROR={message}")
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


def distribution(series):
    counts = (
        series
        .value_counts()
        .reindex(
            EXPECTED_CLASSES,
            fill_value=0,
        )
    )

    total = len(series)

    result = {}

    for class_name in EXPECTED_CLASSES:
        count = int(counts[class_name])

        result[class_name] = {
            "count": count,
            "percentage": (
                float(count / total * 100)
                if total > 0
                else 0.0
            ),
        }

    return result


def main():
    print("T2_MOD_009_START")

    ANALYSIS_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Verify required files.
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

    if not MODEL_FILE.exists():
        fail(
            f"MODEL_FILE_NOT_FOUND={MODEL_FILE}"
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
    # Verify no train/validation ID overlap.
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
    # Load the already-trained T2-MOD-006 artifact.
    #
    # No fitting occurs here.
    # --------------------------------------------------------
    artifact = joblib.load(
        MODEL_FILE
    )

    if artifact.get("task") != "T2":
        fail("MODEL_TASK_MISMATCH")

    if artifact.get("model_type") != "LogisticRegression":
        fail(
            "MODEL_TYPE_MISMATCH="
            f"{artifact.get('model_type')}"
        )

    vectorizer = artifact["vectorizer"]
    model = artifact["model"]

    # --------------------------------------------------------
    # Recreate validation representation.
    #
    # transform() only.
    # No vocabulary/IDF refitting.
    # --------------------------------------------------------
    validation_text = build_text(
        validation
    )

    X_validation = vectorizer.transform(
        validation_text
    )

    y_actual = validation[
        "target_priority"
    ]

    y_pred = model.predict(
        X_validation
    )

    # --------------------------------------------------------
    # Prediction distribution.
    # --------------------------------------------------------
    actual_distribution = distribution(
        y_actual
    )

    predicted_distribution = distribution(
        pd.Series(
            y_pred,
            name="prediction",
        )
    )

    # --------------------------------------------------------
    # Confusion matrix.
    # Rows = actual.
    # Columns = predicted.
    # --------------------------------------------------------
    cm = confusion_matrix(
        y_actual,
        y_pred,
        labels=EXPECTED_CLASSES,
    )

    confusion_df = pd.DataFrame(
        cm,
        index=EXPECTED_CLASSES,
        columns=EXPECTED_CLASSES,
    )

    confusion_df.index.name = "actual"

    # --------------------------------------------------------
    # Per-class error analysis.
    # --------------------------------------------------------
    per_class = {}

    for index, class_name in enumerate(
        EXPECTED_CLASSES
    ):
        actual_count = int(
            cm[index].sum()
        )

        correct_count = int(
            cm[index, index]
        )

        error_count = (
            actual_count - correct_count
        )

        error_rate = (
            error_count / actual_count
            if actual_count > 0
            else 0.0
        )

        predicted_as = {}

        for predicted_index, predicted_class in enumerate(
            EXPECTED_CLASSES
        ):
            predicted_as[predicted_class] = int(
                cm[index, predicted_index]
            )

        per_class[class_name] = {
            "actual_support": actual_count,
            "correct": correct_count,
            "errors": error_count,
            "error_rate": float(error_rate),
            "predicted_as": predicted_as,
        }

    # --------------------------------------------------------
    # Actual -> predicted error pairs.
    # --------------------------------------------------------
    error_pairs = []

    for actual_index, actual_class in enumerate(
        EXPECTED_CLASSES
    ):
        for predicted_index, predicted_class in enumerate(
            EXPECTED_CLASSES
        ):
            if actual_index == predicted_index:
                continue

            count = int(
                cm[
                    actual_index,
                    predicted_index,
                ]
            )

            if count > 0:
                error_pairs.append(
                    {
                        "actual": actual_class,
                        "predicted": predicted_class,
                        "count": count,
                    }
                )

    error_pairs.sort(
        key=lambda item: item["count"],
        reverse=True,
    )

    # --------------------------------------------------------
    # Train/validation class distribution shift.
    # --------------------------------------------------------
    train_distribution = distribution(
        train["target_priority"]
    )

    validation_distribution = distribution(
        validation["target_priority"]
    )

    distribution_shift = {}

    for class_name in EXPECTED_CLASSES:
        train_pct = train_distribution[
            class_name
        ]["percentage"]

        validation_pct = validation_distribution[
            class_name
        ]["percentage"]

        distribution_shift[class_name] = {
            "train_percentage": float(
                train_pct
            ),
            "validation_percentage": float(
                validation_pct
            ),
            "percentage_point_change": float(
                validation_pct - train_pct
            ),
        }

    # --------------------------------------------------------
    # Save validation predictions.
    #
    # This is an analysis artifact only.
    # --------------------------------------------------------
    prediction_df = validation[
        [
            "ID",
            "target_priority",
        ]
    ].copy()

    prediction_df[
        "predicted_priority"
    ] = y_pred

    prediction_df[
        "correct"
    ] = (
        prediction_df[
            "target_priority"
        ]
        == prediction_df[
            "predicted_priority"
        ]
    )

    prediction_df.to_csv(
        PREDICTIONS_FILE,
        index=False,
    )

    # --------------------------------------------------------
    # Save confusion matrix.
    # --------------------------------------------------------
    confusion_df.to_csv(
        CONFUSION_FILE
    )

    # --------------------------------------------------------
    # Final report.
    # --------------------------------------------------------
    report = {
        "operation": "T2-MOD-009",
        "operation_name": (
            "Baseline Error and Distribution Analysis"
        ),
        "task": "T2",
        "task_name": "Priority Prediction",
        "dataset": "Mozilla CORE",
        "reference_model": (
            "T2-MOD-006 TF-IDF + Logistic Regression"
        ),
        "test_used": False,
        "train_rows": int(len(train)),
        "validation_rows": int(len(validation)),
        "class_distribution": {
            "train": train_distribution,
            "validation": validation_distribution,
            "predicted_validation": predicted_distribution,
        },
        "distribution_shift": distribution_shift,
        "per_class_error_analysis": per_class,
        "error_pairs_ranked": error_pairs,
        "confusion_matrix": {
            "labels": EXPECTED_CLASSES,
            "rows_actual_columns_predicted": cm.tolist(),
        },
        "artifacts": {
            "predictions": str(PREDICTIONS_FILE),
            "confusion_matrix": str(CONFUSION_FILE),
        },
        "integrity": {
            "model_retrained": False,
            "train_validation_overlap": False,
            "test_loaded": False,
            "raw_source_modified": False,
            "split_artifacts_modified": False,
            "model_artifact_modified": False,
        },
        "status": "COMPLETE",
    }


    with REPORT_FILE.open(
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
    print("T2_MOD_009_COMPLETE")

    print("\nACTUAL_VALIDATION_DISTRIBUTION")

    for class_name in EXPECTED_CLASSES:
        values = validation_distribution[
            class_name
        ]

        print(
            f"{class_name} "
            f"COUNT={values['count']} "
            f"PERCENT={values['percentage']:.4f}"
        )

    print("\nPREDICTED_VALIDATION_DISTRIBUTION")

    for class_name in EXPECTED_CLASSES:
        values = predicted_distribution[
            class_name
        ]

        print(
            f"{class_name} "
            f"COUNT={values['count']} "
            f"PERCENT={values['percentage']:.4f}"
        )

    print("\nTRAIN_TO_VALIDATION_SHIFT")

    for class_name in EXPECTED_CLASSES:
        values = distribution_shift[
            class_name
        ]

        print(
            f"{class_name} "
            f"TRAIN={values['train_percentage']:.4f} "
            f"VALIDATION={values['validation_percentage']:.4f} "
            f"CHANGE_PP="
            f"{values['percentage_point_change']:.4f}"
        )

    print("\nTOP_ERROR_PAIRS")

    for item in error_pairs[:10]:
        print(
            f"ACTUAL={item['actual']} "
            f"PREDICTED={item['predicted']} "
            f"COUNT={item['count']}"
        )

    print("\nPER_CLASS_ERRORS")

    for class_name in EXPECTED_CLASSES:
        values = per_class[class_name]

        print(
            f"{class_name} "
            f"SUPPORT={values['actual_support']} "
            f"CORRECT={values['correct']} "
            f"ERRORS={values['errors']} "
            f"ERROR_RATE={values['error_rate']:.6f}"
        )

    print(f"\nPREDICTIONS={PREDICTIONS_FILE}")
    print(f"CONFUSION_MATRIX={CONFUSION_FILE}")
    print(f"REPORT={REPORT_FILE}")
    print("TEST_USED=False")
    print("STATUS=COMPLETE")


if __name__ == "__main__":
    main()