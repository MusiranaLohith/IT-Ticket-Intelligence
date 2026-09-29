from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


# ============================================================
# T9 MOD-037 OP-013C
# T7 FULL EVIDENCE SCAN & EVALUATION-SCOPE RECONCILIATION
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T7_ROOT = PROJECT_ROOT / "modeling" / "T7"
T9_ROOT = PROJECT_ROOT / "modeling" / "T9"
OUTPUT_DIR = T9_ROOT / "mod037"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_JSON = (
    OUTPUT_DIR
    / "t9_mod037_op013c_t7_full_evidence_scan.json"
)


# ============================================================
# PRIOR T9 ARTIFACTS
# ============================================================

OP004 = (
    OUTPUT_DIR
    / "t9_mod037_op004_native_output_acceptance.json"
)

OP005 = (
    OUTPUT_DIR
    / "t9_mod037_op005_output_semantics_lock.json"
)

OP013A = (
    OUTPUT_DIR
    / "t9_mod037_op013a_t7_prior_artifact_schema.json"
)

OP013B = (
    OUTPUT_DIR
    / "t9_mod037_op013b_t7_survival_semantics_audit.json"
)


# ============================================================
# HIGH-VALUE T7 EVIDENCE
# ============================================================

HIGH_VALUE_FILES = [

    "contracts/t7_modeling_contract.json",

    "splits/t7_train.csv",
    "splits/t7_evaluation.csv",

    "metrics/t7_mod006_survival_baseline_audit.json",

    "metrics/t7_mod007_predictive_survival_audit.json",

    "metrics/t7_mod008_predictive_vs_reference.csv",

    "metrics/t7_mod008_predictive_vs_reference_audit.json",

    "metrics/t7_mod009_survival_calibration.csv",

    "metrics/t7_mod009_survival_calibration_audit.json",

    "metrics/t7_mod012_final_closure.json",

    "derived/t7_mod006_kaplan_meier_curve.csv",

    "derived/t7_mod007_evaluation_predictions.csv",

    "derived/t7_mod010_evaluation_predictions.csv",

    "baselines/t7_kaplan_meier_baseline.csv",

    "baselines/t7_nelson_aalen_baseline.csv",
]


# ============================================================
# SEARCH TERMS
# ============================================================

SURVIVAL_TERMS = [
    "survival",
    "censor",
    "event",
    "duration",
    "hazard",
    "kaplan",
    "nelson",
    "brier",
    "concordance",
    "c-index",
    "calibration",
    "reliability",
    "median",
    "time-to-event",
    "time_to_event",
]

METHODOLOGY_TERMS = [
    "brier",
    "c-index",
    "concordance",
    "kaplan",
    "nelson",
    "calibration",
    "reliability",
    "integrated",
    "survival",
    "censor",
    "bootstrap",
    "confidence interval",
    "evaluation",
    "baseline",
    "reference",
]

PREDICTION_TERMS = [
    "predicted",
    "prediction",
    "median_survival",
    "survival_probability",
    "duration_seconds",
    "event",
]


# ============================================================
# HELPERS
# ============================================================

def load_json(
    path: Path,
) -> Any:

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


def compact_value(
    value: Any,
    max_chars: int = 500,
) -> Any:

    if (
        isinstance(
            value,
            (
                str,
                int,
                float,
                bool,
            ),
        )
        or value is None
    ):

        text = str(value)

        if len(text) <= max_chars:
            return value

        return (
            text[:max_chars]
            + "...<truncated>"
        )

    if isinstance(
        value,
        list,
    ):

        if len(value) <= 15:

            return [
                compact_value(
                    item,
                    max_chars,
                )
                for item in value
            ]

        return {
            "type": "list",
            "length": len(value),
            "first_items": [
                compact_value(
                    item,
                    max_chars,
                )
                for item in value[:10]
            ],
        }

    if isinstance(
        value,
        dict,
    ):

        return {
            str(key): compact_value(
                item,
                max_chars,
            )
            for key, item in list(
                value.items()
            )[:30]
        }

    return str(value)[
        :max_chars
    ]


