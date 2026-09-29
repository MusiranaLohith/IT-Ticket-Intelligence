#!/usr/bin/env python3

import csv
import json
from pathlib import Path


# ============================================================
# T8 MOD-011
# Decision-Question / Fusion-Evaluation Design Audit
#
# READ-ONLY
# No model loading
# No training
# No fusion
# No synthetic target
# No transformed predictions
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

TASK_CLOSURES = {
    "T2": MODELING_ROOT /
    "T2/analysis/t2_final_closure.json",

    "T3": MODELING_ROOT /
    "T3/analysis/t3_final_closure.json",

    "T4": MODELING_ROOT /
    "T4/results/t4_mod013_closure.json",

    "T5": MODELING_ROOT /
    "T5/metrics/t5_mod011_final_closure.json",

    "T7": MODELING_ROOT /
    "T7/metrics/t7_mod012_final_closure.json",
}


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
        return []

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
    result = []

    if isinstance(obj, dict):

        for key, value in obj.items():

            current = (
                f"{prefix}.{key}"
                if prefix
                else str(key)
            )

            result.extend(
                flatten_strings(
                    value,
                    current
                )
            )

    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            current = f"{prefix}[{index}]"

            result.extend(
                flatten_strings(
                    value,
                    current
                )
            )

    elif isinstance(obj, str):

        result.append(
            (prefix, obj)
        )

    return result


# ============================================================
# 1. T8 decision-support layer audit
# ============================================================

print_header(
    "MOD-011 — T8 DECISION-SUPPORT LAYER AUDIT"
)

t8_layers = {
    "Layer A": LAYER_A,
    "Layer B": LAYER_B,
    "Layer C": LAYER_C,
    "Ticket Decision Support": TICKET_DS,
}

for name, path in t8_layers.items():

    header = read_header(path)

    print()
    print(name)
    print(f"Exists: {path.exists()}")
    print(f"Columns: {len(header)}")

    if header:
        print("Key structural fields:")

        for field in header:

            low = field.lower()

            if any(
                token in low
                for token in (
                    "ticket",
                    "query",
                    "candidate",
                    "t2",
                    "t3",
                    "t4",
                    "t5",
                    "t6",
                    "t7",
                    "t8",
                    "creation",
                    "boundary",
                    "provenance",
                    "missing",
                )
            ):
                print(f"  {field}")


# ============================================================
# 2. Task role / target / limitations inventory
# ============================================================

print_header(
    "MOD-011 — COMPLETED TASK ROLE INVENTORY"
)

for task, path in TASK_CLOSURES.items():

    print()
    print(f"--- {task} ---")
    print(f"File: {path}")

    data = load_json(path)

    if data is None:
        print("Closure metadata unavailable.")
        continue

    strings = flatten_strings(data)

    keywords = [
        "task",
        "role",
        "decision",
        "target",
        "evaluation",
        "limitation",
        "unsupported",
        "supported",
        "prediction",
        "signal",
        "downstream",
        "fusion",
        "human",
    ]

    shown = 0

    for key, value in strings:

        low = value.lower()

        if any(
            keyword in low
            for keyword in keywords
        ):

            print(
                f"  {key}: {value}"
            )

            shown += 1

            if shown >= 60:
                print(
                    "  ... output limited to first 60 "
                    "relevant metadata fields ..."
                )
                break


# ============================================================
# 3. T8 conceptual constraints
# ============================================================

print_header(
    "MOD-011 — T8 CONCEPTUAL CONSTRAINTS"
)

constraints = [
    (
        "Universal target",
        "No validated universal ticket-level T8 target "
        "is established."
    ),
    (
        "Missing evidence",
        "Unavailable evidence must remain unavailable; "
        "it is not a negative prediction."
    ),
    (
        "T4 semantics",
        "T4 remains native ranking/retrieval evidence; "
        "ranking scores are not probabilities."
    ),
    (
        "T5 semantics",
        "T5 probability represents duplicate-relationship "
        "existence, not duplicate-ticket identity."
    ),
    (
        "T7 semantics",
        "T7 retains survival duration/event and right-censoring."
    ),
    (
        "T3 addressability",
        "T3 predictions are not currently preserved with "
        "an ID-addressable prediction artifact."
    ),
    (
        "Prediction boundary",
        "Evidence must respect the Creation-time prediction boundary."
    ),
    (
        "Synthetic score",
        "No universal triage/confidence score is defined."
    ),
]

