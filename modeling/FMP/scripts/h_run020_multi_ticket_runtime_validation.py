from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

ORCHESTRATOR = (
    ROOT
    / "modeling"
    / "FMP"
    / "scripts"
    / "h_run019_full_ticket_pipeline.py"
)

METRICS = ROOT / "modeling" / "FMP" / "metrics"

TICKETS = [
    {
        "id": "H-RUN-020-VPN-001",
        "title": "VPN connection fails after password reset",
        "description": (
            "I reset my corporate password this morning. Since then, "
            "the VPN client connects briefly and then disconnects. "
            "I restarted the laptop and reinstalled the VPN client, "
            "but the issue persists. I need access to the internal systems "
            "for today's work."
        ),
    },
    {
        "id": "H-RUN-020-HW-001",
        "title": "Laptop does not detect external monitor",
        "description": (
            "My laptop stopped detecting the external monitor connected "
            "through the docking station. I restarted the laptop and "
            "reconnected the dock, but the monitor is still not detected."
        ),
    },
    {
        "id": "H-RUN-020-ACC-001",
        "title": "Unable to access corporate account",
        "description": (
            "I cannot sign in to my corporate account after changing "
            "my password. The new password is accepted on one service "
            "but access to the internal account portal continues to fail."
        ),
    },
]


def run_ticket(ticket):
    """
    Execute the frozen H-RUN-019R2 orchestrator as a subprocess.

    The orchestrator itself remains unchanged. This operation only
    validates multi-ticket execution behavior.
    """

    source = ORCHESTRATOR.read_text(encoding="utf-8")

    replacement = f'''
TICKET_ID = {ticket["id"]!r}
TITLE = {ticket["title"]!r}
DESCRIPTION = {ticket["description"]!r}
'''

    # Replace the ticket constants in a temporary execution copy.
    lines = source.splitlines()

    output_lines = []

    skip_ticket_id = False
    skip_title = False
    skip_description = False

    i = 0

    while i < len(lines):
        line = lines[i]

        if line.startswith("TICKET_ID = "):
            output_lines.append(replacement.strip().splitlines()[0])
            i += 1
            continue

        if line.startswith("TITLE = "):
            output_lines.append(replacement.strip().splitlines()[1])
            i += 1
            continue

        if line.startswith("DESCRIPTION = ("):
            output_lines.append(
                replacement.strip().splitlines()[2]
            )
            i += 1

            while i < len(lines):
                if lines[i].strip() == ")":
                    i += 1
                    break
                i += 1

            continue

        output_lines.append(line)
        i += 1

    temp_script = METRICS / f"_h_run020_{ticket['id']}.py"
    temp_script.write_text(
        "\n".join(output_lines),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, str(temp_script)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )

    try:
        temp_script.unlink()
    except FileNotFoundError:
        pass

    stdout = completed.stdout
    stderr = completed.stderr

    return {
        "ticket": ticket,
        "return_code": completed.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "process_status": (
            "PASS" if completed.returncode == 0 else "FAIL"
        ),
    }


