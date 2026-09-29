from pathlib import Path
import json
import importlib.util

import numpy as np
import pandas as pd


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

SOURCE = (
    ROOT / "modeling/T7/scripts/"
    "t7_mod010_log_normal_aft_baseline.py"
)

MODEL_JSON = (
    ROOT / "modeling/T7/metrics/"
    "t7_mod010_log_normal_aft_model.json"
)

TRAIN_CSV = (
    ROOT / "modeling/T7/splits/"
    "t7_train.csv"
)

EVAL_CSV = (
    ROOT / "modeling/T7/splits/"
    "t7_evaluation.csv"
)

OUT_JSON = (
    ROOT / "modeling/FMP/metrics/"
    "fmp06_op018r27_t7_exact_frozen_runtime_probe.json"
)


def load_t7_module():
    spec = importlib.util.spec_from_file_location(
        "t7_mod010_runtime_source",
        SOURCE,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "Could not create module specification."
        )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


def main():
    print("=" * 72)
    print("FMP-06 OP-018R27 — T7 EXACT FROZEN RUNTIME PROBE")
    print("=" * 72)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: YES — frozen parameters only")
    print("Evaluation metrics: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    # ------------------------------------------------------------
    # 1. Load authoritative T7 implementation
    # ------------------------------------------------------------
    print("\n[1] Loading authoritative MOD-010 implementation...")

    t7 = load_t7_module()

    if not hasattr(t7, "make_features"):
        raise RuntimeError(
            "Authoritative make_features() not found."
        )

    if not hasattr(t7, "text_features"):
        raise RuntimeError(
            "Authoritative text_features() not found."
        )

    print("  make_features(): PRESENT")
    print("  text_features(): PRESENT")

    # ------------------------------------------------------------
    # 2. Load frozen parameters
    # ------------------------------------------------------------
    print("\n[2] Loading frozen T7 parameters...")

    with MODEL_JSON.open(
        "r",
        encoding="utf-8"
    ) as f:
        model = json.load(f)

    feature_names = model["feature_names"]
    beta_dict = model["beta"]
    sigma = float(model["sigma"])

    beta = np.asarray(
        [
            float(beta_dict[name])
            for name in feature_names
        ],
        dtype=np.float64,
    )

    print(f"  model_type: {model['model_type']}")
    print(f"  features: {len(feature_names)}")
    print(f"  sigma: {sigma}")

    if len(beta) != len(feature_names):
        raise RuntimeError(
            "Beta/feature dimension mismatch."
        )

    # ------------------------------------------------------------
    # 3. Load native train/evaluation populations
    # ------------------------------------------------------------
    print("\n[3] Loading native T7 populations...")

    train = pd.read_csv(TRAIN_CSV)
    evaluation = pd.read_csv(EVAL_CSV)

    print(f"  train rows: {len(train)}")
    print(f"  evaluation rows: {len(evaluation)}")

    # ------------------------------------------------------------
    # 4. Reconstruct exact frequency evidence
    # ------------------------------------------------------------
    print("\n[4] Reconstructing native frequency evidence...")

    creator_counts = (
        train["Creator"]
        .fillna("")
        .astype(str)
        .str.strip()
        .value_counts()
        .to_dict()
    )

    detail_counts = (
        train["Creator Detail"]
        .fillna("")
        .astype(str)
        .str.strip()
        .value_counts()
        .to_dict()
    )

    print(
        f"  creator keys: {len(creator_counts)}"
    )

    print(
        f"  creator-detail keys: {len(detail_counts)}"
    )

    # ------------------------------------------------------------
    # 5. Three native evaluation rows
    # ------------------------------------------------------------
    print("\n[5] Selecting native evaluation probe...")

    probe_rows = (
        evaluation
        .head(3)
        .to_dict(orient="records")
    )

    print(
        "  IDs:",
        [str(row["ID"]) for row in probe_rows]
    )

    # ------------------------------------------------------------
    # 6. Exact authoritative feature construction
    # ------------------------------------------------------------
    print("\n[6] Calling authoritative make_features()...")

    X, ids, durations, events, names = (
        t7.make_features(
            probe_rows,
            creator_counts,
            detail_counts,
        )
    )

    X = np.asarray(
        X,
        dtype=np.float64,
    )

    print(f"  X shape: {X.shape}")
    print(f"  returned feature count: {len(names)}")

    if list(names) != list(feature_names):
        raise RuntimeError(
            "Authoritative feature order does not match "
            "frozen model feature order."
        )

    if X.shape != (
        len(probe_rows),
        len(feature_names),
    ):
        raise RuntimeError(
            "Unexpected feature matrix shape."
        )

    # ------------------------------------------------------------
    # 7. Frozen model execution
    # ------------------------------------------------------------
    print("\n[7] Executing frozen T7 model...")

    linear_predictor = X @ beta

    print(
        "  linear predictor:",
        [
            round(float(x), 8)
            for x in linear_predictor
        ]
    )

    # Median of Log-Normal distribution:
    # exp(mu)
    predicted_median_duration = np.exp(
        linear_predictor
    )

    print(
        "  predicted median duration:",
        [
            round(float(x), 6)
            for x in predicted_median_duration
        ]
    )

    if not np.all(
        np.isfinite(predicted_median_duration)
    ):
        raise RuntimeError(
            "Frozen runtime produced non-finite "
            "median duration."
        )

    # ------------------------------------------------------------
    # 8. Native event semantics
    # ------------------------------------------------------------
    print("\n[8] Preserving native event semantics...")

    event_values = [
        int(x)
        for x in events.tolist()
    ]

    print(
        f"  events: {event_values}"
    )

    print(
        "  observed durations:",
        [
            float(x)
            for x in durations.tolist()
        ]
    )

    # ------------------------------------------------------------
    # 9. Evidence artifact
    # ------------------------------------------------------------
    result = {
        "operation":
            "FMP-06 OP-018R27",

        "status":
            "PASS",

        "read_only":
            True,

        "training_performed":
            False,

        "fitting_performed":
            False,

        "prediction_performed":
            True,

        "evaluation_performed":
            False,

        "locked_test_used":
            False,

        "artifact_modified":
            False,

        "source":
            str(SOURCE),

        "model_type":
            model["model_type"],

        "feature_count":
            len(feature_names),

        "feature_names":
            feature_names,

        "sigma":
            sigma,

        "probe_ids":
            [
                str(x)
                for x in ids
            ],

        "observed_durations":
            [
                float(x)
                for x in durations.tolist()
            ],

        "event_values":
            event_values,

        "linear_predictor":
            [
                float(x)
                for x in linear_predictor
            ],

        "predicted_median_duration":
            [
                float(x)
                for x in predicted_median_duration
            ],

        "authoritative_feature_builder_used":
            True,

        "interpretation":
            (
                "The authoritative T7 MOD-010 make_features() "
                "implementation was executed directly on three "
                "native evaluation rows using frozen model "
                "coefficients. No fitting or parameter selection "
                "was performed."
            ),
    }

    OUT_JSON.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUT_JSON.open(
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            result,
            f,
            indent=2
        )

    # ------------------------------------------------------------
    # 10. Compact terminal summary
    # ------------------------------------------------------------
    print("\n" + "=" * 72)
    print("OP-018R27 PROBE COMPLETE")
    print("=" * 72)

    print(f"Status: {result['status']}")
    print(f"Model: {result['model_type']}")
    print(f"Feature matrix: {X.shape}")
    print(f"Probe rows: {len(probe_rows)}")

    print(
        "Predicted median durations:",
        [
            round(float(x), 6)
            for x in predicted_median_duration
        ]
    )

    print(
        f"Events: {event_values}"
    )

    print(
        f"Output: {OUT_JSON}"
    )

    print("\nNo training performed.")
    print("No fitting performed.")
    print("No evaluation performed.")
    print("No locked test used.")
    print("No artifact modification performed.")

    print("=" * 72)


if __name__ == "__main__":
    main()