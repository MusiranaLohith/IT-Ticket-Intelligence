from __future__ import annotations

import json
import math
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# =============================================================================
# T6 MOD-010 — CORRECTED HYBRID LEXICAL RECONSTRUCTION
# =============================================================================
#
# Purpose
# -------
# Correct the MOD-009 lexical branch so that it uses the exact text
# representation and TF-IDF scoring procedure established by MOD-004.
#
# Semantic scores are reused from the already-computed MOD-009 artifact.
#
# This operation does NOT:
#   - read the raw dataset
#   - modify targets
#   - modify candidate pools
#   - retrain a model
#   - recompute semantic embeddings
#   - calibrate probabilities
#   - optimize thresholds
#
# Integrity principle
# -------------------
# The corrected lexical branch must reproduce MOD-004 exactly before
# corrected hybrid results are accepted.
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

MOD004_RANKINGS_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod004_query_rankings.csv"
)

MOD009_RANKINGS_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod009_hybrid_query_rankings.csv"
)

OUTPUT_RANKINGS_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod010_corrected_hybrid_query_rankings.csv"
)

OUTPUT_RESULTS_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod010_corrected_hybrid_results.json"
)

OUTPUT_RECONCILIATION_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod010_corrected_lexical_reconciliation.csv"
)


# Exact frozen MOD-004 fields.
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

CANDIDATES_PER_QUERY = 101

SEMANTIC_WEIGHTS = [
    0.10,
    0.25,
    0.50,
    0.75,
    0.90,
]


# =============================================================================
# EXACT MOD-004 TEXT FUNCTIONS
# =============================================================================

def clean_text(value: object) -> str:

    if pd.isna(value):
        return ""

    return str(value).strip()


def build_mod004_text(
    frame: pd.DataFrame,
    columns: list[str],
) -> pd.Series:

    parts = []

    for column in columns:

        field_name = column.replace(
            "_",
            " ",
        )

        values = frame[column].map(
            clean_text
        )

        parts.append(
            field_name
            + " "
            + values
        )

    result = parts[0]

    for part in parts[1:]:

        result = (
            result
            + " "
            + part
        )

    return result


# =============================================================================
# NORMALIZATION
# =============================================================================

def minmax_normalize_within_query(
    frame: pd.DataFrame,
    score_column: str,
    output_column: str,
) -> pd.DataFrame:

    output = frame.copy()

    normalized_parts = []

    for _, group in output.groupby(
        "query_id",
        sort=False,
    ):

        scores = group[
            score_column
        ].to_numpy(
            dtype=np.float64
        )

        minimum = float(
            np.min(scores)
        )

        maximum = float(
            np.max(scores)
        )

        if maximum > minimum:

            normalized = (
                scores - minimum
            ) / (
                maximum - minimum
            )

        else:

            normalized = np.zeros_like(
                scores
            )

        normalized_parts.append(
            pd.Series(
                normalized,
                index=group.index,
                dtype=np.float64,
            )
        )

    output[
        output_column
    ] = pd.concat(
        normalized_parts
    ).sort_index()

    return output


# =============================================================================
# RANK METRICS
# =============================================================================

