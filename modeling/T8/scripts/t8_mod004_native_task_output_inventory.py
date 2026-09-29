#!/usr/bin/env python3

import csv
import sys
from collections import Counter

csv.field_size_limit(sys.maxsize)

# ---------------------------------------------------------------------
# T8 MOD-004
# Native Task-Output / Evidence-Field Inventory
#
# READ-ONLY AUDIT
# ---------------------------------------------------------------------

LAYER_A = (
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T8_LAYER_A_TICKET_EVIDENCE_derived.csv"
)

TASK_FIELDS = {
    "T2": [
        "t2_available",
        "t2_target_priority",
        "t2_target_priority_time",
        "t2_target_elapsed_seconds",
        "t2_prediction_cutoff",
        "t2_horizon_hours",
        "t2_target_definition",
        "t2_contract",
        "t2_source_artifact",
        "t2_Product_historical",
        "t2_Product_historical_available",
        "t2_Component_historical",
        "t2_Component_historical_available",
        "t2_Priority_historical",
        "t2_Priority_historical_available",
        "t2_Status_historical",
        "t2_Status_historical_available",
        "t2_Keywords_historical",
        "t2_Keywords_historical_available",
        "t2_Blocks_historical",
        "t2_Blocks_historical_available",
        "t2_CC_historical",
        "t2_CC_historical_available",
    ],
    "T3": [
        "t3_available",
        "t3_target_severity",
        "t3_target_time",
        "t3_target_removed_severity",
        "t3_target_actor",
        "t3_target_history_event_index",
        "t3_target_event_date",
        "t3_migration_excluded",
    ],
    "T4": [
        "t4_available",
        "t4_target_assignee",
        "t4_target_assignment_time",
        "t4_target_event_index",
        "t4_target_change_index",
    ],
    "T5": [
        "t5_available",
        "t5_target",
        "t5_target_event_index",
        "t5_target_change_index",
        "t5_target_time",
        "t5_target_actor",
    ],
    "T7": [
        "t7_available",
        "t7_first_resolved_time",
        "t7_duration_seconds",
        "t7_event",
        "t7_endpoint_type",
        "t7_observation_endpoint",
        "t7_source_row_width",
    ],
}

TARGET_FIELDS = {
    "T2": ["t2_target_priority"],
    "T3": ["t3_target_severity"],
    "T4": ["t4_target_assignee"],
    "T5": ["t5_target"],
    "T7": [
        "t7_first_resolved_time",
        "t7_duration_seconds",
        "t7_event",
    ],
}

TIME_FIELDS = [
    "creation_time",
    "t2_target_priority_time",
    "t3_target_time",
    "t3_target_event_date",
    "t4_target_assignment_time",
    "t5_target_time",
    "t7_first_resolved_time",
    "t7_observation_endpoint",
]

SYNTHETIC_T8_FIELDS = [
    "t8_target",
    "t8_score",
]


def is_blank(value):
    if value is None:
        return True

    text = str(value).strip()

    return (
        text == ""
        or text.lower() in {
            "none",
            "null",
            "nan",
            "na",
            "n/a",
        }
    )


def display_value(value):
    if is_blank(value):
        return "<BLANK_OR_NULL>"

    return str(value).strip()


def population_stats(counter, rows):
    nonblank = rows - counter.get(
        "<BLANK_OR_NULL>",
        0,
    )

    rate = (
        nonblank / rows * 100
        if rows
        else 0
    )

    return nonblank, rate


print("=" * 78)
print("T8 MOD-004 — NATIVE TASK-OUTPUT / EVIDENCE-FIELD INVENTORY")
print("=" * 78)

print("\nREAD-ONLY CONTRACT")
print("- Existing Layer A T8 derived artifact only")
print("- No raw Mozilla archive access")
print("- No raw Mozilla CSV access")
print("- No artifact modification")
print("- No target construction")
print("- No score construction")
print("- No model training")
print("- No evidence fusion")
print("- Native target/outcome fields are not treated as predictions")


# ---------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------

print("\n[1] INPUT ARTIFACT")
print("-" * 78)
print(f"path: {LAYER_A}")

