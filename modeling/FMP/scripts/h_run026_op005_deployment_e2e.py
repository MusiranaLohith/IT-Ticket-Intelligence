from pathlib import Path
import sys

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
DEPLOYMENT_RUNTIME = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "deployment"
    / "runtime"
)

sys.path.insert(0, str(DEPLOYMENT_RUNTIME))

from ticket_pipeline import TicketPipeline
from ticket_explanation import TicketExplanation


DEMO_TICKETS = [
    {
        "ticket_id": "DEPLOY-001",
        "creation_time": "2026-09-27T08:00:00",
        "creator": "user_001",
        "creator_detail": "employee",
        "summary": "VPN connection fails after password reset",
        "description": "After resetting my corporate password, the VPN disconnects and I cannot reconnect to the company network.",
    },
    {
        "ticket_id": "DEPLOY-002",
        "creation_time": "2026-09-27T08:05:00",
        "creator": "user_002",
        "creator_detail": "employee",
        "summary": "Laptop does not boot",
        "description": "The company laptop does not boot after being powered on. The screen remains blank.",
    },
    {
        "ticket_id": "DEPLOY-003",
        "creation_time": "2026-09-27T08:10:00",
        "creator": "user_003",
        "creator_detail": "employee",
        "summary": "Account locked after several login attempts",
        "description": "My corporate account is locked and I cannot sign in to internal applications.",
    },
    {
        "ticket_id": "DEPLOY-004",
        "creation_time": "2026-09-27T08:15:00",
        "creator": "user_004",
        "creator_detail": "employee",
        "summary": "Outlook is not working",
        "description": "Outlook fails to open correctly and I cannot access my corporate mailbox.",
    },
    {
        "ticket_id": "DEPLOY-005",
        "creation_time": "2026-09-27T08:20:00",
        "creator": "user_005",
        "creator_detail": "employee",
        "summary": "Application crashes during startup",
        "description": "The business application crashes immediately after I try to launch it.",
    },
    {
        "ticket_id": "DEPLOY-006",
        "creation_time": "2026-09-27T08:25:00",
        "creator": "user_006",
        "creator_detail": "employee",
        "summary": "Cannot access network folder",
        "description": "I cannot open the shared network folder used by our team.",
    },
    {
        "ticket_id": "DEPLOY-007",
        "creation_time": "2026-09-27T08:30:00",
        "creator": "user_007",
        "creator_detail": "employee",
        "summary": "General IT support request",
        "description": "I am having a general IT issue and need help identifying the problem.",
    },
]


def main():
    print("=" * 88)
    print("H-RUN-026-OP-005 — DEPLOYMENT RUNTIME E2E VALIDATION")
    print("=" * 88)
    print()
    print(f"Deployment runtime: {DEPLOYMENT_RUNTIME}")
    print()

    failures = 0

    print("[1] Loading packaged runtime")

    try:
        pipeline = TicketPipeline()
        explainer = TicketExplanation()
        print("TicketPipeline: PASS")
        print("TicketExplanation: PASS")
    except Exception as exc:
        print(f"Runtime load: FAIL — {type(exc).__name__}: {exc}")
        raise SystemExit(1)

    print()

    print("[2] Executing packaged runtime against 7 tickets")
    print()

    for ticket in DEMO_TICKETS:
        try:
            result = pipeline.predict(ticket)
            explanation = explainer.explain(result)

            tasks = result.get("tasks", {})
            final = result.get("final", {})
            integrity = result.get("integrity", {})

            required_tasks = [
                "T1", "T2", "T3", "T4", "T5",
                "T6", "T7", "T8", "T9", "T10", "T11"
            ]

            missing_tasks = [
                task for task in required_tasks
                if task not in tasks
            ]

            integrity_failures = [
                key for key, value in integrity.items()
                if value is True
            ]

            print("-" * 88)
            print(f"TICKET: {ticket['ticket_id']}")
            print(f"CATEGORY: {final.get('category')}")
            print(f"PRIORITY: {final.get('priority')}")
            print(f"SEVERITY: {final.get('severity')}")
            print(f"EVIDENCE: {final.get('evidence_state')}")
            print(f"ACTION: {final.get('action')}")
            print(f"LIFECYCLE: {final.get('lifecycle')}")
            print(f"TASKS: {len(tasks)}/11")
            print(f"INTEGRITY FAILURES: {len(integrity_failures)}")

            if missing_tasks:
                print(f"STATUS: FAIL — missing tasks {missing_tasks}")
                failures += 1
            elif integrity_failures:
                print(
                    "STATUS: FAIL — integrity flags "
                    f"{integrity_failures}"
                )
                failures += 1
            else:
                print("STATUS: PASS")

            print()
            print("Human-readable explanation:")
            print(explanation)

        except Exception as exc:
            failures += 1
            print("-" * 88)
            print(f"TICKET: {ticket['ticket_id']}")
            print(f"STATUS: FAIL — {type(exc).__name__}: {exc}")

    print()
    print("=" * 88)
    print("DEPLOYMENT E2E SUMMARY")
    print("=" * 88)
    print(f"Tickets processed: {len(DEMO_TICKETS)}")
    print(f"Failures: {failures}")

    if failures == 0:
        print("FINAL STATUS: PASS_WITH_LIMITATIONS")
        print("Packaged deployment runtime executed successfully.")
        print("No production authorization is established.")
    else:
        print("FINAL STATUS: FAIL")


if __name__ == "__main__":
    main()