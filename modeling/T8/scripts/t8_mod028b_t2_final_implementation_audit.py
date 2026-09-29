#!/usr/bin/env python3

import ast
import json
from pathlib import Path


# ============================================================================
# T8 MOD-028B
# T2 Final Implementation Contract Audit
# ============================================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_ROOT = PROJECT_ROOT / "modeling/T2"

FINAL_SELECTION = (
    T2_ROOT / "analysis/t2_final_model_selection.json"
)

FINAL_CLOSURE = (
    T2_ROOT / "analysis/t2_final_closure.json"
)

MODEL_CONTRACT = (
    T2_ROOT / "contracts/t2_model_contract.json"
)

TRAIN_SCRIPT = (
    T2_ROOT / "scripts/t2_class_weighted.py"
)

FINAL_SELECTION_SCRIPT = (
    T2_ROOT / "scripts/t2_final_model_selection.py"
)

MODEL_PATH = (
    T2_ROOT / "models/t2_class_weighted_tfidf_logreg.joblib"
)


# ============================================================================
# Helpers
# ============================================================================

def header(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def require_file(path, label):
    exists = path.exists()

    print(
        f"{label:45s} "
        f"{'FOUND' if exists else 'MISSING':8s} "
        f"{path}"
    )

    if not exists:
        raise FileNotFoundError(
            f"Required artifact missing: {path}"
        )


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def source(path):
    return path.read_text(
        encoding="utf-8"
    )


def print_matching_lines(text, patterns):
    lines = text.splitlines()

    for number, line in enumerate(
        lines,
        start=1,
    ):
        lowered = line.lower()

        if any(
            pattern.lower() in lowered
            for pattern in patterns
        ):
            print(
                f"{number:5d}: {line}"
            )


def ast_string(node):
    if isinstance(node, ast.Constant):
        return node.value

    return None


# ============================================================================
# Header
# ============================================================================

print("=" * 100)
print(
    "T8 MOD-028B — T2 FINAL IMPLEMENTATION CONTRACT AUDIT"
)
print("=" * 100)

print(
    """
Purpose:
Recover the exact implementation parameters required to reproduce
T2-MOD-007 inside chronological OoF folds.

This module is READ-ONLY.

No model is loaded.
No model is fitted.
No prediction is generated.
No artifact is modified.
"""
)


# ============================================================================
# 1. Required artifacts
# ============================================================================

header(
    "MOD-028B — 1. REQUIRED ARTIFACTS"
)

required = [
    ("T2 final selection", FINAL_SELECTION),
    ("T2 final closure", FINAL_CLOSURE),
    ("T2 model contract", MODEL_CONTRACT),
    ("T2 class-weighted implementation", TRAIN_SCRIPT),
    ("T2 final-selection implementation", FINAL_SELECTION_SCRIPT),
    ("T2 class-weighted model artifact", MODEL_PATH),
]

for label, path in required:
    require_file(path, label)


# ============================================================================
# 2. Frozen selection
# ============================================================================

header(
    "MOD-028B — 2. FROZEN MODEL SELECTION"
)

selection = load_json(
    FINAL_SELECTION
)

selected = selection.get(
    "selected_model",
    {}
)

print(
    json.dumps(
        selected,
        indent=2,
        ensure_ascii=False,
    )
)

print(
    "\nSelection basis:"
)

print(
    json.dumps(
        selection.get(
            "selection_basis",
            {}
        ),
        indent=2,
        ensure_ascii=False,
    )
)


# ============================================================================
# 3. Source inventory
# ============================================================================

header(
    "MOD-028B — 3. IMPLEMENTATION SOURCE INVENTORY"
)

train_source = source(
    TRAIN_SCRIPT
)

selection_source = source(
    FINAL_SELECTION_SCRIPT
)

print(
    f"Class-weighted implementation lines: "
    f"{len(train_source.splitlines()):,}"
)

print(
    f"Final-selection implementation lines: "
    f"{len(selection_source.splitlines()):,}"
)


# ============================================================================
# 4. Relevant source lines
# ============================================================================

header(
    "MOD-028B — 4. T2 IMPLEMENTATION SOURCE MARKERS"
)

patterns = [
    "TfidfVectorizer",
    "LogisticRegression",
    "class_weight",
    "ngram_range",
    "max_features",
    "min_df",
    "max_df",
    "sublinear_tf",
    "strip_accents",
    "lowercase",
    "analyzer",
    "token_pattern",
    "C=",
    "solver",
    "max_iter",
    "random_state",
    "Summary",
    "Description",
    "fit_transform",
    "transform",
    "pipeline",
    "FeatureUnion",
    "ColumnTransformer",
]

print_matching_lines(
    train_source,
    patterns,
)


# ============================================================================
# 5. AST extraction of constructor calls
# ============================================================================

header(
    "MOD-028B — 5. AST CONSTRUCTOR EXTRACTION"
)

tree = ast.parse(
    train_source
)

constructors = []

for node in ast.walk(tree):

    if not isinstance(
        node,
        ast.Call,
    ):
        continue

    func_name = None

    if isinstance(
        node.func,
        ast.Name,
    ):
        func_name = node.func.id

    elif isinstance(
        node.func,
        ast.Attribute,
    ):
        func_name = node.func.attr

    if func_name in {
        "TfidfVectorizer",
        "LogisticRegression",
    }:

        arguments = {}

        for keyword in node.keywords:

            if keyword.arg is None:
                continue

            value = ast_string(
                keyword.value
            )

            if value is None:
                try:
                    value = ast.literal_eval(
                        keyword.value
                    )
                except Exception:
                    value = (
                        ast.unparse(
                            keyword.value
                        )
                    )

            arguments[
                keyword.arg
            ] = value

        constructors.append(
            {
                "function": func_name,
                "line": node.lineno,
                "arguments": arguments,
            }
        )


if constructors:

    for item in constructors:

        print(
            f"\n{item['function']} "
            f"(line {item['line']})"
        )

        for key, value in item[
            "arguments"
        ].items():

            print(
                f"  {key}: {value!r}"
            )

else:

    print(
        "No direct TfidfVectorizer / "
        "LogisticRegression constructor "
        "calls found by AST extraction."
    )


# ============================================================================
# 6. Model artifact metadata WITHOUT loading it
# ============================================================================

header(
    "MOD-028B — 6. MODEL ARTIFACT METADATA CHECK"
)

print(
    """
The .joblib artifact is NOT loaded.

Only filesystem metadata is inspected here.
The implementation source remains the authoritative basis for
fold-local reproduction.
"""
)

stat = MODEL_PATH.stat()

print(
    f"Model artifact size : {stat.st_size:,} bytes"
)

print(
    f"Model artifact path : {MODEL_PATH}"
)


# ============================================================================
# 7. T2 feature-input contract
# ============================================================================

header(
    "MOD-028B — 7. T2 FEATURE-INPUT CONTRACT"
)

contract = load_json(
    MODEL_CONTRACT
)

for key in [
    "task_id",
    "task_name",
    "prediction_boundary",
    "target",
    "feature_boundary",
    "leakage_controls",
]:

    if key in contract:

        print(
            f"\n[{key}]"
        )

        print(
            json.dumps(
                contract[key],
                indent=2,
                ensure_ascii=False,
            )
        )


# ============================================================================
# 8. Closure evidence
# ============================================================================

header(
    "MOD-028B — 8. T2 FINAL CLOSURE EVIDENCE"
)

closure = load_json(
    FINAL_CLOSURE
)

print(
    json.dumps(
        closure,
        indent=2,
        ensure_ascii=False,
    )
)


# ============================================================================
# 9. Determine whether exact fold reproduction is auditable
# ============================================================================

header(
    "MOD-028B — 9. FOLD-REPRODUCTION READINESS"
)

constructor_names = {
    item["function"]
    for item in constructors
}

has_tfidf = (
    "TfidfVectorizer"
    in constructor_names
)

has_logreg = (
    "LogisticRegression"
    in constructor_names
)

print(
    f"TF-IDF constructor source-visible      : "
    f"{has_tfidf}"
)

print(
    f"Logistic Regression constructor visible: "
    f"{has_logreg}"
)

print(
    "\nRequired for T2 chronological OoF:"
)

print(
    "  1. Exact TF-IDF configuration"
)

print(
    "  2. Exact Logistic Regression configuration"
)

print(
    "  3. Exact class-weighting configuration"
)

print(
    "  4. Exact text construction / concatenation"
)

print(
    "  5. Fold-local fit_transform on training text"
)

print(
    "  6. Fold-local transform on prediction block"
)

print(
    "  7. No prediction-block target information in fitting"
)

print(
    "  8. Chronological training-prefix restriction"
)


# ============================================================================
# 10. Final status
# ============================================================================

header(
    "MOD-028B — FINAL STATUS"
)

if has_tfidf and has_logreg:

    print(
        "STATUS: SOURCE IMPLEMENTATION FOUND"
    )

    print(
        """
The exact T2 implementation appears directly recoverable from
the existing source code.

The next step is to inspect the constructor configuration above
and determine whether it can be reproduced fold-locally without
loading or reusing the locked full-training model artifact.
"""
    )

else:

    print(
        "STATUS: FOLLOW-UP REQUIRED"
    )

    print(
        """
The exact T2 implementation could not be fully recovered from
the inspected source. Do not begin OoF generation until the
missing implementation details are established.
"""
    )

print(
    "\nNo model was loaded."
)

print(
    "No model was fitted."
)

print(
    "No predictions were generated."
)

print(
    "No artifacts were modified."
)

print(
    "\nMOD-028B COMPLETE"
)