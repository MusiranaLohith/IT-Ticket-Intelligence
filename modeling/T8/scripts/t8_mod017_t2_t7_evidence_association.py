#!/usr/bin/env python3

import csv
import math
from pathlib import Path

csv.field_size_limit(1024 * 1024 * 1024)

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T2_PRED = (
    PROJECT_ROOT
    / "modeling/T2/analysis/t2_final_test_predictions.csv"
)

T7_PRED = (
    PROJECT_ROOT
    / "modeling/T7/derived/t7_mod010_evaluation_predictions.csv"
)


def safe_float(value):
    try:
        x = float(value)
        if math.isfinite(x):
            return x
    except Exception:
        pass

    return None


def read_csv(path):
    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames or []


def mean(values):
    values = [x for x in values if x is not None]

    if not values:
        return None

    return sum(values) / len(values)


def median(values):
    values = sorted(
        x for x in values
        if x is not None
    )

    if not values:
        return None

    n = len(values)

    if n % 2:
        return values[n // 2]

    return (
        values[n // 2 - 1]
        + values[n // 2]
    ) / 2.0


def accuracy(rows):
    if not rows:
        return None

    return sum(
        r["actual_priority"] == r["predicted_priority"]
        for r in rows
    ) / len(rows)


def pct(value):
    return f"{value * 100:.6f}%"


def quantile(sorted_values, q):
    if not sorted_values:
        return None

    if len(sorted_values) == 1:
        return sorted_values[0]

    position = (len(sorted_values) - 1) * q

    lower = int(math.floor(position))
    upper = int(math.ceil(position))

    if lower == upper:
        return sorted_values[lower]

    fraction = position - lower

    return (
        sorted_values[lower]
        + fraction
        * (
            sorted_values[upper]
            - sorted_values[lower]
        )
    )


def quartile_bins(values):
    clean = sorted(
        x for x in values
        if x is not None
    )

    q1 = quantile(clean, 0.25)
    q2 = quantile(clean, 0.50)
    q3 = quantile(clean, 0.75)

    return q1, q2, q3


print("=" * 78)
print("MOD-017 — T2 + T7 EVIDENCE ASSOCIATION / CONDITIONAL-ERROR AUDIT")
print("=" * 78)


# ---------------------------------------------------------------------------
# Load prediction artifacts
# ---------------------------------------------------------------------------

t2_rows, t2_fields = read_csv(T2_PRED)
t7_rows, t7_fields = read_csv(T7_PRED)

print("\nT2 prediction fields:")
print(f"  {t2_fields}")

print("\nT7 prediction fields:")
print(f"  {t7_fields}")


# ---------------------------------------------------------------------------
# Explicit prediction-time fields
# ---------------------------------------------------------------------------

t7_prediction_fields = [
    "predicted_median_survival_seconds",
    "survival_probability_at_211583_seconds",
    "survival_probability_at_1780179_seconds",
    "survival_probability_at_14608619_seconds",
]

t7_outcome_fields = [
    "duration_seconds",
    "event",
]

print("\nT7 prediction-time evidence fields:")
for field in t7_prediction_fields:
    print(f"  {field}: {'PRESENT' if field in t7_fields else 'MISSING'}")

print("\nT7 outcome fields explicitly excluded from predictors:")
for field in t7_outcome_fields:
    print(f"  {field}")


# ---------------------------------------------------------------------------
# Addressable ID populations
# ---------------------------------------------------------------------------

t2_by_id = {
    r["ID"].strip(): r
    for r in t2_rows
    if r.get("ID", "").strip()
}

t7_by_id = {
    r["ID"].strip(): r
    for r in t7_rows
    if r.get("ID", "").strip()
}

common_ids = (
    set(t2_by_id)
    & set(t7_by_id)
)

print("\n" + "=" * 78)
print("MOD-017 — COMMON PREDICTION POPULATION")
print("=" * 78)

print(f"  T2 prediction rows: {len(t2_by_id)}")
print(f"  T7 prediction rows: {len(t7_by_id)}")
print(f"  common IDs:         {len(common_ids)}")


# ---------------------------------------------------------------------------
# Build common analysis rows
# ---------------------------------------------------------------------------

analysis_rows = []

for ticket_id in sorted(common_ids):

    t2 = t2_by_id[ticket_id]
    t7 = t7_by_id[ticket_id]

    actual = t2.get(
        "actual_priority",
        ""
    ).strip()

    predicted = t2.get(
        "predicted_priority",
        ""
    ).strip()

    median_survival = safe_float(
        t7.get(
            "predicted_median_survival_seconds",
            ""
        )
    )

    p_211k = safe_float(
        t7.get(
            "survival_probability_at_211583_seconds",
            ""
        )
    )

    p_1780k = safe_float(
        t7.get(
            "survival_probability_at_1780179_seconds",
            ""
        )
    )

    p_14608k = safe_float(
        t7.get(
            "survival_probability_at_14608619_seconds",
            ""
        )
    )

    if not actual or not predicted:
        continue

    analysis_rows.append(
        {
            "ID": ticket_id,
            "actual_priority": actual,
            "predicted_priority": predicted,
            "correct": (
                actual == predicted
            ),
            "predicted_median_survival_seconds":
                median_survival,
            "survival_probability_at_211583_seconds":
                p_211k,
            "survival_probability_at_1780179_seconds":
                p_1780k,
            "survival_probability_at_14608619_seconds":
                p_14608k,
        }
    )


print(f"  analyzable common rows: {len(analysis_rows)}")

if len(analysis_rows) != 4425:
    raise RuntimeError(
        "Expected 4,425 clean T2+T7 rows; "
        f"found {len(analysis_rows)}."
    )


# ---------------------------------------------------------------------------
# Native T2 baseline on exact common population
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-017 — T2 BASELINE ON EXACT T2+T7 POPULATION")
print("=" * 78)

baseline_accuracy = accuracy(
    analysis_rows
)

print(f"  rows:     {len(analysis_rows)}")
print(f"  correct:  {sum(r['correct'] for r in analysis_rows)}")
print(f"  incorrect:{sum(not r['correct'] for r in analysis_rows)}")
print(f"  accuracy: {baseline_accuracy:.8f}")


# ---------------------------------------------------------------------------
# T2 outcome composition
# ---------------------------------------------------------------------------

print("\nT2 priority distribution:")

for label in ["P1", "P2", "P3", "P4", "P5"]:

    rows = [
        r for r in analysis_rows
        if r["actual_priority"] == label
    ]

    correct = sum(
        r["correct"]
        for r in rows
    )

    print(
        f"  {label}: "
        f"n={len(rows)}, "
        f"accuracy="
        f"{correct / len(rows):.8f}"
    )


# ---------------------------------------------------------------------------
# T7 prediction summaries by T2 correctness
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-017 — T7 EVIDENCE VS T2 CORRECTNESS")
print("=" * 78)

correct_rows = [
    r for r in analysis_rows
    if r["correct"]
]

incorrect_rows = [
    r for r in analysis_rows
    if not r["correct"]
]

print(
    f"\nCorrect T2 predictions: "
    f"{len(correct_rows)} "
    f"({pct(len(correct_rows) / len(analysis_rows))})"
)

print(
    f"Incorrect T2 predictions: "
    f"{len(incorrect_rows)} "
    f"({pct(len(incorrect_rows) / len(analysis_rows))})"
)


evidence_fields = [
    "predicted_median_survival_seconds",
    "survival_probability_at_211583_seconds",
    "survival_probability_at_1780179_seconds",
    "survival_probability_at_14608619_seconds",
]


for field in evidence_fields:

    correct_values = [
        r[field]
        for r in correct_rows
        if r[field] is not None
    ]

    incorrect_values = [
        r[field]
        for r in incorrect_rows
        if r[field] is not None
    ]

    print(f"\n{field}")

    print(
        f"  correct:   "
        f"n={len(correct_values)}, "
        f"mean={mean(correct_values)}, "
        f"median={median(correct_values)}"
    )

    print(
        f"  incorrect: "
        f"n={len(incorrect_values)}, "
        f"mean={mean(incorrect_values)}, "
        f"median={median(incorrect_values)}"
    )


# ---------------------------------------------------------------------------
# Quartile-conditioned T2 error analysis
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-017 — QUARTILE-CONDITIONED T2 ERROR ANALYSIS")
print("=" * 78)

for field in evidence_fields:

    values = sorted(
        r[field]
        for r in analysis_rows
        if r[field] is not None
    )

    if not values:
        print(f"\n{field}: unavailable")
        continue

    q1, q2, q3 = quartile_bins(values)

    bins = [
        (
            "Q1",
            lambda x: x <= q1
        ),
        (
            "Q2",
            lambda x: q1 < x <= q2
        ),
        (
            "Q3",
            lambda x: q2 < x <= q3
        ),
        (
            "Q4",
            lambda x: x > q3
        ),
    ]

    print(f"\n{field}")

    print(
        f"  quartiles: "
        f"Q1={q1}, "
        f"Q2={q2}, "
        f"Q3={q3}"
    )

    for label, predicate in bins:

        rows = [
            r for r in analysis_rows
            if r[field] is not None
            and predicate(r[field])
        ]

        if not rows:
            continue

        acc = accuracy(rows)

        print(
            f"  {label}: "
            f"n={len(rows)}, "
            f"correct={sum(r['correct'] for r in rows)}, "
            f"incorrect={sum(not r['correct'] for r in rows)}, "
            f"accuracy={acc:.8f}"
        )


# ---------------------------------------------------------------------------
# Priority-specific conditional analysis
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-017 — PRIORITY-SPECIFIC T7 EVIDENCE ANALYSIS")
print("=" * 78)

for priority in ["P1", "P2", "P3", "P4", "P5"]:

    rows = [
        r for r in analysis_rows
        if r["actual_priority"] == priority
    ]

    if not rows:
        continue

    print(f"\nActual priority {priority}")
    print(f"  rows: {len(rows)}")
    print(
        f"  T2 accuracy: "
        f"{accuracy(rows):.8f}"
    )

    for field in evidence_fields:

        values = [
            r[field]
            for r in rows
            if r[field] is not None
        ]

        print(
            f"  {field}: "
            f"mean={mean(values)}, "
            f"median={median(values)}"
        )


# ---------------------------------------------------------------------------
# Error-direction analysis
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-017 — T2 ERROR DIRECTION")
print("=" * 78)

priority_order = {
    "P1": 1,
    "P2": 2,
    "P3": 3,
    "P4": 4,
    "P5": 5,
}

error_direction = {}

for row in incorrect_rows:

    actual = row["actual_priority"]
    predicted = row["predicted_priority"]

    if actual not in priority_order:
        continue

    if predicted not in priority_order:
        continue

    difference = (
        priority_order[predicted]
        - priority_order[actual]
    )

    if difference < 0:
        direction = "predicted_higher_priority"
    elif difference > 0:
        direction = "predicted_lower_priority"
    else:
        direction = "same"

    error_direction[direction] = (
        error_direction.get(direction, 0)
        + 1
    )

for direction, count in sorted(
    error_direction.items()
):
    print(
        f"  {direction}: "
        f"{count} "
        f"({pct(count / len(incorrect_rows))})"
    )


# ---------------------------------------------------------------------------
# Evidence availability / missingness
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-017 — T7 PREDICTION EVIDENCE AVAILABILITY")
print("=" * 78)

for field in evidence_fields:

    available = sum(
        r[field] is not None
        for r in analysis_rows
    )

    print(
        f"  {field}: "
        f"{available}/{len(analysis_rows)} "
        f"({pct(available / len(analysis_rows))})"
    )


# ---------------------------------------------------------------------------
# Leakage guard
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-017 — LEAKAGE GUARD")
print("=" * 78)

used_fields = (
    ["actual_priority", "predicted_priority"]
    + evidence_fields
)

print("Predictive analysis fields:")
for field in used_fields:
    print(f"  {field}")

print("\nExplicitly excluded T7 outcome fields:")
for field in t7_outcome_fields:
    print(f"  {field}")

leakage_checks = [
    (
        "T7 duration_seconds excluded",
        "duration_seconds" not in evidence_fields
    ),
    (
        "T7 event excluded",
        "event" not in evidence_fields
    ),
    (
        "T7 predicted fields present",
        all(
            field in t7_fields
            for field in evidence_fields
        )
    ),
    (
        "Common population equals T2+T7 cohort",
        len(analysis_rows) == 4425
    ),
]

for label, passed in leakage_checks:
    print(
        f"  {label}: "
        f"{'PASS' if passed else 'FAIL'}"
    )


# ---------------------------------------------------------------------------
# Interpretation guard
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-017 — INTERPRETATION CONTRACT")
print("=" * 78)

print("""
This module does NOT claim that T7 improves T2.

It only determines whether T7 prediction-time evidence is
associated with differences in T2 prediction correctness.

A difference in conditional T2 accuracy is NOT treated as:

  - causal evidence,
  - proof of fusion benefit,
  - proof that T7 should receive a particular weight,
  - proof of a universal T8 confidence score.

A future learned fusion model requires a separate training/development
population and must not be trained on this locked evaluation cohort.
""")


# ---------------------------------------------------------------------------
# Final status
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-017 — INTEGRITY CHECKS")
print("=" * 78)

checks = [
    (
        "T2/T7 common population = 4,425",
        len(common_ids) == 4425
    ),
    (
        "All analyzable rows have T2 actual/predicted labels",
        len(analysis_rows) == 4425
    ),
    (
        "T7 predictive evidence is available for all rows",
        all(
            all(
                r[field] is not None
                for field in evidence_fields
            )
            for r in analysis_rows
        )
    ),
    (
        "T7 outcome fields excluded",
        all(
            field not in evidence_fields
            for field in t7_outcome_fields
        )
    ),
]

for label, passed in checks:
    print(
        f"  {label}: "
        f"{'PASS' if passed else 'FAIL'}"
    )


if all(passed for _, passed in checks):
    print(
        "\nMOD-017 T2 + T7 EVIDENCE ASSOCIATION / "
        "CONDITIONAL-ERROR AUDIT COMPLETE"
    )
    print("STATUS: COMPLETE / PASS")
else:
    print("\nMOD-017 INTEGRITY FAILURE")
    print("STATUS: REVIEW REQUIRED")