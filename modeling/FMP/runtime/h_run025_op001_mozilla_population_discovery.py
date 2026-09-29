from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

SEARCH_ROOTS = [
    PROJECT_ROOT,
    Path("/run/media/whiteblack"),
    Path("/mnt"),
]

REQUIRED_PATTERNS = {
    "id": ["id", "ticket_id", "issue_id"],
    "creation_time": ["creation time", "creation_time", "created", "creation"],
    "creator": ["creator"],
    "creator_detail": ["creator detail", "creator_detail"],
    "summary": ["summary", "title"],
    "description": ["description", "description_clean"],
}


def normalize(name):
    return str(name).strip().lower().replace("_", " ").replace("-", " ")


def classify_columns(columns):
    normalized = {normalize(c): c for c in columns}

    result = {}

    for logical_name, candidates in REQUIRED_PATTERNS.items():
        found = None

        for candidate in candidates:
            candidate_norm = normalize(candidate)

            if candidate_norm in normalized:
                found = normalized[candidate_norm]
                break

        result[logical_name] = found

    return result


def inspect_file(path):
    try:
        suffix = path.suffix.lower()

        if suffix == ".csv":
            df = pd.read_csv(path, nrows=5)

        elif suffix == ".parquet":
            df = pd.read_parquet(path)

            if len(df) > 5:
                df = df.head(5)

        else:
            return None

        columns = list(df.columns)
        mapping = classify_columns(columns)

        matched = sum(value is not None for value in mapping.values())

        return {
            "path": str(path),
            "suffix": suffix,
            "columns": columns,
            "mapping": mapping,
            "matched_runtime_fields": matched,
        }

    except Exception:
        return None


def main():

    print("=" * 70)
    print("H-RUN-025-OP-001 — MOZILLA CORE POPULATION DISCOVERY")
    print("=" * 70)

    candidates = []
    seen = set()

    for root in SEARCH_ROOTS:

        if not root.exists():
            continue

        print(f"[SCAN] {root}")

        try:
            files = list(root.rglob("*"))
        except Exception:
            continue

        for path in files:

            if not path.is_file():
                continue

            if path.suffix.lower() not in {".csv", ".parquet"}:
                continue

            path_str = str(path)

            if path_str in seen:
                continue

            seen.add(path_str)

            name = path.name.lower()

            # Focus discovery on Mozilla/Core-related files.
            if not any(
                token in name
                for token in ["mozilla", "core", "ticket", "issue"]
            ):
                continue

            result = inspect_file(path)

            if result is None:
                continue

            candidates.append(result)

    candidates.sort(
        key=lambda x: (
            -x["matched_runtime_fields"],
            len(x["columns"]),
            x["path"],
        )
    )

    print()
    print(f"Candidate files found : {len(candidates)}")
    print()

    if not candidates:
        print("STATUS : BLOCKED")
        print("Reason : No readable Mozilla/Core CSV or Parquet population found.")
        return

    for i, item in enumerate(candidates[:15], start=1):

        print(f"[{i}] {item['path']}")
        print(f"    runtime fields matched : "
              f"{item['matched_runtime_fields']}/6")

        mapping = item["mapping"]

        print(
            "    mapping : "
            f"ID={mapping['id']}, "
            f"Creation={mapping['creation_time']}, "
            f"Creator={mapping['creator']}, "
            f"CreatorDetail={mapping['creator_detail']}, "
            f"Summary={mapping['summary']}, "
            f"Description={mapping['description']}"
        )

        print()

    best = candidates[0]

    print("=" * 70)
    print("BEST CANDIDATE")
    print("=" * 70)

    print(f"Path : {best['path']}")
    print(f"Matched runtime fields : {best['matched_runtime_fields']}/6")

    print("Columns:")
    for column in best["columns"]:
        print(f"  - {column}")

    print()

    if best["matched_runtime_fields"] == 6:
        print("STATUS : PASS")
        print("The candidate contains all six runtime input fields.")
    else:
        print("STATUS : REQUIRES_REVIEW")
        print("The candidate does not expose all six runtime fields.")

    print()
    print("No model execution performed.")
    print("No dataset modification performed.")
    print("No training/evaluation population modified.")


if __name__ == "__main__":
    main()