from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


RUNTIME_DIR = Path(__file__).resolve().parent


def find_project_root() -> Path:
    for candidate in [RUNTIME_DIR, *RUNTIME_DIR.parents]:
        if (
            (candidate / "modeling").is_dir()
            and (candidate / "modeling" / "T1").is_dir()
            and (candidate / "modeling" / "FMP").is_dir()
        ):
            return candidate

    raise RuntimeError(
        "Could not locate IT-Ticket-Triage-System project root."
    )


PROJECT_ROOT = find_project_root()

if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from ticket_pipeline import TicketPipeline


OUTPUT_JSON = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "h_run024_final_e2e_demonstration.json"
)

OUTPUT_TXT = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "h_run024_final_e2e_demonstration.txt"
)


# ============================================================
# DEVELOPMENT DEMONSTRATION TICKETS
# ============================================================

TICKETS = [
    {
        "ticket_id": "E2E-001",
        "creation_time": "2026-09-27T09:00:00+05:30",
        "creator": "",
        "creator_detail": "",
        "summary": (
            "VPN connection fails after password reset"
        ),
        "description": (
            "I reset my corporate password this morning. "
            "Since then, the VPN client connects briefly and "
            "then disconnects. I restarted the laptop and "
            "reinstalled the VPN client, but the issue persists. "
            "I need access to the internal systems for today's work."
        ),
    },
    {
        "ticket_id": "E2E-002",
        "creation_time": "2026-09-27T09:05:00+05:30",
        "creator": "",
        "creator_detail": "",
        "summary": (
            "Laptop will not connect to external monitor"
        ),
        "description": (
            "The company laptop detects the monitor but the "
            "external display remains black. I tried another "
            "HDMI cable and restarted the laptop. The monitor "
            "works with another computer."
        ),
    },
    {
        "ticket_id": "E2E-003",
        "creation_time": "2026-09-27T09:10:00+05:30",
        "creator": "",
        "creator_detail": "",
        "summary": (
            "Account locked after repeated password attempts"
        ),
        "description": (
            "My corporate account is locked after several "
            "failed password attempts. I cannot sign in to "
            "company applications and need the account restored."
        ),
    },
]


def stage_status(result: dict, task: str):
    task_data = result.get("tasks", {}).get(task, {})

    if isinstance(task_data, dict):
        return task_data.get("status")

    return None


def summarize_result(ticket: dict, result: dict) -> dict:

    tasks = result.get("tasks", {})
    final = result.get("final", {})
    integrity = result.get("integrity", {})

    return {
        "ticket_id": ticket["ticket_id"],

        "T1": {
            "status": stage_status(result, "T1"),
            "output": tasks.get("T1"),
        },

        "T2": {
            "status": stage_status(result, "T2"),
            "output": tasks.get("T2"),
        },

        "T3": {
            "status": stage_status(result, "T3"),
            "output": tasks.get("T3"),
        },

        "T4": {
            "status": stage_status(result, "T4"),
            "output": tasks.get("T4"),
        },

        "T5": {
            "status": stage_status(result, "T5"),
            "output": tasks.get("T5"),
        },

        "T6": {
            "status": stage_status(result, "T6"),
            "output": tasks.get("T6"),
        },

        "T7": {
            "status": stage_status(result, "T7"),
            "output": tasks.get("T7"),
        },

        "T8": {
            "status": stage_status(result, "T8"),
            "output": tasks.get("T8"),
        },

        "T9": {
            "status": stage_status(result, "T9"),
            "output": tasks.get("T9"),
        },

        "T10": {
            "status": stage_status(result, "T10"),
            "output": tasks.get("T10"),
        },

        "T11": {
            "status": stage_status(result, "T11"),
            "output": tasks.get("T11"),
        },

        "final": final,

        "integrity": integrity,
    }


def print_final_ticket_output(final: dict):

    print("FINAL TICKET OUTPUT")
    print(
        f"  Category              : "
        f"{final.get('category')}"
    )

    print(
        f"  Priority              : "
        f"{final.get('priority')}"
    )

    print(
        f"  Severity              : "
        f"{final.get('severity')}"
    )

    print(
        f"  Duplicate evidence    : "
        f"{final.get('duplicate_evidence')}"
    )

    print(
        f"  Related ticket IDs    : "
        f"{final.get('related_ticket_ids')}"
    )

    print(
        f"  Resolution median     : "
        f"{final.get('resolution_median_seconds')} sec"
    )

    print(
        f"  Evidence state        : "
        f"{final.get('evidence_state')}"
    )

    print(
        f"  Action                : "
        f"{final.get('action')}"
    )

    print(
        f"  Lifecycle             : "
        f"{final.get('lifecycle')}"
    )


