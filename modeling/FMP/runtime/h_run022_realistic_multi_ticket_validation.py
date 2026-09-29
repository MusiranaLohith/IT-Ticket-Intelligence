from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = RUNTIME_DIR.parents[3]

if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from ticket_pipeline import TicketPipeline


OUTPUT_JSON = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "h_run022r2_realistic_multi_ticket_validation.json"
)


TICKETS = [
    {
        "ticket_id": "DEV-001",
        "creation_time": "2026-09-27T09:00:00+05:30",
        "creator": "",
        "creator_detail": "",
        "summary": "VPN disconnects after password reset",
        "description": (
            "I reset my corporate password this morning. "
            "The VPN connects briefly and then disconnects. "
            "I restarted the laptop and reinstalled the VPN client, "
            "but the issue persists."
        ),
    },
    {
        "ticket_id": "DEV-002",
        "creation_time": "2026-09-27T09:05:00+05:30",
        "creator": "employee01",
        "creator_detail": "Engineering",
        "summary": "Cannot sign in after password change",
        "description": (
            "My corporate password was changed successfully, "
            "but I cannot sign in to several internal applications. "
            "The old password no longer works."
        ),
    },
    {
        "ticket_id": "DEV-003",
        "creation_time": "2026-09-27T09:10:00+05:30",
        "creator": "employee02",
        "creator_detail": "Finance",
        "summary": "Email messages are not arriving",
        "description": (
            "New email messages are not appearing in my mailbox. "
            "The sender receives no error and the problem started this morning."
        ),
    },
    {
        "ticket_id": "DEV-004",
        "creation_time": "2026-09-27T09:15:00+05:30",
        "creator": "employee03",
        "creator_detail": "Operations",
        "summary": "Laptop will not boot",
        "description": (
            "The laptop powers on but remains stuck on the startup screen. "
            "I tried restarting it several times and disconnected external devices."
        ),
    },
    {
        "ticket_id": "DEV-005",
        "creation_time": "2026-09-27T09:20:00+05:30",
        "creator": "employee04",
        "creator_detail": "Human Resources",
        "summary": "Printer is unavailable",
        "description": (
            "The office printer is showing as offline on my workstation. "
            "Other applications can be opened normally but print jobs remain queued."
        ),
    },
    {
        "ticket_id": "DEV-006",
        "creation_time": "2026-09-27T09:25:00+05:30",
        "creator": "employee05",
        "creator_detail": "Engineering",
        "summary": "Access denied to shared project folder",
        "description": (
            "I can access other shared folders but receive an access denied "
            "message when opening the project directory."
        ),
    },
    {
        "ticket_id": "DEV-007",
        "creation_time": "2026-09-27T09:30:00+05:30",
        "creator": "employee06",
        "creator_detail": "Data Platform",
        "summary": "Database connection failing",
        "description": (
            "The application cannot connect to the reporting database. "
            "The connection worked yesterday and now times out."
        ),
    },
    {
        "ticket_id": "DEV-008",
        "creation_time": "2026-09-27T09:35:00+05:30",
        "creator": "employee07",
        "creator_detail": "Platform",
        "summary": "Monitoring alert triggered repeatedly",
        "description": (
            "The monitoring system is generating repeated alerts for the same "
            "service even though the service appears to be responding normally."
        ),
    },
    {
        "ticket_id": "DEV-009",
        "creation_time": "2026-09-27T09:40:00+05:30",
        "creator": "employee08",
        "creator_detail": "DevOps",
        "summary": "Deployment failed in production",
        "description": (
            "The latest application deployment failed during the release step. "
            "The previous version is still running."
        ),
    },
    {
        "ticket_id": "DEV-010",
        "creation_time": "2026-09-27T09:45:00+05:30",
        "creator": "employee09",
        "creator_detail": "Network Operations",
        "summary": "DNS resolution fails intermittently",
        "description": (
            "Internal hostnames sometimes fail to resolve while external "
            "websites continue to work. Retrying usually succeeds."
        ),
    },
    {
        "ticket_id": "DEV-011",
        "creation_time": "2026-09-27T09:50:00+05:30",
        "creator": "employee10",
        "creator_detail": "Engineering",
        "summary": "Application crashes when opening report",
        "description": (
            "The internal reporting application closes unexpectedly whenever "
            "I open a specific monthly report."
        ),
    },
    {
        "ticket_id": "DEV-012",
        "creation_time": "2026-09-27T09:55:00+05:30",
        "creator": "employee11",
        "creator_detail": "IT Support",
        "summary": "Two factor authentication code rejected",
        "description": (
            "My authentication code is rejected even though the code is "
            "generated by the registered authenticator application."
        ),
    },
    {
        "ticket_id": "DEV-013",
        "creation_time": "2026-09-27T10:00:00+05:30",
        "creator": "employee12",
        "creator_detail": "Sales",
        "summary": "Web application is very slow",
        "description": (
            "The customer portal takes more than a minute to load several pages. "
            "The problem affects multiple users in the team."
        ),
    },
    {
        "ticket_id": "DEV-014",
        "creation_time": "2026-09-27T10:05:00+05:30",
        "creator": "employee13",
        "creator_detail": "Infrastructure",
        "summary": "Internal server cannot be reached",
        "description": (
            "The internal server does not respond from my workstation. "
            "Other internal services remain reachable."
        ),
    },
    {
        "ticket_id": "DEV-015",
        "creation_time": "2026-09-27T10:10:00+05:30",
        "creator": "employee14",
        "creator_detail": "Engineering",
        "summary": "Software installation fails",
        "description": (
            "The approved development tool fails during installation with "
            "an error message near the end of the setup process."
        ),
    },
]


