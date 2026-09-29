from pathlib import Path
import csv
import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    log_loss,
    classification_report,
)


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

TRAIN_SOURCE = ROOT / "modeling/T2/splits/train.csv"
VALIDATION_SOURCE = ROOT / "modeling/T2/splits/validation.csv"

OUT_DIR = ROOT / "modeling/T8/mod036/op019"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REPORT = OUT_DIR / "t8_mod036_op019_priority_component_baseline.json"
PREDICTIONS = OUT_DIR / "t8_mod036_op019_priority_predictions.csv"

csv.field_size_limit(10_000_000)


def resolve_column(row, candidates, field_name):
    """
    Resolve a column case-insensitively without assuming
    the exact spelling/capitalization used by the source.
    """

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


def get_id(row):
    column = resolve_column(
        row,
        (
            "id",
            "ticket_id",
            "bug_id",
            "ticket",
        ),
        "ticket ID",
    )

    value = str(row[column]).strip()

    if not value:
        raise RuntimeError(
            "Empty ticket ID encountered."
        )

    return value


def get_text(row):
    summary_column = resolve_column(
        row,
        (
            "summary",
            "short_desc",
            "short_description",
        ),
        "summary",
    )

    description_column = resolve_column(
        row,
        (
            "description",
        ),
        "description",
    )

    summary = str(
        row[summary_column]
    ).strip()

    description = str(
        row[description_column]
    ).strip()

    text = (
        f"summary: {summary} "
        f"description: {description}"
    ).strip()

    if not text:
        raise RuntimeError(
            "Empty ticket text encountered."
        )

    return text


def get_target(row):
    target_column = resolve_column(
        row,
        (
            "target_priority",
            "priority",
            "priority_truth",
            "priority_target",
        ),
        "priority target",
    )

    value = str(
        row[target_column]
    ).strip()

    if not value:
        raise RuntimeError(
            "Empty priority target encountered."
        )

    return value


def prepare(rows):
    prepared = []

    for row in rows:

        prepared.append(
            {
                "id": get_id(row),
                "text": get_text(row),
                "target": get_target(row),
            }
        )

    return prepared


def target_distribution(rows):
    counts = {}

    for row in rows:
        label = row["target"]
        counts[label] = counts.get(label, 0) + 1

    return dict(
        sorted(counts.items())
    )


