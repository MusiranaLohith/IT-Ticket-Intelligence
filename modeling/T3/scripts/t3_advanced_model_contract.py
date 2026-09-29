from pathlib import Path
import json


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T3"
    / "contracts"
    / "t3_advanced_model_contract.json"
)


def main():
    print("T3_MOD_019_START")

    contract = {
        "task": "T3_SEVERITY_PREDICTION",
        "operation": "T3-MOD-019",

        "advanced_branch_status": "JUSTIFIED",

        "candidate_model": {
            "primary": "DistilBERT",
            "alternatives": [
                "MiniLM",
                "BERT"
            ],
            "selection_status": "PRIMARY_CANDIDATE_DEFINED",
            "reason": (
                "Use a pretrained transformer encoder to test whether "
                "contextual language representations improve severity "
                "separation beyond classical TF-IDF models."
            ),
        },

        "data_contract": {
            "dataset": "Mozilla_CORE",
            "supervised_population": 30839,
            "target": "target_severity",
            "target_labels": [
                "S1",
                "S2",
                "S3",
                "S4"
            ],
            "prediction_boundary": "Creation",
            "features": [
                "Summary",
                "Description"
            ],
            "feature_rule": (
                "Only Creation-time Summary and Description may be "
                "provided to the model."
            ),
        },

        "split_contract": {
            "train_rows": 21587,
            "validation_rows": 4626,
            "test_rows": 4626,
            "split_type": "chronological",
            "ordering": "Creation time with deterministic ID tie-break",
            "test_status": "LOCKED",
        },

        "training_contract": {
            "pretrained_model": True,
            "fine_tuning": True,
            "training_from_scratch": False,
            "class_weighting": False,
            "data_augmentation": False,
            "feature_engineering": False,
            "post_creation_features": False,
            "target_derived_features": False,
        },

        "evaluation_contract": {
            "primary_metric": "macro_f1",
            "secondary_metrics": [
                "accuracy",
                "weighted_f1"
            ],
            "per_class_metrics_required": True,
            "labels": [
                "S1",
                "S2",
                "S3",
                "S4"
            ],
            "s1_support_caution": True,
            "test_use_for_candidate_selection": False,
        },

        "comparison_contract": {
            "classical_reference": "T3-MOD-008",
            "comparison_basis": (
                "Validation macro F1 under the frozen chronological "
                "evaluation design."
            ),
            "no_unsupported_acceptance_threshold": True,
        },

        "environment_contract": {
            "python": "3.14.7",
            "cuda_available": False,
            "transformers_installed": False,
            "pytorch_installed": False,
            "tokenizers_installed": False,
            "datasets_installed": False,
            "installation_status": "NOT_STARTED",
            "installation_must_be_verified_before_training": True,
        },

        "resource_constraints": {
            "gpu": False,
            "large_dependency_installation": (
                "Requires explicit environment verification before proceeding."
            ),
            "training_resource_assessment_required": True,
            "fallback": (
                "If the primary advanced model cannot be executed "
                "reliably in the available environment, record the "
                "advanced branch as operationally infeasible rather "
                "than silently substituting another methodology."
            ),
        },

        "forbidden": [
            "Locked test access before final candidate selection",
            "Post-Creation information",
            "Current mutable fields",
            "Target-derived features",
            "Raw Mozilla archive rescanning",
            "Dataset modification",
            "Training from scratch",
            "Unsupported acceptance threshold",
            "Claiming improvement before measurement",
        ],

        "status": "ADVANCED_EXPERIMENT_CONTRACT_FROZEN",
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_PATH.write_text(
        json.dumps(contract, indent=2),
        encoding="utf-8",
    )

    print("TASK=T3_SEVERITY_PREDICTION")
    print("ADVANCED_BRANCH_STATUS=JUSTIFIED")
    print("PRIMARY_MODEL=DistilBERT")
    print("ALTERNATIVES=MiniLM,BERT")
    print("SUPERVISED_POPULATION=30839")
    print("FEATURES=Summary,Description")
    print("BOUNDARY=Creation")
    print("TRAIN_ROWS=21587")
    print("VALIDATION_ROWS=4626")
    print("TEST_ROWS=4626")
    print("TEST_LOCKED=True")
    print("PRIMARY_METRIC=macro_f1")
    print("PYTHON=3.14.7")
    print("CUDA_AVAILABLE=False")
    print("TRANSFORMERS_INSTALLED=False")
    print("PYTORCH_INSTALLED=False")
    print("INSTALLATION_STARTED=False")
    print("TRAINING_STARTED=False")
    print("TEST_USED=False")
    print("RAW_MOZILLA_ACCESSED=False")
    print("DATASET_MODIFIED=False")
    print(f"OUTPUT={OUTPUT_PATH}")
    print("STATUS=ADVANCED_EXPERIMENT_CONTRACT_FROZEN")
    print("T3_MOD_019_COMPLETE")


if __name__ == "__main__":
    main()