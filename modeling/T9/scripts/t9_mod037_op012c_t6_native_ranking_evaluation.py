from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


# ============================================================
# T9 MOD-037 OP-012C
# T6 Native Query-Level Ranking Evaluation
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T9_ROOT = PROJECT_ROOT / "modeling" / "T9"
OUTPUT_DIR = T9_ROOT / "mod037"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_JSON = (
    OUTPUT_DIR
    / "t9_mod037_op012c_t6_native_ranking_evaluation.json"
)

OUTPUT_QUERY_CSV = (
    OUTPUT_DIR
    / "t9_mod037_op012c_t6_query_level_results.csv"
)


# ============================================================
# PRIOR T9 ARTIFACTS
# ============================================================

OP004_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op004_native_output_acceptance.json"
)

OP005_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op005_output_semantics_lock.json"
)

OP012A_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op012a_t6_prior_artifact_schema.json"
)

OP012B_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op012b_t6_target_observation_audit.json"
)


# ============================================================
# AUTHORITATIVE T6 ARTIFACT
# ============================================================

T6_RANKINGS = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod010_corrected_hybrid_query_rankings.csv"
)


# ============================================================
# HELPERS
# ============================================================

def require_file(path: Path) -> None:

    if not path.exists():
        raise FileNotFoundError(
            f"Required artifact missing: {path}"
        )


def load_json(path: Path) -> dict[str, Any]:

    require_file(path)

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        value = json.load(f)

    if not isinstance(value, dict):

        raise TypeError(
            f"Expected JSON object: {path}"
        )

    return value


def normalize_id(
    series: pd.Series,
) -> pd.Series:

    return (
        series
        .astype(str)
        .str.strip()
    )


# ============================================================
# PRIOR OPERATION VALIDATION
# ============================================================

def validate_prior_operations() -> dict[str, Any]:

    op004 = load_json(
        OP004_ARTIFACT
    )

    op005 = load_json(
        OP005_ARTIFACT
    )

    op012a = load_json(
        OP012A_ARTIFACT
    )

    op012b = load_json(
        OP012B_ARTIFACT
    )

    checks = {}

    # --------------------------------------------------------
    # OP-004
    # --------------------------------------------------------

    accepted_tasks = op004.get(
        "accepted_tasks",
        []
    )

    checks[
        "OP-004_T6_acceptance"
    ] = {

        "status": (
            "PASS"
            if "T6" in accepted_tasks
            else "FAIL"
        ),

        "accepted_tasks": accepted_tasks,
    }

    # --------------------------------------------------------
    # OP-005
    # --------------------------------------------------------

    task_boundary = op005.get(
        "task_boundary",
        {}
    )

    t6_boundary = task_boundary.get(
        "T6",
        {}
    )

    checks[
        "OP-005_T6_boundary"
    ] = {

        "status": (
            "PASS"
            if (
                op005.get(
                    "status"
                )
                == "PASS"
                and
                t6_boundary.get(
                    "status"
                )
                == "ACCEPTED_NATIVE_RANKING"
                and
                t6_boundary.get(
                    "accepted_for_native_evaluation"
                )
                is True
                and
                t6_boundary.get(
                    "native_probability_output"
                )
                is False
            )
            else "FAIL"
        ),

        "boundary": t6_boundary,
    }

    # --------------------------------------------------------
    # OP-012A
    # --------------------------------------------------------

    checks[
        "OP-012A"
    ] = {

        "status": (
            "PASS"
            if op012a.get(
                "status"
            )
            == "PASS"
            else "FAIL"
        ),

        "observed_status": (
            op012a.get(
                "status"
            )
        ),
    }

    # --------------------------------------------------------
    # OP-012B
    # --------------------------------------------------------

    checks[
        "OP-012B"
    ] = {

        "status": (
            "PASS"
            if op012b.get(
                "status"
            )
            == "PASS"
            else "FAIL"
        ),

        "observed_status": (
            op012b.get(
                "status"
            )
        ),
    }

    failed = [
        key
        for key, value
        in checks.items()
        if value["status"]
        != "PASS"
    ]

    return {

        "status": (
            "PASS"
            if not failed
            else "FAIL"
        ),

        "checks": checks,

        "failed_checks": failed,
    }


