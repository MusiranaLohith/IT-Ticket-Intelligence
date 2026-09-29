from pathlib import Path
import pandas as pd


# ============================================================
# T10 / OP-025
# T2 Priority-Transition & Error-Distance Analysis
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

# Ordinal representation of the observed priority labels.
# This is used only to characterize transition distance.
PRIORITY_ORDER = {
    "P1": 1,
    "P2": 2,
    "P3": 3,
    "P4": 4,
    "P5": 5,
}


def main():
    print("=" * 70)
    print("T10 / OP-025 — T2 PRIORITY-TRANSITION & ERROR-DISTANCE ANALYSIS")
    print("=" * 70)

    print("\n[1] Input artifact")
    print(f"Path: {INPUT_PATH}")

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input artifact not found: {INPUT_PATH}"
        )

    total_rows = 0
    correct_rows = 0
    incorrect_rows = 0

    distance_counts = {}
    direction_counts = {}

    transition_counts = {}

    unknown_priority_rows = 0

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

            if actual == predicted:
                correct_rows += 1
                continue

            incorrect_rows += 1

            # Track exact transition.
            transition_key = (actual, predicted)
            transition_counts[transition_key] = (
                transition_counts.get(transition_key, 0) + 1
            )

            if (
                actual not in PRIORITY_ORDER
                or predicted not in PRIORITY_ORDER
            ):
                unknown_priority_rows += 1
                continue

            actual_num = PRIORITY_ORDER[actual]
            predicted_num = PRIORITY_ORDER[predicted]

            distance = abs(predicted_num - actual_num)

            distance_counts[distance] = (
                distance_counts.get(distance, 0) + 1
            )

            if predicted_num < actual_num:
                direction = "predicted_higher_priority"
            else:
                direction = "predicted_lower_priority"

            direction_counts[direction] = (
                direction_counts.get(direction, 0) + 1
            )

    # --------------------------------------------------------
    # [3] Population summary
    # --------------------------------------------------------
    print("\n[3] Population summary")

    accuracy = (
        correct_rows / total_rows
        if total_rows
        else float("nan")
    )

    error_rate = (
        incorrect_rows / total_rows
        if total_rows
        else float("nan")
    )

    print(f"Rows: {total_rows:,}")
    print(f"Correct: {correct_rows:,}")
    print(f"Incorrect: {incorrect_rows:,}")
    print(f"Accuracy: {accuracy:.6f}")
    print(f"Error rate: {error_rate:.6f}")

    # --------------------------------------------------------
    # [4] Error-distance distribution
    # --------------------------------------------------------
    print("\n[4] Error-distance distribution")

    print(
        f"\n{'Distance':>12} "
        f"{'Errors':>12} "
        f"{'Share of Errors':>18}"
    )

    print("-" * 48)

    for distance in sorted(distance_counts):
        count = distance_counts[distance]

        share = (
            count / incorrect_rows
            if incorrect_rows
            else float("nan")
        )

        print(
            f"{distance:>12} "
            f"{count:>12,} "
            f"{share:>18.6f}"
        )

    # --------------------------------------------------------
    # [5] Adjacent vs non-adjacent errors
    # --------------------------------------------------------
    adjacent_errors = distance_counts.get(1, 0)

    non_adjacent_errors = sum(
        count
        for distance, count in distance_counts.items()
        if distance >= 2
    )

    adjacent_share = (
        adjacent_errors / incorrect_rows
        if incorrect_rows
        else float("nan")
    )

    non_adjacent_share = (
        non_adjacent_errors / incorrect_rows
        if incorrect_rows
        else float("nan")
    )

    print("\n[5] Adjacent vs non-adjacent errors")

    print(f"Adjacent-priority errors: {adjacent_errors:,}")
    print(f"Adjacent error share: {adjacent_share:.6f}")

    print(f"Non-adjacent errors: {non_adjacent_errors:,}")
    print(f"Non-adjacent error share: {non_adjacent_share:.6f}")

    # --------------------------------------------------------
    # [6] Direction of error
    # --------------------------------------------------------
    print("\n[6] Direction of priority transition")

    higher = direction_counts.get(
        "predicted_higher_priority",
        0,
    )

    lower = direction_counts.get(
        "predicted_lower_priority",
        0,
    )

    print(
        "Predicted higher priority than actual: "
        f"{higher:,}"
    )

    print(
        "Predicted lower priority than actual: "
        f"{lower:,}"
    )

    if incorrect_rows:
        print(
            "Higher-priority prediction share: "
            f"{higher / incorrect_rows:.6f}"
        )

        print(
            "Lower-priority prediction share: "
            f"{lower / incorrect_rows:.6f}"
        )

    # --------------------------------------------------------
    # [7] Exact transition table
    # --------------------------------------------------------
    print("\n[7] Exact error transitions")

    print(
        f"\n{'Rank':>6} "
        f"{'Actual':>10} "
        f"{'Predicted':>12} "
        f"{'Errors':>12} "
        f"{'Distance':>12} "
        f"{'Direction':>30}"
    )

    print("-" * 88)

    ranked_transitions = sorted(
        transition_counts.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    for rank, ((actual, predicted), count) in enumerate(
        ranked_transitions,
        start=1,
    ):
        if (
            actual in PRIORITY_ORDER
            and predicted in PRIORITY_ORDER
        ):
            distance = abs(
                PRIORITY_ORDER[predicted]
                - PRIORITY_ORDER[actual]
            )

            if PRIORITY_ORDER[predicted] < PRIORITY_ORDER[actual]:
                direction = "predicted_higher_priority"
            else:
                direction = "predicted_lower_priority"
        else:
            distance = "NA"
            direction = "unknown_priority"

        print(
            f"{rank:>6} "
            f"{actual:>10} "
            f"{predicted:>12} "
            f"{count:>12,} "
            f"{str(distance):>12} "
            f"{direction:>30}"
        )

    # --------------------------------------------------------
    # [8] Data-quality check
    # --------------------------------------------------------
    print("\n[8] Priority-label integrity")

    print(
        f"Rows with unknown priority labels: "
        f"{unknown_priority_rows:,}"
    )

    if unknown_priority_rows == 0:
        print("All observed error transitions use P1–P5 labels.")
    else:
        print(
            "WARNING: Some error transitions could not be "
            "assigned ordinal distance."
        )

    # --------------------------------------------------------
    # [9] Operating-region boundary
    # --------------------------------------------------------
    print("\n[9] Operating-region boundary")

    print(
        "This analysis characterizes observed priority "
        "transitions and ordinal error distance only."
    )

    print(
        "It does NOT define acceptable or unacceptable "
        "priority errors."
    )

    print(
        "It does NOT select an automation threshold, "
        "confidence boundary, or universal T10 score."
    )

    print(
        "It does NOT assign AUTOMATE, HUMAN_REVIEW, or "
        "DEFER_INSUFFICIENT_EVIDENCE states."
    )

    print(
        "Any future operating-region policy requires "
        "separate empirical validation."
    )

    # --------------------------------------------------------
    # [10] Final status
    # --------------------------------------------------------
    print("\n[10] OP-025 status")

    if total_rows == 0:
        print("STATUS: FAIL — no prediction rows found")
        raise RuntimeError("No prediction rows found.")

    if unknown_priority_rows > 0:
        print(
            "STATUS: PASS WITH DATA-QUALITY LIMITATION"
        )
    else:
        print("STATUS: PASS")

    print(
        "Native T2 priority-transition evidence "
        "successfully characterized."
    )

    print("No automation policy was selected.")

    print("\n" + "=" * 70)
    print("END OF T10 / OP-025")
    print("=" * 70)


if __name__ == "__main__":
    main()