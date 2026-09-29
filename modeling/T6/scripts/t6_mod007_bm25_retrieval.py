#!/usr/bin/env python3

"""
T6 — MOD-007
BM25 Alternative Retrieval Baseline

Purpose:
    Evaluate a classical BM25 retrieval/ranking baseline against the
    already-frozen T6 query-candidate pools.

Inputs:
    modeling/T6/splits/t6_train_group_aware.csv
    modeling/T6/splits/t6_eval_group_aware.csv

Each query has exactly 101 candidates:
    - exactly 1 observed positive target
    - 100 observable non-positive candidates

BM25 is used strictly as a ranking function.

Important:
    observable_non_positive candidates are NOT treated as true negatives.

No:
    - new candidate construction
    - target modification
    - binary classification
    - probability calibration
    - threshold optimization
    - neural model
    - raw Mozilla CORE dataset access

This version explicitly normalizes the existing target_observed field
instead of assuming that it is stored as the literal string "1".
"""

from __future__ import annotations

import json
import math
import re
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd


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

OUTPUT_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
)

RANKINGS_PATH = (
    OUTPUT_DIR
    / "t6_mod007_bm25_query_rankings.csv"
)

RESULTS_PATH = (
    OUTPUT_DIR
    / "t6_mod007_bm25_retrieval_results.json"
)

LOG_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "logs"
)

LOG_PATH = (
    LOG_DIR
    / "t6_mod007_bm25_retrieval.log"
)


# ============================================================================
# Frozen BM25 parameters
# ============================================================================

K1 = 1.2
B = 0.75

CANDIDATES_PER_QUERY = 101

K_VALUES = [
    1,
    3,
    5,
    10,
    20,
]


# ============================================================================
# Required schema
# ============================================================================

REQUIRED_COLUMNS = [
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


TOKEN_PATTERN = re.compile(
    r"[A-Za-z0-9_]+"
)


# ============================================================================
# Target normalization
# ============================================================================

def is_observed_positive(value: object) -> bool:
    """
    Normalize the existing target_observed representation.

    Accepted positive representations:
        True
        1
        1.0
        "1"
        "true"
        "True"

    Accepted negative representations:
        False
        0
        0.0
        "0"
        "false"
        "False"

    No labels are created or inferred here. This only normalizes the
    existing binary observation flag already present in the frozen
    modeling artifact.
    """

    if pd.isna(value):
        return False

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, np.integer)):
        return int(value) == 1

    if isinstance(value, (float, np.floating)):
        return math.isclose(
            float(value),
            1.0,
            abs_tol=1e-12,
        )

    normalized = str(value).strip().lower()

    if normalized in {
        "1",
        "1.0",
        "true",
    }:
        return True

    if normalized in {
        "0",
        "0.0",
        "false",
    }:
        return False

    raise ValueError(
        "Unexpected target_observed value: "
        f"{value!r}"
    )


# ============================================================================
# Text helpers
# ============================================================================

def safe_text(value: object) -> str:
    if pd.isna(value):
        return ""

    return str(value).strip()


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(
        text.lower()
    )


def build_query_text(row: pd.Series) -> str:
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
# BM25 implementation
# ============================================================================

class BM25:

    def __init__(
        self,
        documents: list[list[str]],
        k1: float = 1.2,
        b: float = 0.75,
    ) -> None:

        self.k1 = k1
        self.b = b

        self.documents = documents
        self.document_count = len(documents)

        if self.document_count == 0:
            raise ValueError(
                "BM25 received zero documents."
            )

        self.document_lengths = np.array(
            [
                len(document)
                for document in documents
            ],
            dtype=np.float64,
        )

        self.average_document_length = float(
            self.document_lengths.mean()
        )

        self.term_frequencies: list[Counter[str]] = []

        document_frequency: Counter[str] = Counter()

        for document in documents:

            frequencies = Counter(
                document
            )

            self.term_frequencies.append(
                frequencies
            )

            for term in frequencies:
                document_frequency[term] += 1

        self.document_frequency = document_frequency

        self.idf: dict[str, float] = {}

        for term, df in document_frequency.items():

            numerator = (
                self.document_count
                - df
                + 0.5
            )

            denominator = (
                df
                + 0.5
            )

            self.idf[term] = math.log(
                1.0
                + (
                    numerator
                    / denominator
                )
            )

    def score(
        self,
        query_tokens: list[str],
        document_index: int,
    ) -> float:

        if not query_tokens:
            return 0.0

        frequencies = self.term_frequencies[
            document_index
        ]

        document_length = float(
            self.document_lengths[
                document_index
            ]
        )

        if self.average_document_length == 0:
            return 0.0

        score = 0.0

        for term in set(query_tokens):

            if term not in frequencies:
                continue

            term_frequency = frequencies[
                term
            ]

            idf = self.idf.get(
                term,
                0.0,
            )

            denominator = (
                term_frequency
                + self.k1
                * (
                    1.0
                    - self.b
                    + self.b
                    * (
                        document_length
                        / self.average_document_length
                    )
                )
            )

            score += (
                idf
                * (
                    term_frequency
                    * (self.k1 + 1.0)
                    / denominator
                )
            )

        return float(score)

    def score_all(
        self,
        query_tokens: list[str],
    ) -> np.ndarray:

        return np.array(
            [
                self.score(
                    query_tokens,
                    index,
                )
                for index in range(
                    self.document_count
                )
            ],
            dtype=np.float64,
        )


