from __future__ import annotations

import ast
import json
import re
from pathlib import Path


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T6_ROOT = ROOT / "modeling" / "T6"
SCRIPT_DIR = T6_ROOT / "scripts"
MODEL_DIR = T6_ROOT / "models"
METRICS_DIR = T6_ROOT / "metrics"

SOURCE_FILES = [
    SCRIPT_DIR / "t6_mod010_corrected_hybrid_reconstruction.py",
    SCRIPT_DIR / "t6_mod010_final_hybrid_comparison.py",
    SCRIPT_DIR / "t6_mod010_exact_tfidf_reproduction.py",
    SCRIPT_DIR / "t6_mod010_inspect_artifact_schemas.py",
    SCRIPT_DIR / "t6_final_model_selection_and_closure.py",
]


SEARCH_TERMS = [
    "SentenceTransformer",
    "sentence_transformers",
    "SentenceTransformer(",
    "embedding",
    "embeddings",
    "encode",
    "cosine_similarity",
    "semantic_score",
    "semantic_scores",
    "semantic_model",
    "semantic_model_name",
    "model_name",
    "model_path",
    "pretrained",
    "checkpoint",
    "transformer",
    "torch",
    "faiss",
    "normalize",
    "hybrid_score",
    "semantic_weight",
    "tfidf_weight",
]


def read_text(path: Path) -> str:
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def extract_matching_lines(
    text: str,
    terms: list[str],
) -> list[str]:
    matches = []

    for line_number, line in enumerate(
        text.splitlines(),
        start=1,
    ):
        lowered = line.lower()

        if any(
            term.lower() in lowered
            for term in terms
        ):
            matches.append(
                f"{line_number}: {line.rstrip()}"
            )

    return matches


def extract_functions(path: Path) -> dict[str, str]:
    text = read_text(path)

    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return {
            "__SYNTAX_ERROR__": str(exc)
        }

    lines = text.splitlines()

    output = {}

    for node in tree.body:
        if not isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            continue

        function_name = node.name.lower()

        keywords = (
            "semantic",
            "embedding",
            "encode",
            "cosine",
            "model",
            "score",
            "hybrid",
            "load",
            "retrieve",
        )

        if not any(
            keyword in function_name
            for keyword in keywords
        ):
            continue

        start = node.lineno
        end = getattr(
            node,
            "end_lineno",
            node.lineno,
        )

        output[node.name] = "\n".join(
            lines[start - 1:end]
        )

    return output


def find_string_literals(path: Path) -> list[str]:
    text = read_text(path)

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    values = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                value = node.value.strip()

                if not value:
                    continue

                lowered = value.lower()

                if any(
                    token in lowered
                    for token in (
                        "sentence",
                        "transformer",
                        "embedding",
                        "model",
                        "checkpoint",
                        "encoder",
                        "all-",
                    )
                ):
                    values.append(value)

    return sorted(set(values))


def locate_embedding_related_files() -> list[str]:
    matches = []

    search_roots = [
        T6_ROOT,
    ]

    extensions = {
        ".py",
        ".json",
        ".yaml",
        ".yml",
        ".txt",
        ".joblib",
        ".pkl",
        ".pickle",
        ".pt",
        ".pth",
        ".bin",
        ".safetensors",
        ".npz",
        ".npy",
    }

    filename_tokens = (
        "embed",
        "semantic",
        "sentence",
        "transformer",
        "encoder",
        "bert",
        "model",
        "checkpoint",
    )

    for root in search_roots:
        if not root.exists():
            continue

        for path in root.rglob("*"):
            if not path.is_file():
                continue

            if path.suffix.lower() not in extensions:
                continue

            lowered = path.name.lower()

            if any(
                token in lowered
                for token in filename_tokens
            ):
                matches.append(
                    str(path.relative_to(ROOT))
                )

    return sorted(set(matches))


