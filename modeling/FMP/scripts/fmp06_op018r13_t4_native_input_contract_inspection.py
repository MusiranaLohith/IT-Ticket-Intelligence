from pathlib import Path
import json
import ast
import pandas as pd


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T4_ROOT = ROOT / "modeling" / "T4"
T4_TRAIN = T4_ROOT / "derived" / "t4_train.csv"

OUTPUT = (
    ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "fmp06_op018r13_t4_native_input_contract_inspection.json"
)


def safe_read_text(path: Path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return f"<<READ_ERROR: {type(exc).__name__}: {exc}>>"


def extract_function_source(source: str, function_names):
    results = {}

    try:
        tree = ast.parse(source)
    except Exception as exc:
        return {
            "parse_error": f"{type(exc).__name__}: {exc}"
        }

    lines = source.splitlines()

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in function_names:
                start = node.lineno
                end = getattr(node, "end_lineno", node.lineno)

                results[node.name] = "\n".join(
                    lines[start - 1:end]
                )

    return results


def main():

    print("=" * 72)
    print("FMP-06 OP-018R13 — T4 NATIVE INPUT CONTRACT INSPECTION")
    print("=" * 72)

    print()
    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Evaluation metrics: NO")
    print("Locked test population: NO")
    print("Artifact modification: NO")
    print()

    report = {
        "operation": "FMP-06 OP-018R13",
        "operation_name": "T4 native input contract inspection",
        "read_only": True,
        "training_or_fitting": False,
        "evaluation": False,
        "locked_test_used": False,
        "artifact_modified": False,
        "t4_train": {},
        "implementation_sources": [],
        "function_sources": {},
        "relevant_source_hits": [],
    }

    # ------------------------------------------------------------
    # 1. Inspect actual T4 training/source CSV
    # ------------------------------------------------------------

    print("[1] Inspecting T4 training/source population...")

    if not T4_TRAIN.exists():
        print(f"ERROR: Missing file: {T4_TRAIN}")

        report["t4_train"]["status"] = "MISSING"
        report["status"] = "BLOCKED"

        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(
            json.dumps(report, indent=2),
            encoding="utf-8"
        )

        raise SystemExit(1)

    df = pd.read_csv(T4_TRAIN, nrows=5)

    print(f"Source: {T4_TRAIN}")
    print(f"Columns ({len(df.columns)}):")
    for col in df.columns:
        print(f"  - {col}")

    print()
    print("First 5 rows / values:")
    print(df.to_string(index=False))

    report["t4_train"] = {
        "path": str(T4_TRAIN),
        "columns": [str(c) for c in df.columns],
        "column_count": int(len(df.columns)),
        "sample_rows": df.astype(object).where(
            pd.notna(df), None
        ).to_dict(orient="records"),
    }

    # ------------------------------------------------------------
    # 2. Locate T4 Python implementation files
    # ------------------------------------------------------------

    print()
    print("[2] Locating T4 implementation source files...")

    python_files = sorted(T4_ROOT.rglob("*.py"))

    print(f"Python files found: {len(python_files)}")

    for path in python_files:
        rel = path.relative_to(ROOT)
        print(f"  - {rel}")

        report["implementation_sources"].append(
            str(rel)
        )

    # ------------------------------------------------------------
    # 3. Inspect likely implementation files
    # ------------------------------------------------------------

    print()
    print("[3] Inspecting source for native text/preprocessing logic...")

    target_functions = {
        "build_text",
        "validate_data",
        "rank_assignees",
        "rank_assignees_for_row",
        "prepare_text",
        "preprocess_text",
        "clean_text",
        "make_text",
        "construct_text",
    }

    search_terms = [
        "build_text",
        "summary",
        "description",
        "description_clean",
        "text",
        "TfidfVectorizer",
        "NearestNeighbors",
        "fit_transform",
        "transform",
        "train_text",
        "eval_text",
        "rank_assignees",
        "rank_assignees_for_row",
    ]

    for path in python_files:

        source = safe_read_text(path)

        if source.startswith("<<READ_ERROR"):
            continue

        functions = extract_function_source(
            source,
            target_functions
        )

        if functions:
            rel = str(path.relative_to(ROOT))

            print()
            print("-" * 72)
            print(f"SOURCE: {rel}")
            print("-" * 72)

            report["function_sources"][rel] = functions

            for function_name, function_source in functions.items():
                print()
                print(f"[FUNCTION: {function_name}]")
                print(function_source)

        for term in search_terms:
            if term in source:
                rel = str(path.relative_to(ROOT))

                report["relevant_source_hits"].append({
                    "file": rel,
                    "term": term,
                })

    # Remove duplicate source hits
    unique_hits = []
    seen = set()

    for hit in report["relevant_source_hits"]:
        key = (hit["file"], hit["term"])

        if key not in seen:
            seen.add(key)
            unique_hits.append(hit)

    report["relevant_source_hits"] = unique_hits

    # ------------------------------------------------------------
    # 4. Print concise source-hit summary
    # ------------------------------------------------------------

    print()
    print("[4] Relevant source-hit summary...")

    by_file = {}

    for hit in unique_hits:
        by_file.setdefault(hit["file"], []).append(hit["term"])

    for file_name in sorted(by_file):
        print()
        print(f"{file_name}")

        for term in sorted(set(by_file[file_name])):
            print(f"  -> {term}")

    # ------------------------------------------------------------
    # 5. Preliminary status
    # ------------------------------------------------------------

    report["status"] = "INSPECTION_COMPLETE"

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print()
    print("=" * 72)
    print("OP-018R13 INSPECTION COMPLETE")
    print("=" * 72)
    print(f"Output: {OUTPUT}")
    print()
    print("No model fitting performed.")
    print("No artifact modification performed.")
    print("No evaluation performed.")
    print("No locked test population used.")
    print("=" * 72)


if __name__ == "__main__":
    main()