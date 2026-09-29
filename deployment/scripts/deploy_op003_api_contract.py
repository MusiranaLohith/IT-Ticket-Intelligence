from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

DEPLOYMENT_ROOT = PROJECT_ROOT / "modeling" / "FMP" / "deployment"
RUNTIME_ROOT = DEPLOYMENT_ROOT / "runtime"

METRICS_ROOT = PROJECT_ROOT / "modeling" / "FMP" / "metrics"

OUTPUT_PATH = METRICS_ROOT / "deploy_op003_api_contract.json"


PUBLIC_TICKET_FIELDS = [
    "ticket_id",
    "creation_time",
    "creator",
    "creator_detail",
    "summary",
    "description",
]


def build_contract() -> dict:
    return {
        "operation": "DEPLOY-OP-003",
        "title": "API/Application Boundary Contract",
        "status": "CONTRACT_DEFINED",

        "project_root": str(PROJECT_ROOT),
        "deployment_root": str(DEPLOYMENT_ROOT),
        "runtime_root": str(RUNTIME_ROOT),

        "frozen_runtime_policy": {
            "runtime_is_frozen": True,
            "runtime_files": [
                "runtime/ticket_pipeline.py",
                "runtime/ticket_explanation.py",
            ],
            "application_layer_may_wrap_runtime": True,
            "application_layer_must_not_duplicate_model_logic": True,
            "application_layer_must_not_modify_runtime": True,
            "application_layer_must_not_retrain": True,
            "application_layer_must_not_recalibrate": True,
            "application_layer_must_not_reoptimize_thresholds": True,
        },

        "input_contract": {
            "required_fields": PUBLIC_TICKET_FIELDS,
            "additional_fields_policy": "REJECT_OR_EXPLICITLY_CONTROL; DO_NOT_SILENTLY_INTERPRET",
            "validation_owner": "API_APPLICATION_LAYER",
            "runtime_input_type": "dict[str, Any]",
        },

        "endpoints": {
            "health": {
                "method": "GET",
                "path": "/health",
                "purpose": "Report application and packaged-runtime availability.",
                "must_not_execute_ticket_prediction": True,
            },

            "analyze_ticket": {
                "method": "POST",
                "path": "/tickets/analyze",
                "purpose": (
                    "Validate a public ticket payload, execute the frozen "
                    "TicketPipeline, generate TicketExplanation output, and "
                    "return stable ticket-facing evidence."
                ),
                "runtime_call": "TicketPipeline.predict(ticket)",
                "explanation_call": "TicketExplanation.explain(result)",
            },
        },

        "response_contract": {
            "analyze_ticket": {
                "required_top_level_sections": [
                    "ticket",
                    "tasks",
                    "final",
                    "integrity",
                    "explanation",
                ],
                "tasks_required": [
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
                ],
                "preserve_runtime_semantics": True,
                "preserve_task_specific_fields": True,
                "preserve_integrity_flags": True,
                "preserve_ticket_explanation": True,
            }
        },

        "task_semantics": {
            "T1": "Category prediction",
            "T2": "Priority prediction",
            "T3": "Severity prediction",
            "T4": "Historical assignee retrieval evidence",
            "T5": "Duplicate evidence",
            "T6": "Related-ticket retrieval evidence with native runtime limitation preserved",
            "T7": "Resolution-time evidence with temporal-support limitation preserved",
            "T8": "Evidence integration",
            "T9": "Reliability/evidence boundary",
            "T10": "Decision/policy boundary",
            "T11": "Lifecycle/feedback state",
        },

        "mandatory_boundary_semantics": {
            "T6": {
                "required": True,
                "full_mod010_hybrid_may_not_be_fabricated": True,
                "new_ticket_semantic_score_may_not_be_invented": True,
            },

            "T7": {
                "required": True,
                "temporal_support_limitation_must_be_preserved": True,
                "out_of_training_range_must_not_be_silently_hidden": True,
            },

            "T8": {
                "required": True,
                "missing_evidence_is_not_negative": True,
                "native_evidence_semantics_must_be_preserved": True,
            },

            "T9": {
                "required": True,
                "universal_confidence_must_not_be_created": True,
                "universal_risk_must_not_be_created": True,
                "cross_task_probability_aggregation_must_not_be_created": True,
            },

            "T10": {
                "required": True,
                "human_decision_required_must_be_preserved": True,
                "automation_must_remain_not_established": True,
                "universal_threshold_must_not_be_invented": True,
            },

            "T11": {
                "required": True,
                "awaiting_outcome_semantics_must_be_preserved": True,
                "synthetic_feedback_must_not_be_created": True,
            },
        },

        "artifact_path_policy": {
            "runtime_may_return_internal_artifact_paths": True,
            "absolute_filesystem_paths_must_not_be_exposed_to_clients": True,
            "frozen_runtime_must_not_be_modified_to_remove_paths": True,
            "api_layer_must_sanitize_or_transform_internal_paths": True,
            "client_facing_artifact_reference_policy": (
                "Expose stable non-sensitive artifact identifiers or "
                "omit internal filesystem locations."
            ),
        },

        "prohibited_application_behavior": [
            "Do not duplicate T1-T11 model logic in FastAPI.",
            "Do not create universal confidence.",
            "Do not create universal risk.",
            "Do not invent automation thresholds.",
            "Do not invent human-review thresholds.",
            "Do not fabricate T6 semantic scores for genuinely new tickets.",
            "Do not hide T7 temporal-support limitations.",
            "Do not interpret missing evidence as negative evidence.",
            "Do not create synthetic feedback.",
            "Do not modify frozen model artifacts.",
            "Do not retrain frozen models.",
            "Do not recalibrate frozen models.",
            "Do not optimize thresholds during deployment.",
            "Do not claim production authorization.",
        ],

        "persistence": {
            "postgresql_selected": False,
            "reason": (
                "Persistence has not yet been justified by an identified "
                "deployment requirement. No history endpoint is defined "
                "until persistence is explicitly selected."
            ),
        },

        "health_contract": {
            "status_values": [
                "OK",
                "DEGRADED",
                "ERROR",
            ],
            "minimum_information": [
                "application availability",
                "packaged runtime availability",
            ],
            "must_not_claim": [
                "production authorization",
                "model quality",
                "business performance",
                "autonomous operational readiness",
            ],
        },

        "maturity_boundary": {
            "current_state": "RESEARCH_ENGINEERING_PROTOTYPE",
            "production_ready": False,
            "production_authorization": "NOT_ESTABLISHED",
            "purpose": "Decision-support evidence, not autonomous ticket disposition.",
        },

        "contract_proof": {
            "source_runtime_contract": (
                "DEPLOY-OP-002 packaged TicketPipeline/TicketExplanation "
                "inspection"
            ),
            "source_runtime_validation": (
                "H-RUN-026-OP-005 packaged deployment runtime validation"
            ),
            "design_rule": (
                "The application layer wraps the frozen runtime without "
                "changing its modeling semantics."
            ),
        },
    }


