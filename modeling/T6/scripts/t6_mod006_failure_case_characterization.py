#!/usr/bin/env python3

"""
T6 — MOD-006
Failure-Case Characterization

Characterizes the T6 MOD-004 TF-IDF retrieval failures identified by
MOD-005.

Inputs:
    modeling/T6/metrics/t6_mod005_top20_failures.csv
    modeling/T6/splits/t6_train_group_aware.csv
    modeling/T6/splits/t6_eval_group_aware.csv

The split artifacts are the already-materialized modeling datasets.
No raw Mozilla CORE dataset is accessed.

Analysis:
    - failure rank distribution
    - TRAIN/EVAL failure counts
    - positive similarity score
    - Top-1 similarity score
    - Top-1 vs positive score gap
    - query/positive text length
    - lexical token overlap
    - zero-similarity cases
    - failure severity bands

No:
    - model retraining
    - TF-IDF refitting
    - calibration
    - threshold optimization
    - candidate-pool modification
    - raw dataset access
"""

from __future__ import annotations

import json
import math
import re
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

RESULTS_PATH = (
    OUTPUT_DIR
    / "t6_mod006_failure_case_characterization.json"
)

CASES_PATH = (
    OUTPUT_DIR
    / "t6_mod006_failure_cases.csv"
)

RANK_PATH = (
    OUTPUT_DIR
    / "t6_mod006_failure_rank_distribution.csv"
)

LOG_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "logs"
)

LOG_PATH = (
    LOG_DIR
    / "t6_mod006_failure_case_characterization.log"
)


# ============================================================================
# Constants
# ============================================================================

TEXT_COLUMNS = [
    "query_creator",
    "query_creator_detail",
    "query_summary",
    "query_description",
    "candidate_creator",
    "candidate_creator_detail",
    "candidate_summary",
    "candidate_description",
]

