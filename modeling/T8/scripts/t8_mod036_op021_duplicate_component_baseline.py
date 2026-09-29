from pathlib import Path
import csv
import json

import numpy as np
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    log_loss,
    brier_score_loss,
)


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

SOURCE = ROOT / "modeling/T5/splits/t5_model_val.csv"

PROBABILITY_SOURCE = (
    ROOT
    / "modeling/T5/metrics/"
    "t5_mod007_calibrated_validation_predictions.npz"
)

OUT_DIR = ROOT / "modeling/T8/mod036/op021"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REPORT = (
    OUT_DIR
    / "t8_mod036_op021_duplicate_component_baseline.json"
)

PREDICTIONS = (
    OUT_DIR
    / "t8_mod036_op021_duplicate_component_predictions.csv"
)

csv.field_size_limit(10_000_000)


def resolve_column(row, candidates, field_name):
    normalized = {
        str(key).strip().lower(): key
        for key in row.keys()
    }

    for candidate in candidates:
        actual = normalized.get(
            candidate.strip().lower()
        )

        if actual is not None:
            return actual

    raise RuntimeError(
        f"Could not resolve {field_name}. "
        f"Available columns: {list(row.keys())}"
    )


def to_binary_target(value):
    value = str(value).strip().lower()

    if value in {
        "1",
        "true",
        "yes",
        "duplicate",
        "dup",
    }:
        return 1

    if value in {
        "0",
        "false",
        "no",
        "not_duplicate",
        "non_duplicate",
        "non-duplicate",
    }:
        return 0

    try:
        numeric = float(value)

        if numeric in (0.0, 1.0):
            return int(numeric)

    except ValueError:
        pass

    raise RuntimeError(
        f"Could not interpret T5 target value: {value!r}"
    )


