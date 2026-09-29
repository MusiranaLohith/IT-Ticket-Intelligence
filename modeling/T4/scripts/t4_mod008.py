from pathlib import Path
import json
import time

import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
DERIVED = ROOT / "modeling/T4/derived"
RESULTS = ROOT / "modeling/T4/results"

TRAIN_FILE = DERIVED / "t4_train.csv"
EVAL_FILE = DERIVED / "t4_eval.csv"
RESULT_FILE = RESULTS / "t4_mod008_screen.json"

SAMPLE_SIZE = 2000
TOP_K = 20
BATCH_SIZE = 100
MAX_FEATURES = 20000


def make_text(df):
    return (
        "Creator=" + df["Creator"].fillna("").astype(str)
        + " CreatorDetail=" + df["Creator Detail"].fillna("").astype(str)
        + " Summary=" + df["Summary"].fillna("").astype(str)
        + " Description=" + df["Description"].fillna("").astype(str)
    ).to_numpy()


def retrieve(train_matrix, eval_matrix, train_targets, eval_targets):
    hits = {1: 0, 3: 0, 5: 0, 10: 0, 20: 0}

    start = time.time()

    for start_idx in range(0, len(eval_targets), BATCH_SIZE):
        end_idx = min(
            start_idx + BATCH_SIZE,
            len(eval_targets),
        )

        similarities = (
            eval_matrix[start_idx:end_idx]
            @ train_matrix.T
        )

        for local_idx in range(end_idx - start_idx):
            row = similarities.getrow(local_idx)

            if row.nnz == 0:
                continue

            data = row.data
            indices = row.indices

            if len(data) > TOP_K:
                positions = np.argpartition(
                    -data,
                    TOP_K - 1,
                )[:TOP_K]

                positions = positions[
                    np.argsort(-data[positions])
                ]
            else:
                positions = np.argsort(-data)

            retrieved = train_targets[
                indices[positions]
            ]

            target = eval_targets[
                start_idx + local_idx
            ]

            found = np.where(
                retrieved == target
            )[0]

            if len(found) == 0:
                continue

            rank = int(found[0]) + 1

            for k in hits:
                if rank <= k:
                    hits[k] += 1

        elapsed = time.time() - start

        print(
            f"Processed {end_idx}/{len(eval_targets)} "
            f"({end_idx / len(eval_targets):.1%}) "
            f"elapsed={elapsed:.1f}s"
        )

        del similarities

    runtime = time.time() - start

    return {
        "hit_at_1": hits[1] / len(eval_targets),
        "hit_at_3": hits[3] / len(eval_targets),
        "hit_at_5": hits[5] / len(eval_targets),
        "hit_at_10": hits[10] / len(eval_targets),
        "hit_at_20": hits[20] / len(eval_targets),
        "runtime_seconds": runtime,
    }


def run_word(
    train_text,
    eval_text,
    train_targets,
    eval_targets,
):
    print()
    print("WORD TF-IDF")

    vectorizer = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 1),
        max_features=MAX_FEATURES,
        min_df=2,
        sublinear_tf=True,
    )

    start = time.time()

    train_matrix = vectorizer.fit_transform(
        train_text
    )

    eval_matrix = vectorizer.transform(
        eval_text
    )

    print(
        f"Train matrix: {train_matrix.shape}"
    )

    print(
        f"Eval matrix: {eval_matrix.shape}"
    )

    metrics = retrieve(
        train_matrix,
        eval_matrix,
        train_targets,
        eval_targets,
    )

    metrics["vectorization_seconds"] = (
        time.time() - start
        - metrics["runtime_seconds"]
    )

    del train_matrix
    del eval_matrix
    del vectorizer

    return metrics


def run_char(
    train_text,
    eval_text,
    train_targets,
    eval_targets,
):
    print()
    print("CHAR TF-IDF")

    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(3, 5),
        max_features=MAX_FEATURES,
        min_df=2,
        sublinear_tf=True,
    )

    start = time.time()

    train_matrix = vectorizer.fit_transform(
        train_text
    )

    eval_matrix = vectorizer.transform(
        eval_text
    )

    print(
        f"Train matrix: {train_matrix.shape}"
    )

    print(
        f"Eval matrix: {eval_matrix.shape}"
    )

    metrics = retrieve(
        train_matrix,
        eval_matrix,
        train_targets,
        eval_targets,
    )

    metrics["vectorization_seconds"] = (
        time.time() - start
        - metrics["runtime_seconds"]
    )

    del train_matrix
    del eval_matrix
    del vectorizer

    return metrics


