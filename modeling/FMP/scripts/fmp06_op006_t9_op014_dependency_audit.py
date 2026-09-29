from pathlib import Path
import ast
import json
import re


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

TARGET = (
    PROJECT_ROOT
    / "modeling"
    / "T9"
    / "scripts"
    / "t9_mod037_op014_cross_task_evidence_synthesis.py"
)

OUTPUT = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "fmp06_op006_t9_op014_dependency_audit.json"
)


def collect_string_constants(tree):
    values = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            values.append(node.value)

    return values


def main():
    print("=" * 80)
    print("FMP-06 OP-006")
    print("T9 OP-014 PRODUCER / CONSUMER DEPENDENCY AUDIT")
    print("=" * 80)

    if not TARGET.exists():
        raise FileNotFoundError(f"Target script not found: {TARGET}")

    source = TARGET.read_text(encoding="utf-8")
    tree = ast.parse(source)

    strings = collect_string_constants(tree)

    path_like_strings = []
    t8_references = []
    op025_references = []
    op026_references = []
    t9_references = []

    for value in strings:
        lower = value.lower()

        if (
            "/" in value
            or "\\" in value
            or ".json" in lower
            or ".csv" in lower
            or ".joblib" in lower
        ):
            path_like_strings.append(value)

        if "modeling/t8" in lower or "modeling\\t8" in lower:
            t8_references.append(value)

        if "op025" in lower:
            op025_references.append(value)

        if "op026" in lower:
            op026_references.append(value)

        if "modeling/t9" in lower or "modeling\\t9" in lower:
            t9_references.append(value)

    # Also inspect raw source for important dependency keywords.
    source_lower = source.lower()

    keyword_hits = {}
    for keyword in [
        "op025",
        "op026",
        "t8",
        "t9",
        "decision_engine",
        "prediction",
        "evidence",
        "input",
        "output",
    ]:
        keyword_hits[keyword] = source_lower.count(keyword)

    result = {
        "operation": "FMP-06 OP-006",
        "target_script": str(TARGET),
        "syntax_parse": {
            "valid": True,
            "statement_count": len(tree.body),
        },
        "dependency_evidence": {
            "t8_references": sorted(set(t8_references)),
            "op025_references": sorted(set(op025_references)),
            "op026_references": sorted(set(op026_references)),
            "t9_references": sorted(set(t9_references)),
            "path_like_strings": sorted(set(path_like_strings)),
            "keyword_hits": keyword_hits,
        },
        "interpretation": {
            "fresh_t8_op025_consumption_established": bool(op025_references),
            "t8_reference_established": bool(t8_references),
            "op026_reference_established": bool(op026_references),
            "t9_reference_established": bool(t9_references),
        },
        "safeguards": {
            "model_training": False,
            "prediction_generation": False,
            "artifact_modification": False,
            "threshold_selection": False,
            "calibration": False,
            "policy_change": False,
        },
        "status": "PASS",
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    print()
    print("Target:")
    print(f"  {TARGET}")

    print()
    print("T8 references:")
    for item in sorted(set(t8_references)):
        print(f"  {item}")

    print()
    print("OP-025 references:")
    for item in sorted(set(op025_references)):
        print(f"  {item}")

    print()
    print("OP-026 references:")
    for item in sorted(set(op026_references)):
        print(f"  {item}")

    print()
    print("T9 references:")
    for item in sorted(set(t9_references)):
        print(f"  {item}")

    print()
    print("Fresh OP-025 consumption established:")
    print(f"  {bool(op025_references)}")

    print()
    print("Output:")
    print(f"  {OUTPUT}")

    print()
    print("Status: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()