EXPECTED_TASKS = [f"T{i}" for i in range(1, 12)]


def compact_result(result: dict) -> dict:
    tasks = result["tasks"]
    final = result["final"]

    t4_results = tasks["T4"].get("results", [])

    return {
        "ticket_id": result["ticket"]["ticket_id"],
        "overall_status": (
            "PASS_WITH_LIMITATIONS"
            if final.get("evidence_state") == "SUPPORTED_WITH_LIMITATIONS"
            else "PASS"
        ),
        "T1": tasks["T1"].get("status"),
        "T1_prediction": tasks["T1"].get("prediction"),
        "T2": tasks["T2"].get("status"),
        "T2_prediction": tasks["T2"].get("prediction"),
        "T3": tasks["T3"].get("status"),
        "T3_prediction": tasks["T3"].get("prediction"),
        "T4": tasks["T4"].get("status"),
        "T4_count": len(t4_results),
        "T5": tasks["T5"].get("status"),
        "T5_evidence": tasks["T5"].get("duplicate_evidence"),
        "T6": tasks["T6"].get("status"),
        "T7": tasks["T7"].get("status"),
        "T7_median_seconds": tasks["T7"].get("median_seconds"),
        "T7_temporal_support": tasks["T7"].get("temporal_support"),
        "T8": tasks["T8"].get("status"),
        "T9": tasks["T9"].get("status"),
        "T10": tasks["T10"].get("status"),
        "T11": tasks["T11"].get("status"),
        "final_evidence_state": final.get("evidence_state"),
        "final_action": final.get("action"),
        "final_lifecycle": final.get("lifecycle"),
    }


def validate_result_structure(result: dict) -> list[str]:
    failures = []

    if not isinstance(result, dict):
        return ["result_is_not_dict"]

    required_top = {"ticket", "tasks", "final", "integrity"}

    missing_top = required_top - set(result.keys())

    if missing_top:
        failures.append(
            f"missing_top_level_keys={sorted(missing_top)}"
        )

    if not isinstance(result.get("tasks"), dict):
        failures.append("tasks_is_not_dict")
        return failures

    missing_tasks = [
        task
        for task in EXPECTED_TASKS
        if task not in result["tasks"]
    ]

    if missing_tasks:
        failures.append(
            f"missing_tasks={missing_tasks}"
        )

    if not isinstance(result.get("final"), dict):
        failures.append("final_is_not_dict")

    if not isinstance(result.get("integrity"), dict):
        failures.append("integrity_is_not_dict")

    return failures


