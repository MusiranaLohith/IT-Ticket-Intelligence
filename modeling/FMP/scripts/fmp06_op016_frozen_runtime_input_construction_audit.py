from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OUTPUT = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "fmp06_op016_frozen_runtime_input_construction_audit.json"
)


TASK_DIRS = {
    "T1": PROJECT_ROOT / "modeling" / "T1",
    "T2": PROJECT_ROOT / "modeling" / "T2",
    "T3": PROJECT_ROOT / "modeling" / "T3",
    "T4": PROJECT_ROOT / "modeling" / "T4",
    "T5": PROJECT_ROOT / "modeling" / "T5",
    "T6": PROJECT_ROOT / "modeling" / "T6",
    "T7": PROJECT_ROOT / "modeling" / "T7",
}


TERMS = {
    "text_input": [
        "summary",
        "description",
        "text",
        "title",
        "body",
        "concat",
        "join",
    ],
    "prediction": [
        "predict",
        "predict_proba",
        "decision_function",
    ],
    "model_load": [
        "joblib.load",
        "load(",
        "pickle.load",
    ],
    "vectorizer": [
        "tfidf",
        "vectorizer",
        "transform",
        "fit_transform",
    ],
    "candidate": [
        "candidate",
        "candidates",
        "corpus",
        "retrieval",
        "ranking",
    ],
    "pair": [
        "pair",
        "ticket_a",
        "ticket_b",
        "left",
        "right",
        "duplicate",
    ],
    "survival": [
        "survival",
        "duration",
        "event",
        "time_to_resolution",
        "resolution_time",
        "censor",
        "kaplan",
        "weibull",
        "lognormal",
        "aft",
    ],
    "feature": [
        "feature",
        "features",
        "creation",
        "creator",
        "role",
    ],
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def read_source(path: Path) -> str:
    try:
        return path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except Exception:
        return ""


def syntax_valid(source: str, path: Path) -> tuple[bool, str]:
    try:
        ast.parse(
            source,
            filename=str(path),
        )
        return True, ""
    except Exception as exc:
        return False, str(exc)


def keyword_hits(
    source: str,
) -> dict[str, int]:

    lowered = source.lower()

    return {
        term: sum(
            lowered.count(item.lower())
            for item in values
        )
        for term, values in TERMS.items()
    }


def ast_summary(
    source: str,
    path: Path,
) -> dict[str, Any]:

    try:
        tree = ast.parse(
            source,
            filename=str(path),
        )
    except Exception:
        return {
            "functions": [],
            "classes": [],
            "calls": [],
        }

    functions = []
    classes = []
    calls = []

    for node in ast.walk(tree):

        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            functions.append(node.name)

        elif isinstance(
            node,
            ast.ClassDef,
        ):
            classes.append(node.name)

        elif isinstance(
            node,
            ast.Call,
        ):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)

            elif isinstance(
                node.func,
                ast.Attribute,
            ):
                calls.append(node.func.attr)

    return {
        "functions": sorted(set(functions)),
        "classes": sorted(set(classes)),
        "calls": sorted(set(calls)),
    }


def score_file(
    task: str,
    path: Path,
    source: str,
) -> int:

    name = path.name.lower()
    hits = keyword_hits(source)

    score = 0

    # Strong filename signals.
    filename_terms = {
        "inference": 6,
        "predict": 6,
        "prediction": 5,
        "runtime": 6,
        "test": 3,
        "evaluation": 2,
        "model": 2,
        "retrieval": 5,
        "duplicate": 5,
        "survival": 5,
    }

    for term, weight in filename_terms.items():
        if term in name:
            score += weight

    # Strong implementation signals.
    score += hits["prediction"] * 3
    score += hits["model_load"] * 2
    score += hits["vectorizer"] * 2

    if task in {"T4", "T6"}:
        score += hits["candidate"] * 2

    if task == "T5":
        score += hits["pair"] * 2

    if task == "T7":
        score += hits["survival"] * 2

    return score


def candidate_files(
    task: str,
    task_dir: Path,
) -> list[Path]:

    files = sorted(
        task_dir.rglob("*.py")
    )

    scored = []

    for path in files:

        if "__pycache__" in path.parts:
            continue

        source = read_source(path)

        if not source:
            continue

        score = score_file(
            task,
            path,
            source,
        )

        if score > 0:
            scored.append(
                (score, path)
            )

    scored.sort(
        key=lambda item: (
            -item[0],
            str(item[1]),
        )
    )

    return [
        path
        for _, path in scored[:15]
    ]


def inspect_file(
    task: str,
    path: Path,
) -> dict[str, Any]:

    source = read_source(path)

    valid, error = syntax_valid(
        source,
        path,
    )

    return {
        "file": rel(path),
        "syntax_valid": valid,
        "syntax_error": error,
        "keyword_hits": keyword_hits(source),
        "ast": ast_summary(
            source,
            path,
        ),
        "source_excerpt": [
            line.strip()
            for line in source.splitlines()
            if any(
                term in line.lower()
                for group in TERMS.values()
                for term in group
            )
        ][:40],
    }


