from pathlib import Path
import json

import joblib
import pandas as pd
from sklearn.metrics import confusion_matrix


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

SPLIT_DIR = PROJECT_ROOT / "modeling" / "T3" / "splits"
MODEL_DIR = PROJECT_ROOT / "modeling" / "T3" / "models"
ANALYSIS_DIR = PROJECT_ROOT / "modeling" / "T3" / "analysis"

VALIDATION_PATH = SPLIT_DIR / "t3_validation.csv"
MODEL_PATH = MODEL_DIR / "t3_baseline_tfidf_logreg.joblib"
OUTPUT_PATH = ANALYSIS_DIR / "t3_error_analysis.json"

TARGET = "target_severity"
LABELS = ["S1", "S2", "S3", "S4"]


def combine_text(df):
    return (
        df["Summary"].fillna("").astype(str)
        + " "
        + df["Description"].fillna("").astype(str)
    ).str.strip()


def main():
    print("T3_MOD_012_START")

    validation = pd.read_csv(
        VALIDATION_PATH,
        keep_default_na=False,
    )

    artifact = joblib.load(MODEL_PATH)

    vectorizer = artifact["vectorizer"]
    model = artifact["model"]

    print(f"VALIDATION_ROWS={len(validation)}")

    X_text = combine_text(validation)
    y_true = validation[TARGET]

    X = vectorizer.transform(X_text)

    predictions = model.predict(X)

    print(f"FEATURE_SHAPE={X.shape}")

    matrix = confusion_matrix(
        y_true,
        predictions,
        labels=LABELS,
    )

    prediction_counts = (
        pd.Series(predictions)
        .value_counts()
        .reindex(LABELS, fill_value=0)
    )

    confusion_pairs = []

    for actual_index, actual_label in enumerate(LABELS):
        for predicted_index, predicted_label in enumerate(LABELS):
            if actual_label == predicted_label:
                continue

            count = int(
                matrix[actual_index, predicted_index]
            )

            if count > 0:
                confusion_pairs.append(
                    {
                        "actual": actual_label,
                        "predicted": predicted_label,
                        "count": count,
                    }
                )

    confusion_pairs.sort(
        key=lambda item: item["count"],
        reverse=True,
    )

    representative_errors = {}

    for pair in confusion_pairs:
        actual = pair["actual"]
        predicted = pair["predicted"]

        mask = (
            (y_true == actual)
            & (pd.Series(predictions, index=validation.index)
               == predicted)
        )

        examples = validation.loc[
            mask,
            ["ID", "Creation time", "Summary", "Description", TARGET],
        ].copy()

        examples["text_length"] = (
            examples["Summary"].fillna("").astype(str).str.len()
            + examples["Description"].fillna("").astype(str).str.len()
        )

        examples = examples.head(10)

        representative_errors[
            f"{actual}_TO_{predicted}"
        ] = [
            {
                "ID": str(row["ID"]),
                "Creation time": str(row["Creation time"]),
                "Summary": str(row["Summary"]),
                "Description": str(row["Description"]),
                "actual": str(row[TARGET]),
                "predicted": predicted,
                "text_length": int(row["text_length"]),
            }
            for _, row in examples.iterrows()
        ]

    results = {
        "task": "T3_SEVERITY_PREDICTION",
        "model": "T3-MOD-007",
        "analysis_type": "VALIDATION_ERROR_ANALYSIS",
        "validation_rows": int(len(validation)),
        "feature_count": int(X.shape[1]),
        "test_used": False,
        "confusion_matrix": matrix.tolist(),
        "labels": LABELS,
        "prediction_counts": {
            label: int(prediction_counts[label])
            for label in LABELS
        },
        "confusion_pairs": confusion_pairs,
        "representative_errors": representative_errors,
    }

    ANALYSIS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            results,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("CONFUSION_MATRIX")

    for row in matrix:
        print(
            " ".join(str(int(value)) for value in row)
        )

    print("PREDICTION_COUNTS")

    for label in LABELS:
        print(
            f"{label}_PREDICTED="
            f"{int(prediction_counts[label])}"
        )

    print("TOP_CONFUSIONS")

    for pair in confusion_pairs[:10]:
        print(
            f"{pair['actual']}->{pair['predicted']}="
            f"{pair['count']}"
        )

    print(
        f"REPRESENTATIVE_ERROR_PAIRS="
        f"{len(representative_errors)}"
    )

    print(f"OUTPUT={OUTPUT_PATH}")
    print("TEST_USED=False")
    print("RETRAINED=False")
    print("STATUS=ERROR_ANALYSIS_COMPLETE")
    print("T3_MOD_012_COMPLETE")


if __name__ == "__main__":
    main()