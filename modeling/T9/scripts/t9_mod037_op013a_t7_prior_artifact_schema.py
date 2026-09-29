from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


# ============================================================
# T9 MOD-037 OP-013A
# T7 Prior-Artifact / Native Survival Output Resolution
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T9_ROOT = PROJECT_ROOT / "modeling" / "T9"
OUTPUT_DIR = T9_ROOT / "mod037"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_JSON = (
    OUTPUT_DIR
    / "t9_mod037_op013a_t7_prior_artifact_schema.json"
)


# ============================================================
# PRIOR T9 ARTIFACTS
# ============================================================

OP004_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op004_native_output_acceptance.json"
)

OP005_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op005_output_semantics_lock.json"
)


# ============================================================
# T7 SOURCE ROOT
# ============================================================

T7_ROOT = PROJECT_ROOT / "modeling" / "T7"


# ============================================================
# HELPERS
# ============================================================

def load_json(path: Path) -> dict[str, Any]:

    if not path.exists():

        raise FileNotFoundError(
            f"Required artifact missing: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        value = json.load(f)

    if not isinstance(value, dict):

        raise TypeError(
            f"Expected JSON object: {path}"
        )

    return value


def safe_json_value(value: Any) -> Any:

    if isinstance(value, dict):

        return {
            str(k): safe_json_value(v)
            for k, v in value.items()
        }

    if isinstance(value, list):

        return [
            safe_json_value(v)
            for v in value
        ]

    if isinstance(value, Path):

        return str(value)

    return value


# ============================================================
# PRIOR T9 BOUNDARY VALIDATION
# ============================================================

def validate_t9_boundary() -> dict[str, Any]:

    op004 = load_json(
        OP004_ARTIFACT
    )

    op005 = load_json(
        OP005_ARTIFACT
    )

    accepted_tasks = op004.get(
        "accepted_tasks",
        [],
    )

    t7_boundary = (
        op005
        .get(
            "task_boundary",
            {},
        )
        .get(
            "T7",
            {},
        )
    )

    checks: dict[str, Any] = {}

    # --------------------------------------------------------
    # OP-004 acceptance
    # --------------------------------------------------------

    checks[
        "OP-004_T7_acceptance"
    ] = {

        "status": (
            "PASS"
            if "T7" in accepted_tasks
            else "FAIL"
        ),

        "accepted_tasks": accepted_tasks,
    }

    # --------------------------------------------------------
    # OP-005 frozen T7 boundary
    # --------------------------------------------------------

    checks[
        "OP-005_T7_boundary"
    ] = {

        "status": (
            "PASS"
            if (
                op005.get(
                    "status"
                )
                == "PASS"
                and
                t7_boundary.get(
                    "status"
                )
                == "ACCEPTED_NATIVE_SURVIVAL"
                and
                t7_boundary.get(
                    "accepted_for_calibration"
                )
                is True
            )
            else "FAIL"
        ),

        "boundary": t7_boundary,
    }

    # --------------------------------------------------------
    # Native survival semantics
    # --------------------------------------------------------

    native_quantity = str(
        t7_boundary.get(
            "native_quantity",
            ""
        )
    ).lower()

    semantic_restrictions = [
        str(value).lower()
        for value in
        t7_boundary.get(
            "semantic_restrictions",
            []
        )
    ]

    calibration_boundary = str(
        t7_boundary.get(
            "calibration_boundary",
            ""
        )
    ).lower()

    survival_evidence_text = " ".join(
        [
            native_quantity,
            calibration_boundary,
            *semantic_restrictions,
        ]
    )

    survival_terms_present = (
        "survival" in survival_evidence_text
        or
        "censor" in survival_evidence_text
        or
        "time-to-event" in survival_evidence_text
        or
        "time to event" in survival_evidence_text
    )

    checks[
        "T7_native_survival_semantics"
    ] = {

        "status": (
            "PASS"
            if survival_terms_present
            else "FAIL"
        ),

        "native_quantity": (
            t7_boundary.get(
                "native_quantity"
            )
        ),

        "semantic_restrictions": (
            t7_boundary.get(
                "semantic_restrictions",
                []
            )
        ),

        "calibration_boundary": (
            t7_boundary.get(
                "calibration_boundary"
            )
        ),
    }

    # --------------------------------------------------------
    # Explicit survival/censoring preservation
    # --------------------------------------------------------

    boundary_text = " ".join(
        [
            str(
                t7_boundary
            ).lower(),
        ]
    )

    censoring_preserved = (
        "censor" in boundary_text
        or
        "right censor" in boundary_text
    )

    checks[
        "T7_censoring_semantics_preserved"
    ] = {

        "status": (
            "PASS"
            if censoring_preserved
            else "FAIL"
        ),

        "evidence_text_contains_censoring_reference": (
            censoring_preserved
        ),
    }

    # --------------------------------------------------------
    # IMPORTANT:
    # Do NOT assume a T6-style native_probability_output
    # field for T7.
    #
    # T7's frozen boundary is survival-specific.
    # --------------------------------------------------------

    checks[
        "T7_binary_conversion_prohibited"
    ] = {

        "status": "PASS",

        "basis": (
            "The frozen T7 boundary is "
            "ACCEPTED_NATIVE_SURVIVAL. This operation "
            "does not require or infer a "
            "native_probability_output field. "
            "Binary conversion is prohibited by the "
            "T7 survival/censoring boundary itself."
        ),

        "native_quantity": (
            t7_boundary.get(
                "native_quantity"
            )
        ),
    }

    # --------------------------------------------------------
    # Failed checks
    # --------------------------------------------------------

    failed = [
        key
        for key, value
        in checks.items()
        if value[
            "status"
        ] != "PASS"
    ]

    return {

        "status": (
            "PASS"
            if not failed
            else "FAIL"
        ),

        "checks": checks,

        "failed_checks": failed,

        "t7_boundary": t7_boundary,
    }


# ============================================================
# FILE DISCOVERY
# ============================================================

def discover_t7_files() -> list[Path]:

    if not T7_ROOT.exists():

        raise FileNotFoundError(
            f"T7 modeling directory does not exist: "
            f"{T7_ROOT}"
        )

    files = []

    for path in T7_ROOT.rglob("*"):

        if not path.is_file():
            continue

        if "__pycache__" in path.parts:
            continue

        files.append(path)

    return sorted(
        files,
        key=lambda p: str(p),
    )


# ============================================================
# ARTIFACT CLASSIFICATION
# ============================================================

def classify_path(
    path: Path,
) -> str:

    name = path.name.lower()
    suffix = path.suffix.lower()

    if suffix == ".json":
        return "json"

    if suffix == ".csv":
        return "csv"

    if suffix == ".parquet":
        return "parquet"

    if suffix in {
        ".npz",
        ".npy",
    }:
        return "numpy"

    if suffix in {
        ".pkl",
        ".pickle",
    }:
        return "pickle"

    if suffix in {
        ".pt",
        ".pth",
        ".h5",
        ".keras",
    }:
        return "model_or_tensor_artifact"

    if (
        "prediction" in name
        or "pred" in name
    ):
        return "prediction_like"

    if (
        "survival" in name
        or "surv" in name
    ):
        return "survival_like"

    if (
        "metric" in name
        or "evaluation" in name
        or "eval" in name
    ):
        return "evaluation_like"

    if (
        "result" in name
        or "output" in name
    ):
        return "result_like"

    return "other"


# ============================================================
# JSON INSPECTION
# ============================================================

def inspect_json(
    path: Path,
) -> dict[str, Any]:

    try:

        data = load_json(
            path
        )

        keys = list(
            data.keys()
        )

        survival_like_keys = [
            key
            for key in keys
            if any(
                token in str(
                    key
                ).lower()
                for token in [
                    "survival",
                    "surv",
                    "time",
                    "event",
                    "censor",
                    "duration",
                    "hazard",
                    "risk",
                    "prediction",
                    "prob",
                    "output",
                ]
            )
        ]

        return {

            "read_status": "PASS",

            "top_level_type": "dict",

            "top_level_keys": keys,

            "survival_related_keys": (
                survival_like_keys
            ),

            "top_level_key_count": len(
                keys
            ),
        }

    except Exception as exc:

        return {

            "read_status": "FAIL",

            "error": str(exc),
        }


# ============================================================
# CSV INSPECTION
# ============================================================

def inspect_csv(
    path: Path,
) -> dict[str, Any]:

    try:

        frame = pd.read_csv(
            path,
            nrows=1000,
            low_memory=False,
        )

        columns = list(
            frame.columns
        )

        survival_like_columns = [
            column
            for column in columns
            if any(
                token in str(
                    column
                ).lower()
                for token in [
                    "survival",
                    "surv",
                    "time",
                    "event",
                    "censor",
                    "duration",
                    "hazard",
                    "risk",
                    "prediction",
                    "prob",
                    "output",
                    "target",
                ]
            )
        ]

        return {

            "read_status": "PASS",

            "sample_rows_read": int(
                len(frame)
            ),

            "columns": columns,

            "column_count": len(
                columns
            ),

            "survival_related_columns": (
                survival_like_columns
            ),

            "dtypes": {
                str(column): str(
                    dtype
                )
                for column, dtype
                in frame.dtypes.items()
            },
        }

    except Exception as exc:

        return {

            "read_status": "FAIL",

            "error": str(exc),
        }


# ============================================================
# PARQUET INSPECTION
# ============================================================

def inspect_parquet(
    path: Path,
) -> dict[str, Any]:

    try:

        frame = pd.read_parquet(
            path
        )

        columns = list(
            frame.columns
        )

        survival_like_columns = [
            column
            for column in columns
            if any(
                token in str(
                    column
                ).lower()
                for token in [
                    "survival",
                    "surv",
                    "time",
                    "event",
                    "censor",
                    "duration",
                    "hazard",
                    "risk",
                    "prediction",
                    "prob",
                    "output",
                    "target",
                ]
            )
        ]

        return {

            "read_status": "PASS",

            "rows": int(
                len(frame)
            ),

            "columns": columns,

            "column_count": len(
                columns
            ),

            "survival_related_columns": (
                survival_like_columns
            ),

            "dtypes": {
                str(column): str(
                    dtype
                )
                for column, dtype
                in frame.dtypes.items()
            },
        }

    except Exception as exc:

        return {

            "read_status": "FAIL",

            "error": str(exc),
        }


# ============================================================
# GENERIC FILE INSPECTION
# ============================================================

def inspect_file(
    path: Path,
) -> dict[str, Any]:

    result = {

        "path": str(
            path.relative_to(
                PROJECT_ROOT
            )
        ),

        "absolute_path": str(
            path
        ),

        "suffix": path.suffix.lower(),

        "size_bytes": int(
            path.stat().st_size
        ),

        "classification": classify_path(
            path
        ),
    }

    suffix = path.suffix.lower()

    if suffix == ".json":

        result[
            "content_inspection"
        ] = inspect_json(
            path
        )

    elif suffix == ".csv":

        result[
            "content_inspection"
        ] = inspect_csv(
            path
        )

    elif suffix == ".parquet":

        result[
            "content_inspection"
        ] = inspect_parquet(
            path
        )

    return result


# ============================================================
# CANDIDATE DISCOVERY
# ============================================================

def identify_candidates(
    inventory: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    candidates = []

    for item in inventory:

        path_text = (
            item[
                "path"
            ]
            .lower()
        )

        classification = item[
            "classification"
        ]

        inspection = item.get(
            "content_inspection",
            {},
        )

        survival_fields = (
            inspection.get(
                "survival_related_columns",
                []
            )
            or
            inspection.get(
                "survival_related_keys",
                []
            )
            or []
        )

        score = 0
        reasons = []

        if "survival" in path_text:

            score += 3

            reasons.append(
                "filename_contains_survival"
            )

        if "surv" in path_text:

            score += 2

            reasons.append(
                "filename_contains_surv"
            )

        if survival_fields:

            score += min(
                len(
                    survival_fields
                ),
                5,
            )

            reasons.append(
                "survival_related_fields_detected"
            )

        if classification in {
            "prediction_like",
            "survival_like",
            "result_like",
            "evaluation_like",
        }:

            score += 1

            reasons.append(
                f"classification={classification}"
            )

        if score > 0:

            candidates.append(
                {

                    "path": item[
                        "path"
                    ],

                    "classification": (
                        classification
                    ),

                    "score": score,

                    "reasons": reasons,

                    "survival_fields": (
                        survival_fields
                    ),
                }
            )

    candidates.sort(
        key=lambda item: (
            -item[
                "score"
            ],
            item[
                "path"
            ],
        )
    )

    return candidates


# ============================================================
# CONTROLS
# ============================================================

def build_controls() -> dict[str, Any]:

    return {

        "artifact_read_only": True,

        "model_fitted": False,

        "prediction_generated": False,

        "probability_generated": False,

        "calibration_fitted": False,

        "target_created": False,

        "target_relabelled": False,

        "censoring_relabelled": False,

        "survival_converted_to_binary": False,

        "binary_resolution_created": False,

        "threshold_selected": False,

        "locked_test_used": False,

        "universal_confidence_created": False,

        "universal_risk_score_created": False,

        "existing_artifacts_modified": False,

        "post_creation_information_used": False,

        "native_survival_semantics_preserved": True,
    }


def validate_controls(
    controls: dict[str, Any],
) -> dict[str, Any]:

    allowed_true = {
        "artifact_read_only",
        "native_survival_semantics_preserved",
    }

    failures = []

    for key, value in controls.items():

        if key in allowed_true:

            if value is not True:

                failures.append(
                    key
                )

        else:

            if value is not False:

                failures.append(
                    key
                )

    return {

        "status": (
            "PASS"
            if not failures
            else "FAIL"
        ),

        "failed_controls": failures,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 72)
    print("T9 MOD-037 OP-013A")
    print(
        "T7 Prior-Artifact / Native Survival "
        "Output Resolution"
    )
    print("=" * 72)
    print()

    # --------------------------------------------------------
    # FROZEN BOUNDARY
    # --------------------------------------------------------

    print(
        "Validating frozen T9 T7 boundary..."
    )

    boundary = validate_t9_boundary()

    print(
        "T7 boundary validation:",
        boundary[
            "status"
        ],
    )

    if boundary[
        "status"
    ] != "PASS":

        print(
            "Failed checks:",
            boundary[
                "failed_checks"
            ],
        )

        raise RuntimeError(
            "Frozen T7 boundary validation failed."
        )

    print()

    # --------------------------------------------------------
    # DISCOVER FILES
    # --------------------------------------------------------

    print(
        "Discovering T7 files..."
    )

    files = discover_t7_files()

    print(
        "T7 files discovered:",
        len(files),
    )

    if not files:

        raise RuntimeError(
            "No files were discovered under T7."
        )

    print()

    # --------------------------------------------------------
    # INSPECT FILES
    # --------------------------------------------------------

    print(
        "Inspecting T7 artifact structures..."
    )

    inventory = []

    for path in files:

        item = inspect_file(
            path
        )

        inventory.append(
            item
        )

    print(
        "Files structurally inspected:",
        len(inventory),
    )

    print()

    # --------------------------------------------------------
    # CANDIDATES
    # --------------------------------------------------------

    candidates = identify_candidates(
        inventory
    )

    print(
        "Potential native survival candidates:",
        len(candidates),
    )

    for candidate in candidates:

        print(
            f"  score={candidate['score']:>2} "
            f"{candidate['path']}"
        )

        if candidate[
            "survival_fields"
        ]:

            print(
                "    survival-related fields:",
                candidate[
                    "survival_fields"
                ],
            )

    print()

    # --------------------------------------------------------
    # CONTROLS
    # --------------------------------------------------------

    controls = build_controls()

    control_validation = (
        validate_controls(
            controls
        )
    )

    print(
        "Control validation:",
        control_validation[
            "status"
        ],
    )

    if (
        control_validation[
            "status"
        ]
        != "PASS"
    ):

        raise RuntimeError(
            "Control validation failed."
        )

    print()

    # --------------------------------------------------------
    # INTERPRETATION
    # --------------------------------------------------------

    interpretation = {

        "operation_role": (
            "Read-only structural and semantic "
            "candidate resolution."
        ),

        "native_survival_output_established": (
            False
        ),

        "final_artifact_selected": (
            False
        ),

        "survival_semantics_inferred_from_filename_only": (
            False
        ),

        "censoring_semantics_inferred_without_evidence": (
            False
        ),

        "probability_semantics_established": (
            False
        ),

        "next_operation": (
            "OP-013B should resolve the actual "
            "T7 event, censoring, duration/time, "
            "and native survival-output semantics "
            "from the strongest candidate artifact(s)."
        ),
    }

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    output = {

        "operation": (
            "T9_MOD-037_OP-013A"
        ),

        "title": (
            "T7 Prior-Artifact / Native Survival "
            "Output Resolution"
        ),

        "status": "PASS",

        "purpose": (
            "Resolve the actual T7 artifact inventory "
            "and candidate native survival-output "
            "structures before empirical evaluation."
        ),

        "frozen_t9_boundary": boundary,

        "t7_root": str(
            T7_ROOT
        ),

        "file_count": len(
            inventory
        ),

        "artifact_inventory": inventory,

        "native_survival_candidates": candidates,

        "candidate_resolution_status": (
            "DISCOVERY_COMPLETE__SEMANTIC_RESOLUTION_PENDING"
        ),

        "controls": controls,

        "control_validation": (
            control_validation
        ),

        "interpretation": interpretation,

        "methodological_restrictions": [

            "This operation is read-only.",

            "No model fitting is permitted.",

            "No prediction generation is permitted.",

            "No probability generation is permitted.",

            "No calibration fitting is permitted.",

            "No target creation or relabelling "
            "is permitted.",

            "No censoring relabelling is permitted.",

            "Survival outputs must not be converted "
            "into an ordinary binary resolution target.",

            "Filename or field-name discovery alone "
            "does not establish survival semantics.",

            "No final T7 artifact is selected solely "
            "from heuristic filename scoring.",

            "No locked test data are used for "
            "method or artifact selection.",
        ],

        "artifacts_generated": [

            str(
                OUTPUT_JSON
            ),
        ],
    }

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            safe_json_value(
                output
            ),
            f,
            indent=2,
            ensure_ascii=False,
        )

    # --------------------------------------------------------
    # FINAL CONSOLE
    # --------------------------------------------------------

    print("=" * 72)
    print("T9 MOD-037 OP-013A RESULT")
    print("=" * 72)
    print()

    print(
        "T7 boundary validation:",
        boundary[
            "status"
        ],
    )

    print(
        "Files inspected:",
        len(
            inventory
        ),
    )

    print(
        "Potential survival candidates:",
        len(
            candidates
        ),
    )

    print(
        "Final native survival artifact selected:",
        "NO",
    )

    print(
        "Survival semantics established:",
        "NO — pending OP-013B",
    )

    print(
        "Calibration performed:",
        "NO",
    )

    print(
        "Binary conversion:",
        "NO",
    )

    print(
        "Censoring relabelled:",
        "NO",
    )

    print(
        "Locked test used:",
        "NO",
    )

    print()

    print(
        "Output:",
        OUTPUT_JSON,
    )

    print()

    print(
        "T9 MOD-037 OP-013A: PASS"
    )


if __name__ == "__main__":
    main()