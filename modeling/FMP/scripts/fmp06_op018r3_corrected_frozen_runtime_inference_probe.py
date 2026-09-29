from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OUTPUT = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "fmp06_op018r3_corrected_frozen_runtime_inference_probe.json"
)

PROBE_ROWS = 3


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def load_csv(
    candidates: list[Path],
) -> tuple[Path, pd.DataFrame]:

    for path in candidates:
        if path.exists():
            df = pd.read_csv(path)

            if df.empty:
                continue

            return path, df

    raise FileNotFoundError(
        "No usable runtime input source found."
    )


def text_from_row(
    row: pd.Series,
) -> str:

    summary = ""

    for column in (
        "summary",
        "Summary",
        "title",
    ):
        if column in row.index:
            value = row[column]

            if pd.notna(value):
                summary = str(value).strip()

                if summary:
                    break

    description = ""

    for column in (
        "description",
        "Description",
        "description_clean",
    ):
        if column in row.index:
            value = row[column]

            if pd.notna(value):
                description = str(value).strip()

                if description:
                    break

    text = (
        f"{summary}\n{description}"
    ).strip()

    if not text:
        raise ValueError(
            "Encountered an empty runtime ticket representation."
        )

    return text


def probe_t1() -> dict[str, Any]:

    artifact = (
        PROJECT_ROOT
        / "modeling/T1/baselines/"
        "t1_it_support_char_svm.joblib"
    )

    input_path, df = load_csv(
        [
            PROJECT_ROOT
            / "modeling/T1/derived/t1_dataset.csv",
            PROJECT_ROOT
            / "modeling/T1/derived/t1_vscode_dataset.csv",
        ]
    )

    bundle = joblib.load(artifact)

    features = bundle["features"]
    model = bundle["model"]

    texts = [
        text_from_row(row)
        for _, row in df.head(PROBE_ROWS).iterrows()
    ]

    X = features.transform(texts)

    predictions = model.predict(X)

    return {
        "status": "PASS",
        "artifact": rel(artifact),
        "input_source": rel(input_path),
        "input_count": len(texts),
        "feature_type": (
            f"{type(features).__module__}."
            f"{type(features).__name__}"
        ),
        "model_type": (
            f"{type(model).__module__}."
            f"{type(model).__name__}"
        ),
        "output_count": len(predictions),
        "output_preview": [
            str(value)
            for value in predictions
        ],
    }


def probe_t2() -> dict[str, Any]:

    artifact = (
        PROJECT_ROOT
        / "modeling/T2/models/"
        "t2_class_weighted_tfidf_logreg.joblib"
    )

    input_path, df = load_csv(
        [
            PROJECT_ROOT
            / "modeling/T2/derived/t2_features.csv",
        ]
    )

    bundle = joblib.load(artifact)

    vectorizer = bundle["vectorizer"]
    model = bundle["model"]

    texts = [
        text_from_row(row)
        for _, row in df.head(PROBE_ROWS).iterrows()
    ]

    X = vectorizer.transform(texts)

    predictions = model.predict(X)

    return {
        "status": "PASS",
        "artifact": rel(artifact),
        "input_source": rel(input_path),
        "input_count": len(texts),
        "vectorizer_type": (
            f"{type(vectorizer).__module__}."
            f"{type(vectorizer).__name__}"
        ),
        "model_type": (
            f"{type(model).__module__}."
            f"{type(model).__name__}"
        ),
        "output_count": len(predictions),
        "output_preview": [
            str(value)
            for value in predictions
        ],
    }


def probe_t3() -> dict[str, Any]:

    artifact = (
        PROJECT_ROOT
        / "modeling/T3/models/"
        "t3_class_weighted_tfidf_logreg.joblib"
    )

    input_path, df = load_csv(
        [
            PROJECT_ROOT
            / "modeling/T3/derived/t3_features.csv",
        ]
    )

    bundle = joblib.load(artifact)

    vectorizer = bundle["vectorizer"]
    model = bundle["model"]

    texts = [
        text_from_row(row)
        for _, row in df.head(PROBE_ROWS).iterrows()
    ]

    X = vectorizer.transform(texts)

    predictions = model.predict(X)

    return {
        "status": "PASS",
        "artifact": rel(artifact),
        "input_source": rel(input_path),
        "input_count": len(texts),
        "vectorizer_type": (
            f"{type(vectorizer).__module__}."
            f"{type(vectorizer).__name__}"
        ),
        "model_type": (
            f"{type(model).__module__}."
            f"{type(model).__name__}"
        ),
        "output_count": len(predictions),
        "output_preview": [
            str(value)
            for value in predictions
        ],
    }


