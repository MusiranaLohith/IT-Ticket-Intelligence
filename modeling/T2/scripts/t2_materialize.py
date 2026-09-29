from pathlib import Path
import csv
import json
import subprocess
import io
import sys


csv.field_size_limit(sys.maxsize)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

TARGET_PATH = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T2_FIRST_PRIORITY_24H_derived.csv"
)

ARCHIVE_PATH = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "Mozilla_CORE_dataset_issues.zip"
)

CSV_MEMBER = "dataset_issues_TOTAL_TOTAL.csv"

OUTPUT_DIR = PROJECT_ROOT / "modeling" / "T2" / "derived"

OUTPUT_PATH = OUTPUT_DIR / "t2_features.csv"

REPORT_PATH = OUTPUT_DIR / "t2_materialize_report.json"

EXPECTED_ROWS = 29498
EXPECTED_SUMMARY = 29498
EXPECTED_DESCRIPTION = 27906
EXPECTED_DESCRIPTION_MISSING = 1592


def load_target():
    target = {}

    with TARGET_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:

        reader = csv.DictReader(handle)

        required = {
            "ID",
            "target_priority",
        }

        missing = required - set(reader.fieldnames or [])

        if missing:
            raise RuntimeError(
                f"Target artifact missing columns: {sorted(missing)}"
            )

        for row in reader:
            ticket_id = row["ID"].strip()

            if not ticket_id:
                raise RuntimeError(
                    "Blank ID found in target artifact."
                )

            if ticket_id in target:
                raise RuntimeError(
                    f"Duplicate target ID: {ticket_id}"
                )

            target[ticket_id] = {
                "target_priority": row["target_priority"].strip()
            }

    if len(target) != EXPECTED_ROWS:
        raise RuntimeError(
            f"Expected {EXPECTED_ROWS} target rows, "
            f"found {len(target)}."
        )

    return target


def stream_source(target):
    command = [
        "7z",
        "x",
        "-so",
        str(ARCHIVE_PATH),
        CSV_MEMBER,
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )

    found = {}
    source_matching_rows = 0

    try:
        text_stream = io.TextIOWrapper(
            process.stdout,
            encoding="utf-8",
            newline="",
        )

        reader = csv.DictReader(text_stream)

        required = {
            "ID",
            "Creation time",
            "Summary",
            "Description",
        }

        missing = required - set(reader.fieldnames or [])

        if missing:
            process.kill()
            raise RuntimeError(
                f"Source CSV missing columns: {sorted(missing)}"
            )

        for row in reader:
            ticket_id = row["ID"].strip()

            if ticket_id not in target:
                continue

            source_matching_rows += 1

            if ticket_id in found:
                process.kill()
                raise RuntimeError(
                    f"Duplicate source ID encountered: {ticket_id}"
                )

            found[ticket_id] = {
                "Creation time": row["Creation time"],
                "Summary": row["Summary"],
                "Description": row["Description"],
            }

            if len(found) % 5000 == 0:
                print(
                    f"MATCHED={len(found)}/{EXPECTED_ROWS}",
                    flush=True,
                )

    finally:
        if process.stdout is not None:
            process.stdout.close()

    return_code = process.wait()

    if return_code != 0:
        raise RuntimeError(
            f"7z streaming failed with return code "
            f"{return_code}."
        )

    return found, source_matching_rows


