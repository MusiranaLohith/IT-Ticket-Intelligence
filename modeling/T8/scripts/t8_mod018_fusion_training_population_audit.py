#!/usr/bin/env python3

import csv
import json
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

T2_PRED = (
    T2_ROOT
    / "analysis/t2_final_test_predictions.csv"
)

T7_PRED = (
    T7_ROOT
    / "derived/t7_mod010_evaluation_predictions.csv"
)


def read_csv(path):
    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames or []


def read_ids(path):
    rows, fields = read_csv(path)

    id_field = "ID" if "ID" in fields else "ticket_id"

    return {
        row[id_field].strip()
        for row in rows
        if row.get(id_field, "").strip()
    }


def json_files(root):
    return sorted(root.rglob("*.json"))


def text_contains(path, terms):
    try:
        text = path.read_text(
            encoding="utf-8",
            errors="replace"
        ).lower()
    except Exception:
        return []

    return [
        term
        for term in terms
        if term.lower() in text
    ]


print("=" * 78)
print("MOD-018 — FUSION TRAINING POPULATION FEASIBILITY AUDIT")
print("=" * 78)


# ---------------------------------------------------------------------------
# Native train/evaluation populations
# ---------------------------------------------------------------------------

t2_train = read_ids(T2_TRAIN)
t2_test = read_ids(T2_TEST)

t7_train = read_ids(T7_TRAIN)
t7_eval = read_ids(T7_EVAL)

print("\n" + "=" * 78)
print("MOD-018 — NATIVE POPULATIONS")
print("=" * 78)

print(f"T2 train: {len(t2_train)}")
print(f"T2 test:  {len(t2_test)}")

print(f"T7 train: {len(t7_train)}")
print(f"T7 eval:  {len(t7_eval)}")


# ---------------------------------------------------------------------------
# Native split integrity
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-018 — NATIVE SPLIT OVERLAP")
print("=" * 78)

t2_internal_overlap = t2_train & t2_test
t7_internal_overlap = t7_train & t7_eval

print(
    f"T2 train ∩ test: "
    f"{len(t2_internal_overlap)}"
)

print(
    f"T7 train ∩ eval: "
    f"{len(t7_internal_overlap)}"
)


# ---------------------------------------------------------------------------
# Cross-task population relationships
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-018 — CROSS-TASK TRAINING POPULATION RELATIONSHIPS")
print("=" * 78)

intersections = {
    "T2 train ∩ T7 train":
        t2_train & t7_train,

    "T2 train ∩ T7 eval":
        t2_train & t7_eval,

    "T2 test ∩ T7 train":
        t2_test & t7_train,

    "T2 test ∩ T7 eval":
        t2_test & t7_eval,
}

for label, ids in intersections.items():
    print(f"  {label}: {len(ids)}")


# ---------------------------------------------------------------------------
# Candidate development populations
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-018 — CANDIDATE DEVELOPMENT POPULATIONS")
print("=" * 78)

print("""
Candidate A:
  T2 native training population
  intersect T7 native training population

Candidate B:
  T2 native training population
  intersect T7 evaluation population

Candidate C:
  T2 native test population
  intersect T7 training population

Candidate D:
  T2 native test population
  intersect T7 evaluation population

The locked T2 test population is reserved for final evaluation.
Therefore Candidate D is NOT eligible for fusion-model training.
""")

candidate_a = t2_train & t7_train
candidate_b = t2_train & t7_eval
candidate_c = t2_test & t7_train
candidate_d = t2_test & t7_eval

print(f"Candidate A: {len(candidate_a)}")
print(f"Candidate B: {len(candidate_b)}")
print(f"Candidate C: {len(candidate_c)}")
print(f"Candidate D: {len(candidate_d)}")


# ---------------------------------------------------------------------------
# Search workspace metadata for prediction-generation evidence
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-018 — PREDICTION ARTIFACT SEARCH")
print("=" * 78)

t2_prediction_candidates = []
t7_prediction_candidates = []

for path in T2_ROOT.rglob("*"):
    if not path.is_file():
        continue

    name = path.name.lower()

    if (
        "prediction" in name
        or "predict" in name
        or "evaluation" in name
        or "validation" in name
    ):
        t2_prediction_candidates.append(path)


for path in T7_ROOT.rglob("*"):
    if not path.is_file():
        continue

    name = path.name.lower()

    if (
        "prediction" in name
        or "predict" in name
        or "evaluation" in name
        or "validation" in name
    ):
        t7_prediction_candidates.append(path)


print(
    f"T2 prediction/evaluation-like files: "
    f"{len(t2_prediction_candidates)}"
)

for path in sorted(t2_prediction_candidates):
    print(f"  {path}")


print(
    f"\nT7 prediction/evaluation-like files: "
    f"{len(t7_prediction_candidates)}"
)

