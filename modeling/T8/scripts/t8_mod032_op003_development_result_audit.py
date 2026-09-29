from pathlib import Path
import json

import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_recall_fscore_support,
)


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T8_ROOT = ROOT / "modeling/T8"
MOD_ROOT = T8_ROOT / "mod032"

PREDICTIONS = (
    MOD_ROOT /
    "t8_mod032_op002_dev_predictions.csv"
)

METRICS = (
    MOD_ROOT /
    "t8_mod032_op002_dev_metrics.json"
)

OUTPUT = (
    MOD_ROOT /
    "t8_mod032_op003_development_audit.json"
)

CLASSES = ["P1", "P2", "P3", "P4", "P5"]


print("=" * 100)
print(
    "T8 MOD-032 — OP-003: "
    "DEVELOPMENT FUSION RESULT / CLASS-BEHAVIOR AUDIT"
)
print("=" * 100)


# ------------------------------------------------------------------
# [1] SOURCE ARTIFACTS
# ------------------------------------------------------------------

print("\n[1] SOURCE ARTIFACTS")

assert PREDICTIONS.exists()
assert METRICS.exists()

pred = pd.read_csv(
    PREDICTIONS,
    keep_default_na=False,
)

with METRICS.open(
    "r",
    encoding="utf-8",
) as f:
    metrics = json.load(f)

print(
    "Development prediction artifact:",
    PREDICTIONS.name,
)

print(
    "Development rows:",
    len(pred),
)

assert len(pred) == 4129
assert pred["ID"].nunique() == 4129

print("Prediction artifact integrity: PASS")


# ------------------------------------------------------------------
# [2] TARGET / PREDICTION VALIDITY
# ------------------------------------------------------------------

print("\n[2] TARGET / PREDICTION VALIDITY")

required = [
    "target_priority",
    "candidate_A_prediction",
    "candidate_B_prediction",
]

for column in required:
    assert column in pred.columns

for column in required:
    assert pred[column].notna().all()

for column in [
    "target_priority",
    "candidate_A_prediction",
    "candidate_B_prediction",
]:
    assert set(pred[column].unique()).issubset(
        set(CLASSES)
    )

print("Target and prediction values: PASS")


# ------------------------------------------------------------------
# [3] SUPPORT / TARGET DISTRIBUTION
# ------------------------------------------------------------------

print("\n[3] TRUE TARGET DISTRIBUTION")

target_counts = (
    pred["target_priority"]
    .value_counts()
    .reindex(CLASSES, fill_value=0)
)

print(target_counts.to_string())

assert int(target_counts.sum()) == 4129


# ------------------------------------------------------------------
# [4] PREDICTED CLASS DISTRIBUTIONS
# ------------------------------------------------------------------

print("\n[4] PREDICTED CLASS DISTRIBUTIONS")

pred_a_counts = (
    pred["candidate_A_prediction"]
    .value_counts()
    .reindex(CLASSES, fill_value=0)
)

pred_b_counts = (
    pred["candidate_B_prediction"]
    .value_counts()
    .reindex(CLASSES, fill_value=0)
)

print("\nCandidate A:")
print(pred_a_counts.to_string())

print("\nCandidate B:")
print(pred_b_counts.to_string())

print("\nCandidate A proportions:")
print(
    (pred_a_counts / len(pred))
    .round(6)
    .to_string()
)

print("\nCandidate B proportions:")
print(
    (pred_b_counts / len(pred))
    .round(6)
    .to_string()
)


# ------------------------------------------------------------------
# [5] CONFUSION MATRICES
# ------------------------------------------------------------------

print("\n[5] CONFUSION MATRICES")

cm_a = confusion_matrix(
    pred["target_priority"],
    pred["candidate_A_prediction"],
    labels=CLASSES,
)

cm_b = confusion_matrix(
    pred["target_priority"],
    pred["candidate_B_prediction"],
    labels=CLASSES,
)

print("\nCandidate A — rows=true, columns=predicted")
print(
    pd.DataFrame(
        cm_a,
        index=CLASSES,
        columns=CLASSES,
    ).to_string()
)

print("\nCandidate B — rows=true, columns=predicted")
print(
    pd.DataFrame(
        cm_b,
        index=CLASSES,
        columns=CLASSES,
    ).to_string()
)


# ------------------------------------------------------------------
# [6] PER-CLASS METRICS
# ------------------------------------------------------------------

print("\n[6] PER-CLASS METRICS")

