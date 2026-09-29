from pathlib import Path
import pandas as pd


# ============================================================
# T10 / OP-029
# T2 Error-Cohort Composition & Traceability Audit
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

PRIORITY_ORDER = {
    "P1": 1,
    "P2": 2,
    "P3": 3,
    "P4": 4,
    "P5": 5,
}


def main():
    print("=" * 70)
    print("T10 / OP-029 — T2 ERROR-COHORT COMPOSITION & TRACEABILITY AUDIT")
    print("=" * 70)

    print("\n[1] Input artifact")
    print(f"Path: {INPUT_PATH}")

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input artifact not found: {INPUT_PATH}"
        )

    total_rows = 0
    null_ids = 0
    blank_ids = 0

    all_ids = set()

    correct_ids = set()
    incorrect_ids = set()

    distance1_ids = set()
    distance2plus_ids = set()

    # Per-cohort priority counts.
    cohort_priority_counts = {
        "correct": {},
        "incorrect": {},
        "distance1": {},
        "distance2plus": {},
    }

    invalid_priority_rows = 0

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

        for row in chunk.itertuples(index=False):
            ticket_id = row.ID
            actual = str(row.actual_priority)
            predicted = str(row.predicted_priority)

            # ID checks
            if pd.isna(ticket_id):
                null_ids += 1
                continue

            ticket_id = str(ticket_id)

            if not ticket_id.strip():
                blank_ids += 1
                continue

            all_ids.add(ticket_id)

            # Priority checks
            if (
                actual not in PRIORITY_ORDER
                or predicted not in PRIORITY_ORDER
            ):
                invalid_priority_rows += 1
                continue

            # Correct / incorrect partition
            if actual == predicted:
                correct_ids.add(ticket_id)

                cohort_priority_counts["correct"][actual] = (
                    cohort_priority_counts["correct"].get(actual, 0) + 1
                )

            else:
                incorrect_ids.add(ticket_id)

                cohort_priority_counts["incorrect"][actual] = (
                    cohort_priority_counts["incorrect"].get(actual, 0) + 1
                )

                distance = abs(
                    PRIORITY_ORDER[predicted]
                    - PRIORITY_ORDER[actual]
                )

                if distance == 1:
                    distance1_ids.add(ticket_id)

                    cohort_priority_counts["distance1"][actual] = (
                        cohort_priority_counts["distance1"].get(actual, 0)
                        + 1
                    )

                elif distance >= 2:
                    distance2plus_ids.add(ticket_id)

                    cohort_priority_counts["distance2plus"][actual] = (
                        cohort_priority_counts["distance2plus"].get(actual, 0)
                        + 1
                    )

    # --------------------------------------------------------
    # [3] Basic population
    # --------------------------------------------------------
    print("\n[3] Population and ID summary")

    print(f"Rows: {total_rows:,}")
    print(f"Unique IDs: {len(all_ids):,}")
    print(f"Null IDs: {null_ids:,}")
    print(f"Blank IDs: {blank_ids:,}")
    print(f"Invalid priority rows: {invalid_priority_rows:,}")

    # --------------------------------------------------------
    # [4] Cohort counts
    # --------------------------------------------------------
    print("\n[4] Cohort counts")

    print(
        f"\n{'Cohort':>18} "
        f"{'Rows':>12} "
        f"{'Unique IDs':>14}"
    )

    print("-" * 50)

    cohorts = [
        ("correct", correct_ids),
        ("incorrect", incorrect_ids),
        ("distance1", distance1_ids),
        ("distance2plus", distance2plus_ids),
    ]

    for name, ids in cohorts:
        print(
            f"{name:>18} "
            f"{len(ids):>12,} "
            f"{len(ids):>14,}"
        )

    # --------------------------------------------------------
    # [5] Partition arithmetic
    # --------------------------------------------------------
    print("\n[5] Partition arithmetic")

    correct_count = len(correct_ids)
    incorrect_count = len(incorrect_ids)

    distance1_count = len(distance1_ids)
    distance2plus_count = len(distance2plus_ids)

    print(
        f"Correct + incorrect: "
        f"{correct_count + incorrect_count:,}"
    )

    print(
        f"Distance-1 + distance-2+: "
        f"{distance1_count + distance2plus_count:,}"
    )

    print(
        f"Total rows: "
        f"{total_rows:,}"
    )

    print(
        f"Correct + incorrect == total: "
        f"{correct_count + incorrect_count == total_rows}"
    )

    print(
        f"Distance-1 + distance-2+ == incorrect: "
        f"{distance1_count + distance2plus_count == incorrect_count}"
    )

    # --------------------------------------------------------
    # [6] Set-overlap checks
    # --------------------------------------------------------
    print("\n[6] Cohort set-overlap checks")

    correct_incorrect_overlap = (
        correct_ids & incorrect_ids
    )

    distance_overlap = (
        distance1_ids & distance2plus_ids
    )

    correct_distance1_overlap = (
        correct_ids & distance1_ids
    )

    correct_distance2plus_overlap = (
        correct_ids & distance2plus_ids
    )

    print(
        "Correct ∩ Incorrect: "
        f"{len(correct_incorrect_overlap):,}"
    )

    print(
        "Distance-1 ∩ Distance-2+: "
        f"{len(distance_overlap):,}"
    )

    print(
        "Correct ∩ Distance-1: "
        f"{len(correct_distance1_overlap):,}"
    )

    print(
        "Correct ∩ Distance-2+: "
        f"{len(correct_distance2plus_overlap):,}"
    )

    # --------------------------------------------------------
    # [7] Cohort completeness
    # --------------------------------------------------------
    print("\n[7] Cohort completeness")

    union_ids = (
        correct_ids
        | distance1_ids
        | distance2plus_ids
    )

    uncovered_ids = all_ids - union_ids

    multiply_assigned = (
        (correct_ids & distance1_ids)
        | (correct_ids & distance2plus_ids)
        | (distance1_ids & distance2plus_ids)
    )

    print(f"All traceable IDs: {len(all_ids):,}")
    print(f"Cohort-union IDs: {len(union_ids):,}")
    print(f"Uncovered IDs: {len(uncovered_ids):,}")
    print(f"Multiply-assigned IDs: {len(multiply_assigned):,}")

    # --------------------------------------------------------
    # [8] Cohort composition by actual priority
    # --------------------------------------------------------
    print("\n[8] Cohort composition by actual priority")

    print(
        f"\n{'Actual':>10} "
        f"{'Correct':>12} "
        f"{'Incorrect':>12} "
        f"{'Distance1':>12} "
        f"{'Distance2+':>12}"
    )

    print("-" * 62)

    for priority in ["P1", "P2", "P3", "P4", "P5"]:
        correct = cohort_priority_counts["correct"].get(
            priority,
            0,
        )

        incorrect = cohort_priority_counts["incorrect"].get(
            priority,
            0,
        )

        distance1 = cohort_priority_counts["distance1"].get(
            priority,
            0,
        )

        distance2plus = cohort_priority_counts[
            "distance2plus"
        ].get(priority, 0)

        print(
            f"{priority:>10} "
            f"{correct:>12,} "
            f"{incorrect:>12,} "
            f"{distance1:>12,} "
            f"{distance2plus:>12,}"
        )

    # --------------------------------------------------------
    # [9] Traceability status
    # --------------------------------------------------------
    print("\n[9] Traceability assessment")

    traceability_pass = (
        null_ids == 0
        and blank_ids == 0
        and invalid_priority_rows == 0
        and len(all_ids) == total_rows
        and correct_count + incorrect_count == total_rows
        and distance1_count + distance2plus_count == incorrect_count
        and len(correct_incorrect_overlap) == 0
        and len(distance_overlap) == 0
        and len(correct_distance1_overlap) == 0
        and len(correct_distance2plus_overlap) == 0
        and len(uncovered_ids) == 0
        and len(multiply_assigned) == 0
    )

    if traceability_pass:
        print(
            "PASS: Evaluation rows form a complete, mutually "
            "exclusive, ID-traceable cohort partition."
        )
    else:
        print(
            "FAIL: One or more cohort/traceability checks failed."
        )

    # --------------------------------------------------------
    # [10] Interpretation boundary
    # --------------------------------------------------------
    print("\n[10] Interpretation boundary")

    print(
        "This operation validates the structure and traceability "
        "of the T2 empirical error cohorts."
    )

    print(
        "It does NOT establish acceptable or unacceptable "
        "prediction errors."
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
    # [11] Final status
    # --------------------------------------------------------
    print("\n[11] OP-029 status")

    if traceability_pass:
        print("STATUS: PASS")
        print(
            "T2 error cohorts are complete, mutually exclusive, "
            "and ID-traceable."
        )
        print("No automation policy was selected.")
    else:
        print("STATUS: FAIL")
        raise RuntimeError(
            "T2 error-cohort traceability audit failed."
        )

    print("\n" + "=" * 70)
    print("END OF T10 / OP-029")
    print("=" * 70)


if __name__ == "__main__":
    main()