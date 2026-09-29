from pathlib import Path
import pandas as pd


# ============================================================
# T10 / OP-027
# T2 Support-Stratified Error Analysis
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
    print("T10 / OP-027 — T2 SUPPORT-STRATIFIED ERROR ANALYSIS")
    print("=" * 70)

    print("\n[1] Input artifact")
    print(f"Path: {INPUT_PATH}")

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input artifact not found: {INPUT_PATH}"
        )

    # --------------------------------------------------------
    # Accumulators
    # --------------------------------------------------------
    total_rows = 0
    total_correct = 0
    total_incorrect = 0

    actual_support = {}
    actual_correct = {}
    actual_incorrect = {}

    predicted_support = {}
    predicted_correct = {}
    predicted_incorrect = {}

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

            actual_support[actual] = (
                actual_support.get(actual, 0) + 1
            )

            predicted_support[predicted] = (
                predicted_support.get(predicted, 0) + 1
            )

            if actual == predicted:
                total_correct += 1

                actual_correct[actual] = (
                    actual_correct.get(actual, 0) + 1
                )

                predicted_correct[predicted] = (
                    predicted_correct.get(predicted, 0) + 1
                )
            else:
                total_incorrect += 1

                actual_incorrect[actual] = (
                    actual_incorrect.get(actual, 0) + 1
                )

                predicted_incorrect[predicted] = (
                    predicted_incorrect.get(predicted, 0) + 1
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
    # [4] Actual-class support and error analysis
    # --------------------------------------------------------
    print("\n[4] Actual-class support stratification")

    print(
        "\n"
        f"{'Actual':>10} "
        f"{'Support':>12} "
        f"{'PopShare':>12} "
        f"{'Correct':>12} "
        f"{'Incorrect':>12} "
        f"{'Accuracy':>12} "
        f"{'ErrorRate':>12} "
        f"{'ErrorShare':>12}"
    )

    print("-" * 104)

    for priority in PRIORITIES:
        support = actual_support.get(priority, 0)
        correct = actual_correct.get(priority, 0)
        incorrect = actual_incorrect.get(priority, 0)

        population_share = (
            support / total_rows
            if total_rows
            else float("nan")
        )

        class_accuracy = (
            correct / support
            if support
            else float("nan")
        )

        class_error_rate = (
            incorrect / support
            if support
            else float("nan")
        )

        error_share = (
            incorrect / total_incorrect
            if total_incorrect
            else float("nan")
        )

        print(
            f"{priority:>10} "
            f"{support:>12,} "
            f"{population_share:>12.6f} "
            f"{correct:>12,} "
            f"{incorrect:>12,} "
            f"{class_accuracy:>12.6f} "
            f"{class_error_rate:>12.6f} "
            f"{error_share:>12.6f}"
        )

    # --------------------------------------------------------
    # [5] Support bands
    # --------------------------------------------------------
    print("\n[5] Support bands")

    support_bands = [
        ("very_low", 0, 50),
        ("low", 51, 200),
        ("medium", 201, 1000),
        ("high", 1001, float("inf")),
    ]

    print(
        "\n"
        f"{'Band':>12} "
        f"{'Classes':>12} "
        f"{'Tickets':>12} "
        f"{'Correct':>12} "
        f"{'Incorrect':>12} "
        f"{'Accuracy':>12} "
        f"{'ErrorRate':>12}"
    )

    print("-" * 88)

    for band_name, lower, upper in support_bands:
        band_classes = [
            priority
            for priority in PRIORITIES
            if lower <= actual_support.get(priority, 0) <= upper
        ]

        band_tickets = sum(
            actual_support.get(priority, 0)
            for priority in band_classes
        )

        band_correct = sum(
            actual_correct.get(priority, 0)
            for priority in band_classes
        )

        band_incorrect = sum(
            actual_incorrect.get(priority, 0)
            for priority in band_classes
        )

        band_accuracy = (
            band_correct / band_tickets
            if band_tickets
            else float("nan")
        )

        band_error_rate = (
            band_incorrect / band_tickets
            if band_tickets
            else float("nan")
        )

        classes_display = (
            ",".join(band_classes)
            if band_classes
            else "-"
        )

        print(
            f"{band_name:>12} "
            f"{classes_display:>12} "
            f"{band_tickets:>12,} "
            f"{band_correct:>12,} "
            f"{band_incorrect:>12,} "
            f"{band_accuracy:>12.6f} "
            f"{band_error_rate:>12.6f}"
        )

    # --------------------------------------------------------
    # [6] Support vs observed error-rate diagnostic
    # --------------------------------------------------------
    print("\n[6] Per-class support vs observed error-rate")

    print(
        "\n"
        f"{'Priority':>12} "
        f"{'Support':>12} "
        f"{'ErrorRate':>14}"
    )

    print("-" * 42)

    for priority in PRIORITIES:
        support = actual_support.get(priority, 0)
        incorrect = actual_incorrect.get(priority, 0)

        error_rate_class = (
            incorrect / support
            if support
            else float("nan")
        )

        print(
            f"{priority:>12} "
            f"{support:>12,} "
            f"{error_rate_class:>14.6f}"
        )

    # --------------------------------------------------------
    # [7] Rank classes by support
    # --------------------------------------------------------
    print("\n[7] Support ranking")

    support_ranking = sorted(
        [
            (
                priority,
                actual_support.get(priority, 0),
                actual_incorrect.get(priority, 0),
            )
            for priority in PRIORITIES
        ],
        key=lambda item: item[1],
        reverse=True,
    )

    print(
        f"\n{'Rank':>6} "
        f"{'Priority':>12} "
        f"{'Support':>12} "
        f"{'Incorrect':>12}"
    )

    print("-" * 48)

    for rank, (priority, support, incorrect) in enumerate(
        support_ranking,
        start=1,
    ):
        print(
            f"{rank:>6} "
            f"{priority:>12} "
            f"{support:>12,} "
            f"{incorrect:>12,}"
        )

    # --------------------------------------------------------
    # [8] Interpretation boundary
    # --------------------------------------------------------
    print("\n[8] Interpretation boundary")

    print(
        "Support-stratified results describe the observed "
        "relationship between class population size and T2 "
        "held-out error."
    )

    print(
        "Low support does NOT by itself establish that a class "
        "is unsafe, unreliable, or unsuitable for automation."
    )

    print(
        "This operation does NOT establish causation between "
        "support size and prediction error."
    )

    print(
        "No automation threshold, confidence boundary, universal "
        "T10 score, or ticket-level policy is selected."
    )

    print(
        "No AUTOMATE, HUMAN_REVIEW, or "
        "DEFER_INSUFFICIENT_EVIDENCE states are assigned."
    )

    # --------------------------------------------------------
    # [9] Final status
    # --------------------------------------------------------
    print("\n[9] OP-027 status")

    if total_rows == 0:
        print("STATUS: FAIL — no prediction rows found")
        raise RuntimeError("No prediction rows found.")

    print("STATUS: PASS")
    print(
        "T2 support-stratified error evidence successfully "
        "characterized."
    )
    print("No automation policy was selected.")

    print("\n" + "=" * 70)
    print("END OF T10 / OP-027")
    print("=" * 70)


if __name__ == "__main__":
    main()