from pathlib import Path
import json
import numpy as np
import pandas as pd
import joblib


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T1_MODEL = ROOT / "modeling/T1/baselines/t1_it_support_char_svm.joblib"
T2_MODEL = ROOT / "modeling/T2/models/t2_class_weighted_tfidf_logreg.joblib"
T3_MODEL = ROOT / "modeling/T3/models/t3_class_weighted_tfidf_logreg.joblib"

T4_TFIDF = ROOT / "modeling/T4/results/mod007_checkpoints/t4_mod007_tfidf.joblib"
T4_NEIGHBORS = ROOT / "modeling/T4/results/mod007_checkpoints/t4_mod007_neighbors.joblib"
T4_POPULATION = ROOT / "modeling/T4/derived/t4_train.csv"

T5_TFIDF = ROOT / "modeling/T5/models/t5_mod005_tfidf.joblib"
T5_CLASSIFIER = ROOT / "modeling/T5/models/t5_mod005_logreg.joblib"
T5_CALIBRATION = ROOT / "modeling/T5/models/t5_mod007_calibration_models.joblib"

T6_TFIDF = ROOT / "modeling/T6/models/t6_mod004_tfidf_vectorizer.joblib"

T7_MODEL = ROOT / "modeling/T7/metrics/t7_mod010_log_normal_aft_model.json"
T7_TRAIN = ROOT / "modeling/T7/splits/t7_train.csv"

OUTPUT = ROOT / "modeling/FMP/metrics/h_run015_final_ticket_orchestrator.json"


def fail(message):
    raise RuntimeError(message)


def load_joblib(path):
    if not path.exists():
        fail(f"Missing frozen artifact: {path}")
    return joblib.load(path)


def require_text(ticket):
    text = f"{ticket['title']}\n{ticket['description']}".strip()
    if not text:
        fail("Ticket title + description are empty.")
    return text


def run_t1(text):
    bundle = load_joblib(T1_MODEL)
    X = bundle["features"].transform([text])
    prediction = bundle["model"].predict(X)[0]

    return {
        "status": "EXECUTED",
        "prediction": str(prediction),
        "feature_shape": list(X.shape),
    }


def run_t2(text):
    bundle = load_joblib(T2_MODEL)
    X = bundle["vectorizer"].transform([text])
    prediction = bundle["model"].predict(X)[0]

    return {
        "status": "EXECUTED",
        "prediction": str(prediction),
        "feature_shape": list(X.shape),
    }


def run_t3(text):
    bundle = load_joblib(T3_MODEL)
    X = bundle["vectorizer"].transform([text])
    model = bundle["model"]

    prediction = model.predict(X)[0]
    scores = model.decision_function(X)

    if np.ndim(scores) == 1:
        score_map = {
            "native_decision_score": float(scores[0])
        }
    else:
        score_map = {
            str(cls): float(score)
            for cls, score in zip(model.classes_, scores[0])
        }

    return {
        "status": "EXECUTED",
        "prediction": str(prediction),
        "native_decision_scores": score_map,
        "decision_scores_are_probabilities": False,
    }


def run_t4(text, top_k=5):
    vectorizer = load_joblib(T4_TFIDF)
    neighbors = load_joblib(T4_NEIGHBORS)
    population = pd.read_csv(T4_POPULATION)

    X = vectorizer.transform([text])
    distances, indices = neighbors.kneighbors(
        X,
        n_neighbors=top_k
    )

    results = []

    for rank, (distance, index) in enumerate(
        zip(distances[0], indices[0]),
        start=1
    ):
        row = population.iloc[int(index)]

        results.append({
            "rank": rank,
            "population_index": int(index),
            "distance": float(distance),
            "ID": str(row["ID"]),
            "summary": str(row["Summary"]),
            "target_assignee": str(row["target_assignee"]),
        })

    return {
        "status": "EXECUTED",
        "retrieved_count": len(results),
        "evidence_semantics": "historical_retrieval_only",
        "autonomous_assignment": False,
        "neighbors": results,
    }


def run_t5(first_text, comparison_text):
    vectorizer = load_joblib(T5_TFIDF)
    classifier = load_joblib(T5_CLASSIFIER)
    calibration = load_joblib(T5_CALIBRATION)

    pair_text = f"{first_text} [SEP] {comparison_text}"
    X = vectorizer.transform([pair_text])

    decision = classifier.decision_function(X)

    sigmoid = (
        calibration.get("sigmoid_calibrator")
        if isinstance(calibration, dict)
        else None
    )

    calibrated = None

    if sigmoid is not None:
        calibrated = sigmoid.predict(
            np.asarray(decision).reshape(-1, 1)
        )

    return {
        "status": "EXECUTED",
        "native_decision_score": float(
            np.asarray(decision).ravel()[0]
        ),
        "calibrated_duplicate_evidence": (
            float(np.asarray(calibrated).ravel()[0])
            if calibrated is not None
            else None
        ),
        "threshold_used": False,
        "autonomous_duplicate_decision": False,
        "semantics": "pairwise_duplicate_evidence_only",
    }


