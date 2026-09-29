from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]

MOD004_PATH = (
    PROJECT_ROOT / "modeling" / "T6" / "metrics"
    / "t6_mod004_query_rankings.csv"
)

MOD009_PATH = (
    PROJECT_ROOT / "modeling" / "T6" / "metrics"
    / "t6_mod009_hybrid_query_rankings.csv"
)

OUTPUT_REPORT = (
    PROJECT_ROOT / "modeling" / "T6" / "metrics"
    / "t6_mod010_tfidf_reproducibility_report.json"
)

OUTPUT_MISMATCHES = (
    PROJECT_ROOT / "modeling" / "T6" / "metrics"
    / "t6_mod010_tfidf_query_mismatches.csv"
)


def require_columns(
    df: pd.DataFrame,
    columns: list[str],
    name: str,
) -> None:

    missing = [c for c in columns if c not in df.columns]

    if missing:
        raise ValueError(
            f"{name}: missing required columns: {missing}"
        )


def normalize_bool(series: pd.Series) -> pd.Series:

    values = []

    for value in series:

        if isinstance(value, (bool, np.bool_)):
            values.append(bool(value))

        elif isinstance(value, (int, np.integer)):
            if int(value) in (0, 1):
                values.append(bool(int(value)))
            else:
                raise ValueError(
                    f"Unexpected integer target value: {value}"
                )

        elif isinstance(value, str):
            value = value.strip().lower()

            if value in {"true", "1"}:
                values.append(True)
            elif value in {"false", "0"}:
                values.append(False)
            else:
                raise ValueError(
                    f"Unexpected string target value: {value!r}"
                )

        else:
            raise ValueError(
                f"Unexpected target value: {value!r}"
            )

    return pd.Series(
        values,
        index=series.index,
        dtype=bool,
    )


def reconstruct_query_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:

    records = []

    for query_id, group in df.groupby(
        "query_id",
        sort=False,
    ):

        ordered = group.sort_values(
            ["tfidf_score", "candidate_id"],
            ascending=[False, True],
            kind="mergesort",
        ).reset_index(drop=True)

        positives = ordered[
            ordered["target_observed"]
        ]

        if len(positives) != 1:
            raise ValueError(
                f"Query {query_id} has "
                f"{len(positives)} observed positives."
            )

        positive_position = int(
            np.flatnonzero(
                ordered["target_observed"].to_numpy(dtype=bool)
            )[0]
        )

        positive_row = ordered.iloc[positive_position]
        top_row = ordered.iloc[0]

        records.append(
            {
                "query_id": query_id,
                "positive_candidate_id_reconstructed": int(
                    positive_row["candidate_id"]
                ),
                "positive_rank_reconstructed": (
                    positive_position + 1
                ),
                "top_candidate_id_reconstructed": int(
                    top_row["candidate_id"]
                ),
                "top_candidate_role_reconstructed": (
                    "positive"
                    if bool(top_row["target_observed"])
                    else "observable_non_positive"
                ),
                "top_score_reconstructed": float(
                    top_row["tfidf_score"]
                ),
                "positive_score_reconstructed": float(
                    positive_row["tfidf_score"]
                ),
            }
        )

    return pd.DataFrame(records)


