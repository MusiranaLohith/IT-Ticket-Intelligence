from pathlib import Path
import json


MODELING_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = MODELING_DIR.parent

OUTPUT_DIR = MODELING_DIR / "project_consolidation"
OUTPUT_FILE = OUTPUT_DIR / "t1_t5_consolidated_evidence.json"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # T1
    # ------------------------------------------------------------------

    t1_it_support = load_json(
        MODELING_DIR
        / "T1"
        / "baselines"
        / "t1_it_support_char_svm_report.json"
    )

    t1_vscode = load_json(
        MODELING_DIR
        / "T1"
        / "baselines"
        / "t1_vscode_model_compare_report.json"
    )

    t1_vscode_contract = load_json(
        MODELING_DIR
        / "T1"
        / "contracts"
        / "t1_vscode_contract.json"
    )

    # ------------------------------------------------------------------
    # T2-T5
    # ------------------------------------------------------------------

    t2 = load_json(
        MODELING_DIR
        / "T2"
        / "analysis"
        / "t2_final_closure.json"
    )

    t3 = load_json(
        MODELING_DIR
        / "T3"
        / "analysis"
        / "t3_final_closure.json"
    )

    t4 = load_json(
        MODELING_DIR
        / "T4"
        / "results"
        / "t4_mod013_closure.json"
    )

    t5 = load_json(
        MODELING_DIR
        / "T5"
        / "metrics"
        / "t5_mod011_final_closure.json"
    )

    # ------------------------------------------------------------------
    # Consolidated evidence record
    # ------------------------------------------------------------------

    consolidated = {
        "project": {
            "name": "IT Ticket Intelligence / IT Ticket Triage System",
            "purpose": (
                "Controlled evidence-first modeling consolidation across "
                "T1-T5 completed task investigations."
            ),
            "project_root": str(PROJECT_ROOT),
            "raw_datasets_modified": False,
            "synthetic_data_used": False,
            "project_level_model_freeze": False,
        },

        "consolidation_status": "COMPLETE",

        # ==============================================================
        # T1
        # ==============================================================

        "t1": {
            "task": "Incoming IT-ticket classification",

            "it_support": {
                "status": "FINAL_CANDIDATE_ESTABLISHED",
                "formal_model_freeze": False,

                "source_artifact": (
                    "modeling/T1/baselines/"
                    "t1_it_support_char_svm_report.json"
                ),

                "model": t1_it_support.get("model"),

                "accuracy": t1_it_support.get(
                    "overall", {}
                ).get("accuracy"),

                "macro_f1": t1_it_support.get(
                    "overall", {}
                ).get("macro_f1"),

                "weighted_f1": t1_it_support.get(
                    "overall", {}
                ).get("weighted_f1"),

                "evaluation_used_for_fit": t1_it_support.get(
                    "evaluation_used_for_fit"
                ),

                "interpretation": (
                    "Controlled modeling established a final candidate. "
                    "However, the available T1 contract does not contain "
                    "a formal model-freeze state."
                ),
            },

            "vscode": {
                "status": "MODEL_COMPARISON_COMPLETE",
                "formal_model_freeze": False,

                "decision_status": t1_vscode.get(
                    "decision_status"
                ),

                "source_artifact": (
                    "modeling/T1/baselines/"
                    "t1_vscode_model_compare_report.json"
                ),

                "evaluation_used_for_fit": t1_vscode.get(
                    "evaluation_used_for_fit"
                ),

                "comparison": {
                    "model": t1_vscode.get("model"),
                    "accuracy": t1_vscode.get("accuracy"),
                    "macro_f1": t1_vscode.get("macro_f1"),
                    "weighted_f1": t1_vscode.get("weighted_f1"),
                },

                "evaluation_class_counts": t1_vscode.get(
                    "class_counts"
                ),

                "missing_evaluation_classes": (
                    t1_vscode.get("missing_evaluation_classes")
                    or ["Usability"]
                ),

                "contract_model_selected": (
                    t1_vscode_contract
                    .get("modeling_status", {})
                    .get("model_selected")
                ),

                "interpretation": (
                    "Baseline/model comparison was completed, but the "
                    "comparison artifact explicitly records "
                    "MODEL_NOT_FROZEN. The evaluation partition contains "
                    "zero Usability examples."
                ),
            },

            "project_role": "INCOMING_TICKET_CLASSIFICATION_SIGNAL",
        },

        # ==============================================================
        # T2
        # ==============================================================

        "t2": {
            "task": "Priority Prediction",
            "source_artifact": (
                "modeling/T2/analysis/t2_final_closure.json"
            ),
            "closure": t2,
        },

        # ==============================================================
        # T3
        # ==============================================================

        "t3": {
            "task": "Severity Prediction",
            "source_artifact": (
                "modeling/T3/analysis/t3_final_closure.json"
            ),
            "closure": t3,
        },

        # ==============================================================
        # T4
        # ==============================================================

        "t4": {
            "task": "Routing / Assignment / Specific Assignee Prediction",
            "source_artifact": (
                "modeling/T4/results/t4_mod013_closure.json"
            ),
            "closure": t4,
        },

        # ==============================================================
        # T5
        # ==============================================================

        "t5": {
            "task": "Binary Duplicate Detection",
            "source_artifact": (
                "modeling/T5/metrics/t5_mod011_final_closure.json"
            ),
            "closure": t5,
        },

        # ==============================================================
        # Project-level interpretation
        # ==============================================================

        "project_level_interpretation": {
            "evidence_model": (
                "T1-T5 are retained as distinct task-specific signals. "
                "They are not treated as a single universally calibrated "
                "score or as automatically interchangeable predictions."
            ),

            "system_role": (
                "The completed modeling evidence supports a multi-signal "
                "decision-support architecture rather than autonomous "
                "ticket triage."
            ),

            "human_review": (
                "Human review remains necessary where task evidence shows "
                "class imbalance, temporal degradation, unseen entities, "
                "missing evaluation support, low minority performance, "
                "calibration limitations, or unresolved operational "
                "threshold requirements."
            ),

            "deployment_claim": (
                "No project-level autonomous deployment claim is established "
                "by T1-T5 alone."
            ),
        },

        # ==============================================================
        # Integrity controls
        # ==============================================================

        "integrity_controls": {
            "raw_source_modification": False,
            "synthetic_labels": False,
            "future_information_used": False,
            "silent_cross_dataset_merge": False,
            "evaluation_reuse_for_model_selection": False,
            "unsupported_operational_threshold_claim": False,
            "universal_confidence_score_claim": False,
        },
    }

    # ------------------------------------------------------------------
    # Write output
    # ------------------------------------------------------------------

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(consolidated, f, indent=2)

    print("PROJECT-LEVEL T1-T5 CONSOLIDATION")
    print("=" * 72)
    print(f"Project root : {PROJECT_ROOT}")
    print(f"Modeling dir : {MODELING_DIR}")
    print(f"Output       : {OUTPUT_FILE}")
    print()

    print(
        "T1 IT Support : "
        "FINAL CANDIDATE ESTABLISHED / NOT FORMALLY FROZEN"
    )

    print(
        "T1 VS Code    : "
        "MODEL COMPARISON COMPLETE / MODEL NOT FROZEN"
    )

    print("T2            : CLOSED")
    print("T3            : CLOSED")
    print("T4            : CLOSED")
    print("T5            : CLOSED")
    print()

    print("Project-level model freeze : FALSE")
    print("Raw datasets modified      : FALSE")
    print("Synthetic data used        : FALSE")
    print()
    print("Consolidation artifact written successfully.")


if __name__ == "__main__":
    main()