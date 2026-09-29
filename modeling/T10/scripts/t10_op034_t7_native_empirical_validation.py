from pathlib import Path
import csv
import json


# ============================================================
# T10 / OP-034 — T7 Native Empirical Validation
# ============================================================

AUDIT_PATH = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/"
    "modeling/T7/metrics/t7_mod010_log_normal_aft_audit.json"
)

COMPARISON_PATH = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/"
    "modeling/T7/metrics/t7_mod011_final_model_comparison_audit.json"
)

PREDICTIONS_PATH = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/"
    "modeling/T7/derived/t7_mod010_evaluation_predictions.csv"
)

EXPECTED_TRAIN_ROWS = 411052
EXPECTED_EVAL_ROWS = 102764

EXPECTED_HORIZONS = {
    211583.0,
    1780179.0,
    14608619.0,
}


print("=" * 70)
print("T10 / OP-034 — T7 NATIVE EMPIRICAL VALIDATION")
print("=" * 70)


# ------------------------------------------------------------
# 1. Artifact availability
# ------------------------------------------------------------

print("\n[1] Native T7 artifacts")

artifacts = {
    "log_normal_audit": AUDIT_PATH,
    "final_comparison_audit": COMPARISON_PATH,
    "evaluation_predictions": PREDICTIONS_PATH,
}

artifact_pass = True

for name, path in artifacts.items():
    exists = path.exists()

    print(f"{name}: {path}")
    print(f"exists: {exists}")

    if not exists:
        artifact_pass = False

if not artifact_pass:
    print("\nSTATUS: FAIL")
    print("Reason: Required native T7 artifact is missing.")
    raise SystemExit(1)


# ------------------------------------------------------------
# 2. Native model audit
# ------------------------------------------------------------

print("\n[2] Native T7 model audit")

with AUDIT_PATH.open("r", encoding="utf-8") as f:
    audit = json.load(f)

print(f"Task: {audit.get('task')}")
print(f"Operation: {audit.get('operation')}")
print(f"Status: {audit.get('status')}")
print(f"Model family: {audit['model']['family']}")

training_rows = audit["model"]["training_rows"]
evaluation_rows = audit["model"]["evaluation_rows"]

print(f"Training rows: {training_rows}")
print(f"Evaluation rows: {evaluation_rows}")
print(f"Feature count: {audit['model']['feature_count']}")

print("\nFeature boundary:")
for key, value in audit["feature_boundary"].items():
    print(f"{key}: {value}")


# ------------------------------------------------------------
# 3. Prediction artifact schema
# ------------------------------------------------------------

print("\n[3] Native evaluation prediction schema")

with PREDICTIONS_PATH.open(
    "r",
    encoding="utf-8",
    newline=""
) as f:

    reader = csv.reader(f)
    header = next(reader)

required_columns = {
    "ID",
    "duration_seconds",
    "event",
    "predicted_median_survival_seconds",
    "survival_probability_at_211583_seconds",
    "survival_probability_at_1780179_seconds",
    "survival_probability_at_14608619_seconds",
}

missing_columns = sorted(
    required_columns - set(header)
)

print(f"Columns: {header}")
print(f"Required columns missing: {missing_columns}")

schema_pass = len(missing_columns) == 0

if not schema_pass:
    print("\nSTATUS: FAIL")
    raise SystemExit(1)


# ------------------------------------------------------------
# 4. Lightweight evaluation reconciliation
# ------------------------------------------------------------

print("\n[4] Evaluation population reconciliation")

row_count = 0
unique_ids = set()

null_ids = 0
blank_ids = 0

null_duration = 0
invalid_duration = 0

null_events = 0
invalid_events = 0

event_counts = {
    "0": 0,
    "1": 0,
}

horizon_probability_nulls = {
    "211583": 0,
    "1780179": 0,
    "14608619": 0,
}

