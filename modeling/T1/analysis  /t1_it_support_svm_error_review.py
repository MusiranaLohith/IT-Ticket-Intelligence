from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(
    "/"
)

INPUT_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "analysis"
    / "t1_it_support_svm_errors.json"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "analysis"
    / "t1_it_support_svm_error_review.txt"
)


PAIR_ORDER = [
    ("Active Directory", "Software"),
    ("Active Directory", "Support general"),
    ("O365", "Software"),
    ("O365", "Support general"),
    ("O365", "Active Directory"),
    ("Software", "Support general"),
    ("Software", "Fileservice"),
    ("Computer-Services", "Support general"),
    ("Computer-Services", "Fileservice"),
    ("Fileservice", "Software"),
    ("Active Directory", "Fileservice"),
]


def main():

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input artifact not found: {INPUT_PATH}"
        )

    with INPUT_PATH.open(
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    errors = data.get("errors", [])

    if not errors:
        raise RuntimeError(
            "No misclassified records found."
        )

    sections = []

    for actual, predicted in PAIR_ORDER:

        matching = [
            error
            for error in errors
            if error["actual"] == actual
            and error["predicted"] == predicted
        ]

        if not matching:
            continue

        sections.append(
            "\n"
            + "=" * 80
            + "\n"
            + f"ACTUAL: {actual}\n"
            + f"PREDICTED: {predicted}\n"
            + f"COUNT: {len(matching)}\n"
            + "=" * 80
            + "\n"
        )

        for index, error in enumerate(
            matching,
            start=1,
        ):

            sections.append(
                f"\nCASE {index}\n"
                f"ID: {error['id']}\n"
                f"ACTUAL: {error['actual']}\n"
                f"PREDICTED: {error['predicted']}\n"
                f"SOURCE_PARTITION: "
                f"{error['source_partition']}\n"
                f"SOURCE_ROW_X: "
                f"{error['source_row_x']}\n"
                f"SOURCE_ROW_Y: "
                f"{error['source_row_y']}\n"
                f"TEXT:\n"
                f"{error['text']}\n"
            )

    # Include any unexpected error pair at the end.
    known_pairs = set(PAIR_ORDER)

    unexpected = [
        error
        for error in errors
        if (
            error["actual"],
            error["predicted"],
        ) not in known_pairs
    ]

    if unexpected:

        sections.append(
            "\n"
            + "=" * 80
            + "\n"
            + "OTHER ERROR PAIRS\n"
            + "=" * 80
            + "\n"
        )

        for index, error in enumerate(
            unexpected,
            start=1,
        ):

            sections.append(
                f"\nCASE {index}\n"
                f"ID: {error['id']}\n"
                f"ACTUAL: {error['actual']}\n"
                f"PREDICTED: {error['predicted']}\n"
                f"SOURCE_PARTITION: "
                f"{error['source_partition']}\n"
                f"SOURCE_ROW_X: "
                f"{error['source_row_x']}\n"
                f"SOURCE_ROW_Y: "
                f"{error['source_row_y']}\n"
                f"TEXT:\n"
                f"{error['text']}\n"
            )

    header = (
        "IT SUPPORT T1 — LINEAR SVM ERROR REVIEW\n"
        "\n"
        f"TOTAL EVALUATION ERRORS: {len(errors)}\n"
        "\n"
        "Review purpose:\n"
        "Inspect actual misclassifications without modifying\n"
        "labels, splits, source data, or model artifacts.\n"
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as f:

        f.write(
            header
            + "\n".join(sections)
        )

    print(
        "IT_SUPPORT_T1_SVM_ERROR_REVIEW_COMPLETE"
    )

    print(
        f"MISCLASSIFIED_RECORDS={len(errors)}"
    )

    print(
        f"OUTPUT_PATH={OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()