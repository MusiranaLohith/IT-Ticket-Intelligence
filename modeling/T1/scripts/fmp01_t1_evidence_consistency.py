from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T1_ROOT = PROJECT_ROOT / "modeling" / "T1"


FILES = {
    "contract": T1_ROOT / "contracts" / "t1_contract.json",
    "split_report": T1_ROOT / "splits" / "t1_split_report.json",
    "three_model": T1_ROOT / "analysis" / "t1_it_support_3model_compare.json",
    "char_analysis": T1_ROOT / "analysis" / "t1_it_support_char_svm_analysis.json",
    "eval_groups": T1_ROOT / "analysis" / "t1_it_support_eval_groups.json",
    "group_eval": T1_ROOT / "analysis" / "t1_it_support_group_eval.json",
    "subset_compare": T1_ROOT / "analysis" / "t1_it_support_model_subset_compare.json",
    "split_check": T1_ROOT / "analysis" / "t1_it_support_split_check.json",
    "subset_analysis": T1_ROOT / "analysis" / "t1_it_support_subset_analysis.json",
    "errors": T1_ROOT / "analysis" / "t1_it_support_svm_errors.json",
    "char_report": T1_ROOT / "baselines" / "t1_it_support_char_svm_report.json",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        obj = json.load(f)

    if not isinstance(obj, dict):
        raise TypeError(f"Expected JSON object: {path}")

    return obj


def get_nested(
    obj: dict[str, Any],
    *keys: str,
    default: Any = None,
) -> Any:
    current: Any = obj

    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default

        current = current[key]

    return current


def print_value(label: str, value: Any) -> None:
    print(f"{label}: {value!r}")


def main() -> None:
    print("=" * 76)
    print("FMP-01 / T1 EVIDENCE CONSISTENCY & METRIC SEMANTICS AUDIT")
    print("=" * 76)

    reports: dict[str, dict[str, Any]] = {}

    print()
    print("-" * 76)
    print("1. LOADING EVIDENCE")
    print("-" * 76)

    for name, path in FILES.items():
        if not path.exists():
            print(f"[MISSING] {name}: {path}")
            continue

        reports[name] = load_json(path)
        print(
            f"[LOADED]  {name}: "
            f"{path.relative_to(PROJECT_ROOT)}"
        )

    print()
    print("-" * 76)
    print("2. CONTRACT MODEL POLICY")
    print("-" * 76)

    contract = reports["contract"]

    print_value(
        "contract_id",
        contract.get("contract_id"),
    )

    print_value(
        "contract_status",
        contract.get("status"),
    )

    print_value(
        "task",
        contract.get("task"),
    )

    model_policy = contract.get("model_policy", {})

    print_value(
        "model_policy.selected_model",
        model_policy.get("model_selected"),
    )

    print_value(
        "model_policy.training_started",
        model_policy.get("training_started"),
    )

    print_value(
        "model_policy.baseline_required_first",
        model_policy.get("baseline_required_first"),
    )

    print()
    print("-" * 76)
    print("3. FORMAL THREE-MODEL COMPARISON")
    print("-" * 76)

    three_model = reports["three_model"]

    print_value("status", three_model.get("status"))
    print_value(
        "evaluation_records",
        three_model.get("evaluation_records"),
    )
    print_value(
        "evaluation_used_for_fit",
        three_model.get("evaluation_used_for_fit"),
    )
    print_value(
        "models_retrained",
        three_model.get("models_retrained"),
    )
    print_value(
        "frozen_split_modified",
        three_model.get("frozen_split_modified"),
    )

    results = three_model.get("results", {})

    if isinstance(results, dict):
        for model_name, result in results.items():
            print()
            print(f"MODEL: {model_name}")

            if isinstance(result, dict):
                print_value("  accuracy", result.get("accuracy"))
                print_value("  macro_f1", result.get("macro_f1"))
                print_value("  weighted_f1", result.get("weighted_f1"))

    print()
    print("Rankings:")
    print(three_model.get("rankings"))

    print()
    print("-" * 76)
    print("4. WORD + CHARACTER SVM ANALYSIS")
    print("-" * 76)

    char_analysis = reports["char_analysis"]

    print_value("status", char_analysis.get("status"))
    print_value(
        "evaluation_records",
        char_analysis.get("evaluation_records"),
    )
    print_value(
        "overall_accuracy",
        char_analysis.get("overall_accuracy"),
    )
    print_value(
        "model_retrained",
        char_analysis.get("model_retrained"),
    )
    print_value(
        "evaluation_used_for_fit",
        char_analysis.get("evaluation_used_for_fit"),
    )
    print_value(
        "frozen_split_modified",
        char_analysis.get("frozen_split_modified"),
    )

    subset_summary = char_analysis.get("subset_summary", {})

    if isinstance(subset_summary, dict):
        for name, value in subset_summary.items():
            print()
            print(f"SUBSET: {name}")
            print(value)

    print()
    print("-" * 76)
    print("5. GROUP-LEVEL METRIC SEMANTICS")
    print("-" * 76)

    group_eval = reports["group_eval"]

    group_keys = [
        "evaluation_records",
        "record_correct",
        "record_incorrect",
        "record_accuracy",
        "unique_normalized_text_groups",
        "repeated_normalized_text_groups",
        "records_in_repeated_groups",
        "repeated_record_rate",
        "single_record_groups",
        "fully_correct_groups",
        "fully_correct_group_rate",
        "prediction_consistent_groups",
        "prediction_consistent_group_rate",
        "homogeneous_label_groups",
        "homogeneous_group_correct",
        "homogeneous_group_accuracy",
        "multi_label_normalized_text_groups",
        "records_in_multi_label_groups",
        "repeated_group_record_accuracy",
        "single_record_group_accuracy",
        "model_retrained",
        "evaluation_used_for_fit",
        "frozen_split_modified",
        "labels_modified",
        "raw_source_modified",
    ]

    for key in group_keys:
        print_value(key, group_eval.get(key))

    print()
    print("Referenced split path:")
    print(group_eval.get("split_path"))

    print()
    print("Referenced model path:")
    print(group_eval.get("model_path"))

    print()
    print("-" * 76)
    print("6. EVALUATION-GROUP AUDIT")
    print("-" * 76)

    eval_groups = reports["eval_groups"]

    print_value("status", eval_groups.get("status"))
    print_value("evaluation", eval_groups.get("evaluation"))
    print_value("integrity", eval_groups.get("integrity"))

    print()
    print("-" * 76)
    print("7. SPLIT INTEGRITY")
    print("-" * 76)

    split_report = reports["split_report"]

    split_keys = [
        "status",
        "seed",
        "total_records",
        "development_records",
        "evaluation_records",
        "total_normalized_text_groups",
        "evaluation_groups",
        "cross_split_groups",
        "missing_evaluation_classes",
        "evaluation_class_counts",
        "grouping_key",
        "source_partition_role",
        "source_partition_preserved",
        "labels_modified",
        "text_modified",
        "raw_source_modified",
        "objective_score",
    ]

    for key in split_keys:
        print_value(key, split_report.get(key))

    print()
    print("Methodological note:")
    print(split_report.get("methodological_note"))

    print()
    print("-" * 76)
    print("8. SPLIT CHECK")
    print("-" * 76)

    split_check = reports["split_check"]

    print_value("status", split_check.get("status"))
    print_value("summary", split_check.get("summary"))
    print_value("cross_split_groups", split_check.get("cross_split_groups"))
    print_value("raw_source_modified", split_check.get("raw_source_modified"))
    print_value("split_modified", split_check.get("split_modified"))
    print_value("labels_modified", split_check.get("labels_modified"))

    print()
    print("-" * 76)
    print("9. ERROR EVIDENCE")
    print("-" * 76)

    errors = reports["errors"]

    print_value("status", errors.get("status"))
    print_value("task", errors.get("task"))
    print_value("data", errors.get("data"))
    print_value("error_summary", errors.get("error_summary"))

    error_rows = errors.get("errors")

    if isinstance(error_rows, list):
        print_value("misclassified_record_count", len(error_rows))

    print()
    print("-" * 76)
    print("10. CALIBRATION / THRESHOLD EVIDENCE DISCOVERY")
    print("-" * 76)

    calibration_hits = []

    for report_name, report in reports.items():
        serialized = json.dumps(
            report,
            ensure_ascii=False,
        ).lower()

        terms = [
            "calibration",
            "threshold",
            "probability",
            "confidence",
            "decision boundary",
            "review boundary",
        ]

        found = [
            term for term in terms
            if term in serialized
        ]

        if found:
            calibration_hits.append(
                (report_name, found)
            )

    if calibration_hits:
        for report_name, terms in calibration_hits:
            print(
                f"[FOUND] {report_name}: "
                f"{', '.join(terms)}"
            )
    else:
        print(
            "[NONE] No calibration/threshold/confidence/review "
            "terms found in the inspected JSON evidence."
        )

    print()
    print("-" * 76)
    print("11. PATH RECONCILIATION")
    print("-" * 76)

    actual_model = (
        T1_ROOT / "baselines" / "t1_it_support_char_svm.joblib"
    )

    actual_split = (
        T1_ROOT / "splits" / "t1_split.csv"
    )

    print_value(
        "actual_char_svm_model_exists",
        actual_model.exists(),
    )

    print_value(
        "actual_t1_split_exists",
        actual_split.exists(),
    )

    report_model_path = reports["char_report"].get("model_path")
    report_analysis_path = reports["char_report"].get("analysis_path")

    print_value(
        "char_report.model_path",
        report_model_path,
    )

    print_value(
        "char_report.analysis_path",
        report_analysis_path,
    )

    print()
    print("-" * 76)
    print("12. PRELIMINARY FMP-01 FINDINGS")
    print("-" * 76)

    findings = []

    if (
        three_model.get("status") == "COMPLETE"
        and three_model.get("evaluation_records") == 446
        and three_model.get("evaluation_used_for_fit") is False
    ):
        findings.append(
            "Formal three-model comparison is complete and evaluation "
            "data was not used for fitting."
        )

    if (
        split_report.get("cross_split_groups") == 0
        and split_check.get("cross_split_groups") == []
    ):
        findings.append(
            "No cross-split normalized-text groups were reported."
        )

    if (
        char_analysis.get("evaluation_used_for_fit") is False
        and char_analysis.get("frozen_split_modified") is False
    ):
        findings.append(
            "Word+Character SVM analysis reports no evaluation fitting "
            "and no frozen-split modification."
        )

    if group_eval.get("homogeneous_group_accuracy") is not None:
        findings.append(
            "The homogeneous-group metric requires semantic review "
            "before architecture freeze because its reported value is "
            "not directly interpretable from the current summary alone."
        )

    if calibration_hits:
        findings.append(
            "Calibration/threshold-related terminology exists somewhere "
            "in the inspected evidence and requires targeted inspection."
        )
    else:
        findings.append(
            "No explicit calibration/threshold/review-boundary evidence "
            "was found in the inspected JSON reports."
        )

    if report_model_path:
        expected_suffix = (
            "modeling/T1/baselines/t1_it_support_char_svm.joblib"
        )

        if expected_suffix not in report_model_path:
            findings.append(
                "The stored model path in the report differs from the "
                "current T1 artifact location and requires provenance "
                "reconciliation."
            )

    for index, finding in enumerate(findings, start=1):
        print(f"{index}. {finding}")

    print()
    print("PRELIMINARY STATUS: EVIDENCE_REVIEW_CONTINUES")
    print(
        "No architecture freeze, calibration selection, threshold "
        "selection, or retraining was performed."
    )

    print()
    print("=" * 76)
    print("END OF FMP-01 / T1 EVIDENCE CONSISTENCY AUDIT")
    print("=" * 76)


if __name__ == "__main__":
    main()