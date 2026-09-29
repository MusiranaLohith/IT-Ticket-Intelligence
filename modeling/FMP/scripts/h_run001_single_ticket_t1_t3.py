from pathlib import Path
import json

import joblib

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

TICKET_TITLE = (
    "VPN connection fails after password reset"
)

TICKET_DESCRIPTION = (
    "I reset my corporate password this morning. "
    "Since then, the VPN client connects briefly and "
    "then disconnects. I restarted the laptop and "
    "reinstalled the VPN client, but the issue persists. "
    "I need access to the internal systems for today's work."
)

TICKET_TEXT = (
    f"{TICKET_TITLE}\n"
    f"{TICKET_DESCRIPTION}"
).strip()

ARTIFACTS = {

    "T1": (
            PROJECT_ROOT
            / "modeling/T1/baselines/"
              "t1_it_support_char_svm.joblib"
    ),

    "T2": (
            PROJECT_ROOT
            / "modeling/T2/models/"
              "t2_class_weighted_tfidf_logreg.joblib"
    ),

    "T3": (
            PROJECT_ROOT
            / "modeling/T3/models/"
              "t3_class_weighted_tfidf_logreg.joblib"
    ),
}

OUTPUT = (
        PROJECT_ROOT
        / "modeling/FMP/metrics/"
          "h_run001_single_ticket_t1_t3.json"
)


def run_t1(text):
    bundle = joblib.load(
        ARTIFACTS["T1"]
    )

    if not isinstance(bundle, dict):
        raise TypeError(
            "T1 artifact is not a dict bundle."
        )

    features = bundle["features"]
    model = bundle["model"]

    X = features.transform([text])

    prediction = model.predict(X)

    return {
        "prediction": str(
            prediction[0]
        ),
        "feature_type": (
            f"{type(features).__module__}."
            f"{type(features).__name__}"
        ),
        "model_type": (
            f"{type(model).__module__}."
            f"{type(model).__name__}"
        ),
        "transformed_shape": list(
            X.shape
        ),
    }


def run_t2(text):
    bundle = joblib.load(
        ARTIFACTS["T2"]
    )

    if not isinstance(bundle, dict):
        raise TypeError(
            "T2 artifact is not a dict bundle."
        )

    vectorizer = bundle["vectorizer"]
    model = bundle["model"]

    X = vectorizer.transform([text])

    prediction = model.predict(X)

    return {
        "prediction": str(
            prediction[0]
        ),
        "vectorizer_type": (
            f"{type(vectorizer).__module__}."
            f"{type(vectorizer).__name__}"
        ),
        "model_type": (
            f"{type(model).__module__}."
            f"{type(model).__name__}"
        ),
        "transformed_shape": list(
            X.shape
        ),
    }


def run_t3(text):
    bundle = joblib.load(
        ARTIFACTS["T3"]
    )

    if not isinstance(bundle, dict):
        raise TypeError(
            "T3 artifact is not a dict bundle."
        )

    vectorizer = bundle["vectorizer"]
    model = bundle["model"]

    X = vectorizer.transform([text])

    prediction = model.predict(X)

    return {
        "prediction": str(
            prediction[0]
        ),
        "vectorizer_type": (
            f"{type(vectorizer).__module__}."
            f"{type(vectorizer).__name__}"
        ),
        "model_type": (
            f"{type(model).__module__}."
            f"{type(model).__name__}"
        ),
        "transformed_shape": list(
            X.shape
        ),
    }


def main():
    print("=" * 72)
    print(
        "H-RUN-001 — SINGLE TICKET T1/T2/T3"
    )
    print("=" * 72)

    print()
    print("TITLE:")
    print(TICKET_TITLE)

    print()
    print("DESCRIPTION:")
    print(TICKET_DESCRIPTION)

    print()
    print("FROZEN ARTIFACTS:")

    for task, path in ARTIFACTS.items():

        if not path.exists():
            raise FileNotFoundError(
                f"{task} artifact missing: {path}"
            )

        print(
            f"{task}: {path}"
        )

    print()
    print("CONTROLS:")
    print("model execution: YES")
    print("model fitting: NO")
    print("retraining: NO")
    print("threshold selection: NO")
    print("artifact modification: NO")
    print("locked test use: NO")

    print()
    print("Running T1...")

    t1 = run_t1(
        TICKET_TEXT
    )

    print(
        "T1 prediction:",
        t1["prediction"],
    )

    print()
    print("Running T2...")

    t2 = run_t2(
        TICKET_TEXT
    )

    print(
        "T2 prediction:",
        t2["prediction"],
    )

    print()
    print("Running T3...")

    t3 = run_t3(
        TICKET_TEXT
    )

    print(
        "T3 prediction:",
        t3["prediction"],
    )

    result = {

        "operation":
            "H-RUN-001",

        "operation_name":
            "First Single-Ticket Frozen Runtime",

        "status":
            "PASS",

        "ticket": {
            "title":
                TICKET_TITLE,

            "description":
                TICKET_DESCRIPTION,

            "representation":
                TICKET_TEXT,
        },

        "results": {
            "T1": t1,
            "T2": t2,
            "T3": t3,
        },

        "controls": {

            "model_execution":
                True,

            "model_fitting":
                False,

            "retraining":
                False,

            "threshold_selection":
                False,

            "artifact_modification":
                False,

            "locked_test_use":
                False,
        },

        "interpretation": (
            "Predictions are native outputs from the "
            "frozen T1/T2/T3 artifacts. This run does not "
            "establish operational thresholds, universal "
            "confidence, universal risk, or autonomous action."
        ),
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            result,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 72)
    print("STATUS: PASS")
    print("OUTPUT:", OUTPUT)
    print("=" * 72)


if __name__ == "__main__":
    main()