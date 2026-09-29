from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T6_ROOT = ROOT / "modeling" / "T6"
SCRIPT_DIR = T6_ROOT / "scripts"
MODEL_DIR = T6_ROOT / "models"
METRICS_DIR = T6_ROOT / "metrics"


SOURCE_FILES = [
    SCRIPT_DIR / "t6_mod009_hybrid_lexical_semantic_retrieval.py",
    SCRIPT_DIR / "t6_mod008_semantic_failure_retrieval.py",
    SCRIPT_DIR / "t6_mod010_corrected_hybrid_reconstruction.py",
    SCRIPT_DIR / "t6_final_model_selection_and_closure.py",
]


SEARCH_TERMS = [
    "all-MiniLM-L6-v2",
    "SentenceTransformer",
    "sentence_transformers",
    "encode",
    "embedding",
    "embeddings",
    "semantic",
    "cosine",
    "similarity",
    "semantic_score",
    "model_name",
    "model_path",
    "checkpoint",
    "transformer",
    "torch",
    "faiss",
    "joblib",
    "pickle",
    "dump",
    "load",
    "np.save",
    "np.load",
    "semantic_weight",
]


ARTIFACT_TERMS = [
    "embedding",
    "semantic",
    "mod009",
    "hybrid",
    "similarity",
    "score",
    "retrieval",
    "sentence",
    "transformer",
    "model",
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
    output = {}

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
                "semantic",
                "embedding",
                "encode",
                "similar",
                "score",
                "model",
                "retriev",
                "hybrid",
                "load",
            )
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


def locate_candidate_artifacts() -> list[dict]:
    results = []

    for root in [
        T6_ROOT,
    ]:
        if not root.exists():
            continue

        for path in root.rglob("*"):

            if not path.is_file():
                continue

            lowered = path.name.lower()

            if not any(
                term in lowered
                for term in ARTIFACT_TERMS
            ):
                continue

            try:
                size = path.stat().st_size
            except OSError:
                continue

            results.append(
                {
                    "path": str(
                        path.relative_to(ROOT)
                    ),
                    "size_bytes": size,
                    "suffix": path.suffix.lower(),
                }
            )

    return sorted(
        results,
        key=lambda item: item["path"],
    )


def main() -> None:

    print("=" * 72)
    print(
        "FMP-06 OP-018R20 — "
        "T6 MOD-009 SEMANTIC RUNTIME BINDING"
    )
    print("=" * 72)

    print()
    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Evaluation metrics: NO")
    print("Locked test population: NO")
    print("Artifact modification: NO")

    report = {
        "operation": "FMP-06 OP-018R20",
        "status": "PASS",
        "read_only": True,
        "training_performed": False,
        "evaluation_performed": False,
        "locked_test_used": False,
        "artifact_modified": False,
        "sources": {},
        "candidate_artifacts": [],
    }

    print()
    print("[1] Inspecting MOD-009 / semantic source files...")

    for path in SOURCE_FILES:

        print()
        print("-" * 72)
        print(
            f"SOURCE: {path.relative_to(ROOT)}"
        )
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

        lines = matching_lines(text)
        functions = relevant_functions(path)

        print(
            f"Size: {path.stat().st_size} bytes"
        )

        print()
        print("Matching source lines:")

        if lines:

            for line in lines:
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

        report["sources"][
            str(path.relative_to(ROOT))
        ] = {
            "exists": True,
            "size_bytes": path.stat().st_size,
            "matching_lines": lines,
            "relevant_functions": functions,
        }

    print()
    print("[2] Locating candidate semantic/MOD-009 artifacts...")

    artifacts = locate_candidate_artifacts()

    report["candidate_artifacts"] = artifacts

    print(
        f"Candidate artifacts found: "
        f"{len(artifacts)}"
    )

    for item in artifacts:

        print(
            f"  - {item['path']} "
            f"({item['size_bytes']} bytes)"
        )

    print()
    print("[3] Inspecting T6 model directory...")

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
        f"T6 model files: "
        f"{len(model_files)}"
    )

    for item in model_files:

        print(
            f"  - {item['path']} "
            f"({item['size_bytes']} bytes)"
        )

    report["model_directory_files"] = model_files

    print()
    print("[4] Determining MOD-009 semantic runtime signals...")

    combined = json.dumps(
        report["sources"],
        ensure_ascii=False,
    ).lower()

    signals = {
        "all_minilm_l6_v2_reference": (
            "all-minilm-l6-v2" in combined
        ),
        "sentence_transformers_reference": (
            "sentence_transformers" in combined
            or "sentencetransformer" in combined
        ),
        "encode_reference": (
            "encode" in combined
        ),
        "embedding_reference": (
            "embedding" in combined
        ),
        "cosine_reference": (
            "cosine" in combined
        ),
        "semantic_score_reference": (
            "semantic_score" in combined
        ),
        "serialized_semantic_artifact_candidate": any(
            item["path"].lower().endswith(
                (
                    ".joblib",
                    ".pkl",
                    ".pickle",
                    ".pt",
                    ".pth",
                    ".bin",
                    ".safetensors",
                    ".npy",
                    ".npz",
                )
            )
            and any(
                token in item["path"].lower()
                for token in (
                    "semantic",
                    "embedding",
                    "mod009",
                    "sentence",
                    "transformer",
                )
            )
            for item in artifacts
        ),
    }

    for key, value in signals.items():

        print(
            f"  {key}: {value}"
        )

    report["semantic_runtime_signals"] = signals

    print()
    print("=" * 72)
    print("OP-018R20 INSPECTION COMPLETE")
    print("=" * 72)

    output = (
        METRICS_DIR
        / "fmp06_op018r20_t6_mod009_semantic_runtime_binding.json"
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"Output: {output}"
    )

    print()
    print("No model fitting performed.")
    print("No artifact modification performed.")
    print("No evaluation performed.")
    print("No locked test population used.")
    print("=" * 72)


if __name__ == "__main__":
    main()