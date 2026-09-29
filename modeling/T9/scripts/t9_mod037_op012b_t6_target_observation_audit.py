from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


# ============================================================
# T9 MOD-037 OP-012B
# T6 Target-Observation Semantics & Native Ranking
# Population Audit
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
    / "t9_mod037_op012b_t6_target_observation_audit.json"
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

T6_TRAIN = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "splits"
    / "t6_train_group_aware.csv"
)

T6_EVAL = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "splits"
    / "t6_eval_group_aware.csv"
)

T6_GROUP_AUDIT = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_group_aware_split_audit.json"
)

T6_GROUP_ASSIGNMENTS = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "derived"
    / "t6_content_group_assignments.csv"
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


def normalize_series(
    series: pd.Series,
) -> pd.Series:

    return (
        series
        .astype(str)
        .str.strip()
    )


def summarize_column(
    frame: pd.DataFrame,
    column: str,
) -> dict[str, Any]:

    series = frame[column]

    result = {

        "column": column,

        "dtype": str(
            series.dtype
        ),

        "rows": int(
            len(series)
        ),

        "non_null": int(
            series.notna().sum()
        ),

        "null": int(
            series.isna().sum()
        ),

        "unique": int(
            series.nunique(
                dropna=True
            )
        ),
    }

    counts = (
        series
        .value_counts(
            dropna=False
        )
    )

    result[
        "value_counts"
    ] = {
        str(key): int(value)
        for key, value
        in counts.items()
    }

    return result


