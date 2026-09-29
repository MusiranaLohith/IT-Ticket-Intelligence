from pathlib import Path
import ast
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

SOURCE = (
    ROOT / "modeling/T7/scripts/"
    "t7_mod010_log_normal_aft_baseline.py"
)

OUT_JSON = (
    ROOT / "modeling/FMP/metrics/"
    "fmp06_op018r26_t7_make_features_source_extract.json"
)


def main():
    print("=" * 72)
    print("FMP-06 OP-018R26 — T7 MAKE_FEATURES SOURCE EXTRACT")
    print("=" * 72)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation metrics: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    source_text = SOURCE.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(source_text)
    lines = source_text.splitlines()

    make_features_node = None
    survival_node = None

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name == "make_features":
                make_features_node = node
            elif node.name == "survival":
                survival_node = node

    if make_features_node is None:
        raise RuntimeError(
            "make_features() was not found."
        )

    start = make_features_node.lineno
    end = make_features_node.end_lineno

    make_features_source = "\n".join(
        lines[start - 1:end]
    )

    print("\n[1] Exact make_features() implementation...")
    print(f"  lines: {start}-{end}")

    print("\n" + "-" * 72)
    print(make_features_source)
    print("-" * 72)

    survival_source = None

    if survival_node is not None:
        s_start = survival_node.lineno
        s_end = survival_node.end_lineno

        survival_source = "\n".join(
            lines[s_start - 1:s_end]
        )

        print("\n[2] Exact survival() implementation...")
        print(f"  lines: {s_start}-{s_end}")

        print("\n" + "-" * 72)
        print(survival_source)
        print("-" * 72)

    result = {
        "operation":
            "FMP-06 OP-018R26",

        "status":
            "PASS",

        "read_only":
            True,

        "training_performed":
            False,

        "fitting_performed":
            False,

        "prediction_performed":
            False,

        "evaluation_performed":
            False,

        "locked_test_used":
            False,

        "artifact_modified":
            False,

        "source":
            str(SOURCE),

        "make_features_start_line":
            start,

        "make_features_end_line":
            end,

        "make_features_source":
            make_features_source,

        "survival_source":
            survival_source,

        "purpose":
            (
                "Extract the authoritative T7 MOD-010 feature "
                "construction and survival implementation so the "
                "frozen runtime probe can reproduce the original "
                "model interface without inference from feature "
                "names alone."
            ),
    }

    OUT_JSON.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUT_JSON.open(
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            result,
            f,
            indent=2
        )

    print("\n" + "=" * 72)
    print("OP-018R26 EXTRACT COMPLETE")
    print("=" * 72)

    print(
        f"make_features(): lines {start}-{end}"
    )

    if survival_node is not None:
        print(
            f"survival(): lines "
            f"{survival_node.lineno}-"
            f"{survival_node.end_lineno}"
        )

    print(f"Output: {OUT_JSON}")

    print("\nNo training performed.")
    print("No fitting performed.")
    print("No prediction performed.")
    print("No evaluation performed.")
    print("No locked test used.")
    print("No artifact modification performed.")

    print("=" * 72)


if __name__ == "__main__":
    main()