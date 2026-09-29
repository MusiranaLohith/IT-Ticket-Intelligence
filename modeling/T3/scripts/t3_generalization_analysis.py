import json
from pathlib import Path


# ============================================================
# T3-MOD-028
# Final Generalization & Error Analysis
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

VALIDATION_PATH = (
    PROJECT_ROOT
    / "modeling/T3/metrics/"
      "t3_class_weighted_validation_metrics.json"
)

TEST_PATH = (
    PROJECT_ROOT
    / "modeling/T3/metrics/"
      "t3_final_test_metrics.json"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "modeling/T3/analysis/"
      "t3_final_generalization_analysis.json"
)

LABELS = ["S1", "S2", "S3", "S4"]


# ============================================================
# Start
# ============================================================

print("T3_MOD_028_START")


# ============================================================
# Load existing validation/test evidence
# ============================================================

if not VALIDATION_PATH.exists():
    raise FileNotFoundError(
        f"VALIDATION_METRICS_NOT_FOUND={VALIDATION_PATH}"
    )

if not TEST_PATH.exists():
    raise FileNotFoundError(
        f"TEST_METRICS_NOT_FOUND={TEST_PATH}"
    )


with open(
    VALIDATION_PATH,
    "r",
    encoding="utf-8",
) as f:
    validation = json.load(f)


with open(
    TEST_PATH,
    "r",
    encoding="utf-8",
) as f:
    test = json.load(f)


# ============================================================
# Overall metrics
# ============================================================

validation_accuracy = float(
    validation["accuracy"]
)

validation_macro_f1 = float(
    validation["macro_f1"]
)

validation_weighted_f1 = float(
    validation["weighted_f1"]
)

test_accuracy = float(
    test["accuracy"]
)

test_macro_f1 = float(
    test["macro_f1"]
)

test_weighted_f1 = float(
    test["weighted_f1"]
)


accuracy_change = (
    test_accuracy
    - validation_accuracy
)

macro_f1_change = (
    test_macro_f1
    - validation_macro_f1
)

weighted_f1_change = (
    test_weighted_f1
    - validation_weighted_f1
)


# ============================================================
# Per-class generalization
# ============================================================

per_class = {}

for label in LABELS:

    val_f1 = float(
        validation["per_class"][label]["f1"]
    )

    test_f1 = float(
        test["per_class"][label]["f1"]
    )

    per_class[label] = {
        "validation": validation["per_class"][label],
        "test": test["per_class"][label],
        "f1_change": test_f1 - val_f1,
    }


# ============================================================
# Confusion matrix
# ============================================================

cm = test["confusion_matrix"]

confusion_pairs = []

for actual_index, actual_label in enumerate(LABELS):

    for predicted_index, predicted_label in enumerate(
        LABELS
    ):

        count = int(
            cm[actual_index][predicted_index]
        )

        if (
            actual_label != predicted_label
            and count > 0
        ):
            confusion_pairs.append(
                {
                    "actual": actual_label,
                    "predicted": predicted_label,
                    "count": count,
                }
            )


confusion_pairs.sort(
    key=lambda x: x["count"],
    reverse=True,
)


# ============================================================
# Prediction distribution
# ============================================================

true_counts = test["true_counts"]
prediction_counts = test["prediction_counts"]

total_test = sum(
    int(value)
    for value in true_counts.values()
)

prediction_shares = {
    label: (
        float(prediction_counts[label])
        / total_test
    )
    for label in LABELS
}


# ============================================================
# Key observations
# ============================================================

s1_test_f1 = float(
    test["per_class"]["S1"]["f1"]
)

s2_test_f1 = float(
    test["per_class"]["S2"]["f1"]
)

s3_test_f1 = float(
    test["per_class"]["S3"]["f1"]
)

s4_test_f1 = float(
    test["per_class"]["S4"]["f1"]
)


s1_unsupported = (
    s1_test_f1 == 0.0
)

s3_dominant = (
    prediction_counts["S3"]
    == max(
        prediction_counts.values()
    )
)


# ============================================================
# Print results
# ============================================================

print(
    f"VALIDATION_ACCURACY="
    f"{validation_accuracy:.6f}"
)

print(
    f"TEST_ACCURACY="
    f"{test_accuracy:.6f}"
)

