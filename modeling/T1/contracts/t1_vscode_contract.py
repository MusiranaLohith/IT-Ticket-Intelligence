from pathlib import Path
import json


PROJECT_ROOT = Path(
    "/"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "contracts"
    / "t1_vscode_contract.json"
)


CONTRACT = {
    "dataset": "GitBugs VS Code",

    "task": {
        "name": "T1 Classification",
        "objective": (
            "Classify an incoming VS Code issue by issue type "
            "at the Created prediction boundary."
        ),
    },

    "source": {
        "archive": (
            "/run/media/whiteblack/User 1/Datasets/"
            "GitBugs/vscode_bugs.csv.zip"
        ),
        "data_member": "vscode_bugs.csv",
        "source_records": 32829,
    },

    "target": {
        "semantic_name": "issue_type",
        "physical_source_column": None,
        "derivation_source": "Description",
        "historical_markers": [
            "Issue Type:",
            "Type:",
        ],
        "classes": [
            "Bug",
            "Feature Request",
            "Performance Issue",
            "Usability",
        ],
        "normalization": (
            "Use the DTM-established normalization of the historical "
            "Issue Type:/Type: representations into the four frozen "
            "T1 classes. Ambiguous or non-mappable values must not "
            "be force-assigned."
        ),
    },

    "prediction_boundary": {
        "field": "Created",
        "moment": "Created",
    },

    "features": {
        "primary": [
            "Summary",
        ],
        "conditional": [
            "Description",
        ],
        "forbidden": [
            "Resolved",
            "Resolution",
        ],
        "provenance_only": [
            "Issue id",
        ],
    },

    "description_control": {
        "allowed": True,
        "rule": (
            "Description may be used only after removing the "
            "target-bearing Issue Type:/Type: material used to "
            "derive the target."
        ),
    },

    "split": {
        "method": "chronological",
        "ordering_field": "Created",
        "random_split": False,
    },

    "modeling_status": {
        "derived_dataset_created": False,
        "derived_dataset_validated": False,
        "split_created": False,
        "baseline_trained": False,
        "model_selected": False,
        "training_started": False,
    },

    "data_integrity": {
        "labels_modified": False,
        "source_data_modified": False,
    },

    "rules": [
        "Preserve the raw source dataset unchanged.",
        "Do not use future information relative to Created.",
        "Do not use Resolved as a predictive feature.",
        "Do not use Resolution as a predictive feature.",
        "Do not use Issue id as a semantic predictive feature.",
        "Do not silently merge VS Code with IT Support.",
        "Do not force ambiguous target values into a class.",
        "Preserve label provenance during target derivation.",
        "Remove target-bearing Description material before using "
        "Description as a predictive feature.",
        "Freeze the chronological split before model training.",
        "Establish the baseline before advanced model selection.",
    ],
}


def main():
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            CONTRACT,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("VSCODE_T1_CONTRACT_CORRECTED")
    print(f"OUTPUT={OUTPUT_PATH}")
    print("TARGET_SEMANTIC_NAME=issue_type")
    print("PHYSICAL_TARGET_COLUMN=None")
    print("TARGET_SOURCE=Description")
    print("HISTORICAL_MARKERS=Issue Type:,Type:")
    print("CLASSES=4")
    print("SOURCE_RECORDS=32829")
    print("SPLIT=CHRONOLOGICAL")
    print("MODEL_SELECTED=False")
    print("TRAINING_STARTED=False")
    print("STATUS=SUPPORTED")


if __name__ == "__main__":
    main()