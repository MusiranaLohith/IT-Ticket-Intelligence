from __future__ import annotations

import json
import re
from pathlib import Path


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OP026_DIR = (
    PROJECT_ROOT / "modeling/T8/mod036/op026"
)

T8_DIR = (
    PROJECT_ROOT / "modeling/T8"
)

FMP_SCRIPTS_DIR = (
    PROJECT_ROOT / "modeling/FMP/scripts"
)

METRICS_DIR = (
    PROJECT_ROOT / "modeling/FMP/metrics"
)

VALIDATION_JSON = (
    OP026_DIR
    / "t8_mod036_op026_decision_engine_validation.json"
)

OUTPUT_PATH = (
    METRICS_DIR
    / "f_op005_op026_producer_output_trace.json"
)

SEARCH_TERMS = [
    "119895",
    "19",
    "prediction",
    "predictions",
    "prediction_path",
    "output",
    "output_path",
    "artifact",
    "artifact_path",
    "row_count",
    "ticket_id",
    "write_csv",
    "to_csv",
    "to_parquet",
    "json",
    "save",
]


def flatten_json(
    value,
    path="root",
):
    results = []

    if isinstance(value, dict):

        for key, child in value.items():

            child_path = (
                f"{path}.{key}"
            )

            results.append(
                (
                    child_path,
                    key,
                    child,
                )
            )

            results.extend(
                flatten_json(
                    child,
                    child_path,
                )
            )

    elif isinstance(value, list):

        for index, child in enumerate(
            value[:20]
        ):

            child_path = (
                f"{path}[{index}]"
            )

            results.append(
                (
                    child_path,
                    str(index),
                    child,
                )
            )

            results.extend(
                flatten_json(
                    child,
                    child_path,
                )
            )

    return results


def trace_validation_json():

    result = {
        "exists": VALIDATION_JSON.exists(),
        "readable": False,
        "matches": [],
        "top_level_keys": [],
    }

    if not VALIDATION_JSON.exists():
        return result

    try:

        with VALIDATION_JSON.open(
            "r",
            encoding="utf-8",
        ) as f:

            data = json.load(f)

        result["readable"] = True

        if isinstance(data, dict):
            result["top_level_keys"] = [
                str(key)
                for key in data.keys()
            ]

        flattened = flatten_json(data)

        for path, key, value in flattened:

            text = (
                f"{path} = "
                f"{repr(value)}"
            )

            lower_text = text.lower()

            matched_terms = [
                term
                for term in SEARCH_TERMS
                if term.lower() in lower_text
            ]

            if matched_terms:

                result["matches"].append(
                    {
                        "path": path,
                        "key": key,
                        "value": value,
                        "matched_terms": (
                            matched_terms
                        ),
                    }
                )

    except Exception as exc:

        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

    return result


def candidate_source_files():

    candidates = []

    # FMP scripts
    if FMP_SCRIPTS_DIR.exists():

        for path in sorted(
            FMP_SCRIPTS_DIR.glob(
                "*op026*.py"
            )
        ):
            candidates.append(path)

    # T8 tree — only filenames that
    # clearly reference OP-026
    if T8_DIR.exists():

        for path in sorted(
            T8_DIR.rglob("*")
        ):

            if not path.is_file():
                continue

            name = path.name.lower()

            if (
                "op026" in name
                and path.suffix.lower()
                == ".py"
            ):
                if path not in candidates:
                    candidates.append(path)

    return candidates


def trace_source(
    path: Path,
):

    result = {
        "path": str(path),
        "readable": False,
        "matching_lines": [],
    }

    try:

        text = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        result["readable"] = True
        result["bytes"] = path.stat().st_size

        for line_number, line in enumerate(
            text.splitlines(),
            start=1,
        ):

            lower = line.lower()

            matched_terms = [
                term
                for term in SEARCH_TERMS
                if term.lower() in lower
            ]

            if matched_terms:

                result[
                    "matching_lines"
                ].append(
                    {
                        "line": line_number,
                        "text": line.strip(),
                        "matched_terms": (
                            matched_terms
                        ),
                    }
                )

    except Exception as exc:

        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

    return result


def locate_referenced_paths(
    validation_trace,
):

    paths = []

    for match in validation_trace.get(
        "matches",
        [],
    ):

        value = match.get(
            "value"
        )

        if not isinstance(
            value,
            str,
        ):
            continue

        candidate = value.strip()

        if not candidate:
            continue

        if (
            "/"
            in candidate
            or "\\"
            in candidate
            or candidate.endswith(
                (
                    ".csv",
                    ".json",
                    ".jsonl",
                    ".parquet",
                    ".pkl",
                    ".pickle",
                    ".npz",
                    ".joblib",
                )
            )
        ):

            paths.append(candidate)

    return sorted(
        set(paths)
    )


