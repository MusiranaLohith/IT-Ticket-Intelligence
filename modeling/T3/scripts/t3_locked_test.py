import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)


# ============================================================
# T3-MOD-027
# Locked Test Evaluation
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "modeling/T3/models/t3_class_weighted_tfidf_logreg.joblib"
)

TEST_PATH = (
    PROJECT_ROOT
    / "modeling/T3/splits/t3_test.csv"
)

OUTPUT_METRICS = (
    PROJECT_ROOT
    / "modeling/T3/metrics/t3_final_test_metrics.json"
)

OUTPUT_ANALYSIS = (
    PROJECT_ROOT
    / "modeling/T3/analysis/t3_locked_test_evaluation.json"
)

LABELS = ["S1", "S2", "S3", "S4"]


print("T3_MOD_027_START")


# ============================================================
# Load selected model artifact
# ============================================================

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"MODEL_NOT_FOUND={MODEL_PATH}"
    )

if not TEST_PATH.exists():
    raise FileNotFoundError(
        f"TEST_SPLIT_NOT_FOUND={TEST_PATH}"
    )

print("LOADING_SELECTED_MODEL=True")

artifact = joblib.load(MODEL_PATH)

if not isinstance(artifact, dict):
    raise RuntimeError(
        "MODEL_ARTIFACT_FORMAT_INVALID"
    )

if "vectorizer" not in artifact:
    raise RuntimeError(
        "VECTORISER_MISSING_FROM_ARTIFACT"
    )

if "model" not in artifact:
    raise RuntimeError(
        "CLASSIFIER_MISSING_FROM_ARTIFACT"
    )

vectorizer = artifact["vectorizer"]
model = artifact["model"]

print(
    f"VECTORIZER_TYPE={type(vectorizer).__name__}"
)

print(
    f"MODEL_TYPE={type(model).__name__}"
)

print("MODEL_ARTIFACT_LOADED=True")


# ============================================================
# Load locked test set
# ============================================================

print("LOADING_LOCKED_TEST=True")

test_df = pd.read_csv(
    TEST_PATH,
    keep_default_na=False,
)

print(f"TEST_ROWS={len(test_df)}")

if len(test_df) != 4626:
    raise RuntimeError(
        f"UNEXPECTED_TEST_ROWS={len(test_df)}"
    )


# ============================================================
# Verify test artifact
# ============================================================

required_columns = {
    "ID",
    "Creation time",
    "Summary",
    "Description",
    "target_severity",
}

if not required_columns.issubset(
    test_df.columns
):
    raise RuntimeError(
        "TEST_COLUMNS_INVALID"
    )

if not set(
    test_df["target_severity"]
).issubset(LABELS):
    raise RuntimeError(
        "TEST_TARGET_VOCABULARY_INVALID"
    )


# ============================================================
# Verify unique IDs
# ============================================================

duplicate_ids = int(
    test_df["ID"].duplicated().sum()
)

print(
    f"DUPLICATE_TEST_IDS={duplicate_ids}"
)

if duplicate_ids != 0:
    raise RuntimeError(
        f"DUPLICATE_TEST_IDS={duplicate_ids}"
    )


# ============================================================
# Build EXACT same text representation
# ============================================================

summary = (
    test_df["Summary"]
    .fillna("")
    .astype(str)
)

description = (
    test_df["Description"]
    .fillna("")
    .astype(str)
)

texts = (
    "Summary: "
    + summary
    + "\nDescription: "
    + description
).tolist()

y_true = (
    test_df["target_severity"]
    .astype(str)
    .tolist()
)


# ============================================================
# LOCKED TEST TRANSFORMATION
#
# IMPORTANT:
# vectorizer.transform() ONLY
# NEVER vectorizer.fit_transform()
# ============================================================

print("TEST_VECTORIZATION_START=True")

X_test = vectorizer.transform(texts)

print(
    f"TEST_FEATURE_SHAPE={X_test.shape}"
)

print("TEST_VECTORIZATION_COMPLETE=True")


# ============================================================
# LOCKED TEST PREDICTION
#
# IMPORTANT:
# classifier.predict() ONLY
# NO FIT
# NO REFIT
# NO RETRAINING
# ============================================================

print("TEST_PREDICTION_START=True")

predictions = model.predict(X_test)

predictions = [
    str(x)
    for x in predictions
]

print("TEST_PREDICTION_COMPLETE=True")


# ============================================================
# Metrics
# ============================================================

accuracy = accuracy_score(
    y_true,
    predictions,
)

