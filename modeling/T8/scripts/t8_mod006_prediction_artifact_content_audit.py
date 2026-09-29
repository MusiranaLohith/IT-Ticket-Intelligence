#!/home/whiteblack/Documents/IT-Ticket-Triage-System/.venv/bin/python

import csv
import json
import os
import sys
from pathlib import Path

import numpy as np


# ------------------------------------------------------------
# T8 MOD-006
# Targeted Prediction-Artifact Content Audit
#
# READ-ONLY
# No model loading
# No training
# No raw Mozilla archive access
# No artifact modification
# ------------------------------------------------------------

csv.field_size_limit(sys.maxsize)

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
MODEL_ROOT = PROJECT_ROOT / "modeling"

T2_FINAL_PRED = (
    MODEL_ROOT / "T2" / "analysis" / "t2_final_test_predictions.csv"
)

T4_TOPK_PRED = (
    MODEL_ROOT / "T4" / "results" / "r1_checkpoints"
    / "t4_r1_topk_predictions.npz"
)

T5_LOCKED_PRED = (
    MODEL_ROOT / "T5" / "metrics"
    / "t5_mod009_locked_evaluation_predictions.npz"
)

T5_CALIBRATED_VAL_PRED = (
    MODEL_ROOT / "T5" / "metrics"
    / "t5_mod007_calibrated_validation_predictions.npz"
)

T7_EVAL_PRED = (
    MODEL_ROOT / "T7" / "derived"
    / "t7_mod010_evaluation_predictions.csv"
)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def file_info(path: Path):
    if not path.exists():
        return {
            "exists": False,
            "path": str(path),
        }

    stat = path.stat()

    return {
        "exists": True,
        "path": str(path),
        "size_bytes": stat.st_size,
    }


def classify_name(name):
    name_lower = name.lower()

    groups = []

    if any(x in name_lower for x in [
        "id", "ticket", "issue", "query", "candidate"
    ]):
        groups.append("KEY/ID-LIKE")

    if any(x in name_lower for x in [
        "pred", "prediction", "score", "rank",
        "survival", "prob"
    ]):
        groups.append("PREDICTION/SCORE-LIKE")

    if any(x in name_lower for x in [
        "target", "actual", "true", "label",
        "event", "duration"
    ]):
        groups.append("TARGET/OUTCOME-LIKE")

    if any(x in name_lower for x in [
        "split", "fold", "train", "test", "validation", "val"
    ]):
        groups.append("SPLIT/EVALUATION-LIKE")

    if any(x in name_lower for x in [
        "time", "date", "creation", "cutoff",
        "horizon", "timestamp"
    ]):
        groups.append("TEMPORAL-LIKE")

    return groups


