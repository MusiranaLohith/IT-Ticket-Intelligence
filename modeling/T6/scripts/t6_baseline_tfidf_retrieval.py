#!/usr/bin/env python3

"""
T6 — MOD-004
TF-IDF + Cosine Similarity Retrieval Baseline

Task:
    Duplicate-related ticket retrieval.

Formulation:
    Given a query ticket at Creation time, rank the 101 candidates
    in its native candidate pool using lexical TF-IDF cosine similarity.

Important semantic constraints:
    - The positive candidate is the observed Dupe-of target.
    - observable_non_positive is NOT treated as a true negative.
    - No post-Creation information is used.
    - No target-ticket relationship information is used as a query feature.
    - No probabilities or automation thresholds are produced.

Vectorizer policy:
    - Vocabulary and IDF are fitted on TRAIN text only.
    - TRAIN labels are not used.
    - EVAL is transformed using the frozen TRAIN vectorizer.

Evaluation:
    Recall@1, @3, @5, @10, @20
    MRR
    NDCG@5
    NDCG@10
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer


# ============================================================================
# Paths
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

TRAIN_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "splits"
    / "t6_train_group_aware.csv"
)

EVAL_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "splits"
    / "t6_eval_group_aware.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "models"
)

METRICS_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
)

LOG_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "logs"
)

MODEL_DIR.mkdir(parents=True, exist_ok=True)
METRICS_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


VECTORIZER_PATH = (
    MODEL_DIR / "t6_mod004_tfidf_vectorizer.joblib"
)

RESULTS_PATH = (
    METRICS_DIR / "t6_mod004_tfidf_retrieval_results.json"
)

QUERY_RESULTS_PATH = (
    METRICS_DIR / "t6_mod004_query_rankings.csv"
)

LOG_PATH = (
    LOG_DIR / "t6_mod004_tfidf_retrieval.log"
)


# ============================================================================
# Frozen feature definition
# ============================================================================

QUERY_COLUMNS = [
    "query_creator",
    "query_creator_detail",
    "query_summary",
    "query_description",
]

CANDIDATE_COLUMNS = [
    "candidate_creator",
    "candidate_creator_detail",
    "candidate_summary",
    "candidate_description",
]

EXPECTED_CANDIDATES_PER_QUERY = 101
EXPECTED_POSITIVE_PER_QUERY = 1

K_VALUES = [1, 3, 5, 10, 20]


# ============================================================================
# Text construction
# ============================================================================

def clean_text(value: object) -> str:
    """Convert a value into deterministic text."""
    if pd.isna(value):
        return ""
    return str(value).strip()


def build_text(
    frame: pd.DataFrame,
    columns: list[str],
) -> pd.Series:
    """
    Concatenate the four permitted Creation-time fields.

    Field names are included as textual markers so that the representation
    remains field-aware while staying within a simple classical baseline.
    """
    parts = []

    for column in columns:
        field_name = column.replace("_", " ")
        values = frame[column].map(clean_text)

        parts.append(
            field_name
            + " "
            + values
        )

    result = parts[0]

    for part in parts[1:]:
        result = result + " " + part

    return result


# ============================================================================
# Ranking metrics
# ============================================================================

def reciprocal_rank(rank: int) -> float:
    if rank <= 0:
        return 0.0
    return 1.0 / float(rank)


def dcg_at_k(rank: int, k: int) -> float:
    if rank <= 0 or rank > k:
        return 0.0

    return 1.0 / np.log2(rank + 1.0)


def ndcg_single_positive(rank: int, k: int) -> float:
    """
    With exactly one relevant candidate:
        ideal DCG = 1
        NDCG = 1/log2(rank+1) when rank <= k
    """
    return dcg_at_k(rank, k)


# ============================================================================
# Query-level ranking
# ============================================================================

def rank_candidates(
    query_vector,
    candidate_matrix: csr_matrix,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute cosine similarity because TF-IDF vectors are L2 normalized.

    Returns:
        ranked_indices
        ranked_scores
    """
    scores = candidate_matrix @ query_vector.T

    scores = np.asarray(
        scores.toarray()
    ).reshape(-1)

    # Stable deterministic ordering:
    # highest similarity first; candidate original order breaks ties.
    indices = np.arange(len(scores))

    order = np.lexsort(
        (
            indices,
            -scores,
        )
    )

    return order, scores[order]


