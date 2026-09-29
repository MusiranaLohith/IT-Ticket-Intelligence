from pathlib import Path
import csv
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

SOURCES = {
    "priority": (
        ROOT
        / "modeling/T8/mod036/op019/"
        "t8_mod036_op019_priority_predictions.csv"
    ),
    "assignment": (
        ROOT
        / "modeling/T8/mod036/op020/"
        "t8_mod036_op020_assignment_predictions.csv"
    ),
    "duplicate": (
        ROOT
        / "modeling/T8/mod036/op021/"
        "t8_mod036_op021_duplicate_component_predictions.csv"
    ),
    "resolution": (
        ROOT
        / "modeling/T8/mod036/op023/"
        "t8_mod036_op023_resolution_predictions.csv"
    ),
}

OUT_DIR = ROOT / "modeling/T8/mod036/op025"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REPORT = (
    OUT_DIR
    / "t8_mod036_op025_decision_engine_composition.json"
)

PREDICTIONS = (
    OUT_DIR
    / "t8_mod036_op025_decision_engine_predictions.csv"
)


def normalize(name):
    return (
        str(name)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def read_csv(path):
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline="",
    ) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        columns = reader.fieldnames or []

    return columns, rows


def resolve_column(columns, candidates, field_name):
    normalized = {
        normalize(column): column
        for column in columns
    }

    for candidate in candidates:
        key = normalize(candidate)

        if key in normalized:
            return normalized[key]

    raise RuntimeError(
        f"Could not resolve {field_name}.\n"
        f"Candidates: {candidates}\n"
        f"Available columns: {list(columns)}"
    )


def parse_float(value, field_name, row_number):
    try:
        return float(value)
    except (TypeError, ValueError):
        raise RuntimeError(
            f"Could not parse {field_name} "
            f"at row {row_number}: {value!r}"
        )


def parse_bool(value, field_name, row_number):
    value = str(value).strip().lower()

    if value in {
        "true",
        "1",
        "yes",
    }:
        return True

    if value in {
        "false",
        "0",
        "no",
    }:
        return False

    raise RuntimeError(
        f"Could not parse {field_name} "
        f"at row {row_number}: {value!r}"
    )


def load_component(component, path):
    columns, rows = read_csv(path)

    id_column = resolve_column(
        columns,
        (
            "id",
            "ticket_id",
            "bug_id",
        ),
        f"{component} ID",
    )

    data = {}

    for row_number, row in enumerate(
        rows,
        start=2,
    ):

        ticket_id = str(
            row[id_column]
        ).strip()

        if not ticket_id:
            raise RuntimeError(
                f"{component}: empty ID at row "
                f"{row_number}"
            )

        if ticket_id in data:
            raise RuntimeError(
                f"{component}: duplicate ID "
                f"{ticket_id!r}"
            )

        data[ticket_id] = row

    return columns, id_column, data


def priority_record(row, columns):
    predicted_column = resolve_column(
        columns,
        ("predicted_priority",),
        "predicted priority",
    )

    probabilities = {}

    for cls in (
        "P1",
        "P2",
        "P3",
        "P4",
        "P5",
    ):
        column = resolve_column(
            columns,
            (f"probability_{cls}",),
            f"priority probability {cls}",
        )

        probabilities[cls] = parse_float(
            row[column],
            column,
            0,
        )

    predicted = str(
        row[predicted_column]
    ).strip()

    if not predicted:
        return {
            "available": False,
            "state": "INSUFFICIENT_EVIDENCE",
            "recommendation": None,
            "probabilities": probabilities,
        }

    return {
        "available": True,
        "state": "SUPPORTED",
        "recommendation": predicted,
        "probabilities": probabilities,
    }


def assignment_record(row, columns):
    recommended_column = resolve_column(
        columns,
        ("recommended_assignee",),
        "recommended assignee",
    )

    score_column = resolve_column(
        columns,
        ("recommended_score",),
        "assignment recommendation score",
    )

    status_column = resolve_column(
        columns,
        ("status",),
        "assignment status",
    )

    target_present_column = resolve_column(
        columns,
        ("target_present",),
        "assignment target-present indicator",
    )

    recommended = str(
        row[recommended_column]
    ).strip()

    score = parse_float(
        row[score_column],
        score_column,
        0,
    )

    status = str(
        row[status_column]
    ).strip()

    target_present = parse_bool(
        row[target_present_column],
        target_present_column,
        0,
    )

    # The native T4 semantics explicitly distinguish
    # unavailable candidate evidence from a negative result.
    if status.lower() in {
        "no_recommendation",
        "unavailable",
        "insufficient_evidence",
    }:
        state = "INSUFFICIENT_EVIDENCE"

    elif not recommended:
        state = "INSUFFICIENT_EVIDENCE"

    elif not target_present:
        # A missing historical target candidate is not a
        # negative assignment prediction.
        state = "SUPPORTED"

    else:
        state = "SUPPORTED"

    return {
        "available": True,
        "state": state,
        "recommendation": (
            recommended
            if recommended
            else None
        ),
        "score": score,
        "status": status,
        "target_present": target_present,
    }


