from __future__ import annotations

import json
from pathlib import Path


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T10_ROOT = ROOT / "modeling" / "T10"
FMP_ROOT = ROOT / "modeling" / "FMP"


TARGET_EXTENSIONS = {
    ".json",
    ".csv",
    ".md",
    ".txt",
}

TARGET_TERMS = (
    "t10",
    "policy",
    "automation",
    "review",
    "defer",
    "closure",
)


def safe_json_read(path: Path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        return {"__read_error__": str(exc)}


def targeted_files(root: Path):
    if not root.exists():
        return []

    results = []

    for path in root.iterdir():
        if path.is_file() and path.suffix.lower() in TARGET_EXTENSIONS:
            name = path.name.lower()

            if any(term in name for term in TARGET_TERMS):
                results.append(path)

        elif path.is_dir():
            # Only inspect one additional directory level.
            for child in path.iterdir():
                if not child.is_file():
                    continue

                if child.suffix.lower() not in TARGET_EXTENSIONS:
                    continue

                name = child.name.lower()

                if any(term in name for term in TARGET_TERMS):
                    results.append(child)

    return sorted(results)


def print_json_summary(path: Path, data):
    if not isinstance(data, dict):
        print(f"  JSON type: {type(data).__name__}")
        return

    preferred_fields = [
        "operation",
        "title",
        "status",
        "closure_status",
        "purpose",
        "role",
        "state",
        "result",
        "policy_status",
        "automation_status",
        "human_review_status",
        "defer_status",
        "threshold_status",
        "validation_status",
        "universal_threshold",
        "universal_confidence",
        "universal_risk",
    ]

    printed = set()

    for field in preferred_fields:
        if field in data:
            print(f"  {field}: {data[field]}")
            printed.add(field)

    nested_keys = [
        "contract",
        "policy",
        "controls",
        "validation",
        "closure",
        "limitations",
        "methodological_restrictions",
    ]

    for key in nested_keys:
        value = data.get(key)

        if value is not None:
            print(f"  [{key}]")

            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    print(f"    {subkey}: {subvalue}")
            else:
                print(f"    {value}")

            printed.add(key)

    remaining = [
        key for key in data.keys()
        if key not in printed
    ]

    if remaining:
        print(f"  Remaining top-level keys: {remaining}")


def inspect_root(root: Path, label: str):
    print(f"\n[{label}]")
    print("-" * 80)
    print(f"Path: {root}")
    print(f"Exists: {root.exists()}")

    if not root.exists():
        print("No directory found.")
        return []

    files = targeted_files(root)

    print(f"Targeted artifacts found: {len(files)}")

    for path in files:
        print(f"\nArtifact: {path}")

        if path.suffix.lower() == ".json":
            data = safe_json_read(path)

            if isinstance(data, dict) and "__read_error__" in data:
                print(f"  READ ERROR: {data['__read_error__']}")
            else:
                print("  JSON readable: True")
                print_json_summary(path, data)
        else:
            print(f"  File type: {path.suffix.lower()}")
            print(f"  Size bytes: {path.stat().st_size}")

    return files


def main():
    print("=" * 80)
    print("FMP-05 OP-001 — T10 EXISTING POLICY / CLOSURE ARTIFACT INSPECTION")
    print("=" * 80)

    print("\n[1] T10 artifact inspection")
    t10_files = inspect_root(T10_ROOT, "T10 ROOT")

    print("\n[2] Targeted FMP artifact inspection")
    fmp_files = inspect_root(FMP_ROOT, "FMP ROOT")

    print("\n[3] T10-related artifact reconciliation")
    print("-" * 80)

    all_files = sorted(set(t10_files + fmp_files))

    print(f"Total targeted artifacts: {len(all_files)}")

    if not all_files:
        print(
            "No targeted T10/policy/automation/review/defer "
            "artifacts were found in the inspected locations."
        )
        print(
            "This is an inventory finding, not evidence that T10 policy "
            "does not exist elsewhere."
        )

    print("\n[4] Read-only safeguards")
    print("-" * 80)

    print("Models loaded: False")
    print("Predictions generated: False")
    print("Retraining performed: False")
    print("New calibration fitted: False")
    print("Threshold selected: False")
    print("Policy created: False")
    print("Artifacts modified: False")

    print("\n[5] Final summary")
    print("-" * 80)

    print("Operation type: READ_ONLY_T10_POLICY_CLOSURE_INSPECTION")
    print("STATUS: PASS")


if __name__ == "__main__":
    main()