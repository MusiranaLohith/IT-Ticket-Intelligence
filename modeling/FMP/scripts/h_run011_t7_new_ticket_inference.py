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
    "h_run011_t7_new_ticket_inference.json"
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


EXPECTED_FEATURES = [
    "creator_frequency_log1p",
    "creator_detail_frequency_log1p",
    "summary_chars_log1p",
    "summary_words_log1p",
    "summary_digits_log1p",
    "summary_lines_log1p",
    "summary_uppercase_log1p",
    "summary_missing",
    "description_chars_log1p",
    "description_words_log1p",
    "description_digits_log1p",
    "description_lines_log1p",
    "description_uppercase_log1p",
    "description_missing",
    "creation_year_scaled",
    "creation_month_sin",
    "creation_month_cos",
    "creation_weekday_sin",
    "creation_weekday_cos",
    "creation_hour_sin",
    "creation_hour_cos",
]


def load_t7_source():
    spec = importlib.util.spec_from_file_location(
        "t7_mod010_runtime",
        T7_SOURCE,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "Could not create T7 module specification."
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def main():
    print("=" * 72)
    print("H-RUN-011R3 — T7 NEW-TICKET INFERENCE")
    print("=" * 72)

    print("\n[CONTROL]")
    print("training/retraining: NO")
    print("outcome/duration supplied: NO")
    print("event supplied: NO")
    print("model modification: NO")
    print("locked-test use: NO")
    print("threshold selection: NO")

    for path in [
        T7_SOURCE,
        T7_MODEL,
        T7_TRAIN,
    ]:
        if not path.exists():
            raise FileNotFoundError(
                f"Missing required T7 artifact/input: {path}"
            )

    print("\n[LOAD]")
    print(f"T7 source: {T7_SOURCE}")
    print(f"T7 model:  {T7_MODEL}")
    print(f"T7 train:  {T7_TRAIN}")

    t7 = load_t7_source()

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

    standardization_mean = np.asarray(
        model_spec["standardization_mean"],
        dtype=np.float64,
    )

    standardization_std = np.asarray(
        model_spec["standardization_std"],
        dtype=np.float64,
    )

    sigma = float(model_spec["sigma"])

    print("\n[MODEL]")
    print(f"feature count: {len(feature_names)}")
    print(f"beta entries: {len(beta_map)}")
    print(
        f"standardization mean count: "
        f"{len(standardization_mean)}"
    )
    print(
        f"standardization std count: "
        f"{len(standardization_std)}"
    )
    print(f"sigma: {sigma}")

    if feature_names != EXPECTED_FEATURES:
        raise RuntimeError(
            "Frozen T7 feature order does not match "
            "the authoritative make_features() contract."
        )

    if len(beta_map) != len(feature_names):
        raise RuntimeError(
            "Frozen beta dictionary does not contain "
            "exactly one coefficient per feature."
        )

    if len(standardization_mean) != len(feature_names):
        raise RuntimeError(
            "Frozen standardization mean length does not "
            "match feature count."
        )

    if len(standardization_std) != len(feature_names):
        raise RuntimeError(
            "Frozen standardization std length does not "
            "match feature count."
        )

    if np.any(standardization_std == 0):
        raise RuntimeError(
            "Frozen standardization contains zero standard deviation."
        )

    beta = np.asarray(
        [
            beta_map[name]
            for name in feature_names
        ],
        dtype=np.float64,
    )

    print("feature order: VERIFIED")
    print("beta alignment: VERIFIED")
    print("standardization parameters: VERIFIED")

    print("\n[TRAINING-DERIVED FREQUENCY CONTEXT]")

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

    print(
        f"training rows used for creator frequencies: "
        f"{len(train_df)}"
    )

    print(
        f"creator frequency entries: "
        f"{len(creator_counts)}"
    )

    print(
        f"creator-detail frequency entries: "
        f"{len(detail_counts)}"
    )

    runtime_row = {
        "ID": "H-RUN-011-NEW-TICKET",
        "Creation time": CREATION_TIME,
        "Creator": "",
        "Creator Detail": "",
        "Summary": TITLE,
        "Description": DESCRIPTION,
    }

    print("\n[TICKET]")
    print(f"ID: {runtime_row['ID']}")
    print(
        f"Creation time: "
        f"{runtime_row['Creation time']}"
    )
    print(
        f"Summary: "
        f"{runtime_row['Summary']}"
    )

    # Exact feature construction from the authoritative
    # T7 make_features() implementation.
    #
    # duration_seconds and event are deliberately excluded
    # because they are observed outcomes, not input features.

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

    X_raw_row = [
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
    ]

    X_raw = np.asarray(
        [X_raw_row],
        dtype=np.float64,
    )

    print("\n[RAW FEATURES]")
    print(f"shape: {list(X_raw.shape)}")

    if X_raw.shape != (1, 21):
        raise RuntimeError(
            f"Unexpected raw feature shape: "
            f"{X_raw.shape}"
        )

    # Exact frozen standardization used by T7 training:
    # X_standardized = (X_raw - mean) / std

    X_standardized = (
        X_raw - standardization_mean
    ) / standardization_std

    print("\n[STANDARDIZATION]")
    print(
        f"standardized shape: "
        f"{list(X_standardized.shape)}"
    )

    if not np.all(
        np.isfinite(X_standardized)
    ):
        raise RuntimeError(
            "Non-finite standardized feature value detected."
        )

    print("finite-value check: PASS")

    # Frozen T7 prediction:
    #
    # mu = X_standardized @ beta
    # median duration = exp(mu)

    linear_predictor = float(
        (X_standardized @ beta).item()
    )

    predicted_median_duration = float(
        np.exp(linear_predictor)
    )

    print("\n[T7 FROZEN INFERENCE]")
    print(
        f"linear predictor: "
        f"{linear_predictor:.6f}"
    )

    print(
        f"predicted median duration seconds: "
        f"{predicted_median_duration:.6f}"
    )

    print(
        f"predicted median duration hours: "
        f"{predicted_median_duration / 3600.0:.6f}"
    )

    print(
        f"predicted median duration days: "
        f"{predicted_median_duration / 86400.0:.6f}"
    )

    output = {
        "operation": "H-RUN-011R3",
        "operation_name": (
            "T7 New-Ticket Inference"
        ),
        "status": "PASS",

        "ticket": {
            "id": runtime_row["ID"],
            "creation_time": (
                runtime_row["Creation time"]
            ),
            "summary": runtime_row["Summary"],
            "description": runtime_row["Description"],
        },

        "model": {
            "artifact": str(T7_MODEL),
            "model_type": model_spec["model_type"],
            "feature_count": len(feature_names),
            "feature_order_verified": True,
            "beta_alignment_verified": True,
            "standardization_verified": True,
            "sigma": sigma,
        },

        "training_derived_context": {
            "population": str(T7_TRAIN),
            "rows": int(len(train_df)),
            "creator_frequency_entries": len(
                creator_counts
            ),
            "creator_detail_frequency_entries": len(
                detail_counts
            ),
        },

        "inference": {
            "raw_feature_shape": list(
                X_raw.shape
            ),
            "standardized_feature_shape": list(
                X_standardized.shape
            ),
            "feature_names": feature_names,
            "linear_predictor": (
                linear_predictor
            ),
            "predicted_median_duration_seconds": (
                predicted_median_duration
            ),
            "predicted_median_duration_hours": (
                predicted_median_duration / 3600.0
            ),
            "predicted_median_duration_days": (
                predicted_median_duration / 86400.0
            ),
        },

        "outcomes": {
            "duration_seconds_supplied": False,
            "event_supplied": False,
        },

        "controls": {
            "training": False,
            "retraining": False,
            "model_modification": False,
            "locked_test_use": False,
            "synthetic_target_creation": False,
            "threshold_selection": False,
        },

        "interpretation_boundary": (
            "Frozen T7 Log-Normal AFT inference only. "
            "The output is the model-derived median duration "
            "estimate using the frozen feature standardization "
            "and frozen coefficients. It is not an autonomous "
            "workflow decision, SLA guarantee, calibrated "
            "universal risk score, or human-review threshold."
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
    print("H-RUN-011R3 COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()