def duplicate_record(row, columns):
    probability_column = resolve_column(
        columns,
        ("p_duplicate",),
        "duplicate probability",
    )

    probability = parse_float(
        row[probability_column],
        probability_column,
        0,
    )

    if (
        probability < 0.0
        or probability > 1.0
    ):
        raise RuntimeError(
            "Duplicate probability outside [0,1]."
        )

    # Do not create an automation threshold.
    # Native calibrated probability is retained as
    # evidence only.
    return {
        "available": True,
        "state": "SUPPORTED",
        "recommendation": {
            "p_duplicate": probability
        },
    }


def resolution_record(row, columns):
    median_column = resolve_column(
        columns,
        (
            "predicted_median_survival_seconds",
        ),
        "predicted median survival",
    )

    short_column = resolve_column(
        columns,
        (
            "survival_probability_at_211583_seconds",
        ),
        "short survival probability",
    )

    medium_column = resolve_column(
        columns,
        (
            "survival_probability_at_1780179_seconds",
        ),
        "medium survival probability",
    )

    long_column = resolve_column(
        columns,
        (
            "survival_probability_at_14608619_seconds",
        ),
        "long survival probability",
    )

    context_column = resolve_column(
        columns,
        ("resolution_context",),
        "resolution context",
    )

    median = parse_float(
        row[median_column],
        median_column,
        0,
    )

    short = parse_float(
        row[short_column],
        short_column,
        0,
    )

    medium = parse_float(
        row[medium_column],
        medium_column,
        0,
    )

    long = parse_float(
        row[long_column],
        long_column,
        0,
    )

    context = str(
        row[context_column]
    ).strip()

    for value, name in (
        (short, "short survival"),
        (medium, "medium survival"),
        (long, "long survival"),
    ):
        if not 0.0 <= value <= 1.0:
            raise RuntimeError(
                f"{name} outside [0,1]."
            )

    if not (
        short >= medium >= long
    ):
        raise RuntimeError(
            "T7 survival ordering violated."
        )

    return {
        "available": True,
        "state": "SUPPORTED",
        "recommendation": {
            "predicted_median_survival_seconds": median,
            "survival_probability_at_211583_seconds": short,
            "survival_probability_at_1780179_seconds": medium,
            "survival_probability_at_14608619_seconds": long,
            "resolution_context": context,
        },
    }


def determine_overall_state(
    available_components,
):
    count = len(
        available_components
    )

    if count == 0:
        return "UNAVAILABLE"

    if count == 1:
        return "INSUFFICIENT_EVIDENCE"

    return "SUPPORTED"


