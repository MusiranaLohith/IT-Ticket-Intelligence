from pathlib import Path
import csv
import json
import sys


# ============================================================
# T2-MOD-011
# Controlled Baseline Comparison & Advancement Decision
#
# Reads completed T2 baseline metric artifacts only.
# No training.
# No test-set access.
# No modification of previous artifacts.
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_ROOT = PROJECT_ROOT / "modeling" / "T2"

METRICS_DIR = T2_ROOT / "metrics"
ANALYSIS_DIR = T2_ROOT / "analysis"

OUTPUT_FILE = (
    ANALYSIS_DIR
    / "t2_baseline_comparison.json"
)

COMPARISON_CSV = (
    ANALYSIS_DIR
    / "t2_baseline_comparison.csv"
)

EXPECTED_CLASSES = [
    "P1",
    "P2",
    "P3",
    "P4",
    "P5",
]


EXPERIMENTS = [
    {
        "operation": "T2-MOD-006",
        "name": "TF-IDF + Logistic Regression",
        "file": (
            METRICS_DIR
            / "t2_baseline_metrics.json"
        ),
    },
    {
        "operation": "T2-MOD-007",
        "name": (
            "TF-IDF + Class-Weighted "
            "Logistic Regression"
        ),
        "file": (
            METRICS_DIR
            / "t2_class_weighted_metrics.json"
        ),
    },
    {
        "operation": "T2-MOD-008",
        "name": "TF-IDF + Linear SVM",
        "file": (
            METRICS_DIR
            / "t2_svm_metrics.json"
        ),
    },
    {
        "operation": "T2-MOD-010",
        "name": (
            "TF-IDF + Class-Weighted "
            "Linear SVM"
        ),
        "file": (
            METRICS_DIR
            / "t2_weighted_svm_metrics.json"
        ),
    },
]


def fail(message):
    print(f"COMPARISON_ERROR={message}")
    sys.exit(1)


def load_json(path):
    if not path.exists():
        fail(
            f"FILE_NOT_FOUND={path}"
        )

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)

    except Exception as exc:
        fail(
            f"INVALID_JSON={path} "
            f"ERROR={exc}"
        )


def get_evaluation_block(data):
    """
    T2-MOD-006/007/008 store metrics under:
        data["evaluation"]

    T2-MOD-010 stores metrics at the top level.

    Normalize both schemas here without modifying
    the original artifacts.
    """

    if "evaluation" in data:
        evaluation = data["evaluation"]

        if not isinstance(
            evaluation,
            dict,
        ):
            fail(
                "INVALID_EVALUATION_BLOCK"
            )

        return evaluation

    required = [
        "accuracy",
        "macro_f1",
        "weighted_f1",
        "per_class",
    ]

    if all(
        field in data
        for field in required
    ):
        return data

    fail(
        "UNRECOGNIZED_METRICS_SCHEMA"
    )


