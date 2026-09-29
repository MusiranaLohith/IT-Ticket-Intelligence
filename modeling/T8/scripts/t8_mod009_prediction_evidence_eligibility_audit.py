#!/usr/bin/env python3

import csv
from pathlib import Path
from collections import Counter


# ============================================================
# T8 MOD-009
# Prediction-Evidence Eligibility & Missingness Audit
#
# READ-ONLY
# No model loading
# No training
# No raw Mozilla archive access
# No synthetic target
# No fusion
# No artifact modification
# ============================================================

csv.field_size_limit(2**31 - 1)


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

MODELING_ROOT = PROJECT_ROOT / "modeling"

LAYER_A = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T8_LAYER_A_TICKET_EVIDENCE_derived.csv"
)

T2_PRED = (
    MODELING_ROOT /
    "T2/analysis/t2_final_test_predictions.csv"
)

T4_EVAL = (
    MODELING_ROOT /
    "T4/derived/t4_eval.csv"
)

T5_EVAL = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T5_EVAL_GROUP_AWARE.csv"
)

T7_PRED = (
    MODELING_ROOT /
    "T7/derived/t7_mod010_evaluation_predictions.csv"
)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def normalize_id(value):
    if value is None:
        return None

    value = str(value).strip()

    return value if value else None


def read_id_set(path, id_column):
    ids = set()

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        if id_column not in reader.fieldnames:
            raise RuntimeError(
                f"{id_column!r} not found in {path}. "
                f"Columns: {reader.fieldnames}"
            )

        for row in reader:
            value = normalize_id(row[id_column])

            if value is not None:
                ids.add(value)

    return ids


