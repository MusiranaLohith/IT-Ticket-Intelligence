from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T4_CLOSURE = (
    PROJECT_ROOT
    / "modeling/T4/results/t4_mod013_closure.json"
)

T4_RESULTS_DIR = (
    PROJECT_ROOT
    / "modeling/T4/results"
)

OUTPUT = (
    PROJECT_ROOT
    / "modeling/FMP/metrics/"
    "fmp06_op018r6_t4_runtime_interface_probe.json"
)


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def inspect_python_file(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": rel(path),
        "readable": path.exists(),
        "functions": [],
        "classes": [],
        "imports": [],
    }

    if not path.exists():
        return result

    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result["functions"].append(node.name)

        elif isinstance(node, ast.ClassDef):
            result["classes"].append(node.name)

        elif isinstance(node, ast.Import):
            for alias in node.names:
                result["imports"].append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                result["imports"].append(node.module)

    return result


def main() -> None:

    print("=" * 72)
    print(
        "FMP-06 OP-018R6 — "
        "T4 RUNTIME INTERFACE PROBE"
    )
    print("=" * 72)
    print()

    print("Purpose:")
    print(
        "Resolve the frozen T4 retrieval interface before attempting "
        "runtime execution."
    )
    print()

    if not T4_CLOSURE.exists():
        raise FileNotFoundError(
            f"T4 closure not found: {T4_CLOSURE}"
        )

    closure = json.loads(
        T4_CLOSURE.read_text(encoding="utf-8")
    )

    print("T4 CLOSURE:")
    print(json.dumps(closure, indent=2)[:6000])
    print()

    candidate_files = sorted(
        T4_RESULTS_DIR.rglob("*.py")
    )

    python_inventory = []

    for path in candidate_files:
        try:
            python_inventory.append(
                inspect_python_file(path)
            )
        except Exception as exc:
            python_inventory.append(
                {
                    "path": rel(path),
                    "readable": True,
                    "parse_error": str(exc),
                }
            )

    json_inventory = []

    for path in sorted(T4_RESULTS_DIR.rglob("*.json")):
        try:
            payload = json.loads(
                path.read_text(encoding="utf-8")
            )

            json_inventory.append(
                {
                    "path": rel(path),
                    "top_level_type": type(payload).__name__,
                    "top_level_keys": (
                        list(payload.keys())
                        if isinstance(payload, dict)
                        else None
                    ),
                }
            )

        except Exception as exc:
            json_inventory.append(
                {
                    "path": rel(path),
                    "read_error": str(exc),
                }
            )

    print("T4 PYTHON CANDIDATES:")
    for item in python_inventory:
        print(
            f"  {item['path']} "
            f"functions={item.get('functions', [])} "
            f"classes={item.get('classes', [])}"
        )

    print()

    print("T4 JSON ARTIFACTS:")
    for item in json_inventory:
        print(
            f"  {item['path']} "
            f"keys={item.get('top_level_keys')}"
        )

    result = {
        "operation": "FMP-06 OP-018R6",
        "operation_type": (
            "T4_RUNTIME_INTERFACE_RESOLUTION"
        ),
        "status": "PASS",
        "closure": {
            "path": rel(T4_CLOSURE),
            "top_level_keys": list(closure.keys()),
        },
        "results_directory": rel(T4_RESULTS_DIR),
        "python_candidates": python_inventory,
        "json_artifacts": json_inventory,
        "runtime_execution": False,
        "retraining": False,
        "artifact_modification": False,
        "threshold_selection": False,
        "synthetic_input_created": False,
        "synthetic_target_created": False,
        "note": (
            "This operation resolves the T4 runtime interface only. "
            "No T4 inference or retrieval execution is performed."
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