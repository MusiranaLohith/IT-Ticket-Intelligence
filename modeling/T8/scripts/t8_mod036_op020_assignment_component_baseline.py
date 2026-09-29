from pathlib import Path
import csv
import json
from collections import defaultdict

import numpy as np


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

TRAIN_SOURCE = ROOT / "modeling/T4/derived/t4_train.csv"
EVAL_SOURCE = ROOT / "modeling/T4/derived/t4_eval.csv"
RETRIEVAL_SOURCE = (
    ROOT
    / "modeling/T4/results/mod011_checkpoints/t4_mod011_retrieval.npz"
)

OUT_DIR = ROOT / "modeling/T8/mod036/op020"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REPORT = (
    OUT_DIR
    / "t8_mod036_op020_assignment_component_baseline.json"
)

PREDICTIONS = (
    OUT_DIR
    / "t8_mod036_op020_assignment_predictions.csv"
)

csv.field_size_limit(10_000_000)


def load_csv(path):
    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline="",
    ) as f:
        return list(csv.DictReader(f))


def resolve_column(row, candidates, field_name):
    normalized = {
        str(key).strip().lower(): key
        for key in row.keys()
    }

    for candidate in candidates:
        actual = normalized.get(
            candidate.strip().lower()
        )

        if actual is not None:
            return actual

    raise RuntimeError(
        f"Could not resolve {field_name}. "
        f"Available columns: {list(row.keys())}"
    )


def get_id(row):
    column = resolve_column(
        row,
        (
            "id",
            "ticket_id",
            "bug_id",
            "ticket",
        ),
        "ticket ID",
    )

    value = str(row[column]).strip()

    if not value:
        raise RuntimeError(
            "Empty ticket ID encountered."
        )

    return value


def get_target(row):
    column = resolve_column(
        row,
        (
            "target_assignee",
            "assignee_target",
            "target",
        ),
        "target_assignee",
    )

    value = str(row[column]).strip()

    if not value:
        raise RuntimeError(
            "Empty target_assignee encountered."
        )

    return value


