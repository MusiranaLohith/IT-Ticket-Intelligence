from pathlib import Path
import json


# ============================================================
# T2-MOD-012
# Advanced NLP Model Contract
#
# Contract only.
# No training.
# No test-set access.
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_ROOT = PROJECT_ROOT / "modeling" / "T2"

OUTPUT_DIR = T2_ROOT / "contracts"

OUTPUT_FILE = (
    OUTPUT_DIR
    / "t2_advanced_model_contract.json"
)


def main():
    print("T2_MOD_012_START")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    contract = {
        "operation": "T2-MOD-012",
        "operation_name": (
            "Advanced NLP Model Contract"
        ),

        "task": "T2",
        "task_name": "Priority Prediction",
        "dataset": "Mozilla CORE",

        "target": {
            "physical_field": "target_priority",
            "semantic_name": "priority",
            "classes": [
                "P1",
                "P2",
                "P3",
                "P4",
                "P5",
            ],
            "eligible_records": 29498,
        },

        "prediction_boundary": {
            "event": "Creation",
            "future_information_forbidden": True,
            "target_derived_features_forbidden": True,
        },

        "admitted_features": {
            "sources": [
                "Summary",
                "Description",
            ],
            "summary_coverage": {
                "records": 29498,
                "percentage": 100.0,
            },
            "description_coverage": {
                "records": 27906,
                "percentage": 94.60,
            },
            "description_missing": {
                "records": 1592,
                "percentage": 5.40,
            },
            "missingness_policy": (
                "Description unavailable at Creation "
                "is retained as missing; no information "
                "is fabricated."
            ),
        },

        "frozen_split": {
            "method": "chronological",
            "ordering_key": [
                "Creation time",
                "ID",
            ],
            "random_shuffling": False,
            "stratification": False,
            "train_records": 20648,
            "validation_records": 4425,
            "test_records": 4425,
            "test_locked": True,
        },

        "baseline_reference": {
            "experiments": [
                "T2-MOD-006",
                "T2-MOD-007",
                "T2-MOD-008",
                "T2-MOD-010",
            ],
            "best_accuracy_operation": (
                "T2-MOD-006"
            ),
            "best_accuracy": 0.470282,
            "best_macro_f1_operation": (
                "T2-MOD-007"
            ),
            "best_macro_f1": 0.310450,
            "best_weighted_f1": 0.448665,
            "best_p4_f1": 0.107143,
            "best_p5_f1": 0.139037,
        },

        "advanced_model_family": {
            "family": (
                "pretrained transformer-based "
                "text classification"
            ),
            "architecture_selected": False,
            "candidate_selection_required": True,
            "fine_tuning_allowed": True,
            "from_scratch_training": False,
        },

        "input_representation": {
            "primary_text": (
                "Summary + Description"
            ),
            "creation_time_text_only": True,
            "administrative_current_state_features": False,
            "post_creation_features": False,
            "target_derived_features": False,
        },

        "imbalance_policy": {
            "class_imbalance_must_be_addressed": True,
            "class_weighting_or_equivalent": (
                "permitted only as a controlled experiment"
            ),
            "oversampling": (
                "not automatically permitted; "
                "requires explicit experiment definition"
            ),
            "synthetic_label_generation": False,
        },

        "evaluation_policy": {
            "primary_metrics": [
                "macro_f1",
                "weighted_f1",
                "accuracy",
            ],
            "minority_class_metrics_required": [
                "P4 precision",
                "P4 recall",
                "P4 F1",
                "P5 precision",
                "P5 recall",
                "P5 F1",
            ],
            "confusion_matrix_required": True,
            "per_class_metrics_required": True,
            "test_evaluation_before_model_selection": False,
        },

        "comparison_policy": {
            "validation_partition_frozen": True,
            "baseline_comparison_required": True,
            "same_target_definition": True,
            "same_prediction_boundary": True,
            "same_temporal_split": True,
            "test_remains_locked": True,
        },

        "reproducibility": {
            "random_seed_required": True,
            "training_configuration_logged": True,
            "tokenizer_version_logged": True,
            "model_identifier_logged": True,
            "software_versions_logged": True,
            "hardware_environment_logged": True,
        },

        "resource_policy": {
            "hardware_constraint": (
                "Use available local compute; "
                "avoid unnecessarily large models."
            ),
            "memory_exhaustion_to_be_avoided": True,
            "training_must_be_reproducible": True,
        },

        "selection_policy": {
            "final_model_not_selected": True,
            "selection_based_on_validation": True,
            "test_used_only_for_final_locked_evaluation": True,
            "single_metric_selection_forbidden": True,
        },

        "forbidden": [
            "random re-splitting",
            "test-set tuning",
            "test-set model selection",
            "post-Creation administrative features",
            "current-state backfill",
            "future information",
            "target-derived features",
            "fabricated Description content",
            "synthetic labels",
            "silent dataset merging",
            "unlogged preprocessing changes",
        ],

        "status": (
            "READY_FOR_ADVANCED_MODEL_SELECTION"
        ),

        "contract_status": "FROZEN",
    }

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            contract,
            f,
            indent=2,
        )

    print("T2_MOD_012_COMPLETE")
    print(
        f"OUTPUT={OUTPUT_FILE}"
    )
    print("TASK=T2")
    print("TARGET=target_priority")
    print("CLASSES=5")
    print("ELIGIBLE_RECORDS=29498")
    print(
        "ADMITTED_FEATURES=Summary,Description"
    )
    print(
        "TRAIN=20648 "
        "VALIDATION=4425 "
        "TEST=4425"
    )
    print(
        "TEST_LOCKED=True"
    )
    print(
        "ADVANCED_MODEL_FAMILY="
        "PRETRAINED_TRANSFORMER_TEXT_CLASSIFICATION"
    )
    print(
        "ARCHITECTURE_SELECTED=False"
    )
    print(
        "STATUS=READY_FOR_ADVANCED_MODEL_SELECTION"
    )
    print(
        "CONTRACT_STATUS=FROZEN"
    )


if __name__ == "__main__":
    main()