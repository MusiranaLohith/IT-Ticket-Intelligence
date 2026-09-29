from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T4_DIR = ROOT / "modeling" / "T4"
FMP_DIR = ROOT / "modeling" / "FMP"
METRICS_DIR = FMP_DIR / "metrics"

TICKET_TITLE = "VPN connection fails after password reset"

TICKET_DESCRIPTION = (
    "I reset my corporate password this morning. Since then, the VPN client "
    "connects briefly and then disconnects. I restarted the laptop and "
    "reinstalled the VPN client, but the issue persists. I need access to "
    "the internal systems for today's work."
)

TICKET_TEXT = f"{TICKET_TITLE}\n{TICKET_DESCRIPTION}".strip()

TFIDF_PATH = (
    T4_DIR / "results" / "mod007_checkpoints" / "t4_mod007_tfidf.joblib"
)

NEIGHBORS_PATH = (
    T4_DIR / "results" / "mod007_checkpoints" / "t4_mod007_neighbors.joblib"
)

RETRIEVAL_PATH = (
    T4_DIR / "results" / "mod007_checkpoints" / "t4_mod007_full_retrieval.npz"
)

OUTPUT_PATH = METRICS_DIR / "h_run003_single_ticket_t4_neighbor_mapping.json"


def describe_path(path):
    return str(path)


def find_candidate_mapping_files():
    """
    Locate likely frozen/development-population files WITHOUT loading them.
    We are looking for files that can establish:

        neighbor index
            ->
        historical ticket row
            ->
        assignee

    This is discovery only. No model or dataset is modified.
    """

    candidate_dirs = [
        T4_DIR,
        T4_DIR / "results",
        T4_DIR / "results" / "mod007_checkpoints",
        T4_DIR / "data",
        T4_DIR / "derived",
        T4_DIR / "metrics",
        ROOT / "datasets",
        ROOT / "data",
    ]

    keywords = (
        "assignee",
        "assignment",
        "retrieval",
        "neighbor",
        "development",
        "train",
        "ticket",
        "mod007",
    )

    candidates = []

    for directory in candidate_dirs:
        if not directory.exists():
            continue

        for path in directory.rglob("*"):
            if not path.is_file():
                continue

            name = path.name.lower()

            if any(keyword in name for keyword in keywords):
                candidates.append(path)

    # Remove duplicates while preserving order.
    unique = []
    seen = set()

    for path in candidates:
        resolved = str(path.resolve())
        if resolved not in seen:
            seen.add(resolved)
            unique.append(path)

    return unique


def inspect_tabular_file(path):
    """
    Read only the schema/sample of likely tabular files.
    Does not alter the source.
    """

    suffix = path.suffix.lower()

    try:
        if suffix == ".csv":
            df = pd.read_csv(path, nrows=5)

        elif suffix == ".parquet":
            df = pd.read_parquet(path).head(5)

        elif suffix in {".json", ".jsonl"}:
            if suffix == ".jsonl":
                df = pd.read_json(path, lines=True).head(5)
            else:
                df = pd.read_json(path)

                if isinstance(df, pd.Series):
                    df = df.to_frame()

                df = df.head(5)

        else:
            return None

        return {
            "path": str(path),
            "suffix": suffix,
            "columns": [str(c) for c in df.columns],
            "sample_rows": int(len(df)),
        }

    except Exception as exc:
        return {
            "path": str(path),
            "suffix": suffix,
            "read_error": f"{type(exc).__name__}: {exc}",
        }


def main():
    print("=" * 72)
    print("H-RUN-003 — T4 NEIGHBOR → HISTORICAL MAPPING")
    print("=" * 72)

    print()
    print("TICKET:")
    print(TICKET_TEXT)

    print()
    print("FROZEN T4 ARTIFACTS:")
    print(f"TF-IDF:     {describe_path(TFIDF_PATH)}")
    print(f"NEIGHBORS:  {describe_path(NEIGHBORS_PATH)}")
    print(f"RETRIEVAL:  {describe_path(RETRIEVAL_PATH)}")

    # ------------------------------------------------------------
    # Load frozen retrieval artifacts.
    # ------------------------------------------------------------

    tfidf = joblib.load(TFIDF_PATH)
    neighbors = joblib.load(NEIGHBORS_PATH)
    retrieval = np.load(RETRIEVAL_PATH, allow_pickle=False)

    neighbor_indices = retrieval["neighbor_indices"]
    neighbor_similarities = retrieval["neighbor_similarities"]

    X = tfidf.transform([TICKET_TEXT])

    distances, indices = neighbors.kneighbors(
        X,
        n_neighbors=5,
        return_distance=True,
    )

    indices = indices[0].tolist()
    distances = distances[0].tolist()

    print()
    print("RUNTIME NEIGHBOR INDICES:")
    print(indices)

    print()
    print("RUNTIME DISTANCES:")
    print(distances)

    # ------------------------------------------------------------
    # Locate possible historical mapping artifacts.
    # ------------------------------------------------------------

    print()
    print("SEARCHING FOR HISTORICAL MAPPING ARTIFACTS...")

    candidates = find_candidate_mapping_files()

    inspected = []

    for path in candidates:
        result = inspect_tabular_file(path)

        if result is not None:
            inspected.append(result)

    print()
    print(f"CANDIDATE FILES FOUND: {len(candidates)}")
    print(f"TABULAR FILES INSPECTED: {len(inspected)}")

    for item in inspected[:30]:
        print()
        print(item)

    # ------------------------------------------------------------
    # IMPORTANT:
    # Do NOT guess a mapping if no authoritative source is found.
    # ------------------------------------------------------------

    result = {
        "operation": "H-RUN-003",
        "operation_name": "T4 neighbor to historical mapping",
        "status": "MAPPING_SOURCE_DISCOVERY_COMPLETE",

        "ticket": {
            "title": TICKET_TITLE,
            "description": TICKET_DESCRIPTION,
        },

        "frozen_artifacts": {
            "tfidf": str(TFIDF_PATH),
            "neighbors": str(NEIGHBORS_PATH),
            "retrieval": str(RETRIEVAL_PATH),
        },

        "runtime": {
            "transformed_shape": list(X.shape),
            "neighbor_count": len(indices),
            "neighbor_indices": indices,
            "distances": distances,
        },

        "retrieval_archive": {
            "neighbor_indices_shape": list(neighbor_indices.shape),
            "neighbor_similarities_shape": list(
                neighbor_similarities.shape
            ),
        },

        "candidate_mapping_files": [
            str(path) for path in candidates
        ],

        "tabular_schema_inspection": inspected,

        "controls": {
            "model_execution": True,
            "model_fitting": False,
            "retraining": False,
            "threshold_selection": False,
            "artifact_modification": False,
            "locked_test_use": False,
            "synthetic_target_creation": False,
            "assignee_inference_without_mapping": False,
        },

        "interpretation": (
            "The frozen T4 runtime produced historical neighbor indices. "
            "An assignee interpretation is permitted only if an "
            "authoritative development-population mapping from neighbor "
            "index to historical ticket/assignee is identified."
        ),
    }

    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)

    print()
    print("=" * 72)
    print("STATUS: PASS")
    print(f"OUTPUT: {OUTPUT_PATH}")
    print("=" * 72)


if __name__ == "__main__":
    main()