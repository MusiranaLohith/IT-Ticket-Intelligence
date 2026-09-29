from __future__ import annotations

import csv
import sys
from pathlib import Path


csv.field_size_limit(sys.maxsize)


PROJECT_ROOT = Path(
    "/"
)

DATASET = (
    PROJECT_ROOT
    / "modeling"
    / "derived"
    / "t1_vscode_dataset.csv"
)


def context(text: str, index: int, width: int = 180) -> str:
    start = max(0, index - width)
    end = min(len(text), index + width)

    return (
        text[start:end]
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )


def main():

    if not DATASET.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET}"
        )

    with DATASET.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        rows = list(reader)

    flagged = []

    for row in rows:

        description = row["description_clean"]

        lower = description.casefold()

        positions = []

        for marker in [
            "issue type:",
            "type:",
        ]:

            start = 0

            while True:

                index = lower.find(
                    marker,
                    start,
                )

                if index == -1:
                    break

                positions.append(
                    (
                        index,
                        marker,
                    )
                )

                start = index + 1

        if positions:

            flagged.append(
                (
                    row,
                    positions,
                )
            )

    print(
        "VSCODE_T1_LEAKAGE_INSPECTION_COMPLETE"
    )

    print(
        f"FLAGGED_RECORDS={len(flagged)}"
    )

    print()

    for number, (row, positions) in enumerate(
        flagged,
        start=1,
    ):

        print(
            f"RECORD={number}"
            f" ISSUE_ID={row['issue_id']}"
            f" TARGET={row['issue_type']}"
            f" REPRESENTATION={row['target_representation']}"
            f" SOURCE_ROW={row['source_row']}"
        )

        for index, marker in positions:

            print(
                f"MARKER={marker}"
                f" INDEX={index}"
            )

            print(
                "CONTEXT="
                + context(
                    row["description_clean"],
                    index,
                )
            )

        print()

    print(
        "RAW_SOURCE_MODIFIED=False"
    )


if __name__ == "__main__":
    main()