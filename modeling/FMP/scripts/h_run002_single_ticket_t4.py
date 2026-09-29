from pathlib import Path
import json

import joblib
import numpy as np


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)


# ------------------------------------------------------------------
# Test ticket
# ------------------------------------------------------------------

TICKET_TITLE = (
    "VPN connection fails after password reset"
)

TICKET_DESCRIPTION = (
    "I reset my corporate password this morning. "
    "Since then, the VPN client connects briefly and "
    "then disconnects. I restarted the laptop and "
    "reinstalled the VPN client, but the issue persists. "
    "I need access to the internal systems for today's work."
)

TICKET_TEXT = (
    f"{TICKET_TITLE}\n"
    f"{TICKET_DESCRIPTION}"
).strip()


# ------------------------------------------------------------------
# Frozen T4 artifacts
#
# Actual locations verified on the user's machine.
# ------------------------------------------------------------------

TFIDF_ARTIFACT = (
    PROJECT_ROOT
    / "modeling/T4/results/mod007_checkpoints/"
    "t4_mod007_tfidf.joblib"
)

NEIGHBORS_ARTIFACT = (
    PROJECT_ROOT
    / "modeling/T4/results/mod007_checkpoints/"
    "t4_mod007_neighbors.joblib"
)

RETRIEVAL_ARTIFACT = (
    PROJECT_ROOT
    / "modeling/T4/results/mod007_checkpoints/"
    "t4_mod007_full_retrieval.npz"
)


OUTPUT = (
    PROJECT_ROOT
    / "modeling/FMP/metrics/"
    "h_run002_single_ticket_t4.json"
)


# ------------------------------------------------------------------
# Helper
# ------------------------------------------------------------------