# ============================================================================
# Validation
# ============================================================================

def validate_split(
    df: pd.DataFrame,
    split_name: str,
) -> None:

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"{split_name} missing required columns: "
            + ", ".join(missing)
        )

    query_counts = (
        df.groupby("query_id")
        .size()
    )

    invalid_query_counts = query_counts[
        query_counts != CANDIDATES_PER_QUERY
    ]

    if not invalid_query_counts.empty:
        raise ValueError(
            f"{split_name}: queries without exactly "
            f"{CANDIDATES_PER_QUERY} candidates: "
            f"{len(invalid_query_counts)}"
        )

    duplicate_pairs = df.duplicated(
        subset=[
            "query_id",
            "candidate_id",
        ]
    )

    if duplicate_pairs.any():
        raise ValueError(
            f"{split_name}: duplicate query-candidate pairs: "
            f"{int(duplicate_pairs.sum())}"
        )

    positive_mask = (
        df["target_observed"]
        .map(is_observed_positive)
    )

    positive_counts = (
        pd.DataFrame(
            {
                "query_id": df["query_id"],
                "positive": positive_mask,
            }
        )
        .groupby("query_id")["positive"]
        .sum()
    )

    invalid_positive_counts = positive_counts[
        positive_counts != 1
    ]

    if not invalid_positive_counts.empty:
        raise ValueError(
            f"{split_name}: queries without exactly one "
            f"observed positive: "
            f"{len(invalid_positive_counts)}"
        )


# ============================================================================
# Ranking
# ============================================================================

