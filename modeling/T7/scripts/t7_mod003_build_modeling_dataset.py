#!/usr/bin/env python3

import csv
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path


# ============================================================================
# T7 MOD-003
# FINALIZE CREATION-TIME MODELING DATASET
#
# Recovery mode:
#   The expensive Mozilla CORE raw streaming stage has already completed.
#   The 513,816-row Creation-time feature artifact is reused.
#
# Critical timezone rule:
#
#   Raw Mozilla Creation time:
#       explicit UTC, e.g. 2022-10-28T20:57:23Z
#
#   Accepted T7 target Creation time:
#       timezone-naive UTC+05:30 local wall-clock,
#       e.g. 2022-10-29T02:27:23
#
# Therefore:
#       naive target time +05:30
#       must equal
#       explicit raw UTC time
#
# The final dataset preserves the accepted T7 target Creation-time string.
# No raw source or accepted target artifact is modified.
# ============================================================================


# ============================================================================
# PATHS
# ============================================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T7_TARGET = Path(
    "/run/media/whiteblack/User 1/Datasets/"
    "Mozilla_CORE/"
    "DTM-002_T7_TIME_TO_FIRST_RESOLVED_derived.csv"
)

DERIVED_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "T7"
    / "derived"
)

METRICS_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "T7"
    / "metrics"
)

FEATURE_TEMP = (
    DERIVED_DIR
    / "t7_mod003_creation_features.tmp.csv"
)

SQLITE_PATH = (
    DERIVED_DIR
    / "t7_mod003_staging.sqlite"
)

FINAL_TEMP = (
    DERIVED_DIR
    / "t7_creation_time_modeling_dataset.tmp.csv"
)

FINAL_OUTPUT = (
    DERIVED_DIR
    / "t7_creation_time_modeling_dataset.csv"
)

AUDIT_OUTPUT = (
    METRICS_DIR
    / "t7_mod003_feature_construction_audit.json"
)


# ============================================================================
# EXPECTATIONS
# ============================================================================

EXPECTED_T7_ROWS = 513_816

EXPECTED_EVENT_ROWS = 455_762

EXPECTED_CENSORED_ROWS = 58_054

KNOWN_DUPLICATE_ID = "44606"

UTC_PLUS_0530 = timezone(
    timedelta(hours=5, minutes=30)
)


# ============================================================================
# SCHEMAS
# ============================================================================

TARGET_COLUMNS = [
    "ID",
    "Creation time",
    "first_resolved_time",
    "duration_seconds",
    "event",
    "endpoint_type",
    "observation_endpoint",
    "source_row_width",
]


FEATURE_FILE_COLUMNS = [
    "ID",
    "Creation time",
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
]


FINAL_COLUMNS = [
    "ID",
    "Creation time",
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
    "first_resolved_time",
    "duration_seconds",
    "event",
    "endpoint_type",
    "observation_endpoint",
    "source_row_width",
]


FEATURE_COLUMNS = [
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
]


csv.field_size_limit(sys.maxsize)


# ============================================================================
# UTILITY
# ============================================================================

def fail(message):
    raise RuntimeError(message)


def remove_if_exists(path):
    if path.exists():
        path.unlink()


def ensure_directories():
    DERIVED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    METRICS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


# ============================================================================
# TIMESTAMP PARSING
# ============================================================================

def parse_raw_creation_timestamp(value):
    """
    Parse the raw Mozilla CORE Creation timestamp.

    Raw source Creation timestamps carry explicit UTC notation, e.g.:

        2022-10-28T20:57:23Z

    They are therefore interpreted as UTC.
    """

    text = str(value).strip()

    if not text:
        fail(
            "Blank raw Creation timestamp encountered."
        )

    candidate = text.replace(
        "Z",
        "+00:00",
    )

    try:

        dt = datetime.fromisoformat(
            candidate
        )

    except ValueError:

        try:

            dt = datetime.strptime(
                text,
                "%Y-%m-%dT%H:%M:%SZ",
            ).replace(
                tzinfo=timezone.utc
            )

        except ValueError as exc:

            fail(
                "Unable to parse raw Mozilla Creation timestamp:\n"
                f"{text}"
            )

    if dt.tzinfo is None:

        dt = dt.replace(
            tzinfo=timezone.utc
        )

    else:

        dt = dt.astimezone(
            timezone.utc
        )

    return dt


