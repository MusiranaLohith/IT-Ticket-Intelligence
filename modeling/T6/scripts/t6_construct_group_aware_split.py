#!/usr/bin/env python3

"""
T6 — Group-Aware Chronological Split Construction

Constructs the modeling-side T6 train/evaluation split from the
accepted DTM-002 T6 candidate dataset.

Frozen split policy:
    Nominal boundary:
        TRAIN = query Creation year < 2024
        EVAL  = query Creation year >= 2024

    Content-group isolation:
        Group = normalized query Summary + normalized query Description

        A whole content group must remain entirely within one split.

        Crossing groups:
            assign to side with majority query-occurrence count
            ties -> side containing earliest query Creation year

Important:
    - The accepted DTM artifact is read-only.
    - No raw Mozilla archive is accessed.
    - observable_non_positive remains a candidate role, not a true-negative label.
    - No model training occurs in this script.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

SOURCE_PATH = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T6_CANDIDATE_DATASET_derived.csv"
)

SPLIT_DIR = PROJECT_ROOT / "modeling" / "T6" / "splits"
DERIVED_DIR = PROJECT_ROOT / "modeling" / "T6" / "derived"
METRICS_DIR = PROJECT_ROOT / "modeling" / "T6" / "metrics"
LOG_DIR = PROJECT_ROOT / "modeling" / "T6" / "logs"

TRAIN_PATH = SPLIT_DIR / "t6_train_group_aware.csv"
EVAL_PATH = SPLIT_DIR / "t6_eval_group_aware.csv"

ASSIGNMENT_PATH = DERIVED_DIR / "t6_content_group_assignments.csv"
AUDIT_PATH = METRICS_DIR / "t6_group_aware_split_audit.json"
LOG_PATH = LOG_DIR / "t6_mod003_split_construction.log"


# ---------------------------------------------------------------------------
# Frozen constants
# ---------------------------------------------------------------------------

TASK_ID = "T6"
NOMINAL_BOUNDARY_YEAR = 2024
SAMPLING_PROTOCOL = "T6-DCS-v2"

EXPECTED_QUERIES = 2722
EXPECTED_ROWS = 274922
EXPECTED_POSITIVE_ROWS = 2722
EXPECTED_NON_POSITIVE_ROWS = 272200
EXPECTED_CANDIDATES_PER_QUERY = 101

REQUIRED_COLUMNS = [
    "query_id",
    "query_creation_time",
    "query_creator",
    "query_creator_detail",
    "query_summary",
    "query_description",
    "candidate_id",
    "candidate_creation_time",
    "candidate_creator",
    "candidate_creator_detail",
    "candidate_summary",
    "candidate_description",
    "candidate_role",
    "target_observed",
    "target_type",
    "sampling_protocol",
    "sampling_seed",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def normalize_text(value: object) -> str:
    """
    Deterministic normalization for content-group construction.

    The DTM content-group rule is based on normalized Summary+Description.
    This normalization deliberately does not introduce semantic processing.
    """
    if pd.isna(value):
        return ""

    text = str(value)

    # Normalize whitespace.
    text = re.sub(r"\s+", " ", text)

    # Trim leading/trailing whitespace.
    text = text.strip()

    # Case-fold for deterministic content grouping.
    text = text.casefold()

    return text


def content_group_hash(summary: object, description: object) -> str:
    """
    SHA-256 hash of normalized Summary + normalized Description.
    """
    normalized_summary = normalize_text(summary)
    normalized_description = normalize_text(description)

    payload = (
        normalized_summary
        + "\n"
        + normalized_description
    )

    return hashlib.sha256(
        payload.encode("utf-8")
    ).hexdigest()


def fail(message: str) -> None:
    raise RuntimeError(message)


def ensure_directories() -> None:
    for directory in (
        SPLIT_DIR,
        DERIVED_DIR,
        METRICS_DIR,
        LOG_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(
            payload,
            handle,
            indent=2,
            ensure_ascii=False,
        )


def count_query_rows(frame: pd.DataFrame) -> int:
    return int(frame["query_id"].nunique())


def count_positive_rows(frame: pd.DataFrame) -> int:
    return int(
        (
            frame["candidate_role"]
            .astype(str)
            .eq("positive")
        ).sum()
    )


def count_non_positive_rows(frame: pd.DataFrame) -> int:
    return int(
        (
            frame["candidate_role"]
            .astype(str)
            .eq("observable_non_positive")
        ).sum()
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:

    ensure_directories()

    log_lines: list[str] = []

    def log(message: str) -> None:
        print(message)
        log_lines.append(message)

    log("=" * 80)
    log("T6 MOD-003 — GROUP-AWARE CHRONOLOGICAL SPLIT CONSTRUCTION")
    log("=" * 80)
    log(f"Source: {SOURCE_PATH}")
    log(f"Nominal boundary year: {NOMINAL_BOUNDARY_YEAR}")
    log(f"Sampling protocol expected: {SAMPLING_PROTOCOL}")
    log("")

    # -----------------------------------------------------------------------
    # Source existence
    # -----------------------------------------------------------------------

    if not SOURCE_PATH.exists():
        fail(f"Accepted T6 source artifact not found: {SOURCE_PATH}")

    log("[1/9] Loading accepted T6 candidate dataset...")
    df = pd.read_csv(SOURCE_PATH)

    log(f"Rows loaded: {len(df):,}")
    log(f"Columns loaded: {len(df.columns)}")

    # -----------------------------------------------------------------------
    # Schema validation
    # -----------------------------------------------------------------------

    log("")
    log("[2/9] Validating source schema...")

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        fail(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    log("Required schema: VALID")

    # -----------------------------------------------------------------------
    # Source accounting
    # -----------------------------------------------------------------------

    log("")
    log("[3/9] Validating source accounting...")

    if len(df) != EXPECTED_ROWS:
        fail(
            f"Unexpected row count: {len(df)} "
            f"(expected {EXPECTED_ROWS})"
        )

    query_count = df["query_id"].nunique()

    if query_count != EXPECTED_QUERIES:
        fail(
            f"Unexpected query count: {query_count} "
            f"(expected {EXPECTED_QUERIES})"
        )

    positive_count = count_positive_rows(df)
    non_positive_count = count_non_positive_rows(df)

    if positive_count != EXPECTED_POSITIVE_ROWS:
        fail(
            f"Unexpected positive count: {positive_count} "
            f"(expected {EXPECTED_POSITIVE_ROWS})"
        )

    if non_positive_count != EXPECTED_NON_POSITIVE_ROWS:
        fail(
            f"Unexpected observable_non_positive count: "
            f"{non_positive_count} "
            f"(expected {EXPECTED_NON_POSITIVE_ROWS})"
        )

    query_sizes = df.groupby("query_id").size()

    if not bool((query_sizes == EXPECTED_CANDIDATES_PER_QUERY).all()):
        fail(
            "Not every query contains exactly "
            f"{EXPECTED_CANDIDATES_PER_QUERY} candidates."
        )

    log(f"Source rows: {len(df):,}")
    log(f"Unique queries: {query_count:,}")
    log(f"Positive rows: {positive_count:,}")
    log(f"Observable non-positive rows: {non_positive_count:,}")
    log("Query candidate cardinality: VALID")

    # -----------------------------------------------------------------------
    # Candidate-role semantics
    # -----------------------------------------------------------------------

    log("")
    log("[4/9] Validating candidate-role semantics...")

    allowed_roles = {
        "positive",
        "observable_non_positive",
    }

    observed_roles = set(
        df["candidate_role"]
        .astype(str)
        .unique()
    )

    if not observed_roles.issubset(allowed_roles):
        fail(
            "Unexpected candidate roles: "
            + repr(sorted(observed_roles - allowed_roles))
        )

    positive_per_query = (
        df["candidate_role"]
        .astype(str)
        .eq("positive")
        .groupby(df["query_id"])
        .sum()
    )

    if not bool((positive_per_query == 1).all()):
        fail(
            "Every query must contain exactly one positive candidate."
        )

    log("Candidate-role semantics: VALID")
    log("Exactly one positive candidate per query: VALID")
    log("Observable non-positive candidates remain non-positive candidates.")

    # -----------------------------------------------------------------------
    # Query-level metadata
    # -----------------------------------------------------------------------

    log("")
    log("[5/9] Constructing query-level temporal metadata...")

    query_meta = (
        df[
            [
                "query_id",
                "query_creation_time",
                "query_summary",
                "query_description",
            ]
        ]
        .drop_duplicates(subset=["query_id"])
        .copy()
    )

    if len(query_meta) != EXPECTED_QUERIES:
        fail(
            "Query metadata does not contain exactly "
            f"{EXPECTED_QUERIES} unique queries."
        )

    query_meta["query_creation_time"] = pd.to_datetime(
        query_meta["query_creation_time"],
        errors="coerce",
        utc=True,
    )

    if query_meta["query_creation_time"].isna().any():
        bad_count = int(
            query_meta["query_creation_time"].isna().sum()
        )
        fail(
            f"{bad_count} queries have invalid Creation timestamps."
        )

    query_meta["creation_year"] = (
        query_meta["query_creation_time"]
        .dt.year
        .astype(int)
    )

    # -----------------------------------------------------------------------
    # Content groups
    # -----------------------------------------------------------------------

    log("")
    log("[6/9] Constructing normalized Summary+Description content groups...")

    query_meta["content_group_hash"] = [
        content_group_hash(summary, description)
        for summary, description in zip(
            query_meta["query_summary"],
            query_meta["query_description"],
        )
    ]

    total_groups = int(
        query_meta["content_group_hash"].nunique()
    )

    log(f"Unique content groups: {total_groups:,}")

    # -----------------------------------------------------------------------
    # Determine group assignment
    # -----------------------------------------------------------------------

    log("")
    log("[7/9] Applying frozen DTM content-group assignment rule...")

    group_records: list[dict] = []

    for group_hash, group in query_meta.groupby(
        "content_group_hash",
        sort=True,
    ):
        train_queries = group[
            group["creation_year"] < NOMINAL_BOUNDARY_YEAR
        ]

        eval_queries = group[
            group["creation_year"] >= NOMINAL_BOUNDARY_YEAR
        ]

        train_count = len(train_queries)
        eval_count = len(eval_queries)

        if train_count > eval_count:
            assigned_side = "TRAIN"
        elif eval_count > train_count:
            assigned_side = "EVAL"
        else:
            earliest_year = int(group["creation_year"].min())

            if earliest_year < NOMINAL_BOUNDARY_YEAR:
                assigned_side = "TRAIN"
            else:
                assigned_side = "EVAL"

        if train_count > 0 and eval_count > 0:
            group_type = "cross_boundary"
        elif train_count > 0:
            group_type = "train_only"
        else:
            group_type = "eval_only"

        group_records.append(
            {
                "content_group_hash": group_hash,
                "train_query_count_nominal": train_count,
                "eval_query_count_nominal": eval_count,
                "earliest_creation_year": int(
                    group["creation_year"].min()
                ),
                "latest_creation_year": int(
                    group["creation_year"].max()
                ),
                "group_type": group_type,
                "assigned_side": assigned_side,
            }
        )

    group_assignments = pd.DataFrame(group_records)

    # -----------------------------------------------------------------------
    # Apply assignment to queries
    # -----------------------------------------------------------------------

    query_meta = query_meta.merge(
        group_assignments[
            [
                "content_group_hash",
                "assigned_side",
            ]
        ],
        on="content_group_hash",
        how="left",
        validate="many_to_one",
    )

    if query_meta["assigned_side"].isna().any():
        fail("Some queries did not receive a content-group assignment.")

    query_meta["split"] = query_meta["assigned_side"]

    # Deterministic assignment artifact.
    assignment_output = query_meta[
        [
            "query_id",
            "query_creation_time",
            "creation_year",
            "content_group_hash",
            "assigned_side",
        ]
    ].sort_values(
        ["assigned_side", "query_creation_time", "query_id"]
    )

    assignment_output.to_csv(
        ASSIGNMENT_PATH,
        index=False,
    )

    # -----------------------------------------------------------------------
    # Join split assignment to candidate rows
    # -----------------------------------------------------------------------

    df = df.merge(
        query_meta[
            [
                "query_id",
                "content_group_hash",
                "assigned_side",
            ]
        ],
        on="query_id",
        how="left",
        validate="many_to_one",
    )

    if df["assigned_side"].isna().any():
        fail("Some candidate rows did not receive a split assignment.")

    train_df = df[
        df["assigned_side"] == "TRAIN"
    ].copy()

    eval_df = df[
        df["assigned_side"] == "EVAL"
    ].copy()

    # Remove modeling-only helper columns before writing split artifacts.
    helper_columns = [
        "content_group_hash",
        "assigned_side",
    ]

    train_output = train_df.drop(
        columns=helper_columns
    )

    eval_output = eval_df.drop(
        columns=helper_columns
    )

    train_output.to_csv(
        TRAIN_PATH,
        index=False,
    )

    eval_output.to_csv(
        EVAL_PATH,
        index=False,
    )

    # -----------------------------------------------------------------------
    # Audit
    # -----------------------------------------------------------------------

    log("")
    log("[8/9] Auditing final split...")

    train_query_count = count_query_rows(train_df)
    eval_query_count = count_query_rows(eval_df)

    train_rows = len(train_df)
    eval_rows = len(eval_df)

    train_positive_rows = count_positive_rows(train_df)
    eval_positive_rows = count_positive_rows(eval_df)

    train_non_positive_rows = count_non_positive_rows(train_df)
    eval_non_positive_rows = count_non_positive_rows(eval_df)

    # Query overlap.
    train_query_ids = set(
        train_df["query_id"].astype(str)
    )
    eval_query_ids = set(
        eval_df["query_id"].astype(str)
    )

    query_overlap = train_query_ids.intersection(
        eval_query_ids
    )

    if query_overlap:
        fail(
            f"Query leakage detected: {len(query_overlap)} "
            "queries occur in both splits."
        )

    # Content-group overlap.
    train_groups = set(
        train_df["content_group_hash"].astype(str)
    )
    eval_groups = set(
        eval_df["content_group_hash"].astype(str)
    )

    group_overlap = train_groups.intersection(
        eval_groups
    )

    if group_overlap:
        fail(
            f"Content-group leakage detected: {len(group_overlap)} "
            "groups occur in both splits."
        )

    # Row accounting.
    if train_rows + eval_rows != EXPECTED_ROWS:
        fail(
            "Final row accounting failed: "
            f"{train_rows + eval_rows} != {EXPECTED_ROWS}"
        )

    if train_positive_rows + eval_positive_rows != EXPECTED_POSITIVE_ROWS:
        fail(
            "Final positive-row accounting failed."
        )

    if (
        train_non_positive_rows
        + eval_non_positive_rows
        != EXPECTED_NON_POSITIVE_ROWS
    ):
        fail(
            "Final observable_non_positive accounting failed."
        )

    # Nominal temporal classification.
    train_nominal_preboundary = int(
        (
            query_meta[
                query_meta["assigned_side"] == "TRAIN"
            ]["creation_year"]
            < NOMINAL_BOUNDARY_YEAR
        ).sum()
    )

    train_nominal_boundary_plus = (
        train_query_count - train_nominal_preboundary
    )

    eval_nominal_preboundary = int(
        (
            query_meta[
                query_meta["assigned_side"] == "EVAL"
            ]["creation_year"]
            < NOMINAL_BOUNDARY_YEAR
        ).sum()
    )

    eval_nominal_boundary_plus = (
        eval_query_count - eval_nominal_preboundary
    )

    # Since each query has exactly 101 rows, query-level temporal
    # displacement can be converted to row counts.
    train_preboundary_rows = (
        train_nominal_preboundary
        * EXPECTED_CANDIDATES_PER_QUERY
    )

    train_boundary_plus_rows = (
        train_nominal_boundary_plus
        * EXPECTED_CANDIDATES_PER_QUERY
    )

    eval_preboundary_rows = (
        eval_nominal_preboundary
        * EXPECTED_CANDIDATES_PER_QUERY
    )

    eval_boundary_plus_rows = (
        eval_nominal_boundary_plus
        * EXPECTED_CANDIDATES_PER_QUERY
    )

    train_temporal_purity = (
        train_preboundary_rows / train_rows
        if train_rows
        else 0.0
    )

    eval_temporal_purity = (
        eval_boundary_plus_rows / eval_rows
        if eval_rows
        else 0.0
    )

    # Positive-query temporal purity.
    train_positive_query_meta = query_meta[
        query_meta["assigned_side"] == "TRAIN"
    ].copy()

    eval_positive_query_meta = query_meta[
        query_meta["assigned_side"] == "EVAL"
    ].copy()

    # Every query has exactly one positive.
    train_positive_preboundary = int(
        (
            train_positive_query_meta["creation_year"]
            < NOMINAL_BOUNDARY_YEAR
        ).sum()
    )

    train_positive_boundary_plus = (
        train_positive_query_meta.shape[0]
        - train_positive_preboundary
    )

    eval_positive_preboundary = int(
        (
            eval_positive_query_meta["creation_year"]
            < NOMINAL_BOUNDARY_YEAR
        ).sum()
    )

    eval_positive_boundary_plus = (
        eval_positive_query_meta.shape[0]
        - eval_positive_preboundary
    )

    train_positive_temporal_purity = (
        train_positive_preboundary / train_positive_rows
        if train_positive_rows
        else 0.0
    )

    eval_positive_temporal_purity = (
        eval_positive_boundary_plus / eval_positive_rows
        if eval_positive_rows
        else 0.0
    )

    # Content-group assignment statistics.
    crossing_groups = group_assignments[
        group_assignments["group_type"] == "cross_boundary"
    ]

    train_only_groups = group_assignments[
        group_assignments["group_type"] == "train_only"
    ]

    eval_only_groups = group_assignments[
        group_assignments["group_type"] == "eval_only"
    ]

    crossing_assigned_train = int(
        (
            crossing_groups["assigned_side"]
            == "TRAIN"
        ).sum()
    )

    crossing_assigned_eval = int(
        (
            crossing_groups["assigned_side"]
            == "EVAL"
        ).sum()
    )

    audit = {
        "operation": "T6 MOD-003",
        "task": TASK_ID,
        "status": "ACCEPTED",
        "source_artifact": str(SOURCE_PATH),
        "source_artifact_modified": False,

        "split_policy": {
            "nominal_boundary_year": NOMINAL_BOUNDARY_YEAR,
            "nominal_train_rule": (
                "query Creation year < 2024"
            ),
            "nominal_eval_rule": (
                "query Creation year >= 2024"
            ),
            "content_group_definition": (
                "normalized Summary + normalized Description"
            ),
            "crossing_group_rule": (
                "majority query-occurrence side"
            ),
            "tie_rule": (
                "side containing earliest query Creation year"
            ),
            "group_isolation": True,
        },

        "source_accounting": {
            "rows": int(len(df)),
            "queries": int(query_count),
            "positive_rows": int(positive_count),
            "observable_non_positive_rows": int(
                non_positive_count
            ),
            "candidates_per_query": EXPECTED_CANDIDATES_PER_QUERY,
        },

        "content_groups": {
            "total": int(total_groups),
            "train_only": int(len(train_only_groups)),
            "eval_only": int(len(eval_only_groups)),
            "cross_boundary": int(len(crossing_groups)),
            "cross_boundary_assigned_train": crossing_assigned_train,
            "cross_boundary_assigned_eval": crossing_assigned_eval,
        },

        "final_split": {
            "train_rows": int(train_rows),
            "eval_rows": int(eval_rows),
            "train_queries": int(train_query_count),
            "eval_queries": int(eval_query_count),
            "train_positive_rows": int(train_positive_rows),
            "eval_positive_rows": int(eval_positive_rows),
            "train_observable_non_positive_rows": int(
                train_non_positive_rows
            ),
            "eval_observable_non_positive_rows": int(
                eval_non_positive_rows
            ),
        },

        "temporal_displacement": {
            "train_preboundary_queries": int(
                train_nominal_preboundary
            ),
            "train_boundary_plus_queries": int(
                train_nominal_boundary_plus
            ),
            "eval_preboundary_queries": int(
                eval_nominal_preboundary
            ),
            "eval_boundary_plus_queries": int(
                eval_nominal_boundary_plus
            ),
            "train_preboundary_rows": int(
                train_preboundary_rows
            ),
            "train_boundary_plus_rows": int(
                train_boundary_plus_rows
            ),
            "eval_preboundary_rows": int(
                eval_preboundary_rows
            ),
            "eval_boundary_plus_rows": int(
                eval_boundary_plus_rows
            ),
        },

        "temporal_purity": {
            "train": float(train_temporal_purity),
            "eval": float(eval_temporal_purity),
            "train_positive": float(
                train_positive_temporal_purity
            ),
            "eval_positive": float(
                eval_positive_temporal_purity
            ),
        },

        "leakage_controls": {
            "query_overlap": int(len(query_overlap)),
            "content_group_overlap": int(len(group_overlap)),
            "no_query_overlap": len(query_overlap) == 0,
            "no_content_group_overlap": len(group_overlap) == 0,
        },

        "immutability_controls": {
            "raw_dataset_modified": False,
            "accepted_dtm_artifact_modified": False,
            "modeling_copy_created": True,
        },

        "artifacts": {
            "train": str(TRAIN_PATH),
            "eval": str(EVAL_PATH),
            "content_group_assignments": str(
                ASSIGNMENT_PATH
            ),
            "audit": str(AUDIT_PATH),
        },

        "overall_control": True,
        "decision": (
            "ACCEPTED — group-aware chronological split "
            "constructed from the accepted DTM T6 candidate artifact."
        ),
    }

    write_json(AUDIT_PATH, audit)

    # -----------------------------------------------------------------------
    # Final output
    # -----------------------------------------------------------------------

    log("")
    log("[9/9] Final split summary")
    log("-" * 80)

    log(
        f"TRAIN: {train_rows:,} rows / "
        f"{train_query_count:,} queries / "
        f"{train_positive_rows:,} positives"
    )

    log(
        f"EVAL:  {eval_rows:,} rows / "
        f"{eval_query_count:,} queries / "
        f"{eval_positive_rows:,} positives"
    )

    log(
        f"Content groups: {total_groups:,}"
    )

    log(
        f"Cross-boundary groups: {len(crossing_groups):,}"
    )

    log(
        f"Cross-boundary groups -> TRAIN: "
        f"{crossing_assigned_train:,}"
    )

    log(
        f"Cross-boundary groups -> EVAL: "
        f"{crossing_assigned_eval:,}"
    )

    log(
        f"Query overlap: {len(query_overlap):,}"
    )

    log(
        f"Content-group overlap: {len(group_overlap):,}"
    )

    log(
        f"TRAIN temporal purity: "
        f"{train_temporal_purity:.6f}"
    )

    log(
        f"EVAL temporal purity: "
        f"{eval_temporal_purity:.6f}"
    )

    log(
        f"TRAIN positive temporal purity: "
        f"{train_positive_temporal_purity:.6f}"
    )

    log(
        f"EVAL positive temporal purity: "
        f"{eval_positive_temporal_purity:.6f}"
    )

    log("")
    log("Artifacts written:")
    log(f"  {TRAIN_PATH}")
    log(f"  {EVAL_PATH}")
    log(f"  {ASSIGNMENT_PATH}")
    log(f"  {AUDIT_PATH}")

    log("")
    log("T6 MOD-003: ACCEPTED")

    LOG_PATH.write_text(
        "\n".join(log_lines) + "\n",
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("")
        print("=" * 80)
        print("T6 MOD-003 FAILED")
        print("=" * 80)
        print(f"{type(exc).__name__}: {exc}")
        raise