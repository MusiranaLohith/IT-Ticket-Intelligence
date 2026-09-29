from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OP026_DIR = (
    PROJECT_ROOT / "modeling/T8/mod036/op026"
)

METRICS_DIR = (
    PROJECT_ROOT / "modeling/FMP/metrics"
)

OUTPUT_PATH = (
    METRICS_DIR
    / "f_op003_op026_row_population_locator.json"
)

EXPECTED_ROWS = 119_895


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def describe_value(value: Any) -> dict[str, Any]:
    result = {
        "type": type(value).__name__,
    }

    if isinstance(value, list):
        result["length"] = len(value)

        if value and isinstance(value[0], dict):
            result["first_row_keys"] = [
                str(key)
                for key in value[0].keys()
            ]

    elif isinstance(value, dict):
        result["keys"] = [
            str(key)
            for key in value.keys()
        ]

    return result


def inspect_json(path: Path) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": str(path),
        "filename": path.name,
        "bytes": path.stat().st_size,
        "readable": False,
    }

    try:
        data = load_json(path)

        record["readable"] = True
        record["top_level_type"] = type(data).__name__

        if isinstance(data, list):
            record["top_level_length"] = len(data)

            if data and isinstance(data[0], dict):
                record["row_like"] = True
                record["row_count"] = len(data)
                record["keys"] = [
                    str(key)
                    for key in data[0].keys()
                ]

        elif isinstance(data, dict):
            record["top_level_keys"] = [
                str(key)
                for key in data.keys()
            ]

            candidate_row_keys = [
                "predictions",
                "prediction_rows",
                "records",
                "rows",
                "results",
                "data",
            ]

            nested_candidates = []

            for key in candidate_row_keys:
                if key not in data:
                    continue

                value = data[key]

                description = describe_value(value)

                nested_record = {
                    "key": key,
                    **description,
                }

                if (
                    isinstance(value, list)
                    and value
                    and isinstance(value[0], dict)
                ):
                    nested_record["row_count"] = len(value)

                nested_candidates.append(
                    nested_record
                )

            record["nested_row_candidates"] = (
                nested_candidates
            )

        return record

    except Exception as exc:
        record["error"] = (
            f"{type(exc).__name__}: {exc}"
        )
        return record


def main() -> None:
    METRICS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_files = sorted(
        OP026_DIR.glob("*.json")
    )

    records = [
        inspect_json(path)
        for path in json_files
    ]

    row_candidates = []

    for record in records:
        if not record.get("readable"):
            continue

        if (
            record.get("row_like") is True
            and record.get("row_count") is not None
        ):
            row_candidates.append(
                {
                    "path": record["path"],
                    "row_count": record["row_count"],
                    "keys": record.get("keys", []),
                    "matches_expected": (
                        record["row_count"]
                        == EXPECTED_ROWS
                    ),
                }
            )

        for candidate in record.get(
            "nested_row_candidates",
            [],
        ):
            if candidate.get("row_count") is None:
                continue

            row_candidates.append(
                {
                    "path": record["path"],
                    "container_key": candidate["key"],
                    "row_count": candidate["row_count"],
                    "keys": candidate.get(
                        "first_row_keys",
                        [],
                    ),
                    "matches_expected": (
                        candidate["row_count"]
                        == EXPECTED_ROWS
                    ),
                }
            )

    exact_matches = [
        candidate
        for candidate in row_candidates
        if candidate["matches_expected"]
    ]

    status = (
        "PASS"
        if len(exact_matches) == 1
        else "REQUIRES_REVIEW"
    )

    result = {
        "operation": "F-OP-003",
        "title": (
            "OP-026 Row-Level Population Locator"
        ),
        "status": status,
        "read_only": True,
        "models_executed": False,
        "model_modified": False,
        "retraining_performed": False,
        "threshold_selection_performed": False,
        "locked_test_reused_for_policy_selection": False,
        "op026_directory": str(OP026_DIR),
        "json_files_discovered": len(json_files),
        "json_files_readable": sum(
            1
            for record in records
            if record.get("readable") is True
        ),
        "expected_row_count": EXPECTED_ROWS,
        "row_candidates": row_candidates,
        "exact_expected_matches": exact_matches,
        "all_file_records": records,
        "authoritative_population_resolution": (
            "UNIQUE_119895_ROW_ARTIFACT_IDENTIFIED"
            if len(exact_matches) == 1
            else "NOT_UNIQUELY_RESOLVED"
        ),
        "next_step": (
            "Use the uniquely identified row-level artifact "
            "for final E2E evaluation."
            if len(exact_matches) == 1
            else "Resolve population artifact before evaluation."
        ),
    }

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("=" * 72)
    print(
        "F-OP-003 — OP-026 ROW-LEVEL POPULATION LOCATOR"
    )
    print("=" * 72)
    print(
        f"OP-026 directory       : {OP026_DIR}"
    )
    print(
        f"JSON files discovered  : {len(json_files)}"
    )
    print(
        "Expected row count     : "
        f"{EXPECTED_ROWS}"
    )
    print(
        "Row candidates         : "
        f"{len(row_candidates)}"
    )
    print(
        "Exact 119895 matches   : "
        f"{len(exact_matches)}"
    )

    print()

    if exact_matches:
        print("EXACT MATCHES")
        print("-" * 72)

        for match in exact_matches:
            print(
                f"File        : {match['path']}"
            )

            if "container_key" in match:
                print(
                    f"Container    : "
                    f"{match['container_key']}"
                )

            print(
                f"Rows        : "
                f"{match['row_count']}"
            )

            print(
                "Keys        : "
                f"{', '.join(match['keys'])}"
            )

    print()
    print(
        "Population resolution : "
        + (
            "UNIQUE_119895_ROW_ARTIFACT_IDENTIFIED"
            if len(exact_matches) == 1
            else "NOT_UNIQUELY_RESOLVED"
        )
    )

    print(
        f"Output                 : {OUTPUT_PATH}"
    )

    print("=" * 72)
    print(
        f"RESULT: {status} — F-OP-003 complete"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()