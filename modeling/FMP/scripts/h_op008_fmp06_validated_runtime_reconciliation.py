from pathlib import Path
import ast
import json


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

MODELING_ROOT = PROJECT_ROOT / "modeling"
FMP_ROOT = MODELING_ROOT / "FMP"
METRICS_DIR = FMP_ROOT / "metrics"

H006 = (
    METRICS_DIR
    / "h_op006_exact_callable_source_inspection.json"
)

FMP06_BINDING = (
    METRICS_DIR
    / "fmp06_op019r1_final_t1_t7_runtime_binding_reconciliation.json"
)

FMP06_CLOSURE = (
    METRICS_DIR
    / "fmp06_final_phase_closure.json"
)

OUTPUT = (
    METRICS_DIR
    / "h_op008_fmp06_validated_runtime_reconciliation.json"
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


# These are the exact FMP-06 validated runtime operations already
# established during the frozen-runtime investigation.
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


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Missing required file: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def normalize(path):
    return str(
        Path(path).resolve()
    )


def collect_all_strings(obj):
    values = []

    if isinstance(obj, dict):

        for key, value in obj.items():

            values.append(str(key))
            values.extend(
                collect_all_strings(value)
            )

    elif isinstance(obj, list):

        for value in obj:
            values.extend(
                collect_all_strings(value)
            )

    elif isinstance(obj, str):

        values.append(obj)

    return values


def find_operation_records(
    obj,
    operation_id,
    path=(),
):
    matches = []

    if isinstance(obj, dict):

        # Check whether this dictionary appears to describe
        # the requested operation.
        operation_values = []

        for key in [
            "operation",
            "operation_id",
            "validated_operation",
            "op",
        ]:

            value = obj.get(key)

            if value is not None:
                operation_values.append(
                    str(value)
                )

        if operation_id in operation_values:

            matches.append(
                {
                    "path": list(path),
                    "record": obj,
                }
            )

        for key, value in obj.items():

            matches.extend(
                find_operation_records(
                    value,
                    operation_id,
                    path + (str(key),),
                )
            )

    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            matches.extend(
                find_operation_records(
                    value,
                    operation_id,
                    path + (str(index),),
                )
            )

    return matches


def extract_paths_from_record(record):
    strings = collect_all_strings(
        record
    )

    paths = []

    for value in strings:

        if (
            ".py" in value
            and (
                "/home/"
                in value
                or str(PROJECT_ROOT)
                in value
            )
        ):

            paths.append(
                value
            )

    return sorted(
        set(paths)
    )


def function_names_from_source(path):
    try:
        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        tree = ast.parse(source)

    except Exception:
        return []

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
                node.name
            )

    return sorted(
        set(functions)
    )


def build_candidate_index(h006):
    index = {}

    for task in TASKS:

        candidates = (
            h006
            .get("task_results", {})
            .get(task, {})
            .get("candidates", [])
        )

        task_index = {}

        for candidate in candidates:

            path = normalize(
                candidate["path"]
            )

            function = candidate[
                "function"
            ]

            task_index.setdefault(
                path,
                set()
            ).add(
                function
            )

        index[task] = task_index

    return index


