from pathlib import Path
import json


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "fmp05_op005_empirical_policy_support_assessment.json"
)


AUTHORITATIVE_ARTIFACTS = {
    "T2": (
        PROJECT_ROOT
        / "modeling/T2/analysis/t2_final_closure.json"
    ),
    "T3": (
        PROJECT_ROOT
        / "modeling/T3/analysis/t3_final_closure.json"
    ),
    "T4": (
        PROJECT_ROOT
        / "modeling/T4/results/t4_mod013_closure.json"
    ),
    "T5": (
        PROJECT_ROOT
        / "modeling/T5/metrics/t5_mod011_final_closure.json"
    ),
    "T6": (
        PROJECT_ROOT
        / "modeling/T6/metrics/t6_final_closure.json"
    ),
    "T7": (
        PROJECT_ROOT
        / "modeling/T7/metrics/t7_mod012_final_closure.json"
    ),
    "T9": (
        PROJECT_ROOT
        / "modeling/T9/mod037/t9_mod037_op015_final_integrated_closure.json"
    ),
}


POLICY_TERMS = [
    "automation",
    "automatic",
    "autonomous",
    "human_review",
    "human review",
    "defer",
    "threshold",
    "operational",
    "decision support",
    "supported_as",
    "not_supported_as",
    "validated",
    "not established",
    "not_established",
    "universal_confidence",
    "universal_risk",
]