def aggregate_neighbor_scores(
    neighbor_indices,
    neighbor_scores,
    train_assignees,
):
    """
    Convert retrieved training-neighbor evidence into an
    assignment recommendation.

    Each retrieved training row contributes its retrieval
    score to that row's target_assignee.

    This preserves T4's retrieval semantics rather than
    converting the task into ordinary multiclass classification.
    """

    candidate_scores = defaultdict(float)

    for neighbor_index, score in zip(
        neighbor_indices,
        neighbor_scores,
    ):

        index = int(neighbor_index)

        if index < 0:
            continue

        if index >= len(train_assignees):
            continue

        score = float(score)

        if not np.isfinite(score):
            continue

        assignee = train_assignees[index]

        if not assignee:
            continue

        candidate_scores[assignee] += score

    if not candidate_scores:
        return [], []

    ranked = sorted(
        candidate_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    assignees = [
        item[0]
        for item in ranked
    ]

    scores = [
        float(item[1])
        for item in ranked
    ]

    return assignees, scores


def main():

    print("=" * 80)
    print("T8 DECISION ENGINE — MOD-036 OP-020")
    print("Assignment Decision Component Baseline")
    print("=" * 80)

    # =============================================================
    # 1. Resolve native T4 sources
    # =============================================================

    for path in (
        TRAIN_SOURCE,
        EVAL_SOURCE,
        RETRIEVAL_SOURCE,
    ):
        if not path.exists():
            raise FileNotFoundError(path)

    train_rows = load_csv(
        TRAIN_SOURCE
    )

    eval_rows = load_csv(
        EVAL_SOURCE
    )

    print("\nNative T4 populations")
    print("-" * 80)
    print(
        f"  T4 train: "
        f"{len(train_rows)}"
    )
    print(
        f"  T4 evaluation: "
        f"{len(eval_rows)}"
    )

    # =============================================================
    # 2. Resolve T4 target column
    # =============================================================

    train_target_column = resolve_column(
        train_rows[0],
        (
            "target_assignee",
            "assignee_target",
            "target",
        ),
        "T4 training target_assignee",
    )

    eval_target_column = resolve_column(
        eval_rows[0],
        (
            "target_assignee",
            "assignee_target",
            "target",
        ),
        "T4 evaluation target_assignee",
    )

    print("\nTarget columns")
    print("-" * 80)
    print(
        f"  train: "
        f"{train_target_column}"
    )
    print(
        f"  evaluation: "
        f"{eval_target_column}"
    )

    # =============================================================
    # 3. Build training-neighbor target mapping
    # =============================================================

    train_ids = [
        get_id(row)
        for row in train_rows
    ]

    train_assignees = [
        str(
            row[train_target_column]
        ).strip()
        for row in train_rows
    ]

    train_unique_ids = set(
        train_ids
    )

    if len(train_unique_ids) != len(
        train_rows
    ):
        raise RuntimeError(
            "Duplicate IDs detected in T4 training population."
        )

    empty_train_targets = sum(
        1
        for value in train_assignees
        if not value
    )

    if empty_train_targets:
        raise RuntimeError(
            "Blank target_assignee values detected "
            "in T4 training population."
        )

    print("\nTraining-neighbor mapping")
    print("-" * 80)
    print(
        f"  training rows: "
        f"{len(train_rows)}"
    )
    print(
        f"  unique training IDs: "
        f"{len(train_unique_ids)}"
    )
    print(
        f"  distinct assignees: "
        f"{len(set(train_assignees))}"
    )
    print(
        f"  blank targets: "
        f"{empty_train_targets}"
    )

    # =============================================================
    # 4. Evaluation population
    # =============================================================

    eval_ids = [
        get_id(row)
        for row in eval_rows
    ]

    eval_targets = [
        get_target(row)
        for row in eval_rows
    ]

    eval_unique_ids = set(
        eval_ids
    )

    if len(eval_unique_ids) != len(
        eval_rows
    ):
        raise RuntimeError(
            "Duplicate IDs detected in T4 evaluation population."
        )

    print("\nEvaluation population integrity")
    print("-" * 80)
    print(
        f"  rows: "
        f"{len(eval_rows)}"
    )
    print(
        f"  unique IDs: "
        f"{len(eval_unique_ids)}"
    )

    # =============================================================
    # 5. Load exact T4 retrieval checkpoint
    # =============================================================

    retrieval = np.load(
        RETRIEVAL_SOURCE,
        allow_pickle=False,
    )

    required_keys = {
        "neighbor_indices",
        "neighbor_scores",
    }

    if not required_keys.issubset(
        set(retrieval.files)
    ):
        raise RuntimeError(
            "T4 retrieval artifact does not contain "
            "the required native keys. "
            f"Found: {retrieval.files}"
        )

    neighbor_indices = retrieval[
        "neighbor_indices"
    ]

    neighbor_scores = retrieval[
        "neighbor_scores"
    ]

    print("\nRetrieval checkpoint")
    print("-" * 80)
    print(
        f"  keys: "
        f"{retrieval.files}"
    )
    print(
        f"  neighbor_indices shape: "
        f"{neighbor_indices.shape}"
    )
    print(
        f"  neighbor_scores shape: "
        f"{neighbor_scores.shape}"
    )

    # =============================================================
    # 6. Exact alignment validation
    # =============================================================

    if neighbor_indices.ndim != 2:
        raise RuntimeError(
            "neighbor_indices must be 2-dimensional."
        )

    if neighbor_scores.ndim != 2:
        raise RuntimeError(
            "neighbor_scores must be 2-dimensional."
        )

    if neighbor_indices.shape != neighbor_scores.shape:
        raise RuntimeError(
            "neighbor_indices and neighbor_scores "
            "have different shapes."
        )

    if neighbor_indices.shape[0] != len(
        eval_rows
    ):
        raise RuntimeError(
            "Retrieval rows do not match T4 evaluation rows. "
            f"retrieval={neighbor_indices.shape[0]}, "
            f"evaluation={len(eval_rows)}"
        )

    neighbor_count = neighbor_indices.shape[1]

    print(
        f"  evaluation-row alignment: "
        f"{neighbor_indices.shape[0]} = {len(eval_rows)}"
    )

    print(
        f"  neighbors per evaluation ticket: "
        f"{neighbor_count}"
    )

    # =============================================================
    # 7. Validate neighbor indices
    # =============================================================

    invalid_neighbor_indices = 0

    for value in neighbor_indices.ravel():

        index = int(value)

        if (
            index < 0
            or index >= len(train_assignees)
        ):
            invalid_neighbor_indices += 1

    print(
        f"  invalid neighbor indices: "
        f"{invalid_neighbor_indices}"
    )

    if invalid_neighbor_indices:
        raise RuntimeError(
            "Retrieval artifact contains neighbor indices "
            "outside the T4 training population."
        )

    # =============================================================
    # 8. Generate assignment recommendations
    # =============================================================

    top1_hits = 0
    top3_hits = 0
    top5_hits = 0
    top10_hits = 0
    top20_hits = 0

    target_present_rows = 0
    unseen_target_rows = 0
    no_recommendation_rows = 0

    prediction_rows = []

    for row_index in range(
        len(eval_rows)
    ):

        target = eval_targets[
            row_index
        ]

        ranked_assignees, ranked_scores = (
            aggregate_neighbor_scores(
                neighbor_indices[row_index],
                neighbor_scores[row_index],
                train_assignees,
            )
        )

        if not ranked_assignees:

            no_recommendation_rows += 1

            prediction_rows.append(
                [
                    eval_ids[row_index],
                    target,
                    "",
                    "",
                    "",
                    0,
                    "",
                    "NO_RECOMMENDATION",
                ]
            )

            continue

        target_present = (
            target in ranked_assignees
        )

        if target_present:

            target_present_rows += 1

            target_rank = (
                ranked_assignees.index(target)
                + 1
            )

            if target_rank <= 1:
                top1_hits += 1

            if target_rank <= 3:
                top3_hits += 1

            if target_rank <= 5:
                top5_hits += 1

            if target_rank <= 10:
                top10_hits += 1

            if target_rank <= 20:
                top20_hits += 1

        else:

            unseen_target_rows += 1
            target_rank = ""

        recommendation = (
            ranked_assignees[0]
        )

        recommendation_score = (
            ranked_scores[0]
        )

        top20 = ranked_assignees[:20]

        prediction_rows.append(
            [
                eval_ids[row_index],
                target,
                recommendation,
                recommendation_score,
                target_rank,
                int(target_present),
                "|".join(top20),
                "OK",
            ]
        )

    total = len(eval_rows)

    top1 = top1_hits / total
    top3 = top3_hits / total
    top5 = top5_hits / total
    top10 = top10_hits / total
    top20 = top20_hits / total

    unseen_rate = (
        unseen_target_rows / total
    )

    no_recommendation_rate = (
        no_recommendation_rows / total
    )

    # =============================================================
    # 9. Report metrics
    # =============================================================

    print("\nAssignment recommendation metrics")
    print("-" * 80)
    print(
        f"  Top-1 accuracy: "
        f"{top1:.6f}"
    )
    print(
        f"  Top-3 recall:   "
        f"{top3:.6f}"
    )
    print(
        f"  Top-5 recall:   "
        f"{top5:.6f}"
    )
    print(
        f"  Top-10 recall:  "
        f"{top10:.6f}"
    )
    print(
        f"  Top-20 recall:  "
        f"{top20:.6f}"
    )
    print(
        f"  target present: "
        f"{target_present_rows}"
    )
    print(
        f"  unseen target:  "
        f"{unseen_target_rows}"
    )
    print(
        f"  unseen rate:    "
        f"{unseen_rate:.6f}"
    )
    print(
        f"  no recommendation: "
        f"{no_recommendation_rows}"
    )
    print(
        f"  no recommendation rate: "
        f"{no_recommendation_rate:.6f}"
    )

    # =============================================================
    # 10. Save predictions
    # =============================================================

    with PREDICTIONS.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            [
                "id",
                "true_assignee",
                "recommended_assignee",
                "recommended_score",
                "target_rank",
                "target_present",
                "top20_candidates",
                "status",
            ]
        )

        writer.writerows(
            prediction_rows
        )

    # =============================================================
    # 11. Save research artifact
    # =============================================================

    report = {
        "operation": "MOD-036 OP-020",
        "component": "assignment",
        "status": "PASS",

        "sources": {
            "t4_train": str(
                TRAIN_SOURCE.relative_to(ROOT)
            ),
            "t4_eval": str(
                EVAL_SOURCE.relative_to(ROOT)
            ),
            "retrieval": str(
                RETRIEVAL_SOURCE.relative_to(ROOT)
            ),
        },

        "population": {
            "train_rows": len(train_rows),
            "evaluation_rows": len(eval_rows),
            "train_unique_ids": len(
                train_unique_ids
            ),
            "evaluation_unique_ids": len(
                eval_unique_ids
            ),
        },

        "native_semantics": {
            "task_type": "candidate_ranking",
            "target": "target_assignee",
            "recommendation_type": (
                "ranked_assignment_candidates"
            ),
            "neighbor_count": neighbor_count,
            "retrieval_keys": [
                "neighbor_indices",
                "neighbor_scores",
            ],
        },

        "alignment": {
            "retrieval_rows": int(
                neighbor_indices.shape[0]
            ),
            "evaluation_rows": len(
                eval_rows
            ),
            "aligned": True,
            "invalid_neighbor_indices": (
                invalid_neighbor_indices
            ),
        },

        "metrics": {
            "top1_accuracy": float(top1),
            "top3_recall": float(top3),
            "top5_recall": float(top5),
            "top10_recall": float(top10),
            "top20_recall": float(top20),
            "target_present_rows": (
                target_present_rows
            ),
            "unseen_target_rows": (
                unseen_target_rows
            ),
            "unseen_target_rate": float(
                unseen_rate
            ),
            "no_recommendation_rows": (
                no_recommendation_rows
            ),
            "no_recommendation_rate": float(
                no_recommendation_rate
            ),
        },

        "outputs": {
            "predictions": str(
                PREDICTIONS.relative_to(ROOT)
            ),
        },

        "controls": {
            "post_creation_information_used": False,
            "locked_t4_evaluation_used": False,
            "target_converted_to_negative": False,
            "candidate_universe_expanded": False,
            "probability_conversion_performed": False,
            "blind_probability_averaging": False,
            "arbitrary_cross_task_weighting": False,
        },
    }

    REPORT.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nArtifacts")
    print("-" * 80)
    print(
        f"  report: {REPORT}"
    )
    print(
        f"  predictions: {PREDICTIONS}"
    )

    print("\nStatus: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()