from pathlib import Path
import csv
import sys


csv.field_size_limit(sys.maxsize)


EVALUATION = Path(
    "/run/media/whiteblack/User 1/Datasets/"
    "Mozilla_CORE/"
    "DTM-002_T5_EVAL_GROUP_AWARE.csv"
)


EXPECTED_COLUMNS = [
    "ID",
    "Creation time",
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
    "T5 target",
    "Target event index",
    "Target change index",
    "Target time",
    "Target actor",
]


def main():
    print("=" * 80)
    print("T5-MOD-009 — EXACT SCHEMA DIAGNOSTIC")
    print("=" * 80)

    with EVALUATION.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.reader(file)
        actual = next(reader)

    print("\nACTUAL HEADER")

    for index, value in enumerate(actual):
        print(
            f"{index + 1:02d}: "
            f"{value!r} "
            f"length={len(value)}"
        )

    print("\nEXPECTED HEADER")

    for index, value in enumerate(EXPECTED_COLUMNS):
        print(
            f"{index + 1:02d}: "
            f"{value!r} "
            f"length={len(value)}"
        )

    print("\nCOMPARISON")

    print(
        f"Actual column count: "
        f"{len(actual)}"
    )

    print(
        f"Expected column count: "
        f"{len(EXPECTED_COLUMNS)}"
    )

    print(
        f"Exact list equality: "
        f"{actual == EXPECTED_COLUMNS}"
    )

    if len(actual) == len(EXPECTED_COLUMNS):
        for index, (a, e) in enumerate(
            zip(actual, EXPECTED_COLUMNS),
            start=1,
        ):
            print(
                f"Column {index:02d}: "
                f"equal={a == e}"
            )

    print("\nNo model loaded.")
    print("No evaluation performed.")
    print("No files modified.")

    print(
        "\nRESULT: EXACT_SCHEMA_DIAGNOSTIC_COMPLETE"
    )


if __name__ == "__main__":
    main()