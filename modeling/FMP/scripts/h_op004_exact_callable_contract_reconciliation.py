from pathlib import Path
import ast
import json


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

FMP_ROOT = PROJECT_ROOT / "modeling" / "FMP"
METRICS_DIR = FMP_ROOT / "metrics"

INPUT = (
    METRICS_DIR
    / "h_op003_exact_frozen_runtime_reconciliation.json"
)

OUTPUT = (
    METRICS_DIR
    / "h_op004_exact_callable_contract_reconciliation.json"
)


TASKS = ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]


INPUT_TERMS = {
    "ticket": [
        "ticket",
        "issue",
        "request",
        "incident",
        "case",
    ],
    "text": [
        "text",
        "description",
        "body",
        "message",
        "content",
        "title",
        "subject",
        "query",
    ],
    "historical": [
        "history",
        "historical",
        "reference",
        "corpus",
        "database",
        "dataset",
        "training",
        "neighbor",
        "candidate",
        "retrieval",
        "index",
    ],
}


def read_source(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def safe_unparse(node):
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def extract_function_contract(source, node):
    parameters = []

    for arg in node.args.posonlyargs:
        parameters.append(arg.arg)

    for arg in node.args.args:
        parameters.append(arg.arg)

    if node.args.vararg:
        parameters.append("*" + node.args.vararg.arg)

    for arg in node.args.kwonlyargs:
        parameters.append(arg.arg)

    if node.args.kwarg:
        parameters.append("**" + node.args.kwarg.arg)

    returns = []

    for child in ast.walk(node):

        if isinstance(child, ast.Return):

            if child.value is None:
                returns.append("None")
            else:
                returns.append(
                    safe_unparse(child.value)
                )

    source_segment = safe_unparse(node)

    source_lower = source_segment.lower()

    input_hits = {}

    for category, terms in INPUT_TERMS.items():

        hits = [
            term
            for term in terms
            if term.lower() in source_lower
        ]

        if hits:
            input_hits[category] = sorted(
                set(hits)
            )

    artifact_hits = []

    for token in [
        "joblib.load",
        "pickle.load",
        "torch.load",
        "load_model",
        "read_csv",
        "read_parquet",
        "np.load",
        "open(",
        "Path(",
    ]:

        if token.lower() in source_lower:
            artifact_hits.append(token)

    prediction_hits = []

    for token in [
        "predict(",
        "predict_proba(",
        "decision_function(",
        "transform(",
        "kneighbors(",
        "similarity",
        "rank(",
        "retrieve",
        "score(",
        "survival",
        "weibull",
        "lognormal",
    ]:

        if token.lower() in source_lower:
            prediction_hits.append(token)

    return {
        "name": node.name,
        "parameters": parameters,
        "return_count": len(returns),
        "return_expressions": returns[:10],
        "input_hits": input_hits,
        "artifact_loading_hits": sorted(
            set(artifact_hits)
        ),
        "prediction_hits": sorted(
            set(prediction_hits)
        ),
        "source_length": len(source_segment),
    }


def inspect_file(path):
    source = read_source(path)

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {
            "path": str(path),
            "syntax_valid": False,
            "functions": [],
        }

    functions = []

    for node in ast.walk(tree):

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):

            functions.append(
                extract_function_contract(
                    source,
                    node,
                )
            )

    return {
        "path": str(path),
        "syntax_valid": True,
        "functions": functions,
    }


def score_callable(function_record):
    score = 0

    name = function_record[
        "name"
    ].lower()

    params = " ".join(
        function_record["parameters"]
    ).lower()

    prediction_hits = function_record[
        "prediction_hits"
    ]

    artifact_hits = function_record[
        "artifact_loading_hits"
    ]

    input_hits = function_record[
        "input_hits"
    ]

    # Strong runtime naming signals.
    for term in [
        "predict",
        "infer",
        "classify",
        "retrieve",
        "rank",
        "score",
        "run",
        "process",
        "transform",
    ]:

        if term in name:
            score += 3

    # Ticket/text input.
    if "ticket" in input_hits:
        score += 3

    if "text" in input_hits:
        score += 3

    # Prediction/retrieval operation.
    score += min(
        len(prediction_hits) * 2,
        10,
    )

    # Artifact loading.
    score += min(
        len(artifact_hits),
        5,
    )

    # Parameters are useful for an external callable.
    if function_record[
        "parameters"
    ]:
        score += 2

    # Historical references are not bad; they are important
    # evidence for retrieval tasks.
    if "historical" in input_hits:
        score += 1

    # Very generic functions receive no additional score.
    if name in {
        "main",
        "__init__",
        "load",
        "save",
        "run",
    }:
        score -= 1

    return score


