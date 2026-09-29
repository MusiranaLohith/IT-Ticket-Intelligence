#!/usr/bin/env python3

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

csv.field_size_limit(1024 * 1024 * 1024)

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_ROOT = PROJECT_ROOT / "modeling/T2"
T7_ROOT = PROJECT_ROOT / "modeling/T7"

T2_TRAIN = T2_ROOT / "splits/train.csv"
T2_VALIDATION = T2_ROOT / "splits/validation.csv"
T2_TEST = T2_ROOT / "splits/test.csv"

T7_TRAIN = T7_ROOT / "splits/t7_train.csv"
T7_EVAL = T7_ROOT / "splits/t7_evaluation.csv"

T2_CLOSURE = T2_ROOT / "analysis/t2_final_closure.json"
T2_SELECTION = T2_ROOT / "analysis/t2_final_model_selection.json"
T2_CONTRACT = T2_ROOT / "contracts/t2_model_contract.json"
T2_SPLIT_REPORT = T2_ROOT / "splits/t2_split_report.json"

T7_CLOSURE_CANDIDATES = [
    T7_ROOT / "analysis/t7_mod012_closure.json",
    T7_ROOT / "analysis/t7_final_closure.json",
    T7_ROOT / "analysis/t7_mod011_final_comparison.json",
]

T7_MODEL_CANDIDATES = [
    T7_ROOT / "analysis/t7_mod011_final_comparison.json",
    T7_ROOT / "analysis/t7_mod010_closure.json",
    T7_ROOT / "analysis/t7_mod007_closure.json",
]

T7_CONTRACT_CANDIDATES = [
    T7_ROOT / "contracts/t7_model_contract.json",
    T7_ROOT / "contracts/t7_contract.json",
]

T7_SPLIT_CANDIDATES = [
    T7_ROOT / "analysis/t7_mod005_split_report.json",
    T7_ROOT / "splits/t7_split_report.json",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_csv(path):
    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:
        return list(csv.DictReader(f))


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
    except Exception as exc:
        return {
            "__load_error__": str(exc)
        }


def parse_creation(value):
    value = value.strip()

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
    ]

    parsed = None

    for fmt in formats:
        try:
            parsed = datetime.strptime(
                value,
                fmt
            )
            break
        except ValueError:
            pass

    if parsed is None:
        try:
            parsed = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise RuntimeError(
                f"Unable to parse Creation time: {value}"
            ) from exc

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=timezone.utc
        )
    else:
        parsed = parsed.astimezone(
            timezone.utc
        )

    return parsed


def get_id(row):
    return str(
        row.get("ID", "")
    ).strip()


def chronological_records(rows):
    records = []

    for row in rows:

        ticket_id = get_id(row)

        if not ticket_id:
            continue

        records.append(
            {
                "ID": ticket_id,
                "Creation time": parse_creation(
                    row["Creation time"]
                ),
                "row": row,
            }
        )

    records.sort(
        key=lambda x: (
            x["Creation time"],
            x["ID"]
        )
    )

    return records


def print_header(title):
    print("\n" + "=" * 96)
    print(title)
    print("=" * 96)


def print_json_value(label, value, indent=2):
    print(f"\n{label}:")

    if value is None:
        print("  NOT FOUND")
        return

    if isinstance(value, dict):
        print(
            json.dumps(
                value,
                indent=indent,
                ensure_ascii=False
            )
        )

    elif isinstance(value, list):
        print(
            json.dumps(
                value,
                indent=indent,
                ensure_ascii=False
            )
        )

    else:
        print(f"  {value}")


def find_first_existing(paths):
    for path in paths:
        if path.exists():
            return path

    return None


def recursive_find_keys(obj, wanted, prefix=""):
    found = {}

    if isinstance(obj, dict):

        for key, value in obj.items():

            path = (
                f"{prefix}.{key}"
                if prefix
                else key
            )

            if key in wanted:
                found[path] = value

            found.update(
                recursive_find_keys(
                    value,
                    wanted,
                    path
                )
            )

    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            path = f"{prefix}[{index}]"

            found.update(
                recursive_find_keys(
                    value,
                    wanted,
                    path
                )
            )

    return found


def search_text(path, terms):
    try:
        text = path.read_text(
            encoding="utf-8",
            errors="replace"
        )
    except Exception:
        return {}

    lower = text.lower()

    result = {}

    for term in terms:

        if term.lower() in lower:
            result[term] = True

    return result


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

