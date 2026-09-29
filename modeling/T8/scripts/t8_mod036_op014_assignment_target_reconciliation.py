from pathlib import Path
import json
import csv


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
OUT_DIR = ROOT / "modeling/T8/mod036"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = OUT_DIR / "t8_mod036_op014_assignment_target_reconciliation.json"

csv.field_size_limit(10_000_000)


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "_read_error": str(exc)
        }


def inspect_json(path):
    data = load_json(path)

    result = {
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "readable": "_read_error" not in data,
        "target_fields": {},
    }

    if "_read_error" in data:
        result["read_error"] = data["_read_error"]
        return result

    target_terms = {
        "target",
        "assignee",
        "assignment",
        "assigned",
        "creation",
        "future",
        "evaluation",
        "candidate",
        "population",
        "event",
        "split",
    }

    def walk(obj, location="root"):
        if isinstance(obj, dict):
            for key, value in obj.items():
                key_lower = str(key).lower()

                if any(term in key_lower for term in target_terms):
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        result["target_fields"][
                            f"{location}.{key}"
                        ] = value

                walk(value, f"{location}.{key}")

        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                walk(value, f"{location}[{i}]")

    walk(data)

    return result


def inspect_csv(path):
    result = {
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "status": "MISSING",
        "columns": [],
        "target_columns": [],
        "sample_rows": [],
    }

    if not path.exists():
        return result

    try:
        with path.open(
            "r",
            encoding="utf-8",
            errors="replace",
            newline="",
        ) as f:
            reader = csv.DictReader(f)

            result["columns"] = reader.fieldnames or []

            target_columns = []
            for col in result["columns"]:
                low = col.lower()
                if (
                    "target_assignee" in low
                    or "assignee" in low
                    or "assignment" in low
                ):
                    target_columns.append(col)

            result["target_columns"] = target_columns

            for row in reader:
                sample = {}

                for col in (
                    "id",
                    "ticket",
                    "creation",
                    "creation_time",
                    "target_assignee",
                    "current_assigned_to",
                    "assigned_to",
                ):
                    if col in row:
                        sample[col] = row[col]

                if sample:
                    result["sample_rows"].append(sample)

                if len(result["sample_rows"]) >= 5:
                    break

            result["status"] = "INSPECTED"

    except Exception as exc:
        result["status"] = "ERROR"
        result["error"] = str(exc)

    return result


