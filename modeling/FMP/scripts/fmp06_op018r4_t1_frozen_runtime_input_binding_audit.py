from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OUTPUT = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "fmp06_op018r4_t1_frozen_runtime_input_binding_audit.json"
)

T1_ARTIFACT = (
    PROJECT_ROOT
    / "modeling/T1/baselines/"
    "t1_it_support_char_svm.joblib"
)

CANDIDATE_SOURCES = [
    PROJECT_ROOT / "modeling/T1/derived/t1_dataset.csv",
    PROJECT_ROOT / "modeling/T1/derived/t1_vscode_dataset.csv",
    PROJECT_ROOT / "modeling/T1/splits/t1_split.csv",
]


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def safe_type(obj: Any) -> str:
    return (
        f"{type(obj).__module__}."
        f"{type(obj).__name__}"
    )


def inspect_transformer(
    name: str,
    transformer: Any,
) -> dict[str, Any]:

    result: dict[str, Any] = {
        "name": name,
        "type": safe_type(transformer),
        "methods": {
            "transform": callable(
                getattr(
                    transformer,
                    "transform",
                    None,
                )
            ),
            "fit": callable(
                getattr(
                    transformer,
                    "fit",
                    None,
                )
            ),
        },
    }

    # Inspect known text-vectorizer metadata without
    # modifying or transforming anything.
    for attribute in (
        "analyzer",
        "ngram_range",
        "lowercase",
        "strip_accents",
        "token_pattern",
        "binary",
        "use_idf",
        "sublinear_tf",
    ):

        try:
            value = getattr(
                transformer,
                attribute,
            )

            result[attribute] = str(value)

        except Exception:
            pass

    return result


def inspect_feature_union(
    features: Any,
) -> dict[str, Any]:

    result: dict[str, Any] = {
        "type": safe_type(features),
        "transformer_list": [],
    }

    transformer_list = getattr(
        features,
        "transformer_list",
        None,
    )

    if transformer_list is None:
        result["transformer_list_status"] = (
            "NOT_AVAILABLE"
        )
        return result

    for name, transformer in transformer_list:

        result["transformer_list"].append(
            inspect_transformer(
                str(name),
                transformer,
            )
        )

    return result


def inspect_dataframe(
    path: Path,
) -> dict[str, Any]:

    result: dict[str, Any] = {
        "source": rel(path),
        "exists": path.exists(),
    }

    if not path.exists():
        return result

    try:
        df = pd.read_csv(path)

    except Exception as exc:

        result["status"] = "READ_FAILED"
        result["error"] = str(exc)
        return result

    result["status"] = "READ_OK"
    result["rows"] = int(len(df))
    result["columns"] = [
        str(column)
        for column in df.columns
    ]

    result["dtypes"] = {
        str(column): str(dtype)
        for column, dtype in df.dtypes.items()
    }

    result["non_null_counts_head"] = {
        str(column): int(df[column].notna().sum())
        for column in df.columns
    }

    sample_records = []

    for index, row in df.head(3).iterrows():

        record = {
            "row_index": int(index),
        }

        for column in df.columns:

            value = row[column]

            if pd.isna(value):
                record[str(column)] = None
            else:
                text = str(value)

                if len(text) > 300:
                    text = text[:300] + "..."

                record[str(column)] = text

        sample_records.append(record)

    result["sample_rows"] = sample_records

    return result


