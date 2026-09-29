from pathlib import Path
import json
import time

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer


PROJECT_DIR = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
DERIVED_DIR = PROJECT_DIR / "modeling" / "T4" / "derived"
RESULTS_DIR = PROJECT_DIR / "modeling" / "T4" / "results"
CHECKPOINT_DIR = RESULTS_DIR / "mod011_checkpoints"

TRAIN_PATH = DERIVED_DIR / "t4_train.csv"
EVAL_PATH = DERIVED_DIR / "t4_eval.csv"

OUTPUT_PATH = RESULTS_DIR / "t4_mod011_full.json"
RETRIEVAL_CHECKPOINT = CHECKPOINT_DIR / "t4_mod011_retrieval.npz"

MAX_FEATURES = 50000
MIN_DF = 2
K1 = 1.5
B = 0.75
TOP_K = 20
BATCH_SIZE = 100


def build_text(df):
    return (
        df["Creator"].fillna("").astype(str)
        + " "
        + df["Creator Detail"].fillna("").astype(str)
        + " "
        + df["Summary"].fillna("").astype(str)
        + " "
        + df["Description"].fillna("").astype(str)
    ).to_numpy()


def bm25_weight_matrix(
    count_matrix,
    document_lengths,
    avgdl,
    idf,
):
    matrix = count_matrix.tocsr(copy=True).astype(
        np.float64
    )

    rows = np.repeat(
        np.arange(matrix.shape[0]),
        np.diff(matrix.indptr),
    )

    denominator = (
        matrix.data
        + K1
        * (
            1.0
            - B
            + B * document_lengths[rows] / avgdl
        )
    )

    matrix.data = (
        matrix.data
        * (K1 + 1.0)
        / denominator
    )

    matrix.data *= idf[matrix.indices]

    return matrix


def bm25_query_matrix(count_matrix, idf):
    matrix = count_matrix.tocsr(copy=True).astype(
        np.float64
    )

    matrix.data *= idf[matrix.indices]

    return matrix


def calculate_ranking_metrics(
    neighbor_indices,
    train_targets,
    eval_targets,
):
    rows = len(eval_targets)

    hits = {
        1: 0,
        3: 0,
        5: 0,
        10: 0,
        20: 0,
    }

    reciprocal_rank_sum = 0.0
    ndcg5_sum = 0.0
    ndcg10_sum = 0.0

    for i in range(rows):
        retrieved_targets = train_targets[
            neighbor_indices[i]
        ]

        true_target = eval_targets[i]

        rank = None

        for position, candidate in enumerate(
            retrieved_targets,
            start=1,
        ):
            if candidate == true_target:
                rank = position
                break

        for k in hits:
            if rank is not None and rank <= k:
                hits[k] += 1

        if rank is not None:
            reciprocal_rank_sum += 1.0 / rank

            if rank <= 5:
                ndcg5_sum += (
                    1.0 / np.log2(rank + 1)
                )

            if rank <= 10:
                ndcg10_sum += (
                    1.0 / np.log2(rank + 1)
                )

    return {
        "hit_at_1": hits[1] / rows,
        "hit_at_3": hits[3] / rows,
        "hit_at_5": hits[5] / rows,
        "hit_at_10": hits[10] / rows,
        "hit_at_20": hits[20] / rows,
        "mrr": reciprocal_rank_sum / rows,
        "ndcg_at_5": ndcg5_sum / rows,
        "ndcg_at_10": ndcg10_sum / rows,
    }


