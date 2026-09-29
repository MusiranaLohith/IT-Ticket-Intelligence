#!/usr/bin/env python3

import csv
import json
from pathlib import Path

csv.field_size_limit(1024 * 1024 * 1024)

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_ROOT = PROJECT_ROOT / "modeling" / "T2"
T7_ROOT = PROJECT_ROOT / "modeling" / "T7"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_csv_info(path):
    if not path.exists():
        return {
            "exists": False,
            "rows": None,
            "fields": [],
            "ids": set(),
            "id_field": None,
        }

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:

        reader = csv.DictReader(f)
        fields = reader.fieldnames or []

        id_field = None

        for candidate in ["ID", "ticket_id"]:
            if candidate in fields:
                id_field = candidate
                break

        rows = 0
        ids = set()

        for row in reader:
            rows += 1

            if id_field:
                value = row.get(id_field, "").strip()

                if value:
                    ids.add(value)

        return {
            "exists": True,
            "rows": rows,
            "fields": fields,
            "ids": ids,
            "id_field": id_field,
        }


def read_json(path):
    try:
        with path.open(
            "r",
            encoding="utf-8",
            errors="replace"
        ) as f:
            return json.load(f)
    except Exception as exc:
        return {
            "__read_error__": str(exc)
        }


def flatten_strings(obj, prefix=""):
    """
    Recursively collect JSON leaf strings with their paths.
    """
    output = []

    if isinstance(obj, dict):

        for key, value in obj.items():

            child = (
                f"{prefix}.{key}"
                if prefix
                else str(key)
            )

            output.extend(
                flatten_strings(value, child)
            )

    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            child = f"{prefix}[{index}]"

            output.extend(
                flatten_strings(value, child)
            )

    elif isinstance(obj, str):

        output.append(
            (prefix, obj)
        )

    return output


def relevant_json_text(path, terms):
    data = read_json(path)

    flattened = flatten_strings(data)

    hits = []

    for field_path, value in flattened:

        lower_value = value.lower()

        matched = [
            term
            for term in terms
            if term.lower() in lower_value
        ]

        if matched:
            hits.append(
                {
                    "field": field_path,
                    "value": value,
                    "terms": matched,
                }
            )

    return hits


def print_csv_info(label, info):

    print(f"\n{label}")

    print(f"  exists: {info['exists']}")
    print(f"  rows: {info['rows']}")
    print(f"  ID field: {info['id_field']}")

    print(
        f"  unique IDs: "
        f"{len(info['ids'])}"
    )

    print(
        "  fields: "
        + ", ".join(info["fields"])
    )


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

print("=" * 80)
print(
    "MOD-019 — CONTROLLED DEVELOPMENT-PREDICTION "
    "FEASIBILITY / PROVENANCE AUDIT"
)
print("=" * 80)


# ---------------------------------------------------------------------------
# Native split artifacts
# ---------------------------------------------------------------------------

print("\n" + "=" * 80)
print("MOD-019 — NATIVE SPLIT ARTIFACTS")
print("=" * 80)

paths = {
    "T2 train":
        T2_ROOT / "splits" / "train.csv",

    "T2 validation":
        T2_ROOT / "splits" / "validation.csv",

    "T2 test":
        T2_ROOT / "splits" / "test.csv",

    "T7 train":
        T7_ROOT / "splits" / "t7_train.csv",

    "T7 evaluation":
        T7_ROOT / "splits" / "t7_evaluation.csv",
}

split_info = {}

for label, path in paths.items():

    info = read_csv_info(path)

    split_info[label] = info

    print_csv_info(
        f"{label}: {path}",
        info
    )


# ---------------------------------------------------------------------------
# Existing prediction artifacts
# ---------------------------------------------------------------------------

print("\n" + "=" * 80)
print("MOD-019 — EXISTING PREDICTION ARTIFACTS")
print("=" * 80)

prediction_paths = {
    "T2 baseline validation predictions":
        T2_ROOT
        / "analysis"
        / "t2_baseline_validation_predictions.csv",

    "T2 final test predictions":
        T2_ROOT
        / "analysis"
        / "t2_final_test_predictions.csv",

    "T7 MOD-007 evaluation predictions":
        T7_ROOT
        / "derived"
        / "t7_mod007_evaluation_predictions.csv",

    "T7 MOD-010 evaluation predictions":
        T7_ROOT
        / "derived"
        / "t7_mod010_evaluation_predictions.csv",
}

prediction_info = {}

for label, path in prediction_paths.items():

    info = read_csv_info(path)

    prediction_info[label] = info

    print_csv_info(
        f"{label}: {path}",
        info
    )


# ---------------------------------------------------------------------------
# Prediction-vs-split membership
# ---------------------------------------------------------------------------

