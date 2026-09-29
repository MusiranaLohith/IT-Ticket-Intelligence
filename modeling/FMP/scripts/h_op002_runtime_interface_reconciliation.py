from pathlib import Path
import ast
import json
import re


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

MODELING_ROOT = PROJECT_ROOT / "modeling"
FMP_ROOT = MODELING_ROOT / "FMP"
METRICS_DIR = FMP_ROOT / "metrics"

INPUT = (
    METRICS_DIR
    / "h_op001_runtime_interface_inventory.json"
)

OUTPUT = (
    METRICS_DIR
    / "h_op002_runtime_interface_reconciliation.json"
)

TASKS = ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]

RUNTIME_KEYWORDS = (
    "predict",
    "inference",
    "infer",
    "runtime",
    "pipeline",
    "classify",
    "retrieve",
    "search",
    "score",
    "rank",
    "load_model",
    "model",
    "transform",
    "encode",
)

INPUT_KEYWORDS = (
    "text",
    "ticket",
    "title",
    "description",
    "query",
    "subject",
    "body",
    "issue",
    "message",
)

OUTPUT_KEYWORDS = (
    "predict",
    "prediction",
    "result",
    "score",
    "rank",
    "candidate",
    "prob",
    "label",
    "output",
)


def load_json(path):
    with path.open(
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def read_source(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace"
    )


def function_source(source, node):
    try:
        return ast.get_source_segment(
            source,
            node
        ) or ""
    except Exception:
        return ""


def inspect_python_file(path):
    source = read_source(path)

    record = {
        "path": str(path),
        "syntax_valid": False,
        "functions": [],
        "classes": [],
        "runtime_functions": [],
        "runtime_classes": [],
        "model_loading_evidence": [],
        "input_parameter_evidence": [],
        "output_evidence": [],
    }

    try:
        tree = ast.parse(source)
        record["syntax_valid"] = True
    except SyntaxError:
        return record

    for node in ast.walk(tree):

        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef)
        ):

            name = node.name.lower()

            record["functions"].append(
                node.name
            )

            src = function_source(
                source,
                node
            )

            src_lower = src.lower()

            runtime_score = sum(
                keyword in name
                or keyword in src_lower
                for keyword in RUNTIME_KEYWORDS
            )

            input_hits = [
                keyword
                for keyword in INPUT_KEYWORDS
                if keyword in src_lower
            ]

            output_hits = [
                keyword
                for keyword in OUTPUT_KEYWORDS
                if keyword in src_lower
            ]

            model_hits = [
                token
                for token in (
                    "joblib.load",
                    "pickle.load",
                    "torch.load",
                    "load_model",
                    "LinearSVC",
                    "LogisticRegression",
                    "TfidfVectorizer",
                    "NearestNeighbors",
                    "bm25",
                    "sentence_transformer",
                )
                if token.lower() in src_lower
            ]

            if runtime_score > 0:

                record[
                    "runtime_functions"
                ].append(
                    {
                        "name": node.name,
                        "runtime_score": runtime_score,
                        "parameters": [
                            arg.arg
                            for arg in node.args.args
                        ],
                        "input_keyword_hits": input_hits,
                        "output_keyword_hits": output_hits,
                    }
                )

            if model_hits:

                record[
                    "model_loading_evidence"
                ].append(
                    {
                        "function": node.name,
                        "evidence": model_hits,
                    }
                )

            if input_hits:

                record[
                    "input_parameter_evidence"
                ].append(
                    {
                        "function": node.name,
                        "keywords": input_hits,
                    }
                )

            if output_hits:

                record[
                    "output_evidence"
                ].append(
                    {
                        "function": node.name,
                        "keywords": output_hits,
                    }
                )

        elif isinstance(
            node,
            ast.ClassDef
        ):

            record["classes"].append(
                node.name
            )

            class_name = node.name.lower()

            if any(
                keyword in class_name
                for keyword in RUNTIME_KEYWORDS
            ):
                record[
                    "runtime_classes"
                ].append(
                    node.name
                )

    return record


