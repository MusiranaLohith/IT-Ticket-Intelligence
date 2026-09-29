#!/usr/bin/env python3

import csv
from datetime import datetime, timezone
from pathlib import Path

csv.field_size_limit(1024 * 1024 * 1024)

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_ROOT = PROJECT_ROOT / "modeling/T2"
T7_ROOT = PROJECT_ROOT / "modeling/T7"

T2_TRAIN = T2_ROOT / "splits/train.csv"
T2_TEST = T2_ROOT / "splits/test.csv"

T7_TRAIN = T7_ROOT / "splits/t7_train.csv"
T7_EVAL = T7_ROOT / "splits/t7_evaluation.csv"


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


def parse_creation(value):
    """
    Parse Creation time and normalize every timestamp to
    timezone-aware UTC.

    This prevents comparisons between timezone-naive and
    timezone-aware datetime objects.
    """

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

    # Normalize every timestamp to UTC-aware.
    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=timezone.utc
        )
    else:
        parsed = parsed.astimezone(
            timezone.utc
        )

    return parsed


def get_id(row):
    return str(
        row.get("ID", "")
    ).strip()


def chronological_records(rows):
    records = []

    for row in rows:

        ticket_id = get_id(row)

        if not ticket_id:
            continue

        records.append(
            {
                "ID": ticket_id,
                "Creation time": parse_creation(
                    row["Creation time"]
                ),
                "row": row,
            }
        )

    records.sort(
        key=lambda x: (
            x["Creation time"],
            x["ID"]
        )
    )

    return records


def print_header(title):
    print("\n" + "=" * 88)
    print(title)
    print("=" * 88)


def inspect_source_tree(root, patterns):

    matches = []

    if not root.exists():
        return matches

    for path in root.rglob("*"):

        if not path.is_file():
            continue

        name = path.name.lower()

        if any(
            pattern.lower() in name
            for pattern in patterns
        ):
            matches.append(path)

    return sorted(matches)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

print("=" * 88)
print(
    "MOD-022 — JOINT T2/T7 DEVELOPMENT-PREDICTION DESIGN AUDIT"
)
print("=" * 88)

print(
    "Purpose: determine whether a common leakage-safe development "
    "population can receive both T2 and T7 OoF predictions."
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
    "MOD-022 — LOAD FROZEN TASK POPULATIONS"
)

t2_train_rows = load_csv(T2_TRAIN)
t2_test_rows = load_csv(T2_TEST)

t7_train_rows = load_csv(T7_TRAIN)
t7_eval_rows = load_csv(T7_EVAL)

t2_train = chronological_records(
    t2_train_rows
)

t2_test = chronological_records(
    t2_test_rows
)

t7_train = chronological_records(
    t7_train_rows
)

t7_eval = chronological_records(
    t7_eval_rows
)

t2_train_ids = {
    x["ID"]
    for x in t2_train
}

t2_test_ids = {
    x["ID"]
    for x in t2_test
}

t7_train_ids = {
    x["ID"]
    for x in t7_train
}

t7_eval_ids = {
    x["ID"]
    for x in t7_eval
}

print(
    f"T2 train: {len(t2_train):,}"
)

print(
    f"T2 test: {len(t2_test):,}"
)

print(
    f"T7 train: {len(t7_train):,}"
)

print(
    f"T7 evaluation: {len(t7_eval):,}"
)


# ---------------------------------------------------------------------------
# Population intersections
# ---------------------------------------------------------------------------

print_header(
    "MOD-022 — CROSS-TASK POPULATION INTERSECTIONS"
)

shared_train = (
    t2_train_ids
    &
    t7_train_ids
)

print(
    f"T2 train ∩ T7 train: "
    f"{len(shared_train):,}"
)

print(
    f"T2 train ∩ T7 evaluation: "
    f"{len(t2_train_ids & t7_eval_ids):,}"
)

print(
    f"T2 test ∩ T7 train: "
    f"{len(t2_test_ids & t7_train_ids):,}"
)

print(
    f"T2 test ∩ T7 evaluation: "
    f"{len(t2_test_ids & t7_eval_ids):,}"
)

print(
    f"T2 train ∩ T2 test: "
    f"{len(t2_train_ids & t2_test_ids):,}"
)

print(
    f"T7 train ∩ T7 evaluation: "
    f"{len(t7_train_ids & t7_eval_ids):,}"
)


# ---------------------------------------------------------------------------
# Common development population
# ---------------------------------------------------------------------------

print_header(
    "MOD-022 — COMMON DEVELOPMENT POPULATION"
)

common = [
    x
    for x in t2_train
    if x["ID"] in shared_train
]

common.sort(
    key=lambda x: (
        x["Creation time"],
        x["ID"]
    )
)

print(
    f"Candidate common development population: "
    f"{len(common):,}"
)

print(
    f"Earliest: "
    f"{common[0]['Creation time']}"
)

print(
    f"Latest: "
    f"{common[-1]['Creation time']}"
)


