from pathlib import Path
import json

import joblib
import pandas as pd
from scipy.sparse import hstack

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

SPLIT_DIR = PROJECT_ROOT / "modeling" / "T3" / "splits"
MODEL_DIR = PROJECT_ROOT / "modeling" / "T3" / "models"
METRIC_DIR = PROJECT_ROOT / "modeling" / "T3" / "metrics"

TRAIN_PATH = SPLIT_DIR / "t3_train.csv"
VALIDATION_PATH = SPLIT_DIR / "t3_validation.csv"

MODEL_PATH = MODEL_DIR / "t3_word_char_tfidf_logreg.joblib"
METRICS_PATH = METRIC_DIR / "t3_word_char_validation_metrics.json"

TARGET = "target_severity"
LABELS = ["S1", "S2", "S3", "S4"]


def combine_text(df):
    return (
        df["Summary"].fillna("").astype(str)
        + " "
        + df["Description"].fillna("").astype(str)
    ).str.strip()


def main():
    print("T3_MOD_010_START")

    train = pd.read_csv(
        TRAIN_PATH,
        keep_default_na=False,
    )

    validation = pd.read_csv(
        VALIDATION_PATH,
        keep_default_na=False,
    )

    print(f"TRAIN_ROWS={len(train)}")
    print(f"VALIDATION_ROWS={len(validation)}")

    X_train_text = combine_text(train)
    X_validation_text = combine_text(validation)

    y_train = train[TARGET]
    y_validation = validation[TARGET]

    # Word-level representation
    word_vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.98,
        sublinear_tf=True,
    )

    X_train_word = word_vectorizer.fit_transform(
        X_train_text
    )

    X_validation_word = word_vectorizer.transform(
        X_validation_text
    )

    print(
        f"WORD_TRAIN_FEATURE_SHAPE={X_train_word.shape}"
    )
    print(
        f"WORD_VALIDATION_FEATURE_SHAPE="
        f"{X_validation_word.shape}"
    )

    # Character-level representation
    char_vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(3, 5),
        min_df=2,
        max_df=0.98,
        sublinear_tf=True,
    )

    X_train_char = char_vectorizer.fit_transform(
        X_train_text
    )

    X_validation_char = char_vectorizer.transform(
        X_validation_text
    )

    print(
        f"CHAR_TRAIN_FEATURE_SHAPE={X_train_char.shape}"
    )
    print(
        f"CHAR_VALIDATION_FEATURE_SHAPE="
        f"{X_validation_char.shape}"
    )

    # Combine sparse word + character representations
    X_train = hstack(
        [
            X_train_word,
            X_train_char,
        ],
        format="csr",
    )

    X_validation = hstack(
        [
            X_validation_word,
            X_validation_char,
        ],
        format="csr",
    )

    print(f"COMBINED_TRAIN_FEATURE_SHAPE={X_train.shape}")
    print(
        "COMBINED_VALIDATION_FEATURE_SHAPE="
        f"{X_validation.shape}"
    )

    model = LogisticRegression(
        max_iter=2000,
        solver="lbfgs",
        class_weight=None,
    )

    model.fit(
        X_train,
        y_train,
    )

    predictions = model.predict(
        X_validation
    )

    accuracy = accuracy_score(
        y_validation,
        predictions,
    )

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

    precision, recall, f1, support = (
        precision_recall_fscore_support(
            y_validation,
            predictions,
            labels=LABELS,
            zero_division=0,
        )
    )

    matrix = confusion_matrix(
        y_validation,
        predictions,
        labels=LABELS,
    )

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    METRIC_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact = {
        "word_vectorizer": word_vectorizer,
        "char_vectorizer": char_vectorizer,
        "model": model,
        "task": "T3_SEVERITY_PREDICTION",
        "target": TARGET,
        "features": [
            "Summary",
            "Description",
        ],
        "representation": (
            "Word TF-IDF + Character TF-IDF"
        ),
        "word_ngram_range": [1, 2],
        "char_ngram_range": [3, 5],
        "class_weight": None,
    }

    joblib.dump(
        artifact,
        MODEL_PATH,
    )

    per_class = {}

    for index, label in enumerate(LABELS):
        per_class[label] = {
            "precision": float(
                precision[index]
            ),
            "recall": float(
                recall[index]
            ),
            "f1": float(
                f1[index]
            ),
            "support": int(
                support[index]
            ),
        }

    metrics = {
        "task": "T3_SEVERITY_PREDICTION",
        "model": (
            "Word TF-IDF + Character TF-IDF "
            "+ Logistic Regression"
        ),
        "class_weight": None,
        "train_rows": int(len(train)),
        "validation_rows": int(len(validation)),
        "word_feature_count": int(
            X_train_word.shape[1]
        ),
        "char_feature_count": int(
            X_train_char.shape[1]
        ),
        "combined_feature_count": int(
            X_train.shape[1]
        ),
        "accuracy": float(accuracy),
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "per_class": per_class,
        "confusion_matrix": matrix.tolist(),
        "labels": LABELS,
        "test_used": False,
        "status": "VALIDATION_ONLY",
    }

    METRICS_PATH.write_text(
        json.dumps(
            metrics,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"ACCURACY={accuracy:.6f}")
    print(f"MACRO_F1={macro_f1:.6f}")
    print(f"WEIGHTED_F1={weighted_f1:.6f}")

    for label in LABELS:
        print(
            f"{label}_PRECISION="
            f"{per_class[label]['precision']:.6f}"
        )
        print(
            f"{label}_RECALL="
            f"{per_class[label]['recall']:.6f}"
        )
        print(
            f"{label}_F1="
            f"{per_class[label]['f1']:.6f}"
        )
        print(
            f"{label}_SUPPORT="
            f"{per_class[label]['support']}"
        )

    print(f"MODEL={MODEL_PATH}")
    print(f"METRICS={METRICS_PATH}")
    print("TEST_USED=False")
    print("STATUS=WORD_CHAR_BASELINE_COMPLETE")
    print("T3_MOD_010_COMPLETE")


if __name__ == "__main__":
    main()