def resolve_column(
    frame: pd.DataFrame,
    candidates: list[str],
    label: str,
) -> str:

    for candidate in candidates:

        if candidate in frame.columns:
            return candidate

    lowered = {
        str(column).lower(): column
        for column in frame.columns
    }

    for candidate in candidates:

        if candidate.lower() in lowered:

            return lowered[
                candidate.lower()
            ]

    raise RuntimeError(
        f"Could not resolve {label}. "
        f"Candidates={candidates}; "
        f"available={list(frame.columns)}"
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

    checks = {}

    # --------------------------------------------------------
    # OP-004 T6 acceptance
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

        "overall_status": op004.get(
            "status"
        ),
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
# LOAD NATIVE T6 DATA
# ============================================================

def load_t6_data() -> dict[str, pd.DataFrame]:

    require_file(
        T6_RANKINGS
    )

    require_file(
        T6_TRAIN
    )

    require_file(
        T6_EVAL
    )

    return {

        "rankings": pd.read_csv(
            T6_RANKINGS,
            low_memory=False,
        ),

        "train": pd.read_csv(
            T6_TRAIN,
            low_memory=False,
        ),

        "evaluation": pd.read_csv(
            T6_EVAL,
            low_memory=False,
        ),
    }


# ============================================================
# SCHEMA RESOLUTION
# ============================================================

def resolve_t6_schema(
    data: dict[str, pd.DataFrame],
) -> dict[str, Any]:

    rankings = data[
        "rankings"
    ]

    train = data[
        "train"
    ]

    evaluation = data[
        "evaluation"
    ]

    ranking_query_id = resolve_column(
        rankings,
        ["query_id"],
        "T6 ranking query ID",
    )

    ranking_candidate_id = resolve_column(
        rankings,
        ["candidate_id"],
        "T6 ranking candidate ID",
    )

    target_observed = resolve_column(
        rankings,
        ["target_observed"],
        "T6 target_observed",
    )

    hybrid_score = resolve_column(
        rankings,
        ["hybrid_score"],
        "T6 hybrid score",
    )

    split = resolve_column(
        rankings,
        ["split"],
        "T6 ranking split",
    )

    train_query_id = resolve_column(
        train,
        ["query_id", "id"],
        "T6 train query ID",
    )

    eval_query_id = resolve_column(
        evaluation,
        ["query_id", "id"],
        "T6 evaluation query ID",
    )

    return {

        "status": "PASS",

        "rankings": {

            "query_id": ranking_query_id,

            "candidate_id": ranking_candidate_id,

            "target_observed": target_observed,

            "hybrid_score": hybrid_score,

            "split": split,
        },

        "train": {

            "query_id": train_query_id,
        },

        "evaluation": {

            "query_id": eval_query_id,
        },
    }


# ============================================================
# TARGET_OBSERVED SEMANTICS
# ============================================================

def audit_target_observed(
    rankings: pd.DataFrame,
    column: str,
) -> dict[str, Any]:

    series = rankings[
        column
    ]

    result = {

        "column": column,

        "dtype": str(
            series.dtype
        ),

        "rows": int(
            len(series)
        ),

        "null_count": int(
            series.isna().sum()
        ),

        "unique_count": int(
            series.nunique(
                dropna=True
            )
        ),

        "value_counts": {
            str(key): int(value)
            for key, value
            in series.value_counts(
                dropna=False
            ).items()
        },
    }

    numeric = pd.to_numeric(
        series,
        errors="coerce",
    )

    result[
        "numeric_conversion"
    ] = {

        "numeric_rows": int(
            numeric.notna().sum()
        ),

        "non_numeric_rows": int(
            numeric.isna().sum()
        ),

        "unique_numeric_values": sorted(
            [
                float(value)
                for value
                in numeric.dropna()
                .unique()
            ]
        ),
    }

    unique_values = set(
        series.dropna()
        .tolist()
    )

    # --------------------------------------------------------
    # We do NOT infer semantic meaning merely from
    # column name. We only classify the observed structural
    # properties.
    # --------------------------------------------------------

    binary_like = (
        len(unique_values) <= 2
    )

    result[
        "structural_classification"
    ] = {

        "binary_like": binary_like,

        "observed_unique_values": [
            str(value)
            for value
            in sorted(
                unique_values,
                key=lambda x: str(x),
            )
        ],

        "semantic_meaning_established": False,

        "true_negative_semantics_established": False,
    }

    return result


# ============================================================
# QUERY/CANDIDATE STRUCTURE
# ============================================================

def audit_query_candidate_structure(
    rankings: pd.DataFrame,
    query_column: str,
    candidate_column: str,
    score_column: str,
    split_column: str,
) -> dict[str, Any]:

    query_ids = rankings[
        query_column
    ]

    candidate_ids = rankings[
        candidate_column
    ]

    scores = rankings[
        score_column
    ]

    split_values = rankings[
        split_column
    ]

    duplicate_query_candidate = (
        rankings
        .duplicated(
            subset=[
                query_column,
                candidate_column,
            ]
        )
    )

    query_counts = (
        rankings[
            query_column
        ]
        .value_counts()
    )

    candidate_counts = (
        rankings[
            candidate_column
        ]
        .value_counts()
    )

    return {

        "rows": int(
            len(rankings)
        ),

        "unique_queries": int(
            query_ids.nunique()
        ),

        "unique_candidates": int(
            candidate_ids.nunique()
        ),

        "duplicate_query_candidate_pairs": int(
            duplicate_query_candidate.sum()
        ),

        "query_candidate_pair_unique": (
            not duplicate_query_candidate.any()
        ),

        "score_nulls": int(
            scores.isna().sum()
        ),

        "score_unique_values": int(
            scores.nunique()
        ),

        "split_value_counts": {
            str(key): int(value)
            for key, value
            in split_values.value_counts(
                dropna=False
            ).items()
        },

        "query_candidate_rows_min": (
            int(
                query_counts.min()
            )
            if len(query_counts)
            else 0
        ),

        "query_candidate_rows_max": (
            int(
                query_counts.max()
            )
            if len(query_counts)
            else 0
        ),

        "query_candidate_rows_median": (
            float(
                query_counts.median()
            )
            if len(query_counts)
            else 0.0
        ),

        "candidate_frequency_min": (
            int(
                candidate_counts.min()
            )
            if len(candidate_counts)
            else 0
        ),

        "candidate_frequency_max": (
            int(
                candidate_counts.max()
            )
            if len(candidate_counts)
            else 0
        ),
    }


# ============================================================
# SCORE / RANKING STRUCTURE
# ============================================================

def audit_score_structure(
    rankings: pd.DataFrame,
    score_column: str,
    query_column: str,
) -> dict[str, Any]:

    scores = pd.to_numeric(
        rankings[
            score_column
        ],
        errors="coerce",
    )

    query_score_monotonicity = []

    grouped = rankings.groupby(
        query_column,
        sort=False,
    )

    for query_id, group in grouped:

        values = pd.to_numeric(
            group[
                score_column
            ],
            errors="coerce",
        ).dropna()

        if len(values) < 2:
            continue

        descending = (
            values.iloc[:-1].to_numpy()
            >=
            values.iloc[1:].to_numpy()
        ).all()

        query_score_monotonicity.append(
            bool(descending)
        )

    monotonic_count = int(
        sum(
            query_score_monotonicity
        )
    )

    monotonic_total = int(
        len(
            query_score_monotonicity
        )
    )

    return {

        "score_column": score_column,

        "score_dtype": str(
            rankings[
                score_column
            ].dtype
        ),

        "score_nulls": int(
            scores.isna().sum()
        ),

        "score_min": float(
            scores.min()
        ),

        "score_max": float(
            scores.max()
        ),

        "score_mean": float(
            scores.mean()
        ),

        "score_median": float(
            scores.median()
        ),

        "queries_checked_for_native_order": (
            monotonic_total
        ),

        "queries_monotonic_descending": (
            monotonic_count
        ),

        "descending_monotonic_query_rate": (
            monotonic_count
            /
            monotonic_total
            if monotonic_total
            else 0.0
        ),
    }


# ============================================================
# SPLIT INTEGRITY
# ============================================================

def audit_split_integrity(
    data: dict[str, pd.DataFrame],
    schema: dict[str, Any],
) -> dict[str, Any]:

    rankings = data[
        "rankings"
    ]

    train = data[
        "train"
    ]

    evaluation = data[
        "evaluation"
    ]

    ranking_query = schema[
        "rankings"
    ]["query_id"]

    train_query = schema[
        "train"
    ]["query_id"]

    eval_query = schema[
        "evaluation"
    ]["query_id"]

    ranking_split = schema[
        "rankings"
    ]["split"]

    train_ids = set(
        normalize_series(
            train[
                train_query
            ]
        )
    )

    eval_ids = set(
        normalize_series(
            evaluation[
                eval_query
            ]
        )
    )

    ranking_train_ids = set(
        normalize_series(
            rankings.loc[
                rankings[
                    ranking_split
                ].astype(str).str.lower()
                == "train",
                ranking_query,
            ]
        )
    )

    ranking_eval_ids = set(
        normalize_series(
            rankings.loc[
                rankings[
                    ranking_split
                ].astype(str).str.lower()
                == "eval",
                ranking_query,
            ]
        )
    )

    return {

        "train_query_count": len(
            train_ids
        ),

        "evaluation_query_count": len(
            eval_ids
        ),

        "train_eval_query_overlap": len(
            train_ids
            &
            eval_ids
        ),

        "ranking_train_query_count": len(
            ranking_train_ids
        ),

        "ranking_eval_query_count": len(
            ranking_eval_ids
        ),

        "ranking_train_eval_overlap": len(
            ranking_train_ids
            &
            ranking_eval_ids
        ),

        "train_query_alignment": (
            ranking_train_ids
            ==
            train_ids
            or
            ranking_train_ids
            <=
            train_ids
        ),

        "evaluation_query_alignment": (
            ranking_eval_ids
            ==
            eval_ids
            or
            ranking_eval_ids
            <=
            eval_ids
        ),

        "group_leakage_status": (
            "NOT_REESTABLISHED_IN_THIS_OPERATION"
        ),
    }


# ============================================================
# OBSERVED POSITIVE / NON-POSITIVE STRUCTURE
# ============================================================

def audit_observation_by_split(
    rankings: pd.DataFrame,
    target_column: str,
    split_column: str,
) -> dict[str, Any]:

    result = {}

    for split_value, group in (
        rankings.groupby(
            split_column,
            dropna=False,
        )
    ):

        result[
            str(split_value)
        ] = {

            "rows": int(
                len(group)
            ),

            "target_observed_summary": (
                summarize_column(
                    group,
                    target_column,
                )
            ),
        }

    return result


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

        "existing_artifacts_modified": False,
    }


