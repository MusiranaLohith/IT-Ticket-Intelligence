from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd


# =============================================================================
# T7 MOD-003 — DUPLICATE SOURCE-ID DIAGNOSTIC
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

T7_TARGET_ARTIFACT = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T7_TIME_TO_FIRST_RESOLVED_derived.csv"
)

RAW_ARCHIVE = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "Mozilla_CORE_dataset_issues.zip"
)

RAW_MEMBER = "dataset_issues_TOTAL_TOTAL.csv"

OUTPUT_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "T7"
    / "metrics"
)

DUPLICATE_OUTPUT = (
    OUTPUT_DIR
    / "t7_mod003_duplicate_source_records.csv"
)

CHUNK_SIZE = 25_000

SOURCE_COLUMNS = [
    "ID",
    "Creation time",
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
]


def clean_ids(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip()


def main() -> None:

    print("=" * 80)
    print("T7 MOD-003 — DUPLICATE SOURCE-ID DIAGNOSTIC")
    print("=" * 80)
    print()

    # -------------------------------------------------------------------------
    # 1. Load accepted T7 IDs only
    # -------------------------------------------------------------------------

    print("[1/5] Loading accepted T7 ID population...")

    target = pd.read_csv(
        T7_TARGET_ARTIFACT,
        dtype={"ID": "string"},
        usecols=["ID"],
    )

    target["ID"] = clean_ids(target["ID"])

    if target["ID"].duplicated().any():
        raise ValueError(
            "Accepted T7 artifact itself contains duplicate IDs."
        )

    target_ids = set(target["ID"].tolist())

    print(f"T7 IDs: {len(target_ids):,}")
    print()

    # -------------------------------------------------------------------------
    # 2. Prepare output
    # -------------------------------------------------------------------------

    print("[2/5] Preparing duplicate diagnostic output...")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if DUPLICATE_OUTPUT.exists():
        DUPLICATE_OUTPUT.unlink()

    print(f"Output: {DUPLICATE_OUTPUT}")
    print()

    # -------------------------------------------------------------------------
    # 3. Stream raw source
    # -------------------------------------------------------------------------

    print("[3/5] Streaming Mozilla CORE source...")
    print()
    print("This pass stores ONLY duplicate T7 source records.")
    print(f"Chunk size: {CHUNK_SIZE:,}")
    print()

    command = [
        "/usr/bin/7z",
        "x",
        "-so",
        str(RAW_ARCHIVE),
        RAW_MEMBER,
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1024 * 1024,
    )

    if process.stdout is None:
        process.kill()
        raise RuntimeError(
            "Could not open 7z stdout."
        )

    seen_ids: set[str] = set()

    duplicate_ids: set[str] = set()

    raw_rows = 0
    chunks = 0
    matched_rows = 0
    duplicate_rows = 0
    output_header_written = False

    try:

        reader = pd.read_csv(
            process.stdout,
            chunksize=CHUNK_SIZE,
            dtype={"ID": "string"},
            usecols=SOURCE_COLUMNS,
            low_memory=False,
        )

        for chunk in reader:

            chunks += 1
            raw_rows += len(chunk)

            chunk["ID"] = clean_ids(
                chunk["ID"]
            )

            matched = chunk[
                chunk["ID"].isin(target_ids)
            ].copy()

            if not matched.empty:

                matched_rows += len(matched)

                duplicate_mask = matched["ID"].isin(
                    seen_ids
                )

                duplicate_part = matched[
                    duplicate_mask
                ].copy()

                if not duplicate_part.empty:

                    duplicate_rows += len(
                        duplicate_part
                    )

                    duplicate_ids.update(
                        duplicate_part["ID"]
                        .dropna()
                        .tolist()
                    )

                    duplicate_part.to_csv(
                        DUPLICATE_OUTPUT,
                        mode=(
                            "a"
                            if output_header_written
                            else "w"
                        ),
                        header=not output_header_written,
                        index=False,
                    )

                    output_header_written = True

                # Add IDs only after duplicate detection.
                seen_ids.update(
                    matched["ID"]
                    .dropna()
                    .tolist()
                )

            del matched
            del chunk

            if chunks % 20 == 0:

                print(
                    f"  chunks={chunks:,} | "
                    f"raw_rows={raw_rows:,} | "
                    f"matched_rows={matched_rows:,} | "
                    f"duplicate_rows={duplicate_rows:,}"
                )

    finally:

        if process.poll() is None:
            process.kill()

    stderr = process.stderr.read().decode(
        "utf-8",
        errors="replace",
    )

    return_code = process.wait()

    if return_code != 0:

        print()
        print("7z stderr:")
        print(stderr)

        raise RuntimeError(
            f"7z failed with exit code {return_code}."
        )

    # -------------------------------------------------------------------------
    # 4. Final diagnostic accounting
    # -------------------------------------------------------------------------

    print()
    print("[4/5] Duplicate accounting...")
    print()

    print(f"Raw rows processed:      {raw_rows:,}")
    print(f"Chunks processed:        {chunks:,}")
    print(f"Matched T7 rows:         {matched_rows:,}")
    print(f"Unique matched IDs:      {len(seen_ids):,}")
    print(f"Duplicate source rows:   {duplicate_rows:,}")
    print(f"Duplicate ID values:     {len(duplicate_ids):,}")
    print()

    if duplicate_ids:
        print("Duplicate T7 ID(s):")
        for duplicate_id in sorted(duplicate_ids):
            print(f"  {duplicate_id}")
    else:
        print("No duplicate T7 IDs detected.")

    print()

    # -------------------------------------------------------------------------
    # 5. Show exact duplicate records
    # -------------------------------------------------------------------------

    print("[5/5] Showing duplicate records...")

    if DUPLICATE_OUTPUT.exists():

        duplicate_df = pd.read_csv(
            DUPLICATE_OUTPUT,
            dtype={"ID": "string"},
            low_memory=False,
        )

        duplicate_df["ID"] = clean_ids(
            duplicate_df["ID"]
        )

        print()
        print(
            duplicate_df.to_string(
                index=False
            )
        )

        print()
        print(
            f"Diagnostic records written: "
            f"{len(duplicate_df):,}"
        )

    else:

        print("No duplicate diagnostic records were written.")

    print()
    print("=" * 80)
    print("DUPLICATE DIAGNOSTIC COMPLETED")
    print("=" * 80)
    print()
    print("Raw archive modified: NO")
    print("T7 target modified:   NO")
    print("Model trained:        NO")
    print()
    print(
        f"Diagnostic artifact: {DUPLICATE_OUTPUT}"
    )


if __name__ == "__main__":
    main()