def evaluate_split(
    df: pd.DataFrame,
    split_name: str,
    log,
) -> tuple[list[dict], dict]:

    query_rankings: list[dict] = []

    grouped = df.groupby(
        "query_id",
        sort=False,
    )

    query_total = len(grouped)

    start_time = time.time()

    for query_index, (
        query_id,
        group,
    ) in enumerate(
        grouped,
        start=1,
    ):

        group = group.reset_index(
            drop=True
        )

        query_row = group.iloc[0]

        query_text = build_query_text(
            query_row
        )

        query_tokens = tokenize(
            query_text
        )

        candidate_texts = [
            build_candidate_text(row)
            for _, row in group.iterrows()
        ]

        candidate_tokens = [
            tokenize(text)
            for text in candidate_texts
        ]

        bm25 = BM25(
            candidate_tokens,
            k1=K1,
            b=B,
        )

        scores = bm25.score_all(
            query_tokens
        )

        positive_mask = (
            group["target_observed"]
            .map(is_observed_positive)
            .to_numpy()
        )

        positive_indices = np.flatnonzero(
            positive_mask
        )

        if len(positive_indices) != 1:
            raise ValueError(
                f"Query {query_id} does not have "
                "exactly one observed positive."
            )

        positive_index = int(
            positive_indices[0]
        )

        candidate_ids = (
            group["candidate_id"]
            .astype(str)
            .to_numpy()
        )

        # Deterministic ranking:
        #   1. descending BM25 score
        #   2. candidate ID ascending for exact-score ties
        ordering = sorted(
            range(len(scores)),
            key=lambda index: (
                -float(scores[index]),
                candidate_ids[index],
            ),
        )

        positive_rank = (
            ordering.index(
                positive_index
            )
            + 1
        )

        top_index = ordering[0]

        top_score = float(
            scores[top_index]
        )

        positive_score = float(
            scores[positive_index]
        )

        query_rankings.append(
            {
                "split": split_name,
                "query_id": str(query_id),
                "query_creation_time": str(
                    query_row[
                        "query_creation_time"
                    ]
                ),
                "positive_candidate_id": str(
                    group.iloc[
                        positive_index
                    ][
                        "candidate_id"
                    ]
                ),
                "positive_rank": int(
                    positive_rank
                ),
                "top_candidate_id": str(
                    group.iloc[
                        top_index
                    ][
                        "candidate_id"
                    ]
                ),
                "top_candidate_role": str(
                    group.iloc[
                        top_index
                    ][
                        "candidate_role"
                    ]
                ),
                "top_score": top_score,
                "positive_score": positive_score,
                "score_gap_top1_minus_positive": (
                    top_score
                    - positive_score
                ),
                "query_token_count": int(
                    len(query_tokens)
                ),
            }
        )

        if (
            query_index == 1
            or query_index % 250 == 0
            or query_index == query_total
        ):

            elapsed = (
                time.time()
                - start_time
            )

            log(
                f"  {split_name}: "
                f"{query_index:,}/{query_total:,} "
                f"queries processed "
                f"({elapsed:.1f}s)"
            )

    ranking_df = pd.DataFrame(
        query_rankings
    )

    ranks = (
        ranking_df["positive_rank"]
        .astype(int)
    )

    metrics = {
        "queries": int(
            len(ranking_df)
        ),

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
            "minimum": int(
                ranks.min()
            ),
            "median": float(
                ranks.median()
            ),
            "mean": float(
                ranks.mean()
            ),
            "maximum": int(
                ranks.max()
            ),
        },
    }

    return (
        query_rankings,
        metrics,
    )


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
    log("T6 MOD-007 — BM25 ALTERNATIVE RETRIEVAL BASELINE")
    log("=" * 80)

    log("")
    log("Configuration:")
    log(f"  BM25 k1: {K1}")
    log(f"  BM25 b:  {B}")
    log(
        f"  Candidates/query: "
        f"{CANDIDATES_PER_QUERY}"
    )

    # ------------------------------------------------------------------------
    # Load frozen modeling splits
    # ------------------------------------------------------------------------

    log("")
    log("[1/6] Loading frozen T6 modeling splits...")

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

    log(
        f"TRAIN rows: {len(train):,}"
    )

    log(
        f"EVAL rows: {len(evaluation):,}"
    )

    # ------------------------------------------------------------------------
    # Target representation diagnostics
    # ------------------------------------------------------------------------

    log("")
    log("[2/6] Inspecting existing target_observed representation...")

    train_target_values = (
        train["target_observed"]
        .value_counts(dropna=False)
        .to_dict()
    )

    eval_target_values = (
        evaluation["target_observed"]
        .value_counts(dropna=False)
        .to_dict()
    )

    log(
        f"TRAIN target_observed values: "
        f"{train_target_values}"
    )

    log(
        f"EVAL target_observed values: "
        f"{eval_target_values}"
    )

    train_positive_count = int(
        train["target_observed"]
        .map(is_observed_positive)
        .sum()
    )

    eval_positive_count = int(
        evaluation["target_observed"]
        .map(is_observed_positive)
        .sum()
    )

    log(
        f"TRAIN observed-positive rows: "
        f"{train_positive_count:,}"
    )

    log(
        f"EVAL observed-positive rows: "
        f"{eval_positive_count:,}"
    )

    # ------------------------------------------------------------------------
    # Validate
    # ------------------------------------------------------------------------

    log("")
    log("[3/6] Validating frozen retrieval structure...")

    validate_split(
        train,
        "TRAIN",
    )

    validate_split(
        evaluation,
        "EVAL",
    )

    train_queries = (
        train["query_id"]
        .nunique()
    )

    eval_queries = (
        evaluation["query_id"]
        .nunique()
    )

    log(
        f"TRAIN queries: {train_queries:,}"
    )

    log(
        f"EVAL queries: {eval_queries:,}"
    )

    log(
        "101 candidates/query: VALID"
    )

    log(
        "Exactly one observed positive/query: VALID"
    )

    log(
        "No duplicate query-candidate pairs: VALID"
    )

    # ------------------------------------------------------------------------
    # TRAIN retrieval
    # ------------------------------------------------------------------------

    log("")
    log("[4/6] Running BM25 retrieval on TRAIN...")

    train_rankings, train_metrics = (
        evaluate_split(
            train,
            "train",
            log,
        )
    )

    log("")
    log("TRAIN complete.")

    # ------------------------------------------------------------------------
    # EVAL retrieval
    # ------------------------------------------------------------------------

    log("")
    log("[5/6] Running BM25 retrieval on EVAL...")

    eval_rankings, eval_metrics = (
        evaluate_split(
            evaluation,
            "eval",
            log,
        )
    )

    log("")
    log("EVAL complete.")

    # ------------------------------------------------------------------------
    # Save outputs
    # ------------------------------------------------------------------------

    log("")
    log("[6/6] Saving BM25 results...")

    all_rankings = pd.DataFrame(
        train_rankings
        + eval_rankings
    )

    all_rankings.to_csv(
        RANKINGS_PATH,
        index=False,
    )

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

    train_eval_deltas = {}

    for key in metric_keys:
        train_eval_deltas[
            f"{key}_eval_minus_train"
        ] = float(
            eval_metrics[key]
            - train_metrics[key]
        )

    results = {
        "operation": "T6 MOD-007",

        "task": (
            "T6 Similar-Ticket Retrieval"
        ),

        "task_formulation": (
            "Duplicate-Related Ticket Retrieval"
        ),

        "status": (
            "BASELINE_COMPLETED"
        ),

        "method": {
            "name": "BM25",
            "k1": K1,
            "b": B,
            "ranking_only": True,
            "probability_output": False,
            "calibration": False,
        },

        "candidate_pool": {
            "candidates_per_query": (
                CANDIDATES_PER_QUERY
            ),
            "same_as_mod004": True,
            "candidate_pool_reconstructed": False,
        },

        "target_handling": {
            "one_observed_positive_per_query": True,
            "observable_non_positive_is_true_negative": False,
            "binary_classification": False,
            "target_representation_normalized": True,
        },

        "controls": {
            "raw_mozilla_dataset_read": False,
            "accepted_dtm_artifact_read": False,
            "candidate_pool_modified": False,
            "target_modified": False,
            "model_retrained": False,
            "tfidf_refit": False,
            "calibration": False,
            "threshold_optimization": False,
        },

        "train": train_metrics,

        "eval": eval_metrics,

        "train_eval_deltas": train_eval_deltas,

        "artifacts": {
            "query_rankings": str(
                RANKINGS_PATH
            ),
            "results": str(
                RESULTS_PATH
            ),
        },

        "interpretation_notes": [
            (
                "BM25 is evaluated as a ranking baseline on the "
                "same frozen 101-candidate query pools used by MOD-004."
            ),
            (
                "The existing target_observed field is normalized "
                "only for recognizing the already-defined observed "
                "positive candidate."
            ),
            (
                "No new labels are created by this normalization."
            ),
            (
                "Observable non-positive candidates are not treated "
                "as true-negative labels."
            ),
            (
                "BM25 scores are retrieval scores and are not "
                "interpreted as probabilities or calibrated confidence."
            ),
            (
                "This operation is a baseline comparison and does not "
                "select a final T6 model."
            ),
        ],
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
    log("T6 MOD-007 — BM25 RESULTS")
    log("=" * 80)

    log("")
    log("TRAIN:")

    for key in metric_keys:
        log(
            f"  {key}: "
            f"{train_metrics[key]:.6f}"
        )

    log("")
    log("EVAL:")

    for key in metric_keys:
        log(
            f"  {key}: "
            f"{eval_metrics[key]:.6f}"
        )

    log("")
    log("EVAL - TRAIN:")

    for key in metric_keys:
        delta = train_eval_deltas[
            f"{key}_eval_minus_train"
        ]

        log(
            f"  {key}: "
            f"{delta:+.6f}"
        )

    log("")
    log("Positive rank:")

    log(
        f"  TRAIN median: "
        f"{train_metrics['positive_rank']['median']:.1f}"
    )

    log(
        f"  TRAIN mean: "
        f"{train_metrics['positive_rank']['mean']:.2f}"
    )

    log(
        f"  EVAL median: "
        f"{eval_metrics['positive_rank']['median']:.1f}"
    )

    log(
        f"  EVAL mean: "
        f"{eval_metrics['positive_rank']['mean']:.2f}"
    )

    log("")
    log("Artifacts:")
    log(
        f"  {RANKINGS_PATH}"
    )
    log(
        f"  {RESULTS_PATH}"
    )

    runtime = (
        time.time()
        - overall_start
    )

    log("")
    log(
        f"Runtime: {runtime:.2f} seconds"
    )

    log("")
    log(
        "T6 MOD-007: BASELINE_COMPLETED"
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
        print("T6 MOD-007 FAILED")
        print("=" * 80)
        print(
            f"{type(exc).__name__}: {exc}"
        )
        raise