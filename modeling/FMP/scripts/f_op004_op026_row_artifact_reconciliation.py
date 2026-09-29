from __future__ import annotations

import csv
import json
import pickle
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
    / "f_op004_op026_row_artifact_reconciliation.json"
)

EXPECTED_ROWS = 119_895
EXPECTED_COLUMNS = 19


def detect_ticket_column(
    columns: list[str],
) -> str | None:

    normalized = {
        str(column).strip().lower(): str(column)
        for column in columns
    }

    candidates = [
        "ticket_id",
        "ticketid",
        "ticket",
        "id",
        "issue_id",
        "case_id",
        "query_id",
    ]

    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]

    for column in columns:
        value = str(column).lower()

        if (
            "ticket" in value
            and "id" in value
        ):
            return str(column)

        if (
            "issue" in value
            and "id" in value
        ):
            return str(column)

    return None


def inspect_csv(
    path: Path,
    delimiter: str = ",",
) -> dict[str, Any]:

    result: dict[str, Any] = {
        "path": str(path),
        "format": "csv" if delimiter == "," else "tsv",
        "bytes": path.stat().st_size,
        "readable": False,
    }

    try:
        with path.open(
            "r",
            encoding="utf-8",
            errors="replace",
            newline="",
        ) as f:

            reader = csv.reader(
                f,
                delimiter=delimiter,
            )

            header = next(reader, None)

            if header is None:
                result["error"] = "EMPTY_FILE"
                return result

            row_count = 0

            for _ in reader:
                row_count += 1

            result["readable"] = True
            result["row_count"] = row_count
            result["column_count"] = len(header)
            result["columns"] = header
            result["ticket_id_column"] = (
                detect_ticket_column(header)
            )

    except Exception as exc:
        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

    return result


def inspect_json(
    path: Path,
) -> dict[str, Any]:

    result: dict[str, Any] = {
        "path": str(path),
        "format": "json",
        "bytes": path.stat().st_size,
        "readable": False,
    }

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        result["readable"] = True
        result["top_level_type"] = type(data).__name__

        if isinstance(data, list):

            result["row_count"] = len(data)

            if data and isinstance(
                data[0],
                dict,
            ):
                columns = [
                    str(key)
                    for key in data[0].keys()
                ]

                result["column_count"] = len(
                    columns
                )

                result["columns"] = columns

                result["ticket_id_column"] = (
                    detect_ticket_column(columns)
                )

        elif isinstance(data, dict):

            result["top_level_keys"] = [
                str(key)
                for key in data.keys()
            ]

            candidates = [
                "predictions",
                "prediction_rows",
                "records",
                "rows",
                "results",
                "data",
            ]

            for key in candidates:

                value = data.get(key)

                if not isinstance(
                    value,
                    list,
                ):
                    continue

                if not value:
                    continue

                if not isinstance(
                    value[0],
                    dict,
                ):
                    continue

                columns = [
                    str(k)
                    for k in value[0].keys()
                ]

                result[
                    "nested_row_container"
                ] = key

                result["row_count"] = len(
                    value
                )

                result["column_count"] = len(
                    columns
                )

                result["columns"] = columns

                result[
                    "ticket_id_column"
                ] = detect_ticket_column(
                    columns
                )

                break

    except Exception as exc:
        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

    return result


def inspect_jsonl(
    path: Path,
) -> dict[str, Any]:

    result: dict[str, Any] = {
        "path": str(path),
        "format": "jsonl",
        "bytes": path.stat().st_size,
        "readable": False,
    }

    try:
        row_count = 0
        first_row = None

        with path.open(
            "r",
            encoding="utf-8",
            errors="replace",
        ) as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                value = json.loads(line)

                if first_row is None:
                    first_row = value

                row_count += 1

        result["readable"] = True
        result["row_count"] = row_count

        if isinstance(
            first_row,
            dict,
        ):
            columns = [
                str(key)
                for key in first_row.keys()
            ]

            result["column_count"] = len(
                columns
            )

            result["columns"] = columns

            result["ticket_id_column"] = (
                detect_ticket_column(columns)
            )

    except Exception as exc:
        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

    return result


