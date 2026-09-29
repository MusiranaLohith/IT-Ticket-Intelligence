from pathlib import Path
import json

import joblib
import pandas as pd


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T4_TRAIN = ROOT / "modeling/T4/derived/t4_train.csv"

TFIDF_PATH = (
    ROOT
    / "modeling/T4/results/mod007_checkpoints/t4_mod007_tfidf.joblib"
)

NN_PATH = (
    ROOT
    / "modeling/T4/results/mod007_checkpoints/t4_mod007_neighbors.joblib"
)

OUTPUT = (
    ROOT
    / "modeling/FMP/metrics/"
    / "fmp06_op018r14_t4_corrected_frozen_runtime_smoke.json"
)


def build_text(df: pd.DataFrame) -> pd.Series:
    """
    Exact native T4 build_text logic recovered from
    modeling/T4/scripts/t4_ranking_baseline.py.
    """
    columns = [
        "Creator",
        "Creator Detail",
        "Summary",
        "Description",
    ]

    text = df[columns[0]].fillna("").astype(str)

    for column in columns[1:]:
        text = text + " " + df[column].fillna("").astype(str)

    return text.str.strip()


def rank_assignees(
    neighbor_indices,
    neighbor_similarities,
    train_targets,
):
    """
    Exact native T4 ranking aggregation logic recovered from
    t4_ranking_baseline.py.
    """
    scores = {}

    for idx, similarity in zip(
        neighbor_indices,
        neighbor_similarities,
    ):
        assignee = train_targets[idx]

        scores[assignee] = (
            scores.get(assignee, 0.0)
            + float(similarity)
        )

    ranked = sorted(
        scores.items(),
        key=lambda item: (-item[1], item[0]),
    )

    return ranked


