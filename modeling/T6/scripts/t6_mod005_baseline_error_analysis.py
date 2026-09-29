#!/usr/bin/env python3

"""
T6 — MOD-005
TF-IDF Retrieval Baseline Error Analysis

Reads only the MOD-004 query-level ranking artifact and performs
query-level error analysis.

No:
    - model retraining
    - vectorizer refitting
    - raw dataset access
    - threshold optimization
    - probability calibration

Analyzes:
    - positive-rank distribution
    - Recall@K counts
    - Top-20 failures
    - Top-1 correctness
    - score gaps between the positive and Top-1 candidate
    - score-gap behavior for correct/incorrect Top-1 results
    - TRAIN vs EVAL rank distributions
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================================
# Paths
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod004_query_rankings.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
)

RESULTS_PATH = (
    OUTPUT_DIR
    / "t6_mod005_baseline_error_analysis.json"
)

RANK_DISTRIBUTION_PATH = (
    OUTPUT_DIR
    / "t6_mod005_rank_distribution.csv"
)

FAILURES_PATH = (
    OUTPUT_DIR
    / "t6_mod005_top20_failures.csv"
)

LOG_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "logs"
)

LOG_PATH = (
    LOG_DIR
    / "t6_mod005_baseline_error_analysis.log"
)


# ============================================================================
# Frozen analysis parameters
# ============================================================================

K_VALUES = [1, 3, 5, 10, 20]


# ============================================================================
# Helpers
# ============================================================================

def validate_input(df: pd.DataFrame) -> None:
    required_columns = [
        "split",
        "query_id",
        "positive_candidate_id",
        "positive_rank",
        "top_candidate_id",
        "top_candidate_role",
        "top_score",
        "positive_score",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing)
        )


def summarize_split(
    frame: pd.DataFrame,
) -> dict:

    query_count = len(frame)

    if query_count == 0:
        raise ValueError("Cannot summarize an empty split.")

    rank = frame["positive_rank"].astype(int)

    result = {
        "queries": int(query_count),
        "recall_at_1": float(
            (rank <= 1).mean()
        ),
        "recall_at_3": float(
            (rank <= 3).mean()
        ),
        "recall_at_5": float(
            (rank <= 5).mean()
        ),
        "recall_at_10": float(
            (rank <= 10).mean()
        ),
        "recall_at_20": float(
            (rank <= 20).mean()
        ),
        "mrr": float(
            (1.0 / rank).mean()
        ),
        "positive_rank": {
            "minimum": int(rank.min()),
            "median": float(rank.median()),
            "mean": float(rank.mean()),
            "maximum": int(rank.max()),
        },
        "rank_distribution": {
            "rank_1": int((rank == 1).sum()),
            "rank_2_3": int(
                ((rank >= 2) & (rank <= 3)).sum()
            ),
            "rank_4_5": int(
                ((rank >= 4) & (rank <= 5)).sum()
            ),
            "rank_6_10": int(
                ((rank >= 6) & (rank <= 10)).sum()
            ),
            "rank_11_20": int(
                ((rank >= 11) & (rank <= 20)).sum()
            ),
            "rank_gt_20": int(
                (rank > 20).sum()
            ),
        },
    }

    # ------------------------------------------------------------------------
    # Score-gap analysis
    # ------------------------------------------------------------------------

    frame = frame.copy()

    frame["score_gap_top1_minus_positive"] = (
        frame["top_score"].astype(float)
        - frame["positive_score"].astype(float)
    )

    frame["top1_correct"] = (
        frame["positive_rank"] == 1
    )

    correct = frame[
        frame["top1_correct"]
    ]

    incorrect = frame[
        ~frame["top1_correct"]
    ]

    result["top1"] = {
        "correct_queries": int(len(correct)),
        "incorrect_queries": int(len(incorrect)),
        "correct_rate": float(
            len(correct) / query_count
        ),
    }

    def gap_summary(
        subset: pd.DataFrame,
    ) -> dict:

        if len(subset) == 0:
            return {
                "queries": 0,
                "mean": None,
                "median": None,
                "minimum": None,
                "maximum": None,
            }

        values = subset[
            "score_gap_top1_minus_positive"
        ].astype(float)

        return {
            "queries": int(len(values)),
            "mean": float(values.mean()),
            "median": float(values.median()),
            "minimum": float(values.min()),
            "maximum": float(values.max()),
        }

    result["score_gap"] = {
        "all": gap_summary(frame),
        "top1_correct": gap_summary(correct),
        "top1_incorrect": gap_summary(incorrect),
    }

    # ------------------------------------------------------------------------
    # Positive-score analysis
    # ------------------------------------------------------------------------

    result["positive_score"] = {
        "mean": float(
            frame["positive_score"].astype(float).mean()
        ),
        "median": float(
            frame["positive_score"].astype(float).median()
        ),
        "minimum": float(
            frame["positive_score"].astype(float).min()
        ),
        "maximum": float(
            frame["positive_score"].astype(float).max()
        ),
    }

    result["top1_score"] = {
        "mean": float(
            frame["top_score"].astype(float).mean()
        ),
        "median": float(
            frame["top_score"].astype(float).median()
        ),
        "minimum": float(
            frame["top_score"].astype(float).min()
        ),
        "maximum": float(
            frame["top_score"].astype(float).max()
        ),
    }

    return result


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

    log("=" * 80)
    log("T6 MOD-005 — TF-IDF RETRIEVAL BASELINE ERROR ANALYSIS")
    log("=" * 80)
    log(f"Input: {INPUT_PATH}")
    log("")

    # ------------------------------------------------------------------------
    # Load MOD-004 artifact
    # ------------------------------------------------------------------------

    log("[1/7] Loading MOD-004 query-level rankings...")

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"MOD-004 ranking artifact not found: {INPUT_PATH}"
        )

    df = pd.read_csv(INPUT_PATH)

    log(f"Rows loaded: {len(df):,}")

    validate_input(df)

    # ------------------------------------------------------------------------
    # Validate native ranking artifact
    # ------------------------------------------------------------------------

    log("")
    log("[2/7] Validating ranking artifact...")

    expected_splits = {"train", "eval"}

    observed_splits = set(
        df["split"].astype(str).unique()
    )

    if not observed_splits.issubset(expected_splits):
        raise ValueError(
            "Unexpected split values: "
            + repr(
                sorted(
                    observed_splits - expected_splits
                )
            )
        )

    if df["query_id"].duplicated().any():
        duplicate_query_count = int(
            df["query_id"].duplicated().sum()
        )

        # query_id is expected to be unique within each split,
        # but the same query ID must never cross splits.
        duplicate_pairs = df.duplicated(
            subset=["split", "query_id"]
        )

        if duplicate_pairs.any():
            raise ValueError(
                "Duplicate split/query records detected: "
                f"{int(duplicate_pairs.sum())}"
            )

    if not bool(
        (df["positive_rank"] >= 1).all()
    ):
        raise ValueError(
            "Invalid positive rank detected."
        )

    log(
        f"TRAIN queries: "
        f"{int((df['split'] == 'train').sum()):,}"
    )

    log(
        f"EVAL queries: "
        f"{int((df['split'] == 'eval').sum()):,}"
    )

    log("Ranking artifact structure: VALID")

    # ------------------------------------------------------------------------
    # Rank distribution
    # ------------------------------------------------------------------------

    log("")
    log("[3/7] Calculating positive-rank distribution...")

    rank_rows = []

    for split_name in ["train", "eval"]:
        split_df = df[
            df["split"] == split_name
        ]

        ranks = (
            split_df["positive_rank"]
            .astype(int)
        )

        for k in K_VALUES:
            rank_rows.append(
                {
                    "split": split_name,
                    "metric": f"Recall@{k}",
                    "value": float(
                        (ranks <= k).mean()
                    ),
                    "successful_queries": int(
                        (ranks <= k).sum()
                    ),
                    "total_queries": int(
                        len(split_df)
                    ),
                }
            )

        # Exact ranks 1–20 plus >20.
        for rank_value in range(1, 21):
            count = int(
                (ranks == rank_value).sum()
            )

            rank_rows.append(
                {
                    "split": split_name,
                    "metric": f"ExactRank@{rank_value}",
                    "value": float(
                        count / len(split_df)
                    ),
                    "successful_queries": count,
                    "total_queries": int(
                        len(split_df)
                    ),
                }
            )

        count_gt20 = int(
            (ranks > 20).sum()
        )

        rank_rows.append(
            {
                "split": split_name,
                "metric": "Rank>20",
                "value": float(
                    count_gt20 / len(split_df)
                ),
                "successful_queries": count_gt20,
                "total_queries": int(
                    len(split_df)
                ),
            }
        )

    rank_distribution_df = pd.DataFrame(
        rank_rows
    )

    rank_distribution_df.to_csv(
        RANK_DISTRIBUTION_PATH,
        index=False,
    )

    # ------------------------------------------------------------------------
    # Score-gap calculation
    # ------------------------------------------------------------------------

    log("")
    log("[4/7] Calculating Top-1 / positive score gaps...")

    df["score_gap_top1_minus_positive"] = (
        df["top_score"].astype(float)
        - df["positive_score"].astype(float)
    )

    df["top1_correct"] = (
        df["positive_rank"] == 1
    )

    log(
        "Score-gap definition:"
    )

    log(
        "  Top-1 score minus observed-positive score"
    )

    # ------------------------------------------------------------------------
    # Identify Top-20 failures
    # ------------------------------------------------------------------------

    log("")
    log("[5/7] Identifying Top-20 retrieval failures...")

    failures = df[
        df["positive_rank"] > 20
    ].copy()

    failures = failures.sort_values(
        [
            "split",
            "positive_rank",
            "score_gap_top1_minus_positive",
        ],
        ascending=[
            True,
            True,
            False,
        ],
    )

    failure_columns = [
        "split",
        "query_id",
        "positive_candidate_id",
        "positive_rank",
        "top_candidate_id",
        "top_candidate_role",
        "top_score",
        "positive_score",
        "score_gap_top1_minus_positive",
    ]

    failures[
        failure_columns
    ].to_csv(
        FAILURES_PATH,
        index=False,
    )

    log(
        f"Top-20 failures: {len(failures):,}"
    )

    # ------------------------------------------------------------------------
    # Aggregate summaries
    # ------------------------------------------------------------------------

    log("")
    log("[6/7] Building split-level error analysis...")

    train_df = df[
        df["split"] == "train"
    ].copy()

    eval_df = df[
        df["split"] == "eval"
    ].copy()

    train_summary = summarize_split(
        train_df
    )

    eval_summary = summarize_split(
        eval_df
    )

    # ------------------------------------------------------------------------
    # Compare TRAIN and EVAL
    # ------------------------------------------------------------------------

    def metric_delta(
        metric_name: str,
    ) -> float:
        return float(
            eval_summary[metric_name]
            - train_summary[metric_name]
        )

    comparison = {
        "recall_at_1_eval_minus_train": metric_delta(
            "recall_at_1"
        ),
        "recall_at_3_eval_minus_train": metric_delta(
            "recall_at_3"
        ),
        "recall_at_5_eval_minus_train": metric_delta(
            "recall_at_5"
        ),
        "recall_at_10_eval_minus_train": metric_delta(
            "recall_at_10"
        ),
        "recall_at_20_eval_minus_train": metric_delta(
            "recall_at_20"
        ),
        "mrr_eval_minus_train": metric_delta(
            "mrr"
        ),
    }

    # ------------------------------------------------------------------------
    # Additional failure concentration
    # ------------------------------------------------------------------------

    def failure_concentration(
        frame: pd.DataFrame,
    ) -> dict:

        total = len(frame)

        return {
            "rank_gt_20": int(
                (frame["positive_rank"] > 20).sum()
            ),
            "rank_gt_50": int(
                (frame["positive_rank"] > 50).sum()
            ),
            "rank_gt_75": int(
                (frame["positive_rank"] > 75).sum()
            ),
            "rank_gt_100": int(
                (frame["positive_rank"] > 100).sum()
            ),
            "rank_gt_20_rate": float(
                (frame["positive_rank"] > 20).mean()
            ),
            "rank_gt_50_rate": float(
                (frame["positive_rank"] > 50).mean()
            ),
            "rank_gt_75_rate": float(
                (frame["positive_rank"] > 75).mean()
            ),
            "rank_gt_100_rate": float(
                (frame["positive_rank"] > 100).mean()
            ),
        }

    concentration = {
        "train": failure_concentration(train_df),
        "eval": failure_concentration(eval_df),
    }

    # ------------------------------------------------------------------------
    # Full result artifact
    # ------------------------------------------------------------------------

    log("")
    log("[7/7] Saving analysis artifacts...")

    results = {
        "operation": "T6 MOD-005",
        "task": "T6 Similar-Ticket Retrieval",
        "status": "BASELINE_ERROR_ANALYSIS_COMPLETED",

        "input_artifact": str(INPUT_PATH),

        "analysis_only": True,

        "controls": {
            "model_retrained": False,
            "vectorizer_refit": False,
            "raw_dataset_read": False,
            "accepted_dtm_artifact_read": False,
            "threshold_optimization": False,
            "probability_calibration": False,
            "candidate_pool_modified": False,
            "ranking_artifact_modified": False,
        },

        "train": train_summary,
        "eval": eval_summary,

        "train_eval_comparison": comparison,

        "failure_concentration": concentration,

        "top20_failures": {
            "total": int(len(failures)),
            "train": int(
                (failures["split"] == "train").sum()
            ),
            "eval": int(
                (failures["split"] == "eval").sum()
            ),
        },

        "score_gap_definition": (
            "top1_score - positive_score"
        ),

        "interpretation_notes": [
            (
                "Positive rank is the position of the observed "
                "Dupe-of target within the native 101-candidate pool."
            ),
            (
                "observable_non_positive candidates are retained "
                "as candidate roles and are not interpreted as "
                "true-negative labels."
            ),
            (
                "A positive rank greater than 20 means the observed "
                "target was not retrieved in the Top-20 by this baseline."
            ),
            (
                "Score gaps are similarity-score differences, not "
                "probabilities or calibrated confidence."
            ),
            (
                "TRAIN/EVAL metric differences are descriptive and "
                "are not treated as evidence of superiority or failure "
                "without further investigation."
            ),
        ],

        "artifacts": {
            "rank_distribution": str(
                RANK_DISTRIBUTION_PATH
            ),
            "top20_failures": str(
                FAILURES_PATH
            ),
            "analysis_results": str(
                RESULTS_PATH
            ),
        },
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
    log("T6 MOD-005 — ERROR ANALYSIS SUMMARY")
    log("=" * 80)

    for split_name, summary in (
        ("TRAIN", train_summary),
        ("EVAL", eval_summary),
    ):
        log(split_name)

        log(
            f"  Queries: "
            f"{summary['queries']:,}"
        )

        log(
            f"  Recall@1: "
            f"{summary['recall_at_1']:.6f}"
        )

        log(
            f"  Recall@3: "
            f"{summary['recall_at_3']:.6f}"
        )

        log(
            f"  Recall@5: "
            f"{summary['recall_at_5']:.6f}"
        )

        log(
            f"  Recall@10: "
            f"{summary['recall_at_10']:.6f}"
        )

        log(
            f"  Recall@20: "
            f"{summary['recall_at_20']:.6f}"
        )

        log(
            f"  MRR: "
            f"{summary['mrr']:.6f}"
        )

        log(
            f"  Median positive rank: "
            f"{summary['positive_rank']['median']:.1f}"
        )

        log(
            f"  Mean positive rank: "
            f"{summary['positive_rank']['mean']:.2f}"
        )

        log(
            f"  Top-20 failures: "
            f"{summary['rank_distribution']['rank_gt_20']:,}"
        )

        log("")

    log("TRAIN → EVAL deltas:")

    for key, value in comparison.items():
        log(
            f"  {key}: {value:+.6f}"
        )

    log("")
    log(
        f"Top-20 failures total: "
        f"{len(failures):,}"
    )

    log(
        f"  TRAIN: "
        f"{int((failures['split'] == 'train').sum()):,}"
    )

    log(
        f"  EVAL: "
        f"{int((failures['split'] == 'eval').sum()):,}"
    )

    log("")
    log("Artifacts:")
    log(f"  {RANK_DISTRIBUTION_PATH}")
    log(f"  {FAILURES_PATH}")
    log(f"  {RESULTS_PATH}")

    log("")
    log("T6 MOD-005: BASELINE_ERROR_ANALYSIS_COMPLETED")

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
        print("T6 MOD-005 FAILED")
        print("=" * 80)
        print(f"{type(exc).__name__}: {exc}")
        raise