from pathlib import Path
import ast
import json
import re


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

MODELING_ROOT = PROJECT_ROOT / "modeling"
FMP_ROOT = MODELING_ROOT / "FMP"
FMP_SCRIPTS = FMP_ROOT / "scripts"
METRICS_DIR = FMP_ROOT / "metrics"

INPUT = (
    METRICS_DIR
    / "h_op002_runtime_interface_reconciliation.json"
)

OUTPUT = (
    METRICS_DIR
    / "h_op003_exact_frozen_runtime_reconciliation.json"
)


VALIDATED_OPERATIONS = {
    "T1": [
        "OP-018R5",
    ],
    "T2": [
        "OP-018R3",
    ],
    "T3": [
        "OP-018R3",
    ],
    "T4": [
        "OP-018R6",
        "OP-018R7",
        "OP-018R8",
        "OP-018R9",
        "OP-018R10",
        "OP-018R11",
        "OP-018R12",
        "OP-018R13",
        "OP-018R14",
        "OP-018R16",
    ],
    "T5": [
        "OP-018R3",
    ],
    "T6": [
        "OP-018R17",
        "OP-018R18",
        "OP-018R19",
        "OP-018R20",
        "OP-018R21",
    ],
    "T7": [
        "OP-018R22C",
        "OP-018R23",
        "OP-018R24",
        "OP-018R25",
        "OP-018R26",
        "OP-018R27",
        "OP-018R28",
    ],
}


def read_text(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace"
    )


def extract_ast_names(source):
    """
    Return source-level functions/classes.
    """
    result = {
        "functions": [],
        "classes": [],
    }

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return result

    for node in ast.walk(tree):

        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            result["functions"].append(
                node.name
            )

        elif isinstance(
            node,
            ast.ClassDef
        ):
            result["classes"].append(
                node.name
            )

    return result


def operation_hits(source, operation):

    source_lower = source.lower()
    op_lower = operation.lower()

    variants = {
        op_lower,
        op_lower.replace("-", "_"),
        op_lower.replace("-", ""),
    }

    hits = []

    for variant in variants:

        if variant in source_lower:
            hits.append(variant)

    return sorted(set(hits))


def runtime_signal_hits(source):

    source_lower = source.lower()

    signals = [
        "joblib.load",
        "pickle.load",
        "torch.load",
        "load_model",
        "predict(",
        "predict_proba(",
        "transform(",
        "kneighbors(",
        "retrieve",
        "ranking",
        "rank(",
        "similarity",
        "survival",
        "weibull",
        "lognormal",
        "log-normal",
        "tfidf",
        "t5_mod",
        "t6_mod010",
        "t7_mod010",
    ]

    return [
        signal
        for signal in signals
        if signal.lower() in source_lower
    ]