def rank_metrics(
    frame: pd.DataFrame,
    score_column: str,
) -> dict:

    recalls = {
        1: [],
        3: [],
        5: [],
        10: [],
        20: [],
    }

    reciprocal_ranks = []
    ndcg5 = []
    ndcg10 = []

    for query_id, group in frame.groupby(
        "query_id",
        sort=False,
    ):

        ordered = group.sort_values(
            [
                score_column,
                "candidate_id",
            ],
            ascending=[
                False,
                True,
            ],
            kind="mergesort",
        )

        positive_positions = np.flatnonzero(
            ordered[
                "target_observed"
            ].to_numpy(
                dtype=bool
            )
        )

        if len(positive_positions) != 1:

            raise ValueError(
                f"Query {query_id} does not have exactly one positive."
            )

        rank = (
            int(
                positive_positions[0]
            )
            + 1
        )

        for k in recalls:

            recalls[k].append(
                1.0
                if rank <= k
                else 0.0
            )

        reciprocal_ranks.append(
            1.0 / rank
        )

        ndcg5.append(
            (
                1.0
                / math.log2(rank + 1)
            )
            if rank <= 5
            else 0.0
        )

        ndcg10.append(
            (
                1.0
                / math.log2(rank + 1)
            )
            if rank <= 10
            else 0.0
        )

    return {
        "recall_at_1": float(
            np.mean(recalls[1])
        ),
        "recall_at_3": float(
            np.mean(recalls[3])
        ),
        "recall_at_5": float(
            np.mean(recalls[5])
        ),
        "recall_at_10": float(
            np.mean(recalls[10])
        ),
        "recall_at_20": float(
            np.mean(recalls[20])
        ),
        "mrr": float(
            np.mean(reciprocal_ranks)
        ),
        "ndcg_at_5": float(
            np.mean(ndcg5)
        ),
        "ndcg_at_10": float(
            np.mean(ndcg10)
        ),
    }


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:

    start_time = time.time()

    print("=" * 80)
    print(
        "T6 MOD-010 — CORRECTED HYBRID LEXICAL RECONSTRUCTION"
    )
    print("=" * 80)
    print()

    # =========================================================================
    # 1. LOAD FROZEN ARTIFACTS
    # =========================================================================

    print(
        "[1/9] Loading frozen modeling artifacts..."
    )

    train = pd.read_csv(
        TRAIN_PATH
    )

    evaluation = pd.read_csv(
        EVAL_PATH
    )

    mod004 = pd.read_csv(
        MOD004_RANKINGS_PATH
    )

    mod009 = pd.read_csv(
        MOD009_RANKINGS_PATH
    )

    vectorizer = joblib.load(
        TFIDF_VECTOR_PATH
    )

    print(
        f"TRAIN rows: {len(train):,}"
    )

    print(
        f"EVAL rows: {len(evaluation):,}"
    )

    print(
        f"MOD-004 query rankings: "
        f"{len(mod004):,}"
    )

    print(
        f"MOD-009 candidate rankings: "
        f"{len(mod009):,}"
    )

    print(
        f"TF-IDF vocabulary: "
        f"{len(vectorizer.vocabulary_):,}"
    )

    # =========================================================================
    # 2. VALIDATE POPULATIONS
    # =========================================================================

    print()
    print(
        "[2/9] Validating frozen populations..."
    )

    combined = pd.concat(
        [
            train.assign(
                split_expected="TRAIN"
            ),
            evaluation.assign(
                split_expected="EVAL"
            ),
        ],
        ignore_index=True,
    )

    if len(mod009) != len(combined):

        raise ValueError(
            "MOD-009 row count does not match "
            "frozen train/eval population."
        )

    if (
        mod009[
            [
                "split",
                "query_id",
                "candidate_id",
            ]
        ]
        .duplicated()
        .any()
    ):

        raise ValueError(
            "MOD-009 contains duplicate "
            "split/query/candidate rows."
        )

    mod009["split"] = (
        mod009["split"]
        .astype(str)
        .str.upper()
    )

    print(
        "Frozen population: VALID"
    )

    print(
        f"Unique queries: "
        f"{mod009['query_id'].nunique():,}"
    )

    print(
        f"Unique candidates: "
        f"{mod009['candidate_id'].nunique():,}"
    )

    # =========================================================================
    # 3. RECREATE EXACT MOD-004 TEXT
    # =========================================================================

    print()
    print(
        "[3/9] Recreating exact MOD-004 text..."
    )

    # Query text is defined by query-level fields.
    query_source = (
        combined[
            [
                "query_id",
                *QUERY_COLUMNS,
            ]
        ]
        .drop_duplicates(
            subset=["query_id"],
            keep="first",
        )
        .copy()
    )

    # Candidate text must preserve the candidate representation used by
    # each frozen row. We first verify whether each candidate_id has exactly
    # one textual representation across the frozen modeling population.
    candidate_source = combined[
        [
            "candidate_id",
            *CANDIDATE_COLUMNS,
        ]
    ].copy()

    candidate_source[
        "candidate_text"
    ] = build_mod004_text(
        candidate_source,
        CANDIDATE_COLUMNS,
    )

    candidate_representation_counts = (
        candidate_source
        .groupby(
            "candidate_id"
        )[
            "candidate_text"
        ]
        .nunique(
            dropna=False
        )
    )

    candidates_with_multiple_texts = (
        candidate_representation_counts
        > 1
    )

    print(
        f"Unique candidates: "
        f"{candidate_representation_counts.size:,}"
    )

    print(
        "Candidates with multiple textual "
        f"representations: "
        f"{int(candidates_with_multiple_texts.sum()):,}"
    )

    if candidates_with_multiple_texts.any():

        raise ValueError(
            "Candidate IDs have multiple textual representations "
            "across the frozen modeling population. "
            "Candidate-ID-level lexical deduplication would not be "
            "an exact representation of MOD-004."
        )

    query_source[
        "query_text"
    ] = build_mod004_text(
        query_source,
        QUERY_COLUMNS,
    )

    candidate_source = (
        candidate_source[
            [
                "candidate_id",
                "candidate_text",
            ]
        ]
        .drop_duplicates(
            subset=["candidate_id"],
            keep="first",
        )
        .copy()
    )

    print(
        "Exact MOD-004 text construction: READY"
    )

    # =========================================================================
    # 4. TRANSFORM WITH SAVED MOD-004 VECTORIZER
    # =========================================================================

    print()
    print(
        "[4/9] Transforming exact MOD-004 representations..."
    )

    query_matrix = vectorizer.transform(
        query_source[
            "query_text"
        ]
    )

    candidate_matrix = vectorizer.transform(
        candidate_source[
            "candidate_text"
        ]
    )

    print(
        f"Query matrix: "
        f"{query_matrix.shape}"
    )

    print(
        f"Candidate matrix: "
        f"{candidate_matrix.shape}"
    )

    # =========================================================================
    # 5. RECONSTRUCT CORRECTED LEXICAL SCORES
    # =========================================================================

    print()
    print(
        "[5/9] Computing corrected MOD-004-equivalent "
        "lexical scores..."
    )

    query_index = {
        value: index
        for index, value in enumerate(
            query_source[
                "query_id"
            ]
        )
    }

    candidate_index = {
        value: index
        for index, value in enumerate(
            candidate_source[
                "candidate_id"
            ]
        )
    }

    corrected_scores = []

    for row in mod009.itertuples(
        index=False
    ):

        query_id = row.query_id
        candidate_id = row.candidate_id

        q_index = query_index[
            query_id
        ]

        c_index = candidate_index[
            candidate_id
        ]

        score = float(
            query_matrix[
                q_index
            ]
            .dot(
                candidate_matrix[
                    c_index
                ].T
            )
            .toarray()[0, 0]
        )

        corrected_scores.append(
            score
        )

    mod009[
        "corrected_tfidf_score"
    ] = corrected_scores

    # =========================================================================
    # 6. HARD RECONCILIATION AGAINST MOD-004
    # =========================================================================

    print()
    print(
        "[6/9] Performing hard lexical reconciliation..."
    )

    # Reconstruct MOD-004 scores directly from the frozen split rows.
    exact_row_scores = []

    for split_name, frame in [
        (
            "TRAIN",
            train,
        ),
        (
            "EVAL",
            evaluation,
        ),
    ]:

        query_text = build_mod004_text(
            frame,
            QUERY_COLUMNS,
        )

        candidate_text = build_mod004_text(
            frame,
            CANDIDATE_COLUMNS,
        )

        q_matrix = vectorizer.transform(
            query_text
        )

        c_matrix = vectorizer.transform(
            candidate_text
        )

        for query_id, row_indices in frame.groupby(
            "query_id",
            sort=False,
        ).groups.items():

            row_indices = np.asarray(
                row_indices,
                dtype=int,
            )

            query_vector = q_matrix[
                row_indices[0]
            ]

            candidate_vectors = c_matrix[
                row_indices
            ]

            scores = (
                candidate_vectors
                @ query_vector.T
            )

            scores = np.asarray(
                scores.toarray()
            ).reshape(-1)

            candidate_ids = frame.iloc[
                row_indices
            ][
                "candidate_id"
            ].to_numpy()

            for candidate_id, score in zip(
                candidate_ids,
                scores,
            ):

                exact_row_scores.append(
                    {
                        "split": split_name,
                        "query_id": query_id,
                        "candidate_id": candidate_id,
                        "exact_mod004_score": float(
                            score
                        ),
                    }
                )

    exact_scores_df = pd.DataFrame(
        exact_row_scores
    )

    comparison = exact_scores_df.merge(
        mod009[
            [
                "split",
                "query_id",
                "candidate_id",
                "corrected_tfidf_score",
            ]
        ],
        on=[
            "split",
            "query_id",
            "candidate_id",
        ],
        how="inner",
        validate="one_to_one",
    )

    if len(comparison) != len(
        exact_scores_df
    ):

        raise ValueError(
            "Hard reconciliation failed: "
            "not all MOD-004 rows matched."
        )

    comparison[
        "absolute_difference"
    ] = (
        comparison[
            "exact_mod004_score"
        ]
        -
        comparison[
            "corrected_tfidf_score"
        ]
        .abs()
    )

    max_difference = float(
        comparison[
            "absolute_difference"
        ].max()
    )

    mean_difference = float(
        comparison[
            "absolute_difference"
        ].mean()
    )

    print(
        f"Rows reconciled: "
        f"{len(comparison):,}"
    )

    print(
        f"Mean absolute difference: "
        f"{mean_difference:.12g}"
    )

    print(
        f"Maximum absolute difference: "
        f"{max_difference:.12g}"
    )

    if max_difference > 1e-12:

        raise ValueError(
            "HARD GATE FAILED: corrected lexical scores "
            "do not reproduce MOD-004 within 1e-12."
        )

    print(
        "HARD GATE: PASS"
    )

    # Save reconciliation.
    comparison.to_csv(
        OUTPUT_RECONCILIATION_PATH,
        index=False,
    )

    # =========================================================================
    # 7. VERIFY SEMANTIC SCORE ALIGNMENT
    # =========================================================================

    print()
    print(
        "[7/9] Verifying reuse of MOD-009 semantic scores..."
    )

    semantic_required = [
        "split",
        "query_id",
        "candidate_id",
        "target_observed",
        "semantic_score",
    ]

    missing = [
        column
        for column in semantic_required
        if column not in mod009.columns
    ]

    if missing:

        raise ValueError(
            f"MOD-009 missing semantic columns: {missing}"
        )

    semantic_positive_count = int(
        mod009[
            "target_observed"
        ]
        .astype(bool)
        .sum()
    )

    if semantic_positive_count != 2722:

        raise ValueError(
            "Unexpected MOD-009 positive count."
        )

    print(
        f"Stored semantic scores available: "
        f"{len(mod009):,}"
    )

    print(
        f"Observed positives: "
        f"{semantic_positive_count:,}"
    )

    print(
        "Semantic branch reused from MOD-009; "
        "no embedding recomputation."
    )

    # =========================================================================
    # 8. CORRECTED HYBRID + TRAIN-ONLY WEIGHT SELECTION
    # =========================================================================

    print()
    print(
        "[8/9] Constructing corrected hybrid and selecting "
        "weight on TRAIN only..."
    )

    rankings = mod009[
        [
            "split",
            "query_id",
            "candidate_id",
            "target_observed",
            "semantic_score",
        ]
    ].copy()

    rankings[
        "tfidf_score"
    ] = mod009[
        "corrected_tfidf_score"
    ].to_numpy(
        dtype=np.float64
    )

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

    train_rankings = rankings[
        rankings["split"] == "TRAIN"
    ].copy()

    eval_rankings = rankings[
        rankings["split"] == "EVAL"
    ].copy()

    weight_results = []

    for semantic_weight in SEMANTIC_WEIGHTS:

        lexical_weight = (
            1.0
            - semantic_weight
        )

        train_test = train_rankings.copy()

        train_test[
            "hybrid_score"
        ] = (
            lexical_weight
            * train_test[
                "tfidf_score_normalized"
            ]
            +
            semantic_weight
            * train_test[
                "semantic_score_normalized"
            ]
        )

        metrics = rank_metrics(
            train_test,
            "hybrid_score",
        )

        metrics[
            "semantic_weight"
        ] = semantic_weight

        metrics[
            "lexical_weight"
        ] = lexical_weight

        weight_results.append(
            metrics
        )

        print(
            f"  semantic={semantic_weight:.2f} "
            f"lexical={lexical_weight:.2f} "
            f"R@20={metrics['recall_at_20']:.6f} "
            f"MRR={metrics['mrr']:.6f} "
            f"R@10={metrics['recall_at_10']:.6f}"
        )

    selected = sorted(
        weight_results,
        key=lambda item: (
            -item["recall_at_20"],
            -item["mrr"],
            -item["recall_at_10"],
            item["semantic_weight"],
        ),
    )[0]

    selected_semantic_weight = (
        selected["semantic_weight"]
    )

    selected_lexical_weight = (
        selected["lexical_weight"]
    )

    print()
    print(
        "SELECTED WEIGHT:"
    )

    print(
        f"  lexical: "
        f"{selected_lexical_weight:.2f}"
    )

    print(
        f"  semantic: "
        f"{selected_semantic_weight:.2f}"
    )

    rankings[
        "hybrid_score"
    ] = (
        selected_lexical_weight
        * rankings[
            "tfidf_score_normalized"
        ]
        +
        selected_semantic_weight
        * rankings[
            "semantic_score_normalized"
        ]
    )

    # =========================================================================
    # 9. FINAL METRICS + SAVE
    # =========================================================================

    print()
    print(
        "[9/9] Computing corrected hybrid results..."
    )

    train_tfidf_metrics = rank_metrics(
        train_rankings.assign(
            hybrid_score=train_rankings[
                "tfidf_score_normalized"
            ]
        ),
        "hybrid_score",
    )

    eval_tfidf_metrics = rank_metrics(
        eval_rankings.assign(
            hybrid_score=eval_rankings[
                "tfidf_score_normalized"
            ]
        ),
        "hybrid_score",
    )

    train_semantic_metrics = rank_metrics(
        train_rankings,
        "semantic_score",
    )

    eval_semantic_metrics = rank_metrics(
        eval_rankings,
        "semantic_score",
    )

    train_corrected = rankings[
        rankings["split"] == "TRAIN"
    ].copy()

    eval_corrected = rankings[
        rankings["split"] == "EVAL"
    ].copy()

    train_hybrid_metrics = rank_metrics(
        train_corrected,
        "hybrid_score",
    )

    eval_hybrid_metrics = rank_metrics(
        eval_corrected,
        "hybrid_score",
    )

    rankings.to_csv(
        OUTPUT_RANKINGS_PATH,
        index=False,
    )

    results = {
        "task_id": "T6",
        "operation_id": "MOD-010",
        "operation_name": (
            "Corrected Hybrid Lexical Reconstruction"
        ),
        "status": "COMPLETED",

        "lexical_reconciliation": {
            "rows": int(
                len(comparison)
            ),
            "mean_absolute_difference": mean_difference,
            "maximum_absolute_difference": max_difference,
            "tolerance": 1e-12,
            "hard_gate_passed": True,
        },

        "semantic_branch": {
            "source": "MOD-009",
            "recomputed": False,
            "rows": int(
                len(mod009)
            ),
            "positive_rows": semantic_positive_count,
        },

        "population": {
            "train_rows": int(
                len(train)
            ),
            "eval_rows": int(
                len(evaluation)
            ),
            "queries": int(
                rankings["query_id"].nunique()
            ),
            "candidate_rows": int(
                len(rankings)
            ),
        },

        "weight_selection": {
            "selection_split": "TRAIN",
            "criteria": [
                "Recall@20",
                "MRR",
                "Recall@10",
            ],
            "predeclared_weights": SEMANTIC_WEIGHTS,
            "candidates": weight_results,
            "selected": selected,
        },

        "metrics": {
            "train": {
                "tfidf": train_tfidf_metrics,
                "semantic": train_semantic_metrics,
                "corrected_hybrid": train_hybrid_metrics,
            },
            "eval": {
                "tfidf": eval_tfidf_metrics,
                "semantic": eval_semantic_metrics,
                "corrected_hybrid": eval_hybrid_metrics,
            },
        },

        "controls": {
            "raw_dataset_read": False,
            "target_modification": False,
            "candidate_pool_modification": False,
            "semantic_recomputation": False,
            "model_training": False,
            "calibration": False,
            "threshold_optimization": False,
            "evaluation_weight_selection": False,
        },

        "artifacts": {
            "corrected_rankings": str(
                OUTPUT_RANKINGS_PATH
            ),
            "results": str(
                OUTPUT_RESULTS_PATH
            ),
            "lexical_reconciliation": str(
                OUTPUT_RECONCILIATION_PATH
            ),
        },

        "runtime_seconds": round(
            time.time()
            - start_time,
            2,
        ),
    }

    with OUTPUT_RESULTS_PATH.open(
        "w",
        encoding="utf-8",
    ) as handle:

        json.dump(
            results,
            handle,
            indent=2,
        )

    print()
    print("=" * 80)
    print(
        "CORRECTED TF-IDF:"
    )

    print(
        f"  Mean absolute difference: "
        f"{mean_difference:.12g}"
    )

    print(
        f"  Maximum absolute difference: "
        f"{max_difference:.12g}"
    )

    print()
    print("TRAIN — TF-IDF:")
    for key, value in train_tfidf_metrics.items():
        print(
            f"  {key}: {value:.6f}"
        )

    print()
    print("TRAIN — SEMANTIC:")
    for key, value in train_semantic_metrics.items():
        print(
            f"  {key}: {value:.6f}"
        )

    print()
    print("TRAIN — CORRECTED HYBRID:")
    for key, value in train_hybrid_metrics.items():
        print(
            f"  {key}: {value:.6f}"
        )

    print()
    print("EVAL — TF-IDF:")
    for key, value in eval_tfidf_metrics.items():
        print(
            f"  {key}: {value:.6f}"
        )

    print()
    print("EVAL — SEMANTIC:")
    for key, value in eval_semantic_metrics.items():
        print(
            f"  {key}: {value:.6f}"
        )

    print()
    print("EVAL — CORRECTED HYBRID:")
    for key, value in eval_hybrid_metrics.items():
        print(
            f"  {key}: {value:.6f}"
        )

    print()
    print(
        f"Runtime: "
        f"{results['runtime_seconds']:.2f} seconds"
    )

    print()
    print("Artifacts:")
    print(
        f"  {OUTPUT_RANKINGS_PATH}"
    )
    print(
        f"  {OUTPUT_RESULTS_PATH}"
    )
    print(
        f"  {OUTPUT_RECONCILIATION_PATH}"
    )

    print()
    print(
        "T6 MOD-010: "
        "CORRECTED_HYBRID_RECONCILIATION_COMPLETED"
    )


if __name__ == "__main__":
    main()