def probe_t5() -> dict[str, Any]:

    vectorizer_path = (
        PROJECT_ROOT
        / "modeling/T5/models/"
        "t5_mod005_tfidf.joblib"
    )

    classifier_path = (
        PROJECT_ROOT
        / "modeling/T5/models/"
        "t5_mod005_logreg.joblib"
    )

    calibration_path = (
        PROJECT_ROOT
        / "modeling/T5/models/"
        "t5_mod007_calibration_models.joblib"
    )

    input_path, df = load_csv(
        [
            PROJECT_ROOT
            / "modeling/T5/derived/t5_train_features.csv",
            PROJECT_ROOT
            / "modeling/T5/splits/t5_model_train.csv",
        ]
    )

    if len(df) < 2:
        raise ValueError(
            "T5 requires at least two existing tickets."
        )

    vectorizer = joblib.load(
        vectorizer_path
    )

    classifier = joblib.load(
        classifier_path
    )

    calibration_bundle = joblib.load(
        calibration_path
    )

    sigmoid = calibration_bundle[
        "sigmoid_calibrator"
    ]

    texts = [
        text_from_row(row)
        for _, row in df.head(
            max(PROBE_ROWS, 3)
        ).iterrows()
    ]

    pairs = []

    for index in range(
        min(PROBE_ROWS, len(texts))
    ):

        first = texts[index]
        second = texts[
            (index + 1) % len(texts)
        ]

        pairs.append(
            first
            + " [SEP] "
            + second
        )

    X = vectorizer.transform(pairs)

    decision_scores = (
        classifier.decision_function(X)
    )

    decision_matrix = decision_scores.reshape(
        -1,
        1,
    )

    calibrated_probability = sigmoid.predict(
        decision_matrix
    )

    return {
        "status": "PASS",
        "vectorizer_artifact": rel(
            vectorizer_path
        ),
        "classifier_artifact": rel(
            classifier_path
        ),
        "calibration_artifact": rel(
            calibration_path
        ),
        "input_source": rel(input_path),
        "input_count": len(pairs),
        "decision_score_shape": list(
            decision_scores.shape
        ),
        "calibrator_input_shape": list(
            decision_matrix.shape
        ),
        "output_count": len(
            calibrated_probability
        ),
        "calibrated_probability_preview": [
            float(value)
            for value
            in calibrated_probability
        ],
        "threshold_applied": False,
        "threshold_selection": False,
    }


def not_executed(
    task: str,
    reason: str,
) -> dict[str, Any]:

    return {
        "status": "NOT_EXECUTED_BY_THIS_PROBE",
        "task": task,
        "reason": reason,
    }


def main() -> None:

    print("=" * 72)
    print(
        "FMP-06 OP-018R3 — "
        "CORRECTED FROZEN RUNTIME INFERENCE PROBE"
    )
    print("=" * 72)
    print()
    print("Frozen artifacts: YES")
    print("Inference: YES")
    print("Retraining: NO")
    print("Calibration fitting: NO")
    print("Threshold selection: NO")
    print("Artifact modification: NO")
    print()

    report: dict[str, Any] = {
        "operation": "FMP-06 OP-018R3",
        "operation_type": (
            "CORRECTED_CONTROLLED_FROZEN_RUNTIME_INFERENCE_PROBE"
        ),
        "probe_rows": PROBE_ROWS,
        "tasks": {},
        "safeguards": {
            "inference_executed": True,
            "retraining": False,
            "artifact_modification": False,
            "calibration_fitting": False,
            "threshold_selection": False,
            "threshold_applied": False,
            "synthetic_target_created": False,
            "locked_test_used_for_selection": False,
            "universal_confidence_created": False,
            "universal_risk_created": False,
        },
    }

    probes = {
        "T1": probe_t1,
        "T2": probe_t2,
        "T3": probe_t3,
        "T5": probe_t5,
    }

    for task, function in probes.items():

        print("-" * 72)
        print(task)

        try:

            result = function()

        except Exception as exc:

            result = {
                "status": "FAIL",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }

        report["tasks"][task] = result

        print(
            "  status:",
            result["status"],
        )

        if result["status"] == "PASS":

            if "artifact" in result:
                print(
                    "  artifact:",
                    result["artifact"],
                )

            if "input_source" in result:
                print(
                    "  input:",
                    result["input_source"],
                )

            print(
                "  output_count:",
                result["output_count"],
            )

            if "output_preview" in result:
                print(
                    "  output_preview:",
                    result["output_preview"],
                )

            if (
                "calibrated_probability_preview"
                in result
            ):
                print(
                    "  calibrated probabilities:",
                    result[
                        "calibrated_probability_preview"
                    ],
                )

        else:

            print(
                "  ERROR:",
                result.get("error"),
            )

    report["tasks"]["T4"] = not_executed(
        "T4",
        (
            "Historical assignee candidate-ranking runtime "
            "requires an explicit frozen candidate-population "
            "binding; no new population is invented here."
        ),
    )

    report["tasks"]["T6"] = not_executed(
        "T6",
        (
            "Hybrid lexical-semantic retrieval requires an "
            "explicit frozen retrieval corpus binding."
        ),
    )

    report["tasks"]["T7"] = not_executed(
        "T7",
        (
            "Native survival inference requires a frozen "
            "runtime feature binding preserving event and "
            "censoring semantics."
        ),
    )

    executed_statuses = [
        report["tasks"][task]["status"]
        for task in (
            "T1",
            "T2",
            "T3",
            "T5",
        )
    ]

    if all(
        status == "PASS"
        for status in executed_statuses
    ):
        report["overall_status"] = "PASS"
    else:
        report["overall_status"] = "FAIL"

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            report,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 72)
    print(
        "OVERALL STATUS:",
        report["overall_status"],
    )
    print(
        "OUTPUT:",
        OUTPUT,
    )
    print("=" * 72)


if __name__ == "__main__":
    main()