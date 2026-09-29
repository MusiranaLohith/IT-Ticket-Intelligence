from pathlib import Path
import json
import time
import joblib
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, f1_score


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DERIVED_DIR = PROJECT_ROOT / "modeling" / "T4" / "derived"
RESULTS_DIR = PROJECT_ROOT / "modeling" / "T4" / "results"
CHECKPOINT_DIR = RESULTS_DIR / "r1_checkpoints"

TRAIN_PATH = DERIVED_DIR / "t4_train.csv"
EVAL_PATH = DERIVED_DIR / "t4_eval.csv"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------
# Controlled R1 configuration
# ---------------------------------------------------------------------

MAX_FEATURES = 20_000
NGRAM_RANGE = (1, 1)
MIN_DF = 2
MAX_DF = 0.995
SUBLINEAR_TF = True

C = 0.5
MAX_ITER = 300

TOP_KS = [1, 3, 5, 10]

EVAL_CHUNK_SIZE = 1000

MODEL_PATH = CHECKPOINT_DIR / "t4_r1_linear_svc.joblib"
VECTORIZER_PATH = CHECKPOINT_DIR / "t4_r1_tfidf.joblib"

SCORES_PATH = CHECKPOINT_DIR / "t4_r1_topk_predictions.npz"
METRICS_PATH = RESULTS_DIR / "t4_r1_metrics.json"


def combined_text(df: pd.DataFrame) -> pd.Series:
    cols = ["Creator", "Creator Detail", "Summary", "Description"]

    parts = []
    for col in cols:
        parts.append(df[col].fillna("").astype(str))

    text = parts[0]
    for part in parts[1:]:
        text = text + " " + part

    return text.str.strip()


def load_data():
    train = pd.read_csv(TRAIN_PATH)
    evaluation = pd.read_csv(EVAL_PATH)

    expected_train = 142501
    expected_eval = 35626

    if len(train) != expected_train:
        raise RuntimeError(
            f"Unexpected train rows: {len(train)} != {expected_train}"
        )

    if len(evaluation) != expected_eval:
        raise RuntimeError(
            f"Unexpected evaluation rows: {len(evaluation)} != {expected_eval}"
        )

    if train["target_assignee"].isna().any():
        raise RuntimeError("Blank training targets detected.")

    if evaluation["target_assignee"].isna().any():
        raise RuntimeError("Blank evaluation targets detected.")

    return train, evaluation