macro_f1 = f1_score(
    y_true,
    predictions,
    labels=LABELS,
    average="macro",
    zero_division=0,
)

weighted_f1 = f1_score(
    y_true,
    predictions,
    labels=LABELS,
    average="weighted",
    zero_division=0,
)


precision, recall, f1, support = (
    precision_recall_fscore_support(
        y_true,
        predictions,
        labels=LABELS,
        zero_division=0,
    )
)


cm = confusion_matrix(
    y_true,
    predictions,
    labels=LABELS,
)


true_counts = {
    label: int(
        y_true.count(label)
    )
    for label in LABELS
}

prediction_counts = {
    label: int(
        predictions.count(label)
    )
    for label in LABELS
}


# ============================================================
# Print results
# ============================================================

print(f"ACCURACY={accuracy:.6f}")
print(f"MACRO_F1={macro_f1:.6f}")
print(f"WEIGHTED_F1={weighted_f1:.6f}")

for i, label in enumerate(LABELS):

    print(
        f"{label}_PRECISION="
        f"{precision[i]:.6f}"
    )

    print(
        f"{label}_RECALL="
        f"{recall[i]:.6f}"
    )

    print(
        f"{label}_F1="
        f"{f1[i]:.6f}"
    )

    print(
        f"{label}_SUPPORT="
        f"{support[i]}"
    )


print("TRUE_COUNTS")

for label in LABELS:
    print(
        f"{label}_TRUE="
        f"{true_counts[label]}"
    )


print("PREDICTION_COUNTS")

for label in LABELS:
    print(
        f"{label}_PREDICTED="
        f"{prediction_counts[label]}"
    )


print("CONFUSION_MATRIX")

for row in cm:
    print(
        " ".join(
            str(int(x))
            for x in row
        )
    )


# ============================================================
# Save metrics
# ============================================================

OUTPUT_METRICS.parent.mkdir(
    parents=True,
    exist_ok=True,
)

metrics = {
    "operation": "T3-MOD-027",
    "task": "T3_SEVERITY_PREDICTION",
    "model_id": "T3-MOD-008",
    "model_path": str(MODEL_PATH),
    "test_rows": len(test_df),

    "accuracy": float(accuracy),
    "macro_f1": float(macro_f1),
    "weighted_f1": float(weighted_f1),

    "per_class": {
        LABELS[i]: {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1": float(f1[i]),
            "support": int(support[i]),
        }
        for i in range(len(LABELS))
    },

    "true_counts": true_counts,
    "prediction_counts": prediction_counts,

    "confusion_matrix": cm.tolist(),

    "controls": {
        "retrained": False,
        "refit": False,
        "test_used_for_selection": False,
        "raw_mozilla_accessed": False,
        "dataset_modified": False,
    },
}

with open(
    OUTPUT_METRICS,
    "w",
    encoding="utf-8",
) as f:
    json.dump(
        metrics,
        f,
        indent=2,
    )


# ============================================================
# Save analysis
# ============================================================

OUTPUT_ANALYSIS.parent.mkdir(
    parents=True,
    exist_ok=True,
)

analysis = {
    "operation": "T3-MOD-027",
    "status": "LOCKED_TEST_EVALUATION_COMPLETE",

    "selected_model": "T3-MOD-008",

    "selection_basis": {
        "primary_metric": "macro_f1",
        "validation_macro_f1": 0.348017,
    },

    "test_metrics": {
        "accuracy": float(accuracy),
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
    },

    "test_rows": len(test_df),

    "controls": {
        "model_retrained": False,
        "model_refit": False,
        "test_used_for_selection": False,
        "raw_mozilla_accessed": False,
        "dataset_modified": False,
    },

    "artifacts": {
        "metrics": str(OUTPUT_METRICS),
        "model": str(MODEL_PATH),
    },
}

with open(
    OUTPUT_ANALYSIS,
    "w",
    encoding="utf-8",
) as f:
    json.dump(
        analysis,
        f,
        indent=2,
    )


print(f"MODEL={MODEL_PATH}")
print(f"METRICS={OUTPUT_METRICS}")
print(f"ANALYSIS={OUTPUT_ANALYSIS}")

print("RETRAINED=False")
print("REFIT=False")
print("TEST_USED_FOR_SELECTION=False")
print("RAW_MOZILLA_ACCESSED=False")
print("DATASET_MODIFIED=False")

print("STATUS=LOCKED_TEST_EVALUATION_COMPLETE")
print("T3_MOD_027_COMPLETE")