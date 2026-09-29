from pathlib import Path
import json


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

ANALYSIS_DIR = PROJECT_ROOT / "modeling" / "T3" / "analysis"

INPUT_PATH = (
    ANALYSIS_DIR / "t3_error_analysis.json"
)

OUTPUT_PATH = (
    ANALYSIS_DIR / "t3_error_inspection.json"
)

ERROR_PAIRS = [
    "S4_TO_S3",
    "S2_TO_S3",
    "S3_TO_S4",
    "S1_TO_S3",
    "S2_TO_S4",
]

MAX_DESCRIPTION_CHARS = 600


def main():
    print("T3_MOD_013_START")

    with INPUT_PATH.open(
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    inspection = {
        "task": "T3_SEVERITY_PREDICTION",
        "source": "T3-MOD-012 validation error analysis",
        "test_used": False,
        "pairs": {},
    }

    for pair in ERROR_PAIRS:
        examples = data["representative_errors"].get(
            pair,
            [],
        )

        selected = []

        for example in examples:
            description = example.get(
                "Description",
                "",
            )

            if len(description) > MAX_DESCRIPTION_CHARS:
                description = (
                    description[:MAX_DESCRIPTION_CHARS]
                    + "...[TRUNCATED]"
                )

            selected.append(
                {
                    "ID": example["ID"],
                    "Creation time": example[
                        "Creation time"
                    ],
                    "actual": example["actual"],
                    "predicted": example["predicted"],
                    "Summary": example["Summary"],
                    "Description": description,
                    "text_length": example[
                        "text_length"
                    ],
                }
            )

        inspection["pairs"][pair] = selected

    OUTPUT_PATH.write_text(
        json.dumps(
            inspection,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("ERROR_PAIR_COUNTS")

    for pair in ERROR_PAIRS:
        count = len(
            inspection["pairs"][pair]
        )
        print(f"{pair}_EXAMPLES={count}")

    print()

    for pair in ERROR_PAIRS:
        examples = inspection["pairs"][pair]

        print("=" * 80)
        print(pair)
        print("=" * 80)

        if not examples:
            print("NO_EXAMPLES")
            continue

        for index, example in enumerate(
            examples,
            start=1,
        ):
            print()
            print(f"EXAMPLE_{index}")
            print(f"ID={example['ID']}")
            print(
                f"CREATION={example['Creation time']}"
            )
            print(
                f"ACTUAL={example['actual']}"
            )
            print(
                f"PREDICTED={example['predicted']}"
            )
            print(
                f"TEXT_LENGTH={example['text_length']}"
            )
            print(
                f"SUMMARY={example['Summary']}"
            )
            print(
                "DESCRIPTION="
                f"{example['Description']}"
            )

    print()
    print(f"OUTPUT={OUTPUT_PATH}")
    print("TEST_USED=False")
    print("RETRAINED=False")
    print("RAW_MOZILLA_ACCESSED=False")
    print("STATUS=ERROR_INSPECTION_COMPLETE")
    print("T3_MOD_013_COMPLETE")


if __name__ == "__main__":
    main()