from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

TRAIN_SOURCE = (
    PROJECT_ROOT
    / "modeling/T4/derived/t4_train.csv"
)

TFIDF_ARTIFACT = (
    PROJECT_ROOT
    / "modeling/T4/results/mod007_checkpoints/"
    "t4_mod007_tfidf.joblib"
)

NEIGHBOR_ARTIFACT = (
    PROJECT_ROOT
    / "modeling/T4/results/mod007_checkpoints/"
    "t4_mod007_neighbors.joblib"
)

OUTPUT = (
    PROJECT_ROOT
    / "modeling/FMP/metrics/"
    "fmp06_op018r12_t4_frozen_runtime_smoke.json"
)

PROBE_ROWS = 3


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def build_text(row: pd.Series) -> str:
    parts = []

    for column in [
        "summary",
        "description_clean",
        "description",
        "text",
    ]:
        if column in row.index:
            value = row[column]

            if pd.notna(value):
                text = str(value).strip()

                if text:
                    parts.append(text)

    if not parts:
        raise ValueError(
            "No usable text fields found for T4 probe row."
        )

    return " ".join(parts)


def rank_assignees(
    neighbor_indices: np.ndarray,
    similarities: np.ndarray,
    train_targets: np.ndarray,
) -> list[dict]:

    scores = {}

    for index, similarity in zip(
        neighbor_indices,
        similarities,
    ):
        target = str(train_targets[index])

        if target not in scores:
            scores[target] = {
                "score": 0.0,
                "neighbor_count": 0,
            }

        scores[target]["score"] += float(similarity)
        scores[target]["neighbor_count"] += 1

    ranked = sorted(
        scores.items(),
        key=lambda item: (
            -item[1]["score"],
            -item[1]["neighbor_count"],
            item[0],
        ),
    )

    return [
        {
            "assignee": assignee,
            "score": values["score"],
            "neighbor_count": values["neighbor_count"],
        }
        for assignee, values in ranked
    ]


def main() -> None:

    print("=" * 72)
    print(
        "FMP-06 OP-018R12 — "
        "T4 FROZEN RUNTIME SMOKE"
    )
    print("=" * 72)
    print()

    print("Frozen TF-IDF: YES")
    print("Frozen NearestNeighbors: YES")
    print("Training/fitting: NO")
    print("Evaluation metrics: NO")
    print("Locked test population: NO")
    print("Threshold selection: NO")
    print()

    for path in [
        TRAIN_SOURCE,
        TFIDF_ARTIFACT,
        NEIGHBOR_ARTIFACT,
    ]:
        if not path.exists():
            raise FileNotFoundError(path)

    df = pd.read_csv(TRAIN_SOURCE)

    if df.empty:
        raise ValueError(
            "T4 training source is empty."
        )

    if "target_assignee" not in df.columns:
        raise KeyError(
            "T4 training source does not contain "
            "'target_assignee'."
        )

    probe = df.head(PROBE_ROWS).copy()

    texts = [
        build_text(row)
        for _, row in probe.iterrows()
    ]

    train_targets = (
        df["target_assignee"]
        .astype(str)
        .to_numpy()
    )

    print(
        "TRAIN SOURCE:",
        rel(TRAIN_SOURCE),
    )

    print(
        "TRAIN ROWS:",
        len(df),
    )

    print(
        "PROBE ROWS:",
        len(probe),
    )

    print()

    tfidf = joblib.load(TFIDF_ARTIFACT)
    neighbors = joblib.load(NEIGHBOR_ARTIFACT)

    print(
        "TF-IDF TYPE:",
        f"{type(tfidf).__module__}."
        f"{type(tfidf).__name__}",
    )

    print(
        "NEIGHBOR TYPE:",
        f"{type(neighbors).__module__}."
        f"{type(neighbors).__name__}",
    )

    # ------------------------------------------------------------
    # Frozen inference only.
    # ------------------------------------------------------------

    X_probe = tfidf.transform(texts)

    print(
        "TRANSFORMED SHAPE:",
        list(X_probe.shape),
    )

    distances, indices = neighbors.kneighbors(
        X_probe,
        return_distance=True,
    )

    print(
        "NEIGHBOR SHAPE:",
        list(indices.shape),
    )

    results = []

    for row_position in range(PROBE_ROWS):

        ranked = rank_assignees(
            indices[row_position],
            1.0 - distances[row_position],
            train_targets,
        )

        results.append(
            {
                "probe_row_position": row_position,
                "top_candidates": ranked[:5],
            }
        )

    print()

    for item in results:
        print(
            "PROBE ROW:",
            item["probe_row_position"],
        )

        for candidate in item["top_candidates"]:
            print(
                "  ",
                candidate,
            )

    output = {
        "operation": "FMP-06 OP-018R12",
        "operation_type": (
            "T4_FROZEN_RUNTIME_SMOKE"
        ),
        "status": "PASS",
        "train_source": rel(TRAIN_SOURCE),
        "train_rows": int(len(df)),
        "probe_rows": int(PROBE_ROWS),
        "tfidf_artifact": rel(TFIDF_ARTIFACT),
        "neighbor_artifact": rel(NEIGHBOR_ARTIFACT),
        "tfidf_type": (
            f"{type(tfidf).__module__}."
            f"{type(tfidf).__name__}"
        ),
        "neighbor_type": (
            f"{type(neighbors).__module__}."
            f"{type(neighbors).__name__}"
        ),
        "transformed_shape": list(X_probe.shape),
        "neighbor_shape": list(indices.shape),
        "probe_results": results,
        "safeguards": {
            "fit_called": False,
            "fit_transform_called": False,
            "retraining": False,
            "locked_test_used": False,
            "evaluation_metrics_calculated": False,
            "threshold_selection": False,
            "artifact_modification": False,
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
            output,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 72)
    print("STATUS: PASS")
    print("T4 FROZEN RUNTIME SMOKE: SUCCESS")
    print("OUTPUT:", OUTPUT)
    print("=" * 72)


if __name__ == "__main__":
    main()