def main():

    print("=" * 80)
    print("T8 DECISION ENGINE — MOD-036 OP-019")
    print("Priority Decision Component Baseline")
    print("=" * 80)

    # =============================================================
    # 1. Load authoritative T2 development splits
    # =============================================================

    if not TRAIN_SOURCE.exists():
        raise FileNotFoundError(
            TRAIN_SOURCE
        )

    if not VALIDATION_SOURCE.exists():
        raise FileNotFoundError(
            VALIDATION_SOURCE
        )

    train_rows = []

    with TRAIN_SOURCE.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline="",
    ) as f:
        train_rows = list(
            csv.DictReader(f)
        )

    validation_rows = []

    with VALIDATION_SOURCE.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline="",
    ) as f:
        validation_rows = list(
            csv.DictReader(f)
        )

    train = prepare(train_rows)
    validation = prepare(validation_rows)

    print("\nSource populations")
    print("-" * 80)
    print(
        f"  train:      {len(train)}"
    )
    print(
        f"  validation: {len(validation)}"
    )

    # =============================================================
    # 2. ID integrity
    # =============================================================

    train_ids = {
        row["id"]
        for row in train
    }

    validation_ids = {
        row["id"]
        for row in validation
    }

    train_duplicate_count = (
        len(train)
        - len(train_ids)
    )

    validation_duplicate_count = (
        len(validation)
        - len(validation_ids)
    )

    overlap = (
        train_ids
        & validation_ids
    )

    print("\nPopulation integrity")
    print("-" * 80)
    print(
        f"  train duplicate IDs: "
        f"{train_duplicate_count}"
    )
    print(
        f"  validation duplicate IDs: "
        f"{validation_duplicate_count}"
    )
    print(
        f"  train ∩ validation: "
        f"{len(overlap)}"
    )

    if train_duplicate_count != 0:
        raise RuntimeError(
            "Duplicate IDs detected in T2 train."
        )

    if validation_duplicate_count != 0:
        raise RuntimeError(
            "Duplicate IDs detected in T2 validation."
        )

    if overlap:
        raise RuntimeError(
            "Train/validation ticket overlap detected."
        )

    # =============================================================
    # 3. Target distribution
    # =============================================================

    train_distribution = target_distribution(
        train
    )

    validation_distribution = target_distribution(
        validation
    )

    print("\nTarget distribution")
    print("-" * 80)

    print(
        f"  train: {train_distribution}"
    )

    print(
        f"  validation: "
        f"{validation_distribution}"
    )

    # =============================================================
    # 4. Source schema / boundary audit
    # =============================================================

    train_columns = list(
        train_rows[0].keys()
    )

    validation_columns = list(
        validation_rows[0].keys()
    )

    required_columns = {
        "id",
        "summary",
        "description",
        "target_priority",
    }

    train_lower = {
        column.lower()
        for column in train_columns
    }

    validation_lower = {
        column.lower()
        for column in validation_columns
    }

    missing_train = sorted(
        required_columns - train_lower
    )

    missing_validation = sorted(
        required_columns - validation_lower
    )

    if missing_train:
        raise RuntimeError(
            "Required fields missing from T2 train: "
            f"{missing_train}"
        )

    if missing_validation:
        raise RuntimeError(
            "Required fields missing from T2 validation: "
            f"{missing_validation}"
        )

    forbidden_tokens = (
        "resolved",
        "resolution",
        "closed",
        "closure",
        "assigned",
        "assignee",
        "assignment",
        "history",
        "event",
    )

    suspicious_columns = [
        column
        for column in train_columns
        if any(
            token in column.lower()
            for token in forbidden_tokens
        )
    ]

    print("\nBoundary audit")
    print("-" * 80)
    print(
        f"  suspicious post-Creation-like "
        f"columns: {suspicious_columns}"
    )

    if suspicious_columns:
        raise RuntimeError(
            "Potential post-Creation columns detected."
        )

    # =============================================================
    # 5. TF-IDF representation
    # =============================================================

    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.98,
        sublinear_tf=True,
    )

    X_train = vectorizer.fit_transform(
        [
            row["text"]
            for row in train
        ]
    )

    X_validation = vectorizer.transform(
        [
            row["text"]
            for row in validation
        ]
    )

    y_train = [
        row["target"]
        for row in train
    ]

    y_validation = [
        row["target"]
        for row in validation
    ]

    print("\nFeature representation")
    print("-" * 80)
    print(
        f"  train matrix: "
        f"{X_train.shape}"
    )
    print(
        f"  validation matrix: "
        f"{X_validation.shape}"
    )

    # =============================================================
    # 6. T8 priority decision component baseline
    # =============================================================

    model = LogisticRegression(
        max_iter=2000,
        solver="lbfgs",
        class_weight="balanced",
        random_state=42,
    )

    model.fit(
        X_train,
        y_train,
    )

    predictions = model.predict(
        X_validation
    )

    probabilities = model.predict_proba(
        X_validation
    )

    # =============================================================
    # 7. Metrics
    # =============================================================

    accuracy = accuracy_score(
        y_validation,
        predictions,
    )

    macro_f1 = f1_score(
        y_validation,
        predictions,
        average="macro",
    )

    weighted_f1 = f1_score(
        y_validation,
        predictions,
        average="weighted",
    )

    logloss = log_loss(
        y_validation,
        probabilities,
        labels=model.classes_,
    )

    print("\nValidation metrics")
    print("-" * 80)
    print(
        f"  accuracy:    {accuracy:.6f}"
    )
    print(
        f"  macro F1:    {macro_f1:.6f}"
    )
    print(
        f"  weighted F1: {weighted_f1:.6f}"
    )
    print(
        f"  log loss:    {logloss:.6f}"
    )

    print("\nClassification report")
    print("-" * 80)

    print(
        classification_report(
            y_validation,
            predictions,
            zero_division=0,
        )
    )

    # =============================================================
    # 8. Save validation predictions
    # =============================================================

    with PREDICTIONS.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.writer(f)

        header = [
            "id",
            "true_priority",
            "predicted_priority",
        ]

        header.extend(
            f"probability_{label}"
            for label in model.classes_
        )

        writer.writerow(header)

        for row, prediction, probability in zip(
            validation,
            predictions,
            probabilities,
        ):

            output_row = [
                row["id"],
                row["target"],
                prediction,
            ]

            output_row.extend(
                float(value)
                for value in probability
            )

            writer.writerow(output_row)

    # =============================================================
    # 9. Save research artifact
    # =============================================================

    report = {
        "operation": "MOD-036 OP-019",
        "component": "priority",
        "status": "PASS",

        "sources": {
            "train": str(
                TRAIN_SOURCE.relative_to(ROOT)
            ),
            "validation": str(
                VALIDATION_SOURCE.relative_to(ROOT)
            ),
        },

        "population": {
            "train_rows": len(train),
            "validation_rows": len(validation),
            "development_rows": (
                len(train)
                + len(validation)
            ),
            "train_unique_ids": len(train_ids),
            "validation_unique_ids": (
                len(validation_ids)
            ),
            "train_validation_overlap": len(
                overlap
            ),
        },

        "target": {
            "column": "target_priority",
            "classes": list(
                model.classes_
            ),
            "train_distribution": (
                train_distribution
            ),
            "validation_distribution": (
                validation_distribution
            ),
        },

        "boundary": {
            "prediction_boundary": "Creation",
            "features": [
                "summary",
                "description",
            ],
            "post_creation_features_used": False,
        },

        "model": {
            "type": (
                "TFIDF_LOGISTIC_REGRESSION"
            ),
            "class_weight": "balanced",
            "solver": "lbfgs",
            "max_iter": 2000,
            "random_state": 42,
            "ngram_range": [1, 2],
            "min_df": 2,
            "max_df": 0.98,
            "sublinear_tf": True,
        },

        "metrics": {
            "accuracy": float(
                accuracy
            ),
            "macro_f1": float(
                macro_f1
            ),
            "weighted_f1": float(
                weighted_f1
            ),
            "log_loss": float(
                logloss
            ),
        },

        "outputs": {
            "validation_predictions": str(
                PREDICTIONS.relative_to(ROOT)
            ),
        },

        "controls": {
            "locked_test_used": False,
            "post_creation_information_used": False,
            "synthetic_universal_target_created": False,
            "blind_cross_task_probability_averaging": False,
            "arbitrary_cross_task_weighting": False,
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
    print(
        f"  report: {REPORT}"
    )
    print(
        f"  predictions: {PREDICTIONS}"
    )

    print("\nStatus: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()