def main():

    METRICS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    validation_trace = (
        trace_validation_json()
    )

    source_files = (
        candidate_source_files()
    )

    source_traces = [
        trace_source(path)
        for path in source_files
    ]

    referenced_paths = (
        locate_referenced_paths(
            validation_trace
        )
    )

    existing_referenced_paths = []
    missing_referenced_paths = []

    for raw_path in referenced_paths:

        path = Path(raw_path)

        if not path.is_absolute():
            path = PROJECT_ROOT / path

        if path.exists():
            existing_referenced_paths.append(
                str(path.resolve())
            )
        else:
            missing_referenced_paths.append(
                raw_path
            )

    output = {
        "operation": "F-OP-005",
        "title": (
            "OP-026 Producer/Output Trace"
        ),
        "read_only": True,
        "models_executed": False,
        "model_modified": False,
        "retraining_performed": False,
        "threshold_selection_performed": False,
        "locked_test_reused_for_policy_selection": (
            False
        ),
        "expected_population": {
            "rows": 119895,
            "columns": 19,
        },
        "validation_json": (
            validation_trace
        ),
        "candidate_source_files": [
            str(path)
            for path in source_files
        ],
        "source_traces": source_traces,
        "referenced_paths": (
            referenced_paths
        ),
        "existing_referenced_paths": (
            existing_referenced_paths
        ),
        "missing_referenced_paths": (
            missing_referenced_paths
        ),
    }

    # Determine whether the producer/output
    # binding has been uniquely resolved.
    strong_output_matches = []

    for source in source_traces:

        for match in source.get(
            "matching_lines",
            [],
        ):

            line = match["text"].lower()

            output_signal = any(
                token in line
                for token in [
                    "to_csv",
                    "to_parquet",
                    "json.dump",
                    "open(",
                    "write(",
                    "save(",
                ]
            )

            population_signal = (
                "119895" in line
                or "prediction" in line
                or "predictions" in line
                or "output" in line
                or "artifact" in line
            )

            if (
                output_signal
                and population_signal
            ):
                strong_output_matches.append(
                    {
                        "source": source[
                            "path"
                        ],
                        "line": match[
                            "line"
                        ],
                        "text": match[
                            "text"
                        ],
                    }
                )

    output[
        "strong_producer_output_matches"
    ] = strong_output_matches

    unique_existing = sorted(
        set(existing_referenced_paths)
    )

    if len(unique_existing) == 1:

        status = "PASS"

        resolution = (
            "UNIQUE_OUTPUT_PATH_REFERENCED"
        )

    elif len(strong_output_matches) == 1:

        status = "PASS"

        resolution = (
            "UNIQUE_PRODUCER_OUTPUT_BINDING"
        )

    else:

        status = "REQUIRES_REVIEW"

        resolution = (
            "PRODUCER_OUTPUT_BINDING_NOT_UNIQUELY_RESOLVED"
        )

    output["status"] = status
    output["population_resolution"] = resolution

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("=" * 72)
    print(
        "F-OP-005 — OP-026 "
        "PRODUCER/OUTPUT TRACE"
    )
    print("=" * 72)

    print(
        "Validation JSON readable : "
        f"{validation_trace['readable']}"
    )

    print(
        "OP-026 source files      : "
        f"{len(source_files)}"
    )

    print(
        "Referenced paths         : "
        f"{len(referenced_paths)}"
    )

    print(
        "Existing referenced     : "
        f"{len(unique_existing)}"
    )

    print(
        "Missing referenced      : "
        f"{len(missing_referenced_paths)}"
    )

    print(
        "Producer/output matches : "
        f"{len(strong_output_matches)}"
    )

    if unique_existing:

        print()
        print(
            "EXISTING REFERENCED PATHS"
        )
        print("-" * 72)

        for path in unique_existing:
            print(path)

    if missing_referenced_paths:

        print()
        print(
            "MISSING REFERENCED PATHS"
        )
        print("-" * 72)

        for path in missing_referenced_paths:
            print(path)

    if strong_output_matches:

        print()
        print(
            "PRODUCER OUTPUT MATCHES"
        )
        print("-" * 72)

        for match in strong_output_matches:

            print(
                f"{match['source']}::"
                f"{match['line']}"
            )

            print(
                f"  {match['text']}"
            )

    print()
    print(
        "Population resolution : "
        f"{resolution}"
    )

    print(
        f"Output                 : "
        f"{OUTPUT_PATH}"
    )

    print("=" * 72)
    print(
        f"RESULT: {status} — "
        "F-OP-005 complete"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()