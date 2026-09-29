from pathlib import Path
import json
import sys

import joblib
import numpy as np
import pandas as pd


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T1_DIR = ROOT / "modeling" / "T1"

SPLIT_PATH = T1_DIR / "splits" / "t1_split.csv"
MODEL_PATH = T1_DIR / "baselines" / "t1_it_support_char_svm.joblib"

EXPECTED_DEVELOPMENT = 1783
EXPECTED_EVALUATION = 446


def fail(message):
    print(f"STATUS: BLOCKED")
    print(message)
    sys.exit(1)


print("=" * 76)
print("FMP-01 / T1 DEVELOPMENT-ONLY CALIBRATION FEASIBILITY")
print("=" * 76)

# -------------------------------------------------------------------------
# 1. LOAD CONTROLLED MODELING SPLIT
# -------------------------------------------------------------------------
print("\n" + "-" * 76)
print("1. CONTROLLED DEVELOPMENT POPULATION")
print("-" * 76)

split = pd.read_csv(SPLIT_PATH)

required_columns = {
    "id",
    "text",
    "category_truth",
    "source_partition",
    "modeling_split",
}

missing = required_columns - set(split.columns)

if missing:
    fail(f"Missing required columns: {sorted(missing)}")

development = split[split["modeling_split"] == "development"].copy()
evaluation = split[split["modeling_split"] == "evaluation"].copy()

print(f"development_records={len(development)}")
print(f"evaluation_records={len(evaluation)}")

if len(development) != EXPECTED_DEVELOPMENT:
    fail(
        f"Expected {EXPECTED_DEVELOPMENT} development records, "
        f"found {len(development)}"
    )

if len(evaluation) != EXPECTED_EVALUATION:
    fail(
        f"Expected {EXPECTED_EVALUATION} evaluation records, "
        f"found {len(evaluation)}"
    )

print("Development/evaluation split: PASS")

# -------------------------------------------------------------------------
# 2. LOAD SERIALIZED ARTIFACT
# -------------------------------------------------------------------------
print("\n" + "-" * 76)
print("2. MODEL ARTIFACT")
print("-" * 76)

artifact = joblib.load(MODEL_PATH)

if not isinstance(artifact, dict):
    fail(f"Expected dictionary artifact, found {type(artifact)}")

model = artifact.get("model")
features = artifact.get("features")

print(f"model_type={type(model)}")
print(f"features_type={type(features)}")

if model is None:
    fail("Serialized artifact does not contain 'model'")

if features is None:
    fail("Serialized artifact does not contain 'features'")

if not hasattr(model, "decision_function"):
    fail("Model does not expose decision_function()")

if not hasattr(model, "predict"):
    fail("Model does not expose predict()")

print("LinearSVC prediction interface: PASS")

# -------------------------------------------------------------------------
# 3. DEVELOPMENT-ONLY TRANSFORMATION
# -------------------------------------------------------------------------
print("\n" + "-" * 76)
print("3. DEVELOPMENT-ONLY SCORE EXTRACTION")
print("-" * 76)

X_dev = development["text"].fillna("").astype(str)
y_dev = development["category_truth"].astype(str)

# Transform only development records.
X_dev_features = features.transform(X_dev)

print(f"development_feature_rows={X_dev_features.shape[0]}")
print(f"development_feature_columns={X_dev_features.shape[1]}")

if X_dev_features.shape[0] != EXPECTED_DEVELOPMENT:
    fail("Development feature transformation row count mismatch")

# -------------------------------------------------------------------------
# 4. DEVELOPMENT PREDICTIONS + DECISION SCORES
# -------------------------------------------------------------------------
print("\n" + "-" * 76)
print("4. DEVELOPMENT PREDICTION / DECISION SCORE ANALYSIS")
print("-" * 76)

pred_dev = model.predict(X_dev_features)
scores_dev = model.decision_function(X_dev_features)

print(f"prediction_shape={np.asarray(pred_dev).shape}")
print(f"decision_score_shape={np.asarray(scores_dev).shape}")

classes = np.asarray(model.classes_)
print(f"class_count={len(classes)}")
print(f"classes={classes}")

if len(pred_dev) != EXPECTED_DEVELOPMENT:
    fail("Development prediction count mismatch")

if scores_dev.shape[0] != EXPECTED_DEVELOPMENT:
    fail("Development decision score row count mismatch")

# LinearSVC multiclass normally gives one score per class.
if scores_dev.ndim != 2:
    fail(
        "Unexpected decision_function dimensionality. "
        f"Expected 2D multiclass scores, found ndim={scores_dev.ndim}"
    )

