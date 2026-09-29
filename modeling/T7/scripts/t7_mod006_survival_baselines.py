import csv
import json
import math
import sys
from bisect import bisect_right
from pathlib import Path


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

TRAIN_PATH = PROJECT_ROOT / "modeling/T7/splits/t7_train.csv"
EVAL_PATH = PROJECT_ROOT / "modeling/T7/splits/t7_evaluation.csv"

CURVE_DIR = PROJECT_ROOT / "modeling/T7/derived"
METRICS_DIR = PROJECT_ROOT / "modeling/T7/metrics"

KM_CURVE_PATH = CURVE_DIR / "t7_mod006_kaplan_meier_curve.csv"
NA_CURVE_PATH = CURVE_DIR / "t7_mod006_nelson_aalen_curve.csv"
AUDIT_PATH = METRICS_DIR / "t7_mod006_survival_baseline_audit.json"


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

csv.field_size_limit(sys.maxsize)


# ---------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------

def load_split(path):
    durations = []
    events = []

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            duration = float(row["duration_seconds"])
            event = int(row["event"])

            if not math.isfinite(duration):
                raise RuntimeError(f"Non-finite duration found in {path}")

            if duration <= 0:
                raise RuntimeError(f"Non-positive duration found in {path}")

            if event not in (0, 1):
                raise RuntimeError(f"Invalid event value found in {path}")

            durations.append(duration)
            events.append(event)

    return durations, events


# ---------------------------------------------------------------------
# Grouped survival statistics
# ---------------------------------------------------------------------

def build_grouped_statistics(durations, events):
    """
    Sort once and construct grouped event/censor counts.

    Returns:
        unique_times
        event_counts
        censor_counts
        at_risk_counts
    """

    observations = sorted(zip(durations, events), key=lambda x: x[0])

    unique_times = []
    event_counts = []
    censor_counts = []
    at_risk_counts = []

    i = 0
    n = len(observations)

    while i < n:
        time = observations[i][0]

        event_count = 0
        censor_count = 0

        j = i

        while j < n and observations[j][0] == time:
            if observations[j][1] == 1:
                event_count += 1
            else:
                censor_count += 1

            j += 1

        unique_times.append(time)
        event_counts.append(event_count)
        censor_counts.append(censor_count)

        i = j

    # At-risk count immediately before each unique time.
    total = len(observations)
    cumulative_before = 0

    for event_count, censor_count in zip(event_counts, censor_counts):
        at_risk_counts.append(total - cumulative_before)
        cumulative_before += event_count + censor_count

    return (
        unique_times,
        event_counts,
        censor_counts,
        at_risk_counts,
    )


# ---------------------------------------------------------------------
# Kaplan-Meier
# ---------------------------------------------------------------------

def build_kaplan_meier(
    unique_times,
    event_counts,
    censor_counts,
    at_risk_counts,
):
    survival = []
    current_survival = 1.0

    for event_count, at_risk in zip(event_counts, at_risk_counts):

        if at_risk <= 0:
            raise RuntimeError("Invalid non-positive risk set.")

        if event_count > 0:
            current_survival *= (
                1.0 - (event_count / at_risk)
            )

        survival.append(current_survival)

    return survival


# ---------------------------------------------------------------------
# Nelson-Aalen
# ---------------------------------------------------------------------

def build_nelson_aalen(
    unique_times,
    event_counts,
    at_risk_counts,
):
    cumulative_hazard = []
    current_hazard = 0.0

    for event_count, at_risk in zip(
        event_counts,
        at_risk_counts,
    ):

        if at_risk <= 0:
            raise RuntimeError("Invalid non-positive risk set.")

        if event_count > 0:
            current_hazard += event_count / at_risk

        cumulative_hazard.append(current_hazard)

    return cumulative_hazard


# ---------------------------------------------------------------------
# Survival lookup
# ---------------------------------------------------------------------

def survival_at_time(query_time, event_times, survival_values):
    """
    KM survival immediately after all events at or before query_time.
    """

    index = bisect_right(event_times, query_time) - 1

    if index < 0:
        return 1.0

    return survival_values[index]


# ---------------------------------------------------------------------
# Censoring KM
# ---------------------------------------------------------------------

def build_censoring_survival(durations, events):
    """
    Construct KM estimate of censoring survival G(t).

    Original event=0 is treated as censoring event for this auxiliary
    censoring-distribution estimator.
    """

    censor_events = [
        1 if event == 0 else 0
        for event in events
    ]

    (
        unique_times,
        censor_event_counts,
        original_event_counts,
        at_risk_counts,
    ) = build_grouped_statistics(
        durations,
        censor_events,
    )

    survival = []
    current_survival = 1.0

    for censor_event_count, at_risk in zip(
        censor_event_counts,
        at_risk_counts,
    ):

        if at_risk <= 0:
            raise RuntimeError(
                "Invalid censoring risk set."
            )

        if censor_event_count > 0:
            current_survival *= (
                1.0
                - censor_event_count / at_risk
            )

        survival.append(current_survival)

    return unique_times, survival


