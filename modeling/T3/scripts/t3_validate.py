from pathlib import Path
import json
import pandas as pd


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

INPUT = PROJECT_ROOT / "modeling" / "T3" / "derived" / "t3_features.csv"
OUTPUT = PROJECT_ROOT / "modeling" / "T3" / "analysis" / "t3_validation_report.json"


EXPECTED_COLUMNS = [
    "ID",
    "Creation time",
    "Summary",
    "Description",
    "target_severity",
]

EXPECTED_TARGETS = {"S1", "S2", "S3", "S4"}

EXPECTED_ROWS = 30839

FORBIDDEN_COLUMNS = {
    "target_time",
    "target_removed_severity",
    "target_actor",
    "target_history_event_index",
    "target_event_date",
    "migration_excluded",
}


def main():
    print("T3_MOD_005_START")

    if not INPUT.is_file():
        raise FileNotFoundError(f"INPUT_NOT_FOUND={INPUT}")

    df = pd.read_csv(
        INPUT,
        keep_default_na=False,
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "input": str(INPUT),
        "rows": int(len(df)),
        "columns": list(df.columns),
    }

    if len(df) != EXPECTED_ROWS:
        raise RuntimeError(
            f"ROW_COUNT_MISMATCH={len(df)}!={EXPECTED_ROWS}"
        )

    if list(df.columns) != EXPECTED_COLUMNS:
        raise RuntimeError(
            f"SCHEMA_MISMATCH={list(df.columns)}"
        )

    forbidden_present = sorted(
        FORBIDDEN_COLUMNS.intersection(df.columns)
    )

    if forbidden_present:
        raise RuntimeError(
            f"FORBIDDEN_COLUMNS_PRESENT={forbidden_present}"
        )

    duplicate_ids = int(df["ID"].duplicated().sum())

    if duplicate_ids:
        raise RuntimeError(
            f"DUPLICATE_IDS={duplicate_ids}"
        )

    target_values = set(df["target_severity"].astype(str))

    invalid_targets = sorted(
        target_values - EXPECTED_TARGETS
    )

    if invalid_targets:
        raise RuntimeError(
            f"INVALID_TARGETS={invalid_targets}"
        )

    creation = pd.to_datetime(
        df["Creation time"],
        errors="coerce",
        utc=True,
    )

    invalid_creation = int(creation.isna().sum())

    if invalid_creation:
        raise RuntimeError(
            f"INVALID_CREATION_TIMES={invalid_creation}"
        )

    summary_blank = int(
        (df["Summary"].str.strip() == "").sum()
    )

    description_blank = int(
        (df["Description"].str.strip() == "").sum()
    )

    usable_text = (
        (df["Summary"].str.strip() != "")
        | (df["Description"].str.strip() != "")
    )

    no_usable_text = int((~usable_text).sum())

    if no_usable_text:
        raise RuntimeError(
            f"ROWS_WITH_NO_USABLE_TEXT={no_usable_text}"
        )

    target_counts = (
        df["target_severity"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    report.update(
        {
            "unique_ids": int(df["ID"].nunique()),
            "duplicate_ids": duplicate_ids,
            "invalid_target_values": invalid_targets,
            "invalid_creation_times": invalid_creation,
            "summary_blank": summary_blank,
            "description_blank": description_blank,
            "no_usable_text": no_usable_text,
            "target_counts": target_counts,
            "forbidden_columns_present": forbidden_present,
            "status": "PASS",
        }
    )

    OUTPUT.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(f"ROWS={len(df)}")
    print(f"UNIQUE_IDS={df['ID'].nunique()}")
    print(f"DUPLICATE_IDS={duplicate_ids}")
    print(f"INVALID_CREATION_TIMES={invalid_creation}")
    print(f"SUMMARY_BLANK={summary_blank}")
    print(f"DESCRIPTION_BLANK={description_blank}")
    print(f"NO_USABLE_TEXT={no_usable_text}")
    print(f"TARGET_COUNTS={target_counts}")
    print(f"FORBIDDEN_COLUMNS={forbidden_present}")
    print(f"REPORT={OUTPUT}")
    print("STATUS=PASS")
    print("T3_MOD_005_COMPLETE")


if __name__ == "__main__":
    main()