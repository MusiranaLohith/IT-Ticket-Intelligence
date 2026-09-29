from pathlib import Path
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
OUT_DIR = ROOT / "modeling/T8/mod036"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = OUT_DIR / "t8_mod036_op015_trainable_component_design.json"


def main():
    print("=" * 80)
    print("T8 DECISION ENGINE — MOD-036 OP-015")
    print("Trainable Component Design")
    print("=" * 80)

    components = {
        "priority_component": {
            "output": "priority_recommendation",
            "supervision": {
                "status": "TRAINABLE",
                "target_source": "T2",
                "target": "native T2 priority target",
                "semantics": "Creation-boundary priority classification",
            },
            "allowed_inputs": [
                "T2 native priority evidence",
                "T3 secondary severity evidence",
                "Creation-boundary ticket information already permitted by T2/T3",
            ],
            "primary_role": (
                "Generate a machine recommendation for ticket priority "
                "while preserving T2 native priority semantics."
            ),
            "evaluation": [
                "native priority classification metrics",
                "macro-F1",
                "accuracy",
                "class-wise performance",
                "conflict-state analysis",
            ],
        },

        "assignment_component": {
            "output": "assignment_recommendation",
            "supervision": {
                "status": "TRAINABLE",
                "target_source": "T4",
                "target": "target_assignee",
                "semantics": (
                    "first valid assignment event strictly after Creation"
                ),
            },
            "allowed_inputs": [
                "T4 native retrieval evidence",
                "T1 category evidence",
                "T6 ranking evidence where semantically compatible",
                "Creation-boundary ticket information permitted by source tasks",
            ],
            "primary_role": (
                "Recommend an assignee or assignment group using the "
                "validated historical T4 assignment target and native "
                "retrieval evidence."
            ),
            "mandatory_constraints": [
                "Preserve T4 candidate-space policy.",
                "Do not use current assigned_to as a Creation-time feature.",
                "Do not use post-Creation assignment information.",
                "Do not convert unseen evaluation targets into negatives.",
                "Do not claim operational assignee eligibility.",
            ],
            "evaluation": [
                "top-1 recommendation accuracy",
                "top-k recommendation recall",
                "unseen-target handling",
                "candidate-space integrity",
            ],
        },

        "duplicate_component": {
            "output": "duplicate_recommendation",
            "supervision": {
                "status": "TRAINABLE",
                "target_source": "T5",
                "target": "native T5 duplicate target",
                "semantics": "Duplicate-ticket classification",
            },
            "allowed_inputs": [
                "T5 native duplicate evidence",
                "T4 retrieval evidence only where explicitly validated",
                "Creation-boundary ticket information",
            ],
            "primary_role": (
                "Generate a machine duplicate recommendation while "
                "preserving T5's native duplicate semantics."
            ),
            "mandatory_constraints": [
                "Preserve T5 calibration semantics.",
                "Do not reinterpret retrieval scores as duplicate probabilities.",
                "Do not use post-Creation information.",
            ],
            "evaluation": [
                "ROC-AUC",
                "average precision",
                "log loss",
                "calibration",
                "duplicate-class operating analysis",
            ],
        },

        "resolution_component": {
            "output": "resolution_context",
            "supervision": {
                "status": "TRAINABLE",
                "target_source": "T7",
                "target": "T7 time-to-resolution survival target",
                "semantics": (
                    "time-to-resolution with event/censoring semantics"
                ),
            },
            "allowed_inputs": [
                "T7 native survival evidence",
                "T2 priority evidence where explicitly justified",
                "T3 severity evidence where explicitly justified",
                "Creation-boundary ticket information",
            ],
            "primary_role": (
                "Produce resolution-time context while preserving T7 "
                "survival semantics."
            ),
            "mandatory_constraints": [
                "Preserve event/censoring semantics.",
                "Do not convert survival predictions into ordinary regression.",
                "Do not treat censored cases as ordinary negative labels.",
            ],
            "evaluation": [
                "C-index",
                "IPCW Brier score",
                "survival calibration where available",
                "event/censoring subgroup analysis",
            ],
        },

        "overall_triage_component": {
            "output": "overall_triage_recommendation",
            "supervision": {
                "status": "NOT_SUPERVISED_BY_UNIVERSAL_TARGET",
                "target_source": None,
                "target": None,
                "semantics": (
                    "structured synthesis of component recommendations "
                    "and supporting evidence"
                ),
            },
            "allowed_inputs": [
                "priority recommendation",
                "assignment recommendation",
                "duplicate recommendation",
                "resolution context",
                "T1-T7 supporting evidence",
                "cross-task conflict states",
                "evidence availability states",
            ],
            "primary_role": (
                "Synthesize component recommendations into a machine-"
                "generated overall triage recommendation without inventing "
                "a universal historical label."
            ),
            "implementation_policy": (
                "Evidence-based decision synthesis. The implementation "
                "must explicitly represent support, conflict, insufficient "
                "evidence, and unavailable evidence."
            ),
            "evaluation": [
                "component-level correctness",
                "cross-task consistency",
                "conflict handling",
                "missing-evidence handling",
                "decision traceability",
            ],
        },
    }

    architecture = {
        "operation": "MOD-036 OP-015",
        "purpose": (
            "Define which T8 decision components can be supervised and "
            "which must remain evidence-based because no authoritative "
            "historical target exists."
        ),

        "trainable_components": [
            "priority_component",
            "assignment_component",
            "duplicate_component",
            "resolution_component",
        ],

        "non_supervised_component": "overall_triage_component",

        "components": components,

        "development_population_policy": {
            "primary_unit": "canonical Mozilla ticket",
            "prediction_boundary": "Creation",
            "all_task_intersection_required": False,
            "missing_evidence": "unavailable, not negative",
            "post_creation_information_allowed": False,
        },

        "cross_task_learning_policy": {
            "principle": (
                "A task may use another task's evidence only when the "
                "supporting evidence is semantically compatible with the "
                "decision target and respects the source task's boundary."
            ),
            "forbidden": [
                "blind feature concatenation",
                "arbitrary task weights",
                "incompatible probability averaging",
                "synthetic universal target",
                "post-Creation features",
            ],
        },

        "overall_decision_policy": {
            "machine_recommendation_required": True,
            "human_review": True,
            "human_replaces_machine": False,
            "universal_scalar_required": False,
        },

        "modeling_sequence": [
            "freeze component contracts",
            "construct leakage-safe development inputs",
            "establish component baselines",
            "evaluate native evidence",
            "test justified cross-task supporting evidence",
            "perform robustness analysis",
            "freeze validated component implementations",
            "implement overall evidence-based decision synthesis",
        ],

        "controls": {
            "training_performed": False,
            "prediction_generation_performed": False,
            "new_model_selected": False,
            "model_modified": False,
            "dataset_modified": False,
        },
    }

    OUTPUT.write_text(
        json.dumps(architecture, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\nTrainable components:")
    for name in architecture["trainable_components"]:
        component = components[name]
        print(
            f"  {name}: "
            f"{component['supervision']['status']}"
        )

    print("\nNon-supervised component:")
    print(f"  {architecture['non_supervised_component']}")

    print("\nT8 outputs:")
    for name, component in components.items():
        print(f"  {component['output']}")

    print("\nModeling sequence:")
    for i, step in enumerate(
        architecture["modeling_sequence"],
        start=1,
    ):
        print(f"  {i}. {step}")

    print("\nControls:")
    for key, value in architecture["controls"].items():
        print(f"  {key}: {value}")

    print(f"\nArtifact: {OUTPUT}")
    print("\nStatus: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()