print("=" * 96)
print(
    "MOD-024 — T2/T7 OoF FOLD-DESIGN AND "
    "FROZEN-MODEL CONTRACT AUDIT"
)
print("=" * 96)

print(
    "Purpose: freeze a defensible chronological OoF design and "
    "identify the exact already-validated T2/T7 modeling contracts "
    "that must be reproduced during controlled development prediction."
)

print(
    "\nNo model loading."
    "\nNo model fitting."
    "\nNo prediction generation."
    "\nNo artifact modification."
)


# ---------------------------------------------------------------------------
# Load populations
# ---------------------------------------------------------------------------

print_header(
    "MOD-024 — LOAD FROZEN T2/T7 POPULATIONS"
)

t2_train = chronological_records(
    load_csv(T2_TRAIN)
)

t2_validation = chronological_records(
    load_csv(T2_VALIDATION)
)

t2_test = chronological_records(
    load_csv(T2_TEST)
)

t7_train = chronological_records(
    load_csv(T7_TRAIN)
)

t7_eval = chronological_records(
    load_csv(T7_EVAL)
)

t2_train_ids = {
    x["ID"] for x in t2_train
}

t2_validation_ids = {
    x["ID"] for x in t2_validation
}

t2_test_ids = {
    x["ID"] for x in t2_test
}

t7_train_ids = {
    x["ID"] for x in t7_train
}

t7_eval_ids = {
    x["ID"] for x in t7_eval
}

common_ids = (
    t2_train_ids
    &
    t7_train_ids
)

common = [
    x
    for x in t2_train
    if x["ID"] in common_ids
]

common.sort(
    key=lambda x: (
        x["Creation time"],
        x["ID"]
    )
)

print(
    f"T2 train: {len(t2_train):,}"
)

print(
    f"T2 validation: {len(t2_validation):,}"
)

print(
    f"T2 test: {len(t2_test):,}"
)

print(
    f"T7 train: {len(t7_train):,}"
)

print(
    f"T7 evaluation: {len(t7_eval):,}"
)

print(
    f"Common T2-train ∩ T7-train: "
    f"{len(common):,}"
)


# ---------------------------------------------------------------------------
# Existing split boundaries
# ---------------------------------------------------------------------------

print_header(
    "MOD-024 — EXISTING TASK TEMPORAL BOUNDARIES"
)

for label, rows in [
    ("T2 train", t2_train),
    ("T2 validation", t2_validation),
    ("T2 test", t2_test),
    ("T7 train", t7_train),
    ("T7 evaluation", t7_eval),
]:

    print(
        f"\n{label}:"
    )

    print(
        f"  earliest = {rows[0]['Creation time']}"
    )

    print(
        f"  latest   = {rows[-1]['Creation time']}"
    )

    print(
        f"  rows     = {len(rows):,}"
    )


# ---------------------------------------------------------------------------
# Candidate fold structures
# ---------------------------------------------------------------------------

print_header(
    "MOD-024 — CHRONOLOGICAL FOLD-DESIGN COMPARISON"
)

candidate_results = {}

for block_count in [3, 4, 5]:

    n = len(common)

    base = n // block_count
    remainder = n % block_count

    blocks = []

    start = 0

    for i in range(block_count):

        size = base + (
            1
            if i < remainder
            else 0
        )

        end = start + size

        blocks.append(
            common[start:end]
        )

        start = end

    usable_blocks = []

    print(
        f"\n{block_count}-block candidate:"
    )

    for block_index, block in enumerate(
        blocks,
        start=1
    ):

        first = block[0]

        boundary = (
            first["Creation time"],
            first["ID"]
        )

        t2_history = [
            row
            for row in t2_train
            if (
                row["Creation time"],
                row["ID"]
            )
            <
            boundary
        ]

        t7_history = [
            row
            for row in t7_train
            if (
                row["Creation time"],
                row["ID"]
            )
            <
            boundary
        ]

        t2_targets = {
            str(
                row["row"].get(
                    "target_priority",
                    ""
                )
            ).strip()
            for row in t2_history
        }

        required = {
            "P1",
            "P2",
            "P3",
            "P4",
            "P5",
        }

        missing = sorted(
            required - t2_targets
        )

        usable = (
            len(t2_history) > 0
            and
            len(t7_history) > 0
            and
            not missing
        )

        if usable:
            usable_blocks.append(
                block_index
            )

        print(
            f"  Block {block_index}: "
            f"prediction={len(block):,} | "
            f"T2 history={len(t2_history):,} | "
            f"T7 history={len(t7_history):,} | "
            f"missing T2 classes="
            f"{missing if missing else 'NONE'} | "
            f"joint-usable="
            f"{'YES' if usable else 'NO'}"
        )

    candidate_results[block_count] = {
        "blocks": blocks,
        "usable_blocks": usable_blocks,
    }

    print(
        f"  Usable chronological blocks: "
        f"{usable_blocks}"
    )