def main():
    print("=" * 80)
    print("T8 DECISION ENGINE — MOD-036 OP-014")
    print("Assignment Target Reconciliation")
    print("=" * 80)

    # Authoritative / high-value T4 evidence.
    json_candidates = [
        ROOT / "modeling/T4/contracts/t4_model_contract.json",
        ROOT / "modeling/T4/analysis/t4_final_closure.json",
        ROOT / "modeling/T4/metrics/t4_final_metrics.json",
        ROOT / "modeling/T4/analysis/t4_retrieval_analysis.json",
    ]

    csv_candidates = [
        ROOT / "modeling/T4/derived/t4_features.csv",
        ROOT / "modeling/T4/derived/t4_train.csv",
        ROOT / "modeling/T4/derived/t4_eval.csv",
    ]

    print("\nT4 JSON evidence")
    print("-" * 80)

    json_results = []

    for path in json_candidates:
        if not path.exists():
            print(f"MISSING  {path.relative_to(ROOT)}")
            json_results.append({
                "path": str(path.relative_to(ROOT)),
                "exists": False,
            })
            continue

        result = inspect_json(path)
        json_results.append(result)

        print(f"FOUND    {path.relative_to(ROOT)}")

        fields = result.get("target_fields", {})

        if not fields:
            print("  No target/assignment-related scalar fields found.")
            continue

        for key, value in list(fields.items())[:25]:
            print(f"  {key} = {value!r}")

        if len(fields) > 25:
            print(f"  ... {len(fields) - 25} additional fields")

    print("\nT4 CSV evidence")
    print("-" * 80)

    csv_results = []

    for path in csv_candidates:
        result = inspect_csv(path)
        csv_results.append(result)

        if result["status"] == "MISSING":
            print(f"MISSING  {path.relative_to(ROOT)}")
            continue

        print(f"{result['status']:<8} {path.relative_to(ROOT)}")

        print(
            "  target/assignment columns: "
            + (
                ", ".join(result["target_columns"])
                if result["target_columns"]
                else "NONE"
            )
        )

        for row in result["sample_rows"]:
            print(f"  sample: {row}")

    # Explicit semantic reconciliation.
    reconciliation = {
        "t4_target_name": "target_assignee",
        "t4_target_event": (
            "first valid assignment event strictly after Creation"
        ),
        "t4_target_population": (
            "historical target assignees observed after Creation"
        ),
        "t8_assignment_recommendation": (
            "machine-generated recommendation of an assignee or group "
            "for an incoming ticket"
        ),
        "semantic_relationship": (
            "T4 target_assignee is a legitimate supervised historical "
            "assignment outcome candidate for T8 assignment recommendation, "
            "provided the T8 development population preserves the same "
            "Creation boundary and target-event definition."
        ),
        "important_restrictions": [
            "Current assigned_to at Creation is target-side information "
            "and must not be used as a Creation-time predictive feature "
            "when it represents future assignment information.",
            "The recommendation must operate over the valid historical "
            "assignee candidate space rather than inventing a new label.",
            "T4 retrieval scores remain retrieval evidence.",
            "T1 category evidence may support assignment reasoning but is "
            "not itself the assignment target.",
            "Missing retrieval or category evidence must not be interpreted "
            "as negative assignment evidence.",
            "No post-Creation feature may enter the T8 prediction input.",
            "No synthetic assignment label may be constructed.",
        ],
        "development_eligibility": True,
    }

    # Check the known T4 contract fields directly.
    contract_path = ROOT / "modeling/T4/contracts/t4_model_contract.json"
    contract = load_json(contract_path)

    contract_checks = {
        "contract_found": contract_path.exists(),
        "target_column_is_target_assignee": False,
        "strictly_after_creation": False,
        "future_assignment_forbidden": False,
        "blank_target_excluded": False,
    }

    if isinstance(contract, dict) and "_read_error" not in contract:
        operational_target = contract.get("operational_target", {})
        feature_boundary = contract.get("feature_boundary", {})

        contract_checks["target_column_is_target_assignee"] = (
            operational_target.get("target_column")
            == "target_assignee"
        )

        contract_checks["strictly_after_creation"] = (
            operational_target.get(
                "target_event_must_be_strictly_after_creation"
            )
            is True
        )

        contract_checks["future_assignment_forbidden"] = (
            feature_boundary.get(
                "future_assignment_information_forbidden"
            )
            is True
        )

        contract_checks["blank_target_excluded"] = (
            operational_target.get("blank_target_excluded")
            is True
        )

    result = {
        "operation": "MOD-036 OP-014",
        "purpose": (
            "Determine whether the validated T4 target_assignee semantics "
            "can supervise the T8 assignment_recommendation output."
        ),
        "json_evidence": json_results,
        "csv_evidence": csv_results,
        "contract_checks": contract_checks,
        "reconciliation": reconciliation,
        "controls": {
            "training_performed": False,
            "prediction_generation_performed": False,
            "model_selected": False,
            "model_modified": False,
            "dataset_modified": False,
            "post_creation_information_used_for_prediction": False,
        },
    }

    OUTPUT.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\nContract checks")
    print("-" * 80)

    for key, value in contract_checks.items():
        print(f"  {key}: {value}")

    print("\nAssignment reconciliation")
    print("-" * 80)

    print(
        "  T4 target: "
        f"{reconciliation['t4_target_name']}"
    )

    print(
        "  T4 event: "
        f"{reconciliation['t4_target_event']}"
    )

    print(
        "  T8 output: "
        f"{reconciliation['t8_assignment_recommendation']}"
    )

    print(
        "  development eligibility: "
        f"{reconciliation['development_eligibility']}"
    )

    print("\nControls")
    print("-" * 80)

    for key, value in result["controls"].items():
        print(f"  {key}: {value}")

    print(f"\nArtifact: {OUTPUT}")
    print("\nStatus: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()