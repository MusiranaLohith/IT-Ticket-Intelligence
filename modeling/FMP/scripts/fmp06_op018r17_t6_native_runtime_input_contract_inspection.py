from pathlib import Path
import json
import ast

import pandas as pd


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T6_ROOT = ROOT / "modeling/T6"

OUTPUT = (
    ROOT
    / "modeling/FMP/metrics/"
    / "fmp06_op018r17_t6_native_runtime_input_contract_inspection.json"
)


TARGET_FUNCTIONS = {
    "build_text",
    "make_text",
    "prepare_text",
    "preprocess_text",
    "clean_text",
    "construct_text",
    "build_query_text",
    "build_candidate_text",
    "rank",
    "retrieve",
    "retrieve_candidates",
}


SEARCH_TERMS = [
    "query",
    "candidate",
    "target_observed",
    "target_assignee",
    "text",
    "summary",
    "description",
    "TfidfVectorizer",
    "NearestNeighbors",
    "cosine",
    "fit_transform",
    "transform",
    "semantic",
    "hybrid",
    "embedding",
    "similarity",
    "rank",
]


def safe_read_text(path: Path):
    try:
        return path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except Exception as exc:
        return (
            f"<<READ_ERROR: "
            f"{type(exc).__name__}: {exc}>>"
        )


def extract_functions(source: str):
    results = {}

    try:
        tree = ast.parse(source)
    except Exception as exc:
        return {
            "__parse_error__": (
                f"{type(exc).__name__}: {exc}"
            )
        }

    lines = source.splitlines()

    for node in ast.walk(tree):

        if not isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            continue

        if node.name not in TARGET_FUNCTIONS:
            continue

        start = node.lineno
        end = getattr(
            node,
            "end_lineno",
            node.lineno,
        )

        results[node.name] = "\n".join(
            lines[start - 1:end]
        )

    return results


def inspect_csv(path: Path):

    result = {
        "path": str(path),
        "status": "UNKNOWN",
    }

    try:
        df = pd.read_csv(
            path,
            nrows=5,
        )

        result["status"] = "READABLE"
        result["columns"] = [
            str(c)
            for c in df.columns
        ]
        result["column_count"] = len(
            df.columns
        )
        result["sample_rows"] = (
            df.astype(object)
            .where(
                pd.notna(df),
                None,
            )
            .to_dict(
                orient="records"
            )
        )

        print()
        print(
            f"SOURCE: {path.relative_to(ROOT)}"
        )

        print(
            f"Columns ({len(df.columns)}):"
        )

        for column in df.columns:
            print(f"  - {column}")

    except Exception as exc:

        result["status"] = "READ_ERROR"
        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

    return result


