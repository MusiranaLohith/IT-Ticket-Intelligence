from pathlib import Path
import csv
import hashlib
import json
import sys
import time

import joblib
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
    log_loss,
    brier_score_loss,
)


csv.field_size_limit(sys.maxsize)


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T5_ROOT = PROJECT_ROOT / "modeling" / "T5"

SOURCE = T5_ROOT / "splits" / "t5_model_train.csv"
VALIDATION = T5_ROOT / "splits" / "t5_model_val.csv"

MODEL_DIR = T5_ROOT / "models"
METRIC_DIR = T5_ROOT / "metrics"

CALIBRATION_TRAIN = (
    T5_ROOT / "splits" / "t5_calibration_fit.csv"
)

CALIBRATION_SET = (
    T5_ROOT / "splits" / "t5_calibration_cal.csv"
)

COMPARISON_METRICS = (
    METRIC_DIR
    / "t5_mod007_calibration_comparison.json"
)

CALIBRATION_ARTIFACT = (
    MODEL_DIR
    / "t5_mod007_calibration_models.joblib"
)

VALIDATION_PREDICTIONS = (
    METRIC_DIR
    / "t5_mod007_calibrated_validation_predictions.npz"
)


TEXT_COLUMNS = [
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
]

TARGET_COLUMN = "T5 target"

OUTPUT_COLUMNS = [
    "ID",
    "Creation time",
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
    "T5 target",
]

CALIBRATION_FRACTION = 0.20
RANDOM_SEED = 42


def fail(message):
    print(f"FAIL: {message}")
    sys.exit(1)


def normalized_content_key(row):
    summary = (row["Summary"] or "").strip().lower()
    description = (row["Description"] or "").strip().lower()

    return summary + "\n" + description


def deterministic_group_value(group_key):
    payload = f"{RANDOM_SEED}|{group_key}".encode(
        "utf-8"
    )

    digest = hashlib.sha256(payload).hexdigest()

    return int(digest[:16], 16) / float(16**16)


def combine_text(row):
    parts = []

    for column in TEXT_COLUMNS:
        value = row[column] or ""
        parts.append(
            f"{column}: {value.strip()}"
        )

    return "\n".join(parts)


def load_rows(path):
    rows = []

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames != OUTPUT_COLUMNS:
            fail(
                f"{path.name}: schema mismatch."
            )

        for row in reader:
            target = row[TARGET_COLUMN].strip()

            if target not in {"0", "1"}:
                fail(
                    f"{path.name}: invalid target {target!r}."
                )

            rows.append(row)

    return rows


def target_stats(rows):
    positive = sum(
        row[TARGET_COLUMN].strip() == "1"
        for row in rows
    )

    return {
        "rows": len(rows),
        "positive": positive,
        "negative": len(rows) - positive,
    }


def calculate_metrics(y_true, probabilities):
    predictions = (
        probabilities >= 0.5
    ).astype(np.int8)

    return {
        "average_precision": float(
            average_precision_score(
                y_true,
                probabilities,
            )
        ),
        "pr_auc": float(
            average_precision_score(
                y_true,
                probabilities,
            )
        ),
        "roc_auc": float(
            roc_auc_score(
                y_true,
                probabilities,
            )
        ),
        "log_loss": float(
            log_loss(
                y_true,
                probabilities,
            )
        ),
        "brier_score": float(
            brier_score_loss(
                y_true,
                probabilities,
            )
        ),
        "threshold_0_5_precision": float(
            np.sum(
                (predictions == 1) & (y_true == 1)
            )
            / max(
                np.sum(predictions == 1),
                1,
            )
        ),
        "threshold_0_5_recall": float(
            np.sum(
                (predictions == 1) & (y_true == 1)
            )
            / max(
                np.sum(y_true == 1),
                1,
            )
        ),
        "threshold_0_5_positive_predictions": int(
            predictions.sum()
        ),
    }


def fit_sigmoid_calibrator(
    probabilities,
    y_true,
):
    """
    Platt-style sigmoid calibration.

    The base classifier is NOT retrained.
    Only calibration probabilities are used here.
    """

    epsilon = 1e-7

    clipped = np.clip(
        probabilities,
        epsilon,
        1.0 - epsilon,
    )

    logits = np.log(
        clipped / (1.0 - clipped)
    ).reshape(-1, 1)

    calibrator = LogisticRegression(
        solver="lbfgs",
        max_iter=1000,
        random_state=RANDOM_SEED,
    )

    calibrator.fit(
        logits,
        y_true,
    )

    return calibrator


