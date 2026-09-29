from pathlib import Path
import json


PROJECT_ROOT = Path(__file__).resolve().parents[3]

CONTRACT_DIR = PROJECT_ROOT / "modeling" / "T4" / "contracts"
CONTRACT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = CONTRACT_DIR / "t4_ranking_contract.json"


contract = {
    "experiment_id": "T4-MOD-007",
    "title": "Historical Similarity Assignee Ranking Baseline",
    "status": "FROZEN_DESIGN",

    "objective": (
        "Evaluate specific-assignee routing as a candidate-ranking/"
        "information-retrieval problem rather than as a flat "
        "multiclass classification problem."
    ),

    "frozen_source": {
        "dataset": "Mozilla CORE",
        "accepted_artifact": (
            "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
            "DTM-002_T4_FIRST_SPECIFIC_ASSIGNEE_derived.csv"
        ),
        "modeling_artifact": (
            "modeling/T4/derived/t4_features.csv"
        ),
        "raw_mozilla_accessed": False,
        "target_reconstructed": False
    },

    "target": {
        "definition": (
            "First post-Creation assignment to a specific assignee."
        ),
        "target_column": "target_assignee",
        "target_time_column": "target_assignment_time",
        "nobody_excluded": True,
        "global_historical_target_assignees": 4809,
        "training_observed_candidate_assignees": 4139
    },

    "prediction_boundary": {
        "boundary": "Creation",
        "admitted_features": [
            "Creator",
            "Creator Detail",
            "Summary",
            "Description"
        ],
        "forbidden_target_side_fields": [
            "target_assignee",
            "target_assignment_time",
            "target_event_index",
            "target_change_index"
        ],
        "current_assignment_fields_forbidden": True
    },

    "data_split": {
        "method": "chronological",
        "train_rows": 142501,
        "evaluation_rows": 35626,
        "id_overlap": 0,
        "evaluation_distinct_targets": 1161,
        "covered_evaluation_rows": 32773,
        "unseen_evaluation_rows": 2853,
        "unseen_evaluation_rate": 0.08008196
    },

    "problem_formulation": {
        "type": "candidate_ranking",
        "closed_world_candidate_pool": (
            "Assignees observed in the training period only."
        ),
        "open_world_behavior": (
            "Evaluation targets unseen during training remain in "
            "evaluation and are explicitly reported as unseen-target "
            "cases. They are not converted into negatives or removed."
        ),
        "historical_evidence_unit": (
            "Training-period tickets available before the evaluation "
            "prediction boundary."
        )
    },

    "ranking_pipeline": {
        "representation": (
            "TF-IDF representation of Creation-time ticket text "
            "constructed from Creator, Creator Detail, Summary, "
            "and Description."
        ),
        "retrieval": (
            "Retrieve the most similar historical training tickets "
            "for each evaluation ticket."
        ),
        "candidate_generation": (
            "Collect assignees associated with retrieved historical "
            "tickets."
        ),
        "candidate_scoring": (
            "Aggregate historical similarity evidence by assignee "
            "to produce a ranked candidate list."
        ),
        "final_output": [
            "Top-1 assignee",
            "Top-3 assignees",
            "Top-5 assignees",
            "Top-10 assignees"
        ]
    },

    "evaluation_metrics": {
        "primary_ranking_metrics": [
            "MRR",
            "NDCG@5",
            "NDCG@10"
        ],
        "retrieval_metrics": [
            "Hit@1",
            "Hit@3",
            "Hit@5",
            "Hit@10"
        ],
        "supporting_metrics": [
            "Macro-F1",
            "Weighted-F1",
            "covered-target performance",
            "unseen-target diagnostics"
        ],
        "coverage": (
            "Report the proportion of evaluation tickets for which "
            "the historical ranking pipeline can generate candidates."
        )
    },

    "evaluation_stratification": {
        "historical_support_buckets": [
            "1",
            "2-5",
            "6-10",
            "11-20",
            "21-50",
            "51-100",
            "101+"
        ],
        "required_comparison": (
            "Compare ranking performance across historical "
            "assignee-support buckets."
        )
    },

    "leakage_controls": [
        "Use only Creation-time admitted features.",
        "Use only training-period historical tickets for retrieval.",
        "Do not retrieve from evaluation tickets.",
        "Do not use target assignment time as a feature.",
        "Do not use current mutable assignment fields.",
        "Do not use future/post-Creation information.",
        "Do not silently remove unseen evaluation targets.",
        "Do not treat unseen targets as negative examples.",
        "Do not claim historical assignment is universal routing correctness."
    ],

    "computational_controls": {
        "raw_archive_access": False,
        "full_raw_dataset_scan": False,
        "training_model_required": False,
        "initial_retrieval_scope": (
            "Controlled experiment using the existing modeling-only "
            "train/evaluation artifacts."
        ),
        "checkpoint_required": True
    },

    "business_interpretation": {
        "system_role": "secondary decision-support signal",
        "output_interpretation": (
            "Ranked historically plausible assignee candidates "
            "for human triager review."
        ),
        "prohibited_claims": [
            "Autonomous assignment correctness",
            "Universal operational eligibility",
            "Guaranteed triager time savings"
        ],
        "future_business_evaluation": (
            "A human evaluation may later compare manual routing "
            "time against routing with ranked recommendations. "
            "No time-saving claim is made without empirical measurement."
        )
    },

    "comparison_with_T4_MOD_006_R1": {
        "baseline": "Flat multiclass LinearSVC",
        "baseline_top1_accuracy": 0.281059,
        "baseline_top3_accuracy": 0.363527,
        "baseline_top5_accuracy": 0.401926,
        "baseline_top10_accuracy": 0.450065,
        "covered_top1_accuracy": 0.3055258902145058,
        "covered_top10_accuracy": 0.48924419491654714,
        "purpose": (
            "T4-MOD-006-R1 remains the controlled classical "
            "classification baseline against which T4-MOD-007 "
            "ranking performance will be compared."
        )
    },

    "decision_rule": (
        "T4-MOD-007 will be evaluated against the frozen baseline "
        "without assuming that ranking will outperform classification. "
        "The formulation will be judged using ranking quality, "
        "coverage, long-tail behavior, and open-world diagnostics."
    )
}


with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(contract, f, indent=2)


print("T4-MOD-007_CONTRACT_COMPLETE")
print(f"OUTPUT={OUTPUT_PATH}")
print("STATUS=FROZEN_DESIGN")
print("RAW_MOZILLA_ACCESSED=False")
print("MODEL_TRAINED=False")
print("PREDICTIONS_CREATED=False")
print("TEST_USED=False")