def parse_target_creation_timestamp(value):
    """
    Parse the accepted T7 target Creation timestamp.

    The target artifact stores Creation time without an explicit timezone.
    Existing Mozilla DTM evidence establishes that these timezone-naive
    target timestamps correspond to the UTC+05:30 local wall-clock frame.

    Therefore a value such as:

        2022-10-29T02:27:23

    is interpreted as:

        2022-10-29T02:27:23+05:30
    """

    text = str(value).strip()

    if not text:
        fail(
            "Blank target Creation timestamp encountered."
        )

    candidate = text.replace(
        "Z",
        "+00:00",
    )

    try:

        dt = datetime.fromisoformat(
            candidate
        )

    except ValueError:

        parsed = None

        for fmt in (
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S.%f",
        ):

            try:

                parsed = datetime.strptime(
                    text,
                    fmt,
                )

                break

            except ValueError:
                pass

        if parsed is None:

            fail(
                "Unable to parse target Creation timestamp:\n"
                f"{text}"
            )

        dt = parsed

    # --------------------------------------------------------
    # Explicit timezone in target, if present.
    # Otherwise apply established UTC+05:30 interpretation.
    # --------------------------------------------------------

    if dt.tzinfo is None:

        dt = dt.replace(
            tzinfo=UTC_PLUS_0530
        )

    return dt.astimezone(
        timezone.utc
    )


def creation_timestamps_equal(
    target_value,
    raw_value,
):

    target_dt = parse_target_creation_timestamp(
        target_value
    )

    raw_dt = parse_raw_creation_timestamp(
        raw_value
    )

    return target_dt == raw_dt


# ============================================================================
# LOAD TARGET
# ============================================================================

