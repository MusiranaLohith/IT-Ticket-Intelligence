#!/usr/bin/env python3

import csv
import os
import sys
from collections import Counter

# ---------------------------------------------------------------------
# T8 MOD-002
# Native Evidence / Semantic-State Verification
#
# READ-ONLY AUDIT
#
# Reads only the four frozen T8 derived artifacts.
# Does not access the raw Mozilla archive / raw CSV.
# Does not create derived datasets.
# Does not train models.
# Does not create targets or scores.
# ---------------------------------------------------------------------

csv.field_size_limit(sys.maxsize)


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

LAYER_A = (
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T8_LAYER_A_TICKET_EVIDENCE_derived.csv"
)

LAYER_B = (
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T8_LAYER_B_T6_QUERY_EVIDENCE_derived.csv"
)

LAYER_C = (
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T8_LAYER_C_T6_QUERY_CANDIDATE_EVIDENCE_derived.csv"
)

TICKET_DS = (
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "DTM-002_T8_TICKET_DECISION_SUPPORT_derived.csv"
)

FILES = {
    "Layer A": LAYER_A,
    "Layer B": LAYER_B,
    "Layer C": LAYER_C,
    "Ticket Decision Support": TICKET_DS,
}


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def is_blank(value):
    if value is None:
        return True

    text = str(value).strip()

    if text == "":
        return True

    return text.lower() in {
        "none",
        "null",
        "nan",
        "na",
        "n/a",
    }


def display_counter(counter, limit=30):
    if not counter:
        print("  <none>")
        return

    items = counter.most_common()

    for value, count in items[:limit]:
        print(f"  {value!r}: {count}")

    if len(items) > limit:
        print(
            f"  ... {len(items) - limit} additional "
            "distinct values"
        )


def classify_availability(value):
    """
    Descriptive normalization only.
    Raw values are also reported.

    This does NOT redefine dataset semantics.
    """
    if is_blank(value):
        return "BLANK_OR_NULL"

    text = str(value).strip().lower()

    if text in {"true", "1", "yes", "available"}:
        return "AVAILABLE"

    if text in {"false", "0", "no", "unavailable"}:
        return "UNAVAILABLE"

    return "OTHER"


def audit_file_exists(path):
    exists = os.path.isfile(path)

    print(f"  exists: {exists}")

    if exists:
        print(f"  size_bytes: {os.path.getsize(path)}")

    return exists


def profile_columns(path, columns):
    """
    Profile exact raw values for specified columns.
    """
    counters = {
        column: Counter()
        for column in columns
    }

    nonblank = Counter()
    rows = 0

    with open(
        path,
        "r",
        encoding="utf-8",
        newline=""
    ) as handle:

        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []

        missing_columns = [
            column
            for column in columns
            if column not in fieldnames
        ]

        if missing_columns:
            raise RuntimeError(
                f"Missing required columns: {missing_columns}"
            )

        for row in reader:
            rows += 1

            for column in columns:
                value = row.get(column, "")

                display_value = (
                    "<BLANK_OR_NULL>"
                    if is_blank(value)
                    else str(value).strip()
                )

                counters[column][display_value] += 1

                if not is_blank(value):
                    nonblank[column] += 1

    return rows, counters, nonblank


def profile_availability(path, columns):
    """
    Profile availability fields without assuming their encoding.
    """
    raw = {
        column: Counter()
        for column in columns
    }

    normalized = {
        column: Counter()
        for column in columns
    }

    rows = 0

    with open(
        path,
        "r",
        encoding="utf-8",
        newline=""
    ) as handle:

        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []

        missing_columns = [
            column
            for column in columns
            if column not in fieldnames
        ]

        if missing_columns:
            raise RuntimeError(
                f"Missing required columns: {missing_columns}"
            )

        for row in reader:
            rows += 1

            for column in columns:
                value = row.get(column, "")

                raw_value = (
                    "<BLANK_OR_NULL>"
                    if is_blank(value)
                    else str(value).strip()
                )

                raw[column][raw_value] += 1
                normalized[column][
                    classify_availability(value)
                ] += 1

    return rows, raw, normalized


# ---------------------------------------------------------------------
# Start
# ---------------------------------------------------------------------

print("=" * 78)
print("T8 MOD-002 — NATIVE EVIDENCE / SEMANTIC-STATE VERIFICATION")
print("=" * 78)

