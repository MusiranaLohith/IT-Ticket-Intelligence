from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T4_TRAIN = (
    ROOT / "modeling/T4/derived/t4_train.csv"
)

TFIDF_PATH = (
    ROOT
    / "modeling/T4/results/mod007_checkpoints/t4_mod007_tfidf.joblib"
)

NN_PATH = (
    ROOT
    / "modeling/T4/results/mod007_checkpoints/t4_mod007_neighbors.joblib"
)

RETRIEVAL_PATH = (
    ROOT
    / "modeling/T4/results/mod007_checkpoints/"
    / "t4_mod007_full_retrieval.npz"
)

OUTPUT = (
    ROOT
    / "modeling/FMP/metrics/"
    / "fmp06_op018r15_t4_frozen_retrieval_reproducibility.json"
)


def build_text(df: pd.DataFrame) -> pd.Series:
    """
    Native T4 text construction recovered from
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


def normalize_array_shape(arr):
    return tuple(int(x) for x in arr.shape)


def main():

    print("=" * 72)
    print("FMP-06 OP-018R15 — T4 FROZEN RETRIEVAL REPRODUCIBILITY")
    print("=" * 72)

    print()
    print("Read-only: YES")
    print("Frozen TF-IDF: YES")
    print("Frozen NearestNeighbors: YES")
    print("Stored retrieval artifact: YES")
    print("Training/fitting: NO")
    print("Evaluation metrics: NO")
    print("Locked test population: NO")
    print("Artifact modification: NO")
    print()

    # ------------------------------------------------------------
    # 1. Verify required artifacts
    # ------------------------------------------------------------

    print("[1] Checking required files...")

    required = {
        "t4_train": T4_TRAIN,
        "tfidf": TFIDF_PATH,
        "nearest_neighbors": NN_PATH,
        "stored_retrieval": RETRIEVAL_PATH,
    }

    for name, path in required.items():

        exists = path.exists()

        print(
            f"{name}: "
            f"{'PRESENT' if exists else 'MISSING'}"
        )

        if not exists:
            raise FileNotFoundError(
                f"Required artifact missing: {path}"
            )

    # ------------------------------------------------------------
    # 2. Load frozen components
    # ------------------------------------------------------------

    print()
    print("[2] Loading frozen T4 components...")

    vectorizer = joblib.load(TFIDF_PATH)
    neighbors = joblib.load(NN_PATH)

    print(
        f"TF-IDF type: {type(vectorizer).__name__}"
    )

    print(
        f"NearestNeighbors type: {type(neighbors).__name__}"
    )

    params = neighbors.get_params()

    print(
        f"metric: {params.get('metric')}"
    )

    print(
        f"algorithm: {params.get('algorithm')}"
    )

    print(
        f"n_neighbors: {params.get('n_neighbors')}"
    )

    if params.get("metric") != "cosine":
        raise RuntimeError(
            "Frozen NearestNeighbors metric is not cosine."
        )

    # ------------------------------------------------------------
    # 3. Load native T4 training population
    # ------------------------------------------------------------

    print()
    print("[3] Loading native T4 training population...")

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
            "T4 training schema does not match frozen schema."
        )

    # ------------------------------------------------------------
    # 4. Load stored retrieval artifact
    # ------------------------------------------------------------

    print()
    print("[4] Loading stored T4 MOD-007 retrieval artifact...")

    stored = np.load(
        RETRIEVAL_PATH,
        allow_pickle=False,
    )

    print(
        "Stored arrays:"
    )

    for key in stored.files:
        arr = stored[key]

        print(
            f"  - {key}: "
            f"shape={arr.shape}, "
            f"dtype={arr.dtype}"
        )

    # ------------------------------------------------------------
    # 5. Identify retrieval arrays
    # ------------------------------------------------------------

    print()
    print("[5] Identifying stored neighbor/distance arrays...")

    candidate_index_keys = []
    candidate_distance_keys = []

    for key in stored.files:

        key_lower = key.lower()

        if (
            "neighbor" in key_lower
            or "index" in key_lower
            or key_lower == "indices"
        ):
            candidate_index_keys.append(key)

        if (
            "distance" in key_lower
            or "similar" in key_lower
            or key_lower == "distances"
        ):
            candidate_distance_keys.append(key)

    print(
        f"Candidate index arrays: {candidate_index_keys}"
    )

    print(
        f"Candidate distance/similarity arrays: "
        f"{candidate_distance_keys}"
    )

    if not candidate_index_keys:
        raise RuntimeError(
            "Could not identify stored neighbor-index array."
        )

    if not candidate_distance_keys:
        raise RuntimeError(
            "Could not identify stored distance/similarity array."
        )

    # Prefer exact conventional names where available.
    index_key = (
        "indices"
        if "indices" in stored.files
        else candidate_index_keys[0]
    )

    if "distances" in stored.files:
        distance_key = "distances"
    elif "similarities" in stored.files:
        distance_key = "similarities"
    else:
        distance_key = candidate_distance_keys[0]

    stored_indices = stored[index_key]
    stored_values = stored[distance_key]

    print(
        f"Selected index array: {index_key}"
    )

    print(
        f"Selected distance/similarity array: "
        f"{distance_key}"
    )

    print(
        f"Stored index shape: "
        f"{stored_indices.shape}"
    )

    print(
        f"Stored value shape: "
        f"{stored_values.shape}"
    )

    # ------------------------------------------------------------
    # 6. Determine safe probe rows
    # ------------------------------------------------------------

    print()
    print("[6] Selecting reproducibility probe rows...")

    probe_count = min(
        3,
        len(train),
        stored_indices.shape[0],
    )

    if probe_count < 1:
        raise RuntimeError(
            "No usable probe rows available."
        )

    probe = train.iloc[:probe_count].copy()

    print(
        f"Probe rows: {probe_count}"
    )

    print(
        "Probe IDs:"
    )

    for ticket_id in probe["ID"].tolist():
        print(f"  - {ticket_id}")

    # ------------------------------------------------------------
    # 7. Native text transformation
    # ------------------------------------------------------------

    print()
    print("[7] Transforming probe using frozen TF-IDF...")

    probe_text = build_text(probe)

    transformed = vectorizer.transform(
        probe_text
    )

    print(
        f"Transformed shape: {transformed.shape}"
    )

    # ------------------------------------------------------------
    # 8. Frozen retrieval
    # ------------------------------------------------------------

    print()
    print("[8] Executing frozen NearestNeighbors...")

    reproduced_distances, reproduced_indices = (
        neighbors.kneighbors(
            transformed,
            return_distance=True,
        )
    )

    print(
        f"Reproduced index shape: "
        f"{reproduced_indices.shape}"
    )

    print(
        f"Reproduced distance shape: "
        f"{reproduced_distances.shape}"
    )

    # ------------------------------------------------------------
    # 9. Compare shapes
    # ------------------------------------------------------------

    print()
    print("[9] Comparing stored and reproduced retrieval...")

    stored_index_probe = stored_indices[:probe_count]

    stored_value_probe = stored_values[:probe_count]

    index_shape_match = (
        stored_index_probe.shape
        == reproduced_indices.shape
    )

    value_shape_match = (
        stored_value_probe.shape
        == reproduced_distances.shape
    )

    print(
        f"Index shape match: {index_shape_match}"
    )

    print(
        f"Distance/value shape match: {value_shape_match}"
    )

    if not index_shape_match:
        raise RuntimeError(
            "Stored and reproduced neighbor-index shapes differ."
        )

    if not value_shape_match:
        raise RuntimeError(
            "Stored and reproduced distance/value shapes differ."
        )

    # ------------------------------------------------------------
    # 10. Compare neighbor indices
    # ------------------------------------------------------------

    index_equal = np.array_equal(
        stored_index_probe,
        reproduced_indices,
    )

    print(
        f"Neighbor indices exact match: {index_equal}"
    )

    # ------------------------------------------------------------
    # 11. Compare numerical values
    # ------------------------------------------------------------

    # Stored artifact may contain either distances or similarities.
    # First test direct distance equality.
    direct_distance_match = np.allclose(
        stored_value_probe,
        reproduced_distances,
        rtol=1e-6,
        atol=1e-7,
    )

    similarity_match = np.allclose(
        stored_value_probe,
        1.0 - reproduced_distances,
        rtol=1e-6,
        atol=1e-7,
    )

    print(
        f"Stored values match reproduced distances: "
        f"{direct_distance_match}"
    )

    print(
        f"Stored values match reproduced cosine similarities: "
        f"{similarity_match}"
    )

    # ------------------------------------------------------------
    # 12. Show first-row comparison
    # ------------------------------------------------------------

    print()
    print("[12] First probe-row comparison...")

    first_n = min(
        5,
        reproduced_indices.shape[1],
    )

    print()
    print("Stored neighbor indices:")
    print(
        stored_index_probe[0][:first_n].tolist()
    )

    print("Reproduced neighbor indices:")
    print(
        reproduced_indices[0][:first_n].tolist()
    )

    print()
    print("Stored values:")
    print(
        stored_value_probe[0][:first_n].tolist()
    )

    print("Reproduced distances:")
    print(
        reproduced_distances[0][:first_n].tolist()
    )

    print("Reproduced similarities:")
    print(
        (1.0 - reproduced_distances[0][:first_n]).tolist()
    )

    # ------------------------------------------------------------
    # 13. Determine result
    # ------------------------------------------------------------

    exact_reproduction = (
        index_equal
        and (
            direct_distance_match
            or similarity_match
        )
    )

    if exact_reproduction:
        status = "PASS"
        finding = (
            "Frozen T4 TF-IDF and NearestNeighbors reproduce "
            "the stored MOD-007 retrieval artifact for the "
            "probe rows."
        )
    else:
        status = "REPRODUCIBILITY_MISMATCH"
        finding = (
            "Frozen T4 runtime executes, but stored MOD-007 "
            "retrieval values and/or neighbor indices do not "
            "exactly reproduce for the probe rows."
        )

    # ------------------------------------------------------------
    # 14. Write report
    # ------------------------------------------------------------

    report = {
        "operation": "FMP-06 OP-018R15",
        "operation_name": (
            "T4 frozen retrieval reproducibility check"
        ),
        "status": status,
        "finding": finding,
        "read_only": True,
        "training_or_fitting": False,
        "evaluation_metrics": False,
        "locked_test_used": False,
        "artifact_modified": False,
        "probe_rows": probe_count,
        "frozen_metric": params.get("metric"),
        "frozen_algorithm": params.get("algorithm"),
        "frozen_n_neighbors": params.get("n_neighbors"),
        "stored_index_key": index_key,
        "stored_value_key": distance_key,
        "stored_index_shape": list(
            stored_indices.shape
        ),
        "stored_value_shape": list(
            stored_values.shape
        ),
        "reproduced_index_shape": list(
            reproduced_indices.shape
        ),
        "reproduced_distance_shape": list(
            reproduced_distances.shape
        ),
        "index_exact_match": bool(
            index_equal
        ),
        "stored_value_matches_distance": bool(
            direct_distance_match
        ),
        "stored_value_matches_similarity": bool(
            similarity_match
        ),
        "exact_reproduction": bool(
            exact_reproduction
        ),
        "output": str(OUTPUT),
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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
    print("OP-018R15 COMPLETE")
    print("=" * 72)
    print(f"Status: {status}")
    print(f"Output: {OUTPUT}")
    print()
    print("Training/fitting: NO")
    print("Evaluation metrics: NO")
    print("Locked test population: NO")
    print("Artifact modification: NO")
    print("=" * 72)


if __name__ == "__main__":
    main()