def main():

    print("=" * 78)
    print("H-RUN-024 — FINAL END-TO-END DEMONSTRATION")
    print("=" * 78)

    print()
    print("Project root:")
    print(f"  {PROJECT_ROOT}")

    print()
    print("Initializing frozen TicketPipeline...")

    pipeline = TicketPipeline()

    print("Pipeline initialization : PASS")

    print()
    print(
        f"Executing {len(TICKETS)} representative development tickets..."
    )

    results = []

    for ticket in TICKETS:

        print()
        print("-" * 78)
        print(f"TICKET {ticket['ticket_id']}")
        print("-" * 78)

        result = pipeline.predict(ticket)

        summary = summarize_result(
            ticket,
            result,
        )

        results.append(summary)

        for task_name in [
            "T1",
            "T2",
            "T3",
            "T4",
            "T5",
            "T6",
            "T7",
            "T8",
            "T9",
            "T10",
            "T11",
        ]:

            print(
                f"{task_name:<4} "
                f"{summary[task_name]['status']}"
            )

        print()

        print_final_ticket_output(
            summary["final"]
        )

    # --------------------------------------------------------
    # STRUCTURAL VALIDATION
    # --------------------------------------------------------

    print()
    print("=" * 78)
    print("STRUCTURAL VALIDATION")
    print("=" * 78)

    expected_tasks = {
        f"T{i}"
        for i in range(1, 12)
    }

    structural_failures = []

    for summary in results:

        actual_tasks = {
            key
            for key in summary
            if key.startswith("T")
            and key[1:].isdigit()
        }

        missing = expected_tasks - actual_tasks

        if missing:
            structural_failures.append(
                {
                    "ticket_id":
                        summary["ticket_id"],
                    "missing_tasks":
                        sorted(missing),
                }
            )

    print(
        "Tickets executed:",
        len(results),
    )

    print(
        "Expected tickets:",
        len(TICKETS),
    )

    print(
        "Structural failures:",
        len(structural_failures),
    )

    # --------------------------------------------------------
    # INTEGRITY VALIDATION
    # --------------------------------------------------------

    integrity_failures = []

    for summary in results:

        integrity = summary["integrity"]

        if not isinstance(
            integrity,
            dict,
        ):
            integrity_failures.append(
                {
                    "ticket_id":
                        summary["ticket_id"],
                    "reason":
                        "missing_integrity_record",
                }
            )
            continue

        for key, value in integrity.items():

            if value is True:
                integrity_failures.append(
                    {
                        "ticket_id":
                            summary["ticket_id"],
                        "field":
                            key,
                        "value":
                            value,
                    }
                )

    print(
        "Integrity failures:",
        len(integrity_failures),
    )

    # --------------------------------------------------------
    # STAGE VALIDATION
    # --------------------------------------------------------

    stage_failures = []

    for summary in results:

        for task_name in [
            "T1",
            "T2",
            "T3",
            "T4",
            "T5",
            "T6",
            "T7",
            "T8",
            "T9",
            "T10",
            "T11",
        ]:

            status = summary[task_name]["status"]

            if status is None:
                stage_failures.append(
                    {
                        "ticket_id":
                            summary["ticket_id"],
                        "task":
                            task_name,
                        "reason":
                            "missing_stage_status",
                    }
                )

    print(
        "Stage-status failures:",
        len(stage_failures),
    )

    # --------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------

    demonstration_pass = (
        len(results) == len(TICKETS)
        and not structural_failures
        and not integrity_failures
        and not stage_failures
    )

    final_status = (
        "PASS_WITH_LIMITATIONS"
        if demonstration_pass
        else "REQUIRES_REVIEW"
    )

    # --------------------------------------------------------
    # MANIFEST
    # --------------------------------------------------------

    manifest = {
        "operation":
            "H-RUN-024",

        "operation_name":
            "final_end_to_end_demonstration",

        "timestamp_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "project_root":
            str(PROJECT_ROOT),

        "runtime_module":
            str(
                RUNTIME_DIR
                / "ticket_pipeline.py"
            ),

        "input_population": {
            "type":
                "development_demonstration_tickets",

            "training":
                False,

            "evaluation":
                False,

            "ticket_count":
                len(TICKETS),

            "tickets":
                TICKETS,
        },

        "results":
            results,

        "validation": {
            "expected_ticket_count":
                len(TICKETS),

            "executed_ticket_count":
                len(results),

            "structural_failures":
                structural_failures,

            "integrity_failures":
                integrity_failures,

            "stage_failures":
                stage_failures,
        },

        "freeze_controls": {
            "model_retraining":
                False,

            "model_modification":
                False,

            "threshold_optimization":
                False,

            "locked_test_reuse":
                False,

            "prediction_modification":
                False,

            "synthetic_feedback":
                False,
        },

        "final_status":
            final_status,

        "known_boundaries": {
            "T6_full_MOD010_new_ticket_semantic_runtime":
                "NOT_AVAILABLE",

            "T7_temporal_support_for_2026_tickets":
                "OUTSIDE_OBSERVED_TRAINING_RANGE",

            "T8_missing_evidence":
                "UNAVAILABLE_IS_NOT_NEGATIVE",

            "T9_universal_confidence":
                "NOT_CREATED",

            "T9_universal_risk":
                "NOT_CREATED",

            "T10_automatic_action_policy":
                "NOT_ESTABLISHED",

            "T11_operational_feedback":
                "NOT_AVAILABLE",
        },
    }

    # --------------------------------------------------------
    # WRITE JSON
    # --------------------------------------------------------

    OUTPUT_JSON.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            manifest,
            f,
            indent=2,
            default=str,
        )

    # --------------------------------------------------------
    # WRITE TEXT REPORT
    # --------------------------------------------------------

    with OUTPUT_TXT.open(
        "w",
        encoding="utf-8",
    ) as f:

        f.write(
            "H-RUN-024 — FINAL END-TO-END DEMONSTRATION\n"
        )

        f.write("=" * 78 + "\n\n")

        f.write(
            f"Project root: {PROJECT_ROOT}\n"
        )

        f.write(
            f"Tickets executed: {len(results)}\n\n"
        )

        for summary in results:

            f.write(
                f"TICKET {summary['ticket_id']}\n"
            )

            f.write("-" * 78 + "\n")

            for task_name in [
                "T1",
                "T2",
                "T3",
                "T4",
                "T5",
                "T6",
                "T7",
                "T8",
                "T9",
                "T10",
                "T11",
            ]:

                f.write(
                    f"{task_name}: "
                    f"{summary[task_name]['status']}\n"
                )

            f.write("\n")

            final = summary["final"]

            f.write("FINAL TICKET OUTPUT\n")

            f.write(
                f"Category: "
                f"{final.get('category')}\n"
            )

            f.write(
                f"Priority: "
                f"{final.get('priority')}\n"
            )

            f.write(
                f"Severity: "
                f"{final.get('severity')}\n"
            )

            f.write(
                f"Duplicate evidence: "
                f"{final.get('duplicate_evidence')}\n"
            )

            f.write(
                f"Related ticket IDs: "
                f"{final.get('related_ticket_ids')}\n"
            )

            f.write(
                f"Resolution median seconds: "
                f"{final.get('resolution_median_seconds')}\n"
            )

            f.write(
                f"Evidence state: "
                f"{final.get('evidence_state')}\n"
            )

            f.write(
                f"Action: "
                f"{final.get('action')}\n"
            )

            f.write(
                f"Lifecycle: "
                f"{final.get('lifecycle')}\n\n"
            )

        f.write("VALIDATION\n")
        f.write("-" * 78 + "\n")

        f.write(
            f"Structural failures: "
            f"{len(structural_failures)}\n"
        )

        f.write(
            f"Integrity failures: "
            f"{len(integrity_failures)}\n"
        )

        f.write(
            f"Stage failures: "
            f"{len(stage_failures)}\n"
        )

        f.write(
            f"FINAL STATUS: "
            f"{final_status}\n"
        )

    # --------------------------------------------------------
    # TERMINAL SUMMARY
    # --------------------------------------------------------

    print()
    print("=" * 78)
    print("H-RUN-024 SUMMARY")
    print("=" * 78)

    print(
        "Tickets executed        :",
        len(results),
    )

    print(
        "Structural failures     :",
        len(structural_failures),
    )

    print(
        "Integrity failures      :",
        len(integrity_failures),
    )

    print(
        "Stage-status failures   :",
        len(stage_failures),
    )

    print()
    print(
        "FINAL STATUS             :",
        final_status,
    )

    print()
    print("[FREEZE CONTROLS]")
    print("Model retraining         : NO")
    print("Model modification       : NO")
    print("Threshold optimization   : NO")
    print("Locked test reuse        : NO")
    print("Prediction modification  : NO")
    print("Synthetic feedback       : NO")

    print()
    print("[ARTIFACTS]")
    print(f"JSON : {OUTPUT_JSON}")
    print(f"TEXT : {OUTPUT_TXT}")


if __name__ == "__main__":
    main()