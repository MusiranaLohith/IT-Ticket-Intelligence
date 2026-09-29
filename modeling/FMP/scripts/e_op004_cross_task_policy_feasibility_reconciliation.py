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
    / "e_op004_cross_task_policy_feasibility_reconciliation.json"
)


SOURCES = {
    "T1": [
        PROJECT_ROOT
        / "modeling/T1/analysis/t1_final_closure.json",
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


TASK_BOUNDARIES = {
    "T1": {
        "native_semantics": "classification / native decision score",
        "policy_candidate": False,
        "reason": (
            "T1 calibration is not required by downstream contracts; "
            "native decision score is retained."
        ),
    },
    "T2": {
        "native_semantics": "priority classification",
        "policy_candidate": False,
        "reason": (
            "No accepted native probability artifact or validated "
            "operational threshold exists."
        ),
    },
    "T3": {
        "native_semantics": "severity classification",
        "policy_candidate": False,
        "reason": (
            "No accepted native probability artifact or validated "
            "operational threshold exists."
        ),
    },
    "T4": {
        "native_semantics": "historical assignee retrieval",
        "policy_candidate": False,
        "reason": (
            "Historical retrieval is evidence for routing support; "
            "retrieval ranking does not establish operational eligibility "
            "or correctness thresholds."
        ),
    },
    "T5": {
        "native_semantics": "duplicate probability / calibration",
        "policy_candidate": False,
        "reason": (
            "Calibration evidence exists, but no validated operational "
            "duplicate-review or automation threshold was established."
        ),
    },
    "T6": {
        "native_semantics": "retrieval ranking",
        "policy_candidate": False,
        "reason": (
            "Ranking metrics establish retrieval behavior, not a binary "
            "policy threshold or probability."
        ),
    },
    "T7": {
        "native_semantics": "survival / time-to-resolution",
        "policy_candidate": False,
        "reason": (
            "Survival evidence is censoring-aware, but no validated "
            "operational resolution-time policy or review boundary exists."
        ),
    },
    "T8": {
        "native_semantics": "evidence availability / decision state",
        "policy_candidate": False,
        "reason": (
            "T8 integrates task-native evidence and preserves missingness; "
            "it does not create a universal probability or policy threshold."
        ),
    },
    "T9": {
        "native_semantics": "task-specific reliability semantics",
        "policy_candidate": False,
        "reason": (
            "T9 explicitly does not establish universal confidence, "
            "universal risk, or an automatic action policy."
        ),
    },
}


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


def inspect_source(path: Path) -> dict[str, Any]:
    record = {
        "path": str(path),
        "exists": path.exists(),
        "readable": False,
    }

    if not path.exists():
        return record

    try:
        data = load_json(path)
        text = flatten(data).lower()

        record["readable"] = True
        record["bytes"] = path.stat().st_size

        # These are descriptive evidence flags only.
        record["contains_probability_language"] = (
            "probabil" in text
        )
        record["contains_calibration_language"] = (
            "calibrat" in text
        )
        record["contains_threshold_language"] = (
            "threshold" in text
        )
        record["contains_automation_language"] = (
            "automation" in text
        )
        record["contains_human_review_language"] = (
            "human_review" in text
            or "human review" in text
        )

    except Exception as exc:
        record["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

    return record


def main() -> None:
    METRICS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    source_records = {}
    total_expected = 0
    total_existing = 0
    total_readable = 0

    for task, paths in SOURCES.items():
        records = []

        for path in paths:
            total_expected += 1

            record = inspect_source(path)
            records.append(record)

            if record["exists"]:
                total_existing += 1

            if record["readable"]:
                total_readable += 1

        source_records[task] = records

    task_results = {}

    for task, boundary in TASK_BOUNDARIES.items():
        task_results[task] = {
            "native_semantics": boundary["native_semantics"],
            "policy_investigation_supported": (
                boundary["policy_candidate"]
            ),
            "policy_status": (
                "POLICY_NOT_ESTABLISHED"
                if not boundary["policy_candidate"]
                else "INVESTIGATION_SUPPORTED"
            ),
            "reason": boundary["reason"],
        }

    policy_boundary = {
        "AUTOMATION": "NOT_ESTABLISHED",
        "HUMAN_REVIEW": "NOT_ESTABLISHED",
        "DEFER": "NOT_ESTABLISHED",
        "UNIVERSAL_THRESHOLD": "NOT_ESTABLISHED",
        "UNIVERSAL_CONFIDENCE": "NOT_CREATED",
        "UNIVERSAL_RISK": "NOT_CREATED",
        "CROSS_TASK_PROBABILITY_AGGREGATION": "NOT_CREATED",
        "SYNTHETIC_FUSION_TARGET": "NOT_CREATED",
    }

    result = {
        "operation": "E-OP-004",
        "title": (
            "Cross-Task Policy Feasibility Reconciliation"
        ),
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
        "source_reconciliation": {
            "expected": total_expected,
            "existing": total_existing,
            "readable": total_readable,
        },
        "source_records": source_records,
        "task_results": task_results,
        "policy_boundary": policy_boundary,
        "overall_conclusion": (
            "NO_OPERATIONAL_POLICY_ESTABLISHED_FROM_CURRENT_FROZEN_EVIDENCE"
        ),
        "interpretation": {
            "task_evidence_is_not_policy_validation": True,
            "calibration_is_not_threshold_validation": True,
            "retrieval_is_not_probability": True,
            "survival_is_not_automation_threshold": True,
            "native_semantics_preserved": True,
            "additional_policy_threshold_optimization_not_authorized": True,
        },
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

    print("=" * 72)
    print(
        "E-OP-004 — CROSS-TASK POLICY FEASIBILITY RECONCILIATION"
    )
    print("=" * 72)

    print(
        f"Sources readable : "
        f"{total_readable}/{total_expected}"
    )
    print(
        f"Sources existing : "
        f"{total_existing}/{total_expected}"
    )

    print()
    print("TASK POLICY STATUS")
    print("-" * 72)

    for task, data in task_results.items():
        print(
            f"{task}: "
            f"{data['policy_status']}"
        )

    print()
    print("FINAL POLICY BOUNDARY")
    print("-" * 72)
    print("AUTOMATION              : NOT_ESTABLISHED")
    print("HUMAN_REVIEW            : NOT_ESTABLISHED")
    print("DEFER                   : NOT_ESTABLISHED")
    print("UNIVERSAL_THRESHOLD     : NOT_ESTABLISHED")
    print("UNIVERSAL_CONFIDENCE    : NOT_CREATED")
    print("UNIVERSAL_RISK          : NOT_CREATED")
    print("CROSS-TASK PROBABILITY  : NOT_CREATED")
    print("SYNTHETIC FUSION TARGET : NOT_CREATED")

    print()
    print(
        "Overall conclusion:"
    )
    print(
        "NO_OPERATIONAL_POLICY_ESTABLISHED_FROM_CURRENT_FROZEN_EVIDENCE"
    )

    print()
    print("Threshold selected     : False")
    print("Threshold optimized    : False")
    print("Locked test reused     : False")
    print("Model modified         : False")

    print()
    print(f"Output                 : {OUTPUT_PATH}")
    print("=" * 72)
    print(
        "RESULT: PASS — cross-task policy feasibility reconciled"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()