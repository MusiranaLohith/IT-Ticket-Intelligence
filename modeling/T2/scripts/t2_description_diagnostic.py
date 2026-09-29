from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
FEATURE_FILE = (
    PROJECT_ROOT
    / "modeling"
    / "T2"
    / "derived"
    / "t2_features.csv"
)


def main():
    print("T2_MOD_004A_START")

    if not FEATURE_FILE.exists():
        raise FileNotFoundError(FEATURE_FILE)

    df = pd.read_csv(
        FEATURE_FILE,
        dtype={
            "ID": "string",
            "Summary": "string",
            "Description": "string",
            "target_priority": "string",
        },
        keep_default_na=False,
    )

    description = df["Description"]

    null_count = int(description.isna().sum())

    empty_count = int(
        description.eq("").sum()
    )

    whitespace_only_count = int(
        description.str.strip().eq("").sum()
    )

    non_empty_count = int(
        description.str.strip().ne("").sum()
    )

    total_unavailable = int(
        description.str.strip().eq("").sum()
    )

    print(f"ROWS={len(df)}")
    print(f"DESCRIPTION_NULL={null_count}")
    print(f"DESCRIPTION_EMPTY={empty_count}")
    print(f"DESCRIPTION_WHITESPACE_ONLY={whitespace_only_count}")
    print(f"DESCRIPTION_UNAVAILABLE={total_unavailable}")
    print(f"DESCRIPTION_NON_EMPTY={non_empty_count}")

    print("\nDESCRIPTION_VALUE_COUNTS_FOR_EMPTY_LIKE_VALUES")

    empty_like = df[
        description.str.strip().eq("")
    ]

    print(f"EMPTY_LIKE_ROWS={len(empty_like)}")

    if len(empty_like) > 0:
        print("\nSAMPLE_EMPTY_LIKE_RECORDS")
        print(
            empty_like[
                ["ID", "Description"]
            ].head(20).to_string(index=False)
        )

    print("\nT2_MOD_004A_COMPLETE")
    print("STATUS=DIAGNOSTIC_ONLY")


if __name__ == "__main__":
    main()