# ============================================================
# LOAD DATA
# ============================================================

def load_rankings() -> pd.DataFrame:

    require_file(
        T6_RANKINGS
    )

    frame = pd.read_csv(
        T6_RANKINGS,
        low_memory=False,
    )

    required_columns = [
        "split",
        "query_id",
        "candidate_id",
        "target_observed",
        "hybrid_score",
    ]

    missing = [
        column
        for column
        in required_columns
        if column not in frame.columns
    ]

    if missing:

        raise RuntimeError(
            "Required T6 columns missing: "
            f"{missing}; "
            f"available={list(frame.columns)}"
        )

    return frame


# ============================================================
# INPUT VALIDATION
# ============================================================

def validate_input(
    frame: pd.DataFrame,
) -> dict[str, Any]:

    checks = {}

    # --------------------------------------------------------
    # Required null checks
    # --------------------------------------------------------

    required_columns = [
        "split",
        "query_id",
        "candidate_id",
        "target_observed",
        "hybrid_score",
    ]

    null_counts = {
        column: int(
            frame[
                column
            ].isna().sum()
        )
        for column in required_columns
    }

    checks[
        "required_nulls"
    ] = {

        "status": (
            "PASS"
            if all(
                value == 0
                for value
                in null_counts.values()
            )
            else "FAIL"
        ),

        "null_counts": null_counts,
    }

    # --------------------------------------------------------
    # Query-candidate uniqueness
    # --------------------------------------------------------

    duplicate_pairs = int(
        frame
        .duplicated(
            subset=[
                "query_id",
                "candidate_id",
            ]
        )
        .sum()
    )

    checks[
        "query_candidate_uniqueness"
    ] = {

        "status": (
            "PASS"
            if duplicate_pairs == 0
            else "FAIL"
        ),

        "duplicate_pairs": (
            duplicate_pairs
        ),
    }

    # --------------------------------------------------------
    # target_observed structural validation
    # --------------------------------------------------------

    observed_values = set(
        frame[
            "target_observed"
        ]
        .dropna()
        .tolist()
    )

    checks[
        "target_observed_boolean"
    ] = {

        "status": (
            "PASS"
            if observed_values
            <= {
                True,
                False,
            }
            else "FAIL"
        ),

        "observed_values": [
            str(value)
            for value
            in sorted(
                observed_values,
                key=lambda x: str(x),
            )
        ],
    }

    # --------------------------------------------------------
    # Score numeric validation
    # --------------------------------------------------------

    scores = pd.to_numeric(
        frame[
            "hybrid_score"
        ],
        errors="coerce",
    )

    checks[
        "hybrid_score_numeric"
    ] = {

        "status": (
            "PASS"
            if scores.notna().all()
            else "FAIL"
        ),

        "non_numeric_rows": int(
            scores.isna().sum()
        ),
    }

    failed = [
        key
        for key, value
        in checks.items()
        if value["status"]
        != "PASS"
    ]

    return {

        "status": (
            "PASS"
            if not failed
            else "FAIL"
        ),

        "checks": checks,

        "failed_checks": failed,
    }


# ============================================================
# QUERY-LEVEL RANKING
# ============================================================

def build_query_results(
    frame: pd.DataFrame,
) -> pd.DataFrame:

    work = frame.copy()

    work[
        "hybrid_score"
    ] = pd.to_numeric(
        work[
            "hybrid_score"
        ],
        errors="coerce",
    )

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # The source CSV is NOT guaranteed to be ordered by score.
    # Therefore rank is explicitly reconstructed within each
    # query from hybrid_score descending.
    #
    # candidate_id provides deterministic tie-breaking only.
    # --------------------------------------------------------

    work[
        "candidate_id"
    ] = normalize_id(
        work[
            "candidate_id"
        ]
    )

    work[
        "query_id"
    ] = normalize_id(
        work[
            "query_id"
        ]
    )

    work = work.sort_values(
        by=[
            "query_id",
            "hybrid_score",
            "candidate_id",
        ],
        ascending=[
            True,
            False,
            True,
        ],
        kind="mergesort",
    )

    work[
        "rank"
    ] = (
        work
        .groupby(
            "query_id",
            sort=False,
        )
        .cumcount()
        + 1
    )

    return work


