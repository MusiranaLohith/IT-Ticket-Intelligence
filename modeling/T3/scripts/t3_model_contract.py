from pathlib import Path
import json


# ============================================================
# T3-MOD-001
# T3 Modeling Contract Reconciliation
#
# Contract-only operation.
# No training.
# No dataset modification.
# No target reconstruction.
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T3_ROOT = PROJECT_ROOT / "modeling" / "T3"

CONTRACTS_DIR = T3_ROOT / "contracts"

OUTPUT_FILE = (
    CONTRACTS_DIR
    / "t3_model_contract.json"
)


def main():

    print("T3_MOD_001_START")

    CONTRACTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    contract = {

        "operation": "T3-MOD-001",

        "task": "T3",

        "task_name": (
            "Severity Prediction"
        ),

        "dataset": "Mozilla CORE",

        "status": (
            "READY_FOR_CONTROLLED_MODELING"
        ),

        "target": {
            "name": (
                "first operational "
                "post-Creation Severity"
            ),

            "classes": [
                "S1",
                "S2",
                "S3",
                "S4",
            ],

            "selection_rule": (
                "First post-Creation History "
                "event containing a Severity "
                "change; use the first Severity "
                "change within that event."
            ),

            "admissible_added_values": [
                "S1",
                "S2",
                "S3",
                "S4",
            ],

            "excluded_target_values": [
                "S3 S3",
            ],

            "historical_severity_mapping": (
                "FORBIDDEN"
            ),

            "current_final_severity": (
                "FORBIDDEN_AS_CREATION_TARGET"
            ),
        },

        "prediction_boundary": {
            "name": "Creation",
            "type": "Creation-time cutoff",
            "post_creation_information": (
                "FORBIDDEN"
            ),
            "current_state_backfill": (
                "FORBIDDEN"
            ),
        },

        "horizon": {
            "type": (
                "event-based "
                "first-observable outcome"
            ),

            "fixed_hour_horizon": False,

            "description": (
                "The prediction target is the "
                "first admissible post-Creation "
                "Severity event rather than an "
                "arbitrary fixed-hour state."
            ),
        },

        "features": {
            "admitted": [
                "Summary",
                "Description",
            ],

            "boundary": (
                "Creation-time ticket content"
            ),

            "forbidden": [
                "post-Creation History",
                "target-event information",
                "current/final Severity",
                "current mutable state",
                "future information",
                "target-derived features",
                "historical Severity relabeling",
            ],
        },

        "migration_policy": {
            "documented_migration": (
                "2022-10-11/2022-10-12"
            ),

            "migration_actor": (
                "automation@bmo.tld"
            ),

            "excluded_migration_events": (
                39832
            ),

            "treatment": (
                "Exclude from ordinary "
                "operational T3 target population"
            ),

            "raw_history_modified": False,
        },

        "eligibility": {
            "authoritative_pre_exclusion_population": (
                70671
            ),

            "migration_exclusions": (
                39832
            ),

            "final_supervised_population": (
                30839
            ),

            "malformed_history_as_negative": (
                False
            ),

            "no_observation_as_negative": (
                False
            ),
        },

        "class_distribution": {
            "S1": {
                "count": 227,
                "percentage": 0.74,
            },

            "S2": {
                "count": 2886,
                "percentage": 9.36,
            },

            "S3": {
                "count": 20955,
                "percentage": 67.95,
            },

            "S4": {
                "count": 6771,
                "percentage": 21.96,
            },
        },

        "validated_artifact": {
            "path": (
                "/run/media/whiteblack/User 1/"
                "Datasets/Mozilla_CORE/"
                "DTM-002_T3_FIRST_SEVERITY_derived.csv"
            ),

            "rows": 30839,

            "columns": 11,

            "validated": True,

            "validation_operation": (
                "DTM-002 OP-049"
            ),

            "readiness_operation": (
                "DTM-002 OP-055"
            ),
        },

        "validation_status": {
            "structural_validation": "PASS",
            "target_accounting": "PASS",
            "temporal_integrity": "PASS",
            "migration_exclusion": "PASS",
            "feature_availability": "PASS",
            "semantic_leakage_review": "PASS",
            "duplicate_consistency": "PASS",
            "class_eligibility_accounting": "PASS",
        },

        "modeling_constraints": {
            "advanced_model_required": False,

            "test_set": (
                "Must remain locked until "
                "final model selection."
            ),

            "model_selection": (
                "Must be based on training/"
                "validation evidence only."
            ),

            "class_imbalance": (
                "Must be explicitly considered "
                "during modeling and evaluation."
            ),

            "minority_classes": [
                "S1",
                "S2",
            ],

            "calibration": (
                "Categorical probability/"
                "confidence evaluation is "
                "permitted and should remain "
                "task-specific."
            ),
        },

        "integrity": {
            "training_started": False,
            "model_selected": False,
            "test_used": False,
            "dataset_modified": False,
            "raw_source_modified": False,
            "rn136_modified": False,
        },

        "source_decision": {
            "dtm_status": (
                "CLOSED"
            ),

            "dtm_readiness": (
                "PASS"
            ),

            "modeling_readiness": (
                "READY_FOR_CONTROLLED_MODELING"
            ),
        },
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

    print(
        "TASK=T3_SEVERITY_PREDICTION"
    )

    print(
        "DATASET=Mozilla_CORE"
    )

    print(
        "FINAL_POPULATION=30839"
    )

    print(
        "TARGET=S1,S2,S3,S4"
    )

    print(
        "BOUNDARY=Creation"
    )

    print(
        "FEATURES=Summary,Description"
    )

    print(
        "HORIZON=EVENT_BASED_FIRST_OBSERVABLE"
    )

    print(
        "MIGRATION_EXCLUSIONS=39832"
    )

    print(
        "MODEL_SELECTED=False"
    )

    print(
        "TRAINING_STARTED=False"
    )

    print(
        "TEST_USED=False"
    )

    print(
        "DATASET_MODIFIED=False"
    )

    print(
        "STATUS=READY_FOR_CONTROLLED_MODELING"
    )

    print(
        "OUTPUT="
        f"{OUTPUT_FILE}"
    )

    print(
        "T3_MOD_001_COMPLETE"
    )


if __name__ == "__main__":
    main()