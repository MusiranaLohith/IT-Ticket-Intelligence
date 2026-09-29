#!/usr/bin/env python3

import csv
from datetime import datetime
from pathlib import Path

csv.field_size_limit(1024 * 1024 * 1024)

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_TRAIN = (
    PROJECT_ROOT
    / "modeling/T2/splits/train.csv"
)

T7_TRAIN = (
    PROJECT_ROOT
    / "modeling/T7/splits/t7_train.csv"
)

T7_EVAL = (
    PROJECT_ROOT
    / "modeling/T7/splits/t7_evaluation.csv"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_rows(path):
    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        rows = []

        for row in reader:
            rows.append(row)

        return rows


def parse_creation(value):
    value = value.strip()

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
    ]

    for fmt in formats:

        try:
            return datetime.strptime(
                value,
                fmt
            )
        except ValueError:
            pass

    # Final fallback for ISO-like timestamps
    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise RuntimeError(
            f"Unable to parse Creation time: {value}"
        ) from exc


def print_header(title):
    print("\n" + "=" * 82)
    print(title)
    print("=" * 82)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

print("=" * 82)
print(
    "MOD-021 — T7 CHRONOLOGICAL OoF DEVELOPMENT-DESIGN AUDIT"
)
print("=" * 82)

print(
    "Purpose: determine whether the shared T2-train / T7-train "
    "population supports a legitimate chronology-preserving "
    "out-of-fold development design."
)

print(
    "\nNo model loading."
    "\nNo model fitting."
    "\nNo prediction generation."
    "\nNo artifact modification."
)


# ---------------------------------------------------------------------------
# Load populations
# ---------------------------------------------------------------------------

print_header(
    "MOD-021 — LOAD SHARED DEVELOPMENT POPULATION"
)

t2_rows = load_rows(T2_TRAIN)
t7_rows = load_rows(T7_TRAIN)
t7_eval_rows = load_rows(T7_EVAL)

t2_ids = {
    row["ID"].strip()
    for row in t2_rows
    if row.get("ID", "").strip()
}

t7_train_by_id = {
    row["ID"].strip(): row
    for row in t7_rows
    if row.get("ID", "").strip()
}

t7_eval_ids = {
    row["ID"].strip()
    for row in t7_eval_rows
    if row.get("ID", "").strip()
}

shared_ids = t2_ids & set(t7_train_by_id)

print(f"T2 train rows: {len(t2_rows):,}")
print(f"T7 train rows: {len(t7_rows):,}")
print(f"T7 evaluation rows: {len(t7_eval_rows):,}")

print(
    f"T2 train ∩ T7 train: "
    f"{len(shared_ids):,}"
)

print(
    f"Shared IDs outside T7 train: "
    f"{len(shared_ids - set(t7_train_by_id))}"
)

print(
    f"Shared IDs overlapping T7 evaluation: "
    f"{len(shared_ids & t7_eval_ids)}"
)


# ---------------------------------------------------------------------------
# Shared Creation-time distribution
# ---------------------------------------------------------------------------

print_header(
    "MOD-021 — SHARED POPULATION CREATION-TIME DISTRIBUTION"
)

shared_records = []

for ticket_id in shared_ids:

    row = t7_train_by_id[ticket_id]

    creation = parse_creation(
        row["Creation time"]
    )

    shared_records.append(
        {
            "ID": ticket_id,
            "Creation time": creation,
            "row": row,
        }
    )

shared_records.sort(
    key=lambda x: (
        x["Creation time"],
        x["ID"]
    )
)

print(
    f"Earliest shared Creation: "
    f"{shared_records[0]['Creation time']}"
)

print(
    f"Latest shared Creation: "
    f"{shared_records[-1]['Creation time']}"
)

print(
    f"Shared population size: "
    f"{len(shared_records):,}"
)


# ---------------------------------------------------------------------------
# Quantiles
# ---------------------------------------------------------------------------

print_header(
    "MOD-021 — SHARED POPULATION TEMPORAL QUANTILES"
)

n = len(shared_records)

