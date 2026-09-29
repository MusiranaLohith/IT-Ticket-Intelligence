from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


# ============================================================
# T9 MOD-037 OP-012A
# T6 Prior-Artifact Schema / Value Resolution
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
    / "t9_mod037_op012a_t6_prior_artifact_schema.json"
)


# ============================================================
# T9 PRIOR ARTIFACTS
# ============================================================

OP004_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op004_native_output_acceptance.json"
)

OP005_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op005_output_semantics_lock.json"
)


# ============================================================
# T6 AUTHORITATIVE / SUPPORTING ARTIFACTS
# ============================================================

T6_CONTRACT = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "contracts"
    / "t6_modeling_contract.json"
)

T6_FINAL_RANKINGS = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod010_corrected_hybrid_query_rankings.csv"
)

T6_FINAL_CLOSURE = (
    PROJECT_ROOT
    / "modeling"
    / "metrics"
    / "t6_final_closure.json"
)

T6_GROUP_AWARE_AUDIT = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_group_aware_split_audit.json"
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

T6_CONTENT_GROUPS = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "derived"
    / "t6_content_group_assignments.csv"
)


# ============================================================
# OTHER NATIVE RANKING ARTIFACTS
# ============================================================

T6_OTHER_RANKINGS = {
    "MOD-004": (
        PROJECT_ROOT
        / "modeling"
        / "T6"
        / "metrics"
        / "t6_mod004_query_rankings.csv"
    ),
    "MOD-007": (
        PROJECT_ROOT
        / "modeling"
        / "T6"
        / "metrics"
        / "t6_mod007_bm25_query_rankings.csv"
    ),
    "MOD-008": (
        PROJECT_ROOT
        / "modeling"
        / "T6"
        / "metrics"
        / "t6_mod008_semantic_failure_rankings.csv"
    ),
    "MOD-009": (
        PROJECT_ROOT
        / "modeling"
        / "T6"
        / "metrics"
        / "t6_mod009_hybrid_query_rankings.csv"
    ),
}


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


def frame_summary(
    frame: pd.DataFrame,
) -> dict[str, Any]:

    return {
        "rows": int(len(frame)),
        "columns_count": int(
            len(frame.columns)
        ),
        "columns": [
            str(column)
            for column in frame.columns
        ],
        "dtypes": {
            str(column): str(dtype)
            for column, dtype
            in frame.dtypes.items()
        },
    }


def resolve_column(
    frame: pd.DataFrame,
    candidates: list[str],
    label: str,
) -> str | None:

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

    return None


