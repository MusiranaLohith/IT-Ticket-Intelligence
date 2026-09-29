from pathlib import Path
import json
import importlib.util

import joblib
import numpy as np
import pandas as pd


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
METRICS = ROOT / "modeling" / "FMP" / "metrics"


# =====================================================================
# NEW TICKET
# =====================================================================

TITLE = "VPN connection fails after password reset"

DESCRIPTION = (
    "I reset my corporate password this morning. Since then, the VPN "
    "client connects briefly and then disconnects. I restarted the "
    "laptop and reinstalled the VPN client, but the issue persists. "
    "I need access to the internal systems for today's work."
)

TICKET_TEXT = f"{TITLE}\n{DESCRIPTION}".strip()


# =====================================================================
# T1
# =====================================================================

T1_ARTIFACT = (
    ROOT
    / "modeling/T1/baselines/"
    / "t1_it_support_char_svm.joblib"
)


# =====================================================================
# T2
# =====================================================================

T2_ARTIFACT = (
    ROOT
    / "modeling/T2/models/"
    / "t2_class_weighted_tfidf_logreg.joblib"
)


# =====================================================================
# T3
# =====================================================================

T3_ARTIFACT = (
    ROOT
    / "modeling/T3/models/"
    / "t3_class_weighted_tfidf_logreg.joblib"
)


# =====================================================================
# T4
# =====================================================================

T4_TFIDF = (
    ROOT
    / "modeling/T4/results/mod007_checkpoints/"
    / "t4_mod007_tfidf.joblib"
)

T4_NEIGHBORS = (
    ROOT
    / "modeling/T4/results/mod007_checkpoints/"
    / "t4_mod007_neighbors.joblib"
)

T4_TRAIN = (
    ROOT
    / "modeling/T4/derived/"
    / "t4_train.csv"
)


# =====================================================================
# T5
# =====================================================================

T5_TFIDF = (
    ROOT
    / "modeling/T5/models/"
    / "t5_mod005_tfidf.joblib"
)

T5_LOGREG = (
    ROOT
    / "modeling/T5/models/"
    / "t5_mod005_logreg.joblib"
)

T5_CALIBRATION = (
    ROOT
    / "modeling/T5/models/"
    / "t5_mod007_calibration_models.joblib"
)


# =====================================================================
# T6
#
# Frozen MOD-010 runtime uses:
#   - frozen MOD-004 TF-IDF
#   - stored MOD-009 semantic evidence
#
# The semantic model itself is NOT loaded.
# Therefore a new-ticket semantic score cannot be produced.
# =====================================================================

T6_TFIDF = (
    ROOT
    / "modeling/T6/models/"
    / "t6_mod004_tfidf_vectorizer.joblib"
)


# =====================================================================
# T7
# =====================================================================

T7_SOURCE = (
    ROOT
    / "modeling/T7/scripts/"
    / "t7_mod010_log_normal_aft_baseline.py"
)

T7_MODEL = (
    ROOT
    / "modeling/T7/metrics/"
    / "t7_mod010_log_normal_aft_model.json"
)

T7_TRAIN = (
    ROOT
    / "modeling/T7/splits/"
    / "t7_train.csv"
)


# =====================================================================
# OUTPUT
# =====================================================================

OUTPUT = (
    METRICS
    / "h_run006_integrated_ticket_runtime.json"
)


# =====================================================================
# HELPERS
# =====================================================================

