#!/usr/bin/env python3

import json
from pathlib import Path


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T8_VALIDATION = (
    ROOT
    / "modeling"
    / "T8"
    / "mod036"
    / "op026"
    / "t8_mod036_op026_decision_engine_validation.json"
)

CONTRACTS = {
    "T2": ROOT / "modeling" / "T2" / "contracts",
    "T3": ROOT / "modeling" / "T3" / "contracts",
    "T4": ROOT / "modeling" / "T4" / "contracts",
    "T5": ROOT / "modeling" / "T5" / "contracts",
    "T6": ROOT / "modeling" / "T6" / "contracts",
    "T7": ROOT / "modeling" / "T7" / "contracts",
}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def print_tree(obj, prefix="", max_depth=3, depth=0):
    if depth > max_depth:
        return

    if isinstance(obj, dict):
        for key, value in obj.items():
            print(f"{prefix}{key}: {type(value).__name__}")

            if depth < max_depth:
                if isinstance(value, dict):
                    print_tree(
                        value,
                        prefix + "  ",
                        max_depth=max_depth,
                        depth=depth + 1,
                    )
                elif isinstance(value, list) and value:
                    print(f"{prefix}  [list_length={len(value)}]")
                    print_tree(
                        value[0],
                        prefix + "    ",
                        max_depth=max_depth,
                        depth=depth + 1,
                    )

    elif isinstance(obj, list):
        print(f"{prefix}[list_length={len(obj)}]")


print("=" * 72)
print("FMP-03 OP-001 — T8 NATIVE INTERFACE INSPECTION")
print("=" * 72)

# ------------------------------------------------------------------
# 1. T8 validation artifact
# ------------------------------------------------------------------

print("\n[1] T8 validation artifact")
print("-" * 72)

if not T8_VALIDATION.exists():
    print(f"STATUS: BLOCKED")
    print(f"Missing: {T8_VALIDATION}")
    raise SystemExit(1)

t8 = load_json(T8_VALIDATION)

print(f"Path: {T8_VALIDATION}")
print(f"Top-level type: {type(t8).__name__}")

if isinstance(t8, dict):
    print(f"Top-level keys: {list(t8.keys())}")

    print("\nT8 structure:")
    print_tree(t8, max_depth=3)

# ------------------------------------------------------------------
# 2. Existing task contracts
# ------------------------------------------------------------------

print("\n[2] Existing T2–T7 contracts")
print("-" * 72)

contract_count = 0

for task, directory in CONTRACTS.items():

    print(f"\n[{task}]")
    print(f"Directory: {directory}")

    if not directory.exists():
        print("STATUS: DIRECTORY_MISSING")
        continue

    json_files = sorted(directory.glob("*.json"))

    if not json_files:
        print("STATUS: NO_JSON_CONTRACT_FOUND")
        continue

    for path in json_files:
        try:
            data = load_json(path)

            print(f"\nFile: {path.name}")
            print(f"Top-level type: {type(data).__name__}")

            if isinstance(data, dict):
                print(f"Top-level keys: {list(data.keys())}")

                # Print only the first two structural levels here.
                print("Structure:")
                print_tree(data, max_depth=2)

            contract_count += 1

        except Exception as exc:
            print(f"ERROR reading {path.name}: {exc}")

# ------------------------------------------------------------------
# 3. Read-only integrity conclusion
# ------------------------------------------------------------------

print("\n[3] Inspection summary")
print("-" * 72)

print(f"T8 validation artifact readable: {T8_VALIDATION.exists()}")
print(f"T2–T7 contract JSON files discovered: {contract_count}")

print("\nNo predictions generated.")
print("No models loaded.")
print("No retraining performed.")
print("No evaluation performed.")
print("No artifacts modified.")

print("\nSTATUS: PASS")
print("Operation type: READ_ONLY_INTERFACE_INSPECTION")