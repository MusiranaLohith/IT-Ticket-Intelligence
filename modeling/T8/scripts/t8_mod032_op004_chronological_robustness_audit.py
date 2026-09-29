from pathlib import Path
import json

import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T8_ROOT = ROOT / "modeling/T8"

JOINT_OOF = T8_ROOT / "t8_mod029_joint_oof.csv"

OUTPUT = (
    T8_ROOT /
    "mod032" /
    "t8_mod032_op004_chronological_robustness.json"
)

PREDICTIONS_OUTPUT = (
    T8_ROOT /
    "mod032" /
    "t8_mod032_op004_chronological_predictions.csv"
)

CLASSES = ["P1", "P2", "P3", "P4", "P5"]

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


def make_model():
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


def evaluate(
    train_df,
    eval_df,
    features,
    candidate_name,
):
    model = make_model()

    model.fit(
        train_df[features].astype(float),
        train_df[TARGET],
    )

    predictions = model.predict(
        eval_df[features].astype(float)
    )

    accuracy = accuracy_score(
        eval_df[TARGET],
        predictions,
    )

    macro_f1 = f1_score(
        eval_df[TARGET],
        predictions,
        average="macro",
    )

    weighted_f1 = f1_score(
        eval_df[TARGET],
        predictions,
        average="weighted",
    )

    per_class_f1 = f1_score(
        eval_df[TARGET],
        predictions,
        labels=CLASSES,
        average=None,
        zero_division=0,
    )

    predicted_counts = (
        pd.Series(predictions)
        .value_counts()
        .reindex(CLASSES, fill_value=0)
    )

    return {
        "candidate": candidate_name,
        "train_rows": len(train_df),
        "evaluation_rows": len(eval_df),
        "accuracy": float(accuracy),
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "per_class_f1": {
            cls: float(per_class_f1[i])
            for i, cls in enumerate(CLASSES)
        },
        "predicted_counts": {
            cls: int(predicted_counts[cls])
            for cls in CLASSES
        },
        "predicted_proportions": {
            cls: float(
                predicted_counts[cls] /
                len(eval_df)
            )
            for cls in CLASSES
        },
        "predictions": predictions,
    }


print("=" * 100)
print(
    "T8 MOD-032 — OP-004: "
    "CHRONOLOGICAL FUSION ROBUSTNESS AUDIT"
)
print("=" * 100)


# ------------------------------------------------------------------
# [1] LOAD
# ------------------------------------------------------------------

print("\n[1] OoF ARTIFACT")

assert JOINT_OOF.exists()

df = pd.read_csv(
    JOINT_OOF,
    keep_default_na=False,
)

assert len(df) == 16518
assert df["ID"].nunique() == 16518

print("Rows:", len(df))
print("Unique IDs:", df["ID"].nunique())
print("Artifact integrity: PASS")


# ------------------------------------------------------------------
# [2] BLOCK STRUCTURE
# ------------------------------------------------------------------

print("\n[2] BLOCK STRUCTURE")

expected = {
    "B2": 4130,
    "B3": 4130,
    "B4": 4129,
    "B5": 4129,
}

for block, expected_count in expected.items():

    actual = int(
        (df["prediction_block"] == block).sum()
    )

    print(
        f"{block}: {actual}"
    )

    assert actual == expected_count

print("Block structure: PASS")


# ------------------------------------------------------------------
# [3] CHRONOLOGICAL EXPERIMENTS
# ------------------------------------------------------------------

experiments = [
    {
        "evaluation_block": "B3",
        "training_blocks": ["B2"],
    },
    {
        "evaluation_block": "B4",
        "training_blocks": ["B2", "B3"],
    },
    {
        "evaluation_block": "B5",
        "training_blocks": ["B2", "B3", "B4"],
    },
]

all_results = []
prediction_rows = []