def json_structure(
    value: Any,
    depth: int = 0,
    max_depth: int = 3,
) -> Any:

    if depth > max_depth:

        return {
            "type": type(value).__name__
        }

    if isinstance(
        value,
        dict,
    ):

        return {
            "type": "dict",
            "keys": list(
                value.keys()
            ),
            "children": {
                str(key): json_structure(
                    child,
                    depth + 1,
                    max_depth,
                )
                for key, child in list(
                    value.items()
                )[:40]
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
                "first_item_structure"
            ] = json_structure(
                value[0],
                depth + 1,
                max_depth,
            )

        return result

    return {
        "type": type(value).__name__,
        "value": compact_value(
            value,
            250,
        ),
    }


def recursive_text_hits(
    value: Any,
    path: str = "",
) -> list[dict[str, str]]:

    hits = []

    if isinstance(
        value,
        dict,
    ):

        for key, child in value.items():

            child_path = (
                f"{path}.{key}"
                if path
                else str(key)
            )

            hits.extend(
                recursive_text_hits(
                    child,
                    child_path,
                )
            )

    elif isinstance(
        value,
        list,
    ):

        for index, child in enumerate(
            value[:100]
        ):

            child_path = (
                f"{path}[{index}]"
            )

            hits.extend(
                recursive_text_hits(
                    child,
                    child_path,
                )
            )

    elif isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ):

        text = str(value).lower()

        matched = []

        for term in SURVIVAL_TERMS:

            if term.lower() in text:

                matched.append(
                    term
                )

        if matched:

            hits.append(
                {
                    "path": path,
                    "value": str(value)[:500],
                    "matched_terms": ",".join(
                        sorted(
                            set(matched)
                        )
                    ),
                }
            )

    return hits


def read_csv_header(
    path: Path,
) -> dict[str, Any]:

    result = {
        "path": str(path),
        "exists": path.exists(),
    }

    if not path.exists():
        return result

    result[
        "size_bytes"
    ] = path.stat().st_size

    try:

        with open(
            path,
            "r",
            encoding="utf-8",
            errors="replace",
            newline="",
        ) as f:

            reader = csv.reader(f)

            header = next(
                reader,
                [],
            )

            sample_rows = []

            for _, row in zip(
                range(3),
                reader,
            ):

                sample_rows.append(
                    row
                )

        result[
            "columns"
        ] = header

        result[
            "column_count"
        ] = len(header)

        result[
            "sample_row_lengths"
        ] = [
            len(row)
            for row in sample_rows
        ]

        result[
            "sample_rows"
        ] = [
            row[:20]
            for row in sample_rows
        ]

        survival_columns = []

        for column in header:

            lower = column.lower()

            if any(
                term in lower
                for term in (
                    SURVIVAL_TERMS
                    + PREDICTION_TERMS
                )
            ):

                survival_columns.append(
                    column
                )

        result[
            "survival_related_columns"
        ] = survival_columns

        result[
            "status"
        ] = "PASS"

    except Exception as exc:

        result[
            "status"
        ] = "FAIL"

        result[
            "error"
        ] = repr(exc)

    return result


def read_json_evidence(
    path: Path,
) -> dict[str, Any]:

    result = {
        "path": str(path),
        "exists": path.exists(),
    }

    if not path.exists():
        return result

    result[
        "size_bytes"
    ] = path.stat().st_size

    try:

        value = load_json(
            path
        )

        result[
            "top_level_type"
        ] = type(
            value
        ).__name__

        if isinstance(
            value,
            dict,
        ):

            result[
                "top_level_keys"
            ] = list(
                value.keys()
            )

        result[
            "structure"
        ] = json_structure(
            value
        )

        result[
            "survival_term_hits"
        ] = recursive_text_hits(
            value
        )

        result[
            "status"
        ] = "PASS"

    except Exception as exc:

        result[
            "status"
        ] = "FAIL"

        result[
            "error"
        ] = repr(exc)

    return result


