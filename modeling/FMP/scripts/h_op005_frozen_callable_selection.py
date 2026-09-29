from pathlib import Path
import ast
import json


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

MODELING_ROOT = PROJECT_ROOT / "modeling"
FMP_ROOT = MODELING_ROOT / "FMP"
METRICS_DIR = FMP_ROOT / "metrics"

INPUT = (
    METRICS_DIR
    / "h_op004_exact_callable_contract_reconciliation.json"
)

OUTPUT = (
    METRICS_DIR
    / "h_op005_frozen_callable_selection.json"
)


FROZEN_ARTIFACTS = {
    "T1": [
        "t1_it_support_char_svm.joblib",
    ],

    "T2": [
        "t2_class_weighted_tfidf_logreg.joblib",
    ],

    "T3": [
        "t3_class_weighted_tfidf_logreg.joblib",
    ],

    "T4": [
        "t4_mod007_tfidf.joblib",
        "t4_mod007_neighbors.joblib",
        "t4_mod007_full_retrieval.npz",
    ],

    "T5": [
        "t5_mod005_tfidf.joblib",
        "t5_mod005_logreg.joblib",
        "t5_mod007_calibrated_tfidf.joblib",
        "t5_mod007_calibration_models.joblib",
    ],

    "T6": [
        "t6_mod010_corrected_hybrid_results.json",
    ],

    "T7": [
        "t7_mod010_log_normal_aft_model.json",
    ],
}


TASK_OUTPUT_TERMS = {
    "T1": [
        "predict",
        "decision_function",
        "category",
        "class",
    ],

    "T2": [
        "predict",
        "priority",
        "class",
    ],

    "T3": [
        "predict",
        "severity",
        "class",
    ],

    "T4": [
        "neighbor",
        "retrieve",
        "candidate",
        "assignee",
        "rank",
    ],

    "T5": [
        "duplicate",
        "predict",
        "prob",
        "score",
    ],

    "T6": [
        "similar",
        "retrieve",
        "rank",
        "score",
        "candidate",
    ],

    "T7": [
        "survival",
        "time",
        "resolution",
        "hazard",
        "prediction",
    ],
}


