#!/usr/bin/env python3

import csv
import sys
from collections import Counter
from itertools import combinations

csv.field_size_limit(sys.maxsize)

# ---------------------------------------------------------------------
# T8 MOD-003
# Common Decision-Population / Evidence-Overlap Audit
#
# READ-ONLY AUDIT
# ---------------------------------------------------------------------

LAYER_A = (
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T8_LAYER_A_TICKET_EVIDENCE_derived.csv"
)

TASKS = ["T2", "T3", "T4", "T5", "T7"]

AVAILABILITY_COLUMNS = {
    "T2": "t2_available",
    "T3": "t3_available",
    "T4": "t4_available",
    "T5": "t5_available",
    "T7": "t7_available",
}


def is_blank(value):
    if value is None:
        return True

    text = str(value).strip()

    return (
        text == ""
        or text.lower() in {
            "none",
            "null",
            "nan",
            "na",
            "n/a",
        }
    )


def classify_available(value):
    if is_blank(value):
        return False

    text = str(value).strip().lower()

    if text in {"1", "true", "yes", "available"}:
        return True

    if text in {"0", "false", "no", "unavailable"}:
        return False

    raise ValueError(
        f"Unexpected availability value: {value!r}"
    )


def combination_label(tasks):
    if not tasks:
        return "NONE"

    return "+".join(tasks)


print("=" * 78)
print("T8 MOD-003 — COMMON DECISION-POPULATION / EVIDENCE-OVERLAP AUDIT")
print("=" * 78)

print("\nREAD-ONLY CONTRACT")
print("- Existing Layer A T8 derived artifact only")
print("- No raw Mozilla archive access")
print("- No raw Mozilla CSV access")
print("- No artifact modification")
print("- No target construction")
print("- No score construction")
print("- No model training")
print("- No evidence fusion")


# ---------------------------------------------------------------------
# Input validation and scan
# ---------------------------------------------------------------------

print("\n[1] INPUT ARTIFACT")
print("-" * 78)

print(f"path: {LAYER_A}")


rows = 0

raw_values = {
    task: Counter()
    for task in TASKS
}

availability_patterns = Counter()

single_task_counts = Counter()
pairwise_counts = Counter()
triple_counts = Counter()
higher_order_counts = Counter()


with open(
    LAYER_A,
    "r",
    encoding="utf-8",
    newline=""
) as handle:

    reader = csv.DictReader(handle)
    fieldnames = reader.fieldnames or []

    print(f"columns: {len(fieldnames)}")

    missing = [
        column
        for column in AVAILABILITY_COLUMNS.values()
        if column not in fieldnames
    ]

    if missing:
        print("\nSTATUS: FAIL")
        print(
            f"Missing required availability columns: {missing}"
        )
        sys.exit(1)

    print("required availability columns: PRESENT")

    for row in reader:

        rows += 1

        available_tasks = []

        for task in TASKS:

            column = AVAILABILITY_COLUMNS[task]
            value = row.get(column, "")

            raw_display = (
                "<BLANK_OR_NULL>"
                if is_blank(value)
                else str(value).strip()
            )

            raw_values[task][raw_display] += 1

            available = classify_available(value)

            if available:
                available_tasks.append(task)

        # -------------------------------------------------------------
        # Complete availability pattern
        # -------------------------------------------------------------

        pattern = combination_label(
            available_tasks
        )

        availability_patterns[pattern] += 1

        # -------------------------------------------------------------
        # Single-task counts
        # -------------------------------------------------------------

        for task in available_tasks:
            single_task_counts[task] += 1

        # -------------------------------------------------------------
        # Pairwise intersections
        # -------------------------------------------------------------

        for pair in combinations(
            available_tasks,
            2
        ):
            pairwise_counts[
                combination_label(pair)
            ] += 1

        # -------------------------------------------------------------
        # Triple intersections
        # -------------------------------------------------------------

        for triple in combinations(
            available_tasks,
            3
        ):
            triple_counts[
                combination_label(triple)
            ] += 1

        # -------------------------------------------------------------
        # Four-way / five-way intersections
        # -------------------------------------------------------------

        for size in range(
            4,
            len(available_tasks) + 1
        ):
            for combo in combinations(
                available_tasks,
                size
            ):
                higher_order_counts[
                    combination_label(combo)
                ] += 1


# ---------------------------------------------------------------------
# Population
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[2] TICKET POPULATION")
print("=" * 78)

print(f"rows scanned: {rows}")


# ---------------------------------------------------------------------
# Raw values
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[3] RAW AVAILABILITY VALUES")
print("=" * 78)

for task in TASKS:

    print(f"\n{task} ({AVAILABILITY_COLUMNS[task]})")

    for value, count in raw_values[task].most_common():
        print(
            f"  {value!r}: {count}"
        )


