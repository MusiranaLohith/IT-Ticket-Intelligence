from pathlib import Path
import re


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T5_ROOT = PROJECT_ROOT / "modeling" / "T5"

TARGET = "t5_mod009_locked_evaluation_predictions.npz"

KEYWORDS = [
    "t5_mod009_locked_evaluation_predictions",
    "locked_evaluation",
    "p_duplicate",
    "np.savez",
    "np.savez_compressed",
    "20827",
]


def inspect_file(path):
    """
    Read only source/provenance-sized files.

    Large CSV/NPY/NPZ files are deliberately excluded.
    """
    allowed = {
        ".py",
        ".json",
        ".txt",
        ".md",
        ".yaml",
        ".yml",
    }

    if path.suffix.lower() not in allowed:
        return

    try:
        size = path.stat().st_size
    except OSError:
        return

    # Safety limit: do not read unexpectedly large text files.
    if size > 2_000_000:
        return

    try:
        text = path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except Exception:
        return

    lower = text.lower()

    matches = [
        keyword
        for keyword in KEYWORDS
        if keyword.lower() in lower
    ]

    if not matches:
        return

    print()
    print("=" * 80)
    print(f"FILE: {path}")
    print(f"SIZE: {size:,} bytes")
    print(f"MATCHES: {matches}")
    print("=" * 80)

    lines = text.splitlines()

    printed = set()

    for i, line in enumerate(lines):

        if not any(
            keyword.lower() in line.lower()
            for keyword in matches
        ):
            continue

        start = max(0, i - 3)
        end = min(len(lines), i + 4)

        for j in range(start, end):

            if j in printed:
                continue

            printed.add(j)

            print(
                f"{j + 1:5d}: {lines[j][:220]}"
            )


def main():

    print("=" * 80)
    print("T10 / OP-017 — T5 LOCKED-EVALUATION PROVENANCE")
    print("=" * 80)

    print()
    print("Target artifact:")
    print(T5_ROOT / "metrics" / TARGET)

    target_path = T5_ROOT / "metrics" / TARGET

    if not target_path.exists():
        print()
        print("ERROR: Target NPZ does not exist.")
        return 1

    print()
    print("Target artifact EXISTS.")

    print()
    print("=" * 80)
    print("1. T5 FILE INVENTORY")
    print("=" * 80)

    for path in sorted(T5_ROOT.rglob("*")):

        if not path.is_file():
            continue

        suffix = path.suffix.lower()

        # Only show potentially relevant lightweight files.
        if suffix in {
            ".py",
            ".json",
            ".txt",
            ".md",
            ".yaml",
            ".yml",
        }:
            try:
                size = path.stat().st_size
            except OSError:
                continue

            print(
                f"{path.relative_to(T5_ROOT)} "
                f"({size:,} bytes)"
            )

    print()
    print("=" * 80)
    print("2. TARGETED PROVENANCE SEARCH")
    print("=" * 80)

    inspected = 0

    for path in sorted(T5_ROOT.rglob("*")):

        if not path.is_file():
            continue

        if path.suffix.lower() not in {
            ".py",
            ".json",
            ".txt",
            ".md",
            ".yaml",
            ".yml",
        }:
            continue

        inspected += 1
        inspect_file(path)

    print()
    print("=" * 80)
    print("3. SAFETY / METHODOLOGY CHECK")
    print("=" * 80)

    print("Large CSV/NPZ/NPY files were NOT loaded.")
    print("No dataset was modified.")
    print("No new split was created.")
    print("No positional ID mapping was inferred.")
    print("No T2/T4/T7 intersection was performed.")

    print()
    print("=" * 80)
    print("4. FINAL RESULT")
    print("=" * 80)

    print(f"Lightweight files inspected: {inspected}")
    print()
    print("OP-017 STATUS : PROVENANCE INVESTIGATION")
    print("RN ASSIGNMENT : DEFERRED")
    print()
    print(
        "Use the printed provenance evidence to determine whether "
        "the 20,827 locked rows have an explicit canonical-ID mapping."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())