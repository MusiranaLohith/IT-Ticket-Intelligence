from __future__ import annotations

import json
import sys
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
    / "fmp06_op018_controlled_frozen_runtime_inference_probe.json"
)


PROBE_ROWS = 3


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"Required file not found: {path}"
        )


def find_first_existing(
    candidates: list[Path],
) -> Path | None:

    for path in candidates:
        if path.exists():
            return path

    return None


def load_table(
    candidates: list[Path],
) -> tuple[Path | None, pd.DataFrame | None]:

    path = find_first_existing(candidates)

    if path is None:
        return None, None

    return path, pd.read_csv(path)


def text_from_row(
    row: pd.Series,
    summary_candidates: list[str],
    description_candidates: list[str],
) -> str:

    summary = ""

    for column in summary_candidates:
        if column in row.index:
            value = row[column]

            if pd.notna(value):
                summary = str(value).strip()
                if summary:
                    break

    description = ""

    for column in description_candidates:
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
        text = "runtime probe ticket text"

    return text


def probe_t1() -> dict[str, Any]:

    task = "T1"

    artifact = (
        PROJECT_ROOT
        / "modeling/T1/baselines/"
        "t1_it_support_char_svm.joblib"
    )

    data_candidates = [
        PROJECT_ROOT / "modeling/T1/derived/t1_dataset.csv",
        PROJECT_ROOT / "modeling/T1/derived/t1_vscode_dataset.csv",
    ]

    require_file(artifact)

    data_path, df = load_table(data_candidates)

    if df is None or df.empty:
        raise RuntimeError(
            "T1 probe data unavailable."
        )

    texts = []

    for _, row in df.head(PROBE_ROWS).iterrows():
        texts.append(
            text_from_row(
                row,
                ["summary", "Summary", "title"],
                [
                    "description",
                    "Description",
                    "description_clean",
                ],
            )
        )

    model = joblib.load(artifact)

    predictions = model.predict(texts)

    return {
        "task": task,
        "status": "PASS",
        "artifact": rel(artifact),
        "input_source": rel(data_path),
        "input_count": len(texts),
        "output_type": type(predictions).__name__,
        "output_count": len(predictions),
        "output_preview": [
            str(value)
            for value in predictions[:PROBE_ROWS]
        ],
    }


def probe_t2() -> dict[str, Any]:

    task = "T2"

    artifact = (
        PROJECT_ROOT
        / "modeling/T2/models/"
        "t2_class_weighted_tfidf_logreg.joblib"
    )

    data_candidates = [
        PROJECT_ROOT / "modeling/T2/derived/t2_features.csv",
    ]

    require_file(artifact)

    data_path, df = load_table(data_candidates)

    if df is None or df.empty:
        raise RuntimeError(
            "T2 probe data unavailable."
        )

    texts = []

    for _, row in df.head(PROBE_ROWS).iterrows():
        texts.append(
            text_from_row(
                row,
                ["Summary", "summary"],
                ["Description", "description"],
            )
        )

    model = joblib.load(artifact)

    predictions = model.predict(texts)

    return {
        "task": task,
        "status": "PASS",
        "artifact": rel(artifact),
        "input_source": rel(data_path),
        "input_count": len(texts),
        "output_type": type(predictions).__name__,
        "output_count": len(predictions),
        "output_preview": [
            str(value)
            for value in predictions[:PROBE_ROWS]
        ],
    }


