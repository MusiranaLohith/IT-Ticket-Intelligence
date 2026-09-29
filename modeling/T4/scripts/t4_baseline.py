from pathlib import Path
import json
import time

import joblib
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

TRAIN_PATH = PROJECT_ROOT / "modeling" / "T4" / "derived" / "t4_train.csv"
EVAL_PATH = PROJECT_ROOT / "modeling" / "T4" / "derived" / "t4_eval.csv"

MODEL_DIR = PROJECT_ROOT / "modeling" / "T4" / "models"
REPORT_DIR = PROJECT_ROOT / "modeling" / "T4" / "reports"

MODEL_PATH = MODEL_DIR / "t4_baseline_tfidf_logreg.joblib"
REPORT_PATH = REPORT_DIR / "t4_baseline_report.json"


# ============================================================
# FROZEN CONTRACT
# ============================================================

FEATURES = [
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
]

TARGET = "target_assignee"

EXPECTED_TRAIN_ROWS = 142501
EXPECTED_EVAL_ROWS = 35626

TOP_K_VALUES = [1, 3, 5, 10]


# ============================================================
# HELPERS
# ============================================================

def fail(message):
    raise RuntimeError(f"T4-MOD-006_FAILED: {message}")


def combine_features(df):
    """
    Combine Creation-time admitted features into one text field.

    Explicit field markers preserve the distinction between metadata
    fields and ticket text while remaining compatible with word TF-IDF.
    """
    parts = []

    for feature in FEATURES:
        values = df[feature].fillna("").astype(str).str.strip()

        if feature == "Creator":
            prefix = " creator "
        elif feature == "Creator Detail":
            prefix = " creator_detail "
        elif feature == "Summary":
            prefix = " summary "
        elif feature == "Description":
            prefix = " description "
        else:
            prefix = " "

        parts.append(prefix + values)

    combined = parts[0]

    for part in parts[1:]:
        combined = combined + part

    return combined


def top_k_accuracy(y_true, probabilities, classes, k):
    """
    Top-k exact target hit rate.

    A row is counted as correct when its true target is among
    the model's k highest-probability training-observed candidates.
    """
    k = min(k, probabilities.shape[1])

    top_indices = np.argpartition(
        probabilities,
        -k,
        axis=1
    )[:, -k:]

    top_classes = classes[top_indices]

    hits = np.any(
        top_classes == np.asarray(y_true)[:, None],
        axis=1
    )

    return float(np.mean(hits))


def candidate_coverage_metrics(y_true, candidate_set):
    y_true = np.asarray(y_true)

    covered_mask = np.isin(y_true, list(candidate_set))

    covered_rows = int(covered_mask.sum())
    unseen_rows = int((~covered_mask).sum())

    covered_rate = covered_rows / len(y_true)

    unseen_rate = unseen_rows / len(y_true)

    return {
        "evaluation_rows": int(len(y_true)),
        "covered_rows": covered_rows,
        "unseen_target_rows": unseen_rows,
        "covered_row_rate": float(covered_rate),
        "unseen_target_rate": float(unseen_rate),
    }


def class_concentration(predicted):
    counts = pd.Series(predicted).value_counts()

    total = len(predicted)

    def share(top_n):
        return float(
            counts.head(top_n).sum() / total
        )

    return {
        "prediction_class_count": int(counts.shape[0]),
        "prediction_top_1_share": share(1),
        "prediction_top_10_share": share(10),
        "prediction_top_50_share": share(50),
        "prediction_top_100_share": share(100),
    }


# ============================================================
# MAIN
# ============================================================

