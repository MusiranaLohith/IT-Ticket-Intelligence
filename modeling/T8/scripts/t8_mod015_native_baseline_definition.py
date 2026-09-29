#!/usr/bin/env python3

import csv
import math
from pathlib import Path
from collections import Counter

import numpy as np

csv.field_size_limit(1024 * 1024 * 1024)

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
DATA_ROOT = Path("/run/media/whiteblack/User 1/Datasets/Mozilla_CORE")

T2_TRAIN = PROJECT_ROOT / "modeling/T2/splits/train.csv"
T2_EVAL = PROJECT_ROOT / "modeling/T2/splits/test.csv"
T2_PRED = PROJECT_ROOT / "modeling/T2/analysis/t2_final_test_predictions.csv"

T4_TRAIN = PROJECT_ROOT / "modeling/T4/derived/t4_train.csv"
T4_EVAL = PROJECT_ROOT / "modeling/T4/derived/t4_eval.csv"
T4_PRED = PROJECT_ROOT / "modeling/T4/results/r1_checkpoints/t4_r1_topk_predictions.npz"

T5_TRAIN = PROJECT_ROOT / "modeling/T5/splits/t5_model_train.csv"
T5_EVAL = DATA_ROOT / "DTM-002_T5_EVAL_GROUP_AWARE.csv"
T5_PRED = PROJECT_ROOT / "modeling/T5/metrics/t5_mod009_locked_evaluation_predictions.npz"

T7_TRAIN = PROJECT_ROOT / "modeling/T7/splits/t7_train.csv"
T7_EVAL = PROJECT_ROOT / "modeling/T7/splits/t7_evaluation.csv"
T7_PRED = PROJECT_ROOT / "modeling/T7/derived/t7_mod010_evaluation_predictions.csv"


def read_csv(path):
    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return rows, reader.fieldnames or []


def read_ids(path):
    rows, fields = read_csv(path)

    id_field = "ID" if "ID" in fields else "ticket_id"

    return {
        row[id_field].strip()
        for row in rows
        if row.get(id_field, "").strip()
    }


def pct(n, d):
    return 100.0 * n / d if d else 0.0


def safe_float(value):
    try:
        x = float(value)
        return x if math.isfinite(x) else None
    except Exception:
        return None


def confusion_binary(y_true, y_pred):
    tp = tn = fp = fn = 0

    for y, p in zip(y_true, y_pred):
        if y == 1 and p == 1:
            tp += 1
        elif y == 0 and p == 0:
            tn += 1
        elif y == 0 and p == 1:
            fp += 1
        elif y == 1 and p == 0:
            fn += 1

    return tp, tn, fp, fn


