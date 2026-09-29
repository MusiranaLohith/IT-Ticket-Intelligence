import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT = PROJECT_ROOT / "modeling" / "contracts" / "t1_contract.json"


contract = {
    "contract_id": "T1-IT-SUPPORT-v1",
    "task": "Incoming IT-ticket classification",
    "dataset": "IT Support",
    "dtm": "DTM-003",
    "status": "SUPPORTED",

    "source": {
        "artifact": "7384758.zip",
        "raw_data_immutable": True
    },

    "target": {
        "field": "category_truth",
        "type": "multiclass",
        "classes": [
            "Fileservice",
            "Support general",
            "Software",
            "O365",
            "Active Directory",
            "Computer-Services",
            "EOL"
        ]
    },

    "features": {
        "allowed": ["text"],
        "forbidden": ["id", "category_truth"]
    },

    "prediction_boundary": {
        "input": "incoming ticket text",
        "future_information_forbidden": True,
        "temporal_split_claim": False
    },

    "text_policy": {
        "repeated_text_is_not_duplicate_ground_truth": True,
        "exact_text_overlap_requires_control": True,
        "normalization_must_be_versioned": True
    },

    "split_policy": {
        "split_before_model_fitting": True,
        "normalized_text_grouping": True,
        "identical_normalized_text_must_not_cross_evaluation_boundary": True
    },

    "evaluation": {
        "metrics": [
            "accuracy",
            "macro_f1",
            "weighted_f1",
            "per_class_precision",
            "per_class_recall",
            "per_class_f1",
            "confusion_matrix"
        ]
    },

    "model_policy": {
        "model_selected": False,
        "training_started": False,
        "baseline_required_first": True
    },

    "historical_reference": {
        "supplier_accuracy": 0.79,
        "independent_accuracy": 0.779300,
        "gap_percentage_points": 1.07,
        "discrepancy_cause": "UNRESOLVED",
        "supplied_model_must_not_be_overwritten": True
    },

    "created_utc": datetime.now(timezone.utc).isoformat()
}


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)

    with OUT.open("w", encoding="utf-8") as f:
        json.dump(contract, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("T1_CONTRACT_CREATED")
    print(f"OUTPUT={OUT}")
    print(f"TARGET={contract['target']['field']}")
    print(f"CLASSES={len(contract['target']['classes'])}")
    print("MODEL_SELECTED=False")
    print("TRAINING_STARTED=False")
    print("STATUS=SUPPORTED")


if __name__ == "__main__":
    main()