for name, description in constraints:

    print()
    print(f"{name}:")
    print(f"  {description}")


# ============================================================
# 4. Candidate research-question feasibility
# ============================================================

print_header(
    "MOD-011 — RESEARCH-QUESTION FEASIBILITY MATRIX"
)

questions = [
    (
        "Q1",
        "Can T8 produce one universal ticket-level triage "
        "prediction with a single accuracy/F1 target?",
        "NOT ESTABLISHED",
        "No validated universal T8 target exists."
    ),

    (
        "Q2",
        "Can heterogeneous task probabilities/scores be "
        "combined into one universal triage score?",
        "NOT ESTABLISHED",
        "Native outputs have incompatible semantics."
    ),

    (
        "Q3",
        "Can T8 evaluate whether an additional evidence "
        "channel improves a specific native task outcome?",
        "POTENTIALLY FEASIBLE",
        "Requires a common ID-addressable evaluation population "
        "for that native outcome and leakage-safe evidence."
    ),

    (
        "Q4",
        "Can T8 perform native-outcome ablation on a specific "
        "task using additional validated task evidence?",
        "POTENTIALLY FEASIBLE",
        "Requires a defensible overlapping held-out population."
    ),

    (
        "Q5",
        "Can T8 perform descriptive cross-task complementarity "
        "analysis without creating a universal target?",
        "FEASIBLE",
        "Can compare evidence availability and native outcomes "
        "without collapsing task semantics."
    ),

    (
        "Q6",
        "Can T8 evaluate T4 ranking evidence as a probability "
        "feature without calibration/semantic justification?",
        "NOT FEASIBLE AS STATED",
        "T4 output is native ranking/retrieval evidence."
    ),

    (
        "Q7",
        "Can T8 evaluate T7 outputs as an ordinary regression "
        "target such as raw resolution duration?",
        "NOT FEASIBLE AS STATED",
        "T7 contains right-censoring and survival semantics."
    ),

    (
        "Q8",
        "Can the 585-ticket all-four intersection automatically "
        "serve as the definitive T8 fusion evaluation population?",
        "NOT ESTABLISHED",
        "Intersection is descriptive; selection requires an "
        "explicit evaluation rationale."
    ),

    (
        "Q9",
        "Can T3 currently participate in an ID-level fusion "
        "experiment using its preserved final artifacts?",
        "NOT CURRENTLY ESTABLISHED",
        "Per-record predictions exist in execution logic, but "
        "the preserved final artifact is not ID-addressable."
    ),

    (
        "Q10",
        "Can T8 compare evidence-channel combinations against "
        "native task outcomes without claiming causal effects?",
        "POTENTIALLY FEASIBLE",
        "Descriptive/predictive comparison may be possible if "
        "population and temporal provenance are controlled."
    ),
]

for code, question, status, basis in questions:

    print()
    print(f"{code}: {question}")
    print(f"  Status: {status}")
    print(f"  Basis: {basis}")


# ============================================================
# 5. Native-outcome fusion candidates
# ============================================================

print_header(
    "MOD-011 — NATIVE-OUTCOME FUSION CANDIDATE MAP"
)

candidate_map = [
    (
        "T2-native evaluation",
        "Priority",
        "T2",
        "Additional T4/T5/T7 evidence could only be considered "
        "if the exact T2 held-out tickets overlap and the added "
        "signals are legitimately available without leakage."
    ),

    (
        "T4-native evaluation",
        "Assignee ranking/retrieval",
        "T4",
        "Additional evidence could be examined only while "
        "preserving ranking semantics and the T4 evaluation population."
    ),

    (
        "T5-native evaluation",
        "Duplicate relationship existence",
        "T5",
        "Additional evidence could be examined on the exact T5 "
        "evaluation IDs while retaining duplicate-probability semantics."
    ),

    (
        "T7-native evaluation",
        "Time-to-resolution survival",
        "T7",
        "Additional evidence could be examined only with survival "
        "evaluation and censoring preserved."
    ),

    (
        "T3-native evaluation",
        "Severity",
        "T3",
        "Currently blocked for ID-level fusion by missing preserved "
        "ID-addressable prediction output."
    ),
]