if scores_dev.shape[1] != len(classes):
    fail(
        "Decision-score class dimension does not match model classes: "
        f"scores={scores_dev.shape[1]}, classes={len(classes)}"
    )

# -------------------------------------------------------------------------
# 5. BASIC DEVELOPMENT PERFORMANCE SANITY
# -------------------------------------------------------------------------
print("\n" + "-" * 76)
print("5. DEVELOPMENT SCORE SANITY")
print("-" * 76)

development_accuracy = float(np.mean(pred_dev == y_dev.to_numpy()))

print(f"development_accuracy={development_accuracy:.6f}")

print("\nPredicted class distribution:")
print(
    pd.Series(pred_dev)
    .value_counts()
    .sort_index()
    .to_string()
)

# -------------------------------------------------------------------------
# 6. TOP-1 / TOP-2 SCORE MARGIN
# -------------------------------------------------------------------------
print("\n" + "-" * 76)
print("6. DEVELOPMENT DECISION MARGINS")
print("-" * 76)

sorted_scores = np.sort(scores_dev, axis=1)

top1 = sorted_scores[:, -1]
top2 = sorted_scores[:, -2]

margin = top1 - top2

print(f"top1_min={float(np.min(top1)):.6f}")
print(f"top1_median={float(np.median(top1)):.6f}")
print(f"top1_max={float(np.max(top1)):.6f}")

print(f"margin_min={float(np.min(margin)):.6f}")
print(f"margin_median={float(np.median(margin)):.6f}")
print(f"margin_max={float(np.max(margin)):.6f}")

# -------------------------------------------------------------------------
# 7. CORRECT VS INCORRECT DEVELOPMENT SCORE SEPARATION
# -------------------------------------------------------------------------
print("\n" + "-" * 76)
print("7. CORRECT / INCORRECT SCORE SEPARATION")
print("-" * 76)

correct = pred_dev == y_dev.to_numpy()

if correct.any():
    print(
        f"correct_count={int(correct.sum())}"
    )
    print(
        f"correct_margin_median="
        f"{float(np.median(margin[correct])):.6f}"
    )
    print(
        f"correct_margin_mean="
        f"{float(np.mean(margin[correct])):.6f}"
    )

if (~correct).any():
    print(
        f"incorrect_count={int((~correct).sum())}"
    )
    print(
        f"incorrect_margin_median="
        f"{float(np.median(margin[~correct])):.6f}"
    )
    print(
        f"incorrect_margin_mean="
        f"{float(np.mean(margin[~correct])):.6f}"
    )

# -------------------------------------------------------------------------
# 8. DEVELOPMENT-ONLY MARGIN BANDS
# -------------------------------------------------------------------------
print("\n" + "-" * 76)
print("8. DEVELOPMENT-ONLY REVIEW-BAND DIAGNOSTIC")
print("-" * 76)

quantiles = [0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]

print("margin_quantiles")

for q in quantiles:
    print(
        f"q={q:.2f} "
        f"value={float(np.quantile(margin, q)):.6f}"
    )

# -------------------------------------------------------------------------
# 9. NO CALIBRATION FITTING
# -------------------------------------------------------------------------
print("\n" + "-" * 76)
print("9. CALIBRATION / THRESHOLD PROTECTION")
print("-" * 76)

print("Calibration model fitted: NO")
print("Probability calibration selected: NO")
print("Review threshold selected: NO")
print("Locked evaluation records used: NO")
print("Evaluation predictions generated: NO")
print("Existing model artifact modified: NO")

# -------------------------------------------------------------------------
# 10. FEASIBILITY INTERPRETATION
# -------------------------------------------------------------------------
print("\n" + "-" * 76)
print("10. FEASIBILITY STATUS")
print("-" * 76)

print(
    "Decision scores are available for development-only "
    "task-specific reliability/review analysis."
)

print(
    "This operation does NOT establish a calibrated probability, "
    "a production review threshold, or an autonomous decision boundary."
)

print(
    "Further calibration/review-boundary work is justified only if "
    "the final T1 system actually requires such an interface."
)

print("\nSTATUS: PASS")
print(
    "Development-only T1 decision-score feasibility was established "
    "without using the locked evaluation population."
)

print("\n" + "=" * 76)
print("END OF FMP-01 / T1 DEVELOPMENT-ONLY CALIBRATION FEASIBILITY")
print("=" * 76)