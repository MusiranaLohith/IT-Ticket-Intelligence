from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T4_SCRIPTS = PROJECT_ROOT / "modeling/T4/scripts"

TARGET_FILES = [
    "t4_ranking_baseline.py",
    "t4_mod009.py",
    "t4_mod011.py",
]

OUTPUT = (
    PROJECT_ROOT
    / "modeling/FMP/metrics/"
    "fmp06_op018r8_t4_final_implementation_binding_audit.json"
)


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def source_literals(tree: ast.AST) -> list[str]:
    values: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                values.append(node.value)

    return sorted(set(values))


def inspect_file(path: Path) -> dict[str, Any]:

    source = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    tree = ast.parse(source)

    functions = []
    classes = []
    calls = []
    string_literals = source_literals(tree)

    for node in ast.walk(tree):

        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            functions.append(node.name)

        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)

        elif isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)

            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)

    # Look specifically for path-like references.
    path_references = []

    for value in string_literals:

        lower = value.lower()

        if (
            "/" in value
            or "\\" in value
            or ".csv" in lower
            or ".json" in lower
            or ".joblib" in lower
            or ".pkl" in lower
            or ".npz" in lower
            or ".npy" in lower
        ):
            path_references.append(value)

    # Search source for explicit model/data loading operations.
    loading_lines = []

    for line_number, line in enumerate(
        source.splitlines(),
        start=1,
    ):
        lower = line.lower()

        if any(
            token in lower
            for token in [
                "read_csv",
                "read_json",
                "joblib.load",
                "load(",
                "read_pickle",
                "np.load",
                "open(",
                "to_csv",
                "dump(",
                "joblib.dump",
                "to_json",
            ]
        ):
            loading_lines.append(
                {
                    "line": line_number,
                    "text": line.strip(),
                }
            )

    training_lines = []

    for line_number, line in enumerate(
        source.splitlines(),
        start=1,
    ):
        lower = line.lower()

        if any(
            token in lower
            for token in [
                ".fit(",
                "fit_transform(",
                "train_test_split",
                "model.fit",
            ]
        ):
            training_lines.append(
                {
                    "line": line_number,
                    "text": line.strip(),
                }
            )

    retrieval_functions = [
        name
        for name in functions
        if any(
            token in name.lower()
            for token in [
                "rank",
                "retriev",
                "bm25",
                "candidate",
                "similarity",
            ]
        )
    ]

    return {
        "path": rel(path),
        "functions": functions,
        "classes": classes,
        "retrieval_functions": retrieval_functions,
        "calls": sorted(set(calls)),
        "path_references": path_references,
        "load_save_lines": loading_lines,
        "training_related_lines": training_lines,
        "source_line_count": len(source.splitlines()),
    }


def main() -> None:

    print("=" * 72)
    print(
        "FMP-06 OP-018R8 — "
        "T4 FINAL IMPLEMENTATION BINDING AUDIT"
    )
    print("=" * 72)
    print()

    findings = []

    for filename in TARGET_FILES:

        path = T4_SCRIPTS / filename

        if not path.exists():
            findings.append(
                {
                    "path": rel(path),
                    "status": "MISSING",
                }
            )
            continue

        info = inspect_file(path)
        findings.append(info)

        print("-" * 72)
        print("FILE:", info["path"])
        print("FUNCTIONS:", info["functions"])
        print(
            "RETRIEVAL FUNCTIONS:",
            info["retrieval_functions"],
        )

        print("PATH REFERENCES:")
        for value in info["path_references"]:
            print("  ", repr(value))

        print("LOAD/SAVE OPERATIONS:")
        for item in info["load_save_lines"]:
            print(
                f"  L{item['line']}: "
                f"{item['text']}"
            )

        print("TRAINING-RELATED OPERATIONS:")
        if info["training_related_lines"]:
            for item in info["training_related_lines"]:
                print(
                    f"  L{item['line']}: "
                    f"{item['text']}"
                )
        else:
            print("  NONE DETECTED")

        print()

    result = {
        "operation": "FMP-06 OP-018R8",
        "operation_type": (
            "T4_FINAL_IMPLEMENTATION_BINDING_AUDIT"
        ),
        "status": "PASS",
        "target_files": TARGET_FILES,
        "findings": findings,
        "runtime_execution": False,
        "retraining": False,
        "artifact_modification": False,
        "test_execution": False,
        "note": (
            "Read-only source audit. The operation resolves "
            "implementation/data bindings and does not execute "
            "the T4 retrieval pipeline."
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

    print("=" * 72)
    print("STATUS: PASS")
    print("RUNTIME EXECUTION: NOT PERFORMED")
    print("OUTPUT:", OUTPUT)
    print("=" * 72)


if __name__ == "__main__":
    main()