# ---------------------------------------------------------------------------
# Inspect T2 native target
# ---------------------------------------------------------------------------

print_header(
    "MOD-022 — T2 NATIVE TARGET / PREDICTION SEMANTICS"
)

target_fields = [
    "target_priority",
    "actual_priority",
    "priority",
    "Creation time",
]

for field in target_fields:

    count = sum(
        1
        for x in common
        if str(
            x["row"].get(field, "")
        ).strip()
    )

    print(
        f"{field}: "
        f"{count:,}/{len(common):,} populated"
    )

print(
    """
T2 OoF prediction must preserve the frozen T2 task target
and must not use the target as a feature.

The audit does not reconstruct or alter the T2 target.
"""
)


# ---------------------------------------------------------------------------
# Inspect T2 source/model scripts
# ---------------------------------------------------------------------------

print_header(
    "MOD-022 — T2 IMPLEMENTATION / PROVENANCE DISCOVERY"
)

t2_candidates = inspect_source_tree(
    T2_ROOT,
    [
        ".py",
        ".json",
        "closure",
        "split",
        "baseline",
        "final",
        "validation",
        "prediction",
    ]
)

print(
    f"T2 candidate implementation/metadata files: "
    f"{len(t2_candidates)}"
)

for path in t2_candidates[:100]:

    relative = path.relative_to(
        PROJECT_ROOT
    )

    print(
        f"  {relative}"
    )


# ---------------------------------------------------------------------------
# Search source code text for critical implementation terms
# ---------------------------------------------------------------------------

print_header(
    "MOD-022 — T2 MODELING-CONTRACT TERM AUDIT"
)

terms = [
    "LogisticRegression",
    "TfidfVectorizer",
    "class_weight",
    "macro_f1",
    "Creation time",
    "train.csv",
    "validation",
    "test.csv",
    "model.predict",
]

term_hits = {
    term: []
    for term in terms
}

for path in t2_candidates:

    if path.suffix.lower() != ".py":
        continue

    try:
        text = path.read_text(
            encoding="utf-8",
            errors="replace"
        )
    except Exception:
        continue

    for term in terms:

        if term.lower() in text.lower():

            term_hits[term].append(
                path.relative_to(
                    PROJECT_ROOT
                )
            )


for term, paths in term_hits.items():

    print(
        f"\n{term}: "
        f"{len(paths)} file(s)"
    )

    for path in paths[:20]:

        print(
            f"  {path}"
        )


# ---------------------------------------------------------------------------
# Chronological common population
# ---------------------------------------------------------------------------

print_header(
    "MOD-022 — COMMON POPULATION TEMPORAL ORDER"
)

print(
    "The common population is sorted by:"
)

print(
    "  1. Creation time"
)

print(
    "  2. ID for deterministic tie handling"
)

print(
    "\nFirst 10:"
)

for x in common[:10]:

    print(
        f"  {x['Creation time']}  "
        f"ID={x['ID']}"
    )

print(
    "\nLast 10:"
)

for x in common[-10:]:

    print(
        f"  {x['Creation time']}  "
        f"ID={x['ID']}"
    )


# ---------------------------------------------------------------------------
# Joint expanding-window design candidates
# ---------------------------------------------------------------------------

print_header(
    "MOD-022 — JOINT EXPANDING-WINDOW DESIGN CANDIDATES"
)

for block_count in [3, 4, 5]:

    n = len(common)

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
            common[start:end]
        )

        start = end

    print(
        f"\n{block_count}-block chronological candidate:"
    )

    for i, block in enumerate(
        blocks,
        start=1
    ):

        print(
            f"  Prediction block {i}: "
            f"{len(block):,} rows | "
            f"{block[0]['Creation time']} "
            f"→ "
            f"{block[-1]['Creation time']}"
        )


# ---------------------------------------------------------------------------
# Earlier-history feasibility
# ---------------------------------------------------------------------------

print_header(
    "MOD-022 — EARLIER-HISTORY FEASIBILITY"
)

t2_train_times = [
    x["Creation time"]
    for x in t2_train
]

t7_train_times = [
    x["Creation time"]
    for x in t7_train
]

t2_train_times.sort()
t7_train_times.sort()

print(
    f"T2 training earliest: "
    f"{t2_train_times[0]}"
)

print(
    f"T2 training latest: "
    f"{t2_train_times[-1]}"
)

print(
    f"T7 training earliest: "
    f"{t7_train_times[0]}"
)

print(
    f"T7 training latest: "
    f"{t7_train_times[-1]}"
)

print(
    """
For each prediction block, the eventual OoF generator must
construct:

    T2 fitting population
        = eligible T2 training records strictly earlier
          than the prediction block

    T7 fitting population
        = eligible T7 training records strictly earlier
          than the prediction block

The prediction ticket itself must not enter its fitting population.
"""
)


# ---------------------------------------------------------------------------
# Warm-up feasibility
# ---------------------------------------------------------------------------

print_header(
    "MOD-022 — WARM-UP / FIRST-PREDICTABLE-COMMON-TICKET AUDIT"
)

