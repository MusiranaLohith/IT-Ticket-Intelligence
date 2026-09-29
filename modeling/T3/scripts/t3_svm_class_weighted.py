from pathlib import Path
import json

import pandas as pd
from joblib import dump
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support
from sklearn.svm import LinearSVC


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

DERIVED_PATH = PROJECT_ROOT / "modeling" / "T3" / "derived" / "t3_features.csv"
SPLIT_DIR = PROJECT_ROOT / "modeling" / "T3" / "splits"
MODEL_DIR = PROJECT_ROOT / "modeling" / "T3" / "models"
METRICS_DIR = PROJECT_ROOT / "modeling" / "T3" / "metrics"

MODEL_PATH = MODEL_DIR / "t3_svm_class_weighted.joblib"
METRICS_PATH = METRICS_DIR / "t3_svm_class_weighted_validation_metrics.json"

LABELS = ["S1", "S2", "S3", "S4"]


def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def main():
    print("T3_MOD_016_START")

    data = pd.read_csv(
        DERIVED_PATH,
        keep_default_na=False,
    )

    train_ids = pd.read_csv(SPLIT_DIR / "t3_train.csv")["ID"]
    validation_ids = pd.read_csv(SPLIT_DIR / "t3_validation.csv")["ID"]

    train = data[data["ID"].isin(train_ids)].copy()
    validation = data[data["ID"].isin(validation_ids)].copy()

    train = train.set_index("ID").loc[train_ids].reset_index()
    validation = validation.set_index("ID").loc[validation_ids].reset_index()

    train_text = (
        train["Summary"].map(clean_text)
        + " "
        + train["Description"].map(clean_text)
    )

    validation_text = (
        validation["Summary"].map(clean_text)
        + " "
        + validation["Description"].map(clean_text)
    )

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.98,
        sublinear_tf=True,
    )

    X_train = vectorizer.fit_transform(train_text)
    X_validation = vectorizer.transform(validation_text)

    y_train = train["target_severity"]
    y_validation = validation["target_severity"]

    model = LinearSVC(
        C=1.0,
        class_weight="balanced",
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_validation)

    accuracy = accuracy_score(y_validation, predictions)

    macro_f1 = f1_score(
        y_validation,
        predictions,
        labels=LABELS,
        average="macro",
        zero_division=0,
    )

    weighted_f1 = f1_score(
        y_validation,
        predictions,
        labels=LABELS,
        average="weighted",
        zero_division=0,
    )

    precision, recall, f1, support = precision_recall_fscore_support(
        y_validation,
        predictions,
        labels=LABELS,
        zero_division=0,
    )

    metrics = {
        "task": "T3_SEVERITY_PREDICTION",
        "model_id": "T3-MOD-016",
        "model_family": "LinearSVC",
        "class_weight": "balanced",
        "parameters": {
            "C": 1.0,
        },
        "features": {
            "fields": ["Summary", "Description"],
            "representation": "TF-IDF",
            "analyzer": "word",
            "ngram_range": [1, 2],
            "min_df": 2,
            "max_df": 0.98,
            "sublinear_tf": True,
        },
        "train_rows": len(train),
        "validation_rows": len(validation),
        "feature_dimensions": X_train.shape[1],
        "accuracy": float(accuracy),
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "per_class": {
            label: {
                "precision": float(precision[i]),
                "recall": float(recall[i]),
                "f1": float(f1[i]),
                "support": int(support[i]),
            }
            for i, label in enumerate(LABELS)
        },
        "test_used": False,
        "status": "CLASS_WEIGHTED_LINEAR_SVM_VALIDATION_COMPLETE",
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    dump(
        {
            "vectorizer": vectorizer,
            "model": model,
        },
        MODEL_PATH,
    )

    METRICS_PATH.write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )

    print(f"TRAIN_ROWS={len(train)}")
    print(f"VALIDATION_ROWS={len(validation)}")
    print(f"TRAIN_FEATURE_SHAPE={X_train.shape}")
    print(f"VALIDATION_FEATURE_SHAPE={X_validation.shape}")
    print(f"ACCURACY={accuracy:.6f}")
    print(f"MACRO_F1={macro_f1:.6f}")
    print(f"WEIGHTED_F1={weighted_f1:.6f}")

    for i, label in enumerate(LABELS):
        print(f"{label}_PRECISION={precision[i]:.6f}")
        print(f"{label}_RECALL={recall[i]:.6f}")
        print(f"{label}_F1={f1[i]:.6f}")
        print(f"{label}_SUPPORT={support[i]}")

    print(f"MODEL={MODEL_PATH}")
    print(f"METRICS={METRICS_PATH}")
    print("TEST_USED=False")
    print("STATUS=CLASS_WEIGHTED_LINEAR_SVM_VALIDATION_COMPLETE")
    print("T3_MOD_016_COMPLETE")


if __name__ == "__main__":
    main()