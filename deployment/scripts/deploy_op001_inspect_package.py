#!/usr/bin/env python3

from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

FMP_ROOT = PROJECT_ROOT / "modeling" / "FMP"
DEPLOYMENT_ROOT = FMP_ROOT / "deployment"
RUNTIME_ROOT = DEPLOYMENT_ROOT / "runtime"

EXPECTED_FILES = [
    DEPLOYMENT_ROOT / "README.md",
    DEPLOYMENT_ROOT / "requirements.txt",
    RUNTIME_ROOT / "ticket_pipeline.py",
    RUNTIME_ROOT / "ticket_explanation.py",
]

REPORT_DIR = FMP_ROOT / "metrics"
REPORT_PATH = REPORT_DIR / "deploy_op001_package_inspection.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            digest.update(chunk)

    return digest.hexdigest()


def file_metadata(path: Path) -> dict:
    if not path.exists():
        return {
            "path": str(path),
            "exists": False,
        }

    stat = path.stat()

    return {
        "path": str(path),
        "exists": True,
        "is_file": path.is_file(),
        "is_directory": path.is_dir(),
        "size_bytes": stat.st_size if path.is_file() else None,
        "modified_time": datetime.fromtimestamp(
            stat.st_mtime
        ).isoformat(),
        "sha256": sha256_file(path) if path.is_file() else None,
    }


def list_tree(root: Path, max_depth: int = 4) -> list[dict]:
    results = []

    if not root.exists():
        return results

    root_parts = len(root.parts)

    for path in sorted(root.rglob("*")):
        try:
            relative_depth = len(path.parts) - root_parts
        except Exception:
            continue

        if relative_depth > max_depth:
            continue

        results.append(
            {
                "path": str(path),
                "relative_path": str(path.relative_to(root)),
                "type": (
                    "directory"
                    if path.is_dir()
                    else "file"
                ),
                "size_bytes": (
                    path.stat().st_size
                    if path.is_file()
                    else None
                ),
            }
        )

    return results


def python_symbols(path: Path) -> dict:
    result = {
        "path": str(path),
        "parsed": False,
        "classes": [],
        "functions": [],
        "imports": [],
        "error": None,
    }

    if not path.exists():
        result["error"] = "FILE_NOT_FOUND"
        return result

    try:
        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        tree = ast.parse(source)

        result["parsed"] = True

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                result["classes"].append(node.name)

            elif isinstance(node, ast.FunctionDef):
                result["functions"].append(node.name)

            elif isinstance(node, ast.AsyncFunctionDef):
                result["functions"].append(
                    f"async:{node.name}"
                )

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""

                for alias in node.names:
                    result["imports"].append(
                        f"{module}.{alias.name}"
                    )

    except Exception as exc:
        result["error"] = repr(exc)

    return result


def read_text_file(path: Path) -> dict:
    if not path.exists():
        return {
            "path": str(path),
            "exists": False,
            "content": None,
        }

    try:
        content = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        return {
            "path": str(path),
            "exists": True,
            "content": content,
        }

    except Exception as exc:
        return {
            "path": str(path),
            "exists": True,
            "content": None,
            "error": repr(exc),
        }


def find_deployment_related_files() -> list[str]:
    candidates = []

    if not PROJECT_ROOT.exists():
        return candidates

    keywords = {
        "fastapi",
        "frontend",
        "dashboard",
        "requirements",
        "docker",
        "compose",
        "api",
        "server",
        "app",
    }

    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file():
            continue

        # Do not descend into large dataset/model directories
        # merely for discovery.
        path_string = str(path)

        if any(
            excluded in path_string
            for excluded in [
                "/Datasets/",
                "/datasets/",
                "/.git/",
                "/node_modules/",
                "/__pycache__/",
            ]
        ):
            continue

        name_lower = path.name.lower()

        if any(keyword in name_lower for keyword in keywords):
            candidates.append(str(path))

    return sorted(set(candidates))


def run_import_probe() -> dict:
    result = {
        "attempted": False,
        "success": False,
        "stdout": "",
        "stderr": "",
        "return_code": None,
    }

    pipeline_path = RUNTIME_ROOT / "ticket_pipeline.py"
    explanation_path = RUNTIME_ROOT / "ticket_explanation.py"

    if not pipeline_path.exists() or not explanation_path.exists():
        result["error"] = (
            "Required packaged runtime files are missing."
        )
        return result

    probe = f"""
import sys
from pathlib import Path

runtime = Path(
    r"{RUNTIME_ROOT}"
)

sys.path.insert(0, str(runtime))

import ticket_pipeline
import ticket_explanation

print("IMPORT ticket_pipeline: PASS")
print("IMPORT ticket_explanation: PASS")

print(
    "ticket_pipeline symbols:",
    sorted(
        name for name in dir(ticket_pipeline)
        if not name.startswith("_")
    )
)

print(
    "ticket_explanation symbols:",
    sorted(
        name for name in dir(ticket_explanation)
        if not name.startswith("_")
    )
)
"""

    result["attempted"] = True

    completed = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )

    result["return_code"] = completed.returncode
    result["stdout"] = completed.stdout
    result["stderr"] = completed.stderr
    result["success"] = completed.returncode == 0

    return result


