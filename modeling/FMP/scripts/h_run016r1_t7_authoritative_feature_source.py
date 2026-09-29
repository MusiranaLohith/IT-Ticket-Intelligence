from pathlib import Path
import ast
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

SOURCE = ROOT / "modeling/T7/scripts/t7_mod010_log_normal_aft_baseline.py"

OUTPUT = ROOT / "modeling/FMP/metrics/h_run016r1_t7_authoritative_feature_source.json"


def main():
    source_text = SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source_text)

    targets = {
        "make_features",
        "text_features",
    }

    found = {}

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in targets:
                found[node.name] = ast.get_source_segment(
                    source_text,
                    node
                )

    print("=" * 72)
    print("H-RUN-016R1 — T7 AUTHORITATIVE FEATURE SOURCE")
    print("=" * 72)

    print("\n[SOURCE]")
    print(SOURCE)

    print("\n[FUNCTIONS FOUND]")

    for name in targets:
        if name in found:
            print(f"{name}: FOUND")
        else:
            print(f"{name}: NOT_FOUND")

    print("\n[RELEVANT SOURCE]")

    for name, code in found.items():
        print(f"\n--- {name} ---")
        print(code)

    result = {
        "operation": "H-RUN-016R1",
        "operation_name":
            "T7_AUTHORITATIVE_FEATURE_SOURCE_EXTRACTION",
        "status": "PASS",
        "source": str(SOURCE),
        "functions_found": list(found.keys()),
        "function_source": found,
        "purpose":
            "Extract the authoritative T7 feature construction "
            "without modifying the frozen model or inventing "
            "a replacement feature formula.",
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8"
    )

    print("\n[OUTPUT]")
    print("written:", OUTPUT)

    print("\n" + "=" * 72)
    print("H-RUN-016R1 COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()