def probe_t3() -> dict[str, Any]:

    task = "T3"

    artifact = (
        PROJECT_ROOT
        / "modeling/T3/models/"
        "t3_class_weighted_tfidf_logreg.joblib"
    )

    data_candidates = [
        PROJECT_ROOT / "modeling/T3/derived/t3_features.csv",
    ]

    require_file(artifact)

    data_path, df = load_table(data_candidates)

    if df is None or df.empty:
        raise RuntimeError(
            "T3 probe data unavailable."
        )

    texts = []

    for _, row in df.head(PROBE_ROWS).iterrows():
        texts.append(
            text_from_row(
                row,
                ["Summary", "summary"],
                ["Description", "description"],
            )
        )

    model = joblib.load(artifact)

    predictions = model.predict(texts)

    return {
        "task": task,
        "status": "PASS",
        "artifact": rel(artifact),
        "input_source": rel(data_path),
        "input_count": len(texts),
        "output_type": type(predictions).__name__,
        "output_count": len(predictions),
        "output_preview": [
            str(value)
            for value in predictions[:PROBE_ROWS]
        ],
    }


def probe_t4() -> dict[str, Any]:

    task = "T4"

    closure = (
        PROJECT_ROOT
        / "modeling/T4/results/"
        "t4_mod013_closure.json"
    )

    implementation = (
        PROJECT_ROOT
        / "modeling/T4/scripts/t4_mod013.py"
    )

    require_file(closure)
    require_file(implementation)

    return {
        "task": task,
        "status": "NOT_EXECUTED_BY_THIS_PROBE",
        "reason": (
            "T4 is a native historical candidate-ranking "
            "task rather than a single frozen joblib inference "
            "interface. This probe does not invent a new "
            "candidate-population runtime."
        ),
        "closure": rel(closure),
        "implementation": rel(implementation),
    }


def probe_t5() -> dict[str, Any]:

    task = "T5"

    vectorizer_artifact = (
        PROJECT_ROOT
        / "modeling/T5/models/"
        "t5_mod005_tfidf.joblib"
    )

    classifier_artifact = (
        PROJECT_ROOT
        / "modeling/T5/models/"
        "t5_mod005_logreg.joblib"
    )

    calibration_artifact = (
        PROJECT_ROOT
        / "modeling/T5/models/"
        "t5_mod007_calibration_models.joblib"
    )

    data_candidates = [
        PROJECT_ROOT
        / "modeling/T5/derived/t5_train_features.csv",
        PROJECT_ROOT
        / "modeling/T5/splits/t5_model_train.csv",
    ]

    for artifact in (
        vectorizer_artifact,
        classifier_artifact,
        calibration_artifact,
    ):
        require_file(artifact)

    data_path, df = load_table(data_candidates)

    if df is None or df.empty:
        raise RuntimeError(
            "T5 probe data unavailable."
        )

    vectorizer = joblib.load(
        vectorizer_artifact
    )

    classifier = joblib.load(
        classifier_artifact
    )

    calibration_models = joblib.load(
        calibration_artifact
    )

    if not isinstance(calibration_models, dict):
        raise RuntimeError(
            "T5 calibration artifact is not the "
            "expected mapping structure."
        )

    if "sigmoid_calibrator" not in calibration_models:
        raise RuntimeError(
            "T5 sigmoid calibrator missing."
        )

    calibrator = calibration_models[
        "sigmoid_calibrator"
    ]

    texts = []

    for _, row in df.head(PROBE_ROWS).iterrows():

        text = text_from_row(
            row,
            ["Summary", "summary"],
            ["Description", "description"],
        )

        texts.append(text)

    # Construct a genuine pair from two existing rows.
    # No synthetic ticket is created.
    if len(texts) < 2:
        raise RuntimeError(
            "T5 requires at least two existing tickets."
        )

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

    decision_scores = classifier.decision_function(X)

    probabilities = calibrator.predict(
        decision_scores
    )

    return {
        "task": task,
        "status": "PASS",
        "vectorizer_artifact": rel(
            vectorizer_artifact
        ),
        "classifier_artifact": rel(
            classifier_artifact
        ),
        "calibration_artifact": rel(
            calibration_artifact
        ),
        "input_source": rel(data_path),
        "input_count": len(pairs),
        "output_type": type(probabilities).__name__,
        "output_count": len(probabilities),
        "output_preview": [
            float(value)
            for value in probabilities[:PROBE_ROWS]
        ],
        "threshold_used": False,
    }


