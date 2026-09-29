#!/usr/bin/env python3

import csv
from pathlib import Path

csv.field_size_limit(1024 * 1024 * 1024)

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
DATA_ROOT = Path("/run/media/whiteblack/User 1/Datasets/Mozilla_CORE")

T2_TRAIN = PROJECT_ROOT / "modeling/T2/splits/train.csv"
T2_EVAL = PROJECT_ROOT / "modeling/T2/splits/test.csv"
T2_PRED = PROJECT_ROOT / "modeling/T2/analysis/t2_final_test_predictions.csv"

T4_TRAIN = PROJECT_ROOT / "modeling/T4/derived/t4_train.csv"
T4_EVAL = PROJECT_ROOT / "modeling/T4/derived/t4_eval.csv"
T4_PRED = PROJECT_ROOT / "modeling/T4/results/r1_checkpoints/t4_r1_topk_predictions.npz"

T5_TRAIN = PROJECT_ROOT / "modeling/T5/splits/t5_model_train.csv"
T5_EVAL = DATA_ROOT / "DTM-002_T5_EVAL_GROUP_AWARE.csv"
T5_PRED = PROJECT_ROOT / "modeling/T5/metrics/t5_mod009_locked_evaluation_predictions.npz"

T7_TRAIN = PROJECT_ROOT / "modeling/T7/splits/t7_train.csv"
T7_EVAL = PROJECT_ROOT / "modeling/T7/splits/t7_evaluation.csv"
T7_PRED = PROJECT_ROOT / "modeling/T7/derived/t7_mod010_evaluation_predictions.csv"


def read_csv(path):
    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return rows, reader.fieldnames or []


def ids_from_rows(rows, field="ID"):
    return {
        r[field].strip()
        for r in rows
        if r.get(field, "").strip()
    }


def read_ids(path):
    rows, fields = read_csv(path)

    field = "ID" if "ID" in fields else "ticket_id"

    return {
        r[field].strip()
        for r in rows
        if r.get(field, "").strip()
    }


def clean_pair(anchor_eval, auxiliary_train, auxiliary_eval):
    return (
        anchor_eval - auxiliary_train
    ) & auxiliary_eval


def clean_multi(anchor_eval, auxiliary_trains, auxiliary_evals):
    clean = set(anchor_eval)

    for train_ids in auxiliary_trains:
        clean -= train_ids

    prediction_available = set(anchor_eval)

    for eval_ids in auxiliary_evals:
        prediction_available &= eval_ids

    return clean, clean & prediction_available


def status_line(status):
    return f"[{status}]"


print("=" * 78)
print("MOD-016 — EVIDENCE-ADDITION / ABLATION DESIGN AUDIT")
print("=" * 78)


# ---------------------------------------------------------------------------
# Load populations
# ---------------------------------------------------------------------------

t2_train = read_ids(T2_TRAIN)
t2_eval_rows, _ = read_csv(T2_EVAL)
t2_eval = ids_from_rows(t2_eval_rows)

t4_train = read_ids(T4_TRAIN)
t4_eval_rows, _ = read_csv(T4_EVAL)
t4_eval = ids_from_rows(t4_eval_rows)

t5_train = read_ids(T5_TRAIN)
t5_eval_rows, _ = read_csv(T5_EVAL)
t5_eval = ids_from_rows(t5_eval_rows)

t7_train = read_ids(T7_TRAIN)
t7_eval_rows, _ = read_csv(T7_EVAL)
t7_eval = ids_from_rows(t7_eval_rows)


evals = {
    "T2": t2_eval,
    "T4": t4_eval,
    "T5": t5_eval,
    "T7": t7_eval,
}

trains = {
    "T2": t2_train,
    "T4": t4_train,
    "T5": t5_train,
    "T7": t7_train,
}

pred_paths = {
    "T2": T2_PRED,
    "T4": T4_PRED,
    "T5": T5_PRED,
    "T7": T7_PRED,
}

print("\nNative populations:")
for task in ["T2", "T4", "T5", "T7"]:
    print(
        f"  {task}: "
        f"train={len(trains[task])}, "
        f"eval={len(evals[task])}"
    )


# ---------------------------------------------------------------------------
# Prediction artifact existence
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-016 — PREDICTION ARTIFACT AVAILABILITY")
print("=" * 78)

for task in ["T2", "T4", "T5", "T7"]:
    print(
        f"  {task}: "
        f"{status_line('AVAILABLE' if pred_paths[task].exists() else 'MISSING')} "
        f"{pred_paths[task]}"
    )


# ---------------------------------------------------------------------------
# Native metric contracts
# ---------------------------------------------------------------------------

