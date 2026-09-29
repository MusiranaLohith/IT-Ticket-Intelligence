#!/usr/bin/env python3

import csv
import json
import math
from pathlib import Path
from collections import Counter

csv.field_size_limit(1024 * 1024 * 1024)

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
DATA_ROOT = Path("/run/media/whiteblack/User 1/Datasets/Mozilla_CORE")

T2_TRAIN = PROJECT_ROOT / "modeling/T2/splits/train.csv"
T2_EVAL = PROJECT_ROOT / "modeling/T2/splits/test.csv"

T4_TRAIN = PROJECT_ROOT / "modeling/T4/derived/t4_train.csv"
T4_EVAL = PROJECT_ROOT / "modeling/T4/derived/t4_eval.csv"

T5_TRAIN = PROJECT_ROOT / "modeling/T5/splits/t5_model_train.csv"
T5_EVAL = DATA_ROOT / "DTM-002_T5_EVAL_GROUP_AWARE.csv"

T7_TRAIN = PROJECT_ROOT / "modeling/T7/splits/t7_train.csv"
T7_EVAL = PROJECT_ROOT / "modeling/T7/splits/t7_evaluation.csv"

T2_PRED = PROJECT_ROOT / "modeling/T2/analysis/t2_final_test_predictions.csv"
T4_PRED = PROJECT_ROOT / "modeling/T4/derived/t4_eval.csv"
T5_PRED = PROJECT_ROOT / "modeling/T5/metrics/t5_mod009_locked_evaluation_predictions.npz"
T7_PRED = PROJECT_ROOT / "modeling/T7/derived/t7_mod010_evaluation_predictions.csv"


def read_csv(path):
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return rows, reader.fieldnames or []


def read_ids(path):
    rows, fields = read_csv(path)

    id_field = "ID" if "ID" in fields else "ticket_id"

    ids = {
        r[id_field].strip()
        for r in rows
        if r.get(id_field, "").strip()
    }

    return ids


def safe_float(value):
    try:
        x = float(value)
        return x if math.isfinite(x) else None
    except Exception:
        return None


def pct(n, d):
    return 100.0 * n / d if d else 0.0


def distribution(values):
    c = Counter(values)
    total = len(values)

    return [
        (key, count, pct(count, total))
        for key, count in sorted(c.items(), key=lambda x: str(x[0]))
    ]


def print_distribution(title, values):
    print(f"\n{title}")
    for key, count, percentage in distribution(values):
        print(f"  {key}: {count} ({percentage:.6f}%)")


def jensen_shannon(p, q):
    """
    Jensen-Shannon divergence using natural logarithms.

    p and q are dictionaries over the same categorical support.
    """
    keys = sorted(set(p) | set(q))

    p_total = sum(p.values())
    q_total = sum(q.values())

    if not p_total or not q_total:
        return None

    pp = {k: p.get(k, 0) / p_total for k in keys}
    qq = {k: q.get(k, 0) / q_total for k in keys}

    m = {
        k: (pp[k] + qq[k]) / 2.0
        for k in keys
    }

    def kl(a, b):
        result = 0.0
        for k in keys:
            if a[k] > 0:
                result += a[k] * math.log(a[k] / b[k])
        return result

    return 0.5 * kl(pp, m) + 0.5 * kl(qq, m)


def categorical_counts(values):
    return Counter(values)


def compare_categorical(label, full_values, cohort_values):
    full = categorical_counts(full_values)
    cohort = categorical_counts(cohort_values)

    print(f"\n{label}")
    print("  category | native_count | native_% | cohort_count | cohort_%")

    keys = sorted(set(full) | set(cohort), key=str)

    for key in keys:
        nf = full.get(key, 0)
        nc = cohort.get(key, 0)

        print(
            f"  {key} | "
            f"{nf} | {pct(nf, len(full_values)):.6f}% | "
            f"{nc} | {pct(nc, len(cohort_values)):.6f}%"
        )

    js = jensen_shannon(full, cohort)

    if js is None:
        print("  Jensen-Shannon divergence: unavailable")
    else:
        print(f"  Jensen-Shannon divergence: {js:.8f}")


def mean(values):
    values = [x for x in values if x is not None]
    return sum(values) / len(values) if values else None


