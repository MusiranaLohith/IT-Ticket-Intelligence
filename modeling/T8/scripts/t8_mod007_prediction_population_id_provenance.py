#!/usr/bin/env python3

import csv
import json
import re
import zipfile
from pathlib import Path

import numpy as np


# ============================================================
# T8 MOD-007
# Prediction Population / ID Provenance Reconciliation
#
# READ-ONLY AUDIT
# No model loading
# No training
# No raw Mozilla archive access
# No artifact modification
# No pickle execution
# ============================================================

csv.field_size_limit(2**31 - 1)


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
MODELING_ROOT = PROJECT_ROOT / "modeling"
T8_ROOT = MODELING_ROOT / "T8"

LAYER_A = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T8_LAYER_A_TICKET_EVIDENCE_derived.csv"
)

T2_PRED = (
    MODELING_ROOT / "T2/analysis/t2_final_test_predictions.csv"
)

T5_EVAL = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T5_EVAL_GROUP_AWARE.csv"
)

T5_PRED = (
    MODELING_ROOT / "T5/metrics/"
    "t5_mod009_locked_evaluation_predictions.npz"
)

T4_PRED = (
    MODELING_ROOT / "T4/results/r1_checkpoints/"
    "t4_r1_topk_predictions.npz"
)

T7_PRED = (
    MODELING_ROOT / "T7/derived/"
    "t7_mod010_evaluation_predictions.csv"
)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def print_header(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def normalize_id(value):
    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def find_id_column(fieldnames):
    if not fieldnames:
        return None

    candidates = [
        "ID",
        "id",
        "ticket_id",
        "ticketID",
        "issue_id",
        "issueID",
    ]

    lowered = {f.lower(): f for f in fieldnames}

    for candidate in candidates:
        if candidate in fieldnames:
            return candidate

        if candidate.lower() in lowered:
            return lowered[candidate.lower()]

    # Conservative fallback:
    for field in fieldnames:
        low = field.lower()
        if low.endswith("_id") or low == "id":
            return field

    return None


def read_csv_ids(path):
    result = {
        "path": str(path),
        "exists": path.exists(),
        "rows": 0,
        "id_column": None,
        "ids": [],
        "blank_ids": 0,
        "duplicate_ids": 0,
        "header": [],
    }

    if not path.exists():
        return result

    seen = set()

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:

        reader = csv.reader(f)

        try:
            header = next(reader)
        except StopIteration:
            return result

        result["header"] = header
        id_col = find_id_column(header)
        result["id_column"] = id_col

        if id_col is None:
            return result

        idx = header.index(id_col)

        for row in reader:
            result["rows"] += 1

            value = row[idx] if idx < len(row) else ""
            value = normalize_id(value)

            if value is None:
                result["blank_ids"] += 1
                continue

            if value in seen:
                result["duplicate_ids"] += 1

            seen.add(value)
            result["ids"].append(value)

    return result


def read_csv_header_and_rows(path):
    result = {
        "path": str(path),
        "exists": path.exists(),
        "rows": 0,
        "header": [],
    }

    if not path.exists():
        return result

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:

        reader = csv.reader(f)

        try:
            header = next(reader)
        except StopIteration:
            return result

        result["header"] = header

        for _ in reader:
            result["rows"] += 1

    return result


def load_json(path):
    try:
        with path.open(
            "r",
            encoding="utf-8",
            errors="replace"
        ) as f:
            return json.load(f)
    except Exception:
        return None


def flatten_strings(obj, prefix=""):
    """
    Recursively collect string-valued JSON fields.
    Used only for provenance text discovery.
    """
    results = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            results.extend(flatten_strings(value, path))

    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            path = f"{prefix}[{i}]"
            results.extend(flatten_strings(value, path))

    elif isinstance(obj, str):
        results.append((prefix, obj))

    return results


def print_population_result(name, artifact, canonical_ids):
    print()
    print(f"[{name}]")
    print(f"  Path: {artifact['path']}")
    print(f"  Exists: {artifact['exists']}")
    print(f"  Rows: {artifact['rows']}")
    print(f"  ID column: {artifact['id_column']}")
    print(f"  Blank IDs: {artifact['blank_ids']}")
    print(f"  Duplicate IDs: {artifact['duplicate_ids']}")

    if not artifact["ids"]:
        print("  Canonical overlap: NOT COMPUTABLE")
        return

    ids = set(artifact["ids"])
    overlap = ids & canonical_ids

    print(f"  Unique IDs: {len(ids)}")
    print(f"  IDs in canonical T8 population: {len(overlap)}")
    print(
        f"  Coverage of artifact by canonical T8 population: "
        f"{len(overlap) / len(ids) * 100:.6f}%"
    )
    print(
        f"  Canonical T8 tickets represented: "
        f"{len(overlap) / len(canonical_ids) * 100:.6f}%"
    )

    outside = ids - canonical_ids

    print(f"  IDs outside canonical T8 population: {len(outside)}")

    if outside:
        sample = sorted(outside)[:10]
        print(f"  Outside-ID sample: {sample}")


# ------------------------------------------------------------
# 1. Canonical T8 population
# ------------------------------------------------------------

print_header("MOD-007 — CANONICAL T8 POPULATION")

canonical = read_csv_ids(LAYER_A)

print(f"Layer A path: {LAYER_A}")
print(f"Exists: {canonical['exists']}")
print(f"Rows: {canonical['rows']}")
print(f"ID column: {canonical['id_column']}")
print(f"Blank IDs: {canonical['blank_ids']}")
print(f"Duplicate IDs: {canonical['duplicate_ids']}")

canonical_ids = set(canonical["ids"])

print(f"Unique canonical ticket IDs: {len(canonical_ids)}")

if len(canonical_ids) != canonical["rows"]:
    print("WARNING: canonical Layer A is not one-row-per-unique-ID.")

print()


# ------------------------------------------------------------
# 2. T2 direct ID reconciliation
# ------------------------------------------------------------

print_header("MOD-007 — T2 ID RECONCILIATION")

t2 = read_csv_ids(T2_PRED)
print_population_result("T2 final test predictions", t2, canonical_ids)


# ------------------------------------------------------------
# 3. T7 direct ID reconciliation
# ------------------------------------------------------------

print_header("MOD-007 — T7 ID RECONCILIATION")

t7 = read_csv_ids(T7_PRED)
print_population_result("T7 evaluation predictions", t7, canonical_ids)


# ------------------------------------------------------------
# 4. T5 evaluation CSV
# ------------------------------------------------------------

print_header("MOD-007 — T5 EVALUATION POPULATION")

t5_eval = read_csv_ids(T5_EVAL)

print(f"Path: {T5_EVAL}")
print(f"Exists: {t5_eval['exists']}")
print(f"Rows: {t5_eval['rows']}")
print(f"Header: {t5_eval['header']}")
print(f"Detected ID column: {t5_eval['id_column']}")
print(f"Blank IDs: {t5_eval['blank_ids']}")
print(f"Duplicate IDs: {t5_eval['duplicate_ids']}")

if t5_eval["ids"]:
    t5_eval_ids = set(t5_eval["ids"])
    overlap = t5_eval_ids & canonical_ids

    print(f"Unique evaluation IDs: {len(t5_eval_ids)}")
    print(f"IDs in canonical T8 population: {len(overlap)}")
    print(
        f"Canonical overlap: "
        f"{len(overlap) / len(t5_eval_ids) * 100:.6f}%"
    )
    print(
        f"Canonical population represented: "
        f"{len(overlap) / len(canonical_ids) * 100:.6f}%"
    )


# ------------------------------------------------------------
# 5. T5 NPZ row alignment
# ------------------------------------------------------------

print_header("MOD-007 — T5 NPZ / EVALUATION ROW ALIGNMENT")

print(f"NPZ path: {T5_PRED}")
print(f"Exists: {T5_PRED.exists()}")

if T5_PRED.exists():

    with np.load(T5_PRED, allow_pickle=False) as data:

        print(f"NPZ arrays: {list(data.files)}")

        array_lengths = {}

        for key in data.files:
            arr = data[key]

            print(
                f"  {key}: "
                f"shape={arr.shape}, "
                f"dtype={arr.dtype}"
            )

            if arr.ndim >= 1:
                array_lengths[key] = arr.shape[0]

        unique_lengths = sorted(set(array_lengths.values()))

        print(f"Array first-dimension lengths: {unique_lengths}")

        if t5_eval["exists"]:

            if len(unique_lengths) == 1:
                npz_rows = unique_lengths[0]

                print(f"T5 evaluation CSV rows: {t5_eval['rows']}")
                print(f"T5 NPZ rows: {npz_rows}")

                if npz_rows == t5_eval["rows"]:
                    print(
                        "RESULT: T5 NPZ row count matches "
                        "evaluation CSV row count."
                    )
                else:
                    print(
                        "RESULT: T5 NPZ row count DOES NOT match "
                        "evaluation CSV row count."
                    )
            else:
                print(
                    "RESULT: T5 NPZ arrays do not share one common "
                    "row population."
                )


# ------------------------------------------------------------
# 6. T4 NPZ safe structural inspection
# ------------------------------------------------------------

print_header("MOD-007 — T4 NPZ SAFE STRUCTURAL INSPECTION")

print(f"NPZ path: {T4_PRED}")
print(f"Exists: {T4_PRED.exists()}")

if T4_PRED.exists():

    with zipfile.ZipFile(T4_PRED, "r") as zf:

        members = zf.namelist()

        print(f"Archive members: {members}")

        for member in members:

            if not member.endswith(".npy"):
                continue

            info = zf.getinfo(member)

            print()
            print(f"Member: {member}")
            print(f"  Compressed size: {info.compress_size}")
            print(f"  Uncompressed size: {info.file_size}")

            # NumPy's .npy header can be read safely without
            # loading object-array contents.
            with zf.open(member, "r") as raw:

                version = np.lib.format.read_magic(raw)

                if version == (1, 0):
                    shape, fortran_order, dtype = (
                        np.lib.format.read_array_header_1_0(raw)
                    )

                elif version == (2, 0):
                    shape, fortran_order, dtype = (
                        np.lib.format.read_array_header_2_0(raw)
                    )

                elif version == (3, 0):
                    shape, fortran_order, dtype = (
                        np.lib.format.read_array_header_2_0(raw)
                    )

                else:
                    raise RuntimeError(
                        f"Unsupported .npy header version: {version}"
                    )

                print(f"  NPY version: {version}")
                print(f"  Shape: {shape}")
                print(f"  Fortran order: {fortran_order}")
                print(f"  Dtype: {dtype}")

                if dtype.hasobject:
                    print(
                        "  OBJECT ARRAY: contents intentionally NOT "
                        "loaded because that would require pickle."
                    )
                else:
                    print(
                        "  Non-object array: header is sufficient for "
                        "structural provenance audit."
                    )


# ------------------------------------------------------------
# 7. T4 provenance text discovery
# ------------------------------------------------------------

print_header("MOD-007 — T4 PROVENANCE TRACE")

t4_keywords = [
    "t4_r1_topk_predictions.npz",
    "top_indices",
    "top_scores",
    "35626",
    "r1_checkpoints",
]

t4_matches = []

for path in MODELING_ROOT.glob("T4/**/*"):
    if not path.is_file():
        continue

    if path.suffix.lower() not in {
        ".py", ".json", ".txt", ".md", ".csv"
    }:
        continue

    try:
        text = path.read_text(
            encoding="utf-8",
            errors="replace"
        )
    except Exception:
        continue

    matched = [
        keyword
        for keyword in t4_keywords
        if keyword in text
    ]

    if matched:
        t4_matches.append((path, matched))


print(f"T4 provenance files containing target terms: {len(t4_matches)}")

for path, matched in t4_matches[:50]:
    print()
    print(f"FILE: {path}")
    print(f"MATCHES: {matched}")

    try:
        lines = path.read_text(
            encoding="utf-8",
            errors="replace"
        ).splitlines()

        shown = 0

        for line_no, line in enumerate(lines, start=1):

            if any(k in line for k in t4_keywords):

                print(
                    f"  L{line_no}: "
                    f"{line[:300]}"
                )

                shown += 1

                if shown >= 12:
                    break

    except Exception:
        pass


# ------------------------------------------------------------
# 8. T3 prediction artifact / provenance trace
# ------------------------------------------------------------

print_header("MOD-007 — T3 PREDICTION ARTIFACT TRACE")

t3_candidates = []

for path in MODELING_ROOT.glob("T3/**/*"):
    if not path.is_file():
        continue

    name = path.name.lower()

    if any(
        token in name
        for token in (
            "pred",
            "prediction",
            "eval",
            "evaluation",
            "output",
            "test",
        )
    ):
        t3_candidates.append(path)


print(f"T3 filename-level candidates: {len(t3_candidates)}")

for path in sorted(t3_candidates)[:100]:
    print(f"  {path}")


print()
print("T3 JSON provenance metadata:")

for path in sorted(
    MODELING_ROOT.glob("T3/**/*.json")
):

    name = path.name.lower()

    if not any(
        token in name
        for token in (
            "closure",
            "evaluation",
            "metrics",
            "selection",
            "final",
            "test",
        )
    ):
        continue

    data = load_json(path)

    if data is None:
        continue

    print()
    print(f"FILE: {path}")

    strings = flatten_strings(data)

    relevant = []

    for key, value in strings:

        low = value.lower()

        if any(
            token in low
            for token in (
                "prediction",
                "predictions",
                "test.csv",
                "eval",
                "evaluation",
                "artifact",
                "rows",
                "id",
            )
        ):
            relevant.append((key, value))

    for key, value in relevant[:40]:
        print(f"  {key}: {value}")


# ------------------------------------------------------------
# 9. T5/T2/T7 metadata population references
# ------------------------------------------------------------

print_header("MOD-007 — TASK POPULATION METADATA CROSS-CHECK")

metadata_targets = {
    "T2": [
        "t2_final_closure.json",
        "t2_final_test_metrics.json",
        "t2_final_model_selection.json",
    ],
    "T5": [
        "t5_mod009_locked_evaluation_metrics.json",
        "t5_mod011_final_closure.json",
    ],
    "T7": [
        "t7_mod011_final_model_comparison_audit.json",
        "t7_mod012_final_closure.json",
    ],
}

for task, filenames in metadata_targets.items():

    print()
    print(f"--- {task} ---")

    task_root = MODELING_ROOT / task

    for filename in filenames:

        matches = list(task_root.rglob(filename))

        for path in matches:

            data = load_json(path)

            print(f"FILE: {path}")

            if data is None:
                print("  Could not parse JSON.")
                continue

            strings = flatten_strings(data)

            for key, value in strings:

                low = value.lower()

                if any(
                    token in low
                    for token in (
                        "evaluation",
                        "eval",
                        "test",
                        "prediction",
                        "artifact",
                        "rows",
                        "population",
                        "split",
                    )
                ):

                    print(
                        f"  {key}: {value}"
                    )


# ------------------------------------------------------------
# 10. Final status
# ------------------------------------------------------------

print_header("MOD-007 — PROVISIONAL RECONCILIATION STATUS")

print(
    "This operation does NOT select fusion inputs and does NOT "
    "create a common prediction population."
)

print(
    "Direct ID-bearing artifacts can be compared against the "
    "canonical 513,816-ticket T8 population."
)

print(
    "T5 requires row-order provenance between the NPZ arrays and "
    "the exact group-aware evaluation CSV."
)

print(
    "T4 requires provenance from the Top-K artifact back to its "
    "evaluation split; object-array contents were not loaded."
)

print(
    "T3 requires resolution of whether a per-record prediction "
    "artifact exists and how its evaluation rows map to ticket IDs."
)

print()
print("MOD-007 COMPLETE: PROVENANCE RESULTS ABOVE.")
print("No model training performed.")
print("No model loaded.")
print("No raw Mozilla archive accessed.")
print("No pickle-enabled NPZ loading performed.")
print("No existing artifact modified.")