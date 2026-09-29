from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

SOURCE_SCRIPT = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "scripts"
    / "h_run015_final_ticket_orchestrator.py"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "h_run017r3_multi_ticket_runtime_validation.json"
)


TICKETS = [
    {
        "ticket_id": "H-RUN-017-A",
        "title": "VPN connection fails after password reset",
        "description": (
            "I reset my corporate password this morning. "
            "Since then, the VPN client connects briefly and "
            "then disconnects. I restarted the laptop and "
            "reinstalled the VPN client, but the issue persists. "
            "I need access to the internal systems for today's work."
        ),
    },
    {
        "ticket_id": "H-RUN-017-B",
        "title": "Laptop battery replacement request",
        "description": (
            "The battery in my work laptop is no longer holding "
            "a charge and the machine shuts down shortly after "
            "being unplugged. I need a replacement battery or "
            "another laptop so I can continue working."
        ),
    },
    {
        "ticket_id": "H-RUN-017-C",
        "title": "Unable to access corporate account",
        "description": (
            "I cannot sign in to my corporate account after "
            "changing my password. The login page rejects the "
            "new password even though it was accepted during "
            "the password change. I need access to email and "
            "internal applications."
        ),
    },
]


def fail(message: str) -> None:
    raise RuntimeError(message)


def find_ticket_nodes(
    source_text: str,
) -> tuple[list[ast.Constant], list[ast.Constant]]:

    tree = ast.parse(source_text)

    title_nodes = []
    description_nodes = []

    for node in ast.walk(tree):

        if not isinstance(node, ast.Dict):
            continue

        for key, value in zip(node.keys, node.values):

            if key is None:
                continue

            if not isinstance(key, ast.Constant):
                continue

            if key.value == "title":
                if (
                    isinstance(value, ast.Constant)
                    and isinstance(value.value, str)
                ):
                    title_nodes.append(value)

            elif key.value == "description":
                if (
                    isinstance(value, ast.Constant)
                    and isinstance(value.value, str)
                ):
                    description_nodes.append(value)

    return title_nodes, description_nodes


def line_offsets(
    source_text: str,
) -> list[int]:

    offsets = [0]

    for match in re.finditer(
        r"\n",
        source_text,
    ):
        offsets.append(match.end())

    return offsets


def node_offsets(
    node: ast.Constant,
    offsets: list[int],
) -> tuple[int, int]:

    start = (
        offsets[node.lineno - 1]
        + node.col_offset
    )

    end = (
        offsets[node.end_lineno - 1]
        + node.end_col_offset
    )

    return start, end


def replace_ticket_nodes(
    source_text: str,
    replacements: list[tuple[ast.Constant, str]],
) -> str:

    offsets = line_offsets(source_text)

    edits = []

    for node, new_value in replacements:

        start, end = node_offsets(
            node,
            offsets,
        )

        edits.append(
            (
                start,
                end,
                repr(new_value),
            )
        )

    edits.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    modified = source_text

    for start, end, replacement in edits:

        modified = (
            modified[:start]
            + replacement
            + modified[end:]
        )

    return modified


def prepare_ticket_source(
    source_text: str,
    ticket: dict,
) -> tuple[str, dict]:

    title_nodes, description_nodes = (
        find_ticket_nodes(source_text)
    )

    if len(title_nodes) != 1:
        fail(
            "Expected exactly one literal 'title' entry, "
            f"found {len(title_nodes)}."
        )

    if len(description_nodes) != 1:
        fail(
            "Expected exactly one literal 'description' entry, "
            f"found {len(description_nodes)}."
        )

    original_title = title_nodes[0].value
    original_description = (
        description_nodes[0].value
    )

    modified = replace_ticket_nodes(
        source_text,
        [
            (
                title_nodes[0],
                ticket["title"],
            ),
            (
                description_nodes[0],
                ticket["description"],
            ),
        ],
    )

    return modified, {
        "original_title": original_title,
        "original_description": original_description,
        "title_entries_found": len(title_nodes),
        "description_entries_found": len(
            description_nodes
        ),
    }