def load_target_artifact():

    if not T7_TARGET.exists():
        fail(
            "T7 target artifact not found:\n"
            f"{T7_TARGET}"
        )

    rows = []

    ids = set()

    with open(
        T7_TARGET,
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:

        reader = csv.DictReader(handle)

        if reader.fieldnames != TARGET_COLUMNS:

            fail(
                "T7 target schema mismatch.\n"
                f"Expected: {TARGET_COLUMNS}\n"
                f"Found:    {reader.fieldnames}"
            )

        for row in reader:

            ticket_id = str(
                row["ID"]
            ).strip()

            if not ticket_id:
                fail(
                    "Blank ID in T7 target artifact."
                )

            if ticket_id in ids:
                fail(
                    "Duplicate ID in T7 target artifact: "
                    f"{ticket_id}"
                )

            ids.add(ticket_id)

            # Validate using the established target timezone frame.
            parse_target_creation_timestamp(
                row["Creation time"]
            )

            rows.append(row)

    if len(rows) != EXPECTED_T7_ROWS:

        fail(
            "T7 target row count mismatch.\n"
            f"Expected: {EXPECTED_T7_ROWS}\n"
            f"Found:    {len(rows)}"
        )

    return rows


# ============================================================================
# VALIDATE EXISTING STREAMED FEATURES
# ============================================================================

def validate_feature_artifact():

    if not FEATURE_TEMP.exists():

        fail(
            "Completed Creation-time feature artifact not found:\n"
            f"{FEATURE_TEMP}\n\n"
            "The raw streaming stage would have to be rerun."
        )

    row_count = 0

    ids = set()

    with open(
        FEATURE_TEMP,
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:

        reader = csv.DictReader(handle)

        if reader.fieldnames != FEATURE_FILE_COLUMNS:

            fail(
                "Temporary feature schema mismatch.\n"
                f"Expected: {FEATURE_FILE_COLUMNS}\n"
                f"Found:    {reader.fieldnames}"
            )

        for row in reader:

            row_count += 1

            ticket_id = str(
                row["ID"]
            ).strip()

            if not ticket_id:
                fail(
                    "Blank ID in temporary feature artifact."
                )

            if ticket_id in ids:
                fail(
                    "Duplicate ID in temporary feature artifact: "
                    f"{ticket_id}"
                )

            ids.add(ticket_id)

            # Validate raw-source Creation representation as UTC.
            parse_raw_creation_timestamp(
                row["Creation time"]
            )

    if row_count != EXPECTED_T7_ROWS:

        fail(
            "Temporary feature population mismatch.\n"
            f"Expected: {EXPECTED_T7_ROWS}\n"
            f"Found:    {row_count}"
        )

    return {
        "feature_rows": row_count,
        "feature_unique_ids": len(ids),
    }


# ============================================================================
# SQLITE STAGING
# ============================================================================

def build_sqlite_staging(
    target_rows,
):

    remove_if_exists(
        SQLITE_PATH
    )

    connection = sqlite3.connect(
        SQLITE_PATH
    )

    try:

        cursor = connection.cursor()

        cursor.execute(
            "PRAGMA journal_mode = DELETE"
        )

        cursor.execute(
            "PRAGMA synchronous = NORMAL"
        )

        # --------------------------------------------------------
        # Target table
        # --------------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE target (
                ID TEXT PRIMARY KEY,
                creation_time TEXT NOT NULL,
                first_resolved_time TEXT,
                duration_seconds TEXT,
                event TEXT,
                endpoint_type TEXT,
                observation_endpoint TEXT,
                source_row_width TEXT
            )
            """
        )

        # --------------------------------------------------------
        # Raw-source feature table
        # --------------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE features (
                ID TEXT PRIMARY KEY,
                creation_time TEXT NOT NULL,
                creator TEXT,
                creator_detail TEXT,
                summary TEXT,
                description TEXT
            )
            """
        )

        # --------------------------------------------------------
        # Insert accepted T7 target.
        # --------------------------------------------------------

        for row in target_rows:

            cursor.execute(
                """
                INSERT INTO target (
                    ID,
                    creation_time,
                    first_resolved_time,
                    duration_seconds,
                    event,
                    endpoint_type,
                    observation_endpoint,
                    source_row_width
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["ID"],
                    row["Creation time"],
                    row["first_resolved_time"],
                    row["duration_seconds"],
                    row["event"],
                    row["endpoint_type"],
                    row["observation_endpoint"],
                    row["source_row_width"],
                ),
            )

        connection.commit()

        # --------------------------------------------------------
        # Insert already completed raw-source feature extraction.
        # --------------------------------------------------------

        with open(
            FEATURE_TEMP,
            "r",
            encoding="utf-8",
            newline="",
        ) as handle:

            reader = csv.DictReader(handle)

            for row in reader:

                cursor.execute(
                    """
                    INSERT INTO features (
                        ID,
                        creation_time,
                        creator,
                        creator_detail,
                        summary,
                        description
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["ID"],
                        row["Creation time"],
                        row["Creator"],
                        row["Creator Detail"],
                        row["Summary"],
                        row["Description"],
                    ),
                )

        connection.commit()

        # --------------------------------------------------------
        # Population checks.
        # --------------------------------------------------------

        target_count = cursor.execute(
            "SELECT COUNT(*) FROM target"
        ).fetchone()[0]

        feature_count = cursor.execute(
            "SELECT COUNT(*) FROM features"
        ).fetchone()[0]

        join_count = cursor.execute(
            """
            SELECT COUNT(*)
            FROM target AS t
            INNER JOIN features AS f
                ON t.ID = f.ID
            """
        ).fetchone()[0]

        missing_features = cursor.execute(
            """
            SELECT COUNT(*)
            FROM target AS t
            LEFT JOIN features AS f
                ON t.ID = f.ID
            WHERE f.ID IS NULL
            """
        ).fetchone()[0]

        extra_features = cursor.execute(
            """
            SELECT COUNT(*)
            FROM features AS f
            LEFT JOIN target AS t
                ON f.ID = t.ID
            WHERE t.ID IS NULL
            """
        ).fetchone()[0]

        if target_count != EXPECTED_T7_ROWS:
            fail(
                "Target SQLite population mismatch."
            )

        if feature_count != EXPECTED_T7_ROWS:
            fail(
                "Feature SQLite population mismatch."
            )

        if join_count != EXPECTED_T7_ROWS:
            fail(
                "Join population mismatch."
            )

        if missing_features != 0:
            fail(
                "Missing Creation-time feature rows: "
                f"{missing_features}"
            )

        if extra_features != 0:
            fail(
                "Unexpected feature rows: "
                f"{extra_features}"
            )

        # --------------------------------------------------------
        # Creation-time alignment.
        #
        # THIS IS THE CRITICAL CORRECTION.
        #
        # Target:
        #   timezone-naive UTC+05:30
        #
        # Raw feature:
        #   explicit UTC
        #
        # We compare the actual instants.
        # --------------------------------------------------------

        print()
        print(
            "Checking Creation-time alignment "
            "(target UTC+05:30 vs raw UTC)..."
        )

        mismatch_count = 0

        examples = []

        cursor.execute(
            """
            SELECT
                t.ID,
                t.creation_time,
                f.creation_time
            FROM target AS t
            INNER JOIN features AS f
                ON t.ID = f.ID
            """
        )

        for (
            ticket_id,
            target_creation,
            raw_creation,
        ) in cursor:

            if not creation_timestamps_equal(
                target_creation,
                raw_creation,
            ):

                mismatch_count += 1

                if len(examples) < 10:

                    examples.append(
                        {
                            "ID": ticket_id,
                            "target_creation":
                                target_creation,
                            "raw_creation":
                                raw_creation,
                        }
                    )

        if mismatch_count != 0:

            fail(
                "Creation-time semantic mismatch detected.\n"
                f"Mismatch count: {mismatch_count}\n"
                f"Examples:\n"
                f"{json.dumps(examples, indent=2)}"
            )

        print(
            "Creation-time alignment: PASS"
        )

        # --------------------------------------------------------
        # Known duplicate.
        # --------------------------------------------------------

        duplicate_count = cursor.execute(
            """
            SELECT COUNT(*)
            FROM features
            WHERE ID = ?
            """,
            (KNOWN_DUPLICATE_ID,),
        ).fetchone()[0]

        if duplicate_count != 1:

            fail(
                "Known duplicate ID 44606 is not represented "
                "exactly once in canonical feature staging."
            )

        return {
            "target_rows": target_count,
            "feature_rows": feature_count,
            "join_rows": join_count,
            "missing_feature_rows": missing_features,
            "extra_feature_rows": extra_features,
            "creation_time_mismatches": mismatch_count,
            "known_duplicate_id_feature_rows":
                duplicate_count,
        }

    finally:

        connection.close()