# ---------------------------------------------------------------------------
# Earliest usable boundary for each design
# ---------------------------------------------------------------------------

print_header(
    "MOD-024 — EARLIEST JOINT-USABLE BOUNDARY"
)

for block_count, result in candidate_results.items():

    usable = result["usable_blocks"]

    if not usable:

        print(
            f"{block_count}-block: "
            f"NO JOINT-USABLE BLOCK"
        )

        continue

    first_block_number = usable[0]

    block = result["blocks"][
        first_block_number - 1
    ]

    first = block[0]

    boundary = (
        first["Creation time"],
        first["ID"]
    )

    t2_history = [
        row
        for row in t2_train
        if (
            row["Creation time"],
            row["ID"]
        )
        <
        boundary
    ]

    t7_history = [
        row
        for row in t7_train
        if (
            row["Creation time"],
            row["ID"]
        )
        <
        boundary
    ]

    print(
        f"\n{block_count}-block:"
    )

    print(
        f"  First usable block: "
        f"{first_block_number}"
    )

    print(
        f"  First prediction: "
        f"{first['Creation time']} "
        f"ID={first['ID']}"
    )

    print(
        f"  T2 fitting history: "
        f"{len(t2_history):,}"
    )

    print(
        f"  T7 fitting history: "
        f"{len(t7_history):,}"
    )


# ---------------------------------------------------------------------------
# Inspect authoritative T2 metadata
# ---------------------------------------------------------------------------

print_header(
    "MOD-024 — T2 AUTHORITATIVE MODEL CONTRACT"
)

t2_closure = load_json(T2_CLOSURE)
t2_selection = load_json(T2_SELECTION)
t2_contract = load_json(T2_CONTRACT)
t2_split = load_json(T2_SPLIT_REPORT)

for label, data in [
    ("T2 final closure", t2_closure),
    ("T2 final model selection", t2_selection),
    ("T2 model contract", t2_contract),
    ("T2 split report", t2_split),
]:

    print(
        f"\n--- {label} ---"
    )

    if data is None:

        print(
            "NOT FOUND"
        )

        continue

    wanted = {
        "task",
        "task_name",
        "prediction_boundary",
        "selected_model",
        "final_model",
        "selection_basis",
        "selection_reasons",
        "admitted_features",
        "excluded_features",
        "missingness_policy",
        "leakage_controls",
        "modeling_policy",
        "target",
        "objective",
        "system_role",
        "closure_status",
        "final_model_status",
        "split_method",
        "shuffle",
        "stratification",
        "ordering",
        "temporal_boundaries",
        "fractions",
        "sizes",
        "class_counts",
    }

    found = recursive_find_keys(
        data,
        wanted
    )

    for path, value in found.items():

        print(
            f"\n{path}:"
        )

        print(
            json.dumps(
                value,
                indent=2,
                ensure_ascii=False
            )
        )


# ---------------------------------------------------------------------------
# Inspect authoritative T7 metadata
# ---------------------------------------------------------------------------

print_header(
    "MOD-024 — T7 AUTHORITATIVE MODEL CONTRACT DISCOVERY"
)

t7_closure_path = find_first_existing(
    T7_CLOSURE_CANDIDATES
)

t7_model_path = find_first_existing(
    T7_MODEL_CANDIDATES
)

t7_contract_path = find_first_existing(
    T7_CONTRACT_CANDIDATES
)

t7_split_path = find_first_existing(
    T7_SPLIT_CANDIDATES
)

