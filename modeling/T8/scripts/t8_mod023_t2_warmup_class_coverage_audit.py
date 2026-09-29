#!/usr/bin/env python3

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

csv.field_size_limit(1024 * 1024 * 1024)

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_ROOT = PROJECT_ROOT / "modeling/T2"

T2_TRAIN = T2_ROOT / "splits/train.csv"
T2_TEST = T2_ROOT / "splits/test.csv"
T2_VALIDATION = T2_ROOT / "splits/validation.csv"

T2_CLOSURE = T2_ROOT / "analysis/t2_final_closure.json"
T2_SELECTION = T2_ROOT / "analysis/t2_final_model_selection.json"
T2_CONTRACT = T2_ROOT / "contracts/t2_model_contract.json"
T2_SPLIT_REPORT = T2_ROOT / "splits/t2_split_report.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_csv(path):
    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:
        return list(csv.DictReader(f))


def load_json(path):
    if not path.exists():
        return None

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace"
    ) as f:
        return json.load(f)


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

    parsed = None

    for fmt in formats:
        try:
            parsed = datetime.strptime(
                value,
                fmt
            )
            break
        except ValueError:
            pass

    if parsed is None:
        try:
            parsed = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise RuntimeError(
                f"Unable to parse Creation time: {value}"
            ) from exc

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=timezone.utc
        )
    else:
        parsed = parsed.astimezone(
            timezone.utc
        )

    return parsed


def print_header(title):
    print("\n" + "=" * 92)
    print(title)
    print("=" * 92)


def get_target(row):
    return str(
        row.get("target_priority", "")
    ).strip()


def get_id(row):
    return str(
        row.get("ID", "")
    ).strip()


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

print("=" * 92)
print(
    "MOD-023 — T2 CHRONOLOGICAL WARM-UP / CLASS-COVERAGE AUDIT"
)
print("=" * 92)

print(
    "Purpose: identify the earliest defensible T2 chronological "
    "fitting boundary for joint T2/T7 development prediction."
)

print(
    "\nNo model loading."
    "\nNo model fitting."
    "\nNo prediction generation."
    "\nNo artifact modification."
)


# ---------------------------------------------------------------------------
# Load T2 populations
# ---------------------------------------------------------------------------

print_header(
    "MOD-023 — LOAD T2 POPULATIONS"
)

train_rows = load_csv(T2_TRAIN)
test_rows = load_csv(T2_TEST)
validation_rows = load_csv(T2_VALIDATION)

print(
    f"T2 train rows: {len(train_rows):,}"
)

print(
    f"T2 validation rows: {len(validation_rows):,}"
)

print(
    f"T2 test rows: {len(test_rows):,}"
)


# ---------------------------------------------------------------------------
# Validate training IDs
# ---------------------------------------------------------------------------

print_header(
    "MOD-023 — T2 TRAIN ID / TARGET INTEGRITY"
)

train_ids = [
    get_id(row)
    for row in train_rows
]

duplicate_train_ids = (
    len(train_ids)
    -
    len(set(train_ids))
)

missing_ids = sum(
    1
    for ticket_id in train_ids
    if not ticket_id
)

missing_targets = sum(
    1
    for row in train_rows
    if not get_target(row)
)

print(
    f"Unique T2 train IDs: "
    f"{len(set(train_ids)):,}"
)

print(
    f"Duplicate T2 train IDs: "
    f"{duplicate_train_ids:,}"
)

print(
    f"Missing T2 train IDs: "
    f"{missing_ids:,}"
)

print(
    f"Missing target_priority: "
    f"{missing_targets:,}"
)


# ---------------------------------------------------------------------------
# Chronological ordering
# ---------------------------------------------------------------------------

print_header(
    "MOD-023 — CHRONOLOGICAL T2 TRAINING ORDER"
)

records = []

