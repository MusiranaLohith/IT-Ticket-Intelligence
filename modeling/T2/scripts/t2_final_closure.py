from pathlib import Path
import json


# ============================================================
# T2-MOD-022
# Final T2 Task Suitability & Closure
#
# Evidence synthesis only.
# No training.
# No refitting.
# No test tuning.
# No dataset modification.
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_ROOT = PROJECT_ROOT / "modeling" / "T2"

ANALYSIS_DIR = T2_ROOT / "analysis"
CONTRACTS_DIR = T2_ROOT / "contracts"

OUTPUT_FILE = (
    ANALYSIS_DIR
    / "t2_final_closure.json"
)

GENERALIZATION_FILE = (
    ANALYSIS_DIR
    / "t2_final_generalization_analysis.json"
)

FINAL_SELECTION_FILE = (
    ANALYSIS_DIR
    / "t2_final_model_selection.json"
)

BASELINE_COMPARISON_FILE = (
    ANALYSIS_DIR
    / "t2_baseline_comparison.json"
)

ADVANCED_CLOSURE_FILE = (
    ANALYSIS_DIR
    / "t2_advanced_branch_closure.json"
)

MODEL_CONTRACT_FILE = (
    CONTRACTS_DIR
    / "t2_model_contract.json"
)


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(
            f"REQUIRED_ARTIFACT_NOT_FOUND={path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def main():

    print("T2_MOD_022_START")

    ANALYSIS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Load completed evidence.
    # --------------------------------------------------------

    generalization = load_json(
        GENERALIZATION_FILE
    )

    final_selection = load_json(
        FINAL_SELECTION_FILE
    )

    baseline_comparison = load_json(
        BASELINE_COMPARISON_FILE
    )

    advanced_closure = load_json(
        ADVANCED_CLOSURE_FILE
    )

    model_contract = load_json(
        MODEL_CONTRACT_FILE
    )

    # --------------------------------------------------------
    # Frozen task facts.
    # --------------------------------------------------------

    eligible_population = 29498

    target_classes = [
        "P1",
        "P2",
        "P3",
        "P4",
        "P5",
    ]

    target_counts = {
        "P1": 7325,
        "P2": 9156,
        "P3": 11015,
        "P4": 784,
        "P5": 1218,
    }

    prediction_boundary = (
        "Creation"
    )

    admitted_features = [
        "Summary",
        "Description",
    ]

    excluded_feature_categories = [
        "post-Creation administrative information",
        "current mutable state",
        "final-state backfill",
        "target-derived information",
        "future information",
        "fabricated historical information",
    ]

    # --------------------------------------------------------
    # Final selected model.
    # --------------------------------------------------------

    selected_model = {
        "operation": "T2-MOD-007",
        "name": (
            "TF-IDF + Class-Weighted "
            "Logistic Regression"
        ),
        "selection_basis": (
            "validation macro-F1 with "
            "minority-class performance considered"
        ),
        "final_model_selected": True,
    }

    # --------------------------------------------------------
    # Final test evidence.
    # --------------------------------------------------------

    test = generalization["test"]

    test_metrics = {
        "accuracy": test["accuracy"],
        "macro_f1": test["macro_f1"],
        "weighted_f1": test["weighted_f1"],
    }

    test_per_class = (
        generalization["test_per_class"]
    )

    # --------------------------------------------------------
    # Suitability assessment.
    # --------------------------------------------------------

    strengths = [
        (
            "The T2 target has an explicit temporal "
            "definition: first valid P1-P5 Priority "
            "assigned after Creation and within the "
            "following 24 hours."
        ),
        (
            "The prediction boundary is Creation, "
            "preserving the intended incoming-ticket "
            "decision boundary."
        ),
        (
            "The modeling features are restricted to "
            "Creation-time Summary and Description."
        ),
        (
            "A chronological train/validation/test "
            "split was used."
        ),
        (
            "The locked test set was evaluated only "
            "after model selection."
        ),
        (
            "The final evaluation was performed "
            "without retraining or refitting."
        ),
        (
            "The model provides measurable signal "
            "for priority prediction, especially "
            "for the more represented classes."
        ),
    ]

    limitations = [
        (
            "Overall five-class predictive performance "
            "is limited: final test accuracy is "
            "42.0113% and macro-F1 is 26.4960%."
        ),
        (
            "Minority-class performance is very weak, "
            "with P4 F1=4.1237% and P5 F1=6.7340%."
        ),
        (
            "Performance decreases from validation "
            "to the later locked test period."
        ),
        (
            "The dominant error paths involve confusion "
            "among P1, P2, and P3."
        ),
        (
            "The evidence does not justify treating "
            "the model as a fully autonomous priority "
            "assignment system."
        ),
        (
            "A universal automated confidence threshold "
            "has not been empirically established."
        ),
    ]

    # --------------------------------------------------------
    # System role.
    # --------------------------------------------------------

    system_role = (
        "SECONDARY_DECISION_SUPPORT_SIGNAL"
    )

    system_role_description = (
        "T2 is suitable as a secondary, "
        "confidence-aware priority prediction "
        "signal within the integrated IT Ticket "
        "Intelligence system. It should assist "
        "triage and downstream evidence fusion, "
        "but should not independently determine "
        "final ticket priority."
    )

    # --------------------------------------------------------
    # What T2 supports.
    # --------------------------------------------------------

    supported_claims = [
        (
            "A leakage-controlled five-class "
            "priority prediction experiment "
            "can be performed on Mozilla CORE."
        ),
        (
            "Creation-time Summary and Description "
            "contain predictive signal for the "
            "subsequent 24-hour priority outcome."
        ),
        (
            "The selected model generalizes to a "
            "later chronological test period, "
            "although with degraded performance."
        ),
        (
            "Priority prediction is substantially "
            "harder for P4 and P5 than for the "
            "more represented priority classes."
        ),
        (
            "T2 can contribute one evidence channel "
            "to a larger confidence-aware triage "
            "system."
        ),
    ]

    unsupported_claims = [
        (
            "T2 does not support claiming highly "
            "accurate autonomous five-class "
            "priority assignment."
        ),
        (
            "T2 does not support claiming reliable "
            "prediction of P4 or P5."
        ),
        (
            "T2 does not support automatic action "
            "at a fixed confidence threshold "
            "without further empirical calibration "
            "and policy evaluation."
        ),
        (
            "T2 does not establish that predicted "
            "priority should replace human priority "
            "judgment."
        ),
    ]

    # --------------------------------------------------------
    # Integrity checks.
    # --------------------------------------------------------

    integrity = {
        "training_in_closure": False,
        "refitting_in_closure": False,
        "test_tuning_in_closure": False,
        "dataset_modified": False,
        "new_labels_created": False,
        "future_features_added": False,
        "target_derived_features_added": False,
        "advanced_branch_reopened": False,
    }

    # --------------------------------------------------------
    # Final decision.
    # --------------------------------------------------------

    decision = (
        "SUPPORTED_WITH_LIMITATIONS"
    )

    closure_status = "CLOSED"

    # --------------------------------------------------------
    # Formal report.
    # --------------------------------------------------------

    report = {

        "operation": "T2-MOD-022",

        "operation_name": (
            "Final T2 Task Suitability & Closure"
        ),

        "task": "T2",

        "task_name": (
            "Priority Prediction"
        ),

        "dataset": {
            "name": "Mozilla CORE",
            "eligible_population": (
                eligible_population
            ),
            "target": (
                "first valid P1-P5 Priority "
                "assigned strictly after Creation "
                "and within following 24 hours"
            ),
            "target_field": "target_priority",
            "semantic_target": "priority",
            "classes": target_classes,
            "class_counts": target_counts,
        },

        "prediction_boundary": (
            prediction_boundary
        ),

        "admitted_features": (
            admitted_features
        ),

        "excluded_features": (
            excluded_feature_categories
        ),

        "final_model": selected_model,

        "final_test": {
            "rows": test["rows"],
            "accuracy": test_metrics[
                "accuracy"
            ],
            "macro_f1": test_metrics[
                "macro_f1"
            ],
            "weighted_f1": test_metrics[
                "weighted_f1"
            ],
            "per_class": test_per_class,
        },

        "generalization": {
            "validation_accuracy": (
                generalization[
                    "validation"
                ]["accuracy"]
            ),
            "test_accuracy": (
                test_metrics["accuracy"]
            ),
            "accuracy_change_pp": (
                generalization[
                    "generalization_change"
                ][
                    "accuracy_change_percentage_points"
                ]
            ),

            "validation_macro_f1": (
                generalization[
                    "validation"
                ]["macro_f1"]
            ),
            "test_macro_f1": (
                test_metrics["macro_f1"]
            ),
            "macro_f1_change_pp": (
                generalization[
                    "generalization_change"
                ][
                    "macro_f1_change_percentage_points"
                ]
            ),

            "validation_weighted_f1": (
                generalization[
                    "validation"
                ]["weighted_f1"]
            ),
            "test_weighted_f1": (
                test_metrics["weighted_f1"]
            ),
            "weighted_f1_change_pp": (
                generalization[
                    "generalization_change"
                ][
                    "weighted_f1_change_percentage_points"
                ]
            ),
        },

        "system_role": {
            "decision": system_role,
            "description": system_role_description,
        },

        "suitability_decision": decision,

        "strengths": strengths,

        "limitations": limitations,

        "supported_claims": supported_claims,

        "unsupported_claims": unsupported_claims,

        "integrity": integrity,

        "evidence_dependencies": {
            "model_contract": (
                model_contract.get(
                    "status",
                    model_contract.get(
                        "contract_status",
                        "AVAILABLE",
                    ),
                )
            ),
            "baseline_comparison": (
                baseline_comparison.get(
                    "status",
                    "AVAILABLE",
                )
            ),
            "advanced_branch": (
                advanced_closure.get(
                    "status",
                    "AVAILABLE",
                )
            ),
            "final_model_selection": (
                final_selection.get(
                    "status",
                    "AVAILABLE",
                )
            ),
            "generalization_analysis": (
                generalization.get(
                    "status",
                    "AVAILABLE",
                )
            ),
        },

        "final_conclusion": (
            "Mozilla CORE is suitable for T2 "
            "priority-prediction modeling under "
            "the frozen Creation-time target and "
            "feature boundary. The final "
            "TF-IDF + Class-Weighted Logistic "
            "Regression model demonstrates "
            "measurable but limited predictive "
            "performance on the locked chronological "
            "test period. Because minority-class "
            "performance is weak and generalization "
            "degrades on the later period, T2 is "
            "closed as a supported secondary "
            "decision-support signal rather than "
            "an autonomous priority assignment "
            "component."
        ),

        "closure_status": closure_status,

        "next_system_use": (
            "Retain the T2 prediction as one "
            "evidence channel for later "
            "confidence-aware fusion and "
            "human-review policy development. "
            "Do not independently automate final "
            "priority assignment from T2."
        ),
    }

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            report,
            f,
            indent=2,
        )

    # --------------------------------------------------------
    # Console summary.
    # --------------------------------------------------------

    print(
        "TASK=T2_PRIORITY_PREDICTION"
    )

    print(
        "DATASET=Mozilla_CORE"
    )

    print(
        "ELIGIBLE_POPULATION="
        f"{eligible_population}"
    )

    print(
        "TARGET_CLASSES="
        + ",".join(target_classes)
    )

    print(
        "PREDICTION_BOUNDARY=Creation"
    )

    print(
        "ADMITTED_FEATURES=Summary,Description"
    )

    print(
        "FINAL_MODEL=T2-MOD-007"
    )

    print(
        "FINAL_TEST_ACCURACY="
        f"{test_metrics['accuracy']:.6f}"
    )

    print(
        "FINAL_TEST_MACRO_F1="
        f"{test_metrics['macro_f1']:.6f}"
    )

    print(
        "FINAL_TEST_WEIGHTED_F1="
        f"{test_metrics['weighted_f1']:.6f}"
    )

    print(
        "P4_F1="
        f"{test_per_class['P4']['f1']:.6f}"
    )

    print(
        "P5_F1="
        f"{test_per_class['P5']['f1']:.6f}"
    )

    print(
        "SUITABILITY_DECISION="
        f"{decision}"
    )

    print(
        "SYSTEM_ROLE="
        f"{system_role}"
    )

    print(
        "TRAINING=False"
    )

    print(
        "REFITTING=False"
    )

    print(
        "TEST_TUNING=False"
    )

    print(
        "DATASET_MODIFIED=False"
    )

    print(
        "STATUS="
        f"{closure_status}"
    )

    print(
        "OUTPUT="
        f"{OUTPUT_FILE}"
    )

    print(
        "T2_MOD_022_COMPLETE"
    )


if __name__ == "__main__":
    main()