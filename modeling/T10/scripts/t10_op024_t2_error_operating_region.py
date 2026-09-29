from pathlib import Path
import pandas as pd


# ============================================================
# T10 / OP-024
# T2 Error & Operating-Region Analysis
# ============================================================

INPUT_PATH = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/"
    "modeling/T2/analysis/t2_final_test_predictions.csv"
)

CHUNK_SIZE = 1000

REQUIRED_COLUMNS = [
    "ID",
    "actual_priority",
    "predicted_priority",
]


def main():
    print("=" * 70)
    print("T10 / OP-024 — T2 ERROR & OPERATING-REGION ANALYSIS")
    print("=" * 70)

    print("\n[1] Input artifact")
    print(f"Path: {INPUT_PATH}")

    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input artifact not found: {INPUT_PATH}")

    # --------------------------------------------------------
    # Accumulators
    # --------------------------------------------------------
    total_rows = 0
    total_correct = 0
    total_incorrect = 0

    actual_counts = {}
    predicted_counts = {}
    confusion = {}

    # --------------------------------------------------------
    # [2] Chunked read
    # --------------------------------------------------------
    print("\n[2] Reading predictions in chunks...")

    for chunk in pd.read_csv(
        INPUT_PATH,
        usecols=REQUIRED_COLUMNS,
        chunksize=CHUNK_SIZE,
    ):
        total_rows += len(chunk)

        correct_mask = (
            chunk["actual_priority"]
            == chunk["predicted_priority"]
        )

        total_correct += int(correct_mask.sum())
        total_incorrect += int((~correct_mask).sum())

        # Actual-class support
        for value, count in chunk["actual_priority"].value_counts().items():
            actual_counts[value] = actual_counts.get(value, 0) + int(count)

        # Predicted-class support
        for value, count in chunk["predicted_priority"].value_counts().items():
            predicted_counts[value] = (
                predicted_counts.get(value, 0) + int(count)
            )

        # Confusion pairs
        pair_counts = (
            chunk.groupby(
                ["actual_priority", "predicted_priority"],
                dropna=False,
            )
            .size()
        )

        for (actual, predicted), count in pair_counts.items():
            key = (actual, predicted)
            confusion[key] = confusion.get(key, 0) + int(count)

    # --------------------------------------------------------
    # [3] Basic population
    # --------------------------------------------------------
    print("\n[3] Population summary")

    accuracy = (
        total_correct / total_rows
        if total_rows > 0
        else float("nan")
    )

    error_rate = (
        total_incorrect / total_rows
        if total_rows > 0
        else float("nan")
    )

    print(f"Rows: {total_rows:,}")
    print(f"Correct: {total_correct:,}")
    print(f"Incorrect: {total_incorrect:,}")
    print(f"Accuracy: {accuracy:.6f}")
    print(f"Error rate: {error_rate:.6f}")

    # --------------------------------------------------------
    # [4] Actual-class error concentration
    # --------------------------------------------------------
    print("\n[4] Error concentration by actual priority")

    priorities = sorted(
        set(actual_counts.keys()) | set(predicted_counts.keys()),
        key=lambda x: str(x),
    )

    actual_error_table = []

    for priority in priorities:
        support = actual_counts.get(priority, 0)
        correct = confusion.get((priority, priority), 0)
        incorrect = support - correct

        class_accuracy = (
            correct / support
            if support > 0
            else float("nan")
        )

        class_error_rate = (
            incorrect / support
            if support > 0
            else float("nan")
        )

        error_share = (
            incorrect / total_incorrect
            if total_incorrect > 0
            else float("nan")
        )

        actual_error_table.append(
            (
                priority,
                support,
                correct,
                incorrect,
                class_accuracy,
                class_error_rate,
                error_share,
            )
        )

    print(
        "\n"
        f"{'Actual':>10} "
        f"{'Support':>10} "
        f"{'Correct':>10} "
        f"{'Incorrect':>10} "
        f"{'Accuracy':>12} "
        f"{'ErrorRate':>12} "
        f"{'ErrorShare':>12}"
    )

    print("-" * 82)

    for row in actual_error_table:
        (
            priority,
            support,
            correct,
            incorrect,
            class_accuracy,
            class_error_rate,
            error_share,
        ) = row

        print(
            f"{str(priority):>10} "
            f"{support:>10,} "
            f"{correct:>10,} "
            f"{incorrect:>10,} "
            f"{class_accuracy:>12.6f} "
            f"{class_error_rate:>12.6f} "
            f"{error_share:>12.6f}"
        )

    # --------------------------------------------------------
    # [5] Predicted-class concentration
    # --------------------------------------------------------
    print("\n[5] Prediction concentration")

    print(
        "\n"
        f"{'Predicted':>12} "
        f"{'Count':>12} "
        f"{'Share':>12}"
    )

    print("-" * 40)

    for priority in priorities:
        count = predicted_counts.get(priority, 0)
        share = count / total_rows if total_rows > 0 else float("nan")

        print(
            f"{str(priority):>12} "
            f"{count:>12,} "
            f"{share:>12.6f}"
        )

    # --------------------------------------------------------
    # [6] Confusion matrix
    # --------------------------------------------------------
    print("\n[6] Confusion matrix")

    print(
        "\nRows = actual priority"
        "\nColumns = predicted priority\n"
    )

    header = f"{'Actual\\Pred':>14}"

    for predicted in priorities:
        header += f"{str(predicted):>12}"

    print(header)
    print("-" * (14 + 12 * len(priorities)))

    for actual in priorities:
        row = f"{str(actual):>14}"

        for predicted in priorities:
            count = confusion.get((actual, predicted), 0)
            row += f"{count:>12,}"

        print(row)

    # --------------------------------------------------------
    # [7] Top error pairs
    # --------------------------------------------------------
    print("\n[7] Most frequent error pairs")

    error_pairs = [
        (actual, predicted, count)
        for (actual, predicted), count in confusion.items()
        if actual != predicted
    ]

    error_pairs.sort(
        key=lambda x: x[2],
        reverse=True,
    )

    print(
        "\n"
        f"{'Rank':>6} "
        f"{'Actual':>10} "
        f"{'Predicted':>12} "
        f"{'Errors':>12} "
        f"{'ErrorShare':>12}"
    )

    print("-" * 58)

    for rank, (actual, predicted, count) in enumerate(
        error_pairs,
        start=1,
    ):
        share = (
            count / total_incorrect
            if total_incorrect > 0
            else float("nan")
        )

        print(
            f"{rank:>6} "
            f"{str(actual):>10} "
            f"{str(predicted):>12} "
            f"{count:>12,} "
            f"{share:>12.6f}"
        )

    # --------------------------------------------------------
    # [8] Operating-region evidence status
    # --------------------------------------------------------
    print("\n[8] Operating-region evidence assessment")

    print(
        "T2 error concentration is characterized from the native "
        "held-out predictions."
    )

    print(
        "This operation does NOT select an automation threshold, "
        "confidence boundary, or universal T10 score."
    )

    print(
        "This operation does NOT assign ticket-level AUTOMATE, "
        "HUMAN_REVIEW, or DEFER_INSUFFICIENT_EVIDENCE states."
    )

    print(
        "A potential review/defer operating region remains an "
        "empirical question requiring additional evidence."
    )

    # --------------------------------------------------------
    # [9] Final status
    # --------------------------------------------------------
    print("\n[9] OP-024 status")

    if total_rows == 0:
        print("STATUS: FAIL — no prediction rows found")
        raise RuntimeError("No prediction rows found.")

    print("STATUS: PASS")
    print("Native T2 error concentration successfully characterized.")
    print("No automation policy was selected.")

    print("\n" + "=" * 70)
    print("END OF T10 / OP-024")
    print("=" * 70)


if __name__ == "__main__":
    main()