def calculate_support_buckets(
    neighbor_indices,
    train_targets,
    eval_targets,
    train_support,
):
    buckets = {
        "1": [],
        "2-5": [],
        "6-10": [],
        "11-20": [],
        "21-50": [],
        "51-100": [],
        "101+": [],
    }

    for i, true_target in enumerate(eval_targets):
        support = train_support.get(
            true_target,
            0,
        )

        if support == 1:
            bucket = "1"
        elif support <= 5:
            bucket = "2-5"
        elif support <= 10:
            bucket = "6-10"
        elif support <= 20:
            bucket = "11-20"
        elif support <= 50:
            bucket = "21-50"
        elif support <= 100:
            bucket = "51-100"
        else:
            bucket = "101+"

        retrieved_targets = train_targets[
            neighbor_indices[i]
        ]

        hit1 = float(
            retrieved_targets[0] == true_target
        )

        hit5 = float(
            true_target in retrieved_targets[:5]
        )

        hit10 = float(
            true_target in retrieved_targets[:10]
        )

        hit20 = float(
            true_target in retrieved_targets[:20]
        )

        buckets[bucket].append(
            (
                hit1,
                hit5,
                hit10,
                hit20,
            )
        )

    results = {}

    for bucket, values in buckets.items():
        if not values:
            continue

        arr = np.asarray(
            values,
            dtype=np.float64,
        )

        results[bucket] = {
            "rows": int(len(values)),
            "hit_at_1": float(
                arr[:, 0].mean()
            ),
            "hit_at_5": float(
                arr[:, 1].mean()
            ),
            "hit_at_10": float(
                arr[:, 2].mean()
            ),
            "hit_at_20": float(
                arr[:, 3].mean()
            ),
        }

    return results