def main():
    print("T2_MOD_011_START")

    ANALYSIS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Load completed experiment artifacts.
    # --------------------------------------------------------
    loaded = []

    for experiment in EXPERIMENTS:
        data = load_json(
            experiment["file"]
        )

        loaded.append(
            {
                "operation": experiment[
                    "operation"
                ],
                "name": experiment[
                    "name"
                ],
                "data": data,
            }
        )

    # --------------------------------------------------------
    # Verify common task/dataset identity and test usage.
    # --------------------------------------------------------
    for item in loaded:
        data = item["data"]

        if data.get("task") != "T2":
            fail(
                "TASK_MISMATCH="
                f"{item['operation']}"
            )

        if data.get("dataset") != "Mozilla CORE":
            fail(
                "DATASET_MISMATCH="
                f"{item['operation']}"
            )

        evaluation = get_evaluation_block(
            data
        )

        if evaluation.get(
            "test_used"
        ) is True:
            fail(
                "TEST_USAGE_DETECTED="
                f"{item['operation']}"
            )

        if evaluation.get(
            "split"
        ) not in (
            None,
            "validation",
        ):
            fail(
                "UNEXPECTED_EVALUATION_SPLIT="
                f"{item['operation']} "
                f"SPLIT={evaluation.get('split')}"
            )

    # --------------------------------------------------------
    # Extract normalized metrics.
    # --------------------------------------------------------
    rows = []

    for item in loaded:
        data = item["data"]
        evaluation = get_evaluation_block(
            data
        )

        try:
            row = {
                "operation": item[
                    "operation"
                ],
                "model": item[
                    "name"
                ],
                "accuracy": float(
                    evaluation[
                        "accuracy"
                    ]
                ),
                "macro_f1": float(
                    evaluation[
                        "macro_f1"
                    ]
                ),
                "weighted_f1": float(
                    evaluation[
                        "weighted_f1"
                    ]
                ),
            }

            per_class = evaluation[
                "per_class"
            ]

            for class_name in EXPECTED_CLASSES:
                row[
                    f"{class_name}_f1"
                ] = float(
                    per_class[
                        class_name
                    ]["f1"]
                )

        except KeyError as exc:
            fail(
                "METRIC_FIELD_MISSING="
                f"{item['operation']} "
                f"FIELD={exc}"
            )

        rows.append(row)

    # --------------------------------------------------------
    # Identify best experiments.
    # --------------------------------------------------------
    best_accuracy = max(
        rows,
        key=lambda row: row[
            "accuracy"
        ],
    )

    best_macro_f1 = max(
        rows,
        key=lambda row: row[
            "macro_f1"
        ],
    )

    best_weighted_f1 = max(
        rows,
        key=lambda row: row[
            "weighted_f1"
        ],
    )

    best_p4 = max(
        rows,
        key=lambda row: row[
            "P4_f1"
        ],
    )

    best_p5 = max(
        rows,
        key=lambda row: row[
            "P5_f1"
        ],
    )

    # --------------------------------------------------------
    # Retrieve specific controlled experiments.
    # --------------------------------------------------------
    weighted_logistic = next(
        row
        for row in rows
        if row["operation"]
        == "T2-MOD-007"
    )

    unweighted_logistic = next(
        row
        for row in rows
        if row["operation"]
        == "T2-MOD-006"
    )

    weighted_svm = next(
        row
        for row in rows
        if row["operation"]
        == "T2-MOD-010"
    )

    unweighted_svm = next(
        row
        for row in rows
        if row["operation"]
        == "T2-MOD-008"
    )

    # --------------------------------------------------------
    # Minority-class comparison.
    # --------------------------------------------------------
    minority_summary = {
        "weighted_logistic_vs_unweighted_logistic": {
            "P4_f1_change": (
                weighted_logistic[
                    "P4_f1"
                ]
                - unweighted_logistic[
                    "P4_f1"
                ]
            ),
            "P5_f1_change": (
                weighted_logistic[
                    "P5_f1"
                ]
                - unweighted_logistic[
                    "P5_f1"
                ]
            ),
            "macro_f1_change": (
                weighted_logistic[
                    "macro_f1"
                ]
                - unweighted_logistic[
                    "macro_f1"
                ]
            ),
            "accuracy_change": (
                weighted_logistic[
                    "accuracy"
                ]
                - unweighted_logistic[
                    "accuracy"
                ]
            ),
        },
        "weighted_svm_vs_unweighted_svm": {
            "P4_f1_change": (
                weighted_svm[
                    "P4_f1"
                ]
                - unweighted_svm[
                    "P4_f1"
                ]
            ),
            "P5_f1_change": (
                weighted_svm[
                    "P5_f1"
                ]
                - unweighted_svm[
                    "P5_f1"
                ]
            ),
            "macro_f1_change": (
                weighted_svm[
                    "macro_f1"
                ]
                - unweighted_svm[
                    "macro_f1"
                ]
            ),
            "accuracy_change": (
                weighted_svm[
                    "accuracy"
                ]
                - unweighted_svm[
                    "accuracy"
                ]
            ),
        },
    }

    # --------------------------------------------------------
    # Advancement diagnosis.
    #
    # These are project-specific diagnostic criteria,
    # NOT universal ML benchmark thresholds.
    # --------------------------------------------------------
    linear_baseline_limitation = {
        "P4_recognition_weak": (
            best_p4["P4_f1"] < 0.20
        ),
        "P5_recognition_weak": (
            best_p5["P5_f1"] < 0.20
        ),
        "best_macro_f1_below_0_40": (
            best_macro_f1[
                "macro_f1"
            ] < 0.40
        ),
        "best_accuracy_below_0_60": (
            best_accuracy[
                "accuracy"
            ] < 0.60
        ),
    }

    advancement_justified = all(
        linear_baseline_limitation.values()
    )

    if advancement_justified:
        advancement_status = (
            "ADVANCED_NLP_JUSTIFIED"
        )

        advancement_reason = (
            "Across four controlled TF-IDF "
            "linear baseline experiments, "
            "the best validation accuracy "
            "remains below 60 percent and "
            "the best macro-F1 remains below "
            "40 percent. P4 and P5 recognition "
            "remain weak even after class "
            "weighting. The linear baseline "
            "family therefore does not provide "
            "sufficient minority-class or "
            "overall performance to serve as "
            "the final T2 modeling approach. "
            "Advancement to a more capable NLP "
            "model is justified. The advanced "
            "architecture is not selected by "
            "this operation."
        )

    else:
        advancement_status = (
            "ADVANCED_NLP_NOT_YET_JUSTIFIED"
        )

        advancement_reason = (
            "The controlled linear baseline "
            "family has not yet met the "
            "project-specific advancement "
            "conditions. Further baseline "
            "investigation would be required."
        )

    # --------------------------------------------------------
    # Save comparison CSV.
    # --------------------------------------------------------
    comparison_columns = [
        "operation",
        "model",
        "accuracy",
        "macro_f1",
        "weighted_f1",
        "P1_f1",
        "P2_f1",
        "P3_f1",
        "P4_f1",
        "P5_f1",
    ]

    try:
        with COMPARISON_CSV.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=comparison_columns,
            )

            writer.writeheader()

            for row in rows:
                writer.writerow(row)

    except Exception as exc:
        fail(
            f"CSV_WRITE_FAILED={exc}"
        )

    # --------------------------------------------------------
    # Save formal report.
    # --------------------------------------------------------
    report = {
        "operation": "T2-MOD-011",
        "operation_name": (
            "Controlled Baseline Comparison "
            "& Advancement Decision"
        ),
        "task": "T2",
        "task_name": "Priority Prediction",
        "dataset": "Mozilla CORE",
        "evaluation_partition": "validation",
        "test_used": False,

        "experiments_compared": rows,

        "best_by_metric": {
            "accuracy": {
                "operation": best_accuracy[
                    "operation"
                ],
                "model": best_accuracy[
                    "model"
                ],
                "value": best_accuracy[
                    "accuracy"
                ],
            },
            "macro_f1": {
                "operation": best_macro_f1[
                    "operation"
                ],
                "model": best_macro_f1[
                    "model"
                ],
                "value": best_macro_f1[
                    "macro_f1"
                ],
            },
            "weighted_f1": {
                "operation": best_weighted_f1[
                    "operation"
                ],
                "model": best_weighted_f1[
                    "model"
                ],
                "value": best_weighted_f1[
                    "weighted_f1"
                ],
            },
            "P4_f1": {
                "operation": best_p4[
                    "operation"
                ],
                "model": best_p4[
                    "model"
                ],
                "value": best_p4[
                    "P4_f1"
                ],
            },
            "P5_f1": {
                "operation": best_p5[
                    "operation"
                ],
                "model": best_p5[
                    "model"
                ],
                "value": best_p5[
                    "P5_f1"
                ],
            },
        },

        "minority_class_analysis": (
            minority_summary
        ),

        "linear_baseline_limitation": (
            linear_baseline_limitation
        ),

        "advancement_decision": {
            "status": advancement_status,
            "advanced_model_selected": False,
            "reason": advancement_reason,
        },

        "integrity": {
            "training_performed": False,
            "test_loaded": False,
            "raw_source_modified": False,
            "split_artifacts_modified": False,
            "previous_model_artifacts_modified": False,
            "historical_metric_artifacts_modified": False,
        },

        "artifacts": {
            "comparison_csv": str(
                COMPARISON_CSV
            ),
            "report": str(
                OUTPUT_FILE
            ),
        },

        "status": "COMPLETE",
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
    # Console output.
    # --------------------------------------------------------
    print("T2_MOD_011_COMPLETE")

    print("\nBASELINE_COMPARISON")

    for row in rows:
        print(
            f"{row['operation']} "
            f"ACCURACY={row['accuracy']:.6f} "
            f"MACRO_F1={row['macro_f1']:.6f} "
            f"WEIGHTED_F1={row['weighted_f1']:.6f} "
            f"P4_F1={row['P4_f1']:.6f} "
            f"P5_F1={row['P5_f1']:.6f}"
        )

    print("\nBEST_RESULTS")

    print(
        "BEST_ACCURACY="
        f"{best_accuracy['operation']} "
        f"{best_accuracy['accuracy']:.6f}"
    )

    print(
        "BEST_MACRO_F1="
        f"{best_macro_f1['operation']} "
        f"{best_macro_f1['macro_f1']:.6f}"
    )

    print(
        "BEST_WEIGHTED_F1="
        f"{best_weighted_f1['operation']} "
        f"{best_weighted_f1['weighted_f1']:.6f}"
    )

    print(
        "BEST_P4_F1="
        f"{best_p4['operation']} "
        f"{best_p4['P4_f1']:.6f}"
    )

    print(
        "BEST_P5_F1="
        f"{best_p5['operation']} "
        f"{best_p5['P5_f1']:.6f}"
    )

    print("\nADVANCEMENT_DECISION")

    print(
        f"STATUS={advancement_status}"
    )

    print(
        "ADVANCED_MODEL_SELECTED=False"
    )

    print(
        f"COMPARISON_CSV={COMPARISON_CSV}"
    )

    print(
        f"REPORT={OUTPUT_FILE}"
    )

    print("TEST_USED=False")
    print("STATUS=COMPLETE")


if __name__ == "__main__":
    main()