def probe_t6() -> dict[str, Any]:

    task = "T6"

    closure = (
        PROJECT_ROOT
        / "modeling/T6/metrics/"
        "t6_final_closure.json"
    )

    result_artifact = (
        PROJECT_ROOT
        / "modeling/T6/metrics/"
        "t6_mod010_corrected_hybrid_results.json"
    )

    require_file(closure)
    require_file(result_artifact)

    return {
        "task": task,
        "status": "NOT_EXECUTED_BY_THIS_PROBE",
        "reason": (
            "T6 requires a retrieval corpus and native "
            "hybrid lexical/semantic ranking execution. "
            "This probe does not invent a corpus binding "
            "or substitute an arbitrary ranking runtime."
        ),
        "closure": rel(closure),
        "result_artifact": rel(result_artifact),
    }


def probe_t7() -> dict[str, Any]:

    task = "T7"

    closure = (
        PROJECT_ROOT
        / "modeling/T7/metrics/"
        "t7_mod012_final_closure.json"
    )

    implementation = (
        PROJECT_ROOT
        / "modeling/T7/scripts/"
        "t7_mod010_log_normal_aft_baseline.py"
    )

    require_file(closure)
    require_file(implementation)

    return {
        "task": task,
        "status": "NOT_EXECUTED_BY_THIS_PROBE",
        "reason": (
            "T7 is a native survival-analysis task with "
            "event/censoring semantics. This probe does not "
            "construct a new survival runtime or relabel "
            "censored observations."
        ),
        "closure": rel(closure),
        "implementation": rel(implementation),
    }


def main() -> None:

    print("=" * 72)
    print(
        "FMP-06 OP-018 — "
        "CONTROLLED FROZEN RUNTIME INFERENCE PROBE"
    )
    print("=" * 72)
    print()
    print("READ-ONLY PROJECT STATE")
    print("Existing frozen artifacts may be loaded.")
    print("No retraining.")
    print("No artifact modification.")
    print("No calibration fitting.")
    print("No threshold selection.")
    print("No synthetic targets.")
    print()

    report: dict[str, Any] = {
        "operation": "FMP-06 OP-018",
        "operation_type": (
            "CONTROLLED_FROZEN_RUNTIME_INFERENCE_PROBE"
        ),
        "probe_rows": PROBE_ROWS,
        "tasks": {},
        "safeguards": {
            "retraining": False,
            "artifact_modification": False,
            "calibration_fitting": False,
            "threshold_selection": False,
            "synthetic_ticket_creation": False,
            "synthetic_target_creation": False,
            "locked_test_used_for_selection": False,
            "universal_confidence_created": False,
            "universal_risk_created": False,
        },
    }

    probes = {
        "T1": probe_t1,
        "T2": probe_t2,
        "T3": probe_t3,
        "T4": probe_t4,
        "T5": probe_t5,
        "T6": probe_t6,
        "T7": probe_t7,
    }

    for task, function in probes.items():

        print("-" * 72)
        print(task)

        try:
            result = function()

        except Exception as exc:

            result = {
                "task": task,
                "status": "FAIL",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }

        report["tasks"][task] = result

        print(
            "  status:",
            result["status"],
        )

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

        if "input_count" in result:
            print(
                "  input_count:",
                result["input_count"],
            )

        if "output_type" in result:
            print(
                "  output:",
                result["output_type"],
                "count=",
                result["output_count"],
            )

        if result["status"] == "FAIL":
            print(
                "  ERROR:",
                result["error"],
            )

        if (
            result["status"]
            == "NOT_EXECUTED_BY_THIS_PROBE"
        ):
            print(
                "  reason:",
                result["reason"],
            )

    statuses = [
        result["status"]
        for result in report["tasks"].values()
    ]

    if "FAIL" in statuses:
        report["overall_status"] = "FAIL"
    else:
        report["overall_status"] = "PASS"

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            report,
            indent=2,
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