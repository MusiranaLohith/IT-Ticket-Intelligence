#!/usr/bin/env python3

"""
T6 — MOD-010
Direct TF-IDF Score Reconciliation

Purpose:
    Compare the exact original MOD-004 TF-IDF scores against the
    TF-IDF scores stored inside the MOD-009 candidate-level artifact.

This is a read-only diagnostic.

Controls:
    - No raw dataset access.
    - No model training.
    - No target modification.
    - No candidate-pool modification.
    - No semantic model loading.
    - No calibration.
    - No threshold optimization.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
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

VECTORIZER_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "models"
    / "t6_mod004_tfidf_vectorizer.joblib"
)

MOD009_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod009_hybrid_query_rankings.csv"
)

OUTPUT_REPORT = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod010_direct_score_reconciliation.json"
)

OUTPUT_SAMPLE = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod010_direct_score_differences.csv"
)


# ============================================================================
# Exact MOD-004 feature definition
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


# ============================================================================
# Exact MOD-004 text construction
# ============================================================================

def clean_text(value: object) -> str:

    if pd.isna(value):
        return ""

    return str(value).strip()


def build_text(
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


# ============================================================================
# Main
# ============================================================================

def main() -> None:

    print("=" * 80)
    print("T6 MOD-010 — DIRECT TF-IDF SCORE RECONCILIATION")
    print("=" * 80)
    print()

    # ------------------------------------------------------------------------
    # 1. Load
    # ------------------------------------------------------------------------

    print("[1/8] Loading frozen artifacts...")

    train = pd.read_csv(
        TRAIN_PATH
    )

    evaluation = pd.read_csv(
        EVAL_PATH
    )

    mod009 = pd.read_csv(
        MOD009_PATH
    )

    vectorizer = joblib.load(
        VECTORIZER_PATH
    )

    print(
        f"TRAIN rows: {len(train):,}"
    )

    print(
        f"EVAL rows: {len(evaluation):,}"
    )

    print(
        f"MOD-009 rows: {len(mod009):,}"
    )

    print(
        f"Vectorizer vocabulary: "
        f"{len(vectorizer.vocabulary_):,}"
    )

    # ------------------------------------------------------------------------
    # 2. Validate MOD-009
    # ------------------------------------------------------------------------

    print()
    print("[2/8] Validating MOD-009 candidate artifact...")

    required_mod009 = [
        "split",
        "query_id",
        "candidate_id",
        "target_observed",
        "tfidf_score",
    ]

    missing = [
        column
        for column in required_mod009
        if column not in mod009.columns
    ]

    if missing:
        raise ValueError(
            f"MOD-009 missing columns: {missing}"
        )

    if mod009[
        [
            "split",
            "query_id",
            "candidate_id",
        ]
    ].duplicated().any():

        raise ValueError(
            "MOD-009 contains duplicate "
            "split/query_id/candidate_id rows."
        )

    print("MOD-009 schema: VALID")

    print(
        f"Unique queries: "
        f"{mod009['query_id'].nunique():,}"
    )

    print(
        f"Unique query-candidate pairs: "
        f"{len(mod009[['query_id', 'candidate_id']].drop_duplicates()):,}"
    )

    print(
        f"Stored TF-IDF score range: "
        f"{mod009['tfidf_score'].min():.12f} → "
        f"{mod009['tfidf_score'].max():.12f}"
    )

    # ------------------------------------------------------------------------
    # 3. Build exact MOD-004 text
    # ------------------------------------------------------------------------

    print()
    print(
        "[3/8] Recreating exact MOD-004 text representations..."
    )

    train_query_text = build_text(
        train,
        QUERY_COLUMNS,
    )

    train_candidate_text = build_text(
        train,
        CANDIDATE_COLUMNS,
    )

    eval_query_text = build_text(
        evaluation,
        QUERY_COLUMNS,
    )

    eval_candidate_text = build_text(
        evaluation,
        CANDIDATE_COLUMNS,
    )

    print(
        "Exact MOD-004 text construction: REPRODUCED"
    )

    # ------------------------------------------------------------------------
    # 4. Transform with saved vectorizer
    # ------------------------------------------------------------------------

    print()
    print(
        "[4/8] Transforming frozen splits with saved vectorizer..."
    )

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

    print(
        f"TRAIN query matrix: "
        f"{train_query_matrix.shape}"
    )

    print(
        f"TRAIN candidate matrix: "
        f"{train_candidate_matrix.shape}"
    )

    print(
        f"EVAL query matrix: "
        f"{eval_query_matrix.shape}"
    )

    print(
        f"EVAL candidate matrix: "
        f"{eval_candidate_matrix.shape}"
    )

    # ------------------------------------------------------------------------
    # 5. Compute exact scores for every candidate row
    # ------------------------------------------------------------------------

    print()
    print(
        "[5/8] Computing exact MOD-004 TF-IDF scores..."
    )

    exact_scores = []

    for split_name, frame, query_matrix, candidate_matrix in [
        (
            "TRAIN",
            train,
            train_query_matrix,
            train_candidate_matrix,
        ),
        (
            "EVAL",
            evaluation,
            eval_query_matrix,
            eval_candidate_matrix,
        ),
    ]:

        grouped_indices = frame.groupby(
            "query_id",
            sort=False,
        ).indices

        for query_id, row_indices in grouped_indices.items():

            row_indices = np.asarray(
                row_indices,
                dtype=int,
            )

            # Exact MOD-004 behavior:
            # first row in each query group is the query vector.
            query_vector = query_matrix[
                row_indices[0]
            ]

            candidate_vectors = candidate_matrix[
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
            ]["candidate_id"].to_numpy()

            for candidate_id, score in zip(
                candidate_ids,
                scores,
            ):

                exact_scores.append(
                    {
                        "split": split_name,
                        "query_id": int(
                            query_id
                        ),
                        "candidate_id": int(
                            candidate_id
                        ),
                        "exact_tfidf_score": float(
                            score
                        ),
                    }
                )

    exact_df = pd.DataFrame(
        exact_scores
    )

    print(
        f"Exact score rows: "
        f"{len(exact_df):,}"
    )

    # ------------------------------------------------------------------------
    # 6. Merge against MOD-009 stored TF-IDF scores
    # ------------------------------------------------------------------------

    print()
    print(
        "[6/8] Comparing exact scores with MOD-009 scores..."
    )

    stored = mod009[
        [
            "split",
            "query_id",
            "candidate_id",
            "tfidf_score",
        ]
    ].copy()

    stored["split"] = (
        stored["split"]
        .astype(str)
        .str.upper()
    )

    exact_df["split"] = (
        exact_df["split"]
        .astype(str)
        .str.upper()
    )

    comparison = exact_df.merge(
        stored,
        on=[
            "split",
            "query_id",
            "candidate_id",
        ],
        how="inner",
        validate="one_to_one",
    )

    if len(comparison) != len(exact_df):

        raise ValueError(
            "Not all exact score rows matched MOD-009."
        )

    print(
        f"Rows compared: "
        f"{len(comparison):,}"
    )

    comparison["score_difference"] = (
        comparison["exact_tfidf_score"]
        -
        comparison["tfidf_score"]
    )

    comparison["absolute_score_difference"] = (
        comparison["score_difference"].abs()
    )

    # ------------------------------------------------------------------------
    # 7. Analyze
    # ------------------------------------------------------------------------

    print()
    print(
        "[7/8] Analyzing score discrepancies..."
    )

    mean_abs = float(
        comparison[
            "absolute_score_difference"
        ].mean()
    )

    median_abs = float(
        comparison[
            "absolute_score_difference"
        ].median()
    )

    max_abs = float(
        comparison[
            "absolute_score_difference"
        ].max()
    )

    exact_match_count = int(
        (
            comparison[
                "absolute_score_difference"
            ]
            <= 1e-12
        ).sum()
    )

    difference_count = (
        len(comparison)
        -
        exact_match_count
    )

    print(
        f"Mean absolute difference: "
        f"{mean_abs:.12g}"
    )

    print(
        f"Median absolute difference: "
        f"{median_abs:.12g}"
    )

    print(
        f"Maximum absolute difference: "
        f"{max_abs:.12g}"
    )

    print(
        f"Scores equal within 1e-12: "
        f"{exact_match_count:,}/"
        f"{len(comparison):,}"
    )

    print(
        f"Scores differing >1e-12: "
        f"{difference_count:,}/"
        f"{len(comparison):,}"
    )

    # By split.
    print()
    print("By split:")

    split_summary = (
        comparison
        .groupby("split")
        [
            "absolute_score_difference"
        ]
        .agg(
            [
                "count",
                "mean",
                "median",
                "max",
            ]
        )
    )

    print(
        split_summary.to_string()
    )

    # Largest discrepancies.
    largest = (
        comparison
        .sort_values(
            "absolute_score_difference",
            ascending=False,
        )
        .head(20)
    )

    print()
    print(
        "Largest 20 score discrepancies:"
    )

    print(
        largest[
            [
                "split",
                "query_id",
                "candidate_id",
                "exact_tfidf_score",
                "tfidf_score",
                "score_difference",
                "absolute_score_difference",
            ]
        ].to_string(index=False)
    )

    # ------------------------------------------------------------------------
    # 8. Save
    # ------------------------------------------------------------------------

    print()
    print(
        "[8/8] Saving reconciliation artifacts..."
    )

    largest.to_csv(
        OUTPUT_SAMPLE,
        index=False,
    )

    report = {
        "task_id": "T6",
        "operation_id": "MOD-010",
        "operation_name": (
            "Direct TF-IDF Score Reconciliation"
        ),
        "status": "COMPLETED",

        "population": {
            "exact_score_rows": int(
                len(exact_df)
            ),
            "mod009_rows": int(
                len(mod009)
            ),
            "rows_compared": int(
                len(comparison)
            ),
        },

        "score_comparison": {
            "mean_absolute_difference": mean_abs,
            "median_absolute_difference": median_abs,
            "maximum_absolute_difference": max_abs,
            "scores_equal_within_1e-12": exact_match_count,
            "scores_differing_gt_1e-12": difference_count,
        },

        "controls": {
            "raw_dataset_read": False,
            "model_training": False,
            "semantic_model_loading": False,
            "target_modification": False,
            "candidate_pool_modification": False,
            "calibration": False,
            "threshold_optimization": False,
        },

        "artifacts": {
            "report": str(
                OUTPUT_REPORT
            ),
            "largest_score_differences": str(
                OUTPUT_SAMPLE
            ),
        },
    }

    with OUTPUT_REPORT.open(
        "w",
        encoding="utf-8",
    ) as handle:

        json.dump(
            report,
            handle,
            indent=2,
        )

    print()
    print("Artifacts:")
    print(
        f"  {OUTPUT_REPORT}"
    )
    print(
        f"  {OUTPUT_SAMPLE}"
    )

    print()
    print("=" * 80)
    print(
        "T6 MOD-010: DIRECT_SCORE_RECONCILIATION_COMPLETED"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()