def main():

    print("=" * 80)
    print("T8 DECISION ENGINE — MOD-036 OP-025")
    print("Decision Engine Composition Baseline")
    print("=" * 80)

    # ------------------------------------------------------------------
    # 1. Load all four established component outputs
    # ------------------------------------------------------------------

    loaded = {}

    for component, path in SOURCES.items():

        print(f"\nLoading {component.upper()} component")
        print("-" * 80)
        print(f"  path: {path}")

        columns, id_column, data = load_component(
            component,
            path,
        )

        loaded[component] = {
            "columns": columns,
            "id_column": id_column,
            "data": data,
        }

        print(f"  rows: {len(data)}")
        print(f"  ID column: {id_column}")

    # ------------------------------------------------------------------
    # 2. Construct union population
    # ------------------------------------------------------------------

    union_ids = set()

    for component in loaded:
        union_ids.update(
            loaded[component]["data"].keys()
        )

    print("\nDecision-engine population")
    print("-" * 80)
    print(
        f"  union tickets: {len(union_ids)}"
    )

    # ------------------------------------------------------------------
    # 3. Compose native evidence
    # ------------------------------------------------------------------

    output_rows = []

    state_counts = {
        "SUPPORTED": 0,
        "CONFLICTING": 0,
        "INSUFFICIENT_EVIDENCE": 0,
        "UNAVAILABLE": 0,
    }

    component_availability = {
        "priority": 0,
        "assignment": 0,
        "duplicate": 0,
        "resolution": 0,
    }

    for ticket_id in sorted(union_ids):

        priority = None
        assignment = None
        duplicate = None
        resolution = None

        available = []

        # --------------------------------------------------------------
        # Priority
        # --------------------------------------------------------------

        if ticket_id in loaded["priority"]["data"]:

            row = loaded["priority"]["data"][
                ticket_id
            ]

            priority = priority_record(
                row,
                loaded["priority"]["columns"],
            )

            available.append("priority")
            component_availability["priority"] += 1

        # --------------------------------------------------------------
        # Assignment
        # --------------------------------------------------------------

        if ticket_id in loaded["assignment"]["data"]:

            row = loaded["assignment"]["data"][
                ticket_id
            ]

            assignment = assignment_record(
                row,
                loaded["assignment"]["columns"],
            )

            available.append("assignment")
            component_availability["assignment"] += 1

        # --------------------------------------------------------------
        # Duplicate
        # --------------------------------------------------------------

        if ticket_id in loaded["duplicate"]["data"]:

            row = loaded["duplicate"]["data"][
                ticket_id
            ]

            duplicate = duplicate_record(
                row,
                loaded["duplicate"]["columns"],
            )

            available.append("duplicate")
            component_availability["duplicate"] += 1

        # --------------------------------------------------------------
        # Resolution
        # --------------------------------------------------------------

        if ticket_id in loaded["resolution"]["data"]:

            row = loaded["resolution"]["data"][
                ticket_id
            ]

            resolution = resolution_record(
                row,
                loaded["resolution"]["columns"],
            )

            available.append("resolution")
            component_availability["resolution"] += 1

        # --------------------------------------------------------------
        # Cross-task consistency
        # --------------------------------------------------------------
        #
        # There is currently no validated universal relation that
        # permits priority, assignment, duplicate probability, and
        # survival probability to be mathematically combined.
        #
        # Therefore:
        # - no arbitrary conflict is declared
        # - no probabilities are averaged
        # - no weights are introduced
        #
        # Cross-task state is consequently:
        #   SUPPORTED when multiple independent task signals exist
        #   INSUFFICIENT_EVIDENCE when only one exists
        #   UNAVAILABLE when none exists
        #
        # This is an evidence-state classification, not a performance
        # claim.

        overall_state = determine_overall_state(
            available
        )

        state_counts[overall_state] += 1

        # --------------------------------------------------------------
        # Structured output
        # --------------------------------------------------------------

        priority_recommendation = ""

        if priority is not None:
            priority_recommendation = (
                priority["recommendation"]
                or ""
            )

        assignment_recommendation = ""

        if assignment is not None:
            assignment_recommendation = (
                assignment["recommendation"]
                or ""
            )

        duplicate_probability = ""

        if duplicate is not None:
            duplicate_probability = (
                duplicate["recommendation"]
                ["p_duplicate"]
            )

        resolution_median = ""

        resolution_short = ""
        resolution_medium = ""
        resolution_long = ""
        resolution_context = ""

        if resolution is not None:

            resolution_median = (
                resolution["recommendation"]
                ["predicted_median_survival_seconds"]
            )

            resolution_short = (
                resolution["recommendation"]
                ["survival_probability_at_211583_seconds"]
            )

            resolution_medium = (
                resolution["recommendation"]
                ["survival_probability_at_1780179_seconds"]
            )

            resolution_long = (
                resolution["recommendation"]
                ["survival_probability_at_14608619_seconds"]
            )

            resolution_context = (
                resolution["recommendation"]
                ["resolution_context"]
            )

        output_rows.append(
            {
                "id": ticket_id,

                "available_components":
                    "|".join(available),

                "evidence_count":
                    len(available),

                "overall_triage_state":
                    overall_state,

                "priority_state":
                    (
                        priority["state"]
                        if priority is not None
                        else "UNAVAILABLE"
                    ),

                "priority_recommendation":
                    priority_recommendation,

                "assignment_state":
                    (
                        assignment["state"]
                        if assignment is not None
                        else "UNAVAILABLE"
                    ),

                "assignment_recommendation":
                    assignment_recommendation,

                "assignment_status":
                    (
                        assignment["status"]
                        if assignment is not None
                        else ""
                    ),

                "assignment_target_present":
                    (
                        assignment["target_present"]
                        if assignment is not None
                        else ""
                    ),

                "duplicate_state":
                    (
                        duplicate["state"]
                        if duplicate is not None
                        else "UNAVAILABLE"
                    ),

                "p_duplicate":
                    duplicate_probability,

                "resolution_state":
                    (
                        resolution["state"]
                        if resolution is not None
                        else "UNAVAILABLE"
                    ),

                "predicted_median_survival_seconds":
                    resolution_median,

                "survival_probability_at_211583_seconds":
                    resolution_short,

                "survival_probability_at_1780179_seconds":
                    resolution_medium,

                "survival_probability_at_14608619_seconds":
                    resolution_long,

                "resolution_context":
                    resolution_context,

                # Explicitly preserve that no cross-task
                # compatibility relation has been established.
                "cross_task_consistency":
                    (
                        "SUPPORTED"
                        if len(available) >= 2
                        else (
                            "INSUFFICIENT_EVIDENCE"
                            if len(available) == 1
                            else "UNAVAILABLE"
                        )
                    ),
            }
        )

    # ------------------------------------------------------------------
    # 4. Save composed decision-engine population
    # ------------------------------------------------------------------

    fieldnames = [
        "id",
        "available_components",
        "evidence_count",
        "overall_triage_state",

        "priority_state",
        "priority_recommendation",

        "assignment_state",
        "assignment_recommendation",
        "assignment_status",
        "assignment_target_present",

        "duplicate_state",
        "p_duplicate",

        "resolution_state",
        "predicted_median_survival_seconds",
        "survival_probability_at_211583_seconds",
        "survival_probability_at_1780179_seconds",
        "survival_probability_at_14608619_seconds",
        "resolution_context",

        "cross_task_consistency",
    ]

    with PREDICTIONS.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            output_rows
        )

    # ------------------------------------------------------------------
    # 5. Availability distribution
    # ------------------------------------------------------------------

    availability_distribution = {}

    for row in output_rows:

        pattern = (
            row["available_components"]
            if row["available_components"]
            else "NONE"
        )

        availability_distribution[
            pattern
        ] = (
            availability_distribution.get(
                pattern,
                0,
            )
            + 1
        )

    print("\nComponent availability")
    print("-" * 80)

    for component, count in (
        component_availability.items()
    ):
        print(
            f"  {component:<15} "
            f"{count:>8}"
        )

    print("\nOverall evidence-state distribution")
    print("-" * 80)

    for state, count in state_counts.items():
        print(
            f"  {state:<25} "
            f"{count:>8}"
        )

    print("\nEvidence-pattern distribution")
    print("-" * 80)

    for pattern, count in sorted(
        availability_distribution.items(),
        key=lambda item: (
            -item[1],
            item[0],
        ),
    ):
        print(
            f"  {pattern:<45} "
            f"{count:>8}"
        )

    # ------------------------------------------------------------------
    # 6. Save report
    # ------------------------------------------------------------------

    report = {
        "operation": "MOD-036 OP-025",
        "operation_name": (
            "Decision Engine Composition Baseline"
        ),
        "status": "PASS",

        "population": {
            "union_rows": len(union_ids),
        },

        "component_availability":
            component_availability,

        "overall_evidence_states":
            state_counts,

        "evidence_patterns":
            availability_distribution,

        "decision_engine_semantics": {
            "variable_evidence_population": True,
            "missing_evidence_is_unavailable": True,
            "native_task_outputs_preserved": True,
            "probability_averaging": False,
            "arbitrary_weights": False,
            "synthetic_universal_target": False,
            "cross_task_compatibility_assumed": False,
        },

        "structured_outputs": {
            "priority_recommendation": True,
            "assignment_recommendation": True,
            "duplicate_recommendation": True,
            "resolution_context": True,
            "overall_triage_recommendation": True,
        },

        "controls": {
            "new_model_fitted": False,
            "training_performed": False,
            "test_data_used_for_model_selection": False,
            "post_creation_features_added": False,
            "censored_cases_relabelled": False,
            "native_probability_semantics_preserved": True,
        },

        "outputs": {
            "predictions": str(
                PREDICTIONS.relative_to(ROOT)
            ),
            "report": str(
                REPORT.relative_to(ROOT)
            ),
        },

        "next_operation": (
            "MOD-036 OP-026 — "
            "Decision Engine Validation and Closure"
        ),
    }

    REPORT.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nArtifacts")
    print("-" * 80)
    print(f"  report:      {REPORT}")
    print(f"  predictions: {PREDICTIONS}")

    print("\nStatus: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()