for label, path in [
    ("T7 closure candidate", t7_closure_path),
    ("T7 model-selection/comparison candidate", t7_model_path),
    ("T7 contract candidate", t7_contract_path),
    ("T7 split candidate", t7_split_path),
]:

    print(
        f"{label}: "
        f"{path.relative_to(PROJECT_ROOT) if path else 'NOT FOUND'}"
    )


for label, path in [
    ("T7 closure", t7_closure_path),
    ("T7 model comparison", t7_model_path),
    ("T7 contract", t7_contract_path),
    ("T7 split", t7_split_path),
]:

    print(
        f"\n--- {label} ---"
    )

    if path is None:

        print(
            "NOT FOUND"
        )

        continue

    data = load_json(path)

    if data is None:

        print(
            "Could not load JSON"
        )

        continue

    wanted = {
        "task",
        "task_name",
        "prediction_boundary",
        "selected_model",
        "final_model",
        "selection_basis",
        "selection_reasons",
        "admitted_features",
        "excluded_features",
        "missingness_policy",
        "leakage_controls",
        "modeling_policy",
        "target",
        "objective",
        "system_role",
        "closure_status",
        "final_model_status",
        "split_method",
        "shuffle",
        "stratification",
        "ordering",
        "temporal_boundaries",
        "fractions",
        "sizes",
        "class_counts",
        "event",
        "censoring",
        "observation_endpoint",
    }

    found = recursive_find_keys(
        data,
        wanted
    )

    for key_path, value in found.items():

        print(
            f"\n{key_path}:"
        )

        print(
            json.dumps(
                value,
                indent=2,
                ensure_ascii=False
            )
        )


# ---------------------------------------------------------------------------
# T2 implementation inspection
# ---------------------------------------------------------------------------

print_header(
    "MOD-024 — T2 IMPLEMENTATION DETAILS"
)

t2_scripts = [
    T2_ROOT / "scripts/t2_baseline.py",
    T2_ROOT / "scripts/t2_class_weighted.py",
    T2_ROOT / "scripts/t2_final_model_selection.py",
    T2_ROOT / "scripts/t2_final_test_evaluation.py",
]

t2_terms = [
    "TfidfVectorizer",
    "LogisticRegression",
    "class_weight",
    "max_features",
    "ngram_range",
    "min_df",
    "max_df",
    "sublinear_tf",
    "analyzer",
    "strip_accents",
    "lowercase",
    "token_pattern",
    "predict_proba",
    "decision_function",
]

for path in t2_scripts:

    print(
        f"\n--- {path.relative_to(PROJECT_ROOT)} ---"
    )

    if not path.exists():

        print(
            "NOT FOUND"
        )

        continue

    hits = search_text(
        path,
        t2_terms
    )

    for term in hits:

        print(
            f"  contains: {term}"
        )


# ---------------------------------------------------------------------------
# T7 implementation inspection
# ---------------------------------------------------------------------------

print_header(
    "MOD-024 — T7 IMPLEMENTATION DETAILS"
)

t7_scripts = [
    T7_ROOT / "scripts/t7_mod007_weibull_aft.py",
    T7_ROOT / "scripts/t7_mod010_log_normal_aft.py",
    T7_ROOT / "scripts/t7_mod011_model_comparison.py",
    T7_ROOT / "scripts/t7_mod012_closure.py",
]

t7_terms = [
    "Weibull",
    "LogNormal",
    "Log-Normal",
    "duration_seconds",
    "event",
    "Creation time",
    "creation_year_scaled",
    "creation_month_sin",
    "creation_month_cos",
    "weekday_sin",
    "weekday_cos",
    "hour_sin",
    "hour_cos",
    "predicted_median_survival_seconds",
    "survival_probability_at_211583_seconds",
    "survival_probability_at_1780179_seconds",
    "survival_probability_at_14608619_seconds",
]

for path in t7_scripts:

    print(
        f"\n--- {path.relative_to(PROJECT_ROOT)} ---"
    )

    if not path.exists():

        print(
            "NOT FOUND"
        )

        continue

    hits = search_text(
        path,
        t7_terms
    )

    for term in hits:

        print(
            f"  contains: {term}"
        )


# ---------------------------------------------------------------------------
# Prediction representation
# ---------------------------------------------------------------------------

print_header(
    "MOD-024 — NATIVE DEVELOPMENT-PREDICTION REPRESENTATION"
)

