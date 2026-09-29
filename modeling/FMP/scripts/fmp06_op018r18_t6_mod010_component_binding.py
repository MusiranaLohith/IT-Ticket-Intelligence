from pathlib import Path
import json
import ast
import re


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T6_ROOT = ROOT / "modeling/T6"

OUTPUT = (
    ROOT
    / "modeling/FMP/metrics/"
    / "fmp06_op018r18_t6_mod010_component_binding.json"
)


TARGET_FILES = [
    T6_ROOT / "scripts/t6_mod010_corrected_hybrid_reconstruction.py",
    T6_ROOT / "scripts/t6_mod010_exact_tfidf_reproduction.py",
    T6_ROOT / "scripts/t6_mod010_final_hybrid_comparison.py",
    T6_ROOT / "scripts/t6_mod010_inspect_artifact_schemas.py",
    T6_ROOT / "scripts/t6_final_model_selection_and_closure.py",
]

SEARCH_TERMS = [
    "TfidfVectorizer",
    "SentenceTransformer",
    "sentence_transformers",
    "embedding",
    "encode",
    "cosine_similarity",
    "semantic_score",
    "tfidf_score",
    "hybrid_score",
    "tfidf_weight",
    "semantic_weight",
    "0.5",
    "normalize",
    "MinMaxScaler",
    "RobustScaler",
    "fit",
    "fit_transform",
    "transform",
    "joblib",
    "load",
    "dump",
    "model",
    "artifact",
    "MOD-010",
]


def safe_read(path):
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


def extract_functions(source):
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
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        start = node.lineno
        end = getattr(
            node,
            "end_lineno",
            node.lineno,
        )

        # Capture functions that are likely relevant
        # to the final runtime construction.
        name = node.name.lower()

        keywords = [
            "build",
            "text",
            "tfidf",
            "semantic",
            "embedding",
            "hybrid",
            "normalize",
            "score",
            "retrieve",
            "reconstruct",
            "load",
            "model",
        ]

        if any(
            keyword in name
            for keyword in keywords
        ):
            results[node.name] = "\n".join(
                lines[start - 1:end]
            )

    return results


def main():

    print("=" * 72)
    print(
        "FMP-06 OP-018R18 — "
        "T6 FINAL MOD-010 COMPONENT BINDING"
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
        "operation": "FMP-06 OP-018R18",
        "operation_name": (
            "T6 final MOD-010 component binding"
        ),
        "read_only": True,
        "training_or_fitting": False,
        "evaluation_metrics": False,
        "locked_test_used": False,
        "artifact_modified": False,
        "files": {},
        "search_hits": [],
        "function_sources": {},
        "candidate_artifacts": [],
        "candidate_data_sources": [],
    }

    # ------------------------------------------------------------
    # 1. Inspect exact final T6 source files
    # ------------------------------------------------------------

    print("[1] Inspecting final T6 source files...")

    for path in TARGET_FILES:

        print()
        print("-" * 72)
        print(
            f"SOURCE: {path.relative_to(ROOT)}"
        )
        print("-" * 72)

        if not path.exists():

            print("MISSING")

            report["files"][
                str(path.relative_to(ROOT))
            ] = {
                "status": "MISSING"
            }

            continue

        source = safe_read(path)

        relative = str(
            path.relative_to(ROOT)
        )

        report["files"][relative] = {
            "status": "READABLE"
        }

        functions = extract_functions(
            source
        )

        if functions:

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

                report["search_hits"].append(
                    {
                        "file": relative,
                        "term": term,
                    }
                )

    # ------------------------------------------------------------
    # 2. Inspect all serialized artifacts
    # ------------------------------------------------------------

    print()
    print(
        "[2] Inspecting T6 serialized artifacts..."
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

    artifacts = sorted(
        path
        for path in T6_ROOT.rglob("*")
        if (
            path.is_file()
            and path.suffix.lower()
            in artifact_suffixes
        )
    )

    print(
        f"Serialized artifacts found: "
        f"{len(artifacts)}"
    )

    for path in artifacts:

        relative = str(
            path.relative_to(ROOT)
        )

        size = path.stat().st_size

        print(
            f"  - {relative} "
            f"({size} bytes)"
        )

        report["candidate_artifacts"].append(
            {
                "path": relative,
                "size_bytes": int(size),
            }
        )

    # ------------------------------------------------------------
    # 3. Inspect T6 data sources relevant to final runtime
    # ------------------------------------------------------------

    print()
    print(
        "[3] Inspecting T6 final runtime data sources..."
    )

    data_candidates = []

    for path in sorted(
        T6_ROOT.rglob("*")
    ):

        if not path.is_file():
            continue

        if path.suffix.lower() not in {
            ".csv",
            ".json",
            ".npz",
        }:
            continue

        name = path.name.lower()

        if any(
            token in name
            for token in [
                "train",
                "eval",
                "query",
                "candidate",
                "mod010",
                "hybrid",
                "closure",
            ]
        ):
            data_candidates.append(
                path
            )

    for path in data_candidates:

        relative = str(
            path.relative_to(ROOT)
        )

        print(
            f"  - {relative}"
        )

        report[
            "candidate_data_sources"
        ].append(
            relative
        )

    # ------------------------------------------------------------
    # 4. De-duplicate search hits
    # ------------------------------------------------------------

    unique_hits = []
    seen = set()

    for hit in report["search_hits"]:

        key = (
            hit["file"],
            hit["term"],
        )

        if key in seen:
            continue

        seen.add(key)
        unique_hits.append(hit)

    report["search_hits"] = unique_hits

    # ------------------------------------------------------------
    # 5. Print concise search summary
    # ------------------------------------------------------------

    print()
    print(
        "[4] Relevant MOD-010 source-hit summary..."
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
    # 6. Extract explicit numeric weights from source
    # ------------------------------------------------------------

    print()
    print(
        "[5] Searching for explicit fusion weights..."
    )

    weight_patterns = [
        r"tfidf_weight\s*=\s*([0-9.]+)",
        r"semantic_weight\s*=\s*([0-9.]+)",
        r"lexical_weight\s*=\s*([0-9.]+)",
        r"weights?\s*=\s*\[([^\]]+)\]",
    ]

    weight_matches = []

    for relative, file_info in report[
        "files"
    ].items():

        path = ROOT / relative

        if not path.exists():
            continue

        source = safe_read(path)

        for pattern in weight_patterns:

            matches = re.findall(
                pattern,
                source,
                flags=re.IGNORECASE,
            )

            for match in matches:

                weight_matches.append(
                    {
                        "file": relative,
                        "pattern": pattern,
                        "match": match,
                    }
                )

    for match in weight_matches:

        print(
            f"{match['file']}: "
            f"{match['match']}"
        )

    report[
        "explicit_weight_matches"
    ] = weight_matches

    # ------------------------------------------------------------
    # 7. Final inspection status
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
    print("OP-018R18 INSPECTION COMPLETE")
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