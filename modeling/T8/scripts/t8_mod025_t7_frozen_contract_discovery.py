#!/usr/bin/env python3

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T7_ROOT = PROJECT_ROOT / "modeling/T7"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path):
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


def print_header(title):
    print("\n" + "=" * 96)
    print(title)
    print("=" * 96)


def relative(path):
    try:
        return path.relative_to(PROJECT_ROOT)
    except ValueError:
        return path


def recursive_find_keys(obj, wanted, prefix=""):
    found = {}

    if isinstance(obj, dict):

        for key, value in obj.items():

            current = (
                f"{prefix}.{key}"
                if prefix
                else key
            )

            if key in wanted:
                found[current] = value

            found.update(
                recursive_find_keys(
                    value,
                    wanted,
                    current
                )
            )

    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            current = f"{prefix}[{index}]"

            found.update(
                recursive_find_keys(
                    value,
                    wanted,
                    current
                )
            )

    return found


def text_contains_any(text, terms):
    lower = text.lower()
    return [
        term
        for term in terms
        if term.lower() in lower
    ]


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

print("=" * 96)
print(
    "MOD-025 — T7 FROZEN CONTRACT AND "
    "IMPLEMENTATION ARTIFACT DISCOVERY"
)
print("=" * 96)

print(
    "Purpose: locate the authoritative T7 closure, model-selection, "
    "contract, split, implementation, and prediction-generation artifacts."
)

print(
    "\nREAD-ONLY DISCOVERY ONLY."
    "\nNo model loading."
    "\nNo model fitting."
    "\nNo prediction generation."
    "\nNo artifact modification."
)


# ---------------------------------------------------------------------------
# Verify T7 root
# ---------------------------------------------------------------------------

print_header(
    "MOD-025 — T7 ROOT"
)

print(
    f"T7 root: {T7_ROOT}"
)

print(
    f"Exists: {T7_ROOT.exists()}"
)

if not T7_ROOT.exists():
    raise SystemExit(
        "T7 modeling root does not exist."
    )


# ---------------------------------------------------------------------------
# Full filesystem inventory
# ---------------------------------------------------------------------------

print_header(
    "MOD-025 — T7 FILESYSTEM INVENTORY"
)

all_files = sorted(
    [
        p
        for p in T7_ROOT.rglob("*")
        if p.is_file()
    ]
)

print(
    f"Total files under T7: {len(all_files):,}"
)

for path in all_files:

    print(
        relative(path)
    )


# ---------------------------------------------------------------------------
# Candidate contract / closure / selection / split artifacts
# ---------------------------------------------------------------------------

print_header(
    "MOD-025 — CANDIDATE GOVERNANCE / CONTRACT ARTIFACTS"
)

governance_terms = [
    "closure",
    "contract",
    "selection",
    "comparison",
    "split",
    "model",
    "final",
    "report",
]

governance_candidates = []

for path in all_files:

    name = path.name.lower()

    if (
        path.suffix.lower() in {
            ".json",
            ".yaml",
            ".yml",
            ".txt",
            ".md"
        }
        and
        any(
            term in name
            for term in governance_terms
        )
    ):

        governance_candidates.append(
            path
        )

print(
    f"Governance-like candidates: "
    f"{len(governance_candidates):,}"
)

for path in governance_candidates:

    print(
        f"  {relative(path)}"
    )


# ---------------------------------------------------------------------------
# Candidate implementation scripts
# ---------------------------------------------------------------------------

print_header(
    "MOD-025 — T7 IMPLEMENTATION SCRIPT DISCOVERY"
)

script_candidates = [
    path
    for path in all_files
    if path.suffix.lower() == ".py"
]

print(
    f"Python scripts: {len(script_candidates):,}"
)

for path in script_candidates:

    print(
        f"  {relative(path)}"
    )


# ---------------------------------------------------------------------------
# Search implementation scripts by semantic markers
# ---------------------------------------------------------------------------

print_header(
    "MOD-025 — T7 IMPLEMENTATION SEMANTIC SEARCH"
)

