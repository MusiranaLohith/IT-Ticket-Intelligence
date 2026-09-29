import csv
import json
import math
import sys
from pathlib import Path

import numpy as np


# ============================================================================
# PATHS
# ============================================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

EVAL_PATH = (
    PROJECT_ROOT
    / "modeling/T7/splits/t7_evaluation.csv"
)

KM_CURVE_PATH = (
    PROJECT_ROOT
    / "modeling/T7/derived/t7_mod006_kaplan_meier_curve.csv"
)

MOD006_AUDIT_PATH = (
    PROJECT_ROOT
    / "modeling/T7/metrics/t7_mod006_survival_baseline_audit.json"
)

MOD007_AUDIT_PATH = (
    PROJECT_ROOT
    / "modeling/T7/metrics/t7_mod007_predictive_survival_audit.json"
)

PREDICTION_PATH = (
    PROJECT_ROOT
    / "modeling/T7/derived/t7_mod007_evaluation_predictions.csv"
)

AUDIT_PATH = (
    PROJECT_ROOT
    / "modeling/T7/metrics/t7_mod008_predictive_vs_reference_audit.json"
)

COMPARISON_PATH = (
    PROJECT_ROOT
    / "modeling/T7/metrics/t7_mod008_predictive_vs_reference.csv"
)

csv.field_size_limit(sys.maxsize)


# ============================================================================
# LOADING
# ============================================================================

def load_evaluation(path):

    ids = []
    durations = []
    events = []

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        required = {
            "ID",
            "duration_seconds",
            "event",
        }

        missing = required - set(
            reader.fieldnames or []
        )

        if missing:
            raise RuntimeError(
                f"Evaluation split missing: "
                f"{sorted(missing)}"
            )

        for row in reader:

            ids.append(row["ID"])
            durations.append(
                float(
                    row["duration_seconds"]
                )
            )
            events.append(
                int(row["event"])
            )

    return (
        ids,
        np.asarray(
            durations,
            dtype=np.float64,
        ),
        np.asarray(
            events,
            dtype=np.int8,
        ),
    )


def load_predictions(path):

    ids = []

    durations = []
    events = []

    median_survival = []

    horizon_columns = []

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        fields = reader.fieldnames or []

        required = {
            "ID",
            "duration_seconds",
            "event",
            "predicted_median_survival_seconds",
        }

        missing = required - set(fields)

        if missing:
            raise RuntimeError(
                f"Prediction artifact missing: "
                f"{sorted(missing)}"
            )

        horizon_columns = [
            field
            for field in fields
            if field.startswith(
                "survival_probability_at_"
            )
        ]

        if not horizon_columns:
            raise RuntimeError(
                "No survival-probability horizon columns found."
            )

        for field in horizon_columns:
            print(
                f"Found prediction horizon: {field}"
            )

        for row in reader:

            ids.append(row["ID"])

            durations.append(
                float(
                    row["duration_seconds"]
                )
            )

            events.append(
                int(row["event"])
            )

            median_survival.append(
                float(
                    row[
                        "predicted_median_survival_seconds"
                    ]
                )
            )

    prediction_matrix = np.empty(
        (
            len(ids),
            len(horizon_columns),
        ),
        dtype=np.float64,
    )

    # Reload only the small prediction columns.
    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        for i, row in enumerate(reader):

            for j, field in enumerate(
                horizon_columns
            ):

                prediction_matrix[
                    i,
                    j,
                ] = float(
                    row[field]
                )

    return (
        ids,
        np.asarray(
            durations,
            dtype=np.float64,
        ),
        np.asarray(
            events,
            dtype=np.int8,
        ),
        np.asarray(
            median_survival,
            dtype=np.float64,
        ),
        horizon_columns,
        prediction_matrix,
    )


def load_km_curve(path):

    times = []
    survival = []

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            times.append(
                float(
                    row["duration_seconds"]
                )
            )

            survival.append(
                float(
                    row["kaplan_meier_survival"]
                )
            )

    return (
        np.asarray(
            times,
            dtype=np.float64,
        ),
        np.asarray(
            survival,
            dtype=np.float64,
        ),
    )