def main():

    print("=" * 72)
    print(
        "FMP-06 OP-018R17 — "
        "T6 NATIVE RUNTIME INPUT CONTRACT INSPECTION"
    )
    print("=" * 72)

    print()
    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Evaluation metrics: NO")
    print("Locked test population: NO")
    print("Artifact modification: NO")
    print()

    report = {
        "operation": "FMP-06 OP-018R17",
        "operation_name": (
            "T6 native runtime input contract inspection"
        ),
        "read_only": True,
        "training_or_fitting": False,
        "evaluation_metrics": False,
        "locked_test_used": False,
        "artifact_modified": False,
        "t6_root": str(T6_ROOT),
        "csv_sources": [],
        "python_sources": [],
        "function_sources": {},
        "source_hits": [],
        "artifact_candidates": [],
    }

    # ------------------------------------------------------------
    # 1. Locate T6 files
    # ------------------------------------------------------------

    print("[1] Locating T6 files...")

    if not T6_ROOT.exists():
        raise FileNotFoundError(
            f"T6 root missing: {T6_ROOT}"
        )

    all_files = sorted(
        path
        for path in T6_ROOT.rglob("*")
        if path.is_file()
    )

    print(
        f"Total T6 files found: {len(all_files)}"
    )

    # ------------------------------------------------------------
    # 2. Inspect CSV sources
    # ------------------------------------------------------------

    print()
    print("[2] Inspecting T6 CSV sources...")

    csv_files = [
        path
        for path in all_files
        if path.suffix.lower() == ".csv"
    ]

    print(
        f"CSV files found: {len(csv_files)}"
    )

    for path in csv_files:

        result = inspect_csv(path)

        report["csv_sources"].append(
            result
        )

    # ------------------------------------------------------------
    # 3. Locate Python implementation files
    # ------------------------------------------------------------

    print()
    print("[3] Locating T6 implementation source...")

    python_files = [
        path
        for path in all_files
        if path.suffix.lower() == ".py"
    ]

    print(
        f"Python files found: {len(python_files)}"
    )

    for path in python_files:

        relative = str(
            path.relative_to(ROOT)
        )

        print(f"  - {relative}")

        report["python_sources"].append(
            relative
        )

    # ------------------------------------------------------------
    # 4. Inspect native functions and source hits
    # ------------------------------------------------------------

    print()
    print(
        "[4] Inspecting native T6 "
        "text/retrieval logic..."
    )

    for path in python_files:

        source = safe_read_text(path)

        if source.startswith(
            "<<READ_ERROR"
        ):
            continue

        relative = str(
            path.relative_to(ROOT)
        )

        functions = extract_functions(
            source
        )

        if functions:

            print()
            print("-" * 72)
            print(
                f"SOURCE: {relative}"
            )
            print("-" * 72)

            report["function_sources"][
                relative
            ] = functions

            for (
                function_name,
                function_source,
            ) in functions.items():

                print()
                print(
                    f"[FUNCTION: "
                    f"{function_name}]"
                )

                print(function_source)

        for term in SEARCH_TERMS:

            if term.lower() in source.lower():

                report["source_hits"].append(
                    {
                        "file": relative,
                        "term": term,
                    }
                )

    # ------------------------------------------------------------
    # 5. Locate serialized/model artifacts
    # ------------------------------------------------------------

    print()
    print(
        "[5] Locating T6 serialized/model artifacts..."
    )

    artifact_suffixes = {
        ".joblib",
        ".pkl",
        ".pickle",
        ".pt",
        ".pth",
        ".bin",
        ".onnx",
        ".npz",
    }

    artifact_files = [
        path
        for path in all_files
        if path.suffix.lower()
        in artifact_suffixes
    ]

    print(
        f"Candidate artifacts: "
        f"{len(artifact_files)}"
    )

    for path in artifact_files:

        relative = str(
            path.relative_to(ROOT)
        )

        size = path.stat().st_size

        print(
            f"  - {relative} "
            f"({size} bytes)"
        )

        report[
            "artifact_candidates"
        ].append(
            {
                "path": relative,
                "size_bytes": int(size),
            }
        )

    # ------------------------------------------------------------
    # 6. De-duplicate source hits
    # ------------------------------------------------------------

    unique_hits = []
    seen = set()

    for hit in report["source_hits"]:

        key = (
            hit["file"],
            hit["term"],
        )

        if key in seen:
            continue

        seen.add(key)
        unique_hits.append(hit)

    report["source_hits"] = unique_hits

    # ------------------------------------------------------------
    # 7. Print source-hit summary
    # ------------------------------------------------------------

    print()
    print(
        "[6] Relevant source-hit summary..."
    )

    grouped = {}

    for hit in unique_hits:

        grouped.setdefault(
            hit["file"],
            [],
        ).append(
            hit["term"]
        )

    for file_name in sorted(grouped):

        print()
        print(file_name)

        for term in sorted(
            set(grouped[file_name])
        ):
            print(
                f"  -> {term}"
            )

    # ------------------------------------------------------------
    # 8. Write report
    # ------------------------------------------------------------

    report["status"] = (
        "INSPECTION_COMPLETE"
    )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 72)
    print("OP-018R17 INSPECTION COMPLETE")
    print("=" * 72)
    print(
        f"Output: {OUTPUT}"
    )
    print()
    print("No model fitting performed.")
    print("No artifact modification performed.")
    print("No evaluation performed.")
    print("No locked test population used.")
    print("=" * 72)


if __name__ == "__main__":
    main()