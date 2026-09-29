from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import load


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T6_ROOT = ROOT / "modeling" / "T6"

EVAL_PATH = (
    T6_ROOT
    / "splits"
    / "t6_eval_group_aware.csv"
)

TFIDF_PATH = (
    T6_ROOT
    / "models"
    / "t6_mod004_tfidf_vectorizer.joblib"
)

MOD009_RANKINGS_PATH = (
    T6_ROOT
    / "metrics"
    / "t6_mod009_hybrid_query_rankings.csv"
)

OUTPUT_PATH = (
    ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "fmp06_op018r21_t6_mod010_frozen_runtime_composition_probe.json"
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

SELECTED_SEMANTIC_WEIGHT = 0.50
SELECTED_LEXICAL_WEIGHT = 0.50


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""

    return str(value).strip()


def build_text(
    frame: pd.DataFrame,
    columns: list[str],
) -> pd.Series:

    parts = []

    for column in columns:

        field_name = column.replace(
            "_",
            " ",
        )

        values = frame[column].map(
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


def minmax_normalize(
    values: np.ndarray,
) -> np.ndarray:

    minimum = float(
        np.min(values)
    )

    maximum = float(
        np.max(values)
    )

    if maximum > minimum:

        return (
            values - minimum
        ) / (
            maximum - minimum
        )

    return np.zeros_like(
        values,
        dtype=np.float64,
    )


def find_column(
    frame: pd.DataFrame,
    candidates: list[str],
) -> str | None:

    for candidate in candidates:

        if candidate in frame.columns:
            return candidate

    return None


def main() -> None:

    print("=" * 72)
    print(
        "FMP-06 OP-018R21 — "
        "T6 MOD-010 FROZEN RUNTIME COMPOSITION PROBE"
    )
    print("=" * 72)

    print()
    print("Read-only runtime probe: YES")
    print("Training/fitting: NO")
    print("Evaluation metrics: NO")
    print("Locked test population: NO")
    print("Artifact modification: NO")
    print("Semantic model loading: NO")
    print("Weight selection: NO")
    print("Selected semantic weight: 0.50")
    print("Selected lexical weight: 0.50")

    report = {
        "operation": "FMP-06 OP-018R21",
        "status": "PASS",
        "read_only": True,
        "training_performed": False,
        "fitting_performed": False,
        "evaluation_metrics_calculated": False,
        "locked_test_used": False,
        "artifact_modified": False,
        "semantic_model_loaded": False,
        "weight_selection_performed": False,
        "selected_semantic_weight": 0.50,
        "selected_lexical_weight": 0.50,
    }

    # ---------------------------------------------------------------
    # 1. Verify required files
    # ---------------------------------------------------------------

    print()
    print("[1] Verifying frozen runtime inputs...")

    required_files = [
        EVAL_PATH,
        TFIDF_PATH,
        MOD009_RANKINGS_PATH,
    ]

    for path in required_files:

        exists = path.exists()

        print(
            f"  {'FOUND' if exists else 'MISSING'}: "
            f"{path.relative_to(ROOT)}"
        )

        if not exists:
            raise FileNotFoundError(
                f"Required file missing: {path}"
            )

    # ---------------------------------------------------------------
    # 2. Load native evaluation population
    # ---------------------------------------------------------------

    print()
    print("[2] Loading native T6 evaluation population...")

    eval_df = pd.read_csv(
        EVAL_PATH
    )

    print(
        f"Evaluation rows available: "
        f"{len(eval_df):,}"
    )

    required_eval_columns = (
        QUERY_FIELDS
        + CANDIDATE_FIELDS
        + [
            "query_id",
            "candidate_id",
        ]
    )

    missing_eval_columns = [
        column
        for column in required_eval_columns
        if column not in eval_df.columns
    ]

    if missing_eval_columns:
        raise ValueError(
            "Missing native T6 columns: "
            + repr(missing_eval_columns)
        )

    print(
        "Native T6 schema: VERIFIED"
    )

    # ---------------------------------------------------------------
    # 3. Select one complete native query
    # ---------------------------------------------------------------

    print()
    print(
        "[3] Selecting one complete native query "
        "for runtime probing..."
    )

    first_query_id = eval_df.iloc[0][
        "query_id"
    ]

    probe_df = eval_df[
        eval_df["query_id"]
        == first_query_id
    ].copy()

    probe_df = probe_df.reset_index(
        drop=True
    )

    if len(probe_df) < 2:
        raise ValueError(
            "Selected query has fewer than "
            "2 candidate rows."
        )

    print(
        f"Selected query_id: "
        f"{first_query_id}"
    )

    print(
        f"Candidate rows for probe: "
        f"{len(probe_df):,}"
    )

    print(
        f"Candidate IDs unique: "
        f"{probe_df['candidate_id'].nunique()}"
    )

    # ---------------------------------------------------------------
    # 4. Load frozen lexical component
    # ---------------------------------------------------------------

    print()
    print(
        "[4] Loading frozen MOD-004 TF-IDF vectorizer..."
    )

    vectorizer = load(
        TFIDF_PATH
    )

    print(
        f"Vectorizer type: "
        f"{type(vectorizer).__name__}"
    )

    if not hasattr(
        vectorizer,
        "transform",
    ):
        raise TypeError(
            "Frozen vectorizer does not expose transform()."
        )

    print(
        "Frozen transform interface: VERIFIED"
    )

    # ---------------------------------------------------------------
    # 5. Reconstruct exact native MOD-004 text
    # ---------------------------------------------------------------

    print()
    print(
        "[5] Reconstructing exact MOD-004 "
        "lexical text representation..."
    )

    query_frame = (
        probe_df[
            [
                "query_id",
                *QUERY_FIELDS,
            ]
        ]
        .drop_duplicates(
            subset=["query_id"]
        )
        .reset_index(drop=True)
    )

    query_text = build_text(
        query_frame,
        QUERY_FIELDS,
    ).iloc[0]

    candidate_text = build_text(
        probe_df,
        CANDIDATE_FIELDS,
    )

    print(
        f"Query text length: "
        f"{len(query_text):,}"
    )

    print(
        f"Candidate text rows: "
        f"{len(candidate_text):,}"
    )

    # ---------------------------------------------------------------
    # 6. Execute frozen lexical component
    # ---------------------------------------------------------------

    print()
    print(
        "[6] Executing frozen TF-IDF lexical component..."
    )

    query_matrix = vectorizer.transform(
        [query_text]
    )

    candidate_matrix = vectorizer.transform(
        candidate_text
    )

    lexical_scores = (
        candidate_matrix
        @ query_matrix.T
    ).toarray().ravel()

    lexical_scores = np.asarray(
        lexical_scores,
        dtype=np.float64,
    )

    print(
        f"Query transformed shape: "
        f"{query_matrix.shape}"
    )

    print(
        f"Candidate transformed shape: "
        f"{candidate_matrix.shape}"
    )

    print(
        f"Lexical scores generated: "
        f"{len(lexical_scores):,}"
    )

    # ---------------------------------------------------------------
    # 7. Load stored MOD-009 semantic evidence
    # ---------------------------------------------------------------

    print()
    print(
        "[7] Loading stored MOD-009 semantic evidence..."
    )

    mod009 = pd.read_csv(
        MOD009_RANKINGS_PATH
    )

    print(
        f"MOD-009 rows available: "
        f"{len(mod009):,}"
    )

    query_id_column = find_column(
        mod009,
        [
            "query_id",
        ],
    )

    candidate_id_column = find_column(
        mod009,
        [
            "candidate_id",
        ],
    )

    semantic_score_column = find_column(
        mod009,
        [
            "semantic_score",
        ],
    )

    if query_id_column is None:
        raise ValueError(
            "MOD-009 rankings do not contain query_id."
        )

    if candidate_id_column is None:
        raise ValueError(
            "MOD-009 rankings do not contain candidate_id."
        )

    if semantic_score_column is None:
        raise ValueError(
            "MOD-009 rankings do not contain semantic_score."
        )

    semantic_probe = mod009[
        mod009[query_id_column]
        == first_query_id
    ][
        [
            query_id_column,
            candidate_id_column,
            semantic_score_column,
        ]
    ].copy()

    print(
        f"MOD-009 semantic rows for probe query: "
        f"{len(semantic_probe):,}"
    )

    if len(semantic_probe) == 0:
        raise ValueError(
            "No MOD-009 semantic evidence found "
            "for selected query."
        )

    semantic_probe = semantic_probe.rename(
        columns={
            query_id_column: "query_id",
            candidate_id_column: "candidate_id",
            semantic_score_column: "semantic_score",
        }
    )

    # ---------------------------------------------------------------
    # 8. Align semantic evidence to native candidates
    # ---------------------------------------------------------------

    print()
    print(
        "[8] Aligning stored semantic evidence "
        "to native candidate population..."
    )

    probe_df["lexical_score"] = lexical_scores

    merged = probe_df[
        [
            "query_id",
            "candidate_id",
            "lexical_score",
        ]
    ].merge(
        semantic_probe,
        on=[
            "query_id",
            "candidate_id",
        ],
        how="left",
        validate="one_to_one",
    )

    missing_semantic = int(
        merged["semantic_score"]
        .isna()
        .sum()
    )

    print(
        f"Aligned rows: "
        f"{len(merged):,}"
    )

    print(
        f"Missing semantic scores: "
        f"{missing_semantic:,}"
    )

    if missing_semantic != 0:
        raise ValueError(
            "Semantic evidence did not align "
            "completely with native candidate rows."
        )

    # ---------------------------------------------------------------
    # 9. Exact per-query normalization
    # ---------------------------------------------------------------

    print()
    print(
        "[9] Applying exact MOD-010 "
        "per-query normalization..."
    )

    lexical_array = merged[
        "lexical_score"
    ].to_numpy(
        dtype=np.float64
    )

    semantic_array = merged[
        "semantic_score"
    ].to_numpy(
        dtype=np.float64
    )

    lexical_normalized = minmax_normalize(
        lexical_array
    )

    semantic_normalized = minmax_normalize(
        semantic_array
    )

    merged[
        "lexical_score_normalized"
    ] = lexical_normalized

    merged[
        "semantic_score_normalized"
    ] = semantic_normalized

    print(
        "Lexical normalization: VERIFIED"
    )

    print(
        "Semantic normalization: VERIFIED"
    )

    # ---------------------------------------------------------------
    # 10. Apply already-selected MOD-010 weight
    # ---------------------------------------------------------------

    print()
    print(
        "[10] Applying frozen MOD-010 "
        "0.50 / 0.50 composition..."
    )

    merged["hybrid_score"] = (
        SELECTED_LEXICAL_WEIGHT
        * merged[
            "lexical_score_normalized"
        ]
        +
        SELECTED_SEMANTIC_WEIGHT
        * merged[
            "semantic_score_normalized"
        ]
    )

    print(
        "Lexical weight: "
        f"{SELECTED_LEXICAL_WEIGHT:.2f}"
    )

    print(
        "Semantic weight: "
        f"{SELECTED_SEMANTIC_WEIGHT:.2f}"
    )

    print(
        "Hybrid score generation: VERIFIED"
    )

    # ---------------------------------------------------------------
    # 11. Produce small runtime evidence sample
    # ---------------------------------------------------------------

    print()
    print(
        "[11] Producing runtime evidence sample..."
    )

    sample = (
        merged.sort_values(
            [
                "hybrid_score",
                "candidate_id",
            ],
            ascending=[
                False,
                True,
            ],
            kind="mergesort",
        )
        .head(5)
    )

    sample_records = []

    for _, row in sample.iterrows():

        sample_records.append(
            {
                "query_id": int(
                    row["query_id"]
                ),
                "candidate_id": int(
                    row["candidate_id"]
                ),
                "lexical_score": float(
                    row["lexical_score"]
                ),
                "semantic_score": float(
                    row["semantic_score"]
                ),
                "lexical_score_normalized": float(
                    row[
                        "lexical_score_normalized"
                    ]
                ),
                "semantic_score_normalized": float(
                    row[
                        "semantic_score_normalized"
                    ]
                ),
                "hybrid_score": float(
                    row["hybrid_score"]
                ),
            }
        )

    for record in sample_records:

        print(
            "  candidate_id="
            f"{record['candidate_id']} "
            f"lexical="
            f"{record['lexical_score']:.6f} "
            f"semantic="
            f"{record['semantic_score']:.6f} "
            f"hybrid="
            f"{record['hybrid_score']:.6f}"
        )

    # ---------------------------------------------------------------
    # 12. Final runtime assertions
    # ---------------------------------------------------------------

    print()
    print(
        "[12] Verifying runtime invariants..."
    )

    assertions = {
        "native_query_population": (
            len(probe_df) > 1
        ),
        "lexical_scores_complete": (
            len(lexical_scores)
            == len(probe_df)
        ),
        "semantic_alignment_complete": (
            missing_semantic == 0
        ),
        "lexical_normalization_complete": (
            merged[
                "lexical_score_normalized"
            ].notna().all()
        ),
        "semantic_normalization_complete": (
            merged[
                "semantic_score_normalized"
            ].notna().all()
        ),
        "hybrid_scores_complete": (
            merged[
                "hybrid_score"
            ].notna().all()
        ),
        "weights_sum_to_one": (
            abs(
                (
                    SELECTED_LEXICAL_WEIGHT
                    +
                    SELECTED_SEMANTIC_WEIGHT
                )
                - 1.0
            )
            < 1e-12
        ),
        "semantic_model_not_loaded": True,
    }

    for name, value in assertions.items():

        print(
            f"  {name}: "
            f"{'PASS' if value else 'FAIL'}"
        )

    if not all(
        assertions.values()
    ):
        raise AssertionError(
            "One or more runtime invariants failed."
        )

    report.update(
        {
            "runtime_status": "PASS",
            "query_id": int(
                first_query_id
            ),
            "probe_candidate_count": int(
                len(probe_df)
            ),
            "lexical_component": {
                "artifact": str(
                    TFIDF_PATH.relative_to(ROOT)
                ),
                "type": type(
                    vectorizer
                ).__name__,
                "transform_executed": True,
            },
            "semantic_component": {
                "source": str(
                    MOD009_RANKINGS_PATH.relative_to(ROOT)
                ),
                "column": "semantic_score",
                "model_not_loaded": True,
                "scores_reused_from_MOD009": True,
            },
            "normalization": {
                "method": "per_query_minmax",
                "lexical_normalized": True,
                "semantic_normalized": True,
            },
            "hybrid_composition": {
                "lexical_weight": 0.50,
                "semantic_weight": 0.50,
                "formula": (
                    "0.50 * lexical_score_normalized "
                    "+ 0.50 * semantic_score_normalized"
                ),
            },
            "sample": sample_records,
        }
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 72)
    print(
        "OP-018R21 RUNTIME COMPOSITION PROBE COMPLETE"
    )
    print("=" * 72)

    print(
        f"Output: {OUTPUT_PATH}"
    )

    print()
    print("No model fitting performed.")
    print("No artifact modification performed.")
    print("No evaluation metrics calculated.")
    print("No locked test population used.")
    print("No SentenceTransformer loaded.")
    print("No weight selection performed.")

    print("=" * 72)


if __name__ == "__main__":
    main()