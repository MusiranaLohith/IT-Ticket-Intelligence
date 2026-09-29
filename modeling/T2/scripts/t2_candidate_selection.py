from pathlib import Path
import json
import platform
import sys


# ============================================================
# T2-MOD-013
# Advanced Model Candidate Selection
#
# Selection only.
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
    / "t2_advanced_candidate_selection.json"
)


def detect_compute_environment():
    """
    Record the local execution environment without
    requiring GPU-specific packages.
    """

    cpu_count = 1

    try:
        import os
        cpu_count = os.cpu_count() or 1
    except Exception:
        pass

    gpu_available = False
    gpu_count = 0
    gpu_name = None

    try:
        import torch

        gpu_available = bool(
            torch.cuda.is_available()
        )

        if gpu_available:
            gpu_count = torch.cuda.device_count()

            if gpu_count > 0:
                gpu_name = torch.cuda.get_device_name(0)

    except Exception:
        # PyTorch may not yet be installed.
        # This does not invalidate candidate selection.
        pass

    return {
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "cpu_count": cpu_count,
        "gpu_available": gpu_available,
        "gpu_count": gpu_count,
        "gpu_name": gpu_name,
    }


def main():
    print("T2_MOD_013_START")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    compute = detect_compute_environment()

    # --------------------------------------------------------
    # Candidate decision
    # --------------------------------------------------------

    selected_candidate = {
        "model_family": (
            "pretrained transformer-based "
            "text classification"
        ),
        "model_identifier": (
            "distilbert-base-uncased"
        ),
        "architecture": "DistilBERT",
        "pretrained": True,
        "fine_tuning": True,
        "from_scratch_training": False,
        "selection_role": (
            "primary advanced-model candidate"
        ),
    }

    alternatives = [
        {
            "model_identifier": (
                "microsoft/MiniLM-L12-H384-uncased"
            ),
            "role": "lighter alternative",
            "status": "not_selected_for_first_test",
        },
        {
            "model_identifier": (
                "bert-base-uncased"
            ),
            "role": "larger conventional transformer baseline",
            "status": "not_selected_for_first_test",
        },
    ]

    selection_reasons = [
        (
            "Provides contextual language representations "
            "beyond sparse TF-IDF features."
        ),
        (
            "Appropriate for the Summary + Description "
            "text-only prediction boundary."
        ),
        (
            "Smaller and lighter than full BERT, making "
            "it a reasonable first local transformer "
            "experiment."
        ),
        (
            "Pretrained representation reduces the need "
            "for training a language model from scratch."
        ),
        (
            "Creates a meaningful controlled comparison "
            "against the completed TF-IDF baselines."
        ),
        (
            "The candidate is selected for experimentation, "
            "not declared the final T2 model."
        ),
    ]

    frozen_comparison_requirements = {
        "target": "target_priority",
        "classes": [
            "P1",
            "P2",
            "P3",
            "P4",
            "P5",
        ],
        "features": [
            "Summary",
            "Description",
        ],
        "prediction_boundary": "Creation",
        "train_records": 20648,
        "validation_records": 4425,
        "test_records": 4425,
        "split_method": "chronological",
        "test_used_for_selection": False,
        "test_used_for_tuning": False,
    }

    evaluation_requirements = {
        "primary_metrics": [
            "macro_f1",
            "weighted_f1",
            "accuracy",
        ],
        "minority_metrics": [
            "P4 precision",
            "P4 recall",
            "P4 F1",
            "P5 precision",
            "P5 recall",
            "P5 F1",
        ],
        "required_analysis": [
            "confusion matrix",
            "per-class metrics",
            "prediction distribution",
            "comparison against T2 baselines",
        ],
    }

    forbidden_changes = [
        "changing the frozen target",
        "changing the prediction boundary",
        "changing the chronological split",
        "using the test set for tuning",
        "using the test set for model selection",
        "adding post-Creation features",
        "adding current-state administrative fields",
        "using target-derived features",
        "fabricating missing Description text",
        "silently merging another dataset",
    ]

    contract = {
        "operation": "T2-MOD-013",
        "operation_name": (
            "Advanced Model Candidate Selection"
        ),
        "task": "T2",
        "task_name": "Priority Prediction",
        "dataset": "Mozilla CORE",

        "candidate_selection": {
            "selected": selected_candidate,
            "alternatives": alternatives,
            "selection_reasons": selection_reasons,
        },

        "compute_environment_at_selection": compute,

        "frozen_comparison_requirements": (
            frozen_comparison_requirements
        ),

        "evaluation_requirements": (
            evaluation_requirements
        ),

        "forbidden_changes": forbidden_changes,

        "baseline_reference": {
            "best_accuracy": {
                "operation": "T2-MOD-006",
                "value": 0.470282,
            },
            "best_macro_f1": {
                "operation": "T2-MOD-007",
                "value": 0.310450,
            },
            "best_weighted_f1": {
                "operation": "T2-MOD-006",
                "value": 0.448665,
            },
        },

        "training_status": {
            "training_started": False,
            "test_loaded": False,
            "final_model_selected": False,
        },

        "status": (
            "READY_FOR_CONTROLLED_TRANSFORMER_TRAINING"
        ),

        "selection_status": "FROZEN",
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

    print("T2_MOD_013_COMPLETE")
    print(
        f"OUTPUT={OUTPUT_FILE}"
    )

    print(
        "SELECTED_ARCHITECTURE=DistilBERT"
    )

    print(
        "MODEL_IDENTIFIER="
        "distilbert-base-uncased"
    )

    print(
        "MODEL_FAMILY="
        "PRETRAINED_TRANSFORMER_TEXT_CLASSIFICATION"
    )

    print(
        "TRAINING_STARTED=False"
    )

    print(
        "TEST_USED=False"
    )

    print(
        "FINAL_MODEL_SELECTED=False"
    )

    print(
        "STATUS="
        "READY_FOR_CONTROLLED_TRANSFORMER_TRAINING"
    )

    print(
        "SELECTION_STATUS=FROZEN"
    )


if __name__ == "__main__":
    main()