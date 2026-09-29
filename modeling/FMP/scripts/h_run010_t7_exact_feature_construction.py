from pathlib import Path
import ast
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T7_SOURCE = (
    ROOT
    / "modeling/T7/scripts/t7_mod010_log_normal_aft_baseline.py"
)

OUTPUT = (
    ROOT
    / "modeling/FMP/metrics/h_run010_t7_exact_feature_construction.json"
)


def get_function(source_text, function_name):
    tree = ast.parse(source_text)

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            if node.name == function_name:
                return node

    return None


def main():
    print("=" * 72)
    print("H-RUN-010 — T7 EXACT FEATURE CONSTRUCTION")
    print("=" * 72)

    print("\n[CONTROL]")
    print("training/retraining: NO")
    print("model execution: NO")
    print("artifact modification: NO")
    print("locked-test use: NO")
    print("synthetic target creation: NO")
    print("threshold selection: NO")

    if not T7_SOURCE.exists():
        raise FileNotFoundError(
            f"Missing T7 source: {T7_SOURCE}"
        )

    source_text = T7_SOURCE.read_text(
        encoding="utf-8"
    )

    node = get_function(
        source_text,
        "make_features",
    )

    if node is None:
        raise RuntimeError(
            "make_features() was not found."
        )

    source = ast.get_source_segment(
        source_text,
        node,
    )

    if source is None:
        raise RuntimeError(
            "Could not extract make_features() source."
        )

    print("\n[AUTHORITATIVE FUNCTION]")
    print("function: make_features")
    print(f"source: {T7_SOURCE}")

    print("\n[EXACT SOURCE]")
    print(source)

    output = {
        "operation": "H-RUN-010",
        "operation_name": (
            "T7 Exact Feature Construction"
        ),
        "status": "PASS",
        "source": str(T7_SOURCE),
        "function": "make_features",
        "make_features_source": source,
        "controls": {
            "training": False,
            "retraining": False,
            "model_execution": False,
            "artifact_modification": False,
            "locked_test_use": False,
            "synthetic_target_creation": False,
            "threshold_selection": False,
        },
        "interpretation_boundary": (
            "Exact source extraction only. "
            "No feature values were generated and no model "
            "prediction was performed."
        ),
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            output,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n[OUTPUT]")
    print(f"written: {OUTPUT}")

    print("\n" + "=" * 72)
    print("H-RUN-010 COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()