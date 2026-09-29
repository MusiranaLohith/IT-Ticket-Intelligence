from pathlib import Path
import json
import time

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import CountVectorizer


PROJECT_DIR = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
DERIVED_DIR = PROJECT_DIR / "modeling/T4/derived"
RESULTS_DIR = PROJECT_DIR / "modeling/T4/results"

TRAIN_PATH = DERIVED_DIR / "t4_train.csv"
EVAL_PATH = DERIVED_DIR / "t4_eval.csv"

OUTPUT_PATH = RESULTS_DIR / "t4_mod009_screen.json"

RANDOM_SEED = 42
SCREEN_SAMPLE = 2000
TOP_K = 20

MAX_FEATURES = 50000
MIN_DF = 2

K1 = 1.5
B = 0.75

BATCH_SIZE = 100


def combine_text(df):
    columns = [
        "Creator",
        "Creator Detail",
        "Summary",
        "Description",
    ]

    return (
        df[columns]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
        .str.strip()
        .to_numpy()
    )


def bm25_documents(count_matrix, document_lengths):
    avgdl = float(document_lengths.mean())

    matrix = count_matrix.tocsr().astype(
        np.float32
    )

    rows, cols = matrix.nonzero()

    denominator = (
        matrix.data
        + K1
        * (
            1.0
            - B
            + B
            * (
                document_lengths[rows]
                / avgdl
            )
        )
    )

    matrix.data = (
        matrix.data
        * (K1 + 1.0)
        / denominator
    )

    return matrix


def bm25_queries(count_matrix):
    matrix = count_matrix.tocsr().astype(
        np.float32
    )

    rows, cols = matrix.nonzero()

    row_counts = np.bincount(
        rows,
        minlength=matrix.shape[0],
    ).astype(np.float32)

    matrix.data = matrix.data / np.maximum(
        row_counts[rows],
        1.0,
    )

    return matrix


def compute_idf(count_matrix):
    document_frequency = np.asarray(
        (count_matrix > 0).sum(axis=0)
    ).ravel().astype(np.float32)

    n_documents = count_matrix.shape[0]

    return np.log(
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
    ).astype(np.float32)


def apply_idf(matrix, idf):
    matrix = matrix.tocsr().astype(
        np.float32
    )

    matrix.data *= idf[
        matrix.indices
    ]

    return matrix


def extract_top_indices(scores, k):
    if scores.nnz == 0:
        return np.full(
            k,
            -1,
            dtype=np.int32,
        )

    data = scores.data
    indices = scores.indices

    if len(data) <= k:
        order = np.argsort(-data)
    else:
        partial = np.argpartition(
            -data,
            k - 1,
        )[:k]

        order = partial[
            np.argsort(
                -data[partial]
            )
        ]

    selected = indices[order]

    output = np.full(
        k,
        -1,
        dtype=np.int32,
    )

    output[:len(selected)] = selected

    return output


