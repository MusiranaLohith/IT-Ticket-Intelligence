from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T7_ROOT = ROOT / "modeling" / "T7"
SCRIPT_DIR = T7_ROOT / "scripts"
METRICS_DIR = T7_ROOT / "metrics"
MODEL_DIR = T7_ROOT / "models"
DERIVED_DIR = T7_ROOT / "derived"
SPLITS_DIR = T7_ROOT / "splits"

OUTPUT_PATH = (
    ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "fmp06_op018r22c_t7_compact_runtime_interface_resolution.json"
)


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def source_signals(path: Path) -> dict:
    text = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    lowered = text.lower()

    signals = {
        "lognormal": (
            "lognormal" in lowered
            or "log-normal" in lowered
        ),
        "aft": "aft" in lowered,
        "survival": "survival" in lowered,
        "duration": "duration" in lowered,
        "event": "event" in lowered,
        "censor": "censor" in lowered,
        "right_censor": (
            "right censor" in lowered
            or "right_censored" in lowered
            or "right-censored" in lowered
        ),
        "predict": "predict" in lowered,
        "predict_survival_function": (
            "predict_survival_function" in lowered
        ),
        "predict_median": (
            "predict_median" in lowered
        ),
        "predict_expectation": (
            "predict_expectation" in lowered
        ),
        "joblib_load": (
            "joblib.load" in lowered
            or "from joblib import load" in lowered
        ),
        "pickle_load": (
            "pickle.load" in lowered
        ),
        "fit": ".fit(" in lowered,
    }

    return signals


def function_names(path: Path) -> list[str]:
    try:
        tree = ast.parse(
            path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        )
    except SyntaxError:
        return []

    names = []

    for node in ast.walk(tree):

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            lowered = node.name.lower()

            if any(
                token in lowered
                for token in (
                    "predict",
                    "survival",
                    "censor",
                    "duration",
                    "event",
                    "model",
                    "feature",
                    "load",
                    "reconstruct",
                    "aft",
                )
            ):
                names.append(
                    node.name
                )

    return sorted(
        set(names)
    )


def json_summary(path: Path) -> dict:
    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
    except Exception as exc:
        return {
            "read_error": str(exc)
        }

    if not isinstance(data, dict):
        return {
            "type": type(data).__name__
        }

    keys = list(data.keys())

    interesting = {}

    wanted = {
        "model",
        "model_type",
        "final_model",
        "final_model_name",
        "selected_model",
        "selected_model_name",
        "event",
        "event_column",
        "duration",
        "duration_column",
        "time_column",
        "censoring",
        "boundary",
        "target",
        "status",
        "closure_status",
    }

    for key in keys:

        if key in wanted:
            value = data[key]

            if isinstance(
                value,
                (str, int, float, bool),
            ) or value is None:

                interesting[key] = value

    return {
        "keys": keys[:80],
        "interesting_fields": interesting,
    }


def csv_schema(path: Path) -> dict:
    import pandas as pd

    try:
        frame = pd.read_csv(
            path,
            nrows=3,
        )

        return {
            "columns": list(
                frame.columns
            ),
            "sample_rows": len(frame),
        }

    except Exception as exc:

        return {
            "read_error": str(exc)
        }


