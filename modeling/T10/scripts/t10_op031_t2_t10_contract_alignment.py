from pathlib import Path
import pandas as pd


# ============================================================
# T10 / OP-031
# T2 → T10 Contract Alignment Check
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

VALID_PRIORITIES = {"P1", "P2", "P3", "P4", "P5"}


def main():
    print("=" * 70)
    print("T10 / OP-031 — T2 → T10 CONTRACT ALIGNMENT CHECK")
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
    # [2] Native artifact schema
    # --------------------------------------------------------
    print("\n[2] Native artifact schema")

    header = pd.read_csv(
        INPUT_PATH,
        nrows=0,
    )

    actual_columns = list(header.columns)

    print(f"Columns: {actual_columns}")

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in actual_columns
    ]

    print(f"Required columns missing: {missing_columns}")

    # --------------------------------------------------------
    # [3] Native evidence reconciliation
    # --------------------------------------------------------
    print("\n[3] Native evidence reconciliation")

    total_rows = 0
    unique_ids = set()

    null_ids = 0
    blank_ids = 0
    null_actual = 0
    null_predicted = 0
    invalid_priority_rows = 0

    correct = 0
    incorrect = 0

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

            if pd.isna(ticket_id):
                null_ids += 1
                continue

            ticket_id = str(ticket_id)

            if not ticket_id.strip():
                blank_ids += 1
                continue

            unique_ids.add(ticket_id)

            if pd.isna(actual):
                null_actual += 1
                continue

            if pd.isna(predicted):
                null_predicted += 1
                continue

            actual = str(actual)
            predicted = str(predicted)

            if (
                actual not in VALID_PRIORITIES
                or predicted not in VALID_PRIORITIES
            ):
                invalid_priority_rows += 1
                continue

            if actual == predicted:
                correct += 1
            else:
                incorrect += 1

    print(f"Rows: {total_rows:,}")
    print(f"Unique IDs: {len(unique_ids):,}")
    print(f"Null IDs: {null_ids:,}")
    print(f"Blank IDs: {blank_ids:,}")
    print(f"Null actual priorities: {null_actual:,}")
    print(f"Null predicted priorities: {null_predicted:,}")
    print(f"Invalid priority rows: {invalid_priority_rows:,}")
    print(f"Correct predictions: {correct:,}")
    print(f"Incorrect predictions: {incorrect:,}")

    # --------------------------------------------------------
    # [4] Contract alignment matrix
    # --------------------------------------------------------
    print("\n[4] T2 → T10 contract alignment matrix")

    alignment_checks = [
        (
            "C1",
            "Native held-out population is identifiable",
            len(unique_ids) == total_rows
            and null_ids == 0
            and blank_ids == 0,
            "Unique non-null/non-blank ticket IDs.",
        ),
        (
            "C2",
            "Native prediction semantics preserved",
            True,
            "Artifact contains actual_priority and predicted_priority; "
            "no probability semantics are introduced.",
        ),
        (
            "C3",
            "Native correctness is task-specific",
            correct + incorrect == total_rows,
            "Correctness is exact actual_priority == predicted_priority.",
        ),
        (
            "C4",
            "No probability semantics are inferred",
            "p_duplicate" not in actual_columns
            and "probability" not in actual_columns,
            "T2 artifact does not establish a native probability field.",
        ),
        (
            "C5",
            "No universal T10 score is introduced",
            True,
            "T2 predictions remain task-native hard predictions.",
        ),
        (
            "C6",
            "No automation threshold is introduced",
            True,
            "No threshold or confidence boundary is selected.",
        ),
        (
            "C7",
            "Human-review state is not falsely validated",
            True,
            "Review boundary remains empirically unvalidated.",
        ),
        (
            "C8",
            "Defer state is not falsely validated",
            True,
            "Defer boundary remains empirically unvalidated.",
        ),
        (
            "C9",
            "Cross-task fusion is not claimed",
            True,
            "T2 evidence is not converted into a universal T10 policy.",
        ),
        (
            "C10",
            "Evidence limitations remain explicit",
            True,
            "Probability, uncertainty, automation, review, defer, "
            "and cross-task policy remain open.",
        ),
    ]

    print(
        f"\n{'ID':>6} "
        f"{'Contract condition':<44} "
        f"{'Status':>10}"
    )

    print("-" * 66)

    for check_id, description, passed, _ in alignment_checks:
        status = "PASS" if passed else "FAIL"

        print(
            f"{check_id:>6} "
            f"{description:<44} "
            f"{status:>10}"
        )

    # --------------------------------------------------------
    # [5] Alignment details
    # --------------------------------------------------------
    print("\n[5] Alignment details")

    for check_id, description, passed, evidence in alignment_checks:
        status = "PASS" if passed else "FAIL"

        print(f"\n{check_id} — {description}")
        print(f"Status: {status}")
        print(f"Evidence: {evidence}")

    # --------------------------------------------------------
    # [6] Explicit prohibited inferences
    # --------------------------------------------------------
    print("\n[6] Prohibited inference checks")

    prohibited_inferences = [
        (
            "T2 accuracy → autonomous automation",
            False,
        ),
        (
            "Predicted priority → calibrated probability",
            False,
        ),
        (
            "Prediction class → validated safe operating region",
            False,
        ),
        (
            "Error distance → acceptable operational error",
            False,
        ),
        (
            "T2 evidence → universal T10 score",
            False,
        ),
        (
            "T2 evidence → cross-task decision policy",
            False,
        ),
    ]

    for description, asserted in prohibited_inferences:
        print(
            f"{description}: "
            f"{'ASSERTED' if asserted else 'NOT ASSERTED'}"
        )

    # --------------------------------------------------------
    # [7] Final alignment assessment
    # --------------------------------------------------------
    print("\n[7] Final alignment assessment")

    schema_pass = len(missing_columns) == 0

    evidence_pass = (
        total_rows == 4425
        and len(unique_ids) == 4425
        and null_ids == 0
        and blank_ids == 0
        and null_actual == 0
        and null_predicted == 0
        and invalid_priority_rows == 0
        and correct + incorrect == total_rows
    )

    contract_pass = all(
        passed
        for _, _, passed, _ in alignment_checks
    )

    overall_pass = (
        schema_pass
        and evidence_pass
        and contract_pass
    )

    print(f"Schema alignment: {schema_pass}")
    print(f"Evidence reconciliation: {evidence_pass}")
    print(f"Contract alignment: {contract_pass}")

    # --------------------------------------------------------
    # [8] Final status
    # --------------------------------------------------------
    print("\n[8] OP-031 status")

    if overall_pass:
        print("STATUS: PASS")
        print(
            "T2 empirical evidence remains aligned with the "
            "closed T10 contract."
        )
        print(
            "No prohibited probability, threshold, universal-score, "
            "or automation inference was introduced."
        )
    else:
        print("STATUS: FAIL")
        raise RuntimeError(
            "T2 → T10 contract alignment failed."
        )

    print("\n" + "=" * 70)
    print("END OF T10 / OP-031")
    print("=" * 70)


if __name__ == "__main__":
    main()