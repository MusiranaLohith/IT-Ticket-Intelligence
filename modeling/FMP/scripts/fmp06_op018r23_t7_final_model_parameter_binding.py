from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T7_ROOT = ROOT / "modeling" / "T7"
METRICS_DIR = T7_ROOT / "metrics"
SCRIPTS_DIR = T7_ROOT / "scripts"

OUTPUT_PATH = (
    ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "fmp06_op018r23_t7_final_model_parameter_binding.json"
)


TARGET_FILES = [
    METRICS_DIR / "t7_mod012_final_closure.json",
    METRICS_DIR / "t7_mod011_final_model_comparison_audit.json",
    METRICS_DIR / "t7_mod010_log_normal_aft_model.json",
]


KEYWORDS = [
    "lognormal",
    "log-normal",
    "aft",
    "coefficient",
    "coefficients",
    "parameter",
    "params",
    "intercept",
    "scale",
    "mu",
    "sigma",
    "feature",
    "features",
    "formula",
    "model",
    "prediction",
    "duration",
    "event",
    "censor",
]


def read_json(path: Path) -> object:
    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


def compact_value(
    value: object,
    depth: int = 0,
) -> object:

    if depth >= 3:
        if isinstance(value, dict):
            return {
                "type": "dict",
                "keys": list(value.keys())[:30],
            }

        if isinstance(value, list):
            return {
                "type": "list",
                "length": len(value),
            }

        return value

    if isinstance(value, dict):

        output = {}

        for key, item in value.items():

            lowered = str(key).lower()

            if any(
                keyword in lowered
                for keyword in KEYWORDS
            ):
                output[str(key)] = compact_value(
                    item,
                    depth + 1,
                )

        return output

    if isinstance(value, list):

        if len(value) <= 10:
            return [
                compact_value(
                    item,
                    depth + 1,
                )
                for item in value
            ]

        return {
            "type": "list",
            "length": len(value),
            "first_items": [
                compact_value(
                    item,
                    depth + 1,
                )
                for item in value[:3]
            ],
        }

    if isinstance(
        value,
        (str, int, float, bool),
    ) or value is None:

        return value

    return str(value)


def find_keyword_paths(
    value: object,
    path: str = "$",
) -> list[str]:

    matches = []

    if isinstance(value, dict):

        for key, item in value.items():

            current = (
                f"{path}.{key}"
            )

            if any(
                keyword in str(key).lower()
                for keyword in KEYWORDS
            ):
                matches.append(
                    current
                )

            matches.extend(
                find_keyword_paths(
                    item,
                    current,
                )
            )

    elif isinstance(value, list):

        for index, item in enumerate(value):

            matches.extend(
                find_keyword_paths(
                    item,
                    f"{path}[{index}]",
                )
            )

    return matches


def source_model_signals() -> dict:

    signals = {}

    for path in sorted(
        SCRIPTS_DIR.glob("*.py")
    ):

        text = path.read_text(
            encoding="utf-8",
            errors="replace",
        ).lower()

        if (
            "lognormal" not in text
            and "log-normal" not in text
            and "aft" not in text
        ):
            continue

        signals[str(path.relative_to(ROOT))] = {
            "predict_survival_function": (
                "predict_survival_function"
                in text
            ),
            "predict_expectation": (
                "predict_expectation"
                in text
            ),
            "predict_median": (
                "predict_median"
                in text
            ),
            "coefficients": (
                "coef_" in text
                or "params_" in text
                or "coefficient" in text
            ),
            "formula": (
                "formula" in text
            ),
            "fit": (
                ".fit(" in text
            ),
        }

    return signals


def main() -> None:

    print("=" * 72)
    print(
        "FMP-06 OP-018R23 — "
        "T7 FINAL MODEL PARAMETER BINDING"
    )
    print("=" * 72)

    print()
    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation metrics: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    report = {
        "operation": "FMP-06 OP-018R23",
        "status": "PASS",
        "read_only": True,
        "training": False,
        "fitting": False,
        "prediction": False,
        "evaluation": False,
        "locked_test": False,
        "artifact_modification": False,
        "files": {},
    }

    print()
    print("[1] Inspecting final T7 model evidence...")

    for path in TARGET_FILES:

        print()
        print(
            f"  FILE: {path.relative_to(ROOT)}"
        )

        if not path.exists():

            print("    MISSING")

            report["files"][
                str(path.relative_to(ROOT))
            ] = {
                "exists": False,
            }

            continue

        data = read_json(path)

        keyword_paths = find_keyword_paths(
            data
        )

        compact = compact_value(
            data
        )

        print(
            f"    Top-level type: "
            f"{type(data).__name__}"
        )

        if isinstance(data, dict):

            print(
                f"    Top-level keys: "
                f"{list(data.keys())}"
            )

        print(
            f"    Relevant JSON paths: "
            f"{len(keyword_paths)}"
        )

        for item in keyword_paths[:40]:

            print(
                f"      {item}"
            )

        report["files"][
            str(path.relative_to(ROOT))
        ] = {
            "exists": True,
            "size_bytes": path.stat().st_size,
            "top_level_type": type(data).__name__,
            "top_level_keys": (
                list(data.keys())
                if isinstance(data, dict)
                else []
            ),
            "relevant_paths": keyword_paths,
            "compact_relevant_content": compact,
        }

    print()
    print(
        "[2] Inspecting Log-Normal AFT source interfaces..."
    )

    signals = source_model_signals()

    for path, values in signals.items():

        active = [
            key
            for key, value in values.items()
            if value
        ]

        print(
            f"  {path}"
        )

        print(
            "    active: "
            + (
                ", ".join(active)
                if active
                else "none"
            )
        )

    report["source_model_signals"] = signals

    print()
    print(
        "[3] Parameter/runtime binding summary..."
    )

    all_content = json.dumps(
        report,
        ensure_ascii=False,
    ).lower()

    summary = {
        "lognormal_evidence": (
            "lognormal" in all_content
            or "log-normal" in all_content
        ),
        "aft_evidence": (
            "aft" in all_content
        ),
        "coefficient_evidence": (
            "coefficient" in all_content
            or "coef_" in all_content
            or "params_" in all_content
        ),
        "feature_evidence": (
            "feature" in all_content
        ),
        "prediction_interface_evidence": (
            "predict_survival_function"
            in all_content
            or "predict_expectation"
            in all_content
            or "predict_median"
            in all_content
        ),
        "parameter_artifact_candidate": (
            "parameter" in all_content
            or "coefficient" in all_content
            or "coef_" in all_content
            or "params_" in all_content
        ),
    }

    report["binding_summary"] = summary

    for key, value in summary.items():

        print(
            f"  {key}: "
            f"{value}"
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 72)
    print(
        "OP-018R23 INSPECTION COMPLETE"
    )
    print("=" * 72)

    print(
        f"Output: {OUTPUT_PATH}"
    )

    print()
    print("No training performed.")
    print("No fitting performed.")
    print("No prediction performed.")
    print("No evaluation performed.")
    print("No locked test used.")
    print("No artifact modification performed.")

    print("=" * 72)


if __name__ == "__main__":
    main()