def main():

    print("=" * 80)
    print("T8 DECISION ENGINE — MOD-036 OP-021")
    print("Duplicate Decision Component Baseline")
    print("=" * 80)

    # =============================================================
    # 1. Load native T5 validation population
    # =============================================================

    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)

    if not PROBABILITY_SOURCE.exists():
        raise FileNotFoundError(
            PROBABILITY_SOURCE
        )

    with SOURCE.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline="",
    ) as f:
        rows = list(
            csv.DictReader(f)
        )

    print("\nNative T5 validation source")
    print("-" * 80)
    print(f"  rows: {len(rows)}")
    print(
        f"  columns: {len(rows[0].keys())}"
    )

    # =============================================================
    # 2. Resolve native T5 target
    # =============================================================

    id_column = resolve_column(
        rows[0],
        (
            "id",
            "ticket_id",
            "bug_id",
            "ticket",
        ),
        "ticket ID",
    )

    target_column = resolve_column(
        rows[0],
        (
            "T5 target",
            "t5_target",
        ),
        "native T5 duplicate target",
    )

    print("\nResolved native fields")
    print("-" * 80)
    print(f"  ID:     {id_column}")
    print(f"  target: {target_column}")

    ids = []
    targets = []

    for row in rows:

        ticket_id = str(
            row[id_column]
        ).strip()

        if not ticket_id:
            raise RuntimeError(
                "Empty ticket ID encountered."
            )

        target = to_binary_target(
            row[target_column]
        )

        ids.append(ticket_id)
        targets.append(target)

    # =============================================================
    # 3. Population integrity
    # =============================================================

    unique_ids = set(ids)

    duplicate_id_count = (
        len(ids)
        - len(unique_ids)
    )

    positive_count = sum(targets)
    negative_count = (
        len(targets)
        - positive_count
    )

    print("\nPopulation integrity")
    print("-" * 80)
    print(f"  rows: {len(ids)}")
    print(f"  unique IDs: {len(unique_ids)}")
    print(
        f"  duplicate IDs: "
        f"{duplicate_id_count}"
    )
    print(
        f"  positive duplicate targets: "
        f"{positive_count}"
    )
    print(
        f"  negative targets: "
        f"{negative_count}"
    )

    if duplicate_id_count:
        raise RuntimeError(
            "Duplicate ticket IDs detected."
        )

    y_true = np.asarray(
        targets,
        dtype=int,
    )

    # =============================================================
    # 4. Load native calibrated T5 probabilities
    # =============================================================

    probability_data = np.load(
        PROBABILITY_SOURCE,
        allow_pickle=False,
    )

    required_keys = {
        "y_true",
        "p_base",
        "p_sigmoid",
        "p_isotonic",
    }

    if not required_keys.issubset(
        set(probability_data.files)
    ):
        raise RuntimeError(
            "T5 calibrated artifact does not contain "
            "the expected probability outputs. "
            f"Found: {list(probability_data.files)}"
        )

    artifact_y_true = np.asarray(
        probability_data["y_true"]
    )

    p_base = np.asarray(
        probability_data["p_base"],
        dtype=float,
    )

    p_sigmoid = np.asarray(
        probability_data["p_sigmoid"],
        dtype=float,
    )

    p_isotonic = np.asarray(
        probability_data["p_isotonic"],
        dtype=float,
    )

    print("\nNative T5 calibrated probability artifact")
    print("-" * 80)
    print(
        f"  path: {PROBABILITY_SOURCE}"
    )
    print(
        f"  keys: {list(probability_data.files)}"
    )
    print(
        f"  rows: {len(p_sigmoid)}"
    )
    print(
        "  selected native probability: p_sigmoid"
    )

    # =============================================================
    # 5. Alignment validation
    # =============================================================

    probability_arrays = {
        "y_true": artifact_y_true,
        "p_base": p_base,
        "p_sigmoid": p_sigmoid,
        "p_isotonic": p_isotonic,
    }

    for name, array in probability_arrays.items():

        if len(array) != len(rows):
            raise RuntimeError(
                f"T5 artifact '{name}' has "
                f"{len(array)} rows but the native "
                f"T5 validation population has "
                f"{len(rows)} rows."
            )

    # The calibrated artifact carries its own y_true.
    # Verify it agrees with the native validation target.
    artifact_y_true = artifact_y_true.astype(int)

    if not np.array_equal(
        artifact_y_true,
        y_true,
    ):
        raise RuntimeError(
            "T5 artifact y_true does not align "
            "with the native T5 validation target."
        )

    if not np.all(
        np.isfinite(p_sigmoid)
    ):
        raise RuntimeError(
            "Non-finite p_sigmoid values detected."
        )

    if np.any(
        (p_sigmoid < 0.0)
        | (p_sigmoid > 1.0)
    ):
        raise RuntimeError(
            "p_sigmoid contains values outside [0,1]."
        )

    print("\nAlignment")
    print("-" * 80)
    print(
        "  target rows:     "
        f"{len(y_true)}"
    )
    print(
        "  p_base rows:     "
        f"{len(p_base)}"
    )
    print(
        "  p_sigmoid rows:  "
        f"{len(p_sigmoid)}"
    )
    print(
        "  p_isotonic rows: "
        f"{len(p_isotonic)}"
    )
    print(
        "  y_true aligned:  True"
    )

    # =============================================================
    # 6. Native calibrated duplicate evidence
    # =============================================================

    roc_auc = roc_auc_score(
        y_true,
        p_sigmoid,
    )

    average_precision = (
        average_precision_score(
            y_true,
            p_sigmoid,
        )
    )

    logloss = log_loss(
        y_true,
        p_sigmoid,
    )

    brier = brier_score_loss(
        y_true,
        p_sigmoid,
    )

    # Descriptive threshold only.
    threshold = 0.5

    threshold_predictions = (
        p_sigmoid >= threshold
    ).astype(int)

    threshold_accuracy = float(
        np.mean(
            threshold_predictions
            == y_true
        )
    )

    print("\nDuplicate evidence metrics")
    print("-" * 80)
    print(
        f"  ROC-AUC:           "
        f"{roc_auc:.6f}"
    )
    print(
        f"  Average Precision: "
        f"{average_precision:.6f}"
    )
    print(
        f"  Log loss:          "
        f"{logloss:.6f}"
    )
    print(
        f"  Brier score:       "
        f"{brier:.6f}"
    )
    print(
        f"  descriptive "
        f"threshold accuracy: "
        f"{threshold_accuracy:.6f}"
    )

    print(
        "\nThreshold 0.5 is descriptive only; "
        "no T8 automation threshold is selected."
    )

    # =============================================================
    # 7. Probability distribution
    # =============================================================

    print("\np_duplicate distribution")
    print("-" * 80)
    print(
        f"  minimum: "
        f"{p_sigmoid.min():.6f}"
    )
    print(
        f"  maximum: "
        f"{p_sigmoid.max():.6f}"
    )
    print(
        f"  mean: "
        f"{p_sigmoid.mean():.6f}"
    )
    print(
        f"  median: "
        f"{np.median(p_sigmoid):.6f}"
    )

    # =============================================================
    # 8. Save T8 duplicate evidence
    # =============================================================

    with PREDICTIONS.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            [
                "id",
                "true_duplicate",
                "p_duplicate",
                "descriptive_threshold_0_5_prediction",
            ]
        )

        for (
            ticket_id,
            target,
            probability,
            prediction,
        ) in zip(
            ids,
            y_true,
            p_sigmoid,
            threshold_predictions,
        ):

            writer.writerow(
                [
                    ticket_id,
                    int(target),
                    float(probability),
                    int(prediction),
                ]
            )

    # =============================================================
    # 9. Save research artifact
    # =============================================================

    report = {
        "operation": "MOD-036 OP-021",
        "component": "duplicate",
        "status": "PASS",

        "source": {
            "native_population": str(
                SOURCE.relative_to(ROOT)
            ),
            "probability_artifact": str(
                PROBABILITY_SOURCE.relative_to(ROOT)
            ),
            "rows": len(rows),
            "unique_ids": len(unique_ids),
        },

        "native_semantics": {
            "task_type": "duplicate_detection",
            "target_column": target_column,
            "native_probability_key": "p_sigmoid",
            "recommendation_type": (
                "duplicate_recommendation"
            ),
        },

        "population": {
            "positive_duplicate_rows": (
                positive_count
            ),
            "negative_rows": (
                negative_count
            ),
        },

        "alignment": {
            "target_rows": len(y_true),
            "probability_rows": len(
                p_sigmoid
            ),
            "artifact_y_true_aligned": True,
        },

        "metrics": {
            "roc_auc": float(roc_auc),
            "average_precision": float(
                average_precision
            ),
            "log_loss": float(logloss),
            "brier_score": float(brier),
        },

        "descriptive_threshold": {
            "threshold": 0.5,
            "accuracy": (
                threshold_accuracy
            ),
            "used_for_automation": False,
        },

        "probability_distribution": {
            "minimum": float(
                p_sigmoid.min()
            ),
            "maximum": float(
                p_sigmoid.max()
            ),
            "mean": float(
                p_sigmoid.mean()
            ),
            "median": float(
                np.median(p_sigmoid)
            ),
        },

        "outputs": {
            "predictions": str(
                PREDICTIONS.relative_to(ROOT)
            ),
        },

        "controls": {
            "post_creation_information_used": False,
            "native_t5_target_preserved": True,
            "native_probability_semantics_preserved": True,
            "probability_reinterpreted_as_universal_score": False,
            "blind_cross_task_probability_averaging": False,
            "arbitrary_cross_task_weighting": False,
            "automation_threshold_selected": False,
        },
    }

    REPORT.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nArtifacts")
    print("-" * 80)
    print(f"  report: {REPORT}")
    print(f"  predictions: {PREDICTIONS}")

    print("\nStatus: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()