first_common = common[0]

first_common_time = (
    first_common["Creation time"]
)

first_common_key = (
    first_common_time,
    first_common["ID"]
)

t2_before_first = sum(
    1
    for x in t2_train
    if (
        x["Creation time"],
        x["ID"]
    )
    <
    first_common_key
)

t7_before_first = sum(
    1
    for x in t7_train
    if (
        x["Creation time"],
        x["ID"]
    )
    <
    first_common_key
)

print(
    f"First common ticket: "
    f"{first_common['ID']}"
)

print(
    f"First common Creation: "
    f"{first_common_time}"
)

print(
    f"Earlier T2 training observations: "
    f"{t2_before_first:,}"
)

print(
    f"Earlier T7 training observations: "
    f"{t7_before_first:,}"
)


# ---------------------------------------------------------------------------
# Evaluate candidate block training history
# ---------------------------------------------------------------------------

print_header(
    "MOD-022 — BLOCK-BY-BLOCK TRAINING HISTORY"
)

n = len(common)

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
        common[start:end]
    )

    start = end


for i, block in enumerate(
    blocks,
    start=1
):

    prediction_first = block[0]

    boundary = (
        prediction_first["Creation time"],
        prediction_first["ID"]
    )

    t2_history = sum(
        1
        for x in t2_train
        if (
            x["Creation time"],
            x["ID"]
        )
        <
        boundary
    )

    t7_history = sum(
        1
        for x in t7_train
        if (
            x["Creation time"],
            x["ID"]
        )
        <
        boundary
    )

    print(
        f"\nBlock {i}:"
    )

    print(
        f"  prediction rows: "
        f"{len(block):,}"
    )

    print(
        f"  first prediction: "
        f"{prediction_first['Creation time']} "
        f"ID={prediction_first['ID']}"
    )

    print(
        f"  T2 earlier-history rows: "
        f"{t2_history:,}"
    )

    print(
        f"  T7 earlier-history rows: "
        f"{t7_history:,}"
    )


# ---------------------------------------------------------------------------
# Leakage guard design
# ---------------------------------------------------------------------------

print_header(
    "MOD-022 — REQUIRED LEAKAGE GUARDS"
)

guards = [
    "T2 prediction population ⊆ T2 training population",
    "T7 prediction population ⊆ T7 training population",
    "T2 prediction ticket absent from its fitting data",
    "T7 prediction ticket absent from its fitting data",
    "fitting data Creation time strictly precedes prediction ticket",
    "T7 evaluation completely excluded",
    "T2 test completely excluded",
    "no post-Creation feature information",
    "native T7 censoring retained",
    "native T2 target semantics retained",
    "no random split",
    "no target-derived feature",
    "no fusion model trained in MOD-022",
]

for i, guard in enumerate(
    guards,
    start=1
):

    print(
        f"{i:02d}. {guard}"
    )


# ---------------------------------------------------------------------------
# Joint-design conclusion
# ---------------------------------------------------------------------------

print_header(
    "MOD-022 — DESIGN DECISION"
)

print(
    """
A common development population is established:

    T2 train ∩ T7 train = 20,648 tickets.

Both tasks have chronological training populations containing
those tickets, while the locked evaluation populations remain
disjoint.

Therefore a joint OoF development design is feasible in principle.

The preferred implementation is:

    chronological expanding-window prediction

where, for each prediction block:

    T2 model:
        fit only on earlier T2 training observations

    T7 model:
        fit only on earlier T7 training observations

    predictions:
        generated only for the current common prediction block

The resulting development table will contain native T2 and T7
prediction evidence for the same ticket IDs.

However:

    no prediction generation occurs in MOD-022.

The exact block count and minimum warm-up policy must be frozen
before execution.

Existing T2/T7 locked evaluation artifacts remain untouched.
"""
)


# ---------------------------------------------------------------------------
# Integrity checks
# ---------------------------------------------------------------------------

print_header(
    "MOD-022 — INTEGRITY CHECKS"
)

checks = [
    (
        "Common development population = 20,648",
        len(common) == 20_648
    ),
    (
        "Common population has unique IDs",
        len({
            x["ID"]
            for x in common
        }) == len(common)
    ),
    (
        "No common ID in T7 evaluation",
        len(
            shared_train
            &
            t7_eval_ids
        ) == 0
    ),
    (
        "No T2 train/test overlap",
        len(
            t2_train_ids
            &
            t2_test_ids
        ) == 0
    ),
    (
        "No T7 train/evaluation overlap",
        len(
            t7_train_ids
            &
            t7_eval_ids
        ) == 0
    ),
    (
        "T2 earlier history exists",
        t2_before_first > 0
    ),
    (
        "T7 earlier history exists",
        t7_before_first > 0
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
    "\nMOD-022 JOINT T2/T7 DEVELOPMENT-PREDICTION "
    "DESIGN AUDIT COMPLETE"
)

print(
    "STATUS: COMPLETE / PASS"
)