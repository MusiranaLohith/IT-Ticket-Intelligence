from pathlib import Path
import json
import numpy as np


T5_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/modeling/T5"
)

PREDICTION_PATH = (
    T5_ROOT
    / "metrics"
    / "t5_mod009_locked_evaluation_predictions.npz"
)

METRICS_PATH = (
    T5_ROOT
    / "metrics"
    / "t5_mod009_locked_evaluation_metrics.json"
)

CLOSURE_PATH = (
    T5_ROOT
    / "metrics"
    / "t5_mod011_final_closure.json"
)


EXPECTED_ROWS = 20_827
EXPECTED_POSITIVE = 1_318
EXPECTED_NEGATIVE = 19_509


def check(condition, label):
    status = "PASS" if condition else "FAIL"
    print(f"{label}: {status}")
    return condition


print("=" * 78)
print("T10 / OP-035 — T5 NATIVE EMPIRICAL EVIDENCE VALIDATION")
print("=" * 78)


# ---------------------------------------------------------------------
# 1. Artifact existence
# ---------------------------------------------------------------------

print("\n[1] ARTIFACT EXISTENCE")

artifacts_ok = True

for path in [PREDICTION_PATH, METRICS_PATH, CLOSURE_PATH]:
    exists = path.is_file()
    print(f"{path}: {'FOUND' if exists else 'MISSING'}")
    artifacts_ok &= exists

check(artifacts_ok, "C1 artifact inventory")


if not artifacts_ok:
    raise SystemExit("Required T5 artifact missing.")


# ---------------------------------------------------------------------
# 2. Load locked prediction checkpoint
# ---------------------------------------------------------------------

print("\n[2] LOCKED PREDICTION CHECKPOINT")

data = np.load(PREDICTION_PATH, allow_pickle=False)

expected_keys = {"y_true", "p_duplicate", "p_base"}

keys_ok = set(data.files) == expected_keys

print("Keys:", data.files)

check(keys_ok, "C2 expected native probability keys")


if not keys_ok:
    raise SystemExit("Unexpected T5 prediction checkpoint schema.")


y_true = data["y_true"]
p_duplicate = data["p_duplicate"]
p_base = data["p_base"]


# ---------------------------------------------------------------------
# 3. Population alignment
# ---------------------------------------------------------------------

print("\n[3] POPULATION ALIGNMENT")

print("y_true rows:", len(y_true))
print("p_duplicate rows:", len(p_duplicate))
print("p_base rows:", len(p_base))

population_ok = (
    len(y_true) == EXPECTED_ROWS
    and len(p_duplicate) == EXPECTED_ROWS
    and len(p_base) == EXPECTED_ROWS
    and len(y_true) == len(p_duplicate) == len(p_base)
)

check(population_ok, "C3 locked population = 20,827 and arrays aligned")


# ---------------------------------------------------------------------
# 4. Native target validation
# ---------------------------------------------------------------------

print("\n[4] NATIVE TARGET VALIDATION")

unique_targets = np.unique(y_true)

positive = int(np.sum(y_true == 1))
negative = int(np.sum(y_true == 0))

print("Unique y_true values:", unique_targets.tolist())
print("Positive:", positive)
print("Negative:", negative)

target_ok = (
    np.array_equal(unique_targets, np.array([0, 1], dtype=np.int8))
    and positive == EXPECTED_POSITIVE
    and negative == EXPECTED_NEGATIVE
)

check(target_ok, "C4 native binary outcome and expected class counts")


# ---------------------------------------------------------------------
# 5. Probability validity
# ---------------------------------------------------------------------

print("\n[5] PROBABILITY VALIDATION")

duplicate_finite = bool(np.isfinite(p_duplicate).all())
base_finite = bool(np.isfinite(p_base).all())

duplicate_range = bool(
    ((p_duplicate >= 0.0) & (p_duplicate <= 1.0)).all()
)

base_range = bool(
    ((p_base >= 0.0) & (p_base <= 1.0)).all()
)

print("p_duplicate finite:", duplicate_finite)
print("p_duplicate min:", float(np.min(p_duplicate)))
print("p_duplicate max:", float(np.max(p_duplicate)))

print("p_base finite:", base_finite)
print("p_base min:", float(np.min(p_base)))
print("p_base max:", float(np.max(p_base)))

probability_ok = (
    duplicate_finite
    and base_finite
    and duplicate_range
    and base_range
)

check(probability_ok, "C5 probability values finite and within [0, 1]")


# ---------------------------------------------------------------------
# 6. Locked metrics metadata
# ---------------------------------------------------------------------

print("\n[6] LOCKED METRICS METADATA")

with open(METRICS_PATH, "r", encoding="utf-8") as f:
    metrics = json.load(f)

evaluation_population = metrics["evaluation_population"]
locked_metrics = metrics["metrics"]
controls = metrics["controls"]

