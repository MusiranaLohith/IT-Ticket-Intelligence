from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T1_ROOT = PROJECT_ROOT / "modeling" / "T1"

ARTIFACTS = [
    T1_ROOT / "contracts" / "t1_contract.json",
    T1_ROOT / "splits" / "t1_split_report.json",
    T1_ROOT / "analysis" / "t1_it_support_3model_compare.json",
    T1_ROOT / "analysis" / "t1_it_support_char_svm_analysis.json",
    T1_ROOT / "analysis" / "t1_it_support_eval_groups.json",
    T1_ROOT / "analysis" / "t1_it_support_group_eval.json",
    T1_ROOT / "analysis" / "t1_it_support_model_subset_compare.json",
    T1_ROOT / "analysis" / "t1_it_support_split_check.json",
    T1_ROOT / "analysis" / "t1_it_support_subset_analysis.json",
    T1_ROOT / "analysis" / "t1_it_support_svm_errors.json",
    T1_ROOT / "baselines" / "t1_it_support_char_svm_report.json",
    T1_ROOT / "baselines" / "t1_it_support_char_svm.joblib",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def summarize_value(value: Any, depth: int = 0) -> str:
    """
    Produce a compact structural description without dumping large JSON files.
    """
    if depth > 2:
        return type(value).__name__

    if isinstance(value, dict):
        keys = list(value.keys())
        preview = keys[:20]
        suffix = " ..." if len(keys) > 20 else ""
        return f"dict(keys={preview}{suffix}, n_keys={len(keys)})"

    if isinstance(value, list):
        if not value:
            return "list(len=0)"

        first_type = type(value[0]).__name__
        return f"list(len={len(value)}, first_type={first_type})"

    return f"{type(value).__name__}: {repr(value)[:200]}"


def print_dict_structure(
    obj: Any,
    prefix: str = "",
    max_depth: int = 2,
) -> None:
    """
    Print useful structural information from JSON objects without
    dumping entire reports.
    """
    if not isinstance(obj, dict):
        print(f"{prefix}{summarize_value(obj)}")
        return

    for key, value in obj.items():
        print(f"{prefix}{key}: {summarize_value(value)}")

        if (
            isinstance(value, dict)
            and prefix.count("  ") < max_depth
        ):
            print_dict_structure(
                value,
                prefix=prefix + "  ",
                max_depth=max_depth,
            )


def main() -> None:
    print("=" * 72)
    print("FMP-01 / T1 EVIDENCE INVENTORY & RECONCILIATION")
    print("=" * 72)

    print()
    print(f"Project root: {PROJECT_ROOT}")
    print(f"T1 root:      {T1_ROOT}")

    if not PROJECT_ROOT.exists():
        raise FileNotFoundError(
            f"Project root does not exist: {PROJECT_ROOT}"
        )

    if not T1_ROOT.exists():
        raise FileNotFoundError(
            f"T1 root does not exist: {T1_ROOT}"
        )

    print()
    print("-" * 72)
    print("1. REQUIRED ARTIFACT EXISTENCE")
    print("-" * 72)

    missing = []
    existing = []

    for path in ARTIFACTS:
        relative = path.relative_to(PROJECT_ROOT)

        if path.exists():
            size = path.stat().st_size
            existing.append(path)
            print(f"[FOUND]   {relative}    size={size} bytes")
        else:
            missing.append(path)
            print(f"[MISSING] {relative}")

    print()
    print(f"Found : {len(existing)}")
    print(f"Missing: {len(missing)}")

    if missing:
        print()
        print("Missing artifacts:")
        for path in missing:
            print(f"  - {path.relative_to(PROJECT_ROOT)}")

    print()
    print("-" * 72)
    print("2. JSON REPORT STRUCTURES")
    print("-" * 72)

    json_artifacts = [
        path for path in ARTIFACTS
        if path.suffix.lower() == ".json"
    ]

    json_results = {}

    for path in json_artifacts:
        relative = path.relative_to(PROJECT_ROOT)

        print()
        print(f"[JSON] {relative}")

        if not path.exists():
            print("  STATUS: MISSING")
            continue

        try:
            obj = load_json(path)
            json_results[str(relative)] = obj

            print(f"  top-level: {summarize_value(obj)}")

            if isinstance(obj, dict):
                print("  keys / structure:")
                print_dict_structure(obj, prefix="    ", max_depth=1)

        except Exception as exc:
            print(f"  STATUS: READ_ERROR")
            print(f"  ERROR: {type(exc).__name__}: {exc}")

    print()
    print("-" * 72)
    print("3. TARGETED T1 EVIDENCE CHECKS")
    print("-" * 72)

    # The checks below intentionally look for common evidence fields without
    # assuming a particular exact schema. They report where such fields exist.
    target_terms = [
        "accuracy",
        "macro_f1",
        "weighted_f1",
        "f1",
        "evaluation",
        "eval",
        "group",
        "repeat",
        "single",
        "calibration",
        "probability",
        "confidence",
        "threshold",
        "error",
        "subset",
        "model",
        "split",
        "leakage",
    ]

    for relative_str, obj in json_results.items():
        if not isinstance(obj, dict):
            continue

        matches = []

        for key in obj.keys():
            key_lower = str(key).lower()

            matched_terms = [
                term for term in target_terms
                if term in key_lower
            ]

            if matched_terms:
                matches.append(
                    f"{key} <- {', '.join(matched_terms)}"
                )

        if matches:
            print()
            print(relative_str)
            for match in matches:
                print(f"  {match}")

    print()
    print("-" * 72)
    print("4. MODEL ARTIFACTS")
    print("-" * 72)

    model_paths = [
        T1_ROOT / "baselines" / "t1_it_support_char_svm.joblib",
        T1_ROOT / "baselines" / "t1_it_support_svm.joblib",
        T1_ROOT / "baselines" / "t1_it_support_baseline.joblib",
    ]

    for path in model_paths:
        if path.exists():
            print(
                f"[FOUND] {path.relative_to(PROJECT_ROOT)}"
                f"    size={path.stat().st_size} bytes"
            )
        else:
            print(
                f"[ABSENT] {path.relative_to(PROJECT_ROOT)}"
            )

    print()
    print("-" * 72)
    print("5. FMP-01 INITIAL RECONCILIATION STATUS")
    print("-" * 72)

    if missing:
        print("STATUS: BLOCKED")
        print("Reason: one or more required evidence artifacts are missing.")
        print(
            "No architecture decision or retraining should be performed "
            "from this inventory."
        )
    else:
        print("STATUS: READY_FOR_EVIDENCE_REVIEW")
        print(
            "All required FMP-01 inventory artifacts are present."
        )
        print(
            "This operation does NOT freeze the architecture and does "
            "NOT perform retraining."
        )

    print()
    print("=" * 72)
    print("END OF FMP-01 / T1 EVIDENCE INVENTORY")
    print("=" * 72)


if __name__ == "__main__":
    main()