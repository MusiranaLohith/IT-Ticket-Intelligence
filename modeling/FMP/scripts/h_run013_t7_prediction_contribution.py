from pathlib import Path
import json
import math
import importlib.util

import numpy as np
import pandas as pd


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T7_SOURCE = (
    ROOT
    / "modeling/T7/scripts/t7_mod010_log_normal_aft_baseline.py"
)

T7_MODEL = (
    ROOT
    / "modeling/T7/metrics/t7_mod010_log_normal_aft_model.json"
)

T7_TRAIN = (
    ROOT
    / "modeling/T7/splits/t7_train.csv"
)

OUTPUT = (
    ROOT
    / "modeling/FMP/metrics/"
    "h_run013_t7_prediction_contribution.json"
)

TITLE = "VPN connection fails after password reset"

DESCRIPTION = (
    "I reset my corporate password this morning. "
    "Since then, the VPN client connects briefly and then disconnects. "
    "I restarted the laptop and reinstalled the VPN client, "
    "but the issue persists. "
    "I need access to the internal systems for today's work."
)

CREATION_TIME = "2026-09-26T18:03:00Z"


def load_t7_source():
    spec = importlib.util.spec_from_file_location(
        "t7_mod010_runtime",
        T7_SOURCE,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "Could not load T7 source module."
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def main():
    print("=" * 72)
    print("H-RUN-013 — T7 PREDICTION CONTRIBUTION DECOMPOSITION")
    print("=" * 72)

    print("\n[CONTROL]")
    print("training/retraining: NO")
    print("model modification: NO")
    print("locked-test use: NO")
    print("prediction modification: NO")
    print("threshold selection: NO")

    for path in [
        T7_SOURCE,
        T7_MODEL,
        T7_TRAIN,
    ]:
        if not path.exists():
            raise FileNotFoundError(
                f"Missing required file: {path}"
            )

    model_spec = json.loads(
        T7_MODEL.read_text(
            encoding="utf-8"
        )
    )

    feature_names = model_spec["feature_names"]

    beta_map = {
        str(name): float(value)
        for name, value in model_spec["beta"].items()
    }

    mean = np.asarray(
        model_spec["standardization_mean"],
        dtype=np.float64,
    )

    std = np.asarray(
        model_spec["standardization_std"],
        dtype=np.float64,
    )

    beta = np.asarray(
        [
            beta_map[name]
            for name in feature_names
        ],
        dtype=np.float64,
    )

    if len(feature_names) != 21:
        raise RuntimeError(
            "Expected exactly 21 T7 features."
        )

    train_df = pd.read_csv(T7_TRAIN)

    creator_counts = (
        train_df["Creator"]
        .fillna("")
        .astype(str)
        .str.strip()
        .value_counts()
        .to_dict()
    )

    detail_counts = (
        train_df["Creator Detail"]
        .fillna("")
        .astype(str)
        .str.strip()
        .value_counts()
        .to_dict()
    )

    t7 = load_t7_source()

    runtime_row = {
        "ID": "H-RUN-013-NEW-TICKET",
        "Creation time": CREATION_TIME,
        "Creator": "",
        "Creator Detail": "",
        "Summary": TITLE,
        "Description": DESCRIPTION,
    }

    dt = t7.parse_creation(
        runtime_row["Creation time"]
    )

    s = t7.text_features(
        runtime_row["Summary"]
    )

    d = t7.text_features(
        runtime_row["Description"]
    )

    month = (
        2 * math.pi * (dt.month - 1) / 12
    )

    weekday = (
        2 * math.pi * dt.weekday() / 7
    )

    hour = (
        2 * math.pi * dt.hour / 24
    )

    raw = np.asarray(
        [[
            math.log1p(
                creator_counts.get(
                    runtime_row["Creator"].strip(),
                    0,
                )
            ),

            math.log1p(
                detail_counts.get(
                    runtime_row["Creator Detail"].strip(),
                    0,
                )
            ),

            math.log1p(s[0]),
            math.log1p(s[1]),
            math.log1p(s[2]),
            math.log1p(s[3]),
            math.log1p(s[4]),
            s[5],

            math.log1p(d[0]),
            math.log1p(d[1]),
            math.log1p(d[2]),
            math.log1p(d[3]),
            math.log1p(d[4]),
            d[5],

            (dt.year - 2010.0) / 10.0,

            math.sin(month),
            math.cos(month),

            math.sin(weekday),
            math.cos(weekday),

            math.sin(hour),
            math.cos(hour),
        ]],
        dtype=np.float64,
    )

    standardized = (
        raw - mean
    ) / std

    contributions = standardized[0] * beta

    total = float(
        contributions.sum()
    )

    print("\n[FEATURE CONTRIBUTIONS]")

    records = []

    for i, name in enumerate(feature_names):
        record = {
            "index": i,
            "feature": name,
            "raw_value": float(raw[0, i]),
            "standardization_mean": float(mean[i]),
            "standardization_std": float(std[i]),
            "standardized_value": float(
                standardized[0, i]
            ),
            "beta": float(beta[i]),
            "contribution_to_linear_predictor": float(
                contributions[i]
            ),
        }

        records.append(record)

        print(
            f"{i:02d} "
            f"{name}: "
            f"raw={raw[0, i]:.6f} "
            f"std={standardized[0, i]:.6f} "
            f"beta={beta[i]:.6f} "
            f"contribution={contributions[i]:.6f}"
        )

    ranked = sorted(
        records,
        key=lambda item: abs(
            item["contribution_to_linear_predictor"]
        ),
        reverse=True,
    )

    print("\n[TOP ABSOLUTE CONTRIBUTORS]")

    for item in ranked[:10]:
        print(
            f"{item['feature']}: "
            f"{item['contribution_to_linear_predictor']:.6f}"
        )

    predicted_duration = float(
        np.exp(total)
    )

    print("\n[RECONSTRUCTION]")

    print(
        f"sum of contributions: {total:.6f}"
    )

    print(
        f"exp(sum): {predicted_duration:.6f}"
    )

    print(
        f"hours: "
        f"{predicted_duration / 3600.0:.6f}"
    )

    output = {
        "operation": "H-RUN-013",
        "operation_name": (
            "T7 Prediction Contribution Decomposition"
        ),
        "status": "PASS",
        "feature_count": len(feature_names),
        "features": records,
        "ranked_absolute_contributors": ranked,
        "linear_predictor": total,
        "predicted_median_duration_seconds": (
            predicted_duration
        ),
        "controls": {
            "training": False,
            "retraining": False,
            "locked_test_use": False,
            "prediction_modification": False,
            "threshold_selection": False,
        },
        "interpretation_boundary": (
            "This operation decomposes the existing frozen "
            "T7 prediction into standardized feature "
            "contributions. It does not modify the model "
            "or establish an operational decision threshold."
        ),
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            output,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n[OUTPUT]")
    print(f"written: {OUTPUT}")

    print("\n" + "=" * 72)
    print("H-RUN-013 COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()