def validate_controls(
    controls: dict[str, Any],
) -> dict[str, Any]:

    failures = []

    for key, value in controls.items():

        if key == "artifact_read_only":

            if value is not True:
                failures.append(key)

        else:

            if value is not False:
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
    print("T9 MOD-037 OP-012B")
    print(
        "T6 Target-Observation Semantics & "
        "Native Ranking Population Audit"
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
    # LOAD DATA
    # --------------------------------------------------------

    print(
        "Loading native T6 data..."
    )

    data = load_t6_data()

    print(
        "T6 ranking rows:",
        len(
            data[
                "rankings"
            ]
        ),
    )

    print(
        "T6 train rows:",
        len(
            data[
                "train"
            ]
        ),
    )

    print(
        "T6 evaluation rows:",
        len(
            data[
                "evaluation"
            ]
        ),
    )

    print()

    # --------------------------------------------------------
    # SCHEMA
    # --------------------------------------------------------

    print(
        "Resolving exact T6 schema..."
    )

    schema = resolve_t6_schema(
        data
    )

    print(
        "Schema resolution:",
        schema[
            "status"
        ],
    )

    print(
        "Ranking schema:",
        schema[
            "rankings"
        ],
    )

    print()

    # --------------------------------------------------------
    # TARGET OBSERVATION
    # --------------------------------------------------------

    print(
        "Auditing target_observed semantics..."
    )

    target_observed = (
        audit_target_observed(
            data[
                "rankings"
            ],
            schema[
                "rankings"
            ][
                "target_observed"
            ],
        )
    )

    print(
        "target_observed dtype:",
        target_observed[
            "dtype"
        ],
    )

    print(
        "target_observed unique values:",
        target_observed[
            "unique_count"
        ],
    )

    print(
        "target_observed value counts:"
    )

    print(
        json.dumps(
            target_observed[
                "value_counts"
            ],
            indent=2,
            ensure_ascii=False,
        )
    )

    print()

    # --------------------------------------------------------
    # QUERY / CANDIDATE
    # --------------------------------------------------------

    print(
        "Auditing query/candidate structure..."
    )

    query_candidate = (
        audit_query_candidate_structure(
            data[
                "rankings"
            ],
            schema[
                "rankings"
            ][
                "query_id"
            ],
            schema[
                "rankings"
            ][
                "candidate_id"
            ],
            schema[
                "rankings"
            ][
                "hybrid_score"
            ],
            schema[
                "rankings"
            ][
                "split"
            ],
        )
    )

    print(
        "Unique queries:",
        query_candidate[
            "unique_queries"
        ],
    )

    print(
        "Unique candidates:",
        query_candidate[
            "unique_candidates"
        ],
    )

    print(
        "Duplicate query-candidate pairs:",
        query_candidate[
            "duplicate_query_candidate_pairs"
        ],
    )

    print()

    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    print(
        "Auditing native hybrid-score structure..."
    )

    score_structure = (
        audit_score_structure(
            data[
                "rankings"
            ],
            schema[
                "rankings"
            ][
                "hybrid_score"
            ],
            schema[
                "rankings"
            ][
                "query_id"
            ],
        )
    )

    print(
        "Score min:",
        score_structure[
            "score_min"
        ],
    )

    print(
        "Score max:",
        score_structure[
            "score_max"
        ],
    )

    print(
        "Descending query-order rate:",
        f"{score_structure['descending_monotonic_query_rate']:.6f}",
    )

    print()

    # --------------------------------------------------------
    # SPLIT
    # --------------------------------------------------------

    print(
        "Auditing group-aware split/query structure..."
    )

    split_integrity = (
        audit_split_integrity(
            data,
            schema,
        )
    )

    print(
        "Train/eval query overlap:",
        split_integrity[
            "train_eval_query_overlap"
        ],
    )

    print(
        "Ranking train/eval query overlap:",
        split_integrity[
            "ranking_train_eval_overlap"
        ],
    )

    print()

    # --------------------------------------------------------
    # OBSERVATION BY SPLIT
    # --------------------------------------------------------

    print(
        "Auditing target_observed by split..."
    )

    observation_by_split = (
        audit_observation_by_split(
            data[
                "rankings"
            ],
            schema[
                "rankings"
            ][
                "target_observed"
            ],
            schema[
                "rankings"
            ][
                "split"
            ],
        )
    )

    print(
        json.dumps(
            observation_by_split,
            indent=2,
            ensure_ascii=False,
        )
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
    # INTERPRETATION
    # --------------------------------------------------------

    interpretation = {

        "target_observed_semantic_status": (
            "STRUCTURE_RESOLVED_BUT_SEMANTIC_"
            "MEANING_NOT_INFERRED_FROM_COLUMN_NAME"
        ),

        "true_negative_status": (
            "NOT_ESTABLISHED"
        ),

        "ranking_semantics": (
            "PRESERVED"
        ),

        "probability_semantics": (
            "NOT_ESTABLISHED"
        ),

        "observable_non_positive_boundary": (
            "Must not be interpreted as an ordinary "
            "true-negative class without explicit "
            "source-supported semantics."
        ),

        "next_required_operation": (
            "Native T6 ranking evaluation using the "
            "resolved target_observation structure "
            "and source-supported relevance semantics."
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

            schema[
                "status"
            ] == "PASS",

            control_validation[
                "status"
            ] == "PASS",
        ]
    )

    output = {

        "operation": (
            "T9_MOD-037_OP-012B"
        ),

        "title": (
            "T6 Target-Observation Semantics & "
            "Native Ranking Population Audit"
        ),

        "status": (
            "PASS"
            if overall_pass
            else "FAIL"
        ),

        "purpose": (
            "Resolve and audit the native T6 "
            "target_observed field, query/candidate "
            "population, hybrid ranking score, and "
            "split structure before native ranking "
            "evaluation."
        ),

        "previous_operation_validation": (
            previous
        ),

        "schema_resolution": schema,

        "target_observed_audit": (
            target_observed
        ),

        "query_candidate_audit": (
            query_candidate
        ),

        "score_structure_audit": (
            score_structure
        ),

        "split_integrity_audit": (
            split_integrity
        ),

        "observation_by_split": (
            observation_by_split
        ),

        "controls": controls,

        "control_validation": (
            control_validation
        ),

        "interpretation": interpretation,

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

            "T6_rankings": str(
                T6_RANKINGS
            ),

            "T6_train": str(
                T6_TRAIN
            ),

            "T6_eval": str(
                T6_EVAL
            ),

            "T6_group_audit": str(
                T6_GROUP_AUDIT
            ),

            "T6_group_assignments": str(
                T6_GROUP_ASSIGNMENTS
            ),
        },

        "methodological_restrictions": [

            (
                "Do not reinterpret target_observed "
                "values as ordinary binary negatives "
                "without source-supported semantics."
            ),

            (
                "Do not convert observable non-positive "
                "cases into true-negative labels."
            ),

            (
                "Do not create synthetic relevance targets."
            ),

            (
                "Do not convert hybrid_score into "
                "probability."
            ),

            (
                "Do not fit calibration during OP-012B."
            ),

            (
                "Do not select thresholds."
            ),

            (
                "Do not use the locked test set for "
                "selection."
            ),

            (
                "Preserve native query-level "
                "retrieval/ranking semantics."
            ),
        ],
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

    print("=" * 72)
    print("T9 MOD-037 OP-012B RESULT")
    print("=" * 72)
    print()

    print(
        "Previous-operation validation:",
        previous[
            "status"
        ],
    )

    print(
        "Schema resolution:",
        schema[
            "status"
        ],
    )

    print(
        "target_observed semantic status:",
        interpretation[
            "target_observed_semantic_status"
        ],
    )

    print(
        "True-negative semantics:",
        interpretation[
            "true_negative_status"
        ],
    )

    print(
        "Native ranking semantics:",
        interpretation[
            "ranking_semantics"
        ],
    )

    print(
        "Probability semantics:",
        interpretation[
            "probability_semantics"
        ],
    )

    print(
        "Control validation:",
        control_validation[
            "status"
        ],
    )

    print()

    print(
        "Output:",
        OUTPUT_JSON,
    )

    print()

    print(
        "T9 MOD-037 OP-012B:",
        (
            "PASS"
            if overall_pass
            else "FAIL"
        ),
    )


if __name__ == "__main__":
    main()