def print_section(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def inspect_csv(path: Path):
    print_section(f"CSV ARTIFACT: {path}")

    info = file_info(path)
    print(f"exists: {info['exists']}")

    if not info["exists"]:
        return

    print(f"size_bytes: {info['size_bytes']}")

    columns = []
    row_count = 0

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:
        reader = csv.reader(f)

        try:
            columns = next(reader)
        except StopIteration:
            columns = []

        for _ in reader:
            row_count += 1

    print(f"column_count: {len(columns)}")
    print(f"row_count: {row_count}")

    print()
    print("columns:")

    for idx, col in enumerate(columns, start=1):
        tags = classify_name(col)
        tag_text = f" [{' | '.join(tags)}]" if tags else ""
        print(f"  {idx:02d}. {col}{tag_text}")

    # Small semantic summary
    print()
    print("semantic field groups:")

    for group in [
        "KEY/ID-LIKE",
        "PREDICTION/SCORE-LIKE",
        "TARGET/OUTCOME-LIKE",
        "SPLIT/EVALUATION-LIKE",
        "TEMPORAL-LIKE",
    ]:
        matches = [
            col for col in columns
            if group in classify_name(col)
        ]

        print(f"  {group}: {matches}")

    # Lightweight ID uniqueness inspection for obvious ID columns.
    id_columns = [
        col for col in columns
        if "id" in col.lower()
        or col.lower() in {"issue", "ticket", "query_id", "candidate_id"}
    ]

    if id_columns:
        print()
        print("ID-like columns detected:")
        for col in id_columns:
            print(f"  - {col}")

        # Only inspect the first obvious ID column to keep this audit focused.
        id_col = id_columns[0]

        unique_values = set()
        null_count = 0
        data_rows = 0

        with path.open(
            "r",
            encoding="utf-8",
            errors="replace",
            newline=""
        ) as f:
            reader = csv.DictReader(f)

            for row in reader:
                data_rows += 1
                value = row.get(id_col, "")

                if value == "":
                    null_count += 1
                else:
                    unique_values.add(value)

        print(f"uniqueness_check_column: {id_col}")
        print(f"unique_values: {len(unique_values)}")
        print(f"blank_values: {null_count}")
        print(f"rows_checked: {data_rows}")


def summarize_numeric_array(name, arr):
    print(f"  {name}")
    print(f"    shape: {arr.shape}")
    print(f"    dtype: {arr.dtype}")

    if arr.size == 0:
        print("    size: 0")
        return

    print(f"    size: {arr.size}")

    if np.issubdtype(arr.dtype, np.number):
        finite = np.isfinite(arr)

        if finite.any():
            vals = arr[finite]

            print(f"    finite_min: {vals.min()}")
            print(f"    finite_max: {vals.max()}")

            if vals.size <= 20:
                print(f"    unique_values: {np.unique(vals).tolist()}")

    elif arr.dtype.kind in {"U", "S", "O"}:
        flat = arr.reshape(-1)

        if flat.size <= 20:
            print(f"    values: {flat.tolist()}")


def inspect_npz(path: Path):
    print_section(f"NPZ ARTIFACT: {path}")

    info = file_info(path)
    print(f"exists: {info['exists']}")

    if not info["exists"]:
        return

    print(f"size_bytes: {info['size_bytes']}")

    try:
        with np.load(path, allow_pickle=False) as data:

            keys = list(data.files)

            print(f"array_count: {len(keys)}")
            print()
            print("arrays:")

            for key in keys:
                arr = data[key]
                summarize_numeric_array(key, arr)

            print()
            print("semantic array groups:")

            for group_name, keywords in {
                "KEY/ID-LIKE": [
                    "id", "ticket", "issue",
                    "query", "candidate"
                ],
                "PREDICTION/SCORE-LIKE": [
                    "pred", "prediction",
                    "prob", "score", "rank",
                    "survival"
                ],
                "TARGET/OUTCOME-LIKE": [
                    "target", "actual", "true",
                    "label", "event", "duration"
                ],
                "SPLIT/EVALUATION-LIKE": [
                    "split", "fold",
                    "train", "test", "val"
                ],
                "TEMPORAL-LIKE": [
                    "time", "date",
                    "creation", "cutoff",
                    "horizon"
                ],
            }.items():

                matches = []

                for key in keys:
                    lower = key.lower()

                    if any(keyword in lower for keyword in keywords):
                        matches.append(key)

                print(f"  {group_name}: {matches}")

    except Exception as exc:
        print(f"NPZ inspection ERROR: {type(exc).__name__}: {exc}")


def find_relevant_jsons(task_dir: Path):
    """
    Targeted metadata discovery only.
    We inspect JSON filenames associated with closure,
    model selection, locked evaluation, metrics, or result metadata.
    """

    if not task_dir.exists():
        return []

    patterns = [
        "*closure*.json",
        "*model*selection*.json",
        "*locked*evaluation*.json",
        "*evaluation*.json",
        "*final*.json",
        "*metrics*.json",
        "*comparison*.json",
    ]

    found = set()

    for pattern in patterns:
        for path in task_dir.rglob(pattern):
            if path.is_file():
                found.add(path)

    return sorted(found)


def inspect_json(path: Path):
    print_section(f"METADATA JSON: {path}")

    info = file_info(path)
    print(f"exists: {info['exists']}")

    if not info["exists"]:
        return

    print(f"size_bytes: {info['size_bytes']}")

    try:
        with path.open(
            "r",
            encoding="utf-8",
            errors="replace"
        ) as f:
            obj = json.load(f)

    except Exception as exc:
        print(f"JSON read ERROR: {type(exc).__name__}: {exc}")
        return

    print(f"top_level_type: {type(obj).__name__}")

    if isinstance(obj, dict):
        print(f"top_level_keys: {list(obj.keys())}")

        # Search recursively for metadata fields that can establish
        # artifact provenance without dumping the entire JSON.
        interesting_terms = [
            "prediction",
            "predictions",
            "artifact",
            "path",
            "file",
            "split",
            "test",
            "validation",
            "train",
            "cutoff",
            "horizon",
            "target",
            "metric",
            "evaluation",
            "model",
            "population",
        ]

        matches = []

        def walk(value, prefix=""):
            if isinstance(value, dict):
                for key, child in value.items():
                    key_path = f"{prefix}.{key}" if prefix else key
                    key_lower = key.lower()

                    if any(term in key_lower for term in interesting_terms):
                        if not isinstance(child, (dict, list)):
                            matches.append(
                                (key_path, child)
                            )

                    walk(child, key_path)

            elif isinstance(value, list):
                for i, child in enumerate(value):
                    walk(child, f"{prefix}[{i}]")

        walk(obj)

        print()
        print("relevant scalar metadata:")

        if not matches:
            print("  none identified")
        else:
            for key, value in matches[:150]:
                text = repr(value)

                if len(text) > 500:
                    text = text[:500] + "..."

                print(f"  {key} = {text}")

            if len(matches) > 150:
                print(
                    f"  ... {len(matches) - 150} additional "
                    "matches omitted"
                )

    elif isinstance(obj, list):
        print(f"top_level_length: {len(obj)}")


def inspect_task_metadata(task_name):
    task_dir = MODEL_ROOT / task_name

    print_section(f"{task_name} TARGETED METADATA DISCOVERY")

    if not task_dir.exists():
        print(f"task_directory_exists: FALSE")
        print(f"path: {task_dir}")
        return

    print(f"task_directory_exists: TRUE")
    print(f"path: {task_dir}")

    jsons = find_relevant_jsons(task_dir)

    print(f"candidate_metadata_json_count: {len(jsons)}")

    if not jsons:
        print("No relevant JSON metadata files discovered.")
        return

    for path in jsons:
        inspect_json(path)


# ------------------------------------------------------------
# Main audit
# ------------------------------------------------------------

def main():

    print("=" * 78)
    print("T8 MOD-006 — TARGETED PREDICTION-ARTIFACT CONTENT AUDIT")
    print("=" * 78)

    print()
    print("MODE: READ-ONLY")
    print("RAW MOZILLA ARCHIVE: NOT ACCESSED")
    print("MODEL LOADING: FALSE")
    print("TRAINING: FALSE")
    print("ARTIFACT MODIFICATION: FALSE")
    print()

    print("PROJECT ROOT:")
    print(PROJECT_ROOT)

    print()
    print("MODEL ROOT:")
    print(MODEL_ROOT)

    # --------------------------------------------------------
    # T2
    # --------------------------------------------------------

    inspect_csv(T2_FINAL_PRED)
    inspect_task_metadata("T2")

    # --------------------------------------------------------
    # T3
    # --------------------------------------------------------

    inspect_task_metadata("T3")

    # --------------------------------------------------------
    # T4
    # --------------------------------------------------------

    inspect_npz(T4_TOPK_PRED)
    inspect_task_metadata("T4")

    # --------------------------------------------------------
    # T5
    # --------------------------------------------------------

    inspect_npz(T5_LOCKED_PRED)
    inspect_npz(T5_CALIBRATED_VAL_PRED)
    inspect_task_metadata("T5")

    # --------------------------------------------------------
    # T7
    # --------------------------------------------------------

    inspect_csv(T7_EVAL_PRED)
    inspect_task_metadata("T7")

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    print_section("T8 MOD-006 AUDIT STATUS")

    print("Prediction artifacts inspected:")
    print("  T2 final test CSV")
    print("  T3 targeted metadata discovery")
    print("  T4 Top-K NPZ")
    print("  T5 locked evaluation NPZ")
    print("  T5 calibrated validation NPZ")
    print("  T7 evaluation CSV")

    print()
    print("This operation does NOT establish T8 eligibility,")
    print("common-population coverage, or fusion usability.")
    print("Those remain subsequent controlled decisions.")

    print()
    print("MOD-006 COMPLETE")


if __name__ == "__main__":
    main()