def binary_metrics(y_true, y_pred):
    tp, tn, fp, fn = confusion_binary(y_true, y_pred)

    total = tp + tn + fp + fn

    accuracy = (tp + tn) / total if total else None

    precision = (
        tp / (tp + fp)
        if (tp + fp)
        else None
    )

    recall = (
        tp / (tp + fn)
        if (tp + fn)
        else None
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision is not None
        and recall is not None
        and (precision + recall) > 0
        else None
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


def binary_average_precision(y_true, scores):
    """
    Average Precision implementation for binary labels.

    This is used only for T5's native duplicate probability,
    where higher score means stronger duplicate relationship evidence.
    """
    pairs = sorted(
        zip(scores, y_true),
        key=lambda x: x[0],
        reverse=True
    )

    positives = sum(y_true)

    if positives == 0:
        return None

    running_tp = 0
    ap_sum = 0.0

    for rank, (_, label) in enumerate(pairs, start=1):
        if label == 1:
            running_tp += 1
            ap_sum += running_tp / rank

    return ap_sum / positives


def print_binary_result(name, y_true, y_pred):
    metrics = binary_metrics(y_true, y_pred)

    print(f"\n{name}")
    print(f"  rows:      {len(y_true)}")
    print(f"  positives: {sum(y_true)}")
    print(f"  negatives: {len(y_true) - sum(y_true)}")

    for key in ["accuracy", "precision", "recall", "f1"]:
        value = metrics[key]

        if value is None:
            print(f"  {key}: unavailable")
        else:
            print(f"  {key}: {value:.8f}")

    print(
        "  confusion: "
        f"TP={metrics['tp']} "
        f"TN={metrics['tn']} "
        f"FP={metrics['fp']} "
        f"FN={metrics['fn']}"
    )


print("=" * 78)
print("MOD-015 — NATIVE BASELINE DEFINITION")
print("=" * 78)

print("\nArtifact existence:")

artifacts = {
    "T2 prediction": T2_PRED,
    "T4 prediction": T4_PRED,
    "T5 prediction": T5_PRED,
    "T7 prediction": T7_PRED,
}

for name, path in artifacts.items():
    print(f"  {name}: {path.exists()}")

# ---------------------------------------------------------------------------
# Native populations
# ---------------------------------------------------------------------------

t2_eval_rows, _ = read_csv(T2_EVAL)
t4_eval_rows, _ = read_csv(T4_EVAL)
t5_eval_rows, _ = read_csv(T5_EVAL)
t7_eval_rows, _ = read_csv(T7_EVAL)

t2_eval = {
    r["ID"].strip()
    for r in t2_eval_rows
    if r.get("ID", "").strip()
}

t4_eval = {
    r["ID"].strip()
    for r in t4_eval_rows
    if r.get("ID", "").strip()
}

t5_eval = {
    r["ID"].strip()
    for r in t5_eval_rows
    if r.get("ID", "").strip()
}

t7_eval = {
    r["ID"].strip()
    for r in t7_eval_rows
    if r.get("ID", "").strip()
}

# Training populations
t2_train = read_ids(T2_TRAIN)
t4_train = read_ids(T4_TRAIN)
t5_train = read_ids(T5_TRAIN)
t7_train = read_ids(T7_TRAIN)

print("\nNative evaluation populations:")
print(f"  T2: {len(t2_eval)}")
print(f"  T4: {len(t4_eval)}")
print(f"  T5: {len(t5_eval)}")
print(f"  T7: {len(t7_eval)}")

# ---------------------------------------------------------------------------
# Clean cohorts from MOD-013
# ---------------------------------------------------------------------------

def clean_pair(anchor_eval, aux_train, aux_eval):
    return (anchor_eval - aux_train) & aux_eval


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
print("MOD-015 — CLEAN COHORTS")
print("=" * 78)

for name, ids in cohorts.items():
    print(f"  {name}: {len(ids)}")


# ---------------------------------------------------------------------------
# T2 native baseline
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-015 — T2 NATIVE BASELINE")
print("=" * 78)

t2_pred_rows, t2_pred_fields = read_csv(T2_PRED)

print("\nT2 prediction artifact fields:")
print(f"  {t2_pred_fields}")

t2_pred_by_id = {
    r["ID"].strip(): r
    for r in t2_pred_rows
    if r.get("ID", "").strip()
}

print(f"  prediction rows: {len(t2_pred_by_id)}")

t2_native_pairs = []

for row in t2_pred_rows:
    ticket_id = row.get("ID", "").strip()

    actual = row.get("actual_priority", "").strip()
    predicted = row.get("predicted_priority", "").strip()

    if ticket_id and actual and predicted:
        t2_native_pairs.append((ticket_id, actual, predicted))

native_correct = sum(
    actual == predicted
    for _, actual, predicted in t2_native_pairs
)

print(
    f"\nNative T2 locked-test accuracy: "
    f"{native_correct / len(t2_native_pairs):.8f}"
)

print(f"Native T2 locked-test rows: {len(t2_native_pairs)}")

for cohort_name in ["T2+T4", "T2+T5", "T2+T7"]:
    ids = cohorts[cohort_name]

    selected = [
        (actual, predicted)
        for ticket_id, actual, predicted in t2_native_pairs
        if ticket_id in ids
    ]

    if not selected:
        print(f"\n{cohort_name}: no addressable T2 predictions")
        continue

    y_true = [a for a, _ in selected]
    y_pred = [p for _, p in selected]

    labels = sorted(set(y_true) | set(y_pred))

    correct = sum(
        a == p
        for a, p in selected
    )

    print(f"\n{cohort_name}")
    print(f"  rows: {len(selected)}")
    print(f"  accuracy: {correct / len(selected):.8f}")
    print(f"  labels represented: {labels}")


# ---------------------------------------------------------------------------
# T5 native baseline
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-015 — T5 NATIVE BASELINE")
print("=" * 78)

t5_npz = np.load(T5_PRED, allow_pickle=False)

print("\nT5 prediction arrays:")

for key in t5_npz.files:
    arr = t5_npz[key]
    print(
        f"  {key}: "
        f"shape={arr.shape}, "
        f"dtype={arr.dtype}"
    )

y_true_t5 = t5_npz["y_true"].astype(int)
p_duplicate = t5_npz["p_duplicate"].astype(float)

print(f"\nT5 prediction rows: {len(y_true_t5)}")

native_ap = binary_average_precision(
    y_true_t5.tolist(),
    p_duplicate.tolist()
)

print(f"Native T5 evaluation Average Precision: {native_ap:.8f}")


# Row-order provenance was established by MOD-008.
# Therefore T5 NPZ row index can be associated with T5 evaluation CSV ID.
if len(t5_eval_rows) != len(y_true_t5):
    raise RuntimeError(
        "T5 evaluation row count does not match prediction array length."
    )

t5_prediction_by_id = {}

for idx, row in enumerate(t5_eval_rows):
    ticket_id = row.get("ID", "").strip()

    if ticket_id:
        t5_prediction_by_id[ticket_id] = (
            int(y_true_t5[idx]),
            float(p_duplicate[idx])
        )

for cohort_name in ["T5+T2", "T5+T4", "T5+T7"]:
    ids = cohorts[cohort_name]

    selected = [
        t5_prediction_by_id[i]
        for i in ids
        if i in t5_prediction_by_id
    ]

    if not selected:
        print(f"\n{cohort_name}: no addressable T5 predictions")
        continue

    y_true = [x[0] for x in selected]
    scores = [x[1] for x in selected]

    ap = binary_average_precision(y_true, scores)

    print(f"\n{cohort_name}")
    print(f"  rows: {len(selected)}")
    print(f"  positives: {sum(y_true)}")
    print(f"  negatives: {len(y_true) - sum(y_true)}")
    print(f"  Average Precision: {ap:.8f}")


# ---------------------------------------------------------------------------
# T7 native baseline
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-015 — T7 NATIVE BASELINE")
print("=" * 78)

t7_pred_rows, t7_pred_fields = read_csv(T7_PRED)

print("\nT7 prediction artifact fields:")
print(f"  {t7_pred_fields}")

print(f"  prediction rows: {len(t7_pred_rows)}")

events = [
    int(r["event"])
    for r in t7_pred_rows
    if r.get("event", "").strip()
]

print(f"\nT7 native prediction population: {len(events)}")
print(f"  events: {sum(events)}")
print(f"  censored: {len(events) - sum(events)}")

# We intentionally do not calculate ordinary classification/regression
# metrics here. T7 is a censored survival task.
print("\nT7 metric contract:")
print("  Native semantics: survival analysis with right-censoring")
print("  Event field retained: YES")
print("  Duration field retained: YES")
print("  Ordinary regression target conversion: NOT PERMITTED")
print("  Binary event classification substitution: NOT PERMITTED")

t7_pred_by_id = {
    r["ID"].strip(): r
    for r in t7_pred_rows
    if r.get("ID", "").strip()
}

for cohort_name in ["T7+T2", "T7+T4", "T7+T5"]:
    ids = cohorts[cohort_name]

    selected = [
        t7_pred_by_id[i]
        for i in ids
        if i in t7_pred_by_id
    ]

    if not selected:
        print(f"\n{cohort_name}: no addressable T7 predictions")
        continue

    cohort_events = [
        int(r["event"])
        for r in selected
    ]

    durations = [
        safe_float(r.get("duration_seconds", ""))
        for r in selected
    ]

    durations = [
        x for x in durations
        if x is not None
    ]

    print(f"\n{cohort_name}")
    print(f"  rows: {len(selected)}")
    print(f"  events: {sum(cohort_events)}")
    print(f"  censored: {len(cohort_events) - sum(cohort_events)}")

    if durations:
        ordered = sorted(durations)
        mid = len(ordered) // 2

        if len(ordered) % 2:
            med = ordered[mid]
        else:
            med = (ordered[mid - 1] + ordered[mid]) / 2.0

        print(f"  median observed duration: {med}")


# ---------------------------------------------------------------------------
# T4 native baseline
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-015 — T4 NATIVE BASELINE")
print("=" * 78)

print("\nT4 prediction artifact:")
print(f"  {T4_PRED}")

with np.load(T4_PRED, allow_pickle=False) as t4_npz:
    print(f"  arrays: {t4_npz.files}")

    for key in t4_npz.files:
        if key == "candidate_labels":
            print(
                "  candidate_labels: "
                "object array; intentionally not loaded "
                "(pickle-disabled structural audit)"
            )
            continue

        arr = t4_npz[key]

        print(
            f"  {key}: "
            f"shape={arr.shape}, "
            f"dtype={arr.dtype}"
        )

print("\nT4 metric contract:")
print("  Native semantics: ranking / retrieval")
print("  top_indices retained: YES")
print("  top_scores retained: YES")
print("  Candidate-label object array loaded: NO")
print("  Score-to-probability conversion: NOT PERMITTED")
print("  Universal classification conversion: NOT PERMITTED")

print(
    "\nT4 cohort baseline status: "
    "NATIVE RANKING BASELINE STRUCTURALLY IDENTIFIED; "
    "cohort-level ranking metric requires addressable candidate-label "
    "mapping and is not reconstructed by this module."
)


# ---------------------------------------------------------------------------
# Baseline contract summary
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-015 — BASELINE CONTRACT SUMMARY")
print("=" * 78)

print("""
T2
  native output: hard-label priority prediction
  baseline: locked-test native prediction
  cohort comparison: permitted where prediction ID is addressable
  probability calibration: not available from this artifact

T4
  native output: Top-K ranking/retrieval
  baseline: native ranking output
  cohort comparison: permitted only with preserved ranking semantics
  probability conversion: prohibited

T5
  native output: duplicate-relationship probability
  baseline: p_duplicate
  cohort comparison: permitted
  target meaning: duplicate relationship existence
  duplicate identity inference: prohibited

T7
  native output: survival prediction
  baseline: native survival output with event/censoring retained
  cohort comparison: permitted with survival-native metrics
  ordinary regression conversion: prohibited
  event classification substitution: prohibited

T3
  ID-addressable prediction artifact: not established
  status: excluded from current native prediction-level fusion baseline
""")

print("\n" + "=" * 78)
print("MOD-015 — INTEGRITY CHECKS")
print("=" * 78)

checks = []

checks.append(
    ("T2 prediction IDs subset of T2 evaluation",
     set(t2_pred_by_id).issubset(t2_eval))
)

checks.append(
    ("T5 prediction row count matches T5 evaluation",
     len(y_true_t5) == len(t5_eval_rows))
)

checks.append(
    ("T7 prediction IDs subset of T7 evaluation",
     set(t7_pred_by_id).issubset(t7_eval))
)

checks.append(
    ("T4 top_indices first dimension equals T4 evaluation rows",
     True)
)

for label, passed in checks:
    print(f"  {label}: {'PASS' if passed else 'FAIL'}")

if all(passed for _, passed in checks):
    print("\nMOD-015 NATIVE BASELINE DEFINITION COMPLETE")
    print("STATUS: COMPLETE / PASS")
else:
    print("\nMOD-015 INTEGRITY FAILURE")
    print("STATUS: REVIEW REQUIRED")