def extract_task_blocks(
    stdout: str,
) -> dict[str, list[str]]:

    task_blocks = {}

    current_task = None

    for raw_line in stdout.splitlines():

        line = raw_line.strip()

        header_match = re.fullmatch(
            r"\[(T1|T2|T3|T4|T5|T6|T7|T8|T9|T10|T11)\]",
            line,
        )

        if header_match:
            current_task = header_match.group(1)
            task_blocks[current_task] = []
            continue

        if current_task is not None:
            task_blocks[current_task].append(line)

    return task_blocks


def compact_task_block(
    lines: list[str],
) -> str:

    meaningful = [
        line
        for line in lines
        if line
    ]

    return " | ".join(
        meaningful
    )


def classify_status(
    task_blocks: dict[str, list[str]],
) -> str:

    required_tasks = [
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
    ]

    if any(
        task not in task_blocks
        for task in required_tasks
    ):
        return "MISSING_TASK_BLOCK"

    blocks = {
        task: compact_task_block(
            task_blocks[task]
        )
        for task in required_tasks
    }

    if any(
        "error" in block.lower()
        or "failed" in block.lower()
        for block in blocks.values()
    ):
        return "RUNTIME_ERROR"

    expected_fragments = {
        "T1": "EXECUTED",
        "T2": "EXECUTED",
        "T3": "EXECUTED",
        "T4": "EXECUTED",
        "T5": "EXECUTED",
        "T6": "PARTIAL_NATIVE_RUNTIME",
        "T7": "EXECUTED_WITH_SUPPORT_LIMITATION",
        "T8": "BOUNDARY_ENVELOPE",
        "T9": "BOUNDARY_ENVELOPE",
        "T10": "automation",
        "T11": "SPECIFICATION_ONLY",
    }

    missing = []

    for task, fragment in expected_fragments.items():

        if fragment.lower() not in blocks[task].lower():
            missing.append(task)

    if not missing:
        return "PASS"

    return "REQUIRES_REVIEW"


def run_ticket(
    ticket: dict,
    source_text: str,
    temp_dir: Path,
) -> dict:

    modified_source, binding = (
        prepare_ticket_source(
            source_text,
            ticket,
        )
    )

    temp_script = (
        temp_dir
        / f"{ticket['ticket_id']}_orchestrator.py"
    )

    temp_script.write_text(
        modified_source,
        encoding="utf-8",
    )

    syntax = subprocess.run(
        [
            sys.executable,
            "-m",
            "py_compile",
            str(temp_script),
        ],
        capture_output=True,
        text=True,
    )

    if syntax.returncode != 0:

        return {
            "ticket_id": ticket["ticket_id"],
            "title": ticket["title"],
            "status": "SYNTAX_FAIL",
            "return_code": syntax.returncode,
            "task_blocks": {},
            "compact_task_blocks": {},
            "binding": binding,
            "stderr": syntax.stderr.strip(),
        }

    execution = subprocess.run(
        [
            sys.executable,
            str(temp_script),
        ],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )

    task_blocks = extract_task_blocks(
        execution.stdout
    )

    compact_blocks = {
        task: compact_task_block(lines)
        for task, lines in task_blocks.items()
    }

    status = classify_status(
        task_blocks
    )

    return {
        "ticket_id": ticket["ticket_id"],
        "title": ticket["title"],
        "status": status,
        "return_code": execution.returncode,
        "task_blocks": task_blocks,
        "compact_task_blocks": compact_blocks,
        "binding": binding,
        "stdout_line_count": len(
            execution.stdout.splitlines()
        ),
        "stderr": execution.stderr.strip(),
    }


