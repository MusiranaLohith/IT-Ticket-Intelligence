"""
T10 / OP-017
T5 Locked-Evaluation Generation Provenance Resolution

Purpose
-------
Trace the provenance of:

    T5/metrics/t5_mod009_locked_evaluation_predictions.npz

back to the existing T5 generation logic and determine whether the
20,827 prediction rows can be explicitly connected to canonical
ticket IDs.

This operation is investigative and fail-closed.

It does NOT:
    - modify T5 artifacts
    - create a new split
    - reconstruct IDs by assumption
    - use the 74,091 validation population as the locked population
    - perform T2/T4/T7 joins
    - create a fusion model
    - create a universal score
    - establish thresholds
    - assign ticket-level policy states
"""

from pathlib import Path
import re
import json


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T5_ROOT = PROJECT_ROOT / "modeling" / "T5"

LOCKED_NPZ = (
    T5_ROOT
    / "metrics"
    / "t5_mod009_locked_evaluation_predictions.npz"
)

SEARCH_ROOTS = [
    T5_ROOT,
    PROJECT_ROOT / "modeling" / "T8",
]


KEYWORDS = [
    "t5_mod009_locked_evaluation_predictions",
    "mod009",
    "locked_evaluation",
    "20827",
    "20827",
    "evaluation_predictions",
    "p_duplicate",
]


def read_text(path):
    try:
        return path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except Exception:
        return ""


def search_files():
    results = []

    seen = set()

    for root in SEARCH_ROOTS:

        if not root.exists():
            continue

        for path in root.rglob("*"):

            if not path.is_file():
                continue

            if path in seen:
                continue

            seen.add(path)

            suffix = path.suffix.lower()

            if suffix not in {
                ".py",
                ".json",
                ".txt",
                ".md",
                ".csv",
            }:
                continue

            text = read_text(path)

            if not text:
                continue

            lower = text.lower()

            matched = []

            for keyword in KEYWORDS:
                if keyword.lower() in lower:
                    matched.append(keyword)

            if matched:
                results.append(
                    (
                        path,
                        matched,
                    )
                )

    return results


def print_context(path, matched):
    print()
    print("-" * 82)
    print(f"FILE : {path}")
    print(f"MATCHES : {matched}")
    print("-" * 82)

    text = read_text(path)

    lines = text.splitlines()

    emitted = set()

    for index, line in enumerate(lines):

        lower = line.lower()

        if not any(
            keyword.lower() in lower
            for keyword in matched
        ):
            continue

        start = max(0, index - 3)
        end = min(len(lines), index + 4)

        for i in range(start, end):

            if i in emitted:
                continue

            emitted.add(i)

            print(
                f"{i + 1:5d}: {lines[i][:240]}"
            )


def inspect_t5_structure():
    print("=" * 82)
    print("T5 LOCKED ARTIFACT")
    print("=" * 82)

    if not LOCKED_NPZ.exists():
        raise FileNotFoundError(
            f"Missing locked NPZ: {LOCKED_NPZ}"
        )

    import numpy as np

    with np.load(
        LOCKED_NPZ,
        allow_pickle=False,
    ) as data:

        print(f"Artifact : {LOCKED_NPZ}")
        print(f"Arrays   : {data.files}")

        for name in data.files:

            arr = data[name]

            print(
                f"{name:15s} "
                f"shape={arr.shape} "
                f"dtype={arr.dtype}"
            )

    print()


def main():

    print("=" * 82)
    print("T10 / OP-017 — T5 LOCKED-EVALUATION GENERATION PROVENANCE")
    print("=" * 82)
    print()

    inspect_t5_structure()

    print("=" * 82)
    print("1. SEARCHING EXISTING T5/T8 PROVENANCE")
    print("=" * 82)

    results = search_files()

    print(
        f"Candidate provenance files containing relevant keywords: "
        f"{len(results)}"
    )

    for path, matched in results:
        print(f"{path}")
        print(f"  matches: {matched}")

    print()

    print("=" * 82)
    print("2. RELEVANT PROVENANCE CONTEXT")
    print("=" * 82)

    for path, matched in results:
        print_context(path, matched)

    print()

    print("=" * 82)
    print("3. PROVENANCE RESOLUTION QUESTIONS")
    print("=" * 82)

    print(
        "A valid resolution requires explicit evidence for:"
    )

    print(
        "  [A] which source dataset produced the 20,827 evaluation rows"
    )

    print(
        "  [B] which split/file supplied those rows"
    )

    print(
        "  [C] how the prediction-row ordering was constructed"
    )

    print(
        "  [D] whether the ordering is explicitly tied to canonical IDs"
    )

    print(
        "  [E] whether any saved evaluation artifact contains those IDs"
    )

    print()

    print("=" * 82)
    print("4. FORBIDDEN INFERENCES")
    print("=" * 82)

    print(
        "74,091-row validation population != 20,827-row locked evaluation"
    )

    print(
        "NPZ array position != ticket ID unless explicitly documented"
    )

    print(
        "Equal row counts != population identity"
    )

    print(
        "Matching target values != ticket identity"
    )

    print()

    print("=" * 82)
    print("5. CURRENT PROVENANCE STATUS")
    print("=" * 82)

    print(
        "The script has inspected existing provenance evidence only."
    )

    print(
        "No new split or mapping has been created."
    )

    print(
        "No T2/T4/T7 intersection has been performed."
    )

    print()

    print("=" * 82)
    print("6. FINAL RESULT")
    print("=" * 82)

    print(
        "OP-017 STATUS : PROVENANCE INVESTIGATION COMPLETE"
    )

    print(
        "Interpretation depends on the evidence printed above."
    )

    print(
        "NO RN IS ASSIGNED AUTOMATICALLY."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())