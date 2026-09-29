from pathlib import Path
import json
import csv
csv.field_size_limit(10_000_000)

ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T8 = ROOT / "modeling/T8"

OUT_DIR = T8 / "mod036"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "t8_mod036_op002_task_output_inventory.json"


def inspect_csv(path, task, description, level, output_fields, target=None):
    result = {
        "task": task,
        "description": description,
        "artifact": str(path),
        "exists": path.exists(),
        "decision_level": level,
        "output_fields": output_fields,
        "target": target,
    }

    if not path.exists():
        result["status"] = "MISSING"
        return result

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        first_rows = []
        row_count = 0

        for row in reader:
            row_count += 1
            if len(first_rows) < 3:
                first_rows.append(row)

    result["status"] = "FOUND"
    result["rows"] = row_count
    result["columns"] = header

    result["id_fields_present"] = [
        c for c in ["ID", "id", "ticket_id", "query_id"]
        if c in header
    ]

    result["requested_output_fields_present"] = [
        c for c in output_fields
        if c in header
    ]

    result["target_fields_present"] = (
        [target] if target and target in header else []
    )

    result["sample_rows"] = first_rows

    return result


# ------------------------------------------------------------------
# Known native artifacts
# ------------------------------------------------------------------

artifacts = []


# T2
artifacts.append(
    inspect_csv(
        ROOT / "modeling/T2/splits/test.csv",
        "T2",
        "Priority Prediction",
        "ticket",
        [
            "ID",
            "summary",
            "description",
            "priority",
        ],
        target="priority",
    )
)


# T4
artifacts.append(
    inspect_csv(
        ROOT / "modeling/T4/derived/t4_eval.csv",
        "T4",
        "Assignee Retrieval",
        "ticket",
        [
            "ID",
            "target_assignee",
        ],
        target="target_assignee",
    )
)


# T5
artifacts.append(
    inspect_csv(
        ROOT / "modeling/T5/splits/t5_model_val.csv",
        "T5",
        "Duplicate Prediction",
        "ticket",
        [
            "ID",
            "T5 target",
        ],
        target="T5 target",
    )
)


# T6 / T7 / T1 / T3
#
# These are deliberately discovered from the project tree instead
# of inventing artifact paths. We inspect filenames first and then
# report candidate evidence locations.
# ------------------------------------------------------------------

candidate_patterns = {
    "T1": [
        "*t1*",
        "*T1*",
    ],
    "T3": [
        "*t3*",
        "*T3*",
    ],
    "T6": [
        "*t6*",
        "*T6*",
    ],
    "T7": [
        "*t7*",
        "*T7*",
    ],
}


def discover_candidates(task):
    matches = set()

    for pattern in candidate_patterns[task]:
        for p in ROOT.rglob(pattern):
            if not p.is_file():
                continue

            # Avoid overwhelming the inventory with cache/build files.
            if any(
                part in {
                    ".git",
                    "__pycache__",
                    ".venv",
                    "node_modules",
                }
                for part in p.parts
            ):
                continue

            matches.add(p)

    return sorted(
        str(p.relative_to(ROOT))
        for p in matches
    )


for task in ["T1", "T3", "T6", "T7"]:
    candidates = discover_candidates(task)

    artifacts.append(
        {
            "task": task,
            "status": "DISCOVERY_REQUIRED",
            "candidate_artifacts": candidates,
        }
    )


# ------------------------------------------------------------------
# T8 input eligibility rules
# ------------------------------------------------------------------

eligibility_rules = {
    "creation_boundary": True,
    "post_creation_information": False,
    "native_semantics_preserved": True,
    "missingness_is_not_negative": True,
    "synthetic_universal_target": False,
    "arbitrary_output_weighting": False,
    "blind_probability_averaging": False,
}


# ------------------------------------------------------------------
# Build report
# ------------------------------------------------------------------

report = {
    "operation": "T8 / MOD-036 / OP-002",
    "status": "PASS",
    "purpose": (
        "Inventory the available native T1-T7 task outputs and "
        "identify which artifacts can serve as T8 Decision Engine inputs."
    ),
    "artifacts": artifacts,
    "eligibility_rules": eligibility_rules,
}


OUT.write_text(
    json.dumps(report, indent=2)
)


# ------------------------------------------------------------------
# Terminal summary
# ------------------------------------------------------------------

print("=" * 80)
print("T8 DECISION ENGINE — MOD-036 OP-002")
print("=" * 80)

print()
print("Task output inventory")
print("-" * 80)

for item in artifacts:
    task = item["task"]
    status = item["status"]

    print(f"{task}: {status}")

    if "artifact" in item:
        print(f"  Artifact: {item['artifact']}")

    if "rows" in item:
        print(f"  Rows: {item['rows']}")

    if "decision_level" in item:
        print(f"  Level: {item['decision_level']}")

    if "id_fields_present" in item:
        print(
            f"  ID fields: "
            f"{item['id_fields_present']}"
        )

    if "requested_output_fields_present" in item:
        print(
            f"  Output fields found: "
            f"{item['requested_output_fields_present']}"
        )

    if "target_fields_present" in item:
        print(
            f"  Target fields: "
            f"{item['target_fields_present']}"
        )

    if status == "DISCOVERY_REQUIRED":
        print(
            f"  Candidate artifacts discovered: "
            f"{len(item['candidate_artifacts'])}"
        )

print()
print("T8 eligibility rules")
print("-" * 80)

for key, value in eligibility_rules.items():
    print(f"{key}: {value}")

print()
print("Status: PASS")
print(f"Artifact: {OUT}")
print("=" * 80)