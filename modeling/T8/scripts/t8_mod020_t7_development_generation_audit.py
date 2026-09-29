#!/usr/bin/env python3

from pathlib import Path
import json
import re

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T7_ROOT = PROJECT_ROOT / "modeling" / "T7"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_text(path):
    try:
        return path.read_text(
            encoding="utf-8",
            errors="replace"
        )
    except Exception as exc:
        return f"[READ ERROR: {exc}]"


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


def flatten_json(obj, prefix=""):
    values = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            child = (
                f"{prefix}.{key}"
                if prefix
                else str(key)
            )
            values.extend(
                flatten_json(value, child)
            )

    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            values.extend(
                flatten_json(
                    value,
                    f"{prefix}[{i}]"
                )
            )

    elif isinstance(obj, str):
        values.append((prefix, obj))

    return values


def print_section(title):
    print("\n" + "=" * 82)
    print(title)
    print("=" * 82)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

print("=" * 82)
print(
    "MOD-020 — T7 DEVELOPMENT-PREDICTION "
    "GENERATION FEASIBILITY AUDIT"
)
print("=" * 82)

print(f"T7 root: {T7_ROOT}")


# ---------------------------------------------------------------------------
# Key files
# ---------------------------------------------------------------------------

print_section(
    "MOD-020 — KEY T7 ARTIFACTS"
)

key_paths = [
    T7_ROOT / "contracts" / "t7_modeling_contract.json",

    T7_ROOT / "metrics" / "t7_mod004_feature_temporal_split_audit.json",
    T7_ROOT / "metrics" / "t7_mod005_split_freeze.json",
    T7_ROOT / "metrics" / "t7_mod006_survival_baseline_audit.json",
    T7_ROOT / "metrics" / "t7_mod007_predictive_survival_audit.json",
    T7_ROOT / "metrics" / "t7_mod008_predictive_vs_reference_audit.json",
    T7_ROOT / "metrics" / "t7_mod009_survival_calibration_audit.json",
    T7_ROOT / "metrics" / "t7_mod010_log_normal_aft_audit.json",
    T7_ROOT / "metrics" / "t7_mod011_final_model_comparison_audit.json",
    T7_ROOT / "metrics" / "t7_mod012_final_closure.json",

    T7_ROOT / "splits" / "t7_train.csv",
    T7_ROOT / "splits" / "t7_evaluation.csv",

    T7_ROOT / "scripts" / "t7_mod007_predictive_survival_baseline.py",
    T7_ROOT / "scripts" / "t7_mod008_predictive_vs_reference_evaluation.py",
]

for path in key_paths:
    print(
        f"{'PRESENT' if path.exists() else 'MISSING'}  {path}"
    )


# ---------------------------------------------------------------------------
# JSON provenance extraction
# ---------------------------------------------------------------------------

print_section(
    "MOD-020 — T7 CONTRACT / CLOSURE PROVENANCE"
)

metadata_paths = [
    T7_ROOT / "contracts" / "t7_modeling_contract.json",
    T7_ROOT / "metrics" / "t7_mod004_feature_temporal_split_audit.json",
    T7_ROOT / "metrics" / "t7_mod005_split_freeze.json",
    T7_ROOT / "metrics" / "t7_mod006_survival_baseline_audit.json",
    T7_ROOT / "metrics" / "t7_mod007_predictive_survival_audit.json",
    T7_ROOT / "metrics" / "t7_mod008_predictive_vs_reference_audit.json",
    T7_ROOT / "metrics" / "t7_mod009_survival_calibration_audit.json",
    T7_ROOT / "metrics" / "t7_mod010_log_normal_aft_audit.json",
    T7_ROOT / "metrics" / "t7_mod011_final_model_comparison_audit.json",
    T7_ROOT / "metrics" / "t7_mod012_final_closure.json",
]

terms = [
    "train",
    "validation",
    "development",
    "evaluation",
    "test",
    "split",
    "chronological",
    "prediction",
    "predict",
    "feature",
    "creation",
    "censor",
    "censoring",
    "locked",
    "model",
    "artifact",
]

for path in metadata_paths:

    if not path.exists():
        continue

    data = read_json(path)

    print(f"\n--- {path.name} ---")

    matches = []

    for field, value in flatten_json(data):

        lower = value.lower()

        matched = [
            term
            for term in terms
            if term in lower
        ]

        if matched:
            matches.append(
                (
                    field,
                    value,
                    matched
                )
            )

    for field, value, matched in matches[:30]:

        print(
            f"{field}: {value}"
        )

    if len(matches) > 30:
        print(
            f"... {len(matches) - 30} additional matches"
        )


