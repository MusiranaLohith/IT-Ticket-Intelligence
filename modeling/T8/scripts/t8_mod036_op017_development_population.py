from pathlib import Path
import csv
import json
import hashlib


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
OUT_DIR = ROOT / "modeling/T8/mod036"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_CSV = OUT_DIR / "t8_mod036_op017_development_population.csv"
OUTPUT_JSON = OUT_DIR / "t8_mod036_op017_development_population.json"

csv.field_size_limit(10_000_000)


# ---------------------------------------------------------------------
# Source artifacts
# ---------------------------------------------------------------------

T2 = ROOT / "modeling/T8/t8_mod029_t2_oof.csv"
T4 = ROOT / "modeling/T4/derived/t4_features.csv"
T5 = ROOT / "modeling/T5/splits/t5_model_val.csv"
T7 = ROOT / "modeling/T8/t8_mod029_t7_oof.csv"


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def read_csv(path):
    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline="",
    ) as f:
        return list(csv.DictReader(f))


def norm_id(value):
    if value is None:
        return ""
    return str(value).strip()


def find_id(row):
    """
    Resolve the canonical ticket identifier from common existing
    artifact naming without inventing identifiers.
    """
    for key in ("id", "ID", "ticket_id", "ticket", "bug_id"):
        if key in row and norm_id(row[key]):
            return norm_id(row[key])
    return ""


def build_index(rows, name):
    index = {}
    duplicates = 0
    missing = 0

    for row in rows:
        ticket_id = find_id(row)

        if not ticket_id:
            missing += 1
            continue

        if ticket_id in index:
            duplicates += 1

        index[ticket_id] = row

    return {
        "name": name,
        "index": index,
        "duplicates": duplicates,
        "missing_id_rows": missing,
    }


def pick(row, keys):
    for key in keys:
        if key in row:
            return row[key]
    return ""


def parse_float(value):
    if value in (None, ""):
        return None

    try:
        return float(value)
    except Exception:
        return None


def parse_int(value):
    if value in (None, ""):
        return None

    try:
        return int(value)
    except Exception:
        return None


