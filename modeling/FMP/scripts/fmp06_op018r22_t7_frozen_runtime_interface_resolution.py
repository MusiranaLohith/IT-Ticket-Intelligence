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
    / "fmp06_op018r22_t7_frozen_runtime_interface_resolution.json"
)


SEARCH_TERMS = [
    "LogNormal",
    "Log-Normal",
    "lognormal",
    "AFT",
    "survival",
    "Surv",
    "duration",
    "event",
    "censor",
    "censored",
    "right_censor",
    "time_to_resolution",
    "time_to_event",
    "predict",
    "predict_survival_function",
    "predict_median",
    "predict_expectation",
    "lifelines",
    "Weibull",
    "KaplanMeier",
    "joblib",
    "pickle",
    "load",
    "dump",
    "fit",
]


def read_text(path: Path) -> str:
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def matching_lines(
    text: str,
) -> list[str]:

    results = []

    for number, line in enumerate(
        text.splitlines(),
        start=1,
    ):
        lowered = line.lower()

        if any(
            term.lower() in lowered
            for term in SEARCH_TERMS
        ):
            results.append(
                f"{number}: {line.rstrip()}"
            )

    return results


def relevant_functions(
    path: Path,
) -> dict[str, str]:

    text = read_text(path)

    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return {
            "__SYNTAX_ERROR__": str(exc)
        }

    lines = text.splitlines()
    functions = {}

    for node in ast.walk(tree):

        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        name = node.name.lower()

        if not any(
            token in name
            for token in (
                "survival",
                "surv",
                "event",
                "censor",
                "duration",
                "time",
                "predict",
                "model",
                "fit",
                "load",
                "feature",
                "design",
                "reconstruct",
                "aft",
            )
        ):
            continue

        start = node.lineno
        end = getattr(
            node,
            "end_lineno",
            node.lineno,
        )

        functions[node.name] = "\n".join(
            lines[start - 1:end]
        )

    return functions


def inspect_source_file(
    path: Path,
) -> dict:

    if not path.exists():

        return {
            "exists": False,
        }

    text = read_text(path)

    return {
        "exists": True,
        "size_bytes": path.stat().st_size,
        "matching_lines": matching_lines(text),
        "relevant_functions": relevant_functions(path),
    }


def collect_files(
    root: Path,
) -> list[dict]:

    results = []

    if not root.exists():
        return results

    for path in sorted(
        root.rglob("*")
    ):

        if not path.is_file():
            continue

        try:
            relative = str(
                path.relative_to(ROOT)
            )
        except ValueError:
            relative = str(path)

        results.append(
            {
                "path": relative,
                "size_bytes": path.stat().st_size,
                "suffix": path.suffix.lower(),
            }
        )

    return results


def inspect_csv_schema(
    path: Path,
) -> dict:

    if not path.exists():

        return {
            "exists": False,
        }

    if path.suffix.lower() != ".csv":

        return {
            "exists": True,
            "supported_for_schema": False,
            "size_bytes": path.stat().st_size,
        }

    import pandas as pd

    frame = pd.read_csv(
        path,
        nrows=5,
    )

    return {
        "exists": True,
        "supported_for_schema": True,
        "size_bytes": path.stat().st_size,
        "columns": list(frame.columns),
        "sample_rows": len(frame),
    }