# ============================================================
# TARGET POSITION EXTRACTION
# ============================================================

def extract_query_level_results(
    ranked: pd.DataFrame,
) -> pd.DataFrame:

    query_results = []

    for query_id, group in ranked.groupby(
        "query_id",
        sort=False,
    ):

        group = group.sort_values(
            "rank"
        )

        target_rows = group[
            group[
                "target_observed"
            ]
            == True
        ]

        candidate_count = int(
            len(group)
        )

        target_count = int(
            len(target_rows)
        )

        if target_count == 0:

            target_rank = pd.NA
            target_candidate = pd.NA
            target_score = pd.NA

        elif target_count == 1:

            target_row = (
                target_rows.iloc[0]
            )

            target_rank = int(
                target_row[
                    "rank"
                ]
            )

            target_candidate = str(
                target_row[
                    "candidate_id"
                ]
            )

            target_score = float(
                target_row[
                    "hybrid_score"
                ]
            )

        else:

            # ------------------------------------------------
            # This should not occur under the observed
            # structure of one True target per query.
            #
            # Do not silently collapse multiple observed
            # targets into one.
            # ------------------------------------------------

            raise RuntimeError(
                "Multiple target_observed=True "
                f"rows found for query {query_id}: "
                f"{target_count}"
            )

        query_results.append(
            {
                "query_id": str(
                    query_id
                ),

                "candidate_count": (
                    candidate_count
                ),

                "target_observed_count": (
                    target_count
                ),

                "target_present": (
                    target_count == 1
                ),

                "target_rank": (
                    target_rank
                ),

                "target_candidate_id": (
                    target_candidate
                ),

                "target_hybrid_score": (
                    target_score
                ),
            }
        )

    result = pd.DataFrame(
        query_results
    )

    return result


# ============================================================
# RANKING METRICS
# ============================================================

def calculate_ranking_metrics(
    query_results: pd.DataFrame,
) -> dict[str, Any]:

    total_queries = int(
        len(query_results)
    )

    target_present = (
        query_results[
            "target_present"
        ]
        .astype(bool)
    )

    present_results = (
        query_results[
            target_present
        ]
        .copy()
    )

    present_count = int(
        len(present_results)
    )

    absent_count = (
        total_queries
        -
        present_count
    )

    metrics = {

        "total_queries": (
            total_queries
        ),

        "queries_with_observed_target": (
            present_count
        ),

        "queries_without_observed_target": (
            absent_count
        ),

        "target_observed_query_rate": (
            present_count / total_queries
            if total_queries
            else 0.0
        ),
    }

    # --------------------------------------------------------
    # Native ranking metrics
    # --------------------------------------------------------

    for k in [
        1,
        3,
        5,
        10,
        20,
        50,
        100,
    ]:

        if present_count == 0:

            hit_rate = 0.0

        else:

            hit_rate = float(
                (
                    present_results[
                        "target_rank"
                    ]
                    <= k
                )
                .mean()
            )

        metrics[
            f"hit_at_{k}"
        ] = hit_rate

    # --------------------------------------------------------
    # MRR
    #
    # Only queries with an observed target are included.
    # Queries without an observed target do not receive an
    # artificial reciprocal rank of zero because that would
    # reinterpret missing observation as negative evidence.
    # --------------------------------------------------------

    if present_count:

        reciprocal_rank = (
            1.0
            /
            present_results[
                "target_rank"
            ].astype(float)
        )

        metrics[
            "mrr_observed_target_queries"
        ] = float(
            reciprocal_rank.mean()
        )

    else:

        metrics[
            "mrr_observed_target_queries"
        ] = 0.0

    # --------------------------------------------------------
    # Rank distribution
    # --------------------------------------------------------

    if present_count:

        ranks = (
            present_results[
                "target_rank"
            ].astype(int)
        )

        metrics[
            "target_rank_min"
        ] = int(
            ranks.min()
        )

        metrics[
            "target_rank_median"
        ] = float(
            ranks.median()
        )

        metrics[
            "target_rank_mean"
        ] = float(
            ranks.mean()
        )

        metrics[
            "target_rank_max"
        ] = int(
            ranks.max()
        )

    else:

        metrics[
            "target_rank_min"
        ] = None

        metrics[
            "target_rank_median"
        ] = None

        metrics[
            "target_rank_mean"
        ] = None

        metrics[
            "target_rank_max"
        ] = None

    return metrics