print("\n" + "=" * 80)
print("MOD-019 — PREDICTION / SPLIT MEMBERSHIP")
print("=" * 80)


def compare_prediction_to_split(
    prediction_label,
    split_label
):

    pred_ids = prediction_info[prediction_label]["ids"]
    split_ids = split_info[split_label]["ids"]

    intersection = pred_ids & split_ids

    print(
        f"{prediction_label} "
        f"∩ {split_label}: "
        f"{len(intersection)}"
    )

    return intersection


t2_validation_ids = compare_prediction_to_split(
    "T2 baseline validation predictions",
    "T2 validation"
)

compare_prediction_to_split(
    "T2 baseline validation predictions",
    "T2 train"
)

compare_prediction_to_split(
    "T2 baseline validation predictions",
    "T2 test"
)

t2_test_prediction_ids = compare_prediction_to_split(
    "T2 final test predictions",
    "T2 test"
)

compare_prediction_to_split(
    "T2 final test predictions",
    "T2 train"
)

compare_prediction_to_split(
    "T2 final test predictions",
    "T2 validation"
)

t7_eval_prediction_ids = compare_prediction_to_split(
    "T7 MOD-010 evaluation predictions",
    "T7 evaluation"
)

compare_prediction_to_split(
    "T7 MOD-010 evaluation predictions",
    "T7 train"
)


# ---------------------------------------------------------------------------
# T2 validation artifact integrity
# ---------------------------------------------------------------------------

print("\n" + "=" * 80)
print("MOD-019 — T2 VALIDATION PREDICTION INTEGRITY")
print("=" * 80)

t2_val_pred = prediction_info[
    "T2 baseline validation predictions"
]

t2_val_split = split_info[
    "T2 validation"
]

if (
    t2_val_pred["exists"]
    and t2_val_split["exists"]
):

    print(
        "Prediction rows: "
        f"{t2_val_pred['rows']}"
    )

    print(
        "Validation split rows: "
        f"{t2_val_split['rows']}"
    )

    print(
        "Prediction unique IDs: "
        f"{len(t2_val_pred['ids'])}"
    )

    print(
        "Validation unique IDs: "
        f"{len(t2_val_split['ids'])}"
    )

    print(
        "Prediction IDs ∩ validation IDs: "
        f"{len(t2_validation_ids)}"
    )

    print(
        "Prediction IDs outside validation: "
        f"{len(t2_val_pred['ids'] - t2_val_split['ids'])}"
    )

    print(
        "Validation IDs without predictions: "
        f"{len(t2_val_split['ids'] - t2_val_pred['ids'])}"
    )


# ---------------------------------------------------------------------------
# T7 development-prediction discovery
# ---------------------------------------------------------------------------

print("\n" + "=" * 80)
print("MOD-019 — T7 DEVELOPMENT / VALIDATION PREDICTION DISCOVERY")
print("=" * 80)

t7_candidates = []

for path in sorted(T7_ROOT.rglob("*")):

    if not path.is_file():
        continue

    name = path.name.lower()

    if any(
        token in name
        for token in [
            "validation",
            "development",
            "oof",
            "out_of_fold",
            "predict"
        ]
    ):

        t7_candidates.append(path)

print(
    f"T7 candidate files: "
    f"{len(t7_candidates)}"
)

for path in t7_candidates:
    print(f"  {path}")


# ---------------------------------------------------------------------------
# Contract / metadata provenance audit
# ---------------------------------------------------------------------------

print("\n" + "=" * 80)
print("MOD-019 — CONTRACT / METADATA PROVENANCE AUDIT")
print("=" * 80)

terms = [
    "validation",
    "development",
    "out-of-fold",
    "out of fold",
    "oof",
    "prediction",
    "held-out",
    "evaluation",
    "test",
    "train",
    "split",
    "model selection",
    "selection",
]

for task_root, task_name in [
    (T2_ROOT, "T2"),
    (T7_ROOT, "T7"),
]:

    print(
        f"\n--- {task_name} relevant metadata ---"
    )

    json_paths = sorted(
        task_root.rglob("*.json")
    )

    shown = 0

    for path in json_paths:

        hits = relevant_json_text(
            path,
            terms
        )

        if not hits:
            continue

        # Show only the first several relevant fields
        print(f"\n{path}")

        for hit in hits[:12]:

            print(
                f"  {hit['field']}: "
                f"{hit['value']}"
            )

        if len(hits) > 12:
            print(
                f"  ... "
                f"{len(hits) - 12} additional matches"
            )

        shown += 1

        if shown >= 20:
            print(
                "\n  [metadata display capped at 20 files]"
            )
            break


# ---------------------------------------------------------------------------
# Shared development population
# ---------------------------------------------------------------------------

