"""
T10 / OP-023

T2 Native Empirical Validation

Purpose
-------
Evaluate the existing T2 final test prediction artifact using the
native Priority Prediction semantics.

This operation does NOT:
    - establish an automation threshold
    - assign policy states
    - create a universal T10 score
    - combine task outputs
    - modify the source artifact

The CSV is processed in chunks to minimize RAM usage.
"""

from pathlib import Path
from collections import Counter


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_PREDICTIONS = (
    PROJECT_ROOT
    / "modeling"
    / "T2"
    / "analysis"
    / "t2_final_test_predictions.csv"
)

CHUNK_SIZE = 1000

REQUIRED_COLUMNS = {
    "ID",
    "Creation time",
    "actual_priority",
    "predicted_priority",
}


def main():

    print("=" * 82)
    print("T10 / OP-023 — T2 NATIVE EMPIRICAL VALIDATION")
    print("=" * 82)

    if not T2_PREDICTIONS.exists():
        print()
        print("ERROR: T2 prediction artifact not found.")
        print(T2_PREDICTIONS)
        return 1

    print()
    print("Artifact:")
    print(T2_PREDICTIONS)

    # Import pandas only after artifact existence is confirmed.
    import pandas as pd

    # ------------------------------------------------------------
    # Read header only
    # ------------------------------------------------------------

    header = pd.read_csv(
        T2_PREDICTIONS,
        nrows=0,
    )

    columns = set(header.columns)

    print()
    print("=" * 82)
    print("1. SCHEMA CHECK")
    print("=" * 82)

    print(
        f"Columns : {list(header.columns)}"
    )

    missing_columns = (
        REQUIRED_COLUMNS - columns
    )

    if missing_columns:

        print(
            f"ERROR: Missing columns: {sorted(missing_columns)}"
        )

        return 1

    print(
        "PASS : required columns present"
    )

    # ------------------------------------------------------------
    # Chunked empirical evaluation
    # ------------------------------------------------------------

    total_rows = 0
    null_ids = 0
    null_actual = 0
    null_predicted = 0

    unique_ids = set()

    actual_counts = Counter()
    predicted_counts = Counter()

    correct_counts = Counter()
    incorrect_counts = Counter()

    confusion = Counter()

    # Only load required columns.
    usecols = [
        "ID",
        "actual_priority",
        "predicted_priority",
    ]

    print()
    print("=" * 82)
    print("2. CHUNKED EMPIRICAL EVALUATION")
    print("=" * 82)

    for chunk in pd.read_csv(
        T2_PREDICTIONS,
        usecols=usecols,
        chunksize=CHUNK_SIZE,
    ):

        total_rows += len(chunk)

        null_ids += int(
            chunk["ID"].isna().sum()
        )

        null_actual += int(
            chunk["actual_priority"].isna().sum()
        )

        null_predicted += int(
            chunk["predicted_priority"].isna().sum()
        )

        unique_ids.update(
            chunk["ID"].dropna().tolist()
        )

        for actual in chunk["actual_priority"]:

            if pd.notna(actual):
                actual_counts[str(actual)] += 1

        for predicted in chunk["predicted_priority"]:

            if pd.notna(predicted):
                predicted_counts[str(predicted)] += 1

        valid = chunk[
            chunk["actual_priority"].notna()
            & chunk["predicted_priority"].notna()
        ]

        for actual, predicted in zip(
            valid["actual_priority"],
            valid["predicted_priority"],
        ):

            actual = str(actual)
            predicted = str(predicted)

            confusion[(actual, predicted)] += 1

            if actual == predicted:
                correct_counts[actual] += 1
            else:
                incorrect_counts[actual] += 1

    valid_rows = (
        total_rows
        - null_actual
        - null_predicted
    )

    correct_total = sum(
        correct_counts.values()
    )

    incorrect_total = sum(
        incorrect_counts.values()
    )

    accuracy = (
        correct_total / valid_rows
        if valid_rows
        else 0.0
    )

    # ------------------------------------------------------------
    # Results
    # ------------------------------------------------------------

    print()
    print("=" * 82)
    print("3. POPULATION INTEGRITY")
    print("=" * 82)

    print(
        f"Total rows       : {total_rows:,}"
    )

    print(
        f"Unique IDs       : {len(unique_ids):,}"
    )

    print(
        f"Null IDs         : {null_ids:,}"
    )

    print(
        f"Null actual      : {null_actual:,}"
    )

    print(
        f"Null predicted   : {null_predicted:,}"
    )

    print()
    print("=" * 82)
    print("4. NATIVE PRIORITY CORRECTNESS")
    print("=" * 82)

    print(
        f"Valid evaluated rows : {valid_rows:,}"
    )

    print(
        f"Correct predictions  : {correct_total:,}"
    )

    print(
        f"Incorrect predictions: {incorrect_total:,}"
    )

    print(
        f"Accuracy             : {accuracy:.6f}"
    )

    print()
    print("=" * 82)
    print("5. ACTUAL CLASS SUPPORT")
    print("=" * 82)

    for label in sorted(actual_counts):

        print(
            f"{label:20s} : "
            f"{actual_counts[label]:,}"
        )

    print()
    print("=" * 82)
    print("6. PER-CLASS CORRECTNESS")
    print("=" * 82)

    for label in sorted(actual_counts):

        support = actual_counts[label]

        correct = correct_counts[label]

        class_accuracy = (
            correct / support
            if support
            else 0.0
        )

        print(
            f"{label:20s} "
            f"support={support:,} "
            f"correct={correct:,} "
            f"accuracy={class_accuracy:.6f}"
        )

    print()
    print("=" * 82)
    print("7. CONFUSION MATRIX")
    print("=" * 82)

    labels = sorted(
        set(actual_counts)
        | set(predicted_counts)
    )

    print(
        "actual -> predicted"
    )

    for actual in labels:

        for predicted in labels:

            count = confusion[
                (actual, predicted)
            ]

            if count:
                print(
                    f"{actual:20s} -> "
                    f"{predicted:20s} : {count:,}"
                )

    print()
    print("=" * 82)
    print("8. POLICY BOUNDARY")
    print("=" * 82)

    print(
        "This operation establishes native T2 predictive correctness only."
    )

    print(
        "It does NOT establish an automation threshold."
    )

    print(
        "It does NOT assign AUTOMATE, HUMAN_REVIEW, or "
        "DEFER_INSUFFICIENT_EVIDENCE states."
    )

    print(
        "It does NOT establish universal T10 confidence or risk."
    )

    print(
        "It does NOT combine T2 with other task outputs."
    )

    print()
    print("=" * 82)
    print("9. FINAL RESULT")
    print("=" * 82)

    integrity_pass = (
        total_rows == 4425
        and len(unique_ids) == 4425
        and null_ids == 0
        and null_actual == 0
        and null_predicted == 0
        and valid_rows == 4425
    )

    if integrity_pass:

        print(
            "Population integrity : PASS"
        )

        print(
            "OP-023 STATUS : PASS"
        )

        print(
            "Native T2 empirical correctness successfully evaluated."
        )

    else:

        print(
            "Population integrity : FAIL"
        )

        print(
            "OP-023 STATUS : FAIL"
        )

    return 0 if integrity_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())