#!/usr/bin/env python3

import csv
from pathlib import Path


# ============================================================
# T8 MOD-013
# Clean Native-Evaluation Candidate Population Audit
#
# READ-ONLY
# No model loading
# No training
# No fusion
# No score transformation
# No synthetic target
# No raw archive access
# No artifact modification
# ============================================================

csv.field_size_limit(2**31 - 1)


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

MODELING_ROOT = PROJECT_ROOT / "modeling"


TASKS = {
    "T2": {
        "train": MODELING_ROOT / "T2/splits/train.csv",
        "eval": MODELING_ROOT / "T2/splits/test.csv",
        "prediction": MODELING_ROOT /
        "T2/analysis/t2_final_test_predictions.csv",
    },

    "T4": {
        "train": MODELING_ROOT / "T4/derived/t4_train.csv",
        "eval": MODELING_ROOT / "T4/derived/t4_eval.csv",
        "prediction": MODELING_ROOT /
        "T4/derived/t4_eval.csv",
    },

    "T5": {
        "train": MODELING_ROOT /
        "T5/splits/t5_model_train.csv",
        "eval": Path(
            "/run/media/whiteblack/User 1/Datasets/"
            "Mozilla_CORE/DTM-002_T5_EVAL_GROUP_AWARE.csv"
        ),
        "prediction": MODELING_ROOT /
        "T5/metrics/t5_mod009_locked_evaluation_predictions.npz",
    },

    "T7": {
        "train": MODELING_ROOT / "T7/splits/t7_train.csv",
        "eval": MODELING_ROOT / "T7/splits/t7_evaluation.csv",
        "prediction": MODELING_ROOT /
        "T7/derived/t7_mod010_evaluation_predictions.csv",
    },
}


