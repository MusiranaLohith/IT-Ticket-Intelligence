from pathlib import Path
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
    / "h_op006_exact_callable_source_inspection.json"
)

OUTPUT = (
    METRICS_DIR
    / "h_op007_final_runtime_contract_reconciliation.json"
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


TASK_REQUIREMENTS = {

    "T1": {
        "required_input_any": [
            "text",
            "ticket",
            "description",
            "title",
            "subject",
            "body",
            "message",
        ],
        "required_runtime_any": [
            "predict(",
            "decision_function(",
        ],
        "required_output_any": [
            "predict",
            "class",
            "category",
        ],
        "artifact_required": True,
        "reference_dependency": False,
    },

    "T2": {
        "required_input_any": [
            "text",
            "ticket",
            "description",
            "title",
            "subject",
            "body",
            "message",
        ],
        "required_runtime_any": [
            "predict(",
            "predict_proba(",
            "decision_function(",
        ],
        "required_output_any": [
            "predict",
            "class",
            "priority",
        ],
        "artifact_required": True,
        "reference_dependency": False,
    },

    "T3": {
        "required_input_any": [
            "text",
            "ticket",
            "description",
            "title",
            "subject",
            "body",
            "message",
        ],
        "required_runtime_any": [
            "predict(",
            "predict_proba(",
            "decision_function(",
        ],
        "required_output_any": [
            "predict",
            "class",
            "severity",
        ],
        "artifact_required": True,
        "reference_dependency": False,
    },

    "T4": {
        "required_input_any": [
            "ticket",
            "text",
            "query",
            "description",
            "title",
        ],
        "required_runtime_any": [
            "kneighbors(",
            "retrieve",
            "similarity",
            "rank(",
            "score(",
            "candidate",
            "neighbor",
        ],
        "required_output_any": [
            "assignee",
            "candidate",
            "neighbor",
            "rank",
            "retrieve",
        ],
        "artifact_required": True,
        "reference_dependency": True,
    },

    "T5": {
        "required_input_any": [
            "ticket",
            "text",
            "query",
            "description",
            "title",
        ],
        "required_runtime_any": [
            "predict(",
            "predict_proba(",
            "decision_function(",
            "score(",
        ],
        "required_output_any": [
            "duplicate",
            "prob",
            "score",
            "predict",
        ],
        "artifact_required": True,
        "reference_dependency": False,
    },

    "T6": {
        "required_input_any": [
            "ticket",
            "text",
            "query",
            "description",
            "title",
        ],
        "required_runtime_any": [
            "retrieve",
            "similarity",
            "rank(",
            "score(",
            "candidate",
        ],
        "required_output_any": [
            "candidate",
            "rank",
            "score",
            "similar",
            "retrieve",
        ],
        "artifact_required": False,
        "reference_dependency": True,
    },

    "T7": {
        "required_input_any": [
            "ticket",
            "text",
            "query",
            "description",
            "title",
            "issue",
            "request",
        ],
        "required_runtime_any": [
            "survival",
            "resolution",
            "time",
            "hazard",
            "lognormal",
        ],
        "required_output_any": [
            "resolution",
            "time",
            "survival",
            "prediction",
        ],
        "artifact_required": True,
        "reference_dependency": False,
    },
}


def lower_list(values):
    return [
        str(value).lower()
        for value in values
    ]


def contains_any(
    values,
    required_terms,
):
    values_lower = lower_list(values)

    for term in required_terms:
        term_lower = term.lower()

        if any(
            term_lower in value
            for value in values_lower
        ):
            return True

    return False


def evaluate_candidate(
    task,
    candidate,
):
    requirements = TASK_REQUIREMENTS[task]

    input_hits = candidate.get(
        "input_hits",
        [],
    )

    runtime_hits = candidate.get(
        "runtime_hits",
        [],
    )

    artifact_hits = candidate.get(
        "artifact_hits",
        [],
    )

    output_hits = (
        candidate.get(
            "return_expressions",
            [],
        )
        + candidate.get(
            "runtime_hits",
            [],
        )
    )

    input_ok = contains_any(
        input_hits,
        requirements["required_input_any"],
    )

    runtime_ok = contains_any(
        runtime_hits,
        requirements["required_runtime_any"],
    )

    output_ok = contains_any(
        output_hits,
        requirements["required_output_any"],
    )

    if requirements["artifact_required"]:
        artifact_ok = bool(
            artifact_hits
        )
    else:
        artifact_ok = True

    reference_ok = True

    if requirements[
        "reference_dependency"
    ]:
        reference_ok = (
            bool(
                candidate.get(
                    "historical_hits",
                    [],
                )
            )
            or task == "T6"
        )

    evidence_count = sum(
        [
            input_ok,
            runtime_ok,
            output_ok,
            artifact_ok,
            reference_ok,
        ]
    )

    return {
        "input_contract_signal":
            input_ok,

        "runtime_signal":
            runtime_ok,

        "output_contract_signal":
            output_ok,

        "artifact_binding_signal":
            artifact_ok,

        "reference_dependency_signal":
            reference_ok,

        "evidence_count":
            evidence_count,

        "contract_status":
            (
                "STRONG_CANDIDATE"
                if evidence_count >= 4
                else "INSUFFICIENT_SOURCE_EVIDENCE"
            ),
    }


def main():

    print("=" * 72)
    print(
        "H-OP-007 — FINAL RUNTIME CONTRACT RECONCILIATION"
    )
    print("=" * 72)

    if not INPUT.exists():
        raise FileNotFoundError(
            f"Missing H-OP-006 output: {INPUT}"
        )

    source = json.loads(
        INPUT.read_text(
            encoding="utf-8"
        )
    )

    task_results = {}
    final_contract_candidates = {}

    for task in TASKS:

        candidates = (
            source
            .get("task_results", {})
            .get(task, {})
            .get("candidates", [])
        )

        evaluated = []

        for candidate in candidates:

            evaluation = evaluate_candidate(
                task,
                candidate,
            )

            evaluated.append(
                {
                    "path":
                        candidate.get(
                            "path"
                        ),

                    "function":
                        candidate.get(
                            "function"
                        ),

                    "parameters":
                        candidate.get(
                            "parameters",
                            [],
                        ),

                    "artifact_hits":
                        candidate.get(
                            "artifact_hits",
                            [],
                        ),

                    "runtime_hits":
                        candidate.get(
                            "runtime_hits",
                            [],
                        ),

                    "input_hits":
                        candidate.get(
                            "input_hits",
                            [],
                        ),

                    "historical_hits":
                        candidate.get(
                            "historical_hits",
                            [],
                        ),

                    "return_expressions":
                        candidate.get(
                            "return_expressions",
                            [],
                        ),

                    "evaluation":
                        evaluation,
                }
            )

        evaluated = sorted(
            evaluated,
            key=lambda x: (
                x["evaluation"][
                    "evidence_count"
                ],
                len(
                    x["artifact_hits"]
                ),
                len(
                    x["runtime_hits"]
                ),
            ),
            reverse=True,
        )

        strong = [
            candidate
            for candidate in evaluated
            if candidate[
                "evaluation"
            ][
                "contract_status"
            ]
            == "STRONG_CANDIDATE"
        ]

        # A source-level winner is only declared when exactly
        # one candidate has the highest evidence count.
        unique_top = False
        selected = None

        if strong:

            top_score = strong[0][
                "evaluation"
            ][
                "evidence_count"
            ]

            top = [
                candidate
                for candidate in strong
                if candidate[
                    "evaluation"
                ][
                    "evidence_count"
                ]
                == top_score
            ]

            if len(top) == 1:

                unique_top = True
                selected = top[0]

        if selected is not None:

            selection_status = (
                "SOURCE_CONTRACT_CANDIDATE_IDENTIFIED"
            )

        elif strong:

            selection_status = (
                "MULTIPLE_STRONG_CANDIDATES"
            )

        else:

            selection_status = (
                "NO_STRONG_SOURCE_CANDIDATE"
            )

        task_results[task] = {
            "inspected_candidates":
                len(evaluated),

            "strong_candidates":
                len(strong),

            "unique_top_candidate":
                unique_top,

            "selection_status":
                selection_status,

            "top_candidates":
                evaluated[:5],
        }

        if selected is not None:

            final_contract_candidates[
                task
            ] = {
                "path":
                    selected["path"],

                "function":
                    selected["function"],

                "parameters":
                    selected["parameters"],

                "artifact_hits":
                    selected["artifact_hits"],

                "runtime_hits":
                    selected["runtime_hits"],

                "input_hits":
                    selected["input_hits"],

                "historical_hits":
                    selected["historical_hits"],

                "evidence_count":
                    selected[
                        "evaluation"
                    ][
                        "evidence_count"
                    ],
            }

    # --------------------------------------------------------------
    # Runtime contract status.
    # --------------------------------------------------------------

    contract_count = len(
        final_contract_candidates
    )

    if contract_count == 7:

        overall_status = (
            "ALL_TASKS_HAVE_SOURCE_CONTRACT_CANDIDATES"
        )

    else:

        overall_status = (
            "ADDITIONAL_SOURCE_RECONCILIATION_REQUIRED"
        )

    result = {

        "operation":
            "H-OP-007",

        "operation_name":
            "Final Runtime Contract Reconciliation",

        "status":
            "PASS",

        "overall_contract_status":
            overall_status,

        "task_contract_candidate_count":
            contract_count,

        "task_results":
            task_results,

        "final_contract_candidates":
            final_contract_candidates,

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

            "production_orchestrator_created":
                False,
        },

        "boundary": (
            "H-OP-007 identifies source-level callable "
            "candidates only. A candidate is not treated as "
            "production-ready until its exact runtime behavior "
            "is exercised against a controlled non-locked-test "
            "single-ticket probe."
        ),

        "next_operation": (
            "H-OP-008 — controlled single-ticket runtime "
            "probe using the reconciled callable candidates."
        ),

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
            f"strong="
            f"{data['strong_candidates']} "
            f"unique="
            f"{data['unique_top_candidate']} "
            f"status="
            f"{data['selection_status']}"
        )

    print()

    print(
        f"CONTRACT CANDIDATES: "
        f"{contract_count}/7"
    )

    print(
        f"OVERALL: {overall_status}"
    )

    print(
        f"OUTPUT: {OUTPUT}"
    )

    print(
        "STATUS: PASS"
    )


if __name__ == "__main__":
    main()