print(
    f"ACCURACY_CHANGE="
    f"{accuracy_change:+.6f}"
)


print(
    f"VALIDATION_MACRO_F1="
    f"{validation_macro_f1:.6f}"
)

print(
    f"TEST_MACRO_F1="
    f"{test_macro_f1:.6f}"
)

print(
    f"MACRO_F1_CHANGE="
    f"{macro_f1_change:+.6f}"
)


print(
    f"VALIDATION_WEIGHTED_F1="
    f"{validation_weighted_f1:.6f}"
)

print(
    f"TEST_WEIGHTED_F1="
    f"{test_weighted_f1:.6f}"
)

print(
    f"WEIGHTED_F1_CHANGE="
    f"{weighted_f1_change:+.6f}"
)


print("PER_CLASS_GENERALIZATION")

for label in LABELS:

    print(
        f"{label}_VAL_F1="
        f"{per_class[label]['validation']['f1']:.6f}"
    )

    print(
        f"{label}_TEST_F1="
        f"{per_class[label]['test']['f1']:.6f}"
    )

    print(
        f"{label}_F1_CHANGE="
        f"{per_class[label]['f1_change']:+.6f}"
    )


print("TOP_TEST_CONFUSIONS")

for item in confusion_pairs[:10]:

    print(
        f"{item['actual']}->"
        f"{item['predicted']}="
        f"{item['count']}"
    )


print("TEST_PREDICTION_SHARES")

for label in LABELS:

    print(
        f"{label}_SHARE="
        f"{prediction_shares[label]:.6f}"
    )


print(
    f"S1_TEST_F1_ZERO={s1_unsupported}"
)

print(
    f"S3_PREDICTION_DOMINANT={s3_dominant}"
)


# ============================================================
# Analysis artifact
# ============================================================

result = {
    "operation": "T3-MOD-028",
    "task": "T3_SEVERITY_PREDICTION",

    "model": "T3-MOD-008",

    "evaluation_design": {
        "validation_rows": int(
            validation.get("validation_rows", 4626)
        ),
        "test_rows": int(
            test["test_rows"]
        ),
        "test_used_for_selection": False,
        "retrained": False,
        "refit": False,
    },

    "overall_generalization": {
        "validation": {
            "accuracy": validation_accuracy,
            "macro_f1": validation_macro_f1,
            "weighted_f1": validation_weighted_f1,
        },

        "test": {
            "accuracy": test_accuracy,
            "macro_f1": test_macro_f1,
            "weighted_f1": test_weighted_f1,
        },

        "test_minus_validation": {
            "accuracy": accuracy_change,
            "macro_f1": macro_f1_change,
            "weighted_f1": weighted_f1_change,
        },
    },

    "per_class_generalization": per_class,

    "test_confusion_pairs": confusion_pairs,

    "test_prediction_distribution": {
        "counts": prediction_counts,
        "shares": prediction_shares,
    },

    "observations": {
        "s1_test_f1_zero": s1_unsupported,
        "s3_prediction_dominant": s3_dominant,
        "test_s1_f1": s1_test_f1,
        "test_s2_f1": s2_test_f1,
        "test_s3_f1": s3_test_f1,
        "test_s4_f1": s4_test_f1,
    },

    "interpretation": {
        "primary_metric": "macro_f1",
        "statement": (
            "The final generalization assessment compares "
            "the selected T3-MOD-008 candidate's validation "
            "metrics with its locked test metrics. "
            "The analysis documents overall and per-class "
            "changes and the structure of test-set "
            "misclassifications without changing the model "
            "or selection decision."
        ),
    },

    "controls": {
        "test_used_for_selection": False,
        "model_retrained": False,
        "model_refit": False,
        "raw_mozilla_accessed": False,
        "dataset_modified": False,
    },

    "status": "GENERALIZATION_ANALYSIS_COMPLETE",
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
    json.dump(
        result,
        f,
        indent=2,
    )


print(f"OUTPUT={OUTPUT_PATH}")
print("TEST_USED_FOR_SELECTION=False")
print("RETRAINED=False")
print("REFIT=False")
print("RAW_MOZILLA_ACCESSED=False")
print("DATASET_MODIFIED=False")
print("STATUS=GENERALIZATION_ANALYSIS_COMPLETE")
print("T3_MOD_028_COMPLETE")