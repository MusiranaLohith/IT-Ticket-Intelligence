from pathlib import Path
import json

import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    log_loss,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T8_ROOT = ROOT / "modeling/T8"

JOINT_OOF = T8_ROOT / "t8_mod029_joint_oof.csv"

OUTPUT_DIR = T8_ROOT / "mod032"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PREDICTIONS_OUT = (
    OUTPUT_DIR /
    "t8_mod032_op002_dev_predictions.csv"
)

METRICS_OUT = (
    OUTPUT_DIR /
    "t8_mod032_op002_dev_metrics.json"
)


T2_FEATURES = [
    "predicted_probability_P1",
    "predicted_probability_P2",
    "predicted_probability_P3",
    "predicted_probability_P4",
    "predicted_probability_P5",
]

T7_FEATURES = [
    "predicted_median_survival_seconds",
    "survival_probability_at_211583_seconds",
    "survival_probability_at_1780179_seconds",
    "survival_probability_at_14608619_seconds",
]

TARGET = "target_priority"

TRAIN_BLOCKS = ["B2", "B3", "B4"]
DEV_BLOCK = "B5"


def make_fusion_pipeline():
    return Pipeline(
        steps=[
            (
                "scaler",
                StandardScaler()
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=2000,
                    solver="lbfgs",
                    class_weight="balanced",
                    C=1.0,
                    random_state=42,
                ),
            ),
        ]
    )


def evaluate_candidate(
    name,
    feature_columns,
    train_df,
    dev_df,
):
    X_train = train_df[feature_columns].astype(float)
    y_train = train_df[TARGET]

    X_dev = dev_df[feature_columns].astype(float)
    y_dev = dev_df[TARGET]

    model = make_fusion_pipeline()

    model.fit(X_train, y_train)

    predictions = model.predict(X_dev)
    probabilities = model.predict_proba(X_dev)

    accuracy = accuracy_score(
        y_dev,
        predictions,
    )

    macro_f1 = f1_score(
        y_dev,
        predictions,
        average="macro",
    )

    weighted_f1 = f1_score(
        y_dev,
        predictions,
        average="weighted",
    )

    logloss = log_loss(
        y_dev,
        probabilities,
        labels=model.classes_,
    )

    return {
        "candidate": name,
        "feature_count": len(feature_columns),
        "features": feature_columns,
        "train_rows": len(train_df),
        "development_rows": len(dev_df),
        "accuracy": float(accuracy),
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "log_loss": float(logloss),
        "predictions": predictions,
        "probabilities": probabilities,
        "classes": model.classes_.tolist(),
    }


print("=" * 100)
print(
    "T8 MOD-032 — OP-002: "
    "CONTROLLED FUSION DEVELOPMENT EXPERIMENT"
)
print("=" * 100)


# ------------------------------------------------------------------
# [1] LOAD OoF DEVELOPMENT ARTIFACT
# ------------------------------------------------------------------

print("\n[1] OoF DEVELOPMENT ARTIFACT")

assert JOINT_OOF.exists()

df = pd.read_csv(
    JOINT_OOF,
    keep_default_na=False,
)

print("Total OoF rows:", len(df))

assert len(df) == 16518
assert df["ID"].nunique() == 16518

print("OoF artifact integrity: PASS")


# ------------------------------------------------------------------
# [2] CHRONOLOGICAL DEVELOPMENT SPLIT
# ------------------------------------------------------------------

print("\n[2] CHRONOLOGICAL FUSION TRAIN/DEVELOPMENT SPLIT")

train_df = df[
    df["prediction_block"].isin(TRAIN_BLOCKS)
].copy()

dev_df = df[
    df["prediction_block"] == DEV_BLOCK
].copy()

print(
    "Fusion training blocks:",
    TRAIN_BLOCKS
)

print(
    "Fusion training rows:",
    len(train_df)
)

print(
    "Development holdout block:",
    DEV_BLOCK
)

print(
    "Development holdout rows:",
    len(dev_df)
)

assert len(train_df) == 12389
assert len(dev_df) == 4129

assert set(
    train_df["ID"]
).isdisjoint(
    set(dev_df["ID"])
)

