from pathlib import Path
import json

import numpy as np


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

RETRIEVAL_FILE = (
    PROJECT_ROOT
    / "modeling/T4/results/mod007_checkpoints/"
    / "t4_mod007_full_retrieval.npz"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "modeling/T4/results/"
    / "t4_mod007_similarity_analysis.json"
)


def percentile(values, q):
    return float(np.percentile(values, q))


def main():
    print("T4 MOD-007 similarity/evidence analysis")

    retrieval = np.load(
        RETRIEVAL_FILE,
        allow_pickle=True,
    )

    similarities = retrieval["neighbor_similarities"]

    if similarities.ndim != 2:
        raise RuntimeError(
            f"Expected 2D similarity matrix, got "
            f"{similarities.shape}"
        )

    rows, k = similarities.shape

    # ------------------------------------------------------------
    # Basic validation
    # ------------------------------------------------------------

    if rows != 35626:
        raise RuntimeError(
            f"Unexpected evaluation rows: {rows}"
        )

    if k != 20:
        raise RuntimeError(
            f"Unexpected neighbor count: {k}"
        )

    if not np.all(np.isfinite(similarities)):
        raise RuntimeError(
            "Non-finite similarity value detected."
        )

    # ------------------------------------------------------------
    # Per-rank similarity statistics
    # ------------------------------------------------------------

    rank_statistics = {}

    for rank in range(k):
        values = similarities[:, rank]

        rank_statistics[str(rank + 1)] = {
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "p10": percentile(values, 10),
            "p25": percentile(values, 25),
            "p75": percentile(values, 75),
            "p90": percentile(values, 90),
        }

    # ------------------------------------------------------------
    # Total similarity mass
    # ------------------------------------------------------------

    total_mass = np.sum(
        similarities,
        axis=1,
    )

    top1_mass = similarities[:, 0]

    top3_mass = np.sum(
        similarities[:, :3],
        axis=1,
    )

    top5_mass = np.sum(
        similarities[:, :5],
        axis=1,
    )

    top10_mass = np.sum(
        similarities[:, :10],
        axis=1,
    )

    mass_statistics = {
        "total_20": {
            "mean": float(np.mean(total_mass)),
            "median": float(np.median(total_mass)),
            "p10": percentile(total_mass, 10),
            "p90": percentile(total_mass, 90),
        },
        "top1": {
            "mean": float(np.mean(top1_mass)),
            "median": float(np.median(top1_mass)),
        },
        "top3": {
            "mean": float(np.mean(top3_mass)),
            "median": float(np.median(top3_mass)),
        },
        "top5": {
            "mean": float(np.mean(top5_mass)),
            "median": float(np.median(top5_mass)),
        },
        "top10": {
            "mean": float(np.mean(top10_mass)),
            "median": float(np.median(top10_mass)),
        },
    }

    # ------------------------------------------------------------
    # Concentration of similarity evidence
    # ------------------------------------------------------------

    concentration_top1 = (
        top1_mass / np.maximum(total_mass, 1e-12)
    )

    concentration_top3 = (
        top3_mass / np.maximum(total_mass, 1e-12)
    )

    concentration_top5 = (
        top5_mass / np.maximum(total_mass, 1e-12)
    )

    concentration_top10 = (
        top10_mass / np.maximum(total_mass, 1e-12)
    )

    concentration = {
        "top1_share": {
            "mean": float(np.mean(concentration_top1)),
            "median": float(np.median(concentration_top1)),
            "p10": percentile(concentration_top1, 10),
            "p90": percentile(concentration_top1, 90),
        },
        "top3_share": {
            "mean": float(np.mean(concentration_top3)),
            "median": float(np.median(concentration_top3)),
            "p10": percentile(concentration_top3, 10),
            "p90": percentile(concentration_top3, 90),
        },
        "top5_share": {
            "mean": float(np.mean(concentration_top5)),
            "median": float(np.median(concentration_top5)),
            "p10": percentile(concentration_top5, 10),
            "p90": percentile(concentration_top5, 90),
        },
        "top10_share": {
            "mean": float(np.mean(concentration_top10)),
            "median": float(np.median(concentration_top10)),
            "p10": percentile(concentration_top10, 10),
            "p90": percentile(concentration_top10, 90),
        },
    }

    # ------------------------------------------------------------
    # Similarity decay between neighboring ranks
    # ------------------------------------------------------------

    rank_decay = {}

    for rank in range(k - 1):
        current = similarities[:, rank]
        following = similarities[:, rank + 1]

        difference = current - following

        ratio = following / np.maximum(
            current,
            1e-12,
        )

        rank_decay[f"{rank + 1}_to_{rank + 2}"] = {
            "mean_absolute_drop": float(
                np.mean(difference)
            ),
            "median_drop": float(
                np.median(difference)
            ),
            "mean_relative_retention": float(
                np.mean(ratio)
            ),
            "median_relative_retention": float(
                np.median(ratio)
            ),
        }

    # ------------------------------------------------------------
    # Similarity distribution across all retrieved neighbors
    # ------------------------------------------------------------

    all_values = similarities.reshape(-1)

    global_similarity = {
        "mean": float(np.mean(all_values)),
        "median": float(np.median(all_values)),
        "min": float(np.min(all_values)),
        "max": float(np.max(all_values)),
        "p01": percentile(all_values, 1),
        "p05": percentile(all_values, 5),
        "p10": percentile(all_values, 10),
        "p25": percentile(all_values, 25),
        "p75": percentile(all_values, 75),
        "p90": percentile(all_values, 90),
        "p95": percentile(all_values, 95),
        "p99": percentile(all_values, 99),
    }

    # ------------------------------------------------------------
    # Rows with very weak retrieval evidence
    # ------------------------------------------------------------

    weak_thresholds = [
        0.00,
        0.05,
        0.10,
        0.20,
        0.30,
        0.40,
        0.50,
    ]

    weak_retrieval = {}

    for threshold in weak_thresholds:
        mask = top1_mass < threshold

        weak_retrieval[str(threshold)] = {
            "rows": int(np.sum(mask)),
            "share": float(np.mean(mask)),
        }

    # ------------------------------------------------------------
    # Effective evidence concentration
    #
    # This is a descriptive diagnostic only.
    # It does not define a new scoring rule.
    # ------------------------------------------------------------

    normalized = (
        similarities
        / np.maximum(
            total_mass[:, None],
            1e-12,
        )
    )

    effective_neighbor_count = 1.0 / np.sum(
        normalized ** 2,
        axis=1,
    )

    effective_neighbor_statistics = {
        "mean": float(
            np.mean(effective_neighbor_count)
        ),
        "median": float(
            np.median(effective_neighbor_count)
        ),
        "min": float(
            np.min(effective_neighbor_count)
        ),
        "max": float(
            np.max(effective_neighbor_count)
        ),
        "p10": percentile(
            effective_neighbor_count,
            10,
        ),
        "p90": percentile(
            effective_neighbor_count,
            90,
        ),
    }

    # ------------------------------------------------------------
    # Interpretation
    # ------------------------------------------------------------

    result = {
        "experiment": (
            "T4 MOD-007 Similarity/Evidence Distribution Analysis"
        ),
        "status": "COMPLETE",
        "retrieval": {
            "rows": int(rows),
            "neighbors_per_row": int(k),
        },
        "global_similarity": global_similarity,
        "rank_statistics": rank_statistics,
        "mass_statistics": mass_statistics,
        "similarity_concentration": concentration,
        "rank_decay": rank_decay,
        "weak_retrieval": weak_retrieval,
        "effective_neighbor_count": (
            effective_neighbor_statistics
        ),
        "interpretation": [
            "This operation descriptively analyzes the saved "
            "MOD-007 cosine-similarity evidence.",
            "It does not train a model or create new predictions.",
            "Similarity concentration indicates how much of the "
            "retrieval evidence is carried by the highest-ranked "
            "historical neighbors.",
            "Rank decay indicates how quickly similarity decreases "
            "from one retrieved neighbor to the next.",
            "Effective neighbor count summarizes how concentrated "
            "the normalized similarity mass is across the 20 "
            "retrieved neighbors.",
            "These diagnostics will be used to determine whether "
            "a rank-weighted or similarity-normalized aggregation "
            "experiment is justified.",
        ],
        "controls": {
            "raw_mozilla_accessed": False,
            "model_trained": False,
            "new_predictions_created": False,
            "test_used": False,
        },
    }

    # ------------------------------------------------------------
    # Save
    # ------------------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            indent=2,
        )

    # ------------------------------------------------------------
    # Terminal summary
    # ------------------------------------------------------------

    print()
    print("GLOBAL SIMILARITY")

    print(
        f"Mean   : {global_similarity['mean']:.6f}"
    )

    print(
        f"Median : {global_similarity['median']:.6f}"
    )

    print(
        f"P10    : {global_similarity['p10']:.6f}"
    )

    print(
        f"P90    : {global_similarity['p90']:.6f}"
    )

    print()
    print("SIMILARITY CONCENTRATION")

    print(
        f"Top-1 share  mean/median: "
        f"{concentration['top1_share']['mean']:.6f} / "
        f"{concentration['top1_share']['median']:.6f}"
    )

    print(
        f"Top-3 share  mean/median: "
        f"{concentration['top3_share']['mean']:.6f} / "
        f"{concentration['top3_share']['median']:.6f}"
    )

    print(
        f"Top-5 share  mean/median: "
        f"{concentration['top5_share']['mean']:.6f} / "
        f"{concentration['top5_share']['median']:.6f}"
    )

    print(
        f"Top-10 share mean/median: "
        f"{concentration['top10_share']['mean']:.6f} / "
        f"{concentration['top10_share']['median']:.6f}"
    )

    print()
    print("RANK DECAY")

    selected_ranks = [
        "1_to_2",
        "2_to_3",
        "5_to_6",
        "10_to_11",
        "19_to_20",
    ]

    for name in selected_ranks:
        row = rank_decay[name]

        print(
            f"{name}: "
            f"drop={row['mean_absolute_drop']:.6f}, "
            f"retention={row['mean_relative_retention']:.6f}"
        )

    print()
    print("EFFECTIVE NEIGHBOR COUNT")

    print(
        f"Mean   : "
        f"{effective_neighbor_statistics['mean']:.6f}"
    )

    print(
        f"Median : "
        f"{effective_neighbor_statistics['median']:.6f}"
    )

    print(
        f"P10    : "
        f"{effective_neighbor_statistics['p10']:.6f}"
    )

    print(
        f"P90    : "
        f"{effective_neighbor_statistics['p90']:.6f}"
    )

    print()
    print(
        f"Analysis saved: {OUTPUT_FILE}"
    )

    print("STATUS=COMPLETE")


if __name__ == "__main__":
    main()