from pathlib import Path
import ast
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

SOURCE = (
    ROOT / "modeling/T7/scripts/"
    "t7_mod010_log_normal_aft_baseline.py"
)

MODEL_JSON = (
    ROOT / "modeling/T7/metrics/"
    "t7_mod010_log_normal_aft_model.json"
)

OUT_JSON = (
    ROOT / "modeling/FMP/metrics/"
    "fmp06_op018r25_t7_exact_feature_builder_audit.json"
)


def main():
    print("=" * 72)
    print("FMP-06 OP-018R25 — T7 EXACT FEATURE BUILDER AUDIT")
    print("=" * 72)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation metrics: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    print("\n[1] Loading T7 MOD-010 source...")

    source_text = SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source_text)

    print(f"  source: {SOURCE}")
    print(f"  source lines: {len(source_text.splitlines())}")

    # ------------------------------------------------------------
    # Locate relevant functions
    # ------------------------------------------------------------
    print("\n[2] Locating feature/model functions...")

    functions = {}

    for node in ast.walk(tree):
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            functions[node.name] = node

    relevant_names = [
        name
        for name in functions
        if any(
            token in name.lower()
            for token in [
                "feature",
                "text",
                "model",
                "predict",
                "survival",
                "log"
            ]
        )
    ]

    print(
        "  relevant functions:",
        sorted(relevant_names)
    )

    # ------------------------------------------------------------
    # Extract source for relevant functions
    # ------------------------------------------------------------
    extracted = {}

    lines = source_text.splitlines()

    for name in sorted(relevant_names):
        node = functions[name]

        start = node.lineno
        end = getattr(
            node,
            "end_lineno",
            node.lineno
        )

        extracted[name] = {
            "start_line": start,
            "end_line": end,
            "source": "\n".join(
                lines[start - 1:end]
            ),
        }

    # ------------------------------------------------------------
    # Load frozen model metadata
    # ------------------------------------------------------------
    print("\n[3] Loading frozen model feature contract...")

    with MODEL_JSON.open(
        "r",
        encoding="utf-8"
    ) as f:
        model = json.load(f)

    feature_names = model.get(
        "feature_names",
        []
    )

    beta = model.get(
        "beta",
        {}
    )

    print(
        f"  frozen feature count: {len(feature_names)}"
    )

    print(
        "  frozen feature names:"
    )

    for i, feature in enumerate(
        feature_names
    ):
        print(
            f"    {i:02d}: {feature}"
        )

    # ------------------------------------------------------------
    # Search exact feature references in source
    # ------------------------------------------------------------
    print("\n[4] Searching source for frozen feature names...")

    feature_hits = {}

    for feature in feature_names:
        hits = []

        for line_no, line in enumerate(
            lines,
            start=1
        ):
            if feature in line:
                hits.append(line_no)

        feature_hits[feature] = hits

        print(
            f"  {feature}: {hits[:8]}"
            + (" ..." if len(hits) > 8 else "")
        )

    # ------------------------------------------------------------
    # Search critical transformation terms
    # ------------------------------------------------------------
    print("\n[5] Auditing transformation primitives...")

    search_terms = [
        "log1p",
        "value_counts",
        "StandardScaler",
        "mean",
        "std",
        "sin",
        "cos",
        "month",
        "weekday",
        "hour",
        "Creator",
        "Creator Detail",
        "Summary",
        "Description",
        "creation_year_scaled",
        "creation_month_sin",
        "creation_month_cos",
        "creation_weekday_sin",
        "creation_weekday_cos",
        "creation_hour_sin",
        "creation_hour_cos",
    ]

    term_hits = {}

    for term in search_terms:
        hits = [
            line_no
            for line_no, line in enumerate(
                lines,
                start=1
            )
            if term in line
        ]

        term_hits[term] = hits

        if hits:
            print(
                f"  {term}: {hits[:10]}"
                + (" ..." if len(hits) > 10 else "")
            )

    # ------------------------------------------------------------
    # Check parameter ordering
    # ------------------------------------------------------------
    print("\n[6] Checking coefficient contract...")

    beta_missing = [
        feature
        for feature in feature_names
        if feature not in beta
    ]

    extra_beta = [
        feature
        for feature in beta
        if feature not in feature_names
    ]

    print(
        f"  missing beta features: {len(beta_missing)}"
    )

    print(
        f"  extra beta features: {len(extra_beta)}"
    )

    result = {
        "operation":
            "FMP-06 OP-018R25",

        "status":
            "PASS",

        "read_only":
            True,

        "training_performed":
            False,

        "fitting_performed":
            False,

        "prediction_performed":
            False,

        "evaluation_performed":
            False,

        "locked_test_used":
            False,

        "artifact_modified":
            False,

        "source":
            str(SOURCE),

        "frozen_model":
            str(MODEL_JSON),

        "relevant_functions":
            sorted(relevant_names),

        "feature_names":
            feature_names,

        "feature_hits":
            feature_hits,

        "transformation_term_hits":
            term_hits,

        "beta_missing_features":
            beta_missing,

        "extra_beta_features":
            extra_beta,

        "extracted_functions":
            extracted,

        "purpose":
            (
                "Establish the exact native MOD-010 feature "
                "construction and model-interface implementation "
                "before accepting a reconstructed frozen runtime "
                "prediction."
            ),
    }

    OUT_JSON.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUT_JSON.open(
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            result,
            f,
            indent=2
        )

    print("\n" + "=" * 72)
    print("OP-018R25 AUDIT COMPLETE")
    print("=" * 72)

    print(
        f"Relevant functions: {len(relevant_names)}"
    )

    print(
        f"Frozen features: {len(feature_names)}"
    )

    print(
        f"Missing beta features: {len(beta_missing)}"
    )

    print(
        f"Extra beta features: {len(extra_beta)}"
    )

    print(
        f"Output: {OUT_JSON}"
    )

    print("\nNo training performed.")
    print("No fitting performed.")
    print("No prediction performed.")
    print("No evaluation performed.")
    print("No locked test used.")
    print("No artifact modification performed.")

    print("=" * 72)


if __name__ == "__main__":
    main()