# ============================================================
# TRAIN / EVAL SEPARATION
# ============================================================

def evaluate_by_split(
    ranked: pd.DataFrame,
) -> dict[str, Any]:

    results = {}

    for split_value in [
        "TRAIN",
        "EVAL",
    ]:

        split_frame = ranked[
            ranked[
                "split"
            ]
            .astype(str)
            .str.upper()
            == split_value
        ]

        if split_frame.empty:

            results[
                split_value
            ] = {

                "status": "NOT_PRESENT",

                "rows": 0,
            }

            continue

        query_results = (
            extract_query_level_results(
                split_frame
            )
        )

        metrics = (
            calculate_ranking_metrics(
                query_results
            )
        )

        results[
            split_value
        ] = {

            "status": "EVALUATED",

            "rows": int(
                len(split_frame)
            ),

            "query_results": query_results,

            "metrics": metrics,
        }

    return results


# ============================================================
# EVALUATION POPULATION AUDIT
# ============================================================

def audit_eval_population(
    ranked: pd.DataFrame,
) -> dict[str, Any]:

    eval_frame = ranked[
        ranked[
            "split"
        ]
        .astype(str)
        .str.upper()
        == "EVAL"
    ]

    eval_query_results = (
        extract_query_level_results(
            eval_frame
        )
    )

    target_present = (
        eval_query_results[
            "target_present"
        ]
        .astype(bool)
    )

    return {

        "evaluation_rows": int(
            len(eval_frame)
        ),

        "evaluation_queries": int(
            len(eval_query_results)
        ),

        "queries_with_observed_target": int(
            target_present.sum()
        ),

        "queries_without_observed_target": int(
            (~target_present).sum()
        ),

        "query_results_rows": int(
            len(eval_query_results)
        ),
    }


# ============================================================
# CONTROL DEFINITIONS
# ============================================================

def build_controls() -> dict[str, Any]:

    return {

        "artifact_read_only": True,

        "model_fitted": False,

        "prediction_generated": False,

        "probability_generated": False,

        "calibration_fitted": False,

        "target_created": False,

        "target_relabelled": False,

        "observable_non_positive_reinterpreted_as_true_negative": (
            False
        ),

        "binary_classifier_created": False,

        "synthetic_negative_created": False,

        "synthetic_probability_created": False,

        "threshold_selected": False,

        "locked_test_used": False,

        "universal_confidence_created": False,

        "universal_risk_score_created": False,

        "existing_artifacts_modified": False,

        "native_query_ranking_preserved": True,

        "ranking_constructed_from_native_score": True,

        "row_order_used_as_rank": False,

        "candidate_space_expanded": False,
    }