def load_json(path):

    with path.open(
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


# ============================================================================
# KM LOOKUP
# ============================================================================

def km_survival_at(
    horizon,
    times,
    survival,
):

    index = np.searchsorted(
        times,
        horizon,
        side="right",
    ) - 1

    if index < 0:
        return 1.0

    return float(
        survival[index]
    )


# ============================================================================
# TRAIN-ONLY CENSORING KM
# ============================================================================

def build_censoring_km(
    durations,
    events,
):

    observations = sorted(
        zip(
            durations,
            events,
        ),
        key=lambda x: x[0],
    )

    n = len(observations)

    times = []
    censor_counts = []
    at_risk = []

    i = 0
    removed = 0

    while i < n:

        time = observations[i][0]

        j = i
        censor_count = 0

        while (
            j < n
            and observations[j][0] == time
        ):

            if observations[j][1] == 0:
                censor_count += 1

            j += 1

        times.append(time)
        censor_counts.append(
            censor_count
        )
        at_risk.append(
            n - removed
        )

        removed += j - i
        i = j

    survival = []
    current = 1.0

    for censor_count, risk in zip(
        censor_counts,
        at_risk,
    ):

        if censor_count:
            current *= (
                1.0
                - censor_count / risk
            )

        survival.append(current)

    return (
        np.asarray(
            times,
            dtype=np.float64,
        ),
        np.asarray(
            survival,
            dtype=np.float64,
        ),
    )


# ============================================================================
# IPCW BRIER
# ============================================================================

def censor_survival_at(
    time,
    times,
    survival,
):

    index = np.searchsorted(
        times,
        time,
        side="right",
    ) - 1

    if index < 0:
        return 1.0

    return float(
        survival[index]
    )


def censor_survival_before(
    time,
    times,
    survival,
):

    index = np.searchsorted(
        times,
        time,
        side="left",
    ) - 1

    if index < 0:
        return 1.0

    return float(
        survival[index]
    )


def ipcw_brier(
    durations,
    events,
    predictions,
    horizon,
    censor_times,
    censor_survival,
):

    g_horizon = censor_survival_at(
        horizon,
        censor_times,
        censor_survival,
    )

    if g_horizon <= 0:
        raise RuntimeError(
            "Censoring survival reached zero."
        )

    total = 0.0
    weight_total = 0.0

    for duration, event, prediction in zip(
        durations,
        events,
        predictions,
    ):

        if (
            event == 1
            and duration <= horizon
        ):

            g_before = (
                censor_survival_before(
                    duration,
                    censor_times,
                    censor_survival,
                )
            )

            if g_before <= 0:
                continue

            weight = 1.0 / g_before

            total += (
                weight
                * prediction ** 2
            )

            weight_total += weight

        elif duration > horizon:

            weight = 1.0 / g_horizon

            total += (
                weight
                * (1.0 - prediction) ** 2
            )

            weight_total += weight

    if weight_total == 0:
        return None

    return (
        total / weight_total
    )


# ============================================================================
# MAIN
# ============================================================================

def main():

    print("=" * 80)
    print(
        "T7 MOD-008 — Predictive vs Reference Survival Evaluation"
    )
    print("=" * 80)

    # -----------------------------------------------------------------
    # 1. Load frozen evaluation
    # -----------------------------------------------------------------

    print(
        "\n[1/7] Loading frozen evaluation split..."
    )

    (
        eval_ids,
        eval_durations,
        eval_events,
    ) = load_evaluation(
        EVAL_PATH
    )

    print(
        f"Evaluation rows: {len(eval_ids):,}"
    )

    # -----------------------------------------------------------------
    # 2. Load MOD-007 predictions
    # -----------------------------------------------------------------

    print(
        "\n[2/7] Loading MOD-007 predictions..."
    )

    (
        prediction_ids,
        prediction_durations,
        prediction_events,
        median_survival,
        horizon_columns,
        prediction_matrix,
    ) = load_predictions(
        PREDICTION_PATH
    )

    print(
        f"Prediction rows: "
        f"{len(prediction_ids):,}"
    )

    if len(eval_ids) != len(prediction_ids):
        raise RuntimeError(
            "Evaluation/prediction row counts differ."
        )

    # Exact ordered alignment.
    if eval_ids != prediction_ids:
        raise RuntimeError(
            "Evaluation IDs and prediction IDs "
            "are not in identical order."
        )

    if not np.array_equal(
        eval_events,
        prediction_events,
    ):
        raise RuntimeError(
            "Evaluation event labels differ "
            "from prediction artifact."
        )

    if not np.array_equal(
        eval_durations,
        prediction_durations,
    ):
        raise RuntimeError(
            "Evaluation durations differ "
            "from prediction artifact."
        )

    print(
        "Population alignment: PASS"
    )

    # -----------------------------------------------------------------
    # 3. Load KM reference
    # -----------------------------------------------------------------

    print(
        "\n[3/7] Loading MOD-006 KM reference..."
    )

    (
        km_times,
        km_survival,
    ) = load_km_curve(
        KM_CURVE_PATH
    )

    mod006_audit = load_json(
        MOD006_AUDIT_PATH
    )

    mod007_audit = load_json(
        MOD007_AUDIT_PATH
    )

    print(
        f"KM curve points: "
        f"{len(km_times):,}"
    )

    # -----------------------------------------------------------------
    # 4. Recover horizons
    # -----------------------------------------------------------------

    print(
        "\n[4/7] Resolving evaluation horizons..."
    )

    horizons = []

    for field in horizon_columns:

        prefix = (
            "survival_probability_at_"
        )

        if not field.startswith(prefix):
            raise RuntimeError(
                f"Unexpected prediction column: {field}"
            )

        horizon = float(
            field[len(prefix):-8]
        )

        # The suffix is "_seconds".
        horizons.append(horizon)

    print(
        "Horizon values:"
    )

    for horizon in horizons:
        print(
            f"  {horizon:.6f} seconds"
        )

    # -----------------------------------------------------------------
    # 5. Recompute metrics from frozen artifacts
    # -----------------------------------------------------------------

    print(
        "\n[5/7] Computing reference and predictive metrics..."
    )

    # Train-only censoring distribution.
    #
    # We recover the TRAIN durations/events from the MOD-006
    # audit context by loading the frozen TRAIN split.
    train_path = (
        PROJECT_ROOT
        / "modeling/T7/splits/t7_train.csv"
    )

    train_durations = []
    train_events = []

    with train_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            train_durations.append(
                float(
                    row["duration_seconds"]
                )
            )

            train_events.append(
                int(row["event"])
            )

    train_durations = np.asarray(
        train_durations,
        dtype=np.float64,
    )

    train_events = np.asarray(
        train_events,
        dtype=np.int8,
    )

    (
        censor_times,
        censor_survival,
    ) = build_censoring_km(
        train_durations,
        train_events,
    )

    results = []

    for index, horizon in enumerate(
        horizons
    ):

        predictive = (
            prediction_matrix[
                :,
                index,
            ]
        )

        reference_survival = (
            km_survival_at(
                horizon,
                km_times,
                km_survival,
            )
        )

        reference_predictions = np.full(
            len(eval_ids),
            reference_survival,
            dtype=np.float64,
        )

        predictive_brier = (
            ipcw_brier(
                eval_durations,
                eval_events,
                predictive,
                horizon,
                censor_times,
                censor_survival,
            )
        )

        reference_brier = (
            ipcw_brier(
                eval_durations,
                eval_events,
                reference_predictions,
                horizon,
                censor_times,
                censor_survival,
            )
        )

        brier_delta = (
            predictive_brier
            - reference_brier
        )

        relative_change = (
            brier_delta
            / reference_brier
        )

        predictive_mean = float(
            np.mean(
                predictive
            )
        )

        predictive_std = float(
            np.std(
                predictive
            )
        )

        predictive_min = float(
            np.min(
                predictive
            )
        )

        predictive_max = float(
            np.max(
                predictive
            )
        )

        result = {
            "horizon_seconds": horizon,

            "km_reference_survival": (
                reference_survival
            ),

            "predictive_mean_survival": (
                predictive_mean
            ),

            "predictive_std_survival": (
                predictive_std
            ),

            "predictive_min_survival": (
                predictive_min
            ),

            "predictive_max_survival": (
                predictive_max
            ),

            "km_reference_ipcw_brier": (
                reference_brier
            ),

            "predictive_ipcw_brier": (
                predictive_brier
            ),

            "predictive_minus_reference_brier": (
                brier_delta
            ),

            "relative_brier_change": (
                relative_change
            ),
        }

        results.append(
            result
        )

        print(
            f"\nHorizon: "
            f"{horizon:.6f} seconds"
        )

        print(
            f"  KM survival: "
            f"{reference_survival:.8f}"
        )

        print(
            f"  KM Brier: "
            f"{reference_brier:.12f}"
        )

        print(
            f"  Predictive mean survival: "
            f"{predictive_mean:.8f}"
        )

        print(
            f"  Predictive Brier: "
            f"{predictive_brier:.12f}"
        )

        print(
            f"  Brier delta: "
            f"{brier_delta:.12f}"
        )

    # -----------------------------------------------------------------
    # 6. Write comparison table
    # -----------------------------------------------------------------

    print(
        "\n[6/7] Writing comparison table..."
    )

    with COMPARISON_PATH.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "horizon_seconds",
            "km_reference_survival",
            "predictive_mean_survival",
            "predictive_std_survival",
            "predictive_min_survival",
            "predictive_max_survival",
            "km_reference_ipcw_brier",
            "predictive_ipcw_brier",
            "predictive_minus_reference_brier",
            "relative_brier_change",
        ])

        for result in results:

            writer.writerow([
                result[
                    "horizon_seconds"
                ],
                result[
                    "km_reference_survival"
                ],
                result[
                    "predictive_mean_survival"
                ],
                result[
                    "predictive_std_survival"
                ],
                result[
                    "predictive_min_survival"
                ],
                result[
                    "predictive_max_survival"
                ],
                result[
                    "km_reference_ipcw_brier"
                ],
                result[
                    "predictive_ipcw_brier"
                ],
                result[
                    "predictive_minus_reference_brier"
                ],
                result[
                    "relative_brier_change"
                ],
            ])

    # -----------------------------------------------------------------
    # 7. Audit
    # -----------------------------------------------------------------

    print(
        "\n[7/7] Writing MOD-008 audit..."
    )

    c_index = (
        mod007_audit
        .get(
            "evaluation_metrics",
            {},
        )
        .get(
            "harrell_concordance_index"
        )
    )

    audit = {
        "task": "T7 Resolution-Time Estimation",

        "operation": "MOD-008",

        "status": "COMPLETE",

        "purpose": (
            "Compare the first predictive survival "
            "baseline against the MOD-006 "
            "nonparametric reference on the "
            "frozen evaluation population."
        ),

        "evaluation_population": {
            "rows": len(eval_ids),
            "events": int(
                np.sum(eval_events)
            ),
            "right_censored": int(
                len(eval_events)
                - np.sum(eval_events)
            ),
        },

        "alignment": {
            "evaluation_prediction_population": True,
            "id_order_match": True,
            "duration_match": True,
            "event_match": True,
        },

        "models_compared": {
            "reference": (
                "MOD-006 Kaplan-Meier"
            ),
            "predictive": (
                "MOD-007 Weibull AFT"
            ),
        },

        "predictive_model": {
            "harrell_concordance_index": c_index,
            "source": str(
                MOD007_AUDIT_PATH
            ),
        },

        "horizon_results": results,

        "integrity": {
            "retraining": False,
            "evaluation_fitting": False,
            "raw_archive_access": False,
            "new_features": False,
            "chronological_split_changed": False,
            "train_only_censoring_distribution": True,
        },

        "source_artifacts": {
            "evaluation_split": str(
                EVAL_PATH
            ),
            "km_curve": str(
                KM_CURVE_PATH
            ),
            "mod006_audit": str(
                MOD006_AUDIT_PATH
            ),
            "mod007_audit": str(
                MOD007_AUDIT_PATH
            ),
            "mod007_predictions": str(
                PREDICTION_PATH
            ),
        },

        "output_artifacts": {
            "comparison": str(
                COMPARISON_PATH
            ),
            "audit": str(
                AUDIT_PATH
            ),
        },
    }

    with AUDIT_PATH.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            audit,
            f,
            indent=2,
        )

    print("\n" + "=" * 80)
    print(
        "MOD-008 COMPLETE"
    )
    print("=" * 80)

    print(
        f"\nComparison: "
        f"{COMPARISON_PATH}"
    )

    print(
        f"Audit: "
        f"{AUDIT_PATH}"
    )


if __name__ == "__main__":
    main()