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


class TicketPipeline:
    """
    Ticket-facing runtime for the frozen T1-T7 modeling package
    followed by T8-T11 evidence/policy/lifecycle handling.

    Public interface:

        pipeline.predict(ticket)
        pipeline.predict_batch(tickets)

    The frozen modeling artifacts are read-only.
    """

    def __init__(self):
        self._load_t1()
        self._load_t2()
        self._load_t3()
        self._load_t4()
        self._load_t5()
        self._load_t7()

    # ==============================================================
    # GENERAL UTILITIES
    # ==============================================================

    @staticmethod
    def _extract_model_and_vectorizer(bundle):
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
                if hasattr(value, "predict") or hasattr(
                    value, "decision_function"
                ):
                    model = value
                    break

        if vectorizer is None:
            for value in bundle.values():
                if hasattr(value, "transform") and not hasattr(
                    value, "predict"
                ):
                    vectorizer = value
                    break

        if vectorizer is None or model is None:
            raise RuntimeError(
                "Could not resolve frozen vectorizer/model bundle."
            )

        return vectorizer, model

    @staticmethod
    def _load_classifier(path: Path):
        if not path.exists():
            raise FileNotFoundError(str(path))

        bundle = joblib.load(path)

        return TicketPipeline._extract_model_and_vectorizer(bundle)

    @staticmethod
    def _require_ticket_field(ticket, field):
        if field not in ticket:
            raise ValueError(
                f"Missing required ticket field: {field}"
            )

    @staticmethod
    def _normalise_ticket(ticket):
        if not isinstance(ticket, dict):
            raise TypeError("Ticket must be a dictionary.")

        required = [
            "ticket_id",
            "creation_time",
            "creator",
            "creator_detail",
            "summary",
            "description",
        ]

        for field in required:
            TicketPipeline._require_ticket_field(ticket, field)

        normalised = dict(ticket)

        for field in [
            "ticket_id",
            "creator",
            "creator_detail",
            "summary",
            "description",
        ]:
            value = normalised[field]

            if value is None:
                normalised[field] = ""
            else:
                normalised[field] = str(value)

        if normalised["creation_time"] is None:
            raise ValueError("creation_time cannot be None.")

        normalised["creation_time"] = str(
            normalised["creation_time"]
        )

        return normalised

    @staticmethod
    def _ticket_text(ticket):
        return (
            f"{ticket['summary']}\n"
            f"{ticket['description']}"
        ).strip()

    # ==============================================================
    # FROZEN T1
    # ==============================================================

    def _load_t1(self):
        path = (
            MODELING
            / "T1"
            / "baselines"
            / "t1_it_support_char_svm.joblib"
        )

        self.t1_vectorizer, self.t1_model = self._load_classifier(path)
        self.t1_artifact = str(path)

    def _run_t1(self, ticket):
        text = self._ticket_text(ticket)

        X = self.t1_vectorizer.transform([text])

        prediction = self.t1_model.predict(X)[0]

        return {
            "status": "EXECUTED",
            "prediction": str(prediction),
            "transformed_shape": list(X.shape),
            "artifact": self.t1_artifact,
        }

    # ==============================================================
    # FROZEN T2
    # ==============================================================

    def _load_t2(self):
        path = (
            MODELING
            / "T2"
            / "models"
            / "t2_class_weighted_tfidf_logreg.joblib"
        )

        self.t2_vectorizer, self.t2_model = self._load_classifier(path)
        self.t2_artifact = str(path)

    def _run_t2(self, ticket):
        text = self._ticket_text(ticket)

        X = self.t2_vectorizer.transform([text])

        prediction = self.t2_model.predict(X)[0]

        return {
            "status": "EXECUTED",
            "prediction": str(prediction),
            "transformed_shape": list(X.shape),
            "artifact": self.t2_artifact,
        }

    # ==============================================================
    # FROZEN T3
    # ==============================================================

    def _load_t3(self):
        path = (
            MODELING
            / "T3"
            / "models"
            / "t3_class_weighted_tfidf_logreg.joblib"
        )

        self.t3_vectorizer, self.t3_model = self._load_classifier(path)
        self.t3_artifact = str(path)

    def _run_t3(self, ticket):
        text = self._ticket_text(ticket)

        X = self.t3_vectorizer.transform([text])

        prediction = self.t3_model.predict(X)[0]

        return {
            "status": "EXECUTED",
            "prediction": str(prediction),
            "transformed_shape": list(X.shape),
            "artifact": self.t3_artifact,
        }

    # ==============================================================
    # FROZEN T4
    # ==============================================================

    def _load_t4(self):
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

        train_path = (
            MODELING
            / "T4"
            / "derived"
            / "t4_train.csv"
        )

        self.t4_vectorizer = joblib.load(tfidf_path)
        self.t4_neighbors = joblib.load(neighbors_path)
        self.t4_train = pd.read_csv(train_path)

        self.t4_artifacts = {
            "tfidf": str(tfidf_path),
            "neighbors": str(neighbors_path),
            "population": str(train_path),
        }

    def _run_t4(self, ticket):
        text = self._ticket_text(ticket)

        X = self.t4_vectorizer.transform([text])

        distances, indices = self.t4_neighbors.kneighbors(
            X,
            n_neighbors=5,
        )

        results = []

        for distance, index in zip(
            distances[0],
            indices[0],
        ):
            row = self.t4_train.iloc[int(index)]

            results.append(
                {
                    "id": str(row["ID"]),
                    "distance": float(distance),
                    "summary": str(row["Summary"]),
                    "target_assignee": str(
                        row["target_assignee"]
                    ),
                }
            )

        return {
            "status": "EXECUTED",
            "results": results,
            "artifacts": self.t4_artifacts,
        }

    # ==============================================================
    # FROZEN T5
    # ==============================================================

    def _load_t5(self):
        root = MODELING / "T5"

        tfidf_path = next(
            root.rglob("t5_mod005_tfidf.joblib"),
            None,
        )

        logreg_path = next(
            root.rglob("t5_mod005_logreg.joblib"),
            None,
        )

        calibrated_vectorizer_path = next(
            root.rglob("t5_mod007_calibrated_tfidf.joblib"),
            None,
        )

        calibration_models_path = next(
            root.rglob("t5_mod007_calibration_models.joblib"),
            None,
        )

        paths = [
            tfidf_path,
            logreg_path,
            calibrated_vectorizer_path,
            calibration_models_path,
        ]

        if any(path is None for path in paths):
            raise FileNotFoundError(
                "One or more frozen T5 artifacts could not be found."
            )

        self.t5_classifier = joblib.load(logreg_path)
        self.t5_vectorizer = joblib.load(
            calibrated_vectorizer_path
        )
        self.t5_calibration_models = joblib.load(
            calibration_models_path
        )

        self.t5_artifacts = {
            "tfidf": str(tfidf_path),
            "classifier": str(logreg_path),
            "calibrated_vectorizer": str(
                calibrated_vectorizer_path
            ),
            "calibration_models": str(
                calibration_models_path
            ),
        }

    def _run_t5(self, ticket):
        text = self._ticket_text(ticket)

        # Self-pairing is retained from the validated runtime probe.
        pair_text = f"{text} [SEP] {text}"

        X = self.t5_vectorizer.transform([pair_text])

        decision = self.t5_classifier.decision_function(X)

        decision_2d = np.asarray(
            decision,
            dtype=float,
        ).reshape(-1, 1)

        calibrator = self.t5_calibration_models[
            "sigmoid_calibrator"
        ]

        calibrated = calibrator.predict(decision_2d)

        evidence = float(
            np.asarray(calibrated).reshape(-1)[0]
        )

        return {
            "status": "EXECUTED",
            "duplicate_evidence": evidence,
            "threshold_used": False,
            "decision_score": float(
                np.asarray(decision).reshape(-1)[0]
            ),
            "artifacts": self.t5_artifacts,
        }

    # ==============================================================
    # FROZEN T6 — NEW-TICKET BOUNDARY
    # ==============================================================

    def _run_t6(self, ticket):
        return {
            "status": "PARTIAL_NATIVE_RUNTIME",
            "full_mod010_hybrid_available": False,
            "top_ids": [],
            "reason": (
                "The frozen MOD-010 semantic component depends "
                "on stored semantic evidence for the existing "
                "evaluation population. A genuinely new ticket "
                "does not have a corresponding stored semantic "
                "evidence row. No semantic score is fabricated."
            ),
        }

    # ==============================================================
    # FROZEN T7
    # ==============================================================

    @staticmethod
    def _text_features(text):
        text = "" if text is None else str(text)

        return (
            len(text),
            len(text.split()),
            sum(c.isdigit() for c in text),
            text.count("\n"),
            sum(c.isupper() for c in text),
            1.0 if not text else 0.0,
        )

    def _load_t7(self):
        model_path = (
            MODELING
            / "T7"
            / "metrics"
            / "t7_mod010_log_normal_aft_model.json"
        )

        train_path = (
            MODELING
            / "T7"
            / "splits"
            / "t7_train.csv"
        )

        with open(
            model_path,
            "r",
            encoding="utf-8",
        ) as f:
            self.t7_model = json.load(f)

        train = pd.read_csv(train_path)

        self.t7_creator_counts = (
            train["Creator"]
            .fillna("")
            .astype(str)
            .str.strip()
            .value_counts()
            .to_dict()
        )

        self.t7_detail_counts = (
            train["Creator Detail"]
            .fillna("")
            .astype(str)
            .str.strip()
            .value_counts()
            .to_dict()
        )

        self.t7_artifacts = {
            "model": str(model_path),
            "train_population": str(train_path),
        }

        self.t7_training_year_min = int(
            pd.to_datetime(
                train["Creation time"]
            ).dt.year.min()
        )

        self.t7_training_year_max = int(
            pd.to_datetime(
                train["Creation time"]
            ).dt.year.max()
        )

    def _run_t7(self, ticket):
        dt = pd.Timestamp(
            ticket["creation_time"]
        ).to_pydatetime()

        summary = self._text_features(
            ticket["summary"]
        )

        description = self._text_features(
            ticket["description"]
        )

        month = (
            2.0
            * math.pi
            * (dt.month - 1)
            / 12.0
        )

        weekday = (
            2.0
            * math.pi
            * dt.weekday()
            / 7.0
        )

        hour = (
            2.0
            * math.pi
            * dt.hour
            / 24.0
        )

        raw_features = [
            math.log1p(
                self.t7_creator_counts.get(
                    ticket["creator"].strip(),
                    0,
                )
            ),
            math.log1p(
                self.t7_detail_counts.get(
                    ticket["creator_detail"].strip(),
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

            (dt.year - 2010.0) / 10.0,

            math.sin(month),
            math.cos(month),

            math.sin(weekday),
            math.cos(weekday),

            math.sin(hour),
            math.cos(hour),
        ]

        feature_names = self.t7_model[
            "feature_names"
        ]

        beta_source = self.t7_model["beta"]

        if isinstance(beta_source, dict):
            beta = np.asarray(
                [
                    float(beta_source[name])
                    for name in feature_names
                ]
            )
        else:
            beta = np.asarray(
                beta_source,
                dtype=float,
            ).reshape(-1)

        mean_source = self.t7_model[
            "standardization_mean"
        ]

        if isinstance(mean_source, dict):
            mean = np.asarray(
                [
                    float(mean_source[name])
                    for name in feature_names
                ]
            )
        else:
            mean = np.asarray(
                mean_source,
                dtype=float,
            ).reshape(-1)

        std_source = self.t7_model[
            "standardization_std"
        ]

        if isinstance(std_source, dict):
            std = np.asarray(
                [
                    float(std_source[name])
                    for name in feature_names
                ]
            )
        else:
            std = np.asarray(
                std_source,
                dtype=float,
            ).reshape(-1)

        raw = np.asarray(
            raw_features,
            dtype=float,
        )

        if len(raw) != len(feature_names):
            raise RuntimeError(
                "T7 feature count does not match model."
            )

        if np.any(std == 0):
            raise RuntimeError(
                "T7 contains zero standard deviation."
            )

        standardized = (raw - mean) / std

        linear_predictor = float(
            np.dot(
                standardized,
                beta,
            )
        )

        median_seconds = float(
            np.exp(linear_predictor)
        )

        temporal_supported = (
            self.t7_training_year_min
            <= dt.year
            <= self.t7_training_year_max
        )

        return {
            "status": (
                "EXECUTED"
                if temporal_supported
                else "EXECUTED_WITH_SUPPORT_LIMITATION"
            ),
            "median_seconds": median_seconds,
            "creation_year": dt.year,
            "training_year_min": (
                self.t7_training_year_min
            ),
            "training_year_max": (
                self.t7_training_year_max
            ),
            "temporal_support": (
                "WITHIN_OBSERVED_TRAINING_RANGE"
                if temporal_supported
                else "OUTSIDE_OBSERVED_TRAINING_RANGE"
            ),
            "linear_predictor": linear_predictor,
            "feature_count": len(feature_names),
            "artifacts": self.t7_artifacts,
        }

    # ==============================================================
    # T8
    # ==============================================================

    @staticmethod
    def _run_t8(results):
        available = []
        partial = []
        unavailable = []

        for task in [
            "T1",
            "T2",
            "T3",
            "T4",
            "T5",
            "T6",
            "T7",
        ]:
            status = results[task]["status"]

            if status == "EXECUTED":
                available.append(task)
            elif (
                status.startswith("PARTIAL")
                or status.endswith("LIMITATION")
            ):
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

    # ==============================================================
    # T9
    # ==============================================================

    @staticmethod
    def _run_t9():
        return {
            "status": "EXECUTED",
            "universal_confidence": None,
            "universal_risk": None,
            "cross_task_probability_aggregation": False,
            "reason": (
                "Task outputs retain native semantics. "
                "No universal confidence or risk score is created."
            ),
        }

    # ==============================================================
    # T10
    # ==============================================================

    @staticmethod
    def _run_t10(results):
        warnings = []

        if (
            results["T8"]["evidence_state"]
            != "SUPPORTED"
        ):
            warnings.append(
                "Evidence is not fully supported; "
                "missing evidence is not negative evidence."
            )

        if (
            results["T6"]["status"]
            == "PARTIAL_NATIVE_RUNTIME"
        ):
            warnings.append(
                "T6 full MOD-010 hybrid is unavailable "
                "for this new-ticket runtime."
            )

        if (
            results["T7"].get("temporal_support")
            == "OUTSIDE_OBSERVED_TRAINING_RANGE"
        ):
            warnings.append(
                "T7 ticket creation year is outside "
                "observed training temporal range."
            )

        return {
            "status": "EXECUTED",
            "action": "HUMAN_DECISION_REQUIRED",
            "automation": "NOT_ESTABLISHED",
            "warnings": warnings,
        }

    # ==============================================================
    # T11
    # ==============================================================

    @staticmethod
    def _run_t11():
        return {
            "status": "EXECUTED",
            "feedback": "AWAITING_OUTCOME",
            "synthetic_feedback": False,
        }

    # ==============================================================
    # PUBLIC SINGLE-TICKET API
    # ==============================================================

    def predict(self, ticket: dict[str, Any]):
        """
        Execute one ticket through T1-T11.
        """

        ticket = self._normalise_ticket(ticket)

        results = {}

        results["T1"] = self._run_t1(ticket)
        results["T2"] = self._run_t2(ticket)
        results["T3"] = self._run_t3(ticket)
        results["T4"] = self._run_t4(ticket)
        results["T5"] = self._run_t5(ticket)
        results["T6"] = self._run_t6(ticket)
        results["T7"] = self._run_t7(ticket)

        results["T8"] = self._run_t8(results)
        results["T9"] = self._run_t9()
        results["T10"] = self._run_t10(results)
        results["T11"] = self._run_t11()

        return {
            "ticket": ticket,
            "tasks": results,
            "final": {
                "category": results["T1"].get(
                    "prediction"
                ),
                "priority": results["T2"].get(
                    "prediction"
                ),
                "severity": results["T3"].get(
                    "prediction"
                ),
                "duplicate_evidence": results["T5"].get(
                    "duplicate_evidence"
                ),
                "related_ticket_ids": results["T6"].get(
                    "top_ids",
                    [],
                ),
                "resolution_median_seconds": results[
                    "T7"
                ].get("median_seconds"),
                "evidence_state": results["T8"][
                    "evidence_state"
                ],
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
        }

    # ==============================================================
    # PUBLIC BATCH API
    # ==============================================================

    def predict_batch(
        self,
        tickets: list[dict[str, Any]],
    ):
        """
        Execute the same runtime independently for N tickets.

        Each ticket gets an independent T1-T11 result.
        """

        if not isinstance(tickets, list):
            raise TypeError(
                "predict_batch() expects a list of tickets."
            )

        results = []

        for ticket in tickets:
            results.append(
                self.predict(ticket)
            )

        return results