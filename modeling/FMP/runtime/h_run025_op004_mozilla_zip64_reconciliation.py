from pathlib import Path
import struct
import json


ARCHIVE = Path(
    "/run/media/whiteblack/User 1/Datasets/Mozilla_CORE/"
    "Mozilla_CORE_dataset_issues.zip"
)

OUTPUT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/modeling/FMP/"
    "metrics/h_run025_op004_mozilla_zip64_reconciliation.json"
)

LOCAL_HEADER = b"PK\x03\x04"
ZIP64_EOCD = b"PK\x06\x06"
ZIP64_LOCATOR = b"PK\x06\x07"
CENTRAL_HEADER = b"PK\x01\x02"
EOCD = b"PK\x05\x06"


def find_last(data, signature):
    return data.rfind(signature)


def inspect_local_header(path):
    with path.open("rb") as f:
        data = f.read(64)

    result = {
        "bytes_read": len(data),
        "signature_found": data.startswith(LOCAL_HEADER),
    }

    if not data.startswith(LOCAL_HEADER):
        result["reason"] = "Local-file-header signature not found at offset 0."
        result["first_32_bytes_hex"] = data[:32].hex()
        return result

    if len(data) < 30:
        result["parseable"] = False
        result["reason"] = "Incomplete local-file header."
        return result

    (
        signature,
        version_needed,
        flags,
        compression_method,
        mod_time,
        mod_date,
        crc32,
        compressed_size,
        uncompressed_size,
        filename_length,
        extra_length,
    ) = struct.unpack_from("<4s5H3L2H", data, 0)

    filename_start = 30
    filename_end = filename_start + filename_length

    filename = data[filename_start:filename_end]

    result.update(
        {
            "parseable": True,
            "version_needed": version_needed,
            "flags": flags,
            "compression_method": compression_method,
            "crc32": f"{crc32:08x}",
            "compressed_size_32": compressed_size,
            "uncompressed_size_32": uncompressed_size,
            "filename_length": filename_length,
            "extra_length": extra_length,
            "filename": filename.decode("utf-8", errors="replace"),
        }
    )

    return result


def inspect_zip64_tail(path):
    file_size = path.stat().st_size

    with path.open("rb") as f:
        start = max(0, file_size - 131072)
        f.seek(start)
        tail = f.read()

    result = {
        "tail_start": start,
        "tail_bytes": len(tail),
    }

    locator_pos = find_last(tail, ZIP64_LOCATOR)
    eocd64_pos = find_last(tail, ZIP64_EOCD)
    eocd_pos = find_last(tail, EOCD)

    result["signature_positions"] = {
        "zip64_locator": (
            None if locator_pos == -1 else start + locator_pos
        ),
        "zip64_eocd": (
            None if eocd64_pos == -1 else start + eocd64_pos
        ),
        "eocd": None if eocd_pos == -1 else start + eocd_pos,
    }

    if locator_pos != -1 and locator_pos + 20 <= len(tail):
        (
            signature,
            disk_with_eocd64,
            eocd64_offset,
            total_disks,
        ) = struct.unpack_from("<4sLQL", tail, locator_pos)

        result["zip64_locator_data"] = {
            "disk_with_eocd64": disk_with_eocd64,
            "zip64_eocd_offset": eocd64_offset,
            "total_disks": total_disks,
        }

    if eocd64_pos != -1 and eocd64_pos + 56 <= len(tail):
        (
            signature,
            record_size,
            version_made,
            version_needed,
            disk_number,
            central_directory_disk,
            entries_on_disk,
            total_entries,
            central_directory_size,
            central_directory_offset,
        ) = struct.unpack_from(
            "<4sQ2H2L2Q2Q",
            tail,
            eocd64_pos,
        )

        result["zip64_eocd_data"] = {
            "record_size": record_size,
            "version_made": version_made,
            "version_needed": version_needed,
            "disk_number": disk_number,
            "central_directory_disk": central_directory_disk,
            "entries_on_disk": entries_on_disk,
            "total_entries": total_entries,
            "central_directory_size": central_directory_size,
            "central_directory_offset": central_directory_offset,
        }

    return result


