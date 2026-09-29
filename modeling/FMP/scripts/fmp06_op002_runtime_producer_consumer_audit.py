from pathlib import Path
import json
import ast
from datetime import datetime, timezone


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

OUTPUT_PATH = (
    PROJECT_ROOT
    / "modeling/FMP/metrics/fmp06_op002_runtime_producer_consumer_audit.json"
)


TARGETS = {
    "T8_validation": (
        PROJECT_ROOT
        / "modeling/T8/mod036/op026/"
        "t8_mod036_op026_decision_engine_validation.json"
    ),
    "T9_closure": (
        PROJECT_ROOT
        / "modeling/T9/mod037/"
        "t9_mod037_op015_final_integrated_closure.json"
    ),
    "T10_consolidation": (
        PROJECT_ROOT
        / "modeling/project_consolidation.py"
    ),
}


RUNTIME_ROOTS = {
    "T8": PROJECT_ROOT / "modeling/T8",
    "T9": PROJECT_ROOT / "modeling/T9",
    "T10_project_root": PROJECT_ROOT,
}


KEYWORDS = [
    "input",
    "output",
    "artifact",
    "layer",
    "evidence",
    "producer",
    "consumer",
    "runtime",
    "execute",
    "execution",
    "prediction",
    "decision",
    "policy",
    "interface",
]


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def recursive_strings(obj, prefix=""):
    found = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            current = f"{prefix}.{key}" if prefix else key
            found.extend(recursive_strings(value, current))

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            current = f"{prefix}[{index}]"
            found.extend(recursive_strings(value, current))

    elif isinstance(obj, str):
        found.append(
            {
                "path": prefix,
                "value": obj,
            }
        )

    return found


def inspect_python(path):
    result = {
        "path": str(path),
        "exists": path.exists(),
        "readable": False,
        "syntax_valid": False,
        "function_names": [],
        "class_names": [],
        "imports": [],
        "keyword_hits": [],
        "error": None,
    }

    if not path.exists():
        return result

    try:
        source = path.read_text(encoding="utf-8")
        result["readable"] = True

        tree = ast.parse(source)

        result["syntax_valid"] = True

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                result["function_names"].append(node.name)

            elif isinstance(node, ast.AsyncFunctionDef):
                result["function_names"].append(node.name)

            elif isinstance(node, ast.ClassDef):
                result["class_names"].append(node.name)

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                result["imports"].append(module)

        lowered = source.lower()

        for keyword in KEYWORDS:
            if keyword in lowered:
                result["keyword_hits"].append(keyword)

    except Exception as exc:
        result["error"] = str(exc)

    return result


def inspect_json(path):
    result = {
        "path": str(path),
        "exists": path.exists(),
        "readable": False,
        "top_level_keys": [],
        "string_evidence": [],
        "error": None,
    }

    if not path.exists():
        return result

    try:
        data = load_json(path)
        result["readable"] = True

        if isinstance(data, dict):
            result["top_level_keys"] = list(data.keys())

        strings = recursive_strings(data)

        for item in strings:
            value_lower = item["value"].lower()

            if any(
                keyword in value_lower
                for keyword in KEYWORDS
            ):
                result["string_evidence"].append(item)

    except Exception as exc:
        result["error"] = str(exc)

    return result


def find_python_files(root):
    if not root.exists():
        return []

    return sorted(root.rglob("*.py"))


