from __future__ import annotations

import json
from pathlib import Path


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
INPUT = ROOT / "modeling/T8/mod033/t8_mod033_op004_t4_t5_development_provenance_audit.json"


with INPUT.open("r", encoding="utf-8") as f:
    data = json.load(f)


def show_section(name: str, section: dict) -> None:
    print(f"\n{'=' * 70}")
    print(name)
    print("=" * 70)

    print("Discovered files:", len(section.get("discovered_files", [])))

    groups = section.get("file_groups", {})
    for key in ["contracts", "splits", "predictions", "models", "scripts"]:
        print(f"{key}: {len(groups.get(key, []))}")

    print("\nCSV artifacts:")
    for item in section.get("csv_inspection", []):
        print(
            f"  {item.get('path')}"
            f" | rows={item.get('rows')}"
            f" | IDs={item.get('id_column_candidates')}"
            f" | Creation={item.get('creation_column_candidates')}"
        )

    print("\nJSON artifacts:")
    for item in section.get("json_inspection", []):
        print(f"  {item.get('path')}")
        interesting = item.get("interesting_fields", {})
        for key, value in interesting.items():
            text = str(value).replace("\n", " ")
            if len(text) > 300:
                text = text[:300] + "..."
            print(f"    {key}: {text}")


show_section("T4 SUMMARY", data.get("t4", {}))
show_section("T5 SUMMARY", data.get("t5", {}))

print(f"\n{'=' * 70}")
print("GUARDS")
print("=" * 70)

for key, value in data.get("guards", {}).items():
    print(f"{key}: {value}")

print(f"\n{'=' * 70}")
print("AUDIT DECISION")
print("=" * 70)
print(data.get("decision", "NOT FOUND"))

print("\nAudit status:", data.get("status", "NOT FOUND"))