assert (
    train_df["prediction_creation_time"].max()
    <=
    dev_df["prediction_creation_time"].min()
)

print(
    "Chronological train -> development boundary: PASS"
)


# ------------------------------------------------------------------
# [3] TARGET CONTRACT
# ------------------------------------------------------------------

print("\n[3] NATIVE T2 TARGET")

assert TARGET in df.columns

assert set(
    train_df[TARGET].unique()
).issubset({"P1", "P2", "P3", "P4", "P5"})

assert set(
    dev_df[TARGET].unique()
).issubset({"P1", "P2", "P3", "P4", "P5"})

print("Target:", TARGET)
print("Target semantics: native T2 Priority Prediction")
print("Synthetic T8 target: NO")
print("Target contract: PASS")


# ------------------------------------------------------------------
# [4] CANDIDATE DEFINITIONS
# ------------------------------------------------------------------

print("\n[4] FUSION CANDIDATES")

CANDIDATE_A = T2_FEATURES

CANDIDATE_B = T2_FEATURES + T7_FEATURES

print("Candidate A — T2 only")
print("Feature count:", len(CANDIDATE_A))

for feature in CANDIDATE_A:
    print("  ", feature)

print("\nCandidate B — T2 + T7")
print("Feature count:", len(CANDIDATE_B))

for feature in CANDIDATE_B:
    print("  ", feature)


# ------------------------------------------------------------------
# [5] FEATURE VALIDITY
# ------------------------------------------------------------------

print("\n[5] FEATURE VALIDITY")

for feature in CANDIDATE_B:

    assert feature in train_df.columns
    assert feature in dev_df.columns

    assert (
        pd.to_numeric(
            train_df[feature],
            errors="coerce",
        ).notna().all()
    )

    assert (
        pd.to_numeric(
            dev_df[feature],
            errors="coerce",
        ).notna().all()
    )

print("All candidate features numeric and complete: PASS")


# ------------------------------------------------------------------
# [6] LEAKAGE / ROLE GUARD
# ------------------------------------------------------------------

print("\n[6] FEATURE ROLE GUARD")

FORBIDDEN = [
    "ID",
    "target_priority",
    "duration_seconds",
    "event",
    "prediction_block",
    "prediction_creation_time",
    "prediction_boundary",
    "t2_implementation_identifier",
    "t7_implementation_identifier",
    "t2_preprocessing_scope",
    "t7_preprocessing_scope",
]

used_features = set(CANDIDATE_B)

for feature in FORBIDDEN:
    assert feature not in used_features

print("Outcome fields excluded: PASS")
print("Target excluded from predictors: PASS")
print("Identifiers excluded: PASS")
print("Temporal/provenance metadata excluded: PASS")


# ------------------------------------------------------------------
# [7] TRAIN CANDIDATE A
# ------------------------------------------------------------------

print("\n[7] TRAINING CANDIDATE A")

result_a = evaluate_candidate(
    "A_T2_ONLY",
    CANDIDATE_A,
    train_df,
    dev_df,
)

print(
    "Candidate A accuracy:",
    result_a["accuracy"]
)

print(
    "Candidate A macro-F1:",
    result_a["macro_f1"]
)

print(
    "Candidate A weighted-F1:",
    result_a["weighted_f1"]
)

print(
    "Candidate A log-loss:",
    result_a["log_loss"]
)


# ------------------------------------------------------------------
# [8] TRAIN CANDIDATE B
# ------------------------------------------------------------------

print("\n[8] TRAINING CANDIDATE B")

result_b = evaluate_candidate(
    "B_T2_PLUS_T7",
    CANDIDATE_B,
    train_df,
    dev_df,
)

print(
    "Candidate B accuracy:",
    result_b["accuracy"]
)

print(
    "Candidate B macro-F1:",
    result_b["macro_f1"]
)

print(
    "Candidate B weighted-F1:",
    result_b["weighted_f1"]
)

print(
    "Candidate B log-loss:",
    result_b["log_loss"]
)


# ------------------------------------------------------------------
# [9] DIRECT DEVELOPMENT COMPARISON
# ------------------------------------------------------------------

print("\n[9] DEVELOPMENT COMPARISON")

