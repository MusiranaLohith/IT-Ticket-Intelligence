from pathlib import Path
import json

import numpy as np
import pandas as pd


PROJECT_DIR = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
DERIVED_DIR = PROJECT_DIR / "modeling" / "T4" / "derived"
RESULTS_DIR = PROJECT_DIR / "modeling" / "T4" / "results"

TRAIN_PATH = DERIVED_DIR / "t4_train.csv"
EVAL_PATH = DERIVED_DIR / "t4_eval.csv"

MOD007_CHECKPOINT = (
    RESULTS_DIR
    / "mod007_checkpoints"
    / "t4_mod007_full_retrieval.npz"
)

MOD011_CHECKPOINT = (
    RESULTS_DIR
    / "mod011_checkpoints"
    / "t4_mod011_retrieval.npz"
)

OUTPUT_PATH = RESULTS_DIR / "t4_mod012_analysis.json"


TOP_K = 20


def load_checkpoint(path):
    data = np.load(path)
    return (
        data["neighbor_indices"],
        data[
            "neighbor_similarities"
        ]
        if "neighbor_similarities" in data
        else data["neighbor_scores"],
    )


def retrieval_metrics(
    neighbor_indices,
    train_targets,
    eval_targets,
):
    n = len(eval_targets)

    hits = {
        1: 0,
        3: 0,
        5: 0,
        10: 0,
        20: 0,
    }

    reciprocal_rank = 0.0
    ndcg5 = 0.0
    ndcg10 = 0.0

    for i in range(n):
        retrieved = train_targets[
            neighbor_indices[i]
        ]

        true_target = eval_targets[i]

        rank = None

        for position, candidate in enumerate(
            retrieved,
            start=1,
        ):
            if candidate == true_target:
                rank = position
                break

        if rank is not None:
            for k in hits:
                if rank <= k:
                    hits[k] += 1

            reciprocal_rank += 1.0 / rank

            if rank <= 5:
                ndcg5 += (
                    1.0
                    / np.log2(rank + 1)
                )

            if rank <= 10:
                ndcg10 += (
                    1.0
                    / np.log2(rank + 1)
                )

    return {
        "hit_at_1": hits[1] / n,
        "hit_at_3": hits[3] / n,
        "hit_at_5": hits[5] / n,
        "hit_at_10": hits[10] / n,
        "hit_at_20": hits[20] / n,
        "mrr": reciprocal_rank / n,
        "ndcg_at_5": ndcg5 / n,
        "ndcg_at_10": ndcg10 / n,
    }


def true_assignee_positions(
    neighbor_indices,
    train_targets,
    eval_targets,
):
    n = len(eval_targets)

    position_counts = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
        7: 0,
        8: 0,
        9: 0,
        10: 0,
        11: 0,
        12: 0,
        13: 0,
        14: 0,
        15: 0,
        16: 0,
        17: 0,
        18: 0,
        19: 0,
        20: 0,
        "not_retrieved": 0,
    }

    for i in range(n):
        retrieved = train_targets[
            neighbor_indices[i]
        ]

        true_target = eval_targets[i]

        found = False

        for position, candidate in enumerate(
            retrieved,
            start=1,
        ):
            if candidate == true_target:
                position_counts[position] += 1
                found = True
                break

        if not found:
            position_counts["not_retrieved"] += 1

    return position_counts


def support_bucket(support):
    if support == 1:
        return "1"
    if support <= 5:
        return "2-5"
    if support <= 10:
        return "6-10"
    if support <= 20:
        return "11-20"
    if support <= 50:
        return "21-50"
    if support <= 100:
        return "51-100"
    return "101+"


def support_analysis(
    neighbor_indices,
    train_targets,
    eval_targets,
    train_support,
):
    buckets = {
        "1": [],
        "2-5": [],
        "6-10": [],
        "11-20": [],
        "21-50": [],
        "51-100": [],
        "101+": [],
    }

    for i, true_target in enumerate(
        eval_targets
    ):
        support = train_support.get(
            true_target,
            0,
        )

        bucket = support_bucket(
            support
        )

        retrieved = train_targets[
            neighbor_indices[i]
        ]

        rank = None

        for position, candidate in enumerate(
            retrieved,
            start=1,
        ):
            if candidate == true_target:
                rank = position
                break

        buckets[bucket].append(
            rank
        )

    output = {}

    for bucket, ranks in buckets.items():
        ranks = np.asarray(
            ranks,
            dtype=np.float64,
        )

        output[bucket] = {
            "rows": int(len(ranks)),
            "retrieved_within_20": int(
                np.sum(~np.isnan(ranks))
            ),
            "retrieval_coverage_at_20": float(
                np.mean(~np.isnan(ranks))
            ),
            "mean_rank_when_retrieved": (
                float(
                    np.nanmean(ranks)
                )
                if np.any(~np.isnan(ranks))
                else None
            ),
        }

    return output