precision_a, recall_a, f1_a, support_a = (
    precision_recall_fscore_support(
        pred["target_priority"],
        pred["candidate_A_prediction"],
        labels=CLASSES,
        zero_division=0,
    )
)

precision_b, recall_b, f1_b, support_b = (
    precision_recall_fscore_support(
        pred["target_priority"],
        pred["candidate_B_prediction"],
        labels=CLASSES,
        zero_division=0,
    )
)

rows = []

for i, cls in enumerate(CLASSES):

    rows.append(
        {
            "class": cls,
            "support": int(support_a[i]),
            "A_precision": float(precision_a[i]),
            "B_precision": float(precision_b[i]),
            "delta_precision": float(
                precision_b[i] - precision_a[i]
            ),
            "A_recall": float(recall_a[i]),
            "B_recall": float(recall_b[i]),
            "delta_recall": float(
                recall_b[i] - recall_a[i]
            ),
            "A_f1": float(f1_a[i]),
            "B_f1": float(f1_b[i]),
            "delta_f1": float(
                f1_b[i] - f1_a[i]
            ),
        }
    )

class_metrics = pd.DataFrame(rows)

print(
    class_metrics.to_string(
        index=False,
        float_format=lambda x: f"{x:.6f}",
    )
)


# ------------------------------------------------------------------
# [7] AGGREGATE METRIC RECOMPUTATION
# ------------------------------------------------------------------

print("\n[7] AGGREGATE METRICS")

y_true = pred["target_priority"]

a_pred = pred["candidate_A_prediction"]
b_pred = pred["candidate_B_prediction"]

aggregate = {
    "A": {
        "accuracy": float(
            accuracy_score(y_true, a_pred)
        ),
        "macro_f1": float(
            f1_score(
                y_true,
                a_pred,
                average="macro",
            )
        ),
        "weighted_f1": float(
            f1_score(
                y_true,
                a_pred,
                average="weighted",
            )
        ),
    },
    "B": {
        "accuracy": float(
            accuracy_score(y_true, b_pred)
        ),
        "macro_f1": float(
            f1_score(
                y_true,
                b_pred,
                average="macro",
            )
        ),
        "weighted_f1": float(
            f1_score(
                y_true,
                b_pred,
                average="weighted",
            )
        ),
    },
}

for candidate in ["A", "B"]:

    print(
        f"Candidate {candidate}: "
        f"accuracy={aggregate[candidate]['accuracy']:.6f}, "
        f"macro-F1={aggregate[candidate]['macro_f1']:.6f}, "
        f"weighted-F1={aggregate[candidate]['weighted_f1']:.6f}"
    )


# ------------------------------------------------------------------
# [8] PER-TRUE-CLASS LOG-LOSS
# ------------------------------------------------------------------

print("\n[8] PER-TRUE-CLASS PROBABILISTIC LOSS")

prob_a_cols = [
    f"candidate_A_probability_{cls}"
    for cls in CLASSES
]

prob_b_cols = [
    f"candidate_B_probability_{cls}"
    for cls in CLASSES
]

for column in prob_a_cols + prob_b_cols:
    assert column in pred.columns

prob_a = pred[prob_a_cols].astype(float).to_numpy()
prob_b = pred[prob_b_cols].astype(float).to_numpy()

assert np.isfinite(prob_a).all()
assert np.isfinite(prob_b).all()

assert (
    np.abs(prob_a.sum(axis=1) - 1.0)
    < 1e-8
).all()

assert (
    np.abs(prob_b.sum(axis=1) - 1.0)
    < 1e-8
).all()

class_logloss = []

for cls_index, cls in enumerate(CLASSES):

    mask = (
        pred["target_priority"].to_numpy()
        == cls
    )

    true_index = np.full(
        mask.sum(),
        cls_index,
        dtype=int,
    )

    # Extract probability assigned to the actual class.
    p_a = prob_a[mask, cls_index]
    p_b = prob_b[mask, cls_index]

    # Clip only for numerical safety in log calculation.
    p_a = np.clip(p_a, 1e-15, 1.0)
    p_b = np.clip(p_b, 1e-15, 1.0)

    ll_a = float(
        -np.mean(np.log(p_a))
    )

    ll_b = float(
        -np.mean(np.log(p_b))
    )

    class_logloss.append(
        {
            "class": cls,
            "support": int(mask.sum()),
            "A_log_loss": ll_a,
            "B_log_loss": ll_b,
            "delta_B_minus_A": ll_b - ll_a,
        }
    )

