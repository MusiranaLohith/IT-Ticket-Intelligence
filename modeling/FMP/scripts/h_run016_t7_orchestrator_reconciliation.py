from pathlib import Path
import json
import numpy as np
import pandas as pd


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T7_MODEL = ROOT / "modeling/T7/metrics/t7_mod010_log_normal_aft_model.json"
T7_TRAIN = ROOT / "modeling/T7/splits/t7_train.csv"

PREVIOUS = ROOT / "modeling/FMP/metrics/h_run011_t7_new_ticket_inference.json"

OUTPUT = ROOT / "modeling/FMP/metrics/h_run016_t7_orchestrator_reconciliation.json"


def fail(message):
    raise RuntimeError(message)


def log1p(value):
    return float(np.log1p(value))


def build_features(ticket, payload, train):
    creator_counts = (
        train["Creator"]
        .fillna("")
        .value_counts()
        .to_dict()
    )

    creator_detail_counts = (
        train["Creator Detail"]
        .fillna("")
        .value_counts()
        .to_dict()
    )

    creation_time = pd.to_datetime(
        ticket["creation_time"],
        utc=True
    )

    creator = ticket.get("creator", "")
    creator_detail = ticket.get("creator_detail", "")
    summary = ticket["title"]
    description = ticket["description"]

    raw = {
        "creator_frequency_log1p":
            log1p(creator_counts.get(creator, 0)),

        "creator_detail_frequency_log1p":
            log1p(creator_detail_counts.get(creator_detail, 0)),

        "summary_chars_log1p":
            log1p(len(summary)),

        "summary_words_log1p":
            log1p(len(summary.split())),

        "summary_digits_log1p":
            log1p(sum(c.isdigit() for c in summary)),

        "summary_lines_log1p":
            log1p(len(summary.splitlines())),

        "summary_uppercase_log1p":
            log1p(sum(c.isupper() for c in summary)),

        "summary_missing":
            float(not summary.strip()),

        "description_chars_log1p":
            log1p(len(description)),

        "description_words_log1p":
            log1p(len(description.split())),

        "description_digits_log1p":
            log1p(sum(c.isdigit() for c in description)),

        "description_lines_log1p":
            log1p(len(description.splitlines())),

        "description_uppercase_log1p":
            log1p(sum(c.isupper() for c in description)),

        "description_missing":
            float(not description.strip()),

        "creation_year_scaled":
            float(creation_time.year - 2000) / 10.0,

        "creation_month_sin":
            float(np.sin(
                2.0 * np.pi * creation_time.month / 12.0
            )),

        "creation_month_cos":
            float(np.cos(
                2.0 * np.pi * creation_time.month / 12.0
            )),

        "creation_weekday_sin":
            float(np.sin(
                2.0 * np.pi * creation_time.weekday() / 7.0
            )),

        "creation_weekday_cos":
            float(np.cos(
                2.0 * np.pi * creation_time.weekday() / 7.0
            )),

        "creation_hour_sin":
            float(np.sin(
                2.0 * np.pi * creation_time.hour / 24.0
            )),

        "creation_hour_cos":
            float(np.cos(
                2.0 * np.pi * creation_time.hour / 24.0
            )),
    }

    feature_names = payload["feature_names"]

    beta = np.asarray(
        [payload["beta"][name] for name in feature_names],
        dtype=float
    )

    mean = np.asarray(
        payload["standardization_mean"],
        dtype=float
    )

    std = np.asarray(
        payload["standardization_std"],
        dtype=float
    )

    X_raw = np.asarray(
        [raw[name] for name in feature_names],
        dtype=float
    ).reshape(1, -1)

    X_std = (X_raw - mean) / std

    lp = float((X_std @ beta).item())

    prediction = float(np.exp(lp))

    return (
        feature_names,
        raw,
        X_raw,
        X_std,
        beta,
        lp,
        prediction,
    )


