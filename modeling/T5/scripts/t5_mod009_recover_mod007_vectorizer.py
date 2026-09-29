from pathlib import Path
import csv
import hashlib
import sys
import time

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer


csv.field_size_limit(sys.maxsize)


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T5_ROOT = PROJECT_ROOT / "modeling" / "T5"

SOURCE = (
    T5_ROOT
    / "splits"
    / "t5_model_train.csv"
)

CALIBRATION_MODEL = (
    T5_ROOT
    / "models"
    / "t5_mod007_calibration_models.joblib"
)

OUTPUT_VECTORIZER = (
    T5_ROOT
    / "models"
    / "t5_mod007_calibrated_tfidf.joblib"
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
    summary = (
        row["Summary"] or ""
    ).strip().lower()

    description = (
        row["Description"] or ""
    ).strip().lower()

    return summary + "\n" + description


def deterministic_group_value(group_key):
    payload = (
        f"{RANDOM_SEED}|{group_key}"
    ).encode("utf-8")

    digest = hashlib.sha256(
        payload
    ).hexdigest()

    return (
        int(digest[:16], 16)
        / float(16**16)
    )


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
            target = row[
                TARGET_COLUMN
            ].strip()

            if target not in {"0", "1"}:
                fail(
                    f"{path.name}: invalid target "
                    f"{target!r}."
                )

            rows.append(row)

    return rows


def main():
    overall_start = time.time()

    print("=" * 80)
    print(
        "T5-MOD-009 — RECOVER MOD-007 TF-IDF VECTORIZER"
    )
    print("=" * 80)

    # ------------------------------------------------------------------
    # 1. Verify required inputs
    # ------------------------------------------------------------------

    print("\n[1] Verify recovery inputs")

    if not SOURCE.exists():
        fail(
            f"Missing controlled source: {SOURCE}"
        )

    if not CALIBRATION_MODEL.exists():
        fail(
            "Missing MOD-007 calibration model artifact."
        )

    print(
        f"Source: {SOURCE}"
    )

    print(
        f"Locked model artifact: "
        f"{CALIBRATION_MODEL}"
    )

    print("PASS")

    # ------------------------------------------------------------------
    # 2. Load existing MOD-007 model
    # ------------------------------------------------------------------

    print("\n[2] Inspect existing MOD-007 base model")

    artifact = joblib.load(
        CALIBRATION_MODEL
    )

    if not isinstance(artifact, dict):
        fail(
            "MOD-007 calibration artifact is not a dictionary."
        )

    if "base_model" not in artifact:
        fail(
            "MOD-007 artifact does not contain base_model."
        )

    base_model = artifact[
        "base_model"
    ]

    expected_features = (
        base_model.n_features_in_
    )

    print(
        f"Existing base model type: "
        f"{type(base_model).__name__}"
    )

    print(
        f"Existing base model feature count: "
        f"{expected_features}"
    )

    if expected_features != 100_000:
        fail(
            "Existing MOD-007 base model does not "
            "have the expected 100,000 features."
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 3. Load controlled training source
    # ------------------------------------------------------------------

    print("\n[3] Load controlled MOD-007 source")

    start = time.time()

    source_rows = load_rows(
        SOURCE
    )

    elapsed = time.time() - start

    print(
        f"Source rows: {len(source_rows)}"
    )

    print(
        f"Load time: {elapsed:.2f} seconds"
    )

    if len(source_rows) != 418_898:
        fail(
            "Controlled source row count does not "
            "match the frozen MOD-007 source."
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 4. Recreate exact group-aware partition
    # ------------------------------------------------------------------

    print(
        "\n[4] Recreate exact MOD-007 classifier-fit partition"
    )

    groups = {}

    for row in source_rows:
        key = normalized_content_key(
            row
        )

        if key not in groups:
            groups[key] = []

        groups[key].append(row)

    fit_rows = []
    calibration_rows = []

    for key, rows in groups.items():

        group_value = (
            deterministic_group_value(key)
        )

        if group_value < CALIBRATION_FRACTION:
            calibration_rows.extend(rows)
        else:
            fit_rows.extend(rows)

    fit_group_keys = {
        normalized_content_key(row)
        for row in fit_rows
    }

    calibration_group_keys = {
        normalized_content_key(row)
        for row in calibration_rows
    }

    crossing_groups = (
        fit_group_keys
        & calibration_group_keys
    )

    if crossing_groups:
        fail(
            f"{len(crossing_groups)} groups crossed "
            "classifier-fit/calibration partitions."
        )

    print(
        f"Total groups: {len(groups)}"
    )

    print(
        f"Classifier-fit groups: "
        f"{len(fit_group_keys)}"
    )

    print(
        f"Calibration groups: "
        f"{len(calibration_group_keys)}"
    )

    print(
        f"Classifier-fit rows: "
        f"{len(fit_rows)}"
    )

    print(
        f"Calibration rows: "
        f"{len(calibration_rows)}"
    )

    print(
        f"Crossing groups: "
        f"{len(crossing_groups)}"
    )

    if len(fit_rows) != 394_483:
        fail(
            "Classifier-fit row count does not match "
            "the frozen MOD-007 partition."
        )

    if len(calibration_rows) != 24_415:
        fail(
            "Calibration row count does not match "
            "the frozen MOD-007 partition."
        )

    if len(fit_group_keys) != 393_467:
        fail(
            "Classifier-fit group count does not match "
            "the frozen MOD-007 partition."
        )

    if len(calibration_group_keys) != 24_352:
        fail(
            "Calibration group count does not match "
            "the frozen MOD-007 partition."
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 5. Recreate exact MOD-007 classifier-fit text
    # ------------------------------------------------------------------

    print(
        "\n[5] Recreate exact classifier-fit text"
    )

    fit_text = [
        combine_text(row)
        for row in fit_rows
    ]

    print(
        f"Documents prepared: "
        f"{len(fit_text)}"
    )

    print(
        "Text columns:"
    )

    for column in TEXT_COLUMNS:
        print(
            f"  - {column}"
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 6. Fit ONLY the missing TF-IDF vectorizer
    # ------------------------------------------------------------------

    print(
        "\n[6] Recover MOD-007 TF-IDF vectorizer"
    )

    print(
        "This step fits preprocessing only."
    )

    print(
        "The LogisticRegression base model will NOT be refit."
    )

    print(
        "No calibrator will be refit."
    )

    print(
        "The official evaluation set will NOT be read."
    )

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_features=100_000,
        sublinear_tf=True,
        lowercase=True,
    )

    start = time.time()

    X_fit = vectorizer.fit_transform(
        fit_text
    )

    elapsed = time.time() - start

    actual_features = (
        len(vectorizer.vocabulary_)
    )

    print(
        f"Recovered vocabulary size: "
        f"{actual_features}"
    )

    print(
        f"Recovered matrix shape: "
        f"{X_fit.shape}"
    )

    print(
        f"TF-IDF recovery time: "
        f"{elapsed:.2f} seconds"
    )

    if actual_features != expected_features:
        fail(
            "Recovered TF-IDF feature count does not "
            "match the existing MOD-007 base model."
        )

    if X_fit.shape[0] != 394_483:
        fail(
            "Recovered TF-IDF row count does not match "
            "the classifier-fit partition."
        )

    if X_fit.shape[1] != 100_000:
        fail(
            "Recovered TF-IDF matrix does not have "
            "100,000 features."
        )

    print("PASS")

    # ------------------------------------------------------------------
    # 7. Save recovered preprocessing artifact
    # ------------------------------------------------------------------

    print(
        "\n[7] Save recovered vectorizer"
    )

    joblib.dump(
        vectorizer,
        OUTPUT_VECTORIZER,
    )

    print(
        f"Saved: {OUTPUT_VECTORIZER}"
    )

    print(
        f"File size: "
        f"{OUTPUT_VECTORIZER.stat().st_size:,} bytes"
    )

    # ------------------------------------------------------------------
    # 8. Reload and verify
    # ------------------------------------------------------------------

    print(
        "\n[8] Reload and verify recovered vectorizer"
    )

    reloaded = joblib.load(
        OUTPUT_VECTORIZER
    )

    reloaded_features = len(
        reloaded.vocabulary_
    )

    print(
        f"Reloaded vectorizer type: "
        f"{type(reloaded).__name__}"
    )

    print(
        f"Reloaded vocabulary size: "
        f"{reloaded_features}"
    )

    if reloaded_features != 100_000:
        fail(
            "Reloaded vectorizer does not have "
            "100,000 features."
        )

    if (
        reloaded.get_params()
        != vectorizer.get_params()
    ):
        fail(
            "Reloaded vectorizer parameters do not "
            "match the recovered vectorizer."
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
        "RESULT: MOD007_TFIDF_RECOVERY_COMPLETE"
    )
    print("=" * 80)

    print(
        f"\nTotal elapsed time: "
        f"{total_elapsed:.2f} seconds"
    )

    print(
        "Base model refit: NO"
    )

    print(
        "Sigmoid calibrator refit: NO"
    )

    print(
        "Isotonic calibrator refit: NO"
    )

    print(
        "Official evaluation read: NO"
    )

    print(
        "Raw archive read: NO"
    )

    print(
        "Recovered feature count: "
        f"{actual_features}"
    )


if __name__ == "__main__":
    main()