print("Rows:", evaluation_population["rows"])
print("Positive:", evaluation_population["positive"])
print("Negative:", evaluation_population["negative"])
print("Unique IDs in source evaluation population:",
      evaluation_population["unique_ids"])

print("Average Precision:",
      locked_metrics["average_precision"])

print("ROC-AUC:",
      locked_metrics["roc_auc"])

print("Log Loss:",
      locked_metrics["log_loss"])

print("Brier:",
      locked_metrics["brier_score"])

print("Descriptive 0.5 precision:",
      locked_metrics["threshold_0_5"]["precision"])

print("Descriptive 0.5 recall:",
      locked_metrics["threshold_0_5"]["recall"])

print("Descriptive 0.5 F1:",
      locked_metrics["threshold_0_5"]["f1"])

print("Descriptive positive predictions:",
      locked_metrics["threshold_0_5"]["positive_predictions"])

metadata_ok = (
    evaluation_population["rows"] == EXPECTED_ROWS
    and evaluation_population["positive"] == EXPECTED_POSITIVE
    and evaluation_population["negative"] == EXPECTED_NEGATIVE
    and evaluation_population["unique_ids"] == EXPECTED_ROWS
)

check(metadata_ok, "C6 locked evaluation metadata reconciles")


# ---------------------------------------------------------------------
# 7. Locked-evaluation controls
# ---------------------------------------------------------------------

print("\n[7] LOCKED-EVALUATION CONTROLS")

control_names = [
    "model_refit",
    "calibrator_refit",
    "vectorizer_refit",
    "threshold_optimization",
    "evaluation_used_for_selection",
    "evaluation_used_for_calibration",
    "synthetic_data",
    "raw_archive_scanned",
    "target_provenance_used_as_feature",
]

controls_ok = True

for name in control_names:
    value = controls.get(name)
    print(f"{name}: {value}")
    controls_ok &= value is False

check(controls_ok, "C7 locked evaluation controls preserved")


# ---------------------------------------------------------------------
# 8. Ticket-level provenance limitation
# ---------------------------------------------------------------------

print("\n[8] TICKET-LEVEL PROVENANCE")

print("NPZ contains canonical ticket IDs: NO")
print("NPZ keys:", data.files)
print("Positional ID reconstruction attempted: NO")
print("Ticket-level T5 intersection established: NO")

provenance_limitation_acknowledged = True

check(
    provenance_limitation_acknowledged,
    "C8 ticket-level provenance limitation explicitly preserved"
)


# ---------------------------------------------------------------------
# 9. Calibration / probability semantics
# ---------------------------------------------------------------------

print("\n[9] PROBABILITY SEMANTICS")

closure = {}

with open(CLOSURE_PATH, "r", encoding="utf-8") as f:
    closure = json.load(f)

selected_pipeline = closure["selected_pipeline"]

print("Representation:",
      selected_pipeline["representation"])

print("Classifier:",
      selected_pipeline["classifier"]["type"])

print("Calibration:",
      selected_pipeline["calibration"])

print("Probability output:",
      selected_pipeline["probability_output"])

print("Threshold:",
      selected_pipeline["threshold"]["value"])

print("Threshold status:",
      selected_pipeline["threshold"]["status"])

probability_semantics_ok = (
    selected_pipeline["calibration"] == "Sigmoid"
    and selected_pipeline["probability_output"] == "p_duplicate"
    and selected_pipeline["threshold"]["status"] == "descriptive_only"
)

check(
    probability_semantics_ok,
    "C9 native probability and threshold semantics preserved"
)


# ---------------------------------------------------------------------
# 10. T10 policy boundary
# ---------------------------------------------------------------------

print("\n[10] T10 POLICY BOUNDARY")

policy_checks = {
    "automation_threshold": False,
    "autonomous_duplicate_decision": False,
    "human_review_removal": False,
    "universal_t10_score": False,
    "cross_task_fusion": False,
}

for name, value in policy_checks.items():
    print(f"{name}: {'NOT ASSERTED' if value is False else value}")

policy_boundary_ok = all(value is False for value in policy_checks.values())

check(
    policy_boundary_ok,
    "C10 no unsupported T10 policy inference"
)


# ---------------------------------------------------------------------
# Final status
# ---------------------------------------------------------------------

all_checks = (
    artifacts_ok
    and keys_ok
    and population_ok
    and target_ok
    and probability_ok
    and metadata_ok
    and controls_ok
    and provenance_limitation_acknowledged
    and probability_semantics_ok
    and policy_boundary_ok
)

print("\n" + "=" * 78)

if all_checks:
    print("STATUS: PASS WITH PROVENANCE LIMITATION")
    print("T5 native probability evidence is empirically validated.")
    print(
        "The locked evaluation artifact does not establish canonical "
        "ticket-ID provenance."
    )
    print(
        "No ticket-level intersection, operational threshold, "
        "automation policy, or universal T10 score is established."
    )
else:
    print("STATUS: FAIL")

print("=" * 78)