from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T8_VALIDATION = (
    ROOT
    / "modeling"
    / "T8"
    / "mod036"
    / "op026"
    / "t8_mod036_op026_decision_engine_validation.json"
)

CONTRACT_ROOTS = [
    ROOT / "modeling" / "T2" / "contracts",
    ROOT / "modeling" / "T3" / "contracts",
    ROOT / "modeling" / "T4" / "contracts",
    ROOT / "modeling" / "T5" / "contracts",
    ROOT / "modeling" / "T6" / "contracts",
    ROOT / "modeling" / "T7" / "contracts",
]


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def flatten_keys(obj: Any, prefix: str = "") -> list[str]:
    keys = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            current = f"{prefix}.{key}" if prefix else str(key)
            keys.append(current)
            keys.extend(flatten_keys(value, current))

    elif isinstance(obj, list):
        for i, value in enumerate(obj[:10]):
            current = f"{prefix}[{i}]"
            keys.extend(flatten_keys(value, current))

    return keys


def discover_contracts() -> list[Path]:
    paths = []

    for root in CONTRACT_ROOTS:
        if root.exists():
            paths.extend(sorted(root.glob("*.json")))

    return sorted(set(paths))


def classify_task(path: Path) -> str:
    name = path.name.upper()
    parent = str(path.parent).upper()

    for task in ["T2", "T3", "T4", "T5", "T6", "T7"]:
        if f"/{task}/" in parent.replace("\\", "/") or name.startswith(task):
            return task

    return "UNKNOWN"


def inspect_contract(path: Path) -> dict[str, Any]:
    data = read_json(path)
    keys = flatten_keys(data)

    return {
        "file": str(path),
        "task": classify_task(path),
        "top_level_type": type(data).__name__,
        "top_level_keys": list(data.keys()) if isinstance(data, dict) else [],
        "key_count": len(keys),
        "selected_semantic_keys": [
            k
            for k in keys
            if any(
                token in k.lower()
                for token in [
                    "target",
                    "feature",
                    "input",
                    "output",
                    "prediction",
                    "probability",
                    "score",
                    "rank",
                    "retriev",
                    "surviv",
                    "censor",
                    "time",
                    "grain",
                    "provenance",
                    "missing",
                    "semantic",
                    "evidence",
                ]
            )
        ],
    }


def main() -> None:
    print("=" * 80)
    print("FMP-03 OP-002 — NATIVE EVIDENCE INTERFACE EXTRACTION")
    print("=" * 80)

    print("\n[1] Checking T8 validation artifact")
    print("-" * 80)

    if not T8_VALIDATION.exists():
        print(f"T8 validation artifact exists: False")
        print("\nSTATUS: BLOCKED")
        return

    t8_data = read_json(T8_VALIDATION)

    print(f"T8 validation artifact: {T8_VALIDATION}")
    print(f"Readable JSON: True")
    print(f"Top-level type: {type(t8_data).__name__}")

    if isinstance(t8_data, dict):
        print(f"Top-level keys: {list(t8_data.keys())}")

    print("\n[2] Discovering T2–T7 contracts")
    print("-" * 80)

    contracts = discover_contracts()

    print(f"Contracts discovered: {len(contracts)}")

    if not contracts:
        print("\nSTATUS: BLOCKED")
        return

    task_counts: dict[str, int] = {}

    for path in contracts:
        task = classify_task(path)
        task_counts[task] = task_counts.get(task, 0) + 1

    for task in ["T2", "T3", "T4", "T5", "T6", "T7"]:
        print(f"{task}: {task_counts.get(task, 0)}")

    print("\n[3] Extracting native semantic interfaces")
    print("-" * 80)

    records = []

    for path in contracts:
        try:
            record = inspect_contract(path)
            records.append(record)
        except Exception as exc:
            print(f"ERROR reading {path}: {exc}")

    for task in ["T2", "T3", "T4", "T5", "T6", "T7"]:
        task_records = [r for r in records if r["task"] == task]

        print(f"\n--- {task} ---")

        for record in task_records:
            print(f"Contract: {Path(record['file']).name}")
            print(f"Top-level type: {record['top_level_type']}")
            print(f"Top-level keys: {record['top_level_keys']}")

            semantic_keys = record["selected_semantic_keys"]

            if semantic_keys:
                print("Relevant semantic/interface keys:")
                for key in semantic_keys[:40]:
                    print(f"  - {key}")
            else:
                print("Relevant semantic/interface keys: NONE DETECTED")

    print("\n[4] T8 validation controls")
    print("-" * 80)

    if isinstance(t8_data, dict):
        controls = t8_data.get("controls")

        if isinstance(controls, dict):
            for key, value in controls.items():
                print(f"{key}: {value}")
        else:
            print("controls object: not present at expected top level")

    print("\n[5] Operation safeguards")
    print("-" * 80)

    print("Predictions generated: False")
    print("Models loaded: False")
    print("Retraining performed: False")
    print("Evaluation performed: False")
    print("Artifacts modified: False")
    print("Universal score created: False")
    print("Native task semantics altered: False")

    print("\n[6] Extraction summary")
    print("-" * 80)

    task_presence = {
        task: any(r["task"] == task for r in records)
        for task in ["T2", "T3", "T4", "T5", "T6", "T7"]
    }

    print(f"Task contract presence: {task_presence}")
    print(f"Total contract files inspected: {len(records)}")

    all_tasks_present = all(task_presence.values())

    print(f"All T2–T7 represented: {all_tasks_present}")

    if all_tasks_present:
        print("\nSTATUS: PASS")
        print("Operation type: READ_ONLY_NATIVE_EVIDENCE_INTERFACE_EXTRACTION")
    else:
        print("\nSTATUS: BLOCKED")
        print("Reason: One or more T2–T7 task contract groups were not discovered.")


if __name__ == "__main__":
    main()