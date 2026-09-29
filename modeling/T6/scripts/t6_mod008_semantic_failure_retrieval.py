#!/usr/bin/env python3

"""
T6 — MOD-008
Bounded Semantic Retrieval on TF-IDF Failure Cases

Purpose:
    Test whether semantic embeddings can recover T6 queries for which
    the lexical TF-IDF baseline failed to place the observed Dupe-of
    target inside Top-20.

This is a bounded diagnostic experiment.

Primary evaluation population:
    173 MOD-005 Top-20 TF-IDF failures.

Candidate pools:
    Exactly the same frozen 101-candidate pools already materialized
    in the T6 TRAIN/EVAL split artifacts.

Semantic model:
    sentence-transformers/all-MiniLM-L6-v2

Important:
    - This is retrieval/ranking, NOT binary classification.
    - observable_non_positive is NOT treated as a true negative.
    - No new candidate pool is constructed.
    - No labels are changed.
    - No threshold is optimized.
    - No calibration is performed.
    - The full raw Mozilla CORE dataset is NOT read.
    - The full 274,922-row candidate layer is NOT embedded.
    - Only the 173 failure queries and their 101 candidates/query
      are embedded.

Outputs:
    modeling/T6/metrics/t6_mod008_semantic_failure_rankings.csv
    modeling/T6/metrics/t6_mod008_semantic_failure_results.json
    modeling/T6/logs/t6_mod008_semantic_failure_retrieval.log

The experiment compares:
    - original TF-IDF positive rank
    - semantic positive rank
    - semantic recovery into Top-1/3/5/10/20
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================================
# Paths
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

FAILURES_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod005_top20_failures.csv"
)

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

OUTPUT_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
)

RANKINGS_PATH = (
    OUTPUT_DIR
    / "t6_mod008_semantic_failure_rankings.csv"
)

RESULTS_PATH = (
    OUTPUT_DIR
    / "t6_mod008_semantic_failure_results.json"
)

LOG_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "logs"
)

LOG_PATH = (
    LOG_DIR
    / "t6_mod008_semantic_failure_retrieval.log"
)


# ============================================================================
# Configuration
# ============================================================================

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

CANDIDATES_PER_QUERY = 101

K_VALUES = [
    1,
    3,
    5,
    10,
    20,
]

BATCH_SIZE = 32

# CPU-only environment: keep the experiment deterministic and bounded.
DEVICE = "cpu"


# ============================================================================
# Required schema
# ============================================================================

FAILURE_COLUMNS = [
    "split",
    "query_id",
    "positive_candidate_id",
    "positive_rank",
    "top_candidate_id",
    "top_candidate_role",
    "top_score",
    "positive_score",
]

MODEL_COLUMNS = [
    "query_id",
    "query_creation_time",
    "query_creator",
    "query_creator_detail",
    "query_summary",
    "query_description",
    "candidate_id",
    "candidate_creation_time",
    "candidate_creator",
    "candidate_creator_detail",
    "candidate_summary",
    "candidate_description",
    "candidate_role",
    "target_observed",
    "target_type",
    "sampling_protocol",
    "sampling_seed",
]


# ============================================================================
# Text construction
# ============================================================================

def safe_text(value: object) -> str:
    if pd.isna(value):
        return ""

    return str(value).strip()


def build_query_text(row: pd.Series) -> str:
    """
    Reproduce the four admitted creation-time query fields.
    """

    parts = [
        safe_text(row["query_creator"]),
        safe_text(row["query_creator_detail"]),
        safe_text(row["query_summary"]),
        safe_text(row["query_description"]),
    ]

    return " ".join(
        part for part in parts if part
    )


def build_candidate_text(row: pd.Series) -> str:
    """
    Reproduce the four admitted creation-time candidate fields.
    """

    parts = [
        safe_text(row["candidate_creator"]),
        safe_text(row["candidate_creator_detail"]),
        safe_text(row["candidate_summary"]),
        safe_text(row["candidate_description"]),
    ]

    return " ".join(
        part for part in parts if part
    )


# ============================================================================
# Validation
# ============================================================================

def validate_columns(
    frame: pd.DataFrame,
    required: list[str],
    name: str,
) -> None:

    missing = [
        column
        for column in required
        if column not in frame.columns
    ]

    if missing:
        raise ValueError(
            f"{name} missing required columns: "
            + ", ".join(missing)
        )


def validate_failure_population(
    failures: pd.DataFrame,
) -> None:

    if failures.empty:
        raise ValueError(
            "MOD-005 failure artifact is empty."
        )

    if failures["query_id"].duplicated().any():
        raise ValueError(
            "Duplicate query IDs in MOD-005 failure artifact."
        )

    if not (
        failures["positive_rank"]
        .astype(int)
        .gt(20)
        .all()
    ):
        raise ValueError(
            "Failure artifact contains a query with positive_rank <= 20."
        )


def validate_query_group(
    group: pd.DataFrame,
    query_id: str,
) -> None:

    if len(group) != CANDIDATES_PER_QUERY:
        raise ValueError(
            f"Query {query_id} has {len(group)} candidates; "
            f"expected {CANDIDATES_PER_QUERY}."
        )

    if group["candidate_id"].duplicated().any():
        raise ValueError(
            f"Query {query_id} contains duplicate candidate IDs."
        )

    positive_mask = (
        group["target_observed"]
        .astype(bool)
        .to_numpy()
    )

    if int(positive_mask.sum()) != 1:
        raise ValueError(
            f"Query {query_id} does not contain exactly one "
            "observed positive."
        )


# ============================================================================
# Metrics
# ============================================================================

def calculate_metrics(
    ranking_frame: pd.DataFrame,
) -> dict:

    ranks = (
        ranking_frame["semantic_positive_rank"]
        .astype(int)
    )

    total = len(ranks)

    return {
        "queries": int(total),

        "recall_at_1": float(
            (ranks <= 1).mean()
        ),

        "recall_at_3": float(
            (ranks <= 3).mean()
        ),

        "recall_at_5": float(
            (ranks <= 5).mean()
        ),

        "recall_at_10": float(
            (ranks <= 10).mean()
        ),

        "recall_at_20": float(
            (ranks <= 20).mean()
        ),

        "mrr": float(
            (1.0 / ranks).mean()
        ),

        "ndcg_at_5": float(
            np.where(
                ranks <= 5,
                1.0 / np.log2(
                    ranks + 1
                ),
                0.0,
            ).mean()
        ),

        "ndcg_at_10": float(
            np.where(
                ranks <= 10,
                1.0 / np.log2(
                    ranks + 1
                ),
                0.0,
            ).mean()
        ),

        "positive_rank": {
            "minimum": int(ranks.min()),
            "median": float(ranks.median()),
            "mean": float(ranks.mean()),
            "maximum": int(ranks.max()),
        },
    }


# ============================================================================
# Main
# ============================================================================

def main() -> int:

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    log_lines: list[str] = []

    def log(message: str) -> None:
        print(message)
        log_lines.append(message)

    overall_start = time.time()

    log("=" * 80)
    log("T6 MOD-008 — BOUNDED SEMANTIC RETRIEVAL")
    log("=" * 80)

    log("")
    log("Purpose:")
    log(
        "Test semantic retrieval specifically on the "
        "MOD-005 TF-IDF Top-20 failure population."
    )

    log("")
    log("Semantic model:")
    log(f"  {MODEL_NAME}")

    log("")
    log("Device:")
    log(f"  {DEVICE}")

    # ------------------------------------------------------------------------
    # Import dependency
    # ------------------------------------------------------------------------

    log("")
    log("[1/8] Loading semantic retrieval dependency...")

    try:
        from sentence_transformers import (
            SentenceTransformer,
        )
    except ImportError as exc:
        raise ImportError(
            "sentence-transformers is not installed in the active "
            "environment. Install it before running MOD-008."
        ) from exc

    log(
        "sentence-transformers import: OK"
    )

    # ------------------------------------------------------------------------
    # Load failure population
    # ------------------------------------------------------------------------

    log("")
    log("[2/8] Loading MOD-005 failure population...")

    if not FAILURES_PATH.exists():
        raise FileNotFoundError(
            f"Failure artifact not found: {FAILURES_PATH}"
        )

    failures = pd.read_csv(
        FAILURES_PATH
    )

    validate_columns(
        failures,
        FAILURE_COLUMNS,
        "MOD-005 failure artifact",
    )

    validate_failure_population(
        failures
    )

    failures["query_id"] = (
        failures["query_id"]
        .astype(str)
    )

    failures["positive_candidate_id"] = (
        failures["positive_candidate_id"]
        .astype(str)
    )

    log(
        f"Failure queries: {len(failures):,}"
    )

    # ------------------------------------------------------------------------
    # Load materialized splits
    # ------------------------------------------------------------------------

    log("")
    log("[3/8] Loading frozen T6 modeling splits...")

    if not TRAIN_PATH.exists():
        raise FileNotFoundError(
            f"TRAIN split not found: {TRAIN_PATH}"
        )

    if not EVAL_PATH.exists():
        raise FileNotFoundError(
            f"EVAL split not found: {EVAL_PATH}"
        )

    train = pd.read_csv(
        TRAIN_PATH
    )

    evaluation = pd.read_csv(
        EVAL_PATH
    )

    validate_columns(
        train,
        MODEL_COLUMNS,
        "TRAIN modeling artifact",
    )

    validate_columns(
        evaluation,
        MODEL_COLUMNS,
        "EVAL modeling artifact",
    )

    train["query_id"] = (
        train["query_id"]
        .astype(str)
    )

    train["candidate_id"] = (
        train["candidate_id"]
        .astype(str)
    )

    evaluation["query_id"] = (
        evaluation["query_id"]
        .astype(str)
    )

    evaluation["candidate_id"] = (
        evaluation["candidate_id"]
        .astype(str)
    )

    failure_query_ids = set(
        failures["query_id"]
    )

    train_relevant = train[
        train["query_id"].isin(
            failure_query_ids
        )
    ].copy()

    eval_relevant = evaluation[
        evaluation["query_id"].isin(
            failure_query_ids
        )
    ].copy()

    log(
        f"Relevant TRAIN rows: "
        f"{len(train_relevant):,}"
    )

    log(
        f"Relevant EVAL rows: "
        f"{len(eval_relevant):,}"
    )

    expected_relevant_rows = (
        len(failures)
        * CANDIDATES_PER_QUERY
    )

    actual_relevant_rows = (
        len(train_relevant)
        + len(eval_relevant)
    )

    if actual_relevant_rows != expected_relevant_rows:
        raise ValueError(
            "Failure population does not map to exactly "
            f"{expected_relevant_rows:,} candidate rows. "
            f"Found {actual_relevant_rows:,}."
        )

    # ------------------------------------------------------------------------
    # Load semantic model
    # ------------------------------------------------------------------------

    log("")
    log("[4/8] Loading semantic embedding model...")

    model_start = time.time()

    model = SentenceTransformer(
        MODEL_NAME,
        device=DEVICE,
    )

    model_load_time = (
        time.time()
        - model_start
    )

    log(
        f"Model loaded in "
        f"{model_load_time:.2f} seconds"
    )

    embedding_dimension = (
        model.get_sentence_embedding_dimension()
    )

    log(
        f"Embedding dimension: "
        f"{embedding_dimension}"
    )

    # ------------------------------------------------------------------------
    # Build failure-level query/candidate collections
    # ------------------------------------------------------------------------

    log("")
    log("[5/8] Preparing bounded semantic retrieval population...")

    query_records: list[dict] = []
    candidate_records: list[dict] = []

    # Keep query and candidate records in deterministic failure-artifact order.
    for failure in failures.itertuples(
        index=False
    ):

        split = str(
            failure.split
        )

        query_id = str(
            failure.query_id
        )

        positive_candidate_id = str(
            failure.positive_candidate_id
        )

        split_df = (
            train_relevant
            if split == "train"
            else eval_relevant
        )

        group = split_df[
            split_df["query_id"] == query_id
        ].copy()

        validate_query_group(
            group,
            query_id,
        )

        group = group.reset_index(
            drop=True
        )

        positive_rows = group[
            group["candidate_id"]
            == positive_candidate_id
        ]

        if len(positive_rows) != 1:
            raise ValueError(
                f"Query {query_id}: expected exactly one "
                "observed positive matching MOD-005 failure artifact."
            )

        query_row = group.iloc[0]

        query_text = build_query_text(
            query_row
        )

        query_records.append(
            {
                "split": split,
                "query_id": query_id,
                "positive_candidate_id": (
                    positive_candidate_id
                ),
                "original_tfidf_rank": int(
                    failure.positive_rank
                ),
                "query_text": query_text,
            }
        )

        for candidate_index, candidate_row in group.iterrows():

            candidate_records.append(
                {
                    "split": split,
                    "query_id": query_id,
                    "candidate_id": str(
                        candidate_row[
                            "candidate_id"
                        ]
                    ),
                    "candidate_role": str(
                        candidate_row[
                            "candidate_role"
                        ]
                    ),
                    "candidate_index": int(
                        candidate_index
                    ),
                    "candidate_text": (
                        build_candidate_text(
                            candidate_row
                        )
                    ),
                }
            )

    query_frame = pd.DataFrame(
        query_records
    )

    candidate_frame = pd.DataFrame(
        candidate_records
    )

    log(
        f"Queries to embed: "
        f"{len(query_frame):,}"
    )

    log(
        f"Candidates to embed: "
        f"{len(candidate_frame):,}"
    )

    # ------------------------------------------------------------------------
    # Embed queries and candidates
    # ------------------------------------------------------------------------

    log("")
    log("[6/8] Encoding semantic embeddings...")

    embedding_start = time.time()

    query_embeddings = model.encode(
        query_frame[
            "query_text"
        ].tolist(),
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    candidate_embeddings = model.encode(
        candidate_frame[
            "candidate_text"
        ].tolist(),
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    embedding_runtime = (
        time.time()
        - embedding_start
    )

    log(
        f"Embedding runtime: "
        f"{embedding_runtime:.2f} seconds"
    )

    log(
        f"Query embedding shape: "
        f"{query_embeddings.shape}"
    )

    log(
        f"Candidate embedding shape: "
        f"{candidate_embeddings.shape}"
    )

    # ------------------------------------------------------------------------
    # Rank candidates within each query
    # ------------------------------------------------------------------------

    log("")
    log("[7/8] Ranking semantic candidates...")

    ranking_rows: list[dict] = []

    query_lookup = {
        str(
            row["query_id"]
        ): index
        for index, row
        in query_frame.iterrows()
    }

    query_total = len(query_frame)

    for query_position, query_row in query_frame.iterrows():

        query_id = str(
            query_row["query_id"]
        )

        split = str(
            query_row["split"]
        )

        positive_candidate_id = str(
            query_row[
                "positive_candidate_id"
            ]
        )

        candidate_mask = (
            candidate_frame["query_id"]
            == query_id
        )

        candidate_indices = np.flatnonzero(
            candidate_mask.to_numpy()
        )

        if len(candidate_indices) != CANDIDATES_PER_QUERY:
            raise ValueError(
                f"Query {query_id}: expected "
                f"{CANDIDATES_PER_QUERY} candidate embeddings, "
                f"found {len(candidate_indices)}."
            )

        query_vector = (
            query_embeddings[
                query_position
            ]
        )

        candidate_matrix = (
            candidate_embeddings[
                candidate_indices
            ]
        )

        # Embeddings are normalized, therefore dot product == cosine similarity.
        scores = (
            candidate_matrix
            @ query_vector
        )

        local_candidate_ids = (
            candidate_frame.iloc[
                candidate_indices
            ]["candidate_id"]
            .astype(str)
            .to_numpy()
        )

        positive_local_positions = np.flatnonzero(
            local_candidate_ids
            == positive_candidate_id
        )

        if len(positive_local_positions) != 1:
            raise ValueError(
                f"Query {query_id}: positive candidate not found "
                "exactly once in candidate embedding set."
            )

        positive_local_index = int(
            positive_local_positions[0]
        )

        ordering = sorted(
            range(
                len(candidate_indices)
            ),
            key=lambda local_index: (
                -float(
                    scores[
                        local_index
                    ]
                ),
                local_candidate_ids[
                    local_index
                ],
            ),
        )

        positive_rank = (
            ordering.index(
                positive_local_index
            )
            + 1
        )

        top_local_index = ordering[0]

        top_candidate_id = str(
            local_candidate_ids[
                top_local_index
            ]
        )

        top_score = float(
            scores[
                top_local_index
            ]
        )

        positive_score = float(
            scores[
                positive_local_index
            ]
        )

        ranking_rows.append(
            {
                "split": split,
                "query_id": query_id,
                "positive_candidate_id": (
                    positive_candidate_id
                ),
                "original_tfidf_rank": int(
                    query_row[
                        "original_tfidf_rank"
                    ]
                ),
                "semantic_positive_rank": int(
                    positive_rank
                ),
                "semantic_top_candidate_id": (
                    top_candidate_id
                ),
                "semantic_top_score": top_score,
                "semantic_positive_score": (
                    positive_score
                ),
                "semantic_score_gap_top1_minus_positive": (
                    top_score
                    - positive_score
                ),
            }
        )

        processed = (
            query_position
            + 1
        )

        if (
            processed == 1
            or processed % 25 == 0
            or processed == query_total
        ):
            log(
                f"  ranked "
                f"{processed:,}/{query_total:,} "
                f"failure queries"
            )

    rankings = pd.DataFrame(
        ranking_rows
    )

    # ------------------------------------------------------------------------
    # Save rankings
    # ------------------------------------------------------------------------

    log("")
    log("[8/8] Saving semantic retrieval results...")

    rankings.to_csv(
        RANKINGS_PATH,
        index=False,
    )

    # ------------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------------

    overall_metrics = calculate_metrics(
        rankings
    )

    train_rankings = rankings[
        rankings["split"] == "train"
    ].copy()

    eval_rankings = rankings[
        rankings["split"] == "eval"
    ].copy()

    train_metrics = calculate_metrics(
        train_rankings
    )

    eval_metrics = calculate_metrics(
        eval_rankings
    )

    # ------------------------------------------------------------------------
    # Recovery analysis
    # ------------------------------------------------------------------------

    rankings["tfidf_top20_failure"] = True

    rankings["semantic_recovered_top20"] = (
        rankings["semantic_positive_rank"]
        <= 20
    )

    rankings["semantic_recovered_top10"] = (
        rankings["semantic_positive_rank"]
        <= 10
    )

    rankings["semantic_recovered_top5"] = (
        rankings["semantic_positive_rank"]
        <= 5
    )

    rankings["semantic_recovered_top1"] = (
        rankings["semantic_positive_rank"]
        == 1
    )

    recovery = {
        "top1": int(
            rankings[
                "semantic_recovered_top1"
            ].sum()
        ),
        "top5": int(
            rankings[
                "semantic_recovered_top5"
            ].sum()
        ),
        "top10": int(
            rankings[
                "semantic_recovered_top10"
            ].sum()
        ),
        "top20": int(
            rankings[
                "semantic_recovered_top20"
            ].sum()
        ),
        "total_failure_queries": int(
            len(rankings)
        ),
    }

    recovery_rates = {
        key: float(
            value
            / recovery["total_failure_queries"]
        )
        for key, value in recovery.items()
        if key != "total_failure_queries"
    }

    # ------------------------------------------------------------------------
    # Rank movement
    # ------------------------------------------------------------------------

    rank_movement = (
        rankings["original_tfidf_rank"]
        .astype(int)
        - rankings["semantic_positive_rank"]
        .astype(int)
    )

    rank_movement_summary = {
        "mean_tfidf_rank_minus_semantic_rank": float(
            rank_movement.mean()
        ),
        "median_tfidf_rank_minus_semantic_rank": float(
            rank_movement.median()
        ),
        "semantic_rank_improved_count": int(
            (rank_movement > 0).sum()
        ),
        "semantic_rank_worsened_count": int(
            (rank_movement < 0).sum()
        ),
        "semantic_rank_unchanged_count": int(
            (rank_movement == 0).sum()
        ),
    }

    # ------------------------------------------------------------------------
    # Train/EVAL comparison
    # ------------------------------------------------------------------------

    metric_keys = [
        "recall_at_1",
        "recall_at_3",
        "recall_at_5",
        "recall_at_10",
        "recall_at_20",
        "mrr",
        "ndcg_at_5",
        "ndcg_at_10",
    ]

    eval_minus_train = {
        key: float(
            eval_metrics[key]
            - train_metrics[key]
        )
        for key in metric_keys
    }

    # ------------------------------------------------------------------------
    # Result artifact
    # ------------------------------------------------------------------------

    results = {
        "operation": "T6 MOD-008",

        "task": (
            "T6 Similar-Ticket Retrieval"
        ),

        "task_formulation": (
            "Duplicate-Related Ticket Retrieval"
        ),

        "status": (
            "BOUNDED_SEMANTIC_EXPERIMENT_COMPLETED"
        ),

        "experiment_scope": {
            "purpose": (
                "Test semantic recovery of MOD-005 "
                "TF-IDF Top-20 failures."
            ),
            "failure_queries": int(
                len(failures)
            ),
            "candidates_per_query": (
                CANDIDATES_PER_QUERY
            ),
            "total_candidate_rows": int(
                len(candidate_frame)
            ),
            "same_frozen_candidate_pools": True,
        },

        "semantic_model": {
            "name": MODEL_NAME,
            "device": DEVICE,
            "embedding_dimension": int(
                embedding_dimension
            ),
            "normalized_embeddings": True,
            "similarity": (
                "cosine via normalized embedding dot product"
            ),
            "batch_size": BATCH_SIZE,
        },

        "overall": overall_metrics,

        "train_failure_subset": train_metrics,

        "eval_failure_subset": eval_metrics,

        "eval_minus_train": eval_minus_train,

        "recovery_of_tfidf_top20_failures": {
            "counts": recovery,
            "rates": recovery_rates,
        },

        "rank_movement": rank_movement_summary,

        "controls": {
            "raw_mozilla_dataset_read": False,
            "accepted_dtm_artifact_read": False,
            "new_candidate_pool": False,
            "target_modified": False,
            "binary_classification": False,
            "threshold_optimization": False,
            "probability_calibration": False,
            "full_candidate_layer_embedded": False,
            "full_dataset_embedded": False,
        },

        "interpretation_notes": [
            (
                "This is a bounded semantic retrieval experiment "
                "restricted to the 173 MOD-005 Top-20 TF-IDF failures."
            ),
            (
                "The candidate pools are exactly the already-frozen "
                "101-candidate pools from T6 modeling splits."
            ),
            (
                "The observed Dupe-of target determines positive rank "
                "only; observable non-positive candidates are not "
                "treated as true-negative labels."
            ),
            (
                "Semantic similarity scores are retrieval scores, "
                "not probabilities or calibrated confidence."
            ),
            (
                "Recovery metrics describe whether semantic retrieval "
                "can recover lexical-baseline failures; they do not "
                "establish whole-population superiority."
            ),
            (
                "No final T6 model is selected by this operation."
            ),
        ],

        "artifacts": {
            "rankings": str(
                RANKINGS_PATH
            ),
            "results": str(
                RESULTS_PATH
            ),
        },

        "runtime_seconds": float(
            time.time()
            - overall_start
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
    # Console report
    # ------------------------------------------------------------------------

    log("")
    log("=" * 80)
    log("T6 MOD-008 — SEMANTIC FAILURE-RECOVERY SUMMARY")
    log("=" * 80)

    log("")
    log("Overall failure population:")
    log(
        f"  Queries: "
        f"{overall_metrics['queries']:,}"
    )

    log(
        f"  Semantic Recall@1: "
        f"{overall_metrics['recall_at_1']:.6f}"
    )

    log(
        f"  Semantic Recall@3: "
        f"{overall_metrics['recall_at_3']:.6f}"
    )

    log(
        f"  Semantic Recall@5: "
        f"{overall_metrics['recall_at_5']:.6f}"
    )

    log(
        f"  Semantic Recall@10: "
        f"{overall_metrics['recall_at_10']:.6f}"
    )

    log(
        f"  Semantic Recall@20: "
        f"{overall_metrics['recall_at_20']:.6f}"
    )

    log(
        f"  Semantic MRR: "
        f"{overall_metrics['mrr']:.6f}"
    )

    log("")
    log("Recovery of TF-IDF Top-20 failures:")

    log(
        f"  Recovered Top-1: "
        f"{recovery['top1']:,} "
        f"({recovery_rates['top1']:.2%})"
    )

    log(
        f"  Recovered Top-5: "
        f"{recovery['top5']:,} "
        f"({recovery_rates['top5']:.2%})"
    )

    log(
        f"  Recovered Top-10: "
        f"{recovery['top10']:,} "
        f"({recovery_rates['top10']:.2%})"
    )

    log(
        f"  Recovered Top-20: "
        f"{recovery['top20']:,} "
        f"({recovery_rates['top20']:.2%})"
    )

    log("")
    log("Rank movement:")
    log(
        f"  Mean TF-IDF rank - semantic rank: "
        f"{rank_movement_summary['mean_tfidf_rank_minus_semantic_rank']:.2f}"
    )

    log(
        f"  Median rank movement: "
        f"{rank_movement_summary['median_tfidf_rank_minus_semantic_rank']:.1f}"
    )

    log(
        f"  Semantic improved: "
        f"{rank_movement_summary['semantic_rank_improved_count']:,}"
    )

    log(
        f"  Semantic worsened: "
        f"{rank_movement_summary['semantic_rank_worsened_count']:,}"
    )

    log(
        f"  Semantic unchanged: "
        f"{rank_movement_summary['semantic_rank_unchanged_count']:,}"
    )

    log("")
    log("TRAIN failure subset:")
    log(
        f"  Recall@20: "
        f"{train_metrics['recall_at_20']:.6f}"
    )

    log(
        f"  MRR: "
        f"{train_metrics['mrr']:.6f}"
    )

    log("")
    log("EVAL failure subset:")
    log(
        f"  Recall@20: "
        f"{eval_metrics['recall_at_20']:.6f}"
    )

    log(
        f"  MRR: "
        f"{eval_metrics['mrr']:.6f}"
    )

    log("")
    log("Artifacts:")
    log(
        f"  {RANKINGS_PATH}"
    )
    log(
        f"  {RESULTS_PATH}"
    )

    log("")
    log(
        f"Runtime: "
        f"{time.time() - overall_start:.2f} seconds"
    )

    log("")
    log(
        "T6 MOD-008: "
        "BOUNDED_SEMANTIC_EXPERIMENT_COMPLETED"
    )

    LOG_PATH.write_text(
        "\n".join(log_lines) + "\n",
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(
            main()
        )
    except Exception as exc:
        print("")
        print("=" * 80)
        print("T6 MOD-008 FAILED")
        print("=" * 80)
        print(
            f"{type(exc).__name__}: {exc}"
        )
        raise