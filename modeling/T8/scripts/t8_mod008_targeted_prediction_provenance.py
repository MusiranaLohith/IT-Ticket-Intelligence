#!/usr/bin/env python3

import csv
import json
from pathlib import Path

import numpy as np


# ============================================================
# T8 MOD-008
# Targeted Prediction Provenance Proof
#
# READ-ONLY
# No model loading
# No training
# No raw Mozilla archive access
# No pickle-enabled loading
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

T5_EVAL = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T5_EVAL_GROUP_AWARE.csv"
)

T5_NPZ = (
    MODELING_ROOT / "T5/metrics/"
    "t5_mod009_locked_evaluation_predictions.npz"
)

T4_EVAL = MODELING_ROOT / "T4/derived/t4_eval.csv"

T4_NPZ = (
    MODELING_ROOT / "T4/results/r1_checkpoints/"
    "t4_r1_topk_predictions.npz"
)

T4_GENERATOR = (
    MODELING_ROOT / "T4/scripts/t4_baseline_r1.py"
)

T3_TEST_SCRIPT = (
    MODELING_ROOT / "T3/scripts/t3_locked_test.py"
)

T3_LOCKED_META = (
    MODELING_ROOT / "T3/analysis/t3_locked_test_evaluation.json"
)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def normalize_id(value):
    if value is None:
        return None

    value = str(value).strip()

    return value if value else None


def read_csv_column(path, column_name):
    values = []

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        if column_name not in reader.fieldnames:
            raise RuntimeError(
                f"{column_name!r} not found in {path}"
            )

        for row in reader:
            values.append(row[column_name])

    return values


def read_csv_ids(path, id_column=None):
    values = []

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        if id_column is None:
            if "ID" in reader.fieldnames:
                id_column = "ID"
            elif "ticket_id" in reader.fieldnames:
                id_column = "ticket_id"
            else:
                raise RuntimeError(
                    f"No supported ID column found in {path}. "
                    f"Columns: {reader.fieldnames}"
                )

        if id_column not in reader.fieldnames:
            raise RuntimeError(
                f"{id_column!r} not found in {path}"
            )

        for row in reader:
            values.append(
                normalize_id(row[id_column])
            )

    return values