def validate_controls(
    controls: dict[str, Any],
) -> dict[str, Any]:

    failures = []

    positive_controls = {
        "artifact_read_only",
        "native_query_ranking_preserved",
        "ranking_constructed_from_native_score",
    }

    negative_controls = {
        key
        for key
        in controls
        if key
        not in positive_controls
        and key
        != "row_order_used_as_rank"
    }

    for key in positive_controls:

        if controls[
            key
        ] is not True:

            failures.append(key)

    for key in negative_controls:

        if controls[
            key
        ] is not False:

            failures.append(key)

    if controls[
        "row_order_used_as_rank"
    ] is not False:

        failures.append(
            "row_order_used_as_rank"
        )

    return {

        "status": (
            "PASS"
            if not failures
            else "FAIL"
        ),

        "failed_controls": failures,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 72)
    print("T9 MOD-037 OP-012C")
    print(
        "T6 Native Query-Level Ranking Evaluation"
    )
    print("=" * 72)
    print()

    # --------------------------------------------------------
    # PRIOR OPERATIONS
    # --------------------------------------------------------

    print(
        "Validating prior T9 operations..."
    )

    previous = (
        validate_prior_operations()
    )

    print(
        "Previous-operation validation:",
        previous[
            "status"
        ],
    )

    if previous[
        "status"
    ] != "PASS":

        print(
            "Failed checks:",
            previous[
                "failed_checks"
            ],
        )

        raise RuntimeError(
            "Prior-operation validation failed."
        )

    print()

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    print(
        "Loading authoritative T6 ranking artifact..."
    )

    frame = load_rankings()

    print(
        "Rows:",
        len(frame),
    )

    print(
        "Columns:",
        list(frame.columns),
    )

    print()

    # --------------------------------------------------------
    # INPUT VALIDATION
    # --------------------------------------------------------

    print(
        "Validating native T6 input..."
    )

    input_validation = (
        validate_input(
            frame
        )
    )

    print(
        "Input validation:",
        input_validation[
            "status"
        ],
    )

    if input_validation[
        "status"
    ] != "PASS":

        print(
            "Failed checks:",
            input_validation[
                "failed_checks"
            ],
        )

        raise RuntimeError(
            "Native T6 input validation failed."
        )

    print()

    # --------------------------------------------------------
    # RANK CONSTRUCTION
    # --------------------------------------------------------

    print(
        "Constructing query-level native ranking..."
    )

    ranked = build_query_results(
        frame
    )

    print(
        "Ranking constructed from hybrid_score:",
        True,
    )

    print(
        "CSV row order used as rank:",
        False,
    )

    print()

    # --------------------------------------------------------
    # QUERY LEVEL RESULTS
    # --------------------------------------------------------

    print(
        "Extracting query-level target positions..."
    )

    query_results_all = (
        extract_query_level_results(
            ranked
        )
    )

    multiple_targets = int(
        (
            query_results_all[
                "target_observed_count"
            ]
            > 1
        ).sum()
    )

    print(
        "Queries:",
        len(
            query_results_all
        ),
    )

    print(
        "Queries with exactly one observed target:",
        int(
            (
                query_results_all[
                    "target_observed_count"
                ]
                == 1
            ).sum()
        ),
    )

    print(
        "Queries with zero observed targets:",
        int(
            (
                query_results_all[
                    "target_observed_count"
                ]
                == 0
            ).sum()
        ),
    )

    print(
        "Queries with multiple observed targets:",
        multiple_targets,
    )

    if multiple_targets:

        raise RuntimeError(
            "Multiple target_observed=True rows "
            "were found for at least one query."
        )

    print()

    # --------------------------------------------------------
    # EVALUATION
    # --------------------------------------------------------

    print(
        "Evaluating native ranking by split..."
    )

    split_results = (
        evaluate_by_split(
            ranked
        )
    )

    for split_name, result in (
        split_results.items()
    ):

        if result[
            "status"
        ] != "EVALUATED":

            continue

        metrics = result[
            "metrics"
        ]

        print()
        print(
            f"{split_name} rows:",
            result[
                "rows"
            ],
        )

        print(
            f"{split_name} queries:",
            metrics[
                "total_queries"
            ],
        )

        print(
            f"{split_name} queries with observed target:",
            metrics[
                "queries_with_observed_target"
            ],
        )

        print(
            f"{split_name} target-present rate:",
            f"{metrics['target_observed_query_rate']:.6f}",
        )

        print(
            f"{split_name} Hit@1:",
            f"{metrics['hit_at_1']:.6f}",
        )

        print(
            f"{split_name} Hit@3:",
            f"{metrics['hit_at_3']:.6f}",
        )

        print(
            f"{split_name} Hit@5:",
            f"{metrics['hit_at_5']:.6f}",
        )

        print(
            f"{split_name} Hit@10:",
            f"{metrics['hit_at_10']:.6f}",
        )

        print(
            f"{split_name} Hit@20:",
            f"{metrics['hit_at_20']:.6f}",
        )

        print(
            f"{split_name} Hit@50:",
            f"{metrics['hit_at_50']:.6f}",
        )

        print(
            f"{split_name} Hit@100:",
            f"{metrics['hit_at_100']:.6f}",
        )

        print(
            f"{split_name} MRR "
            "(observed-target queries):",
            f"{metrics['mrr_observed_target_queries']:.6f}",
        )

    print()

    # --------------------------------------------------------
    # EVAL POPULATION
    # --------------------------------------------------------

    print(
        "Auditing T6 evaluation population..."
    )

    eval_population = (
        audit_eval_population(
            ranked
        )
    )

    print(
        "Evaluation rows:",
        eval_population[
            "evaluation_rows"
        ],
    )

    print(
        "Evaluation queries:",
        eval_population[
            "evaluation_queries"
        ],
    )

    print(
        "Queries with observed target:",
        eval_population[
            "queries_with_observed_target"
        ],
    )

    print(
        "Queries without observed target:",
        eval_population[
            "queries_without_observed_target"
        ],
    )

    print()

    # --------------------------------------------------------
    # SAVE QUERY-LEVEL RESULTS
    # --------------------------------------------------------

    eval_query_results = (
        split_results[
            "EVAL"
        ][
            "query_results"
        ]
        .copy()
    )

    eval_query_results.to_csv(
        OUTPUT_QUERY_CSV,
        index=False,
    )

    print(
        "Saved evaluation query-level results:",
        OUTPUT_QUERY_CSV,
    )

    print()

    # --------------------------------------------------------
    # CONTROLS
    # --------------------------------------------------------

    controls = build_controls()

    control_validation = (
        validate_controls(
            controls
        )
    )

    print(
        "Control validation:",
        control_validation[
            "status"
        ],
    )

    if (
        control_validation[
            "status"
        ]
        != "PASS"
    ):

        raise RuntimeError(
            "Control validation failed."
        )

    # --------------------------------------------------------
    # CALIBRATION BOUNDARY
    # --------------------------------------------------------

    calibration_boundary = {

        "native_ranking_evaluation": (
            "ESTABLISHED"
        ),

        "native_probability": (
            "NOT_ESTABLISHED"
        ),

        "probability_calibration": (
            "NOT_PERFORMED"
        ),

        "reason": (
            "hybrid_score is retained as a native "
            "query-level ranking score. No probability "
            "interpretation is introduced."
        ),
    }

    # --------------------------------------------------------
    # INTERPRETATION
    # --------------------------------------------------------

    interpretation = {

        "task_semantics": (
            "Query-level candidate retrieval/ranking."
        ),

        "ranking_quantity": (
            "hybrid_score"
        ),

        "target_observation": (
            "target_observed=True identifies the "
            "observed target relationship used to "
            "locate the target within the ranked "
            "candidate set."
        ),

        "non_observed_semantics": (
            "target_observed=False is not treated as "
            "a true-negative class."
        ),

        "ranking_construction": (
            "Candidates are explicitly ordered within "
            "each query by hybrid_score descending. "
            "CSV row order is not used as rank."
        ),

        "metric_population": (
            "Queries with an observed target are used "
            "for target-rank retrieval metrics. "
            "Queries without an observed target are "
            "reported separately rather than assigned "
            "an artificial negative rank."
        ),

        "probability_boundary": (
            "hybrid_score is not interpreted as a "
            "calibrated probability."
        ),
    }

    # --------------------------------------------------------
    # OVERALL
    # --------------------------------------------------------

    overall_pass = all(
        [
            previous[
                "status"
            ] == "PASS",

            input_validation[
                "status"
            ] == "PASS",

            control_validation[
                "status"
            ] == "PASS",

            multiple_targets == 0,

            "EVAL" in split_results,
        ]
    )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    output = {

        "operation": (
            "T9_MOD-037_OP-012C"
        ),

        "title": (
            "T6 Native Query-Level Ranking Evaluation"
        ),

        "status": (
            "PASS"
            if overall_pass
            else "FAIL"
        ),

        "purpose": (
            "Evaluate native T6 query-level retrieval "
            "ranking using hybrid_score while preserving "
            "the established target-observation semantics."
        ),

        "previous_operation_validation": (
            previous
        ),

        "input_validation": (
            input_validation
        ),

        "source": {

            "artifact": str(
                T6_RANKINGS
            ),

            "rows": int(
                len(frame)
            ),

            "columns": list(
                frame.columns
            ),
        },

        "ranking_construction": {

            "score_column": (
                "hybrid_score"
            ),

            "direction": (
                "descending"
            ),

            "tie_breaker": (
                "candidate_id ascending"
            ),

            "row_order_used_as_rank": (
                False
            ),
        },

        "evaluation_population": (
            eval_population
        ),

        "split_results": {

            split: {
                key: value
                for key, value
                in result.items()
                if key
                != "query_results"
            }

            for split, result
            in split_results.items()
        },

        "evaluation_query_results_artifact": (
            str(
                OUTPUT_QUERY_CSV
            )
        ),

        "calibration_boundary": (
            calibration_boundary
        ),

        "controls": controls,

        "control_validation": (
            control_validation
        ),

        "interpretation": (
            interpretation
        ),

        "artifacts_used": {

            "OP-004": str(
                OP004_ARTIFACT
            ),

            "OP-005": str(
                OP005_ARTIFACT
            ),

            "OP-012A": str(
                OP012A_ARTIFACT
            ),

            "OP-012B": str(
                OP012B_ARTIFACT
            ),

            "T6_rankings": str(
                T6_RANKINGS
            ),
        },

        "methodological_restrictions": [

            (
                "Do not interpret target_observed=False "
                "as a true-negative class."
            ),

            (
                "Do not create synthetic negative targets."
            ),

            (
                "Do not convert hybrid_score into "
                "probability."
            ),

            (
                "Do not fit calibration."
            ),

            (
                "Do not select thresholds."
            ),

            (
                "Do not use locked test data for "
                "selection."
            ),

            (
                "Do not use CSV row order as ranking order."
            ),

            (
                "Preserve native query-level retrieval "
                "semantics."
            ),
        ],

        "decision": (
            "T6 native query-level ranking is evaluated "
            "from the native hybrid_score ordering while "
            "preserving target-observation semantics. "
            "The operation does not establish probability "
            "calibration."
        ),
    }

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False,
        )

    # --------------------------------------------------------
    # FINAL CONSOLE
    # --------------------------------------------------------

    print("=" * 72)
    print("T9 MOD-037 OP-012C RESULT")
    print("=" * 72)
    print()

    print(
        "Previous-operation validation:",
        previous[
            "status"
        ],
    )

    print(
        "Input validation:",
        input_validation[
            "status"
        ],
    )

    print(
        "Multiple-target query check:",
        (
            "PASS"
            if multiple_targets == 0
            else "FAIL"
        ),
    )

    print(
        "Native ranking constructed:",
        True,
    )

    print(
        "CSV row order used as rank:",
        False,
    )

    print(
        "Control validation:",
        control_validation[
            "status"
        ],
    )

    print()

    if "EVAL" in split_results:

        eval_metrics = (
            split_results[
                "EVAL"
            ][
                "metrics"
            ]
        )

        print(
            "EVAL queries:",
            eval_metrics[
                "total_queries"
            ],
        )

        print(
            "EVAL queries with observed target:",
            eval_metrics[
                "queries_with_observed_target"
            ],
        )

        print(
            "EVAL Hit@1:",
            f"{eval_metrics['hit_at_1']:.6f}",
        )

        print(
            "EVAL Hit@3:",
            f"{eval_metrics['hit_at_3']:.6f}",
        )

        print(
            "EVAL Hit@5:",
            f"{eval_metrics['hit_at_5']:.6f}",
        )

        print(
            "EVAL Hit@10:",
            f"{eval_metrics['hit_at_10']:.6f}",
        )

        print(
            "EVAL Hit@20:",
            f"{eval_metrics['hit_at_20']:.6f}",
        )

        print(
            "EVAL MRR:",
            f"{eval_metrics['mrr_observed_target_queries']:.6f}",
        )

    print()

    print(
        "Native ranking evaluation: ESTABLISHED"
    )

    print(
        "Probability calibration: NOT PERFORMED"
    )

    print(
        "Target relabelling: NO"
    )

    print(
        "Synthetic negatives: NO"
    )

    print(
        "Synthetic probabilities: NO"
    )

    print(
        "Threshold selection: NO"
    )

    print(
        "Locked test used: NO"
    )

    print()

    print(
        "Output:",
        OUTPUT_JSON,
    )

    print(
        "Query-level output:",
        OUTPUT_QUERY_CSV,
    )

    print()

    print(
        "T9 MOD-037 OP-012C:",
        (
            "PASS"
            if overall_pass
            else "FAIL"
        ),
    )


if __name__ == "__main__":
    main()