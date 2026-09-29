from pathlib import Path
import json
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_PATH = PROJECT_ROOT / "modeling" / "T4" / "derived" / "t4_features.csv"
TRAIN_PATH = PROJECT_ROOT / "modeling" / "T4" / "derived" / "t4_train.csv"
EVAL_PATH = PROJECT_ROOT / "modeling" / "T4" / "derived" / "t4_eval.csv"

OUTPUT_DIR = PROJECT_ROOT / "modeling" / "T4" / "contracts"
OUTPUT_PATH = OUTPUT_DIR / "t4_baseline_contract.json"


EXPECTED_FEATURES = [
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
]

TARGET_COLUMN = "target_assignee"

EXPECTED_MODELING_COLUMNS = [
    "ID",
    "Creation time",
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
    "target_assignee",
]

FORBIDDEN_TARGET_SIDE_COLUMNS = [
    "target_assignment_time",
    "target_event_index",
    "target_change_index",
    "Assigned to",
    "Assigned to detail",
]

BASELINE = {
    "model_family": "TF-IDF + Logistic Regression",
    "text_representation": "word-level TF-IDF",
    "input_features": EXPECTED_FEATURES,
    "classifier": "LogisticRegression",
    "advanced_nlp": False,
    "class_weight": None,
}

METRICS = {
    "primary": [
        "top_1_accuracy",
        "top_3_accuracy",
        "top_5_accuracy",
        "top_10_accuracy",
    ],
    "secondary": [
        "macro_f1",
        "weighted_f1",
    ],
    "coverage": [
        "evaluation_candidate_coverage",
        "evaluation_row_coverage",
        "unseen_target_rows",
        "unseen_target_rate",
    ],
    "diagnostic": [
        "prediction_class_count",
        "prediction_top_1_share",
        "prediction_top_10_share",
        "prediction_top_50_share",
        "prediction_top_100_share",
    ],
}

CONTROLS = {
    "chronological_split_frozen": True,
    "candidate_space_from_training_only": True,
    "unseen_evaluation_targets_retained": True,
    "unseen_targets_not_converted_to_negatives": True,
    "unseen_targets_not_dropped": True,
    "target_side_fields_excluded_from_features": True,
    "creation_time_boundary_respected": True,
    "raw_mozilla_access": False,
    "target_reconstruction": False,
    "test_use": False,
}


def fail(message):
    raise RuntimeError(f"T4-MOD-005_FAILED: {message}")


