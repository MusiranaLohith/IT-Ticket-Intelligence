import csv
import json
import math
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.special import log_ndtr


# ============================================================================
# PATHS
# ============================================================================

ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

TRAIN = ROOT / "modeling/T7/splits/t7_train.csv"
EVAL = ROOT / "modeling/T7/splits/t7_evaluation.csv"

METRICS = ROOT / "modeling/T7/metrics"
DERIVED = ROOT / "modeling/T7/derived"

MODEL_OUT = METRICS / "t7_mod010_log_normal_aft_model.json"
PRED_OUT = DERIVED / "t7_mod010_evaluation_predictions.csv"
AUDIT_OUT = METRICS / "t7_mod010_log_normal_aft_audit.json"

csv.field_size_limit(sys.maxsize)


# ============================================================================
# DATA
# ============================================================================

REQUIRED = {
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

        missing = REQUIRED - set(reader.fieldnames or [])

        if missing:
            raise RuntimeError(
                f"Missing columns in {path}: {sorted(missing)}"
            )

        for row in reader:

            duration = float(row["duration_seconds"])
            event = int(row["event"])

            if duration <= 0 or event not in (0, 1):
                raise RuntimeError(
                    f"Invalid target for ID={row['ID']}"
                )

            rows.append(row)

    return rows


def parse_creation(value):
    if value.endswith("Z"):
        value = value[:-1]

    return datetime.fromisoformat(value)


def text_features(text):
    text = "" if text is None else str(text)

    return (
        len(text),
        len(text.split()),
        sum(c.isdigit() for c in text),
        text.count("\n"),
        sum(c.isupper() for c in text),
        1.0 if not text else 0.0,
    )


def frequency_maps(rows):

    creator = Counter()
    detail = Counter()

    for row in rows:

        if row["Creator"].strip():
            creator[row["Creator"].strip()] += 1

        if row["Creator Detail"].strip():
            detail[row["Creator Detail"].strip()] += 1

    return creator, detail


def make_features(
    rows,
    creator_counts,
    detail_counts,
):

    names = [
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

        dt = parse_creation(
            row["Creation time"]
        )

        s = text_features(row["Summary"])
        d = text_features(row["Description"])

        month = (
            2 * math.pi * (dt.month - 1) / 12
        )

        weekday = (
            2 * math.pi * dt.weekday() / 7
        )

        hour = (
            2 * math.pi * dt.hour / 24
        )

        X.append([
            math.log1p(
                creator_counts.get(
                    row["Creator"].strip(), 0
                )
            ),

            math.log1p(
                detail_counts.get(
                    row["Creator Detail"].strip(), 0
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
        ])

        ids.append(row["ID"])
        durations.append(float(row["duration_seconds"]))
        events.append(int(row["event"]))

    return (
        np.asarray(X, dtype=np.float64),
        ids,
        np.asarray(durations, dtype=np.float64),
        np.asarray(events, dtype=np.int8),
        names,
    )


def standardize_fit(X):
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    std[std < 1e-12] = 1.0
    return mean, std


# ============================================================================
# LOG-NORMAL AFT
# ============================================================================

class LogNormalAFT:

    def __init__(self, l2=1e-3):
        self.l2 = l2
        self.beta = None
        self.log_sigma = None

    def objective(
        self,
        params,
        X,
        durations,
        events,
    ):

        beta = params[:-1]
        log_sigma = params[-1]

        sigma = np.exp(
            np.clip(log_sigma, -5, 5)
        )

        y = np.log(durations)

        mu = X @ beta

        z = (y - mu) / sigma

        # Event:
        # log f(y) =
        # -log(y) - log(sigma) - 0.5*z^2 - log(sqrt(2pi))
        #
        # Since the likelihood is formulated in duration T,
        # the Jacobian contributes -log(T).

        log_pdf = (
            -np.log(durations)
            - log_sigma
            - 0.5 * z * z
            - 0.5 * math.log(2 * math.pi)
        )

        # Censored:
        # log P(T > t) = log Phi(-z)
        log_survival = log_ndtr(-z)

        ll = (
            events * log_pdf
            + (1 - events) * log_survival
        )

        penalty = (
            0.5
            * self.l2
            * np.sum(beta * beta)
        )

        return -np.sum(ll) + penalty

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

        # Initial sigma around one log-time unit.
        initial[-1] = 1.0

        result = minimize(
            self.objective,
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
                "Log-Normal AFT optimization failed: "
                + str(result.message)
            )

        self.beta = result.x[:-1]
        self.log_sigma = result.x[-1]

        return result

    @property
    def sigma(self):
        return float(
            np.exp(
                np.clip(
                    self.log_sigma,
                    -5,
                    5,
                )
            )
        )

    def survival(
        self,
        X,
        time,
    ):

        mu = X @ self.beta

        z = (
            math.log(time) - mu
        ) / self.sigma

        return np.exp(
            log_ndtr(-z)
        )

    def median(self, X):
        return np.exp(
            X @ self.beta
        )


# ============================================================================
# TRAIN-ONLY CENSORING DISTRIBUTION
# ============================================================================

def censoring_km(
    durations,
    events,
):

    order = np.argsort(
        durations,
        kind="mergesort",
    )

    d = durations[order]
    e = events[order]

    times = []
    counts = []
    risks = []

    n = len(d)
    i = 0
    removed = 0

    while i < n:

        t = d[i]
        j = i

        c = 0

        while j < n and d[j] == t:

            if e[j] == 0:
                c += 1

            j += 1

        times.append(t)
        counts.append(c)
        risks.append(n - removed)

        removed += j - i
        i = j

    survival = []
    current = 1.0

    for c, risk in zip(counts, risks):

        if c:
            current *= (
                1.0 - c / risk
            )

        survival.append(current)

    return (
        np.asarray(times),
        np.asarray(survival),
    )


def G_at(
    time,
    times,
    survival,
):

    i = np.searchsorted(
        times,
        time,
        side="right",
    ) - 1

    if i < 0:
        return 1.0

    return float(survival[i])


def G_before(
    time,
    times,
    survival,
):

    i = np.searchsorted(
        times,
        time,
        side="left",
    ) - 1

    if i < 0:
        return 1.0

    return float(survival[i])


def ipcw_brier(
    durations,
    events,
    predictions,
    horizon,
    censor_times,
    censor_survival,
):

    gh = G_at(
        horizon,
        censor_times,
        censor_survival,
    )

    if gh <= 0:
        raise RuntimeError(
            "G(horizon) reached zero."
        )

    total = 0.0
    weights = 0.0

    for t, event, pred in zip(
        durations,
        events,
        predictions,
    ):

        if event == 1 and t <= horizon:

            g = G_before(
                t,
                censor_times,
                censor_survival,
            )

            if g <= 0:
                continue

            w = 1.0 / g

            total += w * pred * pred
            weights += w

        elif t > horizon:

            w = 1.0 / gh

            error = 1.0 - pred

            total += w * error * error
            weights += w

    return (
        total / weights
        if weights
        else None
    )


# ============================================================================
# O(N LOG N) CONCORDANCE
# ============================================================================

class Fenwick:

    def __init__(self, n):
        self.tree = np.zeros(
            n + 1,
            dtype=np.int64,
        )

    def add(self, i):
        i += 1

        while i < len(self.tree):
            self.tree[i] += 1
            i += i & -i

    def query(self, i):

        if i < 0:
            return 0

        i += 1
        total = 0

        while i:
            total += self.tree[i]
            i -= i & -i

        return int(total)


def concordance(
    durations,
    events,
    risk,
):

    order = np.argsort(
        durations,
        kind="mergesort",
    )

    d = durations[order]
    e = events[order]
    r = risk[order]

    scores = np.unique(r)

    ranks = np.searchsorted(
        scores,
        r,
    )

    tree = Fenwick(
        len(scores)
    )

    comparable = 0
    concordant = 0.0

    i = len(d) - 1

    while i >= 0:

        t = d[i]
        j = i

        while (
            j >= 0
            and d[j] == t
        ):
            j -= 1

        inserted = tree.query(
            len(scores) - 1
        )

        if inserted:

            for k in range(
                j + 1,
                i + 1,
            ):

                if e[k] != 1:
                    continue

                rank = ranks[k]

                lower = tree.query(
                    rank - 1
                )

                equal = (
                    tree.query(rank)
                    - lower
                )

                comparable += inserted

                concordant += lower
                concordant += 0.5 * equal

        for k in range(
            j + 1,
            i + 1,
        ):
            tree.add(ranks[k])

        i = j

    if comparable == 0:
        return None, 0

    return (
        concordant / comparable,
        comparable,
    )


# ============================================================================
# MAIN
# ============================================================================

def main():

    METRICS.mkdir(
        parents=True,
        exist_ok=True,
    )

    DERIVED.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 80)
    print(
        "T7 MOD-010 — Alternative Log-Normal AFT Survival Baseline"
    )
    print("=" * 80)

    print(
        "\n[1/8] Loading frozen TRAIN split..."
    )

    train_rows = read_rows(TRAIN)

    print(
        f"TRAIN rows: {len(train_rows):,}"
    )

    print(
        "\n[2/8] Loading frozen EVALUATION split..."
    )

    eval_rows = read_rows(EVAL)

    print(
        f"EVAL rows: {len(eval_rows):,}"
    )

    print(
        "\n[3/8] Building identical Creation-only feature set..."
    )

    creator_counts, detail_counts = (
        frequency_maps(train_rows)
    )

    (
        Xtr_raw,
        train_ids,
        train_t,
        train_e,
        feature_names,
    ) = make_features(
        train_rows,
        creator_counts,
        detail_counts,
    )

    (
        Xev_raw,
        eval_ids,
        eval_t,
        eval_e,
        _,
    ) = make_features(
        eval_rows,
        creator_counts,
        detail_counts,
    )

    mean, std = standardize_fit(
        Xtr_raw
    )

    Xtr = (
        Xtr_raw - mean
    ) / std

    Xev = (
        Xev_raw - mean
    ) / std

    print(
        f"Feature count: {Xtr.shape[1]}"
    )

    print(
        "Feature boundary: Creation-only"
    )

    print(
        "\n[4/8] Fitting censored Log-Normal AFT..."
    )

    model = LogNormalAFT(
        l2=1e-3
    )

    result = model.fit(
        Xtr,
        train_t,
        train_e,
    )

    print(
        f"Optimization success: {result.success}"
    )

    print(
        f"Iterations: {result.nit}"
    )

    print(
        f"Final objective: {result.fun:.6f}"
    )

    print(
        f"Estimated sigma: {model.sigma:.8f}"
    )

    print(
        "\n[5/8] Generating evaluation predictions..."
    )

    observed = train_t[
        train_e == 1
    ]

    horizons = [
        float(np.quantile(observed, 0.25)),
        float(np.quantile(observed, 0.50)),
        float(np.quantile(observed, 0.75)),
    ]

    prediction_matrix = np.column_stack([
        model.survival(
            Xev,
            horizon,
        )
        for horizon in horizons
    ])

    median_predictions = model.median(
        Xev
    )

    risk = -np.log(
        np.maximum(
            median_predictions,
            1e-12,
        )
    )

    print(
        "\n[6/8] Calculating O(n log n) concordance..."
    )

    c_index, comparable = concordance(
        eval_t,
        eval_e,
        risk,
    )

    print(
        f"Harrell concordance index: "
        f"{c_index:.8f}"
    )

    print(
        f"Comparable pairs: "
        f"{comparable:,}"
    )

    print(
        "\n[7/8] Calculating IPCW Brier scores..."
    )

    censor_times, censor_survival = (
        censoring_km(
            train_t,
            train_e,
        )
    )

    brier_results = []

    for i, horizon in enumerate(
        horizons
    ):

        predictions = prediction_matrix[
            :, i
        ]

        score = ipcw_brier(
            eval_t,
            eval_e,
            predictions,
            horizon,
            censor_times,
            censor_survival,
        )

        row = {
            "horizon_seconds": horizon,
            "mean_predicted_survival": float(
                np.mean(predictions)
            ),
            "ipcw_brier_score": float(score),
        }

        brier_results.append(row)

        print(
            f"\nHorizon: {horizon:.6f} seconds"
        )

        print(
            f"  Mean predicted survival: "
            f"{np.mean(predictions):.8f}"
        )

        print(
            f"  IPCW Brier: "
            f"{score:.12f}"
        )

    print(
        "\n[8/8] Writing MOD-010 artifacts..."
    )

    with PRED_OUT.open(
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
                f"survival_probability_at_{int(horizon)}_seconds"
            )

        writer.writerow(header)

        for i in range(
            len(eval_ids)
        ):

            row = [
                eval_ids[i],
                eval_t[i],
                eval_e[i],
                median_predictions[i],
            ]

            row.extend(
                prediction_matrix[i]
            )

            writer.writerow(row)

    model_payload = {
        "model_type": "LogNormal_AFT",
        "l2": model.l2,
        "sigma": model.sigma,
        "beta": {
            name: float(value)
            for name, value in zip(
                feature_names,
                model.beta,
            )
        },
        "feature_names": feature_names,
        "standardization_mean": [
            float(x)
            for x in mean
        ],
        "standardization_std": [
            float(x)
            for x in std
        ],
        "optimization": {
            "success": bool(result.success),
            "iterations": int(result.nit),
            "objective": float(result.fun),
            "message": str(result.message),
        },
    }

    with MODEL_OUT.open(
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
        "operation": "MOD-010",
        "status": "COMPLETE",

        "purpose": (
            "Controlled alternative survival "
            "distribution to assess whether "
            "Weibull model-form assumptions explain "
            "the observed predictive limitations."
        ),

        "model": {
            "family": "LogNormal_AFT",
            "training_rows": len(train_rows),
            "evaluation_rows": len(eval_rows),
            "feature_count": len(feature_names),
            "sigma": model.sigma,
        },

        "feature_boundary": {
            "creation_only": True,
            "post_creation_history_used": False,
            "current_status_used": False,
            "current_resolution_used": False,
            "evaluation_fitting": False,
            "raw_archive_access": False,
        },

        "optimization": {
            "success": bool(result.success),
            "iterations": int(result.nit),
            "objective": float(result.fun),
        },

        "evaluation_metrics": {
            "harrell_concordance_index": c_index,
            "comparable_pairs": comparable,
            "ipcw_brier": brier_results,
        },

        "horizons_seconds": horizons,

        "artifacts": {
            "model": str(MODEL_OUT),
            "predictions": str(PRED_OUT),
            "audit": str(AUDIT_OUT),
        },
    }

    with AUDIT_OUT.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            audit,
            f,
            indent=2,
        )

    print("\n" + "=" * 80)
    print("MOD-010 COMPLETE")
    print("=" * 80)

    print(
        f"\nModel: {MODEL_OUT}"
    )

    print(
        f"Predictions: {PRED_OUT}"
    )

    print(
        f"Audit: {AUDIT_OUT}"
    )


if __name__ == "__main__":
    main()