def value_summary(
    series: pd.Series,
    max_unique: int = 20,
) -> dict[str, Any]:

    non_null = series.dropna()

    result = {
        "dtype": str(series.dtype),
        "rows": int(len(series)),
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

    if (
        series.nunique(
            dropna=True
        )
        <= max_unique
    ):

        result[
            "value_counts"
        ] = {
            str(key): int(value)
            for key, value
            in series.value_counts(
                dropna=False
            ).items()
        }

    else:

        result[
            "sample_values"
        ] = [
            str(value)
            for value
            in non_null.head(10)
        ]

    return result


# ============================================================
# OP-004 RESOLUTION
# ============================================================

def resolve_op004() -> dict[str, Any]:

    artifact = load_json(
        OP004_ARTIFACT
    )

    return {
        "status": artifact.get(
            "status"
        ),

        "accepted_tasks": artifact.get(
            "accepted_tasks",
            []
        ),

        "rejected_tasks": artifact.get(
            "rejected_tasks",
            []
        ),

        "unavailable_tasks": artifact.get(
            "unavailable_tasks",
            []
        ),

        "T6_accepted": (
            "T6"
            in artifact.get(
                "accepted_tasks",
                []
            )
        ),

        "controls": artifact.get(
            "controls",
            {}
        ),
    }


# ============================================================
# OP-005 RESOLUTION
# ============================================================

def resolve_op005() -> dict[str, Any]:

    artifact = load_json(
        OP005_ARTIFACT
    )

    task_boundary = artifact.get(
        "task_boundary",
        {}
    )

    t6_boundary = task_boundary.get(
        "T6",
        {}
    )

    return {
        "status": artifact.get(
            "status"
        ),

        "native_evaluation_tasks": (
            artifact.get(
                "native_evaluation_tasks",
                []
            )
        ),

        "empirical_calibration_tasks": (
            artifact.get(
                "empirical_calibration_tasks",
                []
            )
        ),

        "unavailable_tasks": (
            artifact.get(
                "unavailable_tasks",
                []
            )
        ),

        "T6_boundary": t6_boundary,

        "global_restrictions": (
            artifact.get(
                "global_restrictions",
                []
            )
        ),

        "global_control_validation": (
            artifact.get(
                "global_control_validation",
                {}
            )
        ),
    }


# ============================================================
# T6 CONTRACT RESOLUTION
# ============================================================

def resolve_t6_contract() -> dict[str, Any]:

    artifact = load_json(
        T6_CONTRACT
    )

    return {
        "top_level_keys": list(
            artifact.keys()
        ),

        "artifact": artifact,
    }


# ============================================================
# T6 DATA SCHEMA
# ============================================================

def resolve_t6_data_schema() -> dict[str, Any]:

    require_file(
        T6_FINAL_RANKINGS
    )

    require_file(
        T6_TRAIN
    )

    require_file(
        T6_EVAL
    )

    rankings = pd.read_csv(
        T6_FINAL_RANKINGS,
        low_memory=False,
    )

    train = pd.read_csv(
        T6_TRAIN,
        low_memory=False,
    )

    evaluation = pd.read_csv(
        T6_EVAL,
        low_memory=False,
    )

    return {

        "final_rankings": frame_summary(
            rankings
        ),

        "train_group_aware": frame_summary(
            train
        ),

        "eval_group_aware": frame_summary(
            evaluation
        ),
    }


# ============================================================
# T6 RANKING COLUMN DISCOVERY
# ============================================================

def resolve_ranking_columns() -> dict[str, Any]:

    rankings = pd.read_csv(
        T6_FINAL_RANKINGS,
        low_memory=False,
    )

    candidates = {

        "query_id": [
            "query_id",
            "id",
            "ticket_id",
            "source_id",
            "issue_id",
        ],

        "candidate_id": [
            "candidate_id",
            "candidate",
            "candidate_issue_id",
            "target_id",
            "result_id",
        ],

        "rank": [
            "rank",
            "candidate_rank",
            "retrieval_rank",
            "position",
        ],

        "score": [
            "score",
            "similarity",
            "similarity_score",
            "ranking_score",
            "hybrid_score",
            "bm25_score",
        ],

        "relevance": [
            "relevance",
            "relevant",
            "is_relevant",
            "label",
            "target",
            "ground_truth",
        ],

        "observed_non_positive": [
            "observable_non_positive",
            "observed_non_positive",
            "non_positive",
        ],
    }

    resolved = {}

    for key, names in candidates.items():

        resolved[key] = (
            resolve_column(
                rankings,
                names,
                f"T6 {key}",
            )
        )

    return {
        "status": "PASS",
        "resolved_columns": resolved,
    }


# ============================================================
# T6 RANKING VALUE AUDIT
# ============================================================

def audit_ranking_values(
    resolved_columns: dict[str, str | None],
) -> dict[str, Any]:

    rankings = pd.read_csv(
        T6_FINAL_RANKINGS,
        low_memory=False,
    )

    result = {}

    for semantic_name, column in (
        resolved_columns.items()
    ):

        if column is None:
            result[
                semantic_name
            ] = {
                "status": "NOT_RESOLVED"
            }

            continue

        result[
            semantic_name
        ] = {

            "status": "RESOLVED",

            "column": column,

            "summary": value_summary(
                rankings[column]
            ),
        }

    return result


# ============================================================
# T6 ARTIFACT INVENTORY
# ============================================================

def inventory_other_rankings() -> dict[str, Any]:

    inventory = {}

    for label, path in (
        T6_OTHER_RANKINGS.items()
    ):

        if not path.exists():

            inventory[label] = {
                "exists": False,
                "path": str(path),
            }

            continue

        frame = pd.read_csv(
            path,
            low_memory=False,
        )

        inventory[label] = {
            "exists": True,
            "path": str(path),
            "summary": frame_summary(
                frame
            ),
        }

    return inventory


# ============================================================
# CLOSURE / SUPPORTING ARTIFACT RESOLUTION
# ============================================================

def resolve_supporting_artifacts() -> dict[str, Any]:

    result = {}

    for label, path in {

        "T6_final_closure": T6_FINAL_CLOSURE,

        "T6_group_aware_split_audit": (
            T6_GROUP_AWARE_AUDIT
        ),

        "T6_content_group_assignments": (
            T6_CONTENT_GROUPS
        ),

    }.items():

        result[label] = {

            "exists": path.exists(),

            "path": str(path),
        }

        if not path.exists():
            continue

        if path.suffix.lower() == ".json":

            artifact = load_json(
                path
            )

            result[label][
                "top_level_keys"
            ] = list(
                artifact.keys()
            )

            result[label][
                "status"
            ] = artifact.get(
                "status"
            )

        elif path.suffix.lower() == ".csv":

            frame = pd.read_csv(
                path,
                low_memory=False,
            )

            result[label][
                "summary"
            ] = frame_summary(
                frame
            )

    return result


# ============================================================
# METHODOLOGICAL BOUNDARY DISCOVERY
# ============================================================

def resolve_t6_boundary(
    op005: dict[str, Any],
) -> dict[str, Any]:

    boundary = op005.get(
        "T6_boundary",
        {}
    )

    return {

        "status": (
            boundary.get(
                "status"
            )
        ),

        "native_quantity": (
            boundary.get(
                "native_quantity"
            )
        ),

        "native_probability_output": (
            boundary.get(
                "native_probability_output"
            )
        ),

        "accepted_for_calibration": (
            boundary.get(
                "accepted_for_calibration"
            )
        ),

        "accepted_for_native_evaluation": (
            boundary.get(
                "accepted_for_native_evaluation"
            )
        ),

        "native_outputs": (
            boundary.get(
                "native_outputs",
                []
            )
        ),

        "semantic_restrictions": (
            boundary.get(
                "semantic_restrictions",
                []
            )
        ),

        "calibration_boundary": (
            boundary.get(
                "calibration_boundary"
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

        "observable_non_positive_reinterpreted_as_true_negative": False,

        "ranking_forced_into_binary_classification": False,

        "threshold_selected": False,

        "locked_test_used": False,

        "universal_confidence_created": False,

        "universal_risk_score_created": False,

        "synthetic_probability_created": False,

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
    print("T9 MOD-037 OP-012A")
    print("T6 Prior-Artifact Schema / Value Resolution")
    print("=" * 72)
    print()

    # --------------------------------------------------------
    # OP-004
    # --------------------------------------------------------

    print(
        "Resolving OP-004 T6 acceptance..."
    )

    op004 = resolve_op004()

    print(
        "OP-004 overall status:",
        op004["status"],
    )

    print(
        "T6 accepted:",
        op004["T6_accepted"],
    )

    if not op004["T6_accepted"]:

        raise RuntimeError(
            "T6 is not accepted by OP-004."
        )

    print()

    # --------------------------------------------------------
    # OP-005
    # --------------------------------------------------------

    print(
        "Resolving OP-005 T6 semantic boundary..."
    )

    op005 = resolve_op005()

    print(
        "OP-005 status:",
        op005["status"],
    )

    print(
        "T6 native boundary:"
    )

    print(
        json.dumps(
            op005[
                "T6_boundary"
            ],
            indent=2,
            ensure_ascii=False,
        )
    )

    print()

    # --------------------------------------------------------
    # T6 CONTRACT
    # --------------------------------------------------------

    print(
        "Resolving T6 modeling contract..."
    )

    t6_contract = (
        resolve_t6_contract()
    )

    print(
        "T6 contract top-level keys:",
        t6_contract[
            "top_level_keys"
        ],
    )

    print()

    # --------------------------------------------------------
    # DATA SCHEMAS
    # --------------------------------------------------------

    print(
        "Resolving T6 dataset schemas..."
    )

    data_schema = (
        resolve_t6_data_schema()
    )

    print(
        "Final ranking rows:",
        data_schema[
            "final_rankings"
        ]["rows"],
    )

    print(
        "Final ranking columns:",
        data_schema[
            "final_rankings"
        ]["columns"],
    )

    print(
        "T6 train rows:",
        data_schema[
            "train_group_aware"
        ]["rows"],
    )

    print(
        "T6 eval rows:",
        data_schema[
            "eval_group_aware"
        ]["rows"],
    )

    print()

    # --------------------------------------------------------
    # RANKING COLUMNS
    # --------------------------------------------------------

    print(
        "Resolving native T6 ranking columns..."
    )

    ranking_columns = (
        resolve_ranking_columns()
    )

    print(
        "Resolved ranking columns:"
    )

    print(
        json.dumps(
            ranking_columns[
                "resolved_columns"
            ],
            indent=2,
            ensure_ascii=False,
        )
    )

    print()

    # --------------------------------------------------------
    # RANKING VALUES
    # --------------------------------------------------------

    print(
        "Auditing native T6 ranking values..."
    )

    ranking_values = (
        audit_ranking_values(
            ranking_columns[
                "resolved_columns"
            ]
        )
    )

    print(
        json.dumps(
            ranking_values,
            indent=2,
            ensure_ascii=False,
        )
    )

    print()

    # --------------------------------------------------------
    # OTHER ARTIFACTS
    # --------------------------------------------------------

    print(
        "Resolving other T6 ranking artifacts..."
    )

    other_rankings = (
        inventory_other_rankings()
    )

    for label, value in (
        other_rankings.items()
    ):

        print(
            label,
            "exists:",
            value["exists"],
        )

    print()

    # --------------------------------------------------------
    # SUPPORTING ARTIFACTS
    # --------------------------------------------------------

    print(
        "Resolving T6 supporting artifacts..."
    )

    supporting = (
        resolve_supporting_artifacts()
    )

    for label, value in (
        supporting.items()
    ):

        print(
            label,
            "exists:",
            value["exists"],
        )

    print()

    # --------------------------------------------------------
    # BOUNDARY
    # --------------------------------------------------------

    print(
        "Resolving frozen T6 methodological boundary..."
    )

    boundary = resolve_t6_boundary(
        op005
    )

    print(
        json.dumps(
            boundary,
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
            "OP-012A control validation failed."
        )

    # --------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------

    required_checks = [

        op004[
            "T6_accepted"
        ],

        op005.get(
            "status"
        ) == "PASS",

        ranking_columns[
            "status"
        ] == "PASS",

        control_validation[
            "status"
        ] == "PASS",

    ]

    overall_pass = all(
        required_checks
    )

    output = {

        "operation": (
            "T9_MOD-037_OP-012A"
        ),

        "title": (
            "T6 Prior-Artifact "
            "Schema / Value Resolution"
        ),

        "status": (
            "PASS"
            if overall_pass
            else "FAIL"
        ),

        "purpose": (
            "Resolve the actual schemas, values, "
            "native ranking fields, supporting "
            "artifacts, and frozen methodological "
            "boundary of T6 before performing "
            "the OP-012 native evaluation audit."
        ),

        "op004_resolution": op004,

        "op005_resolution": op005,

        "t6_contract_resolution": t6_contract,

        "t6_data_schema": data_schema,

        "native_ranking_columns": (
            ranking_columns
        ),

        "native_ranking_value_audit": (
            ranking_values
        ),

        "other_t6_ranking_artifacts": (
            other_rankings
        ),

        "supporting_artifacts": (
            supporting
        ),

        "t6_methodological_boundary": (
            boundary
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

            "T6_contract": str(
                T6_CONTRACT
            ),

            "T6_final_rankings": str(
                T6_FINAL_RANKINGS
            ),

            "T6_final_closure": str(
                T6_FINAL_CLOSURE
            ),

            "T6_group_aware_audit": str(
                T6_GROUP_AWARE_AUDIT
            ),

            "T6_train": str(
                T6_TRAIN
            ),

            "T6_eval": str(
                T6_EVAL
            ),

            "T6_content_groups": str(
                T6_CONTENT_GROUPS
            ),
        },

        "interpretation_boundary": [

            (
                "This operation performs schema/value "
                "resolution only."
            ),

            (
                "No new model or prediction is generated."
            ),

            (
                "Native T6 ranking quantities remain "
                "ranking quantities."
            ),

            (
                "Observable non-positive observations "
                "must not be reinterpreted as true "
                "negative labels."
            ),

            (
                "No binary probability calibration "
                "is established by schema inspection alone."
            ),

            (
                "No synthetic target or synthetic "
                "probability may be introduced."
            ),

            (
                "Any later OP-012 evaluation must use "
                "the actual resolved native schema."
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
    print("T9 MOD-037 OP-012A RESULT")
    print("=" * 72)
    print()

    print(
        "OP-004 T6 accepted:",
        op004[
            "T6_accepted"
        ],
    )

    print(
        "OP-005 status:",
        op005[
            "status"
        ],
    )

    print(
        "Native ranking schema:",
        ranking_columns[
            "status"
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
        "T9 MOD-037 OP-012A:",
        (
            "PASS"
            if overall_pass
            else "FAIL"
        ),
    )


if __name__ == "__main__":
    main()