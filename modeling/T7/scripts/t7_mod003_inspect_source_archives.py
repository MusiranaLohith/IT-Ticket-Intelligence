from __future__ import annotations

from pathlib import Path
import zipfile


# =============================================================================
# T7 MOD-003 — SOURCE ARCHIVE STRUCTURE INSPECTION
# =============================================================================

DATASET_ROOT = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE"
)

ARCHIVES = [
    DATASET_ROOT / "Core_bugs.csv.zip",
    DATASET_ROOT / "Mozilla_CORE_dataset_issues.zip",
]


def inspect_archive(archive_path: Path) -> None:
    print("-" * 80)
    print(f"Archive: {archive_path.name}")
    print(f"Size:   {archive_path.stat().st_size:,} bytes")
    print()

    try:
        with zipfile.ZipFile(archive_path, "r") as archive:
            members = archive.infolist()

            print(f"Archive members: {len(members):,}")
            print()

            for index, member in enumerate(members, start=1):
                print(
                    f"  {index:04d}. "
                    f"{member.filename} "
                    f"| compressed={member.compress_size:,} bytes "
                    f"| uncompressed={member.file_size:,} bytes"
                )

    except zipfile.BadZipFile as exc:
        print(f"ERROR: Invalid ZIP archive: {exc}")

    print()


def main() -> None:
    print("=" * 80)
    print("T7 MOD-003 — SOURCE ARCHIVE STRUCTURE INSPECTION")
    print("=" * 80)
    print()

    for archive_path in ARCHIVES:
        if not archive_path.exists():
            print(f"NOT FOUND: {archive_path}")
            print()
            continue

        inspect_archive(archive_path)

    print("=" * 80)
    print("SCAN BOUNDARY")
    print("=" * 80)
    print("  ZIP central-directory metadata only: YES")
    print("  CSV contents read: NO")
    print("  Archive extraction: NO")
    print("  Raw dataset modified: NO")
    print("  T7 artifact modified: NO")
    print("  Model trained: NO")


if __name__ == "__main__":
    main()