REQUIRED_FAILURE_COLUMNS = [
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

REQUIRED_MODELING_COLUMNS = [
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
# Text helpers
# ============================================================================

TOKEN_PATTERN = re.compile(
    r"[A-Za-z0-9_]+"
)


def safe_text(value: object) -> str:
    if pd.isna(value):
        return ""

    return str(value).strip()


def tokenize(text: str) -> set[str]:
    return set(
        TOKEN_PATTERN.findall(
            text.lower()
        )
    )


def combined_query_text(row: pd.Series) -> str:
    parts = [
        safe_text(row["query_creator"]),
        safe_text(row["query_creator_detail"]),
        safe_text(row["query_summary"]),
        safe_text(row["query_description"]),
    ]

    return " ".join(
        part for part in parts if part
    )


def combined_candidate_text(row: pd.Series) -> str:
    parts = [
        safe_text(row["candidate_creator"]),
        safe_text(row["candidate_creator_detail"]),
        safe_text(row["candidate_summary"]),
        safe_text(row["candidate_description"]),
    ]

    return " ".join(
        part for part in parts if part
    )


def lexical_overlap(
    query_text: str,
    candidate_text: str,
) -> tuple[int, float]:

    query_tokens = tokenize(query_text)
    candidate_tokens = tokenize(candidate_text)

    if not query_tokens:
        return 0, 0.0

    intersection = query_tokens.intersection(
        candidate_tokens
    )

    overlap_count = len(intersection)

    overlap_ratio = (
        overlap_count
        / len(query_tokens)
    )

    return overlap_count, overlap_ratio


def length_stats(text: str) -> dict:
    characters = len(text)
    tokens = TOKEN_PATTERN.findall(
        text.lower()
    )

    return {
        "characters": int(characters),
        "tokens": int(len(tokens)),
    }


# ============================================================================
# Validation
# ============================================================================

def validate_columns(
    df: pd.DataFrame,
    required: list[str],
    name: str,
) -> None:

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"{name} is missing required columns: "
            + ", ".join(missing)
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

    log("=" * 80)
    log("T6 MOD-006 — FAILURE-CASE CHARACTERIZATION")
    log("=" * 80)

    log("")
    log("Inputs:")
    log(f"  Failures: {FAILURES_PATH}")
    log(f"  TRAIN split: {TRAIN_PATH}")
    log(f"  EVAL split: {EVAL_PATH}")

    # ------------------------------------------------------------------------
    # Load failure artifact
    # ------------------------------------------------------------------------

    log("")
    log("[1/8] Loading MOD-005 Top-20 failures...")

    if not FAILURES_PATH.exists():
        raise FileNotFoundError(
            f"Failure artifact not found: {FAILURES_PATH}"
        )

    failures = pd.read_csv(
        FAILURES_PATH
    )

    validate_columns(
        failures,
        REQUIRED_FAILURE_COLUMNS,
        "MOD-005 failure artifact",
    )

    log(
        f"Failure rows loaded: {len(failures):,}"
    )

    if failures.empty:
        raise ValueError(
            "MOD-005 failure artifact is empty."
        )

    if failures["query_id"].duplicated().any():
        raise ValueError(
            "Duplicate query IDs found in failure artifact."
        )

    # ------------------------------------------------------------------------
    # Load materialized modeling data
    # ------------------------------------------------------------------------

    log("")
    log("[2/8] Loading materialized T6 modeling splits...")

    if not TRAIN_PATH.exists():
        raise FileNotFoundError(
            f"TRAIN artifact not found: {TRAIN_PATH}"
        )

    if not EVAL_PATH.exists():
        raise FileNotFoundError(
            f"EVAL artifact not found: {EVAL_PATH}"
        )

    train = pd.read_csv(
        TRAIN_PATH
    )

    evaluation = pd.read_csv(
        EVAL_PATH
    )

    validate_columns(
        train,
        REQUIRED_MODELING_COLUMNS,
        "TRAIN modeling artifact",
    )

    validate_columns(
        evaluation,
        REQUIRED_MODELING_COLUMNS,
        "EVAL modeling artifact",
    )

    log(
        f"TRAIN rows loaded: {len(train):,}"
    )

    log(
        f"EVAL rows loaded: {len(evaluation):,}"
    )

    # ------------------------------------------------------------------------
    # Validate failure split accounting
    # ------------------------------------------------------------------------

    log("")
    log("[3/8] Validating failure-to-split accounting...")

    failure_splits = set(
        failures["split"].astype(str)
    )

    if not failure_splits.issubset(
        {"train", "eval"}
    ):
        raise ValueError(
            "Unexpected failure split values: "
            + repr(
                sorted(
                    failure_splits
                    - {"train", "eval"}
                )
            )
        )

    train_failures = failures[
        failures["split"] == "train"
    ].copy()

    eval_failures = failures[
        failures["split"] == "eval"
    ].copy()

    log(
        f"TRAIN failures: {len(train_failures):,}"
    )

    log(
        f"EVAL failures: {len(eval_failures):,}"
    )

    log(
        f"Total failures: {len(failures):,}"
    )

    # ------------------------------------------------------------------------
    # Construct compact query/candidate lookup
    # ------------------------------------------------------------------------

    log("")
    log("[4/8] Constructing query/candidate lookup...")

    # Only rows referenced by the failure artifact are retained.
    # This keeps the analysis bounded and avoids unnecessary processing.

    failure_query_ids = set(
        failures["query_id"].astype(str)
    )

    failure_candidate_ids = set(
        failures["positive_candidate_id"]
        .astype(str)
    )

    train["query_id"] = (
        train["query_id"].astype(str)
    )

    train["candidate_id"] = (
        train["candidate_id"].astype(str)
    )

    evaluation["query_id"] = (
        evaluation["query_id"].astype(str)
    )

    evaluation["candidate_id"] = (
        evaluation["candidate_id"].astype(str)
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

    relevant = pd.concat(
        [
            train_relevant,
            eval_relevant,
        ],
        ignore_index=True,
    )

    if relevant.empty:
        raise ValueError(
            "No failure queries were found in the modeling splits."
        )

    log(
        f"Relevant modeling rows: {len(relevant):,}"
    )

    # ------------------------------------------------------------------------
    # Build failure-level cases
    # ------------------------------------------------------------------------

    log("")
    log("[5/8] Characterizing individual failure cases...")

    case_rows: list[dict] = []

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

        query_rows = split_df[
            split_df["query_id"] == query_id
        ]

        if query_rows.empty:
            raise ValueError(
                f"Failure query not found in {split}: "
                f"{query_id}"
            )

        # There should be 101 candidate rows per query.
        if len(query_rows) != 101:
            raise ValueError(
                f"Expected 101 candidates for query "
                f"{query_id}, found {len(query_rows)}."
            )

        positive_rows = query_rows[
            query_rows["candidate_id"]
            == positive_candidate_id
        ]

        if len(positive_rows) != 1:
            raise ValueError(
                f"Expected exactly one positive candidate "
                f"for query {query_id}; found "
                f"{len(positive_rows)}."
            )

        positive = positive_rows.iloc[0]

        query_text = combined_query_text(
            positive
        )

        candidate_text = combined_candidate_text(
            positive
        )

        query_lengths = length_stats(
            query_text
        )

        candidate_lengths = length_stats(
            candidate_text
        )

        overlap_count, overlap_ratio = lexical_overlap(
            query_text,
            candidate_text,
        )

        positive_score = float(
            failure.positive_score
        )

        top_score = float(
            failure.top_score
        )

        score_gap = float(
            failure.score_gap_top1_minus_positive
        )

        # --------------------------------------------------------------------
        # Failure severity
        # --------------------------------------------------------------------

        positive_rank = int(
            failure.positive_rank
        )

        if positive_rank > 100:
            rank_band = "101"
        elif positive_rank > 75:
            rank_band = "76-100"
        elif positive_rank > 50:
            rank_band = "51-75"
        elif positive_rank > 20:
            rank_band = "21-50"
        else:
            rank_band = "unexpected"

        # --------------------------------------------------------------------
        # Zero-similarity diagnostics
        # --------------------------------------------------------------------

        positive_zero_similarity = (
            math.isclose(
                positive_score,
                0.0,
                abs_tol=1e-12,
            )
        )

        query_empty = (
            query_lengths["tokens"] == 0
        )

        candidate_empty = (
            candidate_lengths["tokens"] == 0
        )

        case_rows.append(
            {
                "split": split,
                "query_id": query_id,
                "positive_candidate_id": (
                    positive_candidate_id
                ),
                "positive_rank": positive_rank,
                "rank_band": rank_band,

                "top_candidate_id": str(
                    failure.top_candidate_id
                ),

                "top_candidate_role": str(
                    failure.top_candidate_role
                ),

                "top_score": top_score,
                "positive_score": positive_score,
                "score_gap_top1_minus_positive": score_gap,

                "query_characters": (
                    query_lengths["characters"]
                ),

                "query_tokens": (
                    query_lengths["tokens"]
                ),

                "candidate_characters": (
                    candidate_lengths["characters"]
                ),

                "candidate_tokens": (
                    candidate_lengths["tokens"]
                ),

                "lexical_overlap_tokens": (
                    overlap_count
                ),

                "query_token_overlap_ratio": (
                    overlap_ratio
                ),

                "positive_similarity_zero": (
                    positive_zero_similarity
                ),

                "query_text_empty": (
                    query_empty
                ),

                "candidate_text_empty": (
                    candidate_empty
                ),

                "query_creation_time": str(
                    positive["query_creation_time"]
                ),

                "candidate_creation_time": str(
                    positive["candidate_creation_time"]
                ),

                "target_observed": str(
                    positive["target_observed"]
                ),

                "target_type": str(
                    positive["target_type"]
                ),
            }
        )

    cases = pd.DataFrame(
        case_rows
    )

    # ------------------------------------------------------------------------
    # Save case-level artifact
    # ------------------------------------------------------------------------

    log("")
    log("[6/8] Saving case-level diagnostics...")

    cases = cases.sort_values(
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

    cases.to_csv(
        CASES_PATH,
        index=False,
    )

    # ------------------------------------------------------------------------
    # Rank distribution
    # ------------------------------------------------------------------------

    rank_rows: list[dict] = []

    rank_bands = [
        ("21-50", 21, 50),
        ("51-75", 51, 75),
        ("76-100", 76, 100),
        ("101", 101, 101),
    ]

    for split_name in ["train", "eval", "all"]:

        if split_name == "all":
            frame = cases
        else:
            frame = cases[
                cases["split"] == split_name
            ]

        total = len(frame)

        for label, lower, upper in rank_bands:

            count = int(
                (
                    (frame["positive_rank"] >= lower)
                    & (frame["positive_rank"] <= upper)
                ).sum()
            )

            rank_rows.append(
                {
                    "split": split_name,
                    "rank_band": label,
                    "count": count,
                    "proportion_of_failures": (
                        float(count / total)
                        if total
                        else None
                    ),
                }
            )

    rank_distribution = pd.DataFrame(
        rank_rows
    )

    rank_distribution.to_csv(
        RANK_PATH,
        index=False,
    )

    # ------------------------------------------------------------------------
    # Aggregate diagnostics
    # ------------------------------------------------------------------------

    log("")
    log("[7/8] Building aggregate failure diagnostics...")

    def aggregate(frame: pd.DataFrame) -> dict:

        total = len(frame)

        if total == 0:
            return {
                "failures": 0
            }

        return {
            "failures": int(total),

            "positive_rank": {
                "minimum": int(
                    frame["positive_rank"].min()
                ),
                "median": float(
                    frame["positive_rank"].median()
                ),
                "mean": float(
                    frame["positive_rank"].mean()
                ),
                "maximum": int(
                    frame["positive_rank"].max()
                ),
            },

            "score_gap": {
                "mean": float(
                    frame[
                        "score_gap_top1_minus_positive"
                    ].mean()
                ),
                "median": float(
                    frame[
                        "score_gap_top1_minus_positive"
                    ].median()
                ),
                "minimum": float(
                    frame[
                        "score_gap_top1_minus_positive"
                    ].min()
                ),
                "maximum": float(
                    frame[
                        "score_gap_top1_minus_positive"
                    ].max()
                ),
            },

            "positive_score": {
                "mean": float(
                    frame["positive_score"].mean()
                ),
                "median": float(
                    frame["positive_score"].median()
                ),
                "minimum": float(
                    frame["positive_score"].min()
                ),
                "maximum": float(
                    frame["positive_score"].max()
                ),
            },

            "top1_score": {
                "mean": float(
                    frame["top_score"].mean()
                ),
                "median": float(
                    frame["top_score"].median()
                ),
                "minimum": float(
                    frame["top_score"].min()
                ),
                "maximum": float(
                    frame["top_score"].max()
                ),
            },

            "query_length": {
                "mean_characters": float(
                    frame["query_characters"].mean()
                ),
                "median_characters": float(
                    frame["query_characters"].median()
                ),
                "mean_tokens": float(
                    frame["query_tokens"].mean()
                ),
                "median_tokens": float(
                    frame["query_tokens"].median()
                ),
            },

            "candidate_length": {
                "mean_characters": float(
                    frame["candidate_characters"].mean()
                ),
                "median_characters": float(
                    frame["candidate_characters"].median()
                ),
                "mean_tokens": float(
                    frame["candidate_tokens"].mean()
                ),
                "median_tokens": float(
                    frame["candidate_tokens"].median()
                ),
            },

            "lexical_overlap": {
                "mean_shared_tokens": float(
                    frame[
                        "lexical_overlap_tokens"
                    ].mean()
                ),
                "median_shared_tokens": float(
                    frame[
                        "lexical_overlap_tokens"
                    ].median()
                ),
                "mean_query_overlap_ratio": float(
                    frame[
                        "query_token_overlap_ratio"
                    ].mean()
                ),
                "median_query_overlap_ratio": float(
                    frame[
                        "query_token_overlap_ratio"
                    ].median()
                ),
            },

            "zero_similarity": {
                "count": int(
                    frame[
                        "positive_similarity_zero"
                    ].sum()
                ),
                "rate": float(
                    frame[
                        "positive_similarity_zero"
                    ].mean()
                ),
            },

            "empty_text": {
                "query_empty": int(
                    frame["query_text_empty"].sum()
                ),
                "query_empty_rate": float(
                    frame["query_text_empty"].mean()
                ),
                "candidate_empty": int(
                    frame["candidate_text_empty"].sum()
                ),
                "candidate_empty_rate": float(
                    frame["candidate_text_empty"].mean()
                ),
            },

            "rank_bands": {
                "21-50": int(
                    (
                        (frame["positive_rank"] >= 21)
                        & (frame["positive_rank"] <= 50)
                    ).sum()
                ),
                "51-75": int(
                    (
                        (frame["positive_rank"] >= 51)
                        & (frame["positive_rank"] <= 75)
                    ).sum()
                ),
                "76-100": int(
                    (
                        (frame["positive_rank"] >= 76)
                        & (frame["positive_rank"] <= 100)
                    ).sum()
                ),
                "101": int(
                    (
                        frame["positive_rank"] == 101
                    ).sum()
                ),
            },
        }

    train_diag = aggregate(
        cases[
            cases["split"] == "train"
        ]
    )

    eval_diag = aggregate(
        cases[
            cases["split"] == "eval"
        ]
    )

    all_diag = aggregate(
        cases
    )

    # ------------------------------------------------------------------------
    # Compare TRAIN vs EVAL failures
    # ------------------------------------------------------------------------

    comparison = {}

    if (
        train_diag["failures"] > 0
        and eval_diag["failures"] > 0
    ):

        comparison = {
            "failure_count_eval_minus_train": (
                eval_diag["failures"]
                - train_diag["failures"]
            ),

            "mean_failure_rank_eval_minus_train": (
                eval_diag["positive_rank"]["mean"]
                - train_diag["positive_rank"]["mean"]
            ),

            "median_failure_rank_eval_minus_train": (
                eval_diag["positive_rank"]["median"]
                - train_diag["positive_rank"]["median"]
            ),

            "mean_score_gap_eval_minus_train": (
                eval_diag["score_gap"]["mean"]
                - train_diag["score_gap"]["mean"]
            ),

            "mean_positive_score_eval_minus_train": (
                eval_diag["positive_score"]["mean"]
                - train_diag["positive_score"]["mean"]
            ),

            "mean_query_tokens_eval_minus_train": (
                eval_diag["query_length"]["mean_tokens"]
                - train_diag["query_length"]["mean_tokens"]
            ),

            "mean_candidate_tokens_eval_minus_train": (
                eval_diag["candidate_length"]["mean_tokens"]
                - train_diag["candidate_length"]["mean_tokens"]
            ),

            "mean_lexical_overlap_eval_minus_train": (
                eval_diag["lexical_overlap"][
                    "mean_shared_tokens"
                ]
                - train_diag["lexical_overlap"][
                    "mean_shared_tokens"
                ]
            ),
        }

    # ------------------------------------------------------------------------
    # Save final result
    # ------------------------------------------------------------------------

    results = {
        "operation": "T6 MOD-006",
        "task": "T6 Similar-Ticket Retrieval",
        "task_formulation": (
            "Duplicate-Related Ticket Retrieval"
        ),
        "status": "FAILURE_CASE_CHARACTERIZATION_COMPLETED",

        "inputs": {
            "mod005_failures": str(
                FAILURES_PATH
            ),
            "train_modeling_split": str(
                TRAIN_PATH
            ),
            "eval_modeling_split": str(
                EVAL_PATH
            ),
        },

        "controls": {
            "model_retrained": False,
            "vectorizer_refit": False,
            "raw_dataset_read": False,
            "accepted_dtm_artifact_read": False,
            "candidate_pool_modified": False,
            "ranking_artifact_modified": False,
            "calibration_performed": False,
            "threshold_optimization": False,
        },

        "failure_population": {
            "total": int(len(cases)),
            "train": int(
                (cases["split"] == "train").sum()
            ),
            "eval": int(
                (cases["split"] == "eval").sum()
            ),
        },

        "all_failures": all_diag,
        "train_failures": train_diag,
        "eval_failures": eval_diag,

        "train_eval_failure_comparison": comparison,

        "interpretation_notes": [
            (
                "Failure cases are queries whose observed Dupe-of target "
                "ranked below Top-20 under the MOD-004 TF-IDF baseline."
            ),
            (
                "Similarity scores are native cosine-similarity scores "
                "and are not probabilities or calibrated confidence."
            ),
            (
                "Lexical overlap is a descriptive diagnostic and is not "
                "treated as a duplicate ground-truth signal."
            ),
            (
                "Observable non-positive candidates are not converted "
                "into true-negative labels."
            ),
            (
                "Failure characteristics are descriptive and do not "
                "establish causality."
            ),
            (
                "TRAIN/EVAL differences are recorded for characterization "
                "and do not constitute a model-selection claim."
            ),
        ],

        "artifacts": {
            "failure_cases": str(
                CASES_PATH
            ),
            "rank_distribution": str(
                RANK_PATH
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
    # Console summary
    # ------------------------------------------------------------------------

    log("")
    log("=" * 80)
    log("T6 MOD-006 — FAILURE CHARACTERIZATION SUMMARY")
    log("=" * 80)

    for name, diagnostics in (
        ("TRAIN", train_diag),
        ("EVAL", eval_diag),
        ("ALL", all_diag),
    ):

        log("")
        log(name)

        log(
            f"  Failures: "
            f"{diagnostics['failures']:,}"
        )

        if diagnostics["failures"] == 0:
            continue

        log(
            f"  Positive rank mean: "
            f"{diagnostics['positive_rank']['mean']:.2f}"
        )

        log(
            f"  Positive rank median: "
            f"{diagnostics['positive_rank']['median']:.1f}"
        )

        log(
            f"  Positive rank max: "
            f"{diagnostics['positive_rank']['maximum']}"
        )

        log(
            f"  Mean positive score: "
            f"{diagnostics['positive_score']['mean']:.6f}"
        )

        log(
            f"  Mean Top-1 score: "
            f"{diagnostics['top1_score']['mean']:.6f}"
        )

        log(
            f"  Mean Top-1-positive score gap: "
            f"{diagnostics['score_gap']['mean']:.6f}"
        )

        log(
            f"  Mean query tokens: "
            f"{diagnostics['query_length']['mean_tokens']:.2f}"
        )

        log(
            f"  Mean candidate tokens: "
            f"{diagnostics['candidate_length']['mean_tokens']:.2f}"
        )

        log(
            f"  Mean shared lexical tokens: "
            f"{diagnostics['lexical_overlap']['mean_shared_tokens']:.2f}"
        )

        log(
            f"  Zero-similarity positives: "
            f"{diagnostics['zero_similarity']['count']:,} "
            f"("
            f"{diagnostics['zero_similarity']['rate']:.2%}"
            f")"
        )

        log(
            "  Rank bands:"
        )

        for band in [
            "21-50",
            "51-75",
            "76-100",
            "101",
        ]:
            log(
                f"    {band}: "
                f"{diagnostics['rank_bands'][band]:,}"
            )

    log("")
    log("Artifacts:")
    log(f"  {CASES_PATH}")
    log(f"  {RANK_PATH}")
    log(f"  {RESULTS_PATH}")

    log("")
    log(
        "T6 MOD-006: "
        "FAILURE_CASE_CHARACTERIZATION_COMPLETED"
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
        print("T6 MOD-006 FAILED")
        print("=" * 80)
        print(
            f"{type(exc).__name__}: {exc}"
        )
        raise