def main():

    start_time = time.time()

    # --------------------------------------------------------
    # Input checks
    # --------------------------------------------------------

    if not TRAIN_PATH.exists():
        fail(f"Missing training split: {TRAIN_PATH}")

    if not EVAL_PATH.exists():
        fail(f"Missing evaluation split: {EVAL_PATH}")

    train_df = pd.read_csv(
        TRAIN_PATH,
        low_memory=False
    )

    eval_df = pd.read_csv(
        EVAL_PATH,
        low_memory=False
    )

    if len(train_df) != EXPECTED_TRAIN_ROWS:
        fail(
            f"Unexpected training rows: "
            f"{len(train_df)} != {EXPECTED_TRAIN_ROWS}"
        )

    if len(eval_df) != EXPECTED_EVAL_ROWS:
        fail(
            f"Unexpected evaluation rows: "
            f"{len(eval_df)} != {EXPECTED_EVAL_ROWS}"
        )

    required_columns = FEATURES + [TARGET]

    for column in required_columns:
        if column not in train_df.columns:
            fail(f"Missing training column: {column}")

        if column not in eval_df.columns:
            fail(f"Missing evaluation column: {column}")

    # --------------------------------------------------------
    # Split integrity
    # --------------------------------------------------------

    train_ids = set(train_df["ID"])
    eval_ids = set(eval_df["ID"])

    id_overlap = train_ids & eval_ids

    if id_overlap:
        fail(
            f"Train/evaluation ID overlap detected: "
            f"{len(id_overlap)}"
        )

    # --------------------------------------------------------
    # Candidate space
    # --------------------------------------------------------

    training_candidates = np.array(
        sorted(
            train_df[TARGET]
            .dropna()
            .astype(str)
            .unique()
        ),
        dtype=object,
    )

    candidate_set = set(training_candidates)

    if len(training_candidates) != 4139:
        fail(
            "Unexpected training-observed candidate count: "
            f"{len(training_candidates)} != 4139"
        )

    y_train = train_df[TARGET].astype(str).to_numpy()
    y_eval = eval_df[TARGET].astype(str).to_numpy()

    evaluation_distinct_targets = set(y_eval)

    covered_eval_targets = (
        evaluation_distinct_targets & candidate_set
    )

    unseen_eval_targets = (
        evaluation_distinct_targets - candidate_set
    )

    coverage = candidate_coverage_metrics(
        y_eval,
        candidate_set,
    )

    # --------------------------------------------------------
    # Text construction
    # --------------------------------------------------------

    print("T4-MOD-006_START")
    print("LOADING_COMPLETE")
    print(f"TRAIN_ROWS={len(train_df)}")
    print(f"EVALUATION_ROWS={len(eval_df)}")
    print(f"TRAINING_CANDIDATES={len(training_candidates)}")
    print(
        "FEATURES="
        + "|".join(FEATURES)
    )
    print("BUILDING_COMBINED_TEXT=True")

    X_train_text = combine_features(train_df)
    X_eval_text = combine_features(eval_df)

    usable_train = X_train_text.str.strip().ne("").sum()
    usable_eval = X_eval_text.str.strip().ne("").sum()

    if usable_train != len(train_df):
        fail(
            "Training contains rows with empty combined text."
        )

    if usable_eval != len(eval_df):
        fail(
            "Evaluation contains rows with empty combined text."
        )

    # --------------------------------------------------------
    # TF-IDF
    # --------------------------------------------------------

    print("TFIDF_FITTING_START")

    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.995,
        sublinear_tf=True,
        max_features=100000,
        dtype=np.float32,
    )

    X_train = vectorizer.fit_transform(X_train_text)

    print("TFIDF_FITTING_COMPLETE")
    print(f"VOCABULARY_SIZE={len(vectorizer.vocabulary_)}")
    print(f"TRAIN_MATRIX_ROWS={X_train.shape[0]}")
    print(f"TRAIN_MATRIX_COLS={X_train.shape[1]}")
    print(f"TRAIN_MATRIX_NNZ={X_train.nnz}")

    X_eval = vectorizer.transform(X_eval_text)

    print("TFIDF_EVALUATION_TRANSFORM_COMPLETE")
    print(f"EVAL_MATRIX_ROWS={X_eval.shape[0]}")
    print(f"EVAL_MATRIX_COLS={X_eval.shape[1]}")
    print(f"EVAL_MATRIX_NNZ={X_eval.nnz}")

    # --------------------------------------------------------
    # Logistic Regression
    # --------------------------------------------------------

    print("LOGREG_FITTING_START")
    print("SOLVER=saga")
    print("MULTICLASS=multinomial")
    print("MAX_ITER=100")
    print("C=1.0")
    print("CLASS_WEIGHT=None")

    model = LogisticRegression(
        C=1.0,
        solver="saga",
        penalty="l2",
        max_iter=100,
        tol=1e-3,
        random_state=42,
    )

    model.fit(X_train, y_train)

    print("LOGREG_FITTING_COMPLETE")
    print(f"MODEL_CLASSES={len(model.classes_)}")
    print(f"MODEL_N_ITER={model.n_iter_}")

    # --------------------------------------------------------
    # Evaluation probabilities
    # --------------------------------------------------------

    print("PREDICTION_START")

    probabilities = model.predict_proba(X_eval)

    predicted_top1 = model.classes_[
        np.argmax(probabilities, axis=1)
    ]

    print("PREDICTION_COMPLETE")

    # --------------------------------------------------------
    # Primary metrics
    # --------------------------------------------------------

    metrics = {}

    for k in TOP_K_VALUES:
        metrics[f"top_{k}_accuracy"] = top_k_accuracy(
            y_eval,
            probabilities,
            model.classes_,
            k,
        )

    metrics["top_1_accuracy"] = float(
        accuracy_score(
            y_eval,
            predicted_top1
        )
    )

    # --------------------------------------------------------
    # F1 metrics
    # --------------------------------------------------------

    metrics["macro_f1"] = float(
        f1_score(
            y_eval,
            predicted_top1,
            average="macro",
            zero_division=0,
        )
    )

    metrics["weighted_f1"] = float(
        f1_score(
            y_eval,
            predicted_top1,
            average="weighted",
            zero_division=0,
        )
    )

    # Covered-only F1 is diagnostic.
    covered_mask = np.isin(
        y_eval,
        list(candidate_set)
    )

    if covered_mask.any():

        metrics["covered_only_top_1_accuracy"] = float(
            accuracy_score(
                y_eval[covered_mask],
                predicted_top1[covered_mask],
            )
        )

        metrics["covered_only_macro_f1"] = float(
            f1_score(
                y_eval[covered_mask],
                predicted_top1[covered_mask],
                average="macro",
                zero_division=0,
            )
        )

        metrics["covered_only_weighted_f1"] = float(
            f1_score(
                y_eval[covered_mask],
                predicted_top1[covered_mask],
                average="weighted",
                zero_division=0,
            )
        )

    # --------------------------------------------------------
    # Coverage / open-world diagnostics
    # --------------------------------------------------------

    concentration = class_concentration(predicted_top1)

    # Prediction rank behavior for unseen true targets.
    unseen_mask = ~covered_mask

    if unseen_mask.any():
        unseen_top1_accuracy = float(
            np.mean(
                y_eval[unseen_mask]
                == predicted_top1[unseen_mask]
            )
        )
    else:
        unseen_top1_accuracy = 0.0

    # For an unseen target, it cannot be present in a
    # training-observed candidate list. Therefore top-k exact
    # hit is necessarily zero for those rows.
    unseen_top_k_accuracy = {
        f"top_{k}_accuracy": 0.0
        for k in TOP_K_VALUES
    }

    # --------------------------------------------------------
    # Save model bundle
    # --------------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    model_bundle = {
        "task": "T4 — Specific Assignee Prediction",
        "model_name": "T4-MOD-006",
        "vectorizer": vectorizer,
        "model": model,
        "features": FEATURES,
        "target": TARGET,
        "candidate_space": training_candidates,
        "candidate_space_size": len(training_candidates),
        "prediction_boundary": "Creation time",
        "random_state": 42,
    }

    joblib.dump(
        model_bundle,
        MODEL_PATH,
        compress=3,
    )

    # --------------------------------------------------------
    # Report
    # --------------------------------------------------------

    elapsed = time.time() - start_time

    report = {
        "operation": "T4-MOD-006",
        "task": "T4 — Specific Assignee Prediction",
        "status": "BASELINE_EVALUATED",

        "training": {
            "rows": int(len(train_df)),
            "candidate_assignees": int(
                len(training_candidates)
            ),
            "usable_text_rows": int(usable_train),
        },

        "evaluation": {
            "rows": int(len(eval_df)),
            "distinct_targets": int(
                len(evaluation_distinct_targets)
            ),
            "covered_distinct_targets": int(
                len(covered_eval_targets)
            ),
            "unseen_distinct_targets": int(
                len(unseen_eval_targets)
            ),
            "covered_rows": coverage["covered_rows"],
            "unseen_target_rows": coverage[
                "unseen_target_rows"
            ],
            "covered_row_rate": coverage[
                "covered_row_rate"
            ],
            "unseen_target_rate": coverage[
                "unseen_target_rate"
            ],
        },

        "features": FEATURES,

        "baseline": {
            "model": "LogisticRegression",
            "solver": "saga",
            "multiclass": "multinomial",
            "C": 1.0,
            "penalty": "l2",
            "class_weight": None,
            "max_iter": 100,
            "tol": 1e-3,
            "random_state": 42,
            "tfidf": {
                "ngram_range": [1, 2],
                "min_df": 2,
                "max_df": 0.995,
                "sublinear_tf": True,
                "max_features": 100000,
                "dtype": "float32",
                "vocabulary_size": int(
                    len(vectorizer.vocabulary_)
                ),
            },
        },

        "metrics": metrics,

        "open_world_diagnostics": {
            "unseen_target_top_1_accuracy": unseen_top1_accuracy,
            **unseen_top_k_accuracy,
        },

        "prediction_concentration": concentration,

        "controls": {
            "raw_mozilla_accessed": False,
            "target_reconstructed": False,
            "candidate_space_from_training_only": True,
            "unseen_targets_retained": True,
            "unseen_targets_not_converted_to_negatives": True,
            "unseen_targets_not_dropped": True,
            "evaluation_used_only_after_fit": True,
            "test_used": False,
        },

        "modeling_state": {
            "model_fitted": True,
            "predictions_created": True,
            "evaluation_scored": True,
            "test_used": False,
        },

        "runtime_seconds": float(elapsed),

        "artifacts": {
            "model": str(MODEL_PATH),
            "report": str(REPORT_PATH),
        },
    }

    with open(
        REPORT_PATH,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            report,
            f,
            indent=2,
        )

    # --------------------------------------------------------
    # Terminal summary
    # --------------------------------------------------------

    print("T4-MOD-006_COMPLETE")
    print(f"TRAIN_ROWS={len(train_df)}")
    print(f"EVALUATION_ROWS={len(eval_df)}")
    print(
        f"TRAINING_CANDIDATES="
        f"{len(training_candidates)}"
    )
    print(
        f"EVALUATION_DISTINCT_TARGETS="
        f"{len(evaluation_distinct_targets)}"
    )
    print(
        f"COVERED_EVALUATION_ROWS="
        f"{coverage['covered_rows']}"
    )
    print(
        f"UNSEEN_EVALUATION_ROWS="
        f"{coverage['unseen_target_rows']}"
    )
    print(
        f"UNSEEN_EVALUATION_RATE="
        f"{coverage['unseen_target_rate']:.8f}"
    )

    print(
        f"TOP_1_ACCURACY="
        f"{metrics['top_1_accuracy']:.8f}"
    )
    print(
        f"TOP_3_ACCURACY="
        f"{metrics['top_3_accuracy']:.8f}"
    )
    print(
        f"TOP_5_ACCURACY="
        f"{metrics['top_5_accuracy']:.8f}"
    )
    print(
        f"TOP_10_ACCURACY="
        f"{metrics['top_10_accuracy']:.8f}"
    )
    print(
        f"MACRO_F1="
        f"{metrics['macro_f1']:.8f}"
    )
    print(
        f"WEIGHTED_F1="
        f"{metrics['weighted_f1']:.8f}"
    )

    print(
        f"COVERED_ONLY_TOP_1_ACCURACY="
        f"{metrics['covered_only_top_1_accuracy']:.8f}"
    )
    print(
        f"COVERED_ONLY_MACRO_F1="
        f"{metrics['covered_only_macro_f1']:.8f}"
    )
    print(
        f"COVERED_ONLY_WEIGHTED_F1="
        f"{metrics['covered_only_weighted_f1']:.8f}"
    )

    print(
        f"PREDICTION_CLASS_COUNT="
        f"{concentration['prediction_class_count']}"
    )
    print(
        f"PREDICTION_TOP_1_SHARE="
        f"{concentration['prediction_top_1_share']:.8f}"
    )
    print(
        f"PREDICTION_TOP_10_SHARE="
        f"{concentration['prediction_top_10_share']:.8f}"
    )

    print(f"RUNTIME_SECONDS={elapsed:.2f}")

    print("RAW_MOZILLA_ACCESSED=False")
    print("TARGET_RECONSTRUCTED=False")
    print("TEST_USED=False")
    print("STATUS=BASELINE_EVALUATED")
    print(f"MODEL={MODEL_PATH}")
    print(f"REPORT={REPORT_PATH}")


if __name__ == "__main__":
    main()