native_contracts = {
    "T2": {
        "outcome": "priority",
        "metric": "native multiclass classification metric",
        "semantic": "hard-label priority prediction",
    },
    "T4": {
        "outcome": "assignee",
        "metric": "native ranking/retrieval metric",
        "semantic": "Top-K candidate ranking",
    },
    "T5": {
        "outcome": "duplicate_relationship",
        "metric": "Average Precision / PR-AUC-compatible ranking metric",
        "semantic": "duplicate relationship existence",
    },
    "T7": {
        "outcome": "time_to_resolution",
        "metric": "survival-native metric",
        "semantic": "right-censored survival prediction",
    },
}


print("\n" + "=" * 78)
print("MOD-016 — NATIVE METRIC CONTRACTS")
print("=" * 78)

for task, contract in native_contracts.items():
    print(f"\n{task}")
    print(f"  outcome:  {contract['outcome']}")
    print(f"  metric:   {contract['metric']}")
    print(f"  semantic: {contract['semantic']}")


# ---------------------------------------------------------------------------
# Pairwise candidate matrix
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-016 — PAIRWISE EVIDENCE-ADDITION MATRIX")
print("=" * 78)

pair_results = []

for anchor in ["T2", "T4", "T5", "T7"]:

    print(f"\nANCHOR {anchor}")
    print("-" * 60)

    for auxiliary in ["T2", "T4", "T5", "T7"]:

        if auxiliary == anchor:
            continue

        anchor_eval = evals[anchor]
        auxiliary_train = trains[auxiliary]
        auxiliary_eval = evals[auxiliary]

        clean_anchor = anchor_eval - auxiliary_train
        clean_prediction_cohort = (
            clean_anchor & auxiliary_eval
        )

        anchor_prediction_available = (
            anchor_eval & evals[anchor]
        )

        anchor_prediction_cohort = (
            clean_prediction_cohort & anchor_prediction_available
        )

        contamination = (
            len(anchor_eval & auxiliary_train)
        )

        print(f"\n  {anchor} + {auxiliary}")
        print(f"    anchor evaluation:           {len(anchor_eval)}")
        print(f"    auxiliary train overlap:     {contamination}")
        print(f"    clean anchor population:     {len(clean_anchor)}")
        print(f"    common prediction cohort:    {len(anchor_prediction_cohort)}")

        # ---------------------------------------------------------------
        # Semantic compatibility
        # ---------------------------------------------------------------

        if anchor == "T4":
            semantic = "VALID — preserve ranking/retrieval semantics"

        elif anchor == "T7":
            semantic = "VALID — preserve survival/censoring semantics"

        elif anchor == "T5":
            semantic = (
                "VALID — preserve duplicate-relationship probability semantics"
            )

        elif anchor == "T2":
            semantic = "VALID — preserve native priority classification semantics"

        else:
            semantic = "NOT ESTABLISHED"

        # ---------------------------------------------------------------
        # Candidate status
        # ---------------------------------------------------------------

        if len(anchor_prediction_cohort) == 0:
            status = "NOT ESTABLISHED"

        elif contamination > 0 and len(clean_prediction_cohort) > 0:
            status = "VALID_WITH_RESTRICTION"

        else:
            status = "VALID"

        pair_results.append(
            {
                "anchor": anchor,
                "auxiliary": auxiliary,
                "anchor_eval": len(anchor_eval),
                "aux_train_overlap": contamination,
                "clean_anchor": len(clean_anchor),
                "prediction_cohort": len(anchor_prediction_cohort),
                "status": status,
            }
        )

        print(f"    semantic contract:            {semantic}")
        print(f"    design status:                {status_line(status)}")


# ---------------------------------------------------------------------------
# Multi-channel candidates
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-016 — MULTI-CHANNEL ABLATION CANDIDATES")
print("=" * 78)


multi_candidates = [
    ("T2", ["T4", "T7"]),
    ("T2", ["T5", "T7"]),
    ("T2", ["T4", "T5"]),
    ("T2", ["T4", "T5", "T7"]),

    ("T4", ["T2", "T7"]),
    ("T4", ["T5", "T7"]),
    ("T4", ["T2", "T5"]),
    ("T4", ["T2", "T5", "T7"]),

    ("T5", ["T2", "T7"]),
    ("T5", ["T4", "T7"]),
    ("T5", ["T2", "T4"]),
    ("T5", ["T2", "T4", "T7"]),

    ("T7", ["T2", "T4"]),
    ("T7", ["T2", "T5"]),
    ("T7", ["T4", "T5"]),
    ("T7", ["T2", "T4", "T5"]),
]


