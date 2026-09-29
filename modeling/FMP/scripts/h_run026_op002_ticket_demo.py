from pathlib import Path
import sys


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


def main():
    print("=" * 78)
    print("H-RUN-026-OP-002 — ACTUAL TICKET DEMONSTRATION")
    print("=" * 78)
    print(f"Runtime: {DEPLOY_RUNTIME}")
    print(f"Tickets: {len(TICKETS)}")

    pipeline = TicketPipeline()

    print("\nPIPELINE LOAD: PASS")

    results = []

    for ticket in TICKETS:
        result = pipeline.predict(ticket)
        results.append(result)

        final = result["final"]
        tasks = result["tasks"]

        print("\n" + "=" * 78)
        print(f"TICKET: {ticket['ticket_id']}")
        print("=" * 78)

        print(f"Summary   : {ticket['summary']}")
        print(f"T1 Category : {final.get('category')}")
        print(f"T2 Priority : {final.get('priority')}")
        print(f"T3 Severity : {final.get('severity')}")

        t4 = tasks.get("T4", {})
        t4_results = t4.get("results", [])

        print(f"T4 Related tickets: {len(t4_results)}")

        for item in t4_results[:5]:
            print(
                f"   - {item.get('id')} | "
                f"distance={item.get('distance')} | "
                f"{item.get('summary')}"
            )

        t5 = tasks.get("T5", {})
        print(
            f"T5 Duplicate evidence: "
            f"{t5.get('duplicate_evidence')}"
        )

        t6 = tasks.get("T6", {})
        print(
            f"T6 Status: {t6.get('status')}"
        )

        if t6.get("reason"):
            print(f"   T6 reason: {t6.get('reason')}")

        t7 = tasks.get("T7", {})
        print(
            f"T7 Resolution median: "
            f"{t7.get('median_seconds')} sec"
        )
        print(
            f"T7 Temporal support: "
            f"{t7.get('temporal_support')}"
        )

        print(f"T8 Evidence: {final.get('evidence_state')}")
        print(f"T10 Action: {final.get('action')}")
        print(f"T11 Lifecycle: {final.get('lifecycle')}")

        warnings = tasks.get("T10", {}).get("warnings", [])

        if warnings:
            print("Warnings:")
            for warning in warnings:
                print(f"   - {warning}")

    print("\n" + "=" * 78)
    print("FINAL DEMO INTEGRITY")
    print("=" * 78)

    integrity_failures = []

    for result in results:
        integrity = result.get("integrity", {})

        for key, value in integrity.items():
            if value not in (False, "NO", "NOT_PERFORMED"):
                integrity_failures.append(
                    (result.get("ticket", {}).get("ticket_id"), key, value)
                )

    print(
        "Integrity:",
        "PASS" if not integrity_failures else "FAIL"
    )

    print(
        "Tickets successfully processed:",
        len(results),
        "/",
        len(TICKETS)
    )

    print(
        "Overall:",
        "PASS_WITH_LIMITATIONS"
        if not integrity_failures and len(results) == len(TICKETS)
        else "FAIL"
    )

    print("=" * 78)


if __name__ == "__main__":
    main()