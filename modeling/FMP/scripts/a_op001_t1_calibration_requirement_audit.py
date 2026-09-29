from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
METRICS_DIR = PROJECT_ROOT / "modeling" / "FMP" / "metrics"

OUTPUT_PATH = METRICS_DIR / "a_op001_t1_calibration_requirement_audit.json"


TARGET_FILES = [
    PROJECT_ROOT / "modeling/T1/analysis/t1_final_closure.json",
    PROJECT_ROOT / "modeling/T1/analysis/t1_it_support_3model_compare.json",
    PROJECT_ROOT / "modeling/T8/mod036/op026/t8_mod036_op026_decision_engine_validation.json",
    PROJECT_ROOT / "modeling/T9/mod037/t9_mod037_op015_final_integrated_closure.json",
    PROJECT_ROOT / "modeling/T10",
]


SEARCH_TERMS = [
    "calibrat",
    "probability",
    "probabilities",
    "probability-like",
    "confidence",
    "threshold",
    "t1",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def collect_json_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]

    if target.is_dir():
        return sorted(target.rglob("*.json"))

    return []


def flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(
            f"{flatten_text(k)} {flatten_text(v)}"
            for k, v in value.items()
        )

    if isinstance(value, list):
        return " ".join(flatten_text(v) for v in value)

    return str(value)


def extract_matches(data: Any) -> dict[str, list[str]]:
    text = flatten_text(data).lower()
    matches: dict[str, list[str]] = {}

    for term in SEARCH_TERMS:
        if term.lower() in text:
            matches[term] = ["present"]

    return matches


def main() -> None:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    discovered: list[Path] = []
    missing: list[str] = []

    for target in TARGET_FILES:
        files = collect_json_files(target)

        if files:
            discovered.extend(files)
        else:
            missing.append(str(target))

    # Remove duplicates while preserving order.
    unique_files = list(dict.fromkeys(discovered))

    file_evidence = []

    for path in unique_files:
        try:
            data = load_json(path)
            matches = extract_matches(data)

            file_evidence.append(
                {
                    "path": str(path),
                    "readable": True,
                    "keyword_matches": matches,
                }
            )
        except Exception as exc:
            file_evidence.append(
                {
                    "path": str(path),
                    "readable": False,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    # Explicitly inspect the known final T1 closure values when available.
    t1_closure_path = PROJECT_ROOT / "modeling/T1/analysis/t1_final_closure.json"

    t1_closure_summary = {
        "path": str(t1_closure_path),
        "readable": False,
        "decision_scores_are_probabilities": "NOT_ESTABLISHED",
        "calibration_required_by_closure": "NOT_ESTABLISHED",
    }

    if t1_closure_path.exists():
        try:
            t1_data = load_json(t1_closure_path)
            t1_text = flatten_text(t1_data).lower()

            t1_closure_summary["readable"] = True

            if "not calibrated" in t1_text:
                t1_closure_summary["calibration_status_evidence"] = (
                    "closure explicitly contains 'not calibrated'"
                )

            if "decision score" in t1_text:
                t1_closure_summary["decision_score_evidence"] = (
                    "closure contains decision-score semantics"
                )

            if "probability" in t1_text:
                t1_closure_summary["probability_term_present"] = True

        except Exception as exc:
            t1_closure_summary["error"] = (
                f"{type(exc).__name__}: {exc}"
            )

    result = {
        "operation": "A-OP-001",
        "operation_title": "T1 Calibration Requirement Audit",
        "status": "PASS",
        "read_only": True,
        "model_modified": False,
        "retraining_performed": False,
        "threshold_optimization_performed": False,
        "locked_test_reused": False,
        "project_root": str(PROJECT_ROOT),
        "files_discovered": len(unique_files),
        "missing_targets": missing,
        "t1_closure_summary": t1_closure_summary,
        "file_evidence": file_evidence,
        "decision_boundary": {
            "calibration_is_not_assumed": True,
            "calibration_should_only_proceed_if_downstream_contract_requires_probability_like_t1_output": True,
            "this_operation_does_not_authorize_calibration": True,
        },
    }

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    readable_count = sum(
        1 for item in file_evidence if item.get("readable") is True
    )

    print("=" * 62)
    print("A-OP-001 — T1 CALIBRATION REQUIREMENT AUDIT")
    print("=" * 62)
    print(f"Project root       : {PROJECT_ROOT}")
    print(f"JSON files checked : {len(unique_files)}")
    print(f"Readable           : {readable_count}")
    print(f"Missing targets    : {len(missing)}")
    print(f"Model modified     : False")
    print(f"Retraining         : False")
    print(f"Threshold tuning   : False")
    print(f"Locked test reused : False")
    print(f"Output             : {OUTPUT_PATH}")
    print("=" * 62)
    print("RESULT: PASS — requirement audit completed")
    print("=" * 62)


if __name__ == "__main__":
    main()