def main():
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "T4-MOD-009 BM25 retrieval screening"
    )

    train = pd.read_csv(
        TRAIN_PATH
    )

    evaluation = pd.read_csv(
        EVAL_PATH
    )

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

    rng = np.random.default_rng(
        RANDOM_SEED
    )

    if len(covered_indices) > SCREEN_SAMPLE:
        sample_indices = np.sort(
            rng.choice(
                covered_indices,
                size=SCREEN_SAMPLE,
                replace=False,
            )
        )
    else:
        sample_indices = covered_indices

    sample_targets = eval_targets[
        sample_indices
    ]

    print(
        f"TRAIN_ROWS={len(train)}"
    )

    print(
        f"EVALUATION_ROWS={len(evaluation)}"
    )

    print(
        f"COVERED_EVALUATION_ROWS="
        f"{len(covered_indices)}"
    )

    print(
        f"SCREEN_SAMPLE="
        f"{len(sample_indices)}"
    )

    print(
        f"TOP_K={TOP_K}"
    )

    train_text = combine_text(
        train
    )

    sample_text = combine_text(
        evaluation.iloc[
            sample_indices
        ]
    )

    print()
    print(
        "FITTING BM25 VOCABULARY"
    )

    vectorizer = CountVectorizer(
        lowercase=True,
        max_features=MAX_FEATURES,
        min_df=MIN_DF,
        token_pattern=r"(?u)\b\w+\b",
    )

    start = time.time()

    train_counts = vectorizer.fit_transform(
        train_text
    )

    sample_counts = vectorizer.transform(
        sample_text
    )

    print(
        f"Train count matrix: "
        f"{train_counts.shape}"
    )

    print(
        f"Sample count matrix: "
        f"{sample_counts.shape}"
    )

    print(
        f"Vectorization: "
        f"{time.time() - start:.2f}s"
    )

    print()
    print(
        "COMPUTING DOCUMENT LENGTHS"
    )

    train_lengths = np.asarray(
        train_counts.sum(axis=1)
    ).ravel().astype(np.float32)

    print(
        f"Mean document length: "
        f"{train_lengths.mean():.4f}"
    )

    print()
    print(
        "COMPUTING BM25 IDF"
    )

    idf = compute_idf(
        train_counts
    )

    print(
        f"Vocabulary size: "
        f"{len(idf)}"
    )

    print()
    print(
        "BUILDING SPARSE BM25 DOCUMENT MATRIX"
    )

    start = time.time()

    train_bm25 = bm25_documents(
        train_counts,
        train_lengths,
    )

    train_bm25 = apply_idf(
        train_bm25,
        idf,
    )

    print(
        f"BM25 train matrix: "
        f"{train_bm25.shape}"
    )

    print(
        f"Document weighting: "
        f"{time.time() - start:.2f}s"
    )

    print()
    print(
        "BUILDING SPARSE BM25 QUERY MATRIX"
    )

    sample_bm25 = bm25_queries(
        sample_counts
    )

    sample_bm25 = apply_idf(
        sample_bm25,
        idf,
    )

    print(
        f"BM25 query matrix: "
        f"{sample_bm25.shape}"
    )

    print()
    print(
        "BM25 RETRIEVAL"
    )

    top_indices = np.full(
        (
            len(sample_indices),
            TOP_K,
        ),
        -1,
        dtype=np.int32,
    )

    start = time.time()

    for start_idx in range(
        0,
        len(sample_indices),
        BATCH_SIZE,
    ):
        end_idx = min(
            start_idx + BATCH_SIZE,
            len(sample_indices),
        )

        query_batch = sample_bm25[
            start_idx:end_idx
        ]

        scores = (
            query_batch
            @ train_bm25.T
        ).tocsr()

        for row_idx in range(
            scores.shape[0]
        ):
            top_indices[
                start_idx + row_idx
            ] = extract_top_indices(
                scores.getrow(row_idx),
                TOP_K,
            )

        processed = end_idx

        elapsed = time.time() - start

        print(
            f"Processed "
            f"{processed}/"
            f"{len(sample_indices)} "
            f"("
            f"{processed / len(sample_indices) * 100:.1f}"
            f"%) "
            f"elapsed={elapsed:.1f}s"
        )

    retrieval_seconds = (
        time.time() - start
    )

    print()
    print(
        "CALCULATING RETRIEVAL COVERAGE"
    )

    hits = {
        k: 0
        for k in [
            1,
            3,
            5,
            10,
            20,
        ]
    }

    for row_idx in range(
        len(sample_indices)
    ):
        target = sample_targets[
            row_idx
        ]

        retrieved = top_indices[
            row_idx
        ]

        retrieved = retrieved[
            retrieved >= 0
        ]

        retrieved_targets = (
            train_targets[
                retrieved
            ]
        )

        for k in [
            1,
            3,
            5,
            10,
            20,
        ]:
            if target in (
                retrieved_targets[:k]
            ):
                hits[k] += 1

    metrics = {}

    for k in [
        1,
        3,
        5,
        10,
        20,
    ]:
        metrics[
            f"hit_at_{k}"
        ] = (
            hits[k]
            / len(sample_indices)
        )

    print()
    print(
        "SCREENING RESULTS"
    )

    for k in [
        1,
        3,
        5,
        10,
        20,
    ]:
        print(
            f"Hit@{k}: "
            f"{metrics[f'hit_at_{k}']:.6f}"
        )

    print()
    print(
        "CONTROLS"
    )

    print(
        "RAW_MOZILLA_ACCESSED=False"
    )

    print(
        "TARGET_RECONSTRUCTED=False"
    )

    print(
        "TEST_USED=False"
    )

    print(
        "FUTURE_FEATURES_USED=False"
    )

    print(
        "SPLIT_CHANGED=False"
    )

    output = {
        "experiment": "T4-MOD-009",
        "status": "COMPLETE",
        "method": "BM25",
        "population": {
            "train_rows": len(train),
            "evaluation_rows": len(evaluation),
            "covered_evaluation_rows": len(
                covered_indices
            ),
            "screen_sample": len(
                sample_indices
            ),
            "training_candidates": len(
                training_candidates
            ),
        },
        "bm25": {
            "max_features": MAX_FEATURES,
            "min_df": MIN_DF,
            "k1": K1,
            "b": B,
            "vocabulary_size": int(
                len(idf)
            ),
        },
        "retrieval": {
            "top_k": TOP_K,
            "metrics": metrics,
            "runtime_seconds": retrieval_seconds,
        },
        "sampling": {
            "seed": RANDOM_SEED,
            "deterministic": True,
            "covered_only": True,
        },
        "controls": {
            "raw_mozilla_accessed": False,
            "target_reconstructed": False,
            "test_used": False,
            "future_features_used": False,
            "split_changed": False,
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
        "T4-MOD-009_SCREEN_COMPLETE"
    )


if __name__ == "__main__":
    main()