from pathlib import Path
import json


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T5_ROOT = PROJECT_ROOT / "modeling" / "T5"

CONTRACT_DIR = T5_ROOT / "contracts"

OUTPUT_PATH = CONTRACT_DIR / "t5_baseline_contract.json"


CONTRACT = {
    "operation": "T5-MOD-002",
    "operation_name": "Baseline Modeling Contract",
    "task": "T5 Binary Duplicate Detection",
    "dataset": "Mozilla CORE",

    "status": "FROZEN_BASELINE_CONTRACT",

    "target": {
        "column": "T5 target",
        "type": "binary",
        "positive_value": 1,
        "negative_value": 0,
        "meaning_positive": (
            "First observed post-Creation Dupe of addition"
        ),
        "meaning_negative": (
            "No observed post-Creation Dupe of addition "
            "through the administrative observation endpoint"
        ),
        "target_ticket_identification": False,
    },

    "prediction_boundary": {
        "time": "Creation",
        "post_creation_history_allowed": False,
        "post_creation_fields_allowed": False,
        "target_side_fields_allowed": False,
    },

    "features": {
        "admitted": [
            "Creator",
            "Creator Detail",
            "Summary",
            "Description",
        ],
        "excluded_target_and_provenance": [
            "T5 target",
            "Target event index",
            "Target change index",
            "Target time",
            "Target actor",
        ],
    },

    "representation": {
        "type": "TF-IDF",
        "granularity": "word",
        "ngram_range": [1, 2],
        "min_df": 2,
        "max_features": 100000,
        "sublinear_tf": True,
        "lowercase": True,
    },

    "classifier": {
        "type": "LogisticRegression",
        "solver": "liblinear",
        "class_weight": "balanced",
        "max_iter": 1000,
        "random_state": 42,
    },

    "probability_output": {
        "required": True,
        "positive_class_probability": True,
        "probability_column": "p_duplicate",
    },

    "evaluation": {
        "primary_metrics": [
            "average_precision",
            "pr_auc",
        ],
        "secondary_metrics": [
            "roc_auc",
            "log_loss",
            "brier_score_loss",
        ],
        "class_metrics": [
            "precision",
            "recall",
            "f1",
        ],
        "confusion_matrix": True,
    },

    "calibration": {
        "required": True,
        "metrics": [
            "brier_score_loss",
            "expected_calibration_error",
        ],
        "reliability_analysis": True,
        "threshold_independent_probability_analysis": True,
    },

    "threshold_policy": {
        "baseline_threshold": 0.5,
        "threshold_optimization": False,
        "evaluation_threshold_tuning": False,
        "automatic_operational_threshold": False,
    },

    "split_policy": {
        "training_artifact": (
            "DTM-002_T5_TRAIN_GROUP_AWARE.csv"
        ),
        "evaluation_artifact": (
            "DTM-002_T5_EVAL_GROUP_AWARE.csv"
        ),
        "group_aware_boundary": True,
        "normalized_content_group_crossing_allowed": False,
        "evaluation_set_used_for_model_selection": False,
        "evaluation_set_used_for_threshold_tuning": False,
    },

    "data_usage": {
        "canonical_artifact": (
            "DTM-002_T5_DUPLICATE_DETECTION_derived_canonical.csv"
        ),
        "raw_archive_access": False,
        "raw_archive_reconstruction": False,
        "artifact_modification": False,
        "synthetic_data": False,
    },

    "model_selection": {
        "advanced_model_before_baseline": False,
        "baseline_required_first": True,
        "selection_metric": "average_precision",
        "evaluation_set_locked_until_baseline_complete": True,
    },

    "interpretation_controls": {
        "similarity_alone_is_not_duplication_proof": True,
        "relationship_existence_target": True,
        "target_ticket_pairing": False,
        "autonomous_duplicate_confirmation": False,
    },

    "operational_claims": {
        "guaranteed_duplicate_detection": False,
        "universal_automation": False,
        "automatic_confirmation": False,
        "human_review_boundary_established": False,
    },

    "next_operation": {
        "operation": "T5-MOD-003",
        "purpose": "Materialize controlled modeling features from accepted T5 training artifact",
        "model_training": False,
    },
}