def main() -> None:

    print("=" * 72)
    print(
        "FMP-06 OP-018R4 — "
        "T1 FROZEN RUNTIME INPUT BINDING AUDIT"
    )
    print("=" * 72)
    print()
    print("Mode: READ-ONLY")
    print("joblib.load(): YES")
    print("Feature transform: NO")
    print("Inference: NO")
    print("Fit: NO")
    print("Artifact modification: NO")
    print()

    report: dict[str, Any] = {
        "operation": "FMP-06 OP-018R4",
        "operation_type": (
            "READ_ONLY_T1_FROZEN_RUNTIME_INPUT_BINDING_AUDIT"
        ),
        "artifact": rel(T1_ARTIFACT),
        "feature_pipeline": {},
        "candidate_sources": [],
        "binding_analysis": {},
        "safeguards": {
            "transform_executed": False,
            "predict_executed": False,
            "fit_executed": False,
            "retraining": False,
            "artifact_modification": False,
        },
    }

    if not T1_ARTIFACT.exists():
        raise FileNotFoundError(
            f"Missing T1 artifact: {T1_ARTIFACT}"
        )

    # Load only for structure inspection.
    bundle = joblib.load(T1_ARTIFACT)

    print(
        "T1 artifact:",
        rel(T1_ARTIFACT),
    )

    print(
        "Bundle type:",
        safe_type(bundle),
    )

    if not isinstance(bundle, dict):
        raise TypeError(
            "T1 frozen artifact is not a dict bundle."
        )

    print(
        "Bundle keys:",
        list(bundle.keys()),
    )

    features = bundle.get("features")

    if features is None:
        raise KeyError(
            "T1 frozen artifact does not contain "
            "'features'."
        )

    print(
        "Feature object:",
        safe_type(features),
    )

    feature_info = inspect_feature_union(
        features
    )

    report["feature_pipeline"] = feature_info

    print()
    print("-" * 72)
    print("FROZEN FEATURE PIPELINE")
    print("-" * 72)

    print(
        "FeatureUnion type:",
        feature_info["type"],
    )

    for transformer in feature_info[
        "transformer_list"
    ]:

        print(
            "Transformer:",
            transformer["name"],
        )

        print(
            "  type:",
            transformer["type"],
        )

        print(
            "  methods:",
            transformer["methods"],
        )

        for key in (
            "analyzer",
            "ngram_range",
            "lowercase",
            "strip_accents",
            "token_pattern",
            "binary",
            "use_idf",
            "sublinear_tf",
        ):

            if key in transformer:
                print(
                    f"  {key}:",
                    transformer[key],
                )

    print()
    print("-" * 72)
    print("CANDIDATE T1 INPUT SOURCES")
    print("-" * 72)

    for path in CANDIDATE_SOURCES:

        info = inspect_dataframe(path)

        report["candidate_sources"].append(info)

        print()
        print(
            "SOURCE:",
            info["source"],
        )

        print(
            "  exists:",
            info["exists"],
        )

        if info.get("status") != "READ_OK":
            print(
                "  status:",
                info.get("status"),
            )
            continue

        print(
            "  rows:",
            info["rows"],
        )

        print(
            "  columns:",
            info["columns"],
        )

        print(
            "  non-null counts:",
            info["non_null_counts_head"],
        )

        print(
            "  sample rows:",
        )

        for row in info["sample_rows"]:
            print(
                "   ",
                row,
            )

    # Infer only from stored structure and source schemas.
    feature_names = []

    for transformer in feature_info[
        "transformer_list"
    ]:
        feature_names.append(
            transformer["name"]
        )

    source_assessments = []

    for source in report[
        "candidate_sources"
    ]:

        if source.get("status") != "READ_OK":
            continue

        columns_lower = {
            column.lower()
            for column in source["columns"]
        }

        has_summary = (
            "summary" in columns_lower
            or "title" in columns_lower
        )

        has_description = (
            "description" in columns_lower
            or "description_clean" in columns_lower
        )

        has_text = (
            "text" in columns_lower
        )

        assessment = {
            "source": source["source"],
            "has_summary": has_summary,
            "has_description": has_description,
            "has_text": has_text,
            "candidate_runtime_representation": (
                "SUMMARY_AND_DESCRIPTION"
                if (
                    has_summary
                    and has_description
                )
                else
                "TEXT_COLUMN"
                if has_text
                else
                "NO_OBVIOUS_TEXT_REPRESENTATION"
            ),
        }

        source_assessments.append(
            assessment
        )

    report["binding_analysis"] = {
        "feature_transformer_names": feature_names,
        "source_assessments": source_assessments,
        "conclusion": (
            "Determine the authoritative existing T1 "
            "input representation from the frozen "
            "FeatureUnion structure and candidate "
            "source schemas before executing T1 "
            "inference."
        ),
    }

    report["overall_status"] = "PASS"

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            report,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 72)
    print("OVERALL STATUS: PASS")
    print("OUTPUT:", OUTPUT)
    print("=" * 72)


if __name__ == "__main__":
    main()