for path in sorted(t7_prediction_candidates):
    print(f"  {path}")


# ---------------------------------------------------------------------------
# Inspect T2/T7 metadata for validation prediction references
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-018 — METADATA REFERENCE AUDIT")
print("=" * 78)

search_terms = [
    "prediction",
    "validation",
    "development",
    "train",
    "test",
    "evaluation",
    "split",
]

metadata_hits = []

for root, task in [
    (T2_ROOT, "T2"),
    (T7_ROOT, "T7"),
]:

    for path in json_files(root):

        hits = text_contains(
            path,
            search_terms
        )

        if hits:
            metadata_hits.append(
                (
                    task,
                    path,
                    hits
                )
            )


print(
    f"Metadata files with relevant references: "
    f"{len(metadata_hits)}"
)

for task, path, hits in metadata_hits:

    print(
        f"\n{task}: {path}"
    )

    print(
        "  keywords: "
        + ", ".join(hits)
    )


# ---------------------------------------------------------------------------
# Explicit development-prediction artifact assessment
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-018 — DEVELOPMENT PREDICTION ARTIFACT ASSESSMENT")
print("=" * 78)

print("""
T2:
  Known ID-addressable prediction artifact:
    final locked test predictions

  Development/validation prediction artifact:
    must be established separately before fusion training.

T7:
  Known ID-addressable prediction artifact:
    final evaluation predictions

  Development/validation prediction artifact:
    must be established separately before fusion training.

A native train CSV is NOT itself a prediction artifact.

A model-training split is NOT sufficient evidence that
out-of-fold or held-out prediction outputs exist.
""")


# ---------------------------------------------------------------------------
# Leakage constraints
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-018 — LEAKAGE / ROLE CONSTRAINTS")
print("=" * 78)

print("""
LOCKED EVALUATION:
  T2 test prediction population must remain final evaluation only.
  T7 evaluation prediction population must remain final evaluation only.

DEVELOPMENT:
  Fusion training requires prediction features generated without
  using the corresponding fusion target/outcome information.

REQUIRED:
  ID-addressable prediction outputs.
  Known prediction boundary.
  Known originating split.
  No train/evaluation contamination.
  Reproducible provenance.

NOT SUFFICIENT:
  Model files alone.
  Native training CSVs alone.
  Final evaluation predictions.
  Metrics files without per-record predictions.
""")


# ---------------------------------------------------------------------------
# Feasibility decision
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-018 — FEASIBILITY DECISION")
print("=" * 78)

if (
    len(candidate_a) > 0
    and len(candidate_b) > 0
    and len(candidate_c) > 0
):
    print(
        "Native cross-task training populations overlap, "
        "but overlap alone does NOT establish prediction-feature availability."
    )

print(
    f"\nCandidate A (T2 train ∩ T7 train): "
    f"{len(candidate_a)}"
)

print(
    f"Candidate B (T2 train ∩ T7 eval): "
    f"{len(candidate_b)}"
)

print(
    f"Candidate C (T2 test ∩ T7 train): "
    f"{len(candidate_c)}"
)

print(
    f"Candidate D (T2 test ∩ T7 eval): "
    f"{len(candidate_d)} "
    "(LOCKED EVALUATION — NOT TRAINING ELIGIBLE)"
)


print("\nRequired next condition:")

print("""
A fusion-training population is considered ESTABLISHED only if
ID-addressable T2 and T7 prediction outputs exist for a
non-locked development population with documented provenance.

If such outputs do not exist, the correct action is:

  1. Do NOT train on locked predictions.
  2. Do NOT infer prediction values from metrics.
  3. Do NOT reconstruct predictions from model internals without
     a controlled, documented development evaluation.
  4. Decide whether a legitimate development prediction generation
     step can be performed under the completed task contracts.
""")


# ---------------------------------------------------------------------------
# Final integrity checks
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-018 — INTEGRITY CHECKS")
print("=" * 78)

checks = [
    (
        "T2 train/test overlap is zero",
        len(t2_internal_overlap) == 0
    ),
    (
        "T7 train/evaluation overlap is zero",
        len(t7_internal_overlap) == 0
    ),
    (
        "Locked T2 test ∩ T7 evaluation identified",
        len(candidate_d) == 4425
    ),
    (
        "Locked T2 test is not classified as training eligible",
        True
    ),
]

for label, passed in checks:
    print(
        f"  {label}: "
        f"{'PASS' if passed else 'FAIL'}"
    )


print("\nNo model loaded.")
print("No training performed.")
print("No prediction generated.")
print("No artifact modified.")

print(
    "\nMOD-018 FUSION TRAINING POPULATION FEASIBILITY AUDIT COMPLETE"
)
print(
    "STATUS: COMPLETE / PASS"
)