def print_header(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


# ============================================================
# 1. Canonical T8 population
# ============================================================

print_header(
    "MOD-009 — CANONICAL T8 POPULATION"
)

canonical_ids = read_id_set(
    LAYER_A,
    "ticket_id"
)

print(
    f"Canonical T8 unique tickets: "
    f"{len(canonical_ids)}"
)


# ============================================================
# 2. Read prediction/evaluation populations
# ============================================================

print_header(
    "MOD-009 — TASK EVIDENCE POPULATIONS"
)

T2_IDS = read_id_set(
    T2_PRED,
    "ID"
)

T4_IDS = read_id_set(
    T4_EVAL,
    "ID"
)

T5_IDS = read_id_set(
    T5_EVAL,
    "ID"
)

T7_IDS = read_id_set(
    T7_PRED,
    "ID"
)

task_sets = {
    "T2": T2_IDS,
    "T4": T4_IDS,
    "T5": T5_IDS,
    "T7": T7_IDS,
}

for task, ids in task_sets.items():

    overlap = ids & canonical_ids
    outside = ids - canonical_ids

    print()
    print(f"{task}")
    print(f"  Artifact/evaluation IDs: {len(ids)}")
    print(f"  In canonical T8: {len(overlap)}")
    print(f"  Outside canonical T8: {len(outside)}")
    print(
        f"  Canonical coverage: "
        f"{len(overlap) / len(canonical_ids) * 100:.6f}%"
    )


# ============================================================
# 3. Canonical eligibility matrix
# ============================================================

print_header(
    "MOD-009 — CANONICAL PREDICTION-EVIDENCE ELIGIBILITY"
)

task_order = ["T2", "T4", "T5", "T7"]

pattern_counts = Counter()

for ticket_id in canonical_ids:

    pattern = tuple(
        task
        for task in task_order
        if ticket_id in task_sets[task]
    )

    pattern_counts[pattern] += 1


print(
    "Eligibility is defined only by existence of an "
    "ID-addressable completed-task evaluation artifact."
)

print()
print("Evidence-pattern distribution:")

for pattern, count in sorted(
    pattern_counts.items(),
    key=lambda x: (-x[1], x[0])
):

    label = "+".join(pattern) if pattern else "NONE"

    percentage = (
        count /
        len(canonical_ids) *
        100
    )

    print(
        f"  {label:<12} "
        f"{count:>8} "
        f"({percentage:>9.6f}%)"
    )


# ============================================================
# 4. Single-task availability
# ============================================================

print_header(
    "MOD-009 — SINGLE-TASK EVIDENCE AVAILABILITY"
)

for task in task_order:

    available = (
        canonical_ids &
        task_sets[task]
    )

    unavailable = (
        canonical_ids -
        task_sets[task]
    )

    print()
    print(f"{task}")
    print(
        f"  Available:   {len(available):>8} "
        f"({len(available) / len(canonical_ids) * 100:.6f}%)"
    )
    print(
        f"  Unavailable: {len(unavailable):>8} "
        f"({len(unavailable) / len(canonical_ids) * 100:.6f}%)"
    )


# ============================================================
# 5. Pairwise overlaps
# ============================================================

print_header(
    "MOD-009 — PAIRWISE EVIDENCE OVERLAP"
)

for i, task_a in enumerate(task_order):

    for task_b in task_order[i + 1:]:

        overlap = (
            task_sets[task_a] &
            task_sets[task_b] &
            canonical_ids
        )

        print(
            f"{task_a} + {task_b}: "
            f"{len(overlap):>8} "
            f"({len(overlap) / len(canonical_ids) * 100:.6f}%)"
        )


# ============================================================
# 6. Triple overlaps
# ============================================================

print_header(
    "MOD-009 — TRIPLE EVIDENCE OVERLAP"
)

triples = [
    ("T2", "T4", "T5"),
    ("T2", "T4", "T7"),
    ("T2", "T5", "T7"),
    ("T4", "T5", "T7"),
]

for a, b, c in triples:

    overlap = (
        task_sets[a] &
        task_sets[b] &
        task_sets[c] &
        canonical_ids
    )

    print(
        f"{a} + {b} + {c}: "
        f"{len(overlap):>8} "
        f"({len(overlap) / len(canonical_ids) * 100:.6f}%)"
    )


# ============================================================
# 7. All-four overlap
# ============================================================

print_header(
    "MOD-009 — ALL-FOUR PREDICTION EVIDENCE OVERLAP"
)

all_four = (
    T2_IDS &
    T4_IDS &
    T5_IDS &
    T7_IDS &
    canonical_ids
)

print(
    f"T2 + T4 + T5 + T7: "
    f"{len(all_four)}"
)

print(
    f"Canonical percentage: "
    f"{len(all_four) / len(canonical_ids) * 100:.6f}%"
)


# ============================================================
# 8. Minimum evidence counts
# ============================================================

print_header(
    "MOD-009 — NUMBER OF AVAILABLE TASK SIGNALS PER TICKET"
)

signal_count_distribution = Counter()

for ticket_id in canonical_ids:

    count = sum(
        ticket_id in task_sets[task]
        for task in task_order
    )

    signal_count_distribution[count] += 1


for count in sorted(signal_count_distribution):

    n = signal_count_distribution[count]

    print(
        f"  {count} available task signals: "
        f"{n:>8} "
        f"({n / len(canonical_ids) * 100:.6f}%)"
    )


# ============================================================
# 9. Candidate fusion populations
# ============================================================

print_header(
    "MOD-009 — DESCRIPTIVE CANDIDATE FUSION POPULATIONS"
)

population_definitions = {
    "T2+T5": T2_IDS & T5_IDS,
    "T2+T7": T2_IDS & T7_IDS,
    "T4+T5": T4_IDS & T5_IDS,
    "T4+T7": T4_IDS & T7_IDS,
    "T5+T7": T5_IDS & T7_IDS,
    "T2+T4+T5": T2_IDS & T4_IDS & T5_IDS,
    "T2+T4+T7": T2_IDS & T4_IDS & T7_IDS,
    "T2+T5+T7": T2_IDS & T5_IDS & T7_IDS,
    "T4+T5+T7": T4_IDS & T5_IDS & T7_IDS,
    "T2+T4+T5+T7": all_four,
}

for name, ids in population_definitions.items():

    ids = ids & canonical_ids

    print(
        f"{name:<15} "
        f"{len(ids):>8} "
        f"({len(ids) / len(canonical_ids) * 100:.6f}%)"
    )


# ============================================================
# 10. Explicit semantic missingness statement
# ============================================================

print_header(
    "MOD-009 — MISSINGNESS SEMANTICS"
)

print(
    "T2 unavailable = no ID-addressable held-out T2 prediction "
    "artifact for that canonical ticket."
)

print(
    "T4 unavailable = no ID-addressable held-out T4 evaluation "
    "ranking evidence for that canonical ticket."
)

print(
    "T5 unavailable = no ID-addressable held-out T5 evaluation "
    "probability evidence for that canonical ticket."
)

print(
    "T7 unavailable = no ID-addressable held-out T7 survival "
    "prediction artifact for that canonical ticket."
)

print(
    "Unavailable evidence is NOT interpreted as a negative prediction, "
    "negative outcome, zero score, or model failure."
)

print(
    "T3 remains excluded from this matrix because its preserved "
    "locked-test predictions are not currently ID-addressable."
)


# ============================================================
# 11. Integrity checks
# ============================================================

print_header(
    "MOD-009 — INTEGRITY CHECKS"
)

assert len(canonical_ids) == 513816

assert T2_IDS <= canonical_ids
assert T4_IDS <= canonical_ids
assert T5_IDS <= canonical_ids
assert T7_IDS <= canonical_ids

for task, ids in task_sets.items():

    assert len(ids) == len(
        ids & canonical_ids
    )

print("Canonical population assertion: PASS")
print("T2 population containment: PASS")
print("T4 population containment: PASS")
print("T5 population containment: PASS")
print("T7 population containment: PASS")


# ============================================================
# 12. Final status
# ============================================================

print_header(
    "MOD-009 — FINAL STATUS"
)

print(
    "This operation is descriptive only."
)

print(
    "No fusion population has been selected."
)

print(
    "No synthetic target has been created."
)

print(
    "No probabilities have been transformed."
)

print(
    "No missing evidence has been imputed."
)

print(
    "No task has been assigned a negative value because "
    "its evidence is unavailable."
)

print()
print(
    "MOD-009 COMPLETE"
)