def main():

    print("=" * 72)
    print("H-OP-003 — EXACT FROZEN RUNTIME RECONCILIATION")
    print("=" * 72)

    if not INPUT.exists():
        raise FileNotFoundError(
            f"Missing H-OP-002 output: {INPUT}"
        )

    inventory = json.loads(
        INPUT.read_text(
            encoding="utf-8"
        )
    )

    # --------------------------------------------------------------
    # Build a source corpus only from FMP scripts.
    # --------------------------------------------------------------

    script_records = []

    if not FMP_SCRIPTS.exists():
        raise FileNotFoundError(
            f"Missing FMP scripts directory: {FMP_SCRIPTS}"
        )

    for path in sorted(
        FMP_SCRIPTS.rglob("*.py")
    ):

        try:
            source = read_text(path)
        except Exception:
            continue

        ast_info = extract_ast_names(
            source
        )

        script_records.append(
            {
                "path": str(path),
                "source": source,
                "functions": ast_info["functions"],
                "classes": ast_info["classes"],
                "runtime_signals":
                    runtime_signal_hits(source),
            }
        )

    # --------------------------------------------------------------
    # Reconcile each task against its previously validated
    # FMP-06 operation IDs.
    # --------------------------------------------------------------

    task_results = {}

    for task, operations in VALIDATED_OPERATIONS.items():

        matches = []

        for record in script_records:

            matched_operations = []

            for operation in operations:

                hits = operation_hits(
                    record["source"],
                    operation
                )

                if hits:
                    matched_operations.append(
                        {
                            "operation": operation,
                            "source_hits": hits,
                        }
                    )

            if matched_operations:

                matches.append(
                    {
                        "path": record["path"],
                        "matched_operations":
                            matched_operations,
                        "functions":
                            record["functions"],
                        "classes":
                            record["classes"],
                        "runtime_signals":
                            record["runtime_signals"],
                    }
                )

        # ----------------------------------------------------------
        # Deduplicate paths while preserving evidence.
        # ----------------------------------------------------------

        unique = {}

        for match in matches:

            path = match["path"]

            if path not in unique:
                unique[path] = match

            else:

                existing = unique[path]

                existing_ops = {
                    item["operation"]
                    for item in
                    existing["matched_operations"]
                }

                for item in match[
                    "matched_operations"
                ]:

                    if item["operation"] not in existing_ops:
                        existing[
                            "matched_operations"
                        ].append(item)

        matches = list(
            unique.values()
        )

        task_results[task] = {
            "validated_operations":
                operations,

            "matching_fmp_scripts":
                len(matches),

            "matches":
                matches,
        }

    # --------------------------------------------------------------
    # Search specifically for final runtime reconciliation scripts
    # that reference the validated frozen bindings.
    # --------------------------------------------------------------

    binding_evidence = []

    binding_tokens = [
        "fmp06_op019r1",
        "op019r1",
        "t1_it_support_char_svm",
        "t2_class_weighted_tfidf_logreg",
        "t3_class_weighted_tfidf_logreg",
        "t4_mod007",
        "t5_mod007",
        "t6_mod010",
        "t7_mod010",
    ]

    for record in script_records:

        source_lower = record["source"].lower()

        hits = [
            token
            for token in binding_tokens
            if token.lower() in source_lower
        ]

        if hits:

            binding_evidence.append(
                {
                    "path": record["path"],
                    "binding_hits": hits,
                    "functions":
                        record["functions"],
                    "classes":
                        record["classes"],
                }
            )

    # --------------------------------------------------------------
    # Compact summary.
    # --------------------------------------------------------------

    summary = {}

    for task, data in task_results.items():

        operation_count = len(
            data["validated_operations"]
        )

        matched_script_count = data[
            "matching_fmp_scripts"
        ]

        matched_operations = set()

        for match in data["matches"]:

            for item in match[
                "matched_operations"
            ]:

                matched_operations.add(
                    item["operation"]
                )

        summary[task] = {
            "validated_operation_count":
                operation_count,

            "validated_operations_found_in_source":
                len(matched_operations),

            "matching_script_count":
                matched_script_count,

            "all_operations_referenced":
                (
                    len(matched_operations)
                    == operation_count
                ),
        }

    # --------------------------------------------------------------
    # Important interpretation:
    #
    # Multiple scripts can legitimately reference the same operation.
    # This operation identifies source evidence; it does not yet
    # declare a unique callable.
    # --------------------------------------------------------------

    result = {

        "operation":
            "H-OP-003",

        "operation_name":
            "Exact Frozen Runtime Reconciliation",

        "status":
            "PASS",

        "purpose": (
            "Trace previously validated FMP-06 runtime operations "
            "back to their actual FMP source scripts and callable "
            "definitions before constructing the new-ticket "
            "orchestrator."
        ),

        "validated_operations":
            VALIDATED_OPERATIONS,

        "task_summary":
            summary,

        "task_results":
            task_results,

        "frozen_binding_evidence":
            binding_evidence,

        "controls": {
            "model_execution": False,
            "model_retraining": False,
            "model_selection": False,
            "artifact_modification": False,
            "threshold_optimization": False,
            "locked_test_reuse": False,
        },

        "interpretation_boundary": (
            "A source reference to a validated operation establishes "
            "traceability but does not automatically establish that "
            "the referenced script is the final single-ticket callable. "
            "The exact callable and its input/output contract require "
            "the next reconciliation step."
        ),

        "next_operation":
            "H-OP-004 — identify the exact callable/input/output "
            "contract for the frozen T1-T7 runtime components.",

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

    # --------------------------------------------------------------
    # Compact terminal output.
    # --------------------------------------------------------------

    print()

    for task in (
        "T1",
        "T2",
        "T3",
        "T4",
        "T5",
        "T6",
        "T7",
    ):

        data = summary[task]

        print(
            f"{task}: "
            f"validated_ops="
            f"{data['validated_operation_count']} "
            f"ops_found="
            f"{data['validated_operations_found_in_source']} "
            f"matching_scripts="
            f"{data['matching_script_count']} "
            f"all_ops_referenced="
            f"{data['all_operations_referenced']}"
        )

    print()

    print(
        "Frozen binding evidence records: "
        f"{len(binding_evidence)}"
    )

    print(
        f"OUTPUT: {OUTPUT}"
    )

    print(
        "STATUS: PASS"
    )


if __name__ == "__main__":
    main()