def load_t7_module():
    spec = importlib.util.spec_from_file_location(
        "t7_mod010_runtime",
        T7_SOURCE,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "Could not load authoritative T7 module."
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def clean_text(value):
    if pd.isna(value):
        return ""

    return str(value).strip()


def t5_pair_text(summary, description):
    return (
        f"{summary}\n{description}"
    ).strip()


# =====================================================================
# T1
# =====================================================================

def run_t1():

    bundle = joblib.load(T1_ARTIFACT)

    features = bundle["features"]
    model = bundle["model"]

    X = features.transform([TICKET_TEXT])
    prediction = model.predict(X)[0]

    return {
        "status": "PASS",
        "prediction": str(prediction),
        "transformed_shape": list(X.shape),
        "artifact": str(T1_ARTIFACT),
    }


# =====================================================================
# T2
# =====================================================================

def run_t2():

    bundle = joblib.load(T2_ARTIFACT)

    vectorizer = bundle["vectorizer"]
    model = bundle["model"]

    X = vectorizer.transform([TICKET_TEXT])
    prediction = model.predict(X)[0]

    return {
        "status": "PASS",
        "prediction": str(prediction),
        "transformed_shape": list(X.shape),
        "artifact": str(T2_ARTIFACT),
    }


# =====================================================================
# T3
# =====================================================================

def run_t3():

    bundle = joblib.load(T3_ARTIFACT)

    vectorizer = bundle["vectorizer"]
    model = bundle["model"]

    X = vectorizer.transform([TICKET_TEXT])
    prediction = model.predict(X)[0]

    return {
        "status": "PASS",
        "prediction": str(prediction),
        "transformed_shape": list(X.shape),
        "artifact": str(T3_ARTIFACT),
    }


# =====================================================================
# T4
# =====================================================================

def run_t4():

    tfidf = joblib.load(T4_TFIDF)
    neighbors = joblib.load(T4_NEIGHBORS)
    train = pd.read_csv(T4_TRAIN)

    X = tfidf.transform([TICKET_TEXT])

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
                "Description": row["Description"],
            }
        )

    return {
        "status": "PASS",
        "transformed_shape": list(X.shape),
        "neighbors": resolved,
    }


# =====================================================================
# T5
#
# Compare the new ticket against the closest T4 historical ticket.
# =====================================================================

def run_t5(t4_result):

    closest = t4_result["neighbors"][0]

    historical_summary = clean_text(
        closest["Summary"]
    )

    historical_description = clean_text(
        closest["Description"]
    )

    first = t5_pair_text(
        TITLE,
        DESCRIPTION,
    )

    second = t5_pair_text(
        historical_summary,
        historical_description,
    )

    pair_text = (
        first
        + " [SEP] "
        + second
    )

    vectorizer = joblib.load(T5_TFIDF)
    classifier = joblib.load(T5_LOGREG)
    calibration = joblib.load(T5_CALIBRATION)

    X = vectorizer.transform(
        [pair_text]
    )

    decision = classifier.decision_function(X)

    # The frozen T5 calibration artifact is a dictionary
    # containing the accepted calibrators.
    sigmoid = calibration.get(
        "sigmoid_calibrator"
    )

    if sigmoid is None:
        raise RuntimeError(
            "Frozen T5 sigmoid calibrator missing."
        )

    calibrated = sigmoid.predict(
        decision.reshape(-1, 1)
    )

    return {
        "status": "PASS",
        "comparison_ticket_id": str(
            closest["ID"]
        ),
        "comparison_summary": historical_summary,
        "comparison_distance": float(
            closest["distance"]
        ),
        "decision_function": [
            float(x)
            for x in np.asarray(
                decision
            ).ravel()
        ],
        "calibrated_duplicate_evidence": [
            float(x)
            for x in np.asarray(
                calibrated
            ).ravel()
        ],
        "threshold_used": False,
        "autonomous_duplicate_decision": False,
    }


# =====================================================================
# T6
#
# Execute the frozen lexical component.
#
# MOD-010 semantic evidence cannot be generated for a new ticket
# because the validated frozen runtime explicitly does not load the
# semantic model. We therefore do NOT fabricate a hybrid score.
# =====================================================================