print(
    """
T2:
  Preserve the native T2 predictive representation established
  by its frozen final model contract.

  Candidate outputs for development use must not be invented
  independently of that contract.

T7:
  Preserve survival-native predictive outputs.

  In particular, do not convert survival predictions into an
  ordinary regression target or arbitrary universal score.

T7 censoring remains part of the native task semantics.

The eventual fusion layer must receive prediction evidence,
not task outcomes or post-Creation information.
"""
)


# ---------------------------------------------------------------------------
# Required generation controls
# ---------------------------------------------------------------------------

print_header(
    "MOD-024 — REQUIRED CONTROLS FOR EVENTUAL OoF GENERATION"
)

controls = [
    "Only frozen T2 training population may be used for T2 fitting.",
    "Only frozen T7 training population may be used for T7 fitting.",
    "T2 validation and test remain excluded from OoF fitting.",
    "T7 locked evaluation remains excluded from OoF fitting.",
    "Prediction rows are chronologically later than fitting rows.",
    "Creation time is the prediction boundary.",
    "ID is deterministic tie-breaker for equal Creation timestamps.",
    "No prediction ticket may appear in its own fitting population.",
    "No post-Creation features may enter either model.",
    "T2 target_priority remains the native T2 target.",
    "T7 event/censoring remains native survival semantics.",
    "No synthetic T8 target is created.",
    "No fusion model is trained during OoF generation.",
    "Generated prediction artifacts must preserve ticket IDs.",
    "Every generated prediction must retain fold/provenance metadata.",
]

for index, control in enumerate(
    controls,
    start=1
):

    print(
        f"{index:02d}. {control}"
    )


# ---------------------------------------------------------------------------
# Design recommendation
# ---------------------------------------------------------------------------

print_header(
    "MOD-024 — PRELIMINARY DESIGN RECOMMENDATION"
)

print(
    """
The five-block chronological candidate provides a clear structure:

  Block 1:
    cannot provide joint T2/T7 OoF because T2 has zero prior
    training observations.

  Block 2:
    4,130 earlier T2 observations and 79,830 earlier T7
    observations.

  Block 3:
    8,260 earlier T2 observations and 278,087 earlier T7
    observations.

  Block 4:
    12,390 earlier T2 observations and 319,685 earlier T7
    observations.

  Block 5:
    16,519 earlier T2 observations and 352,229 earlier T7
    observations.

Block 2 is therefore the first substantial joint chronological
candidate under the five-block design.

However, the final fold count should be frozen only after the
authoritative T2/T7 contract details above have been inspected.
"""
)


# ---------------------------------------------------------------------------
# Integrity checks
# ---------------------------------------------------------------------------

print_header(
    "MOD-024 — INTEGRITY CHECKS"
)

checks = [
    (
        "Common population = 20,648",
        len(common) == 20_648
    ),
    (
        "Common IDs unique",
        len({
            x["ID"] for x in common
        }) == len(common)
    ),
    (
        "T2 train/test disjoint",
        not (
            t2_train_ids
            &
            t2_test_ids
        )
    ),
    (
        "T2 train/validation disjoint",
        not (
            t2_train_ids
            &
            t2_validation_ids
        )
    ),
    (
        "T2 validation/test disjoint",
        not (
            t2_validation_ids
            &
            t2_test_ids
        )
    ),
    (
        "T7 train/evaluation disjoint",
        not (
            t7_train_ids
            &
            t7_eval_ids
        )
    ),
    (
        "Common population has no T7 evaluation overlap",
        not (
            common_ids
            &
            t7_eval_ids
        )
    ),
    (
        "Common population has no T2 validation overlap",
        not (
            common_ids
            &
            t2_validation_ids
        )
    ),
    (
        "Common population has no T2 test overlap",
        not (
            common_ids
            &
            t2_test_ids
        )
    ),
]

for label, passed in checks:

    print(
        f"  {label}: "
        f"{'PASS' if passed else 'FAIL'}"
    )


print("\nNo model loaded.")
print("No model trained.")
print("No prediction generated.")
print("No artifact modified.")

print(
    "\nMOD-024 T2/T7 OoF FOLD-DESIGN AND "
    "FROZEN-MODEL CONTRACT AUDIT COMPLETE"
)

print(
    "STATUS: COMPLETE / REVIEW REQUIRED"
)