for name, outcome, anchor, condition in candidate_map:

    print()
    print(f"{name}")
    print(f"  Native outcome: {outcome}")
    print(f"  Evaluation anchor: {anchor}")
    print(f"  Condition: {condition}")


# ============================================================
# 6. Selection-bias / population warnings
# ============================================================

print_header(
    "MOD-011 — POPULATION / SELECTION WARNINGS"
)

warnings = [
    (
        "Task-specific held-out populations",
        "T2/T4/T5/T7 evaluation sets are different populations."
    ),
    (
        "Sparse all-task overlap",
        "Only 585 canonical tickets contain all four ID-addressable "
        "completed-task prediction artifacts."
    ),
    (
        "Unequal task coverage",
        "T7 covers ~20% of T8 while T2 covers <1%."
    ),
    (
        "Intersection selection",
        "Selecting the all-four intersection solely because it is "
        "the complete intersection may create an unrepresentative "
        "evaluation cohort."
    ),
    (
        "Post-outcome contamination",
        "Native task outcomes cannot become predictors for another "
        "task if they occur after the prediction boundary."
    ),
    (
        "Task-specific target semantics",
        "A native target for one task cannot automatically become "
        "a target for another task."
    ),
]

for name, warning in warnings:

    print()
    print(f"{name}:")
    print(f"  {warning}")


# ============================================================
# 7. Candidate T8 research questions that survive current gate
# ============================================================

print_header(
    "MOD-011 — SURVIVING RESEARCH QUESTIONS"
)

surviving = [
    (
        "R1",
        "Does adding an independently validated evidence channel "
        "provide measurable incremental predictive information for "
        "a specific native task outcome on a defensible overlapping "
        "evaluation population?"
    ),

    (
        "R2",
        "How does native task performance/reliability change when "
        "specific evidence channels are ablated or added, while "
        "preserving the native target semantics?"
    ),

    (
        "R3",
        "What cross-task evidence availability and disagreement "
        "patterns are observable at the Creation-time ticket level "
        "without collapsing heterogeneous outcomes into one label?"
    ),

    (
        "R4",
        "Under what evidence-availability conditions can multiple "
        "validated task signals coexist as decision-support evidence "
        "without treating missing evidence as negative evidence?"
    ),
]

for code, question in surviving:

    print()
    print(f"{code}: {question}")


# ============================================================
# 8. Next-gate requirements
# ============================================================

print_header(
    "MOD-011 — REQUIREMENTS BEFORE ANY FUSION MODEL"
)

requirements = [
    "Select a native outcome/evaluation anchor rather than inventing "
    "a universal T8 target.",

    "Identify the exact held-out evaluation population for that anchor.",

    "Verify every added evidence channel is ID-addressable on that "
    "same population.",

    "Verify every added signal is prediction-time available and does "
    "not use the anchor's post-Creation outcome.",

    "Preserve native output semantics for classification, ranking, "
    "duplicate probability, and survival evidence.",

    "Define an explicit baseline before adding cross-task evidence.",

    "Define ablations before interpreting incremental evidence.",

    "Do not claim causal improvement from observational association "
    "or evidence co-occurrence.",

    "Do not create a universal confidence or triage score before "
    "evaluation semantics justify it.",
]

for index, requirement in enumerate(
    requirements,
    start=1
):

    print(
        f"{index:02d}. {requirement}"
    )


# ============================================================
# 9. Final status
# ============================================================

print_header(
    "MOD-011 — FINAL STATUS"
)

print(
    "No fusion model created."
)

print(
    "No evaluation population selected."
)

print(
    "No universal target created."
)

print(
    "No scores transformed."
)

print(
    "No model loaded."
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
    "MOD-011 COMPLETE"
)