def main():
    print(
        "T4-MOD-012 final retrieval "
        "evidence/error analysis"
    )
    print()

    train = pd.read_csv(
        TRAIN_PATH
    )

    evaluation = pd.read_csv(
        EVAL_PATH
    )

    train_targets = (
        train[
            "target_assignee"
        ]
        .astype(str)
        .to_numpy()
    )

    eval_targets = (
        evaluation[
            "target_assignee"
        ]
        .astype(str)
        .to_numpy()
    )

    training_candidates = set(
        train_targets
    )

    covered_mask = np.array(
        [
            target in training_candidates
            for target in eval_targets
        ],
        dtype=bool,
    )

    covered_indices = np.flatnonzero(
        covered_mask
    )

    unseen_indices = np.flatnonzero(
        ~covered_mask
    )

    print(
        f"TRAIN_ROWS={len(train)}"
    )

    print(
        f"EVALUATION_ROWS="
        f"{len(evaluation)}"
    )

    print(
        f"COVERED_ROWS="
        f"{len(covered_indices)}"
    )

    print(
        f"UNSEEN_ROWS="
        f"{len(unseen_indices)}"
    )

    print()

    print(
        "LOADING SAVED RETRIEVAL "
        "CHECKPOINTS"
    )

    mod007_indices, mod007_scores = (
        load_checkpoint(
            MOD007_CHECKPOINT
        )
    )

    mod011_indices, mod011_scores = (
        load_checkpoint(
            MOD011_CHECKPOINT
        )
    )

    print(
        "MOD-007 neighbor shape:",
        mod007_indices.shape,
    )

    print(
        "MOD-011 neighbor shape:",
        mod011_indices.shape,
    )

    print()

    print(
        "TRUE-ASSIGNEE RETRIEVAL "
        "COVERAGE"
    )

    mod007_positions = (
        true_assignee_positions(
            mod007_indices[
                covered_indices
            ],
            train_targets,
            eval_targets[
                covered_indices
            ],
        )
    )

    mod011_positions = (
        true_assignee_positions(
            mod011_indices[
                covered_indices
            ],
            train_targets,
            eval_targets[
                covered_indices
            ],
        )
    )

    mod007_coverage = (
        1.0
        - (
            mod007_positions[
                "not_retrieved"
            ]
            / len(covered_indices)
        )
    )

    mod011_coverage = (
        1.0
        - (
            mod011_positions[
                "not_retrieved"
            ]
            / len(covered_indices)
        )
    )

    print(
        f"MOD-007 Top-20 coverage: "
        f"{mod007_coverage:.6f}"
    )

    print(
        f"MOD-011 Top-20 coverage: "
        f"{mod011_coverage:.6f}"
    )

    print(
        f"Delta: "
        f"{mod011_coverage - mod007_coverage:+.6f}"
    )

    print()

    print(
        "TRUE-ASSIGNEE POSITION "
        "DISTRIBUTION"
    )

    print()

    print(
        f"{'Position':<15}"
        f"{'MOD-007':>12}"
        f"{'MOD-011':>12}"
    )

    for position in range(1, 21):
        print(
            f"{position:<15}"
            f"{mod007_positions[position]:>12}"
            f"{mod011_positions[position]:>12}"
        )

    print(
        f"{'Not retrieved':<15}"
        f"{mod007_positions['not_retrieved']:>12}"
        f"{mod011_positions['not_retrieved']:>12}"
    )

    print()

    print(
        "FULL COVERED-POPULATION "
        "RANKING METRICS"
    )

    mod007_covered_metrics = (
        retrieval_metrics(
            mod007_indices[
                covered_indices
            ],
            train_targets,
            eval_targets[
                covered_indices
            ],
        )
    )

    mod011_covered_metrics = (
        retrieval_metrics(
            mod011_indices[
                covered_indices
            ],
            train_targets,
            eval_targets[
                covered_indices
            ],
        )
    )

    for key in mod007_covered_metrics:
        print(
            f"{key.upper():<15}"
            f"MOD007="
            f"{mod007_covered_metrics[key]:.6f} "
            f"MOD011="
            f"{mod011_covered_metrics[key]:.6f}"
        )

    print()

    print(
        "FULL OVERALL "
        "RANKING METRICS"
    )

    mod007_overall = retrieval_metrics(
        mod007_indices,
        train_targets,
        eval_targets,
    )

    mod011_overall = retrieval_metrics(
        mod011_indices,
        train_targets,
        eval_targets,
    )

    for key in mod007_overall:
        print(
            f"{key.upper():<15}"
            f"MOD007="
            f"{mod007_overall[key]:.6f} "
            f"MOD011="
            f"{mod011_overall[key]:.6f}"
        )

    print()

    print(
        "HISTORICAL SUPPORT "
        "ANALYSIS"
    )

    train_support = (
        train[
            "target_assignee"
        ]
        .astype(str)
        .value_counts()
        .to_dict()
    )

    mod007_support = (
        support_analysis(
            mod007_indices[
                covered_indices
            ],
            train_targets,
            eval_targets[
                covered_indices
            ],
            train_support,
        )
    )

    mod011_support = (
        support_analysis(
            mod011_indices[
                covered_indices
            ],
            train_targets,
            eval_targets[
                covered_indices
            ],
            train_support,
        )
    )

    for bucket in [
        "1",
        "2-5",
        "6-10",
        "11-20",
        "21-50",
        "51-100",
        "101+",
    ]:
        print(
            f"{bucket}: "
            f"MOD007 coverage="
            f"{mod007_support[bucket]['retrieval_coverage_at_20']:.6f} "
            f"MOD011 coverage="
            f"{mod011_support[bucket]['retrieval_coverage_at_20']:.6f}"
        )

    print()

    print(
        "OPEN-WORLD"
    )

    print(
        f"Unseen evaluation rows: "
        f"{len(unseen_indices)}"
    )

    print(
        "Both methods have zero "
        "true-assignee retrieval "
        "coverage for unseen targets "
        "because those targets are "
        "absent from the training "
        "candidate space."
    )

    output = {
        "experiment": "T4-MOD-012",
        "status": "COMPLETE",
        "population": {
            "train_rows": int(
                len(train)
            ),
            "evaluation_rows": int(
                len(evaluation)
            ),
            "covered_rows": int(
                len(covered_indices)
            ),
            "unseen_rows": int(
                len(unseen_indices)
            ),
            "training_candidates": int(
                len(training_candidates)
            ),
        },
        "methods": {
            "mod007": (
                "Word TF-IDF historical "
                "retrieval"
            ),
            "mod011": (
                "BM25 historical "
                "retrieval"
            ),
        },
        "true_assignee_retrieval_coverage": {
            "mod007": mod007_coverage,
            "mod011": mod011_coverage,
            "delta_mod011_minus_mod007": (
                mod011_coverage
                - mod007_coverage
            ),
        },
        "true_assignee_position_counts": {
            "mod007": mod007_positions,
            "mod011": mod011_positions,
        },
        "covered_metrics": {
            "mod007": mod007_covered_metrics,
            "mod011": mod011_covered_metrics,
        },
        "overall_metrics": {
            "mod007": mod007_overall,
            "mod011": mod011_overall,
        },
        "historical_support": {
            "mod007": mod007_support,
            "mod011": mod011_support,
        },
        "open_world": {
            "unseen_rows": int(
                len(unseen_indices)
            ),
            "unseen_rate": float(
                len(unseen_indices)
                / len(evaluation)
            ),
            "true_assignee_retrievable": False,
        },
        "controls": {
            "raw_mozilla_accessed": False,
            "target_reconstructed": False,
            "test_used": False,
            "future_features_used": False,
            "split_changed": False,
            "evaluation_used_only_for_scoring": True,
            "training_tickets_used_for_retrieval": True,
            "evaluation_tickets_used_for_retrieval": False,
        },
    }

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            output,
            f,
            indent=2,
        )

    print()
    print(
        f"ANALYSIS_SAVED="
        f"{OUTPUT_PATH}"
    )

    print(
        "T4-MOD-012_COMPLETE"
    )


if __name__ == "__main__":
    main()