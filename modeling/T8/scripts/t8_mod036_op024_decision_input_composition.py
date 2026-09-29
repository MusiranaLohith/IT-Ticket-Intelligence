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

OUT_DIR = ROOT / "modeling/T8/mod036/op024"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REPORT = (
    OUT_DIR
    / "t8_mod036_op024_decision_input_composition.json"
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


def resolve_id(columns):
    normalized = {
        normalize(column): column
        for column in columns
    }

    for candidate in (
        "id",
        "ticket_id",
        "bug_id",
    ):
        if candidate in normalized:
            return normalized[candidate]

    raise RuntimeError(
        "Could not resolve ID column. "
        f"Available columns: {columns}"
    )


def main():

    print("=" * 80)
    print("T8 DECISION ENGINE — MOD-036 OP-024")
    print("Decision Engine Input Composition")
    print("=" * 80)

    inventories = {}
    populations = {}
    id_sets = {}

    # ------------------------------------------------------------------
    # 1. Inspect all established T8 component outputs
    # ------------------------------------------------------------------

    for component, path in SOURCES.items():

        print(f"\n{component.upper()} component")
        print("-" * 80)
        print(f"  path: {path}")

        columns, rows = read_csv(path)

        id_column = resolve_id(columns)

        ids = [
            str(row[id_column]).strip()
            for row in rows
        ]

        unique_ids = set(ids)
        duplicate_count = (
            len(ids)
            - len(unique_ids)
        )

        if duplicate_count != 0:
            raise RuntimeError(
                f"{component}: duplicate IDs detected: "
                f"{duplicate_count}"
            )

        inventories[component] = {
            "path": str(path.relative_to(ROOT)),
            "rows": len(rows),
            "columns": columns,
            "id_column": id_column,
        }

        populations[component] = len(rows)
        id_sets[component] = unique_ids

        print(f"  rows: {len(rows)}")
        print(f"  columns: {len(columns)}")
        print(f"  ID column: {id_column}")
        print(f"  unique IDs: {len(unique_ids)}")
        print(f"  duplicate IDs: {duplicate_count}")

        print("  fields:")
        for column in columns:
            print(f"    - {column}")

    # ------------------------------------------------------------------
    # 2. Pairwise population intersections
    # ------------------------------------------------------------------

    components = list(SOURCES.keys())

    pairwise = {}

    print("\nPairwise population intersections")
    print("-" * 80)

    for i, left in enumerate(components):
        for right in components[i + 1:]:

            intersection = (
                id_sets[left]
                & id_sets[right]
            )

            key = f"{left}__{right}"

            pairwise[key] = len(
                intersection
            )

            print(
                f"  {left:<12} ∩ "
                f"{right:<12}: "
                f"{len(intersection)}"
            )

    # ------------------------------------------------------------------
    # 3. Higher-order intersections
    # ------------------------------------------------------------------

    all_four = set.intersection(
        *(id_sets[name] for name in components)
    )

    union = set.union(
        *(id_sets[name] for name in components)
    )

    print("\nHigher-order population structure")
    print("-" * 80)
    print(
        f"  all four components: "
        f"{len(all_four)}"
    )
    print(
        f"  union population:    "
        f"{len(union)}"
    )

    # ------------------------------------------------------------------
    # 4. Per-ticket evidence availability over union
    # ------------------------------------------------------------------

    availability_counts = {}

    for ticket_id in union:

        available = tuple(
            component
            for component in components
            if ticket_id in id_sets[component]
        )

        key = (
            "+".join(available)
            if available
            else "NONE"
        )

        availability_counts[key] = (
            availability_counts.get(key, 0)
            + 1
        )

    print("\nEvidence availability across union")
    print("-" * 80)

    for pattern, count in sorted(
        availability_counts.items(),
        key=lambda item: (-item[1], item[0]),
    ):
        print(
            f"  {pattern:<45} "
            f"{count:>8}"
        )

    # ------------------------------------------------------------------
    # 5. Architecture decision
    # ------------------------------------------------------------------

    architecture = {
        "decision_engine_population": "UNION_OF_AVAILABLE_TASK_EVIDENCE",
        "forced_common_supervised_population": False,
        "four_way_intersection_required": False,
        "missing_component_means_unavailable": True,
        "component_outputs_retain_native_semantics": True,
        "blind_probability_averaging": False,
        "arbitrary_cross_task_weights": False,
        "synthetic_universal_target": False,
    }

    # ------------------------------------------------------------------
    # 6. Save report
    # ------------------------------------------------------------------

    report = {
        "operation": "MOD-036 OP-024",
        "operation_name": (
            "Decision Engine Input Composition"
        ),
        "status": "PASS",

        "component_inventory": inventories,

        "population_sizes": populations,

        "pairwise_intersections": pairwise,

        "higher_order_population": {
            "all_four_components": len(all_four),
            "union": len(union),
        },

        "evidence_availability": availability_counts,

        "architecture": architecture,

        "controls": {
            "no_model_fitted": True,
            "no_target_created": True,
            "no_probability_combination": True,
            "no_task_relabeling": True,
            "no_post_creation_feature_injection": True,
        },

        "next_operation": (
            "MOD-036 OP-025 — "
            "Decision Engine Composition Baseline"
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

    print("\nArtifact")
    print("-" * 80)
    print(f"  report: {REPORT}")

    print("\nStatus: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()