for experiment in experiments:

    eval_block = experiment["evaluation_block"]
    training_blocks = experiment["training_blocks"]

    print("\n" + "-" * 100)
    print(
        f"Evaluation block: {eval_block}"
    )
    print(
        f"Training blocks: {training_blocks}"
    )
    print("-" * 100)

    train_df = df[
        df["prediction_block"].isin(
            training_blocks
        )
    ].copy()

    eval_df = df[
        df["prediction_block"] == eval_block
    ].copy()

    print(
        "Training rows:",
        len(train_df),
    )

    print(
        "Evaluation rows:",
        len(eval_df),
    )

    assert len(train_df) > 0
    assert len(eval_df) > 0

    train_ids = set(
        train_df["ID"].astype(str)
    )

    eval_ids = set(
        eval_df["ID"].astype(str)
    )

    assert train_ids.isdisjoint(eval_ids)

    # Chronology guard.
    train_time = pd.to_datetime(
        train_df["prediction_creation_time"],
        utc=True,
    )

    eval_time = pd.to_datetime(
        eval_df["prediction_creation_time"],
        utc=True,
    )

    assert (
        train_time.max()
        <
        eval_time.min()
    )

    print(
        "Chronological boundary: PASS"
    )

    # Candidate A.
    result_a = evaluate(
        train_df,
        eval_df,
        T2_FEATURES,
        "A_T2_ONLY",
    )

    # Candidate B.
    result_b = evaluate(
        train_df,
        eval_df,
        T2_FEATURES + T7_FEATURES,
        "B_T2_PLUS_T7",
    )

    print(
        f"A accuracy: "
        f"{result_a['accuracy']:.6f}"
    )

    print(
        f"B accuracy: "
        f"{result_b['accuracy']:.6f}"
    )

    print(
        f"A macro-F1: "
        f"{result_a['macro_f1']:.6f}"
    )

    print(
        f"B macro-F1: "
        f"{result_b['macro_f1']:.6f}"
    )

    print(
        f"A weighted-F1: "
        f"{result_a['weighted_f1']:.6f}"
    )

    print(
        f"B weighted-F1: "
        f"{result_b['weighted_f1']:.6f}"
    )

    print(
        f"B-A accuracy: "
        f"{result_b['accuracy'] - result_a['accuracy']:+.6f}"
    )

    print(
        f"B-A macro-F1: "
        f"{result_b['macro_f1'] - result_a['macro_f1']:+.6f}"
    )

    print(
        f"B-A weighted-F1: "
        f"{result_b['weighted_f1'] - result_a['weighted_f1']:+.6f}"
    )

    print(
        "A predicted P3 proportion:",
        f"{result_a['predicted_proportions']['P3']:.6f}",
    )

    print(
        "B predicted P3 proportion:",
        f"{result_b['predicted_proportions']['P3']:.6f}",
    )

    print("\nPer-class F1:")

    for cls in CLASSES:

        a_f1 = result_a[
            "per_class_f1"
        ][cls]

        b_f1 = result_b[
            "per_class_f1"
        ][cls]

        print(
            f"  {cls}: "
            f"A={a_f1:.6f}, "
            f"B={b_f1:.6f}, "
            f"delta={b_f1 - a_f1:+.6f}"
        )

    # Store serializable result.
    clean_a = {
        k: v
        for k, v in result_a.items()
        if k != "predictions"
    }

    clean_b = {
        k: v
        for k, v in result_b.items()
        if k != "predictions"
    }

    all_results.append(
        {
            "evaluation_block": eval_block,
            "training_blocks": training_blocks,
            "candidate_A": clean_a,
            "candidate_B": clean_b,
            "deltas": {
                "accuracy": (
                    result_b["accuracy"]
                    -
                    result_a["accuracy"]
                ),
                "macro_f1": (
                    result_b["macro_f1"]
                    -
                    result_a["macro_f1"]
                ),
                "weighted_f1": (
                    result_b["weighted_f1"]
                    -
                    result_a["weighted_f1"]
                ),
            },
        }
    )

    for i, row in eval_df.reset_index(
        drop=True
    ).iterrows():

        prediction_rows.append(
            {
                "ID": row["ID"],
                "evaluation_block": eval_block,
                "target_priority": row[TARGET],
                "candidate_A_prediction": result_a[
                    "predictions"
                ][i],
                "candidate_B_prediction": result_b[
                    "predictions"
                ][i],
            }
        )


# ------------------------------------------------------------------
# [4] ROBUSTNESS SUMMARY
# ------------------------------------------------------------------

