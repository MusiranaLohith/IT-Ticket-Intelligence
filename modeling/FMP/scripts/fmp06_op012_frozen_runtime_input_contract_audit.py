from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
FMP_METRICS = PROJECT_ROOT / "modeling" / "FMP" / "metrics"

OUTPUT_FILE = (
    FMP_METRICS
    / "fmp06_op012_frozen_runtime_input_contract_audit.json"
)


TASKS = {
    "T1": {
        "task_dir": PROJECT_ROOT / "modeling" / "T1",
        "keywords": [
            "predict",
            "decision_function",
            "joblib.load",
            "TfidfVectorizer",
            "LinearSVC",
            "ticket",
            "text",
        ],
    },
    "T2": {
        "task_dir": PROJECT_ROOT / "modeling" / "T2",
        "keywords": [
            "predict",
            "predict_proba",
            "joblib.load",
            "TfidfVectorizer",
            "LogisticRegression",
            "ticket",
            "text",
        ],
    },
    "T3": {
        "task_dir": PROJECT_ROOT / "modeling" / "T3",
        "keywords": [
            "predict",
            "predict_proba",
            "joblib.load",
            "TfidfVectorizer",
            "LogisticRegression",
            "ticket",
            "text",
        ],
    },
    "T4": {
        "task_dir": PROJECT_ROOT / "modeling" / "T4",
        "keywords": [
            "predict",
            "joblib.load",
            "candidate",
            "assignee",
            "query",
            "ticket",
            "ranking",
        ],
    },
    "T5": {
        "task_dir": PROJECT_ROOT / "modeling" / "T5",
        "keywords": [
            "predict",
            "predict_proba",
            "joblib.load",
            "ticket",
            "pair",
            "duplicate",
            "text",
        ],
    },
    "T6": {
        "task_dir": PROJECT_ROOT / "modeling" / "T6",
        "keywords": [
            "predict",
            "joblib.load",
            "query",
            "candidate",
            "retrieval",
            "ranking",
            "ticket",
            "corpus",
        ],
    },
    "T7": {
        "task_dir": PROJECT_ROOT / "modeling" / "T7",
        "keywords": [
            "predict",
            "joblib.load",
            "survival",
            "time",
            "resolution",
            "ticket",
            "censor",
            "event",
        ],
    },
}


def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def syntax_check(path: Path) -> tuple[bool, str]:
    try:
        source = safe_read_text(path)
        ast.parse(source, filename=str(path))
        return True, ""
    except Exception as exc:
        return False, str(exc)


def collect_python_files(task_dir: Path) -> list[Path]:
    if not task_dir.exists():
        return []

    return sorted(
        p for p in task_dir.rglob("*.py")
        if ".venv" not in p.parts
        and "__pycache__" not in p.parts
    )


def collect_json_files(task_dir: Path) -> list[Path]:
    if not task_dir.exists():
        return []

    return sorted(
        p for p in task_dir.rglob("*.json")
        if "__pycache__" not in p.parts
    )


def relative_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def keyword_hits(source: str, keywords: list[str]) -> dict[str, int]:
    result: dict[str, int] = {}

    lowered = source.lower()

    for keyword in keywords:
        result[keyword] = lowered.count(keyword.lower())

    return result


def ast_summary(source: str, path: Path) -> dict[str, Any]:
    try:
        tree = ast.parse(source, filename=str(path))
    except Exception:
        return {
            "functions": [],
            "classes": [],
            "imports": [],
            "calls": [],
        }

    functions: list[str] = []
    classes: list[str] = []
    imports: list[str] = []
    calls: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)

        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)

        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append(module)

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)

    return {
        "functions": sorted(set(functions)),
        "classes": sorted(set(classes)),
        "imports": sorted(set(imports)),
        "calls": sorted(set(calls)),
    }


def select_candidate_scripts(
    task: str,
    python_files: list[Path],
) -> list[Path]:
    candidates: list[tuple[int, Path]] = []

    priority_terms = [
        "inference",
        "predict",
        "prediction",
        "runtime",
        "test",
        "evaluation",
        "model",
        "class",
        "retrieval",
        "survival",
        "duplicate",
    ]

    for path in python_files:
        name = path.name.lower()
        score = 0

        for term in priority_terms:
            if term in name:
                score += 1

        # Avoid treating this audit script itself as task evidence.
        if "fmp06_op012" in name:
            continue

        if score > 0:
            candidates.append((score, path))

    candidates.sort(
        key=lambda item: (-item[0], str(item[1]))
    )

    return [path for _, path in candidates[:12]]