def inspect_python_metadata(path):
    import zipfile

    result = {
        "opened": False,
        "entry_count": None,
        "entries": [],
        "error": None,
    }

    try:
        with zipfile.ZipFile(path, "r") as zf:
            result["opened"] = True

            infos = zf.infolist()
            result["entry_count"] = len(infos)

            for info in infos:
                result["entries"].append(
                    {
                        "filename": info.filename,
                        "compress_size": info.compress_size,
                        "file_size": info.file_size,
                        "header_offset": info.header_offset,
                        "compress_type": info.compress_type,
                        "flag_bits": info.flag_bits,
                        "CRC": f"{info.CRC:08x}",
                        "create_system": info.create_system,
                        "extract_version": info.extract_version,
                    }
                )

    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"

    return result


def main():
    print("=" * 70)
    print("H-RUN-025-OP-004 — MOZILLA CORE ZIP64 RECONCILIATION")
    print("=" * 70)

    if not ARCHIVE.exists():
        print("\nARCHIVE : MISSING")
        print("STATUS  : BLOCKED")
        return

    size_bytes = ARCHIVE.stat().st_size

    print("\nARCHIVE")
    print(f"  path       : {ARCHIVE}")
    print(f"  size_bytes : {size_bytes:,}")

    print("\n[1] Inspecting first 64 bytes only...")
    local = inspect_local_header(ARCHIVE)

    print(f"    local-header signature : {local['signature_found']}")
    if local.get("filename"):
        print(f"    filename               : {local['filename']}")
        print(
            f"    compression method     : "
            f"{local['compression_method']}"
        )
        print(
            f"    compressed size (32)  : "
            f"{local['compressed_size_32']:,}"
        )
        print(
            f"    uncompressed size (32): "
            f"{local['uncompressed_size_32']:,}"
        )

    print("\n[2] Inspecting final 128 KiB only...")
    zip64 = inspect_zip64_tail(ARCHIVE)

    locator = zip64.get("zip64_locator_data")
    eocd64 = zip64.get("zip64_eocd_data")

    if locator:
        print(
            "    ZIP64 EOCD offset     : "
            f"{locator['zip64_eocd_offset']:,}"
        )
        print(
            "    total disks           : "
            f"{locator['total_disks']}"
        )

    if eocd64:
        print(
            "    ZIP64 total entries   : "
            f"{eocd64['total_entries']}"
        )
        print(
            "    ZIP64 CD size         : "
            f"{eocd64['central_directory_size']:,}"
        )
        print(
            "    ZIP64 CD offset       : "
            f"{eocd64['central_directory_offset']:,}"
        )

    print("\n[3] Python metadata reconciliation...")
    python_metadata = inspect_python_metadata(ARCHIVE)

    print(
        f"    opened      : "
        f"{python_metadata['opened']}"
    )
    print(
        f"    entry_count : "
        f"{python_metadata['entry_count']}"
    )

    if python_metadata["entries"]:
        entry = python_metadata["entries"][0]
        print(f"    filename    : {entry['filename']}")
        print(f"    header_offset: {entry['header_offset']:,}")
        print(f"    compressed  : {entry['compress_size']:,}")
        print(f"    uncompressed: {entry['file_size']:,}")
        print(f"    CRC         : {entry['CRC']}")

    result = {
        "operation": "H-RUN-025-OP-004",
        "operation_name": "Mozilla CORE ZIP64 reconciliation",
        "archive": {
            "path": str(ARCHIVE),
            "size_bytes": size_bytes,
        },
        "local_header": local,
        "zip64_tail": zip64,
        "python_metadata": python_metadata,
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

    if (
        local.get("signature_found")
        and python_metadata.get("opened")
        and python_metadata.get("entry_count") == 1
    ):
        print("STATUS : PASS")
    else:
        print("STATUS : STRUCTURAL_REVIEW_REQUIRED")


if __name__ == "__main__":
    main()