implementation_terms = [
    "WeibullAFTFitter",
    "LogNormalAFTFitter",
    "Log-Normal",
    "Weibull",
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
    "predict_median",
    "predict_survival_function",
    "survival_probability_at_211583_seconds",
    "survival_probability_at_1780179_seconds",
    "survival_probability_at_14608619_seconds",
    "TRAIN_PATH",
    "EVAL_PATH",
    "t7_train",
    "t7_evaluation",
]

for path in script_candidates:

    try:
        text = path.read_text(
            encoding="utf-8",
            errors="replace"
        )
    except Exception:
        continue

    hits = text_contains_any(
        text,
        implementation_terms
    )

    if hits:

        print(
            f"\n{relative(path)}"
        )

        for hit in hits:

            print(
                f"  contains: {hit}"
            )


# ---------------------------------------------------------------------------
# Search every JSON for authoritative semantic keys
# ---------------------------------------------------------------------------

print_header(
    "MOD-025 — JSON SEMANTIC DISCOVERY"
)

json_files = [
    path
    for path in all_files
    if path.suffix.lower() == ".json"
]

print(
    f"JSON files: {len(json_files):,}"
)

wanted_keys = {
    "task",
    "task_name",
    "objective",
    "target",
    "prediction_boundary",
    "admitted_features",
    "excluded_features",
    "missingness_policy",
    "leakage_controls",
    "modeling_policy",
    "selected_model",
    "final_model",
    "selection_basis",
    "selection_reasons",
    "closure_status",
    "final_model_status",
    "split_method",
    "shuffle",
    "ordering",
    "temporal_boundaries",
    "sizes",
    "fractions",
    "event",
    "censoring",
    "observation_endpoint",
    "evaluation",
    "training",
}

json_semantic_hits = []

for path in json_files:

    data = load_json(path)

    if not isinstance(data, (dict, list)):
        continue

    found = recursive_find_keys(
        data,
        wanted_keys
    )

    if found:

        json_semantic_hits.append(
            (
                path,
                found
            )
        )


print(
    f"JSON files containing relevant semantic keys: "
    f"{len(json_semantic_hits):,}"
)

for path, found in json_semantic_hits:

    print(
        f"\n--- {relative(path)} ---"
    )

    print(
        f"Relevant key paths: {len(found):,}"
    )

    for key_path in sorted(found):

        print(
            f"  {key_path}"
        )


# ---------------------------------------------------------------------------
# Identify strongest closure / selection / contract candidates
# ---------------------------------------------------------------------------

print_header(
    "MOD-025 — GOVERNANCE CANDIDATE SCORING"
)

candidate_scores = []

semantic_name_terms = {
    "closure": 5,
    "contract": 5,
    "selection": 4,
    "comparison": 4,
    "split": 3,
    "final": 3,
    "model": 2,
}

for path, found in json_semantic_hits:

    name = path.name.lower()

    score = 0

    for term, weight in semantic_name_terms.items():

        if term in name:
            score += weight

    key_names = {
        key_path.split(".")[-1]
        for key_path in found
    }

    if "closure_status" in key_names:
        score += 5

    if "selected_model" in key_names:
        score += 5

    if "prediction_boundary" in key_names:
        score += 4

    if "target" in key_names:
        score += 4

    if "admitted_features" in key_names:
        score += 4

    if "split_method" in key_names:
        score += 3

    candidate_scores.append(
        (
            score,
            path,
            found,
        )
    )

candidate_scores.sort(
    key=lambda x: (
        -x[0],
        str(x[1])
    )
)

for score, path, found in candidate_scores:

    print(
        f"{score:02d}  {relative(path)}"
    )


# ---------------------------------------------------------------------------
# Deep extraction from strongest candidates
# ---------------------------------------------------------------------------

print_header(
    "MOD-025 — STRONGEST T7 GOVERNANCE ARTIFACT CONTENT"
)

top_candidates = candidate_scores[:10]

