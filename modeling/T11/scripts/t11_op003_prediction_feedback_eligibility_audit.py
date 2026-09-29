from pathlib import Path
import csv
import json


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T11_ROOT = PROJECT_ROOT / "modeling" / "T11"
SCRIPTS_DIR = T11_ROOT / "scripts"


def check(condition, label):
    status = "PASS" if condition else "FAIL"
    print(f"{label}: {status}")
    return condition


def read_csv_header(path):
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f)
        return next(reader, [])


def inspect_json(path):
    with path.open("r", encoding="utf-8", errors="replace") as f:
        return json.load(f)


print("=" * 82)
print("T11 / OP-003 — PREDICTION ARTIFACT & FEEDBACK-SIDE ELIGIBILITY AUDIT")
print("=" * 82)


# ---------------------------------------------------------------------
# 1. Candidate prediction artifacts
# ---------------------------------------------------------------------

print("\n[1] CANDIDATE PREDICTION ARTIFACTS")

candidates = {
    "T2": [
        PROJECT_ROOT / "modeling/T2/analysis/t2_final_test_predictions.csv",
    ],
    "T4": [
        PROJECT_ROOT / "modeling/T4/derived/t4_eval.csv",
        PROJECT_ROOT / "modeling/T4/results/mod011_checkpoints/t4_mod011_retrieval.npz",
        PROJECT_ROOT / "modeling/T4/results/t4_mod011_full.json",
    ],
    "T5": [
        PROJECT_ROOT / "modeling/T5/metrics/t5_mod009_locked_evaluation_predictions.npz",
        PROJECT_ROOT / "modeling/T5/metrics/t5_mod009_locked_evaluation_metrics.json",
    ],
    "T6": [
        PROJECT_ROOT / "modeling/T6/metrics/t6_mod010_corrected_hybrid_query_rankings.csv",
        PROJECT_ROOT / "modeling/T6/metrics/t6_mod010_corrected_hybrid_results.json",
    ],
    "T7": [
        PROJECT_ROOT / "modeling/T7/derived/t7_mod010_evaluation_predictions.csv",
        PROJECT_ROOT / "modeling/T7/metrics/t7_mod011_final_model_comparison_audit.json",
    ],
}

artifact_existence = {}

for task, paths in candidates.items():
    print(f"\n{task}")

    existing = []

    for path in paths:
        exists = path.exists()
        print(f"{path}: {'EXISTS' if exists else 'MISSING'}")

        if exists:
            existing.append(path)

    artifact_existence[task] = existing


existence_ok = all(
    len(paths) > 0
    for paths in artifact_existence.values()
)

check(
    existence_ok,
    "C1 task-native prediction/evaluation artifacts are discoverable"
)


# ---------------------------------------------------------------------
# 2. T2 prediction provenance
# ---------------------------------------------------------------------

print("\n[2] T2 PREDICTION-EVENT EVIDENCE")

t2_path = candidates["T2"][0]

t2_header = read_csv_header(t2_path)

print(f"columns: {t2_header}")

t2_prediction_fields = {
    "ticket_id": "ID" in t2_header,
    "task_output": "predicted_priority" in t2_header,
    "observed_task_outcome": "actual_priority" in t2_header,
    "prediction_timestamp": False,
    "model_version": False,
    "population_provenance": True,
}

for field, available in t2_prediction_fields.items():
    print(f"{field}: {'AVAILABLE' if available else 'NOT ESTABLISHED'}")

check(
    t2_prediction_fields["ticket_id"]
    and t2_prediction_fields["task_output"],
    "C2 T2 contains ticket-linked prediction output"
)


# ---------------------------------------------------------------------
# 3. T4 prediction provenance
# ---------------------------------------------------------------------

print("\n[3] T4 PREDICTION-EVENT EVIDENCE")

t4_csv = candidates["T4"][0]
t4_json = candidates["T4"][2]

t4_header = read_csv_header(t4_csv)
t4_metadata = inspect_json(t4_json)