for row in train_rows:

    ticket_id = get_id(row)

    if not ticket_id:
        continue

    creation = parse_creation(
        row["Creation time"]
    )

    target = get_target(row)

    records.append(
        {
            "ID": ticket_id,
            "Creation time": creation,
            "target": target,
            "row": row,
        }
    )


records.sort(
    key=lambda x: (
        x["Creation time"],
        x["ID"]
    )
)

print(
    f"Earliest T2 train Creation: "
    f"{records[0]['Creation time']}"
)

print(
    f"Latest T2 train Creation: "
    f"{records[-1]['Creation time']}"
)

print(
    "\nFirst 10 chronological T2 training records:"
)

for record in records[:10]:

    print(
        f"  {record['Creation time']} "
        f"ID={record['ID']} "
        f"target={record['target']}"
    )


# ---------------------------------------------------------------------------
# Overall class distribution
# ---------------------------------------------------------------------------

print_header(
    "MOD-023 — FULL T2 TRAIN TARGET DISTRIBUTION"
)

classes = [
    "P1",
    "P2",
    "P3",
    "P4",
    "P5",
]

overall_counts = {
    target: 0
    for target in classes
}

other_targets = {}

for record in records:

    target = record["target"]

    if target in overall_counts:
        overall_counts[target] += 1
    else:
        other_targets[target] = (
            other_targets.get(target, 0)
            + 1
        )

for target in classes:

    count = overall_counts[target]

    pct = (
        count / len(records) * 100
        if records
        else 0
    )

    print(
        f"{target}: "
        f"{count:,} "
        f"({pct:.6f}%)"
    )

if other_targets:

    print(
        "\nOther target values:"
    )

    for target, count in sorted(
        other_targets.items()
    ):

        print(
            f"  {repr(target)}: "
            f"{count:,}"
        )


# ---------------------------------------------------------------------------
# First appearance of each class
# ---------------------------------------------------------------------------

print_header(
    "MOD-023 — FIRST CHRONOLOGICAL APPEARANCE OF EACH PRIORITY"
)

first_appearance = {}

for record in records:

    target = record["target"]

    if target not in classes:
        continue

    if target not in first_appearance:

        first_appearance[target] = record


for target in classes:

    record = first_appearance.get(
        target
    )

    if record is None:

        print(
            f"{target}: NEVER APPEARS"
        )

    else:

        print(
            f"{target}: "
            f"{record['Creation time']} "
            f"ID={record['ID']}"
        )


# ---------------------------------------------------------------------------
# Cumulative class coverage
# ---------------------------------------------------------------------------

print_header(
    "MOD-023 — CUMULATIVE CLASS-COVERAGE MILESTONES"
)

required_classes = set(classes)

seen = set()

milestone_records = []

for index, record in enumerate(
    records,
    start=1
):

    target = record["target"]

    if target in required_classes:
        seen.add(target)

    if len(seen) == len(required_classes):

        milestone_records.append(
            (
                index,
                record
            )
        )

        break


if milestone_records:

    index, record = milestone_records[0]

    print(
        f"All five classes first observed by "
        f"chronological row: {index:,}"
    )

    print(
        f"Boundary record:"
    )

    print(
        f"  Creation: {record['Creation time']}"
    )

    print(
        f"  ID: {record['ID']}"
    )

    print(
        f"  Target: {record['target']}"
    )

else:

    print(
        "All-five-class coverage was NOT reached."
    )


# ---------------------------------------------------------------------------
# Candidate fitting boundaries
# ---------------------------------------------------------------------------

print_header(
    "MOD-023 — CANDIDATE CHRONOLOGICAL FITTING BOUNDARIES"
)

candidate_quantiles = [
    ("Q10", 0.10),
    ("Q20", 0.20),
    ("Q25", 0.25),
    ("Q30", 0.30),
    ("Q33", 1 / 3),
    ("Q40", 0.40),
    ("Q50", 0.50),
    ("Q60", 0.60),
    ("Q67", 2 / 3),
    ("Q75", 0.75),
]