# ---------------------------------------------------------------------
# IPCW Brier score
# ---------------------------------------------------------------------

def ipcw_brier_score(
    eval_durations,
    eval_events,
    prediction_survival,
    horizon,
    censor_times,
    censor_survival,
):
    """
    IPCW Brier score for survival probability at one horizon.

    Event before/equal horizon:
        weight = 1 / G(T-)

    Still under observation beyond horizon:
        weight = 1 / G(horizon)

    Censored before/equal horizon:
        contributes zero.
    """

    g_horizon = survival_at_time(
        horizon,
        censor_times,
        censor_survival,
    )

    if g_horizon <= 0:
        raise RuntimeError(
            f"Censoring survival G(t) reached zero at "
            f"horizon={horizon}"
        )

    score_sum = 0.0
    weight_sum = 0.0

    for duration, event in zip(
        eval_durations,
        eval_events,
    ):

        # Observed event by horizon.
        if event == 1 and duration <= horizon:

            # G(T-) -- survival strictly before T.
            index = bisect_right(
                censor_times,
                duration,
            ) - 1

            if index <= 0:
                g_before = 1.0
            else:
                g_before = censor_survival[index - 1]

            if g_before <= 0:
                continue

            weight = 1.0 / g_before

            # Actual survival outcome at horizon = 0.
            error = prediction_survival ** 2

            score_sum += weight * error
            weight_sum += weight

        # Still event-free and uncensored beyond horizon.
        elif duration > horizon:

            weight = 1.0 / g_horizon

            # Actual survival outcome at horizon = 1.
            error = (1.0 - prediction_survival) ** 2

            score_sum += weight * error
            weight_sum += weight

        # Censored before/equal horizon:
        # no observable contribution.

    if weight_sum == 0:
        return None

    return score_sum / weight_sum


# ---------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------

def percentile(values, q):
    ordered = sorted(values)

    if not ordered:
        raise RuntimeError("Cannot calculate percentile of empty data.")

    position = (len(ordered) - 1) * q
    lower = int(math.floor(position))
    upper = int(math.ceil(position))

    if lower == upper:
        return ordered[lower]

    fraction = position - lower

    return (
        ordered[lower]
        + fraction * (
            ordered[upper] - ordered[lower]
        )
    )


