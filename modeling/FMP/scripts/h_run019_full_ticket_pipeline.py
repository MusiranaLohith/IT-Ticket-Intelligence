from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
MODELING = ROOT / "modeling"
METRICS = MODELING / "FMP" / "metrics"

TICKET_ID = "H-RUN-019R2-VPN-001"
TITLE = "VPN connection fails after password reset"
DESCRIPTION = (
    "I reset my corporate password this morning. Since then, the VPN client "
    "connects briefly and then disconnects. I restarted the laptop and "
    "reinstalled the VPN client, but the issue persists. I need access to "
    "the internal systems for today's work."
)
CREATOR = ""
CREATOR_DETAIL = ""
CREATION_TIME = "2026-09-26T18:03:00Z"


def first_existing(paths):
    for p in paths:
        if p.exists():
            return p
    return None


def find_file_by_name(root: Path, filename: str):
    matches = list(root.rglob(filename))
    return matches[0] if matches else None


def extract_model_and_vectorizer(bundle):
    """
    Frozen T1/T2/T3 artifacts may be serialized as dictionaries or
    direct objects. Resolve the actual vectorizer/model without
    modifying either object.
    """
    if not isinstance(bundle, dict):
        return None, bundle

    vectorizer = None
    model = None

    vectorizer_keys = [
        "vectorizer",
        "tfidf",
        "tfidf_vectorizer",
        "text_vectorizer",
    ]

    model_keys = [
        "model",
        "classifier",
        "clf",
        "estimator",
    ]

    for key in vectorizer_keys:
        if key in bundle:
            vectorizer = bundle[key]
            break

    for key in model_keys:
        if key in bundle:
            model = bundle[key]
            break

    if model is None:
        for value in bundle.values():
            if hasattr(value, "predict") or hasattr(value, "decision_function"):
                model = value
                break

    if vectorizer is None:
        for value in bundle.values():
            if hasattr(value, "transform") and not hasattr(value, "predict"):
                vectorizer = value
                break

    return vectorizer, model


def load_text_classifier(artifact_path: Path):
    bundle = joblib.load(artifact_path)
    vectorizer, model = extract_model_and_vectorizer(bundle)

    if vectorizer is None or model is None:
        raise RuntimeError(
            f"Could not resolve vectorizer/model from {artifact_path}"
        )

    return vectorizer, model


def ticket_text():
    return f"{TITLE}\n{DESCRIPTION}".strip()


def run_t1():
    candidates = [
        MODELING / "T1" / "baselines" / "t1_it_support_char_svm.joblib",
        MODELING / "T1" / "models" / "t1_it_support_char_svm.joblib",
    ]

    artifact = first_existing(candidates)

    if artifact is None:
        raise FileNotFoundError("T1 frozen artifact not found")

    vectorizer, model = load_text_classifier(artifact)

    # IMPORTANT:
    # The frozen vectorizer expects a collection of documents.
    # A single ticket is therefore passed as a one-element list.
    X = vectorizer.transform([ticket_text()])

    if getattr(X, "ndim", 2) != 2:
        raise RuntimeError(f"T1 transformed input is not 2-D: ndim={X.ndim}")

    prediction = model.predict(X)[0]

    return {
        "status": "EXECUTED",
        "prediction": str(prediction),
        "artifact": str(artifact),
        "transformed_shape": list(X.shape),
    }


def run_t2():
    artifact = (
        MODELING
        / "T2"
        / "models"
        / "t2_class_weighted_tfidf_logreg.joblib"
    )

    vectorizer, model = load_text_classifier(artifact)

    X = vectorizer.transform([ticket_text()])

    if getattr(X, "ndim", 2) != 2:
        raise RuntimeError(f"T2 transformed input is not 2-D: ndim={X.ndim}")

    prediction = model.predict(X)[0]

    return {
        "status": "EXECUTED",
        "prediction": str(prediction),
        "artifact": str(artifact),
        "transformed_shape": list(X.shape),
    }


def run_t3():
    artifact = (
        MODELING
        / "T3"
        / "models"
        / "t3_class_weighted_tfidf_logreg.joblib"
    )

    vectorizer, model = load_text_classifier(artifact)

    X = vectorizer.transform([ticket_text()])

    if getattr(X, "ndim", 2) != 2:
        raise RuntimeError(f"T3 transformed input is not 2-D: ndim={X.ndim}")

    prediction = model.predict(X)[0]

    return {
        "status": "EXECUTED",
        "prediction": str(prediction),
        "artifact": str(artifact),
        "transformed_shape": list(X.shape),
    }