accuracy_delta = (
    result_b["accuracy"]
    -
    result_a["accuracy"]
)

macro_f1_delta = (
    result_b["macro_f1"]
    -
    result_a["macro_f1"]
)

weighted_f1_delta = (
    result_b["weighted_f1"]
    -
    result_a["weighted_f1"]
)

logloss_delta = (
    result_b["log_loss"]
    -
    result_a["log_loss"]
)

print(
    "Candidate B - Candidate A accuracy:",
    accuracy_delta
)

print(
    "Candidate B - Candidate A macro-F1:",
    macro_f1_delta
)

print(
    "Candidate B - Candidate A weighted-F1:",
    weighted_f1_delta
)

print(
    "Candidate B - Candidate A log-loss:",
    logloss_delta
)


# ------------------------------------------------------------------
# [10] SAVE DEVELOPMENT PREDICTIONS
# ------------------------------------------------------------------

print("\n[10] SAVE DEVELOPMENT PREDICTIONS")

prediction_output = pd.DataFrame(
    {
        "ID": dev_df["ID"].astype(str),
        "prediction_block": dev_df[
            "prediction_block"
        ].astype(str),
        "target_priority": dev_df[
            TARGET
        ].astype(str),

        "candidate_A_prediction": result_a[
            "predictions"
        ].astype(str),

        "candidate_B_prediction": result_b[
            "predictions"
        ].astype(str),
    }
)

for index, class_name in enumerate(
    result_a["classes"]
):
    prediction_output[
        f"candidate_A_probability_{class_name}"
    ] = result_a["probabilities"][:, index]

for index, class_name in enumerate(
    result_b["classes"]
):
    prediction_output[
        f"candidate_B_probability_{class_name}"
    ] = result_b["probabilities"][:, index]

prediction_output.to_csv(
    PREDICTIONS_OUT,
    index=False,
)

assert len(prediction_output) == 4129
assert prediction_output["ID"].nunique() == 4129

print(
    "Development predictions written:",
    PREDICTIONS_OUT
)


# ------------------------------------------------------------------
# [11] SAVE METRICS
# ------------------------------------------------------------------

print("\n[11] SAVE METRICS")

metrics = {
    "module": "T8-MOD-032",
    "operation": "OP-002",
    "development_population": 16518,
    "fusion_training_blocks": TRAIN_BLOCKS,
    "fusion_training_rows": 12389,
    "development_holdout_block": DEV_BLOCK,
    "development_holdout_rows": 4129,
    "target": TARGET,
    "candidate_A": {
        "name": result_a["candidate"],
        "features": result_a["features"],
        "accuracy": result_a["accuracy"],
        "macro_f1": result_a["macro_f1"],
        "weighted_f1": result_a["weighted_f1"],
        "log_loss": result_a["log_loss"],
    },
    "candidate_B": {
        "name": result_b["candidate"],
        "features": result_b["features"],
        "accuracy": result_b["accuracy"],
        "macro_f1": result_b["macro_f1"],
        "weighted_f1": result_b["weighted_f1"],
        "log_loss": result_b["log_loss"],
    },
    "delta_B_minus_A": {
        "accuracy": accuracy_delta,
        "macro_f1": macro_f1_delta,
        "weighted_f1": weighted_f1_delta,
        "log_loss": logloss_delta,
    },
    "locked_evaluation_used": False,
    "synthetic_t8_target_created": False,
    "universal_t8_score_created": False,
}

with METRICS_OUT.open(
    "w",
    encoding="utf-8",
) as f:
    json.dump(
        metrics,
        f,
        indent=2,
    )

print(
    "Metrics written:",
    METRICS_OUT
)


# ------------------------------------------------------------------
# [12] FINAL STATUS
# ------------------------------------------------------------------

print("\n" + "=" * 100)
print("MOD-032 OP-002 COMPLETE")
print("=" * 100)

print("Candidate A trained: PASS")
print("Candidate B trained: PASS")
print("Chronological development holdout: PASS")
print("Locked evaluation used: NO")
print("Development predictions saved: PASS")
print("Development metrics saved: PASS")

print("\nNo locked evaluation result has been produced.")
print("Final T8 evidence-addition conclusion is NOT yet made.")
print("=" * 100)