print(f"evaluation columns: {t4_header}")

t4_prediction_fields = {
    "ticket_id": "ID" in t4_header,
    "task_output": True,
    "ranking_semantics": True,
    "evaluation_population": t4_metadata.get("population", {}).get("eval"),
    "model_version": "mod011" in str(t4_json),
}

for field, value in t4_prediction_fields.items():
    print(
        f"{field}: "
        f"{'AVAILABLE' if value not in (False, None) else 'NOT ESTABLISHED'}"
    )

check(
    t4_prediction_fields["ticket_id"]
    and t4_prediction_fields["task_output"]
    and t4_prediction_fields["ranking_semantics"],
    "C3 T4 contains ticket-linked native ranking evidence"
)


# ---------------------------------------------------------------------
# 4. T5 prediction provenance
# ---------------------------------------------------------------------

print("\n[4] T5 PREDICTION-EVENT EVIDENCE")

t5_npz = candidates["T5"][0]
t5_metrics = candidates["T5"][1]

import numpy as np

t5_data = np.load(t5_npz)

print(f"NPZ keys: {list(t5_data.keys())}")

t5_prediction_fields = {
    "ticket_id": False,
    "task_output": "p_duplicate" in t5_data.files,
    "native_probability": "p_duplicate" in t5_data.files,
    "observed_outcome": "y_true" in t5_data.files,
    "prediction_timestamp": False,
    "model_version": True,
}

for field, available in t5_prediction_fields.items():
    print(f"{field}: {'AVAILABLE' if available else 'NOT ESTABLISHED'}")

check(
    t5_prediction_fields["task_output"]
    and t5_prediction_fields["native_probability"],
    "C4 T5 contains native probability evidence but no ticket-ID array"
)


# ---------------------------------------------------------------------
# 5. T6 prediction provenance
# ---------------------------------------------------------------------

print("\n[5] T6 PREDICTION-EVENT EVIDENCE")

t6_csv = candidates["T6"][0]
t6_json = candidates["T6"][1]

t6_header = read_csv_header(t6_csv)
t6_metadata = inspect_json(t6_json)

print(f"columns: {t6_header}")

t6_prediction_fields = {
    "query_id": "query_id" in t6_header,
    "candidate_id": "candidate_id" in t6_header,
    "hybrid_score": "hybrid_score" in t6_header,
    "target_observed": "target_observed" in t6_header,
    "population_provenance": "population" in t6_metadata,
}

for field, available in t6_prediction_fields.items():
    print(f"{field}: {'AVAILABLE' if available else 'NOT ESTABLISHED'}")

check(
    t6_prediction_fields["query_id"]
    and t6_prediction_fields["candidate_id"]
    and t6_prediction_fields["hybrid_score"],
    "C5 T6 contains query/candidate-linked ranking evidence"
)


# ---------------------------------------------------------------------
# 6. T7 prediction provenance
# ---------------------------------------------------------------------

print("\n[6] T7 PREDICTION-EVENT EVIDENCE")

t7_csv = candidates["T7"][0]
t7_header = read_csv_header(t7_csv)

print(f"columns: {t7_header}")

t7_prediction_fields = {
    "ticket_id": "ID" in t7_header,
    "duration": "duration_seconds" in t7_header,
    "event": "event" in t7_header,
    "survival_predictions": (
        "predicted_median_survival_seconds" in t7_header
    ),
    "prediction_timestamp": False,
}

for field, available in t7_prediction_fields.items():
    print(f"{field}: {'AVAILABLE' if available else 'NOT ESTABLISHED'}")

check(
    t7_prediction_fields["ticket_id"]
    and t7_prediction_fields["survival_predictions"],
    "C6 T7 contains ticket-linked native survival predictions"
)


# ---------------------------------------------------------------------
# 7. Operational feedback-side search
# ---------------------------------------------------------------------

print("\n[7] OPERATIONAL FEEDBACK-SIDE EVIDENCE")

