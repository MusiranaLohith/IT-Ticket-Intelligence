from pathlib import Path
import struct
import zipfile
import json


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
ARCHIVE = (
    PROJECT_ROOT
    / "Datasets"
    / "Mozilla_CORE"
    / "Mozilla_CORE_dataset_issues.zip"
)

# Actual mounted dataset location
ARCHIVE = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "Mozilla_CORE_dataset_issues.zip"
)

OUTPUT = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "h_run025_op003_mozilla_archive_structure.json"
)


def format_gib(value):
    return round(value / (1024 ** 3), 3)


def read_tail(path, size=65536):
    with path.open("rb") as f:
        file_size = path.stat().st_size
        start = max(0, file_size - size)
        f.seek(start)
        return start, f.read()


def inspect_signatures(tail, tail_start):
    signatures = {
        "local_file_header": b"PK\x03\x04",
        "central_directory": b"PK\x01\x02",
        "end_of_central_directory": b"PK\x05\x06",
        "zip64_end_of_central_directory": b"PK\x06\x06",
        "zip64_locator": b"PK\x06\x07",
    }

    result = {}

    for name, signature in signatures.items():
        positions = []
        offset = 0

        while True:
            pos = tail.find(signature, offset)
            if pos == -1:
                break

            positions.append(tail_start + pos)
            offset = pos + 1

        result[name] = {
            "count": len(positions),
            "positions": positions[-10:],
        }

    return result


def inspect_eocd(tail, tail_start):
    signature = b"PK\x05\x06"
    pos = tail.rfind(signature)

    if pos == -1:
        return {
            "found": False,
            "reason": "EOCD signature not found in inspected tail",
        }

    absolute_pos = tail_start + pos

    if pos + 22 > len(tail):
        return {
            "found": True,
            "absolute_offset": absolute_pos,
            "parseable": False,
            "reason": "EOCD signature found but incomplete record",
        }

    fields = struct.unpack_from("<4s4H2LH", tail, pos)

    (
        sig,
        disk_number,
        central_directory_disk,
        entries_on_disk,
        total_entries,
        central_directory_size,
        central_directory_offset,
        comment_length,
    ) = fields

    return {
        "found": True,
        "absolute_offset": absolute_pos,
        "parseable": True,
        "disk_number": disk_number,
        "central_directory_disk": central_directory_disk,
        "entries_on_disk": entries_on_disk,
        "total_entries": total_entries,
        "central_directory_size": central_directory_size,
        "central_directory_offset": central_directory_offset,
        "comment_length": comment_length,
    }


def inspect_zip_parser(path):
    result = {
        "opened": False,
        "readable": False,
        "entry_count": None,
        "entries": [],
        "error": None,
    }

    try:
        with zipfile.ZipFile(path, "r") as zf:
            result["opened"] = True

            infos = zf.infolist()
            result["readable"] = True
            result["entry_count"] = len(infos)

            # Do NOT read/decompress file contents.
            for info in infos[:20]:
                result["entries"].append(
                    {
                        "filename": info.filename,
                        "file_size": info.file_size,
                        "compress_size": info.compress_size,
                        "header_offset": info.header_offset,
                        "compress_type": info.compress_type,
                    }
                )

    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"

    return result


def main():
    print("=" * 70)
    print("H-RUN-025-OP-003 — MOZILLA CORE ARCHIVE STRUCTURE")
    print("=" * 70)

    if not ARCHIVE.exists():
        print("\nARCHIVE : MISSING")
        print(f"PATH    : {ARCHIVE}")
        print("STATUS  : BLOCKED")
        return

    size_bytes = ARCHIVE.stat().st_size

    print("\nARCHIVE")
    print(f"  path       : {ARCHIVE}")
    print(f"  size_bytes : {size_bytes:,}")
    print(f"  size_gib   : {format_gib(size_bytes)}")

    print("\n[1] Reading final 64 KiB only...")
    tail_start, tail = read_tail(ARCHIVE)

    print(f"    tail_start : {tail_start:,}")
    print(f"    tail_bytes : {len(tail):,}")

    signatures = inspect_signatures(tail, tail_start)

    print("\n[2] ZIP signatures found")
    for name, info in signatures.items():
        print(f"    {name:32s}: {info['count']}")

    print("\n[3] End-of-central-directory")
    eocd = inspect_eocd(tail, tail_start)

    if eocd.get("found"):
        print(f"    absolute_offset          : {eocd['absolute_offset']:,}")
        print(f"    parseable                : {eocd['parseable']}")

        if eocd.get("parseable"):
            print(f"    total_entries            : {eocd['total_entries']}")
            print(
                "    central_directory_size  : "
                f"{eocd['central_directory_size']:,}"
            )
            print(
                "    central_directory_offset: "
                f"{eocd['central_directory_offset']:,}"
            )
            print(f"    comment_length           : {eocd['comment_length']}")
    else:
        print("    EOCD : NOT FOUND")

    print("\n[4] Python ZIP parser")
    parser_result = inspect_zip_parser(ARCHIVE)

    print(f"    opened      : {parser_result['opened']}")
    print(f"    readable    : {parser_result['readable']}")
    print(f"    entry_count : {parser_result['entry_count']}")

    if parser_result["error"]:
        print(f"    error       : {parser_result['error']}")

    if parser_result["entries"]:
        print("\n    First entries:")
        for entry in parser_result["entries"][:10]:
            print(
                f"      {entry['filename']} "
                f"(compressed={entry['compress_size']:,}, "
                f"uncompressed={entry['file_size']:,})"
            )

    result = {
        "operation": "H-RUN-025-OP-003",
        "operation_name": "Mozilla CORE archive structural inspection",
        "archive": {
            "path": str(ARCHIVE),
            "size_bytes": size_bytes,
            "size_gib": format_gib(size_bytes),
        },
        "inspection": {
            "tail_bytes_read": len(tail),
            "signatures": signatures,
            "eocd": eocd,
            "zip_parser": parser_result,
        },
        "controls": {
            "archive_modified": False,
            "archive_extracted": False,
            "dataset_loaded": False,
            "dataset_rewritten": False,
            "model_execution": False,
        },
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    print("\n" + "=" * 70)
    print("OUTPUT")
    print("=" * 70)
    print(f"JSON : {OUTPUT}")

    if parser_result["readable"]:
        print("STATUS : PASS")
    else:
        print("STATUS : STRUCTURAL_REVIEW_REQUIRED")


if __name__ == "__main__":
    main()