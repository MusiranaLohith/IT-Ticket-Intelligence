import json
from pathlib import Path


# ============================================================
# T3-MOD-029
# Final T3 Closure & System Role
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

VALIDATION_PATH = (
    PROJECT_ROOT
    / "modeling/T3/metrics/"
      "t3_class_weighted_validation_metrics.json"
)

TEST_PATH = (
    PROJECT_ROOT
    / "modeling/T3/metrics/"
      "t3_final_test_metrics.json"
)

GENERALIZATION_PATH = (
    PROJECT_ROOT
    / "modeling/T3/analysis/"
      "t3_final_generalization_analysis.json"
)

ADVANCED_PATH = (
    PROJECT_ROOT
    / "modeling/T3/analysis/"
      "t3_advanced_branch_closure.json"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "modeling/T3/analysis/"
      "t3_final_closure.json"
)


# ============================================================
# Start
# ============================================================

print("T3_MOD_029_START")


# ============================================================
# Load completed evidence
# ============================================================

required_files = [
    VALIDATION_PATH,
    TEST_PATH,
    GENERALIZATION_PATH,
    ADVANCED_PATH,
]

for path in required_files:

    if not path.exists():
        raise FileNotFoundError(
            f"REQUIRED_ARTIFACT_NOT_FOUND={path}"
        )


with open(
    VALIDATION_PATH,
    "r",
    encoding="utf-8",
) as f:
    validation = json.load(f)


with open(
    TEST_PATH,
    "r",
    encoding="utf-8",
) as f:
    test = json.load(f)


with open(
    GENERALIZATION_PATH,
    "r",
    encoding="utf-8",
) as f:
    generalization = json.load(f)


with open(
    ADVANCED_PATH,
    "r",
    encoding="utf-8",
) as f:
    advanced = json.load(f)


# ============================================================
# Frozen final candidate
# ============================================================

FINAL_MODEL = "T3-MOD-008"

PRIMARY_METRIC = "macro_f1"


# ============================================================
# Extract final metrics
# ============================================================

validation_accuracy = float(
    validation["accuracy"]
)

validation_macro_f1 = float(
    validation["macro_f1"]
)

validation_weighted_f1 = float(
    validation["weighted_f1"]
)

test_accuracy = float(
    test["accuracy"]
)

test_macro_f1 = float(
    test["macro_f1"]
)

test_weighted_f1 = float(
    test["weighted_f1"]
)


# ============================================================
# Per-class test evidence
# ============================================================

test_per_class = test["per_class"]


s1_test_f1 = float(
    test_per_class["S1"]["f1"]
)

s2_test_f1 = float(
    test_per_class["S2"]["f1"]
)

s3_test_f1 = float(
    test_per_class["S3"]["f1"]
)

s4_test_f1 = float(
    test_per_class["S4"]["f1"]
)


# ============================================================
# Generalization changes
# ============================================================

accuracy_change = float(
    generalization[
        "overall_generalization"
    ]["test_minus_validation"]["accuracy"]
)

macro_f1_change = float(
    generalization[
        "overall_generalization"
    ]["test_minus_validation"]["macro_f1"]
)

weighted_f1_change = float(
    generalization[
        "overall_generalization"
    ]["test_minus_validation"]["weighted_f1"]
)


# ============================================================
# Advanced branch evidence
# ============================================================

distilbert_macro_f1 = float(
    advanced[
        "advanced_candidate"
    ]["macro_f1"]
)

distilbert_accuracy = float(
    advanced[
        "advanced_candidate"
    ]["accuracy"]
)

distilbert_weighted_f1 = float(
    advanced[
        "advanced_candidate"
    ]["weighted_f1"]
)


# ============================================================
# Suitability assessment
#
# This is a documented system-role conclusion, not a
# numerical model score.
# ============================================================

s1_limitation = (
    s1_test_f1 == 0.0
)

minority_limitation = (
    s1_test_f1 == 0.0
    or s2_test_f1 < 0.25
)

temporal_degradation = (
    macro_f1_change < 0.0
)

advanced_not_selected = (
    advanced["decision"]["final_candidate"]
    == FINAL_MODEL
)


# ============================================================
# System role
# ============================================================

SYSTEM_ROLE = (
    "SECONDARY_DECISION_SUPPORT_SIGNAL"
)

SUITABILITY = (
    "SUPPORTED_WITH_LIMITATIONS"
)

STATUS = "CLOSED"


# ============================================================
# Print summary
# ============================================================

print(f"FINAL_MODEL={FINAL_MODEL}")
print(f"PRIMARY_METRIC={PRIMARY_METRIC}")

print(
    f"VALIDATION_ACCURACY="
    f"{validation_accuracy:.6f}"
)

print(
    f"VALIDATION_MACRO_F1="
    f"{validation_macro_f1:.6f}"
)

print(
    f"VALIDATION_WEIGHTED_F1="
    f"{validation_weighted_f1:.6f}"
)

print(
    f"TEST_ACCURACY="
    f"{test_accuracy:.6f}"
)

print(
    f"TEST_MACRO_F1="
    f"{test_macro_f1:.6f}"
)

