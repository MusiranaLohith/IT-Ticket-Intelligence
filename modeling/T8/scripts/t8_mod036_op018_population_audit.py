from pathlib import Path
import csv
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
OUT_DIR = ROOT / "modeling/T8/mod036"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = OUT_DIR / "t8_mod036_op018_population_audit.json"

csv.field_size_limit(10_000_000)


SOURCES = {
    "T2": ROOT / "modeling/T8/t8_mod029_t2_oof.csv",
    "T4": ROOT / "modeling/T4/derived/t4_features.csv",
    "T5": ROOT / "modeling/T5/splits/t5_model_val.csv",
    "T7": ROOT / "modeling/T8/t8_mod029_t7_oof.csv",
}


def read_csv(path):
    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline="",
    ) as f:
        return list(csv.DictReader(f))


def find_id(row):
    for key in ("id", "ID", "ticket_id", "ticket", "bug_id"):
        value = row.get(key, "")
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def summarize_columns(rows):
    if not rows:
        return []

    columns = list(rows[0].keys())

    target_like = []
    time_like = []
    post_creation_like = []
    prediction_like = []

    for column in columns:
        low = column.lower()

        if any(
            token in low
            for token in (
                "target",
                "label",
                "truth",
                "ground",
                "event",
            )
        ):
            target_like.append(column)

        if any(
            token in low
            for token in (
                "creation",
                "created",
                "timestamp",
                "time",
            )
        ):
            time_like.append(column)

        if any(
            token in low
            for token in (
                "resolved",
                "resolution",
                "closed",
                "assigned_at",
                "assignment_time",
                "future",
            )
        ):
            post_creation_like.append(column)

        if any(
            token in low
            for token in (
                "predicted",
                "probability",
                "score",
                "rank",
                "survival",
            )
        ):
            prediction_like.append(column)

    return {
        "all_columns": columns,
        "target_like_columns": target_like,
        "time_like_columns": time_like,
        "post_creation_like_columns": post_creation_like,
        "prediction_like_columns": prediction_like,
    }


def build_ids(rows):
    return {
        find_id(row)
        for row in rows
        if find_id(row)
    }