n = len(records)

for label, q in candidate_quantiles:

    index = min(
        n - 1,
        max(
            0,
            int(q * (n - 1))
        )
    )

    fitting = records[
        :index + 1
    ]

    counts = {
        target: 0
        for target in classes
    }

    for record in fitting:

        target = record["target"]

        if target in counts:
            counts[target] += 1

    print(
        f"\n{label}: "
        f"{len(fitting):,} fitting rows"
    )

    print(
        f"  Through: "
        f"{fitting[-1]['Creation time']}"
    )

    print(
        "  "
        +
        " | ".join(
            f"{target}={counts[target]:,}"
            for target in classes
        )
    )


# ---------------------------------------------------------------------------
# Five-block T2 history analysis
# ---------------------------------------------------------------------------

print_header(
    "MOD-023 — FIVE-BLOCK T2 FITTING-HISTORY CLASS COVERAGE"
)

block_count = 5

base = n // block_count
remainder = n % block_count

blocks = []

start = 0

for i in range(block_count):

    size = base + (
        1
        if i < remainder
        else 0
    )

    end = start + size

    blocks.append(
        records[start:end]
    )

    start = end


for block_index, block in enumerate(
    blocks,
    start=1
):

    prediction_first = block[0]

    boundary = (
        prediction_first["Creation time"],
        prediction_first["ID"]
    )

    fitting = [
        record
        for record in records
        if (
            record["Creation time"],
            record["ID"]
        )
        <
        boundary
    ]

    counts = {
        target: 0
        for target in classes
    }

    for record in fitting:

        target = record["target"]

        if target in counts:
            counts[target] += 1

    missing_classes = [
        target
        for target in classes
        if counts[target] == 0
    ]

    print(
        f"\nBlock {block_index}:"
    )

    print(
        f"  Prediction rows: "
        f"{len(block):,}"
    )

    print(
        f"  First prediction: "
        f"{prediction_first['Creation time']} "
        f"ID={prediction_first['ID']}"
    )

    print(
        f"  Earlier T2 fitting rows: "
        f"{len(fitting):,}"
    )

    print(
        "  Class counts: "
        +
        " | ".join(
            f"{target}={counts[target]:,}"
            for target in classes
        )
    )

    print(
        f"  Missing classes: "
        f"{missing_classes if missing_classes else 'NONE'}"
    )


# ---------------------------------------------------------------------------
# Earliest boundary with all classes
# ---------------------------------------------------------------------------

print_header(
    "MOD-023 — EARLIEST FIVE-CLASS T2 FITTING POPULATION"
)

all_class_boundary = None

for index, record in enumerate(
    records
):

    fitting = records[:index]

    seen = {
        r["target"]
        for r in fitting
        if r["target"] in required_classes
    }

    if seen == required_classes:

        all_class_boundary = {
            "index": index,
            "record": record,
            "fitting": fitting,
        }

        break


if all_class_boundary is None:

    print(
        "No chronological boundary exists where all five "
        "priority classes are represented."
    )

else:

    index = all_class_boundary["index"]
    record = all_class_boundary["record"]
    fitting = all_class_boundary["fitting"]

    print(
        f"Earliest prediction position with all-five-class "
        f"fitting history: {index:,}"
    )

    print(
        f"First ticket that can be predicted after this boundary:"
    )

    print(
        f"  Creation: {record['Creation time']}"
    )

    print(
        f"  ID: {record['ID']}"
    )

    print(
        f"  Target: {record['target']}"
    )

    counts = {
        target: 0
        for target in classes
    }

    for row in fitting:

        if row["target"] in counts:
            counts[row["target"]] += 1

    print(
        "\nFitting-population class counts:"
    )

    for target in classes:

        print(
            f"  {target}: "
            f"{counts[target]:,}"
        )