def inspect_text_file(
    path: Path,
) -> dict[str, Any]:

    result = {
        "path": str(path),
        "exists": path.exists(),
    }

    if not path.exists():
        return result

    result[
        "size_bytes"
    ] = path.stat().st_size

    try:

        text = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        lower = text.lower()

        matched_terms = []

        for term in METHODOLOGY_TERMS:

            if term.lower() in lower:

                matched_terms.append(
                    term
                )

        result[
            "line_count"
        ] = (
            text.count("\n")
            + 1
        )

        result[
            "matched_methodology_terms"
        ] = sorted(
            set(
                matched_terms
            )
        )

        evidence_lines = []

        for number, line in enumerate(
            text.splitlines(),
            start=1,
        ):

            line_lower = line.lower()

            if any(
                term.lower()
                in line_lower
                for term in METHODOLOGY_TERMS
            ):

                evidence_lines.append(
                    {
                        "line": number,
                        "text": line[:500],
                    }
                )

            if len(
                evidence_lines
            ) >= 80:

                break

        result[
            "methodology_evidence_lines"
        ] = evidence_lines

        result[
            "status"
        ] = "PASS"

    except Exception as exc:

        result[
            "status"
        ] = "FAIL"

        result[
            "error"
        ] = repr(exc)

    return result


def inspect_tree(
    root: Path,
) -> dict[str, Any]:

    files = []

    for path in sorted(
        root.rglob("*")
    ):

        if not path.is_file():
            continue

        relative = path.relative_to(
            root
        )

        suffix = path.suffix.lower()

        files.append(
            {
                "relative_path": str(
                    relative
                ),
                "suffix": suffix,
                "size_bytes": path.stat().st_size,
            }
        )

    by_suffix = {}

    for item in files:

        suffix = (
            item["suffix"]
            or "<none>"
        )

        by_suffix[
            suffix
        ] = (
            by_suffix.get(
                suffix,
                0,
            )
            + 1
        )

    return {
        "root": str(root),
        "file_count": len(files),
        "by_suffix": by_suffix,
        "files": files,
    }


def compare_prediction_headers(
    path_a: Path,
    path_b: Path,
) -> dict[str, Any]:

    a = read_csv_header(
        path_a
    )

    b = read_csv_header(
        path_b
    )

    columns_a = a.get(
        "columns",
        [],
    )

    columns_b = b.get(
        "columns",
        [],
    )

    return {

        "A": str(path_a),

        "B": str(path_b),

        "A_columns": columns_a,

        "B_columns": columns_b,

        "same_columns": (
            columns_a
            == columns_b
        ),

        "A_only_columns": [
            column
            for column in columns_a
            if column not in columns_b
        ],

        "B_only_columns": [
            column
            for column in columns_b
            if column not in columns_a
        ],
    }


# ============================================================
# PRIOR OPERATION AUDIT
# ============================================================

def audit_prior_operations() -> dict[str, Any]:

    # --------------------------------------------------------
    # OP-004 IS SPECIAL
    #
    # OP-004 overall status may be FAIL because another
    # task (T2) was rejected. For T7 continuation, the
    # authoritative task-level field is accepted_tasks.
    # --------------------------------------------------------

    if not OP004.exists():

        return {
            "status": "FAIL",
            "failed": ["OP-004"],
            "reason": "OP-004 artifact missing.",
        }

    op004 = load_json(
        OP004
    )

    accepted_tasks = op004.get(
        "accepted_tasks",
        [],
    )

    op004_t7_accepted = (
        "T7"
        in accepted_tasks
    )

    op004_check = (
        "PASS"
        if op004_t7_accepted
        else "FAIL"
    )

    # --------------------------------------------------------
    # OP-005 / OP-013A / OP-013B
    # These operations are T7-chain operations and must
    # have overall PASS status.
    # --------------------------------------------------------

    required_pass_artifacts = {
        "OP-005": OP005,
        "OP-013A": OP013A,
        "OP-013B": OP013B,
    }

    checks = {
        "OP-004_T7_task_acceptance": (
            op004_check
        )
    }

    details = {

        "OP-004": {

            "overall_status": op004.get(
                "status"
            ),

            "accepted_tasks": accepted_tasks,

            "T7_accepted": (
                op004_t7_accepted
            ),

            "validation_basis": (
                "Task-level T7 acceptance; "
                "OP-004 overall PASS is not required "
                "because OP-004 contains unrelated "
                "task rejection."
            ),
        }
    }

    for name, path in (
        required_pass_artifacts.items()
    ):

        if not path.exists():

            checks[
                name
            ] = "FAIL"

            details[
                name
            ] = {
                "status": "MISSING",
                "path": str(path),
            }

            continue

        try:

            data = load_json(
                path
            )

            status = data.get(
                "status"
            )

            checks[
                name
            ] = (
                "PASS"
                if status == "PASS"
                else "FAIL"
            )

            details[
                name
            ] = {
                "status": status,
                "path": str(path),
            }

        except Exception as exc:

            checks[
                name
            ] = "FAIL"

            details[
                name
            ] = {
                "error": repr(exc),
                "path": str(path),
            }

    failed = [
        name
        for name, status in checks.items()
        if status != "PASS"
    ]

    return {

        "status": (
            "PASS"
            if not failed
            else "FAIL"
        ),

        "checks": checks,

        "failed": failed,

        "details": details,
    }


