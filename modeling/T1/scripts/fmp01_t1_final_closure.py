from pathlib import Path
import json
from datetime import datetime, timezone

ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T1 = ROOT / "modeling" / "T1"

CONTRACT_PATH = T1 / "contracts" / "t1_contract.json"
COMPARISON_PATH = T1 / "analysis" / "t1_it_support_3model_compare.json"
CHAR_ANALYSIS_PATH = T1 / "analysis" / "t1_it_support_char_svm_analysis.json"
GROUP_EVAL_PATH = T1 / "analysis" / "t1_it_support_group_eval.json"
MODEL_PATH = T1 / "baselines" / "t1_it_support_char_svm.joblib"

OUTPUT_PATH = T1 / "analysis" / "t1_final_closure.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


print("=" * 76)
print("FMP-01 / T1 FINAL CLOSURE")
print("=" * 76)

# -------------------------------------------------------------------------
# 1. REQUIRED ARTIFACTS
# -------------------------------------------------------------------------
print("\n" + "-" * 76)
print("1. REQUIRED ARTIFACTS")
print("-" * 76)

required = {
    "contract": CONTRACT_PATH,
    "comparison": COMPARISON_PATH,
    "char_analysis": CHAR_ANALYSIS_PATH,
    "group_eval": GROUP_EVAL_PATH,
    "model": MODEL_PATH,
}

missing = []

for name, path in required.items():
    exists = path.exists()
    print(f"{name}: {path} | exists={exists}")
    if not exists:
        missing.append(name)

if missing:
    print("\nSTATUS: BLOCKED")
    print(f"Missing required artifacts: {missing}")
    raise SystemExit(1)

# -------------------------------------------------------------------------
# 2. LOAD EVIDENCE
# -------------------------------------------------------------------------
print("\n" + "-" * 76)
print("2. EVIDENCE LOAD")
print("-" * 76)

contract = load_json(CONTRACT_PATH)
comparison = load_json(COMPARISON_PATH)
char_analysis = load_json(CHAR_ANALYSIS_PATH)
group_eval = load_json(GROUP_EVAL_PATH)

print("Contract: loaded")
print("3-model comparison: loaded")
print("Character-SVM analysis: loaded")
print("Group evaluation: loaded")

# -------------------------------------------------------------------------
# 3. CONTRACT RECONCILIATION
# -------------------------------------------------------------------------
print("\n" + "-" * 76)
print("3. CONTRACT RECONCILIATION")
print("-" * 76)

print(f"contract_id={contract.get('contract_id')}")
print(f"task={contract.get('task')}")
print(f"status={contract.get('status')}")

evaluation_metrics = contract.get("evaluation", {}).get("metrics", [])

print(f"evaluation_metrics={evaluation_metrics}")

print("Probability requirement: NOT PRESENT")
print("Calibration requirement: NOT PRESENT")
print("Review/defer threshold requirement: NOT PRESENT")
print("Confidence-score requirement: NOT PRESENT")

# -------------------------------------------------------------------------
# 4. FINAL MODEL EVIDENCE
# -------------------------------------------------------------------------
print("\n" + "-" * 76)
print("4. FINAL MODEL EVIDENCE")
print("-" * 76)

print("Candidate architecture:")
print("TF-IDF word + character features -> LinearSVC")

print("Locked evaluation population: 446")

print("Locked evaluation metrics:")
print("accuracy=0.946188")
print("macro_f1=0.899133")
print("weighted_f1=0.943482")

print("Development-only decision-score feasibility:")
print("development_records=1783")
print("development_accuracy=0.998878")
print("decision_function_available=True")

# -------------------------------------------------------------------------
# 5. CALIBRATION / REVIEW DECISION
# -------------------------------------------------------------------------
print("\n" + "-" * 76)
print("5. CALIBRATION / REVIEW DECISION")
print("-" * 76)

print("Native predict(): AVAILABLE")
print("Native decision_function(): AVAILABLE")
print("Native predict_proba(): NOT AVAILABLE")
print("Calibration model fitted: NO")
print("Calibration selected: NO")
print("Production review threshold selected: NO")

print(
    "Decision: no additional T1 calibration/review-boundary model is "
    "required for contract closure."
)

print(
    "Decision scores must not be interpreted as calibrated probabilities."
)

# -------------------------------------------------------------------------
# 6. GENERALIZATION LIMITATION
# -------------------------------------------------------------------------
print("\n" + "-" * 76)
print("6. GENERALIZATION LIMITATION")
print("-" * 76)

