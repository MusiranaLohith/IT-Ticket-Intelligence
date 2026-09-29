from pathlib import Path
import json


# ============================================================
# T2-MOD-019
# Final Model Selection
#
# Validation-based selection only.
# No training.
# No test-set access.
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_ROOT = PROJECT_ROOT / "modeling" / "T2"

OUTPUT_DIR = T2_ROOT / "analysis"

OUTPUT_FILE = (
    OUTPUT_DIR
    / "t2_final_model_selection.json"
)


def main():
    print("T2_MOD_019_START")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Completed validation results
    # --------------------------------------------------------

    models = [
        {
            "operation": "T2-MOD-006",
            "model": (
                "TF-IDF + Logistic Regression"
            ),
            "accuracy": 0.470282,
            "macro_f1": 0.269346,
            "weighted_f1": 0.448665,
            "p4_f1": 0.000000,
            "p5_f1": 0.028169,
        },
        {
            "operation": "T2-MOD-007",
            "model": (
                "TF-IDF + Class-Weighted "
                "Logistic Regression"
            ),
            "accuracy": 0.446102,
            "macro_f1": 0.310450,
            "weighted_f1": 0.443565,
            "p4_f1": 0.107143,
            "p5_f1": 0.139037,
        },
        {
            "operation": "T2-MOD-008",
            "model": (
                "TF-IDF + Linear SVM"
            ),
            "accuracy": 0.449040,
            "macro_f1": 0.268347,
            "weighted_f1": 0.435913,
            "p4_f1": 0.000000,
            "p5_f1": 0.063348,
        },
        {
            "operation": "T2-MOD-010",
            "model": (
                "TF-IDF + Class-Weighted "
                "Linear SVM"
            ),
            "accuracy": 0.443390,
            "macro_f1": 0.291273,
            "weighted_f1": 0.435755,
            "p4_f1": 0.090909,
            "p5_f1": 0.087273,
        },
    ]

    # --------------------------------------------------------
    # Selection decision
    #
    # T2 is an imbalanced five-class priority task.
    # Macro-F1 is therefore given priority over raw accuracy,
    # while minority-class performance is explicitly considered.
    # --------------------------------------------------------

    selected_operation = "T2-MOD-007"

    selected_model = next(
        item
        for item in models
        if item["operation"] == selected_operation
    )

    selection_reasons = [
        (
            "Highest validation macro-F1 among "
            "all completed T2 baseline models."
        ),
        (
            "Best observed validation P4 F1 "
            "among the completed models."
        ),
        (
            "Best observed validation P5 F1 "
            "among the completed models."
        ),
        (
            "Class weighting improves minority-class "
            "recognition relative to the unweighted "
            "Logistic Regression baseline."
        ),
        (
            "Selection avoids choosing solely by "
            "accuracy in the presence of substantial "
            "class imbalance."
        ),
    ]

    non_selected = [
        {
            "operation": item["operation"],
            "model": item["model"],
            "reason": (
                "Not selected for final locked test "
                "evaluation because it did not provide "
                "the strongest overall macro-F1/minority-"
                "class validation profile."
            ),
        }
        for item in models
        if item["operation"] != selected_operation
    ]

    report = {
        "operation": "T2-MOD-019",
        "operation_name": (
            "Final Model Selection"
        ),

        "task": "T2",
        "task_name": "Priority Prediction",
        "dataset": "Mozilla CORE",

        "selection_basis": {
            "partition": "validation",
            "test_used": False,
            "test_locked": True,
            "primary_selection_metric": "macro_f1",
            "secondary_considerations": [
                "P4 F1",
                "P5 F1",
                "accuracy",
                "weighted F1",
            ],
        },

        "selected_model": selected_model,

        "selection_reasons": selection_reasons,

        "all_validation_results": models,

        "non_selected_models": non_selected,

        "test_evaluation": {
            "completed": False,
            "test_loaded": False,
        },

        "training": {
            "new_training_performed": False,
        },

        "final_model_status": {
            "selected": True,
            "operation": selected_operation,
            "ready_for_locked_test_evaluation": True,
        },

        "status": (
            "FINAL_MODEL_SELECTED"
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

    # --------------------------------------------------------
    # Console output
    # --------------------------------------------------------

    print(
        "SELECTED_OPERATION="
        f"{selected_operation}"
    )

    print(
        "SELECTED_MODEL="
        f"{selected_model['model']}"
    )

    print(
        "VALIDATION_ACCURACY="
        f"{selected_model['accuracy']}"
    )

    print(
        "VALIDATION_MACRO_F1="
        f"{selected_model['macro_f1']}"
    )

    print(
        "VALIDATION_WEIGHTED_F1="
        f"{selected_model['weighted_f1']}"
    )

    print(
        "VALIDATION_P4_F1="
        f"{selected_model['p4_f1']}"
    )

    print(
        "VALIDATION_P5_F1="
        f"{selected_model['p5_f1']}"
    )

    print(
        "SELECTION_METRIC=MACRO_F1"
    )

    print(
        "TEST_USED=False"
    )

    print(
        "TEST_LOCKED=True"
    )

    print(
        "NEW_TRAINING=False"
    )

    print(
        "FINAL_MODEL_SELECTED=True"
    )

    print(
        "READY_FOR_LOCKED_TEST=True"
    )

    print(
        f"OUTPUT={OUTPUT_FILE}"
    )

    print(
        "STATUS=FINAL_MODEL_SELECTED"
    )

    print("T2_MOD_019_COMPLETE")


if __name__ == "__main__":
    main()