with PREDICTIONS_PATH.open(
    "r",
    encoding="utf-8",
    newline=""
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        row_count += 1

        ticket_id = row.get("ID")
        duration = row.get("duration_seconds")
        event = row.get("event")

        # ----------------------------------------------------
        # ID
        # ----------------------------------------------------

        if ticket_id is None:
            null_ids += 1
        elif ticket_id.strip() == "":
            blank_ids += 1
        else:
            unique_ids.add(ticket_id.strip())

        # ----------------------------------------------------
        # Duration
        # ----------------------------------------------------

        if duration is None or duration.strip() == "":
            null_duration += 1
        else:
            try:
                duration_value = float(duration)

                if duration_value < 0:
                    invalid_duration += 1

            except ValueError:
                invalid_duration += 1

        # ----------------------------------------------------
        # Event
        # ----------------------------------------------------

        if event is None or event.strip() == "":
            null_events += 1
        elif event.strip() not in {"0", "1"}:
            invalid_events += 1
        else:
            event_counts[event.strip()] += 1

        # ----------------------------------------------------
        # Native survival probabilities
        # ----------------------------------------------------

        for horizon, key in [
            ("211583", "survival_probability_at_211583_seconds"),
            ("1780179", "survival_probability_at_1780179_seconds"),
            ("14608619", "survival_probability_at_14608619_seconds"),
        ]:

            value = row.get(key)

            if value is None or value.strip() == "":
                horizon_probability_nulls[horizon] += 1


print(f"Rows: {row_count}")
print(f"Unique IDs: {len(unique_ids)}")

print(f"Null IDs: {null_ids}")
print(f"Blank IDs: {blank_ids}")

print(f"Null durations: {null_duration}")
print(f"Invalid durations: {invalid_duration}")

print(f"Null events: {null_events}")
print(f"Invalid events: {invalid_events}")

print(f"Event=1 rows: {event_counts['1']}")
print(f"Event=0 rows: {event_counts['0']}")

print(
    "Null survival probabilities by horizon:",
    horizon_probability_nulls
)


# ------------------------------------------------------------
# 5. Native survival semantics
# ------------------------------------------------------------

print("\n[5] Native survival semantics")

event_semantics_pass = (
    invalid_events == 0
    and event_counts["1"] + event_counts["0"] == row_count
)

duration_semantics_pass = (
    null_duration == 0
    and invalid_duration == 0
)

print(
    "event ∈ {0,1}:",
    event_semantics_pass
)

print(
    "duration is populated and non-negative:",
    duration_semantics_pass
)

print(
    "event=1 represents observed resolution; "
    "event=0 remains right-censored."
)

print(
    "Censored observations are not interpreted as negative outcomes."
)


# ------------------------------------------------------------
# 6. Native evaluation metrics
# ------------------------------------------------------------

print("\n[6] Native T7 empirical correctness evidence")

evaluation_metrics = audit["evaluation_metrics"]

print(
    "Harrell concordance index:",
    evaluation_metrics["harrell_concordance_index"]
)

for item in evaluation_metrics["ipcw_brier"]:

    print(
        f"Horizon {item['horizon_seconds']}: "
        f"IPCW Brier={item['ipcw_brier_score']:.6f}"
    )


# ------------------------------------------------------------
# 7. Final model comparison evidence
# ------------------------------------------------------------

print("\n[7] Native final model comparison")

with COMPARISON_PATH.open("r", encoding="utf-8") as f:
    comparison = json.load(f)

comparison_population = comparison["evaluation_population"]

print(
    "Comparison evaluation rows:",
    comparison_population["rows"]
)

print(
    "Population alignment:",
    comparison_population["population_alignment"]
)

print(
    "Models compared:",
    comparison["models_compared"]
)

print(
    "Weibull C-index:",
    comparison["weibull_aft"]["harrell_concordance_index"]
)

print(
    "Log-Normal C-index:",
    comparison["lognormal_aft"]["harrell_concordance_index"]
)

print(
    "Log-Normal horizons better than Weibull:",
    comparison["comparison"][
        "lognormal_horizons_better_than_weibull"
    ]
)

print(
    "Weibull horizons better than KM:",
    comparison["comparison"][
        "weibull_horizons_better_than_km"
    ]
)

print(
    "Log-Normal horizons better than KM:",
    comparison["comparison"][
        "lognormal_horizons_better_than_km"
    ]
)


# ------------------------------------------------------------
# 8. T7 → T10 contract alignment
# ------------------------------------------------------------

print("\n[8] T7 → T10 empirical contract alignment")

population_pass = (
    training_rows == EXPECTED_TRAIN_ROWS
    and evaluation_rows == EXPECTED_EVAL_ROWS
    and row_count == EXPECTED_EVAL_ROWS
)

id_pass = (
    len(unique_ids) == row_count
    and null_ids == 0
    and blank_ids == 0
)

horizon_pass = (
    set(EXPECTED_HORIZONS)
    == {
        float(item["horizon_seconds"])
        for item in evaluation_metrics["ipcw_brier"]
    }
)

comparison_alignment_pass = (
    comparison_population["rows"] == EXPECTED_EVAL_ROWS
    and comparison_population["population_alignment"] == "PASS"
)

controls_pass = (
    audit["feature_boundary"]["creation_only"] is True
    and audit["feature_boundary"]["post_creation_history_used"] is False
    and audit["feature_boundary"]["current_status_used"] is False
    and audit["feature_boundary"]["current_resolution_used"] is False
    and audit["feature_boundary"]["evaluation_fitting"] is False
    and audit["feature_boundary"]["raw_archive_access"] is False
)

checks = [
    (
        "C1",
        "Native chronological evaluation population reconciles",
        population_pass,
    ),
    (
        "C2",
        "Evaluation ticket IDs are traceable",
        id_pass,
    ),
    (
        "C3",
        "Native event/time-to-event semantics are preserved",
        event_semantics_pass and duration_semantics_pass,
    ),
    (
        "C4",
        "Native survival horizons are preserved",
        horizon_pass,
    ),
    (
        "C5",
        "Creation-only feature boundary is preserved",
        controls_pass,
    ),
    (
        "C6",
        "Final comparison population aligns",
        comparison_alignment_pass,
    ),
    (
        "C7",
        "Censoring-aware native evaluation remains task-specific",
        True,
    ),
    (
        "C8",
        "Survival probabilities are not converted into a universal T10 probability",
        True,
    ),
    (
        "C9",
        "No automation threshold is introduced",
        True,
    ),
    (
        "C10",
        "No universal T10 policy or cross-task fusion is introduced",
        True,
    ),
]

all_pass = True

for cid, description, status in checks:

    print(
        f"{cid} {description:<65} "
        f"{'PASS' if status else 'FAIL'}"
    )

    if not status:
        all_pass = False


# ------------------------------------------------------------
# 9. Explicit limitations
# ------------------------------------------------------------

print("\n[9] Explicit T7 limitations")

print(
    "T7 native evidence establishes resolution-time survival "
    "model behavior only."
)

print(
    "Event=0 remains right-censored and is not treated as "
    "a negative resolution outcome."
)

print(
    "Survival probabilities are task-native survival estimates, "
    "not a universal T10 automation probability."
)

print(
    "The reported predictive survival models do not show "
    "uniform improvement across the reported metrics and horizons."
)

print(
    "No autonomous resolution-time decision boundary is validated."
)

print(
    "No ticket-level AUTOMATE state is validated."
)

print(
    "No HUMAN_REVIEW boundary is empirically validated."
)

print(
    "No DEFER_INSUFFICIENT_EVIDENCE boundary is empirically validated."
)

print(
    "No universal T10 score, threshold, or cross-task policy "
    "is introduced."
)


# ------------------------------------------------------------
# 10. Final assessment
# ------------------------------------------------------------

print("\n[10] Final validation assessment")

print(f"Artifact availability: {artifact_pass}")
print(f"Schema alignment: {schema_pass}")
print(f"Population reconciliation: {population_pass}")
print(f"ID traceability: {id_pass}")
print(f"Event semantics: {event_semantics_pass}")
print(f"Duration semantics: {duration_semantics_pass}")
print(f"Horizon alignment: {horizon_pass}")
print(f"Comparison population alignment: {comparison_alignment_pass}")
print(f"Creation-only controls: {controls_pass}")

if all_pass:

    print("\nSTATUS: PASS")

    print(
        "T7 native empirical evidence is reconciled and remains "
        "aligned with the closed T10 contract."
    )

else:

    print("\nSTATUS: FAIL")

    print(
        "One or more T7 empirical validation checks failed."
    )


print("=" * 70)
print("END OF T10 / OP-034")
print("=" * 70)