# ============================================================================
# FINAL MATERIALIZATION
# ============================================================================

def materialize_final_dataset():

    connection = sqlite3.connect(
        SQLITE_PATH
    )

    try:

        cursor = connection.cursor()

        remove_if_exists(
            FINAL_TEMP
        )

        with open(
            FINAL_TEMP,
            "w",
            encoding="utf-8",
            newline="",
        ) as output:

            writer = csv.writer(
                output,
                lineterminator="\n",
            )

            writer.writerow(
                FINAL_COLUMNS
            )

            cursor.execute(
                """
                SELECT
                    t.ID,
                    t.creation_time,
                    f.creator,
                    f.creator_detail,
                    f.summary,
                    f.description,
                    t.first_resolved_time,
                    t.duration_seconds,
                    t.event,
                    t.endpoint_type,
                    t.observation_endpoint,
                    t.source_row_width
                FROM target AS t
                INNER JOIN features AS f
                    ON t.ID = f.ID
                ORDER BY CAST(t.ID AS INTEGER)
                """
            )

            written = 0

            for row in cursor:

                writer.writerow(
                    row
                )

                written += 1

        if written != EXPECTED_T7_ROWS:

            fail(
                "Final dataset row count mismatch.\n"
                f"Expected: {EXPECTED_T7_ROWS}\n"
                f"Found:    {written}"
            )

        os.replace(
            FINAL_TEMP,
            FINAL_OUTPUT,
        )

        return written

    finally:

        connection.close()


