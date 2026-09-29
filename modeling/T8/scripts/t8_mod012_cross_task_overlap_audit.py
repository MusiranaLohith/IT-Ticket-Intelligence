#!/usr/bin/env python3

import csv
import json
from pathlib import Path


# ============================================================
# T8 MOD-012
# Cross-Task Prediction Independence / Split-Overlap Audit
#
# READ-ONLY
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
    },

    "T4": {
        "train": MODELING_ROOT / "T4/derived/t4_train.csv",
        "eval": MODELING_ROOT / "T4/derived/t4_eval.csv",
    },

    "T5": {
        "train": MODELING_ROOT / "T5/splits/t5_model_train.csv",
        "eval": None,
    },

    "T7": {
        "train": MODELING_ROOT / "T7/splits/t7_train.csv",
        "eval": MODELING_ROOT / "T7/splits/t7_evaluation.csv",
    },
}


T5_METADATA = (
    MODELING_ROOT /
    "T5/metrics/t5_mod009_locked_evaluation_metrics.json"
)


T5_CLOSURE = (
    MODELING_ROOT /
    "T5/metrics/t5_mod011_final_closure.json"
)


T5_EVAL_CANDIDATES = [
    Path(
        "/run/media/whiteblack/User 1/Datasets/"
        "Mozilla_CORE/DTM-002_T5_EVAL_GROUP_AWARE.csv"
    ),
]


PREDICTION_ARTIFACTS = {
    "T2": (
        MODELING_ROOT /
        "T2/analysis/t2_final_test_predictions.csv"
    ),

    "T4": (
        MODELING_ROOT /
        "T4/derived/t4_eval.csv"
    ),

    "T5": (
        MODELING_ROOT /
        "T5/metrics/t5_mod009_locked_evaluation_predictions.npz"
    ),

    "T7": (
        MODELING_ROOT /
        "T7/derived/t7_mod010_evaluation_predictions.csv"
    ),
}


def print_header(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def load_csv_ids(path):
    """
    Read only the ID column from a CSV.
    """
    ids = set()

    if path is None or not path.exists():
        return ids

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        if reader.fieldnames is None:
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


def load_json(path):
    if not path.exists():
        return None

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace"
    ) as f:

        return json.load(f)


def find_strings(obj):
    """
    Recursively return all string values from JSON.
    """
    values = []

    if isinstance(obj, dict):

        for value in obj.values():
            values.extend(find_strings(value))

    elif isinstance(obj, list):

        for value in obj:
            values.extend(find_strings(value))

    elif isinstance(obj, str):

        values.append(obj)

    return values


def find_csv_references(obj):
    """
    Recursively find strings that look like CSV paths.
    """
    matches = []

    for value in find_strings(obj):

        low = value.lower()

        if ".csv" in low:
            matches.append(value)

    return matches


# ============================================================
# 1. Recover T5 evaluation artifact
# ============================================================

print_header(
    "MOD-012 — T5 LOCKED EVALUATION POPULATION RECOVERY"
)

print(
    f"Metadata: {T5_METADATA}"
)

print(
    f"Metadata exists: {T5_METADATA.exists()}"
)

t5_eval_path = None

metadata = load_json(T5_METADATA)

if metadata is not None:

    references = find_csv_references(metadata)

    print()
    print("CSV references found in T5 evaluation metadata:")

    for ref in references:
        print(f"  {ref}")

        candidate = Path(ref)

        if candidate.exists():
            t5_eval_path = candidate
            break


if t5_eval_path is None:

    print()
    print(
        "No existing T5 evaluation CSV was resolved from metadata."
    )

    print(
        "Checking controlled known candidate paths:"
    )

    for candidate in T5_EVAL_CANDIDATES:

        print(
            f"  {candidate} | exists={candidate.exists()}"
        )

        if candidate.exists():
            t5_eval_path = candidate
            break


print()

if t5_eval_path is not None:

    print(
        f"T5 evaluation population: {t5_eval_path}"
    )

else:

    print(
        "T5 evaluation population could not be resolved."
    )


# ============================================================
# 2. Load task populations
# ============================================================

print_header(
    "MOD-012 — TASK POPULATION LOADING"
)

populations = {}

for task, paths in TASKS.items():

    print()
    print(f"--- {task} ---")

    train_ids = load_csv_ids(paths["train"])

    eval_path = paths["eval"]

    if task == "T5" and t5_eval_path is not None:
        eval_path = t5_eval_path

    eval_ids = load_csv_ids(eval_path)

    populations[task] = {
        "train": train_ids,
        "eval": eval_ids,
    }

    print(
        f"Train path: {paths['train']}"
    )

    print(
        f"Train exists: {paths['train'].exists()}"
    )

    print(
        f"Train IDs: {len(train_ids):,}"
    )

    print(
        f"Eval path: {eval_path}"
    )

    print(
        f"Eval exists: "
        f"{eval_path.exists() if eval_path else False}"
    )

    print(
        f"Eval IDs: {len(eval_ids):,}"
    )

    if train_ids and eval_ids:

        internal_overlap = (
            train_ids & eval_ids
        )

        print(
            f"Train ∩ Eval: "
            f"{len(internal_overlap):,}"
        )


# ============================================================
# 3. Prediction artifact population confirmation
# ============================================================

