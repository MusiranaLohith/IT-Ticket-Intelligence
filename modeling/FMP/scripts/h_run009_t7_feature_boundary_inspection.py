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
    / "modeling/FMP/metrics/h_run009_t7_feature_boundary_inspection.json"
)


def source_function(source_text, function_name):
    tree = ast.parse(source_text)

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == function_name:
                return ast.get_source_segment(source_text, node)

    return None


def collect_subscript_fields(function_node):
    fields = []

    for node in ast.walk(function_node):
        if isinstance(node, ast.Subscript):
            value = node.value

            if (
                isinstance(value, ast.Name)
                and value.id == "row"
            ):
                slice_node = node.slice

                if isinstance(slice_node, ast.Constant):
                    if isinstance(slice_node.value, str):
                        fields.append(slice_node.value)

    return sorted(set(fields))


def collect_called_functions(function_node):
    names = []

    for node in ast.walk(function_node):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                names.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                names.append(node.func.attr)

    return sorted(set(names))


def main():
    print("=" * 72)
    print("H-RUN-009 — T7 INFERENCE BOUNDARY INSPECTION")
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
            f"Missing authoritative T7 source: {T7_SOURCE}"
        )

    source_text = T7_SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source_text)

    target_functions = {
        "make_features",
        "text_features",
    }

    inspected = {}

    print("\n[SOURCE]")
    print(f"path: {T7_SOURCE}")

    for node in tree.body:
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name in target_functions
        ):
            fields = collect_subscript_fields(node)
            calls = collect_called_functions(node)

            inspected[node.name] = {
                "source": ast.get_source_segment(
                    source_text,
                    node,
                ),
                "row_fields_accessed": fields,
                "called_functions": calls,
            }

            print(f"\nFUNCTION: {node.name}")

            print("row fields accessed:")
            for field in fields:
                print(f"  - {field}")

            print("called functions:")
            for call in calls:
                print(f"  - {call}")

    make_features_node = None

    for node in tree.body:
        if (
            isinstance(node, ast.FunctionDef)
            and node.name == "make_features"
        ):
            make_features_node = node
            break

    if make_features_node is None:
        raise RuntimeError(
            "Could not locate make_features()"
        )

    make_fields = collect_subscript_fields(
        make_features_node
    )

    outcome_dependent_fields = {
        "duration_seconds",
        "target",
        "target_duration",
        "event",
        "event_observed",
    }

    runtime_required_fields = sorted(
        set(make_fields) - outcome_dependent_fields
    )

    outcome_fields_found = sorted(
        set(make_fields) & outcome_dependent_fields
    )

    print("\n[BOUNDARY CLASSIFICATION]")

    print("runtime-available candidate fields:")
    for field in runtime_required_fields:
        print(f"  - {field}")

    print("\noutcome/target-dependent fields:")
    for field in outcome_fields_found:
        print(f"  - {field}")

    print("\n[DECISION]")

    if outcome_fields_found:
        status = "OUTCOME_DEPENDENCY_PRESENT"
        print(
            "T7 make_features() accesses outcome-dependent "
            "field(s); direct reuse for a new unresolved ticket "
            "is NOT inference-safe."
        )
    else:
        status = "NO_OUTCOME_DEPENDENCY_DETECTED"
        print(
            "No outcome-dependent field was detected in "
            "make_features()."
        )

    output = {
        "operation": "H-RUN-009",
        "operation_name": (
            "T7 Inference Boundary Inspection"
        ),
        "status": "PASS",
        "source": str(T7_SOURCE),
        "functions_inspected": inspected,
        "make_features_row_fields": make_fields,
        "runtime_available_candidate_fields": (
            runtime_required_fields
        ),
        "outcome_dependent_fields": (
            outcome_fields_found
        ),
        "inference_boundary": status,
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
            "Static source inspection only. "
            "This operation does not establish model quality, "
            "prediction accuracy, calibration, or production policy."
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
    print("H-RUN-009 COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()