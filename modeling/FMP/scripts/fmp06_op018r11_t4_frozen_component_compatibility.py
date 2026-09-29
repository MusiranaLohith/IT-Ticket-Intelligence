from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

import joblib


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T4_SCRIPT = (
    PROJECT_ROOT
    / "modeling/T4/scripts/t4_ranking_baseline.py"
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

RETRIEVAL_ARTIFACT = (
    PROJECT_ROOT
    / "modeling/T4/results/mod007_checkpoints/"
    "t4_mod007_full_retrieval.npz"
)

OUTPUT = (
    PROJECT_ROOT
    / "modeling/FMP/metrics/"
    "fmp06_op018r11_t4_frozen_component_compatibility.json"
)


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def main() -> None:

    print("=" * 72)
    print(
        "FMP-06 OP-018R11 — "
        "T4 FROZEN COMPONENT COMPATIBILITY"
    )
    print("=" * 72)
    print()

    required = [
        T4_SCRIPT,
        TFIDF_ARTIFACT,
        NEIGHBOR_ARTIFACT,
        RETRIEVAL_ARTIFACT,
    ]

    for path in required:
        print(
            f"{rel(path)}: "
            f"{'PRESENT' if path.exists() else 'MISSING'}"
        )

    print()

    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)

    # ------------------------------------------------------------
    # Inspect the actual retrieval function.
    # ------------------------------------------------------------

    source = T4_SCRIPT.read_text(
        encoding="utf-8",
        errors="replace",
    )

    tree = ast.parse(source)

    target_function = None

    for node in tree.body:
        if (
            isinstance(node, ast.FunctionDef)
            and node.name == "rank_assignees_for_row"
        ):
            target_function = node
            break

    if target_function is None:
        raise RuntimeError(
            "rank_assignees_for_row() was not found."
        )

    arguments = [
        arg.arg
        for arg in target_function.args.args
    ]

    function_source = ast.get_source_segment(
        source,
        target_function,
    )

    print(
        "rank_assignees_for_row() arguments:",
        arguments,
    )

    print()
    print(
        "rank_assignees_for_row() source:"
    )
    print(function_source)

    print()

    # ------------------------------------------------------------
    # Load frozen components.
    # ------------------------------------------------------------

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
    # Inspect inference interfaces.
    # ------------------------------------------------------------

    tfidf_methods = [
        name
        for name in [
            "transform",
            "fit",
            "fit_transform",
            "get_feature_names_out",
        ]
        if hasattr(tfidf, name)
    ]

    neighbor_methods = [
        name
        for name in [
            "kneighbors",
            "fit",
            "predict",
            "transform",
        ]
        if hasattr(neighbors, name)
    ]

    print(
        "TF-IDF METHODS:",
        tfidf_methods,
    )

    print(
        "NEIGHBOR METHODS:",
        neighbor_methods,
    )

    # ------------------------------------------------------------
    # Inspect serialized retrieval artifact without executing it.
    # ------------------------------------------------------------

    retrieval_size = RETRIEVAL_ARTIFACT.stat().st_size

    print(
        "RETRIEVAL ARTIFACT SIZE:",
        retrieval_size,
        "bytes",
    )

    result: dict[str, Any] = {
        "operation": "FMP-06 OP-018R11",
        "operation_type": (
            "T4_FROZEN_COMPONENT_COMPATIBILITY"
        ),
        "status": "PASS",
        "script": rel(T4_SCRIPT),
        "rank_assignees_for_row_arguments": arguments,
        "rank_assignees_for_row_source": function_source,
        "tfidf_artifact": rel(TFIDF_ARTIFACT),
        "neighbor_artifact": rel(NEIGHBOR_ARTIFACT),
        "retrieval_artifact": rel(RETRIEVAL_ARTIFACT),
        "tfidf_type": (
            f"{type(tfidf).__module__}."
            f"{type(tfidf).__name__}"
        ),
        "neighbor_type": (
            f"{type(neighbors).__module__}."
            f"{type(neighbors).__name__}"
        ),
        "tfidf_methods": tfidf_methods,
        "neighbor_methods": neighbor_methods,
        "retrieval_artifact_size_bytes": (
            int(retrieval_size)
        ),
        "runtime_inference": False,
        "transform_called": False,
        "kneighbors_called": False,
        "fit_called": False,
        "retraining": False,
        "artifact_modification": False,
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
    print("RUNTIME INFERENCE: NOT PERFORMED")
    print("FIT: NOT CALLED")
    print("OUTPUT:", OUTPUT)
    print("=" * 72)


if __name__ == "__main__":
    main()