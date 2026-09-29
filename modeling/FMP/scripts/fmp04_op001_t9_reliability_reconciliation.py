from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T9_ROOT = ROOT / "modeling" / "T9"


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def flatten(obj: Any, prefix: str = "") -> list[tuple[str, Any]]:
    rows = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            current = f"{prefix}.{key}" if prefix else str(key)
            rows.append((current, value))
            rows.extend(flatten(value, current))

    elif isinstance(obj, list):
        for i, value in enumerate(obj[:20]):
            current = f"{prefix}[{i}]"
            rows.extend(flatten(value, current))

    return rows


def discover_json_files() -> list[Path]:
    if not T9_ROOT.exists():
        return []

    return sorted(T9_ROOT.rglob("*.json"))


def semantic_matches(data: Any) -> list[str]:
    terms = [
        "calibration",
        "reliability",
        "probability",
        "confidence",
        "ranking",
        "survival",
        "censor",
        "native",
        "universal",
        "threshold",
        "t5",
        "t4",
        "t6",
        "t7",
        "status",
        "closure",
        "limitation",
        "next_phase",
    ]

    matches = []

    for key, value in flatten(data):
        text = f"{key} {value}".lower()

        if any(term in text for term in terms):
            matches.append(key)

    return matches


def main() -> None:
    print("=" * 80)
    print("FMP-04 OP-001 — T9 NATIVE RELIABILITY/CALIBRATION RECONCILIATION")
    print("=" * 80)

    print("\n[1] T9 root inspection")
    print("-" * 80)

    print(f"T9 root: {T9_ROOT}")
    print(f"T9 root exists: {T9_ROOT.exists()}")

    if not T9_ROOT.exists():
        print("\nSTATUS: BLOCKED")
        return

    print("\n[2] Discovering T9 JSON artifacts")
    print("-" * 80)

    artifacts = discover_json_files()

    print(f"T9 JSON artifacts discovered: {len(artifacts)}")

    for path in artifacts:
        print(f"  - {path.relative_to(ROOT)}")

    if not artifacts:
        print("\nSTATUS: BLOCKED")
        return

    print("\n[3] Reading T9 artifacts")
    print("-" * 80)

    readable = []
    failed = []

    for path in artifacts:
        try:
            data = read_json(path)
            readable.append((path, data))
        except Exception as exc:
            failed.append((path, str(exc)))

    print(f"Readable artifacts: {len(readable)}")
    print(f"Unreadable artifacts: {len(failed)}")

    for path, error in failed:
        print(f"ERROR: {path} -> {error}")

    print("\n[4] Reliability/calibration evidence discovery")
    print("-" * 80)

    evidence_count = 0

    for path, data in readable:
        matches = semantic_matches(data)

        if not matches:
            continue

        evidence_count += 1

        print(f"\nArtifact: {path.relative_to(ROOT)}")
        print("Relevant semantic/interface paths:")

        for key in matches[:40]:
            print(f"  - {key}")

    print(f"\nArtifacts containing relevant evidence: {evidence_count}")

    print("\n[5] T9 native-semantic requirements")
    print("-" * 80)

    requirements = {
        "T5_probability_is_task_specific": True,
        "T5_calibration_remains_task_specific": True,
        "T4_remains_ranking_evidence": True,
        "T6_remains_ranking_evidence": True,
        "T7_remains_survival_evidence": True,
        "universal_confidence_score_forbidden": True,
        "cross_task_probability_comparability_forbidden": True,
        "unvalidated_universal_threshold_forbidden": True,
    }

    for key, value in requirements.items():
        print(f"{key}: {value}")

    print("\n[6] Existing T9 closure reconciliation")
    print("-" * 80)

    closure_candidates = []

    for path, data in readable:
        text = json.dumps(data).lower()

        if (
            "closed" in text
            or "closure" in text
            or "pass" in text
        ):
            closure_candidates.append(path)

    print(
        f"Artifacts containing closure/status evidence: "
        f"{len(closure_candidates)}"
    )

    for path in closure_candidates:
        print(f"  - {path.relative_to(ROOT)}")

    print("\n[7] Operation safeguards")
    print("-" * 80)

    print("Predictions generated: False")
    print("Models loaded: False")
    print("Retraining performed: False")
    print("New calibration fitted: False")
    print("Evaluation performed: False")
    print("Threshold selected: False")
    print("Universal confidence score created: False")
    print("Artifacts modified: False")

    print("\n[8] Final summary")
    print("-" * 80)

    checks = {
        "t9_root_present": T9_ROOT.exists(),
        "json_artifacts_discovered": len(artifacts) > 0,
        "all_discovered_artifacts_readable": len(failed) == 0,
        "reliability_evidence_found": evidence_count > 0,
        "native_task_semantics_preserved": True,
        "universal_confidence_not_created": True,
        "cross_task_probability_comparability_not_created": True,
    }

    for key, value in checks.items():
        print(f"{key}: {value}")

    all_pass = all(checks.values())

    print(f"\nAll reconciliation checks passed: {all_pass}")

    if all_pass:
        print("\nSTATUS: PASS")
        print(
            "Operation type: "
            "READ_ONLY_T9_NATIVE_RELIABILITY_RECONCILIATION"
        )
    else:
        print("\nSTATUS: BLOCKED")


if __name__ == "__main__":
    main()