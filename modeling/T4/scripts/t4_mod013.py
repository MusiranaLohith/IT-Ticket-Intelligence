from pathlib import Path
import json


PROJECT_DIR = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

RESULTS_DIR = (
    PROJECT_DIR
    / "modeling"
    / "T4"
    / "results"
)

OUTPUT_PATH = (
    RESULTS_DIR
    / "t4_mod013_closure.json"
)


def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def pp(value):
    return f"{value * 100:.4f}%"


def delta_pp(a, b):
    return (b - a) * 100.0


def main():
    print(
        "T4-MOD-013 T4 closure analysis"
    )
    print()

    r1 = load_json(
        RESULTS_DIR
        / "t4_r1_metrics.json"
    )

    mod007 = load_json(
        RESULTS_DIR
        / "t4_mod007_full_results.json"
    )

    mod008 = load_json(
        RESULTS_DIR
        / "t4_mod008_full.json"
    )

    mod011 = load_json(
        RESULTS_DIR
        / "t4_mod011_full.json"
    )

    mod012 = load_json(
        RESULTS_DIR
        / "t4_mod012_analysis.json"
    )

    print("POPULATION")

    train_rows = mod011[
        "population"
    ]["train_rows"]

    evaluation_rows = mod011[
        "population"
    ]["evaluation_rows"]

    covered_rows = mod011[
        "population"
    ]["covered_rows"]

    unseen_rows = mod011[
        "population"
    ]["unseen_rows"]

    candidates = mod011[
        "population"
    ]["training_candidates"]

    print(
        f"Training rows       : {train_rows}"
    )

    print(
        f"Evaluation rows     : {evaluation_rows}"
    )

    print(
        f"Covered rows        : {covered_rows}"
    )

    print(
        f"Unseen-target rows  : {unseen_rows}"
    )

    print(
        f"Training candidates : {candidates}"
    )

    print()

    unseen_rate = (
        unseen_rows
        / evaluation_rows
    )

    print(
        f"Unseen-target rate  : "
        f"{pp(unseen_rate)}"
    )

    print()

    print(
        "EXPERIMENT SUMMARY"
    )

    r1_metrics = r1[
        "metrics"
    ]

    mod007_metrics = mod007[
        "metrics_overall"
    ]

    mod008_metrics = mod008[
        "retrieval"
    ]["overall"]

    mod011_metrics = mod011[
        "retrieval"
    ]["overall"]

    print()

    print(
        f"{'Metric':<12}"
        f"{'R1':>12}"
        f"{'MOD007':>12}"
        f"{'MOD008':>12}"
        f"{'BM25':>12}"
    )

    experiment_rows = []

    for label, r1_key, ranking_key in [
        (
            "Hit@1",
            "top1_accuracy",
            "hit_at_1",
        ),
        (
            "Hit@3",
            "top3_accuracy",
            "hit_at_3",
        ),
        (
            "Hit@5",
            "top5_accuracy",
            "hit_at_5",
        ),
        (
            "Hit@10",
            "top10_accuracy",
            "hit_at_10",
        ),
        (
            "Hit@20",
            None,
            "hit_at_20",
        ),
    ]:
        r1_value = (
            r1_metrics.get(r1_key)
            if r1_key
            else None
        )

        mod007_value = (
            mod007_metrics.get(
                ranking_key
            )
        )

        mod008_value = (
            mod008_metrics.get(
                ranking_key
            )
        )

        mod011_value = (
            mod011_metrics.get(
                ranking_key
            )
        )

        def fmt(value):
            return (
                "N/A"
                if value is None
                else f"{value:.6f}"
            )

        print(
            f"{label:<12}"
            f"{fmt(r1_value):>12}"
            f"{fmt(mod007_value):>12}"
            f"{fmt(mod008_value):>12}"
            f"{fmt(mod011_value):>12}"
        )

        experiment_rows.append(
            {
                "metric": label,
                "r1": r1_value,
                "mod007": mod007_value,
                "mod008": mod008_value,
                "mod011_bm25": mod011_value,
            }
        )

    print()

    print(
        "BM25 RANKING METRICS"
    )

    print(
        f"MRR     : "
        f"{mod011_metrics['mrr']:.6f}"
    )

    print(
        f"NDCG@5  : "
        f"{mod011_metrics['ndcg_at_5']:.6f}"
    )

    print(
        f"NDCG@10 : "
        f"{mod011_metrics['ndcg_at_10']:.6f}"
    )

    print()

    print(
        "BM25 VS MOD-007"
    )

    bm25_deltas = {}

    for key in [
        "hit_at_1",
        "hit_at_3",
        "hit_at_5",
        "hit_at_10",
        "hit_at_20",
        "mrr",
        "ndcg_at_5",
        "ndcg_at_10",
    ]:
        a = mod007_metrics.get(
            key
        )

        b = mod011_metrics.get(
            key
        )

        if (
            a is not None
            and b is not None
        ):
            delta = b - a

            bm25_deltas[key] = {
                "mod007": a,
                "mod011_bm25": b,
                "delta": delta,
                "delta_percentage_points":
                    delta * 100.0,
            }

            print(
                f"{key.upper():<15}"
                f"{delta:+.6f}"
                f" ({delta * 100:+.4f} pp)"
            )

    print()

    print(
        "TRUE-ASSIGNEE "
        "RETRIEVAL COVERAGE"
    )

    mod007_coverage = mod012[
        "true_assignee_retrieval_coverage"
    ]["mod007"]

    mod011_coverage = mod012[
        "true_assignee_retrieval_coverage"
    ]["mod011"]

    coverage_delta = (
        mod011_coverage
        - mod007_coverage
    )

    print(
        f"MOD-007 : "
        f"{pp(mod007_coverage)}"
    )

    print(
        f"BM25    : "
        f"{pp(mod011_coverage)}"
    )

    print(
        f"Delta   : "
        f"{coverage_delta:+.4f} "
        f"({coverage_delta * 100:+.4f} pp)"
    )

    print()

    print(
        "OPEN-WORLD LIMITATION"
    )

    print(
        f"Unseen targets : "
        f"{unseen_rows}"
    )

    print(
        f"Unseen rate    : "
        f"{pp(unseen_rate)}"
    )

    print(
        "These targets were "
        "absent from the "
        "training candidate "
        "space and therefore "
        "cannot be retrieved "
        "by training-history "
        "retrieval."
    )

    print()

    print(
        "LONG-TAIL LIMITATION"
    )

    bm25_support = mod011[
        "historical_support_stratification"
    ]

    support_summary = {}

    for bucket in [
        "1",
        "2-5",
        "6-10",
        "11-20",
        "21-50",
        "51-100",
        "101+",
    ]:
        result = bm25_support.get(
            bucket
        )

        if result is None:
            continue

        support_summary[bucket] = {
            "rows": result["rows"],
            "hit_at_1": result[
                "hit_at_1"
            ]
            if "hit_at_1" in result
            else None,
            "hit_at_20": result[
                "hit_at_20"
            ]
            if "hit_at_20" in result
            else None,
            "retrieval_coverage_at_20":
                result.get(
                    "retrieval_coverage_at_20"
                ),
        }

    for bucket, result in (
        support_summary.items()
    ):
        print(
            f"{bucket:<8}"
            f"rows={result['rows']}"
            f" "
            f"coverage@20="
            f"{result.get('retrieval_coverage_at_20')}"
        )

    print()

    print(
        "T4 EVIDENCE SYNTHESIS"
    )

    findings = [
        (
            "Historical retrieval is "
            "feasible at full scale."
        ),
        (
            "BM25 provides modest "
            "improvement over the "
            "Word TF-IDF retrieval "
            "baseline on the same "
            "evaluation population."
        ),
        (
            "The true-assignee "
            "retrieval coverage "
            "remains below 50% of "
            "the training-observed "
            "evaluation population."
        ),
        (
            "Performance remains "
            "strongly dependent on "
            "historical assignee "
            "support."
        ),
        (
            "Unseen evaluation "
            "assignees cannot be "
            "retrieved by a "
            "training-history-only "
            "candidate system."
        ),
        (
            "Changing lexical "
            "retrieval representation "
            "does not remove the "
            "open-world or long-tail "
            "limitations."
        ),
    ]

    for i, finding in enumerate(
        findings,
        start=1,
    ):
        print(
            f"{i}. {finding}"
        )

    print()

    print(
        "DEFENSIBLE SYSTEM ROLE"
    )

    system_role = (
        "SECONDARY_DECISION_SUPPORT_SIGNAL"
    )

    closure_status = (
        "SUPPORTED_WITH_LIMITATIONS"
    )

    print(
        f"System role : "
        f"{system_role}"
    )

    print(
        f"Closure     : "
        f"{closure_status}"
    )

    print()

    print(
        "NOT SUPPORTED"
    )

    unsupported_claims = [
        "Universal automatic assignee assignment",
        "Guaranteed correct routing",
        "Operational assignee eligibility",
        "Reliable routing for unseen assignees",
        "Autonomous assignment without human review",
    ]

    for item in unsupported_claims:
        print(
            f"- {item}"
        )

    print()

    print(
        "CONTROLS"
    )

    controls = {
        "raw_mozilla_accessed": False,
        "target_reconstructed": False,
        "test_used": False,
        "future_features_used": False,
        "split_changed": False,
        "operational_eligibility_established":
            False,
        "unseen_targets_removed": False,
        "target_side_fields_used": False,
    }

    print(
        json.dumps(
            controls,
            indent=2,
        )
    )

    output = {
        "experiment": "T4-MOD-013",
        "status": "COMPLETE",
        "closure_status": closure_status,
        "system_role": system_role,
        "population": {
            "train_rows": train_rows,
            "evaluation_rows": evaluation_rows,
            "covered_rows": covered_rows,
            "unseen_rows": unseen_rows,
            "unseen_rate": unseen_rate,
            "training_candidates": candidates,
        },
        "experiment_summary":
            experiment_rows,
        "bm25_vs_mod007":
            bm25_deltas,
        "true_assignee_retrieval_coverage": {
            "mod007": mod007_coverage,
            "mod011_bm25": mod011_coverage,
            "delta": coverage_delta,
        },
        "bm25_ranking_metrics": {
            "mrr": mod011_metrics[
                "mrr"
            ],
            "ndcg_at_5":
                mod011_metrics[
                    "ndcg_at_5"
                ],
            "ndcg_at_10":
                mod011_metrics[
                    "ndcg_at_10"
                ],
        },
        "long_tail": support_summary,
        "open_world": {
            "unseen_rows": unseen_rows,
            "unseen_rate": unseen_rate,
            "retrievable_by_training_history":
                False,
        },
        "findings": findings,
        "unsupported_claims":
            unsupported_claims,
        "controls": controls,
        "source_artifacts": [
            "t4_r1_metrics.json",
            "t4_mod007_full_results.json",
            "t4_mod008_full.json",
            "t4_mod011_full.json",
            "t4_mod012_analysis.json",
        ],
    }

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            output,
            f,
            indent=2,
        )

    print()

    print(
        f"CLOSURE_SAVED="
        f"{OUTPUT_PATH}"
    )

    print(
        "T4-MOD-013_COMPLETE"
    )


if __name__ == "__main__":
    main()