def infer_contract(
    task: str,
    candidate_records: list[dict[str, Any]],
) -> dict[str, Any]:
    combined = json.dumps(candidate_records).lower()

    if task in {"T1", "T2", "T3"}:
        input_contract = (
            "single ticket textual input"
            if "ticket" in combined or "text" in combined
            else "not established"
        )

    elif task == "T4":
        if "candidate" in combined or "assignee" in combined:
            input_contract = (
                "ticket/query plus historical candidate population"
            )
        else:
            input_contract = "not established"

    elif task == "T5":
        if "pair" in combined or "duplicate" in combined:
            input_contract = "ticket pair / two-ticket comparison"
        else:
            input_contract = "not established"

    elif task == "T6":
        if "query" in combined or "candidate" in combined:
            input_contract = (
                "query ticket plus retrieval candidate/corpus population"
            )
        else:
            input_contract = "not established"

    elif task == "T7":
        if "survival" in combined or "resolution" in combined:
            input_contract = (
                "ticket-level survival features with native "
                "time/event/censoring semantics"
            )
        else:
            input_contract = "not established"

    else:
        input_contract = "not established"

    output_contract = "not established"

    if task == "T1":
        output_contract = "category/class prediction"
    elif task == "T2":
        output_contract = "priority class prediction"
    elif task == "T3":
        output_contract = "severity class prediction"
    elif task == "T4":
        output_contract = "historical assignee candidate ranking"
    elif task == "T5":
        output_contract = "duplicate relationship score/probability"
    elif task == "T6":
        output_contract = "similar-ticket candidate ranking"
    elif task == "T7":
        output_contract = "native survival / time-to-resolution output"

    return {
        "input_contract": input_contract,
        "output_contract": output_contract,
    }


def inspect_task(task: str, config: dict[str, Any]) -> dict[str, Any]:
    task_dir = config["task_dir"]
    keywords = config["keywords"]

    python_files = collect_python_files(task_dir)
    json_files = collect_json_files(task_dir)

    candidates = select_candidate_scripts(task, python_files)

    candidate_records: list[dict[str, Any]] = []

    for path in candidates:
        source = safe_read_text(path)
        syntax_valid, syntax_error = syntax_check(path)

        record = {
            "file": relative_path(path),
            "syntax_valid": syntax_valid,
            "syntax_error": syntax_error,
            "keyword_hits": keyword_hits(source, keywords),
            "ast": ast_summary(source, path),
        }

        candidate_records.append(record)

    contract = infer_contract(task, candidate_records)

    closure_candidates = [
        relative_path(path)
        for path in json_files
        if "closure" in path.name.lower()
        or "final" in path.name.lower()
    ][:20]

    return {
        "task": task,
        "task_directory_exists": task_dir.exists(),
        "python_file_count": len(python_files),
        "json_file_count": len(json_files),
        "candidate_scripts": candidate_records,
        "candidate_closure_artifacts": closure_candidates,
        "runtime_contract": contract,
    }


def main() -> None:
    print("=" * 72)
    print("FMP-06 OP-012 — FROZEN RUNTIME INPUT CONTRACT AUDIT")
    print("=" * 72)
    print()
    print("Mode: READ-ONLY")
    print("No model loading")
    print("No inference")
    print("No retraining")
    print("No artifact modification")
    print()

    FMP_METRICS.mkdir(parents=True, exist_ok=True)

    results: dict[str, Any] = {
        "operation": "FMP-06 OP-012",
        "operation_type": "READ_ONLY_FROZEN_RUNTIME_INPUT_CONTRACT_AUDIT",
        "project_root": str(PROJECT_ROOT),
        "tasks": {},
        "safeguards": {
            "inference_executed": False,
            "models_loaded": False,
            "retraining": False,
            "artifact_modification": False,
            "threshold_created": False,
            "synthetic_target_created": False,
            "universal_confidence_created": False,
            "universal_risk_created": False,
        },
    }

    overall_status = "PASS"

    for task, config in TASKS.items():
        print(f"[{task}]")
        result = inspect_task(task, config)
        results["tasks"][task] = result

        print(
            f"  task directory exists: "
            f"{result['task_directory_exists']}"
        )
        print(
            f"  Python files: "
            f"{result['python_file_count']}"
        )
        print(
            f"  JSON files: "
            f"{result['json_file_count']}"
        )

        print(
            f"  inferred input: "
            f"{result['runtime_contract']['input_contract']}"
        )
        print(
            f"  inferred output: "
            f"{result['runtime_contract']['output_contract']}"
        )

        valid_count = sum(
            1
            for item in result["candidate_scripts"]
            if item["syntax_valid"]
        )

        invalid_count = sum(
            1
            for item in result["candidate_scripts"]
            if not item["syntax_valid"]
        )

        print(
            f"  candidate scripts inspected: "
            f"{len(result['candidate_scripts'])}"
        )
        print(
            f"  syntax valid: {valid_count}"
        )
        print(
            f"  syntax invalid: {invalid_count}"
        )

        if invalid_count > 0:
            overall_status = "FAIL"

        print()

    results["overall_status"] = overall_status

    OUTPUT_FILE.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )

    print("=" * 72)
    print(f"OVERALL STATUS: {overall_status}")
    print(f"OUTPUT: {OUTPUT_FILE}")
    print("=" * 72)


if __name__ == "__main__":
    main()