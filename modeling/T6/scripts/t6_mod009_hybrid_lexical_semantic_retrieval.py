from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import load
from sentence_transformers import SentenceTransformer


# =============================================================================
# T6 MOD-009 — HYBRID LEXICAL + SEMANTIC RETRIEVAL
# =============================================================================

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

TFIDF_VECTOR_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "models"
    / "t6_mod004_tfidf_vectorizer.joblib"
)

TFIDF_RANKINGS_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod004_query_rankings.csv"
)

OUTPUT_RANKINGS = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod009_hybrid_query_rankings.csv"
)

OUTPUT_RESULTS = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod009_hybrid_retrieval_results.json"
)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

TEXT_FIELDS = [
    "query_creator",
    "query_creator_detail",
    "query_summary",
    "query_description",
]

CANDIDATE_TEXT_FIELDS = [
    "candidate_creator",
    "candidate_creator_detail",
    "candidate_summary",
    "candidate_description",
]

CANDIDATES_PER_QUERY = 101

# Predeclared semantic weights.
SEMANTIC_WEIGHTS = [0.10, 0.25, 0.50, 0.75, 0.90]

RANDOM_SEED = 42


# =============================================================================
# HELPERS
# =============================================================================

def normalize_target_observed(series: pd.Series) -> pd.Series:
    """
    Normalize the already-existing target_observed representation.

    No labels are created or modified.
    """
    values = []

    for value in series:
        if isinstance(value, (bool, np.bool_)):
            values.append(bool(value))
        elif isinstance(value, (int, np.integer)):
            if int(value) in (0, 1):
                values.append(bool(int(value)))
            else:
                raise ValueError(
                    f"Unexpected integer target_observed value: {value}"
                )
        elif isinstance(value, (float, np.floating)):
            if float(value) in (0.0, 1.0):
                values.append(bool(int(value)))
            else:
                raise ValueError(
                    f"Unexpected float target_observed value: {value}"
                )
        elif isinstance(value, str):
            lowered = value.strip().lower()

            if lowered in {"true", "1"}:
                values.append(True)
            elif lowered in {"false", "0"}:
                values.append(False)
            else:
                raise ValueError(
                    f"Unexpected string target_observed value: {value!r}"
                )
        else:
            raise ValueError(
                f"Unexpected target_observed type/value: {value!r}"
            )

    return pd.Series(values, index=series.index, dtype=bool)


def validate_split(df: pd.DataFrame, split_name: str) -> None:
    required = [
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
    ]

    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(
            f"{split_name}: missing required columns: {missing}"
        )

    df["target_observed"] = normalize_target_observed(
        df["target_observed"]
    )

    counts = df.groupby("query_id").size()

    if not bool((counts == CANDIDATES_PER_QUERY).all()):
        bad = counts[counts != CANDIDATES_PER_QUERY]
        raise ValueError(
            f"{split_name}: invalid candidate count for queries:\n{bad.head()}"
        )

    positives = df.groupby("query_id")["target_observed"].sum()

    if not bool((positives == 1).all()):
        bad = positives[positives != 1]
        raise ValueError(
            f"{split_name}: queries without exactly one observed positive:\n"
            f"{bad.head()}"
        )

    if df.duplicated(
        subset=["query_id", "candidate_id"]
    ).any():
        raise ValueError(
            f"{split_name}: duplicate query-candidate pairs detected."
        )

    if (df["query_id"] == df["candidate_id"]).any():
        raise ValueError(
            f"{split_name}: self-candidate rows detected."
        )


def clean_text(value) -> str:
    if pd.isna(value):
        return ""

    return str(value).strip()


def build_text(
    df: pd.DataFrame,
    fields: list[str],
) -> pd.Series:
    return (
        df[fields]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )


def rank_metrics(
    rankings: pd.DataFrame,
    score_column: str,
) -> dict:
    """
    Compute query-level ranking metrics for exactly one positive/query.
    """

    recall_values = {1: [], 3: [], 5: [], 10: [], 20: []}
    reciprocal_ranks = []
    ndcg5 = []
    ndcg10 = []

    for query_id, group in rankings.groupby("query_id", sort=False):
        ordered = group.sort_values(
            [score_column, "candidate_id"],
            ascending=[False, True],
            kind="mergesort",
        )

        positive_positions = np.flatnonzero(
            ordered["target_observed"].to_numpy(dtype=bool)
        )

        if len(positive_positions) != 1:
            raise ValueError(
                f"Query {query_id} does not have exactly one positive."
            )

        rank = int(positive_positions[0]) + 1

        for k in recall_values:
            recall_values[k].append(1.0 if rank <= k else 0.0)

        reciprocal_ranks.append(1.0 / rank)

        if rank <= 5:
            ndcg5.append(1.0 / math.log2(rank + 1))
        else:
            ndcg5.append(0.0)

        if rank <= 10:
            ndcg10.append(1.0 / math.log2(rank + 1))
        else:
            ndcg10.append(0.0)

    return {
        "recall_at_1": float(np.mean(recall_values[1])),
        "recall_at_3": float(np.mean(recall_values[3])),
        "recall_at_5": float(np.mean(recall_values[5])),
        "recall_at_10": float(np.mean(recall_values[10])),
        "recall_at_20": float(np.mean(recall_values[20])),
        "mrr": float(np.mean(reciprocal_ranks)),
        "ndcg_at_5": float(np.mean(ndcg5)),
        "ndcg_at_10": float(np.mean(ndcg10)),
    }


def get_positive_ranks(
    rankings: pd.DataFrame,
    score_column: str,
) -> pd.DataFrame:

    records = []

    for query_id, group in rankings.groupby("query_id", sort=False):

        ordered = group.sort_values(
            [score_column, "candidate_id"],
            ascending=[False, True],
            kind="mergesort",
        ).reset_index(drop=True)

        positive_positions = np.flatnonzero(
            ordered["target_observed"].to_numpy(dtype=bool)
        )

        if len(positive_positions) != 1:
            raise ValueError(
                f"Query {query_id} does not have exactly one positive."
            )

        positive_index = int(positive_positions[0])

        records.append(
            {
                "query_id": query_id,
                "positive_rank": positive_index + 1,
                "positive_score": float(
                    ordered.loc[positive_index, score_column]
                ),
            }
        )

    return pd.DataFrame(records)


def minmax_normalize_within_query(
    rankings: pd.DataFrame,
    score_column: str,
    output_column: str,
) -> pd.DataFrame:
    """
    Normalize scores within each query.

    This avoids assuming that TF-IDF and semantic cosine values have
    directly comparable numerical scales.
    """

    output = rankings.copy()

    normalized_parts = []

    for _, group in output.groupby("query_id", sort=False):

        scores = group[score_column].to_numpy(dtype=np.float64)

        minimum = float(np.min(scores))
        maximum = float(np.max(scores))

        if maximum > minimum:
            normalized = (scores - minimum) / (maximum - minimum)
        else:
            normalized = np.zeros_like(scores)

        normalized_parts.append(
            pd.Series(
                normalized,
                index=group.index,
                dtype=np.float64,
            )
        )

    normalized_series = pd.concat(normalized_parts).sort_index()

    output[output_column] = normalized_series

    return output


def evaluate_weight(
    rankings: pd.DataFrame,
    semantic_weight: float,
) -> dict:

    lexical_weight = 1.0 - semantic_weight

    rankings = rankings.copy()

    rankings["hybrid_score"] = (
        lexical_weight * rankings["tfidf_score_normalized"]
        + semantic_weight * rankings["semantic_score_normalized"]
    )

    metrics = rank_metrics(
        rankings,
        "hybrid_score",
    )

    metrics["semantic_weight"] = semantic_weight
    metrics["lexical_weight"] = lexical_weight

    return metrics