def main():
    if not INPUT_PATH.exists():
        fail(f"Missing modeling artifact: {INPUT_PATH}")

    if not TRAIN_PATH.exists():
        fail(f"Missing chronological training split: {TRAIN_PATH}")

    if not EVAL_PATH.exists():
        fail(f"Missing chronological evaluation split: {EVAL_PATH}")

    full_df = pd.read_csv(INPUT_PATH, low_memory=False)
    train_df = pd.read_csv(TRAIN_PATH, low_memory=False)
    eval_df = pd.read_csv(EVAL_PATH, low_memory=False)

    # ------------------------------------------------------------------
    # Structural validation
    # ------------------------------------------------------------------
    if list(full_df.columns) != EXPECTED_MODELING_COLUMNS:
        fail(
            "Full modeling artifact schema mismatch.\n"
            f"Expected: {EXPECTED_MODELING_COLUMNS}\n"
            f"Found:    {list(full_df.columns)}"
        )

    if list(train_df.columns) != EXPECTED_MODELING_COLUMNS:
        fail("Training split schema mismatch.")

    if list(eval_df.columns) != EXPECTED_MODELING_COLUMNS:
        fail("Evaluation split schema mismatch.")

    if len(full_df) != 178127:
        fail(f"Unexpected full-row count: {len(full_df)}")

    if len(train_df) != 142501:
        fail(f"Unexpected training-row count: {len(train_df)}")

    if len(eval_df) != 35626:
        fail(f"Unexpected evaluation-row count: {len(eval_df)}")

    if len(set(train_df["ID"]) & set(eval_df["ID"])) != 0:
        fail("ID overlap detected between train and evaluation.")

    # ------------------------------------------------------------------
    # Feature/target controls
    # ------------------------------------------------------------------
    for feature in EXPECTED_FEATURES:
        if feature not in train_df.columns:
            fail(f"Required feature missing: {feature}")

    if TARGET_COLUMN not in train_df.columns:
        fail("Target column missing.")

    forbidden_present = [
        col for col in FORBIDDEN_TARGET_SIDE_COLUMNS
        if col in train_df.columns
    ]

    if forbidden_present:
        fail(
            "Forbidden target-side columns present in modeling split: "
            + "|".join(forbidden_present)
        )

    # ------------------------------------------------------------------
    # Candidate-space controls
    # ------------------------------------------------------------------
    training_candidates = set(train_df[TARGET_COLUMN].dropna().unique())
    evaluation_targets = set(eval_df[TARGET_COLUMN].dropna().unique())

    covered_targets = evaluation_targets & training_candidates
    unseen_targets = evaluation_targets - training_candidates

    covered_rows = eval_df[TARGET_COLUMN].isin(training_candidates).sum()
    unseen_rows = len(eval_df) - covered_rows

    unseen_rate = unseen_rows / len(eval_df)

    # ------------------------------------------------------------------
    # Feature availability
    # ------------------------------------------------------------------
    blank_feature_counts = {
        feature: int(train_df[feature].fillna("").astype(str).str.strip().eq("").sum())
        for feature in EXPECTED_FEATURES
    }

    # Summary is required by the validated artifact; Description may be blank.
    usable_text_rows_train = (
        train_df["Summary"].fillna("").astype(str).str.strip().ne("")
        |
        train_df["Description"].fillna("").astype(str).str.strip().ne("")
    ).sum()

    usable_text_rows_eval = (
        eval_df["Summary"].fillna("").astype(str).str.strip().ne("")
        |
        eval_df["Description"].fillna("").astype(str).str.strip().ne("")
    ).sum()

    if usable_text_rows_train != len(train_df):
        fail(
            "Training contains rows with neither usable Summary nor Description."
        )

    if usable_text_rows_eval != len(eval_df):
        fail(
            "Evaluation contains rows with neither usable Summary nor Description."
        )

    # ------------------------------------------------------------------
    # Baseline protocol
    # ------------------------------------------------------------------
    contract = {
        "operation": "T4-MOD-005",
        "task": "T4 — Specific Assignee Prediction",
        "status": "READY_FOR_BASELINE_MODELING",

        "source_artifact": str(INPUT_PATH),
        "training_artifact": str(TRAIN_PATH),
        "evaluation_artifact": str(EVAL_PATH),

        "population": {
            "full_rows": int(len(full_df)),
            "training_rows": int(len(train_df)),
            "evaluation_rows": int(len(eval_df)),
            "training_observed_candidate_assignees": int(
                len(training_candidates)
            ),
            "evaluation_distinct_targets": int(len(evaluation_targets)),
            "covered_evaluation_distinct_targets": int(
                len(covered_targets)
            ),
            "unseen_evaluation_distinct_targets": int(
                len(unseen_targets)
            ),
            "covered_evaluation_rows": int(covered_rows),
            "unseen_evaluation_rows": int(unseen_rows),
            "unseen_evaluation_rate": float(unseen_rate),
        },

        "prediction_boundary": "Creation time",

        "features": {
            "admitted": EXPECTED_FEATURES,
            "target": TARGET_COLUMN,
            "target_side_fields_excluded": FORBIDDEN_TARGET_SIDE_COLUMNS,
            "blank_feature_counts_training": blank_feature_counts,
        },

        "baseline": BASELINE,

        "evaluation_protocol": {
            "primary_metrics": METRICS["primary"],
            "secondary_metrics": METRICS["secondary"],
            "coverage_metrics": METRICS["coverage"],
            "diagnostic_metrics": METRICS["diagnostic"],
            "top_k": [1, 3, 5, 10],
            "candidate_space": (
                "Distinct target_assignee values observed in training only"
            ),
            "unseen_target_policy": (
                "Retain in evaluation; do not convert to negatives, "
                "do not silently discard"
            ),
        },

        "controls": CONTROLS,

        "modeling_state": {
            "model_fitted": False,
            "predictions_created": False,
            "evaluation_scored": False,
            "test_used": False,
        },

        "notes": [
            "T4 is a high-cardinality multiclass routing/assignment task.",
            "Historical target assignees are not treated as universal "
            "operational eligibility.",
            "Top-k metrics are required because routing is a candidate "
            "recommendation problem with a severe long tail.",
            "Unseen evaluation targets represent open-world cases outside "
            "the training-observed candidate space.",
            "No advanced NLP model is admitted before the classical baseline "
            "is executed and analyzed.",
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(contract, f, indent=2)

    print("T4-MOD-005_COMPLETE")
    print(f"FULL_ROWS={len(full_df)}")
    print(f"TRAIN_ROWS={len(train_df)}")
    print(f"EVALUATION_ROWS={len(eval_df)}")
    print(f"TRAINING_OBSERVED_CANDIDATES={len(training_candidates)}")
    print(f"EVALUATION_DISTINCT_TARGETS={len(evaluation_targets)}")
    print(f"COVERED_EVALUATION_DISTINCT_TARGETS={len(covered_targets)}")
    print(f"UNSEEN_EVALUATION_DISTINCT_TARGETS={len(unseen_targets)}")
    print(f"COVERED_EVALUATION_ROWS={covered_rows}")
    print(f"UNSEEN_EVALUATION_ROWS={unseen_rows}")
    print(f"UNSEEN_EVALUATION_RATE={unseen_rate:.8f}")
    print(f"TRAIN_USABLE_TEXT_ROWS={usable_text_rows_train}")
    print(f"EVAL_USABLE_TEXT_ROWS={usable_text_rows_eval}")
    print(f"BASELINE={BASELINE['model_family']}")
    print("TOP_K=1|3|5|10")
    print("RAW_MOZILLA_ACCESSED=False")
    print("MODEL_TRAINED=False")
    print("PREDICTIONS_CREATED=False")
    print("TEST_USED=False")
    print("STATUS=READY_FOR_BASELINE_MODELING")
    print(f"OUTPUT={OUTPUT_PATH}")


if __name__ == "__main__":
    main()