def main() -> None:
    METRICS_ROOT.mkdir(parents=True, exist_ok=True)

    contract = build_contract()

    OUTPUT_PATH.write_text(
        json.dumps(contract, indent=2),
        encoding="utf-8",
    )

    print("=" * 60)
    print("DEPLOY-OP-003 — API/APPLICATION BOUNDARY CONTRACT")
    print("=" * 60)

    print(f"[1] Project root: {PROJECT_ROOT}")
    print(f"[2] Deployment root: {DEPLOYMENT_ROOT}")
    print(f"[3] Runtime root: {RUNTIME_ROOT}")

    print("\n[4] PUBLIC TICKET INPUT FIELDS")
    for field in PUBLIC_TICKET_FIELDS:
        print(f"  - {field}")

    print("\n[5] ENDPOINTS DEFINED")
    for name, endpoint in contract["endpoints"].items():
        print(
            f"  - {endpoint['method']} {endpoint['path']} "
            f"-> {endpoint['purpose']}"
        )

    print("\n[6] RESPONSE CONTRACT")
    for section in contract["response_contract"]["analyze_ticket"][
        "required_top_level_sections"
    ]:
        print(f"  - {section}")

    print("\n[7] TASK CONTRACT")
    for task in contract["response_contract"]["analyze_ticket"]["tasks_required"]:
        print(f"  - {task}: {contract['task_semantics'][task]}")

    print("\n[8] CRITICAL BOUNDARIES")
    print(
        "  - T6 full MOD-010 semantic score fabrication: PROHIBITED"
    )
    print(
        "  - T7 temporal-support limitation hiding: PROHIBITED"
    )
    print(
        "  - Universal confidence/risk creation: PROHIBITED"
    )
    print(
        "  - Threshold invention: PROHIBITED"
    )
    print(
        "  - Synthetic feedback: PROHIBITED"
    )
    print(
        "  - Frozen runtime modification: PROHIBITED"
    )

    print("\n[9] ARTIFACT PATH POLICY")
    print(
        "  - Internal absolute filesystem paths may exist in runtime output."
    )
    print(
        "  - API layer must sanitize/transform them before client exposure."
    )
    print(
        "  - Frozen runtime will NOT be modified."
    )

    print("\n[10] PERSISTENCE")
    print("  - PostgreSQL selected: False")
    print("  - History endpoint defined: False")

    print("\n[11] MATURITY")
    print("  - Research / engineering prototype")
    print("  - Production ready: False")
    print("  - Production authorization: NOT_ESTABLISHED")

    print("\n[12] EVIDENCE")
    print(f"  - Contract written to: {OUTPUT_PATH}")
    print("  - Frozen runtime modified: False")
    print("  - Models modified: False")

    print("\nDEPLOY-OP-003 STATUS: CONTRACT_DEFINED")
    print("=" * 60)


if __name__ == "__main__":
    main()