def choose_training_weight(results: list[dict]) -> dict:
    """
    Primary criterion:
      Recall@20

    Secondary criterion:
      MRR

    Tertiary criterion:
      Recall@10

    Final deterministic tie-break:
      lower semantic weight.
    """

    ordered = sorted(
        results,
        key=lambda item: (
            -item["recall_at_20"],
            -item["mrr"],
            -item["recall_at_10"],
            item["semantic_weight"],
        ),
    )

    return ordered[0]


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:

    start_time = time.time()

    print("=" * 80)
    print("T6 MOD-009 — HYBRID LEXICAL + SEMANTIC RETRIEVAL")
    print("=" * 80)
    print()
    print("Purpose:")
    print("  Test complementary lexical + semantic ranking on the full")
    print("  frozen T6 query-candidate population.")
    print()
    print(f"Semantic model: {MODEL_NAME}")
    print("Device: cpu")
    print()
    print("Frozen candidate pool:")
    print("  101 candidates/query")
    print("  Same T6 train/eval splits")
    print("  Exactly one observed positive/query")
    print()
    print("Predeclared semantic weights:")
    print(f"  {SEMANTIC_WEIGHTS}")
    print()

    # -------------------------------------------------------------------------
    # 1. Load frozen splits
    # -------------------------------------------------------------------------

    print("[1/9] Loading frozen T6 modeling splits...")

    train = pd.read_csv(TRAIN_PATH)
    evaluation = pd.read_csv(EVAL_PATH)

    validate_split(train, "TRAIN")
    validate_split(evaluation, "EVAL")

    print(f"TRAIN rows: {len(train):,}")
    print(f"EVAL rows: {len(evaluation):,}")
    print(
        f"TRAIN queries: {train['query_id'].nunique():,}"
    )
    print(
        f"EVAL queries: {evaluation['query_id'].nunique():,}"
    )
    print()

    # -------------------------------------------------------------------------
    # 2. Load TF-IDF vectorizer
    # -------------------------------------------------------------------------

    print("[2/9] Loading MOD-004 TF-IDF vectorizer...")

    tfidf_vectorizer = load(TFIDF_VECTOR_PATH)

    print(
        f"TF-IDF vocabulary size: "
        f"{len(tfidf_vectorizer.vocabulary_):,}"
    )
    print()

    # -------------------------------------------------------------------------
    # 3. Reconstruct exact query/candidate lexical scores
    # -------------------------------------------------------------------------

    print("[3/9] Reconstructing frozen TF-IDF similarity scores...")

    combined = pd.concat(
        [
            train.assign(_split="TRAIN"),
            evaluation.assign(_split="EVAL"),
        ],
        ignore_index=True,
    )

    query_rows = (
        combined[
            [
                "query_id",
                "query_creator",
                "query_creator_detail",
                "query_summary",
                "query_description",
            ]
        ]
        .drop_duplicates(subset=["query_id"])
        .copy()
    )

    query_rows["query_text"] = build_text(
        query_rows,
        TEXT_FIELDS,
    )

    candidate_rows = (
        combined[
            [
                "candidate_id",
                "candidate_creator",
                "candidate_creator_detail",
                "candidate_summary",
                "candidate_description",
            ]
        ]
        .drop_duplicates(subset=["candidate_id"])
        .copy()
    )

    candidate_rows["candidate_text"] = build_text(
        candidate_rows,
        CANDIDATE_TEXT_FIELDS,
    )

    print(
        f"Unique queries: {len(query_rows):,}"
    )
    print(
        f"Unique candidates: {len(candidate_rows):,}"
    )

    query_matrix = tfidf_vectorizer.transform(
        query_rows["query_text"]
    )

    candidate_matrix = tfidf_vectorizer.transform(
        candidate_rows["candidate_text"]
    )

    query_id_to_row = {
        value: index
        for index, value in enumerate(query_rows["query_id"])
    }

    candidate_id_to_row = {
        value: index
        for index, value in enumerate(candidate_rows["candidate_id"])
    }

    print(
        f"Query TF-IDF matrix: "
        f"{query_matrix.shape[0]:,} x {query_matrix.shape[1]:,}"
    )

    print(
        f"Candidate TF-IDF matrix: "
        f"{candidate_matrix.shape[0]:,} x {candidate_matrix.shape[1]:,}"
    )

    # -------------------------------------------------------------------------
    # 4. Load semantic model
    # -------------------------------------------------------------------------

    print()
    print("[4/9] Loading semantic embedding model...")

    semantic_model = SentenceTransformer(
        MODEL_NAME,
        device="cpu",
    )

    print(
        "Embedding dimension: "
        f"{semantic_model.get_sentence_embedding_dimension()}"
    )
    print()

    # -------------------------------------------------------------------------
    # 5. Encode unique query/candidate documents
    # -------------------------------------------------------------------------

    print("[5/9] Encoding unique query and candidate documents...")

    query_embeddings = semantic_model.encode(
        query_rows["query_text"].tolist(),
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    candidate_embeddings = semantic_model.encode(
        candidate_rows["candidate_text"].tolist(),
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    query_embeddings = np.asarray(
        query_embeddings,
        dtype=np.float32,
    )

    candidate_embeddings = np.asarray(
        candidate_embeddings,
        dtype=np.float32,
    )

    print(
        f"Query embeddings: {query_embeddings.shape}"
    )
    print(
        f"Candidate embeddings: {candidate_embeddings.shape}"
    )
    print()

    # -------------------------------------------------------------------------
    # 6. Reconstruct row-level lexical + semantic scores
    # -------------------------------------------------------------------------

    print("[6/9] Computing frozen lexical and semantic scores...")

    records = []

    for split_name, split_df in [
        ("TRAIN", train),
        ("EVAL", evaluation),
    ]:

        for row in split_df.itertuples(index=False):

            query_id = row.query_id
            candidate_id = row.candidate_id

            q_index = query_id_to_row[query_id]
            c_index = candidate_id_to_row[candidate_id]

            # TF-IDF cosine.
            lexical_score = float(
                query_matrix[q_index].dot(
                    candidate_matrix[c_index].T
                ).toarray()[0, 0]
            )

            # Semantic cosine because embeddings are normalized.
            semantic_score = float(
                np.dot(
                    query_embeddings[q_index],
                    candidate_embeddings[c_index],
                )
            )

            records.append(
                {
                    "split": split_name,
                    "query_id": query_id,
                    "candidate_id": candidate_id,
                    "target_observed": bool(
                        row.target_observed
                    ),
                    "tfidf_score": lexical_score,
                    "semantic_score": semantic_score,
                }
            )

    rankings = pd.DataFrame(records)

    print(
        f"Scored query-candidate rows: {len(rankings):,}"
    )

    # -------------------------------------------------------------------------
    # 7. Normalize scores within query
    # -------------------------------------------------------------------------

    print("[7/9] Normalizing lexical and semantic scores within query...")

    rankings = minmax_normalize_within_query(
        rankings,
        "tfidf_score",
        "tfidf_score_normalized",
    )

    rankings = minmax_normalize_within_query(
        rankings,
        "semantic_score",
        "semantic_score_normalized",
    )

    # -------------------------------------------------------------------------
    # 8. Training-only hybrid weight selection
    # -------------------------------------------------------------------------

    print("[8/9] Selecting hybrid weight using TRAIN only...")

    train_rankings = rankings[
        rankings["split"] == "TRAIN"
    ].copy()

    train_weight_results = []

    for semantic_weight in SEMANTIC_WEIGHTS:

        result = evaluate_weight(
            train_rankings,
            semantic_weight,
        )

        train_weight_results.append(result)

        print(
            f"  semantic={semantic_weight:.2f} "
            f"lexical={1.0 - semantic_weight:.2f} "
            f"R@20={result['recall_at_20']:.6f} "
            f"MRR={result['mrr']:.6f}"
        )

    selected_weight = choose_training_weight(
        train_weight_results
    )

    semantic_weight = selected_weight["semantic_weight"]
    lexical_weight = selected_weight["lexical_weight"]

    print()
    print("SELECTED TRAINING WEIGHT:")
    print(
        f"  semantic_weight: {semantic_weight:.2f}"
    )
    print(
        f"  lexical_weight: {lexical_weight:.2f}"
    )
    print(
        "  Selection criteria: "
        "Recall@20 → MRR → Recall@10"
    )
    print()

    # -------------------------------------------------------------------------
    # 9. Final frozen evaluation
    # -------------------------------------------------------------------------

    print("[9/9] Applying selected hybrid weight to TRAIN and EVAL...")

    rankings["hybrid_score"] = (
        lexical_weight * rankings["tfidf_score_normalized"]
        + semantic_weight * rankings["semantic_score_normalized"]
    )

    train_final = rankings[
        rankings["split"] == "TRAIN"
    ].copy()

    eval_final = rankings[
        rankings["split"] == "EVAL"
    ].copy()

    # Baseline TF-IDF and hybrid metrics.
    train_tfidf_metrics = rank_metrics(
        train_final,
        "tfidf_score",
    )

    eval_tfidf_metrics = rank_metrics(
        eval_final,
        "tfidf_score",
    )

    train_hybrid_metrics = rank_metrics(
        train_final,
        "hybrid_score",
    )

    eval_hybrid_metrics = rank_metrics(
        eval_final,
        "hybrid_score",
    )

    # Semantic-only diagnostic on full population.
    train_semantic_metrics = rank_metrics(
        train_final,
        "semantic_score",
    )

    eval_semantic_metrics = rank_metrics(
        eval_final,
        "semantic_score",
    )

    # -------------------------------------------------------------------------
    # Rank movement
    # -------------------------------------------------------------------------

    train_tfidf_ranks = get_positive_ranks(
        train_final,
        "tfidf_score",
    ).rename(
        columns={
            "positive_rank": "tfidf_positive_rank",
        }
    )

    train_hybrid_ranks = get_positive_ranks(
        train_final,
        "hybrid_score",
    ).rename(
        columns={
            "positive_rank": "hybrid_positive_rank",
        }
    )

    eval_tfidf_ranks = get_positive_ranks(
        eval_final,
        "tfidf_score",
    ).rename(
        columns={
            "positive_rank": "tfidf_positive_rank",
        }
    )

    eval_hybrid_ranks = get_positive_ranks(
        eval_final,
        "hybrid_score",
    ).rename(
        columns={
            "positive_rank": "hybrid_positive_rank",
        }
    )

    train_movement = train_tfidf_ranks[
        ["query_id", "tfidf_positive_rank"]
    ].merge(
        train_hybrid_ranks[
            ["query_id", "hybrid_positive_rank"]
        ],
        on="query_id",
        how="inner",
    )

    eval_movement = eval_tfidf_ranks[
        ["query_id", "tfidf_positive_rank"]
    ].merge(
        eval_hybrid_ranks[
            ["query_id", "hybrid_positive_rank"]
        ],
        on="query_id",
        how="inner",
    )

    def movement_summary(df: pd.DataFrame) -> dict:

        movement = (
            df["tfidf_positive_rank"]
            - df["hybrid_positive_rank"]
        )

        return {
            "mean_rank_movement": float(movement.mean()),
            "median_rank_movement": float(movement.median()),
            "improved": int((movement > 0).sum()),
            "worsened": int((movement < 0).sum()),
            "unchanged": int((movement == 0).sum()),
        }

    train_movement_summary = movement_summary(
        train_movement
    )

    eval_movement_summary = movement_summary(
        eval_movement
    )

    # -------------------------------------------------------------------------
    # TF-IDF Top-20 recovery
    # -------------------------------------------------------------------------

    tfidf_failure_query_ids = set()

    for query_id, group in rankings.groupby(
        "query_id",
        sort=False,
    ):

        ordered = group.sort_values(
            ["tfidf_score", "candidate_id"],
            ascending=[False, True],
            kind="mergesort",
        )

        positive_positions = np.flatnonzero(
            ordered["target_observed"].to_numpy(dtype=bool)
        )

        if len(positive_positions) != 1:
            raise ValueError(
                f"Query {query_id} does not have exactly one positive."
            )

        if int(positive_positions[0]) + 1 > 20:
            tfidf_failure_query_ids.add(query_id)

    failure_rows = rankings[
        rankings["query_id"].isin(tfidf_failure_query_ids)
    ].copy()

    failure_metrics = rank_metrics(
        failure_rows,
        "hybrid_score",
    )

    # -------------------------------------------------------------------------
    # Save detailed rankings
    # -------------------------------------------------------------------------

    rankings[
        [
            "split",
            "query_id",
            "candidate_id",
            "target_observed",
            "tfidf_score",
            "semantic_score",
            "tfidf_score_normalized",
            "semantic_score_normalized",
            "hybrid_score",
        ]
    ].to_csv(
        OUTPUT_RANKINGS,
        index=False,
    )

    # -------------------------------------------------------------------------
    # Save result JSON
    # -------------------------------------------------------------------------

    results = {
        "task_id": "T6",
        "operation_id": "MOD-009",
        "operation_name": "Hybrid Lexical + Semantic Retrieval",
        "status": "COMPLETED",
        "semantic_model": MODEL_NAME,
        "device": "cpu",
        "embedding_dimension": int(
            semantic_model.get_sentence_embedding_dimension()
        ),
        "candidate_pool": {
            "candidates_per_query": CANDIDATES_PER_QUERY,
            "same_frozen_train_eval_splits": True,
            "candidate_pool_modified": False,
        },
        "query_features": [
            "Creator",
            "Creator Detail",
            "Summary",
            "Description",
        ],
        "candidate_features": [
            "Creator",
            "Creator Detail",
            "Summary",
            "Description",
        ],
        "target_policy": {
            "observable_non_positive_is_true_negative": False,
            "binary_classification": False,
            "target_modified": False,
        },
        "population": {
            "total_queries": int(
                rankings["query_id"].nunique()
            ),
            "total_rows": int(len(rankings)),
            "train_queries": int(
                train["query_id"].nunique()
            ),
            "eval_queries": int(
                evaluation["query_id"].nunique()
            ),
            "train_rows": int(len(train)),
            "eval_rows": int(len(evaluation)),
        },
        "predeclared_semantic_weights": SEMANTIC_WEIGHTS,
        "training_weight_selection": {
            "selection_split": "TRAIN",
            "primary_criterion": "recall_at_20",
            "secondary_criterion": "mrr",
            "tertiary_criterion": "recall_at_10",
            "candidate_results": train_weight_results,
            "selected": selected_weight,
        },
        "metrics": {
            "train": {
                "tfidf": train_tfidf_metrics,
                "semantic": train_semantic_metrics,
                "hybrid": train_hybrid_metrics,
            },
            "eval": {
                "tfidf": eval_tfidf_metrics,
                "semantic": eval_semantic_metrics,
                "hybrid": eval_hybrid_metrics,
            },
        },
        "rank_movement": {
            "train": train_movement_summary,
            "eval": eval_movement_summary,
        },
        "tfidf_top20_failure_population": {
            "queries": int(
                len(tfidf_failure_query_ids)
            ),
            "hybrid_metrics": failure_metrics,
        },
        "controls": {
            "raw_dataset_read": False,
            "target_reconstruction": False,
            "target_modification": False,
            "candidate_pool_modification": False,
            "evaluation_weight_selection": False,
            "threshold_optimization": False,
            "calibration": False,
            "binary_classification": False,
        },
        "artifacts": {
            "rankings": str(OUTPUT_RANKINGS),
            "results": str(OUTPUT_RESULTS),
            "tfidf_vectorizer": str(TFIDF_VECTOR_PATH),
        },
        "runtime_seconds": None,
    }

    results["runtime_seconds"] = round(
        time.time() - start_time,
        2,
    )

    with OUTPUT_RESULTS.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            results,
            handle,
            indent=2,
        )

    # -------------------------------------------------------------------------
    # Final console summary
    # -------------------------------------------------------------------------

    print()
    print("=" * 80)
    print("T6 MOD-009 — HYBRID RETRIEVAL SUMMARY")
    print("=" * 80)

    print()
    print("Selected TRAIN hybrid weight:")
    print(
        f"  lexical={lexical_weight:.2f} "
        f"semantic={semantic_weight:.2f}"
    )

    print()
    print("TRAIN:")
    print("  TF-IDF:")
    for key, value in train_tfidf_metrics.items():
        print(f"    {key}: {value:.6f}")

    print("  Semantic:")
    for key, value in train_semantic_metrics.items():
        print(f"    {key}: {value:.6f}")

    print("  Hybrid:")
    for key, value in train_hybrid_metrics.items():
        print(f"    {key}: {value:.6f}")

    print()
    print("EVAL:")
    print("  TF-IDF:")
    for key, value in eval_tfidf_metrics.items():
        print(f"    {key}: {value:.6f}")

    print("  Semantic:")
    for key, value in eval_semantic_metrics.items():
        print(f"    {key}: {value:.6f}")

    print("  Hybrid:")
    for key, value in eval_hybrid_metrics.items():
        print(f"    {key}: {value:.6f}")

    print()
    print("EVAL rank movement: TF-IDF → Hybrid")
    print(
        f"  Mean:   "
        f"{eval_movement_summary['mean_rank_movement']:.4f}"
    )
    print(
        f"  Median: "
        f"{eval_movement_summary['median_rank_movement']:.4f}"
    )
    print(
        f"  Improved: "
        f"{eval_movement_summary['improved']}"
    )
    print(
        f"  Worsened: "
        f"{eval_movement_summary['worsened']}"
    )
    print(
        f"  Unchanged: "
        f"{eval_movement_summary['unchanged']}"
    )

    print()
    print("TF-IDF Top-20 failure population:")
    print(
        f"  Queries: "
        f"{len(tfidf_failure_query_ids)}"
    )
    print(
        f"  Hybrid Recall@20: "
        f"{failure_metrics['recall_at_20']:.6f}"
    )

    print()
    print("Artifacts:")
    print(f"  {OUTPUT_RANKINGS}")
    print(f"  {OUTPUT_RESULTS}")

    print()
    print(
        f"Runtime: "
        f"{results['runtime_seconds']:.2f} seconds"
    )

    print()
    print("T6 MOD-009: HYBRID_RETRIEVAL_EXPERIMENT_COMPLETED")


if __name__ == "__main__":
    main()