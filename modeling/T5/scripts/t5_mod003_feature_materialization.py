from pathlib import Path
import csv
import json
import time
import sys


csv.field_size_limit(sys.maxsize)


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

DATASET_ROOT = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE"
)

SOURCE = DATASET_ROOT / "DTM-002_T5_TRAIN_GROUP_AWARE.csv"

OUTPUT_DIR = PROJECT_ROOT / "modeling" / "T5" / "derived"

OUTPUT = OUTPUT_DIR / "t5_train_features.csv"

REPORT = OUTPUT_DIR / "t5_mod003_materialize_report.json"


REQUIRED_COLUMNS = [
    "ID",
    "Creation time",
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
    "T5 target",
]


EXPECTED_ROWS = 492_989


def fail(message):
    print(f"FAIL: {message}")
    sys.exit(1)


def main():
    start_time = time.time()

    print("=" * 80)
    print("T5-MOD-003 — CONTROLLED FEATURE MATERIALIZATION")
    print("=" * 80)

    # ------------------------------------------------------------------
    # 1. Verify source
    # ------------------------------------------------------------------

    print("\n[1] Source artifact")

    print(f"Source: {SOURCE}")

    if not SOURCE.exists():
        fail("Accepted T5 training artifact does not exist.")

    print("PASS")

    # ------------------------------------------------------------------
    # 2. Prepare controlled output directory
    # ------------------------------------------------------------------

    print("\n[2] Output directory")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(f"Output directory: {OUTPUT_DIR}")
    print("PASS")

    # ------------------------------------------------------------------
    # 3. Validate source schema
    # ------------------------------------------------------------------

    print("\n[3] Source schema")

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as source_file:

        reader = csv.DictReader(source_file)

        if reader.fieldnames is None:
            fail("Source CSV has no header.")

        missing = [
            column
            for column in REQUIRED_COLUMNS
            if column not in reader.fieldnames
        ]

        if missing:
            fail(
                "Missing required columns: "
                + ", ".join(missing)
            )

        print(f"Source columns: {len(reader.fieldnames)}")
        print("Required modeling columns:")

        for column in REQUIRED_COLUMNS:
            print(f"  - {column}")

    print("PASS")

    # ------------------------------------------------------------------
    # 4. Materialize controlled modeling artifact
    # ------------------------------------------------------------------

    print("\n[4] Materialize controlled training artifact")

    rows_written = 0
    positive_count = 0
    negative_count = 0

    temp_output = OUTPUT.with_suffix(".tmp")

    if temp_output.exists():
        temp_output.unlink()

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as source_file:

        reader = csv.DictReader(source_file)

        with temp_output.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as output_file:

            writer = csv.DictWriter(
                output_file,
                fieldnames=REQUIRED_COLUMNS,
            )

            writer.writeheader()

            for row in reader:
                target = row["T5 target"].strip()

                if target == "1":
                    positive_count += 1
                elif target == "0":
                    negative_count += 1
                else:
                    fail(
                        f"Invalid T5 target value: {target!r}"
                    )

                writer.writerow(
                    {
                        column: row[column]
                        for column in REQUIRED_COLUMNS
                    }
                )

                rows_written += 1

    temp_output.replace(OUTPUT)

    print(f"Rows written: {rows_written}")
    print(f"Positive: {positive_count}")
    print(f"Negative: {negative_count}")

    if rows_written != EXPECTED_ROWS:
        fail(
            f"Expected {EXPECTED_ROWS} rows, "
            f"found {rows_written}."
        )

    if positive_count != 3_373:
        fail(
            f"Expected 3,373 positives, "
            f"found {positive_count}."
        )

    if negative_count != 489_616:
        fail(
            f"Expected 489,616 negatives, "
            f"found {negative_count}."
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 5. Validate output
    # ------------------------------------------------------------------

    print("\n[5] Validate materialized artifact")

    if not OUTPUT.exists():
        fail("Output artifact was not created.")

    with OUTPUT.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as output_file:

        reader = csv.DictReader(output_file)

        if reader.fieldnames != REQUIRED_COLUMNS:
            fail(
                "Materialized artifact schema does not match "
                "the frozen modeling schema."
            )

        output_rows = sum(1 for _ in reader)

    print(f"Output rows: {output_rows}")
    print(f"Output columns: {len(reader.fieldnames)}")

    if output_rows != EXPECTED_ROWS:
        fail(
            f"Expected {EXPECTED_ROWS} output rows, "
            f"found {output_rows}."
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 6. Write materialization report
    # ------------------------------------------------------------------

    print("\n[6] Write materialization report")

    elapsed = time.time() - start_time

    report = {
        "operation": "T5-MOD-003",
        "operation_name": (
            "Controlled Feature Materialization"
        ),
        "source": str(SOURCE),
        "output": str(OUTPUT),
        "rows_written": rows_written,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "columns": REQUIRED_COLUMNS,
        "source_modified": False,
        "raw_archive_accessed": False,
        "synthetic_data_used": False,
        "target_reconstructed": False,
        "status": "PASS",
        "elapsed_seconds": round(elapsed, 3),
    }

    with REPORT.open(
        "w",
        encoding="utf-8",
    ) as report_file:

        json.dump(
            report,
            report_file,
            indent=2,
            ensure_ascii=False,
        )

        report_file.write("\n")

    print(f"Report: {REPORT}")
    print(f"Elapsed: {elapsed:.2f} seconds")
    print("PASS")

    # ------------------------------------------------------------------
    # Final
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("T5-MOD-003 RESULT: MATERIALIZATION_PASS")
    print("=" * 80)

    print(f"\nControlled artifact:")
    print(OUTPUT)

    print("\nNo model trained.")
    print("No evaluation performed.")
    print("No raw archive accessed.")
    print("Source artifact not modified.")


if __name__ == "__main__":
    main()