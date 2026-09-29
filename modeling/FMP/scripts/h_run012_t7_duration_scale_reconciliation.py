from pathlib import Path
import json
import numpy as np
import pandas as pd


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T7_SOURCE = (
    ROOT
    / "modeling/T7/scripts/t7_mod010_log_normal_aft_baseline.py"
)

T7_MODEL = (
    ROOT
    / "modeling/T7/metrics/t7_mod010_log_normal_aft_model.json"
)

T7_TRAIN = (
    ROOT
    / "modeling/T7/splits/t7_train.csv"
)

T7_EVAL = (
    ROOT
    / "modeling/T7/splits/t7_evaluation.csv"
)

H_RUN_011 = (
    ROOT
    / "modeling/FMP/metrics/"
    "h_run011_t7_new_ticket_inference.json"
)

OUTPUT = (
    ROOT
    / "modeling/FMP/metrics/"
    "h_run012_t7_duration_scale_reconciliation.json"
)


def describe_duration(series, label):
    values = pd.to_numeric(
        series,
        errors="coerce",
    ).dropna()

    if values.empty:
        return {
            "label": label,
            "count": 0,
        }

    quantiles = values.quantile(
        [0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]
    )

    return {
        "label": label,
        "count": int(values.size),
        "min": float(values.min()),
        "max": float(values.max()),
        "mean": float(values.mean()),
        "median": float(values.median()),
        "q01": float(quantiles.loc[0.01]),
        "q05": float(quantiles.loc[0.05]),
        "q25": float(quantiles.loc[0.25]),
        "q50": float(quantiles.loc[0.50]),
        "q75": float(quantiles.loc[0.75]),
        "q95": float(quantiles.loc[0.95]),
        "q99": float(quantiles.loc[0.99]),
    }


def seconds_to_human(seconds):
    seconds = float(seconds)

    return {
        "seconds": seconds,
        "minutes": seconds / 60.0,
        "hours": seconds / 3600.0,
        "days": seconds / 86400.0,
    }


def main():
    print("=" * 72)
    print("H-RUN-012 — T7 DURATION SCALE RECONCILIATION")
    print("=" * 72)

    print("\n[CONTROL]")
    print("training/retraining: NO")
    print("model modification: NO")
    print("prediction: NO")
    print("locked-test use: NO")
    print("target modification: NO")

    required = [
        T7_SOURCE,
        T7_MODEL,
        T7_TRAIN,
        T7_EVAL,
        H_RUN_011,
    ]

    for path in required:
        if not path.exists():
            raise FileNotFoundError(
                f"Missing required file: {path}"
            )

    print("\n[LOAD]")

    model_spec = json.loads(
        T7_MODEL.read_text(
            encoding="utf-8"
        )
    )

    runtime_result = json.loads(
        H_RUN_011.read_text(
            encoding="utf-8"
        )
    )

    train_df = pd.read_csv(
        T7_TRAIN
    )

    eval_df = pd.read_csv(
        T7_EVAL
    )

    print(
        f"train rows: {len(train_df)}"
    )

    print(
        f"evaluation rows: {len(eval_df)}"
    )

    print(
        f"model type: "
        f"{model_spec.get('model_type')}"
    )

    print(
        f"sigma: "
        f"{model_spec.get('sigma')}"
    )

    print("\n[TRAIN TARGET COLUMNS]")
    for column in train_df.columns:
        print(f"  - {column}")

    print("\n[EVALUATION TARGET COLUMNS]")
    for column in eval_df.columns:
        print(f"  - {column}")

    if "duration_seconds" not in train_df.columns:
        raise RuntimeError(
            "Training population does not contain "
            "duration_seconds."
        )

    if "duration_seconds" not in eval_df.columns:
        raise RuntimeError(
            "Evaluation population does not contain "
            "duration_seconds."
        )

    print("\n[DURATION SCALE — TRAIN]")
    train_stats = describe_duration(
        train_df["duration_seconds"],
        "T7 train duration_seconds",
    )

    for key, value in train_stats.items():
        print(f"{key}: {value}")

    print("\n[DURATION SCALE — EVALUATION]")
    eval_stats = describe_duration(
        eval_df["duration_seconds"],
        "T7 evaluation duration_seconds",
    )

    for key, value in eval_stats.items():
        print(f"{key}: {value}")

    runtime_prediction = float(
        runtime_result["inference"][
            "predicted_median_duration_seconds"
        ]
    )

    print("\n[RUNTIME PREDICTION]")
    print(
        f"predicted median duration seconds: "
        f"{runtime_prediction}"
    )

    human = seconds_to_human(
        runtime_prediction
    )

    print(
        f"minutes: {human['minutes']}"
    )

    print(
        f"hours: {human['hours']}"
    )

    print(
        f"days: {human['days']}"
    )

    print("\n[RELATIVE POSITION]")

    train_median = train_stats["median"]
    eval_median = eval_stats["median"]

    train_ratio = (
        runtime_prediction / train_median
        if train_median != 0
        else None
    )

    eval_ratio = (
        runtime_prediction / eval_median
        if eval_median != 0
        else None
    )

    print(
        f"vs train median: "
        f"{train_ratio}"
    )

    print(
        f"vs evaluation median: "
        f"{eval_ratio}"
    )

    print("\n[TARGET SEMANTICS IN SOURCE]")

    source_text = T7_SOURCE.read_text(
        encoding="utf-8"
    )

    relevant_lines = []

    for line_number, line in enumerate(
        source_text.splitlines(),
        start=1,
    ):
        lower = line.lower()

        if (
            "duration_seconds" in lower
            or "resolution" in lower
            or "time to" in lower
            or "target" in lower
            or "resolved" in lower
        ):
            relevant_lines.append(
                {
                    "line": line_number,
                    "text": line.rstrip(),
                }
            )

    for item in relevant_lines[:120]:
        print(
            f"{item['line']}: "
            f"{item['text']}"
        )

    output = {
        "operation": "H-RUN-012",
        "operation_name": (
            "T7 Duration Scale Reconciliation"
        ),
        "status": "PASS",
        "files": {
            "t7_source": str(T7_SOURCE),
            "t7_model": str(T7_MODEL),
            "t7_train": str(T7_TRAIN),
            "t7_evaluation": str(T7_EVAL),
            "h_run_011": str(H_RUN_011),
        },
        "model": {
            "model_type": model_spec.get(
                "model_type"
            ),
            "sigma": model_spec.get("sigma"),
        },
        "training_duration_statistics": train_stats,
        "evaluation_duration_statistics": eval_stats,
        "runtime_prediction": {
            "seconds": runtime_prediction,
            **human,
        },
        "relative_position": {
            "ratio_to_train_median": train_ratio,
            "ratio_to_evaluation_median": eval_ratio,
        },
        "source_duration_semantics": relevant_lines[
            :120
        ],
        "controls": {
            "training": False,
            "retraining": False,
            "prediction": False,
            "model_modification": False,
            "locked_test_use": False,
            "target_modification": False,
        },
        "interpretation_boundary": (
            "This operation reconciles the frozen T7 "
            "runtime prediction against the native "
            "duration scale present in the T7 development "
            "and evaluation populations. It does not "
            "modify the model or establish an operational "
            "SLA, threshold, or workflow policy."
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
    print("H-RUN-012 COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()