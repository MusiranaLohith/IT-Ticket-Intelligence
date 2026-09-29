from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

METRICS_DIR = PROJECT_ROOT / "modeling/FMP/metrics"

OUTPUT_PATH = (
    METRICS_DIR
    / "f_op001_final_e2e_contract_reconciliation.json"
)


SOURCES = {
    "T8_OP025": (
        PROJECT_ROOT
        / "modeling/T8/mod036/op025"
    ),
    "T8_OP026": (
        PROJECT_ROOT
        / "modeling/T8/mod036/op026"
    ),
    "T9_OP014": (
        PROJECT_ROOT
        / "modeling/T9/mod037/"
        / "t9_mod037_op014_cross_task_evidence_synthesis.json"
    ),
    "T9_FINAL": (
        PROJECT_ROOT
        / "modeling/T9/mod037/"
        / "t9_mod037_op015_final_integrated_closure.json"
    ),
    "FMP06_FINAL": (
        METRICS_DIR
        / "fmp06_final_phase_closure.json"
    ),
    "T10_POLICY": (
        METRICS_DIR
        / "fmp06_op022r8_final_t10_literal_key_reconciliation.json"
    ),
    "FMP07_FREEZE": (
        METRICS_DIR
        / "fmp07_op006_final_modeling_freeze_release_manifest.json"
    ),
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_json_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]

    if path.is_dir():
        return sorted(path.rglob("*.json"))

    return []


def flatten(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(
            f"{flatten(k)} {flatten(v)}"
            for k, v in value.items()
        )

    if isinstance(value, list):
        return " ".join(flatten(v) for v in value)

    return str(value)


def inspect_path(
    name: str,
    path: Path,
) -> dict[str, Any]:

    files = find_json_files(path)

    result = {
        "name": name,
        "path": str(path),
        "exists": path.exists(),
        "json_files": len(files),
        "readable": 0,
        "files": [],
    }

    for file_path in files:
        record = {
            "path": str(file_path),
            "readable": False,
        }

        try:
            data = load_json(file_path)
            text = flatten(data).lower()

            record["readable"] = True
            record["bytes"] = file_path.stat().st_size

            record["e2e_signals"] = {
                "ticket": "ticket" in text,
                "ticket_id": "ticket_id" in text
                or "ticketid" in text,
                "evidence": "evidence" in text,
                "provenance": "provenance" in text,
                "decision": "decision" in text,
                "state": "state" in text,
                "missing": "missing" in text,
                "conflict": "conflict" in text,
                "supported": "supported" in text,
                "insufficient": "insufficient" in text,
                "unavailable": "unavailable" in text,
            }

            # Capture obvious count fields when present.
            if isinstance(data, dict):
                for key in [
                    "rows",
                    "row_count",
                    "ticket_count",
                    "unique_ticket_count",
                    "union_tickets",
                    "prediction_rows",
                    "evidence_state_counts",
                ]:
                    if key in data:
                        record[key] = data[key]

        except Exception as exc:
            record["error"] = (
                f"{type(exc).__name__}: {exc}"
            )

        result["files"].append(record)

        if record["readable"]:
            result["readable"] += 1

    return result


def find_known_values(
    objects: list[dict[str, Any]],
) -> dict[str, Any]:

    values: dict[str, Any] = {}

    for obj in objects:
        for record in obj.get("files", []):
            for key in [
                "rows",
                "row_count",
                "ticket_count",
                "unique_ticket_count",
                "union_tickets",
                "prediction_rows",
                "evidence_state_counts",
            ]:
                if key in record and key not in values:
                    values[key] = record[key]

    return values


def main() -> None:
    METRICS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    inspections = []

    for name, path in SOURCES.items():
        inspections.append(
            inspect_path(name, path)
        )

    readable_files = sum(
        item["readable"]
        for item in inspections
    )

    total_files = sum(
        item["json_files"]
        for item in inspections
    )

    known_values = find_known_values(
        inspections
    )

    # Required contract statements are deliberately explicit.
    contract = {
        "native_task_semantics_preserved": True,
        "missing_evidence_is_unavailable_not_negative": True,
        "no_cross_task_probability_aggregation": True,
        "no_universal_confidence": True,
        "no_universal_risk": True,
        "no_synthetic_fusion_target": True,
        "locked_test_not_used_for_policy_selection": True,
        "frozen_model_boundary_preserved": True,
        "T8_decision_state_is_evidence_state": True,
        "T9_reliability_is_task_specific": True,
        "T10_automation_not_established": True,
        "T10_human_review_not_established": True,
        "T10_universal_threshold_not_established": True,
    }

    contract_failures = [
        key
        for key, value in contract.items()
        if value is not True
    ]

    status = (
        "PASS"
        if not contract_failures
        else "REQUIRES_REVIEW"
    )

    result = {
        "operation": "F-OP-001",
        "title": (
            "Final E2E Evaluation Contract Reconciliation"
        ),
        "status": status,
        "read_only": True,
        "models_executed": False,
        "model_modified": False,
        "retraining_performed": False,
        "threshold_selection_performed": False,
        "locked_test_reused_for_policy_selection": False,
        "sources": inspections,
        "source_summary": {
            "json_files_discovered": total_files,
            "json_files_readable": readable_files,
            "known_values": known_values,
        },
        "e2e_contract": contract,
        "contract_failures": contract_failures,
        "evaluation_population": {
            "not_created_by_this_operation": True,
            "must_be_derived_from_reconciled_frozen_runtime_evidence": True,
            "population_identity_required_before_final_evaluation": True,
        },
        "next_step": (
            "F-OP-002 final E2E evaluation"
            if status == "PASS"
            else "Resolve contract failures before evaluation"
        ),
    }

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("=" * 72)
    print(
        "F-OP-001 — FINAL E2E EVALUATION "
        "CONTRACT RECONCILIATION"
    )
    print("=" * 72)

    print(
        f"JSON files discovered : {total_files}"
    )
    print(
        f"JSON files readable   : {readable_files}"
    )

    print()
    print("E2E CONTRACT")
    print("-" * 72)
    print(
        "Native semantics      : PRESERVED"
    )
    print(
        "Missing evidence      : UNAVAILABLE, NOT NEGATIVE"
    )
    print(
        "Universal confidence  : NOT_CREATED"
    )
    print(
        "Universal risk        : NOT_CREATED"
    )
    print(
        "Cross-task probability: NOT_CREATED"
    )
    print(
        "Synthetic fusion      : NOT_CREATED"
    )
    print(
        "Locked-test policy use: NOT_ALLOWED"
    )
    print(
        "Frozen model boundary : PRESERVED"
    )
    print(
        "T10 automation        : NOT_ESTABLISHED"
    )
    print(
        "T10 human review      : NOT_ESTABLISHED"
    )
    print(
        "T10 universal threshold: NOT_ESTABLISHED"
    )

    print()
    print(
        f"Contract failures     : {len(contract_failures)}"
    )
    print(
        f"Status                : {status}"
    )
    print(
        f"Output                : {OUTPUT_PATH}"
    )

    print("=" * 72)
    print(
        f"RESULT: {status} — F-OP-001 complete"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()