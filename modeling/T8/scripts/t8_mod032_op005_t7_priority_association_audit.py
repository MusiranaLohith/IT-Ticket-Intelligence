from pathlib import Path
import json

import numpy as np
import pandas as pd

from sklearn.metrics import roc_auc_score


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T8_ROOT = ROOT / "modeling/T8"

JOINT_OOF = T8_ROOT / "t8_mod029_joint_oof.csv"

OUTPUT = (
    T8_ROOT
    / "mod032"
    / "t8_mod032_op005_t7_priority_association.json"
)

CLASSES = ["P1", "P2", "P3", "P4", "P5"]

T7_FEATURES = [
    "predicted_median_survival_seconds",
    "survival_probability_at_211583_seconds",
    "survival_probability_at_1780179_seconds",
    "survival_probability_at_14608619_seconds",
]


print("=" * 100)
print(
    "T8 MOD-032 — OP-005: "
    "T7 EVIDENCE / PRIORITY ASSOCIATION STABILITY AUDIT"
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
# [2] BASIC VALIDITY
# ------------------------------------------------------------------

print("\n[2] T7 EVIDENCE VALIDITY")

for feature in T7_FEATURES:

    assert feature in df.columns

    values = pd.to_numeric(
        df[feature],
        errors="coerce",
    )

    assert values.notna().all()
    assert np.isfinite(values).all()

    print(
        f"{feature}: "
        f"finite={values.notna().sum()}"
    )

median_feature = (
    df["predicted_median_survival_seconds"]
    .astype(float)
)

assert (median_feature > 0).all()

survival_features = [
    feature
    for feature in T7_FEATURES
    if feature !=
    "predicted_median_survival_seconds"
]

for feature in survival_features:

    values = df[feature].astype(float)

    assert (
        (values >= 0)
        & (values <= 1)
    ).all()

print("T7 evidence validity: PASS")


# ------------------------------------------------------------------
# [3] TARGET VALIDITY
# ------------------------------------------------------------------

print("\n[3] TARGET VALIDITY")

assert "target_priority" in df.columns

assert set(
    df["target_priority"].unique()
).issubset(set(CLASSES))

print(
    df["target_priority"]
    .value_counts()
    .reindex(CLASSES, fill_value=0)
    .to_string()
)

print("Native T2 target: PASS")


# ------------------------------------------------------------------
# [4] GLOBAL CLASS-CONDITIONAL DISTRIBUTIONS
# ------------------------------------------------------------------

print("\n[4] GLOBAL CLASS-CONDITIONAL DISTRIBUTIONS")

global_results = {}

for feature in T7_FEATURES:

    print("\n" + feature)

    rows = []

    for cls in CLASSES:

        values = df.loc[
            df["target_priority"] == cls,
            feature,
        ].astype(float)

        row = {
            "class": cls,
            "n": int(len(values)),
            "mean": float(values.mean()),
            "median": float(values.median()),
            "q25": float(values.quantile(0.25)),
            "q75": float(values.quantile(0.75)),
        }

        rows.append(row)

        print(
            f"{cls}: "
            f"n={row['n']}, "
            f"mean={row['mean']:.6f}, "
            f"median={row['median']:.6f}, "
            f"q25={row['q25']:.6f}, "
            f"q75={row['q75']:.6f}"
        )

    global_results[feature] = rows


# ------------------------------------------------------------------
# [5] GLOBAL ONE-VS-REST AUC
# ------------------------------------------------------------------

print("\n[5] GLOBAL ONE-VS-REST AUC")

global_auc = {}

for feature in T7_FEATURES:

    print("\n" + feature)

    feature_values = df[feature].astype(float)

    global_auc[feature] = {}

    for cls in CLASSES:

        y = (
            df["target_priority"] == cls
        ).astype(int)

        auc = roc_auc_score(
            y,
            feature_values,
        )

        # Because some T7 quantities have an inverse
        # semantic direction, report both the raw AUC
        # and distance from 0.5.
        discrimination = max(
            auc,
            1.0 - auc,
        )

        global_auc[feature][cls] = {
            "auc": float(auc),
            "direction_free_auc": float(
                discrimination
            ),
        }

        print(
            f"{cls}: "
            f"AUC={auc:.6f}, "
            f"direction_free={discrimination:.6f}"
        )


# ------------------------------------------------------------------
# [6] BLOCK-WISE ONE-VS-REST AUC
# ------------------------------------------------------------------

print("\n[6] BLOCK-WISE ONE-VS-REST AUC")

blocks = ["B2", "B3", "B4", "B5"]

block_auc = {}

for block in blocks:

    block_df = df[
        df["prediction_block"] == block
    ].copy()

    print("\n" + "-" * 80)
    print(
        f"Block {block}: {len(block_df)} rows"
    )

    assert len(block_df) > 0

    block_auc[block] = {}

    for feature in T7_FEATURES:

        block_auc[block][feature] = {}

        print("\n", feature)

        for cls in CLASSES:

            y = (
                block_df["target_priority"]
                == cls
            ).astype(int)

            values = block_df[
                feature
            ].astype(float)

            # Every block should contain every
            # target class for the audit to be valid.
            if y.sum() == 0 or y.sum() == len(y):

                auc = None
                direction_free = None

            else:

                auc = roc_auc_score(
                    y,
                    values,
                )

                direction_free = max(
                    auc,
                    1.0 - auc,
                )

            block_auc[block][feature][cls] = {
                "auc": (
                    None
                    if auc is None
                    else float(auc)
                ),
                "direction_free_auc": (
                    None
                    if direction_free is None
                    else float(direction_free)
                ),
            }

            print(
                f"  {cls}: "
                f"{'NA' if auc is None else f'AUC={auc:.6f}, df={direction_free:.6f}'}"
            )


# ------------------------------------------------------------------
# [7] ASSOCIATION DIRECTION STABILITY
# ------------------------------------------------------------------

print("\n[7] ASSOCIATION DIRECTION STABILITY")

direction_results = {}

for feature in T7_FEATURES:

    print("\n" + feature)

    direction_results[feature] = {}

    for cls in CLASSES:

        aucs = []

        for block in blocks:

            auc = (
                block_auc
                [block]
                [feature]
                [cls]
                ["auc"]
            )

            if auc is not None:
                aucs.append(auc)

        signs = [
            "positive"
            if auc > 0.5
            else
            "negative"
            if auc < 0.5
            else
            "neutral"
            for auc in aucs
        ]

        direction_results[feature][cls] = {
            "aucs": [
                float(x)
                for x in aucs
            ],
            "directions": signs,
            "direction_consistent": (
                len(set(signs)) <= 1
            ),
        }

        print(
            f"{cls}: "
            f"AUCs={[round(x, 6) for x in aucs]}, "
            f"directions={signs}, "
            f"consistent={len(set(signs)) <= 1}"
        )


# ------------------------------------------------------------------
# [8] DISCRIMINATION STABILITY
# ------------------------------------------------------------------

print("\n[8] DISCRIMINATION STABILITY")

stability = {}

for feature in T7_FEATURES:

    print("\n" + feature)

    stability[feature] = {}

    for cls in CLASSES:

        values = []

        for block in blocks:

            value = (
                block_auc
                [block]
                [feature]
                [cls]
                ["direction_free_auc"]
            )

            if value is not None:
                values.append(value)

        mean_value = float(
            np.mean(values)
        )

        min_value = float(
            np.min(values)
        )

        max_value = float(
            np.max(values)
        )

        range_value = (
            max_value - min_value
        )

        stability[feature][cls] = {
            "mean_direction_free_auc":
                mean_value,
            "min_direction_free_auc":
                min_value,
            "max_direction_free_auc":
                max_value,
            "range_direction_free_auc":
                range_value,
        }

        print(
            f"{cls}: "
            f"mean={mean_value:.6f}, "
            f"min={min_value:.6f}, "
            f"max={max_value:.6f}, "
            f"range={range_value:.6f}"
        )


# ------------------------------------------------------------------
# [9] INTERPRETIVE SUMMARY
# ------------------------------------------------------------------

print("\n" + "=" * 100)
print("[9] ASSOCIATION SUMMARY")
print("=" * 100)

for feature in T7_FEATURES:

    stable_count = 0
    total_count = 0

    for cls in CLASSES:

        result = (
            direction_results
            [feature]
            [cls]
        )

        total_count += 1

        if result[
            "direction_consistent"
        ]:
            stable_count += 1

    print(
        f"{feature}: "
        f"direction-consistent class associations "
        f"{stable_count}/{total_count}"
    )


print(
    "\nThis operation does not determine causal relevance."
)

print(
    "It does not select a fusion learner."
)

print(
    "It only tests whether the native T7 prediction "
    "evidence has stable descriptive association "
    "with the native T2 priority target."
)


# ------------------------------------------------------------------
# [10] SAVE
# ------------------------------------------------------------------

print("\n[10] SAVE AUDIT")

audit = {
    "module": "T8-MOD-032",
    "operation": "OP-005",
    "purpose": (
        "Assess chronological stability of the "
        "association between native T7 prediction "
        "evidence and native T2 priority."
    ),
    "global_class_conditional_distributions":
        global_results,
    "global_one_vs_rest_auc":
        global_auc,
    "block_one_vs_rest_auc":
        block_auc,
    "direction_stability":
        direction_results,
    "discrimination_stability":
        stability,
    "locked_evaluation_used": False,
    "fusion_model_trained": False,
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

print(
    "Audit written:",
    OUTPUT,
)


# ------------------------------------------------------------------
# [11] FINAL STATUS
# ------------------------------------------------------------------

print("\n" + "=" * 100)
print("MOD-032 OP-005 COMPLETE")
print("=" * 100)

print("Global T7 association analysis: PASS")
print("Block-wise association analysis: PASS")
print("Direction stability analysis: PASS")
print("Discrimination stability analysis: PASS")
print("Locked evaluation used: NO")
print("Fusion model trained: NO")
print("Final candidate selected: NO")

print("=" * 100)