from pathlib import Path
import json
import pandas as pd


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

INPUT = (
    PROJECT_ROOT
    / "modeling"
    / "T3"
    / "derived"
    / "t3_features.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "T3"
    / "splits"
)

REPORT = (
    PROJECT_ROOT
    / "modeling"
    / "T3"
    / "analysis"
    / "t3_split_report.json"
)

EXPECTED_ROWS = 30839

TRAIN_FRACTION = 0.70
VALIDATION_FRACTION = 0.15
TEST_FRACTION = 0.15


def distribution(df):
    counts = (
        df["target_severity"]
        .value_counts()
        .reindex(["S1", "S2", "S3", "S4"], fill_value=0)
    )

    percentages = (
        counts / len(df) * 100
    ).round(4)

    return {
        label: {
            "count": int(counts[label]),
            "percentage": float(percentages[label]),
        }
        for label in ["S1", "S2", "S3", "S4"]
    }


def main():
    print("T3_MOD_006_START")

    if not INPUT.is_file():
        raise FileNotFoundError(
            f"INPUT_NOT_FOUND={INPUT}"
        )

    df = pd.read_csv(
        INPUT,
        keep_default_na=False,
    )

    if len(df) != EXPECTED_ROWS:
        raise RuntimeError(
            f"UNEXPECTED_ROW_COUNT={len(df)}"
        )

    df["Creation time"] = pd.to_datetime(
        df["Creation time"],
        utc=True,
        errors="raise",
    )

    # Deterministic chronological ordering.
    # ID is the tie-breaker for identical Creation timestamps.
    df = df.sort_values(
        by=["Creation time", "ID"],
        kind="mergesort",
    ).reset_index(drop=True)

    n = len(df)

    train_end = int(n * TRAIN_FRACTION)
    validation_end = int(
        n * (TRAIN_FRACTION + VALIDATION_FRACTION)
    )

    train = df.iloc[:train_end].copy()
    validation = df.iloc[
        train_end:validation_end
    ].copy()
    test = df.iloc[validation_end:].copy()

    if (
        len(train)
        + len(validation)
        + len(test)
        != n
    ):
        raise RuntimeError(
            "SPLIT_ROW_ACCOUNTING_FAILED"
        )

    if (
        train["ID"].isin(validation["ID"]).any()
        or train["ID"].isin(test["ID"]).any()
        or validation["ID"].isin(test["ID"]).any()
    ):
        raise RuntimeError(
            "ID_OVERLAP_BETWEEN_SPLITS"
        )

    # Verify strict chronological separation.
    if train["Creation time"].max() > validation["Creation time"].min():
        raise RuntimeError(
            "TRAIN_VALIDATION_TEMPORAL_ORDER_FAILED"
        )

    if validation["Creation time"].max() > test["Creation time"].min():
        raise RuntimeError(
            "VALIDATION_TEST_TEMPORAL_ORDER_FAILED"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    train_path = OUTPUT_DIR / "t3_train.csv"
    validation_path = OUTPUT_DIR / "t3_validation.csv"
    test_path = OUTPUT_DIR / "t3_test.csv"

    train.to_csv(
        train_path,
        index=False,
    )

    validation.to_csv(
        validation_path,
        index=False,
    )

    test.to_csv(
        test_path,
        index=False,
    )

    report = {
        "input": str(INPUT),
        "total_rows": int(n),
        "split_method": (
            "chronological Creation time with deterministic ID tie-break"
        ),
        "fractions": {
            "train": TRAIN_FRACTION,
            "validation": VALIDATION_FRACTION,
            "test": TEST_FRACTION,
        },
        "splits": {
            "train": {
                "rows": int(len(train)),
                "creation_min": train["Creation time"].min().isoformat(),
                "creation_max": train["Creation time"].max().isoformat(),
                "distribution": distribution(train),
            },
            "validation": {
                "rows": int(len(validation)),
                "creation_min": validation["Creation time"].min().isoformat(),
                "creation_max": validation["Creation time"].max().isoformat(),
                "distribution": distribution(validation),
            },
            "test": {
                "rows": int(len(test)),
                "creation_min": test["Creation time"].min().isoformat(),
                "creation_max": test["Creation time"].max().isoformat(),
                "distribution": distribution(test),
            },
        },
        "id_overlap": False,
        "temporal_order_valid": True,
        "status": "PASS",
    }

    REPORT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"TOTAL_ROWS={n}")

    print(
        f"TRAIN_ROWS={len(train)}"
    )
    print(
        f"TRAIN_RANGE="
        f"{train['Creation time'].min().isoformat()}"
        f" -> "
        f"{train['Creation time'].max().isoformat()}"
    )
    print(
        f"TRAIN_TARGET_COUNTS="
        f"{train['target_severity'].value_counts().sort_index().to_dict()}"
    )

    print(
        f"VALIDATION_ROWS={len(validation)}"
    )
    print(
        f"VALIDATION_RANGE="
        f"{validation['Creation time'].min().isoformat()}"
        f" -> "
        f"{validation['Creation time'].max().isoformat()}"
    )
    print(
        f"VALIDATION_TARGET_COUNTS="
        f"{validation['target_severity'].value_counts().sort_index().to_dict()}"
    )

    print(
        f"TEST_ROWS={len(test)}"
    )
    print(
        f"TEST_RANGE="
        f"{test['Creation time'].min().isoformat()}"
        f" -> "
        f"{test['Creation time'].max().isoformat()}"
    )
    print(
        f"TEST_TARGET_COUNTS="
        f"{test['target_severity'].value_counts().sort_index().to_dict()}"
    )

    print("ID_OVERLAP=False")
    print("TEMPORAL_ORDER_VALID=True")
    print(f"REPORT={REPORT}")
    print("STATUS=PASS")
    print("T3_MOD_006_COMPLETE")


if __name__ == "__main__":
    main()