def main() -> None:

    print("=" * 72)
    print(
        "FMP-06 OP-018R22C — "
        "T7 COMPACT FROZEN RUNTIME INTERFACE RESOLUTION"
    )
    print("=" * 72)

    print()
    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation metrics: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    report = {
        "operation": "FMP-06 OP-018R22C",
        "status": "PASS",
        "read_only": True,
        "training": False,
        "fitting": False,
        "prediction": False,
        "evaluation": False,
        "locked_test": False,
        "artifact_modification": False,
    }

    # ================================================================
    # 1. Closure evidence
    # ================================================================

    print()
    print("[1] T7 closure evidence")

    closure_files = sorted(
        METRICS_DIR.glob("*closure*.json")
    )

    report["closure_files"] = []

    for path in closure_files:

        summary = json_summary(path)

        report["closure_files"].append(
            {
                "path": relative(path),
                **summary,
            }
        )

        interesting = summary.get(
            "interesting_fields",
            {},
        )

        print(
            f"  {relative(path)}"
        )

        for key, value in interesting.items():

            print(
                f"    {key}: {value}"
            )

    if not closure_files:
        print("  NONE")

    # ================================================================
    # 2. Runtime scripts
    # ================================================================

    print()
    print("[2] T7 runtime-relevant scripts")

    script_results = []

    for path in sorted(
        SCRIPT_DIR.glob("*.py")
    ):

        signals = source_signals(path)
        functions = function_names(path)

        relevant = any(
            signals.values()
        ) or bool(functions)

        if not relevant:
            continue

        result = {
            "path": relative(path),
            "signals": signals,
            "functions": functions,
        }

        script_results.append(
            result
        )

        active_signals = [
            key
            for key, value in signals.items()
            if value
        ]

        print(
            f"  {relative(path)}"
        )

        if active_signals:

            print(
                "    signals: "
                + ", ".join(
                    active_signals
                )
            )

        if functions:

            print(
                "    functions: "
                + ", ".join(functions)
            )

    report["runtime_scripts"] = (
        script_results
    )

    # ================================================================
    # 3. Serialized artifacts
    # ================================================================

    print()
    print("[3] T7 serialized artifacts")

    serialized_suffixes = {
        ".joblib",
        ".pkl",
        ".pickle",
        ".pt",
        ".pth",
        ".bin",
        ".safetensors",
    }

    serialized = []

    if MODEL_DIR.exists():

        for path in sorted(
            MODEL_DIR.rglob("*")
        ):

            if (
                path.is_file()
                and path.suffix.lower()
                in serialized_suffixes
            ):

                serialized.append(
                    {
                        "path": relative(path),
                        "size_bytes": path.stat().st_size,
                    }
                )

    report["serialized_artifacts"] = serialized

    if serialized:

        for item in serialized:

            print(
                f"  {item['path']} "
                f"({item['size_bytes']} bytes)"
            )

    else:

        print("  NONE")

    # ================================================================
    # 4. Candidate native CSV schemas
    # ================================================================

    print()
    print("[4] Native T7 CSV schemas")

    csv_results = []

    roots = [
        DERIVED_DIR,
        SPLITS_DIR,
    ]

    for root in roots:

        if not root.exists():
            continue

        for path in sorted(
            root.rglob("*.csv")
        ):

            schema = csv_schema(
                path
            )

            columns = schema.get(
                "columns",
                [],
            )

            survival_columns = [
                column
                for column in columns
                if any(
                    token in column.lower()
                    for token in (
                        "time",
                        "duration",
                        "event",
                        "resolved",
                        "censor",
                        "creation",
                        "target",
                    )
                )
            ]

            if not survival_columns:
                continue

            result = {
                "path": relative(path),
                "columns": columns,
                "survival_relevant_columns": (
                    survival_columns
                ),
            }

            csv_results.append(
                result
            )

            print(
                f"  {relative(path)}"
            )

            print(
                "    relevant: "
                + ", ".join(
                    survival_columns
                )
            )

    report["native_csv_schemas"] = (
        csv_results
    )

    # ================================================================
    # 5. Final compact resolution
    # ================================================================

    print()
    print("[5] Runtime resolution")

    combined = json.dumps(
        report,
        ensure_ascii=False,
    ).lower()

    resolution = {
        "lognormal": (
            "lognormal" in combined
            or "log-normal" in combined
        ),
        "aft": "aft" in combined,
        "survival": "survival" in combined,
        "event_semantics": "event" in combined,
        "censor_semantics": "censor" in combined,
        "right_censor_semantics": (
            "right_censor" in combined
            or "right-censor" in combined
        ),
        "serialized_model_available": (
            len(serialized) > 0
        ),
        "prediction_interface_candidate": any(
            item["signals"].get(
                "predict",
                False,
            )
            for item in script_results
        ),
    }

    report["resolution"] = resolution

    for key, value in resolution.items():

        print(
            f"  {key}: "
            f"{value}"
        )

    # ================================================================
    # 6. Save detailed report
    # ================================================================

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 72)
    print(
        "OP-018R22C INSPECTION COMPLETE"
    )
    print("=" * 72)

    print(
        f"Output: {OUTPUT_PATH}"
    )

    print()
    print("No training performed.")
    print("No fitting performed.")
    print("No prediction performed.")
    print("No evaluation performed.")
    print("No locked test used.")
    print("No artifact modification performed.")

    print("=" * 72)


if __name__ == "__main__":
    main()