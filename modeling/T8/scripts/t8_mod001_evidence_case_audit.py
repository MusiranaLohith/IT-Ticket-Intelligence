#!/usr/bin/env python3

from __future__ import annotations

import csv
import sys
from pathlib import Path


# Allow large CSV fields without truncating or modifying source data.
csv.field_size_limit(sys.maxsize)


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

MODELING_ROOT = PROJECT_ROOT / "modeling"
T8_ROOT = MODELING_ROOT / "T8"

MOZILLA_ROOT = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE"
)

RAW_MOZILLA_ARCHIVE = (
    MOZILLA_ROOT / "Mozilla_CORE_dataset_issues.zip"
)

ARTIFACTS = [
    {
        "name": "Layer A — Ticket-Level Evidence",
        "path": MOZILLA_ROOT
        / "DTM-002_T8_LAYER_A_TICKET_EVIDENCE_derived.csv",
        "expected_width": 51,
        "expected_rows": 513_816,
        "grain": "ticket_id",
        "required_columns": ["ticket_id"],
    },
    {
        "name": "Layer B — T6 Query Evidence",
        "path": MOZILLA_ROOT
        / "DTM-002_T8_LAYER_B_T6_QUERY_EVIDENCE_derived.csv",
        "expected_width": 13,
        "expected_rows": 2_722,
        "grain": "query_id",
        "required_columns": ["query_id"],
    },
    {
        "name": "Layer C — T6 Query-Candidate Evidence",
        "path": MOZILLA_ROOT
        / "DTM-002_T8_LAYER_C_T6_QUERY_CANDIDATE_EVIDENCE_derived.csv",
        "expected_width": 20,
        "expected_rows": 274_922,
        "grain": "query_id + candidate_id",
        "required_columns": ["query_id", "candidate_id"],
    },
    {
        "name": "Ticket Decision-Support Representation",
        "path": MOZILLA_ROOT
        / "DTM-002_T8_TICKET_DECISION_SUPPORT_derived.csv",
        "expected_width": 44,
        "expected_rows": 513_816,
        "grain": "ticket_id",
        "required_columns": ["ticket_id"],
    },
]


def print_rule(char: str = "=") -> None:
    print(char * 88)


def inspect_modeling_structure() -> None:
    print_rule()
    print("STEP 1 — EXISTING MODELING STRUCTURE")
    print_rule()

    print(f"Project root : {PROJECT_ROOT}")
    print(f"Modeling root: {MODELING_ROOT}")
    print()

    if not PROJECT_ROOT.exists():
        print("PROJECT_ROOT_EXISTS: FALSE")
        raise SystemExit(
            "ERROR: Project root does not exist."
        )

    print("PROJECT_ROOT_EXISTS: TRUE")

    if not MODELING_ROOT.exists():
        print("MODELING_ROOT_EXISTS: FALSE")
        print("No existing modeling/ directory was found.")
        return

    print("MODELING_ROOT_EXISTS: TRUE")

    entries = sorted(
        MODELING_ROOT.iterdir(),
        key=lambda p: (not p.is_dir(), p.name.lower()),
    )

    if not entries:
        print("MODELING_ROOT_CONTENTS: EMPTY")
        return

    print("MODELING_ROOT_CONTENTS:")

    for entry in entries:
        kind = "DIR " if entry.is_dir() else "FILE"
        print(f"  {kind}  {entry.name}")

    if T8_ROOT.exists():
        print()
        print("T8_ROOT_EXISTS: TRUE")

        for path in sorted(T8_ROOT.rglob("*")):
            relative = path.relative_to(T8_ROOT)
            kind = "DIR " if path.is_dir() else "FILE"
            print(f"  {kind}  T8/{relative}")
    else:
        print("T8_ROOT_EXISTS: FALSE")


def inspect_artifact(spec: dict) -> dict:
    path = spec["path"]

    result = {
        "name": spec["name"],
        "path": str(path),
        "exists": path.is_file(),
        "size_bytes": None,
        "header": None,
        "schema_width": None,
        "physical_rows": None,
        "expected_width": spec["expected_width"],
        "expected_rows": spec["expected_rows"],
        "width_match": False,
        "population_match": False,
        "required_columns": spec["required_columns"],
        "grain": spec["grain"],
        "grain_columns_present": False,
    }

    if not result["exists"]:
        return result

    result["size_bytes"] = path.stat().st_size

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:

        reader = csv.reader(handle)

        header = next(reader, None)

        if header is None:
            result["header"] = []
            result["schema_width"] = 0
            result["physical_rows"] = 0
            return result

        result["header"] = header
        result["schema_width"] = len(header)

        result["grain_columns_present"] = all(
            column in header
            for column in spec["required_columns"]
        )

        physical_rows = 0

        for _ in reader:
            physical_rows += 1

        result["physical_rows"] = physical_rows

    result["width_match"] = (
        result["schema_width"] == result["expected_width"]
    )

    result["population_match"] = (
        result["physical_rows"] == result["expected_rows"]
    )

    return result


