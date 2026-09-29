import csv
import json
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

PREDICTION_PATH = (
    PROJECT_ROOT
    / "modeling/T7/derived/t7_mod007_evaluation_predictions.csv"
)

AUDIT_PATH = (
    PROJECT_ROOT
    / "modeling/T7/metrics/t7_mod009_survival_calibration_audit.json"
)

RESULT_PATH = (
    PROJECT_ROOT
    / "modeling/T7/metrics/t7_mod009_survival_calibration.csv"
)

csv.field_size_limit(sys.maxsize)


# ============================================================================
# LOAD EVALUATION
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

        for row in reader:

            ids.append(row["ID"])

            durations.append(
                float(row["duration_seconds"])
            )

            events.append(
                int(row["event"])
            )

    return (
        ids,
        np.asarray(durations),
        np.asarray(events),
    )


# ============================================================================
# LOAD PREDICTIONS
# ============================================================================

def load_predictions(path):

    ids = []
    durations = []
    events = []
    horizons = []
    predictions = []

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        fields = reader.fieldnames or []

        horizon_columns = [
            field
            for field in fields
            if field.startswith(
                "survival_probability_at_"
            )
        ]

        for field in horizon_columns:

            horizon = float(
                field[
                    len(
                        "survival_probability_at_"
                    ):-8]
            )

            horizons.append(horizon)

        for row in reader:

            ids.append(row["ID"])

            durations.append(
                float(row["duration_seconds"])
            )

            events.append(
                int(row["event"])
            )

            predictions.append([
                float(row[field])
                for field in horizon_columns
            ])

    return (
        ids,
        np.asarray(durations),
        np.asarray(events),
        np.asarray(horizons),
        np.asarray(predictions),
    )


# ============================================================================
# CALIBRATION
# ============================================================================

def calibration_for_horizon(
    durations,
    events,
    predictions,
    horizon,
    n_bins=10,
):
    """
    Calibration-style diagnostic.

    Predicted survival is grouped into quantile bins.

    Observed survival proxy:

        1 - event proportion among tickets
        with an observable event/censoring outcome
        at or before the horizon.

    Tickets censored before the horizon are excluded
    from the observed-outcome calculation.

    This is explicitly a diagnostic, not a formal
    IPCW calibration estimator.
    """

    observable = (
        (events == 1)
        | (durations > horizon)
    )

    observable_predictions = predictions[
        observable
    ]

    observable_durations = durations[
        observable
    ]

    observable_events = events[
        observable
    ]

    if len(observable_predictions) == 0:
        return []

    quantiles = np.quantile(
        observable_predictions,
        np.linspace(
            0.0,
            1.0,
            n_bins + 1,
        ),
    )

    results = []

    for i in range(n_bins):

        lower = quantiles[i]
        upper = quantiles[i + 1]

        if i == n_bins - 1:

            mask = (
                (observable_predictions >= lower)
                & (observable_predictions <= upper)
            )

        else:

            mask = (
                (observable_predictions >= lower)
                & (observable_predictions < upper)
            )

        if not np.any(mask):
            continue

        p = observable_predictions[mask]

        d = observable_durations[mask]

        e = observable_events[mask]

        # For observable tickets:
        #
        # event by horizon -> survival outcome = 0
        # still unresolved at horizon -> survival = 1
        #
        # Early censoring is excluded above.

        observed_survival = np.where(
            (e == 1) & (d <= horizon),
            0.0,
            1.0,
        )

        results.append({
            "bin": i + 1,
            "n": int(len(p)),
            "predicted_survival_mean": float(
                np.mean(p)
            ),
            "observed_survival_mean": float(
                np.mean(observed_survival)
            ),
            "absolute_calibration_gap": float(
                abs(
                    np.mean(p)
                    - np.mean(observed_survival)
                )
            ),
            "predicted_min": float(
                np.min(p)
            ),
            "predicted_max": float(
                np.max(p)
            ),
        })

    return results


# ============================================================================
# MAIN
# ============================================================================