def describe_object(obj):

    result = {
        "type": (
            f"{type(obj).__module__}."
            f"{type(obj).__name__}"
        )
    }

    for attribute in (
        "shape",
        "n_features_in_",
        "n_samples_fit_",
        "n_neighbors",
    ):

        if hasattr(obj, attribute):

            try:

                value = getattr(
                    obj,
                    attribute,
                )

                if isinstance(
                    value,
                    (int, float, str, bool),
                ):

                    result[attribute] = value

            except Exception:
                pass

    if isinstance(obj, dict):

        result["keys"] = list(
            obj.keys()
        )[:30]

    return result


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():

    print("=" * 72)
    print(
        "H-RUN-002 — SINGLE TICKET T4 RETRIEVAL"
    )
    print("=" * 72)

    print()
    print("TITLE:")
    print(TICKET_TITLE)

    print()
    print("DESCRIPTION:")
    print(TICKET_DESCRIPTION)

    # --------------------------------------------------------------
    # Verify frozen artifacts.
    # --------------------------------------------------------------

    artifacts = {
        "tfidf": TFIDF_ARTIFACT,
        "neighbors": NEIGHBORS_ARTIFACT,
        "retrieval": RETRIEVAL_ARTIFACT,
    }

    print()
    print("FROZEN ARTIFACTS:")

    for name, path in artifacts.items():

        if not path.exists():

            raise FileNotFoundError(
                f"T4 {name} artifact missing: {path}"
            )

        print(
            f"{name}: {path}"
        )

    # --------------------------------------------------------------
    # Runtime controls.
    # --------------------------------------------------------------

    print()
    print("CONTROLS:")
    print("model execution: YES")
    print("model fitting: NO")
    print("retraining: NO")
    print("threshold selection: NO")
    print("artifact modification: NO")
    print("locked test use: NO")

    # --------------------------------------------------------------
    # Load frozen artifacts.
    # --------------------------------------------------------------

    tfidf = joblib.load(
        TFIDF_ARTIFACT
    )

    neighbors = joblib.load(
        NEIGHBORS_ARTIFACT
    )

    retrieval = np.load(
        RETRIEVAL_ARTIFACT,
        allow_pickle=True,
    )

    # --------------------------------------------------------------
    # Describe loaded objects.
    # --------------------------------------------------------------

    print()
    print("TF-IDF:")

    print(
        json.dumps(
            describe_object(tfidf),
            indent=2,
        )
    )

    print()
    print("NEIGHBORS:")

    print(
        json.dumps(
            describe_object(neighbors),
            indent=2,
        )
    )

    # --------------------------------------------------------------
    # Inspect retrieval archive.
    # --------------------------------------------------------------

    print()
    print("RETRIEVAL ARCHIVE KEYS:")

    print(
        list(
            retrieval.files
        )
    )

    retrieval_summary = {}

    for key in retrieval.files:

        value = retrieval[key]

        summary = {
            "type": (
                f"{type(value).__module__}."
                f"{type(value).__name__}"
            ),

            "shape": (
                list(value.shape)
                if hasattr(value, "shape")
                else None
            ),
        }

        if hasattr(value, "dtype"):

            if value.dtype.kind in (
                "U",
                "S",
                "O",
            ):

                try:

                    flattened = (
                        value.reshape(-1)
                    )

                    summary["preview"] = [
                        str(item)
                        for item
                        in flattened[:5]
                    ]

                except Exception:
                    pass

        retrieval_summary[key] = summary

    print()

    print(
        json.dumps(
            retrieval_summary,
            indent=2,
        )
    )

    # --------------------------------------------------------------
    # Verify runtime interfaces.
    # --------------------------------------------------------------

    if not hasattr(
        tfidf,
        "transform",
    ):

        raise TypeError(
            "Frozen T4 TF-IDF artifact "
            "does not expose transform()."
        )

    if not hasattr(
        neighbors,
        "kneighbors",
    ):

        raise TypeError(
            "Frozen T4 neighbor artifact "
            "does not expose kneighbors()."
        )

    # --------------------------------------------------------------
    # Actual frozen retrieval inference.
    # --------------------------------------------------------------

    X = tfidf.transform(
        [TICKET_TEXT]
    )

    print()
    print(
        "TRANSFORMED SHAPE:",
        list(X.shape),
    )

    distances, indices = (
        neighbors.kneighbors(
            X,
            n_neighbors=5,
            return_distance=True,
        )
    )

    print()
    print(
        "RETRIEVED COUNT:",
        len(indices[0]),
    )

    print(
        "NEIGHBOR INDICES:",
        [
            int(value)
            for value in indices[0]
        ],
    )

    print(
        "DISTANCES:",
        [
            float(value)
            for value in distances[0]
        ],
    )

    # --------------------------------------------------------------
    # Persist result.
    # --------------------------------------------------------------

    result = {

        "operation":
            "H-RUN-002",

        "operation_name":
            "Single Ticket T4 Frozen Retrieval",

        "status":
            "PASS",

        "ticket": {

            "title":
                TICKET_TITLE,

            "description":
                TICKET_DESCRIPTION,

            "representation":
                TICKET_TEXT,
        },

        "artifacts": {

            "tfidf":
                str(TFIDF_ARTIFACT),

            "neighbors":
                str(NEIGHBORS_ARTIFACT),

            "retrieval":
                str(RETRIEVAL_ARTIFACT),
        },

        "runtime": {

            "transformed_shape":
                list(X.shape),

            "retrieved_count":
                int(len(indices[0])),

            "neighbor_indices": [
                int(value)
                for value in indices[0]
            ],

            "distances": [
                float(value)
                for value in distances[0]
            ],
        },

        "retrieval_archive":
            retrieval_summary,

        "controls": {

            "model_execution":
                True,

            "model_fitting":
                False,

            "retraining":
                False,

            "threshold_selection":
                False,

            "artifact_modification":
                False,

            "locked_test_use":
                False,
        },

        "interpretation": (
            "T4 output is native historical retrieval "
            "evidence. Retrieved historical neighbors are "
            "not treated as guaranteed operationally "
            "eligible assignees and no autonomous assignment "
            "decision is made."
        ),
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