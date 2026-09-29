from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


# =============================================================================
# T6 FINAL MODEL SELECTION + CLOSURE
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

MOD004_RESULTS = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod004_tfidf_retrieval_results.json"
)

MOD007_RESULTS = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod007_bm25_retrieval_results.json"
)

MOD008_RESULTS = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod008_semantic_failure_results.json"
)

MOD009_RESULTS = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod009_hybrid_retrieval_results.json"
)

MOD010_RESULTS = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod010_corrected_hybrid_results.json"
)

MOD010_COMPARISON = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod010_final_comparison.json"
)

MOD010_RANKINGS = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_mod010_corrected_hybrid_query_rankings.csv"
)

OUTPUT_CLOSURE = (
    PROJECT_ROOT
    / "modeling"
    / "T6"
    / "metrics"
    / "t6_final_closure.json"
)


def load_json(path: Path) -> dict:
    with path.open(
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def main() -> None:

    print("=" * 80)
    print("T6 — FINAL MODEL SELECTION + CLOSURE")
    print("=" * 80)
    print()

    # =========================================================================
    # 1. LOAD ALL COMPLETED EVIDENCE
    # =========================================================================

    print("[1/7] Loading completed T6 evidence...")

    mod004 = load_json(MOD004_RESULTS)
    mod007 = load_json(MOD007_RESULTS)
    mod008 = load_json(MOD008_RESULTS)
    mod009 = load_json(MOD009_RESULTS)
    mod010 = load_json(MOD010_RESULTS)
    comparison = load_json(MOD010_COMPARISON)

    rankings = pd.read_csv(
        MOD010_RANKINGS
    )

    print("Evidence loaded.")

    # =========================================================================
    # 2. VERIFY FINAL POPULATION
    # =========================================================================

    print()
    print("[2/7] Verifying final evaluation population...")

    eval_rows = rankings[
        rankings["split"] == "EVAL"
    ]

    eval_queries = eval_rows[
        "query_id"
    ].nunique()

    eval_positive_rows = int(
        eval_rows[
            "target_observed"
        ].sum()
    )

    if len(eval_rows) != 82416:
        raise ValueError(
            "Unexpected final EVAL row count."
        )

    if eval_queries != 816:
        raise ValueError(
            "Unexpected final EVAL query count."
        )

    if eval_positive_rows != 816:
        raise ValueError(
            "Unexpected final EVAL positive count."
        )

    print(
        f"EVAL rows: {len(eval_rows):,}"
    )

    print(
        f"EVAL queries: {eval_queries:,}"
    )

    print(
        f"EVAL observed positives: "
        f"{eval_positive_rows:,}"
    )

    print("Population verification: PASS")

    # =========================================================================
    # 3. VERIFY MOD-010 RECONCILIATION
    # =========================================================================

    print()
    print("[3/7] Verifying corrected lexical reconciliation...")

    lexical_reconciliation = mod010[
        "lexical_reconciliation"
    ]

    if not lexical_reconciliation[
        "hard_gate_passed"
    ]:
        raise ValueError(
            "MOD-010 lexical reconciliation gate failed."
        )

    if lexical_reconciliation[
        "maximum_absolute_difference"
    ] > 1e-12:
        raise ValueError(
            "MOD-010 lexical difference exceeds tolerance."
        )

    if lexical_reconciliation[
        "rows"
    ] != 274922:
        raise ValueError(
            "Unexpected lexical reconciliation population."
        )

    print(
        "Rows reconciled: "
        f"{lexical_reconciliation['rows']:,}"
    )

    print(
        "Maximum absolute difference: "
        f"{lexical_reconciliation['maximum_absolute_difference']}"
    )

    print("Lexical reconciliation: PASS")

    # =========================================================================
    # 4. VERIFY MODEL-SELECTION CONTROLS
    # =========================================================================

    print()
    print("[4/7] Verifying model-selection controls...")

    weight_selection = mod010[
        "weight_selection"
    ]

    selected_weight = weight_selection[
        "selected"
    ]

    selection_split = weight_selection[
        "selection_split"
    ]

    if selection_split != "TRAIN":
        raise ValueError(
            "Hybrid weight was not selected using TRAIN only."
        )

    if mod010[
        "controls"
    ][
        "evaluation_weight_selection"
    ]:
        raise ValueError(
            "Evaluation was used for weight selection."
        )

    if mod010[
        "controls"
    ][
        "raw_dataset_read"
    ]:
        raise ValueError(
            "Raw dataset was read during MOD-010."
        )

    if mod010[
        "controls"
    ][
        "target_modification"
    ]:
        raise ValueError(
            "Target modification detected."
        )

    if mod010[
        "controls"
    ][
        "candidate_pool_modification"
    ]:
        raise ValueError(
            "Candidate-pool modification detected."
        )

    print(
        "Selection split: "
        f"{selection_split}"
    )

    print(
        "Selected lexical weight: "
        f"{selected_weight['lexical_weight']:.2f}"
    )

    print(
        "Selected semantic weight: "
        f"{selected_weight['semantic_weight']:.2f}"
    )

    print("Model-selection controls: PASS")

    # =========================================================================
    # 5. FINAL MODEL EVIDENCE
    # =========================================================================

    print()
    print("[5/7] Consolidating final model evidence...")

    baseline_eval = mod004[
        "evaluation"
    ][
        "metrics"
    ]

    corrected_hybrid_eval = mod010[
        "metrics"
    ][
        "eval"
    ][
        "corrected_hybrid"
    ]

    metric_comparison = comparison[
        "metric_comparison"
    ]

    print()
    print("FINAL EVAL — MOD-004 TF-IDF:")
    for metric, value in baseline_eval.items():
        print(
            f"  {metric}: {value:.6f}"
        )

    print()
    print("FINAL EVAL — MOD-010 CORRECTED HYBRID:")
    for metric, value in corrected_hybrid_eval.items():
        print(
            f"  {metric}: {value:.6f}"
        )

    print()
    print("Observed hybrid-minus-TF-IDF deltas:")

    for metric, values in metric_comparison.items():
        print(
            f"  {metric}: "
            f"{values['absolute_delta']:+.6f}"
        )

    # =========================================================================
    # 6. CLOSURE DECISION
    # =========================================================================

    print()
    print("[6/7] Applying T6 closure criteria...")

    final_model = {
        "name": (
            "Corrected Hybrid Lexical + Semantic "
            "Duplicate-Related Retrieval"
        ),
        "operation": "MOD-010",
        "lexical_component": (
            "MOD-004 exact TF-IDF cosine retrieval"
        ),
        "semantic_component": (
            "all-MiniLM-L6-v2 semantic similarity"
        ),
        "lexical_weight": float(
            selected_weight[
                "lexical_weight"
            ]
        ),
        "semantic_weight": float(
            selected_weight[
                "semantic_weight"
            ]
        ),
        "selection_split": "TRAIN",
    }

    final_role = (
        "SECONDARY_DECISION_SUPPORT_SIGNAL"
    )

    final_status = (
        "SUPPORTED_WITH_LIMITATIONS"
    )

    closure_status = "CLOSED"

    limitations = [
        (
            "T6 is duplicate-related ticket retrieval, "
            "not unrestricted generic similarity retrieval."
        ),
        (
            "The retrieval target is based on subsequently "
            "observed Dupe-of relationships."
        ),
        (
            "Observable non-positive candidates are not "
            "treated as true negatives."
        ),
        (
            "The evaluation measures ranking/retrieval "
            "performance within the frozen 101-candidate "
            "candidate pools."
        ),
        (
            "The evaluation does not establish exhaustive "
            "open-world retrieval performance."
        ),
        (
            "The evaluation does not establish reliable "
            "retrieval for candidates outside the frozen "
            "candidate-pool construction."
        ),
        (
            "The system should not be interpreted as "
            "guaranteeing duplicate identification."
        ),
        (
            "Retrieval output is a decision-support signal "
            "and does not by itself justify autonomous "
            "routing or human-review removal."
        ),
        (
            "Ranking scores are not calibrated probabilities "
            "and no candidate-level probability interpretation "
            "is established."
        ),
        (
            "No automation threshold has been established."
        ),
    ]

    exclusions = [
        (
            "No binary-classification interpretation of "
            "observable_non_positive was used."
        ),
        (
            "No target-ticket pairing claim was made for "
            "missing target IDs."
        ),
        (
            "No post-Creation query information was used."
        ),
        (
            "No current/final Dupe-of field was used as a feature."
        ),
        (
            "No post-Creation administrative fields were used "
            "as prediction features."
        ),
        (
            "No evaluation-based semantic-weight selection "
            "was performed."
        ),
        (
            "No raw dataset modification occurred."
        ),
    ]

    closure = {
        "task_id": "T6",

        "task_name": (
            "Similar-Ticket Retrieval"
        ),

        "operational_task_name": (
            "Duplicate-Related Ticket Retrieval"
        ),

        "task_family": (
            "duplicate_related_ticket_retrieval"
        ),

        "status": closure_status,

        "final_status": final_status,

        "final_system_role": final_role,

        "final_model": final_model,

        "evaluation_population": {
            "rows": int(
                len(eval_rows)
            ),
            "queries": int(
                eval_queries
            ),
            "observed_positive_queries": int(
                eval_positive_rows
            ),
            "candidates_per_query": 101,
        },

        "final_evaluation_metrics": {
            metric: float(value)
            for metric, value
            in corrected_hybrid_eval.items()
        },

        "baseline_comparison": metric_comparison,

        "completed_operations": [
            "MOD-001 Contract Reconciliation",
            "MOD-002 Baseline Modeling Contract",
            "MOD-003 Group-Aware Split Construction",
            "MOD-004 TF-IDF Retrieval Baseline",
            "MOD-005 Baseline Error Analysis",
            "MOD-006 Failure Case Characterization",
            "MOD-007 BM25 Retrieval Baseline",
            "MOD-008 Bounded Semantic Failure Experiment",
            "MOD-009 Hybrid Lexical + Semantic Experiment",
            "MOD-010 Corrected Lexical Reconstruction and Final Controlled Comparison",
        ],

        "final_evidence": {
            "mod004_baseline": (
                "Frozen lexical retrieval baseline"
            ),
            "mod007_bm25": (
                "Alternative lexical retrieval comparison"
            ),
            "mod008_semantic": (
                "Bounded semantic diagnostic"
            ),
            "mod009_original": (
                "Original hybrid artifact retained as "
                "non-final due lexical representation mismatch"
            ),
            "mod010_corrected": (
                "Corrected hybrid with exact MOD-004 lexical "
                "reconciliation"
            ),
        },

        "limitations": limitations,

        "explicit_exclusions": exclusions,

        "controls": {
            "lexical_reconciliation_passed": True,
            "evaluation_population_frozen": True,
            "candidate_pool_frozen": True,
            "weight_selection_train_only": True,
            "raw_dataset_modified": False,
            "target_modified": False,
            "candidate_pool_modified": False,
            "evaluation_used_for_weight_selection": False,
            "calibration_performed": False,
            "automation_threshold_established": False,
            "binary_classification_primary": False,
        },

        "decision_statement": (
            "T6 is closed as a supported-with-limitations "
            "secondary decision-support retrieval capability. "
            "The corrected 0.50 lexical / 0.50 semantic hybrid "
            "is retained as the final advanced retrieval candidate "
            "because its lexical component exactly reproduces the "
            "frozen MOD-004 baseline and its hybrid weight was "
            "selected using TRAIN only. The frozen EVAL population "
            "shows the documented retrieval metrics. These results "
            "do not establish exhaustive open-world duplicate "
            "retrieval, autonomous decision-making, calibrated "
            "probabilities, or removal of human review."
        ),
    }

    # =========================================================================
    # 7. WRITE CLOSURE ARTIFACT
    # =========================================================================

    print()
    print("[7/7] Writing final T6 closure artifact...")

    with OUTPUT_CLOSURE.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            closure,
            f,
            indent=2,
        )

    print()
    print(
        f"Closure artifact: {OUTPUT_CLOSURE}"
    )

    print()
    print("=" * 80)
    print("T6 FINAL CLOSURE")
    print("=" * 80)
    print()
    print(
        f"Status: {closure_status}"
    )
    print(
        f"Final status: {final_status}"
    )
    print(
        f"System role: {final_role}"
    )
    print()
    print(
        "Final model:"
    )
    print(
        f"  Lexical weight: "
        f"{final_model['lexical_weight']:.2f}"
    )
    print(
        f"  Semantic weight: "
        f"{final_model['semantic_weight']:.2f}"
    )
    print()
    print(
        "T6 FINAL MODEL SELECTION + CLOSURE: COMPLETED"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()