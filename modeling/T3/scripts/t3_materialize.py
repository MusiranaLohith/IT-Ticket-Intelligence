from pathlib import Path
import pandas as pd


SOURCE = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T3_FIRST_SEVERITY_derived.csv"
)

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

OUTPUT_DIR = PROJECT_ROOT / "modeling" / "T3" / "derived"
OUTPUT = OUTPUT_DIR / "t3_features.csv"


REQUIRED_COLUMNS = [
    "ID",
    "Creation time",
    "Summary",
    "Description",
    "target_severity",
]

EXPECTED_TARGETS = {"S1", "S2", "S3", "S4"}


def main():
    print("T3_MOD_004_START")

    if not SOURCE.is_file():
        raise FileNotFoundError(f"SOURCE_ARTIFACT_NOT_FOUND={SOURCE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(
        SOURCE,
        keep_default_na=False,
    )

    print(f"SOURCE_ROWS={len(df)}")
    print(f"SOURCE_COLUMNS={len(df.columns)}")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise RuntimeError(f"REQUIRED_COLUMNS_MISSING={missing}")

    unexpected_target_values = sorted(
        set(df["target_severity"].astype(str)) - EXPECTED_TARGETS
    )

    if unexpected_target_values:
        raise RuntimeError(
            f"INVALID_TARGET_VALUES={unexpected_target_values}"
        )

    if df["ID"].duplicated().any():
        duplicate_count = int(df["ID"].duplicated().sum())
        raise RuntimeError(
            f"DUPLICATE_IDS_IN_SOURCE={duplicate_count}"
        )

    if (df["Summary"].str.strip() == "").all() and (
        df["Description"].str.strip() == ""
    ).all():
        raise RuntimeError("NO_PREDICTIVE_TEXT_AVAILABLE")

    features = df[REQUIRED_COLUMNS].copy()

    if len(features) != 30839:
        raise RuntimeError(
            f"UNEXPECTED_T3_ROW_COUNT={len(features)}"
        )

    target_counts = (
        features["target_severity"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    print(f"TARGET_COUNTS={target_counts}")

    tmp_output = OUTPUT.with_suffix(".tmp.csv")

    features.to_csv(
        tmp_output,
        index=False,
    )

    written = pd.read_csv(
        tmp_output,
        keep_default_na=False,
    )

    if len(written) != len(features):
        raise RuntimeError(
            f"WRITTEN_ROW_COUNT_MISMATCH="
            f"{len(written)}!={len(features)}"
        )

    if list(written.columns) != REQUIRED_COLUMNS:
        raise RuntimeError(
            f"WRITTEN_SCHEMA_MISMATCH={list(written.columns)}"
        )

    if written["ID"].duplicated().any():
        raise RuntimeError("DUPLICATE_IDS_IN_WRITTEN_ARTIFACT")

    written_target_counts = (
        written["target_severity"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    if written_target_counts != target_counts:
        raise RuntimeError(
            "WRITTEN_TARGET_DISTRIBUTION_MISMATCH"
        )

    tmp_output.replace(OUTPUT)

    print(f"OUTPUT_ROWS={len(written)}")
    print(f"OUTPUT_COLUMNS={len(written.columns)}")
    print(f"OUTPUT={OUTPUT}")
    print("RAW_MOZILLA_ACCESSED=False")
    print("TARGET_RECONSTRUCTED=False")
    print("STATUS=ACCEPTED")
    print("T3_MOD_004_COMPLETE")


if __name__ == "__main__":
    main()