def validate_and_write(
    target,
    found,
    source_matching_rows,
):
    missing_ids = sorted(
        set(target) - set(found)
    )

    if missing_ids:
        raise RuntimeError(
            f"{len(missing_ids)} T2 IDs were not found. "
            f"First IDs: {missing_ids[:10]}"
        )

    if len(found) != EXPECTED_ROWS:
        raise RuntimeError(
            f"Expected {EXPECTED_ROWS} matched records, "
            f"found {len(found)}."
        )

    summary_count = sum(
        1
        for ticket_id in target
        if found[ticket_id]["Summary"].strip()
    )

    description_count = sum(
        1
        for ticket_id in target
        if found[ticket_id]["Description"].strip()
    )

    description_missing = (
        EXPECTED_ROWS - description_count
    )

    if summary_count != EXPECTED_SUMMARY:
        raise RuntimeError(
            f"Summary coverage mismatch: "
            f"expected {EXPECTED_SUMMARY}, "
            f"found {summary_count}."
        )

    if description_count != EXPECTED_DESCRIPTION:
        raise RuntimeError(
            f"Description coverage mismatch: "
            f"expected {EXPECTED_DESCRIPTION}, "
            f"found {description_count}."
        )

    if description_missing != EXPECTED_DESCRIPTION_MISSING:
        raise RuntimeError(
            f"Description missingness mismatch: "
            f"expected {EXPECTED_DESCRIPTION_MISSING}, "
            f"found {description_missing}."
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_output = OUTPUT_PATH.with_suffix(
        ".tmp"
    )

    with temporary_output.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:

        fieldnames = [
            "ID",
            "Creation time",
            "Summary",
            "Description",
            "target_priority",
        ]

        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for ticket_id in target:
            writer.writerow(
                {
                    "ID": ticket_id,
                    "Creation time": found[ticket_id][
                        "Creation time"
                    ],
                    "Summary": found[ticket_id][
                        "Summary"
                    ],
                    "Description": found[ticket_id][
                        "Description"
                    ],
                    "target_priority": target[ticket_id][
                        "target_priority"
                    ],
                }
            )

    temporary_output.replace(
        OUTPUT_PATH
    )

    report = {
        "operation": "T2-MOD-003",
        "operation_name": (
            "Controlled Summary/Description "
            "Feature Materialization"
        ),
        "task": "T2",
        "dataset": "Mozilla CORE",

        "source": {
            "archive": str(ARCHIVE_PATH),
            "member": CSV_MEMBER,
            "access_method": "7z_streaming",
            "full_extraction": False,
        },

        "target": {
            "artifact": str(TARGET_PATH),
            "expected_rows": EXPECTED_ROWS,
            "matched_rows": len(found),
        },

        "features": {
            "Summary": {
                "non_empty": summary_count,
                "expected": EXPECTED_SUMMARY,
            },
            "Description": {
                "non_empty": description_count,
                "expected": EXPECTED_DESCRIPTION,
                "missing": description_missing,
                "expected_missing": EXPECTED_DESCRIPTION_MISSING,
            },
        },

        "integrity": {
            "source_matching_rows": source_matching_rows,
            "missing_t2_ids": len(missing_ids),
            "raw_source_modified": False,
            "target_artifact_modified": False,
            "labels_modified": False,
            "post_creation_information_added": False,
            "current_mutable_features_added": False,
            "fabricated_description_values": False,
        },

        "output": {
            "artifact": str(OUTPUT_PATH),
            "rows": len(found),
            "columns": 5,
        },

        "status": "COMPLETE",
    }

    with REPORT_PATH.open(
        "w",
        encoding="utf-8",
    ) as handle:

        json.dump(
            report,
            handle,
            indent=2,
        )

    print("T2_MOD_003_COMPLETE")
    print(f"OUTPUT={OUTPUT_PATH}")
    print(f"REPORT={REPORT_PATH}")
    print(f"ROWS={len(found)}")
    print(f"SOURCE_MATCHES={source_matching_rows}")
    print(f"SUMMARY_NON_EMPTY={summary_count}")
    print(f"DESCRIPTION_NON_EMPTY={description_count}")
    print(f"DESCRIPTION_MISSING={description_missing}")
    print("FULL_ARCHIVE_EXTRACTION=False")
    print("TARGET_ARTIFACT_MODIFIED=False")
    print("RAW_SOURCE_MODIFIED=False")
    print("STATUS=COMPLETE")


def main():
    target = load_target()

    print("T2_MOD_003_START")
    print(f"TARGET_ROWS={len(target)}")
    print("SOURCE_ACCESS=7z_STREAMING")
    print("FULL_EXTRACTION=False")

    found, source_matching_rows = stream_source(
        target
    )

    validate_and_write(
        target,
        found,
        source_matching_rows,
    )


if __name__ == "__main__":
    main()