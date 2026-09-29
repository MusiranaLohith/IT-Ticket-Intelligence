from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T10_ROOT = PROJECT_ROOT / "modeling" / "T10"

OUTPUT_DIR = PROJECT_ROOT / "modeling" / "FMP" / "metrics"

OUTPUT_PATH = (
    OUTPUT_DIR
    / "fmp05_op003_t10_authoritative_evidence_extraction.json"
)


KEYWORDS = [
    "model_independent",
    "empirical_evidence",
    "human_review",
    "automation",
    "defer",
    "threshold",
    "unsupported_operational_threshold_claim",
    "validation",
    "policy",
    "task_specific",
    "universal",
    "autonomous",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def flatten_strings(obj: Any, prefix: str = ""):
    """
    Yield (path, value) pairs for every string value in a JSON object.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            current = f"{prefix}.{key}" if prefix else str(key)
            yield from flatten_strings(value, current)

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            current = f"{prefix}[{index}]"
            yield from flatten_strings(value, current)

    elif isinstance(obj, str):
        yield prefix, obj


def keyword_matches(text: str):
    lowered = text.lower()

    matches = []

    for keyword in KEYWORDS:
        if keyword.lower() in lowered:
            matches.append(keyword)

    return matches


def summarize_value(value: Any, max_length: int = 500) -> str:
    if isinstance(value, str):
        text = value.strip()
    else:
        text = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
        )

    if len(text) > max_length:
        return text[:max_length] + "..."

    return text


def main():

    print("=" * 80)
    print("FMP-05 OP-003 — TARGETED T10 AUTHORITATIVE EVIDENCE EXTRACTION")
    print("=" * 80)

    print()
    print("[1] Project paths")
    print("-" * 80)

    print(f"Project root : {PROJECT_ROOT}")
    print(f"T10 root     : {T10_ROOT}")
    print(f"Output       : {OUTPUT_PATH}")

    if not PROJECT_ROOT.exists():
        raise RuntimeError(
            f"Project root does not exist: {PROJECT_ROOT}"
        )

    if not T10_ROOT.exists():
        raise RuntimeError(
            f"T10 root does not exist: {T10_ROOT}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print()
    print("[2] Discovering T10 JSON artifacts")
    print("-" * 80)

    json_files = sorted(T10_ROOT.rglob("*.json"))

    print(f"T10 JSON artifacts discovered: {len(json_files)}")

    if not json_files:
        raise RuntimeError(
            "No T10 JSON artifacts were discovered."
        )

    print()
    print("[3] Reading T10 artifacts")
    print("-" * 80)

    readable = []
    unreadable = []

    for path in json_files:
        try:
            data = load_json(path)

            readable.append(
                {
                    "path": str(path.relative_to(PROJECT_ROOT)),
                    "absolute_path": str(path),
                    "top_level_type": type(data).__name__,
                    "top_level_keys": (
                        sorted(data.keys())
                        if isinstance(data, dict)
                        else None
                    ),
                    "data": data,
                }
            )

        except Exception as exc:
            unreadable.append(
                {
                    "path": str(path.relative_to(PROJECT_ROOT)),
                    "error": str(exc),
                }
            )

    print(f"Readable artifacts   : {len(readable)}")
    print(f"Unreadable artifacts : {len(unreadable)}")

    if unreadable:
        print()
        print("Unreadable artifacts:")
        for item in unreadable:
            print(f"  - {item['path']}")
            print(f"    {item['error']}")

    print()
    print("[4] Targeted evidence extraction")
    print("-" * 80)

    evidence_records = []

    keyword_counts = {
        keyword: 0
        for keyword in KEYWORDS
    }

    for artifact in readable:

        relative_path = artifact["path"]
        data = artifact["data"]

        for json_path, value in flatten_strings(data):

            matches = keyword_matches(value)

            if not matches:
                continue

            for keyword in matches:
                keyword_counts[keyword] += 1

            evidence_records.append(
                {
                    "artifact": relative_path,
                    "json_path": json_path,
                    "matched_keywords": matches,
                    "value": summarize_value(value),
                }
            )

    print(
        f"Targeted evidence records extracted: "
        f"{len(evidence_records)}"
    )

    print()
    print("[5] Evidence indicator counts")
    print("-" * 80)

    for keyword in KEYWORDS:
        print(
            f"{keyword}: "
            f"{keyword_counts[keyword]}"
        )

    print()
    print("[6] High-value T10 evidence")
    print("-" * 80)

    high_value_terms = {
        "unsupported_operational_threshold_claim",
        "human_review",
        "defer",
        "threshold",
        "automation",
        "model_independent",
        "empirical_evidence",
    }

    high_value_records = [
        record
        for record in evidence_records
        if any(
            keyword in high_value_terms
            for keyword in record["matched_keywords"]
        )
    ]

    print(
        f"High-value records: "
        f"{len(high_value_records)}"
    )

    # Print only a bounded number to keep console output manageable.
    display_limit = 80

    for index, record in enumerate(
        high_value_records[:display_limit],
        start=1,
    ):
        print()
        print(f"[{index}] {record['artifact']}")
        print(f"JSON path : {record['json_path']}")
        print(
            "Keywords  : "
            + ", ".join(record["matched_keywords"])
        )
        print(f"Value     : {record['value']}")

    if len(high_value_records) > display_limit:
        print()
        print(
            f"... {len(high_value_records) - display_limit} "
            f"additional high-value records omitted from console."
        )

    print()
    print("[7] Explicit unsupported-threshold evidence")
    print("-" * 80)

    threshold_records = [
        record
        for record in evidence_records
        if "unsupported_operational_threshold_claim"
        in record["matched_keywords"]
        or "unsupported_operational_threshold_claim"
        in record["value"].lower()
    ]

    print(
        f"Unsupported-threshold records found: "
        f"{len(threshold_records)}"
    )

    for record in threshold_records[:30]:
        print()
        print(record["artifact"])
        print(record["json_path"])
        print(record["value"])

    print()
    print("[8] Safeguard verification")
    print("-" * 80)

    print("Models loaded: False")
    print("Predictions generated: False")
    print("Retraining performed: False")
    print("Calibration fitted: False")
    print("Threshold selected: False")
    print("Policy modified: False")
    print("Artifacts modified: False")

    result = {
        "operation": "FMP-05-OP-003",
        "operation_type": (
            "READ_ONLY_T10_AUTHORITATIVE_EVIDENCE_EXTRACTION"
        ),
        "status": (
            "PASS"
            if not unreadable
            else "PASS_WITH_UNREADABLE_ARTIFACTS"
        ),
        "project_root": str(PROJECT_ROOT),
        "t10_root": str(T10_ROOT),
        "artifacts_discovered": len(json_files),
        "artifacts_readable": len(readable),
        "artifacts_unreadable": len(unreadable),
        "keyword_counts": keyword_counts,
        "evidence_record_count": len(evidence_records),
        "high_value_record_count": len(high_value_records),
        "unsupported_threshold_record_count": (
            len(threshold_records)
        ),
        "unsupported_threshold_records": threshold_records,
        "read_only_safeguards": {
            "models_loaded": False,
            "predictions_generated": False,
            "retraining_performed": False,
            "calibration_fitted": False,
            "threshold_selected": False,
            "policy_modified": False,
            "artifacts_modified": False,
        },
        "evidence_records": evidence_records,
        "unreadable_artifacts": unreadable,
    }

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("[9] Output")
    print("-" * 80)

    print(f"Saved: {OUTPUT_PATH}")

    print()
    print("[10] Final summary")
    print("-" * 80)

    print(
        "Operation type: "
        "READ_ONLY_T10_AUTHORITATIVE_EVIDENCE_EXTRACTION"
    )

    print(
        "STATUS: "
        + result["status"]
    )

    print("=" * 80)


if __name__ == "__main__":
    main()