quantile_positions = [
    ("Q00", 0.00),
    ("Q10", 0.10),
    ("Q20", 0.20),
    ("Q25", 0.25),
    ("Q33", 1 / 3),
    ("Q40", 0.40),
    ("Q50", 0.50),
    ("Q60", 0.60),
    ("Q67", 2 / 3),
    ("Q75", 0.75),
    ("Q80", 0.80),
    ("Q90", 0.90),
    ("Q100", 1.00),
]

for label, q in quantile_positions:

    index = min(
        n - 1,
        max(
            0,
            int(q * (n - 1))
        )
    )

    record = shared_records[index]

    print(
        f"{label:>4}: "
        f"{record['Creation time']} "
        f"ID={record['ID']}"
    )


# ---------------------------------------------------------------------------
# Candidate fold designs
# ---------------------------------------------------------------------------

print_header(
    "MOD-021 — CANDIDATE CHRONOLOGICAL OoF DESIGNS"
)

print("""
Candidate design A — 3 sequential blocks

  Fold 1:
    early development block predicted from earlier T7 history

  Fold 2:
    later development block predicted from earlier T7 history

  Fold 3:
    latest development block predicted from all earlier eligible
    T7 history

Requirement:
  Every prediction must be strictly later than its fitting population.

Candidate design B — 4 sequential blocks

  Same principle, with four chronological prediction blocks.

Candidate design C — expanding-window rolling prediction

  For each development block:
    fit on all eligible earlier T7 observations
    predict only the next development block

This is closest to a forward temporal evaluation procedure,
but may require more model fits.

The design must not use the frozen T7 evaluation population
for fitting, tuning, or development prediction generation.
""")


# ---------------------------------------------------------------------------
# Evaluate temporal feasibility for candidate block counts
# ---------------------------------------------------------------------------

print_header(
    "MOD-021 — BLOCK SIZE / TEMPORAL FEASIBILITY"
)

for block_count in [3, 4, 5]:

    base = n // block_count
    remainder = n % block_count

    blocks = []

    start = 0

    for i in range(block_count):

        size = base + (
            1 if i < remainder else 0
        )

        end = start + size

        block = shared_records[start:end]

        blocks.append(block)

        start = end

    print(
        f"\n{block_count}-block design:"
    )

    for i, block in enumerate(blocks, start=1):

        print(
            f"  Block {i}: "
            f"{len(block):,} rows | "
            f"{block[0]['Creation time']} "
            f"→ "
            f"{block[-1]['Creation time']}"
        )


# ---------------------------------------------------------------------------
# Strict temporal prediction feasibility
# ---------------------------------------------------------------------------

print_header(
    "MOD-021 — STRICT TEMPORAL OoF CONDITION"
)

print("""
For a valid chronological OoF prediction:

    max(Creation time of fitting population)
        <
    min(Creation time of prediction population)

for every prediction block.

Creation-time ties require deterministic ID ordering, matching the
frozen T7 split policy.

No future observation may contribute to the model used to predict
an earlier development observation.
""")


# ---------------------------------------------------------------------------
# Inspect T7 train chronology
# ---------------------------------------------------------------------------

print_header(
    "MOD-021 — T7 TRAIN TEMPORAL RANGE"
)

t7_train_records = []

for row in t7_rows:

    t7_train_records.append(
        (
            parse_creation(row["Creation time"]),
            row["ID"].strip()
        )
    )

t7_train_records.sort()

print(
    f"T7 train earliest: "
    f"{t7_train_records[0][0]}"
)

print(
    f"T7 train latest: "
    f"{t7_train_records[-1][0]}"
)

print(
    f"T7 evaluation earliest: "
    f"{min(
        parse_creation(row['Creation time'])
        for row in t7_eval_rows
    )}"
)

print(
    f"T7 evaluation latest: "
    f"{max(
        parse_creation(row['Creation time'])
        for row in t7_eval_rows
    )}"
)


# ---------------------------------------------------------------------------
# Verify shared population sits inside T7 training period
# ---------------------------------------------------------------------------

print_header(
    "MOD-021 — SHARED POPULATION / T7 TRAINING PERIOD"
)

t7_train_min = t7_train_records[0][0]
t7_train_max = t7_train_records[-1][0]

outside = [
    record
    for record in shared_records
    if (
        record["Creation time"] < t7_train_min
        or
        record["Creation time"] > t7_train_max
    )
]