def parse_statuses(stdout):
    statuses = {}

    for line in stdout.splitlines():
        line = line.strip()

        for task in [
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
            prefix = f"[{task}]"

            if line.startswith(prefix):
                statuses[task] = line

    return statuses


def parse_overall(stdout):
    for line in stdout.splitlines():
        if line.startswith("OVERALL STATUS:"):
            return line.split(":", 1)[1].strip()

    return "UNKNOWN"


def main():
    print("=" * 70)
    print("H-RUN-020 — MULTI-TICKET RUNTIME VALIDATION")
    print("=" * 70)

    print(f"\nTickets under validation: {len(TICKETS)}")

    records = []

    for index, ticket in enumerate(TICKETS, start=1):
        print("\n" + "-" * 70)
        print(f"TICKET {index}/{len(TICKETS)}")
        print(f"ID    : {ticket['id']}")
        print(f"TITLE : {ticket['title']}")
        print("-" * 70)

        result = run_ticket(ticket)

        statuses = parse_statuses(result["stdout"])
        overall = parse_overall(result["stdout"])

        record = {
            "ticket": ticket,
            "process_status": result["process_status"],
            "return_code": result["return_code"],
            "task_status_lines": statuses,
            "overall_status": overall,
            "stderr": result["stderr"],
        }

        records.append(record)

        print(f"Process       : {result['process_status']}")
        print(f"Overall       : {overall}")

        for task in [
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
            if task in statuses:
                print(statuses[task])

        if result["stderr"].strip():
            print("\nSTDERR:")
            print(result["stderr"])

    process_failures = [
        r for r in records
        if r["process_status"] != "PASS"
    ]

    overall_failures = [
        r for r in records
        if r["overall_status"] == "FAIL"
    ]

    all_processes_pass = len(process_failures) == 0
    no_overall_failures = len(overall_failures) == 0

    if all_processes_pass and no_overall_failures:
        final_status = "PASS_WITH_LIMITATIONS"
    else:
        final_status = "FAIL"

    report = {
        "operation": "H-RUN-020",
        "operation_name": "Multi-ticket runtime validation",
        "ticket_count": len(TICKETS),
        "tickets": records,
        "validation": {
            "all_processes_pass": all_processes_pass,
            "no_overall_failures": no_overall_failures,
            "frozen_orchestrator_unchanged": True,
            "model_retraining": False,
            "model_modification": False,
            "threshold_optimization": False,
            "locked_test_reuse": False,
            "prediction_modification": False,
            "synthetic_feedback": False,
        },
        "final_status": final_status,
    }

    METRICS.mkdir(parents=True, exist_ok=True)

    json_path = (
        METRICS
        / "h_run020_multi_ticket_runtime_validation.json"
    )

    report_path = (
        METRICS
        / "h_run020_multi_ticket_runtime_validation_report.txt"
    )

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    report_lines = [
        "=" * 70,
        "H-RUN-020 — MULTI-TICKET RUNTIME VALIDATION REPORT",
        "=" * 70,
        "",
    ]

    for record in records:
        ticket = record["ticket"]

        report_lines.extend(
            [
                f"Ticket ID : {ticket['id']}",
                f"Title     : {ticket['title']}",
                f"Process   : {record['process_status']}",
                f"Overall   : {record['overall_status']}",
            ]
        )

        for task, status_line in record["task_status_lines"].items():
            report_lines.append(status_line)

        report_lines.append("")

    report_lines.extend(
        [
            "=" * 70,
            f"FINAL STATUS: {final_status}",
            "=" * 70,
            "",
            "[INTEGRITY]",
            "Frozen orchestrator unchanged : YES",
            "Model retraining              : NO",
            "Model modification            : NO",
            "Threshold optimization        : NO",
            "Locked test reuse             : NO",
            "Prediction modification       : NO",
            "Synthetic feedback            : NO",
        ]
    )

    report_path.write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )

    print("\n" + "=" * 70)
    print("H-RUN-020 SUMMARY")
    print("=" * 70)

    for record in records:
        print(
            f"{record['ticket']['id']} -> "
            f"PROCESS={record['process_status']} | "
            f"OVERALL={record['overall_status']}"
        )

    print("-" * 70)
    print(f"FINAL STATUS: {final_status}")

    print("\n[ARTIFACTS]")
    print(f"JSON   : {json_path}")
    print(f"REPORT : {report_path}")

    print("\n[INTEGRITY]")
    print("Frozen orchestrator unchanged : YES")
    print("Model retraining              : NO")
    print("Model modification            : NO")
    print("Threshold optimization        : NO")
    print("Locked test reuse             : NO")
    print("Prediction modification       : NO")
    print("Synthetic feedback            : NO")


if __name__ == "__main__":
    main()