def print_header(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def load_ids(path):
    """
    Load non-empty IDs from a CSV.
    """
    ids = set()

    if not path.exists():
        return ids

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        if not reader.fieldnames:
            return ids

        if "ID" not in reader.fieldnames:
            return ids

        for row in reader:

            value = row.get("ID")

            if value is None:
                continue

            value = value.strip()

            if value:
                ids.add(value)

    return ids


def percentage(part, whole):
    if not whole:
        return 0.0

    return 100.0 * part / whole


# ============================================================
# 1. Load populations
# ============================================================

print_header(
    "MOD-013 — NATIVE EVALUATION POPULATION LOADING"
)

populations = {}

for task, info in TASKS.items():

    train_ids = load_ids(info["train"])
    eval_ids = load_ids(info["eval"])

    populations[task] = {
        "train": train_ids,
        "eval": eval_ids,
    }

    print()
    print(task)
    print(f"  train IDs: {len(train_ids):,}")
    print(f"  eval IDs:  {len(eval_ids):,}")


# ============================================================
# 2. Prediction population references
# ============================================================

print_header(
    "MOD-013 — PREDICTION POPULATION REFERENCES"
)

for task, info in TASKS.items():

    path = info["prediction"]

    print()
    print(task)
    print(f"  artifact: {path}")
    print(f"  exists:   {path.exists()}")


# ============================================================
# 3. Pairwise clean candidate cohorts
# ============================================================

print_header(
    "MOD-013 — PAIRWISE CLEAN CANDIDATE COHORTS"
)

tasks = list(TASKS.keys())

for anchor in tasks:

    anchor_eval = populations[anchor]["eval"]

    print()
    print(
        f"ANCHOR {anchor}"
    )
    print(
        f"  Evaluation population: "
        f"{len(anchor_eval):,}"
    )

    for auxiliary in tasks:

        if auxiliary == anchor:
            continue

        auxiliary_train = populations[auxiliary]["train"]
        auxiliary_eval = populations[auxiliary]["eval"]

        # Tickets where auxiliary model training has seen
        # the anchor evaluation ticket.
        contaminated = (
            anchor_eval &
            auxiliary_train
        )

        # Anchor evaluation tickets unseen by auxiliary training.
        clean_anchor = (
            anchor_eval -
            auxiliary_train
        )

        # Clean tickets for which an auxiliary evaluation
        # prediction exists.
        clean_prediction = (
            clean_anchor &
            auxiliary_eval
        )

        print()
        print(
            f"  + {auxiliary}"
        )
        print(
            f"    anchor eval:                 "
            f"{len(anchor_eval):,}"
        )
        print(
            f"    auxiliary train overlap:     "
            f"{len(contaminated):,} "
            f"({percentage(len(contaminated), len(anchor_eval)):.6f}%)"
        )
        print(
            f"    anchor eval outside aux train:"
            f" {len(clean_anchor):,}"
        )
        print(
            f"    clean aux-prediction cohort:  "
            f"{len(clean_prediction):,} "
            f"({percentage(len(clean_prediction), len(anchor_eval)):.6f}%)"
        )


# ============================================================
# 4. Pairwise + triple clean cohorts
# ============================================================

print_header(
    "MOD-013 — MULTI-AUXILIARY CLEAN COHORTS"
)

for anchor in tasks:

    anchor_eval = populations[anchor]["eval"]

    auxiliaries = [
        task
        for task in tasks
        if task != anchor
    ]

    print()
    print(
        f"ANCHOR {anchor}"
    )

    # --------------------------------------------------------
    # Two auxiliary channels
    # --------------------------------------------------------

    for i in range(len(auxiliaries)):

        for j in range(i + 1, len(auxiliaries)):

            a = auxiliaries[i]
            b = auxiliaries[j]

            # Both auxiliary training populations must exclude
            # the anchor evaluation ticket.
            clean = (
                anchor_eval
                - populations[a]["train"]
                - populations[b]["train"]
            )

            # Both auxiliary evaluation predictions must exist.
            prediction_cohort = (
                clean
                & populations[a]["eval"]
                & populations[b]["eval"]
            )

            print()
            print(
                f"  auxiliaries: {a} + {b}"
            )
            print(
                f"    clean anchor population: "
                f"{len(clean):,}"
            )
            print(
                f"    clean prediction cohort: "
                f"{len(prediction_cohort):,}"
            )

    # --------------------------------------------------------
    # All three auxiliary channels
    # --------------------------------------------------------

    clean_all = set(anchor_eval)

    for auxiliary in auxiliaries:

        clean_all -= populations[auxiliary]["train"]

    prediction_all = set(clean_all)

    for auxiliary in auxiliaries:

        prediction_all &= populations[auxiliary]["eval"]

    print()
    print(
        f"  auxiliaries: "
        f"{' + '.join(auxiliaries)}"
    )
    print(
        f"    clean anchor population: "
        f"{len(clean_all):,}"
    )
    print(
        f"    clean prediction cohort: "
        f"{len(prediction_all):,}"
    )


# ============================================================
# 5. Candidate cohort classification
# ============================================================

print_header(
    "MOD-013 — CANDIDATE COHORT CLASSIFICATION"
)

print(
    "Definitions:"
)

print(
    "  CLEAN_PAIRWISE:"
    " anchor evaluation ticket is absent from the auxiliary"
    " task's training population and has an auxiliary"
    " evaluation prediction."
)

print(
    "  CLEAN_MULTI:"
    " anchor evaluation ticket is absent from every auxiliary"
    " training population used in the combination and has"
    " evaluation predictions for every auxiliary channel."
)

print(
    "  DESCRIPTIVE_ONLY:"
    " overlap exists, but independence requirements are not"
    " established by this audit."
)


# ============================================================
# 6. Native-anchor candidate summary
# ============================================================

print_header(
    "MOD-013 — NATIVE ANCHOR SUMMARY"
)

for anchor in tasks:

    anchor_eval = populations[anchor]["eval"]

    print()
    print(
        f"{anchor}"
    )
    print(
        f"  native evaluation population: "
        f"{len(anchor_eval):,}"
    )

    for auxiliary in tasks:

        if auxiliary == anchor:
            continue

        clean = (
            anchor_eval
            - populations[auxiliary]["train"]
        )

        cohort = (
            clean
            & populations[auxiliary]["eval"]
        )

        print(
            f"  clean + {auxiliary}: "
            f"{len(cohort):,}"
        )


# ============================================================
# 7. Design warnings
# ============================================================

print_header(
    "MOD-013 — DESIGN WARNINGS"
)

warnings = [
    (
        "Cohort size",
        "A clean overlap is not automatically sufficient for "
        "statistical evaluation; sample size and class/event "
        "composition must be audited next."
    ),

    (
        "Task semantics",
        "Clean overlap does not make heterogeneous outputs "
        "interchangeable."
    ),

    (
        "Evaluation integrity",
        "Auxiliary prediction availability must remain tied "
        "to its actual evaluation population."
    ),

    (
        "T5",
        "T5 duplicate probability remains a duplicate-relationship "
        "signal and cannot be interpreted as duplicate identity."
    ),

    (
        "T7",
        "T7 remains survival evidence with censoring preserved."
    ),

    (
        "T4",
        "T4 remains ranking/retrieval evidence."
    ),

    (
        "T3",
        "T3 remains excluded from ID-level candidate cohorts "
        "until an addressable prediction artifact exists."
    ),
]

for name, description in warnings:

    print()
    print(
        f"{name}:"
    )
    print(
        f"  {description}"
    )


# ============================================================
# 8. Final status
# ============================================================

print_header(
    "MOD-013 — FINAL STATUS"
)

print(
    "Candidate native evaluation cohorts enumerated."
)

print(
    "Cross-task training contamination accounted for."
)

print(
    "No final fusion anchor selected."
)

print(
    "No fusion model created."
)

print(
    "No scores transformed."
)

print(
    "No target created."
)

print(
    "No model loaded."
)

print(
    "No training performed."
)

print(
    "No artifact modified."
)

print()
print(
    "MOD-013 CLEAN CANDIDATE POPULATION AUDIT COMPLETE"
)