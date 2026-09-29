from pathlib import Path
import pandas as pd


# ============================================================
# T10 / OP-030
# T2 Empirical Evidence Sufficiency & Limitation Assessment
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
    print(
        "T10 / OP-030 — T2 EMPIRICAL EVIDENCE SUFFICIENCY "
        "& LIMITATION ASSESSMENT"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # [1] Input artifact
    # --------------------------------------------------------
    print("\n[1] Input artifact")
    print(f"Path: {INPUT_PATH}")

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input artifact not found: {INPUT_PATH}"
        )

    # --------------------------------------------------------
    # [2] Reconcile native evaluation population
    # --------------------------------------------------------
    print("\n[2] Native evaluation-population reconciliation")

    total_rows = 0
    unique_ids = set()
    null_ids = 0
    blank_ids = 0
    null_actual = 0
    null_predicted = 0

    correct = 0
    incorrect = 0

    distance1 = 0
    distance2plus = 0

    valid_priorities = {"P1", "P2", "P3", "P4", "P5"}

    invalid_priority_rows = 0

    priority_order = {
        "P1": 1,
        "P2": 2,
        "P3": 3,
        "P4": 4,
        "P5": 5,
    }

    for chunk in pd.read_csv(
        INPUT_PATH,
        usecols=REQUIRED_COLUMNS,
        chunksize=CHUNK_SIZE,
    ):
        total_rows += len(chunk)

        for row in chunk.itertuples(index=False):
            ticket_id = row.ID
            actual = row.actual_priority
            predicted = row.predicted_priority

            # ID integrity
            if pd.isna(ticket_id):
                null_ids += 1
                continue

            ticket_id = str(ticket_id)

            if not ticket_id.strip():
                blank_ids += 1
                continue

            unique_ids.add(ticket_id)

            # Target / prediction integrity
            if pd.isna(actual):
                null_actual += 1
                continue

            if pd.isna(predicted):
                null_predicted += 1
                continue

            actual = str(actual)
            predicted = str(predicted)

            if (
                actual not in valid_priorities
                or predicted not in valid_priorities
            ):
                invalid_priority_rows += 1
                continue

            # Correctness
            if actual == predicted:
                correct += 1
                continue

            incorrect += 1

            distance = abs(
                priority_order[predicted]
                - priority_order[actual]
            )

            if distance == 1:
                distance1 += 1
            elif distance >= 2:
                distance2plus += 1

    # --------------------------------------------------------
    # [3] Population results
    # --------------------------------------------------------
    print("\n[3] Population results")

    print(f"Rows: {total_rows:,}")
    print(f"Unique IDs: {len(unique_ids):,}")
    print(f"Null IDs: {null_ids:,}")
    print(f"Blank IDs: {blank_ids:,}")
    print(f"Null actual priorities: {null_actual:,}")
    print(f"Null predicted priorities: {null_predicted:,}")
    print(f"Invalid priority rows: {invalid_priority_rows:,}")

    print(f"Correct predictions: {correct:,}")
    print(f"Incorrect predictions: {incorrect:,}")
    print(f"Distance-1 errors: {distance1:,}")
    print(f"Distance-2+ errors: {distance2plus:,}")

    # --------------------------------------------------------
    # [4] Arithmetic reconciliation
    # --------------------------------------------------------
    print("\n[4] Arithmetic reconciliation")

    correctness_reconciles = (
        correct + incorrect == total_rows
    )

    error_distance_reconciles = (
        distance1 + distance2plus == incorrect
    )

    id_reconciles = (
        len(unique_ids) == total_rows
    )

    print(
        "Correct + incorrect == total rows: "
        f"{correctness_reconciles}"
    )

    print(
        "Distance-1 + distance-2+ == incorrect: "
        f"{error_distance_reconciles}"
    )

    print(
        "Unique IDs == total rows: "
        f"{id_reconciles}"
    )

    # --------------------------------------------------------
    # [5] Evidence sufficiency matrix
    # --------------------------------------------------------
    print("\n[5] T10 empirical evidence sufficiency matrix")

    evidence = [
        (
            "E1",
            "Traceable held-out population",
            True,
            "4,425 unique ticket IDs with complete cohort reconciliation.",
        ),
        (
            "E2",
            "Native predictive correctness",
            True,
            "1,859 correct and 2,566 incorrect native T2 predictions.",
        ),
        (
            "E3",
            "Error concentration analysis",
            True,
            "Actual-class, predicted-class, transition, support, "
            "and distance analyses completed.",
        ),
        (
            "E4",
            "Error-cohort traceability",
            True,
            "Correct/incorrect and distance cohorts are mutually "
            "exclusive and collectively exhaustive.",
        ),
        (
            "E5",
            "Native calibrated probability",
            False,
            "T2 retained artifact contains hard predictions only; "
            "no native probability field was established.",
        ),
        (
            "E6",
            "Validated uncertainty measure",
            False,
            "No native uncertainty evidence has been established "
            "for T2.",
        ),
        (
            "E7",
            "Validated automation boundary",
            False,
            "No empirical automation threshold or operating region "
            "has been validated.",
        ),
        (
            "E8",
            "Validated human-review boundary",
            False,
            "No empirically validated review threshold or region "
            "has been established.",
        ),
        (
            "E9",
            "Validated defer boundary",
            False,
            "No empirically validated insufficient-evidence/defer "
            "boundary has been established.",
        ),
        (
            "E10",
            "Validated cross-task T10 policy",
            False,
            "No universal target, score, or empirically validated "
            "cross-task decision policy exists.",
        ),
    ]

    print(
        f"\n{'ID':>6} "
        f"{'Evidence area':<40} "
        f"{'Status':>12}"
    )

    print("-" * 64)

    for evidence_id, description, available, _ in evidence:
        status = "AVAILABLE" if available else "OPEN"

        print(
            f"{evidence_id:>6} "
            f"{description:<40} "
            f"{status:>12}"
        )

    # --------------------------------------------------------
    # [6] Evidence details
    # --------------------------------------------------------
    print("\n[6] Evidence details")

    for evidence_id, description, available, detail in evidence:
        status = "AVAILABLE" if available else "OPEN"

        print(f"\n{evidence_id} — {description}")
        print(f"Status: {status}")
        print(f"Evidence: {detail}")

    # --------------------------------------------------------
    # [7] Decision-state readiness
    # --------------------------------------------------------
    print("\n[7] T10 decision-state readiness")

    automate_validated = False
    human_review_validated = False
    defer_validated = False

    print(
        "AUTOMATE: "
        + (
            "VALIDATED"
            if automate_validated
            else "NOT_VALIDATED"
        )
    )

    print(
        "HUMAN_REVIEW: "
        + (
            "VALIDATED"
            if human_review_validated
            else "NOT_VALIDATED"
        )
    )

    print(
        "DEFER_INSUFFICIENT_EVIDENCE: "
        + (
            "VALIDATED"
            if defer_validated
            else "NOT_VALIDATED"
        )
    )

    # --------------------------------------------------------
    # [8] Policy boundary
    # --------------------------------------------------------
    print("\n[8] Policy boundary")

    print(
        "T2 has sufficient native held-out evidence for "
        "descriptive empirical error analysis."
    )

    print(
        "T2 does NOT currently have sufficient evidence to "
        "validate an automation region."
    )

    print(
        "T2 does NOT currently have sufficient evidence to "
        "validate a human-review operating boundary."
    )

    print(
        "T2 does NOT currently have sufficient evidence to "
        "validate a defer operating boundary."
    )

    print(
        "T2 evidence does NOT establish a universal T10 target "
        "or decision score."
    )

    print(
        "No threshold, confidence boundary, or ticket-level "
        "decision state is selected."
    )

    # --------------------------------------------------------
    # [9] Sufficiency status
    # --------------------------------------------------------
    print("\n[9] OP-030 status")

    population_pass = (
        total_rows == 4425
        and len(unique_ids) == 4425
        and null_ids == 0
        and blank_ids == 0
        and null_actual == 0
        and null_predicted == 0
        and invalid_priority_rows == 0
        and correctness_reconciles
        and error_distance_reconciles
        and id_reconciles
    )

    if not population_pass:
        print("STATUS: FAIL")
        raise RuntimeError(
            "T2 native empirical population reconciliation failed."
        )

    print("STATUS: PASS")
    print(
        "T2 has sufficient traceable native evidence for "
        "descriptive empirical validation."
    )
    print(
        "Policy-level validation remains OPEN for automation, "
        "human-review, defer, uncertainty, and cross-task fusion."
    )

    print("\n" + "=" * 70)
    print("END OF T10 / OP-030")
    print("=" * 70)


if __name__ == "__main__":
    main()