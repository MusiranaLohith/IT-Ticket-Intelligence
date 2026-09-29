from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T4_ROOT = PROJECT_ROOT / "modeling/T4"

OUTPUT = (
    PROJECT_ROOT
    / "modeling/FMP/metrics/"
    "fmp06_op018r10_t4_artifact_location_reconciliation.json"
)

EXPECTED_ARTIFACTS = [
    "t4_mod007_tfidf.joblib",
    "t4_mod007_neighbors.joblib",
    "t4_mod007_full_retrieval.npz",
]

T4_CLOSURE_REFERENCES = [
    "t4_r1_metrics.json",
    "t4_mod007_full_results.json",
    "t4_mod007_full_retrieval.npz",
    "t4_mod007_neighbors.joblib",
    "t4_mod007_tfidf.joblib",
    "t4_mod008_full.json",
    "t4_mod011_full.json",
]


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def describe(path: Path) -> dict:
    return {
        "path": rel(path),
        "size_bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> None:

    print("=" * 72)
    print(
        "FMP-06 OP-018R10 — "
        "T4 ARTIFACT LOCATION RECONCILIATION"
    )
    print("=" * 72)
    print()

    if not T4_ROOT.exists():
        raise FileNotFoundError(
            f"T4 directory not found: {T4_ROOT}"
        )

    print("T4 ROOT:")
    print(rel(T4_ROOT))
    print()

    # ------------------------------------------------------------
    # 1. Exact-name search
    # ------------------------------------------------------------

    exact_matches = {}

    for filename in EXPECTED_ARTIFACTS:

        matches = sorted(
            T4_ROOT.rglob(filename)
        )

        exact_matches[filename] = [
            describe(path)
            for path in matches
        ]

        print(
            f"{filename}: "
            f"{len(matches)} exact match(es)"
        )

        for path in matches:
            print(
                f"  {rel(path)} "
                f"({path.stat().st_size} bytes)"
            )

    print()

    # ------------------------------------------------------------
    # 2. All serialized T4 artifacts
    # ------------------------------------------------------------

    extensions = {
        ".joblib",
        ".npz",
        ".pkl",
        ".pickle",
        ".npy",
    }

    serialized_files = []

    for path in sorted(T4_ROOT.rglob("*")):

        if not path.is_file():
            continue

        if path.suffix.lower() not in extensions:
            continue

        serialized_files.append(
            describe(path)
        )

    print(
        "SERIALIZED T4 FILES FOUND:",
        len(serialized_files),
    )

    for item in serialized_files:
        print(
            f"  {item['path']} "
            f"({item['size_bytes']} bytes)"
        )

    print()

    # ------------------------------------------------------------
    # 3. T4 result/closure references
    # ------------------------------------------------------------

    reference_reconciliation = []

    for filename in T4_CLOSURE_REFERENCES:

        matches = sorted(
            T4_ROOT.rglob(filename)
        )

        reference_reconciliation.append(
            {
                "referenced_name": filename,
                "found": bool(matches),
                "matches": [
                    describe(path)
                    for path in matches
                ],
            }
        )

    # ------------------------------------------------------------
    # 4. Status classification
    # ------------------------------------------------------------

    missing_exact = [
        filename
        for filename, matches in exact_matches.items()
        if not matches
    ]

    ambiguous_exact = [
        filename
        for filename, matches in exact_matches.items()
        if len(matches) > 1
    ]

    found_exact = [
        filename
        for filename, matches in exact_matches.items()
        if len(matches) == 1
    ]

    if ambiguous_exact:
        status = "AMBIGUOUS"
    elif missing_exact:
        status = "INCOMPLETE"
    else:
        status = "FOUND"

    result = {
        "operation": "FMP-06 OP-018R10",
        "operation_type": (
            "T4_ARTIFACT_LOCATION_RECONCILIATION"
        ),
        "status": status,
        "t4_root": rel(T4_ROOT),
        "expected_artifacts": EXPECTED_ARTIFACTS,
        "exact_matches": exact_matches,
        "found_exact": found_exact,
        "missing_exact": missing_exact,
        "ambiguous_exact": ambiguous_exact,
        "all_serialized_t4_files": serialized_files,
        "closure_reference_reconciliation": (
            reference_reconciliation
        ),
        "runtime_execution": False,
        "retraining": False,
        "artifact_creation": False,
        "artifact_modification": False,
        "note": (
            "Read-only artifact reconciliation. "
            "No T4 inference, fitting, retraining, or artifact "
            "creation was performed."
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

    print("=" * 72)
    print("STATUS:", status)
    print("RUNTIME EXECUTION: NOT PERFORMED")
    print("RETRAINING: NOT PERFORMED")
    print("ARTIFACT CREATION: NOT PERFORMED")
    print("OUTPUT:", OUTPUT)
    print("=" * 72)


if __name__ == "__main__":
    main()