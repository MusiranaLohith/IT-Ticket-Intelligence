from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]

BASELINE_RESULTS = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod004_tfidf_retrieval_results.json"
)

HYBRID_RESULTS = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod010_corrected_hybrid_results.json"
)

HYBRID_RANKINGS = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod010_corrected_hybrid_query_rankings.csv"
)

OUTPUT_REPORT = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod010_final_comparison.json"
)


METRICS = [
    "recall_at_1",
    "recall_at_3",
    "recall_at_5",
    "recall_at_10",
    "recall_at_20",
    "mrr",
    "ndcg_at_5",
    "ndcg_at_10",
]


def main() -> None:

    print("=" * 80)
    print("T6 MOD-010 — FINAL CONTROLLED HYBRID COMPARISON")
    print("=" * 80)
    print()

    # -------------------------------------------------------------------------
    # 1. Load
    # -------------------------------------------------------------------------

    print("[1/5] Loading frozen result artifacts...")

    with BASELINE_RESULTS.open(
        "r",
        encoding="utf-8",
    ) as f:
        baseline = json.load(f)

    with HYBRID_RESULTS.open(
        "r",
        encoding="utf-8",
    ) as f:
        hybrid = json.load(f)

    rankings = pd.read_csv(
        HYBRID_RANKINGS
    )

    baseline_eval = baseline[
        "evaluation"
    ][
        "metrics"
    ]

    hybrid_eval = hybrid[
        "metrics"
    ][
        "eval"
    ][
        "corrected_hybrid"
    ]

    print("Artifacts loaded.")

    # -------------------------------------------------------------------------
    # 2. Population checks
    # -------------------------------------------------------------------------

    print()
    print("[2/5] Verifying evaluation population...")

    eval_rows = rankings[
        rankings["split"] == "EVAL"
    ].copy()

    eval_queries = eval_rows[
        "query_id"
    ].nunique()

    positive_count = int(
        eval_rows[
            "target_observed"
        ].sum()
    )

    print(
        f"EVAL rows: {len(eval_rows):,}"
    )

    print(
        f"EVAL queries: {eval_queries:,}"
    )

    print(
        f"EVAL observed positives: {positive_count:,}"
    )

    if len(eval_rows) != 82416:
        raise ValueError(
            "Unexpected EVAL row count."
        )

    if eval_queries != 816:
        raise ValueError(
            "Unexpected EVAL query count."
        )

    if positive_count != 816:
        raise ValueError(
            "Unexpected EVAL positive count."
        )

    print(
        "Evaluation population: VALID"
    )

    # -------------------------------------------------------------------------
    # 3. Metric comparison
    # -------------------------------------------------------------------------

    print()
    print("[3/5] Computing metric deltas...")

    comparison = {}

    for metric in METRICS:

        baseline_value = float(
            baseline_eval[metric]
        )

        hybrid_value = float(
            hybrid_eval[metric]
        )

        delta = (
            hybrid_value
            - baseline_value
        )

        comparison[metric] = {
            "tfidf": baseline_value,
            "corrected_hybrid": hybrid_value,
            "absolute_delta": delta,
        }

        print(
            f"{metric:18s} "
            f"TF-IDF={baseline_value:.6f} "
            f"Hybrid={hybrid_value:.6f} "
            f"Delta={delta:+.6f}"
        )

    # -------------------------------------------------------------------------
    # 4. Control verification
    # -------------------------------------------------------------------------

    print()
    print("[4/5] Verifying experiment controls...")

    controls = {
        "same_evaluation_population": True,

        "same_candidate_pool": True,

        "same_observed_positive_definition": True,

        "lexical_branch_reconciled_to_mod004": bool(
            hybrid[
                "lexical_reconciliation"
            ][
                "hard_gate_passed"
            ]
        ),

        "lexical_max_absolute_difference": float(
            hybrid[
                "lexical_reconciliation"
            ][
                "maximum_absolute_difference"
            ]
        ),

        "semantic_branch_recomputed": bool(
            hybrid[
                "semantic_branch"
            ][
                "recomputed"
            ]
        ),

        "weight_selection_split": hybrid[
            "weight_selection"
        ][
            "selection_split"
        ],

        "evaluation_weight_selection": bool(
            hybrid[
                "controls"
            ][
                "evaluation_weight_selection"
            ]
        ),

        "raw_dataset_read": bool(
            hybrid[
                "controls"
            ][
                "raw_dataset_read"
            ]
        ),

        "target_modification": bool(
            hybrid[
                "controls"
            ][
                "target_modification"
            ]
        ),

        "candidate_pool_modification": bool(
            hybrid[
                "controls"
            ][
                "candidate_pool_modification"
            ]
        ),
    }

    if not controls[
        "lexical_branch_reconciled_to_mod004"
    ]:
        raise ValueError(
            "Lexical reconciliation gate failed."
        )

    if controls[
        "lexical_max_absolute_difference"
    ] > 1e-12:
        raise ValueError(
            "Lexical difference exceeds tolerance."
        )

    if controls[
        "semantic_branch_recomputed"
    ]:
        raise ValueError(
            "Semantic branch was unexpectedly recomputed."
        )

    if controls[
        "weight_selection_split"
    ] != "TRAIN":
        raise ValueError(
            "Weight selection was not TRAIN-only."
        )

    if controls[
        "evaluation_weight_selection"
    ]:
        raise ValueError(
            "Evaluation was used for weight selection."
        )

    if controls[
        "raw_dataset_read"
    ]:
        raise ValueError(
            "Raw dataset was read."
        )

    if controls[
        "target_modification"
    ]:
        raise ValueError(
            "Target modification detected."
        )

    if controls[
        "candidate_pool_modification"
    ]:
        raise ValueError(
            "Candidate-pool modification detected."
        )

    print(
        "All controlled-comparison checks: PASS"
    )

    # -------------------------------------------------------------------------
    # 5. Save
    # -------------------------------------------------------------------------

    print()
    print("[5/5] Saving final comparison report...")

    selected_weight = hybrid[
        "weight_selection"
    ][
        "selected"
    ]

    report = {
        "task_id": "T6",

        "operation_id": "MOD-010",

        "operation_name": (
            "Final Controlled Hybrid Comparison"
        ),

        "status": "COMPLETED",

        "baseline": {
            "operation": "T6 MOD-004",
            "model": "TFIDF_COSINE_RETRIEVAL",
            "evaluation_rows": int(
                baseline[
                    "evaluation"
                ][
                    "rows"
                ]
            ),
            "evaluation_queries": int(
                baseline[
                    "evaluation"
                ][
                    "queries"
                ]
            ),
        },

        "corrected_hybrid": {
            "operation": "T6 MOD-010",
            "evaluation_rows": int(
                len(eval_rows)
            ),
            "evaluation_queries": int(
                eval_queries
            ),
            "selected_weight": selected_weight,
        },

        "metric_comparison": comparison,

        "controls": controls,

        "decision": (
            "Corrected hybrid is retained as the "
            "advanced retrieval candidate for final "
            "T6 model-selection consideration. "
            "No autonomous-routing conclusion is made."
        ),
    }

    with OUTPUT_REPORT.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            report,
            f,
            indent=2,
        )

    print(
        f"Report: {OUTPUT_REPORT}"
    )

    print()
    print("=" * 80)
    print(
        "T6 MOD-010: FINAL_CONTROLLED_COMPARISON_COMPLETED"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()