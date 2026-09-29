from pathlib import Path
import csv
import json

import numpy as np


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T7_OOF = ROOT / "modeling/T8/t8_mod029_t7_oof.csv"

T7_EVAL = ROOT / "modeling/T7/derived/t7_mod007_evaluation_predictions.csv"

OUT_DIR = ROOT / "modeling/T8/mod036/op022"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REPORT = OUT_DIR / "t8_mod036_op022_t7_output_resolution.json"


def normalize(name):
    return (
        str(name)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def resolve_column(columns, candidates, required=True):
    normalized = {
        normalize(col): col
        for col in columns
    }

    for candidate in candidates:
        key = normalize(candidate)
        if key in normalized:
            return normalized[key]

    if required:
        raise RuntimeError(
            f"Could not resolve required field.\n"
            f"Candidates: {candidates}\n"
            f"Available columns: {list(columns)}"
        )

    return None


def inspect_csv(path):
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline="",
    ) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        columns = reader.fieldnames or []

    return columns, rows


def classify_column(name):
    n = normalize(name)

    if any(
        token in n
        for token in (
            "id",
            "ticket",
            "bug",
        )
    ):
        return "identifier"

    if any(
        token in n
        for token in (
            "time",
            "date",
            "duration",
            "survival",
            "event",
            "censor",
            "status",
            "resolved",
            "prediction",
            "risk",
            "hazard",
            "prob",
            "score",
        )
    ):
        return "resolution_related"

    return "other"


