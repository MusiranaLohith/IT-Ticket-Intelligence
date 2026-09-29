from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


# ============================================================
# T9 MOD-037 OP-002
# Native Model-Output / Confidence Artifact Inventory
#
# Purpose:
#   Inventory actual prediction / probability / confidence /
#   uncertainty / ranking outputs already produced by T2-T8.
#
# This operation MUST NOT:
#   - fit a model
#   - fit a calibration model
#   - create targets
#   - select a model
#   - create thresholds
#   - create synthetic confidence
#   - create a universal confidence/risk score
#
# It only audits existing artifacts.
# ============================================================


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

MODELING_ROOT = PROJECT_ROOT / "modeling"

T9_ROOT = MODELING_ROOT / "T9"
OUTPUT_DIR = T9_ROOT / "mod037"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_JSON = OUTPUT_DIR / (
    "t9_mod037_op002_native_output_inventory.json"
)


# ------------------------------------------------------------
# Task boundaries
# ------------------------------------------------------------

TASKS = {
    "T1": MODELING_ROOT / "T1",
    "T2": MODELING_ROOT / "T2",
    "T3": MODELING_ROOT / "T3",
    "T4": MODELING_ROOT / "T4",
    "T5": MODELING_ROOT / "T5",
    "T6": MODELING_ROOT / "T6",
    "T7": MODELING_ROOT / "T7",
    "T8": MODELING_ROOT / "T8",
}


# ------------------------------------------------------------
# File types relevant to empirical output inspection
# ------------------------------------------------------------

SUPPORTED_SUFFIXES = {
    ".csv",
    ".npz",
    ".json",
}


# ------------------------------------------------------------
# Filename hints.
#
# These are discovery hints only.
# They do NOT establish that an artifact contains a valid
# confidence/probability output.
# ------------------------------------------------------------

FILENAME_HINTS = (
    "prediction",
    "predictions",
    "prob",
    "probability",
    "confidence",
    "uncertainty",
    "score",
    "ranking",
    "rank",
    "oof",
    "calibrat",
    "retrieval",
    "decision",
    "output",
)


# ------------------------------------------------------------
# Column/key semantic hints.
# ------------------------------------------------------------

SEMANTIC_HINTS = (
    "prob",
    "probability",
    "confidence",
    "uncertainty",
    "score",
    "prediction",
    "predicted",
    "ranking",
    "rank",
    "survival",
    "hazard",
    "risk",
    "logit",
    "distance",
    "similarity",
    "neighbor",
)


