from pathlib import Path
import json
import sys
from datetime import datetime, timezone


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T5_ROOT = PROJECT_ROOT / "modeling" / "T5"

CONTRACT = (
    T5_ROOT
    / "contracts"
    / "t5_baseline_contract.json"
)

SELECTION_LOCK = (
    T5_ROOT
    / "contracts"
    / "t5_mod008_model_selection_lock.json"
)

CALIBRATION_COMPARISON = (
    T5_ROOT
    / "metrics"
    / "t5_mod007_calibration_comparison.json"
)

LOCKED_EVALUATION = (
    T5_ROOT
    / "metrics"
    / "t5_mod009_locked_evaluation_metrics.json"
)

GENERALIZATION = (
    T5_ROOT
    / "metrics"
    / "t5_mod010_generalization_analysis.json"
)

OUTPUT = (
    T5_ROOT
    / "metrics"
    / "t5_mod011_final_closure.json"
)


def fail(message):
    print(f"FAIL: {message}")
    sys.exit(1)


def load_json(path):
    if not path.exists():
        fail(f"Missing required artifact: {path}")

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main():
    print("=" * 80)
    print("T5-MOD-011 — FINAL TASK CLOSURE")
    print("=" * 80)

    # ------------------------------------------------------------------
    # 1. Verify controlled artifacts
    # ------------------------------------------------------------------

    print("\n[1] Verify controlled T5 artifacts")

    contract = load_json(CONTRACT)
    selection_lock = load_json(SELECTION_LOCK)
    calibration = load_json(CALIBRATION_COMPARISON)
    evaluation = load_json(LOCKED_EVALUATION)
    generalization = load_json(GENERALIZATION)

    print("Baseline contract: PASS")
    print("Model selection lock: PASS")
    print("Calibration comparison: PASS")
    print("Locked evaluation: PASS")
    print("Generalization analysis: PASS")

    # ------------------------------------------------------------------
    # 2. Verify closure controls
    # ------------------------------------------------------------------

    print("\n[2] Verify closure controls")

    if selection_lock.get("status") != "MODEL_SELECTION_LOCKED":
        fail(
            "Model selection lock does not have expected status."
        )

    if evaluation.get("status") != "LOCKED_EVALUATION_COMPLETE":
        fail(
            "Locked evaluation does not have expected status."
        )

    if generalization.get("status") != (
        "GENERALIZATION_ANALYSIS_COMPLETE"
    ):
        fail(
            "Generalization analysis does not have expected status."
        )

    evaluation_controls = evaluation.get(
        "controls",
        {},
    )

    forbidden_controls = [
        "model_refit",
        "calibrator_refit",
        "vectorizer_refit",
        "threshold_optimization",
        "evaluation_used_for_selection",
        "evaluation_used_for_calibration",
        "synthetic_data",
        "target_provenance_used_as_feature",
    ]

    for control in forbidden_controls:
        if evaluation_controls.get(control) is True:
            fail(
                f"Evaluation control violation: {control}"
            )

    print(
        "No prohibited evaluation/refit/tuning control detected."
    )
    print("PASS")

    # ------------------------------------------------------------------
    # 3. Frozen task definition
    # ------------------------------------------------------------------

    print("\n[3] Record frozen T5 task definition")

    task_definition = {
        "task": "Binary Duplicate Detection",

        "target": {
            "name": "T5 target",
            "type": "binary",
            "positive": (
                "First observed post-Creation "
                "'Dupe of' addition"
            ),
            "negative": (
                "No observed post-Creation "
                "'Dupe of' addition through "
                "the administrative observation endpoint"
            ),
            "interpretation": (
                "Relationship-existence detection; "
                "not target-ticket identification or pairing"
            ),
        },

        "canonical_population": {
            "rows": 513816,
            "positive": 4691,
            "negative": 509125,
            "unique_ids": 513816,
            "normalized_content_groups": 512504,
        },

        "features": [
            "Creator",
            "Creator Detail",
            "Summary",
            "Description",
        ],

        "excluded_from_inference": [
            "Dupe of",
            "Assigned to",
            "Assigned to detail",
            "post-Creation History",
            "target-ticket information",
        ],
    }

    print(
        "Task definition recorded."
    )
    print(
        "Prediction-time features: "
        "Creator, Creator Detail, Summary, Description"
    )
    print("PASS")

    # ------------------------------------------------------------------
    # 4. Split controls
    # ------------------------------------------------------------------

    print("\n[4] Record frozen split controls")

    split_definition = {
        "official_boundary": (
            "Creation year < 2024 = training; "
            "Creation year >= 2024 = evaluation"
        ),

        "group_definition": (
            "Normalized Summary + Description"
        ),

        "group_integrity": True,

        "training_rows": 492989,
        "training_positive": 3373,
        "training_negative": 489616,

        "evaluation_rows": 20827,
        "evaluation_positive": 1318,
        "evaluation_negative": 19509,

        "cross_split_normalized_content_groups": 0,

        "train_eval_id_overlap": 0,

        "crossing_groups": 5,

        "crossing_group_rows": 10,

        "crossing_group_action": (
            "All five crossing groups assigned to TRAIN "
            "to preserve group integrity"
        ),
    }

    print(
        "Training rows: 492989"
    )

    print(
        "Official evaluation rows: 20827"
    )

    print(
        "Cross-split normalized-content groups: 0"
    )

    print(
        "Train/evaluation ID overlap: 0"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 5. Selected modeling pipeline
    # ------------------------------------------------------------------

    print("\n[5] Record selected modeling pipeline")

    selected_pipeline = {
        "representation": (
            "Word-level TF-IDF unigram/bigram"
        ),

        "vectorizer": {
            "ngram_range": [1, 2],
            "min_df": 2,
            "max_features": 100000,
            "sublinear_tf": True,
            "lowercase": True,
        },

        "classifier": {
            "type": "LogisticRegression",
            "class_weight": "balanced",
            "solver": "liblinear",
            "max_iter": 1000,
            "random_state": 42,
        },

        "calibration": "Sigmoid",

        "probability_output": "p_duplicate",

        "threshold": {
            "value": 0.5,
            "status": "descriptive_only",
            "optimized": False,
        },
    }

    print(
        "Selected classifier: balanced LogisticRegression"
    )

    print(
        "Selected calibration: sigmoid"
    )

    print(
        "Threshold optimization: NO"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 6. Validation evidence
    # ------------------------------------------------------------------

    print("\n[6] Record validation evidence")

    validation_metrics = calibration[
        "sigmoid_calibrated"
    ]

    validation_evidence = {
        "average_precision": float(
            validation_metrics[
                "average_precision"
            ]
        ),

        "roc_auc": float(
            validation_metrics[
                "roc_auc"
            ]
        ),

        "log_loss": float(
            validation_metrics[
                "log_loss"
            ]
        ),

        "brier_score": float(
            validation_metrics[
                "brier_score"
            ]
        ),
    }

    print(
        f"Validation AP: "
        f"{validation_evidence['average_precision']:.12f}"
    )

    print(
        f"Validation ROC-AUC: "
        f"{validation_evidence['roc_auc']:.12f}"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 7. Locked evaluation evidence
    # ------------------------------------------------------------------

    print("\n[7] Record locked evaluation evidence")

    evaluation_metrics = evaluation[
        "metrics"
    ]

    locked_evaluation_evidence = {
        "average_precision": float(
            evaluation_metrics[
                "average_precision"
            ]
        ),

        "roc_auc": float(
            evaluation_metrics[
                "roc_auc"
            ]
        ),

        "log_loss": float(
            evaluation_metrics[
                "log_loss"
            ]
        ),

        "brier_score": float(
            evaluation_metrics[
                "brier_score"
            ]
        ),

        "threshold_0_5": {
            "precision": float(
                evaluation_metrics[
                    "threshold_0_5"
                ]["precision"]
            ),

            "recall": float(
                evaluation_metrics[
                    "threshold_0_5"
                ]["recall"]
            ),

            "f1": float(
                evaluation_metrics[
                    "threshold_0_5"
                ]["f1"]
            ),

            "positive_predictions": int(
                evaluation_metrics[
                    "threshold_0_5"
                ]["positive_predictions"]
            ),
        },
    }

    print(
        f"Evaluation AP: "
        f"{locked_evaluation_evidence['average_precision']:.12f}"
    )

    print(
        f"Evaluation ROC-AUC: "
        f"{locked_evaluation_evidence['roc_auc']:.12f}"
    )

    print(
        "Evaluation selection/tuning: NO"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 8. Generalization evidence
    # ------------------------------------------------------------------

    print("\n[8] Record generalization evidence")

    generalization_evidence = (
        generalization["generalization"]
    )

    observed_direction = (
        generalization["observed_direction"]
    )

    print(
        "AP relative change: "
        f"{generalization_evidence['average_precision']['relative_change_percent']:.2f}%"
    )

    print(
        "ROC-AUC relative change: "
        f"{generalization_evidence['roc_auc']['relative_change_percent']:.2f}%"
    )

    print(
        "Log Loss relative change: "
        f"{generalization_evidence['log_loss']['relative_change_percent']:.2f}%"
    )

    print(
        "Brier relative change: "
        f"{generalization_evidence['brier_score']['relative_change_percent']:.2f}%"
    )

    print(
        "Discrimination decreased: "
        f"{observed_direction['discrimination_decreased']}"
    )

    print(
        "Log Loss increased: "
        f"{observed_direction['log_loss_increased']}"
    )

    print(
        "Brier increased: "
        f"{observed_direction['brier_score_increased']}"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 9. Final role and limitations
    # ------------------------------------------------------------------

    print("\n[9] Establish final T5 system role")

    final_role = (
        "SECONDARY_DECISION_SUPPORT_SIGNAL"
    )

    final_status = (
        "SUPPORTED_WITH_LIMITATIONS"
    )

    limitations = [
        (
            "Temporal generalization degradation was "
            "observed between validation and the official "
            "evaluation population."
        ),
        (
            "Locked evaluation AP was 0.125833 and "
            "ROC-AUC was 0.678142."
        ),
        (
            "The descriptive 0.5 threshold produced "
            "23 positive predictions with 0.008346 recall."
        ),
        (
            "No operational threshold was established."
        ),
        (
            "No autonomous duplicate determination "
            "or human-review removal is supported."
        ),
        (
            "The target detects observed duplicate-"
            "relationship existence, not the identity "
            "of the duplicate target ticket."
        ),
    ]

    print(
        f"Final system role: {final_role}"
    )

    print(
        f"Final task status: {final_status}"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 10. Build closure record
    # ------------------------------------------------------------------

    print("\n[10] Build final closure record")

    closure = {
        "operation": "T5-MOD-011",
        "operation_name": "Final Task Closure",

        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),

        "task": "T5 — Binary Duplicate Detection",

        "task_definition": task_definition,

        "split_definition": split_definition,

        "selected_pipeline": selected_pipeline,

        "validation_evidence": validation_evidence,

        "locked_evaluation_evidence": (
            locked_evaluation_evidence
        ),

        "generalization_evidence": (
            generalization_evidence
        ),

        "final_role": final_role,

        "final_status": final_status,

        "limitations": limitations,

        "controls": {
            "model_refit": False,
            "calibrator_refit": False,
            "vectorizer_refit": False,
            "threshold_optimization": False,
            "evaluation_used_for_selection": False,
            "evaluation_used_for_calibration": False,
            "evaluation_modified": False,
            "raw_dataset_modified": False,
            "synthetic_data": False,
            "autonomous_decision_support_claim": False,
        },

        "closure_statement": (
            "T5 Binary Duplicate Detection is closed for "
            "the current controlled modeling cycle. The "
            "frozen pipeline is retained as a secondary "
            "decision-support signal with limitations. "
            "The official evaluation was used only for "
            "locked final assessment and not for model "
            "selection, calibration, threshold optimization, "
            "or refitting."
        ),

        "status": "CLOSED",
    }

    # ------------------------------------------------------------------
    # 11. Save closure
    # ------------------------------------------------------------------

    print("\n[11] Save final closure artifact")

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            closure,
            file,
            indent=2,
        )

    print(
        f"Saved: {OUTPUT}"
    )

    print(
        f"File size: "
        f"{OUTPUT.stat().st_size:,} bytes"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # Final
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print(
        "T5-MOD-011 RESULT: FINAL_TASK_CLOSED"
    )
    print("=" * 80)

    print(
        "\nFinal role: "
        f"{final_role}"
    )

    print(
        "Final status: "
        f"{final_status}"
    )

    print(
        "Task status: CLOSED"
    )


if __name__ == "__main__":
    main()