# ============================================================================
# Main
# ============================================================================

def main() -> int:

    start_time = time.perf_counter()

    log_lines: list[str] = []

    def log(message: str) -> None:
        print(message)
        log_lines.append(message)

    log("=" * 80)
    log("T6 MOD-004 — TF-IDF COSINE RETRIEVAL BASELINE")
    log("=" * 80)
    log(f"Train artifact: {TRAIN_PATH}")
    log(f"Evaluation artifact: {EVAL_PATH}")
    log("")

    # ------------------------------------------------------------------------
    # Load train/evaluation artifacts
    # ------------------------------------------------------------------------

    log("[1/8] Loading modeling split artifacts...")

    if not TRAIN_PATH.exists():
        raise FileNotFoundError(
            f"Training artifact not found: {TRAIN_PATH}"
        )

    if not EVAL_PATH.exists():
        raise FileNotFoundError(
            f"Evaluation artifact not found: {EVAL_PATH}"
        )

    train_df = pd.read_csv(TRAIN_PATH)
    eval_df = pd.read_csv(EVAL_PATH)

    log(f"TRAIN rows: {len(train_df):,}")
    log(f"EVAL rows:  {len(eval_df):,}")

    # ------------------------------------------------------------------------
    # Validate required columns
    # ------------------------------------------------------------------------

    log("")
    log("[2/8] Validating retrieval schema...")

    required_columns = (
        QUERY_COLUMNS
        + CANDIDATE_COLUMNS
        + [
            "query_id",
            "candidate_id",
            "candidate_role",
        ]
    )

    for column in required_columns:
        if column not in train_df.columns:
            raise ValueError(
                f"Missing TRAIN column: {column}"
            )

        if column not in eval_df.columns:
            raise ValueError(
                f"Missing EVAL column: {column}"
            )

    log("Required retrieval schema: VALID")

    # ------------------------------------------------------------------------
    # Validate query candidate structure
    # ------------------------------------------------------------------------

    log("")
    log("[3/8] Validating native query-candidate structure...")

    for name, frame in (
        ("TRAIN", train_df),
        ("EVAL", eval_df),
    ):
        query_sizes = frame.groupby(
            "query_id"
        ).size()

        if not bool(
            (query_sizes == EXPECTED_CANDIDATES_PER_QUERY).all()
        ):
            bad_queries = int(
                (
                    query_sizes
                    != EXPECTED_CANDIDATES_PER_QUERY
                ).sum()
            )

            raise ValueError(
                f"{name}: {bad_queries} queries do not contain "
                f"exactly {EXPECTED_CANDIDATES_PER_QUERY} candidates."
            )

        positive_counts = (
            frame["candidate_role"]
            .astype(str)
            .eq("positive")
            .groupby(frame["query_id"])
            .sum()
        )

        if not bool(
            (positive_counts == EXPECTED_POSITIVE_PER_QUERY).all()
        ):
            raise ValueError(
                f"{name}: not every query has exactly one positive."
            )

        duplicate_pairs = int(
            frame.duplicated(
                subset=["query_id", "candidate_id"]
            ).sum()
        )

        if duplicate_pairs != 0:
            raise ValueError(
                f"{name}: {duplicate_pairs} duplicate "
                "query-candidate pairs detected."
            )

    log("101 candidates/query: VALID")
    log("Exactly one positive/query: VALID")
    log("No duplicate query-candidate pairs: VALID")

    # ------------------------------------------------------------------------
    # Build text
    # ------------------------------------------------------------------------

    log("")
    log("[4/8] Building permitted query/candidate text representations...")

    train_query_text = build_text(
        train_df,
        QUERY_COLUMNS,
    )

    train_candidate_text = build_text(
        train_df,
        CANDIDATE_COLUMNS,
    )

    eval_query_text = build_text(
        eval_df,
        QUERY_COLUMNS,
    )

    eval_candidate_text = build_text(
        eval_df,
        CANDIDATE_COLUMNS,
    )

    log("Query features:")
    log("  Creator")
    log("  Creator Detail")
    log("  Summary")
    log("  Description")

    log("Candidate features:")
    log("  Creator")
    log("  Creator Detail")
    log("  Summary")
    log("  Description")

    # ------------------------------------------------------------------------
    # Fit TF-IDF on TRAIN only
    # ------------------------------------------------------------------------

    log("")
    log("[5/8] Fitting TF-IDF vectorizer on TRAIN only...")

    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        analyzer="word",
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.98,
        sublinear_tf=True,
        max_features=100_000,
        norm="l2",
    )

    # Fit vocabulary and IDF only on TRAIN documents.
    #
    # We use both query and candidate text from TRAIN because this is an
    # unsupervised retrieval representation. No labels are used.
    fit_text = pd.concat(
        [
            train_query_text,
            train_candidate_text,
        ],
        ignore_index=True,
    )

    vectorizer.fit(fit_text)

    feature_count = len(
        vectorizer.vocabulary_
    )

    log(f"TF-IDF vocabulary size: {feature_count:,}")

    if feature_count == 0:
        raise RuntimeError(
            "TF-IDF vocabulary is empty."
        )

    joblib.dump(
        vectorizer,
        VECTORIZER_PATH,
    )

    log(f"Vectorizer saved: {VECTORIZER_PATH}")

    # ------------------------------------------------------------------------
    # Transform
    # ------------------------------------------------------------------------

    log("")
    log("[6/8] Transforming TRAIN/EVAL query and candidate representations...")

    train_query_matrix = vectorizer.transform(
        train_query_text
    )

    train_candidate_matrix = vectorizer.transform(
        train_candidate_text
    )

    eval_query_matrix = vectorizer.transform(
        eval_query_text
    )

    eval_candidate_matrix = vectorizer.transform(
        eval_candidate_text
    )

    log(
        "TRAIN query matrix: "
        f"{train_query_matrix.shape[0]:,} x "
        f"{train_query_matrix.shape[1]:,}"
    )

    log(
        "TRAIN candidate matrix: "
        f"{train_candidate_matrix.shape[0]:,} x "
        f"{train_candidate_matrix.shape[1]:,}"
    )

    log(
        "EVAL query matrix: "
        f"{eval_query_matrix.shape[0]:,} x "
        f"{eval_query_matrix.shape[1]:,}"
    )

    log(
        "EVAL candidate matrix: "
        f"{eval_candidate_matrix.shape[0]:,} x "
        f"{eval_candidate_matrix.shape[1]:,}"
    )

    # ------------------------------------------------------------------------
    # Evaluate retrieval
    # ------------------------------------------------------------------------

    log("")
    log("[7/8] Ranking candidates and calculating retrieval metrics...")

    all_query_results: list[dict] = []

    metric_values = {
        "train": {
            "recall_at_1": [],
            "recall_at_3": [],
            "recall_at_5": [],
            "recall_at_10": [],
            "recall_at_20": [],
            "mrr": [],
            "ndcg_at_5": [],
            "ndcg_at_10": [],
        },
        "eval": {
            "recall_at_1": [],
            "recall_at_3": [],
            "recall_at_5": [],
            "recall_at_10": [],
            "recall_at_20": [],
            "mrr": [],
            "ndcg_at_5": [],
            "ndcg_at_10": [],
        },
    }

    def evaluate_split(
        split_name: str,
        frame: pd.DataFrame,
        query_matrix,
        candidate_matrix,
    ) -> None:

        grouped_indices = frame.groupby(
            "query_id",
            sort=False,
        ).indices

        for query_id, row_indices in grouped_indices.items():

            row_indices = np.asarray(
                row_indices,
                dtype=int,
            )

            query_vector = query_matrix[
                row_indices[0]
            ]

            candidate_vectors = candidate_matrix[
                row_indices
            ]

            ranked_local_indices, ranked_scores = rank_candidates(
                query_vector,
                candidate_vectors,
            )

            ranked_original_indices = (
                row_indices[
                    ranked_local_indices
                ]
            )

            ranked_roles = (
                frame.iloc[
                    ranked_original_indices
                ]["candidate_role"]
                .astype(str)
                .to_numpy()
            )

            positive_positions = np.flatnonzero(
                ranked_roles == "positive"
            )

            if len(positive_positions) != 1:
                raise RuntimeError(
                    f"{split_name}: query {query_id} does not "
                    "have exactly one ranked positive."
                )

            positive_rank = int(
                positive_positions[0]
            ) + 1

            # Top-k recall for one positive candidate.
            recall_values = {}

            for k in K_VALUES:
                recall_values[k] = (
                    1.0
                    if positive_rank <= k
                    else 0.0
                )

            mrr_value = reciprocal_rank(
                positive_rank
            )

            ndcg5 = ndcg_single_positive(
                positive_rank,
                5,
            )

            ndcg10 = ndcg_single_positive(
                positive_rank,
                10,
            )

            metric_values[
                split_name
            ]["recall_at_1"].append(
                recall_values[1]
            )

            metric_values[
                split_name
            ]["recall_at_3"].append(
                recall_values[3]
            )

            metric_values[
                split_name
            ]["recall_at_5"].append(
                recall_values[5]
            )

            metric_values[
                split_name
            ]["recall_at_10"].append(
                recall_values[10]
            )

            metric_values[
                split_name
            ]["recall_at_20"].append(
                recall_values[20]
            )

            metric_values[
                split_name
            ]["mrr"].append(
                mrr_value
            )

            metric_values[
                split_name
            ]["ndcg_at_5"].append(
                ndcg5
            )

            metric_values[
                split_name
            ]["ndcg_at_10"].append(
                ndcg10
            )

            # Record only the ranking position and enough metadata for
            # later analysis. This is not used to fit anything.
            positive_row = frame.iloc[
                row_indices[
                    frame.iloc[
                        row_indices
                    ]["candidate_role"]
                    .astype(str)
                    .eq("positive")
                    .to_numpy()
                    .argmax()
                ]
            ]

            top_ranked_original_index = (
                ranked_original_indices[0]
            )

            top_candidate = frame.iloc[
                top_ranked_original_index
            ]

            all_query_results.append(
                {
                    "split": split_name,
                    "query_id": query_id,
                    "positive_candidate_id": positive_row[
                        "candidate_id"
                    ],
                    "positive_rank": positive_rank,
                    "top_candidate_id": top_candidate[
                        "candidate_id"
                    ],
                    "top_candidate_role": top_candidate[
                        "candidate_role"
                    ],
                    "top_score": float(
                        ranked_scores[0]
                    ),
                    "positive_score": float(
                        ranked_scores[
                            positive_rank - 1
                        ]
                    ),
                }
            )

    evaluate_split(
        "train",
        train_df,
        train_query_matrix,
        train_candidate_matrix,
    )

    evaluate_split(
        "eval",
        eval_df,
        eval_query_matrix,
        eval_candidate_matrix,
    )

    # ------------------------------------------------------------------------
    # Aggregate metrics
    # ------------------------------------------------------------------------

    log("")
    log("[8/8] Aggregating and saving retrieval results...")

    def mean_metric(
        values: list[float],
    ) -> float:
        return float(
            np.mean(
                np.asarray(values, dtype=float)
            )
        )

    train_metrics = {
        "recall_at_1": mean_metric(
            metric_values["train"]["recall_at_1"]
        ),
        "recall_at_3": mean_metric(
            metric_values["train"]["recall_at_3"]
        ),
        "recall_at_5": mean_metric(
            metric_values["train"]["recall_at_5"]
        ),
        "recall_at_10": mean_metric(
            metric_values["train"]["recall_at_10"]
        ),
        "recall_at_20": mean_metric(
            metric_values["train"]["recall_at_20"]
        ),
        "mrr": mean_metric(
            metric_values["train"]["mrr"]
        ),
        "ndcg_at_5": mean_metric(
            metric_values["train"]["ndcg_at_5"]
        ),
        "ndcg_at_10": mean_metric(
            metric_values["train"]["ndcg_at_10"]
        ),
    }

    eval_metrics = {
        "recall_at_1": mean_metric(
            metric_values["eval"]["recall_at_1"]
        ),
        "recall_at_3": mean_metric(
            metric_values["eval"]["recall_at_3"]
        ),
        "recall_at_5": mean_metric(
            metric_values["eval"]["recall_at_5"]
        ),
        "recall_at_10": mean_metric(
            metric_values["eval"]["recall_at_10"]
        ),
        "recall_at_20": mean_metric(
            metric_values["eval"]["recall_at_20"]
        ),
        "mrr": mean_metric(
            metric_values["eval"]["mrr"]
        ),
        "ndcg_at_5": mean_metric(
            metric_values["eval"]["ndcg_at_5"]
        ),
        "ndcg_at_10": mean_metric(
            metric_values["eval"]["ndcg_at_10"]
        ),
    }

    query_results_df = pd.DataFrame(
        all_query_results
    )

    query_results_df.to_csv(
        QUERY_RESULTS_PATH,
        index=False,
    )

    elapsed_seconds = (
        time.perf_counter()
        - start_time
    )

    results = {
        "operation": "T6 MOD-004",
        "task": "T6 Similar-Ticket Retrieval",
        "status": "BASELINE_COMPLETED",

        "model": {
            "name": "TFIDF_COSINE_RETRIEVAL",
            "family": "lexical_information_retrieval",
            "supervised": False,
            "similarity": "cosine",
        },

        "feature_policy": {
            "query_features": QUERY_COLUMNS,
            "candidate_features": CANDIDATE_COLUMNS,
            "post_creation_information_used": False,
            "target_ticket_information_used_as_query_feature": False,
        },

        "vectorizer": {
            "analyzer": "word",
            "ngram_range": [1, 2],
            "min_df": 2,
            "max_df": 0.98,
            "sublinear_tf": True,
            "max_features": 100000,
            "normalization": "l2",
            "fit_source": "TRAIN_QUERY_AND_CANDIDATE_TEXT_ONLY",
            "feature_count": feature_count,
        },

        "candidate_structure": {
            "candidates_per_query": EXPECTED_CANDIDATES_PER_QUERY,
            "positive_per_query": EXPECTED_POSITIVE_PER_QUERY,
            "observable_non_positive_semantics": (
                "NOT_TRUE_NEGATIVE"
            ),
        },

        "train": {
            "rows": int(len(train_df)),
            "queries": int(train_df["query_id"].nunique()),
            "metrics": train_metrics,
        },

        "evaluation": {
            "rows": int(len(eval_df)),
            "queries": int(eval_df["query_id"].nunique()),
            "metrics": eval_metrics,
        },

        "evaluation_metrics": [
            "Recall@1",
            "Recall@3",
            "Recall@5",
            "Recall@10",
            "Recall@20",
            "MRR",
            "NDCG@5",
            "NDCG@10",
        ],

        "controls": {
            "train_only_vectorizer_fit": True,
            "evaluation_used_for_vectorizer_fit": False,
            "labels_used_for_vectorizer_fit": False,
            "observable_non_positive_converted_to_true_negative": False,
            "threshold_optimization": False,
            "probability_calibration": False,
            "automation_threshold": False,
            "raw_source_modified": False,
            "accepted_dtm_artifact_modified": False,
        },

        "artifacts": {
            "vectorizer": str(VECTORIZER_PATH),
            "query_rankings": str(QUERY_RESULTS_PATH),
            "results": str(RESULTS_PATH),
        },

        "runtime_seconds": float(
            elapsed_seconds
        ),
    }

    with RESULTS_PATH.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            results,
            handle,
            indent=2,
            ensure_ascii=False,
        )

    # ------------------------------------------------------------------------
    # Console summary
    # ------------------------------------------------------------------------

    log("")
    log("=" * 80)
    log("T6 MOD-004 — BASELINE RESULTS")
    log("=" * 80)

    log("TRAIN")
    for key, value in train_metrics.items():
        log(f"  {key}: {value:.6f}")

    log("")
    log("EVAL")
    for key, value in eval_metrics.items():
        log(f"  {key}: {value:.6f}")

    log("")
    log(f"Runtime: {elapsed_seconds:.2f} seconds")

    log("")
    log("Artifacts:")
    log(f"  {VECTORIZER_PATH}")
    log(f"  {QUERY_RESULTS_PATH}")
    log(f"  {RESULTS_PATH}")

    log("")
    log("T6 MOD-004: BASELINE_COMPLETED")

    LOG_PATH.write_text(
        "\n".join(log_lines) + "\n",
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("")
        print("=" * 80)
        print("T6 MOD-004 FAILED")
        print("=" * 80)
        print(f"{type(exc).__name__}: {exc}")
        raise