def stable_hash(text):
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    print("=" * 80)
    print("T8 DECISION ENGINE — MOD-036 OP-017")
    print("Development Population Construction")
    print("=" * 80)

    sources = {
        "T2": T2,
        "T4": T4,
        "T5": T5,
        "T7": T7,
    }

    print("\nSource artifacts")
    print("-" * 80)

    source_status = {}

    for name, path in sources.items():
        exists = path.exists()

        source_status[name] = {
            "path": str(path.relative_to(ROOT)),
            "exists": exists,
        }

        print(
            f"  {name}: "
            f"{'FOUND' if exists else 'MISSING'} "
            f"{path.relative_to(ROOT)}"
        )

        if not exists:
            raise FileNotFoundError(path)

    # -------------------------------------------------------------
    # Load sources
    # -------------------------------------------------------------

    print("\nLoading source artifacts")
    print("-" * 80)

    t2_rows = read_csv(T2)
    t4_rows = read_csv(T4)
    t5_rows = read_csv(T5)
    t7_rows = read_csv(T7)

    print(f"  T2 rows: {len(t2_rows)}")
    print(f"  T4 rows: {len(t4_rows)}")
    print(f"  T5 rows: {len(t5_rows)}")
    print(f"  T7 rows: {len(t7_rows)}")

    # -------------------------------------------------------------
    # Build indexes
    # -------------------------------------------------------------

    t2_idx = build_index(t2_rows, "T2")
    t4_idx = build_index(t4_rows, "T4")
    t5_idx = build_index(t5_rows, "T5")
    t7_idx = build_index(t7_rows, "T7")

    print("\nSource ID integrity")
    print("-" * 80)

    for item in (t2_idx, t4_idx, t5_idx, t7_idx):
        print(
            f"  {item['name']}: "
            f"unique={len(item['index'])} "
            f"duplicates={item['duplicates']} "
            f"missing_id_rows={item['missing_id_rows']}"
        )

    # -------------------------------------------------------------
    # Development population policy
    # -------------------------------------------------------------
    #
    # T8 explicitly does NOT require the intersection of all tasks.
    #
    # We therefore use the union of ticket IDs represented in the
    # validated T2/T4/T5/T7 development evidence and preserve
    # availability per task.
    #
    # This prevents missing task evidence from becoming a negative.
    # -------------------------------------------------------------

    population_ids = set()

    for index in (
        t2_idx["index"],
        t4_idx["index"],
        t5_idx["index"],
        t7_idx["index"],
    ):
        population_ids.update(index.keys())

    population_ids = sorted(population_ids)

    print("\nDevelopment population")
    print("-" * 80)
    print(f"  union ticket population: {len(population_ids)}")

    # -------------------------------------------------------------
    # Build evidence rows
    # -------------------------------------------------------------

    output_rows = []

    availability_counts = {
        "T2": 0,
        "T4": 0,
        "T5": 0,
        "T7": 0,
    }

    for ticket_id in population_ids:
        t2 = t2_idx["index"].get(ticket_id)
        t4 = t4_idx["index"].get(ticket_id)
        t5 = t5_idx["index"].get(ticket_id)
        t7 = t7_idx["index"].get(ticket_id)

        if t2 is not None:
            availability_counts["T2"] += 1

        if t4 is not None:
            availability_counts["T4"] += 1

        if t5 is not None:
            availability_counts["T5"] += 1

        if t7 is not None:
            availability_counts["T7"] += 1

        # ---------------------------------------------------------
        # T2 native evidence
        # ---------------------------------------------------------

        t2_predicted_priority = (
            pick(t2, ["predicted_priority"])
            if t2 else ""
        )

        t2_probability_fields = [
            "predicted_probability_P1",
            "predicted_probability_P2",
            "predicted_probability_P3",
            "predicted_probability_P4",
            "predicted_probability_P5",
        ]

        # ---------------------------------------------------------
        # T4 native evidence
        # ---------------------------------------------------------

        t4_target_assignee = (
            pick(t4, ["target_assignee"])
            if t4 else ""
        )

        # Keep retrieval fields only when they actually exist.
        t4_retrieval_fields = {}
        if t4:
            for key, value in t4.items():
                low = key.lower()

                if (
                    "rank" in low
                    or "score" in low
                    or "candidate" in low
                ):
                    t4_retrieval_fields[key] = value

        # ---------------------------------------------------------
        # T5 native evidence
        # ---------------------------------------------------------

        t5_target = (
            pick(
                t5,
                [
                    "T5 target",
                    "t5_target",
                    "target_duplicate",
                    "duplicate_target",
                    "label",
                    "target",
                ],
            )
            if t5
            else ""
        )

        t5_probability = (
            pick(
                t5,
                [
                    "p_duplicate",
                    "duplicate_probability",
                    "predicted_probability",
                ],
            )
            if t5
            else ""
        )

        # ---------------------------------------------------------
        # T7 native survival evidence
        # ---------------------------------------------------------

        t7_median = (
            pick(
                t7,
                [
                    "predicted_median_survival_seconds",
                ],
            )
            if t7
            else ""
        )

        t7_event = (
            pick(
                t7,
                [
                    "event",
                ],
            )
            if t7
            else ""
        )

        t7_survival_fields = {}
        if t7:
            for key, value in t7.items():
                if "survival" in key.lower():
                    t7_survival_fields[key] = value

        # ---------------------------------------------------------
        # Creation time / provenance
        # ---------------------------------------------------------

        creation_time = ""

        for row in (t2, t7):
            if not row:
                continue

            candidate = pick(
                row,
                [
                    "creation_time",
                    "created_at",
                    "creation",
                ],
            )

            if candidate:
                creation_time = candidate
                break

        evidence_sources = []

        if t2:
            evidence_sources.append("T2")

        if t4:
            evidence_sources.append("T4")

        if t5:
            evidence_sources.append("T5")

        if t7:
            evidence_sources.append("T7")

        output_rows.append(
            {
                "ticket_id": ticket_id,
                "creation_time": creation_time,

                "T2_available": bool(t2),
                "T2_predicted_priority": t2_predicted_priority,

                "T4_available": bool(t4),
                "T4_target_assignee": t4_target_assignee,

                "T5_available": bool(t5),
                "T5_target": t5_target,
                "T5_duplicate_probability": t5_probability,

                "T7_available": bool(t7),
                "T7_predicted_median_survival_seconds": t7_median,
                "T7_event": t7_event,

                "T2_probability_P1": (
                    pick(t2, ["predicted_probability_P1"])
                    if t2 else ""
                ),
                "T2_probability_P2": (
                    pick(t2, ["predicted_probability_P2"])
                    if t2 else ""
                ),
                "T2_probability_P3": (
                    pick(t2, ["predicted_probability_P3"])
                    if t2 else ""
                ),
                "T2_probability_P4": (
                    pick(t2, ["predicted_probability_P4"])
                    if t2 else ""
                ),
                "T2_probability_P5": (
                    pick(t2, ["predicted_probability_P5"])
                    if t2 else ""
                ),

                "T4_retrieval_evidence_json": json.dumps(
                    t4_retrieval_fields,
                    ensure_ascii=False,
                    sort_keys=True,
                ),

                "T7_survival_evidence_json": json.dumps(
                    t7_survival_fields,
                    ensure_ascii=False,
                    sort_keys=True,
                ),

                "available_evidence_tasks": ",".join(
                    evidence_sources
                ),
            }
        )

    # -------------------------------------------------------------
    # Validate population construction
    # -------------------------------------------------------------

    missing_as_negative_violations = 0

    for row in output_rows:
        availability = {
            "T2": row["T2_available"],
            "T4": row["T4_available"],
            "T5": row["T5_available"],
            "T7": row["T7_available"],
        }

        # If a task is unavailable, its evidence fields must remain
        # empty rather than being filled with a negative/default value.
        for task, available in availability.items():
            if not available:
                if task == "T2":
                    fields = [
                        "T2_predicted_priority",
                        "T2_probability_P1",
                        "T2_probability_P2",
                        "T2_probability_P3",
                        "T2_probability_P4",
                        "T2_probability_P5",
                    ]

                elif task == "T4":
                    fields = ["T4_target_assignee"]

                elif task == "T5":
                    fields = [
                        "T5_target",
                        "T5_duplicate_probability",
                    ]

                else:
                    fields = [
                        "T7_predicted_median_survival_seconds",
                        "T7_event",
                    ]

                if any(row[field] not in ("", None) for field in fields):
                    missing_as_negative_violations += 1

    # -------------------------------------------------------------
    # Write development table
    # -------------------------------------------------------------

    fieldnames = list(output_rows[0].keys()) if output_rows else []

    with OUTPUT_CSV.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(output_rows)

    # -------------------------------------------------------------
    # Provenance manifest
    # -------------------------------------------------------------

    manifest = {
        "operation": "MOD-036 OP-017",
        "purpose": (
            "Construct a T8 development evidence population from "
            "validated T2/T4/T5/T7 artifacts while preserving per-task "
            "availability and Creation-boundary semantics."
        ),
        "prediction_boundary": "Creation",
        "decision_unit": "canonical Mozilla ticket",

        "population_policy": {
            "construction": "union_of_available_validated_task_evidence",
            "all_task_intersection_required": False,
            "missing_evidence": "unavailable",
            "missing_evidence_is_negative": False,
        },

        "sources": source_status,

        "source_row_counts": {
            "T2": len(t2_rows),
            "T4": len(t4_rows),
            "T5": len(t5_rows),
            "T7": len(t7_rows),
        },

        "source_unique_id_counts": {
            "T2": len(t2_idx["index"]),
            "T4": len(t4_idx["index"]),
            "T5": len(t5_idx["index"]),
            "T7": len(t7_idx["index"]),
        },

        "development_population": {
            "rows": len(output_rows),
            "sha256": stable_hash(
                "\n".join(
                    row["ticket_id"]
                    for row in output_rows
                )
            ),
        },

        "task_availability": availability_counts,

        "validation": {
            "missing_as_negative_violations": (
                missing_as_negative_violations
            ),
            "creation_time_source_restricted_to_existing_artifacts": True,
            "post_creation_features_added": False,
            "synthetic_target_created": False,
            "blind_all_task_intersection": False,
        },

        "included_native_targets": [
            "T2 target/evidence where present",
            "T4 target_assignee where present",
            "T5 native duplicate target/evidence where present",
            "T7 event/survival evidence where present",
        ],

        "explicit_exclusions": [
            "T1 frozen model output because no authoritative T1 model "
            "freeze exists",
            "T3 as a target",
            "T6 observable_non_positive as a negative label",
            "post-Creation information",
            "synthetic universal T8 target",
        ],

        "controls": {
            "training_performed": False,
            "prediction_generation_performed": False,
            "model_selected": False,
            "model_modified": False,
            "dataset_modified": False,
        },

        "artifacts": {
            "development_population_csv": str(
                OUTPUT_CSV.relative_to(ROOT)
            ),
            "manifest_json": str(
                OUTPUT_JSON.relative_to(ROOT)
            ),
        },
    }

    OUTPUT_JSON.write_text(
        json.dumps(
            manifest,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nDevelopment population")
    print("-" * 80)
    print(f"  rows: {len(output_rows)}")

    print("\nTask availability")
    print("-" * 80)
    for task, count in availability_counts.items():
        print(
            f"  {task}: {count} / {len(output_rows)}"
        )

    print("\nValidation")
    print("-" * 80)
    for key, value in manifest["validation"].items():
        print(f"  {key}: {value}")

    print("\nArtifacts")
    print("-" * 80)
    print(f"  CSV: {OUTPUT_CSV}")
    print(f"  JSON: {OUTPUT_JSON}")

    print("\nControls")
    print("-" * 80)
    for key, value in manifest["controls"].items():
        print(f"  {key}: {value}")

    print("\nStatus: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()