# ============================================================================
# FINAL VALIDATION
# ============================================================================

def validate_final_dataset():

    row_count = 0

    ids = set()

    event_1 = 0
    event_0 = 0

    with open(
        FINAL_OUTPUT,
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:

        reader = csv.DictReader(handle)

        if reader.fieldnames != FINAL_COLUMNS:

            fail(
                "Final dataset schema mismatch.\n"
                f"Expected: {FINAL_COLUMNS}\n"
                f"Found:    {reader.fieldnames}"
            )

        for row in reader:

            row_count += 1

            ticket_id = row["ID"]

            if ticket_id in ids:

                fail(
                    "Duplicate ID in final dataset: "
                    f"{ticket_id}"
                )

            ids.add(ticket_id)

            # Final Creation representation is the accepted target
            # representation, so parse it with the target timezone rule.
            parse_target_creation_timestamp(
                row["Creation time"]
            )

            event = str(
                row["event"]
            ).strip()

            if event == "1":

                event_1 += 1

            elif event == "0":

                event_0 += 1

            else:

                fail(
                    "Unexpected event value: "
                    f"{event}"
                )

    if row_count != EXPECTED_T7_ROWS:

        fail(
            "Final row count mismatch."
        )

    if len(ids) != EXPECTED_T7_ROWS:

        fail(
            "Final unique-ID count mismatch."
        )

    if event_1 != EXPECTED_EVENT_ROWS:

        fail(
            "Final event count mismatch.\n"
            f"Expected: {EXPECTED_EVENT_ROWS}\n"
            f"Found:    {event_1}"
        )

    if event_0 != EXPECTED_CENSORED_ROWS:

        fail(
            "Final censored count mismatch.\n"
            f"Expected: {EXPECTED_CENSORED_ROWS}\n"
            f"Found:    {event_0}"
        )

    return {
        "rows": row_count,
        "unique_ids": len(ids),
        "event_1": event_1,
        "event_0": event_0,
    }


# ============================================================================
# MAIN
# ============================================================================

def main():

    started = time.time()

    print("=" * 78)
    print(
        "T7 MOD-003 — FINALIZE CREATION-TIME MODELING DATASET"
    )
    print("=" * 78)

    print()
    print(
        "Accepted T7 target:"
    )
    print(T7_TARGET)

    print()
    print(
        "Existing streamed Creation-time feature artifact:"
    )
    print(FEATURE_TEMP)

    print()
    print(
        "Final modeling dataset:"
    )
    print(FINAL_OUTPUT)

    print()
    print(
        "Frozen Creation-time features:"
    )

    for feature in FEATURE_COLUMNS:
        print(
            f"  - {feature}"
        )

    print()
    print(
        "Recovery mode:"
    )
    print(
        "  Raw 96 GB archive will NOT be rescanned."
    )
    print(
        "  Existing 513,816-row feature extraction will be reused."
    )
    print(
        "  Target Creation = timezone-naive UTC+05:30."
    )
    print(
        "  Raw Creation    = explicit UTC."
    )

    ensure_directories()

    # Do not delete the successful feature artifact.
    remove_if_exists(
        SQLITE_PATH
    )

    remove_if_exists(
        FINAL_TEMP
    )

    # --------------------------------------------------------
    # 1
    # --------------------------------------------------------

    print()
    print(
        "[1/4] Loading accepted T7 target..."
    )

    target_rows = load_target_artifact()

    print(
        f"Target rows: {len(target_rows):,}"
    )

    # --------------------------------------------------------
    # 2
    # --------------------------------------------------------

    print()
    print(
        "[2/4] Validating existing Creation-time feature extraction..."
    )

    feature_audit = validate_feature_artifact()

    for key, value in feature_audit.items():

        print(
            f"{key}: {value:,}"
        )

    # --------------------------------------------------------
    # 3
    # --------------------------------------------------------

    print()
    print(
        "[3/4] Building disk-backed SQLite join..."
    )

    join_audit = build_sqlite_staging(
        target_rows
    )

    for key, value in join_audit.items():

        print(
            f"{key}: {value:,}"
        )

    # --------------------------------------------------------
    # 4
    # --------------------------------------------------------

    print()
    print(
        "[4/4] Materializing final T7 modeling dataset..."
    )

    written = materialize_final_dataset()

    print(
        f"Rows written: {written:,}"
    )

    final_audit = validate_final_dataset()

    print()
    print(
        "Final validation:"
    )

    for key, value in final_audit.items():

        print(
            f"{key}: {value:,}"
        )

    # --------------------------------------------------------
    # Audit
    # --------------------------------------------------------

    elapsed = time.time() - started

    audit = {
        "operation": "T7_MOD-003",
        "status": "ACCEPTED",

        "task": "T7 Resolution-Time Estimation",

        "target_artifact": str(
            T7_TARGET
        ),

        "creation_feature_artifact": str(
            FEATURE_TEMP
        ),

        "final_output": str(
            FINAL_OUTPUT
        ),

        "feature_boundary": FEATURE_COLUMNS,

        "population": {
            "rows": EXPECTED_T7_ROWS,
            "event_1": EXPECTED_EVENT_ROWS,
            "event_0": EXPECTED_CENSORED_ROWS,
        },

        "timezone_contract": {
            "raw_creation": "UTC",
            "target_creation": "UTC+05:30",
            "comparison": "semantic_instant",
            "offset_seconds": 19800,
        },

        "feature_audit": feature_audit,

        "join_audit": join_audit,

        "final_audit": final_audit,

        "controls": {
            "raw_source_modified": False,
            "accepted_target_modified": False,
            "raw_archive_rescanned": False,
            "pandas_used": False,
            "full_raw_extraction": False,
            "disk_backed_join": True,
            "raw_creation_interpreted_as_utc": True,
            "target_creation_interpreted_as_utc_plus_0530": True,
            "raw_target_string_equality_required": False,
        },

        "known_duplicate_id": KNOWN_DUPLICATE_ID,

        "elapsed_seconds": elapsed,
    }

    with open(
        AUDIT_OUTPUT,
        "w",
        encoding="utf-8",
    ) as handle:

        json.dump(
            audit,
            handle,
            indent=2,
        )

        handle.write("\n")

    # Keep successful feature artifact.
    remove_if_exists(
        SQLITE_PATH
    )

    remove_if_exists(
        FINAL_TEMP
    )

    print()
    print("=" * 78)
    print(
        "T7 MOD-003 COMPLETE"
    )
    print("=" * 78)

    print()
    print(
        "Final modeling dataset:"
    )
    print(
        FINAL_OUTPUT
    )

    print()
    print(
        "MOD-003 audit:"
    )
    print(
        AUDIT_OUTPUT
    )

    print()
    print(
        f"Elapsed: {elapsed:.2f} seconds"
    )


if __name__ == "__main__":
    main()