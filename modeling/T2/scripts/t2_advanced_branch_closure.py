from pathlib import Path
import json


# ============================================================
# T2-MOD-018
# Advanced Model Branch Closure
#
# Documentation/closure operation only.
# No training.
# No dataset modification.
# No test-set access.
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_ROOT = PROJECT_ROOT / "modeling" / "T2"

OUTPUT_DIR = T2_ROOT / "analysis"

OUTPUT_FILE = (
    OUTPUT_DIR
    / "t2_advanced_branch_closure.json"
)


def main():
    print("T2_MOD_018_START")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = {
        "operation": "T2-MOD-018",
        "operation_name": (
            "Advanced Model Branch Closure"
        ),

        "task": "T2",
        "dataset": "Mozilla CORE",
        "target": "target_priority",

        "advanced_candidate": {
            "architecture": "DistilBERT",
            "model_identifier": (
                "distilbert-base-uncased"
            ),
            "candidate_selected": True,
            "training_started": False,
            "trained_model_exists": False,
        },

        "branch_decision": {
            "advanced_training_executed": False,
            "reason": (
                "The additional dependency and "
                "resource cost of transformer "
                "experimentation was not justified "
                "for the current working-model "
                "objective."
            ),
            "transformer_dependencies": (
                "not installed"
            ),
            "existing_project_environment": (
                "preserved"
            ),
        },

        "retained_models": [
            {
                "operation": "T2-MOD-006",
                "model": (
                    "TF-IDF + Logistic Regression"
                ),
                "validation_accuracy": 0.470282,
                "validation_macro_f1": 0.269346,
                "validation_weighted_f1": 0.448665,
            },
            {
                "operation": "T2-MOD-007",
                "model": (
                    "TF-IDF + Class-Weighted "
                    "Logistic Regression"
                ),
                "validation_accuracy": 0.446102,
                "validation_macro_f1": 0.310450,
                "validation_weighted_f1": 0.443565,
            },
            {
                "operation": "T2-MOD-008",
                "model": (
                    "TF-IDF + Linear SVM"
                ),
                "validation_accuracy": 0.449040,
                "validation_macro_f1": 0.268347,
                "validation_weighted_f1": 0.435913,
            },
            {
                "operation": "T2-MOD-010",
                "model": (
                    "TF-IDF + Class-Weighted "
                    "Linear SVM"
                ),
                "validation_accuracy": 0.443390,
                "validation_macro_f1": 0.291273,
                "validation_weighted_f1": 0.435755,
            },
        ],

        "evaluation_state": {
            "validation_comparison_complete": True,
            "test_evaluation_completed": False,
            "test_set_locked": True,
            "final_model_selected": False,
        },

        "important_limitation": (
            "No transformer performance claim is made. "
            "DistilBERT was a selected candidate only "
            "and was never trained or evaluated."
        ),

        "dataset_integrity": {
            "dataset_modified": False,
            "target_modified": False,
            "split_modified": False,
        },

        "status": (
            "ADVANCED_MODEL_BRANCH_CLOSED"
        ),
    }

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            report,
            f,
            indent=2,
        )

    print("T2_MOD_018_COMPLETE")

    print(
        "DISTILBERT_SELECTED=True"
    )

    print(
        "DISTILBERT_TRAINED=False"
    )

    print(
        "TRANSFORMER_DEPENDENCIES_INSTALLED=False"
    )

    print(
        "RETAINED_MODELS=4"
    )

    print(
        "VALIDATION_COMPARISON_COMPLETE=True"
    )

    print(
        "TEST_EVALUATED=False"
    )

    print(
        "FINAL_MODEL_SELECTED=False"
    )

    print(
        "TEST_LOCKED=True"
    )

    print(
        "DATASET_MODIFIED=False"
    )

    print(
        "STATUS="
        "ADVANCED_MODEL_BRANCH_CLOSED"
    )

    print(
        f"OUTPUT={OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()