def main():

    print("=" * 72)
    print("H-OP-002 — RUNTIME INTERFACE RECONCILIATION")
    print("=" * 72)

    if not INPUT.exists():
        raise FileNotFoundError(
            f"Missing H-OP-001 inventory: {INPUT}"
        )

    inventory = load_json(INPUT)

    reconciled = {}

    for task in TASKS:

        task_data = inventory[
            "tasks"
        ].get(task, {})

        files = task_data.get(
            "python_files",
            []
        )

        task_records = []

        for file_record in files:

            path = Path(
                file_record["path"]
            )

            if not path.exists():
                continue

            inspected = inspect_python_file(
                path
            )

            if (
                inspected["runtime_functions"]
                or
                inspected["runtime_classes"]
                or
                inspected["model_loading_evidence"]
            ):
                task_records.append(
                    inspected
                )

        reconciled[task] = {
            "candidate_file_count":
                len(task_records),
            "candidates":
                task_records,
        }

    # --------------------------------------------------------------
    # FMP candidates that may represent orchestration/runtime logic.
    # --------------------------------------------------------------

    fmp_records = []

    for record in inventory.get(
        "fmp_python_files",
        []
    ):

        path = Path(
            record["path"]
        )

        if not path.exists():
            continue

        inspected = inspect_python_file(
            path
        )

        if (
            inspected["runtime_functions"]
            or
            inspected["runtime_classes"]
            or
            inspected["model_loading_evidence"]
        ):
            fmp_records.append(
                inspected
            )

    # --------------------------------------------------------------
    # Runtime evidence already established by FMP-06.
    # Search the FMP scripts for explicit OP-018/019 runtime
    # references so we can connect discovery to previously
    # validated runtime work.
    # --------------------------------------------------------------

    validated_runtime_evidence = []

    fmp_scripts = FMP_ROOT / "scripts"

    if fmp_scripts.exists():

        for path in fmp_scripts.rglob(
            "*.py"
        ):

            source = read_source(path)
            source_lower = source.lower()

            validation_hits = []

            for token in (
                "op-018",
                "op018",
                "op-019",
                "op019",
                "runtime smoke",
                "runtime_reproduction",
                "frozen runtime",
            ):

                if token.lower() in source_lower:

                    validation_hits.append(
                        token
                    )

            if validation_hits:

                validated_runtime_evidence.append(
                    {
                        "path": str(path),
                        "evidence": validation_hits,
                    }
                )

    # --------------------------------------------------------------
    # Produce compact candidate summary.
    # --------------------------------------------------------------

    task_summary = {}

    for task in TASKS:

        records = reconciled[
            task
        ]["candidates"]

        task_summary[task] = {
            "candidate_files":
                len(records),

            "runtime_functions":
                sum(
                    len(
                        r["runtime_functions"]
                    )
                    for r in records
                ),

            "model_loading_evidence":
                sum(
                    len(
                        r["model_loading_evidence"]
                    )
                    for r in records
                ),

            "input_evidence":
                sum(
                    len(
                        r["input_parameter_evidence"]
                    )
                    for r in records
                ),
        }

    result = {

        "operation":
            "H-OP-002",

        "operation_name":
            "Actual Runtime Interface Reconciliation",

        "status":
            "PASS",

        "purpose": (
            "Read-only reconciliation of candidate T1-T7 runtime "
            "interfaces against actual source-level callable, "
            "input, output, and frozen-model-loading evidence."
        ),

        "task_summary":
            task_summary,

        "task_candidates":
            reconciled,

        "fmp_runtime_candidates":
            fmp_records,

        "validated_runtime_evidence":
            validated_runtime_evidence,

        "controls": {
            "model_execution": False,
            "model_retraining": False,
            "model_selection": False,
            "artifact_modification": False,
            "threshold_optimization": False,
            "locked_test_reuse": False,
        },

        "interpretation_boundary": (
            "Source-level candidate discovery is not itself "
            "runtime validation. A candidate becomes a usable "
            "runtime interface only after its exact input/output "
            "contract is reconciled against the previously "
            "validated frozen runtime evidence."
        ),

        "next_operation":
            "H-OP-003 — select and reconcile the exact frozen "
            "runtime callable for each task before constructing "
            "the single-ticket orchestrator.",

        "output":
            str(OUTPUT),
    }

    with OUTPUT.open(
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            indent=2
        )

    print()

    for task in TASKS:

        summary = task_summary[
            task
        ]

        print(
            f"{task}: "
            f"candidate_files="
            f"{summary['candidate_files']} "
            f"runtime_functions="
            f"{summary['runtime_functions']} "
            f"model_loading="
            f"{summary['model_loading_evidence']} "
            f"input_evidence="
            f"{summary['input_evidence']}"
        )

    print()

    print(
        "Validated runtime evidence records: "
        f"{len(validated_runtime_evidence)}"
    )

    print(
        "FMP runtime candidate records: "
        f"{len(fmp_records)}"
    )

    print()

    print(
        f"OUTPUT: {OUTPUT}"
    )

    print(
        "STATUS: PASS"
    )


if __name__ == "__main__":
    main()