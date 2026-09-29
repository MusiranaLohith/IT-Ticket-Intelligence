import csv
import json
import math
import sys
from bisect import bisect_right
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
from scipy.optimize import minimize


# ============================================================================
# PATHS
# ============================================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

TRAIN_PATH = PROJECT_ROOT / "modeling/T7/splits/t7_train.csv"
EVAL_PATH = PROJECT_ROOT / "modeling/T7/splits/t7_evaluation.csv"

METRICS_DIR = PROJECT_ROOT / "modeling/T7/metrics"
DERIVED_DIR = PROJECT_ROOT / "modeling/T7/derived"

MODEL_PATH = (
    METRICS_DIR
    / "t7_mod007_weibull_aft_model.json"
)

PREDICTION_PATH = (
    DERIVED_DIR
    / "t7_mod007_evaluation_predictions.csv"
)

AUDIT_PATH = (
    METRICS_DIR
    / "t7_mod007_predictive_survival_audit.json"
)

csv.field_size_limit(sys.maxsize)


# ============================================================================
# DATA LOADING
# ============================================================================

REQUIRED_COLUMNS = {
    "ID",
    "Creation time",
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
    "duration_seconds",
    "event",
}


def read_rows(path):
    rows = []

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        missing = REQUIRED_COLUMNS - set(
            reader.fieldnames or []
        )

        if missing:
            raise RuntimeError(
                f"{path} missing columns: "
                f"{sorted(missing)}"
            )

        for row in reader:

            duration = float(
                row["duration_seconds"]
            )

            event = int(row["event"])

            if duration <= 0:
                raise RuntimeError(
                    f"Non-positive duration: {row['ID']}"
                )

            if event not in (0, 1):
                raise RuntimeError(
                    f"Invalid event: {row['ID']}"
                )

            rows.append(row)

    return rows


# ============================================================================
# CREATION-TIME FEATURES
# ============================================================================

def parse_creation(value):
    value = value.strip()

    if value.endswith("Z"):
        value = value[:-1]

    return datetime.fromisoformat(value)


def text_features(text):
    if text is None:
        text = ""

    text = str(text)

    length = len(text)
    words = len(text.split())
    digits = sum(c.isdigit() for c in text)
    lines = text.count("\n")
    uppercase = sum(c.isupper() for c in text)

    return (
        length,
        words,
        digits,
        lines,
        uppercase,
        1.0 if length == 0 else 0.0,
    )


def build_frequency_maps(rows):

    creator_counts = Counter()
    creator_detail_counts = Counter()

    for row in rows:

        creator = row["Creator"].strip()
        creator_detail = row["Creator Detail"].strip()

        if creator:
            creator_counts[creator] += 1

        if creator_detail:
            creator_detail_counts[
                creator_detail
            ] += 1

    return (
        creator_counts,
        creator_detail_counts,
    )