print("\n" + "=" * 100)
print("[4] CHRONOLOGICAL ROBUSTNESS SUMMARY")
print("=" * 100)

summary_rows = []

for result in all_results:

    a = result["candidate_A"]
    b = result["candidate_B"]

    summary_rows.append(
        {
            "block": result["evaluation_block"],
            "A_accuracy": a["accuracy"],
            "B_accuracy": b["accuracy"],
            "delta_accuracy": result[
                "deltas"
            ]["accuracy"],
            "A_macro_f1": a["macro_f1"],
            "B_macro_f1": b["macro_f1"],
            "delta_macro_f1": result[
                "deltas"
            ]["macro_f1"],
            "A_weighted_f1": a["weighted_f1"],
            "B_weighted_f1": b["weighted_f1"],
            "delta_weighted_f1": result[
                "deltas"
            ]["weighted_f1"],
            "A_P3_prop": a[
                "predicted_proportions"
            ]["P3"],
            "B_P3_prop": b[
                "predicted_proportions"
            ]["P3"],
        }
    )

summary_df = pd.DataFrame(
    summary_rows
)

print(
    summary_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.6f}",
    )
)


# ------------------------------------------------------------------
# [5] CROSS-BLOCK PATTERN
# ------------------------------------------------------------------

print("\n[5] CROSS-BLOCK PATTERN")

accuracy_deltas = summary_df[
    "delta_accuracy"
].to_numpy()

macro_deltas = summary_df[
    "delta_macro_f1"
].to_numpy()

weighted_deltas = summary_df[
    "delta_weighted_f1"
].to_numpy()

print(
    "Blocks evaluated:",
    list(summary_df["block"])
)

print(
    "Accuracy deltas:",
    accuracy_deltas.tolist()
)

print(
    "Macro-F1 deltas:",
    macro_deltas.tolist()
)

print(
    "Weighted-F1 deltas:",
    weighted_deltas.tolist()
)

print(
    "B accuracy improved in all blocks:",
    bool((accuracy_deltas > 0).all())
)

print(
    "B macro-F1 improved in all blocks:",
    bool((macro_deltas > 0).all())
)

print(
    "B weighted-F1 improved in all blocks:",
    bool((weighted_deltas > 0).all())
)


# ------------------------------------------------------------------
# [6] P3 CONCENTRATION
# ------------------------------------------------------------------

print("\n[6] P3 CONCENTRATION")

p3_props = summary_df[
    ["block", "A_P3_prop", "B_P3_prop"]
]

print(
    p3_props.to_string(
        index=False,
        float_format=lambda x: f"{x:.6f}",
    )
)

print(
    "\nThis measures prediction concentration only."
)

# ------------------------------------------------------------------
# [7] SAVE
# ------------------------------------------------------------------

print("\n[7] SAVE ARTIFACTS")

audit = {
    "module": "T8-MOD-032",
    "operation": "OP-004",
    "purpose": (
        "Chronological robustness audit of the "
        "controlled T2 versus T2+T7 fusion candidates."
    ),
    "experiments": all_results,
    "summary": summary_rows,
    "locked_evaluation_used": False,
    "final_candidate_selected": False,
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

prediction_df = pd.DataFrame(
    prediction_rows
)

prediction_df.to_csv(
    PREDICTIONS_OUTPUT,
    index=False,
)

assert len(prediction_df) == (
    4130 + 4129 + 4129
)

assert prediction_df["ID"].nunique() == len(
    prediction_df
)

print(
    "Audit written:",
    OUTPUT,
)

print(
    "Predictions written:",
    PREDICTIONS_OUTPUT,
)


# ------------------------------------------------------------------
# [8] FINAL STATUS
# ------------------------------------------------------------------

print("\n" + "=" * 100)
print("MOD-032 OP-004 COMPLETE")
print("=" * 100)

print("Chronological B3 evaluation: PASS")
print("Chronological B4 evaluation: PASS")
print("Chronological B5 evaluation: PASS")
print("Cross-block comparison: PASS")
print("Locked evaluation used: NO")
print("Final fusion candidate selected: NO")

print("=" * 100)