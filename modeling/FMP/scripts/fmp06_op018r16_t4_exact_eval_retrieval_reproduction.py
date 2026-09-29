from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T4_EVAL = (
    ROOT / "modeling/T4/derived/t4_eval.csv"
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
    / "fmp06_op018r16_t4_exact_eval_retrieval_reproduction.json"
)


def build_text(df: pd.DataFrame) -> pd.Series:
    """
    Exact native T4 text construction.
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


def main():

    print("=" * 72)
    print("FMP-06 OP-018R16 — T4 EXACT EVALUATION RETRIEVAL REPRODUCTION")
    print("=" * 72)

    print()
    print("Read-only: YES")
    print("Frozen TF-IDF: YES")
    print("Frozen NearestNeighbors: YES")
    print("Training/fitting: NO")
    print("Evaluation metric calculation: NO")
    print("Locked test population: NO")
    print("Artifact modification: NO")
    print()

    # ------------------------------------------------------------
    # 1. Verify files
    # ------------------------------------------------------------

    print("[1] Checking required files...")

    required = {
        "t4_eval": T4_EVAL,
        "tfidf": TFIDF_PATH,
        "nearest_neighbors": NN_PATH,
        "stored_retrieval": RETRIEVAL_PATH,
    }

    for name, path in required.items():

        if not path.exists():
            raise FileNotFoundError(
                f"{name} missing: {path}"
            )

        print(f"{name}: PRESENT")

    # ------------------------------------------------------------
    # 2. Load evaluation population
    # ------------------------------------------------------------

    print()
    print("[2] Loading T4 evaluation population...")

    evaluation = pd.read_csv(T4_EVAL)

    print(f"Rows: {len(evaluation)}")
    print(
        f"Columns: {list(evaluation.columns)}"
    )

    expected_columns = {
        "ID",
        "Creation time",
        "Creator",
        "Creator Detail",
        "Summary",
        "Description",
        "target_assignee",
    }

    if set(evaluation.columns) != expected_columns:
        raise RuntimeError(
            "T4 evaluation schema does not match "
            "the native T4 schema."
        )

    # ------------------------------------------------------------
    # 3. Load frozen components
    # ------------------------------------------------------------

    print()
    print("[3] Loading frozen T4 components...")

    vectorizer = joblib.load(TFIDF_PATH)
    neighbors = joblib.load(NN_PATH)

    params = neighbors.get_params()

    print(
        f"TF-IDF: {type(vectorizer).__name__}"
    )

    print(
        f"NearestNeighbors: {type(neighbors).__name__}"
    )

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
            "Frozen T4 NearestNeighbors metric is not cosine."
        )

    # ------------------------------------------------------------
    # 4. Load stored retrieval artifact
    # ------------------------------------------------------------

    print()
    print("[4] Loading stored MOD-007 retrieval artifact...")

    stored = np.load(
        RETRIEVAL_PATH,
        allow_pickle=False,
    )

    print("Stored arrays:")

    for key in stored.files:
        print(
            f"  - {key}: "
            f"shape={stored[key].shape}, "
            f"dtype={stored[key].dtype}"
        )

    if "neighbor_indices" not in stored.files:
        raise RuntimeError(
            "neighbor_indices not found."
        )

    if "neighbor_similarities" not in stored.files:
        raise RuntimeError(
            "neighbor_similarities not found."
        )

    stored_indices = stored[
        "neighbor_indices"
    ]

    stored_similarities = stored[
        "neighbor_similarities"
    ]

    # ------------------------------------------------------------
    # 5. Population alignment check
    # ------------------------------------------------------------

    print()
    print("[5] Checking evaluation/retrieval population alignment...")

    print(
        f"T4 evaluation rows: {len(evaluation)}"
    )

    print(
        f"Stored retrieval rows: "
        f"{stored_indices.shape[0]}"
    )

    if len(evaluation) != stored_indices.shape[0]:
        raise RuntimeError(
            "T4 evaluation population size does not "
            "match stored retrieval population size."
        )

    if stored_indices.shape[1] != 20:
        raise RuntimeError(
            "Stored retrieval does not contain 20 neighbors."
        )

    print("Population alignment: EXACT")

    # ------------------------------------------------------------
    # 6. Probe first three ACTUAL evaluation rows
    # ------------------------------------------------------------

    print()
    print("[6] Selecting first three evaluation rows...")

    probe_count = 3

    probe = evaluation.iloc[
        :probe_count
    ].copy()

    print("Evaluation probe IDs:")

    for ticket_id in probe["ID"].tolist():
        print(f"  - {ticket_id}")

    # ------------------------------------------------------------
    # 7. Native T4 text construction
    # ------------------------------------------------------------

    print()
    print("[7] Constructing native T4 evaluation text...")

    probe_text = build_text(probe)

    for i, text in enumerate(probe_text):
        print(
            f"Row {i}: text_length={len(text)}"
        )

    # ------------------------------------------------------------
    # 8. Frozen TF-IDF transformation
    # ------------------------------------------------------------

    print()
    print("[8] Transforming evaluation probe with frozen TF-IDF...")

    transformed = vectorizer.transform(
        probe_text
    )

    print(
        f"Transformed shape: {transformed.shape}"
    )

    # ------------------------------------------------------------
    # 9. Frozen nearest-neighbor retrieval
    # ------------------------------------------------------------

    print()
    print("[9] Executing frozen NearestNeighbors...")

    reproduced_distances, reproduced_indices = (
        neighbors.kneighbors(
            transformed,
            return_distance=True,
        )
    )

    reproduced_similarities = (
        1.0 - reproduced_distances
    )

    print(
        f"Reproduced index shape: "
        f"{reproduced_indices.shape}"
    )

    print(
        f"Reproduced similarity shape: "
        f"{reproduced_similarities.shape}"
    )

    # ------------------------------------------------------------
    # 10. Compare exact neighbor indices
    # ------------------------------------------------------------

    print()
    print("[10] Comparing neighbor indices...")

    stored_probe_indices = stored_indices[
        :probe_count
    ]

    stored_probe_similarities = (
        stored_similarities[
            :probe_count
        ]
    )

    index_exact = np.array_equal(
        stored_probe_indices,
        reproduced_indices,
    )

    print(
        f"Exact neighbor-index match: "
        f"{index_exact}"
    )

    # ------------------------------------------------------------
    # 11. Compare similarity values
    # ------------------------------------------------------------

    print()
    print("[11] Comparing stored cosine similarities...")

    similarity_exact = np.allclose(
        stored_probe_similarities,
        reproduced_similarities,
        rtol=1e-5,
        atol=1e-6,
    )

    print(
        f"Cosine similarity match: "
        f"{similarity_exact}"
    )

    max_abs_difference = float(
        np.max(
            np.abs(
                stored_probe_similarities
                - reproduced_similarities
            )
        )
    )

    print(
        f"Maximum absolute similarity difference: "
        f"{max_abs_difference:.12g}"
    )

    # ------------------------------------------------------------
    # 12. Print first-row comparison
    # ------------------------------------------------------------

    print()
    print("[12] First evaluation-row comparison...")

    print()
    print(
        f"Evaluation ID: "
        f"{probe.iloc[0]['ID']}"
    )

    print()
    print("Stored neighbor indices:")
    print(
        stored_probe_indices[0].tolist()
    )

    print()
    print("Reproduced neighbor indices:")
    print(
        reproduced_indices[0].tolist()
    )

    print()
    print("Stored similarities:")
    print(
        stored_probe_similarities[0].tolist()
    )

    print()
    print("Reproduced similarities:")
    print(
        reproduced_similarities[0].tolist()
    )

    # ------------------------------------------------------------
    # 13. Final status
    # ------------------------------------------------------------

    exact_reproduction = (
        index_exact
        and similarity_exact
    )

    if exact_reproduction:
        status = "PASS"
        finding = (
            "Frozen T4 TF-IDF and NearestNeighbors reproduce "
            "the stored MOD-007 retrieval artifact for the "
            "same evaluation rows."
        )
    else:
        status = "REPRODUCIBILITY_MISMATCH"
        finding = (
            "Frozen T4 runtime executes on the correct "
            "evaluation population, but stored MOD-007 "
            "retrieval indices and/or similarities do not "
            "match the reproduced values."
        )

    # ------------------------------------------------------------
    # 14. Write report
    # ------------------------------------------------------------

    report = {
        "operation": "FMP-06 OP-018R16",
        "operation_name": (
            "T4 exact evaluation retrieval reproduction"
        ),
        "status": status,
        "finding": finding,
        "read_only": True,
        "training_or_fitting": False,
        "evaluation_metric_calculation": False,
        "locked_test_used": False,
        "artifact_modified": False,
        "evaluation_rows": int(len(evaluation)),
        "stored_retrieval_rows": int(
            stored_indices.shape[0]
        ),
        "population_alignment": True,
        "probe_rows": probe_count,
        "probe_ids": [
            str(x)
            for x in probe["ID"].tolist()
        ],
        "frozen_metric": params.get("metric"),
        "frozen_algorithm": params.get("algorithm"),
        "frozen_n_neighbors": params.get(
            "n_neighbors"
        ),
        "index_exact_match": bool(
            index_exact
        ),
        "similarity_match": bool(
            similarity_exact
        ),
        "max_abs_similarity_difference": (
            max_abs_difference
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
    print("OP-018R16 COMPLETE")
    print("=" * 72)
    print(f"Status: {status}")
    print(f"Output: {OUTPUT}")
    print()
    print("Training/fitting: NO")
    print("Evaluation metric calculation: NO")
    print("Locked test population: NO")
    print("Artifact modification: NO")
    print("=" * 72)


if __name__ == "__main__":
    main()