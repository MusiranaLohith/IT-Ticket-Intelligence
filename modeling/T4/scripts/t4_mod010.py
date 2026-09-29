from pathlib import Path
import json


PROJECT_DIR = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
RESULTS_DIR = PROJECT_DIR / "modeling" / "T4" / "results"

R1_PATH = RESULTS_DIR / "t4_r1_metrics.json"
MOD007_PATH = RESULTS_DIR / "t4_mod007_full_results.json"
MOD008_PATH = RESULTS_DIR / "t4_mod008_full.json"
MOD009_PATH = RESULTS_DIR / "t4_mod009_screen.json"

OUTPUT_PATH = RESULTS_DIR / "t4_mod010_comparison.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fmt(value):
    if value is None:
        return "N/A"
    return f"{value:.6f}"


def main():
    print("T4-MOD-010 retrieval experiment comparison")
    print()

    r1 = load_json(R1_PATH)
    mod007 = load_json(MOD007_PATH)
    mod008 = load_json(MOD008_PATH)
    mod009 = load_json(MOD009_PATH)

    r1_metrics = r1["metrics"]
    mod007_metrics = mod007["metrics_overall"]
    mod008_metrics = mod008["retrieval"]["overall"]
    mod009_metrics = mod009["retrieval"]["metrics"]

    print("EXPERIMENTS")
    print("R1      : Flat TF-IDF + LinearSVC")
    print("MOD-007 : Word TF-IDF historical retrieval")
    print("MOD-008 : Word + Character TF-IDF historical retrieval")
    print("MOD-009 : BM25 historical retrieval screening")
    print()

    print("POPULATION")
    print(f"R1 evaluation rows      : {r1['evaluation_rows']}")
    print(f"MOD-007 evaluation rows : {mod007['evaluation_rows']}")
    print(f"MOD-008 evaluation rows : {mod008['population']['evaluation_rows']}")
    print(
        f"MOD-009 screening rows  : "
        f"{mod009['population']['screen_sample']}"
    )
    print()

    print("OVERALL HIT@K")
    print()

    print(
        f"{'Metric':<10}"
        f"{'R1':>12}"
        f"{'MOD-007':>12}"
        f"{'MOD-008':>12}"
        f"{'MOD-009*':>12}"
    )

    metric_map = [
        ("Hit@1", "top1_accuracy", "hit_at_1"),
        ("Hit@3", "top3_accuracy", "hit_at_3"),
        ("Hit@5", "top5_accuracy", "hit_at_5"),
        ("Hit@10", "top10_accuracy", "hit_at_10"),
        ("Hit@20", None, "hit_at_20"),
    ]

    comparison_rows = []

    for label, r1_key, ranking_key in metric_map:
        r1_value = r1_metrics.get(r1_key) if r1_key else None
        mod007_value = mod007_metrics.get(ranking_key)
        mod008_value = mod008_metrics.get(ranking_key)
        mod009_value = mod009_metrics.get(ranking_key)

        comparison_rows.append(
            {
                "metric": label,
                "r1": r1_value,
                "mod007": mod007_value,
                "mod008": mod008_value,
                "mod009_screen": mod009_value,
            }
        )

        print(
            f"{label:<10}"
            f"{fmt(r1_value):>12}"
            f"{fmt(mod007_value):>12}"
            f"{fmt(mod008_value):>12}"
            f"{fmt(mod009_value):>12}"
        )

    print()
    print("* MOD-009 values are screening-sample results.")
    print()

    print("MOD-009 SCREENING DELTAS")
    print()

    delta_rows = {}

    for metric_key in [
        "hit_at_1",
        "hit_at_3",
        "hit_at_5",
        "hit_at_10",
        "hit_at_20",
    ]:
        mod009_value = mod009_metrics[metric_key]
        mod007_value = mod007_metrics.get(metric_key)
        mod008_value = mod008_metrics.get(metric_key)

        delta_007 = (
            mod009_value - mod007_value
            if mod007_value is not None
            else None
        )

        delta_008 = (
            mod009_value - mod008_value
            if mod008_value is not None
            else None
        )

        delta_rows[metric_key] = {
            "vs_mod007": delta_007,
            "vs_mod008": delta_008,
        }

        print(
            f"{metric_key.upper():<10}"
            f"MOD009-MOD007={fmt(delta_007):>10} "
            f"MOD009-MOD008={fmt(delta_008):>10}"
        )

    print()
    print("MOD-009 SCREENING DETAILS")
    print()

    print(f"Vocabulary size : {mod009['bm25']['vocabulary_size']}")
    print(f"K1              : {mod009['bm25']['k1']}")
    print(f"B               : {mod009['bm25']['b']}")
    print(f"Top-K           : {mod009['retrieval']['top_k']}")
    print(f"Seed            : {mod009['sampling']['seed']}")
    print(
        f"Covered-only    : "
        f"{mod009['sampling']['covered_only']}"
    )
    print()

    print("FULL-SCALE COMPARABILITY")
    print()

    print(
        "MOD-009 full evaluation available : False"
    )
    print(
        "MOD-009 screening sample          : "
        f"{mod009['population']['screen_sample']}"
    )
    print(
        "MOD-008 full evaluation           : "
        f"{mod008['population']['evaluation_rows']}"
    )
    print(
        "MOD-007 full evaluation           : "
        f"{mod007['evaluation_rows']}"
    )

    print()
    print("RANKING METRICS FROM MOD-007")
    print()

    print(
        f"MRR     : "
        f"{mod007['metrics_overall']['mrr']:.6f}"
    )
    print(
        f"NDCG@5  : "
        f"{mod007['metrics_overall']['ndcg_at_5']:.6f}"
    )
    print(
        f"NDCG@10 : "
        f"{mod007['metrics_overall']['ndcg_at_10']:.6f}"
    )

    print()
    print("INTERPRETATION")
    print()

    mod009_h1 = mod009_metrics["hit_at_1"]
    mod009_h10 = mod009_metrics["hit_at_10"]
    mod009_h20 = mod009_metrics["hit_at_20"]

    mod008_h1 = mod008_metrics["hit_at_1"]
    mod008_h10 = mod008_metrics["hit_at_10"]
    mod008_h20 = mod008_metrics["hit_at_20"]

    print(
        f"MOD-009 screening Hit@1  : {mod009_h1:.6f}"
    )
    print(
        f"MOD-008 full Hit@1       : {mod008_h1:.6f}"
    )
    print()

    print(
        f"MOD-009 screening Hit@10 : {mod009_h10:.6f}"
    )
    print(
        f"MOD-008 full Hit@10      : {mod008_h10:.6f}"
    )
    print()

    print(
        f"MOD-009 screening Hit@20 : {mod009_h20:.6f}"
    )
    print(
        f"MOD-008 full Hit@20      : {mod008_h20:.6f}"
    )
    print()

    print(
        "NOTE: MOD-009 screening and MOD-008 full-population "
        "results are not directly comparable for model selection."
    )

    print()
    print("CONTROL CHECKS")
    print()

    controls = {
        "r1": r1.get("controls", {}),
        "mod007": mod007.get("controls", {}),
        "mod008": mod008.get("controls", {}),
        "mod009": mod009.get("controls", {}),
    }

    print(json.dumps(controls, indent=2))

    output = {
        "experiment": "T4-MOD-010",
        "status": "COMPLETE",
        "purpose": (
            "Controlled comparison of T4 retrieval and "
            "classification experiments"
        ),
        "experiments": {
            "r1": "Flat TF-IDF + LinearSVC",
            "mod007": "Word TF-IDF historical retrieval",
            "mod008": (
                "Word + Character TF-IDF historical retrieval"
            ),
            "mod009": "BM25 historical retrieval screening",
        },
        "population": {
            "r1_evaluation_rows": r1["evaluation_rows"],
            "mod007_evaluation_rows": mod007["evaluation_rows"],
            "mod008_evaluation_rows": (
                mod008["population"]["evaluation_rows"]
            ),
            "mod009_screen_rows": (
                mod009["population"]["screen_sample"]
            ),
        },
        "metrics": comparison_rows,
        "mod009_screening": {
            "population": mod009["population"],
            "bm25": mod009["bm25"],
            "retrieval": mod009["retrieval"],
            "sampling": mod009["sampling"],
        },
        "deltas": delta_rows,
        "ranking_metrics_mod007": {
            "mrr": mod007["metrics_overall"]["mrr"],
            "ndcg_at_5": mod007["metrics_overall"]["ndcg_at_5"],
            "ndcg_at_10": mod007["metrics_overall"]["ndcg_at_10"],
        },
        "comparability": {
            "mod009_is_screening_only": True,
            "mod009_full_evaluation_completed": False,
            "mod009_screen_rows": (
                mod009["population"]["screen_sample"]
            ),
            "mod008_full_evaluation_rows": (
                mod008["population"]["evaluation_rows"]
            ),
            "mod007_full_evaluation_rows": (
                mod007["evaluation_rows"]
            ),
        },
        "interpretation": {
            "screening_not_final_model_selection": True,
            "full_scale_mod009_required_before_final_comparison": True,
        },
        "controls": controls,
        "raw_mozilla_accessed": False,
        "target_reconstructed": False,
        "test_used": False,
        "future_features_used": False,
        "split_changed": False,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print()
    print(f"ANALYSIS_SAVED={OUTPUT_PATH}")
    print("T4-MOD-010_COMPLETE")


if __name__ == "__main__":
    main()