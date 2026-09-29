from pathlib import Path
import pandas as pd


# ============================================================
# T10 / OP-026
# T2 Prediction-Class Reliability Analysis
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

PRIORITIES = ["P1", "P2", "P3", "P4", "P5"]


def main():
    print("=" * 70)
    print("T10 / OP-026 — T2 PREDICTION-CLASS RELIABILITY ANALYSIS")
    print("=" * 70)

    print("\n[1] Input artifact")
    print(f"Path: {INPUT_PATH}")

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input artifact not found: {INPUT_PATH}"
        )

    total_rows = 0
    total_correct = 0
    total_incorrect = 0

    predicted_counts = {}
    predicted_correct = {}
    predicted_incorrect = {}

    # For each predicted class, retain the actual-class
    # distribution of the errors.
    predicted_error_actual_counts = {}

    unknown_predicted = 0
    unknown_actual = 0

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

        for actual, predicted in zip(
            chunk["actual_priority"],
            chunk["predicted_priority"],
        ):
            actual = str(actual)
            predicted = str(predicted)

            predicted_counts[predicted] = (
                predicted_counts.get(predicted, 0) + 1
            )

            if predicted not in PRIORITIES:
                unknown_predicted += 1

            if actual not in PRIORITIES:
                unknown_actual += 1

            if actual == predicted:
                total_correct += 1

                predicted_correct[predicted] = (
                    predicted_correct.get(predicted, 0) + 1
                )
            else:
                total_incorrect += 1

                predicted_incorrect[predicted] = (
                    predicted_incorrect.get(predicted, 0) + 1
                )

                if predicted not in predicted_error_actual_counts:
                    predicted_error_actual_counts[predicted] = {}

                actual_counts = predicted_error_actual_counts[predicted]

                actual_counts[actual] = (
                    actual_counts.get(actual, 0) + 1
                )

    # --------------------------------------------------------
    # [3] Population summary
    # --------------------------------------------------------
    print("\n[3] Population summary")

    accuracy = (
        total_correct / total_rows
        if total_rows
        else float("nan")
    )

    error_rate = (
        total_incorrect / total_rows
        if total_rows
        else float("nan")
    )

    print(f"Rows: {total_rows:,}")
    print(f"Correct: {total_correct:,}")
    print(f"Incorrect: {total_incorrect:,}")
    print(f"Accuracy: {accuracy:.6f}")
    print(f"Error rate: {error_rate:.6f}")

    # --------------------------------------------------------
    # [4] Prediction-class reliability
    # --------------------------------------------------------
    print("\n[4] Reliability of each predicted priority")

    print(
        "\n"
        f"{'Predicted':>12} "
        f"{'Predictions':>14} "
        f"{'Correct':>12} "
        f"{'Incorrect':>12} "
        f"{'CorrectRate':>14} "
        f"{'ErrorRate':>12} "
        f"{'ErrorShare':>12}"
    )

    print("-" * 92)

    for priority in PRIORITIES:
        predictions = predicted_counts.get(priority, 0)
        correct = predicted_correct.get(priority, 0)
        incorrect = predicted_incorrect.get(priority, 0)

        correct_rate = (
            correct / predictions
            if predictions
            else float("nan")
        )

        class_error_rate = (
            incorrect / predictions
            if predictions
            else float("nan")
        )

        error_share = (
            incorrect / total_incorrect
            if total_incorrect
            else float("nan")
        )

        print(
            f"{priority:>12} "
            f"{predictions:>14,} "
            f"{correct:>12,} "
            f"{incorrect:>12,} "
            f"{correct_rate:>14.6f} "
            f"{class_error_rate:>12.6f} "
            f"{error_share:>12.6f}"
        )

    # --------------------------------------------------------
    # [5] Error composition behind each prediction class
    # --------------------------------------------------------
    print("\n[5] Actual-priority composition of errors")

    for predicted in PRIORITIES:
        predictions = predicted_counts.get(predicted, 0)
        incorrect = predicted_incorrect.get(predicted, 0)

        print(f"\nPredicted {predicted}")
        print("-" * 50)
        print(f"Total predictions: {predictions:,}")
        print(f"Incorrect predictions: {incorrect:,}")

        if incorrect == 0:
            print("No errors for this predicted class.")
            continue

        print(
            f"\n{'Actual':>12} "
            f"{'Errors':>12} "
            f"{'Share of Class Errors':>24}"
        )

        print("-" * 52)

        actual_errors = predicted_error_actual_counts.get(
            predicted,
            {},
        )

        ranked_actual_errors = sorted(
            actual_errors.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        for actual, count in ranked_actual_errors:
            share = count / incorrect

            print(
                f"{actual:>12} "
                f"{count:>12,} "
                f"{share:>24.6f}"
            )

    # --------------------------------------------------------
    # [6] Overall error concentration by predicted class
    # --------------------------------------------------------
    print("\n[6] Error concentration by predicted priority")

    ranked_prediction_errors = sorted(
        [
            (
                predicted,
                predicted_incorrect.get(predicted, 0),
            )
            for predicted in PRIORITIES
        ],
        key=lambda item: item[1],
        reverse=True,
    )

    print(
        f"\n{'Rank':>6} "
        f"{'Predicted':>12} "
        f"{'Errors':>12} "
        f"{'Share of Errors':>18}"
    )

    print("-" * 52)

    for rank, (predicted, errors) in enumerate(
        ranked_prediction_errors,
        start=1,
    ):
        share = (
            errors / total_incorrect
            if total_incorrect
            else float("nan")
        )

        print(
            f"{rank:>6} "
            f"{predicted:>12} "
            f"{errors:>12,} "
            f"{share:>18.6f}"
        )

    # --------------------------------------------------------
    # [7] Data-quality checks
    # --------------------------------------------------------
    print("\n[7] Priority-label integrity")

    print(
        f"Unknown predicted-priority rows: "
        f"{unknown_predicted:,}"
    )

    print(
        f"Unknown actual-priority rows: "
        f"{unknown_actual:,}"
    )

    if unknown_predicted == 0 and unknown_actual == 0:
        print("All observed priority labels are P1–P5.")
    else:
        print(
            "WARNING: Unknown priority labels were observed."
        )

    # --------------------------------------------------------
    # [8] Operating-region boundary
    # --------------------------------------------------------
    print("\n[8] Operating-region boundary")

    print(
        "This operation characterizes empirical correctness "
        "conditional on the predicted priority."
    )

    print(
        "It does NOT establish that any predicted class is "
        "safe or unsafe for automation."
    )

    print(
        "It does NOT create a confidence threshold, "
        "automation threshold, or universal T10 score."
    )

    print(
        "It does NOT assign ticket-level AUTOMATE, "
        "HUMAN_REVIEW, or DEFER_INSUFFICIENT_EVIDENCE states."
    )

    print(
        "Prediction-class reliability is descriptive evidence "
        "for later empirical policy validation."
    )

    # --------------------------------------------------------
    # [9] Final status
    # --------------------------------------------------------
    print("\n[9] OP-026 status")

    if total_rows == 0:
        print("STATUS: FAIL — no prediction rows found")
        raise RuntimeError("No prediction rows found.")

    if unknown_predicted > 0 or unknown_actual > 0:
        print("STATUS: PASS WITH DATA-QUALITY LIMITATION")
    else:
        print("STATUS: PASS")

    print(
        "T2 prediction-class reliability successfully "
        "characterized."
    )

    print("No automation policy was selected.")

    print("\n" + "=" * 70)
    print("END OF T10 / OP-026")
    print("=" * 70)


if __name__ == "__main__":
    main()