print_header(
    "MOD-012 — PREDICTION ARTIFACT POPULATION REFERENCE"
)

for task, path in PREDICTION_ARTIFACTS.items():

    print()
    print(task)
    print(f"Path: {path}")
    print(f"Exists: {path.exists()}")


# ============================================================
# 4. Evaluation × Evaluation overlap
# ============================================================

print_header(
    "MOD-012 — EVALUATION × EVALUATION OVERLAP"
)

tasks = list(populations.keys())

for i, anchor in enumerate(tasks):

    for auxiliary in tasks[i + 1:]:

        anchor_eval = populations[anchor]["eval"]
        auxiliary_eval = populations[auxiliary]["eval"]

        overlap = anchor_eval & auxiliary_eval

        print()
        print(
            f"{anchor} eval ∩ {auxiliary} eval"
        )

        print(
            f"  overlap: {len(overlap):,}"
        )

        if anchor_eval:
            print(
                f"  % of {anchor} eval: "
                f"{100 * len(overlap) / len(anchor_eval):.6f}%"
            )

        if auxiliary_eval:
            print(
                f"  % of {auxiliary} eval: "
                f"{100 * len(overlap) / len(auxiliary_eval):.6f}%"
            )


# ============================================================
# 5. Anchor evaluation × auxiliary training overlap
# ============================================================

print_header(
    "MOD-012 — ANCHOR EVALUATION × AUXILIARY TRAINING OVERLAP"
)

for anchor in tasks:

    anchor_eval = populations[anchor]["eval"]

    if not anchor_eval:
        continue

    print()
    print(
        f"ANCHOR: {anchor} evaluation "
        f"({len(anchor_eval):,} IDs)"
    )

    for auxiliary in tasks:

        if auxiliary == anchor:
            continue

        auxiliary_train = populations[auxiliary]["train"]

        overlap = (
            anchor_eval &
            auxiliary_train
        )

        print()
        print(
            f"  {anchor} eval ∩ {auxiliary} train"
        )

        print(
            f"    overlap: {len(overlap):,}"
        )

        print(
            f"    % of anchor eval: "
            f"{100 * len(overlap) / len(anchor_eval):.6f}%"
        )


# ============================================================
# 6. Anchor evaluation × auxiliary non-training population
# ============================================================

print_header(
    "MOD-012 — CLEAN AUXILIARY EVIDENCE CANDIDATES"
)

for anchor in tasks:

    anchor_eval = populations[anchor]["eval"]

    if not anchor_eval:
        continue

    print()
    print(
        f"ANCHOR: {anchor}"
    )

    for auxiliary in tasks:

        if auxiliary == anchor:
            continue

        auxiliary_train = populations[auxiliary]["train"]
        auxiliary_eval = populations[auxiliary]["eval"]

        clean = (
            anchor_eval -
            auxiliary_train
        )

        prediction_overlap = (
            clean &
            auxiliary_eval
        )

        contaminated_eval = (
            anchor_eval &
            auxiliary_train
        )

        print()
        print(
            f"  Auxiliary: {auxiliary}"
        )

        print(
            f"    anchor eval population: "
            f"{len(anchor_eval):,}"
        )

        print(
            f"    anchor IDs in auxiliary train: "
            f"{len(contaminated_eval):,}"
        )

        print(
            f"    anchor IDs outside auxiliary train: "
            f"{len(clean):,}"
        )

        print(
            f"    clean IDs with auxiliary eval prediction: "
            f"{len(prediction_overlap):,}"
        )


# ============================================================
# 7. All-task training contamination
# ============================================================

print_header(
    "MOD-012 — ALL-TASK TRAINING CONTAMINATION CHECK"
)

for anchor in tasks:

    anchor_eval = populations[anchor]["eval"]

    if not anchor_eval:
        continue

    contaminated_by = []

    for auxiliary in tasks:

        if auxiliary == anchor:
            continue

        overlap = (
            anchor_eval &
            populations[auxiliary]["train"]
        )

        if overlap:
            contaminated_by.append(
                (
                    auxiliary,
                    len(overlap)
                )
            )

    print()
    print(
        f"{anchor} evaluation population: "
        f"{len(anchor_eval):,}"
    )

    if contaminated_by:

        for auxiliary, count in contaminated_by:

            print(
                f"  overlaps {auxiliary} training: "
                f"{count:,}"
            )

    else:

        print(
            "  No cross-task training overlap detected."
        )


# ============================================================
# 8. Interpretation gate
# ============================================================

print_header(
    "MOD-012 — INTERPRETATION GATE"
)

print(
    "An evaluation/evaluation overlap establishes that an "
    "ID-addressable auxiliary prediction exists on the same ticket."
)

print(
    "An anchor-evaluation/auxiliary-training overlap indicates "
    "that the auxiliary model's training population contains "
    "the anchor evaluation ticket."
)

print(
    "Such overlap requires explicit provenance treatment before "
    "the auxiliary prediction can be treated as independent "
    "evidence for the anchor evaluation."
)

print(
    "This audit does not automatically declare every overlap "
    "invalid; it identifies populations requiring interpretation."
)

print()
print(
    "No fusion model created."
)

print(
    "No predictions transformed."
)

print(
    "No target created."
)

print(
    "No artifact modified."
)

print()
print(
    "MOD-012 CROSS-TASK OVERLAP AUDIT COMPLETE"
)