for anchor, auxiliaries in multi_candidates:

    train_sets = [
        trains[x]
        for x in auxiliaries
    ]

    eval_sets = [
        evals[x]
        for x in auxiliaries
    ]

    clean_anchor, prediction_cohort = clean_multi(
        evals[anchor],
        train_sets,
        eval_sets
    )

    contamination_tasks = [
        task
        for task in auxiliaries
        if evals[anchor] & trains[task]
    ]

    print(f"\n{anchor} + {' + '.join(auxiliaries)}")
    print(
        f"  clean anchor population: "
        f"{len(clean_anchor)}"
    )
    print(
        f"  common prediction cohort: "
        f"{len(prediction_cohort)}"
    )

    if contamination_tasks:
        print(
            "  training-overlap restrictions: "
            + ", ".join(contamination_tasks)
        )
    else:
        print(
            "  training-overlap restrictions: NONE"
        )

    if len(prediction_cohort) == 0:
        status = "NOT ESTABLISHED"
    else:
        status = "VALID"

    print(f"  design status: {status_line(status)}")


# ---------------------------------------------------------------------------
# Explicit invalid transformations
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-016 — EXPLICITLY INVALID FUSION OPERATIONS")
print("=" * 78)

invalid_operations = [
    "Average T2/T5/T7 probabilities into a universal triage score",
    "Convert T4 ranking scores into probabilities without a validated mapping",
    "Convert T7 survival output into ordinary regression output",
    "Convert T7 event/censoring into an ordinary binary classification target",
    "Treat unavailable auxiliary evidence as negative evidence",
    "Use T5 p_duplicate as duplicate-ticket identity",
    "Use T4 ranking output as an autonomous assignee assignment",
    "Create a synthetic universal T8 target solely to enable fusion accuracy",
    "Compare anchor and fused models on different evaluation populations",
    "Use post-Creation outcomes as Creation-time predictive features",
]

for item in invalid_operations:
    print(f"  PROHIBITED: {item}")


# ---------------------------------------------------------------------------
# Ablation design principles
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-016 — ABLATION DESIGN CONTRACT")
print("=" * 78)

print("""
For every proposed native-anchor experiment:

  A. Anchor-only baseline
     Evaluate the existing native prediction on the exact clean cohort.

  B. Single-evidence addition
     Add exactly one auxiliary evidence channel.

  C. Multi-evidence addition
     Add multiple channels only where the common clean cohort is established.

  D. Same population
     Anchor-only and augmented evaluations must use identical ticket IDs.

  E. Native outcome
     Improvement is measured against the anchor's native outcome,
     not against a synthetic universal T8 target.

  F. Native semantics
     T2 remains classification.
     T4 remains ranking/retrieval.
     T5 remains duplicate-relationship probability.
     T7 remains survival analysis.

  G. No causal interpretation
     An observed improvement demonstrates predictive/evaluative association,
     not that the auxiliary evidence causes the improvement.

  H. Missing evidence
     Missing auxiliary evidence is unavailable evidence, not a negative
     observation.
""")


# ---------------------------------------------------------------------------
# Final summary
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("MOD-016 — DESIGN SUMMARY")
print("=" * 78)

valid_pairs = [
    x for x in pair_results
    if x["status"] in {
        "VALID",
        "VALID_WITH_RESTRICTION",
    }
]

print(f"  pairwise candidate designs: {len(pair_results)}")
print(f"  pairwise viable designs:   {len(valid_pairs)}")

print("\nRecommended evaluation principle:")
print(
    "  Select native anchors based on "
    "ID-addressability + clean provenance + "
    "native metric compatibility + cohort composition."
)

print("\nNo fusion model created.")
print("No score transformed.")
print("No target created.")
print("No model loaded.")
print("No training performed.")
print("No artifact modified.")

print("\n" + "=" * 78)
print("MOD-016 — INTEGRITY CHECKS")
print("=" * 78)

checks = [
    (
        "All native anchors have evaluation populations",
        all(len(evals[t]) > 0 for t in evals)
    ),
    (
        "All native prediction artifacts exist",
        all(pred_paths[t].exists() for t in pred_paths)
    ),
    (
        "All pairwise candidate cohorts are subsets of anchor evaluation",
        all(
            (
                (evals[r["anchor"]] - trains[r["auxiliary"]])
                & evals[r["auxiliary"]]
            ).issubset(evals[r["anchor"]])
            for r in pair_results
        )
    ),
]

for label, passed in checks:
    print(f"  {label}: {'PASS' if passed else 'FAIL'}")


if all(passed for _, passed in checks):
    print("\nMOD-016 EVIDENCE-ADDITION / ABLATION DESIGN AUDIT COMPLETE")
    print("STATUS: COMPLETE / PASS")
else:
    print("\nMOD-016 INTEGRITY FAILURE")
    print("STATUS: REVIEW REQUIRED")