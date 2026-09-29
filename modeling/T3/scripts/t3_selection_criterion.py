from pathlib import Path
import json


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

CONTRACT_DIR = PROJECT_ROOT / "modeling" / "T3" / "contracts"
OUTPUT_PATH = CONTRACT_DIR / "t3_model_selection_criterion.json"

LABELS = ["S1", "S2", "S3", "S4"]


def main():
    print("T3_MOD_014_START")

    criterion = {
        "task": "T3_SEVERITY_PREDICTION",
        "evaluation_stage": "VALIDATION_ONLY",
        "primary_metric": "macro_f1",
        "secondary_metrics": [
            "accuracy",
            "weighted_f1",
        ],
        "per_class_metrics": {
            "required": True,
            "labels": LABELS,
            "metrics": [
                "precision",
                "recall",
                "f1",
                "support",
            ],
        },
        "selection_principles": [
            "Prioritize balanced four-class performance.",
            "Inspect minority-class S1/S2/S4 behavior.",
            "Retain accuracy and weighted F1 as secondary measures.",
            "Do not select solely on accuracy.",
            "Do not use locked test results for candidate selection.",
            "Interpret S1 results cautiously because validation support is only 20.",
            "Do not impose an unsupported numerical acceptance threshold.",
        ],
        "test_policy": {
            "candidate_selection_uses_test": False,
            "final_test_locked_until_candidate_freeze": True,
        },
        "status": "FROZEN_FOR_T3_CANDIDATE_SELECTION",
    }

    CONTRACT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            criterion,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("PRIMARY_METRIC=macro_f1")
    print("SECONDARY_METRICS=accuracy,weighted_f1")
    print("PER_CLASS_ANALYSIS_REQUIRED=True")
    print("S1_VALIDATION_SUPPORT=20")
    print("TEST_USED=False")
    print(f"OUTPUT={OUTPUT_PATH}")
    print("STATUS=SELECTION_CRITERION_FROZEN")
    print("T3_MOD_014_COMPLETE")


if __name__ == "__main__":
    main()