def apply_sigmoid_calibrator(
    calibrator,
    probabilities,
):
    epsilon = 1e-7

    clipped = np.clip(
        probabilities,
        epsilon,
        1.0 - epsilon,
    )

    logits = np.log(
        clipped / (1.0 - clipped)
    ).reshape(-1, 1)

    return calibrator.predict_proba(
        logits
    )[:, 1]


def main():
    overall_start = time.time()

    print("=" * 80)
    print("T5-MOD-007 — CALIBRATION COMPARISON")
    print("=" * 80)

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    METRIC_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ------------------------------------------------------------------
    # 1. Verify inputs
    # ------------------------------------------------------------------

    print("\n[1] Verify controlled inputs")

    if not SOURCE.exists():
        fail(f"Missing source: {SOURCE}")

    if not VALIDATION.exists():
        fail(f"Missing validation: {VALIDATION}")

    print(f"Training source: {SOURCE}")
    print(f"Validation: {VALIDATION}")
    print("PASS")

    # ------------------------------------------------------------------
    # 2. Load controlled training source
    # ------------------------------------------------------------------

    print("\n[2] Load controlled training source")

    start = time.time()

    source_rows = load_rows(SOURCE)

    elapsed = time.time() - start

    stats = target_stats(source_rows)

    print(f"Rows: {stats['rows']}")
    print(f"Positive: {stats['positive']}")
    print(f"Negative: {stats['negative']}")
    print(f"Load time: {elapsed:.2f} seconds")
    print("PASS")

    # ------------------------------------------------------------------
    # 3. Create group-aware calibration partition
    # ------------------------------------------------------------------

    print("\n[3] Create group-aware calibration partition")

    groups = {}

    for row in source_rows:
        key = normalized_content_key(row)

        if key not in groups:
            groups[key] = []

        groups[key].append(row)

    fit_rows = []
    calibration_rows = []

    for key, rows in groups.items():

        group_value = deterministic_group_value(key)

        if group_value < CALIBRATION_FRACTION:
            calibration_rows.extend(rows)
        else:
            fit_rows.extend(rows)

    fit_groups = {
        normalized_content_key(row)
        for row in fit_rows
    }

    calibration_groups = {
        normalized_content_key(row)
        for row in calibration_rows
    }

    crossing_groups = (
        fit_groups & calibration_groups
    )

    if crossing_groups:
        fail(
            f"{len(crossing_groups)} groups crossed "
            "classifier-fit/calibration partitions."
        )

    fit_stats = target_stats(fit_rows)
    calibration_stats = target_stats(
        calibration_rows
    )

    print(
        f"Total groups: {len(groups)}"
    )

    print(
        f"Classifier-fit groups: "
        f"{len(fit_groups)}"
    )

    print(
        f"Calibration groups: "
        f"{len(calibration_groups)}"
    )

    print(
        f"Classifier-fit rows: "
        f"{fit_stats['rows']}"
    )

    print(
        f"Calibration rows: "
        f"{calibration_stats['rows']}"
    )

    print(
        f"Classifier-fit positives: "
        f"{fit_stats['positive']}"
    )

    print(
        f"Calibration positives: "
        f"{calibration_stats['positive']}"
    )

    print(
        f"Crossing groups: "
        f"{len(crossing_groups)}"
    )

    if fit_stats["positive"] == 0:
        fail(
            "Classifier-fit partition has no positives."
        )

    if calibration_stats["positive"] == 0:
        fail(
            "Calibration partition has no positives."
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 4. Materialize calibration partitions
    # ------------------------------------------------------------------

    print("\n[4] Materialize calibration partitions")

    with CALIBRATION_TRAIN.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=OUTPUT_COLUMNS,
        )

        writer.writeheader()
        writer.writerows(fit_rows)

    with CALIBRATION_SET.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=OUTPUT_COLUMNS,
        )

        writer.writeheader()
        writer.writerows(calibration_rows)

    print(
        f"Classifier-fit artifact: "
        f"{CALIBRATION_TRAIN}"
    )

    print(
        f"Calibration artifact: "
        f"{CALIBRATION_SET}"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 5. Load untouched validation
    # ------------------------------------------------------------------

    print("\n[5] Load untouched validation set")

    validation_rows = load_rows(
        VALIDATION
    )

    validation_stats = target_stats(
        validation_rows
    )

    print(
        f"Validation rows: "
        f"{validation_stats['rows']}"
    )

    print(
        f"Validation positives: "
        f"{validation_stats['positive']}"
    )

    print(
        f"Validation negatives: "
        f"{validation_stats['negative']}"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 6. Prepare text
    # ------------------------------------------------------------------

    print("\n[6] Prepare text representations")

    X_fit_text = [
        combine_text(row)
        for row in fit_rows
    ]

    y_fit = np.asarray(
        [
            int(row[TARGET_COLUMN])
            for row in fit_rows
        ],
        dtype=np.int8,
    )

    X_cal_text = [
        combine_text(row)
        for row in calibration_rows
    ]

    y_cal = np.asarray(
        [
            int(row[TARGET_COLUMN])
            for row in calibration_rows
        ],
        dtype=np.int8,
    )

    X_val_text = [
        combine_text(row)
        for row in validation_rows
    ]

    y_val = np.asarray(
        [
            int(row[TARGET_COLUMN])
            for row in validation_rows
        ],
        dtype=np.int8,
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 7. Fit TF-IDF only on classifier-fit partition
    # ------------------------------------------------------------------

    print("\n[7] Fit TF-IDF")

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_features=100_000,
        sublinear_tf=True,
        lowercase=True,
    )

    start = time.time()

    X_fit = vectorizer.fit_transform(
        X_fit_text
    )

    X_cal = vectorizer.transform(
        X_cal_text
    )

    X_val = vectorizer.transform(
        X_val_text
    )

    elapsed = time.time() - start

    print(
        f"Vocabulary size: "
        f"{len(vectorizer.vocabulary_)}"
    )

    print(
        f"Fit matrix: "
        f"{X_fit.shape[0]} x {X_fit.shape[1]}"
    )

    print(
        f"Calibration matrix: "
        f"{X_cal.shape[0]} x {X_cal.shape[1]}"
    )

    print(
        f"Validation matrix: "
        f"{X_val.shape[0]} x {X_val.shape[1]}"
    )

    print(
        f"TF-IDF time: "
        f"{elapsed:.2f} seconds"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 8. Train base classifier
    # ------------------------------------------------------------------

    print("\n[8] Train classifier")

    base_model = LogisticRegression(
        solver="liblinear",
        class_weight="balanced",
        max_iter=1000,
        random_state=RANDOM_SEED,
    )

    start = time.time()

    base_model.fit(
        X_fit,
        y_fit,
    )

    elapsed = time.time() - start

    print(
        f"Training time: "
        f"{elapsed:.2f} seconds"
    )

    print(
        f"Iterations: "
        f"{base_model.n_iter_}"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 9. Generate calibration-set base probabilities
    # ------------------------------------------------------------------

    print("\n[9] Generate calibration-set probabilities")

    p_cal_base = base_model.predict_proba(
        X_cal
    )[:, 1]

    print(
        f"Probability range: "
        f"{p_cal_base.min():.8f} "
        f"to {p_cal_base.max():.8f}"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 10. Fit sigmoid calibration
    # ------------------------------------------------------------------

    print("\n[10] Fit sigmoid calibration")

    start = time.time()

    sigmoid_calibrator = fit_sigmoid_calibrator(
        p_cal_base,
        y_cal,
    )

    elapsed = time.time() - start

    print(
        f"Sigmoid calibration time: "
        f"{elapsed:.2f} seconds"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 11. Fit isotonic calibration
    # ------------------------------------------------------------------

    print("\n[11] Fit isotonic calibration")

    start = time.time()

    isotonic_calibrator = IsotonicRegression(
        y_min=0.0,
        y_max=1.0,
        out_of_bounds="clip",
    )

    isotonic_calibrator.fit(
        p_cal_base,
        y_cal,
    )

    elapsed = time.time() - start

    print(
        f"Isotonic calibration time: "
        f"{elapsed:.2f} seconds"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 12. Generate untouched validation probabilities
    # ------------------------------------------------------------------

    print("\n[12] Generate validation probabilities")

    p_base = base_model.predict_proba(
        X_val
    )[:, 1]

    p_sigmoid = apply_sigmoid_calibrator(
        sigmoid_calibrator,
        p_base,
    )

    p_isotonic = isotonic_calibrator.predict(
        p_base
    )

    print(
        f"Base range: "
        f"{p_base.min():.8f} "
        f"to {p_base.max():.8f}"
    )

    print(
        f"Sigmoid range: "
        f"{p_sigmoid.min():.8f} "
        f"to {p_sigmoid.max():.8f}"
    )

    print(
        f"Isotonic range: "
        f"{p_isotonic.min():.8f} "
        f"to {p_isotonic.max():.8f}"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 13. Calculate validation comparison
    # ------------------------------------------------------------------

    print("\n[13] Calculate validation comparison")

    base_metrics = calculate_metrics(
        y_val,
        p_base,
    )

    sigmoid_metrics = calculate_metrics(
        y_val,
        p_sigmoid,
    )

    isotonic_metrics = calculate_metrics(
        y_val,
        p_isotonic,
    )

    print("\nBASELINE")

    for name, value in base_metrics.items():
        print(f"{name}: {value}")

    print("\nSIGMOID CALIBRATED")

    for name, value in sigmoid_metrics.items():
        print(f"{name}: {value}")

    print("\nISOTONIC CALIBRATED")

    for name, value in isotonic_metrics.items():
        print(f"{name}: {value}")

    # ------------------------------------------------------------------
    # 14. Save artifacts
    # ------------------------------------------------------------------

    print("\n[14] Save artifacts")

    joblib.dump(
        {
            "base_model": base_model,
            "sigmoid_calibrator": sigmoid_calibrator,
            "isotonic_calibrator": isotonic_calibrator,
        },
        CALIBRATION_ARTIFACT,
    )

    np.savez_compressed(
        VALIDATION_PREDICTIONS,
        y_true=y_val,
        p_base=p_base,
        p_sigmoid=p_sigmoid,
        p_isotonic=p_isotonic,
    )

    comparison = {
        "operation": "T5-MOD-007",
        "operation_name": "Calibration Comparison",
        "calibration_fraction": CALIBRATION_FRACTION,
        "random_seed": RANDOM_SEED,
        "classifier_fit_partition": fit_stats,
        "calibration_partition": calibration_stats,
        "validation_partition": validation_stats,
        "group_controls": {
            "group_definition": (
                "normalized Summary + normalized Description"
            ),
            "total_groups": len(groups),
            "classifier_fit_groups": len(
                fit_groups
            ),
            "calibration_groups": len(
                calibration_groups
            ),
            "crossing_groups": len(
                crossing_groups
            ),
        },
        "calibration_methods": [
            "sigmoid",
            "isotonic",
        ],
        "base_model": base_metrics,
        "sigmoid_calibrated": sigmoid_metrics,
        "isotonic_calibrated": isotonic_metrics,
        "calibration_fit_data": (
            "separate group-aware calibration partition"
        ),
        "validation_used_for_calibrator_fit": False,
        "official_evaluation_used": False,
        "threshold_optimization": False,
        "model_selection": False,
        "status": "CALIBRATION_COMPARISON_COMPLETE",
    }

    with COMPARISON_METRICS.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            comparison,
            file,
            indent=2,
        )

        file.write("\n")

    print(
        f"Calibration models: "
        f"{CALIBRATION_ARTIFACT}"
    )

    print(
        f"Validation predictions: "
        f"{VALIDATION_PREDICTIONS}"
    )

    print(
        f"Comparison metrics: "
        f"{COMPARISON_METRICS}"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # Final
    # ------------------------------------------------------------------

    total_elapsed = (
        time.time() - overall_start
    )

    print("\n" + "=" * 80)
    print(
        "T5-MOD-007 RESULT: "
        "CALIBRATION_COMPARISON_COMPLETE"
    )
    print("=" * 80)

    print(
        f"\nTotal elapsed time: "
        f"{total_elapsed:.2f} seconds"
    )

    print(
        "\nOfficial evaluation set: NOT USED."
    )

    print(
        "Validation set was not used to fit "
        "the calibrators."
    )

    print(
        "No threshold optimization performed."
    )


if __name__ == "__main__":
    main()