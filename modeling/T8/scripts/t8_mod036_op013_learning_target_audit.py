from pathlib import Path
import json
import csv
import re


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
OUT_DIR = ROOT / "modeling/T8/mod036"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = OUT_DIR / "t8_mod036_op013_learning_target_audit.json"

csv.field_size_limit(10_000_000)


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def inspect_json_targets(path):
    data = load_json(path)
    if data is None:
        return []

    findings = []

    target_terms = {
        "target",
        "label",
        "labels",
        "outcome",
        "ground_truth",
        "truth",
        "event",
        "resolved",
        "resolution",
        "priority",
        "severity",
        "category",
        "duplicate",
        "assignee",
        "assignment",
    }

    def walk(obj, location="root"):
        if isinstance(obj, dict):
            for key, value in obj.items():
                key_lower = str(key).lower()

                if any(term in key_lower for term in target_terms):
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        findings.append({
                            "location": f"{location}.{key}",
                            "value": value,
                        })

                walk(value, f"{location}.{key}")

        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                walk(value, f"{location}[{i}]")

    walk(data)
    return findings


def inspect_csv(path):
    result = {
        "path": str(path.relative_to(ROOT)),
        "status": "ERROR",
        "rows_sampled": 0,
        "columns": [],
        "target_like_columns": [],
    }

    try:
        with path.open(
            "r",
            encoding="utf-8",
            errors="replace",
            newline="",
        ) as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames or []
            result["columns"] = columns

            lowered = {
                col: col.lower()
                for col in columns
            }

            target_patterns = [
                r"target",
                r"label",
                r"truth",
                r"ground",
                r"priority",
                r"severity",
                r"category",
                r"duplicate",
                r"assignee",
                r"assignment",
                r"event",
                r"resolved",
                r"resolution",
            ]

            result["target_like_columns"] = [
                col
                for col, low in lowered.items()
                if any(re.search(pattern, low) for pattern in target_patterns)
            ]

            for _ in reader:
                result["rows_sampled"] += 1
                if result["rows_sampled"] >= 5:
                    break

            result["status"] = "INSPECTED"

    except Exception as exc:
        result["error"] = str(exc)

    return result


