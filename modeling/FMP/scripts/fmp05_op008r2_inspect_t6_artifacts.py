from pathlib import Path


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T6_ROOT = PROJECT_ROOT / "modeling/T6"


def main():
    print("=" * 80)
    print("FMP-05 OP-008R2 — INSPECT T6 ARTIFACTS")
    print("=" * 80)

    print(f"\nT6 root: {T6_ROOT}")
    print(f"exists: {T6_ROOT.exists()}")

    if not T6_ROOT.exists():
        print("\nSTATUS: BLOCKED")
        print("T6 modeling directory does not exist.")
        return

    json_files = sorted(T6_ROOT.rglob("*.json"))

    print(f"\nJSON artifacts found: {len(json_files)}")
    print("-" * 80)

    for path in json_files:
        relative = path.relative_to(PROJECT_ROOT)

        try:
            size = path.stat().st_size
        except OSError:
            size = "UNAVAILABLE"

        print(f"{relative}")
        print(f"  size_bytes: {size}")

    print("\n" + "-" * 80)
    print("Candidate closure-like filenames:")
    print("-" * 80)

    candidates = []

    for path in json_files:
        name = path.name.lower()

        if any(
            term in name
            for term in [
                "closure",
                "final",
                "mod010",
                "mod011",
                "mod012",
            ]
        ):
            candidates.append(path)

    if candidates:
        for path in candidates:
            print(path.relative_to(PROJECT_ROOT))
    else:
        print("No closure/final/mod010-mod012 candidates found.")

    print("\n" + "-" * 80)
    print("STATUS: PASS")
    print("Read-only T6 artifact inspection completed.")
    print("=" * 80)


if __name__ == "__main__":
    main()