def run_t6_lexical(text, t4_neighbors):
    vectorizer = load_joblib(T6_TFIDF)
    query = vectorizer.transform([text])

    candidates = []

    for item in t4_neighbors:
        candidate_text = (
            f"{item['summary']}\n"
            f"{item['ID']}"
        )

        candidate_vector = vectorizer.transform(
            [candidate_text]
        )

        numerator = query.multiply(candidate_vector).sum()
        q_norm = np.sqrt(query.multiply(query).sum())
        c_norm = np.sqrt(
            candidate_vector.multiply(candidate_vector).sum()
        )

        if q_norm == 0 or c_norm == 0:
            score = 0.0
        else:
            score = float(
                numerator / (q_norm * c_norm)
            )

        candidates.append({
            "ID": item["ID"],
            "lexical_score": score,
        })

    candidates.sort(
        key=lambda x: x["lexical_score"],
        reverse=True
    )

    for rank, item in enumerate(candidates, start=1):
        item["rank"] = rank

    return {
        "status": "PARTIAL_NATIVE_RUNTIME",
        "semantic_score_available": False,
        "full_mod010_hybrid_score_available": False,
        "candidates": candidates,
    }


def run_t7(ticket):
    with open(T7_MODEL, "r", encoding="utf-8") as f:
        payload = json.load(f)

    train = pd.read_csv(T7_TRAIN)

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

    summary_features = text_features(summary)
    description_features = text_features(description)

    month = (
        2.0 * np.pi * (creation_time.month - 1) / 12.0
    )

    weekday = (
        2.0 * np.pi * creation_time.weekday() / 7.0
    )

    hour = (
        2.0 * np.pi * creation_time.hour / 24.0
    )

    raw = {
        "creator_frequency_log1p":
            float(np.log1p(
                creator_counts.get(creator.strip(), 0)
            )),

        "creator_detail_frequency_log1p":
            float(np.log1p(
                creator_detail_counts.get(
                    creator_detail.strip(),
                    0
                )
            )),

        "summary_chars_log1p":
            float(np.log1p(summary_features[0])),

        "summary_words_log1p":
            float(np.log1p(summary_features[1])),

        "summary_digits_log1p":
            float(np.log1p(summary_features[2])),

        "summary_lines_log1p":
            float(np.log1p(summary_features[3])),

        "summary_uppercase_log1p":
            float(np.log1p(summary_features[4])),

        "summary_missing":
            float(summary_features[5]),

        "description_chars_log1p":
            float(np.log1p(description_features[0])),

        "description_words_log1p":
            float(np.log1p(description_features[1])),

        "description_digits_log1p":
            float(np.log1p(description_features[2])),

        "description_lines_log1p":
            float(np.log1p(description_features[3])),

        "description_uppercase_log1p":
            float(np.log1p(description_features[4])),

        "description_missing":
            float(description_features[5]),

        # AUTHORITATIVE T7 FORMULA
        "creation_year_scaled":
            (creation_time.year - 2010.0) / 10.0,

        "creation_month_sin":
            float(np.sin(month)),

        "creation_month_cos":
            float(np.cos(month)),

        "creation_weekday_sin":
            float(np.sin(weekday)),

        "creation_weekday_cos":
            float(np.cos(weekday)),

        "creation_hour_sin":
            float(np.sin(hour)),

        "creation_hour_cos":
            float(np.cos(hour)),
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

    if X_raw.shape[1] != len(feature_names):
        fail("T7 feature count mismatch.")

    if len(mean) != len(feature_names):
        fail("T7 standardization mean mismatch.")

    if len(std) != len(feature_names):
        fail("T7 standardization std mismatch.")

    if len(beta) != len(feature_names):
        fail("T7 beta alignment mismatch.")

    X_std = (X_raw - mean) / std

    if not np.all(np.isfinite(X_std)):
        fail("T7 standardized features contain non-finite values.")

    linear_predictor = float(
        (X_std @ beta).item()
    )

    predicted_seconds = float(
        np.exp(linear_predictor)
    )

    return {
        "status": "EXECUTED_WITH_SUPPORT_LIMITATION",
        "predicted_median_duration_seconds":
            predicted_seconds,
        "predicted_median_duration_hours":
            predicted_seconds / 3600.0,
        "predicted_median_duration_days":
            predicted_seconds / 86400.0,
        "linear_predictor":
            linear_predictor,
        "training_year_range": [1997, 2020],
        "runtime_creation_year":
            int(creation_time.year),
        "temporal_support":
            "OUTSIDE_OBSERVED_TRAINING_RANGE",
        "operational_sla_interpretation":
            False,
    }


def build_downstream_boundary():
    return {
        "T8": {
            "status": "BOUNDARY_ENVELOPE",
            "architecture": "CLOSED",
            "ticket_facing_execution": False,
            "missing_evidence_is_unavailable": True,
            "native_task_semantics_preserved": True,
            "universal_probability_fusion": False,
            "synthetic_fusion_target": False,
        },

        "T9": {
            "status": "BOUNDARY_ENVELOPE",
            "task_specific_reliability_only": True,
            "universal_confidence": "NOT_CREATED",
            "universal_risk": "NOT_CREATED",
            "cross_task_probability_aggregation": False,
        },

        "T10": {
            "status": "POLICY_BOUNDARY",
            "AUTOMATION": "NOT_ESTABLISHED",
            "HUMAN_REVIEW": "NOT_ESTABLISHED",
            "UNIVERSAL_THRESHOLD": "NOT_ESTABLISHED",
            "UNIVERSAL_CONFIDENCE": "NOT_CREATED",
            "UNIVERSAL_RISK": "NOT_CREATED",
        },

        "T11": {
            "status": "SPECIFICATION_ONLY",
            "operational_feedback_population": "NOT_AVAILABLE",
            "production_feedback_loop": "NOT_ESTABLISHED",
            "future_re_evaluation":
                "REQUIRES_REAL_OPERATIONAL_FEEDBACK",
        },
    }


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

    text = require_text(ticket)

    print("=" * 72)
    print("H-RUN-015R2 — FINAL TICKET-FACING ORCHESTRATOR")
    print("=" * 72)

    print("\n[TICKET]")
    print("ID:", ticket["ticket_id"])
    print("Title:", ticket["title"])

    print("\n[CONTROL]")
    print("training/retraining: NO")
    print("model modification: NO")
    print("prediction modification: NO")
    print("locked-test use: NO")
    print("threshold optimization: NO")

    t1 = run_t1(text)
    print("\n[T1]")
    print("status:", t1["status"])
    print("prediction:", t1["prediction"])

    t2 = run_t2(text)
    print("\n[T2]")
    print("status:", t2["status"])
    print("prediction:", t2["prediction"])

    t3 = run_t3(text)
    print("\n[T3]")
    print("status:", t3["status"])
    print("prediction:", t3["prediction"])

    t4 = run_t4(text)
    print("\n[T4]")
    print("status:", t4["status"])
    print("retrieved:", t4["retrieved_count"])
    print("top IDs:", [x["ID"] for x in t4["neighbors"]])

    comparison_text = (
        f"{t4['neighbors'][0]['summary']}\n"
        f"{t4['neighbors'][0]['ID']}"
    )

    t5 = run_t5(text, comparison_text)

    print("\n[T5]")
    print("status:", t5["status"])
    print(
        "calibrated duplicate evidence:",
        t5["calibrated_duplicate_evidence"]
    )
    print("threshold used:", t5["threshold_used"])

    t6 = run_t6_lexical(text, t4["neighbors"])

    print("\n[T6]")
    print("status:", t6["status"])
    print(
        "full MOD-010 hybrid available:",
        t6["full_mod010_hybrid_score_available"]
    )
    print(
        "top lexical IDs:",
        [x["ID"] for x in t6["candidates"]]
    )

    t7 = run_t7(ticket)

    print("\n[T7]")
    print("status:", t7["status"])
    print(
        "median duration seconds:",
        round(
            t7["predicted_median_duration_seconds"],
            6
        )
    )
    print(
        "temporal support:",
        t7["temporal_support"]
    )

    downstream = build_downstream_boundary()

    print("\n[T8]")
    print("status:", downstream["T8"]["status"])

    print("\n[T9]")
    print("status:", downstream["T9"]["status"])

    print("\n[T10]")
    print(
        "automation:",
        downstream["T10"]["AUTOMATION"]
    )

    print("\n[T11]")
    print("status:", downstream["T11"]["status"])

    result = {
        "operation": "H-RUN-015R2",
        "operation_name":
            "FINAL_TICKET_FACING_ORCHESTRATOR",
        "status": "PASS",
        "ticket": ticket,
        "components": {
            "T1": t1,
            "T2": t2,
            "T3": t3,
            "T4": t4,
            "T5": t5,
            "T6": t6,
            "T7": t7,
        },
        "downstream": downstream,
        "controls": {
            "training": False,
            "retraining": False,
            "model_modification": False,
            "prediction_modification": False,
            "locked_test_use": False,
            "threshold_optimization": False,
            "universal_confidence_creation": False,
            "universal_risk_creation": False,
            "synthetic_fusion_target_creation": False,
        },
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
    print("H-RUN-015R2 COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()