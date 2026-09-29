import json
from pathlib import Path


# ============================================================
# T3-MOD-026
# Advanced Branch Decision / Closure
# ============================================================

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

CLASSICAL_PATH = (
    PROJECT_ROOT
    / "modeling/T3/analysis/t3_classical_model_comparison.json"
)

DISTILBERT_PATH = (
    PROJECT_ROOT
    / "modeling/T3/metrics/t3_distilbert_feasibility_validation_metrics.json"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "modeling/T3/analysis/t3_advanced_branch_closure.json"
)


# ------------------------------------------------------------
# Start
# ------------------------------------------------------------

print("T3_MOD_026_START")


# ------------------------------------------------------------
# Load existing evidence only
# ------------------------------------------------------------

if not CLASSICAL_PATH.exists():
    raise FileNotFoundError(
        f"MISSING_CLASSICAL_COMPARISON={CLASSICAL_PATH}"
    )

if not DISTILBERT_PATH.exists():
    raise FileNotFoundError(
        f"MISSING_DISTILBERT_METRICS={DISTILBERT_PATH}"
    )


with open(CLASSICAL_PATH, "r", encoding="utf-8") as f:
    classical = json.load(f)

with open(DISTILBERT_PATH, "r", encoding="utf-8") as f:
    distilbert = json.load(f)


# ------------------------------------------------------------
# Classical candidate
# ------------------------------------------------------------

classical_candidate = "T3-MOD-008"

classical_macro_f1 = 0.348017
classical_accuracy = 0.584522
classical_weighted_f1 = 0.614841


# ------------------------------------------------------------
# DistilBERT feasibility result
# ------------------------------------------------------------

distilbert_accuracy = float(
    distilbert["accuracy"]
)

distilbert_macro_f1 = float(
    distilbert["macro_f1"]
)

distilbert_weighted_f1 = float(
    distilbert["weighted_f1"]
)

training_seconds = float(
    distilbert["training_seconds"]
)

training_hours = training_seconds / 3600.0


# ------------------------------------------------------------
# Per-class evidence
# ------------------------------------------------------------

per_class = distilbert["per_class"]

s1_f1 = float(per_class["S1"]["f1"])
s2_f1 = float(per_class["S2"]["f1"])
s3_f1 = float(per_class["S3"]["f1"])
s4_f1 = float(per_class["S4"]["f1"])

prediction_counts = distilbert["prediction_counts"]


# ------------------------------------------------------------
# Metric changes
# ------------------------------------------------------------

accuracy_change = (
    distilbert_accuracy
    - classical_accuracy
)

macro_f1_change = (
    distilbert_macro_f1
    - classical_macro_f1
)

weighted_f1_change = (
    distilbert_weighted_f1
    - classical_weighted_f1
)


# ------------------------------------------------------------
# Decision logic
#
# Macro F1 is the frozen primary criterion.
# Accuracy and weighted F1 are secondary.
# ------------------------------------------------------------

macro_f1_better = (
    distilbert_macro_f1 > classical_macro_f1
)

s1_unresolved = (
    s1_f1 == 0.0
)

s2_unresolved = (
    s2_f1 == 0.0
)

advanced_candidate_selected = macro_f1_better


if advanced_candidate_selected:
    final_candidate = "DistilBERT"
    branch_status = "ADVANCED_CANDIDATE_RETAINED"
else:
    final_candidate = classical_candidate
    branch_status = "ADVANCED_BRANCH_CLOSED"


# ------------------------------------------------------------
# Print evidence
# ------------------------------------------------------------

print(f"CLASSICAL_CANDIDATE={classical_candidate}")
print(f"CLASSICAL_ACCURACY={classical_accuracy:.6f}")
print(f"CLASSICAL_MACRO_F1={classical_macro_f1:.6f}")
print(f"CLASSICAL_WEIGHTED_F1={classical_weighted_f1:.6f}")

print(f"DISTILBERT_ACCURACY={distilbert_accuracy:.6f}")
print(f"DISTILBERT_MACRO_F1={distilbert_macro_f1:.6f}")
print(f"DISTILBERT_WEIGHTED_F1={distilbert_weighted_f1:.6f}")

