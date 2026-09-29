from pathlib import Path
import json


PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T2"
    / "contracts"
    / "t2_model_contract.json"
)


CONTRACT = {
    "operation": "T2-MOD-002",
    "operation_name": "T2 MODELING CONTRACT RECONCILIATION",
    "task": "T2",
    "task_name": "Priority Prediction",

    "status": "READY_FOR_CONTROLLED_MODELING",
    "contract_status": "RECONCILED",

    "source_authority": {
        "dataset": "Mozilla CORE",
        "dtm": "DTM-002",
        "final_readiness_operation": "OP-036",
        "task_contract_operation": "OP-024",
        "feature_admissibility_operation": "OP-035",
    },

    "dataset": {
        "name": "Mozilla CORE",
        "role": "PRIMARY_T2_DATASET",
        "derived_artifact": (
            "/run/media/whiteblack/User 1/Datasets/"
            "Mozilla_CORE/"
            "DTM-002_T2_FIRST_PRIORITY_24H_derived.csv"
        ),
        "eligible_records": 29498,
        "derived_artifact_rows": 29498,
        "derived_artifact_columns": 24,
        "raw_source_immutable": True,
        "rn136_immutable": True,
    },

    "objective": {
        "statement": (
            "Predict the first valid P1-P5 Priority assigned "
            "strictly after Creation and within the following "
            "24-hour observation window using information "
            "available at the Creation boundary."
        ),
        "prediction_unit": "ticket",
        "task_type": "multiclass_classification",
    },

    "target": {
        "physical_field": "target_priority",
        "semantic_name": "priority",
        "semantic_definition": (
            "Earliest valid P1-P5 Priority assignment occurring "
            "strictly after Creation and within the subsequent "
            "24-hour window."
        ),
        "classes": [
            "P1",
            "P2",
            "P3",
            "P4",
            "P5",
        ],
        "class_counts": {
            "P1": 7325,
            "P2": 9156,
            "P3": 11015,
            "P4": 784,
            "P5": 1218,
        },
        "target_total": 29498,
        "target_directly_observed": True,
        "target_semantics_frozen": True,
    },

    "prediction_boundary": {
        "event": "Creation",
        "horizon_hours": 24,
        "strictly_after_creation": True,
        "allowed_information": (
            "Information legitimately available at the "
            "Creation prediction boundary."
        ),
        "future_information_forbidden": True,
        "post_creation_information_forbidden": True,
        "future_target_information_forbidden": True,
    },

    "admitted_features": {
        "feature_sources": [
            "Summary",
            "Description",
        ],

        "Summary": {
            "status": "ADMITTED",
            "semantic_role": "submitted_ticket_content",
            "coverage_records": 29498,
            "coverage_fraction": 1.0,
            "missing_records": 0,
            "missingness_preserved": True,
        },

        "Description": {
            "status": "ADMITTED",
            "semantic_role": "submitted_ticket_content",
            "coverage_records": 27906,
            "coverage_fraction": 0.9460,
            "missing_records": 1592,
            "missing_fraction": 0.0540,
            "missingness_preserved": True,
            "backfill_forbidden": True,
        },

        "feature_materialization_required": True,

        "feature_materialization_note": (
            "The accepted 24-column T2 target artifact does not "
            "physically contain Summary and Description. The "
            "admitted modeling feature boundary therefore requires "
            "a controlled feature-materialization step using the "
            "same 29,498 frozen T2 IDs. The target artifact itself "
            "must remain unchanged."
        ),
    },

    "rn136_historical_features": {
        "source": "RN136_D6_historical_features.csv",
        "status": "FROZEN_BUT_UNAVAILABLE_FOR_T2_POPULATION",
        "fields": [
            "Product_historical",
            "Component_historical",
            "Priority_historical",
            "Status_historical",
            "Keywords_historical",
            "Blocks_historical",
            "CC_historical",
        ],
        "availability_all_zero": True,
        "available_records_per_field": 0,
        "total_t2_records": 29498,
        "use_as_predictive_features": False,
        "current_state_substitution_forbidden": True,
        "final_state_substitution_forbidden": True,
        "dataset_rebuild_forbidden": True,
    },

    "excluded_features": {
        "current_mutable_fields": [
            "Product",
            "Component",
            "Priority",
            "Severity",
            "Status",
            "Keywords",
            "Version",
            "Platform",
            "Target Milestone",
            "Classification",
        ],
        "future_or_post_cutoff_information": [
            "Future Priority assignments",
            "Post-Creation Priority changes",
            "Post-Creation administrative changes",
            "Post-Creation workflow information",
            "Future events",
            "Target-derived information",
        ],
        "target_related_columns": [
            "target_priority",
            "target_priority_time",
            "target_elapsed_seconds",
            "t2_target_definition",
        ],
        "metadata_only_columns": [
            "ID",
            "Creation time",
            "t2_prediction_cutoff",
            "t2_horizon_hours",
            "t2_contract",
            "t2_source_artifact",
        ],
    },

    "missingness_policy": {
        "description_missing_records": 1592,
        "description_missing_fraction": 0.0540,
        "missing_description_must_remain_missing": True,
        "later_value_backfill_forbidden": True,
        "fabricated_text_forbidden": True,
    },

    "leakage_controls": {
        "creation_boundary_frozen": True,
        "future_target_excluded": True,
        "post_creation_information_excluded": True,
        "current_mutable_backfill_forbidden": True,
        "rn136_unavailable_features_not_substituted": True,
        "target_derived_features_excluded": True,
        "evaluation_data_must_not_be_used_for_fit": True,
    },

    "modeling_policy": {
        "baseline_required_before_advanced_model": True,
        "model_selected": False,
        "training_started": False,
        "advanced_model_preselected": False,
        "evaluation_used_for_training": False,
        "final_architecture_frozen": False,
    },

    "required_next_steps": [
        "Controlled Summary/Description feature materialization",
        "Feature materialization validation",
        "Leakage-sensitive modeling split",
        "Baseline model",
        "Advanced candidate comparison",
        "Error analysis",
        "Candidate model selection",
        "Task-specific calibration under T9",
    ],

    "downstream": {
        "t8_evidence_fusion": "PENDING",
        "t9_calibration": "PENDING",
        "t10_review_automation_policy": "PENDING",
        "t11_feedback": "PENDING",
    },

    "integrity": {
        "raw_mozilla_source_modified": False,
        "rn136_modified": False,
        "t2_target_artifact_modified": False,
        "labels_modified": False,
        "target_reconstructed_during_modeling": False,
        "fabricated_labels": False,
        "silent_feature_substitution": False,
    },
}