def find_survival_landmark(
    times,
    survival,
    threshold,
):
    for time, value in zip(times, survival):
        if value <= threshold:
            return time

    return None


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():

    CURVE_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("T7 MOD-006 — Efficient Survival Baselines")
    print("=" * 80)

    print("\n[1/8] Loading frozen TRAIN split...")
    train_durations, train_events = load_split(
        TRAIN_PATH
    )

    print(
        f"TRAIN rows: {len(train_durations):,}"
    )

    print("\n[2/8] Loading frozen EVALUATION split...")
    eval_durations, eval_events = load_split(
        EVAL_PATH
    )

    print(
        f"EVAL rows: {len(eval_durations):,}"
    )

    train_event_count = sum(train_events)
    train_censor_count = len(train_events) - train_event_count

    eval_event_count = sum(eval_events)
    eval_censor_count = len(eval_events) - eval_event_count

    print(
        f"TRAIN event=1: {train_event_count:,}"
    )
    print(
        f"TRAIN event=0: {train_censor_count:,}"
    )
    print(
        f"EVAL event=1: {eval_event_count:,}"
    )
    print(
        f"EVAL event=0: {eval_censor_count:,}"
    )

    # ---------------------------------------------------------------
    # Group training data once.
    # ---------------------------------------------------------------

    print(
        "\n[3/8] Building grouped TRAIN survival statistics..."
    )

    (
        train_times,
        train_event_counts,
        train_censor_counts,
        train_at_risk,
    ) = build_grouped_statistics(
        train_durations,
        train_events,
    )

    print(
        f"Unique TRAIN duration times: "
        f"{len(train_times):,}"
    )

    # ---------------------------------------------------------------
    # Kaplan-Meier
    # ---------------------------------------------------------------

    print(
        "\n[4/8] Building Kaplan-Meier baseline..."
    )

    km_survival = build_kaplan_meier(
        train_times,
        train_event_counts,
        train_censor_counts,
        train_at_risk,
    )

    median_survival = None

    for time, survival in zip(
        train_times,
        km_survival,
    ):
        if survival <= 0.5:
            median_survival = time
            break

    landmark_75 = find_survival_landmark(
        train_times,
        km_survival,
        0.75,
    )

    landmark_90 = find_survival_landmark(
        train_times,
        km_survival,
        0.90,
    )

    print(
        f"Median survival: "
        f"{median_survival}"
    )

    print(
        f"25% resolved landmark "
        f"(S(t)<=0.75): {landmark_75}"
    )

    print(
        f"10% resolved landmark "
        f"(S(t)<=0.90): {landmark_90}"
    )

    # ---------------------------------------------------------------
    # Nelson-Aalen
    # ---------------------------------------------------------------

    print(
        "\n[5/8] Building Nelson-Aalen baseline..."
    )

    na_hazard = build_nelson_aalen(
        train_times,
        train_event_counts,
        train_at_risk,
    )

    final_cumulative_hazard = na_hazard[-1]

    print(
        f"Final cumulative hazard: "
        f"{final_cumulative_hazard:.15f}"
    )

    # ---------------------------------------------------------------
    # Curves
    # ---------------------------------------------------------------

    print(
        "\n[6/8] Writing survival baseline curves..."
    )

    with KM_CURVE_PATH.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "duration_seconds",
            "event_count",
            "censor_count",
            "at_risk",
            "kaplan_meier_survival",
        ])

        for row in zip(
            train_times,
            train_event_counts,
            train_censor_counts,
            train_at_risk,
            km_survival,
        ):
            writer.writerow(row)

    with NA_CURVE_PATH.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "duration_seconds",
            "event_count",
            "at_risk",
            "nelson_aalen_cumulative_hazard",
        ])

        for row in zip(
            train_times,
            train_event_counts,
            train_at_risk,
            na_hazard,
        ):
            writer.writerow(row)

    # ---------------------------------------------------------------
    # Censoring distribution
    # ---------------------------------------------------------------

    print(
        "\n[7/8] Computing efficient IPCW Brier diagnostics..."
    )

    (
        censor_times,
        censor_survival,
    ) = build_censoring_survival(
        train_durations,
        train_events,
    )

    observed_train_durations = [
        duration
        for duration, event in zip(
            train_durations,
            train_events,
        )
        if event == 1
    ]

    # Preserve the same three representative event-time
    # horizons used by the original MOD-006 implementation.
    horizons = [
        percentile(
            observed_train_durations,
            0.25,
        ),
        percentile(
            observed_train_durations,
            0.50,
        ),
        percentile(
            observed_train_durations,
            0.75,
        ),
    ]

    brier_results = []

    for horizon in horizons:

        prediction_survival = survival_at_time(
            horizon,
            train_times,
            km_survival,
        )

        score = ipcw_brier_score(
            eval_durations=eval_durations,
            eval_events=eval_events,
            prediction_survival=prediction_survival,
            horizon=horizon,
            censor_times=censor_times,
            censor_survival=censor_survival,
        )

        result = {
            "horizon_seconds": horizon,
            "km_predicted_survival": prediction_survival,
            "ipcw_brier_score": score,
        }

        brier_results.append(result)

        print(
            f"\nHorizon: {horizon:.6f} seconds"
        )
        print(
            f"  KM predicted survival: "
            f"{prediction_survival:.6f}"
        )
        print(
            f"  IPCW Brier score: "
            f"{score:.12f}"
        )

    # ---------------------------------------------------------------
    # Audit
    # ---------------------------------------------------------------

    print(
        "\n[8/8] Writing MOD-006 audit..."
    )

    audit = {
        "task": "T7 Resolution-Time Estimation",
        "operation": "MOD-006",
        "status": "COMPLETE",
        "baseline_family": "nonparametric_survival",
        "training_source": str(TRAIN_PATH),
        "evaluation_source": str(EVAL_PATH),

        "train_rows": len(train_durations),
        "evaluation_rows": len(eval_durations),

        "train_event_1": train_event_count,
        "train_event_0": train_censor_count,
        "evaluation_event_1": eval_event_count,
        "evaluation_event_0": eval_censor_count,

        "kaplan_meier": {
            "unique_duration_times": len(train_times),
            "median_survival_seconds": median_survival,
            "landmark_s_0_75_seconds": landmark_75,
            "landmark_s_0_90_seconds": landmark_90,
        },

        "nelson_aalen": {
            "unique_duration_times": len(train_times),
            "final_cumulative_hazard": final_cumulative_hazard,
        },

        "ipcw_brier": {
            "horizons": brier_results,
            "censoring_distribution_fitted_on": "TRAIN_ONLY",
        },

        "evaluation_integrity": {
            "evaluation_fitting": False,
            "feature_usage": False,
            "raw_archive_access": False,
            "chronological_split_respected": True,
        },

        "c_index": {
            "reported": False,
            "reason": (
                "Population-level KM baseline assigns the same "
                "survival trajectory to every evaluation ticket; "
                "therefore an individual risk ordering is not "
                "defined for a meaningful concordance calculation."
            ),
        },

        "artifacts": {
            "kaplan_meier_curve": str(KM_CURVE_PATH),
            "nelson_aalen_curve": str(NA_CURVE_PATH),
            "audit": str(AUDIT_PATH),
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
    print("MOD-006 COMPLETE")
    print("=" * 80)

    print(
        f"\nAudit: {AUDIT_PATH}"
    )
    print(
        f"KM curve: {KM_CURVE_PATH}"
    )
    print(
        f"NA curve: {NA_CURVE_PATH}"
    )


if __name__ == "__main__":
    main()