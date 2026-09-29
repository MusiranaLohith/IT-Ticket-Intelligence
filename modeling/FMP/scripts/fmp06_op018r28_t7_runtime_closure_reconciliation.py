from pathlib import Path
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

CLOSURE = (
    ROOT / "modeling/T7/metrics/"
    "t7_mod012_final_closure.json"
)

COMPARISON = (
    ROOT / "modeling/T7/metrics/"
    "t7_mod011_final_model_comparison_audit.json"
)

MODEL = (
    ROOT / "modeling/T7/metrics/"
    "t7_mod010_log_normal_aft_model.json"
)

RUNTIME = (
    ROOT / "modeling/FMP/metrics/"
    "fmp06_op018r27_t7_exact_frozen_runtime_probe.json"
)

OUT = (
    ROOT / "modeling/FMP/metrics/"
    "fmp06_op018r28_t7_runtime_closure_reconciliation.json"
)


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("=" * 72)
    print("FMP-06 OP-018R28 — T7 RUNTIME-TO-CLOSURE RECONCILIATION")
    print("=" * 72)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation metrics: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    print("\n[1] Loading authoritative T7 evidence...")

    closure = load_json(CLOSURE)
    comparison = load_json(COMPARISON)
    model = load_json(MODEL)
    runtime = load_json(RUNTIME)

    print(f"  closure status: {closure.get('status')}")
    print(f"  comparison status: {comparison.get('status')}")
    print(f"  model type: {model.get('model_type')}")
    print(f"  runtime status: {runtime.get('status')}")

    # ------------------------------------------------------------
    # Closure/model identity
    # ------------------------------------------------------------
    print("\n[2] Checking model identity...")

    closure_models = closure.get(
        "predictive_models",
        {}
    )

    closure_lognormal = closure_models.get(
        "lognormal_aft",
        {}
    )

    model_type_match = (
        str(model.get("model_type", "")).lower()
        == "lognormal_aft"
    )

    runtime_model_match = (
        str(runtime.get("model_type", "")).lower()
        == "lognormal_aft"
    )

    print(
        f"  closure Log-Normal evidence: "
        f"{bool(closure_lognormal)}"
    )

    print(
        f"  frozen model identity: "
        f"{model_type_match}"
    )

    print(
        f"  runtime model identity: "
        f"{runtime_model_match}"
    )

    # ------------------------------------------------------------
    # Parameter contract
    # ------------------------------------------------------------
    print("\n[3] Checking frozen parameter contract...")

    feature_count = len(
        model.get("feature_names", [])
    )

    beta_count = len(
        model.get("beta", {})
    )

    parameter_contract = (
        feature_count == 21
        and beta_count == 21
        and "sigma" in model
    )

    print(f"  feature count: {feature_count}")
    print(f"  beta count: {beta_count}")
    print(f"  sigma present: {'sigma' in model}")
    print(
        f"  parameter contract: "
        f"{parameter_contract}"
    )

    # ------------------------------------------------------------
    # Runtime evidence
    # ------------------------------------------------------------
    print("\n[4] Checking R27 runtime evidence...")

    runtime_pass = (
        runtime.get("status") == "PASS"
        and runtime.get("prediction_performed") is True
        and runtime.get("training_performed") is False
        and runtime.get("fitting_performed") is False
        and runtime.get("locked_test_used") is False
        and runtime.get("artifact_modified") is False
    )

    finite_predictions = all(
        isinstance(x, (int, float))
        and x != float("inf")
        and x != float("-inf")
        for x in runtime.get(
            "predicted_median_duration",
            []
        )
    )

    print(f"  runtime execution contract: {runtime_pass}")
    print(f"  finite predictions: {finite_predictions}")
    print(
        f"  probe rows: "
        f"{len(runtime.get('probe_ids', []))}"
    )

    # ------------------------------------------------------------
    # Population/semantic boundary
    # ------------------------------------------------------------
    print("\n[5] Checking T7 semantic boundary...")

    task_definition = closure.get(
        "task_definition",
        {}
    )

    prediction_boundary = (
        task_definition.get(
            "prediction_boundary"
        )
    )

    event_definition = (
        task_definition.get(
            "event_definition"
        )
    )

    censoring_definition = (
        task_definition.get(
            "censoring_definition"
        )
    )

    print(
        f"  prediction boundary: "
        f"{prediction_boundary}"
    )

    print(
        f"  event definition present: "
        f"{bool(event_definition)}"
    )

    print(
        f"  censoring definition present: "
        f"{bool(censoring_definition)}"
    )

    # ------------------------------------------------------------
    # Final reconciliation
    # ------------------------------------------------------------
    reconciliation_pass = all([
        closure.get("status") == "COMPLETE",
        model_type_match,
        runtime_model_match,
        parameter_contract,
        runtime_pass,
        finite_predictions,
        bool(prediction_boundary),
        bool(event_definition),
        bool(censoring_definition),
    ])

    print("\n[6] Final reconciliation...")

    print(
        f"  T7 runtime-to-closure reconciliation: "
        f"{'PASS' if reconciliation_pass else 'FAIL'}"
    )

    result = {
        "operation":
            "FMP-06 OP-018R28",

        "status":
            "PASS" if reconciliation_pass else "FAIL",

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

        "closure_status":
            closure.get("status"),

        "model_type":
            model.get("model_type"),

        "feature_count":
            feature_count,

        "beta_count":
            beta_count,

        "parameter_contract":
            parameter_contract,

        "runtime_status":
            runtime.get("status"),

        "runtime_execution_contract":
            runtime_pass,

        "finite_runtime_predictions":
            finite_predictions,

        "runtime_probe_rows":
            len(runtime.get("probe_ids", [])),

        "prediction_boundary":
            prediction_boundary,

        "event_definition_present":
            bool(event_definition),

        "censoring_definition_present":
            bool(censoring_definition),

        "reconciliation":
            (
                "PASS — frozen T7 runtime evidence is "
                "consistent with the closed Log-Normal AFT "
                "model contract and native survival semantics."
                if reconciliation_pass
                else
                "FAIL — runtime and closure evidence require "
                "further reconciliation."
            ),
    }

    OUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUT.open(
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            result,
            f,
            indent=2
        )

    print("\n" + "=" * 72)
    print("OP-018R28 RECONCILIATION COMPLETE")
    print("=" * 72)

    print(f"Status: {result['status']}")
    print(
        f"Runtime-to-closure: "
        f"{'PASS' if reconciliation_pass else 'FAIL'}"
    )
    print(f"Output: {OUT}")

    print("\nNo training performed.")
    print("No fitting performed.")
    print("No prediction performed.")
    print("No evaluation performed.")
    print("No locked test used.")
    print("No artifact modification performed.")

    print("=" * 72)


if __name__ == "__main__":
    main()