def inspect_pickle(
    path: Path,
) -> dict[str, Any]:

    result: dict[str, Any] = {
        "path": str(path),
        "format": "pickle",
        "bytes": path.stat().st_size,
        "readable": False,
    }

    try:
        with path.open("rb") as f:
            data = pickle.load(f)

        result["readable"] = True
        result["object_type"] = type(data).__name__

        # Pandas DataFrame
        if hasattr(data, "shape"):

            shape = tuple(data.shape)

            result["shape"] = [
                int(value)
                for value in shape
            ]

            if hasattr(data, "columns"):

                columns = [
                    str(column)
                    for column in data.columns
                ]

                result["columns"] = columns
                result["column_count"] = len(
                    columns
                )

                result["row_count"] = int(
                    shape[0]
                )

                result["ticket_id_column"] = (
                    detect_ticket_column(
                        columns
                    )
                )

        elif isinstance(data, list):

            result["row_count"] = len(data)

            if data and isinstance(
                data[0],
                dict,
            ):

                columns = [
                    str(key)
                    for key in data[0].keys()
                ]

                result["column_count"] = len(
                    columns
                )

                result["columns"] = columns

                result["ticket_id_column"] = (
                    detect_ticket_column(
                        columns
                    )
                )

    except Exception as exc:
        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

    return result


def inspect_parquet(
    path: Path,
) -> dict[str, Any]:

    result: dict[str, Any] = {
        "path": str(path),
        "format": "parquet",
        "bytes": path.stat().st_size,
        "readable": False,
    }

    try:

        import pandas as pd

        frame = pd.read_parquet(
            path,
            engine="auto",
        )

        columns = [
            str(column)
            for column in frame.columns
        ]

        result["readable"] = True
        result["row_count"] = int(
            frame.shape[0]
        )
        result["column_count"] = int(
            frame.shape[1]
        )
        result["columns"] = columns
        result["ticket_id_column"] = (
            detect_ticket_column(
                columns
            )
        )

    except Exception as exc:
        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

    return result


def inspect_file(
    path: Path,
) -> dict[str, Any]:

    suffix = path.suffix.lower()

    if suffix == ".csv":
        return inspect_csv(path)

    if suffix == ".tsv":
        return inspect_csv(
            path,
            delimiter="\t",
        )

    if suffix == ".json":
        return inspect_json(path)

    if suffix in {
        ".jsonl",
        ".ndjson",
    }:
        return inspect_jsonl(path)

    if suffix in {
        ".pkl",
        ".pickle",
    }:
        return inspect_pickle(path)

    if suffix == ".parquet":
        return inspect_parquet(path)

    return {
        "path": str(path),
        "format": suffix or "no_extension",
        "bytes": path.stat().st_size,
        "inspected": False,
        "reason": "UNSUPPORTED_EXTENSION",
    }


