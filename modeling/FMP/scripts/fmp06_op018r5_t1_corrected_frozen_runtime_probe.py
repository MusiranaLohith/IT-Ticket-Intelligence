from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

ARTIFACT = (
    PROJECT_ROOT
    / "modeling/T1/baselines/"
    "t1_it_support_char_svm.joblib"
)

INPUT_SOURCE = (
    PROJECT_ROOT
    / "modeling/T1/derived/"
    "t1_dataset.csv"
)

OUTPUT = (
    PROJECT_ROOT
    / "modeling/FMP/metrics/"
    "fmp06_op018r5_t1_corrected_frozen_runtime_probe.json"
)

PROBE_ROWS = 3


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def main() -> None:

    print("=" * 72)
    print(
        "FMP-06 OP-018R5 — "
        "T1 CORRECTED FROZEN RUNTIME PROBE"
    )
    print("=" * 72)
    print()

    print("Frozen artifact: YES")
    print("Existing input source: YES")
    print("Inference: YES")
    print("Retraining: NO")
    print("Feature fitting: NO")
    print("Threshold selection: NO")
    print("Artifact modification: NO")
    print()

    if not ARTIFACT.exists():
        raise FileNotFoundError(
            f"Frozen T1 artifact missing: {ARTIFACT}"
        )

    if not INPUT_SOURCE.exists():
        raise FileNotFoundError(
            f"T1 input source missing: {INPUT_SOURCE}"
        )

    df = pd.read_csv(INPUT_SOURCE)

    if "text" not in df.columns:
        raise KeyError(
            "Authoritative T1 input source does not "
            "contain the required 'text' column."
        )

    if df.empty:
        raise ValueError(
            "T1 input source is empty."
        )

    probe_df = df.head(PROBE_ROWS).copy()

    if probe_df["text"].isna().any():
        raise ValueError(
            "Selected T1 probe rows contain null text."
        )

    texts = [
        str(value)
        for value in probe_df["text"].tolist()
    ]

    if any(not text.strip() for text in texts):
        raise ValueError(
            "Selected T1 probe rows contain empty text."
        )

    print(
        "INPUT:",
        rel(INPUT_SOURCE),
    )

    print(
        "ROWS AVAILABLE:",
        len(df),
    )

    print(
        "PROBE ROWS:",
        len(texts),
    )

    print(
        "TEXT FIELD:",
        "text",
    )

    print()

    # Load the already-frozen bundle.
    bundle = joblib.load(ARTIFACT)

    if not isinstance(bundle, dict):
        raise TypeError(
            "Frozen T1 artifact is not the expected dict bundle."
        )

    if "features" not in bundle:
        raise KeyError(
            "Frozen T1 bundle does not contain 'features'."
        )

    if "model" not in bundle:
        raise KeyError(
            "Frozen T1 bundle does not contain 'model'."
        )

    features = bundle["features"]
    model = bundle["model"]

    print(
        "FEATURE TYPE:",
        f"{type(features).__module__}."
        f"{type(features).__name__}",
    )

    print(
        "MODEL TYPE:",
        f"{type(model).__module__}."
        f"{type(model).__name__}",
    )

    print()

    # IMPORTANT:
    # transform() is inference-time use of the already-fitted
    # FeatureUnion. No fit() or fit_transform() is called.
    X = features.transform(texts)

    print(
        "TRANSFORMED SHAPE:",
        list(X.shape),
    )

    predictions = model.predict(X)

    print(
        "PREDICTION COUNT:",
        len(predictions),
    )

    print(
        "PREDICTIONS:",
        [
            str(value)
            for value in predictions
        ],
    )

    result = {
        "operation": "FMP-06 OP-018R5",
        "operation_type": (
            "T1_CORRECTED_FROZEN_RUNTIME_INFERENCE_PROBE"
        ),
        "status": "PASS",
        "artifact": rel(ARTIFACT),
        "input_source": rel(INPUT_SOURCE),
        "input_field": "text",
        "input_available_rows": int(len(df)),
        "probe_rows": int(len(texts)),
        "feature_type": (
            f"{type(features).__module__}."
            f"{type(features).__name__}"
        ),
        "model_type": (
            f"{type(model).__module__}."
            f"{type(model).__name__}"
        ),
        "transformed_shape": list(X.shape),
        "prediction_count": int(len(predictions)),
        "prediction_preview": [
            str(value)
            for value in predictions
        ],
        "safeguards": {
            "inference_executed": True,
            "fit_called": False,
            "fit_transform_called": False,
            "retraining": False,
            "artifact_modification": False,
            "threshold_selection": False,
            "calibration_fitting": False,
            "synthetic_input_created": False,
            "synthetic_target_created": False,
        },
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