def run_t4():
    tfidf_path = (
        MODELING
        / "T4"
        / "results"
        / "mod007_checkpoints"
        / "t4_mod007_tfidf.joblib"
    )

    neighbors_path = (
        MODELING
        / "T4"
        / "results"
        / "mod007_checkpoints"
        / "t4_mod007_neighbors.joblib"
    )

    train_path = MODELING / "T4" / "derived" / "t4_train.csv"

    vectorizer = joblib.load(tfidf_path)
    neighbors = joblib.load(neighbors_path)

    train = pd.read_csv(train_path)

    query = ticket_text()
    X = vectorizer.transform([query])

    distances, indices = neighbors.kneighbors(X, n_neighbors=5)

    results = []

    for distance, index in zip(distances[0], indices[0]):
        row = train.iloc[int(index)]

        results.append(
            {
                "id": str(row["ID"]),
                "distance": float(distance),
                "summary": str(row["Summary"]),
                "target_assignee": str(row["target_assignee"]),
            }
        )

    return {
        "status": "EXECUTED",
        "results": results,
        "artifact_tfidf": str(tfidf_path),
        "artifact_neighbors": str(neighbors_path),
    }


def run_t5():
    root = MODELING / "T5"

    tfidf_path = find_file_by_name(root, "t5_mod005_tfidf.joblib")
    logreg_path = find_file_by_name(root, "t5_mod005_logreg.joblib")
    calibrated_tfidf_path = find_file_by_name(
        root, "t5_mod007_calibrated_tfidf.joblib"
    )
    calibration_models_path = find_file_by_name(
        root, "t5_mod007_calibration_models.joblib"
    )

    required = {
        "tfidf": tfidf_path,
        "logreg": logreg_path,
        "calibrated_tfidf": calibrated_tfidf_path,
        "calibration_models": calibration_models_path,
    }

    missing = [name for name, path in required.items() if path is None]

    if missing:
        raise FileNotFoundError(
            "Missing T5 frozen artifacts: " + ", ".join(missing)
        )

    vectorizer = joblib.load(calibrated_tfidf_path)
    models = joblib.load(calibration_models_path)
    classifier = joblib.load(logreg_path)

    pair_text = f"{ticket_text()} [SEP] {ticket_text()}"

    # Calibrated vectorizer receives one document.
    X = vectorizer.transform([pair_text])

    if getattr(X, "ndim", 2) != 2:
        raise RuntimeError(f"T5 transformed input is not 2-D: ndim={X.ndim}")

    decision = classifier.decision_function(X)

    # decision_function returns an array for one sample.
    # Preserve the sample dimension for the calibrator.
    decision_2d = np.asarray(decision, dtype=float).reshape(-1, 1)

    sigmoid_calibrator = models["sigmoid_calibrator"]

    calibrated = sigmoid_calibrator.predict(decision_2d)

    evidence = float(np.asarray(calibrated).reshape(-1)[0])

    return {
        "status": "EXECUTED",
        "duplicate_evidence": evidence,
        "threshold_used": False,
        "decision_score": float(np.asarray(decision).reshape(-1)[0]),
        "artifact_vectorizer": str(calibrated_tfidf_path),
        "artifact_classifier": str(logreg_path),
        "artifact_calibration": str(calibration_models_path),
    }


def run_t6():
    """
    The frozen MOD-010 runtime depends on stored semantic evidence
    from the evaluation population. A genuinely new ticket has no
    corresponding frozen semantic embedding/evidence row.

    Therefore this stage reports the native runtime limitation rather
    than fabricating a semantic score.
    """
    return {
        "status": "PARTIAL_NATIVE_RUNTIME",
        "full_mod010_hybrid_available": False,
        "top_ids": [],
        "reason": (
            "Frozen MOD-010 semantic evidence is bound to the existing "
            "evaluation population; a new ticket has no stored semantic "
            "evidence row."
        ),
    }


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