def run_t6(t4_result):

    vectorizer = joblib.load(T6_TFIDF)

    query_text = (
        "query_summary "
        + TITLE
        + " query_description "
        + DESCRIPTION
    )

    query_matrix = vectorizer.transform(
        [query_text]
    )

    candidate_rows = t4_result["neighbors"]

    candidate_texts = []

    for row in candidate_rows:

        candidate_text = (
            "candidate_summary "
            + clean_text(row["Summary"])
            + " candidate_description "
            + clean_text(row["Description"])
        )

        candidate_texts.append(
            candidate_text
        )

    candidate_matrix = vectorizer.transform(
        candidate_texts
    )

    lexical_scores = (
        candidate_matrix
        @ query_matrix.T
    ).toarray().ravel()

    order = np.argsort(
        -lexical_scores
    )

    lexical_rankings = []

    for rank, position in enumerate(
        order,
        start=1,
    ):

        row = candidate_rows[
            int(position)
        ]

        lexical_rankings.append(
            {
                "rank": rank,
                "ID": row["ID"],
                "lexical_score": float(
                    lexical_scores[position]
                ),
            }
        )

    return {
        "status": "PARTIAL_NATIVE_RUNTIME",
        "native_semantics": (
            "lexical retrieval evidence"
        ),
        "query_transformed_shape": list(
            query_matrix.shape
        ),
        "candidate_count": len(
            candidate_rows
        ),
        "lexical_rankings": lexical_rankings,
        "semantic_model_loaded": False,
        "semantic_score_available": False,
        "hybrid_mod010_score_available": False,
        "reason": (
            "The validated frozen T6 MOD-010 runtime "
            "uses stored MOD-009 semantic evidence and "
            "does not load a semantic model. Therefore "
            "a new-ticket semantic score cannot be "
            "reproduced without introducing a non-frozen "
            "component."
        ),
    }


# =====================================================================
# T7
# =====================================================================

def run_t7():

    t7 = load_t7_module()

    with T7_MODEL.open(
        "r",
        encoding="utf-8",
    ) as f:
        model = json.load(f)

    feature_names = model[
        "feature_names"
    ]

    beta_dict = model["beta"]

    sigma = float(
        model["sigma"]
    )

    beta = np.asarray(
        [
            float(beta_dict[name])
            for name in feature_names
        ],
        dtype=np.float64,
    )

    train = pd.read_csv(
        T7_TRAIN
    )

    creator_counts = (
        train["Creator"]
        .fillna("")
        .astype(str)
        .str.strip()
        .value_counts()
        .to_dict()
    )

    detail_counts = (
        train["Creator Detail"]
        .fillna("")
        .astype(str)
        .str.strip()
        .value_counts()
        .to_dict()
    )

    # Runtime ticket representation.
    #
    # Creator fields are unavailable for this new ticket, so
    # they are represented as empty rather than fabricated.
    runtime_row = {
        "ID": "H-RUN-006-NEW-TICKET",
        "Creation time": "2026-09-26T18:03:00Z",
        "Creator": "",
        "Creator Detail": "",
        "Summary": TITLE,
        "Description": DESCRIPTION,
    }

    X, ids, durations, events, names = (
        t7.make_features(
            [runtime_row],
            creator_counts,
            detail_counts,
        )
    )

    X = np.asarray(
        X,
        dtype=np.float64,
    )

    if list(names) != list(
        feature_names
    ):
        raise RuntimeError(
            "T7 feature order does not match "
            "frozen model feature order."
        )

    linear_predictor = X @ beta

    predicted_median_duration = np.exp(
        linear_predictor
    )

    return {
        "status": "PASS",
        "model_type": model[
            "model_type"
        ],
        "feature_count": len(
            feature_names
        ),
        "feature_matrix_shape": list(
            X.shape
        ),
        "linear_predictor": [
            float(x)
            for x in linear_predictor
        ],
        "predicted_median_duration": [
            float(x)
            for x in predicted_median_duration
        ],
        "sigma": sigma,
        "creator_evidence_available": False,
        "creator_detail_evidence_available": False,
        "fitting_performed": False,
        "parameter_selection": False,
    }


# =====================================================================
# MAIN
# =====================================================================