class_logloss_df = pd.DataFrame(
    class_logloss
)

print(
    class_logloss_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.6f}",
    )
)


# ------------------------------------------------------------------
# [9] MAJORITY-CLASS CONCENTRATION CHECK
# ------------------------------------------------------------------

print("\n[9] PREDICTION CONCENTRATION CHECK")

majority_class = (
    target_counts
    .idxmax()
)

majority_support = int(
    target_counts.max()
)

a_majority_pred = int(
    pred_a_counts[majority_class]
)

b_majority_pred = int(
    pred_b_counts[majority_class]
)

print(
    "True majority class:",
    majority_class,
)

print(
    "True majority support:",
    majority_support,
)

print(
    "Candidate A predictions of majority class:",
    a_majority_pred,
)

print(
    "Candidate B predictions of majority class:",
    b_majority_pred,
)

print(
    "Candidate A majority prediction proportion:",
    a_majority_pred / len(pred),
)

print(
    "Candidate B majority prediction proportion:",
    b_majority_pred / len(pred),
)


# ------------------------------------------------------------------
# [10] CLASS-WISE F1 CHANGE
# ------------------------------------------------------------------

print("\n[10] CLASS-WISE F1 CHANGE")

for _, row in class_metrics.iterrows():

    direction = (
        "IMPROVED"
        if row["delta_f1"] > 0
        else
        "DECLINED"
        if row["delta_f1"] < 0
        else
        "UNCHANGED"
    )

    print(
        f"{row['class']}: "
        f"{direction} "
        f"({row['delta_f1']:+.6f})"
    )


# ------------------------------------------------------------------
# [11] DEVELOPMENT DECISION EVIDENCE
# ------------------------------------------------------------------

print("\n[11] DEVELOPMENT DECISION EVIDENCE")

macro_delta = (
    aggregate["B"]["macro_f1"]
    -
    aggregate["A"]["macro_f1"]
)

weighted_delta = (
    aggregate["B"]["weighted_f1"]
    -
    aggregate["A"]["weighted_f1"]
)

accuracy_delta = (
    aggregate["B"]["accuracy"]
    -
    aggregate["A"]["accuracy"]
)

print(
    f"Accuracy delta B-A: {accuracy_delta:+.6f}"
)

print(
    f"Macro-F1 delta B-A: {macro_delta:+.6f}"
)

print(
    f"Weighted-F1 delta B-A: {weighted_delta:+.6f}"
)

print(
    "\nThis operation does NOT select a final T8 model."
)

print(
    "It characterizes whether the development accuracy gain "
    "is distributed across classes."
)


# ------------------------------------------------------------------
# [12] SAVE AUDIT
# ------------------------------------------------------------------

audit = {
    "module": "T8-MOD-032",
    "operation": "OP-003",
    "development_rows": len(pred),
    "development_block": "B5",

    "target_distribution": {
        str(k): int(v)
        for k, v in target_counts.items()
    },

    "predicted_distribution_A": {
        str(k): int(v)
        for k, v in pred_a_counts.items()
    },

    "predicted_distribution_B": {
        str(k): int(v)
        for k, v in pred_b_counts.items()
    },

    "confusion_matrix_A": cm_a.tolist(),
    "confusion_matrix_B": cm_b.tolist(),

    "class_metrics": rows,
    "class_log_loss": class_logloss,

    "aggregate": aggregate,

    "deltas": {
        "accuracy": accuracy_delta,
        "macro_f1": macro_delta,
        "weighted_f1": weighted_delta,
    },

    "locked_evaluation_used": False,
    "final_model_selected": False,
}

with OUTPUT.open(
    "w",
    encoding="utf-8",
) as f:
    json.dump(
        audit,
        f,
        indent=2,
    )

print(
    "\nAudit written:",
    OUTPUT,
)


# ------------------------------------------------------------------
# [13] FINAL STATUS
# ------------------------------------------------------------------

print("\n" + "=" * 100)
print("MOD-032 OP-003 COMPLETE")
print("=" * 100)

print("Development class analysis: PASS")
print("Confusion-matrix analysis: PASS")
print("Per-class metric analysis: PASS")
print("Per-class probabilistic-loss analysis: PASS")
print("Prediction-concentration analysis: PASS")
print("Locked evaluation used: NO")
print("Final fusion candidate selected: NO")

print("=" * 100)