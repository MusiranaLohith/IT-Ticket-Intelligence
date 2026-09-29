from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# ============================================================
# T9 MOD-037 OP-011A
# T4 Prior-Artifact Schema Resolution
#
# Purpose:
#   Inspect the ACTUAL JSON structures of the prior T9/T8
#   artifacts required by OP-011.
#
# This is a read-only schema-resolution operation.
#
# It DOES NOT:
#   - fit a model
#   - generate predictions
#   - generate probabilities
#   - calibrate anything
#   - create targets
#   - select thresholds
#   - use test data
#   - modify any existing artifact
# ============================================================


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T9_ROOT = (
    PROJECT_ROOT
    / "modeling"
    / "T9"
)

OUTPUT_DIR = (
    T9_ROOT
    / "mod037"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUTPUT_JSON = (
    OUTPUT_DIR
    / "t9_mod037_op011a_t4_prior_artifact_schema.json"
)


# ------------------------------------------------------------
# Prior artifacts
# ------------------------------------------------------------

OP004_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op004_native_output_acceptance.json"
)

OP005_ARTIFACT = (
    OUTPUT_DIR
    / "t9_mod037_op005_output_semantics_lock.json"
)

OP020_ARTIFACT = (
    PROJECT_ROOT
    / "modeling"
    / "T8"
    / "mod036"
    / "op020"
    / "t8_mod036_op020_assignment_component_baseline.json"
)


# ============================================================
# Helpers
# ============================================================

