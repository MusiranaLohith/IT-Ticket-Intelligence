import csv
import json
import sys
from pathlib import Path


# ============================================================================
# PATHS
# ============================================================================

ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

METRICS = ROOT / "modeling/T7/metrics"

MOD007_AUDIT = (
    METRICS /
    "t7_mod007_predictive_survival_audit.json"
)

MOD008 = (
    METRICS /
    "t7_mod008_predictive_vs_reference.csv"
)

MOD010_AUDIT = (
    METRICS /
    "t7_mod010_log_normal_aft_audit.json"
)

OUTPUT_CSV = (
    METRICS /
    "t7_mod011_final_model_comparison.csv"
)

OUTPUT_JSON = (
    METRICS /
    "t7_mod011_final_model_comparison_audit.json"
)

csv.field_size_limit(sys.maxsize)


# ============================================================================
# HELPERS
# ============================================================================

def load_json(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Required artifact not found:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def load_csv(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Required artifact not found:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        if not reader.fieldnames:
            raise RuntimeError(
                f"CSV has no header: {path}"
            )

        rows = list(reader)

    return reader.fieldnames, rows


def find_column(fieldnames, required_terms):
    """
    Find exactly one column containing all required terms.
    Matching is case-insensitive.
    """

    matches = []

    for field in fieldnames:

        normalized = field.lower().replace(
            "_", " "
        )

        if all(
            term.lower() in normalized
            for term in required_terms
        ):
            matches.append(field)

    if len(matches) == 1:
        return matches[0]

    if len(matches) == 0:
        raise RuntimeError(
            "Could not find a unique MOD-008 column "
            f"containing terms {required_terms}.\n"
            f"Available columns: {fieldnames}"
        )

    raise RuntimeError(
        "Multiple MOD-008 columns matched "
        f"{required_terms}: {matches}\n"
        "The comparison cannot safely continue."
    )


def find_horizon_column(fieldnames):
    matches = []

    for field in fieldnames:

        normalized = field.lower().replace(
            "_", " "
        )

        if "horizon" in normalized:
            matches.append(field)

    if len(matches) == 1:
        return matches[0]

    if len(matches) == 0:
        raise RuntimeError(
            "Could not find MOD-008 horizon column.\n"
            f"Available columns: {fieldnames}"
        )

    raise RuntimeError(
        f"Multiple horizon columns found: {matches}"
    )


# ============================================================================
# MAIN
# ============================================================================

def main():

    print("=" * 80)
    print(
        "T7 MOD-011 — Final Model Comparison & Locked Evaluation Decision"
    )
    print("=" * 80)

    # ------------------------------------------------------------------------
    # 1. Load artifacts
    # ------------------------------------------------------------------------

    print(
        "\n[1/7] Loading established T7 artifacts..."
    )

    mod007 = load_json(
        MOD007_AUDIT
    )

    mod008_fields, mod008_rows = load_csv(
        MOD008
    )

    mod010 = load_json(
        MOD010_AUDIT
    )

    print("  MOD-007: loaded")
    print("  MOD-008: loaded")
    print("  MOD-010: loaded")

    print(
        "\n  MOD-008 columns:"
    )

    for field in mod008_fields:
        print(
            f"    - {field}"
        )

    # ------------------------------------------------------------------------
    # 2. Validate population
    # ------------------------------------------------------------------------

    print(
        "\n[2/7] Validating evaluation population consistency..."
    )

    mod007_eval_rows = int(
        mod007[
            "model"
        ][
            "evaluation_rows"
        ]
    )

    mod010_eval_rows = int(
        mod010[
            "model"
        ][
            "evaluation_rows"
        ]
    )

    if mod007_eval_rows != mod010_eval_rows:
        raise RuntimeError(
            "MOD-007 and MOD-010 evaluation populations differ: "
            f"{mod007_eval_rows} vs {mod010_eval_rows}"
        )

    evaluation_rows = mod007_eval_rows

    print(
        f"  MOD-007 evaluation rows: "
        f"{mod007_eval_rows:,}"
    )

    print(
        f"  MOD-010 evaluation rows: "
        f"{mod010_eval_rows:,}"
    )

    print(
        "  Population alignment: PASS"
    )

    # ------------------------------------------------------------------------
    # 3. Extract Weibull metrics
    # ------------------------------------------------------------------------

    print(
        "\n[3/7] Extracting Weibull AFT metrics..."
    )

    weibull_cindex = float(
        mod007[
            "evaluation_metrics"
        ][
            "harrell_concordance_index"
        ]
    )

    weibull_brier = {}

    for item in mod007[
        "evaluation_metrics"
    ][
        "ipcw_brier"
    ]:

        horizon = float(
            item["horizon_seconds"]
        )

        weibull_brier[horizon] = float(
            item["ipcw_brier_score"]
        )

    print(
        f"  C-index: "
        f"{weibull_cindex:.9f}"
    )

    # ------------------------------------------------------------------------
    # 4. Extract Log-Normal metrics
    # ------------------------------------------------------------------------

    print(
        "\n[4/7] Extracting Log-Normal AFT metrics..."
    )

    lognormal_cindex = float(
        mod010[
            "evaluation_metrics"
        ][
            "harrell_concordance_index"
        ]
    )

    lognormal_brier = {}

    for item in mod010[
        "evaluation_metrics"
    ][
        "ipcw_brier"
    ]:

        horizon = float(
            item["horizon_seconds"]
        )

        lognormal_brier[horizon] = float(
            item["ipcw_brier_score"]
        )

    print(
        f"  C-index: "
        f"{lognormal_cindex:.9f}"
    )

    # ------------------------------------------------------------------------
    # 5. Extract KM reference from actual MOD-008 schema
    # ------------------------------------------------------------------------

    print(
        "\n[5/7] Extracting Kaplan–Meier reference metrics..."
    )

    horizon_column = find_horizon_column(
        mod008_fields
    )

    # We deliberately require both "km" and "brier".
    # This avoids accidentally selecting predictive Brier columns.
    km_brier_column = find_column(
        mod008_fields,
        [
            "km",
            "brier",
        ],
    )

    print(
        f"  Horizon column: {horizon_column}"
    )

    print(
        f"  KM Brier column: {km_brier_column}"
    )

    if not mod008_rows:
        raise RuntimeError(
            "MOD-008 comparison artifact is empty."
        )

    km_brier = {}

    for row in mod008_rows:

        horizon = float(
            row[horizon_column]
        )

        score = float(
            row[km_brier_column]
        )

        if horizon in km_brier:
            raise RuntimeError(
                f"Duplicate MOD-008 horizon: {horizon}"
            )

        km_brier[horizon] = score

    print(
        f"  KM reference horizons: "
        f"{len(km_brier)}"
    )

    # ------------------------------------------------------------------------
    # 6. Build final comparison
    # ------------------------------------------------------------------------

    print(
        "\n[6/7] Building final comparison..."
    )

    horizons = sorted(
        km_brier.keys()
    )

    if not horizons:
        raise RuntimeError(
            "No evaluation horizons found."
        )

    comparison_rows = []

    for horizon in horizons:

        if horizon not in weibull_brier:
            raise RuntimeError(
                f"Weibull Brier missing horizon "
                f"{horizon}"
            )

        if horizon not in lognormal_brier:
            raise RuntimeError(
                f"Log-Normal Brier missing horizon "
                f"{horizon}"
            )

        km_score = km_brier[horizon]
        weibull_score = weibull_brier[horizon]
        lognormal_score = lognormal_brier[horizon]

        comparison_rows.append({
            "horizon_seconds": horizon,
            "kaplan_meier_ipcw_brier": km_score,
            "weibull_aft_ipcw_brier": weibull_score,
            "lognormal_aft_ipcw_brier": lognormal_score,
            "weibull_minus_km":
                weibull_score - km_score,
            "lognormal_minus_km":
                lognormal_score - km_score,
            "lognormal_minus_weibull":
                lognormal_score - weibull_score,
        })

    cindex_difference = (
        lognormal_cindex
        - weibull_cindex
    )

    weibull_better_than_km = sum(
        row["weibull_minus_km"] < 0
        for row in comparison_rows
    )

    lognormal_better_than_km = sum(
        row["lognormal_minus_km"] < 0
        for row in comparison_rows
    )

    lognormal_better_than_weibull = sum(
        row["lognormal_minus_weibull"] < 0
        for row in comparison_rows
    )

    if (
        lognormal_better_than_km
        == len(comparison_rows)
        and
        lognormal_better_than_weibull
        == len(comparison_rows)
        and
        lognormal_cindex
        > weibull_cindex
    ):

        evidence_statement = (
            "The Log-Normal AFT formulation has lower reported "
            "IPCW Brier error than both the Kaplan-Meier reference "
            "and Weibull AFT at every evaluated horizon, and its "
            "Harrell C-index is higher than the Weibull AFT "
            "C-index. This is comparative evaluation evidence "
            "on the frozen evaluation population; it does not "
            "establish autonomous operational suitability."
        )

    else:

        evidence_statement = (
            "The evaluated predictive survival models do not "
            "show uniform improvement across the reported "
            "metrics and horizons. The evidence should "
            "therefore be carried forward as model-performance "
            "limitations."
        )

    # ------------------------------------------------------------------------
    # 7. Write artifacts
    # ------------------------------------------------------------------------

    print(
        "\n[7/7] Writing final comparison artifacts..."
    )

    with OUTPUT_CSV.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "horizon_seconds",
                "kaplan_meier_ipcw_brier",
                "weibull_aft_ipcw_brier",
                "lognormal_aft_ipcw_brier",
                "weibull_minus_km",
                "lognormal_minus_km",
                "lognormal_minus_weibull",
            ],
        )

        writer.writeheader()

        writer.writerows(
            comparison_rows
        )

    audit = {
        "task":
            "T7 Resolution-Time Estimation",

        "operation":
            "MOD-011",

        "status":
            "COMPLETE",

        "operation_purpose": (
            "Final comparative evaluation of established "
            "survival baselines using existing artifacts only."
        ),

        "raw_archive_access":
            False,

        "model_refitting":
            False,

        "new_feature_engineering":
            False,

        "evaluation_population": {
            "rows":
                evaluation_rows,

            "population_alignment":
                "PASS",
        },

        "models_compared": [
            "Kaplan-Meier reference",
            "Weibull AFT",
            "Log-Normal AFT",
        ],

        "source_schema": {
            "mod008_horizon_column":
                horizon_column,

            "mod008_km_brier_column":
                km_brier_column,
        },

        "weibull_aft": {
            "harrell_concordance_index":
                weibull_cindex,

            "ipcw_brier": [
                {
                    "horizon_seconds":
                        row["horizon_seconds"],

                    "score":
                        row[
                            "weibull_aft_ipcw_brier"
                        ],
                }
                for row in comparison_rows
            ],
        },

        "lognormal_aft": {
            "harrell_concordance_index":
                lognormal_cindex,

            "ipcw_brier": [
                {
                    "horizon_seconds":
                        row["horizon_seconds"],

                    "score":
                        row[
                            "lognormal_aft_ipcw_brier"
                        ],
                }
                for row in comparison_rows
            ],
        },

        "kaplan_meier_reference": {
            "ipcw_brier": [
                {
                    "horizon_seconds":
                        row["horizon_seconds"],

                    "score":
                        row[
                            "kaplan_meier_ipcw_brier"
                        ],
                }
                for row in comparison_rows
            ],
        },

        "comparison": {
            "lognormal_minus_weibull_cindex":
                cindex_difference,

            "weibull_horizons_better_than_km":
                weibull_better_than_km,

            "lognormal_horizons_better_than_km":
                lognormal_better_than_km,

            "lognormal_horizons_better_than_weibull":
                lognormal_better_than_weibull,
        },

        "evidence_statement":
            evidence_statement,

        "interpretation_boundary": (
            "The comparison describes model behavior on "
            "the frozen chronological evaluation population. "
            "It does not establish autonomous operational "
            "deployment suitability or an unsupported "
            "automation threshold."
        ),

        "artifacts": {
            "comparison_csv":
                str(OUTPUT_CSV),

            "audit_json":
                str(OUTPUT_JSON),
        },
    }

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            audit,
            f,
            indent=2,
        )

    print("\n" + "=" * 80)
    print("MOD-011 COMPLETE")
    print("=" * 80)

    print(
        f"\nEvaluation rows: "
        f"{evaluation_rows:,}"
    )

    print(
        f"Weibull C-index: "
        f"{weibull_cindex:.9f}"
    )

    print(
        f"Log-Normal C-index: "
        f"{lognormal_cindex:.9f}"
    )

    print(
        f"C-index difference "
        f"(LogNormal - Weibull): "
        f"{cindex_difference:+.9f}"
    )

    print(
        "\nHorizon comparison:"
    )

    for row in comparison_rows:

        print(
            f"  {row['horizon_seconds']:.0f}s | "
            f"KM={row['kaplan_meier_ipcw_brier']:.9f} | "
            f"Weibull={row['weibull_aft_ipcw_brier']:.9f} | "
            f"LogNormal={row['lognormal_aft_ipcw_brier']:.9f}"
        )

    print(
        "\nEvidence statement:"
    )

    print(
        evidence_statement
    )

    print(
        f"\nComparison CSV:\n"
        f"{OUTPUT_CSV}"
    )

    print(
        f"\nAudit JSON:\n"
        f"{OUTPUT_JSON}"
    )


if __name__ == "__main__":
    main()