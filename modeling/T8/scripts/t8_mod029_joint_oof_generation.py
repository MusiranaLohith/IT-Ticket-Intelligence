#!/usr/bin/env python3

"""
T8 MOD-029 — Controlled Joint T2/T7 Chronological OoF Generation

Purpose
-------
Generate chronology-preserving out-of-fold predictions for the joint
T2 + T7 development population.

This module does NOT perform fusion.

Frozen implementations
----------------------
T2:
    T2-MOD-007
    TF-IDF + Class-Weighted Logistic Regression

T7:
    T7-MOD-010
    Log-Normal AFT

Design
------
- Joint development population = T2 train ∩ T7 train
- Five chronological blocks
- B1 = warm-up only
- B2-B5 = OoF prediction blocks
- T2 training uses only earlier common-development rows
- T7 training uses only T7 training rows strictly before the
  prediction boundary
- Prediction rows are never used for fitting
- Frozen source implementations are loaded directly
- No locked final model artifact is loaded
- No fusion is performed
- No synthetic universal T8 target is created
- No synthetic universal T8 score is created

Critical representation rule
-----------------------------
T8 uses:

    _t8_creation_dt

for chronology only.

Frozen T7 receives:

    Creation time

as the original CSV-style string because its frozen
parse_creation() implementation expects string operations such
as .endswith("Z").
"""


from __future__ import annotations


import ast
import hashlib
import json
import time
from pathlib import Path
from types import ModuleType
from typing import Any


import numpy as np
import pandas as pd


# =============================================================================
# PATHS
# =============================================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_SOURCE = (
    PROJECT_ROOT
    / "modeling"
    / "T2"
    / "scripts"
    / "t2_class_weighted.py"
)

T7_SOURCE = (
    PROJECT_ROOT
    / "modeling"
    / "T7"
    / "scripts"
    / "t7_mod010_log_normal_aft_baseline.py"
)

T2_SPLIT_ROOT = (
    PROJECT_ROOT
    / "modeling"
    / "T2"
    / "splits"
)

T7_SPLIT_ROOT = (
    PROJECT_ROOT
    / "modeling"
    / "T7"
    / "splits"
)

T8_ROOT = (
    PROJECT_ROOT
    / "modeling"
    / "T8"
)

T8_T2_OOF = (
    T8_ROOT
    / "t8_mod029_t2_oof.csv"
)

T8_T7_OOF = (
    T8_ROOT
    / "t8_mod029_t7_oof.csv"
)

T8_JOINT_OOF = (
    T8_ROOT
    / "t8_mod029_joint_oof.csv"
)

T8_MANIFEST = (
    T8_ROOT
    / "t8_mod029_generation_manifest.json"
)


# =============================================================================
# CONSTANTS
# =============================================================================

N_BLOCKS = 5

T7_HORIZONS = (
    211_583,
    1_780_179,
    14_608_619,
)


# =============================================================================
# LOGGING
# =============================================================================

def log(
    message: str = "",
) -> None:

    timestamp = time.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    print(
        f"[{timestamp}] {message}",
        flush=True,
    )


# =============================================================================
# FILE HASH
# =============================================================================

def sha256_file(
    path: Path,
) -> str:

    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as handle:

        while True:

            chunk = handle.read(
                1024 * 1024
            )

            if not chunk:
                break

            digest.update(
                chunk
            )

    return digest.hexdigest()


# =============================================================================
# CSV LOADING
# =============================================================================

def load_csv(
    path: Path,
) -> pd.DataFrame:
    """
    Preserve empty CSV fields as empty strings.

    This is required because the frozen T7 implementation expects
    CSV-style string values for text and Creation time.
    """

    if not path.exists():

        raise FileNotFoundError(
            f"Missing required file:\n{path}"
        )

    log(
        "Loading:"
    )

    log(
        f"  {path}"
    )

    df = pd.read_csv(
        path,
        low_memory=False,
        keep_default_na=False,
    )

    log(
        f"  rows={len(df):,} "
        f"cols={len(df.columns):,}"
    )

    return df


# =============================================================================
# CREATION TIME HANDLING
# =============================================================================

