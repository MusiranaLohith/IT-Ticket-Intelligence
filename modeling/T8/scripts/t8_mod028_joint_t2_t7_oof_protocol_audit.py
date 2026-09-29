#!/usr/bin/env python3

import json
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================================
# T8 MOD-028
# Joint T2/T7 Chronological OoF Protocol Audit
# ============================================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_ROOT = PROJECT_ROOT / "modeling/T2"
T7_ROOT = PROJECT_ROOT / "modeling/T7"


# ---------------------------------------------------------------------------
# Actual frozen T2 split artifact paths
# ---------------------------------------------------------------------------

T2_TRAIN = T2_ROOT / "splits/train.csv"
T2_VAL = T2_ROOT / "splits/validation.csv"
T2_TEST = T2_ROOT / "splits/test.csv"

T2_SPLIT_REPORT = T2_ROOT / "splits/t2_split_report.json"

T2_CLOSURE = T2_ROOT / "analysis/t2_final_closure.json"
T2_SELECTION = T2_ROOT / "analysis/t2_final_model_selection.json"
T2_ARTIFACT_ID = (
    T2_ROOT / "analysis/t2_split_artifact_identification.json"
)

T2_CONTRACT = T2_ROOT / "contracts/t2_model_contract.json"

T2_FEATURES = T2_ROOT / "derived/t2_features.csv"

T2_MODEL = (
    T2_ROOT / "models/t2_baseline_tfidf_logreg.joblib"
)

T2_CLASS_WEIGHTED_MODEL = (
    T2_ROOT / "models/t2_class_weighted_tfidf_logreg.joblib"
)


# ---------------------------------------------------------------------------
# T7 frozen artifacts
# ---------------------------------------------------------------------------

T7_TRAIN = T7_ROOT / "splits/t7_train.csv"
T7_EVAL = T7_ROOT / "splits/t7_evaluation.csv"

T7_CONTRACT = T7_ROOT / "contracts/t7_modeling_contract.json"
T7_SPLIT_FREEZE = T7_ROOT / "metrics/t7_mod005_split_freeze.json"
T7_MODEL = T7_ROOT / "metrics/t7_mod010_log_normal_aft_model.json"

T7_SCRIPT = (
    T7_ROOT
    / "scripts/t7_mod010_log_normal_aft_baseline.py"
)


# ============================================================================
# Helpers
# ============================================================================