def main():

    print("=" * 72)
    print(
        "H-OP-004 — EXACT CALLABLE / INPUT / OUTPUT "
        "CONTRACT RECONCILIATION"
    )
    print("=" * 72)

    if not INPUT.exists():
        raise FileNotFoundError(
            f"Missing H-OP-003 output: {INPUT}"
        )

    source_record = json.loads(
        INPUT.read_text(
            encoding="utf-8"
        )
    )

    task_results = {}

    for task in TASKS:

        h003_task = source_record[
            "task_results"
        ].get(
            task,
            {}
        )

        matches = h003_task.get(
            "matches",
            []
        )

        inspected_files = []

        seen_paths = set()

        for match in matches:

            path = Path(
                match["path"]
            )

            if (
                not path.exists()
                or path in seen_paths
            ):
                continue

            seen_paths.add(path)

            inspected = inspect_file(
                path
            )

            # Keep only functions that have
            # some runtime relevance.
            relevant_functions = []

            for function in inspected[
                "functions"
            ]:

                score = score_callable(
                    function
                )

                if score > 0:

                    function[
                        "runtime_score"
                    ] = score

                    relevant_functions.append(
                        function
                    )

            if relevant_functions:

                inspected_files.append(
                    {
                        "path":
                            inspected["path"],

                        "functions":
                            sorted(
                                relevant_functions,
                                key=lambda x:
                                x["runtime_score"],
                                reverse=True,
                            ),

                        "validated_operations":
                            match[
                                "matched_operations"
                            ],
                    }
                )

        # ----------------------------------------------------------
        # Flatten and select strongest candidates.
        # ----------------------------------------------------------

        candidates = []

        for file_record in inspected_files:

            for function in file_record[
                "functions"
            ]:

                candidates.append(
                    {
                        "path":
                            file_record["path"],

                        "function":
                            function,

                        "validated_operations":
                            file_record[
                                "validated_operations"
                            ],
                    }
                )

        candidates = sorted(
            candidates,
            key=lambda x:
            x["function"]["runtime_score"],
            reverse=True,
        )

        task_results[task] = {

            "validated_operations":
                h003_task.get(
                    "validated_operations",
                    [],
                ),

            "inspected_file_count":
                len(inspected_files),

            "callable_candidate_count":
                len(candidates),

            "top_candidates":
                candidates[:15],
        }

    # --------------------------------------------------------------
    # Summaries.
    # --------------------------------------------------------------

    summary = {}

    for task in TASKS:

        data = task_results[task]

        top = data[
            "top_candidates"
        ]

        summary[task] = {

            "inspected_files":
                data[
                    "inspected_file_count"
                ],

            "callable_candidates":
                data[
                    "callable_candidate_count"
                ],

            "top_candidate_count":
                len(top),

            "strongest_runtime_score":
                (
                    top[0]["function"][
                        "runtime_score"
                    ]
                    if top
                    else None
                ),
        }

    result = {

        "operation":
            "H-OP-004",

        "operation_name":
            "Exact Callable / Input / Output Contract Reconciliation",

        "status":
            "PASS",

        "purpose": (
            "Source-driven inspection of previously validated "
            "T1-T7 runtime scripts to identify callable functions, "
            "parameters, return behavior, artifact loading, "
            "ticket/text inputs, and historical/reference-data "
            "dependencies."
        ),

        "task_summary":
            summary,

        "task_results":
            task_results,

        "controls": {

            "model_execution":
                False,

            "model_retraining":
                False,

            "model_selection":
                False,

            "artifact_modification":
                False,

            "threshold_optimization":
                False,

            "locked_test_reuse":
                False,
        },

        "interpretation_boundary": (
            "Runtime scores identify source-level callable "
            "candidates only. They do not establish an official "
            "production entrypoint or authorize model execution. "
            "The next operation must reconcile the strongest "
            "candidates against frozen artifact bindings and "
            "previously validated runtime behavior."
        ),

        "next_operation":
            "H-OP-005 — final frozen callable selection and "
            "single-ticket runtime contract definition.",

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

    # --------------------------------------------------------------
    # Compact output.
    # --------------------------------------------------------------

    print()

    for task in TASKS:

        data = summary[task]

        print(
            f"{task}: "
            f"inspected_files="
            f"{data['inspected_files']} "
            f"callable_candidates="
            f"{data['callable_candidates']} "
            f"strongest_score="
            f"{data['strongest_runtime_score']}"
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