#!/usr/bin/env python3

import csv
import json
from pathlib import Path


# ============================================================
# T8 MOD-010
# Outcome / Evaluation-Target Feasibility Audit
#
# READ-ONLY
# No model loading
# No training
# No fusion
# No synthetic target creation
# No raw Mozilla archive access
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

LAYER_B = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T8_LAYER_B_T6_QUERY_EVIDENCE_derived.csv"
)

LAYER_C = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T8_LAYER_C_T6_QUERY_CANDIDATE_EVIDENCE_derived.csv"
)

TICKET_DS = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T8_TICKET_DECISION_SUPPORT_derived.csv"
)

T2_PRED = (
    MODELING_ROOT /
    "T2/analysis/t2_final_test_predictions.csv"
)

T3_TEST = (
    MODELING_ROOT /
    "T3/splits/t3_test.csv"
)

T4_EVAL = (
    MODELING_ROOT /
    "T4/derived/t4_eval.csv"
)

T5_EVAL = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T5_EVAL_GROUP_AWARE.csv"
)

T7_PRED = (
    MODELING_ROOT /
    "T7/derived/t7_mod010_evaluation_predictions.csv"
)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def print_header(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def read_header(path):
    if not path.exists():
        return None

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:

        reader = csv.reader(f)

        try:
            return next(reader)
        except StopIteration:
            return []


def read_rows_selected(path, selected_columns):
    rows = []

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        missing = [
            c for c in selected_columns
            if c not in reader.fieldnames
        ]

        if missing:
            raise RuntimeError(
                f"Missing columns in {path}: {missing}"
            )

        for row in reader:
            rows.append({
                c: row[c]
                for c in selected_columns
            })

    return rows


def load_json(path):
    if not path.exists():
        return None

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
    results = []

    if isinstance(obj, dict):

        for key, value in obj.items():

            current = (
                f"{prefix}.{key}"
                if prefix
                else str(key)
            )

            results.extend(
                flatten_strings(
                    value,
                    current
                )
            )

    elif isinstance(obj, list):

        for i, value in enumerate(obj):

            current = f"{prefix}[{i}]"

            results.extend(
                flatten_strings(
                    value,
                    current
                )
            )

    elif isinstance(obj, str):

        results.append(
            (prefix, obj)
        )

    return results


def print_relevant_json_fields(
    path,
    keywords
):

    data = load_json(path)

    if data is None:
        print(
            f"  Could not parse or open: {path}"
        )
        return

    strings = flatten_strings(data)

    for key, value in strings:

        low = value.lower()

        if any(
            keyword.lower() in low
            for keyword in keywords
        ):

            print(
                f"  {key}: {value}"
            )


# ============================================================
# 1. T8 schema-level target inventory
# ============================================================

print_header(
    "MOD-010 — T8 NATIVE TARGET / OUTCOME INVENTORY"
)

t8_files = {
    "Layer A": LAYER_A,
    "Layer B": LAYER_B,
    "Layer C": LAYER_C,
    "Ticket Decision Support": TICKET_DS,
}

for name, path in t8_files.items():

    header = read_header(path)

    print()
    print(name)
    print(f"Path: {path}")
    print(f"Exists: {path.exists()}")

    if header is None:
        continue

    print(f"Columns: {len(header)}")

    target_like = [
        column
        for column in header
        if any(
            token in column.lower()
            for token in (
                "target",
                "outcome",
                "event",
                "resolved",
                "duration",
                "score",
                "priority",
                "severity",
                "assignee",
                "duplicate",
            )
        )
    ]

    print(
        "Target/outcome-related columns:"
    )

    for column in target_like:
        print(f"  {column}")


# ============================================================
# 2. T8 synthetic-target field audit
# ============================================================

print_header(
    "MOD-010 — SYNTHETIC T8 TARGET / SCORE FIELD AUDIT"
)

for name, path in t8_files.items():

    header = read_header(path)

    if header is None:
        continue

    t8_fields = [
        column
        for column in header
        if column.lower() in {
            "t8_target",
            "t8_score",
            "triage_score",
            "confidence",
            "fusion_score",
        }
    ]

    print()
    print(name)

    if t8_fields:
        for field in t8_fields:
            print(f"  Present: {field}")
    else:
        print(
            "  No explicit synthetic T8 target/score field "
            "in schema."
        )


# ============================================================
# 3. Native task target inventory
# ============================================================

print_header(
    "MOD-010 — NATIVE TASK TARGET INVENTORY"
)

task_files = {
    "T2": T2_PRED,
    "T3": T3_TEST,
    "T4": T4_EVAL,
    "T5": T5_EVAL,
    "T7": T7_PRED,
}

for task, path in task_files.items():

    header = read_header(path)

    print()
    print(task)
    print(f"Path: {path}")
    print(f"Exists: {path.exists()}")

    if header is None:
        continue

    print(
        f"Columns ({len(header)}):"
    )

    for column in header:
        print(f"  {column}")


# ============================================================
# 4. Native target semantics from final closure metadata
# ============================================================

print_header(
    "MOD-010 — NATIVE TARGET SEMANTICS"
)

metadata_files = [
    MODELING_ROOT /
    "T2/analysis/t2_final_closure.json",

    MODELING_ROOT /
    "T3/analysis/t3_final_closure.json",

    MODELING_ROOT /
    "T4/results/t4_mod013_closure.json",

    MODELING_ROOT /
    "T5/metrics/t5_mod011_final_closure.json",

    MODELING_ROOT /
    "T7/metrics/t7_mod012_final_closure.json",
]

keywords = [
    "target",
    "outcome",
    "prediction boundary",
    "prediction_boundary",
    "evaluation",
    "task",
    "role",
    "signal",
    "survival",
    "duplicate",
    "priority",
    "severity",
    "assignee",
]

for path in metadata_files:

    print()
    print(f"FILE: {path}")

    if not path.exists():
        print("  MISSING")
        continue

    print_relevant_json_fields(
        path,
        keywords
    )


# ============================================================
# 5. T2 target / prediction alignment
# ============================================================

print_header(
    "MOD-010 — T2 NATIVE TARGET ALIGNMENT"
)

if T2_PRED.exists():

    rows = read_rows_selected(
        T2_PRED,
        [
            "ID",
            "Creation time",
            "actual_priority",
            "predicted_priority",
        ]
    )

    print(
        f"T2 prediction rows: {len(rows)}"
    )

    actual_values = {
        row["actual_priority"]
        for row in rows
        if row["actual_priority"].strip()
    }

    predicted_values = {
        row["predicted_priority"]
        for row in rows
        if row["predicted_priority"].strip()
    }

    print(
        f"Observed native actual_priority values: "
        f"{sorted(actual_values)}"
    )

    print(
        f"Observed native predicted_priority values: "
        f"{sorted(predicted_values)}"
    )

    print(
        "Interpretation: T2 has a native task-specific "
        "five-class priority outcome."
    )


# ============================================================
# 6. T3 native target
# ============================================================

print_header(
    "MOD-010 — T3 NATIVE TARGET ALIGNMENT"
)

if T3_TEST.exists():

    header = read_header(T3_TEST)

    print(
        f"T3 locked-test rows file exists: "
        f"{len(header) if header else 0} columns"
    )

    print("Columns:")

    for column in header:
        print(f"  {column}")

    target_columns = [
        c
        for c in header
        if "target" in c.lower()
        or "severity" in c.lower()
    ]

    print(
        f"Target/severity-related columns: "
        f"{target_columns}"
    )

    print(
        "Interpretation: T3 retains a native severity "
        "prediction target, but its prediction artifact is "
        "not currently ID-addressable for T8."
    )


# ============================================================
# 7. T4 native target
# ============================================================

print_header(
    "MOD-010 — T4 NATIVE TARGET ALIGNMENT"
)

if T4_EVAL.exists():

    header = read_header(T4_EVAL)

    print(
        f"T4 evaluation columns: {len(header)}"
    )

    target_columns = [
        c
        for c in header
        if "target" in c.lower()
        or "assignee" in c.lower()
    ]

    print(
        "Target/assignee-related columns:"
    )

    for column in target_columns:
        print(f"  {column}")

    print(
        "Interpretation: T4 has a native assignee target "
        "at evaluation time. Its prediction output remains "
        "ranking/retrieval evidence."
    )


# ============================================================
# 8. T5 native target
# ============================================================

print_header(
    "MOD-010 — T5 NATIVE TARGET ALIGNMENT"
)

if T5_EVAL.exists():

    header = read_header(T5_EVAL)

    print(
        f"T5 evaluation columns: {len(header)}"
    )

    target_columns = [
        c
        for c in header
        if "target" in c.lower()
        or "duplicate" in c.lower()
    ]

    print(
        "Target/duplicate-related columns:"
    )

    for column in target_columns:
        print(f"  {column}")

    print(
        "Interpretation: T5 has a native binary duplicate "
        "outcome. Its probability output is task-specific."
    )


# ============================================================
# 9. T7 native outcome
# ============================================================

print_header(
    "MOD-010 — T7 NATIVE OUTCOME ALIGNMENT"
)

if T7_PRED.exists():

    header = read_header(T7_PRED)

    print(
        f"T7 prediction columns: {len(header)}"
    )

    for column in header:
        print(f"  {column}")

    print(
        "Interpretation: T7 retains survival-native "
        "duration/event semantics and must not be reduced "
        "to an ordinary classification/regression target."
    )


# ============================================================
# 10. Common target search across T8 artifacts
# ============================================================

print_header(
    "MOD-010 — COMMON EVALUATION TARGET SEARCH"
)

all_headers = {}

for name, path in t8_files.items():

    header = read_header(path)

    if header is not None:
        all_headers[name] = set(
            column.lower()
            for column in header
        )

if all_headers:

    common_columns = set.intersection(
        *all_headers.values()
    )

    print(
        "Columns common to all four T8 evidence layers:"
    )

    for column in sorted(common_columns):
        print(f"  {column}")

    print()

    target_like_common = [
        column
        for column in common_columns
        if any(
            token in column
            for token in (
                "target",
                "outcome",
                "score",
                "priority",
                "severity",
                "assignee",
                "duplicate",
                "resolved",
                "duration",
            )
        )
    ]

    print(
        "Common target/outcome-like columns:"
    )

    for column in target_like_common:
        print(f"  {column}")

    if not target_like_common:
        print(
            "  NONE"
        )


# ============================================================
# 11. Evaluation-design feasibility matrix
# ============================================================

print_header(
    "MOD-010 — EVALUATION DESIGN FEASIBILITY"
)

designs = [
    (
        "Universal ticket-level triage accuracy",
        "NOT ESTABLISHED",
        "No validated universal T8 target is defined."
    ),
    (
        "Universal fused probability / triage score",
        "NOT ESTABLISHED",
        "No validated common target or score semantics."
    ),
    (
        "Task-specific T2 evaluation",
        "AVAILABLE",
        "Native priority target exists."
    ),
    (
        "Task-specific T3 evaluation",
        "AVAILABLE WITH LIMITATION",
        "Native severity target exists, but preserved "
        "prediction output is not ID-addressable."
    ),
    (
        "Task-specific T4 evaluation",
        "AVAILABLE",
        "Native assignee target and ranking evidence exist."
    ),
    (
        "Task-specific T5 evaluation",
        "AVAILABLE",
        "Native duplicate target and probability evidence exist."
    ),
    (
        "Task-specific T7 evaluation",
        "AVAILABLE",
        "Native survival outcome and survival predictions exist."
    ),
    (
        "Cross-task evidence analysis without universal target",
        "POTENTIALLY AVAILABLE",
        "Requires an explicitly defined evaluation question "
        "that preserves native task semantics."
    ),
]

for name, status, reason in designs:

    print()
    print(f"{name}")
    print(f"  Status: {status}")
    print(f"  Basis: {reason}")


# ============================================================
# 12. Prohibited constructions check
# ============================================================

print_header(
    "MOD-010 — PROHIBITED CONSTRUCTION CHECK"
)

prohibited = [
    "Synthetic universal triage label",
    "Weighted average of unrelated task probabilities",
    "Majority vote across heterogeneous task outputs",
    "Treating T4 ranking scores as probabilities",
    "Treating T7 survival outputs as ordinary regression",
    "Treating missing evidence as a negative",
    "Using post-Creation outcomes as Creation-time features",
    "Inventing a universal confidence score",
]

for item in prohibited:
    print(
        f"  PRESERVE PROHIBITION: {item}"
    )


# ============================================================
# 13. Final status
# ============================================================

print_header(
    "MOD-010 — FINAL STATUS"
)

print(
    "No universal T8 evaluation target was created."
)

print(
    "Native task targets/outcomes remain task-specific."
)

print(
    "No cross-task prediction values were transformed."
)

print(
    "No fusion model or fused score was created."
)

print(
    "No model was loaded."
)

print(
    "No training performed."
)

print(
    "No raw Mozilla archive accessed."
)

print(
    "No existing artifact modified."
)

print()
print(
    "MOD-010 COMPLETE"
)