from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# =============================================================================
# T6 MOD-010 — DIAGNOSE MOD-009 LEXICAL RECONSTRUCTION
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

TRAIN_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "splits"
    / "t6_train_group_aware.csv"
)

EVAL_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "splits"
    / "t6_eval_group_aware.csv"
)

VECTORIZER_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "models"
    / "t6_mod004_tfidf_vectorizer.joblib"
)

MOD009_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod009_hybrid_query_rankings.csv"
)


QUERY_FIELDS = [
    "query_creator",
    "query_creator_detail",
    "query_summary",
    "query_description",
]

CANDIDATE_FIELDS = [
    "candidate_creator",
    "candidate_creator_detail",
    "candidate_summary",
    "candidate_description",
]


# =============================================================================
# Exact MOD-004 text construction
# =============================================================================

def clean_text(value: object) -> str:

    if pd.isna(value):
        return ""

    return str(value).strip()


def build_mod004_text(
    df: pd.DataFrame,
    fields: list[str],
) -> pd.Series:

    parts = []

    for field in fields:

        field_name = field.replace(
            "_",
            " ",
        )

        values = df[field].map(
            clean_text
        )

        parts.append(
            field_name
            + " "
            + values
        )

    result = parts[0]

    for part in parts[1:]:

        result = (
            result
            + " "
            + part
        )

    return result


# =============================================================================
# Exact MOD-009 text construction
# =============================================================================

def build_mod009_text(
    df: pd.DataFrame,
    fields: list[str],
) -> pd.Series:

    return (
        df[fields]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
        .str.replace(
            r"\s+",
            " ",
            regex=True,
        )
        .str.strip()
    )


# =============================================================================
# Main
# =============================================================================