def main():
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            CONTRACT,
            handle,
            indent=2,
            ensure_ascii=False,
        )

    print("T2_MODEL_CONTRACT_RECONCILED")
    print(f"OUTPUT={OUTPUT_PATH}")
    print("TASK=T2")
    print("TASK_NAME=Priority Prediction")
    print("DATASET=Mozilla CORE")
    print("TARGET=target_priority")
    print("TARGET_SEMANTIC_NAME=priority")
    print("CLASSES=5")
    print("ELIGIBLE_RECORDS=29498")
    print("PREDICTION_BOUNDARY=Creation")
    print("HORIZON_HOURS=24")
    print("ADMITTED_FEATURES=Summary,Description")
    print("SUMMARY_RECORDS=29498")
    print("DESCRIPTION_RECORDS=27906")
    print("DESCRIPTION_MISSING=1592")
    print("RN136_FEATURES_AVAILABLE=0")
    print("RN136_FEATURE_SUBSTITUTION=False")
    print("CURRENT_STATE_BACKFILL_FORBIDDEN=True")
    print("FUTURE_INFORMATION_FORBIDDEN=True")
    print("TARGET_DERIVED_FEATURES_FORBIDDEN=True")
    print("FEATURE_MATERIALIZATION_REQUIRED=True")
    print("MODEL_SELECTED=False")
    print("TRAINING_STARTED=False")
    print("STATUS=READY_FOR_CONTROLLED_MODELING")
    print("CONTRACT_STATUS=RECONCILED")


if __name__ == "__main__":
    main()