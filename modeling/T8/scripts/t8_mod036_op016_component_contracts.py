from pathlib import Path
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
OUT_DIR = ROOT / "modeling/T8/mod036"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = OUT_DIR / "t8_mod036_op016_component_contracts.json"


def main():
    print("=" * 80)
    print("T8 DECISION ENGINE — MOD-036 OP-016")
    print("Trainable Component Contracts")
    print("=" * 80)

    contracts = {
        "priority_component": {
            "output": "priority_recommendation",
            "source_task": "T2",
            "target": "target_priority",
            "target_semantics": (
                "first valid P1-P5 priority event strictly after Creation "
                "within the validated T2 target window"
            ),
            "prediction_boundary": "Creation",
            "development_population": (
                "T2 development population using the established T2 "
                "train/validation structure"
            ),
            "evaluation_population": (
                "locked T2 test population; not used for model selection"
            ),
            "primary_metrics": [
                "macro_f1",
                "accuracy",
                "weighted_f1",
            ],
            "output_fields": [
                "recommended_priority",
                "native_priority_evidence",
                "support_state",
            ],
            "allowed_supporting_evidence": [
                "T3 secondary severity evidence",
            ],
            "missing_evidence_policy": (
                "T3 unavailable means no T3 support; it is not treated "
                "as negative evidence."
            ),
            "leakage_controls": [
                "Creation boundary enforced.",
                "Future priority target information forbidden.",
                "Post-Creation features forbidden.",
                "T2 locked evaluation data excluded from model selection.",
            ],
        },

        "assignment_component": {
            "output": "assignment_recommendation",
            "source_task": "T4",
            "target": "target_assignee",
            "target_semantics": (
                "first valid assignment event strictly after Creation"
            ),
            "prediction_boundary": "Creation",
            "development_population": (
                "T4 model-development population using T4's established "
                "training/evaluation construction."
            ),
            "evaluation_population": (
                "locked T4 evaluation population; not used for candidate "
                "selection or model selection."
            ),
            "candidate_space": {
                "selection": (
                    "training/validation-observed candidate assignees"
                ),
                "evaluation": (
                    "T4-prescribed evaluation candidate handling"
                ),
                "global_universe_for_selection": False,
            },
            "primary_metrics": [
                "top_1_accuracy",
                "top_k_recall",
                "unseen_target_rate",
            ],
            "output_fields": [
                "recommended_assignee_or_group",
                "ranked_assignment_candidates",
                "retrieval_evidence",
                "support_state",
            ],
            "allowed_supporting_evidence": [
                "T1 category evidence",
                "T6 ranking evidence where semantically compatible",
            ],
            "missing_evidence_policy": (
                "Unavailable T1/T6 evidence is omitted from support; "
                "it is not treated as negative assignment evidence."
            ),
            "leakage_controls": [
                "Creation boundary enforced.",
                "Current assigned_to is target-side information.",
                "Future assignment information forbidden.",
                "Unseen evaluation targets are not converted into negatives.",
                "Operational assignee eligibility is not claimed.",
            ],
        },

        "duplicate_component": {
            "output": "duplicate_recommendation",
            "source_task": "T5",
            "target": "T5 native duplicate target",
            "target_semantics": "validated T5 duplicate classification target",
            "prediction_boundary": "Creation",
            "development_population": (
                "T5 model-development population using the established "
                "T5 train/validation construction."
            ),
            "evaluation_population": (
                "locked T5 evaluation population; not used for model "
                "selection."
            ),
            "primary_metrics": [
                "roc_auc",
                "average_precision",
                "log_loss",
                "calibration",
            ],
            "output_fields": [
                "duplicate_recommendation",
                "duplicate_probability",
                "support_state",
            ],
            "allowed_supporting_evidence": [
                "T4 retrieval evidence only where explicitly validated"
            ],
            "missing_evidence_policy": (
                "Unavailable supporting evidence is omitted rather than "
                "treated as negative duplicate evidence."
            ),
            "leakage_controls": [
                "Creation boundary enforced.",
                "Post-Creation information forbidden.",
                "T5 calibration semantics preserved.",
                "Retrieval scores are not automatically interpreted as "
                "duplicate probabilities.",
            ],
        },

        "resolution_component": {
            "output": "resolution_context",
            "source_task": "T7",
            "target": "T7 time-to-resolution survival target",
            "target_semantics": (
                "time-to-resolution with event and right-censoring semantics"
            ),
            "prediction_boundary": "Creation",
            "development_population": (
                "T7 development population using its established "
                "chronological construction."
            ),
            "evaluation_population": (
                "locked T7 evaluation population; not used for model "
                "selection."
            ),
            "primary_metrics": [
                "c_index",
                "ipcw_brier_score",
            ],
            "output_fields": [
                "predicted_median_resolution_time",
                "survival_context",
                "censoring_state",
                "support_state",
            ],
            "allowed_supporting_evidence": [
                "T2 priority evidence where justified",
                "T3 severity evidence where justified",
            ],
            "missing_evidence_policy": (
                "Unavailable supporting evidence is omitted; it is not "
                "interpreted as evidence for or against resolution time."
            ),
            "leakage_controls": [
                "Creation boundary enforced.",
                "Event and censoring semantics preserved.",
                "Censored cases are not converted into ordinary negative labels.",
                "Survival predictions are not converted into ordinary "
                "regression targets.",
            ],
        },
    }

    global_contract = {
        "operation": "MOD-036 OP-016",
        "purpose": (
            "Freeze the interfaces, targets, populations, outputs, "
            "metrics, and leakage controls for the four trainable T8 "
            "decision components before modeling."
        ),
        "prediction_boundary": "Creation",
        "decision_unit": "canonical Mozilla ticket",
        "all_task_intersection_required": False,
        "components": contracts,
        "global_rules": [
            "Native task semantics must be preserved.",
            "Missing evidence is unavailable, not negative.",
            "No synthetic universal T8 target.",
            "No blind concatenation of heterogeneous task outputs.",
            "No arbitrary task weights.",
            "No incompatible probability averaging.",
            "No post-Creation information.",
            "Locked evaluation populations are not used for model selection.",
            "Overall triage remains evidence-based synthesis rather than "
            "supervised learning against a synthetic universal label.",
        ],
        "frozen_status": {
            "contracts_frozen": True,
            "training_performed": False,
            "prediction_generation_performed": False,
            "new_model_selected": False,
            "model_modified": False,
            "dataset_modified": False,
        },
    }

    OUTPUT.write_text(
        json.dumps(global_contract, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\nFrozen component contracts:")

    for name, contract in contracts.items():
        print(f"\n  {name}")
        print(f"    source task: {contract['source_task']}")
        print(f"    target: {contract['target']}")
        print(f"    output: {contract['output']}")
        print(
            "    prediction boundary: "
            f"{contract['prediction_boundary']}"
        )
        print(
            "    primary metrics: "
            + ", ".join(contract["primary_metrics"])
        )

    print("\nGlobal contract rules:")
    for rule in global_contract["global_rules"]:
        print(f"  - {rule}")

    print("\nFrozen status:")
    for key, value in global_contract["frozen_status"].items():
        print(f"  {key}: {value}")

    print(f"\nArtifact: {OUTPUT}")
    print("\nStatus: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()