def header(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def require_file(path, label):
    exists = path.exists()

    print(
        f"{label:48s} "
        f"{'FOUND' if exists else 'MISSING':8s} "
        f"{path}"
    )

    if not exists:
        raise FileNotFoundError(
            f"Required artifact missing: {path}"
        )


def read_csv(path):
    return pd.read_csv(
        path,
        low_memory=False,
    )


def normalize_creation(df):
    result = df.copy()

    result["_creation_utc"] = pd.to_datetime(
        result["Creation time"],
        utc=True,
        errors="raise",
    )

    result["_id_str"] = (
        result["ID"]
        .astype(str)
    )

    return result


def chronological_sort(df):
    return df.sort_values(
        ["_creation_utc", "_id_str"],
        kind="mergesort",
    ).reset_index(drop=True)


def print_population(label, df):
    print(
        f"{label:24s}: {len(df):,}"
    )

    print(
        f"  earliest: {df['_creation_utc'].min()}"
    )

    print(
        f"  latest:   {df['_creation_utc'].max()}"
    )


def class_counts(df):
    if "target_priority" not in df.columns:
        return {}

    return dict(
        df["target_priority"]
        .astype(str)
        .value_counts()
        .sort_index()
    )


def format_counts(counts):
    if not counts:
        return "N/A"

    return ", ".join(
        f"{key}={value:,}"
        for key, value in counts.items()
    )


def get_first_existing_key(obj, keys):
    for key in keys:
        if key in obj:
            return obj[key]
    return None


# ============================================================================
# Header
# ============================================================================

print("=" * 100)
print(
    "T8 MOD-028 — JOINT T2/T7 CHRONOLOGICAL OoF PROTOCOL AUDIT"
)
print("=" * 100)

print(
    """
Purpose:
Freeze the exact development-prediction protocol for joint T2/T7
chronological out-of-fold evidence generation before any prediction
generation or model fitting is performed.

This module is READ-ONLY.

No model is loaded.
No model is fitted.
No prediction is generated.
No artifact is modified.
"""
)


# ============================================================================
# 1. Required artifact availability
# ============================================================================

header(
    "MOD-028 — 1. REQUIRED ARTIFACT AVAILABILITY"
)

required = [
    ("T2 train", T2_TRAIN),
    ("T2 validation", T2_VAL),
    ("T2 test", T2_TEST),
    ("T2 split report", T2_SPLIT_REPORT),
    ("T2 final closure", T2_CLOSURE),
    ("T2 model selection", T2_SELECTION),
    ("T2 artifact identification", T2_ARTIFACT_ID),
    ("T2 model contract", T2_CONTRACT),
    ("T2 materialized features", T2_FEATURES),
    ("T2 baseline TF-IDF model", T2_MODEL),
    ("T2 class-weighted TF-IDF model", T2_CLASS_WEIGHTED_MODEL),
    ("T7 train", T7_TRAIN),
    ("T7 evaluation", T7_EVAL),
    ("T7 modeling contract", T7_CONTRACT),
    ("T7 split freeze", T7_SPLIT_FREEZE),
    ("T7 Log-Normal model metadata", T7_MODEL),
    ("T7 Log-Normal implementation", T7_SCRIPT),
]

for label, path in required:
    require_file(path, label)


# ============================================================================
# 2. Load frozen populations
# ============================================================================

header(
    "MOD-028 — 2. FROZEN POPULATION INVENTORY"
)

t2_train = chronological_sort(
    normalize_creation(
        read_csv(T2_TRAIN)
    )
)

t2_val = chronological_sort(
    normalize_creation(
        read_csv(T2_VAL)
    )
)

t2_test = chronological_sort(
    normalize_creation(
        read_csv(T2_TEST)
    )
)

t7_train = chronological_sort(
    normalize_creation(
        read_csv(T7_TRAIN)
    )
)

t7_eval = chronological_sort(
    normalize_creation(
        read_csv(T7_EVAL)
    )
)

print_population("T2 train", t2_train)
print_population("T2 validation", t2_val)
print_population("T2 test", t2_test)
print_population("T7 train", t7_train)
print_population("T7 evaluation", t7_eval)


# ============================================================================
# 3. Basic population integrity
# ============================================================================

header(
    "MOD-028 — 3. POPULATION INTEGRITY"
)

population_checks = {}

population_checks["T2 train IDs unique"] = (
    t2_train["_id_str"].is_unique
)

population_checks["T2 validation IDs unique"] = (
    t2_val["_id_str"].is_unique
)

population_checks["T2 test IDs unique"] = (
    t2_test["_id_str"].is_unique
)

population_checks["T7 train IDs unique"] = (
    t7_train["_id_str"].is_unique
)

population_checks["T7 evaluation IDs unique"] = (
    t7_eval["_id_str"].is_unique
)

population_checks["T2 train/test disjoint"] = (
    set(t2_train["_id_str"]).isdisjoint(
        set(t2_test["_id_str"])
    )
)

population_checks["T2 train/validation disjoint"] = (
    set(t2_train["_id_str"]).isdisjoint(
        set(t2_val["_id_str"])
    )
)

population_checks["T2 validation/test disjoint"] = (
    set(t2_val["_id_str"]).isdisjoint(
        set(t2_test["_id_str"])
    )
)

population_checks["T7 train/evaluation disjoint"] = (
    set(t7_train["_id_str"]).isdisjoint(
        set(t7_eval["_id_str"])
    )
)

for name, passed in population_checks.items():
    print(
        f"{name:48s}: "
        f"{'PASS' if passed else 'FAIL'}"
    )


# ============================================================================
# 4. Frozen task boundaries
# ============================================================================

header(
    "MOD-028 — 4. TASK BOUNDARIES"
)

print(
    "T2 prediction boundary : Creation"
)

print(
    "T2 target              : first valid P1-P5 Priority assigned "
    "strictly after Creation within following 24 hours"
)

print(
    "T2 model               : TF-IDF + Class-Weighted Logistic Regression"
)

print(
    "T2 system role         : SECONDARY_DECISION_SUPPORT_SIGNAL"
)

print()

print(
    "T7 prediction boundary : Creation"
)

print(
    "T7 target              : time from Creation until first "
    "post-Creation History Status change to RESOLVED"
)

print(
    "T7 event semantics     : event=1 qualifying resolution; "
    "event=0 right-censored"
)

print(
    "T7 model               : Log-Normal AFT"
)


# ============================================================================
# 5. T2 contract / selection extraction
# ============================================================================

header(
    "MOD-028 — 5. T2 CONTRACT AND MODEL SELECTION"
)

t2_contract = load_json(T2_CONTRACT)
t2_selection = load_json(T2_SELECTION)
t2_closure = load_json(T2_CLOSURE)
t2_split_report = load_json(T2_SPLIT_REPORT)
t2_artifact_id = load_json(T2_ARTIFACT_ID)

print(
    "T2 model selection artifact:"
)

print(
    json.dumps(
        t2_selection,
        indent=2,
        ensure_ascii=False,
    )
)

print(
    "\nT2 split report:"
)

print(
    json.dumps(
        t2_split_report,
        indent=2,
        ensure_ascii=False,
    )
)

print(
    "\nT2 artifact identification:"
)

print(
    json.dumps(
        t2_artifact_id,
        indent=2,
        ensure_ascii=False,
    )
)


# ============================================================================
# 6. T2 exact source feature availability
# ============================================================================

header(
    "MOD-028 — 6. T2 FEATURE MATERIALIZATION AUDIT"
)

print(
    "Materialized T2 feature artifact:"
)

print(
    f"  {T2_FEATURES}"
)

t2_features = read_csv(T2_FEATURES)

print(
    f"\nRows: {len(t2_features):,}"
)

print(
    f"Columns: {len(t2_features.columns):,}"
)

print(
    "\nColumns:"
)

for index, column in enumerate(
    t2_features.columns,
    start=1,
):

    print(
        f"  {index:03d}. {column}"
    )

required_t2_feature_names = {
    "Summary",
    "Description",
}

feature_presence = {
    name: name in t2_features.columns
    for name in required_t2_feature_names
}

print(
    "\nRequired admitted T2 text fields:"
)

for name, present in feature_presence.items():

    print(
        f"  {name:20s}: "
        f"{'FOUND' if present else 'MISSING'}"
    )


# ============================================================================
# 7. T2 target / class coverage
# ============================================================================

header(
    "MOD-028 — 7. T2 TARGET AND CLASS COVERAGE"
)

for label, df in [
    ("T2 train", t2_train),
    ("T2 validation", t2_val),
    ("T2 test", t2_test),
]:

    counts = class_counts(df)

    print(
        f"{label}:"
    )

    print(
        f"  rows   : {len(df):,}"
    )

    print(
        f"  classes: {format_counts(counts)}"
    )


# ============================================================================
# 8. T7 contract / model extraction
# ============================================================================

header(
    "MOD-028 — 8. T7 CONTRACT AND MODEL"
)

t7_contract = load_json(T7_CONTRACT)
t7_split_freeze = load_json(T7_SPLIT_FREEZE)
t7_model = load_json(T7_MODEL)

print(
    "T7 modeling contract:"
)

print(
    json.dumps(
        t7_contract,
        indent=2,
        ensure_ascii=False,
    )
)

print(
    "\nT7 split freeze:"
)

print(
    json.dumps(
        t7_split_freeze,
        indent=2,
        ensure_ascii=False,
    )
)

print(
    "\nT7 model metadata summary:"
)

print(
    json.dumps(
        {
            "model_type": t7_model.get("model_type"),
            "l2": t7_model.get("l2"),
            "sigma": t7_model.get("sigma"),
            "feature_count": len(
                t7_model.get("feature_names", [])
            ),
        },
        indent=2,
        ensure_ascii=False,
    )
)


# ============================================================================
# 9. Exact T7 feature order
# ============================================================================

header(
    "MOD-028 — 9. T7 FEATURE ORDER"
)

t7_feature_names = t7_model.get(
    "feature_names",
    [],
)

for index, name in enumerate(
    t7_feature_names,
    start=1,
):

    print(
        f"{index:02d}. {name}"
    )

print(
    f"\nFeature count: {len(t7_feature_names)}"
)


# ============================================================================
# 10. T7 preprocessing freeze
# ============================================================================

header(
    "MOD-028 — 10. T7 PREPROCESSING FREEZE"
)

print(
    """
For EVERY chronological OoF fold:

1. Restrict T7 fitting rows to rows strictly earlier than
   the current prediction block.

2. Build Creator frequency counts from those fold-local
   T7 training rows only.

3. Build Creator Detail frequency counts from those
   fold-local T7 training rows only.

4. Construct all 21 native T7 features using those
   fold-local frequency maps.

5. Fit standardization mean/std on fold-local T7
   training features only.

6. Apply those exact mean/std values to the prediction
   block.

7. Fit Log-Normal AFT using the fold-local standardized
   training matrix.

8. Generate native T7 survival outputs for the prediction
   block.

9. Do not use prediction-block duration/event values in
   preprocessing or model fitting.

10. Do not use future rows.
"""
)


# ============================================================================
# 11. Common joint development population
# ============================================================================

header(
    "MOD-028 — 11. COMMON JOINT DEVELOPMENT POPULATION"
)

common_ids = (
    set(t2_train["_id_str"])
    .intersection(
        set(t7_train["_id_str"])
    )
)

common = chronological_sort(
    t2_train[
        t2_train["_id_str"].isin(common_ids)
    ]
)

print(
    f"Common T2/T7 development population: "
    f"{len(common):,}"
)

print(
    f"Earliest Creation: "
    f"{common['_creation_utc'].min()}"
)

print(
    f"Latest Creation:   "
    f"{common['_creation_utc'].max()}"
)

print(
    f"Common IDs inside T2 train: "
    f"{set(common['_id_str']).issubset(set(t2_train['_id_str']))}"
)

print(
    f"Common IDs inside T7 train: "
    f"{set(common['_id_str']).issubset(set(t7_train['_id_str']))}"
)

print(
    f"Common IDs inside T7 evaluation: "
    f"{len(set(common['_id_str']).intersection(set(t7_eval['_id_str']))):,}"
)


# ============================================================================
# 12. Candidate chronological fold designs
# ============================================================================

header(
    "MOD-028 — 12. CHRONOLOGICAL OoF DESIGN AUDIT"
)


def audit_design(n_blocks):

    print()
    print("-" * 96)
    print(f"{n_blocks}-BLOCK DESIGN")

    # Preserve pandas DataFrame structure when creating chronological blocks.
    block_indices = np.array_split(
        np.arange(len(common)),
        n_blocks,
    )

    blocks = [
        common.iloc[index_array].copy()
        for index_array in block_indices
    ]

    design_usable = True

    total_usable_predictions = 0

    for block_index, block in enumerate(
        blocks,
        start=1,
    ):

        prediction_start = (
            block["_creation_utc"].min()
        )

        prediction_end = (
            block["_creation_utc"].max()
        )

        # ---------------------------------------------------------------
        # T2 fitting history:
        # only T2 train rows strictly earlier than prediction boundary
        # ---------------------------------------------------------------

        t2_history = t2_train[
            t2_train["_creation_utc"]
            < prediction_start
        ]

        # ---------------------------------------------------------------
        # T7 fitting history:
        # all T7 train rows strictly earlier than prediction boundary
        # ---------------------------------------------------------------

        t7_history = t7_train[
            t7_train["_creation_utc"]
            < prediction_start
        ]

        counts = class_counts(
            t2_history
        )

        all_five_classes = {
            "P1",
            "P2",
            "P3",
            "P4",
            "P5",
        }.issubset(
            set(counts.keys())
        )

        block_usable = (
            len(t2_history) > 0
            and len(t7_history) > 0
            and all_five_classes
        )

        if not block_usable:
            design_usable = False

        if block_index >= 2:
            total_usable_predictions += len(block)

        print(
            f"\nBlock {block_index}"
        )

        print(
            f"  prediction rows        : "
            f"{len(block):,}"
        )

        print(
            f"  prediction start       : "
            f"{prediction_start}"
        )

        print(
            f"  prediction end         : "
            f"{prediction_end}"
        )

        print(
            f"  T2 historical rows     : "
            f"{len(t2_history):,}"
        )

        print(
            f"  T7 historical rows     : "
            f"{len(t7_history):,}"
        )

        print(
            f"  T2 class counts        : "
            f"{format_counts(counts)}"
        )

        print(
            f"  all five T2 classes    : "
            f"{all_five_classes}"
        )

        print(
            f"  block usable           : "
            f"{block_usable}"
        )

    print(
        f"\nDesign overall status: "
        f"{'USABLE' if design_usable else 'NOT USABLE'}"
    )

    print(
        f"Potential OoF population "
        f"(blocks 2..{n_blocks}): "
        f"{total_usable_predictions:,}"
    )

    return {
        "n_blocks": n_blocks,
        "usable": design_usable,
        "blocks": blocks,
        "potential_oof_population": total_usable_predictions,
    }


design_results = {}

for n_blocks in [3, 4, 5]:

    design_results[n_blocks] = audit_design(
        n_blocks
    )


# ============================================================================
# 13. First all-five-class historical point
# ============================================================================

header(
    "MOD-028 — 13. T2 CLASS-COVERAGE WARM-UP POINT"
)

seen = set()
first_all_classes = None

for position, row in common.iterrows():

    matching = t2_train[
        t2_train["_id_str"]
        == row["_id_str"]
    ]

    if len(matching) != 1:
        continue

    target = str(
        matching.iloc[0]["target_priority"]
    )

    seen.add(target)

    if {
        "P1",
        "P2",
        "P3",
        "P4",
        "P5",
    }.issubset(seen):

        first_all_classes = position
        break

if first_all_classes is None:

    print(
        "Could not establish a first all-five-class point."
    )

else:

    row = common.iloc[
        first_all_classes
    ]

    prior_t2 = t2_train[
        t2_train["_creation_utc"]
        < row["_creation_utc"]
    ]

    print(
        f"First common row after all five T2 classes "
        f"have appeared:"
    )

    print(
        f"  common position        : "
        f"{first_all_classes + 1:,}"
    )

    print(
        f"  ID                     : "
        f"{row['_id_str']}"
    )

    print(
        f"  Creation               : "
        f"{row['_creation_utc']}"
    )

    print(
        f"  prior T2 history       : "
        f"{len(prior_t2):,}"
    )

    print(
        f"  prior class counts     : "
        f"{format_counts(class_counts(prior_t2))}"
    )


# ============================================================================
# 14. T7 temporal history
# ============================================================================

header(
    "MOD-028 — 14. T7 TEMPORAL HISTORY"
)

earliest_common = common["_creation_utc"].min()
latest_common = common["_creation_utc"].max()

t7_before_earliest = t7_train[
    t7_train["_creation_utc"]
    < earliest_common
]

t7_before_latest = t7_train[
    t7_train["_creation_utc"]
    < latest_common
]

print(
    f"T7 train before earliest common prediction: "
    f"{len(t7_before_earliest):,}"
)

print(
    f"T7 train before latest common prediction:   "
    f"{len(t7_before_latest):,}"
)

print(
    "\nThis confirms that T7 fold-local training history "
    "must be cut at each prediction boundary."
)


# ============================================================================
# 15. Native output contract
# ============================================================================

header(
    "MOD-028 — 15. NATIVE OoF OUTPUT CONTRACT"
)

print(
    "T2 output:"
)

print(
    "  ID"
)

print(
    "  predicted_priority"
)

print(
    "  fold/block provenance"
)

print()

print(
    "T7 output:"
)

for column in [
    "ID",
    "predicted_median_survival_seconds",
    "survival_probability_at_211583_seconds",
    "survival_probability_at_1780179_seconds",
    "survival_probability_at_14608619_seconds",
]:

    print(
        f"  {column}"
    )

print(
    "\nT7 duration_seconds and event remain native outcomes, "
    "not predictive evidence."
)


# ============================================================================
# 16. Provenance contract
# ============================================================================

header(
    "MOD-028 — 16. OoF PROVENANCE CONTRACT"
)

print(
    """
Every generated OoF row must retain:

  ID
  prediction_block
  prediction_creation_time
  model_task
  implementation_identifier
  training_start_time
  training_end_time
  training_row_count
  prediction_row_count
  preprocessing_scope
  prediction_boundary

T2 additionally retains the native predicted priority.

T7 additionally retains the native survival outputs.

No synthetic universal T8 target or score is created.
"""
)


# ============================================================================
# 17. Leakage guards
# ============================================================================

header(
    "MOD-028 — 17. LEAKAGE GUARDS"
)

checks = {}

checks["T2 train/test disjoint"] = (
    set(t2_train["_id_str"]).isdisjoint(
        set(t2_test["_id_str"])
    )
)

checks["T2 train/validation disjoint"] = (
    set(t2_train["_id_str"]).isdisjoint(
        set(t2_val["_id_str"])
    )
)

checks["T2 validation/test disjoint"] = (
    set(t2_val["_id_str"]).isdisjoint(
        set(t2_test["_id_str"])
    )
)

checks["T7 train/evaluation disjoint"] = (
    set(t7_train["_id_str"]).isdisjoint(
        set(t7_eval["_id_str"])
    )
)

checks["Common population unique"] = (
    common["_id_str"].is_unique
)

checks["Common population inside T2 train"] = (
    set(common["_id_str"]).issubset(
        set(t2_train["_id_str"])
    )
)

checks["Common population inside T7 train"] = (
    set(common["_id_str"]).issubset(
        set(t7_train["_id_str"])
    )
)

checks["Common population outside T7 evaluation"] = (
    set(common["_id_str"]).isdisjoint(
        set(t7_eval["_id_str"])
    )
)

for name, passed in checks.items():

    print(
        f"{name:52s}: "
        f"{'PASS' if passed else 'FAIL'}"
    )


# ============================================================================
# 18. Candidate design summary
# ============================================================================

header(
    "MOD-028 — 18. CANDIDATE DESIGN SUMMARY"
)

for n_blocks in [3, 4, 5]:

    result = design_results[n_blocks]

    print(
        f"{n_blocks}-block:"
    )

    print(
        f"  eligible               : "
        f"{result['usable']}"
    )

    print(
        f"  potential OoF rows     : "
        f"{result['potential_oof_population']:,}"
    )


# ============================================================================
# 19. Final status
# ============================================================================

header(
    "MOD-028 — FINAL STATUS"
)

print(
    """
This audit intentionally does NOT silently select a fold count.

The final protocol must be frozen using the observed evidence for:

  - chronological ordering,
  - T2 warm-up/class coverage,
  - T7 historical availability,
  - fold-local preprocessing,
  - prediction-block isolation,
  - native task semantics,
  - locked evaluation protection,
  - reproducible provenance.

No model fitting occurred.
No predictions were generated.
No artifacts were modified.
"""
)

print(
    "\nMOD-028 JOINT T2/T7 CHRONOLOGICAL OoF PROTOCOL AUDIT COMPLETE"
)

print(
    "STATUS: REVIEW REQUIRED"
)