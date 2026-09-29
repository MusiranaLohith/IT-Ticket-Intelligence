from pathlib import Path
import json
import joblib
import numpy as np


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T3_MODEL = (
    ROOT
    / "modeling/T3/models/t3_class_weighted_tfidf_logreg.joblib"
)

OUTPUT = (
    ROOT
    / "modeling/FMP/metrics/h_run008_t3_decision_scores.json"
)


TICKETS = [
    {
        "id": "H-RUN-008-A",
        "title": "VPN connection fails after password reset",
        "description": (
            "I reset my corporate password this morning. "
            "Since then, the VPN client connects briefly and then disconnects. "
            "I restarted the laptop and reinstalled the VPN client, "
            "but the issue persists. "
            "I need access to the internal systems for today's work."
        ),
    },
    {
        "id": "H-RUN-008-B",
        "title": "Monitor replacement request",
        "description": (
            "The monitor on my desk has a cracked display. "
            "The computer itself works normally and I can continue working "
            "using another monitor. "
            "Please arrange a replacement when convenient."
        ),
    },
    {
        "id": "H-RUN-008-C",
        "title": "Password reset instructions",
        "description": (
            "I forgot my account password and need instructions for resetting it. "
            "I am currently able to access my workstation and there is no "
            "immediate service outage."
        ),
    },
]


def build_text(ticket):
    return f"{ticket['title']}\n{ticket['description']}".strip()


def main():
    print("=" * 72)
    print("H-RUN-008 — T3 DECISION-SCORE INSPECTION")
    print("=" * 72)

    print("\n[CONTROL]")
    print("training/retraining: NO")
    print("model modification: NO")
    print("threshold selection: NO")
    print("calibration: NO")
    print("locked-test use: NO")

    if not T3_MODEL.exists():
        raise FileNotFoundError(
            f"Missing T3 artifact: {T3_MODEL}"
        )

    bundle = joblib.load(T3_MODEL)

    vectorizer = bundle["vectorizer"]
    model = bundle["model"]

    classes = [str(x) for x in model.classes_]

    print("\n[T3 CLASSES]")
    for idx, cls in enumerate(classes):
        print(f"class[{idx}] = {cls}")

    results = []

    print("\n[DECISION SCORES]")

    for ticket in TICKETS:
        text = build_text(ticket)

        X = vectorizer.transform([text])

        prediction = model.predict(X)[0]
        scores = model.decision_function(X)[0]

        score_pairs = [
            {
                "class": classes[i],
                "score": float(scores[i]),
            }
            for i in range(len(classes))
        ]

        ranked = sorted(
            score_pairs,
            key=lambda item: item["score"],
            reverse=True,
        )

        top_score = ranked[0]["score"]

        second_score = (
            ranked[1]["score"]
            if len(ranked) > 1
            else None
        )

        margin = (
            top_score - second_score
            if second_score is not None
            else None
        )

        print(f"\n{ticket['id']}")
        print(f"title: {ticket['title']}")
        print(f"prediction: {prediction}")

        for item in ranked:
            print(
                f"  {item['class']}: "
                f"{item['score']:.6f}"
            )

        if margin is not None:
            print(f"top-vs-second margin: {margin:.6f}")

        results.append(
            {
                "ticket_id": ticket["id"],
                "title": ticket["title"],
                "prediction": str(prediction),
                "scores": score_pairs,
                "ranked_scores": ranked,
                "top_vs_second_margin": (
                    float(margin)
                    if margin is not None
                    else None
                ),
            }
        )

    output = {
        "operation": "H-RUN-008",
        "operation_name": "T3 Decision-Score Inspection",
        "status": "PASS",
        "runtime_controls": {
            "training": False,
            "retraining": False,
            "model_modification": False,
            "threshold_selection": False,
            "calibration": False,
            "locked_test_use": False,
        },
        "artifact": str(T3_MODEL),
        "classes": classes,
        "results": results,
        "interpretation_boundary": (
            "Decision scores are native classifier outputs. "
            "They are not probabilities, calibrated confidence, "
            "or an operational severity threshold."
        ),
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            output,
            f,
            indent=2,
        )

    print("\n[OUTPUT]")
    print(f"written: {OUTPUT}")

    print("\n" + "=" * 72)
    print("H-RUN-008 COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()