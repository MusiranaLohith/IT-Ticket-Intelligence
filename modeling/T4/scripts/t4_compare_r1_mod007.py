from pathlib import Path
import json


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

R1_METRICS_FILE = (
    PROJECT_ROOT / "modeling/T4/results/t4_r1_metrics.json"
)

R1_ANALYSIS_FILE = (
    PROJECT_ROOT / "modeling/T4/results/t4_r1_analysis.json"
)

MOD007_RESULTS_FILE = (
    PROJECT_ROOT / "modeling/T4/results/t4_mod007_full_results.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT / "modeling/T4/results/t4_r1_vs_mod007_analysis.json"
)


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    print("T4 R1 vs MOD-007 comparative analysis")

    r1 = load_json(R1_METRICS_FILE)
    r1_analysis = load_json(R1_ANALYSIS_FILE)
    mod007 = load_json(MOD007_RESULTS_FILE)

    r1_metrics = r1["metrics"]
    r1_covered = r1_analysis["covered_topk_accuracy"]

    mod007_overall = mod007["metrics_overall"]
    mod007_covered = mod007["metrics_covered_targets"]

    r1_long_tail = r1_analysis["training_frequency_bucket_results"]
    mod007_long_tail = mod007["historical_support_stratification"]

    result = {
        "experiment": "T4 R1 vs MOD-007 Comparative Analysis",
        "status": "COMPLETE",
        "overall": {},
        "covered_targets": {},
        "open_world": {},
        "long_tail": {},
        "interpretation": [],
    }

    # ------------------------------------------------------------
    # Overall metrics
    # ------------------------------------------------------------

    result["overall"]["R1"] = {
        "top1_accuracy": r1_metrics["top1_accuracy"],
        "top3_accuracy": r1_metrics["top3_accuracy"],
        "top5_accuracy": r1_metrics["top5_accuracy"],
        "top10_accuracy": r1_metrics["top10_accuracy"],
        "macro_f1": r1_metrics["top1_macro_f1"],
        "weighted_f1": r1_metrics["top1_weighted_f1"],
    }

    result["overall"]["MOD-007"] = {
        "hit_at_1": mod007_overall["hit_at_1"],
        "hit_at_3": mod007_overall["hit_at_3"],
        "hit_at_5": mod007_overall["hit_at_5"],
        "hit_at_10": mod007_overall["hit_at_10"],
        "mrr": mod007_overall["mrr"],
        "ndcg_at_5": mod007_overall["ndcg_at_5"],
        "ndcg_at_10": mod007_overall["ndcg_at_10"],
    }

    result["overall"]["MOD-007_minus_R1"] = {
        "hit_at_1": (
            mod007_overall["hit_at_1"]
            - r1_metrics["top1_accuracy"]
        ),
        "hit_at_3": (
            mod007_overall["hit_at_3"]
            - r1_metrics["top3_accuracy"]
        ),
        "hit_at_5": (
            mod007_overall["hit_at_5"]
            - r1_metrics["top5_accuracy"]
        ),
        "hit_at_10": (
            mod007_overall["hit_at_10"]
            - r1_metrics["top10_accuracy"]
        ),
    }

    # ------------------------------------------------------------
    # Covered-target metrics
    # ------------------------------------------------------------

    result["covered_targets"]["R1"] = {
        "top1_accuracy": r1_covered["top1_accuracy"],
        "top3_accuracy": r1_covered["top3_accuracy"],
        "top5_accuracy": r1_covered["top5_accuracy"],
        "top10_accuracy": r1_covered["top10_accuracy"],
    }

    result["covered_targets"]["MOD-007"] = {
        "hit_at_1": mod007_covered["hit_at_1"],
        "hit_at_3": mod007_covered["hit_at_3"],
        "hit_at_5": mod007_covered["hit_at_5"],
        "hit_at_10": mod007_covered["hit_at_10"],
        "mrr": mod007_covered["mrr"],
        "ndcg_at_5": mod007_covered["ndcg_at_5"],
        "ndcg_at_10": mod007_covered["ndcg_at_10"],
    }

    result["covered_targets"]["MOD-007_minus_R1"] = {
        "hit_at_1": (
            mod007_covered["hit_at_1"]
            - r1_covered["top1_accuracy"]
        ),
        "hit_at_3": (
            mod007_covered["hit_at_3"]
            - r1_covered["top3_accuracy"]
        ),
        "hit_at_5": (
            mod007_covered["hit_at_5"]
            - r1_covered["top5_accuracy"]
        ),
        "hit_at_10": (
            mod007_covered["hit_at_10"]
            - r1_covered["top10_accuracy"]
        ),
    }

    # ------------------------------------------------------------
    # Open-world comparison
    # ------------------------------------------------------------

    result["open_world"] = {
        "evaluation_rows": r1_analysis["evaluation_rows"],
        "covered_rows": r1_analysis["covered_rows"],
        "unseen_rows": r1_analysis["unseen_rows"],
        "unseen_rate": r1_analysis["unseen_rate"],
        "R1_unseen_top1_accuracy": r1_analysis[
            "unseen_top1_accuracy"
        ],
        "MOD007_unseen_rows": mod007["open_world"]["unseen_rows"],
        "MOD007_unseen_rate": mod007["open_world"]["unseen_rate"],
        "MOD007_unseen_hit_at_1": mod007[
            "metrics_unseen_targets"
        ]["hit_at_1"],
    }

    # ------------------------------------------------------------
    # Long-tail comparison
    # ------------------------------------------------------------

    buckets = [
        "1",
        "2-5",
        "6-10",
        "11-20",
        "21-50",
        "51-100",
        "101+",
    ]

    for bucket in buckets:
        r1_bucket = r1_long_tail[bucket]
        mod_bucket = mod007_long_tail[bucket]

        result["long_tail"][bucket] = {
            "evaluation_rows": r1_bucket["evaluation_rows"],
            "R1_top1": r1_bucket["top1_accuracy"],
            "MOD007_hit_at_1": mod_bucket["hit_at_1"],
            "MOD007_hit_at_5": mod_bucket["hit_at_5"],
            "MOD007_hit_at_10": mod_bucket["hit_at_10"],
            "MOD007_minus_R1_top1": (
                mod_bucket["hit_at_1"]
                - r1_bucket["top1_accuracy"]
            ),
        }

    # ------------------------------------------------------------
    # Evidence-based interpretation
    # ------------------------------------------------------------

    result["interpretation"].append(
        "Both experiments use the same frozen chronological "
        "training/evaluation population."
    )

    result["interpretation"].append(
        "R1 achieves higher Top-K accuracy than the current "
        "MOD-007 historical-similarity ranking formulation "
        "at K=1, 3, 5, and 10."
    )

    result["interpretation"].append(
        "MOD-007 provides ranking-native MRR and NDCG metrics, "
        "which R1 does not provide."
    )

    result["interpretation"].append(
        "Both approaches show strong historical-support dependence: "
        "performance increases substantially as the target assignee "
        "has more training-period examples."
    )

    result["interpretation"].append(
        "Singleton and low-support assignees remain difficult for "
        "both approaches, while high-support assignees account for "
        "substantially stronger performance."
    )

    result["interpretation"].append(
        "The current MOD-007 result does not justify selecting the "
        "current similarity-plus-assignee-aggregation formulation "
        "over R1 on Hit@K."
    )

    result["interpretation"].append(
        "The evidence does justify investigating a modified ranking "
        "scoring or aggregation strategy rather than repeating the "
        "same MOD-007 formulation."
    )

    result["interpretation"].append(
        "Unseen evaluation targets remain genuine open-world cases "
        "and are not converted into ordinary negatives."
    )

    result["interpretation"].append(
        "No conclusion about operational assignee eligibility or "
        "universal routing correctness is made from these historical "
        "evaluation results."
    )

    # ------------------------------------------------------------
    # Save
    # ------------------------------------------------------------

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)

    # ------------------------------------------------------------
    # Concise terminal output
    # ------------------------------------------------------------

    print()
    print("OVERALL")

    print(
        "R1      Top1/3/5/10: "
        f"{r1_metrics['top1_accuracy']:.6f} / "
        f"{r1_metrics['top3_accuracy']:.6f} / "
        f"{r1_metrics['top5_accuracy']:.6f} / "
        f"{r1_metrics['top10_accuracy']:.6f}"
    )

    print(
        "MOD-007 Hit1/3/5/10: "
        f"{mod007_overall['hit_at_1']:.6f} / "
        f"{mod007_overall['hit_at_3']:.6f} / "
        f"{mod007_overall['hit_at_5']:.6f} / "
        f"{mod007_overall['hit_at_10']:.6f}"
    )

    print()
    print("MOD-007 ranking metrics")

    print(f"MRR      : {mod007_overall['mrr']:.6f}")
    print(f"NDCG@5   : {mod007_overall['ndcg_at_5']:.6f}")
    print(f"NDCG@10  : {mod007_overall['ndcg_at_10']:.6f}")

    print()
    print("MOD-007 minus R1")

    deltas = result["overall"]["MOD-007_minus_R1"]

    print(f"Hit@1    : {deltas['hit_at_1']:+.6f}")
    print(f"Hit@3    : {deltas['hit_at_3']:+.6f}")
    print(f"Hit@5    : {deltas['hit_at_5']:+.6f}")
    print(f"Hit@10   : {deltas['hit_at_10']:+.6f}")

    print()
    print("LONG-TAIL TOP-1")

    for bucket in buckets:
        row = result["long_tail"][bucket]

        print(
            f"{bucket:>6}  "
            f"R1={row['R1_top1']:.6f}  "
            f"MOD007={row['MOD007_hit_at_1']:.6f}  "
            f"delta={row['MOD007_minus_R1_top1']:+.6f}"
        )

    print()
    print("OPEN-WORLD")

    print(f"Evaluation rows : {result['open_world']['evaluation_rows']}")
    print(f"Covered rows    : {result['open_world']['covered_rows']}")
    print(f"Unseen rows     : {result['open_world']['unseen_rows']}")
    print(
        f"Unseen rate     : "
        f"{result['open_world']['unseen_rate']:.6f}"
    )
    print(
        f"R1 unseen Top-1 : "
        f"{result['open_world']['R1_unseen_top1_accuracy']:.6f}"
    )
    print(
        f"MOD007 unseen H1: "
        f"{result['open_world']['MOD007_unseen_hit_at_1']:.6f}"
    )

    print()
    print(f"Analysis saved: {OUTPUT_FILE}")
    print("STATUS=COMPLETE")


if __name__ == "__main__":
    main()