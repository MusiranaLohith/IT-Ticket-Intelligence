#!/usr/bin/env python3

import ast
import re
from pathlib import Path

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T7_SCRIPT = (
    PROJECT_ROOT
    / "modeling/T7/scripts/t7_mod010_log_normal_aft_baseline.py"
)

T7_AUDIT = (
    PROJECT_ROOT
    / "modeling/T7/metrics/t7_mod010_log_normal_aft_audit.json"
)

T7_MODEL = (
    PROJECT_ROOT
    / "modeling/T7/metrics/t7_mod010_log_normal_aft_model.json"
)

T7_TRAIN = (
    PROJECT_ROOT
    / "modeling/T7/splits/t7_train.csv"
)

T7_EVAL = (
    PROJECT_ROOT
    / "modeling/T7/splits/t7_evaluation.csv"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def print_header(title):
    print("\n" + "=" * 96)
    print(title)
    print("=" * 96)


def relative(path):
    try:
        return path.relative_to(PROJECT_ROOT)
    except ValueError:
        return path


def print_code_context(lines, line_number, radius=5):
    start = max(1, line_number - radius)
    end = min(len(lines), line_number + radius)

    for number in range(start, end + 1):

        marker = ">>>" if number == line_number else "   "

        print(
            f"{marker} {number:04d}: "
            f"{lines[number - 1]}"
        )


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

print("=" * 96)
print(
    "MOD-027 — T7 LOG-NORMAL AFT FEATURE AND "
    "PREPROCESSING CONTRACT AUDIT"
)
print("=" * 96)

print(
    "Purpose: explicitly extract the exact Log-Normal AFT feature "
    "construction, missingness handling, preprocessing, standardization, "
    "and native prediction pathway before controlled OoF generation."
)

print(
    "\nREAD-ONLY AUDIT."
    "\nNo model loading."
    "\nNo model fitting."
    "\nNo prediction generation."
    "\nNo artifact modification."
)


# ---------------------------------------------------------------------------
# File availability
# ---------------------------------------------------------------------------

print_header(
    "MOD-027 — ARTIFACT AVAILABILITY"
)

for label, path in [
    ("T7 Log-Normal script", T7_SCRIPT),
    ("T7 Log-Normal audit", T7_AUDIT),
    ("T7 Log-Normal model metadata", T7_MODEL),
    ("T7 train", T7_TRAIN),
    ("T7 evaluation", T7_EVAL),
]:

    print(
        f"{label:30s} "
        f"{'FOUND' if path.exists() else 'MISSING'} "
        f"{relative(path)}"
    )


# ---------------------------------------------------------------------------
# Read implementation source
# ---------------------------------------------------------------------------

print_header(
    "MOD-027 — LOG-NORMAL IMPLEMENTATION SOURCE"
)

if not T7_SCRIPT.exists():

    raise SystemExit(
        "T7 Log-Normal implementation script not found."
    )

source = T7_SCRIPT.read_text(
    encoding="utf-8",
    errors="replace"
)

lines = source.splitlines()

print(
    f"Source lines: {len(lines):,}"
)


# ---------------------------------------------------------------------------
# Feature construction function
# ---------------------------------------------------------------------------

print_header(
    "MOD-027 — FEATURE-CONSTRUCTION FUNCTION DISCOVERY"
)

feature_markers = [
    "def text_features",
    "def make_features",
    "def build_features",
    "feature_names",
    "features =",
    "X.append",
]

for marker in feature_markers:

    matches = [
        number
        for number, line in enumerate(
            lines,
            start=1
        )
        if marker in line
    ]

    print(
        f"{marker:30s}: "
        f"{matches if matches else 'NOT FOUND'}"
    )


# ---------------------------------------------------------------------------
# Print exact make_features implementation
# ---------------------------------------------------------------------------

print_header(
    "MOD-027 — EXACT TEXT / FEATURE CONSTRUCTION"
)

make_start = None
make_end = None

for number, line in enumerate(
    lines,
    start=1
):

    if line.startswith("def make_features("):

        make_start = number

        break

if make_start is not None:

    for number in range(
        make_start + 1,
        len(lines) + 1
    ):

        line = lines[number - 1]

        if (
            line.startswith("def ")
            and number > make_start
        ):

            make_end = number - 1

            break

    if make_end is None:

        make_end = len(lines)

    print(
        f"make_features(): "
        f"lines {make_start}-{make_end}"
    )

    for number in range(
        make_start,
        make_end + 1
    ):

        print(
            f"{number:04d}: {lines[number - 1]}"
        )

else:

    print(
        "make_features() NOT FOUND"
    )


# ---------------------------------------------------------------------------
# Text feature function
# ---------------------------------------------------------------------------

print_header(
    "MOD-027 — EXACT TEXT-FEATURE CONSTRUCTION"
)

text_start = None
text_end = None

for number, line in enumerate(
    lines,
    start=1
):

    if line.startswith("def text_features("):

        text_start = number

        break

if text_start is not None:

    for number in range(
        text_start + 1,
        len(lines) + 1
    ):

        if (
            lines[number - 1].startswith("def ")
            and number > text_start
        ):

            text_end = number - 1

            break

    if text_end is None:

        text_end = len(lines)

    print(
        f"text_features(): "
        f"lines {text_start}-{text_end}"
    )

    for number in range(
        text_start,
        text_end + 1
    ):

        print(
            f"{number:04d}: {lines[number - 1]}"
        )

else:

    print(
        "text_features() NOT FOUND"
    )


# ---------------------------------------------------------------------------
# Standardization function
# ---------------------------------------------------------------------------

print_header(
    "MOD-027 — STANDARDIZATION IMPLEMENTATION"
)

standardization_markers = [
    "def standardize_fit",
    "def standardize_apply",
    "mean",
    "std",
    "standardize",
    "X_train",
    "X_eval",
]

for marker in standardization_markers:

    matches = [
        number
        for number, line in enumerate(
            lines,
            start=1
        )
        if marker.lower() in line.lower()
    ]

    print(
        f"{marker:25s}: "
        f"{matches if matches else 'NOT FOUND'}"
    )


standardize_start = None

for number, line in enumerate(
    lines,
    start=1
):

    if line.startswith(
        "def standardize_fit("
    ):

        standardize_start = number

        break

if standardize_start is not None:

    standardize_end = None

    for number in range(
        standardize_start + 1,
        len(lines) + 1
    ):

        if (
            lines[number - 1].startswith("def ")
            and number > standardize_start
        ):

            standardize_end = number - 1

            break

    if standardize_end is None:

        standardize_end = len(lines)

    print(
        f"\nExact standardize_fit() implementation:"
    )

    for number in range(
        standardize_start,
        standardize_end + 1
    ):

        print(
            f"{number:04d}: {lines[number - 1]}"
        )


# ---------------------------------------------------------------------------
# Data-loading / train-eval feature pathway
# ---------------------------------------------------------------------------

print_header(
    "MOD-027 — TRAIN / EVALUATION FEATURE MATERIALIZATION"
)

pathway_terms = [
    "TRAIN_PATH",
    "EVAL_PATH",
    "pd.read_csv",
    "make_features(",
    "standardize_fit(",
    "standardize_apply(",
    "X_train",
    "X_eval",
    "X_test",
    "train_df",
    "eval_df",
    "fit(",
    "predict_median",
    "predict_survival_function",
]

for number, line in enumerate(
    lines,
    start=1
):

    if any(
        term.lower() in line.lower()
        for term in pathway_terms
    ):

        print(
            f"{number:04d}: {line}"
        )


# ---------------------------------------------------------------------------
# Native prediction output construction
# ---------------------------------------------------------------------------

print_header(
    "MOD-027 — NATIVE PREDICTION OUTPUT EXTRACTION"
)

prediction_terms = [
    "predicted_median_survival_seconds",
    "survival_probability_at_211583_seconds",
    "survival_probability_at_1780179_seconds",
    "survival_probability_at_14608619_seconds",
    "predict_median",
    "predict_survival_function",
    "result",
    "to_csv",
]

for number, line in enumerate(
    lines,
    start=1
):

    if any(
        term.lower() in line.lower()
        for term in prediction_terms
    ):

        print(
            f"{number:04d}: {line}"
        )


# ---------------------------------------------------------------------------
# Exact model-fitting pathway
# ---------------------------------------------------------------------------

print_header(
    "MOD-027 — MODEL-FITTING PATHWAY"
)

fit_markers = [
    "LogNormalAFTFitter",
    "model =",
    "model.fit",
    "duration_col",
    "event_col",
    "X_train",
    "train_df",
]

for number, line in enumerate(
    lines,
    start=1
):

    if any(
        marker.lower() in line.lower()
        for marker in fit_markers
    ):

        print(
            f"{number:04d}: {line}"
        )


# ---------------------------------------------------------------------------
# Feature-name extraction from source
# ---------------------------------------------------------------------------

print_header(
    "MOD-027 — FEATURE-NAME EXTRACTION"
)

# Look for the feature_names / feature list assignment.
feature_lines = []

for number, line in enumerate(
    lines,
    start=1
):

    if (
        "feature_names" in line
        or
        "features = [" in line
    ):

        feature_lines.append(
            number
        )

for number in feature_lines:

    print_code_context(
        lines,
        number,
        radius=8
    )


# ---------------------------------------------------------------------------
# Leakage-sensitive operations
# ---------------------------------------------------------------------------

print_header(
    "MOD-027 — LEAKAGE-SENSITIVE OPERATIONS"
)

leakage_terms = [
    "fit_transform",
    "transform",
    "standardize_fit",
    "mean(",
    "std(",
    "global",
    "full",
    "train",
    "eval",
    "evaluation",
    "Creation time",
    "first_resolved_time",
    "duration_seconds",
    "event",
]

for number, line in enumerate(
    lines,
    start=1
):

    if any(
        term.lower() in line.lower()
        for term in leakage_terms
    ):

        print(
            f"{number:04d}: {line}"
        )


# ---------------------------------------------------------------------------
# Model metadata
# ---------------------------------------------------------------------------

print_header(
    "MOD-027 — LOG-NORMAL MODEL METADATA"
)

if T7_MODEL.exists():

    import json

    with T7_MODEL.open(
        "r",
        encoding="utf-8",
        errors="replace"
    ) as f:

        model_data = json.load(f)

    print(
        json.dumps(
            model_data,
            indent=2,
            ensure_ascii=False
        )
    )

else:

    print(
        "MODEL METADATA NOT FOUND"
    )


# ---------------------------------------------------------------------------
# Audit metadata
# ---------------------------------------------------------------------------

print_header(
    "MOD-027 — LOG-NORMAL AUDIT METADATA"
)

if T7_AUDIT.exists():

    import json

    with T7_AUDIT.open(
        "r",
        encoding="utf-8",
        errors="replace"
    ) as f:

        audit_data = json.load(f)

    print(
        json.dumps(
            audit_data,
            indent=2,
            ensure_ascii=False
        )
    )

else:

    print(
        "AUDIT METADATA NOT FOUND"
    )


# ---------------------------------------------------------------------------
# Contract conclusion
# ---------------------------------------------------------------------------

print_header(
    "MOD-027 — CONTRACT QUESTIONS TO RESOLVE"
)

questions = [
    "1. Exact Log-Normal feature list?",
    "2. Exact text-statistic definitions?",
    "3. Exact missing-text handling?",
    "4. Exact Creator / Creator Detail frequency handling?",
    "5. Exact Creation-time transformations?",
    "6. Exact standardization procedure?",
    "7. Are standardization statistics fitted only on training data?",
    "8. Are evaluation/prediction rows transformed using training statistics?",
    "9. Exact columns passed to LogNormalAFTFitter?",
    "10. Exact native prediction outputs?",
    "11. Are duration_seconds and event used only as native training outcomes?",
    "12. Is any post-Creation information used in feature construction?",
]

for question in questions:

    print(
        question
    )


print_header(
    "MOD-027 — SAFETY GATE"
)

print(
    """
No model loaded.
No model trained.
No prediction generated.
No artifact modified.

OoF generation remains blocked until the source-level
preprocessing behavior is understood and can be reproduced
without temporal leakage.
"""
)

print(
    "\nMOD-027 T7 LOG-NORMAL AFT FEATURE AND "
    "PREPROCESSING CONTRACT AUDIT COMPLETE"
)

print(
    "STATUS: COMPLETE / REVIEW REQUIRED"
)