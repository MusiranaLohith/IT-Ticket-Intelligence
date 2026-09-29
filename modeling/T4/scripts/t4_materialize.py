from pathlib import Path
import json
import pandas as pd


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

SOURCE_ARTIFACT = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T4_FIRST_SPECIFIC_ASSIGNEE_derived.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT / "modeling" / "T4" / "derived"
)

OUTPUT_ARTIFACT = (
    OUTPUT_DIR / "t4_features.csv"
)

OUTPUT_REPORT = (
    OUTPUT_DIR / "t4_materialize_report.json"
)


OUTPUT_COLUMNS = [
    "ID",
    "Creation time",
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
    "target_assignee",
]


FORBIDDEN_OUTPUT_COLUMNS = [
    "target_assignment_time",
    "target_event_index",
    "target_change_index",
]


EXPECTED_ROWS = 178_127


def main():
    OUTPUT_DIR.mkdir(
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

    source_rows = len(df)
    source_columns = len(df.columns)

    missing_columns = [
        column
        for column in OUTPUT_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise RuntimeError(
            "REQUIRED_COLUMNS_MISSING="
            f"{missing_columns}"
        )

    output_df = df[OUTPUT_COLUMNS].copy()

    output_rows = len(output_df)
    output_columns = len(output_df.columns)

    duplicate_ids = int(
        output_df["ID"].duplicated().sum()
    )

    blank_target = int(
        output_df["target_assignee"]
        .str.strip()
        .eq("")
        .sum()
    )

    blank_creation = int(
        output_df["Creation time"]
        .str.strip()
        .eq("")
        .sum()
    )

    blank_creator = int(
        output_df["Creator"]
        .str.strip()
        .eq("")
        .sum()
    )

    blank_creator_detail = int(
        output_df["Creator Detail"]
        .str.strip()
        .eq("")
        .sum()
    )

    blank_summary = int(
        output_df["Summary"]
        .str.strip()
        .eq("")
        .sum()
    )

    blank_description = int(
        output_df["Description"]
        .str.strip()
        .eq("")
        .sum()
    )

    forbidden_present = [
        column
        for column in FORBIDDEN_OUTPUT_COLUMNS
        if column in output_df.columns
    ]

    if forbidden_present:
        raise RuntimeError(
            "FORBIDDEN_OUTPUT_COLUMNS_PRESENT="
            f"{forbidden_present}"
        )

    target_count = int(
        output_df["target_assignee"].nunique()
    )

    target_distribution = (
        output_df["target_assignee"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    output_df.to_csv(
        OUTPUT_ARTIFACT,
        index=False,
    )

    report = {
        "operation": "T4-MOD-002",
        "status": "ACCEPTED",

        "source_artifact":
            str(SOURCE_ARTIFACT),

        "output_artifact":
            str(OUTPUT_ARTIFACT),

        "source_rows":
            source_rows,

        "source_columns":
            source_columns,

        "output_rows":
            output_rows,

        "output_columns":
            output_columns,

        "output_columns_list":
            OUTPUT_COLUMNS,

        "duplicate_ids":
            duplicate_ids,

        "distinct_target_assignees":
            target_count,

        "blank_counts": {
            "target_assignee":
                blank_target,

            "Creation time":
                blank_creation,

            "Creator":
                blank_creator,

            "Creator Detail":
                blank_creator_detail,

            "Summary":
                blank_summary,

            "Description":
                blank_description,
        },

        "forbidden_output_columns_present":
            forbidden_present,

        "target_distribution":
            target_distribution,

        "controls": {
            "raw_mozilla_accessed":
                False,

            "history_reconstructed":
                False,

            "target_reconstructed":
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
    }

    OUTPUT_REPORT.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("T4-MOD-002_COMPLETE")
    print(f"SOURCE_ROWS={source_rows}")
    print(f"SOURCE_COLUMNS={source_columns}")
    print(f"OUTPUT={OUTPUT_ARTIFACT}")
    print(f"OUTPUT_ROWS={output_rows}")
    print(f"OUTPUT_COLUMNS={output_columns}")
    print(
        "OUTPUT_SCHEMA="
        + "|".join(OUTPUT_COLUMNS)
    )
    print(
        "DISTINCT_TARGET_ASSIGNEES="
        f"{target_count}"
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
        "FORBIDDEN_OUTPUT_COLUMNS_PRESENT="
        + "|".join(forbidden_present)
    )
    print(
        "RAW_MOZILLA_ACCESSED=False"
    )
    print(
        "TARGET_RECONSTRUCTED=False"
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
    print(
        "STATUS=ACCEPTED"
    )


if __name__ == "__main__":
    main()