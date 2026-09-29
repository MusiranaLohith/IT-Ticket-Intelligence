#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
OUT = ROOT / "modeling/FMP/metrics/fmp02_t2_t7_inference_manifest.json"


def p(relative: str) -> str:
    return str(ROOT / relative)


MANIFEST = {
    "phase": "FMP-02",
    "artifact": "T2-T7 inference hardening manifest",
    "status": "DRAFT_FOR_VALIDATION",
    "purpose": (
        "Machine-readable description of retained T2-T7 inference components "
        "and native task semantics. This manifest does not create a universal "
        "prediction space."
    ),

    "global_constraints": {
        "universal_probability_averaging": False,
        "arbitrary_cross_task_weights": False,
        "synthetic_universal_target": False,
        "universal_confidence_score": False,
        "missing_evidence_is_negative": False,
        "native_task_semantics_preserved": True,
        "locked_test_metrics_unchanged": True,
        "evaluation_used_for_new_model_selection": False,
    },

    "tasks": {

        "T2": {
            "name": "Priority",
            "status": "CLOSED",
            "final_model": "T2-MOD-007",
            "artifact": p(
                "modeling/T2/models/t2_class_weighted_tfidf_logreg.joblib"
            ),
            "closure": p(
                "modeling/T2/analysis/t2_final_closure.json"
            ),
            "input_boundary": "Creation-time ticket text fields permitted by T2 contract",
            "output_type": "multiclass_classification",
            "output_semantics": "Predicted priority class P1-P5",
            "probability_semantics": "Native classifier probabilities only; not a universal confidence measure",
            "calibration_status": "Not established as a universal operational confidence layer",
            "system_role": "SECONDARY_DECISION_SUPPORT_SIGNAL",
            "autonomous_use": False,
            "known_limitations": [
                "Chronological validation-to-test degradation is documented.",
                "P4 and P5 performance is substantially weaker than majority classes.",
                "No autonomous priority assignment is supported.",
            ],
        },

        "T3": {
            "name": "Severity",
            "status": "CLOSED",
            "final_model": "T3-MOD-008",
            "artifact": p(
                "modeling/T3/models/t3_class_weighted_tfidf_logreg.joblib"
            ),
            "closure": p(
                "modeling/T3/analysis/t3_final_closure.json"
            ),
            "input_boundary": "Creation-time ticket text fields permitted by T3 contract",
            "output_type": "multiclass_classification",
            "output_semantics": "Predicted severity class S1-S4",
            "probability_semantics": "Native classifier output only; not a universal confidence measure",
            "calibration_status": "No universal operational confidence layer",
            "system_role": "SECONDARY_DECISION_SUPPORT_SIGNAL",
            "autonomous_use": False,
            "known_limitations": [
                "Locked-test macro F1 is substantially lower than weighted F1.",
                "S1 has very small locked-test support.",
                "DistilBERT feasibility branch was closed and is not the retained model.",
            ],
        },

        "T4": {
            "name": "Historical Routing / Assignment Retrieval",
            "status": "SUPPORTED_WITH_LIMITATIONS",
            "final_model": "T4-MOD-014 / retained retrieval evidence",
            "artifacts": [
                p(
                    "modeling/T4/results/mod007_checkpoints/t4_mod007_tfidf.joblib"
                ),
                p(
                    "modeling/T4/results/mod007_checkpoints/t4_mod007_neighbors.joblib"
                ),
                p(
                    "modeling/T4/results/r1_checkpoints/t4_r1_tfidf.joblib"
                ),
                p(
                    "modeling/T4/results/r1_checkpoints/t4_r1_linear_svc.joblib"
                ),
            ],
            "closure": p(
                "modeling/T4/results/t4_mod013_closure.json"
            ),
            "input_boundary": "Ticket fields permitted by T4 historical retrieval contract",
            "output_type": "ranking",
            "output_semantics": "Historically observed assignee candidates ranked by retrieval evidence",
            "probability_semantics": "None",
            "calibration_status": "Not applicable",
            "system_role": "SECONDARY_DECISION_SUPPORT_SIGNAL",
            "autonomous_use": False,
            "known_limitations": [
                "Historical retrieval is not operational eligibility.",
                "Historical retrieval is not proof of current routing correctness.",
                "Open-world unseen targets cannot be retrieved.",
                "Coverage and Hit@20 limitations remain documented.",
            ],
        },

        "T5": {
            "name": "Duplicate Detection",
            "status": "SUPPORTED_WITH_LIMITATIONS",
            "final_model": "T5-MOD-007 calibrated pipeline",
            "artifacts": [
                p(
                    "modeling/T5/models/t5_mod005_tfidf.joblib"
                ),
                p(
                    "modeling/T5/models/t5_mod005_logreg.joblib"
                ),
                p(
                    "modeling/T5/models/t5_mod007_calibrated_tfidf.joblib"
                ),
                p(
                    "modeling/T5/models/t5_mod007_calibration_models.joblib"
                ),
            ],
            "closure": p(
                "modeling/T5/metrics/t5_mod011_final_closure.json"
            ),
            "input_boundary": (
                "Creator, Creator Detail, Summary and Description "
                "within the documented Creation-time boundary"
            ),
            "output_type": "binary_relationship_probability",
            "output_semantics": (
                "p_duplicate for existence of an observed post-Creation "
                "'Dupe of' relationship"
            ),
            "probability_semantics": (
                "Native calibrated duplicate probability under the retained "
                "task definition; not a universal confidence score"
            ),
            "calibration_status": "Task-specific sigmoid calibration retained",
            "system_role": "SECONDARY_DECISION_SUPPORT_SIGNAL",
            "autonomous_use": False,
            "known_limitations": [
                "The target establishes relationship existence, not target-ticket identification.",
                "Provenance limitation is retained.",
                "The descriptive 0.5 threshold is not an operational threshold.",
                "Human review removal is not supported.",
            ],
        },

        "T6": {
            "name": "Similar / Duplicate-Related Ticket Retrieval",
            "status": "CLOSED_SUPPORTED_WITH_LIMITATIONS",
            "final_model": "T6-MOD-010 corrected hybrid lexical + semantic retrieval",
            "artifacts": [
                p(
                    "modeling/T6/models/t6_mod004_tfidf_vectorizer.joblib"
                ),
                p(
                    "modeling/T6/metrics/t6_mod010_corrected_hybrid_results.json"
                ),
                p(
                    "modeling/T6/metrics/t6_mod010_corrected_hybrid_query_rankings.csv"
                ),
                p(
                    "modeling/T6/metrics/t6_mod010_direct_score_reconciliation.json"
                ),
            ],
            "implementation_scripts": [
                p(
                    "modeling/T6/scripts/t6_mod008_semantic_failure_retrieval.py"
                ),
                p(
                    "modeling/T6/scripts/t6_mod009_hybrid_lexical_semantic_retrieval.py"
                ),
            ],
            "input_boundary": "Query and frozen candidate pool defined by T6 contract",
            "output_type": "ranking",
            "output_semantics": (
                "Ranked similar/duplicate-related ticket candidates "
                "using corrected hybrid lexical + semantic retrieval"
            ),
            "probability_semantics": "None",
            "calibration_status": "Not applicable",
            "system_role": "SECONDARY_DECISION_SUPPORT_SIGNAL",
            "autonomous_use": False,
            "known_limitations": [
                "Observable non-positive candidates are not true negatives.",
                "Candidate pool and ranking semantics are frozen.",
                "No probability interpretation is permitted.",
                "No universal automation threshold is established.",
            ],
        },

        "T7": {
            "name": "Resolution-Time Survival",
            "status": "CLOSED_SUPPORTED_WITH_LIMITATIONS",
            "final_model": "T7-MOD-010 Log-Normal AFT",
            "model_specification": p(
                "modeling/T7/metrics/t7_mod010_log_normal_aft_model.json"
            ),
            "comparison_specification": p(
                "modeling/T7/metrics/t7_mod011_final_model_comparison_audit.json"
            ),
            "weibull_reference_specification": p(
                "modeling/T7/metrics/t7_mod007_weibull_aft_model.json"
            ),
            "evaluation_predictions": p(
                "modeling/T7/derived/t7_mod010_evaluation_predictions.csv"
            ),
            "closure": p(
                "modeling/T7/metrics/t7_mod012_final_closure.json"
            ),
            "implementation_script": p(
                "modeling/T7/scripts/t7_mod010_log_normal_aft_baseline.py"
            ),
            "input_boundary": "Creation-time features permitted by T7 temporal contract",
            "output_type": "survival_model",
            "output_semantics": (
                "Time-to-resolution quantities under right-censoring semantics"
            ),
            "probability_semantics": (
                "Survival quantities are native survival-model outputs and "
                "are not cross-task confidence scores"
            ),
            "calibration_status": (
                "No formal IPCW survival calibration suitable for autonomous "
                "production use was established"
            ),
            "system_role": "SECONDARY_DECISION_SUPPORT_SIGNAL",
            "autonomous_use": False,
            "known_limitations": [
                "Unresolved observations are right-censored, not negative duration targets.",
                "Log-Normal AFT did not uniformly dominate reference survival baselines.",
                "No validated automation threshold exists.",
                "Current artifact is specification-based rather than a serialized estimator.",
            ],
        },
    },
}


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    OUT.write_text(
        json.dumps(MANIFEST, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("=" * 80)
    print("FMP-02 / OPERATION 6")
    print("T2-T7 INFERENCE MANIFEST")
    print("=" * 80)
    print()
    print("Manifest written:")
    print(OUT)
    print()
    print("Tasks documented:")
    for task in MANIFEST["tasks"]:
        print(f"  {task}: {MANIFEST['tasks'][task]['name']}")
    print()
    print("Global controls:")
    for key, value in MANIFEST["global_constraints"].items():
        print(f"  {key}: {value}")
    print()
    print("No prediction generated.")
    print("No retraining performed.")
    print("No evaluation data used for selection.")
    print("No existing artifact modified.")
    print()
    print("STATUS: COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()