def main():

    print("=" * 80)
    print("T8 DECISION ENGINE — MOD-036 OP-022")
    print("T7 Native Resolution Output Resolution")
    print("=" * 80)

    # ------------------------------------------------------------------
    # 1. Inspect T7 OOF artifact
    # ------------------------------------------------------------------

    print("\nT7 OOF source")
    print("-" * 80)
    print(f"  path: {T7_OOF}")

    oof_columns, oof_rows = inspect_csv(T7_OOF)

    print(f"  rows: {len(oof_rows)}")
    print(f"  columns: {len(oof_columns)}")

    print("\n  available columns:")
    for column in oof_columns:
        print(
            f"    - {column}"
        )

    # ------------------------------------------------------------------
    # 2. Inspect T7 evaluation artifact
    # ------------------------------------------------------------------

    print("\nT7 evaluation source")
    print("-" * 80)
    print(f"  path: {T7_EVAL}")

    eval_columns, eval_rows = inspect_csv(T7_EVAL)

    print(f"  rows: {len(eval_rows)}")
    print(f"  columns: {len(eval_columns)}")

    print("\n  available columns:")
    for column in eval_columns:
        print(
            f"    - {column}"
        )

    # ------------------------------------------------------------------
    # 3. Resolve identifiers where possible
    # ------------------------------------------------------------------

    oof_id = resolve_column(
        oof_columns,
        (
            "ID",
            "id",
            "ticket_id",
            "bug_id",
        ),
    )

    eval_id = resolve_column(
        eval_columns,
        (
            "ID",
            "id",
            "ticket_id",
            "bug_id",
        ),
    )

    print("\nResolved identifiers")
    print("-" * 80)
    print(f"  T7 OOF ID:  {oof_id}")
    print(f"  T7 eval ID: {eval_id}")

    # ------------------------------------------------------------------
    # 4. Basic population integrity
    # ------------------------------------------------------------------

    oof_ids = [
        str(row[oof_id]).strip()
        for row in oof_rows
    ]

    eval_ids = [
        str(row[eval_id]).strip()
        for row in eval_rows
    ]

    oof_unique = len(set(oof_ids))
    eval_unique = len(set(eval_ids))

    print("\nPopulation integrity")
    print("-" * 80)
    print(f"  OOF rows:          {len(oof_ids)}")
    print(f"  OOF unique IDs:    {oof_unique}")
    print(
        f"  OOF duplicate IDs: "
        f"{len(oof_ids) - oof_unique}"
    )

    print(f"  Eval rows:         {len(eval_ids)}")
    print(f"  Eval unique IDs:   {eval_unique}")
    print(
        f"  Eval duplicate IDs: "
        f"{len(eval_ids) - eval_unique}"
    )

    if len(oof_ids) != oof_unique:
        raise RuntimeError(
            "Duplicate IDs detected in T7 OOF artifact."
        )

    if len(eval_ids) != eval_unique:
        raise RuntimeError(
            "Duplicate IDs detected in T7 evaluation artifact."
        )

    # ------------------------------------------------------------------
    # 5. Identify resolution-related fields
    # ------------------------------------------------------------------

    oof_classification = {
        column: classify_column(column)
        for column in oof_columns
    }

    eval_classification = {
        column: classify_column(column)
        for column in eval_columns
    }

    print("\nT7 OOF field classification")
    print("-" * 80)

    for column, category in oof_classification.items():
        print(
            f"  {column:<40} {category}"
        )

    print("\nT7 evaluation field classification")
    print("-" * 80)

    for column, category in eval_classification.items():
        print(
            f"  {column:<40} {category}"
        )

    # ------------------------------------------------------------------
    # 6. Search for explicit event / duration semantics
    # ------------------------------------------------------------------

    event_candidates = [
        column
        for column in oof_columns
        if any(
            token in normalize(column)
            for token in (
                "event",
                "resolved",
                "status",
            )
        )
    ]

    duration_candidates = [
        column
        for column in oof_columns
        if any(
            token in normalize(column)
            for token in (
                "duration",
                "time_to",
                "survival",
                "days",
                "hours",
            )
        )
    ]

    prediction_candidates = [
        column
        for column in oof_columns
        if any(
            token in normalize(column)
            for token in (
                "prediction",
                "risk",
                "hazard",
                "survival",
                "prob",
                "score",
            )
        )
    ]

    print("\nCandidate T7 semantic fields")
    print("-" * 80)

    print(
        f"  event/status candidates: "
        f"{event_candidates}"
    )

    print(
        f"  duration/survival candidates: "
        f"{duration_candidates}"
    )

    print(
        f"  prediction candidates: "
        f"{prediction_candidates}"
    )

    # ------------------------------------------------------------------
    # 7. Inspect sample values for candidate fields
    # ------------------------------------------------------------------

    candidate_fields = list(
        dict.fromkeys(
            event_candidates
            + duration_candidates
            + prediction_candidates
        )
    )

    print("\nCandidate field samples")
    print("-" * 80)

    for column in candidate_fields:

        values = []

        for row in oof_rows[:5]:
            values.append(
                row.get(column)
            )

        print(
            f"\n  {column}"
        )

        for value in values:
            print(
                f"    {value!r}"
            )

    # ------------------------------------------------------------------
    # 8. Check whether OOF and evaluation expose comparable schemas
    # ------------------------------------------------------------------

    oof_normalized = {
        normalize(column): column
        for column in oof_columns
    }

    eval_normalized = {
        normalize(column): column
        for column in eval_columns
    }

    common_normalized = sorted(
        set(oof_normalized)
        & set(eval_normalized)
    )

    common_columns = [
        (
            oof_normalized[name],
            eval_normalized[name],
        )
        for name in common_normalized
    ]

    print("\nOOF / evaluation schema overlap")
    print("-" * 80)
    print(
        f"  common normalized fields: "
        f"{len(common_columns)}"
    )

    for oof_column, eval_column in common_columns:
        print(
            f"  OOF: {oof_column:<35} "
            f"Eval: {eval_column}"
        )

    # ------------------------------------------------------------------
    # 9. Save resolution report
    # ------------------------------------------------------------------

    report = {
        "operation": "MOD-036 OP-022",
        "operation_name": (
            "T7 Native Resolution Output Resolution"
        ),
        "status": "PASS",

        "sources": {
            "t7_oof": str(
                T7_OOF.relative_to(ROOT)
            ),
            "t7_evaluation": str(
                T7_EVAL.relative_to(ROOT)
            ),
        },

        "population": {
            "oof_rows": len(oof_rows),
            "oof_unique_ids": oof_unique,
            "oof_duplicate_ids": (
                len(oof_ids) - oof_unique
            ),
            "evaluation_rows": len(eval_rows),
            "evaluation_unique_ids": eval_unique,
            "evaluation_duplicate_ids": (
                len(eval_ids) - eval_unique
            ),
        },

        "resolved_fields": {
            "oof_id": oof_id,
            "evaluation_id": eval_id,
        },

        "schemas": {
            "oof_columns": oof_columns,
            "evaluation_columns": eval_columns,
            "common_columns": [
                {
                    "oof": oof_column,
                    "evaluation": eval_column,
                }
                for oof_column, eval_column
                in common_columns
            ],
        },

        "candidate_semantic_fields": {
            "event_status": event_candidates,
            "duration_survival": duration_candidates,
            "prediction": prediction_candidates,
        },

        "controls": {
            "no_model_fitted": True,
            "no_target_redefined": True,
            "no_censored_case_relabeling": True,
            "no_probability_assumption": True,
            "no_post_creation_feature_engineering": True,
            "native_t7_semantics_preserved": True,
        },

        "decision": {
            "purpose": (
                "Resolve native T7 output structure "
                "before constructing the T8 resolution "
                "decision component."
            ),
            "component_not_yet_built": True,
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

    print("\nArtifact")
    print("-" * 80)
    print(f"  report: {REPORT}")

    print("\nStatus: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()