def infer_runtime_contract(
    task: str,
    records: list[dict[str, Any]],
) -> dict[str, Any]:

    combined = json.dumps(
        records
    ).lower()

    if task in {"T1", "T2", "T3"}:

        input_type = (
            "textual ticket representation"
            if (
                "text_input" in combined
                or "summary" in combined
                or "description" in combined
            )
            else "not established"
        )

        transformation = (
            "source ticket text must be transformed "
            "using the frozen implementation's native "
            "text preprocessing/vectorization path"
        )

        output = (
            "native task class/decision output"
        )

    elif task == "T4":

        input_type = (
            "query ticket plus historical candidate population"
        )

        transformation = (
            "query representation plus candidate records "
            "must be passed through the frozen retrieval/ranking "
            "implementation; target_assignee is outcome evidence "
            "and is not a runtime input"
        )

        output = (
            "historical assignee candidate ranking"
        )

    elif task == "T5":

        input_type = (
            "two ticket representations"
        )

        transformation = (
            "ticket pair must be constructed from two distinct "
            "ticket records; duplicate target/label must not "
            "enter inference input"
        )

        output = (
            "native duplicate score/probability"
        )

    elif task == "T6":

        input_type = (
            "query ticket plus candidate retrieval population"
        )

        transformation = (
            "query and candidate ticket representations must "
            "follow the frozen lexical/semantic retrieval path; "
            "target_observed must not be used as an inference input"
        )

        output = (
            "native similar-ticket ranking"
        )

    elif task == "T7":

        input_type = (
            "ticket-level survival feature representation"
        )

        transformation = (
            "native survival features must preserve "
            "time/event/censoring semantics; observed "
            "resolution outcome must not be manufactured"
        )

        output = (
            "native survival/time-to-resolution output"
        )

    else:

        input_type = "not established"
        transformation = "not established"
        output = "not established"

    return {
        "runtime_input_type": input_type,
        "construction_requirement": transformation,
        "runtime_output": output,
    }


def main() -> None:

    print("=" * 72)
    print(
        "FMP-06 OP-016 — "
        "FROZEN RUNTIME INPUT CONSTRUCTION AUDIT"
    )
    print("=" * 72)
    print()
    print("Mode: READ-ONLY")
    print("No model loading")
    print("No inference")
    print("No retraining")
    print("No artifact modification")
    print()

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = {
        "operation": "FMP-06 OP-016",
        "operation_type": (
            "READ_ONLY_FROZEN_RUNTIME_INPUT_CONSTRUCTION_AUDIT"
        ),
        "project_root": str(PROJECT_ROOT),
        "tasks": {},
        "safeguards": {
            "models_loaded": False,
            "inference_executed": False,
            "retraining": False,
            "artifact_modification": False,
            "threshold_created": False,
            "calibration_performed": False,
            "synthetic_input_created": False,
            "synthetic_target_created": False,
            "universal_confidence_created": False,
            "universal_risk_created": False,
        },
    }

    overall_status = "PASS"

    for task, task_dir in TASK_DIRS.items():

        print("-" * 72)
        print(task)

        paths = candidate_files(
            task,
            task_dir,
        )

        records = [
            inspect_file(
                task,
                path,
            )
            for path in paths
        ]

        invalid = [
            record
            for record in records
            if not record["syntax_valid"]
        ]

        if invalid:
            overall_status = "FAIL"

        contract = infer_runtime_contract(
            task,
            records,
        )

        report["tasks"][task] = {
            "task_directory": rel(task_dir),
            "candidate_script_count": len(records),
            "candidate_scripts": records,
            "runtime_contract": contract,
        }

        print(
            "  candidate implementation files:",
            len(records),
        )

        print(
            "  syntax-invalid files:",
            len(invalid),
        )

        print(
            "  runtime input:",
            contract["runtime_input_type"],
        )

        print(
            "  construction:",
            contract["construction_requirement"],
        )

        print(
            "  output:",
            contract["runtime_output"],
        )

        for record in records[:8]:

            print(
                "    SCRIPT:",
                record["file"],
            )

            print(
                "      functions:",
                record["ast"]["functions"],
            )

            print(
                "      calls:",
                record["ast"]["calls"],
            )

            print(
                "      prediction hits:",
                record["keyword_hits"]["prediction"],
            )

            print(
                "      model-load hits:",
                record["keyword_hits"]["model_load"],
            )

        print()

    report["overall_status"] = overall_status

    OUTPUT.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("=" * 72)
    print(
        f"OVERALL STATUS: {overall_status}"
    )
    print(
        f"OUTPUT: {OUTPUT}"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()