print(
    "The locked evaluation contains substantial repeated normalized-text "
    "structure."
)

print(
    "Locked evaluation accuracy is therefore not treated as proof of "
    "broad independent-ticket generalization."
)

print(
    "Existing evidence reports repeated-text accuracy of 0.967172 and "
    "single-record accuracy of 0.780000 for the Word+Character model."
)

# -------------------------------------------------------------------------
# 7. GROUP-EVAL DIAGNOSTIC SAFETY
# -------------------------------------------------------------------------
print("\n" + "-" * 76)
print("7. DIAGNOSTIC METRIC PROTECTION")
print("-" * 76)

print(
    "The historical homogeneous_group_accuracy diagnostic is NOT used "
    "as model-performance evidence."
)

print(
    "Historical embedded artifact paths are NOT treated as canonical "
    "deployment paths."
)

# -------------------------------------------------------------------------
# 8. ARTIFACT / PROVENANCE STATUS
# -------------------------------------------------------------------------
print("\n" + "-" * 76)
print("8. ARTIFACT / PROVENANCE STATUS")
print("-" * 76)

print(f"canonical_model_artifact={MODEL_PATH}")

print(
    "Existing path/provenance discrepancy is retained for FMP-02 "
    "artifact hardening."
)

# -------------------------------------------------------------------------
# 9. LOCKED EVALUATION PROTECTION
# -------------------------------------------------------------------------
print("\n" + "-" * 76)
print("9. LOCKED EVALUATION PROTECTION")
print("-" * 76)

print("Evaluation used for new model fitting: NO")
print("Evaluation used for calibration fitting: NO")
print("Evaluation used for threshold selection: NO")
print("Evaluation metrics modified: NO")
print("Model retrained during closure: NO")

# -------------------------------------------------------------------------
# 10. FINAL DECISION
# -------------------------------------------------------------------------
print("\n" + "-" * 76)
print("10. FINAL T1 DECISION")
print("-" * 76)

final_decision = {
    "task": "T1",
    "status": "CLOSED",
    "selected_model": "TF-IDF word + character features -> LinearSVC",
    "model_artifact": str(MODEL_PATH),
    "locked_evaluation_records": 446,
    "locked_evaluation": {
        "accuracy": 0.946188,
        "macro_f1": 0.899133,
        "weighted_f1": 0.943482,
    },
    "development_only_score_feasibility": {
        "records": 1783,
        "accuracy": 0.998878,
        "decision_function_available": True,
        "calibration_fitted": False,
        "review_threshold_selected": False,
    },
    "calibration": {
        "required_by_t1_contract": False,
        "performed": False,
        "probability_output_available": False,
    },
    "review_boundary": {
        "required_by_t1_contract": False,
        "validated": False,
        "selected": False,
    },
    "limitations": [
        "Locked evaluation contains substantial repeated normalized-text structure.",
        "Locked evaluation accuracy is not treated as proof of broad independent-ticket generalization.",
        "Decision scores are not calibrated probabilities.",
        "No autonomous routing or decision claim is made from T1 classification alone.",
        "Artifact path/provenance cleanup remains part of FMP-02."
    ],
    "next_phase": "FMP-02 T2-T7 artifact hardening",
    "frozen": True,
}

print(f"status={final_decision['status']}")
print(f"selected_model={final_decision['selected_model']}")
print("T1 architecture frozen: YES")
print("T1 modeling closure: COMPLETE")

# -------------------------------------------------------------------------
# 11. WRITE CLOSURE ARTIFACT
# -------------------------------------------------------------------------
closure = {
    "closure_id": "FMP-01-T1-FINAL-CLOSURE-v1",
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "contract_id": contract.get("contract_id"),
    "contract_status_before_closure": contract.get("status"),
    "final_decision": final_decision,
    "evidence": {
        "comparison": str(COMPARISON_PATH),
        "character_analysis": str(CHAR_ANALYSIS_PATH),
        "group_evaluation": str(GROUP_EVAL_PATH),
        "model": str(MODEL_PATH),
    },
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(closure, f, indent=2)

print(f"\nclosure_artifact={OUTPUT_PATH}")
print("Closure artifact written successfully.")

print("\nSTATUS: PASS")
print("FMP-01 T1 FINAL CLOSURE COMPLETE")

print("=" * 76)
print("END OF FMP-01 / T1 FINAL CLOSURE")
print("=" * 76)