# ---------------------------------------------------------------------------
# Existing T2 closure / selection metadata
# ---------------------------------------------------------------------------

print_header(
    "MOD-023 — EXISTING T2 CLOSURE / SELECTION METADATA"
)

for label, path in [
    ("T2 final closure", T2_CLOSURE),
    ("T2 final model selection", T2_SELECTION),
    ("T2 model contract", T2_CONTRACT),
    ("T2 split report", T2_SPLIT_REPORT),
]:

    data = load_json(path)

    print(
        f"\n{label}: "
        f"{'FOUND' if data is not None else 'NOT FOUND'}"
    )

    if data is None:
        continue

    if isinstance(data, dict):

        # Print only shallow keys here. This is a discovery audit,
        # not a full semantic reconstruction of the JSON.
        print(
            "  Top-level keys:"
        )

        for key in data.keys():

            print(
                f"    {key}"
            )


# ---------------------------------------------------------------------------
# Existing validation/test boundary
# ---------------------------------------------------------------------------

print_header(
    "MOD-023 — EXISTING T2 VALIDATION / TEST TEMPORAL BOUNDARIES"
)

for label, rows in [
    ("T2 validation", validation_rows),
    ("T2 test", test_rows),
]:

    parsed = []

    for row in rows:

        if not get_id(row):
            continue

        parsed.append(
            (
                parse_creation(
                    row["Creation time"]
                ),
                get_id(row)
            )
        )

    parsed.sort()

    if not parsed:
        print(
            f"{label}: EMPTY"
        )
        continue

    print(
        f"{label}:"
    )

    print(
        f"  earliest: {parsed[0][0]}"
    )

    print(
        f"  latest: {parsed[-1][0]}"
    )

    print(
        f"  rows: {len(parsed):,}"
    )


# ---------------------------------------------------------------------------
# Design interpretation
# ---------------------------------------------------------------------------

print_header(
    "MOD-023 — DESIGN INTERPRETATION"
)

print(
    """
The T2 OoF generator must satisfy all of the following:

1. A prediction ticket is excluded from its own fitting data.

2. Fitting observations precede the prediction ticket
   chronologically.

3. T2 test remains completely untouched.

4. Existing T2 validation predictions are not substituted for
   OoF predictions on the T2 training population.

5. The frozen T2 target semantics remain unchanged.

6. The earliest prediction boundary must have a defensible
   fitting population.

7. All required target classes should be represented before
   using a chronological fitting population for a five-class
   T2 model, unless the frozen T2 implementation explicitly
   establishes another valid handling.

8. No arbitrary warm-up cutoff should be introduced merely to
   obtain a convenient cohort size.
"""
)


# ---------------------------------------------------------------------------
# Integrity checks
# ---------------------------------------------------------------------------

print_header(
    "MOD-023 — INTEGRITY CHECKS"
)

all_classes_present = (
    set(
        target
        for target in overall_counts
        if overall_counts[target] > 0
    )
    == required_classes
)

checks = [
    (
        "T2 training population is non-empty",
        len(records) > 0
    ),
    (
        "T2 train IDs are unique",
        duplicate_train_ids == 0
    ),
    (
        "T2 train IDs are populated",
        missing_ids == 0
    ),
    (
        "T2 train targets are populated",
        missing_targets == 0
    ),
    (
        "All five required priorities occur in T2 train",
        all_classes_present
    ),
    (
        "Chronological records are ordered",
        all(
            (
                records[i]["Creation time"],
                records[i]["ID"]
            )
            <=
            (
                records[i + 1]["Creation time"],
                records[i + 1]["ID"]
            )
            for i in range(
                len(records) - 1
            )
        )
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
    "\nMOD-023 T2 CHRONOLOGICAL WARM-UP / "
    "CLASS-COVERAGE AUDIT COMPLETE"
)

print(
    "STATUS: COMPLETE / REVIEW REQUIRED"
)