def main() -> None:

    print("=" * 72)
    print(
        "FMP-06 OP-018R22 — "
        "T7 FROZEN RUNTIME INTERFACE RESOLUTION"
    )
    print("=" * 72)

    print()
    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Evaluation metrics: NO")
    print("Locked test population: NO")
    print("Artifact modification: NO")
    print("Runtime prediction: NO")

    report = {
        "operation": "FMP-06 OP-018R22",
        "status": "PASS",
        "read_only": True,
        "training_performed": False,
        "fitting_performed": False,
        "evaluation_performed": False,
        "locked_test_used": False,
        "artifact_modified": False,
        "runtime_prediction_performed": False,
    }

    # ================================================================
    # 1. T7 directory inventory
    # ================================================================

    print()
    print("[1] Inspecting T7 directory structure...")

    directory_inventory = {
        "scripts": collect_files(
            SCRIPT_DIR
        ),
        "metrics": collect_files(
            METRICS_DIR
        ),
        "models": collect_files(
            MODEL_DIR
        ),
        "derived": collect_files(
            DERIVED_DIR
        ),
        "splits": collect_files(
            SPLITS_DIR
        ),
    }

    for name, files in directory_inventory.items():

        print(
            f"  {name}: "
            f"{len(files)} files"
        )

        for item in files:

            print(
                f"    - {item['path']} "
                f"({item['size_bytes']} bytes)"
            )

    report["directory_inventory"] = directory_inventory

    # ================================================================
    # 2. Locate T7 closure evidence
    # ================================================================

    print()
    print("[2] Inspecting T7 closure evidence...")

    closure_candidates = []

    for path in sorted(
        METRICS_DIR.glob("*closure*.json")
    ):

        closure_candidates.append(
            path
        )

    if not closure_candidates:

        print(
            "  No closure JSON matching *closure*.json found."
        )

    for path in closure_candidates:

        print()
        print(
            f"  CLOSURE: "
            f"{path.relative_to(ROOT)}"
        )

        try:

            data = json.loads(
                read_text(path)
            )

            print(
                f"  Top-level keys: "
                f"{list(data.keys())}"
            )

            report.setdefault(
                "closure_evidence",
                [],
            ).append(
                {
                    "path": str(
                        path.relative_to(ROOT)
                    ),
                    "keys": list(
                        data.keys()
                    ),
                    "content": data,
                }
            )

        except Exception as exc:

            print(
                f"  JSON read error: {exc}"
            )

    # ================================================================
    # 3. Inspect T7 Python sources
    # ================================================================

    print()
    print(
        "[3] Inspecting T7 Python source files..."
    )

    python_sources = []

    if SCRIPT_DIR.exists():

        for path in sorted(
            SCRIPT_DIR.glob("*.py")
        ):

            print()
            print("-" * 72)
            print(
                f"SOURCE: "
                f"{path.relative_to(ROOT)}"
            )
            print("-" * 72)

            result = inspect_source_file(
                path
            )

            python_sources.append(
                {
                    "path": str(
                        path.relative_to(ROOT)
                    ),
                    **result,
                }
            )

            print(
                f"Size: "
                f"{result.get('size_bytes', 0)} bytes"
            )

            matches = result.get(
                "matching_lines",
                [],
            )

            print()
            print("Matching source lines:")

            if matches:

                for line in matches:
                    print(line)

            else:

                print("  NONE")

            functions = result.get(
                "relevant_functions",
                {},
            )

            print()
            print("Relevant functions:")

            if functions:

                for name, source in functions.items():

                    print()
                    print(
                        f"[FUNCTION: {name}]"
                    )
                    print(source)

            else:

                print("  NONE")

    report["python_sources"] = python_sources

    # ================================================================
    # 4. Inspect CSV runtime candidates
    # ================================================================

    print()
    print(
        "[4] Inspecting candidate T7 CSV schemas..."
    )

    csv_candidates = []

    for root in [
        DERIVED_DIR,
        SPLITS_DIR,
        METRICS_DIR,
    ]:

        if not root.exists():
            continue

        for path in sorted(
            root.rglob("*.csv")
        ):

            csv_candidates.append(
                inspect_csv_schema(
                    path
                )
                | {
                    "path": str(
                        path.relative_to(ROOT)
                    )
                }
            )

    for item in csv_candidates:

        print()
        print(
            f"CSV: {item['path']}"
        )

        if not item.get(
            "supported_for_schema",
            False,
        ):

            print(
                "  Schema inspection unavailable."
            )

            continue

        print(
            f"  Columns: "
            f"{item['columns']}"
        )

    report["csv_candidates"] = csv_candidates

    # ================================================================
    # 5. Identify survival semantics
    # ================================================================

    print()
    print(
        "[5] Resolving T7 survival/event/censoring semantics..."
    )

    combined_source = json.dumps(
        {
            "sources": python_sources,
            "closures": report.get(
                "closure_evidence",
                [],
            ),
            "csv": csv_candidates,
        },
        ensure_ascii=False,
    ).lower()

    semantic_signals = {
        "lognormal_reference": (
            "lognormal" in combined_source
            or "log-normal" in combined_source
        ),
        "aft_reference": (
            "aft" in combined_source
        ),
        "survival_reference": (
            "survival" in combined_source
        ),
        "duration_reference": (
            "duration" in combined_source
        ),
        "event_reference": (
            "event" in combined_source
        ),
        "censor_reference": (
            "censor" in combined_source
        ),
        "right_censor_reference": (
            "right censor" in combined_source
            or "right_censored" in combined_source
            or "right-censor" in combined_source
        ),
        "predict_survival_function_reference": (
            "predict_survival_function"
            in combined_source
        ),
        "predict_expectation_reference": (
            "predict_expectation"
            in combined_source
        ),
        "predict_median_reference": (
            "predict_median"
            in combined_source
        ),
    }

    for key, value in semantic_signals.items():

        print(
            f"  {key}: {value}"
        )

    report["survival_semantic_signals"] = (
        semantic_signals
    )

    # ================================================================
    # 6. Locate serialized model artifacts
    # ================================================================

    print()
    print(
        "[6] Inspecting T7 serialized model artifacts..."
    )

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

    for item in directory_inventory[
        "models"
    ]:

        if item["suffix"] in serialized_suffixes:

            serialized.append(
                item
            )

    print(
        f"Serialized model artifacts: "
        f"{len(serialized)}"
    )

    for item in serialized:

        print(
            f"  - {item['path']} "
            f"({item['size_bytes']} bytes)"
        )

    report["serialized_model_artifacts"] = (
        serialized
    )

    # ================================================================
    # 7. Final resolution
    # ================================================================

    print()
    print(
        "[7] T7 runtime interface resolution summary..."
    )

    print()
    print(
        "  Model family signals:"
    )

    print(
        f"    Log-Normal: "
        f"{semantic_signals['lognormal_reference']}"
    )

    print(
        f"    AFT: "
        f"{semantic_signals['aft_reference']}"
    )

    print()
    print(
        "  Survival semantics:"
    )

    print(
        f"    Event: "
        f"{semantic_signals['event_reference']}"
    )

    print(
        f"    Censoring: "
        f"{semantic_signals['censor_reference']}"
    )

    print(
        f"    Right-censoring: "
        f"{semantic_signals['right_censor_reference']}"
    )

    print()
    print(
        "  Runtime prediction interface:"
    )

    print(
        f"    predict_survival_function: "
        f"{semantic_signals['predict_survival_function_reference']}"
    )

    print(
        f"    predict_expectation: "
        f"{semantic_signals['predict_expectation_reference']}"
    )

    print(
        f"    predict_median: "
        f"{semantic_signals['predict_median_reference']}"
    )

    report["resolution_summary"] = {
        "lognormal_reference": semantic_signals[
            "lognormal_reference"
        ],
        "aft_reference": semantic_signals[
            "aft_reference"
        ],
        "event_reference": semantic_signals[
            "event_reference"
        ],
        "censor_reference": semantic_signals[
            "censor_reference"
        ],
        "right_censor_reference": semantic_signals[
            "right_censor_reference"
        ],
        "serialized_model_artifact_count": len(
            serialized
        ),
    }

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
        "OP-018R22 INSPECTION COMPLETE"
    )
    print("=" * 72)

    print(
        f"Output: {OUTPUT_PATH}"
    )

    print()
    print("No model fitting performed.")
    print("No artifact modification performed.")
    print("No evaluation performed.")
    print("No locked test population used.")
    print("No runtime prediction performed.")

    print("=" * 72)


if __name__ == "__main__":
    main()