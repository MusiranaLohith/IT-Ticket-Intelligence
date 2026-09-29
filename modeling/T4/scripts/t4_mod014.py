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


def main():
    print(
        "T4-MOD-014 closure artifact correction"
    )
    print()

    mod011 = load_json(
        RESULTS_DIR
        / "t4_mod011_full.json"
    )

    mod012 = load_json(
        RESULTS_DIR
        / "t4_mod012_analysis.json"
    )

    mod013 = load_json(
        RESULTS_DIR
        / "t4_mod013_closure.json"
    )

    support = mod011[
        "historical_support_stratification"
    ]

    corrected_support = {}

    print(
        "CORRECTING LONG-TAIL "
        "REPORTING"
    )
    print()

    for bucket, result in support.items():
        corrected_support[bucket] = {
            "rows": result["rows"],
            "hit_at_1": result["hit_at_1"],
            "hit_at_5": result["hit_at_5"],
            "hit_at_10": result["hit_at_10"],
            "hit_at_20": result["hit_at_20"],
        }

        print(
            f"{bucket:<8}"
            f"rows={result['rows']} "
            f"Hit@1={result['hit_at_1']:.6f} "
            f"Hit@5={result['hit_at_5']:.6f} "
            f"Hit@10={result['hit_at_10']:.6f} "
            f"Hit@20={result['hit_at_20']:.6f}"
        )

    print()

    print(
        "VERIFYING RETRIEVAL COVERAGE"
    )

    coverage = mod012[
        "true_assignee_retrieval_coverage"
    ]

    print(
        f"MOD-007 Top-20 coverage: "
        f"{coverage['mod007']:.6f}"
    )

    print(
        f"BM25 Top-20 coverage: "
        f"{coverage['mod011']:.6f}"
    )

    print(
        f"Delta: "
        f"{coverage['delta_mod011_minus_mod007']:.6f}"
    )

    print()

    print(
        "VERIFYING OPEN-WORLD "
        "LIMITATION"
    )

    population = mod011[
        "population"
    ]

    unseen_rows = population[
        "unseen_rows"
    ]

    evaluation_rows = population[
        "evaluation_rows"
    ]

    unseen_rate = (
        unseen_rows
        / evaluation_rows
    )

    print(
        f"Unseen rows: {unseen_rows}"
    )

    print(
        f"Unseen rate: "
        f"{unseen_rate:.6f}"
    )

    print()

    corrected = dict(mod013)

    corrected[
        "experiment"
    ] = "T4-MOD-014"

    corrected[
        "artifact_type"
    ] = (
        "Corrected final T4 closure artifact"
    )

    corrected[
        "closure_status"
    ] = (
        "SUPPORTED_WITH_LIMITATIONS"
    )

    corrected[
        "system_role"
    ] = (
        "SECONDARY_DECISION_SUPPORT_SIGNAL"
    )

    corrected[
        "long_tail"
    ] = corrected_support

    corrected[
        "open_world"
    ] = {
        "unseen_rows": unseen_rows,
        "unseen_rate": unseen_rate,
        "retrievable_by_training_history":
            False,
    }

    corrected[
        "true_assignee_retrieval_coverage"
    ] = {
        "mod007": coverage["mod007"],
        "mod011_bm25": coverage["mod011"],
        "delta": coverage[
            "delta_mod011_minus_mod007"
        ],
    }

    corrected[
        "controls"
    ] = {
        "raw_mozilla_accessed": False,
        "target_reconstructed": False,
        "test_used": False,
        "future_features_used": False,
        "split_changed": False,
        "operational_eligibility_established":
            False,
        "unseen_targets_removed": False,
        "target_side_fields_used": False,
        "model_retrained": False,
        "new_predictions_created": False,
    }

    corrected[
        "correction"
    ] = {
        "source_artifact":
            "t4_mod013_closure.json",
        "issue":
            "Long-tail reporting referenced a "
            "nonexistent coverage_at_20 field "
            "and produced None values.",
        "resolution":
            "Replaced those values with the "
            "actual Hit@1/5/10/20 metrics "
            "from the completed MOD-011 "
            "historical-support analysis.",
        "raw_data_accessed": False,
        "modeling_repeated": False,
        "retrieval_repeated": False,
    }

    corrected[
        "source_artifacts"
    ] = [
        "t4_r1_metrics.json",
        "t4_mod007_full_results.json",
        "t4_mod008_full.json",
        "t4_mod011_full.json",
        "t4_mod012_analysis.json",
        "t4_mod013_closure.json",
    ]

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            corrected,
            f,
            indent=2,
        )

    print(
        f"CORRECTED_CLOSURE_SAVED="
        f"{OUTPUT_PATH}"
    )

    print(
        "T4-MOD-014_COMPLETE"
    )


if __name__ == "__main__":
    main()