def print_artifact_result(result: dict) -> None:
    print_rule()
    print(result["name"])
    print_rule("-")

    print(f"Path:                  {result['path']}")
    print(f"Exists:                {result['exists']}")

    if not result["exists"]:
        print("STATUS:                MISSING")
        return

    print(f"File size (bytes):     {result['size_bytes']}")
    print(f"Schema width:          {result['schema_width']}")
    print(f"Expected width:        {result['expected_width']}")
    print(f"Width match:           {result['width_match']}")
    print(f"Physical CSV rows:     {result['physical_rows']}")
    print(f"Expected population:   {result['expected_rows']}")
    print(f"Population match:      {result['population_match']}")
    print(f"Required grain:        {result['grain']}")
    print(
        "Grain columns present:"
        f" {result['grain_columns_present']}"
    )

    print()
    print("Header:")

    for index, column in enumerate(
        result["header"],
        start=1,
    ):
        print(f"  {index:02d}. {column}")

    print()

    if (
        result["width_match"]
        and result["population_match"]
        and result["grain_columns_present"]
    ):
        print("ARTIFACT RECONCILIATION: PASS")
    else:
        print("ARTIFACT RECONCILIATION: REVIEW REQUIRED")


def verify_raw_archive_not_opened() -> None:
    print_rule()
    print("RAW MOZILLA ARCHIVE SAFETY CHECK")
    print_rule()

    print(f"Raw archive path: {RAW_MOZILLA_ARCHIVE}")
    print(
        "Archive exists:"
        f" {RAW_MOZILLA_ARCHIVE.is_file()}"
    )

    if RAW_MOZILLA_ARCHIVE.is_file():
        print(
            "Archive size (bytes):"
            f" {RAW_MOZILLA_ARCHIVE.stat().st_size}"
        )

    print()
    print(
        "RAW ARCHIVE ACCESS MODE: "
        "FILESYSTEM METADATA ONLY"
    )
    print(
        "RAW ARCHIVE OPENED/SCANNED: FALSE"
    )
    print(
        "RAW CSV MEMBER OPENED/SCANNED: FALSE"
    )


def main() -> None:
    print()
    print_rule()
    print("T8 MOD-001 — EVIDENCE / CASE-DEFINITION RECONCILIATION")
    print("RN #015")
    print_rule()

    print(
        "MODE: READ-ONLY CURRENT-WORKSPACE RECONCILIATION"
    )
    print("No T8 contract reconstruction.")
    print("No T8 derived artifact creation.")
    print("No model training.")
    print("No raw Mozilla archive scanning.")
    print()

    inspect_modeling_structure()

    print()
    print_rule()
    print("STEP 2 — FROZEN T8 ARTIFACT RECONCILIATION")
    print_rule()

    results = []

    for spec in ARTIFACTS:
        result = inspect_artifact(spec)
        results.append(result)
        print_artifact_result(result)

    print()
    verify_raw_archive_not_opened()

    print()
    print_rule()
    print("T8 MOD-001 SUMMARY")
    print_rule()

    all_present = all(
        result["exists"]
        for result in results
    )

    all_widths_match = all(
        result["width_match"]
        for result in results
        if result["exists"]
    )

    all_populations_match = all(
        result["population_match"]
        for result in results
        if result["exists"]
    )

    all_grains_present = all(
        result["grain_columns_present"]
        for result in results
        if result["exists"]
    )

    print(
        f"All four artifacts present:     "
        f"{all_present}"
    )
    print(
        f"All schema widths match:        "
        f"{all_widths_match}"
    )
    print(
        f"All populations match:          "
        f"{all_populations_match}"
    )
    print(
        f"All grain identifiers present:  "
        f"{all_grains_present}"
    )
    print(
        "Raw archive opened/scanned:     FALSE"
    )

    if (
        all_present
        and all_widths_match
        and all_populations_match
        and all_grains_present
    ):
        print()
        print(
            "T8 MOD-001 RECONCILIATION RESULT: PASS"
        )
        print(
            "The current workspace matches the "
            "frozen T8 artifact definitions."
        )
    else:
        print()
        print(
            "T8 MOD-001 RECONCILIATION RESULT: "
            "REVIEW REQUIRED"
        )
        print(
            "One or more current-workspace properties "
            "do not match the frozen DTM evidence."
        )

    print()
    print_rule()
    print("END OF RN #015 EXECUTION")
    print_rule()


if __name__ == "__main__":
    main()