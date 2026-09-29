from pathlib import Path
import csv
import json
import joblib
import numpy as np

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)


# ============================================================
# T2-MOD-020
# Final Locked Test Evaluation
#
# Uses the already-trained T2-MOD-007 model.
#
# No training.
# No refitting.
# No parameter changes.
# Test is used ONLY for final evaluation.
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_ROOT = PROJECT_ROOT / "modeling" / "T2"

MODEL_FILE = (
    T2_ROOT
    / "models"
    / "t2_class_weighted_tfidf_logreg.joblib"
)

TEST_FILE = (
    T2_ROOT
    / "splits"
    / "test.csv"
)

OUTPUT_DIR = T2_ROOT / "analysis"

METRICS_FILE = (
    OUTPUT_DIR
    / "t2_final_test_metrics.json"
)

PREDICTIONS_FILE = (
    OUTPUT_DIR
    / "t2_final_test_predictions.csv"
)

CONFUSION_FILE = (
    OUTPUT_DIR
    / "t2_final_test_confusion_matrix.csv"
)

CLASSES = [
    "P1",
    "P2",
    "P3",
    "P4",
    "P5",
]


def load_test_data():
    """
    Load the frozen T2 test partition.

    Actual frozen schema:
        ID
        Creation time
        Summary
        Description
        target_priority
    """

    rows = []

    with TEST_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        required = {
            "ID",
            "Creation time",
            "Summary",
            "Description",
            "target_priority",
        }

        fields = set(
            reader.fieldnames or []
        )

        missing = required - fields

        if missing:
            raise RuntimeError(
                "TEST_SCHEMA_MISSING="
                + ",".join(sorted(missing))
            )

        for row in reader:

            summary = (
                row.get("Summary", "")
                or ""
            )

            description = (
                row.get("Description", "")
                or ""
            )

            text = (
                summary.strip()
                + " "
                + description.strip()
            ).strip()

            rows.append(
                {
                    "ID": row["ID"],
                    "Creation time": row[
                        "Creation time"
                    ],
                    "Summary": summary,
                    "Description": description,
                    "target_priority": (
                        row["target_priority"]
                    ),
                    "text": text,
                }
            )

    return rows


def predict_with_artifact(
    model_artifact,
    texts,
):
    """
    Predict using the already-fitted T2-MOD-007
    artifact.

    No fit/refit operation is performed.
    """

    # --------------------------------------------------------
    # Case 1: sklearn Pipeline
    # --------------------------------------------------------

    if hasattr(
        model_artifact,
        "predict",
    ):

        return model_artifact.predict(
            texts
        )

    # --------------------------------------------------------
    # Case 2: dictionary artifact
    # --------------------------------------------------------

    if isinstance(
        model_artifact,
        dict,
    ):

        vectorizer = None
        classifier = None

        for key, value in (
            model_artifact.items()
        ):

            key_lower = str(
                key
            ).lower()

            if (
                "vector" in key_lower
                or "tfidf" in key_lower
            ):
                vectorizer = value

            if (
                "classifier" in key_lower
                or "model" in key_lower
                or "logreg" in key_lower
            ):
                classifier = value

        if (
            vectorizer is None
            or classifier is None
        ):
            raise RuntimeError(
                "MODEL_ARTIFACT_COMPONENTS_NOT_FOUND"
            )

        features = vectorizer.transform(
            texts
        )

        return classifier.predict(
            features
        )

    raise RuntimeError(
        "UNSUPPORTED_MODEL_ARTIFACT"
    )


