from pathlib import Path
import json

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

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
    / "modeling/T4/results/"
    / "t4_mod007_true_assignee_coverage.json"
)


def main():
    print("T4 MOD-007 true-assignee retrieval coverage analysis")

    # ------------------------------------------------------------
    # Load frozen artifacts
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
            f"Unexpected retrieval shape: "
            f"{neighbor_indices.shape}"
        )

    if neighbor_similarities.shape != (35626, 20):
        raise RuntimeError(
            f"Unexpected similarity shape: "
            f"{neighbor_similarities.shape}"
        )

    # ------------------------------------------------------------
    # Training candidate space
    # ------------------------------------------------------------

    training_candidate_set = set(
        train_targets.tolist()
    )

    covered_mask = np.asarray(
        [
            target in training_candidate_set
            for target in eval_targets
        ],
        dtype=bool,
    )

    covered_rows = int(np.sum(covered_mask))
    unseen_rows = int(np.sum(~covered_mask))

    # ------------------------------------------------------------
    # Per-row diagnostics
    # ------------------------------------------------------------

    true_assignee_retrieved = []
    true_assignee_neighbor_counts = []
    true_assignee_best_rank = []
    true_assignee_best_similarity = []
    true_assignee_similarity_mass = []

    aggregation_rank = []
    aggregation_hit_at_1 = []

    # ------------------------------------------------------------
    # Analyze only covered evaluation targets.
    #
    # Unseen targets cannot have historical training tickets
    # belonging to them by definition.
    # ------------------------------------------------------------

    for row_idx in range(len(evaluation)):

        if not covered_mask[row_idx]:
            continue

        target = eval_targets[row_idx]

        indices = neighbor_indices[row_idx]
        similarities = neighbor_similarities[row_idx]

        assignees = train_targets[indices]

        target_mask = assignees == target

        retrieved = bool(
            np.any(target_mask)
        )

        true_assignee_retrieved.append(
            retrieved
        )

        count = int(
            np.sum(target_mask)
        )

        true_assignee_neighbor_counts.append(
            count
        )

        if retrieved:
            target_positions = np.where(
                target_mask
            )[0]

            best_rank = int(
                target_positions[0] + 1
            )

            best_similarity = float(
                np.max(
                    similarities[target_mask]
                )
            )

            similarity_mass = float(
                np.sum(
                    similarities[target_mask]
                )
            )

        else:
            best_rank = None
            best_similarity = None
            similarity_mass = 0.0

        true_assignee_best_rank.append(
            best_rank
        )

        true_assignee_best_similarity.append(
            best_similarity
        )

        true_assignee_similarity_mass.append(
            similarity_mass
        )

        # --------------------------------------------------------
        # Reproduce MOD-007 aggregation
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

        ranked_assignees = [
            assignee
            for assignee, _ in ranked
        ]

        if target in ranked_assignees:
            target_rank = (
                ranked_assignees.index(target) + 1
            )
        else:
            target_rank = None

        aggregation_rank.append(
            target_rank
        )

        aggregation_hit_at_1.append(
            bool(
                target_rank == 1
            )
        )

    # ------------------------------------------------------------
    # Convert diagnostics
    # ------------------------------------------------------------

    retrieved_array = np.asarray(
        true_assignee_retrieved,
        dtype=bool,
    )

    neighbor_count_array = np.asarray(
        true_assignee_neighbor_counts,
        dtype=np.int32,
    )

    best_similarity_values = [
        value
        for value in true_assignee_best_similarity
        if value is not None
    ]

    best_rank_values = [
        value
        for value in true_assignee_best_rank
        if value is not None
    ]

    mass_values = np.asarray(
        true_assignee_similarity_mass,
        dtype=np.float64,
    )

    aggregation_hit_array = np.asarray(
        aggregation_hit_at_1,
        dtype=bool,
    )

    # ------------------------------------------------------------
    # Retrieval coverage
    # ------------------------------------------------------------

    retrieval_coverage = float(
        np.mean(retrieved_array)
    )

    retrieval_failure_mask = ~retrieved_array

    aggregation_failure_after_retrieval = (
        retrieved_array
        & ~aggregation_hit_array
    )

    retrieval_and_aggregation_success = (
        retrieved_array
        & aggregation_hit_array
    )

    retrieval_failure_count = int(
        np.sum(retrieval_failure_mask)
    )

    aggregation_failure_after_retrieval_count = int(
        np.sum(
            aggregation_failure_after_retrieval
        )
    )

    success_count = int(
        np.sum(
            retrieval_and_aggregation_success
        )
    )

    # ------------------------------------------------------------
    # Rank distribution of true assignee in retrieval
    # ------------------------------------------------------------

    retrieval_rank_distribution = {}

    for rank in range(1, 21):
        count = int(
            np.sum(
                np.asarray(
                    [
                        value == rank
                        for value in best_rank_values
                    ],
                    dtype=bool,
                )
            )
        )

        if count > 0:
            retrieval_rank_distribution[
                str(rank)
            ] = count

    # ------------------------------------------------------------
    # Retrieval Top-K coverage
    # ------------------------------------------------------------

    retrieval_topk_coverage = {}

    for k in [1, 3, 5, 10, 20]:
        count = int(
            np.sum(
                np.asarray(
                    [
                        value is not None
                        and value <= k
                        for value in true_assignee_best_rank
                    ],
                    dtype=bool,
                )
            )
        )

        retrieval_topk_coverage[
            str(k)
        ] = {
            "rows": count,
            "rate": (
                count / covered_rows
                if covered_rows
                else 0.0
            ),
        }

    # ------------------------------------------------------------
    # Similarity evidence for retrieved true assignees
    # ------------------------------------------------------------

    if best_similarity_values:
        similarity_statistics = {
            "mean_best_similarity": float(
                np.mean(best_similarity_values)
            ),
            "median_best_similarity": float(
                np.median(best_similarity_values)
            ),
            "p10_best_similarity": float(
                np.percentile(
                    best_similarity_values,
                    10,
                )
            ),
            "p90_best_similarity": float(
                np.percentile(
                    best_similarity_values,
                    90,
                )
            ),
            "mean_similarity_mass": float(
                np.mean(mass_values[retrieved_array])
            ),
            "median_similarity_mass": float(
                np.median(mass_values[retrieved_array])
            ),
        }
    else:
        similarity_statistics = {
            "mean_best_similarity": None,
            "median_best_similarity": None,
            "p10_best_similarity": None,
            "p90_best_similarity": None,
            "mean_similarity_mass": None,
            "median_similarity_mass": None,
        }

    # ------------------------------------------------------------
    # Support of true assignee inside retrieved neighbors
    # ------------------------------------------------------------

    neighbor_count_distribution = {}

    for count in sorted(
        np.unique(neighbor_count_array)
    ):
        mask = (
            neighbor_count_array == count
        )

        neighbor_count_distribution[
            str(int(count))
        ] = {
            "rows": int(np.sum(mask)),
            "share": float(
                np.mean(mask)
            ),
            "aggregation_hit_at_1": float(
                np.mean(
                    aggregation_hit_array[mask]
                )
            ),
        }

    # ------------------------------------------------------------
    # Covered-target outcome decomposition
    # ------------------------------------------------------------

    decomposition = {
        "covered_rows": covered_rows,
        "retrieval_success_and_aggregation_success": (
            success_count
        ),
        "retrieval_success_but_aggregation_failure": (
            aggregation_failure_after_retrieval_count
        ),
        "retrieval_failure": (
            retrieval_failure_count
        ),
        "rates": {
            "retrieval_success": float(
                np.mean(retrieved_array)
            ),
            "retrieval_success_and_aggregation_success": (
                success_count / covered_rows
                if covered_rows
                else 0.0
            ),
            "retrieval_success_but_aggregation_failure": (
                aggregation_failure_after_retrieval_count
                / covered_rows
                if covered_rows
                else 0.0
            ),
            "retrieval_failure": (
                retrieval_failure_count
                / covered_rows
                if covered_rows
                else 0.0
            ),
        },
    }

    # ------------------------------------------------------------
    # Result
    # ------------------------------------------------------------

    result = {
        "experiment": (
            "T4 MOD-007 True-Assignee Retrieval Coverage"
        ),
        "status": "COMPLETE",
        "population": {
            "evaluation_rows": int(
                len(evaluation)
            ),
            "covered_rows": covered_rows,
            "unseen_rows": unseen_rows,
            "unseen_rate": float(
                unseen_rows / len(evaluation)
            ),
        },
        "retrieval_coverage": {
            "true_assignee_retrieved_rate": (
                retrieval_coverage
            ),
            "true_assignee_not_retrieved_rate": (
                1.0 - retrieval_coverage
            ),
            "retrieved_rows": int(
                np.sum(retrieved_array)
            ),
            "not_retrieved_rows": (
                retrieval_failure_count
            ),
        },
        "retrieval_topk_coverage": (
            retrieval_topk_coverage
        ),
        "retrieval_rank_distribution": (
            retrieval_rank_distribution
        ),
        "true_assignee_similarity": (
            similarity_statistics
        ),
        "true_assignee_neighbor_count": {
            "mean": float(
                np.mean(neighbor_count_array)
            ),
            "median": float(
                np.median(neighbor_count_array)
            ),
            "maximum": int(
                np.max(neighbor_count_array)
            ),
            "distribution": (
                neighbor_count_distribution
            ),
        },
        "covered_outcome_decomposition": (
            decomposition
        ),
        "interpretation": [
            "This analysis separates retrieval failure from "
            "candidate-aggregation failure.",
            "A covered target is considered retrieval-successful "
            "when at least one of its historical training tickets "
            "appears among the 20 retrieved neighbors.",
            "Retrieval failure means the true training-observed "
            "assignee has no retrieved historical evidence within "
            "the Top-20 set.",
            "Aggregation failure after retrieval means the true "
            "assignee was retrieved but the MOD-007 summed-"
            "similarity aggregation did not rank it first.",
            "This decomposition determines whether a subsequent "
            "experiment should primarily modify retrieval or "
            "assignee scoring.",
            "Unseen evaluation targets are excluded from this "
            "covered-target retrieval analysis because they have "
            "no corresponding training-period assignee evidence."
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
    # Terminal output
    # ------------------------------------------------------------

    print()
    print("POPULATION")

    print(
        f"Evaluation rows : {len(evaluation)}"
    )

    print(
        f"Covered rows    : {covered_rows}"
    )

    print(
        f"Unseen rows     : {unseen_rows}"
    )

    print()
    print("TRUE-ASSIGNEE RETRIEVAL")

    print(
        f"Retrieved in Top-20 : "
        f"{retrieval_coverage:.6f}"
    )

    print(
        f"Not retrieved       : "
        f"{1.0 - retrieval_coverage:.6f}"
    )

    print()
    print("RETRIEVAL TOP-K COVERAGE")

    for k in [1, 3, 5, 10, 20]:
        row = retrieval_topk_coverage[
            str(k)
        ]

        print(
            f"Top-{k:<2} : "
            f"{row['rate']:.6f}"
        )

    print()
    print("OUTCOME DECOMPOSITION")

    print(
        "Retrieval + aggregation success : "
        f"{success_count} "
        f"({success_count / covered_rows:.6f})"
    )

    print(
        "Retrieved but aggregation failed: "
        f"{aggregation_failure_after_retrieval_count} "
        f"({aggregation_failure_after_retrieval_count / covered_rows:.6f})"
    )

    print(
        "Retrieval failure               : "
        f"{retrieval_failure_count} "
        f"({retrieval_failure_count / covered_rows:.6f})"
    )

    print()
    print("TRUE-ASSIGNEE RETRIEVED SUPPORT")

    print(
        f"Mean neighbors for true assignee   : "
        f"{np.mean(neighbor_count_array):.4f}"
    )

    print(
        f"Median neighbors for true assignee : "
        f"{np.median(neighbor_count_array):.4f}"
    )

    print(
        f"Maximum neighbors for true assignee: "
        f"{np.max(neighbor_count_array)}"
    )

    if best_similarity_values:
        print()
        print("TRUE-ASSIGNEE SIMILARITY")

        print(
            f"Mean best similarity   : "
            f"{np.mean(best_similarity_values):.6f}"
        )

        print(
            f"Median best similarity : "
            f"{np.median(best_similarity_values):.6f}"
        )

        print(
            f"Mean similarity mass   : "
            f"{np.mean(mass_values[retrieved_array]):.6f}"
        )

    print()
    print(
        f"Analysis saved: {OUTPUT_FILE}"
    )

    print("STATUS=COMPLETE")


if __name__ == "__main__":
    main()