# ---------------------------------------------------------------------------
# Source-code discovery
# ---------------------------------------------------------------------------

print_section(
    "MOD-020 — T7 SOURCE-CODE DISCOVERY"
)

script_paths = sorted(
    T7_ROOT.rglob("*.py")
)

print(
    f"T7 Python source files: "
    f"{len(script_paths)}"
)

for path in script_paths:
    print(path)


# ---------------------------------------------------------------------------
# Prediction-generation code search
# ---------------------------------------------------------------------------

print_section(
    "MOD-020 — PREDICTION-GENERATION CODE SEARCH"
)

code_terms = [
    "predict(",
    "predict_survival_function",
    "predict_median",
    "survival_probability",
    "save(",
    "np.savez",
    "to_csv",
    "evaluation",
    "train",
    "validation",
    "test",
    "t7_evaluation",
    "t7_train",
]

for path in script_paths:

    text = read_text(path)

    hits = []

    for term in code_terms:

        if term.lower() in text.lower():
            hits.append(term)

    if not hits:
        continue

    print(
        f"\n{path}"
    )

    print(
        "  matched: "
        + ", ".join(hits)
    )


# ---------------------------------------------------------------------------
# Detailed inspection of predictive scripts
# ---------------------------------------------------------------------------

print_section(
    "MOD-020 — PREDICTIVE SCRIPT STRUCTURAL INSPECTION"
)

predictive_scripts = [
    path
    for path in script_paths
    if any(
        token in path.name.lower()
        for token in [
            "predictive",
            "survival",
            "aft",
            "model"
        ]
    )
]

for path in predictive_scripts:

    text = read_text(path)

    print(
        f"\n--- {path} ---"
    )

    lines = text.splitlines()

    important_patterns = [
        r"read_csv",
        r"train",
        r"evaluation",
        r"validation",
        r"test",
        r"fit\(",
        r"predict",
        r"predict_survival",
        r"predict_median",
        r"save",
        r"to_csv",
        r"np\.savez",
        r"joblib",
        r"pickle",
        r"Creation",
        r"duration",
        r"event",
        r"censor",
    ]

    shown = 0

    for number, line in enumerate(lines, start=1):

        if any(
            re.search(
                pattern,
                line,
                flags=re.IGNORECASE
            )
            for pattern in important_patterns
        ):

            print(
                f"{number:5d}: {line}"
            )

            shown += 1

            if shown >= 80:
                print(
                    "  ... source display capped at 80 matching lines"
                )
                break


# ---------------------------------------------------------------------------
# Explicit validation / development implementation search
# ---------------------------------------------------------------------------

print_section(
    "MOD-020 — VALIDATION / DEVELOPMENT IMPLEMENTATION SEARCH"
)

validation_hits = []

search_patterns = [
    r"\bvalidation\b",
    r"\bdevelopment\b",
    r"\boof\b",
    r"out.of.fold",
    r"cross.validation",
    r"KFold",
    r"TimeSeriesSplit",
    r"train.*validation",
    r"validation.*train",
]

for path in script_paths:

    text = read_text(path)

    matches = []

    for pattern in search_patterns:

        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        ):
            matches.append(pattern)

    if matches:

        validation_hits.append(
            (path, matches)
        )

for path, matches in validation_hits:

    print(
        f"{path}"
    )

    print(
        "  matched: "
        + ", ".join(matches)
    )


# ---------------------------------------------------------------------------
# Model artifact discovery
# ---------------------------------------------------------------------------

print_section(
    "MOD-020 — T7 MODEL ARTIFACT DISCOVERY"
)

model_extensions = {
    ".joblib",
    ".pkl",
    ".pickle",
    ".model",
    ".bin",
    ".pt",
    ".pth",
    ".h5",
    ".keras",
}

model_candidates = []

for path in sorted(T7_ROOT.rglob("*")):

    if not path.is_file():
        continue

    if path.suffix.lower() in model_extensions:
        model_candidates.append(path)

    elif any(
        token in path.name.lower()
        for token in [
            "model",
            "estimator",
            "aft"
        ]
    ):
        model_candidates.append(path)