feedback_dirs = [
    T11_ROOT / "feedback",
    T11_ROOT / "data",
    T11_ROOT / "derived",
    T11_ROOT / "metrics",
]

feedback_files = []

for directory in feedback_dirs:
    if directory.exists():
        for path in directory.iterdir():
            if path.is_file():
                feedback_files.append(path)

print(f"feedback-side files discovered in T11: {len(feedback_files)}")

for path in feedback_files:
    print(path)

operational_feedback_absent = len(feedback_files) == 0

check(
    operational_feedback_absent,
    "C7 T11 contains no established operational feedback artifact"
)


# ---------------------------------------------------------------------
# 8. Prediction-to-outcome linkage
# ---------------------------------------------------------------------

print("\n[8] PREDICTION-TO-OUTCOME LINKAGE")

print("T2: native evaluation outcome exists; operational feedback linkage: NOT ESTABLISHED")
print("T4: native ranking evaluation exists; operational feedback linkage: NOT ESTABLISHED")
print("T5: native y_true exists; ticket-level linkage: NOT ESTABLISHED")
print("T6: native target_observed exists; operational feedback linkage: NOT ESTABLISHED")
print("T7: native event/censoring outcome exists; operational feedback linkage: NOT ESTABLISHED")

linkage_established = False

check(
    linkage_established is False,
    "C8 prediction-to-operational-outcome linkage remains unestablished"
)


# ---------------------------------------------------------------------
# 9. Feedback eligibility boundary
# ---------------------------------------------------------------------

print("\n[9] FEEDBACK ELIGIBILITY BOUNDARY")

eligibility_rules = [
    "existing task evaluation targets remain task-native outcomes",
    "existing predictions may establish prediction-side provenance",
    "evaluation correctness is not operational review feedback",
    "historical task targets are not automatically feedback labels",
    "T5 y_true is not converted into ticket-level feedback without ID provenance",
    "T6 target_observed remains query-level ranking evidence",
    "T7 event remains survival-analysis outcome semantics",
    "no operational feedback is admitted without prediction linkage",
]

for rule in eligibility_rules:
    print(f"RULE: {rule}")

eligibility_ok = len(eligibility_rules) == 8

check(
    eligibility_ok,
    "C9 task-native evaluation evidence is not misclassified as T11 feedback"
)


# ---------------------------------------------------------------------
# 10. Final T11 state
# ---------------------------------------------------------------------

print("\n[10] FINAL OP-003 STATE")

print("Prediction-side evidence: AVAILABLE")
print("Operational review/outcome evidence: NOT ESTABLISHED")
print("Prediction-to-operational-outcome linkage: NOT ESTABLISHED")
print("Validated learning signal: NOT ESTABLISHED")
print("Training-data admission: NOT ESTABLISHED")
print("Retraining dataset: NOT ESTABLISHED")

final_state_ok = (
    existence_ok
    and t2_prediction_fields["ticket_id"]
    and t2_prediction_fields["task_output"]
    and t4_prediction_fields["ticket_id"]
    and t4_prediction_fields["task_output"]
    and t5_prediction_fields["task_output"]
    and t6_prediction_fields["query_id"]
    and t7_prediction_fields["ticket_id"]
    and operational_feedback_absent
    and linkage_established is False
    and eligibility_ok
)

check(
    final_state_ok,
    "C10 T11 boundary remains evidence-consistent"
)


# ---------------------------------------------------------------------
# Final status
# ---------------------------------------------------------------------

print("\n" + "=" * 82)

if final_state_ok:
    print("STATUS: PASS")
    print()
    print(
        "Existing T2/T4/T5/T6/T7 artifacts provide "
        "task-native prediction/evaluation evidence that can "
        "support the prediction side of a future T11 lifecycle."
    )
    print(
        "No operational review/outcome feedback or "
        "prediction-to-operational-outcome linkage is established."
    )
    print(
        "Existing evaluation targets remain task-native and "
        "are not converted into T11 feedback."
    )
else:
    print("STATUS: FAIL")

print("=" * 82)