# ---------------------------------------------------------------------
# Single-task availability
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[4] SINGLE-TASK AVAILABILITY")
print("=" * 78)

for task in TASKS:

    count = single_task_counts[task]

    rate = (
        count / rows * 100
        if rows
        else 0
    )

    print(
        f"{task}: "
        f"{count}/{rows} "
        f"({rate:.6f}%)"
    )


# ---------------------------------------------------------------------
# Pairwise overlap
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[5] PAIRWISE EVIDENCE OVERLAP")
print("=" * 78)

for pair in combinations(TASKS, 2):

    label = combination_label(pair)
    count = pairwise_counts[label]

    rate = (
        count / rows * 100
        if rows
        else 0
    )

    print(
        f"{label}: "
        f"{count}/{rows} "
        f"({rate:.6f}%)"
    )


# ---------------------------------------------------------------------
# Triple overlap
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[6] TRIPLE EVIDENCE OVERLAP")
print("=" * 78)

for triple in combinations(TASKS, 3):

    label = combination_label(triple)
    count = triple_counts[label]

    rate = (
        count / rows * 100
        if rows
        else 0
    )

    print(
        f"{label}: "
        f"{count}/{rows} "
        f"({rate:.6f}%)"
    )


# ---------------------------------------------------------------------
# Four-way / five-way
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[7] FOUR-WAY / FIVE-WAY OVERLAP")
print("=" * 78)

for size in [4, 5]:

    for combo in combinations(TASKS, size):

        label = combination_label(combo)
        count = higher_order_counts[label]

        rate = (
            count / rows * 100
            if rows
            else 0
        )

        print(
            f"{label}: "
            f"{count}/{rows} "
            f"({rate:.6f}%)"
        )


# ---------------------------------------------------------------------
# Complete availability patterns
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[8] FULL AVAILABILITY-PATTERN DISTRIBUTION")
print("=" * 78)

print(
    "Each ticket is classified by exactly which task evidence "
    "is available."
)

for pattern, count in availability_patterns.most_common():

    rate = (
        count / rows * 100
        if rows
        else 0
    )

    print(
        f"{pattern}: "
        f"{count}/{rows} "
        f"({rate:.6f}%)"
    )


# ---------------------------------------------------------------------
# Pattern diversity
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[9] PATTERN DIVERSITY")
print("=" * 78)

print(
    "distinct observed availability patterns: "
    f"{len(availability_patterns)}"
)

print(
    "possible binary patterns for five tasks: 32"
)


# ---------------------------------------------------------------------
# T5/T7 common base
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[10] COMMON T5 / T7 BASE")
print("=" * 78)

t5_t7 = pairwise_counts["T5+T7"]

print(
    f"T5+T7: "
    f"{t5_t7}/{rows} "
    f"({t5_t7 / rows * 100:.6f}%)"
)

if t5_t7 == rows:
    print(
        "All ticket-level T8 records have both T5 and T7 evidence."
    )
else:
    print(
        "Not all ticket-level T8 records have both T5 and T7 evidence."
    )


# ---------------------------------------------------------------------
# All-task intersection
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[11] ALL-TASK INTERSECTION")
print("=" * 78)

all_tasks = higher_order_counts[
    "T2+T3+T4+T5+T7"
]

print(
    f"T2+T3+T4+T5+T7: "
    f"{all_tasks}/{rows} "
    f"({all_tasks / rows * 100:.6f}%)"
)

print(
    "Reported descriptively only; this operation does not select "
    "an evaluation population."
)


# ---------------------------------------------------------------------
# Zero-evidence population
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[12] ZERO-EVIDENCE TICKET PATTERN")
print("=" * 78)

zero_evidence = availability_patterns.get(
    "NONE",
    0
)

print(
    f"NONE: "
    f"{zero_evidence}/{rows} "
    f"({zero_evidence / rows * 100:.6f}%)"
)


# ---------------------------------------------------------------------
# Final summary
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[13] MOD-003 EXECUTION SUMMARY")
print("=" * 78)

print(f"Rows scanned: {rows}")

print(
    "Observed availability patterns: "
    f"{len(availability_patterns)}"
)

print("\nComputed:")
print("- raw task availability states")
print("- single-task availability")
print("- pairwise intersections")
print("- triple intersections")
print("- four-way/five-way intersections")
print("- complete availability-pattern distribution")
print("- T5/T7 common-base size")
print("- all-task intersection size")
print("- zero-evidence population")

print("\nNOT performed:")
print("- target construction")
print("- score construction")
print("- model training")
print("- evidence fusion")
print("- evaluation-population selection")
print("- raw archive access")
print("- artifact modification")

print("\nSTATUS: MOD-003 EXECUTION COMPLETE")