from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# =============================================================================
# T6 VISUALIZATION
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

RESULTS_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod010_corrected_hybrid_results.json"
)

RANKINGS_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod010_corrected_hybrid_query_rankings.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "plots"
)

MANIFEST_PATH = (
    OUTPUT_DIR
    / "t6_visualization_manifest.json"
)


def save_figure(
    fig: plt.Figure,
    path: Path,
) -> None:

    fig.savefig(
        path,
        dpi=180,
        bbox_inches="tight",
    )

    plt.close(fig)


def positive_ranks(
    df: pd.DataFrame,
    score_column: str,
) -> pd.Series:

    ranks = []

    for query_id, group in df.groupby(
        "query_id",
        sort=False,
    ):

        ordered = group.sort_values(
            [score_column, "candidate_id"],
            ascending=[False, True],
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
                f"Query {query_id} does not have exactly one observed positive."
            )

        ranks.append(
            int(positive_positions[0]) + 1
        )

    return pd.Series(
        ranks,
        dtype="int64",
    )


def main() -> None:

    print("=" * 80)
    print("T6 — VISUALIZATION")
    print("=" * 80)
    print()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # =========================================================================
    # 1. LOAD COMPLETED ARTIFACTS
    # =========================================================================

    print("[1/6] Loading completed T6 artifacts...")

    with RESULTS_PATH.open(
        "r",
        encoding="utf-8",
    ) as f:
        results = json.load(f)

    rankings = pd.read_csv(
        RANKINGS_PATH
    )

    required_columns = {
        "split",
        "query_id",
        "candidate_id",
        "target_observed",
        "tfidf_score",
        "semantic_score",
        "hybrid_score",
    }

    missing = required_columns - set(
        rankings.columns
    )

    if missing:
        raise ValueError(
            f"Missing required ranking columns: {sorted(missing)}"
        )

    eval_rankings = rankings[
        rankings["split"] == "EVAL"
    ].copy()

    train_rankings = rankings[
        rankings["split"] == "TRAIN"
    ].copy()

    if len(eval_rankings) != 82_416:
        raise ValueError(
            "Unexpected EVAL row count."
        )

    if (
        eval_rankings["query_id"].nunique()
        != 816
    ):
        raise ValueError(
            "Unexpected EVAL query count."
        )

    if int(
        eval_rankings[
            "target_observed"
        ].sum()
    ) != 816:
        raise ValueError(
            "Unexpected EVAL positive count."
        )

    print(
        f"Total ranking rows: {len(rankings):,}"
    )

    print(
        f"TRAIN rows: {len(train_rankings):,}"
    )

    print(
        f"EVAL rows: {len(eval_rankings):,}"
    )

    print(
        f"EVAL queries: "
        f"{eval_rankings['query_id'].nunique():,}"
    )

    print("Artifact validation: PASS")

    metrics = results[
        "metrics"
    ][
        "eval"
    ]

    # =========================================================================
    # 2. RECALL@K
    # =========================================================================

    print()
    print("[2/6] Creating Recall@K comparison...")

    k_values = [
        1,
        3,
        5,
        10,
        20,
    ]

    tfidf_values = [
        metrics["tfidf"][
            f"recall_at_{k}"
        ]
        for k in k_values
    ]

    semantic_values = [
        metrics["semantic"][
            f"recall_at_{k}"
        ]
        for k in k_values
    ]

    hybrid_values = [
        metrics["corrected_hybrid"][
            f"recall_at_{k}"
        ]
        for k in k_values
    ]

    fig, ax = plt.subplots(
        figsize=(9, 5.5)
    )

    ax.plot(
        k_values,
        tfidf_values,
        marker="o",
        label="TF-IDF",
    )

    ax.plot(
        k_values,
        semantic_values,
        marker="o",
        label="Semantic",
    )

    ax.plot(
        k_values,
        hybrid_values,
        marker="o",
        label="Corrected Hybrid",
    )

    ax.set_xlabel(
        "K"
    )

    ax.set_ylabel(
        "Recall@K"
    )

    ax.set_title(
        "T6 EVAL — Retrieval Recall@K"
    )

    ax.set_xticks(
        k_values
    )

    ax.set_ylim(
        0,
        1,
    )

    ax.grid(
        alpha=0.25
    )

    ax.legend()

    path = (
        OUTPUT_DIR
        / "t6_recall_at_k_comparison.png"
    )

    save_figure(
        fig,
        path,
    )

    print(path)

    # =========================================================================
    # 3. FINAL METRIC COMPARISON
    # =========================================================================

    print()
    print("[3/6] Creating final metric comparison...")

    metric_labels = [
        "Recall@1",
        "Recall@3",
        "Recall@5",
        "Recall@10",
        "Recall@20",
        "MRR",
        "NDCG@5",
        "NDCG@10",
    ]

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

    x = np.arange(
        len(metric_labels)
    )

    width = 0.36

    tfidf_metric_values = [
        metrics["tfidf"][key]
        for key in metric_keys
    ]

    hybrid_metric_values = [
        metrics["corrected_hybrid"][key]
        for key in metric_keys
    ]

    fig, ax = plt.subplots(
        figsize=(12, 6)
    )

    ax.bar(
        x - width / 2,
        tfidf_metric_values,
        width,
        label="TF-IDF",
    )

    ax.bar(
        x + width / 2,
        hybrid_metric_values,
        width,
        label="Corrected Hybrid",
    )

    ax.set_xlabel(
        "Metric"
    )

    ax.set_ylabel(
        "Score"
    )

    ax.set_title(
        "T6 EVAL — Frozen TF-IDF vs Corrected Hybrid"
    )

    ax.set_xticks(
        x
    )

    ax.set_xticklabels(
        metric_labels,
        rotation=35,
        ha="right",
    )

    ax.set_ylim(
        0,
        1,
    )

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    ax.legend()

    path = (
        OUTPUT_DIR
        / "t6_final_metric_comparison.png"
    )

    save_figure(
        fig,
        path,
    )

    print(path)

    # =========================================================================
    # 4. TRAIN WEIGHT SELECTION
    # =========================================================================

    print()
    print("[4/6] Creating TRAIN hybrid-weight selection plot...")

    weight_candidates = pd.DataFrame(
        results[
            "weight_selection"
        ][
            "candidates"
        ]
    ).sort_values(
        "semantic_weight"
    )

    selected_weight = float(
        results[
            "weight_selection"
        ][
            "selected"
        ][
            "semantic_weight"
        ]
    )

    fig, ax = plt.subplots(
        figsize=(9, 5.5)
    )

    ax.plot(
        weight_candidates[
            "semantic_weight"
        ],
        weight_candidates[
            "recall_at_20"
        ],
        marker="o",
        label="Recall@20",
    )

    ax.plot(
        weight_candidates[
            "semantic_weight"
        ],
        weight_candidates[
            "mrr"
        ],
        marker="o",
        label="MRR",
    )

    ax.axvline(
        selected_weight,
        linestyle="--",
        label=(
            f"Selected semantic weight = "
            f"{selected_weight:.2f}"
        ),
    )

    ax.set_xlabel(
        "Semantic Weight"
    )

    ax.set_ylabel(
        "Metric"
    )

    ax.set_title(
        "T6 TRAIN — Hybrid Weight Selection"
    )

    ax.set_xticks(
        weight_candidates[
            "semantic_weight"
        ]
    )

    ax.set_ylim(
        0,
        1,
    )

    ax.grid(
        alpha=0.25
    )

    ax.legend()

    path = (
        OUTPUT_DIR
        / "t6_train_hybrid_weight_selection.png"
    )

    save_figure(
        fig,
        path,
    )

    print(path)

    # =========================================================================
    # 5. POSITIVE RANK DISTRIBUTION
    # =========================================================================

    print()
    print("[5/6] Creating positive-rank distribution...")

    tfidf_ranks = positive_ranks(
        eval_rankings,
        "tfidf_score",
    )

    hybrid_ranks = positive_ranks(
        eval_rankings,
        "hybrid_score",
    )

    rank_bands = [
        ("1", 1, 1),
        ("2–3", 2, 3),
        ("4–5", 4, 5),
        ("6–10", 6, 10),
        ("11–20", 11, 20),
        ("21–50", 21, 50),
        ("51–100", 51, 100),
        ("101", 101, 101),
    ]

    labels = [
        band[0]
        for band in rank_bands
    ]

    def count_bands(
        ranks: pd.Series,
    ) -> list[int]:

        counts = []

        for _, lower, upper in rank_bands:

            counts.append(
                int(
                    (
                        (ranks >= lower)
                        & (ranks <= upper)
                    ).sum()
                )
            )

        return counts

    tfidf_counts = count_bands(
        tfidf_ranks
    )

    hybrid_counts = count_bands(
        hybrid_ranks
    )

    x = np.arange(
        len(labels)
    )

    width = 0.36

    fig, ax = plt.subplots(
        figsize=(11, 5.8)
    )

    ax.bar(
        x - width / 2,
        tfidf_counts,
        width,
        label="TF-IDF",
    )

    ax.bar(
        x + width / 2,
        hybrid_counts,
        width,
        label="Corrected Hybrid",
    )

    ax.set_xlabel(
        "Rank band of observed positive"
    )

    ax.set_ylabel(
        "Number of EVAL queries"
    )

    ax.set_title(
        "T6 EVAL — Observed Positive Rank Distribution"
    )

    ax.set_xticks(
        x
    )

    ax.set_xticklabels(
        labels
    )

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    ax.legend()

    path = (
        OUTPUT_DIR
        / "t6_positive_rank_distribution.png"
    )

    save_figure(
        fig,
        path,
    )

    print(path)

    # =========================================================================
    # 6. RANK MOVEMENT
    # =========================================================================

    print()
    print("[6/6] Creating positive-rank movement plot...")

    movement = (
        tfidf_ranks.to_numpy()
        - hybrid_ranks.to_numpy()
    )

    improved = int(
        (movement > 0).sum()
    )

    worsened = int(
        (movement < 0).sum()
    )

    unchanged = int(
        (movement == 0).sum()
    )

    fig, ax = plt.subplots(
        figsize=(8.5, 5.5)
    )

    ax.bar(
        [
            "Improved",
            "Worsened",
            "Unchanged",
        ],
        [
            improved,
            worsened,
            unchanged,
        ],
    )

    ax.set_xlabel(
        "Positive-rank movement"
    )

    ax.set_ylabel(
        "Number of EVAL queries"
    )

    ax.set_title(
        "T6 EVAL — Positive-Rank Movement: TF-IDF → Corrected Hybrid"
    )

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    path = (
        OUTPUT_DIR
        / "t6_positive_rank_movement.png"
    )

    save_figure(
        fig,
        path,
    )

    print(path)

    # =========================================================================
    # MANIFEST
    # =========================================================================

    manifest = {
        "task_id": "T6",
        "visualization_only": True,

        "source_artifacts": [
            str(RESULTS_PATH),
            str(RANKINGS_PATH),
        ],

        "controls": {
            "raw_dataset_read": False,
            "model_training": False,
            "embedding_recomputation": False,
            "calibration": False,
            "threshold_optimization": False,
            "model_selection": False,
            "target_modification": False,
            "candidate_pool_modification": False,
        },

        "evaluation_population": {
            "rows": 82416,
            "queries": 816,
            "observed_positive_queries": 816,
            "candidates_per_query": 101,
        },

        "plots": [
            {
                "file": "t6_recall_at_k_comparison.png",
                "purpose": (
                    "EVAL Recall@K comparison for TF-IDF, "
                    "semantic, and corrected hybrid retrieval."
                ),
            },
            {
                "file": "t6_final_metric_comparison.png",
                "purpose": (
                    "EVAL comparison of frozen TF-IDF baseline "
                    "and corrected hybrid across retrieval metrics."
                ),
            },
            {
                "file": "t6_train_hybrid_weight_selection.png",
                "purpose": (
                    "TRAIN-only hybrid semantic-weight selection."
                ),
            },
            {
                "file": "t6_positive_rank_distribution.png",
                "purpose": (
                    "Distribution of observed-positive ranks "
                    "within the frozen EVAL candidate pools."
                ),
            },
            {
                "file": "t6_positive_rank_movement.png",
                "purpose": (
                    "EVAL query counts showing whether the observed "
                    "positive rank improved, worsened, or remained unchanged."
                ),
            },
        ],
    }

    with MANIFEST_PATH.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            manifest,
            f,
            indent=2,
        )

    print()
    print("=" * 80)
    print("T6 VISUALIZATION COMPLETED")
    print("=" * 80)
    print()
    print(
        f"Plots directory: {OUTPUT_DIR}"
    )
    print(
        f"Manifest: {MANIFEST_PATH}"
    )
    print()
    print(
        "Visualization only — no modeling state was changed."
    )


if __name__ == "__main__":
    main()