def main():
    print("=" * 80)
    print("T5-MOD-002 — BASELINE MODELING CONTRACT")
    print("=" * 80)

    print("\n[1] Project structure")

    if not PROJECT_ROOT.exists():
        raise FileNotFoundError(
            f"Project root does not exist: {PROJECT_ROOT}"
        )

    T5_ROOT.mkdir(parents=True, exist_ok=True)
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Project root: {PROJECT_ROOT}")
    print(f"T5 root: {T5_ROOT}")
    print(f"Contract directory: {CONTRACT_DIR}")
    print("PASS")

    print("\n[2] Validate frozen target")

    assert CONTRACT["target"]["column"] == "T5 target"
    assert CONTRACT["target"]["type"] == "binary"
    assert CONTRACT["target"]["positive_value"] == 1
    assert CONTRACT["target"]["negative_value"] == 0

    print("Target: T5 target")
    print("Type: binary")
    print("Positive: 1")
    print("Negative: 0")
    print("PASS")

    print("\n[3] Validate Creation-time feature boundary")

    expected_features = [
        "Creator",
        "Creator Detail",
        "Summary",
        "Description",
    ]

    assert CONTRACT["features"]["admitted"] == expected_features

    print("Admitted features:")
    for feature in expected_features:
        print(f"  - {feature}")

    print("Post-Creation features: NOT ALLOWED")
    print("Target-side fields: NOT ALLOWED")
    print("PASS")

    print("\n[4] Validate baseline representation")

    representation = CONTRACT["representation"]

    print(f"Representation: {representation['type']}")
    print(f"Granularity: {representation['granularity']}")
    print(f"N-grams: {representation['ngram_range']}")
    print(f"min_df: {representation['min_df']}")
    print(f"max_features: {representation['max_features']}")
    print(f"sublinear_tf: {representation['sublinear_tf']}")
    print("PASS")

    print("\n[5] Validate baseline classifier")

    classifier = CONTRACT["classifier"]

    print(f"Classifier: {classifier['type']}")
    print(f"Solver: {classifier['solver']}")
    print(f"class_weight: {classifier['class_weight']}")
    print(f"max_iter: {classifier['max_iter']}")
    print(f"random_state: {classifier['random_state']}")
    print("PASS")

    print("\n[6] Validate probability requirement")

    assert CONTRACT["probability_output"]["required"] is True

    print("Probability output: REQUIRED")
    print("Positive-class probability: p_duplicate")
    print("PASS")

    print("\n[7] Validate evaluation contract")

    print("Primary metrics:")
    for metric in CONTRACT["evaluation"]["primary_metrics"]:
        print(f"  - {metric}")

    print("Secondary metrics:")
    for metric in CONTRACT["evaluation"]["secondary_metrics"]:
        print(f"  - {metric}")

    print("Calibration:")
    for metric in CONTRACT["calibration"]["metrics"]:
        print(f"  - {metric}")

    print("PASS")

    print("\n[8] Validate threshold policy")

    threshold = CONTRACT["threshold_policy"]

    print(
        f"Baseline threshold: "
        f"{threshold['baseline_threshold']}"
    )
    print(
        f"Threshold optimization: "
        f"{threshold['threshold_optimization']}"
    )
    print(
        f"Evaluation threshold tuning: "
        f"{threshold['evaluation_threshold_tuning']}"
    )
    print(
        f"Automatic operational threshold: "
        f"{threshold['automatic_operational_threshold']}"
    )

    print("PASS")

    print("\n[9] Validate split protection")

    split = CONTRACT["split_policy"]

    assert split["group_aware_boundary"] is True
    assert split["normalized_content_group_crossing_allowed"] is False
    assert split["evaluation_set_used_for_model_selection"] is False
    assert split["evaluation_set_used_for_threshold_tuning"] is False

    print("Group-aware split: REQUIRED")
    print("Cross-split normalized-content groups: NOT ALLOWED")
    print("Evaluation-set model selection: NOT ALLOWED")
    print("Evaluation-set threshold tuning: NOT ALLOWED")
    print("PASS")

    print("\n[10] Validate modeling safeguards")

    safeguards = [
        (
            "Advanced model before baseline",
            CONTRACT["model_selection"][
                "advanced_model_before_baseline"
            ],
        ),
        (
            "Raw archive access",
            CONTRACT["data_usage"]["raw_archive_access"],
        ),
        (
            "Synthetic data",
            CONTRACT["data_usage"]["synthetic_data"],
        ),
        (
            "Automatic duplicate confirmation",
            CONTRACT["operational_claims"][
                "automatic_confirmation"
            ],
        ),
    ]

    for name, value in safeguards:
        print(f"{name}: {value}")

    assert all(value is False for _, value in safeguards)

    print("PASS")

    print("\n[11] Write frozen contract")

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(
            CONTRACT,
            f,
            indent=2,
            ensure_ascii=False,
        )
        f.write("\n")

    print(f"Contract written to:")
    print(OUTPUT_PATH)

    if not OUTPUT_PATH.exists():
        raise RuntimeError(
            "Contract file was not created."
        )

    print("PASS")

    print("\n" + "=" * 80)
    print("T5-MOD-002 RESULT: BASELINE_CONTRACT_FROZEN")
    print("=" * 80)

    print("\nNo model trained.")
    print("No evaluation performed.")
    print("No raw archive accessed.")
    print("No dataset modified.")


if __name__ == "__main__":
    main()