from pathlib import Path
import json
import joblib


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T2_MODEL = ROOT / "modeling/T2/models/t2_class_weighted_tfidf_logreg.joblib"
T3_MODEL = ROOT / "modeling/T3/models/t3_class_weighted_tfidf_logreg.joblib"

OUTPUT = ROOT / "modeling/FMP/metrics/h_run007_t2_t3_variation_probe.json"


TICKETS = [
    {
        "id": "H-RUN-007-A",
        "title": "VPN connection fails after password reset",
        "description": (
            "I reset my corporate password this morning. "
            "Since then, the VPN client connects briefly and then disconnects. "
            "I restarted the laptop and reinstalled the VPN client, but the issue persists. "
            "I need access to the internal systems for today's work."
        ),
    },
    {
        "id": "H-RUN-007-B",
        "title": "Monitor replacement request",
        "description": (
            "The monitor on my desk has a cracked display. "
            "The computer itself works normally and I can continue working using another monitor. "
            "Please arrange a replacement when convenient."
        ),
    },
    {
        "id": "H-RUN-007-C",
        "title": "Password reset instructions",
        "description": (
            "I forgot my account password and need instructions for resetting it. "
            "I am currently able to access my workstation and there is no immediate service outage."
        ),
    },
]


def build_text(ticket):
    return f"{ticket['title']}\n{ticket['description']}".strip()


def main():
    print("=" * 72)
    print("H-RUN-007 — T2/T3 PREDICTION VARIATION PROBE")
    print("=" * 72)

    print("\n[CONTROL]")
    print("training/retraining: NO")
    print("model modification: NO")
    print("threshold selection: NO")
    print("locked-test use: NO")
    print("new model selection: NO")

    if not T2_MODEL.exists():
        raise FileNotFoundError(f"Missing T2 artifact: {T2_MODEL}")

    if not T3_MODEL.exists():
        raise FileNotFoundError(f"Missing T3 artifact: {T3_MODEL}")

    print("\n[LOAD]")
    print(f"T2 artifact: {T2_MODEL}")
    print(f"T3 artifact: {T3_MODEL}")

    t2_bundle = joblib.load(T2_MODEL)
    t3_bundle = joblib.load(T3_MODEL)

    t2_vectorizer = t2_bundle["vectorizer"]
    t2_model = t2_bundle["model"]

    t3_vectorizer = t3_bundle["vectorizer"]
    t3_model = t3_bundle["model"]

    results = []

    print("\n[PREDICTIONS]")

    for ticket in TICKETS:
        text = build_text(ticket)

        t2_x = t2_vectorizer.transform([text])
        t3_x = t3_vectorizer.transform([text])

        t2_prediction = t2_model.predict(t2_x)[0]
        t3_prediction = t3_model.predict(t3_x)[0]

        record = {
            "ticket_id": ticket["id"],
            "title": ticket["title"],
            "t2_prediction": str(t2_prediction),
            "t3_prediction": str(t3_prediction),
        }

        results.append(record)

        print(f"\n{ticket['id']}")
        print(f"title: {ticket['title']}")
        print(f"T2 prediction: {t2_prediction}")
        print(f"T3 prediction: {t3_prediction}")

    t2_predictions = [r["t2_prediction"] for r in results]
    t3_predictions = [r["t3_prediction"] for r in results]

    t2_unique = sorted(set(t2_predictions))
    t3_unique = sorted(set(t3_predictions))

    print("\n[VARIATION]")
    print(f"T2 unique predictions: {t2_unique}")
    print(f"T3 unique predictions: {t3_unique}")

    if len(t2_unique) > 1:
        t2_variation = "OBSERVED"
    else:
        t2_variation = "NOT_OBSERVED"

    if len(t3_unique) > 1:
        t3_variation = "OBSERVED"
    else:
        t3_variation = "NOT_OBSERVED"

    print(f"T2 variation: {t2_variation}")
    print(f"T3 variation: {t3_variation}")

    output = {
        "operation": "H-RUN-007",
        "operation_name": "T2/T3 Prediction Variation Probe",
        "status": "PASS",
        "runtime_controls": {
            "training": False,
            "retraining": False,
            "model_modification": False,
            "threshold_selection": False,
            "locked_test_use": False,
            "new_model_selection": False,
        },
        "artifacts": {
            "t2": str(T2_MODEL),
            "t3": str(T3_MODEL),
        },
        "tickets": results,
        "variation": {
            "t2_unique_predictions": t2_unique,
            "t3_unique_predictions": t3_unique,
            "t2_variation": t2_variation,
            "t3_variation": t3_variation,
        },
        "interpretation_boundary": (
            "This operation tests runtime prediction variation only. "
            "It does not establish model quality, calibration, operational thresholds, "
            "or production decision policy."
        ),
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("\n[OUTPUT]")
    print(f"written: {OUTPUT}")

    print("\n" + "=" * 72)
    print("H-RUN-007 COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()