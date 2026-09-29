from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
METRICS_DIR = PROJECT_ROOT / "modeling/FMP/metrics"

OUTPUT_PATH = (
    METRICS_DIR
    / "a_op002_t1_calibration_requirement_reconciliation.json"
)


FILES = {
    "t1_final_closure": (
        PROJECT_ROOT / "modeling/T1/analysis/t1_final_closure.json"
    ),
    "t1_model_comparison": (
        PROJECT_ROOT / "modeling/T1/analysis/t1_it_support_3model_compare.json"
    ),
    "t8_final_validation": (
        PROJECT_ROOT
        / "modeling/T8/mod036/op026/"
        / "t8_mod036_op026_decision_engine_validation.json"
    ),
    "t9_final_closure": (
        PROJECT_ROOT
        / "modeling/T9/mod037/"
        / "t9_mod037_op015_final_integrated_closure.json"
    ),
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def walk(
    value: Any,
    path: str = "",
):
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            yield child_path, child
            yield from walk(child, child_path)

    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            yield child_path, child
            yield from walk(child, child_path)


def collect_relevant_fields(data: Any) -> list[dict[str, Any]]:
    terms = (
        "calibrat",
        "probabil",
        "confidence",
        "threshold",
        "decision",
        "score",
        "t1",
    )

    results = []

    for path, value in walk(data):
        path_lower = path.lower()

        if any(term in path_lower for term in terms):
            results.append(
                {
                    "path": path,
                    "value": value,
                }
            )

    return results


def compact(value: Any, max_len: int = 300) -> str:
    text = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    if len(text) <= max_len:
        return text

    return text[:max_len] + "...<truncated>"


def main() -> None:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    evidence = {}
    readable = 0
    missing = []

    for name, path in FILES.items():
        if not path.exists():
            missing.append(
                {
                    "name": name,
                    "path": str(path),
                }
            )
            continue

        try:
            data = load_json(path)
            readable += 1

            evidence[name] = {
                "path": str(path),
                "readable": True,
                "relevant_fields": collect_relevant_fields(data),
            }

        except Exception as exc:
            evidence[name] = {
                "path": str(path),
                "readable": False,
                "error": f"{type(exc).__name__}: {exc}",
            }

    # Directly capture the known T1 closure semantics.
    t1 = evidence.get("t1_final_closure", {})

    t1_text = json.dumps(
        t1,
        ensure_ascii=False,
    ).lower()

    t1_probability_language = (
        "probability" in t1_text
        or "probabilities" in t1_text
    )

    t1_calibration_language = "calibrat" in t1_text

    # Downstream evidence is inspected for explicit T1 probability
    # requirements rather than assuming that generic probability/
    # calibration terms imply a T1 requirement.
    downstream_text = json.dumps(
        {
            "t8": evidence.get("t8_final_validation", {}),
            "t9": evidence.get("t9_final_closure", {}),
        },
        ensure_ascii=False,
    ).lower()

    explicit_t1_probability_requirement = (
        "t1 probability" in downstream_text
        or "t1 probabil" in downstream_text
        or "t1 calibrated probability" in downstream_text
        or "t1 calibration required" in downstream_text
    )

    explicit_t1_confidence_requirement = (
        "t1 confidence" in downstream_text
        or "t1 calibrated confidence" in downstream_text
    )

    explicit_t1_threshold_requirement = (
        "t1 threshold required" in downstream_text
        or "t1 probability threshold" in downstream_text
    )

    calibration_requirement = (
        explicit_t1_probability_requirement
        or explicit_t1_confidence_requirement
        or explicit_t1_threshold_requirement
    )

    if missing:
        status = "PARTIAL"
        decision = "NOT_DETERMINED"
    elif calibration_requirement:
        status = "PASS"
        decision = "CALIBRATION_REQUIREMENT_IDENTIFIED"
    else:
        status = "PASS"
        decision = "NO_DOWNSTREAM_T1_CALIBRATION_REQUIREMENT_IDENTIFIED"

    result = {
        "operation": "A-OP-002",
        "title": "T1 Calibration Requirement Reconciliation",
        "status": status,
        "read_only": True,
        "model_modified": False,
        "retraining_performed": False,
        "threshold_optimization_performed": False,
        "locked_test_reused": False,
        "files_expected": len(FILES),
        "files_readable": readable,
        "missing_files": missing,
        "t1_closure": {
            "probability_language_present": t1_probability_language,
            "calibration_language_present": t1_calibration_language,
        },
        "downstream_requirement_checks": {
            "explicit_t1_probability_requirement": (
                explicit_t1_probability_requirement
            ),
            "explicit_t1_confidence_requirement": (
                explicit_t1_confidence_requirement
            ),
            "explicit_t1_threshold_requirement": (
                explicit_t1_threshold_requirement
            ),
        },
        "decision": decision,
        "calibration_not_performed": True,
        "calibration_authorization": (
            "NOT_AUTHORIZED_BY_THIS_OPERATION"
        ),
        "evidence": evidence,
    }

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("=" * 66)
    print("A-OP-002 — T1 CALIBRATION REQUIREMENT RECONCILIATION")
    print("=" * 66)
    print(f"Expected files       : {len(FILES)}")
    print(f"Readable files       : {readable}")
    print(f"Missing files        : {len(missing)}")
    print(
        "T1 probability req   : "
        f"{explicit_t1_probability_requirement}"
    )
    print(
        "T1 confidence req    : "
        f"{explicit_t1_confidence_requirement}"
    )
    print(
        "T1 threshold req     : "
        f"{explicit_t1_threshold_requirement}"
    )
    print(f"Decision             : {decision}")
    print("Calibration performed: False")
    print(f"Output               : {OUTPUT_PATH}")
    print("=" * 66)
    print(f"RESULT: {status}")
    print("=" * 66)


if __name__ == "__main__":
    main()