def load_json(
    path: Path,
) -> dict[str, Any]:

    if not path.exists():

        raise FileNotFoundError(
            f"Required artifact missing: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        data = json.load(f)

    if not isinstance(
        data,
        dict,
    ):

        raise TypeError(
            f"Expected JSON object at {path}, "
            f"got {type(data).__name__}"
        )

    return data


def summarize_value(
    value: Any,
    depth: int = 0,
    max_depth: int = 3,
) -> Any:
    """
    Produce a compact recursive schema summary without
    dumping large arrays or complete nested artifacts.
    """

    if depth >= max_depth:

        return {
            "type": type(value).__name__,
        }

    if isinstance(
        value,
        dict,
    ):

        return {
            "type": "dict",
            "keys": {
                str(key): summarize_value(
                    child,
                    depth + 1,
                    max_depth,
                )
                for key, child in value.items()
            },
        }

    if isinstance(
        value,
        list,
    ):

        result = {
            "type": "list",
            "length": len(value),
        }

        if value:

            result[
                "first_item"
            ] = summarize_value(
                value[0],
                depth + 1,
                max_depth,
            )

        return result

    return {
        "type": type(value).__name__,
        "value": value,
    }


def find_key_paths(
    obj: Any,
    target_keys: set[str],
    path: str = "",
) -> list[dict[str, Any]]:

    matches = []

    if isinstance(
        obj,
        dict,
    ):

        for key, value in obj.items():

            current_path = (
                f"{path}.{key}"
                if path
                else str(key)
            )

            if str(key) in target_keys:

                matches.append(
                    {
                        "key": str(key),
                        "path": current_path,
                        "value_type": (
                            type(value).__name__
                        ),
                        "value": (
                            value
                            if not isinstance(
                                value,
                                (
                                    dict,
                                    list,
                                ),
                            )
                            else None
                        ),
                    }
                )

            matches.extend(
                find_key_paths(
                    value,
                    target_keys,
                    current_path,
                )
            )

    elif isinstance(
        obj,
        list,
    ):

        for index, value in enumerate(obj):

            current_path = (
                f"{path}[{index}]"
            )

            matches.extend(
                find_key_paths(
                    value,
                    target_keys,
                    current_path,
                )
            )

    return matches


def find_paths_containing(
    obj: Any,
    fragments: list[str],
    path: str = "",
) -> list[dict[str, Any]]:

    matches = []

    if isinstance(
        obj,
        dict,
    ):

        for key, value in obj.items():

            current_path = (
                f"{path}.{key}"
                if path
                else str(key)
            )

            key_lower = str(key).lower()

            if any(
                fragment.lower()
                in key_lower
                for fragment in fragments
            ):

                matches.append(
                    {
                        "key": str(key),
                        "path": current_path,
                        "value_type": (
                            type(value).__name__
                        ),
                        "value": (
                            value
                            if not isinstance(
                                value,
                                (
                                    dict,
                                    list,
                                ),
                            )
                            else None
                        ),
                    }
                )

            matches.extend(
                find_paths_containing(
                    value,
                    fragments,
                    current_path,
                )
            )

    elif isinstance(
        obj,
        list,
    ):

        for index, value in enumerate(obj):

            current_path = (
                f"{path}[{index}]"
            )

            matches.extend(
                find_paths_containing(
                    value,
                    fragments,
                    current_path,
                )
            )

    return matches


# ============================================================
# Artifact inspection
# ============================================================

def inspect_artifact(
    name: str,
    path: Path,
) -> dict[str, Any]:

    data = load_json(path)

    top_level_keys = [
        str(key)
        for key in data.keys()
    ]

    status_candidates = (
        find_key_paths(
            data,
            {
                "status",
                "operation_status",
                "overall_status",
                "acceptance_status",
                "final_status",
            },
        )
    )

    t4_candidates = (
        find_paths_containing(
            data,
            [
                "t4",
                "assignee",
                "assignment",
                "ranking",
            ],
        )
    )

    control_candidates = (
        find_paths_containing(
            data,
            [
                "control",
                "threshold",
                "probability",
                "confidence",
                "unseen",
                "synthetic",
                "post_creation",
                "locked_test",
            ],
        )
    )

    return {
        "artifact_name": name,
        "path": str(path),
        "top_level_keys": top_level_keys,
        "top_level_key_count": len(
            top_level_keys
        ),
        "schema_summary": summarize_value(
            data,
            max_depth=4,
        ),
        "status_candidates": status_candidates,
        "t4_semantic_candidates": t4_candidates,
        "control_candidates": control_candidates,
    }


# ============================================================
# Main
# ============================================================

def main() -> None:

    print("=" * 72)
    print("T9 MOD-037 OP-011A")
    print("T4 Prior-Artifact Schema Resolution")
    print("=" * 72)
    print()

    artifacts = [
        (
            "OP-004",
            OP004_ARTIFACT,
        ),
        (
            "OP-005",
            OP005_ARTIFACT,
        ),
        (
            "T8 OP-020",
            OP020_ARTIFACT,
        ),
    ]

    inspection_results = []

    for name, path in artifacts:

        print(
            f"Inspecting {name}..."
        )

        result = inspect_artifact(
            name,
            path,
        )

        inspection_results.append(
            result
        )

        print(
            f"  Path: {path}"
        )

        print(
            "  Top-level keys:"
        )

        for key in result[
            "top_level_keys"
        ]:

            print(
                f"    - {key}"
            )

        print(
            f"  Top-level key count: "
            f"{result['top_level_key_count']}"
        )

        print()

    # --------------------------------------------------------
    # Explicit candidate-key discovery
    # --------------------------------------------------------

    combined_text_fragments = [
        "t4",
        "assignee",
        "assignment",
        "ranking",
        "status",
        "control",
        "probability",
        "confidence",
        "threshold",
        "unseen",
        "synthetic",
        "post_creation",
        "locked_test",
    ]

    key_inventory = {}

    for result in inspection_results:

        artifact_name = result[
            "artifact_name"
        ]

        artifact_key_paths = []

        artifact_key_paths.extend(
            result[
                "status_candidates"
            ]
        )

        artifact_key_paths.extend(
            result[
                "t4_semantic_candidates"
            ]
        )

        artifact_key_paths.extend(
            result[
                "control_candidates"
            ]
        )

        # Remove duplicate paths while preserving order.
        seen = set()
        unique_paths = []

        for item in artifact_key_paths:

            path = item["path"]

            if path in seen:
                continue

            seen.add(path)

            unique_paths.append(
                item
            )

        key_inventory[
            artifact_name
        ] = unique_paths

    # --------------------------------------------------------
    # Controls
    # --------------------------------------------------------

    controls = {

        "artifact_read_only": True,

        "model_fitted": False,

        "prediction_generated": False,

        "probability_generated": False,

        "calibration_fitted": False,

        "target_created": False,

        "target_relabelled": False,

        "threshold_selected": False,

        "locked_test_used_for_selection": False,

        "universal_confidence_created": False,

        "universal_risk_score_created": False,

        "existing_artifacts_modified": False,
    }

    control_failures = []

    for key, value in controls.items():

        if key == "artifact_read_only":

            if value is not True:
                control_failures.append(
                    key
                )

        else:

            if value is not False:
                control_failures.append(
                    key
                )

    controls_status = (
        "PASS"
        if not control_failures
        else "FAIL"
    )

    overall_status = (
        "PASS"
        if controls_status == "PASS"
        and len(
            inspection_results
        ) == 3
        else "FAIL"
    )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    output = {

        "operation": (
            "T9_MOD-037_OP-011A"
        ),

        "title": (
            "T4 Prior-Artifact Schema Resolution"
        ),

        "status": overall_status,

        "operation_type": (
            "READ_ONLY_PRIOR_ARTIFACT_SCHEMA_RESOLUTION"
        ),

        "purpose": (
            "Resolve the actual JSON schema of the prior "
            "T9/T8 artifacts required by OP-011 before "
            "writing artifact-dependent validation logic."
        ),

        "artifacts_inspected": (
            inspection_results
        ),

        "candidate_key_inventory": (
            key_inventory
        ),

        "controls": controls,

        "control_failures": (
            control_failures
        ),

        "interpretation_boundary": [

            (
                "This operation only inspects existing "
                "JSON artifacts."
            ),

            (
                "No model fitting or prediction generation "
                "is performed."
            ),

            (
                "No calibration or probability generation "
                "is performed."
            ),

            (
                "No target, threshold, confidence, or risk "
                "construct is created."
            ),

            (
                "The discovered schema must be used to "
                "construct the corrected OP-011 validator."
            ),
        ],

        "next_operation": (
            "Use the resolved artifact schema to construct "
            "the corrected T9 MOD-037 OP-011 T4 native "
            "ranking evaluation and calibration-readiness audit."
        ),
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

    print("=" * 72)
    print("T9 MOD-037 OP-011A RESULT")
    print("=" * 72)
    print()

    print(
        "Artifacts inspected:",
        len(inspection_results),
    )

    print(
        "Control validation:",
        controls_status,
    )

    print()

    for result in inspection_results:

        print(
            f"{result['artifact_name']}: "
            f"{result['top_level_key_count']} "
            f"top-level keys"
        )

    print()

    print(
        "Model fitting: NO"
    )

    print(
        "Prediction generation: NO"
    )

    print(
        "Probability generation: NO"
    )

    print(
        "Calibration fitting: NO"
    )

    print(
        "Target creation: NO"
    )

    print(
        "Threshold selection: NO"
    )

    print(
        "Locked test used: NO"
    )

    print(
        "Existing artifacts modified: NO"
    )

    print()

    print(
        "Output:",
        OUTPUT_JSON,
    )

    print()

    print(
        f"T9 MOD-037 OP-011A schema resolution: "
        f"{overall_status}"
    )


if __name__ == "__main__":
    main()