from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T1_ROOT = PROJECT_ROOT / "modeling" / "T1"

SPLIT_PATH = T1_ROOT / "splits" / "t1_split.csv"
MODEL_PATH = T1_ROOT / "baselines" / "t1_it_support_char_svm.joblib"
CONTRACT_PATH = T1_ROOT / "contracts" / "t1_contract.json"


def main() -> None:
    print("=" * 76)
    print("FMP-01 / T1 CALIBRATION FEASIBILITY")
    print("=" * 76)

    print()
    print("-" * 76)
    print("1. INPUT ARTIFACTS")
    print("-" * 76)

    for path in [SPLIT_PATH, MODEL_PATH, CONTRACT_PATH]:
        print(
            f"{path.relative_to(PROJECT_ROOT)}"
            f" | exists={path.exists()}"
            f" | size={path.stat().st_size if path.exists() else 'NA'}"
        )

    if not SPLIT_PATH.exists():
        raise FileNotFoundError(SPLIT_PATH)

    if not MODEL_PATH.exists():
        raise FileNotFoundError(MODEL_PATH)

    if not CONTRACT_PATH.exists():
        raise FileNotFoundError(CONTRACT_PATH)

    print()
    print("-" * 76)
    print("2. T1 SPLIT INSPECTION")
    print("-" * 76)

    df = pd.read_csv(SPLIT_PATH)

    print(f"rows={len(df)}")
    print(f"columns={list(df.columns)}")

    print()
    print("Column dtypes:")
    print(df.dtypes.to_string())

    print()
    print("Potential split-role columns:")

    for column in df.columns:
        lower = column.lower()

        if any(
            term in lower
            for term in [
                "split",
                "partition",
                "role",
                "set",
                "fold",
            ]
        ):
            print(
                f"  {column}: "
                f"{df[column].value_counts(dropna=False).to_dict()}"
            )

    print()
    print("Potential target columns:")

    for column in df.columns:
        lower = column.lower()

        if any(
            term in lower
            for term in [
                "category",
                "target",
                "label",
                "truth",
                "class",
            ]
        ):
            print(
                f"  {column}: "
                f"nunique={df[column].nunique(dropna=False)}"
            )

    print()
    print("-" * 76)
    print("3. DEVELOPMENT / EVALUATION POPULATION")
    print("-" * 76)

    # Determine the likely split column from known T1 structure.
    split_column = None

    for candidate in [
        "split",
        "partition",
        "set",
        "dataset_split",
        "role",
    ]:
        if candidate in df.columns:
            split_column = candidate
            break

    if split_column is None:
        for column in df.columns:
            lower = column.lower()

            if "split" in lower or "partition" in lower:
                split_column = column
                break

    if split_column is None:
        print("split_column: NOT_IDENTIFIED")
    else:
        print(f"split_column: {split_column}")
        print(
            "split_values:",
            df[split_column].value_counts(dropna=False).to_dict(),
        )

    if split_column is not None:
        split_values = {
            str(value).lower(): value
            for value in df[split_column].dropna().unique()
        }

        development_value = None
        evaluation_value = None

        for normalized, original in split_values.items():
            if normalized in {
                "development",
                "dev",
                "train",
                "training",
            }:
                development_value = original

            if normalized in {
                "evaluation",
                "eval",
                "test",
                "testing",
            }:
                evaluation_value = original

        if development_value is not None:
            development = df[
                df[split_column] == development_value
            ].copy()
        else:
            development = pd.DataFrame()

        if evaluation_value is not None:
            evaluation = df[
                df[split_column] == evaluation_value
            ].copy()
        else:
            evaluation = pd.DataFrame()

        print(
            f"development_records={len(development)}"
        )
        print(
            f"evaluation_records={len(evaluation)}"
        )

        if len(evaluation) > 0:
            print(
                "evaluation_population_present=True"
            )

    else:
        development = pd.DataFrame()
        evaluation = pd.DataFrame()

    print()
    print("-" * 76)
    print("4. DEVELOPMENT TARGET DISTRIBUTION")
    print("-" * 76)

    target_column = None

    for candidate in [
        "category_truth",
        "target",
        "label",
        "category",
        "class",
    ]:
        if candidate in df.columns:
            target_column = candidate
            break

    if target_column is None:
        for column in df.columns:
            lower = column.lower()

            if (
                "category" in lower
                or "target" in lower
                or "label" in lower
                or "truth" in lower
            ):
                target_column = column
                break

    if target_column is None:
        print("target_column: NOT_IDENTIFIED")
    else:
        print(f"target_column: {target_column}")

        if len(development) > 0:
            print(
                development[target_column]
                .value_counts(dropna=False)
                .to_string()
            )

    print()
    print("-" * 76)
    print("5. DEVELOPMENT NORMALIZED-TEXT GROUP STRUCTURE")
    print("-" * 76)

    normalized_column = None

    for candidate in [
        "normalized_text",
        "normalized_ticket_text",
        "text_normalized",
    ]:
        if candidate in df.columns:
            normalized_column = candidate
            break

    if normalized_column is None:
        for column in df.columns:
            if "normalized" in column.lower():
                normalized_column = column
                break

    if normalized_column is None:
        print("normalized_text_column: NOT_IDENTIFIED")
    elif len(development) > 0:
        print(
            f"normalized_text_column: {normalized_column}"
        )

        group_sizes = (
            development
            .groupby(normalized_column, dropna=False)
            .size()
        )

        repeated_groups = group_sizes[group_sizes > 1]

        print(
            f"development_unique_normalized_texts="
            f"{len(group_sizes)}"
        )

        print(
            f"development_repeated_normalized_text_groups="
            f"{len(repeated_groups)}"
        )

        print(
            f"development_records_in_repeated_groups="
            f"{int(repeated_groups.sum())}"
        )

    print()
    print("-" * 76)
    print("6. NATIVE MODEL INTERFACE")
    print("-" * 76)

    model = joblib.load(MODEL_PATH)

    print(f"python_type={type(model)}")

    print(
        f"has_predict="
        f"{callable(getattr(model, 'predict', None))}"
    )

    print(
        f"has_predict_proba="
        f"{callable(getattr(model, 'predict_proba', None))}"
    )

    print(
        f"has_decision_function="
        f"{callable(getattr(model, 'decision_function', None))}"
    )

    print(
        f"has_transform="
        f"{callable(getattr(model, 'transform', None))}"
    )

    print()
    print("Model attributes:")
    print(
        [
            name
            for name in dir(model)
            if not name.startswith("_")
            and name in {
                "predict",
                "predict_proba",
                "decision_function",
                "transform",
                "named_steps",
                "steps",
                "classes_",
                "n_features_in_",
            }
        ]
    )

    if hasattr(model, "classes_"):
        print(
            f"classes_={getattr(model, 'classes_')}"
        )

    print()
    print("-" * 76)
    print("7. CONTRACT CALIBRATION POLICY")
    print("-" * 76)

    with CONTRACT_PATH.open("r", encoding="utf-8") as f:
        contract = json.load(f)

    print(
        "model_selected:",
        contract.get("model_policy", {})
        .get("model_selected"),
    )

    print(
        "training_started:",
        contract.get("model_policy", {})
        .get("training_started"),
    )

    print(
        "evaluation_metrics:",
        contract.get("evaluation", {})
        .get("metrics"),
    )

    print()
    print("-" * 76)
    print("8. LOCKED-EVALUATION PROTECTION")
    print("-" * 76)

    print(
        "This operation generates no model predictions."
    )
    print(
        "This operation performs no calibration fitting."
    )
    print(
        "This operation performs no threshold optimization."
    )
    print(
        "The 446-record evaluation population is not used "
        "for calibration selection."
    )

    print()
    print("-" * 76)
    print("9. FEASIBILITY CONCLUSION")
    print("-" * 76)

    feasibility_conditions = {
        "development_population_present": len(development) == 1783,
        "evaluation_population_present": len(evaluation) == 446,
        "native_model_loaded": model is not None,
        "decision_function_available": callable(
            getattr(model, "decision_function", None)
        ),
        "evaluation_protected": True,
    }

    for name, value in feasibility_conditions.items():
        print(f"{name}: {value}")

    if all(feasibility_conditions.values()):
        print()
        print(
            "PRELIMINARY_RESULT: "
            "TASK_SPECIFIC_CALIBRATION_FEASIBILITY_SUPPORTED"
        )
        print(
            "Interpretation: the existing development population "
            "and native SVM decision interface are sufficient to "
            "consider a separate development-only calibration "
            "investigation."
        )
    else:
        print()
        print(
            "PRELIMINARY_RESULT: "
            "TASK_SPECIFIC_CALIBRATION_FEASIBILITY_NOT_ESTABLISHED"
        )

    print()
    print(
        "IMPORTANT: No calibration model, threshold, probability, "
        "or architecture decision was created by this operation."
    )

    print()
    print("=" * 76)
    print("END OF FMP-01 / T1 CALIBRATION FEASIBILITY")
    print("=" * 76)


if __name__ == "__main__":
    main()