def main():

    print("=" * 72)
    print(
        "H-OP-008 — FMP-06 VALIDATED RUNTIME RECONCILIATION"
    )
    print("=" * 72)

    h006 = load_json(H006)
    binding = load_json(FMP06_BINDING)
    closure = load_json(FMP06_CLOSURE)

    candidate_index = (
        build_candidate_index(
            h006
        )
    )

    task_results = {}

    for task in TASKS:

        operation_results = []

        validated_scripts = set()

        for operation_id in (
            VALIDATED_OPERATIONS[task]
        ):

            matches = find_operation_records(
                binding,
                operation_id,
            )

            operation_paths = []

            for match in matches:

                paths = (
                    extract_paths_from_record(
                        match["record"]
                    )
                )

                for path in paths:

                    try:
                        resolved = normalize(
                            path
                        )

                    except Exception:
                        continue

                    operation_paths.append(
                        resolved
                    )

                    validated_scripts.add(
                        resolved
                    )

            operation_results.append(
                {
                    "operation":
                        operation_id,

                    "binding_records_found":
                        len(matches),

                    "source_paths":
                        sorted(
                            set(
                                operation_paths
                            )
                        ),
                }
            )

        candidate_matches = []

        for script_path in sorted(
            validated_scripts
        ):

            functions = (
                function_names_from_source(
                    Path(script_path)
                )
                if Path(script_path).exists()
                else []
            )

            candidate_functions = (
                candidate_index[task].get(
                    script_path,
                    set()
                )
            )

            for function in sorted(
                candidate_functions
            ):

                candidate_matches.append(
                    {
                        "path":
                            script_path,

                        "function":
                            function,

                        "source_function_exists":
                            function in functions,

                        "validated_runtime_script":
                            True,
                    }
                )

        # Also identify validated scripts that contain functions
        # even when H-OP-006 did not shortlist them.
        validated_script_functions = []

        for script_path in sorted(
            validated_scripts
        ):

            path = Path(
                script_path
            )

            if not path.exists():
                continue

            functions = (
                function_names_from_source(
                    path
                )
            )

            validated_script_functions.append(
                {
                    "path":
                        script_path,

                    "functions":
                        functions,
                }
            )

        task_results[task] = {

            "validated_operations":
                VALIDATED_OPERATIONS[task],

            "operation_results":
                operation_results,

            "validated_script_count":
                len(validated_scripts),

            "validated_scripts":
                sorted(
                    validated_scripts
                ),

            "h006_candidate_matches":
                candidate_matches,

            "validated_script_function_inventory":
                validated_script_functions,
        }

    # --------------------------------------------------------------
    # Determine whether the FMP-06 evidence gives us a direct
    # source-level runtime candidate.
    # --------------------------------------------------------------

    final_candidates = {}

    for task in TASKS:

        matches = task_results[task][
            "h006_candidate_matches"
        ]

        # Deduplicate path/function pairs.
        unique = {}

        for match in matches:

            key = (
                match["path"],
                match["function"],
            )

            unique[key] = match

        matches = list(
            unique.values()
        )

        task_results[task][
            "deduplicated_candidate_count"
        ] = len(matches)

        if len(matches) == 1:

            final_candidates[task] = {
                "status":
                    "DIRECT_VALIDATED_CANDIDATE",

                "path":
                    matches[0]["path"],

                "function":
                    matches[0]["function"],
            }

        elif len(matches) > 1:

            final_candidates[task] = {
                "status":
                    "MULTIPLE_VALIDATED_CANDIDATES",

                "candidates":
                    matches,
            }

        else:

            final_candidates[task] = {
                "status":
                    "NO_H006_CANDIDATE_IN_VALIDATED_SCRIPT",
            }

    result = {

        "operation":
            "H-OP-008",

        "operation_name":
            "FMP-06 Validated Runtime Reconciliation",

        "status":
            "PASS",

        "purpose": (
            "Reconcile H-OP-006 source candidates against "
            "the exact scripts associated with previously "
            "validated FMP-06 frozen-runtime executions."
        ),

        "validated_operations":
            VALIDATED_OPERATIONS,

        "fmp06_binding_file":
            str(FMP06_BINDING),

        "fmp06_closure_file":
            str(FMP06_CLOSURE),

        "task_results":
            task_results,

        "final_candidates":
            final_candidates,

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
            "FMP-06 validated runtime evidence is treated as "
            "stronger evidence than generic source heuristics. "
            "This operation does not itself execute a model or "
            "declare a production orchestrator."
        ),

        "next_operation":
            "H-OP-009 — inspect the exact validated runtime "
            "source paths and reconcile callable roles.",

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
            f"validated_scripts="
            f"{data['validated_script_count']} "
            f"h006_matches="
            f"{data['deduplicated_candidate_count']} "
            f"status="
            f"{final_candidates[task]['status']}"
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