def print_header(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


# ============================================================
# 1. T5 row-order proof
# ============================================================

print_header("MOD-008 — T5 ROW-ORDER PROVENANCE")

print(f"T5 evaluation CSV: {T5_EVAL}")
print(f"T5 prediction NPZ: {T5_NPZ}")

t5_target_raw = read_csv_column(
    T5_EVAL,
    "T5 target"
)

t5_target = []

for value in t5_target_raw:

    value = normalize_id(value)

    if value is None:
        t5_target.append(None)
    else:
        try:
            t5_target.append(int(float(value)))
        except ValueError:
            t5_target.append(value)

print(f"Evaluation rows: {len(t5_target)}")

with np.load(T5_NPZ, allow_pickle=False) as data:

    print(f"NPZ arrays: {list(data.files)}")

    y_true = data["y_true"]

    print(f"NPZ y_true shape: {y_true.shape}")
    print(f"NPZ y_true dtype: {y_true.dtype}")

    if len(t5_target) != len(y_true):
        print("RESULT: FAIL — row counts differ.")

    else:

        csv_targets = np.asarray(
            t5_target,
            dtype=y_true.dtype
        )

        exact_match = np.array_equal(
            csv_targets,
            y_true
        )

        mismatch_count = int(
            np.count_nonzero(csv_targets != y_true)
        )

        print(
            f"Exact row-for-row y_true match: "
            f"{exact_match}"
        )

        print(
            f"Target mismatches: "
            f"{mismatch_count}"
        )

        if exact_match:
            print(
                "PROVENANCE RESULT: PASS — the NPZ y_true "
                "array preserves the T5 evaluation CSV row order."
            )
        else:
            print(
                "PROVENANCE RESULT: FAIL — NPZ y_true does not "
                "match the T5 evaluation CSV row order."
            )


# ============================================================
# 2. T5 ID population
# ============================================================

print_header("MOD-008 — T5 ID POPULATION")

t5_ids = read_csv_ids(T5_EVAL)

print(f"T5 evaluation rows: {len(t5_ids)}")
print(f"T5 unique IDs: {len(set(t5_ids))}")
print(f"Blank IDs: {sum(x is None for x in t5_ids)}")

canonical_ids = set(
    read_csv_ids(
        LAYER_A,
        id_column="ticket_id"
    )
)

overlap = set(t5_ids) & canonical_ids

print(
    f"IDs in canonical T8 population: "
    f"{len(overlap)}"
)

print(
    f"Canonical overlap: "
    f"{len(overlap) / len(t5_ids) * 100:.6f}%"
)


# ============================================================
# 3. T4 evaluation population
# ============================================================

print_header("MOD-008 — T4 EVALUATION POPULATION")

t4_ids = read_csv_ids(T4_EVAL)

print(f"T4 evaluation path: {T4_EVAL}")
print(f"T4 evaluation rows: {len(t4_ids)}")
print(f"T4 unique IDs: {len(set(t4_ids))}")
print(f"Blank IDs: {sum(x is None for x in t4_ids)}")

t4_unique = set(t4_ids)
t4_overlap = t4_unique & canonical_ids

print(
    f"T4 IDs in canonical T8 population: "
    f"{len(t4_overlap)}"
)

if t4_ids:
    print(
        f"T4 canonical coverage: "
        f"{len(t4_overlap) / len(t4_unique) * 100:.6f}%"
    )


# ============================================================
# 4. T4 Top-K structural alignment
# ============================================================

print_header("MOD-008 — T4 TOP-K ROW ALIGNMENT")

with np.load(T4_NPZ, allow_pickle=False) as data:

    print(f"NPZ arrays: {list(data.files)}")

    top_indices = data["top_indices"]
    top_scores = data["top_scores"]

    print(
        f"top_indices shape: "
        f"{top_indices.shape}"
    )

    print(
        f"top_scores shape: "
        f"{top_scores.shape}"
    )

    print(
        f"T4 evaluation rows: "
        f"{len(t4_ids)}"
    )

    row_count_match = (
        top_indices.shape[0] == len(t4_ids)
        and top_scores.shape[0] == len(t4_ids)
    )

    print(
        f"Prediction/evaluation row-count match: "
        f"{row_count_match}"
    )

    print(
        "Candidate-label object array intentionally not loaded."
    )


# ============================================================
# 5. T4 generator provenance
# ============================================================

print_header("MOD-008 — T4 GENERATOR PROVENANCE")

print(f"Generator: {T4_GENERATOR}")
print(f"Exists: {T4_GENERATOR.exists()}")

if T4_GENERATOR.exists():

    lines = T4_GENERATOR.read_text(
        encoding="utf-8",
        errors="replace"
    ).splitlines()

    target_terms = [
        "evaluation",
        "eval_df",
        "top_indices",
        "top_scores",
        "np.savez",
        "SCORES_PATH",
    ]

    hits = []

    for line_no, line in enumerate(lines, start=1):

        if any(term in line for term in target_terms):
            hits.append((line_no, line.strip()))

    print(
        f"Relevant generator lines found: "
        f"{len(hits)}"
    )

    for line_no, line in hits:
        print(
            f"L{line_no}: {line[:500]}"
        )


# ============================================================
# 6. T3 prediction-output provenance
# ============================================================

print_header("MOD-008 — T3 PREDICTION OUTPUT PROVENANCE")

print(f"T3 locked-test script: {T3_TEST_SCRIPT}")
print(f"Exists: {T3_TEST_SCRIPT.exists()}")

if T3_TEST_SCRIPT.exists():

    lines = T3_TEST_SCRIPT.read_text(
        encoding="utf-8",
        errors="replace"
    ).splitlines()

    target_terms = [
        "predict",
        "prediction",
        "y_pred",
        "pred",
        "to_csv",
        "json.dump",
        "np.save",
        "joblib.dump",
        "test.csv",
    ]

    hits = []

    for line_no, line in enumerate(lines, start=1):

        if any(term in line.lower() for term in target_terms):
            hits.append((line_no, line.strip()))

    print(
        f"Prediction/output-related lines found: "
        f"{len(hits)}"
    )

    for line_no, line in hits:
        print(
            f"L{line_no}: {line[:500]}"
        )


print()
print(f"T3 locked-test metadata: {T3_LOCKED_META}")
print(f"Exists: {T3_LOCKED_META.exists()}")

if T3_LOCKED_META.exists():

    try:
        with T3_LOCKED_META.open(
            "r",
            encoding="utf-8",
            errors="replace"
        ) as f:
            metadata = json.load(f)

        print("Metadata keys:")
        for key in metadata.keys():
            print(f"  {key}")

        print()

        print("Artifact section:")

        artifacts = metadata.get("artifacts")

        if artifacts is not None:
            print(
                json.dumps(
                    artifacts,
                    indent=2
                )
            )
        else:
            print("No explicit artifacts section.")

    except Exception as exc:
        print(
            f"Could not parse T3 metadata: "
            f"{type(exc).__name__}: {exc}"
        )


# ============================================================
# 7. Final status
# ============================================================

print_header("MOD-008 — FINAL TARGETED PROVENANCE STATUS")

print(
    "T5: row-order proof performed by comparing NPZ y_true "
    "against the evaluation CSV T5 target."
)

print(
    "T4: evaluation IDs, Top-K row counts, and prediction "
    "generation code inspected without loading the object array."
)

print(
    "T3: locked-test prediction/output generation inspected "
    "without executing the model."
)

print()
print("MOD-008 END")
print("READ-ONLY")
print("No model loaded.")
print("No training performed.")
print("No raw Mozilla archive accessed.")
print("No pickle-enabled loading performed.")
print("No existing artifact modified.")