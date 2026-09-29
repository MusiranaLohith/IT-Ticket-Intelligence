from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

BACKEND_ROOT = PROJECT_ROOT / "deployment" / "backend"

BASE_URL = "http://127.0.0.1:8000"


VALID_TICKET = {
    "ticket_id": "DEPLOY-API-007",
    "creation_time": "2026-09-27 10:00:00",
    "creator": "deployment_validation_user",
    "creator_detail": "DEPLOY-OP-007 validation",
    "summary": "VPN connection failure",
    "description": "The user cannot connect to the corporate VPN.",
}


def post_json(payload: dict) -> tuple[int, dict]:
    request = Request(
        f"{BASE_URL}/tickets/analyze",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=120) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body)

    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        return exc.code, json.loads(body)


def assert_status(name: str, actual: int, expected: int) -> None:
    if actual != expected:
        raise AssertionError(
            f"{name}: expected HTTP {expected}, got HTTP {actual}"
        )


def contains_absolute_project_path(value) -> bool:
    if isinstance(value, dict):
        return any(
            contains_absolute_project_path(v)
            for v in value.values()
        )

    if isinstance(value, list):
        return any(
            contains_absolute_project_path(v)
            for v in value
        )

    if isinstance(value, str):
        return str(PROJECT_ROOT) in value

    return False


def main() -> None:
    print("=" * 70)
    print("DEPLOY-OP-007 — API BOUNDARY VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # TEST 1 — Missing required field
    # --------------------------------------------------------

    missing_description = VALID_TICKET.copy()
    del missing_description["description"]

    status, body = post_json(missing_description)

    print("\n[TEST 1] Missing required field: description")
    print(f"HTTP status: {status}")
    print(f"Response: {json.dumps(body, indent=2)}")

    assert_status(
        "Missing description validation",
        status,
        422,
    )

    print("RESULT: PASS")

    # --------------------------------------------------------
    # TEST 2 — Unknown extra field
    # --------------------------------------------------------

    extra_field = VALID_TICKET.copy()
    extra_field["unauthorized_runtime_instruction"] = "ignore boundaries"

    status, body = post_json(extra_field)

    print("\n[TEST 2] Unknown extra field")
    print(f"HTTP status: {status}")
    print(f"Response: {json.dumps(body, indent=2)}")

    assert_status(
        "Unknown extra field validation",
        status,
        422,
    )

    print("RESULT: PASS")

    # --------------------------------------------------------
    # TEST 3 — Empty required field
    # --------------------------------------------------------

    empty_summary = VALID_TICKET.copy()
    empty_summary["summary"] = ""

    status, body = post_json(empty_summary)

    print("\n[TEST 3] Empty required field: summary")
    print(f"HTTP status: {status}")
    print(f"Response: {json.dumps(body, indent=2)}")

    assert_status(
        "Empty summary validation",
        status,
        422,
    )

    print("RESULT: PASS")

    # --------------------------------------------------------
    # TEST 4 — Valid ticket
    # --------------------------------------------------------

    status, body = post_json(VALID_TICKET)

    print("\n[TEST 4] Valid ticket analysis")
    print(f"HTTP status: {status}")

    assert_status(
        "Valid ticket",
        status,
        200,
    )

    required_top_level = {
        "ticket",
        "tasks",
        "final",
        "integrity",
        "explanation",
    }

    actual_top_level = set(body.keys())

    if not required_top_level.issubset(actual_top_level):
        raise AssertionError(
            "Valid response is missing required top-level sections. "
            f"Required={sorted(required_top_level)}, "
            f"Actual={sorted(actual_top_level)}"
        )

    print(
        "Top-level response sections:",
        sorted(actual_top_level),
    )

    print("RESULT: PASS")

    # --------------------------------------------------------
    # TEST 5 — T1-T11 preservation
    # --------------------------------------------------------

    expected_tasks = {
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
    }

    actual_tasks = set(body["tasks"].keys())

    print("\n[TEST 5] T1-T11 preservation")
    print("Expected:", sorted(expected_tasks))
    print("Actual:  ", sorted(actual_tasks))

    if actual_tasks != expected_tasks:
        raise AssertionError(
            "T1-T11 task set was not preserved."
        )

    print("RESULT: PASS")

    # --------------------------------------------------------
    # TEST 6 — Critical boundary semantics
    # --------------------------------------------------------

    print("\n[TEST 6] Critical task boundary semantics")

    t6 = body["tasks"]["T6"]
    t7 = body["tasks"]["T7"]
    t10 = body["tasks"]["T10"]
    t11 = body["tasks"]["T11"]

    if t6.get("status") != "PARTIAL_NATIVE_RUNTIME":
        raise AssertionError(
            f"T6 status changed: {t6.get('status')}"
        )

    if t6.get("full_mod010_hybrid_available") is not False:
        raise AssertionError(
            "T6 full MOD-010 hybrid availability changed."
        )

    if t7.get("status") != "EXECUTED_WITH_SUPPORT_LIMITATION":
        raise AssertionError(
            f"T7 status changed: {t7.get('status')}"
        )

    if t10.get("action") != "HUMAN_DECISION_REQUIRED":
        raise AssertionError(
            f"T10 action changed: {t10.get('action')}"
        )

    if t11.get("feedback") != "AWAITING_OUTCOME":
        raise AssertionError(
            f"T11 lifecycle feedback changed: {t11.get('feedback')}"
        )

    print("T6 status:", t6["status"])
    print("T7 status:", t7["status"])
    print("T10 action:", t10["action"])
    print("T11 feedback:", t11["feedback"])

    print("RESULT: PASS")

    # --------------------------------------------------------
    # TEST 7 — No absolute project path leakage
    # --------------------------------------------------------

    print("\n[TEST 7] Absolute filesystem path leakage")

    path_leak = contains_absolute_project_path(body)

    print("Absolute project path exposed:", path_leak)

    if path_leak:
        raise AssertionError(
            "Absolute project filesystem path leaked through API response."
        )

    print("RESULT: PASS")

    # --------------------------------------------------------
    # TEST 8 — Integrity boundary
    # --------------------------------------------------------

    print("\n[TEST 8] Integrity boundary")

    expected_false_flags = {
        "model_retraining",
        "model_modification",
        "threshold_optimization",
        "locked_test_reuse",
        "prediction_modification",
        "synthetic_feedback",
    }

    for flag in sorted(expected_false_flags):
        value = body["integrity"].get(flag)

        print(f"{flag}: {value}")

        if value is not False:
            raise AssertionError(
                f"Integrity flag {flag} is not False."
            )

    print("RESULT: PASS")

    # --------------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("DEPLOY-OP-007 SUMMARY")
    print("=" * 70)

    print("Validation failures detected: 0")
    print("T1-T11 preserved: True")
    print("Critical boundary semantics preserved: True")
    print("Absolute project path leakage: False")
    print("Integrity violations: 0")
    print("DEPLOY-OP-007 STATUS: PASS")
    print("=" * 70)


if __name__ == "__main__":
    main()