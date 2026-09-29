from pathlib import Path
import json
import time

import numpy as np
import pandas as pd
from joblib import dump, load

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import accuracy_score, f1_score


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DERIVED_DIR = PROJECT_ROOT / "modeling" / "T4" / "derived"
RESULTS_DIR = PROJECT_ROOT / "modeling" / "T4" / "results"
CHECKPOINT_DIR = RESULTS_DIR / "mod007_checkpoints"

TRAIN_PATH = DERIVED_DIR / "t4_train.csv"
EVAL_PATH = DERIVED_DIR / "t4_eval.csv"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------
# FROZEN MOD-007 CONFIGURATION
# ---------------------------------------------------------------------

RETRIEVAL_K = 20

MAX_FEATURES = 20_000
NGRAM_RANGE = (1, 1)
MIN_DF = 2
MAX_DF = 0.995
SUBLINEAR_TF = True

VECTORIZER_PATH = CHECKPOINT_DIR / "t4_mod007_tfidf.joblib"
NEIGHBORS_PATH = CHECKPOINT_DIR / "t4_mod007_neighbors.joblib"

RETRIEVAL_PATH = CHECKPOINT_DIR / "t4_mod007_full_retrieval.npz"
RESULTS_PATH = RESULTS_DIR / "t4_mod007_full_results.json"


def build_text(df: pd.DataFrame) -> pd.Series:
    columns = [
        "Creator",
        "Creator Detail",
        "Summary",
        "Description",
    ]

    text = df[columns[0]].fillna("").astype(str)

    for column in columns[1:]:
        text = text + " " + df[column].fillna("").astype(str)

    return text.str.strip()


def validate_data(train: pd.DataFrame, evaluation: pd.DataFrame):
    expected_columns = {
        "ID",
        "Creation time",
        "Creator",
        "Creator Detail",
        "Summary",
        "Description",
        "target_assignee",
    }

    if len(train) != 142501:
        raise RuntimeError(
            f"Unexpected training rows: {len(train)}"
        )

    if len(evaluation) != 35626:
        raise RuntimeError(
            f"Unexpected evaluation rows: {len(evaluation)}"
        )

    if set(train.columns) != expected_columns:
        raise RuntimeError(
            "Training schema does not match frozen T4 schema."
        )

    if set(evaluation.columns) != expected_columns:
        raise RuntimeError(
            "Evaluation schema does not match frozen T4 schema."
        )

    if train["target_assignee"].isna().any():
        raise RuntimeError("Blank training target detected.")

    if evaluation["target_assignee"].isna().any():
        raise RuntimeError("Blank evaluation target detected.")


def rank_assignees(
    neighbor_indices,
    neighbor_similarities,
    train_targets,
):
    """
    Aggregate similarity evidence from retrieved historical tickets.

    Each historical ticket contributes its cosine similarity to the
    assignee who handled that historical ticket.

    Assignees are ranked by descending summed similarity.
    """

    scores = {}

    for idx, similarity in zip(
        neighbor_indices,
        neighbor_similarities,
    ):
        assignee = train_targets[idx]

        scores[assignee] = (
            scores.get(assignee, 0.0)
            + float(similarity)
        )

    ranked = sorted(
        scores.items(),
        key=lambda item: (-item[1], item[0]),
    )

    return [assignee for assignee, _ in ranked]


def reciprocal_rank(ranked, target):
    for rank, assignee in enumerate(ranked, start=1):
        if assignee == target:
            return 1.0 / rank

    return 0.0


def ndcg_binary(ranked, target, k):
    """
    Binary relevance:
        1 if the true historical target appears in the ranked list
        0 otherwise.

    With one relevant target, NDCG@K is:
        1 / log2(rank + 1)
    when the target is within K, otherwise 0.
    """

    for rank, assignee in enumerate(ranked[:k], start=1):
        if assignee == target:
            return 1.0 / np.log2(rank + 1)

    return 0.0