print("\nREAD-ONLY CONTRACT")
print("- Existing T8 derived artifacts only")
print("- No raw Mozilla archive access")
print("- No raw Mozilla CSV access")
print("- No artifact modification")
print("- No model training")
print("- No target creation")
print("- No universal T8 score creation")


# ---------------------------------------------------------------------
# 1. Artifact existence
# ---------------------------------------------------------------------

print("\n[1] REQUIRED ARTIFACT EXISTENCE")
print("-" * 78)

missing_files = []

for name, path in FILES.items():

    print(f"\n{name}")
    print(f"  path: {path}")

    if not audit_file_exists(path):
        missing_files.append(name)

if missing_files:
    print("\nSTATUS: FAIL")
    print(f"Missing artifacts: {missing_files}")
    sys.exit(1)


# ---------------------------------------------------------------------
# 2. Layer A — native task evidence
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[2] LAYER A — TICKET-LEVEL NATIVE TASK EVIDENCE")
print("=" * 78)

availability_columns = [
    "t2_available",
    "t3_available",
    "t4_available",
    "t5_available",
    "t7_available",
]

layer_a_target_columns = [
    "t2_target_priority",
    "t3_target_severity",
    "t4_target_assignee",
    "t5_target",
    "t7_first_resolved_time",
    "t7_duration_seconds",
    "t7_event",
    "t7_endpoint_type",
    "t7_observation_endpoint",
]

layer_a_rows, layer_a_raw, layer_a_normalized = (
    profile_availability(
        LAYER_A,
        availability_columns
    )
)

_, layer_a_targets, layer_a_target_nonblank = (
    profile_columns(
        LAYER_A,
        layer_a_target_columns
    )
)

print(f"\nRows scanned: {layer_a_rows}")


print("\n[2A] TASK AVAILABILITY — RAW VALUES")

for column in availability_columns:

    print(f"\n{column}")
    display_counter(layer_a_raw[column])


print("\n[2B] TASK AVAILABILITY — DESCRIPTIVE NORMALIZATION")

for column in availability_columns:

    print(f"\n{column}")
    display_counter(layer_a_normalized[column])


print("\n[2C] NATIVE TARGET / OUTCOME FIELD POPULATION")

for column in layer_a_target_columns:

    print(
        f"\n{column}: "
        f"nonblank={layer_a_target_nonblank[column]}"
    )

    display_counter(layer_a_targets[column])


# ---------------------------------------------------------------------
# 3. Ticket Decision Support
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[3] TICKET DECISION-SUPPORT REPRESENTATION")
print("=" * 78)

ticket_rows, ticket_raw, ticket_normalized = (
    profile_availability(
        TICKET_DS,
        availability_columns
    )
)

ticket_t8_columns = [
    "t8_prediction_boundary",
    "t8_missingness_semantics",
    "t8_provenance_preserved",
    "t8_record_type",
    "t8_native_grain",
    "t8_target",
    "t8_score",
]

_, ticket_t8_counts, ticket_t8_nonblank = (
    profile_columns(
        TICKET_DS,
        ticket_t8_columns
    )
)

print(f"\nRows scanned: {ticket_rows}")


print("\n[3A] TASK AVAILABILITY")

for column in availability_columns:

    print(f"\n{column}")
    print("RAW:")
    display_counter(ticket_raw[column])

    print("NORMALIZED:")
    display_counter(ticket_normalized[column])


print("\n[3B] T8 SEMANTIC METADATA")

for column in ticket_t8_columns:

    print(
        f"\n{column}: "
        f"nonblank={ticket_t8_nonblank[column]}"
    )

    display_counter(ticket_t8_counts[column])


# ---------------------------------------------------------------------
# 4. Layer B — query-level evidence
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[4] LAYER B — T6 QUERY-LEVEL EVIDENCE")
print("=" * 78)

layer_b_columns = [
    "t8_prediction_boundary",
    "t8_missingness_semantics",
    "t8_provenance_preserved",
    "t8_layer",
    "t8_grain",
    "t8_target",
    "t8_score",
]

layer_b_rows, layer_b_counts, layer_b_nonblank = (
    profile_columns(
        LAYER_B,
        layer_b_columns
    )
)

print(f"\nRows scanned: {layer_b_rows}")

for column in layer_b_columns:

    print(
        f"\n{column}: "
        f"nonblank={layer_b_nonblank[column]}"
    )

    display_counter(layer_b_counts[column])


# ---------------------------------------------------------------------
# 5. Layer C — query-candidate evidence
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[5] LAYER C — T6 QUERY-CANDIDATE EVIDENCE")
print("=" * 78)