# Explicit fields which are important but must not automatically
# be interpreted as confidence.
SPECIAL_FIELDS = {
    "t8_score": "T8 score-like field; must be checked for population/non-blank values",
    "observable_non_positive": (
        "T6 retrieval state; NOT a true negative class"
    ),
}


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def safe_relative(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def semantic_matches(names: list[str]) -> list[str]:
    matches = []

    for name in names:
        lower = name.lower()

        if any(hint in lower for hint in SEMANTIC_HINTS):
            matches.append(name)

    return sorted(set(matches))


def filename_matches(path: Path) -> list[str]:
    lower = path.name.lower()

    return [
        hint
        for hint in FILENAME_HINTS
        if hint in lower
    ]


def scalar_summary(series: pd.Series) -> dict[str, Any]:
    result = {
        "dtype": str(series.dtype),
        "rows": int(len(series)),
        "non_null": int(series.notna().sum()),
        "null": int(series.isna().sum()),
        "non_null_rate": (
            float(series.notna().mean())
            if len(series) > 0
            else None
        ),
    }

    if len(series) == 0:
        return result

    if pd.api.types.is_numeric_dtype(series):
        numeric = pd.to_numeric(series, errors="coerce")

        finite = numeric[np.isfinite(numeric)]

        result["finite_numeric_values"] = int(len(finite))

        if len(finite) > 0:
            result["min"] = float(finite.min())
            result["max"] = float(finite.max())
            result["mean"] = float(finite.mean())
            result["median"] = float(finite.median())

    else:
        non_null_values = series.dropna()

        if len(non_null_values) > 0:
            result["unique_non_null"] = int(
                non_null_values.nunique(dropna=True)
            )

            sample = (
                non_null_values
                .astype(str)
                .drop_duplicates()
                .head(10)
                .tolist()
            )

            result["sample_values"] = sample

    return result


def inspect_csv(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "format": "csv",
        "path": safe_relative(path),
        "filename_hints": filename_matches(path),
        "status": "UNKNOWN",
    }

    try:
        header = pd.read_csv(path, nrows=0)
        columns = [str(c) for c in header.columns]

        result["columns"] = columns
        result["column_count"] = len(columns)
        result["semantic_columns"] = semantic_matches(columns)

        special = {
            field: meaning
            for field, meaning in SPECIAL_FIELDS.items()
            if field in columns
        }

        result["special_fields"] = special

        candidate_columns = sorted(
            set(result["semantic_columns"])
            | set(special.keys())
        )

        if candidate_columns:
            data = pd.read_csv(
                path,
                usecols=candidate_columns,
            )

            summaries = {}

            for column in candidate_columns:
                summaries[column] = scalar_summary(
                    data[column]
                )

            result["candidate_column_summaries"] = summaries

        # Exact row count without loading entire CSV.
        row_count = sum(
            1
            for _ in open(
                path,
                "r",
                encoding="utf-8",
                errors="replace",
            )
        ) - 1

        result["rows"] = max(row_count, 0)

        populated_candidates = []

        for column, summary in result.get(
            "candidate_column_summaries", {}
        ).items():
            if summary["non_null"] > 0:
                populated_candidates.append(column)

        result["populated_candidate_columns"] = (
            populated_candidates
        )

        result["status"] = "PASS"

    except Exception as exc:
        result["status"] = "ERROR"
        result["error"] = repr(exc)

    return result


def inspect_npz(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "format": "npz",
        "path": safe_relative(path),
        "filename_hints": filename_matches(path),
        "status": "UNKNOWN",
    }

    try:
        with np.load(path, allow_pickle=False) as data:
            keys = list(data.files)

            result["keys"] = keys
            result["key_count"] = len(keys)

            semantic_keys = semantic_matches(keys)

            result["semantic_keys"] = semantic_keys

            special = {
                field: meaning
                for field, meaning in SPECIAL_FIELDS.items()
                if field in keys
            }

            result["special_fields"] = special

            summaries = {}

            for key in keys:
                arr = np.asarray(data[key])

                summary = {
                    "shape": list(arr.shape),
                    "dtype": str(arr.dtype),
                    "size": int(arr.size),
                }

                if arr.size > 0:
                    if np.issubdtype(
                        arr.dtype,
                        np.number,
                    ):
                        finite = arr[
                            np.isfinite(arr)
                        ]

                        summary["finite_values"] = int(
                            finite.size
                        )

                        if finite.size > 0:
                            summary["min"] = float(
                                np.min(finite)
                            )
                            summary["max"] = float(
                                np.max(finite)
                            )
                            summary["mean"] = float(
                                np.mean(finite)
                            )
                            summary["median"] = float(
                                np.median(finite)
                            )

                    elif arr.dtype.kind in {"U", "S"}:
                        summary["sample_values"] = [
                            str(x)
                            for x in arr.flatten()[:10]
                        ]

                summaries[key] = summary

            result["key_summaries"] = summaries

            result["populated_semantic_keys"] = [
                key
                for key in semantic_keys
                if summaries[key]["size"] > 0
            ]

        result["status"] = "PASS"

    except Exception as exc:
        result["status"] = "ERROR"
        result["error"] = repr(exc)

    return result


def inspect_json(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "format": "json",
        "path": safe_relative(path),
        "filename_hints": filename_matches(path),
        "status": "UNKNOWN",
    }

    try:
        with open(
            path,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        result["top_level_type"] = type(data).__name__

        if isinstance(data, dict):
            top_keys = [
                str(k)
                for k in data.keys()
            ]

            result["top_level_keys"] = top_keys
            result["semantic_keys"] = semantic_matches(
                top_keys
            )

            result["special_fields"] = {
                field: meaning
                for field, meaning in SPECIAL_FIELDS.items()
                if field in data
            }

        elif isinstance(data, list):
            result["list_length"] = len(data)

            if data and isinstance(data[0], dict):
                first_keys = [
                    str(k)
                    for k in data[0].keys()
                ]

                result["first_item_keys"] = first_keys
                result["semantic_keys"] = semantic_matches(
                    first_keys
                )

        result["status"] = "PASS"

    except Exception as exc:
        result["status"] = "ERROR"
        result["error"] = repr(exc)

    return result


def inspect_file(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return inspect_csv(path)

    if suffix == ".npz":
        return inspect_npz(path)

    if suffix == ".json":
        return inspect_json(path)

    return {
        "format": suffix,
        "path": safe_relative(path),
        "status": "SKIPPED",
    }


# ------------------------------------------------------------
# Main inventory
# ------------------------------------------------------------

def main() -> None:
    print("=" * 72)
    print("T9 MOD-037 OP-002")
    print("Native Model-Output / Confidence Artifact Inventory")
    print("=" * 72)

    print()
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Output:       {OUTPUT_JSON}")
    print()

    if not PROJECT_ROOT.exists():
        raise FileNotFoundError(
            f"Project root does not exist: {PROJECT_ROOT}"
        )

    artifact_inventory: dict[str, list[dict[str, Any]]] = {}
    all_artifacts: list[dict[str, Any]] = []

    # --------------------------------------------------------
    # Discover candidate empirical artifacts.
    #
    # We inspect CSV / NPZ / JSON artifacts only.
    # Model binaries such as .h5/.keras are intentionally
    # excluded because they are not prediction-output artifacts.
    # --------------------------------------------------------

    for task, task_root in TASKS.items():

        if not task_root.exists():
            artifact_inventory[task] = []
            continue

        candidates = []

        for path in task_root.rglob("*"):

            if not path.is_file():
                continue

            if path.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue

            hints = filename_matches(path)

            # A file is considered an OP-002 candidate if:
            #   1. its filename indicates output/prediction-like
            #      semantics, OR
            #   2. it contains a likely semantic field after
            #      header/key inspection.
            #
            # We therefore initially collect all supported
            # structured artifacts. This avoids silently missing
            # a prediction file with an unexpected filename.
            candidates.append(path)

        candidates = sorted(
            candidates,
            key=lambda p: str(p),
        )

        artifact_inventory[task] = []

        for path in candidates:

            print(
                f"Inspecting {task}: "
                f"{safe_relative(path)}"
            )

            inspected = inspect_file(path)

            # Keep all inspected artifacts, because the purpose
            # is an auditable inventory rather than only a
            # filtered list of "confidence-looking" files.
            artifact_inventory[task].append(inspected)
            all_artifacts.append(inspected)

    # --------------------------------------------------------
    # Determine empirical findings.
    # --------------------------------------------------------

    populated_semantic_fields = []
    blank_t8_score_fields = []
    prediction_like_artifacts = []
    confidence_like_artifacts = []
    uncertainty_like_artifacts = []

    for artifact in all_artifacts:

        if artifact.get("status") != "PASS":
            continue

        path = artifact["path"]

        # CSV
        if artifact.get("format") == "csv":

            semantic_columns = artifact.get(
                "semantic_columns",
                [],
            )

            populated = artifact.get(
                "populated_candidate_columns",
                [],
            )

            for column in populated:
                populated_semantic_fields.append({
                    "path": path,
                    "field": column,
                    "type": "csv_column",
                })

                lower = column.lower()

                if (
                    "confidence" in lower
                    or "probability" in lower
                    or "prob" in lower
                ):
                    confidence_like_artifacts.append({
                        "path": path,
                        "field": column,
                    })

                if "uncertainty" in lower:
                    uncertainty_like_artifacts.append({
                        "path": path,
                        "field": column,
                    })

                if (
                    "prediction" in lower
                    or "predicted" in lower
                ):
                    prediction_like_artifacts.append({
                        "path": path,
                        "field": column,
                    })

            if "t8_score" in artifact.get(
                "special_fields",
                {},
            ):
                summary = artifact.get(
                    "candidate_column_summaries",
                    {},
                ).get("t8_score")

                if summary is not None:
                    if summary.get("non_null", 0) == 0:
                        blank_t8_score_fields.append({
                            "path": path,
                            "field": "t8_score",
                            "status": "BLANK",
                        })
                    else:
                        blank_t8_score_fields.append({
                            "path": path,
                            "field": "t8_score",
                            "status": "POPULATED",
                            "non_null": summary.get(
                                "non_null"
                            ),
                        })

        # NPZ
        elif artifact.get("format") == "npz":

            semantic_keys = artifact.get(
                "semantic_keys",
                [],
            )

            populated_keys = artifact.get(
                "populated_semantic_keys",
                [],
            )

            for key in populated_keys:
                populated_semantic_fields.append({
                    "path": path,
                    "field": key,
                    "type": "npz_key",
                })

                lower = key.lower()

                if (
                    "confidence" in lower
                    or "probability" in lower
                    or "prob" in lower
                ):
                    confidence_like_artifacts.append({
                        "path": path,
                        "field": key,
                    })

                if "uncertainty" in lower:
                    uncertainty_like_artifacts.append({
                        "path": path,
                        "field": key,
                    })

                if (
                    "prediction" in lower
                    or "predicted" in lower
                ):
                    prediction_like_artifacts.append({
                        "path": path,
                        "field": key,
                    })

        # JSON
        elif artifact.get("format") == "json":

            semantic_keys = artifact.get(
                "semantic_keys",
                [],
            )

            for key in semantic_keys:
                populated_semantic_fields.append({
                    "path": path,
                    "field": key,
                    "type": "json_key",
                })

    # --------------------------------------------------------
    # Important OP-002 conclusion.
    #
    # We do NOT declare calibration readiness merely because
    # a score/prediction exists.
    # --------------------------------------------------------

    findings = {
        "supported_prediction_like_fields": (
            prediction_like_artifacts
        ),
        "supported_confidence_probability_like_fields": (
            confidence_like_artifacts
        ),
        "supported_uncertainty_like_fields": (
            uncertainty_like_artifacts
        ),
        "blank_t8_score_fields": blank_t8_score_fields,
    }

    # --------------------------------------------------------
    # Controls
    # --------------------------------------------------------

    controls = {
        "model_fitting_performed": False,
        "calibration_fitting_performed": False,
        "target_creation_performed": False,
        "model_selection_performed": False,
        "threshold_selection_performed": False,
        "universal_confidence_created": False,
        "universal_risk_score_created": False,
        "synthetic_target_created": False,
        "t6_observable_non_positive_reinterpreted_as_true_negative": False,
        "t7_converted_to_binary_resolution": False,
        "t7_censoring_relabelled": False,
    }

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary = {
        "tasks_scanned": list(TASKS.keys()),
        "artifact_count": len(all_artifacts),
        "artifact_count_by_task": {
            task: len(items)
            for task, items in artifact_inventory.items()
        },
        "populated_semantic_field_count": len(
            populated_semantic_fields
        ),
        "prediction_like_field_count": len(
            prediction_like_artifacts
        ),
        "confidence_probability_like_field_count": len(
            confidence_like_artifacts
        ),
        "uncertainty_like_field_count": len(
            uncertainty_like_artifacts
        ),
        "blank_t8_score_count": len(
            [
                x
                for x in blank_t8_score_fields
                if x.get("status") == "BLANK"
            ]
        ),
    }

    # --------------------------------------------------------
    # Write auditable artifact
    # --------------------------------------------------------

    output = {
        "operation": "T9_MOD-037_OP-002",
        "title": (
            "Native Model-Output / Confidence Artifact Inventory"
        ),
        "status": "PASS",
        "purpose": (
            "Inventory existing T2-T8 prediction, probability, "
            "confidence, ranking, and uncertainty artifacts "
            "without fitting models, calibration procedures, "
            "targets, thresholds, or universal confidence scores."
        ),
        "project_root": str(PROJECT_ROOT),
        "tasks": {
            task: str(path)
            for task, path in TASKS.items()
        },
        "summary": summary,
        "findings": findings,
        "controls": controls,
        "artifact_inventory": artifact_inventory,
        "interpretation_rules": {
            "blank_t8_score": (
                "A blank t8_score field is not evidence of "
                "confidence or calibration."
            ),
            "t6_observable_non_positive": (
                "observable_non_positive is not a true negative "
                "classification target."
            ),
            "t7_survival": (
                "T7 survival/time-to-event outputs must retain "
                "right-censoring semantics and must not be "
                "converted into ordinary binary confidence."
            ),
            "cross_task_confidence": (
                "Task-specific confidence/probability quantities "
                "are not assumed numerically comparable across "
                "T2-T7."
            ),
        },
    }

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False,
        )

    # --------------------------------------------------------
    # Console summary
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print("T9 MOD-037 OP-002 RESULT")
    print("=" * 72)

    print(
        f"Artifacts inspected: "
        f"{summary['artifact_count']}"
    )

    print(
        f"Prediction-like fields: "
        f"{summary['prediction_like_field_count']}"
    )

    print(
        f"Confidence/probability-like fields: "
        f"{summary['confidence_probability_like_field_count']}"
    )

    print(
        f"Uncertainty-like fields: "
        f"{summary['uncertainty_like_field_count']}"
    )

    print(
        f"Blank t8_score fields: "
        f"{summary['blank_t8_score_count']}"
    )

    print()
    print("Controls:")
    for key, value in controls.items():
        print(f"  {key}: {value}")

    print()
    print(f"Output: {OUTPUT_JSON}")
    print()
    print("T9 MOD-037 OP-002 inventory: PASS")


if __name__ == "__main__":
    main()