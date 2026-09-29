from pathlib import Path
import csv
import json
import zipfile


DATA_ROOT = Path("/run/media/whiteblack/User 1/Datasets")
OUTPUT = (
    Path("/")
    / "modeling"
    / "inspection"
    / "t1_vscode_source_report.json"
)

KEYWORDS = ("vscode", "vs_code", "gitbugs", "visual studio code")

REQUIRED_COLUMNS = {
    "Type",
    "Summary",
    "Description",
    "Created",
    "Resolved",
    "Resolution",
}

IDENTIFIER_CANDIDATES = {
    "Issue id",
    "Issue_id",
    "issue_id",
    "id",
}


def read_csv_sample(path, limit=10000):
    with open(path, "r", encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []

        rows = []
        for i, row in enumerate(reader):
            if i >= limit:
                break
            rows.append(row)

    return columns, rows


def inspect_csv(path):
    columns, rows = read_csv_sample(path)

    result = {
        "file": str(path),
        "format": "csv",
        "columns": columns,
        "sample_rows_read": len(rows),
    }

    for column in columns:
        non_empty = sum(
            1 for row in rows
            if row.get(column) is not None
            and str(row.get(column)).strip() != ""
        )
        result.setdefault("sample_non_empty", {})[column] = non_empty

    if "Type" in columns:
        values = {}
        for row in rows:
            value = str(row.get("Type", "")).strip()
            if value:
                values[value] = values.get(value, 0) + 1

        result["sample_type_counts"] = dict(
            sorted(values.items(), key=lambda x: (-x[1], x[0]))
        )

    return result


def inspect_zip(path):
    with zipfile.ZipFile(path, "r") as z:
        members = z.namelist()

        csv_members = [
            m for m in members
            if m.lower().endswith(".csv")
        ]

        result = {
            "file": str(path),
            "format": "zip",
            "member_count": len(members),
            "csv_members": csv_members,
            "csv_inspections": [],
        }

        for member in csv_members:
            with z.open(member) as raw:
                sample = raw.read(2_000_000)

            text = sample.decode("utf-8-sig", errors="replace")
            reader = csv.reader(text.splitlines())

            try:
                columns = next(reader)
            except StopIteration:
                columns = []

            result["csv_inspections"].append({
                "member": member,
                "columns": columns,
            })

        return result


def main():
    if not DATA_ROOT.exists():
        raise FileNotFoundError(
            f"Dataset root not found: {DATA_ROOT}"
        )

    candidates = []

    for path in DATA_ROOT.rglob("*"):
        if not path.is_file():
            continue

        name = path.name.lower()

        if any(keyword in name for keyword in KEYWORDS):
            if path.suffix.lower() in {".csv", ".zip", ".json", ".jsonl"}:
                candidates.append(path)

    candidates = sorted(set(candidates))

    report = {
        "status": "INSPECTION_COMPLETE",
        "data_root": str(DATA_ROOT),
        "read_only": True,
        "raw_source_modified": False,
        "candidate_count": len(candidates),
        "candidates": [],
    }

    for path in candidates:
        try:
            if path.suffix.lower() == ".csv":
                inspection = inspect_csv(path)
            elif path.suffix.lower() == ".zip":
                inspection = inspect_zip(path)
            else:
                inspection = {
                    "file": str(path),
                    "format": path.suffix.lower().lstrip("."),
                    "inspection": "candidate located; format not parsed",
                }

            report["candidates"].append(inspection)

        except Exception as exc:
            report["candidates"].append({
                "file": str(path),
                "inspection_error": str(exc),
            })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("VSCODE_T1_SOURCE_INSPECTION_COMPLETE")
    print(f"OUTPUT={OUTPUT}")
    print(f"CANDIDATES_FOUND={len(candidates)}")
    print("READ_ONLY=True")
    print("RAW_SOURCE_MODIFIED=False")


if __name__ == "__main__":
    main()