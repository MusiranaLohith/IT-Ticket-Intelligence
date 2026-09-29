from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
DEPLOY_RUNTIME = PROJECT_ROOT / "modeling" / "FMP" / "deployment" / "runtime"

sys.path.insert(0, str(DEPLOY_RUNTIME))

from ticket_pipeline import TicketPipeline


TICKETS = [
    {
        "ticket_id": "DEMO-001",
        "creation_time": "2026-09-27 09:00:00",
        "creator": "user001",
        "creator_detail": "employee",
        "summary": "VPN connection fails after password reset",
        "description": (
            "I reset my corporate password this morning. "
            "Since then the VPN connects briefly and immediately disconnects."
        ),
    },
    {
        "ticket_id": "DEMO-002",
        "creation_time": "2026-09-27 09:05:00",
        "creator": "user002",
        "creator_detail": "employee",
        "summary": "Laptop will not boot",
        "description": (
            "My company laptop suddenly stopped starting. "
            "The power light comes on but Windows does not load."
        ),
    },
    {
        "ticket_id": "DEMO-003",
        "creation_time": "2026-09-27 09:10:00",
        "creator": "user003",
        "creator_detail": "employee",
        "summary": "Account locked after too many password attempts",
        "description": (
            "My account is locked after several incorrect password attempts. "
            "I cannot sign in to the corporate network."
        ),
    },
    {
        "ticket_id": "DEMO-004",
        "creation_time": "2026-09-27 09:15:00",
        "creator": "user004",
        "creator_detail": "employee",
        "summary": "Outlook is not sending emails",
        "description": (
            "Outlook opens normally but messages remain stuck in the outbox "
            "and are not being sent."
        ),
    },
    {
        "ticket_id": "DEMO-005",
        "creation_time": "2026-09-27 09:20:00",
        "creator": "user005",
        "creator_detail": "employee",
        "summary": "Application crashes when opening report",
        "description": (
            "The reporting application closes whenever I try to open "
            "the monthly report."
        ),
    },
    {
        "ticket_id": "DEMO-006",
        "creation_time": "2026-09-27 09:25:00",
        "creator": "user006",
        "creator_detail": "employee",
        "summary": "Cannot access shared network folder",
        "description": (
            "I receive an access denied message when trying to open "
            "the department shared folder."
        ),
    },
    {
        "ticket_id": "DEMO-007",
        "creation_time": "2026-09-27 09:30:00",
        "creator": "user007",
        "creator_detail": "employee",
        "summary": "Need help with a general IT issue",
        "description": (
            "I am having an IT problem and need assistance. "
            "I am not sure which support team should handle it."
        ),
    },
]


def compact(value, max_len=180):
    if value is None:
        return None

    text = str(value).replace("\n", " ")
    if len(text) <= max_len:
        return text

    return text[: max_len - 3] + "..."


def print_ticket_result(result):
    ticket_id = result.get("ticket_id", "UNKNOWN")

    print()
    print("=" * 78)
    print(f"TICKET: {ticket_id}")
    print("=" * 78)

    for stage in [
        "t1",
        "t2",
        "t3",
        "t4",
        "t5",
        "t6",
        "t7",
        "t8",
        "t9",
        "t10",
        "t11",
    ]:
        value = result.get(stage)

        if value is None:
            print(f"{stage.upper():<5}: <not returned>")
            continue

        if isinstance(value, dict):
            print(f"{stage.upper():<5}:")
            for key, item in value.items():
                if isinstance(item, (dict, list)):
                    item_text = compact(json.dumps(item, ensure_ascii=False))
                else:
                    item_text = compact(item)

                print(f"       {key}: {item_text}")
        else:
            print(f"{stage.upper():<5}: {compact(value)}")


def main():
    print("=" * 78)
    print("H-RUN-026-OP-002 — ACTUAL TICKET RUNTIME DEMO")
    print("=" * 78)
    print(f"Runtime: {DEPLOY_RUNTIME}")
    print(f"Tickets: {len(TICKETS)}")
    print()

    pipeline = TicketPipeline()

    print("PIPELINE LOAD: PASS")
    print()

    results = []

    for ticket in TICKETS:
        result = pipeline.predict(ticket)
        results.append(result)
        print_ticket_result(result)

    print()
    print("=" * 78)
    print("DEMO SUMMARY")
    print("=" * 78)

    print(f"Tickets submitted : {len(TICKETS)}")
    print(f"Results returned  : {len(results)}")

    required_stages = [
        "t1",
        "t2",
        "t3",
        "t4",
        "t5",
        "t6",
        "t7",
        "t8",
        "t9",
        "t10",
        "t11",
    ]

    stage_failures = []

    for result in results:
        missing = [
            stage
            for stage in required_stages
            if stage not in result
        ]

        if missing:
            stage_failures.append(
                {
                    "ticket_id": result.get("ticket_id"),
                    "missing": missing,
                }
            )

    print(f"Stage completeness: {'PASS' if not stage_failures else 'FAIL'}")

    if stage_failures:
        print("Stage failures:")
        print(json.dumps(stage_failures, indent=2))

    print()
    print("INTEGRITY CHECKS")
    print("----------------")

    integrity_keys = [
        "model_modified",
        "retraining_performed",
        "locked_test_access",
    ]

    integrity_failures = []

    for result in results:
        for key in integrity_keys:
            if result.get(key) not in (None, False, "NO", "NOT_PERFORMED"):
                integrity_failures.append(
                    {
                        "ticket_id": result.get("ticket_id"),
                        key: result.get(key),
                    }
                )

    print(
        "Integrity status:",
        "PASS" if not integrity_failures else "FAIL"
    )

    if integrity_failures:
        print(json.dumps(integrity_failures, indent=2))

    overall = (
        "PASS_WITH_LIMITATIONS"
        if not stage_failures and not integrity_failures
        else "FAIL"
    )

    print()
    print(f"OVERALL DEMO STATUS: {overall}")
    print("=" * 78)


if __name__ == "__main__":
    main()