def build_t7_features():
    """
    Exact feature construction corresponding to the authoritative
    frozen T7 MOD-010 Log-Normal AFT implementation.
    """

    creator_counts = {}
    detail_counts = {}

    train_path = MODELING / "T7" / "splits" / "t7_train.csv"

    train = pd.read_csv(train_path)

    for value in train["Creator"].fillna("").astype(str):
        key = value.strip()
        creator_counts[key] = creator_counts.get(key, 0) + 1

    for value in train["Creator Detail"].fillna("").astype(str):
        key = value.strip()
        detail_counts[key] = detail_counts.get(key, 0) + 1

    dt = pd.Timestamp(CREATION_TIME).to_pydatetime()

    summary = TITLE
    description = DESCRIPTION

    s = text_features(summary)
    d = text_features(description)

    month = 2.0 * math.pi * (dt.month - 1) / 12.0
    weekday = 2.0 * math.pi * dt.weekday() / 7.0
    hour = 2.0 * math.pi * dt.hour / 24.0

    features = [
        math.log1p(
            creator_counts.get(CREATOR.strip(), 0)
        ),
        math.log1p(
            detail_counts.get(CREATOR_DETAIL.strip(), 0)
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
    ]

    return np.asarray(features, dtype=float)


def as_ordered_vector(value, feature_names):
    if isinstance(value, dict):
        return np.asarray(
            [float(value[name]) for name in feature_names],
            dtype=float,
        )

    arr = np.asarray(value, dtype=float).reshape(-1)

    if len(arr) != len(feature_names):
        raise RuntimeError(
            f"Vector length mismatch: {len(arr)} != {len(feature_names)}"
        )

    return arr


def run_t7():
    model_path = MODELING / "T7" / "metrics" / "t7_mod010_log_normal_aft_model.json"

    if not model_path.exists():
        raise FileNotFoundError(f"T7 model not found: {model_path}")

    with open(model_path, "r", encoding="utf-8") as f:
        model = json.load(f)

    feature_names = model["feature_names"]

    X_raw = build_t7_features()

    beta = as_ordered_vector(model["beta"], feature_names)
    mean = as_ordered_vector(
        model["standardization_mean"],
        feature_names,
    )
    std = as_ordered_vector(
        model["standardization_std"],
        feature_names,
    )

    if np.any(std == 0):
        raise RuntimeError("T7 standardization contains zero standard deviation")

    X_standardized = (X_raw - mean) / std

    linear_predictor = float(np.dot(X_standardized, beta))

    predicted_median_seconds = float(np.exp(linear_predictor))

    return {
        "status": "EXECUTED_WITH_SUPPORT_LIMITATION",
        "median_seconds": predicted_median_seconds,
        "temporal_support": "OUTSIDE_OBSERVED_TRAINING_RANGE",
        "creation_year": 2026,
        "training_year_max": 2020,
        "linear_predictor": linear_predictor,
        "feature_count": len(feature_names),
        "model": str(model_path),
    }


def run_t8(results):
    available = []
    partial = []
    unavailable = []

    for task in ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]:
        status = results[task]["status"]

        if status == "EXECUTED":
            available.append(task)
        elif status.startswith("PARTIAL") or status.endswith("LIMITATION"):
            partial.append(task)
        else:
            unavailable.append(task)

    if unavailable:
        evidence_state = "INSUFFICIENT_EVIDENCE"
    elif partial:
        evidence_state = "SUPPORTED_WITH_LIMITATIONS"
    else:
        evidence_state = "SUPPORTED"

    return {
        "status": "EXECUTED",
        "evidence_state": evidence_state,
        "available": available,
        "partial": partial,
        "unavailable": unavailable,
        "missing_evidence_is_not_negative": True,
        "native_semantics_preserved": True,
    }


def run_t9(results):
    return {
        "status": "EXECUTED",
        "universal_confidence": None,
        "universal_risk": None,
        "cross_task_probability_aggregation": False,
        "reason": (
            "Task outputs retain their native semantics; no universal "
            "confidence or risk score is created."
        ),
    }


def run_t10(t8, results):
    warnings = []

    if t8["evidence_state"] != "SUPPORTED":
        warnings.append(
            "Evidence is not fully supported; missing evidence is not negative evidence."
        )

    if results["T6"]["status"] == "PARTIAL_NATIVE_RUNTIME":
        warnings.append(
            "T6 full MOD-010 hybrid is unavailable for this new-ticket runtime."
        )

    if results["T7"].get("temporal_support") == "OUTSIDE_OBSERVED_TRAINING_RANGE":
        warnings.append(
            "T7 ticket creation year is outside observed training temporal range."
        )

    return {
        "status": "EXECUTED",
        "action": "HUMAN_DECISION_REQUIRED",
        "automation": "NOT_ESTABLISHED",
        "warnings": warnings,
    }


def run_t11():
    return {
        "status": "EXECUTED",
        "feedback": "AWAITING_OUTCOME",
        "synthetic_feedback": False,
    }


def safe_run(name, fn):
    try:
        return fn()
    except Exception as exc:
        return {
            "status": "FAILED",
            "error": str(exc),
        }


