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
RESULT_FILE = RESULTS / "t4_mod008_full.json"

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


def retrieve(
    train_matrix,
    eval_matrix,
    train_targets,
    eval_targets,
    covered_mask,
):
    total_rows = len(eval_targets)
    covered_rows = int(np.sum(covered_mask))

    hits = {1: 0, 3: 0, 5: 0, 10: 0, 20: 0}
    covered_hits = {1: 0, 3: 0, 5: 0, 10: 0, 20: 0}

    retrieved_true = 0

    start = time.time()

    for start_idx in range(
        0,
        total_rows,
        BATCH_SIZE,
    ):
        end_idx = min(
            start_idx + BATCH_SIZE,
            total_rows,
        )

        similarities = (
            eval_matrix[start_idx:end_idx]
            @ train_matrix.T
        )

        for local_idx in range(
            end_idx - start_idx
        ):
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

            retrieved_true += 1

            rank = int(found[0]) + 1

            for k in hits:
                if rank <= k:
                    hits[k] += 1

                    if covered_mask[
                        start_idx + local_idx
                    ]:
                        covered_hits[k] += 1

        elapsed = time.time() - start

        print(
            f"Processed {end_idx}/{total_rows} "
            f"({end_idx / total_rows:.1%}) "
            f"elapsed={elapsed:.1f}s"
        )

        del similarities

    runtime = time.time() - start

    return {
        "overall": {
            f"hit_at_{k}": hits[k] / total_rows
            for k in hits
        },
        "covered": {
            f"hit_at_{k}": (
                covered_hits[k] / covered_rows
                if covered_rows
                else 0.0
            )
            for k in covered_hits
        },
        "retrieved_true_assignee_rows": retrieved_true,
        "retrieval_coverage_at_20": (
            retrieved_true / covered_rows
            if covered_rows
            else 0.0
        ),
        "runtime_seconds": runtime,
    }


def main():
    RESULTS.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "T4-MOD-008 full Word + Character retrieval"
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

    eval_targets = (
        evaluation["target_assignee"]
        .astype(str)
        .to_numpy()
    )

    candidate_set = set(
        train_targets
    )

    covered_mask = np.asarray(
        [
            target in candidate_set
            for target in eval_targets
        ],
        dtype=bool,
    )

    covered_rows = int(
        np.sum(covered_mask)
    )

    unseen_rows = int(
        np.sum(~covered_mask)
    )

    print(
        f"TRAIN_ROWS={len(train)}"
    )

    print(
        f"EVALUATION_ROWS={len(evaluation)}"
    )

    print(
        f"TRAINING_CANDIDATES={len(candidate_set)}"
    )

    print(
        f"COVERED_ROWS={covered_rows}"
    )

    print(
        f"UNSEEN_ROWS={unseen_rows}"
    )

    train_text = make_text(train)
    eval_text = make_text(evaluation)

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

    print()
    print("FITTING WORD TF-IDF")

    start = time.time()

    train_word = word_vectorizer.fit_transform(
        train_text
    )

    eval_word = word_vectorizer.transform(
        eval_text
    )

    print(
        f"Train word matrix: {train_word.shape}"
    )

    print(
        f"Eval word matrix: {eval_word.shape}"
    )

    print(
        f"Word vectorization: "
        f"{time.time() - start:.2f}s"
    )

    del word_vectorizer

    print()
    print("FITTING CHARACTER TF-IDF")

    start = time.time()

    train_char = char_vectorizer.fit_transform(
        train_text
    )

    eval_char = char_vectorizer.transform(
        eval_text
    )

    print(
        f"Train char matrix: {train_char.shape}"
    )

    print(
        f"Eval char matrix: {eval_char.shape}"
    )

    print(
        f"Character vectorization: "
        f"{time.time() - start:.2f}s"
    )

    del char_vectorizer

    print()
    print("COMBINING REPRESENTATIONS")

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
        f"Combined train matrix: "
        f"{train_matrix.shape}"
    )

    print(
        f"Combined eval matrix: "
        f"{eval_matrix.shape}"
    )

    print()
    print("FULL RETRIEVAL")

    retrieval_result = retrieve(
        train_matrix,
        eval_matrix,
        train_targets,
        eval_targets,
        covered_mask,
    )

    output = {
        "experiment": "T4-MOD-008",
        "status": "COMPLETE",
        "representation": {
            "type": "word_plus_character_tfidf",
            "word_features": MAX_FEATURES,
            "character_features": MAX_FEATURES,
            "total_features": MAX_FEATURES * 2,
            "word_ngrams": [1, 1],
            "character_ngrams": [3, 5],
        },
        "population": {
            "train_rows": len(train),
            "evaluation_rows": len(evaluation),
            "covered_rows": covered_rows,
            "unseen_rows": unseen_rows,
            "training_candidates": len(candidate_set),
        },
        "retrieval": retrieval_result,
        "comparison": {
            "mod007_full_hit_at_20": 0.457450,
            "mod008_screen_hit_at_20": 0.584000,
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
    print("FINAL RESULTS")

    for k in [1, 3, 5, 10, 20]:
        print(
            f"Overall Hit@{k}: "
            f"{retrieval_result['overall'][f'hit_at_{k}']:.6f}"
        )

    print()

    for k in [1, 3, 5, 10, 20]:
        print(
            f"Covered Hit@{k}: "
            f"{retrieval_result['covered'][f'hit_at_{k}']:.6f}"
        )

    print()
    print(
        "True-assignee retrieval coverage@20: "
        f"{retrieval_result['retrieval_coverage_at_20']:.6f}"
    )

    print()
    print(
        f"RESULTS_SAVED={RESULT_FILE}"
    )

    print(
        "T4-MOD-008_FULL_COMPLETE"
    )


if __name__ == "__main__":
    main()