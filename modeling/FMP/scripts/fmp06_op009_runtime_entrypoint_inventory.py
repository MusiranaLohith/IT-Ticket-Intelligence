from pathlib import Path
import ast
import json


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
MODELING_ROOT = PROJECT_ROOT / "modeling"

OUTPUT = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "fmp06_op009_runtime_entrypoint_inventory.json"
)


RUNTIME_KEYWORDS = {
    "fastapi": "FastAPI",
    "predict": "predict",
    "predict_proba": "predict_proba",
    "decision_function": "decision_function",
    "joblib.load": "joblib.load",
    "inference": "inference",
    "orchestrator": "orchestrator",
    "pipeline": "pipeline",
    "api": "api",
    "argparse": "argparse",
}


def inspect_python_file(path):
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        function_names = sorted({
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        })

        class_names = sorted({
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
        })

        lower = source.lower()

        keyword_hits = {
            label: lower.count(search_term)
            for search_term, label in RUNTIME_KEYWORDS.items()
        }

        relevant_hits = {
            label: count
            for label, count in keyword_hits.items()
            if count > 0
        }

        return {
            "syntax_valid": True,
            "functions": function_names,
            "classes": class_names,
            "runtime_keyword_hits": relevant_hits,
        }

    except Exception as exc:
        return {
            "syntax_valid": False,
            "error": repr(exc),
        }


def main():
    print("=" * 80)
    print("FMP-06 OP-009")
    print("EXISTING RUNTIME / ORCHESTRATOR INVENTORY")
    print("=" * 80)

    if not MODELING_ROOT.exists():
        raise FileNotFoundError(
            f"Modeling root not found: {MODELING_ROOT}"
        )

    candidates = []

    # Narrow scope: only Python source inside modeling/.
    for path in sorted(MODELING_ROOT.rglob("*.py")):

        # Do not inspect generated virtual environments or caches.
        if any(
            part in {
                ".venv",
                "venv",
                "__pycache__",
                ".git",
            }
            for part in path.parts
        ):
            continue

        info = inspect_python_file(path)

        hits = info.get("runtime_keyword_hits", {})

        if hits:
            relative = str(path.relative_to(PROJECT_ROOT))

            candidates.append({
                "path": relative,
                **info,
            })

    # Rank only for readability; this does NOT establish that a candidate
    # is actually an orchestrator.
    candidates.sort(
        key=lambda item: (
            -len(item.get("runtime_keyword_hits", {})),
            item["path"],
        )
    )

    result = {
        "operation": "FMP-06 OP-009",
        "scope": str(MODELING_ROOT),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "interpretation": {
            "orchestrator_confirmed": False,
            "raw_ticket_pipeline_confirmed": False,
            "automated_operation_engine_confirmed": False,
            "note": (
                "This operation only inventories candidate runtime "
                "entrypoints. A candidate is not considered an "
                "orchestrator until its actual producer/consumer "
                "interface is inspected."
            ),
        },
        "safeguards": {
            "execution_of_project_models": False,
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
    print("Modeling root:")
    print(f"  {MODELING_ROOT}")

    print()
    print("Runtime candidate files:")
    print(f"  {len(candidates)}")

    for item in candidates:
        print()
        print(f"  {item['path']}")
        print(f"    syntax_valid: {item['syntax_valid']}")

        if item.get("runtime_keyword_hits"):
            print("    runtime signals:")
            for key, count in item["runtime_keyword_hits"].items():
                print(f"      {key}: {count}")

        if item.get("functions"):
            print("    functions:")
            for name in item["functions"]:
                print(f"      {name}")

    print()
    print("IMPORTANT:")
    print("  Candidate inventory only.")
    print("  No orchestrator is declared by this operation.")

    print()
    print("Output:")
    print(f"  {OUTPUT}")

    print()
    print("Status: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()