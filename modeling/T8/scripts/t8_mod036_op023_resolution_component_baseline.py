from pathlib import Path
import csv
import json

import numpy as np


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

SOURCE = ROOT / "modeling/T8/t8_mod029_t7_oof.csv"

OUT_DIR = ROOT / "modeling/T8/mod036/op023"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REPORT = (
    OUT_DIR
    / "t8_mod036_op023_resolution_component_baseline.json"
)

PREDICTIONS = (
    OUT_DIR
    / "t8_mod036_op023_resolution_predictions.csv"
)


# Native T7 horizons established in OP-022.
HORIZONS = {
    "short": 211583,
    "medium": 1780179,
    "long": 14608619,
}


def normalize(name):
    return (
        str(name)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


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
        value = float(value)
    except (TypeError, ValueError):
        raise RuntimeError(
            f"Could not parse {field_name} "
            f"at row {row_number}: {value!r}"
        )

    if not np.isfinite(value):
        raise RuntimeError(
            f"Non-finite {field_name} "
            f"at row {row_number}: {value!r}"
        )

    return value


def classify_resolution_context(
    short_survival,
    medium_survival,
    long_survival,
):
    """
    Descriptive state only.

    These states are NOT learned labels and are NOT
    automation thresholds.

    They describe the shape of the native T7
    survival evidence without converting it into
    a binary resolution probability.
    """

    if (
        short_survival >= 0.75
        and medium_survival >= 0.50
        and long_survival >= 0.25
    ):
        return "LONGER_RESOLUTION_HORIZON"

    if (
        short_survival < 0.25
        and medium_survival < 0.10
    ):
        return "EARLIER_RESOLUTION_HORIZON"

    if (
        short_survival < 0.50
        and medium_survival >= 0.10
    ):
        return "INTERMEDIATE_RESOLUTION_HORIZON"

    return "MIXED_RESOLUTION_EVIDENCE"


def main():

    print("=" * 80)
    print("T8 DECISION ENGINE — MOD-036 OP-023")
    print("Resolution Decision Component Baseline")
    print("=" * 80)

    # ------------------------------------------------------------------
    # 1. Load native T7 OOF
    # ------------------------------------------------------------------

    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)

    with SOURCE.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        rows = list(reader)
        columns = reader.fieldnames or []

    print("\nNative T7 OOF source")
    print("-" * 80)
    print(f"  path: {SOURCE}")
    print(f"  rows: {len(rows)}")
    print(f"  columns: {len(columns)}")

    # ------------------------------------------------------------------
    # 2. Resolve exact native T7 fields
    # ------------------------------------------------------------------

    id_column = resolve_column(
        columns,
        (
            "ID",
            "id",
            "ticket_id",
            "bug_id",
        ),
        "T7 ID",
    )

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
        "short-horizon survival probability",
    )

    medium_column = resolve_column(
        columns,
        (
            "survival_probability_at_1780179_seconds",
        ),
        "medium-horizon survival probability",
    )

    long_column = resolve_column(
        columns,
        (
            "survival_probability_at_14608619_seconds",
        ),
        "long-horizon survival probability",
    )

    boundary_column = resolve_column(
        columns,
        (
            "prediction_boundary",
        ),
        "prediction boundary",
    )

    print("\nResolved native T7 fields")
    print("-" * 80)
    print(f"  ID:             {id_column}")
    print(f"  median survival:{median_column}")
    print(f"  short horizon:  {short_column}")
    print(f"  medium horizon: {medium_column}")
    print(f"  long horizon:   {long_column}")
    print(f"  boundary:       {boundary_column}")

    # ------------------------------------------------------------------
    # 3. Population integrity
    # ------------------------------------------------------------------

    ids = [
        str(row[id_column]).strip()
        for row in rows
    ]

    unique_ids = set(ids)

    duplicate_ids = (
        len(ids)
        - len(unique_ids)
    )

    print("\nPopulation integrity")
    print("-" * 80)
    print(f"  rows:          {len(rows)}")
    print(f"  unique IDs:    {len(unique_ids)}")
    print(f"  duplicate IDs: {duplicate_ids}")

    if duplicate_ids != 0:
        raise RuntimeError(
            "Duplicate IDs detected in native T7 OOF."
        )

    # ------------------------------------------------------------------
    # 4. Parse native T7 predictions
    # ------------------------------------------------------------------

    median_survival = []
    short_survival = []
    medium_survival = []
    long_survival = []
    boundaries = []

    for row_number, row in enumerate(
        rows,
        start=2,
    ):

        median_value = parse_float(
            row[median_column],
            median_column,
            row_number,
        )

        short_value = parse_float(
            row[short_column],
            short_column,
            row_number,
        )

        medium_value = parse_float(
            row[medium_column],
            medium_column,
            row_number,
        )

        long_value = parse_float(
            row[long_column],
            long_column,
            row_number,
        )

        boundary = str(
            row[boundary_column]
        ).strip()

        median_survival.append(
            median_value
        )

        short_survival.append(
            short_value
        )

        medium_survival.append(
            medium_value
        )

        long_survival.append(
            long_value
        )

        boundaries.append(boundary)

    median_survival = np.asarray(
        median_survival,
        dtype=float,
    )

    short_survival = np.asarray(
        short_survival,
        dtype=float,
    )

    medium_survival = np.asarray(
        medium_survival,
        dtype=float,
    )

    long_survival = np.asarray(
        long_survival,
        dtype=float,
    )

    # ------------------------------------------------------------------
    # 5. Semantic validation
    # ------------------------------------------------------------------

    if np.any(
        median_survival < 0
    ):
        raise RuntimeError(
            "Negative predicted survival time detected."
        )

    for name, values in (
        (
            "short-horizon survival",
            short_survival,
        ),
        (
            "medium-horizon survival",
            medium_survival,
        ),
        (
            "long-horizon survival",
            long_survival,
        ),
    ):

        if np.any(
            (values < 0.0)
            | (values > 1.0)
        ):
            raise RuntimeError(
                f"{name} contains values outside [0,1]."
            )

    unexpected_boundaries = sorted(
        set(boundaries)
        - {"Creation"}
    )

    if unexpected_boundaries:
        raise RuntimeError(
            "Unexpected prediction boundaries found: "
            f"{unexpected_boundaries}"
        )

    # Survival probability should generally decrease
    # as the time horizon increases.
    monotonic_violations = int(
        np.sum(
            (short_survival < medium_survival)
            | (
                medium_survival
                < long_survival
            )
        )
    )

    print("\nNative T7 semantic validation")
    print("-" * 80)
    print(
        f"  median survival min: "
        f"{median_survival.min():.6f}"
    )
    print(
        f"  median survival max: "
        f"{median_survival.max():.6f}"
    )

    print(
        f"  short survival range: "
        f"{short_survival.min():.6f} → "
        f"{short_survival.max():.6f}"
    )

    print(
        f"  medium survival range: "
        f"{medium_survival.min():.6f} → "
        f"{medium_survival.max():.6f}"
    )

    print(
        f"  long survival range: "
        f"{long_survival.min():.6f} → "
        f"{long_survival.max():.6f}"
    )

    print(
        f"  prediction boundary values: "
        f"{sorted(set(boundaries))}"
    )

    print(
        f"  survival monotonicity violations: "
        f"{monotonic_violations}"
    )

    if monotonic_violations != 0:
        raise RuntimeError(
            "T7 survival probabilities violate "
            "expected non-increasing survival "
            "ordering across horizons."
        )

    # ------------------------------------------------------------------
    # 6. Build descriptive resolution context
    # ------------------------------------------------------------------

    context_states = []

    for (
        short_value,
        medium_value,
        long_value,
    ) in zip(
        short_survival,
        medium_survival,
        long_survival,
    ):

        context_states.append(
            classify_resolution_context(
                short_value,
                medium_value,
                long_value,
            )
        )

    context_counts = {}

    for state in context_states:
        context_counts[state] = (
            context_counts.get(state, 0)
            + 1
        )

    print("\nResolution context distribution")
    print("-" * 80)

    for state, count in sorted(
        context_counts.items()
    ):
        percentage = (
            count / len(context_states)
        )

        print(
            f"  {state:<32} "
            f"{count:>6} "
            f"({percentage:.4%})"
        )

    # ------------------------------------------------------------------
    # 7. Write structured T8 resolution evidence
    # ------------------------------------------------------------------

    with PREDICTIONS.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            [
                "id",
                "predicted_median_survival_seconds",
                "survival_probability_at_211583_seconds",
                "survival_probability_at_1780179_seconds",
                "survival_probability_at_14608619_seconds",
                "resolution_context",
                "prediction_boundary",
            ]
        )

        for i, ticket_id in enumerate(ids):

            writer.writerow(
                [
                    ticket_id,
                    float(
                        median_survival[i]
                    ),
                    float(
                        short_survival[i]
                    ),
                    float(
                        medium_survival[i]
                    ),
                    float(
                        long_survival[i]
                    ),
                    context_states[i],
                    boundaries[i],
                ]
            )

    # ------------------------------------------------------------------
    # 8. Save research artifact
    # ------------------------------------------------------------------

    report = {
        "operation": "MOD-036 OP-023",
        "operation_name": (
            "Resolution Decision Component Baseline"
        ),
        "status": "PASS",

        "source": {
            "native_t7_oof": str(
                SOURCE.relative_to(ROOT)
            ),
            "rows": len(rows),
            "unique_ids": len(unique_ids),
        },

        "native_semantics": {
            "task_type": (
                "time_to_first_post_creation_resolution"
            ),
            "prediction_boundary": "Creation",
            "survival_analysis_preserved": True,
            "censoring_relabeling": False,
        },

        "native_outputs": {
            "predicted_median_survival_seconds": (
                median_column
            ),
            "survival_probability_at_211583_seconds": (
                short_column
            ),
            "survival_probability_at_1780179_seconds": (
                medium_column
            ),
            "survival_probability_at_14608619_seconds": (
                long_column
            ),
        },

        "horizons_seconds": HORIZONS,

        "validation": {
            "duplicate_ids": duplicate_ids,
            "monotonicity_violations": (
                monotonic_violations
            ),
            "all_survival_probabilities_in_0_1": True,
            "all_predicted_survival_times_nonnegative": True,
            "all_prediction_boundaries_creation": True,
        },

        "resolution_context": {
            "states": sorted(
                context_counts.keys()
            ),
            "counts": context_counts,
            "thresholds_are_descriptive": True,
            "learned_binary_target": False,
            "automation_threshold_selected": False,
        },

        "controls": {
            "new_model_fitted": False,
            "synthetic_target_created": False,
            "binary_resolution_probability_created": False,
            "censored_cases_relabelled": False,
            "post_creation_features_used": False,
            "blind_probability_averaging": False,
            "arbitrary_cross_task_weights": False,
            "native_t7_output_preserved": True,
        },

        "outputs": {
            "predictions": str(
                PREDICTIONS.relative_to(ROOT)
            ),
        },
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