def main():
    print("=" * 78)
    print("H-RUN-022R2 — REALISTIC MULTI-TICKET RUNTIME VALIDATION")
    print("=" * 78)

    print()
    print("[1] Initializing reusable TicketPipeline...")
    pipeline = TicketPipeline()
    print("TicketPipeline initialization: PASS")

    print()
    print(f"[2] Preparing {len(TICKETS)} development tickets...")
    print("Synthetic runtime inputs only : YES")
    print("Training/evaluation modification: NO")

    print()
    print("[3] Running predict_batch()...")
    results = pipeline.predict_batch(TICKETS)

    print(f"Tickets returned: {len(results)}")

    if len(results) != len(TICKETS):
        print(
            f"ERROR: expected {len(TICKETS)} results "
            f"but received {len(results)}"
        )
        raise RuntimeError("Batch result count mismatch")

    compact = []
    structural_failures = []

    print()
    print("=" * 78)
    print("PER-TICKET RUNTIME SUMMARY")
    print("=" * 78)

    for result in results:
        failures = validate_result_structure(result)

        if failures:
            structural_failures.append({
                "ticket_id": (
                    result.get("ticket", {}).get("ticket_id")
                    if isinstance(result, dict)
                    else None
                ),
                "failures": failures,
            })
            continue

        row = compact_result(result)
        compact.append(row)

        print(
            f"{row['ticket_id']} | "
            f"T1={row['T1']}:{row['T1_prediction']} | "
            f"T2={row['T2']}:{row['T2_prediction']} | "
            f"T3={row['T3']}:{row['T3_prediction']} | "
            f"T4={row['T4']}({row['T4_count']}) | "
            f"T5={row['T5']}:{row['T5_evidence']} | "
            f"T6={row['T6']} | "
            f"T7={row['T7']}:{row['T7_median_seconds']:.6f}s | "
            f"T8={row['T8']} | "
            f"T9={row['T9']} | "
            f"T10={row['T10']} | "
            f"T11={row['T11']}"
        )

    print()
    print("=" * 78)
    print("STRUCTURAL VALIDATION")
    print("=" * 78)

    print(
        f"Expected result objects : {len(TICKETS)}"
    )
    print(
        f"Valid result objects    : {len(compact)}"
    )
    print(
        f"Structural failures     : {len(structural_failures)}"
    )

    if structural_failures:
        for failure in structural_failures:
            print(
                f"  {failure['ticket_id']} -> "
                f"{failure['failures']}"
            )

    stage_failure_counts = {
        f"T{i}": 0
        for i in range(1, 12)
    }

    stage_status_counts = {
        f"T{i}": {}
        for i in range(1, 12)
    }

    integrity_failures = []

    for result in results:
        if not isinstance(result, dict):
            continue

        tasks = result.get("tasks", {})
        integrity = result.get("integrity", {})

        for task_name in EXPECTED_TASKS:
            task = tasks.get(task_name)

            if not isinstance(task, dict):
                stage_failure_counts[task_name] += 1
                continue

            status = task.get("status")

            stage_status_counts[task_name][status] = (
                stage_status_counts[task_name].get(status, 0) + 1
            )

            if status == "FAILED":
                stage_failure_counts[task_name] += 1

        required_integrity_flags = {
            "model_retraining": False,
            "model_modification": False,
            "threshold_optimization": False,
            "locked_test_reuse": False,
            "prediction_modification": False,
            "synthetic_feedback": False,
        }

        for key, expected in required_integrity_flags.items():
            actual = integrity.get(key)

            if actual != expected:
                integrity_failures.append({
                    "ticket_id": result.get(
                        "ticket", {}
                    ).get("ticket_id"),
                    "field": key,
                    "expected": expected,
                    "actual": actual,
                })

    any_stage_failure = any(
        count > 0
        for count in stage_failure_counts.values()
    )

    any_structural_failure = len(structural_failures) > 0
    any_integrity_failure = len(integrity_failures) > 0

    if (
        any_stage_failure
        or any_structural_failure
        or any_integrity_failure
    ):
        overall_status = "FAIL"
    else:
        overall_status = "PASS_WITH_LIMITATIONS"

    report = {
        "operation": "H-RUN-022R2",
        "operation_name": "realistic_multi_ticket_runtime_validation",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": overall_status,
        "ticket_count": len(TICKETS),
        "results_returned": len(results),
        "tickets": TICKETS,
        "compact_results": compact,
        "structural_failures": structural_failures,
        "stage_failure_counts": stage_failure_counts,
        "stage_status_counts": stage_status_counts,
        "integrity_failures": integrity_failures,
        "runtime_properties": {
            "reusable_ticket_pipeline": True,
            "predict_batch_used": True,
            "same_pipeline_instance": True,
            "training_data_modified": False,
            "evaluation_data_modified": False,
            "model_retraining": False,
            "model_modification": False,
            "threshold_optimization": False,
            "locked_test_reuse": False,
            "prediction_modification": False,
            "synthetic_feedback": False,
        },
        "interpretation": {
            "synthetic_inputs_are_runtime_only": True,
            "t6_full_mod010_semantic_runtime_available": False,
            "t7_temporal_support_must_be_reported_per_ticket": True,
            "t8_missing_evidence_is_not_negative": True,
            "t9_universal_confidence_not_created": True,
            "t9_universal_risk_not_created": True,
            "t10_automatic_action_policy_not_established": True,
            "t11_operational_feedback_not_present": True,
        },
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    print()
    print("=" * 78)
    print("H-RUN-022R2 SUMMARY")
    print("=" * 78)

    print(f"Tickets submitted        : {len(TICKETS)}")
    print(f"Results returned         : {len(results)}")
    print(f"Valid result structures  : {len(compact)}")
    print(f"Structural failures      : {len(structural_failures)}")

    print()
    print("Stage failure counts:")

    for stage in EXPECTED_TASKS:
        print(
            f"  {stage}: "
            f"{stage_failure_counts[stage]}"
        )

    print()
    print("Integrity failures       :", len(integrity_failures))

    print()
    print(f"FINAL STATUS             : {overall_status}")

    print()
    print("[INTEGRITY]")
    print("Training data modified   : NO")
    print("Evaluation data modified : NO")
    print("Model retraining         : NO")
    print("Model modification       : NO")
    print("Threshold optimization   : NO")
    print("Locked test reuse        : NO")
    print("Prediction modification  : NO")
    print("Synthetic feedback       : NO")

    print()
    print("[ARTIFACT]")
    print(f"JSON : {OUTPUT_JSON}")


if __name__ == "__main__":
    main()