def main() -> None:

    print("=" * 80)
    print("T6 MOD-010 — MOD-009 LEXICAL RECONSTRUCTION DIAGNOSTIC")
    print("=" * 80)
    print()

    # -------------------------------------------------------------------------
    # 1. Load frozen artifacts
    # -------------------------------------------------------------------------

    print("[1/7] Loading frozen artifacts...")

    train = pd.read_csv(
        TRAIN_PATH
    )

    evaluation = pd.read_csv(
        EVAL_PATH
    )

    mod009 = pd.read_csv(
        MOD009_PATH
    )

    vectorizer = joblib.load(
        VECTORIZER_PATH
    )

    combined = pd.concat(
        [
            train,
            evaluation,
        ],
        ignore_index=True,
    )

    print(
        f"TRAIN rows: {len(train):,}"
    )

    print(
        f"EVAL rows: {len(evaluation):,}"
    )

    print(
        f"MOD-009 rows: {len(mod009):,}"
    )

    print(
        f"Combined rows: {len(combined):,}"
    )

    print()

    # -------------------------------------------------------------------------
    # 2. Compare text construction
    # -------------------------------------------------------------------------

    print("[2/7] Comparing MOD-004 and MOD-009 text construction...")

    query_source = (
        combined[
            [
                "query_id",
                *QUERY_FIELDS,
            ]
        ]
        .drop_duplicates(
            subset=["query_id"]
        )
        .copy()
    )

    candidate_source = (
        combined[
            [
                "candidate_id",
                *CANDIDATE_FIELDS,
            ]
        ]
        .drop_duplicates(
            subset=["candidate_id"]
        )
        .copy()
    )

    query_source["mod004_text"] = build_mod004_text(
        query_source,
        QUERY_FIELDS,
    )

    query_source["mod009_text"] = build_mod009_text(
        query_source,
        QUERY_FIELDS,
    )

    candidate_source["mod004_text"] = build_mod004_text(
        candidate_source,
        CANDIDATE_FIELDS,
    )

    candidate_source["mod009_text"] = build_mod009_text(
        candidate_source,
        CANDIDATE_FIELDS,
    )

    query_text_mismatch = (
        query_source["mod004_text"]
        != query_source["mod009_text"]
    )

    candidate_text_mismatch = (
        candidate_source["mod004_text"]
        != candidate_source["mod009_text"]
    )

    print(
        f"Unique queries: "
        f"{len(query_source):,}"
    )

    print(
        f"Queries with different text: "
        f"{int(query_text_mismatch.sum()):,}"
    )

    print(
        f"Unique candidates: "
        f"{len(candidate_source):,}"
    )

    print(
        f"Candidates with different text: "
        f"{int(candidate_text_mismatch.sum()):,}"
    )

    print()

    # -------------------------------------------------------------------------
    # 3. Show examples
    # -------------------------------------------------------------------------

    print("[3/7] Showing representative text differences...")

    query_examples = query_source[
        query_text_mismatch
    ].head(3)

    print()
    print("QUERY EXAMPLES:")

    for _, row in query_examples.iterrows():

        print(
            f"\nquery_id={row['query_id']}"
        )

        print(
            "MOD-004:"
        )

        print(
            repr(row["mod004_text"])
        )

        print(
            "MOD-009:"
        )

        print(
            repr(row["mod009_text"])
        )

    candidate_examples = candidate_source[
        candidate_text_mismatch
    ].head(3)

    print()
    print("CANDIDATE EXAMPLES:")

    for _, row in candidate_examples.iterrows():

        print(
            f"\ncandidate_id={row['candidate_id']}"
        )

        print(
            "MOD-004:"
        )

        print(
            repr(row["mod004_text"])
        )

        print(
            "MOD-009:"
        )

        print(
            repr(row["mod009_text"])
        )

    print()

    # -------------------------------------------------------------------------
    # 4. Transform both representations
    # -------------------------------------------------------------------------

    print(
        "[4/7] Transforming both text representations with the "
        "SAVED MOD-004 vectorizer..."
    )

    query_mod004_matrix = vectorizer.transform(
        query_source["mod004_text"]
    )

    query_mod009_matrix = vectorizer.transform(
        query_source["mod009_text"]
    )

    candidate_mod004_matrix = vectorizer.transform(
        candidate_source["mod004_text"]
    )

    candidate_mod009_matrix = vectorizer.transform(
        candidate_source["mod009_text"]
    )

    print(
        f"Query matrix: "
        f"{query_mod004_matrix.shape}"
    )

    print(
        f"Candidate matrix: "
        f"{candidate_mod004_matrix.shape}"
    )

    # -------------------------------------------------------------------------
    # 5. Measure matrix differences
    # -------------------------------------------------------------------------

    print()
    print("[5/7] Measuring TF-IDF representation differences...")

    query_difference = (
        query_mod004_matrix
        != query_mod009_matrix
    )

    candidate_difference = (
        candidate_mod004_matrix
        != candidate_mod009_matrix
    )

    print(
        f"Query matrix differing entries: "
        f"{query_difference.nnz:,}"
    )

    print(
        f"Candidate matrix differing entries: "
        f"{candidate_difference.nnz:,}"
    )

    # -------------------------------------------------------------------------
    # 6. Directly compare scores for MOD-009 candidate mappings
    # -------------------------------------------------------------------------

    print()
    print(
        "[6/7] Comparing scores using MOD-004 vs MOD-009 "
        "text representations..."
    )

    query_index = {
        value: index
        for index, value in enumerate(
            query_source["query_id"]
        )
    }

    candidate_index = {
        value: index
        for index, value in enumerate(
            candidate_source["candidate_id"]
        )
    }

    comparison_records = []

    for row in mod009.itertuples(
        index=False
    ):

        qid = row.query_id
        cid = row.candidate_id

        q_index = query_index[qid]
        c_index = candidate_index[cid]

        score_mod004 = float(
            query_mod004_matrix[q_index]
            .dot(
                candidate_mod004_matrix[c_index].T
            )
            .toarray()[0, 0]
        )

        score_mod009_text = float(
            query_mod009_matrix[q_index]
            .dot(
                candidate_mod009_matrix[c_index].T
            )
            .toarray()[0, 0]
        )

        stored_score = float(
            row.tfidf_score
        )

        comparison_records.append(
            {
                "query_id": qid,
                "candidate_id": cid,
                "stored_mod009_tfidf": stored_score,
                "score_using_mod004_text": score_mod004,
                "score_using_mod009_text": score_mod009_text,
                "stored_minus_mod009_text": (
                    stored_score
                    -
                    score_mod009_text
                ),
                "stored_minus_mod004_text": (
                    stored_score
                    -
                    score_mod004
                ),
                "mod009_text_minus_mod004_text": (
                    score_mod009_text
                    -
                    score_mod004
                ),
            }
        )

    comparison = pd.DataFrame(
        comparison_records
    )

    # -------------------------------------------------------------------------
    # 7. Summarize
    # -------------------------------------------------------------------------

    print()
    print("[7/7] Summarizing reconstruction behavior...")

    stored_vs_mod009 = (
        comparison[
            "stored_minus_mod009_text"
        ].abs()
    )

    stored_vs_mod004 = (
        comparison[
            "stored_minus_mod004_text"
        ].abs()
    )

    text_difference = (
        comparison[
            "mod009_text_minus_mod004_text"
        ].abs()
    )

    print()
    print(
        "Stored MOD-009 score vs MOD-009 text reconstruction:"
    )

    print(
        f"  Mean absolute difference: "
        f"{stored_vs_mod009.mean():.12g}"
    )

    print(
        f"  Median absolute difference: "
        f"{stored_vs_mod009.median():.12g}"
    )

    print(
        f"  Maximum absolute difference: "
        f"{stored_vs_mod009.max():.12g}"
    )

    print()
    print(
        "Stored MOD-009 score vs MOD-004 text reconstruction:"
    )

    print(
        f"  Mean absolute difference: "
        f"{stored_vs_mod004.mean():.12g}"
    )

    print(
        f"  Median absolute difference: "
        f"{stored_vs_mod004.median():.12g}"
    )

    print(
        f"  Maximum absolute difference: "
        f"{stored_vs_mod004.max():.12g}"
    )

    print()
    print(
        "MOD-009 text score vs MOD-004 text score:"
    )

    print(
        f"  Mean absolute difference: "
        f"{text_difference.mean():.12g}"
    )

    print(
        f"  Median absolute difference: "
        f"{text_difference.median():.12g}"
    )

    print(
        f"  Maximum absolute difference: "
        f"{text_difference.max():.12g}"
    )

    # -------------------------------------------------------------------------
    # Largest discrepancies
    # -------------------------------------------------------------------------

    print()
    print(
        "Largest 10 MOD-009-text vs MOD-004-text "
        "score differences:"
    )

    largest = (
        comparison.assign(
            absolute_text_difference=text_difference
        )
        .sort_values(
            "absolute_text_difference",
            ascending=False,
        )
        .head(10)
    )

    print(
        largest[
            [
                "query_id",
                "candidate_id",
                "stored_mod009_tfidf",
                "score_using_mod004_text",
                "score_using_mod009_text",
                "mod009_text_minus_mod004_text",
                "absolute_text_difference",
            ]
        ].to_string(
            index=False
        )
    )

    print()
    print("=" * 80)
    print(
        "T6 MOD-010: "
        "LEXICAL_RECONSTRUCTION_DIAGNOSTIC_COMPLETED"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()