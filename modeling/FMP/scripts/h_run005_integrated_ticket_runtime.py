from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
METRICS_DIR = ROOT / "modeling" / "FMP" / "metrics"

# ---------------------------------------------------------------------
# INPUT TICKET
# ---------------------------------------------------------------------

TITLE = "VPN connection fails after password reset"

DESCRIPTION = (
    "I reset my corporate password this morning. Since then, the VPN client "
    "connects briefly and then disconnects. I restarted the laptop and "
    "reinstalled the VPN client, but the issue persists. I need access to "
    "the internal systems for today's work."
)

TICKET_TEXT = f"{TITLE}\n{DESCRIPTION}".strip()


# ---------------------------------------------------------------------
# FROZEN ARTIFACTS
# ---------------------------------------------------------------------

T1_PATH = (
    ROOT / "modeling" / "T1" / "baselines"
    / "t1_it_support_char_svm.joblib"
)

T2_PATH = (
    ROOT / "modeling" / "T2" / "models"
    / "t2_class_weighted_tfidf_logreg.joblib"
)

T3_PATH = (
    ROOT / "modeling" / "T3" / "models"
    / "t3_class_weighted_tfidf_logreg.joblib"
)

T4_TFIDF_PATH = (
    ROOT / "modeling" / "T4" / "results" / "mod007_checkpoints"
    / "t4_mod007_tfidf.joblib"
)

T4_NEIGHBORS_PATH = (
    ROOT / "modeling" / "T4" / "results" / "mod007_checkpoints"
    / "t4_mod007_neighbors.joblib"
)

T4_TRAIN_PATH = (
    ROOT / "modeling" / "T4" / "derived" / "t4_train.csv"
)


OUTPUT_PATH = (
    METRICS_DIR / "h_run005_integrated_ticket_runtime.json"
)


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------

def load_bundle(path):
    if not path.exists():
        raise FileNotFoundError(f"Frozen artifact missing: {path}")
    return joblib.load(path)


def run_t1(text):
    bundle = load_bundle(T1_PATH)

    features = bundle["features"]
    model = bundle["model"]

    X = features.transform([text])
    prediction = model.predict(X)[0]

    return {
        "status": "PASS",
        "prediction": str(prediction),
        "transformed_shape": list(X.shape),
        "artifact": str(T1_PATH),
    }


def run_t2(text):
    bundle = load_bundle(T2_PATH)

    vectorizer = bundle["vectorizer"]
    model = bundle["model"]

    X = vectorizer.transform([text])
    prediction = model.predict(X)[0]

    return {
        "status": "PASS",
        "prediction": str(prediction),
        "transformed_shape": list(X.shape),
        "artifact": str(T2_PATH),
    }


def run_t3(text):
    bundle = load_bundle(T3_PATH)

    vectorizer = bundle["vectorizer"]
    model = bundle["model"]

    X = vectorizer.transform([text])
    prediction = model.predict(X)[0]

    return {
        "status": "PASS",
        "prediction": str(prediction),
        "transformed_shape": list(X.shape),
        "artifact": str(T3_PATH),
    }


def run_t4(text):
    tfidf = load_bundle(T4_TFIDF_PATH)
    neighbors = load_bundle(T4_NEIGHBORS_PATH)

    train = pd.read_csv(T4_TRAIN_PATH)

    X = tfidf.transform([text])

    distances, indices = neighbors.kneighbors(
        X,
        n_neighbors=5,
        return_distance=True,
    )

    distances = distances[0]
    indices = indices[0]

    resolved = []

    for rank, (index, distance) in enumerate(
        zip(indices, distances),
        start=1,
    ):
        row = train.iloc[int(index)]

        resolved.append(
            {
                "rank": rank,
                "neighbor_index": int(index),
                "distance": float(distance),
                "ID": row["ID"],
                "Creation time": row["Creation time"],
                "Summary": row["Summary"],
                "target_assignee": row["target_assignee"],
            }
        )

    return {
        "status": "PASS",
        "transformed_shape": list(X.shape),
        "neighbors": resolved,
        "artifacts": {
            "tfidf": str(T4_TFIDF_PATH),
            "neighbors": str(T4_NEIGHBORS_PATH),
            "development_population": str(T4_TRAIN_PATH),
        },
    }


# ---------------------------------------------------------------------
# T5–T7 BOUNDARY
#
# These are deliberately represented as native evidence slots for now.
# We do NOT invent a probability, threshold, or prediction.
# ---------------------------------------------------------------------

def t5_boundary():
    return {
        "status": "NOT_BOUND_IN_THIS_RUNTIME_STEP",
        "native_semantics": "duplicate relationship evidence",
        "universal_duplicate_threshold": "NOT_ESTABLISHED",
        "note": (
            "T5 requires pairwise ticket evidence and is not converted "
            "into an autonomous duplicate decision."
        ),
    }


def t6_boundary():
    return {
        "status": "NOT_BOUND_IN_THIS_RUNTIME_STEP",
        "native_semantics": "related-ticket retrieval/ranking",
        "probability_interpretation": "NOT_ALLOWED",
        "note": (
            "T6 remains native retrieval/ranking evidence."
        ),
    }