print("\n" + "=" * 80)
print("MOD-019 — SHARED DEVELOPMENT POPULATION")
print("=" * 80)

t2_train_ids = split_info["T2 train"]["ids"]
t2_validation_ids_set = split_info["T2 validation"]["ids"]

t7_train_ids = split_info["T7 train"]["ids"]
t7_eval_ids = split_info["T7 evaluation"]["ids"]

shared_train = (
    t2_train_ids
    & t7_train_ids
)

shared_validation = (
    t2_validation_ids_set
    & t7_eval_ids
)

print(
    "T2 train ∩ T7 train: "
    f"{len(shared_train)}"
)

print(
    "T2 validation ∩ T7 evaluation: "
    f"{len(shared_validation)}"
)


# ---------------------------------------------------------------------------
# Feasibility conditions
# ---------------------------------------------------------------------------

print("\n" + "=" * 80)
print("MOD-019 — CONTROLLED DEVELOPMENT PREDICTION CONDITIONS")
print("=" * 80)

print("""
For learned fusion training, the preferred development population
is a set of tickets for which each participating task contributes
an out-of-sample prediction.

Required evidence:

1. T2 prediction values are ID-addressable.
2. T2 predictions are generated on data not used to fit the
   corresponding T2 predictor for that prediction.
3. T7 prediction values are ID-addressable.
4. T7 predictions are generated on data not used to fit the
   corresponding T7 predictor for that prediction.
5. Both outputs share an explicit prediction boundary.
6. The provenance of each prediction population is documented.
7. Neither output originates from the locked final evaluation
   population.
8. The fusion-development target/outcome is separately defined.
""")


# ---------------------------------------------------------------------------
# Preliminary determination
# ---------------------------------------------------------------------------

print("\n" + "=" * 80)
print("MOD-019 — PRELIMINARY DETERMINATION")
print("=" * 80)

t2_validation_is_addressable = (
    len(t2_validation_ids) > 0
    and
    len(
        t2_val_pred["ids"]
        - t2_val_split["ids"]
    ) == 0
)

t7_development_candidates = [
    p for p in t7_candidates
    if p.suffix.lower() in [
        ".csv",
        ".npz",
        ".json"
    ]
]

print(
    "T2 ID-addressable validation prediction evidence: "
    f"{'PRESENT' if t2_validation_is_addressable else 'NOT ESTABLISHED'}"
)

print(
    "T7 validation/development prediction candidates: "
    f"{len(t7_development_candidates)}"
)

print("""
IMPORTANT:

Presence of a filename containing 'validation' or 'prediction'
does not establish that an artifact is a valid out-of-sample
development prediction artifact.

Its split provenance must be demonstrated before use.
""")


# ---------------------------------------------------------------------------
# Leakage guard
# ---------------------------------------------------------------------------

print("\n" + "=" * 80)
print("MOD-019 — LEAKAGE GUARD")
print("=" * 80)

checks = {
    "T2 validation predictions do not overlap T2 test":
        len(
            prediction_info[
                "T2 baseline validation predictions"
            ]["ids"]
            &
            split_info["T2 test"]["ids"]
        ) == 0,

    "T2 final test predictions are restricted to T2 test":
        len(
            prediction_info[
                "T2 final test predictions"
            ]["ids"]
            -
            split_info["T2 test"]["ids"]
        ) == 0,

    "T7 evaluation predictions are restricted to T7 evaluation":
        len(
            prediction_info[
                "T7 MOD-010 evaluation predictions"
            ]["ids"]
            -
            split_info["T7 evaluation"]["ids"]
        ) == 0,

    "T2 train/test split disjoint":
        len(
            split_info["T2 train"]["ids"]
            &
            split_info["T2 test"]["ids"]
        ) == 0,

    "T7 train/evaluation split disjoint":
        len(
            split_info["T7 train"]["ids"]
            &
            split_info["T7 evaluation"]["ids"]
        ) == 0,
}

for label, passed in checks.items():

    print(
        f"  {label}: "
        f"{'PASS' if passed else 'FAIL'}"
    )


# ---------------------------------------------------------------------------
# Final status
# ---------------------------------------------------------------------------

print("\n" + "=" * 80)
print("MOD-019 — FINAL STATUS")
print("=" * 80)

print("""
No model loaded.
No model trained.
No predictions generated.
No raw archive accessed.
No artifacts modified.

The audit determines whether existing task artifacts provide a
documented route to controlled development/OoF prediction features.

Fusion training remains BLOCKED until both participating task
prediction populations have demonstrated valid development
provenance.
""")

print(
    "\nMOD-019 CONTROLLED DEVELOPMENT-PREDICTION "
    "FEASIBILITY / PROVENANCE AUDIT COMPLETE"
)