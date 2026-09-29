from pathlib import Path
import sys

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
RUNTIME_DIR = PROJECT_ROOT / "modeling" / "FMP" / "runtime"

sys.path.insert(0, str(RUNTIME_DIR))

from ticket_pipeline import TicketPipeline
from ticket_explanation import TicketExplanation


DEMO_TICKETS = [
    {
        "ticket_id": "DEMO-001",
        "creation_time": "2026-09-27T08:00:00",
        "creator": "user_001",
        "creator_detail": "employee",
        "summary": "VPN connection fails after password reset",
        "description": (
            "After resetting my corporate password, the VPN disconnects "
            "and I cannot reconnect to the company network."
        ),
    },
    {
        "ticket_id": "DEMO-002",
        "creation_time": "2026-09-27T08:05:00",
        "creator": "user_002",
        "creator_detail": "employee",
        "summary": "Laptop does not boot",
        "description": (
            "The company laptop does not boot after being powered on. "
            "The screen remains blank."
        ),
    },
    {
        "ticket_id": "DEMO-003",
        "creation_time": "2026-09-27T08:10:00",
        "creator": "user_003",
        "creator_detail": "employee",
        "summary": "Account locked after several login attempts",
        "description": (
            "My corporate account is locked and I cannot sign in "
            "to internal applications."
        ),
    },
    {
        "ticket_id": "DEMO-004",
        "creation_time": "2026-09-27T08:15:00",
        "creator": "user_004",
        "creator_detail": "employee",
        "summary": "Outlook is not working",
        "description": (
            "Outlook fails to open correctly and I cannot access "
            "my corporate mailbox."
        ),
    },
    {
        "ticket_id": "DEMO-005",
        "creation_time": "2026-09-27T08:20:00",
        "creator": "user_005",
        "creator_detail": "employee",
        "summary": "Application crashes during startup",
        "description": (
            "The business application crashes immediately after "
            "I try to launch it."
        ),
    },
    {
        "ticket_id": "DEMO-006",
        "creation_time": "2026-09-27T08:25:00",
        "creator": "user_006",
        "creator_detail": "employee",
        "summary": "Cannot access network folder",
        "description": (
            "I cannot open the shared network folder used by "
            "our team."
        ),
    },
    {
        "ticket_id": "DEMO-007",
        "creation_time": "2026-09-27T08:30:00",
        "creator": "user_007",
        "creator_detail": "employee",
        "summary": "General IT support request",
        "description": (
            "I am having a general IT issue and need help "
            "identifying the problem."
        ),
    },
]


def print_separator():
    print("=" * 88)


def main():
    print_separator()
    print("H-RUN-026-OP-003 — HUMAN-READABLE TICKET EXPLANATION DEMO")
    print_separator()
    print()

    print("Loading frozen TicketPipeline...")
    pipeline = TicketPipeline()
    print("Pipeline load: PASS")
    print()

    explainer = TicketExplanation()

    failures = 0

    for ticket in DEMO_TICKETS:
        print_separator()

        try:
            result = pipeline.predict(ticket)
            explanation = explainer.explain(result)

            print(explanation)

        except Exception as exc:
            failures += 1
            print(f"TICKET: {ticket['ticket_id']}")
            print("STATUS: FAILED")
            print(f"ERROR: {type(exc).__name__}: {exc}")

        print()

    print_separator()
    print("DEMO SUMMARY")
    print_separator()
    print(f"Tickets processed: {len(DEMO_TICKETS)}")
    print(f"Failures: {failures}")

    if failures == 0:
        print("FINAL STATUS: PASS_WITH_LIMITATIONS")
    else:
        print("FINAL STATUS: FAIL")


if __name__ == "__main__":
    main()