print(
    f"TEST_WEIGHTED_F1="
    f"{test_weighted_f1:.6f}"
)

print(
    f"TEST_MACRO_F1_CHANGE="
    f"{macro_f1_change:+.6f}"
)

print(
    f"TEST_ACCURACY_CHANGE="
    f"{accuracy_change:+.6f}"
)

print(
    f"TEST_WEIGHTED_F1_CHANGE="
    f"{weighted_f1_change:+.6f}"
)

print(
    f"S1_TEST_F1="
    f"{s1_test_f1:.6f}"
)

print(
    f"S2_TEST_F1="
    f"{s2_test_f1:.6f}"
)

print(
    f"S3_TEST_F1="
    f"{s3_test_f1:.6f}"
)

print(
    f"S4_TEST_F1="
    f"{s4_test_f1:.6f}"
)

print(
    f"DISTILBERT_MACRO_F1="
    f"{distilbert_macro_f1:.6f}"
)

print(
    f"DISTILBERT_ACCURACY="
    f"{distilbert_accuracy:.6f}"
)

print(
    f"DISTILBERT_WEIGHTED_F1="
    f"{distilbert_weighted_f1:.6f}"
)

print(
    f"S1_LIMITATION={s1_limitation}"
)

print(
    f"MINORITY_CLASS_LIMITATION="
    f"{minority_limitation}"
)

print(
    f"TEMPORAL_MACRO_F1_DEGRADATION="
    f"{temporal_degradation}"
)

print(
    f"ADVANCED_BRANCH_CLOSED="
    f"{advanced_not_selected}"
)

print(f"SUITABILITY={SUITABILITY}")
print(f"SYSTEM_ROLE={SYSTEM_ROLE}")
print(f"STATUS={STATUS}")


# ============================================================
# Closure artifact
# ============================================================

result = {
    "operation": "T3-MOD-029",

    "task": "T3_SEVERITY_PREDICTION",

    "status": STATUS,

    "final_candidate": {
        "model_id": FINAL_MODEL,
        "selection_primary_metric": PRIMARY_METRIC,
        "validation_metrics": {
            "accuracy": validation_accuracy,
            "macro_f1": validation_macro_f1,
            "weighted_f1": validation_weighted_f1,
        },
        "locked_test_metrics": {
            "accuracy": test_accuracy,
            "macro_f1": test_macro_f1,
            "weighted_f1": test_weighted_f1,
        },
    },

    "test_per_class": test_per_class,

    "generalization": {
        "accuracy_change": accuracy_change,
        "macro_f1_change": macro_f1_change,
        "weighted_f1_change": weighted_f1_change,
    },

    "advanced_branch": {
        "distilbert_accuracy": distilbert_accuracy,
        "distilbert_macro_f1": distilbert_macro_f1,
        "distilbert_weighted_f1": distilbert_weighted_f1,
        "selected": False,
        "status": "CLOSED",
    },

    "limitations": [
        (
            "S1 remained undetected on the locked test set "
            "with F1=0 and support=13."
        ),
        (
            "S2 test F1 was 0.186005, indicating limited "
            "minority-class discrimination."
        ),
        (
            "Macro F1 decreased from 0.348017 on validation "
            "to 0.303682 on the locked test set."
        ),
        (
            "The largest test errors involved S3/S4 and "
            "S3/S2 confusion."
        ),
        (
            "The chronological evaluation exhibits temporal "
            "distribution shift across severity classes."
        ),
        (
            "DistilBERT achieved higher accuracy and weighted "
            "F1 in feasibility testing but lower macro F1 and "
            "did not resolve S1/S2 detection."
        ),
    ],

    "suitability": SUITABILITY,

    "system_role": SYSTEM_ROLE,

    "recommended_use": (
        "Use T3 severity prediction as a secondary decision-"
        "support signal for downstream triage or human review. "
        "Do not treat the prediction as an autonomous or "
        "authoritative severity assignment."
    ),

    "evidence_controls": {
        "validation_used_for_selection": True,
        "locked_test_used_for_final_evaluation": True,
        "test_used_for_selection": False,
        "final_model_retrained_after_selection": False,
        "final_model_refit_on_test": False,
        "raw_mozilla_accessed_during_closure": False,
        "dataset_modified": False,
    },

    "closure_statement": (
        "T3 — Severity Prediction is CLOSED as a "
        "SUPPORTED_WITH_LIMITATIONS secondary decision-"
        "support signal. The selected candidate is T3-MOD-008 "
        "under the pre-frozen macro-F1 criterion. Locked test "
        "evaluation and final generalization analysis are "
        "complete. The task is not treated as an autonomous "
        "severity assignment capability."
    ),

    "next_task": "T4",
}


# ============================================================
# Save
# ============================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8",
) as f:
    json.dump(
        result,
        f,
        indent=2,
    )


print(f"OUTPUT={OUTPUT_PATH}")

print("TEST_USED_FOR_SELECTION=False")
print("FINAL_MODEL_RETRAINED=False")
print("FINAL_MODEL_REFIT=False")
print("RAW_MOZILLA_ACCESSED=False")
print("DATASET_MODIFIED=False")

print("STATUS=CLOSED")
print("T3_MOD_029_COMPLETE")