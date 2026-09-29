from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T4_ROOT = PROJECT_ROOT / "modeling/T4"

OUTPUT = (
    PROJECT_ROOT
    / "modeling/FMP/metrics/"
    "fmp06_op018r7_t4_implementation_locator.json"
)


KEYWORDS = {
    "retrieval",
    "retrieve",
    "tfidf",
    "bm25",
    "assignee",
    "candidate",
    "cosine",
    "similarity",
    "rank",
    "topk",
}


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def inspect_python(path: Path) -> dict[str, Any]:
    source = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    result: dict[str, Any] = {
        "path": rel(path),
        "size_bytes": path.stat().st_size,
        "functions": [],
        "classes": [],
        "imports": [],
        "keyword_hits": [],
    }

    try:
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            ):
                result["functions"].append(node.name)

            elif isinstance(node, ast.ClassDef):
                result["classes"].append(node.name)

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    result["imports"].append(node.module)

    except SyntaxError as exc:
        result["parse_error"] = str(exc)

    lower_source = source.lower()

    for keyword in sorted(KEYWORDS):
        if keyword in lower_source:
            result["keyword_hits"].append(keyword)

    return result


def main() -> None:

    print("=" * 72)
    print(
        "FMP-06 OP-018R7 — "
        "T4 IMPLEMENTATION LOCATOR"
    )
    print("=" * 72)
    print()

    if not T4_ROOT.exists():
        raise FileNotFoundError(
            f"T4 directory not found: {T4_ROOT}"
        )

    python_files = sorted(
        T4_ROOT.rglob("*.py")
    )

    print(
        "T4 ROOT:",
        rel(T4_ROOT),
    )

    print(
        "PYTHON FILES FOUND:",
        len(python_files),
    )
    print()

    candidates = []

    for path in python_files:

        info = inspect_python(path)

        # Keep files that either expose executable structure
        # or contain vocabulary strongly associated with the
        # T4 retrieval implementation.
        if (
            info["functions"]
            or info["classes"]
            or info["keyword_hits"]
        ):
            candidates.append(info)

    print(
        "IMPLEMENTATION CANDIDATES:",
        len(candidates),
    )
    print()

    for item in candidates:
        print("-" * 72)
        print("FILE:", item["path"])
        print("FUNCTIONS:", item["functions"])
        print("CLASSES:", item["classes"])
        print("IMPORTS:", item["imports"][:20])
        print("KEYWORD HITS:", item["keyword_hits"])

        if "parse_error" in item:
            print("PARSE ERROR:", item["parse_error"])

    result = {
        "operation": "FMP-06 OP-018R7",
        "operation_type": "T4_IMPLEMENTATION_LOCATOR",
        "status": "PASS",
        "t4_root": rel(T4_ROOT),
        "python_files_found": len(python_files),
        "implementation_candidates": candidates,
        "runtime_executed": False,
        "retraining": False,
        "artifact_modification": False,
        "test_execution": False,
        "note": (
            "Read-only source discovery. This operation does not "
            "execute T4 retrieval and does not modify artifacts."
        ),
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            result,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 72)
    print("STATUS: PASS")
    print("RUNTIME EXECUTION: NOT PERFORMED")
    print("OUTPUT:", OUTPUT)
    print("=" * 72)


if __name__ == "__main__":
    main()