# ============================================================
# HIGH-VALUE FILE SCAN
# ============================================================

def scan_high_value_files() -> dict[str, Any]:

    results = {}

    for relative in HIGH_VALUE_FILES:

        path = T7_ROOT / relative

        if not path.exists():

            results[
                relative
            ] = {
                "path": str(path),
                "exists": False,
                "status": "MISSING",
            }

            continue

        suffix = path.suffix.lower()

        if suffix == ".json":

            results[
                relative
            ] = read_json_evidence(
                path
            )

        elif suffix == ".csv":

            results[
                relative
            ] = read_csv_header(
                path
            )

        else:

            results[
                relative
            ] = inspect_text_file(
                path
            )

    return results


# ============================================================
# T7 SCRIPT / CODE INVENTORY
# ============================================================

def scan_t7_scripts() -> list[dict[str, Any]]:

    results = []

    for path in sorted(
        T7_ROOT.rglob("*.py")
    ):

        results.append(
            inspect_text_file(
                path
            )
        )

    return results


# ============================================================
# RELEVANT FILE DISCOVERY
# ============================================================

def discover_relevant_files() -> list[dict[str, Any]]:

    results = []

    relevant_terms = [
        "survival",
        "calibration",
        "evaluation",
        "prediction",
        "baseline",
        "closure",
        "reference",
        "audit",
        "kaplan",
        "nelson",
    ]

    for path in sorted(
        T7_ROOT.rglob("*")
    ):

        if not path.is_file():
            continue

        name = path.name.lower()

        if any(
            term in name
            for term in relevant_terms
        ):

            results.append(
                {
                    "relative_path": str(
                        path.relative_to(
                            T7_ROOT
                        )
                    ),
                    "size_bytes": path.stat().st_size,
                    "suffix": path.suffix.lower(),
                }
            )

    return results


# ============================================================
# RECONCILIATION
# ============================================================