def t7_boundary():
    return {
        "status": "NOT_BOUND_IN_THIS_RUNTIME_STEP",
        "native_semantics": "survival/resolution-time evidence",
        "note": (
            "T7 remains censoring-aware survival evidence and is not "
            "converted into an autonomous resolution-time decision."
        ),
    }


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main():

    print("=" * 72)
    print("H-RUN-005 — INTEGRATED TICKET RUNTIME")
    print("=" * 72)

    print()
    print("INPUT TICKET")
    print("-" * 72)
    print(f"TITLE: {TITLE}")
    print(f"DESCRIPTION: {DESCRIPTION}")

    # -------------------------------------------------------------
    # T1
    # -------------------------------------------------------------

    print()
    print("[T1] CATEGORY")

    t1 = run_t1(TICKET_TEXT)

    print(f"prediction: {t1['prediction']}")
    print(f"status: {t1['status']}")

    # -------------------------------------------------------------
    # T2
    # -------------------------------------------------------------

    print()
    print("[T2] PRIORITY")

    t2 = run_t2(TICKET_TEXT)

    print(f"prediction: {t2['prediction']}")
    print(f"status: {t2['status']}")

    # -------------------------------------------------------------
    # T3
    # -------------------------------------------------------------

    print()
    print("[T3] SEVERITY")

    t3 = run_t3(TICKET_TEXT)

    print(f"prediction: {t3['prediction']}")
    print(f"status: {t3['status']}")

    # -------------------------------------------------------------
    # T4
    # -------------------------------------------------------------

    print()
    print("[T4] HISTORICAL ASSIGNMENT RETRIEVAL")

    t4 = run_t4(TICKET_TEXT)

    print(f"status: {t4['status']}")

    for item in t4["neighbors"]:
        print(
            f"rank={item['rank']} "
            f"distance={item['distance']:.6f} "
            f"ID={item['ID']} "
            f"assignee={item['target_assignee']}"
        )

    # -------------------------------------------------------------
    # T5
    # -------------------------------------------------------------

    print()
    print("[T5] DUPLICATE EVIDENCE")

    t5 = t5_boundary()

    print(f"status: {t5['status']}")

    # -------------------------------------------------------------
    # T6
    # -------------------------------------------------------------

    print()
    print("[T6] RELATED-TICKET RETRIEVAL")

    t6 = t6_boundary()

    print(f"status: {t6['status']}")

    # -------------------------------------------------------------
    # T7
    # -------------------------------------------------------------

    print()
    print("[T7] RESOLUTION-TIME EVIDENCE")

    t7 = t7_boundary()

    print(f"status: {t7['status']}")

    # -------------------------------------------------------------
    # T8
    # -------------------------------------------------------------

    t8 = {
        "status": "NATIVE_EVIDENCE_BOUNDARY",
        "variable_evidence": True,
        "missing_evidence_is_unavailable": True,
        "universal_probability_aggregation": False,
        "synthetic_fusion_target": False,
    }

    print()
    print("[T8] EVIDENCE FUSION")
    print("status: NATIVE_EVIDENCE_BOUNDARY")

    # -------------------------------------------------------------
    # T9
    # -------------------------------------------------------------

    t9 = {
        "status": "NATIVE_RELIABILITY_BOUNDARY",
        "universal_confidence": "NOT_CREATED",
        "universal_risk": "NOT_CREATED",
        "automatic_action_policy": "NOT_ESTABLISHED",
    }

    print()
    print("[T9] RELIABILITY")
    print("status: NATIVE_RELIABILITY_BOUNDARY")

    # -------------------------------------------------------------
    # T10
    # -------------------------------------------------------------

    t10 = {
        "automation": "NOT_ESTABLISHED",
        "human_review": "NOT_ESTABLISHED",
        "universal_threshold": "NOT_ESTABLISHED",
    }

    print()
    print("[T10] POLICY")
    print("automation: NOT_ESTABLISHED")
    print("human review: NOT_ESTABLISHED")
    print("universal threshold: NOT_ESTABLISHED")

    # -------------------------------------------------------------
    # CONTROLS
    # -------------------------------------------------------------

    controls = {
        "frozen_model_execution": True,
        "model_fitting": False,
        "retraining": False,
        "new_model_selection": False,
        "threshold_optimization": False,
        "universal_confidence_creation": False,
        "universal_risk_creation": False,
        "synthetic_fusion_target_creation": False,
        "artifact_modification": False,
        "locked_test_use": False,
    }

    # -------------------------------------------------------------
    # FINAL RECORD
    # -------------------------------------------------------------

    result = {
        "operation": "H-RUN-005",
        "operation_name": "integrated ticket runtime",
        "status": "PASS",

        "ticket": {
            "title": TITLE,
            "description": DESCRIPTION,
        },

        "tasks": {
            "T1": t1,
            "T2": t2,
            "T3": t3,
            "T4": t4,
            "T5": t5,
            "T6": t6,
            "T7": t7,
            "T8": t8,
            "T9": t9,
            "T10": t10,
        },

        "controls": controls,

        "interpretation": (
            "This runtime demonstrates one ticket flowing through the "
            "integrated frozen evidence architecture. T1-T4 execute "
            "their validated frozen runtime paths. T5-T7 retain their "
            "native task semantics and are not converted into fabricated "
            "universal scores or autonomous decisions."
        ),
    }

    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(
            result,
            f,
            indent=2,
            default=str,
        )

    print()
    print("=" * 72)
    print("INTEGRATED RUNTIME STATUS: PASS")
    print(f"OUTPUT: {OUTPUT_PATH}")
    print("=" * 72)


if __name__ == "__main__":
    main()