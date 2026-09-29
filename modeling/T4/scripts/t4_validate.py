from pathlib import Path
import json
import pandas as pd


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

INPUT_ARTIFACT = (
    PROJECT_ROOT
    / "modeling"
    / "T4"
    / "derived"
    / "t4_features.csv"
)

OUTPUT_REPORT = (
    PROJECT_ROOT
    / "modeling"
    / "T4"
    / "derived"
    / "t4_validation_report.json"
)


EXPECTED_ROWS = 178_127

EXPECTED_COLUMNS = [
    "ID",
    "Creation time",
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
    "target_assignee",
]

FORBIDDEN_COLUMNS = [
    "Assigned to",
    "Assigned to detail",
    "target_assignment_time",
    "target_event_index",
    "target_change_index",
]


def main():
    if not INPUT_ARTIFACT.exists():
        raise FileNotFoundError(
            "INPUT_ARTIFACT_NOT_FOUND="
            f"{INPUT_ARTIFACT}"
        )

    df = pd.read_csv(
        INPUT_ARTIFACT,
        dtype=str,
        keep_default_na=False,
    )

    rows = len(df)
    columns = list(df.columns)

    schema_exact = columns == EXPECTED_COLUMNS

    missing_columns = [
        col
        for col in EXPECTED_COLUMNS
        if col not in columns
    ]

    unexpected_columns = [
        col
        for col in columns
        if col not in EXPECTED_COLUMNS
    ]

    duplicate_ids = int(
        df["ID"].duplicated().sum()
    )

    blank_ids = int(
        df["ID"]
        .str.strip()
        .eq("")
        .sum()
    )

    creation_parsed = pd.to_datetime(
        df["Creation time"],
        errors="coerce",
        utc=True,
    )

    invalid_creation = int(
        creation_parsed.isna().sum()
    )

    blank_creation = int(
        df["Creation time"]
        .str.strip()
        .eq("")
        .sum()
    )

    blank_target = int(
        df["target_assignee"]
        .str.strip()
        .eq("")
        .sum()
    )

    target_count = int(
        df["target_assignee"].nunique()
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

    usable_text = (
        df["Summary"].str.strip()
        + " "
        + df["Description"].str.strip()
    ).str.strip()

    no_usable_text = int(
        usable_text.eq("").sum()
    )

    forbidden_present = [
        col
        for col in FORBIDDEN_COLUMNS
        if col in columns
    ]

    target_counts = (
        df["target_assignee"]
        .value_counts()
        .sort_values(ascending=False)
    )

    target_count_values = (
        target_counts
        .tolist()
    )

    if target_count_values:
        top_1_count = target_count_values[0]

        top_10_count = sum(
            target_count_values[:10]
        )

        top_50_count = sum(
            target_count_values[:50]
        )

        top_100_count = sum(
            target_count_values[:100]
        )

        singleton_classes = int(
            (target_counts == 1).sum()
        )

        classes_with_le_5 = int(
            (target_counts <= 5).sum()
        )

        classes_with_le_10 = int(
            (target_counts <= 10).sum()
        )

        classes_with_le_20 = int(
            (target_counts <= 20).sum()
        )

        median_class_support = float(
            target_counts.median()
        )

        mean_class_support = float(
            target_counts.mean()
        )

        min_class_support = int(
            target_counts.min()
        )

        max_class_support = int(
            target_counts.max()
        )
    else:
        top_1_count = 0
        top_10_count = 0
        top_50_count = 0
        top_100_count = 0
        singleton_classes = 0
        classes_with_le_5 = 0
        classes_with_le_10 = 0
        classes_with_le_20 = 0
        median_class_support = 0.0
        mean_class_support = 0.0
        min_class_support = 0
        max_class_support = 0

    top_share = (
        top_1_count / rows
        if rows
        else 0.0
    )

    top_10_share = (
        top_10_count / rows
        if rows
        else 0.0
    )

    top_50_share = (
        top_50_count / rows
        if rows
        else 0.0
    )

    top_100_share = (
        top_100_count / rows
        if rows
        else 0.0
    )

    validation_pass = (
        rows == EXPECTED_ROWS
        and schema_exact
        and duplicate_ids == 0
        and blank_ids == 0
        and invalid_creation == 0
        and blank_creation == 0
        and blank_target == 0
        and no_usable_text == 0
        and len(forbidden_present) == 0
        and len(missing_columns) == 0
        and len(unexpected_columns) == 0
    )

    report = {
        "operation": "T4-MOD-003",

        "status":
            "PASS"
            if validation_pass
            else "FAIL",

        "artifact":
            str(INPUT_ARTIFACT),

        "rows":
            rows,

        "expected_rows":
            EXPECTED_ROWS,

        "columns":
            columns,

        "expected_columns":
            EXPECTED_COLUMNS,

        "schema_exact":
            schema_exact,

        "missing_columns":
            missing_columns,

        "unexpected_columns":
            unexpected_columns,

        "id_integrity": {
            "duplicate_ids":
                duplicate_ids,

            "blank_ids":
                blank_ids,
        },

        "creation_time": {
            "blank_creation":
                blank_creation,

            "invalid_creation":
                invalid_creation,
        },

        "target": {
            "column":
                "target_assignee",

            "blank_target":
                blank_target,

            "distinct_targets":
                target_count,
        },

        "feature_missingness": {
            "Creator":
                blank_creator,

            "Creator Detail":
                blank_creator_detail,

            "Summary":
                blank_summary,

            "Description":
                blank_description,

            "rows_without_any_summary_or_description":
                no_usable_text,
        },

        "forbidden_columns_present":
            forbidden_present,

        "target_distribution_profile": {
            "classes":
                target_count,

            "min_class_support":
                min_class_support,

            "median_class_support":
                median_class_support,

            "mean_class_support":
                mean_class_support,

            "max_class_support":
                max_class_support,

            "singleton_classes":
                singleton_classes,

            "classes_with_support_le_5":
                classes_with_le_5,

            "classes_with_support_le_10":
                classes_with_le_10,

            "classes_with_support_le_20":
                classes_with_le_20,

            "top_1_rows":
                top_1_count,

            "top_1_share":
                top_share,

            "top_10_rows":
                top_10_count,

            "top_10_share":
                top_10_share,

            "top_50_rows":
                top_50_count,

            "top_50_share":
                top_50_share,

            "top_100_rows":
                top_100_count,

            "top_100_share":
                top_100_share,
        },

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

    print("T4-MOD-003_COMPLETE")
    print(
        f"ROWS={rows}"
    )
    print(
        f"EXPECTED_ROWS={EXPECTED_ROWS}"
    )
    print(
        f"SCHEMA_EXACT={schema_exact}"
    )
    print(
        f"DUPLICATE_IDS={duplicate_ids}"
    )
    print(
        f"BLANK_IDS={blank_ids}"
    )
    print(
        f"BLANK_CREATION={blank_creation}"
    )
    print(
        f"INVALID_CREATION={invalid_creation}"
    )
    print(
        f"BLANK_TARGET={blank_target}"
    )
    print(
        f"DISTINCT_TARGETS={target_count}"
    )
    print(
        f"BLANK_CREATOR={blank_creator}"
    )
    print(
        f"BLANK_CREATOR_DETAIL={blank_creator_detail}"
    )
    print(
        f"BLANK_SUMMARY={blank_summary}"
    )
    print(
        f"BLANK_DESCRIPTION={blank_description}"
    )
    print(
        "NO_USABLE_SUMMARY_DESCRIPTION="
        f"{no_usable_text}"
    )
    print(
        "FORBIDDEN_COLUMNS_PRESENT="
        + "|".join(forbidden_present)
    )
    print(
        f"SINGLETON_CLASSES={singleton_classes}"
    )
    print(
        f"CLASSES_SUPPORT_LE_5={classes_with_le_5}"
    )
    print(
        f"CLASSES_SUPPORT_LE_10={classes_with_le_10}"
    )
    print(
        f"CLASSES_SUPPORT_LE_20={classes_with_le_20}"
    )
    print(
        f"MIN_CLASS_SUPPORT={min_class_support}"
    )
    print(
        f"MEDIAN_CLASS_SUPPORT={median_class_support}"
    )
    print(
        f"MAX_CLASS_SUPPORT={max_class_support}"
    )
    print(
        f"TOP_1_SHARE={top_share:.8f}"
    )
    print(
        f"TOP_10_SHARE={top_10_share:.8f}"
    )
    print(
        f"TOP_50_SHARE={top_50_share:.8f}"
    )
    print(
        f"TOP_100_SHARE={top_100_share:.8f}"
    )
    print(
        f"STATUS={'PASS' if validation_pass else 'FAIL'}"
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