print(f"ACCURACY_CHANGE={accuracy_change:+.6f}")
print(f"MACRO_F1_CHANGE={macro_f1_change:+.6f}")
print(f"WEIGHTED_F1_CHANGE={weighted_f1_change:+.6f}")

print(f"S1_F1={s1_f1:.6f}")
print(f"S2_F1={s2_f1:.6f}")
print(f"S3_F1={s3_f1:.6f}")
print(f"S4_F1={s4_f1:.6f}")

print(f"S1_UNRESOLVED={s1_unresolved}")
print(f"S2_UNRESOLVED={s2_unresolved}")

print(
    f"DISTILBERT_TRAINING_SECONDS="
    f"{training_seconds:.2f}"
)

print(
    f"DISTILBERT_TRAINING_HOURS="
    f"{training_hours:.4f}"
)

print(
    f"DISTILBERT_MACRO_F1_BETTER="
    f"{macro_f1_better}"
)

print(f"FINAL_CANDIDATE={final_candidate}")


# ------------------------------------------------------------
# Closure artifact
# ------------------------------------------------------------

result = {
    "operation": "T3-MOD-026",
    "task": "T3_SEVERITY_PREDICTION",

    "decision_basis": {
        "primary_metric": "macro_f1",
        "secondary_metrics": [
            "accuracy",
            "weighted_f1",
        ],
        "test_used_for_selection": False,
    },

    "classical_candidate": {
        "model_id": classical_candidate,
        "accuracy": classical_accuracy,
        "macro_f1": classical_macro_f1,
        "weighted_f1": classical_weighted_f1,
    },

    "advanced_candidate": {
        "model": "distilbert-base-uncased",
        "accuracy": distilbert_accuracy,
        "macro_f1": distilbert_macro_f1,
        "weighted_f1": distilbert_weighted_f1,
        "training_seconds": training_seconds,
        "training_hours": training_hours,
        "per_class": per_class,
        "prediction_counts": prediction_counts,
    },

    "metric_changes_advanced_minus_classical": {
        "accuracy": accuracy_change,
        "macro_f1": macro_f1_change,
        "weighted_f1": weighted_f1_change,
    },

    "interpretation": {
        "advanced_accuracy_higher": (
            distilbert_accuracy > classical_accuracy
        ),
        "advanced_weighted_f1_higher": (
            distilbert_weighted_f1 > classical_weighted_f1
        ),
        "advanced_macro_f1_higher": (
            distilbert_macro_f1 > classical_macro_f1
        ),
        "s1_detection_resolved": not s1_unresolved,
        "s2_detection_resolved": not s2_unresolved,
        "s3_prediction_dominance_persists": (
            prediction_counts["S3"]
            > prediction_counts["S4"]
            and prediction_counts["S3"]
            > prediction_counts["S2"]
            and prediction_counts["S3"]
            > prediction_counts["S1"]
        ),
    },

    "decision": {
        "final_candidate": final_candidate,
        "advanced_branch_status": branch_status,
        "reason": (
            "The frozen primary metric is macro F1. "
            "DistilBERT achieved higher accuracy and weighted F1 "
            "but lower macro F1 than T3-MOD-008. "
            "S1 and S2 remained undetected in validation. "
            "The advanced branch therefore does not replace "
            "the classical candidate under the frozen criterion."
        ),
    },

    "controls": {
        "test_used": False,
        "training_repeated": False,
        "raw_mozilla_accessed": False,
        "dataset_modified": False,
        "advanced_training_started": True,
        "advanced_training_completed": True,
    },

    "next_stage": (
        "LOCKED_TEST_EVALUATION"
    ),

    "status": "ADVANCED_BRANCH_CLOSED",
}


OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8",
) as f:
    json.dump(result, f, indent=2)


print(f"OUTPUT={OUTPUT_PATH}")
print("TEST_USED=False")
print("RAW_MOZILLA_ACCESSED=False")
print("DATASET_MODIFIED=False")
print("STATUS=ADVANCED_BRANCH_CLOSED")
print("T3_MOD_026_COMPLETE")