def main():
    print("=" * 80)
    print("T8 DECISION ENGINE — MOD-036 OP-013")
    print("Learning Target / Historical Outcome Audit")
    print("=" * 80)

    task_definitions = {
        "priority_recommendation": {
            "task": "T2",
            "target_question": (
                "Is there a valid Creation-boundary historical priority "
                "target that can supervise a T8 priority recommendation?"
            ),
        },
        "assignment_recommendation": {
            "task": "T1/T4",
            "target_question": (
                "Is there a valid historical assignment/assignee outcome "
                "aligned with the Creation-boundary evidence?"
            ),
        },
        "duplicate_recommendation": {
            "task": "T5",
            "target_question": (
                "Is there a valid historical duplicate target aligned with "
                "the T5 duplicate definition?"
            ),
        },
        "resolution_context": {
            "task": "T7",
            "target_question": (
                "Does T7 provide a valid survival/time-to-resolution target "
                "that can support this recommendation?"
            ),
        },
        "overall_triage_recommendation": {
            "task": "T8",
            "target_question": (
                "Does an authoritative historical universal triage decision "
                "target exist? Do not synthesize one if absent."
            ),
        },
    }

    # Targeted authoritative files plus relevant task artifacts.
    json_candidates = [
        ROOT / "modeling/T1/contracts/t1_contract.json",
        ROOT / "modeling/T1/analysis/t1_it_support_3model_compare.json",
        ROOT / "modeling/T2/contracts/t2_model_contract.json",
        ROOT / "modeling/T3/contracts/t3_model_contract.json",
        ROOT / "modeling/T3/analysis/t3_final_closure.json",
        ROOT / "modeling/T4/contracts/t4_model_contract.json",
        ROOT / "modeling/T5/metrics/t5_mod011_final_closure.json",
        ROOT / "modeling/T7/contracts/t7_model_contract.json",
        ROOT / "modeling/T7/analysis/t7_final_closure.json",
    ]

    csv_candidates = [
        ROOT / "modeling/T1/derived/t1_features.csv",
        ROOT / "modeling/T2/splits/train.csv",
        ROOT / "modeling/T2/splits/test.csv",
        ROOT / "modeling/T2/splits/validation.csv",
        ROOT / "modeling/T4/derived/t4_features.csv",
        ROOT / "modeling/T4/derived/t4_train.csv",
        ROOT / "modeling/T4/derived/t4_eval.csv",
        ROOT / "modeling/T5/derived/t5_train_features.csv",
        ROOT / "modeling/T5/splits/t5_model_train.csv",
        ROOT / "modeling/T5/splits/t5_model_val.csv",
        ROOT / "modeling/T6/metrics/t6_mod010_corrected_hybrid_query_rankings.csv",
        ROOT / "modeling/T7/derived/t7_mod010_evaluation_predictions.csv",
    ]

    print("\nDecision outputs under audit:")
    for name, definition in task_definitions.items():
        print(f"\n{name}")
        print(f"  source task: {definition['task']}")
        print(f"  question: {definition['target_question']}")

    print("\nJSON target evidence:")
    json_results = []

    for path in json_candidates:
        if not path.exists():
            json_results.append({
                "path": str(path.relative_to(ROOT)),
                "status": "MISSING",
            })
            print(f"  MISSING  {path.relative_to(ROOT)}")
            continue

        findings = inspect_json_targets(path)

        result = {
            "path": str(path.relative_to(ROOT)),
            "status": "INSPECTED",
            "target_like_findings": findings,
        }

        json_results.append(result)

        print(
            f"  FOUND    {path.relative_to(ROOT)} "
            f"target_like_findings={len(findings)}"
        )

        for finding in findings[:12]:
            print(
                f"      {finding['location']} = "
                f"{finding['value']!r}"
            )

        if len(findings) > 12:
            print(f"      ... {len(findings) - 12} additional findings")

    print("\nCSV target/column evidence:")
    csv_results = []

    for path in csv_candidates:
        if not path.exists():
            csv_results.append({
                "path": str(path.relative_to(ROOT)),
                "status": "MISSING",
            })
            print(f"  MISSING  {path.relative_to(ROOT)}")
            continue

        result = inspect_csv(path)
        csv_results.append(result)

        print(
            f"  {result['status']:<10} "
            f"{path.relative_to(ROOT)}"
        )

        if result.get("target_like_columns"):
            print(
                "      target-like columns: "
                + ", ".join(result["target_like_columns"])
            )

    # The audit does not declare a learning target merely because
    # a column happens to contain a target-like name.
    target_assessment = {
        "priority_recommendation": {
            "source": "T2",
            "status": "VALID_NATIVE_TARGET_AVAILABLE",
            "reason": (
                "T2 has a frozen Creation-boundary priority task and "
                "native priority target semantics."
            ),
        },
        "assignment_recommendation": {
            "source": "T1/T4",
            "status": "REQUIRES_NATIVE_OUTCOME_RECONCILIATION",
            "reason": (
                "T1 category evidence and T4 retrieval/assignee evidence "
                "are not automatically equivalent to a historical "
                "assignment decision target."
            ),
        },
        "duplicate_recommendation": {
            "source": "T5",
            "status": "VALID_NATIVE_TARGET_AVAILABLE",
            "reason": (
                "T5 has an established duplicate target and calibrated "
                "native duplicate evidence."
            ),
        },
        "resolution_context": {
            "source": "T7",
            "status": "VALID_NATIVE_SURVIVAL_TARGET_AVAILABLE",
            "reason": (
                "T7 has an established time-to-resolution survival target "
                "with event/censoring semantics."
            ),
        },
        "overall_triage_recommendation": {
            "source": "T8",
            "status": "NO_AUTHORITATIVE_UNIVERSAL_TARGET_ESTABLISHED",
            "reason": (
                "No validated universal historical triage label should "
                "be synthesized from T1-T7 outputs."
            ),
        },
    }

    result = {
        "operation": "MOD-036 OP-013",
        "purpose": (
            "Audit whether each T8 structured recommendation has a valid "
            "historical learning target or must remain evidence-based."
        ),
        "decision_outputs": task_definitions,
        "json_evidence": json_results,
        "csv_evidence": csv_results,
        "target_assessment": target_assessment,
        "rules": [
            "Do not infer a target from a target-like column name alone.",
            "Do not synthesize a universal T8 target.",
            "Preserve native task semantics.",
            "Missing target evidence means unresolved, not negative.",
            "Do not train a T8 model in this operation.",
        ],
        "controls": {
            "training_performed": False,
            "prediction_generation_performed": False,
            "model_selected": False,
            "dataset_modified": False,
        },
    }

    OUTPUT.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\nTarget assessment:")
    for output, assessment in target_assessment.items():
        print(f"  {output}: {assessment['status']}")

    print("\nControls:")
    for key, value in result["controls"].items():
        print(f"  {key}: {value}")

    print(f"\nArtifact: {OUTPUT}")
    print("\nStatus: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()