def main():

    print("=" * 72)
    print("FMP-06 OP-018R14 — T4 CORRECTED FROZEN RUNTIME SMOKE")
    print("=" * 72)

    print()
    print("Native T4 text construction: YES")
    print("Frozen TF-IDF: YES")
    print("Frozen NearestNeighbors: YES")
    print("Training/fitting: NO")
    print("Evaluation metrics: NO")
    print("Locked test population: NO")
    print("Threshold selection: NO")
    print()

    # ------------------------------------------------------------
    # 1. Load frozen artifacts
    # ------------------------------------------------------------

    print("[1] Loading frozen T4 artifacts...")

    if not TFIDF_PATH.exists():
        raise FileNotFoundError(
            f"Missing frozen TF-IDF: {TFIDF_PATH}"
        )

    if not NN_PATH.exists():
        raise FileNotFoundError(
            f"Missing frozen NearestNeighbors: {NN_PATH}"
        )

    vectorizer = joblib.load(TFIDF_PATH)
    neighbors = joblib.load(NN_PATH)

    print(f"TF-IDF: {type(vectorizer).__name__}")
    print(f"NearestNeighbors: {type(neighbors).__name__}")

    # ------------------------------------------------------------
    # 2. Load native T4 training population
    # ------------------------------------------------------------

    print()
    print("[2] Loading T4 native training population...")

    if not T4_TRAIN.exists():
        raise FileNotFoundError(
            f"Missing T4 training source: {T4_TRAIN}"
        )

    train = pd.read_csv(T4_TRAIN)

    print(f"Rows: {len(train)}")
    print(f"Columns: {list(train.columns)}")

    expected_columns = {
        "ID",
        "Creation time",
        "Creator",
        "Creator Detail",
        "Summary",
        "Description",
        "target_assignee",
    }

    if set(train.columns) != expected_columns:
        raise RuntimeError(
            "T4 training schema does not match the frozen native schema."
        )

    if train["target_assignee"].isna().any():
        raise RuntimeError(
            "Blank target_assignee detected in T4 training population."
        )

    # ------------------------------------------------------------
    # 3. Construct native T4 text
    # ------------------------------------------------------------

    print()
    print("[3] Constructing native T4 text representation...")

    train_text = build_text(train)

    print(f"Constructed text rows: {len(train_text)}")

    if train_text.isna().any():
        raise RuntimeError(
            "Native T4 text construction produced missing values."
        )

    nonempty_count = int(
        (train_text.str.len() > 0).sum()
    )

    print(f"Non-empty text rows: {nonempty_count}")

    # ------------------------------------------------------------
    # 4. Tiny frozen inference probe
    # ------------------------------------------------------------

    print()
    print("[4] Running 3-row frozen runtime probe...")

    probe = train.iloc[:3].copy()
    probe_text = build_text(probe)

    print("Probe IDs:")
    for value in probe["ID"].tolist():
        print(f"  - {value}")

    transformed = vectorizer.transform(probe_text)

    print()
    print(f"Transformed shape: {transformed.shape}")

    # ------------------------------------------------------------
    # 5. Inspect frozen NN metric
    # ------------------------------------------------------------

    print()
    print("[5] Inspecting frozen NearestNeighbors configuration...")

    nn_params = neighbors.get_params()

    print(f"metric: {nn_params.get('metric')}")
    print(f"algorithm: {nn_params.get('algorithm')}")
    print(f"n_neighbors: {nn_params.get('n_neighbors')}")

    # The frozen T4 implementation describes the retrieval evidence
    # as cosine similarity. For sklearn NearestNeighbors using cosine
    # distance, similarity = 1 - distance.

    if nn_params.get("metric") != "cosine":
        raise RuntimeError(
            "Frozen T4 NearestNeighbors metric is not cosine; "
            "do not infer cosine similarity."
        )

    # ------------------------------------------------------------
    # 6. Frozen neighbor retrieval
    # ------------------------------------------------------------

    print()
    print("[6] Executing frozen NearestNeighbors retrieval...")

    distances, indices = neighbors.kneighbors(
        transformed,
        return_distance=True,
    )

    similarities = 1.0 - distances

    train_targets = train["target_assignee"].to_numpy()

    results = []

    for row_idx in range(len(probe)):

        ranked = rank_assignees(
            indices[row_idx],
            similarities[row_idx],
            train_targets,
        )

        top5 = [
            {
                "assignee": str(assignee),
                "aggregated_similarity": float(score),
            }
            for assignee, score in ranked[:5]
        ]

        print()
        print(f"Probe row {row_idx + 1}")
        print(f"ID: {probe.iloc[row_idx]['ID']}")
        print(f"Top-5 candidate assignees:")

        for item in top5:
            print(
                f"  {item['assignee']} "
                f"(score={item['aggregated_similarity']:.8f})"
            )

        results.append(
            {
                "probe_row": row_idx,
                "ticket_id": str(probe.iloc[row_idx]["ID"]),
                "top5": top5,
            }
        )

    # ------------------------------------------------------------
    # 7. Write audit output
    # ------------------------------------------------------------

    report = {
        "operation": "FMP-06 OP-018R14",
        "operation_name": "T4 corrected frozen runtime smoke",
        "status": "PASS",
        "native_text_contract": {
            "columns": [
                "Creator",
                "Creator Detail",
                "Summary",
                "Description",
            ],
            "construction": (
                "Creator + Creator Detail + Summary + Description"
            ),
            "strip": True,
        },
        "frozen_artifacts": {
            "tfidf": str(TFIDF_PATH),
            "nearest_neighbors": str(NN_PATH),
        },
        "training_or_fitting": False,
        "evaluation": False,
        "locked_test_used": False,
        "threshold_selection": False,
        "training_rows_loaded": int(len(train)),
        "probe_rows": int(len(probe)),
        "transformed_shape": [
            int(transformed.shape[0]),
            int(transformed.shape[1]),
        ],
        "nearest_neighbors_metric": nn_params.get("metric"),
        "nearest_neighbors_algorithm": nn_params.get("algorithm"),
        "nearest_neighbors_n_neighbors": nn_params.get(
            "n_neighbors"
        ),
        "results": results,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 72)
    print("OP-018R14 COMPLETE")
    print("=" * 72)
    print(f"Output: {OUTPUT}")
    print()
    print("Training/fitting: NO")
    print("Evaluation: NO")
    print("Locked test population: NO")
    print("Threshold selection: NO")
    print("Artifact modification: NO")
    print("=" * 72)


if __name__ == "__main__":
    main()