def median(values):
    values = sorted(x for x in values if x is not None)

    if not values:
        return None

    n = len(values)

    if n % 2:
        return values[n // 2]

    return (values[n // 2 - 1] + values[n // 2]) / 2.0


def summarize_numeric(label, native_values, cohort_values):
    n_mean = mean(native_values)
    c_mean = mean(cohort_values)

    n_med = median(native_values)
    c_med = median(cohort_values)

    print(f"\n{label}")
    print(f"  native count:  {len([x for x in native_values if x is not None])}")
    print(f"  cohort count:  {len([x for x in cohort_values if x is not None])}")
    print(f"  native mean:   {n_mean}")
    print(f"  cohort mean:   {c_mean}")
    print(f"  native median: {n_med}")
    print(f"  cohort median: {c_med}")


def build_rows_by_id(path):
    rows, fields = read_csv(path)

    id_field = "ID" if "ID" in fields else "ticket_id"

    result = {}

    for row in rows:
        ticket_id = row.get(id_field, "").strip()

        if ticket_id:
            result[ticket_id] = row

    return result, fields


print("=" * 78)
print("MOD-014 — NATIVE EVALUATION COMPOSITION LOADING")
print("=" * 78)

t2_train = read_ids(T2_TRAIN)
t2_eval_rows, t2_eval_fields = read_csv(T2_EVAL)
t2_eval = {
    r["ID"].strip()
    for r in t2_eval_rows
    if r.get("ID", "").strip()
}

t4_train = read_ids(T4_TRAIN)
t4_eval_rows, t4_eval_fields = read_csv(T4_EVAL)
t4_eval = {
    r["ID"].strip()
    for r in t4_eval_rows
    if r.get("ID", "").strip()
}

t5_train = read_ids(T5_TRAIN)
t5_eval_rows, t5_eval_fields = read_csv(T5_EVAL)
t5_eval = {
    r["ID"].strip()
    for r in t5_eval_rows
    if r.get("ID", "").strip()
}

t7_train = read_ids(T7_TRAIN)
t7_eval_rows, t7_eval_fields = read_csv(T7_EVAL)
t7_eval = {
    r["ID"].strip()
    for r in t7_eval_rows
    if r.get("ID", "").strip()
}

print("\nNative evaluation populations:")
print(f"  T2: {len(t2_eval)}")
print(f"  T4: {len(t4_eval)}")
print(f"  T5: {len(t5_eval)}")
print(f"  T7: {len(t7_eval)}")

print("\nTraining populations:")
print(f"  T2: {len(t2_train)}")
print(f"  T4: {len(t4_train)}")
print(f"  T5: {len(t5_train)}")
print(f"  T7: {len(t7_train)}")


# ---------------------------------------------------------------------------
# Build candidate cohorts from native evaluation overlaps.
# These reproduce the clean cohorts from MOD-013.
# ---------------------------------------------------------------------------

def clean_pair(anchor_eval, auxiliary_train, auxiliary_eval):
    clean_anchor = anchor_eval - auxiliary_train
    return clean_anchor & auxiliary_eval


cohorts = {
    "T2+T4": clean_pair(t2_eval, t4_train, t4_eval),
    "T2+T5": clean_pair(t2_eval, t5_train, t5_eval),
    "T2+T7": clean_pair(t2_eval, t7_train, t7_eval),

    "T4+T2": clean_pair(t4_eval, t2_train, t2_eval),
    "T4+T5": clean_pair(t4_eval, t5_train, t5_eval),
    "T4+T7": clean_pair(t4_eval, t7_train, t7_eval),

    "T5+T2": clean_pair(t5_eval, t2_train, t2_eval),
    "T5+T4": clean_pair(t5_eval, t4_train, t4_eval),
    "T5+T7": clean_pair(t5_eval, t7_train, t7_eval),

    "T7+T2": clean_pair(t7_eval, t2_train, t2_eval),
    "T7+T4": clean_pair(t7_eval, t4_train, t4_eval),
    "T7+T5": clean_pair(t7_eval, t5_train, t5_eval),
}

print("\n" + "=" * 78)
print("MOD-014 — RECONSTRUCTED CLEAN PAIRWISE COHORTS")
print("=" * 78)

for name, ids in cohorts.items():
    print(f"  {name}: {len(ids)}")


# ---------------------------------------------------------------------------
# Load native evaluation rows for outcome composition.
# ---------------------------------------------------------------------------

t2_by_id = {
    r["ID"].strip(): r
    for r in t2_eval_rows
    if r.get("ID", "").strip()
}

t4_by_id = {
    r["ID"].strip(): r
    for r in t4_eval_rows
    if r.get("ID", "").strip()
}

t5_by_id = {
    r["ID"].strip(): r
    for r in t5_eval_rows
    if r.get("ID", "").strip()
}

t7_by_id = {
    r["ID"].strip(): r
    for r in t7_eval_rows
    if r.get("ID", "").strip()
}


# ---------------------------------------------------------------------------
# T2 composition
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-014 — T2 OUTCOME COMPOSITION")
print("=" * 78)

t2_native_priority = [
    r.get("target_priority", "").strip()
    for r in t2_eval_rows
    if r.get("target_priority", "").strip()
]

print_distribution(
    "Native T2 evaluation target_priority",
    t2_native_priority
)

for cohort_name in ["T2+T4", "T2+T5", "T2+T7"]:
    ids = cohorts[cohort_name]

    values = [
        t2_by_id[i].get("target_priority", "").strip()
        for i in ids
        if i in t2_by_id
        and t2_by_id[i].get("target_priority", "").strip()
    ]

    compare_categorical(
        f"{cohort_name} vs native T2 evaluation",
        t2_native_priority,
        values
    )


# ---------------------------------------------------------------------------
# T4 composition
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-014 — T4 OUTCOME / COVERAGE COMPOSITION")
print("=" * 78)

t4_native_assignee = [
    r.get("target_assignee", "").strip()
    for r in t4_eval_rows
    if r.get("target_assignee", "").strip()
]

print(f"\nNative T4 evaluation target_assignee count: {len(t4_native_assignee)}")
print(f"Native T4 unique assignees: {len(set(t4_native_assignee))}")

for cohort_name in ["T4+T2", "T4+T5", "T4+T7"]:
    ids = cohorts[cohort_name]

    values = [
        t4_by_id[i].get("target_assignee", "").strip()
        for i in ids
        if i in t4_by_id
        and t4_by_id[i].get("target_assignee", "").strip()
    ]

    print(f"\n{cohort_name}")
    print(f"  cohort rows with target_assignee: {len(values)}")
    print(f"  cohort unique assignees: {len(set(values))}")

    # Coverage of native assignee categories.
    native_set = set(t4_native_assignee)
    cohort_set = set(values)

    print(
        f"  native assignees represented: "
        f"{len(cohort_set & native_set)} / {len(native_set)}"
    )


# ---------------------------------------------------------------------------
# T5 composition
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-014 — T5 OUTCOME COMPOSITION")
print("=" * 78)

t5_native_target = [
    r.get("T5 target", "").strip()
    for r in t5_eval_rows
    if r.get("T5 target", "").strip()
]

print_distribution(
    "Native T5 evaluation T5 target",
    t5_native_target
)

for cohort_name in ["T5+T2", "T5+T4", "T5+T7"]:
    ids = cohorts[cohort_name]

    values = [
        t5_by_id[i].get("T5 target", "").strip()
        for i in ids
        if i in t5_by_id
        and t5_by_id[i].get("T5 target", "").strip()
    ]

    compare_categorical(
        f"{cohort_name} vs native T5 evaluation",
        t5_native_target,
        values
    )


# ---------------------------------------------------------------------------
# T7 composition
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-014 — T7 EVENT / CENSORING COMPOSITION")
print("=" * 78)

t7_native_event = [
    r.get("event", "").strip()
    for r in t7_eval_rows
    if r.get("event", "").strip()
]

print_distribution(
    "Native T7 evaluation event",
    t7_native_event
)

for cohort_name in ["T7+T2", "T7+T4", "T7+T5"]:
    ids = cohorts[cohort_name]

    values = [
        t7_by_id[i].get("event", "").strip()
        for i in ids
        if i in t7_by_id
        and t7_by_id[i].get("event", "").strip()
    ]

    compare_categorical(
        f"{cohort_name} vs native T7 evaluation event",
        t7_native_event,
        values
    )


# ---------------------------------------------------------------------------
# T7 duration composition
# ---------------------------------------------------------------------------

native_t7_duration = [
    safe_float(r.get("duration_seconds", ""))
    for r in t7_eval_rows
]

for cohort_name in ["T7+T2", "T7+T4", "T7+T5"]:
    ids = cohorts[cohort_name]

    cohort_duration = [
        safe_float(t7_by_id[i].get("duration_seconds", ""))
        for i in ids
        if i in t7_by_id
    ]

    summarize_numeric(
        f"{cohort_name} vs native T7 duration_seconds",
        native_t7_duration,
        cohort_duration
    )


# ---------------------------------------------------------------------------
# Overall candidate summary
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-014 — CANDIDATE COMPOSITION SUMMARY")
print("=" * 78)

for name, ids in cohorts.items():
    anchor = name.split("+")[0]

    if anchor == "T2":
        native = t2_eval
    elif anchor == "T4":
        native = t4_eval
    elif anchor == "T5":
        native = t5_eval
    elif anchor == "T7":
        native = t7_eval
    else:
        native = set()

    print(
        f"  {name}: "
        f"{len(ids)} / {len(native)} "
        f"({pct(len(ids), len(native)):.6f}%)"
    )


print("\n" + "=" * 78)
print("MOD-014 — INTEGRITY CHECKS")
print("=" * 78)

checks = []

checks.append(("T2 eval IDs unique", len(t2_eval) == len(t2_eval_rows)))
checks.append(("T4 eval IDs unique", len(t4_eval) == len(t4_eval_rows)))
checks.append(("T5 eval IDs unique", len(t5_eval) == len(t5_eval_rows)))
checks.append(("T7 eval IDs unique", len(t7_eval) == len(t7_eval_rows)))

for name, ids in cohorts.items():
    anchor = name.split("+")[0]

    anchor_eval = {
        "T2": t2_eval,
        "T4": t4_eval,
        "T5": t5_eval,
        "T7": t7_eval,
    }[anchor]

    checks.append(
        (
            f"{name} subset of native anchor evaluation",
            ids.issubset(anchor_eval)
        )
    )

for label, passed in checks:
    print(f"  {label}: {'PASS' if passed else 'FAIL'}")


if all(passed for _, passed in checks):
    print("\nMOD-014 CANDIDATE COHORT OUTCOME / COMPOSITION AUDIT COMPLETE")
    print("STATUS: COMPLETE / PASS")
else:
    print("\nMOD-014 INTEGRITY CHECK FAILURE")
    print("STATUS: REVIEW REQUIRED")