for path in model_candidates:
    print(path)

print(
    f"\nModel-like artifact count: "
    f"{len(model_candidates)}"
)


# ---------------------------------------------------------------------------
# Existing prediction artifacts
# ---------------------------------------------------------------------------

print_section(
    "MOD-020 — EXISTING T7 PREDICTION ARTIFACTS"
)

prediction_candidates = []

for path in sorted(T7_ROOT.rglob("*")):

    if not path.is_file():
        continue

    name = path.name.lower()

    if any(
        token in name
        for token in [
            "prediction",
            "predictive",
            "predictions"
        ]
    ):
        prediction_candidates.append(path)

for path in prediction_candidates:

    print(
        f"{path}"
    )

    try:
        size = path.stat().st_size
        print(
            f"  size: {size:,} bytes"
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Split semantics
# ---------------------------------------------------------------------------

print_section(
    "MOD-020 — SPLIT SEMANTICS"
)

print("""
The audit must distinguish:

  TRAIN
    Used to fit the T7 predictive model.

  DEVELOPMENT / VALIDATION
    A population on which predictions are generated without
    fitting the corresponding prediction for that population.

  LOCKED EVALUATION
    Frozen chronological population reserved for final evaluation.

The existence of a TRAIN population does not itself provide
out-of-sample predictions for TRAIN.

The existence of an EVALUATION prediction artifact does not
make that population eligible for fusion development.
""")


# ---------------------------------------------------------------------------
# Creation boundary / censoring semantics
# ---------------------------------------------------------------------------

print_section(
    "MOD-020 — TEMPORAL / SURVIVAL SEMANTICS"
)

print("""
Required preservation if development predictions are generated:

  Prediction boundary:
    Creation

  Outcome:
    Time from Creation until first post-Creation operationally
    observed Status change to RESOLVED.

  Censoring:
    Administrative/right-censoring remains intrinsic to T7.

  Feature eligibility:
    Only information available at Creation.

  Development predictions:
    Must not use first_resolved_time, duration_seconds, event,
    or observation-end information as predictive inputs.

  Final evaluation:
    t7_evaluation.csv remains locked.
""")


# ---------------------------------------------------------------------------
# Feasibility assessment
# ---------------------------------------------------------------------------

print_section(
    "MOD-020 — FEASIBILITY ASSESSMENT"
)

print("""
The audit is looking for one of three evidence states:

STATE A — EXISTING DEVELOPMENT PREDICTIONS
  A documented, ID-addressable T7 validation/OoF prediction
  artifact already exists and its provenance is sufficient.

STATE B — CONTROLLED GENERATION POSSIBLE
  No existing development predictions exist, but the completed
  T7 implementation clearly separates training from evaluation,
  preserves the frozen Creation boundary and survival formulation,
  and contains enough reproducible training/prediction machinery
  to generate a new held-out development prediction population
  without touching the locked evaluation.

STATE C — CONTROLLED GENERATION NOT ESTABLISHED
  The evidence is insufficient to safely generate development
  predictions without reopening or altering the completed T7
  modeling workflow.

No state is selected automatically by filename.
""")


# ---------------------------------------------------------------------------
# Explicit prohibitions
# ---------------------------------------------------------------------------

print_section(
    "MOD-020 — PROHIBITIONS"
)

print("""
DO NOT:

  - predict on T7 training rows and call those OoF predictions;
  - use T7 evaluation predictions for fusion training;
  - refit T7 on the evaluation population;
  - alter the frozen chronological evaluation boundary;
  - use duration_seconds or event as predictive features;
  - convert survival outputs into ordinary regression targets;
  - alter censoring semantics;
  - create a synthetic validation split after inspecting evaluation;
  - tune T7 using the locked evaluation population;
  - modify the existing T7 prediction artifacts.
""")


# ---------------------------------------------------------------------------
# Final integrity status
# ---------------------------------------------------------------------------

print_section(
    "MOD-020 — INTEGRITY STATUS"
)

print("""
No model loaded.
No model trained.
No prediction generated.
No raw dataset accessed.
No prediction artifact modified.
No T7 split modified.

This operation is source-code / metadata / artifact provenance
inspection only.
""")


print("\nMOD-020 T7 DEVELOPMENT-PREDICTION GENERATION")
print("FEASIBILITY AUDIT COMPLETE")
print("STATUS: COMPLETE / PASS")