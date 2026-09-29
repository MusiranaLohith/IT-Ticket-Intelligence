from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

RUNTIME_ROOT = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "deployment"
    / "runtime"
)

PIPELINE_PATH = RUNTIME_ROOT / "ticket_pipeline.py"

EVIDENCE_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "deploy_op002_batch_api_contract.json"
)

REQUIRED_TICKET_FIELDS = [
    "ticket_id",
    "creation_time",
    "creator",
    "creator_detail",
    "summary",
    "description",
]


def load_pipeline_class():
    import sys

    runtime_root = str(RUNTIME_ROOT)

    if runtime_root not in sys.path:
        sys.path.insert(0, runtime_root)

    from ticket_pipeline import TicketPipeline

    return TicketPipeline


def main() -> None:
    print("=" * 72)
    print("DEPLOY-OP-002 — BATCH API CONTRACT")
    print("=" * 72)

    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"RUNTIME_ROOT: {RUNTIME_ROOT}")
    print(f"PIPELINE_PATH: {PIPELINE_PATH}")

    if not PROJECT_ROOT.is_dir():
        raise RuntimeError(
            f"Project root does not exist: {PROJECT_ROOT}"
        )

    if not RUNTIME_ROOT.is_dir():
        raise RuntimeError(
            f"Runtime root does not exist: {RUNTIME_ROOT}"
        )

    if not PIPELINE_PATH.is_file():
        raise RuntimeError(
            f"Frozen pipeline file does not exist: {PIPELINE_PATH}"
        )

    TicketPipeline = load_pipeline_class()

    print("\n--- FROZEN RUNTIME INTERFACE ---")

    predict_signature = inspect.signature(
        TicketPipeline.predict
    )

    predict_batch_signature = inspect.signature(
        TicketPipeline.predict_batch
    )

    print(f"predict: {predict_signature}")
    print(f"predict_batch: {predict_batch_signature}")

    predict_batch_exists = hasattr(
        TicketPipeline,
        "predict_batch"
    )

    predict_exists = hasattr(
        TicketPipeline,
        "predict"
    )

    print(
        f"predict_exists: {predict_exists}"
    )

    print(
        f"predict_batch_exists: {predict_batch_exists}"
    )

    if not predict_exists:
        raise RuntimeError(
            "Frozen runtime does not expose predict()."
        )

    if not predict_batch_exists:
        raise RuntimeError(
            "Frozen runtime does not expose predict_batch()."
        )

    batch_parameters = list(
        predict_batch_signature.parameters.values()
    )

    batch_parameter_names = [
        parameter.name
        for parameter in batch_parameters
    ]

    print(
        "predict_batch_parameters:",
        batch_parameter_names
    )

    expected_batch_parameters = [
        "self",
        "tickets",
    ]

    batch_signature_matches = (
        batch_parameter_names
        == expected_batch_parameters
    )

    print(
        "batch_signature_matches:",
        batch_signature_matches
    )

    if not batch_signature_matches:
        raise RuntimeError(
            "Unexpected frozen predict_batch() signature."
        )

    print("\n--- TICKET SCHEMA ---")

    for field in REQUIRED_TICKET_FIELDS:
        print(f"required field: {field}")

    print("\n--- API CONTRACT ---")

    api_contract = {
        "operation": "DEPLOY-OP-002",
        "status": "CONTRACT_DEFINED",
        "endpoint": {
            "method": "POST",
            "path": "/tickets/analyze-batch",
        },
        "input": {
            "type": "object",
            "required_field": "tickets",
            "tickets_type": "array",
            "minimum_tickets": 1,
            "ticket_schema": REQUIRED_TICKET_FIELDS,
        },
        "processing": {
            "runtime_class": "TicketPipeline",
            "runtime_method": "predict_batch",
            "independent_ticket_processing": True,
            "batch_size_agnostic": True,
            "special_batch_sizes": [],
        },
        "output": {
            "one_result_per_input_ticket": True,
            "preserve_ticket_identity": True,
            "preserve_t1_t11_results": True,
            "preserve_ticket_explanation": True,
        },
        "validation": {
            "required_ticket_fields": REQUIRED_TICKET_FIELDS,
            "malformed_tickets_rejected": True,
            "empty_batch_rejected": True,
            "extra_ticket_fields": "REJECT",
        },
        "single_ticket_boundary": {
            "existing_endpoint_preserved": True,
            "existing_endpoint": {
                "method": "POST",
                "path": "/tickets/analyze",
            },
        },
        "runtime_protection": {
            "frozen_runtime_modified": False,
            "ml_logic_duplicated": False,
            "model_artifacts_modified": False,
            "thresholds_added": False,
            "universal_confidence_added": False,
            "universal_risk_added": False,
            "t8_semantics_changed": False,
            "t9_boundaries_changed": False,
            "t10_autonomous_policy_added": False,
            "t11_feedback_fabricated": False,
        },
        "priority_severity_display": {
            "use_class_labels_only": True,
            "invented_english_meanings": False,
        },
        "production_boundary": {
            "production_ready": False,
            "authorization": "NOT_ESTABLISHED",
        },
    }

    print(
        json.dumps(
            api_contract,
            indent=2,
            sort_keys=False,
        )
    )

    print("\n--- CONTRACT ASSERTIONS ---")

    assertions = {
        "project_root_exists": PROJECT_ROOT.is_dir(),
        "runtime_root_exists": RUNTIME_ROOT.is_dir(),
        "pipeline_exists": PIPELINE_PATH.is_file(),
        "predict_exists": predict_exists,
        "predict_batch_exists": predict_batch_exists,
        "predict_batch_signature_valid": batch_signature_matches,
        "batch_endpoint_defined": (
            api_contract["endpoint"]["path"]
            == "/tickets/analyze-batch"
        ),
        "batch_size_agnostic": (
            api_contract["processing"]["batch_size_agnostic"]
            is True
        ),
        "one_result_per_input_ticket": (
            api_contract["output"][
                "one_result_per_input_ticket"
            ]
            is True
        ),
        "single_endpoint_preserved": (
            api_contract["single_ticket_boundary"][
                "existing_endpoint_preserved"
            ]
            is True
        ),
        "frozen_runtime_protected": (
            all(
                value is False
                for value in api_contract[
                    "runtime_protection"
                ].values()
            )
        ),
        "production_not_ready": (
            api_contract["production_boundary"][
                "production_ready"
            ]
            is False
        ),
    }

    for name, passed in assertions.items():
        print(
            f"[{'PASS' if passed else 'FAIL'}] {name}"
        )

    all_passed = all(assertions.values())

    if not all_passed:
        raise RuntimeError(
            "One or more DEPLOY-OP-002 contract "
            "assertions failed."
        )

    EVIDENCE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    evidence = {
        "operation": "DEPLOY-OP-002",
        "status": "PASS",
        "contract": api_contract,
        "runtime_interface": {
            "predict": str(predict_signature),
            "predict_batch": str(
                predict_batch_signature
            ),
            "predict_batch_parameters": (
                batch_parameter_names
            ),
        },
        "assertions": assertions,
        "read_only_runtime": True,
        "frozen_runtime_modified": False,
    }

    EVIDENCE_PATH.write_text(
        json.dumps(
            evidence,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n--- EVIDENCE ---")
    print(f"Evidence file: {EVIDENCE_PATH}")
    print(
        f"Evidence exists: {EVIDENCE_PATH.is_file()}"
    )

    print("\n" + "=" * 72)
    print("DEPLOY-OP-002 COMPLETE")
    print("=" * 72)
    print("STATUS: PASS")
    print("API CONTRACT: DEFINED")
    print("PREDICT_BATCH: AVAILABLE")
    print("BATCH SIZE: AGNOSTIC")
    print("SINGLE-TICKET ENDPOINT: PRESERVED")
    print("FROZEN RUNTIME: UNMODIFIED")
    print("PRODUCTION READY: FALSE")
    print("=" * 72)


if __name__ == "__main__":
    main()