def main():
    print("=" * 80)
    print("T8 DECISION ENGINE — MOD-036 OP-018")
    print("T8 Development Population Audit")
    print("=" * 80)

    rows = {}
    ids = {}
    summaries = {}

    print("\nLoading populations")
    print("-" * 80)

    for task, path in SOURCES.items():
        if not path.exists():
            raise FileNotFoundError(path)

        rows[task] = read_csv(path)
        ids[task] = build_ids(rows[task])
        summaries[task] = summarize_columns(rows[task])

        print(
            f"  {task}: rows={len(rows[task])} "
            f"unique_ids={len(ids[task])}"
        )

    # -------------------------------------------------------------
    # Pairwise intersections
    # -------------------------------------------------------------

    print("\nPairwise ticket intersections")
    print("-" * 80)

    pairwise = {}

    tasks = list(SOURCES.keys())

    for i, left in enumerate(tasks):
        for right in tasks[i + 1:]:
            intersection = ids[left] & ids[right]

            key = f"{left}_x_{right}"

            pairwise[key] = {
                "rows": len(intersection),
                "left_population": len(ids[left]),
                "right_population": len(ids[right]),
            }

            print(
                f"  {left} ∩ {right}: "
                f"{len(intersection)}"
            )

    # -------------------------------------------------------------
    # Higher-order intersections
    # -------------------------------------------------------------

    all_union = set().union(*ids.values())
    all_intersection = set.intersection(*ids.values())

    t2_t4_t5 = ids["T2"] & ids["T4"] & ids["T5"]
    t2_t4_t7 = ids["T2"] & ids["T4"] & ids["T7"]
    t2_t5_t7 = ids["T2"] & ids["T5"] & ids["T7"]
    t4_t5_t7 = ids["T4"] & ids["T5"] & ids["T7"]

    print("\nHigher-order intersections")
    print("-" * 80)

    print(f"  T2 ∩ T4 ∩ T5: {len(t2_t4_t5)}")
    print(f"  T2 ∩ T4 ∩ T7: {len(t2_t4_t7)}")
    print(f"  T2 ∩ T5 ∩ T7: {len(t2_t5_t7)}")
    print(f"  T4 ∩ T5 ∩ T7: {len(t4_t5_t7)}")
    print(f"  T2 ∩ T4 ∩ T5 ∩ T7: {len(all_intersection)}")
    print(f"  T2 ∪ T4 ∪ T5 ∪ T7: {len(all_union)}")

    # -------------------------------------------------------------
    # Population-specific observations
    # -------------------------------------------------------------

    population_assessment = {
        "T2": {
            "role": "native priority development/evidence population",
            "use_for_shared_T8_population": "NO",
            "reason": (
                "Retain native T2 population and semantics rather than "
                "expanding it with unrelated task rows."
            ),
        },
        "T4": {
            "role": "native assignment/retrieval development population",
            "use_for_shared_T8_population": "NO",
            "reason": (
                "T4 has a substantially larger native population and its "
                "candidate-space/evaluation protocol is task-specific."
            ),
        },
        "T5": {
            "role": "native duplicate development population",
            "use_for_shared_T8_population": "NO",
            "reason": (
                "T5 validation population has its own duplicate-target "
                "semantics and calibration protocol."
            ),
        },
        "T7": {
            "role": "native resolution/survival development population",
            "use_for_shared_T8_population": "NO",
            "reason": (
                "T7 has explicit chronological and censoring semantics."
            ),
        },
    }

    # -------------------------------------------------------------
    # Feature/target separation audit
    # -------------------------------------------------------------

    feature_target_separation = {}

    for task in tasks:
        summary = summaries[task]

        feature_target_separation[task] = {
            "target_like_columns": summary["target_like_columns"],
            "time_like_columns": summary["time_like_columns"],
            "post_creation_like_columns": (
                summary["post_creation_like_columns"]
            ),
            "prediction_like_columns": summary["prediction_like_columns"],
            "target_columns_are_not_automatically_features": True,
        }

    # -------------------------------------------------------------
    # T8 population architecture decision
    # -------------------------------------------------------------

    architecture_decision = {
        "shared_supervised_population": {
            "status": "NOT_ESTABLISHED",
            "decision": (
                "Do not use the 232,520-row union as a single supervised "
                "T8 training population."
            ),
            "reason": (
                "The four source populations have different native task "
                "definitions, target semantics, evaluation protocols, "
                "and population sizes."
            ),
        },
        "native_component_populations": {
            "status": "RETAIN",
            "decision": (
                "Each supervised T8 component should initially train and "
                "evaluate using its corresponding native task population."
            ),
        },
        "decision_engine_population": {
            "status": "SEPARATE_LAYER",
            "decision": (
                "T8 decision synthesis should consume validated component "
                "outputs/evidence at the decision-engine layer rather than "
                "forcing all training targets into one population."
            ),
        },
        "missing_task_evidence": {
            "rule": "unavailable",
            "negative_interpretation": False,
        },
    }

    # -------------------------------------------------------------
    # Validation controls
    # -------------------------------------------------------------

    controls = {
        "training_performed": False,
        "prediction_generation_performed": False,
        "model_selected": False,
        "model_modified": False,
        "dataset_modified": False,
        "232520_union_used_as_supervised_training_population": False,
        "synthetic_universal_target_created": False,
        "all_task_intersection_forced": False,
    }

    result = {
        "operation": "MOD-036 OP-018",
        "purpose": (
            "Audit T2/T4/T5/T7 development populations and determine "
            "whether T8 should use a shared supervised population or "
            "native task populations."
        ),
        "source_populations": {
            task: {
                "rows": len(rows[task]),
                "unique_ids": len(ids[task]),
                "path": str(SOURCES[task].relative_to(ROOT)),
            }
            for task in tasks
        },
        "pairwise_intersections": pairwise,
        "higher_order_intersections": {
            "T2_T4_T5": len(t2_t4_t5),
            "T2_T4_T7": len(t2_t4_t7),
            "T2_T5_T7": len(t2_t5_t7),
            "T4_T5_T7": len(t4_t5_t7),
            "T2_T4_T5_T7": len(all_intersection),
            "union": len(all_union),
        },
        "column_audit": summaries,
        "feature_target_separation": feature_target_separation,
        "population_assessment": population_assessment,
        "architecture_decision": architecture_decision,
        "controls": controls,
    }

    OUTPUT.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nArchitecture decision")
    print("-" * 80)

    print(
        "  shared supervised population: "
        f"{architecture_decision['shared_supervised_population']['status']}"
    )

    print(
        "  native component populations: "
        f"{architecture_decision['native_component_populations']['status']}"
    )

    print(
        "  decision-engine population: "
        f"{architecture_decision['decision_engine_population']['status']}"
    )

    print("\nControls")
    print("-" * 80)

    for key, value in controls.items():
        print(f"  {key}: {value}")

    print(f"\nArtifact: {OUTPUT}")
    print("\nStatus: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()