for score, path, found in top_candidates:

    print(
        "\n" + "-" * 96
    )

    print(
        f"FILE: {relative(path)}"
    )

    print(
        f"SCORE: {score}"
    )

    data = load_json(path)

    if isinstance(data, dict) and "__load_error__" in data:

        print(
            f"LOAD ERROR: {data['__load_error__']}"
        )

        continue

    # Only extract the most decision-relevant semantic fields.
    priority_keys = {
        "task",
        "task_name",
        "objective",
        "target",
        "prediction_boundary",
        "admitted_features",
        "excluded_features",
        "missingness_policy",
        "leakage_controls",
        "selected_model",
        "final_model",
        "selection_basis",
        "selection_reasons",
        "closure_status",
        "final_model_status",
        "split_method",
        "shuffle",
        "ordering",
        "temporal_boundaries",
        "sizes",
        "event",
        "censoring",
        "observation_endpoint",
        "training",
        "evaluation",
    }

    selected = {
        key_path: value
        for key_path, value in found.items()
        if key_path.split(".")[-1] in priority_keys
    }

    for key_path in sorted(selected):

        print(
            f"\n{key_path}:"
        )

        print(
            json.dumps(
                selected[key_path],
                indent=2,
                ensure_ascii=False
            )
        )


# ---------------------------------------------------------------------------
# Prediction artifact discovery
# ---------------------------------------------------------------------------

print_header(
    "MOD-025 — T7 PREDICTION ARTIFACT DISCOVERY"
)

prediction_terms = [
    "prediction",
    "evaluation",
    "eval",
    "survival",
    "median",
]

prediction_candidates = []

for path in all_files:

    name = path.name.lower()

    if any(
        term in name
        for term in prediction_terms
    ):

        prediction_candidates.append(
            path
        )

print(
    f"Prediction/evaluation-like files: "
    f"{len(prediction_candidates):,}"
)

for path in prediction_candidates:

    print(
        f"  {relative(path)}"
    )


# ---------------------------------------------------------------------------
# Inspect T7 CSV headers
# ---------------------------------------------------------------------------

print_header(
    "MOD-025 — T7 CSV SCHEMA DISCOVERY"
)

csv_files = [
    path
    for path in all_files
    if path.suffix.lower() == ".csv"
]

print(
    f"T7 CSV files: {len(csv_files):,}"
)

for path in csv_files:

    try:

        with path.open(
            "r",
            encoding="utf-8",
            errors="replace",
            newline=""
        ) as f:

            header = f.readline().strip()

    except Exception as exc:

        print(
            f"\n{relative(path)}"
        )

        print(
            f"  READ ERROR: {exc}"
        )

        continue

    print(
        f"\n{relative(path)}"
    )

    print(
        f"  HEADER: {header}"
    )


# ---------------------------------------------------------------------------
# Inspect model artifact names
# ---------------------------------------------------------------------------

print_header(
    "MOD-025 — T7 MODEL ARTIFACT DISCOVERY"
)

model_terms = [
    "model",
    "aft",
    "weibull",
    "log_normal",
    "log-normal",
    "lifelines",
]

model_candidates = []

for path in all_files:

    name = path.name.lower()

    if any(
        term in name
        for term in model_terms
    ):

        model_candidates.append(
            path
        )

print(
    f"Model-like files: "
    f"{len(model_candidates):,}"
)

for path in model_candidates:

    print(
        f"  {relative(path)}"
    )


# ---------------------------------------------------------------------------
# Final discovery summary
# ---------------------------------------------------------------------------

print_header(
    "MOD-025 — DISCOVERY SUMMARY"
)

print(
    f"T7 total files: {len(all_files):,}"
)

print(
    f"T7 Python scripts: {len(script_candidates):,}"
)

print(
    f"T7 JSON files: {len(json_files):,}"
)

print(
    f"T7 semantic JSON candidates: "
    f"{len(json_semantic_hits):,}"
)

print(
    f"T7 prediction/evaluation candidates: "
    f"{len(prediction_candidates):,}"
)

print(
    f"T7 model-like candidates: "
    f"{len(model_candidates):,}"
)

print(
    """
The purpose of this module is discovery only.

The output must be used to identify the authoritative T7
closure/model-selection/contract/split artifacts before any
controlled T7 OoF prediction generation is attempted.
"""
)

print(
    "\nNo model loaded."
)

print(
    "No model trained."
)

print(
    "No prediction generated."
)

print(
    "No artifact modified."
)

print(
    "\nMOD-025 T7 FROZEN CONTRACT AND "
    "IMPLEMENTATION ARTIFACT DISCOVERY COMPLETE"
)

print(
    "STATUS: DISCOVERY COMPLETE / REVIEW REQUIRED"
)