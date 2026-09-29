from pathlib import Path
import json
import pandas as pd


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

INPUT_ARTIFACT = (
    PROJECT_ROOT
    / "modeling"
    / "T4"
    / "derived"
    / "t4_features.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "T4"
    / "derived"
)

TRAIN_OUTPUT = OUTPUT_DIR / "t4_train.csv"
EVAL_OUTPUT = OUTPUT_DIR / "t4_eval.csv"
SPLIT_REPORT = OUTPUT_DIR / "t4_split_report.json"


EXPECTED_TOTAL = 178_127
EXPECTED_TRAIN = 142_501
EXPECTED_EVAL = 35_626


def class_support(series):
    counts = series.value_counts()

    return {
        "classes": int(len(counts)),
        "min_support": int(counts.min()),
        "median_support": float(counts.median()),
        "mean_support": float(counts.mean()),
        "max_support": int(counts.max()),
        "singleton_classes": int((counts == 1).sum()),
        "classes_support_le_5": int((counts <= 5).sum()),
        "classes_support_le_10": int((counts <= 10).sum()),
        "classes_support_le_20": int((counts <= 20).sum()),
    }


def main():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not INPUT_ARTIFACT.exists():
        raise FileNotFoundError(
            "INPUT_ARTIFACT_NOT_FOUND="
            f"{INPUT_ARTIFACT}"
        )

    df = pd.read_csv(
        INPUT_ARTIFACT,
        dtype=str,
        keep_default_na=False,
    )

    df["__creation_parsed"] = pd.to_datetime(
        df["Creation time"],
        errors="coerce",
        utc=True,
    )

    if df["__creation_parsed"].isna().any():
        raise RuntimeError(
            "INVALID_CREATION_TIME_PRESENT"
        )

    # Deterministic chronological ordering.
    # ID is used only as a tie-breaker.
    df = df.sort_values(
        by=["__creation_parsed", "ID"],
        kind="mergesort",
    ).reset_index(drop=True)

    total_rows = len(df)

    if total_rows != EXPECTED_TOTAL:
        raise RuntimeError(
            f"UNEXPECTED_TOTAL_ROWS={total_rows}"
        )

    train = df.iloc[:EXPECTED_TRAIN].copy()
    evaluation = df.iloc[
        EXPECTED_TRAIN:
    ].copy()

    train = train.drop(
        columns=["__creation_parsed"]
    )

    evaluation = evaluation.drop(
        columns=["__creation_parsed"]
    )

    train.to_csv(
        TRAIN_OUTPUT,
        index=False,
    )

    evaluation.to_csv(
        EVAL_OUTPUT,
        index=False,
    )

    train_ids = set(train["ID"])
    eval_ids = set(evaluation["ID"])

    id_overlap = train_ids.intersection(
        eval_ids
    )

    train_targets = set(
        train["target_assignee"]
    )

    eval_targets = set(
        evaluation["target_assignee"]
    )

    covered_eval_targets = (
        eval_targets.intersection(
            train_targets
        )
    )

    unseen_eval_targets = (
        eval_targets.difference(
            train_targets
        )
    )

    eval_target_covered_rows = int(
        evaluation["target_assignee"]
        .isin(train_targets)
        .sum()
    )

    eval_target_unseen_rows = int(
        len(evaluation)
        - eval_target_covered_rows
    )

    train_start = train["Creation time"].min()
    train_end = train["Creation time"].max()

    eval_start = evaluation["Creation time"].min()
    eval_end = evaluation["Creation time"].max()

    train_profile = class_support(
        train["target_assignee"]
    )

    eval_profile = class_support(
        evaluation["target_assignee"]
    )

    unseen_rate = (
        eval_target_unseen_rows
        / len(evaluation)
    )

    report = {
        "operation": "T4-MOD-004",

        "status": "PASS",

        "input_artifact":
            str(INPUT_ARTIFACT),

        "train_output":
            str(TRAIN_OUTPUT),

        "evaluation_output":
            str(EVAL_OUTPUT),

        "total_rows":
            total_rows,

        "train_rows":
            len(train),

        "evaluation_rows":
            len(evaluation),

        "chronological_order": {
            "sort_keys": [
                "Creation time",
                "ID",
            ],

            "train_start":
                train_start,

            "train_end":
                train_end,

            "evaluation_start":
                eval_start,

            "evaluation_end":
                eval_end,

            "random_shuffle":
                False,
        },

        "id_integrity": {
            "train_unique_ids":
                len(train_ids),

            "evaluation_unique_ids":
                len(eval_ids),

            "overlap_count":
                len(id_overlap),

            "overlap":
                len(id_overlap) > 0,
        },

        "candidate_space": {
            "training_observed_candidates":
                len(train_targets),

            "evaluation_distinct_targets":
                len(eval_targets),

            "covered_evaluation_distinct_targets":
                len(covered_eval_targets),

            "unseen_evaluation_distinct_targets":
                len(unseen_eval_targets),

            "covered_evaluation_rows":
                eval_target_covered_rows,

            "unseen_evaluation_rows":
                eval_target_unseen_rows,

            "unseen_evaluation_rate":
                unseen_rate,
        },

        "train_class_support":
            train_profile,

        "evaluation_class_support":
            eval_profile,

        "controls": {
            "chronological_split":
                True,

            "random_shuffle":
                False,

            "candidate_space_from_training_only":
                True,

            "unseen_targets_retained":
                True,

            "unseen_targets_not_negative":
                True,

            "raw_mozilla_accessed":
                False,

            "model_trained":
                False,

            "predictions_created":
                False,

            "test_used":
                False,
        },
    }

    SPLIT_REPORT.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("T4-MOD-004_COMPLETE")
    print(
        f"TOTAL_ROWS={total_rows}"
    )
    print(
        f"TRAIN_ROWS={len(train)}"
    )
    print(
        f"EVALUATION_ROWS={len(evaluation)}"
    )
    print(
        "TRAIN_START="
        f"{train_start}"
    )
    print(
        "TRAIN_END="
        f"{train_end}"
    )
    print(
        "EVALUATION_START="
        f"{eval_start}"
    )
    print(
        "EVALUATION_END="
        f"{eval_end}"
    )
    print(
        "ID_OVERLAP_COUNT="
        f"{len(id_overlap)}"
    )
    print(
        "TRAINING_OBSERVED_CANDIDATES="
        f"{len(train_targets)}"
    )
    print(
        "EVALUATION_DISTINCT_TARGETS="
        f"{len(eval_targets)}"
    )
    print(
        "COVERED_EVALUATION_DISTINCT_TARGETS="
        f"{len(covered_eval_targets)}"
    )
    print(
        "UNSEEN_EVALUATION_DISTINCT_TARGETS="
        f"{len(unseen_eval_targets)}"
    )
    print(
        "COVERED_EVALUATION_ROWS="
        f"{eval_target_covered_rows}"
    )
    print(
        "UNSEEN_EVALUATION_ROWS="
        f"{eval_target_unseen_rows}"
    )
    print(
        f"UNSEEN_EVALUATION_RATE={unseen_rate:.8f}"
    )

    print(
        "TRAIN_SINGLETON_CLASSES="
        f"{train_profile['singleton_classes']}"
    )

    print(
        "TRAIN_CLASSES_SUPPORT_LE_5="
        f"{train_profile['classes_support_le_5']}"
    )

    print(
        "TRAIN_CLASSES_SUPPORT_LE_10="
        f"{train_profile['classes_support_le_10']}"
    )

    print(
        "TRAIN_CLASSES_SUPPORT_LE_20="
        f"{train_profile['classes_support_le_20']}"
    )

    print(
        "EVAL_SINGLETON_CLASSES="
        f"{eval_profile['singleton_classes']}"
    )

    print(
        "EVAL_CLASSES_SUPPORT_LE_5="
        f"{eval_profile['classes_support_le_5']}"
    )

    print(
        "EVAL_CLASSES_SUPPORT_LE_10="
        f"{eval_profile['classes_support_le_10']}"
    )

    print(
        "EVAL_CLASSES_SUPPORT_LE_20="
        f"{eval_profile['classes_support_le_20']}"
    )

    print(
        "STATUS=PASS"
    )

    print(
        "RAW_MOZILLA_ACCESSED=False"
    )

    print(
        "MODEL_TRAINED=False"
    )

    print(
        "PREDICTIONS_CREATED=False"
    )

    print(
        "TEST_USED=False"
    )


if __name__ == "__main__":
    main()