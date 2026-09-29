from pathlib import Path
import json
import math
import re

import numpy as np
import pandas as pd


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

MODEL_JSON = (
    ROOT / "modeling/T7/metrics/t7_mod010_log_normal_aft_model.json"
)

EVAL_CSV = (
    ROOT / "modeling/T7/splits/t7_evaluation.csv"
)

OUT_JSON = (
    ROOT / "modeling/FMP/metrics/"
    "fmp06_op018r24_t7_frozen_runtime_probe.json"
)


def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def log1p_value(value):
    return float(np.log1p(float(value)))


def text_chars(value):
    return len(value)


def text_words(value):
    return len(re.findall(r"\S+", value))


def text_digits(value):
    return sum(ch.isdigit() for ch in value)


def text_lines(value):
    if not value:
        return 0
    return value.count("\n") + 1


def text_uppercase(value):
    return sum(ch.isupper() for ch in value)


def main():
    print("=" * 72)
    print("FMP-06 OP-018R24 — T7 FROZEN RUNTIME PROBE")
    print("=" * 72)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: YES — frozen parameters only")
    print("Evaluation metrics: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    # ------------------------------------------------------------
    # 1. Load frozen parameter artifact
    # ------------------------------------------------------------
    print("\n[1] Loading frozen T7 parameter artifact...")

    with MODEL_JSON.open("r", encoding="utf-8") as f:
        model = json.load(f)

    feature_names = model["feature_names"]
    beta_dict = model["beta"]
    means = model["standardization_mean"]
    stds = model["standardization_std"]
    sigma = float(model["sigma"])

    print(f"  model_type: {model.get('model_type')}")
    print(f"  feature_count: {len(feature_names)}")
    print(f"  beta_count: {len(beta_dict)}")
    print(f"  mean_count: {len(means)}")
    print(f"  std_count: {len(stds)}")
    print(f"  sigma: {sigma}")

    if not (
        len(feature_names)
        == len(beta_dict)
        == len(means)
        == len(stds)
    ):
        raise RuntimeError(
            "Frozen parameter dimensions do not agree."
        )

    # ------------------------------------------------------------
    # 2. Load native T7 evaluation population
    # ------------------------------------------------------------
    print("\n[2] Loading native T7 evaluation population...")

    df = pd.read_csv(EVAL_CSV)

    required = [
        "ID",
        "Creation time",
        "Creator",
        "Creator Detail",
        "Summary",
        "Description",
        "duration_seconds",
        "event",
    ]

    missing = [c for c in required if c not in df.columns]

    if missing:
        raise RuntimeError(
            f"Missing native T7 columns: {missing}"
        )

    print(f"  rows: {len(df)}")
    print(f"  columns: {len(df.columns)}")

    # ------------------------------------------------------------
    # 3. Native training population for frequency features
    # ------------------------------------------------------------
    print("\n[3] Loading native T7 training population...")

    train_csv = ROOT / "modeling/T7/splits/t7_train.csv"
    train = pd.read_csv(train_csv)

    creator_counts = (
        train["Creator"]
        .fillna("")
        .astype(str)
        .value_counts()
    )

    creator_detail_counts = (
        train["Creator Detail"]
        .fillna("")
        .astype(str)
        .value_counts()
    )

    print(f"  training rows: {len(train)}")

    # ------------------------------------------------------------
    # 4. Three-row native probe
    # ------------------------------------------------------------
    print("\n[4] Constructing native T7 feature vectors...")

    probe = df.head(3).copy()

    feature_rows = []

    for _, row in probe.iterrows():

        creator = clean_text(row["Creator"])
        creator_detail = clean_text(row["Creator Detail"])
        summary = clean_text(row["Summary"])
        description = clean_text(row["Description"])

        creation_time = pd.to_datetime(
            row["Creation time"],
            errors="raise"
        )

        month = creation_time.month
        weekday = creation_time.weekday()
        hour = creation_time.hour

        feature_row = {
            "creator_frequency_log1p":
                log1p_value(
                    creator_counts.get(creator, 0)
                ),

            "creator_detail_frequency_log1p":
                log1p_value(
                    creator_detail_counts.get(
                        creator_detail, 0
                    )
                ),

            "summary_chars_log1p":
                log1p_value(
                    text_chars(summary)
                ),

            "summary_words_log1p":
                log1p_value(
                    text_words(summary)
                ),

            "summary_digits_log1p":
                log1p_value(
                    text_digits(summary)
                ),

            "summary_lines_log1p":
                log1p_value(
                    text_lines(summary)
                ),

            "summary_uppercase_log1p":
                log1p_value(
                    text_uppercase(summary)
                ),

            "summary_missing":
                float(not bool(summary)),

            "description_chars_log1p":
                log1p_value(
                    text_chars(description)
                ),

            "description_words_log1p":
                log1p_value(
                    text_words(description)
                ),

            "description_digits_log1p":
                log1p_value(
                    text_digits(description)
                ),

            "description_lines_log1p":
                log1p_value(
                    text_lines(description)
                ),

            "description_uppercase_log1p":
                log1p_value(
                    text_uppercase(description)
                ),

            "description_missing":
                float(not bool(description)),

            "creation_year_scaled":
                float(creation_time.year),

            "creation_month_sin":
                math.sin(
                    2 * math.pi * month / 12.0
                ),

            "creation_month_cos":
                math.cos(
                    2 * math.pi * month / 12.0
                ),

            "creation_weekday_sin":
                math.sin(
                    2 * math.pi * weekday / 7.0
                ),

            "creation_weekday_cos":
                math.cos(
                    2 * math.pi * weekday / 7.0
                ),

            "creation_hour_sin":
                math.sin(
                    2 * math.pi * hour / 24.0
                ),

            "creation_hour_cos":
                math.cos(
                    2 * math.pi * hour / 24.0
                ),
        }

        feature_rows.append(feature_row)

    raw = pd.DataFrame(feature_rows)

    missing_features = [
        feature
        for feature in feature_names
        if feature not in raw.columns
    ]

    if missing_features:
        raise RuntimeError(
            f"Missing reconstructed features: "
            f"{missing_features}"
        )

    X_raw = raw[feature_names].astype(float)

    # ------------------------------------------------------------
    # 5. Align frozen parameter vectors
    # ------------------------------------------------------------
    print("\n[5] Aligning frozen parameters...")

    beta_vector = np.asarray(
        [float(beta_dict[f]) for f in feature_names],
        dtype=float
    )

    mean_vector = np.asarray(
        means,
        dtype=float
    )

    std_vector = np.asarray(
        stds,
        dtype=float
    )

    if len(beta_vector) != len(feature_names):
        raise RuntimeError("Beta dimension mismatch.")

    if len(mean_vector) != len(feature_names):
        raise RuntimeError("Mean dimension mismatch.")

    if len(std_vector) != len(feature_names):
        raise RuntimeError("Std dimension mismatch.")

    if np.any(std_vector == 0):
        raise RuntimeError(
            "Frozen standardization contains zero std."
        )

    print("  parameter dimensions: PASS")

    # ------------------------------------------------------------
    # 6. Frozen standardization
    # ------------------------------------------------------------
    print("\n[6] Applying frozen standardization...")

    X_scaled = (
        X_raw.to_numpy(dtype=float)
        - mean_vector
    ) / std_vector

    # ------------------------------------------------------------
    # 7. Frozen Log-Normal AFT prediction
    # ------------------------------------------------------------
    print("\n[7] Executing frozen Log-Normal AFT...")

    linear_predictor = (
        X_scaled @ beta_vector
    )

    predicted_median_duration = np.exp(
        linear_predictor
    )

    print(
        "  linear predictor:",
        [
            round(float(x), 6)
            for x in linear_predictor
        ]
    )

    print(
        "  predicted median duration:",
        [
            round(float(x), 6)
            for x in predicted_median_duration
        ]
    )

    # ------------------------------------------------------------
    # 8. Preserve native event/censor semantics
    # ------------------------------------------------------------
    print("\n[8] Checking native event semantics...")

    event_values = [
        int(x)
        for x in probe["event"].tolist()
    ]

    valid_events = all(
        value in (0, 1)
        for value in event_values
    )

    print(f"  event values: {event_values}")
    print(f"  binary event encoding: {valid_events}")

    # ------------------------------------------------------------
    # 9. Write evidence artifact
    # ------------------------------------------------------------
    result = {
        "operation":
            "FMP-06 OP-018R24",

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

        "model_type":
            model.get("model_type"),

        "feature_count":
            len(feature_names),

        "feature_names":
            feature_names,

        "sigma":
            sigma,

        "probe_ids":
            [
                str(x)
                for x in probe["ID"].tolist()
            ],

        "event_values":
            event_values,

        "parameter_dimensions_verified":
            True,

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

        "interpretation":
            (
                "The final T7 Log-Normal AFT parameter artifact "
                "was executed using its frozen coefficients and "
                "standardization vectors on native T7 evaluation "
                "rows. No fitting or parameter selection was "
                "performed. Event/censoring metadata remains "
                "observational."
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
    print("OP-018R24 PROBE COMPLETE")
    print("=" * 72)

    print(f"Status: {result['status']}")
    print(f"Model: {result['model_type']}")
    print(f"Frozen features: {result['feature_count']}")
    print(f"Probe rows: {len(probe)}")

    print(
        "Predicted median durations:",
        [
            round(float(x), 6)
            for x in predicted_median_duration
        ]
    )

    print(f"Event values: {event_values}")
    print(f"Output: {OUT_JSON}")

    print("\nNo training performed.")
    print("No fitting performed.")
    print("No evaluation performed.")
    print("No locked test used.")
    print("No artifact modification performed.")

    print("=" * 72)


if __name__ == "__main__":
    main()