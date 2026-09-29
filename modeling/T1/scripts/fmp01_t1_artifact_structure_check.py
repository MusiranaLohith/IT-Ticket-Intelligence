from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T1_ROOT = PROJECT_ROOT / "modeling" / "T1"

SPLIT_PATH = T1_ROOT / "splits" / "t1_split.csv"
MODEL_PATH = T1_ROOT / "baselines" / "t1_it_support_char_svm.joblib"


def main() -> None:
    print("=" * 76)
    print("FMP-01 / T1 ARTIFACT STRUCTURE + MODELING-SPLIT CHECK")
    print("=" * 76)

    # ---------------------------------------------------------------
    # 1. SPLIT
    # ---------------------------------------------------------------

    print()
    print("-" * 76)
    print("1. CONTROLLED MODELING SPLIT")
    print("-" * 76)

    df = pd.read_csv(SPLIT_PATH)

    print(f"rows={len(df)}")
    print(f"columns={list(df.columns)}")

    required_split_column = "modeling_split"

    if required_split_column not in df.columns:
        raise RuntimeError(
            "Expected modeling_split column was not found."
        )

    print()
    print(
        df[required_split_column]
        .value_counts(dropna=False)
        .to_string()
    )

    development = df[
        df[required_split_column] == "development"
    ].copy()

    evaluation = df[
        df[required_split_column] == "evaluation"
    ].copy()

    print()
    print(f"development_records={len(development)}")
    print(f"evaluation_records={len(evaluation)}")

    print()
    print("Source partition preserved separately:")
    print(
        df["source_partition"]
        .value_counts(dropna=False)
        .to_string()
    )

    # ---------------------------------------------------------------
    # 2. TARGET
    # ---------------------------------------------------------------

    print()
    print("-" * 76)
    print("2. DEVELOPMENT TARGET DISTRIBUTION")
    print("-" * 76)

    print(
        development["category_truth"]
        .value_counts(dropna=False)
        .to_string()
    )

    print()
    print("Evaluation target distribution:")
    print(
        evaluation["category_truth"]
        .value_counts(dropna=False)
        .to_string()
    )

    # ---------------------------------------------------------------
    # 3. MODEL ARTIFACT STRUCTURE
    # ---------------------------------------------------------------

    print()
    print("-" * 76)
    print("3. SERIALIZED MODEL ARTIFACT STRUCTURE")
    print("-" * 76)

    artifact = joblib.load(MODEL_PATH)

    print(f"top_level_type={type(artifact)}")

    if isinstance(artifact, dict):
        print(f"dict_keys={list(artifact.keys())}")

        print()

        for key, value in artifact.items():
            print(f"KEY: {key}")
            print(f"  type={type(value)}")

            if hasattr(value, "predict"):
                print("  has_predict=True")
            else:
                print("  has_predict=False")

            if hasattr(value, "predict_proba"):
                print("  has_predict_proba=True")
            else:
                print("  has_predict_proba=False")

            if hasattr(value, "decision_function"):
                print("  has_decision_function=True")
            else:
                print("  has_decision_function=False")

            if hasattr(value, "transform"):
                print("  has_transform=True")
            else:
                print("  has_transform=False")

            if hasattr(value, "classes_"):
                print(
                    f"  classes_={value.classes_}"
                )

            print()

    else:
        print("artifact_is_not_dict=True")

        print(
            f"has_predict="
            f"{hasattr(artifact, 'predict')}"
        )

        print(
            f"has_predict_proba="
            f"{hasattr(artifact, 'predict_proba')}"
        )

        print(
            f"has_decision_function="
            f"{hasattr(artifact, 'decision_function')}"
        )

    # ---------------------------------------------------------------
    # 4. RECURSIVE STRUCTURE FOR COMMON CONTAINER TYPES
    # ---------------------------------------------------------------

    print()
    print("-" * 76)
    print("4. CONTAINER STRUCTURE")
    print("-" * 76)

    if isinstance(artifact, dict):

        for key, value in artifact.items():

            if isinstance(value, dict):
                print(
                    f"{key}: nested_dict_keys="
                    f"{list(value.keys())}"
                )

            elif isinstance(value, (list, tuple)):
                print(
                    f"{key}: "
                    f"{type(value).__name__}, "
                    f"length={len(value)}"
                )

            else:
                print(
                    f"{key}: "
                    f"{type(value).__name__}"
                )

    # ---------------------------------------------------------------
    # 5. LOCKED EVALUATION PROTECTION
    # ---------------------------------------------------------------

    print()
    print("-" * 76)
    print("5. LOCKED EVALUATION PROTECTION")
    print("-" * 76)

    print(
        "Predictions generated: NO"
    )

    print(
        "Calibration fitted: NO"
    )

    print(
        "Threshold selected: NO"
    )

    print(
        "Model modified: NO"
    )

    print(
        f"controlled_development_population={len(development)}"
    )

    print(
        f"locked_evaluation_population={len(evaluation)}"
    )

    # ---------------------------------------------------------------
    # 6. STATUS
    # ---------------------------------------------------------------

    print()
    print("-" * 76)
    print("6. OPERATION STATUS")
    print("-" * 76)

    if (
        len(development) == 1783
        and len(evaluation) == 446
        and isinstance(artifact, dict)
    ):
        print(
            "STATUS: PASS"
        )
        print(
            "The controlled T1 modeling populations are correctly "
            "identified and the serialized artifact structure has "
            "been exposed for the next feasibility decision."
        )
    else:
        print(
            "STATUS: BLOCKED"
        )

    print()
    print("=" * 76)
    print("END OF FMP-01 / T1 ARTIFACT STRUCTURE CHECK")
    print("=" * 76)


if __name__ == "__main__":
    main()