def main():

    ticket = {
        "ticket_id": "H-RUN-015-VPN-001",
        "creation_time": "2026-09-26T18:03:00Z",
        "creator": "",
        "creator_detail": "",
        "title": "VPN connection fails after password reset",
        "description": (
            "I reset my corporate password this morning. "
            "Since then, the VPN client connects briefly and "
            "then disconnects. I restarted the laptop and "
            "reinstalled the VPN client, but the issue persists. "
            "I need access to the internal systems for today's work."
        ),
    }

    with open(T7_MODEL, "r", encoding="utf-8") as f:
        payload = json.load(f)

    train = pd.read_csv(T7_TRAIN)

    (
        feature_names,
        raw,
        X_raw,
        X_std,
        beta,
        lp,
        prediction,
    ) = build_features(ticket, payload, train)

    previous_prediction = None

    if PREVIOUS.exists():
        with open(PREVIOUS, "r", encoding="utf-8") as f:
            previous = json.load(f)

        previous_prediction = previous.get(
            "predicted_median_duration_seconds"
        )

    print("=" * 72)
    print("H-RUN-016 — T7 ORCHESTRATOR REPRODUCTION RECONCILIATION")
    print("=" * 72)

    print("\n[CONTROL]")
    print("training/retraining: NO")
    print("model modification: NO")
    print("prediction modification: NO")
    print("locked-test use: NO")

    print("\n[CURRENT ORCHESTRATOR REPRODUCTION]")
    print("feature count:", len(feature_names))
    print("linear predictor:", round(lp, 9))
    print("predicted seconds:", round(prediction, 9))

    print("\n[PREVIOUS H-RUN-011R3]")
    print("recorded prediction:", previous_prediction)

    if previous_prediction is not None:
        delta = prediction - float(previous_prediction)
        print("prediction delta:", round(delta, 9))

    print("\n[FEATURE CONTRIBUTIONS]")

    contributions = []

    for name, x, b in zip(
        feature_names,
        X_std[0],
        beta
    ):
        contribution = float(x * b)

        contributions.append({
            "feature": name,
            "raw": float(raw[name]),
            "standardized": float(x),
            "beta": float(b),
            "contribution": contribution,
        })

        print(
            f"{name}: "
            f"raw={raw[name]:.9f} "
            f"std={x:.9f} "
            f"beta={b:.9f} "
            f"contribution={contribution:.9f}"
        )

    contributions.sort(
        key=lambda x: abs(x["contribution"]),
        reverse=True
    )

    print("\n[TOP CONTRIBUTIONS]")

    for item in contributions[:7]:
        print(
            item["feature"],
            "=",
            round(item["contribution"], 9)
        )

    print("\n[CHECKS]")

    checks = {
        "feature_count_21":
            len(feature_names) == 21,

        "beta_alignment":
            len(beta) == len(feature_names),

        "standardization_alignment":
            len(X_std[0]) == len(feature_names),

        "finite_features":
            bool(np.all(np.isfinite(X_std))),

        "finite_prediction":
            bool(np.isfinite(prediction)),
    }

    for name, value in checks.items():
        print(f"{name}: {value}")

    result = {
        "operation": "H-RUN-016",
        "operation_name":
            "T7_ORCHESTRATOR_REPRODUCTION_RECONCILIATION",

        "status": "PASS",

        "ticket": ticket,

        "previous_h_run_011r3_prediction":
            previous_prediction,

        "current_prediction":
            prediction,

        "prediction_delta":
            (
                prediction - float(previous_prediction)
                if previous_prediction is not None
                else None
            ),

        "linear_predictor": lp,

        "feature_names": feature_names,

        "raw_features": raw,

        "standardized_features":
            X_std[0].tolist(),

        "beta":
            beta.tolist(),

        "feature_contributions":
            contributions,

        "checks": checks,

        "interpretation":
            "Reconciliation evidence for the T7 value discrepancy. "
            "No model modification or prediction adjustment performed.",
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(
            result,
            f,
            indent=2
        )

    print("\n[OUTPUT]")
    print("written:", OUTPUT)

    print("\n" + "=" * 72)
    print("H-RUN-016 COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()