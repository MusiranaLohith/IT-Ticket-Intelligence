from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

METRICS_DIR = PROJECT_ROOT / "modeling/FMP/metrics"

OUTPUT_PATH = (
    METRICS_DIR
    / "e_op001_policy_evidence_inventory.json"
)


TARGETS = {
    "T1": [
        PROJECT_ROOT / "modeling/T1/analysis/t1_final_closure.json",
        PROJECT_ROOT / "modeling/T1/analysis/t1_it_support_3model_compare.json",
    ],
    "T2": [
        PROJECT_ROOT
        / "modeling/T2/metrics/t2_final_closure.json",
    ],
    "T3": [
        PROJECT_ROOT
        / "modeling/T3/metrics/t3_final_closure.json",
    ],
    "T4": [
        PROJECT_ROOT
        / "modeling/T4/results/t4_mod013_closure.json",
    ],
    "T5": [
        PROJECT_ROOT
        / "modeling/T5/metrics/t5_mod011_final_closure.json",
    ],
    "T6": [
        PROJECT_ROOT
        / "modeling/T6/metrics/t6_final_closure.json",
    ],
    "T7": [
        PROJECT_ROOT
        / "modeling/T7/metrics/t7_mod012_final_closure.json",
    ],
    "T8": [
        PROJECT_ROOT
        / "modeling/T8/mod036/op026/"
        / "t8_mod036_op026_decision_engine_validation.json",
    ],
    "T9": [
        PROJECT_ROOT
        / "modeling/T9/mod037/"
        / "t9_mod037_op015_final_integrated_closure.json",
    ],
}


T10_SEARCH_ROOTS = [
    PROJECT_ROOT / "modeling/T10",
    PROJECT_ROOT / "modeling/FMP/metrics",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def flatten(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(
            f"{flatten(k)} {flatten(v)}"
            for k, v in value.items()
        )

    if isinstance(value, list):
        return " ".join(flatten(v) for v in value)

    return str(value)


def find_json_files(root: Path) -> list[Path]:
    if not root.exists():
        return []

    if root.is_file() and root.suffix.lower() == ".json":
        return [root]

    if root.is_dir():
        return sorted(root.rglob("*.json"))

    return []


def collect_target_evidence(
    name: str,
    paths: list[Path],
) -> dict[str, Any]:

    records = []

    for path in paths:
        record = {
            "path": str(path),
            "exists": path.exists(),
            "readable": False,
        }

        if not path.exists():
            records.append(record)
            continue

        try:
            data = load_json(path)
            text = flatten(data).lower()

            record["readable"] = True
            record["text_length"] = len(text)

            terms = [
                "probability",
                "confidence",
                "threshold",
                "ranking",
                "retrieval",
                "calibration",
                "review",
                "automation",
                "defer",
                "risk",
                "evidence",
                "decision",
            ]

            record["policy_relevant_terms"] = {
                term: term in text
                for term in terms
            }

        except Exception as exc:
            record["error"] = (
                f"{type(exc).__name__}: {exc}"
            )

        records.append(record)

    return {
        "task": name,
        "records": records,
    }


def main() -> None:
    METRICS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    task_evidence = {}

    for task, paths in TARGETS.items():
        task_evidence[task] = collect_target_evidence(
            task,
            paths,
        )

    # Discover T10 evidence without assuming a single filename.
    t10_files = []

    for root in T10_SEARCH_ROOTS:
        t10_files.extend(find_json_files(root))

    t10_files = list(dict.fromkeys(t10_files))

    t10_records = []

    for path in t10_files:
        try:
            data = load_json(path)
            text = flatten(data).lower()

            relevant_terms = {
                term: term in text
                for term in [
                    "automation",
                    "human_review",
                    "review",
                    "defer",
                    "threshold",
                    "universal_threshold",
                    "universal_confidence",
                    "universal_risk",
                    "not_established",
                    "not_created",
                    "policy",
                ]
            }

            t10_records.append(
                {
                    "path": str(path),
                    "readable": True,
                    "policy_relevant_terms": relevant_terms,
                }
            )

        except Exception as exc:
            t10_records.append(
                {
                    "path": str(path),
                    "readable": False,
                    "error": (
                        f"{type(exc).__name__}: {exc}"
                    ),
                }
            )

    result = {
        "operation": "E-OP-001",
        "title": "Policy-Relevant Evidence Inventory",
        "status": "PASS",
        "read_only": True,
        "model_modified": False,
        "retraining_performed": False,
        "threshold_selection_performed": False,
        "threshold_optimization_performed": False,
        "locked_test_reused": False,
        "universal_confidence_created": False,
        "universal_risk_created": False,
        "synthetic_fusion_target_created": False,
        "task_evidence": task_evidence,
        "t10_evidence": {
            "files_discovered": len(t10_records),
            "records": t10_records,
        },
        "policy_boundary": {
            "automation": "NOT_ESTABLISHED",
            "human_review": "NOT_ESTABLISHED",
            "universal_threshold": "NOT_ESTABLISHED",
            "universal_confidence": "NOT_CREATED",
            "universal_risk": "NOT_CREATED",
        },
        "interpretation": (
            "This operation inventories policy-relevant evidence only. "
            "It does not establish an operational policy or threshold."
        ),
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

    readable_task_files = 0
    expected_task_files = 0

    for task_data in task_evidence.values():
        for record in task_data["records"]:
            expected_task_files += 1
            if record.get("readable") is True:
                readable_task_files += 1

    t10_readable = sum(
        1
        for record in t10_records
        if record.get("readable") is True
    )

    print("=" * 66)
    print("E-OP-001 — POLICY-RELEVANT EVIDENCE INVENTORY")
    print("=" * 66)
    print(
        f"T1-T9 target files : "
        f"{readable_task_files}/{expected_task_files} readable"
    )
    print(
        f"T10 JSON discovered: "
        f"{len(t10_records)}"
    )
    print(
        f"T10 JSON readable  : "
        f"{t10_readable}"
    )
    print("Automation         : NOT_ESTABLISHED")
    print("Human review       : NOT_ESTABLISHED")
    print("Universal threshold: NOT_ESTABLISHED")
    print("Universal confidence: NOT_CREATED")
    print("Universal risk     : NOT_CREATED")
    print("Threshold selection: False")
    print("Threshold optimize : False")
    print("Locked test reused : False")
    print(f"Output             : {OUTPUT_PATH}")
    print("=" * 66)
    print("RESULT: PASS — evidence inventory completed")
    print("=" * 66)


if __name__ == "__main__":
    main()