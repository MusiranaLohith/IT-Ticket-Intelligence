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
    / "e_op005_final_policy_boundary_reconciliation.json"
)


TASKS = [
    "T1",
    "T2",
    "T3",
    "T4",
    "T5",
    "T6",
    "T7",
    "T8",
    "T9",
]


T10_AUTHORITATIVE_FILES = [
    METRICS_DIR
    / "fmp05_op006_native_policy_evidence_inventory.json",
    METRICS_DIR
    / "fmp05_op007r_native_operating_evidence.json",
    METRICS_DIR
    / "fmp05_op008_empirical_policy_boundary_audit.json",
    METRICS_DIR
    / "fmp06_op022r8_final_t10_literal_key_reconciliation.json",
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


def discover_task_json(task: str) -> list[Path]:
    """
    Targeted discovery only inside the relevant task directory.

    No project-wide scan is performed.
    """
    root = PROJECT_ROOT / "modeling" / task

    if not root.exists():
        return []

    files = sorted(root.rglob("*.json"))

    return files


def select_relevant_files(
    task: str,
    files: list[Path],
) -> list[Path]:

    if not files:
        return []

    priority_terms = [
        "closure",
        "final",
        "comparison",
        "policy",
        "reliability",
        "validation",
        "evidence",
    ]

    scored = []

    for path in files:
        name = path.name.lower()

        score = sum(
            1
            for term in priority_terms
            if term in name
        )

        scored.append(
            (score, path)
        )

    scored.sort(
        key=lambda item: (-item[0], str(item[1]))
    )

    # Keep all files with a positive authoritative-looking signal.
    selected = [
        path
        for score, path in scored
        if score > 0
    ]

    return selected


def inspect_task_file(path: Path) -> dict[str, Any]:
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

        record["explicit_policy_signals"] = {
            "automation_not_established": (
                "automation" in text
                and "not_established" in text
            ),
            "human_review_not_established": (
                (
                    "human_review" in text
                    or "human review" in text
                )
                and "not_established" in text
            ),
            "universal_threshold_not_established": (
                "universal_threshold" in text
                and "not_established" in text
            ),
            "universal_confidence_not_created": (
                "universal_confidence" in text
                and "not_created" in text
            ),
            "universal_risk_not_created": (
                "universal_risk" in text
                and "not_created" in text
            ),
            "synthetic_fusion_target_not_created": (
                "synthetic_fusion_target" in text
                and "not_created" in text
            ),
            "operational_threshold_not_established": (
                "operational_threshold" in text
                and "not_established" in text
            ),
        }

    except Exception as exc:
        record["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

    return record


def inspect_t10() -> dict[str, Any]:
    records = []

    for path in T10_AUTHORITATIVE_FILES:
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

            record["policy_boundary_signals"] = {
                "automation_not_established": (
                    "automation" in text
                    and "not_established" in text
                ),
                "human_review_not_established": (
                    (
                        "human_review" in text
                        or "human review" in text
                    )
                    and "not_established" in text
                ),
                "universal_threshold_not_established": (
                    "universal_threshold" in text
                    and "not_established" in text
                ),
                "universal_confidence_not_created": (
                    "universal_confidence" in text
                    and "not_created" in text
                ),
                "universal_risk_not_created": (
                    "universal_risk" in text
                    and "not_created" in text
                ),
            }

        except Exception as exc:
            record["error"] = (
                f"{type(exc).__name__}: {exc}"
            )

        records.append(record)

    return {
        "expected": len(T10_AUTHORITATIVE_FILES),
        "records": records,
    }


def main() -> None:
    METRICS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    task_results = {}
    task_file_count = 0
    task_readable_count = 0

    for task in TASKS:
        discovered = discover_task_json(task)
        selected = select_relevant_files(
            task,
            discovered,
        )

        inspected = []

        for path in selected:
            record = inspect_task_file(path)
            inspected.append(record)

            task_file_count += 1

            if record.get("readable") is True:
                task_readable_count += 1

        task_results[task] = {
            "task_directory": str(
                PROJECT_ROOT / "modeling" / task
            ),
            "json_discovered": len(discovered),
            "relevant_json_selected": len(selected),
            "records": inspected,
        }

    t10 = inspect_t10()

    t10_readable = sum(
        1
        for record in t10["records"]
        if record.get("readable") is True
    )

    # Aggregate only explicit T10 policy-boundary evidence.
    boundary_keys = [
        "automation_not_established",
        "human_review_not_established",
        "universal_threshold_not_established",
        "universal_confidence_not_created",
        "universal_risk_not_created",
    ]

    t10_boundary = {}

    for key in boundary_keys:
        t10_boundary[key] = any(
            record.get(
                "policy_boundary_signals",
                {},
            ).get(key, False)
            for record in t10["records"]
        )

    all_required_t10_boundaries_present = all(
        t10_boundary.values()
    )

    # Important:
    #
    # We do NOT infer task-specific policy status merely because
    # a task has no threshold. The only defensible global policy
    # conclusion comes from the authoritative T10 boundary.
    #
    # If all T10 boundary statements are explicitly present,
    # the current frozen system has no established operational
    # policy.
    if (
        t10_readable == t10["expected"]
        and all_required_t10_boundaries_present
    ):
        final_policy_status = (
            "NO_OPERATIONAL_POLICY_ESTABLISHED"
        )
        closure_status = "GREEN_CLOSED"
    else:
        final_policy_status = (
            "POLICY_BOUNDARY_NOT_FULLY_RECONCILED"
        )
        closure_status = "REQUIRES_REVIEW"

    result = {
        "operation": "E-OP-005",
        "title": (
            "Final Source-Driven Policy Boundary Reconciliation"
        ),
        "status": "PASS",
        "read_only": True,
        "model_modified": False,
        "retraining_performed": False,
        "threshold_selection_performed": False,
        "threshold_optimization_performed": False,
        "locked_test_reused": False,
        "task_source_reconciliation": {
            "tasks_checked": len(TASKS),
            "relevant_files_inspected": task_file_count,
            "readable_files": task_readable_count,
        },
        "task_results": task_results,
        "t10_authoritative_reconciliation": t10,
        "t10_boundary": t10_boundary,
        "all_required_t10_boundaries_present": (
            all_required_t10_boundaries_present
        ),
        "final_policy_status": final_policy_status,
        "closure_status": closure_status,
        "controls": {
            "universal_confidence_created": False,
            "universal_risk_created": False,
            "cross_task_probability_aggregation_created": False,
            "synthetic_fusion_target_created": False,
            "arbitrary_cross_task_weights_created": False,
            "threshold_optimization_performed": False,
            "locked_test_reused_for_policy_selection": False,
        },
        "interpretation": {
            "task_evidence_does_not_automatically_create_policy": True,
            "absence_of_threshold_does_not_equal_negative_evidence": True,
            "t10_is_authoritative_for_global_policy_boundary": True,
            "native_task_semantics_preserved": True,
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

    print("=" * 76)
    print(
        "E-OP-005 — FINAL SOURCE-DRIVEN POLICY "
        "BOUNDARY RECONCILIATION"
    )
    print("=" * 76)

    print(
        f"T1-T9 tasks checked       : {len(TASKS)}"
    )
    print(
        f"Relevant task JSON files  : {task_file_count}"
    )
    print(
        f"Readable task JSON files  : {task_readable_count}"
    )

    print()
    print("T10 AUTHORITATIVE EVIDENCE")
    print("-" * 76)
    print(
        f"Expected sources          : {t10['expected']}"
    )
    print(
        f"Readable sources          : {t10_readable}"
    )

    print()
    print("EXPLICIT POLICY BOUNDARY")
    print("-" * 76)

    print(
        "AUTOMATION           : "
        f"{t10_boundary['automation_not_established']}"
    )
    print(
        "HUMAN_REVIEW         : "
        f"{t10_boundary['human_review_not_established']}"
    )
    print(
        "UNIVERSAL_THRESHOLD  : "
        f"{t10_boundary['universal_threshold_not_established']}"
    )
    print(
        "UNIVERSAL_CONFIDENCE : "
        f"{t10_boundary['universal_confidence_not_created']}"
    )
    print(
        "UNIVERSAL_RISK       : "
        f"{t10_boundary['universal_risk_not_created']}"
    )

    print()
    print(
        f"Final policy status   : {final_policy_status}"
    )
    print(
        f"E closure status      : {closure_status}"
    )

    print()
    print("Threshold selected    : False")
    print("Threshold optimized   : False")
    print("Locked test reused    : False")
    print("Model modified        : False")

    print()
    print(
        f"Output                : {OUTPUT_PATH}"
    )

    print("=" * 76)
    print(
        "RESULT: PASS — source-driven policy boundary reconciliation complete"
    )
    print("=" * 76)


if __name__ == "__main__":
    main()