def main():

    print("=" * 80)
    print(
        "T7 MOD-009 — Survival Calibration / Reliability Analysis"
    )
    print("=" * 80)

    print(
        "\n[1/5] Loading frozen evaluation split..."
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

    print(
        "\n[2/5] Loading MOD-007 predictions..."
    )

    (
        prediction_ids,
        prediction_durations,
        prediction_events,
        horizons,
        prediction_matrix,
    ) = load_predictions(
        PREDICTION_PATH
    )

    if eval_ids != prediction_ids:
        raise RuntimeError(
            "Evaluation and prediction IDs do not align."
        )

    if not np.array_equal(
        eval_durations,
        prediction_durations,
    ):
        raise RuntimeError(
            "Evaluation durations do not align."
        )

    if not np.array_equal(
        eval_events,
        prediction_events,
    ):
        raise RuntimeError(
            "Evaluation events do not align."
        )

    print(
        "Population alignment: PASS"
    )

    print(
        "\n[3/5] Computing calibration diagnostics..."
    )

    all_results = []

    audit_horizons = []

    for i, horizon in enumerate(horizons):

        predictions = prediction_matrix[
            :,
            i,
        ]

        calibration = calibration_for_horizon(
            eval_durations,
            eval_events,
            predictions,
            horizon,
        )

        observable_mask = (
            (eval_events == 1)
            | (eval_durations > horizon)
        )

        observable_count = int(
            np.sum(observable_mask)
        )

        early_censor_count = int(
            len(eval_ids)
            - observable_count
        )

        overall_predicted = float(
            np.mean(predictions)
        )

        overall_observed = float(
            np.mean(
                np.where(
                    (eval_events == 1)
                    & (
                        eval_durations
                        <= horizon
                    ),
                    0.0,
                    1.0,
                )[observable_mask]
            )
        )

        overall_gap = abs(
            overall_predicted
            - overall_observed
        )

        horizon_result = {
            "horizon_seconds": float(
                horizon
            ),
            "evaluation_rows": len(
                eval_ids
            ),
            "observable_rows": observable_count,
            "early_censored_rows": (
                early_censor_count
            ),
            "overall_predicted_survival": (
                overall_predicted
            ),
            "overall_observed_survival_proxy": (
                overall_observed
            ),
            "overall_absolute_calibration_gap": (
                float(overall_gap)
            ),
            "calibration_bins": calibration,
        }

        audit_horizons.append(
            horizon_result
        )

        for row in calibration:

            all_results.append([
                horizon,
                row["bin"],
                row["n"],
                row[
                    "predicted_survival_mean"
                ],
                row[
                    "observed_survival_mean"
                ],
                row[
                    "absolute_calibration_gap"
                ],
                row["predicted_min"],
                row["predicted_max"],
            ])

        print(
            f"\nHorizon: {horizon:.6f} seconds"
        )

        print(
            f"  Observable rows: "
            f"{observable_count:,}"
        )

        print(
            f"  Early-censored rows: "
            f"{early_censor_count:,}"
        )

        print(
            f"  Mean predicted survival: "
            f"{overall_predicted:.8f}"
        )

        print(
            f"  Observed survival proxy: "
            f"{overall_observed:.8f}"
        )

        print(
            f"  Absolute calibration gap: "
            f"{overall_gap:.8f}"
        )

    print(
        "\n[4/5] Writing calibration table..."
    )

    with RESULT_PATH.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "horizon_seconds",
            "bin",
            "n",
            "predicted_survival_mean",
            "observed_survival_mean",
            "absolute_calibration_gap",
            "predicted_min",
            "predicted_max",
        ])

        writer.writerows(
            all_results
        )

    print(
        "\n[5/5] Writing MOD-009 audit..."
    )

    audit = {
        "task": "T7 Resolution-Time Estimation",
        "operation": "MOD-009",
        "status": "COMPLETE",

        "purpose": (
            "Calibration/reliability diagnostic "
            "for MOD-007 survival predictions."
        ),

        "evaluation_rows": len(
            eval_ids
        ),

        "prediction_alignment": {
            "id_match": True,
            "duration_match": True,
            "event_match": True,
        },

        "methodological_note": (
            "This operation is a calibration-style "
            "diagnostic. It is not a formal IPCW "
            "survival calibration estimator. "
            "Tickets censored before the horizon "
            "are excluded from the observed-outcome "
            "proxy."
        ),

        "horizons": audit_horizons,

        "integrity": {
            "model_refit": False,
            "new_features": False,
            "raw_archive_access": False,
            "evaluation_population_changed": False,
        },

        "artifacts": {
            "calibration_table": str(
                RESULT_PATH
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
        "MOD-009 COMPLETE"
    )
    print("=" * 80)

    print(
        f"\nCalibration table: "
        f"{RESULT_PATH}"
    )

    print(
        f"Audit: "
        f"{AUDIT_PATH}"
    )


if __name__ == "__main__":
    main()