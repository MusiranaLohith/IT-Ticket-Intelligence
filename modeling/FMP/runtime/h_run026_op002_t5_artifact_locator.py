from pathlib import Path


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T5_ROOT = PROJECT_ROOT / "modeling" / "T5"

TARGETS = [
    "t5_mod005_tfidf.joblib",
    "t5_mod005_logreg.joblib",
    "t5_mod007_calibrated_tfidf.joblib",
    "t5_mod007_calibration_models.joblib",
]


def main():
    print("=" * 70)
    print("H-RUN-026-OP-002 — T5 ARTIFACT LOCATOR")
    print("=" * 70)

    print(f"\nSearch root:")
    print(f"  {T5_ROOT}")

    all_found = True

    print("\nResults:")

    for name in TARGETS:

        matches = sorted(
            path
            for path in T5_ROOT.rglob(name)
            if path.is_file()
            and path.stat().st_size > 0
        )

        print(f"\n{name}")

        if not matches:
            print("  NOT FOUND")
            all_found = False
            continue

        for path in matches:
            print(f"  {path}")
            print(
                f"  size_bytes: {path.stat().st_size:,}"
            )

    print("\n" + "=" * 70)

    if all_found:
        print("RESULT : ALL_T5_ARTIFACTS_LOCATED")
        print("STATUS : PASS")
    else:
        print("RESULT : T5_ARTIFACTS_MISSING")
        print("STATUS : REQUIRES_REVIEW")


if __name__ == "__main__":
    main()