def main():

    print("T2_MOD_020_START")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Verify artifacts.
    # --------------------------------------------------------

    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            f"MODEL_NOT_FOUND={MODEL_FILE}"
        )

    if not TEST_FILE.exists():
        raise FileNotFoundError(
            f"TEST_FILE_NOT_FOUND={TEST_FILE}"
        )

    # --------------------------------------------------------
    # Load the already-trained model.
    # --------------------------------------------------------

    model_artifact = joblib.load(
        MODEL_FILE
    )

    # --------------------------------------------------------
    # Load frozen test data.
    # --------------------------------------------------------

    rows = load_test_data()

    if len(rows) != 4425:
        raise RuntimeError(
            "UNEXPECTED_TEST_ROWS="
            f"{len(rows)}"
        )

    y_true = np.array(
        [
            row["target_priority"]
            for row in rows
        ]
    )

    texts = [
        row["text"]
        for row in rows
    ]

    # --------------------------------------------------------
    # Validate test target classes.
    # --------------------------------------------------------

    observed_targets = set(
        y_true.tolist()
    )

    if observed_targets != set(
        CLASSES
    ):
        raise RuntimeError(
            "UNEXPECTED_TEST_CLASSES="
            + ",".join(
                sorted(observed_targets)
            )
        )

    # --------------------------------------------------------
    # FINAL PREDICTION
    #
    # No fitting.
    # --------------------------------------------------------

    y_pred = predict_with_artifact(
        model_artifact,
        texts,
    )

    y_pred = np.asarray(
        y_pred
    )

    # --------------------------------------------------------
    # Metrics.
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_true,
        y_pred,
    )

    macro_f1 = f1_score(
        y_true,
        y_pred,
        labels=CLASSES,
        average="macro",
        zero_division=0,
    )

    weighted_f1 = f1_score(
        y_true,
        y_pred,
        labels=CLASSES,
        average="weighted",
        zero_division=0,
    )

    report = classification_report(
        y_true,
        y_pred,
        labels=CLASSES,
        output_dict=True,
        zero_division=0,
    )

    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=CLASSES,
    )

    # --------------------------------------------------------
    # Actual / predicted distributions.
    # --------------------------------------------------------

    actual_distribution = {}

    predicted_distribution = {}

    for label in CLASSES:

        actual_distribution[label] = int(
            np.sum(
                y_true == label
            )
        )

        predicted_distribution[label] = int(
            np.sum(
                y_pred == label
            )
        )

    # --------------------------------------------------------
    # Save predictions.
    # --------------------------------------------------------

    with PREDICTIONS_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            [
                "ID",
                "Creation time",
                "actual_priority",
                "predicted_priority",
            ]
        )

        for row, prediction in zip(
            rows,
            y_pred,
        ):

            writer.writerow(
                [
                    row["ID"],
                    row["Creation time"],
                    row["target_priority"],
                    prediction,
                ]
            )

    # --------------------------------------------------------
    # Save confusion matrix.
    # --------------------------------------------------------

    with CONFUSION_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            ["actual\\predicted"]
            + CLASSES
        )

        for label, values in zip(
            CLASSES,
            cm,
        ):

            writer.writerow(
                [label]
                + values.tolist()
            )

    # --------------------------------------------------------
    # Save final metrics.
    # --------------------------------------------------------

    metrics = {
        "operation": "T2-MOD-020",
        "operation_name": (
            "Final Locked Test Evaluation"
        ),

        "task": "T2",
        "dataset": "Mozilla CORE",

        "model": {
            "operation": "T2-MOD-007",
            "name": (
                "TF-IDF + Class-Weighted "
                "Logistic Regression"
            ),
            "artifact": str(
                MODEL_FILE
            ),
            "refitted": False,
        },

        "test": {
            "artifact": str(
                TEST_FILE
            ),
            "rows": len(rows),
            "schema": [
                "ID",
                "Creation time",
                "Summary",
                "Description",
                "target_priority",
            ],
            "used_for_final_evaluation": True,
        },

        "training": {
            "performed": False,
            "refit": False,
            "parameter_changes": False,
        },

        "metrics": {
            "accuracy": float(
                accuracy
            ),
            "macro_f1": float(
                macro_f1
            ),
            "weighted_f1": float(
                weighted_f1
            ),

            "per_class": {
                label: {
                    "precision": float(
                        report[label][
                            "precision"
                        ]
                    ),
                    "recall": float(
                        report[label][
                            "recall"
                        ]
                    ),
                    "f1": float(
                        report[label][
                            "f1-score"
                        ]
                    ),
                    "support": int(
                        report[label][
                            "support"
                        ]
                    ),
                }
                for label in CLASSES
            },
        },

        "actual_distribution": (
            actual_distribution
        ),

        "predicted_distribution": (
            predicted_distribution
        ),

        "confusion_matrix": (
            cm.tolist()
        ),

        "artifacts": {
            "predictions": str(
                PREDICTIONS_FILE
            ),
            "confusion_matrix": str(
                CONFUSION_FILE
            ),
        },

        "test_evaluation_status": (
            "COMPLETE"
        ),
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
    # Console output.
    # --------------------------------------------------------

    print(
        "MODEL=T2-MOD-007"
    )

    print(
        "TEST_ROWS="
        f"{len(rows)}"
    )

    print(
        "TRAINING_PERFORMED=False"
    )

    print(
        "REFIT=False"
    )

    print(
        "ACCURACY="
        f"{accuracy:.6f}"
    )

    print(
        "MACRO_F1="
        f"{macro_f1:.6f}"
    )

    print(
        "WEIGHTED_F1="
        f"{weighted_f1:.6f}"
    )

    for label in CLASSES:

        print(
            f"{label}_PRECISION="
            f"{report[label]['precision']:.6f}"
        )

        print(
            f"{label}_RECALL="
            f"{report[label]['recall']:.6f}"
        )

        print(
            f"{label}_F1="
            f"{report[label]['f1-score']:.6f}"
        )

        print(
            f"{label}_SUPPORT="
            f"{int(report[label]['support'])}"
        )

    print(
        "TEST_USED=True"
    )

    print(
        "FINAL_TEST_EVALUATION=True"
    )

    print(
        f"METRICS={METRICS_FILE}"
    )

    print(
        f"PREDICTIONS={PREDICTIONS_FILE}"
    )

    print(
        f"CONFUSION_MATRIX={CONFUSION_FILE}"
    )

    print(
        "STATUS=COMPLETE"
    )

    print(
        "T2_MOD_020_COMPLETE"
    )


if __name__ == "__main__":
    main()