def run_word_char(
    train_text,
    eval_text,
    train_targets,
    eval_targets,
):
    print()
    print("WORD + CHAR TF-IDF")

    word_vectorizer = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 1),
        max_features=MAX_FEATURES,
        min_df=2,
        sublinear_tf=True,
    )

    char_vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(3, 5),
        max_features=MAX_FEATURES,
        min_df=2,
        sublinear_tf=True,
    )

    start = time.time()

    train_word = word_vectorizer.fit_transform(
        train_text
    )

    eval_word = word_vectorizer.transform(
        eval_text
    )

    del word_vectorizer

    train_char = char_vectorizer.fit_transform(
        train_text
    )

    eval_char = char_vectorizer.transform(
        eval_text
    )

    del char_vectorizer

    train_matrix = hstack(
        [
            train_word,
            train_char,
        ],
        format="csr",
    )

    eval_matrix = hstack(
        [
            eval_word,
            eval_char,
        ],
        format="csr",
    )

    del train_word
    del eval_word
    del train_char
    del eval_char

    print(
        f"Train matrix: {train_matrix.shape}"
    )

    print(
        f"Eval matrix: {eval_matrix.shape}"
    )

    metrics = retrieve(
        train_matrix,
        eval_matrix,
        train_targets,
        eval_targets,
    )

    metrics["vectorization_seconds"] = (
        time.time() - start
        - metrics["runtime_seconds"]
    )

    del train_matrix
    del eval_matrix

    return metrics


def main():
    RESULTS.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "T4-MOD-008 retrieval screening"
    )

    train = pd.read_csv(
        TRAIN_FILE
    )

    evaluation = pd.read_csv(
        EVAL_FILE
    )

    train_targets = (
        train["target_assignee"]
        .astype(str)
        .to_numpy()
    )

    candidate_set = set(
        train_targets
    )

    covered = evaluation[
        evaluation["target_assignee"]
        .astype(str)
        .isin(candidate_set)
    ].copy()

    covered = covered.sort_values(
        ["Creation time", "ID"],
        kind="mergesort",
    )

    sample = covered.head(
        SAMPLE_SIZE
    )

    train_text = make_text(
        train
    )

    eval_text = make_text(
        sample
    )

    eval_targets = (
        sample["target_assignee"]
        .astype(str)
        .to_numpy()
    )

    print(
        f"TRAIN_ROWS={len(train)}"
    )

    print(
        f"COVERED_EVALUATION_ROWS={len(covered)}"
    )

    print(
        f"SCREEN_SAMPLE={len(sample)}"
    )

    print(
        f"TOP_K={TOP_K}"
    )

    results = {}

    results["word"] = run_word(
        train_text,
        eval_text,
        train_targets,
        eval_targets,
    )

    results["char"] = run_char(
        train_text,
        eval_text,
        train_targets,
        eval_targets,
    )

    results["word_char"] = run_word_char(
        train_text,
        eval_text,
        train_targets,
        eval_targets,
    )

    output = {
        "experiment": "T4-MOD-008",
        "type": "retrieval_screening",
        "status": "COMPLETE",
        "sample_size": len(sample),
        "top_k": TOP_K,
        "results": results,
        "baseline": {
            "mod007_hit_at_20": 0.457450,
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
        RESULT_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            indent=2,
        )

    print()
    print("SCREENING RESULTS")

    for name, result in results.items():
        print(
            f"{name}: "
            f"Hit@1={result['hit_at_1']:.6f} "
            f"Hit@3={result['hit_at_3']:.6f} "
            f"Hit@5={result['hit_at_5']:.6f} "
            f"Hit@10={result['hit_at_10']:.6f} "
            f"Hit@20={result['hit_at_20']:.6f}"
        )

    print()
    print(
        f"RESULTS_SAVED={RESULT_FILE}"
    )

    print(
        "T4-MOD-008_SCREEN_COMPLETE"
    )


if __name__ == "__main__":
    main()