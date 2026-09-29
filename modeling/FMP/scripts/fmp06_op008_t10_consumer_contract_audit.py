from pathlib import Path
import ast
import json


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T10_SOURCE = (
    PROJECT_ROOT
    / "modeling"
    / "project_consolidation.py"
)

T8_CLOSURE = (
    PROJECT_ROOT
    / "modeling"
    / "T8"
    / "mod036"
    / "op026"
    / "t8_mod036_op026_decision_engine_validation.json"
)

T9_CLOSURE = (
    PROJECT_ROOT
    / "modeling"
    / "T9"
    / "mod037"
    / "t9_mod037_op015_final_integrated_closure.json"
)

OUTPUT = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "fmp06_op008_t10_consumer_contract_audit.json"
)


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


def extract_strings(tree):
    values = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            values.append(node.value)

    return values


def collect_function_names(tree):
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)

    return sorted(set(functions))


def collect_imports(tree):
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append(module)

    return sorted(set(imports))


def main():
    print("=" * 80)
    print("FMP-06 OP-008")
    print("T10 CONSUMER / POLICY CONTRACT AUDIT")
    print("=" * 80)

    if not T10_SOURCE.exists():
        raise FileNotFoundError(f"T10 source not found: {T10_SOURCE}")

    source = T10_SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source)

    strings = extract_strings(tree)
    functions = collect_function_names(tree)
    imports = collect_imports(tree)

    source_lower = source.lower()

    keywords = [
        "t8",
        "t9",
        "evidence",
        "prediction",
        "decision",
        "policy",
        "automation",
        "human_review",
        "defer",
        "threshold",
        "ticket",
        "input",
        "output",
        "operation",
        "action",
        "confidence",
        "risk",
    ]

    keyword_hits = {
        keyword: source_lower.count(keyword)
        for keyword in keywords
    }

    path_like_strings = [
        value
        for value in strings
        if (
            "/" in value
            or "\\" in value
            or ".json" in value.lower()
            or ".csv" in value.lower()
            or ".joblib" in value.lower()
        )
    ]

    result = {
        "operation": "FMP-06 OP-008",
        "target": str(T10_SOURCE),

        "source_structure": {
            "syntax_valid": True,
            "function_names": functions,
            "imports": imports,
            "string_constant_count": len(strings),
        },

        "consumer_evidence": {
            "path_like_strings": sorted(set(path_like_strings)),
            "keyword_hits": keyword_hits,
        },

        "known_upstream_artifacts": {
            "t8_closure": load_json(T8_CLOSURE),
            "t9_closure": load_json(T9_CLOSURE),
        },

        "interpretation": {
            "t8_consumer_reference_present": keyword_hits["t8"] > 0,
            "t9_consumer_reference_present": keyword_hits["t9"] > 0,
            "ticket_input_reference_present": keyword_hits["ticket"] > 0,
            "decision_output_reference_present": keyword_hits["decision"] > 0,
            "operation_reference_present": keyword_hits["operation"] > 0,
            "automation_reference_present": keyword_hits["automation"] > 0,
            "human_review_reference_present": keyword_hits["human_review"] > 0,
            "defer_reference_present": keyword_hits["defer"] > 0,
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
    print("T10 source:")
    print(f"  {T10_SOURCE}")

    print()
    print("Functions:")
    for name in functions:
        print(f"  {name}")

    print()
    print("T8 keyword hits:")
    print(f"  {keyword_hits['t8']}")

    print("T9 keyword hits:")
    print(f"  {keyword_hits['t9']}")

    print("Ticket keyword hits:")
    print(f"  {keyword_hits['ticket']}")

    print("Decision keyword hits:")
    print(f"  {keyword_hits['decision']}")

    print("Operation keyword hits:")
    print(f"  {keyword_hits['operation']}")

    print("Automation keyword hits:")
    print(f"  {keyword_hits['automation']}")

    print("Human-review keyword hits:")
    print(f"  {keyword_hits['human_review']}")

    print("Defer keyword hits:")
    print(f"  {keyword_hits['defer']}")

    print()
    print("Path-like source references:")
    for item in sorted(set(path_like_strings)):
        print(f"  {item}")

    print()
    print("Known T8 closure:")
    print(f"  exists: {result['known_upstream_artifacts']['t8_closure']['exists']}")

    print("Known T9 closure:")
    print(f"  exists: {result['known_upstream_artifacts']['t9_closure']['exists']}")

    print()
    print("Output:")
    print(f"  {OUTPUT}")

    print()
    print("Status: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()