from pathlib import Path


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

TARGET_NAME = "t6_mod010_final_closure.json"

SEARCH_ROOTS = [
    PROJECT_ROOT / "modeling/T6",
    PROJECT_ROOT / "modeling/FMP",
]


def main():
    print("=" * 80)
    print("FMP-05 OP-008R — LOCATE AUTHORITATIVE T6 CLOSURE")
    print("=" * 80)

    matches = []

    for root in SEARCH_ROOTS:
        print(f"\nSearching: {root}")

        if not root.exists():
            print("  exists: False")
            continue

        print("  exists: True")

        for path in root.rglob(TARGET_NAME):
            matches.append(path)
            print(f"  MATCH: {path}")

    print("\n" + "-" * 80)

    if not matches:
        print("STATUS: BLOCKED")
        print(f"No file named {TARGET_NAME} found under the expected T6/FMP roots.")
    else:
        print(f"Matches found: {len(matches)}")

        for path in matches:
            print(f"  {path}")

        if len(matches) == 1:
            print("\nSTATUS: PASS")
            print("Exactly one candidate closure artifact was located.")
        else:
            print("\nSTATUS: REVIEW_REQUIRED")
            print("Multiple candidate closure artifacts were located.")

    print("=" * 80)


if __name__ == "__main__":
    main()