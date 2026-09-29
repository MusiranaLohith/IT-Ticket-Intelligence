from pathlib import Path
import pandas as pd


# ============================================================
# T10 / OP-028
# T2 Correctness by Priority-Transition Distance
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

PRIORITY_ORDER = {
    "P1": 1,
    "P2": 2,
    "P3": 3,
    "P4": 4,
    "P5": 5,
}


def main():
    print("=" * 70)
    print(
        "T10 / OP-028 — T2 CORRECTNESS BY "
        "PRIORITY-TRANSITION DISTANCE"
    )
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

    # Per-actual-priority counts.
    class_total = {}
    class_correct = {}
    class_distance_counts = {}

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

            class_total[actual] = (
                class_total.get(actual, 0) + 1
            )

            if actual not in PRIORITY_ORDER:
                unknown_priority_rows += 1
                continue

            if predicted not in PRIORITY_ORDER:
                unknown_priority_rows += 1
                continue

            if actual == predicted:
                total_correct += 1

                class_correct[actual] = (
                    class_correct.get(actual, 0) + 1
                )

            else:
                total_incorrect += 1

                distance = abs(
                    PRIORITY_ORDER[predicted]
                    - PRIORITY_ORDER[actual]
                )

                if actual not in class_distance_counts:
                    class_distance_counts[actual] = {}

                class_distance_counts[actual][distance] = (
                    class_distance_counts[actual].get(distance, 0)
                    + 1
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
    # [4] Per-class correctness by distance
    # --------------------------------------------------------
    print("\n[4] Correctness and error distance by actual priority")

    print(
        "\n"
        f"{'Actual':>8} "
        f"{'Support':>10} "
        f"{'Correct':>10} "
        f"{'Dist1':>10} "
        f"{'Dist2':>10} "
        f"{'Dist3':>10} "
        f"{'Dist4':>10} "
        f"{'Errors':>10}"
    )

    print("-" * 88)

    for priority in PRIORITIES:
        support = class_total.get(priority, 0)
        correct = class_correct.get(priority, 0)

        distance_counts = class_distance_counts.get(
            priority,
            {},
        )

        dist1 = distance_counts.get(1, 0)
        dist2 = distance_counts.get(2, 0)
        dist3 = distance_counts.get(3, 0)
        dist4 = distance_counts.get(4, 0)

        errors = dist1 + dist2 + dist3 + dist4

        print(
            f"{priority:>8} "
            f"{support:>10,} "
            f"{correct:>10,} "
            f"{dist1:>10,} "
            f"{dist2:>10,} "
            f"{dist3:>10,} "
            f"{dist4:>10,} "
            f"{errors:>10,}"
        )

    # --------------------------------------------------------
    # [5] Per-class error-distance composition
    # --------------------------------------------------------
    print("\n[5] Error-distance composition within each actual priority")

    for priority in PRIORITIES:
        support = class_total.get(priority, 0)
        correct = class_correct.get(priority, 0)

        errors = support - correct

        print(f"\nActual {priority}")
        print("-" * 52)

        print(f"Support: {support:,}")
        print(f"Correct: {correct:,}")
        print(f"Incorrect: {errors:,}")

        if errors == 0:
            print("No errors for this actual priority.")
            continue

        distance_counts = class_distance_counts.get(
            priority,
            {},
        )

        print(
            f"\n{'Distance':>12} "
            f"{'Errors':>12} "
            f"{'Share of Class Errors':>24}"
        )

        print("-" * 52)

        for distance in sorted(distance_counts):
            count = distance_counts[distance]
            share = count / errors

            print(
                f"{distance:>12} "
                f"{count:>12,} "
                f"{share:>24.6f}"
            )

    # --------------------------------------------------------
    # [6] Global distance composition
    # --------------------------------------------------------
    print("\n[6] Global error-distance composition")

    global_distance_counts = {}

    for priority in PRIORITIES:
        distance_counts = class_distance_counts.get(
            priority,
            {},
        )

        for distance, count in distance_counts.items():
            global_distance_counts[distance] = (
                global_distance_counts.get(distance, 0)
                + count
            )

    print(
        f"\n{'Distance':>12} "
        f"{'Errors':>12} "
        f"{'Share of Errors':>18}"
    )

    print("-" * 48)

    for distance in sorted(global_distance_counts):
        count = global_distance_counts[distance]

        share = (
            count / total_incorrect
            if total_incorrect
            else float("nan")
        )

        print(
            f"{distance:>12} "
            f"{count:>12,} "
            f"{share:>18.6f}"
        )

    # --------------------------------------------------------
    # [7] Correct vs distance-1 vs distance-2+
    # --------------------------------------------------------
    distance_1 = global_distance_counts.get(1, 0)

    distance_2_plus = sum(
        count
        for distance, count in global_distance_counts.items()
        if distance >= 2
    )

    print("\n[7] Correctness / transition-distance summary")

    print(f"Correct predictions: {total_correct:,}")
    print(f"Distance-1 errors: {distance_1:,}")
    print(f"Distance-2+ errors: {distance_2_plus:,}")

    print(
        f"Correct share of all rows: "
        f"{total_correct / total_rows:.6f}"
    )

    print(
        f"Distance-1 share of all rows: "
        f"{distance_1 / total_rows:.6f}"
    )

    print(
        f"Distance-2+ share of all rows: "
        f"{distance_2_plus / total_rows:.6f}"
    )

    # --------------------------------------------------------
    # [8] Data-quality check
    # --------------------------------------------------------
    print("\n[8] Priority-label integrity")

    print(
        f"Rows involving unknown priority labels: "
        f"{unknown_priority_rows:,}"
    )

    if unknown_priority_rows == 0:
        print("All observed priorities are valid P1–P5 labels.")
    else:
        print(
            "WARNING: Some rows could not be assigned "
            "ordinal transition distance."
        )

    # --------------------------------------------------------
    # [9] Interpretation boundary
    # --------------------------------------------------------
    print("\n[9] Interpretation boundary")

    print(
        "This operation characterizes correctness and observed "
        "ordinal transition distance jointly."
    )

    print(
        "It does NOT define distance-1 errors as acceptable, "
        "safe, or automatable."
    )

    print(
        "It does NOT define distance-2+ errors as unacceptable "
        "for any operational policy."
    )

    print(
        "It does NOT establish an automation threshold, "
        "confidence boundary, or universal T10 score."
    )

    print(
        "It does NOT assign AUTOMATE, HUMAN_REVIEW, or "
        "DEFER_INSUFFICIENT_EVIDENCE states."
    )

    # --------------------------------------------------------
    # [10] Final status
    # --------------------------------------------------------
    print("\n[10] OP-028 status")

    if total_rows == 0:
        print("STATUS: FAIL — no prediction rows found")
        raise RuntimeError("No prediction rows found.")

    if unknown_priority_rows > 0:
        print("STATUS: PASS WITH DATA-QUALITY LIMITATION")
    else:
        print("STATUS: PASS")

    print(
        "T2 correctness by priority-transition distance "
        "successfully characterized."
    )

    print("No automation policy was selected.")

    print("\n" + "=" * 70)
    print("END OF T10 / OP-028")
    print("=" * 70)


if __name__ == "__main__":
    main()