def main() -> None:

    METRICS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not OP026_DIR.exists():

        print("=" * 72)
        print(
            "F-OP-004 — OP-026 ROW ARTIFACT "
            "RECONCILIATION"
        )
        print("=" * 72)
        print(
            "RESULT: BLOCKED — OP-026 directory "
            "does not exist"
        )
        print("=" * 72)

        return

    files = sorted(
        path
        for path in OP026_DIR.iterdir()
        if path.is_file()
    )

    records = [
        inspect_file(path)
        for path in files
    ]

    row_artifacts = []

    for record in records:

        row_count = record.get(
            "row_count"
        )

        column_count = record.get(
            "column_count"
        )

        if row_count is None:
            continue

        row_artifacts.append(
            {
                "path": record["path"],
                "format": record.get(
                    "format"
                ),
                "row_count": row_count,
                "column_count": column_count,
                "ticket_id_column": record.get(
                    "ticket_id_column"
                ),
                "columns": record.get(
                    "columns",
                    [],
                ),
                "matches_expected_rows": (
                    row_count
                    == EXPECTED_ROWS
                ),
                "matches_expected_shape": (
                    row_count
                    == EXPECTED_ROWS
                    and column_count
                    == EXPECTED_COLUMNS
                ),
            }
        )

    exact_shape_matches = [
        record
        for record in row_artifacts
        if record[
            "matches_expected_shape"
        ]
    ]

    exact_row_matches = [
        record
        for record in row_artifacts
        if record[
            "matches_expected_rows"
        ]
    ]

    status = (
        "PASS"
        if len(exact_shape_matches) == 1
        else "REQUIRES_REVIEW"
    )

    result = {
        "operation": "F-OP-004",
        "title": (
            "OP-026 Row-Level Artifact "
            "Reconciliation"
        ),
        "status": status,
        "read_only": True,
        "models_executed": False,
        "model_modified": False,
        "retraining_performed": False,
        "threshold_selection_performed": False,
        "locked_test_reused_for_policy_selection": (
            False
        ),
        "op026_directory": str(
            OP026_DIR
        ),
        "files_discovered": len(files),
        "files_inspected": len(records),
        "expected_rows": EXPECTED_ROWS,
        "expected_columns": EXPECTED_COLUMNS,
        "row_artifacts": row_artifacts,
        "exact_row_matches": exact_row_matches,
        "exact_shape_matches": exact_shape_matches,
        "population_resolution": (
            "UNIQUE_119895x19_ARTIFACT_IDENTIFIED"
            if len(exact_shape_matches) == 1
            else "NOT_UNIQUELY_RESOLVED"
        ),
        "all_file_records": records,
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
        "F-OP-004 — OP-026 ROW ARTIFACT "
        "RECONCILIATION"
    )
    print("=" * 72)

    print(
        f"OP-026 files discovered : {len(files)}"
    )

    print(
        f"Files inspected         : {len(records)}"
    )

    print(
        f"Expected population     : "
        f"{EXPECTED_ROWS} rows × "
        f"{EXPECTED_COLUMNS} columns"
    )

    print(
        f"Row-bearing artifacts   : "
        f"{len(row_artifacts)}"
    )

    print(
        f"119895-row matches      : "
        f"{len(exact_row_matches)}"
    )

    print(
        f"119895×19 matches       : "
        f"{len(exact_shape_matches)}"
    )

    if exact_shape_matches:

        print()
        print("EXACT SHAPE MATCH")
        print("-" * 72)

        for record in exact_shape_matches:

            print(
                f"File        : "
                f"{record['path']}"
            )

            print(
                f"Format      : "
                f"{record['format']}"
            )

            print(
                f"Rows        : "
                f"{record['row_count']}"
            )

            print(
                f"Columns     : "
                f"{record['column_count']}"
            )

            print(
                f"Ticket ID   : "
                f"{record['ticket_id_column']}"
            )

            print(
                "Column names:"
            )

            for column in record[
                "columns"
            ]:
                print(
                    f"  - {column}"
                )

    elif row_artifacts:

        print()
        print("ROW-BEARING ARTIFACTS")
        print("-" * 72)

        for record in row_artifacts:

            print(
                f"{record['path']} | "
                f"{record['row_count']} rows | "
                f"{record['column_count']} cols | "
                f"ticket_id="
                f"{record['ticket_id_column']}"
            )

    else:

        print()
        print(
            "No row-bearing artifact identified."
        )

    print()
    print(
        "Population resolution : "
        + (
            "UNIQUE_119895x19_ARTIFACT_IDENTIFIED"
            if len(exact_shape_matches) == 1
            else "NOT_UNIQUELY_RESOLVED"
        )
    )

    print(
        f"Output                  : "
        f"{OUTPUT_PATH}"
    )

    print("=" * 72)
    print(
        f"RESULT: {status} — F-OP-004 complete"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()