def normalize_creation(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Preserve the original Creation time string and create a separate
    UTC-aware datetime column for T8 chronology.
    """

    out = df.copy()

    if "Creation time" not in out.columns:

        raise RuntimeError(
            "Creation time column missing."
        )

    # Preserve original CSV representation.
    out["Creation time"] = (
        out["Creation time"]
        .astype(str)
    )

    # T8-only chronology representation.
    out["_t8_creation_dt"] = pd.to_datetime(
        out["Creation time"],
        errors="raise",
        utc=True,
    )

    return out


def sort_creation(
    df: pd.DataFrame,
) -> pd.DataFrame:

    out = df.copy()

    if "_t8_creation_dt" not in out.columns:

        out["_t8_creation_dt"] = pd.to_datetime(
            out["Creation time"],
            errors="raise",
            utc=True,
        )

    out = out.sort_values(
        [
            "_t8_creation_dt",
            "ID",
        ],
        kind="mergesort",
    ).reset_index(
        drop=True
    )

    return out


# =============================================================================
# OPTIONAL AST HELPER
#
# Kept only for source-inspection capability. T7 itself is NOT loaded
# through selective AST extraction anymore.
# =============================================================================

def extract_function_source(
    source_path: Path,
    function_name: str,
) -> str:

    source = source_path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(source_path),
    )

    for node in tree.body:

        if (
            isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
            and node.name == function_name
        ):

            return ast.get_source_segment(
                source,
                node,
            )

    raise RuntimeError(
        f"Could not recover function "
        f"{function_name!r} from {source_path}"
    )


# =============================================================================
# FROZEN T2 LOADING
# =============================================================================

def recover_t2_namespace() -> ModuleType:
    """
    Recover the exact T2 build_text() implementation.

    T2's required implementation function is isolated because its
    source dependency is limited to text construction for this
    fold-local reproduction.
    """

    log(
        "Extracting frozen T2 definitions:"
    )

    source = T2_SOURCE.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(T2_SOURCE),
    )

    target_node = None

    for node in tree.body:

        if (
            isinstance(
                node,
                ast.FunctionDef,
            )
            and node.name == "build_text"
        ):

            target_node = node
            break

    if target_node is None:

        raise RuntimeError(
            "Could not recover build_text "
            f"from {T2_SOURCE}"
        )

    # Recover imports required by build_text.
    import_nodes = [
        node
        for node in tree.body
        if isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
            ),
        )
    ]

    selected_module = ast.Module(
        body=(
            import_nodes
            + [target_node]
        ),
        type_ignores=[],
    )

    module = ModuleType(
        "_t8_frozen_T2"
    )

    module.__file__ = str(
        T2_SOURCE
    )

    compiled = compile(
        selected_module,
        filename=str(T2_SOURCE),
        mode="exec",
    )

    exec(
        compiled,
        module.__dict__,
    )

    if not hasattr(
        module,
        "build_text",
    ):

        raise RuntimeError(
            "T2 build_text was not recovered."
        )

    log(
        "T2 text-construction function recovered: "
        f"{module.build_text.__name__}"
    )

    return module


# =============================================================================
# FROZEN T7 LOADING
# =============================================================================

def recover_t7_namespace() -> ModuleType:
    """
    Load the COMPLETE frozen T7 implementation as an isolated module.

    The frozen T7 source contains:

        if __name__ == "__main__":

    so importing the file does not execute its experiment/modeling
    workflow.

    This is intentionally used instead of selectively extracting
    functions because make_features() depends on parse_creation()
    and potentially other definitions from the same source file.
    """

    import importlib.util

    log(
        "Loading complete frozen T7 implementation:"
    )

    log(
        f"  {T7_SOURCE}"
    )

    module_name = "_t8_frozen_T7"

    spec = importlib.util.spec_from_file_location(
        module_name,
        T7_SOURCE,
    )

    if spec is None:

        raise RuntimeError(
            "Could not create import specification "
            f"for frozen T7 source:\n{T7_SOURCE}"
        )

    if spec.loader is None:

        raise RuntimeError(
            "Frozen T7 import specification has no loader."
        )

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(
        module
    )

    required_names = [
        "parse_creation",
        "text_features",
        "frequency_maps",
        "make_features",
        "standardize_fit",
        "LogNormalAFT",
    ]

    missing = [
        name
        for name in required_names
        if not hasattr(
            module,
            name,
        )
    ]

    if missing:

        raise RuntimeError(
            "Frozen T7 module loaded, but required "
            f"definitions are missing: {missing}"
        )

    log(
        "T7 frozen implementation loaded successfully:"
    )

    for name in required_names:

        log(
            f"  {name}: "
            f"{getattr(module, name)}"
        )

    return module


# =============================================================================
# SPLIT RESOLUTION
# =============================================================================

def resolve_splits() -> dict[str, Path]:

    paths = {

        "t2_train":
            T2_SPLIT_ROOT
            / "train.csv",

        "t2_validation":
            T2_SPLIT_ROOT
            / "validation.csv",

        "t2_test":
            T2_SPLIT_ROOT
            / "test.csv",

        "t7_train":
            T7_SPLIT_ROOT
            / "t7_train.csv",

        "t7_eval":
            T7_SPLIT_ROOT
            / "t7_evaluation.csv",
    }

    for name, path in paths.items():

        if not path.exists():

            raise FileNotFoundError(
                f"Missing {name} split:\n{path}"
            )

    log(
        "Resolved split artifacts:"
    )

    for name, path in paths.items():

        log(
            f"  {name}: {path}"
        )

    return paths


# =============================================================================
# SCHEMA VALIDATION
# =============================================================================

def require_columns(
    df: pd.DataFrame,
    required: list[str],
    label: str,
) -> None:

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:

        raise RuntimeError(
            f"{label}: missing columns: {missing}"
        )


def validate_input_schemas(
    t2_train: pd.DataFrame,
    t2_validation: pd.DataFrame,
    t2_test: pd.DataFrame,
    t7_train: pd.DataFrame,
    t7_eval: pd.DataFrame,
) -> None:

    t2_required = [
        "ID",
        "Creation time",
        "Summary",
        "Description",
        "target_priority",
    ]

    t7_required = [
        "ID",
        "Creation time",
        "Creator",
        "Creator Detail",
        "Summary",
        "Description",
        "first_resolved_time",
        "duration_seconds",
        "event",
        "endpoint_type",
        "observation_endpoint",
        "source_row_width",
    ]

    require_columns(
        t2_train,
        t2_required,
        "T2 train",
    )

    require_columns(
        t2_validation,
        t2_required,
        "T2 validation",
    )

    require_columns(
        t2_test,
        t2_required,
        "T2 test",
    )

    require_columns(
        t7_train,
        t7_required,
        "T7 train",
    )

    require_columns(
        t7_eval,
        t7_required,
        "T7 evaluation",
    )


# =============================================================================
# ID VALIDATION
# =============================================================================

def validate_unique_ids(
    df: pd.DataFrame,
    label: str,
) -> None:

    if df["ID"].duplicated().any():

        duplicated = (
            df.loc[
                df["ID"].duplicated(
                    keep=False
                ),
                "ID",
            ]
            .astype(str)
            .head(20)
            .tolist()
        )

        raise RuntimeError(
            f"{label}: duplicate IDs detected: "
            f"{duplicated}"
        )


def validate_split_integrity(
    t2_train: pd.DataFrame,
    t2_validation: pd.DataFrame,
    t2_test: pd.DataFrame,
    t7_train: pd.DataFrame,
    t7_eval: pd.DataFrame,
) -> None:

    validate_unique_ids(
        t2_train,
        "T2 train",
    )

    validate_unique_ids(
        t2_validation,
        "T2 validation",
    )

    validate_unique_ids(
        t2_test,
        "T2 test",
    )

    validate_unique_ids(
        t7_train,
        "T7 train",
    )

    validate_unique_ids(
        t7_eval,
        "T7 evaluation",
    )

    t2_train_ids = set(
        t2_train["ID"]
    )

    t2_val_ids = set(
        t2_validation["ID"]
    )

    t2_test_ids = set(
        t2_test["ID"]
    )

    t7_train_ids = set(
        t7_train["ID"]
    )

    t7_eval_ids = set(
        t7_eval["ID"]
    )

    if (
        t2_train_ids
        & t2_val_ids
    ):

        raise RuntimeError(
            "T2 train/validation overlap."
        )

    if (
        t2_train_ids
        & t2_test_ids
    ):

        raise RuntimeError(
            "T2 train/test overlap."
        )

    if (
        t2_val_ids
        & t2_test_ids
    ):

        raise RuntimeError(
            "T2 validation/test overlap."
        )

    if (
        t7_train_ids
        & t7_eval_ids
    ):

        raise RuntimeError(
            "T7 train/evaluation overlap."
        )

    log(
        "Split integrity checks: PASS"
    )


# =============================================================================
# COMMON DEVELOPMENT POPULATION
# =============================================================================

def build_common_population(
    t2_train: pd.DataFrame,
    t7_train: pd.DataFrame,
) -> pd.DataFrame:

    t2_ids = set(
        t2_train["ID"]
    )

    t7_ids = set(
        t7_train["ID"]
    )

    common_ids = (
        t2_ids
        & t7_ids
    )

    if not common_ids:

        raise RuntimeError(
            "Joint development population is empty."
        )

    common = (
        t2_train[
            t2_train["ID"].isin(
                common_ids
            )
        ]
        .copy()
    )

    common = normalize_creation(
        common
    )

    common = sort_creation(
        common
    )

    validate_unique_ids(
        common,
        "Joint common development",
    )

    log(
        "Joint common development population: "
        f"{len(common):,}"
    )

    return common


# =============================================================================
# CHRONOLOGICAL BLOCKS
# =============================================================================

def make_blocks(
    common: pd.DataFrame,
    n_blocks: int = N_BLOCKS,
) -> list[pd.DataFrame]:
    """
    Create exact chronological DataFrame blocks.

    Five blocks for 20,648 rows become:

        B1 = 4,130
        B2 = 4,130
        B3 = 4,130
        B4 = 4,129
        B5 = 4,129

    The first blocks receive the remainder rows.
    """

    if len(common) < n_blocks:

        raise RuntimeError(
            "Not enough rows for requested blocks."
        )

    common = common.reset_index(
        drop=True
    )

    base_size = (
        len(common)
        // n_blocks
    )

    remainder = (
        len(common)
        % n_blocks
    )

    blocks = []

    start = 0

    for block_index in range(
        n_blocks
    ):

        size = (
            base_size + 1
            if block_index < remainder
            else base_size
        )

        end = (
            start
            + size
        )

        block = (
            common.iloc[
                start:end
            ]
            .copy()
            .reset_index(
                drop=True
            )
        )

        blocks.append(
            block
        )

        start = end

    if sum(
        len(block)
        for block in blocks
    ) != len(common):

        raise RuntimeError(
            "Chronological block partition does not "
            "cover the complete common population."
        )

    log(
        f"Number of chronological blocks: "
        f"{len(blocks)}"
    )

    for index, block in enumerate(
        blocks,
        start=1,
    ):

        first_time = block[
            "_t8_creation_dt"
        ].iloc[0]

        last_time = block[
            "_t8_creation_dt"
        ].iloc[-1]

        log(
            f"B{index}: "
            f"rows={len(block):,}; "
            f"start={first_time}; "
            f"end={last_time}"
        )

    return blocks


# =============================================================================
# T2 FOLD
# =============================================================================

def fit_t2_fold(
    train_df: pd.DataFrame,
    pred_df: pd.DataFrame,
    t2_namespace: ModuleType,
) -> pd.DataFrame:

    from sklearn.feature_extraction.text import (
        TfidfVectorizer,
    )

    from sklearn.linear_model import (
        LogisticRegression,
    )

    build_text = (
        t2_namespace.build_text
    )

    if len(train_df) == 0:

        raise RuntimeError(
            "T2 fold training population is empty."
        )

    if len(pred_df) == 0:

        raise RuntimeError(
            "T2 prediction population is empty."
        )

    # Frozen T2 implementation expects DataFrames.
    train_text = build_text(
        train_df
    )

    pred_text = build_text(
        pred_df
    )

    y_train = (
        train_df[
            "target_priority"
        ]
        .astype(str)
    )

    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.98,
        sublinear_tf=True,
    )

    X_train = vectorizer.fit_transform(
        train_text
    )

    X_pred = vectorizer.transform(
        pred_text
    )

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

    predicted = model.predict(
        X_pred
    )

    probabilities = model.predict_proba(
        X_pred
    )

    result = pd.DataFrame(
        {
            "ID":
                pred_df[
                    "ID"
                ].values,

            "predicted_priority":
                predicted,
        }
    )

    class_names = [
        str(cls)
        for cls in model.classes_
    ]

    for class_index, class_name in enumerate(
        class_names
    ):

        result[
            f"predicted_probability_{class_name}"
        ] = probabilities[
            :,
            class_index,
        ]

    return result


# =============================================================================
# T7 FOLD
# =============================================================================

def fit_t7_fold(
    train_rows: list[dict[str, Any]],
    pred_rows: list[dict[str, Any]],
    t7_namespace: ModuleType,
) -> pd.DataFrame:

    make_features = (
        t7_namespace.make_features
    )

    standardize_fit = (
        t7_namespace.standardize_fit
    )

    LogNormalAFT = (
        t7_namespace.LogNormalAFT
    )

    if len(train_rows) == 0:

        raise RuntimeError(
            "T7 fold training population is empty."
        )

    if len(pred_rows) == 0:

        raise RuntimeError(
            "T7 prediction population is empty."
        )

    required_fields = [
        "ID",
        "Creation time",
        "Creator",
        "Creator Detail",
        "Summary",
        "Description",
        "duration_seconds",
        "event",
    ]

    for row_index, row in enumerate(
        train_rows
    ):

        missing = [
            field
            for field in required_fields
            if field not in row
        ]

        if missing:

            raise RuntimeError(
                f"T7 training row {row_index}: "
                f"missing fields {missing}"
            )

        if not isinstance(
            row["Creation time"],
            str,
        ):

            raise RuntimeError(
                f"T7 training row {row_index}: "
                "Creation time is not a string."
            )

    for row_index, row in enumerate(
        pred_rows
    ):

        missing = [
            field
            for field in required_fields
            if field not in row
        ]

        if missing:

            raise RuntimeError(
                f"T7 prediction row {row_index}: "
                f"missing fields {missing}"
            )

        if not isinstance(
            row["Creation time"],
            str,
        ):

            raise RuntimeError(
                f"T7 prediction row {row_index}: "
                "Creation time is not a string."
            )

    # -------------------------------------------------------------------------
    # Frozen T7 preprocessing
    # -------------------------------------------------------------------------

    creator_counts, detail_counts = (
        t7_namespace.frequency_maps(
            train_rows
        )
    )

    (
        X_train_raw,
        train_ids,
        train_durations,
        train_events,
        feature_names,
    ) = make_features(
        train_rows,
        creator_counts,
        detail_counts,
    )

    (
        X_pred_raw,
        pred_ids,
        _,
        _,
        pred_feature_names,
    ) = make_features(
        pred_rows,
        creator_counts,
        detail_counts,
    )

    if feature_names != pred_feature_names:

        raise RuntimeError(
            "T7 feature-name mismatch between "
            "training and prediction populations."
        )

    # -------------------------------------------------------------------------
    # Frozen T7 standardization
    # -------------------------------------------------------------------------

    mean, std = standardize_fit(
        X_train_raw
    )

    X_train = (
        X_train_raw
        - mean
    ) / std

    X_pred = (
        X_pred_raw
        - mean
    ) / std

    # -------------------------------------------------------------------------
    # Frozen T7 Log-Normal AFT
    # -------------------------------------------------------------------------

    model = LogNormalAFT(
        l2=1e-3
    )

    model.fit(
        X_train,
        train_durations,
        train_events,
    )

    predicted_median = (
        model.median(
            X_pred
        )
    )

    survival_outputs = {}

    for horizon in T7_HORIZONS:

        survival_outputs[
            horizon
        ] = model.survival(
            X_pred,
            horizon,
        )

    result = pd.DataFrame(
        {
            "ID":
                pred_ids,

            "predicted_median_survival_seconds":
                predicted_median,

            "survival_probability_at_211583_seconds":
                survival_outputs[
                    211_583
                ],

            "survival_probability_at_1780179_seconds":
                survival_outputs[
                    1_780_179
                ],

            "survival_probability_at_14608619_seconds":
                survival_outputs[
                    14_608_619
                ],
        }
    )

    return result


# =============================================================================
# T7 HISTORY
# =============================================================================

def t7_history_before(
    t7_train: pd.DataFrame,
    boundary,
) -> pd.DataFrame:

    return (
        t7_train[
            t7_train[
                "_t8_creation_dt"
            ] < boundary
        ]
        .copy()
    )


# =============================================================================
# PREDICTION VALIDATION
# =============================================================================

def validate_oof_result(
    result: pd.DataFrame,
    expected_ids: set[Any],
    label: str,
) -> None:

    if len(result) != len(
        expected_ids
    ):

        raise RuntimeError(
            f"{label}: prediction row count "
            f"{len(result):,} does not match "
            f"expected {len(expected_ids):,}."
        )

    actual_ids = set(
        result["ID"]
    )

    if actual_ids != expected_ids:

        missing = (
            expected_ids
            - actual_ids
        )

        extra = (
            actual_ids
            - expected_ids
        )

        raise RuntimeError(
            f"{label}: ID mismatch. "
            f"missing={len(missing):,}, "
            f"extra={len(extra):,}"
        )

    if result[
        "ID"
    ].duplicated().any():

        raise RuntimeError(
            f"{label}: duplicate prediction IDs."
        )


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:

    overall_start = time.time()

    log(
        "=" * 78
    )

    log(
        "T8 MOD-029 — CONTROLLED JOINT "
        "T2/T7 CHRONOLOGICAL OoF"
    )

    log(
        "=" * 78
    )

    # =========================================================================
    # SOURCE VERIFICATION
    # =========================================================================

    if not T2_SOURCE.exists():

        raise FileNotFoundError(
            f"Missing frozen T2 source:\n{T2_SOURCE}"
        )

    if not T7_SOURCE.exists():

        raise FileNotFoundError(
            f"Missing frozen T7 source:\n{T7_SOURCE}"
        )

    t2_hash = sha256_file(
        T2_SOURCE
    )

    t7_hash = sha256_file(
        T7_SOURCE
    )

    log(
        "Frozen implementation sources:"
    )

    log(
        f"  T2: {T2_SOURCE}"
    )

    log(
        f"  T7: {T7_SOURCE}"
    )

    log(
        f"T2 source SHA256: {t2_hash}"
    )

    log(
        f"T7 source SHA256: {t7_hash}"
    )

    # =========================================================================
    # LOAD FROZEN IMPLEMENTATIONS
    # =========================================================================

    t2_namespace = (
        recover_t2_namespace()
    )

    t7_namespace = (
        recover_t7_namespace()
    )

    # =========================================================================
    # SPLITS
    # =========================================================================

    paths = resolve_splits()

    t2_train = load_csv(
        paths["t2_train"]
    )

    t2_validation = load_csv(
        paths["t2_validation"]
    )

    t2_test = load_csv(
        paths["t2_test"]
    )

    t7_train = load_csv(
        paths["t7_train"]
    )

    t7_eval = load_csv(
        paths["t7_eval"]
    )

    # =========================================================================
    # CREATION REPRESENTATION
    # =========================================================================

    t2_train = normalize_creation(
        t2_train
    )

    t2_validation = normalize_creation(
        t2_validation
    )

    t2_test = normalize_creation(
        t2_test
    )

    t7_train = normalize_creation(
        t7_train
    )

    t7_eval = normalize_creation(
        t7_eval
    )

    # =========================================================================
    # VALIDATION
    # =========================================================================

    validate_input_schemas(
        t2_train,
        t2_validation,
        t2_test,
        t7_train,
        t7_eval,
    )

    validate_split_integrity(
        t2_train,
        t2_validation,
        t2_test,
        t7_train,
        t7_eval,
    )

    # =========================================================================
    # COMMON DEVELOPMENT POPULATION
    # =========================================================================

    common = build_common_population(
        t2_train,
        t7_train,
    )

    blocks = make_blocks(
        common,
        N_BLOCKS,
    )

    # =========================================================================
    # T7 COLUMNS USED BY FROZEN IMPLEMENTATION
    # =========================================================================

    t7_feature_columns = [
        "ID",
        "Creation time",
        "Creator",
        "Creator Detail",
        "Summary",
        "Description",
        "duration_seconds",
        "event",
    ]

    # =========================================================================
    # ACCUMULATORS
    # =========================================================================

    t2_oof_parts = []

    t7_oof_parts = []

    joint_parts = []

    fold_manifest = []

    # =========================================================================
    # BLOCK LOOP
    # =========================================================================

    for block_number in range(
        1,
        len(blocks) + 1,
    ):

        block = (
            blocks[
                block_number - 1
            ]
            .copy()
        )

        boundary = block[
            "_t8_creation_dt"
        ].iloc[0]

        log()

        log(
            "=" * 78
        )

        log(
            f"B{block_number} — "
            f"prediction boundary "
            f"{boundary}"
        )

        log(
            "=" * 78
        )

        # =====================================================================
        # B1 WARM-UP
        # =====================================================================

        if block_number == 1:

            log(
                "B1 is warm-up only. "
                "No OoF predictions generated."
            )

            fold_manifest.append(
                {
                    "prediction_block":
                        "B1",

                    "status":
                        "WARMUP_ONLY",

                    "prediction_rows":
                        int(len(block)),

                    "prediction_start":
                        str(
                            block[
                                "_t8_creation_dt"
                            ].iloc[0]
                        ),

                    "prediction_end":
                        str(
                            block[
                                "_t8_creation_dt"
                            ].iloc[-1]
                        ),
                }
            )

            continue

        # =====================================================================
        # T2 TRAINING PREFIX
        # =====================================================================

        t2_history = (
            common[
                common[
                    "_t8_creation_dt"
                ] < boundary
            ]
            .copy()
        )

        if len(t2_history) == 0:

            raise RuntimeError(
                f"B{block_number}: "
                "T2 history is empty."
            )

        log(
            f"T2 history: "
            f"{len(t2_history):,}"
        )

        # =====================================================================
        # T2 FIT / PREDICT
        # =====================================================================

        t2_start = time.time()

        t2_result = fit_t2_fold(
            t2_history,
            block,
            t2_namespace,
        )

        t2_elapsed = (
            time.time()
            - t2_start
        )

        log(
            f"T2 B{block_number} complete "
            f"in {t2_elapsed:.2f}s"
        )

        validate_oof_result(
            t2_result,
            set(
                block["ID"]
            ),
            f"T2 B{block_number}",
        )

        t2_result[
            "prediction_block"
        ] = f"B{block_number}"

        t2_result[
            "prediction_creation_time"
        ] = (
            block[
                "_t8_creation_dt"
            ]
            .astype(str)
            .values
        )

        t2_result[
            "model_task"
        ] = "T2"

        t2_result[
            "implementation_identifier"
        ] = "T2-MOD-007"

        t2_result[
            "preprocessing_scope"
        ] = "fold_local_training_prefix"

        t2_result[
            "prediction_boundary"
        ] = "Creation"

        t2_oof_parts.append(
            t2_result
        )

        # =====================================================================
        # T7 TRAINING PREFIX
        # =====================================================================

        t7_history = t7_history_before(
            t7_train,
            boundary,
        )

        log(
            f"T7 history: "
            f"{len(t7_history):,}"
        )

        if len(t7_history) == 0:

            raise RuntimeError(
                f"B{block_number}: "
                "T7 history is empty."
            )

        # =====================================================================
        # T7 PREDICTION-SIDE RECOVERY
        #
        # `block` comes from T2 and therefore does not contain the T7
        # fields Creator, Creator Detail, duration_seconds, event, etc.
        #
        # The block defines the canonical IDs and chronological order.
        # Recover the actual T7 rows from t7_train using those IDs.
        # =====================================================================

        block_ids = (
            block["ID"]
            .tolist()
        )

        t7_prediction_source = (
            t7_train[
                t7_train[
                    "ID"
                ].isin(
                    set(block_ids)
                )
            ]
            .copy()
        )

        if len(
            t7_prediction_source
        ) != len(block):

            raise RuntimeError(
                f"B{block_number}: "
                "T7 prediction-side ID recovery "
                f"returned "
                f"{len(t7_prediction_source):,} "
                "rows; expected "
                f"{len(block):,}."
            )

        # Restore exact chronological block order.
        t7_prediction_source = (
            t7_prediction_source
            .set_index("ID")
            .loc[block_ids]
            .reset_index()
        )

        if (
            t7_prediction_source[
                "ID"
            ].tolist()
            != block_ids
        ):

            raise RuntimeError(
                f"B{block_number}: "
                "T7 prediction-side ID order "
                "does not match chronological "
                "prediction block."
            )

        log(
            "T7 prediction-side rows recovered: "
            f"{len(t7_prediction_source):,}"
        )

        # =====================================================================
        # T7 ROW DICTS
        #
        # Only frozen T7 fields are passed into make_features().
        # _t8_creation_dt is deliberately excluded.
        # =====================================================================

        t7_train_rows = (
            t7_history[
                t7_feature_columns
            ]
            .copy()
            .to_dict(
                "records"
            )
        )

        t7_pred_rows = (
            t7_prediction_source[
                t7_feature_columns
            ]
            .copy()
            .to_dict(
                "records"
            )
        )

        # Defensive representation check.
        for row_index, row in enumerate(
            t7_train_rows
        ):

            if not isinstance(
                row[
                    "Creation time"
                ],
                str,
            ):

                raise RuntimeError(
                    f"B{block_number}: "
                    "T7 training Creation time "
                    f"at row {row_index} "
                    "is not a string."
                )

        for row_index, row in enumerate(
            t7_pred_rows
        ):

            if not isinstance(
                row[
                    "Creation time"
                ],
                str,
            ):

                raise RuntimeError(
                    f"B{block_number}: "
                    "T7 prediction Creation time "
                    f"at row {row_index} "
                    "is not a string."
                )

        # =====================================================================
        # T7 FIT / PREDICT
        # =====================================================================

        log(
            f"T7 B{block_number} fitting..."
        )

        t7_start = time.time()

        t7_result = fit_t7_fold(
            t7_train_rows,
            t7_pred_rows,
            t7_namespace,
        )

        t7_elapsed = (
            time.time()
            - t7_start
        )

        log(
            f"T7 B{block_number} complete "
            f"in {t7_elapsed:.2f}s"
        )

        validate_oof_result(
            t7_result,
            set(
                block["ID"]
            ),
            f"T7 B{block_number}",
        )

        t7_result[
            "prediction_block"
        ] = f"B{block_number}"

        t7_result[
            "prediction_creation_time"
        ] = (
            block[
                "_t8_creation_dt"
            ]
            .astype(str)
            .values
        )

        t7_result[
            "model_task"
        ] = "T7"

        t7_result[
            "implementation_identifier"
        ] = "T7-MOD-010-LOGNORMAL-AFT"

        t7_result[
            "preprocessing_scope"
        ] = "fold_local_training_prefix"

        t7_result[
            "prediction_boundary"
        ] = "Creation"

        t7_oof_parts.append(
            t7_result
        )

        # =====================================================================
        # JOINT PREDICTION TABLE
        # =====================================================================

        t2_prediction_columns = [
            "ID",
            "predicted_priority",
            "predicted_probability_P1",
            "predicted_probability_P2",
            "predicted_probability_P3",
            "predicted_probability_P4",
            "predicted_probability_P5",
        ]

        t7_prediction_columns = [
            "ID",
            "predicted_median_survival_seconds",
            "survival_probability_at_211583_seconds",
            "survival_probability_at_1780179_seconds",
            "survival_probability_at_14608619_seconds",
        ]

        joint = (
            t2_result[
                t2_prediction_columns
            ]
            .merge(
                t7_result[
                    t7_prediction_columns
                ],
                on="ID",
                how="inner",
                validate="one_to_one",
            )
        )

        if len(joint) != len(
            block
        ):

            raise RuntimeError(
                f"B{block_number}: "
                "joint merge produced "
                f"{len(joint):,} rows; "
                f"expected {len(block):,}."
            )

        # =====================================================================
        # NATIVE OUTCOMES
        # =====================================================================

        t2_outcome = (
            block[
                [
                    "ID",
                    "target_priority",
                ]
            ]
            .copy()
        )

        t7_outcome = (
            t7_train[
                t7_train[
                    "ID"
                ].isin(
                    set(block_ids)
                )
            ][
                [
                    "ID",
                    "duration_seconds",
                    "event",
                ]
            ]
            .copy()
            .set_index("ID")
            .loc[block_ids]
            .reset_index()
        )

        if len(
            t7_outcome
        ) != len(block):

            raise RuntimeError(
                f"B{block_number}: "
                "T7 native outcome recovery "
                f"returned "
                f"{len(t7_outcome):,} rows; "
                f"expected {len(block):,}."
            )

        joint = (
            joint
            .merge(
                t2_outcome,
                on="ID",
                how="left",
                validate="one_to_one",
            )
            .merge(
                t7_outcome,
                on="ID",
                how="left",
                validate="one_to_one",
            )
        )

        # =====================================================================
        # JOINT PROVENANCE
        # =====================================================================

        joint[
            "prediction_block"
        ] = f"B{block_number}"

        joint[
            "prediction_creation_time"
        ] = (
            block[
                "_t8_creation_dt"
            ]
            .astype(str)
            .values
        )

        joint[
            "t2_implementation_identifier"
        ] = "T2-MOD-007"

        joint[
            "t7_implementation_identifier"
        ] = "T7-MOD-010-LOGNORMAL-AFT"

        joint[
            "t2_preprocessing_scope"
        ] = "fold_local_training_prefix"

        joint[
            "t7_preprocessing_scope"
        ] = "fold_local_training_prefix"

        joint[
            "prediction_boundary"
        ] = "Creation"

        joint_parts.append(
            joint
        )

        # =====================================================================
        # FOLD MANIFEST
        # =====================================================================

        fold_manifest.append(
            {
                "prediction_block":
                    f"B{block_number}",

                "status":
                    "PASS",

                "prediction_rows":
                    int(len(block)),

                "prediction_start":
                    str(
                        block[
                            "_t8_creation_dt"
                        ].iloc[0]
                    ),

                "prediction_end":
                    str(
                        block[
                            "_t8_creation_dt"
                        ].iloc[-1]
                    ),

                "t2_history_rows":
                    int(len(t2_history)),

                "t7_history_rows":
                    int(len(t7_history)),

                "t2_elapsed_seconds":
                    float(
                        t2_elapsed
                    ),

                "t7_elapsed_seconds":
                    float(
                        t7_elapsed
                    ),
            }
        )

        log(
            f"B{block_number} PASS — "
            f"{len(joint):,} joint predictions"
        )

    # =========================================================================
    # FINAL OOF TABLES
    # =========================================================================

    if not t2_oof_parts:

        raise RuntimeError(
            "No T2 OoF predictions generated."
        )

    if not t7_oof_parts:

        raise RuntimeError(
            "No T7 OoF predictions generated."
        )

    if not joint_parts:

        raise RuntimeError(
            "No joint OoF predictions generated."
        )

    t2_oof = pd.concat(
        t2_oof_parts,
        ignore_index=True,
    )

    t7_oof = pd.concat(
        t7_oof_parts,
        ignore_index=True,
    )

    joint_oof = pd.concat(
        joint_parts,
        ignore_index=True,
    )

    # All prediction blocks except B1.
    expected_oof_ids = set(
        pd.concat(
            blocks[1:],
            ignore_index=True,
        )["ID"]
    )

    validate_oof_result(
        t2_oof,
        expected_oof_ids,
        "Final T2 OoF",
    )

    validate_oof_result(
        t7_oof,
        expected_oof_ids,
        "Final T7 OoF",
    )

    validate_oof_result(
        joint_oof,
        expected_oof_ids,
        "Final joint OoF",
    )

    # =========================================================================
    # WRITE ARTIFACTS
    # =========================================================================

    T8_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    t2_oof.to_csv(
        T8_T2_OOF,
        index=False,
    )

    t7_oof.to_csv(
        T8_T7_OOF,
        index=False,
    )

    joint_oof.to_csv(
        T8_JOINT_OOF,
        index=False,
    )

    manifest = {
        "module":
            "T8-MOD-029",

        "status":
            "COMPLETE",

        "purpose":
            "Controlled joint T2/T7 chronological OoF generation",

        "fusion_performed":
            False,

        "synthetic_t8_target_created":
            False,

        "synthetic_t8_score_created":
            False,

        "source": {
            "t2_path":
                str(T2_SOURCE),

            "t2_sha256":
                t2_hash,

            "t7_path":
                str(T7_SOURCE),

            "t7_sha256":
                t7_hash,
        },

        "development_population": {
            "joint_rows":
                int(len(common)),

            "warmup_rows":
                int(len(blocks[0])),

            "prediction_rows":
                int(len(expected_oof_ids)),
        },

        "chronological_blocks":
            fold_manifest,

        "t2_oof_path":
            str(T8_T2_OOF),

        "t7_oof_path":
            str(T8_T7_OOF),

        "joint_oof_path":
            str(T8_JOINT_OOF),

        "runtime_seconds":
            float(
                time.time()
                - overall_start
            ),
    }

    T8_MANIFEST.write_text(
        json.dumps(
            manifest,
            indent=2,
        ),
        encoding="utf-8",
    )

    # =========================================================================
    # FINAL REPORT
    # =========================================================================

    log()

    log(
        "=" * 78
    )

    log(
        "T8 MOD-029 COMPLETE"
    )

    log(
        "=" * 78
    )

    log(
        f"T2 OoF rows: "
        f"{len(t2_oof):,}"
    )

    log(
        f"T7 OoF rows: "
        f"{len(t7_oof):,}"
    )

    log(
        f"Joint OoF rows: "
        f"{len(joint_oof):,}"
    )

    log(
        "T2 OoF artifact:"
    )

    log(
        f"  {T8_T2_OOF}"
    )

    log(
        "T7 OoF artifact:"
    )

    log(
        f"  {T8_T7_OOF}"
    )

    log(
        "Joint OoF artifact:"
    )

    log(
        f"  {T8_JOINT_OOF}"
    )

    log(
        "Generation manifest:"
    )

    log(
        f"  {T8_MANIFEST}"
    )

    log(
        "No fusion performed."
    )

    log(
        "No synthetic universal T8 target created."
    )

    log(
        "No synthetic universal T8 score created."
    )

    log(
        f"Total runtime: "
        f"{time.time() - overall_start:.2f}s"
    )


if __name__ == "__main__":

    main()