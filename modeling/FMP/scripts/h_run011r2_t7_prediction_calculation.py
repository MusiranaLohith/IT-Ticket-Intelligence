from pathlib import Path
import ast
import json


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T7_SOURCE = (
    ROOT
    / "modeling/T7/scripts/t7_mod010_log_normal_aft_baseline.py"
)

OUTPUT = (
    ROOT
    / "modeling/FMP/metrics/"
    "h_run011r2_t7_prediction_calculation.json"
)


TARGET_NAMES = {
    "beta",
    "standardization_mean",
    "standardization_std",
    "linear_predictor",
    "predicted_median_duration",
    "X",
    "X_std",
}


def node_source(source_text, node):
    value = ast.get_source_segment(
        source_text,
        node,
    )

    return value if value is not None else ""


def main():
    print("=" * 72)
    print("H-RUN-011R2 — T7 PREDICTION CALCULATION INSPECTION")
    print("=" * 72)

    print("\n[CONTROL]")
    print("training/retraining: NO")
    print("model execution: NO")
    print("model modification: NO")
    print("locked-test use: NO")
    print("prediction: NO")

    if not T7_SOURCE.exists():
        raise FileNotFoundError(
            f"Missing T7 source: {T7_SOURCE}"
        )

    source_text = T7_SOURCE.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(source_text)

    matches = []

    for node in ast.walk(tree):

        if isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
                ast.AugAssign,
                ast.Return,
                ast.Expr,
            ),
        ):
            source = node_source(
                source_text,
                node,
            )

            if not source:
                continue

            if any(
                name in source
                for name in TARGET_NAMES
            ):
                matches.append(source)

    print("\n[SOURCE]")
    print(f"path: {T7_SOURCE}")

    print("\n[RELEVANT CALCULATION SOURCE]")

    unique_matches = []

    for source in matches:
        if source not in unique_matches:
            unique_matches.append(source)

    for index, source in enumerate(
        unique_matches,
        start=1,
    ):
        print(f"\n--- MATCH {index} ---")
        print(source)

    output = {
        "operation": "H-RUN-011R2",
        "operation_name": (
            "T7 Prediction Calculation Inspection"
        ),
        "status": "PASS",
        "source": str(T7_SOURCE),
        "relevant_source_blocks": unique_matches,
        "controls": {
            "training": False,
            "retraining": False,
            "model_execution": False,
            "model_modification": False,
            "locked_test_use": False,
            "prediction": False,
        },
        "interpretation_boundary": (
            "Static inspection only. "
            "The output identifies the authoritative calculation "
            "used by the T7 implementation; no new-ticket prediction "
            "was executed."
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
    print("H-RUN-011R2 COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()