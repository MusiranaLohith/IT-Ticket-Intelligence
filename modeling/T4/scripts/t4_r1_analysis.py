from pathlib import Path
import json
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DERIVED_DIR = PROJECT_ROOT / "modeling" / "T4" / "derived"
CHECKPOINT_DIR = PROJECT_ROOT / "modeling" / "T4" / "results" / "r1_checkpoints"
RESULTS_DIR = PROJECT_ROOT / "modeling" / "T4" / "results"

EVAL_PATH = DERIVED_DIR / "t4_eval.csv"
SCORES_PATH = CHECKPOINT_DIR / "t4_r1_topk_predictions.npz"
OUTPUT_PATH = RESULTS_DIR / "t4_r1_analysis.json"


def main():
    print("T4-MOD-006-R1_ANALYSIS_START", flush=True)

    evaluation = pd.read_csv(EVAL_PATH)

    scores = np.load(SCORES_PATH, allow_pickle=True)

    top_indices = scores["top_indices"]
    top_scores = scores["top_scores"]
    candidate_labels = scores["candidate_labels"].astype(str)

    y_true = evaluation["target_assignee"].astype(str).to_numpy()

    if len(y_true) != top_indices.shape[0]:
        raise RuntimeError(
            f"Evaluation rows {len(y_true)} != prediction rows "
            f"{top_indices.shape[0]}"
        )

    top1_pred = candidate_labels[top_indices[:, 0]]

    candidate_set = set(candidate_labels.tolist())

    covered_mask = np.array(
        [x in candidate_set for x in y_true],
        dtype=bool,
    )

    unseen_mask = ~covered_mask

    # ---------------------------------------------------------------
    # Actual target frequency in evaluation
    # ---------------------------------------------------------------

    eval_counts = Counter(y_true)

    # ---------------------------------------------------------------
    # Top-1 prediction frequency
    # ---------------------------------------------------------------

    prediction_counts = Counter(top1_pred)

    # ---------------------------------------------------------------
    # Rank-bucket accuracy
    #
    # Rank target classes by TRAINING frequency.
    # ---------------------------------------------------------------

    train = pd.read_csv(DERIVED_DIR / "t4_train.csv")

    train_counts = Counter(
        train["target_assignee"].astype(str)
    )

    frequency_buckets = {
        "1": [],
        "2-5": [],
        "6-10": [],
        "11-20": [],
        "21-50": [],
        "51-100": [],
        "101+": [],
    }

    for label, count in train_counts.items():
        if count == 1:
            frequency_buckets["1"].append(label)
        elif count <= 5:
            frequency_buckets["2-5"].append(label)
        elif count <= 10:
            frequency_buckets["6-10"].append(label)
        elif count <= 20:
            frequency_buckets["11-20"].append(label)
        elif count <= 50:
            frequency_buckets["21-50"].append(label)
        elif count <= 100:
            frequency_buckets["51-100"].append(label)
        else:
            frequency_buckets["101+"].append(label)

    frequency_bucket_sets = {
        key: set(value)
        for key, value in frequency_buckets.items()
    }

    bucket_results = {}

    for bucket, labels in frequency_bucket_sets.items():
        mask = np.array(
            [x in labels for x in y_true],
            dtype=bool,
        )

        if np.any(mask):
            bucket_results[bucket] = {
                "evaluation_rows": int(np.sum(mask)),
                "top1_accuracy": float(
                    np.mean(top1_pred[mask] == y_true[mask])
                ),
            }
        else:
            bucket_results[bucket] = {
                "evaluation_rows": 0,
                "top1_accuracy": None,
            }

    # ---------------------------------------------------------------
    # Covered vs unseen
    # ---------------------------------------------------------------

    covered_accuracy = (
        float(np.mean(top1_pred[covered_mask] == y_true[covered_mask]))
        if np.any(covered_mask)
        else None
    )

    unseen_accuracy = (
        float(np.mean(top1_pred[unseen_mask] == y_true[unseen_mask]))
        if np.any(unseen_mask)
        else None
    )

    # ---------------------------------------------------------------
    # Top-k covered evaluation
    # ---------------------------------------------------------------

    top_k_covered = {}

    for k in [1, 3, 5, 10]:
        predictions = candidate_labels[top_indices[:, :k]]

        hits = np.any(
            predictions == y_true[:, None],
            axis=1,
        )

        if np.any(covered_mask):
            top_k_covered[f"top{k}_accuracy"] = float(
                np.mean(hits[covered_mask])
            )
        else:
            top_k_covered[f"top{k}_accuracy"] = None

    # ---------------------------------------------------------------
    # Prediction concentration
    # ---------------------------------------------------------------

    total = len(top1_pred)

    concentration = {}

    for n in [1, 5, 10, 25, 50, 100]:
        most_common = prediction_counts.most_common(n)

        concentration[f"top_{n}_predicted_assignees"] = {
            "unique_assignees": len(most_common),
            "prediction_count": int(
                sum(count for _, count in most_common)
            ),
            "prediction_share": float(
                sum(count for _, count in most_common) / total
            ),
        }

    # ---------------------------------------------------------------
    # Top predicted assignees
    # ---------------------------------------------------------------

    top_predictions = []

    for label, count in prediction_counts.most_common(20):
        top_predictions.append(
            {
                "assignee": label,
                "prediction_count": int(count),
                "prediction_share": float(count / total),
                "training_support": int(train_counts.get(label, 0)),
                "evaluation_actual_support": int(
                    eval_counts.get(label, 0)
                ),
            }
        )

    # ---------------------------------------------------------------
    # Top errors
    # ---------------------------------------------------------------

    error_pairs = Counter(
        (true, pred)
        for true, pred in zip(y_true, top1_pred)
        if true != pred
    )

    top_errors = []

    for (true, pred), count in error_pairs.most_common(20):
        top_errors.append(
            {
                "true_assignee": true,
                "predicted_assignee": pred,
                "count": int(count),
                "training_support_true": int(
                    train_counts.get(true, 0)
                ),
                "training_support_predicted": int(
                    train_counts.get(pred, 0)
                ),
            }
        )

    # ---------------------------------------------------------------
    # Macro-F1 on covered rows
    # ---------------------------------------------------------------

    covered_macro_f1 = (
        float(
            f1_score(
                y_true[covered_mask],
                top1_pred[covered_mask],
                labels=candidate_labels,
                average="macro",
                zero_division=0,
            )
        )
        if np.any(covered_mask)
        else None
    )

    # ---------------------------------------------------------------
    # Final report
    # ---------------------------------------------------------------

    report = {
        "experiment": "T4-MOD-006-R1",
        "analysis": "post_baseline_error_and_concentration_analysis",
        "evaluation_rows": int(len(y_true)),
        "candidate_classes": int(len(candidate_labels)),
        "covered_rows": int(np.sum(covered_mask)),
        "unseen_rows": int(np.sum(unseen_mask)),
        "unseen_rate": float(np.mean(unseen_mask)),
        "covered_topk_accuracy": top_k_covered,
        "covered_top1_accuracy": covered_accuracy,
        "unseen_top1_accuracy": unseen_accuracy,
        "covered_top1_macro_f1": covered_macro_f1,
        "training_frequency_bucket_results": bucket_results,
        "prediction_concentration": concentration,
        "top_20_predicted_assignees": top_predictions,
        "top_20_error_pairs": top_errors,
        "status": "COMPLETE",
        "raw_mozilla_accessed": False,
        "model_trained": False,
        "predictions_created": False,
        "test_used": False,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"ANALYSIS_SAVED={OUTPUT_PATH}", flush=True)

    print(
        f"COVERED_ROWS={np.sum(covered_mask)}",
        flush=True,
    )

    print(
        f"UNSEEN_ROWS={np.sum(unseen_mask)}",
        flush=True,
    )

    print(
        f"COVERED_TOP1_ACCURACY={covered_accuracy}",
        flush=True,
    )

    print(
        f"UNSEEN_TOP1_ACCURACY={unseen_accuracy}",
        flush=True,
    )

    print("TOP_K_COVERED", flush=True)

    for key, value in top_k_covered.items():
        print(f"{key}={value}", flush=True)

    print("FREQUENCY_BUCKET_RESULTS", flush=True)

    for bucket, result in bucket_results.items():
        print(
            f"{bucket}: "
            f"ROWS={result['evaluation_rows']} "
            f"TOP1={result['top1_accuracy']}",
            flush=True,
        )

    print("TOP_PREDICTION_CONCENTRATION", flush=True)

    for key, value in concentration.items():
        print(
            f"{key}: SHARE={value['prediction_share']:.6f}",
            flush=True,
        )

    print("TOP_10_PREDICTED_ASSIGNEES", flush=True)

    for item in top_predictions[:10]:
        print(
            f"{item['assignee']} | "
            f"COUNT={item['prediction_count']} | "
            f"SHARE={item['prediction_share']:.6f} | "
            f"TRAIN_SUPPORT={item['training_support']}",
            flush=True,
        )

    print("T4-MOD-006-R1_ANALYSIS_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