def build_features(
    rows,
    creator_counts,
    creator_detail_counts,
):

    feature_names = [
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

    X = []
    ids = []
    durations = []
    events = []

    for row in rows:

        creation = parse_creation(
            row["Creation time"]
        )

        creator = row["Creator"].strip()
        creator_detail = row["Creator Detail"].strip()

        summary = text_features(
            row["Summary"]
        )

        description = text_features(
            row["Description"]
        )

        month_angle = (
            2.0
            * math.pi
            * (creation.month - 1)
            / 12.0
        )

        weekday_angle = (
            2.0
            * math.pi
            * creation.weekday()
            / 7.0
        )

        hour_angle = (
            2.0
            * math.pi
            * creation.hour
            / 24.0
        )

        features = [
            math.log1p(
                creator_counts.get(
                    creator,
                    0,
                )
            ),

            math.log1p(
                creator_detail_counts.get(
                    creator_detail,
                    0,
                )
            ),

            math.log1p(summary[0]),
            math.log1p(summary[1]),
            math.log1p(summary[2]),
            math.log1p(summary[3]),
            math.log1p(summary[4]),
            summary[5],

            math.log1p(description[0]),
            math.log1p(description[1]),
            math.log1p(description[2]),
            math.log1p(description[3]),
            math.log1p(description[4]),
            description[5],

            (creation.year - 2010.0) / 10.0,

            math.sin(month_angle),
            math.cos(month_angle),

            math.sin(weekday_angle),
            math.cos(weekday_angle),

            math.sin(hour_angle),
            math.cos(hour_angle),
        ]

        X.append(features)
        ids.append(row["ID"])
        durations.append(
            float(row["duration_seconds"])
        )
        events.append(
            int(row["event"])
        )

    return (
        np.asarray(
            X,
            dtype=np.float64,
        ),
        ids,
        np.asarray(
            durations,
            dtype=np.float64,
        ),
        np.asarray(
            events,
            dtype=np.int8,
        ),
        feature_names,
    )


# ============================================================================
# STANDARDIZATION
# ============================================================================

def fit_standardizer(X):

    mean = X.mean(axis=0)
    std = X.std(axis=0)

    std[std < 1e-12] = 1.0

    return mean, std


def standardize(
    X,
    mean,
    std,
):
    return (
        X - mean
    ) / std


# ============================================================================
# WEIBULL AFT
# ============================================================================

class WeibullAFT:

    def __init__(
        self,
        l2=1e-3,
    ):
        self.l2 = l2
        self.beta_ = None
        self.log_shape_ = None

    def negative_log_likelihood(
        self,
        params,
        X,
        durations,
        events,
    ):

        beta = params[:-1]
        log_shape = params[-1]

        shape = np.exp(
            np.clip(
                log_shape,
                -5.0,
                5.0,
            )
        )

        log_time = np.log(durations)

        eta = X @ beta

        z = shape * (
            log_time - eta
        )

        exp_z = np.exp(
            np.clip(
                z,
                -700.0,
                700.0,
            )
        )

        log_likelihood = (
            events
            * (
                log_shape
                + (shape - 1.0)
                * log_time
                - shape * eta
                - exp_z
            )
            + (1 - events)
            * (-exp_z)
        )

        penalty = (
            0.5
            * self.l2
            * np.sum(beta ** 2)
        )

        return (
            -np.sum(log_likelihood)
            + penalty
        )

    def fit(
        self,
        X,
        durations,
        events,
    ):

        initial = np.zeros(
            X.shape[1] + 1,
            dtype=np.float64,
        )

        initial[-1] = 0.0

        result = minimize(
            self.negative_log_likelihood,
            initial,
            args=(
                X,
                durations,
                events,
            ),
            method="L-BFGS-B",
            options={
                "maxiter": 500,
                "ftol": 1e-10,
                "gtol": 1e-6,
                "maxls": 50,
            },
        )

        if not result.success:
            raise RuntimeError(
                "Weibull AFT optimization failed:\n"
                + str(result.message)
            )

        self.beta_ = result.x[:-1]
        self.log_shape_ = result.x[-1]

        return result

    @property
    def shape_(self):
        return float(
            np.exp(
                np.clip(
                    self.log_shape_,
                    -5.0,
                    5.0,
                )
            )
        )

    def survival(
        self,
        X,
        time,
    ):

        eta = X @ self.beta_

        z = self.shape_ * (
            math.log(time) - eta
        )

        hazard = np.exp(
            np.clip(
                z,
                -700.0,
                700.0,
            )
        )

        return np.exp(-hazard)

    def median_time(
        self,
        X,
    ):

        eta = X @ self.beta_

        return np.exp(
            eta
            + (
                math.log(
                    math.log(2.0)
                )
                / self.shape_
            )
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

        removed += (
            j - i
        )

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


# ============================================================================
# IPCW BRIER
# ============================================================================

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
# EFFICIENT HARRELL CONCORDANCE
# ============================================================================

class FenwickTree:

    def __init__(self, size):
        self.tree = np.zeros(
            size + 1,
            dtype=np.int64,
        )

    def add(
        self,
        index,
        value=1,
    ):

        index += 1

        n = len(self.tree)

        while index < n:

            self.tree[index] += value

            index += (
                index
                & -index
            )

    def prefix_sum(
        self,
        index,
    ):

        if index < 0:
            return 0

        index += 1

        total = 0

        while index > 0:

            total += self.tree[index]

            index -= (
                index
                & -index
            )

        return int(total)


def efficient_harrell_concordance(
    durations,
    events,
    risk_scores,
):
    """
    O(n log n) Harrell concordance.

    Higher risk score = shorter predicted survival.

    For every observed event at time t, all subjects with
    strictly larger observed/censored duration form the
    comparable set.

    Scores are coordinate-compressed and maintained in a
    Fenwick tree.
    """

    order = np.argsort(
        durations,
        kind="mergesort",
    )

    d = durations[order]
    e = events[order]
    r = risk_scores[order]

    # Coordinate-compress risk scores.
    unique_scores = np.unique(r)

    score_index = np.searchsorted(
        unique_scores,
        r,
        side="left",
    )

    tree = FenwickTree(
        len(unique_scores)
    )

    comparable = 0
    concordant = 0.0

    n = len(d)
    i = n - 1

    while i >= 0:

        current_duration = d[i]

        j = i

        while (
            j >= 0
            and d[j] == current_duration
        ):
            j -= 1

        # Subjects already inserted have duration
        # strictly greater than current_duration.
        greater_count = (
            tree.prefix_sum(
                len(unique_scores) - 1
            )
        )

        if greater_count > 0:

            for k in range(
                j + 1,
                i + 1,
            ):

                if e[k] != 1:
                    continue

                score = r[k]
                idx = score_index[k]

                less_count = (
                    tree.prefix_sum(
                        idx - 1
                    )
                )

                less_or_equal = (
                    tree.prefix_sum(
                        idx
                    )
                )

                equal_count = (
                    less_or_equal
                    - less_count
                )

                comparable += greater_count

                # Higher risk = earlier event.
                # So current event is concordant when
                # its risk score is greater than the
                # later-surviving subject's risk score.
                #
                # The Fenwick tree counts later subjects.
                # less_count = later subjects with lower risk.
                concordant += less_count

                # Ties receive 0.5.
                concordant += (
                    0.5
                    * equal_count
                )

        # Add the complete current-duration group
        # only after comparisons, ensuring equal-time
        # subjects are never treated as comparable.
        for k in range(
            j + 1,
            i + 1,
        ):

            tree.add(
                score_index[k]
            )

        i = j

    if comparable == 0:
        return None, 0

    return (
        concordant / comparable,
        comparable,
    )


# ============================================================================
# PERCENTILES
# ============================================================================

def percentile(
    values,
    q,
):

    values = np.asarray(
        values,
        dtype=np.float64,
    )

    return float(
        np.quantile(
            values,
            q,
            method="linear",
        )
    )


# ============================================================================
# MAIN
# ============================================================================

def main():

    METRICS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    DERIVED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 80)
    print(
        "T7 MOD-007 — Optimized First Predictive Survival Baseline"
    )
    print("=" * 80)

    # -----------------------------------------------------------------
    # 1. Load train
    # -----------------------------------------------------------------

    print(
        "\n[1/8] Loading frozen TRAIN split..."
    )

    train_rows = read_rows(
        TRAIN_PATH
    )

    print(
        f"TRAIN rows: {len(train_rows):,}"
    )

    # -----------------------------------------------------------------
    # 2. Load evaluation
    # -----------------------------------------------------------------

    print(
        "\n[2/8] Loading frozen EVALUATION split..."
    )

    eval_rows = read_rows(
        EVAL_PATH
    )

    print(
        f"EVAL rows: {len(eval_rows):,}"
    )

    # -----------------------------------------------------------------
    # 3. Build Creation-only features
    # -----------------------------------------------------------------

    print(
        "\n[3/8] Building TRAIN-only Creation-time features..."
    )

    (
        creator_counts,
        creator_detail_counts,
    ) = build_frequency_maps(
        train_rows
    )

    (
        X_train_raw,
        train_ids,
        train_durations,
        train_events,
        feature_names,
    ) = build_features(
        train_rows,
        creator_counts,
        creator_detail_counts,
    )

    (
        X_eval_raw,
        eval_ids,
        eval_durations,
        eval_events,
        _,
    ) = build_features(
        eval_rows,
        creator_counts,
        creator_detail_counts,
    )

    train_mean, train_std = (
        fit_standardizer(
            X_train_raw
        )
    )

    X_train = standardize(
        X_train_raw,
        train_mean,
        train_std,
    )

    X_eval = standardize(
        X_eval_raw,
        train_mean,
        train_std,
    )

    print(
        f"Feature count: {X_train.shape[1]}"
    )

    print(
        "Feature boundary: Creation-only"
    )

    # -----------------------------------------------------------------
    # 4. Fit Weibull AFT
    # -----------------------------------------------------------------

    print(
        "\n[4/8] Fitting censored Weibull AFT model..."
    )

    model = WeibullAFT(
        l2=1e-3
    )

    result = model.fit(
        X_train,
        train_durations,
        train_events,
    )

    print(
        f"Optimization success: "
        f"{result.success}"
    )

    print(
        f"Iterations: {result.nit}"
    )

    print(
        f"Final objective: "
        f"{result.fun:.6f}"
    )

    print(
        f"Estimated Weibull shape: "
        f"{model.shape_:.8f}"
    )

    # -----------------------------------------------------------------
    # 5. Generate predictions
    # -----------------------------------------------------------------

    print(
        "\n[5/8] Generating evaluation survival predictions..."
    )

    observed_train_durations = (
        train_durations[
            train_events == 1
        ]
    )

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

    horizon_predictions = {}

    for horizon in horizons:

        horizon_predictions[
            str(horizon)
        ] = model.survival(
            X_eval,
            horizon,
        )

    median_predictions = (
        model.median_time(
            X_eval
        )
    )

    # Higher = predicted faster resolution / higher event risk.
    risk_scores = -np.log(
        np.maximum(
            median_predictions,
            1e-12,
        )
    )

    # -----------------------------------------------------------------
    # 6. Efficient concordance
    # -----------------------------------------------------------------

    print(
        "\n[6/8] Calculating O(n log n) evaluation concordance..."
    )

    (
        c_index,
        comparable_pairs,
    ) = efficient_harrell_concordance(
        eval_durations,
        eval_events,
        risk_scores,
    )

    print(
        f"Harrell concordance index: "
        f"{c_index:.8f}"
    )

    print(
        f"Comparable pairs: "
        f"{comparable_pairs:,}"
    )

    # -----------------------------------------------------------------
    # 7. IPCW Brier
    # -----------------------------------------------------------------

    print(
        "\n[7/8] Calculating evaluation IPCW Brier scores..."
    )

    (
        censor_times,
        censor_survival,
    ) = build_censoring_km(
        train_durations,
        train_events,
    )

    brier_results = []

    for horizon in horizons:

        predictions = horizon_predictions[
            str(horizon)
        ]

        score = ipcw_brier(
            eval_durations,
            eval_events,
            predictions,
            horizon,
            censor_times,
            censor_survival,
        )

        mean_prediction = float(
            np.mean(predictions)
        )

        result_row = {
            "horizon_seconds": horizon,
            "ipcw_brier_score": score,
            "mean_predicted_survival": (
                mean_prediction
            ),
        }

        brier_results.append(
            result_row
        )

        print(
            f"\nHorizon: "
            f"{horizon:.6f} seconds"
        )

        print(
            f"  Mean predicted survival: "
            f"{mean_prediction:.8f}"
        )

        print(
            f"  IPCW Brier score: "
            f"{score:.12f}"
        )

    # -----------------------------------------------------------------
    # 8. Save artifacts
    # -----------------------------------------------------------------

    print(
        "\n[8/8] Writing model, predictions and audit..."
    )

    with PREDICTION_PATH.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.writer(f)

        header = [
            "ID",
            "duration_seconds",
            "event",
            "predicted_median_survival_seconds",
        ]

        for horizon in horizons:

            header.append(
                "survival_probability_at_"
                f"{int(horizon)}_seconds"
            )

        writer.writerow(header)

        for i in range(
            len(eval_ids)
        ):

            row = [
                eval_ids[i],
                eval_durations[i],
                eval_events[i],
                median_predictions[i],
            ]

            for horizon in horizons:

                row.append(
                    horizon_predictions[
                        str(horizon)
                    ][i]
                )

            writer.writerow(row)

    model_payload = {
        "model_type": "Weibull_AFT",

        "l2": model.l2,

        "shape": model.shape_,

        "beta": {
            name: float(value)
            for name, value in zip(
                feature_names,
                model.beta_,
            )
        },

        "feature_names": feature_names,

        "standardization_mean": [
            float(value)
            for value in train_mean
        ],

        "standardization_std": [
            float(value)
            for value in train_std
        ],

        "creator_frequency_mapping_size": (
            len(creator_counts)
        ),

        "creator_detail_frequency_mapping_size": (
            len(creator_detail_counts)
        ),

        "optimization": {
            "success": bool(
                result.success
            ),
            "message": str(
                result.message
            ),
            "iterations": int(
                result.nit
            ),
            "objective": float(
                result.fun
            ),
        },
    }

    with MODEL_PATH.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            model_payload,
            f,
            indent=2,
        )

    audit = {
        "task": "T7 Resolution-Time Estimation",

        "operation": "MOD-007",

        "status": "COMPLETE",

        "model": {
            "family": "Weibull_AFT",
            "purpose": (
                "First predictive survival baseline"
            ),
            "training_rows": len(
                train_rows
            ),
            "evaluation_rows": len(
                eval_rows
            ),
            "feature_count": len(
                feature_names
            ),
        },

        "feature_boundary": {
            "creation_only": True,
            "post_creation_history_used": False,
            "current_status_used": False,
            "current_resolution_used": False,
            "evaluation_fitting": False,
            "raw_archive_access": False,
        },

        "features": feature_names,

        "train_event_count": int(
            np.sum(train_events)
        ),

        "train_censor_count": int(
            len(train_events)
            - np.sum(train_events)
        ),

        "evaluation_event_count": int(
            np.sum(eval_events)
        ),

        "evaluation_censor_count": int(
            len(eval_events)
            - np.sum(eval_events)
        ),

        "weibull": {
            "shape": model.shape_,
            "optimization_success": bool(
                result.success
            ),
            "iterations": int(
                result.nit
            ),
            "objective": float(
                result.fun
            ),
        },

        "evaluation_metrics": {
            "harrell_concordance_index": (
                c_index
            ),
            "comparable_pairs": (
                comparable_pairs
            ),
            "ipcw_brier": brier_results,
        },

        "artifacts": {
            "model": str(
                MODEL_PATH
            ),
            "predictions": str(
                PREDICTION_PATH
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
    print("MOD-007 COMPLETE")
    print("=" * 80)

    print(
        f"\nModel: {MODEL_PATH}"
    )

    print(
        f"Predictions: {PREDICTION_PATH}"
    )

    print(
        f"Audit: {AUDIT_PATH}"
    )


if __name__ == "__main__":
    main()