from __future__ import annotations

from pathlib import Path


# =============================================================================
# T7 MOD-003 — IDENTIFY MOZILLA CORE SOURCE
# =============================================================================

DATASET_ROOT = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE"
)

EXPECTED_ARTIFACT_NAME = (
    "DTM-002_T7_TIME_TO_FIRST_RESOLVED_derived.csv"
)


def main() -> None:
    print("=" * 80)
    print("T7 MOD-003 — MOZILLA CORE SOURCE IDENTIFICATION")
    print("=" * 80)
    print()

    # -------------------------------------------------------------------------
    # 1. Verify dataset root
    # -------------------------------------------------------------------------

    print("[1/4] Checking Mozilla CORE dataset directory...")

    if not DATASET_ROOT.exists():
        raise FileNotFoundError(
            f"Mozilla CORE dataset directory not found:\n{DATASET_ROOT}"
        )

    if not DATASET_ROOT.is_dir():
        raise NotADirectoryError(
            f"Expected directory, found non-directory:\n{DATASET_ROOT}"
        )

    print(f"Dataset root: {DATASET_ROOT}")
    print("Directory: VALID")
    print()

    # -------------------------------------------------------------------------
    # 2. List immediate children only
    # -------------------------------------------------------------------------

    print("[2/4] Listing immediate contents only...")

    children = sorted(
        DATASET_ROOT.iterdir(),
        key=lambda path: path.name.lower(),
    )

    if not children:
        print("Directory is empty.")
    else:
        for path in children:
            if path.is_dir():
                kind = "DIR "
            elif path.is_file():
                kind = "FILE"
            else:
                kind = "OTHER"

            try:
                size = path.stat().st_size
                size_text = f"{size:,} bytes"
            except OSError:
                size_text = "size unavailable"

            print(f"  [{kind}] {path.name} — {size_text}")

    print()

    # -------------------------------------------------------------------------
    # 3. Identify likely source files
    # -------------------------------------------------------------------------

    print("[3/4] Identifying candidate Mozilla CORE source files...")

    source_candidates = []

    source_extensions = {
        ".csv",
        ".tsv",
        ".json",
        ".jsonl",
        ".parquet",
        ".pkl",
        ".pickle",
        ".zip",
        ".gz",
        ".bz2",
        ".xz",
    }

    for path in children:
        if path.is_file() and path.suffix.lower() in source_extensions:
            if path.name != EXPECTED_ARTIFACT_NAME:
                source_candidates.append(path)

    if source_candidates:
        print()
        print("Potential source files:")
        for path in source_candidates:
            try:
                size = path.stat().st_size
                size_text = f"{size:,} bytes"
            except OSError:
                size_text = "size unavailable"

            print(f"  - {path.name} — {size_text}")
    else:
        print()
        print("No obvious source file found at this directory level.")

    print()

    # -------------------------------------------------------------------------
    # 4. Important: no recursive scan
    # -------------------------------------------------------------------------

    print("[4/4] Scan boundary...")
    print("  Recursive search: NO")
    print("  File contents read: NO")
    print("  CSV/JSON/etc. loaded: NO")
    print("  Raw dataset modified: NO")
    print("  T7 artifact modified: NO")
    print("  Model trained: NO")
    print()

    print("=" * 80)
    print("T7 MOD-003 SOURCE IDENTIFICATION: COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()