def main() -> None:
    print("=" * 72)
    print(
        "FMP-06 OP-018R19 — "
        "T6 SEMANTIC COMPONENT RESOLUTION"
    )
    print("=" * 72)

    print()
    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Evaluation metrics: NO")
    print("Locked test population: NO")
    print("Artifact modification: NO")

    report = {
        "operation": "FMP-06 OP-018R19",
        "status": "PASS",
        "read_only": True,
        "training_performed": False,
        "evaluation_performed": False,
        "locked_test_used": False,
        "artifact_modified": False,
        "sources": {},
        "embedding_related_files": [],
    }

    print()
    print("[1] Inspecting MOD-010 semantic-related source evidence...")

    for path in SOURCE_FILES:
        print()
        print("-" * 72)
        print(f"SOURCE: {path.relative_to(ROOT)}")
        print("-" * 72)

        if not path.exists():
            print("MISSING")
            report["sources"][
                str(path.relative_to(ROOT))
            ] = {
                "exists": False,
            }
            continue

        text = read_text(path)

        matches = extract_matching_lines(
            text,
            SEARCH_TERMS,
        )

        functions = extract_functions(path)
        literals = find_string_literals(path)

        print(
            f"Size: {path.stat().st_size} bytes"
        )

        print()
        print("Matching source lines:")

        if matches:
            for line in matches:
                print(line)
        else:
            print("  NONE")

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

        print()
        print("Relevant string literals:")

        if literals:
            for value in literals:
                print(f"  {value!r}")
        else:
            print("  NONE")

        report["sources"][
            str(path.relative_to(ROOT))
        ] = {
            "exists": True,
            "size_bytes": path.stat().st_size,
            "matching_lines": matches,
            "relevant_functions": functions,
            "relevant_string_literals": literals,
        }

    print()
    print("[2] Locating embedding/semantic-related files...")

    embedding_files = locate_embedding_related_files()

    report["embedding_related_files"] = embedding_files

    print(
        f"Embedding/semantic-related files found: "
        f"{len(embedding_files)}"
    )

    for relative_path in embedding_files:
        print(
            f"  - {relative_path}"
        )

    print()
    print("[3] Inspecting T6 model directory contents...")

    model_files = []

    if MODEL_DIR.exists():
        for path in sorted(
            MODEL_DIR.rglob("*")
        ):
            if path.is_file():
                model_files.append(
                    {
                        "path": str(
                            path.relative_to(ROOT)
                        ),
                        "size_bytes": path.stat().st_size,
                    }
                )

    print(
        f"T6 model files found: "
        f"{len(model_files)}"
    )

    for item in model_files:
        print(
            f"  - {item['path']} "
            f"({item['size_bytes']} bytes)"
        )

    report["model_directory_files"] = model_files

    print()
    print("[4] Semantic-component determination summary...")

    all_source_text = "\n".join(
        json.dumps(
            value,
            ensure_ascii=False,
        )
        for value in report["sources"].values()
    ).lower()

    semantic_signals = {
        "sentence_transformers_reference": (
            "sentence_transformers" in all_source_text
            or "sentencetransformer" in all_source_text
        ),
        "embedding_reference": (
            "embedding" in all_source_text
        ),
        "encode_reference": (
            "encode" in all_source_text
        ),
        "cosine_similarity_reference": (
            "cosine_similarity" in all_source_text
        ),
        "semantic_score_reference": (
            "semantic_score" in all_source_text
        ),
        "semantic_weight_reference": (
            "semantic_weight" in all_source_text
        ),
    }

    for key, value in semantic_signals.items():
        print(
            f"  {key}: {value}"
        )

    report["semantic_signals"] = semantic_signals

    print()
    print("=" * 72)
    print("OP-018R19 INSPECTION COMPLETE")
    print("=" * 72)

    output_path = (
        METRICS_DIR
        / "fmp06_op018r19_t6_semantic_component_resolution.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"Output: {output_path}"
    )

    print()
    print("No model fitting performed.")
    print("No artifact modification performed.")
    print("No evaluation performed.")
    print("No locked test population used.")
    print("=" * 72)


if __name__ == "__main__":
    main()