def main():
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    CHECKPOINT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    started = time.time()

    print("T4-MOD-011 full BM25 retrieval evaluation")
    print()

    train = pd.read_csv(TRAIN_PATH)
    evaluation = pd.read_csv(EVAL_PATH)

    train_targets = (
        train["target_assignee"]
        .astype(str)
        .to_numpy()
    )

    eval_targets = (
        evaluation["target_assignee"]
        .astype(str)
        .to_numpy()
    )

    print(
        f"TRAIN_ROWS={len(train)}"
    )

    print(
        f"EVALUATION_ROWS={len(evaluation)}"
    )

    print()

    training_candidates = set(
        train_targets
    )

    covered_mask = np.array(
        [
            target in training_candidates
            for target in eval_targets
        ],
        dtype=bool,
    )

    covered_indices = np.flatnonzero(
        covered_mask
    )

    unseen_indices = np.flatnonzero(
        ~covered_mask
    )

    print(
        f"TRAINING_CANDIDATES="
        f"{len(training_candidates)}"
    )

    print(
        f"COVERED_ROWS="
        f"{len(covered_indices)}"
    )

    print(
        f"UNSEEN_ROWS="
        f"{len(unseen_indices)}"
    )

    print()

    train_text = build_text(train)
    eval_text = build_text(evaluation)

    print("FITTING BM25 VOCABULARY")

    vectorizer = CountVectorizer(
        max_features=MAX_FEATURES,
        min_df=MIN_DF,
        lowercase=True,
        ngram_range=(1, 1),
    )

    vector_start = time.time()

    train_counts = vectorizer.fit_transform(
        train_text
    )

    eval_counts = vectorizer.transform(
        eval_text
    )

    vector_time = time.time() - vector_start

    print(
        f"Train count matrix: "
        f"{train_counts.shape}"
    )

    print(
        f"Eval count matrix: "
        f"{eval_counts.shape}"
    )

    print(
        f"Vocabulary size: "
        f"{len(vectorizer.vocabulary_)}"
    )

    print(
        f"Vectorization: "
        f"{vector_time:.2f}s"
    )

    print()

    print("COMPUTING DOCUMENT LENGTHS")

    document_lengths = np.asarray(
        train_counts.sum(axis=1)
    ).ravel()

    avgdl = float(
        document_lengths.mean()
    )

    print(
        f"Mean document length: "
        f"{avgdl:.4f}"
    )

    print()

    print("COMPUTING BM25 IDF")

    document_frequency = np.asarray(
        (train_counts > 0).sum(axis=0)
    ).ravel()

    n_documents = train_counts.shape[0]

    idf = np.log(
        1.0
        + (
            n_documents
            - document_frequency
            + 0.5
        )
        / (
            document_frequency
            + 0.5
        )
    )

    print(
        f"Vocabulary size: "
        f"{len(idf)}"
    )

    print()

    print(
        "BUILDING SPARSE BM25 "
        "DOCUMENT MATRIX"
    )

    weighting_start = time.time()

    bm25_train = bm25_weight_matrix(
        train_counts,
        document_lengths,
        avgdl,
        idf,
    )

    weighting_time = (
        time.time()
        - weighting_start
    )

    print(
        f"BM25 train matrix: "
        f"{bm25_train.shape}"
    )

    print(
        f"Document weighting: "
        f"{weighting_time:.2f}s"
    )

    print()

    print(
        "BUILDING SPARSE BM25 "
        "QUERY MATRIX"
    )

    bm25_eval = bm25_query_matrix(
        eval_counts,
        idf,
    )

    print(
        f"BM25 eval matrix: "
        f"{bm25_eval.shape}"
    )

    print()

    del train_counts
    del eval_counts

    print("FULL BM25 RETRIEVAL")
    print()

    n_eval = len(evaluation)

    neighbor_indices = np.empty(
        (n_eval, TOP_K),
        dtype=np.int32,
    )

    neighbor_scores = np.empty(
        (n_eval, TOP_K),
        dtype=np.float32,
    )

    retrieval_start = time.time()

    for start in range(
        0,
        n_eval,
        BATCH_SIZE,
    ):
        end = min(
            start + BATCH_SIZE,
            n_eval,
        )

        query_batch = bm25_eval[
            start:end
        ]

        scores = (
            query_batch
            @ bm25_train.T
        )

        scores = scores.toarray()

        indices = np.argpartition(
            -scores,
            kth=TOP_K - 1,
            axis=1,
        )[:, :TOP_K]

        row_indices = np.arange(
            end - start
        )[:, None]

        selected_scores = scores[
            row_indices,
            indices,
        ]

        order = np.argsort(
            -selected_scores,
            axis=1,
        )

        sorted_indices = (
            np.take_along_axis(
                indices,
                order,
                axis=1,
            )
        )

        sorted_scores = (
            np.take_along_axis(
                selected_scores,
                order,
                axis=1,
            )
        )

        neighbor_indices[
            start:end
        ] = sorted_indices

        neighbor_scores[
            start:end
        ] = sorted_scores

        elapsed = (
            time.time()
            - retrieval_start
        )

        print(
            f"Processed {end}/{n_eval} "
            f"({100.0 * end / n_eval:.1f}%) "
            f"elapsed={elapsed:.1f}s"
        )

    retrieval_time = (
        time.time()
        - retrieval_start
    )

    np.savez_compressed(
        RETRIEVAL_CHECKPOINT,
        neighbor_indices=neighbor_indices,
        neighbor_scores=neighbor_scores,
    )

    print()

    print(
        "RETRIEVAL_CHECKPOINT_SAVED="
        f"{RETRIEVAL_CHECKPOINT}"
    )

    print(
        f"Retrieval runtime: "
        f"{retrieval_time:.2f}s"
    )

    print()

    print(
        "CALCULATING RANKING METRICS"
    )

    overall_metrics = (
        calculate_ranking_metrics(
            neighbor_indices,
            train_targets,
            eval_targets,
        )
    )

    covered_metrics = (
        calculate_ranking_metrics(
            neighbor_indices[
                covered_indices
            ],
            train_targets,
            eval_targets[
                covered_indices
            ],
        )
    )

    print()

    print("OVERALL RANKING METRICS")

    for key, value in (
        overall_metrics.items()
    ):
        print(
            f"{key.upper()}="
            f"{value:.6f}"
        )

    print()

    print(
        "COVERED-TARGET "
        "RANKING METRICS"
    )

    for key, value in (
        covered_metrics.items()
    ):
        print(
            f"{key.upper()}="
            f"{value:.6f}"
        )

    unseen_metrics = {
        "rows": int(
            len(unseen_indices)
        ),
        "hit_at_1": 0.0,
        "hit_at_3": 0.0,
        "hit_at_5": 0.0,
        "hit_at_10": 0.0,
        "hit_at_20": 0.0,
        "mrr": 0.0,
        "ndcg_at_5": 0.0,
        "ndcg_at_10": 0.0,
    }

    print()

    print("UNSEEN-TARGET BEHAVIOR")

    print(
        f"ROWS={len(unseen_indices)}"
    )

    print("HIT_AT_1=0.000000")
    print("HIT_AT_3=0.000000")
    print("HIT_AT_5=0.000000")
    print("HIT_AT_10=0.000000")
    print("HIT_AT_20=0.000000")

    print()

    print(
        "HISTORICAL SUPPORT "
        "STRATIFICATION"
    )

    train_support = (
        train[
            "target_assignee"
        ]
        .astype(str)
        .value_counts()
        .to_dict()
    )

    support_results = (
        calculate_support_buckets(
            neighbor_indices[
                covered_indices
            ],
            train_targets,
            eval_targets[
                covered_indices
            ],
            train_support,
        )
    )

    for bucket, result in (
        support_results.items()
    ):
        print(
            f"{bucket}: "
            f"ROWS={result['rows']} "
            f"H1={result['hit_at_1']:.6f} "
            f"H5={result['hit_at_5']:.6f} "
            f"H10={result['hit_at_10']:.6f} "
            f"H20={result['hit_at_20']:.6f}"
        )

    total_runtime = (
        time.time()
        - started
    )

    output = {
        "experiment": "T4-MOD-011",
        "status": "COMPLETE",
        "method": (
            "BM25 historical "
            "lexical retrieval"
        ),
        "population": {
            "train_rows": int(
                len(train)
            ),
            "evaluation_rows": int(
                len(evaluation)
            ),
            "covered_rows": int(
                len(covered_indices)
            ),
            "unseen_rows": int(
                len(unseen_indices)
            ),
            "training_candidates": int(
                len(training_candidates)
            ),
        },
        "bm25": {
            "max_features": MAX_FEATURES,
            "min_df": MIN_DF,
            "k1": K1,
            "b": B,
            "vocabulary_size": int(
                len(
                    vectorizer.vocabulary_
                )
            ),
            "mean_document_length": avgdl,
        },
        "retrieval": {
            "top_k": TOP_K,
            "batch_size": BATCH_SIZE,
            "overall": overall_metrics,
            "covered": covered_metrics,
            "unseen": unseen_metrics,
            "runtime_seconds": (
                retrieval_time
            ),
        },
        "historical_support_stratification":
            support_results,
        "sampling": {
            "full_evaluation": True,
            "deterministic": True,
        },
        "controls": {
            "raw_mozilla_accessed": False,
            "target_reconstructed": False,
            "test_used": False,
            "future_features_used": False,
            "split_changed": False,
            "evaluation_used_only_for_scoring": True,
            "training_tickets_used_for_retrieval": True,
            "evaluation_tickets_used_for_retrieval": False,
            "target_side_fields_used": False,
            "unseen_targets_removed": False,
        },
        "artifacts": {
            "retrieval_checkpoint": str(
                RETRIEVAL_CHECKPOINT
            ),
            "results": str(
                OUTPUT_PATH
            ),
        },
        "runtime": {
            "vectorization_seconds": (
                vector_time
            ),
            "document_weighting_seconds": (
                weighting_time
            ),
            "retrieval_seconds": (
                retrieval_time
            ),
            "total_seconds": (
                total_runtime
            ),
        },
    }

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            output,
            f,
            indent=2,
        )

    print()

    print(
        f"RESULTS_SAVED="
        f"{OUTPUT_PATH}"
    )

    print(
        f"TOTAL_RUNTIME_SECONDS="
        f"{total_runtime:.2f}"
    )

    print(
        "T4-MOD-011_FULL_COMPLETE"
    )


if __name__ == "__main__":
    main()