def main():
    print("=" * 80)
    print("FMP-06 OP-002 — RUNTIME PRODUCER/CONSUMER INTERFACE AUDIT")
    print("=" * 80)

    print("\n[1] Operation contract")
    print("-" * 80)

    print("Operation type: READ_ONLY_RUNTIME_PRODUCER_CONSUMER_AUDIT")
    print("Models loaded: False")
    print("Predictions generated: False")
    print("Retraining: False")
    print("Calibration fitting: False")
    print("Threshold selection: False")
    print("Policy modification: False")
    print("Artifact modification: False")

    print("\n[2] Inspecting authoritative interface artifacts")
    print("-" * 80)

    artifact_results = {}

    for name, path in TARGETS.items():
        print(f"\n{name}")
        print(f"  path: {path}")
        print(f"  exists: {path.exists()}")

        if path.suffix.lower() == ".json":
            result = inspect_json(path)

            print(f"  readable: {result['readable']}")

            if result["top_level_keys"]:
                print(
                    "  top_level_keys:",
                    ", ".join(result["top_level_keys"])
                )

            print(
                f"  keyword_evidence_count: "
                f"{len(result['string_evidence'])}"
            )

        elif path.suffix.lower() == ".py":
            result = inspect_python(path)

            print(f"  readable: {result['readable']}")
            print(f"  syntax_valid: {result['syntax_valid']}")

            print(
                f"  functions: "
                f"{len(result['function_names'])}"
            )

            print(
                f"  classes: "
                f"{len(result['class_names'])}"
            )

            print(
                f"  keyword_hits: "
                f"{', '.join(result['keyword_hits'])}"
            )

        else:
            result = {
                "path": str(path),
                "exists": path.exists(),
                "readable": False,
                "error": "Unsupported artifact type",
            }

        artifact_results[name] = result

    print("\n[3] Inspecting T8 runtime source surface")
    print("-" * 80)

    t8_python = find_python_files(RUNTIME_ROOTS["T8"])

    print(f"T8 Python files found: {len(t8_python)}")

    t8_sources = []

    for path in t8_python:
        result = inspect_python(path)

        t8_sources.append(result)

        print(f"\n{path.relative_to(PROJECT_ROOT)}")
        print(f"  syntax_valid: {result['syntax_valid']}")
        print(
            f"  functions: "
            f"{', '.join(result['function_names'])}"
        )
        print(
            f"  keyword_hits: "
            f"{', '.join(result['keyword_hits'])}"
        )

    print("\n[4] Inspecting T9 runtime source surface")
    print("-" * 80)

    t9_python = find_python_files(RUNTIME_ROOTS["T9"])

    print(f"T9 Python files found: {len(t9_python)}")

    t9_sources = []

    for path in t9_python:
        result = inspect_python(path)

        t9_sources.append(result)

        print(f"\n{path.relative_to(PROJECT_ROOT)}")
        print(f"  syntax_valid: {result['syntax_valid']}")
        print(
            f"  functions: "
            f"{', '.join(result['function_names'])}"
        )
        print(
            f"  keyword_hits: "
            f"{', '.join(result['keyword_hits'])}"
        )

    print("\n[5] Inspecting T10 project consolidation runtime surface")
    print("-" * 80)

    t10_result = artifact_results["T10_consolidation"]

    print(
        "T10 functions:",
        ", ".join(t10_result.get("function_names", []))
    )

    print(
        "T10 imports:",
        ", ".join(t10_result.get("imports", []))
    )

    print(
        "T10 keyword hits:",
        ", ".join(t10_result.get("keyword_hits", []))
    )

    print("\n[6] Producer / consumer determination")
    print("-" * 80)

    interfaces = {
        "T1_to_T7": {
            "producer_consumer_runtime": (
                "NOT_ESTABLISHED_BY_THIS_AUDIT"
            ),
            "reason": (
                "T1-T7 contain frozen task artifacts, but this operation "
                "does not assume that sequential task predictions form a "
                "runtime execution chain."
            ),
        },

        "T7_to_T8": {
            "producer_consumer_runtime": (
                "INTERFACE_ARTIFACT_PRESENT"
            ),
            "reason": (
                "T8 validation artifact explicitly records evidence-engine "
                "inputs, native evidence semantics, and evidence-layer "
                "architecture."
            ),
        },

        "T8_to_T9": {
            "producer_consumer_runtime": (
                "INTEGRATION_ARTIFACT_PRESENT"
            ),
            "reason": (
                "T9 closure records integrated task evidence and semantic "
                "lock validation, but this audit does not execute T8 into T9."
            ),
        },

        "T9_to_T10": {
            "producer_consumer_runtime": (
                "POLICY_ARCHITECTURE_PRESENT"
            ),
            "reason": (
                "T10 project consolidation contains policy architecture "
                "and decision-support boundaries, but empirical policy "
                "execution is not performed here."
            ),
        },
    }

    for interface, result in interfaces.items():
        print(interface)
        print(
            f"  producer_consumer_runtime = "
            f"{result['producer_consumer_runtime']}"
        )
        print(f"  reason = {result['reason']}")

    print("\n[7] Critical distinction")
    print("-" * 80)

    print(
        "This audit distinguishes interface evidence from executed runtime."
    )

    print(
        "A readable closure/interface artifact is not treated as proof "
        "that the corresponding runtime producer actually invoked the "
        "consumer."
    )

    print(
        "No model inference or end-to-end execution is performed by OP-002."
    )

    print("\n[8] Read-only safeguards")
    print("-" * 80)

    safeguards = {
        "models_loaded": False,
        "predictions_generated": False,
        "retraining_performed": False,
        "calibration_fitted": False,
        "threshold_selected": False,
        "threshold_optimized": False,
        "policy_modified": False,
        "artifacts_modified": False,
    }

    for key, value in safeguards.items():
        print(f"{key}: {value}")

    print("\n[9] Final determination")
    print("-" * 80)

    all_authoritative_present = all(
        result.get("exists") and result.get("readable")
        for result in artifact_results.values()
    )

    if not all_authoritative_present:
        status = "BLOCKED"
    else:
        status = "PASS"

    print(f"authoritative_artifacts_complete: {all_authoritative_present}")
    print(f"STATUS: {status}")

    output = {
        "operation": "FMP-06-OP-002",
        "operation_name": (
            "Runtime Producer Consumer Interface Audit"
        ),
        "operation_type": (
            "READ_ONLY_RUNTIME_PRODUCER_CONSUMER_AUDIT"
        ),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "authoritative_artifacts": artifact_results,
        "t8_runtime_sources": t8_sources,
        "t9_runtime_sources": t9_sources,
        "interfaces": interfaces,
        "e2e_runtime_execution": (
            "NOT_ESTABLISHED_BY_THIS_OPERATION"
        ),
        "safeguards": safeguards,
        "status": status,
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(
            output,
            f,
            indent=2
        )

    print("\n[10] Output")
    print("-" * 80)
    print(f"Saved: {OUTPUT_PATH}")

    print("\n" + "=" * 80)
    print("FMP-06 OP-002 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()