layer_c_columns = [
    "candidate_role",
    "target_observed",
    "target_type",
    "sampling_protocol",
    "t8_prediction_boundary",
    "t8_missingness_semantics",
    "t8_provenance_preserved",
    "t8_layer",
    "t8_grain",
    "t8_target",
    "t8_score",
]

layer_c_rows, layer_c_counts, layer_c_nonblank = (
    profile_columns(
        LAYER_C,
        layer_c_columns
    )
)

print(f"\nRows scanned: {layer_c_rows}")

for column in layer_c_columns:

    print(
        f"\n{column}: "
        f"nonblank={layer_c_nonblank[column]}"
    )

    display_counter(layer_c_counts[column])


# ---------------------------------------------------------------------
# 5A. Preserve observable_non_positive semantics
# ---------------------------------------------------------------------
print("\n[5A] T6 OBSERVABLE-NON-POSITIVE SEMANTIC PRESERVATION")
print("-" * 78)

observable_non_positive_rows = 0
observable_non_positive_not_observed = 0

for value, count in layer_c_counts["candidate_role"].items():

    if value.lower() == "observable_non_positive":
        observable_non_positive_rows += count

for value, count in layer_c_counts["target_observed"].items():

    if value.lower() == "false":
        observable_non_positive_not_observed += count

print(
    "candidate_role = observable_non_positive: "
    f"{observable_non_positive_rows}"
)

print(
    "target_observed = false: "
    f"{observable_non_positive_not_observed}"
)

print(
    "Interpretation: observable_non_positive remains a native "
    "candidate-state label and is NOT reclassified as a true negative."
)


# ---------------------------------------------------------------------
# 6. Synthetic T8 target / score population
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[6] SYNTHETIC T8 TARGET / SCORE POPULATION CHECK")
print("=" * 78)

target_score_profiles = {
    "Ticket Decision Support": {
        "t8_target": ticket_t8_counts["t8_target"],
        "t8_score": ticket_t8_counts["t8_score"],
    },
    "Layer B": {
        "t8_target": layer_b_counts["t8_target"],
        "t8_score": layer_b_counts["t8_score"],
    },
    "Layer C": {
        "t8_target": layer_c_counts["t8_target"],
        "t8_score": layer_c_counts["t8_score"],
    },
}

populated_t8_fields = []

for artifact, fields in target_score_profiles.items():

    print(f"\n{artifact}")

    for field, counter in fields.items():

        nonblank = sum(
            count
            for value, count in counter.items()
            if value != "<BLANK_OR_NULL>"
        )

        print(
            f"  {field}: "
            f"nonblank={nonblank}"
        )

        if nonblank > 0:
            populated_t8_fields.append(
                (artifact, field, nonblank)
            )


if populated_t8_fields:

    print(
        "\nREVIEW FLAG: populated t8_target/t8_score "
        "values were observed."
    )

    for artifact, field, count in populated_t8_fields:
        print(
            f"  {artifact} -> {field}: "
            f"{count} populated rows"
        )

    print(
        "\nThese values are NOT interpreted as a valid "
        "universal T8 target or score by this audit."
    )

else:

    print(
        "\nNo populated t8_target/t8_score values "
        "were observed."
    )

    print(
        "This is consistent with the current T8 boundary: "
        "no synthetic universal target/score has been established."
    )


# ---------------------------------------------------------------------
# 7. Summary
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[7] MOD-002 EXECUTION SUMMARY")
print("=" * 78)

print(f"Layer A rows scanned: {layer_a_rows}")
print(f"Ticket Decision Support rows scanned: {ticket_rows}")
print(f"Layer B rows scanned: {layer_b_rows}")
print(f"Layer C rows scanned: {layer_c_rows}")

print("\nEvidence inspected:")
print("- T2/T3/T4/T5/T7 availability states")
print("- Native task target/outcome population")
print("- T7 event and observation-state representation")
print("- T8 prediction boundary")
print("- T8 missingness semantics")
print("- T8 provenance indicators")
print("- T8 native layer/grain metadata")
print("- Layer B query-level semantics")
print("- Layer C candidate semantics")
print("- observable_non_positive preservation")
print("- t8_target/t8_score population state")

print("\nNOT performed:")
print("- raw archive access")
print("- raw CSV access")
print("- model training")
print("- target construction")
print("- score construction")
print("- probability conversion")
print("- evidence fusion")
print("- artifact modification")

print("\nSTATUS: MOD-002 EXECUTION COMPLETE")