with open(
    LAYER_A,
    "r",
    encoding="utf-8",
    newline="",
) as handle:

    reader = csv.DictReader(handle)
    fieldnames = reader.fieldnames or []

    print(f"columns: {len(fieldnames)}")

    missing = []

    for task, fields in TASK_FIELDS.items():
        for field in fields:
            if field not in fieldnames:
                missing.append(field)

    if missing:
        print("\nSTATUS: FAIL")
        print("Missing required fields:")
        for field in missing:
            print(f"- {field}")
        sys.exit(1)

    print("required native task fields: PRESENT")

    for field in SYNTHETIC_T8_FIELDS:
        if field not in fieldnames:
            print(
                f"{field}: NOT PRESENT IN LAYER A SCHEMA"
            )
        else:
            print(
                f"{field}: PRESENT IN LAYER A SCHEMA"
            )


# ---------------------------------------------------------------------
# Scan
# ---------------------------------------------------------------------

rows = 0

field_counters = {
    field: Counter()
    for fields in TASK_FIELDS.values()
    for field in fields
}

task_available_counts = Counter()

distinct_values = {
    field: Counter()
    for fields in TASK_FIELDS.values()
    for field in fields
}

target_population_counts = Counter()

time_field_nonblank = Counter()

synthetic_t8_counts = {
    field: Counter()
    for field in SYNTHETIC_T8_FIELDS
}


with open(
    LAYER_A,
    "r",
    encoding="utf-8",
    newline="",
) as handle:

    reader = csv.DictReader(handle)

    for row in reader:

        rows += 1

        # -------------------------------------------------------------
        # Native task fields
        # -------------------------------------------------------------

        for task, fields in TASK_FIELDS.items():

            for field in fields:

                value = row.get(field, "")

                shown = display_value(value)

                field_counters[field][shown] += 1

                if not is_blank(value):
                    distinct_values[field][shown] += 1

        # -------------------------------------------------------------
        # Task availability
        # -------------------------------------------------------------

        for task in TASK_FIELDS:

            field = f"{task.lower()}_available"

            if not is_blank(row.get(field, "")):
                task_available_counts[task] += 1

        # -------------------------------------------------------------
        # Target/outcome populations
        # -------------------------------------------------------------

        for task, fields in TARGET_FIELDS.items():

            for field in fields:

                if not is_blank(row.get(field, "")):
                    target_population_counts[field] += 1

        # -------------------------------------------------------------
        # Time fields
        # -------------------------------------------------------------

        for field in TIME_FIELDS:

            if field in fieldnames:

                if not is_blank(row.get(field, "")):
                    time_field_nonblank[field] += 1

        # -------------------------------------------------------------
        # Synthetic T8 fields
        # -------------------------------------------------------------

        for field in SYNTHETIC_T8_FIELDS:

            if field in fieldnames:

                value = row.get(field, "")

                synthetic_t8_counts[field][
                    display_value(value)
                ] += 1


# ---------------------------------------------------------------------
# Population
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[2] POPULATION")
print("=" * 78)

print(f"rows scanned: {rows}")


# ---------------------------------------------------------------------
# Native task availability
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[3] TASK AVAILABILITY RECHECK")
print("=" * 78)

for task in ["T2", "T3", "T4", "T5", "T7"]:

    field = f"{task.lower()}_available"

    count = task_available_counts[task]

    rate = (
        count / rows * 100
        if rows
        else 0
    )

    print(
        f"{task}: "
        f"{count}/{rows} "
        f"({rate:.6f}%) "
        f"via {field}"
    )


# ---------------------------------------------------------------------
# Native field population
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[4] NATIVE FIELD POPULATION")
print("=" * 78)

print(
    "Nonblank population for each native task field."
)

for task, fields in TASK_FIELDS.items():

    print(f"\n{task}")

    for field in fields:

        counter = field_counters[field]

        nonblank, rate = population_stats(
            counter,
            rows,
        )

        print(
            f"  {field}: "
            f"{nonblank}/{rows} "
            f"({rate:.6f}%)"
        )


# ---------------------------------------------------------------------
# Target/outcome fields
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[5] NATIVE TARGET / OUTCOME FIELDS")
print("=" * 78)

print(
    "These are observed task target/outcome fields. "
    "They are NOT interpreted as prediction outputs."
)

for task, fields in TARGET_FIELDS.items():

    print(f"\n{task}")

    for field in fields:

        count = target_population_counts[field]

        rate = (
            count / rows * 100
            if rows
            else 0
        )

        print(
            f"  {field}: "
            f"{count}/{rows} "
            f"({rate:.6f}%)"
        )