def main() -> None:

    print("=" * 72)
    print(
        "H-RUN-017R3 — MULTI-TICKET RUNTIME VALIDATION"
    )
    print("=" * 72)

    print("\n[1] Source validation")

    if not SOURCE_SCRIPT.exists():
        fail(
            "H-RUN-015R2 source not found:\n"
            f"{SOURCE_SCRIPT}"
        )

    source_text = SOURCE_SCRIPT.read_text(
        encoding="utf-8"
    )

    print(
        "H-RUN-015R2 source:",
        SOURCE_SCRIPT,
    )

    print(
        "Source bytes:",
        SOURCE_SCRIPT.stat().st_size,
    )

    try:
        ast.parse(source_text)
    except SyntaxError as exc:
        fail(
            "H-RUN-015R2 source syntax failure:\n"
            f"{exc}"
        )

    print("Source syntax: PASS")

    title_nodes, description_nodes = (
        find_ticket_nodes(source_text)
    )

    print(
        "Title dictionary entries found:",
        len(title_nodes),
    )

    print(
        "Description dictionary entries found:",
        len(description_nodes),
    )

    if len(title_nodes) != 1:
        fail(
            "Expected exactly one literal title entry."
        )

    if len(description_nodes) != 1:
        fail(
            "Expected exactly one literal description entry."
        )

    print(
        "Actual ticket binding structure: PASS"
    )

    print("\n[2] Synthetic development tickets")

    for ticket in TICKETS:
        print(
            f"{ticket['ticket_id']}: "
            f"{ticket['title']}"
        )

    print("\n[3] Runtime execution")

    results = []

    with tempfile.TemporaryDirectory(
        prefix="h_run017r3_"
    ) as tmp:

        temp_dir = Path(tmp)

        for ticket in TICKETS:

            print(
                f"\n--- {ticket['ticket_id']} ---"
            )

            result = run_ticket(
                ticket,
                source_text,
                temp_dir,
            )

            results.append(result)

            print(
                "Status:",
                result["status"],
            )

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

                block = result[
                    "compact_task_blocks"
                ].get(
                    task,
                    "MISSING",
                )

                print(
                    f"{task}:",
                    block[:240],
                )

            if result["stderr"]:

                print(
                    "stderr:",
                    result["stderr"][:1000],
                )

    statuses = [
        result["status"]
        for result in results
    ]

    overall_status = (
        "PASS"
        if all(
            status == "PASS"
            for status in statuses
        )
        else "REQUIRES_REVIEW"
    )

    report = {
        "operation": "H-RUN-017R3",
        "operation_name": (
            "Multi-ticket runtime validation"
        ),
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": overall_status,
        "source_script": str(SOURCE_SCRIPT),
        "source_script_modified": False,
        "temporary_source_copies_only": True,
        "synthetic_development_only": True,
        "locked_test_used": False,
        "model_retraining": False,
        "model_modification": False,
        "prediction_modification": False,
        "threshold_optimization": False,
        "ticket_count": len(TICKETS),
        "tickets": results,
        "preserved_boundaries": {
            "t6_partial_native_runtime": True,
            "t7_support_limitation": True,
            "t8_boundary_envelope": True,
            "t9_boundary_envelope": True,
            "t10_policy_boundary": True,
            "t11_specification_only": True,
        },
    }

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\n[4] Final reconciliation")

    print(
        "Ticket count:",
        len(results),
    )

    print(
        "Statuses:",
        statuses,
    )

    print(
        "Overall status:",
        overall_status,
    )

    print(
        "Original H-RUN-015R2 modified: NO"
    )

    print(
        "Locked evaluation/test data used: NO"
    )

    print(
        "Model retraining/modification: NO"
    )

    print(
        "Prediction modification: NO"
    )

    print(
        "Threshold optimization: NO"
    )

    print(
        "\nOutput:",
        OUTPUT_PATH,
    )

    print("\n" + "=" * 72)
    print(
        "H-RUN-017R3 STATUS:",
        overall_status,
    )
    print("=" * 72)


if __name__ == "__main__":
    main()