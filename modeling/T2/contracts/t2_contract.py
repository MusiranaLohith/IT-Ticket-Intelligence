from pathlib import Path
import json


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T2"
    / "contracts"
    / "t2_contract.json"
)


CONTRACT = {
    "operation": "T2-MOD-001",
    "task": "T2",
    "task_name": "Priority Prediction",
    "status": "SUPPORTED",
    "contract_status": "ACCEPTED",

    "dataset": {
        "name": "Mozilla CORE",
        "role": "PRIMARY_T2_DATASET",
        "eligible_records": 29498,
        "source_contract_status": "ACCEPTED",
        "dtm_status": "COMPLETED_CLOSED",
    },

    "objective": {
        "statement": (
            "Predict the first valid P1-P5 priority assigned "
            "strictly after Creation and within the following "
            "24-hour observation window."
        ),
        "prediction_boundary": "Creation",
        "prediction_unit": "ticket",
        "task_type": "multiclass_classification",
    },

    "target": {
        "field": "priority",
        "semantic_definition": (
            "First valid priority in the P1-P5 vocabulary "
            "assigned strictly after Creation and within "
            "24 hours."
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
    },

    "prediction_boundary": {
        "event": "Creation",
        "allowed_information": (
            "Information demonstrably available at or before "
            "the Creation boundary."
        ),
        "future_information_forbidden": True,
        "post_creation_information_forbidden": True,
        "future_target_information_forbidden": True,
    },

    "historical_feature_basis": {
        "source": "RN136",
        "status": "FROZEN_ACCEPTED",
        "fields": [
            "Product",
            "Component",
            "Priority",
            "Status",
            "Keywords",
            "Blocks",
            "CC",
        ],
        "availability_indicators": [
            "Product_available",
            "Component_available",
            "Priority_available",
            "Status_available",
            "Keywords_available",
            "Blocks_available",
            "CC_available",
        ],
        "historical_only": True,
        "current_state_backfill_forbidden": True,
        "final_state_backfill_forbidden": True,
        "future_state_backfill_forbidden": True,
        "feature_substitution_without_contract_change": False,
    },

    "feature_constraints": {
        "allowed": [
            "Accepted RN136 historical fields and their "
            "availability indicators, subject to actual "
            "historical availability at Creation."
        ],
        "forbidden": [
            "Future priority",
            "Post-Creation priority changes",
            "Current/final priority backfill",
            "Post-Creation status",
            "Post-Creation workflow information",
            "Future events",
            "Target-derived features",
            "Information unavailable at Creation",
            "Unapproved feature substitution",
            "Summary",
            "Description",
            "Severity",
        ],
    },

    "known_feature_availability": {
        "t2_population_records": 29498,
        "historical_feature_availability_indicators_all_zero": True,
        "interpretation": (
            "The accepted T2 population has no populated historical "
            "values for the seven RN136 historical feature fields. "
            "This is an evidence finding and must not be repaired "
            "through current-state or final-state backfill."
        ),
    },

    "split_policy": {
        "required": True,
        "strategy": (
            "A leakage-safe modeling split must be established "
            "using only information permitted by this contract."
        ),
        "evaluation_data_must_not_be_used_for_fit": True,
        "target_distribution_must_be_reported": True,
        "temporal_boundary_must_be_respected": True,
        "future_information_must_not_cross_split": True,
    },

    "modeling_policy": {
        "baseline_required_before_advanced_model": True,
        "model_selected": False,
        "training_started": False,
        "advanced_model_preselected": False,
        "evaluation_used_for_training": False,
    },

    "data_integrity": {
        "raw_source_immutable": True,
        "raw_source_modified": False,
        "labels_modified": False,
        "historical_values_backfilled": False,
        "silent_merge_forbidden": True,
        "fabricated_labels_forbidden": True,
    },

    "downstream": {
        "t8_evidence_fusion": "PENDING",
        "t9_calibration": "PENDING",
        "t10_review_automation_policy": "PENDING",
        "t11_feedback": "PENDING",
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

    print("T2_CONTRACT_CREATED")
    print(f"OUTPUT={OUTPUT_PATH}")
    print("TASK=T2")
    print("TASK_NAME=Priority Prediction")
    print("DATASET=Mozilla CORE")
    print("TARGET=priority")
    print("CLASSES=5")
    print("ELIGIBLE_RECORDS=29498")
    print("PREDICTION_BOUNDARY=Creation")
    print("HISTORICAL_FEATURE_SOURCE=RN136")
    print("HISTORICAL_FEATURE_AVAILABILITY_ALL_ZERO=True")
    print("CURRENT_STATE_BACKFILL_FORBIDDEN=True")
    print("FINAL_STATE_BACKFILL_FORBIDDEN=True")
    print("MODEL_SELECTED=False")
    print("TRAINING_STARTED=False")
    print("RAW_SOURCE_MODIFIED=False")
    print("STATUS=SUPPORTED")
    print("CONTRACT_STATUS=ACCEPTED")


if __name__ == "__main__":
    main()