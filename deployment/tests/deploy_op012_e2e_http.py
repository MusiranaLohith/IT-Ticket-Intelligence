from __future__ import annotations

import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = f"{BASE_URL}/tickets/analyze"

PROJECT_ROOT = "/home/whiteblack/Documents/IT-Ticket-Triage-System"


TEST_TICKET = {
    "ticket_id": "DEPLOY-E2E-012",
    "creation_time": "2026-09-27T10:00:00",
    "creator": "deployment-test-user",
    "creator_detail": "engineering",
    "summary": "VPN connection failure",
    "description": (
        "Unable to connect to the corporate VPN "
        "from the workstation."
    ),
}


def fail(message: str) -> None:
    raise AssertionError(message)


def post_ticket() -> tuple[int, dict]:
    payload = json.dumps(TEST_TICKET).encode("utf-8")

    request = Request(
        ENDPOINT,
        data=payload,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=60) as response:
            status_code = response.status
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        fail(
            f"HTTP request failed: "
            f"status={exc.code}, body={body}"
        )

    try:
        result = json.loads(body)
    except json.JSONDecodeError as exc:
        fail(f"Response is not valid JSON: {exc}")

    return status_code, result


def walk_strings(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from walk_strings(item)

    elif isinstance(value, list):
        for item in value:
            yield from walk_strings(item)

    elif isinstance(value, str):
        yield value


def main() -> None:

    status_code, result = post_ticket()

    print("DEPLOY-OP-012")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. HTTP status
    # --------------------------------------------------------

    if status_code != 200:
        fail(f"Expected HTTP 200, got {status_code}")

    print("[PASS] HTTP status = 200")

    # --------------------------------------------------------
    # 2. Top-level response contract
    # --------------------------------------------------------

    expected_top_level = {
        "ticket",
        "tasks",
        "final",
        "integrity",
        "explanation",
    }

    actual_top_level = set(result.keys())

    if actual_top_level != expected_top_level:
        fail(
            "Top-level response mismatch: "
            f"{actual_top_level}"
        )

    print("[PASS] Top-level response contract")

    # --------------------------------------------------------
    # 3. Ticket identity
    # --------------------------------------------------------

    if result["ticket"]["ticket_id"] != TEST_TICKET["ticket_id"]:
        fail("Ticket ID was not preserved")

    print("[PASS] Ticket identity preserved")

    # --------------------------------------------------------
    # 4. T1-T11 presence
    # --------------------------------------------------------

    expected_tasks = {
        f"T{i}"
        for i in range(1, 12)
    }

    actual_tasks = set(result["tasks"].keys())

    if actual_tasks != expected_tasks:
        fail(
            "T1-T11 task set mismatch: "
            f"{actual_tasks}"
        )

    print("[PASS] T1-T11 preserved")

    # --------------------------------------------------------
    # 5. T6 semantics
    # --------------------------------------------------------

    t6 = result["tasks"]["T6"]

    if t6["status"] != "PARTIAL_NATIVE_RUNTIME":
        fail(
            "T6 status changed: "
            f"{t6['status']}"
        )

    if t6["full_mod010_hybrid_available"] is not False:
        fail("T6 MOD-010 availability was altered")

    print("[PASS] T6 limitation preserved")

    # --------------------------------------------------------
    # 6. T7 semantics
    # --------------------------------------------------------

    t7 = result["tasks"]["T7"]

    if t7["status"] != "EXECUTED_WITH_SUPPORT_LIMITATION":
        fail(
            "T7 status changed: "
            f"{t7['status']}"
        )

    if (
        t7["temporal_support"]
        != "OUTSIDE_OBSERVED_TRAINING_RANGE"
    ):
        fail("T7 temporal limitation was altered")

    print("[PASS] T7 limitation preserved")

    # --------------------------------------------------------
    # 7. T8 semantics
    # --------------------------------------------------------

    t8 = result["tasks"]["T8"]

    if t8["evidence_state"] != "SUPPORTED_WITH_LIMITATIONS":
        fail(
            "T8 evidence state changed: "
            f"{t8['evidence_state']}"
        )

    if t8["missing_evidence_is_not_negative"] is not True:
        fail("T8 missing-evidence semantics changed")

    print("[PASS] T8 semantics preserved")

    # --------------------------------------------------------
    # 8. T9 semantics
    # --------------------------------------------------------

    t9 = result["tasks"]["T9"]

    if t9["universal_confidence"] is not None:
        fail("Universal confidence was created")

    if t9["universal_risk"] is not None:
        fail("Universal risk was created")

    if t9["cross_task_probability_aggregation"] is not False:
        fail("Cross-task probability aggregation was enabled")

    print("[PASS] T9 no universal confidence/risk")

    # --------------------------------------------------------
    # 9. T10 semantics
    # --------------------------------------------------------

    t10 = result["tasks"]["T10"]

    if t10["action"] != "HUMAN_DECISION_REQUIRED":
        fail(
            "T10 action changed: "
            f"{t10['action']}"
        )

    if t10["automation"] != "NOT_ESTABLISHED":
        fail("T10 automation state changed")

    print("[PASS] T10 human-decision boundary")

    # --------------------------------------------------------
    # 10. T11 semantics
    # --------------------------------------------------------

    t11 = result["tasks"]["T11"]

    if t11["feedback"] != "AWAITING_OUTCOME":
        fail(
            "T11 lifecycle changed: "
            f"{t11['feedback']}"
        )

    if t11["synthetic_feedback"] is not False:
        fail("Synthetic feedback was introduced")

    print("[PASS] T11 lifecycle boundary")

    # --------------------------------------------------------
    # 11. Integrity flags
    # --------------------------------------------------------

    integrity = result["integrity"]

    expected_integrity = {
        "model_retraining": False,
        "model_modification": False,
        "threshold_optimization": False,
        "locked_test_reuse": False,
        "prediction_modification": False,
        "synthetic_feedback": False,
    }

    if integrity != expected_integrity:
        fail(
            "Integrity contract changed: "
            f"{integrity}"
        )

    print("[PASS] Integrity protections")

    # --------------------------------------------------------
    # 12. Filesystem path leakage
    # --------------------------------------------------------

    response_strings = list(walk_strings(result))

    leaked_paths = [
        value
        for value in response_strings
        if PROJECT_ROOT in value
    ]

    if leaked_paths:
        fail(
            "Absolute project path leakage detected: "
            f"{leaked_paths}"
        )

    print("[PASS] No absolute project paths leaked")

    # --------------------------------------------------------
    # 13. Explanation
    # --------------------------------------------------------

    explanation = result["explanation"]

    if not isinstance(explanation, str):
        fail("Explanation is not a string")

    if "HUMAN_DECISION_REQUIRED" not in explanation:
        fail("Explanation does not preserve T10 action")

    if "AWAITING_OUTCOME" not in explanation:
        fail("Explanation does not preserve T11 lifecycle")

    print("[PASS] TicketExplanation preserved")

    print("=" * 60)
    print("ALL DEPLOY-OP-012 TESTS PASSED")
    print("STATUS: PASS")


if __name__ == "__main__":
    main()