def main():
    overall_start = time.time()

    print("T4-MOD-007_FULL_START", flush=True)

    # -----------------------------------------------------------------
    # Load frozen modeling artifacts.
    # -----------------------------------------------------------------

    train = pd.read_csv(TRAIN_PATH)
    evaluation = pd.read_csv(EVAL_PATH)

    validate_data(train, evaluation)

    print(
        f"TRAIN_ROWS={len(train)} "
        f"EVALUATION_ROWS={len(evaluation)}",
        flush=True,
    )

    train_targets = train["target_assignee"].astype(str).to_numpy()
    eval_targets = evaluation["target_assignee"].astype(str).to_numpy()

    training_candidates = np.unique(train_targets)
    candidate_set = set(training_candidates.tolist())

    print(
        f"TRAINING_CANDIDATES={len(training_candidates)}",
        flush=True,
    )

    # -----------------------------------------------------------------
    # Text construction.
    # -----------------------------------------------------------------

    print("BUILDING_TRAIN_TEXT_START", flush=True)
    train_text = build_text(train)
    print("BUILDING_TRAIN_TEXT_COMPLETE", flush=True)

    print("BUILDING_EVALUATION_TEXT_START", flush=True)
    eval_text = build_text(evaluation)
    print("BUILDING_EVALUATION_TEXT_COMPLETE", flush=True)

    # -----------------------------------------------------------------
    # TF-IDF.
    # -----------------------------------------------------------------

    if VECTORIZER_PATH.exists():
        print("TFIDF_CHECKPOINT_FOUND", flush=True)
        vectorizer = load(VECTORIZER_PATH)
        print("TFIDF_CHECKPOINT_LOADED", flush=True)

        X_train = vectorizer.transform(train_text)

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

        dump(
            vectorizer,
            VECTORIZER_PATH,
            compress=3,
        )

        print(
            f"TFIDF_FITTING_COMPLETE "
            f"VOCABULARY_SIZE={len(vectorizer.vocabulary_)}",
            flush=True,
        )

        print(
            f"TFIDF_CHECKPOINT_SAVED={VECTORIZER_PATH}",
            flush=True,
        )

    print(
        f"TRAIN_MATRIX_ROWS={X_train.shape[0]} "
        f"TRAIN_MATRIX_COLS={X_train.shape[1]}",
        flush=True,
    )

    print("EVAL_TRANSFORM_START", flush=True)

    X_eval = vectorizer.transform(eval_text)

    print(
        f"EVAL_TRANSFORM_COMPLETE "
        f"ROWS={X_eval.shape[0]} "
        f"COLS={X_eval.shape[1]}",
        flush=True,
    )

    # -----------------------------------------------------------------
    # Nearest-neighbor index.
    # -----------------------------------------------------------------

    if NEIGHBORS_PATH.exists():
        print("NEIGHBORS_CHECKPOINT_FOUND", flush=True)
        nn = load(NEIGHBORS_PATH)
        print("NEIGHBORS_CHECKPOINT_LOADED", flush=True)

    else:
        print("NEAREST_NEIGHBORS_FITTING_START", flush=True)

        nn = NearestNeighbors(
            n_neighbors=RETRIEVAL_K,
            metric="cosine",
            algorithm="brute",
            n_jobs=-1,
        )

        fit_start = time.time()

        nn.fit(X_train)

        fit_seconds = time.time() - fit_start

        dump(
            nn,
            NEIGHBORS_PATH,
            compress=3,
        )

        print(
            f"NEAREST_NEIGHBORS_FITTING_COMPLETE "
            f"SECONDS={fit_seconds:.2f}",
            flush=True,
        )

        print(
            f"NEIGHBORS_CHECKPOINT_SAVED={NEIGHBORS_PATH}",
            flush=True,
        )

    # -----------------------------------------------------------------
    # Full retrieval.
    # -----------------------------------------------------------------

    if RETRIEVAL_PATH.exists():
        print("FULL_RETRIEVAL_CHECKPOINT_FOUND", flush=True)

        saved = np.load(
            RETRIEVAL_PATH,
            allow_pickle=False,
        )

        indices = saved["neighbor_indices"]
        similarities = saved["neighbor_similarities"]

        print(
            "FULL_RETRIEVAL_CHECKPOINT_LOADED",
            flush=True,
        )

    else:
        print("FULL_RETRIEVAL_START", flush=True)

        retrieval_start = time.time()

        distances, indices = nn.kneighbors(X_eval)

        similarities = 1.0 - distances

        retrieval_seconds = time.time() - retrieval_start

        print(
            f"FULL_RETRIEVAL_COMPLETE "
            f"ROWS={len(evaluation)} "
            f"K={RETRIEVAL_K} "
            f"SECONDS={retrieval_seconds:.2f}",
            flush=True,
        )

        np.savez_compressed(
            RETRIEVAL_PATH,
            neighbor_indices=indices.astype(np.int32),
            neighbor_similarities=similarities.astype(np.float32),
        )

        print(
            f"FULL_RETRIEVAL_CHECKPOINT_SAVED={RETRIEVAL_PATH}",
            flush=True,
        )

    # -----------------------------------------------------------------
    # Ranking + metrics.
    # -----------------------------------------------------------------

    print("ASSIGNEE_RANKING_START", flush=True)

    hit_counts = {
        1: 0,
        3: 0,
        5: 0,
        10: 0,
    }

    reciprocal_ranks = []

    ndcg5_values = []
    ndcg10_values = []

    top1_predictions = []

    covered_mask = np.array(
        [target in candidate_set for target in eval_targets],
        dtype=bool,
    )

    unseen_mask = ~covered_mask

    covered_rr = []
    covered_ndcg5 = []
    covered_ndcg10 = []

    covered_hit_counts = {
        1: 0,
        3: 0,
        5: 0,
        10: 0,
    }

    for row_idx in range(len(evaluation)):
        ranked = rank_assignees(
            indices[row_idx],
            similarities[row_idx],
            train_targets,
        )

        target = eval_targets[row_idx]

        top1_predictions.append(
            ranked[0] if ranked else None
        )

        rr = reciprocal_rank(ranked, target)

        reciprocal_ranks.append(rr)
        ndcg5_values.append(
            ndcg_binary(ranked, target, 5)
        )
        ndcg10_values.append(
            ndcg_binary(ranked, target, 10)
        )

        for k in hit_counts:
            if target in ranked[:k]:
                hit_counts[k] += 1

        if covered_mask[row_idx]:
            covered_rr.append(rr)
            covered_ndcg5.append(
                ndcg_binary(ranked, target, 5)
            )
            covered_ndcg10.append(
                ndcg_binary(ranked, target, 10)
            )

            for k in covered_hit_counts:
                if target in ranked[:k]:
                    covered_hit_counts[k] += 1

        if (row_idx + 1) % 5000 == 0:
            print(
                f"RANKING_PROGRESS="
                f"{row_idx + 1}/{len(evaluation)}",
                flush=True,
            )

    top1_predictions = np.array(
        top1_predictions,
        dtype=object,
    )

    print(
        "ASSIGNEE_RANKING_COMPLETE",
        flush=True,
    )

    # -----------------------------------------------------------------
    # Global metrics.
    # -----------------------------------------------------------------

    n = len(evaluation)

    metrics = {
        "hit_at_1": float(hit_counts[1] / n),
        "hit_at_3": float(hit_counts[3] / n),
        "hit_at_5": float(hit_counts[5] / n),
        "hit_at_10": float(hit_counts[10] / n),
        "mrr": float(np.mean(reciprocal_ranks)),
        "ndcg_at_5": float(np.mean(ndcg5_values)),
        "ndcg_at_10": float(np.mean(ndcg10_values)),
    }

    # -----------------------------------------------------------------
    # Covered-target metrics.
    # -----------------------------------------------------------------

    covered_n = int(np.sum(covered_mask))

    if covered_n > 0:
        covered_metrics = {
            "rows": covered_n,
            "hit_at_1": float(
                covered_hit_counts[1] / covered_n
            ),
            "hit_at_3": float(
                covered_hit_counts[3] / covered_n
            ),
            "hit_at_5": float(
                covered_hit_counts[5] / covered_n
            ),
            "hit_at_10": float(
                covered_hit_counts[10] / covered_n
            ),
            "mrr": float(np.mean(covered_rr)),
            "ndcg_at_5": float(np.mean(covered_ndcg5)),
            "ndcg_at_10": float(np.mean(covered_ndcg10)),
        }
    else:
        covered_metrics = {
            "rows": 0
        }

    # -----------------------------------------------------------------
    # Unseen-target diagnostics.
    # -----------------------------------------------------------------

    unseen_n = int(np.sum(unseen_mask))

    unseen_metrics = {
        "rows": unseen_n,
        "rate": float(unseen_n / n),
        "hit_at_1": 0.0,
        "hit_at_3": 0.0,
        "hit_at_5": 0.0,
        "hit_at_10": 0.0,
        "mrr": 0.0,
        "ndcg_at_5": 0.0,
        "ndcg_at_10": 0.0,
    }

    # -----------------------------------------------------------------
    # Top-1 classification-style supporting metrics.
    # These are secondary because MOD-007 is a ranking experiment.
    # -----------------------------------------------------------------

    valid_top1 = np.array(
        [
            pred if pred is not None else ""
            for pred in top1_predictions
        ],
        dtype=str,
    )

    top1_accuracy = accuracy_score(
        eval_targets,
        valid_top1,
    )

    top1_macro_f1 = f1_score(
        eval_targets,
        valid_top1,
        labels=training_candidates,
        average="macro",
        zero_division=0,
    )

    top1_weighted_f1 = f1_score(
        eval_targets,
        valid_top1,
        labels=training_candidates,
        average="weighted",
        zero_division=0,
    )

    # -----------------------------------------------------------------
    # Long-tail support stratification.
    # -----------------------------------------------------------------

    train_counts = (
        train["target_assignee"]
        .astype(str)
        .value_counts()
    )

    def bucket_for_support(support):
        if support == 1:
            return "1"
        if support <= 5:
            return "2-5"
        if support <= 10:
            return "6-10"
        if support <= 20:
            return "11-20"
        if support <= 50:
            return "21-50"
        if support <= 100:
            return "51-100"
        return "101+"

    buckets = {
        "1": [],
        "2-5": [],
        "6-10": [],
        "11-20": [],
        "21-50": [],
        "51-100": [],
        "101+": [],
    }

    for target in eval_targets:
        if target in train_counts:
            bucket = bucket_for_support(
                int(train_counts[target])
            )
            buckets[bucket].append(target)

    bucket_results = {}

    for bucket, targets in buckets.items():
        if not targets:
            bucket_results[bucket] = {
                "rows": 0,
                "hit_at_1": None,
                "hit_at_5": None,
                "hit_at_10": None,
            }
            continue

        target_set = set(targets)

        mask = np.array(
            [
                target in target_set
                for target in eval_targets
            ],
            dtype=bool,
        )

        bucket_results[bucket] = {
            "rows": int(np.sum(mask)),
            "hit_at_1": float(
                np.mean(
                    valid_top1[mask]
                    == eval_targets[mask]
                )
            ),
            "hit_at_5": float(
                np.mean(
                    [
                        eval_targets[i]
                        in rank_assignees_for_row(
                            i,
                            indices,
                            similarities,
                            train_targets,
                        )[:5]
                        for i in np.where(mask)[0]
                    ]
                )
            ),
            "hit_at_10": float(
                np.mean(
                    [
                        eval_targets[i]
                        in rank_assignees_for_row(
                            i,
                            indices,
                            similarities,
                            train_targets,
                        )[:10]
                        for i in np.where(mask)[0]
                    ]
                )
            ),
        }

    # -----------------------------------------------------------------
    # Final report.
    # -----------------------------------------------------------------

    report = {
        "experiment_id": "T4-MOD-007",
        "title": "Historical Similarity Assignee Ranking Baseline",
        "status": "COMPLETE",

        "train_rows": int(len(train)),
        "evaluation_rows": int(len(evaluation)),
        "training_candidate_assignees": int(
            len(training_candidates)
        ),

        "retrieval": {
            "k": RETRIEVAL_K,
            "method": "TF-IDF cosine nearest-neighbor retrieval",
            "aggregation": (
                "sum of similarity evidence by historical assignee"
            ),
        },

        "tfidf": {
            "max_features": MAX_FEATURES,
            "ngram_range": list(NGRAM_RANGE),
            "min_df": MIN_DF,
            "max_df": MAX_DF,
            "sublinear_tf": SUBLINEAR_TF,
        },

        "metrics_overall": metrics,

        "metrics_covered_targets": covered_metrics,

        "metrics_unseen_targets": unseen_metrics,

        "supporting_top1_metrics": {
            "accuracy": float(top1_accuracy),
            "macro_f1": float(top1_macro_f1),
            "weighted_f1": float(top1_weighted_f1),
        },

        "historical_support_stratification": bucket_results,

        "open_world": {
            "covered_rows": covered_n,
            "unseen_rows": unseen_n,
            "unseen_rate": float(unseen_n / n),
        },

        "controls": {
            "raw_mozilla_accessed": False,
            "target_reconstructed": False,
            "evaluation_used_only_for_scoring": True,
            "training_tickets_used_for_retrieval": True,
            "evaluation_tickets_used_for_retrieval": False,
            "future_features_used": False,
            "target_side_fields_used": False,
            "unseen_targets_removed": False,
        },

        "interpretation": {
            "system_role": "secondary decision-support signal",
            "problem_formulation": "candidate ranking",
            "historical_assignment_not_universal_truth": True,
            "operational_eligibility_established": False,
        },

        "runtime": {
            "total_seconds": float(
                time.time() - overall_start
            ),
        },
    }

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            report,
            f,
            indent=2,
        )

    # -----------------------------------------------------------------
    # Console summary.
    # -----------------------------------------------------------------

    print(
        f"RESULTS_SAVED={RESULTS_PATH}",
        flush=True,
    )

    print("OVERALL_RANKING_METRICS", flush=True)

    for key, value in metrics.items():
        print(
            f"{key.upper()}={value:.6f}",
            flush=True,
        )

    print("COVERED_RANKING_METRICS", flush=True)

    for key, value in covered_metrics.items():
        if key != "rows":
            print(
                f"{key.upper()}={value:.6f}",
                flush=True,
            )

    print(
        f"UNSEEN_ROWS={unseen_n}",
        flush=True,
    )

    print(
        f"UNSEEN_RATE={unseen_n / n:.6f}",
        flush=True,
    )

    print("LONG_TAIL_RESULTS", flush=True)

    for bucket, result in bucket_results.items():
        print(
            f"{bucket}: "
            f"ROWS={result['rows']} "
            f"TOP1={result['hit_at_1']} "
            f"TOP5={result['hit_at_5']} "
            f"TOP10={result['hit_at_10']}",
            flush=True,
        )

    print(
        f"TOTAL_RUNTIME_SECONDS="
        f"{time.time() - overall_start:.2f}",
        flush=True,
    )

    print(
        "T4-MOD-007_FULL_COMPLETE",
        flush=True,
    )


def rank_assignees_for_row(
    row_idx,
    indices,
    similarities,
    train_targets,
):
    return rank_assignees(
        indices[row_idx],
        similarities[row_idx],
        train_targets,
    )


if __name__ == "__main__":
    main()