def main() -> int:
    print("=" * 70)
    print("IT TICKET TRIAGE SYSTEM")
    print("DEPLOY-OP-001 — EXISTING DEPLOYMENT PACKAGE INSPECTION")
    print("=" * 70)

    print()
    print("[1] Project root")
    print(PROJECT_ROOT)

    print()
    print("[2] Deployment root")
    print(DEPLOYMENT_ROOT)

    print()
    print("[3] Runtime root")
    print(RUNTIME_ROOT)

    print()
    print("[4] Expected files")

    expected_metadata = []

    for path in EXPECTED_FILES:
        metadata = file_metadata(path)
        expected_metadata.append(metadata)

        status = "FOUND" if metadata["exists"] else "MISSING"

        print(
            f"  {status}: {path}"
        )

    print()
    print("[5] Deployment tree")

    deployment_tree = list_tree(
        DEPLOYMENT_ROOT,
        max_depth=5,
    )

    if deployment_tree:
        for item in deployment_tree:
            print(
                f"  [{item['type']}] "
                f"{item['relative_path']}"
            )
    else:
        print("  DEPLOYMENT DIRECTORY NOT FOUND")

    print()
    print("[6] Runtime Python symbols")

    pipeline_symbols = python_symbols(
        RUNTIME_ROOT / "ticket_pipeline.py"
    )

    explanation_symbols = python_symbols(
        RUNTIME_ROOT / "ticket_explanation.py"
    )

    print(
        "  ticket_pipeline.py parsed:",
        pipeline_symbols["parsed"],
    )

    print(
        "  Classes:",
        pipeline_symbols["classes"],
    )

    print(
        "  Functions:",
        pipeline_symbols["functions"],
    )

    print(
        "  ticket_explanation.py parsed:",
        explanation_symbols["parsed"],
    )

    print(
        "  Classes:",
        explanation_symbols["classes"],
    )

    print(
        "  Functions:",
        explanation_symbols["functions"],
    )

    print()
    print("[7] README")

    readme = read_text_file(
        DEPLOYMENT_ROOT / "README.md"
    )

    if readme.get("exists"):
        print("  README FOUND")
        print("  Lines:", len(
            readme.get("content", "").splitlines()
        ))
    else:
        print("  README MISSING")

    print()
    print("[8] Requirements")

    requirements = read_text_file(
        DEPLOYMENT_ROOT / "requirements.txt"
    )

    if requirements.get("exists"):
        print("  requirements.txt FOUND")
        print(
            "  Lines:",
            len(
                requirements.get(
                    "content",
                    "",
                ).splitlines()
            ),
        )
    else:
        print("  requirements.txt MISSING")

    print()
    print("[9] Existing deployment/application-related files")

    related_files = find_deployment_related_files()

    if related_files:
        for path in related_files:
            print("  ", path)
    else:
        print("  NONE FOUND")

    print()
    print("[10] Packaged runtime import probe")

    import_probe = run_import_probe()

    if import_probe["success"]:
        print("  RESULT: PASS")
    else:
        print("  RESULT: FAIL")

        if import_probe.get("error"):
            print(
                "  ERROR:",
                import_probe["error"],
            )

    if import_probe.get("stdout"):
        print()
        print("  STDOUT:")
        print(import_probe["stdout"])

    if import_probe.get("stderr"):
        print()
        print("  STDERR:")
        print(import_probe["stderr"])

    report = {
        "operation": "DEPLOY-OP-001",
        "title": (
            "Existing Deployment Package Inspection"
        ),
        "timestamp": datetime.now().isoformat(),
        "project_root": str(PROJECT_ROOT),
        "deployment_root": str(DEPLOYMENT_ROOT),
        "runtime_root": str(RUNTIME_ROOT),
        "read_only": True,
        "expected_files": expected_metadata,
        "deployment_tree": deployment_tree,
        "ticket_pipeline_symbols": pipeline_symbols,
        "ticket_explanation_symbols": explanation_symbols,
        "readme": readme,
        "requirements": requirements,
        "deployment_related_files": related_files,
        "import_probe": import_probe,
    }

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print("[11] Inspection report")
    print(REPORT_PATH)

    print()
    print("=" * 70)
    print("DEPLOY-OP-001 COMPLETE")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())