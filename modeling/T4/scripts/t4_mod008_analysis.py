from pathlib import Path
import json

PROJECT_DIR = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
RESULTS_DIR = PROJECT_DIR / "modeling/T4/results"

R1_PATH = RESULTS_DIR / "t4_r1_metrics.json"
MOD007_PATH = RESULTS_DIR / "t4_mod007_full_results.json"
MOD008_PATH = RESULTS_DIR / "t4_mod008_full.json"

OUT_PATH = RESULTS_DIR / "t4_mod008_analysis.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def pp(value):
    return value * 100.0


def fmt(value):
    if value is None:
        return "N/A"
    return f"{value:.6f}"


def main():
    r1 = load_json(R1_PATH)
    mod007 = load_json(MOD007_PATH)
    mod008 = load_json(MOD008_PATH)

    r1_metrics = r1["metrics"]
    r1_covered = r1["covered_evaluation"]

    mod007_overall = mod007["metrics_overall"]
    mod007_covered = mod007["metrics_covered_targets"]

    mod008_overall = mod008["retrieval"]["overall"]
    mod008_covered = mod008["retrieval"]["covered"]

    print("T4 MOD-008 comparative analysis")
    print()

    print("POPULATION")
    print(f"R1 evaluation rows      : {r1['evaluation_rows']}")
    print(f"MOD-007 evaluation rows : {mod007['evaluation_rows']}")
    print(f"MOD-008 evaluation rows : {mod008['population']['evaluation_rows']}")
    print()

    print("OVERALL HIT@K")

    for k in [1, 3, 5, 10, 20]:
        r1_value = r1_metrics.get(f"top{k}_accuracy")
        mod007_value = mod007_overall.get(f"hit_at_{k}")
        mod008_value = mod008_overall.get(f"hit_at_{k}")

        print(
            f"Hit@{k:<2} "
            f"R1={fmt(r1_value):<8} "
            f"MOD007={fmt(mod007_value):<8} "
            f"MOD008={fmt(mod008_value)}"
        )

    print()
    print("MOD-008 MINUS MOD-007 — COMPARABLE OVERALL METRICS")

    overall_deltas = {}

    for k in [1, 3, 5, 10]:
        key = f"hit_at_{k}"

        d = mod008_overall[key] - mod007_overall[key]
        overall_deltas[key] = d

        print(
            f"Hit@{k:<2}: "
            f"{d:+.6f} "
            f"({pp(d):+.4f} pp)"
        )

    print()
    print("COVERED TARGETS")

    for k in [1, 3, 5, 10, 20]:
        r1_value = r1_covered.get(f"top{k}_accuracy")
        mod007_value = mod007_covered.get(f"hit_at_{k}")
        mod008_value = mod008_covered.get(f"hit_at_{k}")

        print(
            f"Hit@{k:<2} "
            f"R1={fmt(r1_value):<8} "
            f"MOD007={fmt(mod007_value):<8} "
            f"MOD008={fmt(mod008_value)}"
        )

    print()
    print("MOD-008 MINUS MOD-007 — COMPARABLE COVERED METRICS")

    covered_deltas = {}

    for k in [1, 3, 5, 10]:
        key = f"hit_at_{k}"

        d = mod008_covered[key] - mod007_covered[key]
        covered_deltas[key] = d

        print(
            f"Hit@{k:<2}: "
            f"{d:+.6f} "
            f"({pp(d):+.4f} pp)"
        )

    print()
    print("MOD-008 COVERED HIT@20")

    print(f"MOD-008 Covered Hit@20 : {mod008_covered['hit_at_20']:.6f}")

    print()
    print("MOD-007 RANKING METRICS")

    print(f"MRR     : {mod007_overall['mrr']:.6f}")
    print(f"NDCG@5  : {mod007_overall['ndcg_at_5']:.6f}")
    print(f"NDCG@10 : {mod007_overall['ndcg_at_10']:.6f}")

    print()
    print("MOD-008 RETRIEVAL COVERAGE")

    retrieval_coverage = mod008["retrieval"]["retrieval_coverage_at_20"]

    print(f"True-assignee retrieval@20 : {retrieval_coverage:.6f}")
    print(
        "Retrieved true-assignee rows: "
        f"{mod008['retrieval']['retrieved_true_assignee_rows']}"
    )

    print()
    print("MOD-007 RETRIEVAL COVERAGE")

    mod007_retrieval_coverage = (
        mod007["metrics_overall"].get("hit_at_20")
    )

    if mod007_retrieval_coverage is None:
        mod007_retrieval_coverage = (
            mod007.get("open_world", {})
            .get("covered_evaluation", {})
            .get("top20_accuracy")
        )

    print(
        "MOD-007 stored Hit@20 ranking metric: "
        f"{fmt(mod007_retrieval_coverage)}"
    )

    print()
    print("SCREENING VS FULL MOD-008")

    screen_hit20 = mod008["comparison"]["mod008_screen_hit_at_20"]
    full_hit20 = mod008_covered["hit_at_20"]

    print(f"Screening Hit@20 : {screen_hit20:.6f}")
    print(f"Full Hit@20      : {full_hit20:.6f}")
    print(f"Difference       : {full_hit20 - screen_hit20:+.6f}")

    print()
    print("INTERPRETATION FLAGS")

    top1_delta = (
        mod008_covered["hit_at_1"]
        - mod007_covered["hit_at_1"]
    )

    top10_delta = (
        mod008_covered["hit_at_10"]
        - mod007_covered["hit_at_10"]
    )

    print(
        "MOD008_TOP1_LOWER_THAN_MOD007="
        f"{top1_delta < 0}"
    )

    print(
        "MOD008_TOP10_LOWER_THAN_MOD007="
        f"{top10_delta < 0}"
    )

    print(
        "MOD008_FULL_HIT20_AVAILABLE="
        f"{'hit_at_20' in mod008_covered}"
    )

    print("MOD007_HIT20_DIRECTLY_COMPARABLE=False")
    print("FINAL_ASSIGNEE_RANKING_EVALUATION_REQUIRED=True")

    print()
    print("CONTROLS")

    controls = mod008["controls"]

    print(f"RAW_MOZILLA_ACCESSED={controls['raw_mozilla_accessed']}")
    print(f"TARGET_RECONSTRUCTED={controls['target_reconstructed']}")
    print(f"TEST_USED={controls['test_used']}")
    print(f"FUTURE_FEATURES_USED={controls['future_features_used']}")
    print(f"SPLIT_CHANGED={controls['split_changed']}")

    analysis = {
        "experiment": "T4-MOD-008",
        "status": "COMPLETE",
        "population": mod008["population"],
        "overall_comparison": {
            "r1": {
                "top1": r1_metrics.get("top1_accuracy"),
                "top3": r1_metrics.get("top3_accuracy"),
                "top5": r1_metrics.get("top5_accuracy"),
                "top10": r1_metrics.get("top10_accuracy"),
                "top20": None,
            },
            "mod007": {
                "top1": mod007_overall.get("hit_at_1"),
                "top3": mod007_overall.get("hit_at_3"),
                "top5": mod007_overall.get("hit_at_5"),
                "top10": mod007_overall.get("hit_at_10"),
                "top20": None,
            },
            "mod008": {
                "top1": mod008_overall.get("hit_at_1"),
                "top3": mod008_overall.get("hit_at_3"),
                "top5": mod008_overall.get("hit_at_5"),
                "top10": mod008_overall.get("hit_at_10"),
                "top20": mod008_overall.get("hit_at_20"),
            },
        },
        "covered_comparison": {
            "r1": {
                "top1": r1_covered.get("top1_accuracy"),
                "top3": r1_covered.get("top3_accuracy"),
                "top5": r1_covered.get("top5_accuracy"),
                "top10": r1_covered.get("top10_accuracy"),
                "top20": None,
            },
            "mod007": {
                "top1": mod007_covered.get("hit_at_1"),
                "top3": mod007_covered.get("hit_at_3"),
                "top5": mod007_covered.get("hit_at_5"),
                "top10": mod007_covered.get("hit_at_10"),
                "top20": None,
            },
            "mod008": mod008_covered,
        },
        "mod008_minus_mod007": {
            "overall_comparable": overall_deltas,
            "covered_comparable": covered_deltas,
        },
        "mod007_ranking_metrics": {
            "mrr": mod007_overall["mrr"],
            "ndcg_at_5": mod007_overall["ndcg_at_5"],
            "ndcg_at_10": mod007_overall["ndcg_at_10"],
        },
        "mod008_retrieval": {
            "covered_hit_at_20": mod008_covered["hit_at_20"],
            "true_assignee_retrieval_coverage_at_20": retrieval_coverage,
            "retrieved_true_assignee_rows": (
                mod008["retrieval"]["retrieved_true_assignee_rows"]
            ),
        },
        "screening_vs_full": {
            "screen_hit_at_20": screen_hit20,
            "full_covered_hit_at_20": full_hit20,
            "difference": full_hit20 - screen_hit20,
        },
        "interpretation": {
            "mod008_top1_lower_than_mod007": top1_delta < 0,
            "mod008_top10_lower_than_mod007": top10_delta < 0,
            "mod007_hit20_directly_comparable": False,
            "final_assignee_ranking_evaluation_required": True,
        },
        "controls": controls,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2)

    print()
    print(f"ANALYSIS_SAVED={OUT_PATH}")
    print("T4-MOD-008_ANALYSIS_COMPLETE")


if __name__ == "__main__":
    main()