def main() -> None:

    print("=" * 80)
    print("T6 MOD-010 — TF-IDF REPRODUCIBILITY / INTEGRITY CHECK")
    print("=" * 80)
    print()

    # -------------------------------------------------------------------------
    # 1. Load
    # -------------------------------------------------------------------------

    print("[1/6] Loading MOD-004 and MOD-009 artifacts...")

    mod004 = pd.read_csv(MOD004_PATH)
    mod009 = pd.read_csv(MOD009_PATH)

    print(f"MOD-004 rows: {len(mod004):,}")
    print(f"MOD-009 rows: {len(mod009):,}")

    # -------------------------------------------------------------------------
    # 2. Validate
    # -------------------------------------------------------------------------

    print()
    print("[2/6] Validating schemas and query populations...")

    require_columns(
        mod004,
        [
            "split",
            "query_id",
            "positive_candidate_id",
            "positive_rank",
            "top_candidate_id",
            "top_candidate_role",
            "top_score",
            "positive_score",
        ],
        "MOD-004",
    )

    require_columns(
        mod009,
        [
            "split",
            "query_id",
            "candidate_id",
            "target_observed",
            "tfidf_score",
        ],
        "MOD-009",
    )

    mod009["target_observed"] = normalize_bool(
        mod009["target_observed"]
    )

    mod004_queries = set(mod004["query_id"])
    mod009_queries = set(mod009["query_id"])

    only_mod004 = mod004_queries - mod009_queries
    only_mod009 = mod009_queries - mod004_queries

    print(f"MOD-004 queries: {len(mod004_queries):,}")
    print(f"MOD-009 queries: {len(mod009_queries):,}")
    print(f"Queries only in MOD-004: {len(only_mod004):,}")
    print(f"Queries only in MOD-009: {len(only_mod009):,}")

    if only_mod004 or only_mod009:
        raise ValueError(
            "Query populations differ."
        )

    if len(mod004) != len(mod004_queries):
        raise ValueError(
            "MOD-004 is not exactly one row per query."
        )

    # -------------------------------------------------------------------------
    # 3. Reconstruct
    # -------------------------------------------------------------------------

    print()
    print(
        "[3/6] Reconstructing query-level TF-IDF results "
        "from MOD-009..."
    )

    reconstructed = reconstruct_query_summary(mod009)

    print(
        f"Reconstructed query summaries: "
        f"{len(reconstructed):,}"
    )

    # -------------------------------------------------------------------------
    # 4. Compare
    # -------------------------------------------------------------------------

    print()
    print(
        "[4/6] Comparing original and reconstructed rankings..."
    )

    original = mod004[
        [
            "split",
            "query_id",
            "positive_candidate_id",
            "positive_rank",
            "top_candidate_id",
            "top_candidate_role",
            "top_score",
            "positive_score",
        ]
    ].copy()

    comparison = original.merge(
        reconstructed,
        on="query_id",
        how="inner",
        validate="one_to_one",
    )

    comparison["positive_candidate_match"] = (
        comparison["positive_candidate_id"]
        ==
        comparison["positive_candidate_id_reconstructed"]
    )

    comparison["positive_rank_match"] = (
        comparison["positive_rank"]
        ==
        comparison["positive_rank_reconstructed"]
    )

    comparison["top_candidate_match"] = (
        comparison["top_candidate_id"]
        ==
        comparison["top_candidate_id_reconstructed"]
    )

    comparison["top_role_match"] = (
        comparison["top_candidate_role"]
        ==
        comparison["top_candidate_role_reconstructed"]
    )

    comparison["top_score_difference"] = (
        comparison["top_score_reconstructed"]
        -
        comparison["top_score"]
    )

    comparison["positive_score_difference"] = (
        comparison["positive_score_reconstructed"]
        -
        comparison["positive_score"]
    )

    comparison["absolute_top_score_difference"] = (
        comparison["top_score_difference"].abs()
    )

    comparison["absolute_positive_score_difference"] = (
        comparison["positive_score_difference"].abs()
    )

    comparison["rank_difference"] = (
        comparison["positive_rank_reconstructed"]
        -
        comparison["positive_rank"]
    )

    ranking_identity_changed = (
        ~comparison["positive_candidate_match"]
        |
        ~comparison["positive_rank_match"]
        |
        ~comparison["top_candidate_match"]
        |
        ~comparison["top_role_match"]
    )

    score_changed = (
        (
            comparison["absolute_top_score_difference"]
            > 1e-12
        )
        |
        (
            comparison["absolute_positive_score_difference"]
            > 1e-12
        )
    )

    print(
        f"Positive candidate mismatches: "
        f"{int((~comparison['positive_candidate_match']).sum()):,}"
    )

    print(
        f"Positive rank mismatches: "
        f"{int((~comparison['positive_rank_match']).sum()):,}"
    )

    print(
        f"Top candidate mismatches: "
        f"{int((~comparison['top_candidate_match']).sum()):,}"
    )

    print(
        f"Top candidate role mismatches: "
        f"{int((~comparison['top_role_match']).sum()):,}"
    )

    print()
    print("Score differences:")

    print(
        f"  Mean absolute top-score difference: "
        f"{comparison['absolute_top_score_difference'].mean():.12g}"
    )

    print(
        f"  Median absolute top-score difference: "
        f"{comparison['absolute_top_score_difference'].median():.12g}"
    )

    print(
        f"  Maximum absolute top-score difference: "
        f"{comparison['absolute_top_score_difference'].max():.12g}"
    )

    print(
        f"  Mean absolute positive-score difference: "
        f"{comparison['absolute_positive_score_difference'].mean():.12g}"
    )

    print(
        f"  Median absolute positive-score difference: "
        f"{comparison['absolute_positive_score_difference'].median():.12g}"
    )

    print(
        f"  Maximum absolute positive-score difference: "
        f"{comparison['absolute_positive_score_difference'].max():.12g}"
    )

    print()
    print("Rank differences:")

    print(
        f"  Mean absolute rank difference: "
        f"{comparison['rank_difference'].abs().mean():.6f}"
    )

    print(
        f"  Maximum absolute rank difference: "
        f"{comparison['rank_difference'].abs().max():.0f}"
    )

    # -------------------------------------------------------------------------
    # 5. Failure sets
    # -------------------------------------------------------------------------

    print()
    print("[5/6] Comparing Top-20 failure sets...")

    original_failures = set(
        comparison.loc[
            comparison["positive_rank"] > 20,
            "query_id",
        ]
    )

    reconstructed_failures = set(
        comparison.loc[
            comparison["positive_rank_reconstructed"] > 20,
            "query_id",
        ]
    )

    common_failures = (
        original_failures
        &
        reconstructed_failures
    )

    original_only_failures = (
        original_failures
        -
        reconstructed_failures
    )

    reconstructed_only_failures = (
        reconstructed_failures
        -
        original_failures
    )

    print(
        f"MOD-004 Top-20 failures: "
        f"{len(original_failures)}"
    )

    print(
        f"MOD-009 reconstructed failures: "
        f"{len(reconstructed_failures)}"
    )

    print(
        f"Common failures: "
        f"{len(common_failures)}"
    )

    print(
        f"MOD-004 only: "
        f"{len(original_only_failures)}"
    )

    print(
        f"MOD-009 only: "
        f"{len(reconstructed_only_failures)}"
    )

    # -------------------------------------------------------------------------
    # 6. Save
    # -------------------------------------------------------------------------

    print()
    print("[6/6] Saving reproducibility report...")

    mismatches = comparison[
        ranking_identity_changed
        |
        score_changed
    ].copy()

    mismatches.to_csv(
        OUTPUT_MISMATCHES,
        index=False,
    )

    report = {
        "task_id": "T6",
        "operation_id": "MOD-010",
        "operation_name": (
            "TF-IDF Reproducibility / Integrity Check"
        ),
        "status": "COMPLETED",

        "population": {
            "mod004_rows": int(len(mod004)),
            "mod009_rows": int(len(mod009)),
            "mod004_queries": int(len(mod004_queries)),
            "mod009_queries": int(len(mod009_queries)),
            "queries_only_mod004": int(len(only_mod004)),
            "queries_only_mod009": int(len(only_mod009)),
        },

        "ranking_identity": {
            "positive_candidate_mismatches": int(
                (~comparison["positive_candidate_match"]).sum()
            ),
            "positive_rank_mismatches": int(
                (~comparison["positive_rank_match"]).sum()
            ),
            "top_candidate_mismatches": int(
                (~comparison["top_candidate_match"]).sum()
            ),
            "top_role_mismatches": int(
                (~comparison["top_role_match"]).sum()
            ),
            "queries_with_ranking_identity_change": int(
                ranking_identity_changed.sum()
            ),
        },

        "score_difference": {
            "mean_absolute_top_score_difference": float(
                comparison[
                    "absolute_top_score_difference"
                ].mean()
            ),
            "median_absolute_top_score_difference": float(
                comparison[
                    "absolute_top_score_difference"
                ].median()
            ),
            "max_absolute_top_score_difference": float(
                comparison[
                    "absolute_top_score_difference"
                ].max()
            ),
            "mean_absolute_positive_score_difference": float(
                comparison[
                    "absolute_positive_score_difference"
                ].mean()
            ),
            "median_absolute_positive_score_difference": float(
                comparison[
                    "absolute_positive_score_difference"
                ].median()
            ),
            "max_absolute_positive_score_difference": float(
                comparison[
                    "absolute_positive_score_difference"
                ].max()
            ),
            "queries_with_score_difference": int(
                score_changed.sum()
            ),
        },

        "rank_difference": {
            "mean_absolute_rank_difference": float(
                comparison[
                    "rank_difference"
                ].abs().mean()
            ),
            "max_absolute_rank_difference": int(
                comparison[
                    "rank_difference"
                ].abs().max()
            ),
        },

        "top20_failure_sets": {
            "mod004": int(len(original_failures)),
            "mod009_reconstructed": int(
                len(reconstructed_failures)
            ),
            "common": int(len(common_failures)),
            "mod004_only": int(
                len(original_only_failures)
            ),
            "mod009_only": int(
                len(reconstructed_only_failures)
            ),
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
            "report": str(OUTPUT_REPORT),
            "mismatches": str(OUTPUT_MISMATCHES),
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
    print(f"  {OUTPUT_REPORT}")
    print(f"  {OUTPUT_MISMATCHES}")

    print()
    print("=" * 80)
    print("T6 MOD-010: REPRODUCIBILITY_CHECK_COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()