def read_text(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def parse_functions(path):
    source = read_text(path)

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    functions = []

    for node in ast.walk(tree):

        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        try:
            source_segment = (
                ast.get_source_segment(
                    source,
                    node
                )
                or ""
            )
        except Exception:
            source_segment = ""

        functions.append(
            {
                "name": node.name,
                "parameters": [
                    arg.arg
                    for arg in node.args.args
                ],
                "source": source_segment,
            }
        )

    return functions


def score_function(
    task,
    function,
    artifact_hits,
):
    name = function["name"].lower()
    source = function["source"].lower()

    score = 0
    evidence = []

    # --------------------------------------------------------------
    # Frozen artifact evidence is the strongest signal.
    # --------------------------------------------------------------

    if artifact_hits:

        score += 20

        evidence.append(
            "frozen_artifact_reference"
        )

    # --------------------------------------------------------------
    # Task-specific runtime terms.
    # --------------------------------------------------------------

    output_hits = []

    for term in TASK_OUTPUT_TERMS[task]:

        if (
            term.lower() in name
            or term.lower() in source
        ):

            output_hits.append(term)

    if output_hits:

        score += min(
            len(set(output_hits)) * 3,
            12,
        )

        evidence.append(
            "task_output_signal"
        )

    # --------------------------------------------------------------
    # Input signals.
    # --------------------------------------------------------------

    input_terms = [
        "text",
        "ticket",
        "query",
        "description",
        "title",
        "subject",
        "body",
        "message",
        "issue",
        "request",
    ]

    input_hits = [
        term
        for term in input_terms
        if term in name
        or term in source
    ]

    if input_hits:

        score += min(
            len(set(input_hits)) * 2,
            10,
        )

        evidence.append(
            "ticket_or_text_input_signal"
        )

    # --------------------------------------------------------------
    # Actual inference/retrieval calls.
    # --------------------------------------------------------------

    inference_terms = [
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
    ]

    inference_hits = [
        term
        for term in inference_terms
        if term in source
    ]

    if inference_hits:

        score += min(
            len(set(inference_hits)) * 3,
            15,
        )

        evidence.append(
            "inference_or_retrieval_call"
        )

    # --------------------------------------------------------------
    # Historical/reference evidence.
    # --------------------------------------------------------------

    historical_terms = [
        "history",
        "historical",
        "reference",
        "corpus",
        "candidate",
        "neighbor",
        "retrieval",
        "index",
        "dataset",
    ]

    historical_hits = [
        term
        for term in historical_terms
        if term in source
    ]

    if historical_hits:

        score += min(
            len(set(historical_hits)),
            5,
        )

        evidence.append(
            "historical_reference_dependency"
        )

    # --------------------------------------------------------------
    # Return evidence.
    # --------------------------------------------------------------

    return {
        "score": score,
        "evidence": sorted(
            set(evidence)
        ),
        "output_hits": sorted(
            set(output_hits)
        ),
        "input_hits": sorted(
            set(input_hits)
        ),
        "inference_hits": sorted(
            set(inference_hits)
        ),
        "historical_hits": sorted(
            set(historical_hits)
        ),
    }


def main():

    print("=" * 72)
    print(
        "H-OP-005 — FROZEN CALLABLE SELECTION"
    )
    print("=" * 72)

    if not INPUT.exists():
        raise FileNotFoundError(
            f"Missing H-OP-004 output: {INPUT}"
        )

    h004 = json.loads(
        INPUT.read_text(
            encoding="utf-8"
        )
    )

    task_results = {}
    final_candidates = {}

    for task in FROZEN_ARTIFACTS:

        h004_task = h004[
            "task_results"
        ].get(
            task,
            {}
        )

        candidates = h004_task.get(
            "top_candidates",
            []
        )

        evaluated = []

        for candidate in candidates:

            path = Path(
                candidate["path"]
            )

            if not path.exists():
                continue

            source = read_text(path)

            artifact_hits = [
                artifact
                for artifact in FROZEN_ARTIFACTS[task]
                if artifact.lower()
                in source.lower()
            ]

            functions = parse_functions(
                path
            )

            for function in functions:

                scoring = score_function(
                    task,
                    function,
                    artifact_hits,
                )

                # Only retain meaningful candidates.
                if scoring["score"] <= 0:
                    continue

                evaluated.append(
                    {
                        "path": str(path),
                        "function": function[
                            "name"
                        ],
                        "parameters": function[
                            "parameters"
                        ],
                        "artifact_hits":
                            artifact_hits,
                        "score":
                            scoring["score"],
                        "evidence":
                            scoring["evidence"],
                        "output_hits":
                            scoring["output_hits"],
                        "input_hits":
                            scoring["input_hits"],
                        "inference_hits":
                            scoring["inference_hits"],
                        "historical_hits":
                            scoring["historical_hits"],
                    }
                )

        evaluated = sorted(
            evaluated,
            key=lambda x: (
                x["score"],
                len(x["artifact_hits"]),
                len(x["inference_hits"]),
                len(x["input_hits"]),
            ),
            reverse=True,
        )

        # Keep top candidates for evidence review.
        top = evaluated[:20]

        # Do NOT automatically declare a winner.
        #
        # A candidate is considered "strong" only when it has
        # direct frozen artifact evidence AND inference/retrieval
        # evidence.
        strong = [
            candidate
            for candidate in evaluated
            if candidate["artifact_hits"]
            and candidate["inference_hits"]
        ]

        task_results[task] = {
            "frozen_artifacts":
                FROZEN_ARTIFACTS[task],

            "evaluated_candidate_count":
                len(evaluated),

            "strong_candidate_count":
                len(strong),

            "top_candidates":
                top,
        }

        final_candidates[task] = [
            {
                "path":
                    candidate["path"],
                "function":
                    candidate["function"],
                "parameters":
                    candidate["parameters"],
                "score":
                    candidate["score"],
                "artifact_hits":
                    candidate["artifact_hits"],
                "inference_hits":
                    candidate["inference_hits"],
                "input_hits":
                    candidate["input_hits"],
                "historical_hits":
                    candidate["historical_hits"],
            }
            for candidate in strong[:5]
        ]

    # --------------------------------------------------------------
    # Determine whether the evidence is sufficient for a unique
    # callable selection.
    # --------------------------------------------------------------

    selection_summary = {}

    for task in FROZEN_ARTIFACTS:

        candidates = final_candidates[task]

        unique_selection = False

        if candidates:

            top_score = candidates[0][
                "score"
            ]

            top_matches = [
                candidate
                for candidate in candidates
                if candidate["score"]
                == top_score
            ]

            unique_selection = (
                len(top_matches) == 1
            )

        selection_summary[task] = {
            "strong_candidates":
                len(candidates),

            "unique_top_candidate":
                unique_selection,

            "selection_status":
                (
                    "UNIQUE_CANDIDATE"
                    if unique_selection
                    else
                    "REQUIRES_INTERFACE_REVIEW"
                ),
        }

    result = {

        "operation":
            "H-OP-005",

        "operation_name":
            "Frozen Callable Selection",

        "status":
            "PASS",

        "purpose": (
            "Reconcile H-OP-004 callable candidates against "
            "the exact frozen T1-T7 artifact bindings and "
            "source-level inference/retrieval evidence."
        ),

        "frozen_artifacts":
            FROZEN_ARTIFACTS,

        "task_results":
            task_results,

        "selection_summary":
            selection_summary,

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
            "This operation identifies source-level candidates "
            "with direct frozen-artifact and inference evidence. "
            "A unique candidate is not treated as production-ready "
            "until its exact input/output contract is manually "
            "reconciled. No model execution occurs in H-OP-005."
        ),

        "next_operation":
            "H-OP-006 — exact callable source inspection and "
            "single-ticket input/output contract confirmation.",

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
            indent=2,
        )

    # --------------------------------------------------------------
    # Compact terminal output.
    # --------------------------------------------------------------

    print()

    for task in FROZEN_ARTIFACTS:

        summary = selection_summary[
            task
        ]

        print(
            f"{task}: "
            f"strong_candidates="
            f"{summary['strong_candidates']} "
            f"unique_top="
            f"{summary['unique_top_candidate']} "
            f"status="
            f"{summary['selection_status']}"
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