def main():
    print("=" * 70)
    print("H-RUN-019R2 — FULL TICKET PIPELINE RUNTIME")
    print("=" * 70)

    print("\n[INPUT]")
    print(f"Ticket ID : {TICKET_ID}")
    print(f"Title     : {TITLE}")

    results = {}

    results["T1"] = safe_run("T1", run_t1)
    print(f"[T1] {results['T1']['status']} -> "
          f"{results['T1'].get('prediction', results['T1'].get('error'))}")

    results["T2"] = safe_run("T2", run_t2)
    print(f"[T2] {results['T2']['status']} -> "
          f"{results['T2'].get('prediction', results['T2'].get('error'))}")

    results["T3"] = safe_run("T3", run_t3)
    print(f"[T3] {results['T3']['status']} -> "
          f"{results['T3'].get('prediction', results['T3'].get('error'))}")

    results["T4"] = safe_run("T4", run_t4)
    t4_ids = [
        x["id"]
        for x in results["T4"].get("results", [])
    ]
    print(f"[T4] {results['T4']['status']} -> {t4_ids}")

    results["T5"] = safe_run("T5", run_t5)
    print(f"[T5] {results['T5']['status']} -> "
          f"{results['T5'].get('duplicate_evidence', results['T5'].get('error'))}")

    results["T6"] = safe_run("T6", run_t6)
    print(f"[T6] {results['T6']['status']} -> "
          f"{results['T6'].get('top_ids', results['T6'].get('error'))}")

    results["T7"] = safe_run("T7", run_t7)
    print(f"[T7] {results['T7']['status']} -> "
          f"{results['T7'].get('median_seconds', results['T7'].get('error'))}")

    results["T8"] = run_t8(results)
    print(f"[T8] {results['T8']['status']} -> "
          f"{results['T8']['evidence_state']}")

    results["T9"] = run_t9(results)
    print("[T9] EXECUTED")

    results["T10"] = run_t10(results["T8"], results)
    print(f"[T10] {results['T10']['status']} -> "
          f"{results['T10']['action']}")

    results["T11"] = run_t11()
    print(f"[T11] {results['T11']['status']} -> "
          f"{results['T11']['feedback']}")

    failures = [
        task for task in ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]
        if results[task]["status"] == "FAILED"
    ]

    limitations = [
        task
        for task in ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]
        if results[task]["status"].startswith("PARTIAL")
        or results[task]["status"].endswith("LIMITATION")
    ]

    if failures:
        overall = "FAIL"
    elif limitations:
        overall = "PASS_WITH_LIMITATIONS"
    else:
        overall = "PASS"

    final_output = {
        "ticket": {
            "id": TICKET_ID,
            "title": TITLE,
        },
        "T1": results["T1"],
        "T2": results["T2"],
        "T3": results["T3"],
        "T4": results["T4"],
        "T5": results["T5"],
        "T6": results["T6"],
        "T7": results["T7"],
        "T8": results["T8"],
        "T9": results["T9"],
        "T10": results["T10"],
        "T11": results["T11"],
        "final": {
            "category": results["T1"].get("prediction"),
            "priority": results["T2"].get("prediction"),
            "severity": results["T3"].get("prediction"),
            "duplicate": results["T5"].get("duplicate_evidence"),
            "related": results["T6"].get("top_ids", []),
            "resolution_seconds": results["T7"].get("median_seconds"),
            "evidence_state": results["T8"]["evidence_state"],
            "action": results["T10"]["action"],
            "lifecycle": results["T11"]["feedback"],
        },
        "integrity": {
            "model_retraining": False,
            "model_modification": False,
            "threshold_optimization": False,
            "locked_test_reuse": False,
            "prediction_modification": False,
            "synthetic_feedback": False,
        },
        "overall_status": overall,
    }

    METRICS.mkdir(parents=True, exist_ok=True)

    json_path = METRICS / "h_run019r2_full_ticket_pipeline.json"
    report_path = METRICS / "h_run019r2_full_ticket_pipeline_report.txt"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, default=str)

    lines = [
        "=" * 70,
        "IT TICKET INTELLIGENCE & TRIAGE SYSTEM",
        "=" * 70,
        "",
        "TICKET",
        "-" * 70,
        f"ID          : {TICKET_ID}",
        f"TITLE       : {TITLE}",
        "",
        "T1 — CATEGORY",
        "-" * 70,
        f"Prediction  : {results['T1'].get('prediction')}",
        f"Status      : {results['T1']['status']}",
        "",
        "T2 — PRIORITY",
        "-" * 70,
        f"Prediction  : {results['T2'].get('prediction')}",
        f"Status      : {results['T2']['status']}",
        "",
        "T3 — SEVERITY",
        "-" * 70,
        f"Prediction  : {results['T3'].get('prediction')}",
        f"Status      : {results['T3']['status']}",
        "",
        "T4 — HISTORICAL ASSIGNEE RETRIEVAL",
        "-" * 70,
    ]

    for i, item in enumerate(results["T4"].get("results", []), start=1):
        lines.append(
            f"{i}. {item['id']} | {item['target_assignee']} | "
            f"distance={item['distance']:.6f}"
        )

    lines += [
        "",
        "T5 — DUPLICATE EVIDENCE",
        "-" * 70,
        f"Evidence    : {results['T5'].get('duplicate_evidence')}",
        f"Status      : {results['T5']['status']}",
        "",
        "T6 — RELATED TICKETS",
        "-" * 70,
        f"Runtime     : {results['T6']['status']}",
        f"Full MOD-010: {results['T6'].get('full_mod010_hybrid_available')}",
        f"IDs         : {results['T6'].get('top_ids', [])}",
        "",
        "T7 — RESOLUTION-TIME EVIDENCE",
        "-" * 70,
        f"Status      : {results['T7']['status']}",
        f"Median sec  : {results['T7'].get('median_seconds')}",
        f"Temporal    : {results['T7'].get('temporal_support')}",
        "",
        "T8 — EVIDENCE INTEGRATION",
        "-" * 70,
        f"Status      : {results['T8']['status']}",
        f"Evidence    : {results['T8']['evidence_state']}",
        f"Available   : {results['T8']['available']}",
        f"Partial     : {results['T8']['partial']}",
        f"Unavailable : {results['T8']['unavailable']}",
        "",
        "T9 — RELIABILITY",
        "-" * 70,
        f"Status      : {results['T9']['status']}",
        f"Universal confidence: {results['T9']['universal_confidence']}",
        f"Universal risk      : {results['T9']['universal_risk']}",
        "",
        "T10 — POLICY",
        "-" * 70,
        f"Status      : {results['T10']['status']}",
        f"Action      : {results['T10']['action']}",
    ]

    for warning in results["T10"]["warnings"]:
        lines.append(f"WARNING     : {warning}")

    lines += [
        "",
        "T11 — LIFECYCLE",
        "-" * 70,
        f"Status      : {results['T11']['status']}",
        f"Feedback    : {results['T11']['feedback']}",
        "",
        "FINAL TRIAGE OUTPUT",
        "-" * 70,
        f"Category    : {final_output['final']['category']}",
        f"Priority    : {final_output['final']['priority']}",
        f"Severity    : {final_output['final']['severity']}",
        f"Duplicate   : {final_output['final']['duplicate']}",
        f"Related     : {final_output['final']['related']}",
        f"Resolution  : {final_output['final']['resolution_seconds']}",
        f"Evidence    : {final_output['final']['evidence_state']}",
        f"Action      : {final_output['final']['action']}",
        f"Lifecycle   : {final_output['final']['lifecycle']}",
        "",
        "=" * 70,
        f"OVERALL STATUS: {overall}",
        "=" * 70,
        "",
        "[INTEGRITY]",
        f"Model retraining       : NO",
        f"Model modification     : NO",
        f"Threshold optimization : NO",
        f"Locked test reuse      : NO",
        f"Prediction modification: NO",
        f"Synthetic feedback     : NO",
    ]

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("\n" + "=" * 70)
    print("        IT TICKET INTELLIGENCE & TRIAGE SYSTEM")
    print("=" * 70)

    print("\nFINAL TRIAGE OUTPUT")
    print("-" * 70)
    print(f"Category    : {final_output['final']['category']}")
    print(f"Priority    : {final_output['final']['priority']}")
    print(f"Severity    : {final_output['final']['severity']}")
    print(f"Duplicate   : {final_output['final']['duplicate']}")
    print(f"Related     : {final_output['final']['related']}")
    print(f"Resolution  : {final_output['final']['resolution_seconds']}")
    print(f"Evidence    : {final_output['final']['evidence_state']}")
    print(f"Action      : {final_output['final']['action']}")
    print(f"Lifecycle   : {final_output['final']['lifecycle']}")

    print("\n" + "=" * 70)
    print(f"OVERALL STATUS: {overall}")
    print("=" * 70)

    print("\n[ARTIFACTS]")
    print(f"JSON   : {json_path}")
    print(f"REPORT : {report_path}")

    print("\n[INTEGRITY]")
    print("Model retraining       : NO")
    print("Model modification     : NO")
    print("Threshold optimization : NO")
    print("Locked test reuse      : NO")
    print("Prediction modification: NO")
    print("Synthetic feedback     : NO")


if __name__ == "__main__":
    main()