print(
    f"Shared rows outside T7 training temporal range: "
    f"{len(outside)}"
)


# ---------------------------------------------------------------------------
# Outcome availability audit
# ---------------------------------------------------------------------------

print_header(
    "MOD-021 — DEVELOPMENT OUTCOME / CENSORING AVAILABILITY"
)

event_counts = {
    "1": 0,
    "0": 0,
    "other": 0,
}

for record in shared_records:

    event = str(
        record["row"].get("event", "")
    ).strip()

    if event in event_counts:
        event_counts[event] += 1
    else:
        event_counts["other"] += 1

print(
    f"event=1: {event_counts['1']:,}"
)

print(
    f"event=0: {event_counts['0']:,}"
)

print(
    f"other/missing: {event_counts['other']:,}"
)


# ---------------------------------------------------------------------------
# Duration availability
# ---------------------------------------------------------------------------

duration_missing = 0
duration_invalid = 0

for record in shared_records:

    value = str(
        record["row"].get(
            "duration_seconds",
            ""
        )
    ).strip()

    if not value:
        duration_missing += 1
        continue

    try:
        duration = float(value)

        if duration <= 0:
            duration_invalid += 1

    except ValueError:
        duration_invalid += 1

print(
    f"Missing duration: "
    f"{duration_missing:,}"
)

print(
    f"Invalid/non-positive duration: "
    f"{duration_invalid:,}"
)


# ---------------------------------------------------------------------------
# Proposed design constraints
# ---------------------------------------------------------------------------

print_header(
    "MOD-021 — DESIGN CONSTRAINTS TO CARRY FORWARD"
)

print("""
1. Development population:
     T2 train ∩ T7 train = shared population.

2. T7 evaluation:
     completely excluded from development fitting/prediction.

3. Prediction boundary:
     Creation.

4. Feature information:
     Creation-time only.

5. Target:
     Native T7 censored survival target.

6. Censoring:
     event=0 remains right-censored.

7. Temporal ordering:
     prediction block must occur after its fitting population.

8. Tie handling:
     Creation timestamp ties ordered deterministically by ID,
     consistent with the frozen T7 split policy.

9. No random K-fold:
     temporal task requires chronology-preserving development.

10. No in-sample prediction:
     predictions for a ticket cannot come from a model fitted
     on that same ticket.

11. Native outputs:
     preserve survival-native outputs:
       predicted median survival
       survival probability at frozen horizons.

12. No fusion training yet:
     this module only establishes the development design.
""")


# ---------------------------------------------------------------------------
# Preliminary design recommendation
# ---------------------------------------------------------------------------

print_header(
    "MOD-021 — PRELIMINARY DESIGN DECISION"
)

print("""
The shared population is large enough to support a chronology-
preserving development design.

The preferred structure is an expanding-window chronological
OoF procedure over the 20,648 shared tickets.

However, the exact number of folds and minimum fitting-history
requirement should be frozen before execution.

No prediction should be generated until that design is explicitly
recorded and audited.
""")


# ---------------------------------------------------------------------------
# Integrity
# ---------------------------------------------------------------------------

print_header(
    "MOD-021 — INTEGRITY CHECKS"
)

checks = [
    (
        "Shared development population is non-empty",
        len(shared_records) > 0
    ),
    (
        "Shared population has unique IDs",
        len({
            r["ID"]
            for r in shared_records
        }) == len(shared_records)
    ),
    (
        "Shared population does not overlap T7 evaluation",
        len(
            shared_ids
            & t7_eval_ids
        ) == 0
    ),
    (
        "Shared population lies within T7 training range",
        len(outside) == 0
    ),
    (
        "Shared outcomes use valid survival event values",
        event_counts["other"] == 0
    ),
    (
        "Shared durations are valid",
        duration_missing == 0
        and duration_invalid == 0
    ),
]

for label, passed in checks:

    print(
        f"  {label}: "
        f"{'PASS' if passed else 'FAIL'}"
    )


print("\nNo model loaded.")
print("No model trained.")
print("No prediction generated.")
print("No artifact modified.")

print(
    "\nMOD-021 T7 CHRONOLOGICAL OoF DEVELOPMENT-DESIGN "
    "AUDIT COMPLETE"
)

print("STATUS: COMPLETE / PASS")