def load_json(path):
    with path.open(
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def flatten(obj, prefix=""):
    if isinstance(obj, dict):

        for key, value in obj.items():

            current = (
                f"{prefix}.{key}"
                if prefix
                else str(key)
            )

            yield from flatten(
                value,
                current,
            )

    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            current = f"{prefix}[{index}]"

            yield from flatten(
                value,
                current,
            )

    elif isinstance(
        obj,
        (str, int, float, bool),
    ):

        yield prefix, obj


def find_policy_evidence(data):

    results = []

    for path, value in flatten(data):

        text = str(value)

        lowered = text.lower()

        matched_terms = []

        for term in POLICY_TERMS:

            if term.lower() in lowered:
                matched_terms.append(term)

        if matched_terms:

            results.append(
                {
                    "json_path": path,
                    "value": value,
                    "matched_terms": matched_terms,
                }
            )

    return results


def main():

    print("=" * 80)
    print(
        "FMP-05 OP-005 — EMPIRICAL POLICY SUPPORT ASSESSMENT"
    )
    print("=" * 80)

    print()
    print("[1] Loading authoritative closure artifacts")
    print("-" * 80)

    artifacts = {}
    missing = {}

    for task, path in AUTHORITATIVE_ARTIFACTS.items():

        if not path.exists():

            missing[task] = str(path)

            print(
                f"{task}: MISSING"
            )

            continue

        try:

            data = load_json(path)

            artifacts[task] = data

            print(
                f"{task}: FOUND / READABLE"
            )

        except Exception as exc:

            missing[task] = {
                "path": str(path),
                "error": str(exc),
            }

            print(
                f"{task}: READ ERROR — {exc}"
            )

    if missing:

        raise RuntimeError(
            "One or more authoritative closure artifacts "
            "could not be loaded."
        )

    print()
    print("[2] Extracting task-level policy evidence")
    print("-" * 80)

    evidence = {}

    for task, data in artifacts.items():

        matches = find_policy_evidence(data)

        evidence[task] = matches

        print(
            f"{task}: "
            f"{len(matches)} policy-related evidence records"
        )

    print()
    print("[3] Task-level support boundaries")
    print("-" * 80)

    for task, data in artifacts.items():

        print()
        print(task)

        # Explicitly surface common closure fields.
        if isinstance(data, dict):

            for key in [
                "status",
                "final_status",
                "closure_status",
                "final_project_status",
                "supported_as",
                "not_supported_as",
                "closure_statement",
                "evidence_statement",
            ]:

                if key in data:

                    print(
                        f"  {key}: "
                        f"{data[key]}"
                    )

            if "closure" in data:

                closure = data["closure"]

                if isinstance(
                    closure,
                    dict,
                ):

                    for key in [
                        "status",
                        "automatic_action_policy",
                        "human_review_boundary",
                        "universal_confidence",
                        "universal_risk",
                        "synthetic_fusion_target",
                        "final_interpretation",
                    ]:

                        if key in closure:

                            print(
                                f"  closure.{key}: "
                                f"{closure[key]}"
                            )

    print()
    print("[4] Explicit policy-support assessment")
    print("-" * 80)

    support_matrix = {
        "T2": {
            "native_evidence": (
                "Priority classification/probability evidence"
            ),
            "automation": "NOT ESTABLISHED",
            "human_review": "NOT VALIDATED",
            "defer": "NOT VALIDATED",
            "operational_threshold": "NOT VALIDATED",
        },
        "T3": {
            "native_evidence": (
                "Severity classification/probability evidence"
            ),
            "automation": "NOT ESTABLISHED",
            "human_review": "NOT VALIDATED",
            "defer": "NOT VALIDATED",
            "operational_threshold": "NOT VALIDATED",
        },
        "T4": {
            "native_evidence": (
                "Historical assignee retrieval/ranking"
            ),
            "automation": "NOT ESTABLISHED",
            "human_review": "NOT VALIDATED",
            "defer": "NOT VALIDATED",
            "operational_threshold": "NOT VALIDATED",
        },
        "T5": {
            "native_evidence": (
                "Task-specific calibrated duplicate probability"
            ),
            "automation": "NOT ESTABLISHED",
            "human_review": "NOT VALIDATED",
            "defer": "NOT VALIDATED",
            "operational_threshold": "NOT VALIDATED",
        },
        "T6": {
            "native_evidence": (
                "Similar/duplicate-related ticket ranking"
            ),
            "automation": "NOT ESTABLISHED",
            "human_review": "NOT VALIDATED",
            "defer": "NOT VALIDATED",
            "operational_threshold": "NOT VALIDATED",
        },
        "T7": {
            "native_evidence": (
                "Right-censored survival/resolution-time evidence"
            ),
            "automation": "NOT SUPPORTED",
            "human_review": "NOT VALIDATED",
            "defer": "NOT VALIDATED",
            "operational_threshold": "NOT VALIDATED",
        },
    }

    for task, values in support_matrix.items():

        print()
        print(task)

        for key, value in values.items():

            print(
                f"  {key}: {value}"
            )

    print()
    print("[5] T9 global policy boundary")
    print("-" * 80)

    t9 = artifacts["T9"]

    t9_closure = (
        t9.get("closure", {})
        if isinstance(t9, dict)
        else {}
    )

    t9_boundary = {
        "automatic_action_policy": t9_closure.get(
            "automatic_action_policy"
        ),
        "human_review_boundary": t9_closure.get(
            "human_review_boundary"
        ),
        "universal_confidence": t9_closure.get(
            "universal_confidence"
        ),
        "universal_risk": t9_closure.get(
            "universal_risk"
        ),
        "synthetic_fusion_target": t9_closure.get(
            "synthetic_fusion_target"
        ),
    }

    for key, value in t9_boundary.items():

        print(
            f"{key}: {value}"
        )

    print()
    print("[6] E closure assessment")
    print("-" * 80)

    assessment = (
        "T10 policy boundaries are defined, but the authoritative "
        "T2-T9 evidence does not establish validated universal "
        "automation, universal human-review, universal defer, or "
        "universal operational thresholds. Task-specific native "
        "evidence remains available and must retain its original "
        "semantics. Therefore empirical decision-policy validation "
        "is not closed by the existing evidence alone."
    )

    print(assessment)

    print()
    print("[7] Safeguards")
    print("-" * 80)

    safeguards = {
        "models_loaded": False,
        "predictions_generated": False,
        "retraining_performed": False,
        "calibration_fitted": False,
        "threshold_selected": False,
        "policy_modified": False,
        "artifacts_modified": False,
    }

    for key, value in safeguards.items():

        print(
            f"{key}: {value}"
        )

    print()
    print("[8] Output")
    print("-" * 80)

    result = {
        "operation": "FMP-05-OP-005",
        "operation_type": (
            "READ_ONLY_EMPIRICAL_POLICY_SUPPORT_ASSESSMENT"
        ),
        "status": "PASS",
        "authoritative_artifacts": {
            task: str(path)
            for task, path
            in AUTHORITATIVE_ARTIFACTS.items()
        },
        "policy_evidence": evidence,
        "support_matrix": support_matrix,
        "t9_policy_boundary": t9_boundary,
        "e_closure_assessment": assessment,
        "read_only_safeguards": safeguards,
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"Saved: {OUTPUT_FILE}"
    )

    print()
    print("[9] Final summary")
    print("-" * 80)

    print(
        "Operation type: "
        "READ_ONLY_EMPIRICAL_POLICY_SUPPORT_ASSESSMENT"
    )

    print("STATUS: PASS")

    print("=" * 80)


if __name__ == "__main__":
    main()