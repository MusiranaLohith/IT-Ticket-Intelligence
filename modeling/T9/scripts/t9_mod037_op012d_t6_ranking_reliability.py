from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


# ============================================================
# T9 MOD-037 OP-012D
# T6 Ranking Reliability & Evaluation Evidence Audit
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
    / "t9_mod037_op012d_t6_ranking_reliability.json"
)

OUTPUT_CSV = (
    OUTPUT_DIR
    / "t9_mod037_op012d_t6_bootstrap_summary.csv"
)

QUERY_RESULTS = (
    OUTPUT_DIR
    / "t9_mod037_op012c_t6_query_level_results.csv"
)


# ============================================================
# PRIOR ARTIFACTS
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

OP012C_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op012c_t6_native_ranking_evaluation.json"
)


# ============================================================
# BOOTSTRAP CONFIGURATION
# ============================================================

BOOTSTRAP_REPLICATES = 2000
RANDOM_SEED = 37012
CI_LOWER = 0.025
CI_UPPER = 0.975


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

    op012c = load_json(
        OP012C_ARTIFACT
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

    t6_boundary = (
        op005
        .get(
            "task_boundary",
            {}
        )
        .get(
            "T6",
            {}
        )
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

    # --------------------------------------------------------
    # OP-012C
    # --------------------------------------------------------

    checks[
        "OP-012C"
    ] = {

        "status": (
            "PASS"
            if op012c.get(
                "status"
            )
            == "PASS"
            else "FAIL"
        ),

        "observed_status": (
            op012c.get(
                "status"
            )
        ),
    }

    failed = [
        key
        for key, value
        in checks.items()
        if value["status"] != "PASS"
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
# LOAD QUERY-LEVEL RESULTS
# ============================================================

def load_query_results() -> pd.DataFrame:

    require_file(
        QUERY_RESULTS
    )

    frame = pd.read_csv(
        QUERY_RESULTS,
        low_memory=False,
    )

    required = [
        "query_id",
        "candidate_count",
        "target_observed_count",
        "target_present",
        "target_rank",
        "target_candidate_id",
        "target_hybrid_score",
    ]

    missing = [
        column
        for column in required
        if column not in frame.columns
    ]

    if missing:

        raise RuntimeError(
            "Required OP-012C query-level columns "
            f"missing: {missing}; "
            f"available={list(frame.columns)}"
        )

    return frame


# ============================================================
# QUERY-LEVEL INPUT VALIDATION
# ============================================================

def validate_query_results(
    frame: pd.DataFrame,
) -> dict[str, Any]:

    checks = {}

    # --------------------------------------------------------
    # Unique query IDs
    # --------------------------------------------------------

    duplicate_queries = int(
        frame[
            "query_id"
        ]
        .duplicated()
        .sum()
    )

    checks[
        "query_id_uniqueness"
    ] = {

        "status": (
            "PASS"
            if duplicate_queries == 0
            else "FAIL"
        ),

        "duplicate_query_ids": (
            duplicate_queries
        ),
    }

    # --------------------------------------------------------
    # Target presence
    # --------------------------------------------------------

    target_present = (
        frame[
            "target_present"
        ]
        .astype(bool)
    )

    checks[
        "target_presence"
    ] = {

        "status": (
            "PASS"
            if target_present.all()
            else "FAIL"
        ),

        "queries": int(
            len(frame)
        ),

        "target_present_queries": int(
            target_present.sum()
        ),

        "target_absent_queries": int(
            (~target_present).sum()
        ),
    }

    # --------------------------------------------------------
    # Target count
    # --------------------------------------------------------

    target_counts = pd.to_numeric(
        frame[
            "target_observed_count"
        ],
        errors="coerce",
    )

    checks[
        "single_observed_target"
    ] = {

        "status": (
            "PASS"
            if (
                target_counts
                .eq(1)
                .all()
            )
            else "FAIL"
        ),

        "non_single_target_queries": int(
            (~target_counts.eq(1)).sum()
        ),
    }

    # --------------------------------------------------------
    # Rank validity
    # --------------------------------------------------------

    ranks = pd.to_numeric(
        frame[
            "target_rank"
        ],
        errors="coerce",
    )

    checks[
        "rank_validity"
    ] = {

        "status": (
            "PASS"
            if (
                ranks.notna().all()
                and
                (ranks >= 1).all()
                and
                np.isfinite(
                    ranks
                ).all()
            )
            else "FAIL"
        ),

        "null_ranks": int(
            ranks.isna().sum()
        ),

        "rank_below_one": int(
            (ranks < 1).sum()
        ),
    }

    failed = [
        key
        for key, value
        in checks.items()
        if value["status"] != "PASS"
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
# METRIC FUNCTIONS
# ============================================================

def metric_hit_at_k(
    ranks: np.ndarray,
    k: int,
) -> float:

    return float(
        np.mean(
            ranks <= k
        )
    )


def metric_mrr(
    ranks: np.ndarray,
) -> float:

    return float(
        np.mean(
            1.0 / ranks
        )
    )


# ============================================================
# POINT ESTIMATES
# ============================================================

def calculate_point_estimates(
    ranks: np.ndarray,
) -> dict[str, float]:

    metrics = {}

    for k in [
        1,
        3,
        5,
        10,
        20,
        50,
        100,
    ]:

        metrics[
            f"hit_at_{k}"
        ] = metric_hit_at_k(
            ranks,
            k,
        )

    metrics[
        "mrr"
    ] = metric_mrr(
        ranks
    )

    return metrics


# ============================================================
# BOOTSTRAP
# ============================================================

def bootstrap_metrics(
    ranks: np.ndarray,
) -> pd.DataFrame:

    rng = np.random.default_rng(
        RANDOM_SEED
    )

    n = len(ranks)

    rows = []

    for replicate in range(
        BOOTSTRAP_REPLICATES
    ):

        sampled_indices = (
            rng.integers(
                0,
                n,
                size=n,
            )
        )

        sampled = ranks[
            sampled_indices
        ]

        row = {
            "replicate": replicate,
        }

        for k in [
            1,
            3,
            5,
            10,
            20,
            50,
            100,
        ]:

            row[
                f"hit_at_{k}"
            ] = metric_hit_at_k(
                sampled,
                k,
            )

        row[
            "mrr"
        ] = metric_mrr(
            sampled
        )

        rows.append(
            row
        )

    return pd.DataFrame(
        rows
    )


# ============================================================
# BOOTSTRAP SUMMARY
# ============================================================

def summarize_bootstrap(
    bootstrap: pd.DataFrame,
    point_estimates: dict[str, float],
) -> pd.DataFrame:

    metric_names = [
        "hit_at_1",
        "hit_at_3",
        "hit_at_5",
        "hit_at_10",
        "hit_at_20",
        "hit_at_50",
        "hit_at_100",
        "mrr",
    ]

    rows = []

    for metric in metric_names:

        values = bootstrap[
            metric
        ].to_numpy()

        rows.append(
            {

                "metric": metric,

                "point_estimate": (
                    point_estimates[
                        metric
                    ]
                ),

                "bootstrap_mean": float(
                    np.mean(
                        values
                    )
                ),

                "bootstrap_std": float(
                    np.std(
                        values,
                        ddof=1,
                    )
                ),

                "ci_lower_95": float(
                    np.quantile(
                        values,
                        CI_LOWER,
                    )
                ),

                "ci_upper_95": float(
                    np.quantile(
                        values,
                        CI_UPPER,
                    )
                ),

                "replicates": int(
                    len(values)
                ),
            }
        )

    return pd.DataFrame(
        rows
    )


# ============================================================
# RANK DISTRIBUTION
# ============================================================

def summarize_rank_distribution(
    ranks: np.ndarray,
) -> dict[str, Any]:

    return {

        "queries": int(
            len(ranks)
        ),

        "minimum_rank": int(
            np.min(ranks)
        ),

        "maximum_rank": int(
            np.max(ranks)
        ),

        "mean_rank": float(
            np.mean(ranks)
        ),

        "median_rank": float(
            np.median(ranks)
        ),

        "q25_rank": float(
            np.quantile(
                ranks,
                0.25,
            )
        ),

        "q75_rank": float(
            np.quantile(
                ranks,
                0.75,
            )
        ),

        "q90_rank": float(
            np.quantile(
                ranks,
                0.90,
            )
        ),

        "q95_rank": float(
            np.quantile(
                ranks,
                0.95,
            )
        ),
    }


# ============================================================
# TRAIN/EVAL DESCRIPTIVE COMPARISON
# ============================================================

def evaluate_split(
    split_name: str,
) -> dict[str, Any]:

    path = (
        PROJECT_ROOT
        / "modeling"
        / "T6"
        / "metrics"
        / "t6_mod010_corrected_hybrid_query_rankings.csv"
    )

    frame = pd.read_csv(
        path,
        low_memory=False,
    )

    split_frame = frame[
        frame[
            "split"
        ]
        .astype(str)
        .str.upper()
        == split_name
    ].copy()

    split_frame[
        "hybrid_score"
    ] = pd.to_numeric(
        split_frame[
            "hybrid_score"
        ],
        errors="coerce",
    )

    split_frame[
        "query_id"
    ] = split_frame[
        "query_id"
    ].astype(str)

    split_frame[
        "candidate_id"
    ] = split_frame[
        "candidate_id"
    ].astype(str)

    split_frame = split_frame.sort_values(
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

    split_frame[
        "rank"
    ] = (
        split_frame
        .groupby(
            "query_id",
            sort=False,
        )
        .cumcount()
        + 1
    )

    target_rows = split_frame[
        split_frame[
            "target_observed"
        ]
        == True
    ].copy()

    target_counts = (
        target_rows[
            "query_id"
        ]
        .value_counts()
    )

    if not target_counts.eq(1).all():

        raise RuntimeError(
            f"{split_name} does not have exactly "
            "one observed target per query."
        )

    ranks = (
        target_rows[
            "rank"
        ]
        .astype(int)
        .to_numpy()
    )

    point = calculate_point_estimates(
        ranks
    )

    return {

        "rows": int(
            len(split_frame)
        ),

        "queries": int(
            split_frame[
                "query_id"
            ].nunique()
        ),

        "observed_target_queries": int(
            len(ranks)
        ),

        "metrics": point,

        "rank_distribution": (
            summarize_rank_distribution(
                ranks
            )
        ),
    }


# ============================================================
# CONTROLS
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

        "arbitrary_cross_task_weighting": False,

        "native_ranking_semantics_preserved": True,

        "query_level_bootstrap_used": True,

        "candidate_rows_resampled_as_independent_units": False,

        "existing_artifacts_modified": False,
    }


def validate_controls(
    controls: dict[str, Any],
) -> dict[str, Any]:

    positive = {
        "artifact_read_only",
        "native_ranking_semantics_preserved",
        "query_level_bootstrap_used",
    }

    negative = {
        key
        for key
        in controls
        if key not in positive
    }

    failures = []

    for key in positive:

        if controls[
            key
        ] is not True:

            failures.append(key)

    for key in negative:

        if controls[
            key
        ] is not False:

            failures.append(key)

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
    print("T9 MOD-037 OP-012D")
    print(
        "T6 Ranking Reliability & "
        "Evaluation Evidence Audit"
    )
    print("=" * 72)
    print()

    # --------------------------------------------------------
    # PRIOR VALIDATION
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
    # QUERY-LEVEL ARTIFACT
    # --------------------------------------------------------

    print(
        "Loading OP-012C query-level evaluation artifact..."
    )

    query_results = (
        load_query_results()
    )

    print(
        "Query-level rows:",
        len(query_results),
    )

    print()

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    print(
        "Validating query-level evaluation population..."
    )

    validation = (
        validate_query_results(
            query_results
        )
    )

    print(
        "Query-level validation:",
        validation[
            "status"
        ],
    )

    if validation[
        "status"
    ] != "PASS":

        print(
            "Failed checks:",
            validation[
                "failed_checks"
            ],
        )

        raise RuntimeError(
            "Query-level validation failed."
        )

    print()

    # --------------------------------------------------------
    # EVAL RANKS
    # --------------------------------------------------------

    ranks = pd.to_numeric(
        query_results[
            "target_rank"
        ],
        errors="coerce",
    ).astype(int).to_numpy()

    print(
        "EVAL observed-target queries:",
        len(ranks),
    )

    # --------------------------------------------------------
    # POINT ESTIMATES
    # --------------------------------------------------------

    point_estimates = (
        calculate_point_estimates(
            ranks
        )
    )

    print()
    print(
        "Point estimates:"
    )

    for metric, value in (
        point_estimates.items()
    ):

        print(
            f"{metric}: {value:.6f}"
        )

    print()

    # --------------------------------------------------------
    # RANK DISTRIBUTION
    # --------------------------------------------------------

    rank_distribution = (
        summarize_rank_distribution(
            ranks
        )
    )

    print(
        "Target-rank distribution:"
    )

    print(
        json.dumps(
            rank_distribution,
            indent=2,
        )
    )

    print()

    # --------------------------------------------------------
    # BOOTSTRAP
    # --------------------------------------------------------

    print(
        "Running query-level bootstrap..."
    )

    print(
        "Replicates:",
        BOOTSTRAP_REPLICATES,
    )

    print(
        "Seed:",
        RANDOM_SEED,
    )

    bootstrap = bootstrap_metrics(
        ranks
    )

    bootstrap_summary = (
        summarize_bootstrap(
            bootstrap,
            point_estimates,
        )
    )

    bootstrap_summary.to_csv(
        OUTPUT_CSV,
        index=False,
    )

    print(
        "Bootstrap summary saved:",
        OUTPUT_CSV,
    )

    print()

    print(
        "Bootstrap 95% intervals:"
    )

    for _, row in (
        bootstrap_summary.iterrows()
    ):

        print(
            f"{row['metric']}: "
            f"{row['point_estimate']:.6f} "
            f"["
            f"{row['ci_lower_95']:.6f}, "
            f"{row['ci_upper_95']:.6f}"
            f"]"
        )

    print()

    # --------------------------------------------------------
    # TRAIN / EVAL DESCRIPTIVE AUDIT
    # --------------------------------------------------------

    print(
        "Computing descriptive TRAIN/EVAL comparison..."
    )

    train_evaluation = {
        "TRAIN": evaluate_split(
            "TRAIN"
        ),

        "EVAL": evaluate_split(
            "EVAL"
        ),
    }

    print()

    for split_name, result in (
        train_evaluation.items()
    ):

        print(
            f"{split_name} queries:",
            result[
                "queries"
            ],
        )

        print(
            f"{split_name} MRR:",
            f"{result['metrics']['mrr']:.6f}",
        )

        print(
            f"{split_name} Hit@1:",
            f"{result['metrics']['hit_at_1']:.6f}",
        )

        print(
            f"{split_name} Hit@10:",
            f"{result['metrics']['hit_at_10']:.6f}",
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
    # RELIABILITY INTERPRETATION
    # --------------------------------------------------------

    reliability_interpretation = {

        "uncertainty_method": (
            "Query-level nonparametric bootstrap"
        ),

        "bootstrap_replicates": (
            BOOTSTRAP_REPLICATES
        ),

        "confidence_interval": (
            "Percentile 95% interval"
        ),

        "resampling_unit": (
            "Query"
        ),

        "why_query_level": (
            "T6 is a query-level retrieval/ranking "
            "task. Candidate rows belonging to the "
            "same query are therefore not treated as "
            "independent evaluation units."
        ),

        "point_estimates_preserved": True,

        "method_selection_performed": False,

        "threshold_selection_performed": False,

        "calibration_performed": False,
    }

    # --------------------------------------------------------
    # INTERPRETATION BOUNDARY
    # --------------------------------------------------------

    interpretation = {

        "native_ranking_evidence": (
            "ESTABLISHED"
        ),

        "ranking_uncertainty": (
            "QUANTIFIED_AT_QUERY_LEVEL"
        ),

        "probability_calibration": (
            "NOT_ESTABLISHED"
        ),

        "true_negative_semantics": (
            "NOT_ESTABLISHED_AND_NOT_ASSUMED"
        ),

        "model_selection": (
            "NOT_PERFORMED"
        ),

        "overall_method_selection": (
            "NOT_PERFORMED"
        ),

        "train_eval_comparison": (
            "DESCRIPTIVE_ONLY"
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

            validation[
                "status"
            ] == "PASS",

            control_validation[
                "status"
            ] == "PASS",

            len(
                bootstrap_summary
            ) == 8,
        ]
    )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    output = {

        "operation": (
            "T9_MOD-037_OP-012D"
        ),

        "title": (
            "T6 Ranking Reliability & "
            "Evaluation Evidence Audit"
        ),

        "status": (
            "PASS"
            if overall_pass
            else "FAIL"
        ),

        "purpose": (
            "Quantify query-level uncertainty around "
            "the already-established native T6 ranking "
            "metrics without changing task semantics, "
            "creating targets, or performing calibration."
        ),

        "previous_operation_validation": (
            previous
        ),

        "query_level_validation": (
            validation
        ),

        "evaluation_population": {

            "queries": int(
                len(ranks)
            ),

            "all_have_observed_target": True,

            "target_rank_min": int(
                np.min(ranks)
            ),

            "target_rank_max": int(
                np.max(ranks)
            ),
        },

        "point_estimates": (
            point_estimates
        ),

        "rank_distribution": (
            rank_distribution
        ),

        "bootstrap_configuration": {

            "replicates": (
                BOOTSTRAP_REPLICATES
            ),

            "seed": RANDOM_SEED,

            "confidence_level": 0.95,

            "method": (
                "Percentile bootstrap"
            ),

            "unit": "query",
        },

        "bootstrap_summary": (
            bootstrap_summary
            .to_dict(
                orient="records"
            )
        ),

        "train_eval_descriptive_comparison": (
            train_evaluation
        ),

        "reliability_interpretation": (
            reliability_interpretation
        ),

        "interpretation": (
            interpretation
        ),

        "controls": controls,

        "control_validation": (
            control_validation
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

            "OP-012C": str(
                OP012C_ARTIFACT
            ),

            "OP-012C_query_results": str(
                QUERY_RESULTS
            ),
        },

        "methodological_restrictions": [

            (
                "The query is the bootstrap resampling "
                "unit; candidate rows are not treated "
                "as independent observations."
            ),

            (
                "target_observed=False is not interpreted "
                "as a true negative."
            ),

            (
                "No synthetic targets are created."
            ),

            (
                "No probability is derived from "
                "hybrid_score."
            ),

            (
                "No calibration model is fitted."
            ),

            (
                "No threshold is selected."
            ),

            (
                "No model-selection decision is made "
                "from the bootstrap results."
            ),

            (
                "The TRAIN/EVAL comparison is descriptive "
                "only."
            ),

            (
                "No locked test data are used."
            ),
        ],

        "decision": (
            "T6 native ranking evidence is supported "
            "with query-level uncertainty estimates. "
            "The evidence remains native retrieval/"
            "ranking evidence; it does not establish "
            "ordinary binary probability calibration."
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
    print("T9 MOD-037 OP-012D RESULT")
    print("=" * 72)
    print()

    print(
        "Previous-operation validation:",
        previous[
            "status"
        ],
    )

    print(
        "Query-level validation:",
        validation[
            "status"
        ],
    )

    print(
        "Bootstrap replicates:",
        BOOTSTRAP_REPLICATES,
    )

    print(
        "Bootstrap unit: query"
    )

    print(
        "Control validation:",
        control_validation[
            "status"
        ],
    )

    print()

    print(
        "EVAL point estimates:"
    )

    for metric, value in (
        point_estimates.items()
    ):

        print(
            f"  {metric}: {value:.6f}"
        )

    print()

    print(
        "Probability calibration: NOT ESTABLISHED"
    )

    print(
        "True-negative reinterpretation: NO"
    )

    print(
        "Model selection: NO"
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
        "Bootstrap summary:",
        OUTPUT_CSV,
    )

    print()

    print(
        "T9 MOD-037 OP-012D:",
        (
            "PASS"
            if overall_pass
            else "FAIL"
        ),
    )


if __name__ == "__main__":
    main()