def main():

    print("=" * 72)
    print("H-RUN-006 — INTEGRATED FROZEN TICKET RUNTIME")
    print("=" * 72)

    print()
    print("TICKET:")
    print(TICKET_TEXT)

    print()
    print("[T1] CATEGORY")

    t1 = run_t1()

    print(
        f"prediction: {t1['prediction']}"
    )

    print()
    print("[T2] PRIORITY")

    t2 = run_t2()

    print(
        f"prediction: {t2['prediction']}"
    )

    print()
    print("[T3] SEVERITY")

    t3 = run_t3()

    print(
        f"prediction: {t3['prediction']}"
    )

    print()
    print("[T4] HISTORICAL ASSIGNMENT EVIDENCE")

    t4 = run_t4()

    for row in t4["neighbors"]:

        print(
            f"rank={row['rank']} "
            f"distance={row['distance']:.6f} "
            f"ID={row['ID']} "
            f"assignee={row['target_assignee']}"
        )

    print()
    print("[T5] DUPLICATE EVIDENCE")

    t5 = run_t5(t4)

    print(
        "comparison ticket:",
        t5["comparison_ticket_id"],
    )

    print(
        "calibrated evidence:",
        t5[
            "calibrated_duplicate_evidence"
        ],
    )

    print(
        "threshold used:",
        t5["threshold_used"],
    )

    print()
    print("[T6] RELATED-TICKET RETRIEVAL")

    t6 = run_t6(t4)

    print(
        "status:",
        t6["status"],
    )

    print(
        "semantic score available:",
        t6[
            "semantic_score_available"
        ],
    )

    for row in t6[
        "lexical_rankings"
    ]:

        print(
            f"rank={row['rank']} "
            f"ID={row['ID']} "
            f"lexical_score={row['lexical_score']:.6f}"
        )

    print()
    print("[T7] RESOLUTION-TIME EVIDENCE")

    t7 = run_t7()

    print(
        "status:",
        t7["status"],
    )

    print(
        "predicted median duration:",
        t7[
            "predicted_median_duration"
        ],
    )

    # -------------------------------------------------------------
    # T8
    # -------------------------------------------------------------

    t8 = {
        "status": "NATIVE_EVIDENCE_BOUNDARY",
        "variable_evidence": True,
        "missing_evidence_is_unavailable": True,
        "available_components": [
            "T1",
            "T2",
            "T3",
            "T4",
            "T5",
            "T6_lexical",
            "T7",
        ],
        "unavailable_components": [
            "T6_semantic_for_new_ticket",
            "T6_MOD010_full_hybrid_for_new_ticket",
        ],
        "universal_probability_aggregation": False,
        "synthetic_fusion_target": False,
    }

    print()
    print("[T8] EVIDENCE FUSION")
    print(
        "status:",
        t8["status"],
    )

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
    print(
        "universal confidence: NOT_CREATED"
    )
    print(
        "universal risk: NOT_CREATED"
    )

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
    print(
        "automation: NOT_ESTABLISHED"
    )
    print(
        "human review: NOT_ESTABLISHED"
    )
    print(
        "universal threshold: NOT_ESTABLISHED"
    )

    # -------------------------------------------------------------
    # Controls
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
    # Final artifact
    # -------------------------------------------------------------

    result = {
        "operation":
            "H-RUN-006",

        "operation_name":
            "integrated frozen ticket runtime",

        "status":
            "PASS",

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

        "controls":
            controls,

        "interpretation": (
            "One new ticket was executed through the "
            "frozen runtime architecture. T1-T5 and T7 "
            "produced native runtime evidence. T6 "
            "produced lexical retrieval evidence; its "
            "full MOD-010 hybrid semantic score was not "
            "fabricated because the validated frozen "
            "runtime does not load the semantic model. "
            "T8-T10 preserve native evidence and policy "
            "boundaries."
        ),
    }

    METRICS.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            result,
            f,
            indent=2,
            default=str,
        )

    print()
    print("=" * 72)
    print("H-RUN-006 STATUS: PASS")
    print(
        "T1/T2/T3/T4/T5/T7: EXECUTED"
    )
    print(
        "T6: LEXICAL EVIDENCE EXECUTED; "
        "SEMANTIC BRANCH UNAVAILABLE"
    )
    print(
        "T8/T9/T10: NATIVE BOUNDARIES PRESERVED"
    )
    print(
        f"OUTPUT: {OUTPUT}"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()