# ---------------------------------------------------------------------
# Distinct native target values
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[6] NATIVE TARGET / OUTCOME VALUE STRUCTURE")
print("=" * 78)

for task, fields in TARGET_FIELDS.items():

    print(f"\n{task}")

    for field in fields:

        counter = distinct_values[field]

        print(f"  {field}:")

        if not counter:
            print("    <NO NONBLANK VALUES>")
            continue

        for value, count in counter.most_common(30):

            rate = (
                count / rows * 100
                if rows
                else 0
            )

            print(
                f"    {value!r}: "
                f"{count} "
                f"({rate:.6f}%)"
            )

        if len(counter) > 30:
            print(
                f"    ... "
                f"{len(counter) - 30} additional distinct values"
            )


# ---------------------------------------------------------------------
# Historical evidence fields
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[7] T2 HISTORICAL EVIDENCE FIELD AVAILABILITY")
print("=" * 78)

t2_historical_fields = [
    "t2_Product_historical",
    "t2_Product_historical_available",
    "t2_Component_historical",
    "t2_Component_historical_available",
    "t2_Priority_historical",
    "t2_Priority_historical_available",
    "t2_Status_historical",
    "t2_Status_historical_available",
    "t2_Keywords_historical",
    "t2_Keywords_historical_available",
    "t2_Blocks_historical",
    "t2_Blocks_historical_available",
    "t2_CC_historical",
    "t2_CC_historical_available",
]

for field in t2_historical_fields:

    count = rows - field_counters[field].get(
        "<BLANK_OR_NULL>",
        0,
    )

    rate = (
        count / rows * 100
        if rows
        else 0
    )

    print(
        f"{field}: "
        f"{count}/{rows} "
        f"({rate:.6f}%)"
    )


# ---------------------------------------------------------------------
# Time / temporal fields
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[8] TEMPORAL FIELD POPULATION")
print("=" * 78)

for field in TIME_FIELDS:

    if field not in fieldnames:
        continue

    count = time_field_nonblank[field]

    rate = (
        count / rows * 100
        if rows
        else 0
    )

    print(
        f"{field}: "
        f"{count}/{rows} "
        f"({rate:.6f}%)"
    )


# ---------------------------------------------------------------------
# Synthetic T8 check
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[9] SYNTHETIC T8 TARGET / SCORE CHECK")
print("=" * 78)

for field in SYNTHETIC_T8_FIELDS:

    if field not in fieldnames:

        print(
            f"{field}: FIELD NOT PRESENT"
        )

        continue

    counter = synthetic_t8_counts[field]

    populated = rows - counter.get(
        "<BLANK_OR_NULL>",
        0,
    )

    print(
        f"{field}: "
        f"populated={populated}, "
        f"blank_or_null={counter.get('<BLANK_OR_NULL>', 0)}"
    )

    if populated == 0:
        print(
            "  STATUS: UNPOPULATED"
        )
    else:
        print(
            "  STATUS: POPULATED — INVESTIGATION REQUIRED"
        )


# ---------------------------------------------------------------------
# Interpretation boundary
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[10] INTERPRETATION BOUNDARY")
print("=" * 78)

print(
    "This operation inventories native evidence and outcome fields."
)

print(
    "Observed task target/outcome fields are not treated as "
    "predictions."
)

print(
    "No predictive score is inferred from a target/outcome field."
)

print(
    "No probability conversion is performed."
)

print(
    "No T8 universal target or score is constructed."
)

print(
    "No evaluation population is selected."
)


# ---------------------------------------------------------------------
# Final
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[11] MOD-004 EXECUTION SUMMARY")
print("=" * 78)

print(f"Rows scanned: {rows}")

print("\nComputed:")
print("- native task field population")
print("- native target/outcome population")
print("- native target/outcome value structure")
print("- T2 historical evidence availability")
print("- temporal field population")
print("- synthetic T8 target/score presence check")

print("\nNOT performed:")
print("- target construction")
print("- prediction generation")
print("- score construction")
print("- probability conversion")
print("- evidence fusion")
print("- evaluation-population selection")
print("- model training")
print("- raw archive access")
print("- artifact modification")

print("\nSTATUS: MOD-004 EXECUTION COMPLETE")