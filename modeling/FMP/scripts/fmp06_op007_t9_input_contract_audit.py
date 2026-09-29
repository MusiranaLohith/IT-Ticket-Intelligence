from pathlib import Path
import ast
import json


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T9_SCRIPT = (
    PROJECT_ROOT
    / "modeling"
    / "T9"
    / "scripts"
    / "t9_mod037_op014_cross_task_evidence_synthesis.py"
)

T9_CLOSURE = (
    PROJECT_ROOT
    / "modeling"
    / "T9"
    / "mod037"
    / "t9_mod037_op015_final_integrated_closure.json"
)

T8_CLOSURE = (
    PROJECT_ROOT
    / "modeling"
    / "T8"
    / "mod036"
    / "op026"
    / "t8_mod036_op026_decision_engine_validation.json"
)

OUTPUT = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "fmp06_op007_t9_input_contract_audit.json"
)


def extract_strings(path):
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    values = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            values.append(node.value)

    return source, values


def keyword_context(source, keywords, radius=140):
    results = []

    lower = source.lower()

    for keyword in keywords:
        start = 0

        while True:
            idx = lower.find(keyword.lower(), start)

            if idx == -1:
                break

            left = max(0, idx - radius)
            right = min(len(source), idx + len(keyword) + radius)

            results.append({
                "keyword": keyword,
                "context": source[left:right].replace("\n", " "),
            })

            start = idx + len(keyword)

    return results


def load_json(path):
    if not path.exists():
        return {
            "exists": False,
            "path": str(path),
        }

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "exists": True,
        "path": str(path),
        "top_level_type": type(data).__name__,
        "top_level_keys": (
            sorted(data.keys())
            if isinstance(data, dict)
            else []
        ),
    }


def main():
    print("=" * 80)
    print("FMP-06 OP-007")
    print("T9 INPUT / INTERFACE CONTRACT AUDIT")
    print("=" * 80)

    if not T9_SCRIPT.exists():
        raise FileNotFoundError(f"T9 script not found: {T9_SCRIPT}")

    source, strings = extract_strings(T9_SCRIPT)

    path_like = []

    for value in strings:
        lower = value.lower()

        if (
            "/" in value
            or "\\" in value
            or ".json" in lower
            or ".csv" in lower
            or ".joblib" in lower
        ):
            path_like.append(value)

    keywords = [
        "task evidence",
        "T8 task-specific interface",
        "interface",
        "evidence",
        "artifact",
        "input",
        "output",
        "calibration",
        "ranking",
        "survival",
        "probability",
        "confidence",
        "risk",
        "T2",
        "T3",
        "T4",
        "T5",
        "T6",
        "T7",
    ]

    contexts = keyword_context(source, keywords)

    result = {
        "operation": "FMP-06 OP-007",
        "target": str(T9_SCRIPT),
        "source_parse": {
            "syntax_valid": True,
            "string_constant_count": len(strings),
        },
        "t9_source": {
            "path_like_strings": sorted(set(path_like)),
            "keyword_contexts": contexts,
        },
        "known_artifacts": {
            "t8_closure": load_json(T8_CLOSURE),
            "t9_closure": load_json(T9_CLOSURE),
        },
        "safeguards": {
            "execution": False,
            "model_training": False,
            "prediction_generation": False,
            "calibration": False,
            "threshold_selection": False,
            "artifact_modification": False,
            "policy_change": False,
        },
        "status": "PASS",
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    print()
    print("T9 source:")
    print(f"  {T9_SCRIPT}")

    print()
    print("Path-like source references:")
    for item in sorted(set(path_like)):
        print(f"  {item}")

    print()
    print("T8 closure:")
    print(f"  exists: {result['known_artifacts']['t8_closure']['exists']}")

    print()
    print("T9 closure:")
    print(f"  exists: {result['known_artifacts']['t9_closure']['exists']}")

    print()
    print("Keyword/context evidence captured:")
    print(f"  {len(contexts)}")

    print()
    print("Output:")
    print(f"  {OUTPUT}")

    print()
    print("Status: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()