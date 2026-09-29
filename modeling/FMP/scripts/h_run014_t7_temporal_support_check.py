from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
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
          "h_run014_t7_temporal_support_check.json"
)

RUNTIME_CREATION_TIME = "2026-09-26T18:03:00Z"


def main():
    print("=" * 72)
    print("H-RUN-014 — T7 TEMPORAL SUPPORT CHECK")
    print("=" * 72)

    print("\n[CONTROL]")
    print("training/retraining: NO")
    print("model modification: NO")
    print("prediction modification: NO")
    print("locked-test use: NO")

    if not T7_MODEL.exists():
        raise FileNotFoundError(
            f"Missing T7 model: {T7_MODEL}"
        )

    if not T7_TRAIN.exists():
        raise FileNotFoundError(
            f"Missing T7 training population: {T7_TRAIN}"
        )

    model = json.loads(
        T7_MODEL.read_text(
            encoding="utf-8"
        )
    )

    train = pd.read_csv(
        T7_TRAIN
    )

    creation = pd.to_datetime(
        train["Creation time"],
        errors="coerce",
        utc=True,
    )

    if creation.isna().any():
        raise RuntimeError(
            "Training population contains "
            "unparseable Creation time values."
        )

    years = creation.dt.year

    runtime_time = pd.Timestamp(
        RUNTIME_CREATION_TIME
    )

    runtime_year = int(
        runtime_time.year
    )

    raw_year_runtime = (
                               runtime_year - 2010.0
                       ) / 10.0

    feature_names = model["feature_names"]

    mean = np.asarray(
        model["standardization_mean"],
        dtype=np.float64,
    )

    std = np.asarray(
        model["standardization_std"],
        dtype=np.float64,
    )

    year_index = feature_names.index(
        "creation_year_scaled"
    )

    standardized_runtime_year = (
                                        raw_year_runtime - mean[year_index]
                                ) / std[year_index]

    train_raw_year = (
                             years.astype(float) - 2010.0
                     ) / 10.0

    train_standardized_year = (
                                      train_raw_year - mean[year_index]
                              ) / std[year_index]

    print("\n[TRAINING TIME RANGE]")

    print(
        f"earliest year: "
        f"{int(years.min())}"
    )

    print(
        f"latest year: "
        f"{int(years.max())}"
    )

    print(
        f"unique years: "
        f"{sorted(years.unique().tolist())}"
    )

    print("\n[TRAINING CREATION YEAR COUNTS]")

    year_counts = (
        years.value_counts()
        .sort_index()
    )

    for year, count in year_counts.items():
        print(
            f"{int(year)}: {int(count)}"
        )

    print("\n[RUNTIME YEAR]")

    print(
        f"runtime creation time: "
        f"{RUNTIME_CREATION_TIME}"
    )

    print(
        f"runtime year: "
        f"{runtime_year}"
    )

    print(
        f"runtime raw creation_year_scaled: "
        f"{raw_year_runtime:.6f}"
    )

    print(
        f"runtime standardized value: "
        f"{standardized_runtime_year:.6f}"
    )

    print("\n[TRAINING STANDARDIZED YEAR RANGE]")

    print(
        f"minimum: "
        f"{train_standardized_year.min():.6f}"
    )

    print(
        f"maximum: "
        f"{train_standardized_year.max():.6f}"
    )

    print(
        f"median: "
        f"{train_standardized_year.median():.6f}"
    )

    print("\n[SUPPORT STATUS]")

    inside_training_range = (
            years.min()
            <= runtime_year
            <= years.max()
    )

    if inside_training_range:
        support_status = "INSIDE_TRAINING_YEAR_RANGE"
        print(
            "runtime year is inside the observed "
            "training year range."
        )
    else:
        support_status = "OUTSIDE_TRAINING_YEAR_RANGE"
        print(
            "runtime year is OUTSIDE the observed "
            "training year range."
        )

    output = {
        "operation": "H-RUN-014",
        "operation_name": (
            "T7 Temporal Support Check"
        ),
        "status": "PASS",
        "runtime_creation_time": (
            RUNTIME_CREATION_TIME
        ),
        "training_year_range": {
            "min": int(years.min()),
            "max": int(years.max()),
            "unique_years": sorted(
                years.unique().tolist()
            ),
        },
        "training_year_counts": {
            str(int(year)): int(count)
            for year, count in year_counts.items()
        },
        "runtime_year": runtime_year,
        "runtime_raw_creation_year_scaled": (
            raw_year_runtime
        ),
        "runtime_standardized_creation_year": (
            float(standardized_runtime_year)
        ),
        "training_standardized_creation_year_range": {
            "min": float(
                train_standardized_year.min()
            ),
            "max": float(
                train_standardized_year.max()
            ),
            "median": float(
                train_standardized_year.median()
            ),
        },
        "support_status": support_status,
        "controls": {
            "training": False,
            "retraining": False,
            "model_modification": False,
            "prediction_modification": False,
            "locked_test_use": False,
        },
        "interpretation_boundary": (
            "This operation checks temporal feature support "
            "relative to the frozen T7 training population. "
            "It does not establish model validity, accuracy, "
            "calibration, or a production policy."
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
    print("H-RUN-014 COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()