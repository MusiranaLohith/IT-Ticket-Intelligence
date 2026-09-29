from pathlib import Path
import ast
import json


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

METRICS_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
)

INPUT = (
    METRICS_DIR
    / "h_op005_frozen_callable_selection.json"
)

OUTPUT = (
    METRICS_DIR
    / "h_op006_exact_callable_source_inspection.json"
)


TASKS = [
    "T1",
    "T2",
    "T3",
    "T4",
    "T5",
    "T6",
    "T7",
]


def read_text(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def get_function_node(path, function_name):
    source = read_text(path)

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None, None

    for node in ast.walk(tree):

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):

            if node.name == function_name:
                return node, source

    return None, source


def extract_function_details(path, function_name):
    node, source = get_function_node(
        path,
        function_name,
    )

    if node is None:

        return {
            "path": str(path),
            "function": function_name,
            "found": False,
        }

    parameters = []

    for arg in node.args.posonlyargs:
        parameters.append(arg.arg)

    for arg in node.args.args:
        parameters.append(arg.arg)

    if node.args.vararg:
        parameters.append(
            "*" + node.args.vararg.arg
        )

    for arg in node.args.kwonlyargs:
        parameters.append(arg.arg)

    if node.args.kwarg:
        parameters.append(
            "**" + node.args.kwarg.arg
        )

    return_expressions = []

    for child in ast.walk(node):

        if isinstance(child, ast.Return):

            if child.value is None:
                return_expressions.append(
                    "None"
                )
            else:

                try:
                    return_expressions.append(
                        ast.unparse(
                            child.value
                        )
                    )
                except Exception:
                    return_expressions.append(
                        "<unparse_failed>"
                    )

    try:
        function_source = (
            ast.get_source_segment(
                source,
                node,
            )
            or ""
        )
    except Exception:
        function_source = ""

    source_lower = function_source.lower()

    artifact_terms = [
        ".joblib",
        ".json",
        ".npz",
        "joblib.load",
        "pickle.load",
        "torch.load",
        "load_model",
        "t1_it_support",
        "t2_class_weighted",
        "t3_class_weighted",
        "t4_mod007",
        "t5_mod005",
        "t5_mod007",
        "t6_mod010",
        "t7_mod010",
    ]

    artifact_hits = [
        term
        for term in artifact_terms
        if term.lower() in source_lower
    ]

    runtime_terms = [
        "predict(",
        "predict_proba(",
        "decision_function(",
        "transform(",
        "kneighbors(",
        "retrieve",
        "similarity",
        "rank(",
        "score(",
        "survival",
        "weibull",
        "lognormal",
        "resolution",
        "candidate",
    ]

    runtime_hits = [
        term
        for term in runtime_terms
        if term.lower() in source_lower
    ]

    input_terms = [
        "ticket",
        "text",
        "title",
        "description",
        "query",
        "subject",
        "body",
        "message",
        "issue",
        "request",
        "candidate",
        "history",
        "reference",
    ]

    input_hits = [
        term
        for term in input_terms
        if term.lower() in source_lower
    ]

    # Keep source compact but sufficient for manual reconciliation.
    source_lines = function_source.splitlines()

    if len(source_lines) > 120:
        source_lines = source_lines[:120]

    return {
        "path": str(path),
        "function": function_name,
        "found": True,
        "parameters": parameters,
        "return_count": len(
            return_expressions
        ),
        "return_expressions":
            return_expressions[:15],
        "artifact_hits":
            sorted(set(artifact_hits)),
        "runtime_hits":
            sorted(set(runtime_hits)),
        "input_hits":
            sorted(set(input_hits)),
        "source_line_count":
            len(function_source.splitlines()),
        "source_preview":
            source_lines,
    }


def main():

    print("=" * 72)
    print(
        "H-OP-006 — EXACT CALLABLE SOURCE INSPECTION"
    )
    print("=" * 72)

    if not INPUT.exists():
        raise FileNotFoundError(
            f"Missing H-OP-005 output: {INPUT}"
        )

    h005 = json.loads(
        INPUT.read_text(
            encoding="utf-8"
        )
    )

    task_results = {}

    for task in TASKS:

        candidates = (
            h005
            .get("task_results", {})
            .get(task, {})
            .get("top_candidates", [])
        )

        # Inspect only the shortlisted candidates.
        inspected = []

        seen = set()

        for candidate in candidates:

            path = Path(
                candidate["path"]
            )

            function_name = candidate[
                "function"
            ]

            identity = (
                str(path),
                function_name,
            )

            if identity in seen:
                continue

            seen.add(identity)

            if not path.exists():
                inspected.append(
                    {
                        "path": str(path),
                        "function": function_name,
                        "found": False,
                        "error":
                            "source_file_missing",
                    }
                )
                continue

            inspected.append(
                extract_function_details(
                    path,
                    function_name,
                )
            )

        task_results[task] = {
            "shortlisted_candidate_count":
                len(candidates),

            "inspected_candidate_count":
                len(inspected),

            "candidates":
                inspected,
        }

    result = {
        "operation":
            "H-OP-006",

        "operation_name":
            "Exact Callable Source Inspection",

        "status":
            "PASS",

        "purpose": (
            "Direct source inspection of shortlisted T1-T7 "
            "runtime callable candidates to establish their "
            "actual parameters, artifact references, inference "
            "operations, input signals, and return behavior."
        ),

        "task_results":
            task_results,

        "controls": {
            "model_execution": False,
            "model_retraining": False,
            "model_selection": False,
            "artifact_modification": False,
            "threshold_optimization": False,
            "locked_test_reuse": False,
        },

        "interpretation_boundary": (
            "This operation exposes source evidence for manual "
            "runtime-contract reconciliation. It does not "
            "automatically select a callable, execute a model, "
            "or establish production readiness."
        ),

        "next_operation":
            "H-OP-007 — final task-by-task frozen runtime "
            "contract reconciliation.",

        "output":
            str(OUTPUT),
    }

    with OUTPUT.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            result,
            f,
            indent=2,
        )

    print()

    for task in TASKS:

        data = task_results[task]

        print(
            f"{task}: "
            f"shortlisted="
            f"{data['shortlisted_candidate_count']} "
            f"inspected="
            f"{data['inspected_candidate_count']}"
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