from pathlib import Path
import json
import hashlib
import pandas as pd


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

SOURCE_ARTIFACT = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T4_FIRST_SPECIFIC_ASSIGNEE_derived.csv"
)

CONTRACT_DIR = (
    PROJECT_ROOT / "modeling" / "T4" / "contracts"
)

OUTPUT_CONTRACT = (
    CONTRACT_DIR / "t4_model_contract.json"
)


TASK = "T4"
TASK_NAME = "Routing / Assignment"
DATASET = "Mozilla CORE"

TARGET_COLUMN = "target_assignee"
CREATION_COLUMN = "Creation time"

ADMITTED_FEATURES = [
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
]

FORBIDDEN_FEATURES = [
    "Assigned to",
    "Assigned to detail",
    "target_assignee",
    "target_assignment_time",
    "target_event_index",
    "target_change_index",
    "any post-Creation information",
    "any future assignment information",
    "any current/final value used as historical backfill",
]

EXPECTED_ROWS = 178_127
EXPECTED_COLUMNS = 10
EXPECTED_DISTINCT_TARGETS = 4_809

EXPECTED_TRAIN_ROWS = 142_501
EXPECTED_EVAL_ROWS = 35_626

EXPECTED_TRAIN_CANDIDATES = 4_139
EXPECTED_UNSEEN_EVAL_ROWS = 2_853
EXPECTED_COVERED_EVAL_ROWS = 32_773


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def main():
    CONTRACT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not SOURCE_ARTIFACT.exists():
        raise FileNotFoundError(
            "SOURCE_ARTIFACT_NOT_FOUND="
            f"{SOURCE_ARTIFACT}"
        )

    df = pd.read_csv(
        SOURCE_ARTIFACT,
        dtype=str,
        keep_default_na=False,
    )

    actual_rows = len(df)
    actual_columns = len(df.columns)

    required_columns = [
        "ID",
        "Creation time",
        "Creator",
        "Creator Detail",
        "Summary",
        "Description",
        "target_assignee",
        "target_assignment_time",
        "target_event_index",
        "target_change_index",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise RuntimeError(
            "MISSING_REQUIRED_COLUMNS="
            f"{missing_columns}"
        )

    actual_target_count = (
        df[TARGET_COLUMN].nunique()
    )

    feature_columns_present = [
        column
        for column in ADMITTED_FEATURES
        if column in df.columns
    ]

    forbidden_columns_present = [
        column
        for column in [
            "Assigned to",
            "Assigned to detail",
            "target_assignee",
            "target_assignment_time",
            "target_event_index",
            "target_change_index",
        ]
        if column in df.columns
    ]

    duplicate_ids = int(
        df["ID"].duplicated().sum()
    )

    blank_target = int(
        df[TARGET_COLUMN]
        .str.strip()
        .eq("")
        .sum()
    )

    blank_creation = int(
        df[CREATION_COLUMN]
        .str.strip()
        .eq("")
        .sum()
    )

    blank_creator = int(
        df["Creator"]
        .str.strip()
        .eq("")
        .sum()
    )

    blank_creator_detail = int(
        df["Creator Detail"]
        .str.strip()
        .eq("")
        .sum()
    )

    blank_summary = int(
        df["Summary"]
        .str.strip()
        .eq("")
        .sum()
    )

    blank_description = int(
        df["Description"]
        .str.strip()
        .eq("")
        .sum()
    )

    target_distribution = (
        df[TARGET_COLUMN]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    contract = {
        "contract_id": "T4-MOD-001",

        "task": TASK,

        "task_name": TASK_NAME,

        "dataset": DATASET,

        "status":
            "READY_FOR_CONTROLLED_MODELING",

        "source_artifact":
            str(SOURCE_ARTIFACT),

        "source_artifact_sha256":
            sha256_file(SOURCE_ARTIFACT),

        "population": {
            "expected_rows": EXPECTED_ROWS,
            "observed_rows": actual_rows,

            "expected_columns":
                EXPECTED_COLUMNS,

            "observed_columns":
                actual_columns,

            "expected_distinct_target_assignees":
                EXPECTED_DISTINCT_TARGETS,

            "observed_distinct_target_assignees":
                actual_target_count,
        },

        "operational_target": {
            "target_column":
                TARGET_COLUMN,

            "definition":
                (
                    "First post-Creation assignment "
                    "to a specific assignee"
                ),

            "prediction_boundary":
                "Creation time",

            "target_event_must_be_strictly_after_creation":
                True,

            "nobody_mozilla_org_excluded":
                True,

            "blank_target_excluded":
                True,
        },

        "feature_boundary": {
            "admitted_features":
                ADMITTED_FEATURES,

            "feature_columns_present":
                feature_columns_present,

            "forbidden_features":
                FORBIDDEN_FEATURES,

            "current_assigned_to_is_target_side_information":
                True,

            "post_creation_information_forbidden":
                True,

            "future_assignment_information_forbidden":
                True,

            "current_final_backfill_forbidden":
                True,
        },

        "dataset_integrity_observed": {
            "duplicate_ids":
                duplicate_ids,

            "blank_target_rows":
                blank_target,

            "blank_creation_rows":
                blank_creation,

            "blank_creator_rows":
                blank_creator,

            "blank_creator_detail_rows":
                blank_creator_detail,

            "blank_summary_rows":
                blank_summary,

            "blank_description_rows":
                blank_description,

            "target_distribution":
                target_distribution,
        },

        "evaluation_protocol": {
            "type":
                "chronological",

            "ordering_variable":
                "Creation time",

            "train_rows":
                EXPECTED_TRAIN_ROWS,

            "evaluation_rows":
                EXPECTED_EVAL_ROWS,

            "train_fraction":
                0.80,

            "evaluation_fraction":
                0.20,

            "random_shuffle":
                False,

            "candidate_space": {
                "definition":
                    (
                        "Distinct target_assignee "
                        "values observed in the "
                        "training portion only"
                    ),

                "training_observed_candidates":
                    EXPECTED_TRAIN_CANDIDATES,

                "global_historical_assignees":
                    EXPECTED_DISTINCT_TARGETS,

                "global_universe_must_not_be_used_for_evaluation":
                    True,
            },

            "unseen_evaluation_targets": {
                "rows":
                    EXPECTED_UNSEEN_EVAL_ROWS,

                "covered_rows":
                    EXPECTED_COVERED_EVAL_ROWS,

                "rate":
                    (
                        EXPECTED_UNSEEN_EVAL_ROWS
                        / EXPECTED_EVAL_ROWS
                    ),

                "retain_in_evaluation":
                    True,

                "treat_as_negative":
                    False,

                "silently_discard":
                    False,
            },
        },

        "evaluation_metrics": {
            "primary": [
                "top_1_accuracy",
                "macro_f1_within_candidate_space",
            ],

            "secondary": [
                "weighted_f1_within_candidate_space",
                "top_3_accuracy",
                "top_5_accuracy",
                "top_10_accuracy",
                "mean_reciprocal_rank",
            ],

            "required_reporting": [
                "per_class_support",
                "per_class_precision",
                "per_class_recall",
                "per_class_f1",
                "candidate_space_coverage",
                "unseen_target_rate",
            ],

            "unseen_target_evaluation":
                (
                    "reported separately; never "
                    "converted into negatives"
                ),
        },

        "modeling_constraints": {
            "advanced_model_before_baseline":
                False,

            "test_or_evaluation_selection":
                False,

            "future_candidate_leakage":
                False,

            "raw_archive_access":
                False,

            "raw_dataset_modification":
                False,

            "derived_dataset_modification":
                False,

            "synthetic_labels":
                False,

            "operational_assignee_eligibility_claim":
                False,

            "universal_routing_correctness_claim":
                False,
        },

        "candidate_selection_policy": {
            "candidate_selection_uses_training_validation_only":
                True,

            "locked_evaluation_not_used_for_selection":
                True,

            "no_predefined_universal_acceptance_threshold":
                True,

            "must_report_class_imbalance":
                True,

            "must_report_long_tail_behavior":
                True,

            "must_preserve_open_world_unseen_target_information":
                True,
        },

        "t4_specific_risks": [
            "high-cardinality multiclass target",
            "long-tail assignee distribution",
            "unseen evaluation assignees",
            "training-only candidate universe",
            (
                "historical assignment is not "
                "universal routing correctness"
            ),
            (
                "operational assignee eligibility "
                "is not established"
            ),
        ],

        "controls": {
            "target_frozen":
                True,

            "prediction_boundary_frozen":
                True,

            "feature_boundary_frozen":
                True,

            "chronological_protocol_frozen":
                True,

            "candidate_space_training_only":
                True,

            "unseen_targets_retained":
                True,

            "unseen_targets_not_negatives":
                True,

            "operational_eligibility_not_claimed":
                True,
        },

        "execution_policy": {
            "raw_mozilla_accessed":
                False,

            "history_reconstructed":
                False,

            "dataset_modified":
                False,

            "model_trained":
                False,

            "predictions_created":
                False,

            "test_used":
                False,
        },

        "evidence_basis": [
            "DTM-002 T4 frozen first-specific-assignee target",
            "DTM-002 T4 Creation-time feature boundary",
            "DTM-002 T4 validated 178,127-row derived dataset",
            "DTM-002 T4 frozen chronological 80/20 evaluation protocol",
            (
                "DTM-002 T4 training-observed "
                "candidate-space definition"
            ),
        ],
    }

    OUTPUT_CONTRACT.write_text(
        json.dumps(
            contract,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("T4-MOD-001_COMPLETE")
    print(f"OUTPUT={OUTPUT_CONTRACT}")
    print(f"SOURCE_ROWS={actual_rows}")
    print(f"SOURCE_COLUMNS={actual_columns}")
    print(
        "DISTINCT_TARGET_ASSIGNEES="
        f"{actual_target_count}"
    )
    print(f"DUPLICATE_IDS={duplicate_ids}")
    print(f"BLANK_TARGET={blank_target}")
    print(f"BLANK_CREATION={blank_creation}")
    print(f"BLANK_CREATOR={blank_creator}")
    print(
        "BLANK_CREATOR_DETAIL="
        f"{blank_creator_detail}"
    )
    print(f"BLANK_SUMMARY={blank_summary}")
    print(
        "BLANK_DESCRIPTION="
        f"{blank_description}"
    )
    print(
        "FEATURES="
        + "|".join(feature_columns_present)
    )
    print(
        "FORBIDDEN_COLUMNS_PRESENT="
        + "|".join(forbidden_columns_present)
    )
    print(
        "STATUS=READY_FOR_CONTROLLED_MODELING"
    )
    print(
        "RAW_MOZILLA_ACCESSED=False"
    )
    print(
        "MODEL_TRAINED=False"
    )
    print(
        "PREDICTIONS_CREATED=False"
    )
    print(
        "TEST_USED=False"
    )


if __name__ == "__main__":
    main()