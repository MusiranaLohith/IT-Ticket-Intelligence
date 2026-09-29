from __future__ import annotations

import csv
import re
import sys
import zipfile
from pathlib import Path


csv.field_size_limit(sys.maxsize)


RAW_ZIP = Path(
    "/run/media/whiteblack/User 1/Datasets/GitBugs/vscode_bugs.csv.zip"
)

SAMPLE_LIMIT = 20


def clean(value):
    if value is None:
        return ""
    return str(value).replace("\r\n", "\n").replace("\r", "\n")


def show_context(text, start, end, width=220):
    left = max(0, start - width)
    right = min(len(text), end + width)

    context = text[left:right]

    return (
        context
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )


def main():

    with zipfile.ZipFile(RAW_ZIP, "r") as zf:

        if "vscode_bugs.csv" not in zf.namelist():
            raise RuntimeError(
                "vscode_bugs.csv not found in source ZIP"
            )

        with zf.open(
            "vscode_bugs.csv",
            "r",
        ) as f:

            text = f.read().decode(
                "utf-8-sig",
                errors="replace",
            )

    reader = csv.DictReader(
        text.splitlines()
    )

    rows = list(reader)

    type_occurrences = []
    issue_type_occurrences = []

    for source_row, row in enumerate(
        rows,
        start=2,
    ):

        description = clean(
            row.get("Description")
        )

        for match in re.finditer(
            r"Type\s*:",
            description,
            flags=re.IGNORECASE,
        ):

            type_occurrences.append(
                {
                    "source_row": source_row,
                    "issue_id": row.get("Issue id", ""),
                    "start": match.start(),
                    "end": match.end(),
                    "context": show_context(
                        description,
                        match.start(),
                        match.end(),
                    ),
                }
            )

        for match in re.finditer(
            r"Issue\s+Type\s*:",
            description,
            flags=re.IGNORECASE,
        ):

            issue_type_occurrences.append(
                {
                    "source_row": source_row,
                    "issue_id": row.get("Issue id", ""),
                    "start": match.start(),
                    "end": match.end(),
                    "context": show_context(
                        description,
                        match.start(),
                        match.end(),
                    ),
                }
            )

    print("VSCODE_T1_MARKER_INSPECTION_COMPLETE")
    print(f"SOURCE_RECORDS={len(rows)}")
    print(
        "LITERAL_TYPE_MARKER_OCCURRENCES="
        f"{len(type_occurrences)}"
    )
    print(
        "LITERAL_ISSUE_TYPE_MARKER_OCCURRENCES="
        f"{len(issue_type_occurrences)}"
    )

    print()
    print("TYPE_MARKER_SAMPLES")

    for i, item in enumerate(
        type_occurrences[:SAMPLE_LIMIT],
        start=1,
    ):

        print(
            f"SAMPLE={i}"
            f" SOURCE_ROW={item['source_row']}"
            f" ISSUE_ID={item['issue_id']}"
        )

        print(
            f"CONTEXT={item['context']}"
        )

    print()
    print("ISSUE_TYPE_MARKER_SAMPLES")

    for i, item in enumerate(
        issue_type_occurrences[:SAMPLE_LIMIT],
        start=1,
    ):

        print(
            f"SAMPLE={i}"
            f" SOURCE_ROW={item['source_row']}"
            f" ISSUE_ID={item['issue_id']}"
        )

        print(
            f"CONTEXT={item['context']}"
        )

    print()
    print("RAW_SOURCE_MODIFIED=False")


if __name__ == "__main__":
    main()