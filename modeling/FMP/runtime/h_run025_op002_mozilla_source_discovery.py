from pathlib import Path


SEARCH_ROOTS = [
    Path("/run/media/whiteblack"),
    Path("/mnt"),
    Path("/home/whiteblack"),
]

TARGET_NAMES = {
    "Mozilla_CORE_dataset_issues.zip",
    "dataset_issues_TOTAL_TOTAL.csv",
    "Core_bugs.csv",
}


def main():

    print("=" * 70)
    print("H-RUN-025-OP-002 — MOZILLA CORE SOURCE LOCATOR")
    print("=" * 70)

    print("Known targets:")
    for name in sorted(TARGET_NAMES):
        print(f"  - {name}")

    print()

    found = []

    for root in SEARCH_ROOTS:

        if not root.exists():
            continue

        print(f"[SCAN] {root}")

        try:
            for path in root.rglob("*"):

                if not path.is_file():
                    continue

                if path.name in TARGET_NAMES:
                    found.append(path)

        except (PermissionError, OSError) as exc:
            print(f"  scan warning: {exc}")

    # Remove duplicates while preserving order.
    unique_found = []
    seen = set()

    for path in found:
        resolved = str(path.resolve())

        if resolved not in seen:
            seen.add(resolved)
            unique_found.append(path)

    print()
    print("=" * 70)
    print("KNOWN SOURCE MATCHES")
    print("=" * 70)

    if not unique_found:
        print("No known Mozilla source file found.")
        print()
        print("STATUS : SOURCE_NOT_LOCATED")
        return

    for i, path in enumerate(unique_found, start=1):

        try:
            size_bytes = path.stat().st_size
            size_gb = size_bytes / (1024 ** 3)
        except OSError:
            size_bytes = None
            size_gb = None

        print()
        print(f"[{i}] {path}")
        print(f"    name       : {path.name}")

        if size_bytes is not None:
            print(f"    size_bytes : {size_bytes:,}")
            print(f"    size_gb    : {size_gb:.3f}")

        if path.name == "Mozilla_CORE_dataset_issues.zip":
            print("    type       : ORIGINAL MOZILLA CORE ARCHIVE")
            print("    action     : LOCATED ONLY — NOT EXTRACTED")

        elif path.name == "dataset_issues_TOTAL_TOTAL.csv":
            print("    type       : KNOWN ARCHIVE ENTRY / RAW DATASET CANDIDATE")
            print("    action     : LOCATED ONLY")

        elif path.name == "Core_bugs.csv":
            print("    type       : KNOWN MOZILLA CORE CSV")
            print("    action     : LOCATED ONLY")

    print()
    print("=" * 70)
    print("SOURCE DISCOVERY RESULT")
    print("=" * 70)

    archive_matches = [
        p for p in unique_found
        if p.name == "Mozilla_CORE_dataset_issues.zip"
    ]

    raw_matches = [
        p for p in unique_found
        if p.name in {
            "dataset_issues_TOTAL_TOTAL.csv",
            "Core_bugs.csv",
        }
    ]

    print(f"Mozilla archive matches : {len(archive_matches)}")
    print(f"Known raw CSV matches   : {len(raw_matches)}")

    if archive_matches:
        print()
        print("RESULT : ORIGINAL_MOZILLA_ARCHIVE_LOCATED")

    elif raw_matches:
        print()
        print("RESULT : MOZILLA_RAW_CSV_LOCATED")

    else:
        print()
        print("RESULT : MOZILLA_SOURCE_NOT_LOCATED")

    print()
    print("No archive extraction performed.")
    print("No CSV loaded into memory.")
    print("No dataset modification performed.")
    print("No model execution performed.")

    print()
    print("STATUS : PASS")


if __name__ == "__main__":
    main()