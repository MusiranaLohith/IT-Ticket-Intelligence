from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

TRAIN_PATH = (
    ROOT
    / "modeling"
    / "T4"
    / "derived"
    / "t4_train.csv"
)

TFIDF_PATH = (
    ROOT
    / "modeling"
    / "T4"
    / "results"
    / "mod007_checkpoints"
    / "t4_mod007_tfidf.joblib"
)

NEIGHBORS_PATH = (
    ROOT
    / "modeling"
    / "T4"
    / "results"
    / "mod007_checkpoints"
    / "t4_mod007_neighbors.joblib"
)

OUTPUT_PATH = (
    ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "h_run004_single_ticket_t4_resolved_neighbors.json"
)


TITLE = "VPN connection fails after password reset"

DESCRIPTION = (
    "I reset my corporate password this morning. Since then, the VPN client "
    "connects briefly and then disconnects. I restarted the laptop and "
    "reinstalled the VPN client, but the issue persists. I need access to "
    "the internal systems for today's work."
)

TICKET_TEXT = f"{TITLE}\n{DESCRIPTION}".strip()


def main():

    print("=" * 72)
    print("H-RUN-004 — T4 RESOLVE HISTORICAL NEIGHBORS")
    print("=" * 72)

    print()
    print("INPUT TICKET:")
    print(TICKET_TEXT)

    print()
    print("LOADING DEVELOPMENT POPULATION:")
    print(TRAIN_PATH)

    train = pd.read_csv(TRAIN_PATH)

    print()
    print("DEVELOPMENT POPULATION:")
    print(f"rows: {len(train)}")
    print(f"columns: {list(train.columns)}")

    required_columns = [
        "ID",
        "Creation time",
        "Creator",
        "Creator Detail",
        "Summary",
        "Description",
        "target_assignee",
    ]

    missing = [
        column
        for column in required_columns
        if column not in train.columns
    ]

    if missing:
        raise RuntimeError(
            f"Required columns missing from t4_train.csv: {missing}"
        )

    print()
    print("LOADING FROZEN T4 RUNTIME:")

    print(f"TF-IDF:    {TFIDF_PATH}")
    print(f"NEIGHBORS: {NEIGHBORS_PATH}")

    tfidf = joblib.load(TFIDF_PATH)
    neighbors = joblib.load(NEIGHBORS_PATH)

    X = tfidf.transform([TICKET_TEXT])

    distances, indices = neighbors.kneighbors(
        X,
        n_neighbors=5,
        return_distance=True,
    )

    indices = indices[0]
    distances = distances[0]

    print()
    print("RUNTIME NEIGHBORS:")
    print(
        json.dumps(
            {
                "indices": indices.tolist(),
                "distances": distances.tolist(),
            },
            indent=2,
        )
    )

    # ------------------------------------------------------------
    # Verify index compatibility before resolving anything.
    # ------------------------------------------------------------

    max_index = int(indices.max())
    min_index = int(indices.min())

    print()
    print("INDEX COMPATIBILITY:")
    print(f"minimum neighbor index: {min_index}")
    print(f"maximum neighbor index: {max_index}")
    print(f"training population rows: {len(train)}")

    if min_index < 0 or max_index >= len(train):
        raise RuntimeError(
            "Neighbor index falls outside t4_train.csv row range."
        )

    # ------------------------------------------------------------
    # Resolve exact rows.
    # ------------------------------------------------------------

    resolved = []

    for rank, (index, distance) in enumerate(
        zip(indices, distances),
        start=1,
    ):

        row = train.iloc[int(index)]

        resolved.append(
            {
                "rank": rank,
                "neighbor_index": int(index),
                "distance": float(distance),
                "ID": row["ID"],
                "Creation time": row["Creation time"],
                "Creator": row["Creator"],
                "Creator Detail": row["Creator Detail"],
                "Summary": row["Summary"],
                "Description": row["Description"],
                "target_assignee": row["target_assignee"],
            }
        )

    print()
    print("=" * 72)
    print("RESOLVED HISTORICAL NEIGHBORS")
    print("=" * 72)

    for item in resolved:

        print()
        print(
            f"RANK {item['rank']} "
            f"| index={item['neighbor_index']} "
            f"| distance={item['distance']:.6f}"
        )

        print(f"ID: {item['ID']}")
        print(f"Creation time: {item['Creation time']}")
        print(f"Creator: {item['Creator']}")
        print(f"Creator Detail: {item['Creator Detail']}")
        print(f"Target assignee: {item['target_assignee']}")
        print(f"Summary: {item['Summary']}")

    # ------------------------------------------------------------
    # Assignee frequency among retrieved historical neighbors.
    # ------------------------------------------------------------

    assignees = [
        item["target_assignee"]
        for item in resolved
        if pd.notna(item["target_assignee"])
    ]

    assignee_counts = (
        pd.Series(assignees)
        .value_counts()
        .to_dict()
    )

    print()
    print("=" * 72)
    print("RETRIEVED ASSIGNEE FREQUENCY")
    print("=" * 72)

    print(json.dumps(assignee_counts, indent=2, default=str))

    # ------------------------------------------------------------
    # IMPORTANT INTERPRETATION
    # ------------------------------------------------------------

    result = {
        "operation": "H-RUN-004",
        "operation_name": "T4 historical neighbor resolution",

        "status": "PASS",

        "ticket": {
            "title": TITLE,
            "description": DESCRIPTION,
        },

        "development_population": {
            "path": str(TRAIN_PATH),
            "rows": int(len(train)),
            "columns": list(train.columns),
        },

        "frozen_runtime": {
            "tfidf": str(TFIDF_PATH),
            "neighbors": str(NEIGHBORS_PATH),
        },

        "runtime": {
            "transformed_shape": list(X.shape),
            "neighbor_count": int(len(indices)),
            "neighbors": resolved,
        },

        "retrieved_assignee_frequency": assignee_counts,

        "controls": {
            "model_execution": True,
            "model_fitting": False,
            "retraining": False,
            "threshold_selection": False,
            "artifact_modification": False,
            "locked_test_use": False,
            "synthetic_target_creation": False,
        },

        "interpretation": (
            "The five T4 nearest neighbors were resolved against the "
            "development population used by the frozen retrieval model. "
            "Their target_assignee values are historical retrieval evidence "
            "only and do not establish operational assignee eligibility, "
            "correctness, authorization, or an autonomous assignment policy."
        ),
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(
            result,
            f,
            indent=2,
            default=str,
        )

    print()
    print("=" * 72)
    print("STATUS: PASS")
    print(f"OUTPUT: {OUTPUT_PATH}")
    print("=" * 72)


if __name__ == "__main__":
    main()