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
    / "e_op003_t5_task_policy_feasibility_audit.json"
)

T5_CLOSURE = (
    PROJECT_ROOT
    / "modeling/T5/metrics/t5_mod011_final_closure.json"
)


KEYWORDS = [
    "calibrat",
    "probability",
    "threshold",
    "validation",
    "development",
    "locked",
    "test",
    "precision",
    "recall",
    "f1",
    "brier",
    "log loss",
    "average precision",
    "roc",
    "human",
    "review",
    "automation",
    "operational",
    "policy",
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


def find_values(
    value: Any,
    keywords: list[str],
    path: str = "",
) -> list[dict[str, Any]]:
    results = []

    if isinstance(value, dict):
        for key, child in value.items():
            child_path = (
                f"{path}.{key}"
                if path
                else str(key)
            )

            key_lower = str(key).lower()

            if any(
                keyword.lower() in key_lower
                for keyword in keywords
            ):
                results.append(
                    {
                        "path": child_path,
                        "value": child,
                    }
                )

            results.extend(
                find_values(
                    child,
                    keywords,
                    child_path,
                )
            )

    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"

            results.extend(
                find_values(
                    child,
                    keywords,
                    child_path,
                )
            )

    return results


def main() -> None:
    METRICS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not T5_CLOSURE.exists():
        result = {
            "operation": "E-OP-003",
            "status": "BLOCKED",
            "reason": "Authoritative T5 closure not found",
            "path": str(T5_CLOSURE),
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

        print("=" * 68)
        print("E-OP-003 — T5 TASK-SPECIFIC POLICY FEASIBILITY AUDIT")
        print("=" * 68)
        print(f"T5 closure : {T5_CLOSURE}")
        print("RESULT     : BLOCKED — T5 closure not found")
        print("=" * 68)

        return

    try:
        t5_data = load_json(T5_CLOSURE)
    except Exception as exc:
        result = {
            "operation": "E-OP-003",
            "status": "BLOCKED",
            "reason": (
                f"{type(exc).__name__}: {exc}"
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

        print("=" * 68)
        print("E-OP-003 — T5 TASK-SPECIFIC POLICY FEASIBILITY AUDIT")
        print("=" * 68)
        print(
            "RESULT     : BLOCKED — T5 closure unreadable"
        )
        print("=" * 68)

        return

    text = flatten(t5_data).lower()

    keyword_presence = {
        keyword: keyword.lower() in text
        for keyword in KEYWORDS
    }

    relevant_fields = find_values(
        t5_data,
        KEYWORDS,
    )

    # Explicit evidence states already known from the T5 closure
    # are checked conservatively.
    descriptive_threshold_evidence = (
        "threshold .5 descriptive only" in text
        or "threshold 0.5 descriptive only" in text
        or "descriptive only" in text
    )

    operational_threshold_evidence = (
        "operational threshold" in text
        or "production threshold" in text
        or "validated threshold" in text
    )

    human_review_evidence = (
        "human review" in text
        or "human_review" in text
    )

    automation_evidence = (
        "automation" in text
        or "automated decision" in text
    )

    locked_test_evidence = (
        "locked test" in text
        or "locked evaluation" in text
        or "test set" in text
    )

    calibration_evidence = (
        "calibrat" in text
        and (
            "sigmoid" in text
            or "isotonic" in text
            or "brier" in text
            or "log loss" in text
        )
    )

    # Feasibility means only that there is enough task-specific
    # evidence to justify a separate policy investigation.
    #
    # It does NOT mean a policy is validated.
    policy_investigation_feasible = (
        calibration_evidence
        and not operational_threshold_evidence
        and not automation_evidence
    )

    if policy_investigation_feasible:
        feasibility = "TASK_SPECIFIC_POLICY_INVESTIGATION_JUSTIFIED"
    else:
        feasibility = "TASK_SPECIFIC_POLICY_NOT_ESTABLISHED"

    result = {
        "operation": "E-OP-003",
        "title": "T5 Task-Specific Policy Feasibility Audit",
        "status": "PASS",
        "read_only": True,
        "model_modified": False,
        "retraining_performed": False,
        "threshold_selection_performed": False,
        "threshold_optimization_performed": False,
        "locked_test_reused_for_selection": False,
        "source": str(T5_CLOSURE),
        "keyword_presence": keyword_presence,
        "relevant_fields": relevant_fields,
        "evidence_checks": {
            "calibration_evidence": calibration_evidence,
            "descriptive_threshold_evidence": (
                descriptive_threshold_evidence
            ),
            "operational_threshold_evidence": (
                operational_threshold_evidence
            ),
            "human_review_evidence": (
                human_review_evidence
            ),
            "automation_evidence": (
                automation_evidence
            ),
            "locked_test_evidence": (
                locked_test_evidence
            ),
        },
        "feasibility": feasibility,
        "interpretation": {
            "calibration_does_not_equal_policy_validation": True,
            "descriptive_threshold_does_not_equal_operational_threshold": True,
            "this_operation_does_not_select_a_threshold": True,
            "this_operation_does_not_authorize_automation": True,
            "this_operation_does_not_authorize_human_review_boundary": True,
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

    print("=" * 68)
    print("E-OP-003 — T5 TASK-SPECIFIC POLICY FEASIBILITY AUDIT")
    print("=" * 68)
    print("Source              : T5 final closure")
    print(
        f"Calibration evidence: {calibration_evidence}"
    )
    print(
        f"Descriptive .5      : {descriptive_threshold_evidence}"
    )
    print(
        f"Operational threshold: "
        f"{operational_threshold_evidence}"
    )
    print(
        f"Human-review evidence: "
        f"{human_review_evidence}"
    )
    print(
        f"Automation evidence : "
        f"{automation_evidence}"
    )
    print(
        f"Locked-test evidence: "
        f"{locked_test_evidence}"
    )
    print()
    print(f"Feasibility         : {feasibility}")
    print("Threshold selected  : False")
    print("Threshold optimized : False")
    print("Locked test reused  : False")
    print("Model modified      : False")
    print(
        f"Output              : {OUTPUT_PATH}"
    )
    print("=" * 68)
    print("RESULT: PASS — T5 feasibility audit completed")
    print("=" * 68)


if __name__ == "__main__":
    main()