def main():
    overall_start = time.time()

    print("T4-MOD-006-R1_RECOVERY_START", flush=True)

    train, evaluation = load_data()

    print(
        f"DATA_LOADED "
        f"TRAIN_ROWS={len(train)} "
        f"EVALUATION_ROWS={len(evaluation)}",
        flush=True,
    )

    # ---------------------------------------------------------------
    # Candidate space is defined ONLY from training
    # ---------------------------------------------------------------

    candidate_labels = np.sort(
        train["target_assignee"].astype(str).unique()
    )

    label_to_index = {
        label: idx for idx, label in enumerate(candidate_labels)
    }

    print(
        f"TRAINING_CANDIDATES={len(candidate_labels)}",
        flush=True,
    )

    # ---------------------------------------------------------------
    # Prepare text
    # ---------------------------------------------------------------

    print("BUILDING_TRAIN_TEXT_START", flush=True)
    train_text = combined_text(train)
    print("BUILDING_TRAIN_TEXT_COMPLETE", flush=True)

    print("BUILDING_EVALUATION_TEXT_START", flush=True)
    eval_text = combined_text(evaluation)
    print("BUILDING_EVALUATION_TEXT_COMPLETE", flush=True)

    # ---------------------------------------------------------------
    # TF-IDF
    # ---------------------------------------------------------------

    vectorizer = None
    X_train = None
    X_eval = None

    if VECTORIZER_PATH.exists():
        print("TFIDF_CHECKPOINT_FOUND", flush=True)
        vectorizer = joblib.load(VECTORIZER_PATH)

        print("TFIDF_CHECKPOINT_LOADED", flush=True)

    else:
        print("TFIDF_FITTING_START", flush=True)

        vectorizer = TfidfVectorizer(
            ngram_range=NGRAM_RANGE,
            min_df=MIN_DF,
            max_df=MAX_DF,
            max_features=MAX_FEATURES,
            sublinear_tf=SUBLINEAR_TF,
            dtype=np.float32,
        )

        X_train = vectorizer.fit_transform(train_text)

        joblib.dump(vectorizer, VECTORIZER_PATH, compress=3)

        print(
            f"TFIDF_FITTING_COMPLETE "
            f"VOCABULARY_SIZE={len(vectorizer.vocabulary_)}",
            flush=True,
        )

        print(
            f"TFIDF_CHECKPOINT_SAVED={VECTORIZER_PATH}",
            flush=True,
        )

    if X_train is None:
        print("TFIDF_TRANSFORM_TRAIN_START", flush=True)
        X_train = vectorizer.transform(train_text)
        print(
            f"TFIDF_TRANSFORM_TRAIN_COMPLETE "
            f"ROWS={X_train.shape[0]} "
            f"COLS={X_train.shape[1]}",
            flush=True,
        )

    print("TFIDF_TRANSFORM_EVAL_START", flush=True)
    X_eval = vectorizer.transform(eval_text)
    print(
        f"TFIDF_TRANSFORM_EVAL_COMPLETE "
        f"ROWS={X_eval.shape[0]} "
        f"COLS={X_eval.shape[1]}",
        flush=True,
    )

    # ---------------------------------------------------------------
    # Training labels
    # ---------------------------------------------------------------

    y_train = train["target_assignee"].astype(str).map(label_to_index).to_numpy(
        dtype=np.int32
    )

    print(
        f"TRAIN_LABELS_READY CLASSES={len(candidate_labels)}",
        flush=True,
    )

    # ---------------------------------------------------------------
    # LinearSVC
    # ---------------------------------------------------------------

    if MODEL_PATH.exists():
        print("MODEL_CHECKPOINT_FOUND", flush=True)
        model = joblib.load(MODEL_PATH)
        print("MODEL_CHECKPOINT_LOADED", flush=True)

    else:
        print("LINEARSVC_FITTING_START", flush=True)
        print(
            f"C={C} MAX_ITER={MAX_ITER} "
            f"CLASS_WEIGHT=None",
            flush=True,
        )

        model = LinearSVC(
            C=C,
            class_weight=None,
            max_iter=MAX_ITER,
            random_state=42,
        )

        fit_start = time.time()

        model.fit(X_train, y_train)

        fit_seconds = time.time() - fit_start

        joblib.dump(model, MODEL_PATH, compress=3)

        print(
            f"LINEARSVC_FITTING_COMPLETE "
            f"SECONDS={fit_seconds:.2f}",
            flush=True,
        )

        print(
            f"MODEL_CHECKPOINT_SAVED={MODEL_PATH}",
            flush=True,
        )

    # Free large training matrix before evaluation scoring.
    del X_train
    del train_text
    del eval_text

    # ---------------------------------------------------------------
    # Chunked evaluation scoring
    #
    # We do NOT construct and retain the complete
    # 35,626 x 4,139 decision matrix.
    # ---------------------------------------------------------------

    print("EVALUATION_SCORING_START", flush=True)

    n_eval = len(evaluation)
    max_k = max(TOP_KS)

    top_indices = np.empty(
        (n_eval, max_k),
        dtype=np.int32,
    )

    top_scores = np.empty(
        (n_eval, max_k),
        dtype=np.float32,
    )

    for start in range(0, n_eval, EVAL_CHUNK_SIZE):
        end = min(start + EVAL_CHUNK_SIZE, n_eval)

        chunk_scores = model.decision_function(
            X_eval[start:end]
        )

        # Handle binary output defensively, although T4 is multiclass.
        if chunk_scores.ndim == 1:
            chunk_scores = np.column_stack(
                [-chunk_scores, chunk_scores]
            )

        k = min(max_k, chunk_scores.shape[1])

        candidate_idx = np.argpartition(
            chunk_scores,
            -k,
            axis=1,
        )[:, -k:]

        candidate_scores = np.take_along_axis(
            chunk_scores,
            candidate_idx,
            axis=1,
        )

        order = np.argsort(
            -candidate_scores,
            axis=1,
        )

        candidate_idx = np.take_along_axis(
            candidate_idx,
            order,
            axis=1,
        )

        candidate_scores = np.take_along_axis(
            candidate_scores,
            order,
            axis=1,
        )

        top_indices[start:end, :k] = candidate_idx.astype(np.int32)
        top_scores[start:end, :k] = candidate_scores.astype(np.float32)

        print(
            f"SCORING_PROGRESS={end}/{n_eval}",
            flush=True,
        )

    np.savez_compressed(
        SCORES_PATH,
        top_indices=top_indices,
        top_scores=top_scores,
        candidate_labels=candidate_labels,
    )

    print(
        f"EVALUATION_SCORING_COMPLETE "
        f"ROWS={n_eval}",
        flush=True,
    )

    print(
        f"SCORES_CHECKPOINT_SAVED={SCORES_PATH}",
        flush=True,
    )

    # ---------------------------------------------------------------
    # Metrics
    # ---------------------------------------------------------------

    y_true = evaluation["target_assignee"].astype(str).to_numpy()

    top1_indices = top_indices[:, 0]
    top1_predictions = candidate_labels[top1_indices]

    metrics = {
        "experiment": "T4-MOD-006-R1",
        "description": (
            "Resource-controlled LinearSVC routing baseline "
            "using word-level TF-IDF."
        ),
        "status": "COMPLETE",
        "train_rows": int(len(train)),
        "evaluation_rows": int(len(evaluation)),
        "candidate_classes": int(len(candidate_labels)),
        "tfidf": {
            "max_features": MAX_FEATURES,
            "ngram_range": list(NGRAM_RANGE),
            "min_df": MIN_DF,
            "max_df": MAX_DF,
            "sublinear_tf": SUBLINEAR_TF,
        },
        "model": {
            "type": "LinearSVC",
            "C": C,
            "class_weight": None,
            "max_iter": MAX_ITER,
        },
        "metrics": {},
    }

    metrics["metrics"]["top1_accuracy"] = float(
        accuracy_score(y_true, top1_predictions)
    )

    metrics["metrics"]["top1_macro_f1"] = float(
        f1_score(
            y_true,
            top1_predictions,
            labels=candidate_labels,
            average="macro",
            zero_division=0,
        )
    )

    metrics["metrics"]["top1_weighted_f1"] = float(
        f1_score(
            y_true,
            top1_predictions,
            labels=candidate_labels,
            average="weighted",
            zero_division=0,
        )
    )

    # ---------------------------------------------------------------
    # Top-K
    # ---------------------------------------------------------------

    for k in TOP_KS:
        idx = top_indices[:, :k]
        predicted_labels = candidate_labels[idx]

        hits = np.any(
            predicted_labels == y_true[:, None],
            axis=1,
        )

        metrics["metrics"][f"top{k}_accuracy"] = float(
            np.mean(hits)
        )

    # ---------------------------------------------------------------
    # Open-world diagnostics
    # ---------------------------------------------------------------

    candidate_set = set(candidate_labels.tolist())

    covered_mask = np.array(
        [target in candidate_set for target in y_true],
        dtype=bool,
    )

    unseen_mask = ~covered_mask

    metrics["open_world"] = {
        "covered_evaluation_rows": int(np.sum(covered_mask)),
        "unseen_evaluation_rows": int(np.sum(unseen_mask)),
        "unseen_evaluation_rate": float(np.mean(unseen_mask)),
    }

    # Top-1 accuracy only makes sense as a closed-candidate routing
    # measurement for covered rows.
    if np.any(covered_mask):
        covered_true = y_true[covered_mask]
        covered_pred = top1_predictions[covered_mask]

        metrics["covered_evaluation"] = {
            "rows": int(np.sum(covered_mask)),
            "top1_accuracy": float(
                accuracy_score(covered_true, covered_pred)
            ),
            "top1_macro_f1": float(
                f1_score(
                    covered_true,
                    covered_pred,
                    labels=candidate_labels,
                    average="macro",
                    zero_division=0,
                )
            ),
            "top1_weighted_f1": float(
                f1_score(
                    covered_true,
                    covered_pred,
                    labels=candidate_labels,
                    average="weighted",
                    zero_division=0,
                )
            ),
        }

    if np.any(unseen_mask):
        metrics["unseen_target_behavior"] = {
            "rows": int(np.sum(unseen_mask)),
            "top1_correct_count": int(
                np.sum(
                    top1_predictions[unseen_mask]
                    == y_true[unseen_mask]
                )
            ),
        }

    metrics["runtime"] = {
        "total_seconds": float(time.time() - overall_start),
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(
        f"METRICS_SAVED={METRICS_PATH}",
        flush=True,
    )

    print(
        "T4-MOD-006-R1_COMPLETE",
        flush=True,
    )

    print(
        f"TOP1_ACCURACY={metrics['metrics']['top1_accuracy']:.6f}",
        flush=True,
    )

    print(
        f"TOP1_MACRO_F1={metrics['metrics']['top1_macro_f1']:.6f}",
        flush=True,
    )

    print(
        f"TOP1_WEIGHTED_F1={metrics['metrics']['top1_weighted_f1']:.6f}",
        flush=True,
    )

    for k in TOP_KS:
        print(
            f"TOP{k}_ACCURACY="
            f"{metrics['metrics'][f'top{k}_accuracy']:.6f}",
            flush=True,
        )

    print(
        f"UNSEEN_EVAL_ROWS={metrics['open_world']['unseen_evaluation_rows']}",
        flush=True,
    )

    print(
        f"UNSEEN_EVAL_RATE="
        f"{metrics['open_world']['unseen_evaluation_rate']:.6f}",
        flush=True,
    )


if __name__ == "__main__":
    main()
