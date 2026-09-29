from pathlib import Path
import json

import numpy as np
import pandas as pd


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

TRAIN_FILE = (
    PROJECT_ROOT / "modeling/T4/derived/t4_train.csv"
)

EVAL_FILE = (
    PROJECT_ROOT / "modeling/T4/derived/t4_eval.csv"
)

RETRIEVAL_FILE = (
    PROJECT_ROOT
    / "modeling/T4/results/mod007_checkpoints/"
    / "t4_mod007_full_retrieval.npz"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "modeling/T4/results/t4_mod007_retrieval_analysis.json"
)


def main():
    print("T4 MOD-007 retrieval structure analysis")

    # ------------------------------------------------------------
    # Load frozen training/evaluation artifacts and retrieval
    # checkpoint used by MOD-007.
    # ------------------------------------------------------------

    train = pd.read_csv(TRAIN_FILE)
    evaluation = pd.read_csv(EVAL_FILE)

    retrieval = np.load(
        RETRIEVAL_FILE,
        allow_pickle=True,
    )

    neighbor_indices = retrieval["neighbor_indices"]
    neighbor_similarities = retrieval["neighbor_similarities"]

    train_targets = (
        train["target_assignee"]
        .astype(str)
        .to_numpy()
    )

    eval_targets = (
        evaluation["target_assignee"]
        .astype(str)
        .to_numpy()
    )

    # ------------------------------------------------------------
    # Structural validation
    # ------------------------------------------------------------

    if len(train) != 142501:
        raise RuntimeError(
            f"Unexpected training rows: {len(train)}"
        )

    if len(evaluation) != 35626:
        raise RuntimeError(
            f"Unexpected evaluation rows: {len(evaluation)}"
        )

    if neighbor_indices.shape != (35626, 20):
        raise RuntimeError(
            "Unexpected neighbor index shape: "
            f"{neighbor_indices.shape}"
        )

    if neighbor_similarities.shape != (35626, 20):
        raise RuntimeError(
            "Unexpected similarity shape: "
            f"{neighbor_similarities.shape}"
        )

    if np.min(neighbor_indices) < 0:
        raise RuntimeError(
            "Negative training index found."
        )

    if np.max(neighbor_indices) >= len(train):
        raise RuntimeError(
            "Neighbor index exceeds training population."
        )

    print()
    print("STRUCTURAL VALIDATION")
    print(f"Training rows       : {len(train)}")
    print(f"Evaluation rows     : {len(evaluation)}")
    print(
        f"Neighbor index shape: "
        f"{neighbor_indices.shape}"
    )
    print(
        f"Similarity shape    : "
        f"{neighbor_similarities.shape}"
    )

    # ------------------------------------------------------------
    # Per-row retrieval analysis
    # ------------------------------------------------------------

    unique_assignee_counts = []
    winner_neighbor_counts = []
    winner_similarity_masses = []
    winner_top_similarities = []

    top_neighbor_matches = []
    aggregation_matches = []

    winner_changed = []

    # ------------------------------------------------------------
    # Analyze every evaluation ticket
    # ------------------------------------------------------------

    for row_idx in range(len(evaluation)):
        indices = neighbor_indices[row_idx]
        similarities = neighbor_similarities[row_idx]

        assignees = train_targets[indices]

        target = eval_targets[row_idx]

        unique_assignee_counts.append(
            len(np.unique(assignees))
        )

        # --------------------------------------------------------
        # Strongest individual historical neighbor
        # --------------------------------------------------------

        top_neighbor_assignee = assignees[0]

        top_neighbor_matches.append(
            top_neighbor_assignee == target
        )

        # --------------------------------------------------------
        # Reproduce MOD-007's exact aggregation:
        #
        # score(assignee) =
        #     sum(similarity of retrieved tickets handled
        #         by that assignee)
        # --------------------------------------------------------

        scores = {}

        for assignee, similarity in zip(
            assignees,
            similarities,
        ):
            scores[assignee] = (
                scores.get(assignee, 0.0)
                + float(similarity)
            )

        ranked = sorted(
            scores.items(),
            key=lambda item: (
                -item[1],
                item[0],
            ),
        )

        winner = ranked[0][0]

        aggregation_matches.append(
            winner == target
        )

        changed = (
            winner != top_neighbor_assignee
        )

        winner_changed.append(changed)

        # --------------------------------------------------------
        # Evidence contributed by winning assignee
        # --------------------------------------------------------

        winner_mask = assignees == winner

        winner_count = int(
            np.sum(winner_mask)
        )

        winner_mass = float(
            np.sum(similarities[winner_mask])
        )

        winner_top_similarity = float(
            np.max(similarities[winner_mask])
        )

        winner_neighbor_counts.append(
            winner_count
        )

        winner_similarity_masses.append(
            winner_mass
        )

        winner_top_similarities.append(
            winner_top_similarity
        )

    # ------------------------------------------------------------
    # Convert to arrays
    # ------------------------------------------------------------

    unique_counts = np.asarray(
        unique_assignee_counts,
        dtype=np.int32,
    )

    winner_counts = np.asarray(
        winner_neighbor_counts,
        dtype=np.int32,
    )

    winner_masses = np.asarray(
        winner_similarity_masses,
        dtype=np.float64,
    )

    winner_top_similarities = np.asarray(
        winner_top_similarities,
        dtype=np.float64,
    )

    top_neighbor_matches = np.asarray(
        top_neighbor_matches,
        dtype=bool,
    )

    aggregation_matches = np.asarray(
        aggregation_matches,
        dtype=bool,
    )

    winner_changed = np.asarray(
        winner_changed,
        dtype=bool,
    )

    # ------------------------------------------------------------
    # Overall comparison
    # ------------------------------------------------------------

    top_neighbor_hit_at_1 = float(
        np.mean(top_neighbor_matches)
    )

    aggregation_hit_at_1 = float(
        np.mean(aggregation_matches)
    )

    winner_changed_rate = float(
        np.mean(winner_changed)
    )

    # ------------------------------------------------------------
    # Changed-winner analysis
    # ------------------------------------------------------------

    changed_count = int(
        np.sum(winner_changed)
    )

    unchanged_count = int(
        np.sum(~winner_changed)
    )

    if changed_count > 0:
        changed_top_neighbor_hit = float(
            np.mean(
                top_neighbor_matches[winner_changed]
            )
        )

        changed_aggregation_hit = float(
            np.mean(
                aggregation_matches[winner_changed]
            )
        )
    else:
        changed_top_neighbor_hit = None
        changed_aggregation_hit = None

    # ------------------------------------------------------------
    # Winner multiplicity
    # ------------------------------------------------------------

    multiplicity_distribution = {}

    for count in sorted(
        np.unique(winner_counts)
    ):
        mask = winner_counts == count

        multiplicity_distribution[
            str(int(count))
        ] = {
            "rows": int(np.sum(mask)),
            "share": float(np.mean(mask)),
            "aggregation_hit_at_1": float(
                np.mean(
                    aggregation_matches[mask]
                )
            ),
        }

    # ------------------------------------------------------------
    # Retrieval diversity
    # ------------------------------------------------------------

    diversity_distribution = {}

    for count in sorted(
        np.unique(unique_counts)
    ):
        mask = unique_counts == count

        diversity_distribution[
            str(int(count))
        ] = {
            "rows": int(np.sum(mask)),
            "share": float(np.mean(mask)),
            "aggregation_hit_at_1": float(
                np.mean(
                    aggregation_matches[mask]
                )
            ),
        }

    # ------------------------------------------------------------
    # Similarity evidence
    # ------------------------------------------------------------

    result = {
        "experiment": (
            "T4 MOD-007 Retrieval Structure Analysis"
        ),
        "status": "COMPLETE",
        "inputs": {
            "training_file": str(TRAIN_FILE),
            "evaluation_file": str(EVAL_FILE),
            "retrieval_checkpoint": str(
                RETRIEVAL_FILE
            ),
            "training_rows": int(len(train)),
            "evaluation_rows": int(len(evaluation)),
            "neighbors_per_evaluation_row": int(
                neighbor_indices.shape[1]
            ),
        },
        "overall": {
            "top_neighbor_hit_at_1": (
                top_neighbor_hit_at_1
            ),
            "mod007_aggregation_hit_at_1": (
                aggregation_hit_at_1
            ),
            "aggregation_minus_top_neighbor": (
                aggregation_hit_at_1
                - top_neighbor_hit_at_1
            ),
            "winner_changed_rate": (
                winner_changed_rate
            ),
            "winner_unchanged_rate": (
                1.0 - winner_changed_rate
            ),
        },
        "winner_change_analysis": {
            "changed_rows": changed_count,
            "unchanged_rows": unchanged_count,
            "changed_share": winner_changed_rate,
            "changed_rows_top_neighbor_hit_at_1": (
                changed_top_neighbor_hit
            ),
            "changed_rows_aggregation_hit_at_1": (
                changed_aggregation_hit
            ),
        },
        "winner_multiplicity": {
            "mean": float(
                np.mean(winner_counts)
            ),
            "median": float(
                np.median(winner_counts)
            ),
            "maximum": int(
                np.max(winner_counts)
            ),
            "single_neighbor_winners": int(
                np.sum(winner_counts == 1)
            ),
            "multiple_neighbor_winners": int(
                np.sum(winner_counts > 1)
            ),
            "distribution": (
                multiplicity_distribution
            ),
        },
        "retrieval_diversity": {
            "mean_unique_assignees": float(
                np.mean(unique_counts)
            ),
            "median_unique_assignees": float(
                np.median(unique_counts)
            ),
            "minimum_unique_assignees": int(
                np.min(unique_counts)
            ),
            "maximum_unique_assignees": int(
                np.max(unique_counts)
            ),
            "distribution": (
                diversity_distribution
            ),
        },
        "winner_similarity_evidence": {
            "mean_similarity_mass": float(
                np.mean(winner_masses)
            ),
            "median_similarity_mass": float(
                np.median(winner_masses)
            ),
            "mean_strongest_similarity": float(
                np.mean(winner_top_similarities)
            ),
            "median_strongest_similarity": float(
                np.median(winner_top_similarities)
            ),
        },
        "interpretation": [
            "The analysis uses the exact frozen training "
            "artifact used by MOD-007 and the saved full "
            "retrieval checkpoint.",
            "The strongest individual neighbor is compared "
            "with the existing sum-of-similarities assignee "
            "aggregation.",
            "Winner-change analysis identifies cases where "
            "aggregation overrides the assignee of the "
            "strongest individual historical match.",
            "Winner multiplicity measures how many retrieved "
            "historical tickets contribute evidence to the "
            "selected assignee.",
            "Retrieval diversity measures how many distinct "
            "assignees appear among the 20 retrieved tickets.",
            "These diagnostics are used to determine whether "
            "the current aggregation mechanism is a justified "
            "target for a subsequent controlled experiment.",
        ],
        "controls": {
            "raw_mozilla_accessed": False,
            "target_reconstructed": False,
            "model_trained": False,
            "new_predictions_created": False,
            "test_used": False,
        },
    }

    # ------------------------------------------------------------
    # Save result
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
    # Terminal output
    # ------------------------------------------------------------

    print()
    print("TOP NEIGHBOR VS MOD-007 AGGREGATION")

    print(
        f"Top-neighbor Hit@1 : "
        f"{top_neighbor_hit_at_1:.6f}"
    )

    print(
        f"MOD-007 Hit@1      : "
        f"{aggregation_hit_at_1:.6f}"
    )

    print(
        f"Aggregation delta  : "
        f"{aggregation_hit_at_1 - top_neighbor_hit_at_1:+.6f}"
    )

    print(
        f"Winner changed     : "
        f"{winner_changed_rate:.6f}"
    )

    print()
    print("WINNER MULTIPLICITY")

    print(
        f"Mean contributing neighbors   : "
        f"{np.mean(winner_counts):.4f}"
    )

    print(
        f"Median contributing neighbors : "
        f"{np.median(winner_counts):.4f}"
    )

    print(
        f"Maximum contributing neighbors: "
        f"{np.max(winner_counts)}"
    )

    print(
        f"Single-neighbor winners       : "
        f"{np.sum(winner_counts == 1)}"
    )

    print(
        f"Multiple-neighbor winners     : "
        f"{np.sum(winner_counts > 1)}"
    )

    print()
    print("RETRIEVAL DIVERSITY")

    print(
        f"Mean unique assignees   : "
        f"{np.mean(unique_counts):.4f}"
    )

    print(
        f"Median unique assignees : "
        f"{np.median(unique_counts):.4f}"
    )

    print(
        f"Minimum unique assignees: "
        f"{np.min(unique_counts)}"
    )

    print(
        f"Maximum unique assignees: "
        f"{np.max(unique_counts)}"
    )

    print()
    print("WINNER CHANGE ANALYSIS")

    print(
        f"Changed rows: {changed_count}"
    )

    if changed_count > 0:
        print(
            f"Changed-row top-neighbor Hit@1: "
            f"{changed_top_neighbor_hit:.6f}"
        )

        print(
            f"Changed-row aggregation Hit@1: "
            f"{changed_aggregation_hit:.6f}"
        )

    print()
    print(
        f"Analysis saved: {OUTPUT_FILE}"
    )

    print("STATUS=COMPLETE")


if __name__ == "__main__":
    main()