def build_reconciliation(
    tree: dict[str, Any],
    high_value: dict[str, Any],
    scripts: list[dict[str, Any]],
    discovered: list[dict[str, Any]],
) -> dict[str, Any]:

    existing_high_value = [
        key
        for key, value in high_value.items()
        if value.get(
            "exists",
            False,
        )
    ]

    missing_high_value = [
        key
        for key, value in high_value.items()
        if not value.get(
            "exists",
            False,
        )
    ]

    methodology_terms = set()

    for result in scripts:

        for term in result.get(
            "matched_methodology_terms",
            [],
        ):

            methodology_terms.add(
                term
            )

    for result in high_value.values():

        for hit in result.get(
            "survival_term_hits",
            [],
        ):

            for term in hit.get(
                "matched_terms",
                "",
            ).split(","):

                if term:

                    methodology_terms.add(
                        term
                    )

    return {

        "T7_total_files": tree[
            "file_count"
        ],

        "T7_file_types": tree[
            "by_suffix"
        ],

        "high_value_existing": (
            existing_high_value
        ),

        "high_value_missing": (
            missing_high_value
        ),

        "relevant_files_discovered": len(
            discovered
        ),

        "T7_scripts_scanned": len(
            scripts
        ),

        "methodology_terms_found": sorted(
            methodology_terms
        ),

        "evaluation_scope_status": (
            "REQUIRES_EVALUATION_DESIGN"
        ),

        "reason": (
            "The scan inventories existing T7 evidence "
            "and methodology without performing new "
            "model fitting, calibration fitting, or "
            "model selection."
        ),

        "next_scope_question": (
            "Determine exactly which native survival "
            "metrics, fixed-horizon outputs, calibration "
            "evidence, and reliability evidence remain "
            "unresolved after reconciliation."
        ),
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 72)
    print(
        "T9 MOD-037 OP-013C"
    )
    print(
        "T7 FULL EVIDENCE SCAN & "
        "EVALUATION-SCOPE RECONCILIATION"
    )
    print("=" * 72)
    print()

    # --------------------------------------------------------
    # PRIOR OPERATIONS
    # --------------------------------------------------------

    print(
        "Checking prior T9 operations..."
    )

    prior = audit_prior_operations()

    print(
        "Prior-operation validation:",
        prior[
            "status"
        ],
    )

    if prior[
        "status"
    ] != "PASS":

        print(
            "Failed:",
            prior[
                "failed"
            ],
        )

        raise RuntimeError(
            "Prior T9 operation validation failed."
        )

    print()

    print(
        "OP-004 overall status:",
        prior[
            "details"
        ][
            "OP-004"
        ][
            "overall_status"
        ],
    )

    print(
        "OP-004 T7 task acceptance:",
        prior[
            "details"
        ][
            "OP-004"
        ][
            "T7_accepted"
        ],
    )

    print()

    # --------------------------------------------------------
    # T7 TREE
    # --------------------------------------------------------

    print(
        "Scanning T7 filesystem..."
    )

    tree = inspect_tree(
        T7_ROOT
    )

    print(
        "T7 files discovered:",
        tree[
            "file_count"
        ],
    )

    print(
        "File types:",
        tree[
            "by_suffix"
        ],
    )

    print()

    # --------------------------------------------------------
    # HIGH-VALUE EVIDENCE
    # --------------------------------------------------------

    print(
        "Scanning high-value T7 evidence..."
    )

    high_value = scan_high_value_files()

    existing = sum(
        1
        for result in high_value.values()
        if result.get(
            "exists",
            False,
        )
    )

    print(
        "High-value files present:",
        f"{existing}/{len(HIGH_VALUE_FILES)}",
    )

    for relative, result in high_value.items():

        print(
            f"  {relative}: "
            f"{result.get('status', 'UNKNOWN')}"
        )

    print()

    # --------------------------------------------------------
    # RELEVANT DISCOVERY
    # --------------------------------------------------------

    print(
        "Discovering additional relevant evidence..."
    )

    discovered = (
        discover_relevant_files()
    )

    print(
        "Relevant files discovered:",
        len(
            discovered
        ),
    )

    print()

    # --------------------------------------------------------
    # PYTHON SCRIPTS
    # --------------------------------------------------------

    print(
        "Scanning T7 scripts for methodology evidence..."
    )

    scripts = scan_t7_scripts()

    print(
        "T7 Python scripts scanned:",
        len(
            scripts
        ),
    )

    print()

    # --------------------------------------------------------
    # MOD-007 / MOD-010 SCHEMA
    # --------------------------------------------------------

    mod007 = (
        T7_ROOT
        / "derived"
        / "t7_mod007_evaluation_predictions.csv"
    )

    mod010 = (
        T7_ROOT
        / "derived"
        / "t7_mod010_evaluation_predictions.csv"
    )

    print(
        "Comparing MOD-007 and MOD-010 schemas..."
    )

    prediction_comparison = (
        compare_prediction_headers(
            mod007,
            mod010,
        )
    )

    print(
        "Same prediction columns:",
        prediction_comparison[
            "same_columns"
        ],
    )

    if prediction_comparison[
        "A_only_columns"
    ]:

        print(
            "MOD-007-only columns:",
            prediction_comparison[
                "A_only_columns"
            ],
        )

    if prediction_comparison[
        "B_only_columns"
    ]:

        print(
            "MOD-010-only columns:",
            prediction_comparison[
                "B_only_columns"
            ],
        )

    print()

    # --------------------------------------------------------
    # RECONCILIATION
    # --------------------------------------------------------

    reconciliation = build_reconciliation(
        tree,
        high_value,
        scripts,
        discovered,
    )

    print(
        "Evaluation-scope status:",
        reconciliation[
            "evaluation_scope_status"
        ],
    )

    print(
        "Methodology terms found:",
        reconciliation[
            "methodology_terms_found"
        ],
    )

    print()

    # --------------------------------------------------------
    # CONTROLS
    # --------------------------------------------------------

    controls = {

        "filesystem_scan_read_only": True,

        "model_fitted": False,

        "prediction_generated": False,

        "calibration_fitted": False,

        "target_created": False,

        "target_relabelled": False,

        "censoring_relabelled": False,

        "survival_to_binary_conversion": False,

        "threshold_selected": False,

        "model_selected": False,

        "locked_test_used": False,

        "universal_confidence_created": False,

        "universal_risk_score_created": False,

        "existing_t7_artifacts_modified": False,

        "post_creation_information_used": False,

        "native_survival_semantics_preserved": True,
    }

    allowed_true = {
        "filesystem_scan_read_only",
        "native_survival_semantics_preserved",
    }

    control_failures = []

    for key, value in controls.items():

        if key in allowed_true:

            if value is not True:

                control_failures.append(
                    key
                )

        elif value is not False:

            control_failures.append(
                key
            )

    control_status = (
        "PASS"
        if not control_failures
        else "FAIL"
    )

    print(
        "Control validation:",
        control_status,
    )

    if control_status != "PASS":

        raise RuntimeError(
            "Control validation failed."
        )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    output = {

        "operation": (
            "T9_MOD-037_OP-013C"
        ),

        "title": (
            "T7 Full Evidence Scan & "
            "Evaluation-Scope Reconciliation"
        ),

        "status": "PASS",

        "purpose": (
            "Perform a fast, read-only, comprehensive "
            "inventory and reconciliation of existing "
            "T7 survival evidence before defining the "
            "next native survival evaluation operation."
        ),

        "prior_operation_validation": prior,

        "t7_filesystem_inventory": tree,

        "high_value_evidence": high_value,

        "relevant_file_discovery": discovered,

        "t7_script_methodology_scan": scripts,

        "mod007_mod010_schema_comparison": (
            prediction_comparison
        ),

        "evaluation_scope_reconciliation": (
            reconciliation
        ),

        "controls": controls,

        "control_validation": {

            "status": control_status,

            "failed_controls": control_failures,
        },

        "interpretation": {

            "native_survival_semantics": (
                "Preserved from OP-013B."
            ),

            "full_evidence_scan": (
                "Completed."
            ),

            "new_model_evaluation": (
                "Not performed."
            ),

            "new_calibration": (
                "Not performed."
            ),

            "model_selection": (
                "Not performed."
            ),

            "OP-004_continuation_rule": (
                "T7 continuation is validated from "
                "OP-004.accepted_tasks rather than "
                "OP-004 overall status because OP-004 "
                "contains task-specific rejection "
                "outside the T7 boundary."
            ),

            "next_operation": (
                "Define the exact native T7 survival "
                "evaluation from the reconciled evidence."
            ),
        },

        "artifacts_generated": [
            str(
                OUTPUT_JSON
            )
        ],
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

    print()
    print(
        "Output:",
        OUTPUT_JSON,
    )

    print()
    print(
        "T9 MOD-037 OP-013C: PASS"
    )


if __name__ == "__main__":
    main()